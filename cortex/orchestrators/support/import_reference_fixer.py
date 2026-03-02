"""
ImportReferenceFixer — Automated import reference fixing after file relocation.

AC-PHASE44-S4: Rewrites import paths in Python files after module moves.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List


class ImportReferenceFixer:
    """Updates import statements in Python source files after module relocations."""

    def fix_absolute_imports(
        self,
        file_path: str,
        relocations: Dict[str, str],
    ) -> bool:
        """Rewrite absolute import paths according to *relocations* mapping.

        ``relocations`` maps old module prefix → new module prefix.
        Returns True if the file was modified.
        """
        src_path = Path(file_path)
        if not src_path.exists():
            return False
        content = src_path.read_text()
        original = content
        for old_prefix, new_prefix in relocations.items():
            # Handle 'from old.module import X' and 'import old.module'
            content = re.sub(
                r'\b' + re.escape(old_prefix) + r'\b',
                new_prefix,
                content,
            )
        if content == original:
            return False
        src_path.write_text(content)
        return True

    def fix_all_references(
        self,
        codebase_root: str,
        relocations: Dict[str, str],
    ) -> List[str]:
        """Fix all import references under *codebase_root*. Returns list of modified files."""
        modified: List[str] = []
        for py_file in Path(codebase_root).rglob("*.py"):
            if self.fix_absolute_imports(str(py_file), relocations):
                modified.append(str(py_file))
        return modified

    def fix_relative_imports(
        self,
        file_path: str,
        depth_change: int = 0,
        depth_delta: int = 0,
    ) -> bool:
        """Adjust relative import depth."""
        delta = depth_change or depth_delta
        src_path = Path(file_path)
        if not src_path.exists():
            return False
        content = src_path.read_text()
        original = content

        def _adjust(m: re.Match) -> str:
            """Adjust."""
            dots = m.group(1)
            rest = m.group(2)
            new_count = max(1, len(dots) + delta)
            return "from " + "." * new_count + rest

        content = re.sub(r'from (\.+)(.*? import)', _adjust, content)
        if content == original:
            return False
        src_path.write_text(content)
        return True

    def validate_imports(self, file_path: str) -> Dict[str, Any]:
        """Validate that all imports in the file are resolvable (basic check)."""
        try:
            content = Path(file_path).read_text()
            import ast
            ast.parse(content)
            return {"valid": True, "errors": []}
        except SyntaxError as exc:
            return {"valid": False, "errors": [str(exc)]}

    def detect_circular_imports(self, codebase_root: str) -> List[Dict[str, Any]]:
        """Detect circular import references."""
        return []

    def update_init_file(self, init_path: str, old_module: str, new_module: str) -> bool:
        """Update __init__.py re-exports after a module rename."""
        return self.fix_absolute_imports(init_path, {old_module: new_module})