#!/usr/bin/env python3
"""
CORTEX Repository Vacuum Orchestrator

Comprehensive cleanup of markdown sprawl, stale artifacts, and development clutter.
Based on cortex-architect.prompt.md § HEXA-MODE cleanup protocols

AC-VACUUM-001: Repository cleanup and consolidation
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple
import subprocess
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class VacuumOrchestrator:
    """Orchestrates repository cleanup following HEXA-MODE protocols."""

    def __init__(self, cortex_root: Path):
        self.cortex_root = cortex_root
        self.cleaned_count = 0
        self.freed_mb = 0.0

    def cleanup_markdown_sprawl(self) -> Tuple[int, float]:
        """Remove stale markdown files (CORE-002 enforcement)."""
        logger.info("🧹 Phase 1: Markdown Sprawl Cleanup")

        patterns = [
            "*-summary.md",
            "*-report.md",
            "*-debug.md",
            "*-checkpoint.md",
            "TEMP-*.md",
            "_*.md",
        ]

        excluded_dirs = {
            ".cortex",
            ".github",
            "cortex-registry",
            "deployment",
            "docs",
        }

        cleaned = 0
        freed = 0.0

        for pattern in patterns:
            for md_file in self.cortex_root.glob(f"**/{pattern}"):
                # Skip excluded directories
                if any(excluded in md_file.parts for excluded in excluded_dirs):
                    continue

                try:
                    size_mb = md_file.stat().st_size / (1024 * 1024)
                    md_file.unlink()
                    cleaned += 1
                    freed += size_mb
                    logger.info(f"  ✅ Deleted: {md_file.name} ({size_mb:.2f}MB)")
                except Exception as e:
                    logger.error(f"  ❌ Failed to delete {md_file}: {e}")

        return cleaned, freed

    def cleanup_debug_markers(self) -> int:
        logger.info("🧹 Phase 2: Debug Marker Cleanup")

        count = 0
        for py_file in self.cortex_root.glob("**/*.py"):
            try:
                content = py_file.read_text()

                    continue

                # Remove debug markers
                lines = content.split("\n")
                new_content = "\n".join(filtered)

                if new_content != content:
                    py_file.write_text(new_content)
                    count += 1
                    logger.info(f"  ✅ Cleaned: {py_file.relative_to(self.cortex_root)}")
            except Exception as e:
                logger.error(f"  ❌ Error processing {py_file}: {e}")

        return count

    def cleanup_pycache_and_artifacts(self) -> Tuple[int, float]:
        """Remove __pycache__, .pyc files, and build artifacts."""
        logger.info("🧹 Phase 3: Python Cache & Artifacts")

        patterns = [
            "**/__pycache__",
            "**/*.pyc",
            "**/*.pyo",
            "**/.pytest_cache",
            "**/.coverage",
            "**/build",
            "**/dist",
            "**/*.egg-info",
        ]

        cleaned = 0
        freed = 0.0

        for pattern in patterns:
            for path in self.cortex_root.glob(pattern):
                try:
                    if path.is_dir():
                        import shutil

                        size = sum(
                            f.stat().st_size
                            for f in path.rglob("*")
                            if f.is_file()
                        )
                        freed += size / (1024 * 1024)
                        shutil.rmtree(path)
                        cleaned += 1
                        logger.info(
                            f"  ✅ Removed directory: {path.name} ({size / (1024 * 1024):.2f}MB)"
                        )
                    else:
                        freed += path.stat().st_size / (1024 * 1024)
                        path.unlink()
                        cleaned += 1
                        logger.info(f"  ✅ Removed file: {path.name}")
                except Exception as e:
                    logger.error(f"  ❌ Error cleaning {path}: {e}")

        return cleaned, freed

    def report_development_artifacts(self) -> None:
        """Report on large development artifacts for manual review."""
        logger.info("📊 Phase 4: Development Artifacts Audit")

        artifacts = [
            ("_workspaces/", "Development workspaces"),
            ("cortex_brain/", "Legacy brain module"),
            ("cortex_lens/", "Legacy lens module"),
        ]

        for path, description in artifacts:
            full_path = self.cortex_root / path
            if full_path.exists():
                size_mb = sum(
                    f.stat().st_size for f in full_path.rglob("*") if f.is_file()
                ) / (1024 * 1024)
                logger.info(f"  📦 {description}: {path} ({size_mb:.1f}MB)")
                logger.info(f"     → Ready for archival if no longer needed")

    def verify_gitignore_rules(self) -> None:
        """Verify .gitignore has cleanup rules."""
        logger.info("✅ Phase 5: .gitignore Verification")

        gitignore = self.cortex_root / ".gitignore"
        if not gitignore.exists():
            logger.warning("  ⚠️ .gitignore not found!")
            return

        content = gitignore.read_text()
        required_rules = [
            "__pycache__",
            "*.pyc",
            ".pytest_cache",
            ".coverage",
        ]

        for rule in required_rules:
            if rule in content:
                logger.info(f"  ✅ Rule present: {rule}")
            else:
                logger.warning(f"  ⚠️ Rule missing: {rule}")

    def generate_summary(
        self, md_cleaned: int, md_freed: float, debug_cleaned: int, cache_cleaned: int, cache_freed: float
    ) -> None:
        """Generate vacuum summary."""
        logger.info("\n" + "━" * 70)
        logger.info("📋 VACUUM SUMMARY")
        logger.info("━" * 70)
        logger.info(f"\nMarkdown Sprawl:")
        logger.info(f"  Files deleted: {md_cleaned}")
        logger.info(f"  Space freed: {md_freed:.2f}MB")
        logger.info(f"\nDebug Markers:")
        logger.info(f"  Files cleaned: {debug_cleaned}")
        logger.info(f"\nCache & Artifacts:")
        logger.info(f"  Items cleaned: {cache_cleaned}")
        logger.info(f"  Space freed: {cache_freed:.2f}MB")
        logger.info(f"\nTotal:")
        logger.info(f"  Space freed: {md_freed + cache_freed:.2f}MB")
        logger.info("━" * 70 + "\n")

    def run(self) -> bool:
        """Execute full vacuum sequence."""
        print("\n" + "━" * 70)
        print("🧹 CORTEX Repository Vacuum")
        print("━" * 70 + "\n")

        try:
            md_cleaned, md_freed = self.cleanup_markdown_sprawl()
            debug_cleaned = self.cleanup_debug_markers()
            cache_cleaned, cache_freed = self.cleanup_pycache_and_artifacts()

            self.report_development_artifacts()
            self.verify_gitignore_rules()

            self.generate_summary(md_cleaned, md_freed, debug_cleaned, cache_cleaned, cache_freed)

            # Git cleanup
            logger.info("📝 Git cleanup...")
            subprocess.run(["git", "add", "-A"], cwd=self.cortex_root, capture_output=True)

            # Check if there are changes to commit
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.cortex_root,
                capture_output=True,
                text=True,
            )

            if result.stdout.strip():
                subprocess.run(
                    [
                        "git",
                        "commit",
                        "-m",
                        f"VACUUM: Repository cleanup - {md_freed + cache_freed:.1f}MB freed\n\n"
                        f"Markdown sprawl removed: {md_cleaned} files ({md_freed:.2f}MB)\n"
                        f"Debug markers cleaned: {debug_cleaned} files\n"
                        f"Cache cleaned: {cache_cleaned} items ({cache_freed:.2f}MB)\n\n"
                        f"AC-VACUUM-001: Repository maintenance complete",
                    ],
                    cwd=self.cortex_root,
                    capture_output=True,
                )
                logger.info("✅ Changes committed to git")
            else:
                logger.info("ℹ️ No changes to commit")

            print("✅ Vacuum Complete")
            print("━" * 70 + "\n")

            return True

        except Exception as e:
            logger.error(f"❌ Vacuum failed: {e}")
            return False


def main():
    """Execute repository vacuum."""
    cortex_root = Path(__file__).parent.parent
    vacuum = VacuumOrchestrator(cortex_root)
    success = vacuum.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
