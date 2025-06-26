#!/usr/bin/env python3
"""
Bruno AI Agent Ecosystem - Main Server Entry Point

This module serves as the main entry point for the Bruno AI multi-agent system.
It initializes all agents, sets up the A2A server, and provides the REST API
for client applications to interact with the agent ecosystem.

Usage:
    python main.py [--host HOST] [--port PORT] [--debug]
    
Environment Variables:
    OPENAI_API_KEY: Required for AI agent functionality
    INSTACART_API_KEY: Required for Instacart integration
    BRUNO_MAX_BUDGET: Maximum budget per user session (default: 150.0)
    BRUNO_DEFAULT_FAMILY_SIZE: Default family size for meal planning (default: 4)
    BRUNO_DEBUG: Enable debug mode (default: False)
"""

import os
import sys
import asyncio
import argparse
import logging
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from a2a_server import BrunoAIServer, ServerConfig
from bruno_master_agent import BrunoMasterAgent
from grocery_browser_agent import GroceryBrowserAgent
from recipe_chef_agent import RecipeChefAgent
from instacart_api_agent import InstacartAPIAgent, InstacartConfig


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bruno_ai.log')
    ]
)
logger = logging.getLogger(__name__)


def load_environment_config() -> ServerConfig:
    """
    Load configuration from environment variables.
    
    Returns:
        ServerConfig: Configuration object with environment values
        
    Raises:
        ValueError: If required environment variables are missing
    """
    # Primary API key for Google Gemini models
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if not gemini_api_key:
        logger.warning(
            "GEMINI_API_KEY not found. Agents may not function properly without it."
        )
    
    # Optional OpenAI API key (legacy support)
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        logger.info("OPENAI_API_KEY not provided - using Google Gemini models")
    
    instacart_api_key = os.getenv('INSTACART_API_KEY')
    if not instacart_api_key:
        logger.warning(
            "INSTACART_API_KEY not found. Instacart integration will use demo data."
        )
        instacart_api_key = "demo_key"
    
    # Optional configuration with defaults
    max_budget = float(os.getenv('BRUNO_MAX_BUDGET', '150.0'))
    default_family_size = int(os.getenv('BRUNO_DEFAULT_FAMILY_SIZE', '4'))
    debug = os.getenv('BRUNO_DEBUG', 'false').lower() in ('true', '1', 'yes')
    host = os.getenv('BRUNO_HOST', 'localhost')
    port = int(os.getenv('BRUNO_PORT', '8000'))
    
    return ServerConfig(
        host=host,
        port=port,
        debug=debug,
        gemini_api_key=gemini_api_key,
        openai_api_key=openai_api_key,
        instacart_api_key=instacart_api_key,
        max_budget=max_budget,
        default_family_size=default_family_size
    )


def setup_cors_middleware(app: FastAPI) -> None:
    """
    Setup CORS middleware for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  # React development server
            "http://localhost:8080",  # Vue development server
            "http://localhost:4200",  # Angular development server
            "http://localhost:5000",  # Flutter web development
            "https://bruno-ai.app",   # Production domain (if applicable)
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )


def setup_error_handlers(app: FastAPI) -> None:
    """
    Setup global error handlers for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    @app.exception_handler(ValueError)
    async def value_error_handler(request, exc):
        logger.error(f"ValueError: {exc}")
        return JSONResponse(
            status_code=400,
            content={
                "error": "Invalid request",
                "message": str(exc),
                "type": "validation_error"
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": "An unexpected error occurred. Please try again later.",
                "type": "server_error"
            }
        )


async def create_bruno_ai_server(config: ServerConfig) -> BrunoAIServer:
    """
    Create and initialize the Bruno AI server with all agents.
    
    Args:
        config: Server configuration
        
    Returns:
        BrunoAIServer: Initialized server instance
    """
    logger.info("Initializing Bruno AI Agent Ecosystem...")
    
    try:
        # Create server instance
        server = BrunoAIServer(config)
        
        # Initialize the server (this sets up all agents)
        await server.initialize()
        
        # Setup middleware and error handlers
        setup_cors_middleware(server.app)
        setup_error_handlers(server.app)
        
        logger.info("Bruno AI server initialized successfully")
        logger.info(f"Available agents: {list(server.agents.keys())}")
        
        return server
        
    except Exception as e:
        logger.error(f"Failed to initialize Bruno AI server: {e}")
        raise


def validate_system_requirements() -> bool:
    """
    Validate that all system requirements are met.
    
    Returns:
        bool: True if all requirements are met
    """
    logger.info("Validating system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        return False
    
    # Check required packages
    required_packages = [
        'fastapi', 'uvicorn', 'openai', 'selenium', 
        'pandas', 'httpx', 'pydantic'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing required packages: {missing_packages}")
        logger.error("Please install them using: pip install -r requirements.txt")
        return False
    
    logger.info("System requirements validation passed")
    return True


def parse_command_line_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Bruno AI Agent Ecosystem Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                          # Run with default settings
  python main.py --host 0.0.0.0 --port 8080 --debug
  python main.py --production             # Run in production mode

Environment Variables:
  OPENAI_API_KEY        OpenAI API key (required)
  INSTACART_API_KEY     Instacart API key (optional, uses demo data if not set)
  BRUNO_MAX_BUDGET      Maximum budget per session (default: 150.0)
  BRUNO_DEFAULT_FAMILY_SIZE  Default family size (default: 4)
  BRUNO_DEBUG           Enable debug mode (default: false)
        """
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default=None,
        help='Host to bind the server to (default: localhost)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=None,
        help='Port to bind the server to (default: 8000)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    
    parser.add_argument(
        '--production',
        action='store_true',
        help='Run in production mode (disables debug, optimizes performance)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--workers',
        type=int,
        default=1,
        help='Number of worker processes (default: 1)'
    )
    
    return parser.parse_args()


def main() -> None:
    """
    Main entry point for the Bruno AI server.
    """
    # Parse command line arguments
    args = parse_command_line_args()
    
    # Set logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Validate system requirements
    if not validate_system_requirements():
        sys.exit(1)
    
    try:
        # Load configuration
        config = load_environment_config()
        
        # Override with command line arguments
        if args.host:
            config.host = args.host
        if args.port:
            config.port = args.port
        if args.debug:
            config.debug = True
        if args.production:
            config.debug = False
        
        # Create and initialize server
        server = asyncio.run(create_bruno_ai_server(config))
        
        # Log startup information
        logger.info(f"Starting Bruno AI server on {config.host}:{config.port}")
        logger.info(f"Debug mode: {config.debug}")
        logger.info(f"Max budget per session: ${config.max_budget}")
        logger.info(f"Default family size: {config.default_family_size}")
        
        # Configure uvicorn settings
        uvicorn_config = {
            "app": server.app,
            "host": config.host,
            "port": config.port,
            "log_level": args.log_level.lower(),
            "access_log": config.debug,
            "reload": config.debug and not args.production,
            "workers": 1 if config.debug else args.workers,
        }
        
        if args.production:
            uvicorn_config.update({
                "reload": False,
                "access_log": False,
                "workers": args.workers,
            })
        
        # Start the server
        logger.info("Bruno AI Agent Ecosystem is ready to serve requests!")
        logger.info("API Documentation available at: http://{}:{}/docs".format(config.host, config.port))
        logger.info("Health check available at: http://{}:{}/health".format(config.host, config.port))
        
        # Run the server
        uvicorn.run(**uvicorn_config)
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal, stopping server...")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise  # Re-raise the exception instead of calling sys.exit(1)
    finally:
        logger.info("Bruno AI server shutdown complete")


def run_server() -> None:
    """
    Synchronous entry point for running the server.
    """
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        logger.error("Server will attempt to restart...")
        raise  # Re-raise instead of sys.exit(1) to allow proper error handling


if __name__ == "__main__":
    # Print banner
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                    Bruno AI Agent Ecosystem                  ║
    ║                                                              ║
    ║  Multi-Agent System for Intelligent Meal Planning           ║
    ║  and Grocery Shopping Assistance                             ║
    ║                                                              ║
    ║  Powered by Google A2A Protocol & OpenAI                    ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Run the server
    run_server()