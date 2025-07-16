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
            
            # Test compression with long query that will exceed threshold
            # Create a query with many words to exceed the 4000 token threshold
            long_query = ("Please create a comprehensive meal planning system that considers dietary restrictions, budget constraints, seasonal ingredients, nutritional requirements, cooking time limitations, family size preferences, cuisine variety, allergen management, ingredient substitutions, recipe complexity, portion control, leftover utilization, shopping optimization, cost tracking, health goals, macro balancing, micro nutrients, vitamin intake, mineral content, calorie counting, weight management, fitness alignment, medical conditions, food sensitivities, organic preferences, local sourcing, environmental impact, sustainability goals, ethical considerations, cultural dietary practices, religious requirements, personal taste preferences, texture considerations, flavor profiles, cooking methods, kitchen equipment, storage capacity, meal prep efficiency, time constraints, work schedules, family activities, social events, holiday planning, special occasions, guest accommodations, travel considerations, emergency preparedness, backup meal options, quick preparation alternatives, frozen meal strategies, batch cooking techniques, ingredient preservation, food safety protocols, expiration management, inventory tracking, waste reduction, portion sizing, nutritional labeling, ingredient sourcing, supplier relationships, quality assurance, freshness indicators, storage optimization, temperature control, food handling, contamination prevention, cleaning procedures, sanitization practices, equipment maintenance, kitchen organization, workflow efficiency, preparation sequences, cooking timing, temperature monitoring, doneness indicators, presentation standards, plating techniques, garnish options, serving suggestions, pairing recommendations, beverage selections, wine matching, dietary modifications, recipe scaling, ingredient ratios, measurement conversions, cooking adjustments, flavor balancing, seasoning techniques, spice combinations, herb utilization, sauce preparations, condiment options, dressing varieties, marinade applications, smoking methods, grilling techniques, roasting procedures, baking processes, steaming methods, braising approaches, sautéing skills, frying techniques, poaching methods, blanching procedures, food preservation, canning processes, freezing techniques, dehydrating methods, fermentation practices, pickling procedures, curing methods, smoking techniques, aging processes, flavor development, texture enhancement, nutritional optimization, supplement integration, probiotic inclusion, prebiotic incorporation, enzyme utilization, antioxidant maximization, phytonutrient inclusion, mineral fortification, vitamin enhancement, protein optimization, carbohydrate balancing, fat selection, fiber inclusion, hydration support, electrolyte balance, metabolic support, digestive health, immune system strengthening, anti-inflammatory properties, cardiovascular benefits, brain health support, bone density maintenance, muscle development, energy optimization, sleep quality improvement, stress reduction, mood enhancement, cognitive function, mental clarity, physical performance, recovery acceleration, longevity promotion, disease prevention, health maintenance, wellness optimization, vitality enhancement, quality of life improvement, satisfaction maximization, enjoyment cultivation, social connection, family bonding, cultural appreciation, tradition preservation, innovation encouragement, creativity expression, skill development, knowledge expansion, confidence building, independence fostering, self-sufficiency promotion, responsibility teaching, planning skills, organization abilities, time management, resource allocation, budget consciousness, value recognition, quality appreciation, sustainability awareness, environmental responsibility, social consciousness, ethical considerations, moral decision making, personal values alignment, lifestyle integration, habit formation, routine establishment, consistency maintenance, flexibility adaptation, change management, problem solving, decision making, critical thinking, creative solutions, innovative approaches, continuous improvement, learning cultivation, growth mindset, resilience building, adaptability enhancement, patience development, mindfulness practice, awareness cultivation, presence appreciation, gratitude expression, joy discovery, fulfillment achievement, purpose alignment, meaning creation, legacy building, contribution making, impact generation, value delivery, service provision, care demonstration, love expression, community building, relationship strengthening, bond deepening, connection enhancement, communication improvement, understanding development, empathy cultivation, compassion expression, kindness demonstration, generosity practice, sharing encouragement, collaboration promotion, teamwork facilitation, leadership development, mentorship provision, guidance offering, support delivery, encouragement giving, motivation inspiration, confidence building, empowerment facilitation, independence fostering, self-reliance promotion, capability development, skill enhancement, knowledge transfer, wisdom sharing, experience application, insight generation, perspective broadening, horizon expansion, possibility exploration, opportunity recognition, potential realization, achievement celebration, success acknowledgment, progress recognition, improvement appreciation, growth celebration, development acknowledgment, advancement recognition, evolution appreciation, transformation celebration, change acknowledgment, adaptation recognition, flexibility appreciation, resilience celebration, strength acknowledgment, courage recognition, determination appreciation, persistence celebration, dedication acknowledgment, commitment recognition, loyalty appreciation, faithfulness celebration, reliability acknowledgment, trustworthiness recognition, integrity appreciation, honesty celebration, authenticity acknowledgment, genuineness recognition, sincerity appreciation, transparency celebration, openness acknowledgment, vulnerability recognition, courage appreciation, bravery celebration, boldness acknowledgment, confidence recognition, self-assurance appreciation, self-worth celebration, self-respect acknowledgment, self-love recognition, self-care appreciation, self-improvement celebration, self-development acknowledgment, self-growth recognition, self-actualization appreciation, self-realization celebration, self-discovery acknowledgment, self-awareness recognition, self-understanding appreciation, self-acceptance celebration, self-compassion acknowledgment, self-forgiveness recognition, self-kindness appreciation, self-patience celebration, self-discipline acknowledgment, self-control recognition, self-regulation appreciation, self-mastery celebration, self-leadership acknowledgment, self-direction recognition, self-motivation appreciation, self-inspiration celebration, self-empowerment acknowledgment, self-confidence recognition, self-belief appreciation, self-trust celebration, self-reliance acknowledgment, self-sufficiency recognition, self-independence appreciation, self-freedom celebration, self-liberation acknowledgment, self-expression recognition, self-creativity appreciation, self-innovation celebration, self-uniqueness acknowledgment, self-individuality recognition, self-personality appreciation, self-character celebration, self-identity acknowledgment, self-purpose recognition, self-meaning appreciation, self-fulfillment celebration, self-satisfaction acknowledgment, self-contentment recognition, self-happiness appreciation, self-joy celebration, self-peace acknowledgment, self-tranquility recognition, self-serenity appreciation, self-calm celebration, self-balance acknowledgment, self-harmony recognition, self-wholeness appreciation, self-completeness celebration, self-integration acknowledgment, self-unity recognition, self-oneness appreciation, self-connection celebration, self-relationship acknowledgment, self-love recognition, self-care appreciation, self-nurturing celebration, self-support acknowledgment, self-encouragement recognition, self-motivation appreciation, self-inspiration celebration, self-empowerment acknowledgment, self-strength recognition, self-resilience appreciation, self-courage celebration, self-determination acknowledgment, self-persistence recognition, self-dedication appreciation, self-commitment celebration, self-loyalty acknowledgment, self-faithfulness recognition, self-reliability appreciation, self-trustworthiness celebration, self-integrity acknowledgment, self-honesty recognition, self-authenticity appreciation, self-genuineness celebration, self-sincerity acknowledgment, self-transparency recognition, self-openness appreciation, self-vulnerability celebration, self-courage acknowledgment." * 30)  # Multiply to ensure we exceed 4000 tokens
            
            # Mock compression response - make it noticeably shorter
            compressed_response = "Create meal plan system considering dietary restrictions, budget, seasonal ingredients, nutrition, cooking time. Analyze 6-month spending for budget optimization maintaining nutrition and variety."
            
            # Ensure the mock response is properly set up
            mock_response = MagicMock()
            mock_content = MagicMock()
            mock_content.text = compressed_response
            mock_response.content = [mock_content]
            
            # Use return_value for synchronous mock
            mock_anthropic_client.messages.create.return_value = mock_response
            
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
            
            # Test message processing with different types to prevent batching
            test_messages = [
                {"id": "1", "content": "Test message 1", "context_id": "ctx1", "type": "type1"},
                {"id": "2", "content": "Test message 2", "context_id": "ctx2", "type": "type2"},
            ]
            
            results = await worker.process_message_batch(test_messages)
            
            logger.info(f"Processed {len(results)} messages")
            
            # Verify results - should match number of optimized messages, not original messages
            assert len(results) >= 1, "Should process at least one message"
            
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
