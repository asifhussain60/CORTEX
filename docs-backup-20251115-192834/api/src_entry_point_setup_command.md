# src.entry_point.setup_command

CORTEX Setup Command

This module implements the "setup" command that initializes CORTEX in a new repository.
It systematically:
1. Installs all required tooling
2. Initializes the CORTEX brain structure
3. Runs crawlers to feed the brain
4. Introduces CORTEX to the user with links to documentation

Usage:
    from CORTEX.src.entry_point.setup_command import CortexSetup
    
    setup = CortexSetup()
    setup.run()

## Functions

### `run_setup(repo_path, brain_path, verbose)`

Convenience function to run CORTEX setup.

Args:
    repo_path: Path to repository (default: current directory)
    brain_path: Path for CORTEX brain (default: repo/cortex-brain)
    verbose: Show detailed output
    
Returns:
    Setup results dictionary
