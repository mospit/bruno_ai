"""
Simple PostgreSQL setup script for Bruno AI
Creates database and user using existing postgres credentials
"""

import psycopg2
import sys
import getpass
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def test_postgres_connection(password):
    """Test connection with postgres user"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            user='postgres',
            password=password,
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn
    except psycopg2.Error as e:
        return None

def create_bruno_database_and_user(conn, postgres_password):
    """Create Bruno database and user"""
    cursor = conn.cursor()
    
    try:
        print("📝 Creating Bruno database and user...")
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'bruno_db'")
        if not cursor.fetchone():
            cursor.execute("CREATE DATABASE bruno_db")
            print("✅ Created database: bruno_db")
        else:
            print("ℹ️ Database bruno_db already exists")
        
        # Check if user exists
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = 'bruno_user'")
        if not cursor.fetchone():
            cursor.execute("CREATE USER bruno_user WITH PASSWORD 'bruno_pass123'")
            print("✅ Created user: bruno_user")
        else:
            print("ℹ️ User bruno_user already exists")
            # Update password just in case
            cursor.execute("ALTER USER bruno_user PASSWORD 'bruno_pass123'")
            print("✅ Updated bruno_user password")
        
        # Grant privileges
        cursor.execute("GRANT ALL PRIVILEGES ON DATABASE bruno_db TO bruno_user")
        print("✅ Granted database privileges to bruno_user")
        
        # Connect to bruno_db to grant schema privileges
        cursor.close()
        conn.close()
        
        # Connect to bruno_db
        bruno_conn = psycopg2.connect(
            host='localhost',
            port='5432',
            user='postgres',
            password=postgres_password,
            database='bruno_db'
        )
        bruno_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        bruno_cursor = bruno_conn.cursor()
        
        # Grant schema privileges
        bruno_cursor.execute("GRANT ALL ON SCHEMA public TO bruno_user")
        bruno_cursor.execute("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO bruno_user")
        bruno_cursor.execute("GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO bruno_user")
        bruno_cursor.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO bruno_user")
        bruno_cursor.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO bruno_user")
        
        print("✅ Granted schema privileges to bruno_user")
        
        bruno_cursor.close()
        bruno_conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Database setup error: {e}")
        return False

def test_bruno_connection():
    """Test connection with bruno_user"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            user='bruno_user',
            password='bruno_pass123',
            database='bruno_db'
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print("✅ Bruno user connection successful!")
        print(f"PostgreSQL version: {version}")
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Bruno user connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🐻 Bruno AI PostgreSQL Setup")
    print("=" * 50)
    
    # Try common passwords first
    common_passwords = ['', 'postgres', 'admin', 'password', '123456']
    postgres_password = None
    postgres_conn = None
    
    print("🔍 Testing common PostgreSQL passwords...")
    for pwd in common_passwords:
        print(f"Trying password: {'(empty)' if pwd == '' else pwd}")
        conn = test_postgres_connection(pwd)
        if conn:
            postgres_password = pwd
            postgres_conn = conn
            print(f"✅ Connected with password: {'(empty)' if pwd == '' else pwd}")
            break
    
    if not postgres_conn:
        print("\n🔐 Common passwords didn't work. Please enter postgres password:")
        while not postgres_conn:
            postgres_password = getpass.getpass("PostgreSQL postgres user password: ")
            postgres_conn = test_postgres_connection(postgres_password)
            if not postgres_conn:
                print("❌ Invalid password. Try again.")
    
    print(f"\n🎉 Connected to PostgreSQL successfully!")
    
    # Create Bruno database and user
    if create_bruno_database_and_user(postgres_conn, postgres_password):
        print("\n🧪 Testing Bruno user connection...")
        if test_bruno_connection():
            print("\n" + "=" * 50)
            print("🎉 Bruno AI database setup completed successfully!")
            print("\nDatabase credentials:")
            print("  Host: localhost")
            print("  Database: bruno_db")
            print("  User: bruno_user")
            print("  Password: bruno_pass123")
            print("  Port: 5432")
            print("\n✅ Ready to initialize Bruno AI!")
        else:
            print("\n❌ Setup completed but connection test failed")
            sys.exit(1)
    else:
        print("\n❌ Database setup failed")
        sys.exit(1)
