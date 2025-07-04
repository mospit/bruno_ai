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
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from a2a_server import BrunoAIServer, ServerConfig
from bruno_master_agent import BrunoMasterAgent
from grocery_browser_agent import GroceryBrowserAgent
from recipe_chef_agent import RecipeChefAgent
from instacart_api_agent import InstacartAPIAgent, InstacartConfig

# API Models
class ProductSearchRequest(BaseModel):
    """Request model for product search."""
    query: str
    max_results: int = 20
    sort_by: str = "relevance"
    category: Optional[str] = None

class ProductSearchResponse(BaseModel):
    """Response model for product search."""
    success: bool
    products: list
    total_results: int
    query: str
    filters: dict
    error: Optional[str] = None

# Global Instacart API agent instance
_instacart_agent: Optional[InstacartAPIAgent] = None

def setup_instacart_routes(app: FastAPI) -> None:
    """
    Setup Instacart API routes for product search and ordering.
    
    Args:
        app: FastAPI application instance
    """
    global _instacart_agent
    
    # Initialize Instacart agent if not already done
    if _instacart_agent is None:
        instacart_config = InstacartConfig(
            api_key=os.getenv('INSTACART_API_KEY', 'demo_key')
        )
        _instacart_agent = InstacartAPIAgent(instacart_config)
    
    @app.post("/api/v1/agents/instacart/search", response_model=ProductSearchResponse)
    async def search_products(request: ProductSearchRequest):
        """
        Search for products using the Instacart API.
        
        Args:
            request: Product search request with query and filters
            
        Returns:
            ProductSearchResponse: Search results with products and metadata
        """
        try:
            logger.info(f"Searching for products: '{request.query}'")
            
            # Use the Instacart agent's search functionality
            search_tool = _instacart_agent._search_products_tool()
            search_results = await search_tool.func(
                query=request.query,
                store_id=None,  # Search across all stores
                category=request.category,
                max_results=request.max_results,
                sort_by=request.sort_by
            )
            
            if search_results.get('success', False):
                return ProductSearchResponse(
                    success=True,
                    products=search_results['products'],
                    total_results=search_results['total_results'],
                    query=request.query,
                    filters=search_results['filters']
                )
            else:
                error_message = search_results.get('error', 'Unknown search error')
                logger.error(f"Product search failed: {error_message}")
                return ProductSearchResponse(
                    success=False,
                    products=[],
                    total_results=0,
                    query=request.query,
                    filters={},
                    error=error_message
                )
                
        except Exception as e:
            logger.error(f"Error in product search: {e}")
            return ProductSearchResponse(
                success=False,
                products=[],
                total_results=0,
                query=request.query,
                filters={},
                error=str(e)
            )
    
    @app.get("/api/v1/agents/instacart/stores")
    async def get_stores(zip_code: str = "90210", radius_miles: float = 10.0):
        """
        Get available stores near a location.
        
        Args:
            zip_code: ZIP code to search near
            radius_miles: Search radius in miles
            
        Returns:
            List of available stores with delivery information
        """
        try:
            stores_tool = _instacart_agent._find_stores_tool()
            stores_results = await stores_tool.func(
                zip_code=zip_code,
                radius_miles=radius_miles,
                delivery_only=True
            )
            
            return stores_results
            
        except Exception as e:
            logger.error(f"Error getting stores: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v1/agents/instacart/deals")
    async def get_weekly_deals(store_id: Optional[str] = None, category: Optional[str] = None):
        """
        Get current weekly deals and promotions.
        
        Args:
            store_id: Specific store to get deals for (optional)
            category: Product category filter (optional)
            
        Returns:
            List of current deals and promotions
        """
        try:
            deals_tool = _instacart_agent._get_weekly_deals_tool()
            deals_results = await deals_tool.func(
                store_id=store_id,
                category=category
            )
            
            return deals_results
            
        except Exception as e:
            logger.error(f"Error getting deals: {e}")
            raise HTTPException(status_code=500, detail=str(e))


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
        
        # Add Instacart API routes
        setup_instacart_routes(server.app)
        
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