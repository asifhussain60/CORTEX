#!/usr/bin/env python3
"""
Dashboard Data Adapter

Transforms CORTEX analyzer outputs into D3.js dashboard JSON format.
Replaces mock data files with real-time analysis results during application onboarding.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class DashboardMetadata:
    """Project metadata for dashboard."""
    project_name: str
    version: str
    analysis_timestamp: str
    scenario: str
    total_files: int
    total_lines: int
    languages: List[str]


@dataclass
class QualityIssue:
    """Quality issue for dashboard."""
    type: str
    severity: str
    file: str
    line: int
    description: str
    suggestion: str


@dataclass
class SecurityVulnerability:
    """Security vulnerability for dashboard."""
    type: str
    severity: str
    cve: Optional[str]
    description: str
    file: str
    line: int
    remediation: str
    owasp_category: Optional[str]


@dataclass
class PerformanceMetric:
    """Performance metric for dashboard."""
    metric_name: str
    current_value: float
    benchmark_value: float
    unit: str
    trend: str
    recommendation: str


class DashboardDataAdapter:
    """
    Transforms CORTEX analyzer outputs into D3.js dashboard format.
    
    Replaces mock data files with real analysis results:
    - CodeQualityAnalyzer → mock-quality.json
    - SecurityScanner → mock-security.json
    - PerformanceMetrics → mock-performance.json
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.dashboard_dir = project_root / "cortex-brain" / "documents" / "analysis" / "dashboard"
        self.dashboard_dir.mkdir(parents=True, exist_ok=True)
    
    def transform_metadata(self, project_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform project info to dashboard metadata format.
        
        Args:
            project_info: {
                'name': str,
                'version': str,
                'files': int,
                'lines': int,
                'languages': List[str]
            }
        
        Returns:
            Dashboard-compatible metadata dict
        """
        return {
            "projectName": project_info.get("name", "Unknown"),
            "version": project_info.get("version", "1.0.0"),
            "analysisTimestamp": datetime.now().isoformat(),
            "scenario": "production",
            "metrics": {
                "totalFiles": project_info.get("files", 0),
                "totalLines": project_info.get("lines", 0),
                "languages": project_info.get("languages", [])
            }
        }
    
    def transform_quality_data(
        self,
        quality_issues: List[Any],
        quality_score: float
    ) -> Dict[str, Any]:
        """
        Transform CodeQualityAnalyzer output to dashboard quality format.
        
        Args:
            quality_issues: List[CodeQualityIssue] from analyzer
            quality_score: Overall score 0-100
        
        Returns:
            Dashboard-compatible quality dict
        """
        # Group issues by severity
        by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        formatted_issues = []
        
        for issue in quality_issues:
            severity = getattr(issue, 'severity', 'medium').lower()
            by_severity[severity] = by_severity.get(severity, 0) + 1
            
            formatted_issues.append({
                "type": getattr(issue, 'issue_type', 'unknown'),
                "severity": severity,
                "file": str(getattr(issue, 'file_path', 'unknown')),
                "line": getattr(issue, 'line_number', 0),
                "description": getattr(issue, 'description', ''),
                "suggestion": getattr(issue, 'suggestion', '')
            })
        
        # Calculate technical debt estimate
        # Formula: critical * 4h + high * 2h + medium * 1h + low * 0.5h
        debt_hours = (
            by_severity["critical"] * 4 +
            by_severity["high"] * 2 +
            by_severity["medium"] * 1 +
            by_severity["low"] * 0.5
        )
        
        return {
            "overallScore": quality_score,
            "totalIssues": len(formatted_issues),
            "issuesBySeverity": by_severity,
            "technicalDebt": {
                "estimatedHours": debt_hours,
                "estimatedCost": debt_hours * 150  # $150/hour assumption
            },
            "issues": formatted_issues,
            "trends": {
                "direction": "stable",  # TODO: Calculate from historical data
                "changePercent": 0
            }
        }
    
    def transform_security_data(
        self,
        vulnerabilities: List[Any]
    ) -> Dict[str, Any]:
        """
        Transform SecurityScanner output to dashboard security format.
        
        Args:
            vulnerabilities: List[SecurityFinding] from scanner
        
        Returns:
            Dashboard-compatible security dict
        """
        # Group by severity
        by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        formatted_vulns = []
        
        for vuln in vulnerabilities:
            severity = getattr(vuln, 'severity', 'medium').lower()
            by_severity[severity] = by_severity.get(severity, 0) + 1
            
            formatted_vulns.append({
                "type": getattr(vuln, 'finding_type', 'unknown'),
                "severity": severity,
                "cve": getattr(vuln, 'cve_reference', None),
                "description": getattr(vuln, 'description', ''),
                "file": str(getattr(vuln, 'file_path', 'unknown')),
                "line": getattr(vuln, 'line_number', 0),
                "remediation": getattr(vuln, 'remediation', ''),
                "owaspCategory": self._map_to_owasp(getattr(vuln, 'finding_type', ''))
            })
        
        return {
            "totalVulnerabilities": len(formatted_vulns),
            "vulnerabilitiesBySeverity": by_severity,
            "owaspCompliance": self._calculate_owasp_compliance(formatted_vulns),
            "vulnerabilities": formatted_vulns,
            "trends": {
                "direction": "stable",
                "changePercent": 0
            }
        }
    
    def transform_performance_data(
        self,
        metrics: List[Any]
    ) -> Dict[str, Any]:
        """
        Transform PerformanceMetrics to dashboard performance format.
        
        Args:
            metrics: List[PerformanceMetric] from telemetry
        
        Returns:
            Dashboard-compatible performance dict
        """
        formatted_metrics = []
        total_latency = 0
        bottleneck_count = 0
        
        for metric in metrics:
            current = getattr(metric, 'current_value', 0)
            benchmark = getattr(metric, 'benchmark_value', 0)
            
            # Identify bottlenecks (current > 2x benchmark)
            is_bottleneck = current > (benchmark * 2) if benchmark > 0 else False
            if is_bottleneck:
                bottleneck_count += 1
            
            formatted_metrics.append({
                "metricName": getattr(metric, 'metric_name', 'unknown'),
                "currentValue": current,
                "benchmarkValue": benchmark,
                "unit": getattr(metric, 'unit', 'ms'),
                "trend": getattr(metric, 'trend', 'stable'),
                "recommendation": getattr(metric, 'recommendation', ''),
                "isBottleneck": is_bottleneck
            })
            
            # Accumulate latency metrics
            if getattr(metric, 'unit', '') == 'ms':
                total_latency += current
        
        return {
            "averageLatency": total_latency / len(metrics) if metrics else 0,
            "bottleneckCount": bottleneck_count,
            "metrics": formatted_metrics,
            "trends": {
                "direction": "stable",
                "changePercent": 0
            }
        }
    
    def _map_to_owasp(self, finding_type: str) -> Optional[str]:
        """Map finding type to OWASP Top 10 category."""
        owasp_mapping = {
            "sql_injection": "A03:2021-Injection",
            "xss": "A03:2021-Injection",
            "broken_access_control": "A01:2021-Broken Access Control",
            "cryptographic_failure": "A02:2021-Cryptographic Failures",
            "insecure_design": "A04:2021-Insecure Design",
            "security_misconfiguration": "A05:2021-Security Misconfiguration",
            "vulnerable_components": "A06:2021-Vulnerable and Outdated Components",
            "auth_failure": "A07:2021-Identification and Authentication Failures",
            "logging_failure": "A09:2021-Security Logging and Monitoring Failures",
            "ssrf": "A10:2021-Server-Side Request Forgery"
        }
        return owasp_mapping.get(finding_type.lower())
    
    def _calculate_owasp_compliance(self, vulnerabilities: List[Dict]) -> float:
        """Calculate OWASP compliance percentage (0-100)."""
        if not vulnerabilities:
            return 100.0
        
        # Simple formula: 100% - (vulnerabilities / 10)
        # Assumes 10 vulnerabilities = 0% compliance
        deduction = len(vulnerabilities) * 10
        return max(0.0, 100.0 - deduction)
    
    def save_dashboard_data(
        self,
        metadata: Dict[str, Any],
        quality: Dict[str, Any],
        security: Dict[str, Any],
        performance: Dict[str, Any]
    ) -> None:
        """
        Save all dashboard data files (replaces mock data).
        
        Args:
            metadata: Transformed metadata
            quality: Transformed quality data
            security: Transformed security data
            performance: Transformed performance data
        """
        data_dir = self.dashboard_dir / "data"
        data_dir.mkdir(exist_ok=True)
        
        files = {
            "metadata.json": metadata,
            "quality.json": quality,
            "security.json": security,
            "performance.json": performance
        }
        
        for filename, data in files.items():
            filepath = data_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved dashboard data: {filepath}")
    
    def generate_full_dashboard_data(
        self,
        project_info: Dict[str, Any],
        quality_issues: List[Any],
        quality_score: float,
        vulnerabilities: List[Any],
        metrics: List[Any]
    ) -> None:
        """
        Generate complete dashboard data from CORTEX analyzers.
        
        This is the main entry point called during application onboarding.
        
        Args:
            project_info: Project metadata
            quality_issues: From CodeQualityAnalyzer
            quality_score: Overall quality score 0-100
            vulnerabilities: From SecurityScanner
            metrics: From PerformanceMetrics
        """
        logger.info("Generating dashboard data from CORTEX analyzers...")
        
        metadata = self.transform_metadata(project_info)
        quality = self.transform_quality_data(quality_issues, quality_score)
        security = self.transform_security_data(vulnerabilities)
        performance = self.transform_performance_data(metrics)
        
        self.save_dashboard_data(metadata, quality, security, performance)
        
        logger.info("✅ Dashboard data generation complete")
        logger.info(f"   Data directory: {self.dashboard_dir / 'data'}")
