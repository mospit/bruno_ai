"""
Database initialization script for Bruno AI
Sets up database tables and creates initial data
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
env_file = project_root / "config" / ".env"
if env_file.exists():
    load_dotenv(env_file)
else:
    print(f"Warning: .env file not found at {env_file}")

from src.database.connection import database_manager
from src.database.models import Base
from src.auth.auth_manager import auth_manager
from src.auth.models import UserRegistration
from loguru import logger

async def init_database():
    """Initialize the database with tables and sample data"""
    
    try:
        logger.info("Starting database initialization...")
        
        # Create all tables
        logger.info("Creating database tables...")
        database_manager.create_tables()
        logger.info("Database tables created successfully!")
        
        # Create a sample user for testing
        logger.info("Creating sample user...")
        sample_user = UserRegistration(
            username="demo_user",
            email="demo@brunoai.com",
            password="demo123",
            family_size=4,
            zip_code="10001"
        )
        
        result = await auth_manager.register_user(sample_user)
        if result['success']:
            logger.info(f"Sample user created: {result['user']['email']}")
        else:
            logger.warning(f"Sample user creation failed: {result.get('error')}")
        
        logger.info("Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

async def reset_database():
    """Reset the database by dropping and recreating all tables"""
    
    try:
        logger.warning("Resetting database - THIS WILL DELETE ALL DATA!")
        
        # Drop all tables
        logger.info("Dropping existing tables...")
        database_manager.drop_tables()
        
        # Recreate tables
        logger.info("Recreating tables...")
        database_manager.create_tables()
        
        logger.info("Database reset completed successfully!")
        
    except Exception as e:
        logger.error(f"Database reset failed: {e}")
        raise

def check_environment():
    """Check if required environment variables are set"""
    
    required_vars = [
        'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_NAME',
        'JWT_SECRET_KEY', 'GEMINI_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Please set these variables in your .env file")
        return False
    
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Bruno AI Database Management")
    parser.add_argument('--reset', action='store_true', 
                       help='Reset database (WARNING: deletes all data)')
    parser.add_argument('--check-env', action='store_true',
                       help='Check environment variables')
    
    args = parser.parse_args()
    
    if args.check_env:
        if check_environment():
            logger.info("All required environment variables are set!")
        sys.exit(0)
    
    if not check_environment():
        sys.exit(1)
    
    if args.reset:
        asyncio.run(reset_database())
    else:
        asyncio.run(init_database())
