#!/usr/bin/env python3
"""
CORTEX Onboarding CLI Wrapper

Entry point for `cortex onboarding` command.
Provides CLI interface to the interactive onboarding script.

Usage:
    python scripts/cli_wrappers/onboarding_wrapper.py
    python scripts/cli_wrappers/onboarding_wrapper.py --phase 3
    python scripts/cli_wrappers/onboarding_wrapper.py --resume
    python scripts/cli_wrappers/onboarding_wrapper.py --output json

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import sys
import argparse
import json
import subprocess
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

# Add CORTEX root to path
CORTEX_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(CORTEX_ROOT))

from scripts.cli_wrappers.base_wrapper import BaseCLIWrapper


class OnboardingWrapper(BaseCLIWrapper):
    """CLI wrapper for CORTEX onboarding."""
    
    def get_orchestrator(self) -> Any:
        """Get onboarding orchestrator (via subprocess)."""
        # Onboarding runs as subprocess for terminal interaction
        return None
    
    def get_operation_name(self) -> str:
        """Get operation name."""
        return "CORTEX Onboarding"
    
    def setup_argparse(self, parser: argparse.ArgumentParser) -> None:
        """Configure arguments."""
        super().setup_argparse(parser)
        
        parser.add_argument(
            '--phase',
            type=int,
            choices=range(1, 7),
            help='Start from specific phase (1-6)'
        )
        
        parser.add_argument(
            '--resume',
            action='store_true',
            help='Resume from last saved progress'
        )
        
        parser.add_argument(
            '--profile',
            choices=['full', 'quick', 'concepts', 'tdd'],
            default='full',
            help='Onboarding profile (default: full)'
        )
    
    def execute(self) -> Dict[str, Any]:
        """Execute onboarding via subprocess."""
        # Build command
        script_path = CORTEX_ROOT / "cortex-toolkit" / "core" / "utilities" / "onboarding_interactive.py"
        
        cmd = [sys.executable, str(script_path)]
        
        # Add arguments
        if self.args.phase:
            cmd.extend(['--phase', str(self.args.phase)])
        
        if self.args.resume:
            cmd.append('--resume')
        
        # Execute in interactive mode (inherit terminal)
        try:
            result = subprocess.run(
                cmd,
                cwd=str(CORTEX_ROOT),
                check=False  # Don't raise on non-zero exit
            )
            
            success = result.returncode == 0
            
            return {
                'success': success,
                'message': 'Onboarding completed' if success else 'Onboarding interrupted',
                'exit_code': result.returncode,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Onboarding failed: {str(e)}',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def format_text_output(self, result: Dict[str, Any]) -> str:
        """Format text output."""
        output = []
        output.append("")
        output.append("=" * 70)
        output.append("  🎓 CORTEX Onboarding")
        output.append("=" * 70)
        output.append("")
        
        if result['success']:
            output.append("✅ Onboarding completed successfully!")
        else:
            output.append("⚠️  Onboarding interrupted or failed")
        
        output.append("")
        output.append(f"Message: {result['message']}")
        output.append(f"Timestamp: {result['timestamp']}")
        
        if not result['success'] and 'error' in result:
            output.append("")
            output.append(f"Error: {result['error']}")
        
        output.append("")
        output.append("=" * 70)
        output.append("")
        
        return "\n".join(output)
    
    def format_json_output(self, result: Dict[str, Any]) -> str:
        """Format JSON output."""
        return json.dumps(result, indent=2)


def main():
    """Main entry point."""
    wrapper = OnboardingWrapper()
    parser = argparse.ArgumentParser(
        description="CORTEX Interactive Onboarding - 6-phase guided tour",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start full onboarding
  python scripts/cli_wrappers/onboarding_wrapper.py
  
  # Start from Phase 3
  python scripts/cli_wrappers/onboarding_wrapper.py --phase 3
  
  # Resume previous session
  python scripts/cli_wrappers/onboarding_wrapper.py --resume
  
  # Quick start only
  python scripts/cli_wrappers/onboarding_wrapper.py --profile quick
  
  # JSON output
  python scripts/cli_wrappers/onboarding_wrapper.py --output json

Phases:
  1. Quick Start (5 min) - Install and verify
  2. Core Concepts (10 min) - 4-tier brain & SKULL
  3. First Planning (15 min) - Create your first plan
  4. TDD Workflow (20 min) - Master RED→GREEN→REFACTOR
  5. Documentation (5 min) - Navigate resources
  6. Common Operations (10 min) - Practice commands

For more information, visit:
  https://asifhussain60.github.io/CORTEX/
"""
    )
    
    wrapper.setup_argparse(parser)
    wrapper.args = parser.parse_args()
    
    # Execute
    result = wrapper.execute()
    
    # Format output
    if wrapper.args.output == 'json':
        print(wrapper.format_json_output(result))
    else:
        print(wrapper.format_text_output(result))
    
    # Return exit code
    sys.exit(0 if result['success'] else 1)


if __name__ == '__main__':
    main()
