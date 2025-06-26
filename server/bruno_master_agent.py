"""Bruno Master Agent - Central coordinator for the Bruno AI ecosystem.

This agent serves as the primary interface and orchestrator for all Bruno AI
functionalities including meal planning, grocery shopping, and budget management.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
from dataclasses import dataclass
from enum import Enum
import json

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from pydantic import BaseModel, Field

from grocery_browser_agent import GroceryBrowserAgent
from recipe_chef_agent import RecipeChefAgent
from instacart_api_agent import InstacartAPIAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BudgetTracker(BaseModel):
    """Budget tracking model for meal planning."""
    weekly_budget: Decimal = Field(default=Decimal('100.00'))
    current_spent: Decimal = Field(default=Decimal('0.00'))
    remaining_budget: Decimal = Field(default=Decimal('100.00'))
    last_updated: datetime = Field(default_factory=datetime.now)

    def update_spent(self, amount: Decimal) -> None:
        """Update the current spent amount and recalculate remaining budget."""
        self.current_spent += amount
        self.remaining_budget = self.weekly_budget - self.current_spent
        self.last_updated = datetime.now()

    def reset_weekly(self) -> None:
        """Reset budget for a new week."""
        self.current_spent = Decimal('0.00')
        self.remaining_budget = self.weekly_budget
        self.last_updated = datetime.now()


class TaskTracker(BaseModel):
    """Task tracking model for agent coordination."""
    task_id: str
    task_type: str
    status: str = "pending"  # pending, in_progress, completed, failed
    assigned_agent: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class BrunoMasterAgent(LlmAgent):
    """Master agent that coordinates meal planning, budgeting, and grocery shopping."""
    
    # Declare instance attributes as Pydantic fields to satisfy Google ADK validation
    active_tasks: Dict[str, Any] = Field(default_factory=dict, description="Active task tracking")
    task_counter: int = Field(default=0, description="Task counter for unique IDs")
    budget_tracker: Optional[Any] = Field(default=None, description="Budget tracking instance")
    
    def __init__(self, model: str = "gpt-4"):
        """Initialize the Bruno Master Agent with coordination capabilities."""
        
        # Initialize the parent LlmAgent first
        super().__init__(
            model=model,
            name="bruno_master_agent",
            description="Central coordinator for Bruno AI ecosystem that manages meal planning, grocery shopping, and budget tracking",
            instruction=self._get_system_prompt(),
            tools=[]
        )
        
        # Initialize complex objects after parent initialization
        self.budget_tracker = BudgetTracker()
        # task_manager will be initialized when needed, not as a single TaskTracker instance
        
        # Add tools after initialization - create them as a list to avoid immediate execution
        self._setup_tools()

    def _setup_tools(self) -> None:
        """Setup tools after all attributes are initialized."""
        self.tools = [
            self._create_meal_plan_tool(),
            self._track_budget_tool(),
            self._get_grocery_prices_tool(),
            self._create_shopping_list_tool(),
            self._get_budget_status_tool()
        ]

    def _create_meal_plan_tool(self) -> FunctionTool:
        """Create a tool for meal planning coordination."""
        async def create_meal_plan(
            dietary_preferences: str,
            number_of_meals: int = 7,
            budget_limit: Optional[float] = None
        ) -> Dict[str, Any]:
            """Create a meal plan based on user preferences and budget.
            
            Args:
                dietary_preferences: User's dietary preferences and restrictions
                number_of_meals: Number of meals to plan (default 7 for a week)
                budget_limit: Optional budget limit for the meal plan
                
            Returns:
                Dictionary containing the meal plan and cost breakdown
            """
            try:
                # Create new task
                task_id = self._create_task("meal_planning", {
                    "dietary_preferences": dietary_preferences,
                    "number_of_meals": number_of_meals,
                    "budget_limit": budget_limit or float(self.budget_tracker.remaining_budget)
                })
                
                # For now, return a basic meal plan structure
                # In full implementation, this would delegate to Recipe Chef Agent
                meal_plan = {
                    "task_id": task_id,
                    "meals": [
                        {
                            "day": f"Day {i+1}",
                            "breakfast": "Oatmeal with fruits",
                            "lunch": "Grilled chicken salad",
                            "dinner": "Pasta with vegetables",
                            "estimated_cost": 12.50
                        } for i in range(number_of_meals)
                    ],
                    "total_estimated_cost": number_of_meals * 12.50,
                    "dietary_preferences": dietary_preferences,
                    "budget_status": {
                        "weekly_budget": float(self.budget_tracker.weekly_budget),
                        "remaining": float(self.budget_tracker.remaining_budget),
                        "projected_spending": number_of_meals * 12.50
                    }
                }
                
                self._complete_task(task_id, meal_plan)
                return meal_plan
                
            except Exception as e:
                logger.error(f"Error creating meal plan: {e}")
                return {"error": str(e), "task_id": task_id if 'task_id' in locals() else None}

        return FunctionTool(create_meal_plan)

    def _track_budget_tool(self) -> FunctionTool:
        """Create a tool for budget tracking."""
        async def track_budget(amount: float, description: str = "") -> Dict[str, Any]:
            """Track spending against the weekly budget.
            
            Args:
                amount: Amount spent
                description: Description of the expense
                
            Returns:
                Updated budget status
            """
            try:
                self.budget_tracker.update_spent(Decimal(str(amount)))
                
                return {
                    "amount_spent": amount,
                    "description": description,
                    "weekly_budget": float(self.budget_tracker.weekly_budget),
                    "total_spent": float(self.budget_tracker.current_spent),
                    "remaining_budget": float(self.budget_tracker.remaining_budget),
                    "budget_percentage_used": float(
                        (self.budget_tracker.current_spent / self.budget_tracker.weekly_budget) * 100
                    ),
                    "last_updated": self.budget_tracker.last_updated.isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error tracking budget: {e}")
                return {"error": str(e)}

        return FunctionTool(track_budget)

    def _get_grocery_prices_tool(self) -> FunctionTool:
        """Create a tool for getting grocery prices."""
        async def get_grocery_prices(items: List[str], store_preference: str = "any") -> Dict[str, Any]:
            """Get current grocery prices for specified items.
            
            Args:
                items: List of grocery items to price check
                store_preference: Preferred store (walmart, target, kroger, or any)
                
            Returns:
                Price comparison data
            """
            try:
                # Create task for grocery price checking
                task_id = self._create_task("price_checking", {
                    "items": items,
                    "store_preference": store_preference
                })
                
                # Placeholder implementation - would delegate to Grocery Browser Agent
                price_data = {
                    "task_id": task_id,
                    "items": [
                        {
                            "item": item,
                            "walmart_price": 3.99,
                            "target_price": 4.29,
                            "kroger_price": 3.79,
                            "best_price": 3.79,
                            "best_store": "kroger"
                        } for item in items
                    ],
                    "total_best_price": len(items) * 3.79,
                    "store_preference": store_preference,
                    "last_updated": datetime.now().isoformat()
                }
                
                self._complete_task(task_id, price_data)
                return price_data
                
            except Exception as e:
                logger.error(f"Error getting grocery prices: {e}")
                return {"error": str(e), "task_id": task_id if 'task_id' in locals() else None}

        return FunctionTool(get_grocery_prices)

    def _create_shopping_list_tool(self) -> FunctionTool:
        """Create a tool for generating optimized shopping lists."""
        async def create_shopping_list(
            meal_plan_id: str,
            store_preference: str = "best_price"
        ) -> Dict[str, Any]:
            """Create an optimized shopping list from a meal plan.
            
            Args:
                meal_plan_id: ID of the meal plan to create shopping list for
                store_preference: Store preference for optimization
                
            Returns:
                Optimized shopping list with store recommendations
            """
            try:
                task_id = self._create_task("shopping_list_creation", {
                    "meal_plan_id": meal_plan_id,
                    "store_preference": store_preference
                })
                
                # Placeholder implementation
                shopping_list = {
                    "task_id": task_id,
                    "meal_plan_id": meal_plan_id,
                    "items": [
                        {
                            "item": "Chicken breast (2 lbs)",
                            "quantity": 1,
                            "estimated_price": 8.99,
                            "recommended_store": "walmart",
                            "category": "protein"
                        },
                        {
                            "item": "Mixed vegetables (frozen)",
                            "quantity": 2,
                            "estimated_price": 3.49,
                            "recommended_store": "kroger",
                            "category": "vegetables"
                        }
                    ],
                    "total_estimated_cost": 12.48,
                    "store_optimization": store_preference,
                    "budget_impact": {
                        "fits_budget": True,
                        "remaining_after_purchase": float(self.budget_tracker.remaining_budget) - 12.48
                    }
                }
                
                self._complete_task(task_id, shopping_list)
                return shopping_list
                
            except Exception as e:
                logger.error(f"Error creating shopping list: {e}")
                return {"error": str(e), "task_id": task_id if 'task_id' in locals() else None}

        return FunctionTool(create_shopping_list)

    def _get_budget_status_tool(self) -> FunctionTool:
        """Create a tool for getting current budget status."""
        async def get_budget_status() -> Dict[str, Any]:
            """Get current budget status and spending summary.
            
            Returns:
                Current budget status and recommendations
            """
            try:
                days_remaining = 7 - datetime.now().weekday()  # Assuming weekly budget resets on Monday
                daily_remaining_budget = float(self.budget_tracker.remaining_budget) / max(days_remaining, 1)
                
                return {
                    "weekly_budget": float(self.budget_tracker.weekly_budget),
                    "current_spent": float(self.budget_tracker.current_spent),
                    "remaining_budget": float(self.budget_tracker.remaining_budget),
                    "budget_percentage_used": float(
                        (self.budget_tracker.current_spent / self.budget_tracker.weekly_budget) * 100
                    ),
                    "days_remaining_in_week": days_remaining,
                    "daily_remaining_budget": daily_remaining_budget,
                    "budget_status": "healthy" if self.budget_tracker.remaining_budget > 0 else "over_budget",
                    "last_updated": self.budget_tracker.last_updated.isoformat(),
                    "recommendations": self._generate_budget_recommendations()
                }
                
            except Exception as e:
                logger.error(f"Error getting budget status: {e}")
                return {"error": str(e)}

        return FunctionTool(get_budget_status)

    def _create_task(self, task_type: str, task_data: Dict[str, Any]) -> str:
        """Create a new task and return its ID."""
        self.task_counter += 1
        task_id = f"{task_type}_{self.task_counter}_{int(datetime.now().timestamp())}"
        
        self.active_tasks[task_id] = TaskTracker(
            task_id=task_id,
            task_type=task_type,
            status="in_progress"
        )
        
        logger.info(f"Created task {task_id} of type {task_type}")
        return task_id

    def _complete_task(self, task_id: str, result: Dict[str, Any]) -> None:
        """Mark a task as completed with results."""
        if task_id in self.active_tasks:
            self.active_tasks[task_id].status = "completed"
            self.active_tasks[task_id].completed_at = datetime.now()
            self.active_tasks[task_id].result = result
            logger.info(f"Completed task {task_id}")

    def _fail_task(self, task_id: str, error_message: str) -> None:
        """Mark a task as failed with error message."""
        if task_id in self.active_tasks:
            self.active_tasks[task_id].status = "failed"
            self.active_tasks[task_id].completed_at = datetime.now()
            self.active_tasks[task_id].error_message = error_message
            logger.error(f"Failed task {task_id}: {error_message}")

    def _generate_budget_recommendations(self) -> List[str]:
        """Generate budget recommendations based on current status."""
        recommendations = []
        
        budget_percentage = (self.budget_tracker.current_spent / self.budget_tracker.weekly_budget) * 100
        
        if budget_percentage > 90:
            recommendations.append("You're close to your budget limit. Consider simple, low-cost meals.")
        elif budget_percentage > 75:
            recommendations.append("You've used most of your budget. Focus on pantry staples and sales.")
        elif budget_percentage < 25:
            recommendations.append("You have plenty of budget remaining. Consider trying new recipes!")
        
        if self.budget_tracker.remaining_budget < 0:
            recommendations.append("You've exceeded your weekly budget. Consider meal prep to save costs.")
        
        return recommendations

    async def set_weekly_budget(self, amount: float) -> Dict[str, Any]:
        """Set the weekly budget amount."""
        try:
            self.budget_tracker.weekly_budget = Decimal(str(amount))
            self.budget_tracker.remaining_budget = self.budget_tracker.weekly_budget - self.budget_tracker.current_spent
            
            return {
                "success": True,
                "new_weekly_budget": amount,
                "remaining_budget": float(self.budget_tracker.remaining_budget),
                "message": f"Weekly budget set to ${amount:.2f}"
            }
        except Exception as e:
            logger.error(f"Error setting weekly budget: {e}")
            return {"success": False, "error": str(e)}

    async def reset_weekly_budget(self) -> Dict[str, Any]:
        """Reset the weekly budget (typically called at start of new week)."""
        try:
            self.budget_tracker.reset_weekly()
            return {
                "success": True,
                "message": "Weekly budget has been reset",
                "weekly_budget": float(self.budget_tracker.weekly_budget),
                "remaining_budget": float(self.budget_tracker.remaining_budget)
            }
        except Exception as e:
            logger.error(f"Error resetting weekly budget: {e}")
            return {"success": False, "error": str(e)}

    def get_task_status(self, task_id: str) -> Optional[TaskTracker]:
        """Get the status of a specific task."""
        return self.active_tasks.get(task_id)

    def get_all_tasks(self) -> Dict[str, TaskTracker]:
        """Get all active tasks."""
        return self.active_tasks.copy()
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the Bruno Master Agent."""
        return """
You are Bruno, a helpful AI assistant that coordinates meal planning, grocery shopping, and budget management. 
You help users create meal plans, find recipes, manage shopping lists, and track their grocery budget.

Your capabilities include:
- Creating personalized meal plans based on dietary preferences and budget
- Finding and suggesting recipes
- Managing grocery shopping lists
- Tracking grocery budgets and expenses
- Coordinating with specialized agents for specific tasks

Always be helpful, friendly, and focused on providing practical solutions for meal planning and grocery shopping.
"""