"""
Overview Aggregator

Combines data from multiple collectors to create overview.json

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class OverviewAggregator:
    """Aggregates health, tech, security, and architecture data into overview"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
    
    def aggregate(self) -> Dict[str, Any]:
        """Generate overview.json from source collectors"""
        
        # Load source data
        health = self._load_json("health-data.json")
        tech = self._load_json("tech-stack.json")
        security = self._load_json("security.json")
        architecture = self._load_json("architecture.json")
        code_org = self._load_json("code-organization.json")
        
        # Calculate overall health (weighted average)
        security_score = security.get("overall_score", 100)
        health_score = health.get("overall_health_score", 75)
        complexity_score = 100 - min(code_org.get("summary", {}).get("avg_complexity", 0), 100)
        
        overall_health_score = int(
            security_score * 0.4 + 
            health_score * 0.3 + 
            complexity_score * 0.3
        )
        
        # Determine status and trend
        status = "healthy" if overall_health_score >= 80 else "warning" if overall_health_score >= 60 else "critical"
        trend = "stable"  # Would analyze historical data
        
        # Build key metrics
        key_metrics = {
            "total_files": code_org.get("summary", {}).get("total_files", 0),
            "total_loc": code_org.get("summary", {}).get("total_loc", 0),
            "test_coverage": health.get("summary", {}).get("test_coverage", 0),
            "maintainability_index": code_org.get("summary", {}).get("maintainability_score", 0),
            "technical_debt_hours": code_org.get("summary", {}).get("technical_debt_hours", 0)
        }
        
        # Build health categories
        health_categories = [
            {
                "name": "code_quality",
                "score": health.get("metrics", {}).get("code_quality_score", 75),
                "status": "healthy" if health.get("metrics", {}).get("code_quality_score", 75) >= 70 else "warning",
                "trend": "stable",
                "issues_count": code_org.get("summary", {}).get("code_smell_count", 0),
                "details": f"{code_org.get('summary', {}).get('code_smell_count', 0)} code smells detected"
            },
            {
                "name": "security",
                "score": security_score,
                "status": "healthy" if security_score >= 90 else "warning",
                "trend": "stable",
                "issues_count": len(security.get("vulnerabilities", [])),
                "details": f"{len(security.get('vulnerabilities', []))} vulnerabilities found"
            },
            {
                "name": "tests",
                "score": health.get("metrics", {}).get("test_score", 0),
                "status": "healthy" if health.get("metrics", {}).get("test_score", 0) >= 70 else "warning",
                "trend": "stable",
                "issues_count": 0,
                "details": f"Test coverage at {health.get('summary', {}).get('test_coverage', 0)}%"
            },
            {
                "name": "documentation",
                "score": health.get("metrics", {}).get("documentation_score", 50),
                "status": "warning" if health.get("metrics", {}).get("documentation_score", 50) < 70 else "healthy",
                "trend": "stable",
                "issues_count": 1 if health.get("metrics", {}).get("documentation_score", 50) < 70 else 0,
                "details": "Documentation needs improvement" if health.get("metrics", {}).get("documentation_score", 50) < 70 else "Documentation adequate"
            }
        ]
        
        # Build critical issues
        critical_issues = []
        vulnerabilities = security.get("vulnerabilities", [])
        if isinstance(vulnerabilities, list):
            high_vuln_count = sum(1 for v in vulnerabilities if isinstance(v, dict) and v.get("severity") == "high")
        else:
            high_vuln_count = 0
        if high_vuln_count > 0:
            critical_issues.append({
                "severity": "high",
                "category": "security",
                "message": f"{high_vuln_count} high-severity vulnerabilities",
                "count": high_vuln_count
            })
        
        critical_hotspots = len([h for h in code_org.get("hotspots", []) if h.get("risk_level") == "critical"])
        if critical_hotspots > 0:
            critical_issues.append({
                "severity": "high",
                "category": "complexity",
                "message": f"{critical_hotspots} critical complexity hotspots",
                "count": critical_hotspots
            })
        
        # Build composition from tech stack
        lang_breakdown = code_org.get("language_breakdown", {})
        languages = [
            {
                "name": lang,
                "percentage": data.get("percentage", 0),
                "loc": data.get("loc", 0)
            }
            for lang, data in sorted(lang_breakdown.items(), key=lambda x: x[1].get("percentage", 0), reverse=True)
        ][:5]  # Top 5 languages
        
        # Build components from architecture
        components = []
        if tech.get("frontend"):
            components.append({
                "type": "frontend",
                "count": len(tech.get("frontend", [])),
                "technologies": [t["name"] for t in tech.get("frontend", [])[:3]]
            })
        if tech.get("backend"):
            components.append({
                "type": "backend",
                "count": len(tech.get("backend", [])),
                "technologies": [t["name"] for t in tech.get("backend", [])[:3]]
            })
        if tech.get("database"):
            components.append({
                "type": "database",
                "count": len(tech.get("database", [])),
                "technologies": [t["name"] for t in tech.get("database", [])[:3]]
            })
        
        # Build trends (simplified - would analyze historical data)
        trends = {
            "health_trend": trend,
            "security_trend": "stable",
            "complexity_trend": "stable"
        }
        
        return {
            "project_name": self.data_dir.name.replace("-", " ").title(),
            "overall_health": {
                "score": overall_health_score,
                "status": status,
                "trend": trend,
                "last_scan": datetime.now().isoformat()
            },
            "key_metrics": key_metrics,
            "health_categories": health_categories,
            "critical_issues": critical_issues,
            "composition": {
                "languages": languages,
                "components": components
            },
            "trends": trends
        }
    
    def _load_json(self, filename: str) -> Dict[str, Any]:
        """Load JSON file with error handling"""
        file_path = self.data_dir / filename
        if file_path.exists():
            try:
                return json.loads(file_path.read_text())
            except:
                return {}
        return {}


def main():
    """CLI entry point"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python overview_aggregator.py <data_dir>")
        sys.exit(1)
    
    data_dir = Path(sys.argv[1])
    aggregator = OverviewAggregator(data_dir)
    result = aggregator.aggregate()
    
    output_path = data_dir / "overview.json"
    output_path.write_text(json.dumps(result, indent=2))
    print(f"Generated: {output_path}")


if __name__ == "__main__":
    main()
