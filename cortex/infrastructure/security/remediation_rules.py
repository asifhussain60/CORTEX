"""
Remediation Rules Registry - Vulnerability-specific remediation patterns
Authority: CORE-035 (Single Canonical Implementation)
AC-ID: AC-SECURITY-REMEDIATION-RULES-001

Provides pattern-based remediation for:
- GitHub Actions unpacking (Arnica)
- Python dependencies (Safety, Pip-audit)  
- Expression injection (GitHub Actions)
- Secrets (Veracode, Bandit)
"""

from pathlib import Path
from typing import Dict, List, Optional

from cortex.infrastructure.security.vulnerability_models import (
    RemediationRule,
    RemediationType,
)


def get_github_actions_rules() -> List[RemediationRule]:
    """GitHub Actions security rules."""
    return [
        RemediationRule(
            id="GHA-PIN-SHA-001",
            vulnerability_id="ARNICA:GHA-UNPIN",
            remediation_type=RemediationType.AUTO_FIX,
            pattern=r'uses:\s+([\w\-/]+)@v[\d.]+',
            replacement_template=r'uses: \1@{latest_sha}',
            priority=1,
            description="Pin GitHub Action to commit SHA instead of version tag",
            tools=["arnica", "semgrep"],
            config={"enable_auto_fetch_sha": True}
        ),
        RemediationRule(
            id="GHA-ESCAPE-INJECTION-001",
            vulnerability_id="GHA-EXPRESSION-INJECTION",
            remediation_type=RemediationType.AUTO_FIX,
            pattern=r'run:\s*\|\s*.*github\.event\.(issue|pull_request|comment)\.(body|title)',
            replacement_template=r'env:\n  EVENT_DATA: ${{ toJson(github.event) }}\nrun: |\n  # Use $EVENT_DATA instead of direct github.event access',
            priority=2,
            description="Escape potentially unsafe github.event expressions",
            tools=["arnica", "semgrep"]
        )
    ]


def get_python_dependency_rules() -> List[RemediationRule]:
    """Python dependency security rules."""
    return [
        RemediationRule(
            id="PYTHON-DEP-AUDIT-001",
            vulnerability_id="SAFETY:VULNERABLE-DEPENDENCY",
            remediation_type=RemediationType.MANUAL,
            pattern=None,
            replacement_template=None,
            priority=1,
            description="Review and upgrade vulnerable Python dependency to patched version",
            tools=["safety", "pip-audit", "veracode"],
            config={"create_ticket": True}
        ),
        RemediationRule(
            id="PYTHON-DEP-HASH-CHECK-001",
            vulnerability_id="VERACODE:CWE-494",
            remediation_type=RemediationType.MANUAL,
            pattern=None,
            replacement_template=None,
            priority=1,
            description="Add hash verification for package downloads",
            tools=["veracode"],
            config={"create_ticket": True}
        )
    ]


def get_secrets_rules() -> List[RemediationRule]:
    """Secrets management rules."""
    return [
        RemediationRule(
            id="SECRET-ROTATE-001",
            vulnerability_id="VERACODE:EXPOSED-SECRET",
            remediation_type=RemediationType.MANUAL,
            pattern=None,
            replacement_template=None,
            priority=1,
            description="Rotate exposed secret immediately and remove from repository history",
            tools=["bandit", "detect-secrets", "veracode"],
            config={"severity": "CRITICAL", "create_ticket": True}
        )
    ]


def get_expression_injection_rules() -> List[RemediationRule]:
    """Expression injection prevention rules."""
    return [
        RemediationRule(
            id="INJECTION-EXPR-001",
            vulnerability_id="GHA-EXPRESSION-INJECTION",
            remediation_type=RemediationType.AUTO_FIX,
            pattern=r'(\$\{\{.*github\.event\..*\}\})',
            replacement_template=r'${{ env.SAFE_EVENT_DATA }}',
            priority=1,
            description="Move github.event expressions to environment variables",
            tools=["semgrep", "arnica"]
        )
    ]


class RemediationRulesRegistry:
    """Central registry for remediation rules."""

    def __init__(self) -> None:
        """Initialize rule registry."""
        self.rules: Dict[str, RemediationRule] = {}
        self._load_rules()

    def _load_rules(self):
        """Load all rules from rule providers."""
        all_rules = (
            get_github_actions_rules()
            + get_python_dependency_rules()
            + get_secrets_rules()
            + get_expression_injection_rules()
        )

        for rule in all_rules:
            self.rules[rule.id] = rule

    def get_rule(self, rule_id: str) -> Optional[RemediationRule]:
        """Get rule by ID."""
        return self.rules.get(rule_id)

    def get_rules_for_vulnerability(
        self,
        vulnerability_id: str
    ) -> List[RemediationRule]:
        """Get all rules applicable to a vulnerability ID."""
        return [
            rule for rule in self.rules.values()
            if rule.vulnerability_id == vulnerability_id
            or vulnerability_id.startswith(rule.vulnerability_id.rstrip(":"))
        ]

    def get_rules_for_tool(self, tool: str) -> List[RemediationRule]:
        """Get all rules for a specific tool."""
        return [
            rule for rule in self.rules.values()
            if tool in rule.tools
        ]

    def get_auto_fixable_rules(self) -> List[RemediationRule]:
        """Get all rules that can auto-fix."""
        return [
            rule for rule in self.rules.values()
            if rule.remediation_type == RemediationType.AUTO_FIX
        ]

    def list_all(self) -> List[RemediationRule]:
        """List all registered rules."""
        return list(self.rules.values())


# Global registry instance
_registry_instance = None


def get_registry() -> RemediationRulesRegistry:
    """Get or create global registry."""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = RemediationRulesRegistry()
    return _registry_instance
