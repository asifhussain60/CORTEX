#!/usr/bin/env python3
"""
Orchestrator Migration Utility
Migrates orchestrators from old manifest format to ManifestLoader

Purpose: Automate migration of 11 active orchestrators to 3-Tier Manifest Architecture
Features:
  - Detect old manifest loading patterns
  - Generate migration code
  - Validate equivalence
  - Performance benchmarking

Author: Asif Hussain
Created: 2025-12-22 (Week 15 Day 4)
Version: 1.0.0
"""

import re
import ast
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrchestratorMigrationUtility:
    """Utility to migrate orchestrators to ManifestLoader."""
    
    def __init__(self, cortex_root: Path):
        self.cortex_root = Path(cortex_root)
        self.src_dir = self.cortex_root / "src" / "orchestrators"
        
        # Migration patterns
        self.old_patterns = [
            r'with open\(manifest_path.*?\) as f:.*?yaml\.safe_load\(f\)',
            r'self\.manifest = self\._load_manifest\(\)',
            r'def _load_manifest\(self\)',
            r'manifest_path = Path\(__file__\)\.parent.*?manifest.*?\.yaml'
        ]
    
    def find_orchestrators_needing_migration(self) -> List[Dict[str, Any]]:
        """
        Find orchestrators that need migration.
        
        Returns:
            List of orchestrator info dicts
        """
        logger.info("🔍 Scanning orchestrators...")
        
        orchestrators = []
        
        for py_file in self.src_dir.rglob("*orchestrator*.py"):
            # Skip __init__ and base files
            if "__init__" in str(py_file) or "base" in str(py_file):
                continue
            
            content = py_file.read_text(encoding='utf-8')
            
            # Check for old manifest loading patterns
            uses_old_format = any(
                re.search(pattern, content, re.DOTALL | re.MULTILINE)
                for pattern in self.old_patterns
            )
            
            if uses_old_format:
                orchestrators.append({
                    "file": py_file,
                    "relative_path": py_file.relative_to(self.cortex_root),
                    "name": self._extract_class_name(content),
                    "lines": len(content.splitlines())
                })
        
        logger.info(f"✅ Found {len(orchestrators)} orchestrators needing migration")
        return orchestrators
    
    def _extract_class_name(self, content: str) -> Optional[str]:
        """Extract orchestrator class name from file content."""
        match = re.search(r'class\s+(\w*Orchestrator\w*)\s*\(', content)
        return match.group(1) if match else None
    
    def generate_migration_code(self, orchestrator_id: str) -> str:
        """
        Generate migration code for an orchestrator.
        
        Args:
            orchestrator_id: Orchestrator identifier (e.g., "planning_orchestrator")
            
        Returns:
            Python code snippet for migration
        """
        return f'''
# OLD: Manual manifest loading
def _load_manifest(self) -> Dict[str, Any]:
    manifest_path = Path(__file__).parent.parent.parent.parent / \\
                   "cortex-brain/manifests/orchestrators/{orchestrator_id}-manifest.yaml"
    
    try:
        with open(manifest_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        self.logger.warning(f"Could not load manifest: {{e}}")
        return {{}}

# NEW: ManifestLoader
def __init__(self, cortex_root: str, **kwargs):
    # ... existing init code ...
    
    # Load manifest using ManifestLoader
    from src.utils.manifest_loader import ManifestLoader
    self.manifest_loader = ManifestLoader(cortex_root)
    
    # Get orchestrator metadata
    self.metadata = self.manifest_loader.get_orchestrator("{orchestrator_id}")
    
    # Resolve cross-references
    resolved = self.manifest_loader.resolve_cross_references("{orchestrator_id}")
    self.config = resolved.get("config", {{}})
    self.integrations = resolved.get("integrations", {{}})
    
    # For backward compatibility, also store as self.manifest
    self.manifest = resolved.get("metadata", {{}})
'''
    
    def create_migration_patch(self, orchestrator_file: Path) -> str:
        """
        Create a git-style patch for migrating an orchestrator.
        
        Args:
            orchestrator_file: Path to orchestrator file
            
        Returns:
            Patch content as string
        """
        content = orchestrator_file.read_text(encoding='utf-8')
        
        # Extract class name
        class_name = self._extract_class_name(content)
        if not class_name:
            return ""
        
        # Generate patch
        patch_lines = [
            f"# Migration patch for {orchestrator_file.name}",
            f"# Orchestrator: {class_name}",
            "",
            "# Add import at top of file:",
            "from src.utils.manifest_loader import ManifestLoader",
            "",
            "# Update __init__ method:",
            "# Add after super().__init__():",
            "",
            "    # Load manifest using ManifestLoader",
            "    self.manifest_loader = ManifestLoader(cortex_root)",
            "    resolved = self.manifest_loader.resolve_cross_references(orchestrator_id)",
            "    self.metadata = resolved.get('metadata', {})",
            "    self.config = resolved.get('config', {})",
            "    self.integrations = resolved.get('integrations', {})",
            "",
            "# Remove old _load_manifest method",
            "# def _load_manifest(self): ...",
        ]
        
        return "\n".join(patch_lines)
    
    def validate_migration(
        self,
        orchestrator_file: Path,
        orchestrator_id: str
    ) -> Dict[str, Any]:
        """
        Validate migration for an orchestrator.
        
        Args:
            orchestrator_file: Path to orchestrator file
            orchestrator_id: Orchestrator identifier
            
        Returns:
            Validation report
        """
        from src.utils.manifest_loader import ManifestMigrationAdapter
        
        adapter = ManifestMigrationAdapter(str(self.cortex_root))
        
        return {
            "orchestrator_id": orchestrator_id,
            "file": str(orchestrator_file),
            "old_format_exists": adapter.load_old_format(orchestrator_id) is not None,
            "new_format_exists": adapter.load_new_format(orchestrator_id) is not None,
            "is_equivalent": adapter.validate_equivalence(orchestrator_id),
            "recommendation": adapter.migrate_orchestrator(orchestrator_id)["recommendation"]
        }
    
    def generate_migration_report(self) -> str:
        """
        Generate complete migration report.
        
        Returns:
            Report content as string
        """
        orchestrators = self.find_orchestrators_needing_migration()
        
        lines = [
            "# Orchestrator Migration Report",
            f"**Generated:** {__import__('datetime').datetime.now().isoformat()}",
            "",
            f"## Summary",
            f"- **Total orchestrators needing migration:** {len(orchestrators)}",
            "",
            "## Orchestrators",
            ""
        ]
        
        for i, orch in enumerate(orchestrators, 1):
            lines.extend([
                f"### {i}. {orch['name']}",
                f"- **File:** `{orch['relative_path']}`",
                f"- **Lines:** {orch['lines']}",
                f"- **Status:** Needs migration",
                ""
            ])
        
        return "\n".join(lines)


def main():
    """Main entry point."""
    import sys
    
    cortex_root = Path(__file__).parent.parent
    
    print("=" * 80)
    print("Orchestrator Migration Utility")
    print("=" * 80)
    
    utility = OrchestratorMigrationUtility(cortex_root)
    
    # Find orchestrators
    orchestrators = utility.find_orchestrators_needing_migration()
    
    print(f"\n📋 Orchestrators Needing Migration: {len(orchestrators)}\n")
    
    for i, orch in enumerate(orchestrators, 1):
        print(f"{i}. {orch['name']}")
        print(f"   File: {orch['relative_path']}")
        print(f"   Lines: {orch['lines']}")
        print()
    
    # Generate report
    print("\n📊 Generating migration report...")
    report = utility.generate_migration_report()
    
    report_file = cortex_root / "cortex-brain" / "documents" / "implementation-guides" / \
                  "orchestrator-migration-report.md"
    report_file.write_text(report, encoding='utf-8')
    
    print(f"✅ Report saved: {report_file}")
    
    # Show migration example
    if orchestrators:
        print("\n📝 Migration Example (for first orchestrator):")
        print("=" * 80)
        
        orch = orchestrators[0]
        orchestrator_id = orch['name'].lower().replace('orchestrator', '_orchestrator')
        
        migration_code = utility.generate_migration_code(orchestrator_id)
        print(migration_code)


if __name__ == "__main__":
    main()
