import os
import json
import logging
import asyncio
from typing import Any, Dict, Optional, List
from datetime import datetime
from pydantic_ai import Agent
from anthropic import AsyncAnthropic
import redis.asyncio as redis
import psycopg2
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

# Multi-provider LLM support
import openai
from google.generativeai import configure as configure_gemini
from .llm_router import get_llm_router, LLMProvider
import time
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

# Import the new token management system
try:
    from ..token_manager import get_token_manager, TokenManager
except ImportError:
    # Fallback for testing
    get_token_manager = lambda: None


class BaseAgent:
    """Base class for all Bruno AI V3.2 agents with multi-provider LLM support and A2A communication."""
    
    def __init__(self, agent_id: str, model_name: str = None, redis_url: str = None, postgres_url: str = None):
        self.agent_id = agent_id
        self.redis_client = redis.from_url(redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379'))
        self.postgres_conn = psycopg2.connect(postgres_url or os.getenv('POSTGRES_URL', 'postgresql://localhost:5432/bruno_ai'))
        self.logger = logging.getLogger(f"bruno.{agent_id}")
        
        # Initialize LLM router and get optimal model
        self.llm_router = get_llm_router()
        self.model_string, self.llm_config = self.llm_router.select_llm_for_agent(agent_id)
        self.model_name = model_name or self.llm_config.model
        
        # Initialize provider-specific clients
        self._init_provider_clients()
        
        # Initialize PydanticAI agent with selected model
        self.agent = Agent(
            self.model_string,
            system_prompt=self._get_system_prompt()
        )
        
        # Performance tracking
        self.request_count = 0
        self.total_tokens_used = 0
        self.total_cost = 0.0
        self.error_count = 0
        
        self.logger.info(f"BaseAgent initialized with {self.model_string} for {agent_id}")
    
    def _init_provider_clients(self):
        """Initialize provider-specific API clients"""
        # Anthropic client
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_key:
            self.anthropic_client = AsyncAnthropic(api_key=anthropic_key)
        else:
            self.anthropic_client = None
        
        # OpenAI client
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            self.openai_client = openai.AsyncOpenAI(api_key=openai_key)
        else:
            self.openai_client = None
        
        # Google Gemini client
        google_key = os.getenv('GOOGLE_API_KEY')
        if google_key:
            configure_gemini(api_key=google_key)
            self.google_client = True  # Gemini uses global configuration
        else:
            self.google_client = False
            
        self.logger.info(f"Initialized clients for available providers")
    
    def _get_system_prompt(self) -> str:
        """Get dynamic system prompt."""
        return """
        You are Bruno, a friendly Brooklyn-based AI assistant specialized in meal planning and grocery shopping.
        Always maintain your warm, helpful personality while being efficient with responses.
        Focus on user wants like budget constraints and cuisine preferences without prescription.
        Adapt based on feedback and context.
        """
    
    async def compress_context(self, context: str, max_tokens: int = 4000) -> str:
        """Compress context using Haiku to reduce token usage."""
        if self.estimate_tokens(context) < max_tokens:
            return context
        
        try:
            response = await self.anthropic_client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=max_tokens // 2,
                messages=[{
                    "role": "user",
                    "content": f"Compress this context keeping user wants like budget/cuisine preferences: {context}"
                }]
            )
            compressed = response.content[0].text
            self.logger.info(f"Context compressed from {self.estimate_tokens(context)} to {self.estimate_tokens(compressed)} tokens")
            return compressed
        except Exception as e:
            self.logger.error(f"Context compression failed: {e}")
            return context[:max_tokens * 4]  # Fallback truncation
    
    async def cache_get(self, key: str) -> Optional[str]:
        """Get cached result async."""
        try:
            cached = await self.redis_client.get(f"bruno:{self.agent_id}:{key}")
            return cached.decode('utf-8') if cached else None
        except Exception as e:
            self.logger.error(f"Cache get failed: {e}")
            return None
    
    async def cache_set(self, key: str, value: str, ttl: int = 3600):
        """Set cached result with TTL async."""
        try:
            await self.redis_client.set(f"bruno:{self.agent_id}:{key}", value, ex=ttl)
        except Exception as e:
            self.logger.error(f"Cache set failed: {e}")
    
    async def process_with_optimization(self, query: str, context_id: str = None) -> str:
        """Process query with advanced token optimization and routing."""
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Query must be a non-empty string.")
        
        cache_key = f"{hash(query)}:{context_id or 'default'}"
        cached_result = await self.cache_get(cache_key)
        if cached_result:
            self.logger.info("Cache hit - returning cached result")
            return cached_result
        
        # Try to use the advanced token manager if available
        try:
            token_manager = get_token_manager()
            if token_manager:
                # Get context for complexity analysis
                context = await self.get_context(context_id) if context_id else None
                
                # Use advanced token management
                result, metrics = await token_manager.process_with_routing(
                    query, context_id, context
                )
                
                # Cache the result
                await self.cache_set(cache_key, result)
                
                # Log metrics
                self.logger.info(f"Query processed with token optimization: "
                               f"tokens={metrics.total_tokens}, "
                               f"model={metrics.model_used}, "
                               f"compression={metrics.compression_ratio:.2f}, "
                               f"cost=${metrics.cost_estimate:.4f}")
                
                return result
        except Exception as e:
            self.logger.warning(f"Token manager not available, falling back to basic optimization: {e}")
        
        # Fallback to basic optimization
        optimized_query = await self.compress_context(query)
        
        try:
            result = await self._run_with_provider_error_handling(optimized_query)
            await self.cache_set(cache_key, result)
            self.logger.info(f"Query processed - estimated tokens: {self.estimate_tokens(optimized_query)}")
            return result
        except Exception as e:
            self.logger.error(f"Agent processing failed: {e}")
            raise
    
    async def get_context(self, context_id: str) -> Dict[str, Any]:
        """Get shared context from Redis."""
        if not isinstance(context_id, str):
            raise ValueError("Context ID must be a string.")
        try:
            context_data = await self.redis_client.get(f"bruno:context:{context_id}")
            if context_data:
                return json.loads(context_data.decode('utf-8'))
            return {}
        except Exception as e:
            self.logger.error(f"Context retrieval failed: {e}")
            return {}
    
    async def set_context(self, context_id: str, data: Dict[str, Any]):
        """Set shared context in Redis."""
        if not isinstance(context_id, str) or not isinstance(data, dict):
            raise ValueError("Context ID must be string, data a dict.")
        try:
            await self.redis_client.set(
                f"bruno:context:{context_id}", 
                json.dumps(data), 
                ex=7200
            )
        except Exception as e:
            self.logger.error(f"Context setting failed: {e}")
    
    async def send_a2a_message(self, to_agent: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send A2A message with JSON-RPC."""
        if not isinstance(to_agent, str) or not isinstance(message, dict):
            raise ValueError("To agent string, message dict required.")
        try:
            a2a_message = {
                'method': 'jsonrpc',
                'jsonrpc': '2.0',
                'id': 1,
                'params': {
                    'timestamp': datetime.now().isoformat(),
                    'from_agent': self.agent_id,
                    'to_agent': to_agent,
                    'message_id': f"{self.agent_id}_{datetime.now().timestamp()}",
                    'payload': message
                }
            }
            self.logger.info(f"Sending A2A message to {to_agent}: {message.get('type', 'unknown')}")
            await self.redis_client.lpush(
                f"bruno:a2a:{to_agent}:inbox",
                json.dumps(a2a_message)
            )
            await self.redis_client.expire(f"bruno:a2a:{to_agent}:inbox", 3600)
            return {
                'success': True,
                'status': 'sent',
                'message_id': a2a_message['params']['message_id'],
                'timestamp': a2a_message['params']['timestamp']
            }
        except Exception as e:
            self.logger.error(f"Failed to send A2A message: {e}")
            return {'success': False, 'error': str(e)}
    
    async def receive_a2a_message(self) -> Optional[Dict[str, Any]]:
        """Receive A2A message."""
        try:
            message_data = await self.redis_client.rpop(f"bruno:a2a:{self.agent_id}:inbox")
            if message_data:
                message = json.loads(message_data.decode('utf-8'))
                self.logger.info(f"Received A2A message from {message.get('from_agent', 'unknown')}")
                return message
            return None
        except Exception as e:
            self.logger.error(f"Failed to receive A2A message: {e}")
            return None
    
    async def persist_to_postgres(self, table: str, data: Dict[str, Any], context_id: str = None) -> bool:
        """Persist data to Postgres async."""
        try:
            loop = asyncio.get_running_loop()
            def _execute():
                with self.postgres_conn.cursor() as cursor:
                    if table == 'user_contexts':
                        cursor.execute(
                            """
                            INSERT INTO user_contexts (context_id, data, updated_at)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (context_id) 
                            DO UPDATE SET data = %s, updated_at = %s
                            """,
                            (context_id, json.dumps(data), datetime.now(), json.dumps(data), datetime.now())
                        )
                    elif table == 'agent_history':
                        cursor.execute(
                            """
                            INSERT INTO agent_history (agent_id, context_id, action_type, data, created_at)
                            VALUES (%s, %s, %s, %s, %s)
                            """,
                            (self.agent_id, context_id, data.get('action_type', 'unknown'), 
                             json.dumps(data), datetime.now())
                        )
                    self.postgres_conn.commit()
                    return True
            with ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(executor, _execute)
            self.logger.info(f"Data persisted to {table} for context {context_id}")
            return result
        except Exception as e:
            self.logger.error(f"Failed to persist to PostgreSQL: {e}")
            return False
    
    async def query_postgres(self, query: str, params: tuple = None, context_id: str = None) -> List[Dict[str, Any]]:
        """Query Postgres async."""
        try:
            loop = asyncio.get_running_loop()
            def _execute():
                with self.postgres_conn.cursor() as cursor:
                    cursor.execute(query, params or ())
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    return [dict(zip(columns, row)) for row in rows]
            with ThreadPoolExecutor() as executor:
                results = await loop.run_in_executor(executor, _execute)
            self.logger.info(f"Query executed: {len(results)} rows returned")
            return results
        except Exception as e:
            self.logger.error(f"PostgreSQL query failed: {e}")
            return []
    
    def switch_model(self, new_model: str) -> bool:
        """Switch model."""
        if not isinstance(new_model, str):
            raise ValueError("New model must be a string.")
        try:
            self.model_name = new_model
            self.agent = Agent(
                f'anthropic:{new_model}',
                system_prompt=self._get_system_prompt()
            )
            self.logger.info(f"Switched to model: {new_model}")
            return True
        except Exception as e:
            self.logger.error(f"Model switch failed: {e}")
            return False
    
    def estimate_tokens(self, text: str) -> int:
        """Improved token estimate."""
        if not isinstance(text, str):
            return 0
        # Better approx: tokens ≈ chars/4 for Claude
        return int(len(text) / 4) + 1  # +1 for safety
    
    async def query_user_if_unclear(self, context: str, question: str, context_id: str = None) -> str:
        """Query user for clarification."""
        if not isinstance(context, str) or not isinstance(question, str):
            raise ValueError("Context and question must be strings.")
        try:
            clarification_query = f"""
            Based on this context: {context[:500]}...
            
            I need clarification: {question}
            
            Please provide a helpful response that maintains Bruno's friendly personality
            and asks for specific information to better assist the user.
            
            Format as a direct question to the user.
            """
            response = await self.anthropic_client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=150,
                messages=[{
                    "role": "user",
                    "content": clarification_query
                }]
            )
            clarification = response.content[0].text
            self.logger.info(f"Generated user clarification: {question}")
            if context_id:
                context_data = await self.get_context(context_id)
                context_data['pending_clarification'] = {
                    'question': question,
                    'generated_response': clarification,
                    'timestamp': datetime.now().isoformat()
                }
                await self.set_context(context_id, context_data)
            return clarification
        except Exception as e:
            self.logger.error(f"User clarification failed: {e}")
            return f"I need more information about: {question}. Could you help clarify?"
    
    async def handle_variance_alert(self, variance_data: Dict[str, Any], context_id: str = None) -> Dict[str, Any]:
        """Handle variance alerts."""
        if not isinstance(variance_data, dict):
            raise ValueError("Variance data must be a dict.")
        try:
            variance_percentage = variance_data.get('variance_percentage', 0)
            current_spending = variance_data.get('current_spending', 0)
            budget = variance_data.get('budget', 0)
            if abs(variance_percentage) > 20:
                alert_level = 'critical'
                urgency = 'immediate'
            elif abs(variance_percentage) > 10:
                alert_level = 'warning'
                urgency = 'soon'
            else:
                alert_level = 'info'
                urgency = 'when_convenient'
            if variance_percentage < -10:
                message = f"You might be spending about {abs(variance_percentage):.1f}% over your ${budget} budget. Consider some budget-friendly alternatives?"
                recommendations = [
                    "You might save by choosing store brands for some items",
                    "Consider looking for items on sale or with coupons",
                    "You might substitute some ingredients with more affordable options"
                ]
            elif variance_percentage > 15:
                message = f"Great news! You might have about {variance_percentage:.1f}% of your budget remaining. You could consider some upgrades!"
                recommendations = [
                    "You might upgrade some ingredients for better quality",
                    "Consider trying some premium or organic options",
                    "You might add some special treats to your list"
                ]
            else:
                message = f"You're tracking well with your ${budget} budget!"
                recommendations = ["Keep up the great budgeting!"]
            alert_data = {
                'alert_level': alert_level,
                'urgency': urgency,
                'message': message,
                'recommendations': recommendations,
                'variance_details': variance_data,
                'timestamp': datetime.now().isoformat()
            }
            if context_id:
                context_data = await self.get_context(context_id)
                context_data['variance_alert'] = alert_data
                await self.set_context(context_id, context_data)
                await self.persist_to_postgres(
                    'agent_history',
                    {
                        'action_type': 'variance_alert',
                        'alert_level': alert_level,
                        'variance_percentage': variance_percentage,
                        'budget': budget,
                        'current_spending': current_spending
                    },
                    context_id
                )
            self.logger.info(f"Variance alert generated: {alert_level} level")
            return {'success': True, 'data': alert_data}
        except Exception as e:
            self.logger.error(f"Variance alert handling failed: {e}")
            return {'success': False, 'error': str(e)}

    

"""
Base Agent Implementation for Bruno AI V3.1
Includes token optimization, memory management, and A2A protocol support
"""

import os
import json
import logging
import asyncio
from typing import Any, Dict, Optional, List
from datetime import datetime
from pydantic_ai import Agent, RunContext
from anthropic import AsyncAnthropic
import redis.asyncio as redis
import psycopg2
from dotenv import load_dotenv

load_dotenv()

class BaseAgent:
    """Base class for all Bruno AI V3.1 agents with token optimization and A2A support"""
    
    def __init__(self, agent_id: str, model_name: str, redis_url: str, postgres_url: str):
        self.agent_id = agent_id
        self.model_name = model_name
        self.redis_client = redis.from_url(redis_url)
        self.postgres_conn = psycopg2.connect(postgres_url)
        self.anthropic_client = AsyncAnthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.logger = logging.getLogger(f"bruno.{agent_id}")
        
        # Initialize PydanticAI agent with proper model specification
        self.agent = Agent(
            f'anthropic:{model_name}',
            system_prompt=self._get_system_prompt()
        )
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the PydanticAI agent"""
        return """
        You are Bruno, a friendly Brooklyn-based AI assistant specialized in meal planning and grocery shopping.
        Always maintain your warm, helpful personality while being efficient with responses.
        Focus on user wants like budget constraints and cuisine preferences.
        """
    
    async def compress_context(self, context: str, max_tokens: int = 4000) -> str:
        """Compress context using Haiku to reduce token usage"""
        if len(context.split()) < max_tokens:
            return context
        
        try:
            # Use Haiku for compression
            response = await self.anthropic_client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=max_tokens // 2,
                messages=[{
                    "role": "user",
                    "content": f"Compress this context keeping user wants like budget/cuisine preferences: {context}"
                }]
            )
            compressed = response.content[0].text
            self.logger.info(f"Context compressed from {len(context)} to {len(compressed)} chars")
            return compressed
        except Exception as e:
            self.logger.error(f"Context compression failed: {e}")
            return context[:max_tokens * 4]  # Fallback truncation
    
    async def cache_get(self, key: str) -> Optional[str]:
        """Get cached result"""
        try:
            cached = await self.redis_client.get(f"bruno:{self.agent_id}:{key}")
            return cached.decode() if cached else None
        except Exception as e:
            self.logger.error(f"Cache get failed: {e}")
            return None
    
    async def cache_set(self, key: str, value: str, ttl: int = 3600):
        """Set cached result with TTL"""
        try:
            await self.redis_client.set(f"bruno:{self.agent_id}:{key}", value, ex=ttl)
        except Exception as e:
            self.logger.error(f"Cache set failed: {e}")
    
    async def process_with_optimization(self, query: str, context_id: str = None) -> str:
        """Process query with token optimization and caching"""
        # Check cache first
        cache_key = f"{hash(query)}:{context_id or 'default'}"
        cached_result = await self.cache_get(cache_key)
        if cached_result:
            self.logger.info("Cache hit - returning cached result")
            return cached_result
        
        # Compress query if needed
        optimized_query = await self.compress_context(query)
        
        # Process with agent
        try:
            result = await self.agent.run(optimized_query)
            
            # Cache result - properly access the result data
            result_data = result.data if hasattr(result, 'data') else str(result)
            await self.cache_set(cache_key, result_data)
            
            # Log token usage
            self.logger.info(f"Query processed - estimated tokens: {len(optimized_query.split())}")
            
            return result_data
            
        except Exception as e:
            self.logger.error(f"Agent processing failed: {e}")
            raise
    
    async def get_context(self, context_id: str) -> Dict[str, Any]:
        """Get shared context from Redis"""
        try:
            context_data = await self.redis_client.get(f"bruno:context:{context_id}")
            if context_data:
                return json.loads(context_data.decode())
            return {}
        except Exception as e:
            self.logger.error(f"Context retrieval failed: {e}")
            return {}
    
    async def set_context(self, context_id: str, data: Dict[str, Any]):
        """Set shared context in Redis"""
        try:
            await self.redis_client.set(
                f"bruno:context:{context_id}", 
                json.dumps(data), 
                ex=7200  # 2 hour TTL
            )
        except Exception as e:
            self.logger.error(f"Context setting failed: {e}")
    
    async def send_a2a_message(self, to_agent: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send A2A message to another agent via FastA2A protocol"""
        try:
            # Create A2A message with proper formatting
            a2a_message = {
                'timestamp': datetime.now().isoformat(),
                'from_agent': self.agent_id,
                'to_agent': to_agent,
                'message_id': f"{self.agent_id}_{datetime.now().timestamp()}",
                'payload': message
            }
            
            # Log the A2A message
            self.logger.info(f"Sending A2A message to {to_agent}: {message.get('type', 'unknown')}")
            
            # Store in Redis for A2A broker (placeholder for FastA2A integration)
            await self.redis_client.lpush(
                f"bruno:a2a:{to_agent}:inbox",
                json.dumps(a2a_message)
            )
            
            # Set expiration on the list
            await self.redis_client.expire(f"bruno:a2a:{to_agent}:inbox", 3600)
            
            return {
                'status': 'sent',
                'message_id': a2a_message['message_id'],
                'timestamp': a2a_message['timestamp']
            }
            
        except Exception as e:
            self.logger.error(f"Failed to send A2A message: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def receive_a2a_message(self) -> Optional[Dict[str, Any]]:
        """Receive A2A message from the agent's inbox"""
        try:
            # Check for messages in Redis inbox
            message_data = await self.redis_client.rpop(f"bruno:a2a:{self.agent_id}:inbox")
            
            if message_data:
                message = json.loads(message_data.decode())
                self.logger.info(f"Received A2A message from {message.get('from_agent', 'unknown')}")
                return message
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to receive A2A message: {e}")
            return None
    
    async def persist_to_postgres(self, table: str, data: Dict[str, Any], context_id: str = None) -> bool:
        """Persist data to PostgreSQL for long-term storage"""
        try:
            # Use psycopg2 with async wrapper for better performance
            import asyncio
            from concurrent.futures import ThreadPoolExecutor
            
            def _execute_query():
                with self.postgres_conn.cursor() as cursor:
                    # Upsert pattern for most common use cases
                    if table == 'user_contexts':
                        cursor.execute(
                            """
                            INSERT INTO user_contexts (context_id, data, updated_at)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (context_id) 
                            DO UPDATE SET data = %s, updated_at = %s
                            """,
                            (context_id, json.dumps(data), datetime.now(), json.dumps(data), datetime.now())
                        )
                    elif table == 'agent_history':
                        cursor.execute(
                            """
                            INSERT INTO agent_history (agent_id, context_id, action_type, data, created_at)
                            VALUES (%s, %s, %s, %s, %s)
                            """,
                            (self.agent_id, context_id, data.get('action_type', 'unknown'), 
                             json.dumps(data), datetime.now())
                        )
                    
                    self.postgres_conn.commit()
                    return True
            
            # Execute in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(executor, _execute_query)
                
            self.logger.info(f"Data persisted to {table} for context {context_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to persist to PostgreSQL: {e}")
            return False
    
    async def query_postgres(self, query: str, params: tuple = None, context_id: str = None) -> List[Dict[str, Any]]:
        """Query PostgreSQL and return results"""
        try:
            import asyncio
            from concurrent.futures import ThreadPoolExecutor
            
            def _execute_query():
                with self.postgres_conn.cursor() as cursor:
                    cursor.execute(query, params or ())
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    return [dict(zip(columns, row)) for row in rows]
            
            # Execute in thread pool
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                results = await loop.run_in_executor(executor, _execute_query)
                
            self.logger.info(f"Query executed: {len(results)} rows returned")
            return results
            
        except Exception as e:
            self.logger.error(f"PostgreSQL query failed: {e}")
            return []
    
    def switch_model(self, new_model: str) -> bool:
        """Switch the underlying Claude model for different use cases"""
        try:
            # Update model name
            self.model_name = new_model
            
            # Reinitialize PydanticAI agent with new model
            self.agent = Agent(
                f'anthropic:{new_model}',
                system_prompt=self._get_system_prompt()
            )
            
            self.logger.info(f"Switched to model: {new_model}")
            return True
            
        except Exception as e:
            self.logger.error(f"Model switch failed: {e}")
            return False
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count using word-based approximation"""
        # Approximation: 1 token ≈ 0.75 words for English text
        words = len(text.split())
        estimated_tokens = int(words / 0.75)
        return estimated_tokens
    
    async def query_user_if_unclear(self, context: str, question: str, context_id: str = None) -> str:
        """Query user for clarification when context is unclear"""
        try:
            # Create a user-friendly clarification request
            clarification_query = f"""
            Based on this context: {context[:500]}...
            
            I need clarification: {question}
            
            Please provide a helpful response that maintains Bruno's friendly personality
            and asks for specific information to better assist the user.
            
            Format as a direct question to the user.
            """
            
            # Use Haiku for efficient clarification generation
            response = await self.anthropic_client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=150,
                messages=[{
                    "role": "user",
                    "content": clarification_query
                }]
            )
            
            clarification = response.content[0].text
            
            # Log the clarification request
            self.logger.info(f"Generated user clarification: {question}")
            
            # Store clarification in context for follow-up
            if context_id:
                context_data = await self.get_context(context_id)
                context_data['pending_clarification'] = {
                    'question': question,
                    'generated_response': clarification,
                    'timestamp': datetime.now().isoformat()
                }
                await self.set_context(context_id, context_data)
            
            return clarification
            
        except Exception as e:
            self.logger.error(f"User clarification failed: {e}")
            return f"I need more information about: {question}. Could you help clarify?"
    
    async def handle_variance_alert(self, variance_data: Dict[str, Any], context_id: str = None) -> Dict[str, Any]:
        """Handle budget variance alerts and generate user-friendly notifications"""
        try:
            variance_percentage = variance_data.get('variance_percentage', 0)
            current_spending = variance_data.get('current_spending', 0)
            budget = variance_data.get('budget', 0)
            
            # Generate appropriate alert level
            if abs(variance_percentage) > 20:
                alert_level = 'critical'
                urgency = 'immediate'
            elif abs(variance_percentage) > 10:
                alert_level = 'warning'
                urgency = 'soon'
            else:
                alert_level = 'info'
                urgency = 'when_convenient'
            
            # Create user-friendly message
            if variance_percentage < -10:  # Over budget
                message = f"You might be spending about {abs(variance_percentage):.1f}% over your ${budget} budget. Consider some budget-friendly alternatives?"
                recommendations = [
                    "You might save by choosing store brands for some items",
                    "Consider looking for items on sale or with coupons",
                    "You might substitute some ingredients with more affordable options"
                ]
            elif variance_percentage > 15:  # Under budget
                message = f"Great news! You might have about {variance_percentage:.1f}% of your budget remaining. You could consider some upgrades!"
                recommendations = [
                    "You might upgrade some ingredients for better quality",
                    "Consider trying some premium or organic options",
                    "You might add some special treats to your list"
                ]
            else:
                message = f"You're tracking well with your ${budget} budget!"
                recommendations = ["Keep up the great budgeting!"]
            
            alert_data = {
                'alert_level': alert_level,
                'urgency': urgency,
                'message': message,
                'recommendations': recommendations,
                'variance_details': variance_data,
                'timestamp': datetime.now().isoformat()
            }
            
            # Persist alert for user interface
            if context_id:
                context_data = await self.get_context(context_id)
                context_data['variance_alert'] = alert_data
                await self.set_context(context_id, context_data)
                
                # Also persist to PostgreSQL for long-term tracking
                await self.persist_to_postgres(
                    'agent_history',
                    {
                        'action_type': 'variance_alert',
                        'alert_level': alert_level,
                        'variance_percentage': variance_percentage,
                        'budget': budget,
                        'current_spending': current_spending
                    },
                    context_id
                )
            
            self.logger.info(f"Variance alert generated: {alert_level} level")
            return alert_data
            
        except Exception as e:
            self.logger.error(f"Variance alert handling failed: {e}")
            return {
                'alert_level': 'error',
                'message': 'Unable to process budget variance at this time',
                'timestamp': datetime.now().isoformat()
            }
