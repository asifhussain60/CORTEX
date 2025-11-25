#!/usr/bin/env python3
"""
Optimization Health Monitor

Analyzes code quality, performance characteristics, and system health
to provide comprehensive optimization recommendations and health validation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import ast
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
import logging

# Import implementation data structures
from .implementation_discovery_engine import ImplementationData, CodeElement, FileChange

logger = logging.getLogger(__name__)

@dataclass
class CodeQualityIssue:
    """Represents a code quality issue"""
    issue_type: str  # 'complexity', 'duplication', 'naming', 'structure', 'security'
    severity: str    # 'critical', 'high', 'medium', 'low'
    description: str
    file_path: str
    line_number: int
    suggestion: str
    code_snippet: Optional[str] = None

@dataclass
class PerformanceMetric:
    """Represents a performance metric"""
    metric_name: str
    current_value: float
    benchmark_value: Optional[float] = None
    unit: str = ""
    trend: str = "unknown"  # 'improving', 'stable', 'degrading'
    recommendation: str = ""

@dataclass
class SecurityFinding:
    """Represents a security concern"""
    finding_type: str  # 'vulnerability', 'misconfiguration', 'exposure'
    severity: str      # 'critical', 'high', 'medium', 'low' 
    description: str
    file_path: str
    line_number: int
    remediation: str
    cve_reference: Optional[str] = None

@dataclass
class OptimizationRecommendation:
    """Represents an optimization recommendation"""
    category: str     # 'performance', 'quality', 'security', 'maintainability'
    priority: str     # 'critical', 'high', 'medium', 'low'
    title: str
    description: str
    implementation_effort: str  # 'low', 'medium', 'high'
    expected_impact: str       # 'low', 'medium', 'high'
    code_examples: List[str] = field(default_factory=list)

@dataclass
class HealthReport:
    """Comprehensive health and optimization report"""
    feature_name: str
    analysis_timestamp: datetime
    
    # Quality analysis
    quality_score: float = 0.0  # 0-100
    quality_issues: List[CodeQualityIssue] = field(default_factory=list)
    
    # Performance analysis
    performance_score: float = 0.0  # 0-100
    performance_metrics: List[PerformanceMetric] = field(default_factory=list)
    
    # Security analysis
    security_score: float = 0.0  # 0-100
    security_findings: List[SecurityFinding] = field(default_factory=list)
    
    # Optimization recommendations
    recommendations: List[OptimizationRecommendation] = field(default_factory=list)
    
    # Overall health
    overall_health_score: float = 0.0  # 0-100
    health_status: str = "unknown"  # 'excellent', 'good', 'fair', 'poor'
    
    # Metrics
    files_analyzed: int = 0
    issues_found: int = 0
    recommendations_generated: int = 0


class CodeQualityAnalyzer:
    """Analyzes code quality metrics and identifies issues"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        
    def analyze_quality(self, implementation_data: ImplementationData) -> Tuple[float, List[CodeQualityIssue]]:
        """Analyze code quality and return score + issues"""
        issues = []
        
        # Analyze complexity
        complexity_issues = self._analyze_complexity(implementation_data.new_functions)
        issues.extend(complexity_issues)
        
        # Analyze naming conventions
        naming_issues = self._analyze_naming_conventions(
            implementation_data.new_classes + implementation_data.new_functions
        )
        issues.extend(naming_issues)
        
        # Analyze structure
        structure_issues = self._analyze_code_structure(implementation_data)
        issues.extend(structure_issues)
        
        # Analyze documentation
        doc_issues = self._analyze_documentation_quality(
            implementation_data.new_classes + implementation_data.new_functions
        )
        issues.extend(doc_issues)
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(issues, implementation_data)
        
        return quality_score, issues
    
    def _analyze_complexity(self, functions: List[CodeElement]) -> List[CodeQualityIssue]:
        """Analyze cyclomatic complexity"""
        issues = []
        
        for func in functions:
            if func.complexity > 15:  # High complexity threshold
                severity = "critical" if func.complexity > 25 else "high"
                issue = CodeQualityIssue(
                    issue_type="complexity",
                    severity=severity,
                    description=f"Function {func.name} has high complexity ({func.complexity})",
                    file_path=func.file_path,
                    line_number=func.line_number,
                    suggestion="Consider breaking this function into smaller, more focused functions"
                )
                issues.append(issue)
                
        return issues
    
    def _analyze_naming_conventions(self, elements: List[CodeElement]) -> List[CodeQualityIssue]:
        """Analyze naming conventions"""
        issues = []
        
        for element in elements:
            # Check class naming (should be PascalCase)
            if element.element_type == 'class':
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', element.name):
                    issue = CodeQualityIssue(
                        issue_type="naming",
                        severity="medium",
                        description=f"Class {element.name} doesn't follow PascalCase convention",
                        file_path=element.file_path,
                        line_number=element.line_number,
                        suggestion="Use PascalCase for class names (e.g., MyClass)"
                    )
                    issues.append(issue)
                    
            # Check function naming (should be snake_case for Python)
            elif element.element_type in ['function', 'method']:
                if element.file_path.endswith('.py'):
                    if not re.match(r'^[a-z_][a-z0-9_]*$', element.name):
                        issue = CodeQualityIssue(
                            issue_type="naming",
                            severity="low",
                            description=f"Function {element.name} doesn't follow snake_case convention",
                            file_path=element.file_path,
                            line_number=element.line_number,
                            suggestion="Use snake_case for function names (e.g., my_function)"
                        )
                        issues.append(issue)
                        
        return issues
    
    def _analyze_code_structure(self, implementation_data: ImplementationData) -> List[CodeQualityIssue]:
        """Analyze code structure and organization"""
        issues = []
        
        # Check for large files
        for file_change in implementation_data.files_changed:
            if file_change.lines_added > 500:  # Large file threshold
                issue = CodeQualityIssue(
                    issue_type="structure",
                    severity="medium", 
                    description=f"File {file_change.file_path} is very large ({file_change.lines_added} lines added)",
                    file_path=file_change.file_path,
                    line_number=1,
                    suggestion="Consider splitting large files into smaller, more focused modules"
                )
                issues.append(issue)
                
        # Check for too many classes in one file
        file_class_count = {}
        for cls in implementation_data.new_classes:
            file_class_count[cls.file_path] = file_class_count.get(cls.file_path, 0) + 1
            
        for file_path, count in file_class_count.items():
            if count > 5:  # Too many classes threshold
                issue = CodeQualityIssue(
                    issue_type="structure",
                    severity="medium",
                    description=f"File {file_path} contains too many classes ({count})",
                    file_path=file_path,
                    line_number=1,
                    suggestion="Consider organizing classes into separate files or modules"
                )
                issues.append(issue)
                
        return issues
    
    def _analyze_documentation_quality(self, elements: List[CodeElement]) -> List[CodeQualityIssue]:
        """Analyze documentation quality"""
        issues = []
        
        for element in elements:
            if element.is_public:  # Only check public elements
                if not element.docstring:
                    severity = "high" if element.element_type == 'class' else "medium"
                    issue = CodeQualityIssue(
                        issue_type="documentation",
                        severity=severity,
                        description=f"{element.element_type.title()} {element.name} lacks documentation",
                        file_path=element.file_path,
                        line_number=element.line_number,
                        suggestion=f"Add comprehensive docstring to {element.element_type} {element.name}"
                    )
                    issues.append(issue)
                    
                elif len(element.docstring.strip()) < 20:  # Too brief
                    issue = CodeQualityIssue(
                        issue_type="documentation",
                        severity="low",
                        description=f"{element.element_type.title()} {element.name} has minimal documentation",
                        file_path=element.file_path,
                        line_number=element.line_number,
                        suggestion="Expand docstring with more detailed description, parameters, and return values"
                    )
                    issues.append(issue)
                    
        return issues
    
    def _calculate_quality_score(self, issues: List[CodeQualityIssue], 
                                implementation_data: ImplementationData) -> float:
        """Calculate overall quality score"""
        if not implementation_data.new_classes and not implementation_data.new_functions:
            return 100.0
            
        # Start with perfect score
        score = 100.0
        
        # Deduct points based on issues
        for issue in issues:
            if issue.severity == "critical":
                score -= 20
            elif issue.severity == "high":
                score -= 10
            elif issue.severity == "medium":
                score -= 5
            elif issue.severity == "low":
                score -= 2
                
        return max(score, 0.0)


class PerformanceAnalyzer:
    """Analyzes performance characteristics"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        
    def analyze_performance(self, implementation_data: ImplementationData) -> Tuple[float, List[PerformanceMetric]]:
        """Analyze performance metrics"""
        metrics = []
        
        # Analyze algorithmic complexity
        complexity_metrics = self._analyze_algorithmic_complexity(implementation_data.new_functions)
        metrics.extend(complexity_metrics)
        
        # Analyze memory usage patterns
        memory_metrics = self._analyze_memory_patterns(implementation_data)
        metrics.extend(memory_metrics)
        
        # Analyze database operations
        db_metrics = self._analyze_database_operations(implementation_data)
        metrics.extend(db_metrics)
        
        # Calculate performance score
        performance_score = self._calculate_performance_score(metrics)
        
        return performance_score, metrics
    
    def _analyze_algorithmic_complexity(self, functions: List[CodeElement]) -> List[PerformanceMetric]:
        """Analyze algorithmic complexity of functions"""
        metrics = []
        
        for func in functions:
            # Simple heuristic based on cyclomatic complexity
            estimated_time_complexity = "O(1)"
            if func.complexity > 20:
                estimated_time_complexity = "O(n²)"
            elif func.complexity > 10:
                estimated_time_complexity = "O(n log n)"
            elif func.complexity > 5:
                estimated_time_complexity = "O(n)"
                
            metric = PerformanceMetric(
                metric_name=f"Time Complexity - {func.name}",
                current_value=float(func.complexity),
                benchmark_value=10.0,  # Ideal complexity
                unit="complexity_points",
                trend="unknown",
                recommendation=f"Estimated {estimated_time_complexity} complexity"
            )
            metrics.append(metric)
            
        return metrics
    
    def _analyze_memory_patterns(self, implementation_data: ImplementationData) -> List[PerformanceMetric]:
        """Analyze memory usage patterns"""
        metrics = []
        
        # Estimate memory usage based on code patterns
        total_new_objects = len(implementation_data.new_classes)
        if total_new_objects > 0:
            metric = PerformanceMetric(
                metric_name="Memory Usage Estimate",
                current_value=float(total_new_objects * 100),  # Rough estimate in KB
                benchmark_value=500.0,  # 500KB baseline
                unit="KB",
                trend="unknown",
                recommendation="Monitor actual memory usage in production"
            )
            metrics.append(metric)
            
        return metrics
    
    def _analyze_database_operations(self, implementation_data: ImplementationData) -> List[PerformanceMetric]:
        """Analyze database operation efficiency"""
        metrics = []
        
        # Count potential database operations based on endpoints
        db_operations = 0
        for endpoint in implementation_data.new_endpoints:
            if endpoint.method in ['GET', 'POST', 'PUT', 'DELETE']:
                db_operations += 1
                
        if db_operations > 0:
            metric = PerformanceMetric(
                metric_name="Database Operations",
                current_value=float(db_operations),
                benchmark_value=5.0,  # Reasonable number
                unit="operations",
                trend="unknown",
                recommendation="Consider query optimization and caching strategies"
            )
            metrics.append(metric)
            
        return metrics
    
    def _calculate_performance_score(self, metrics: List[PerformanceMetric]) -> float:
        """Calculate overall performance score"""
        if not metrics:
            return 90.0  # Default good score if no metrics
            
        score = 100.0
        
        for metric in metrics:
            if metric.benchmark_value:
                ratio = metric.current_value / metric.benchmark_value
                if ratio > 2.0:  # Significantly worse than benchmark
                    score -= 20
                elif ratio > 1.5:
                    score -= 10
                elif ratio > 1.2:
                    score -= 5
                    
        return max(score, 0.0)


class SecurityAnalyzer:
    """Analyzes security aspects of the code"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        
    def analyze_security(self, implementation_data: ImplementationData) -> Tuple[float, List[SecurityFinding]]:
        """Analyze security aspects"""
        findings = []
        
        # Analyze authentication patterns
        auth_findings = self._analyze_authentication_security(implementation_data)
        findings.extend(auth_findings)
        
        # Analyze input validation
        input_findings = self._analyze_input_validation(implementation_data)
        findings.extend(input_findings)
        
        # Analyze data exposure
        exposure_findings = self._analyze_data_exposure(implementation_data)
        findings.extend(exposure_findings)
        
        # Calculate security score
        security_score = self._calculate_security_score(findings)
        
        return security_score, findings
    
    def _analyze_authentication_security(self, implementation_data: ImplementationData) -> List[SecurityFinding]:
        """Analyze authentication and authorization security"""
        findings = []
        
        # Check for authentication endpoints
        auth_endpoints = [ep for ep in implementation_data.new_endpoints 
                         if 'auth' in ep.path.lower() or 'login' in ep.path.lower()]
        
        for endpoint in auth_endpoints:
            if not endpoint.authentication_required:
                finding = SecurityFinding(
                    finding_type="vulnerability",
                    severity="high",
                    description=f"Authentication endpoint {endpoint.path} may lack proper security",
                    file_path=endpoint.file_path,
                    line_number=endpoint.line_number,
                    remediation="Implement proper authentication and authorization checks"
                )
                findings.append(finding)
                
        return findings
    
    def _analyze_input_validation(self, implementation_data: ImplementationData) -> List[SecurityFinding]:
        """Analyze input validation security"""
        findings = []
        
        # Check POST/PUT endpoints for potential input validation issues
        data_endpoints = [ep for ep in implementation_data.new_endpoints 
                         if ep.method in ['POST', 'PUT']]
        
        for endpoint in data_endpoints:
            finding = SecurityFinding(
                finding_type="misconfiguration",
                severity="medium",
                description=f"Data endpoint {endpoint.method} {endpoint.path} should validate input",
                file_path=endpoint.file_path,
                line_number=endpoint.line_number,
                remediation="Implement comprehensive input validation and sanitization"
            )
            findings.append(finding)
            
        return findings
    
    def _analyze_data_exposure(self, implementation_data: ImplementationData) -> List[SecurityFinding]:
        """Analyze potential data exposure issues"""
        findings = []
        
        # Check for potential sensitive data in class names
        sensitive_patterns = ['password', 'secret', 'key', 'token', 'credential']
        
        for cls in implementation_data.new_classes:
            cls_name_lower = cls.name.lower()
            for pattern in sensitive_patterns:
                if pattern in cls_name_lower:
                    finding = SecurityFinding(
                        finding_type="exposure",
                        severity="medium",
                        description=f"Class {cls.name} may handle sensitive data",
                        file_path=cls.file_path,
                        line_number=cls.line_number,
                        remediation="Ensure sensitive data is properly encrypted and not logged"
                    )
                    findings.append(finding)
                    break
                    
        return findings
    
    def _calculate_security_score(self, findings: List[SecurityFinding]) -> float:
        """Calculate overall security score"""
        score = 100.0
        
        for finding in findings:
            if finding.severity == "critical":
                score -= 25
            elif finding.severity == "high":
                score -= 15
            elif finding.severity == "medium":
                score -= 8
            elif finding.severity == "low":
                score -= 3
                
        return max(score, 0.0)


class OptimizationRecommendationEngine:
    """Generates optimization recommendations"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        
    def generate_recommendations(self, quality_issues: List[CodeQualityIssue],
                                performance_metrics: List[PerformanceMetric],
                                security_findings: List[SecurityFinding]) -> List[OptimizationRecommendation]:
        """Generate optimization recommendations based on analysis"""
        recommendations = []
        
        # Quality recommendations
        quality_recs = self._generate_quality_recommendations(quality_issues)
        recommendations.extend(quality_recs)
        
        # Performance recommendations
        perf_recs = self._generate_performance_recommendations(performance_metrics)
        recommendations.extend(perf_recs)
        
        # Security recommendations
        sec_recs = self._generate_security_recommendations(security_findings)
        recommendations.extend(sec_recs)
        
        # Sort by priority
        recommendations.sort(key=lambda x: {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}[x.priority])
        
        return recommendations
    
    def _generate_quality_recommendations(self, issues: List[CodeQualityIssue]) -> List[OptimizationRecommendation]:
        """Generate quality improvement recommendations"""
        recommendations = []
        
        # Group issues by type
        issue_groups = {}
        for issue in issues:
            issue_type = issue.issue_type
            if issue_type not in issue_groups:
                issue_groups[issue_type] = []
            issue_groups[issue_type].append(issue)
            
        # Generate recommendations for each issue type
        for issue_type, type_issues in issue_groups.items():
            if issue_type == "complexity":
                rec = OptimizationRecommendation(
                    category="quality",
                    priority="high",
                    title="Reduce Code Complexity",
                    description=f"Found {len(type_issues)} functions with high complexity. Consider refactoring.",
                    implementation_effort="medium",
                    expected_impact="high",
                    code_examples=[
                        "# Before: Complex function\ndef complex_function(data):\n    # 30+ lines with many conditions\n    pass",
                        "# After: Refactored\ndef process_data(data):\n    validated_data = validate_data(data)\n    return transform_data(validated_data)"
                    ]
                )
                recommendations.append(rec)
                
            elif issue_type == "documentation":
                rec = OptimizationRecommendation(
                    category="maintainability",
                    priority="medium", 
                    title="Improve Documentation",
                    description=f"Found {len(type_issues)} elements lacking documentation.",
                    implementation_effort="low",
                    expected_impact="medium",
                    code_examples=[
                        '"""Comprehensive docstring with description, parameters, and return values"""'
                    ]
                )
                recommendations.append(rec)
                
        return recommendations
    
    def _generate_performance_recommendations(self, metrics: List[PerformanceMetric]) -> List[OptimizationRecommendation]:
        """Generate performance improvement recommendations"""
        recommendations = []
        
        # Check for performance concerns
        has_complexity_issues = any("Complexity" in m.metric_name and m.current_value > 15 
                                   for m in metrics)
        
        if has_complexity_issues:
            rec = OptimizationRecommendation(
                category="performance",
                priority="high",
                title="Optimize Algorithm Complexity",
                description="High algorithmic complexity detected. Consider optimization.",
                implementation_effort="high",
                expected_impact="high",
                code_examples=[
                    "# Use appropriate data structures (sets vs lists for lookups)",
                    "# Consider caching for expensive operations",
                    "# Implement pagination for large data sets"
                ]
            )
            recommendations.append(rec)
            
        return recommendations
    
    def _generate_security_recommendations(self, findings: List[SecurityFinding]) -> List[OptimizationRecommendation]:
        """Generate security improvement recommendations"""
        recommendations = []
        
        if findings:
            critical_count = len([f for f in findings if f.severity == "critical"])
            high_count = len([f for f in findings if f.severity == "high"])
            
            if critical_count > 0 or high_count > 0:
                rec = OptimizationRecommendation(
                    category="security",
                    priority="critical" if critical_count > 0 else "high",
                    title="Address Security Vulnerabilities",
                    description=f"Found {critical_count} critical and {high_count} high severity security issues.",
                    implementation_effort="medium",
                    expected_impact="critical",
                    code_examples=[
                        "# Implement input validation",
                        "# Add authentication middleware",
                        "# Use parameterized queries",
                        "# Encrypt sensitive data"
                    ]
                )
                recommendations.append(rec)
                
        return recommendations


class OptimizationHealthMonitor:
    """
    Main monitor that coordinates all analysis components to provide
    comprehensive health assessment and optimization recommendations.
    """
    
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.quality_analyzer = CodeQualityAnalyzer(workspace_path)
        self.performance_analyzer = PerformanceAnalyzer(workspace_path)
        self.security_analyzer = SecurityAnalyzer(workspace_path)
        self.recommendation_engine = OptimizationRecommendationEngine(workspace_path)
        
    async def generate_health_report(self, implementation_data: ImplementationData) -> HealthReport:
        """
        Main orchestration method that generates comprehensive health report
        and optimization recommendations for implemented feature.
        """
        logger.info(f"Starting health analysis for feature: {implementation_data.feature_name}")
        
        # Analyze code quality
        quality_score, quality_issues = self.quality_analyzer.analyze_quality(implementation_data)
        
        # Analyze performance
        performance_score, performance_metrics = self.performance_analyzer.analyze_performance(implementation_data)
        
        # Analyze security
        security_score, security_findings = self.security_analyzer.analyze_security(implementation_data)
        
        # Generate recommendations
        recommendations = self.recommendation_engine.generate_recommendations(
            quality_issues, performance_metrics, security_findings
        )
        
        # Calculate overall health
        overall_score = (quality_score + performance_score + security_score) / 3
        health_status = self._determine_health_status(overall_score)
        
        # Count files analyzed
        files_analyzed = len(set(
            [issue.file_path for issue in quality_issues] +
            [finding.file_path for finding in security_findings] +
            [change.file_path for change in implementation_data.files_changed]
        ))
        
        report = HealthReport(
            feature_name=implementation_data.feature_name,
            analysis_timestamp=datetime.now(),
            quality_score=quality_score,
            quality_issues=quality_issues,
            performance_score=performance_score,
            performance_metrics=performance_metrics,
            security_score=security_score,
            security_findings=security_findings,
            recommendations=recommendations,
            overall_health_score=overall_score,
            health_status=health_status,
            files_analyzed=files_analyzed,
            issues_found=len(quality_issues) + len(security_findings),
            recommendations_generated=len(recommendations)
        )
        
        logger.info(f"Health analysis complete for {implementation_data.feature_name}: "
                   f"Overall score {overall_score:.1f}, {len(quality_issues)} quality issues, "
                   f"{len(security_findings)} security findings, {len(recommendations)} recommendations")
        
        return report
    
    def _determine_health_status(self, overall_score: float) -> str:
        """Determine health status based on overall score"""
        if overall_score >= 90:
            return "excellent"
        elif overall_score >= 75:
            return "good"
        elif overall_score >= 60:
            return "fair"
        else:
            return "poor"


if __name__ == "__main__":
    # Test optimization health monitor
    import asyncio
    from .implementation_discovery_engine import ImplementationData, CodeElement, APIEndpoint
    
    async def test_health_monitor():
        # Create test implementation data
        test_data = ImplementationData(
            feature_name="User Authentication System",
            discovery_timestamp=datetime.now(),
            new_classes=[
                CodeElement(
                    name="AuthService",
                    element_type="class",
                    file_path="src/auth/auth_service.py",
                    line_number=10,
                    docstring="Service for handling authentication",
                    complexity=8
                )
            ],
            new_functions=[
                CodeElement(
                    name="validate_credentials",
                    element_type="function",
                    file_path="src/auth/auth_service.py",
                    line_number=25,
                    complexity=18  # High complexity
                )
            ],
            new_endpoints=[
                APIEndpoint(
                    path="/auth/login",
                    method="POST",
                    handler_function="login",
                    file_path="src/auth/routes.py",
                    line_number=15
                )
            ]
        )
        
        monitor = OptimizationHealthMonitor("/Users/asifhussain/PROJECTS/CORTEX")
        report = await monitor.generate_health_report(test_data)
        
        print(f"Health Report for {report.feature_name}:")
        print(f"- Overall Health: {report.overall_health_score:.1f}/100 ({report.health_status})")
        print(f"- Quality Score: {report.quality_score:.1f}/100")
        print(f"- Performance Score: {report.performance_score:.1f}/100")
        print(f"- Security Score: {report.security_score:.1f}/100")
        print(f"- Files Analyzed: {report.files_analyzed}")
        print(f"- Issues Found: {report.issues_found}")
        print(f"- Recommendations: {report.recommendations_generated}")
        
        if report.recommendations:
            print("\nTop Recommendations:")
            for rec in report.recommendations[:3]:
                print(f"  - [{rec.priority.upper()}] {rec.title}")
    
    asyncio.run(test_health_monitor())