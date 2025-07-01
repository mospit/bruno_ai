"""
Bruno AI V2.0 Main Orchestration
Optimized multi-agent system startup and coordination
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Any
from loguru import logger
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Add the parent directory to the path to import agents
sys.path.append(str(Path(__file__).parent.parent))

from agents.v2.a2a_gateway import create_gateway_app
from agents.v2.bruno_master_agent import BrunoMasterAgentV2
from agents.v2.instacart_integration_agent import InstacartIntegrationAgentV2
from agents.v2.budget_analyst_agent import BudgetAnalystAgentV2

class BrunoAISystemV2:
    """Main system orchestrator for Bruno AI V2.0"""
    
    def __init__(self):
        self.gateway_app = create_gateway_app()
        self.agents = {}
        self.agent_servers = {}
        self.is_running = False
        
        logger.info("Bruno AI System V2.0 initialized")
    
    async def initialize_agents(self):
        """Initialize all Bruno AI agents"""
        logger.info("Initializing Bruno AI agents...")
        
        try:
            # Initialize agents
            self.agents = {
                "bruno_master_agent": BrunoMasterAgentV2(),
                "instacart_integration_agent": InstacartIntegrationAgentV2(),
                "budget_analyst_agent": BudgetAnalystAgentV2(),
                # Additional agents would be added here
                # "recipe_chef_agent": RecipeChefAgentV2(),
                # "nutrition_guide_agent": NutritionGuideAgentV2(),
                # "pantry_manager_agent": PantryManagerAgentV2(),
            }
            
            logger.info(f"Successfully initialized {len(self.agents)} agents")
            
            # Create agent servers
            await self._create_agent_servers()
            
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            raise
    
    async def _create_agent_servers(self):
        """Create FastAPI servers for each agent"""
        base_port = 8080
        
        for i, (agent_name, agent_instance) in enumerate(self.agents.items()):
            port = base_port + i
            server_app = self._create_agent_server(agent_instance, agent_name, port)
            
            self.agent_servers[agent_name] = {
                "app": server_app,
                "port": port,
                "agent": agent_instance
            }
            
            logger.info(f"Created server for {agent_name} on port {port}")
    
    def _create_agent_server(self, agent_instance, agent_name: str, port: int) -> FastAPI:
        """Create FastAPI server for an individual agent"""
        
        app = FastAPI(
            title=f"{agent_instance.agent_card.name} Server",
            version=agent_instance.agent_card.version,
            description=agent_instance.agent_card.description
        )
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        @app.get("/health")
        async def health_check():
            """Agent health check endpoint"""
            return await agent_instance.health_check()
        
        @app.post("/task")
        async def execute_task(task_data: Dict[str, Any]):
            """Execute task on agent"""
            try:
                result = await agent_instance.process_task(task_data)
                return result
            except Exception as e:
                logger.error(f"Task execution failed for {agent_name}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/capabilities")
        async def get_capabilities():
            """Get agent capabilities"""
            return agent_instance.agent_card.capabilities
        
        @app.get("/metrics")
        async def get_metrics():
            """Get agent metrics"""
            return agent_instance.metrics
        
        # Agent registration with gateway on startup
        @app.on_event("startup")
        async def register_with_gateway():
            """Register agent with A2A gateway"""
            await self._register_agent_with_gateway(agent_name, port, agent_instance)
        
        return app
    
    async def _register_agent_with_gateway(self, agent_name: str, port: int, agent_instance):
        """Register agent with the A2A gateway"""
        import httpx
        
        gateway_url = os.getenv('A2A_GATEWAY_URL', 'http://localhost:3000')
        agent_url = f"http://localhost:{port}"
        
        registration_data = {
            "name": agent_name,
            "url": agent_url,
            "capabilities": agent_instance.agent_card.capabilities,
            "version": agent_instance.agent_card.version,
            "health_endpoint": "/health",
            "task_endpoint": "/task"
        }
        
        max_retries = 5
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{gateway_url}/register_agent",
                        json=registration_data,
                        timeout=10.0
                    )
                    
                    if response.status_code == 200:
                        logger.info(f"Successfully registered {agent_name} with gateway")
                        return
                    else:
                        logger.warning(f"Registration failed for {agent_name}: {response.status_code}")
                        
            except Exception as e:
                logger.warning(f"Registration attempt {attempt + 1} failed for {agent_name}: {e}")
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
        
        logger.error(f"Failed to register {agent_name} with gateway after {max_retries} attempts")
    
    async def start_system(self):
        """Start the complete Bruno AI system"""
        logger.info("Starting Bruno AI System V2.0...")
        
        try:
            # Initialize agents first
            await self.initialize_agents()
            
            # Start agent servers in the background
            agent_tasks = []
            for agent_name, server_info in self.agent_servers.items():
                task = asyncio.create_task(
                    self._run_agent_server(agent_name, server_info)
                )
                agent_tasks.append(task)
            
            # Start gateway server
            gateway_task = asyncio.create_task(self._run_gateway())
            
            # Wait for all servers to start
            await asyncio.sleep(2)
            
            self.is_running = True
            logger.info("Bruno AI System V2.0 started successfully!")
            
            # Keep the system running
            await asyncio.gather(gateway_task, *agent_tasks)
            
        except Exception as e:
            logger.error(f"Failed to start Bruno AI System: {e}")
            raise
    
    async def _run_agent_server(self, agent_name: str, server_info: Dict):
        """Run an individual agent server"""
        app = server_info["app"]
        port = server_info["port"]
        
        config = uvicorn.Config(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=False  # Reduce log noise
        )
        
        server = uvicorn.Server(config)
        
        logger.info(f"Starting {agent_name} server on port {port}")
        await server.serve()
    
    async def _run_gateway(self):
        """Run the A2A gateway server"""
        gateway_port = int(os.getenv("GATEWAY_PORT", 3000))
        gateway_host = os.getenv("GATEWAY_HOST", "0.0.0.0")
        
        config = uvicorn.Config(
            self.gateway_app,
            host=gateway_host,
            port=gateway_port,
            log_level="info",
            access_log=True
        )
        
        server = uvicorn.Server(config)
        
        logger.info(f"Starting A2A Gateway on {gateway_host}:{gateway_port}")
        await server.serve()
    
    async def stop_system(self):
        """Gracefully stop the Bruno AI system"""
        logger.info("Stopping Bruno AI System V2.0...")
        self.is_running = False
        # Additional cleanup logic would go here
        logger.info("Bruno AI System V2.0 stopped")

# Main execution functions
async def main():
    """Main entry point for Bruno AI System"""
    # Configure logging
    logger.remove()
    logger.add(sys.stderr, level="INFO", format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}")
    logger.add("bruno_ai_v2.log", rotation="10 MB", retention="7 days", level="DEBUG")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Verify required environment variables
    required_env_vars = ["GEMINI_API_KEY"]
    optional_env_vars = {
        "INSTACART_API_KEY": "demo_key",
        "REDIS_URL": "redis://localhost:6379",
        "A2A_GATEWAY_URL": "http://localhost:3000"
    }
    
    for var in required_env_vars:
        if not os.getenv(var):
            logger.error(f"Required environment variable {var} not set")
            sys.exit(1)
    
    for var, default in optional_env_vars.items():
        if not os.getenv(var):
            os.environ[var] = default
            logger.info(f"Using default value for {var}: {default}")
    
    # Create and start the system
    system = BrunoAISystemV2()
    
    try:
        await system.start_system()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        await system.stop_system()
    except Exception as e:
        logger.error(f"System error: {e}")
        await system.stop_system()
        sys.exit(1)

def run_system():
    """Convenience function to run the system"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("System shutdown requested")
    except Exception as e:
        logger.error(f"Failed to start system: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_system()
