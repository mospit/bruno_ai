"""
Cost Optimization Testing Framework
Tests the system with realistic workloads to validate cost savings
"""

import asyncio
import json
import random
import time
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class TaskComplexity(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


class ModelType(Enum):
    FLASH_LITE = "gemini-2.5-flash-lite-preview-06-17"
    FLASH = "gemini-2.5-flash"
    PRO = "gemini-2.5-pro"


@dataclass
class TestResult:
    task_type: str
    complexity: TaskComplexity
    model_used: ModelType
    input_tokens: int
    output_tokens: int
    processing_time: float
    estimated_cost: float
    was_cached: bool
    was_batched: bool


class CostCalculator:
    """Calculate costs based on Gemini pricing"""
    
    MODEL_PRICING = {
        ModelType.FLASH_LITE: {"input": 0.10, "output": 0.40},
        ModelType.FLASH: {"input": 0.30, "output": 2.50},
        ModelType.PRO: {"input": 1.25, "output": 10.00}
    }
    
    @classmethod
    def calculate_cost(cls, model: ModelType, input_tokens: int, output_tokens: int, 
                      was_batched: bool = False) -> float:
        pricing = cls.MODEL_PRICING[model]
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost
        
        # Apply batch discount
        if was_batched:
            total_cost *= 0.5
            
        return total_cost


class MockModelRouter:
    """Mock implementation of the ModelRouter for testing"""
    
    TASK_ROUTING = {
        # Simple tasks
        "pantry_update": TaskComplexity.SIMPLE,
        "inventory_check": TaskComplexity.SIMPLE,
        "simple_query": TaskComplexity.SIMPLE,
        "status_check": TaskComplexity.SIMPLE,
        
        # Moderate tasks
        "product_search": TaskComplexity.MODERATE,
        "price_comparison": TaskComplexity.MODERATE,
        "shopping_list_creation": TaskComplexity.MODERATE,
        "basic_meal_planning": TaskComplexity.MODERATE,
        
        # Complex tasks
        "advanced_meal_planning": TaskComplexity.COMPLEX,
        "budget_optimization": TaskComplexity.COMPLEX,
        "nutritional_analysis": TaskComplexity.COMPLEX,
        "recipe_generation": TaskComplexity.COMPLEX,
    }
    
    COMPLEXITY_TO_MODEL = {
        TaskComplexity.SIMPLE: ModelType.FLASH_LITE,
        TaskComplexity.MODERATE: ModelType.FLASH,
        TaskComplexity.COMPLEX: ModelType.FLASH
    }
    
    def get_model_for_task(self, task_type: str) -> ModelType:
        complexity = self.TASK_ROUTING.get(task_type, TaskComplexity.MODERATE)
        return self.COMPLEXITY_TO_MODEL[complexity]
    
    def get_complexity(self, task_type: str) -> TaskComplexity:
        return self.TASK_ROUTING.get(task_type, TaskComplexity.MODERATE)


class WorkloadGenerator:
    """Generate realistic workloads for testing"""
    
    def __init__(self):
        self.router = MockModelRouter()
        
        # Realistic token ranges for different task types
        self.token_ranges = {
            TaskComplexity.SIMPLE: {"input": (50, 200), "output": (100, 300)},
            TaskComplexity.MODERATE: {"input": (200, 500), "output": (300, 800)},
            TaskComplexity.COMPLEX: {"input": (500, 1200), "output": (800, 2000)}
        }
    
    def generate_realistic_workload(self, num_tasks: int = 100) -> List[Dict[str, Any]]:
        """Generate a realistic mix of tasks based on typical user behavior"""
        
        # Realistic distribution based on typical app usage
        task_distribution = {
            # Simple tasks (40% of usage)
            "pantry_update": 15,
            "inventory_check": 10,
            "simple_query": 10,
            "status_check": 5,
            
            # Moderate tasks (45% of usage)
            "product_search": 20,
            "shopping_list_creation": 15,
            "basic_meal_planning": 10,
            
            # Complex tasks (15% of usage)
            "advanced_meal_planning": 8,
            "budget_optimization": 4,
            "nutritional_analysis": 2,
            "recipe_generation": 1
        }
        
        workload = []
        
        # Generate tasks based on distribution
        for task_type, percentage in task_distribution.items():
            task_count = int((percentage / 100) * num_tasks)
            
            for _ in range(task_count):
                complexity = self.router.get_complexity(task_type)
                token_range = self.token_ranges[complexity]
                
                # Add some randomness to token counts
                input_tokens = random.randint(*token_range["input"])
                output_tokens = random.randint(*token_range["output"])
                
                # Simulate caching (20% cache hit rate for user context)
                was_cached = random.random() < 0.20
                
                # Simulate batch processing for eligible tasks
                batchable_tasks = ["advanced_meal_planning", "budget_optimization", "nutritional_analysis"]
                was_batched = task_type in batchable_tasks and random.random() < 0.70
                
                workload.append({
                    "task_type": task_type,
                    "complexity": complexity,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "was_cached": was_cached,
                    "was_batched": was_batched,
                    "user_id": f"user_{random.randint(1, 50)}"  # Simulate 50 users
                })
        
        return workload


class CostOptimizationTester:
    """Main testing framework for cost optimization"""
    
    def __init__(self):
        self.router = MockModelRouter()
        self.workload_generator = WorkloadGenerator()
        self.results = []
    
    async def simulate_task_processing(self, task: Dict[str, Any]) -> TestResult:
        """Simulate processing a single task"""
        
        # Determine model to use
        model = self.router.get_model_for_task(task["task_type"])
        
        # Simulate processing time (more complex tasks take longer)
        complexity = task["complexity"]
        if complexity == TaskComplexity.SIMPLE:
            processing_time = random.uniform(0.1, 0.3)
        elif complexity == TaskComplexity.MODERATE:
            processing_time = random.uniform(0.3, 0.8)
        else:
            processing_time = random.uniform(0.8, 2.0)
        
        # Simulate caching speedup
        if task["was_cached"]:
            processing_time *= 0.3  # 70% time savings from cache
        
        # Simulate batch processing delay but cost savings
        if task["was_batched"]:
            processing_time += random.uniform(60, 300)  # Batch delay
        
        await asyncio.sleep(processing_time / 1000)  # Scale down for testing
        
        # Calculate cost
        estimated_cost = CostCalculator.calculate_cost(
            model, 
            task["input_tokens"], 
            task["output_tokens"],
            task["was_batched"]
        )
        
        return TestResult(
            task_type=task["task_type"],
            complexity=task["complexity"],
            model_used=model,
            input_tokens=task["input_tokens"],
            output_tokens=task["output_tokens"],
            processing_time=processing_time,
            estimated_cost=estimated_cost,
            was_cached=task["was_cached"],
            was_batched=task["was_batched"]
        )
    
    async def run_workload_test(self, num_tasks: int = 100) -> Dict[str, Any]:
        """Run a complete workload test"""
        
        print(f"🚀 Starting workload test with {num_tasks} tasks...")
        start_time = time.time()
        
        # Generate workload
        workload = self.workload_generator.generate_realistic_workload(num_tasks)
        
        # Process tasks
        results = []
        for i, task in enumerate(workload):
            if i % 10 == 0:
                print(f"  Processing task {i+1}/{len(workload)}...")
            
            result = await self.simulate_task_processing(task)
            results.append(result)
        
        total_time = time.time() - start_time
        
        # Analyze results
        analysis = self.analyze_results(results)
        analysis["test_duration"] = total_time
        analysis["tasks_processed"] = len(results)
        
        return analysis
    
    def analyze_results(self, results: List[TestResult]) -> Dict[str, Any]:
        """Analyze test results and calculate savings"""
        
        if not results:
            return {"error": "No results to analyze"}
        
        # Calculate totals
        total_cost = sum(r.estimated_cost for r in results)
        total_input_tokens = sum(r.input_tokens for r in results)
        total_output_tokens = sum(r.output_tokens for r in results)
        
        # Model usage breakdown
        model_usage = {}
        for result in results:
            model = result.model_used.value
            if model not in model_usage:
                model_usage[model] = {"count": 0, "cost": 0.0}
            model_usage[model]["count"] += 1
            model_usage[model]["cost"] += result.estimated_cost
        
        # Calculate what costs would be without optimization
        baseline_cost = 0.0
        for result in results:
            # Assume all tasks would use Flash model without optimization
            baseline_cost += CostCalculator.calculate_cost(
                ModelType.FLASH, 
                result.input_tokens, 
                result.output_tokens,
                was_batched=False
            )
        
        # Optimization impact
        cached_results = [r for r in results if r.was_cached]
        batched_results = [r for r in results if r.was_batched]
        flash_lite_results = [r for r in results if r.model_used == ModelType.FLASH_LITE]
        
        # Calculate savings
        total_savings = baseline_cost - total_cost
        savings_percentage = (total_savings / baseline_cost) * 100 if baseline_cost > 0 else 0
        
        # Detailed breakdown
        flash_lite_savings = sum(
            CostCalculator.calculate_cost(ModelType.FLASH, r.input_tokens, r.output_tokens) - r.estimated_cost
            for r in flash_lite_results
        )
        
        batch_savings = sum(r.estimated_cost for r in batched_results)  # Already discounted
        
        return {
            "cost_analysis": {
                "total_cost": f"${total_cost:.4f}",
                "baseline_cost": f"${baseline_cost:.4f}",
                "total_savings": f"${total_savings:.4f}",
                "savings_percentage": f"{savings_percentage:.1f}%"
            },
            "token_usage": {
                "total_input_tokens": f"{total_input_tokens:,}",
                "total_output_tokens": f"{total_output_tokens:,}",
                "total_tokens": f"{total_input_tokens + total_output_tokens:,}"
            },
            "model_distribution": {
                model: {
                    "tasks": data["count"],
                    "percentage": f"{(data['count'] / len(results)) * 100:.1f}%",
                    "cost": f"${data['cost']:.4f}"
                }
                for model, data in model_usage.items()
            },
            "optimization_impact": {
                "flash_lite_usage": f"{len(flash_lite_results)} tasks ({(len(flash_lite_results)/len(results)*100):.1f}%)",
                "flash_lite_savings": f"${flash_lite_savings:.4f}",
                "cached_requests": f"{len(cached_results)} tasks ({(len(cached_results)/len(results)*100):.1f}%)",
                "batched_requests": f"{len(batched_results)} tasks ({(len(batched_results)/len(results)*100):.1f}%)",
                "batch_savings": f"${batch_savings:.4f}"
            },
            "cost_per_user_per_month": {
                "optimized": f"${(total_cost * 30):.2f}",  # Assuming daily usage
                "baseline": f"${(baseline_cost * 30):.2f}",
                "monthly_savings": f"${((baseline_cost - total_cost) * 30):.2f}"
            }
        }
    
    def print_analysis(self, analysis: Dict[str, Any]):
        """Print detailed analysis in a readable format"""
        
        print("\n" + "="*60)
        print("📊 COST OPTIMIZATION TEST RESULTS")
        print("="*60)
        
        print(f"\n⏱️  Test Duration: {analysis['test_duration']:.2f} seconds")
        print(f"📋 Tasks Processed: {analysis['tasks_processed']}")
        
        cost = analysis["cost_analysis"]
        print(f"\n💰 COST ANALYSIS:")
        print(f"   Total Cost (Optimized): {cost['total_cost']}")
        print(f"   Baseline Cost (No Optimization): {cost['baseline_cost']}")
        print(f"   Total Savings: {cost['total_savings']}")
        print(f"   Savings Percentage: {cost['savings_percentage']}")
        
        tokens = analysis["token_usage"]
        print(f"\n🔢 TOKEN USAGE:")
        print(f"   Input Tokens: {tokens['total_input_tokens']}")
        print(f"   Output Tokens: {tokens['total_output_tokens']}")
        print(f"   Total Tokens: {tokens['total_tokens']}")
        
        print(f"\n🤖 MODEL DISTRIBUTION:")
        for model, data in analysis["model_distribution"].items():
            print(f"   {model}: {data['tasks']} tasks ({data['percentage']}) - {data['cost']}")
        
        opt = analysis["optimization_impact"]
        print(f"\n⚡ OPTIMIZATION IMPACT:")
        print(f"   Flash Lite Usage: {opt['flash_lite_usage']}")
        print(f"   Flash Lite Savings: {opt['flash_lite_savings']}")
        print(f"   Cached Requests: {opt['cached_requests']}")
        print(f"   Batched Requests: {opt['batched_requests']}")
        print(f"   Batch Savings: {opt['batch_savings']}")
        
        monthly = analysis["cost_per_user_per_month"]
        print(f"\n📅 MONTHLY COST PROJECTION:")
        print(f"   Optimized Cost/User: {monthly['optimized']}")
        print(f"   Baseline Cost/User: {monthly['baseline']}")
        print(f"   Monthly Savings/User: {monthly['monthly_savings']}")
        
        print("\n" + "="*60)


async def main():
    """Run the cost optimization test"""
    
    tester = CostOptimizationTester()
    
    # Run different test scenarios
    scenarios = [
        {"name": "Light Usage", "tasks": 50},
        {"name": "Medium Usage", "tasks": 200},
        {"name": "Heavy Usage", "tasks": 500}
    ]
    
    for scenario in scenarios:
        print(f"\n🧪 Running {scenario['name']} scenario...")
        analysis = await tester.run_workload_test(scenario["tasks"])
        
        print(f"\n📈 Results for {scenario['name']}:")
        tester.print_analysis(analysis)
        
        # Save results to file
        filename = f"cost_test_results_{scenario['name'].lower().replace(' ', '_')}.json"
        with open(filename, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"\n💾 Results saved to {filename}")


if __name__ == "__main__":
    print("🚀 Starting Bruno AI Cost Optimization Test Suite")
    asyncio.run(main())
