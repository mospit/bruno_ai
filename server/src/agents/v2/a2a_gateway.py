"""
A2A Gateway V2.0
Enhanced gateway for Bruno AI agent coordination with advanced routing and load balancing
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import httpx
import redis
from loguru import logger
from pydantic import BaseModel
import uvicorn

class AgentRegistration(BaseModel):
    name: str
    url: str
    capabilities: Dict[str, Any]
    version: str
    health_endpoint: str = "/health"
    task_endpoint: str = "/task"

class TaskRequest(BaseModel):
    action: str
    context: Dict[str, Any]
    message: Optional[str] = ""
    priority: str = "normal"
    timeout: int = 30

class BrunoA2AGatewayV2:
    """Enhanced A2A Gateway with intelligent routing and load balancing"""
    
    def __init__(self):
        self.app = FastAPI(
            title="Bruno A2A Gateway V2.0",
            version="2.0.0",
            description="Enhanced gateway for Bruno AI agent coordination"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Agent registry
        self.registered_agents = {}
        self.agent_health_status = {}
        self.agent_metrics = {}
        
        # Load balancing
        self.load_balancer = LoadBalancer()
        
        # Circuit breaker for agent resilience
        self.circuit_breakers = {}
        
        # Redis for distributed coordination
        self.redis_client = self._initialize_redis()
        
        # Background tasks
        self.health_check_interval = 30  # seconds
        self.metrics_collection_interval = 60  # seconds
        
        self.setup_routes()
        logger.info("Bruno A2A Gateway V2.0 initialized")
    
    def _initialize_redis(self) -> Optional[redis.Redis]:
        """Initialize Redis for distributed coordination"""
        try:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
            return redis.from_url(redis_url, decode_responses=True)
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            return None
    
    def setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.post("/register_agent")
        async def register_agent(agent_info: AgentRegistration):
            """Register a new agent with the gateway"""
            agent_name = agent_info.name
            agent_url = agent_info.url
            
            # Verify agent is accessible
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{agent_url}{agent_info.health_endpoint}",
                        timeout=10.0
                    )
                    if response.status_code != 200:
                        raise HTTPException(
                            status_code=400, 
                            detail="Agent health check failed"
                        )
            except Exception as e:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Cannot reach agent: {str(e)}"
                )
            
            # Store agent information
            self.registered_agents[agent_name] = {
                **agent_info.dict(),
                "registered_at": datetime.now().isoformat(),
                "last_health_check": datetime.now().isoformat(),
                "status": "healthy",
                "request_count": 0,
                "error_count": 0,
                "avg_response_time": 0.0
            }
            
            # Initialize circuit breaker
            self.circuit_breakers[agent_name] = CircuitBreaker(agent_name)
            
            # Store in Redis for distributed coordination
            if self.redis_client:
                await asyncio.to_thread(
                    self.redis_client.hset,
                    "bruno_agents",
                    agent_name,
                    json.dumps(self.registered_agents[agent_name])
                )
            
            logger.info(f"Agent {agent_name} registered successfully")
            return {"message": f"Agent {agent_name} registered successfully"}
        
        @self.app.get("/agents")
        async def list_agents():
            """List all registered agents"""
            return {
                "agents": list(self.registered_agents.values()),
                "total_count": len(self.registered_agents),
                "healthy_count": len([a for a in self.registered_agents.values() if a["status"] == "healthy"])
            }
        
        @self.app.post("/agents/{agent_name}/task")
        async def create_task(agent_name: str, task_data: TaskRequest):
            """Create a task for a specific agent with intelligent routing"""
            
            # Check if agent exists and is healthy
            agent_info = await self._get_healthy_agent(agent_name)
            if not agent_info:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Healthy instance of {agent_name} not found"
                )
            
            # Check circuit breaker
            circuit_breaker = self.circuit_breakers.get(agent_name)
            if circuit_breaker and not circuit_breaker.can_execute():
                raise HTTPException(
                    status_code=503,
                    detail=f"Agent {agent_name} is temporarily unavailable (circuit breaker open)"
                )
            
            agent_url = agent_info['url']
            start_time = datetime.now()
            
            try:
                # Execute task with timeout
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{agent_url}{agent_info['task_endpoint']}",
                        json=task_data.dict(),
                        timeout=task_data.timeout
                    )
                    
                    # Record success metrics
                    response_time = (datetime.now() - start_time).total_seconds()
                    await self._record_success_metrics(agent_name, response_time)
                    
                    if circuit_breaker:
                        circuit_breaker.record_success()
                    
                    return response.json()
                    
            except Exception as e:
                # Record failure metrics
                await self._record_failure_metrics(agent_name)
                
                if circuit_breaker:
                    circuit_breaker.record_failure()
                
                logger.error(f"Task execution failed for {agent_name}: {str(e)}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Task execution failed: {str(e)}"
                )
        
        @self.app.get("/agents/{agent_name}/health")
        async def check_agent_health(agent_name: str):
            """Check health of a specific agent"""
            if agent_name not in self.registered_agents:
                raise HTTPException(status_code=404, detail="Agent not found")
            
            agent_info = self.registered_agents[agent_name]
            agent_url = agent_info['url']
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{agent_url}{agent_info['health_endpoint']}",
                        timeout=5.0
                    )
                    
                    if response.status_code == 200:
                        self.registered_agents[agent_name]['status'] = 'healthy'
                        self.registered_agents[agent_name]['last_health_check'] = datetime.now().isoformat()
                        return {
                            "status": "healthy", 
                            "agent": agent_name,
                            "response_data": response.json()
                        }
                    else:
                        self.registered_agents[agent_name]['status'] = 'unhealthy'
                        return {"status": "unhealthy", "agent": agent_name}
                        
            except Exception as e:
                self.registered_agents[agent_name]['status'] = 'unreachable'
                return {
                    "status": "unreachable", 
                    "agent": agent_name, 
                    "error": str(e)
                }
        
        @self.app.get("/gateway/metrics")
        async def get_gateway_metrics():
            """Get gateway and agent metrics"""
            return {
                "gateway_status": "healthy",
                "total_agents": len(self.registered_agents),
                "healthy_agents": len([a for a in self.registered_agents.values() if a["status"] == "healthy"]),
                "agent_metrics": self.agent_metrics,
                "circuit_breaker_status": {
                    name: breaker.get_status() 
                    for name, breaker in self.circuit_breakers.items()
                },
                "load_balancer_stats": self.load_balancer.get_stats()
            }
        
        @self.app.get("/gateway/health")
        async def gateway_health():
            """Gateway health check"""
            return {
                "status": "healthy",
                "version": "2.0.0",
                "timestamp": datetime.now().isoformat(),
                "redis_connected": self.redis_client is not None
            }
        
        @self.app.post("/gateway/shutdown")
        async def shutdown_gateway():
            """Graceful shutdown of gateway"""
            logger.info("Gateway shutdown requested")
            return {"message": "Gateway shutting down gracefully"}
    
    async def _get_healthy_agent(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get a healthy instance of the specified agent"""
        if agent_name in self.registered_agents:
            agent = self.registered_agents[agent_name]
            if agent["status"] == "healthy":
                return agent
        
        return None
    
    async def _record_success_metrics(self, agent_name: str, response_time: float):
        """Record successful request metrics"""
        if agent_name not in self.agent_metrics:
            self.agent_metrics[agent_name] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "avg_response_time": 0.0,
                "last_request": None
            }
        
        metrics = self.agent_metrics[agent_name]
        metrics["total_requests"] += 1
        metrics["successful_requests"] += 1
        
        # Update average response time
        if metrics["total_requests"] == 1:
            metrics["avg_response_time"] = response_time
        else:
            metrics["avg_response_time"] = (
                (metrics["avg_response_time"] * (metrics["total_requests"] - 1) + response_time) / 
                metrics["total_requests"]
            )
        
        metrics["last_request"] = datetime.now().isoformat()
        
        # Update agent info
        self.registered_agents[agent_name]["request_count"] = metrics["total_requests"]
        self.registered_agents[agent_name]["avg_response_time"] = metrics["avg_response_time"]
    
    async def _record_failure_metrics(self, agent_name: str):
        """Record failed request metrics"""
        if agent_name not in self.agent_metrics:
            self.agent_metrics[agent_name] = {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "avg_response_time": 0.0,
                "last_request": None
            }
        
        metrics = self.agent_metrics[agent_name]
        metrics["total_requests"] += 1
        metrics["failed_requests"] += 1
        metrics["last_request"] = datetime.now().isoformat()
        
        # Update agent info
        self.registered_agents[agent_name]["request_count"] = metrics["total_requests"]
        self.registered_agents[agent_name]["error_count"] = metrics["failed_requests"]
    
    async def start_background_tasks(self):
        """Start background monitoring tasks"""
        asyncio.create_task(self.health_monitoring_task())
        asyncio.create_task(self.metrics_collection_task())
        logger.info("Background tasks started")
    
    async def health_monitoring_task(self):
        """Background task to monitor agent health"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                
                for agent_name in list(self.registered_agents.keys()):
                    try:
                        await self.check_agent_health_internal(agent_name)
                    except Exception as e:
                        logger.error(f"Health check failed for {agent_name}: {e}")
                        
            except Exception as e:
                logger.error(f"Health monitoring task error: {e}")
    
    async def metrics_collection_task(self):
        """Background task to collect and store metrics"""
        while True:
            try:
                await asyncio.sleep(self.metrics_collection_interval)
                
                # Store metrics in Redis
                if self.redis_client:
                    metrics_data = {
                        "timestamp": datetime.now().isoformat(),
                        "agent_metrics": self.agent_metrics,
                        "gateway_metrics": {
                            "total_agents": len(self.registered_agents),
                            "healthy_agents": len([a for a in self.registered_agents.values() if a["status"] == "healthy"])
                        }
                    }
                    
                    await asyncio.to_thread(
                        self.redis_client.lpush,
                        "bruno_gateway_metrics",
                        json.dumps(metrics_data)
                    )
                    
                    # Keep only last 100 metric entries
                    await asyncio.to_thread(
                        self.redis_client.ltrim,
                        "bruno_gateway_metrics",
                        0, 99
                    )
                    
            except Exception as e:
                logger.error(f"Metrics collection task error: {e}")
    
    async def check_agent_health_internal(self, agent_name: str):
        """Internal health check without HTTP response"""
        if agent_name not in self.registered_agents:
            return
        
        agent_info = self.registered_agents[agent_name]
        agent_url = agent_info['url']
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{agent_url}{agent_info['health_endpoint']}",
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    self.registered_agents[agent_name]['status'] = 'healthy'
                else:
                    self.registered_agents[agent_name]['status'] = 'unhealthy'
                    
                self.registered_agents[agent_name]['last_health_check'] = datetime.now().isoformat()
                
        except Exception:
            self.registered_agents[agent_name]['status'] = 'unreachable'

class LoadBalancer:
    """Load balancer for distributing requests across agent instances"""
    
    def __init__(self):
        self.request_counts = {}
        self.response_times = {}
    
    def select_agent_instance(self, agent_name: str, available_instances: List[Dict]) -> Dict:
        """Select optimal agent instance based on load balancing strategy"""
        if not available_instances:
            return None
        
        if len(available_instances) == 1:
            return available_instances[0]
        
        # Load balancing strategy: least connections with response time consideration
        best_instance = None
        best_score = float('inf')
        
        for instance in available_instances:
            instance_id = f"{agent_name}_{instance['url']}"
            
            # Calculate load score (lower is better)
            request_count = self.request_counts.get(instance_id, 0)
            avg_response_time = self.response_times.get(instance_id, 0.0)
            
            # Weighted score: 70% request count, 30% response time
            score = (request_count * 0.7) + (avg_response_time * 0.3)
            
            if score < best_score:
                best_score = score
                best_instance = instance
        
        return best_instance
    
    def record_request(self, agent_name: str, instance_url: str, response_time: float):
        """Record request for load balancing metrics"""
        instance_id = f"{agent_name}_{instance_url}"
        
        self.request_counts[instance_id] = self.request_counts.get(instance_id, 0) + 1
        
        # Update average response time
        current_avg = self.response_times.get(instance_id, 0.0)
        request_count = self.request_counts[instance_id]
        
        if request_count == 1:
            self.response_times[instance_id] = response_time
        else:
            self.response_times[instance_id] = (
                (current_avg * (request_count - 1) + response_time) / request_count
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get load balancer statistics"""
        return {
            "total_instances": len(self.request_counts),
            "request_distribution": self.request_counts,
            "response_time_distribution": self.response_times
        }

class CircuitBreaker:
    """Circuit breaker for agent resilience"""
    
    def __init__(self, agent_name: str, failure_threshold: int = 5, timeout: int = 60):
        self.agent_name = agent_name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def can_execute(self) -> bool:
        """Check if request can be executed"""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if self.last_failure_time and \
               datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout):
                self.state = "HALF_OPEN"
                return True
            return False
        elif self.state == "HALF_OPEN":
            return True
        
        return False
    
    def record_success(self):
        """Record successful request"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def record_failure(self):
        """Record failed request"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"Circuit breaker opened for {self.agent_name}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status"""
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None
        }

# Gateway startup function
def create_gateway_app():
    """Create and configure the gateway application"""
    gateway = BrunoA2AGatewayV2()
    
    @gateway.app.on_event("startup")
    async def startup_event():
        await gateway.start_background_tasks()
        logger.info("Bruno A2A Gateway V2.0 started successfully")
    
    return gateway.app

# For running the gateway
if __name__ == "__main__":
    app = create_gateway_app()
    
    # Get port from environment or use default
    port = int(os.getenv("GATEWAY_PORT", 3000))
    host = os.getenv("GATEWAY_HOST", "0.0.0.0")
    
    logger.info(f"Starting Bruno A2A Gateway on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )
