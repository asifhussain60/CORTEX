"""
Copilot Instructions Generator

Auto-generates .github/copilot-instructions.md from cortex-implants rules.
Combines CORTEX universal governance with company-specific rules.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from src.utils.resource_resolver import get_root_path

from .cortex_implants_loader import (
    CortexImplants,
    load_cortex_implants,
    EnforcementLevel
)

logger = logging.getLogger(__name__)


class CopilotInstructionsGenerator:
    """
    Generates .github/copilot-instructions.md from cortex-implants.
    
    Features:
    - Combines CORTEX + company governance
    - Respects priority (HIGH = company overrides CORTEX)
    - Markdown formatting with emojis
    - Auto-detection of rule conflicts
    - Version tracking
    
    Usage:
        generator = CopilotInstructionsGenerator()
        output = generator.generate(repo_path)
        generator.save(repo_path, output)
    """
    
    CORTEX_PROMPT_PATH = get_root_path() / ".github" / "prompts" / "CORTEX.prompt.md"
    
    def __init__(self):
        """Initialize generator."""
        self.template_version = "1.0.0"
    
    def generate(
        self,
        repo_path: Path,
        include_cortex: bool = True
    ) -> str:
        """
        Generate copilot-instructions.md content.
        
        Args:
            repo_path: Repository root path
            include_cortex: Include CORTEX universal governance
            
        Returns:
            Generated markdown content
        """
        logger.info(f"🔧 Generating copilot instructions for {repo_path}")
        
        # Load cortex implants
        implants = load_cortex_implants(repo_path)
        if not implants:
            logger.warning(f"⚠️  No cortex-implants found in {repo_path}")
            return self._generate_cortex_only()
        
        # Build sections
        sections = []
        
        # Header
        sections.append(self._generate_header(implants))
        
        # Company governance (priority HIGH goes first)
        if implants.get_priority() == "HIGH":
            sections.append(self._generate_company_section(implants))
            if include_cortex:
                sections.append(self._generate_cortex_section())
        else:
            if include_cortex:
                sections.append(self._generate_cortex_section())
            sections.append(self._generate_company_section(implants))
        
        # Footer
        sections.append(self._generate_footer(implants))
        
        return "\n\n".join(sections)
    
    def _generate_header(self, implants: CortexImplants) -> str:
        """Generate file header."""
        gov = implants.governance
        
        return f"""# GitHub Copilot Instructions

**Company:** {gov.company_name}  
**Repository:** {gov.repo_name} ({gov.repo_type.value})  
**Language:** {gov.language} ({gov.framework})  
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Version:** {self.template_version}

---

## ⚠️ CRITICAL: Read Company Governance First

This repository enforces **{gov.enforcement_level.value}** company governance.
All code changes must comply with rules below.

**Enforcement:** {"🚫 BLOCKED" if gov.block_on_violation else "⚠️  WARNED"} on violations  
**Priority:** {implants.get_priority()}"""
    
    def _generate_company_section(self, implants: CortexImplants) -> str:
        """Generate company governance section."""
        sections = [
            "## 🏢 Company Governance (Priority: {})".format(implants.get_priority()),
            "",
        ]
        
        # Coding standards
        if implants.coding_standards:
            sections.append(self._format_coding_standards(implants.coding_standards))
        
        # Architecture patterns
        if implants.architecture_patterns:
            sections.append(self._format_architecture_patterns(implants.architecture_patterns))
        
        # Business rules
        if implants.business_rules:
            sections.append(self._format_business_rules(implants.business_rules))
        
        # Tech stack
        if implants.tech_stack:
            sections.append(self._format_tech_stack(implants.tech_stack))
        
        # Security policy
        if implants.security_policy:
            sections.append(self._format_security_policy(implants.security_policy))
        
        return "\n\n".join(sections)
    
    def _format_coding_standards(self, standards) -> str:
        """Format coding standards section."""
        lines = ["### 📝 Coding Standards", ""]
        
        # Naming conventions
        if standards.naming_conventions:
            lines.append("**Naming Conventions:**")
            for key, value in standards.naming_conventions.items():
                if isinstance(value, dict):
                    pattern = value.get('pattern', '')
                    prefix = value.get('prefix', '')
                    example = value.get('example', '')
                    lines.append(
                        f"- **{key.title()}**: {pattern}"
                        f"{' (prefix: ' + prefix + ')' if prefix else ''}"
                        f"{' (e.g., ' + example + ')' if example else ''}"
                    )
            lines.append("")
        
        # Code style
        if standards.code_style:
            lines.append("**Code Style:**")
            for key, value in standards.code_style.items():
                lines.append(f"- {key.replace('_', ' ').title()}: {value}")
            lines.append("")
        
        # File organization
        if standards.file_organization:
            lines.append("**File Organization:**")
            for key, value in standards.file_organization.items():
                lines.append(f"- {key.replace('_', ' ').title()}: {value}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_architecture_patterns(self, patterns) -> str:
        """Format architecture patterns section."""
        lines = ["### 🏗️ Architecture Patterns", ""]
        
        # Required patterns
        if patterns.required_patterns:
            lines.append("**✅ REQUIRED PATTERNS:**")
            for pattern in patterns.required_patterns:
                lines.append(f"- **{pattern['name']}**: {pattern['description']}")
            lines.append("")
        
        # Anti-patterns
        if patterns.anti_patterns:
            lines.append("**❌ FORBIDDEN PATTERNS:**")
            for pattern in patterns.anti_patterns:
                severity_icon = "🔴" if pattern.get('severity') == "CRITICAL" else "⚠️"
                lines.append(
                    f"- {severity_icon} **{pattern['name']}**: {pattern['description']}"
                )
            lines.append("")
        
        # Layer boundaries
        if patterns.layer_boundaries:
            lines.append("**Layer Boundaries:**")
            for layer in patterns.layer_boundaries:
                allowed = ", ".join(layer.get('allowed_dependencies', []))
                lines.append(
                    f"- **{layer['layer']}**: Can depend on: {allowed or 'nothing'}"
                )
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_business_rules(self, rules) -> str:
        """Format business rules section."""
        lines = ["### 📋 Business Rules", ""]
        
        # Domain validations
        if rules.domain_validations:
            lines.append("**Domain Validations:**")
            for validation in rules.domain_validations:
                lines.append(
                    f"- **{validation['rule_id']}**: {validation['description']}"
                )
            lines.append("")
        
        # Workflow rules
        if rules.workflow_rules:
            lines.append("**Workflow Rules:**")
            for workflow in rules.workflow_rules:
                lines.append(
                    f"- **{workflow['rule_id']}**: {workflow['description']}"
                )
            lines.append("")
        
        # Compliance
        if rules.compliance:
            lines.append("**Compliance Requirements:**")
            for compliance in rules.compliance:
                lines.append(f"- **{compliance['regulation']}**:")
                for req in compliance.get('requirements', []):
                    lines.append(f"  - {req}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_tech_stack(self, tech_stack) -> str:
        """Format tech stack section."""
        lines = ["### 🔧 Tech Stack", ""]
        
        # Approved libraries
        if tech_stack.approved_libraries:
            lines.append("**✅ APPROVED LIBRARIES:**")
            for category, libs in tech_stack.approved_libraries.items():
                lines.append(f"- **{category.title()}:**")
                for lib in libs:
                    lines.append(
                        f"  - `{lib['name']}` {lib.get('version', '')} - {lib.get('purpose', '')}"
                    )
            lines.append("")
        
        # Forbidden libraries
        if tech_stack.forbidden_libraries:
            lines.append("**❌ FORBIDDEN LIBRARIES:**")
            for lib in tech_stack.forbidden_libraries:
                reason = lib.get('reason', '')
                replacement = lib.get('replacement', '')
                lines.append(
                    f"- `{lib['name']}` - {reason}"
                    f"{' (use ' + replacement + ')' if replacement else ''}"
                )
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_security_policy(self, policy) -> str:
        """Format security policy section."""
        lines = ["### 🔒 Security Policy", ""]
        
        # Authentication
        if policy.authentication:
            lines.append("**Authentication:**")
            for key, value in policy.authentication.items():
                lines.append(f"- {key.replace('_', ' ').title()}: {value}")
            lines.append("")
        
        # Data protection
        if policy.data_protection:
            lines.append("**Data Protection:**")
            pii_fields = policy.data_protection.get('pii_fields', [])
            if pii_fields:
                lines.append(f"- PII Fields: {', '.join(pii_fields)}")
            lines.append(
                f"- Encryption: {policy.data_protection.get('pii_encryption', 'Required')}"
            )
            lines.append("")
        
        # Secrets management
        if policy.secrets_management:
            lines.append("**Secrets Management:**")
            lines.append("- ❌ NO hardcoded secrets")
            if policy.secrets_management.get('use_vault'):
                lines.append("- ✅ Use secrets vault")
            lines.append("")
        
        return "\n".join(lines)
    
    def _generate_cortex_section(self) -> str:
        """Generate CORTEX universal governance section."""
        return """## 🧠 CORTEX Universal Governance

### TDD Enforcement
- **RED → GREEN → REFACTOR** mandatory
- Tests must fail before implementation
- Per-layer coverage validation

### SOLID Principles
- **Single Responsibility**: One reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Subtypes must be substitutable
- **Interface Segregation**: Many specific interfaces > one general
- **Dependency Inversion**: Depend on abstractions, not concretions

### File Organization
- ❌ NO root-level docs (use cortex-brain/documents/)
- ❌ NO duplicate code (use holistic discovery)
- ✅ Bidirectional linking for related files
- ✅ Live design docs updated with code

### Code Quality
- Max function length: 50 lines
- Max params: 4
- Max nesting depth: 3
- Explicit return types required
- Comprehensive documentation

**Full CORTEX documentation**: See `.github/prompts/CORTEX.prompt.md`"""
    
    def _generate_cortex_only(self) -> str:
        """Generate instructions when no cortex-implants found."""
        return f"""# GitHub Copilot Instructions

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Version:** {self.template_version}

---

{self._generate_cortex_section()}

---

**Note**: No cortex-implants governance found in this repository.
To add company-specific rules, create `.cortex-implants/` folder.

See: `cortex-brain/documents/guides/cortex-implants-setup-guide.md`"""
    
    def _generate_footer(self, implants: CortexImplants) -> str:
        """Generate file footer."""
        gov = implants.governance
        
        return f"""---

## 📚 References

- Company Contact: {gov.contact}
- Cortex Implants: `.cortex-implants/`
- CORTEX Documentation: `.github/prompts/CORTEX.prompt.md`

---

**⚠️  Auto-Generated File**  
This file is auto-generated from `.cortex-implants/` rules.
DO NOT edit manually. Changes will be overwritten.

To update: Modify `.cortex-implants/*.yaml` and regenerate.

**Last Updated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"""
    
    def save(self, repo_path: Path, content: str) -> Path:
        """
        Save generated content to .github/copilot-instructions.md.
        
        Args:
            repo_path: Repository root path
            content: Generated markdown content
            
        Returns:
            Path to saved file
        """
        output_dir = repo_path / ".github"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / "copilot-instructions.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"💾 Saved copilot instructions to {output_file}")
        return output_file
    
    def generate_and_save(self, repo_path: Path) -> Path:
        """
        Generate and save copilot instructions in one step.
        
        Args:
            repo_path: Repository root path
            
        Returns:
            Path to saved file
        """
        content = self.generate(repo_path)
        return self.save(repo_path, content)


def generate_copilot_instructions(repo_path: Path) -> Path:
    """
    Convenience function to generate copilot instructions.
    
    Args:
        repo_path: Repository root path
        
    Returns:
        Path to generated file
    """
    generator = CopilotInstructionsGenerator()
    return generator.generate_and_save(repo_path)
