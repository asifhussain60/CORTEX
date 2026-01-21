"""
CORTEX Templates - Quality Assurance Framework

Template quality assurance and testing framework.

Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from pathlib import Path
import json

from cortex.templates.content_strategy import ContentPopulationStrategy
from cortex.templates.template_manager import TemplateManager
from cortex.templates.template_validation import TemplateContentValidator


@dataclass
class CompletenessResult:
    """Template completeness check result."""
    score: float
    missing_sections: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


@dataclass
class ConsistencyResult:
    """Template consistency check result."""
    consistent: bool
    issues: List[str] = field(default_factory=list)


@dataclass
class TestSuiteResult:
    """QA test suite result."""
    passed: bool
    tests_run: int
    failures: List[str] = field(default_factory=list)


class QualityAssuranceFramework:
    """Quality assurance framework for templates.
    
    Provides quality checks, metrics, and testing for templates.
    """
    
    def __init__(self) -> None:
        """Initialize QA framework."""
        self._strategy = ContentPopulationStrategy()
        self._manager = TemplateManager()
        self._validator = TemplateContentValidator()
    
    def check_completeness(self, template_id: str) -> CompletenessResult:
        """Check template completeness.
        
        Args:
            template_id: Template ID to check.
            
        Returns:
            Completeness result.
        """
        content = self._manager.get_template_content(template_id)
        if content is None:
            return CompletenessResult(score=0.0, missing_sections=['content'])
        
        # Calculate completeness score
        score = 0.0
        missing = []
        suggestions = []
        
        # Check for header
        if '#' in content:
            score += 0.2
        else:
            missing.append('header')
            suggestions.append('Add a header section')
        
        # Check for variables
        if '{' in content and '}' in content:
            score += 0.2
        else:
            missing.append('variables')
            suggestions.append('Add variable placeholders')
        
        # Check for structure
        if '##' in content:
            score += 0.2
        else:
            missing.append('sections')
            suggestions.append('Add section headers')
        
        # Check minimum length
        if len(content) >= 100:
            score += 0.2
        else:
            suggestions.append('Expand content (< 100 chars)')
        
        # Check for description
        if 'overview' in content.lower() or 'description' in content.lower():
            score += 0.2
        else:
            missing.append('description')
        
        return CompletenessResult(
            score=score,
            missing_sections=missing,
            suggestions=suggestions,
        )
    
    def check_consistency(self, domain: str) -> ConsistencyResult:
        """Check template consistency within a domain.
        
        Args:
            domain: Domain to check.
            
        Returns:
            Consistency result.
        """
        templates = self._strategy.get_domain_templates(domain)
        issues = []
        
        # Check template count
        if len(templates) < 8:
            issues.append(f"Domain has only {len(templates)} templates (< 8)")
        
        # Check naming consistency
        prefixes = set()
        for template in templates:
            template_id = template['id']
            if '-' in template_id:
                prefix = template_id.split('-')[0]
                prefixes.add(prefix)
        
        if len(prefixes) > 2:
            issues.append(f"Inconsistent naming prefixes: {prefixes}")
        
        return ConsistencyResult(
            consistent=len(issues) == 0,
            issues=issues,
        )
    
    def check_coverage(self) -> Dict[str, float]:
        """Check domain coverage.
        
        Returns:
            Dictionary of domain to coverage score.
        """
        coverage = {}
        
        for domain in self._strategy.domains:
            templates = self._strategy.get_domain_templates(domain)
            
            # Calculate coverage based on template count
            count = len(templates)
            if count >= 10:
                coverage[domain] = 1.0
            elif count >= 8:
                coverage[domain] = 0.9
            else:
                coverage[domain] = count / 8.0
        
        return coverage
    
    def generate_metrics(self) -> Dict[str, Any]:
        """Generate quality metrics.
        
        Returns:
            Quality metrics dictionary.
        """
        validation_report = self._validator.validate_all()
        coverage = self.check_coverage()
        
        total_templates = self._strategy.total_template_count
        valid_templates = total_templates - len(validation_report.errors)
        
        return {
            'total_templates': total_templates,
            'valid_templates': valid_templates,
            'coverage_score': sum(coverage.values()) / len(coverage) if coverage else 0.0,
            'domains_covered': len(self._strategy.domains),
            'error_count': len(validation_report.errors),
            'warning_count': len(validation_report.warnings),
        }
    
    def lint_template(self, template_id: str) -> List[str]:
        """Lint template for issues.
        
        Args:
            template_id: Template ID to lint.
            
        Returns:
            List of issues found.
        """
        issues = []
        
        content = self._manager.get_template_content(template_id)
        if content is None:
            issues.append("Template content not found")
            return issues
        
        # Check for common issues
        if len(content) < 50:
            issues.append("Content is very short")
        
        # Check variable syntax
        result = self._validator.validate_variables(content)
        if not result.valid:
            issues.extend(result.errors)
        
        return issues
    
    def suggest_improvements(self, template_id: str) -> List[str]:
        """Suggest template improvements.
        
        Args:
            template_id: Template ID.
            
        Returns:
            List of improvement suggestions.
        """
        suggestions = []
        
        # Check completeness
        completeness = self.check_completeness(template_id)
        suggestions.extend(completeness.suggestions)
        
        # Check content length
        content = self._manager.get_template_content(template_id)
        if content and len(content) < 200:
            suggestions.append("Consider expanding content with more sections")
        
        return suggestions
    
    def compare_templates(
        self,
        template_id1: str,
        template_id2: str,
    ) -> Dict[str, Any]:
        """Compare two templates.
        
        Args:
            template_id1: First template ID.
            template_id2: Second template ID.
            
        Returns:
            Comparison dictionary.
        """
        content1 = self._manager.get_template_content(template_id1)
        content2 = self._manager.get_template_content(template_id2)
        
        if not content1 or not content2:
            return {
                'similarity': 0.0,
                'differences': ['One or both templates not found'],
            }
        
        # Simple similarity based on length ratio
        len1 = len(content1)
        len2 = len(content2)
        similarity = min(len1, len2) / max(len1, len2) if max(len1, len2) > 0 else 0.0
        
        differences = []
        if len1 != len2:
            differences.append(f"Length difference: {len1} vs {len2}")
        
        return {
            'similarity': similarity,
            'differences': differences,
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate QA report.
        
        Returns:
            QA report dictionary.
        """
        metrics = self.generate_metrics()
        coverage = self.check_coverage()
        
        recommendations = []
        
        # Check coverage
        for domain, score in coverage.items():
            if score < 0.9:
                recommendations.append(f"Improve {domain} coverage (currently {score:.1%})")
        
        # Check overall quality
        if metrics['error_count'] > 0:
            recommendations.append(f"Fix {metrics['error_count']} template errors")
        
        return {
            'summary': {
                'total_templates': metrics['total_templates'],
                'overall_quality': 'GOOD' if metrics['error_count'] == 0 else 'NEEDS_WORK',
            },
            'metrics': metrics,
            'recommendations': recommendations,
        }
    
    def run_full_suite(self) -> TestSuiteResult:
        """Run full QA test suite.
        
        Returns:
            Test suite result.
        """
        tests_run = 0
        failures = []
        
        # Test 1: Validate all templates
        tests_run += 1
        validation_report = self._validator.validate_all()
        if not validation_report.valid:
            failures.append(f"Validation failed: {len(validation_report.errors)} errors")
        
        # Test 2: Check coverage
        tests_run += 1
        coverage = self.check_coverage()
        if any(score < 0.8 for score in coverage.values()):
            failures.append("Coverage test failed: some domains < 80%")
        
        # Test 3: Check completeness for sample templates
        sample_templates = ['planning-recommendations', 'analysis-gap-assessment', 
                          'governance-compliance-report']
        for template_id in sample_templates:
            tests_run += 1
            completeness = self.check_completeness(template_id)
            if completeness.score < 0.7:
                failures.append(f"Completeness check failed for {template_id}")
        
        # Test 4: Check each domain consistency
        for domain in self._strategy.domains:
            tests_run += 1
            consistency = self.check_consistency(domain)
            if not consistency.consistent:
                failures.append(f"Consistency check failed for {domain}")
        
        return TestSuiteResult(
            passed=len(failures) == 0,
            tests_run=tests_run,
            failures=failures,
        )
    
    def export_results(self, output_path: str) -> None:
        """Export QA results to file.
        
        Args:
            output_path: Output file path.
        """
        report = self.generate_report()
        suite_result = self.run_full_suite()
        
        results = {
            'report': report,
            'test_suite': {
                'passed': suite_result.passed,
                'tests_run': suite_result.tests_run,
                'failures': suite_result.failures,
            },
        }
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
