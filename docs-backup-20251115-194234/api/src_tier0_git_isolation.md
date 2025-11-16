# src.tier0.git_isolation

CORTEX Git Isolation Enforcement
Prevents CORTEX source code from being committed to user application repositories.

This module:
1. Installs git hooks in user repos to block CORTEX code commits
2. Scans staged files for CORTEX paths
3. Provides clear error messages and alternatives

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file

## Functions

### `install_git_isolation_hooks(user_repo_path)`

Install git hooks to enforce CORTEX isolation.

This is called during 'cortex init' setup process.

Args:
    user_repo_path: Path to user's application repository
    
Returns:
    True if hooks installed successfully

### `check_git_isolation(user_repo_path)`

Check if staged files violate git isolation.

Args:
    user_repo_path: Path to user's application repository
    
Returns:
    (is_safe, violations) tuple
