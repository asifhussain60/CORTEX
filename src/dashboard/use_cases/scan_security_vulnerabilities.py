"""
Use Case: Scan Security Vulnerabilities

Business logic for security vulnerability scanning and reporting.

Author: Asif Hussain
Created: 2025-11-30
CORTEX Version: 3.3.0
"""

from typing import Dict, Any, List
import logging

from src.dashboard.data.repository_interface import (
    IComponentRepository,
    IIssueRepository
)
from src.dashboard.domain import IssueType, IssueSeverity

logger = logging.getLogger(__name__)


class ScanSecurityVulnerabilitiesUseCase:
    """
    Use case for scanning and reporting security vulnerabilities.
    
    Provides data for security tab visualizations.
    """
    
    def __init__(
        self,
        component_repo: IComponentRepository,
        issue_repo: IIssueRepository
    ):
        """
        Initialize use case with repository dependencies.
        
        Args:
            component_repo: Component data access
            issue_repo: Issue data access
        """
        self.component_repo = component_repo
        self.issue_repo = issue_repo
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute use case to scan security vulnerabilities.
        
        Returns:
            Dict containing security analysis data
        """
        logger.info("Scanning security vulnerabilities")
        
        try:
            components = self.component_repo.get_all()
            security_issues = self.issue_repo.get_security_issues()
            
            # OWASP Top 10 mapping
            owasp_breakdown = self._map_to_owasp(security_issues)
            
            # CWE classification
            cwe_breakdown = self._classify_by_cwe(security_issues)
            
            # Severity distribution
            severity_distribution = self._analyze_severity(security_issues)
            
            # Vulnerable components
            vulnerable_components = self._identify_vulnerable_components(components, security_issues)
            
            # Security score
            security_score = self._calculate_security_score(components, security_issues)
            
            # Critical vulnerabilities needing immediate attention
            critical_vulns = [
                i for i in security_issues
                if i.severity in [IssueSeverity.BLOCKER, IssueSeverity.CRITICAL]
            ]
            
            security_data = {
                'total_vulnerabilities': len(security_issues),
                'critical_count': len(critical_vulns),
                'owasp_mapping': owasp_breakdown,
                'cwe_classification': cwe_breakdown,
                'severity_distribution': severity_distribution,
                'vulnerable_components': vulnerable_components,
                'security_score': security_score,
                'top_vulnerabilities': [
                    i.to_dict() for i in sorted(
                        security_issues,
                        key=lambda x: x.severity_rank
                    )[:10]
                ],
                'remediation_effort': self._estimate_remediation_effort(security_issues)
            }
            
            logger.info(f"Security scan complete: {len(security_issues)} vulnerabilities found")
            return security_data
            
        except Exception as e:
            logger.error(f"Error scanning security vulnerabilities: {e}")
            raise
    
    def _map_to_owasp(self, issues: List) -> Dict[str, Any]:
        """Map vulnerabilities to OWASP Top 10 categories"""
        owasp_map = {}
        
        for issue in issues:
            if issue.owasp_category:
                category = issue.owasp_category
                if category not in owasp_map:
                    owasp_map[category] = {
                        'count': 0,
                        'critical': 0,
                        'examples': []
                    }
                
                owasp_map[category]['count'] += 1
                
                if issue.is_high_priority:
                    owasp_map[category]['critical'] += 1
                
                if len(owasp_map[category]['examples']) < 3:
                    owasp_map[category]['examples'].append({
                        'title': issue.title,
                        'component': issue.component_path
                    })
        
        # Sort by count
        return dict(sorted(owasp_map.items(), key=lambda x: x[1]['count'], reverse=True))
    
    def _classify_by_cwe(self, issues: List) -> Dict[str, int]:
        """Classify vulnerabilities by CWE (Common Weakness Enumeration)"""
        cwe_map = {}
        
        for issue in issues:
            if issue.cwe_id:
                cwe_map[issue.cwe_id] = cwe_map.get(issue.cwe_id, 0) + 1
        
        return dict(sorted(cwe_map.items(), key=lambda x: x[1], reverse=True))
    
    def _analyze_severity(self, issues: List) -> Dict[str, Any]:
        """Analyze severity distribution of security issues"""
        distribution = {
            'blocker': len([i for i in issues if i.severity == IssueSeverity.BLOCKER]),
            'critical': len([i for i in issues if i.severity == IssueSeverity.CRITICAL]),
            'major': len([i for i in issues if i.severity == IssueSeverity.MAJOR]),
            'minor': len([i for i in issues if i.severity == IssueSeverity.MINOR])
        }
        
        return distribution
    
    def _identify_vulnerable_components(self, components: List, issues: List) -> List[Dict]:
        """Identify components with security vulnerabilities"""
        vulnerable = []
        
        for component in components:
            component_vulns = [i for i in issues if i.component_path == component.path]
            
            if component_vulns:
                critical_count = len([v for v in component_vulns if v.is_high_priority])
                
                vulnerable.append({
                    'name': component.name,
                    'path': component.path,
                    'vulnerability_count': len(component_vulns),
                    'critical_count': critical_count,
                    'security_issues': component.security_issues,
                    'risk_score': self._calculate_risk_score(component, component_vulns)
                })
        
        # Sort by risk score
        vulnerable.sort(key=lambda x: x['risk_score'], reverse=True)
        
        return vulnerable[:15]  # Top 15 most vulnerable
    
    def _calculate_risk_score(self, component, vulnerabilities: List) -> float:
        """Calculate risk score for component (higher = more risk)"""
        # Factors: vuln count, severity, component visibility (dependencies)
        vuln_weight = len(vulnerabilities) * 3
        severity_weight = sum(5 - v.severity_rank for v in vulnerabilities)
        exposure_weight = len(component.dependents) * 0.5  # More dependents = higher exposure
        
        return vuln_weight + severity_weight + exposure_weight
    
    def _calculate_security_score(self, components: List, issues: List) -> float:
        """Calculate overall security score (0-100, higher is better)"""
        if not components:
            return 100.0
        
        # Start at 100 and deduct points
        score = 100.0
        
        # Penalty for vulnerabilities
        vulns_per_component = len(issues) / len(components)
        vuln_penalty = min(vulns_per_component * 10, 50)  # Max 50 point penalty
        
        # Extra penalty for critical vulnerabilities
        critical_vulns = [i for i in issues if i.is_high_priority]
        critical_penalty = min(len(critical_vulns) * 5, 30)  # Max 30 point penalty
        
        score -= vuln_penalty
        score -= critical_penalty
        
        return max(0, round(score, 2))
    
    def _estimate_remediation_effort(self, issues: List) -> Dict[str, Any]:
        """Estimate effort to fix security vulnerabilities"""
        total_hours = sum(i.effort_minutes for i in issues) / 60.0
        
        critical_hours = sum(
            i.effort_minutes for i in issues
            if i.is_high_priority
        ) / 60.0
        
        return {
            'total_hours': round(total_hours, 2),
            'critical_hours': round(critical_hours, 2),
            'estimated_sprints': round(total_hours / 40, 1)  # Assuming 40 hours per sprint
        }
