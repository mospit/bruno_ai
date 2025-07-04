# 🐻 Bruno AI Server

A multi-agent AI system for intelligent meal planning and budget-conscious cooking, featuring Bruno - your friendly Brooklyn bear assistant.

## 📁 Project Structure

```
server/
├── config/                 # Configuration files
│   ├── .env.example       # Environment template
│   ├── .env              # Your actual environment (create from template)
│   └── requirements.txt   # Python dependencies
├── docs/                  # Documentation
│   ├── README.md         # Main documentation
│   ├── *.md             # Additional docs
├── logs/                  # Log files
│   └── *.log            # Application logs
├── scripts/              # Utility scripts
│   ├── setup_dev.py     # Development setup
│   └── run_tests.py     # Test runner
├── src/                  # Source code
│   ├── agents/          # Agent implementations
│   │   ├── v1/         # Legacy agents
│   │   └── v2/         # Current agents
│   ├── a2a_server.py   # Agent-to-Agent server
│   └── main.py         # System entry point
├── tests/               # Test suite
│   ├── test_*.py       # Test files
│   └── run_tests.py    # Test runner
└── main.py             # Application entry point
```

## 🚀 Quick Start

### 1. Setup Development Environment

```bash
# Run the setup script
python scripts/setup_dev.py
```

### 2. Configure Environment

Edit `config/.env` with your API keys:

```bash
GEMINI_API_KEY=your_actual_key_here
INSTACART_API_KEY=your_actual_key_here
```

### 3. Run the System

```bash
# Start Bruno AI
python main.py
```

### 4. Run Tests

```bash
# Run all tests
python scripts/run_tests.py
```

## 🐻 Bruno AI Agents

### V2 Agents (Current)
- **Bruno Master Agent**: Main orchestrator
- **Instacart Integration Agent**: Shopping and pricing
- **Budget Analyst Agent**: Financial analysis
- **Recipe Chef Agent**: Meal planning and recipes
- **Nutrition Guide Agent**: Dietary analysis *(coming soon)*
- **Pantry Manager Agent**: Inventory management *(coming soon)*

### V1 Agents (Legacy)
- Legacy implementations for reference

## 🔧 Development

### Project Standards
- Python 3.8+
- Type hints throughout
- Comprehensive test coverage
- Clear documentation
- Brooklyn Bruno personality consistency

### Adding New Agents
1. Create agent in `src/agents/v2/`
2. Implement Bruno personality bridge
3. Add comprehensive tests
4. Update documentation

### Testing
```bash
# Run specific test
python -m pytest tests/test_specific.py -v

# Run with coverage
python -m pytest tests/ --cov=src/

# Run personality tests
python -m pytest tests/test_bruno_personality*.py -v
```

## 📚 Documentation

- **Architecture**: See `docs/optimized_agent_architecture.md`
- **Personality**: See `docs/bruno_personality_profile.md`
- **API**: See agent-specific documentation

## 🔧 Configuration

### Environment Variables
- `GEMINI_API_KEY`: Required for AI functionality
- `INSTACART_API_KEY`: Required for shopping integration
- `REDIS_URL`: Optional (defaults to localhost)
- `LOG_LEVEL`: Optional (defaults to INFO)

### File Locations
- Config: `config/`
- Logs: `logs/`
- Source: `src/`
- Tests: `tests/`

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `src/` is in Python path
2. **API Keys**: Check your `.env` file configuration
3. **Dependencies**: Run `pip install -r config/requirements.txt`
4. **Logs**: Check `logs/` directory for detailed error information

### Getting Help

1. Check the logs in `logs/`
2. Run tests to identify issues
3. Review documentation in `docs/`
4. Check agent-specific README files

## 📈 Performance

- **Response Time**: <2 seconds for meal plans
- **Accuracy**: >99% pricing accuracy via Instacart API
- **Reliability**: >99.5% uptime target
- **Personality**: Consistent Brooklyn Bruno across all interactions

## 🎯 Next Steps

1. Implement Nutrition Guide Agent
2. Implement Pantry Manager Agent  
3. Enhance multi-agent coordination
4. Add comprehensive integration tests
5. Deploy to production environment

---

**Made with ❤️ by the Bruno AI Team**
