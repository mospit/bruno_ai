"""
Authentication API routes for Bruno AI
Handles user registration, login, token refresh, and profile management
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from ..auth.auth_manager import auth_manager
from ..auth.models import (
    UserRegistration, UserLogin, UserToken, UserResponse,
    PasswordChange, TokenRefresh, SessionData
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

@router.post("/register", response_model=dict)
async def register_user(user_data: UserRegistration):
    """Register a new user account"""
    
    result = await auth_manager.register_user(user_data)
    
    if not result['success']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result['error']
        )
    
    return {
        "message": "User registered successfully",
        "user": result['user'],
        "tokens": result['tokens']
    }

@router.post("/login", response_model=dict)
async def login_user(login_data: UserLogin):
    """Authenticate user and return access tokens"""
    
    result = await auth_manager.authenticate_user(login_data)
    
    if not result['success']:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result['error']
        )
    
    return {
        "message": "Login successful",
        "user": result['user'],
        "tokens": result['tokens']
    }

@router.post("/refresh", response_model=UserToken)
async def refresh_token(refresh_data: TokenRefresh):
    """Refresh access token using refresh token"""
    
    new_tokens = await auth_manager.refresh_token(refresh_data.refresh_token)
    
    if not new_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    return new_tokens

@router.get("/me", response_model=UserResponse)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user information"""
    
    user_session = await auth_manager.get_user_by_token(credentials.credentials)
    
    if not user_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Get full user profile
    user_profile = await auth_manager.get_user_profile(user_session.user_id)
    
    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    
    return UserResponse(**user_profile)

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Change user password"""
    
    user_session = await auth_manager.get_user_by_token(credentials.credentials)
    
    if not user_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    result = await auth_manager.change_password(
        user_id=user_session.user_id,
        current_password=password_data.current_password,
        new_password=password_data.new_password
    )
    
    if not result['success']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result['error']
        )
    
    return {"message": "Password changed successfully"}

@router.post("/logout")
async def logout_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout user (client should discard tokens)"""
    
    # In a production system, you might want to blacklist the token
    # For now, we just return success as logout is handled client-side
    
    return {"message": "Logged out successfully"}

# Dependency for getting current user
async def get_current_user_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> SessionData:
    """Dependency to get current authenticated user"""
    
    user_session = await auth_manager.get_user_by_token(credentials.credentials)
    
    if not user_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return user_session
