"""
Health Assessor Crawler

Evaluates overall project health and provides recommendations.
"""

from typing import Dict, Any, List
from .base_crawler import BaseCrawler


class HealthAssessorCrawler(BaseCrawler):
    """
    Evaluates project health based on data from other crawlers:
    - Overall health score (0-10)
    - Risk factors
    - Opportunities for improvement
    - Strengths
    - Actionable recommendations
    """
    
    def __init__(self, project_root: str, crawler_results: Dict[str, Any] = None):
        """
        Initialize health assessor.
        
        Args:
            project_root: Project root directory
            crawler_results: Results from other crawlers (optional)
        """
        super().__init__(project_root)
        self.crawler_results = crawler_results or {}
    
    def get_name(self) -> str:
        return "Health Assessor"
    
    def crawl(self) -> Dict[str, Any]:
        """
        Assess project health based on crawler data.
        
        Returns:
            Dict containing health assessment
        """
        self.log_info("Starting health assessment")
        
        health_data = {
            'health_score': 0.0,
            'grade': 'F',
            'risks': [],
            'opportunities': [],
            'strengths': [],
            'recommendations': []
        }
        
        # Calculate health score
        health_data['health_score'] = self._calculate_health_score()
        health_data['grade'] = self._score_to_grade(health_data['health_score'])
        
        # Identify risks
        health_data['risks'] = self._identify_risks()
        
        # Identify opportunities
        health_data['opportunities'] = self._identify_opportunities()
        
        # Identify strengths
        health_data['strengths'] = self._identify_strengths()
        
        # Generate recommendations
        health_data['recommendations'] = self._generate_recommendations(
            health_data['risks'],
            health_data['opportunities']
        )
        
        self.log_info(
            f"Health assessment complete: {health_data['health_score']:.1f}/10 "
            f"({health_data['grade']})"
        )
        
        return {
            "success": True,
            "data": health_data
        }
    
    def _calculate_health_score(self) -> float:
        """
        Calculate overall health score (0-10) based on multiple factors.
        
        Returns:
            Health score from 0-10
        """
        score = 0.0
        max_score = 10.0
        
        # Test coverage (2.5 points)
        test_data = self._get_crawler_data('test_parser')
        if test_data:
            if test_data.get('total_tests', 0) > 0:
                score += 0.5
            if test_data.get('total_tests', 0) > 50:
                score += 0.5
            coverage = test_data.get('coverage', 0)
            if coverage >= 80:
                score += 1.5
            elif coverage >= 60:
                score += 1.0
            elif coverage >= 40:
                score += 0.5
        
        # Documentation (2 points)
        doc_data = self._get_crawler_data('doc_mapper')
        if doc_data:
            if doc_data.get('readme_exists'):
                score += 0.5
            readme_quality = doc_data.get('readme_quality', 0)
            score += (readme_quality / 10) * 1.0  # Up to 1 point
            if doc_data.get('total_docs', 0) > 20:
                score += 0.5
        
        # Git activity (1.5 points)
        git_data = self._get_crawler_data('git_analyzer')
        if git_data and git_data.get('is_git_repo'):
            if git_data.get('total_commits', 0) > 100:
                score += 0.5
            recent = git_data.get('recent_activity', {})
            if recent.get('last_7_days', 0) > 0:
                score += 0.5
            if recent.get('last_30_days', 0) > 10:
                score += 0.5
        
        # Brain health (2 points)
        brain_data = self._get_crawler_data('brain_inspector')
        if brain_data:
            brain_health = brain_data.get('brain_health', 0)
            score += (brain_health / 10) * 2.0
        
        # Enhancement health (1 point) - CORTEX 3.0 features
        enhancement_health = self._assess_enhancement_health()
        score += enhancement_health  # 0.0 to 1.0
        
        # Plugin system (1 point)
        plugin_data = self._get_crawler_data('plugin_registry')
        if plugin_data:
            init_rate = plugin_data.get('initialization_success_rate', 0)
            if init_rate >= 90:
                score += 1.0
            elif init_rate >= 70:
                score += 0.5
        
        # File organization (1 point)
        file_data = self._get_crawler_data('file_scanner')
        if file_data:
            if file_data.get('architecture_pattern') != 'custom':
                score += 0.5
            if len(file_data.get('frameworks', [])) > 0:
                score += 0.5
        
        return min(max_score, score)
    
    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 9.0:
            return 'A+'
        elif score >= 8.5:
            return 'A'
        elif score >= 8.0:
            return 'A-'
        elif score >= 7.5:
            return 'B+'
        elif score >= 7.0:
            return 'B'
        elif score >= 6.5:
            return 'B-'
        elif score >= 6.0:
            return 'C+'
        elif score >= 5.5:
            return 'C'
        elif score >= 5.0:
            return 'C-'
        elif score >= 4.0:
            return 'D'
        else:
            return 'F'
    
    def _identify_risks(self) -> List[Dict[str, Any]]:
        """Identify project risk factors."""
        risks = []
        
        # Test coverage risks
        test_data = self._get_crawler_data('test_parser')
        if test_data:
            coverage = test_data.get('coverage', 0)
            if coverage < 40:
                risks.append({
                    'type': 'low_test_coverage',
                    'severity': 'high',
                    'description': f'Test coverage is only {coverage:.1f}% (target: 80%+)',
                    'impact': 'Increased risk of bugs and regressions'
                })
            elif coverage < 60:
                risks.append({
                    'type': 'moderate_test_coverage',
                    'severity': 'medium',
                    'description': f'Test coverage is {coverage:.1f}% (target: 80%+)',
                    'impact': 'Some risk of undetected issues'
                })
        
        # Git activity risks
        git_data = self._get_crawler_data('git_analyzer')
        if git_data and git_data.get('is_git_repo'):
            stale_branches = git_data.get('branches', {}).get('stale', 0)
            if stale_branches > 5:
                risks.append({
                    'type': 'stale_branches',
                    'severity': 'low',
                    'description': f'{stale_branches} stale branches (inactive >90 days)',
                    'impact': 'Cluttered repository, potential merge conflicts'
                })
        
        # Documentation risks
        doc_data = self._get_crawler_data('doc_mapper')
        if doc_data:
            if not doc_data.get('readme_exists'):
                risks.append({
                    'type': 'missing_readme',
                    'severity': 'high',
                    'description': 'No README file found',
                    'impact': 'Poor onboarding experience for new developers'
                })
            
            undocumented = doc_data.get('undocumented_modules', 0)
            if undocumented > 10:
                risks.append({
                    'type': 'undocumented_modules',
                    'severity': 'medium',
                    'description': f'{undocumented} modules lack docstrings',
                    'impact': 'Harder to understand and maintain code'
                })
        
        return risks
    
    def _identify_opportunities(self) -> List[Dict[str, Any]]:
        """Identify improvement opportunities."""
        opportunities = []
        
        # Test opportunities
        test_data = self._get_crawler_data('test_parser')
        if test_data and test_data.get('total_tests', 0) < 100:
            opportunities.append({
                'type': 'expand_test_suite',
                'impact': 'medium',
                'suggestion': 'Add more tests to increase confidence',
                'benefit': 'Better code quality and faster debugging'
            })
        
        # Documentation opportunities
        doc_data = self._get_crawler_data('doc_mapper')
        if doc_data:
            if doc_data.get('api_docs', 0) < 5:
                opportunities.append({
                    'type': 'api_documentation',
                    'impact': 'medium',
                    'suggestion': 'Add API documentation for key modules',
                    'benefit': 'Easier integration and usage'
                })
        
        # Plugin opportunities
        plugin_data = self._get_crawler_data('plugin_registry')
        if plugin_data and plugin_data.get('total_plugins', 0) < 5:
            opportunities.append({
                'type': 'expand_plugins',
                'impact': 'low',
                'suggestion': 'Consider adding more plugins for extensibility',
                'benefit': 'More flexible and customizable system'
            })
        
        return opportunities
    
    def _identify_strengths(self) -> List[str]:
        """Identify project strengths."""
        strengths = []
        
        # Test strengths
        test_data = self._get_crawler_data('test_parser')
        if test_data:
            coverage = test_data.get('coverage', 0)
            if coverage >= 80:
                strengths.append(f"Excellent test coverage ({coverage:.1f}%)")
            
            total_tests = test_data.get('total_tests', 0)
            if total_tests > 100:
                strengths.append(f"Comprehensive test suite ({total_tests} tests)")
        
        # Git strengths
        git_data = self._get_crawler_data('git_analyzer')
        if git_data:
            recent = git_data.get('recent_activity', {})
            if recent.get('last_7_days', 0) > 10:
                strengths.append("High development activity")
        
        # Documentation strengths
        doc_data = self._get_crawler_data('doc_mapper')
        if doc_data:
            readme_quality = doc_data.get('readme_quality', 0)
            if readme_quality >= 8:
                strengths.append("High-quality README documentation")
            
            total_docs = doc_data.get('total_docs', 0)
            if total_docs > 50:
                strengths.append(f"Extensive documentation ({total_docs} files)")
        
        # Plugin strengths
        plugin_data = self._get_crawler_data('plugin_registry')
        if plugin_data:
            init_rate = plugin_data.get('initialization_success_rate', 0)
            if init_rate == 100:
                strengths.append("100% plugin initialization success")
        
        # Brain strengths
        brain_data = self._get_crawler_data('brain_inspector')
        if brain_data:
            brain_health = brain_data.get('brain_health', 0)
            if brain_health >= 8:
                strengths.append("Strong CORTEX brain health")
        
        return strengths
    
    def _generate_recommendations(self, risks: List[Dict], opportunities: List[Dict]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # High priority: Address high-severity risks
        high_risks = [r for r in risks if r.get('severity') == 'high']
        for risk in high_risks[:3]:  # Top 3 high risks
            if risk['type'] == 'low_test_coverage':
                recommendations.append("Add tests to critical modules to reach 80% coverage")
            elif risk['type'] == 'missing_readme':
                recommendations.append("Create a comprehensive README with setup and usage instructions")
        
        # Medium priority: Address medium-severity risks
        medium_risks = [r for r in risks if r.get('severity') == 'medium']
        for risk in medium_risks[:2]:  # Top 2 medium risks
            if risk['type'] == 'undocumented_modules':
                recommendations.append("Add docstrings to undocumented modules")
            elif risk['type'] == 'moderate_test_coverage':
                recommendations.append("Gradually increase test coverage to 80%+")
        
        # Opportunities
        for opp in opportunities[:2]:  # Top 2 opportunities
            recommendations.append(opp['suggestion'])
        
        return recommendations
    
    def _assess_enhancement_health(self) -> float:
        """
        Assess CORTEX 3.0 enhancement health.
        
        Returns:
            Health score from 0.0 to 1.0
        """
        score = 0.0
        
        try:
            import yaml
            from pathlib import Path
            
            project_root = Path(self.project_root)
            
            # Check meta-template system (0.25 points)
            meta_template = project_root / 'cortex-brain' / 'templates' / 'meta-template.yaml'
            validator = project_root / 'src' / 'validators' / 'template_validator.py'
            if meta_template.exists() and validator.exists():
                score += 0.25
            
            # Check confidence display (0.25 points)
            confidence_scorer = project_root / 'src' / 'cognitive' / 'confidence_scorer.py'
            if confidence_scorer.exists():
                score += 0.25
            
            # Check response templates (0.25 points)
            templates = project_root / 'cortex-brain' / 'response-templates.yaml'
            if templates.exists():
                with open(templates, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                template_count = len(data.get('templates', {}))
                if template_count >= 32:
                    score += 0.25
            
            # Check enhancement tests (0.25 points)
            enhancement_tests = project_root / 'tests' / 'integration' / 'test_cortex_enhancements.py'
            if enhancement_tests.exists():
                score += 0.25
            
        except Exception as e:
            self.log_warning(f"Enhancement health check failed: {e}")
        
        return score
    
    def _get_crawler_data(self, crawler_name: str) -> Dict[str, Any]:
        """
        Get data from a specific crawler.
        
        Args:
            crawler_name: Name of crawler (matches get_name() output)
            
        Returns:
            Crawler data or None
        """
        # Map crawler names to keys
        name_map = {
            'file_scanner': 'File Scanner',
            'git_analyzer': 'Git Analyzer',
            'test_parser': 'Test Parser',
            'doc_mapper': 'Documentation Mapper',
            'brain_inspector': 'Brain Inspector',
            'plugin_registry': 'Plugin Registry'
        }
        
        full_name = name_map.get(crawler_name)
        if not full_name:
            return None
        
        crawler_result = self.crawler_results.get(full_name, {})
        return crawler_result.get('data')
