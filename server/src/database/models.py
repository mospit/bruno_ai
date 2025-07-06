"""
SQLAlchemy models for Bruno AI long-term memory system
Defines tables for users, preferences, meal plans, budget analysis, and learning data
"""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, List, Any

Base = declarative_base()

class User(Base):
    """Core user account information"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    meal_plans = relationship("MealPlan", back_populates="user")
    budget_analyses = relationship("BudgetAnalysis", back_populates="user")
    interactions = relationship("UserInteraction", back_populates="user")
    preferences = relationship("UserPreference", back_populates="user")
    shopping_lists = relationship("ShoppingList", back_populates="user")

class UserProfile(Base):
    """Detailed user profile and family information"""
    __tablename__ = 'user_profiles'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    
    # Family details
    family_size = Column(Integer, default=1)
    age_groups = Column(JSON, default=list)  # ['adult', 'teen', 'child']
    activity_levels = Column(JSON, default=list)  # ['sedentary', 'active', 'very_active']
    
    # Location and preferences
    zip_code = Column(String(10))
    city = Column(String(100))
    state = Column(String(50))
    timezone = Column(String(50), default='UTC')
    
    # Dietary information
    dietary_restrictions = Column(JSON, default=list)  # ['vegetarian', 'gluten_free', etc.]
    food_allergies = Column(JSON, default=list)
    cuisine_preferences = Column(JSON, default=list)
    disliked_foods = Column(JSON, default=list)
    
    # Budget and shopping preferences
    default_budget = Column(Float, default=100.0)
    budget_timeframe = Column(String(20), default='week')  # 'week', 'month'
    preferred_stores = Column(JSON, default=list)
    shopping_frequency = Column(String(20), default='weekly')
    
    # Meal planning preferences
    cooking_skill_level = Column(String(20), default='beginner')  # 'beginner', 'intermediate', 'advanced'
    max_cooking_time = Column(Integer, default=30)  # minutes
    meal_types = Column(JSON, default=list)  # ['breakfast', 'lunch', 'dinner', 'snacks']
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="profile")

class MealPlan(Base):
    """Generated meal plans and their performance"""
    __tablename__ = 'meal_plans'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Plan details
    name = Column(String(200))
    duration_days = Column(Integer, default=7)
    target_budget = Column(Float, nullable=False)
    actual_cost = Column(Float)
    
    # Plan data
    recipes = Column(JSON)  # Full recipe data
    nutrition_summary = Column(JSON)
    shopping_list_data = Column(JSON)
    
    # Performance metrics
    user_rating = Column(Integer)  # 1-5 stars
    completion_rate = Column(Float)  # 0.0-1.0
    budget_accuracy = Column(Float)  # How close to target budget
    
    # Status and dates
    status = Column(String(20), default='active')  # 'active', 'completed', 'cancelled'
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="meal_plans")
    recipes_detail = relationship("Recipe", back_populates="meal_plan")

class Recipe(Base):
    """Individual recipes with performance tracking"""
    __tablename__ = 'recipes'
    
    id = Column(Integer, primary_key=True, index=True)
    meal_plan_id = Column(Integer, ForeignKey('meal_plans.id'))
    
    # Recipe details
    name = Column(String(200), nullable=False)
    description = Column(Text)
    cuisine_type = Column(String(50))
    meal_type = Column(String(20))  # 'breakfast', 'lunch', 'dinner', 'snack'
    
    # Recipe data
    ingredients = Column(JSON)  # List of ingredients with quantities
    instructions = Column(JSON)  # Step-by-step instructions
    nutrition_info = Column(JSON)
    
    # Metrics
    servings = Column(Integer, default=4)
    prep_time = Column(Integer)  # minutes
    cook_time = Column(Integer)  # minutes
    cost_per_serving = Column(Float)
    
    # Performance tracking
    times_made = Column(Integer, default=0)
    average_rating = Column(Float)
    success_rate = Column(Float, default=1.0)  # How often users complete it
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    meal_plan = relationship("MealPlan", back_populates="recipes_detail")

class BudgetAnalysis(Base):
    """Budget analysis history and performance tracking"""
    __tablename__ = 'budget_analyses'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Analysis period
    analysis_date = Column(DateTime(timezone=True), server_default=func.now())
    period_start = Column(DateTime(timezone=True))
    period_end = Column(DateTime(timezone=True))
    
    # Budget data
    target_budget = Column(Float, nullable=False)
    actual_spending = Column(Float)
    variance = Column(Float)  # actual - target
    variance_percentage = Column(Float)
    
    # Category breakdown
    category_spending = Column(JSON)  # spending by food category
    optimization_opportunities = Column(JSON)
    
    # Performance metrics
    feasibility_score = Column(Float)
    optimization_score = Column(Float)
    prediction_accuracy = Column(Float)
    
    # Analysis results
    recommendations = Column(JSON)
    seasonal_factors = Column(JSON)
    trends_identified = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="budget_analyses")

class UserInteraction(Base):
    """Track all user interactions for learning"""
    __tablename__ = 'user_interactions'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Interaction details
    interaction_type = Column(String(50), nullable=False)  # 'meal_plan', 'recipe_request', etc.
    user_message = Column(Text)
    agent_response = Column(Text)
    
    # Context data
    context_data = Column(JSON)  # Full context of the interaction
    response_time = Column(Float)
    
    # User feedback
    user_satisfaction = Column(Integer)  # 1-5 rating
    feedback_text = Column(Text)
    was_helpful = Column(Boolean)
    
    # Learning data
    extracted_preferences = Column(JSON)
    learned_patterns = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="interactions")

class UserPreference(Base):
    """Learned user preferences and patterns"""
    __tablename__ = 'user_preferences'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Preference details
    preference_type = Column(String(50), nullable=False)  # 'food', 'budget', 'cooking', etc.
    preference_key = Column(String(100), nullable=False)
    preference_value = Column(JSON)
    
    # Learning metadata
    confidence_score = Column(Float, default=0.5)  # 0.0-1.0
    learning_source = Column(String(50))  # 'explicit', 'implicit', 'pattern'
    times_observed = Column(Integer, default=1)
    
    # Temporal data
    first_observed = Column(DateTime(timezone=True), server_default=func.now())
    last_reinforced = Column(DateTime(timezone=True), server_default=func.now())
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="preferences")
    
    # Unique constraint to avoid duplicates
    __table_args__ = (
        Index('ix_user_preference_unique', 'user_id', 'preference_type', 'preference_key', unique=True),
    )

class FoodItem(Base):
    """Food items for shopping and inventory tracking"""
    __tablename__ = 'food_items'
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Item details
    name = Column(String(200), nullable=False)
    category = Column(String(50))
    subcategory = Column(String(50))
    brand = Column(String(100))
    
    # Nutritional information
    nutrition_per_100g = Column(JSON)
    allergens = Column(JSON, default=list)
    
    # Shopping data
    average_price = Column(Float)
    typical_unit = Column(String(20))  # 'lb', 'oz', 'each', etc.
    seasonal_availability = Column(JSON)
    
    # User interaction data
    times_purchased = Column(Integer, default=0)
    average_user_rating = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ShoppingList(Base):
    """Shopping lists and purchase history"""
    __tablename__ = 'shopping_lists'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # List details
    name = Column(String(200))
    total_budget = Column(Float)
    estimated_cost = Column(Float)
    actual_cost = Column(Float)
    
    # List data
    items = Column(JSON)  # List of items with quantities and prices
    store_assignments = Column(JSON)  # Which items from which stores
    
    # Status and completion
    status = Column(String(20), default='pending')  # 'pending', 'shopping', 'completed'
    completion_percentage = Column(Float, default=0.0)
    
    # Dates
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Performance metrics
    budget_accuracy = Column(Float)
    shopping_efficiency = Column(Float)
    
    # Relationships
    user = relationship("User", back_populates="shopping_lists")

class LearningModel(Base):
    """Store ML model states and learning progress"""
    __tablename__ = 'learning_models'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    
    # Model details
    model_type = Column(String(50), nullable=False)  # 'preference', 'budget', 'recipe'
    model_name = Column(String(100), nullable=False)
    
    # Model data
    model_state = Column(JSON)  # Serialized model parameters
    training_data_hash = Column(String(64))  # To track when retraining is needed
    
    # Performance metrics
    accuracy_score = Column(Float)
    confidence_score = Column(Float)
    prediction_count = Column(Integer, default=0)
    
    # Training metadata
    last_trained = Column(DateTime(timezone=True), server_default=func.now())
    training_samples = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    version = Column(String(20), default='1.0')
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
