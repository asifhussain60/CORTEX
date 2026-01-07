"""
CORTEX Brain Operation: Optimize

This is a delegator to the CLI wrapper in the toolkit.
For the actual implementation, see: cortex-toolkit/cli/wrappers/optimize_wrapper.py
"""
import sys
from pathlib import Path

# Add toolkit to path
toolkit_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(toolkit_root))

# Import and delegate to wrapper
from cli.wrappers.base_wrapper import main_template
from cli.wrappers.optimize_wrapper import OptimizeWrapper

if __name__ == '__main__':
    sys.exit(main_template(OptimizeWrapper))
