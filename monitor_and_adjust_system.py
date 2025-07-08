"""
Cost Optimization Monitoring and Adjustment System
Monitors metrics and automatically adjusts routing rules based on usage patterns
"""

import asyncio
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class OptimizationAction(Enum):
    DOWNGRADE_MODEL = "downgrade_model"
    UPGRADE_MODEL = "upgrade_model"
    ENABLE_BATCHING = "enable_batching"
    ADJUST_CACHE_TTL = "adjust_cache_ttl"
    NO_ACTION = "no_action"


@dataclass
class MetricAlert:
    severity: str  # "low", "medium", "high"
    message: str
    recommended_action: OptimizationAction
    task_type: Optional[str] = None
    current_value: Optional[float] = None
    threshold: Optional[float] = None


class CostOptimizationMonitor:
    """Monitor cost optimization metrics and suggest adjustments"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.monitoring_config = {
            "cost_threshold_per_task": 0.001,  # $0.001 per task
            "flash_lite_usage_target": 0.40,  # 40% of tasks should use Flash Lite
            "cache_hit_rate_target": 0.25,    # 25% cache hit rate target
            "batch_usage_target": 0.15,       # 15% of eligible tasks should be batched
            "high_cost_task_threshold": 0.005, # Tasks costing more than $0.005
        }
        
        self.routing_adjustments = []
        self.alerts = []
    
    async def get_cost_metrics(self) -> Dict[str, Any]:
        """Fetch current cost metrics from the API"""
        try:
            response = requests.get(f"{self.api_base_url}/api/v1/cost-optimization/summary?days=7")
            if response.status_code == 200:
                return response.json()["data"]
            else:
                print(f"❌ Failed to fetch metrics: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ Error fetching metrics: {e}")
            return {}
    
    async def get_model_metrics(self) -> Dict[str, Any]:
        """Fetch model routing metrics"""
        try:
            response = requests.get(f"{self.api_base_url}/api/v1/cost-optimization/model-metrics")
            if response.status_code == 200:
                return response.json()
            else:
                return {}
        except Exception as e:
            print(f"❌ Error fetching model metrics: {e}")
            return {}
    
    async def get_batch_metrics(self) -> Dict[str, Any]:
        """Fetch batch processing metrics"""
        try:
            response = requests.get(f"{self.api_base_url}/api/v1/cost-optimization/batch-metrics")
            if response.status_code == 200:
                return response.json()
            else:
                return {}
        except Exception as e:
            print(f"❌ Error fetching batch metrics: {e}")
            return {}
    
    async def analyze_cost_trends(self, metrics: Dict[str, Any]) -> List[MetricAlert]:
        """Analyze cost trends and generate alerts"""
        alerts = []
        
        if not metrics or "cost_analysis" not in metrics:
            return alerts
        
        cost_analysis = metrics["cost_analysis"]
        
        # Parse cost values (remove $ and convert to float)
        try:
            total_cost = float(cost_analysis["total_cost"].replace("$", ""))
            baseline_cost = float(cost_analysis["baseline_cost"].replace("$", ""))
            savings_percentage = float(cost_analysis["savings_percentage"].replace("%", ""))
        except (ValueError, KeyError):
            print("❌ Unable to parse cost metrics")
            return alerts
        
        # Alert if savings are below target (should be > 20%)
        if savings_percentage < 20:
            alerts.append(MetricAlert(
                severity="medium",
                message=f"Cost savings below target: {savings_percentage:.1f}% (target: >20%)",
                recommended_action=OptimizationAction.DOWNGRADE_MODEL,
                current_value=savings_percentage,
                threshold=20.0
            ))\n        
        # Alert if total cost is too high per task\n        if \"tasks_processed\" in metrics:\n            cost_per_task = total_cost / metrics[\"tasks_processed\"]\n            if cost_per_task > self.monitoring_config[\"cost_threshold_per_task\"]:\n                alerts.append(MetricAlert(\n                    severity=\"high\",\n                    message=f\"Cost per task too high: ${cost_per_task:.4f} (threshold: ${self.monitoring_config['cost_threshold_per_task']:.4f})\",\n                    recommended_action=OptimizationAction.DOWNGRADE_MODEL,\n                    current_value=cost_per_task,\n                    threshold=self.monitoring_config[\"cost_threshold_per_task\"]\n                ))\n        \n        return alerts\n    \n    async def analyze_model_usage(self, model_metrics: Dict[str, Any]) -> List[MetricAlert]:\n        \"\"\"Analyze model usage patterns\"\"\"\n        alerts = []\n        \n        if not model_metrics or \"model_routing\" not in model_metrics:\n            return alerts\n        \n        routing_data = model_metrics[\"model_routing\"]\n        \n        # Check Flash Lite usage percentage\n        if \"model_distribution\" in routing_data:\n            distribution = routing_data[\"model_distribution\"]\n            flash_lite_percentage = float(distribution.get(\"flash_lite\", \"0%\").replace(\"%\", \"\"))\n            \n            target_percentage = self.monitoring_config[\"flash_lite_usage_target\"] * 100\n            \n            if flash_lite_percentage < target_percentage:\n                alerts.append(MetricAlert(\n                    severity=\"medium\",\n                    message=f\"Flash Lite usage below target: {flash_lite_percentage:.1f}% (target: {target_percentage:.1f}%)\",\n                    recommended_action=OptimizationAction.DOWNGRADE_MODEL,\n                    current_value=flash_lite_percentage,\n                    threshold=target_percentage\n                ))\n        \n        return alerts\n    \n    async def analyze_task_performance(self, metrics: Dict[str, Any]) -> List[MetricAlert]:\n        \"\"\"Analyze individual task performance\"\"\"\n        alerts = []\n        \n        if \"task_breakdown\" not in metrics:\n            return alerts\n        \n        task_breakdown = metrics[\"task_breakdown\"]\n        \n        # Identify expensive tasks that could be optimized\n        for task_type, data in task_breakdown.items():\n            try:\n                avg_cost = float(data[\"avg_cost\"].replace(\"$\", \"\"))\n                if avg_cost > self.monitoring_config[\"high_cost_task_threshold\"]:\n                    alerts.append(MetricAlert(\n                        severity=\"medium\",\n                        message=f\"Task '{task_type}' has high average cost: ${avg_cost:.4f}\",\n                        recommended_action=OptimizationAction.DOWNGRADE_MODEL,\n                        task_type=task_type,\n                        current_value=avg_cost,\n                        threshold=self.monitoring_config[\"high_cost_task_threshold\"]\n                    ))\n            except (ValueError, KeyError):\n                continue\n        \n        return alerts\n    \n    async def suggest_routing_adjustments(self, alerts: List[MetricAlert]) -> List[Dict[str, Any]]:\n        \"\"\"Suggest routing rule adjustments based on alerts\"\"\"\n        adjustments = []\n        \n        for alert in alerts:\n            if alert.recommended_action == OptimizationAction.DOWNGRADE_MODEL and alert.task_type:\n                adjustments.append({\n                    \"action\": \"downgrade_model\",\n                    \"task_type\": alert.task_type,\n                    \"from_complexity\": \"moderate\",\n                    \"to_complexity\": \"simple\",\n                    \"reason\": alert.message,\n                    \"estimated_savings\": f\"${(alert.current_value or 0) * 0.7:.4f}\"  # Estimate 70% savings\n                })\n            \n            elif alert.recommended_action == OptimizationAction.ENABLE_BATCHING:\n                adjustments.append({\n                    \"action\": \"enable_batching\",\n                    \"task_type\": alert.task_type or \"all_eligible\",\n                    \"reason\": alert.message,\n                    \"estimated_savings\": \"50% for batched tasks\"\n                })\n        \n        return adjustments\n    \n    async def apply_routing_adjustment(self, adjustment: Dict[str, Any]) -> bool:\n        \"\"\"Apply a routing rule adjustment via API\"\"\"\n        try:\n            if adjustment[\"action\"] == \"downgrade_model\":\n                response = requests.post(\n                    f\"{self.api_base_url}/api/v1/cost-optimization/configuration/model-routing\",\n                    params={\n                        \"task_type\": adjustment[\"task_type\"],\n                        \"complexity\": adjustment[\"to_complexity\"]\n                    }\n                )\n                return response.status_code == 200\n            \n            # Add other adjustment types as needed\n            return False\n            \n        except Exception as e:\n            print(f\"❌ Error applying adjustment: {e}\")\n            return False\n    \n    async def run_monitoring_cycle(self) -> Dict[str, Any]:\n        \"\"\"Run a complete monitoring and analysis cycle\"\"\"\n        print(\"🔍 Starting monitoring cycle...\")\n        \n        # Fetch all metrics\n        cost_metrics = await self.get_cost_metrics()\n        model_metrics = await self.get_model_metrics()\n        batch_metrics = await self.get_batch_metrics()\n        \n        if not cost_metrics:\n            return {\"error\": \"Unable to fetch cost metrics\"}\n        \n        # Analyze metrics\n        cost_alerts = await self.analyze_cost_trends(cost_metrics)\n        model_alerts = await self.analyze_model_usage(model_metrics)\n        task_alerts = await self.analyze_task_performance(cost_metrics)\n        \n        all_alerts = cost_alerts + model_alerts + task_alerts\n        \n        # Generate adjustment suggestions\n        adjustments = await self.suggest_routing_adjustments(all_alerts)\n        \n        # Compile monitoring report\n        report = {\n            \"timestamp\": datetime.now().isoformat(),\n            \"metrics_summary\": {\n                \"cost_metrics\": cost_metrics.get(\"cost_analysis\", {}),\n                \"model_distribution\": model_metrics.get(\"model_routing\", {}).get(\"model_distribution\", {}),\n                \"batch_efficiency\": batch_metrics.get(\"batch_processing\", {}).get(\"batch_efficiency\", \"N/A\")\n            },\n            \"alerts\": [\n                {\n                    \"severity\": alert.severity,\n                    \"message\": alert.message,\n                    \"task_type\": alert.task_type,\n                    \"recommended_action\": alert.recommended_action.value\n                }\n                for alert in all_alerts\n            ],\n            \"suggested_adjustments\": adjustments,\n            \"alert_count\": {\n                \"high\": len([a for a in all_alerts if a.severity == \"high\"]),\n                \"medium\": len([a for a in all_alerts if a.severity == \"medium\"]),\n                \"low\": len([a for a in all_alerts if a.severity == \"low\"])\n            }\n        }\n        \n        return report\n    \n    def print_monitoring_report(self, report: Dict[str, Any]):\n        \"\"\"Print a formatted monitoring report\"\"\"\n        \n        print(\"\\n\" + \"=\"*70)\n        print(\"📊 COST OPTIMIZATION MONITORING REPORT\")\n        print(\"=\"*70)\n        \n        print(f\"\\n🕐 Timestamp: {report['timestamp']}\")\n        \n        # Metrics Summary\n        metrics = report[\"metrics_summary\"]\n        print(f\"\\n💰 COST METRICS:\")\n        cost_metrics = metrics.get(\"cost_metrics\", {})\n        for key, value in cost_metrics.items():\n            print(f\"   {key.replace('_', ' ').title()}: {value}\")\n        \n        print(f\"\\n🤖 MODEL DISTRIBUTION:\")\n        model_dist = metrics.get(\"model_distribution\", {})\n        for model, percentage in model_dist.items():\n            print(f\"   {model}: {percentage}\")\n        \n        # Alerts\n        alerts = report[\"alerts\"]\n        alert_count = report[\"alert_count\"]\n        \n        print(f\"\\n🚨 ALERTS ({alert_count['high']} high, {alert_count['medium']} medium, {alert_count['low']} low):\")\n        \n        if not alerts:\n            print(\"   ✅ No alerts - system operating optimally\")\n        else:\n            for alert in alerts:\n                severity_emoji = {\"high\": \"🔴\", \"medium\": \"🟡\", \"low\": \"🟢\"}[alert[\"severity\"]]\n                print(f\"   {severity_emoji} [{alert['severity'].upper()}] {alert['message']}\")\n                if alert[\"task_type\"]:\n                    print(f\"      Task: {alert['task_type']}\")\n                print(f\"      Recommended: {alert['recommended_action'].replace('_', ' ').title()}\")\n        \n        # Suggested Adjustments\n        adjustments = report[\"suggested_adjustments\"]\n        print(f\"\\n🔧 SUGGESTED ADJUSTMENTS ({len(adjustments)}):\")\n        \n        if not adjustments:\n            print(\"   ✅ No adjustments needed\")\n        else:\n            for i, adj in enumerate(adjustments, 1):\n                print(f\"   {i}. {adj['action'].replace('_', ' ').title()}\")\n                if \"task_type\" in adj:\n                    print(f\"      Task: {adj['task_type']}\")\n                print(f\"      Reason: {adj['reason']}\")\n                print(f\"      Estimated Savings: {adj.get('estimated_savings', 'N/A')}\")\n        \n        print(\"\\n\" + \"=\"*70)\n    \n    async def auto_apply_safe_adjustments(self, adjustments: List[Dict[str, Any]]) -> Dict[str, Any]:\n        \"\"\"Automatically apply safe adjustments\"\"\"\n        results = {\"applied\": 0, \"skipped\": 0, \"failed\": 0, \"details\": []}\n        \n        for adjustment in adjustments:\n            # Only auto-apply low-risk adjustments\n            if adjustment[\"action\"] == \"downgrade_model\":\n                # Skip if it affects critical tasks\n                critical_tasks = [\"budget_optimization\", \"advanced_meal_planning\"]\n                if adjustment.get(\"task_type\") in critical_tasks:\n                    results[\"skipped\"] += 1\n                    results[\"details\"].append(f\"Skipped {adjustment['task_type']} - critical task\")\n                    continue\n                \n                # Apply the adjustment\n                success = await self.apply_routing_adjustment(adjustment)\n                if success:\n                    results[\"applied\"] += 1\n                    results[\"details\"].append(f\"Applied downgrade for {adjustment['task_type']}\")\n                else:\n                    results[\"failed\"] += 1\n                    results[\"details\"].append(f\"Failed to apply adjustment for {adjustment['task_type']}\")\n        \n        return results\n\n\nasync def run_monitoring_demo():\n    \"\"\"Run a monitoring demonstration\"\"\"\n    \n    monitor = CostOptimizationMonitor()\n    \n    print(\"🔍 Running Cost Optimization Monitoring Demo\")\n    print(\"\\n⚠️  Note: This demo uses simulated data since the API server isn't running\")\n    \n    # Simulate monitoring report with realistic data\n    simulated_report = {\n        \"timestamp\": datetime.now().isoformat(),\n        \"metrics_summary\": {\n            \"cost_metrics\": {\n                \"total_cost\": \"$0.5385\",\n                \"baseline_cost\": \"$0.7222\",\n                \"total_savings\": \"$0.1837\",\n                \"savings_percentage\": \"25.4%\"\n            },\n            \"model_distribution\": {\n                \"flash_lite\": \"40.0%\",\n                \"flash\": \"60.0%\",\n                \"pro\": \"0.0%\"\n            },\n            \"batch_efficiency\": \"9.8%\"\n        },\n        \"alerts\": [\n            {\n                \"severity\": \"medium\",\n                \"message\": \"Task 'nutritional_analysis' has high average cost: $0.0055\",\n                \"task_type\": \"nutritional_analysis\",\n                \"recommended_action\": \"downgrade_model\"\n            },\n            {\n                \"severity\": \"low\",\n                \"message\": \"Batch processing rate could be improved: 9.8% (target: 15%)\",\n                \"task_type\": None,\n                \"recommended_action\": \"enable_batching\"\n            }\n        ],\n        \"suggested_adjustments\": [\n            {\n                \"action\": \"downgrade_model\",\n                \"task_type\": \"nutritional_analysis\",\n                \"from_complexity\": \"complex\",\n                \"to_complexity\": \"moderate\",\n                \"reason\": \"High average cost detected\",\n                \"estimated_savings\": \"$0.0039\"\n            }\n        ],\n        \"alert_count\": {\"high\": 0, \"medium\": 1, \"low\": 1}\n    }\n    \n    monitor.print_monitoring_report(simulated_report)\n    \n    # Demonstrate auto-adjustment capabilities\n    print(\"\\n🤖 Testing auto-adjustment capabilities...\")\n    auto_results = await monitor.auto_apply_safe_adjustments(simulated_report[\"suggested_adjustments\"])\n    \n    print(f\"\\n📋 Auto-Adjustment Results:\")\n    print(f\"   Applied: {auto_results['applied']}\")\n    print(f\"   Skipped: {auto_results['skipped']}\")\n    print(f\"   Failed: {auto_results['failed']}\")\n    \n    for detail in auto_results[\"details\"]:\n        print(f\"   • {detail}\")\n\n\nif __name__ == \"__main__\":\n    asyncio.run(run_monitoring_demo())
