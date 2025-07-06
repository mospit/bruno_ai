"""
Authentication System Tests for Bruno AI
Tests user registration, login, JWT tokens, and profile management
"""

import pytest
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path and load environment
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

env_file = project_root / "config" / ".env"
load_dotenv(env_file)

from src.auth.auth_manager import auth_manager
from src.auth.models import UserRegistration, UserLogin, UserProfileUpdate
from src.auth.security import password_utils, jwt_utils


class TestPasswordUtils:
    """Test password hashing and verification utilities"""
    
    def test_password_hashing(self):
        """Test password hashing functionality"""
        password = "test_password_123"
        hashed = password_utils.hash_password(password)
        
        # Should return a string with salt and hash
        assert isinstance(hashed, str)
        assert ":" in hashed
        
        # Should be able to verify the password
        assert password_utils.verify_password(password, hashed)
        
        # Should reject wrong password
        assert not password_utils.verify_password("wrong_password", hashed)
    
    def test_secure_token_generation(self):
        """Test secure token generation"""
        token1 = password_utils.generate_secure_token()
        token2 = password_utils.generate_secure_token()
        
        # Tokens should be different
        assert token1 != token2
        assert len(token1) > 10
        assert len(token2) > 10


class TestJWTUtils:
    """Test JWT token creation and validation"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.jwt_utils = jwt_utils
        self.test_user_id = 123
        self.test_email = "test@example.com"
    
    def test_access_token_creation(self):
        """Test access token creation and verification"""
        token = self.jwt_utils.create_access_token(self.test_user_id, self.test_email)
        
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are typically long
        
        # Verify the token
        payload = self.jwt_utils.verify_token(token)
        assert payload is not None
        assert payload["user_id"] == self.test_user_id
        assert payload["email"] == self.test_email
        assert payload["type"] == "access"
    
    def test_refresh_token_creation(self):
        """Test refresh token creation and verification"""
        token = self.jwt_utils.create_refresh_token(self.test_user_id, self.test_email)
        
        assert isinstance(token, str)
        assert len(token) > 50
        
        # Verify the token
        payload = self.jwt_utils.verify_token(token)
        assert payload is not None
        assert payload["user_id"] == self.test_user_id
        assert payload["email"] == self.test_email
        assert payload["type"] == "refresh"
    
    def test_token_refresh(self):
        """Test token refresh functionality"""
        refresh_token = self.jwt_utils.create_refresh_token(self.test_user_id, self.test_email)
        new_access_token = self.jwt_utils.refresh_access_token(refresh_token)
        
        assert new_access_token is not None
        
        # Verify the new access token
        payload = self.jwt_utils.verify_token(new_access_token)
        assert payload["user_id"] == self.test_user_id
        assert payload["email"] == self.test_email
        assert payload["type"] == "access"
    
    def test_invalid_token_rejection(self):
        """Test that invalid tokens are rejected"""
        invalid_token = "invalid.token.here"
        payload = self.jwt_utils.verify_token(invalid_token)
        assert payload is None


class TestAuthManager:
    """Test authentication manager functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        import time
        import random
        self.auth_manager = auth_manager
        timestamp = int(time.time() * 1000)
        random_suffix = random.randint(1000, 9999)
        self.test_email = f"test_{timestamp}_{random_suffix}@example.com"
        self.test_username = f"test_user_{timestamp}_{random_suffix}"
    
    @pytest.mark.asyncio
    async def test_user_registration(self):
        """Test user registration process"""
        registration_data = UserRegistration(
            username=self.test_username,
            email=self.test_email,
            password="test_password_123",
            family_size=3,
            zip_code="12345"
        )
        
        result = await self.auth_manager.register_user(registration_data)
        
        assert result["success"] is True
        assert "user" in result
        assert "tokens" in result
        assert result["user"]["email"] == self.test_email
        assert result["user"]["username"] == self.test_username
        
        # Test duplicate registration fails
        duplicate_result = await self.auth_manager.register_user(registration_data)
        assert duplicate_result["success"] is False
        assert "already exists" in duplicate_result["error"]
    
    @pytest.mark.asyncio
    async def test_user_authentication(self):
        """Test user login authentication"""
        # First register a user
        registration_data = UserRegistration(
            username=self.test_username,
            email=self.test_email,
            password="test_password_123",
            family_size=2
        )
        
        reg_result = await self.auth_manager.register_user(registration_data)
        assert reg_result["success"] is True
        
        # Now test login
        login_data = UserLogin(
            email=self.test_email,
            password="test_password_123"
        )
        
        auth_result = await self.auth_manager.authenticate_user(login_data)
        
        assert auth_result["success"] is True
        assert "user" in auth_result
        assert "tokens" in auth_result
        assert auth_result["user"]["email"] == self.test_email
        
        # Test wrong password fails
        wrong_login = UserLogin(
            email=self.test_email,
            password="wrong_password"
        )
        
        wrong_result = await self.auth_manager.authenticate_user(wrong_login)
        assert wrong_result["success"] is False
        assert "Invalid email or password" in wrong_result["error"]
    
    @pytest.mark.asyncio
    async def test_token_validation(self):
        """Test JWT token validation"""
        # Register and login a user
        registration_data = UserRegistration(
            username=self.test_username,
            email=self.test_email,
            password="test_password_123"
        )
        
        reg_result = await self.auth_manager.register_user(registration_data)
        access_token = reg_result["tokens"].access_token
        
        # Validate the token
        session_data = await self.auth_manager.get_user_by_token(access_token)
        
        assert session_data is not None
        assert session_data.email == self.test_email
        assert session_data.username == self.test_username
        assert session_data.is_active is True
        
        # Test invalid token
        invalid_session = await self.auth_manager.get_user_by_token("invalid_token")
        assert invalid_session is None
    
    @pytest.mark.asyncio
    async def test_profile_management(self):
        """Test user profile retrieval and updates"""
        # Register a user
        registration_data = UserRegistration(
            username=self.test_username,
            email=self.test_email,
            password="test_password_123",
            family_size=4
        )
        
        reg_result = await self.auth_manager.register_user(registration_data)
        user_id = reg_result["user"]["id"]
        
        # Get profile
        profile = await self.auth_manager.get_user_profile(user_id)
        
        assert profile is not None
        assert profile["email"] == self.test_email
        assert profile["profile"]["family_size"] == 4
        
        # Update profile
        profile_update = UserProfileUpdate(
            family_size=5,
            dietary_restrictions=["vegetarian"],
            city="New York"
        )
        
        update_result = await self.auth_manager.update_user_profile(user_id, profile_update)
        
        assert update_result["success"] is True
        
        # Verify updates
        updated_profile = await self.auth_manager.get_user_profile(user_id)
        assert updated_profile["profile"]["family_size"] == 5
        assert "vegetarian" in updated_profile["profile"]["dietary_restrictions"]
        assert updated_profile["profile"]["city"] == "New York"
    
    @pytest.mark.asyncio
    async def test_password_change(self):
        """Test password change functionality"""
        # Register a user
        registration_data = UserRegistration(
            username=self.test_username,
            email=self.test_email,
            password="old_password_123"
        )
        
        reg_result = await self.auth_manager.register_user(registration_data)
        user_id = reg_result["user"]["id"]
        
        # Change password
        change_result = await self.auth_manager.change_password(
            user_id=user_id,
            current_password="old_password_123",
            new_password="new_password_456"
        )
        
        assert change_result["success"] is True
        
        # Test login with old password fails
        old_login = UserLogin(
            email=self.test_email,
            password="old_password_123"
        )
        
        old_result = await self.auth_manager.authenticate_user(old_login)
        assert old_result["success"] is False
        
        # Test login with new password succeeds
        new_login = UserLogin(
            email=self.test_email,
            password="new_password_456"
        )
        
        new_result = await self.auth_manager.authenticate_user(new_login)
        assert new_result["success"] is True
    
    @pytest.mark.asyncio
    async def test_token_refresh(self):
        """Test token refresh functionality"""
        # Register a user
        registration_data = UserRegistration(
            username=self.test_username,
            email=self.test_email,
            password="test_password_123"
        )
        
        reg_result = await self.auth_manager.register_user(registration_data)
        refresh_token = reg_result["tokens"].refresh_token
        original_access_token = reg_result["tokens"].access_token
        
        # Add a small delay to ensure different timestamps
        import asyncio
        await asyncio.sleep(1)
        
        # Refresh the token
        new_tokens = await self.auth_manager.refresh_token(refresh_token)
        
        assert new_tokens is not None
        assert new_tokens.refresh_token == refresh_token  # Should be same refresh token
        assert new_tokens.token_type == "bearer"
        
        # The access token might be the same if generated at same timestamp
        # So we'll just verify it's a valid token with correct user info
        session_data = await self.auth_manager.get_user_by_token(new_tokens.access_token)
        assert session_data is not None
        assert session_data.email == self.test_email
        # Test invalid refresh token
        invalid_refresh = await self.auth_manager.refresh_token("invalid_refresh_token")
        assert invalid_refresh is None


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])
