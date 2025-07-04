# Bruno AI Server Test Suite

Comprehensive testing framework for the Bruno AI multi-agent ecosystem server, ensuring production readiness, stability, and performance.

## 📋 Test Suite Overview

The Bruno AI server test suite consists of four main categories:

### 🔧 **Stability Tests** (`test_server_stability.py`)
**Critical for Production** ✅

Validates core server functionality and production readiness:
- Health endpoint reliability
- API documentation accessibility
- Error handling and recovery
- Request validation and security
- CORS configuration
- Async operations stability
- Environment variable handling
- Logging configuration
- Memory leak detection
- Timeout handling

### ⚡ **Load & Performance Tests** (`test_load_performance.py`)
**Performance Validation** 🟡

Evaluates server performance under various load conditions:
- Concurrent request handling
- Response time consistency
- Throughput measurement
- Memory usage monitoring
- Burst traffic handling
- Sustained load testing
- Error rate analysis
- Resource utilization

### 🔄 **Integration Tests** (`test_integration.py`)
**Critical for Production** ✅

Validates end-to-end workflows and system integration:
- Complete meal planning workflow
- Agent communication and handoffs
- Budget constraint handling
- Error recovery mechanisms
- Concurrent user support
- Data persistence across requests
- API versioning compatibility
- Security input validation
- Health monitoring integration
- Configuration system validation

### 🤖 **Agent System Tests** (`test_bruno_agents.py`)
**Critical for Production** ✅

Tests multi-agent system functionality:
- Individual agent operations
- Inter-agent communication
- Budget tracking and compliance
- Task management workflows
- Agent failure recovery
- A2A protocol compliance

## 🚀 Quick Start

### Prerequisites

Ensure you have the required dependencies installed:

```bash
pip install pytest fastapi httpx psutil
```

### Running All Tests

```bash
# Run all test suites
python run_tests.py

# Run with verbose output
python run_tests.py --verbose

# Stop on first critical failure
python run_tests.py --fail-fast
```

### Running Specific Test Suites

```bash
# Run only stability tests (recommended for CI/CD)
python run_tests.py --suites stability

# Run stability and integration tests
python run_tests.py --suites stability integration

# Run performance tests only
python run_tests.py --suites load
```

### Generating Test Reports

```bash
# Generate JSON test report
python run_tests.py --report test_results.json

# Run specific suites with report
python run_tests.py --suites stability integration --report ci_results.json
```

## 📊 Test Categories Explained

### Critical Tests (Must Pass for Production)

- **Stability Tests**: Core server functionality
- **Integration Tests**: End-to-end workflows
- **Agent Tests**: Multi-agent system operations

### Performance Tests (Monitoring & Optimization)

- **Load Tests**: Performance under various conditions
- Used for optimization and capacity planning
- Failures don't block production deployment

## 🔍 Individual Test Execution

You can also run individual test files directly with pytest:

```bash
# Run stability tests only
pytest test_server_stability.py -v

# Run specific test function
pytest test_server_stability.py::TestServerStability::test_health_endpoint -v

# Run with detailed output
pytest test_integration.py -v -s

# Run load tests with custom timeout
pytest test_load_performance.py -v --timeout=600
```

## 📈 Understanding Test Results

### Exit Codes

- **0**: All critical tests passed
- **1**: Critical test failures detected
- **124**: Test timeout occurred

### Test Result Interpretation

```
✅ PASS STABILITY    |  25 tests | 100.0% |   45.2s | 🔴 CRITICAL
❌ FAIL LOAD         |  15 tests |  86.7% |  120.5s | 🟡 NON-CRITICAL
✅ PASS INTEGRATION  |  30 tests | 100.0% |   78.3s | 🔴 CRITICAL
✅ PASS AGENTS       |  20 tests | 100.0% |   52.1s | 🔴 CRITICAL
```

- **Status**: ✅ PASS or ❌ FAIL
- **Suite Name**: Test category
- **Test Count**: Number of tests executed
- **Success Rate**: Percentage of tests passed
- **Duration**: Time taken to execute
- **Criticality**: 🔴 CRITICAL (must pass) or 🟡 NON-CRITICAL

## 🛠️ Test Configuration

### Environment Variables

Set these environment variables for comprehensive testing:

```bash
# Required for agent tests
export GEMINI_API_KEY="your_gemini_api_key"
export INSTACART_API_KEY="your_instacart_api_key"

# Optional for enhanced testing
export BRUNO_DEBUG="true"
export BRUNO_LOG_LEVEL="INFO"
```

### Test Timeouts

- **Stability Tests**: 5 minutes
- **Load Tests**: 10 minutes
- **Integration Tests**: 6.5 minutes
- **Agent Tests**: 5 minutes

## 🚨 Troubleshooting

### Common Issues

#### Server Won't Start
```bash
# Check if port is already in use
netstat -an | findstr :8000

# Kill existing processes
taskkill /F /IM python.exe
```

#### Missing Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# Install test-specific packages
pip install pytest pytest-asyncio pytest-timeout
```

#### Test Timeouts
```bash
# Run with increased timeout
python run_tests.py --suites stability --verbose

# Run individual problematic test
pytest test_server_stability.py::TestServerStability::test_health_endpoint -v -s
```

#### Memory Issues
```bash
# Monitor memory usage during tests
python -c "import psutil; print(f'Available RAM: {psutil.virtual_memory().available / (1024**3):.1f} GB')"

# Run tests with memory monitoring
python run_tests.py --suites load --verbose
```

### Debug Mode

For detailed debugging, run tests with maximum verbosity:

```bash
# Maximum verbosity
pytest test_server_stability.py -vvv -s --tb=long

# With pdb debugger on failure
pytest test_server_stability.py --pdb

# Capture all output
pytest test_server_stability.py -v -s --capture=no
```

## 📋 CI/CD Integration

### GitHub Actions Example

```yaml
name: Bruno AI Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio
    - name: Run critical tests
      run: |
        cd server
        python run_tests.py --suites stability integration agents --fail-fast
    - name: Run performance tests
      run: |
        cd server
        python run_tests.py --suites load
      continue-on-error: true
```

### Jenkins Pipeline Example

```groovy
pipeline {
    agent any
    stages {
        stage('Test') {
            steps {
                sh 'cd server && python run_tests.py --suites stability integration agents --report ci_results.json'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'server/ci_results.json', fingerprint: true
                }
            }
        }
    }
}
```

## 📝 Test Development Guidelines

### Adding New Tests

1. **Choose the appropriate test file**:
   - `test_server_stability.py`: Core server functionality
   - `test_load_performance.py`: Performance and load testing
   - `test_integration.py`: End-to-end workflows
   - `test_bruno_agents.py`: Agent-specific functionality

2. **Follow naming conventions**:
   ```python
   def test_descriptive_name_of_what_is_tested(self, fixtures):
       """Test description explaining what is validated."""
   ```

3. **Use appropriate assertions**:
   ```python
   # Good: Descriptive assertion messages
   assert response.status_code == 200, f"Health endpoint failed: {response.text}"
   
   # Good: Performance assertions with context
   assert response_time < 1.0, f"Response too slow: {response_time:.3f}s"
   ```

4. **Mock external dependencies**:
   ```python
   with patch('external_service.api_call') as mock_call:
       mock_call.return_value = expected_response
       # Test logic here
   ```

### Test Best Practices

- **Isolation**: Each test should be independent
- **Cleanup**: Use fixtures for setup and teardown
- **Mocking**: Mock external services and APIs
- **Assertions**: Use descriptive error messages
- **Performance**: Set reasonable timeout expectations
- **Documentation**: Include docstrings explaining test purpose

## 🔧 Advanced Usage

### Custom Test Configuration

```python
# Custom server configuration for testing
test_config = ServerConfig(
    host="localhost",
    port=8005,  # Custom port
    debug=True,
    max_budget=500.0,  # Higher budget for testing
    cors_origins=["*"]
)
```

### Performance Benchmarking

```bash
# Run load tests with custom parameters
python -c "
from test_load_performance import LoadTestRunner
from fastapi.testclient import TestClient
# Custom load testing logic
"
```

### Memory Profiling

```bash
# Install memory profiler
pip install memory-profiler

# Run tests with memory profiling
python -m memory_profiler run_tests.py --suites load
```

## 📞 Support

For test-related issues:

1. **Check the troubleshooting section** above
2. **Run individual tests** to isolate problems
3. **Enable verbose output** for detailed debugging
4. **Check server logs** for additional context
5. **Verify environment setup** and dependencies

## 🎯 Test Coverage Goals

- **Critical Path Coverage**: 100% (health, core APIs, agent communication)
- **Error Handling**: 95% (all error scenarios tested)
- **Performance Benchmarks**: Established baselines for all endpoints
- **Integration Workflows**: All user journeys validated
- **Security**: Input validation and CORS testing

---

**Remember**: Critical tests (🔴) must pass for production deployment. Performance tests (🟡) provide valuable insights but don't block releases.