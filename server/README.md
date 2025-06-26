# Bruno AI Agent Ecosystem

A sophisticated multi-agent system for intelligent meal planning and grocery shopping assistance, built using Google's Agent Development Kit (ADK) and A2A protocol.

## 🎯 Overview

Bruno AI is a comprehensive meal planning and grocery shopping assistant that leverages multiple specialized AI agents to provide personalized, budget-conscious meal recommendations and shopping assistance. The system integrates with real-time grocery pricing data and the Instacart API to deliver a complete end-to-end solution.

## 🏗️ Architecture

### Multi-Agent System

The Bruno AI ecosystem consists of four specialized agents:

1. **Bruno Master Agent** - Central coordinator and user interface
2. **Grocery Browser Agent** - Real-time price discovery and comparison
3. **Recipe Chef Agent** - Meal planning and recipe optimization
4. **Instacart API Agent** - Product search and order management

### Technology Stack

- **Framework**: Google Agent Development Kit (ADK) with A2A Protocol
- **API**: FastAPI with async support
- **AI**: OpenAI GPT models
- **Web Scraping**: Selenium WebDriver
- **Data Processing**: Pandas, Pydantic
- **Testing**: Pytest with async support
- **Integration**: Instacart API

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Instacart API key (optional - uses demo data if not provided)
- Chrome browser (for web scraping)

### Installation

1. **Clone the repository**:
   ```bash
   cd d:/projects/2025/bruno_ai/server
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   # Required
   export OPENAI_API_KEY="your_openai_api_key_here"
   
   # Optional
   export INSTACART_API_KEY="your_instacart_api_key_here"
   export BRUNO_MAX_BUDGET="150.0"
   export BRUNO_DEFAULT_FAMILY_SIZE="4"
   export BRUNO_DEBUG="true"
   ```

   **Windows (PowerShell)**:
   ```powershell
   $env:OPENAI_API_KEY="your_openai_api_key_here"
   $env:INSTACART_API_KEY="your_instacart_api_key_here"
   ```

4. **Run the server**:
   ```bash
   python main.py
   ```

   Or with custom settings:
   ```bash
   python main.py --host 0.0.0.0 --port 8080 --debug
   ```

### Verification

1. **Health Check**: Visit `http://localhost:8000/health`
2. **API Documentation**: Visit `http://localhost:8000/docs`
3. **Agent Status**: Visit `http://localhost:8000/api/v1/agents`

## 📚 API Reference

### Core Endpoints

#### Chat Interface
```http
POST /api/v1/chat
Content-Type: application/json

{
  "user_id": "user123",
  "message": "I need help planning meals for this week",
  "budget_limit": 100.0,
  "family_size": 4,
  "dietary_restrictions": ["vegetarian"],
  "zip_code": "90210"
}
```

#### Meal Planning
```http
POST /api/v1/meal-plan?days=7&meals_per_day=3
Content-Type: application/json

{
  "user_id": "user123",
  "budget_limit": 150.0,
  "family_size": 4,
  "dietary_restrictions": ["no nuts", "gluten-free"],
  "preferences": ["quick meals", "healthy"]
}
```

#### Shopping List Generation
```http
POST /api/v1/shopping-list
Content-Type: application/json

{
  "user_id": "user123",
  "message": "Generate shopping list for chicken stir fry and pasta dinner",
  "budget_limit": 60.0,
  "family_size": 3
}
```

#### Price Checking
```http
POST /api/v1/price-check
Content-Type: application/json

{
  "items": ["milk", "bread", "eggs"],
  "zip_code": "90210"
}
```

### Response Format

All API responses follow this structure:

```json
{
  "request_id": "req_123456789",
  "user_id": "user123",
  "success": true,
  "primary_response": "Your meal plan has been created...",
  "agent_responses": {
    "bruno_master": {...},
    "recipe_chef": {...},
    "grocery_browser": {...}
  },
  "budget_info": {
    "total_budget": 100.0,
    "estimated_cost": 87.50,
    "remaining_budget": 12.50
  },
  "recommendations": [...],
  "shopping_list": [...],
  "total_cost": 87.50,
  "processing_time_ms": 1250
}
```

## 🤖 Agent Details

### Bruno Master Agent

**Role**: Central coordinator and user interface

**Capabilities**:
- User request interpretation and routing
- Budget tracking and enforcement
- Task coordination across agents
- Response synthesis and formatting

**Tools**:
- `create_meal_plan`: Generate comprehensive meal plans
- `track_budget`: Monitor spending and budget compliance
- `get_grocery_prices`: Retrieve real-time pricing data
- `create_shopping_list`: Generate optimized shopping lists

### Grocery Browser Agent

**Role**: Real-time price discovery and comparison

**Capabilities**:
- Web scraping from major grocery stores (Walmart, Target, Kroger)
- Price comparison and deal identification
- Store inventory verification
- Weekly deals and promotions tracking

**Tools**:
- `browse_walmart_prices`: Get current Walmart pricing
- `browse_target_prices`: Get current Target pricing
- `get_weekly_deals`: Find current promotions
- `verify_store_inventory`: Check product availability
- `compare_store_prices`: Cross-store price comparison

### Recipe Chef Agent

**Role**: Meal planning and recipe optimization

**Capabilities**:
- Budget-conscious meal planning
- Recipe optimization and scaling
- Nutritional analysis and recommendations
- Ingredient substitution suggestions

**Tools**:
- `create_meal_plan`: Design custom meal plans
- `optimize_recipe_for_budget`: Budget-friendly recipe modifications
- `suggest_substitutions`: Alternative ingredient recommendations
- `calculate_nutrition`: Nutritional analysis
- `generate_shopping_list`: Recipe-based shopping lists
- `find_recipes_by_ingredients`: Recipe discovery
- `scale_recipe`: Adjust serving sizes
- `get_cooking_tips`: Cooking guidance and tips

### Instacart API Agent

**Role**: Product search and order management

**Capabilities**:
- Product search and details retrieval
- Store location and information
- Shopping cart management
- Order placement and tracking
- Delivery estimation

**Tools**:
- `search_products`: Find products by query
- `get_product_details`: Detailed product information
- `find_stores`: Locate nearby stores
- `create_cart`: Initialize shopping cart
- `add_to_cart`: Add items to cart
- `estimate_delivery`: Calculate delivery time and cost
- `place_order`: Submit order for processing
- `track_order`: Monitor order status

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest test_bruno_agents.py -v

# Run specific test categories
pytest test_bruno_agents.py::TestBrunoAgentEcosystem::test_meal_planning_workflow -v
pytest test_bruno_agents.py::TestBrunoAgentEcosystem::test_budget_tracking_compliance -v

# Run with coverage
pytest test_bruno_agents.py --cov=. --cov-report=html
```

### Test Categories

1. **Meal Planning Workflow** - End-to-end meal planning process
2. **Grocery Browser Price Discovery** - Web scraping and price comparison
3. **Recipe Chef Budget Optimization** - Budget-conscious meal planning
4. **Agent Failure Recovery** - Error handling and fallback mechanisms
5. **A2A Protocol Compliance** - Agent communication and discovery
6. **Budget Tracking** - Budget enforcement and monitoring
7. **Instacart API Integration** - Product search and order management
8. **End-to-End Integration** - Complete system workflow
9. **Error Handling** - Edge cases and error scenarios
10. **Performance and Scalability** - Load testing and response times

## 🔧 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key for AI functionality |
| `INSTACART_API_KEY` | No | "demo_key" | Instacart API key (uses demo data if not set) |
| `BRUNO_MAX_BUDGET` | No | 150.0 | Maximum budget per user session |
| `BRUNO_DEFAULT_FAMILY_SIZE` | No | 4 | Default family size for meal planning |
| `BRUNO_DEBUG` | No | false | Enable debug mode |
| `BRUNO_HOST` | No | localhost | Server host address |
| `BRUNO_PORT` | No | 8000 | Server port number |

### Command Line Options

```bash
python main.py --help

usage: main.py [-h] [--host HOST] [--port PORT] [--debug] [--production]
               [--log-level {DEBUG,INFO,WARNING,ERROR}] [--workers WORKERS]

Bruno AI Agent Ecosystem Server

optional arguments:
  -h, --help            show this help message and exit
  --host HOST           Host to bind the server to (default: localhost)
  --port PORT           Port to bind the server to (default: 8000)
  --debug               Enable debug mode
  --production          Run in production mode (disables debug, optimizes performance)
  --log-level {DEBUG,INFO,WARNING,ERROR}
                        Set logging level (default: INFO)
  --workers WORKERS     Number of worker processes (default: 1)
```

## 🔒 Security Considerations

### API Keys
- Store API keys in environment variables, never in code
- Use different keys for development and production
- Rotate keys regularly

### Web Scraping
- Respect robots.txt and rate limits
- Use appropriate delays between requests
- Handle anti-bot measures gracefully

### Data Privacy
- User data is processed in memory only
- No persistent storage of personal information
- Budget and preference data is session-based

## 📊 Monitoring and Logging

### Log Levels
- **DEBUG**: Detailed debugging information
- **INFO**: General operational messages
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failures

### Log Files
- Application logs: `bruno_ai.log`
- Access logs: Enabled in debug mode
- Error logs: Captured in main log file

### Health Monitoring

```bash
# Check server health
curl http://localhost:8000/health

# Check agent status
curl http://localhost:8000/api/v1/agents

# Monitor request processing
curl http://localhost:8000/api/v1/status/{request_id}
```

## 🚀 Deployment

### Development

```bash
python main.py --debug
```

### Production

```bash
# Single worker
python main.py --production --host 0.0.0.0 --port 8000

# Multiple workers
python main.py --production --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (Optional)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "main.py", "--production", "--host", "0.0.0.0"]
```

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov black flake8
   ```
4. Run tests: `pytest`
5. Format code: `black .`
6. Check linting: `flake8`
7. Submit pull request

### Code Style

- Follow PEP 8 guidelines
- Use type hints for function signatures
- Write comprehensive docstrings
- Maintain test coverage above 80%

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues

1. **"OPENAI_API_KEY not found"**
   - Ensure the environment variable is set correctly
   - Check for typos in the variable name

2. **"Chrome driver not found"**
   - Install Chrome browser
   - Ensure ChromeDriver is in PATH or install via selenium-manager

3. **"Port already in use"**
   - Use a different port: `python main.py --port 8001`
   - Kill existing processes using the port

4. **"Agent timeout"**
   - Check internet connectivity
   - Verify API keys are valid
   - Increase timeout settings in configuration

### Getting Help

- Check the API documentation at `/docs`
- Review log files for error details
- Run health checks to verify system status
- Consult the test suite for usage examples

## 🔄 Updates and Maintenance

### Regular Maintenance

- Update dependencies monthly
- Rotate API keys quarterly
- Monitor log files for errors
- Test web scraping functionality regularly

### Version Updates

- Check Google ADK updates for new features
- Update OpenAI client library for latest models
- Review Instacart API changes
- Update browser drivers for web scraping

---

**Bruno AI Agent Ecosystem** - Intelligent meal planning and grocery shopping assistance powered by multi-agent AI technology.