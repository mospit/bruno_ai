"""
Recipe Chef Agent - Bruno AI V3.1
Uses Claude 4 Sonnet for complex reasoning and adaptive meal planning
"""

import json
from typing import Dict, List, Any, Optional
from .base_agent import TokenOptimizedAgent

class RecipeChefAgent(TokenOptimizedAgent):
    """Generates meal prep ideas and recipes with complex reasoning"""
    
    def __init__(self):
        super().__init__(
            model="anthropic:claude-4-sonnet",
            instructions="""
            You are Bruno's master recipe chef and meal planning specialist. Your role is to:
            - Create adaptive meal plans based on user preferences and constraints
            - Generate detailed recipes with clear instructions
            - Collaborate with other agents for budget validation and ingredient sourcing
            - Suggest creative alternatives and substitutions
            - Consider dietary restrictions, allergies, and cultural preferences
            - Optimize meals for nutrition, taste, and budget efficiency
            
            Always maintain Bruno's warm, encouraging personality while providing expert culinary guidance.
            Focus on practical, achievable recipes that respect user wants and limitations.
            """,
            agent_name="recipe_chef"
        )
    
    async def create_meal_plan(self, requirements: Dict[str, Any], context_id: str = None) -> Dict[str, Any]:
        """Create comprehensive meal plan based on requirements"""
        
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
        """
        
        # Get additional context
        if context_id:
            context = self.get_context(context_id)
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
            context = self.get_context(context_id)
            context['current_meal_plan'] = result
            context['meal_plan_created'] = True
            self.set_context(context_id, context)
        
        return result
    
    async def suggest_recipe_adaptations(self, recipe: str, constraints: Dict[str, Any], context_id: str = None) -> str:
        """Suggest adaptations for existing recipes based on constraints"""
        
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
        """
        
        return await self.process_with_optimization(query, context_id)
    
    async def collaborate_with_budget_agent(self, meal_ideas: List[str], budget: float, context_id: str = None) -> Dict[str, Any]:
        """Prepare A2A request for budget analysis of meal ideas"""
        
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
        
        analysis_prep = await self.process_with_optimization(query, context_id)
        
        # Prepare A2A message for Budget Analyst
        a2a_request = {
            'context_id': context_id,
            'agent_id': 'recipe_chef',
            'meal_ideas': meal_ideas,
            'target_budget': budget,
            'analysis_request': analysis_prep,
            'request_type': 'cost_analysis'
        }
        
        return a2a_request
    
    async def process_a2a_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Process A2A response from other agents (Budget, Instacart)"""
        
        agent_id = response.get('agent_id')
        context_id = response.get('context_id')
        
        if agent_id == 'budget_analyst':
            return await self._process_budget_response(response, context_id)
        elif agent_id == 'instacart_integration':
            return await self._process_instacart_response(response, context_id)
        else:
            return {'status': 'unknown_agent', 'response': response}
    
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
        """Estimate budget usage based on meal plan complexity"""
        if not budget:
            return 0.0
        
        # Simple estimation formula (can be enhanced)
        per_person_per_day = budget / (family_size * duration_days)
        return round(per_person_per_day * family_size * duration_days, 2)
