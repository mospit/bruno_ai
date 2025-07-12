#!/usr/bin/env python3
"""
Bruno AI Server Load Testing and Performance Validation

This module contains load tests and performance benchmarks to ensure
the server can handle production traffic loads.
"""

import pytest
import asyncio
import time
import statistics
import threading
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

import httpx
from fastapi.testclient import TestClient
from a2a_server import BrunoAIServer, ServerConfig


@dataclass
class PerformanceMetrics:
    """Container for performance test results."""
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    min_response_time: float
    max_response_time: float
    median_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    error_rate: float
    test_duration: float


class LoadTestRunner:
    """Utility class for running load tests."""
    
    def __init__(self, test_client: TestClient):
        self.test_client = test_client
        self.results: List[Tuple[float, int, str]] = []  # (response_time, status_code, endpoint)
    
    def make_request(self, method: str, endpoint: str, data: Dict = None) -> Tuple[float, int, str]:
        """Make a single request and measure response time."""
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                response = self.test_client.get(endpoint)
            elif method.upper() == "POST":
                response = self.test_client.post(endpoint, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            end_time = time.time()
            response_time = end_time - start_time
            
            return response_time, response.status_code, endpoint
            
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            return response_time, 500, f"{endpoint} (error: {str(e)})"
    
    def run_concurrent_requests(self, 
                              requests: List[Tuple[str, str, Dict]], 
                              max_workers: int = 10) -> PerformanceMetrics:
        """Run multiple requests concurrently and collect metrics."""
        start_time = time.time()
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            for method, endpoint, data in requests:
                future = executor.submit(self.make_request, method, endpoint, data)
                futures.append(future)
            
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=30)  # 30 second timeout
                    results.append(result)
                except Exception as e:
                    results.append((30.0, 500, f"timeout: {str(e)}"))
        
        end_time = time.time()
        test_duration = end_time - start_time
        
        return self._calculate_metrics(results, test_duration)
    
    def _calculate_metrics(self, results: List[Tuple[float, int, str]], test_duration: float) -> PerformanceMetrics:
        """Calculate performance metrics from results."""
        if not results:
            return PerformanceMetrics(
                total_requests=0, successful_requests=0, failed_requests=0,
                average_response_time=0, min_response_time=0, max_response_time=0,
                median_response_time=0, p95_response_time=0, p99_response_time=0,
                requests_per_second=0, error_rate=0, test_duration=test_duration
            )
        
        response_times = [r[0] for r in results]
        status_codes = [r[1] for r in results]
        
        total_requests = len(results)
        successful_requests = len([s for s in status_codes if 200 <= s < 300])
        failed_requests = total_requests - successful_requests
        
        response_times.sort()
        
        return PerformanceMetrics(
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            average_response_time=statistics.mean(response_times),
            min_response_time=min(response_times),
            max_response_time=max(response_times),
            median_response_time=statistics.median(response_times),
            p95_response_time=response_times[int(0.95 * len(response_times))],
            p99_response_time=response_times[int(0.99 * len(response_times))],
            requests_per_second=total_requests / test_duration if test_duration > 0 else 0,
            error_rate=(failed_requests / total_requests) * 100 if total_requests > 0 else 0,
            test_duration=test_duration
        )


class TestLoadPerformance:
    """Load testing and performance validation test suite."""
    
    @pytest.fixture
    def server_config(self):
        """Create test server configuration."""
        return ServerConfig(
            host="localhost",
            port=8003,  # Different port for load testing
            debug=False,  # Production mode for realistic testing
            gemini_api_key="test_gemini_key",
            max_budget=150.0,
            default_family_size=4
        )
    
    @pytest.fixture
    async def bruno_server(self, server_config):
        """Create and initialize Bruno AI server for testing."""
        server = BrunoAIServer(server_config)
        await server.initialize()
        return server
    
    @pytest.fixture
    def test_client(self, bruno_server):
        """Create test client for API testing."""
        return TestClient(bruno_server.app)
    
    @pytest.fixture
    def load_runner(self, test_client):
        """Create load test runner."""
        return LoadTestRunner(test_client)
    
    def test_health_endpoint_load(self, load_runner):
        """Test health endpoint under load."""
        # Generate 100 health check requests
        requests = [("GET", "/health", None) for _ in range(100)]
        
        metrics = load_runner.run_concurrent_requests(requests, max_workers=20)
        
        # Assertions for health endpoint performance
        assert metrics.total_requests == 100
        assert metrics.error_rate < 5.0, f"Error rate too high: {metrics.error_rate}%"
        assert metrics.average_response_time < 1.0, f"Average response time too slow: {metrics.average_response_time}s"
        assert metrics.p95_response_time < 2.0, f"95th percentile too slow: {metrics.p95_response_time}s"
        assert metrics.requests_per_second > 10, f"Throughput too low: {metrics.requests_per_second} RPS"
        
        print(f"Health Endpoint Load Test Results:")
        print(f"  Total Requests: {metrics.total_requests}")
        print(f"  Success Rate: {100 - metrics.error_rate:.1f}%")
        print(f"  Average Response Time: {metrics.average_response_time:.3f}s")
        print(f"  95th Percentile: {metrics.p95_response_time:.3f}s")
        print(f"  Throughput: {metrics.requests_per_second:.1f} RPS")
    
    def test_api_docs_load(self, load_runner):
        """Test API documentation endpoint under load."""
        # Generate 50 API docs requests (fewer since it's a heavier endpoint)
        requests = [("GET", "/docs", None) for _ in range(50)]
        
        metrics = load_runner.run_concurrent_requests(requests, max_workers=10)
        
        # Assertions for API docs performance
        assert metrics.total_requests == 50
        assert metrics.error_rate < 10.0, f"Error rate too high: {metrics.error_rate}%"
        assert metrics.average_response_time < 3.0, f"Average response time too slow: {metrics.average_response_time}s"
        assert metrics.p95_response_time < 5.0, f"95th percentile too slow: {metrics.p95_response_time}s"
        
        print(f"API Docs Load Test Results:")
        print(f"  Total Requests: {metrics.total_requests}")
        print(f"  Success Rate: {100 - metrics.error_rate:.1f}%")
        print(f"  Average Response Time: {metrics.average_response_time:.3f}s")
        print(f"  95th Percentile: {metrics.p95_response_time:.3f}s")
        print(f"  Throughput: {metrics.requests_per_second:.1f} RPS")
    
    def test_chat_endpoint_load(self, load_runner):
        """Test chat endpoint under load."""
        # Generate 30 chat requests (fewer due to processing complexity)
        chat_data = {
            "message": "Hello, can you help me with a quick question?",
            "agent_name": "bruno_master"
        }
        requests = [("POST", "/api/v1/chat", chat_data) for _ in range(30)]
        
        metrics = load_runner.run_concurrent_requests(requests, max_workers=5)
        
        # More lenient assertions for chat endpoint (complex processing)
        assert metrics.total_requests == 30
        assert metrics.error_rate < 20.0, f"Error rate too high: {metrics.error_rate}%"
        assert metrics.average_response_time < 10.0, f"Average response time too slow: {metrics.average_response_time}s"
        assert metrics.p95_response_time < 20.0, f"95th percentile too slow: {metrics.p95_response_time}s"
        
        print(f"Chat Endpoint Load Test Results:")
        print(f"  Total Requests: {metrics.total_requests}")
        print(f"  Success Rate: {100 - metrics.error_rate:.1f}%")
        print(f"  Average Response Time: {metrics.average_response_time:.3f}s")
        print(f"  95th Percentile: {metrics.p95_response_time:.3f}s")
        print(f"  Throughput: {metrics.requests_per_second:.1f} RPS")
    
    def test_mixed_endpoint_load(self, load_runner):
        """Test mixed endpoint load to simulate realistic traffic."""
        requests = []
        
        # 60% health checks
        requests.extend([("GET", "/health", None) for _ in range(60)])
        
        # 20% API docs
        requests.extend([("GET", "/docs", None) for _ in range(20)])
        
        # 15% chat requests
        chat_data = {"message": "Test message", "agent_name": "bruno_master"}
        requests.extend([("POST", "/api/v1/chat", chat_data) for _ in range(15)])
        
        # 5% meal plan requests
        meal_plan_data = {
            "user_id": "load_test_user",
            "message": "I need a meal plan",
            "budget_limit": 100.0,
            "family_size": 4
        }
        requests.extend([("POST", "/api/v1/meal-plan?days=3&meals_per_day=3", meal_plan_data) for _ in range(5)])
        
        # Shuffle to simulate realistic traffic patterns
        import random
        random.shuffle(requests)
        
        metrics = load_runner.run_concurrent_requests(requests, max_workers=15)
        
        # Assertions for mixed load
        assert metrics.total_requests == 100
        assert metrics.error_rate < 15.0, f"Error rate too high: {metrics.error_rate}%"
        assert metrics.average_response_time < 5.0, f"Average response time too slow: {metrics.average_response_time}s"
        
        print(f"Mixed Load Test Results:")
        print(f"  Total Requests: {metrics.total_requests}")
        print(f"  Success Rate: {100 - metrics.error_rate:.1f}%")
        print(f"  Average Response Time: {metrics.average_response_time:.3f}s")
        print(f"  95th Percentile: {metrics.p95_response_time:.3f}s")
        print(f"  Throughput: {metrics.requests_per_second:.1f} RPS")
    
    def test_sustained_load(self, load_runner):
        """Test server under sustained load over time."""
        # Run requests over 60 seconds
        duration = 60  # seconds
        requests_per_second = 2
        
        start_time = time.time()
        all_requests = []
        
        while time.time() - start_time < duration:
            # Add health check requests
            all_requests.extend([("GET", "/health", None) for _ in range(requests_per_second)])
            
            # Occasionally add chat requests
            if len(all_requests) % 10 == 0:
                chat_data = {"message": "Sustained load test", "agent_name": "bruno_master"}
                all_requests.append(("POST", "/api/v1/chat", chat_data))
            
            time.sleep(1)
        
        metrics = load_runner.run_concurrent_requests(all_requests, max_workers=10)
        
        # Assertions for sustained load
        assert metrics.error_rate < 10.0, f"Error rate too high during sustained load: {metrics.error_rate}%"
        assert metrics.average_response_time < 3.0, f"Average response time degraded: {metrics.average_response_time}s"
        
        print(f"Sustained Load Test Results ({duration}s):")
        print(f"  Total Requests: {metrics.total_requests}")
        print(f"  Success Rate: {100 - metrics.error_rate:.1f}%")
        print(f"  Average Response Time: {metrics.average_response_time:.3f}s")
        print(f"  Throughput: {metrics.requests_per_second:.1f} RPS")
    
    def test_burst_load(self, load_runner):
        """Test server handling of burst traffic."""
        # Simulate traffic bursts
        burst_requests = []
        
        # First burst: 50 health checks
        burst_requests.extend([("GET", "/health", None) for _ in range(50)])
        
        # Second burst: 20 chat requests
        chat_data = {"message": "Burst test", "agent_name": "bruno_master"}
        burst_requests.extend([("POST", "/api/v1/chat", chat_data) for _ in range(20)])
        
        # Third burst: 30 mixed requests
        burst_requests.extend([("GET", "/health", None) for _ in range(15)])
        burst_requests.extend([("GET", "/docs", None) for _ in range(10)])
        burst_requests.extend([("POST", "/api/v1/chat", chat_data) for _ in range(5)])
        
        metrics = load_runner.run_concurrent_requests(burst_requests, max_workers=25)
        
        # Assertions for burst load
        assert metrics.total_requests == 100
        assert metrics.error_rate < 20.0, f"Error rate too high during burst: {metrics.error_rate}%"
        assert metrics.p99_response_time < 30.0, f"99th percentile too slow during burst: {metrics.p99_response_time}s"
        
        print(f"Burst Load Test Results:")
        print(f"  Total Requests: {metrics.total_requests}")
        print(f"  Success Rate: {100 - metrics.error_rate:.1f}%")
        print(f"  Average Response Time: {metrics.average_response_time:.3f}s")
        print(f"  99th Percentile: {metrics.p99_response_time:.3f}s")
        print(f"  Throughput: {metrics.requests_per_second:.1f} RPS")
    
    def test_memory_usage_under_load(self, load_runner):
        """Test memory usage doesn't grow excessively under load."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Run moderate load
        requests = [("GET", "/health", None) for _ in range(200)]
        chat_data = {"message": "Memory test", "agent_name": "bruno_master"}
        requests.extend([("POST", "/api/v1/chat", chat_data) for _ in range(20)])
        
        metrics = load_runner.run_concurrent_requests(requests, max_workers=10)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        memory_increase_mb = memory_increase / (1024 * 1024)
        
        print(f"Memory Usage Test Results:")
        print(f"  Initial Memory: {initial_memory / (1024 * 1024):.1f} MB")
        print(f"  Final Memory: {final_memory / (1024 * 1024):.1f} MB")
        print(f"  Memory Increase: {memory_increase_mb:.1f} MB")
        print(f"  Requests Processed: {metrics.total_requests}")
        
        # Assert memory increase is reasonable (less than 200MB for this test)
        assert memory_increase_mb < 200, f"Excessive memory usage: {memory_increase_mb:.1f} MB increase"
    
    def test_error_rate_under_load(self, load_runner):
        """Test error rates remain acceptable under various load conditions."""
        test_scenarios = [
            ("Light Load", [("GET", "/health", None)] * 50, 5),
            ("Medium Load", [("GET", "/health", None)] * 100, 10),
            ("Heavy Load", [("GET", "/health", None)] * 200, 20),
        ]
        
        for scenario_name, requests, max_workers in test_scenarios:
            metrics = load_runner.run_concurrent_requests(requests, max_workers=max_workers)
            
            print(f"{scenario_name} Results:")
            print(f"  Error Rate: {metrics.error_rate:.1f}%")
            print(f"  Average Response Time: {metrics.average_response_time:.3f}s")
            print(f"  Throughput: {metrics.requests_per_second:.1f} RPS")
            
            # Error rate should remain low even under heavy load
            assert metrics.error_rate < 15.0, f"{scenario_name}: Error rate too high: {metrics.error_rate}%"
    
    def test_response_time_consistency(self, load_runner):
        """Test response time consistency under load."""
        # Run multiple batches and check consistency
        batch_metrics = []
        
        for batch in range(5):
            requests = [("GET", "/health", None) for _ in range(20)]
            metrics = load_runner.run_concurrent_requests(requests, max_workers=5)
            batch_metrics.append(metrics.average_response_time)
            
            print(f"Batch {batch + 1} Average Response Time: {metrics.average_response_time:.3f}s")
        
        # Check response time consistency (standard deviation should be reasonable)
        avg_response_time = statistics.mean(batch_metrics)
        response_time_std = statistics.stdev(batch_metrics) if len(batch_metrics) > 1 else 0
        
        print(f"Response Time Consistency:")
        print(f"  Average: {avg_response_time:.3f}s")
        print(f"  Standard Deviation: {response_time_std:.3f}s")
        
        # Standard deviation should be less than 50% of average
        assert response_time_std < (avg_response_time * 0.5), f"Response times too inconsistent: {response_time_std:.3f}s std dev"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main(["-v", "-s", __file__])