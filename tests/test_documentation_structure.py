"""
CORTEX Documentation Structure Test Harness
Validates that all expected documentation files and folders exist after generation.
"""
import os
from pathlib import Path
import pytest
from typing import Dict, List, Tuple


class DocumentationStructureValidator:
    """Validates CORTEX documentation folder structure against expected configuration."""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.docs_root = workspace_root / "docs"
        self.validation_results = {
            "directories": {"expected": [], "found": [], "missing": []},
            "files": {"expected": [], "found": [], "missing": []},
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
        
        expected_dirs = [
            "docs",
            "docs/getting-started",
            "docs/architecture",
            "docs/operations",
            "docs/plugins",
            "docs/reference",
            "docs/guides",
            "docs/diagrams",
            "docs/diagrams/prompts",
            "docs/diagrams/narratives",
            "docs/diagrams/generated",
            "docs/diagrams/story",
            "docs/images",
            "docs/images/diagrams",
            "docs/images/diagrams/strategic",
            "docs/images/diagrams/architectural",
            "docs/images/diagrams/operational",
            "docs/images/diagrams/integration"
        ]
        
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
            "Image Prompts": [
                "docs/diagrams/prompts/01-tier-architecture.md",
                "docs/diagrams/prompts/02-agent-system.md",
                "docs/diagrams/prompts/03-plugin-architecture.md",
                "docs/diagrams/prompts/04-memory-flow.md",
                "docs/diagrams/prompts/05-agent-coordination.md",
                "docs/diagrams/prompts/06-basement-scene.md",
                "docs/diagrams/prompts/07-cortex-one-pager.md"
            ],
            "Narratives": [
                "docs/diagrams/narratives/01-tier-architecture.md",
                "docs/diagrams/narratives/02-agent-system.md",
                "docs/diagrams/narratives/03-plugin-architecture.md",
                "docs/diagrams/narratives/04-memory-flow.md",
                "docs/diagrams/narratives/05-agent-coordination.md",
                "docs/diagrams/narratives/06-basement-scene.md",
                "docs/diagrams/narratives/07-cortex-one-pager.md"
            ],
            "Story": [
                "docs/diagrams/story/The CORTEX Story.md"
            ]
        }
        
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
    validator = DocumentationStructureValidator(workspace_root)
    results = validator.validate_structure()
    
    # Assert all directories exist
    assert len(results["directories"]["missing"]) == 0, \
        f"Missing directories: {results['directories']['missing']}"
    
    # Assert all files exist
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
    validator = DocumentationStructureValidator(workspace_root)
    results = validator.validate_structure()
    
    # Exit with appropriate code
    dir_complete = len(results["directories"]["missing"]) == 0
    file_complete = len(results["files"]["missing"]) == 0
    
    if dir_complete and file_complete:
        exit(0)  # Success
    else:
        exit(1)  # Failure
