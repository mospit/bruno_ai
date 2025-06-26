"""A2A Server - Agent-to-Agent communication server for Bruno AI.

This server implements Google's A2A protocol for multi-agent coordination
and provides the main entry point for the Bruno AI agent ecosystem.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json
from dataclasses import dataclass, asdict
from decimal import Decimal

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from google.adk.agents import LlmAgent
from google.adk.agents import Agent, LlmAgent
from google.adk.tools import FunctionTool

# Import our custom agents
from bruno_master_agent import BrunoMasterAgent, BudgetTracker
from grocery_browser_agent import GroceryBrowserAgent
from recipe_chef_agent import RecipeChefAgent
from instacart_api_agent import InstacartAPIAgent, InstacartConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ServerConfig:
    """Configuration for the A2A server."""
    host: str = "localhost"
    port: int = 8000
    debug: bool = True
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None  # Legacy support
    instacart_api_key: Optional[str] = None
    max_budget: float = 200.0
    default_family_size: int = 4
    cors_origins: List[str] = None

    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["*"] if self.debug else []


class UserRequest(BaseModel):
    """Model for user requests to the Bruno AI system."""
    user_id: str
    message: str
    context: Optional[Dict[str, Any]] = None
    budget_limit: Optional[float] = None
    family_size: Optional[int] = None
    dietary_restrictions: Optional[List[str]] = None
    zip_code: Optional[str] = None
    preferred_stores: Optional[List[str]] = None


class AgentResponse(BaseModel):
    """Model for agent responses."""
    agent_name: str
    response: str
    data: Optional[Dict[str, Any]] = None
    success: bool = True
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class BrunoAIResponse(BaseModel):
    """Model for complete Bruno AI responses."""
    request_id: str
    user_id: str
    primary_response: str
    agent_responses: List[AgentResponse] = Field(default_factory=list)
    budget_info: Optional[Dict[str, Any]] = None
    recommendations: Optional[List[Dict[str, Any]]] = None
    shopping_list: Optional[List[Dict[str, Any]]] = None
    total_cost: Optional[float] = None
    success: bool = True
    error: Optional[str] = None
    processing_time_ms: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class BrunoAIServer:
    """Main server orchestrating Bruno AI agent ecosystem."""
    
    def __init__(self, config: ServerConfig):
        self.config = config
        self.app = FastAPI(
            title="Bruno AI Agent Ecosystem",
            description="Multi-agent system for meal planning and grocery shopping",
            version="1.0.0"
        )
        
        # Initialize agents
        self.bruno_master = BrunoMasterAgent(
            model="gemini-1.5-flash"
        )
        
        # Note: Budget tracker configuration moved to initialize method
        # to avoid immediate field access validation issues
        self.grocery_browser = GroceryBrowserAgent(model="gemini-2.0-flash-exp")
        self.recipe_chef = RecipeChefAgent()
        # Create Instacart config
        instacart_config = InstacartConfig(
            api_key=self.config.instacart_api_key or "demo_key"
        )
        self.instacart_api = InstacartAPIAgent(config=instacart_config)
        
        # Store agents for coordination
        self.agents = {
            "bruno_master": self.bruno_master,
            "grocery_browser": self.grocery_browser,
            "recipe_chef": self.recipe_chef,
            "instacart_api": self.instacart_api
        }
        
        # Initialize request tracking
        self.active_requests = {}
        self.request_counter = 0
        self.a2a_server = None
        
        # Setup FastAPI routes
        self._setup_routes()

    async def initialize(self) -> None:
        """Initialize the server and all agents."""
        # Initialize budget tracker for bruno_master
        # This is done here to avoid Pydantic field validation issues during __init__
        budget_tracker = BudgetTracker(
            max_budget=self.config.max_budget,
            family_size=self.config.default_family_size
        )
        # Set the budget tracker on the master agent
        self.bruno_master._budget_tracker = budget_tracker
        
        logger.info("Bruno AI server initialization complete")



    def _setup_routes(self) -> None:
        """Setup FastAPI routes."""
        
        @self.app.get("/")
        async def root():
            """Root endpoint with server information."""
            return {
                "service": "Bruno AI - Smart Grocery Assistant",
                "version": "1.0.0",
                "status": "running",
                "agents": list(self.agents.keys()) if self.agents else [],
                "endpoints": {
                    "chat": "/api/v1/chat",
                    "meal_plan": "/api/v1/meal-plan",
                    "shopping_list": "/api/v1/shopping-list",
                    "price_check": "/api/v1/price-check",
                    "health": "/health"
                }
            }
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            agent_status = {}
            for name, agent in self.agents.items():
                try:
                    # Simple health check - could be enhanced
                    agent_status[name] = "healthy"
                except Exception as e:
                    agent_status[name] = f"error: {str(e)}"
            
            return {
                "status": "healthy" if all(status == "healthy" for status in agent_status.values()) else "degraded",
                "agents": agent_status,
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.post("/api/v1/chat", response_model=BrunoAIResponse)
        async def chat_endpoint(
            request: UserRequest,
            background_tasks: BackgroundTasks
        ):
            """Main chat endpoint for user interactions."""
            start_time = datetime.now()
            request_id = f"req_{self.request_counter}_{int(start_time.timestamp())}"
            self.request_counter += 1
            
            try:
                # Track the request
                self.active_requests[request_id] = {
                    "user_id": request.user_id,
                    "message": request.message,
                    "start_time": start_time,
                    "status": "processing"
                }
                
                # Process the request through Bruno Master Agent
                response = await self._process_user_request(request_id, request)
                
                # Calculate processing time
                processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
                response.processing_time_ms = processing_time
                
                # Update request status
                self.active_requests[request_id]["status"] = "completed"
                
                # Schedule cleanup
                background_tasks.add_task(self._cleanup_request, request_id)
                
                return response
                
            except Exception as e:
                logger.error(f"Error processing chat request {request_id}: {e}")
                processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
                
                return BrunoAIResponse(
                    request_id=request_id,
                    user_id=request.user_id,
                    primary_response=f"I apologize, but I encountered an error while processing your request: {str(e)}",
                    success=False,
                    error=str(e),
                    processing_time_ms=processing_time
                )
        
        @self.app.post("/api/v1/meal-plan")
        async def create_meal_plan(
            request: UserRequest,
            days: int = 7,
            meals_per_day: int = 3
        ):
            """Create a meal plan with shopping list."""
            try:
                # Enhance request for meal planning
                enhanced_request = UserRequest(
                    user_id=request.user_id,
                    message=f"Create a {days}-day meal plan with {meals_per_day} meals per day. {request.message}",
                    context={
                        **(request.context or {}),
                        "meal_plan_request": True,
                        "days": days,
                        "meals_per_day": meals_per_day
                    },
                    budget_limit=request.budget_limit,
                    family_size=request.family_size or self.config.default_family_size,
                    dietary_restrictions=request.dietary_restrictions,
                    zip_code=request.zip_code,
                    preferred_stores=request.preferred_stores
                )
                
                request_id = f"meal_plan_{int(datetime.now().timestamp())}"
                response = await self._process_user_request(request_id, enhanced_request)
                
                return response
                
            except Exception as e:
                logger.error(f"Error creating meal plan: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/v1/shopping-list")
        async def generate_shopping_list(
            request: UserRequest,
            recipes: Optional[List[str]] = None
        ):
            """Generate optimized shopping list."""
            try:
                # Enhance request for shopping list generation
                enhanced_request = UserRequest(
                    user_id=request.user_id,
                    message=f"Generate an optimized shopping list. {request.message}",
                    context={
                        **(request.context or {}),
                        "shopping_list_request": True,
                        "recipes": recipes or []
                    },
                    budget_limit=request.budget_limit,
                    family_size=request.family_size or self.config.default_family_size,
                    zip_code=request.zip_code,
                    preferred_stores=request.preferred_stores
                )
                
                request_id = f"shopping_list_{int(datetime.now().timestamp())}"
                response = await self._process_user_request(request_id, enhanced_request)
                
                return response
                
            except Exception as e:
                logger.error(f"Error generating shopping list: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/v1/price-check")
        async def check_prices(
            items: List[str],
            zip_code: Optional[str] = None,
            stores: Optional[List[str]] = None
        ):
            """Check prices for specific items across stores."""
            try:
                # Use grocery browser agent for price checking
                grocery_agent = self.agents.get("grocery_browser")
                if not grocery_agent:
                    raise HTTPException(status_code=503, detail="Grocery browser agent not available")
                
                price_results = []
                for item in items:
                    # This would call the grocery browser agent's price checking tools
                    # For now, return mock data
                    price_results.append({
                        "item": item,
                        "prices": [
                            {"store": "Walmart", "price": 2.99, "availability": True},
                            {"store": "Target", "price": 3.49, "availability": True},
                            {"store": "Kroger", "price": 2.79, "availability": False}
                        ],
                        "best_price": {"store": "Kroger", "price": 2.79, "available": False},
                        "available_best_price": {"store": "Walmart", "price": 2.99, "available": True}
                    })
                
                return {
                    "items": items,
                    "price_results": price_results,
                    "search_area": zip_code,
                    "stores_checked": stores or ["Walmart", "Target", "Kroger"],
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error checking prices: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/agents")
        async def list_agents():
            """List all available agents and their capabilities."""
            agent_info = {}
            for name, agent in self.agents.items():
                agent_info[name] = {
                    "name": agent.name,
                    "description": getattr(agent, 'description', 'No description available'),
                    "tools": [tool.name for tool in getattr(agent, 'tools', [])],
                    "status": "active"
                }
            
            return {
                "agents": agent_info,
                "total_agents": len(agent_info),
                "a2a_enabled": self.a2a_server is not None
            }
        
        @self.app.get("/api/v1/requests/{request_id}")
        async def get_request_status(request_id: str):
            """Get the status of a specific request."""
            if request_id not in self.active_requests:
                raise HTTPException(status_code=404, detail="Request not found")
            
            return self.active_requests[request_id]

    async def _process_user_request(self, request_id: str, request: UserRequest) -> BrunoAIResponse:
        """Process a user request through the agent ecosystem."""
        try:
            # Get the Bruno Master Agent
            master_agent = self.agents.get("bruno_master")
            if not master_agent:
                raise Exception("Bruno Master Agent not available")
            
            # Prepare context for the master agent
            context = {
                "user_id": request.user_id,
                "budget_limit": request.budget_limit or self.config.max_budget,
                "family_size": request.family_size or self.config.default_family_size,
                "dietary_restrictions": request.dietary_restrictions or [],
                "zip_code": request.zip_code,
                "preferred_stores": request.preferred_stores or [],
                "available_agents": list(self.agents.keys()),
                **(request.context or {})
            }
            
            # Process through master agent
            # Note: This is a simplified version. In a full implementation,
            # this would use the A2A protocol for agent communication
            master_response = await self._simulate_master_agent_processing(
                request.message, context
            )
            
            # Collect responses from delegated agents
            agent_responses = []
            
            # Simulate agent delegation based on request type
            if any(keyword in request.message.lower() for keyword in ["recipe", "meal", "cook", "nutrition"]):
                recipe_response = await self._simulate_recipe_agent_processing(request.message, context)
                agent_responses.append(recipe_response)
            
            if any(keyword in request.message.lower() for keyword in ["price", "store", "buy", "shop", "cost"]):
                grocery_response = await self._simulate_grocery_agent_processing(request.message, context)
                agent_responses.append(grocery_response)
            
            if any(keyword in request.message.lower() for keyword in ["order", "delivery", "instacart"]):
                instacart_response = await self._simulate_instacart_agent_processing(request.message, context)
                agent_responses.append(instacart_response)
            
            # Extract structured data from responses
            budget_info = self._extract_budget_info(master_response, context)
            recommendations = self._extract_recommendations(agent_responses)
            shopping_list = self._extract_shopping_list(agent_responses)
            total_cost = self._calculate_total_cost(shopping_list)
            
            return BrunoAIResponse(
                request_id=request_id,
                user_id=request.user_id,
                primary_response=master_response.get("response", "I'm here to help with your grocery and meal planning needs!"),
                agent_responses=agent_responses,
                budget_info=budget_info,
                recommendations=recommendations,
                shopping_list=shopping_list,
                total_cost=total_cost,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Error processing request {request_id}: {e}")
            raise

    async def _simulate_master_agent_processing(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate Bruno Master Agent processing."""
        # This is a simplified simulation. In production, this would use the actual agent
        return {
            "agent_name": "bruno_master",
            "response": f"I understand you want help with: {message}. Let me coordinate with my specialized agents to provide the best assistance.",
            "data": {
                "budget_allocated": context.get("budget_limit", 200.0),
                "family_size": context.get("family_size", 4),
                "agents_to_consult": ["recipe_chef", "grocery_browser", "instacart_api"]
            },
            "success": True
        }

    async def _simulate_recipe_agent_processing(self, message: str, context: Dict[str, Any]) -> AgentResponse:
        """Simulate Recipe Chef Agent processing."""
        return AgentResponse(
            agent_name="recipe_chef",
            response="I've analyzed your request and can suggest budget-friendly recipes that meet your dietary needs.",
            data={
                "suggested_recipes": [
                    {"name": "Budget Chicken Stir Fry", "cost_per_serving": 3.50, "prep_time": 20},
                    {"name": "Lentil Soup", "cost_per_serving": 1.75, "prep_time": 30},
                    {"name": "Pasta with Marinara", "cost_per_serving": 2.25, "prep_time": 15}
                ],
                "nutrition_optimized": True,
                "budget_conscious": True
            },
            success=True
        )

    async def _simulate_grocery_agent_processing(self, message: str, context: Dict[str, Any]) -> AgentResponse:
        """Simulate Grocery Browser Agent processing."""
        return AgentResponse(
            agent_name="grocery_browser",
            response="I've found the best prices across multiple stores in your area.",
            data={
                "price_comparison": [
                    {"item": "Chicken Breast", "walmart": 4.99, "target": 5.49, "kroger": 4.79},
                    {"item": "Rice", "walmart": 2.98, "target": 3.29, "kroger": 2.89},
                    {"item": "Vegetables", "walmart": 1.98, "target": 2.19, "kroger": 1.89}
                ],
                "best_overall_store": "Kroger",
                "total_savings": 3.47
            },
            success=True
        )

    async def _simulate_instacart_agent_processing(self, message: str, context: Dict[str, Any]) -> AgentResponse:
        """Simulate Instacart API Agent processing."""
        return AgentResponse(
            agent_name="instacart_api",
            response="I can help you order these items for delivery through Instacart.",
            data={
                "available_stores": ["Walmart", "Kroger", "Safeway"],
                "delivery_options": {
                    "standard": "2-3 hours, $5.99 fee",
                    "express": "1 hour, $9.99 fee"
                },
                "cart_ready": True,
                "estimated_total": 45.67
            },
            success=True
        )

    def _extract_budget_info(self, master_response: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract budget information from responses."""
        return {
            "total_budget": context.get("budget_limit", 200.0),
            "allocated_budget": master_response.get("data", {}).get("budget_allocated", 0),
            "remaining_budget": context.get("budget_limit", 200.0) - 45.67,  # Mock calculation
            "budget_utilization": 22.8  # Mock percentage
        }

    def _extract_recommendations(self, agent_responses: List[AgentResponse]) -> List[Dict[str, Any]]:
        """Extract recommendations from agent responses."""
        recommendations = []
        for response in agent_responses:
            if response.data and "suggested_recipes" in response.data:
                for recipe in response.data["suggested_recipes"]:
                    recommendations.append({
                        "type": "recipe",
                        "title": recipe["name"],
                        "cost_per_serving": recipe["cost_per_serving"],
                        "prep_time": recipe["prep_time"],
                        "source_agent": response.agent_name
                    })
        return recommendations

    def _extract_shopping_list(self, agent_responses: List[AgentResponse]) -> List[Dict[str, Any]]:
        """Extract shopping list from agent responses."""
        # Mock shopping list extraction
        return [
            {"item": "Chicken Breast", "quantity": "2 lbs", "estimated_cost": 9.98, "store": "Kroger"},
            {"item": "Rice", "quantity": "1 bag", "estimated_cost": 2.89, "store": "Kroger"},
            {"item": "Mixed Vegetables", "quantity": "2 bags", "estimated_cost": 3.78, "store": "Kroger"}
        ]

    def _calculate_total_cost(self, shopping_list: List[Dict[str, Any]]) -> float:
        """Calculate total cost from shopping list."""
        if not shopping_list:
            return 0.0
        return sum(item.get("estimated_cost", 0) for item in shopping_list)

    async def _cleanup_request(self, request_id: str) -> None:
        """Clean up completed request data."""
        await asyncio.sleep(300)  # Keep for 5 minutes
        if request_id in self.active_requests:
            del self.active_requests[request_id]

    async def start(self) -> None:
        """Start the server."""
        await self.initialize_agents()
        
        logger.info(f"Starting Bruno AI server on {self.config.host}:{self.config.port}")
        
        config = uvicorn.Config(
            app=self.app,
            host=self.config.host,
            port=self.config.port,
            log_level="info" if self.config.debug else "warning"
        )
        
        server = uvicorn.Server(config)
        await server.serve()

    async def stop(self) -> None:
        """Stop the server and cleanup resources."""
        logger.info("Stopping Bruno AI server...")
        
        # Cleanup agents
        for agent in self.agents.values():
            if hasattr(agent, 'cleanup'):
                await agent.cleanup()
        
        logger.info("Bruno AI server stopped")


async def main():
    """Main entry point for the Bruno AI server."""
    import os
    
    # Load configuration from environment
    config = ServerConfig(
        host=os.getenv("BRUNO_HOST", "localhost"),
        port=int(os.getenv("BRUNO_PORT", "8000")),
        debug=os.getenv("BRUNO_DEBUG", "true").lower() == "true",
        gemini_api_key=os.getenv("GEMINI_API_KEY"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        instacart_api_key=os.getenv("INSTACART_API_KEY"),
        max_budget=float(os.getenv("BRUNO_MAX_BUDGET", "200.0")),
        default_family_size=int(os.getenv("BRUNO_DEFAULT_FAMILY_SIZE", "4"))
    )
    
    # Create and start server
    server = BrunoAIServer(config)
    
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())