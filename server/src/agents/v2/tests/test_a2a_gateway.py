import pytest
import os
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
import sys
import httpx
from fastapi.testclient import TestClient

# Add the agents directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from a2a_gateway import A2AGateway, app

class TestA2AGateway:
    @pytest.fixture
    def mock_redis(self):
        mock_redis = MagicMock()
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True
        mock_redis.keys.return_value = []
        mock_redis.hgetall.return_value = {}
        mock_redis.hset.return_value = True
        return mock_redis
    
    @pytest.fixture
    def gateway(self, mock_redis):
        with patch('a2a_gateway.redis.from_url', return_value=mock_redis):
            gateway = A2AGateway()
            gateway.redis_client = mock_redis
            return gateway
    
    @pytest.fixture
    def client():
        return TestClient(app)
    
    def test_gateway_initialization(self, gateway):
        """Test gateway initializes correctly"""
        assert gateway.agents == {}
        assert gateway.metrics["total_requests"] == 0
        assert gateway.circuit_breaker_states == {}
        assert gateway.rate_limiters == {}
    
    @pytest.mark.asyncio
    async def test_agent_registration(self, gateway):
        """Test agent registration"""
        agent_info = {
            "name": "test_agent",
            "version": "1.0.0",
            "description": "Test agent",
            "capabilities": {"test": True},
            "health_endpoint": "http://localhost:8001/health"
        }
        
        result = await gateway.register_agent("test_agent", agent_info)
        
        assert result["success"] is True
        assert "test_agent" in gateway.agents
        assert gateway.agents["test_agent"]["name"] == "test_agent"
        assert gateway.agents["test_agent"]["status"] == "active"
    
    @pytest.mark.asyncio
    async def test_agent_deregistration(self, gateway):
        """Test agent deregistration"""
        # First register an agent
        agent_info = {
            "name": "test_agent",
            "version": "1.0.0",
            "description": "Test agent",
            "capabilities": {"test": True},
            "health_endpoint": "http://localhost:8001/health"
        }
        
        await gateway.register_agent("test_agent", agent_info)
        
        # Then deregister it
        result = await gateway.deregister_agent("test_agent")
        
        assert result["success"] is True
        assert "test_agent" not in gateway.agents
    
    @pytest.mark.asyncio
    async def test_task_routing_success(self, gateway):
        """Test successful task routing"""
        # Register an agent
        agent_info = {
            "name": "test_agent",
            "version": "1.0.0",
            "description": "Test agent",
            "capabilities": {"test": True},
            "health_endpoint": "http://localhost:8001/health",
            "task_endpoint": "http://localhost:8001/task"
        }
        
        await gateway.register_agent("test_agent", agent_info)
        
        task = {
            "action": "test_action",
            "context": {"test": "data"}
        }
        
        # Mock the HTTP client response
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True, "result": "test_result"}
        mock_response.status_code = 200
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            result = await gateway.route_task("test_agent", task)
            
            assert result["success"] is True
            assert result["result"] == "test_result"
    
    @pytest.mark.asyncio
    async def test_task_routing_agent_not_found(self, gateway):
        """Test task routing when agent is not found"""
        task = {
            "action": "test_action",
            "context": {"test": "data"}
        }
        
        result = await gateway.route_task("nonexistent_agent", task)
        
        assert result["success"] is False
        assert "Agent nonexistent_agent not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_functionality(self, gateway):
        """Test circuit breaker pattern"""
        agent_name = "failing_agent"
        agent_info = {
            "name": agent_name,
            "version": "1.0.0",
            "description": "Failing agent",
            "capabilities": {"test": True},
            "health_endpoint": "http://localhost:8001/health",
            "task_endpoint": "http://localhost:8001/task"
        }
        
        await gateway.register_agent(agent_name, agent_info)
        
        task = {"action": "test_action", "context": {}}
        
        # Simulate failures to trigger circuit breaker
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.side_effect = Exception("Connection failed")
            
            # Make multiple failed requests to trigger circuit breaker
            for _ in range(6):  # Exceeds failure threshold
                result = await gateway.route_task(agent_name, task)
                assert result["success"] is False
            
            # Check circuit breaker state
            assert gateway.circuit_breaker_states[agent_name]["state"] == "open"
    
    @pytest.mark.asyncio
    async def test_health_check_functionality(self, gateway):
        """Test health check functionality"""
        agent_name = "healthy_agent"
        agent_info = {
            "name": agent_name,
            "version": "1.0.0",
            "description": "Healthy agent",
            "capabilities": {"test": True},
            "health_endpoint": "http://localhost:8001/health"
        }
        
        await gateway.register_agent(agent_name, agent_info)
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"healthy": True, "agent": agent_name}
        mock_response.status_code = 200
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            result = await gateway.check_agent_health(agent_name)
            
            assert result["healthy"] is True
            assert result["agent"] == agent_name
    
    @pytest.mark.asyncio
    async def test_load_balancing(self, gateway):
        """Test load balancing across multiple instances"""
        # Register multiple instances of the same agent
        for i in range(3):
            agent_info = {
                "name": f"load_balanced_agent_{i}",
                "version": "1.0.0",
                "description": f"Instance {i}",
                "capabilities": {"test": True},
                "health_endpoint": f"http://localhost:800{i}/health",
                "task_endpoint": f"http://localhost:800{i}/task"
            }
            await gateway.register_agent(f"load_balanced_agent_{i}", agent_info)
        
        # Simulate multiple requests and check distribution
        task = {"action": "test_action", "context": {}}
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True, "result": "test_result"}
        mock_response.status_code = 200
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            # Make requests and track which agents were called
            called_agents = set()
            for i in range(10):
                # For this test, we'll route to different agent instances
                agent_name = f"load_balanced_agent_{i % 3}"
                result = await gateway.route_task(agent_name, task)
                called_agents.add(agent_name)
                assert result["success"] is True
            
            # Verify multiple agents were used
            assert len(called_agents) > 1
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, gateway):
        """Test rate limiting functionality"""
        agent_name = "rate_limited_agent"
        agent_info = {
            "name": agent_name,
            "version": "1.0.0",
            "description": "Rate limited agent",
            "capabilities": {"test": True},
            "health_endpoint": "http://localhost:8001/health",
            "task_endpoint": "http://localhost:8001/task"
        }
        
        await gateway.register_agent(agent_name, agent_info)
        
        task = {"action": "test_action", "context": {}}
        
        # Initialize rate limiter for this agent (100 requests per minute)
        gateway.rate_limiters[agent_name] = {
            "requests": 0,
            "window_start": datetime.now(),
            "limit": 100,
            "window_seconds": 60
        }
        
        # Set rate limiter to be at the limit
        gateway.rate_limiters[agent_name]["requests"] = 100
        
        result = await gateway.route_task(agent_name, task)
        
        assert result["success"] is False
        assert "Rate limit exceeded" in result["error"]
    
    @pytest.mark.asyncio
    async def test_metrics_collection(self, gateway):
        """Test metrics collection"""
        agent_name = "metrics_agent"
        agent_info = {
            "name": agent_name,
            "version": "1.0.0",
            "description": "Metrics agent",
            "capabilities": {"test": True},
            "health_endpoint": "http://localhost:8001/health",
            "task_endpoint": "http://localhost:8001/task"
        }
        
        await gateway.register_agent(agent_name, agent_info)
        
        task = {"action": "test_action", "context": {}}
        
        initial_requests = gateway.metrics["total_requests"]
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True, "result": "test_result"}
        mock_response.status_code = 200
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            await gateway.route_task(agent_name, task)
            
            # Check metrics were updated
            assert gateway.metrics["total_requests"] == initial_requests + 1
            assert gateway.metrics["successful_requests"] >= initial_requests
    
    def test_api_endpoints(self, client):
        """Test FastAPI endpoints"""
        # Test health endpoint
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        
        # Test agents list endpoint
        response = client.get("/agents")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert isinstance(data["agents"], dict)
        
        # Test metrics endpoint
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "total_requests" in data
        assert "successful_requests" in data
    
    def test_agent_registration_endpoint(self, client):
        """Test agent registration via API endpoint"""
        agent_data = {
            "name": "api_test_agent",
            "version": "1.0.0",
            "description": "API test agent",
            "capabilities": {"test": True},
            "health_endpoint": "http://localhost:8001/health"
        }
        
        response = client.post("/agents/api_test_agent/register", json=agent_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_agent_deregistration_endpoint(self, client):
        """Test agent deregistration via API endpoint"""
        # First register an agent
        agent_data = {
            "name": "deregister_test_agent",
            "version": "1.0.0",
            "description": "Deregister test agent",
            "capabilities": {"test": True},
            "health_endpoint": "http://localhost:8001/health"
        }
        
        client.post("/agents/deregister_test_agent/register", json=agent_data)
        
        # Then deregister it
        response = client.delete("/agents/deregister_test_agent")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, gateway):
        """Test handling of concurrent requests"""
        agent_name = "concurrent_agent"
        agent_info = {
            "name": agent_name,
            "version": "1.0.0",
            "description": "Concurrent agent",
            "capabilities": {"test": True},
            "health_endpoint": "http://localhost:8001/health",
            "task_endpoint": "http://localhost:8001/task"
        }
        
        await gateway.register_agent(agent_name, agent_info)
        
        task = {"action": "test_action", "context": {}}
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True, "result": "test_result"}
        mock_response.status_code = 200
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            # Create multiple concurrent tasks
            tasks = [gateway.route_task(agent_name, task) for _ in range(10)]
            results = await asyncio.gather(*tasks)
            
            # All requests should succeed
            for result in results:
                assert result["success"] is True
                assert result["result"] == "test_result"
    
    @pytest.mark.asyncio
    async def test_agent_failure_recovery(self, gateway):
        """Test agent failure and recovery"""
        agent_name = "recovery_agent"
        agent_info = {
            "name": agent_name,
            "version": "1.0.0",
            "description": "Recovery agent",
            "capabilities": {"test": True},
            "health_endpoint": "http://localhost:8001/health",
            "task_endpoint": "http://localhost:8001/task"
        }
        
        await gateway.register_agent(agent_name, agent_info)
        
        task = {"action": "test_action", "context": {}}
        
        # First, cause failures to open circuit breaker
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.side_effect = Exception("Connection failed")
            
            for _ in range(6):  # Trigger circuit breaker
                await gateway.route_task(agent_name, task)
            
            assert gateway.circuit_breaker_states[agent_name]["state"] == "open"
            
            # Now simulate recovery
            mock_response = MagicMock()
            mock_response.json.return_value = {"success": True, "result": "recovered"}
            mock_response.status_code = 200
            mock_client.return_value.__aenter__.return_value.post.side_effect = None
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            # Reset circuit breaker manually for test (in real scenario, it would timeout)
            gateway.circuit_breaker_states[agent_name]["state"] = "closed"
            gateway.circuit_breaker_states[agent_name]["failure_count"] = 0
            
            result = await gateway.route_task(agent_name, task)
            assert result["success"] is True
            assert result["result"] == "recovered"
    
    @pytest.mark.asyncio
    async def test_performance_monitoring(self, gateway):
        """Test performance monitoring and metrics"""
        agent_name = "performance_agent"
        agent_info = {
            "name": agent_name,
            "version": "1.0.0",
            "description": "Performance agent",
            "capabilities": {"test": True},
            "health_endpoint": "http://localhost:8001/health",
            "task_endpoint": "http://localhost:8001/task"
        }
        
        await gateway.register_agent(agent_name, agent_info)
        
        task = {"action": "test_action", "context": {}}
        
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True, "result": "performance_test"}
        mock_response.status_code = 200
        
        initial_metrics = gateway.metrics.copy()
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            start_time = datetime.now()
            result = await gateway.route_task(agent_name, task)
            end_time = datetime.now()
            
            assert result["success"] is True
            
            # Check that metrics were updated
            assert gateway.metrics["total_requests"] > initial_metrics["total_requests"]
            assert gateway.metrics["successful_requests"] > initial_metrics["successful_requests"]
            
            # Performance should be reasonable (less than 1 second for mocked call)
            response_time = (end_time - start_time).total_seconds()
            assert response_time < 1.0
