#!/usr/bin/env python3
"""
Governance Alignment Validator

Validates that CORE-002 is consistently defined across all 6 layers:
1. Copilot Instructions (.github/copilot-instructions.md)
2. Prompt Files (.github/prompts/cortex-architect.prompt.md)
3. Registry YAML (cortex-registry/_cortex-master/governance/core-rules.yaml)
4. Enforcement Code (cortex/orchestrators/core/enforcement_orchestrator.py)
5. Test Expectations (tests/)
6. MCP Tools (cortex/mcp/tools/governance/)

Authority: Phase 2 - GAP-002 Resolution
Author: Asif Hussain
Date: 2026-02-10
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
import yaml


class AlignmentValidator:
    """Validates governance alignment across all system layers."""
    
    def __init__(self, repo_root: Path):
        """Initialize validator with repository root."""
        self.repo_root = repo_root
        self.violations: List[str] = []
        self.warnings: List[str] = []
        
    def validate_core_002(self) -> bool:
        """
        Validate CORE-002 alignment across all 6 layers.
        
        Returns:
            True if aligned, False if misalignments detected
        """
        print("🔍 Validating CORE-002 Alignment Across 6 Layers...\n")
        
        # Layer 1: Copilot Instructions
        layer1_paths = self._extract_allowed_paths_layer1()
        print(f"✅ Layer 1 (Copilot Instructions): {layer1_paths}")
        
        # Layer 2: Prompt Files
        layer2_paths = self._extract_allowed_paths_layer2()
        print(f"✅ Layer 2 (Prompt Files): {layer2_paths}")
        
        # Layer 3: Registry YAML
        layer3_paths = self._extract_allowed_paths_layer3()
        print(f"✅ Layer 3 (Registry YAML): {layer3_paths}")
        
        # Layer 4: Enforcement Code
        layer4_paths = self._extract_allowed_paths_layer4()
        print(f"✅ Layer 4 (Enforcement Code): {layer4_paths}")
        
        # Layer 5: Test Expectations
        layer5_behavior = self._validate_test_expectations()
        print(f"✅ Layer 5 (Test Expectations): {layer5_behavior}")
        
        # Layer 6: MCP Tools
        layer6_behavior = self._validate_mcp_tools()
        print(f"✅ Layer 6 (MCP Tools): {layer6_behavior}")
        
        # Compare all layers
        print("\n" + "=" * 80)
        print("ALIGNMENT ANALYSIS")
        print("=" * 80)
        
        all_paths = [layer1_paths, layer2_paths, layer3_paths, layer4_paths]
        
        # Check if all layers agree on allowed paths
        if all(paths == layer1_paths for paths in all_paths):
            print("✅ ALL LAYERS ALIGNED: Allowed paths consistent")
            print(f"   Canonical Paths: {sorted(layer1_paths)}")
        else:
            print("❌ MISALIGNMENT DETECTED:")
            for i, paths in enumerate(all_paths, 1):
                if paths != layer1_paths:
                    diff = paths.symmetric_difference(layer1_paths)
                    print(f"   Layer {i} differs: {diff}")
                    self.violations.append(f"Layer {i} path mismatch: {diff}")
        
        # Report violations and warnings
        if self.violations:
            print("\n❌ VIOLATIONS DETECTED:")
            for v in self.violations:
                print(f"   - {v}")
            return False
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for w in self.warnings:
                print(f"   - {w}")
        
        print("\n✅ CORE-002 ALIGNMENT: VALID")
        return True
    
    def _extract_allowed_paths_layer1(self) -> Set[str]:
        """Extract allowed paths from copilot-instructions.md."""
        file_path = self.repo_root / ".github" / "copilot-instructions.md"
        content = file_path.read_text()
        
        # Look for CORE-002 in table format with Exception clause
        # Pattern: **Exception:** ONLY these paths allowed: `.github/prompts/*.md` (prompt files), `.github/agents/*.md` (agent specs), `README.md` (root only)
        if "`.github/prompts/*.md`" in content and "`.github/agents/*.md`" in content and "`README.md` (root only)" in content:
            # Verify these are all in CORE-002 context
            core_002_match = re.search(
                r'\*\*CORE-002\*\*.*?Exception:.*?\.github/prompts/.*?\.github/agents/.*?README\.md',
                content,
                re.DOTALL
            )
            if core_002_match:
                return {".github/prompts/", ".github/agents/", "README.md"}
        
        self.violations.append("Layer 1: Could not parse CORE-002 exception")
        return set()
    
    def _extract_allowed_paths_layer2(self) -> Set[str]:
        """Extract allowed paths from cortex-architect.prompt.md."""
        file_path = self.repo_root / ".github" / "prompts" / "cortex-architect.prompt.md"
        content = file_path.read_text()
        
        # Look for CORE-002 ENFORCEMENT section
        match = re.search(
            r'allowed_md_paths\s*=\s*\[.*?'
            r'\.github/prompts/.*?'
            r'\.github/agents/.*?'
            r'README\.md',
            content,
            re.DOTALL
        )
        
        if match:
            return {".github/prompts/", ".github/agents/", "README.md"}
        else:
            # Also check for explicit exception list
            if "`.github/prompts/*.md`" in content and "`.github/agents/*.md`" in content:
                return {".github/prompts/", ".github/agents/", "README.md"}
            else:
                self.violations.append("Layer 2: Could not parse CORE-002 exception")
                return set()
    
    def _extract_allowed_paths_layer3(self) -> Set[str]:
        """Extract allowed paths from core-rules.yaml."""
        file_path = self.repo_root / "cortex-registry" / "_cortex-master" / "governance" / "core-rules.yaml"
        
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Find CORE-002 rule
        core_002 = next((r for r in data.get('core_rules', []) if r['id'] == 'CORE-002'), None)
        
        if not core_002:
            self.violations.append("Layer 3: CORE-002 rule not found in registry")
            return set()
        
        description = core_002.get('description', '')
        
        if ".github/prompts/" in description and ".github/agents/" in description and "README.md" in description:
            return {".github/prompts/", ".github/agents/", "README.md"}
        else:
            self.violations.append("Layer 3: CORE-002 exception incomplete")
            return set()
    
    def _extract_allowed_paths_layer4(self) -> Set[str]:
        """Extract allowed paths from enforcement_orchestrator.py."""
        file_path = self.repo_root / "cortex" / "orchestrators" / "core" / "enforcement_orchestrator.py"
        content = file_path.read_text()
        
        # Look for allowed_md_paths definition
        match = re.search(
            r'allowed_md_paths\s*=\s*\[(.*?)\]',
            content,
            re.DOTALL
        )
        
        if not match:
            self.violations.append("Layer 4: allowed_md_paths not found")
            return set()
        
        paths_str = match.group(1)
        
        # Extract path strings
        paths = set()
        if ".github/prompts/" in paths_str:
            paths.add(".github/prompts/")
        if ".github/agents/" in paths_str:
            paths.add(".github/agents/")
        if "README.md" in paths_str:
            paths.add("README.md")
        
        if len(paths) != 3:
            self.warnings.append(f"Layer 4: Expected 3 paths, found {len(paths)}")
        
        return paths
    
    def _validate_test_expectations(self) -> str:
        """Validate test expectations align with enforcement."""
        # Check that docs/*.md tests expect BLOCKED
        test_file = self.repo_root / "tests" / "unit" / "orchestrators" / "core" / "test_markdown_suppression_agent.py"
        
        if not test_file.exists():
            self.warnings.append("Layer 5: test_markdown_suppression_agent.py not found")
            return "NOT FOUND"
        
        content = test_file.read_text()
        
        # Check for docs/*.md blocking test
        if "docs/architecture/system-overview.md" in content:
            if "EnforcementLevel.BLOCKED" in content and "docs/*.md is NO LONGER ALLOWED" in content:
                return "docs/*.md BLOCKED ✅"
            else:
                self.violations.append("Layer 5: docs/*.md test expects PASS (should be BLOCKED)")
                return "docs/*.md ALLOWED ❌"
        else:
            self.warnings.append("Layer 5: No docs/*.md test found")
            return "NO TEST"
    
    def _validate_mcp_tools(self) -> str:
        """Validate MCP tools enforce CORE-002."""
        # Check if MCP tools directory exists
        mcp_dir = self.repo_root / "cortex" / "mcp" / "tools" / "governance"
        
        if not mcp_dir.exists():
            self.warnings.append("Layer 6: MCP governance tools directory not found")
            return "NOT FOUND"
        
        # Look for any markdown validation in MCP tools
        found_validation = False
        for tool_file in mcp_dir.glob("*.py"):
            content = tool_file.read_text()
            if "markdown" in content.lower() and "CORE-002" in content:
                found_validation = True
                break
        
        if found_validation:
            return "CORE-002 validation present ✅"
        else:
            self.warnings.append("Layer 6: No explicit CORE-002 validation in MCP tools")
            return "NO VALIDATION"


def main():
    """Run alignment validation."""
    repo_root = Path(__file__).parent.parent
    
    validator = AlignmentValidator(repo_root)
    
    print("=" * 80)
    print("CORTEX Governance Alignment Validator")
    print("=" * 80)
    print(f"Repository: {repo_root}")
    print(f"Validating: CORE-002 (No Markdown File Generation)")
    print("=" * 80)
    print()
    
    is_valid = validator.validate_core_002()
    
    if is_valid:
        print("\n🎉 SUCCESS: All layers aligned")
        sys.exit(0)
    else:
        print("\n❌ FAILURE: Misalignments detected")
        sys.exit(1)


if __name__ == "__main__":
    main()
