"""
Security utilities for Bruno AI authentication
Handles password hashing, JWT tokens, and security validation
"""

import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import os
from cryptography.fernet import Fernet

class PasswordUtils:
    """Utilities for secure password handling"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password with salt using SHA-256"""
        salt = secrets.token_hex(32)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            salt, stored_hash = hashed_password.split(':')
            password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return password_hash == stored_hash
        except ValueError:
            return False
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate a cryptographically secure random token"""
        return secrets.token_urlsafe(length)

class JWTUtils:
    """JWT token management utilities"""
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or os.getenv('JWT_SECRET_KEY', self._generate_key())
        self.algorithm = 'HS256'
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
    
    def _generate_key(self) -> str:
        """Generate a secure key if none provided"""
        return secrets.token_urlsafe(32)
    
    def create_access_token(self, user_id: int, user_email: str, 
                          expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            'user_id': user_id,
            'email': user_email,
            'exp': expire,
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: int, user_email: str) -> str:
        """Create a JWT refresh token"""
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            'user_id': user_id,
            'email': user_email,
            'exp': expire,
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Create new access token from refresh token"""
        payload = self.verify_token(refresh_token)
        
        if not payload or payload.get('type') != 'refresh':
            return None
        
        return self.create_access_token(
            user_id=payload['user_id'],
            user_email=payload['email']
        )

class EncryptionUtils:
    """Data encryption utilities for sensitive user data"""
    
    def __init__(self, encryption_key: str = None):
        if encryption_key:
            try:
                self.key = encryption_key.encode()
                # Test if it's a valid Fernet key
                Fernet(self.key)
            except:
                # If invalid, generate a new key
                self.key = Fernet.generate_key()
        else:
            env_key = os.getenv('ENCRYPTION_KEY')
            if env_key:
                try:
                    # Try to use the environment key
                    self.key = env_key.encode()
                    # Test if it's valid
                    Fernet(self.key)
                except:
                    # If invalid, generate a new key
                    self.key = Fernet.generate_key()
            else:
                self.key = Fernet.generate_key()
        
        self.cipher = Fernet(self.key)
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()

# Global instances
password_utils = PasswordUtils()
jwt_utils = JWTUtils()
encryption_utils = EncryptionUtils()
