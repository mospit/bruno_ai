import pytest
import os
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import sys
import httpx

# Add the agents directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from instacart_integration_agent import InstacartIntegrationAgentV2, RateLimiter
from base_agent import AgentCard

class TestInstacartIntegrationAgentV2:
    @pytest.fixture
    def mock_redis(self):
        mock_redis = MagicMock()
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True
        return mock_redis
    
    @pytest.fixture
    def agent(self, mock_redis):
        with patch('instacart_integration_agent.redis.from_url', return_value=mock_redis):
            with patch.dict(os.environ, {
                'GEMINI_API_KEY': 'test_key',
                'INSTACART_API_KEY': 'test_instacart_key',
                'INSTACART_AFFILIATE_ID': 'test_affiliate'
            }):
                with patch('instacart_integration_agent.genai.configure'):
                    with patch('instacart_integration_agent.genai.GenerativeModel'):
                        agent = InstacartIntegrationAgentV2()
                        agent.redis_client = mock_redis
                        return agent
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly"""
        assert agent.agent_card.name == "Instacart Integration Agent"
        assert agent.agent_card.version == "2.0.0"
        assert "comprehensive_product_search" in [skill["id"] for skill in agent.agent_card.capabilities["skills"]]
        assert agent.api_base_url == "https://connect.instacart.com/v1"
        assert agent.api_key == "test_instacart_key"
        assert agent.affiliate_id == "test_affiliate"
    
    @pytest.mark.asyncio
    async def test_product_search_optimized(self, agent):
        """Test optimized product search functionality"""
        query = "organic chicken breast"
        filters = {"category": "meat", "price_max": 15.00}
        location = "12345"
        
        # Mock API response
        mock_api_response = {
            "results": [
                {
                    "id": "chicken_001",
                    "name": "Organic Chicken Breast",
                    "price": 12.99,
                    "availability": True,
                    "store_id": "whole_foods_001"
                },
                {
                    "id": "chicken_002",
                    "name": "Free Range Chicken Breast",
                    "price": 14.50,
                    "availability": True,
                    "store_id": "kroger_001"
                }
            ]
        }
        
        # Mock enriched product data
        mock_enriched_data = [
            {
                "id": "chicken_001",
                "name": "Organic Chicken Breast",
                "price": 12.99,
                "availability": True,
                "price_history": [13.50, 12.99, 13.25],
                "alternatives": [],
                "nutrition_score": 0.9,
                "value_rating": 0.85
            }
        ]
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_api_response
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            with patch.object(agent, '_enrich_product_data') as mock_enrich:
                mock_enrich.return_value = mock_enriched_data
                
                with patch.object(agent.rate_limiter, 'acquire') as mock_rate_limit:
                    result = await agent.search_products_optimized(query, filters, location)
        
        assert "products" in result
        assert result["total_found"] == 1
        assert result["search_query"] == query
        assert result["cached"] is False
        assert len(result["products"]) == 1
        assert result["products"][0]["nutrition_score"] == 0.9
    
    @pytest.mark.asyncio
    async def test_product_search_cached_result(self, agent):
        """Test product search with cached result"""
        query = "pasta"
        
        # Mock cached result
        cached_result = {
            "products": [{"name": "Barilla Pasta", "price": 1.99}],
            "total_found": 1,
            "cached": True
        }
        
        with patch.object(agent.cache_manager, 'get_with_strategy') as mock_cache:
            mock_cache.return_value = cached_result
            
            result = await agent.search_products_optimized(query)
            
            assert result == cached_result
            mock_cache.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_optimized_shopping_list(self, agent):
        """Test optimized shopping list creation"""
        items = [
            {"name": "chicken breast", "quantity": 2},
            {"name": "pasta", "quantity": 1},
            {"name": "tomato sauce", "quantity": 2}
        ]
        budget = 25.0
        preferences = {"cost_priority": True, "delivery_speed": "standard"}
        
        # Mock store price comparison
        mock_store_prices = {
            "store_1": {
                "store_info": {"name": "Whole Foods", "distance": 2.3},
                "items": [
                    {"item": "chicken breast", "price": 12.99, "availability": True},
                    {"item": "pasta", "price": 2.49, "availability": True}
                ],
                "total_cost": 15.48
            }
        }
        
        # Mock optimization result
        mock_optimization = {
            "cost_savings": 3.50,
            "convenience_score": 0.8,
            "delivery_details": {"estimated_time": "2 hours", "fee": 3.99}
        }
        
        # Mock shopping lists
        mock_shopping_lists = {
            "store_1": {
                "store_name": "Whole Foods",
                "items": items,
                "subtotal": 15.48,
                "delivery_fee": 3.99,
                "total": 19.47
            }
        }
        
        # Mock shopping experience
        mock_experience = {
            "total_cost": 19.47,
            "savings": 5.53,
            "delivery_options": ["standard", "priority"],
            "urls": ["https://instacart.com/store/whole-foods"]
        }
        
        with patch.object(agent, '_compare_prices_across_stores') as mock_compare:
            mock_compare.return_value = mock_store_prices
            
            with patch.object(agent, '_optimize_store_selection_internal') as mock_optimize:
                mock_optimize.return_value = mock_optimization
                
                with patch.object(agent, '_create_store_shopping_lists') as mock_lists:
                    mock_lists.return_value = mock_shopping_lists
                    
                    with patch.object(agent, '_generate_shopping_experience') as mock_experience_gen:
                        mock_experience_gen.return_value = mock_experience
                        
                        result = await agent.create_optimized_shopping_list(items, budget, preferences)
        
        assert result["success"] is True
        assert result["total_cost"] == 19.47
        assert result["estimated_savings"] == 5.53
        assert result["budget_status"]["under_budget"] is True
        assert result["budget_status"]["target_budget"] == budget
        assert "optimization_details" in result
    
    @pytest.mark.asyncio
    async def test_monitor_deals_and_prices(self, agent):
        """Test deal monitoring functionality"""
        products = ["chicken breast", "ground beef", "salmon"]
        user_id = "test_user"
        
        # Mock price thresholds
        mock_thresholds = {
            "chicken breast": {"target_price": 8.99, "current_price": 12.99},
            "ground beef": {"target_price": 6.99, "current_price": 7.99},
            "salmon": {"target_price": 15.99, "current_price": 18.99}
        }
        
        # Mock deal predictions
        mock_predictions = [
            {"product": "chicken breast", "predicted_sale_date": "2025-01-15", "predicted_discount": 0.20},
            {"product": "salmon", "predicted_sale_date": "2025-01-20", "predicted_discount": 0.15}
        ]
        
        # Mock current deals
        mock_current_deals = [
            {"product": "ground beef", "current_discount": 0.10, "store": "Kroger"}
        ]
        
        # Mock savings opportunities
        mock_savings = [
            {"opportunity": "bulk_purchase", "product": "chicken breast", "potential_savings": 2.50}
        ]
        
        with patch.object(agent, '_calculate_price_thresholds') as mock_thresholds_calc:
            mock_thresholds_calc.return_value = mock_thresholds
            
            with patch.object(agent, '_predict_upcoming_deals') as mock_predictions_calc:
                mock_predictions_calc.return_value = mock_predictions
                
                with patch.object(agent, '_setup_price_monitoring') as mock_setup:
                    mock_setup.return_value = None
                    
                    with patch.object(agent, '_analyze_current_deals') as mock_analyze:
                        mock_analyze.return_value = mock_current_deals
                        
                        with patch.object(agent, '_identify_savings_opportunities') as mock_identify:
                            mock_identify.return_value = mock_savings
                            
                            result = await agent.monitor_deals_and_prices(products, user_id)
        
        assert result["monitoring_active"] is True
        assert len(result["current_deals"]) == 1
        assert len(result["predicted_deals"]) == 2
        assert len(result["savings_opportunities"]) == 1
        assert "monitoring_id" in result
        assert result["alert_preferences"]["price_drop_threshold"] == 15
    
    @pytest.mark.asyncio
    async def test_order_lifecycle_create(self, agent):
        """Test order creation"""
        order_data = {
            "items": [
                {"product_id": "chicken_001", "quantity": 2},
                {"product_id": "pasta_001", "quantity": 1}
            ],
            "store_id": "whole_foods_001",
            "delivery_address": "123 Main St",
            "delivery_time": "2025-01-15 14:00:00"
        }
        
        mock_order_result = {
            "order_id": "order_123456",
            "status": "confirmed",
            "estimated_delivery": "2025-01-15 14:30:00",
            "total_cost": 28.47,
            "tracking_url": "https://instacart.com/orders/123456"
        }
        
        with patch.object(agent, '_create_instacart_order') as mock_create:
            mock_create.return_value = mock_order_result
            
            result = await agent.manage_order_lifecycle(order_data, "create")
            
            assert result["order_id"] == "order_123456"
            assert result["status"] == "confirmed"
            assert result["total_cost"] == 28.47
    
    @pytest.mark.asyncio
    async def test_order_lifecycle_track(self, agent):
        """Test order tracking"""
        order_data = {"order_id": "order_123456"}
        
        mock_tracking_result = {
            "order_id": "order_123456",
            "status": "in_progress",
            "delivery_eta": "2025-01-15 14:45:00",
            "shopper_notes": "Found all items except organic tomatoes, substituted with regular",
            "current_location": "En route to delivery address"
        }
        
        with patch.object(agent, '_track_order_status') as mock_track:
            mock_track.return_value = mock_tracking_result
            
            result = await agent.manage_order_lifecycle(order_data, "track")
            
            assert result["order_id"] == "order_123456"
            assert result["status"] == "in_progress"
            assert "delivery_eta" in result
    
    @pytest.mark.asyncio
    async def test_store_selection_optimization(self, agent):
        """Test store selection optimization"""
        items = [{"name": "chicken breast"}, {"name": "pasta"}]
        location = "12345"
        preferences = {
            "cost_weight": 0.5,
            "convenience_weight": 0.3,
            "speed_weight": 0.2
        }
        
        # Mock stores data
        mock_stores = [
            {"id": "store_1", "name": "Whole Foods", "distance": 2.3, "rating": 4.5},
            {"id": "store_2", "name": "Kroger", "distance": 1.8, "rating": 4.2}
        ]
        
        # Mock individual scores
        mock_scores = {
            "store_1": {"cost": 0.7, "convenience": 0.8, "delivery": 0.9, "quality": 0.9},
            "store_2": {"cost": 0.9, "convenience": 0.7, "delivery": 0.8, "quality": 0.8}
        }
        
        with patch.object(agent, '_get_stores_in_location') as mock_get_stores:
            mock_get_stores.return_value = mock_stores
            
            with patch.object(agent, '_calculate_cost_score') as mock_cost:
                mock_cost.side_effect = [0.7, 0.9]
                
                with patch.object(agent, '_calculate_convenience_score') as mock_convenience:
                    mock_convenience.side_effect = [0.8, 0.7]
                    
                    with patch.object(agent, '_calculate_delivery_score') as mock_delivery:
                        mock_delivery.side_effect = [0.9, 0.8]
                        
                        with patch.object(agent, '_calculate_quality_score') as mock_quality:
                            mock_quality.side_effect = [0.9, 0.8]
                            
                            result = await agent.optimize_store_selection(items, location, preferences)
        
        assert "recommended_stores" in result
        assert len(result["recommended_stores"]) <= 3
        assert result["total_stores_analyzed"] == 2
        assert "optimization_factors" in result
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self, agent):
        """Test API error handling"""
        query = "test product"
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 429  # Rate limit error
            mock_response.json.return_value = {"message": "Rate limit exceeded"}
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            with patch.object(agent.rate_limiter, 'acquire'):
                result = await agent.search_products_optimized(query)
        
        assert result["success"] is False
        assert "Rate limit exceeded" in result["error"]
        assert result["fallback_available"] is True
    
    @pytest.mark.asyncio
    async def test_exception_handling(self, agent):
        """Test exception handling"""
        query = "test product"
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = Exception("Network error")
            
            with patch.object(agent.rate_limiter, 'acquire'):
                result = await agent.search_products_optimized(query)
        
        assert result["success"] is False
        assert "Network error" in result["error"]
        assert result["fallback_available"] is True
        assert "recommendations" in result
    
    @pytest.mark.asyncio
    async def test_unknown_action_handling(self, agent):
        """Test handling of unknown actions"""
        task = {
            "action": "unknown_action",
            "context": {}
        }
        
        with pytest.raises(ValueError, match="Unknown action: unknown_action"):
            await agent.execute_task(task)
    
    def test_cache_key_generation(self, agent):
        """Test cache key generation"""
        key1 = agent._generate_cache_key("search", "chicken", {"category": "meat"}, "12345")
        key2 = agent._generate_cache_key("search", "chicken", {"category": "meat"}, "12345")
        key3 = agent._generate_cache_key("search", "beef", {"category": "meat"}, "12345")
        
        # Same inputs should generate same key
        assert key1 == key2
        
        # Different inputs should generate different keys
        assert key1 != key3
        
        # Keys should be valid MD5 hashes (32 characters)
        assert len(key1) == 32
        assert all(c in '0123456789abcdef' for c in key1)
    
    def test_auth_headers_generation(self, agent):
        """Test authentication headers generation"""
        headers = agent._get_auth_headers()
        
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test_instacart_key"
        assert headers["Content-Type"] == "application/json"
        assert headers["User-Agent"] == "Bruno-AI/2.0"
        assert headers["X-Affiliate-ID"] == "test_affiliate"
    
    def test_category_mappings_loading(self, agent):
        """Test category mappings loading"""
        mappings = agent.category_mappings
        
        assert "produce" in mappings
        assert "meat" in mappings
        assert "dairy" in mappings
        assert "fruits" in mappings["produce"]
        assert "chicken" in mappings["meat"]
        assert "milk" in mappings["dairy"]
    
    @pytest.mark.asyncio
    async def test_search_item_across_stores(self, agent):
        """Test searching item across multiple stores"""
        item_name = "chicken breast"
        
        result = await agent._search_item_across_stores(item_name)
        
        assert len(result) >= 2  # Should return multiple stores
        
        for store_result in result:
            assert "store_id" in store_result
            assert "store_info" in store_result
            assert "price" in store_result
            assert "availability" in store_result
            assert store_result["availability"] is True
            assert store_result["price"] > 0

class TestRateLimiter:
    @pytest.fixture
    def rate_limiter(self):
        return RateLimiter(requests_per_hour=10)  # Low limit for testing
    
    @pytest.mark.asyncio
    async def test_rate_limiter_within_limit(self, rate_limiter):
        """Test rate limiter when within limits"""
        # Make a few requests that should be allowed
        for _ in range(5):
            await rate_limiter.acquire()
        
        # Should have 5 requests recorded
        assert len(rate_limiter.requests) == 5
    
    @pytest.mark.asyncio
    async def test_rate_limiter_cleanup(self, rate_limiter):
        """Test rate limiter cleanup of old requests"""
        # Simulate old requests
        old_time = datetime.now() - timedelta(hours=2)
        rate_limiter.requests = [old_time] * 5
        
        # Make a new request
        await rate_limiter.acquire()
        
        # Old requests should be cleaned up, only 1 new request should remain
        assert len(rate_limiter.requests) == 1
        assert all(req_time > old_time for req_time in rate_limiter.requests)
    
    @pytest.mark.asyncio 
    async def test_rate_limiter_at_limit(self, rate_limiter):
        """Test rate limiter behavior when at limit"""
        # Fill up the rate limiter
        for _ in range(10):
            await rate_limiter.acquire()
        
        # This should trigger rate limiting (but we'll mock the sleep to avoid delays)
        with patch('asyncio.sleep') as mock_sleep:
            await rate_limiter.acquire()
            
            # Should have attempted to sleep
            mock_sleep.assert_called_once()
            
            # Should now have 11 requests (cleanup happened)
            assert len(rate_limiter.requests) <= 11
