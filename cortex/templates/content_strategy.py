"""
CORTEX Templates - Content Population Strategy

Manages domain templates, content sources, and template metadata.

"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
from enum import Enum
from pathlib import Path
import yaml


class ContentSource(Enum):
    """Content source types."""
    KNOWLEDGE_GRAPH = "knowledge_graph"
    DOMAIN_REGISTRY = "domain_registry"
    STATIC_CONTENT = "static_content"
    DYNAMIC_GENERATION = "dynamic_generation"
    USER_INPUT = "user_input"


@dataclass
class TemplateMetadata:
    """Template metadata."""
    id: str
    name: str
    description: str
    domain: str
    category: Optional[str] = None
    version: str = "1.0"
    source: ContentSource = ContentSource.STATIC_CONTENT
    variables: List[str] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation.
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'domain': self.domain,
            'category': self.category,
            'version': self.version,
            'source': self.source.value,
            'variables': self.variables,
            'tags': list(self.tags),
        }


class ContentPopulationStrategy:
    """Content population strategy and template registry.
    
    Manages domain templates, content sources, and template metadata.
    """
    
    def __init__(self) -> None:
        """Initialize content population strategy."""
        self._templates: Dict[str, TemplateMetadata] = {}
        self._domain_index: Dict[str, List[str]] = {}
        self._category_index: Dict[str, List[str]] = {}
        self._initialize_default_templates()
    
    def _initialize_default_templates(self) -> None:
        """Initialize default templates for each domain."""
        # Planning domain templates (12 templates)
        planning_templates = [
            TemplateMetadata(
                id='planning-recommendations',
                name='Planning Recommendations',
                description='Strategic planning recommendations template',
                domain='planning',
                category='response',
            ),
            TemplateMetadata(
                id='planning-impact-assessment',
                name='Impact Assessment',
                description='Planning impact assessment template',
                domain='planning',
                category='analysis',
            ),
            TemplateMetadata(
                id='planning-timeline',
                name='Timeline',
                description='Project timeline template',
                domain='planning',
                category='execution',
            ),
            TemplateMetadata(
                id='planning-resource-allocation',
                name='Resource Allocation',
                description='Resource planning template',
                domain='planning',
                category='execution',
            ),
            TemplateMetadata(
                id='planning-risk-analysis',
                name='Risk Analysis',
                description='Risk analysis template',
                domain='planning',
                category='analysis',
            ),
            TemplateMetadata(
                id='planning-milestone-tracker',
                name='Milestone Tracker',
                description='Milestone tracking template',
                domain='planning',
                category='monitoring',
            ),
            TemplateMetadata(
                id='planning-dependency-map',
                name='Dependency Map',
                description='Dependency mapping template',
                domain='planning',
                category='analysis',
            ),
            TemplateMetadata(
                id='planning-progress-report',
                name='Progress Report',
                description='Progress tracking template',
                domain='planning',
                category='response',
            ),
            TemplateMetadata(
                id='planning-roadmap',
                name='Planning Roadmap',
                description='Phase roadmap and timeline template',
                domain='planning',
                category='response',
            ),
            TemplateMetadata(
                id='planning-risk-assessment',
                name='Risk Assessment',
                description='Project risk assessment template',
                domain='planning',
                category='analysis',
            ),
            TemplateMetadata(
                id='planning-stakeholder-analysis',
                name='Stakeholder Analysis',
                description='Stakeholder analysis template',
                domain='planning',
                category='analysis',
            ),
            TemplateMetadata(
                id='planning-phase-breakdown',
                name='Phase Breakdown',
                description='Phase breakdown structure template',
                domain='planning',
                category='execution',
            ),
        ]
        
        # Governance domain templates (10 templates)
        governance_templates = [
            TemplateMetadata(
                id='governance-compliance-report',
                name='Compliance Report',
                description='Governance compliance report template',
                domain='governance',
                category='response',
            ),
            TemplateMetadata(
                id='governance-audit-trail',
                name='Audit Trail',
                description='Audit trail documentation template',
                domain='governance',
                category='response',
            ),
            TemplateMetadata(
                id='governance-policy-definition',
                name='Policy Definition',
                description='Governance policy definition template',
                domain='governance',
                category='execution',
            ),
            TemplateMetadata(
                id='governance-rule-validation',
                name='Rule Validation',
                description='Rule validation report template',
                domain='governance',
                category='validation',
            ),
            TemplateMetadata(
                id='governance-security-hardening',
                name='Security Hardening',
                description='Security hardening checklist template',
                domain='governance',
                category='execution',
            ),
            TemplateMetadata(
                id='governance-access-control',
                name='Access Control',
                description='Access control policy template',
                domain='governance',
                category='execution',
            ),
            TemplateMetadata(
                id='governance-data-retention',
                name='Data Retention',
                description='Data retention policy template',
                domain='governance',
                category='execution',
            ),
            TemplateMetadata(
                id='governance-incident-response',
                name='Incident Response',
                description='Incident response plan template',
                domain='governance',
                category='execution',
            ),
            TemplateMetadata(
                id='governance-compliance-matrix',
                name='Compliance Matrix',
                description='Compliance matrix template',
                domain='governance',
                category='validation',
            ),
            TemplateMetadata(
                id='governance-risk-register',
                name='Risk Register',
                description='Risk register template',
                domain='governance',
                category='monitoring',
            ),
        ]
        
        # Analysis domain templates (12 templates)
        analysis_templates = [
            TemplateMetadata(
                id='analysis-gap-assessment',
                name='Gap Assessment',
                description='Gap analysis report template',
                domain='analysis',
                category='response',
            ),
            TemplateMetadata(
                id='analysis-impact-evaluation',
                name='Impact Evaluation',
                description='Impact evaluation template',
                domain='analysis',
                category='analysis',
            ),
            TemplateMetadata(
                id='analysis-performance-metrics',
                name='Performance Metrics',
                description='Performance metrics analysis template',
                domain='analysis',
                category='monitoring',
            ),
            TemplateMetadata(
                id='analysis-code-quality',
                name='Code Quality',
                description='Code quality analysis template',
                domain='analysis',
                category='validation',
            ),
            TemplateMetadata(
                id='analysis-test-coverage',
                name='Test Coverage',
                description='Test coverage analysis template',
                domain='analysis',
                category='validation',
            ),
            TemplateMetadata(
                id='analysis-technical-debt',
                name='Technical Debt',
                description='Technical debt assessment template',
                domain='analysis',
                category='analysis',
            ),
            TemplateMetadata(
                id='analysis-architecture-review',
                name='Architecture Review',
                description='Architecture review template',
                domain='analysis',
                category='validation',
            ),
            TemplateMetadata(
                id='analysis-dependency-audit',
                name='Dependency Audit',
                description='Dependency audit template',
                domain='analysis',
                category='validation',
            ),
            TemplateMetadata(
                id='analysis-security-scan',
                name='Security Scan',
                description='Security scan results template',
                domain='analysis',
                category='validation',
            ),
            TemplateMetadata(
                id='analysis-bottleneck-identification',
                name='Bottleneck Identification',
                description='Performance bottleneck analysis template',
                domain='analysis',
                category='analysis',
            ),
            TemplateMetadata(
                id='analysis-trend-analysis',
                name='Trend Analysis',
                description='Trend analysis template',
                domain='analysis',
                category='monitoring',
            ),
            TemplateMetadata(
                id='analysis-comparative-study',
                name='Comparative Study',
                description='Comparative study template',
                domain='analysis',
                category='analysis',
            ),
        ]
        
        # Integration domain templates (10 templates)
        integration_templates = [
            TemplateMetadata(
                id='integration-api-spec',
                name='API Specification',
                description='API integration specification template',
                domain='integration',
                category='execution',
            ),
            TemplateMetadata(
                id='integration-data-mapping',
                name='Data Mapping',
                description='Data mapping template',
                domain='integration',
                category='execution',
            ),
            TemplateMetadata(
                id='integration-connector-config',
                name='Connector Configuration',
                description='Connector configuration template',
                domain='integration',
                category='execution',
            ),
            TemplateMetadata(
                id='integration-workflow-definition',
                name='Workflow Definition',
                description='Integration workflow template',
                domain='integration',
                category='execution',
            ),
            TemplateMetadata(
                id='integration-error-handling',
                name='Error Handling',
                description='Error handling strategy template',
                domain='integration',
                category='execution',
            ),
            TemplateMetadata(
                id='integration-authentication',
                name='Authentication',
                description='Authentication configuration template',
                domain='integration',
                category='execution',
            ),
            TemplateMetadata(
                id='integration-rate-limiting',
                name='Rate Limiting',
                description='Rate limiting strategy template',
                domain='integration',
                category='execution',
            ),
            TemplateMetadata(
                id='integration-monitoring',
                name='Integration Monitoring',
                description='Integration monitoring template',
                domain='integration',
                category='monitoring',
            ),
            TemplateMetadata(
                id='integration-validation',
                name='Integration Validation',
                description='Integration validation template',
                domain='integration',
                category='validation',
            ),
            TemplateMetadata(
                id='integration-compatibility',
                name='Compatibility Matrix',
                description='System compatibility template',
                domain='integration',
                category='validation',
            ),
        ]
        
        # Validation domain templates (10 templates)
        validation_templates = [
            TemplateMetadata(
                id='validation-test-plan',
                name='Test Plan',
                description='Test plan template',
                domain='validation',
                category='execution',
            ),
            TemplateMetadata(
                id='validation-test-results',
                name='Test Results',
                description='Test results report template',
                domain='validation',
                category='response',
            ),
            TemplateMetadata(
                id='validation-acceptance-criteria',
                name='Acceptance Criteria',
                description='Acceptance criteria template',
                domain='validation',
                category='validation',
            ),
            TemplateMetadata(
                id='validation-regression-suite',
                name='Regression Suite',
                description='Regression test suite template',
                domain='validation',
                category='execution',
            ),
            TemplateMetadata(
                id='validation-smoke-tests',
                name='Smoke Tests',
                description='Smoke test checklist template',
                domain='validation',
                category='execution',
            ),
            TemplateMetadata(
                id='validation-performance-tests',
                name='Performance Tests',
                description='Performance test template',
                domain='validation',
                category='execution',
            ),
            TemplateMetadata(
                id='validation-security-tests',
                name='Security Tests',
                description='Security test template',
                domain='validation',
                category='execution',
            ),
            TemplateMetadata(
                id='validation-quality-gate',
                name='Quality Gate',
                description='Quality gate criteria template',
                domain='validation',
                category='validation',
            ),
            TemplateMetadata(
                id='validation-defect-report',
                name='Defect Report',
                description='Defect report template',
                domain='validation',
                category='response',
            ),
            TemplateMetadata(
                id='validation-verification-matrix',
                name='Verification Matrix',
                description='Verification matrix template',
                domain='validation',
                category='validation',
            ),
        ]
        
        # Execution domain templates (10 templates)
        execution_templates = [
            TemplateMetadata(
                id='execution-deployment-plan',
                name='Deployment Plan',
                description='Deployment plan template',
                domain='execution',
                category='execution',
            ),
            TemplateMetadata(
                id='execution-rollback-procedure',
                name='Rollback Procedure',
                description='Rollback procedure template',
                domain='execution',
                category='execution',
            ),
            TemplateMetadata(
                id='execution-release-notes',
                name='Release Notes',
                description='Release notes template',
                domain='execution',
                category='response',
            ),
            TemplateMetadata(
                id='execution-implementation-guide',
                name='Implementation Guide',
                description='Implementation guide template',
                domain='execution',
                category='response',
            ),
            TemplateMetadata(
                id='execution-runbook',
                name='Runbook',
                description='Operational runbook template',
                domain='execution',
                category='execution',
            ),
            TemplateMetadata(
                id='execution-monitoring-dashboard',
                name='Monitoring Dashboard',
                description='Monitoring dashboard template',
                domain='execution',
                category='monitoring',
            ),
            TemplateMetadata(
                id='execution-alerting-rules',
                name='Alerting Rules',
                description='Alerting rules template',
                domain='execution',
                category='monitoring',
            ),
            TemplateMetadata(
                id='execution-capacity-planning',
                name='Capacity Planning',
                description='Capacity planning template',
                domain='execution',
                category='execution',
            ),
            TemplateMetadata(
                id='execution-disaster-recovery',
                name='Disaster Recovery',
                description='Disaster recovery plan template',
                domain='execution',
                category='execution',
            ),
            TemplateMetadata(
                id='execution-maintenance-schedule',
                name='Maintenance Schedule',
                description='Maintenance schedule template',
                domain='execution',
                category='execution',
            ),
        ]
        
        # System domain templates (8 templates)
        system_templates = [
            TemplateMetadata(
                id='system-architecture-overview',
                name='Architecture Overview',
                description='System architecture overview template',
                domain='system',
                category='response',
            ),
            TemplateMetadata(
                id='system-configuration',
                name='System Configuration',
                description='System configuration template',
                domain='system',
                category='execution',
            ),
            TemplateMetadata(
                id='system-health-report',
                name='Health Report',
                description='System health report template',
                domain='system',
                category='monitoring',
            ),
            TemplateMetadata(
                id='system-performance-metrics',
                name='Performance Metrics',
                description='System performance metrics template',
                domain='system',
                category='monitoring',
            ),
            TemplateMetadata(
                id='system-diagnostic-report',
                name='Diagnostic Report',
                description='System diagnostic report template',
                domain='system',
                category='analysis',
            ),
            TemplateMetadata(
                id='system-upgrade-plan',
                name='Upgrade Plan',
                description='System upgrade plan template',
                domain='system',
                category='execution',
            ),
            TemplateMetadata(
                id='system-backup-strategy',
                name='Backup Strategy',
                description='System backup strategy template',
                domain='system',
                category='execution',
            ),
            TemplateMetadata(
                id='system-recovery-plan',
                name='Recovery Plan',
                description='System recovery plan template',
                domain='system',
                category='execution',
            ),
        ]
        
        # Register all templates
        all_templates = (
            planning_templates +
            governance_templates +
            analysis_templates +
            integration_templates +
            validation_templates +
            execution_templates +
            system_templates
        )
        
        for template in all_templates:
            self._register_template(template)
    
    def _register_template(self, template: TemplateMetadata) -> None:
        """Register a template in the registry.
        
        Args:
            template: Template metadata to register.
        """
        self._templates[template.id] = template
        
        # Update domain index
        if template.domain not in self._domain_index:
            self._domain_index[template.domain] = []
        self._domain_index[template.domain].append(template.id)
        
        # Update category index
        if template.category:
            if template.category not in self._category_index:
                self._category_index[template.category] = []
            self._category_index[template.category].append(template.id)
    
    @property
    def domains(self) -> List[str]:
        """Get list of all domains.
        
        Returns:
            List of domain names.
        """
        return list(self._domain_index.keys())
    
    @property
    def total_template_count(self) -> int:
        """Get total template count.
        
        Returns:
            Total number of templates.
        """
        return len(self._templates)
    
    def get_domain_templates(self, domain: str) -> List[Dict[str, Any]]:
        """Get templates for a specific domain.
        
        Args:
            domain: Domain name.
            
        Returns:
            List of template dictionaries.
        """
        if domain not in self._domain_index:
            return []
        
        template_ids = self._domain_index[domain]
        return [
            self._templates[tid].to_dict()
            for tid in template_ids
        ]
    
    def get_template_by_id(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get template by ID.
        
        Args:
            template_id: Template ID.
            
        Returns:
            Template dictionary or None if not found.
        """
        template = self._templates.get(template_id)
        if template:
            return template.to_dict()
        return None
    
    def get_templates_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get templates by category.
        
        Args:
            category: Category name.
            
        Returns:
            List of template dictionaries.
        """
        if category not in self._category_index:
            return []
        
        template_ids = self._category_index[category]
        return [
            self._templates[tid].to_dict()
            for tid in template_ids
        ]
    
    def export_registry(self) -> Dict[str, Any]:
        """Export complete template registry.
        
        Returns:
            Registry dictionary.
        """
        return {
            'domains': self.domains,
            'templates': {
                tid: template.to_dict()
                for tid, template in self._templates.items()
            },
            'total_count': self.total_template_count,
            'domain_counts': {
                domain: len(self._domain_index[domain])
                for domain in self.domains
            },
        }
    
    def validate_registry(self) -> ValidationResult:
        """Validate registry integrity.
        
        Returns:
            Validation result.
        """
        errors = []
        warnings = []
        
        # Check for duplicate IDs
        all_ids = list(self._templates.keys())
        if len(all_ids) != len(set(all_ids)):
            errors.append("Duplicate template IDs found")
        
        # Check domain coverage
        for domain in self.domains:
            count = len(self._domain_index[domain])
            if count < 8:
                warnings.append(f"Domain {domain} has only {count} templates (< 8)")
            elif count > 15:
                warnings.append(f"Domain {domain} has {count} templates (> 15)")
        
        # Check total count
        if self.total_template_count < 60:
            warnings.append(f"Total template count {self.total_template_count} < 60")
        elif self.total_template_count > 90:
            warnings.append(f"Total template count {self.total_template_count} > 90")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )
