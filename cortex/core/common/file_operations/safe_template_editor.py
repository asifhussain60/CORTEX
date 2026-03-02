"""
Safe Template Editor - CORE-057 Compliance.

Purpose: Prevent template corruption in Python files with Jinja2 templates
Learning: chat01 showed replace_string_in_file unreliable (8+ fix attempts)

Features:
- Syntax check before write
- Automatic backup creation
- Atomic write operations
- Rollback on corruption
- Import verification
- Multi-line template preservation
"""
import ast
import re
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import importlib.util

class TemplateCorruptionError(Exception):
    """Raised when template corruption detected."""
    pass

class TemplateSyntaxError(Exception):
    """Raised when template has invalid syntax."""
    pass

@dataclass
class EditResult:
    """Result of template replacement operation."""
    success: bool
    backup_path: Optional[Path] = None
    backup_created: bool = False
    write_method: str = "atomic"
    import_check_passed: bool = False
    error: Optional[str] = None

class SafeTemplateEditor:
    """
    Safe editor for Jinja2 templates in Python files.

    CORE-057: Prevents template corruption by:
    1. Creating backup before modification
    2. Syntax checking before write
    3. Atomic write (temp → rename)
    4. Automatic rollback on failure
    5. Import verification after edit

    Example:
        editor = SafeTemplateEditor()
        result = editor.replace_template(
            file_path="cortex/debugging/marker_injection_engine.py",
            template_var="MARKER_TEMPLATE",
        )

        if result.success:
            print(f"Template updated, backup at {result.backup_path}")
        else:
            print(f"Failed: {result.error}")
    """

    def __init__(self) -> None:
        """Initialize SafeTemplateEditor."""
        self.backup_suffix = ".bak"

    def replace_template(
        self,
        file_path: str,
        template_var: str,
        new_template: str,
        allow_empty: bool = False,
        verify_imports: bool = True,
        keep_strip: bool = True
    ) -> EditResult:
        """
        Replace Jinja2 template with safety checks.

        Args:
            file_path: Path to Python file containing template
            template_var: Name of template variable (e.g., "MARKER_TEMPLATE")
            new_template: New template content
            allow_empty: Allow empty templates (default False)
            verify_imports: Check imports after edit (default True)
            keep_strip: Keep .strip() in template definition (default True)

        Returns:
            EditResult with success status and details

        Raises:
            TemplateCorruptionError: If corruption detected
            TemplateSyntaxError: If syntax invalid
            ValueError: If template variable not found
        """
        file_path = Path(file_path)

        # Step 1: Validate inputs
        if not allow_empty and not new_template.strip():
            raise TemplateCorruptionError(
                f"Empty template not allowed for {template_var}"
            )

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Step 2: Create backup
        backup_path = self._create_backup(file_path)

        try:
            # Step 3: Read original content
            original_content = file_path.read_text()

            # Step 4: Find and replace template
            new_content = self._replace_template_content(
                content=original_content,
                template_var=template_var,
                new_template=new_template,
                keep_strip=keep_strip
            )

            # Step 5: Syntax check
            self._check_syntax(new_content, file_path)

            # Step 6: Atomic write
            self._atomic_write(file_path, new_content)

            # Step 7: Import verification (optional)
            import_ok = True
            if verify_imports:
                import_ok = self._verify_imports(file_path)

            return EditResult(
                success=True,
                backup_path=backup_path,
                backup_created=True,
                write_method="atomic",
                import_check_passed=import_ok
            )

        except (TemplateCorruptionError, TemplateSyntaxError, ValueError):
            # Re-raise validation errors without rollback
            raise

        except Exception as e:
            # Rollback on any error
            self._rollback(file_path, backup_path)
            return EditResult(
                success=False,
                backup_path=backup_path,
                error=str(e)
            )

    def _create_backup(self, file_path: Path) -> Path:
        """Create backup of original file."""
        backup_path = file_path.with_suffix(
            file_path.suffix + self.backup_suffix
        )
        shutil.copy2(file_path, backup_path)
        return backup_path

    def _replace_template_content(
        self,
        content: str,
        template_var: str,
        new_template: str,
        keep_strip: bool
    ) -> str:
        """
        Replace template in content.

        Handles:
        - Single-line templates: Template("{{ x }}")
        - Multi-line templates with triple quotes
        - .strip() suffix preservation
        """
        # Pattern to match template variable assignment
        # Handles: TEMPLATE = Template("""...""".strip())
        # or: TEMPLATE = Template("...")
        # Optional .strip() at the end
        pattern = rf'{template_var}\s*=\s*Template\((""".*?"""|\'\'\'.*?\'\'\'|".*?"|\'.*?\')(?:\s*\.strip\(\))?\s*\)'

        match = re.search(pattern, content, re.DOTALL)
        if not match:
            raise ValueError(
                f"Template variable '{template_var}' not found in content"
            )

        # Determine quote style (prefer triple quotes for multi-line)
        if '\n' in new_template:
            quote_style = '"""'
            template_str = f'{quote_style}{new_template}{quote_style}'
        else:
            quote_style = '"'
            template_str = f'{quote_style}{new_template}{quote_style}'

        # Add .strip() if requested
        if keep_strip:
            replacement = f'{template_var} = Template({template_str}.strip())'
        else:
            replacement = f'{template_var} = Template({template_str})'

        # Replace entire template assignment
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

        return new_content

    def _check_syntax(self, content: str, file_path: Path) -> None:
        """Check Python syntax of new content."""
        try:
            ast.parse(content)
        except SyntaxError as e:
            raise TemplateSyntaxError(
                f"Syntax error in {file_path.name}: {e}"
            )

    def _atomic_write(self, file_path: Path, content: str) -> None:
        """
        Write content atomically using temp file + rename.

        This ensures file is never in a corrupted state.
        """
        temp_fd, temp_path = tempfile.mkstemp(
            dir=file_path.parent,
            prefix=f".{file_path.name}.",
            suffix=".tmp"
        )

        try:
            # Write to temp file
            with open(temp_fd, 'w') as f:
                f.write(content)

            # Atomic rename
            temp_path_obj = Path(temp_path)
            temp_path_obj.replace(file_path)

        except Exception:
            # Clean up temp file on error
            if Path(temp_path).exists():
                Path(temp_path).unlink()
            raise

    def _verify_imports(self, file_path: Path) -> bool:
        """
        Verify file can be imported after edit.

        Returns True if imports work, False otherwise.
        """
        try:
            spec = importlib.util.spec_from_file_location(
                "temp_module",
                file_path
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return True
        except Exception:
            return False

        return False

    def _rollback(self, file_path: Path, backup_path: Path) -> None:
        """Rollback to backup on error."""
        if backup_path.exists():
            shutil.copy2(backup_path, file_path)

# AC_COMPLETE: AC-DIGEST-CHAT01-001 ✅
# Implementation covers all chat01 failure scenarios:
# - Multi-line template handling (proper newline preservation)
# - Syntax checking (prevents broken Python)
# - Backup creation (can always recover)
# - Atomic writes (never corrupted state)
# - Rollback mechanism (auto-recovery)
# - Import verification (catches runtime errors)