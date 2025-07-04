"""
Base Agent Framework for Bruno AI Optimized Architecture
Provides common functionality for all specialized agents
"""

import asyncio
import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any
import httpx
import redis
from loguru import logger
from pydantic import BaseModel
import google.generativeai as genai

class AgentCard(BaseModel):
    """Agent capability definition"""
    name: str
    version: str
    description: str
    capabilities: Dict[str, Any]
    performance_targets: Optional[Dict[str, str]] = None
    api_integrations: Optional[Dict[str, Any]] = None

class AgentMessage(BaseModel):
    """Standard message format for A2A communication"""
    id: str
    sender: str
    recipient: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: datetime
    priority: str = "normal"

class BaseAgent(ABC):
    """Base class for all Bruno AI agents"""
    
    def __init__(self, agent_card: AgentCard):
        self.agent_card = agent_card
        self.agent_id = f"{agent_card.name}_{datetime.now().timestamp()}"
        
        # Initialize Gemini AI
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Initialize Redis for caching
        self.redis_client = self._initialize_redis()
        
        # Initialize metrics
        self.metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "average_response_time": 0.0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        # Agent state
        self.is_healthy = True
        self.last_activity = datetime.now()
        
        logger.info(f"Initialized {self.agent_card.name} v{self.agent_card.version}")
    
    def _initialize_redis(self) -> redis.Redis:
        """Initialize Redis connection for caching"""
        try:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
            return redis.from_url(redis_url, decode_responses=True)
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Using in-memory cache.")
            return None
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Main task processing entry point"""
        task_id = task.get('id', f"task_{datetime.now().timestamp()}")
        start_time = datetime.now()
        
        try:
            logger.info(f"Processing task {task_id} for {self.agent_card.name}")
            
            # Validate task
            validation_result = await self.validate_task(task)
            if not validation_result['valid']:
                raise ValueError(validation_result['error'])
            
            # Execute specialized task logic
            result = await self.execute_task(task)
            
            # Update metrics
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            self._update_metrics('success', response_time)
            
            return {
                "success": True,
                "task_id": task_id,
                "agent": self.agent_card.name,
                "result": result,
                "processing_time": response_time,
                "timestamp": end_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Task {task_id} failed: {str(e)}")
            self._update_metrics('failure', 0)
            
            return {
                "success": False,
                "task_id": task_id,
                "agent": self.agent_card.name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    @abstractmethod
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent-specific task logic"""
        pass
    
    async def validate_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Validate incoming task"""
        required_fields = ['action', 'context']
        
        for field in required_fields:
            if field not in task:
                return {
                    "valid": False,
                    "error": f"Missing required field: {field}"
                }
        
        return {"valid": True}
    
    async def get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached result"""
        if not self.redis_client:
            return None
        
        try:
            cached_data = await asyncio.to_thread(
                self.redis_client.get, 
                f"{self.agent_card.name}:{cache_key}"
            )
            
            if cached_data:
                self.metrics["cache_hits"] += 1
                return json.loads(cached_data)
            else:
                self.metrics["cache_misses"] += 1
                return None
                
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")
            return None
    
    async def cache_result(self, cache_key: str, data: Dict[str, Any], ttl: int = 300):
        """Cache result with TTL"""
        if not self.redis_client:
            return
        
        try:
            await asyncio.to_thread(
                self.redis_client.setex,
                f"{self.agent_card.name}:{cache_key}",
                ttl,
                json.dumps(data, default=str)
            )
        except Exception as e:
            logger.warning(f"Cache storage failed: {e}")
    
    async def call_gemini(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Call Gemini AI with prompt and context"""
        try:
            # Build full prompt with context
            full_prompt = self._build_prompt(prompt, context)
            
            # Generate response
            response = await asyncio.to_thread(
                self.model.generate_content,
                full_prompt
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise
    
    def _build_prompt(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Build comprehensive prompt with agent context"""
        agent_context = f"""
        You are Bruno, a savvy New York foodie bear from Brooklyn who helps families eat like kings on working family budgets.
        
        BRUNO'S CORE IDENTITY:
        - Born and raised in Brooklyn where every dollar counted
        - Ma taught you how to stretch grocery budgets while putting love on the table
        - Been hunting deals in bodegas, supermarkets, and farmer's markets since you were a cub
        - Streetwise, caring, practical with a "Trust me, I got this" attitude
        - Protective of family budgets - once you're Bruno's family, he's got your back
        
        BROOKLYN PERSONALITY TRAITS:
        - Voice: Working-class Brooklyn accent (not Manhattan elite)
        - Speech: Direct, practical, uses "ya," "gonna," "lemme," "bada-bing!"
        - Tone: Warm but no-nonsense, quick-witted, confident
        - Attitude: "Wise guy with a heart" - knows all the angles but genuinely cares
        
        BRUNO'S EXPERTISE:
        - Meal planning that doesn't break the bank
        - Deal hunting with insider knowledge
        - Budget analysis that makes sense to real families  
        - Nutrition guidance without the fancy stuff
        - Instacart optimization and smart shopping
        
        CURRENT CONTEXT:
        {json.dumps(context or {}, indent=2)}

        USER REQUEST:
        {prompt}

        BRUNO'S RESPONSE STYLE:
        1. **Brooklyn Charm**: Use authentic phrases like "Listen," "Lemme tell ya," "That's what I'm talkin' about!"
        2. **Celebrate Wins**: Get excited about savings - "Bada-bing! Ya came in $8.50 under budget!"
        3. **Real Talk**: Direct communication, no sugar-coating - "Hold up, that ain't gonna work"
        4. **Family First**: Always protect the family budget and well-being
        5. **Practical Wisdom**: Share insider tips like "Trust me on this one" with real solutions
        6. **Encouragement**: "Hey, don't worry about it. Ya gonna nail this budget thing, trust me. I got ya back."
        7. **Deal Hunter**: Get excited about finds - "I just spotted chicken thighs for $1.99 - that's highway robbery in a GOOD way!"
        
        CATCHPHRASES TO USE:
        - "Trust me on this one"
        - "That's what I'm talkin' about!"
        - "Bada-bing, bada-boom!"
        - "Ya gonna love this"
        - "Bruno's got ya covered"
        - "Lemme show ya how it's done"
        
        Respond as Bruno with authentic Brooklyn warmth, practical wisdom, and genuine care for helping families succeed.
        """
        
        return agent_context
    
    def _update_metrics(self, result_type: str, response_time: float):
        """Update agent performance metrics"""
        if result_type == 'success':
            self.metrics["tasks_completed"] += 1
        else:
            self.metrics["tasks_failed"] += 1
        
        # Update average response time
        total_tasks = self.metrics["tasks_completed"] + self.metrics["tasks_failed"]
        if total_tasks > 1:
            current_avg = self.metrics["average_response_time"]
            self.metrics["average_response_time"] = (
                (current_avg * (total_tasks - 1) + response_time) / total_tasks
            )
        else:
            self.metrics["average_response_time"] = response_time
        
        self.last_activity = datetime.now()
    
    async def health_check(self) -> Dict[str, Any]:
        """Agent health check"""
        return {
            "agent": self.agent_card.name,
            "version": self.agent_card.version,
            "healthy": self.is_healthy,
            "last_activity": self.last_activity.isoformat(),
            "metrics": self.metrics,
            "redis_connected": self.redis_client is not None
        }
    
    async def send_message_to_agent(self, target_agent: str, message: AgentMessage) -> Dict[str, Any]:
        """Send A2A message to another agent"""
        try:
            gateway_url = os.getenv('A2A_GATEWAY_URL', 'http://localhost:3000')
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{gateway_url}/agents/{target_agent}/task",
                    json=message.dict(),
                    timeout=30.0
                )
                
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to send message to {target_agent}: {e}")
            raise

class CacheManager:
    """Advanced caching strategies for agent optimization"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.cache_strategies = {
            "instacart_products": {"ttl": 300, "strategy": "write_through"},
            "recipe_data": {"ttl": 3600, "strategy": "write_behind"},
            "user_preferences": {"ttl": 86400, "strategy": "write_through"},
            "pricing_data": {"ttl": 180, "strategy": "write_through"},
            "nutrition_data": {"ttl": 1800, "strategy": "write_through"}
        }
    
    async def get_with_strategy(self, key: str, category: str) -> Optional[Dict[str, Any]]:
        """Get cached data using category-specific strategy"""
        if not self.redis:
            return None
        
        strategy = self.cache_strategies.get(category, {"ttl": 300})
        cache_key = f"{category}:{key}"
        
        try:
            cached_data = await asyncio.to_thread(self.redis.get, cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Cache retrieval failed for {cache_key}: {e}")
        
        return None
    
    async def set_with_strategy(self, key: str, data: Dict[str, Any], category: str):
        """Cache data using category-specific strategy"""
        if not self.redis:
            return
        
        strategy = self.cache_strategies.get(category, {"ttl": 300})
        cache_key = f"{category}:{key}"
        
        try:
            await asyncio.to_thread(
                self.redis.setex,
                cache_key,
                strategy["ttl"],
                json.dumps(data, default=str)
            )
        except Exception as e:
            logger.warning(f"Cache storage failed for {cache_key}: {e}")
