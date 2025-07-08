# Bruno AI Model Allocation Strategy

## Overview
This document outlines the strategic allocation of Gemini models across the Bruno AI agent ecosystem for optimal performance and cost efficiency.

## Available Models

### gemini-2.5-flash
- **Capabilities**: Superior reasoning, complex analysis, creative content generation
- **Context Window**: Large (exact size TBD)
- **Use Case**: High-complexity tasks requiring deep reasoning
- **Cost**: Higher per token
- **Performance**: Best accuracy and sophistication

### gemini-2.5-flash-lite-preview-06-17
- **Capabilities**: Optimized for speed and efficiency
- **Context Window**: Smaller than full Flash model
- **Use Case**: High-frequency, real-time operations
- **Cost**: Lower per token
- **Performance**: Faster response times

## Model Allocation

### Agents Using gemini-2.5-flash (Premium Model)

#### 1. Base Agent
- **Location**: `src/agents/v2/base_agent.py`
- **Justification**: Handles Bruno's core personality and foundational interactions
- **Key Responsibilities**: 
  - Bruno's Brooklyn personality generation
  - Core LLM interactions
  - User context processing

#### 2. Bruno Master Agent V2
- **Location**: `src/agents/v2/bruno_master_agent.py` (inherits from BaseAgent)
- **Justification**: Central orchestrator requiring complex multi-agent coordination
- **Key Responsibilities**:
  - Meal planning orchestration
  - Multi-agent workflow management
  - Strategic decision making
- **Performance Targets**: <2 seconds response time, >95% coordination efficiency

#### 3. Budget Analyst Agent V2
- **Location**: `src/agents/v2/budget_analyst_agent.py` (inherits from BaseAgent)
- **Justification**: Requires high accuracy for financial analysis and predictions
- **Key Responsibilities**:
  - Predictive financial analytics
  - Complex numerical analysis
  - Budget optimization algorithms
- **Performance Targets**: >90% analysis accuracy, >85% prediction confidence


### Agents Using gemini-2.5-flash-lite-preview-06-17 (Efficiency Model)

#### 1. Instacart Integration Agent V2
- **Location**: `src/agents/v2/instacart_integration_agent.py`
- **Justification**: High-frequency API operations requiring speed and cost efficiency
- **Key Responsibilities**:
  - Real-time price monitoring
  - API data processing
  - Shopping list generation
- **Performance Targets**: <1 second product search, >99% pricing accuracy


## Configuration Details

### Environment Variables Required
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### Code Implementation
All agents inherit from `BaseAgent` (V2):

**V2 Agents (Inheritance-based)**:
```python
# BaseAgent sets default to gemini-2.5-flash
# Specific agents can override in __init__:
self.model = genai.GenerativeModel('gemini-2.5-flash-lite-preview-06-17')
```

## Performance Monitoring

### Metrics to Track
1. **Response Times**: Monitor latency differences between models
2. **Cost Analysis**: Track token usage and costs per agent
3. **Accuracy Metrics**: Measure task success rates
4. **User Satisfaction**: Monitor user interaction quality

### Expected Outcomes
- **Cost Savings**: 20-30% reduction in LLM costs through strategic lite model usage
- **Performance Optimization**: Faster responses for high-frequency operations
- **Quality Maintenance**: No degradation in core Bruno personality or complex reasoning tasks

## Future Considerations

### Model Upgrades
- Monitor for new Gemini model releases
- Evaluate performance improvements vs. cost changes
- Consider specialized models for specific agent types

### Agent Evolution
- As agents become more sophisticated, reassess model requirements
- Consider hybrid approaches for complex agents (lite for preprocessing, full for reasoning)
- Implement dynamic model selection based on task complexity

## Change Log

### 2025-01-08
- Initial model allocation implemented
- Updated BaseAgent to gemini-2.5-flash
- Updated Instacart agents to gemini-2.5-flash-lite-preview-06-17
- Removed all V1 agents - V2 agents only

---

**Note**: This allocation strategy balances performance, cost, and functionality. Regular monitoring and optimization may be needed based on real-world usage patterns.
