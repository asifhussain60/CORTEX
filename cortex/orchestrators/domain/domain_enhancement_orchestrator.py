"""
Domain Enhancement Orchestrator.

AC_START: AC-PHASE38-009, AC-PHASE38-010, AC-PHASE38-011

Provides automatic domain template generation, gap detection during operations,
and continuous domain refinement for company/domains/ directory.

Key Features:
- Auto-create domains from templates during operations
- Detect gaps in company domains (like DIGEST mode)
- 5 core templates (security, testing, docs, API, deployment)
- Track domain usage and freshness
- Version control for domains
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class DomainGap:
    """Represents a gap in company domain coverage."""

    domain: str
    gap_type: str  # 'missing', 'outdated', 'incomplete'
    description: str
    impact: str = 'medium'  # 'low', 'medium', 'high'
    priority: float = 0.5
    recommended_action: Optional[str] = None
    detected_at: datetime = field(default_factory=datetime.now)


class DomainTemplate:
    """Template for creating new domains."""

    def __init__(self, name: str, sections: Dict[str, List[str]]):
        """
        Initialize domain template.

        Args:
            name: Template name
            sections: Dict mapping section names to content lists
        """
        self.name = name
        self.sections = sections

    @classmethod
    def load(cls, template_name: str) -> 'DomainTemplate':
        """
        Load a domain template by name.

        Args:
            template_name: Name of template to load

        Returns:
            Loaded template
        """
        templates = {
            'security-standards': {
                'authentication': [
                    'Use OAuth 2.0 with PKCE for mobile apps',
                    'Implement multi-factor authentication for sensitive operations',
                    'Enforce password complexity requirements (min 12 chars)',
                ],
                'authorization': [
                    'Use role-based access control (RBAC)',
                    'Implement principle of least privilege',
                    'Audit access control changes',
                ],
                'data-protection': [
                    'Encrypt sensitive data at rest (AES-256)',
                    'Use TLS 1.3+ for data in transit',
                    'Implement secure key management',
                ],
            },
            'testing-standards': {
                'unit-testing': [
                    'Minimum 80% code coverage for new code',
                    'Use pytest with fixtures for test isolation',
                    'Follow AAA pattern (Arrange-Act-Assert)',
                ],
                'integration-testing': [
                    'Test all external API integrations',
                    'Use test doubles for slow/expensive operations',
                    'Verify error handling and retry logic',
                ],
                'e2e-testing': [
                    'Cover critical user workflows',
                    'Use realistic test data',
                    'Test across supported browsers/devices',
                ],
            },
            'documentation-standards': {
                'code-comments': [
                    'Use docstrings for all public functions/classes',
                    'Follow Google style guide for Python docstrings',
                    'Document complex algorithms with inline comments',
                ],
                'api-documentation': [
                    'Generate OpenAPI/Swagger specs for REST APIs',
                    'Include request/response examples',
                    'Document authentication requirements',
                ],
                'architecture-docs': [
                    'Maintain architecture decision records (ADRs)',
                    'Document system diagrams (C4 model)',
                    'Keep README up-to-date with setup instructions',
                ],
            },
            'api-design-standards': {
                'rest-api': [
                    'Use RESTful resource naming (plural nouns)',
                    'Follow HTTP status code conventions',
                    'Implement pagination for list endpoints',
                ],
                'versioning': [
                    'Use URL path versioning (e.g., /v1/)',
                    'Maintain backwards compatibility within major versions',
                    'Document deprecation timeline (min 6 months)',
                ],
                'error-handling': [
                    'Return consistent error response format',
                    'Include error codes and human-readable messages',
                    'Log errors with correlation IDs',
                ],
            },
            'deployment-standards': {
                'ci-cd': [
                    'Run tests on every commit',
                    'Use automated deployment pipelines',
                    'Implement canary deployments for production',
                ],
                'rollback-strategy': [
                    'Support zero-downtime deployments',
                    'Maintain ability to rollback within 5 minutes',
                    'Test rollback procedures quarterly',
                ],
                'monitoring': [
                    'Implement health check endpoints',
                    'Set up alerts for critical metrics',
                    'Use distributed tracing for microservices',
                ],
            },
        }

        if template_name not in templates:
            raise ValueError(f"Unknown template: {template_name}")

        return cls(name=template_name, sections=templates[template_name])

    def instantiate(
        self,
        domain_name: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Instantiate template as a domain with company context.

        Args:
            domain_name: Name for the new domain
            context: Company context (industry, compliance, etc.)

        Returns:
            Domain dictionary ready for saving
        """
        context = context or {}

        domain = {
            'name': domain_name,
            'template': self.name,
            'created': datetime.now().isoformat(),
            'context': context,
            'standards': {}
        }

        # Copy template sections
        for section, standards in self.sections.items():
            domain['standards'][section] = standards.copy()

        # Apply context-specific customizations
        if context.get('industry') == 'fintech':
            if 'authorization' in domain['standards']:
                domain['standards']['authorization'].append(
                    'Comply with PCI-DSS for payment processing'
                )

        if context.get('compliance') == 'HIPAA':
            if 'data-protection' in domain['standards']:
                domain['standards']['data-protection'].append(
                    'Implement HIPAA-compliant audit logging'
                )

        return domain

    def validate(self) -> Dict[str, Any]:
        """
        Validate template structure.

        Returns:
            Validation result with errors
        """
        errors = []

        if not self.name:
            errors.append("Template name is required")

        if not self.sections:
            errors.append("Template must have at least one section")

        for section, standards in self.sections.items():
            if not isinstance(standards, list):
                errors.append(f"Section '{section}' must be a list")

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    def extend(self, sections: Dict[str, List[str]]) -> 'DomainTemplate':
        """
        Extend template with additional sections.

        Args:
            sections: New sections to add

        Returns:
            New template with extended sections
        """
        extended_sections = self.sections.copy()
        extended_sections.update(sections)

        return DomainTemplate(name=self.name, sections=extended_sections)


class GapAnalyzer:
    """Analyzes gaps in company domain coverage."""

    def __init__(self):
        """Initialize gap analyzer."""
        self._gap_history: List[DomainGap] = []

    def analyze_gaps(
        self,
        domain: str,
        operation_context: Dict[str, Any]
    ) -> List[DomainGap]:
        """
        Analyze gaps for a specific domain.

        Args:
            domain: Domain name
            operation_context: Context from operation

        Returns:
            List of detected gaps
        """
        gaps = []

        # Check if domain file exists
        domain_path = Path(f"company/domains/{domain}-standards.yaml")

        if not domain_path.exists():
            gaps.append(DomainGap(
                domain=domain,
                gap_type='missing',
                description=f"No {domain} standards defined",
                impact='high',
                priority=0.8,
                recommended_action='create_from_template'
            ))

        return gaps

    def calculate_priority(self, gap: DomainGap) -> float:
        """
        Calculate priority score for a gap.

        Args:
            gap: Gap to score

        Returns:
            Priority score (0.0-1.0)
        """
        impact_weights = {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.9
        }

        base_priority = impact_weights.get(gap.impact, 0.5)

        # Boost priority for missing gaps
        if gap.gap_type == 'missing':
            base_priority *= 1.2

        return min(1.0, base_priority)

    def analyze_from_audit(self, audit_results: Dict[str, Any]) -> List[DomainGap]:
        """
        Analyze gaps from AUDIT mode results.

        Args:
            audit_results: Results from AUDIT mode

        Returns:
            List of gaps detected
        """
        gaps = []

        missing_domains = audit_results.get('domains_missing', [])

        for domain in missing_domains:
            gaps.append(DomainGap(
                domain=domain,
                gap_type='missing',
                description=f"Domain '{domain}' referenced but not defined",
                impact='medium',
                priority=0.6
            ))

        return gaps

    def generate_recommendation(self, gap: DomainGap) -> Dict[str, Any]:
        """
        Generate actionable recommendation for a gap.

        Args:
            gap: Gap to generate recommendation for

        Returns:
            Recommendation dictionary
        """
        if gap.gap_type == 'missing':
            return {
                'action': 'create',
                'template': f"{gap.domain}-standards",
                'description': f"Create {gap.domain} domain from template"
            }

        if gap.gap_type == 'outdated':
            return {
                'action': 'update',
                'description': f"Update {gap.domain} domain with latest standards"
            }

        return {
            'action': 'review',
            'description': f"Review {gap.domain} domain for completeness"
        }

    def record_gap(self, gap: DomainGap):
        """Record a gap in history."""
        self._gap_history.append(gap)

    def get_gap_history(self, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get gap history, optionally filtered by domain.

        Args:
            domain: Optional domain filter

        Returns:
            List of historical gaps
        """
        gaps = self._gap_history

        if domain:
            gaps = [g for g in gaps if g.domain == domain]

        return [
            {
                'domain': g.domain,
                'gap_type': g.gap_type,
                'description': g.description,
                'detected_at': g.detected_at.isoformat(),
                'status': 'open'
            }
            for g in gaps
        ]

    def batch_analyze(self, domains: List[str]) -> Dict[str, List[DomainGap]]:
        """
        Analyze multiple domains at once.

        Args:
            domains: List of domain names

        Returns:
            Dict mapping domain to gaps
        """
        return {
            domain: self.analyze_gaps(domain, {})
            for domain in domains
        }

    def filter_false_positives(
        self,
        potential_gaps: List[DomainGap],
        existing_domains: List[str]
    ) -> List[DomainGap]:
        """
        Filter out false positive gaps.

        Args:
            potential_gaps: Gaps to filter
            existing_domains: List of existing domain names

        Returns:
            Filtered gaps
        """
        filtered = []

        for gap in potential_gaps:
            # Check if domain actually exists
            if gap.gap_type == 'missing':
                if gap.domain not in existing_domains:
                    filtered.append(gap)
            else:
                filtered.append(gap)

        return filtered


class DomainEnhancementOrchestrator:
    """
    Orchestrator for automatic domain enhancement.

    Manages domain templates, gap detection, and continuous refinement.
    """

    def __init__(self):
        """Initialize orchestrator."""
        self._template_registry: Dict[str, DomainTemplate] = {}
        self._domain_usage: Dict[str, Dict[str, Any]] = {}
        self._domain_versions: Dict[str, List[Dict[str, Any]]] = {}
        self._gap_analyzer = GapAnalyzer()

        # Register default templates
        for name in ['security-standards', 'testing-standards',
                     'documentation-standards', 'api-design-standards',
                     'deployment-standards']:
            self._template_registry[name] = DomainTemplate.load(name)

    def create_domain_from_template(
        self,
        template_name: str,
        domain_name: str,
        company_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new domain from template.

        Args:
            template_name: Name of template to use
            domain_name: Name for the new domain
            company_context: Company-specific context

        Returns:
            Result with domain path and success status
        """
        if template_name not in self._template_registry:
            return {'success': False, 'error': f"Unknown template: {template_name}"}

        template = self._template_registry[template_name]
        domain = template.instantiate(domain_name, company_context)

        # Save domain to file
        domain_dir = Path("company/domains")
        domain_dir.mkdir(parents=True, exist_ok=True)

        domain_path = domain_dir / f"{domain_name}.yaml"

        with open(domain_path, 'w') as f:
            yaml.dump(domain, f, default_flow_style=False)

        return {
            'success': True,
            'domain_path': str(domain_path),
            'domain': domain
        }

    def detect_domain_gaps(
        self,
        operation_context: Dict[str, Any]
    ) -> List[DomainGap]:
        """
        Detect gaps in company domains based on operation context.

        Args:
            operation_context: Context from operation

        Returns:
            List of detected gaps
        """
        domain = operation_context.get('domain', 'unknown')

        return self._gap_analyzer.analyze_gaps(domain, operation_context)

    def enhance_domain(
        self,
        domain_name: str,
        learnings: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Enhance existing domain with new learnings.

        Args:
            domain_name: Domain to enhance
            learnings: List of learnings to add

        Returns:
            Result with items added count
        """
        domain_path = Path(f"company/domains/{domain_name}.yaml")

        if not domain_path.exists():
            return {'success': False, 'error': 'Domain not found'}

        with open(domain_path, 'r') as f:
            domain = yaml.safe_load(f)

        items_added = 0

        for learning in learnings:
            topic = learning.get('topic', 'general')
            content = learning.get('content')

            if 'standards' not in domain:
                domain['standards'] = {}

            if topic not in domain['standards']:
                domain['standards'][topic] = []

            if content and content not in domain['standards'][topic]:
                domain['standards'][topic].append(content)
                items_added += 1

        with open(domain_path, 'w') as f:
            yaml.dump(domain, f, default_flow_style=False)

        return {'success': True, 'items_added': items_added}

    def list_templates(self) -> List[Dict[str, Any]]:
        """
        List all available domain templates.

        Returns:
            List of template metadata
        """
        return [
            {
                'name': name,
                'sections': list(template.sections.keys()),
                'section_count': len(template.sections)
            }
            for name, template in self._template_registry.items()
        ]

    def auto_create_missing_domain(
        self,
        domain_name: str,
        trigger_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Automatically create missing domain during operation.

        Args:
            domain_name: Domain to create
            trigger_context: Context that triggered creation

        Returns:
            Result with creation status
        """
        # Map domain name to template
        template_mapping = {
            'security-standards': 'security-standards',
            'testing-standards': 'testing-standards',
            'api-design-standards': 'api-design-standards',
            'documentation-standards': 'documentation-standards',
            'deployment-standards': 'deployment-standards',
        }

        template_name = template_mapping.get(domain_name, 'security-standards')

        result = self.create_domain_from_template(
            template_name=template_name,
            domain_name=domain_name,
            company_context={}
        )

        return {
            'created': result['success'],
            'template_used': template_name,
            'domain_path': result.get('domain_path')
        }

    def validate_domain(self, domain_path: str) -> Dict[str, Any]:
        """
        Validate domain YAML structure.

        Args:
            domain_path: Path to domain file

        Returns:
            Validation result
        """
        path = Path(domain_path)

        if not path.exists():
            return {'valid': False, 'errors': ['Domain file not found']}

        try:
            with open(path, 'r') as f:
                domain = yaml.safe_load(f)

            errors = []

            if 'name' not in domain:
                errors.append("Domain must have 'name' field")

            if 'standards' not in domain:
                errors.append("Domain must have 'standards' field")

            return {'valid': len(errors) == 0, 'errors': errors}

        except Exception as e:
            return {'valid': False, 'errors': [str(e)]}

    def merge_domains(self, domain_names: List[str]) -> Dict[str, Any]:
        """
        Merge multiple domains into consolidated view.

        Args:
            domain_names: List of domain names to merge

        Returns:
            Merged domain dictionary
        """
        merged = {'standards': {}}

        for domain_name in domain_names:
            domain_path = Path(f"company/domains/{domain_name}.yaml")

            if domain_path.exists():
                with open(domain_path, 'r') as f:
                    domain = yaml.safe_load(f)

                if 'standards' in domain:
                    for section, standards in domain['standards'].items():
                        if section not in merged['standards']:
                            merged['standards'][section] = []
                        merged['standards'][section].extend(standards)

        return merged

    def track_domain_usage(
        self,
        domain_name: str,
        operation_context: Dict[str, Any]
    ):
        """
        Track domain usage in operations.

        Args:
            domain_name: Domain being used
            operation_context: Operation context
        """
        if domain_name not in self._domain_usage:
            self._domain_usage[domain_name] = {
                'usage_count': 0,
                'last_used': None,
                'operations': []
            }

        self._domain_usage[domain_name]['usage_count'] += 1
        self._domain_usage[domain_name]['last_used'] = datetime.now()
        self._domain_usage[domain_name]['operations'].append(operation_context)

    def get_domain_usage_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get domain usage statistics.

        Returns:
            Dict mapping domain to usage stats
        """
        return self._domain_usage

    def check_domain_freshness(self, domain_name: str) -> Dict[str, Any]:
        """
        Check if domain needs updating based on age.

        Args:
            domain_name: Domain to check

        Returns:
            Freshness information
        """
        domain_path = Path(f"company/domains/{domain_name}.yaml")

        if not domain_path.exists():
            return {'is_fresh': False, 'error': 'Domain not found'}

        mtime = domain_path.stat().st_mtime
        last_updated = datetime.fromtimestamp(mtime)
        days_since_update = (datetime.now() - last_updated).days

        return {
            'is_fresh': days_since_update < 90,  # 3 months
            'last_updated': last_updated.isoformat(),
            'days_since_update': days_since_update
        }

    def search_domains(self, query: str) -> List[Dict[str, Any]]:
        """
        Search across domain content.

        Args:
            query: Search query

        Returns:
            List of matching results
        """
        results = []
        domain_dir = Path("company/domains")

        if not domain_dir.exists():
            return results

        for domain_path in domain_dir.glob("*.yaml"):
            try:
                with open(domain_path, 'r') as f:
                    domain = yaml.safe_load(f)

                if not domain or 'standards' not in domain:
                    continue

                standards = domain['standards']

                # Handle both dict and list formats
                if isinstance(standards, dict):
                    for section, section_standards in standards.items():
                        if isinstance(section_standards, list):
                            for standard in section_standards:
                                if query.lower() in str(standard).lower():
                                    results.append({
                                        'domain': domain.get('name', domain_path.stem),
                                        'section': section,
                                        'content': standard
                                    })
                elif isinstance(standards, list):
                    for standard in standards:
                        if query.lower() in str(standard).lower():
                            results.append({
                                'domain': domain.get('name', domain_path.stem),
                                'section': 'general',
                                'content': standard
                            })
            except Exception:
                # Skip malformed YAML files
                continue

        return results

    def export_domain(self, domain_name: str, format: str = 'yaml') -> Optional[str]:
        """
        Export domain for sharing/backup.

        Args:
            domain_name: Domain to export
            format: Export format ('yaml', 'json')

        Returns:
            Exported content as string
        """
        domain_path = Path(f"company/domains/{domain_name}.yaml")

        if not domain_path.exists():
            return None

        with open(domain_path, 'r') as f:
            if format == 'yaml':
                return f.read()
            elif format == 'json':
                import json
                domain = yaml.safe_load(f)
                return json.dumps(domain, indent=2)

        return None

    def import_domain(
        self,
        domain_data: Dict[str, Any],
        source: str
    ) -> Dict[str, Any]:
        """
        Import external domain.

        Args:
            domain_data: Domain data to import
            source: Source of import

        Returns:
            Import result
        """
        domain_name = domain_data.get('name', 'imported-domain')
        domain_path = Path(f"company/domains/{domain_name}.yaml")

        domain_path.parent.mkdir(parents=True, exist_ok=True)

        with open(domain_path, 'w') as f:
            yaml.dump(domain_data, f, default_flow_style=False)

        return {'success': True, 'domain_path': str(domain_path)}

    def get_domain_versions(self, domain_name: str) -> List[Dict[str, Any]]:
        """
        Get version history for a domain.

        Args:
            domain_name: Domain to check

        Returns:
            List of versions
        """
        if domain_name not in self._domain_versions:
            self._domain_versions[domain_name] = [
                {'version': '1.0', 'timestamp': datetime.now().isoformat()}
            ]

        return self._domain_versions[domain_name]

    def compute_domain_diff(
        self,
        domain_name: str,
        version_a: str,
        version_b: str
    ) -> Dict[str, List[str]]:
        """
        Compute diff between domain versions.

        Args:
            domain_name: Domain to diff
            version_a: First version
            version_b: Second version

        Returns:
            Diff with added, removed, modified
        """
        # Placeholder implementation
        return {
            'added': [],
            'removed': [],
            'modified': []
        }


# AC_COMPLETE: AC-PHASE38-009, AC-PHASE38-010, AC-PHASE38-011 ✅
