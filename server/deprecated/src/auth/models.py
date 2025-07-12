"""
Authentication models and data structures for Bruno AI
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

class UserRegistration(BaseModel):
    """User registration request model"""
    username: str
    email: EmailStr
    password: str
    family_size: Optional[int] = 1
    zip_code: Optional[str] = None

class UserLogin(BaseModel):
    """User login request model"""
    email: EmailStr
    password: str

class UserToken(BaseModel):
    """JWT token response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes

class SessionData(BaseModel):
    """User session data"""
    user_id: int
    email: str
    username: str
    is_active: bool
    last_login: Optional[datetime] = None

class UserProfileUpdate(BaseModel):
    """User profile update model"""
    family_size: Optional[int] = None
    age_groups: Optional[List[str]] = None
    activity_levels: Optional[List[str]] = None
    zip_code: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    dietary_restrictions: Optional[List[str]] = None
    food_allergies: Optional[List[str]] = None
    cuisine_preferences: Optional[List[str]] = None
    disliked_foods: Optional[List[str]] = None
    default_budget: Optional[float] = None
    budget_timeframe: Optional[str] = None
    preferred_stores: Optional[List[str]] = None
    shopping_frequency: Optional[str] = None
    cooking_skill_level: Optional[str] = None
    max_cooking_time: Optional[int] = None
    meal_types: Optional[List[str]] = None

class UserResponse(BaseModel):
    """User information response model"""
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    profile: Optional[Dict[str, Any]] = None

class PasswordChange(BaseModel):
    """Password change request model"""
    current_password: str
    new_password: str

class PasswordReset(BaseModel):
    """Password reset request model"""
    email: EmailStr

class TokenRefresh(BaseModel):
    """Token refresh request model"""
    refresh_token: str
