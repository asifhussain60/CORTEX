"""
AC-TC-001-01: Content Population Strategy

Provides the strategy and registry for template content population.
Manages domain-specific templates and their metadata.

"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import yaml


@dataclass
class ValidationResult:
    """Result of validation operation."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class TemplateMetadata:
    """Metadata for a template."""
    id: str
    name: str
    description: str
    domain: str
    category: str = "response"
    version: str = "1.0"
    tier: int = 2
    variables: List[str] = field(default_factory=list)
    inherits_from: Optional[str] = None


class ContentPopulationStrategy:
    """
    Content population strategy and registry for tier-2 templates.
    
    Manages template metadata across all domains and provides
    discovery and access to template information.
    """
    
    # Supported domains with their template definitions
    DOMAIN_TEMPLATES: Dict[str, List[Dict[str, Any]]] = {
        'planning': [
            {'id': 'planning-recommendations', 'name': 'Implementation Recommendations', 
             'description': 'Template for implementation planning recommendations',
             'category': 'response', 'variables': ['plan_title', 'phase', 'ac_count', 'estimated_hours']},
            {'id': 'planning-impact-assessment', 'name': 'Impact Assessment',
             'description': 'Template for change impact assessment',
             'category': 'analysis', 'variables': ['change_scope', 'affected_files', 'risk_level']},
            {'id': 'planning-timeline', 'name': 'Project Timeline',
             'description': 'Template for project timeline visualization',
             'category': 'planning', 'variables': ['start_date', 'end_date', 'milestones']},
            {'id': 'planning-resource-allocation', 'name': 'Resource Allocation',
             'description': 'Template for resource allocation planning',
             'category': 'planning', 'variables': ['resources', 'assignments', 'capacity']},
            {'id': 'planning-risk-analysis', 'name': 'Risk Analysis',
             'description': 'Template for risk analysis and mitigation',
             'category': 'analysis', 'variables': ['risks', 'probability', 'impact', 'mitigation']},
            {'id': 'planning-milestone-tracker', 'name': 'Milestone Tracker',
             'description': 'Template for milestone tracking',
             'category': 'tracking', 'variables': ['milestones', 'status', 'completion_date']},
            {'id': 'planning-dependency-map', 'name': 'Dependency Map',
             'description': 'Template for dependency visualization',
             'category': 'visualization', 'variables': ['dependencies', 'blocking', 'blocked_by']},
            {'id': 'planning-progress-report', 'name': 'Progress Report',
             'description': 'Template for progress reporting',
             'category': 'report', 'variables': ['completed', 'in_progress', 'blocked', 'percentage']},
        ],
        'analysis': [
            {'id': 'analysis-codebase-review', 'name': 'Codebase Review',
             'description': 'Template for codebase analysis results',
             'category': 'analysis', 'variables': ['files_analyzed', 'issues_found', 'recommendations']},
            {'id': 'analysis-impact-report', 'name': 'Impact Report',
             'description': 'Template for impact analysis report',
             'category': 'report', 'variables': ['change_description', 'affected_areas', 'severity']},
            {'id': 'analysis-code-quality', 'name': 'Code Quality Report',
             'description': 'Template for code quality metrics',
             'category': 'metrics', 'variables': ['coverage', 'complexity', 'duplication', 'issues']},
            {'id': 'analysis-architecture-review', 'name': 'Architecture Review',
             'description': 'Template for architecture analysis',
             'category': 'analysis', 'variables': ['components', 'patterns', 'violations', 'suggestions']},
            {'id': 'analysis-performance-report', 'name': 'Performance Report',
             'description': 'Template for performance analysis',
             'category': 'metrics', 'variables': ['benchmarks', 'bottlenecks', 'optimizations']},
            {'id': 'analysis-security-scan', 'name': 'Security Scan Results',
             'description': 'Template for security scan results',
             'category': 'security', 'variables': ['vulnerabilities', 'severity', 'remediation']},
            {'id': 'analysis-dependency-audit', 'name': 'Dependency Audit',
             'description': 'Template for dependency audit results',
             'category': 'audit', 'variables': ['dependencies', 'outdated', 'vulnerabilities']},
            {'id': 'analysis-test-coverage', 'name': 'Test Coverage Report',
             'description': 'Template for test coverage analysis',
             'category': 'testing', 'variables': ['total_coverage', 'uncovered_lines', 'by_module']},
        ],
        'integration': [
            {'id': 'integration-api-response', 'name': 'API Response',
             'description': 'Template for API integration responses',
             'category': 'api', 'variables': ['endpoint', 'status', 'data', 'errors']},
            {'id': 'integration-webhook-payload', 'name': 'Webhook Payload',
             'description': 'Template for webhook payloads',
             'category': 'webhook', 'variables': ['event', 'timestamp', 'payload']},
            {'id': 'integration-data-sync', 'name': 'Data Sync Report',
             'description': 'Template for data synchronization results',
             'category': 'sync', 'variables': ['synced', 'failed', 'conflicts', 'resolution']},
            {'id': 'integration-connection-status', 'name': 'Connection Status',
             'description': 'Template for connection status reporting',
             'category': 'status', 'variables': ['service', 'status', 'latency', 'last_check']},
            {'id': 'integration-batch-result', 'name': 'Batch Operation Result',
             'description': 'Template for batch operation results',
             'category': 'batch', 'variables': ['total', 'successful', 'failed', 'details']},
            {'id': 'integration-migration-report', 'name': 'Migration Report',
             'description': 'Template for data migration results',
             'category': 'migration', 'variables': ['migrated', 'skipped', 'errors', 'rollback_available']},
            {'id': 'integration-health-check', 'name': 'Health Check',
             'description': 'Template for service health checks',
             'category': 'health', 'variables': ['services', 'status', 'dependencies', 'uptime']},
            {'id': 'integration-event-log', 'name': 'Event Log',
             'description': 'Template for integration event logging',
             'category': 'logging', 'variables': ['events', 'timestamp', 'source', 'severity']},
        ],
        'validation': [
            {'id': 'validation-schema-result', 'name': 'Schema Validation Result',
             'description': 'Template for schema validation results',
             'category': 'validation', 'variables': ['schema', 'valid', 'errors', 'path']},
            {'id': 'validation-input-check', 'name': 'Input Validation',
             'description': 'Template for input validation results',
             'category': 'validation', 'variables': ['field', 'value', 'valid', 'message']},
            {'id': 'validation-constraint-check', 'name': 'Constraint Check',
             'description': 'Template for constraint validation',
             'category': 'constraint', 'variables': ['constraint', 'satisfied', 'violations']},
            {'id': 'validation-format-check', 'name': 'Format Validation',
             'description': 'Template for format validation results',
             'category': 'format', 'variables': ['format', 'valid', 'expected', 'actual']},
            {'id': 'validation-business-rules', 'name': 'Business Rules Check',
             'description': 'Template for business rule validation',
             'category': 'business', 'variables': ['rules_checked', 'passed', 'failed', 'details']},
            {'id': 'validation-data-integrity', 'name': 'Data Integrity Check',
             'description': 'Template for data integrity validation',
             'category': 'integrity', 'variables': ['checks', 'passed', 'failed', 'anomalies']},
            {'id': 'validation-compliance-report', 'name': 'Compliance Report',
             'description': 'Template for compliance validation',
             'category': 'compliance', 'variables': ['standards', 'compliant', 'violations', 'remediation']},
            {'id': 'validation-audit-trail', 'name': 'Audit Trail Validation',
             'description': 'Template for audit trail validation',
             'category': 'audit', 'variables': ['entries', 'valid', 'gaps', 'hash_chain_status']},
        ],
        'execution': [
            {'id': 'execution-task-result', 'name': 'Task Execution Result',
             'description': 'Template for task execution results',
             'category': 'execution', 'variables': ['task', 'status', 'duration', 'output']},
            {'id': 'execution-pipeline-status', 'name': 'Pipeline Status',
             'description': 'Template for pipeline execution status',
             'category': 'pipeline', 'variables': ['pipeline', 'stages', 'current', 'progress']},
            {'id': 'execution-job-report', 'name': 'Job Report',
             'description': 'Template for job execution report',
             'category': 'job', 'variables': ['job_id', 'status', 'started', 'completed', 'logs']},
            {'id': 'execution-workflow-status', 'name': 'Workflow Status',
             'description': 'Template for workflow execution status',
             'category': 'workflow', 'variables': ['workflow', 'steps', 'current_step', 'state']},
            {'id': 'execution-command-output', 'name': 'Command Output',
             'description': 'Template for command execution output',
             'category': 'command', 'variables': ['command', 'exit_code', 'stdout', 'stderr']},
            {'id': 'execution-deployment-result', 'name': 'Deployment Result',
             'description': 'Template for deployment results',
             'category': 'deployment', 'variables': ['environment', 'version', 'status', 'rollback_available']},
            {'id': 'execution-scheduled-task', 'name': 'Scheduled Task Result',
             'description': 'Template for scheduled task results',
             'category': 'scheduled', 'variables': ['task', 'schedule', 'last_run', 'next_run', 'status']},
            {'id': 'execution-async-operation', 'name': 'Async Operation Status',
             'description': 'Template for async operation status',
             'category': 'async', 'variables': ['operation_id', 'status', 'progress', 'result']},
        ],
        'system': [
            {'id': 'system-error-response', 'name': 'Error Response',
             'description': 'Template for system error responses',
             'category': 'error', 'variables': ['error_code', 'message', 'details', 'trace']},
            {'id': 'system-status-report', 'name': 'System Status',
             'description': 'Template for system status reports',
             'category': 'status', 'variables': ['component', 'status', 'metrics', 'alerts']},
            {'id': 'system-health-summary', 'name': 'Health Summary',
             'description': 'Template for system health summary',
             'category': 'health', 'variables': ['overall_status', 'components', 'issues', 'recommendations']},
            {'id': 'system-config-report', 'name': 'Configuration Report',
             'description': 'Template for configuration reports',
             'category': 'config', 'variables': ['settings', 'environment', 'overrides', 'validation']},
            {'id': 'system-metrics-summary', 'name': 'Metrics Summary',
             'description': 'Template for system metrics summary',
             'category': 'metrics', 'variables': ['cpu', 'memory', 'disk', 'network', 'custom']},
            {'id': 'system-log-summary', 'name': 'Log Summary',
             'description': 'Template for log summary reports',
             'category': 'logging', 'variables': ['period', 'total', 'by_level', 'top_errors']},
            {'id': 'system-alert-notification', 'name': 'Alert Notification',
             'description': 'Template for system alert notifications',
             'category': 'alerts', 'variables': ['alert_type', 'severity', 'source', 'message', 'timestamp']},
            {'id': 'system-resource-usage', 'name': 'Resource Usage Report',
             'description': 'Template for resource usage reports',
             'category': 'resources', 'variables': ['resource_type', 'current_usage', 'limit', 'trend']},
        ],
        'governance': [
            {'id': 'governance-evaluation-result', 'name': 'Evaluation Result',
             'description': 'Template for governance evaluation results',
             'category': 'evaluation', 'variables': ['rules_checked', 'passed', 'failed', 'score']},
            {'id': 'governance-rule-violation', 'name': 'Rule Violation',
             'description': 'Template for rule violation reports',
             'category': 'violation', 'variables': ['rule_id', 'severity', 'description', 'remediation']},
            {'id': 'governance-compliance-status', 'name': 'Compliance Status',
             'description': 'Template for compliance status',
             'category': 'compliance', 'variables': ['framework', 'compliant', 'gaps', 'actions']},
            {'id': 'governance-audit-report', 'name': 'Audit Report',
             'description': 'Template for governance audit reports',
             'category': 'audit', 'variables': ['period', 'findings', 'recommendations', 'risk_level']},
            {'id': 'governance-policy-check', 'name': 'Policy Check Result',
             'description': 'Template for policy check results',
             'category': 'policy', 'variables': ['policy', 'status', 'violations', 'exceptions']},
            {'id': 'governance-approval-status', 'name': 'Approval Status',
             'description': 'Template for approval workflow status',
             'category': 'approval', 'variables': ['request', 'approvers', 'status', 'comments']},
            {'id': 'governance-risk-assessment', 'name': 'Risk Assessment',
             'description': 'Template for risk assessment results',
             'category': 'risk', 'variables': ['risks', 'likelihood', 'impact', 'mitigation']},
            {'id': 'governance-change-control', 'name': 'Change Control',
             'description': 'Template for change control records',
             'category': 'change', 'variables': ['change_id', 'description', 'impact', 'approval_status']},
        ],
        'tdd': [
            {'id': 'tdd-test-result', 'name': 'Test Result',
             'description': 'Template for TDD test results',
             'category': 'testing', 'variables': ['test_name', 'status', 'duration', 'assertions']},
            {'id': 'tdd-coverage-report', 'name': 'Coverage Report',
             'description': 'Template for test coverage reports',
             'category': 'coverage', 'variables': ['total', 'covered', 'uncovered', 'by_file']},
            {'id': 'tdd-test-suite-summary', 'name': 'Test Suite Summary',
             'description': 'Template for test suite summary',
             'category': 'summary', 'variables': ['total', 'passed', 'failed', 'skipped', 'duration']},
            {'id': 'tdd-assertion-failure', 'name': 'Assertion Failure',
             'description': 'Template for assertion failure details',
             'category': 'failure', 'variables': ['test', 'assertion', 'expected', 'actual', 'message']},
            {'id': 'tdd-mock-usage', 'name': 'Mock Usage Report',
             'description': 'Template for mock usage reports',
             'category': 'mocking', 'variables': ['mocks', 'calls', 'assertions', 'unused']},
            {'id': 'tdd-regression-report', 'name': 'Regression Report',
             'description': 'Template for regression test reports',
             'category': 'regression', 'variables': ['baseline', 'current', 'new_failures', 'fixed']},
            {'id': 'tdd-performance-test', 'name': 'Performance Test Result',
             'description': 'Template for performance test results',
             'category': 'performance', 'variables': ['benchmark', 'baseline', 'current', 'change']},
            {'id': 'tdd-integration-test', 'name': 'Integration Test Result',
             'description': 'Template for integration test results',
             'category': 'integration', 'variables': ['scenarios', 'passed', 'failed', 'details']},
        ],
    }
    
    def __init__(self, template_base_path: Optional[Path] = None):
        """
        Initialize content population strategy.
        
        Args:
            template_base_path: Base path for template files (defaults to cortex_brain/tier2)
        """
        if template_base_path is None:
            self.template_base_path = Path(__file__).parent.parent.parent / "cortex_brain" / "tier2"
        else:
            self.template_base_path = Path(template_base_path)
        
        self._build_registry()
    
    def _build_registry(self) -> None:
        """Build the template registry from domain definitions."""
        self._registry: Dict[str, TemplateMetadata] = {}
        
        for domain, templates in self.DOMAIN_TEMPLATES.items():
            for template in templates:
                metadata = TemplateMetadata(
                    id=template['id'],
                    name=template['name'],
                    description=template['description'],
                    domain=domain,
                    category=template.get('category', 'response'),
                    variables=template.get('variables', []),
                )
                self._registry[template['id']] = metadata
    
    @property
    def domains(self) -> List[str]:
        """Get list of supported domains."""
        return list(self.DOMAIN_TEMPLATES.keys())
    
    @property
    def total_template_count(self) -> int:
        """Get total number of templates."""
        return len(self._registry)
    
    def get_domain_templates(self, domain: str) -> List[Dict[str, Any]]:
        """
        Get templates for a specific domain.
        
        Args:
            domain: Domain name
            
        Returns:
            List of template metadata dictionaries
        """
        if domain not in self.DOMAIN_TEMPLATES:
            return []
        
        templates = []
        for template in self.DOMAIN_TEMPLATES[domain]:
            templates.append({
                'id': template['id'],
                'name': template['name'],
                'description': template['description'],
                'domain': domain,
                'category': template.get('category', 'response'),
                'variables': template.get('variables', []),
            })
        return templates
    
    def get_template_by_id(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Get template metadata by ID.
        
        Args:
            template_id: Template identifier
            
        Returns:
            Template metadata dictionary or None if not found
        """
        metadata = self._registry.get(template_id)
        if metadata is None:
            return None
        
        return {
            'id': metadata.id,
            'name': metadata.name,
            'description': metadata.description,
            'domain': metadata.domain,
            'category': metadata.category,
            'variables': metadata.variables,
        }
    
    def get_templates_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get templates filtered by category.
        
        Args:
            category: Template category
            
        Returns:
            List of matching template metadata
        """
        return [
            {
                'id': m.id,
                'name': m.name,
                'description': m.description,
                'domain': m.domain,
                'category': m.category,
                'variables': m.variables,
            }
            for m in self._registry.values()
            if m.category == category
        ]
    
    def export_registry(self) -> Dict[str, Any]:
        """
        Export complete template registry.
        
        Returns:
            Registry export dictionary
        """
        domains_export = {}
        for domain in self.domains:
            domains_export[domain] = self.get_domain_templates(domain)
        
        return {
            'domains': domains_export,
            'templates': [
                self.get_template_by_id(tid)
                for tid in self._registry.keys()
            ],
            'total_count': self.total_template_count,
            'version': '1.0',
        }
    
    def validate_registry(self) -> ValidationResult:
        """
        Validate registry integrity.
        
        Returns:
            Validation result
        """
        errors = []
        warnings = []
        
        # Check for duplicate IDs
        seen_ids: Set[str] = set()
        for tid in self._registry.keys():
            if tid in seen_ids:
                errors.append(f"Duplicate template ID: {tid}")
            seen_ids.add(tid)
        
        # Check all domains have templates
        for domain in self.domains:
            templates = self.get_domain_templates(domain)
            if len(templates) < 6:
                warnings.append(f"Domain {domain} has < 6 templates ({len(templates)})")
        
        # Check template count
        if self.total_template_count < 60:
            errors.append(f"Total templates {self.total_template_count} < 60 minimum")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )
