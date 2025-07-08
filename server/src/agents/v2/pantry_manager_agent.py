"""
Pantry Manager Agent V2.0
Inventory tracking and pantry management with Bruno's organization wisdom
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from loguru import logger
import google.generativeai as genai
from .base_agent import BaseAgent, AgentCard

class PantryManagerAgentV2(BaseAgent):
    """Enhanced Pantry Manager Agent with inventory capabilities"""
    
    def __init__(self):
        # Define agent capabilities
        agent_card = AgentCard(
            name="Pantry Manager Agent",
            version="2.0.0", 
            description="Bruno's organization expert - keeping track of what ya got and what ya need",
            capabilities={
                "skills": [
                    {
                        "id": "inventory_tracking",
                        "name": "Inventory Tracking",
                        "description": "Track pantry items, expiration dates, and quantities",
                        "examples": [
                            "Add new items to pantry inventory",
                            "Check what's expiring soon",
                            "Update quantities after shopping"
                        ],
                        "tags": ["inventory", "tracking", "organization"]
                    },
                    {
                        "id": "meal_optimization",
                        "name": "Pantry-Based Meal Optimization", 
                        "description": "Suggest meals based on current pantry inventory",
                        "examples": [
                            "What can I make with what I have?",
                            "Use up items before they expire",
                            "Minimize waste with smart meal suggestions"
                        ],
                        "tags": ["optimization", "waste-reduction", "meal-planning"]
                    }
                ]
            },
            performance_targets={
                "response_time": "< 2 seconds",
                "accuracy": "> 95%",
                "waste_reduction": "> 20%"
            }
        )
        
        super().__init__(agent_card)
        
        # Override model for faster, cost-efficient operations
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite-preview-06-17')
        
        # Pantry data structures
        self.pantry_inventory = {}
        self.expiration_tracker = {}
        
        logger.info("Pantry Manager Agent V2.0 initialized successfully")
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute pantry management tasks"""
        action = task.get('action')
        context = task.get('context', {})
        
        if action == "track_inventory":
            return await self.track_inventory(
                items=context.get('items', []),
                user_id=context.get('user_id')
            )
        
        elif action == "suggest_meals_from_pantry":
            return await self.suggest_meals_from_pantry(
                user_id=context.get('user_id'),
                dietary_restrictions=context.get('dietary_restrictions', [])
            )
        
        elif action == "check_expiring_items":
            return await self.check_expiring_items(
                user_id=context.get('user_id'),
                days_ahead=context.get('days_ahead', 7)
            )
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def track_inventory(self, items: List[Dict], user_id: str) -> Dict[str, Any]:
        """Track pantry inventory items"""
        
        # Basic inventory tracking logic
        tracked_items = []
        for item in items:
            tracked_item = {
                "name": item.get('name', ''),
                "quantity": item.get('quantity', 1),
                "unit": item.get('unit', 'unit'),
                "expiration_date": item.get('expiration_date'),
                "location": item.get('location', 'pantry'),
                "added_date": datetime.now().isoformat()
            }
            tracked_items.append(tracked_item)
        
        return {
            "success": True,
            "tracked_items": tracked_items,
            "total_items": len(tracked_items),
            "bruno_message": "Bada-bing! Got ya pantry all organized. Bruno's keepin' track of everything!"
        }
    
    async def suggest_meals_from_pantry(self, user_id: str, dietary_restrictions: List) -> Dict[str, Any]:
        """Suggest meals based on current pantry inventory"""
        
        # Mock pantry contents for demo
        pantry_items = [
            "rice", "canned tomatoes", "onions", "garlic", 
            "olive oil", "pasta", "eggs", "cheese"
        ]
        
        prompt = f"""
        Alright, lemme see what we can whip up with what's in ya pantry!
        
        Available ingredients: {', '.join(pantry_items)}
        Dietary restrictions: {', '.join(dietary_restrictions) if dietary_restrictions else 'None'}
        
        Give me 3 meal ideas that use what ya got, with Bruno's cooking wisdom!
        """
        
        response = await self.call_gemini(prompt, {
            "pantry_items": pantry_items,
            "dietary_restrictions": dietary_restrictions
        })
        
        # Parse response (simplified for now)
        meal_suggestions = [
            {
                "name": "Pantry Pasta",
                "ingredients_used": ["pasta", "canned tomatoes", "garlic", "olive oil"],
                "missing_ingredients": [],
                "bruno_tip": "Add some cheese on top - makes everything better!"
            },
            {
                "name": "Fried Rice",
                "ingredients_used": ["rice", "eggs", "onions"],
                "missing_ingredients": ["soy sauce"],
                "bruno_tip": "Use day-old rice if ya got it - works better for frying!"
            }
        ]
        
        return {
            "success": True,
            "meal_suggestions": meal_suggestions,
            "pantry_usage": "85%",
            "bruno_message": "Look at that! Ya got everything ya need for some great meals right in ya pantry!"
        }
    
    async def check_expiring_items(self, user_id: str, days_ahead: int = 7) -> Dict[str, Any]:
        """Check for items expiring soon"""
        
        # Mock expiring items
        expiring_items = [
            {
                "name": "milk",
                "expires_in_days": 2,
                "quantity": "1 gallon",
                "suggested_use": "Make pancakes or use in coffee"
            },
            {
                "name": "bananas",
                "expires_in_days": 3,
                "quantity": "6 pieces", 
                "suggested_use": "Perfect for banana bread or smoothies"
            }
        ]
        
        return {
            "success": True,
            "expiring_items": expiring_items,
            "total_expiring": len(expiring_items),
            "bruno_message": "Hey! Ya got some stuff that needs attention. Let's use it up before it goes bad!"
        }
