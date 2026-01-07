#!/usr/bin/env python3
"""
CORTEX Template Validator - Validate and fix response templates

Validates:
1. All orchestrators reference correct progress templates
2. Visual progress bar components exist in base-components.yaml
3. Autonomous execution defaults are set correctly
4. No references to deprecated 5-part templates

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse
import yaml


# Expected template mappings
EXPECTED_TEMPLATES = {
    "planning_orchestrator.py": {
        "template": "autonomous_execution_progress",
        "key": "response_template"
    },
    "ado_orchestrator.py": {
        "template": "ado_execution_progress", 
        "key": "response_template"
    },
    "maintenance": {
        "template": "maintenance_execution_progress",
        "key": "response_template"
    },
    "sanitization": {
        "template": "sanitization_execution_progress",
        "key": "response_template"
    },
    "refinement": {
        "template": "refinement_execution_progress",
        "key": "response_template"
    }
}

# Autonomous execution checks
AUTONOMOUS_CHECKS = [
    {
        "file_pattern": "**/planning_orchestrator.py",
        "search": r'kwargs\.get\(["\']auto_execute["\'],\s*(True|False)\)',
        "expected": "True"
    },
    {
        "file_pattern": "**/planning_orchestrator.py", 
        "search": r'config\.get\(["\']enable_autonomous_execution["\'],\s*(True|False)\)',
        "expected": "True"
    },
    {
        "file_pattern": "**/ado_orchestrator.py",
        "search": r'["\']autonomous_execution["\']:\s*(True|False)',
        "expected": "True"
    }
]

# Deprecated patterns to find
DEPRECATED_PATTERNS = [
    r"5-part-standard",
    r"five-part-standard",
    r"5_part_standard",
    r"inherits_from:\s*core/base-templates/5-part",
]


class ValidationResult:
    """Container for validation results."""
    
    def __init__(self):
        self.template_issues: List[Dict] = []
        self.autonomous_issues: List[Dict] = []
        self.deprecated_issues: List[Dict] = []
        self.missing_components: List[str] = []
    
    @property
    def has_issues(self) -> bool:
        return bool(
            self.template_issues or 
            self.autonomous_issues or 
            self.deprecated_issues or
            self.missing_components
        )
    
    @property
    def total_issues(self) -> int:
        return (
            len(self.template_issues) + 
            len(self.autonomous_issues) + 
            len(self.deprecated_issues) +
            len(self.missing_components)
        )


def find_files(workspace: Path, pattern: str) -> List[Path]:
    """Find files matching glob pattern."""
    if pattern.startswith("**/"):
        return list(workspace.rglob(pattern[3:]))
    return list(workspace.glob(pattern))


def check_template_references(workspace: Path) -> List[Dict]:
    """Check that orchestrators reference correct templates."""
    issues = []
    
    # Check Python orchestrator files
    for name, config in EXPECTED_TEMPLATES.items():
        if name.endswith(".py"):
            files = find_files(workspace / "src", f"**/{name}")
            for file in files:
                content = file.read_text()
                
                # Look for response_template assignment
                pattern = rf'["\']response_template["\']\s*:\s*["\']([^"\']+)["\']'
                matches = re.findall(pattern, content)
                
                if not matches:
                    issues.append({
                        "file": str(file),
                        "type": "missing_template",
                        "expected": config["template"],
                        "found": None
                    })
                elif config["template"] not in matches:
                    issues.append({
                        "file": str(file),
                        "type": "wrong_template",
                        "expected": config["template"],
                        "found": matches
                    })
    
    return issues


def check_autonomous_defaults(workspace: Path) -> List[Dict]:
    """Check that autonomous execution defaults to True."""
    issues = []
    
    for check in AUTONOMOUS_CHECKS:
        files = find_files(workspace, check["file_pattern"])
        
        for file in files:
            content = file.read_text()
            matches = re.findall(check["search"], content)
            
            for match in matches:
                if match != check["expected"]:
                    issues.append({
                        "file": str(file),
                        "pattern": check["search"],
                        "expected": check["expected"],
                        "found": match
                    })
    
    return issues


def check_deprecated_references(workspace: Path) -> List[Dict]:
    """Find deprecated 5-part template references."""
    issues = []
    
    # Search in cortex-brain and .github
    search_dirs = [
        workspace / "cortex-brain",
        workspace / ".github",
        workspace / "src",
    ]
    
    extensions = [".yaml", ".yml", ".md", ".py"]
    
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
            
        for ext in extensions:
            for file in search_dir.rglob(f"*{ext}"):
                try:
                    content = file.read_text()
                    
                    for pattern in DEPRECATED_PATTERNS:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            # Skip if it's in a planning doc that documents the cleanup
                            if "user-response-template-cleanup" in str(file):
                                continue
                            if "cortex-cleanup.prompt.md" in str(file):
                                continue
                                
                            issues.append({
                                "file": str(file),
                                "pattern": pattern,
                                "matches": matches
                            })
                except Exception:
                    pass
    
    return issues


def check_base_components(workspace: Path) -> List[str]:
    """Check that required progress templates exist in base-components.yaml."""
    missing = []
    
    base_components = workspace / "cortex-brain" / "response-templates" / "base-components.yaml"
    
    if not base_components.exists():
        return ["base-components.yaml not found"]
    
    try:
        content = base_components.read_text()
        
        required_templates = [
            "autonomous_execution_progress",
            "ado_execution_progress",
            "maintenance_execution_progress",
            "sanitization_execution_progress",
            "refinement_execution_progress",
            "progress_bar",
            "phase_row_template",
        ]
        
        for template in required_templates:
            if template not in content:
                missing.append(template)
                
    except Exception as e:
        missing.append(f"Error reading base-components.yaml: {e}")
    
    return missing


def validate_templates(workspace: Path) -> ValidationResult:
    """Run all validation checks."""
    result = ValidationResult()
    
    print(f"\n{'=' * 60}")
    print("🔍 CORTEX Template Validator")
    print(f"{'=' * 60}")
    print(f"\n📂 Workspace: {workspace}")
    
    # Check 1: Template references
    print("\n📋 Checking template references...")
    result.template_issues = check_template_references(workspace)
    print(f"   Found {len(result.template_issues)} issue(s)")
    
    # Check 2: Autonomous defaults
    print("\n⚡ Checking autonomous execution defaults...")
    result.autonomous_issues = check_autonomous_defaults(workspace)
    print(f"   Found {len(result.autonomous_issues)} issue(s)")
    
    # Check 3: Deprecated references
    print("\n🗑️  Checking for deprecated 5-part references...")
    result.deprecated_issues = check_deprecated_references(workspace)
    print(f"   Found {len(result.deprecated_issues)} issue(s)")
    
    # Check 4: Base components
    print("\n📦 Checking base component templates...")
    result.missing_components = check_base_components(workspace)
    print(f"   Found {len(result.missing_components)} missing component(s)")
    
    return result


def print_results(result: ValidationResult):
    """Print detailed validation results."""
    print(f"\n{'=' * 60}")
    print("📊 Validation Results")
    print(f"{'=' * 60}")
    
    if not result.has_issues:
        print("\n✅ All validations passed!")
        return
    
    print(f"\n⚠️  Total issues found: {result.total_issues}")
    
    if result.template_issues:
        print("\n### Template Reference Issues")
        for issue in result.template_issues:
            print(f"\n   📄 {issue['file']}")
            print(f"      Type: {issue['type']}")
            print(f"      Expected: {issue['expected']}")
            print(f"      Found: {issue['found']}")
    
    if result.autonomous_issues:
        print("\n### Autonomous Execution Issues")
        for issue in result.autonomous_issues:
            print(f"\n   📄 {issue['file']}")
            print(f"      Expected: {issue['expected']}")
            print(f"      Found: {issue['found']}")
    
    if result.deprecated_issues:
        print("\n### Deprecated Reference Issues")
        for issue in result.deprecated_issues:
            print(f"\n   📄 {issue['file']}")
            print(f"      Pattern: {issue['pattern']}")
            print(f"      Matches: {issue['matches']}")
    
    if result.missing_components:
        print("\n### Missing Base Components")
        for comp in result.missing_components:
            print(f"   ❌ {comp}")


def fix_autonomous_defaults(workspace: Path, issues: List[Dict], dry_run: bool = True) -> int:
    """Fix autonomous execution defaults."""
    fixed = 0
    
    for issue in issues:
        file_path = Path(issue['file'])
        if not file_path.exists():
            continue
        
        content = file_path.read_text()
        
        # Replace False with True in the specific pattern
        old_pattern = issue['pattern'].replace(r'(True|False)', issue['found'])
        new_pattern = issue['pattern'].replace(r'(True|False)', issue['expected'])
        
        # Simple string replacement
        old_str = content
        new_str = re.sub(
            issue['pattern'].replace(r'(True|False)', issue['found']),
            issue['pattern'].replace(r'(True|False)', issue['expected']).replace('\\', ''),
            content
        )
        
        if old_str != new_str:
            if not dry_run:
                file_path.write_text(new_str)
            fixed += 1
            print(f"   {'Would fix' if dry_run else 'Fixed'}: {file_path}")
    
    return fixed


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="CORTEX Template Validator - Validate and fix response templates"
    )
    parser.add_argument(
        "--workspace",
        type=str,
        default=".",
        help="Workspace root directory (default: current)"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to fix issues automatically"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be fixed without making changes"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    workspace = Path(args.workspace).resolve()
    
    if not workspace.exists():
        print(f"❌ Workspace not found: {workspace}")
        sys.exit(1)
    
    result = validate_templates(workspace)
    print_results(result)
    
    if args.fix and result.autonomous_issues:
        print(f"\n{'=' * 60}")
        print("🔧 Fixing Autonomous Execution Defaults")
        print(f"{'=' * 60}")
        fixed = fix_autonomous_defaults(
            workspace, 
            result.autonomous_issues,
            dry_run=args.dry_run
        )
        print(f"\n{'Would fix' if args.dry_run else 'Fixed'}: {fixed} issue(s)")
    
    print(f"\n{'=' * 60}\n")
    
    sys.exit(0 if not result.has_issues else 1)


if __name__ == "__main__":
    main()
