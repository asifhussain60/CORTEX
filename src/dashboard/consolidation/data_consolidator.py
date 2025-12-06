"""
Data Consolidation Module

Cross-validates dashboard metrics, detects anomalies, triggers specialized deep scans,
calculates weighted holistic scores, and generates actionable recommendations.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ValidationIssue:
    """Represents a data quality issue"""
    severity: str  # critical, high, medium, low
    category: str  # consistency, accuracy, completeness
    metric: str
    issue: str
    impact: str
    recommended_action: str


@dataclass
class DeepScanTrigger:
    """Trigger for specialized deep scan"""
    scan_type: str
    reason: str
    target_path: str
    confidence: float


@dataclass
class ConsolidatedScore:
    """Holistic score with breakdown"""
    overall_health: float
    confidence: float
    weighted_components: Dict[str, float]
    anomalies_detected: int
    deep_scans_triggered: int


@dataclass
class Recommendation:
    """Actionable recommendation"""
    priority: str  # critical, high, medium, low
    category: str  # security, performance, maintainability, architecture
    title: str
    description: str
    impact: str
    effort: str  # high, medium, low
    affected_files: List[str]


class DataConsolidator:
    """
    Consolidates dashboard data with cross-validation, anomaly detection,
    and holistic scoring.
    """
    
    # Score weights for holistic calculation
    WEIGHTS = {
        'security': 0.30,      # Security is critical
        'code_quality': 0.25,  # Code quality impacts everything
        'architecture': 0.20,  # Architecture affects scalability
        'test_coverage': 0.15, # Testing ensures reliability
        'documentation': 0.10  # Documentation aids maintenance
    }
    
    # Validation thresholds
    THRESHOLDS = {
        'security_critical': 30,        # Security < 30 = critical
        'health_security_gap': 40,      # Health - Security gap > 40 = anomaly
        'debt_hours_per_kloc': 100,     # >100 hours/KLOC = high debt
        'min_test_coverage': 60,        # <60% coverage = risky
        'max_complexity_avg': 15        # >15 avg complexity = refactor needed
    }
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.validation_issues: List[ValidationIssue] = []
        self.deep_scan_triggers: List[DeepScanTrigger] = []
        self.recommendations: List[Recommendation] = []
        
    def consolidate(self, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main consolidation entry point.
        
        Args:
            collected_data: Raw data from all collectors
            
        Returns:
            Consolidated data with validation, scoring, and recommendations
        """
        print("🔍 Starting data consolidation...")
        
        # Step 1: Validate individual collectors
        self._validate_collector_outputs(collected_data)
        
        # Step 2: Cross-validate metrics
        self._cross_validate_metrics(collected_data)
        
        # Step 3: Detect anomalies
        anomalies = self._detect_anomalies(collected_data)
        
        # Step 4: Trigger specialized deep scans if needed
        if self.deep_scan_triggers:
            collected_data = self._execute_deep_scans(collected_data)
        
        # Step 5: Calculate holistic score
        consolidated_score = self._calculate_holistic_score(collected_data)
        
        # Step 6: Generate recommendations
        self._generate_recommendations(collected_data, anomalies)
        
        # Step 7: Package consolidated data
        result = {
            **collected_data,
            'consolidation': {
                'timestamp': datetime.now().isoformat(),
                'validation_issues': [asdict(issue) for issue in self.validation_issues],
                'anomalies': anomalies,
                'deep_scans_triggered': [asdict(trigger) for trigger in self.deep_scan_triggers],
                'holistic_score': asdict(consolidated_score),
                'recommendations': [asdict(rec) for rec in self.recommendations]
            }
        }
        
        print(f"✅ Consolidation complete: {len(self.validation_issues)} issues, "
              f"{len(anomalies)} anomalies, {len(self.recommendations)} recommendations")
        
        return result
    
    def _validate_collector_outputs(self, data: Dict[str, Any]) -> None:
        """Validate each collector's output for completeness and sanity"""
        
        # Health data validation
        health = data.get('health_data', {})
        if not health.get('overall_health_score'):
            self.validation_issues.append(ValidationIssue(
                severity='high',
                category='completeness',
                metric='health_data.overall_health_score',
                issue='Missing overall health score',
                impact='Cannot calculate holistic score',
                recommended_action='Re-run health data collector'
            ))
        
        # Security data validation
        security = data.get('security', {})
        if security.get('overall_score') == 0 and not security.get('vulnerabilities'):
            self.validation_issues.append(ValidationIssue(
                severity='critical',
                category='accuracy',
                metric='security.overall_score',
                issue='Security score is 0 but no vulnerabilities data',
                impact='May indicate failed security scan',
                recommended_action='Trigger deep security scan'
            ))
            # Trigger deep scan
            self.deep_scan_triggers.append(DeepScanTrigger(
                scan_type='security_deep_scan',
                reason='Zero security score with missing vulnerability data',
                target_path=str(self.repo_path),
                confidence=0.9
            ))
        
        # Code organization validation
        code_org = data.get('code_organization', {})
        if code_org.get('total_functions', 0) == 0:
            self.validation_issues.append(ValidationIssue(
                severity='high',
                category='completeness',
                metric='code_organization.total_functions',
                issue='No functions detected',
                impact='Code quality metrics unavailable',
                recommended_action='Verify code parser configuration'
            ))
    
    def _cross_validate_metrics(self, data: Dict[str, Any]) -> None:
        """Cross-validate metrics for consistency"""
        
        health_score = data.get('health_data', {}).get('overall_health_score', 0)
        security_score = data.get('security', {}).get('overall_score', 0)
        
        # Rule: If security is critical, health cannot be good
        if security_score < self.THRESHOLDS['security_critical'] and health_score > 70:
            gap = health_score - security_score
            self.validation_issues.append(ValidationIssue(
                severity='critical',
                category='consistency',
                metric='health_vs_security',
                issue=f'Health score ({health_score}) inconsistent with security score ({security_score})',
                impact='Misleading overall health assessment',
                recommended_action='Recalculate health with proper security weight'
            ))
        
        # Rule: High technical debt should lower code quality
        code_org = data.get('code_organization', {})
        debt_hours = code_org.get('technical_debt', {}).get('total_hours', 0)
        loc = data.get('health_data', {}).get('lines_of_code', 1)
        debt_per_kloc = (debt_hours / loc) * 1000 if loc > 0 else 0
        
        if debt_per_kloc > self.THRESHOLDS['debt_hours_per_kloc']:
            self.validation_issues.append(ValidationIssue(
                severity='high',
                category='consistency',
                metric='technical_debt',
                issue=f'High technical debt ({debt_hours:.1f}h for {loc} LOC = {debt_per_kloc:.1f}h/KLOC)',
                impact='Indicates significant maintainability issues',
                recommended_action='Prioritize debt reduction in hotspots'
            ))
    
    def _detect_anomalies(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect data anomalies and contradictions"""
        anomalies = []
        
        # Anomaly: Inline SQL without SQL injection detection
        tech_stack = data.get('tech_stack', {})
        security = data.get('security', {})
        
        # Check for database usage
        has_database = False
        for tech in tech_stack.get('technologies', []):
            if tech.get('category', '').lower() in ['database', 'data access']:
                has_database = True
                break
        
        # Check for SQL injection vulnerabilities
        sql_injection_found = False
        for vuln in security.get('vulnerabilities', []):
            if 'sql' in vuln.get('type', '').lower() or 'injection' in vuln.get('type', '').lower():
                sql_injection_found = True
                break
        
        if has_database and not sql_injection_found:
            anomalies.append({
                'type': 'missing_vulnerability_detection',
                'severity': 'high',
                'description': 'Database usage detected but no SQL injection analysis found',
                'evidence': 'Tech stack shows database technologies',
                'action': 'Trigger SQL injection deep scan'
            })
            # Trigger SQL injection deep scan
            self.deep_scan_triggers.append(DeepScanTrigger(
                scan_type='sql_injection_scan',
                reason='Database detected without SQL injection analysis',
                target_path=str(self.repo_path),
                confidence=0.85
            ))
        
        return anomalies
    
    def _execute_deep_scans(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute triggered deep scans"""
        print(f"🔬 Executing {len(self.deep_scan_triggers)} deep scans...")
        
        for trigger in self.deep_scan_triggers:
            if trigger.scan_type == 'sql_injection_scan':
                sql_results = self._deep_scan_sql_injection(trigger.target_path)
                # Merge into security data
                if 'security' not in data:
                    data['security'] = {}
                if 'deep_scans' not in data['security']:
                    data['security']['deep_scans'] = {}
                data['security']['deep_scans']['sql_injection'] = sql_results
                
            elif trigger.scan_type == 'security_deep_scan':
                # Re-run security collector with verbose mode
                print(f"  Re-running security collector for {trigger.target_path}")
                # Would call security collector here
        
        return data
    
    def _deep_scan_sql_injection(self, target_path: str) -> Dict[str, Any]:
        """Deep scan for SQL injection vulnerabilities"""
        from src.dashboard.consolidation.sql_injection_scanner import SQLInjectionScanner
        
        scanner = SQLInjectionScanner(target_path)
        return scanner.scan()
    
    def _calculate_holistic_score(self, data: Dict[str, Any]) -> ConsolidatedScore:
        """Calculate weighted holistic health score"""
        
        # Extract component scores
        security_score = data.get('security', {}).get('overall_score', 0)
        
        # Code quality from code organization
        code_org = data.get('code_organization', {})
        complexity_avg = code_org.get('complexity', {}).get('average', 10)
        code_quality = max(0, 100 - (complexity_avg * 5))  # Lower complexity = higher quality
        
        # Architecture score (simplified)
        arch = data.get('architecture', {})
        arch_score = 70  # Default neutral
        if arch.get('type') in ['microservices', 'event-driven']:
            arch_score = 85
        elif arch.get('type') in ['monolithic', 'legacy']:
            arch_score = 50
        
        # Test coverage
        test_coverage = data.get('health_data', {}).get('test_coverage', 0)
        
        # Documentation score (simplified)
        doc_score = 60  # Default
        
        # Calculate weighted score
        weighted = {
            'security': security_score * self.WEIGHTS['security'],
            'code_quality': code_quality * self.WEIGHTS['code_quality'],
            'architecture': arch_score * self.WEIGHTS['architecture'],
            'test_coverage': test_coverage * self.WEIGHTS['test_coverage'],
            'documentation': doc_score * self.WEIGHTS['documentation']
        }
        
        overall = sum(weighted.values())
        
        # Calculate confidence based on data completeness
        confidence = 1.0
        if len(self.validation_issues) > 0:
            confidence -= len([i for i in self.validation_issues if i.severity == 'critical']) * 0.2
            confidence -= len([i for i in self.validation_issues if i.severity == 'high']) * 0.1
            confidence = max(0.3, confidence)  # Minimum 30% confidence
        
        return ConsolidatedScore(
            overall_health=round(overall, 1),
            confidence=round(confidence, 2),
            weighted_components=weighted,
            anomalies_detected=len(self._detect_anomalies(data)),
            deep_scans_triggered=len(self.deep_scan_triggers)
        )
    
    def _generate_recommendations(self, data: Dict[str, Any], anomalies: List[Dict[str, Any]]) -> None:
        """Generate prioritized actionable recommendations"""
        
        security_score = data.get('security', {}).get('overall_score', 0)
        
        # Critical: Security issues
        if security_score < self.THRESHOLDS['security_critical']:
            self.recommendations.append(Recommendation(
                priority='critical',
                category='security',
                title='Address Critical Security Vulnerabilities',
                description=f'Security score is {security_score}/100, indicating severe vulnerabilities',
                impact='High risk of data breaches, unauthorized access, or system compromise',
                effort='high',
                affected_files=self._get_security_hotspots(data)
            ))
        
        # High: SQL injection if detected
        for anomaly in anomalies:
            if anomaly['type'] == 'missing_vulnerability_detection':
                self.recommendations.append(Recommendation(
                    priority='critical',
                    category='security',
                    title='Scan for SQL Injection Vulnerabilities',
                    description='Database usage detected without SQL injection analysis',
                    impact='Potential for SQL injection attacks leading to data theft or corruption',
                    effort='medium',
                    affected_files=self._get_database_files(data)
                ))
        
        # High: Technical debt
        code_org = data.get('code_organization', {})
        debt_hours = code_org.get('technical_debt', {}).get('total_hours', 0)
        if debt_hours > 1000:
            hotspots = code_org.get('hotspots', [])[:5]
            self.recommendations.append(Recommendation(
                priority='high',
                category='maintainability',
                title='Reduce Technical Debt in Hotspots',
                description=f'{debt_hours:.1f} hours of technical debt detected',
                impact='Increased maintenance costs, slower feature delivery, higher bug risk',
                effort='high',
                affected_files=[h.get('file', 'unknown') for h in hotspots]
            ))
        
        # Medium: Test coverage
        test_coverage = data.get('health_data', {}).get('test_coverage', 0)
        if test_coverage < self.THRESHOLDS['min_test_coverage']:
            self.recommendations.append(Recommendation(
                priority='medium',
                category='quality',
                title='Increase Test Coverage',
                description=f'Current coverage is {test_coverage}%, below {self.THRESHOLDS["min_test_coverage"]}% threshold',
                impact='Higher risk of regressions, difficulty in refactoring safely',
                effort='medium',
                affected_files=self._get_untested_files(data)
            ))
    
    def _get_security_hotspots(self, data: Dict[str, Any]) -> List[str]:
        """Extract files with security issues"""
        vulns = data.get('security', {}).get('vulnerabilities', [])
        files = []
        for vuln in vulns[:10]:  # Top 10
            if 'file' in vuln:
                files.append(vuln['file'])
        return files
    
    def _get_database_files(self, data: Dict[str, Any]) -> List[str]:
        """Extract files likely to contain database code"""
        # Simplified - would scan for SQL patterns
        return ['data_access_layer/*', 'repositories/*', 'services/*']
    
    def _get_untested_files(self, data: Dict[str, Any]) -> List[str]:
        """Extract files with no test coverage"""
        # Simplified - would analyze coverage data
        return ['untested_modules/*']
