"""
Overview Collector - Dashboard Overview Tab

Orchestrates data aggregation from multiple sources to generate overview.json.
Integrates HealthScoreCalculator and TrendAnalyzer.

Author: Asif Hussain
Created: 2025-12-06
Phase: GREEN (Minimal Implementation)
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from src.dashboard.data.health_calculator import HealthScoreCalculator
from src.dashboard.data.trend_analyzer import TrendAnalyzer


class OverviewCollector:
    """
    Collects and aggregates dashboard overview data.
    
    Aggregates data from:
        - health-data.json
        - security.json
        - tech-stack.json
        - code-organization.json
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize collector.
        
        Args:
            repo_path: Path to repository root
        """
        self.repo_path = repo_path
        self.data_path = Path(repo_path)
        self.health_calculator = HealthScoreCalculator()
        self.trend_analyzer = TrendAnalyzer()
    
    def collect(self) -> Dict[str, Any]:
        """
        Collect and aggregate all overview data.
        
        Returns:
            Overview data conforming to schema
        """
        # Load all data sources
        health_data = self._load_health_data()
        security_data = self._load_security_data()
        tech_stack_data = self._load_tech_stack_data()
        code_org_data = self._load_code_org_data()
        
        # Load previous snapshot for trends
        previous_snapshot = self._load_previous_snapshot()
        
        # Extract category scores
        metrics = health_data.get("metrics", {})
        category_scores = {
            "code_quality": metrics.get("code_quality_score", 0),
            "security": metrics.get("security_score", 0),
            "tests": metrics.get("test_score", 0),
            "documentation": metrics.get("documentation_score", 0)
        }
        
        # Calculate overall health
        overall_health_score = self.health_calculator.calculate_overall_health(category_scores)
        
        # Determine status
        status = self.health_calculator.determine_status(overall_health_score)
        
        # Analyze trends
        current_snapshot = {
            "overall_health_score": overall_health_score,
            **category_scores
        }
        trends = self.trend_analyzer.compare_snapshots(current_snapshot, previous_snapshot)
        
        # Build overview structure
        overview = {
            "project_name": Path(self.repo_path).name,
            "overall_health": {
                "score": overall_health_score,
                "status": status,
                "trend": trends.get("overall_health_score", "N/A"),
                "last_scan": datetime.now().isoformat()
            },
            "key_metrics": self._extract_key_metrics(health_data),
            "health_categories": self._build_health_categories(category_scores, trends),
            "critical_issues": self._extract_critical_issues(health_data, security_data),
            "composition": self._extract_composition(tech_stack_data),
            "trends": {
                "health_trend": trends.get("overall_health_score", "N/A"),
                "velocity_trend": "stable",
                "quality_trend": trends.get("code_quality", "N/A")
            }
        }
        
        return overview
    
    def _load_health_data(self) -> Dict[str, Any]:
        """Load health-data.json."""
        return self._load_json_file("health-data.json")
    
    def _load_security_data(self) -> Dict[str, Any]:
        """Load security.json."""
        return self._load_json_file("security.json")
    
    def _load_tech_stack_data(self) -> Dict[str, Any]:
        """Load tech-stack.json."""
        return self._load_json_file("tech-stack.json")
    
    def _load_code_org_data(self) -> Dict[str, Any]:
        """Load code-organization.json."""
        return self._load_json_file("code-organization.json")
    
    def _load_json_file(self, filename: str) -> Dict[str, Any]:
        """
        Load JSON file from data directory.
        
        Args:
            filename: Name of JSON file
            
        Returns:
            Parsed JSON data or empty dict if file doesn't exist
        """
        file_path = self.data_path / filename
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _load_previous_snapshot(self) -> Optional[Dict[str, Any]]:
        """
        Load previous snapshot for trend comparison.
        
        Returns:
            Previous snapshot data or None
        """
        snapshot_path = self.data_path / "overview-snapshot-previous.json"
        try:
            with open(snapshot_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def _extract_key_metrics(self, health_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics from health data."""
        summary = health_data.get("summary", {})
        return {
            "total_files": summary.get("total_files", 0),
            "total_loc": summary.get("total_loc", 0),
            "test_coverage": summary.get("test_coverage", 0),
            "maintainability_index": summary.get("maintainability_index", 0),
            "technical_debt_hours": summary.get("technical_debt_hours", 0)
        }
    
    def _build_health_categories(
        self,
        category_scores: Dict[str, float],
        trends: Dict[str, str]
    ) -> list:
        """Build health categories list."""
        categories = []
        
        for name, score in category_scores.items():
            status = self.health_calculator.determine_status(score)
            categories.append({
                "name": name,
                "score": score,
                "status": status,
                "trend": trends.get(name, "N/A"),
                "issues_count": 0,
                "details": f"{name.replace('_', ' ').title()} score"
            })
        
        return categories
    
    def _extract_critical_issues(
        self,
        health_data: Dict[str, Any],
        security_data: Dict[str, Any]
    ) -> list:
        """Extract critical issues from data."""
        issues = []
        
        # Check security vulnerabilities
        vulnerabilities = security_data.get("vulnerabilities", {})
        critical_count = vulnerabilities.get("critical", 0) + vulnerabilities.get("high", 0)
        
        if critical_count > 0:
            issues.append({
                "severity": "critical" if vulnerabilities.get("critical", 0) > 0 else "high",
                "category": "security",
                "message": f"{critical_count} high-severity security vulnerabilities",
                "count": critical_count
            })
        
        return issues
    
    def _extract_composition(self, tech_stack_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract composition data."""
        languages = tech_stack_data.get("languages", [])
        
        return {
            "languages": [
                {
                    "name": lang.get("name", "Unknown"),
                    "percentage": lang.get("percentage", 0),
                    "loc": lang.get("loc", 0)
                }
                for lang in languages[:5]  # Top 5 languages
            ],
            "components": []
        }
