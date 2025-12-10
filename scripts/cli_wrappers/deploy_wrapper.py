#!/usr/bin/env python3
"""
CORTEX Deploy CLI Wrapper

Command-line interface for CORTEX production deployment.

Features:
- Build clean production package
- Publish to downloadable repository
- Deployment gate validation
- Git branch management
- Safety checks and rollback

Usage:
    python scripts/cli_wrappers/deploy_wrapper.py
    python scripts/cli_wrappers/deploy_wrapper.py --dry-run
    python scripts/cli_wrappers/deploy_wrapper.py --output json

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

from scripts.cli_wrappers.base_wrapper import BaseCLIWrapper, main_template
from src.operations.modules.deploy.deploy_utility import deploy_to_production
from src.operations.base_operation_module import OperationResult, OperationStatus


class DeployWrapper(BaseCLIWrapper):
    """CLI wrapper for CORTEX deployment."""
    
    def get_orchestrator(self):
        """
        Get deployment executor.
        
        Note: deploy_to_production is a function, not a class.
        We'll wrap it in a simple executor.
        """
        class DeployExecutor:
            def __init__(self, cortex_root: Path, dry_run: bool = False):
                self.cortex_root = cortex_root
                self.dry_run = dry_run
            
            def execute(self, context):
                """Execute deployment."""
                result = deploy_to_production(
                    cortex_root=self.cortex_root,
                    dry_run=self.dry_run
                )
                
                # Convert dict result to OperationResult
                status = OperationStatus.SUCCESS if result.get('success', False) else OperationStatus.FAILED
                
                message_parts = []
                if result.get('success'):
                    message_parts.append("Deployment completed successfully")
                else:
                    message_parts.append("Deployment failed")
                
                if 'package_path' in result:
                    message_parts.append(f"Package: {result['package_path']}")
                
                return OperationResult(
                    success=result.get('success', False),
                    status=status,
                    message='\n'.join(message_parts),
                    data=result,
                    warnings=result.get('warnings', []),
                    errors=result.get('errors', [])
                )
        
        return DeployExecutor(
            cortex_root=CORTEX_ROOT,
            dry_run=getattr(self.args, 'dry_run', False)
        )
    
    def get_operation_name(self) -> str:
        """Get operation name."""
        return "CORTEX Deploy"
    
    def setup_argparse(self, parser: argparse.ArgumentParser) -> None:
        """Configure command-line arguments."""
        super().setup_argparse(parser)
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview deployment without applying changes'
        )
    
    def format_text_output(self, result) -> str:
        """Format deployment result as human-readable text."""
        lines = []
        lines.append(f"\n{'='*70}")
        lines.append(f"  🚀 CORTEX Deploy")
        lines.append(f"{'='*70}\n")
        
        # Status
        if result.status == OperationStatus.SUCCESS:
            lines.append("Status: ✓ SUCCESS")
        else:
            lines.append("Status: ✗ FAILED")
        
        # Message
        if result.message:
            lines.append(f"\n{result.message}")
        
        # Package Info
        if result.data:
            if 'package_path' in result.data:
                lines.append("\n" + "="*70)
                lines.append("PACKAGE INFO")
                lines.append("="*70)
                lines.append(f"  Path: {result.data['package_path']}")
            
            if 'package_size' in result.data:
                lines.append(f"  Size: {result.data['package_size']}")
            
            if 'git_commit' in result.data:
                lines.append(f"  Commit: {result.data['git_commit']}")
            
            if 'branch' in result.data:
                lines.append(f"  Branch: {result.data['branch']}")
        
        # Deployment Gates
        if result.data and 'gates_passed' in result.data:
            lines.append("\n" + "="*70)
            lines.append("DEPLOYMENT GATES")
            lines.append("="*70)
            
            gates = result.data.get('gates_passed', [])
            if gates:
                for gate in gates:
                    lines.append(f"  ✓ {gate}")
        
        # Files Deployed
        if result.data and 'files_deployed' in result.data:
            files = result.data['files_deployed']
            if files:
                lines.append("\n" + "="*70)
                lines.append(f"FILES DEPLOYED ({len(files)})")
                lines.append("="*70)
                for file in files[:20]:  # Show top 20
                    lines.append(f"  {file}")
                
                if len(files) > 20:
                    lines.append(f"  ... and {len(files) - 20} more")
        
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
    sys.exit(main_template(DeployWrapper))
