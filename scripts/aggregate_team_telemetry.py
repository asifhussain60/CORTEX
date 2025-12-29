"""
CORTEX Team Telemetry Aggregator

Consolidates performance reports from multiple engineers for:
- Executive dashboards
- Team-wide ROI analysis  
- Platform comparison (Windows vs Mac vs Linux)
- Engineer performance rankings
- Cross-application insights

Usage:
    python scripts/aggregate_team_telemetry.py --input ./team-reports/ --output team-analytics.yaml

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import argparse
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from collections import defaultdict
import yaml
import json


class TeamTelemetryAggregator:
    """Aggregates CORTEX telemetry from multiple engineers"""
    
    def __init__(self, reports_dir: Path):
        self.reports_dir = reports_dir
        self.engineers = []
        self.team_metrics = {
            "performance": defaultdict(lambda: {
                "total_executions": 0,
                "total_successes": 0,
                "total_failures": 0,
                "durations": [],
                "engineers_using": set()
            }),
            "cost_savings": {
                "total_saved_usd": 0,
                "total_tokens_saved": 0,
                "total_time_saved_hours": 0,
                "by_engineer": []
            },
            "productivity": {
                "total_commits": 0,
                "total_prs_merged": 0,
                "total_bugs_fixed": 0,
                "by_engineer": []
            },
            "copilot": {
                "total_memory_hits": 0,
                "total_memory_misses": 0,
                "total_suggestions_accepted": 0,
                "by_engineer": []
            },
            "platforms": defaultdict(lambda: {
                "engineer_count": 0,
                "avg_latency_ms": [],
                "engineers": []
            })
        }
    
    def aggregate(self) -> Dict[str, Any]:
        """Aggregate all reports"""
        
        # Load all individual reports
        report_files = list(self.reports_dir.glob("*.yaml"))
        
        if not report_files:
            return {"error": "No reports found", "location": str(self.reports_dir)}
        
        print(f"📊 Aggregating {len(report_files)} engineer reports...")
        
        for report_file in report_files:
            with open(report_file, 'r') as f:
                report = yaml.safe_load(f)
                self._process_report(report)
        
        # Calculate team-wide metrics
        team_analysis = self._calculate_team_metrics()
        
        # Generate rankings
        rankings = self._generate_rankings()
        
        # Platform comparison
        platform_comparison = self._compare_platforms()
        
        # Build comprehensive team report
        return {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "engineers_analyzed": len(self.engineers),
                "reports_processed": len(report_files)
            },
            
            # Executive summary
            "executive_summary": {
                "total_cost_savings_usd": round(self.team_metrics["cost_savings"]["total_saved_usd"], 2),
                "annual_projection_usd": round(self.team_metrics["cost_savings"]["total_saved_usd"] * 12, 2),  # Assuming 30-day reports
                "total_time_saved_hours": round(self.team_metrics["cost_savings"]["total_time_saved_hours"], 1),
                "avg_roi_multiplier": round(team_analysis["avg_roi"], 1),
                "total_commits": self.team_metrics["productivity"]["total_commits"],
                "total_prs_merged": self.team_metrics["productivity"]["total_prs_merged"],
                "team_copilot_memory_hit_rate": round(team_analysis["team_memory_hit_rate"], 3),
                "recommendation": team_analysis["recommendation"]
            },
            
            # Engineer details
            "engineers": self.engineers,
            
            # Team-wide metrics
            "team_performance": team_analysis,
            
            # Rankings
            "rankings": rankings,
            
            # Platform comparison
            "platform_analysis": platform_comparison,
            
            # Capability analysis
            "capability_analysis": self._analyze_capabilities(),
            
            # Executive talking points
            "executive_talking_points": self._generate_talking_points(team_analysis, rankings)
        }
    
    def _process_report(self, report: Dict[str, Any]) -> None:
        """Process individual engineer report"""
        
        profile = report.get("engineer_profile", {})
        engineer_name = profile.get("name", "Unknown")
        engineer_email = profile.get("email", "unknown@example.com")
        machine = profile.get("machine", {})
        platform = machine.get("platform", "Unknown")
        
        # Store engineer info
        engineer_summary = {
            "name": engineer_name,
            "email": engineer_email,
            "machine_hostname": machine.get("hostname", "unknown"),
            "platform": platform,
            "cpu": machine.get("cpu", "unknown"),
            "ram_gb": machine.get("ram_gb", 0),
            "cortex_version": profile.get("cortex_version", "unknown"),
            
            # Metrics from report
            "cost_savings_usd": report.get("cost_savings", {}).get("total_cost_saved_usd", 0),
            "time_saved_hours": report.get("cost_savings", {}).get("total_time_saved_hours", 0),
            "commits": report.get("productivity", {}).get("total_commits", 0),
            "prs_merged": report.get("productivity", {}).get("total_prs_merged", 0),
            "test_coverage": report.get("productivity", {}).get("avg_test_coverage", 0),
            "copilot_memory_hit_rate": report.get("copilot_enhancement", {}).get("memory_hit_rate", 0),
            "roi_multiplier": report.get("roi_analysis", {}).get("roi_multiplier", 0)
        }
        
        self.engineers.append(engineer_summary)
        
        # Aggregate performance metrics
        for capability in report.get("performance", {}).get("capabilities", []):
            cap_name = capability["name"]
            metrics = capability["metrics"]
            
            self.team_metrics["performance"][cap_name]["total_executions"] += metrics["total_executions"]
            self.team_metrics["performance"][cap_name]["total_successes"] += int(metrics["total_executions"] * metrics["success_rate"])
            self.team_metrics["performance"][cap_name]["total_failures"] += int(metrics["total_executions"] * (1 - metrics["success_rate"]))
            self.team_metrics["performance"][cap_name]["durations"].append(metrics["avg_execution_time_ms"])
            self.team_metrics["performance"][cap_name]["engineers_using"].add(engineer_name)
        
        # Aggregate cost savings
        cost_savings = report.get("cost_savings", {})
        self.team_metrics["cost_savings"]["total_saved_usd"] += cost_savings.get("total_cost_saved_usd", 0)
        self.team_metrics["cost_savings"]["total_tokens_saved"] += cost_savings.get("total_tokens_saved", 0)
        self.team_metrics["cost_savings"]["total_time_saved_hours"] += cost_savings.get("total_time_saved_hours", 0)
        
        # Aggregate productivity
        productivity = report.get("productivity", {})
        self.team_metrics["productivity"]["total_commits"] += productivity.get("total_commits", 0)
        self.team_metrics["productivity"]["total_prs_merged"] += productivity.get("total_prs_merged", 0)
        self.team_metrics["productivity"]["total_bugs_fixed"] += productivity.get("total_bugs_fixed", 0)
        
        # Aggregate Copilot metrics
        copilot = report.get("copilot_enhancement", {})
        self.team_metrics["copilot"]["total_memory_hits"] += copilot.get("memory_hits", 0)
        self.team_metrics["copilot"]["total_memory_misses"] += copilot.get("memory_misses", 0)
        self.team_metrics["copilot"]["total_suggestions_accepted"] += copilot.get("suggestions_accepted", 0)
        
        # Track by platform
        self.team_metrics["platforms"][platform]["engineer_count"] += 1
        self.team_metrics["platforms"][platform]["engineers"].append(engineer_name)
        
        # Calculate avg latency for platform
        for capability in report.get("performance", {}).get("capabilities", []):
            self.team_metrics["platforms"][platform]["avg_latency_ms"].append(
                capability["metrics"]["avg_execution_time_ms"]
            )
    
    def _calculate_team_metrics(self) -> Dict[str, Any]:
        """Calculate team-wide aggregated metrics"""
        
        # Average ROI across team
        avg_roi = sum(e["roi_multiplier"] for e in self.engineers) / len(self.engineers) if self.engineers else 0
        
        # Team memory hit rate
        total_hits = self.team_metrics["copilot"]["total_memory_hits"]
        total_misses = self.team_metrics["copilot"]["total_memory_misses"]
        team_memory_hit_rate = total_hits / (total_hits + total_misses) if (total_hits + total_misses) > 0 else 0
        
        # Average commits per engineer
        avg_commits = self.team_metrics["productivity"]["total_commits"] / len(self.engineers) if self.engineers else 0
        
        return {
            "avg_roi": avg_roi,
            "team_memory_hit_rate": team_memory_hit_rate,
            "avg_commits_per_engineer": round(avg_commits, 1),
            "avg_cost_savings_per_engineer_usd": round(
                self.team_metrics["cost_savings"]["total_saved_usd"] / len(self.engineers), 2
            ) if self.engineers else 0,
            "recommendation": (
                "🏆 Excellent team ROI - Expand CORTEX usage" if avg_roi >= 3.0
                else "✅ Strong team ROI - Continue investment" if avg_roi >= 2.0
                else "📈 Positive team ROI - Monitor and optimize" if avg_roi >= 1.0
                else "⚠️ Low team ROI - Increase training and adoption"
            )
        }
    
    def _generate_rankings(self) -> Dict[str, List[Dict]]:
        """Generate engineer rankings"""
        
        return {
            "top_cost_savers": sorted(
                self.engineers,
                key=lambda e: e["cost_savings_usd"],
                reverse=True
            )[:5],
            
            "top_producers": sorted(
                self.engineers,
                key=lambda e: e["commits"],
                reverse=True
            )[:5],
            
            "highest_roi": sorted(
                self.engineers,
                key=lambda e: e["roi_multiplier"],
                reverse=True
            )[:5],
            
            "best_copilot_usage": sorted(
                self.engineers,
                key=lambda e: e["copilot_memory_hit_rate"],
                reverse=True
            )[:5]
        }
    
    def _compare_platforms(self) -> Dict[str, Any]:
        """Compare performance across platforms"""
        
        comparison = {}
        
        for platform, data in self.team_metrics["platforms"].items():
            avg_latency = sum(data["avg_latency_ms"]) / len(data["avg_latency_ms"]) if data["avg_latency_ms"] else 0
            
            comparison[platform] = {
                "engineer_count": data["engineer_count"],
                "engineers": data["engineers"],
                "avg_latency_ms": round(avg_latency, 0),
                "performance_grade": (
                    "Excellent" if avg_latency < 500
                    else "Good" if avg_latency < 1000
                    else "Fair" if avg_latency < 2000
                    else "Needs Optimization"
                )
            }
        
        return comparison
    
    def _analyze_capabilities(self) -> List[Dict[str, Any]]:
        """Analyze capability usage across team"""
        
        capabilities = []
        
        for cap_name, data in self.team_metrics["performance"].items():
            total_exec = data["total_executions"]
            success_rate = data["total_successes"] / total_exec if total_exec > 0 else 0
            avg_duration = sum(data["durations"]) / len(data["durations"]) if data["durations"] else 0
            
            capabilities.append({
                "name": cap_name,
                "total_executions": total_exec,
                "success_rate": round(success_rate, 3),
                "avg_duration_ms": round(avg_duration, 0),
                "engineers_using": len(data["engineers_using"]),
                "adoption_rate": round(len(data["engineers_using"]) / len(self.engineers), 2) if self.engineers else 0
            })
        
        # Sort by total executions (most used first)
        return sorted(capabilities, key=lambda c: c["total_executions"], reverse=True)
    
    def _generate_talking_points(self, team_analysis: Dict, rankings: Dict) -> List[str]:
        """Generate executive talking points"""
        
        return [
            f"💰 Team Cost Savings: ${self.team_metrics['cost_savings']['total_saved_usd']:.2f} (${self.team_metrics['cost_savings']['total_saved_usd'] * 12:.2f}/year projected)",
            f"⏱️  Time Saved: {self.team_metrics['cost_savings']['total_time_saved_hours']:.0f} hours across {len(self.engineers)} engineers",
            f"📈 Team Productivity: {self.team_metrics['productivity']['total_commits']} commits, {self.team_metrics['productivity']['total_prs_merged']} PRs merged",
            f"🏆 Top Cost Saver: {rankings['top_cost_savers'][0]['name']} (${rankings['top_cost_savers'][0]['cost_savings_usd']:.2f})",
            f"🚀 Team Copilot Enhancement: {team_analysis['team_memory_hit_rate']:.1%} memory hit rate",
            f"💪 Average ROI: {team_analysis['avg_roi']:.1f}x return on CORTEX investment",
            f"✅ Recommendation: {team_analysis['recommendation']}"
        ]


def main():
    parser = argparse.ArgumentParser(description="Aggregate CORTEX team telemetry")
    parser.add_argument("--input", required=True, help="Directory containing individual engineer reports")
    parser.add_argument("--output", required=True, help="Output file path (YAML)")
    
    args = parser.parse_args()
    
    input_dir = Path(args.input)
    output_file = Path(args.output)
    
    if not input_dir.exists():
        print(f"❌ Error: Input directory not found: {input_dir}")
        return
    
    # Aggregate reports
    aggregator = TeamTelemetryAggregator(input_dir)
    team_report = aggregator.aggregate()
    
    if "error" in team_report:
        print(f"❌ Error: {team_report['error']}")
        return
    
    # Save team report
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        yaml.safe_dump(team_report, f, sort_keys=False, default_flow_style=False)
    
    # Print summary
    print(f"\n✅ Team telemetry aggregated: {output_file}")
    print(f"\n📊 TEAM SUMMARY")
    print(f"   Engineers Analyzed: {team_report['report_metadata']['engineers_analyzed']}")
    print(f"\n💰 COST SAVINGS")
    print(f"   Total: ${team_report['executive_summary']['total_cost_savings_usd']}")
    print(f"   Annual Projection: ${team_report['executive_summary']['annual_projection_usd']}")
    print(f"\n📈 PRODUCTIVITY")
    print(f"   Total Commits: {team_report['executive_summary']['total_commits']}")
    print(f"   PRs Merged: {team_report['executive_summary']['total_prs_merged']}")
    print(f"\n🏆 ROI: {team_report['executive_summary']['avg_roi_multiplier']}x\n")
    
    # Print top performers
    print("🏆 TOP PERFORMERS")
    for i, engineer in enumerate(team_report['rankings']['top_cost_savers'][:3], 1):
        print(f"   #{i} {engineer['name']}: ${engineer['cost_savings_usd']:.2f} saved")
    print()


if __name__ == "__main__":
    main()
