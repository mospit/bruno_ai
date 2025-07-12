"""
Simple database connection test for Bruno AI
Tests if PostgreSQL connection works with the configured credentials
"""

import os
import sys
import psycopg2
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_database_connection():
    """Test PostgreSQL connection"""
    
    # Database connection parameters
    db_params = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'database': os.getenv('DB_NAME', 'bruno_db'),
        'user': os.getenv('DB_USER', 'bruno_user'),
        'password': os.getenv('DB_PASSWORD', 'bruno_pass123'),
        'port': os.getenv('DB_PORT', '5432')
    }
    
    print("🔍 Testing PostgreSQL connection...")
    print(f"Host: {db_params['host']}")
    print(f"Database: {db_params['database']}")
    print(f"User: {db_params['user']}")
    print(f"Port: {db_params['port']}")
    print("-" * 50)
    
    try:
        # Attempt to connect
        print("Connecting to PostgreSQL...")
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Connection successful!")
        print(f"PostgreSQL version: {version}")
        
        # Test database permissions
        cursor.execute("SELECT current_database(), current_user, session_user;")
        db_info = cursor.fetchone()
        print(f"✅ Database: {db_info[0]}")
        print(f"✅ Current user: {db_info[1]}")
        print(f"✅ Session user: {db_info[2]}")
        
        # Test table creation permission
        test_table_sql = """
        CREATE TABLE IF NOT EXISTS test_connection (
            id SERIAL PRIMARY KEY,
            test_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(test_table_sql)
        
        # Insert test data
        cursor.execute("INSERT INTO test_connection (test_message) VALUES (%s);", ("Bruno AI connection test",))
        
        # Read test data
        cursor.execute("SELECT * FROM test_connection ORDER BY id DESC LIMIT 1;")
        test_data = cursor.fetchone()
        print(f"✅ Table operations successful!")
        print(f"Test record: ID={test_data[0]}, Message='{test_data[1]}'")
        
        # Clean up test table
        cursor.execute("DROP TABLE test_connection;")
        
        # Commit and close
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n🎉 Database connection test PASSED!")
        print("Bruno AI is ready to use PostgreSQL!")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ PostgreSQL Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

def load_env_file():
    """Load environment variables from .env file"""
    env_file = project_root / "config" / ".env"
    
    if not env_file.exists():
        print("❌ .env file not found. Please create config/.env file.")
        return False
    
    print(f"📁 Loading environment from: {env_file}")
    
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value
    
    return True

if __name__ == "__main__":
    print("🧠 Bruno AI Database Connection Test")
    print("=" * 50)
    
    # Load environment variables
    if not load_env_file():
        sys.exit(1)
    
    # Test database connection
    success = test_database_connection()
    
    if success:
        print("\n✅ Ready to proceed with Bruno AI initialization!")
        sys.exit(0)
    else:
        print("\n❌ Database connection failed. Please check:")
        print("  1. PostgreSQL is running")
        print("  2. Database credentials are correct")
        print("  3. Database and user exist")
        sys.exit(1)
