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

    def cleanup_prompts_folder(self) -> Tuple[int, float]:
        """Clean up .github/prompts/ folder sprawl - CORE-028 enforcement."""
        logger.info("🧹 Phase 1a: Prompts Folder Cleanup (.github/prompts/)")
        
        prompts_dir = self.cortex_root / ".github" / "prompts"
        if not prompts_dir.exists():
            logger.info("  ⚠️ .github/prompts/ not found, skipping")
            return 0, 0.0
        
        # ONLY *.prompt.md files allowed in root + these exceptions
        allowed_root_files = {
            "cortex-architect.prompt.md",  # Main architect prompt
            "CORTEX.prompt.md",  # Main production prompt
            "cortex-doc.prompt.md",  # Documentor prompt
            "response-format-standards.md",  # Formatting rules (kebab-case, OK)
            "README.md",  # Index
        }
        
        # Files that should move to guides/ (kebab-case guides)
        guide_files = {
            "business-wisdom-wiring.md",  # Phase 6 spec - guide
            "eventbus-debugger-guide.md",  # Debugger guide
            "multi-cycle-tdd-guide.md",  # TDD guide
        }
        
        # Create guides/ subdirectory if it doesn't exist
        guides_dir = prompts_dir / "guides"
        guides_dir.mkdir(exist_ok=True)
        
        # Create .archive/ subdirectory if it doesn't exist
        archive_dir = prompts_dir / ".archive"
        archive_dir.mkdir(exist_ok=True)
        
        cleaned = 0
        freed = 0.0
        moved = 0
        
        # Scan root files
        for md_file in prompts_dir.glob("*.md"):
            if md_file.name in allowed_root_files:
                continue
            
            # Check if it's in the guide files list
            if md_file.name in guide_files:
                target = guides_dir / md_file.name
                if not target.exists():
                    size_mb = md_file.stat().st_size / (1024 * 1024)
                    md_file.rename(target)
                    moved += 1
                    logger.info(f"  📦 Moved to guides/: {md_file.name} ({size_mb:.3f}MB)")
                else:
                    logger.info(f"  ⚠️  Already in guides/: {md_file.name}")
                continue
                
            # Check if it's a SCREAMING_CASE guide
            if md_file.name.isupper() or "-GUIDE.md" in md_file.name or md_file.name.startswith("WAVE-"):
                target = guides_dir / md_file.name
                if not target.exists():
                    size_mb = md_file.stat().st_size / (1024 * 1024)
                    md_file.rename(target)
                    moved += 1
                    logger.info(f"  📦 Moved to guides/: {md_file.name} ({size_mb:.3f}MB)")
                else:
                    logger.info(f"  ⚠️  Already in guides/: {md_file.name}")
            
            # Check if it should be archived (completion summaries, old templates)
            elif any(x in md_file.name.lower() for x in ["summary", "template", "completion"]):
                target = archive_dir / md_file.name
                if not target.exists():
                    size_mb = md_file.stat().st_size / (1024 * 1024)
                    md_file.rename(target)
                    moved += 1
                    logger.info(f"  📦 Moved to .archive/: {md_file.name} ({size_mb:.3f}MB)")
                else:
                    logger.info(f"  ⚠️  Already in .archive/: {md_file.name}")
            
            else:
                # Unknown file - report for manual review
                logger.warning(f"  ❓ Manual review needed: {md_file.name}")
        
        # Also check for *.txt files (like WAVE-7-COMPLETION-SUMMARY.txt)
        for txt_file in prompts_dir.glob("*.txt"):
            target = guides_dir / txt_file.name
            if not target.exists():
                size_mb = txt_file.stat().st_size / (1024 * 1024)
                txt_file.rename(target)
                moved += 1
                logger.info(f"  📦 Moved to guides/: {txt_file.name} ({size_mb:.3f}MB)")
        
        # Report on subdirectories
        if guides_dir.exists():
            guide_count = len(list(guides_dir.glob("*")))
            logger.info(f"  📂 guides/: {guide_count} files")
        
        if archive_dir.exists():
            archive_count = len(list(archive_dir.rglob("*")))
            logger.info(f"  📂 .archive/: {archive_count} files (historical)")
        
        logger.info(f"  ✅ Prompts folder reorganized: {moved} files moved")
        
        return moved, freed

    def cleanup_root_databases(self) -> Tuple[int, float]:
        """Remove orphaned database files from root directory."""
        logger.info("🧹 Phase 2a: Root Database Cleanup")
        
        # Known database files that should be in subdirectories
        db_files = [
            "intelligence_audit.db",
            "contract_validation_audit.db",
            "observability_audit.db",
            "solid_audit.db",
        ]
        
        cleaned = 0
        freed = 0.0
        
        for db_file in db_files:
            db_path = self.cortex_root / db_file
            if db_path.exists():
                try:
                    size_mb = db_path.stat().st_size / (1024 * 1024)
                    db_path.unlink()
                    cleaned += 1
                    freed += size_mb
                    logger.info(f"  ✅ Deleted: {db_file} ({size_mb:.2f}MB)")
                except Exception as e:
                    logger.error(f"  ❌ Failed to delete {db_file}: {e}")
        
        if cleaned == 0:
            logger.info("  ℹ️  No orphaned database files found")
        
        return cleaned, freed

    def cleanup_root_json_files(self) -> Tuple[int, float]:
        """Remove or relocate JSON files from root directory."""
        logger.info("🧹 Phase 2b: Root JSON File Cleanup")
        
        # Files that should be in reports/ or other subdirectories
        json_patterns = [
            "production-readiness-report.json",
            "*-report.json",
            "*-summary.json",
            "*-metrics.json",
        ]
        
        cleaned = 0
        freed = 0.0
        
        # Create reports directory if needed
        reports_dir = self.cortex_root / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        for pattern in json_patterns:
            for json_file in self.cortex_root.glob(pattern):
                # Only process files in root (not subdirectories)
                if json_file.parent != self.cortex_root:
                    continue
                    
                try:
                    size_mb = json_file.stat().st_size / (1024 * 1024)
                    
                    # Move report files to reports/ directory
                    if "report" in json_file.name or "summary" in json_file.name:
                        target = reports_dir / json_file.name
                        json_file.rename(target)
                        logger.info(f"  📦 Moved to reports/: {json_file.name} ({size_mb:.3f}MB)")
                    else:
                        # Delete other JSON files from root
                        json_file.unlink()
                        logger.info(f"  ✅ Deleted: {json_file.name} ({size_mb:.3f}MB)")
                    
                    cleaned += 1
                    freed += size_mb
                except Exception as e:
                    logger.error(f"  ❌ Failed to process {json_file}: {e}")
        
        if cleaned == 0:
            logger.info("  ℹ️  No JSON files found in root")
        
        return cleaned, freed

    def recreate_auto_cleanup_manager(self) -> bool:
        """Delete and recreate auto_cleanup_manager.py with clean template."""
        logger.info("🧹 Phase 2c: Auto Cleanup Manager Reset")
        
        target_file = self.cortex_root / "cortex" / "debugging" / "auto_cleanup_manager.py"
        
        if not target_file.exists():
            logger.info("  ℹ️  auto_cleanup_manager.py does not exist")
            return False
        
        try:
            # Delete existing file
            size_mb = target_file.stat().st_size / (1024 * 1024)
            target_file.unlink()
            logger.info(f"  ✅ Deleted corrupted file ({size_mb:.3f}MB)")
            
            # Create clean version with complete implementation
            clean_content = '''"""
Auto-Cleanup Manager - Automatic Debug Marker Removal

Purpose:
    Manages automatic cleanup of debug markers when debug sessions 
    are resolved (tests pass, issues fixed).

Authority:
    - ENH-089 (EventBus-Driven Debugger)
    - WAVE-R Execution Plan Stage 3

Strategies:
    - on_success: Remove markers when all tests pass
    - time_based: Notify developer if markers > 24 hours old

AC-ID: AC-WAVE-R-005
"""

from typing import Dict, List, Set
from pathlib import Path
from datetime import datetime, timedelta
import re


class AutoCleanupManager:
    """
    Manages automatic cleanup of debug markers.
    
    Strategies:
    - Detect resolved sessions (all tests passing)
    - Remove markers for resolved sessions
    - Identify stale markers (> 24 hours)
    - Notify developer of stale markers
    
    Example:
        >>> manager = AutoCleanupManager()
        >>> resolved = manager.cleanup_resolved_sessions(active_sessions)
        >>> # Returns list of resolved session IDs
    """
    
    def __init__(self):
        """Initialize AutoCleanupManager."""
        self.marker_pattern = re.compile(
            re.DOTALL
        )
    
    def cleanup_resolved_sessions(
        self,
        active_sessions: Dict[str, any]
    ) -> List[str]:
        """
        Cleanup markers for resolved sessions.
        
        Logic:
        1. Identify active sessions with status="active"
        2. Scan all tracked files for markers
        3. Remove markers for sessions NOT in active list
        
        Args:
            active_sessions: Dict of session_id -> DebugSession
        
        Returns:
            List of resolved session IDs
        """
        resolved_sessions = []
        
        # Get list of session IDs that should remain active
        active_session_ids = {
            session_id
            for session_id, session in active_sessions.items()
            if hasattr(session, "status") and session.status == "active"
        }
        
        # Collect all files with markers
        files_with_markers = self._find_files_with_markers()
        
        for file_path in files_with_markers:
            try:
                content = file_path.read_text()
                
                # Find all session IDs in markers
                matches = self.session_id_pattern.findall(content)
                
                # Check for old format markers
                has_old_format = self.old_format_pattern.search(content) is not None
                
                modified = False
                for session_id in matches:
                    # If session not in active list, remove markers
                    if session_id not in active_session_ids:
                        content = self._remove_marker(content, session_id)
                        resolved_sessions.append(session_id)
                        modified = True
                
                # Remove old format markers if no active sessions at all
                if has_old_format and not active_session_ids:
                    content = self._remove_old_format_markers(content)
                    modified = True
                
                # Write cleaned content only if modified
                if modified:
                    file_path.write_text(content)
                
            except Exception as e:
                print(f"Error cleaning {file_path}: {e}")
                continue
        
        return list(set(resolved_sessions))  # Deduplicate
    
    def cleanup_session(self, session_id: str) -> bool:
        """
        Cleanup markers for specific session.
        
        Args:
            session_id: Session ID to cleanup
        
        Returns:
            True if cleanup successful
        """
        files_with_markers = self._find_files_with_markers()
        cleaned = False
        
        for file_path in files_with_markers:
            try:
                content = file_path.read_text()
                
                if session_id in content:
                    content = self._remove_marker(content, session_id)
                    file_path.write_text(content)
                    cleaned = True
                    
            except Exception:
                continue
        
        return cleaned
    
    def check_stale_markers(self, max_age_hours: int = 24) -> List[Dict[str, any]]:
        """
        Identify stale markers (older than max_age_hours).
        
        Args:
            max_age_hours: Maximum age in hours before marker is stale
        
        Returns:
            List of dicts with {session_id, file_path, age_hours, timestamp}
        """
        stale_markers = []
        files_with_markers = self._find_files_with_markers()
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        
        # Pattern to extract session_id and timestamp from markers
        marker_info_pattern = re.compile(
            re.DOTALL
        )
        
        for file_path in files_with_markers:
            try:
                content = file_path.read_text()
                matches = marker_info_pattern.findall(content)
                
                for session_id, timestamp_str in matches:
                    try:
                        timestamp = datetime.fromisoformat(timestamp_str.strip())
                        age_hours = (datetime.now() - timestamp).total_seconds() / 3600
                        
                        if timestamp < cutoff:
                            stale_markers.append({
                                "session_id": session_id,
                                "file_path": str(file_path),
                                "age_hours": age_hours,
                                "timestamp": timestamp_str
                            })
                    except Exception:
                        continue
                        
            except Exception:
                continue
        
        return stale_markers
    
    def _find_files_with_markers(self) -> List[Path]:
        """
        
        Returns:
            List of file paths
        """
        # Search in cortex/ directory for .py files
        cortex_dir = Path("cortex")
        if not cortex_dir.exists():
            return []
        
        files_with_markers = []
        
        for py_file in cortex_dir.rglob("*.py"):
            try:
                content = py_file.read_text()
                    files_with_markers.append(py_file)
            except Exception:
                continue
        
        return files_with_markers
    
    def _remove_marker(self, content: str, session_id: str) -> str:
        """
        Remove marker for specific session from content.
        
        Args:
            content: File content
            session_id: Session ID to remove
        
        Returns:
            Content with marker removed
        """
        # Pattern to match specific session marker
        pattern = re.compile(
            re.DOTALL
        )
        
        return pattern.sub("", content)

    def _remove_old_format_markers(self, content: str) -> str:
        """
        Remove markers in old format (without session_id).
        
        Args:
            content: File content
        
        Returns:
            Content with old format markers removed
        """
        lines = content.split("\\n")
        return "\\n".join(filtered)
'''
            
            target_file.write_text(clean_content)
            logger.info(f"  ✅ Recreated clean auto_cleanup_manager.py")
            return True
            
        except Exception as e:
            logger.error(f"  ❌ Failed to recreate auto_cleanup_manager.py: {e}")
            return False

    def cleanup_debug_markers(self) -> int:
        logger.info("🧹 Phase 2: Debug Marker Cleanup")

        count = 0
        
        for py_file in self.cortex_root.glob("**/*.py"):
            # Skip virtual environments
            if ".venv" in str(py_file) or "venv" in str(py_file):
                continue
                
            try:
                content = py_file.read_text()
                
                # Skip if no debug markers
                if debug_pattern not in content:
                    continue

                # Remove debug markers
                lines = content.split("\n")
                filtered = [line for line in lines if debug_pattern not in line]
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
            "*.db",
        ]

        for rule in required_rules:
            if rule in content:
                logger.info(f"  ✅ Rule present: {rule}")
            else:
                logger.warning(f"  ⚠️ Rule missing: {rule}")

    def generate_summary(
        self, prompts_cleaned: int, prompts_freed: float, md_cleaned: int, md_freed: float, 
        db_cleaned: int, db_freed: float, json_cleaned: int, json_freed: float,
        auto_cleanup_reset: bool, debug_cleaned: int, cache_cleaned: int, cache_freed: float
    ) -> None:
        """Generate vacuum summary."""
        logger.info("\n" + "━" * 70)
        logger.info("📋 VACUUM SUMMARY")
        logger.info("━" * 70)
        logger.info(f"\nPrompts Folder (.github/prompts/):")
        logger.info(f"  Files cleaned: {prompts_cleaned}")
        logger.info(f"  Space freed: {prompts_freed:.2f}MB")
        logger.info(f"\nMarkdown Sprawl:")
        logger.info(f"  Files deleted: {md_cleaned}")
        logger.info(f"  Space freed: {md_freed:.2f}MB")
        logger.info(f"\nRoot Database Files:")
        logger.info(f"  Files deleted: {db_cleaned}")
        logger.info(f"  Space freed: {db_freed:.2f}MB")
        logger.info(f"\nRoot JSON Files:")
        logger.info(f"  Files processed: {json_cleaned}")
        logger.info(f"  Space freed: {json_freed:.2f}MB")
        logger.info(f"\nAuto Cleanup Manager:")
        logger.info(f"  Reset: {'✅ Yes' if auto_cleanup_reset else '⚠️ No'}")
        logger.info(f"\nDebug Markers:")
        logger.info(f"  Files cleaned: {debug_cleaned}")
        logger.info(f"\nCache & Artifacts:")
        logger.info(f"  Items cleaned: {cache_cleaned}")
        logger.info(f"  Space freed: {cache_freed:.2f}MB")
        logger.info(f"\nTotal:")
        logger.info(f"  Space freed: {prompts_freed + md_freed + db_freed + json_freed + cache_freed:.2f}MB")
        logger.info("━" * 70 + "\n")

    def run(self) -> bool:
        """Execute full vacuum sequence."""
        print("\n" + "━" * 70)
        print("🧹 CORTEX Repository Vacuum")
        print("━" * 70 + "\n")

        try:
            prompts_cleaned, prompts_freed = self.cleanup_prompts_folder()
            md_cleaned, md_freed = self.cleanup_markdown_sprawl()
            db_cleaned, db_freed = self.cleanup_root_databases()
            json_cleaned, json_freed = self.cleanup_root_json_files()
            auto_cleanup_reset = self.recreate_auto_cleanup_manager()
            debug_cleaned = self.cleanup_debug_markers()
            cache_cleaned, cache_freed = self.cleanup_pycache_and_artifacts()

            self.report_development_artifacts()
            self.verify_gitignore_rules()

            self.generate_summary(prompts_cleaned, prompts_freed, md_cleaned, md_freed, db_cleaned, db_freed, json_cleaned, json_freed, auto_cleanup_reset, debug_cleaned, cache_cleaned, cache_freed)

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
                freed_total = prompts_freed + md_freed + db_freed + json_freed + cache_freed
                subprocess.run(
                    [
                        "git",
                        "commit",
                        "-m",
                        f"VACUUM: Repository cleanup - {freed_total:.1f}MB freed\n\n"
                        f"Prompts folder reviewed: {prompts_cleaned} files cleaned ({prompts_freed:.2f}MB)\n"
                        f"Markdown sprawl removed: {md_cleaned} files ({md_freed:.2f}MB)\n"
                        f"Root database files removed: {db_cleaned} files ({db_freed:.2f}MB)\n"
                        f"Root JSON files processed: {json_cleaned} files ({json_freed:.2f}MB)\n"
                        f"Auto cleanup manager: {'reset' if auto_cleanup_reset else 'unchanged'}\n"
                        f"Debug markers cleaned: {debug_cleaned} files\n"
                        f"Cache cleaned: {cache_cleaned} items ({cache_freed:.2f}MB)\n\n"
                        f"AC-VACUUM-005: Auto cleanup manager reset\n"
                        f"AC-VACUUM-004: Root JSON file cleanup\n"
                        f"AC-VACUUM-003: Root database file cleanup\n"
                        f"AC-VACUUM-002: .github/prompts/ folder cleanup\n"
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
