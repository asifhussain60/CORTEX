#!/usr/bin/env python3
"""
CORTEX Root Directory Analyzer & Cleanup

Analyzes root directory structure and identifies/removes invalid folders.
Based on proper CORTEX architecture.

AC-ROOT-CLEANUP-001: Repository root directory validation
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class RootDirectoryAnalyzer:
    """Analyzes and cleans root directory structure."""

    # Valid root directories per architecture
    VALID_ROOT_DIRS = {
        # Core CORTEX modules
        "cortex": "Main CORTEX module",
        "cortex-registry": "Phase registry and governance",
        "cortex_brain": "Legacy brain module (can be archived)",
        "cortex_lens": "Legacy lens module (can be archived)",
        
        # Testing and scripts
        "tests": "Test suite",
        "scripts": "Utility scripts",
        
        # Configuration and documentation
        ".github": "GitHub workflows and prompts",
        ".cortex": "CORTEX configuration",
        "docs": "Documentation",
        "deployment": "Deployment configurations",
        
        # Development and company
        "company": "Company domain knowledge",
        "registry": "Alternative registry location",
        # Moved to: company/dashboards/lens
        
        # Virtual environment and cache
        ".venv": "Python virtual environment",
        ".cache": "Cache files",
        ".pytest_temp": "Pytest temporary files",
        ".vscode": "VS Code settings",
        ".git": "Git repository",
        ".githooks": "Git hooks",
        
        # Development workspaces (optional)
        "_workspaces": "Development workspaces (optional)",
    }
    
    # Invalid/accidental directories to remove
    INVALID_DIRS = {
        "d:": "Accidental mount/drive path",
        "~": "Accidental home directory reference",
    }

    def __init__(self, cortex_root: Path):
        self.cortex_root = cortex_root
        self.actual_dirs = set()
        self.valid_dirs = set()
        self.invalid_dirs = set()
        self.unknown_dirs = set()

    def analyze(self) -> None:
        """Analyze root directory structure."""
        logger.info("📊 Analyzing root directory structure...\n")

        for item in self.cortex_root.iterdir():
            if not item.is_dir():
                continue
            
            dir_name = item.name
            self.actual_dirs.add(dir_name)

            # Check if valid
            if dir_name in self.VALID_ROOT_DIRS:
                self.valid_dirs.add(dir_name)
                logger.info(f"✅ VALID: {dir_name}")
                logger.info(f"   → {self.VALID_ROOT_DIRS[dir_name]}")
            
            # Check if invalid
            elif dir_name in self.INVALID_DIRS:
                self.invalid_dirs.add(dir_name)
                logger.info(f"❌ INVALID: {dir_name}")
                logger.info(f"   → {self.INVALID_DIRS[dir_name]}")
                logger.info(f"   → ACTION: Should be deleted")
            
            # Unknown
            else:
                self.unknown_dirs.add(dir_name)
                logger.info(f"❓ UNKNOWN: {dir_name}")
                logger.info(f"   → ACTION: Review manually")

    def generate_report(self) -> None:
        """Generate analysis report."""
        logger.info("\n" + "━" * 70)
        logger.info("📋 ROOT DIRECTORY ANALYSIS REPORT")
        logger.info("━" * 70 + "\n")

        logger.info(f"Total directories: {len(self.actual_dirs)}")
        logger.info(f"  ✅ Valid: {len(self.valid_dirs)}")
        logger.info(f"  ❌ Invalid: {len(self.invalid_dirs)}")
        logger.info(f"  ❓ Unknown: {len(self.unknown_dirs)}")

        if self.invalid_dirs:
            logger.info("\n❌ INVALID DIRECTORIES (should be deleted):")
            for dir_name in sorted(self.invalid_dirs):
                logger.info(f"  • {dir_name}")

        if self.unknown_dirs:
            logger.info("\n❓ UNKNOWN DIRECTORIES (review manually):")
            for dir_name in sorted(self.unknown_dirs):
                dir_path = self.cortex_root / dir_name
                size_mb = sum(
                    f.stat().st_size for f in dir_path.rglob("*") if f.is_file()
                ) / (1024 * 1024) if dir_path.exists() else 0
                logger.info(f"  • {dir_name} ({size_mb:.1f}MB)")

        logger.info("\n" + "━" * 70)

    def delete_invalid_dirs(self) -> Tuple[int, float]:
        """Delete invalid directories."""
        if not self.invalid_dirs:
            logger.info("\n✅ No invalid directories to delete")
            return 0, 0.0

        logger.info("\n🗑️  Deleting invalid directories...\n")

        deleted = 0
        freed = 0.0

        for dir_name in sorted(self.invalid_dirs):
            dir_path = self.cortex_root / dir_name
            
            try:
                import shutil
                
                size = sum(
                    f.stat().st_size for f in dir_path.rglob("*") if f.is_file()
                ) if dir_path.exists() else 0
                
                shutil.rmtree(dir_path)
                freed += size / (1024 * 1024)
                deleted += 1
                
                logger.info(f"✅ Deleted: {dir_name} ({size / (1024 * 1024):.2f}MB)")
            
            except Exception as e:
                logger.error(f"❌ Failed to delete {dir_name}: {e}")

        return deleted, freed

    def run(self) -> bool:
        """Execute analysis and cleanup."""
        print("\n" + "━" * 70)
        print("🔍 CORTEX Root Directory Analyzer")
        print("━" * 70 + "\n")

        try:
            self.analyze()
            self.generate_report()
            
            deleted, freed = self.delete_invalid_dirs()
            
            if deleted > 0:
                logger.info(f"\n✅ Cleanup complete: {deleted} directories deleted, {freed:.2f}MB freed")
                
                # Commit to git
                logger.info("\n📝 Committing changes to git...")
                subprocess.run(
                    ["git", "add", "-A"],
                    cwd=self.cortex_root,
                    capture_output=True
                )
                
                result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=self.cortex_root,
                    capture_output=True,
                    text=True
                )
                
                if result.stdout.strip():
                    subprocess.run(
                        [
                            "git",
                            "commit",
                            "-m",
                            f"CLEANUP: Remove invalid root directories ({freed:.1f}MB freed)\n\n"
                            f"Removed:\n{chr(10).join('  • ' + d for d in sorted(self.invalid_dirs))}\n\n"
                            f"AC-ROOT-CLEANUP-001: Repository root structure validated"
                        ],
                        cwd=self.cortex_root,
                        capture_output=True
                    )
                    logger.info("✅ Changes committed")

            print("✅ Analysis Complete")
            print("━" * 70 + "\n")
            
            return True

        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            return False


def main():
    """Execute root directory analysis."""
    cortex_root = Path(__file__).parent.parent
    analyzer = RootDirectoryAnalyzer(cortex_root)
    success = analyzer.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
