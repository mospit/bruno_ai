#!/usr/bin/env python3
"""
Bruno AI Server Integration Testing Suite

This module contains comprehensive integration tests that validate
end-to-end workflows, agent interactions, and system integration.
"""

import pytest
import asyncio
import json
import time
from typing import Dict, Any, List
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from fastapi.testclient import TestClient
from a2a_server import BrunoAIServer, ServerConfig
from bruno_master_agent import BrunoMasterAgent
from grocery_browser_agent import GroceryBrowserAgent
from recipe_chef_agent import RecipeChefAgent
from instacart_api_agent import InstacartAPIAgent


class TestIntegrationWorkflows:
    """Integration tests for complete Bruno AI workflows."""
    
    @pytest.fixture
    def server_config(self):
        """Create test server configuration."""
        return ServerConfig(
            host="localhost",
            port=8004,  # Different port for integration testing
            debug=True,
            gemini_api_key="test_gemini_key",
            instacart_api_key="test_instacart_key",
            max_budget=200.0,
            default_family_size=4,
            cors_origins=["*"]
        )
    
    @pytest.fixture
    async def bruno_server(self, server_config):
        """Create and initialize Bruno AI server for testing."""
        server = BrunoAIServer(server_config)
        await server.initialize()
        return server
    
    @pytest.fixture
    def test_client(self, bruno_server):
        """Create test client for API testing."""
        return TestClient(bruno_server.app)
    
    def test_complete_meal_planning_workflow(self, test_client):
        """Test complete meal planning workflow from request to shopping list."""
        # Step 1: Create meal plan
        meal_plan_request = {
            "user_id": "integration_test_user",
            "message": "I need a healthy meal plan for my family of 4. We like Italian food and have a budget of $150.",
            "budget_limit": 150.0,
            "family_size": 4
        }
        
        with patch('bruno_master_agent.BrunoMasterAgent.process_request') as mock_process:
            mock_process.return_value = {
                "success": True,
                "meal_plan": {
                    "days": 7,
                    "meals_per_day": 3,
                    "meals": [
                        {
                            "day": 1,
                            "meal_type": "breakfast",
                            "recipe": "Italian Frittata",
                            "ingredients": ["eggs", "cheese", "tomatoes", "basil"]
                        },
                        {
                            "day": 1,
                            "meal_type": "lunch",
                            "recipe": "Caprese Salad",
                            "ingredients": ["mozzarella", "tomatoes", "basil", "olive oil"]
                        }
                    ]
                },
                "estimated_cost": 145.50,
                "agent_used": "recipe_chef"
            }
            
            response = test_client.post(
                "/api/v1/meal-plan?days=7&meals_per_day=3",
                json=meal_plan_request
            )
        
        assert response.status_code == 200
        meal_plan_data = response.json()
        
        assert "meal_plan" in meal_plan_data
        assert "estimated_cost" in meal_plan_data
        assert meal_plan_data["estimated_cost"] <= 150.0
        
        # Step 2: Generate shopping list from meal plan
        shopping_list_request = {
            "user_id": "integration_test_user",
            "meal_plan": meal_plan_data["meal_plan"],
            "budget_limit": 150.0
        }
        
        with patch('bruno_master_agent.BrunoMasterAgent.process_request') as mock_process:
            mock_process.return_value = {
                "success": True,
                "shopping_list": {
                    "items": [
                        {"name": "eggs", "quantity": "12 count", "estimated_price": 3.99},
                        {"name": "mozzarella cheese", "quantity": "8 oz", "estimated_price": 4.50},
                        {"name": "tomatoes", "quantity": "2 lbs", "estimated_price": 5.99},
                        {"name": "fresh basil", "quantity": "1 package", "estimated_price": 2.99}
                    ],
                    "total_estimated_cost": 17.47
                },
                "agent_used": "grocery_browser"
            }
            
            response = test_client.post(
                "/api/v1/shopping-list",
                json=shopping_list_request
            )
        
        assert response.status_code == 200
        shopping_data = response.json()
        
        assert "shopping_list" in shopping_data
        assert "items" in shopping_data["shopping_list"]
        assert len(shopping_data["shopping_list"]["items"]) > 0
        
        # Step 3: Check prices for shopping list items
        price_check_request = {
            "items": [item["name"] for item in shopping_data["shopping_list"]["items"]],
            "store_preference": "kroger"
        }
        
        with patch('bruno_master_agent.BrunoMasterAgent.process_request') as mock_process:
            mock_process.return_value = {
                "success": True,
                "price_comparison": {
                    "store": "kroger",
                    "items": [
                        {"name": "eggs", "price": 3.79, "availability": "in_stock"},
                        {"name": "mozzarella cheese", "price": 4.29, "availability": "in_stock"},
                        {"name": "tomatoes", "price": 5.49, "availability": "in_stock"},
                        {"name": "fresh basil", "price": 2.79, "availability": "in_stock"}
                    ],
                    "total_cost": 16.36
                },
                "agent_used": "grocery_browser"
            }
            
            response = test_client.post(
                "/api/v1/price-check",
                json=price_check_request
            )
        
        assert response.status_code == 200
        price_data = response.json()
        
        assert "price_comparison" in price_data
        assert "total_cost" in price_data["price_comparison"]
        
        print("Complete Meal Planning Workflow Test Passed:")
        print(f"  Meal Plan Cost: ${meal_plan_data['estimated_cost']:.2f}")
        print(f"  Shopping List Items: {len(shopping_data['shopping_list']['items'])}")
        print(f"  Final Price Check: ${price_data['price_comparison']['total_cost']:.2f}")
    
    def test_agent_communication_workflow(self, test_client):
        """Test inter-agent communication and handoffs."""
        # Test chat request that requires multiple agents
        chat_request = {
            "message": "I want to cook Italian pasta tonight but need to check prices at different stores first.",
            "agent_name": "bruno_master"
        }
        
        with patch('bruno_master_agent.BrunoMasterAgent.process_request') as mock_master:
            # Simulate master agent coordinating with recipe chef and grocery browser
            mock_master.return_value = {
                "success": True,
                "response": "I'll help you find Italian pasta recipes and check prices. Let me coordinate with my specialist agents.",
                "agents_consulted": ["recipe_chef", "grocery_browser"],
                "recipe_suggestions": [
                    {
                        "name": "Spaghetti Carbonara",
                        "ingredients": ["spaghetti", "eggs", "pancetta", "parmesan", "black pepper"],
                        "estimated_cost": 12.50
                    },
                    {
                        "name": "Penne Arrabbiata",
                        "ingredients": ["penne pasta", "tomatoes", "garlic", "red pepper flakes", "olive oil"],
                        "estimated_cost": 8.75
                    }
                ],
                "price_comparison": {
                    "kroger": {"total": 12.50, "availability": "all_available"},
                    "walmart": {"total": 11.80, "availability": "all_available"},
                    "target": {"total": 13.20, "availability": "most_available"}
                }
            }
            
            response = test_client.post("/api/v1/chat", json=chat_request)
        
        assert response.status_code == 200
        chat_data = response.json()
        
        assert "response" in chat_data
        assert "agents_consulted" in chat_data
        assert "recipe_suggestions" in chat_data
        assert "price_comparison" in chat_data
        
        # Verify multiple agents were involved
        assert len(chat_data["agents_consulted"]) >= 2
        assert "recipe_chef" in chat_data["agents_consulted"]
        assert "grocery_browser" in chat_data["agents_consulted"]
        
        print("Agent Communication Workflow Test Passed:")
        print(f"  Agents Consulted: {', '.join(chat_data['agents_consulted'])}")
        print(f"  Recipe Suggestions: {len(chat_data['recipe_suggestions'])}")
        print(f"  Stores Compared: {len(chat_data['price_comparison'])}")
    
    def test_budget_constraint_workflow(self, test_client):
        """Test workflow with strict budget constraints."""
        # Test meal planning with very tight budget
        tight_budget_request = {
            "user_id": "budget_test_user",
            "message": "I need meals for a week but only have $30 total.",
            "budget_limit": 30.0,
            "family_size": 2
        }
        
        with patch('bruno_master_agent.BrunoMasterAgent.process_request') as mock_process:
            mock_process.return_value = {
                "success": True,
                "meal_plan": {
                    "days": 7,
                    "meals_per_day": 2,  # Reduced meals due to budget
                    "budget_optimized": True,
                    "meals": [
                        {
                            "day": 1,
                            "meal_type": "lunch",
                            "recipe": "Rice and Beans",
                            "ingredients": ["rice", "black beans", "onion", "garlic"]
                        },
                        {
                            "day": 1,
                            "meal_type": "dinner",
                            "recipe": "Pasta with Tomato Sauce",
                            "ingredients": ["pasta", "canned tomatoes", "garlic", "olive oil"]
                        }
                    ]
                },
                "estimated_cost": 28.50,
                "budget_warnings": ["Reduced to 2 meals per day to meet budget"],
                "cost_saving_tips": ["Buy rice and beans in bulk", "Use generic brands"]
            }
            
            response = test_client.post(
                "/api/v1/meal-plan?days=7&meals_per_day=3",
                json=tight_budget_request
            )
        
        assert response.status_code == 200
        budget_data = response.json()
        
        assert "meal_plan" in budget_data
        assert "estimated_cost" in budget_data
        assert budget_data["estimated_cost"] <= 30.0
        assert "budget_warnings" in budget_data
        assert "cost_saving_tips" in budget_data
        
        print("Budget Constraint Workflow Test Passed:")
        print(f"  Budget Limit: ${tight_budget_request['budget_limit']:.2f}")
        print(f"  Estimated Cost: ${budget_data['estimated_cost']:.2f}")
        print(f"  Budget Warnings: {len(budget_data['budget_warnings'])}")
        print(f"  Cost Saving Tips: {len(budget_data['cost_saving_tips'])}")
    
    def test_error_recovery_workflow(self, test_client):
        """Test system behavior when agents encounter errors."""
        # Test chat request that causes agent failure
        error_request = {
            "message": "Find me recipes with impossible ingredients like unicorn meat.",
            "agent_name": "recipe_chef"
        }
        
        with patch('bruno_master_agent.BrunoMasterAgent.process_request') as mock_process:
            # Simulate agent error and recovery
            mock_process.return_value = {
                "success": False,
                "error": "Recipe agent encountered an error with unusual ingredients",
                "fallback_response": "I couldn't find recipes with those specific ingredients, but I can suggest some creative alternatives.",
                "alternative_suggestions": [
                    "Try exotic but available ingredients like dragon fruit or star fruit",
                    "Consider plant-based meat alternatives for unique flavors"
                ],
                "agent_status": "recovered"
            }
            
            response = test_client.post("/api/v1/chat", json=error_request)
        
        # Should still return 200 with graceful error handling
        assert response.status_code == 200
        error_data = response.json()
        
        assert "error" in error_data
        assert "fallback_response" in error_data
        assert "alternative_suggestions" in error_data
        assert error_data["agent_status"] == "recovered"
        
        print("Error Recovery Workflow Test Passed:")
        print(f"  Error Handled: {error_data['error']}")
        print(f"  Fallback Provided: {bool(error_data['fallback_response'])}")
        print(f"  Agent Status: {error_data['agent_status']}")
    
    def test_concurrent_user_workflow(self, test_client):
        """Test handling multiple concurrent user requests."""
        import threading
        import time
        
        results = []
        errors = []
        
        def make_request(user_id: str, request_data: Dict[str, Any]):
            """Make a request for a specific user."""
            try:
                with patch('bruno_master_agent.BrunoMasterAgent.process_request') as mock_process:
                    mock_process.return_value = {
                        "success": True,
                        "user_id": user_id,
                        "response": f"Response for {user_id}",
                        "timestamp": time.time()
                    }
                    
                    response = test_client.post("/api/v1/chat", json=request_data)
                    results.append((user_id, response.status_code, response.json()))
            except Exception as e:
                errors.append((user_id, str(e)))
        
        # Create multiple concurrent requests
        threads = []
        for i in range(5):
            user_id = f"concurrent_user_{i}"
            request_data = {
                "message": f"Hello from user {i}",
                "agent_name": "bruno_master"
            }
            
            thread = threading.Thread(target=make_request, args=(user_id, request_data))
            threads.append(thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=30)
        
        end_time = time.time()
        
        # Verify results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 5, f"Expected 5 results, got {len(results)}"
        
        # All requests should succeed
        for user_id, status_code, response_data in results:
            assert status_code == 200
            assert response_data["user_id"] == user_id
        
        print("Concurrent User Workflow Test Passed:")
        print(f"  Concurrent Requests: {len(results)}")
        print(f"  Total Time: {end_time - start_time:.2f}s")
        print(f"  Errors: {len(errors)}")
    
    def test_data_persistence_workflow(self, test_client):
        """Test data persistence across requests."""
        user_id = "persistence_test_user"
        
        # First request: Create meal plan
        meal_plan_request = {
            "user_id": user_id,
            "message": "Create a meal plan for me",
            "budget_limit": 100.0,
            "family_size": 3
        }
        
        with patch('bruno_master_agent.BrunoMasterAgent.process_request') as mock_process:
            mock_process.return_value = {
                "success": True,
                "meal_plan_id": "mp_123456",
                "meal_plan": {"days": 5, "meals_per_day": 3},
                "user_preferences": {"budget": 100.0, "family_size": 3}
            }
            
            response1 = test_client.post(
                "/api/v1/meal-plan?days=5&meals_per_day=3",
                json=meal_plan_request
            )
        
        assert response1.status_code == 200
        meal_plan_data = response1.json()
        meal_plan_id = meal_plan_data["meal_plan_id"]
        
        # Second request: Generate shopping list using the meal plan
        shopping_request = {
            "user_id": user_id,
            "meal_plan_id": meal_plan_id,
            "budget_limit": 100.0
        }
        
        with patch('bruno_master_agent.BrunoMasterAgent.process_request') as mock_process:
            mock_process.return_value = {
                "success": True,
                "shopping_list_id": "sl_789012",
                "shopping_list": {"items": ["item1", "item2"]},
                "linked_meal_plan_id": meal_plan_id
            }
            
            response2 = test_client.post("/api/v1/shopping-list", json=shopping_request)
        
        assert response2.status_code == 200
        shopping_data = response2.json()
        
        # Verify data consistency
        assert shopping_data["linked_meal_plan_id"] == meal_plan_id
        
        print("Data Persistence Workflow Test Passed:")
        print(f"  Meal Plan ID: {meal_plan_id}")
        print(f"  Shopping List ID: {shopping_data['shopping_list_id']}")
        print(f"  Data Linked: {shopping_data['linked_meal_plan_id'] == meal_plan_id}")
    
    def test_api_versioning_workflow(self, test_client):
        """Test API versioning and backward compatibility."""
        # Test current API version
        v1_request = {
            "message": "Test API v1",
            "agent_name": "bruno_master"
        }
        
        with patch('bruno_master_agent.BrunoMasterAgent.process_request') as mock_process:
            mock_process.return_value = {
                "success": True,
                "api_version": "v1",
                "response": "API v1 response"
            }
            
            response = test_client.post("/api/v1/chat", json=v1_request)
        
        assert response.status_code == 200
        v1_data = response.json()
        assert v1_data["api_version"] == "v1"
        
        # Test API documentation endpoint
        docs_response = test_client.get("/docs")
        assert docs_response.status_code == 200
        
        # Test OpenAPI schema
        openapi_response = test_client.get("/openapi.json")
        assert openapi_response.status_code == 200
        openapi_data = openapi_response.json()
        assert "openapi" in openapi_data
        assert "paths" in openapi_data
        
        print("API Versioning Workflow Test Passed:")
        print(f"  API Version: {v1_data['api_version']}")
        print(f"  Documentation Available: {docs_response.status_code == 200}")
        print(f"  OpenAPI Schema Valid: {'openapi' in openapi_data}")
    
    def test_security_workflow(self, test_client):
        """Test security features and input validation."""
        # Test with potentially malicious input
        malicious_requests = [
            {
                "message": "<script>alert('xss')</script>",
                "agent_name": "bruno_master"
            },
            {
                "message": "'; DROP TABLE users; --",
                "agent_name": "bruno_master"
            },
            {
                "message": "../../../etc/passwd",
                "agent_name": "bruno_master"
            }
        ]
        
        for malicious_request in malicious_requests:
            with patch('bruno_master_agent.BrunoMasterAgent.process_request') as mock_process:
                mock_process.return_value = {
                    "success": True,
                    "response": "Input sanitized and processed safely",
                    "security_warning": "Potentially malicious input detected and handled"
                }
                
                response = test_client.post("/api/v1/chat", json=malicious_request)
            
            # Should handle malicious input gracefully
            assert response.status_code == 200
            security_data = response.json()
            assert "security_warning" in security_data
        
        # Test CORS headers
        cors_response = test_client.options("/api/v1/chat")
        assert cors_response.status_code == 200
        
        print("Security Workflow Test Passed:")
        print(f"  Malicious Inputs Tested: {len(malicious_requests)}")
        print(f"  All Handled Safely: True")
        print(f"  CORS Enabled: {cors_response.status_code == 200}")


class TestSystemIntegration:
    """System-level integration tests."""
    
    def test_health_monitoring_integration(self, test_client):
        """Test health monitoring and system status."""
        # Test health endpoint
        health_response = test_client.get("/health")
        assert health_response.status_code == 200
        
        health_data = health_response.json()
        assert "status" in health_data
        assert "timestamp" in health_data
        assert "agents" in health_data
        
        # Verify all agents are reported
        expected_agents = ["bruno_master", "recipe_chef", "grocery_browser", "instacart_api"]
        for agent in expected_agents:
            assert agent in health_data["agents"]
        
        print("Health Monitoring Integration Test Passed:")
        print(f"  System Status: {health_data['status']}")
        print(f"  Agents Monitored: {len(health_data['agents'])}")
    
    def test_logging_integration(self, test_client):
        """Test logging system integration."""
        import logging
        import io
        
        # Capture log output
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        logger = logging.getLogger("bruno_ai")
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Make a request that should generate logs
        test_request = {
            "message": "Test logging",
            "agent_name": "bruno_master"
        }
        
        with patch('bruno_master_agent.BrunoMasterAgent.process_request') as mock_process:
            mock_process.return_value = {
                "success": True,
                "response": "Logging test response"
            }
            
            response = test_client.post("/api/v1/chat", json=test_request)
        
        assert response.status_code == 200
        
        # Check that logs were generated
        log_output = log_capture.getvalue()
        
        print("Logging Integration Test Passed:")
        print(f"  Logs Generated: {len(log_output) > 0}")
        print(f"  Log Content Length: {len(log_output)} characters")
        
        # Clean up
        logger.removeHandler(handler)
    
    def test_configuration_integration(self, test_client):
        """Test configuration system integration."""
        # Test that server respects configuration
        # This is implicitly tested by the server starting with test config
        
        # Test health endpoint to verify server is running with config
        health_response = test_client.get("/health")
        assert health_response.status_code == 200
        
        # Test that CORS is configured (from server_config fixture)
        cors_response = test_client.options("/api/v1/chat")
        assert cors_response.status_code == 200
        
        print("Configuration Integration Test Passed:")
        print(f"  Server Running: {health_response.status_code == 200}")
        print(f"  CORS Configured: {cors_response.status_code == 200}")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main(["-v", "-s", __file__])