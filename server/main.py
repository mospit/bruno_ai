#!/usr/bin/env python3
"""
Bruno AI Server Main Entry Point
Start the Bruno AI system with proper logging and error handling.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import main system after path setup
from agents.v2.main import run_system

if __name__ == "__main__":
    try:
        print("🐻 Starting Bruno AI System...")
        run_system()
    except KeyboardInterrupt:
        print("\n🐻 Bruno AI System stopped by user")
    except Exception as e:
        print(f"❌ Failed to start Bruno AI System: {e}")
        sys.exit(1)
