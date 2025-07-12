"""
Unit tests for the main server API endpoints
"""

import pytest
import json
from unittest.mock import AsyncMock, patch, Mock
from fastapi.testclient import TestClient
from httpx import AsyncClient


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self, test_client):
        """Test basic health check"""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert data["version"] == "3.1.0"
    
    def test_health_check_with_dependencies(self, test_client):
        """Test health check includes dependency status"""
        response = test_client.get("/health")
        data = response.json()
        
        # Should include service dependencies
        assert "services" in data
        assert "redis" in data["services"]
        assert "postgres" in data["services"]
        assert "anthropic" in data["services"]


class TestMealPlanningEndpoint:
    """Test meal planning endpoint"""
    
    def test_meal_planning_basic(self, test_client, sample_pantry_data):
        """Test basic meal planning request"""
        request_data = {
            "preferences": ["Italian", "vegetarian"],
            "budget": 50.00,
            "servings": 4,
            "pantry_items": sample_pantry_data["items"]
        }
        
        response = test_client.post("/api/v1/meal-planning", json=request_data)
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "meal_plan" in data
        assert "shopping_list" in data
        assert "budget_analysis" in data
        assert "reflection" in data
    
    def test_meal_planning_missing_preferences(self, test_client):
        """Test meal planning with missing preferences"""
        request_data = {
            "budget": 50.00,
            "servings": 4
        }
        
        response = test_client.post("/api/v1/meal-planning", json=request_data)
        assert response.status_code == 422  # Validation error
    
    def test_meal_planning_invalid_budget(self, test_client):
        """Test meal planning with invalid budget"""
        request_data = {
            "preferences": ["Italian"],
            "budget": -10.00,  # Invalid negative budget
            "servings": 4
        }
        
        response = test_client.post("/api/v1/meal-planning", json=request_data)
        assert response.status_code == 422  # Validation error


class TestPantryEndpoint:
    """Test pantry management endpoint"""
    
    def test_pantry_check(self, test_client):
        """Test checking pantry inventory"""
        response = test_client.get("/api/v1/pantry/check")
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "inventory" in data
        assert "expiring_soon" in data
        assert "suggestions" in data
    
    def test_pantry_add_item(self, test_client):
        """Test adding item to pantry"""
        item_data = {
            "name": "milk",
            "quantity": 1,
            "unit": "gallon",
            "expiry": "2025-01-20"
        }
        
        response = test_client.post("/api/v1/pantry/add", json=item_data)
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "message" in data
    
    def test_pantry_remove_item(self, test_client):
        """Test removing item from pantry"""
        remove_data = {
            "name": "milk",
            "quantity": 1
        }
        
        response = test_client.post("/api/v1/pantry/remove", json=remove_data)
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "message" in data


class TestShoppingEndpoint:
    """Test shopping/Instacart integration endpoint"""
    
    def test_shopping_search(self, test_client):
        """Test searching for products"""
        search_data = {
            "items": ["chicken breast", "pasta"],
            "budget": 25.00,
            "store_preference": "Whole Foods"
        }
        
        response = test_client.post("/api/v1/shopping/search", json=search_data)
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "products" in data
        assert "total_cost" in data
        assert "alternatives" in data
    
    def test_shopping_create_list(self, test_client):
        """Test creating shopping list"""
        list_data = {
            "items": [
                {"name": "chicken breast", "quantity": 2, "unit": "lbs"},
                {"name": "pasta", "quantity": 1, "unit": "box"}
            ],
            "budget": 20.00
        }
        
        response = test_client.post("/api/v1/shopping/create-list", json=list_data)
        assert response.status_code == 200
        data = response.json()
        
        assert "shopping_list" in data
        assert "estimated_total" in data
        assert "delivery_options" in data


class TestBudgetEndpoint:
    """Test budget analysis endpoint"""
    
    def test_budget_analysis(self, test_client, sample_budget_data):
        """Test budget analysis"""
        analysis_data = {
            "monthly_budget": sample_budget_data["monthly_budget"],
            "recent_expenses": sample_budget_data["recent_expenses"]
        }
        
        response = test_client.post("/api/v1/budget/analyze", json=analysis_data)
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "analysis" in data
        assert "recommendations" in data
        assert "forecasts" in data
    
    def test_budget_track_expense(self, test_client):
        """Test tracking new expense"""
        expense_data = {
            "amount": 15.50,
            "category": "groceries",
            "description": "Fresh vegetables",
            "date": "2025-01-12"
        }
        
        response = test_client.post("/api/v1/budget/track-expense", json=expense_data)
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "updated_totals" in data


class TestFeedbackEndpoint:
    """Test feedback processing endpoint"""
    
    def test_feedback_submit(self, test_client, sample_feedback_data):
        """Test submitting feedback"""
        response = test_client.post("/api/v1/feedback/submit", json=sample_feedback_data)
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] == True
        assert "acknowledgment" in data
    
    def test_feedback_analyze(self, test_client):
        """Test analyzing feedback trends"""
        analysis_data = {
            "time_period": "30_days",
            "agent_id": "recipe_chef"
        }
        
        response = test_client.post("/api/v1/feedback/analyze", json=analysis_data)
        assert response.status_code == 200
        data = response.json()
        
        assert "trends" in data
        assert "insights" in data
        assert "recommendations" in data


class TestAgentStatusEndpoint:
    """Test agent status endpoint"""
    
    def test_agent_status(self, test_client):
        """Test getting agent status"""
        response = test_client.get("/api/v1/agents/status")
        assert response.status_code == 200
        data = response.json()
        
        # Check all agents are present
        expected_agents = [
            "pantry_manager",
            "instacart_integration", 
            "recipe_chef",
            "budget_analyst",
            "reflection_feedback"
        ]
        
        for agent in expected_agents:
            assert agent in data
            assert "status" in data[agent]
            assert "last_activity" in data[agent]
            assert "performance" in data[agent]
    
    def test_specific_agent_status(self, test_client):
        """Test getting specific agent status"""
        response = test_client.get("/api/v1/agents/pantry_manager/status")
        assert response.status_code == 200
        data = response.json()
        
        assert "agent_id" in data
        assert "status" in data
        assert "metrics" in data
        assert data["agent_id"] == "pantry_manager"


class TestCollaborativeEndpoint:
    """Test collaborative multi-agent endpoint"""
    
    def test_collaborative_query(self, test_client):
        """Test collaborative query processing"""
        query_data = {
            "query": "Plan a week of meals for $100 budget using items expiring soon",
            "context": {
                "budget": 100.00,
                "time_frame": "1_week"
            }
        }
        
        response = test_client.post("/api/v1/collaborative/query", json=query_data)
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "response" in data
        assert "agents_involved" in data
        assert "execution_flow" in data
        assert "reflection" in data
    
    def test_collaborative_workflow(self, test_client):
        """Test collaborative workflow execution"""
        workflow_data = {
            "workflow_type": "meal_planning_complete",
            "parameters": {
                "preferences": ["healthy", "quick"],
                "budget": 75.00,
                "servings": 2
            }
        }
        
        response = test_client.post("/api/v1/collaborative/workflow", json=workflow_data)
        assert response.status_code == 200
        data = response.json()
        
        assert "workflow_id" in data
        assert "status" in data
        assert "results" in data


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_json(self, test_client):
        """Test handling of invalid JSON"""
        response = test_client.post(
            "/api/v1/meal-planning",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_missing_required_fields(self, test_client):
        """Test handling of missing required fields"""
        response = test_client.post("/api/v1/meal-planning", json={})
        assert response.status_code == 422
    
    def test_invalid_endpoint(self, test_client):
        """Test handling of invalid endpoint"""
        response = test_client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    def test_method_not_allowed(self, test_client):
        """Test handling of invalid HTTP method"""
        response = test_client.delete("/api/v1/health")
        assert response.status_code == 405


class TestAsyncEndpoints:
    """Test async endpoints using async client"""
    
    @pytest.mark.asyncio
    async def test_async_meal_planning(self, async_test_client):
        """Test meal planning endpoint with async client"""
        request_data = {
            "preferences": ["Italian"],
            "budget": 50.00,
            "servings": 4,
            "pantry_items": []
        }
        
        response = await async_test_client.post("/api/v1/meal-planning", json=request_data)
        assert response.status_code == 200
        data = response.json()
        
        assert "meal_plan" in data
        assert "shopping_list" in data
    
    @pytest.mark.asyncio
    async def test_async_collaborative_query(self, async_test_client):
        """Test collaborative query with async client"""
        query_data = {
            "query": "What can I make with tomatoes and pasta?",
            "context": {}
        }
        
        response = await async_test_client.post("/api/v1/collaborative/query", json=query_data)
        assert response.status_code == 200
        data = response.json()
        
        assert "response" in data
        assert "agents_involved" in data


class TestCORS:
    """Test CORS configuration"""
    
    def test_cors_headers(self, test_client):
        """Test CORS headers are present"""
        response = test_client.options("/api/v1/health")
        
        # Check CORS headers
        assert "Access-Control-Allow-Origin" in response.headers
        assert "Access-Control-Allow-Methods" in response.headers
        assert "Access-Control-Allow-Headers" in response.headers
    
    def test_cors_preflight(self, test_client):
        """Test CORS preflight request"""
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        }
        
        response = test_client.options("/api/v1/meal-planning", headers=headers)
        assert response.status_code == 200
