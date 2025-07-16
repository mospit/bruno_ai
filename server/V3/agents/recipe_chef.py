"""
Recipe Chef Agent - Bruno AI V3.1
Enhanced with token optimization, adaptive planning, and improved A2A collaboration
Uses Claude 4 Sonnet for complex reasoning and adaptive meal planning
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from .base_agent import BaseAgent

class RecipeChefAgent(BaseAgent):
    """Generates meal prep ideas and recipes with complex reasoning, optimized for tokens and collaboration using Claude 4 Sonnet"""
    
    def __init__(self, redis_url: str = None, postgres_url: str = None):
        super().__init__(agent_id="recipe_chef", model_name=None,
                         redis_url=redis_url, postgres_url=postgres_url)
        self.logger = logging.getLogger(f"bruno.recipe_chef")
        self.claude_requests = 0
        
        self.logger.info(f"RecipeChefAgent initialized with {self.model_string}")
        
    def _get_system_prompt(self) -> str:
        """Get system prompt for the Recipe Chef Agent"""
        return """
        You are Bruno's meal planning and recipe specialist, powered by advanced AI for sophisticated culinary reasoning. Your role is to:
        - Generate adaptive, non-prescriptive meal plans with creative reasoning
        - Optimize ingredients and costs using complex analysis
        - Collaborate with other agents for comprehensive solutions
        - Keep user wants central to suggestions
        - Use advanced reasoning for recipe adaptations and flavor combinations
        
        Focus on helpful, friendly guidance without dictating choices.
        Present suggestions as options ("You might enjoy...", "Consider trying...").
        Leverage your sophisticated reasoning capabilities for creative culinary solutions.
        """
    
    async def _compress_context(self, context: Dict) -> str:
        """Compress context using Haiku for token efficiency before Sonnet calls"""
        if not context:
            return ""
            
        summary_query = f"Summarize keeping user wants like budget/cuisine/dietary: {json.dumps(context)}"
        try:
            compressed = await self.compress_context(summary_query, max_tokens=500)
            return compressed
        except Exception as e:
            self.logger.warning(f"Context compression failed: {e}")
            return json.dumps(context)[:500]  # Fallback truncation
    
    async def create_meal_plan(self, requirements: Dict[str, Any], context_id: str = None) -> Dict[str, Any]:
        """Create comprehensive meal plan with validation and compression"""
        
        # Input validation
        if not isinstance(requirements, dict):
            return {'success': False, 'error': 'Requirements must be a dictionary'}
        
        required_keys = ['budget', 'cuisine_preferences', 'dietary_restrictions', 'family_size', 'duration_days', 'pantry_items']
        for key in required_keys:
            if key not in requirements:
                self.logger.warning(f"Missing key in requirements: {key}")
        
        # Extract requirements
        budget = requirements.get('budget')
        cuisine_preferences = requirements.get('cuisine_preferences', [])
        dietary_restrictions = requirements.get('dietary_restrictions', [])
        family_size = requirements.get('family_size', 4)
        duration_days = requirements.get('duration_days', 7)
        pantry_items = requirements.get('pantry_items', [])
        
        query = f"""
        Create a {duration_days}-day meal plan for {family_size} people with these requirements:
        
        Budget: ${budget or 'Flexible'}
        Cuisine preferences: {', '.join(cuisine_preferences) or 'Any'}
        Dietary restrictions: {', '.join(dietary_restrictions) or 'None'}
        Available pantry items: {', '.join(pantry_items) or 'None specified'}
        
        Include:
        - Breakfast, lunch, and dinner for each day
        - Detailed recipes with portions
        - Shopping list optimization
        - Prep time estimates
        - Nutritional balance considerations
        - Cost-effective ingredient usage
        
        Adapt to user wants without prescription.
        """
        
        try:
            # Get and compress context
            context = await self.get_context(context_id) if context_id else {}
            compressed_context = await self._compress_context(context)
            if compressed_context:
                query += f"\nCompressed user context: {compressed_context}"
            
            previous_meals = context.get('previous_meals', [])
            user_preferences = context.get('preferences', {})
            
            if previous_meals:
                query += f"\nAvoid repeating these recent meals: {', '.join(previous_meals[-10:])}"
            if user_preferences:
                query += f"\nUser preferences: {json.dumps(user_preferences)}"
            
            meal_plan = await self.process_with_optimization(query, context_id)
            
            # Structure the response
            result = {
                'meal_plan': meal_plan,
                'duration_days': duration_days,
                'family_size': family_size,
                'estimated_budget_used': self._estimate_budget_usage(budget, family_size, duration_days),
                'shopping_list_preview': await self._generate_shopping_preview(meal_plan, context_id),
                'prep_recommendations': await self._generate_prep_recommendations(meal_plan, context_id)
            }
            
            # Update context with meal plan
            if context_id:
                context['current_meal_plan'] = result
                context['meal_plan_created'] = True
                await self.set_context(context_id, context)
            
            return {'success': True, 'data': result}
            
        except Exception as e:
            self.logger.error(f"Meal plan creation failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def suggest_recipe_adaptations(self, recipe: str, constraints: Dict[str, Any], context_id: str = None) -> Dict[str, Any]:
        """Suggest adaptations with validation and compression"""
        
        # Input validation
        if not isinstance(recipe, str) or not recipe:
            return {'success': False, 'error': 'Recipe must be a non-empty string'}
        if not isinstance(constraints, dict):
            return {'success': False, 'error': 'Constraints must be a dictionary'}
        
        query = f"""
        Adapt this recipe based on the following constraints:
        
        Original Recipe: {recipe}
        
        Constraints:
        Budget limit: ${constraints.get('budget', 'No limit')}
        Available ingredients: {', '.join(constraints.get('available_ingredients', []))}
        Dietary restrictions: {', '.join(constraints.get('dietary_restrictions', []))}
        Cooking time limit: {constraints.get('time_limit', 'No limit')}
        Equipment limitations: {', '.join(constraints.get('equipment_limits', []))}
        
        Provide:
        - Ingredient substitutions with reasoning
        - Cooking method modifications
        - Portion adjustments
        - Cost-saving alternatives
        - Time-saving techniques
        
        Adapt to user wants.
        """
        
        try:
            # Get and compress context
            context = await self.get_context(context_id) if context_id else {}
            compressed_context = await self._compress_context(context)
            if compressed_context:
                query += f"\nCompressed context: {compressed_context}"
            
            result = await self.process_with_optimization(query, context_id)
            return {'success': True, 'adaptations': result}
        except Exception as e:
            self.logger.error(f"Recipe adaptation failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def collaborate_with_budget_agent(self, meal_ideas: List[str], budget: float, context_id: str = None) -> Dict[str, Any]:
        """Prepare A2A request for budget analysis with JSON-RPC format"""
        
        # Input validation
        if not isinstance(meal_ideas, list) or not all(isinstance(m, str) for m in meal_ideas):
            return {'success': False, 'error': 'Meal ideas must be a list of strings'}
        if not isinstance(budget, (int, float)):
            return {'success': False, 'error': 'Budget must be a number'}
        
        query = f"""
        Prepare detailed cost analysis request for these meal ideas:
        {chr(10).join(f"- {meal}" for meal in meal_ideas)}
        
        Target budget: ${budget}
        
        Include:
        - Estimated ingredient costs
        - Portion calculations
        - Cost-per-serving estimates
        - Budget optimization suggestions
        """
        
        try:
            # Get and compress context
            context = await self.get_context(context_id) if context_id else {}
            compressed_context = await self._compress_context(context)
            if compressed_context:
                query += f"\nCompressed context: {compressed_context}"
            
            analysis_prep = await self.process_with_optimization(query, context_id)
            
            # Prepare A2A message with JSON-RPC format
            a2a_request = {
                'jsonrpc': '2.0',
                'method': 'handle_cost_analysis',
                'id': f"recipe_chef_{datetime.now().timestamp()}",
                'params': {
                    'context_id': context_id,
                    'agent_id': 'recipe_chef',
                    'meal_ideas': meal_ideas,
                    'target_budget': budget,
                    'analysis_request': analysis_prep,
                    'request_type': 'cost_analysis'
                }
            }
            
            return {'success': True, 'a2a_request': a2a_request}
            
        except Exception as e:
            self.logger.error(f"Budget collaboration failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def process_a2a_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Process A2A response from other agents with comprehensive error handling"""
        
        # Input validation
        if not isinstance(response, dict):
            return {'success': False, 'error': 'Response must be a dictionary'}
        
        agent_id = response.get('agent_id')
        context_id = response.get('context_id')
        
        try:
            if agent_id == 'budget_analyst':
                result = await self._process_budget_response(response, context_id)
            elif agent_id == 'instacart_integration':
                result = await self._process_instacart_response(response, context_id)
            else:
                result = {'status': 'unknown_agent', 'response': response}
            
            return {'success': True, 'data': result}
            
        except Exception as e:
            self.logger.error(f"A2A processing failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    async def _process_budget_response(self, response: Dict[str, Any], context_id: str = None) -> Dict[str, Any]:
        """Process budget analysis response and refine meal recommendations"""
        
        budget_analysis = response.get('analysis', '')
        cost_breakdown = response.get('cost_breakdown', {})
        recommendations = response.get('recommendations', '')
        
        query = f"""
        Refine meal recommendations based on budget analysis:
        
        Budget Analysis: {budget_analysis}
        Cost Breakdown: {json.dumps(cost_breakdown)}
        Budget Recommendations: {recommendations}
        
        Provide:
        - Adjusted meal suggestions within budget
        - Alternative ingredient options
        - Portion optimizations
        - Money-saving cooking techniques
        """
        
        refined_recommendations = await self.process_with_optimization(query, context_id)
        
        return {
            'status': 'budget_optimized',
            'refined_meals': refined_recommendations,
            'cost_analysis': cost_breakdown,
            'savings_achieved': response.get('potential_savings', 0)
        }
    
    async def _process_instacart_response(self, response: Dict[str, Any], context_id: str = None) -> Dict[str, Any]:
        """Process Instacart shopping plan and adjust recipes accordingly"""
        
        shopping_plan = response.get('shopping_plan', '')
        available_products = response.get('products', {})
        recommendations = response.get('recommendations', '')
        
        query = f"""
        Adjust recipes based on Instacart availability and pricing:
        
        Shopping Plan: {shopping_plan}
        Available Products: {json.dumps(available_products)}
        Instacart Recommendations: {recommendations}
        
        Provide:
        - Recipe modifications based on available ingredients
        - Alternative cooking methods for substitute ingredients
        - Timing adjustments for ingredient delivery
        - Storage and prep recommendations
        """
        
        adjusted_recipes = await self.process_with_optimization(query, context_id)
        
        return {
            'status': 'instacart_optimized',
            'adjusted_recipes': adjusted_recipes,
            'shopping_integration': shopping_plan,
            'delivery_considerations': response.get('estimated_delivery', '')
        }
    
    async def _generate_shopping_preview(self, meal_plan: str, context_id: str = None) -> List[str]:
        """Generate preview of shopping list for meal plan"""
        
        query = f"""
        Extract shopping list from this meal plan:
        {meal_plan}
        
        Organize by:
        - Produce
        - Proteins
        - Pantry staples
        - Dairy
        - Other
        
        Provide estimated quantities for efficient shopping.
        """
        
        shopping_preview = await self.process_with_optimization(query, context_id)
        
        # Return as structured list (simplified for now)
        return shopping_preview.split('\n') if shopping_preview else []
    
    async def _generate_prep_recommendations(self, meal_plan: str, context_id: str = None) -> str:
        """Generate meal prep recommendations for efficiency"""
        
        query = f"""
        Provide meal prep recommendations for this plan:
        {meal_plan}
        
        Include:
        - Batch cooking opportunities
        - Make-ahead components
        - Storage recommendations
        - Time-saving techniques
        - Weekly prep schedule
        """
        
        return await self.process_with_optimization(query, context_id)
    
    def _estimate_budget_usage(self, budget: Optional[float], family_size: int, duration_days: int) -> float:
        """Improved budget estimation with base costs and per-person scaling"""
        if not budget:
            return 0.0
        
        # Enhanced formula: base cost + per-person scaling
        base_cost = 50  # Base weekly cost for staples
        per_person_per_day = 10  # Average per person per day
        
        # Calculate estimated usage
        estimated_usage = base_cost + (per_person_per_day * family_size * duration_days)
        
        # Cap at budget to prevent overestimation
        return round(min(estimated_usage, budget), 2)
