"""
Recommendation Collector - Phase 7.5.1
Generates actionable recommendations across 5 categories

Categories:
1. Health Improvements (test coverage, code quality, documentation)
2. Performance Optimizations (slow endpoints, database queries, caching)
3. Security Hardening (validation, authentication, vulnerabilities)
4. Technical Debt Reduction (hotspots, duplication, dependencies)
5. E2E Test Coverage (integrated with prioritizer)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import Dict, List, Any
from pathlib import Path


class RecommendationCollector:
    """Collects and generates actionable recommendations from dashboard data"""
    
    # Priority thresholds
    PRIORITY_THRESHOLDS = {
        'critical': 'P0',
        'high': 'P1',
        'medium': 'P2',
        'low': 'P3'
    }
    
    # Impact keywords
    IMPACT_KEYWORDS = {
        'high': ['critical', 'security', 'data_loss', 'vulnerability', 'authentication'],
        'medium': ['performance', 'slow', 'complexity', 'duplication'],
        'low': ['documentation', 'formatting', 'naming']
    }
    
    # Effort keywords
    EFFORT_KEYWORDS = {
        'low': ['add_index', 'update_config', 'add_validation', 'fix_typo'],
        'medium': ['refactor_method', 'optimize_query', 'add_tests'],
        'high': ['refactor_architecture', 'redesign', 'migrate', 'rewrite']
    }
    
    def __init__(self, repo_path: str):
        """Initialize recommendation collector"""
        self.repo_path = Path(repo_path)
        self.recommendations = {
            'health_improvements': [],
            'performance': [],
            'security': [],
            'technical_debt': [],
            'e2e_testing': []
        }
    
    def collect(self, all_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect all recommendations from dashboard data
        
        Args:
            all_data: Complete dashboard data
            
        Returns:
            Dict with recommendations and summary
        """
        # Reset recommendations
        self.recommendations = {
            'health_improvements': [],
            'performance': [],
            'security': [],
            'technical_debt': [],
            'e2e_testing': []
        }
        
        # Generate recommendations from each data source
        health_data = all_data.get('healthData', {})
        if health_data:
            self.recommendations['health_improvements'].extend(
                self.generate_health_recommendations(health_data)
            )
        
        architecture_data = all_data.get('architecture', {})
        code_org_data = all_data.get('codeOrganization', {})
        if architecture_data or code_org_data:
            self.recommendations['performance'].extend(
                self.generate_performance_recommendations({**architecture_data, **code_org_data})
            )
        
        security_data = all_data.get('security', {})
        if security_data:
            self.recommendations['security'].extend(
                self.generate_security_recommendations(security_data)
            )
        
        heatmap_data = code_org_data.get('heatmap', code_org_data)
        if heatmap_data:
            self.recommendations['technical_debt'].extend(
                self.generate_technical_debt_recommendations(heatmap_data)
            )
        
        # Sort each category by priority
        for category in self.recommendations:
            self.recommendations[category] = self._sort_by_priority(self.recommendations[category])
        
        # Remove duplicates
        self._deduplicate_recommendations()
        
        # Calculate summary
        summary = self._calculate_summary()
        
        return {
            'recommendations': self.recommendations,
            'summary': summary
        }
    
    def generate_health_recommendations(self, health_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate health improvement recommendations"""
        recommendations = []
        
        # Test coverage
        coverage = health_data.get('test_coverage', 100)
        if coverage < 80:
            priority = 'P0' if coverage < 50 else 'P1' if coverage < 70 else 'P2'
            recommendations.append({
                'category': 'health',
                'priority': priority,
                'description': f'Increase test coverage from {coverage}% to at least 80%',
                'impact': 'high' if coverage < 50 else 'medium',
                'effort': 'high',
                'rationale': 'Low test coverage increases risk of regressions and bugs'
            })
        
        # Code complexity
        avg_complexity = health_data.get('avg_complexity', 0)
        if avg_complexity > 15:
            recommendations.append({
                'category': 'health',
                'priority': 'P1' if avg_complexity > 20 else 'P2',
                'description': f'Reduce average code complexity from {avg_complexity} to below 15',
                'impact': 'medium',
                'effort': 'high',
                'rationale': 'High complexity makes code harder to understand and maintain'
            })
        
        # Files over threshold
        files_over_threshold = health_data.get('files_over_threshold', 0)
        if files_over_threshold > 10:
            recommendations.append({
                'category': 'health',
                'priority': 'P2',
                'description': f'Refactor {files_over_threshold} files with complexity > 20',
                'impact': 'medium',
                'effort': 'high',
                'rationale': 'Complex files are bug-prone and difficult to test'
            })
        
        # Code quality score
        quality_score = health_data.get('code_quality_score', 100)
        if quality_score < 70:
            recommendations.append({
                'category': 'health',
                'priority': 'P2',
                'description': f'Improve code quality score from {quality_score} to above 70',
                'impact': 'medium',
                'effort': 'medium',
                'rationale': 'Code quality issues lead to technical debt accumulation'
            })
        
        return recommendations
    
    def generate_performance_recommendations(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # Slow endpoints
        endpoints = data.get('endpoints', [])
        for endpoint in endpoints:
            response_time = endpoint.get('avg_response_time', 0)
            if response_time > 1000:  # > 1 second
                recommendations.append({
                    'category': 'performance',
                    'priority': 'P1' if response_time > 3000 else 'P2',
                    'description': f"Optimize {endpoint.get('path', 'endpoint')} (response time: {response_time}ms)",
                    'impact': 'high' if response_time > 3000 else 'medium',
                    'effort': 'medium',
                    'rationale': 'Slow endpoints degrade user experience'
                })
        
        # Slow endpoints count
        slow_endpoints = data.get('slow_endpoints', 0)
        if slow_endpoints > 0:
            recommendations.append({
                'category': 'performance',
                'priority': 'P1' if slow_endpoints > 5 else 'P2',
                'description': f'Optimize {slow_endpoints} slow endpoints (>1s response time)',
                'impact': 'high',
                'effort': 'medium',
                'rationale': 'Slow endpoints impact user experience and scalability'
            })
        
        # N+1 queries
        n_plus_one = data.get('n_plus_one_queries', 0)
        if n_plus_one > 0:
            recommendations.append({
                'category': 'performance',
                'priority': 'P1',
                'description': f'Fix {n_plus_one} N+1 query issues',
                'impact': 'high',
                'effort': 'medium',
                'rationale': 'N+1 queries cause performance degradation at scale'
            })
        
        # Missing indexes
        missing_indexes = data.get('missing_indexes', 0)
        if missing_indexes > 0:
            recommendations.append({
                'category': 'performance',
                'priority': 'P2',
                'description': f'Add {missing_indexes} missing database indexes',
                'impact': 'medium',
                'effort': 'low',
                'rationale': 'Missing indexes slow down query performance'
            })
        
        return recommendations
    
    def generate_security_recommendations(self, security_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate security hardening recommendations"""
        recommendations = []
        
        # Critical vulnerabilities
        critical_vuln = security_data.get('critical_vulnerabilities', 0)
        if critical_vuln > 0:
            recommendations.append({
                'category': 'security',
                'priority': 'P0',
                'description': f'Fix {critical_vuln} critical security vulnerabilities immediately',
                'impact': 'high',
                'effort': 'high',
                'rationale': 'Critical vulnerabilities pose immediate security risk'
            })
        
        # SQL injection risks
        sql_injection = security_data.get('sql_injection_risks', 0)
        if sql_injection > 0:
            recommendations.append({
                'category': 'security',
                'priority': 'P0',
                'description': f'Fix {sql_injection} SQL injection vulnerabilities',
                'impact': 'high',
                'effort': 'medium',
                'rationale': 'SQL injection can lead to data breaches'
            })
        
        # Input validation
        validation_coverage = security_data.get('input_validation_coverage', 100)
        if validation_coverage < 80:
            recommendations.append({
                'category': 'security',
                'priority': 'P1',
                'description': f'Increase input validation coverage from {validation_coverage}% to 80%+',
                'impact': 'high',
                'effort': 'medium',
                'rationale': 'Missing input validation enables injection attacks'
            })
        
        # Vulnerable endpoints
        vuln_endpoints = security_data.get('vulnerable_endpoints', [])
        if vuln_endpoints:
            recommendations.append({
                'category': 'security',
                'priority': 'P1',
                'description': f'Secure {len(vuln_endpoints)} vulnerable endpoints: {", ".join(vuln_endpoints[:3])}',
                'impact': 'high',
                'effort': 'medium',
                'rationale': 'Vulnerable endpoints are attack vectors'
            })
        
        # Authentication issues
        auth_issues = security_data.get('auth_issues', [])
        if auth_issues:
            recommendations.append({
                'category': 'security',
                'priority': 'P1',
                'description': f'Fix authentication issues: {", ".join(auth_issues[:3])}',
                'impact': 'high',
                'effort': 'medium',
                'rationale': 'Authentication weaknesses enable unauthorized access'
            })
        
        # General vulnerabilities
        vulnerabilities = security_data.get('vulnerabilities', [])
        # Handle both list and int formats
        vuln_count = len(vulnerabilities) if isinstance(vulnerabilities, list) else (vulnerabilities if isinstance(vulnerabilities, int) else 0)
        if vuln_count > 0:
            recommendations.append({
                'category': 'security',
                'priority': 'P1',
                'description': f'Address {vuln_count} security vulnerabilities',
                'impact': 'high',
                'effort': 'medium',
                'rationale': 'Unpatched vulnerabilities increase security risk'
            })
        
        # Security score
        security_score = security_data.get('security_score', 100)
        if security_score < 70:
            recommendations.append({
                'category': 'security',
                'priority': 'P2',
                'description': f'Improve security posture from {security_score} to above 70',
                'impact': 'high',
                'effort': 'high',
                'rationale': 'Low security score indicates multiple vulnerabilities'
            })
        
        return recommendations
    
    def generate_technical_debt_recommendations(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate technical debt reduction recommendations"""
        recommendations = []
        
        # Hotspots
        hotspots = data.get('hotspots', [])
        for hotspot in hotspots[:5]:  # Top 5
            file = hotspot.get('file', 'unknown')
            complexity = hotspot.get('complexity', 0)
            change_freq = hotspot.get('change_frequency', 0)
            
            if complexity > 20 and change_freq > 15:
                recommendations.append({
                    'category': 'technical_debt',
                    'priority': 'P1',
                    'description': f'Refactor hotspot: {file} (complexity: {complexity}, changes: {change_freq})',
                    'impact': 'high',
                    'effort': 'high',
                    'rationale': 'Hotspots are risky and expensive to maintain'
                })
        
        # Code duplication
        duplication = data.get('duplication_percentage', 0)
        if duplication > 10:
            duplicate_blocks = data.get('duplicate_blocks', 0)
            recommendations.append({
                'category': 'technical_debt',
                'priority': 'P2',
                'description': f'Reduce code duplication from {duplication}% to below 10% ({duplicate_blocks} duplicate blocks)',
                'impact': 'medium',
                'effort': 'high',
                'rationale': 'Code duplication increases maintenance burden'
            })
        
        return recommendations
    
    def calculate_impact(self, category: str, issue_type: str) -> str:
        """Calculate impact level for a recommendation"""
        issue_lower = issue_type.lower()
        
        for level, keywords in self.IMPACT_KEYWORDS.items():
            if any(kw in issue_lower for kw in keywords):
                return level
        
        # Category-based defaults
        if category == 'security':
            return 'high'
        elif category in ['performance', 'health']:
            return 'medium'
        else:
            return 'low'
    
    def estimate_effort(self, task_type: str) -> str:
        """Estimate effort level for a recommendation"""
        task_lower = task_type.lower()
        
        for level, keywords in self.EFFORT_KEYWORDS.items():
            if any(kw in task_lower for kw in keywords):
                return level
        
        # Default to medium
        return 'medium'
    
    def _sort_by_priority(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort recommendations by priority (P0 > P1 > P2 > P3)"""
        priority_order = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
        
        def get_priority_value(rec):
            """Extract priority value safely"""
            priority = rec.get('priority', 'P3')
            # Handle case where priority is a dict or other non-string type
            if not isinstance(priority, str):
                return 3  # Default to lowest priority
            return priority_order.get(priority.upper(), 3)
        
        return sorted(recommendations, key=get_priority_value)
    
    def _deduplicate_recommendations(self):
        """Remove duplicate recommendations across categories"""
        seen_descriptions = set()
        
        for category in self.recommendations:
            unique_recs = []
            for rec in self.recommendations[category]:
                desc = rec['description']
                if desc not in seen_descriptions:
                    seen_descriptions.add(desc)
                    unique_recs.append(rec)
            self.recommendations[category] = unique_recs
    
    def _calculate_summary(self) -> Dict[str, Any]:
        """Calculate summary statistics"""
        all_recs = []
        for category_recs in self.recommendations.values():
            all_recs.extend(category_recs)
        
        by_priority = {
            'P0': sum(1 for r in all_recs if r['priority'] == 'P0'),
            'P1': sum(1 for r in all_recs if r['priority'] == 'P1'),
            'P2': sum(1 for r in all_recs if r['priority'] == 'P2'),
            'P3': sum(1 for r in all_recs if r['priority'] == 'P3')
        }
        
        by_category = {
            category: len(recs) 
            for category, recs in self.recommendations.items()
        }
        
        return {
            'total_recommendations': len(all_recs),
            'by_priority': by_priority,
            'by_category': by_category
        }
