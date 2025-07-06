"""
Debug Auth Registration Issue
Test database connection and registration process
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path and load environment
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

env_file = project_root / "config" / ".env"
load_dotenv(env_file)

from src.auth.auth_manager import AuthManager
from src.auth.models import UserRegistration
from src.database.connection import database_manager

async def debug_registration():
    """Debug registration process step by step"""
    print("🔍 Debugging Registration Process")
    
    # Test database connection
    print("\n1. Testing database connection...")
    try:
        session = database_manager.get_session()
        print("✅ Database connection successful")
        session.close()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return
    
    # Test auth manager creation
    print("\n2. Creating auth manager...")
    try:
        auth_manager = AuthManager()
        print("✅ Auth manager created successfully")
    except Exception as e:
        print(f"❌ Auth manager creation failed: {e}")
        return
    
    # Test user registration
    print("\n3. Testing user registration...")
    try:
        import time
        test_username = f"debug_user_{int(time.time())}"
        test_email = f"debug_{int(time.time())}@example.com"
        
        registration_data = UserRegistration(
            username=test_username,
            email=test_email,
            password="debug_password_123",
            family_size=2
        )
        
        print(f"   Username: {test_username}")
        print(f"   Email: {test_email}")
        
        result = await auth_manager.register_user(registration_data)
        print(f"   Registration result: {result}")
        
        if result.get("success"):
            print("✅ Registration successful!")
            print(f"   User ID: {result['user']['id']}")
            print(f"   Has tokens: {'tokens' in result}")
        else:
            print(f"❌ Registration failed: {result.get('error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Registration error: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    asyncio.run(debug_registration())
