"""
MCP Server Unity Enforcer - CORE-026 Governance Rule

Enforces that CORTEX has ONE authoritative MCP tools registry with no duplicates,
UUID suffixes, or scattered definitions.

Prevents registration drift - the #1 failure mode in MCP exposure.
"""

import pathlib
import re
from typing import List, Tuple, Dict
import yaml


class MCPUnityEnforcer:
    """Enforces CORE-026: MCP Server Unity"""
    
    AUTHORITATIVE_REGISTRY = "cortex-brain/tier0/governance/mcp-tools-registry.yaml"
    UUID_PATTERN = re.compile(r'^mcp-tools-registry-[a-f0-9]{8}\.yaml$')
    
    def __init__(self, workspace_root: pathlib.Path):
        self.workspace_root = pathlib.Path(workspace_root)
        self.violations = []
    
    def validate_all(self) -> bool:
        """
        Run all MCPUnityEnforcer validations.
        
        Returns:
            bool: True if all validations pass, False if any violations found
        """
        self.validate_single_registry()
        self.validate_no_uuid_suffixes()
        self.validate_no_duplicate_tools()
        self.validate_authoritative_location()
        
        return len(self.violations) == 0
    
    def validate_single_registry(self) -> bool:
        """
        Validate only ONE *.mcp.yaml file exists (excluding archives).
        
        Violations:
        - Multiple *.mcp.yaml files found
        - No .mcp.yaml files found
        """
        mcp_files = list(
            self.workspace_root.glob("cortex-brain/**/*.mcp.yaml")
        )
        
        # Exclude archive files
        mcp_files = [
            f for f in mcp_files 
            if "archive" not in str(f)
        ]
        
        if len(mcp_files) == 0:
            self.violations.append(
                "CORE-026-001: No *.mcp.yaml files found. "
                "Expected: cortex-brain/tier0/governance/mcp-tools-registry.yaml"
            )
            return False
        
        if len(mcp_files) > 1:
            files_str = "\n  ".join(str(f.relative_to(self.workspace_root)) for f in mcp_files)
            self.violations.append(
                f"CORE-026-002: Multiple *.mcp.yaml files found (expected 1):\n  {files_str}"
            )
            return False
        
        return True
    
    def validate_no_uuid_suffixes(self) -> bool:
        """
        Validate no files matching UUID pattern exist.
        
        Violations:
        - Files like mcp-tools-registry-6160caae.yaml found
        """
        registry_dir = self.workspace_root / "cortex-brain" / "registry"
        if not registry_dir.exists():
            return True  # Directory doesn't exist, so no UUID files
        
        uuid_files = [
            f for f in registry_dir.glob("mcp-tools-registry-*.yaml")
            if self.UUID_PATTERN.match(f.name)
        ]
        
        if uuid_files:
            files_str = "\n  ".join(f.name for f in uuid_files)
            self.violations.append(
                f"CORE-026-003: UUID-suffixed registry files found (forbidden):\n  {files_str}\n"
                f"  These must be deleted and consolidated into:\n"
                f"  cortex-brain/tier0/governance/mcp-tools-registry.yaml"
            )
            return False
        
        return True
    
    def validate_no_duplicate_tools(self) -> bool:
        """
        Validate registry doesn't define same tool multiple times.
        
        Violations:
        - Tool name appears multiple times in registry
        """
        registry_path = self.workspace_root / self.AUTHORITATIVE_REGISTRY
        
        if not registry_path.exists():
            self.violations.append(
                f"CORE-026-004: Authoritative registry not found: {self.AUTHORITATIVE_REGISTRY}"
            )
            return False
        
        try:
            with open(registry_path, 'r') as f:
                registry = yaml.safe_load(f) or {}
        except Exception as e:
            self.violations.append(
                f"CORE-026-005: Failed to parse registry YAML: {e}"
            )
            return False
        
        tool_names = []
        categories = registry.get("categories", {})
        
        for category_name, category_data in categories.items():
            tools = category_data.get("tools", [])
            for tool in tools:
                tool_name = tool.get("name")
                if tool_name:
                    if tool_name in tool_names:
                        self.violations.append(
                            f"CORE-026-006: Tool '{tool_name}' defined multiple times in registry"
                        )
                        return False
                    tool_names.append(tool_name)
        
        return True
    
    def validate_authoritative_location(self) -> bool:
        """
        Validate authoritative registry exists at correct location.
        
        Violations:
        - Registry not at cortex-brain/tier0/governance/mcp-tools-registry.yaml
        """
        registry_path = self.workspace_root / self.AUTHORITATIVE_REGISTRY
        
        if not registry_path.exists():
            self.violations.append(
                f"CORE-026-007: Authoritative registry missing: {self.AUTHORITATIVE_REGISTRY}"
            )
            return False
        
        # Verify it's not a symlink pointing elsewhere
        if registry_path.is_symlink():
            target = registry_path.resolve()
            if target.relative_to(self.workspace_root) != pathlib.Path(self.AUTHORITATIVE_REGISTRY):
                self.violations.append(
                    f"CORE-026-008: Registry is symlink pointing elsewhere: {target}"
                )
                return False
        
        return True
    
    def get_violation_report(self) -> str:
        """
        Generate formatted violation report.
        
        Returns:
            str: Formatted report of all violations
        """
        if not self.violations:
            return "✅ CORE-026 COMPLIANT: MCP Server Unity enforced"
        
        report_lines = ["❌ CORE-026 VIOLATIONS DETECTED:", ""]
        report_lines.extend(f"  • {v}" for v in self.violations)
        report_lines.append("")
        report_lines.append("REMEDIATION:")
        report_lines.append("  1. Consolidate all *.mcp.yaml files into one")
        report_lines.append("  2. Move to: cortex-brain/tier0/governance/mcp-tools-registry.yaml")
        report_lines.append("  3. Remove UUID suffixes (mcp-tools-registry-XXXXX.yaml)")
        report_lines.append("  4. Delete all obsolete files")
        report_lines.append("  5. Update all code references")
        
        return "\n".join(report_lines)
    
    def block_commit_if_violations(self) -> bool:
        """
        Check if violations exist and block commit.
        
        Returns:
            bool: False if violations exist (block commit), True otherwise
        """
        if not self.validate_all():
            print(self.get_violation_report())
            return False
        
        return True


def enforce_pre_commit(workspace_root: str) -> bool:
    """
    Pre-commit hook entrypoint for git pre-commit hook.
    
    Args:
        workspace_root: Root directory of CORTEX workspace
        
    Returns:
        bool: True if check passes, False to block commit
    """
    enforcer = MCPUnityEnforcer(workspace_root)
    return enforcer.block_commit_if_violations()
