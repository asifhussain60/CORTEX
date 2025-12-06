"""
Dashboard Narrative Consolidator

Ensures all metrics tell one coherent story across all tabs.
Detects contradictions, calculates holistic scores, generates aligned recommendations.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class NarrativeIssue:
    """Represents a contradiction or misalignment in the data"""
    severity: str  # 'critical', 'high', 'medium', 'low'
    category: str
    description: str
    affected_tabs: List[str]
    evidence: Dict[str, Any]
    recommendation: str


class NarrativeConsolidator:
    """
    Consolidates dashboard data to ensure narrative consistency.
    All metrics must tell the same story - no contradictions.
    """
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.issues: List[NarrativeIssue] = []
        self.narrative_score = 0.0
        self.dominant_theme = ""
        
    def consolidate(self, all_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Consolidate all dashboard data into a coherent narrative.
        
        Args:
            all_data: Dict containing health, security, tech_stack, architecture, etc.
            
        Returns:
            Consolidated data with narrative_analysis section
        """
        # Extract key metrics
        metrics = self._extract_key_metrics(all_data)
        
        # Detect contradictions
        self._detect_contradictions(metrics, all_data)
        
        # Calculate holistic score (weighted by reality, not optimism)
        holistic_score = self._calculate_holistic_score(metrics)
        
        # Determine dominant narrative theme
        theme = self._determine_narrative_theme(metrics, all_data)
        
        # Generate aligned recommendations
        recommendations = self._generate_aligned_recommendations(metrics, all_data, theme)
        
        # Cross-validate all tabs support the same conclusion
        validation = self._cross_validate_narrative(all_data, theme, holistic_score)
        
        # Build consolidated narrative
        narrative = {
            'holistic_score': holistic_score,
            'dominant_theme': theme,
            'narrative_consistency': validation['consistency_score'],
            'contradictions': [
                {
                    'severity': issue.severity,
                    'category': issue.category,
                    'description': issue.description,
                    'affected_tabs': issue.affected_tabs,
                    'evidence': issue.evidence,
                    'recommendation': issue.recommendation
                }
                for issue in self.issues
            ],
            'aligned_recommendations': recommendations,
            'tab_alignment': validation['tab_alignment'],
            'story_summary': validation['story_summary']
        }
        
        # Inject narrative into all_data
        all_data['narrative_analysis'] = narrative
        
        # Adjust individual tab scores to align with narrative
        all_data = self._realign_tab_scores(all_data, holistic_score, theme)
        
        return all_data
    
    def _extract_key_metrics(self, all_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract critical metrics from all tabs"""
        return {
            'health_score': all_data.get('healthData', {}).get('overall_health_score', 0),
            'security_score': all_data.get('security', {}).get('overall_score', 0),
            'code_quality': all_data.get('codeOrganization', {}).get('quality_score', 0),
            'tech_debt_hours': all_data.get('codeOrganization', {}).get('total_debt_hours', 0),
            'test_coverage': all_data.get('healthData', {}).get('test_coverage', 0),
            'vulnerabilities': len(all_data.get('security', {}).get('vulnerabilities', [])),
            'hotspots': len(all_data.get('codeOrganization', {}).get('hotspots', [])),
            'architecture_tier': all_data.get('architecture', {}).get('tier_count', 0),
            'technologies_count': len(all_data.get('techStack', {}).get('technologies', [])),
            'contributors': all_data.get('teamMetrics', {}).get('total_contributors', 0)
        }
    
    def _detect_contradictions(self, metrics: Dict[str, Any], all_data: Dict[str, Any]):
        """Detect contradictions in the metrics"""
        
        # CRITICAL: High health score with zero security
        if metrics['health_score'] > 80 and metrics['security_score'] == 0:
            self.issues.append(NarrativeIssue(
                severity='critical',
                category='security_health_mismatch',
                description=f"Health score {metrics['health_score']} contradicts Security score {metrics['security_score']}",
                affected_tabs=['overview', 'security'],
                evidence={
                    'health_score': metrics['health_score'],
                    'security_score': metrics['security_score'],
                    'vulnerabilities': metrics['vulnerabilities']
                },
                recommendation="Security score of 0 indicates unscanned/failed security analysis. Re-run security collector or reduce health score to reflect security risk."
            ))
        
        # HIGH: Good health with massive tech debt
        if metrics['health_score'] > 80 and metrics['tech_debt_hours'] > 1000:
            self.issues.append(NarrativeIssue(
                severity='high',
                category='health_debt_mismatch',
                description=f"Health score {metrics['health_score']} ignores {metrics['tech_debt_hours']}h technical debt",
                affected_tabs=['overview', 'code_organization'],
                evidence={
                    'health_score': metrics['health_score'],
                    'tech_debt_hours': metrics['tech_debt_hours'],
                    'hotspots': metrics['hotspots']
                },
                recommendation=f"High technical debt ({metrics['tech_debt_hours']}h) should lower health score. Consider debt as 20% weight in overall calculation."
            ))
        
        # MEDIUM: Zero test coverage with high health
        if metrics['health_score'] > 70 and metrics['test_coverage'] == 0:
            self.issues.append(NarrativeIssue(
                severity='medium',
                category='testing_health_mismatch',
                description=f"Health score {metrics['health_score']} despite 0% test coverage",
                affected_tabs=['overview', 'code_organization'],
                evidence={
                    'health_score': metrics['health_score'],
                    'test_coverage': metrics['test_coverage']
                },
                recommendation="Zero test coverage indicates high risk. Reduce health score or flag as 'unvalidated health'."
            ))
        
        # Check for SQL injection risk in tech stack vs security findings
        tech_stack = all_data.get('techStack', {}).get('technologies', [])
        has_sql = any('sql' in tech.get('name', '').lower() for tech in tech_stack)
        sql_vulns = [v for v in all_data.get('security', {}).get('vulnerabilities', []) 
                     if 'sql' in v.get('type', '').lower() or 'injection' in v.get('type', '').lower()]
        
        if has_sql and len(sql_vulns) == 0:
            self.issues.append(NarrativeIssue(
                severity='high',
                category='sql_detection_missing',
                description="SQL technology detected but no SQL injection vulnerabilities scanned",
                affected_tabs=['tech_stack', 'security'],
                evidence={
                    'sql_technologies': [t['name'] for t in tech_stack if 'sql' in t.get('name', '').lower()],
                    'sql_vulnerabilities': len(sql_vulns)
                },
                recommendation="Run SQL injection pattern scan on inline SQL queries. Check for parameterized queries."
            ))
    
    def _calculate_holistic_score(self, metrics: Dict[str, Any]) -> float:
        """
        Calculate realistic holistic score using weighted average.
        Security issues heavily penalize the score.
        """
        weights = {
            'health': 0.20,
            'security': 0.30,  # Security is most critical
            'code_quality': 0.20,
            'test_coverage': 0.15,
            'tech_debt': 0.15
        }
        
        # Normalize tech debt (inverse - more debt = lower score)
        tech_debt_score = max(0, 100 - (metrics['tech_debt_hours'] / 100))  # 10,000h = 0 score
        
        # Calculate weighted score
        holistic = (
            metrics['health_score'] * weights['health'] +
            metrics['security_score'] * weights['security'] +
            metrics['code_quality'] * weights['code_quality'] +
            metrics['test_coverage'] * weights['test_coverage'] +
            tech_debt_score * weights['tech_debt']
        )
        
        # Apply penalties for critical issues
        if metrics['security_score'] == 0:
            holistic *= 0.5  # 50% penalty for no security scan
        
        if metrics['test_coverage'] == 0:
            holistic *= 0.9  # 10% penalty for no tests
        
        return round(holistic, 1)
    
    def _determine_narrative_theme(self, metrics: Dict[str, Any], all_data: Dict[str, Any]) -> str:
        """Determine the dominant narrative theme based on metrics"""
        
        # Critical security issues dominate
        if metrics['security_score'] < 50 or metrics['vulnerabilities'] > 100:
            return "security_critical"
        
        # High tech debt dominates
        if metrics['tech_debt_hours'] > 5000:
            return "technical_debt_crisis"
        
        # Good health across the board
        if metrics['health_score'] > 80 and metrics['security_score'] > 80 and metrics['code_quality'] > 70:
            return "healthy_codebase"
        
        # Needs modernization
        tech_stack = all_data.get('techStack', {}).get('technologies', [])
        legacy_count = sum(1 for t in tech_stack if t.get('status') == 'legacy')
        if legacy_count > 5:
            return "modernization_needed"
        
        # Moderate health, needs improvement
        return "maintenance_mode"
    
    def _generate_aligned_recommendations(self, metrics: Dict[str, Any], 
                                         all_data: Dict[str, Any], 
                                         theme: str) -> List[Dict[str, Any]]:
        """Generate recommendations that align with narrative theme"""
        recommendations = []
        
        # Theme-based priority recommendations
        if theme == "security_critical":
            recommendations.append({
                'priority': 'P0',
                'category': 'Security',
                'title': 'Immediate Security Audit Required',
                'description': f"Security score {metrics['security_score']} indicates critical vulnerabilities. Suspend deployments until resolution.",
                'effort': 'high',
                'impact': 'critical',
                'tabs': ['security', 'overview']
            })
        
        if theme == "technical_debt_crisis":
            recommendations.append({
                'priority': 'P0',
                'category': 'Technical Debt',
                'title': 'Tech Debt Reduction Sprint',
                'description': f"{metrics['tech_debt_hours']}h technical debt. Allocate 30% of sprint capacity to debt reduction.",
                'effort': 'high',
                'impact': 'high',
                'tabs': ['code_organization', 'overview']
            })
        
        # Issue-specific recommendations
        for issue in self.issues:
            if issue.severity in ['critical', 'high']:
                recommendations.append({
                    'priority': 'P0' if issue.severity == 'critical' else 'P1',
                    'category': issue.category,
                    'title': issue.description,
                    'description': issue.recommendation,
                    'effort': 'medium',
                    'impact': issue.severity,
                    'tabs': issue.affected_tabs
                })
        
        return recommendations[:5]  # Top 5 most critical
    
    def _cross_validate_narrative(self, all_data: Dict[str, Any], 
                                  theme: str, 
                                  holistic_score: float) -> Dict[str, Any]:
        """Validate all tabs support the same narrative"""
        
        tab_alignment = {
            'overview': self._check_overview_alignment(all_data, theme, holistic_score),
            'security': self._check_security_alignment(all_data, theme),
            'tech_stack': self._check_techstack_alignment(all_data, theme),
            'code_organization': self._check_codeorg_alignment(all_data, theme),
            'architecture': self._check_architecture_alignment(all_data, theme)
        }
        
        # Calculate consistency score (% of tabs aligned)
        aligned_count = sum(1 for alignment in tab_alignment.values() if alignment['aligned'])
        consistency_score = (aligned_count / len(tab_alignment)) * 100
        
        # Generate story summary
        story_summary = self._generate_story_summary(theme, holistic_score, tab_alignment)
        
        return {
            'consistency_score': round(consistency_score, 1),
            'tab_alignment': tab_alignment,
            'story_summary': story_summary
        }
    
    def _check_overview_alignment(self, all_data: Dict[str, Any], theme: str, holistic_score: float) -> Dict[str, Any]:
        """Check if overview tab aligns with narrative"""
        health = all_data.get('healthData', {}).get('overall_health_score', 0)
        aligned = abs(health - holistic_score) < 10  # Within 10 points
        
        return {
            'aligned': aligned,
            'message': 'Overview score matches holistic narrative' if aligned else 
                      f'Override needed: {health} → {holistic_score}'
        }
    
    def _check_security_alignment(self, all_data: Dict[str, Any], theme: str) -> Dict[str, Any]:
        """Check if security tab aligns with narrative"""
        security_score = all_data.get('security', {}).get('overall_score', 0)
        
        if theme == 'security_critical':
            aligned = security_score < 50
        elif theme == 'healthy_codebase':
            aligned = security_score > 70
        else:
            aligned = True  # Moderate themes accept any security score
        
        return {
            'aligned': aligned,
            'message': f'Security score {security_score} aligns with {theme}' if aligned else
                      f'Security score {security_score} conflicts with {theme} theme'
        }
    
    def _check_techstack_alignment(self, all_data: Dict[str, Any], theme: str) -> Dict[str, Any]:
        """Check if tech stack aligns with narrative"""
        tech_stack = all_data.get('techStack', {}).get('technologies', [])
        legacy_count = sum(1 for t in tech_stack if t.get('status') == 'legacy')
        
        if theme == 'modernization_needed':
            aligned = legacy_count > 3
        else:
            aligned = True
        
        return {
            'aligned': aligned,
            'message': f'{legacy_count} legacy technologies support {theme}' if aligned else
                      f'{legacy_count} legacy technologies conflict with {theme}'
        }
    
    def _check_codeorg_alignment(self, all_data: Dict[str, Any], theme: str) -> Dict[str, Any]:
        """Check if code organization aligns with narrative"""
        tech_debt = all_data.get('codeOrganization', {}).get('total_debt_hours', 0)
        
        if theme == 'technical_debt_crisis':
            aligned = tech_debt > 3000
        elif theme == 'healthy_codebase':
            aligned = tech_debt < 1000
        else:
            aligned = True
        
        return {
            'aligned': aligned,
            'message': f'{tech_debt}h debt aligns with {theme}' if aligned else
                      f'{tech_debt}h debt conflicts with {theme}'
        }
    
    def _check_architecture_alignment(self, all_data: Dict[str, Any], theme: str) -> Dict[str, Any]:
        """Check if architecture aligns with narrative"""
        # Architecture generally neutral unless specific patterns detected
        return {
            'aligned': True,
            'message': 'Architecture analysis complete'
        }
    
    def _generate_story_summary(self, theme: str, holistic_score: float, 
                               tab_alignment: Dict[str, Any]) -> str:
        """Generate human-readable story summary"""
        
        theme_descriptions = {
            'security_critical': f"🚨 CRITICAL: Security posture requires immediate attention (Score: {holistic_score}/100)",
            'technical_debt_crisis': f"⚠️ HIGH DEBT: Technical debt threatens maintainability (Score: {holistic_score}/100)",
            'healthy_codebase': f"✅ HEALTHY: Codebase shows strong health indicators (Score: {holistic_score}/100)",
            'modernization_needed': f"🔄 LEGACY: Technology stack needs modernization (Score: {holistic_score}/100)",
            'maintenance_mode': f"📊 STABLE: Moderate health, ongoing maintenance required (Score: {holistic_score}/100)"
        }
        
        return theme_descriptions.get(theme, f"Score: {holistic_score}/100")
    
    def _realign_tab_scores(self, all_data: Dict[str, Any], 
                           holistic_score: float, 
                           theme: str) -> Dict[str, Any]:
        """Adjust tab scores to align with holistic narrative"""
        
        # Override overview score with holistic score
        if 'healthData' in all_data:
            all_data['healthData']['overall_score'] = holistic_score
            all_data['healthData']['overall_health_score'] = holistic_score
            all_data['healthData']['score_type'] = 'holistic_weighted'
        
        # Add narrative context to each tab
        all_data['healthData']['narrative_theme'] = theme
        all_data.get('security', {})['narrative_theme'] = theme
        all_data.get('codeOrganization', {})['narrative_theme'] = theme
        
        return all_data


def consolidate_dashboard_data(repo_path: str, all_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point for narrative consolidation.
    
    Args:
        repo_path: Path to repository
        all_data: All collected dashboard data
        
    Returns:
        Consolidated data with narrative analysis
    """
    consolidator = NarrativeConsolidator(repo_path)
    return consolidator.consolidate(all_data)
