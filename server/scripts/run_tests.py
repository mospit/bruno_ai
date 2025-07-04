#!/usr/bin/env python3
"""
Bruno AI Test Runner
Run all tests with proper coverage and reporting.
"""

import sys
import subprocess
from pathlib import Path

def run_tests():
    """Run the complete test suite."""
    
    # Get the server directory
    server_dir = Path(__file__).parent.parent
    
    # Add src to Python path
    src_path = server_dir / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    # Change to server directory
    import os
    os.chdir(server_dir)
    
    print("🐻 Running Bruno AI Test Suite...")
    print("=" * 50)
    
    # Run pytest with coverage
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",
            "--tb=short",
            "--color=yes"
        ], check=True)
        
        print("\n✅ All tests passed!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ pytest not found. Install with: pip install pytest")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
