"""
Token Management and Optimization System - Bruno AI V3.1
Implements intelligent routing, compression, batching, and cost optimization
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import psycopg2
import redis.asyncio as redis
from anthropic import AsyncAnthropic
import re
import hashlib


class ModelType(Enum):
    """Model types for routing decisions"""
    HAIKU = "claude-3-5-haiku-20241022"
    SONNET = "claude-3-5-sonnet-20241022"


@dataclass
class TokenMetrics:
    """Token usage metrics for tracking"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    compression_ratio: float
    processing_time: float
    model_used: str
    cost_estimate: float
    compressed: bool = False


@dataclass
class QueryComplexity:
    """Query complexity analysis results"""
    token_estimate: int
    complexity_score: float
    reasoning_required: bool
    recommended_model: ModelType
    confidence: float


class TokenManager:
    """Advanced token management with intelligent routing and optimization"""
    
    def __init__(self, redis_url: str, postgres_url: str, anthropic_api_key: str):
        self.redis_client = redis.from_url(redis_url)
        self.postgres_conn = psycopg2.connect(postgres_url)
        self.anthropic_client = AsyncAnthropic(api_key=anthropic_api_key)
        self.logger = logging.getLogger("bruno.token_manager")
        
        # Token limits and thresholds
        self.MAX_TOKENS_PER_REQUEST = 16000
        self.HAIKU_THRESHOLD = 2000
        self.COMPRESSION_THRESHOLD = 4000
        self.ALERT_THRESHOLD = 10000
        
        # Cost tracking (estimated per 1K tokens)
        self.COST_PER_1K_TOKENS = {
            ModelType.HAIKU: 0.00025,  # $0.25 per 1M tokens
            ModelType.SONNET: 0.003    # $3 per 1M tokens
        }
        
        # Performance tracking
        self.metrics_cache = {}
        self.compression_stats = {
            'total_compressions': 0,
            'total_savings': 0,
            'avg_compression_ratio': 0
        }
        
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count using improved algorithm"""
        if not text:
            return 0
        
        # More accurate token estimation
        # Account for special tokens, punctuation, and structure
        words = len(text.split())
        chars = len(text)
        
        # Anthropic models average ~0.75 tokens per word
        # But adjust for punctuation, special characters
        word_tokens = words / 0.75
        char_adjustment = chars / 4.5  # Character-based adjustment
        
        # Take average and add buffer for safety
        estimated = int((word_tokens + char_adjustment) / 2 * 1.1)
        
        self.logger.debug(f"Token estimation: {estimated} tokens for {len(text)} characters")
        return estimated
    
    def analyze_query_complexity(self, query: str, context: Dict[str, Any] = None) -> QueryComplexity:
        """Analyze query complexity to determine optimal model"""
        
        # Token estimation
        token_estimate = self.estimate_tokens(query)
        
        # Complexity indicators
        complexity_indicators = {
            'reasoning_keywords': ['analyze', 'compare', 'evaluate', 'optimize', 'forecast', 'predict'],
            'simple_keywords': ['list', 'show', 'get', 'find', 'check', 'status'],
            'complex_patterns': [r'if.*then', r'what.*would.*happen', r'how.*should.*I'],
            'math_operations': [r'\d+\s*[+\-*/]\s*\d+', r'calculate', r'compute'],
            'multi_step': [r'first.*then', r'step.*by.*step', r'after.*do']
        }
        
        complexity_score = 0
        reasoning_required = False
        
        query_lower = query.lower()
        
        # Check for reasoning keywords
        reasoning_matches = sum(1 for keyword in complexity_indicators['reasoning_keywords'] 
                              if keyword in query_lower)
        complexity_score += reasoning_matches * 0.3
        
        # Check for simple keywords (reduces complexity)
        simple_matches = sum(1 for keyword in complexity_indicators['simple_keywords'] 
                           if keyword in query_lower)
        complexity_score -= simple_matches * 0.2
        
        # Check for complex patterns
        for pattern in complexity_indicators['complex_patterns']:
            if re.search(pattern, query_lower):
                complexity_score += 0.4
                reasoning_required = True
        
        # Check for math operations
        for pattern in complexity_indicators['math_operations']:
            if re.search(pattern, query_lower):
                complexity_score += 0.3
        
        # Check for multi-step indicators
        for pattern in complexity_indicators['multi_step']:
            if re.search(pattern, query_lower):
                complexity_score += 0.5
                reasoning_required = True
        
        # Context-based adjustments
        if context:
            # Budget analysis requires more reasoning
            if any(key in context for key in ['budget', 'cost', 'price', 'spending']):
                complexity_score += 0.2
            
            # Multiple constraints increase complexity
            constraints = sum(1 for key in ['dietary_restrictions', 'preferences', 'family_size'] 
                            if context.get(key))
            complexity_score += constraints * 0.1
        
        # Token-based complexity
        if token_estimate > self.HAIKU_THRESHOLD:
            complexity_score += 0.3
        
        # Determine recommended model
        if token_estimate < self.HAIKU_THRESHOLD and complexity_score < 0.5:
            recommended_model = ModelType.HAIKU
            confidence = 0.9
        elif complexity_score > 0.7 or reasoning_required:
            recommended_model = ModelType.SONNET
            confidence = 0.8
        else:
            # Borderline case - consider token count
            if token_estimate > 1500:
                recommended_model = ModelType.SONNET
                confidence = 0.6
            else:
                recommended_model = ModelType.HAIKU
                confidence = 0.7
        
        return QueryComplexity(
            token_estimate=token_estimate,
            complexity_score=complexity_score,
            reasoning_required=reasoning_required,
            recommended_model=recommended_model,
            confidence=confidence
        )
    
    async def compress_query(self, query: str, target_reduction: float = 0.5) -> Tuple[str, float]:
        """Compress query using Haiku while preserving meaning"""
        
        if self.estimate_tokens(query) < self.COMPRESSION_THRESHOLD:
            return query, 1.0
        
        original_tokens = self.estimate_tokens(query)
        
        try:
            compression_prompt = f"""
            Compress the following query while preserving all essential information, user requirements, and context:
            
            Original Query: {query}
            
            Requirements:
            - Maintain all specific details (budget amounts, quantities, preferences)
            - Preserve user intent and constraints
            - Remove redundancy and verbose language
            - Keep technical terms and specific requests
            - Target reduction: {target_reduction * 100:.0f}%
            
            Return only the compressed query:
            """
            
            response = await self.anthropic_client.messages.create(
                model=ModelType.HAIKU.value,
                max_tokens=int(original_tokens * target_reduction),
                messages=[{"role": "user", "content": compression_prompt}]
            )
            
            compressed_query = response.content[0].text.strip()
            compressed_tokens = self.estimate_tokens(compressed_query)
            
            compression_ratio = compressed_tokens / original_tokens
            
            # Update compression stats
            self.compression_stats['total_compressions'] += 1
            self.compression_stats['total_savings'] += (original_tokens - compressed_tokens)
            self.compression_stats['avg_compression_ratio'] = (
                (self.compression_stats['avg_compression_ratio'] * (self.compression_stats['total_compressions'] - 1) 
                 + compression_ratio) / self.compression_stats['total_compressions']
            )
            
            self.logger.info(f"Query compressed: {original_tokens} -> {compressed_tokens} tokens "
                           f"({compression_ratio:.2f} ratio)")
            
            return compressed_query, compression_ratio
            
        except Exception as e:
            self.logger.error(f"Compression failed: {e}")
            return query, 1.0
    
    async def process_with_routing(self, query: str, context_id: str = None, 
                                 context: Dict[str, Any] = None) -> Tuple[str, TokenMetrics]:
        """Process query with intelligent model routing and optimization"""
        
        start_time = time.time()
        
        # Analyze query complexity
        complexity = self.analyze_query_complexity(query, context)
        
        # Check for token overflow
        if complexity.token_estimate > self.MAX_TOKENS_PER_REQUEST:
            self.logger.warning(f"Query exceeds token limit: {complexity.token_estimate} tokens")
            # Attempt aggressive compression
            query, compression_ratio = await self.compress_query(query, target_reduction=0.3)
            complexity = self.analyze_query_complexity(query, context)
        else:
            compression_ratio = 1.0
        
        # Apply compression if beneficial
        if complexity.token_estimate > self.COMPRESSION_THRESHOLD:
            query, compression_ratio = await self.compress_query(query)
            complexity = self.analyze_query_complexity(query, context)
        
        # Select model based on complexity analysis
        model_to_use = complexity.recommended_model
        
        # Check if we should alert on high token usage
        if complexity.token_estimate > self.ALERT_THRESHOLD:
            await self._send_token_alert(complexity.token_estimate, query[:100])
        
        try:
            # Make the API call
            response = await self.anthropic_client.messages.create(
                model=model_to_use.value,
                max_tokens=min(4000, self.MAX_TOKENS_PER_REQUEST - complexity.token_estimate),
                messages=[{"role": "user", "content": query}]
            )
            
            result = response.content[0].text
            
            # Calculate metrics
            processing_time = time.time() - start_time
            completion_tokens = self.estimate_tokens(result)
            total_tokens = complexity.token_estimate + completion_tokens
            
            cost_estimate = (total_tokens / 1000) * self.COST_PER_1K_TOKENS[model_to_use]
            
            metrics = TokenMetrics(
                prompt_tokens=complexity.token_estimate,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                compression_ratio=compression_ratio,
                processing_time=processing_time,
                model_used=model_to_use.value,
                cost_estimate=cost_estimate,
                compressed=compression_ratio < 1.0
            )
            
            # Log metrics
            await self._log_metrics(metrics, context_id)
            
            return result, metrics
            
        except Exception as e:
            self.logger.error(f"API call failed: {e}")
            raise
    
    async def _log_metrics(self, metrics: TokenMetrics, context_id: str = None):
        """Log token usage metrics to database"""
        try:
            loop = asyncio.get_running_loop()
            
            def _execute():
                with self.postgres_conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO token_usage 
                        (context_id, model_used, prompt_tokens, completion_tokens, total_tokens, 
                         compression_applied, cost_estimate, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        context_id,
                        metrics.model_used,
                        metrics.prompt_tokens,
                        metrics.completion_tokens,
                        metrics.total_tokens,
                        metrics.compressed,
                        metrics.cost_estimate,
                        datetime.now()
                    ))
                    self.postgres_conn.commit()
            
            await loop.run_in_executor(None, _execute)
            
        except Exception as e:
            self.logger.error(f"Failed to log metrics: {e}")
    
    async def _send_token_alert(self, token_count: int, query_preview: str):
        """Send alert for high token usage"""
        alert_data = {
            'type': 'high_token_usage',
            'token_count': token_count,
            'threshold': self.ALERT_THRESHOLD,
            'query_preview': query_preview,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Store alert in Redis for monitoring system
            await self.redis_client.lpush(
                "bruno:alerts:token_usage",
                json.dumps(alert_data)
            )
            await self.redis_client.expire("bruno:alerts:token_usage", 86400)  # 24 hours
            
            self.logger.warning(f"High token usage alert: {token_count} tokens")
            
        except Exception as e:
            self.logger.error(f"Failed to send alert: {e}")
    
    async def get_usage_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get token usage statistics for the specified time period"""
        try:
            loop = asyncio.get_running_loop()
            
            def _execute():
                with self.postgres_conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT 
                            model_used,
                            COUNT(*) as request_count,
                            SUM(total_tokens) as total_tokens,
                            AVG(total_tokens) as avg_tokens_per_request,
                            SUM(cost_estimate) as total_cost,
                            AVG(compression_applied::int) as compression_rate
                        FROM token_usage 
                        WHERE created_at > NOW() - INTERVAL '%s hours'
                        GROUP BY model_used
                    """, (hours,))
                    
                    results = cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description]
                    
                    statistics = {
                        'period_hours': hours,
                        'by_model': [dict(zip(columns, row)) for row in results],
                        'compression_stats': self.compression_stats,
                        'generated_at': datetime.now().isoformat()
                    }
                    
                    # Calculate totals
                    total_requests = sum(row['request_count'] for row in statistics['by_model'])
                    total_cost = sum(row['total_cost'] for row in statistics['by_model'])
                    total_tokens = sum(row['total_tokens'] for row in statistics['by_model'])
                    
                    statistics['totals'] = {
                        'total_requests': total_requests,
                        'total_cost': total_cost,
                        'total_tokens': total_tokens,
                        'avg_cost_per_request': total_cost / total_requests if total_requests > 0 else 0
                    }
                    
                    return statistics
            
            return await loop.run_in_executor(None, _execute)
            
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {e}")
            return {}
    
    async def optimize_batch_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize batch of A2A messages for token efficiency"""
        
        if not messages:
            return messages
        
        # Group messages by type and similarity
        grouped_messages = {}
        for msg in messages:
            msg_type = msg.get('type', 'unknown')
            if msg_type not in grouped_messages:
                grouped_messages[msg_type] = []
            grouped_messages[msg_type].append(msg)
        
        optimized_messages = []
        
        for msg_type, msg_group in grouped_messages.items():
            if len(msg_group) == 1:
                optimized_messages.extend(msg_group)
                continue
            
            # Check if messages can be batched
            if self._can_batch_messages(msg_group):
                batched_msg = await self._create_batched_message(msg_group)
                optimized_messages.append(batched_msg)
            else:
                optimized_messages.extend(msg_group)
        
        return optimized_messages
    
    def _can_batch_messages(self, messages: List[Dict[str, Any]]) -> bool:
        """Check if messages can be safely batched"""
        # Simple heuristic - same type and similar content
        if len(messages) < 2:
            return False
        
        # Check if all messages have same structure
        first_keys = set(messages[0].keys())
        return all(set(msg.keys()) == first_keys for msg in messages)
    
    async def _create_batched_message(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a single batched message from multiple messages"""
        
        # Combine message contents
        combined_content = []
        for i, msg in enumerate(messages):
            combined_content.append(f"Request {i+1}: {msg.get('content', '')}")
        
        batched_message = {
            'type': 'batched_request',
            'content': '\n'.join(combined_content),
            'original_count': len(messages),
            'batch_id': hashlib.md5(str(messages).encode()).hexdigest()[:8]
        }
        
        return batched_message


class CompressedWorker:
    """Worker for handling compressed A2A message processing"""
    
    def __init__(self, token_manager: TokenManager):
        self.token_manager = token_manager
        self.logger = logging.getLogger("bruno.compressed_worker")
        self.batch_size = 5
        self.batch_timeout = 30  # seconds
        
    async def process_message_batch(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a batch of messages with optimization"""
        
        if not messages:
            return []
        
        # Optimize the batch
        optimized_messages = await self.token_manager.optimize_batch_messages(messages)
        
        results = []
        for msg in optimized_messages:
            try:
                # Process each message with token optimization
                content = msg.get('content', '')
                result, metrics = await self.token_manager.process_with_routing(
                    content, 
                    context_id=msg.get('context_id')
                )
                
                results.append({
                    'success': True,
                    'result': result,
                    'metrics': metrics,
                    'message_id': msg.get('id'),
                    'processing_time': metrics.processing_time
                })
                
            except Exception as e:
                self.logger.error(f"Failed to process message {msg.get('id')}: {e}")
                results.append({
                    'success': False,
                    'error': str(e),
                    'message_id': msg.get('id')
                })
        
        return results
    
    async def start_batch_processor(self):
        """Start the batch processor for continuous operation"""
        self.logger.info("Starting compressed worker batch processor")
        
        # This would be integrated with the A2A message queue
        # For now, it's a placeholder for the architecture
        pass


# Global token manager instance
token_manager = None

def get_token_manager() -> TokenManager:
    """Get the global token manager instance"""
    global token_manager
    if token_manager is None:
        raise RuntimeError("Token manager not initialized")
    return token_manager

def initialize_token_manager(redis_url: str, postgres_url: str, anthropic_api_key: str):
    """Initialize the global token manager"""
    global token_manager
    token_manager = TokenManager(redis_url, postgres_url, anthropic_api_key)
    return token_manager
