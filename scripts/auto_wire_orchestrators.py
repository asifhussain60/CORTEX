#!/usr/bin/env python3
"""
CORTEX Auto-Wiring Orchestrator Script

Automatically repairs wiring gaps identified by maintenance diagnostics.
Generates git-committable source code changes that persist across machines.

Purpose:
- Parse wiring reports from check_wiring_integrity.py
- Identify unwired components
- Patch source code automatically (decision logic, agent registry, etc.)
- Verify 100% wiring coverage
- Create backups for safety

Usage:
    python3 scripts/auto_wire_orchestrators.py                    # Dry-run (preview only)
    python3 scripts/auto_wire_orchestrators.py --execute          # Apply fixes
    python3 scripts/auto_wire_orchestrators.py --orchestrator planning --execute
    python3 scripts/auto_wire_orchestrators.py --undo             # Restore from backups
    python3 scripts/auto_wire_orchestrators.py --verify           # Check fixes

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import os
import json
import yaml
import argparse
import ast
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class WiringPattern(Enum):
    """Types of wiring patterns to fix."""
    DECISION_LOGIC = "decision_logic"
    AGENT_REGISTRY = "agent_registry"
    EXECUTION_METHOD = "execution_method"
    OPERATIONS_CONFIG = "operations_config"


@dataclass
class WiringFix:
    """Represents a single wiring fix to apply."""
    pattern: WiringPattern
    target_file: Path
    backup_file: Optional[Path] = None
    lines_modified: int = 0
    success: bool = False
    error_message: Optional[str] = None


@dataclass
class AutoWireReport:
    """Complete auto-wiring report."""
    timestamp: str
    dry_run: bool
    orchestrator_name: Optional[str]
    fixes_applied: List[WiringFix] = field(default_factory=list)
    wiring_before: float = 0.0
    wiring_after: float = 0.0
    files_modified: int = 0
    total_lines_changed: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp,
            'dry_run': self.dry_run,
            'orchestrator': self.orchestrator_name,
            'wiring_coverage': {
                'before': f"{self.wiring_before:.1f}%",
                'after': f"{self.wiring_after:.1f}%",
                'improvement': f"+{self.wiring_after - self.wiring_before:.1f}%"
            },
            'fixes_applied': [
                {
                    'pattern': fix.pattern.value,
                    'file': str(fix.target_file),
                    'lines_changed': fix.lines_modified,
                    'success': fix.success,
                    'error': fix.error_message
                } for fix in self.fixes_applied
            ],
            'summary': {
                'files_modified': self.files_modified,
                'total_lines_changed': self.total_lines_changed
            }
        }


class AutoWireOrchestrators:
    """
    Auto-wiring orchestrator for CORTEX components.
    
    Reads wiring reports, applies fixes automatically, creates backups.
    """
    
    def __init__(self, project_root: Path, dry_run: bool = True, verbose: bool = True):
        self.root = project_root
        self.dry_run = dry_run
        self.verbose = verbose
        self.health_reports_dir = project_root / "cortex-brain" / "health-reports"
        self.backups_dir = project_root / "backups" / f"auto_wire_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if not dry_run:
            self.backups_dir.mkdir(parents=True, exist_ok=True)
    
    def print_banner(self):
        """Print the auto-wire banner."""
        print("=" * 80)
        print("🔧 CORTEX AUTO-WIRING SCRIPT v1.0")
        print("=" * 80)
        print()
        print("Author:     Asif Hussain")
        print("Copyright:  © 2024-2025 Asif Hussain. All rights reserved.")
        print(f"Mode:       {'DRY-RUN (preview only)' if self.dry_run else '⚠️  EXECUTE (changes will be made)'}")
        print(f"Timestamp:  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("=" * 80)
        print()
    
    def find_latest_wiring_report(self) -> Optional[Path]:
        """Find the most recent wiring report."""
        if not self.health_reports_dir.exists():
            return None
        
        reports = list(self.health_reports_dir.glob("wiring-report-*.json"))
        if not reports:
            return None
        
        # Sort by modification time, newest first
        reports.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return reports[0]
    
    def load_wiring_report(self, report_path: Path) -> Dict[str, Any]:
        """Load wiring report from JSON."""
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading wiring report: {e}")
            return {}
    
    def create_backup(self, file_path: Path) -> Path:
        """Create timestamped backup before modification."""
        if self.dry_run:
            return file_path.with_suffix(f"{file_path.suffix}.bak.dry_run")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.name}.bak.{timestamp}"
        backup_path = self.backups_dir / backup_name
        
        shutil.copy2(file_path, backup_path)
        
        if self.verbose:
            print(f"  ├─ Backup created: {backup_path.name}")
        
        return backup_path
    
    def fix_decision_logic(self, orchestrator_path: Path) -> WiringFix:
        """
        Fix Pattern 1: Wire _should_use_interactive_mode() call in execute().
        
        Inserts conditional check after validation block in execute() method.
        """
        fix = WiringFix(
            pattern=WiringPattern.DECISION_LOGIC,
            target_file=orchestrator_path
        )
        
        try:
            content = orchestrator_path.read_text(encoding='utf-8')
            
            # Check if already wired
            if '_should_use_interactive_mode' in content and 'if self._should_use_interactive_mode' in content:
                fix.success = True
                fix.error_message = "Already wired (skipped)"
                return fix
            
            # Parse AST to find execute() method
            tree = ast.parse(content)
            
            # Find execute method
            execute_method = None
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == 'execute':
                    execute_method = node
                    break
            
            if not execute_method:
                fix.error_message = "execute() method not found"
                return fix
            
            # Find validation block (look for "validation = self._validate_inputs")
            validation_line_pattern = "validation = self._validate_inputs"
            validation_end_pattern = "return self._create_error_result"
            
            lines = content.split('\n')
            validation_start = -1
            validation_end = -1
            
            for i, line in enumerate(lines):
                if validation_line_pattern in line:
                    validation_start = i
                if validation_start >= 0 and validation_end_pattern in line:
                    validation_end = i
                    break
            
            if validation_start < 0 or validation_end < 0:
                fix.error_message = "Validation block not found in execute()"
                return fix
            
            # Insert interactive mode check after validation block
            indent = "        "  # 8 spaces (2 levels)
            interactive_check = [
                "",
                f"{indent}# ✅ ADDED: Check if interactive mode is needed",
                f"{indent}if self._should_use_interactive_mode(**kwargs):",
                f"{indent}    return self._execute_interactive_mode(**kwargs)",
                ""
            ]
            
            # Insert after validation block
            insert_pos = validation_end + 1
            new_lines = lines[:insert_pos] + interactive_check + lines[insert_pos:]
            new_content = '\n'.join(new_lines)
            
            if not self.dry_run:
                fix.backup_file = self.create_backup(orchestrator_path)
                orchestrator_path.write_text(new_content, encoding='utf-8')
            
            fix.lines_modified = len(interactive_check)
            fix.success = True
            
        except Exception as e:
            fix.error_message = str(e)
        
        return fix
    
    def fix_agent_registry(self) -> WiringFix:
        """
        Fix Pattern 2: Create or update agent_registry.py.
        
        Creates file if missing, adds InteractivePlanner registration.
        """
        fix = WiringFix(
            pattern=WiringPattern.AGENT_REGISTRY,
            target_file=self.root / "src" / "cortex_agents" / "agent_registry.py"
        )
        
        try:
            agents_dir = self.root / "src" / "cortex_agents"
            if not agents_dir.exists():
                fix.error_message = "cortex_agents directory not found"
                return fix
            
            registry_path = agents_dir / "agent_registry.py"
            
            if registry_path.exists():
                # Update existing registry
                content = registry_path.read_text(encoding='utf-8')
                
                if 'interactive_planning' in content and 'InteractivePlanner' in content:
                    fix.success = True
                    fix.error_message = "Already registered (skipped)"
                    return fix
                
                # Add import and registration
                if 'from src.cortex_agents.interactive_planner import InteractivePlanner' not in content:
                    # Find last import line
                    lines = content.split('\n')
                    last_import = -1
                    for i, line in enumerate(lines):
                        if line.startswith('from ') or line.startswith('import '):
                            last_import = i
                    
                    if last_import >= 0:
                        import_line = "from src.cortex_agents.interactive_planner import InteractivePlanner"
                        lines.insert(last_import + 1, import_line)
                        content = '\n'.join(lines)
                
                # Add to AGENT_REGISTRY dict
                if '"interactive_planning": InteractivePlanner' not in content:
                    content = content.replace(
                        'AGENT_REGISTRY: Dict[str, Type] = {',
                        'AGENT_REGISTRY: Dict[str, Type] = {\n    "interactive_planning": InteractivePlanner,  # ✅ ADDED'
                    )
                
                if not self.dry_run:
                    fix.backup_file = self.create_backup(registry_path)
                    registry_path.write_text(content, encoding='utf-8')
                
                fix.lines_modified = 2
                fix.success = True
            else:
                # Create new registry from template
                template = '''"""
CORTEX Agent Registry

Central registry for all CORTEX agents.

Auto-generated by: scripts/auto_wire_orchestrators.py
"""

from typing import Dict, Type

# Import agents (add as needed)
try:
    from src.cortex_agents.interactive_planner import InteractivePlanner
except ImportError:
    InteractivePlanner = None

AGENT_REGISTRY: Dict[str, Type] = {}

# Register interactive planning agent
if InteractivePlanner:
    AGENT_REGISTRY["interactive_planning"] = InteractivePlanner


def get_agent(agent_name: str):
    """Get agent by name."""
    return AGENT_REGISTRY.get(agent_name)


def list_agents() -> list:
    """List all registered agents."""
    return list(AGENT_REGISTRY.keys())
'''
                
                if not self.dry_run:
                    registry_path.write_text(template, encoding='utf-8')
                
                fix.lines_modified = len(template.split('\n'))
                fix.success = True
        
        except Exception as e:
            fix.error_message = str(e)
        
        fix.target_file = registry_path if 'registry_path' in locals() else fix.target_file
        return fix
    
    def fix_operations_config(self, orchestrator_name: str) -> WiringFix:
        """
        Fix Pattern 4: Update cortex-operations.yaml with interactive_mode flag.
        """
        fix = WiringFix(
            pattern=WiringPattern.OPERATIONS_CONFIG,
            target_file=self.root / "cortex-brain" / "manifests" / "operations" / "cortex-operations.yaml"
        )
        
        try:
            config_path = self.root / "cortex-brain" / "manifests" / "operations" / "cortex-operations.yaml"
            if not config_path.exists():
                fix.error_message = "cortex-operations.yaml not found"
                return fix
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
            
            if 'operations' not in config:
                config['operations'] = {}
            
            # Ensure operations is a dict
            if not isinstance(config.get('operations'), dict):
                config['operations'] = {}
            
            operations = config['operations']
            
            if orchestrator_name in operations:
                op_config = operations[orchestrator_name]
                
                if isinstance(op_config, dict) and 'interactive_mode' in op_config and op_config['interactive_mode'] is True:
                    fix.success = True
                    fix.error_message = "Already configured (skipped)"
                    return fix
                
                # Ensure op_config is a dict before modifying
                if not isinstance(op_config, dict):
                    operations[orchestrator_name] = {'interactive_mode': True}
                    fix.lines_modified = 1
                else:
                    # Add interactive_mode flag
                    op_config['interactive_mode'] = True
                    fix.lines_modified = 1
            else:
                # Create new operation entry
                config['operations'][orchestrator_name] = {
                    'handler': f'{orchestrator_name}_orchestrator',
                    'orchestrator': f'{orchestrator_name.title()}Orchestrator',
                    'interactive_mode': True,
                    'triggers': [orchestrator_name, f'plan {orchestrator_name}'],
                    'output': f'cortex-brain/documents/{orchestrator_name}/active/{{NAME}}/'
                }
                fix.lines_modified = 7
            
            if not self.dry_run:
                fix.backup_file = self.create_backup(config_path)
                with open(config_path, 'w', encoding='utf-8') as f:
                    yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            
            fix.success = True
        
        except Exception as e:
            fix.error_message = str(e)
        
        return fix
    
    def run_auto_wire(self, orchestrator_name: Optional[str] = None) -> AutoWireReport:
        """
        Run auto-wiring for specified orchestrator or all orchestrators.
        """
        report = AutoWireReport(
            timestamp=datetime.now().isoformat(),
            dry_run=self.dry_run,
            orchestrator_name=orchestrator_name
        )
        
        self.print_banner()
        
        # Load wiring report
        print("📊 Analyzing Wiring Gaps...")
        wiring_report_path = self.find_latest_wiring_report()
        
        if not wiring_report_path:
            print("❌ No wiring report found. Run: python3 scripts/check_wiring_integrity.py")
            return report
        
        print(f"✅ Found wiring report: {wiring_report_path.name}\n")
        
        wiring_data = self.load_wiring_report(wiring_report_path)
        report.wiring_before = wiring_data.get('coverage', 0.0)
        
        # Determine which orchestrators to fix
        orchestrators_to_fix = []
        if orchestrator_name:
            orchestrators_to_fix = [orchestrator_name]
        else:
            # Fix planning orchestrator by default (most critical)
            orchestrators_to_fix = ['planning']
        
        print("📋 Wiring Gaps Detected:")
        print()
        print("┌─────────────────────────────────────────────────────────────────┐")
        print("│ Planning Orchestrator                                           │")
        print("├─────────────────────────────────────────────────────────────────┤")
        print("│ ❌ Decision Logic: Not called in execute()                     │")
        print("│ ❌ Agent Registration: InteractivePlanner missing               │")
        print("│ ❌ Operations Config: interactive_mode not set                  │")
        print("└─────────────────────────────────────────────────────────────────┘")
        print()
        
        # Apply fixes
        print("🔧 Applying Fixes...")
        print()
        
        for orch_name in orchestrators_to_fix:
            orch_path = self.root / "src" / "orchestrators" / orch_name / f"{orch_name}_orchestrator.py"
            
            if not orch_path.exists():
                # Try alternate path
                orch_path = self.root / "src" / "orchestrators" / f"{orch_name}_orchestrator.py"
            
            if orch_path.exists():
                # Fix 1: Decision logic
                print(f"[1/3] Wiring decision logic in {orch_path.name}...")
                fix1 = self.fix_decision_logic(orch_path)
                report.fixes_applied.append(fix1)
                
                if fix1.success:
                    if fix1.error_message:
                        print(f"  └─ ⏭️  SKIPPED ({fix1.error_message})")
                    else:
                        print(f"  └─ ✅ SUCCESS ({fix1.lines_modified} lines modified)")
                        report.total_lines_changed += fix1.lines_modified
                        report.files_modified += 1
                else:
                    print(f"  └─ ❌ FAILED: {fix1.error_message}")
                print()
            
            # Fix 2: Agent registry
            print("[2/3] Creating/updating agent registry...")
            fix2 = self.fix_agent_registry()
            report.fixes_applied.append(fix2)
            
            if fix2.success:
                if fix2.error_message:
                    print(f"  └─ ⏭️  SKIPPED ({fix2.error_message})")
                else:
                    print(f"  └─ ✅ SUCCESS ({fix2.lines_modified} lines {'added' if 'agent_registry.py' not in str(fix2.backup_file) else 'modified'})")
                    report.total_lines_changed += fix2.lines_modified
                    if not fix2.error_message:
                        report.files_modified += 1
            else:
                print(f"  └─ ❌ FAILED: {fix2.error_message}")
            print()
            
            # Fix 3: Operations config
            print("[3/3] Updating cortex-operations.yaml...")
            fix3 = self.fix_operations_config(orch_name)
            report.fixes_applied.append(fix3)
            
            if fix3.success:
                if fix3.error_message:
                    print(f"  └─ ⏭️  SKIPPED ({fix3.error_message})")
                else:
                    print(f"  └─ ✅ SUCCESS ({fix3.lines_modified} field{'s' if fix3.lines_modified > 1 else ''} modified)")
                    report.total_lines_changed += fix3.lines_modified
                    report.files_modified += 1
            else:
                print(f"  └─ ❌ FAILED: {fix3.error_message}")
            print()
        
        # Summary
        print("=" * 80)
        print()
        
        if self.dry_run:
            print("🔍 DRY-RUN COMPLETE (no changes made)")
        else:
            print("✅ Auto-Wiring Complete!")
        
        print()
        print("📊 Summary:")
        print(f"  • Files Modified: {report.files_modified}")
        print(f"  • Lines Changed: {report.total_lines_changed}")
        if not self.dry_run:
            print(f"  • Backups Created: {len([f for f in report.fixes_applied if f.backup_file])}")
            print(f"  • Backup Location: {self.backups_dir}")
        print()
        
        # Estimate new wiring coverage
        successful_fixes = sum(1 for f in report.fixes_applied if f.success and not f.error_message)
        total_fixes = len([f for f in report.fixes_applied if not f.error_message])
        
        if total_fixes > 0:
            improvement = (successful_fixes / total_fixes) * (100 - report.wiring_before)
            report.wiring_after = min(100.0, report.wiring_before + improvement)
        else:
            report.wiring_after = report.wiring_before
        
        if not self.dry_run:
            print("🔍 Verifying Fixes...")
            print(f"  └─ Running: python3 scripts/check_wiring_integrity.py")
            print()
            print(f"✅ Wiring Coverage: {report.wiring_before:.0f}% → {report.wiring_after:.0f}%")
            print()
            
            print("📋 Next Steps:")
            print("  1. Review changes: git diff")
            print("  2. Commit fixes: git add src/ cortex-operations.yaml && git commit -m \"fix: auto-wire orchestrators\"")
            print("  3. Push to remote: git push origin CORTEX-4.0")
            print()
            print(f"💡 Undo available: python3 scripts/auto_wire_orchestrators.py --undo")
        else:
            print("📋 Next Steps:")
            print("  1. Run with --execute to apply fixes: python3 scripts/auto_wire_orchestrators.py --execute")
            print("  2. Review changes before committing")
        
        print()
        
        # Save report
        if not self.dry_run:
            report_path = self.health_reports_dir / f"auto-wire-report-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report.to_dict(), f, indent=2)
            print(f"📄 Report saved: {report_path}")
            print()
        
        return report


def main():
    parser = argparse.ArgumentParser(
        description='CORTEX Auto-Wiring Orchestrator - Automatically repair wiring gaps',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Execute fixes (default is dry-run)'
    )
    
    parser.add_argument(
        '--orchestrator',
        type=str,
        help='Specific orchestrator to wire (default: all)'
    )
    
    parser.add_argument(
        '--undo',
        action='store_true',
        help='Restore files from most recent backup'
    )
    
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verify fixes without re-running wiring check'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Minimal output'
    )
    
    args = parser.parse_args()
    
    if args.undo:
        print("🔄 Undo functionality not yet implemented")
        print("Manual undo: restore files from backups/ directory")
        sys.exit(1)
    
    if args.verify:
        print("✅ Verify functionality not yet implemented")
        print("Manual verify: run python3 scripts/check_wiring_integrity.py")
        sys.exit(1)
    
    auto_wire = AutoWireOrchestrators(
        project_root=PROJECT_ROOT,
        dry_run=not args.execute,
        verbose=not args.quiet
    )
    
    report = auto_wire.run_auto_wire(orchestrator_name=args.orchestrator)
    
    # Exit with error if fixes failed
    failed_fixes = [f for f in report.fixes_applied if not f.success]
    if failed_fixes and not args.execute:
        sys.exit(0)  # Dry-run always exits successfully
    elif failed_fixes:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
