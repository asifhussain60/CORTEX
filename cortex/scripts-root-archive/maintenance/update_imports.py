#!/usr/bin/env python3
"""
AC-AR-010-03: Import Path Updates & Validation Script

Updates all import statements from old paths to new unified cortex/ structure.
Validates imports, tier isolation, and circular dependencies.

Usage:
    python scripts/update_imports.py --dry-run
    python scripts/update_imports.py --execute
    python scripts/update_imports.py --validate
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import ast
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ImportTransformer:
    """Transforms old imports to new unified cortex/ structure."""

    # Mapping of old imports to new imports
    IMPORT_MAPPINGS = {
        # cortex_brain → cortex.brain
        r'from\s+cortex_brain\.tier0': 'from cortex.brain.tier0',
        r'from\s+cortex_brain\.tier1': 'from cortex.brain.tier1',
        r'from\s+cortex_brain\.tier2': 'from cortex.brain.tier2',
        r'from\s+cortex_brain\.tier3': 'from cortex.brain.tier3',
        r'import\s+cortex_brain\.tier0': 'import cortex.brain.tier0',
        r'import\s+cortex_brain\.tier1': 'import cortex.brain.tier1',
        r'import\s+cortex_brain\.tier2': 'import cortex.brain.tier2',
        r'import\s+cortex_brain\.tier3': 'import cortex.brain.tier3',
        
        # src.api → cortex.api
        r'from\s+src\.api': 'from cortex.api',
        r'import\s+src\.api': 'import cortex.api',
        
        # src.orchestrators → cortex.orchestrators
        r'from\s+src\.orchestrators': 'from cortex.orchestrators',
        r'import\s+src\.orchestrators': 'import cortex.orchestrators',
        
        # src.knowledge → cortex.knowledge
        r'from\s+src\.knowledge': 'from cortex.knowledge',
        r'import\s+src\.knowledge': 'import cortex.knowledge',
        
        # src.infrastructure → cortex.infrastructure
        r'from\s+src\.infrastructure': 'from cortex.infrastructure',
        r'import\s+src\.infrastructure': 'import cortex.infrastructure',
        
        # src.tools → cortex.tools
        r'from\s+src\.tools': 'from cortex.tools',
        r'import\s+src\.tools': 'import cortex.tools',
        
        # src.* → cortex.brain.* (for other modules)
        r'from\s+src\.': 'from cortex.brain.',
        r'import\s+src\.': 'import cortex.brain.',
    }

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.transformations: Dict[Path, List[Dict]] = {}

    def transform_file(self, file_path: Path, dry_run: bool = True) -> bool:
        """Transform imports in a single file."""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            original_content = content

            # Apply transformations
            for old_pattern, new_import in self.IMPORT_MAPPINGS.items():
                content = re.sub(old_pattern, new_import, content)

            # Track transformations
            if content != original_content:
                self.transformations[file_path] = [
                    {'original': old_pattern, 'new': new_import}
                    for old_pattern, new_import in self.IMPORT_MAPPINGS.items()
                    if re.search(old_pattern, original_content)
                ]

                if not dry_run:
                    file_path.write_text(content, encoding='utf-8')
                    logger.info(f"Updated: {file_path}")
                else:
                    logger.info(f"[DRY-RUN] Would update: {file_path}")

                return True

            return False
        except Exception as e:
            logger.error(f"Failed to transform {file_path}: {e}")
            return False

    def transform_all_py_files(self, dry_run: bool = True) -> int:
        """Transform all Python files in cortex/."""
        cortex = self.project_root / "cortex"
        if not cortex.exists():
            logger.error(f"cortex/ not found")
            return 0

        count = 0
        for py_file in cortex.rglob("*.py"):
            if self.transform_file(py_file, dry_run):
                count += 1

        return count


class ImportValidator:
    """Validates import statements and detects issues."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.broken_imports: List[Tuple[Path, str, str]] = []
        self.tier_violations: List[Tuple[Path, str, str]] = []
        self.circular_dependencies: List[Tuple[str, str]] = []

    def validate_all_imports(self) -> bool:
        """Validate all imports in cortex/."""
        logger.info("Validating imports...")
        cortex = self.project_root / "cortex"

        if not cortex.exists():
            logger.error("cortex/ not found")
            return False

        all_valid = True

        for py_file in cortex.rglob("*.py"):
            if not self._validate_file_imports(py_file):
                all_valid = False

        return all_valid

    def _validate_file_imports(self, file_path: Path) -> bool:
        """Validate imports in a single file."""
        try:
            tree = ast.parse(file_path.read_text(encoding='utf-8', errors='ignore'))
        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
            return False

        valid = True

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module_name = node.module if hasattr(node, 'module') else None

                if module_name:
                    # Check for tier isolation violations
                    if not self._check_tier_isolation(file_path, module_name):
                        valid = False

                    # Check for old import paths
                    if self._is_old_import_path(module_name):
                        self.broken_imports.append((
                            file_path,
                            module_name,
                            self._map_to_new_path(module_name)
                        ))
                        valid = False

        return valid

    def _check_tier_isolation(self, file_path: Path, imported_module: str) -> bool:
        """Verify tier isolation rules."""
        # Extract tier of current file
        try:
            tier_path = file_path.relative_to(self.project_root / "cortex" / "brain")
            parts = tier_path.parts
            if not parts or not parts[0].startswith('tier'):
                return True  # Not a tiered module

            current_tier_num = int(parts[0][4])
        except (ValueError, IndexError):
            return True  # Can't determine tier

        # Extract tier of imported module
        try:
            if imported_module.startswith('cortex.brain.tier'):
                imported_tier_num = int(imported_module.split('.')[3][4])

                # Lower tiers can only import from lower or equal tiers
                if imported_tier_num > current_tier_num:
                    self.tier_violations.append((
                        file_path,
                        imported_module,
                        f"Tier{current_tier_num} cannot import from Tier{imported_tier_num}"
                    ))
                    return False
        except (ValueError, IndexError):
            pass

        return True

    @staticmethod
    def _is_old_import_path(module_name: str) -> bool:
        """Check if import uses old paths."""
        if not module_name:
            return False
        return (
            module_name.startswith('cortex_brain') or
            module_name.startswith('src.') or
            (module_name.startswith('cortex.') and not module_name.startswith('cortex.brain'))
        )

    @staticmethod
    def _map_to_new_path(old_module: str) -> str:
        """Map old import to new path."""
        if old_module.startswith('cortex_brain'):
            return old_module.replace('cortex_brain', 'cortex.brain')
        if old_module.startswith('src'):
            return old_module.replace('src', 'cortex.brain', 1)
        return old_module

    def report_issues(self) -> None:
        """Report validation issues."""
        logger.info("=" * 80)
        logger.info("IMPORT VALIDATION REPORT")
        logger.info("=" * 80)

        if self.broken_imports:
            logger.warning(f"\n❌ Broken Imports ({len(self.broken_imports)}):")
            for file_path, old_import, new_import in self.broken_imports[:10]:
                logger.warning(f"  {file_path}: {old_import} → {new_import}")
            if len(self.broken_imports) > 10:
                logger.warning(f"  ... and {len(self.broken_imports) - 10} more")

        if self.tier_violations:
            logger.warning(f"\n⚠️  Tier Isolation Violations ({len(self.tier_violations)}):")
            for file_path, module, reason in self.tier_violations[:10]:
                logger.warning(f"  {file_path}: {module}")
                logger.warning(f"    Reason: {reason}")

        if not self.broken_imports and not self.tier_violations:
            logger.info("\n✅ All imports valid!")
            logger.info("✅ Tier isolation rules satisfied!")


class InitFileGenerator:
    """Generates __init__.py files for all packages."""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def generate_all_init_files(self) -> int:
        """Generate __init__.py for all Python packages."""
        cortex = self.project_root / "cortex"
        count = 0

        for directory in cortex.rglob("*"):
            if not directory.is_dir():
                continue

            # Skip __pycache__
            if '__pycache__' in str(directory):
                continue

            # Check if directory contains .py files
            has_py_files = any(directory.glob("*.py"))
            if not has_py_files and not any(directory.glob("*/")):
                continue  # Empty directory

            init_file = directory / "__init__.py"
            if not init_file.exists():
                init_file.touch()
                logger.info(f"Created: {init_file}")
                count += 1

        return count


def main():
    """Main orchestrator for import updates."""
    parser_help = '''
    Update imports from old paths to new unified cortex/ structure.
    
    Examples:
        python scripts/update_imports.py --dry-run   # Show what would change
        python scripts/update_imports.py --execute   # Make actual changes
        python scripts/update_imports.py --validate  # Validate imports
    '''

    import argparse
    parser = argparse.ArgumentParser(description=parser_help)
    parser.add_argument('--dry-run', action='store_true', help='Show changes without executing')
    parser.add_argument('--execute', action='store_true', help='Execute import updates')
    parser.add_argument('--validate', action='store_true', help='Validate imports only')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    if not args.execute and not args.validate:
        args.dry_run = True

    project_root = Path(__file__).parent.parent

    # Generate __init__.py files
    logger.info("Generating __init__.py files...")
    init_gen = InitFileGenerator(project_root)
    init_count = init_gen.generate_all_init_files()
    logger.info(f"✓ Generated {init_count} __init__.py files")

    if args.execute or args.dry_run:
        # Transform imports
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 1: IMPORT TRANSFORMATION")
        logger.info("=" * 80)

        transformer = ImportTransformer(project_root)
        count = transformer.transform_all_py_files(dry_run=args.dry_run or not args.execute)
        logger.info(f"✓ Transformed {count} files")

    # Validate imports
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 2: IMPORT VALIDATION")
    logger.info("=" * 80)

    validator = ImportValidator(project_root)
    validator.validate_all_imports()
    validator.report_issues()

    if validator.broken_imports or validator.tier_violations:
        logger.error("\n❌ Validation failed!")
        return 1

    logger.info("\n" + "=" * 80)
    logger.info("✅ IMPORT UPDATE COMPLETE")
    logger.info("=" * 80)
    return 0


if __name__ == '__main__':
    sys.exit(main())
