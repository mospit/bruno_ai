#!/usr/bin/env python3
"""
Bruno AI V3 Server Startup Script
Handles server initialization, logging setup, health checks, and graceful shutdown
"""

import asyncio
import logging
import os
import signal
import sys
from pathlib import Path
from typing import Optional

import uvicorn
from dotenv import load_dotenv
import redis
import psycopg2
from psycopg2 import sql

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from main import app


class ServerManager:
    """Manages server startup, health checks, and graceful shutdown"""
    
    def __init__(self):
        self.server: Optional[uvicorn.Server] = None
        self.redis_client: Optional[redis.Redis] = None
        self.postgres_conn: Optional[psycopg2.connection] = None
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging configuration"""
        
        # Create logs directory if it doesn't exist
        logs_dir = Path(__file__).parent / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(logs_dir / "bruno_ai_server.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # Create separate loggers for different components
        logger = logging.getLogger("bruno_ai_server")
        
        # Agent-specific loggers
        agent_logger = logging.getLogger("bruno_ai_agents")
        agent_logger.addHandler(logging.FileHandler(logs_dir / "agents.log"))
        
        # Performance logger
        perf_logger = logging.getLogger("bruno_ai_performance")
        perf_logger.addHandler(logging.FileHandler(logs_dir / "performance.log"))
        
        # Error logger
        error_logger = logging.getLogger("bruno_ai_errors")
        error_logger.addHandler(logging.FileHandler(logs_dir / "errors.log"))
        
        return logger
    
    def load_environment(self) -> bool:
        """Load environment variables and validate configuration"""
        
        try:
            # Load .env file
            env_file = Path(__file__).parent / ".env"
            if env_file.exists():
                load_dotenv(env_file)
                self.logger.info("Loaded environment variables from .env file")
            else:
                self.logger.warning("No .env file found, using system environment variables")
            
            # Validate required environment variables
            required_vars = [
                "ANTHROPIC_API_KEY",
                "REDIS_URL",
                "POSTGRES_URL",
                "SERVER_HOST",
                "SERVER_PORT"
            ]
            
            missing_vars = []
            for var in required_vars:
                if not os.getenv(var):
                    missing_vars.append(var)
            
            if missing_vars:
                self.logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
                return False
            
            self.logger.info("Environment configuration validated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load environment: {e}")
            return False
    
    async def check_dependencies(self) -> bool:
        """Check if all external dependencies are available"""
        
        try:
            # Check Redis connection
            redis_url = os.getenv("REDIS_URL")
            self.redis_client = redis.from_url(redis_url)
            await asyncio.to_thread(self.redis_client.ping)
            self.logger.info("Redis connection verified")
            
            # Check PostgreSQL connection
            postgres_url = os.getenv("POSTGRES_URL")
            self.postgres_conn = psycopg2.connect(postgres_url)
            with self.postgres_conn.cursor() as cursor:
                cursor.execute("SELECT 1")
            self.logger.info("PostgreSQL connection verified")
            
            # Check Anthropic API key (basic validation)
            anthropic_key = os.getenv("ANTHROPIC_API_KEY")
            if not anthropic_key.startswith("sk-"):
                self.logger.warning("Anthropic API key format seems invalid")
            
            return True
            
        except redis.ConnectionError as e:
            self.logger.error(f"Redis connection failed: {e}")
            return False
        except psycopg2.Error as e:
            self.logger.error(f"PostgreSQL connection failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Dependency check failed: {e}")
            return False
    
    async def initialize_database(self) -> bool:
        """Initialize database tables if they don't exist"""
        
        try:
            with self.postgres_conn.cursor() as cursor:
                # Create agent memory table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS agent_memory (
                        id SERIAL PRIMARY KEY,
                        agent_id VARCHAR(100) NOT NULL,
                        session_id VARCHAR(100),
                        memory_type VARCHAR(50) NOT NULL,
                        content JSONB NOT NULL,
                        metadata JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create performance metrics table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        id SERIAL PRIMARY KEY,
                        agent_id VARCHAR(100) NOT NULL,
                        endpoint VARCHAR(100) NOT NULL,
                        response_time FLOAT NOT NULL,
                        token_usage INTEGER,
                        status_code INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create user feedback table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_feedback (
                        id SERIAL PRIMARY KEY,
                        session_id VARCHAR(100) NOT NULL,
                        agent_id VARCHAR(100) NOT NULL,
                        rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                        feedback_text TEXT,
                        feedback_type VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                self.postgres_conn.commit()
                self.logger.info("Database tables initialized successfully")
                return True
                
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            return False
    
    def setup_signal_handlers(self):
        """Setup graceful shutdown signal handlers"""
        
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def shutdown(self):
        """Graceful shutdown procedure"""
        
        self.logger.info("Starting graceful shutdown...")
        
        # Stop the server
        if self.server:
            self.server.should_exit = True
            self.logger.info("Server shutdown initiated")
        
        # Close database connections
        if self.postgres_conn:
            self.postgres_conn.close()
            self.logger.info("PostgreSQL connection closed")
        
        if self.redis_client:
            await asyncio.to_thread(self.redis_client.close)
            self.logger.info("Redis connection closed")
        
        self.logger.info("Graceful shutdown completed")
        sys.exit(0)
    
    async def start_server(self):
        """Start the Bruno AI V3 server"""
        
        try:
            # Load environment
            if not self.load_environment():
                sys.exit(1)
            
            # Check dependencies
            if not await self.check_dependencies():
                sys.exit(1)
            
            # Initialize database
            if not await self.initialize_database():
                sys.exit(1)
            
            # Setup signal handlers
            self.setup_signal_handlers()
            
            # Server configuration
            host = os.getenv("SERVER_HOST", "0.0.0.0")
            port = int(os.getenv("SERVER_PORT", "8000"))
            log_level = os.getenv("LOG_LEVEL", "info").lower()
            
            self.logger.info(f"Starting Bruno AI V3 server on {host}:{port}")
            
            # Create server configuration
            config = uvicorn.Config(
                app,
                host=host,
                port=port,
                log_level=log_level,
                access_log=True,
                reload=False,  # Disable reload in production
                workers=1,  # Single worker for now
            )
            
            # Start server
            self.server = uvicorn.Server(config)
            await self.server.serve()
            
        except Exception as e:
            self.logger.error(f"Server startup failed: {e}")
            sys.exit(1)


async def main():
    """Main entry point"""
    
    server_manager = ServerManager()
    await server_manager.start_server()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
