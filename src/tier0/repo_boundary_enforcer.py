"""
Repo Boundary Enforcer

Enforces strict isolation between repositories in multi-repo workspaces.
Prevents cross-repo imports, state sharing, and cortex-implants leakage.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

from pathlib import Path
from typing import Dict, Optional, Set, List
import logging
import json

logger = logging.getLogger(__name__)


class RepoBoundaryViolation(Exception):
    """Exception raised when repo boundary is violated."""
    pass


class RepoBoundaryEnforcer:
    """
    Enforces forbidden boundaries between repositories.
    
    Rules:
    1. No cross-repo imports (cannot import code from another repo)
    2. No shared state between repos (no shared files/databases)
    3. Each repo's .cortex-implants is invisible to other repos
    4. CORTEX repo is read-only for user repos (can use, can't modify)
    5. No hardcoded paths to other repos
    
    Features:
    - Auto-detection of repo boundaries
    - Import path validation
    - File operation interception
    - Violation logging and reporting
    
    Usage:
        enforcer = RepoBoundaryEnforcer(workspace_root)
        enforcer.validate_operation(
            source_repo=Path("/workspace/frontend"),
            target_path=Path("/workspace/backend/src/models.py"),
            operation="import"
        )
    """
    
    def __init__(self, workspace_root: Path):
        """
        Initialize repo boundary enforcer.
        
        Args:
            workspace_root: VS Code workspace root containing multiple repos
        """
        self.workspace_root = Path(workspace_root).resolve()
        self.repos: Dict[str, Path] = {}  # repo_name -> repo_path
        self.cortex_repo: Optional[Path] = None
        self.violations_log: List[Dict] = []
        
        self._discover_repos()
    
    def _discover_repos(self) -> None:
        """
        Discover all repositories in workspace.
        
        A folder is considered a repo if it has:
        - .git/ folder OR
        - .cortex-implants/ folder OR
        - cortex-brain/ folder (for CORTEX itself)
        """
        logger.info(f"🔍 Discovering repos in {self.workspace_root}")
        
        # Find .git folders (repos)
        for git_dir in self.workspace_root.rglob('.git'):
            if git_dir.is_dir():
                repo_path = git_dir.parent
                repo_name = repo_path.name
                self.repos[repo_name] = repo_path
                logger.debug(f"  📦 Found repo: {repo_name}")
        
        # Find .cortex-implants folders (repos without .git)
        for implants_dir in self.workspace_root.rglob('.cortex-implants'):
            if implants_dir.is_dir():
                repo_path = implants_dir.parent
                repo_name = repo_path.name
                if repo_name not in self.repos:
                    self.repos[repo_name] = repo_path
                    logger.debug(f"  📦 Found company repo: {repo_name}")
        
        # Find CORTEX repo (has cortex-brain/)
        for cortex_brain_dir in self.workspace_root.rglob('cortex-brain'):
            if cortex_brain_dir.is_dir():
                repo_path = cortex_brain_dir.parent
                repo_name = repo_path.name
                self.cortex_repo = repo_path
                self.repos[repo_name] = repo_path
                logger.debug(f"  🧠 Found CORTEX repo: {repo_name}")
                break
        
        logger.info(f"📊 Discovered {len(self.repos)} repos")
    
    def get_repo_root(self, path: Path) -> Optional[Path]:
        """
        Get the repository root for a given path.
        
        Args:
            path: File or directory path
            
        Returns:
            Repository root path or None if not in any repo
        """
        path = Path(path).resolve()
        
        # Check if path is within any known repo
        for repo_name, repo_path in self.repos.items():
            try:
                path.relative_to(repo_path)
                return repo_path
            except ValueError:
                continue
        
        # Path not in any known repo
        return None
    
    def validate_operation(
        self,
        source_repo: Path,
        target_path: Path,
        operation: str = "access"
    ) -> bool:
        """
        Validate if operation crosses repo boundary.
        
        Args:
            source_repo: Source repository path
            target_path: Target file/directory path
            operation: Operation type (import, read, write, access)
            
        Returns:
            True if operation allowed
            
        Raises:
            RepoBoundaryViolation: If operation crosses boundary
        """
        source_root = self.get_repo_root(source_repo)
        target_root = self.get_repo_root(target_path)
        
        if source_root is None:
            logger.warning(f"⚠️  Source not in any repo: {source_repo}")
            return True  # Allow if not in managed repo
        
        if target_root is None:
            logger.warning(f"⚠️  Target not in any repo: {target_path}")
            return True  # Allow if not in managed repo
        
        # Same repo? Always allowed
        if source_root == target_root:
            return True
        
        # Cross-repo operation detected
        logger.warning(
            f"🚨 Cross-repo {operation}: "
            f"{source_root.name} → {target_root.name}"
        )
        
        # Check if allowed (CORTEX read-only exception)
        if self._is_allowed_cross_repo_access(
            source_root, target_root, target_path, operation
        ):
            logger.info(f"✅ Allowed: {operation} to {target_path}")
            return True
        
        # Violation!
        violation = {
            "timestamp": str(Path.cwd()),
            "source_repo": source_root.name,
            "target_repo": target_root.name,
            "target_path": str(target_path),
            "operation": operation
        }
        self.violations_log.append(violation)
        
        raise RepoBoundaryViolation(
            f"❌ FORBIDDEN: Cannot {operation} {target_path} from {source_repo}.\n"
            f"   Repositories must remain isolated.\n"
            f"   Source: {source_root.name}\n"
            f"   Target: {target_root.name}\n"
            f"   Rule: No cross-repo {operation} operations."
        )
    
    def _is_allowed_cross_repo_access(
        self,
        source_root: Path,
        target_root: Path,
        target_path: Path,
        operation: str
    ) -> bool:
        """
        Check if cross-repo access is explicitly allowed.
        
        Allowed scenarios:
        1. Read-only access to CORTEX repo (can use, can't modify)
        2. Read access to shared libraries (if configured)
        """
        # Allow read-only access to CORTEX repo
        if target_root == self.cortex_repo and operation in ["read", "access", "import"]:
            # But NOT to cortex-brain/ (CORTEX internal state)
            if "cortex-brain" in str(target_path):
                return False
            return True
        
        # All other cross-repo operations forbidden
        return False
    
    def validate_import(self, source_file: Path, import_path: str) -> bool:
        """
        Validate Python import statement.
        
        Args:
            source_file: File containing the import
            import_path: Import path (e.g., "src.models.user")
            
        Returns:
            True if import allowed
            
        Raises:
            RepoBoundaryViolation: If import crosses boundary
        """
        source_root = self.get_repo_root(source_file)
        if not source_root:
            return True
        
        # Check if import path references another repo
        # This is heuristic-based (not perfect)
        for repo_name, repo_path in self.repos.items():
            if repo_path == source_root:
                continue  # Skip own repo
            
            # Check if import path contains repo name
            if repo_name.lower() in import_path.lower():
                raise RepoBoundaryViolation(
                    f"❌ FORBIDDEN: Cannot import from another repo.\n"
                    f"   Source: {source_file}\n"
                    f"   Import: {import_path}\n"
                    f"   Detected reference to: {repo_name}\n"
                    f"   Rule: No cross-repo imports."
                )
        
        return True
    
    def check_cortex_implants_leakage(
        self,
        source_repo: Path,
        search_path: Path
    ) -> bool:
        """
        Check if operation would leak cortex-implants between repos.
        
        Args:
            source_repo: Source repository
            search_path: Path being searched
            
        Returns:
            True if no leakage
            
        Raises:
            RepoBoundaryViolation: If leakage detected
        """
        source_root = self.get_repo_root(source_repo)
        search_root = self.get_repo_root(search_path)
        
        if source_root != search_root:
            # Check if search_path is .cortex-implants
            if ".cortex-implants" in str(search_path):
                raise RepoBoundaryViolation(
                    f"❌ FORBIDDEN: Cannot access another repo's cortex-implants.\n"
                    f"   Source: {source_root.name if source_root else 'unknown'}\n"
                    f"   Target: {search_path}\n"
                    f"   Rule: Each repo's cortex-implants is private."
                )
        
        return True
    
    def get_violations_report(self) -> str:
        """
        Generate report of all violations.
        
        Returns:
            Human-readable report
        """
        if not self.violations_log:
            return "✅ No repo boundary violations detected."
        
        report = f"🚨 Repo Boundary Violations: {len(self.violations_log)}\n\n"
        
        for i, violation in enumerate(self.violations_log, 1):
            report += f"{i}. {violation['operation'].upper()}\n"
            report += f"   Source: {violation['source_repo']}\n"
            report += f"   Target: {violation['target_repo']}\n"
            report += f"   Path: {violation['target_path']}\n\n"
        
        return report
    
    def save_violations_log(self, output_file: Path) -> None:
        """Save violations log to JSON file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.violations_log, f, indent=2)
        
        logger.info(f"💾 Saved violations log to {output_file}")
    
    def get_repo_inventory(self) -> Dict[str, any]:
        """
        Get inventory of all repos in workspace.
        
        Returns:
            Dictionary with repo information
        """
        inventory = {
            "workspace_root": str(self.workspace_root),
            "total_repos": len(self.repos),
            "cortex_repo": str(self.cortex_repo) if self.cortex_repo else None,
            "repos": []
        }
        
        for repo_name, repo_path in sorted(self.repos.items()):
            repo_info = {
                "name": repo_name,
                "path": str(repo_path),
                "is_cortex": repo_path == self.cortex_repo,
                "has_cortex_implants": (repo_path / ".cortex-implants").exists(),
                "has_git": (repo_path / ".git").exists()
            }
            inventory["repos"].append(repo_info)
        
        return inventory
    
    def print_repo_inventory(self) -> None:
        """Print repo inventory to console."""
        inventory = self.get_repo_inventory()
        
        print("\n" + "=" * 60)
        print("📦 REPOSITORY INVENTORY")
        print("=" * 60)
        print(f"Workspace: {inventory['workspace_root']}")
        print(f"Total Repos: {inventory['total_repos']}")
        print()
        
        for i, repo in enumerate(inventory['repos'], 1):
            icon = "🧠" if repo['is_cortex'] else "📦"
            implants_status = "✅" if repo['has_cortex_implants'] else "❌"
            
            print(f"{i}. {icon} {repo['name']}")
            print(f"   Path: {repo['path']}")
            print(f"   Cortex Implants: {implants_status}")
            print()
        
        print("=" * 60)
        print("🔒 Repo Boundaries: ENFORCED")
        print("=" * 60)
        print()


# Singleton instance
_enforcer_instance: Optional[RepoBoundaryEnforcer] = None


def get_repo_boundary_enforcer(workspace_root: Path) -> RepoBoundaryEnforcer:
    """Get singleton enforcer instance."""
    global _enforcer_instance
    if _enforcer_instance is None or _enforcer_instance.workspace_root != workspace_root:
        _enforcer_instance = RepoBoundaryEnforcer(workspace_root)
    return _enforcer_instance


def validate_cross_repo_operation(
    source_repo: Path,
    target_path: Path,
    operation: str = "access"
) -> bool:
    """
    Convenience function to validate cross-repo operation.
    
    Args:
        source_repo: Source repository path
        target_path: Target file/directory path
        operation: Operation type
        
    Returns:
        True if allowed
        
    Raises:
        RepoBoundaryViolation: If operation forbidden
    """
    # Find workspace root (go up until we find multiple repos)
    workspace_root = Path(source_repo).resolve()
    while workspace_root.parent != workspace_root:
        workspace_root = workspace_root.parent
        if len(list(workspace_root.glob("*/.git"))) > 1:
            break
    
    enforcer = get_repo_boundary_enforcer(workspace_root)
    return enforcer.validate_operation(source_repo, target_path, operation)
