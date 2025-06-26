# Bruno AI Project Context

## Project Overview

Bruno AI is an innovative AI-powered food budget planning application that combines multi-agent architecture with real-time grocery pricing to help families eat well within their budget constraints. The project features Bruno, a friendly AI bear mascot who serves as a personal meal planning assistant.

## Core Value Proposition

**"Hey Bruno, plan meals for $75 this week"** - Bruno AI creates personalized meal plans that fit exact budget limits using real grocery prices and provides seamless Instacart integration for one-click shopping.

## Technical Architecture

### Multi-Agent System

The project implements Google's Agent-to-Agent (A2A) protocol with four specialized agents:

1. **Bruno Master Agent** - Central orchestrator and user interface
2. **Grocery Browser Agent** - Real-time price discovery and comparison
3. **Recipe Chef Agent** - Meal planning and recipe optimization  
4. **Instacart API Agent** - Product search and order management

### Technology Stack

**Backend (Python)**
- Framework: FastAPI with async support
- AI: Google Gemini API (Gemini 2.5 Flash)
- Multi-Agent: Google Agent Development Kit (ADK) with A2A Protocol
- Web Scraping: Selenium WebDriver for real-time pricing
- Data Processing: Pandas, Pydantic
- Testing: Pytest with comprehensive test suites
- Integration: Instacart API for grocery ordering

**Frontend (Flutter)**
- Framework: Flutter with Dart
- UI: Material Design with custom Bruno branding
- State Management: Provider pattern
- Platform: Cross-platform (iOS & Android)

## Current Project Status

### Completed Components

✅ **Backend Infrastructure**
- Multi-agent system architecture implemented
- FastAPI server with comprehensive endpoints
- Budget tracking and task management systems
- Agent communication protocols
- Comprehensive test suites (integration, stability, performance)

✅ **Agent Implementation**
- Bruno Master Agent with meal planning capabilities
- Grocery Browser Agent with price discovery
- Recipe Chef Agent with budget optimization
- Instacart API Agent with product search

✅ **Flutter Mobile App**
- Cross-platform mobile application
- Material Design UI with Bruno branding
- Chat interface for natural language interaction
- Budget tracking and meal planning screens

### Current Development Focus

🔧 **Testing & Quality Assurance**
- Resolving async/sync fixture issues in test suite
- Improving test coverage for agent interactions
- Performance optimization and load testing

🔧 **API Integration**
- Gemini API integration (API key configured)
- Instacart API integration for real grocery ordering
- Real-time price discovery optimization

## Key Features

### Core Functionality
- **Budget-First Meal Planning**: Creates meal plans within specific budget constraints
- **Real-Time Pricing**: Scrapes current grocery prices from major retailers
- **Smart Shopping Lists**: Generates optimized shopping lists with cost estimates
- **Dietary Accommodations**: Supports various dietary restrictions and preferences
- **Family Sizing**: Adjusts portions and costs based on family size

### Advanced Features
- **Agent Coordination**: Sophisticated multi-agent task delegation
- **Budget Analytics**: Spending pattern analysis and optimization suggestions
- **Recipe Optimization**: Ingredient substitution for budget compliance
- **Store Comparison**: Price comparison across multiple grocery chains
- **Instacart Integration**: One-click grocery ordering and delivery

## Business Model

### Target Market
- Budget-conscious families
- College students
- Young professionals
- Anyone seeking affordable, healthy meal planning

### Revenue Streams
- Premium subscriptions ($4.99/month)
- Instacart affiliate commissions
- Potential grocery store partnerships

### Success Metrics
- User retention (Target: 70% week-1, 40% month-1)
- Instacart conversion rate (Target: 15%+)
- Budget adherence rate (Target: 80%+ users stay within budget)

## Development Environment

### Project Structure
```
bruno_ai/
├── server/                 # Python backend
│   ├── agents/            # Multi-agent implementations
│   ├── tests/             # Comprehensive test suites
│   └── main.py           # FastAPI server entry point
├── brunoai/              # Flutter mobile app
│   ├── lib/              # Dart source code
│   ├── assets/           # Images, fonts, animations
│   └── pubspec.yaml      # Flutter dependencies
└── app docs/             # Project documentation
    ├── prd.md           # Product Requirements Document
    ├── agent.md         # Technical agent specifications
    └── context/         # Project context documentation
```

### Environment Configuration
- **Gemini API Key**: Configured in `.env` file
- **Development Ports**: Server (8000), Flutter (8080)
- **Testing**: Comprehensive pytest suites for all components

## Brand Identity

### Bruno AI Character
- **Appearance**: Friendly brown bear with chef's apron and grocery bag
- **Personality**: Wise, budget-savvy, caring, family-oriented
- **Voice**: Warm, encouraging, knowledgeable but approachable
- **Catchphrase**: "Smart meals, happy families!"
- **Visual Style**: Warm earth tones, professional but friendly

## Technical Challenges & Solutions

### Current Challenges
1. **Test Suite Stability**: Resolving async/sync mismatches in pytest fixtures
2. **Real-Time Pricing**: Optimizing web scraping performance and reliability
3. **Agent Coordination**: Ensuring robust inter-agent communication
4. **Budget Accuracy**: Maintaining precise cost calculations across price fluctuations

### Implemented Solutions
1. **Multi-Agent Architecture**: Modular, scalable agent system with A2A protocol
2. **Comprehensive Testing**: Multiple test suites covering integration, stability, and performance
3. **Error Handling**: Graceful degradation and fallback mechanisms
4. **Budget Tracking**: Sophisticated budget management with real-time monitoring

## Future Roadmap

### Short-Term (Next 3 months)
- Complete test suite stabilization
- Optimize real-time pricing accuracy
- Enhance mobile app user experience
- Launch beta testing program

### Medium-Term (6-12 months)
- Public app store release
- Advanced nutrition optimization
- Expanded grocery store partnerships
- AI-powered budget coaching features

### Long-Term (1-2 years)
- Multi-platform expansion (web, smart speakers)
- International market expansion
- Advanced meal planning AI with learning capabilities
- Bruno merchandise and brand extensions

## Development Guidelines

### Code Quality
- Comprehensive test coverage for all components
- Async/await patterns for optimal performance
- Type hints and documentation for maintainability
- Error handling and graceful degradation

### Agent Development
- Follow A2A protocol specifications
- Implement proper task delegation and coordination
- Maintain agent independence and modularity
- Include comprehensive logging and monitoring

### Testing Strategy
- Unit tests for individual agent functionality
- Integration tests for agent communication
- Performance tests for scalability validation
- End-to-end tests for complete user workflows

This context document provides a comprehensive overview of the Bruno AI project, its current state, technical architecture, and future direction. It serves as a reference for understanding the project's scope, challenges, and opportunities.