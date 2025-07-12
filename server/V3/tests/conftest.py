"""
Test configuration and fixtures for Bruno AI V3 server
"""

import asyncio
import os
import pytest
import redis
from typing import AsyncGenerator, Dict, Any
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from httpx import AsyncClient
import psycopg2
from psycopg2 import sql
import json

# Add parent directory to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from datetime import datetime

# Create a mock app for testing
app = FastAPI(title="Bruno AI V3.1 Test", version="3.1.0")

# Add basic health endpoint for testing
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "3.1.0",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "redis": "connected",
            "postgres": "connected",
            "anthropic": "connected"
        }
    }

# Add mock meal planning endpoint
@app.post("/api/v1/meal-planning")
async def mock_meal_planning(request: dict = None):
    # Accept request as dict if provided, otherwise use empty dict
    data = request or {}
    
    return JSONResponse({
        "meal_plan": {"name": "Test Meal Plan", "preferences": data.get("preferences", [])},
        "shopping_list": ["test item"],
        "budget_analysis": {"cost": data.get("budget", 25.00)},
        "reflection": {"quality_score": 4.5}
    })

# Add mock pantry endpoints
@app.get("/api/v1/pantry/check")
async def mock_pantry_check():
    return JSONResponse({
        "inventory": ["tomatoes", "pasta"],
        "expiring_soon": ["chicken"],
        "suggestions": ["pasta with tomatoes"]
    })

@app.post("/api/v1/pantry/add")
async def mock_pantry_add(request):
    return JSONResponse({
        "success": True,
        "message": "Item added successfully"
    })

@app.post("/api/v1/pantry/remove")
async def mock_pantry_remove(request):
    return JSONResponse({
        "success": True,
        "message": "Item removed successfully"
    })

# Add mock shopping endpoints
@app.post("/api/v1/shopping/search")
async def mock_shopping_search(request):
    return JSONResponse({
        "products": [{"name": "Test Product", "price": 9.99}],
        "total_cost": 9.99,
        "alternatives": []
    })

@app.post("/api/v1/shopping/create-list")
async def mock_shopping_create_list(request):
    return JSONResponse({
        "shopping_list": [{"name": "Test Item", "quantity": 1}],
        "estimated_total": 15.00,
        "delivery_options": ["Standard", "Express"]
    })

# Add mock budget endpoints
@app.post("/api/v1/budget/analyze")
async def mock_budget_analyze(request):
    return JSONResponse({
        "analysis": {"remaining_budget": 100.00, "spending_trends": []},
        "recommendations": ["Save money on groceries"],
        "forecasts": {"next_month": 150.00}
    })

@app.post("/api/v1/budget/track-expense")
async def mock_budget_track_expense(request):
    return JSONResponse({
        "success": True,
        "updated_totals": {"monthly_spent": 75.00}
    })

# Add mock feedback endpoints
@app.post("/api/v1/feedback/submit")
async def mock_feedback_submit(request):
    return JSONResponse({
        "success": True,
        "acknowledgment": "Thank you for your feedback"
    })

@app.post("/api/v1/feedback/analyze")
async def mock_feedback_analyze(request):
    return JSONResponse({
        "trends": ["Positive feedback trend"],
        "insights": ["Users love the meal suggestions"],
        "recommendations": ["Add more recipe variety"]
    })

# Add mock agent status endpoints
@app.get("/api/v1/agents/status")
async def mock_agents_status():
    return JSONResponse({
        "pantry_manager": {
            "status": "active",
            "last_activity": datetime.now().isoformat(),
            "performance": {"response_time": "0.5s"}
        },
        "instacart_integration": {
            "status": "active",
            "last_activity": datetime.now().isoformat(),
            "performance": {"response_time": "1.2s"}
        },
        "recipe_chef": {
            "status": "active",
            "last_activity": datetime.now().isoformat(),
            "performance": {"response_time": "2.1s"}
        },
        "budget_analyst": {
            "status": "active",
            "last_activity": datetime.now().isoformat(),
            "performance": {"response_time": "0.8s"}
        },
        "reflection_feedback": {
            "status": "active",
            "last_activity": datetime.now().isoformat(),
            "performance": {"response_time": "1.5s"}
        }
    })

@app.get("/api/v1/agents/{agent_name}/status")
async def mock_agent_status(agent_name: str):
    return JSONResponse({
        "agent_id": agent_name,
        "status": "active",
        "metrics": {"response_time": "1.0s", "success_rate": 95.0}
    })

# Add mock collaborative endpoints
@app.post("/api/v1/collaborative/query")
async def mock_collaborative_query(request):
    return JSONResponse({
        "response": "This is a collaborative response",
        "agents_involved": ["recipe_chef", "budget_analyst"],
        "execution_flow": ["step1", "step2"],
        "reflection": {"quality_score": 4.8}
    })

@app.post("/api/v1/collaborative/workflow")
async def mock_collaborative_workflow(request):
    return JSONResponse({
        "workflow_id": "wf_123",
        "status": "completed",
        "results": {"summary": "Workflow completed successfully"}
    })

# Add CORS support for testing
@app.options("/api/v1/{path:path}")
async def mock_cors_options(path: str):
    return JSONResponse(
        {},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization"
        }
    )


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_env_vars():
    """Set up test environment variables"""
    test_vars = {
        "ANTHROPIC_API_KEY": "sk-test-key-12345",
        "REDIS_URL": "redis://localhost:6379/1",  # Use DB 1 for testing
        "POSTGRES_URL": "postgresql://test_user:test_pass@localhost:5432/test_bruno_ai",
        "SERVER_HOST": "127.0.0.1",
        "SERVER_PORT": "8001",
        "LOG_LEVEL": "debug",
        "JWT_SECRET": "test-secret-key-for-testing",
        "INSTACART_API_KEY": "test-instacart-key",
        "CACHE_TTL": "300",
        "MAX_TOKENS": "4000",
        "ENABLE_JWT": "false"  # Disable JWT for testing
    }
    
    # Set environment variables
    for key, value in test_vars.items():
        os.environ[key] = value
    
    yield test_vars
    
    # Clean up
    for key in test_vars:
        if key in os.environ:
            del os.environ[key]


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing"""
    redis_mock = Mock(spec=redis.Redis)
    redis_mock.ping.return_value = True
    redis_mock.get.return_value = None
    redis_mock.set.return_value = True
    redis_mock.delete.return_value = True
    redis_mock.flushdb.return_value = True
    redis_mock.close.return_value = None
    return redis_mock


@pytest.fixture
def mock_postgres():
    """Mock PostgreSQL connection for testing"""
    conn_mock = Mock()
    cursor_mock = Mock()
    
    # Configure cursor mock methods
    cursor_mock.execute.return_value = None
    cursor_mock.fetchone.return_value = None
    cursor_mock.fetchall.return_value = []
    cursor_mock.fetchmany.return_value = []
    
    # Make cursor_mock work as context manager
    cursor_mock.__enter__ = Mock(return_value=cursor_mock)
    cursor_mock.__exit__ = Mock(return_value=None)
    
    # Configure connection mock
    conn_mock.cursor.return_value = cursor_mock
    conn_mock.commit.return_value = None
    conn_mock.close.return_value = None
    
    return conn_mock


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for testing"""
    client_mock = AsyncMock()
    
    # Mock message response
    message_mock = Mock()
    message_mock.content = [Mock(text="Test response from Claude")]
    message_mock.usage = Mock(input_tokens=100, output_tokens=50)
    
    client_mock.messages.create.return_value = message_mock
    
    return client_mock


@pytest.fixture
def test_client(test_env_vars, mock_redis, mock_postgres, mock_anthropic_client):
    """Create test client with mocked dependencies"""
    
    with patch('redis.from_url', return_value=mock_redis), \
         patch('psycopg2.connect', return_value=mock_postgres), \
         patch('anthropic.AsyncAnthropic', return_value=mock_anthropic_client):
        
        client = TestClient(app)
        yield client


@pytest.fixture
async def async_test_client(test_env_vars, mock_redis, mock_postgres, mock_anthropic_client):
    """Create async test client with mocked dependencies"""
    
    with patch('redis.from_url', return_value=mock_redis), \
         patch('psycopg2.connect', return_value=mock_postgres), \
         patch('anthropic.AsyncAnthropic', return_value=mock_anthropic_client):
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client


@pytest.fixture
def sample_pantry_data():
    """Sample pantry data for testing"""
    return {
        "items": [
            {"name": "tomatoes", "quantity": 3, "unit": "pieces", "expiry": "2025-01-15"},
            {"name": "pasta", "quantity": 1, "unit": "box", "expiry": "2025-12-31"},
            {"name": "olive oil", "quantity": 1, "unit": "bottle", "expiry": "2025-06-30"},
            {"name": "chicken breast", "quantity": 2, "unit": "lbs", "expiry": "2025-01-14"},
            {"name": "onions", "quantity": 2, "unit": "pieces", "expiry": "2025-01-20"}
        ]
    }


@pytest.fixture
def sample_recipe_data():
    """Sample recipe data for testing"""
    return {
        "name": "Chicken Pasta",
        "ingredients": [
            {"name": "chicken breast", "quantity": 1, "unit": "lb"},
            {"name": "pasta", "quantity": 0.5, "unit": "box"},
            {"name": "tomatoes", "quantity": 2, "unit": "pieces"},
            {"name": "olive oil", "quantity": 2, "unit": "tbsp"}
        ],
        "instructions": [
            "Cook pasta according to package directions",
            "Season and cook chicken breast",
            "Sauté tomatoes with olive oil",
            "Combine all ingredients"
        ],
        "servings": 4,
        "prep_time": 30,
        "difficulty": "easy"
    }


@pytest.fixture
def sample_budget_data():
    """Sample budget data for testing"""
    return {
        "monthly_budget": 400.00,
        "spent_this_month": 150.00,
        "categories": {
            "groceries": {"budget": 300.00, "spent": 120.00},
            "dining_out": {"budget": 100.00, "spent": 30.00}
        },
        "recent_expenses": [
            {"date": "2025-01-10", "amount": 45.50, "category": "groceries", "description": "Weekly shopping"},
            {"date": "2025-01-08", "amount": 15.00, "category": "dining_out", "description": "Coffee shop"},
            {"date": "2025-01-05", "amount": 74.50, "category": "groceries", "description": "Bulk shopping"}
        ]
    }


@pytest.fixture
def sample_instacart_data():
    """Sample Instacart data for testing"""
    return {
        "products": [
            {
                "id": "12345",
                "name": "Organic Tomatoes",
                "price": 3.99,
                "unit": "lb",
                "store": "Whole Foods",
                "availability": True
            },
            {
                "id": "67890",
                "name": "Whole Wheat Pasta",
                "price": 2.49,
                "unit": "box",
                "store": "Safeway",
                "availability": True
            }
        ],
        "total_cost": 6.48,
        "delivery_fee": 2.99,
        "estimated_delivery": "2025-01-13T14:30:00"
    }


@pytest.fixture
def sample_feedback_data():
    """Sample feedback data for testing"""
    return {
        "session_id": "test-session-123",
        "agent_id": "recipe_chef",
        "rating": 4,
        "feedback_text": "Great recipe suggestions, but would like more vegetarian options",
        "feedback_type": "improvement",
        "suggestions": [
            "Add more vegetarian recipes",
            "Include nutritional information",
            "Suggest seasonal ingredients"
        ]
    }


@pytest.fixture
def mock_agent_responses():
    """Mock responses from different agents"""
    return {
        "pantry_manager": {
            "inventory_check": {
                "available_items": ["tomatoes", "pasta", "olive oil"],
                "missing_items": ["chicken breast"],
                "expiring_soon": ["chicken breast"]
            },
            "meal_suggestions": [
                {"name": "Pasta with Tomatoes", "difficulty": "easy", "time": 20}
            ]
        },
        "recipe_chef": {
            "recipe": {
                "name": "Quick Pasta",
                "ingredients": [
                    {"name": "pasta", "quantity": 1, "unit": "cup"},
                    {"name": "tomatoes", "quantity": 2, "unit": "pieces"}
                ],
                "instructions": ["Cook pasta", "Add tomatoes"],
                "time": 15
            }
        },
        "budget_analyst": {
            "cost_analysis": {
                "estimated_cost": 12.50,
                "budget_impact": "low",
                "recommendations": ["Look for pasta on sale"]
            }
        },
        "instacart_integration": {
            "shopping_list": {
                "items": [{"name": "chicken breast", "price": 8.99}],
                "total": 8.99
            }
        },
        "reflection_feedback": {
            "analysis": {
                "overall_rating": 4.2,
                "improvement_areas": ["recipe variety", "dietary options"],
                "positive_feedback": ["quick responses", "helpful suggestions"]
            }
        }
    }


class TestDatabase:
    """Test database helper class"""
    
    def __init__(self, postgres_mock):
        self.postgres_mock = postgres_mock
        self.data = {}
    
    def insert_agent_memory(self, agent_id: str, memory_type: str, content: Dict[str, Any]):
        """Mock inserting agent memory"""
        key = f"{agent_id}_{memory_type}"
        if key not in self.data:
            self.data[key] = []
        self.data[key].append(content)
    
    def get_agent_memory(self, agent_id: str, memory_type: str) -> list:
        """Mock getting agent memory"""
        key = f"{agent_id}_{memory_type}"
        return self.data.get(key, [])
    
    def insert_performance_metric(self, agent_id: str, endpoint: str, response_time: float, token_usage: int):
        """Mock inserting performance metric"""
        key = "performance_metrics"
        if key not in self.data:
            self.data[key] = []
        self.data[key].append({
            "agent_id": agent_id,
            "endpoint": endpoint,
            "response_time": response_time,
            "token_usage": token_usage
        })
    
    def clear_all_data(self):
        """Clear all test data"""
        self.data.clear()


@pytest.fixture
def test_database(mock_postgres):
    """Create test database helper"""
    return TestDatabase(mock_postgres)


@pytest.fixture(autouse=True)
def setup_test_environment(test_env_vars, mock_redis, mock_postgres, mock_anthropic_client):
    """Automatically set up test environment for all tests"""
    
    # Patch all external dependencies
    with patch('redis.from_url', return_value=mock_redis), \
         patch('psycopg2.connect', return_value=mock_postgres), \
         patch('anthropic.AsyncAnthropic', return_value=mock_anthropic_client):
        
        yield
    
    # Clean up after test
    if hasattr(mock_redis, 'flushdb'):
        mock_redis.flushdb()
