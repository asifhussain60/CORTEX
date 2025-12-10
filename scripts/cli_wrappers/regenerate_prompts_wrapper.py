#!/usr/bin/env python3
"""
CORTEX Regenerate Prompts CLI Wrapper

Command-line interface for regenerating Copilot prompt files.

Features:
- Delete and regenerate copilot-instructions.md
- Delete and regenerate CORTEX.prompt.md
- Scan current codebase state
- Preserve manual enhancements (with --force override)
- Intelligent incremental regeneration (only regenerate changed files)
- Dry-run preview mode

Usage:
    python scripts/cli_wrappers/regenerate_prompts_wrapper.py
    python scripts/cli_wrappers/regenerate_prompts_wrapper.py --incremental  # Default mode
    python scripts/cli_wrappers/regenerate_prompts_wrapper.py --force  # Full regeneration
    python scripts/cli_wrappers/regenerate_prompts_wrapper.py --dry-run
    python scripts/cli_wrappers/regenerate_prompts_wrapper.py --output json

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 2.0.0
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
            def __init__(self, cortex_root: Path, dry_run: bool = False, force: bool = False, incremental: bool = True):
                self.cortex_root = cortex_root
                self.dry_run = dry_run
                self.force = force
                self.incremental = incremental and not force  # Force overrides incremental
                
                self.regenerator = PromptRegenerator(
                    cortex_root=cortex_root,
                    dry_run=dry_run,
                    force=force
                )
            
            def execute(self, context):
                """Execute regeneration with intelligent change detection."""
                try:
                    # Import tracker
                    from src.operations.utilities.regeneration_tracker import RegenerationTracker
                    
                    tracker = RegenerationTracker(self.cortex_root)
                    
                    # If force mode, clear manifest to regenerate everything
                    if self.force:
                        print("🔥 Force mode: Regenerating all files")
                        tracker.clear_manifest()
                    elif self.incremental:
                        print("⚡ Incremental mode: Only regenerating changed files")
                    
                    # Define files to regenerate with their dependencies
                    files_to_check = [
                        {
                            'output': '.github/copilot-instructions.md',
                            'dependencies': [
                                'cortex-brain/response-templates.yaml',
                                'cortex-brain/brain-protection-rules.yaml',
                                'cortex-operations.yaml',
                                'scripts/regenerate_cortex_prompts.py',
                                'src/tier0/README.md',
                                'src/tier1/README.md',
                                'src/tier2/README.md',
                                'src/tier3/README.md'
                            ]
                        },
                        {
                            'output': '.github/prompts/CORTEX.prompt.md',
                            'dependencies': [
                                'cortex-brain/response-templates.yaml',
                                'cortex-brain/brain-protection-rules.yaml',
                                'cortex-operations.yaml',
                                'scripts/regenerate_cortex_prompts.py',
                                'cortex-brain/orchestrator-manifests/planning-system-2.0-manifest.yaml',
                                'cortex-brain/orchestrator-manifests/ado-planning-manifest.yaml'
                            ]
                        }
                    ]
                    
                    files_to_regenerate = []
                    files_skipped = []
                    
                    # Check each file
                    if self.incremental and not self.force:
                        for file_config in files_to_check:
                            should_regen, reason = tracker.should_regenerate(
                                file_config['output'],
                                file_config['dependencies']
                            )
                            
                            if should_regen:
                                files_to_regenerate.append(file_config['output'])
                                print(f"  ✓ Will regenerate: {file_config['output']}")
                                print(f"    Reason: {reason}")
                            else:
                                files_skipped.append(file_config['output'])
                                print(f"  ⏭️  Skipping: {file_config['output']}")
                                print(f"    Reason: {reason}")
                        
                        # If nothing to regenerate, return early
                        if not files_to_regenerate:
                            stats = tracker.finalize()
                            
                            return OperationResult(
                                success=True,
                                status=OperationStatus.SUCCESS,
                                message="No files need regeneration - all up to date!",
                                data={
                                    'files_skipped': files_skipped,
                                    'files_updated': [],
                                    'statistics': stats
                                },
                                warnings=[],
                                errors=[]
                            )
                    else:
                        # Force mode - regenerate everything
                        files_to_regenerate = [f['output'] for f in files_to_check]
                    
                    # Run regeneration
                    print(f"\n📝 Regenerating {len(files_to_regenerate)} file(s)...")
                    result = self.regenerator.execute()
                    
                    # Update tracker for regenerated files
                    if result.get('success') and not self.dry_run:
                        for file_config in files_to_check:
                            if file_config['output'] in files_to_regenerate:
                                tracker.mark_regenerated(
                                    file_config['output'],
                                    file_config['dependencies']
                                )
                        
                        if self.force:
                            tracker.mark_full_regeneration()
                    
                    # Finalize and get statistics
                    stats = tracker.finalize()
                    
                    # Show summary
                    if self.incremental:
                        print(f"\n📊 Regeneration Statistics:")
                        print(f"  Files regenerated: {len(files_to_regenerate)}")
                        print(f"  Files skipped: {len(files_skipped)}")
                        print(f"  Time saved: ~{stats['time_saved']:.1f} seconds")
                    
                    # Convert result to OperationResult
                    is_success = result.get('success', False)
                    status = OperationStatus.SUCCESS if is_success else OperationStatus.FAILED
                    
                    message_parts = []
                    if is_success:
                        if self.incremental and files_skipped:
                            message_parts.append(f"Incremental regeneration completed - {len(files_to_regenerate)} regenerated, {len(files_skipped)} skipped")
                        else:
                            message_parts.append("Prompt regeneration completed successfully")
                    else:
                        message_parts.append("Prompt regeneration failed")
                    
                    files_updated = result.get('files_updated', [])
                    if files_updated:
                        message_parts.append(f"Updated {len(files_updated)} files")
                    
                    # Add statistics to result data
                    result['statistics'] = stats
                    result['files_skipped'] = files_skipped
                    
                    return OperationResult(
                        success=is_success,
                        status=status,
                        message='\n'.join(message_parts),
                        data=result,
                        warnings=result.get('warnings', []),
                        errors=result.get('errors', [])
                    )
                except Exception as e:
                    import traceback
                    return OperationResult(
                        success=False,
                        status=OperationStatus.FAILED,
                        message=f"Regeneration failed: {str(e)}",
                        data={},
                        warnings=[],
                        errors=[str(e), traceback.format_exc()]
                    )
        
        return RegeneratorExecutor(
            cortex_root=CORTEX_ROOT,
            dry_run=getattr(self.args, 'dry_run', False),
            force=getattr(self.args, 'force', False),
            incremental=getattr(self.args, 'incremental', True)
        )
    
    def get_operation_name(self) -> str:
        """Get operation name."""
        return "CORTEX Regenerate Prompts"
    
    def setup_argparse(self, parser: argparse.ArgumentParser) -> None:
        """Configure command-line arguments."""
        super().setup_argparse(parser)
        
        parser.add_argument(
            '--incremental',
            action='store_true',
            default=True,
            help='Only regenerate files that changed (default behavior)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without applying'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force full regeneration (overrides --incremental and preservation)'
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
        
        # Statistics (if available)
        if result.data and 'statistics' in result.data:
            stats = result.data['statistics']
            lines.append("\n" + "="*70)
            lines.append("REGENERATION STATISTICS")
            lines.append("="*70)
            lines.append(f"  Files regenerated: {stats.get('files_processed', 0)}")
            lines.append(f"  Files skipped: {stats.get('files_skipped', 0)}")
            lines.append(f"  Time elapsed: {stats.get('elapsed_time', 0):.2f}s")
            lines.append(f"  Time saved: ~{stats.get('time_saved', 0):.1f}s")
        
        # Files Updated
        if result.data and 'files_updated' in result.data:
            files = result.data['files_updated']
            if files:
                lines.append("\n" + "="*70)
                lines.append(f"FILES UPDATED ({len(files)})")
                lines.append("="*70)
                for file in files:
                    lines.append(f"  ✓ {file}")
        
        # Files Skipped
        if result.data and 'files_skipped' in result.data:
            files = result.data['files_skipped']
            if files:
                lines.append("\n" + "="*70)
                lines.append(f"FILES SKIPPED ({len(files)})")
                lines.append("="*70)
                for file in files:
                    lines.append(f"  ⏭️  {file}")
                    lines.append(f"     (No changes detected)")
        
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
