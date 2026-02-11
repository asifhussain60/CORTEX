"""Safe file rename tool with import updates.

Safely renames Python files and updates all imports across the codebase.
Includes rollback on failure and dry-run mode for validation.

Phase 7.4, Task NAMING-004
AC-ID: NAMING-004
"""

import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Set


class RenameError(Exception):
    """Exception raised when rename operation fails."""
    pass


@dataclass
class RenameResult:
    """Result of a file rename operation."""

    success: bool
    old_path: Path
    new_path: Path
    imports_updated: int = 0
    test_files_renamed: int = 0
    error_message: Optional[str] = None


class SafeFileRenamer:
    """Safely rename Python files with automatic import updates.

    Features:
    - Renames files with validation
    - Updates all imports across codebase
    - Renames corresponding test files
    - Rollback on failure
    - Dry-run mode for validation

    Args:
        workspace_root: Root directory of workspace
        dry_run: If True, simulates rename without making changes

    Example:
        >>> renamer = SafeFileRenamer(Path("/path/to/workspace"))
        >>> result = renamer.rename_file(
        ...     Path("cortex/tools/old_name.py"),
        ...     "new-name.py"
        ... )
        >>> print(f"Updated {result.imports_updated} imports")
    """

    def __init__(self, workspace_root: Path, dry_run: bool = False):
        """Initialize safe file renamer.

        Args:
            workspace_root: Root directory of workspace
            dry_run: If True, simulates rename without making changes
        """
        self.workspace_root = workspace_root
        self.dry_run = dry_run
        self._backup_files: List[Path] = []

    def rename_file(self, old_path: Path, new_name: str) -> RenameResult:
        """Rename file and update all imports.

        Args:
            old_path: Current path to file
            new_name: New file name (just the name, not full path)

        Returns:
            RenameResult with operation details

        Raises:
            RenameError: If rename operation fails
        """
        try:
            # Validate inputs
            if not old_path.exists():
                raise RenameError(f"File does not exist: {old_path}")

            if ".." in new_name or "/" in new_name:
                raise RenameError(f"Invalid new name (contains path separators): {new_name}")

            # Calculate new path
            new_path = old_path.parent / new_name

            if new_path.exists() and new_path != old_path:
                raise RenameError(f"Target file already exists: {new_path}")

            # Extract module names
            old_module = old_path.stem.replace("-", "_")  # Python uses underscores
            new_module = Path(new_name).stem.replace("-", "_")

            if self.dry_run:
                print(f"[DRY-RUN] Would rename: {old_path} → {new_path}")
                print(f"[DRY-RUN] Would update imports: {old_module} → {new_module}")
                return RenameResult(
                    success=True,
                    old_path=old_path,
                    new_path=new_path,
                    imports_updated=0,
                    test_files_renamed=0,
                )

            # Find all files that import this module
            references = self.find_import_references(old_path)

            # Update imports in all referencing files
            imports_updated = 0
            for ref_file in references:
                if self.update_import_statement(ref_file, old_module, new_module):
                    imports_updated += 1

            # Rename test files
            test_files_renamed = self._rename_test_files(old_path, new_name)

            # Actually rename the file
            shutil.move(str(old_path), str(new_path))

            return RenameResult(
                success=True,
                old_path=old_path,
                new_path=new_path,
                imports_updated=imports_updated,
                test_files_renamed=test_files_renamed,
            )

        except Exception as e:
            # Rollback on failure
            self._rollback()
            raise RenameError(f"Rename failed: {e}") from e

    def find_import_references(self, target_file: Path) -> List[Path]:
        """Find all files that import the target module.

        Args:
            target_file: File to find references to

        Returns:
            List of files that import the target module
        """
        references = []
        module_name = target_file.stem.replace("-", "_")

        # Search all Python files
        for py_file in self.workspace_root.rglob("*.py"):
            if py_file == target_file:
                continue

            try:
                content = py_file.read_text()

                # Check for various import patterns
                patterns = [
                    rf"from\s+[\w.]*{re.escape(module_name)}\s+import",
                    rf"import\s+[\w.]*{re.escape(module_name)}",
                    rf"from\s+[\w.]*\s+import\s+.*{re.escape(module_name)}",
                ]

                for pattern in patterns:
                    if re.search(pattern, content):
                        references.append(py_file)
                        break
            except Exception:
                # Skip files that can't be read
                continue

        return references

    def update_import_statement(
        self,
        file_path: Path,
        old_module: str,
        new_module: str
    ) -> bool:
        """Update import statements in a file.

        Args:
            file_path: File to update
            old_module: Old module name
            new_module: New module name

        Returns:
            True if file was updated, False otherwise
        """
        try:
            content = file_path.read_text()
            original_content = content

            # Replace import statements
            patterns = [
                (rf"from\s+([\w.]*){re.escape(old_module)}\s+import", rf"from \1{new_module} import"),
                (rf"import\s+([\w.]*){re.escape(old_module)}", rf"import \1{new_module}"),
            ]

            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content)

            # Write back if changed
            if content != original_content:
                # Backup before modifying
                self._backup_file(file_path)
                file_path.write_text(content)
                return True

            return False

        except Exception:
            return False

    def _rename_test_files(self, old_path: Path, new_name: str) -> int:
        """Rename corresponding test files.

        Args:
            old_path: Original file path
            new_name: New file name

        Returns:
            Number of test files renamed
        """
        count = 0
        old_name_stem = old_path.stem.replace("-", "_")
        new_name_stem = Path(new_name).stem.replace("-", "_")

        # Find test files
        test_patterns = [
            f"test_{old_name_stem}.py",
            f"{old_name_stem}_test.py",
            f"test{old_name_stem}.py",
        ]

        for pattern in test_patterns:
            for test_file in self.workspace_root.rglob(pattern):
                # Calculate new test file name
                new_test_name = test_file.name.replace(old_name_stem, new_name_stem)
                new_test_path = test_file.parent / new_test_name

                # Rename test file
                shutil.move(str(test_file), str(new_test_path))
                count += 1

                # Update imports in test file
                self.update_import_statement(new_test_path, old_name_stem, new_name_stem)

        return count

    def _backup_file(self, file_path: Path) -> None:
        """Create backup of file before modification.

        Args:
            file_path: File to backup
        """
        backup_path = file_path.with_suffix(file_path.suffix + ".backup")
        shutil.copy(str(file_path), str(backup_path))
        self._backup_files.append(backup_path)

    def _rollback(self) -> None:
        """Rollback changes by restoring backups."""
        for backup_path in self._backup_files:
            original_path = Path(str(backup_path).replace(".backup", ""))
            shutil.move(str(backup_path), str(original_path))
        self._backup_files.clear()


def main() -> None:
    """CLI entry point for safe file rename.

    Usage:
        python -m cortex.tools.safe_file_rename <old_path> <new_name> [--dry-run]
    """
    import sys

    if len(sys.argv) < 3:
        print("Usage: python -m cortex.tools.safe_file_rename <old_path> <new_name> [--dry-run]")
        sys.exit(1)

    old_path = Path(sys.argv[1])
    new_name = sys.argv[2]
    dry_run = "--dry-run" in sys.argv

    renamer = SafeFileRenamer(workspace_root=Path.cwd(), dry_run=dry_run)

    try:
        result = renamer.rename_file(old_path, new_name)
        print("✅ Success!")
        print(f"   Old: {result.old_path}")
        print(f"   New: {result.new_path}")
        print(f"   Imports updated: {result.imports_updated}")
        print(f"   Test files renamed: {result.test_files_renamed}")
    except RenameError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
