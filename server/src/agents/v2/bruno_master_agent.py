"""
Bruno Master Agent V2.0
Enhanced orchestrator with intelligent coordination capabilities
Central coordinator for the optimized Bruno AI agent ecosystem
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from loguru import logger
from .base_agent import BaseAgent, AgentCard, AgentMessage

class BrunoMasterAgentV2(BaseAgent):
    """Enhanced Bruno Master Agent with advanced coordination capabilities"""
    
    def __init__(self):
        # Define enhanced agent capabilities
        agent_card = AgentCard(
            name="Bruno Master Agent",
            version="2.0.0",
            description="Bruno AI - Intelligent meal planning orchestrator with advanced user interaction",
            capabilities={
                "skills": [
                    {
                        "id": "intelligent_meal_orchestration",
                        "name": "Intelligent Meal Planning Orchestration",
                        "description": "Advanced coordination of specialized agents for optimal meal planning",
                        "examples": [
                            "Bruno, plan meals for $75 this week for family of 4",
                            "Create healthy meals under $60 with delivery by Thursday",
                            "Plan diabetic-friendly meals for $100 budget"
                        ],
                        "tags": ["orchestration", "ai-coordination", "workflow-management"]
                    },
                    {
                        "id": "personalized_budget_coaching",
                        "name": "Personalized Budget Coaching",
                        "description": "AI-driven budget optimization with learning capabilities",
                        "examples": [
                            "Why am I overspending on groceries?",
                            "Show me seasonal savings opportunities",
                            "Optimize my weekly meal budget"
                        ],
                        "tags": ["coaching", "personalization", "ml-optimization"]
                    },
                    {
                        "id": "real_time_adaptation",
                        "name": "Real-time Meal Plan Adaptation",
                        "description": "Dynamic adjustment based on live pricing and availability",
                        "examples": [
                            "Chicken prices went up, suggest alternatives",
                            "Update meal plan based on current deals",
                            "Adapt recipes for out-of-stock ingredients"
                        ],
                        "tags": ["adaptation", "real-time", "optimization"]
                    }
                ]
            },
            performance_targets={
                "response_time": "< 2 seconds",
                "coordination_efficiency": "> 95%",
                "user_satisfaction": "> 90%"
            }
        )
        
        super().__init__(agent_card)
        
        # User preference learning system
        self.user_preferences = {}
        self.optimization_history = []
        
        # Available specialized agents
        self.specialized_agents = {
            "instacart_integration_agent": "Instacart Integration Agent",
            "recipe_chef_agent": "Recipe Chef Agent",
            "nutrition_guide_agent": "Nutrition Guide Agent",
            "budget_analyst_agent": "Budget Analyst Agent",
            "pantry_manager_agent": "Pantry Manager Agent"
        }
        
        logger.info("Bruno Master Agent V2.0 initialized successfully")
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Bruno's orchestration logic"""
        action = task.get('action')
        context = task.get('context', {})
        user_message = task.get('message', '')
        
        # Analyze user request
        request_analysis = await self._analyze_user_request(user_message, context)
        
        # Route to appropriate workflow
        if action == "plan_meals" or "plan meals" in user_message.lower():
            return await self.orchestrate_meal_planning(request_analysis)
        
        elif action == "budget_coaching" or any(word in user_message.lower() for word in ["budget", "save", "spending"]):
            return await self.provide_budget_coaching(request_analysis)
        
        elif action == "adapt_meal_plan" or "update" in user_message.lower():
            return await self.adapt_meal_plan_real_time(request_analysis)
        
        elif action == "create_shopping_list" or "shopping" in user_message.lower():
            return await self.create_instacart_shopping_experience(request_analysis)
        
        else:
            # General Bruno conversation
            return await self.general_bruno_interaction(request_analysis)
    
    async def orchestrate_meal_planning(self, request_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate comprehensive meal planning workflow"""
        logger.info("Starting meal planning orchestration")
        
        # Extract key parameters
        budget = request_analysis.get('budget', 0)
        family_size = request_analysis.get('family_size', 1)
        dietary_restrictions = request_analysis.get('dietary_restrictions', [])
        timeframe = request_analysis.get('timeframe', 'week')
        location = request_analysis.get('location', {})
        
        # Step 1: Parallel execution of budget analysis and nutrition requirements
        parallel_tasks = []
        
        # Budget analysis task
        budget_task = {
            "action": "analyze_budget",
            "context": {
                "target_budget": budget,
                "family_size": family_size,
                "timeframe": timeframe,
                "historical_data": await self._get_user_history(request_analysis.get('user_id'))
            }
        }
        parallel_tasks.append(self._delegate_to_agent("budget_analyst_agent", budget_task))
        
        # Nutrition requirements task
        nutrition_task = {
            "action": "analyze_nutrition_needs",
            "context": {
                "family_size": family_size,
                "dietary_restrictions": dietary_restrictions,
                "age_groups": request_analysis.get('age_groups', []),
                "activity_levels": request_analysis.get('activity_levels', [])
            }
        }
        parallel_tasks.append(self._delegate_to_agent("nutrition_guide_agent", nutrition_task))
        
        # Execute parallel tasks
        parallel_results = await asyncio.gather(*parallel_tasks, return_exceptions=True)
        
        # Process parallel results
        budget_analysis = parallel_results[0] if not isinstance(parallel_results[0], Exception) else {"error": str(parallel_results[0])}
        nutrition_analysis = parallel_results[1] if not isinstance(parallel_results[1], Exception) else {"error": str(parallel_results[1])}
        
        # Step 2: Get current Instacart pricing and deals
        instacart_task = {
            "action": "monitor_deals",
            "context": {
                "products": await self._extract_common_products(dietary_restrictions),
                "location": location,
                "budget_constraints": budget_analysis.get('recommendations', {})
            }
        }
        instacart_result = await self._delegate_to_agent("instacart_integration_agent", instacart_task)
        
        # Step 3: Create optimized recipes based on all gathered data
        recipe_context = {
            "budget_analysis": budget_analysis,
            "nutrition_requirements": nutrition_analysis,
            "current_deals": instacart_result.get('current_deals', []),
            "family_size": family_size,
            "timeframe": timeframe
        }
        
        recipe_task = {
            "action": "create_budget_meal_plan",
            "context": recipe_context
        }
        recipe_result = await self._delegate_to_agent("recipe_chef_agent", recipe_task)
        
        # Step 4: Create optimized shopping list with Instacart integration
        shopping_task = {
            "action": "create_shopping_list",
            "context": {
                "recipes": recipe_result.get('recipes', []),
                "budget": budget,
                "location": location,
                "preferences": {
                    "delivery_speed": "standard",
                    "cost_optimization": True
                }
            }
        }
        shopping_result = await self._delegate_to_agent("instacart_integration_agent", shopping_task)
        
        # Step 5: Generate Bruno's personalized response
        bruno_response = await self._generate_bruno_response(
            request_analysis, budget_analysis, nutrition_analysis, 
            recipe_result, shopping_result, instacart_result
        )
        
        # Step 6: Learn from this interaction
        await self._learn_from_interaction(request_analysis, {
            "budget_analysis": budget_analysis,
            "recipe_result": recipe_result,
            "shopping_result": shopping_result,
            "user_satisfaction": None  # Will be updated based on feedback
        })
        
        return {
            "success": True,
            "bruno_response": bruno_response,
            "meal_plan": recipe_result,
            "shopping_experience": shopping_result,
            "budget_analysis": budget_analysis,
            "nutrition_analysis": nutrition_analysis,
            "coordination_details": {
                "agents_used": ["budget_analyst_agent", "nutrition_guide_agent", "instacart_integration_agent", "recipe_chef_agent"],
                "parallel_execution": True,
                "total_processing_time": self._calculate_total_processing_time(),
                "optimization_score": await self._calculate_optimization_score(budget_analysis, recipe_result, shopping_result)
            }
        }
    
    async def provide_budget_coaching(self, request_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Provide personalized budget coaching"""
        logger.info("Providing budget coaching")
        
        # Get user's historical data
        user_history = await self._get_user_history(request_analysis.get('user_id'))
        
        # Analyze spending patterns
        budget_task = {
            "action": "analyze_spending_patterns",
            "context": {
                "user_history": user_history,
                "current_budget": request_analysis.get('budget'),
                "analysis_timeframe": "3_months"
            }
        }
        budget_analysis = await self._delegate_to_agent("budget_analyst_agent", budget_task)
        
        # Get current market trends
        instacart_task = {
            "action": "monitor_deals",
            "context": {
                "products": user_history.get('frequently_bought', []),
                "analysis_type": "trend_analysis"
            }
        }
        market_trends = await self._delegate_to_agent("instacart_integration_agent", instacart_task)
        
        # Generate personalized coaching
        coaching_response = await self.call_gemini(
            f"Hey there! The user asked: '{request_analysis.get('original_message')}'. As Bruno, provide warm, encouraging budget coaching with your Brooklyn charm. Help them understand their spending patterns and give practical tips to save money while eating well.",
            {
                "budget_analysis": budget_analysis,
                "market_trends": market_trends,
                "user_preferences": self.user_preferences.get(request_analysis.get('user_id'), {})
            }
        )
        
        return {
            "success": True,
            "bruno_coaching": coaching_response,
            "budget_insights": budget_analysis,
            "market_opportunities": market_trends,
            "actionable_tips": await self._generate_actionable_tips(budget_analysis, market_trends)
        }
    
    async def adapt_meal_plan_real_time(self, request_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt existing meal plan based on real-time changes"""
        logger.info("Adapting meal plan in real-time")
        
        current_meal_plan = request_analysis.get('current_meal_plan', {})
        adaptation_reason = request_analysis.get('adaptation_reason', 'general_update')
        
        # Get current pricing and availability
        current_products = self._extract_products_from_meal_plan(current_meal_plan)
        
        instacart_task = {
            "action": "search_products",
            "context": {
                "query": " ".join(current_products),
                "location": request_analysis.get('location'),
                "check_availability": True
            }
        }
        current_pricing = await self._delegate_to_agent("instacart_integration_agent", instacart_task)
        
        # Identify issues and adaptations needed
        adaptations_needed = await self._identify_needed_adaptations(
            current_meal_plan, current_pricing, adaptation_reason
        )
        
        if adaptations_needed['changes_required']:
            # Get recipe adaptations
            recipe_task = {
                "action": "adapt_recipes",
                "context": {
                    "current_recipes": current_meal_plan.get('recipes', []),
                    "adaptations_needed": adaptations_needed,
                    "budget_constraints": request_analysis.get('budget'),
                    "current_pricing": current_pricing
                }
            }
            adapted_recipes = await self._delegate_to_agent("recipe_chef_agent", recipe_task)
            
            # Update shopping list
            shopping_task = {
                "action": "create_shopping_list",
                "context": {
                    "recipes": adapted_recipes.get('recipes', []),
                    "budget": request_analysis.get('budget'),
                    "location": request_analysis.get('location')
                }
            }
            updated_shopping = await self._delegate_to_agent("instacart_integration_agent", shopping_task)
            
            bruno_response = await self.call_gemini(
                "Hey! I just made some smart updates to ya meal plan because of those price changes. Lemme explain what I switched around to keep ya within budget and still eating great!",
                {
                    "adaptations": adaptations_needed,
                    "adapted_recipes": adapted_recipes,
                    "updated_shopping": updated_shopping
                }
            )
            
            return {
                "success": True,
                "adaptations_made": True,
                "bruno_response": bruno_response,
                "updated_meal_plan": adapted_recipes,
                "updated_shopping": updated_shopping,
                "adaptation_details": adaptations_needed
            }
        else:
            bruno_response = await self.call_gemini(
                "Confirm that the current meal plan is still optimal",
                {
                    "current_meal_plan": current_meal_plan,
                    "current_pricing": current_pricing
                }
            )
            
            return {
                "success": True,
                "adaptations_made": False,
                "bruno_response": bruno_response,
                "status": "meal_plan_still_optimal"
            }
    
    async def create_instacart_shopping_experience(self, request_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create complete Instacart shopping experience"""
        logger.info("Creating Instacart shopping experience")
        
        items = request_analysis.get('items', [])
        budget = request_analysis.get('budget', 0)
        location = request_analysis.get('location', {})
        
        # Create optimized shopping list
        shopping_task = {
            "action": "create_shopping_list",
            "context": {
                "items": items,
                "budget": budget,
                "location": location,
                "preferences": {
                    "optimize_delivery": True,
                    "cost_priority": True
                }
            }
        }
        shopping_result = await self._delegate_to_agent("instacart_integration_agent", shopping_task)
        
        # Generate Bruno's shopping guidance
        bruno_response = await self.call_gemini(
            "Hey! I just put together ya shopping list and found some great deals! Lemme walk ya through what I got for ya and how much ya gonna save!",
            {
                "shopping_result": shopping_result,
                "user_budget": budget,
                "savings_found": shopping_result.get('estimated_savings', 0)
            }
        )
        
        return {
            "success": True,
            "bruno_response": bruno_response,
            "shopping_experience": shopping_result,
            "instacart_ready": True
        }
    
    async def general_bruno_interaction(self, request_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general Bruno conversation"""
        user_message = request_analysis.get('original_message', '')
        
        # Generate Bruno's response using Gemini with personality
        bruno_response = await self.call_gemini(
            f"""Hey there! The user said: "{user_message}"
            
            As Bruno from Brooklyn, respond with your characteristic warmth and street smarts. 
            Help them understand what I can do for their family's meal planning and budget needs.
            Show enthusiasm for helping them save money while eating great!
            
            Remember to:
            - Use Brooklyn charm and phrases
            - Highlight my capabilities in a conversational way
            - Ask follow-up questions to understand their needs better
            - Make them feel like family""",
            {
                "user_context": request_analysis,
                "available_capabilities": self.agent_card.capabilities
            }
        )
        
        return {
            "success": True,
            "bruno_response": bruno_response,
            "interaction_type": "general_conversation"
        }
    
    # Helper methods
    
    async def _analyze_user_request(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user request to extract intent and parameters"""
        
        analysis_prompt = f"""
        Analyze this user message and extract structured information:
        Message: "{message}"
        Context: {json.dumps(context, indent=2)}
        
        Extract:
        1. Budget amount (if mentioned)
        2. Family size (if mentioned)
        3. Dietary restrictions
        4. Timeframe (week, month, etc.)
        5. Location information
        6. Primary intent/action requested
        7. Any specific preferences
        
        Return as JSON structure.
        """
        
        analysis_result = await self.call_gemini(analysis_prompt, context)
        
        try:
            # Parse the AI response as JSON
            parsed_analysis = json.loads(analysis_result)
            parsed_analysis['original_message'] = message
            return parsed_analysis
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "original_message": message,
                "budget": context.get('budget', 0),
                "family_size": context.get('family_size', 1),
                "location": context.get('location', {}),
                "intent": "general_meal_planning"
            }
    
    async def _delegate_to_agent(self, agent_name: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate task to specialized agent"""
        try:
            message = AgentMessage(
                id=f"msg_{datetime.now().timestamp()}",
                sender=self.agent_card.name,
                recipient=agent_name,
                message_type="task_delegation",
                payload=task,
                timestamp=datetime.now()
            )
            
            result = await self.send_message_to_agent(agent_name, message)
            return result.get('result', {})
            
        except Exception as e:
            logger.error(f"Failed to delegate to {agent_name}: {e}")
            return {"error": str(e), "agent": agent_name}
    
    async def _generate_bruno_response(self, request_analysis: Dict, budget_analysis: Dict, 
                                     nutrition_analysis: Dict, recipe_result: Dict, 
                                     shopping_result: Dict, instacart_result: Dict) -> str:
        """Generate Bruno's personalized response"""
        
        response_context = {
            "user_request": request_analysis.get('original_message'),
            "budget_target": request_analysis.get('budget'),
            "family_size": request_analysis.get('family_size'),
            "budget_analysis": budget_analysis,
            "nutrition_analysis": nutrition_analysis,
            "recipes_created": len(recipe_result.get('recipes', [])),
            "total_cost": shopping_result.get('total_cost'),
            "savings_found": shopping_result.get('estimated_savings'),
            "deals_available": len(instacart_result.get('current_deals', []))
        }
        
        bruno_prompt = f"""
        As Bruno, a warm and friendly bear who helps families eat well on any budget, 
        create a personalized response to the user based on the meal planning results.
        
        Be encouraging, highlight the savings and value, and explain what you've created for them.
        Include practical tips and show enthusiasm about helping them save money.
        
        Context: {json.dumps(response_context, indent=2)}
        """
        
        return await self.call_gemini(bruno_prompt, response_context)
    
    async def _learn_from_interaction(self, request_analysis: Dict, results: Dict):
        """Learn from user interaction for future optimization"""
        user_id = request_analysis.get('user_id', 'anonymous')
        
        learning_data = {
            "timestamp": datetime.now().isoformat(),
            "user_preferences": {
                "budget_range": request_analysis.get('budget'),
                "family_size": request_analysis.get('family_size'),
                "dietary_restrictions": request_analysis.get('dietary_restrictions', [])
            },
            "results": {
                "budget_accuracy": results.get('budget_analysis', {}).get('accuracy_score'),
                "recipe_satisfaction": None,  # To be updated with feedback
                "shopping_optimization": results.get('shopping_result', {}).get('optimization_score')
            }
        }
        
        # Store in user preferences
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {"interactions": []}
        
        self.user_preferences[user_id]["interactions"].append(learning_data)
        
        # Cache updated preferences
        await self.cache_result(f"user_preferences_{user_id}", self.user_preferences[user_id], ttl=86400)
    
    def _calculate_total_processing_time(self) -> float:
        """Calculate total processing time for the request"""
        # This would be implemented with actual timing
        return 2.5  # Mock value
    
    async def _calculate_optimization_score(self, budget_analysis: Dict, recipe_result: Dict, shopping_result: Dict) -> float:
        """Calculate overall optimization score"""
        budget_score = budget_analysis.get('optimization_score', 0.8)
        recipe_score = recipe_result.get('nutrition_score', 0.85)
        shopping_score = shopping_result.get('cost_efficiency', 0.9)
        
        return (budget_score + recipe_score + shopping_score) / 3
    
    async def _get_user_history(self, user_id: str) -> Dict[str, Any]:
        """Get user's historical data"""
        if not user_id:
            return {"frequently_bought": [], "budget_history": []}
        
        cached_history = await self.get_cached_result(f"user_history_{user_id}")
        if cached_history:
            return cached_history
        
        # Mock implementation - in real scenario, this would query a database
        return {
            "frequently_bought": ["chicken", "rice", "vegetables", "milk"],
            "budget_history": [75, 80, 70, 85],
            "dietary_preferences": [],
            "family_size": 4
        }
    
    async def _extract_common_products(self, dietary_restrictions: List[str]) -> List[str]:
        """Extract common products based on dietary restrictions"""
        base_products = ["chicken", "ground_turkey", "rice", "pasta", "onions", "carrots", "milk", "eggs"]
        
        if "vegetarian" in dietary_restrictions:
            base_products = [p for p in base_products if p not in ["chicken", "ground_turkey"]]
            base_products.extend(["tofu", "beans", "lentils"])
        
        if "gluten_free" in dietary_restrictions:
            base_products = [p for p in base_products if p not in ["pasta"]]
            base_products.append("quinoa")
        
        return base_products
    
    def _extract_products_from_meal_plan(self, meal_plan: Dict[str, Any]) -> List[str]:
        """Extract product names from meal plan"""
        products = []
        for recipe in meal_plan.get('recipes', []):
            for ingredient in recipe.get('ingredients', []):
                products.append(ingredient.get('name', ''))
        return products
    
    async def _identify_needed_adaptations(self, current_meal_plan: Dict, current_pricing: Dict, reason: str) -> Dict[str, Any]:
        """Identify what adaptations are needed for the meal plan"""
        # Mock implementation - in real scenario, this would analyze pricing changes, availability, etc.
        return {
            "changes_required": False,
            "reason": reason,
            "affected_recipes": [],
            "suggested_substitutions": []
        }
    
    async def _generate_actionable_tips(self, budget_analysis: Dict, market_trends: Dict) -> List[str]:
        """Generate actionable budget tips"""
        tips = []
        
        if budget_analysis.get('overspending_categories'):
            tips.append("Consider reducing spending on " + ", ".join(budget_analysis['overspending_categories']))
        
        if market_trends.get('seasonal_deals'):
            tips.append("Take advantage of seasonal deals on " + ", ".join(market_trends['seasonal_deals']))
        
        tips.extend([
            "Buy store brands to save 20-30% on groceries",
            "Plan meals around weekly sales and promotions",
            "Consider bulk buying for non-perishables"
        ])
        
        return tips[:5]  # Return top 5 tips
