"""
CORTEX Documentation Structure Test Harness
Validates that all expected documentation files and folders exist after generation.

NOTE: This test validates COMMITTED documentation structure, not GENERATED content.
Generated content (docs/diagrams/*) is created by enterprise_documentation_orchestrator
and is tested separately in test_enterprise_documentation_orchestrator.py.
"""
import os
from pathlib import Path
import pytest
from typing import Dict, List, Tuple


class DocumentationStructureValidator:
    """Validates CORTEX documentation folder structure against expected configuration."""
    
    def __init__(self, workspace_root: Path, skip_generated: bool = True):
        self.workspace_root = workspace_root
        self.docs_root = workspace_root / "docs"
        self.skip_generated = skip_generated
        self.validation_results = {
            "directories": {"expected": [], "found": [], "missing": [], "skipped": []},
            "files": {"expected": [], "found": [], "missing": [], "skipped": []},
            "categories": {}
        }
    
    def validate_structure(self) -> Dict:
        """Run complete structure validation."""
        print("\n" + "="*80)
        print("🧠 CORTEX Documentation Structure Validation")
        print("="*80 + "\n")
        
        # Validate directories
        self._validate_directories()
        
        # Validate files by category
        self._validate_files_by_category()
        
        # Generate report
        self._generate_report()
        
        return self.validation_results
    
    def _validate_directories(self):
        """Validate expected directory structure."""
        print("📁 Validating Directory Structure...")
        print("-" * 80)
        
        # Core directories (committed, should always exist)
        core_dirs = [
            "docs",
            "docs/getting-started",
            "docs/architecture",
            "docs/operations",
            "docs/plugins",
            "docs/reference",
            "docs/guides",
            "docs/images",
        ]
        
        # Generated directories (created by orchestrator, may not exist)
        generated_dirs = [
            "docs/diagrams",
            "docs/diagrams/prompts",
            "docs/diagrams/narratives",
            "docs/diagrams/generated",
            "docs/diagrams/story",
            "docs/images/diagrams",
            "docs/images/diagrams/strategic",
            "docs/images/diagrams/architectural",
            "docs/images/diagrams/operational",
            "docs/images/diagrams/integration"
        ]
        
        # Combine for full expected list
        expected_dirs = core_dirs + ([] if self.skip_generated else generated_dirs)
        self.validation_results["directories"]["expected"] = expected_dirs
        
        for dir_path in expected_dirs:
            full_path = self.workspace_root / dir_path
            exists = full_path.exists() and full_path.is_dir()
            
            if exists:
                self.validation_results["directories"]["found"].append(dir_path)
                print(f"  ✅ {dir_path}")
            else:
                self.validation_results["directories"]["missing"].append(dir_path)
                print(f"  ❌ {dir_path} (MISSING)")
        
        # Track skipped directories
        if self.skip_generated:
            self.validation_results["directories"]["skipped"] = generated_dirs
            print(f"\n  ℹ️ Skipped {len(generated_dirs)} generated directories (tested separately)")
        
        print()
    
    def _validate_files_by_category(self):
        """Validate files by documentation category."""
        categories = {
            "Getting Started": [
                "docs/getting-started/quick-start.md",
                "docs/getting-started/installation.md",
                "docs/getting-started/configuration.md"
            ],
            "Architecture": [
                "docs/architecture/overview.md",
                "docs/architecture/tier-system.md",
                "docs/architecture/agents.md",
                "docs/architecture/brain-protection.md"
            ],
            "Operations": [
                "docs/operations/overview.md",
                "docs/operations/entry-point-modules.md",
                "docs/operations/workflows.md",
                "docs/operations/health-monitoring.md"
            ],
            "Plugins": [
                "docs/plugins/vscode-extension.md",
                "docs/plugins/development.md"
            ],
            "Reference": [
                "docs/reference/api.md",
                "docs/reference/configuration.md",
                "docs/reference/response-templates.md"
            ],
            "Guides": [
                "docs/guides/admin-guide.md",
                "docs/guides/developer-guide.md",
                "docs/guides/troubleshooting.md",
                "docs/guides/best-practices.md"
            ],
            "Mermaid Diagrams": [
                "docs/images/diagrams/strategic/tier-architecture.md",
                "docs/images/diagrams/strategic/agent-coordination.md",
                "docs/images/diagrams/strategic/information-flow.md",
                "docs/images/diagrams/architectural/epm-doc-generator-pipeline.md",
                "docs/images/diagrams/architectural/module-structure.md",
                "docs/images/diagrams/architectural/brain-protection.md",
                "docs/images/diagrams/operational/conversation-flow.md",
                "docs/images/diagrams/operational/knowledge-graph-update.md",
                "docs/images/diagrams/operational/health-check.md",
                "docs/images/diagrams/integration/vscode-integration.md",
                "docs/images/diagrams/integration/git-integration.md",
                "docs/images/diagrams/integration/mkdocs-integration.md"
            ],
        }
        
        # Generated content categories (skipped if skip_generated=True)
        generated_categories = {
            "Image Prompts (Generated)": [
                "docs/diagrams/prompts/01-tier-architecture.md",
                "docs/diagrams/prompts/02-agent-system.md",
                "docs/diagrams/prompts/03-plugin-architecture.md",
                "docs/diagrams/prompts/04-memory-flow.md",
                "docs/diagrams/prompts/05-agent-coordination.md",
                "docs/diagrams/prompts/06-basement-scene.md",
                "docs/diagrams/prompts/07-cortex-one-pager.md"
            ],
            "Narratives (Generated)": [
                "docs/diagrams/narratives/01-tier-architecture.md",
                "docs/diagrams/narratives/02-agent-system.md",
                "docs/diagrams/narratives/03-plugin-architecture.md",
                "docs/diagrams/narratives/04-memory-flow.md",
                "docs/diagrams/narratives/05-agent-coordination.md",
                "docs/diagrams/narratives/06-basement-scene.md",
                "docs/diagrams/narratives/07-cortex-one-pager.md"
            ],
            "Story (Generated)": [
                "docs/diagrams/story/The CORTEX Story.md"
            ]
        }
        
        # Add generated categories if not skipping
        if not self.skip_generated:
            categories.update(generated_categories)
        
        print("📄 Validating Documentation Files by Category...")
        print("-" * 80)
        
        for category, files in categories.items():
            print(f"\n{category}:")
            category_results = {"expected": len(files), "found": 0, "missing": []}
            
            for file_path in files:
                full_path = self.workspace_root / file_path
                exists = full_path.exists() and full_path.is_file()
                
                self.validation_results["files"]["expected"].append(file_path)
                
                if exists:
                    self.validation_results["files"]["found"].append(file_path)
                    category_results["found"] += 1
                    
                    # Get file size
                    size_kb = full_path.stat().st_size / 1024
                    print(f"  ✅ {Path(file_path).name} ({size_kb:.2f} KB)")
                else:
                    self.validation_results["files"]["missing"].append(file_path)
                    category_results["missing"].append(file_path)
                    print(f"  ❌ {Path(file_path).name} (MISSING)")
            
            self.validation_results["categories"][category] = category_results
            
            # Category summary
            completion = (category_results["found"] / category_results["expected"]) * 100
            print(f"  📊 {category} Completion: {category_results['found']}/{category_results['expected']} ({completion:.1f}%)")
        
        # Track skipped categories
        if self.skip_generated:
            skipped_files = []
            for files in generated_categories.values():
                skipped_files.extend(files)
            self.validation_results["files"]["skipped"] = skipped_files
            print(f"\n  ℹ️ Skipped {len(skipped_files)} generated files (tested separately)")
        
        print()
    
    def _generate_report(self):
        """Generate comprehensive validation report."""
        print("\n" + "="*80)
        print("📊 VALIDATION SUMMARY")
        print("="*80 + "\n")
        
        # Directory summary
        dir_total = len(self.validation_results["directories"]["expected"])
        dir_found = len(self.validation_results["directories"]["found"])
        dir_missing = len(self.validation_results["directories"]["missing"])
        dir_completion = (dir_found / dir_total) * 100 if dir_total > 0 else 0
        
        print(f"Directories:")
        print(f"  Expected: {dir_total}")
        print(f"  Found: {dir_found}")
        print(f"  Missing: {dir_missing}")
        print(f"  Completion: {dir_completion:.1f}%")
        print()
        
        # File summary
        file_total = len(self.validation_results["files"]["expected"])
        file_found = len(self.validation_results["files"]["found"])
        file_missing = len(self.validation_results["files"]["missing"])
        file_completion = (file_found / file_total) * 100 if file_total > 0 else 0
        
        print(f"Files:")
        print(f"  Expected: {file_total}")
        print(f"  Found: {file_found}")
        print(f"  Missing: {file_missing}")
        print(f"  Completion: {file_completion:.1f}%")
        print()
        
        # Category breakdown
        print("Category Breakdown:")
        for category, results in self.validation_results["categories"].items():
            completion = (results["found"] / results["expected"]) * 100
            status = "✅" if completion == 100 else "⚠️" if completion >= 80 else "❌"
            print(f"  {status} {category}: {results['found']}/{results['expected']} ({completion:.1f}%)")
        print()
        
        # Overall status
        overall_completion = ((dir_found + file_found) / (dir_total + file_total)) * 100
        print(f"Overall Completion: {overall_completion:.1f}%")
        
        if overall_completion == 100:
            print("\n✅ All expected documentation files and folders exist!")
        elif overall_completion >= 90:
            print("\n⚠️ Documentation structure is mostly complete (minor gaps)")
        elif overall_completion >= 75:
            print("\n⚠️ Documentation structure has some missing components")
        else:
            print("\n❌ Documentation structure is incomplete")
        
        # List missing items if any
        if dir_missing > 0:
            print("\n❌ Missing Directories:")
            for dir_path in self.validation_results["directories"]["missing"]:
                print(f"  - {dir_path}")
        
        if file_missing > 0:
            print("\n❌ Missing Files:")
            for file_path in self.validation_results["files"]["missing"]:
                print(f"  - {file_path}")
        
        print("\n" + "="*80)


def test_documentation_structure():
    """PyTest test function to validate documentation structure."""
    workspace_root = Path("d:/PROJECTS/CORTEX")
    # Skip generated content by default (tested in test_enterprise_documentation_orchestrator.py)
    validator = DocumentationStructureValidator(workspace_root, skip_generated=True)
    results = validator.validate_structure()
    
    # Assert all expected (non-generated) directories exist
    assert len(results["directories"]["missing"]) == 0, \
        f"Missing directories: {results['directories']['missing']}"
    
    # Assert all expected (non-generated) files exist
    assert len(results["files"]["missing"]) == 0, \
        f"Missing files: {results['files']['missing']}"
    
    # Assert all categories are 100% complete
    for category, category_results in results["categories"].items():
        completion = (category_results["found"] / category_results["expected"]) * 100
        assert completion == 100, \
            f"{category} incomplete: {category_results['found']}/{category_results['expected']} ({completion:.1f}%)"


if __name__ == "__main__":
    """Run test harness directly."""
    workspace_root = Path("d:/PROJECTS/CORTEX")
    # By default, skip generated content when running standalone
    import sys
    skip_generated = "--include-generated" not in sys.argv
    
    validator = DocumentationStructureValidator(workspace_root, skip_generated=skip_generated)
    results = validator.validate_structure()
    
    # Exit with appropriate code
    dir_complete = len(results["directories"]["missing"]) == 0
    file_complete = len(results["files"]["missing"]) == 0
    
    if dir_complete and file_complete:
        exit(0)  # Success
    else:
        exit(1)  # Failure
