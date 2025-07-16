#!/usr/bin/env python3
"""
Bruno AI V3.2 Server - Main Entry Point

Implements the complete V3.2 architecture with:
- 5 specialized agents using Claude models
- FastA2A protocol for agent-to-agent communication
- Advanced token optimization and memory management
- Real-time collaboration and streaming
- Intelligent model routing and compression
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

# FastAPI and server components
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from jose import JWTError, jwt
import uvicorn

# Data and caching
from redis import Redis
from dotenv import load_dotenv

# Import our V3 agents and token management
sys.path.append(str(Path(__file__).parent))
from agents.pantry_manager import PantryManagerAgent
from agents.instacart_agent import InstacartIntegrationAgent
from agents.recipe_chef import RecipeChefAgent
from agents.budget_analyst import BudgetAnalystAgent
from agents.reflection_feedback import ReflectionFeedbackAgent
from agents.llm_router import get_llm_router
from token_manager import initialize_token_manager, get_token_manager

# Load Environment Variables
load_dotenv()

# Configure Logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.getenv('LOG_FILE_PATH', './logs/bruno_v3.log'))
    ]
)
logger = logging.getLogger('bruno.v3.main')

class BrunoV3Server:
    """Main Bruno AI V3.1 Server implementing FastA2A multi-agent architecture"""
    
    def __init__(self):
        self.app = FastAPI(
            title="Bruno AI V3.2 Server",
            description="Multi-agent meal planning and grocery assistant with A2A protocol",
            version="3.2.0"
        )
        
        # Initialize Redis
        self.redis = Redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))
        
        # Initialize token management system
        self.token_manager = initialize_token_manager(
            redis_url=os.getenv('REDIS_URL', 'redis://localhost:6379'),
            postgres_url=os.getenv('POSTGRES_URL', 'postgresql://localhost:5432/bruno_ai'),
            anthropic_api_key=os.getenv('ANTHROPIC_API_KEY')
        )
        logger.info("Token management system initialized")
        
        # Initialize agents
        self.agents = self._initialize_agents()
        
        # Setup middleware and routes
        self._setup_middleware()
        self._setup_routes()
        
        logger.info("Bruno AI V3.2 Server initialized successfully")
    
    def _initialize_agents(self) -> Dict[str, Any]:
        """Initialize all V3.1 agents"""
        logger.info("Initializing Bruno AI V3.1 agents...")
        
        agents = {
            'pantry_manager': PantryManagerAgent(),
            'instacart_integration': InstacartIntegrationAgent(),
            'recipe_chef': RecipeChefAgent(),
            'budget_analyst': BudgetAnalystAgent(),
            'reflection_feedback': ReflectionFeedbackAgent()
        }
        
        logger.info(f"Initialized {len(agents)} agents: {list(agents.keys())}")
        return agents
    
    def _setup_middleware(self):
        """Setup FastAPI middleware"""
        # CORS Configuration
        allowed_origins = os.getenv('CORS_ALLOWED_ORIGINS', '["http://localhost:3000"]')
        if isinstance(allowed_origins, str):
            import json
            allowed_origins = json.loads(allowed_origins)
        
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=["*"],
        )
        
        # JWT Authentication (if enabled)
        if os.getenv('ENABLE_JWT_AUTH', 'false').lower() == 'true':
            self.app.add_middleware(AuthenticationMiddleware, backend=JWTBackend())
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                'status': 'healthy',
                'version': '3.2.0',
                'timestamp': datetime.now().isoformat(),
                'agents': list(self.agents.keys()),
                'redis_connected': await self._check_redis_connection(),
                'token_management': 'enabled'
            }
        
        @self.app.get("/v3/token-stats")
        async def get_token_statistics():
            """Get token usage statistics"""
            try:
                hours = 24  # Default to 24 hours
                stats = await self.token_manager.get_usage_statistics(hours=hours)
                return JSONResponse(stats)
            except Exception as e:
                logger.error(f"Error getting token statistics: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/v3/providers/health")
        async def get_provider_health():
            """Get health status of all LLM providers"""
            try:
                router = get_llm_router()
                health_status = {}
                
                # Check each provider's API key availability
                for provider_name, config in router.llm_configs.items():
                    api_key_available = bool(os.getenv(config.api_key_env))
                    health_status[provider_name] = {
                        'provider': config.provider.value,
                        'model': config.model,
                        'api_key_configured': api_key_available,
                        'cost_per_token': config.cost_per_token,
                        'avg_latency': config.avg_latency,
                        'max_tokens': config.max_tokens,
                        'status': 'healthy' if api_key_available else 'unavailable'
                    }
                
                return JSONResponse({
                    'providers': health_status,
                    'total_providers': len(health_status),
                    'healthy_providers': len([p for p in health_status.values() if p['status'] == 'healthy']),
                    'checked_at': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error getting provider health: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/v3/providers/routing-stats")
        async def get_routing_statistics():
            """Get LLM routing statistics"""
            try:
                router = get_llm_router()
                stats = router.get_routing_stats()
                return JSONResponse(stats)
            except Exception as e:
                logger.error(f"Error getting routing statistics: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/v3/meal-plan")
        async def create_meal_plan(request: Request):
            """Create comprehensive meal plan using agent collaboration"""
            try:
                data = await request.json()
                context_id = data.get('context_id', f"session_{datetime.now().timestamp()}")
                
                # Start with Recipe Chef for meal planning
                meal_plan = await self.agents['recipe_chef'].create_meal_plan(
                    requirements=data.get('requirements', {}),
                    context_id=context_id
                )
                
                # Get budget analysis from Budget Analyst
                if data.get('requirements', {}).get('budget'):
                    budget_request = await self.agents['recipe_chef'].collaborate_with_budget_agent(
                        meal_ideas=data.get('meal_ideas', []),
                        budget=data['requirements']['budget'],
                        context_id=context_id
                    )
                    
                    budget_analysis = await self.agents['budget_analyst'].process_a2a_request(
                        budget_request
                    )
                    
                    # Refine meal plan based on budget analysis
                    meal_plan['budget_analysis'] = budget_analysis
                
                # Get shopping recommendations from Instacart agent
                if meal_plan.get('shopping_list_preview'):
                    shopping_results = await self.agents['instacart_integration'].search_products(
                        items=meal_plan['shopping_list_preview'][:10],  # Limit for efficiency
                        budget=data.get('requirements', {}).get('budget'),
                        context_id=context_id
                    )
                    meal_plan['shopping_integration'] = shopping_results
                
                # Review and optimize with Reflection agent
                reflection_review = await self.agents['reflection_feedback'].review_agent_outputs(
                    agent_outputs={
                        'meal_plan': meal_plan,
                        'budget_analysis': meal_plan.get('budget_analysis', {}),
                        'shopping_integration': meal_plan.get('shopping_integration', {})
                    },
                    user_query=data.get('user_query', ''),
                    context_id=context_id
                )
                
                result = {
                    'meal_plan': meal_plan,
                    'context_id': context_id,
                    'quality_review': reflection_review,
                    'generated_at': datetime.now().isoformat(),
                    'agents_involved': ['recipe_chef', 'budget_analyst', 'instacart_integration', 'reflection_feedback']
                }
                
                return JSONResponse(result)
                
            except Exception as e:
                logger.error(f"Error creating meal plan: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/v3/pantry/check")
        async def check_pantry(request: Request):
            """Check pantry inventory"""
            try:
                data = await request.json()
                result = await self.agents['pantry_manager'].check_inventory(
                    items=data.get('items', []),
                    context_id=data.get('context_id')
                )
                return JSONResponse(result)
            except Exception as e:
                logger.error(f"Error checking pantry: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/v3/shopping/search")
        async def search_products(request: Request):
            """Search for products with budget optimization"""
            try:
                data = await request.json()
                result = await self.agents['instacart_integration'].search_products(
                    items=data.get('items', []),
                    budget=data.get('budget'),
                    context_id=data.get('context_id')
                )
                return JSONResponse(result)
            except Exception as e:
                logger.error(f"Error searching products: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/v3/budget/analyze")
        async def analyze_budget(request: Request):
            """Analyze budget and provide recommendations"""
            try:
                data = await request.json()
                result = await self.agents['budget_analyst'].analyze_meal_costs(
                    meal_ideas=data.get('meal_ideas', []),
                    budget=data.get('budget', 0),
                    context_id=data.get('context_id')
                )
                return JSONResponse(result)
            except Exception as e:
                logger.error(f"Error analyzing budget: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/v3/feedback")
        async def process_feedback(request: Request, background_tasks: BackgroundTasks):
            """Process user feedback for continuous improvement"""
            try:
                data = await request.json()
                result = await self.agents['reflection_feedback'].process_user_feedback(
                    feedback=data.get('feedback', {}),
                    context_id=data.get('context_id')
                )
                
                # Schedule background adaptation if high priority feedback
                if result.get('priority_level') == 'high':
                    background_tasks.add_task(
                        self._adapt_system_behavior,
                        result,
                        data.get('context_id')
                    )
                
                return JSONResponse(result)
            except Exception as e:
                logger.error(f"Error processing feedback: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/v3/agents/{agent_name}/status")
        async def get_agent_status(agent_name: str):
            """Get status of specific agent"""
            if agent_name not in self.agents:
                raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
            
            return {
                'agent_name': agent_name,
                'status': 'active',
                'model': self.agents[agent_name].model,
                'last_activity': datetime.now().isoformat()
            }
        
        @self.app.post("/v3/collaborative-query")
        async def collaborative_query(request: Request):
            """Process query requiring collaboration between multiple agents"""
            try:
                data = await request.json()
                query = data.get('query', '')
                context_id = data.get('context_id', f"collab_{datetime.now().timestamp()}")
                
                # Determine which agents are needed based on query
                involved_agents = self._determine_agent_involvement(query)
                
                results = {}
                
                # Process with each involved agent
                for agent_name in involved_agents:
                    if agent_name in self.agents:
                        try:
                            # Each agent processes the query in their domain
                            if agent_name == 'pantry_manager':
                                if 'pantry' in query.lower() or 'inventory' in query.lower():
                                    results[agent_name] = await self.agents[agent_name].suggest_meals(
                                        available_items=data.get('available_items', []),
                                        context_id=context_id
                                    )
                            elif agent_name == 'recipe_chef':
                                if 'recipe' in query.lower() or 'meal' in query.lower():
                                    results[agent_name] = await self.agents[agent_name].create_meal_plan(
                                        requirements=data.get('requirements', {}),
                                        context_id=context_id
                                    )
                            elif agent_name == 'budget_analyst':
                                if 'budget' in query.lower() or 'cost' in query.lower():
                                    results[agent_name] = await self.agents[agent_name].analyze_meal_costs(
                                        meal_ideas=data.get('meal_ideas', []),
                                        budget=data.get('budget', 0),
                                        context_id=context_id
                                    )
                            elif agent_name == 'instacart_integration':
                                if 'shop' in query.lower() or 'buy' in query.lower():
                                    results[agent_name] = await self.agents[agent_name].search_products(
                                        items=data.get('items', []),
                                        budget=data.get('budget'),
                                        context_id=context_id
                                    )
                        except Exception as e:
                            logger.error(f"Error with agent {agent_name}: {e}")
                            results[agent_name] = {'error': str(e)}
                
                # Review and synthesize results with Reflection agent
                if results:
                    synthesis = await self.agents['reflection_feedback'].review_agent_outputs(
                        agent_outputs=results,
                        user_query=query,
                        context_id=context_id
                    )
                    results['synthesis'] = synthesis
                
                return JSONResponse({
                    'query': query,
                    'context_id': context_id,
                    'involved_agents': involved_agents,
                    'results': results,
                    'processed_at': datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Error in collaborative query: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def _determine_agent_involvement(self, query: str) -> list:
        """Determine which agents should be involved based on query content"""
        query_lower = query.lower()
        involved = []
        
        if any(word in query_lower for word in ['pantry', 'inventory', 'have', 'stock']):
            involved.append('pantry_manager')
        
        if any(word in query_lower for word in ['recipe', 'meal', 'cook', 'prepare', 'dish']):
            involved.append('recipe_chef')
        
        if any(word in query_lower for word in ['budget', 'cost', 'price', 'money', 'cheap', 'expensive']):
            involved.append('budget_analyst')
        
        if any(word in query_lower for word in ['buy', 'shop', 'store', 'instacart', 'order']):
            involved.append('instacart_integration')
        
        # Always include reflection for quality control
        if involved:
            involved.append('reflection_feedback')
        
        return involved or ['recipe_chef', 'reflection_feedback']  # Default agents
    
    async def _check_redis_connection(self) -> bool:
        """Check Redis connection health"""
        try:
            await asyncio.to_thread(self.redis.ping)
            return True
        except Exception:
            return False
    
    async def _adapt_system_behavior(self, feedback_result: Dict[str, Any], context_id: str):
        """Background task to adapt system behavior based on feedback"""
        try:
            adaptation_data = {
                'feedback_priority': feedback_result.get('priority_level'),
                'improvement_actions': feedback_result.get('improvement_actions', []),
                'context_id': context_id
            }
            
            await self.agents['reflection_feedback'].adapt_system_behavior(
                adaptation_data=adaptation_data,
                context_id=context_id
            )
            
            logger.info(f"System behavior adapted based on feedback for context {context_id}")
        except Exception as e:
            logger.error(f"Error adapting system behavior: {e}")


class JWTBackend:
    """JWT Authentication Backend"""
    
    async def authenticate(self, request: Request):
        token = request.headers.get('Authorization')
        if not token:
            return False, None

        try:
            payload = jwt.decode(token.split()[1], os.getenv('SECRET_KEY'))
            return True, payload
        except JWTError:
            return False, None


def create_app():
    """Factory function to create the FastAPI app"""
    server = BrunoV3Server()
    return server.app


# Only initialize server if not being imported for testing
if __name__ != '__main__':
    # For testing or other imports, create a basic app without full initialization
    app = FastAPI(title="Bruno AI V3.1", version="3.1.0")
else:
    app = create_app()


def main():
    """Main entry point for Bruno AI V3.1 Server"""
    logger.info("Starting Bruno AI V3.1 Server...")
    
    # Server configuration
    host = os.getenv('SERVER_HOST', '0.0.0.0')
    port = int(os.getenv('SERVER_PORT', 8000))
    debug = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    
    logger.info(f"Server starting on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    
    # Create the full server instance
    server = BrunoV3Server()
    logger.info(f"Available agents: {list(server.agents.keys())}")
    
    # Run server
    uvicorn.run(
        server.app,
        host=host,
        port=port,
        log_level=os.getenv('LOG_LEVEL', 'info').lower(),
        reload=debug,
        access_log=debug
    )


if __name__ == '__main__':
    main()
