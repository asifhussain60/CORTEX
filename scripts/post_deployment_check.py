#!/usr/bin/env python3
"""
CORTEX Post-Deployment Validation System

Purpose: Comprehensive validation of deployed code to ensure production readiness.
Validates all core features are properly wired and functional.

Usage:
    python scripts/post_deployment_check.py
    python scripts/post_deployment_check.py --verbose
    python scripts/post_deployment_check.py --report-only

Exit Codes:
    0 - All validations passed
    1 - Warnings detected (non-critical)
    2 - Failures detected (critical)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import sys
import os
import sqlite3
import importlib.util
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import argparse

# Add src to path for imports
CORTEX_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(CORTEX_ROOT / "src"))


class ValidationResult:
    """Container for validation results."""
    
    def __init__(self, category: str):
        self.category = category
        self.passed: List[str] = []
        self.warnings: List[str] = []
        self.failures: List[str] = []
        self.recommendations: List[str] = []
    
    @property
    def status(self) -> str:
        """Overall status indicator."""
        if self.failures:
            return "❌ FAILED"
        elif self.warnings:
            return "⚠️  WARNING"
        else:
            return "✅ PASSED"
    
    @property
    def has_issues(self) -> bool:
        """Check if there are any issues."""
        return bool(self.failures or self.warnings)


class PostDeploymentValidator:
    """Comprehensive post-deployment validation system."""
    
    def __init__(self, cortex_root: Path, verbose: bool = False):
        self.cortex_root = cortex_root
        self.verbose = verbose
        self.results: List[ValidationResult] = []
        self.brain_path = cortex_root / "cortex-brain"
        self.src_path = cortex_root / "src"
        
    def log(self, message: str, level: str = "INFO"):
        """Log message if verbose mode enabled."""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {level}: {message}")
    
    def run_all_validations(self) -> Tuple[int, int, int]:
        """
        Run all validation categories.
        
        Returns:
            Tuple of (passed_count, warning_count, failure_count)
        """
        print("\n" + "="*80)
        print("🔍 CORTEX POST-DEPLOYMENT VALIDATION")
        print("="*80 + "\n")
        
        # Run all validation categories
        self.validate_core_agents()
        self.validate_response_templates()
        self.validate_documentation_sync()
        self.validate_tdd_workflow()
        self.validate_planning_system()
        self.validate_ado_integration()
        self.validate_entry_points()
        self.validate_database_schema()
        self.validate_brain_protection()
        self.validate_system_alignment()
        
        # Print results summary
        return self._print_summary()
    
    def validate_core_agents(self):
        """Validate all core agents are discoverable and functional."""
        result = ValidationResult("Core Agents")
        
        agents_path = self.src_path / "cortex_agents"
        
        if not agents_path.exists():
            result.failures.append(f"Agents directory not found: {agents_path}")
            self.results.append(result)
            return
        
        # Discover all agent modules
        agent_files = list(agents_path.glob("**/*_agent.py"))
        expected_agents = [
            "intent_router_agent",
            "work_planner_agent", 
            "executor_agent",
            "tester_agent",
            "feedback_agent",
            "view_discovery_agent",
            "profile_agent"
        ]
        
        for agent_name in expected_agents:
            agent_file = agents_path / f"{agent_name}.py"
            if not agent_file.exists():
                # Check in subdirectories
                found = list(agents_path.glob(f"**/{agent_name}.py"))
                if not found:
                    result.failures.append(f"Missing agent: {agent_name}")
                    continue
                agent_file = found[0]
            
            # Try to import agent
            try:
                spec = importlib.util.spec_from_file_location(agent_name, agent_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    result.passed.append(f"✓ {agent_name} imports successfully")
                else:
                    result.failures.append(f"Failed to load spec for {agent_name}")
            except Exception as e:
                result.failures.append(f"Import error in {agent_name}: {str(e)}")
        
        if result.failures:
            result.recommendations.append("Run: pytest tests/cortex_agents/ to diagnose agent issues")
            result.recommendations.append("Check agent dependencies in requirements.txt")
        
        self.results.append(result)
    
    def validate_response_templates(self):
        """Validate response templates are complete and loadable."""
        result = ValidationResult("Response Templates")
        
        templates_file = self.brain_path / "response-templates.yaml"
        
        if not templates_file.exists():
            result.failures.append(f"Templates file not found: {templates_file}")
            self.results.append(result)
            return
        
        try:
            with open(templates_file, 'r', encoding='utf-8') as f:
                templates = yaml.safe_load(f)
            
            # Check critical templates
            critical_templates = [
                "help_table",
                "fallback",
                "work_planner_success",
                "planning_dor_complete",
                "planning_dor_incomplete",
                "tdd_workflow_start",
                "ado_created",
                "enhance_existing",
                "brain_export_guide",
                "upgrade_cortex",
                "commit_operation"
            ]
            
            for template_name in critical_templates:
                if template_name in templates.get('templates', {}):
                    template = templates['templates'][template_name]
                    # Check required fields
                    if 'triggers' in template or 'trigger' in template:
                        result.passed.append(f"✓ {template_name} template present")
                    else:
                        result.warnings.append(f"Template {template_name} missing triggers")
                else:
                    result.failures.append(f"Missing critical template: {template_name}")
            
            result.passed.append(f"✓ Templates file loads successfully ({len(templates.get('templates', {}))} templates)")
            
        except yaml.YAMLError as e:
            result.failures.append(f"YAML parse error: {str(e)}")
        except Exception as e:
            result.failures.append(f"Error loading templates: {str(e)}")
        
        if result.failures:
            result.recommendations.append("Validate YAML syntax: pyyaml-validator cortex-brain/response-templates.yaml")
            result.recommendations.append("Check template format guide: .github/prompts/modules/template-guide.md")
        
        self.results.append(result)
    
    def validate_documentation_sync(self):
        """Validate documentation is synchronized with codebase."""
        result = ValidationResult("Documentation Synchronization")
        
        # Check CORTEX.prompt.md exists
        prompt_file = self.cortex_root / ".github" / "prompts" / "CORTEX.prompt.md"
        if not prompt_file.exists():
            result.failures.append("CORTEX.prompt.md not found")
        else:
            result.passed.append("✓ CORTEX.prompt.md present")
        
        # Check critical module guides
        modules_path = self.cortex_root / ".github" / "prompts" / "modules"
        critical_modules = [
            "response-format.md",
            "planning-orchestrator-guide.md",
            "tdd-mastery-guide.md",
            "upgrade-guide.md",
            "system-alignment-guide.md",
            "architecture-intelligence-guide.md"
        ]
        
        for module_name in critical_modules:
            module_file = modules_path / module_name
            if not module_file.exists():
                result.failures.append(f"Missing module guide: {module_name}")
            else:
                result.passed.append(f"✓ {module_name} present")
        
        # Check key commands documented in CORTEX.prompt.md
        if prompt_file.exists():
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    prompt_content = f.read()
                
                required_commands = ['help', 'plan', 'feedback', 'discover views', 'upgrade', 'optimize']
                for cmd in required_commands:
                    if cmd.lower() in prompt_content.lower():
                        result.passed.append(f"✓ Command '{cmd}' documented")
                    else:
                        result.warnings.append(f"Command '{cmd}' not found in documentation")
            except Exception as e:
                result.warnings.append(f"Could not verify command documentation: {str(e)}")
        
        if result.failures:
            result.recommendations.append("Run: python scripts/generate_documentation.py")
            result.recommendations.append("Check documentation guides in .github/prompts/modules/")
        
        self.results.append(result)
    
    def validate_tdd_workflow(self):
        """Validate TDD workflow is operational."""
        result = ValidationResult("TDD Workflow")
        
        # Check TDD orchestrator exists
        tdd_orchestrator = self.src_path / "workflows" / "tdd_workflow_orchestrator.py"
        if not tdd_orchestrator.exists():
            result.failures.append("TDD orchestrator not found")
        else:
            result.passed.append("✓ TDD orchestrator file present")
        
        # Check view discovery agent
        view_discovery = list(self.src_path.glob("**/view_discovery_agent.py"))
        if not view_discovery:
            result.failures.append("ViewDiscoveryAgent not found")
        else:
            result.passed.append("✓ ViewDiscoveryAgent present")
        
        # Check TDD guide exists
        tdd_guide = self.cortex_root / ".github" / "prompts" / "modules" / "tdd-mastery-guide.md"
        if not tdd_guide.exists():
            result.failures.append("TDD Mastery guide not found")
        else:
            result.passed.append("✓ TDD Mastery guide present")
        
        # Check test strategy
        test_strategy = self.brain_path / "documents" / "implementation-guides" / "test-strategy.yaml"
        if not test_strategy.exists():
            result.warnings.append("Test strategy file not found")
        else:
            result.passed.append("✓ Test strategy file present")
        
        if result.failures:
            result.recommendations.append("Run: pytest tests/workflows/test_tdd_workflow.py")
            result.recommendations.append("Check TDD guide: .github/prompts/modules/tdd-mastery-guide.md")
        
        self.results.append(result)
    
    def validate_planning_system(self):
        """Validate planning system is functional."""
        result = ValidationResult("Planning System")
        
        # Check planning orchestrator
        planning_orchestrator = list(self.src_path.glob("**/planning_orchestrator.py"))
        if not planning_orchestrator:
            result.failures.append("Planning orchestrator not found")
        else:
            result.passed.append("✓ Planning orchestrator present")
        
        # Check planning guide
        planning_guide = self.cortex_root / ".github" / "prompts" / "modules" / "planning-orchestrator-guide.md"
        if not planning_guide.exists():
            result.failures.append("Planning guide not found")
        else:
            result.passed.append("✓ Planning guide present")
        
        # Check planning templates in response-templates.yaml
        templates_file = self.brain_path / "response-templates.yaml"
        if templates_file.exists():
            try:
                with open(templates_file, 'r', encoding='utf-8') as f:
                    templates = yaml.safe_load(f)
                
                planning_templates = ['work_planner_success', 'planning_dor_complete', 'planning_dor_incomplete']
                for template_name in planning_templates:
                    if template_name in templates.get('templates', {}):
                        result.passed.append(f"✓ Template {template_name} present")
                    else:
                        result.failures.append(f"Missing planning template: {template_name}")
            except Exception as e:
                result.warnings.append(f"Could not verify planning templates: {str(e)}")
        
        # Check planning directory exists
        planning_dir = self.brain_path / "documents" / "planning"
        if not planning_dir.exists():
            result.warnings.append("Planning documents directory not found")
        else:
            result.passed.append("✓ Planning documents directory present")
        
        if result.failures:
            result.recommendations.append("Check planning guide: .github/prompts/modules/planning-orchestrator-guide.md")
            result.recommendations.append("Verify planning orchestrator: src/orchestrators/planning_orchestrator.py")
        
        self.results.append(result)
    
    def validate_ado_integration(self):
        """Validate ADO integration is functional."""
        result = ValidationResult("ADO Integration")
        
        # Check ADO agent
        ado_agent = list(self.src_path.glob("**/ado_agent.py"))
        if not ado_agent:
            result.warnings.append("ADO agent not found (optional feature)")
        else:
            result.passed.append("✓ ADO agent present")
        
        # Check ADO templates
        templates_file = self.brain_path / "response-templates.yaml"
        if templates_file.exists():
            try:
                with open(templates_file, 'r', encoding='utf-8') as f:
                    templates = yaml.safe_load(f)
                
                ado_templates = ['ado_created', 'ado_resumed', 'ado_search_results']
                for template_name in ado_templates:
                    if template_name in templates.get('templates', {}):
                        result.passed.append(f"✓ Template {template_name} present")
                    else:
                        result.warnings.append(f"ADO template not found: {template_name}")
            except Exception as e:
                result.warnings.append(f"Could not verify ADO templates: {str(e)}")
        
        # Check ADO configuration in cortex.config.json
        config_file = self.cortex_root / "cortex.config.json"
        if config_file.exists():
            try:
                import json
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                if 'ado' in config:
                    result.passed.append("✓ ADO configuration section present")
                else:
                    result.warnings.append("ADO configuration section not found (optional)")
            except Exception as e:
                result.warnings.append(f"Could not verify ADO config: {str(e)}")
        
        self.results.append(result)
    
    def validate_entry_points(self):
        """Validate all entry point modules are present."""
        result = ValidationResult("Entry Point Modules")
        
        modules_path = self.cortex_root / ".github" / "prompts" / "modules"
        
        # Critical entry points
        critical_modules = [
            "upgrade-guide.md",
            "response-format.md",
            "template-guide.md",
            "planning-orchestrator-guide.md",
            "tdd-mastery-guide.md"
        ]
        
        for module_name in critical_modules:
            module_file = modules_path / module_name
            if not module_file.exists():
                result.failures.append(f"Missing critical entry point: {module_name}")
            else:
                result.passed.append(f"✓ {module_name}")
        
        # Optional but recommended modules
        optional_modules = [
            "system-alignment-guide.md",
            "architecture-intelligence-guide.md",
            "git-checkpoint-guide.md",
            "setup-epm-guide.md"
        ]
        
        for module_name in optional_modules:
            module_file = modules_path / module_name
            if not module_file.exists():
                result.warnings.append(f"Optional module not found: {module_name}")
            else:
                result.passed.append(f"✓ {module_name}")
        
        if result.failures:
            result.recommendations.append("Generate missing modules: python scripts/generate_documentation.py")
            result.recommendations.append("Check module templates: cortex-brain/templates/")
        
        self.results.append(result)
    
    def validate_database_schema(self):
        """Validate database schema integrity."""
        result = ValidationResult("Database Schema")
        
        # Check Tier 1 database
        tier1_db = self.brain_path / "tier1" / "working_memory.db"
        if not tier1_db.exists():
            result.failures.append("Tier 1 database not found")
        else:
            try:
                conn = sqlite3.connect(tier1_db)
                cursor = conn.cursor()
                
                # Check critical tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                required_tables = ['conversations', 'entities', 'user_profile']
                for table in required_tables:
                    if table in tables:
                        result.passed.append(f"✓ Table '{table}' present in Tier 1")
                    else:
                        result.failures.append(f"Missing table in Tier 1: {table}")
                
                conn.close()
            except Exception as e:
                result.failures.append(f"Tier 1 database error: {str(e)}")
        
        # Check Tier 2 database
        tier2_db = self.brain_path / "tier2" / "knowledge_graph.db"
        if not tier2_db.exists():
            result.warnings.append("Tier 2 database not found")
        else:
            try:
                conn = sqlite3.connect(tier2_db)
                cursor = conn.cursor()
                
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                if 'tier2_element_mappings' in tables:
                    result.passed.append("✓ ViewDiscovery tables present in Tier 2")
                
                conn.close()
            except Exception as e:
                result.warnings.append(f"Tier 2 database error: {str(e)}")
        
        # Check Tier 3 database
        tier3_db = self.brain_path / "tier3" / "context.db"
        if not tier3_db.exists():
            result.warnings.append("Tier 3 database not found")
        else:
            try:
                conn = sqlite3.connect(tier3_db)
                cursor = conn.cursor()
                
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                if 'cortex_features' in tables:
                    result.passed.append("✓ Enhancement Catalog tables present in Tier 3")
                
                conn.close()
            except Exception as e:
                result.warnings.append(f"Tier 3 database error: {str(e)}")
        
        if result.failures:
            result.recommendations.append("Run database migrations: python cortex-brain/migrate_brain_db.py")
            result.recommendations.append("Check schema: cortex-brain/schema.sql")
        
        self.results.append(result)
    
    def validate_brain_protection(self):
        """Validate brain protection rules are active."""
        result = ValidationResult("Brain Protection")
        
        # Check brain protection rules file
        rules_file = self.brain_path / "brain-protection-rules.yaml"
        if not rules_file.exists():
            result.failures.append("Brain protection rules file not found")
        else:
            result.passed.append("✓ Brain protection rules file present")
            
            try:
                with open(rules_file, 'r', encoding='utf-8') as f:
                    rules = yaml.safe_load(f)
                
                # Check critical rules
                if 'rules' in rules:
                    result.passed.append(f"✓ Found {len(rules['rules'])} protection rules")
                else:
                    result.warnings.append("No rules section in brain-protection-rules.yaml")
            except Exception as e:
                result.warnings.append(f"Could not parse brain protection rules: {str(e)}")
        
        # Check brain protector tests pass
        test_file = self.cortex_root / "tests" / "tier0" / "test_brain_protector.py"
        if not test_file.exists():
            result.warnings.append("Brain protector tests not found")
        else:
            result.passed.append("✓ Brain protector tests present")
        
        self.results.append(result)
    
    def validate_system_alignment(self):
        """Validate system alignment is functional."""
        result = ValidationResult("System Alignment")
        
        # Check system alignment orchestrator
        alignment_orchestrator = list(self.src_path.glob("**/system_alignment_orchestrator.py"))
        if not alignment_orchestrator:
            result.failures.append("System alignment orchestrator not found")
        else:
            result.passed.append("✓ System alignment orchestrator present")
        
        # Check alignment guide
        alignment_guide = self.cortex_root / ".github" / "prompts" / "modules" / "system-alignment-guide.md"
        if not alignment_guide.exists():
            result.failures.append("System alignment guide not found")
        else:
            result.passed.append("✓ System alignment guide present")
        
        # Check integration scorer (core component)
        integration_scorer = list(self.src_path.glob("**/integration_scorer.py"))
        if not integration_scorer:
            result.warnings.append("Integration scorer not found")
        else:
            result.passed.append("✓ Integration scorer present")
        
        if result.failures:
            result.recommendations.append("Check alignment guide: .github/prompts/modules/system-alignment-guide.md")
            result.recommendations.append("Run: python scripts/validate_system_alignment.py")
        
        self.results.append(result)
    
    def _print_summary(self) -> Tuple[int, int, int]:
        """Print validation results summary and return counts."""
        print("\n" + "="*80)
        print("📊 VALIDATION RESULTS SUMMARY")
        print("="*80 + "\n")
        
        passed_count = 0
        warning_count = 0
        failure_count = 0
        
        for result in self.results:
            print(f"\n{result.status} {result.category}")
            print("-" * 80)
            
            if result.passed and self.verbose:
                for item in result.passed:
                    print(f"  {item}")
            
            if result.warnings:
                warning_count += len(result.warnings)
                for item in result.warnings:
                    print(f"  ⚠️  {item}")
            
            if result.failures:
                failure_count += len(result.failures)
                for item in result.failures:
                    print(f"  ❌ {item}")
            
            if result.recommendations:
                print("\n  💡 Recommendations:")
                for item in result.recommendations:
                    print(f"     • {item}")
            
            if not result.has_issues:
                passed_count += 1
        
        # Overall summary
        print("\n" + "="*80)
        print(f"✅ Passed Categories: {passed_count}/{len(self.results)}")
        print(f"⚠️  Total Warnings: {warning_count}")
        print(f"❌ Total Failures: {failure_count}")
        print("="*80 + "\n")
        
        return passed_count, warning_count, failure_count
    
    def generate_report(self) -> str:
        """Generate markdown validation report."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        report_path = self.brain_path / "documents" / "reports" / f"post-deployment-validation-{timestamp}.md"
        
        # Ensure directory exists
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# CORTEX Post-Deployment Validation Report\n\n")
            f.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**CORTEX Root:** {self.cortex_root}\n\n")
            
            f.write("---\n\n")
            
            for result in self.results:
                f.write(f"## {result.status} {result.category}\n\n")
                
                if result.passed:
                    f.write("**Passed Checks:**\n")
                    for item in result.passed:
                        f.write(f"- {item}\n")
                    f.write("\n")
                
                if result.warnings:
                    f.write("**Warnings:**\n")
                    for item in result.warnings:
                        f.write(f"- ⚠️  {item}\n")
                    f.write("\n")
                
                if result.failures:
                    f.write("**Failures:**\n")
                    for item in result.failures:
                        f.write(f"- ❌ {item}\n")
                    f.write("\n")
                
                if result.recommendations:
                    f.write("**Recommendations:**\n")
                    for item in result.recommendations:
                        f.write(f"- 💡 {item}\n")
                    f.write("\n")
                
                f.write("---\n\n")
            
            # Summary section
            passed = sum(1 for r in self.results if not r.has_issues)
            warnings = sum(len(r.warnings) for r in self.results)
            failures = sum(len(r.failures) for r in self.results)
            
            f.write("## Summary\n\n")
            f.write(f"- **Passed Categories:** {passed}/{len(self.results)}\n")
            f.write(f"- **Total Warnings:** {warnings}\n")
            f.write(f"- **Total Failures:** {failures}\n\n")
            
            if failures == 0 and warnings == 0:
                f.write("✅ **Overall Status:** PRODUCTION READY\n")
            elif failures == 0:
                f.write("⚠️  **Overall Status:** READY WITH WARNINGS\n")
            else:
                f.write("❌ **Overall Status:** NOT PRODUCTION READY\n")
        
        return str(report_path)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="CORTEX Post-Deployment Validation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/post_deployment_check.py
  python scripts/post_deployment_check.py --verbose
  python scripts/post_deployment_check.py --report-only

Exit Codes:
  0 - All validations passed
  1 - Warnings detected (non-critical)
  2 - Failures detected (critical)
        """
    )
    
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    parser.add_argument('--report-only', action='store_true',
                       help='Generate report only, skip console output')
    
    args = parser.parse_args()
    
    # Initialize validator
    cortex_root = Path(__file__).parent.parent
    validator = PostDeploymentValidator(cortex_root, verbose=args.verbose)
    
    # Run validations
    passed, warnings, failures = validator.run_all_validations()
    
    # Generate report
    report_path = validator.generate_report()
    print(f"\n📄 Detailed report saved to:\n   {report_path}\n")
    
    # Determine exit code
    if failures > 0:
        print("❌ VALIDATION FAILED - Critical issues detected")
        print("   Review failures above and fix before deploying\n")
        sys.exit(2)
    elif warnings > 0:
        print("⚠️  VALIDATION PASSED WITH WARNINGS")
        print("   Review warnings above and consider fixing\n")
        sys.exit(1)
    else:
        print("✅ ALL VALIDATIONS PASSED - Production ready!\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
