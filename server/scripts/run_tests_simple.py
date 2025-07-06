#!/usr/bin/env python3
"""
Simple Test Runner for Bruno AI Server
Tests the core memory and auth systems that we implemented
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime

def run_test_suite(test_file, description):
    """Run a specific test suite and return results"""
    print(f"\n🧪 Running {description}")
    print("=" * 60)
    
    cmd = [
        sys.executable, "-m", "pytest",
        str(test_file),
        "-v",
        "--tb=short",
        "--disable-warnings"
    ]
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Parse output for test results
        output = result.stdout + result.stderr
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            print(f"   Duration: {duration:.1f}s")
            
            # Extract test count from pytest output
            lines = output.split('\n')
            for line in reversed(lines):
                if 'passed' in line and ('warning' in line or 'in' in line):
                    print(f"   {line.strip()}")
                    break
        else:
            print(f"❌ {description} - FAILED")
            print(f"   Duration: {duration:.1f}s")
            print(f"   Exit code: {result.returncode}")
            
            # Show error summary
            error_lines = [line for line in output.split('\n') if 'FAILED' in line]
            if error_lines:
                print("   Failed tests:")
                for error in error_lines[:5]:  # Show first 5 errors
                    print(f"     {error.strip()}")
        
        return {
            'success': result.returncode == 0,
            'duration': duration,
            'output': output
        }
        
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT (5 minutes)")
        return {
            'success': False,
            'duration': 300,
            'output': 'Test timed out'
        }
    except Exception as e:
        print(f"💥 {description} - ERROR: {e}")
        return {
            'success': False,
            'duration': 0,
            'output': str(e)
        }

def main():
    """Main test runner"""
    print("🚀 Bruno AI Server Test Suite")
    print(f"   Timestamp: {datetime.now().isoformat()}")
    print(f"   Working Directory: {Path.cwd()}")
    
    # Test suites to run
    test_suites = [
        {
            'file': 'tests/test_auth_system.py',
            'description': 'Authentication System Tests'
        },
        {
            'file': 'tests/test_memory_system.py',
            'description': 'Memory System Tests'
        },
        {
            'file': 'tests/test_agents_with_memory.py',
            'description': 'Agent Memory Integration Tests'
        }
    ]
    
    results = []
    overall_success = True
    
    for suite in test_suites:
        test_file = Path(suite['file'])
        
        if not test_file.exists():
            print(f"\n⚠️  Test file not found: {test_file}")
            continue
        
        result = run_test_suite(test_file, suite['description'])
        results.append({
            'name': suite['description'],
            'result': result
        })
        
        if not result['success']:
            overall_success = False
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    total_duration = sum(r['result']['duration'] for r in results)
    
    for result in results:
        status = "✅ PASS" if result['result']['success'] else "❌ FAIL"
        duration = result['result']['duration']
        print(f"{status} {result['name']:35} ({duration:.1f}s)")
    
    print(f"\nTotal Duration: {total_duration:.1f}s")
    
    if overall_success:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("💔 SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
