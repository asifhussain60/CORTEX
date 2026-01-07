#!/usr/bin/env python3
"""
CORTEX Cleanup CLI Wrapper

Command-line interface for CORTEX holistic cleanup.

Features:
- Recursive directory scanning
- Production-ready file naming validation
- Redundancy detection and elimination
- Detailed reporting before execution
- Safe execution with backup/rollback support

Usage:
    python scripts/cli_wrappers/cleanup_wrapper.py
    python scripts/cli_wrappers/cleanup_wrapper.py --dry-run
    python scripts/cli_wrappers/cleanup_wrapper.py --output json

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import sys
from pathlib import Path
import argparse

# Add CORTEX root to path
CORTEX_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(CORTEX_ROOT))

from .base_wrapper import BaseCLIWrapper, main_template
from src.operations.modules.cleanup.holistic_cleanup_orchestrator import HolisticCleanupOrchestrator


class CleanupWrapper(BaseCLIWrapper):
    """CLI wrapper for CORTEX holistic cleanup."""
    
    def get_orchestrator(self):
        """Get cleanup orchestrator."""
        return HolisticCleanupOrchestrator(project_root=Path(self.args.project_root))
    
    def get_operation_name(self) -> str:
        """Get operation name."""
        return "CORTEX Holistic Cleanup"
    
    def setup_argparse(self, parser: argparse.ArgumentParser) -> None:
        """Configure command-line arguments."""
        super().setup_argparse(parser)
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without applying'
        )
    
    def build_context(self):
        """Build context for cleanup."""
        from typing import Dict, Any
        context = super().build_context()
        context['dry_run'] = getattr(self.args, 'dry_run', False)
        return context
    
    def format_text_output(self, result) -> str:
        """Format cleanup result as human-readable text."""
        from src.operations.base_operation_module import OperationStatus
        
        lines = []
        lines.append(f"\n{'='*70}")
        lines.append(f"  🧹 CORTEX Holistic Cleanup")
        lines.append(f"{'='*70}\n")
        
        # Status
        if result.status == OperationStatus.SUCCESS:
            lines.append("Status: ✓ SUCCESS")
        else:
            lines.append("Status: ✗ FAILED")
        
        # Message
        if result.message:
            lines.append(f"\n{result.message}")
        
        # Manifest
        if result.data and 'manifest' in result.data:
            lines.append("\n" + "="*70)
            lines.append("CLEANUP MANIFEST")
            lines.append("="*70)
            
            manifest = result.data['manifest']
            if isinstance(manifest, dict):
                overview = manifest.get('overview', {})
                if overview:
                    lines.append(f"\nFiles scanned: {overview.get('total_files', 0)}")
                    lines.append(f"Production-ready: {overview.get('production_ready', 0)}")
                    lines.append(f"Non-production: {overview.get('non_production', 0)}")
                    lines.append(f"Total size: {overview.get('total_size_mb', 0):.2f} MB")
        
        # Actions
        if result.data and 'actions_applied' in result.data:
            actions = result.data['actions_applied']
            if actions:
                lines.append("\n" + "="*70)
                lines.append(f"ACTIONS APPLIED ({len(actions)})")
                lines.append("="*70)
                for action in actions[:20]:  # Show top 20
                    if isinstance(action, dict):
                        action_type = action.get('type', 'unknown')
                        target = action.get('target', 'unknown')
                        lines.append(f"  {action_type}: {target}")
                    else:
                        lines.append(f"  {action}")
                
                if len(actions) > 20:
                    lines.append(f"  ... and {len(actions) - 20} more")
        
        # Proposed Actions (dry-run)
        if result.data and 'proposed_actions' in result.data:
            actions = result.data['proposed_actions']
            if actions:
                lines.append("\n" + "="*70)
                lines.append(f"PROPOSED ACTIONS ({len(actions)})")
                lines.append("="*70)
                for action in actions[:20]:  # Show top 20
                    if isinstance(action, dict):
                        action_type = action.get('type', 'unknown')
                        target = action.get('target', 'unknown')
                        lines.append(f"  {action_type}: {target}")
                    else:
                        lines.append(f"  {action}")
                
                if len(actions) > 20:
                    lines.append(f"  ... and {len(actions) - 20} more")
        
        # Recommendations
        if result.data and 'recommendations' in result.data:
            recommendations = result.data['recommendations']
            if recommendations:
                lines.append("\n" + "="*70)
                lines.append(f"💡 RECOMMENDATIONS ({len(recommendations)})")
                lines.append("="*70)
                for i, rec in enumerate(recommendations[:10], 1):  # Show top 10
                    if isinstance(rec, dict):
                        lines.append(f"  {i}. {rec.get('recommendation', 'Unknown')}")
                    else:
                        lines.append(f"  {i}. {rec}")
        
        # Warnings
        if result.warnings:
            lines.append("\n" + "="*70)
            lines.append(f"⚠️  WARNINGS ({len(result.warnings)})")
            lines.append("="*70)
            for warning in result.warnings:
                lines.append(f"  {warning}")
        
        # Errors
        if result.errors:
            lines.append("\n" + "="*70)
            lines.append(f"❌ ERRORS ({len(result.errors)})")
            lines.append("="*70)
            for error in result.errors:
                lines.append(f"  {error}")
        
        lines.append(f"\n{'='*70}\n")
        return '\n'.join(lines)


if __name__ == '__main__':
    sys.exit(main_template(CleanupWrapper))
