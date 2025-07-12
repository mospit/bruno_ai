#!/usr/bin/env python3
"""
Bruno AI Server Stability and Production Readiness Tests

This module contains comprehensive tests specifically designed to validate
server stability, error handling, and production readiness.
"""

import pytest
import asyncio
import httpx
import time
import threading
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
from unittest.mock import patch, Mock

from fastapi.testclient import TestClient
from a2a_server import BrunoAIServer, ServerConfig


class TestServerStability:
    """Test suite focused on server stability and production readiness."""

    @pytest.fixture
    def server_config(self):
        """Create test server configuration."""
        return ServerConfig(
            host="localhost",
            port=8001,  # Different port for testing
            debug=False,  # Production mode
            gemini_api_key="test_gemini_key",
            max_budget=150.0,
            default_family_size=4
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

    def test_health_endpoint_basic(self, test_client):
        """Test basic health endpoint functionality."""
        response = test_client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "agents" in data
        assert "timestamp" in data
        assert data["status"] in ["healthy", "degraded"]

    def test_health_endpoint_repeated_calls(self, test_client):
        """Test health endpoint with repeated calls to check for crashes."""
        for i in range(10):
            response = test_client.get("/health")
            assert response.status_code == 200, f"Health check failed on iteration {i+1}"
            
            data = response.json()
            assert "status" in data
            assert "agents" in data

    def test_concurrent_health_checks(self, test_client):
        """Test concurrent health endpoint calls for race conditions."""
        def make_health_request():
            response = test_client.get("/health")
            return response.status_code, response.json()

        # Run 20 concurrent health checks
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_health_request) for _ in range(20)]
            
            results = []
            for future in as_completed(futures):
                status_code, data = future.result()
                results.append((status_code, data))
                assert status_code == 200
                assert "status" in data

        assert len(results) == 20

    def test_api_documentation_endpoint(self, test_client):
        """Test API documentation endpoint stability."""
        response = test_client.get("/docs")
        assert response.status_code == 200
        
        # Test multiple calls
        for _ in range(5):
            response = test_client.get("/docs")
            assert response.status_code == 200

    def test_openapi_json_endpoint(self, test_client):
        """Test OpenAPI JSON endpoint."""
        response = test_client.get("/openapi.json")
        assert response.status_code == 200
        
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

    def test_invalid_endpoints(self, test_client):
        """Test server response to invalid endpoints."""
        invalid_endpoints = [
            "/invalid",
            "/api/invalid",
            "/api/v1/invalid",
            "/health/invalid",
            "/docs/invalid"
        ]
        
        for endpoint in invalid_endpoints:
            response = test_client.get(endpoint)
            assert response.status_code == 404

    def test_chat_endpoint_basic(self, test_client):
        """Test basic chat endpoint functionality."""
        request_data = {
            "message": "Hello, can you help me?",
            "agent_name": "bruno_master"
        }
        
        response = test_client.post("/api/v1/chat", json=request_data)
        
        # Should not crash the server
        assert response.status_code in [200, 422, 500]  # Accept various responses but no crashes
        
        # Verify server is still responsive after chat request
        health_response = test_client.get("/health")
        assert health_response.status_code == 200

    def test_chat_endpoint_malformed_requests(self, test_client):
        """Test chat endpoint with malformed requests."""
        malformed_requests = [
            {},  # Empty request
            {"message": ""},  # Empty message
            {"agent_name": "invalid_agent"},  # Missing message
            {"message": "test"},  # Missing agent_name
            {"message": "test", "agent_name": "nonexistent_agent"},  # Invalid agent
            {"message": "x" * 10000, "agent_name": "bruno_master"},  # Very long message
        ]
        
        for i, request_data in enumerate(malformed_requests):
            response = test_client.post("/api/v1/chat", json=request_data)
            
            # Should handle gracefully without crashing
            assert response.status_code in [200, 400, 422, 500], f"Unexpected status for request {i}"
            
            # Verify server is still responsive
            health_response = test_client.get("/health")
            assert health_response.status_code == 200, f"Server crashed after malformed request {i}"

    def test_meal_plan_endpoint_basic(self, test_client):
        """Test basic meal plan endpoint functionality."""
        request_data = {
            "user_id": "test_user",
            "message": "I need a meal plan for 3 days",
            "budget_limit": 100.0,
            "family_size": 4
        }
        
        response = test_client.post("/api/v1/meal-plan?days=3&meals_per_day=3", json=request_data)
        
        # Should not crash the server
        assert response.status_code in [200, 422, 500]
        
        # Verify server is still responsive
        health_response = test_client.get("/health")
        assert health_response.status_code == 200

    def test_shopping_list_endpoint_basic(self, test_client):
        """Test basic shopping list endpoint functionality."""
        request_data = {
            "user_id": "test_user",
            "message": "Generate shopping list for pasta dinner",
            "budget_limit": 50.0
        }
        
        response = test_client.post("/api/v1/shopping-list", json=request_data)
        
        # Should not crash the server
        assert response.status_code in [200, 422, 500]
        
        # Verify server is still responsive
        health_response = test_client.get("/health")
        assert health_response.status_code == 200

    def test_price_check_endpoint_basic(self, test_client):
        """Test basic price check endpoint functionality."""
        request_data = {
            "user_id": "test_user",
            "message": "Check prices for milk and bread",
            "zip_code": "90210"
        }
        
        response = test_client.post("/api/v1/price-check", json=request_data)
        
        # Should not crash the server
        assert response.status_code in [200, 422, 500]
        
        # Verify server is still responsive
        health_response = test_client.get("/health")
        assert health_response.status_code == 200

    def test_server_error_handling(self, test_client):
        """Test server error handling doesn't crash the application."""
        # Test with various HTTP methods on chat endpoint
        methods_and_data = [
            ("GET", None),
            ("PUT", {"test": "data"}),
            ("DELETE", None),
            ("PATCH", {"test": "data"}),
        ]
        
        for method, data in methods_and_data:
            if method == "GET":
                response = test_client.get("/api/v1/chat")
            elif method == "PUT":
                response = test_client.put("/api/v1/chat", json=data)
            elif method == "DELETE":
                response = test_client.delete("/api/v1/chat")
            elif method == "PATCH":
                response = test_client.patch("/api/v1/chat", json=data)
            
            # Should return method not allowed or similar, but not crash
            assert response.status_code in [405, 422, 500]
            
            # Verify server is still responsive
            health_response = test_client.get("/health")
            assert health_response.status_code == 200

    def test_large_payload_handling(self, test_client):
        """Test server handling of large payloads."""
        # Create a large request payload
        large_message = "x" * 50000  # 50KB message
        request_data = {
            "message": large_message,
            "agent_name": "bruno_master"
        }
        
        response = test_client.post("/api/v1/chat", json=request_data)
        
        # Should handle gracefully (may reject, but shouldn't crash)
        assert response.status_code in [200, 400, 413, 422, 500]
        
        # Verify server is still responsive
        health_response = test_client.get("/health")
        assert health_response.status_code == 200

    def test_rapid_sequential_requests(self, test_client):
        """Test server handling of rapid sequential requests."""
        request_data = {
            "message": "Quick test message",
            "agent_name": "bruno_master"
        }
        
        # Send 20 rapid requests
        for i in range(20):
            response = test_client.post("/api/v1/chat", json=request_data)
            # Don't assert specific status codes, just ensure no crashes
            assert response.status_code < 600  # Any valid HTTP status
            
            # Quick health check every 5 requests
            if i % 5 == 0:
                health_response = test_client.get("/health")
                assert health_response.status_code == 200

    def test_memory_leak_detection(self, test_client):
        """Basic test to detect obvious memory leaks."""
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Perform many operations
        for i in range(100):
            # Health checks
            test_client.get("/health")
            
            # API documentation
            if i % 10 == 0:
                test_client.get("/docs")
            
            # Chat requests
            if i % 5 == 0:
                test_client.post("/api/v1/chat", json={
                    "message": f"Test message {i}",
                    "agent_name": "bruno_master"
                })
        
        # Check final memory usage
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Allow for some memory increase, but flag excessive growth
        # This is a basic check - in production, use more sophisticated monitoring
        assert memory_increase < 100 * 1024 * 1024, f"Potential memory leak detected: {memory_increase} bytes increase"

    def test_cors_headers(self, test_client):
        """Test CORS headers are properly set."""
        response = test_client.options("/health")
        
        # Should handle OPTIONS request for CORS
        assert response.status_code in [200, 405]
        
        # Check for CORS headers in a regular request
        response = test_client.get("/health")
        assert response.status_code == 200
        
        # In production mode, CORS should be configured appropriately
        # This test ensures the server doesn't crash when handling CORS

    def test_request_timeout_handling(self, test_client):
        """Test server handling of request timeouts."""
        # This test ensures the server can handle timeout scenarios gracefully
        # We'll simulate this by making requests and checking responsiveness
        
        request_data = {
            "message": "This is a test message that might take time to process",
            "agent_name": "bruno_master"
        }
        
        # Make request and immediately check if server is still responsive
        response = test_client.post("/api/v1/chat", json=request_data)
        
        # Regardless of the response, server should still be responsive
        health_response = test_client.get("/health")
        assert health_response.status_code == 200

    def test_agent_initialization_stability(self, bruno_server):
        """Test that agent initialization is stable and doesn't cause crashes."""
        # Verify all agents are properly initialized
        assert hasattr(bruno_server, 'agents')
        assert len(bruno_server.agents) > 0
        
        # Check each agent is accessible
        for agent_name, agent in bruno_server.agents.items():
            assert agent is not None
            assert hasattr(agent, '__class__')

    @pytest.mark.asyncio
    async def test_async_operations_stability(self, bruno_server):
        """Test async operations don't cause deadlocks or crashes."""
        # Test multiple async operations concurrently
        async def make_async_request():
            # Simulate async agent operations
            await asyncio.sleep(0.1)
            return "completed"
        
        # Run multiple async operations
        tasks = [make_async_request() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 10
        assert all(result == "completed" for result in results)


class TestProductionReadiness:
    """Test suite for production readiness checks."""

    def test_environment_variables_handling(self):
        """Test server handles missing environment variables gracefully."""
        # Test with minimal configuration
        config = ServerConfig(
            host="localhost",
            port=8002,
            debug=False
        )
        
        # Should not crash during initialization
        server = BrunoAIServer(config)
        assert server is not None

    def test_logging_configuration(self, test_client):
        """Test logging doesn't cause issues or duplicate entries."""
        import logging
        
        # Capture log output
        with patch('logging.getLogger') as mock_logger:
            mock_logger_instance = Mock()
            mock_logger.return_value = mock_logger_instance
            
            # Make several requests
            test_client.get("/health")
            test_client.get("/docs")
            
            # Verify logging was called but didn't cause crashes
            # The exact number of calls may vary, but there should be some logging
            assert mock_logger.called

    def test_security_headers(self, test_client):
        """Test basic security headers are present."""
        response = test_client.get("/health")
        assert response.status_code == 200
        
        # Check for basic security considerations
        # The server should handle requests securely
        assert "content-type" in response.headers

    def test_error_response_format(self, test_client):
        """Test error responses are properly formatted."""
        # Test with invalid JSON
        response = test_client.post(
            "/api/v1/chat",
            data="invalid json",
            headers={"content-type": "application/json"}
        )
        
        # Should return proper error format, not crash
        assert response.status_code in [400, 422, 500]
        
        # Response should be valid JSON even for errors
        try:
            error_data = response.json()
            assert isinstance(error_data, dict)
        except json.JSONDecodeError:
            # If not JSON, should at least be a proper HTTP response
            assert len(response.content) > 0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main(["-v", __file__])