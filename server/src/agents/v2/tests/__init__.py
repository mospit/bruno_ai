"""
Bruno AI V2.0 Agent Test Suite

Comprehensive test package for the optimized Bruno AI multi-agent system.

This package contains unit and integration tests for:
- Budget Analyst Agent V2.0
- Bruno Master Agent V2.0  
- Instacart Integration Agent V2.0
- A2A Gateway V2.0
- Base Agent Framework

Usage:
    # Run all tests
    python run_tests.py
    
    # Run specific agent tests
    python run_tests.py --type budget_agent
    
    # Run with coverage
    python run_tests.py --coverage
"""

__version__ = "2.0.0"
__author__ = "Bruno AI Team"

# Test configuration
TEST_CONFIG = {
    "timeout": 30,  # Default test timeout in seconds
    "retry_attempts": 3,
    "mock_external_apis": True,
    "enable_caching_tests": True,
    "performance_thresholds": {
        "agent_response_time": 2.0,  # seconds
        "gateway_routing_time": 0.5,  # seconds
        "cache_access_time": 0.1      # seconds
    }
}

# Test markers for pytest
PYTEST_MARKERS = {
    "unit": "Unit tests for individual components",
    "integration": "Integration tests for agent interactions", 
    "slow": "Tests that take longer than 5 seconds",
    "mock": "Tests that use extensive mocking",
    "performance": "Performance and timing tests"
}
