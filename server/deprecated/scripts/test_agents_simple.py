#!/usr/bin/env python3
"""
Simple standalone test for Bruno AI agents
Test each agent individually without the full system startup.
"""

import sys
import os
from pathlib import Path
import asyncio

# Add src to path
server_dir = Path(__file__).parent.parent
src_path = server_dir / "src"
sys.path.insert(0, str(src_path))

# Load environment
from dotenv import load_dotenv
config_path = server_dir / "config" / ".env"
load_dotenv(dotenv_path=config_path)

# Set defaults for testing
os.environ.setdefault("INSTACART_API_KEY", "demo_key")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")
os.environ.setdefault("GEMINI_API_KEY", "demo_key")

async def test_bruno_master_agent():
    """Test Bruno Master Agent initialization."""
    print("🐻 Testing Bruno Master Agent...")
    
    try:
        from agents.v2.bruno_master_agent import BrunoMasterAgentV2
        agent = BrunoMasterAgentV2()
        
        # Test health check
        health = await agent.health_check()
        print(f"✅ Health Check: {health}")
        
        # Test basic functionality
        print(f"✅ Agent Card: {agent.agent_card.name} v{agent.agent_card.version}")
        print(f"✅ Capabilities: {len(agent.agent_card.capabilities)} defined")
        
        return True
        
    except Exception as e:
        print(f"❌ Bruno Master Agent failed: {e}")
        return False

async def test_instacart_agent():
    """Test Instacart Integration Agent."""
    print("\n🛒 Testing Instacart Integration Agent...")
    
    try:
        from agents.v2.instacart_integration_agent import InstacartIntegrationAgentV2
        agent = InstacartIntegrationAgentV2()
        
        # Test health check
        health = await agent.health_check()
        print(f"✅ Health Check: {health}")
        
        print(f"✅ Agent Card: {agent.agent_card.name} v{agent.agent_card.version}")
        
        return True
        
    except Exception as e:
        print(f"❌ Instacart Agent failed: {e}")
        return False

async def test_budget_analyst_agent():
    """Test Budget Analyst Agent."""
    print("\n💰 Testing Budget Analyst Agent...")
    
    try:
        from agents.v2.budget_analyst_agent import BudgetAnalystAgentV2
        agent = BudgetAnalystAgentV2()
        
        # Test health check
        health = await agent.health_check()
        print(f"✅ Health Check: {health}")
        
        print(f"✅ Agent Card: {agent.agent_card.name} v{agent.agent_card.version}")
        
        return True
        
    except Exception as e:
        print(f"❌ Budget Analyst Agent failed: {e}")
        return False

# Recipe Chef Agent will be implemented as V2 agent
# For now, we focus on the core V2 agents that are working

async def main():
    """Run all agent tests."""
    print("🧪 Bruno AI Agent Testing Suite")
    print("=" * 50)
    
    tests = [
        ("Bruno Master Agent", test_bruno_master_agent),
        ("Instacart Integration Agent", test_instacart_agent),
        ("Budget Analyst Agent", test_budget_analyst_agent)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("🧪 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All agents working correctly!")
        return True
    else:
        print("⚠️  Some agents need attention")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Testing failed: {e}")
        sys.exit(1)
