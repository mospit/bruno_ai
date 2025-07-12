"""
Pantry Manager Agent - Bruno AI V3.1
Uses Claude 3.5 Haiku for fast inventory tracking and management
"""

import json
from typing import Dict, List, Any
from .base_agent import TokenOptimizedAgent

class PantryManagerAgent(TokenOptimizedAgent):
    """Manages pantry inventory with fast Claude Haiku responses"""
    
    def __init__(self):
        super().__init__(
            model="anthropic:claude-3-5-haiku",
            instructions="""
            You are Bruno's pantry management specialist. Your role is to:
            - Track and manage pantry inventory efficiently
            - Predict item expirations and suggest usage
            - Recommend replenishment via Instacart
            - Suggest waste reduction strategies
            - Maintain inventory accuracy with minimal user input
            
            Always be concise and practical in your responses. Focus on actionable insights.
            When suggesting replenishment, consider user budget and preferences.
            """,
            agent_name="pantry_manager"
        )
    
    async def check_inventory(self, items: List[str], context_id: str = None) -> Dict[str, Any]:
        """Check pantry for specific items"""
        query = f"Check pantry inventory for: {', '.join(items)}"
        
        # Get current inventory context
        context = self.get_context(context_id) if context_id else {}
        current_inventory = context.get('pantry_items', {})
        
        # Add inventory context to query
        if current_inventory:
            query += f"\nCurrent inventory: {json.dumps(current_inventory)}"
        
        result = await self.process_with_optimization(query, context_id)
        
        # Parse and return structured response
        inventory_status = {
            'available': [],
            'low_stock': [],
            'missing': [],
            'suggestions': result
        }
        
        return inventory_status
    
    async def add_items(self, items: Dict[str, Any], context_id: str = None) -> str:
        """Add items to pantry inventory"""
        query = f"Add these items to pantry: {json.dumps(items)}"
        
        # Update context
        if context_id:
            context = self.get_context(context_id)
            pantry_items = context.get('pantry_items', {})
            pantry_items.update(items)
            context['pantry_items'] = pantry_items
            self.set_context(context_id, context)
        
        return await self.process_with_optimization(query, context_id)
    
    async def suggest_meals(self, available_items: List[str], context_id: str = None) -> str:
        """Suggest meals based on available pantry items"""
        query = f"Suggest meals using these pantry items: {', '.join(available_items)}"
        
        # Get user preferences from context
        if context_id:
            context = self.get_context(context_id)
            budget = context.get('budget')
            cuisine_prefs = context.get('cuisine_preferences', [])
            
            if budget:
                query += f"\nBudget constraint: ${budget}"
            if cuisine_prefs:
                query += f"\nPreferred cuisines: {', '.join(cuisine_prefs)}"
        
        return await self.process_with_optimization(query, context_id)
    
    async def check_expirations(self, context_id: str = None) -> Dict[str, Any]:
        """Check for items nearing expiration"""
        query = "Check pantry for items nearing expiration and suggest immediate usage"
        
        # Get current inventory
        if context_id:
            context = self.get_context(context_id)
            pantry_items = context.get('pantry_items', {})
            if pantry_items:
                query += f"\nCurrent inventory with dates: {json.dumps(pantry_items)}"
        
        result = await self.process_with_optimization(query, context_id)
        
        return {
            'expiring_soon': [],
            'expired': [],
            'usage_suggestions': result
        }
    
    async def request_replenishment(self, needed_items: List[str], context_id: str = None) -> Dict[str, Any]:
        """Request replenishment via A2A to Instacart agent"""
        query = f"Prepare replenishment request for: {', '.join(needed_items)}"
        
        # Get budget and preferences
        context = {}
        if context_id:
            context = self.get_context(context_id)
            budget = context.get('budget')
            preferences = context.get('preferences', {})
            
            if budget:
                query += f"\nBudget limit: ${budget}"
            if preferences:
                query += f"\nUser preferences: {json.dumps(preferences)}"
        
        suggestions = await self.process_with_optimization(query, context_id)
        
        # Prepare A2A message for Instacart agent
        a2a_request = {
            'context_id': context_id,
            'agent_id': 'pantry_manager',
            'items': needed_items,
            'budget': context.get('budget'),
            'preferences': context.get('preferences', {}),
            'suggestions': suggestions
        }
        
        return a2a_request
