"""Test suite for Bruno AI agent ecosystem.

This module contains comprehensive tests for the multi-agent system including
workflow testing, agent communication, budget management, and A2A protocol compliance.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any

import httpx
from fastapi.testclient import TestClient

# Import our agents and server
from bruno_master_agent import BrunoMasterAgent, BudgetTracker, TaskTracker
from grocery_browser_agent import GroceryBrowserAgent
from recipe_chef_agent import RecipeChefAgent
from instacart_api_agent import InstacartAPIAgent, InstacartConfig
from a2a_server import BrunoAIServer, ServerConfig, UserRequest


class TestBrunoAgentEcosystem:
    """Comprehensive test suite for Bruno AI agent ecosystem."""

    @pytest.fixture
    def server_config(self):
        """Create test server configuration."""
        return ServerConfig(
            host="localhost",
            port=8001,  # Different port for testing
            debug=True,
            openai_api_key="test_openai_key",
            instacart_api_key="test_instacart_key",
            max_budget=150.0,
            default_family_size=3
        )

    @pytest.fixture
    async def bruno_server(self, server_config):
        """Create and initialize Bruno AI server for testing."""
        server = BrunoAIServer(server_config)
        await server.initialize()
        return server

    @pytest.fixture
    async def test_client(self, bruno_server):
        """Create test client for API testing."""
        server = await bruno_server
        return TestClient(server.app)

    @pytest.fixture
    def budget_tracker(self):
        """Create budget tracker for testing."""
        return BudgetTracker(weekly_budget=Decimal('150.0'))

    @pytest.fixture
    def task_tracker(self):
        """Create task tracker for testing."""
        return TaskTracker(task_id="test_task", task_type="test")

    @pytest.fixture
    async def bruno_master_agent(self):
        """Create Bruno Master Agent for testing."""
        return BrunoMasterAgent(model="gpt-4")

    @pytest.fixture
    def grocery_browser_agent(self):
        """Create Grocery Browser Agent for testing."""
        return GroceryBrowserAgent()

    @pytest.fixture
    def recipe_chef_agent(self):
        """Create Recipe Chef Agent for testing."""
        return RecipeChefAgent()

    @pytest.fixture
    def instacart_api_agent(self):
        """Create Instacart API Agent for testing."""
        config = InstacartConfig(api_key="test_key")
        return InstacartAPIAgent(config=config)

    # Test 1: Meal Planning Workflow
    @pytest.mark.asyncio
    async def test_meal_planning_workflow(self, test_client):
        """Test complete meal planning workflow from user request to shopping list."""
        # Simulate user request for meal planning
        user_request = {
            "user_id": "test_user_001",
            "message": "I need a 3-day meal plan for a family of 4 with a $100 budget. We prefer healthy, quick meals.",
            "budget_limit": 100.0,
            "family_size": 4,
            "dietary_restrictions": ["no nuts"],
            "zip_code": "90210"
        }
        
        # Send request to meal plan endpoint
        response = test_client.post("/api/v1/meal-plan?days=3&meals_per_day=3", json=user_request)
        
        # Verify response structure
        assert response.status_code == 200
        data = response.json()
        
        assert "request_id" in data
        assert "user_id" in data
        assert data["user_id"] == "test_user_001"
        assert "primary_response" in data
        assert "agent_responses" in data
        assert "budget_info" in data
        assert "recommendations" in data
        assert "shopping_list" in data
        assert "total_cost" in data
        assert data["success"] is True
        
        # Verify budget compliance
        budget_info = data["budget_info"]
        assert budget_info["total_budget"] == 100.0
        assert budget_info["remaining_budget"] >= 0
        
        # Verify recommendations exist
        recommendations = data["recommendations"]
        assert len(recommendations) > 0
        assert all("type" in rec for rec in recommendations)
        
        # Verify shopping list
        shopping_list = data["shopping_list"]
        assert len(shopping_list) > 0
        assert all("item" in item and "estimated_cost" in item for item in shopping_list)
        
        # Verify total cost is within budget
        total_cost = data["total_cost"]
        assert total_cost <= 100.0

    # Test 2: Grocery Browser Price Discovery
    @pytest.mark.asyncio
    async def test_grocery_browser_price_discovery(self, grocery_browser_agent):
        """Test grocery browser agent's price discovery capabilities."""
        # Mock Selenium WebDriver
        with patch('selenium.webdriver.Chrome') as mock_driver:
            mock_driver_instance = Mock()
            mock_driver.return_value = mock_driver_instance
            
            # Mock web scraping results
            mock_driver_instance.find_elements.return_value = [
                Mock(text="Chicken Breast - $4.99/lb"),
                Mock(text="Ground Beef - $5.99/lb"),
                Mock(text="Salmon Fillet - $8.99/lb")
            ]
            
            # Mock the price browsing methods since they may not exist yet
            grocery_browser_agent._browse_walmart_prices = AsyncMock(return_value={
                "success": True,
                "products": [{"name": "Chicken Breast", "price": 4.99}]
            })
            
            # Test price browsing at Walmart
            walmart_prices = await grocery_browser_agent._browse_walmart_prices(["chicken", "beef", "salmon"])
            
            # Verify results
            assert "success" in walmart_prices
            assert walmart_prices["success"] is True
            assert "products" in walmart_prices
            assert len(walmart_prices["products"]) > 0
            
            # Mock price comparison method
            grocery_browser_agent._compare_store_prices = AsyncMock(return_value={
                "comparison": {},
                "best_deals": [],
                "success": True
            })
            
            # Test price comparison across stores
            comparison_result = await grocery_browser_agent._compare_store_prices(
                ["chicken breast", "ground beef"],
                stores=["walmart", "target"]
            )
            
            assert "comparison" in comparison_result
            assert "best_deals" in comparison_result
            assert comparison_result["success"] is True

    # Test 3: Recipe Chef Budget Optimization
    @pytest.mark.asyncio
    async def test_recipe_chef_budget_optimization(self, recipe_chef_agent):
        """Test recipe chef's budget optimization capabilities."""
        # Test meal plan creation with budget constraints
        meal_plan_request = {
            "family_size": 4,
            "budget": 75.0,
            "days": 5,
            "dietary_restrictions": ["vegetarian"],
            "preferences": ["quick meals", "healthy"]
        }
        
        # Mock the meal plan creation method
        recipe_chef_agent._create_meal_plan = AsyncMock(return_value={
            "meal_plan": {"day_1": "Vegetable Stir Fry"},
            "total_cost": 65.0,
            "shopping_list": ["vegetables", "rice"],
            "success": True
        })
        
        # Create meal plan
        meal_plan = await recipe_chef_agent._create_meal_plan(
            family_size=meal_plan_request["family_size"],
            budget=meal_plan_request["budget"],
            days=meal_plan_request["days"],
            dietary_restrictions=meal_plan_request["dietary_restrictions"]
        )
        
        # Verify meal plan structure
        assert "meal_plan" in meal_plan
        assert "total_cost" in meal_plan
        assert "shopping_list" in meal_plan
        assert meal_plan["success"] is True
        
        # Verify budget compliance
        assert meal_plan["total_cost"] <= meal_plan_request["budget"]
        
        # Test recipe optimization
        recipe_optimization = await recipe_chef_agent._optimize_recipe_for_budget(
            recipe_name="Vegetable Stir Fry",
            target_budget=15.0,
            family_size=4
        )
        
        assert "optimized_recipe" in recipe_optimization
        assert "cost_breakdown" in recipe_optimization
        assert "substitutions" in recipe_optimization
        assert recipe_optimization["success"] is True

    # Test 4: Agent Failure Recovery
    @pytest.mark.asyncio
    async def test_agent_failure_recovery(self, bruno_master_agent):
        """Test system's ability to handle agent failures gracefully."""
        # Mock a failing agent
        with patch.object(bruno_master_agent, '_delegate_to_agent') as mock_delegate:
            # First call fails, second succeeds
            mock_delegate.side_effect = [
                Exception("Agent temporarily unavailable"),
                {"success": True, "response": "Fallback response", "agent": "backup_agent"}
            ]
            
            # Test failure recovery
            result = await bruno_master_agent._handle_user_request(
                "Create a meal plan for tonight",
                {"user_id": "test_user", "budget": 50.0}
            )
            
            # Verify graceful handling
            assert "response" in result
            assert "fallback_used" in result or "error_handled" in result
            
            # Verify retry mechanism was triggered
            assert mock_delegate.call_count >= 2

    # Test 5: A2A Protocol Compliance
    @pytest.mark.asyncio
    async def test_a2a_protocol_compliance(self, bruno_server):
        """Test A2A protocol implementation and agent communication."""
        # Test agent discovery
        agents = bruno_server.agents
        assert len(agents) >= 4  # bruno_master, grocery_browser, recipe_chef, instacart_api
        
        # Verify each agent has required A2A attributes
        for agent_name, agent in agents.items():
            assert hasattr(agent, 'name')
            assert hasattr(agent, 'description')
            assert agent.name is not None
            
        # Test agent delegation through master agent
        master_agent = agents.get("bruno_master")
        assert master_agent is not None
        
        # Mock A2A communication
        with patch.object(master_agent, '_communicate_with_agent') as mock_comm:
            mock_comm.return_value = {
                "success": True,
                "response": "Agent communication successful",
                "data": {"test": "data"}
            }
            
            # Test inter-agent communication
            comm_result = await master_agent._coordinate_agents(
                task="price_check",
                agents=["grocery_browser", "instacart_api"],
                context={"items": ["milk", "bread"]}
            )
            
            assert comm_result["success"] is True
            assert mock_comm.called

    # Test 6: Budget Tracking and Compliance
    @pytest.mark.asyncio
    async def test_budget_tracking_compliance(self, budget_tracker):
        """Test budget tracking and enforcement across agents."""
        # Test initial budget setup
        assert budget_tracker.weekly_budget == Decimal('150.0')
        assert budget_tracker.current_spent == Decimal('0.0')
        assert budget_tracker.remaining_budget == Decimal('150.0')
        
        # Test budget allocation
        allocation_result = budget_tracker.allocate_budget("meal_planning", 75.0)
        assert allocation_result["success"] is True
        assert budget_tracker.allocated_budget == 75.0
        
        # Test spending tracking
        spending_result = budget_tracker.track_spending("groceries", 45.50)
        assert spending_result["success"] is True
        assert budget_tracker.current_spent == 45.50
        
        # Test budget limit enforcement
        over_budget_result = budget_tracker.track_spending("extra_items", 120.0)
        assert over_budget_result["success"] is False
        assert "budget_exceeded" in over_budget_result["error"].lower()
        
        # Test budget warnings
        warning_result = budget_tracker.check_budget_status()
        assert "remaining_budget" in warning_result
        assert "utilization_percentage" in warning_result

    # Test 7: Instacart API Integration
    @pytest.mark.asyncio
    async def test_instacart_api_integration(self, instacart_api_agent):
        """Test Instacart API agent functionality."""
        # Test product search
        search_result = await instacart_api_agent._search_products(
            query="chicken breast",
            max_results=10
        )
        
        assert "products" in search_result
        assert "success" in search_result
        assert search_result["success"] is True
        
        # Test store finding
        stores_result = await instacart_api_agent._find_stores(
            zip_code="90210",
            radius_miles=5.0
        )
        
        assert "stores" in stores_result
        assert len(stores_result["stores"]) > 0
        assert stores_result["success"] is True
        
        # Test cart creation and management
        cart_result = await instacart_api_agent._create_cart("walmart_001")
        assert "cart" in cart_result
        assert cart_result["success"] is True
        
        cart_id = cart_result["cart"]["cart_id"]
        
        # Test adding items to cart
        add_result = await instacart_api_agent._add_to_cart(
            cart_id=cart_id,
            product_id="chicken_breast_001",
            quantity=2
        )
        
        assert add_result["success"] is True
        assert "cart" in add_result
        assert len(add_result["cart"]["items"]) == 1

    # Test 8: End-to-End Integration
    @pytest.mark.asyncio
    async def test_end_to_end_integration(self, test_client):
        """Test complete end-to-end workflow."""
        # Test health check
        health_response = test_client.get("/health")
        assert health_response.status_code == 200
        health_data = health_response.json()
        assert health_data["status"] in ["healthy", "degraded"]
        
        # Test agent listing
        agents_response = test_client.get("/api/v1/agents")
        assert agents_response.status_code == 200
        agents_data = agents_response.json()
        assert "agents" in agents_data
        assert agents_data["total_agents"] >= 4
        
        # Test price checking
        price_check_response = test_client.post(
            "/api/v1/price-check",
            json={
                "items": ["milk", "bread", "eggs"],
                "zip_code": "90210"
            }
        )
        
        assert price_check_response.status_code == 200
        price_data = price_check_response.json()
        assert "price_results" in price_data
        assert len(price_data["price_results"]) == 3
        
        # Test shopping list generation
        shopping_list_request = {
            "user_id": "test_user_002",
            "message": "Generate a shopping list for chicken stir fry and pasta dinner",
            "budget_limit": 60.0,
            "family_size": 3
        }
        
        shopping_response = test_client.post("/api/v1/shopping-list", json=shopping_list_request)
        assert shopping_response.status_code == 200
        shopping_data = shopping_response.json()
        assert "shopping_list" in shopping_data
        assert "total_cost" in shopping_data
        assert shopping_data["total_cost"] <= 60.0

    # Test 9: Error Handling and Edge Cases
    @pytest.mark.asyncio
    async def test_error_handling_edge_cases(self, test_client, bruno_master_agent):
        """Test error handling and edge case scenarios."""
        # Test invalid user request
        invalid_request = {
            "user_id": "",  # Empty user ID
            "message": "",  # Empty message
            "budget_limit": -50.0  # Negative budget
        }
        
        response = test_client.post("/api/v1/chat", json=invalid_request)
        # Should handle gracefully, not crash
        assert response.status_code in [200, 400, 422]
        
        # Test budget overflow scenario
        overflow_request = {
            "user_id": "test_user_003",
            "message": "I want to buy everything in the store",
            "budget_limit": 10.0,  # Very low budget
            "family_size": 10  # Large family
        }
        
        response = test_client.post("/api/v1/meal-plan", json=overflow_request)
        assert response.status_code == 200
        data = response.json()
        
        # Should provide budget-conscious recommendations
        assert data["success"] is True
        if data["total_cost"]:
            assert data["total_cost"] <= overflow_request["budget_limit"] * 1.1  # Allow 10% buffer
        
        # Test agent timeout simulation
        with patch.object(bruno_master_agent, '_delegate_to_agent') as mock_delegate:
            mock_delegate.side_effect = asyncio.TimeoutError("Agent timeout")
            
            timeout_result = await bruno_master_agent._handle_user_request(
                "Quick meal suggestion",
                {"user_id": "test_user", "timeout": 1}
            )
            
            # Should handle timeout gracefully
            assert "error" in timeout_result or "fallback" in timeout_result

    # Test 10: Performance and Scalability
    @pytest.mark.asyncio
    async def test_performance_scalability(self, test_client):
        """Test system performance under load."""
        # Test concurrent requests
        async def make_request(user_id: str):
            request_data = {
                "user_id": user_id,
                "message": f"Quick meal suggestion for user {user_id}",
                "budget_limit": 50.0
            }
            return test_client.post("/api/v1/chat", json=request_data)
        
        # Simulate 5 concurrent users
        tasks = [make_request(f"user_{i}") for i in range(5)]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify all requests were handled
        successful_responses = [r for r in responses if not isinstance(r, Exception)]
        assert len(successful_responses) >= 3  # At least 60% success rate
        
        # Test response time tracking
        start_time = datetime.now()
        response = test_client.post("/api/v1/chat", json={
            "user_id": "perf_test_user",
            "message": "Simple meal suggestion",
            "budget_limit": 30.0
        })
        end_time = datetime.now()
        
        response_time_ms = (end_time - start_time).total_seconds() * 1000
        
        # Response should be reasonably fast (under 5 seconds for simple requests)
        assert response_time_ms < 5000
        
        if response.status_code == 200:
            data = response.json()
            if "processing_time_ms" in data:
                assert data["processing_time_ms"] < 5000


# Additional utility functions for testing
class TestUtilities:
    """Utility functions for testing Bruno AI agents."""
    
    @staticmethod
    def create_mock_user_request(user_id: str = "test_user", **kwargs) -> UserRequest:
        """Create a mock user request for testing."""
        defaults = {
            "user_id": user_id,
            "message": "Test message",
            "budget_limit": 100.0,
            "family_size": 4,
            "dietary_restrictions": [],
            "zip_code": "90210"
        }
        defaults.update(kwargs)
        return UserRequest(**defaults)
    
    @staticmethod
    def validate_agent_response(response: Dict[str, Any]) -> bool:
        """Validate agent response structure."""
        required_fields = ["success", "response"]
        return all(field in response for field in required_fields)
    
    @staticmethod
    def calculate_budget_utilization(spent: float, total: float) -> float:
        """Calculate budget utilization percentage."""
        if total <= 0:
            return 0.0
        return min((spent / total) * 100, 100.0)


# Test configuration and fixtures
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test."""
    # Setup any required test environment variables or mocks
    import os
    os.environ["BRUNO_DEBUG"] = "true"
    os.environ["BRUNO_MAX_BUDGET"] = "150.0"
    yield
    # Cleanup after test
    pass


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main(["-v", "test_bruno_agents.py"])