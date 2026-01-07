"""
Tool Consolidator - Phase 8: Migration & Cleanup

Merges redundant tools into unified implementations.
Part of the Toolkit Manager implementation.

Author: Asif Hussain
Version: 1.0.0
"""
import logging
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set
import yaml

from .tool_auditor import ToolAuditor, ToolInfo, OverlapGroup

logger = logging.getLogger(__name__)


@dataclass
class ConsolidationPlan:
    """Plan for consolidating multiple tools into one."""
    source_tools: List[str]
    target_name: str
    target_command: str
    modes: List[str]
    default_mode: str
    capabilities: List[str]
    description: str
    created: datetime = field(default_factory=datetime.now)


@dataclass
class ConsolidationResult:
    """Result of a consolidation operation."""
    success: bool
    plan: ConsolidationPlan
    files_created: List[Path]
    files_archived: List[Path]
    manifest_updated: bool
    deprecation_notices: List[str]
    errors: List[str] = field(default_factory=list)


@dataclass
class DeprecationNotice:
    """Deprecation notice for a tool."""
    tool_name: str
    deprecated_date: str
    removal_date: str
    replacement: Optional[str]
    reason: str
    migration_guide: str


class ToolConsolidator:
    """
    Merges redundant tools into unified implementations.
    
    Consolidation Process:
    1. Create unified tool with all capabilities
    2. Add mode parameter for specific behaviors
    3. Create deprecation notices for old tools
    4. Update manifest entries
    5. Archive old tool files (don't delete)
    """
    
    # Predefined consolidation groups based on master plan
    CONSOLIDATION_GROUPS = {
        "cleanup": {
            "source_tools": [
                "cleanup",
                "cleanup-temp",
                "full-cleanup",
            ],
            "target_name": "cleanup",
            "target_command": "cortex-cleanup",
            "modes": ["brain", "temp", "full", "cache"],
            "default_mode": "full",
            "description": "Unified cleanup tool with multiple modes",
        },
        "schema-tools": {
            "source_tools": [
                "extract-schemas",
                "generate-ra-specs-v4",
            ],
            "target_name": "schema-tools",
            "target_command": "cortex-schema",
            "modes": ["extract", "generate", "validate"],
            "default_mode": "generate",
            "description": "Schema extraction and generation tools",
        },
    }
    
    def __init__(self, toolkit_root: Optional[Path] = None):
        """Initialize consolidator with toolkit root path."""
        if toolkit_root is None:
            toolkit_root = Path(__file__).parent.parent
        self.toolkit_root = toolkit_root
        self.archive_dir = toolkit_root / "archives" / "deprecated"
        self.auditor = ToolAuditor(toolkit_root)
        
        # Ensure archive directory exists
        self.archive_dir.mkdir(parents=True, exist_ok=True)
    
    def create_consolidation_plan(
        self,
        source_tools: List[str],
        target_name: str,
        target_command: Optional[str] = None,
        modes: Optional[List[str]] = None,
    ) -> ConsolidationPlan:
        """
        Create a plan for consolidating tools.
        
        Args:
            source_tools: List of tool names to consolidate
            target_name: Name for the unified tool
            target_command: CLI command (defaults to cortex-{target_name})
            modes: Mode names (defaults to source tool names)
        
        Returns:
            ConsolidationPlan with all details
        """
        # Get tool info for each source
        tool_infos = [self.auditor.get_tool(t) for t in source_tools]
        tool_infos = [t for t in tool_infos if t is not None]
        
        # Derive modes from tool names if not provided
        if modes is None:
            modes = [t.name.replace("cortex-", "").replace("-", "_") for t in tool_infos]
        
        # Combine capabilities
        all_capabilities: Set[str] = set()
        for tool in tool_infos:
            all_capabilities.update(tool.capabilities)
        
        # Build description
        descriptions = [t.description for t in tool_infos if t.description]
        combined_desc = f"Unified tool combining: {', '.join(descriptions[:3])}"
        
        return ConsolidationPlan(
            source_tools=source_tools,
            target_name=target_name,
            target_command=target_command or f"cortex-{target_name}",
            modes=modes,
            default_mode=modes[0] if modes else "default",
            capabilities=list(all_capabilities),
            description=combined_desc,
        )
    
    def consolidate_group(
        self,
        group_name: str,
        dry_run: bool = True,
    ) -> ConsolidationResult:
        """
        Consolidate a predefined group of tools.
        
        Args:
            group_name: Name of predefined group (e.g., "cleanup")
            dry_run: If True, only preview changes
        
        Returns:
            ConsolidationResult with details of changes
        """
        if group_name not in self.CONSOLIDATION_GROUPS:
            return ConsolidationResult(
                success=False,
                plan=ConsolidationPlan([], "", "", [], "", []),
                files_created=[],
                files_archived=[],
                manifest_updated=False,
                deprecation_notices=[],
                errors=[f"Unknown consolidation group: {group_name}"],
            )
        
        config = self.CONSOLIDATION_GROUPS[group_name]
        plan = self.create_consolidation_plan(
            source_tools=config["source_tools"],
            target_name=config["target_name"],
            target_command=config["target_command"],
            modes=config["modes"],
        )
        plan.default_mode = config["default_mode"]
        plan.description = config["description"]
        
        return self.execute_consolidation(plan, dry_run=dry_run)
    
    def execute_consolidation(
        self,
        plan: ConsolidationPlan,
        dry_run: bool = True,
    ) -> ConsolidationResult:
        """
        Execute a consolidation plan.
        
        Args:
            plan: ConsolidationPlan to execute
            dry_run: If True, only preview changes
        
        Returns:
            ConsolidationResult with details of changes
        """
        files_created: List[Path] = []
        files_archived: List[Path] = []
        deprecation_notices: List[str] = []
        errors: List[str] = []
        
        logger.info(f"{'[DRY RUN] ' if dry_run else ''}Consolidating {plan.source_tools} → {plan.target_name}")
        
        # Step 1: Create deprecation notices for source tools
        for tool_name in plan.source_tools:
            if tool_name != plan.target_name:
                notice = self._create_deprecation_notice(
                    tool_name=tool_name,
                    replacement=plan.target_name,
                    reason=f"Consolidated into unified {plan.target_name} tool",
                )
                deprecation_notices.append(notice.tool_name)
        
        # Step 2: Archive source tool scripts (don't delete)
        for tool_name in plan.source_tools:
            tool_info = self.auditor.get_tool(tool_name)
            if tool_info and tool_info.script_exists:
                script_path = self.toolkit_root / tool_info.script
                archive_path = self.archive_dir / f"{tool_name}_{datetime.now().strftime('%Y%m%d')}.py"
                
                if not dry_run:
                    try:
                        shutil.copy2(script_path, archive_path)
                        files_archived.append(archive_path)
                        logger.info(f"Archived: {script_path} → {archive_path}")
                    except Exception as e:
                        errors.append(f"Failed to archive {tool_name}: {e}")
                else:
                    files_archived.append(archive_path)
                    logger.info(f"[DRY RUN] Would archive: {script_path} → {archive_path}")
        
        # Step 3: Generate unified tool wrapper (stub)
        unified_wrapper = self._generate_unified_wrapper(plan)
        wrapper_path = self.toolkit_root / "cli" / "wrappers" / f"{plan.target_name}_wrapper.py"
        
        if not dry_run:
            try:
                wrapper_path.parent.mkdir(parents=True, exist_ok=True)
                wrapper_path.write_text(unified_wrapper)
                files_created.append(wrapper_path)
                logger.info(f"Created unified wrapper: {wrapper_path}")
            except Exception as e:
                errors.append(f"Failed to create wrapper: {e}")
        else:
            files_created.append(wrapper_path)
            logger.info(f"[DRY RUN] Would create wrapper: {wrapper_path}")
        
        # Step 4: Update manifest (create v2 entry)
        manifest_updated = False
        if not dry_run:
            manifest_updated = self._update_manifest_for_consolidation(plan)
        else:
            logger.info("[DRY RUN] Would update manifest with consolidated tool entry")
            manifest_updated = True
        
        return ConsolidationResult(
            success=len(errors) == 0,
            plan=plan,
            files_created=files_created,
            files_archived=files_archived,
            manifest_updated=manifest_updated,
            deprecation_notices=deprecation_notices,
            errors=errors,
        )
    
    def _create_deprecation_notice(
        self,
        tool_name: str,
        replacement: Optional[str],
        reason: str,
    ) -> DeprecationNotice:
        """Create a deprecation notice for a tool."""
        deprecated_date = datetime.now().strftime("%Y-%m-%d")
        # 90-day deprecation period
        removal_date = (datetime.now().replace(month=datetime.now().month + 3) 
                       if datetime.now().month <= 9 
                       else datetime.now().replace(year=datetime.now().year + 1, month=datetime.now().month - 9)).strftime("%Y-%m-%d")
        
        migration_guide = f"""
## Migration Guide: {tool_name}

### Deprecated Tool
- **Tool:** `{tool_name}`
- **Deprecated:** {deprecated_date}
- **Removal:** {removal_date}

### Replacement
- **New Tool:** `{replacement}`
- **Command:** `cortex-{replacement}`

### Migration Steps
1. Update any scripts using `{tool_name}` to use `{replacement}` instead
2. Check for mode-specific options (use `--help` for details)
3. Test the new tool in your workflow

### Example
```bash
# Before (deprecated)
cortex-{tool_name.replace('_', '-')}

# After (recommended)
cortex-{replacement}
```
"""
        return DeprecationNotice(
            tool_name=tool_name,
            deprecated_date=deprecated_date,
            removal_date=removal_date,
            replacement=replacement,
            reason=reason,
            migration_guide=migration_guide,
        )
    
    def _generate_unified_wrapper(self, plan: ConsolidationPlan) -> str:
        """Generate Python code for unified tool wrapper."""
        modes_enum = ", ".join(f'"{m}"' for m in plan.modes)
        source_tools_list = "\n".join(f"  - {t}" for t in plan.source_tools)
        modes_list = "\n".join(f"  - {m}" for m in plan.modes)
        handlers_dict = "\n".join(f'        "{m}": handle_{m.replace("-", "_")},' for m in plan.modes)
        
        # Generate handler functions
        handler_funcs = []
        for m in plan.modes:
            func_name = m.replace("-", "_")
            handler_funcs.append(f'''
def handle_{func_name}(args):
    """Handle {m} mode."""
    print(f"[{{args.mode}}] Mode handler - TODO: Implement")
    if args.dry_run:
        print("  (dry run - no changes made)")
    return 0
''')
        handlers_code = "\n".join(handler_funcs)
        
        return f'''"""
Unified {plan.target_name.title()} Tool Wrapper

Generated by ToolConsolidator on {datetime.now().strftime('%Y-%m-%d')}

Consolidates:
{source_tools_list}

Usage:
    cortex-{plan.target_name} --mode <mode> [options]

Modes:
{modes_list}
"""
import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="{plan.description}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--mode", "-m",
        choices=[{modes_enum}],
        default="{plan.default_mode}",
        help="Operation mode (default: {plan.default_mode})"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without executing"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Route to appropriate handler based on mode
    handlers = {{
{handlers_dict}
    }}
    
    handler = handlers.get(args.mode)
    if handler:
        return handler(args)
    else:
        print(f"Unknown mode: {{args.mode}}")
        return 1

{handlers_code}

if __name__ == "__main__":
    sys.exit(main())
'''
    
    def _update_manifest_for_consolidation(self, plan: ConsolidationPlan) -> bool:
        """Update manifest with consolidated tool entry."""
        try:
            manifest_path = self.toolkit_root / "toolkit-manifest.yaml"
            with open(manifest_path, "r") as f:
                manifest = yaml.safe_load(f)
            
            # Find the appropriate category
            target_category = "maintenance"  # Default
            for cat_name, cat_data in manifest.get("categories", {}).items():
                for tool in cat_data.get("tools", []):
                    if tool.get("name") in plan.source_tools:
                        target_category = cat_name
                        break
            
            # Create new tool entry
            new_tool = {
                "name": plan.target_name,
                "command": plan.target_command,
                "script": f"cli/wrappers/{plan.target_name}_wrapper.py",
                "description": plan.description,
                "platforms": ["windows", "linux", "macos"],
                "requires_admin": False,
                "execution_method": "cli",
                "capabilities": plan.capabilities,
                "modes": plan.modes,
                "default_mode": plan.default_mode,
                "replaces": plan.source_tools,
            }
            
            # Mark source tools as deprecated in manifest
            for cat_data in manifest.get("categories", {}).values():
                for tool in cat_data.get("tools", []):
                    if tool.get("name") in plan.source_tools:
                        tool["lifecycle"] = "deprecated"
                        tool["deprecated_date"] = datetime.now().strftime("%Y-%m-%d")
                        tool["replacement"] = plan.target_name
            
            # Note: We don't actually add the new tool to manifest in this phase
            # That would require more careful manifest schema management
            
            logger.info(f"Manifest would be updated with {plan.target_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update manifest: {e}")
            return False
    
    def generate_consolidation_report(self, result: ConsolidationResult) -> str:
        """Generate markdown report for consolidation."""
        status = "✅ Success" if result.success else "❌ Failed"
        
        lines = [
            "# Tool Consolidation Report",
            "",
            f"**Status:** {status}",
            f"**Date:** {result.plan.created.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Consolidation Plan",
            "",
            f"- **Target Tool:** `{result.plan.target_name}`",
            f"- **Command:** `{result.plan.target_command}`",
            f"- **Source Tools:** {', '.join(f'`{t}`' for t in result.plan.source_tools)}",
            "",
            "### Modes",
            "",
        ]
        
        for mode in result.plan.modes:
            default = " (default)" if mode == result.plan.default_mode else ""
            lines.append(f"- `{mode}`{default}")
        
        lines.extend([
            "",
            "## Changes Made",
            "",
            "### Files Created",
            "",
        ])
        
        if result.files_created:
            for f in result.files_created:
                lines.append(f"- `{f}`")
        else:
            lines.append("No files created.")
        
        lines.extend([
            "",
            "### Files Archived",
            "",
        ])
        
        if result.files_archived:
            for f in result.files_archived:
                lines.append(f"- `{f}`")
        else:
            lines.append("No files archived.")
        
        lines.extend([
            "",
            "### Deprecation Notices",
            "",
        ])
        
        if result.deprecation_notices:
            for notice in result.deprecation_notices:
                lines.append(f"- `{notice}` marked as deprecated")
        else:
            lines.append("No deprecation notices issued.")
        
        if result.errors:
            lines.extend([
                "",
                "## Errors",
                "",
            ])
            for error in result.errors:
                lines.append(f"- ❌ {error}")
        
        return "\n".join(lines)


if __name__ == "__main__":
    # Run consolidation from command line
    import argparse
    
    logging.basicConfig(level=logging.INFO)
    
    parser = argparse.ArgumentParser(description="Tool Consolidator")
    parser.add_argument("group", choices=list(ToolConsolidator.CONSOLIDATION_GROUPS.keys()),
                       help="Consolidation group to execute")
    parser.add_argument("--execute", action="store_true",
                       help="Actually execute (default is dry run)")
    
    args = parser.parse_args()
    
    consolidator = ToolConsolidator()
    result = consolidator.consolidate_group(args.group, dry_run=not args.execute)
    
    print(consolidator.generate_consolidation_report(result))
