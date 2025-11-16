# src.config

CORTEX Configuration Management

Handles cross-platform path resolution and configuration loading.
Supports development on multiple machines with different paths.

Machine Detection:
- Automatically detects current machine based on hostname or path
- Falls back to environment variables if cortex.config.json not found
- Uses relative paths as final fallback

Usage:
    from src.config import config
    
    # Get brain path (automatically resolved for current machine)
    brain_path = config.brain_path
    
    # Get project root
    root = config.root_path
    
    # Check if running in development mode
    if config.is_development:
        print("Development mode active")

## Functions

### `get_brain_path()`

Get cortex-brain path for current machine.

### `get_root_path()`

Get CORTEX root path for current machine.
