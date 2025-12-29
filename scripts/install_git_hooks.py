#!/usr/bin/env python3
"""
Install Git Hooks for CORTEX 4.0

Installs pre-commit hook that enforces:
- Migration activation validation
- Legacy 3.0 cleanup
- Documents bloat tracking

Usage:
    python scripts/install_git_hooks.py
"""

import shutil
import sys
from pathlib import Path


def install_hooks():
    """Install git hooks"""
    repo_root = Path(__file__).parent.parent
    hooks_dir = repo_root / ".git/hooks"
    
    if not hooks_dir.exists():
        print("❌ .git/hooks directory not found")
        print("Are you in a git repository?")
        return False
    
    # Copy pre-commit hook
    source = repo_root / "scripts/pre-commit"
    dest = hooks_dir / "pre-commit"
    
    try:
        shutil.copy2(source, dest)
        dest.chmod(0o755)  # Make executable
        print(f"✅ Installed pre-commit hook: {dest}")
        
        # Test hook
        print("\n🧪 Testing hook...")
        import subprocess
        result = subprocess.run([sys.executable, str(dest)], capture_output=True)
        
        if result.returncode == 0:
            print("✅ Hook test passed")
        else:
            print("⚠️  Hook test failed (expected if migrations not all activated)")
            print("Run: python scripts/validate_migration_activation.py --all")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to install hook: {e}")
        return False


if __name__ == '__main__':
    success = install_hooks()
    sys.exit(0 if success else 1)
