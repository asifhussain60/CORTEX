#!/usr/bin/env python3
"""
CORTEX Optimize CLI Wrapper

Command-line interface for CORTEX system optimization.

Features:
- SKULL tests execution (brain protection validation)
- Architecture analysis and review
- Pattern learning from Knowledge Graph
- Optimization planning and execution
- Metrics collection and reporting
- Git tracking for all changes

Usage:
    python scripts/cli_wrappers/optimize_wrapper.py
    python scripts/cli_wrappers/optimize_wrapper.py --output json
    python scripts/cli_wrappers/optimize_wrapper.py --verbose

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import sys
from pathlib import Path

# Add CORTEX root to path
CORTEX_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(CORTEX_ROOT))

from .base_wrapper import BaseCLIWrapper, main_template
from src.operations.modules.optimization.optimize_cortex_orchestrator import OptimizeCortexOrchestrator


class OptimizeWrapper(BaseCLIWrapper):
    """CLI wrapper for CORTEX optimization."""
    
    def get_orchestrator(self):
        """Get optimize orchestrator."""
        return OptimizeCortexOrchestrator(project_root=Path(self.args.project_root))
    
    def get_operation_name(self) -> str:
        """Get operation name."""
        return "CORTEX Optimize"
    
    def format_text_output(self, result) -> str:
        """Format optimize result as human-readable text."""
        from src.operations.base_operation_module import OperationStatus
        
        lines = []
        lines.append(f"\n{'='*70}")
        lines.append(f"  ⚡ CORTEX Optimize")
        lines.append(f"{'='*70}\n")
        
        # Status
        if result.status == OperationStatus.SUCCESS:
            lines.append("Status: ✓ SUCCESS")
        else:
            lines.append("Status: ✗ FAILED")
        
        # Message
        if result.message:
            lines.append(f"\n{result.message}")
        
        # Metrics
        if result.data and 'metrics' in result.data:
            lines.append("\n" + "="*70)
            lines.append("OPTIMIZATION METRICS")
            lines.append("="*70)
            
            metrics = result.data['metrics']
            if isinstance(metrics, dict):
                for key, value in metrics.items():
                    if isinstance(value, (int, float, str)):
                        lines.append(f"  {key}: {value}")
        
        # Optimizations Applied
        if result.data and 'optimizations_applied' in result.data:
            optimizations = result.data['optimizations_applied']
            if optimizations:
                lines.append("\n" + "="*70)
                lines.append(f"OPTIMIZATIONS APPLIED ({len(optimizations)})")
                lines.append("="*70)
                for opt in optimizations:
                    if isinstance(opt, dict):
                        title = opt.get('title', 'Unknown')
                        lines.append(f"  ✓ {title}")
                    else:
                        lines.append(f"  ✓ {opt}")
        
        # Git Commits
        if result.data and 'git_commits' in result.data:
            commits = result.data['git_commits']
            if commits:
                lines.append("\n" + "="*70)
                lines.append(f"GIT COMMITS ({len(commits)})")
                lines.append("="*70)
                for commit in commits:
                    lines.append(f"  {commit}")
        
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
    sys.exit(main_template(OptimizeWrapper))
