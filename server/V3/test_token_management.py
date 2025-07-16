#!/usr/bin/env python3
"""
Comprehensive Test Suite for Token Management System - Bruno AI V3.1
Tests token routing, compression, batching, and cost optimization
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Dict, Any, List
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Add the current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TokenManagementTestSuite:
    """Test suite for comprehensive token management validation"""
    
    def __init__(self):
        self.redis_url = "redis://localhost:6379"
        self.postgres_url = "postgresql://localhost:5432/bruno_ai_test"
        self.anthropic_api_key = "test_key"
        
        # Test data
        self.test_queries = [
            {
                "query": "Find me chicken recipes",
                "expected_model": "haiku",
                "expected_tokens": 50,
                "complexity_score": 0.1
            },
            {
                "query": "Analyze my spending patterns over the last 3 months and provide detailed budget optimization recommendations considering my family size, dietary restrictions, and seasonal price variations",
                "expected_model": "sonnet",
                "expected_tokens": 500,
                "complexity_score": 0.9
            },
            {
                "query": "Create a comprehensive 7-day meal plan that optimizes for a $200 budget, accommodates gluten-free dietary restrictions, feeds a family of 4, and includes detailed nutritional analysis with macro breakdowns",
                "expected_model": "sonnet",
                "expected_tokens": 600,
                "complexity_score": 0.8
            }
        ]
        
        self.test_contexts = [
            {
                "budget": 200,
                "dietary_restrictions": ["gluten-free"],
                "family_size": 4,
                "cuisine_preferences": ["Italian", "Mexican"]
            },
            {
                "budget": 150,
                "spending_history": [{"date": "2024-01-01", "amount": 180}],
                "preferences": {"organic": True}
            }
        ]
    
    def mock_anthropic_client(self):
        """Create mock Anthropic client"""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Test response")]
        mock_client.messages.create.return_value = mock_response
        return mock_client
    
    def mock_redis_client(self):
        """Create mock Redis client"""
        mock_client = AsyncMock()
        mock_client.get.return_value = None
        mock_client.set.return_value = True
        mock_client.lpush.return_value = True
        mock_client.expire.return_value = True
        return mock_client
    
    def mock_postgres_conn(self):
        """Create mock PostgreSQL connection"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__ = MagicMock()
        return mock_conn
    
    async def test_token_estimation(self):
        """Test token estimation accuracy"""
        logger.info("Testing token estimation...")
        
        from token_manager import TokenManager
        
        # Mock dependencies
        with patch('redis.asyncio.from_url') as mock_redis, \
             patch('psycopg2.connect') as mock_postgres, \
             patch('anthropic.AsyncAnthropic') as mock_anthropic:
            
            mock_redis.return_value = self.mock_redis_client()
            mock_postgres.return_value = self.mock_postgres_conn()
            mock_anthropic.return_value = self.mock_anthropic_client()
            
            token_manager = TokenManager(
                self.redis_url, 
                self.postgres_url, 
                self.anthropic_api_key
            )
            
            # Test various text lengths
            test_cases = [
                ("Hello world", 3),
                ("This is a longer sentence with more words", 15),
                ("A" * 1000, 280),  # Long string
                ("", 0),  # Empty string
            ]
            
            for text, expected_range in test_cases:
                estimated = token_manager.estimate_tokens(text)
                logger.info(f"Text: '{text[:50]}...' -> Estimated tokens: {estimated}")
                
                # Verify estimation is reasonable
                assert estimated >= 0, "Token estimation should not be negative"
                if text:
                    assert estimated > 0, "Non-empty text should have positive token count"
                
        logger.info("✅ Token estimation tests passed")
    
    async def test_query_complexity_analysis(self):
        """Test query complexity analysis and model routing"""
        logger.info("Testing query complexity analysis...")
        
        from token_manager import TokenManager, ModelType
        
        # Mock dependencies
        with patch('redis.asyncio.from_url') as mock_redis, \
             patch('psycopg2.connect') as mock_postgres, \
             patch('anthropic.AsyncAnthropic') as mock_anthropic:
            
            mock_redis.return_value = self.mock_redis_client()
            mock_postgres.return_value = self.mock_postgres_conn()
            mock_anthropic.return_value = self.mock_anthropic_client()
            
            token_manager = TokenManager(
                self.redis_url, 
                self.postgres_url, 
                self.anthropic_api_key
            )
            
            # Test each query from test data
            for i, test_case in enumerate(self.test_queries):
                query = test_case["query"]
                expected_model = test_case["expected_model"]
                
                # Analyze complexity
                complexity = token_manager.analyze_query_complexity(query)
                
                logger.info(f"Query {i+1}: '{query[:50]}...'")
                logger.info(f"  Token estimate: {complexity.token_estimate}")
                logger.info(f"  Complexity score: {complexity.complexity_score:.2f}")
                logger.info(f"  Recommended model: {complexity.recommended_model.value}")
                logger.info(f"  Confidence: {complexity.confidence:.2f}")
                
                # Verify model selection
                if expected_model == "haiku":
                    assert complexity.recommended_model == ModelType.HAIKU, \
                        f"Expected Haiku for simple query, got {complexity.recommended_model}"
                elif expected_model == "sonnet":
                    assert complexity.recommended_model == ModelType.SONNET, \
                        f"Expected Sonnet for complex query, got {complexity.recommended_model}"
                
                # Verify token estimation is reasonable
                assert complexity.token_estimate > 0, "Token estimate should be positive"
                assert complexity.confidence > 0, "Confidence should be positive"
                
        logger.info("✅ Query complexity analysis tests passed")
    
    async def test_compression_functionality(self):
        """Test query compression"""
        logger.info("Testing query compression...")
        
        from token_manager import TokenManager
        
        # Mock dependencies
        with patch('redis.asyncio.from_url') as mock_redis, \
             patch('psycopg2.connect') as mock_postgres, \
             patch('anthropic.AsyncAnthropic') as mock_anthropic:
            
            mock_redis.return_value = self.mock_redis_client()
            mock_postgres.return_value = self.mock_postgres_conn()
            mock_anthropic_client = self.mock_anthropic_client()
            mock_anthropic.return_value = mock_anthropic_client
            
            token_manager = TokenManager(
                self.redis_url, 
                self.postgres_url, 
                self.anthropic_api_key
            )
            
            # Test compression with long query
            long_query = """
            I need help creating a comprehensive meal planning system that takes into account
            my family's dietary restrictions, budget constraints, seasonal ingredient availability,
            nutritional requirements, and cooking time limitations. Please analyze my spending
            patterns from the last six months and provide detailed recommendations for optimizing
            my grocery budget while maintaining nutritional balance and variety in our meals.
            Consider factors like bulk purchasing opportunities, seasonal price variations,
            and the cost-effectiveness of different protein sources.
            """
            
            # Mock compression response
            mock_anthropic_client.messages.create.return_value.content[0].text = \
                "Create meal plan system considering dietary restrictions, budget, seasonal ingredients, nutrition, cooking time. Analyze 6-month spending for budget optimization maintaining nutrition and variety."
            
            compressed_query, compression_ratio = await token_manager.compress_query(long_query)
            
            logger.info(f"Original query length: {len(long_query)}")
            logger.info(f"Compressed query length: {len(compressed_query)}")
            logger.info(f"Compression ratio: {compression_ratio:.2f}")
            
            # Verify compression worked
            assert len(compressed_query) < len(long_query), "Compressed query should be shorter"
            assert compression_ratio < 1.0, "Compression ratio should be less than 1.0"
            assert compression_ratio > 0, "Compression ratio should be positive"
            
            # Test with short query (should not compress)
            short_query = "Find chicken recipes"
            compressed_short, ratio_short = await token_manager.compress_query(short_query)
            
            assert compressed_short == short_query, "Short query should not be compressed"
            assert ratio_short == 1.0, "Short query compression ratio should be 1.0"
            
        logger.info("✅ Compression functionality tests passed")
    
    async def test_model_routing_with_context(self):
        """Test model routing with context considerations"""
        logger.info("Testing model routing with context...")
        
        from token_manager import TokenManager, ModelType
        
        # Mock dependencies
        with patch('redis.asyncio.from_url') as mock_redis, \
             patch('psycopg2.connect') as mock_postgres, \
             patch('anthropic.AsyncAnthropic') as mock_anthropic:
            
            mock_redis.return_value = self.mock_redis_client()
            mock_postgres.return_value = self.mock_postgres_conn()
            mock_anthropic.return_value = self.mock_anthropic_client()
            
            token_manager = TokenManager(
                self.redis_url, 
                self.postgres_url, 
                self.anthropic_api_key
            )
            
            # Test different contexts
            for context in self.test_contexts:
                # Simple query with budget context should still use Haiku
                simple_query = "Show me today's deals"
                complexity = token_manager.analyze_query_complexity(simple_query, context)
                
                logger.info(f"Context: {context}")
                logger.info(f"Simple query model: {complexity.recommended_model.value}")
                
                # Complex query with budget context should use Sonnet
                complex_query = "Analyze my budget and optimize my spending"
                complexity_complex = token_manager.analyze_query_complexity(complex_query, context)
                
                logger.info(f"Complex query model: {complexity_complex.recommended_model.value}")
                
                # Verify context influences complexity
                assert complexity_complex.complexity_score > complexity.complexity_score, \
                    "Complex query should have higher complexity score"
                
        logger.info("✅ Model routing with context tests passed")
    
    async def test_batch_message_optimization(self):
        """Test A2A message batching"""
        logger.info("Testing batch message optimization...")
        
        from token_manager import TokenManager
        
        # Mock dependencies
        with patch('redis.asyncio.from_url') as mock_redis, \
             patch('psycopg2.connect') as mock_postgres, \
             patch('anthropic.AsyncAnthropic') as mock_anthropic:
            
            mock_redis.return_value = self.mock_redis_client()
            mock_postgres.return_value = self.mock_postgres_conn()
            mock_anthropic.return_value = self.mock_anthropic_client()
            
            token_manager = TokenManager(
                self.redis_url, 
                self.postgres_url, 
                self.anthropic_api_key
            )
            
            # Test messages for batching
            messages = [
                {"type": "price_check", "content": "Check price for chicken", "id": "1"},
                {"type": "price_check", "content": "Check price for beef", "id": "2"},
                {"type": "price_check", "content": "Check price for fish", "id": "3"},
                {"type": "recipe_search", "content": "Find pasta recipes", "id": "4"},
                {"type": "recipe_search", "content": "Find salad recipes", "id": "5"},
            ]
            
            optimized_messages = await token_manager.optimize_batch_messages(messages)
            
            logger.info(f"Original messages: {len(messages)}")
            logger.info(f"Optimized messages: {len(optimized_messages)}")
            
            # Verify batching occurred
            assert len(optimized_messages) < len(messages), \
                "Batching should reduce message count"
            
            # Check for batched messages
            batched_found = False
            for msg in optimized_messages:
                if msg.get("type") == "batched_request":
                    batched_found = True
                    assert "original_count" in msg, "Batched message should have original count"
                    assert "batch_id" in msg, "Batched message should have batch ID"
                    
            assert batched_found, "Should find at least one batched message"
            
        logger.info("✅ Batch message optimization tests passed")
    
    async def test_cost_estimation(self):
        """Test cost estimation accuracy"""
        logger.info("Testing cost estimation...")
        
        from token_manager import TokenManager, ModelType
        
        # Mock dependencies
        with patch('redis.asyncio.from_url') as mock_redis, \
             patch('psycopg2.connect') as mock_postgres, \
             patch('anthropic.AsyncAnthropic') as mock_anthropic:
            
            mock_redis.return_value = self.mock_redis_client()
            mock_postgres.return_value = self.mock_postgres_conn()
            mock_anthropic.return_value = self.mock_anthropic_client()
            
            token_manager = TokenManager(
                self.redis_url, 
                self.postgres_url, 
                self.anthropic_api_key
            )
            
            # Test cost calculation
            test_cases = [
                (1000, ModelType.HAIKU),
                (1000, ModelType.SONNET),
                (5000, ModelType.HAIKU),
                (5000, ModelType.SONNET),
            ]
            
            for tokens, model_type in test_cases:
                cost = (tokens / 1000) * token_manager.COST_PER_1K_TOKENS[model_type]
                
                logger.info(f"Tokens: {tokens}, Model: {model_type.value}, Cost: ${cost:.4f}")
                
                # Verify cost is reasonable
                assert cost > 0, "Cost should be positive"
                assert cost < 1.0, "Cost should be reasonable for test cases"
                
                # Verify Sonnet is more expensive than Haiku
                if model_type == ModelType.SONNET:
                    haiku_cost = (tokens / 1000) * token_manager.COST_PER_1K_TOKENS[ModelType.HAIKU]
                    assert cost > haiku_cost, "Sonnet should be more expensive than Haiku"
                    
        logger.info("✅ Cost estimation tests passed")
    
    async def test_alert_system(self):
        """Test token usage alert system"""
        logger.info("Testing alert system...")
        
        from token_manager import TokenManager
        
        # Mock dependencies
        with patch('redis.asyncio.from_url') as mock_redis, \
             patch('psycopg2.connect') as mock_postgres, \
             patch('anthropic.AsyncAnthropic') as mock_anthropic:
            
            mock_redis_client = self.mock_redis_client()
            mock_redis.return_value = mock_redis_client
            mock_postgres.return_value = self.mock_postgres_conn()
            mock_anthropic.return_value = self.mock_anthropic_client()
            
            token_manager = TokenManager(
                self.redis_url, 
                self.postgres_url, 
                self.anthropic_api_key
            )
            
            # Test alert for high token usage
            high_token_count = 12000
            query_preview = "This is a very long query that uses many tokens"
            
            await token_manager._send_token_alert(high_token_count, query_preview)
            
            # Verify alert was sent to Redis
            mock_redis_client.lpush.assert_called_once()
            mock_redis_client.expire.assert_called_once()
            
            # Verify alert data structure
            call_args = mock_redis_client.lpush.call_args[0]
            alert_data = json.loads(call_args[1])
            
            assert alert_data["type"] == "high_token_usage"
            assert alert_data["token_count"] == high_token_count
            assert alert_data["threshold"] == token_manager.ALERT_THRESHOLD
            assert alert_data["query_preview"] == query_preview
            
        logger.info("✅ Alert system tests passed")
    
    async def test_compressed_worker(self):
        """Test CompressedWorker functionality"""
        logger.info("Testing CompressedWorker...")
        
        from token_manager import TokenManager, CompressedWorker
        
        # Mock dependencies
        with patch('redis.asyncio.from_url') as mock_redis, \
             patch('psycopg2.connect') as mock_postgres, \
             patch('anthropic.AsyncAnthropic') as mock_anthropic:
            
            mock_redis.return_value = self.mock_redis_client()
            mock_postgres.return_value = self.mock_postgres_conn()
            mock_anthropic_client = self.mock_anthropic_client()
            mock_anthropic.return_value = mock_anthropic_client
            
            token_manager = TokenManager(
                self.redis_url, 
                self.postgres_url, 
                self.anthropic_api_key
            )
            
            # Mock the token manager's process_with_routing method
            async def mock_process_with_routing(query, context_id=None, context=None):
                from token_manager import TokenMetrics
                return f"Processed: {query}", TokenMetrics(
                    prompt_tokens=100,
                    completion_tokens=50,
                    total_tokens=150,
                    compression_ratio=0.8,
                    processing_time=0.5,
                    model_used="claude-3-5-haiku-20241022",
                    cost_estimate=0.001,
                    compressed=True
                )
            
            token_manager.process_with_routing = mock_process_with_routing
            
            # Create CompressedWorker
            worker = CompressedWorker(token_manager)
            
            # Test message processing
            test_messages = [
                {"id": "1", "content": "Test message 1", "context_id": "ctx1"},
                {"id": "2", "content": "Test message 2", "context_id": "ctx2"},
            ]
            
            results = await worker.process_message_batch(test_messages)
            
            logger.info(f"Processed {len(results)} messages")
            
            # Verify results
            assert len(results) == len(test_messages), "Should process all messages"
            
            for result in results:
                assert "success" in result, "Result should have success field"
                assert "result" in result or "error" in result, "Result should have result or error"
                assert "message_id" in result, "Result should have message_id"
                
        logger.info("✅ CompressedWorker tests passed")
    
    async def test_statistics_generation(self):
        """Test usage statistics generation"""
        logger.info("Testing statistics generation...")
        
        from token_manager import TokenManager
        
        # Mock dependencies
        with patch('redis.asyncio.from_url') as mock_redis, \
             patch('psycopg2.connect') as mock_postgres, \
             patch('anthropic.AsyncAnthropic') as mock_anthropic:
            
            mock_redis.return_value = self.mock_redis_client()
            mock_postgres_conn = self.mock_postgres_conn()
            mock_postgres.return_value = mock_postgres_conn
            mock_anthropic.return_value = self.mock_anthropic_client()
            
            # Mock cursor results
            mock_cursor = mock_postgres_conn.cursor.return_value.__enter__.return_value
            mock_cursor.fetchall.return_value = [
                ("claude-3-5-haiku-20241022", 100, 50000, 500.0, 0.125, 0.2),
                ("claude-3-5-sonnet-20241022", 50, 75000, 1500.0, 2.25, 0.1),
            ]
            mock_cursor.description = [
                ("model_used",), ("request_count",), ("total_tokens",), 
                ("avg_tokens_per_request",), ("total_cost",), ("compression_rate",)
            ]
            
            token_manager = TokenManager(
                self.redis_url, 
                self.postgres_url, 
                self.anthropic_api_key
            )
            
            # Test statistics generation
            stats = await token_manager.get_usage_statistics(hours=24)
            
            logger.info(f"Statistics: {json.dumps(stats, indent=2)}")
            
            # Verify statistics structure
            assert "period_hours" in stats, "Should have period_hours"
            assert "by_model" in stats, "Should have by_model data"
            assert "totals" in stats, "Should have totals"
            assert "compression_stats" in stats, "Should have compression_stats"
            
            # Verify totals calculation
            expected_total_requests = 150
            expected_total_cost = 2.375
            
            assert stats["totals"]["total_requests"] == expected_total_requests
            assert abs(stats["totals"]["total_cost"] - expected_total_cost) < 0.001
            
        logger.info("✅ Statistics generation tests passed")
    
    async def run_all_tests(self):
        """Run all tests"""
        logger.info("🚀 Starting Token Management Test Suite")
        
        test_methods = [
            self.test_token_estimation,
            self.test_query_complexity_analysis,
            self.test_compression_functionality,
            self.test_model_routing_with_context,
            self.test_batch_message_optimization,
            self.test_cost_estimation,
            self.test_alert_system,
            self.test_compressed_worker,
            self.test_statistics_generation,
        ]
        
        passed = 0
        failed = 0
        
        for test_method in test_methods:
            try:
                await test_method()
                passed += 1
            except Exception as e:
                logger.error(f"❌ {test_method.__name__} failed: {e}")
                failed += 1
        
        logger.info(f"\n🏁 Test Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            logger.info("🎉 All tests passed! Token management system is working correctly.")
        else:
            logger.error(f"⚠️ {failed} tests failed. Please review the errors above.")
        
        return failed == 0


async def main():
    """Main test runner"""
    test_suite = TokenManagementTestSuite()
    success = await test_suite.run_all_tests()
    
    if success:
        print("\n✅ Token Management System - All Tests Passed!")
    else:
        print("\n❌ Token Management System - Some Tests Failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
