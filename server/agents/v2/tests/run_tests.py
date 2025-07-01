#!/usr/bin/env python3
"""
Test runner for Bruno AI V2.0 agent tests
Provides different test execution modes and reporting options
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def setup_test_environment():
    """Setup test environment variables"""
    test_env = {
        'PYTHONPATH': str(Path(__file__).parent.parent),
        'GEMINI_API_KEY': 'test_gemini_key',
        'INSTACART_API_KEY': 'test_instacart_key',
        'INSTACART_AFFILIATE_ID': 'test_affiliate',
        'REDIS_URL': 'redis://localhost:6379',
        'A2A_GATEWAY_URL': 'http://localhost:3000',
        'TESTING': 'true'
    }
    
    # Merge with existing environment
    env = os.environ.copy()
    env.update(test_env)
    return env

def run_tests(test_type='all', coverage=False, verbose=False, parallel=False):
    """Run tests with specified configuration"""
    
    # Base pytest command
    cmd = ['python', '-m', 'pytest']
    
    # Test selection based on type
    if test_type == 'unit':
        cmd.extend(['-m', 'unit'])
    elif test_type == 'integration':
        cmd.extend(['-m', 'integration'])
    elif test_type == 'fast':
        cmd.extend(['-m', 'not slow'])
    elif test_type == 'budget_agent':
        cmd.append('test_budget_analyst_agent_v2.py')
    elif test_type == 'master_agent':
        cmd.append('test_bruno_master_agent.py')
    elif test_type == 'instacart_agent':
        cmd.append('test_instacart_integration_agent.py')
    elif test_type == 'gateway':
        cmd.append('test_a2a_gateway.py')
    
    # Coverage reporting
    if coverage:
        cmd.extend([
            '--cov=../budget_analyst_agent',
            '--cov=../bruno_master_agent', 
            '--cov=../instacart_integration_agent',
            '--cov=../a2a_gateway',
            '--cov=../base_agent',
            '--cov-report=html:htmlcov',
            '--cov-report=term-missing',
            '--cov-fail-under=80'
        ])
    
    # Verbosity
    if verbose:
        cmd.append('-v')
    else:
        cmd.extend(['-q', '--tb=short'])
    
    # Parallel execution
    if parallel:
        cmd.extend(['-n', 'auto'])
    
    # Additional options
    cmd.extend([
        '--strict-markers',
        '--disable-warnings',
        '--tb=short'
    ])
    
    # Setup environment
    env = setup_test_environment()
    
    print(f"Running tests with command: {' '.join(cmd)}")
    print(f"Test type: {test_type}")
    print(f"Coverage: {'enabled' if coverage else 'disabled'}")
    print(f"Parallel: {'enabled' if parallel else 'disabled'}")
    print("-" * 50)
    
    # Run tests
    try:
        result = subprocess.run(cmd, env=env, cwd=Path(__file__).parent)
        return result.returncode
    except KeyboardInterrupt:
        print("\nTest execution interrupted by user")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

def main():
    """Main test runner entry point"""
    parser = argparse.ArgumentParser(description='Bruno AI V2.0 Test Runner')
    
    parser.add_argument(
        '--type', 
        choices=['all', 'unit', 'integration', 'fast', 'budget_agent', 'master_agent', 'instacart_agent', 'gateway'],
        default='all',
        help='Type of tests to run'
    )
    
    parser.add_argument(
        '--coverage', 
        action='store_true',
        help='Enable coverage reporting'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--parallel', '-p',
        action='store_true',
        help='Run tests in parallel'
    )
    
    parser.add_argument(
        '--install-deps',
        action='store_true',
        help='Install test dependencies before running'
    )
    
    args = parser.parse_args()
    
    # Install dependencies if requested
    if args.install_deps:
        print("Installing test dependencies...")
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 
            str(Path(__file__).parent / 'requirements-test.txt')
        ])
        print("Dependencies installed.\n")
    
    # Run tests
    exit_code = run_tests(
        test_type=args.type,
        coverage=args.coverage,
        verbose=args.verbose,
        parallel=args.parallel
    )
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
        if args.coverage:
            print("📊 Coverage report generated in htmlcov/index.html")
    else:
        print("\n❌ Some tests failed!")
    
    return exit_code

if __name__ == '__main__':
    sys.exit(main())
