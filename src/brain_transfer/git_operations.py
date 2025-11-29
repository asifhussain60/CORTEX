#!/usr/bin/env python3
"""
Git Operations Module for Brain Transfer

Provides Git integration for automatic brain export/import synchronization.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import subprocess
import yaml
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class GitOperations:
    """Git operations for brain transfer automation."""
    
    def __init__(self, repo_path: Optional[Path] = None):
        """
        Initialize Git operations.
        
        Args:
            repo_path: Path to git repository (defaults to current directory)
        """
        self.repo_path = repo_path or Path.cwd()
    
    def is_git_repo(self) -> bool:
        """
        Check if current directory is in a git repository.
        
        Returns:
            True if in git repo, False otherwise
        """
        try:
            subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                cwd=self.repo_path,
                capture_output=True,
                check=True,
                text=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def get_current_branch(self) -> str:
        """
        Get current git branch name.
        
        Returns:
            Branch name
            
        Raises:
            RuntimeError: If not in git repo or command fails
        """
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.repo_path,
                capture_output=True,
                check=True,
                text=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get current branch: {e.stderr}")
    
    def git_add(self, file_path: Path) -> None:
        """
        Stage file for commit.
        
        Args:
            file_path: Path to file to stage
            
        Raises:
            RuntimeError: If git add fails
        """
        try:
            subprocess.run(
                ['git', 'add', str(file_path)],
                cwd=self.repo_path,
                capture_output=True,
                check=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to stage file: {e.stderr}")
    
    def git_commit(self, message: str) -> None:
        """
        Commit staged changes.
        
        Args:
            message: Commit message
            
        Raises:
            RuntimeError: If git commit fails
        """
        try:
            subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=self.repo_path,
                capture_output=True,
                check=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            # Check if it's "nothing to commit" - not an error
            if "nothing to commit" in e.stderr.lower():
                return
            raise RuntimeError(f"Failed to commit: {e.stderr}")
    
    def git_push(self, branch: Optional[str] = None) -> None:
        """
        Push to remote repository.
        
        Args:
            branch: Branch to push (defaults to current branch)
            
        Raises:
            RuntimeError: If git push fails
        """
        if branch is None:
            branch = self.get_current_branch()
        
        try:
            subprocess.run(
                ['git', 'push', 'origin', branch],
                cwd=self.repo_path,
                capture_output=True,
                check=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to push to remote: {e.stderr}")
    
    def git_pull(self, branch: Optional[str] = None) -> None:
        """
        Pull from remote repository.
        
        Args:
            branch: Branch to pull (defaults to current branch)
            
        Raises:
            RuntimeError: If git pull fails
        """
        if branch is None:
            branch = self.get_current_branch()
        
        try:
            subprocess.run(
                ['git', 'pull', 'origin', branch],
                cwd=self.repo_path,
                capture_output=True,
                check=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to pull from remote: {e.stderr}")
    
    def generate_commit_message(self, export_file: Path) -> str:
        """
        Generate smart commit message from export YAML.
        
        Args:
            export_file: Path to brain export YAML file
            
        Returns:
            Formatted commit message
        """
        try:
            with open(export_file, 'r') as f:
                data = yaml.safe_load(f)
            
            metadata = data.get('metadata', {})
            patterns = data.get('patterns', [])
            
            scope = metadata.get('scope', 'unknown')
            pattern_count = len(patterns)
            
            # Extract primary namespaces
            namespaces = set()
            for pattern in patterns[:10]:  # Sample first 10
                namespace = pattern.get('namespace', '')
                if namespace:
                    # Extract first segment (e.g., "workspace.authentication" -> "authentication")
                    parts = namespace.split('.')
                    if len(parts) > 1:
                        namespaces.add(parts[1])
            
            namespace_str = ', '.join(sorted(namespaces)[:3]) if namespaces else 'general'
            
            return f"brain: Share {pattern_count} {scope} patterns ({namespace_str})"
            
        except Exception as e:
            # Fallback to generic message
            timestamp = datetime.now().strftime('%Y-%m-%d')
            return f"brain: Share patterns ({timestamp})"
    
    def scan_unprocessed_exports(
        self,
        exports_dir: Path,
        import_history_file: Optional[Path] = None
    ) -> List[Path]:
        """
        Scan exports directory for unprocessed YAML files.
        
        Args:
            exports_dir: Directory containing brain exports
            import_history_file: File tracking imported exports (optional)
            
        Returns:
            List of unprocessed export files, sorted by timestamp
        """
        # Get all YAML files in exports directory
        yaml_files = sorted(exports_dir.glob('brain-export-*.yaml'))
        
        if not import_history_file or not import_history_file.exists():
            # No history - all files are unprocessed
            return yaml_files
        
        # Read import history
        try:
            with open(import_history_file, 'r') as f:
                imported = set(f.read().splitlines())
        except Exception:
            imported = set()
        
        # Filter to unprocessed files only
        unprocessed = [f for f in yaml_files if f.name not in imported]
        
        return unprocessed
    
    def mark_as_processed(
        self,
        export_file: Path,
        import_history_file: Path
    ) -> None:
        """
        Mark export file as processed in import history.
        
        Args:
            export_file: Export file that was imported
            import_history_file: File tracking imported exports
        """
        import_history_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(import_history_file, 'a') as f:
            f.write(f"{export_file.name}\n")
    
    def has_uncommitted_changes(self) -> bool:
        """
        Check if repository has uncommitted changes.
        
        Returns:
            True if there are uncommitted changes, False otherwise
        """
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.repo_path,
                capture_output=True,
                check=True,
                text=True
            )
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError:
            return False


# Convenience functions for backward compatibility
def is_git_repo(repo_path: Optional[Path] = None) -> bool:
    """Check if in git repository."""
    return GitOperations(repo_path).is_git_repo()


def get_current_branch(repo_path: Optional[Path] = None) -> str:
    """Get current git branch."""
    return GitOperations(repo_path).get_current_branch()


def generate_commit_message(export_file: Path) -> str:
    """Generate smart commit message from export."""
    return GitOperations().generate_commit_message(export_file)


def scan_unprocessed_exports(
    exports_dir: Path,
    import_history_file: Optional[Path] = None
) -> List[Path]:
    """Scan for unprocessed exports."""
    return GitOperations().scan_unprocessed_exports(exports_dir, import_history_file)
