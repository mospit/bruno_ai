# Bruno AI V2.0 Agent Test Suite

Comprehensive test suite for the optimized Bruno AI multi-agent system, providing thorough coverage of all agent components and their interactions.

## Overview

This test suite covers:
- **Budget Analyst Agent V2.0** - Financial analysis and predictive budget optimization
- **Bruno Master Agent V2.0** - Intelligent orchestration and coordination
- **Instacart Integration Agent V2.0** - Direct API integration for grocery data and ordering  
- **A2A Gateway V2.0** - Inter-agent communication and load balancing
- **Base Agent Framework** - Common functionality and caching

## Test Structure

```
tests/
├── test_budget_analyst_agent_v2.py    # Budget agent unit tests
├── test_bruno_master_agent.py         # Master agent orchestration tests
├── test_instacart_integration_agent.py # Instacart agent API tests
├── test_a2a_gateway.py                # Gateway routing and management tests
├── run_tests.py                       # Test runner script
├── pytest.ini                        # Test configuration
├── requirements-test.txt              # Test dependencies
└── README.md                          # This file
```

## Quick Start

### 1. Install Test Dependencies

```bash
# Install test requirements
pip install -r requirements-test.txt

# Or use the test runner to auto-install
python run_tests.py --install-deps
```

### 2. Run All Tests

```bash
# Run all tests
python run_tests.py

# Or use pytest directly
pytest
```

### 3. Run Specific Agent Tests

```bash
# Budget Analyst Agent tests
python run_tests.py --type budget_agent

# Master Agent tests  
python run_tests.py --type master_agent

# Instacart Integration Agent tests
python run_tests.py --type instacart_agent

# A2A Gateway tests
python run_tests.py --type gateway
```

## Test Types and Coverage

### Budget Analyst Agent V2.0 Tests
- ✅ Agent initialization and configuration
- ✅ Budget requirement analysis 
- ✅ Spending pattern analysis
- ✅ Future spending predictions with ML
- ✅ Budget allocation optimization
- ✅ USDA guideline comparisons
- ✅ Error handling and edge cases
- ✅ Caching and performance

**Coverage**: Comprehensive unit tests for all financial analysis capabilities

### Bruno Master Agent V2.0 Tests  
- ✅ Agent orchestration workflows
- ✅ Meal planning coordination
- ✅ Budget coaching functionality
- ✅ Real-time meal plan adaptation
- ✅ Instacart shopping experience creation
- ✅ Agent delegation and communication
- ✅ User preference learning
- ✅ Error handling and fallbacks

**Coverage**: Full orchestration workflow testing with mocked agent interactions

### Instacart Integration Agent V2.0 Tests
- ✅ Product search optimization
- ✅ Shopping list creation and optimization
- ✅ Deal monitoring and price tracking
- ✅ Order lifecycle management
- ✅ Store selection optimization
- ✅ Rate limiting and API error handling
- ✅ Multi-store price comparison
- ✅ Caching strategies

**Coverage**: Complete API integration testing with comprehensive mocking

### A2A Gateway V2.0 Tests
- ✅ Agent registration and deregistration
- ✅ Task routing and load balancing
- ✅ Circuit breaker patterns
- ✅ Health check monitoring
- ✅ Rate limiting functionality
- ✅ Metrics collection
- ✅ Concurrent request handling
- ✅ FastAPI endpoint testing

**Coverage**: Full gateway functionality including resilience patterns

## Advanced Testing Options

### Coverage Reports

```bash
# Generate coverage report
python run_tests.py --coverage

# View HTML coverage report
open htmlcov/index.html
```

### Parallel Execution

```bash
# Run tests in parallel for faster execution
python run_tests.py --parallel
```

### Verbose Output

```bash
# Detailed test output
python run_tests.py --verbose
```

### Fast Tests Only

```bash
# Skip slow integration tests
python run_tests.py --type fast
```

## Test Environment Configuration

The test suite automatically configures mock environment variables:

```python
# Environment variables set during testing
PYTHONPATH = "path/to/agents/v2"
GEMINI_API_KEY = "test_gemini_key"
INSTACART_API_KEY = "test_instacart_key" 
INSTACART_AFFILIATE_ID = "test_affiliate"
REDIS_URL = "redis://localhost:6379"
A2A_GATEWAY_URL = "http://localhost:3000"
TESTING = "true"
```

## Key Testing Patterns

### Async Testing
All agent operations are asynchronous and use `pytest-asyncio`:

```python
@pytest.mark.asyncio
async def test_agent_functionality(self, agent):
    result = await agent.execute_task(task)
    assert result["success"] is True
```

### Mocking External Dependencies
External APIs and services are comprehensively mocked:

```python
with patch('httpx.AsyncClient') as mock_client:
    mock_response.json.return_value = {"products": [...]}
    result = await agent.search_products("query")
```

### Agent Communication Testing
Inter-agent communication is tested with realistic message flows:

```python
with patch.object(agent, '_delegate_to_agent') as mock_delegate:
    mock_delegate.return_value = {"analysis": "complete"}
    result = await agent.orchestrate_meal_planning(context)
```

## Performance Testing

### Response Time Verification
Tests include performance assertions:

```python
start_time = datetime.now()
result = await agent.process_task(task)
end_time = datetime.now()
response_time = (end_time - start_time).total_seconds()
assert response_time < 2.0  # Under 2 seconds
```

### Caching Verification
Cache hit/miss ratios are validated:

```python
# First call - cache miss
result1 = await agent.search_products("query")
assert result1["cached"] is False

# Second call - cache hit  
result2 = await agent.search_products("query")
assert result2["cached"] is True
```

## Error Handling Tests

### API Failures
```python
# Test API error handling
mock_response.status_code = 429  # Rate limit
result = await agent.search_products("query")
assert result["success"] is False
assert "fallback_available" in result
```

### Network Issues
```python
# Test network exception handling
mock_client.side_effect = Exception("Network error")
result = await agent.execute_task(task)
assert "error" in result
assert "recommendations" in result
```

## Continuous Integration

The test suite is designed for CI/CD integration:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    cd server/agents/v2/tests
    python run_tests.py --coverage --parallel
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./htmlcov/coverage.xml
```

## Best Practices

### Test Isolation
- Each test uses fresh agent instances
- External dependencies are mocked
- Redis and database connections are isolated

### Realistic Test Data
- Test data mirrors production scenarios
- Budget ranges reflect real user patterns
- Product data includes realistic pricing

### Comprehensive Edge Cases
- Empty input handling
- Invalid parameter validation
- Timeout and retry scenarios
- Rate limiting edge cases

## Troubleshooting

### Common Issues

**Import Errors**
```bash
# Ensure PYTHONPATH is set correctly
export PYTHONPATH=/path/to/bruno_ai/server/agents/v2
```

**Redis Connection**
```bash
# Start Redis locally for integration tests
redis-server
```

**Missing Dependencies**
```bash
# Install all test requirements
pip install -r requirements-test.txt
```

### Debug Mode
```bash
# Run single test with detailed output
pytest -v -s test_budget_analyst_agent_v2.py::TestBudgetAnalystAgentV2::test_analyze_budget_requirements
```

## Contributing

When adding new tests:

1. Follow existing naming conventions
2. Include comprehensive docstrings
3. Mock all external dependencies
4. Test both success and failure scenarios
5. Maintain high coverage standards (>80%)

## Test Metrics

Current test coverage targets:
- **Budget Analyst Agent**: >90% coverage
- **Master Agent**: >85% coverage  
- **Instacart Agent**: >90% coverage
- **A2A Gateway**: >95% coverage
- **Base Agent**: >90% coverage

Execute `python run_tests.py --coverage` to verify current coverage levels.
