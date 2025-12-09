"""CLI Wrappers Package

Provides command-line interface wrappers for CORTEX system operations.

Architecture:
- base_wrapper.py: Abstract base class with template pattern
- {operation}_wrapper.py: Concrete implementations

Pattern:
1. Subclass BaseCLIWrapper
2. Implement get_orchestrator() and get_operation_name()
3. Optionally override setup_argparse() and format_text_output()
4. Use main_template() for entry point

Example:
    from scripts.cli_wrappers.base_wrapper import BaseCLIWrapper, main_template
    from src.operations.my_operation import MyOrchestrator
    
    class MyOperationWrapper(BaseCLIWrapper):
        def get_orchestrator(self):
            return MyOrchestrator()
        
        def get_operation_name(self):
            return "My Operation"
    
    if __name__ == '__main__':
        sys.exit(main_template(MyOperationWrapper))

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

from .base_wrapper import BaseCLIWrapper, main_template

__all__ = ['BaseCLIWrapper', 'main_template']
