#!/usr/bin/env python3
"""
CORTEX Regenerate Prompts CLI Wrapper

Command-line interface for regenerating Copilot prompt files.

Features:
- Delete and regenerate copilot-instructions.md
- Delete and regenerate CORTEX.prompt.md
- Scan current codebase state
- Preserve manual enhancements (with --force override)
- Dry-run preview mode

Usage:
    python scripts/cli_wrappers/regenerate_prompts_wrapper.py
    python scripts/cli_wrappers/regenerate_prompts_wrapper.py --dry-run
    python scripts/cli_wrappers/regenerate_prompts_wrapper.py --force
    python scripts/cli_wrappers/regenerate_prompts_wrapper.py --output json

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

# Import regenerate script
sys.path.insert(0, str(CORTEX_ROOT / "scripts"))
from regenerate_cortex_prompts import PromptRegenerator

from scripts.cli_wrappers.base_wrapper import BaseCLIWrapper, main_template
from src.operations.base_operation_module import OperationResult, OperationStatus


class RegeneratePromptsWrapper(BaseCLIWrapper):
    """CLI wrapper for prompt regeneration."""
    
    def get_orchestrator(self):
        """
        Get prompt regenerator.
        
        Note: PromptRegenerator is a class with run() method.
        We'll wrap it to match BaseOperationModule interface.
        """
        class RegeneratorExecutor:
            def __init__(self, cortex_root: Path, dry_run: bool = False, force: bool = False):
                self.regenerator = PromptRegenerator(
                    cortex_root=cortex_root,
                    dry_run=dry_run,
                    force=force
                )
            
            def execute(self, context):
                """Execute regeneration."""
                try:
                    result = self.regenerator.run()
                    
                    # Convert result to OperationResult
                    status = OperationStatus.SUCCESS if result.get('success', False) else OperationStatus.FAILED
                    
                    message_parts = []
                    if result.get('success'):
                        message_parts.append("Prompt regeneration completed successfully")
                    else:
                        message_parts.append("Prompt regeneration failed")
                    
                    files_updated = result.get('files_updated', [])
                    if files_updated:
                        message_parts.append(f"Updated {len(files_updated)} files")
                    
                    return OperationResult(
                        status=status,
                        message='\n'.join(message_parts),
                        data=result,
                        warnings=result.get('warnings', []),
                        errors=result.get('errors', [])
                    )
                except Exception as e:
                    return OperationResult(
                        status=OperationStatus.FAILED,
                        message=f"Regeneration failed: {str(e)}",
                        data={},
                        warnings=[],
                        errors=[str(e)]
                    )
        
        return RegeneratorExecutor(
            cortex_root=CORTEX_ROOT,
            dry_run=getattr(self.args, 'dry_run', False),
            force=getattr(self.args, 'force', False)
        )
    
    def get_operation_name(self) -> str:
        """Get operation name."""
        return "CORTEX Regenerate Prompts"
    
    def setup_argparse(self, parser: argparse.ArgumentParser) -> None:
        """Configure command-line arguments."""
        super().setup_argparse(parser)
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without applying'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Override preservation of manual enhancements'
        )
    
    def format_text_output(self, result) -> str:
        """Format regeneration result as human-readable text."""
        lines = []
        lines.append(f"\n{'='*70}")
        lines.append(f"  📝 CORTEX Regenerate Prompts")
        lines.append(f"{'='*70}\n")
        
        # Status
        if result.status == OperationStatus.SUCCESS:
            lines.append("Status: ✓ SUCCESS")
        else:
            lines.append("Status: ✗ FAILED")
        
        # Message
        if result.message:
            lines.append(f"\n{result.message}")
        
        # Files Updated
        if result.data and 'files_updated' in result.data:
            files = result.data['files_updated']
            if files:
                lines.append("\n" + "="*70)
                lines.append(f"FILES UPDATED ({len(files)})")
                lines.append("="*70)
                for file in files:
                    lines.append(f"  ✓ {file}")
        
        # Files Preserved
        if result.data and 'files_preserved' in result.data:
            files = result.data['files_preserved']
            if files:
                lines.append("\n" + "="*70)
                lines.append(f"FILES PRESERVED ({len(files)})")
                lines.append("="*70)
                for file in files:
                    lines.append(f"  🔒 {file}")
                    lines.append(f"     (Manual enhancements protected)")
        
        # Backup Info
        if result.data and 'backup_path' in result.data:
            lines.append("\n" + "="*70)
            lines.append("BACKUP")
            lines.append("="*70)
            lines.append(f"  Path: {result.data['backup_path']}")
        
        # Summary
        if result.data and 'summary' in result.data:
            lines.append("\n" + "="*70)
            lines.append("SUMMARY")
            lines.append("="*70)
            
            summary = result.data['summary']
            if isinstance(summary, dict):
                for key, value in summary.items():
                    lines.append(f"  {key}: {value}")
        
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
    sys.exit(main_template(RegeneratePromptsWrapper))
