#!/usr/bin/env python3
"""
Recommendations Engine

Generates prioritized recommendations from security, quality, and architecture analysis.
Provides actionable suggestions with effort/impact scoring.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Recommendation:
    """A single recommendation"""
    id: str
    category: str  # 'security', 'quality', 'performance', 'architecture', 'dependencies'
    priority: str  # 'critical', 'high', 'medium', 'low'
    title: str
    description: str
    rationale: str
    impact: str  # 'high', 'medium', 'low'
    effort: str  # 'high', 'medium', 'low'
    tags: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)
    code_example: Optional[str] = None


class RecommendationsEngine:
    """Generates recommendations from analysis results"""
    
    # Severity to priority mapping
    SEVERITY_TO_PRIORITY = {
        'critical': 'critical',
        'high': 'high',
        'medium': 'medium',
        'low': 'low'
    }
    
    def __init__(self):
        self.recommendations: List[Recommendation] = []
        self._counter = 0
    
    def generate_recommendations(
        self,
        security_issues: List[Any],
        quality_issues: List[Any],
        tech_stack: Dict[str, Any],
        architecture: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate comprehensive recommendations
        
        Args:
            security_issues: List of security vulnerabilities
            quality_issues: List of code quality issues
            tech_stack: Technology stack analysis
            architecture: Architecture graph data
            
        Returns:
            List of recommendations sorted by priority
        """
        logger.info("Generating recommendations...")
        
        self.recommendations = []
        
        # Generate security recommendations
        self._generate_security_recommendations(security_issues)
        
        # Generate quality recommendations
        self._generate_quality_recommendations(quality_issues)
        
        # Generate architecture recommendations
        self._generate_architecture_recommendations(architecture)
        
        # Generate dependency recommendations
        self._generate_dependency_recommendations(tech_stack)
        
        # Sort by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        self.recommendations.sort(key=lambda r: priority_order.get(r.priority, 4))
        
        logger.info(f"Generated {len(self.recommendations)} recommendations")
        
        # Convert to dict format
        return [self._recommendation_to_dict(r) for r in self.recommendations]
    
    def _generate_security_recommendations(self, issues: List[Any]):
        """Generate security-focused recommendations"""
        if not issues:
            return
        
        # Group by vulnerability type
        vuln_types = {}
        for issue in issues:
            vuln_type = getattr(issue, 'vulnerability_type', 'unknown')
            if vuln_type not in vuln_types:
                vuln_types[vuln_type] = []
            vuln_types[vuln_type].append(issue)
        
        # Generate recommendations for each type
        for vuln_type, vulns in vuln_types.items():
            severity = getattr(vulns[0], 'severity', 'medium')
            
            rec = Recommendation(
                id=self._get_next_id(),
                category='security',
                priority=self.SEVERITY_TO_PRIORITY.get(severity, 'medium'),
                title=f"Address {len(vulns)} {vuln_type.replace('_', ' ').title()} Issue(s)",
                description=f"Found {len(vulns)} instances of {vuln_type} vulnerabilities",
                rationale=self._get_security_rationale(vuln_type),
                impact='high' if severity in ['critical', 'high'] else 'medium',
                effort=self._estimate_effort(len(vulns)),
                tags=['security', vuln_type],
                resources=self._get_security_resources(vuln_type)
            )
            self.recommendations.append(rec)
        
        # Add general security recommendation if many issues
        if len(issues) > 50:
            rec = Recommendation(
                id=self._get_next_id(),
                category='security',
                priority='high',
                title='Conduct Comprehensive Security Audit',
                description=f'Project has {len(issues)} security issues requiring systematic review',
                rationale='High number of vulnerabilities suggests need for holistic security review',
                impact='high',
                effort='high',
                tags=['security', 'audit'],
                resources=[
                    'https://owasp.org/www-project-top-ten/',
                    'https://cheatsheetseries.owasp.org/'
                ]
            )
            self.recommendations.append(rec)
    
    def _generate_quality_recommendations(self, issues: List[Any]):
        """Generate code quality recommendations"""
        if not issues:
            return
        
        # Categorize quality issues
        issue_types = {}
        for issue in issues:
            issue_type = getattr(issue, 'type', 'unknown')
            if issue_type not in issue_types:
                issue_types[issue_type] = []
            issue_types[issue_type].append(issue)
        
        for issue_type, issue_list in issue_types.items():
            if len(issue_list) > 5:  # Only recommend if significant number
                rec = Recommendation(
                    id=self._get_next_id(),
                    category='quality',
                    priority='medium',
                    title=f"Improve {issue_type.replace('_', ' ').title()}",
                    description=f"Found {len(issue_list)} {issue_type} issues affecting code quality",
                    rationale=self._get_quality_rationale(issue_type),
                    impact='medium',
                    effort=self._estimate_effort(len(issue_list)),
                    tags=['quality', issue_type]
                )
                self.recommendations.append(rec)
    
    def _generate_architecture_recommendations(self, architecture: Dict[str, Any]):
        """Generate architecture recommendations"""
        if not architecture or 'metadata' not in architecture:
            return
        
        metadata = architecture['metadata']
        
        # Check layer distribution
        layers = metadata.get('layers', {})
        if layers.get('unknown', 0) > layers.get('domain', 0):
            rec = Recommendation(
                id=self._get_next_id(),
                category='architecture',
                priority='medium',
                title='Improve Architectural Layer Organization',
                description='Many components lack clear layer assignment',
                rationale='Clear layering improves maintainability and testability',
                impact='high',
                effort='high',
                tags=['architecture', 'layers'],
                resources=[
                    'https://en.wikipedia.org/wiki/Multitier_architecture',
                    'Clean Architecture by Robert C. Martin'
                ]
            )
            self.recommendations.append(rec)
        
        # Check module coupling
        total_nodes = metadata.get('total_nodes', 0)
        total_edges = metadata.get('total_edges', 0)
        
        if total_nodes > 0:
            coupling_ratio = total_edges / total_nodes
            if coupling_ratio > 3:  # High coupling
                rec = Recommendation(
                    id=self._get_next_id(),
                    category='architecture',
                    priority='medium',
                    title='Reduce Module Coupling',
                    description=f'Average coupling ratio of {coupling_ratio:.1f} suggests tight coupling',
                    rationale='Lower coupling improves modularity and testability',
                    impact='high',
                    effort='high',
                    tags=['architecture', 'coupling'],
                    resources=['https://en.wikipedia.org/wiki/Coupling_(computer_programming)']
                )
                self.recommendations.append(rec)
    
    def _generate_dependency_recommendations(self, tech_stack: Dict[str, Any]):
        """Generate dependency and tech stack recommendations"""
        if not tech_stack:
            return
        
        dependencies = tech_stack.get('dependencies', {})
        
        # Check for outdated dependencies
        total_deps = sum(len(deps) for deps in dependencies.values())
        if total_deps > 100:
            rec = Recommendation(
                id=self._get_next_id(),
                category='dependencies',
                priority='low',
                title='Review and Update Dependencies',
                description=f'Project has {total_deps} dependencies - review for updates',
                rationale='Regular dependency updates improve security and performance',
                impact='medium',
                effort='medium',
                tags=['dependencies', 'maintenance']
            )
            self.recommendations.append(rec)
        
        # Check for missing documentation
        languages = tech_stack.get('languages', [])
        if languages and not self._has_documentation():
            rec = Recommendation(
                id=self._get_next_id(),
                category='quality',
                priority='medium',
                title='Add Comprehensive Documentation',
                description='Project lacks comprehensive documentation',
                rationale='Good documentation improves onboarding and maintainability',
                impact='high',
                effort='medium',
                tags=['documentation', 'quality']
            )
            self.recommendations.append(rec)
    
    def _get_security_rationale(self, vuln_type: str) -> str:
        """Get rationale for security vulnerability type"""
        rationales = {
            'sql_injection': 'SQL injection can lead to data breaches and unauthorized access',
            'xss': 'Cross-site scripting enables attackers to execute malicious scripts',
            'hardcoded_credentials': 'Hardcoded credentials can be easily discovered and exploited',
            'insecure_random': 'Insecure randomness weakens cryptographic operations',
            'path_traversal': 'Path traversal allows unauthorized file system access'
        }
        return rationales.get(vuln_type, f'{vuln_type} poses security risks')
    
    def _get_quality_rationale(self, issue_type: str) -> str:
        """Get rationale for quality issue type"""
        rationales = {
            'file_length': 'Large files are harder to understand and maintain',
            'complexity': 'High complexity increases bug risk and maintenance cost',
            'duplication': 'Code duplication makes changes error-prone',
            'todo_comment': 'TODO comments indicate incomplete work',
            'naming': 'Poor naming conventions reduce code readability'
        }
        return rationales.get(issue_type, f'{issue_type} affects code quality')
    
    def _get_security_resources(self, vuln_type: str) -> List[str]:
        """Get educational resources for vulnerability type"""
        resources = {
            'sql_injection': [
                'https://owasp.org/www-community/attacks/SQL_Injection',
                'https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html'
            ],
            'xss': [
                'https://owasp.org/www-community/attacks/xss/',
                'https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html'
            ]
        }
        return resources.get(vuln_type, ['https://owasp.org/'])
    
    def _estimate_effort(self, issue_count: int) -> str:
        """Estimate effort based on issue count"""
        if issue_count < 5:
            return 'low'
        elif issue_count < 20:
            return 'medium'
        else:
            return 'high'
    
    def _has_documentation(self) -> bool:
        """Check if project has documentation (simplified)"""
        # This is a placeholder - could check for README, docs/ folder, etc.
        return False
    
    def _get_next_id(self) -> str:
        """Get next recommendation ID"""
        self._counter += 1
        return f"REC-{self._counter:04d}"
    
    def _recommendation_to_dict(self, rec: Recommendation) -> Dict[str, Any]:
        """Convert Recommendation to dictionary"""
        return {
            'id': rec.id,
            'category': rec.category,
            'priority': rec.priority,
            'title': rec.title,
            'description': rec.description,
            'rationale': rec.rationale,
            'impact': rec.impact,
            'effort': rec.effort,
            'tags': rec.tags,
            'resources': rec.resources,
            'code_example': rec.code_example
        }


def generate_recommendations_json(
    security_issues: List[Any],
    quality_issues: List[Any],
    tech_stack: Dict[str, Any],
    architecture: Dict[str, Any],
    output_path
) -> List[Dict[str, Any]]:
    """
    Generate recommendations.json
    
    Args:
        security_issues: Security vulnerability list
        quality_issues: Code quality issue list
        tech_stack: Tech stack analysis
        architecture: Architecture graph
        output_path: Path to save recommendations.json
        
    Returns:
        List of recommendations
    """
    import json
    
    engine = RecommendationsEngine()
    recommendations = engine.generate_recommendations(
        security_issues, quality_issues, tech_stack, architecture
    )
    
    # Save to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(recommendations, f, indent=2)
    
    logger.info(f"Recommendations saved to {output_path}")
    return recommendations
