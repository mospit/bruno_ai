"""Recipe Chef Agent - Intelligent meal planning and recipe optimization.

This agent specializes in creating budget-conscious meal plans, optimizing recipes
for cost and nutrition, and providing cooking guidance.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import json
import random

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NutritionInfo(BaseModel):
    """Model for nutritional information."""
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    sodium_mg: float
    sugar_g: float = 0.0


class Ingredient(BaseModel):
    """Model for recipe ingredients."""
    name: str
    quantity: float
    unit: str
    estimated_cost: Decimal
    category: str = "other"  # protein, vegetable, grain, dairy, etc.
    substitutes: List[str] = Field(default_factory=list)


class Recipe(BaseModel):
    """Model for complete recipe information."""
    name: str
    description: str
    ingredients: List[Ingredient]
    instructions: List[str]
    prep_time_minutes: int
    cook_time_minutes: int
    servings: int
    difficulty: str = "easy"  # easy, medium, hard
    cuisine_type: str = "american"
    dietary_tags: List[str] = Field(default_factory=list)  # vegetarian, vegan, gluten-free, etc.
    nutrition: Optional[NutritionInfo] = None
    estimated_total_cost: Decimal = Field(default=Decimal('0.00'))
    cost_per_serving: Decimal = Field(default=Decimal('0.00'))
    created_at: datetime = Field(default_factory=datetime.now)


class MealPlan(BaseModel):
    """Model for complete meal plan."""
    plan_id: str
    name: str
    duration_days: int
    target_budget: Decimal
    dietary_preferences: List[str]
    meals: Dict[str, Dict[str, Recipe]]  # {"day_1": {"breakfast": Recipe, "lunch": Recipe, "dinner": Recipe}}
    shopping_list: List[Ingredient]
    total_estimated_cost: Decimal
    nutritional_summary: Dict[str, float]
    created_at: datetime = Field(default_factory=datetime.now)


class RecipeChefAgent(LlmAgent):
    """Recipe Chef Agent for intelligent meal planning and recipe optimization."""

    def __init__(self, model: str = "gemini-2.0-flash-exp"):
        # Initialize parent class first
        super().__init__(
            model=model,
            name="recipe_chef_agent",
            description="Intelligent meal planning and recipe optimization agent focused on budget-conscious cooking",
            instruction="""You are an expert chef and meal planning specialist focused on
            creating delicious, nutritious, and budget-friendly meals.
            
            Your expertise includes:
            1. Creating comprehensive meal plans within specific budget constraints
            2. Optimizing recipes for cost without sacrificing nutrition or taste
            3. Suggesting ingredient substitutions to reduce costs or accommodate dietary needs
            4. Calculating accurate nutritional information for recipes and meal plans
            5. Generating efficient shopping lists that minimize waste
            6. Providing practical cooking tips and techniques
            
            Always prioritize:
            - Budget consciousness while maintaining nutritional value
            - Practical recipes that match user's cooking skill level
            - Seasonal and locally available ingredients when possible
            - Minimal food waste through smart portioning and ingredient usage
            - Clear, easy-to-follow cooking instructions
            
            When creating meal plans, consider the user's dietary preferences, cooking
            experience, available time, and budget constraints. Provide alternatives
            and substitutions when possible.""",
            tools=[]
        )
        
        # Initialize data after parent class is ready
        self._recipe_database: Dict[str, Recipe] = {}
        self._meal_plans: Dict[str, MealPlan] = {}
        self._ingredient_costs: Dict[str, Decimal] = {}
        
        # Initialize with some basic recipes
        self._initialize_recipe_database()
        self._initialize_ingredient_costs()
        
        # Now add tools after everything is initialized
        self.tools = [
            self._create_meal_plan_tool(),
            self._optimize_recipe_for_budget_tool(),
            self._suggest_recipe_substitutions_tool(),
            self._calculate_recipe_nutrition_tool(),
            self._generate_shopping_list_tool(),
            self._find_recipes_by_ingredients_tool(),
            self._scale_recipe_tool(),
            self._get_cooking_tips_tool()
        ]

    def _initialize_recipe_database(self) -> None:
        """Initialize the recipe database with basic recipes."""
        # Sample recipes for demonstration
        recipes = [
            {
                "name": "Budget Chicken Stir Fry",
                "description": "Quick and affordable chicken stir fry with mixed vegetables",
                "ingredients": [
                    {"name": "Chicken breast", "quantity": 1.0, "unit": "lb", "estimated_cost": 4.99, "category": "protein"},
                    {"name": "Mixed frozen vegetables", "quantity": 1.0, "unit": "bag", "estimated_cost": 2.49, "category": "vegetable"},
                    {"name": "Rice", "quantity": 1.0, "unit": "cup", "estimated_cost": 0.50, "category": "grain"},
                    {"name": "Soy sauce", "quantity": 2.0, "unit": "tbsp", "estimated_cost": 0.25, "category": "condiment"},
                    {"name": "Vegetable oil", "quantity": 1.0, "unit": "tbsp", "estimated_cost": 0.10, "category": "oil"}
                ],
                "instructions": [
                    "Cook rice according to package directions",
                    "Cut chicken into bite-sized pieces",
                    "Heat oil in large pan or wok over medium-high heat",
                    "Cook chicken until no longer pink, about 5-7 minutes",
                    "Add frozen vegetables and cook for 3-4 minutes",
                    "Add soy sauce and stir to combine",
                    "Serve over rice"
                ],
                "prep_time_minutes": 10,
                "cook_time_minutes": 15,
                "servings": 4,
                "difficulty": "easy",
                "cuisine_type": "asian",
                "dietary_tags": ["gluten-free-option"]
            },
            {
                "name": "Hearty Lentil Soup",
                "description": "Nutritious and filling lentil soup perfect for meal prep",
                "ingredients": [
                    {"name": "Red lentils", "quantity": 1.0, "unit": "cup", "estimated_cost": 1.50, "category": "protein"},
                    {"name": "Onion", "quantity": 1.0, "unit": "medium", "estimated_cost": 0.75, "category": "vegetable"},
                    {"name": "Carrots", "quantity": 2.0, "unit": "medium", "estimated_cost": 0.50, "category": "vegetable"},
                    {"name": "Celery", "quantity": 2.0, "unit": "stalks", "estimated_cost": 0.50, "category": "vegetable"},
                    {"name": "Vegetable broth", "quantity": 4.0, "unit": "cups", "estimated_cost": 1.00, "category": "liquid"},
                    {"name": "Canned tomatoes", "quantity": 1.0, "unit": "can", "estimated_cost": 1.25, "category": "vegetable"}
                ],
                "instructions": [
                    "Dice onion, carrots, and celery",
                    "Sauté vegetables in large pot until softened",
                    "Add lentils, broth, and canned tomatoes",
                    "Bring to boil, then simmer for 20-25 minutes",
                    "Season with salt and pepper to taste",
                    "Serve hot with bread if desired"
                ],
                "prep_time_minutes": 15,
                "cook_time_minutes": 30,
                "servings": 6,
                "difficulty": "easy",
                "cuisine_type": "mediterranean",
                "dietary_tags": ["vegetarian", "vegan", "gluten-free"]
            }
        ]
        
        for recipe_data in recipes:
            ingredients = [Ingredient(**ing) for ing in recipe_data["ingredients"]]
            total_cost = sum(ing.estimated_cost for ing in ingredients)
            
            recipe = Recipe(
                name=recipe_data["name"],
                description=recipe_data["description"],
                ingredients=ingredients,
                instructions=recipe_data["instructions"],
                prep_time_minutes=recipe_data["prep_time_minutes"],
                cook_time_minutes=recipe_data["cook_time_minutes"],
                servings=recipe_data["servings"],
                difficulty=recipe_data["difficulty"],
                cuisine_type=recipe_data["cuisine_type"],
                dietary_tags=recipe_data["dietary_tags"],
                estimated_total_cost=Decimal(str(total_cost)),
                cost_per_serving=Decimal(str(total_cost)) / recipe_data["servings"]
            )
            
            self._recipe_database[recipe.name.lower().replace(" ", "_")] = recipe

    def _initialize_ingredient_costs(self) -> None:
        """Initialize typical ingredient costs for estimation."""
        self._ingredient_costs = {
            # Proteins
            "chicken_breast": Decimal("4.99"),
            "ground_beef": Decimal("5.99"),
            "eggs": Decimal("2.49"),
            "lentils": Decimal("1.50"),
            "beans": Decimal("1.25"),
            "tofu": Decimal("2.99"),
            
            # Vegetables
            "onion": Decimal("0.75"),
            "carrots": Decimal("1.00"),
            "celery": Decimal("1.50"),
            "bell_peppers": Decimal("3.99"),
            "broccoli": Decimal("2.49"),
            "spinach": Decimal("2.99"),
            
            # Grains
            "rice": Decimal("2.99"),
            "pasta": Decimal("1.49"),
            "bread": Decimal("2.49"),
            "oats": Decimal("3.99"),
            
            # Dairy
            "milk": Decimal("3.49"),
            "cheese": Decimal("4.99"),
            "yogurt": Decimal("4.49"),
            "butter": Decimal("4.99"),
            
            # Pantry staples
            "olive_oil": Decimal("5.99"),
            "salt": Decimal("0.99"),
            "pepper": Decimal("2.99"),
            "garlic": Decimal("0.50"),
        }

    def _create_meal_plan_tool(self) -> FunctionTool:
        """Create tool for generating comprehensive meal plans."""
        async def create_meal_plan(
            duration_days: int,
            budget_limit: float,
            dietary_preferences: List[str],
            servings_per_meal: int = 2,
            meals_per_day: int = 3
        ) -> Dict[str, Any]:
            """Create a comprehensive meal plan within budget constraints.
            
            Args:
                duration_days: Number of days to plan for
                budget_limit: Maximum budget for the meal plan
                dietary_preferences: List of dietary preferences/restrictions
                servings_per_meal: Number of servings per meal
                meals_per_day: Number of meals per day (1=dinner only, 2=lunch+dinner, 3=all meals)
                
            Returns:
                Complete meal plan with recipes, shopping list, and cost breakdown
            """
            try:
                plan_id = f"meal_plan_{int(datetime.now().timestamp())}"
                target_budget = Decimal(str(budget_limit))
                
                # Calculate budget per meal
                total_meals = duration_days * meals_per_day
                budget_per_meal = target_budget / total_meals
                
                meals = {}
                all_ingredients = []
                total_cost = Decimal('0.00')
                
                meal_types = ["breakfast", "lunch", "dinner"][:meals_per_day]
                
                for day in range(1, duration_days + 1):
                    day_key = f"day_{day}"
                    meals[day_key] = {}
                    
                    for meal_type in meal_types:
                        # Select appropriate recipe based on meal type and budget
                        recipe = self._select_recipe_for_meal(
                            meal_type, budget_per_meal, dietary_preferences, servings_per_meal
                        )
                        
                        if recipe:
                            # Scale recipe if needed
                            scaled_recipe = self._scale_recipe_portions(recipe, servings_per_meal)
                            meals[day_key][meal_type] = scaled_recipe
                            
                            # Add ingredients to shopping list
                            all_ingredients.extend(scaled_recipe.ingredients)
                            total_cost += scaled_recipe.estimated_total_cost
                
                # Consolidate shopping list
                consolidated_shopping_list = self._consolidate_ingredients(all_ingredients)
                
                # Calculate nutritional summary
                nutritional_summary = self._calculate_plan_nutrition(meals)
                
                meal_plan = MealPlan(
                    plan_id=plan_id,
                    name=f"{duration_days}-Day Budget Meal Plan",
                    duration_days=duration_days,
                    target_budget=target_budget,
                    dietary_preferences=dietary_preferences,
                    meals=meals,
                    shopping_list=consolidated_shopping_list,
                    total_estimated_cost=total_cost,
                    nutritional_summary=nutritional_summary
                )
                
                self._meal_plans[plan_id] = meal_plan
                
                return {
                    "plan_id": plan_id,
                    "meal_plan": meal_plan.dict(),
                    "budget_analysis": {
                        "target_budget": float(target_budget),
                        "estimated_cost": float(total_cost),
                        "under_budget": total_cost <= target_budget,
                        "savings": float(target_budget - total_cost) if total_cost <= target_budget else 0,
                        "overage": float(total_cost - target_budget) if total_cost > target_budget else 0
                    },
                    "success": True
                }
                
            except Exception as e:
                logger.error(f"Error creating meal plan: {e}")
                return {"error": str(e), "success": False}

        return FunctionTool(create_meal_plan)

    def _optimize_recipe_for_budget_tool(self) -> FunctionTool:
        """Create tool for optimizing recipes to fit budget constraints."""
        async def optimize_recipe_for_budget(
            recipe_name: str,
            target_budget: float,
            servings: int = 4
        ) -> Dict[str, Any]:
            """Optimize a recipe to fit within a specific budget.
            
            Args:
                recipe_name: Name of the recipe to optimize
                target_budget: Target budget for the recipe
                servings: Number of servings needed
                
            Returns:
                Optimized recipe with cost-effective substitutions
            """
            try:
                # Find the recipe
                recipe_key = recipe_name.lower().replace(" ", "_")
                if recipe_key not in self._recipe_database:
                    return {"error": f"Recipe '{recipe_name}' not found", "success": False}
                
                original_recipe = self._recipe_database[recipe_key]
                target_budget_decimal = Decimal(str(target_budget))
                
                # Scale recipe to desired servings
                scaled_recipe = self._scale_recipe_portions(original_recipe, servings)
                
                if scaled_recipe.estimated_total_cost <= target_budget_decimal:
                    return {
                        "recipe": scaled_recipe.dict(),
                        "optimization_needed": False,
                        "original_cost": float(scaled_recipe.estimated_total_cost),
                        "target_budget": target_budget,
                        "success": True
                    }
                
                # Optimize by finding cheaper substitutions
                optimized_ingredients = []
                total_savings = Decimal('0.00')
                
                for ingredient in scaled_recipe.ingredients:
                    cheaper_option = self._find_cheaper_substitute(ingredient)
                    if cheaper_option and cheaper_option.estimated_cost < ingredient.estimated_cost:
                        savings = ingredient.estimated_cost - cheaper_option.estimated_cost
                        total_savings += savings
                        optimized_ingredients.append(cheaper_option)
                    else:
                        optimized_ingredients.append(ingredient)
                
                optimized_cost = sum(ing.estimated_cost for ing in optimized_ingredients)
                
                optimized_recipe = Recipe(
                    name=f"Budget {original_recipe.name}",
                    description=f"Budget-optimized version of {original_recipe.name}",
                    ingredients=optimized_ingredients,
                    instructions=original_recipe.instructions,
                    prep_time_minutes=original_recipe.prep_time_minutes,
                    cook_time_minutes=original_recipe.cook_time_minutes,
                    servings=servings,
                    difficulty=original_recipe.difficulty,
                    cuisine_type=original_recipe.cuisine_type,
                    dietary_tags=original_recipe.dietary_tags,
                    estimated_total_cost=Decimal(str(optimized_cost)),
                    cost_per_serving=Decimal(str(optimized_cost)) / servings
                )
                
                return {
                    "original_recipe": original_recipe.dict(),
                    "optimized_recipe": optimized_recipe.dict(),
                    "optimization_summary": {
                        "original_cost": float(scaled_recipe.estimated_total_cost),
                        "optimized_cost": float(optimized_cost),
                        "total_savings": float(total_savings),
                        "target_budget": target_budget,
                        "fits_budget": optimized_cost <= target_budget_decimal
                    },
                    "success": True
                }
                
            except Exception as e:
                logger.error(f"Error optimizing recipe: {e}")
                return {"error": str(e), "success": False}

        return FunctionTool(optimize_recipe_for_budget)

    def _suggest_recipe_substitutions_tool(self) -> FunctionTool:
        """Create tool for suggesting ingredient substitutions."""
        async def suggest_recipe_substitutions(
            ingredient_name: str,
            reason: str = "cost"
        ) -> Dict[str, Any]:
            """Suggest substitutions for a specific ingredient.
            
            Args:
                ingredient_name: Name of the ingredient to substitute
                reason: Reason for substitution (cost, dietary, availability)
                
            Returns:
                List of suitable substitutions with details
            """
            try:
                substitutions = self._get_ingredient_substitutions(ingredient_name, reason)
                
                return {
                    "original_ingredient": ingredient_name,
                    "substitution_reason": reason,
                    "substitutions": substitutions,
                    "total_options": len(substitutions),
                    "success": True
                }
                
            except Exception as e:
                logger.error(f"Error suggesting substitutions: {e}")
                return {"error": str(e), "success": False}

        return FunctionTool(suggest_recipe_substitutions)

    def _calculate_recipe_nutrition_tool(self) -> FunctionTool:
        """Create tool for calculating recipe nutrition."""
        async def calculate_recipe_nutrition(recipe_name: str) -> Dict[str, Any]:
            """Calculate nutritional information for a recipe.
            
            Args:
                recipe_name: Name of the recipe to analyze
                
            Returns:
                Detailed nutritional breakdown
            """
            try:
                recipe_key = recipe_name.lower().replace(" ", "_")
                if recipe_key not in self._recipe_database:
                    return {"error": f"Recipe '{recipe_name}' not found", "success": False}
                
                recipe = self._recipe_database[recipe_key]
                nutrition = self._calculate_nutrition_for_recipe(recipe)
                
                return {
                    "recipe_name": recipe.name,
                    "servings": recipe.servings,
                    "nutrition_per_serving": {
                        "calories": nutrition.calories // recipe.servings,
                        "protein_g": round(nutrition.protein_g / recipe.servings, 1),
                        "carbs_g": round(nutrition.carbs_g / recipe.servings, 1),
                        "fat_g": round(nutrition.fat_g / recipe.servings, 1),
                        "fiber_g": round(nutrition.fiber_g / recipe.servings, 1),
                        "sodium_mg": round(nutrition.sodium_mg / recipe.servings, 1)
                    },
                    "nutrition_total": nutrition.dict(),
                    "success": True
                }
                
            except Exception as e:
                logger.error(f"Error calculating nutrition: {e}")
                return {"error": str(e), "success": False}

        return FunctionTool(calculate_recipe_nutrition)

    def _generate_shopping_list_tool(self) -> FunctionTool:
        """Create tool for generating optimized shopping lists."""
        async def generate_shopping_list(meal_plan_id: str) -> Dict[str, Any]:
            """Generate an optimized shopping list from a meal plan.
            
            Args:
                meal_plan_id: ID of the meal plan to generate shopping list for
                
            Returns:
                Organized shopping list with cost estimates
            """
            try:
                if meal_plan_id not in self._meal_plans:
                    return {"error": f"Meal plan '{meal_plan_id}' not found", "success": False}
                
                meal_plan = self._meal_plans[meal_plan_id]
                
                # Organize shopping list by category
                categorized_list = {
                    "protein": [],
                    "vegetable": [],
                    "grain": [],
                    "dairy": [],
                    "pantry": [],
                    "other": []
                }
                
                total_cost = Decimal('0.00')
                
                for ingredient in meal_plan.shopping_list:
                    category = ingredient.category if ingredient.category in categorized_list else "other"
                    categorized_list[category].append({
                        "name": ingredient.name,
                        "quantity": ingredient.quantity,
                        "unit": ingredient.unit,
                        "estimated_cost": float(ingredient.estimated_cost)
                    })
                    total_cost += ingredient.estimated_cost
                
                return {
                    "meal_plan_id": meal_plan_id,
                    "shopping_list_by_category": categorized_list,
                    "total_items": len(meal_plan.shopping_list),
                    "total_estimated_cost": float(total_cost),
                    "budget_comparison": {
                        "target_budget": float(meal_plan.target_budget),
                        "shopping_cost": float(total_cost),
                        "under_budget": total_cost <= meal_plan.target_budget
                    },
                    "success": True
                }
                
            except Exception as e:
                logger.error(f"Error generating shopping list: {e}")
                return {"error": str(e), "success": False}

        return FunctionTool(generate_shopping_list)

    def _find_recipes_by_ingredients_tool(self) -> FunctionTool:
        """Create tool for finding recipes based on available ingredients."""
        async def find_recipes_by_ingredients(
            available_ingredients: List[str],
            max_additional_ingredients: int = 3
        ) -> Dict[str, Any]:
            """Find recipes that can be made with available ingredients.
            
            Args:
                available_ingredients: List of ingredients user has available
                max_additional_ingredients: Maximum additional ingredients to buy
                
            Returns:
                List of matching recipes with required additional ingredients
            """
            try:
                matching_recipes = []
                
                for recipe in self._recipe_database.values():
                    recipe_ingredients = [ing.name.lower() for ing in recipe.ingredients]
                    available_lower = [ing.lower() for ing in available_ingredients]
                    
                    # Find missing ingredients
                    missing_ingredients = [ing for ing in recipe_ingredients if ing not in available_lower]
                    
                    if len(missing_ingredients) <= max_additional_ingredients:
                        additional_cost = sum(
                            self._ingredient_costs.get(ing.replace(" ", "_"), Decimal('2.00'))
                            for ing in missing_ingredients
                        )
                        
                        matching_recipes.append({
                            "recipe": recipe.dict(),
                            "missing_ingredients": missing_ingredients,
                            "additional_cost": float(additional_cost),
                            "match_percentage": (len(recipe_ingredients) - len(missing_ingredients)) / len(recipe_ingredients) * 100
                        })
                
                # Sort by match percentage (highest first)
                matching_recipes.sort(key=lambda x: x["match_percentage"], reverse=True)
                
                return {
                    "available_ingredients": available_ingredients,
                    "matching_recipes": matching_recipes[:10],  # Top 10 matches
                    "total_matches": len(matching_recipes),
                    "success": True
                }
                
            except Exception as e:
                logger.error(f"Error finding recipes by ingredients: {e}")
                return {"error": str(e), "success": False}

        return FunctionTool(find_recipes_by_ingredients)

    def _scale_recipe_tool(self) -> FunctionTool:
        """Create tool for scaling recipes to different serving sizes."""
        async def scale_recipe(recipe_name: str, target_servings: int) -> Dict[str, Any]:
            """Scale a recipe to a different number of servings.
            
            Args:
                recipe_name: Name of the recipe to scale
                target_servings: Desired number of servings
                
            Returns:
                Scaled recipe with adjusted ingredients and costs
            """
            try:
                recipe_key = recipe_name.lower().replace(" ", "_")
                if recipe_key not in self._recipe_database:
                    return {"error": f"Recipe '{recipe_name}' not found", "success": False}
                
                original_recipe = self._recipe_database[recipe_key]
                scaled_recipe = self._scale_recipe_portions(original_recipe, target_servings)
                
                return {
                    "original_recipe": original_recipe.dict(),
                    "scaled_recipe": scaled_recipe.dict(),
                    "scaling_factor": target_servings / original_recipe.servings,
                    "cost_comparison": {
                        "original_total_cost": float(original_recipe.estimated_total_cost),
                        "scaled_total_cost": float(scaled_recipe.estimated_total_cost),
                        "original_cost_per_serving": float(original_recipe.cost_per_serving),
                        "scaled_cost_per_serving": float(scaled_recipe.cost_per_serving)
                    },
                    "success": True
                }
                
            except Exception as e:
                logger.error(f"Error scaling recipe: {e}")
                return {"error": str(e), "success": False}

        return FunctionTool(scale_recipe)

    def _get_cooking_tips_tool(self) -> FunctionTool:
        """Create tool for providing cooking tips and techniques."""
        async def get_cooking_tips(
            recipe_name: Optional[str] = None,
            cooking_method: Optional[str] = None,
            ingredient: Optional[str] = None
        ) -> Dict[str, Any]:
            """Get cooking tips for recipes, methods, or ingredients.
            
            Args:
                recipe_name: Specific recipe to get tips for
                cooking_method: Cooking method to get tips for (sautéing, roasting, etc.)
                ingredient: Specific ingredient to get tips for
                
            Returns:
                Relevant cooking tips and techniques
            """
            try:
                tips = []
                
                if recipe_name:
                    recipe_key = recipe_name.lower().replace(" ", "_")
                    if recipe_key in self._recipe_database:
                        recipe = self._recipe_database[recipe_key]
                        tips.extend(self._get_recipe_specific_tips(recipe))
                
                if cooking_method:
                    tips.extend(self._get_cooking_method_tips(cooking_method))
                
                if ingredient:
                    tips.extend(self._get_ingredient_tips(ingredient))
                
                if not tips:
                    tips = self._get_general_cooking_tips()
                
                return {
                    "tips": tips,
                    "context": {
                        "recipe_name": recipe_name,
                        "cooking_method": cooking_method,
                        "ingredient": ingredient
                    },
                    "success": True
                }
                
            except Exception as e:
                logger.error(f"Error getting cooking tips: {e}")
                return {"error": str(e), "success": False}

        return FunctionTool(get_cooking_tips)

    # Helper methods
    def _select_recipe_for_meal(self, meal_type: str, budget: Decimal, dietary_preferences: List[str], servings: int) -> Optional[Recipe]:
        """Select an appropriate recipe for a specific meal type and budget."""
        suitable_recipes = []
        
        for recipe in self._recipe_database.values():
            # Check if recipe fits dietary preferences
            if dietary_preferences:
                if not any(pref in recipe.dietary_tags for pref in dietary_preferences):
                    continue
            
            # Scale recipe and check budget
            scaled_recipe = self._scale_recipe_portions(recipe, servings)
            if scaled_recipe.estimated_total_cost <= budget:
                suitable_recipes.append(scaled_recipe)
        
        # Return a random suitable recipe or None if none found
        return random.choice(suitable_recipes) if suitable_recipes else None

    def _scale_recipe_portions(self, recipe: Recipe, target_servings: int) -> Recipe:
        """Scale a recipe to a different number of servings."""
        scaling_factor = target_servings / recipe.servings
        
        scaled_ingredients = []
        for ingredient in recipe.ingredients:
            scaled_ingredient = Ingredient(
                name=ingredient.name,
                quantity=ingredient.quantity * scaling_factor,
                unit=ingredient.unit,
                estimated_cost=ingredient.estimated_cost * Decimal(str(scaling_factor)),
                category=ingredient.category,
                substitutes=ingredient.substitutes
            )
            scaled_ingredients.append(scaled_ingredient)
        
        return Recipe(
            name=recipe.name,
            description=recipe.description,
            ingredients=scaled_ingredients,
            instructions=recipe.instructions,
            prep_time_minutes=recipe.prep_time_minutes,
            cook_time_minutes=recipe.cook_time_minutes,
            servings=target_servings,
            difficulty=recipe.difficulty,
            cuisine_type=recipe.cuisine_type,
            dietary_tags=recipe.dietary_tags,
            estimated_total_cost=recipe.estimated_total_cost * Decimal(str(scaling_factor)),
            cost_per_serving=recipe.cost_per_serving
        )

    def _consolidate_ingredients(self, ingredients: List[Ingredient]) -> List[Ingredient]:
        """Consolidate duplicate ingredients in a shopping list."""
        consolidated = {}
        
        for ingredient in ingredients:
            key = ingredient.name.lower()
            if key in consolidated:
                consolidated[key].quantity += ingredient.quantity
                consolidated[key].estimated_cost += ingredient.estimated_cost
            else:
                consolidated[key] = Ingredient(
                    name=ingredient.name,
                    quantity=ingredient.quantity,
                    unit=ingredient.unit,
                    estimated_cost=ingredient.estimated_cost,
                    category=ingredient.category
                )
        
        return list(consolidated.values())

    def _calculate_plan_nutrition(self, meals: Dict[str, Dict[str, Recipe]]) -> Dict[str, float]:
        """Calculate nutritional summary for a meal plan."""
        total_nutrition = {
            "calories": 0,
            "protein_g": 0.0,
            "carbs_g": 0.0,
            "fat_g": 0.0,
            "fiber_g": 0.0,
            "sodium_mg": 0.0
        }
        
        meal_count = 0
        for day_meals in meals.values():
            for recipe in day_meals.values():
                nutrition = self._calculate_nutrition_for_recipe(recipe)
                total_nutrition["calories"] += nutrition.calories
                total_nutrition["protein_g"] += nutrition.protein_g
                total_nutrition["carbs_g"] += nutrition.carbs_g
                total_nutrition["fat_g"] += nutrition.fat_g
                total_nutrition["fiber_g"] += nutrition.fiber_g
                total_nutrition["sodium_mg"] += nutrition.sodium_mg
                meal_count += 1
        
        # Calculate averages per meal
        if meal_count > 0:
            for key in total_nutrition:
                total_nutrition[f"avg_{key}_per_meal"] = total_nutrition[key] / meal_count
        
        return total_nutrition

    def _calculate_nutrition_for_recipe(self, recipe: Recipe) -> NutritionInfo:
        """Calculate nutritional information for a recipe (simplified estimation)."""
        # This is a simplified calculation - in a real implementation,
        # you would use a nutrition database API
        
        total_calories = 0
        total_protein = 0.0
        total_carbs = 0.0
        total_fat = 0.0
        total_fiber = 0.0
        total_sodium = 0.0
        
        # Basic nutrition estimates per ingredient category
        nutrition_estimates = {
            "protein": {"calories": 150, "protein": 25, "carbs": 0, "fat": 5, "fiber": 0, "sodium": 100},
            "vegetable": {"calories": 25, "protein": 2, "carbs": 5, "fat": 0, "fiber": 3, "sodium": 10},
            "grain": {"calories": 100, "protein": 3, "carbs": 20, "fat": 1, "fiber": 2, "sodium": 5},
            "dairy": {"calories": 80, "protein": 8, "carbs": 6, "fat": 4, "fiber": 0, "sodium": 120},
            "oil": {"calories": 120, "protein": 0, "carbs": 0, "fat": 14, "fiber": 0, "sodium": 0},
            "other": {"calories": 50, "protein": 1, "carbs": 10, "fat": 1, "fiber": 1, "sodium": 50}
        }
        
        for ingredient in recipe.ingredients:
            category = ingredient.category if ingredient.category in nutrition_estimates else "other"
            estimates = nutrition_estimates[category]
            
            # Scale by quantity (simplified)
            quantity_factor = ingredient.quantity / 100  # Assume per 100g/ml
            
            total_calories += estimates["calories"] * quantity_factor
            total_protein += estimates["protein"] * quantity_factor
            total_carbs += estimates["carbs"] * quantity_factor
            total_fat += estimates["fat"] * quantity_factor
            total_fiber += estimates["fiber"] * quantity_factor
            total_sodium += estimates["sodium"] * quantity_factor
        
        return NutritionInfo(
            calories=int(total_calories),
            protein_g=round(total_protein, 1),
            carbs_g=round(total_carbs, 1),
            fat_g=round(total_fat, 1),
            fiber_g=round(total_fiber, 1),
            sodium_mg=round(total_sodium, 1)
        )

    def _find_cheaper_substitute(self, ingredient: Ingredient) -> Optional[Ingredient]:
        """Find a cheaper substitute for an ingredient."""
        # Simplified substitution logic
        substitutions = {
            "chicken_breast": "chicken_thighs",
            "ground_beef": "ground_turkey",
            "fresh_vegetables": "frozen_vegetables",
            "brand_name": "store_brand"
        }
        
        ingredient_key = ingredient.name.lower().replace(" ", "_")
        
        for original, substitute in substitutions.items():
            if original in ingredient_key:
                substitute_cost = self._ingredient_costs.get(substitute, ingredient.estimated_cost * Decimal('0.8'))
                if substitute_cost < ingredient.estimated_cost:
                    return Ingredient(
                        name=substitute.replace("_", " ").title(),
                        quantity=ingredient.quantity,
                        unit=ingredient.unit,
                        estimated_cost=substitute_cost,
                        category=ingredient.category
                    )
        
        return None

    def _get_ingredient_substitutions(self, ingredient_name: str, reason: str) -> List[Dict[str, Any]]:
        """Get substitution suggestions for an ingredient."""
        substitutions = []
        
        # Common substitutions based on reason
        if reason == "cost":
            cost_substitutions = {
                "chicken breast": ["chicken thighs", "ground turkey"],
                "ground beef": ["ground turkey", "lentils"],
                "fresh herbs": ["dried herbs", "herb blends"],
                "brand name items": ["store brand alternatives"]
            }
        elif reason == "dietary":
            dietary_substitutions = {
                "dairy milk": ["almond milk", "oat milk", "soy milk"],
                "eggs": ["flax eggs", "chia eggs", "applesauce"],
                "wheat flour": ["almond flour", "coconut flour", "rice flour"]
            }
        else:
            cost_substitutions = {}
            dietary_substitutions = {}
        
        # Combine and format substitutions
        all_substitutions = {**cost_substitutions, **dietary_substitutions}
        
        ingredient_lower = ingredient_name.lower()
        for key, subs in all_substitutions.items():
            if key in ingredient_lower:
                for sub in subs:
                    substitutions.append({
                        "substitute": sub,
                        "reason": reason,
                        "cost_impact": "lower" if reason == "cost" else "similar",
                        "availability": "common"
                    })
        
        return substitutions

    def _get_recipe_specific_tips(self, recipe: Recipe) -> List[str]:
        """Get tips specific to a recipe."""
        tips = []
        
        if "stir fry" in recipe.name.lower():
            tips.extend([
                "Cut all ingredients before starting - stir frying is fast!",
                "Use high heat and keep ingredients moving",
                "Add ingredients in order of cooking time needed"
            ])
        
        if "soup" in recipe.name.lower():
            tips.extend([
                "Sauté aromatics first for better flavor",
                "Simmer, don't boil, to prevent overcooking",
                "Season gradually and taste as you go"
            ])
        
        return tips

    def _get_cooking_method_tips(self, method: str) -> List[str]:
        """Get tips for specific cooking methods."""
        method_tips = {
            "sautéing": [
                "Use medium-high heat",
                "Don't overcrowd the pan",
                "Keep ingredients moving"
            ],
            "roasting": [
                "Preheat your oven",
                "Use appropriate temperature for the ingredient",
                "Don't open the oven door too often"
            ],
            "grilling": [
                "Preheat the grill",
                "Oil the grates to prevent sticking",
                "Let meat rest after cooking"
            ]
        }
        
        return method_tips.get(method.lower(), [])

    def _get_ingredient_tips(self, ingredient: str) -> List[str]:
        """Get tips for specific ingredients."""
        ingredient_tips = {
            "chicken": [
                "Use a meat thermometer to check doneness",
                "Let rest for 5 minutes after cooking",
                "Brine for extra juiciness"
            ],
            "vegetables": [
                "Don't overcook to preserve nutrients",
                "Season with salt to draw out moisture",
                "Cut uniformly for even cooking"
            ],
            "rice": [
                "Rinse before cooking to remove excess starch",
                "Use proper water ratio (usually 2:1)",
                "Let rest after cooking before fluffing"
            ]
        }
        
        ingredient_lower = ingredient.lower()
        for key, tips in ingredient_tips.items():
            if key in ingredient_lower:
                return tips
        
        return []

    def _get_general_cooking_tips(self) -> List[str]:
        """Get general cooking tips."""
        return [
            "Read the entire recipe before starting",
            "Prep all ingredients before cooking (mise en place)",
            "Taste as you go and adjust seasoning",
            "Keep your knives sharp for safety and efficiency",
            "Clean as you cook to stay organized",
            "Use a timer to avoid overcooking",
            "Let proteins rest after cooking",
            "Season food in layers throughout cooking"
        ]