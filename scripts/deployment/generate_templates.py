"""Day-zero template generator for tier1 and tier2 rules.

This module generates clean template files for production deployment,
resetting tier1 and tier2 to day-zero state.

PHASE-DEPLOYMENT-001: AC-DEP-001-02
"""

import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional


class TemplateGenerator:
    """Generates day-zero templates for tier1 and tier2 rules.
    
    Creates template files that serve as the starting point for
    production deployments. Custom rules should extend these templates.
    
    Attributes:
        tier1_path: Path to tier1 directory.
        tier2_path: Path to tier2 directory.
    """
    
    def __init__(
        self,
        tier1_path: Optional[Path] = None,
        tier2_path: Optional[Path] = None,
    ) -> None:
        """Initialize the generator.
        
        Args:
            tier1_path: Path to tier1 directory.
            tier2_path: Path to tier2 directory.
        """
        self.tier1_path = Path(tier1_path) if tier1_path else Path("cortex_brain/tier1")
        self.tier2_path = Path(tier2_path) if tier2_path else Path("cortex_brain/tier2")
    
    def generate_tier1_templates(self) -> List[Path]:
        """Generate tier1 template files.
        
        Returns:
            List of created template paths.
        """
        templates_dir = self.tier1_path / "templates"
        templates_dir.mkdir(parents=True, exist_ok=True)
        
        created = []
        
        # Domain rules template
        domain_template = templates_dir / "domain-rules.yaml.template"
        domain_template.write_text(self._get_domain_template())
        created.append(domain_template)
        
        # Orchestrator rules template
        orchestrator_template = templates_dir / "orchestrator-rules.yaml.template"
        orchestrator_template.write_text(self._get_orchestrator_template())
        created.append(orchestrator_template)
        
        return created
    
    def generate_tier2_templates(self) -> List[Path]:
        """Generate tier2 template files.
        
        Returns:
            List of created template paths.
        """
        templates_dir = self.tier2_path / "templates"
        templates_dir.mkdir(parents=True, exist_ok=True)
        
        created = []
        
        # Context rules template
        context_template = templates_dir / "context-rules.yaml.template"
        context_template.write_text(self._get_context_template())
        created.append(context_template)
        
        # Safety rules template
        safety_template = templates_dir / "safety-rules.yaml.template"
        safety_template.write_text(self._get_safety_template())
        created.append(safety_template)
        
        return created
    
    def reset_to_templates(self) -> None:
        """Reset tier1 and tier2 to template-only state.
        
        Removes all non-template YAML files from tier1 and tier2.
        """
        for tier_path in [self.tier1_path, self.tier2_path]:
            if not tier_path.exists():
                continue
            
            for yaml_file in tier_path.glob("*.yaml"):
                # Don't remove files in templates subdirectory
                if "templates" not in str(yaml_file):
                    yaml_file.unlink()
    
    def create_version_marker(self, version: str = "1.0.0") -> Path:
        """Create .cortex-version marker file.
        
        Args:
            version: Semantic version string.
            
        Returns:
            Path to created version file.
        """
        version_file = Path(".cortex-version")
        version_file.write_text(f"{version}\n")
        return version_file
    
    def _get_domain_template(self) -> str:
        """Get domain rules template content.
        
        Returns:
            Template YAML content.
        """
        return f'''# Domain Rules Template
# Generated: {datetime.now().isoformat()}
# Tier: tier1 (domain-specific rules)
#
# This template defines domain-specific governance rules that extend tier0.
# Copy this file to tier1/domain-rules.yaml and customize for your domain.

metadata:
  template_version: "1.0.0"
  tier: 1
  description: "Domain-specific governance rules"
  extends: "tier0/core-rules.yaml"

rules: []
  # Example domain rule:
  # - id: "DOM-001"
  #   severity: "WARNING"
  #   description: "Domain-specific validation"
  #   condition: "context.domain == 'financial'"
  #   action: "require_approval"
'''

    def _get_orchestrator_template(self) -> str:
        """Get orchestrator rules template content.
        
        Returns:
            Template YAML content.
        """
        return f'''# Orchestrator Rules Template
# Generated: {datetime.now().isoformat()}
# Tier: tier1 (orchestrator-specific rules)
#
# This template defines orchestrator-specific governance rules.
# Copy this file to tier1/orchestrator-rules.yaml and customize.

metadata:
  template_version: "1.0.0"
  tier: 1
  description: "Orchestrator-specific governance rules"
  extends: "tier0/core-rules.yaml"

rules: []
  # Example orchestrator rule:
  # - id: "ORCH-001"
  #   severity: "ERROR"
  #   description: "Orchestrator routing validation"
  #   condition: "orchestrator.type == 'builder'"
  #   action: "validate_phase_lock"
'''

    def _get_context_template(self) -> str:
        """Get context rules template content.
        
        Returns:
            Template YAML content.
        """
        return f'''# Context Rules Template
# Generated: {datetime.now().isoformat()}
# Tier: tier2 (context-specific rules)
#
# This template defines context-specific governance rules.
# These rules apply based on execution context (CI, development, production).

metadata:
  template_version: "1.0.0"
  tier: 2
  description: "Context-specific governance rules"
  extends: "tier1/domain-rules.yaml"

rules: []
  # Example context rule:
  # - id: "CTX-001"
  #   severity: "WARNING"
  #   description: "CI-specific validation"
  #   condition: "context.environment == 'ci'"
  #   action: "enforce_strict_typing"
'''

    def _get_safety_template(self) -> str:
        """Get safety rules template content.
        
        Returns:
            Template YAML content.
        """
        return f'''# Safety Rules Template
# Generated: {datetime.now().isoformat()}
# Tier: tier2 (safety and compliance rules)
#
# This template defines safety and compliance rules.
# These rules help prevent hallucinations and ensure compliance.

metadata:
  template_version: "1.0.0"
  tier: 2
  description: "Safety and compliance rules"
  extends: "tier1/domain-rules.yaml"

rules: []
  # Example safety rule:
  # - id: "SAFE-001"
  #   severity: "CRITICAL"
  #   description: "Prevent hallucinated file paths"
  #   condition: "action.creates_file"
  #   action: "validate_path_exists"
'''


def main() -> int:
    """CLI entry point for template generation.
    
    Returns:
        Exit code.
    """
    import sys
    
    generator = TemplateGenerator()
    
    if "--generate" in sys.argv:
        tier1 = generator.generate_tier1_templates()
        tier2 = generator.generate_tier2_templates()
        print(f"Generated {len(tier1)} tier1 templates and {len(tier2)} tier2 templates")
        return 0
    
    if "--reset" in sys.argv:
        generator.reset_to_templates()
        print("Reset tier1 and tier2 to template-only state")
        return 0
    
    if "--version" in sys.argv:
        version = sys.argv[sys.argv.index("--version") + 1] if len(sys.argv) > sys.argv.index("--version") + 1 else "1.0.0"
        path = generator.create_version_marker(version)
        print(f"Created version marker: {path} with version {version}")
        return 0
    
    print("Usage: generate_templates.py [--generate|--reset|--version <ver>]")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
