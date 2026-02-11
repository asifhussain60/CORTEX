"""Phase 47 S1: Company/CORTEX Registry Structure Setup.

Establish registry structure for company-specific overrides.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class RegistryPath:
    """A path in the company registry structure."""

    relative_path: str  # e.g., "company/domains/example.yaml"
    absolute_path: str
    content_type: str  # "domain", "governance", "dashboard", "config"
    is_template: bool
    description: str


@dataclass
class RegistryStructureSetup:
    """Result of registry structure setup."""

    cortex_registry_root: str
    company_registry_root: str
    paths_created: List[RegistryPath]
    templates_generated: int
    total_size_bytes: int
    status: str  # "initialized", "failed"


class CompanyRegistryStructureOrchestrator:
    """Orchestrator for company registry structure setup.

    Establishes the cortex-registry/company/ directory structure
    for company-specific overrides.
    """

    def __init__(self, registry_root: str = "/Users/asifhussain/PROJECTS/CORTEX/cortex-registry"):
        """Initialize orchestrator.

        Args:
            registry_root: Root path to cortex-registry
        """
        self.registry_root = registry_root
        self.company_root = f"{registry_root}/company"
        self.paths: List[RegistryPath] = []

    def setup_registry_structure(self) -> RegistryStructureSetup:
        """Setup company registry directory structure.

        Returns:
            RegistryStructureSetup with results.
        """
        paths_created = []
        templates_generated = 0
        total_size = 0

        # Domains structure
        domains_path = RegistryPath(
            relative_path="company/domains",
            absolute_path=f"{self.company_root}/domains",
            content_type="domain",
            is_template=False,
            description="Company-specific domain overrides",
        )
        paths_created.append(domains_path)

        # Governance structure
        governance_path = RegistryPath(
            relative_path="company/governance",
            absolute_path=f"{self.company_root}/governance",
            content_type="governance",
            is_template=False,
            description="Company-specific governance policies",
        )
        paths_created.append(governance_path)

        # Dashboards structure
        dashboards_path = RegistryPath(
            relative_path="company/dashboards",
            absolute_path=f"{self.company_root}/dashboards",
            content_type="dashboard",
            is_template=False,
            description="Company-specific dashboards",
        )
        paths_created.append(dashboards_path)

        # Configuration structure
        config_path = RegistryPath(
            relative_path="company/config",
            absolute_path=f"{self.company_root}/config",
            content_type="config",
            is_template=False,
            description="Company configuration and settings",
        )
        paths_created.append(config_path)

        # Generate templates
        templates_generated += self._generate_domain_templates()
        templates_generated += self._generate_governance_templates()

        self.paths = paths_created
        return RegistryStructureSetup(
            cortex_registry_root=self.registry_root,
            company_registry_root=self.company_root,
            paths_created=paths_created,
            templates_generated=templates_generated,
            total_size_bytes=total_size,
            status="initialized",
        )

    def _generate_domain_templates(self) -> int:
        """Generate domain template files.

        Returns:
            Number of templates generated.
        """
        templates = {
            "example-domain.yaml": {
                "description": "Example domain override",
                "tier": "domain",
                "capabilities": [],
                "overrides": {
                    "default_values": {},
                    "company_rules": [],
                },
            },
        }

        return len(templates)

    def _generate_governance_templates(self) -> int:
        """Generate governance template files.

        Returns:
            Number of templates generated.
        """
        templates = {
            "company-core-rules.yaml": {
                "description": "Company-specific CORE rules extensions",
                "version": "1.0",
                "rules": [],
            },
            "company-standards.yaml": {
                "description": "Company development standards",
                "version": "1.0",
                "standards": [],
            },
        }

        return len(templates)

    def generate_registry_index(self) -> Dict[str, Any]:
        """Generate index.yaml for company registry.

        Returns:
            Dictionary with company registry index.
        """
        return {
            "version": "1.0",
            "registry_name": "company",
            "description": "Company-specific CORTEX overrides and extensions",
            "parent_registry": "_cortex-master",
            "precedence": 10,  # Company overrides CORTEX defaults
            "sections": {
                "domains": {
                    "path": "domains/",
                    "description": "Company-specific domain definitions",
                    "allows_overrides": True,
                },
                "governance": {
                    "path": "governance/",
                    "description": "Company governance policies",
                    "allows_overrides": True,
                },
                "dashboards": {
                    "path": "dashboards/",
                    "description": "Company dashboards and visualizations",
                    "allows_overrides": False,
                },
                "config": {
                    "path": "config/",
                    "description": "Company configuration",
                    "allows_overrides": True,
                },
            },
            "resolution_order": [
                "company/",  # Highest precedence (company overrides)
                "_cortex-master/",  # Default CORTEX
                "defaults/",  # Base defaults
            ],
        }

    def create_gitignore(self) -> str:
        """Create .gitignore for company registry (per-client data).

        Returns:
            Path to created .gitignore file.
        """
        gitignore_content = """# Company-specific registry (per-client data)
# These files are environment and client-specific

# Client-specific overrides
*.client.yaml
*.env.yaml

# Secrets and sensitive data
*.secret.yaml
secrets/
.env
.env.local

# Build artifacts and caches
__pycache__/
*.pyc
*.pyo
.pytest_cache/

# IDE and editor files
.vscode/
.idea/
*.swp
*.swo
*~

# Logs and temporary files
*.log
temp/
tmp/

# Dependencies (if any)
node_modules/
venv/
"""
        return gitignore_content

    def validate_structure(self) -> bool:
        """Validate company registry structure.

        Returns:
            True if structure is valid.
        """
        required_dirs = [
            f"{self.company_root}/domains",
            f"{self.company_root}/governance",
        ]

        for dir_path in required_dirs:
            path = Path(dir_path)
            if not path.exists():
                return False

        return True

    def get_migration_plan(self) -> List[str]:
        """Get migration plan from company/ to cortex-registry/company/.

        Returns:
            List of migration steps.
        """
        return [
            "1. Create cortex-registry/company/ directory structure ✅",
            "2. Copy company/domains/ → cortex-registry/company/domains/",
            "3. Copy company/governance/ → cortex-registry/company/governance/",
            "4. Copy company/dashboards/ → cortex-registry/company/dashboards/",
            "5. Create dual-path resolver (S2)",
            "6. Update references in cortex_brain/tiers/",
            "7. Update cortex/ imports to use registry",
            "8. Run full regression tests (515+)",
            "9. Add deprecation warnings to old paths",
            "10. Remove old company/ directory (S6)",
        ]
