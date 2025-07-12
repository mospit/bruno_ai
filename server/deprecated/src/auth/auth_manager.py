"""
Authentication Manager for Bruno AI
Handles user registration, login, authentication, and profile management
"""

from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from loguru import logger

from ..database.models import User, UserProfile
from ..database.connection import database_manager
from .security import password_utils, jwt_utils
from .models import UserRegistration, UserLogin, UserToken, SessionData, UserProfileUpdate

class AuthManager:
    """Manage user authentication and profile operations"""
    
    def __init__(self):
        self.db_manager = database_manager
    
    async def register_user(self, registration_data: UserRegistration) -> Dict[str, Any]:
        """Register a new user with profile"""
        session = self.db_manager.get_session()
        
        try:
            # Check if user already exists
            existing_user = session.query(User).filter(
                (User.email == registration_data.email) | 
                (User.username == registration_data.username)
            ).first()
            
            if existing_user:
                return {
                    "success": False,
                    "error": "User with this email or username already exists"
                }
            
            # Hash password
            hashed_password = password_utils.hash_password(registration_data.password)
            
            # Create user
            new_user = User(
                email=registration_data.email,
                username=registration_data.username,
                hashed_password=hashed_password,
                is_active=True
            )
            
            session.add(new_user)
            session.flush()  # Get the user ID
            
            # Create user profile
            user_profile = UserProfile(
                user_id=new_user.id,
                family_size=registration_data.family_size or 1,
                zip_code=registration_data.zip_code
            )
            
            session.add(user_profile)
            session.commit()
            
            # Generate tokens
            tokens = self._generate_user_tokens(new_user.id, new_user.email)
            
            logger.info(f"New user registered: {new_user.email}")
            
            return {
                "success": True,
                "user": {
                    "id": new_user.id,
                    "username": new_user.username,
                    "email": new_user.email,
                    "created_at": new_user.created_at
                },
                "tokens": tokens
            }
            
        except IntegrityError as e:
            session.rollback()
            logger.error(f"Database integrity error during registration: {e}")
            return {
                "success": False,
                "error": "Registration failed due to data conflict"
            }
        except Exception as e:
            session.rollback()
            logger.error(f"Registration error: {e}")
            return {
                "success": False,
                "error": "Registration failed"
            }
        finally:
            session.close()
    
    async def authenticate_user(self, login_data: UserLogin) -> Dict[str, Any]:
        """Authenticate user and return tokens"""
        session = self.db_manager.get_session()
        
        try:
            # Find user by email
            user = session.query(User).filter(User.email == login_data.email).first()
            
            if not user:
                return {
                    "success": False,
                    "error": "Invalid email or password"
                }
            
            # Verify password
            if not password_utils.verify_password(login_data.password, user.hashed_password):
                return {
                    "success": False,
                    "error": "Invalid email or password"
                }
            
            # Check if user is active
            if not user.is_active:
                return {
                    "success": False,
                    "error": "Account is deactivated"
                }
            
            # Update last login
            user.last_login = datetime.utcnow()
            session.commit()
            
            # Generate tokens
            tokens = self._generate_user_tokens(user.id, user.email)
            
            logger.info(f"User authenticated: {user.email}")
            
            return {
                "success": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "last_login": user.last_login
                },
                "tokens": tokens
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return {
                "success": False,
                "error": "Authentication failed"
            }
        finally:
            session.close()
    
    async def get_user_by_token(self, token: str) -> Optional[SessionData]:
        """Get user information from JWT token"""
        payload = jwt_utils.verify_token(token)
        
        if not payload:
            return None
        
        session = self.db_manager.get_session()
        
        try:
            user = session.query(User).filter(User.id == payload['user_id']).first()
            
            if not user or not user.is_active:
                return None
            
            return SessionData(
                user_id=user.id,
                email=user.email,
                username=user.username,
                is_active=user.is_active,
                last_login=user.last_login
            )
            
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return None
        finally:
            session.close()
    
    async def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get complete user profile"""
        session = self.db_manager.get_session()
        
        try:
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return None
            
            profile_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "last_login": user.last_login,
                "profile": None
            }
            
            if user.profile:
                profile_data["profile"] = {
                    "family_size": user.profile.family_size,
                    "age_groups": user.profile.age_groups,
                    "activity_levels": user.profile.activity_levels,
                    "zip_code": user.profile.zip_code,
                    "city": user.profile.city,
                    "state": user.profile.state,
                    "timezone": user.profile.timezone,
                    "dietary_restrictions": user.profile.dietary_restrictions,
                    "food_allergies": user.profile.food_allergies,
                    "cuisine_preferences": user.profile.cuisine_preferences,
                    "disliked_foods": user.profile.disliked_foods,
                    "default_budget": user.profile.default_budget,
                    "budget_timeframe": user.profile.budget_timeframe,
                    "preferred_stores": user.profile.preferred_stores,
                    "shopping_frequency": user.profile.shopping_frequency,
                    "cooking_skill_level": user.profile.cooking_skill_level,
                    "max_cooking_time": user.profile.max_cooking_time,
                    "meal_types": user.profile.meal_types
                }
            
            return profile_data
            
        except Exception as e:
            logger.error(f"Get profile error: {e}")
            return None
        finally:
            session.close()
    
    async def update_user_profile(self, user_id: int, profile_update: UserProfileUpdate) -> Dict[str, Any]:
        """Update user profile information"""
        session = self.db_manager.get_session()
        
        try:
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return {
                    "success": False,
                    "error": "User not found"
                }
            
            # Get or create profile
            profile = user.profile
            if not profile:
                profile = UserProfile(user_id=user_id)
                session.add(profile)
            
            # Update profile fields
            update_data = profile_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(profile, field):
                    setattr(profile, field, value)
            
            profile.updated_at = datetime.utcnow()
            session.commit()
            
            logger.info(f"Profile updated for user: {user.email}")
            
            return {
                "success": True,
                "message": "Profile updated successfully"
            }
            
        except Exception as e:
            session.rollback()
            logger.error(f"Profile update error: {e}")
            return {
                "success": False,
                "error": "Profile update failed"
            }
        finally:
            session.close()
    
    async def change_password(self, user_id: int, current_password: str, new_password: str) -> Dict[str, Any]:
        """Change user password"""
        session = self.db_manager.get_session()
        
        try:
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                return {
                    "success": False,
                    "error": "User not found"
                }
            
            # Verify current password
            if not password_utils.verify_password(current_password, user.hashed_password):
                return {
                    "success": False,
                    "error": "Current password is incorrect"
                }
            
            # Hash new password
            user.hashed_password = password_utils.hash_password(new_password)
            user.updated_at = datetime.utcnow()
            session.commit()
            
            logger.info(f"Password changed for user: {user.email}")
            
            return {
                "success": True,
                "message": "Password changed successfully"
            }
            
        except Exception as e:
            session.rollback()
            logger.error(f"Password change error: {e}")
            return {
                "success": False,
                "error": "Password change failed"
            }
        finally:
            session.close()
    
    async def refresh_token(self, refresh_token: str) -> Optional[UserToken]:
        """Refresh access token using refresh token"""
        new_access_token = jwt_utils.refresh_access_token(refresh_token)
        
        if not new_access_token:
            return None
        
        # Verify the refresh token to get user info
        payload = jwt_utils.verify_token(refresh_token)
        if not payload:
            return None
        
        return UserToken(
            access_token=new_access_token,
            refresh_token=refresh_token,  # Keep same refresh token
            token_type="bearer",
            expires_in=1800
        )
    
    def _generate_user_tokens(self, user_id: int, user_email: str) -> UserToken:
        """Generate access and refresh tokens for user"""
        access_token = jwt_utils.create_access_token(user_id, user_email)
        refresh_token = jwt_utils.create_refresh_token(user_id, user_email)
        
        return UserToken(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=1800
        )

# Global auth manager instance
auth_manager = AuthManager()
