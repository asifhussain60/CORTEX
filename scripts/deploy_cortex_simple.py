#!/usr/bin/env python3
"""
CORTEX Simplified Deployment Script

Deploys CORTEX to main branch using git worktree approach.
Radically simpler than deploy_cortex.py - no temp directories, no checkpoints, no rebuilds.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import subprocess
import sys
import shutil
from pathlib import Path
from typing import List, Set


def run_command(cmd: List[str], cwd: Path = None, check: bool = True) -> subprocess.CompletedProcess:
    """Run shell command and return result."""
    return subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True)


def get_exclude_patterns() -> Set[str]:
    """Get patterns to exclude from deployment."""
    return {
        'cortex-brain',
        '.git',
        'tests',
        '.pytest_cache',
        '__pycache__',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.vscode',
        '.idea',
        'venv',
        '.env',
        '.main-worktree',
        '.temp-publish',
        '.publish-checkpoint.json',
        'node_modules',
        '.DS_Store',
        'Thumbs.db'
    }


def should_exclude(path: Path, exclude_patterns: Set[str]) -> bool:
    """Check if path matches any exclude pattern."""
    for pattern in exclude_patterns:
        if pattern.startswith('*'):
            # Extension pattern
            if path.suffix == pattern[1:]:
                return True
        else:
            # Directory or exact name pattern
            if pattern in path.parts:
                return True
    return False


def copy_files(source: Path, dest: Path, exclude_patterns: Set[str]) -> tuple[int, int]:
    """Copy files from source to dest, excluding patterns.
    
    Returns: (file_count, total_size_bytes)
    """
    file_count = 0
    total_size = 0
    
    for item in source.rglob('*'):
        if item.is_file() and not should_exclude(item, exclude_patterns):
            # Calculate relative path
            rel_path = item.relative_to(source)
            dest_path = dest / rel_path
            
            # Create parent directory
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(item, dest_path)
            file_count += 1
            total_size += item.stat().st_size
    
    return file_count, total_size


def merge_copilot_instructions(main_worktree: Path, cortex_root: Path) -> None:
    """Merge CORTEX instructions into existing copilot-instructions.md.
    
    Handles 3 scenarios:
    1. No existing file - copy CORTEX file as-is
    2. Existing file without CORTEX - append CORTEX section
    3. Existing file with CORTEX - update existing CORTEX section
    """
    cortex_instructions = cortex_root / ".github" / "copilot-instructions.md"
    target_instructions = main_worktree / ".github" / "copilot-instructions.md"
    
    if not cortex_instructions.exists():
        print("⚠️  CORTEX copilot-instructions.md not found - skipping merge")
        return
    
    # Read CORTEX instructions
    with open(cortex_instructions, 'r', encoding='utf-8') as f:
        cortex_content = f.read()
    
    # Markers for CORTEX section
    cortex_start_marker = "# GitHub Copilot Instructions for CORTEX"
    cortex_end_marker = "**License:** Source-Available (Use Allowed, No Contributions)"
    
    if not target_instructions.exists():
        # Scenario 1: No existing file - create new
        print("  ✅ No existing copilot-instructions.md - creating new")
        target_instructions.parent.mkdir(parents=True, exist_ok=True)
        with open(target_instructions, 'w', encoding='utf-8') as f:
            f.write(cortex_content)
        return
    
    # Read existing file
    with open(target_instructions, 'r', encoding='utf-8') as f:
        existing_content = f.read()
    
    if cortex_start_marker in existing_content:
        # Scenario 3: CORTEX section exists - update it
        print("  ✅ Existing CORTEX section found - updating")
        
        start_idx = existing_content.find(cortex_start_marker)
        end_idx = existing_content.find(cortex_end_marker, start_idx)
        
        if end_idx != -1:
            # Find end of line after end marker
            end_idx = existing_content.find('\n', end_idx) + 1
            
            # Extract CORTEX section from source
            cortex_start = cortex_content.find(cortex_start_marker)
            cortex_end = cortex_content.find(cortex_end_marker, cortex_start)
            cortex_end = cortex_content.find('\n', cortex_end) + 1
            cortex_section = cortex_content[cortex_start:cortex_end]
            
            # Replace section
            merged_content = (
                existing_content[:start_idx] +
                cortex_section +
                existing_content[end_idx:]
            )
            
            with open(target_instructions, 'w', encoding='utf-8') as f:
                f.write(merged_content)
        else:
            print("  ⚠️  Could not find end marker - appending CORTEX section")
            # Fallback to append
            with open(target_instructions, 'a', encoding='utf-8') as f:
                f.write('\n\n' + cortex_content)
    else:
        # Scenario 2: No CORTEX section - append it
        print("  ✅ No CORTEX section found - appending")
        with open(target_instructions, 'a', encoding='utf-8') as f:
            f.write('\n\n' + cortex_content)


def deploy_cortex() -> int:
    """Deploy CORTEX to main branch using git worktree.
    
    Returns: 0 on success, 1 on failure
    """
    cortex_root = Path(__file__).parent.parent
    main_worktree = cortex_root / '.main-worktree'
    
    print("🚀 CORTEX Simplified Deployment")
    print(f"📂 CORTEX root: {cortex_root}")
    print(f"📂 Main worktree: {main_worktree}")
    print()
    
    try:
        # Step 1: Clean up any existing worktree
        if main_worktree.exists():
            print("🧹 Cleaning up existing worktree...")
            run_command(['git', 'worktree', 'remove', '--force', str(main_worktree)], cwd=cortex_root, check=False)
            if main_worktree.exists():
                shutil.rmtree(main_worktree)
        
        # Step 2: Create worktree for main branch
        print("📦 Creating worktree for main branch...")
        run_command(['git', 'worktree', 'add', str(main_worktree), 'main'], cwd=cortex_root)
        print("  ✅ Worktree created")
        print()
        
        # Step 3: Copy files to main worktree
        print("📋 Copying files to main worktree...")
        exclude_patterns = get_exclude_patterns()
        file_count, total_size = copy_files(cortex_root, main_worktree, exclude_patterns)
        print(f"  ✅ Copied {file_count} files ({total_size / (1024*1024):.2f} MB)")
        print()
        
        # Step 4: Merge copilot-instructions.md
        print("🔀 Merging copilot-instructions.md...")
        merge_copilot_instructions(main_worktree, cortex_root)
        print()
        
        # Step 5: Commit changes
        print("💾 Committing changes to main branch...")
        run_command(['git', 'add', '.'], cwd=main_worktree)
        
        # Check if there are changes to commit
        status = run_command(['git', 'status', '--porcelain'], cwd=main_worktree)
        if status.stdout.strip():
            run_command([
                'git', 'commit', '-m', 
                f'Deploy CORTEX 3.2.0\n\nDeployed {file_count} files ({total_size / (1024*1024):.2f} MB)'
            ], cwd=main_worktree)
            print("  ✅ Changes committed")
        else:
            print("  ℹ️  No changes to commit")
        print()
        
        # Step 6: Push to origin
        print("☁️  Pushing to origin/main...")
        run_command(['git', 'push', 'origin', 'main'], cwd=main_worktree)
        print("  ✅ Pushed to origin")
        print()
        
        # Step 7: Cleanup worktree
        print("🧹 Cleaning up worktree...")
        run_command(['git', 'worktree', 'remove', str(main_worktree)], cwd=cortex_root)
        print("  ✅ Worktree removed")
        print()
        
        print("✨ DEPLOYMENT COMPLETE!")
        print()
        print("📦 Users can now clone with:")
        print("   git clone -b main --single-branch https://github.com/asifhussain60/CORTEX.git")
        print()
        
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Command failed: {' '.join(e.cmd)}")
        print(f"   Error: {e.stderr}")
        return 1
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        return 1
    finally:
        # Ensure cleanup even on failure
        if main_worktree.exists():
            print("\n🧹 Final cleanup...")
            run_command(['git', 'worktree', 'remove', '--force', str(main_worktree)], cwd=cortex_root, check=False)
            if main_worktree.exists():
                shutil.rmtree(main_worktree)


if __name__ == '__main__':
    sys.exit(deploy_cortex())
