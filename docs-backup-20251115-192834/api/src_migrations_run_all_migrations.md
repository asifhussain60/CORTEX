# src.migrations.run_all_migrations

CORTEX Master Migration Runner
Orchestrates all three tier migrations in sequence

Sub-Group 3A: Phase 0.5 - Migration Tools

## Functions

### `run_command(cmd, description)`

Run a command and return success status

Args:
    cmd: Command to run as list
    description: Description of what's being done
    
Returns:
    True if successful, False otherwise
