"""
Base CLI Wrapper Pattern

Provides template for creating CLI wrappers for CORTEX system operations.

Pattern:
1. Parse command-line arguments
2. Initialize orchestrator
3. Execute operation
4. Format output using response template
5. Return exit code

Features:
- Progress indicators (@with_progress decorator)
- Error handling with exit codes
- Template-based output formatting
- Consistent interface across all wrappers

Usage:
    from cortex_toolkit.cli.wrappers.base_wrapper import BaseCLIWrapper
    
    class MyOperationWrapper(BaseCLIWrapper):
        def get_orchestrator(self):
            return MyOrchestrator()
        
        def get_operation_name(self):
            return "My Operation"

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime
import logging

# Add CORTEX root to path
CORTEX_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(CORTEX_ROOT))

from src.utils.progress_decorator import with_progress
from src.operations.base_operation_module import OperationResult, OperationStatus

logger = logging.getLogger(__name__)


class BaseCLIWrapper(ABC):
    """
    Abstract base class for CLI wrappers.
    
    Subclasses must implement:
    - get_orchestrator(): Return orchestrator instance
    - get_operation_name(): Return operation name for progress display
    """
    
    def __init__(self):
        """Initialize wrapper."""
        self.args: Optional[argparse.Namespace] = None
        self.result: Optional[OperationResult] = None
        
    @abstractmethod
    def get_orchestrator(self) -> Any:
        """
        Get orchestrator instance.
        
        Returns:
            Orchestrator instance (must have execute() method)
        """
        pass
    
    @abstractmethod
    def get_operation_name(self) -> str:
        """
        Get operation name for display.
        
        Returns:
            Human-readable operation name
        """
        pass
    
    def setup_argparse(self, parser: argparse.ArgumentParser) -> None:
        """
        Configure command-line arguments.
        
        Override to add operation-specific arguments.
        
        Args:
            parser: ArgumentParser instance
        """
        parser.add_argument(
            '--output',
            choices=['text', 'json'],
            default='text',
            help='Output format (default: text)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose logging'
        )
        parser.add_argument(
            '--project-root',
            type=str,
            default='.',
            help='Project root directory (default: current directory)'
        )
    
    def parse_args(self, argv: Optional[list] = None) -> argparse.Namespace:
        """
        Parse command-line arguments.
        
        Args:
            argv: Command-line arguments (default: sys.argv)
        
        Returns:
            Parsed arguments
        """
        parser = argparse.ArgumentParser(
            description=f"CORTEX {self.get_operation_name()} CLI Wrapper"
        )
        self.setup_argparse(parser)
        self.args = parser.parse_args(argv)
        
        # Configure logging
        if self.args.verbose:
            logging.basicConfig(level=logging.DEBUG)
        
        return self.args
    
    def build_context(self) -> Dict[str, Any]:
        """
        Build context dictionary for orchestrator.
        
        Override to add operation-specific context.
        
        Returns:
            Context dictionary
        """
        return {
            'project_root': Path(self.args.project_root).resolve(),
            'cli_mode': True,
            'timestamp': datetime.now().isoformat()
        }
    
    @with_progress(operation_name="CLI Operation", threshold_seconds=3.0)
    def execute(self) -> OperationResult:
        """
        Execute operation using orchestrator.
        
        Returns:
            OperationResult from orchestrator
        """
        orchestrator = self.get_orchestrator()
        context = self.build_context()
        
        try:
            self.result = orchestrator.execute(context)
            return self.result
        except Exception as e:
            logger.exception(f"Orchestrator execution failed: {e}")
            # Create error result
            self.result = OperationResult(
                status=OperationStatus.FAILED,
                message=f"Operation failed: {str(e)}",
                data={'error': str(e)},
                errors=[str(e)]
            )
            return self.result
    
    def format_text_output(self, result: OperationResult) -> str:
        """
        Format result as human-readable text.
        
        Override for operation-specific formatting.
        
        Args:
            result: OperationResult from orchestrator
        
        Returns:
            Formatted text string
        """
        lines = []
        lines.append(f"\n{'='*60}")
        lines.append(f"  {self.get_operation_name()}")
        lines.append(f"{'='*60}\n")
        
        # Status
        status_symbol = "✓" if result.status == OperationStatus.SUCCESS else "✗"
        lines.append(f"Status: {status_symbol} {result.status.value.upper()}")
        
        # Message
        if result.message:
            lines.append(f"\n{result.message}")
        
        # Data (if present)
        if result.data:
            lines.append("\nData:")
            for key, value in result.data.items():
                if isinstance(value, (dict, list)):
                    lines.append(f"  {key}:")
                    lines.append(f"    {json.dumps(value, indent=2)}")
                else:
                    lines.append(f"  {key}: {value}")
        
        # Warnings
        if result.warnings:
            lines.append(f"\n⚠️  Warnings ({len(result.warnings)}):")
            for warning in result.warnings:
                lines.append(f"  - {warning}")
        
        # Errors
        if result.errors:
            lines.append(f"\n❌ Errors ({len(result.errors)}):")
            for error in result.errors:
                lines.append(f"  - {error}")
        
        lines.append(f"\n{'='*60}\n")
        return '\n'.join(lines)
    
    def format_json_output(self, result: OperationResult) -> str:
        """
        Format result as JSON.
        
        Args:
            result: OperationResult from orchestrator
        
        Returns:
            JSON string
        """
        output = {
            'operation': self.get_operation_name(),
            'status': result.status.value,
            'message': result.message,
            'data': result.data,
            'warnings': result.warnings,
            'errors': result.errors,
            'timestamp': datetime.now().isoformat()
        }
        return json.dumps(output, indent=2)
    
    def output_result(self, result: OperationResult) -> None:
        """
        Output result to console.
        
        Args:
            result: OperationResult from orchestrator
        """
        if self.args.output == 'json':
            print(self.format_json_output(result))
        else:
            print(self.format_text_output(result))
    
    def get_exit_code(self, result: OperationResult) -> int:
        """
        Get exit code based on result.
        
        Args:
            result: OperationResult from orchestrator
        
        Returns:
            Exit code (0 = success, 1 = failure)
        """
        return 0 if result.status == OperationStatus.SUCCESS else 1
    
    def run(self, argv: Optional[list] = None) -> int:
        """
        Main entry point for CLI wrapper.
        
        Args:
            argv: Command-line arguments (default: sys.argv)
        
        Returns:
            Exit code (0 = success, 1 = failure)
        """
        try:
            # Parse arguments
            self.parse_args(argv)
            
            # Execute operation
            result = self.execute()
            
            # Output result
            self.output_result(result)
            
            # Return exit code
            return self.get_exit_code(result)
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Operation cancelled by user")
            return 130  # Standard exit code for SIGINT
        except Exception as e:
            logger.exception(f"CLI wrapper failed: {e}")
            print(f"\n❌ Fatal error: {str(e)}")
            return 1


def main_template(wrapper_class: type) -> int:
    """
    Template main() function for CLI wrappers.
    
    Usage:
        if __name__ == '__main__':
            sys.exit(main_template(MyOperationWrapper))
    
    Args:
        wrapper_class: CLI wrapper class (subclass of BaseCLIWrapper)
    
    Returns:
        Exit code
    """
    wrapper = wrapper_class()
    return wrapper.run()
