#!/usr/bin/env python3
"""
CORTEX Align CLI Wrapper

Command-line interface for CORTEX system alignment.

Features:
- Feature registration validation
- Auto-discovery and registration
- Intent router coverage check
- Response template validation
- Documentation alignment
- Obsolete code detection
- Module import health check
- CORTEX.prompt.md optimization validation

Usage:
    python scripts/cli_wrappers/align_wrapper.py
    python scripts/cli_wrappers/align_wrapper.py --auto-fix
    python scripts/cli_wrappers/align_wrapper.py --dry-run
    python scripts/cli_wrappers/align_wrapper.py --output json

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import sys
from pathlib import Path
from typing import Dict, Any
import argparse

# Add CORTEX root to path
CORTEX_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(CORTEX_ROOT))

from .base_wrapper import BaseCLIWrapper, main_template
from src.operations.modules.realignment.realignment_utility import align_system_v2
from src.operations.base_operation_module import OperationResult, OperationStatus


class AlignWrapper(BaseCLIWrapper):
    """CLI wrapper for CORTEX system alignment."""
    
    def get_orchestrator(self):
        """
        Get alignment orchestrator.
        
        Note: align_system_v2 is a function, not a class.
        We'll wrap it in a simple executor.
        """
        class AlignExecutor:
            def __init__(self, auto_fix: bool = False, dry_run: bool = False):
                self.auto_fix = auto_fix
                self.dry_run = dry_run
            
            def execute(self, context: Dict[str, Any]) -> OperationResult:
                """Execute alignment."""
                project_root = context.get('project_root', Path.cwd())
                cortex_root = context.get('cortex_root', CORTEX_ROOT)
                
                result = align_system_v2(
                    project_root=project_root,
                    cortex_root=cortex_root,
                    auto_fix=self.auto_fix,
                    dry_run=self.dry_run
                )
                
                # Convert dict result to OperationResult
                status = OperationStatus.SUCCESS if result.get('success', False) else OperationStatus.FAILED
                
                message_parts = []
                if result.get('success'):
                    message_parts.append("System alignment completed successfully")
                else:
                    message_parts.append("System alignment found issues")
                
                # Add summary
                checks = result.get('checks', {})
                if checks:
                    passed = sum(1 for c in checks.values() if c.get('passed', False))
                    total = len(checks)
                    message_parts.append(f"\nChecks: {passed}/{total} passed")
                
                fixes = result.get('fixes_applied', [])
                if fixes:
                    message_parts.append(f"Fixes applied: {len(fixes)}")
                
                return OperationResult(
                    status=status,
                    message='\n'.join(message_parts),
                    data=result,
                    warnings=result.get('warnings', []),
                    errors=[str(e) for e in result.get('errors', [])]
                )
        
        return AlignExecutor(
            auto_fix=self.args.auto_fix,
            dry_run=self.args.dry_run
        )
    
    def get_operation_name(self) -> str:
        """Get operation name."""
        return "CORTEX Align v2.0"
    
    def setup_argparse(self, parser: argparse.ArgumentParser) -> None:
        """Configure command-line arguments."""
        super().setup_argparse(parser)
        
        parser.add_argument(
            '--auto-fix',
            action='store_true',
            help='Automatically fix issues without prompting'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without applying'
        )
        parser.add_argument(
            '--cortex-root',
            type=str,
            default=str(CORTEX_ROOT),
            help='CORTEX installation root (default: auto-detected)'
        )
    
    def build_context(self) -> Dict[str, Any]:
        """Build context for alignment."""
        context = super().build_context()
        context['cortex_root'] = Path(self.args.cortex_root).resolve()
        return context
    
    def format_text_output(self, result: OperationResult) -> str:
        """Format alignment result as human-readable text."""
        lines = []
        lines.append(f"\n{'='*70}")
        lines.append(f"  🧠 CORTEX Align v2.0 - System Alignment")
        lines.append(f"{'='*70}\n")
        
        # Status
        if result.status == OperationStatus.SUCCESS:
            lines.append("Status: ✓ SUCCESS")
        else:
            lines.append("Status: ✗ FAILED")
        
        # Message
        if result.message:
            lines.append(f"\n{result.message}")
        
        # Checks
        if result.data and 'checks' in result.data:
            lines.append("\n" + "="*70)
            lines.append("CHECKS")
            lines.append("="*70)
            
            checks = result.data['checks']
            for check_name, check_data in checks.items():
                passed = check_data.get('passed', False)
                status_icon = "✓" if passed else "✗"
                lines.append(f"\n{status_icon} {check_name.replace('_', ' ').title()}")
                
                # Show check details
                for key, value in check_data.items():
                    if key != 'passed':
                        lines.append(f"  {key}: {value}")
        
        # Fixes Applied
        if result.data and 'fixes_applied' in result.data:
            fixes = result.data['fixes_applied']
            if fixes:
                lines.append("\n" + "="*70)
                lines.append(f"FIXES APPLIED ({len(fixes)})")
                lines.append("="*70)
                for fix in fixes:
                    lines.append(f"  ✓ {fix}")
        
        # Warnings
        if result.warnings:
            lines.append("\n" + "="*70)
            lines.append(f"⚠️  WARNINGS ({len(result.warnings)})")
            lines.append("="*70)
            for warning in result.warnings:
                if isinstance(warning, dict):
                    lines.append(f"  [{warning.get('severity', 'UNKNOWN')}] {warning.get('message', 'No message')}")
                else:
                    lines.append(f"  {warning}")
        
        # Errors
        if result.errors:
            lines.append("\n" + "="*70)
            lines.append(f"❌ ERRORS ({len(result.errors)})")
            lines.append("="*70)
            for error in result.errors:
                lines.append(f"  {error}")
        
        # Report Path
        if result.data and 'report_path' in result.data and result.data['report_path']:
            lines.append(f"\n📄 Detailed report: {result.data['report_path']}")
        
        lines.append(f"\n{'='*70}\n")
        return '\n'.join(lines)


if __name__ == '__main__':
    sys.exit(main_template(AlignWrapper))
