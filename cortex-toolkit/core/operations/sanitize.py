"""
CORTEX System Operation: Sanitize

This is a delegator to the CLI wrapper in the toolkit.
For the actual implementation, see: cortex-toolkit/cli/wrappers/sanitize_wrapper.py
"""
import sys
from pathlib import Path

# Add toolkit to path
toolkit_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(toolkit_root))

# Import and delegate to wrapper
from cli.wrappers.base_wrapper import main_template
from cli.wrappers.sanitize_wrapper import SanitizeWrapper

if __name__ == '__main__':
    sys.exit(main_template(SanitizeWrapper))
