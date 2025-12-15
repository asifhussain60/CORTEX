"""
Cortex Implants CLI Commands

Provides CLI commands for managing cortex-implants:
- cortex init implants - Initialize implants in repo
- cortex implant update - Regenerate copilot-instructions.md
- cortex implant validate - Validate implants structure
- cortex implant status - Show implants status

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

from pathlib import Path
from typing import Optional, Dict, Any
import shutil
import logging

from src.tier0.cortex_implants_loader import (
    CortexImplantsLoader,
    CortexImplants
)
from src.tier0.copilot_instructions_generator import (
    CopilotInstructionsGenerator,
    generate_copilot_instructions
)
from src.tier0.cortex_implants_integrator import (
    get_implants_integrator,
    has_cortex_implants
)

logger = logging.getLogger(__name__)


class ImplantsCommands:
    """CLI commands for cortex-implants management."""
    
    def __init__(self, repo_path: Optional[Path] = None):
        """
        Initialize commands.
        
        Args:
            repo_path: Repository path (auto-detect if None)
        """
        self.repo_path = repo_path or Path.cwd()
        self.loader = CortexImplantsLoader()
        self.generator = CopilotInstructionsGenerator()
        
        # Templates directory
        self.templates_dir = (
            Path(__file__).parent.parent.parent.parent / 
            "cortex-brain" / "templates" / "cortex-implants-templates"
        )
    
    def init_implants(
        self,
        template: str = "default",
        company_name: Optional[str] = None,
        project_name: Optional[str] = None,
        force: bool = False
    ) -> bool:
        """
        Initialize cortex-implants in repository.
        
        Creates .cortex-implants/ folder with templates:
        - governance.yaml (required)
        - coding-standards.yaml (optional)
        - architecture-patterns.yaml (optional)
        - business-rules.yaml (optional)
        - tech-stack.yaml (optional)
        - security-policy.yaml (optional)
        
        Args:
            template: Template name (default, web-app, api, library)
            company_name: Company/organization name
            project_name: Project name
            force: Overwrite existing implants
            
        Returns:
            True if successful
        """
        implants_dir = self.repo_path / ".cortex-implants"
        
        # Check if already exists
        if implants_dir.exists() and not force:
            logger.error(f"❌ Cortex implants already exist at {implants_dir}")
            logger.info("   Use --force to overwrite")
            return False
        
        # Create directory
        implants_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Creating cortex-implants at {implants_dir}")
        
        # Copy template files
        if not self.templates_dir.exists():
            logger.error(f"❌ Templates directory not found: {self.templates_dir}")
            return False
        
        files_copied = []
        for template_file in self.templates_dir.glob("*.yaml"):
            target_file = implants_dir / template_file.name
            shutil.copy2(template_file, target_file)
            files_copied.append(template_file.name)
            logger.info(f"   ✅ {template_file.name}")
        
        # Customize governance.yaml if company/project provided
        if company_name or project_name:
            self._customize_governance(
                implants_dir / "governance.yaml",
                company_name=company_name,
                project_name=project_name
            )
        
        # Create version marker
        version_file = implants_dir / ".cortex-company-version"
        version_file.write_text("1.0.0")
        
        logger.info(f"\n✅ Cortex implants initialized!")
        logger.info(f"   Location: {implants_dir}")
        logger.info(f"   Files: {len(files_copied)}")
        logger.info(f"\n📝 Next steps:")
        logger.info(f"   1. Edit {implants_dir}/governance.yaml")
        logger.info(f"   2. Customize other YAML files as needed")
        logger.info(f"   3. Run 'cortex implant update' to generate copilot-instructions.md")
        
        return True
    
    def _customize_governance(
        self,
        governance_file: Path,
        company_name: Optional[str] = None,
        project_name: Optional[str] = None
    ) -> None:
        """Customize governance.yaml with provided values."""
        import yaml
        
        with open(governance_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if company_name:
            data['company_name'] = company_name
        
        if project_name:
            data['repo_name'] = project_name  # Map project_name to repo_name
        
        with open(governance_file, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"   🔧 Customized governance.yaml")
    
    def update_implants(self) -> bool:
        """
        Update copilot-instructions.md from cortex-implants.
        
        Regenerates .github/copilot-instructions.md based on:
        - .cortex-implants/*.yaml rules
        - CORTEX universal governance
        - Priority settings (HIGH/MEDIUM/LOW)
        
        Returns:
            True if successful
        """
        logger.info("🔄 Updating copilot-instructions.md...")
        
        # Check if implants exist
        if not has_cortex_implants(self.repo_path):
            logger.error(f"❌ No cortex-implants found in {self.repo_path}")
            logger.info("   Run 'cortex init implants' first")
            return False
        
        try:
            # Generate instructions
            output_file = generate_copilot_instructions(self.repo_path)
            
            logger.info(f"✅ Updated copilot-instructions.md")
            logger.info(f"   Location: {output_file}")
            
            # Show summary
            integrator = get_implants_integrator(self.repo_path)
            logger.info(f"\n{integrator.get_context_summary()}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update: {e}")
            return False
    
    def validate_implants(self) -> bool:
        """
        Validate cortex-implants structure and content.
        
        Checks:
        - Directory structure
        - Required files present
        - YAML syntax valid
        - Schema compliance
        - Cross-references valid
        
        Returns:
            True if valid
        """
        logger.info("🔍 Validating cortex-implants...")
        
        implants_dir = self.repo_path / ".cortex-implants"
        
        if not implants_dir.exists():
            logger.error(f"❌ No cortex-implants found in {self.repo_path}")
            return False
        
        errors = []
        warnings = []
        
        # Check required files
        required_files = ["governance.yaml"]
        for req_file in required_files:
            file_path = implants_dir / req_file
            if not file_path.exists():
                errors.append(f"Missing required file: {req_file}")
        
        # Try loading with loader
        try:
            implants = self.loader.load(self.repo_path)
            
            if implants is None:
                errors.append("Failed to load implants")
            else:
                logger.info("✅ Structure valid")
                logger.info(f"   Company: {implants.governance.company_name}")
                logger.info(f"   Repo: {implants.governance.repo_name}")
                logger.info(f"   Priority: {implants.get_priority()}")
                
                # Check optional files
                if implants.coding_standards:
                    logger.info("   ✅ Coding standards defined")
                if implants.architecture_patterns:
                    logger.info("   ✅ Architecture patterns defined")
                if implants.tech_stack:
                    logger.info("   ✅ Tech stack defined")
                if implants.business_rules:
                    logger.info("   ✅ Business rules defined")
                if implants.security_policy:
                    logger.info("   ✅ Security policy defined")
        
        except Exception as e:
            errors.append(f"Validation error: {e}")
        
        # Report results
        if errors:
            logger.error(f"\n❌ Validation failed with {len(errors)} error(s):")
            for error in errors:
                logger.error(f"   - {error}")
            return False
        
        if warnings:
            logger.warning(f"\n⚠️  {len(warnings)} warning(s):")
            for warning in warnings:
                logger.warning(f"   - {warning}")
        
        logger.info("\n✅ Cortex implants valid!")
        return True
    
    def show_status(self) -> Dict[str, Any]:
        """
        Show cortex-implants status.
        
        Returns:
            Status dictionary with:
            - present: bool
            - location: Path
            - company: str
            - project: str
            - priority: str
            - active_rules: List[str]
        """
        logger.info("📊 Cortex Implants Status\n")
        
        implants_dir = self.repo_path / ".cortex-implants"
        
        status = {
            "present": implants_dir.exists(),
            "location": str(implants_dir),
            "company": None,
            "repo": None,
            "priority": "NONE",
            "active_rules": []
        }
        
        if not status["present"]:
            logger.info("❌ No cortex-implants found")
            logger.info(f"   Searched in: {self.repo_path}")
            logger.info(f"\n💡 To initialize: cortex init implants")
            return status
        
        # Load implants
        try:
            integrator = get_implants_integrator(self.repo_path)
            
            if integrator.has_implants():
                implants = integrator.implants
                gov = implants.governance
                
                status.update({
                    "company": gov.company_name,
                    "repo": gov.repo_name,
                    "priority": integrator.get_priority()
                })
                
                logger.info(f"✅ Cortex implants present")
                logger.info(f"   Location: {implants_dir}")
                logger.info(f"   Company: {gov.company_name}")
                logger.info(f"   Repo: {gov.repo_name}")
                logger.info(f"   Priority: {integrator.get_priority()}")
                logger.info(f"   Enforcement: {gov.enforcement_level.value}")
                logger.info(f"\n📋 Active Rules:")
                
                if implants.coding_standards:
                    logger.info("   ✅ Coding Standards")
                    status["active_rules"].append("coding_standards")
                
                if implants.architecture_patterns:
                    logger.info("   ✅ Architecture Patterns")
                    status["active_rules"].append("architecture_patterns")
                
                if implants.tech_stack:
                    logger.info("   ✅ Tech Stack Restrictions")
                    status["active_rules"].append("tech_stack")
                
                if implants.business_rules:
                    logger.info("   ✅ Business Rules")
                    status["active_rules"].append("business_rules")
                
                if implants.security_policy:
                    logger.info("   ✅ Security Policy")
                    status["active_rules"].append("security_policy")
                
                # Check if copilot-instructions.md exists
                copilot_file = self.repo_path / ".github" / "copilot-instructions.md"
                if copilot_file.exists():
                    logger.info(f"\n📄 Copilot Instructions: ✅ Generated")
                else:
                    logger.info(f"\n📄 Copilot Instructions: ⚠️  Not generated")
                    logger.info(f"   Run: cortex implant update")
        
        except Exception as e:
            logger.error(f"❌ Error reading implants: {e}")
        
        return status


# Convenience functions for CLI integration

def cmd_init_implants(
    company_name: Optional[str] = None,
    project_name: Optional[str] = None,
    force: bool = False
) -> bool:
    """Initialize cortex-implants (CLI wrapper)."""
    commands = ImplantsCommands()
    return commands.init_implants(
        company_name=company_name,
        project_name=project_name,
        force=force
    )


def cmd_update_implants() -> bool:
    """Update copilot-instructions.md (CLI wrapper)."""
    commands = ImplantsCommands()
    return commands.update_implants()


def cmd_validate_implants() -> bool:
    """Validate cortex-implants (CLI wrapper)."""
    commands = ImplantsCommands()
    return commands.validate_implants()


def cmd_status_implants() -> Dict[str, Any]:
    """Show implants status (CLI wrapper)."""
    commands = ImplantsCommands()
    return commands.show_status()
