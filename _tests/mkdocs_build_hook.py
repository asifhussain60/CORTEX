#!/usr/bin/env python3
"""
MkDocs Build Plugin: Automatic Logo Dimension Testing

Integrates pytest logo tests into the mkdocs build process.
Ensures logo assets are valid before documentation deployment.

Usage:
    Add to mkdocs.yml plugins section:
    
    plugins:
      - search
      - build-docs
    
    or run manually:
        python docs/_tests/mkdocs_build_hook.py

Reference: docs/_tests/test_logo_dimensions.py
"""

import sys
import subprocess
from pathlib import Path
import json
from datetime import datetime


def run_logo_tests(docs_root: Path, verbose: bool = True) -> bool:
    """
    Run logo dimension tests as part of mkdocs build.
    
    Args:
        docs_root: Path to docs directory
        verbose: Enable verbose output
        
    Returns:
        bool: True if all tests passed, False otherwise
    """
    
    test_dir = docs_root / "_tests"
    
    if not test_dir.exists():
        print(f"❌ Logo tests not found: {test_dir}")
        return False
    
    print("\n" + "="*70)
    print("🎨 CORTEX Logo Dimension Validation")
    print("="*70)
    
    # Prepare pytest command
    pytest_args = [
        sys.executable, "-m", "pytest",
        str(test_dir / "test_logo_dimensions.py"),
        "-v" if verbose else "-q",
        "-m", "logo",
        "--tb=short",
        "--color=yes",
        f"--mkdocs-build",
    ]
    
    # Run tests
    try:
        result = subprocess.run(
            pytest_args,
            cwd=docs_root.parent,  # Run from project root
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print("\n✅ Logo validation PASSED")
            print("="*70)
            return True
        else:
            print("\n❌ Logo validation FAILED")
            print("="*70)
            return False
            
    except FileNotFoundError:
        print(f"❌ pytest not found. Install with: pip install pytest pillow")
        return False
    except Exception as e:
        print(f"❌ Error running logo tests: {e}")
        return False


def main():
    """Main entry point for logo validation."""
    
    # Determine paths
    script_dir = Path(__file__).parent
    docs_root = script_dir.parent
    
    print(f"📁 Documentation root: {docs_root}")
    print(f"🧪 Test directory: {script_dir}")
    
    # Run tests
    success = run_logo_tests(docs_root, verbose=True)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
