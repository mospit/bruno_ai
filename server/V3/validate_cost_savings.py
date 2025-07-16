#!/usr/bin/env python3
"""
Production Cost Savings Validation Script - Bruno AI V3.1
Validates that the token management system is achieving 25-40% cost savings
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from pathlib import Path
import statistics

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from token_manager import TokenManager, ModelType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CostSavingsValidator:
    """Validates cost savings metrics for token management system"""
    
    def __init__(self):
        self.test_scenarios = [
            {
                "name": "Simple Query Set",
                "queries": [
                    "Find chicken recipes",
                    "Show me beef prices",
                    "List vegetarian options",
                    "Get today's deals",
                    "What's in stock?"
                ],
                "expected_model": ModelType.HAIKU,
                "expected_savings": 35  # % savings from using Haiku vs always Sonnet
            },
            {
                "name": "Complex Query Set", 
                "queries": [
                    "Analyze my spending patterns over the last 3 months and provide detailed budget optimization recommendations",
                    "Create a comprehensive 7-day meal plan that optimizes for a $200 budget with gluten-free restrictions",
                    "Compare the nutritional value and cost-effectiveness of organic vs conventional produce",
                    "Develop a strategic shopping plan that minimizes cost while maximizing nutritional value",
                    "Forecast my monthly food expenses based on historical data and seasonal price variations"
                ],
                "expected_model": ModelType.SONNET,
                "expected_savings": 25  # % savings from compression and optimization
            },
            {
                "name": "Mixed Workload",
                "queries": [
                    "Find pasta recipes",  # Simple -> Haiku
                    "Analyze my budget trends and recommend optimizations",  # Complex -> Sonnet
                    "Show me chicken prices",  # Simple -> Haiku
                    "Create a meal plan for family of 4 with $150 budget and dietary restrictions",  # Complex -> Sonnet
                    "List dairy products",  # Simple -> Haiku
                    "Compare cost efficiency of different protein sources with detailed analysis",  # Complex -> Sonnet
                    "Check stock levels",  # Simple -> Haiku
                    "Optimize shopping schedule based on store promotions and family preferences"  # Complex -> Sonnet
                ],
                "expected_model": "mixed",
                "expected_savings": 30  # % savings from intelligent routing
            }
        ]
    
    def create_mock_token_manager(self) -> TokenManager:
        """Create a mock token manager for testing"""
        from unittest.mock import MagicMock, AsyncMock, patch
        
        # Create a TokenManager instance without calling __init__
        token_manager = TokenManager.__new__(TokenManager)
        
        # Initialize only the necessary attributes for testing
        token_manager.COMPRESSION_THRESHOLD = 4000
        token_manager.HAIKU_THRESHOLD = 2000
        token_manager.COST_PER_1K_TOKENS = {
            ModelType.HAIKU: 0.00025,  # $0.25 per 1M tokens
            ModelType.SONNET: 0.003    # $3 per 1M tokens
        }
        
        # Mock the dependencies
        token_manager.redis_client = AsyncMock()
        token_manager.postgres_conn = MagicMock()
        token_manager.anthropic_client = AsyncMock()
        token_manager.logger = MagicMock()
        
        # Mock the _log_metrics method to avoid database calls
        token_manager._log_metrics = AsyncMock()
        
        return token_manager
    
    def calculate_baseline_cost(self, queries: List[str], model: ModelType) -> float:
        """Calculate baseline cost if all queries used the same model"""
        token_manager = self.create_mock_token_manager()
        total_cost = 0
        
        for query in queries:
            tokens = token_manager.estimate_tokens(query)
            cost = (tokens / 1000) * token_manager.COST_PER_1K_TOKENS[model]
            total_cost += cost
        
        return total_cost
    
    def calculate_optimized_cost(self, queries: List[str]) -> Tuple[float, Dict[str, Any]]:
        """Calculate optimized cost with intelligent routing"""
        token_manager = self.create_mock_token_manager()
        total_cost = 0
        routing_stats = {"haiku_count": 0, "sonnet_count": 0, "total_queries": len(queries)}
        
        for query in queries:
            complexity = token_manager.analyze_query_complexity(query)
            model = complexity.recommended_model
            
            # Track routing decisions
            if model == ModelType.HAIKU:
                routing_stats["haiku_count"] += 1
            else:
                routing_stats["sonnet_count"] += 1
            
            cost = (complexity.token_estimate / 1000) * token_manager.COST_PER_1K_TOKENS[model]
            total_cost += cost
        
        routing_stats["haiku_percentage"] = (routing_stats["haiku_count"] / routing_stats["total_queries"]) * 100
        routing_stats["sonnet_percentage"] = (routing_stats["sonnet_count"] / routing_stats["total_queries"]) * 100
        
        return total_cost, routing_stats
    
    def validate_compression_savings(self, queries: List[str]) -> Dict[str, Any]:
        """Validate compression savings for long queries"""
        token_manager = self.create_mock_token_manager()
        compression_stats = {
            "queries_tested": 0,
            "queries_compressed": 0,
            "total_original_tokens": 0,
            "total_compressed_tokens": 0,
            "compression_ratio": 0,
            "cost_savings": 0
        }
        
        for query in queries:
            original_tokens = token_manager.estimate_tokens(query)
            compression_stats["queries_tested"] += 1
            compression_stats["total_original_tokens"] += original_tokens
            
            # Simulate compression for queries above threshold
            if original_tokens > token_manager.COMPRESSION_THRESHOLD:
                compression_stats["queries_compressed"] += 1
                # Simulate 50% compression ratio
                compressed_tokens = int(original_tokens * 0.5)
                compression_stats["total_compressed_tokens"] += compressed_tokens
            else:
                compression_stats["total_compressed_tokens"] += original_tokens
        
        if compression_stats["total_original_tokens"] > 0:
            compression_stats["compression_ratio"] = compression_stats["total_compressed_tokens"] / compression_stats["total_original_tokens"]
            compression_stats["cost_savings"] = (1 - compression_stats["compression_ratio"]) * 100
        
        return compression_stats
    
    def run_cost_analysis(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run cost analysis for a specific scenario"""
        queries = scenario["queries"]
        
        # Calculate baseline costs (if we always used the most expensive model)
        baseline_cost_sonnet = self.calculate_baseline_cost(queries, ModelType.SONNET)
        baseline_cost_haiku = self.calculate_baseline_cost(queries, ModelType.HAIKU)
        
        # Calculate optimized cost with intelligent routing
        optimized_cost, routing_stats = self.calculate_optimized_cost(queries)
        
        # Calculate compression savings
        compression_stats = self.validate_compression_savings(queries)
        
        # Calculate savings percentages
        savings_vs_sonnet = ((baseline_cost_sonnet - optimized_cost) / baseline_cost_sonnet) * 100
        savings_vs_haiku = ((baseline_cost_haiku - optimized_cost) / baseline_cost_haiku) * 100
        
        # Use the more conservative comparison (vs the cheaper baseline)
        actual_savings = min(savings_vs_sonnet, abs(savings_vs_haiku)) if savings_vs_haiku < 0 else savings_vs_sonnet
        
        return {
            "scenario": scenario["name"],
            "baseline_cost_sonnet": baseline_cost_sonnet,
            "baseline_cost_haiku": baseline_cost_haiku,
            "optimized_cost": optimized_cost,
            "savings_vs_sonnet": savings_vs_sonnet,
            "savings_vs_haiku": savings_vs_haiku,
            "actual_savings": actual_savings,
            "expected_savings": scenario["expected_savings"],
            "meets_target": actual_savings >= 25,  # Minimum target
            "routing_stats": routing_stats,
            "compression_stats": compression_stats
        }
    
    def generate_production_report(self) -> Dict[str, Any]:
        """Generate comprehensive production cost savings report"""
        logger.info("🚀 Starting Production Cost Savings Validation")
        
        results = []
        overall_savings = []
        
        for scenario in self.test_scenarios:
            logger.info(f"📊 Analyzing scenario: {scenario['name']}")
            result = self.run_cost_analysis(scenario)
            results.append(result)
            overall_savings.append(result["actual_savings"])
            
            # Log scenario results
            logger.info(f"  Baseline cost (Sonnet): ${result['baseline_cost_sonnet']:.6f}")
            logger.info(f"  Optimized cost: ${result['optimized_cost']:.6f}")
            logger.info(f"  Actual savings: {result['actual_savings']:.1f}%")
            logger.info(f"  Expected savings: {result['expected_savings']:.1f}%")
            logger.info(f"  Meets target: {'✅' if result['meets_target'] else '❌'}")
            logger.info(f"  Routing: {result['routing_stats']['haiku_percentage']:.1f}% Haiku, {result['routing_stats']['sonnet_percentage']:.1f}% Sonnet")
        
        # Calculate overall metrics
        avg_savings = statistics.mean(overall_savings)
        min_savings = min(overall_savings)
        max_savings = max(overall_savings)
        
        # Determine if we meet the 25-40% target
        meets_minimum = min_savings >= 25
        within_range = 25 <= avg_savings <= 40
        
        report = {
            "validation_date": datetime.now().isoformat(),
            "target_savings_range": "25-40%",
            "results": results,
            "overall_metrics": {
                "average_savings": avg_savings,
                "minimum_savings": min_savings,
                "maximum_savings": max_savings,
                "meets_minimum_target": meets_minimum,
                "within_target_range": within_range,
                "scenarios_meeting_target": sum(1 for r in results if r["meets_target"])
            },
            "validation_status": "PASS" if meets_minimum else "FAIL",
            "recommendations": []
        }
        
        # Add recommendations
        if not meets_minimum:
            report["recommendations"].append("Cost savings below 25% minimum target. Consider adjusting routing thresholds.")
        
        if avg_savings > 40:
            report["recommendations"].append("Savings exceed 40% target. Consider if this indicates too aggressive cost-cutting.")
        
        if within_range and meets_minimum:
            report["recommendations"].append("Cost savings within target range. System is performing optimally.")
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: str = "cost_savings_validation_report.json"):
        """Save the validation report to a file"""
        report_path = Path(__file__).parent / filename
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"📄 Report saved to: {report_path}")
        return report_path
    
    def print_summary(self, report: Dict[str, Any]):
        """Print a summary of the validation results"""
        print("\n" + "="*80)
        print("🎯 PRODUCTION COST SAVINGS VALIDATION SUMMARY")
        print("="*80)
        print(f"Target Range: {report['target_savings_range']}")
        print(f"Validation Status: {report['validation_status']}")
        print(f"Validation Date: {report['validation_date']}")
        print("\n📊 Overall Metrics:")
        print(f"  Average Savings: {report['overall_metrics']['average_savings']:.1f}%")
        print(f"  Minimum Savings: {report['overall_metrics']['minimum_savings']:.1f}%")
        print(f"  Maximum Savings: {report['overall_metrics']['maximum_savings']:.1f}%")
        print(f"  Scenarios Meeting Target: {report['overall_metrics']['scenarios_meeting_target']}/{len(report['results'])}")
        
        print("\n🔍 Scenario Results:")
        for result in report['results']:
            status = "✅ PASS" if result['meets_target'] else "❌ FAIL"
            print(f"  {result['scenario']}: {result['actual_savings']:.1f}% savings {status}")
        
        if report['recommendations']:
            print("\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"  • {rec}")
        
        print("="*80)

def main():
    """Main validation function"""
    validator = CostSavingsValidator()
    
    # Generate validation report
    report = validator.generate_production_report()
    
    # Save report
    report_path = validator.save_report(report)
    
    # Print summary
    validator.print_summary(report)
    
    # Exit with appropriate code
    if report['validation_status'] == "PASS":
        print("\n🎉 Validation PASSED: Cost savings meet the 25-40% target!")
        sys.exit(0)
    else:
        print("\n⚠️  Validation FAILED: Cost savings do not meet the minimum 25% target!")
        sys.exit(1)

if __name__ == "__main__":
    main()
