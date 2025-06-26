#!/usr/bin/env python3
"""
Bruno AI Server Test Runner

Comprehensive test execution script that runs all test suites
with proper configuration, reporting, and CI/CD integration.
"""

import os
import sys
import subprocess
import argparse
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TestResult:
    """Container for test execution results."""
    suite_name: str
    passed: int
    failed: int
    skipped: int
    errors: int
    duration: float
    exit_code: int
    output: str
    
    @property
    def total_tests(self) -> int:
        return self.passed + self.failed + self.skipped + self.errors
    
    @property
    def success_rate(self) -> float:
        if self.total_tests == 0:
            return 0.0
        return (self.passed / self.total_tests) * 100
    
    @property
    def is_successful(self) -> bool:
        return self.exit_code == 0 and self.failed == 0 and self.errors == 0


class TestRunner:
    """Main test runner class."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.server_dir = project_root / "server"
        self.results: List[TestResult] = []
        
        # Test suites configuration
        self.test_suites = {
            "stability": {
                "file": "test_server_stability.py",
                "description": "Server Stability & Production Readiness Tests",
                "timeout": 300,  # 5 minutes
                "critical": True
            },
            "load": {
                "file": "test_load_performance.py",
                "description": "Load Testing & Performance Validation",
                "timeout": 600,  # 10 minutes
                "critical": False
            },
            "integration": {
                "file": "test_integration.py",
                "description": "Integration & End-to-End Workflow Tests",
                "timeout": 400,  # 6.5 minutes
                "critical": True
            },
            "agents": {
                "file": "test_bruno_agents.py",
                "description": "Agent System & Multi-Agent Tests",
                "timeout": 300,  # 5 minutes
                "critical": True
            }
        }
    
    def setup_environment(self) -> bool:
        """Setup test environment and dependencies."""
        print("🔧 Setting up test environment...")
        
        # Check if we're in the correct directory
        if not self.server_dir.exists():
            print(f"❌ Server directory not found: {self.server_dir}")
            return False
        
        # Check for required test files
        missing_files = []
        for suite_name, config in self.test_suites.items():
            test_file = self.server_dir / config["file"]
            if not test_file.exists():
                missing_files.append(config["file"])
        
        if missing_files:
            print(f"❌ Missing test files: {', '.join(missing_files)}")
            return False
        
        # Check Python dependencies
        required_packages = [
            "pytest", "fastapi", "httpx", "psutil"
        ]
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                print(f"❌ Missing required package: {package}")
                print(f"   Install with: pip install {package}")
                return False
        
        print("✅ Test environment setup complete")
        return True
    
    def run_test_suite(self, suite_name: str, config: Dict[str, Any], 
                      verbose: bool = False, capture_output: bool = True) -> TestResult:
        """Run a single test suite."""
        test_file = self.server_dir / config["file"]
        
        print(f"\n🧪 Running {config['description']}...")
        print(f"   File: {config['file']}")
        print(f"   Timeout: {config['timeout']}s")
        print(f"   Critical: {'Yes' if config['critical'] else 'No'}")
        
        # Prepare pytest command
        cmd = [
            sys.executable, "-m", "pytest",
            str(test_file),
            "-v" if verbose else "-q",
            "--tb=short",
            "--durations=10",
            "--strict-markers",
            "--disable-warnings"
        ]
        
        if capture_output:
            cmd.extend(["--capture=no"])
        
        start_time = time.time()
        
        try:
            # Run the test
            result = subprocess.run(
                cmd,
                cwd=self.server_dir,
                capture_output=True,
                text=True,
                timeout=config["timeout"]
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Parse pytest output for statistics
            output = result.stdout + result.stderr
            passed, failed, skipped, errors = self._parse_pytest_output(output)
            
            test_result = TestResult(
                suite_name=suite_name,
                passed=passed,
                failed=failed,
                skipped=skipped,
                errors=errors,
                duration=duration,
                exit_code=result.returncode,
                output=output
            )
            
            # Print immediate results
            if test_result.is_successful:
                print(f"✅ {config['description']} - PASSED")
            else:
                print(f"❌ {config['description']} - FAILED")
            
            print(f"   Tests: {test_result.total_tests} | "
                  f"Passed: {test_result.passed} | "
                  f"Failed: {test_result.failed} | "
                  f"Duration: {duration:.1f}s")
            
            if not test_result.is_successful and verbose:
                print(f"\n📋 Error Output:")
                print(output[-1000:])  # Last 1000 characters
            
            return test_result
            
        except subprocess.TimeoutExpired:
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"⏰ {config['description']} - TIMEOUT ({config['timeout']}s)")
            
            return TestResult(
                suite_name=suite_name,
                passed=0,
                failed=0,
                skipped=0,
                errors=1,
                duration=duration,
                exit_code=124,  # Timeout exit code
                output=f"Test suite timed out after {config['timeout']} seconds"
            )
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"💥 {config['description']} - ERROR: {str(e)}")
            
            return TestResult(
                suite_name=suite_name,
                passed=0,
                failed=0,
                skipped=0,
                errors=1,
                duration=duration,
                exit_code=1,
                output=f"Test execution error: {str(e)}"
            )
    
    def _parse_pytest_output(self, output: str) -> tuple[int, int, int, int]:
        """Parse pytest output to extract test statistics."""
        passed = failed = skipped = errors = 0
        
        # Look for pytest summary line
        lines = output.split('\n')
        for line in lines:
            line = line.strip().lower()
            
            # Match patterns like "5 passed, 2 failed, 1 skipped"
            if 'passed' in line or 'failed' in line or 'skipped' in line or 'error' in line:
                import re
                
                passed_match = re.search(r'(\d+)\s+passed', line)
                if passed_match:
                    passed = int(passed_match.group(1))
                
                failed_match = re.search(r'(\d+)\s+failed', line)
                if failed_match:
                    failed = int(failed_match.group(1))
                
                skipped_match = re.search(r'(\d+)\s+skipped', line)
                if skipped_match:
                    skipped = int(skipped_match.group(1))
                
                error_match = re.search(r'(\d+)\s+error', line)
                if error_match:
                    errors = int(error_match.group(1))
        
        return passed, failed, skipped, errors
    
    def run_all_tests(self, suites: Optional[List[str]] = None, 
                     verbose: bool = False, fail_fast: bool = False) -> bool:
        """Run all or specified test suites."""
        print("🚀 Starting Bruno AI Server Test Suite")
        print(f"   Project Root: {self.project_root}")
        print(f"   Server Directory: {self.server_dir}")
        print(f"   Timestamp: {datetime.now().isoformat()}")
        
        if not self.setup_environment():
            return False
        
        # Determine which suites to run
        suites_to_run = suites if suites else list(self.test_suites.keys())
        
        print(f"\n📋 Test Suites to Run: {', '.join(suites_to_run)}")
        
        # Run each test suite
        overall_success = True
        
        for suite_name in suites_to_run:
            if suite_name not in self.test_suites:
                print(f"⚠️  Unknown test suite: {suite_name}")
                continue
            
            config = self.test_suites[suite_name]
            result = self.run_test_suite(suite_name, config, verbose)
            self.results.append(result)
            
            # Check if we should fail fast
            if fail_fast and not result.is_successful and config["critical"]:
                print(f"\n🛑 Failing fast due to critical test failure: {suite_name}")
                overall_success = False
                break
            
            if not result.is_successful:
                overall_success = False
        
        # Print final summary
        self._print_summary()
        
        return overall_success
    
    def _print_summary(self):
        """Print comprehensive test results summary."""
        print("\n" + "="*80)
        print("📊 TEST EXECUTION SUMMARY")
        print("="*80)
        
        total_tests = sum(r.total_tests for r in self.results)
        total_passed = sum(r.passed for r in self.results)
        total_failed = sum(r.failed for r in self.results)
        total_skipped = sum(r.skipped for r in self.results)
        total_errors = sum(r.errors for r in self.results)
        total_duration = sum(r.duration for r in self.results)
        
        print(f"\n📈 Overall Statistics:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {total_passed} ({(total_passed/total_tests*100) if total_tests > 0 else 0:.1f}%)")
        print(f"   Failed: {total_failed}")
        print(f"   Skipped: {total_skipped}")
        print(f"   Errors: {total_errors}")
        print(f"   Total Duration: {total_duration:.1f}s")
        
        print(f"\n📋 Suite Results:")
        for result in self.results:
            status = "✅ PASS" if result.is_successful else "❌ FAIL"
            critical = "🔴 CRITICAL" if self.test_suites[result.suite_name]["critical"] else "🟡 NON-CRITICAL"
            
            print(f"   {status} {result.suite_name.upper():12} | "
                  f"{result.total_tests:3} tests | "
                  f"{result.success_rate:5.1f}% | "
                  f"{result.duration:6.1f}s | "
                  f"{critical}")
        
        # Determine overall result
        critical_failures = [
            r for r in self.results 
            if not r.is_successful and self.test_suites[r.suite_name]["critical"]
        ]
        
        if critical_failures:
            print(f"\n🚨 OVERALL RESULT: FAILED")
            print(f"   Critical test failures detected: {len(critical_failures)}")
            for failure in critical_failures:
                print(f"   - {failure.suite_name}: {failure.failed} failed, {failure.errors} errors")
        else:
            print(f"\n🎉 OVERALL RESULT: PASSED")
            print(f"   All critical tests passed successfully!")
        
        print("\n" + "="*80)
    
    def generate_report(self, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """Generate detailed test report in JSON format."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "total_suites": len(self.results),
            "overall_success": all(r.is_successful or not self.test_suites[r.suite_name]["critical"] for r in self.results),
            "summary": {
                "total_tests": sum(r.total_tests for r in self.results),
                "total_passed": sum(r.passed for r in self.results),
                "total_failed": sum(r.failed for r in self.results),
                "total_skipped": sum(r.skipped for r in self.results),
                "total_errors": sum(r.errors for r in self.results),
                "total_duration": sum(r.duration for r in self.results)
            },
            "suites": []
        }
        
        for result in self.results:
            suite_config = self.test_suites[result.suite_name]
            suite_report = {
                "name": result.suite_name,
                "description": suite_config["description"],
                "file": suite_config["file"],
                "critical": suite_config["critical"],
                "success": result.is_successful,
                "statistics": {
                    "total": result.total_tests,
                    "passed": result.passed,
                    "failed": result.failed,
                    "skipped": result.skipped,
                    "errors": result.errors,
                    "success_rate": result.success_rate,
                    "duration": result.duration
                },
                "exit_code": result.exit_code,
                "output": result.output
            }
            report["suites"].append(suite_report)
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n📄 Test report saved to: {output_file}")
        
        return report


def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(
        description="Bruno AI Server Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                          # Run all tests
  python run_tests.py --suites stability      # Run only stability tests
  python run_tests.py --verbose --fail-fast   # Verbose output, stop on first critical failure
  python run_tests.py --report results.json   # Generate JSON report
        """
    )
    
    parser.add_argument(
        "--suites", 
        nargs="+", 
        choices=["stability", "load", "integration", "agents"],
        help="Specific test suites to run (default: all)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--fail-fast", "-x",
        action="store_true",
        help="Stop on first critical test failure"
    )
    
    parser.add_argument(
        "--report", "-r",
        type=Path,
        help="Generate JSON test report to specified file"
    )
    
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd().parent,  # Assume we're in server/ directory
        help="Project root directory (default: parent of current directory)"
    )
    
    args = parser.parse_args()
    
    # Create test runner
    runner = TestRunner(args.project_root)
    
    # Run tests
    success = runner.run_all_tests(
        suites=args.suites,
        verbose=args.verbose,
        fail_fast=args.fail_fast
    )
    
    # Generate report if requested
    if args.report:
        runner.generate_report(args.report)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()