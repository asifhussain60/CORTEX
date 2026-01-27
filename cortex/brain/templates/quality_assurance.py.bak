"""
AC-TC-003-02: Quality Assurance Framework

Provides quality assurance tools for templates including
completeness checking, consistency validation, and metrics.

"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import json


@dataclass
class CompletenessResult:
    """Result of completeness check."""
    score: float  # 0.0 to 1.0
    missing: List[str] = field(default_factory=list)
    present: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConsistencyResult:
    """Result of consistency check."""
    consistent: bool
    issues: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QASuiteResult:
    """Result of running full QA suite."""
    passed: bool
    tests_run: int = 0
    tests_passed: int = 0
    failures: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)


class QualityAssuranceFramework:
    """
    Quality assurance framework for templates.
    
    Provides completeness checking, consistency validation,
    coverage analysis, and quality metrics generation.
    """
    
    # Required elements for completeness
    REQUIRED_ELEMENTS = {
        'metadata': ['template_id', 'version', 'domain'],
        'template': ['structure'],
        'content': [],  # Content is optional but checked for quality
    }
    
    # Expected variable patterns per domain
    EXPECTED_VARIABLES: Dict[str, Set[str]] = {
        'planning': {'plan_title', 'phase', 'ac_count', 'estimated_hours'},
        'analysis': {'files_analyzed', 'issues_found', 'recommendations'},
        'validation': {'schema', 'valid', 'errors'},
        'execution': {'task', 'status', 'duration'},
        'system': {'component', 'status', 'metrics'},
        'governance': {'rules_checked', 'passed', 'failed'},
    }
    
    def __init__(self, template_base_path: Optional[Path] = None):
        """
        Initialize QA framework.
        
        Args:
            template_base_path: Base path for templates
        """
        if template_base_path is None:
            self.template_base_path = Path(__file__).parent.parent.parent / "cortex_brain" / "tier2"
        else:
            self.template_base_path = Path(template_base_path)
        
        from .content_strategy import ContentPopulationStrategy
        from .template_manager import TemplateManager
        
        self._strategy = ContentPopulationStrategy(self.template_base_path)
        self._manager = TemplateManager(self.template_base_path)
    
    def check_completeness(self, template_id: str) -> CompletenessResult:
        """
        Check template completeness.
        
        Args:
            template_id: Template identifier
            
        Returns:
            Completeness result with score
        """
        template = self._strategy.get_template_by_id(template_id)
        
        if not template:
            return CompletenessResult(
                score=0.0,
                missing=['template not found'],
            )
        
        # Check required fields
        present = []
        missing = []
        
        # Check basic metadata
        for field in ['id', 'name', 'description', 'domain']:
            if template.get(field):
                present.append(f'metadata.{field}')
            else:
                missing.append(f'metadata.{field}')
        
        # Check for content
        content = self._manager.get_template_content(template_id)
        if content and len(content) > 100:
            present.append('content')
        else:
            missing.append('content (sufficient length)')
        
        # Check for variables
        variables = template.get('variables', [])
        if variables:
            present.append(f'variables ({len(variables)})')
        else:
            missing.append('variables')
        
        # Calculate score
        total = len(present) + len(missing)
        score = len(present) / total if total > 0 else 0.0
        
        return CompletenessResult(
            score=score,
            missing=missing,
            present=present,
            details={'template_id': template_id},
        )
    
    def check_consistency(self, domain: str) -> ConsistencyResult:
        """
        Check consistency within a domain.
        
        Args:
            domain: Domain name
            
        Returns:
            Consistency result
        """
        templates = self._strategy.get_domain_templates(domain)
        issues = []
        
        if not templates:
            return ConsistencyResult(
                consistent=False,
                issues=[f"No templates found for domain: {domain}"],
            )
        
        # Check naming consistency
        for template in templates:
            tid = template['id']
            if not tid.startswith(f"{domain}-"):
                issues.append(f"Template {tid} doesn't follow domain prefix convention")
        
        # Check variable consistency
        expected_vars = self.EXPECTED_VARIABLES.get(domain, set())
        if expected_vars:
            for template in templates:
                template_vars = set(template.get('variables', []))
                common_vars = template_vars & expected_vars
                if len(common_vars) < len(expected_vars) * 0.5:
                    issues.append(
                        f"Template {template['id']} missing common domain variables"
                    )
        
        return ConsistencyResult(
            consistent=len(issues) == 0,
            issues=issues,
            details={'domain': domain, 'template_count': len(templates)},
        )
    
    def check_coverage(self) -> Dict[str, float]:
        """
        Check domain coverage.
        
        Returns:
            Dict of domain to coverage score
        """
        coverage = {}
        
        for domain in self._strategy.domains:
            templates = self._strategy.get_domain_templates(domain)
            
            # Calculate coverage based on template count
            # Expect 8-15 templates per domain
            expected_min = 8
            count = len(templates)
            
            if count >= expected_min:
                coverage[domain] = 1.0
            else:
                coverage[domain] = count / expected_min
        
        return coverage
    
    def generate_metrics(self) -> Dict[str, Any]:
        """
        Generate quality metrics.
        
        Returns:
            Metrics dictionary
        """
        total_templates = self._strategy.total_template_count
        
        # Count valid templates
        valid_count = 0
        for domain in self._strategy.domains:
            templates = self._strategy.get_domain_templates(domain)
            for template in templates:
                result = self.check_completeness(template['id'])
                if result.score >= 0.7:
                    valid_count += 1
        
        # Calculate coverage score
        coverage = self.check_coverage()
        avg_coverage = sum(coverage.values()) / len(coverage) if coverage else 0.0
        
        return {
            'total_templates': total_templates,
            'valid_templates': valid_count,
            'coverage_score': avg_coverage,
            'domains': len(self._strategy.domains),
            'timestamp': datetime.now().isoformat(),
        }
    
    def lint_template(self, template_id: str) -> List[str]:
        """
        Lint template for issues.
        
        Args:
            template_id: Template identifier
            
        Returns:
            List of issues found
        """
        issues = []
        
        template = self._strategy.get_template_by_id(template_id)
        if not template:
            return ["Template not found"]
        
        # Check ID format
        if not template['id'].replace('-', '').replace('_', '').isalnum():
            issues.append("Template ID contains invalid characters")
        
        # Check description
        desc = template.get('description', '')
        if len(desc) < 10:
            issues.append("Description too short (< 10 chars)")
        
        # Check variables
        variables = template.get('variables', [])
        for var in variables:
            if not var.replace('_', '').isalnum():
                issues.append(f"Variable '{var}' contains invalid characters")
            if var != var.lower():
                issues.append(f"Variable '{var}' should be lowercase")
        
        return issues
    
    def suggest_improvements(self, template_id: str) -> List[str]:
        """
        Suggest improvements for template.
        
        Args:
            template_id: Template identifier
            
        Returns:
            List of suggestions
        """
        suggestions = []
        
        template = self._strategy.get_template_by_id(template_id)
        if not template:
            return ["Template not found - cannot suggest improvements"]
        
        # Suggest based on domain best practices
        domain = template.get('domain', '')
        expected_vars = self.EXPECTED_VARIABLES.get(domain, set())
        current_vars = set(template.get('variables', []))
        
        missing_common = expected_vars - current_vars
        if missing_common:
            suggestions.append(
                f"Consider adding common {domain} variables: {', '.join(missing_common)}"
            )
        
        # Check content length
        content = self._manager.get_template_content(template_id)
        if content and len(content) < 200:
            suggestions.append("Consider adding more detailed content (< 200 chars)")
        
        # Check for documentation
        if not template.get('description'):
            suggestions.append("Add a description to document template purpose")
        
        return suggestions
    
    def compare_templates(
        self,
        template_id_1: str,
        template_id_2: str,
    ) -> Dict[str, Any]:
        """
        Compare two templates.
        
        Args:
            template_id_1: First template ID
            template_id_2: Second template ID
            
        Returns:
            Comparison result
        """
        t1 = self._strategy.get_template_by_id(template_id_1)
        t2 = self._strategy.get_template_by_id(template_id_2)
        
        if not t1 or not t2:
            return {
                'error': f"Template(s) not found: {template_id_1 if not t1 else template_id_2}",
                'similarity': 0.0,
                'differences': [],
            }
        
        # Compare variables
        vars1 = set(t1.get('variables', []))
        vars2 = set(t2.get('variables', []))
        
        common = vars1 & vars2
        unique_1 = vars1 - vars2
        unique_2 = vars2 - vars1
        
        # Calculate similarity
        total_vars = len(vars1 | vars2)
        similarity = len(common) / total_vars if total_vars > 0 else 1.0
        
        differences = []
        if t1.get('domain') != t2.get('domain'):
            differences.append(f"Different domains: {t1.get('domain')} vs {t2.get('domain')}")
        if t1.get('category') != t2.get('category'):
            differences.append(f"Different categories: {t1.get('category')} vs {t2.get('category')}")
        if unique_1:
            differences.append(f"Variables only in {template_id_1}: {', '.join(unique_1)}")
        if unique_2:
            differences.append(f"Variables only in {template_id_2}: {', '.join(unique_2)}")
        
        return {
            'similarity': similarity,
            'differences': differences,
            'common_variables': list(common),
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive QA report.
        
        Returns:
            Report dictionary
        """
        metrics = self.generate_metrics()
        coverage = self.check_coverage()
        
        # Collect issues per domain
        domain_issues = {}
        for domain in self._strategy.domains:
            result = self.check_consistency(domain)
            domain_issues[domain] = result.issues
        
        # Generate recommendations
        recommendations = []
        for domain, score in coverage.items():
            if score < 0.8:
                recommendations.append(f"Add more templates to {domain} domain (coverage: {score:.0%})")
        
        return {
            'summary': {
                'total_templates': metrics['total_templates'],
                'valid_templates': metrics['valid_templates'],
                'overall_coverage': metrics['coverage_score'],
                'domains_covered': metrics['domains'],
            },
            'metrics': metrics,
            'coverage': coverage,
            'domain_issues': domain_issues,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat(),
        }
    
    def run_full_suite(self) -> QASuiteResult:
        """
        Run full QA test suite.
        
        Returns:
            Suite result
        """
        tests_run = 0
        tests_passed = 0
        failures = []
        
        # Test 1: Registry validation
        tests_run += 1
        registry_result = self._strategy.validate_registry()
        if registry_result.valid:
            tests_passed += 1
        else:
            failures.extend(registry_result.errors)
        
        # Test 2: Coverage check
        tests_run += 1
        coverage = self.check_coverage()
        if all(c >= 0.8 for c in coverage.values()):
            tests_passed += 1
        else:
            low_coverage = [d for d, c in coverage.items() if c < 0.8]
            failures.append(f"Low coverage domains: {', '.join(low_coverage)}")
        
        # Test 3: Consistency per domain
        for domain in self._strategy.domains:
            tests_run += 1
            result = self.check_consistency(domain)
            if result.consistent:
                tests_passed += 1
            else:
                failures.extend(result.issues[:3])  # First 3 issues
        
        # Test 4: Template count
        tests_run += 1
        if self._strategy.total_template_count >= 60:
            tests_passed += 1
        else:
            failures.append(f"Insufficient templates: {self._strategy.total_template_count} < 60")
        
        return QASuiteResult(
            passed=len(failures) == 0,
            tests_run=tests_run,
            tests_passed=tests_passed,
            failures=failures,
            details={'coverage': coverage},
        )
    
    def export_results(self, output_path: str) -> None:
        """
        Export QA results to file.
        
        Args:
            output_path: Output file path
        """
        report = self.generate_report()
        
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(report, f, indent=2)
