"""
Production Cleanup Tool - Recursive folder cleanup for production readiness.

Safely archives/removes non-production files from .github/prompts and .github/agents
while preserving critical production assets.

CORE-002: No markdown sprawl
CORE-035: Single canonical implementation
"""

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


@dataclass
class CleanupConfig:
    """Configuration for production cleanup."""
    
    # Critical production files that MUST be preserved
    prompts_production: Optional[Set[str]] = None
    agents_production: Optional[Set[str]] = None
    
    # Archive directories
    archive_base: str = ".archive"
    
    def __post_init__(self):
        """Initialize production file sets."""
        if self.prompts_production is None:
            self.prompts_production = {
                "CORTEX.prompt.md",
                "cortex-architect.prompt.md",
                "cortex-doc.prompt.md",
                "MCP-SETUP-GUIDE.md",
                "README.md",
            }
        
        if self.agents_production is None:
            self.agents_production = {
                "AGENT-INDEX.md",
                "README.md",
                # Core agents subfolder preserved entirely
                "core/",
                # Support and education subfolders preserved
                "support/",
                "education/",
            }


def cleanup_production_folders(
    prompts_dir: Path,
    agents_dir: Path,
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Clean up .github/prompts and .github/agents for production.
    
    Args:
        prompts_dir: Path to .github/prompts
        agents_dir: Path to .github/agents
        dry_run: If True, only report what would be done
    
    Returns:
        Dictionary with cleanup results
    """
    config = CleanupConfig()
    results = {
        "prompts_archived": [],
        "agents_archived": [],
        "folders_preserved": [],
        "errors": [],
    }
    
    # Cleanup prompts directory
    if prompts_dir.exists():
        archive_path = prompts_dir / config.archive_base / "phase-docs"
        archive_path.mkdir(parents=True, exist_ok=True)
        
        for item in prompts_dir.iterdir():
            # Skip hidden folders, archives, and production files
            if item.name.startswith("."):
                continue
            if config.prompts_production and item.name in config.prompts_production:
                results["folders_preserved"].append(str(item))
                continue
            if item.name == "guides":
                # Keep guides folder but archive outdated content within it
                results["folders_preserved"].append(str(item))
                continue
            
            # Archive non-production files
            if not dry_run:
                try:
                    if item.is_file():
                        dest = archive_path / item.name
                        shutil.move(str(item), str(dest))
                        results["prompts_archived"].append(item.name)
                    elif item.is_dir() and item.name not in {"guides"}:
                        dest = archive_path / item.name
                        if dest.exists():
                            shutil.rmtree(dest)
                        shutil.move(str(item), str(dest))
                        results["prompts_archived"].append(f"{item.name}/")
                except Exception as e:
                    results["errors"].append(f"Prompts: {item.name} - {str(e)}")
            else:
                results["prompts_archived"].append(f"[DRY RUN] {item.name}")
    
    # Cleanup agents directory
    if agents_dir.exists():
        archive_path = agents_dir / config.archive_base / "phase-docs"
        archive_path.mkdir(parents=True, exist_ok=True)
        
        for item in agents_dir.iterdir():
            # Skip hidden folders, archives, and production structure
            if item.name.startswith("."):
                continue
            if config.agents_production and item.name in config.agents_production:
                results["folders_preserved"].append(str(item))
                continue
            if item.name == "archived":
                # Keep archived folder
                results["folders_preserved"].append(str(item))
                continue
            
            # Archive phase-specific documentation
            if not dry_run:
                try:
                    dest = archive_path / item.name
                    if item.is_file():
                        shutil.move(str(item), str(dest))
                        results["agents_archived"].append(item.name)
                    elif item.is_dir():
                        if dest.exists():
                            shutil.rmtree(dest)
                        shutil.move(str(item), str(dest))
                        results["agents_archived"].append(f"{item.name}/")
                except Exception as e:
                    results["errors"].append(f"Agents: {item.name} - {str(e)}")
            else:
                results["agents_archived"].append(f"[DRY RUN] {item.name}")
    
    return results


def generate_cleanup_report(results: Dict[str, Any]) -> str:
    """Generate human-readable cleanup report."""
    report = []
    report.append("━" * 60)
    report.append("📦 PRODUCTION CLEANUP REPORT")
    report.append("━" * 60)
    report.append("")
    
    if results["prompts_archived"]:
        report.append("📁 PROMPTS ARCHIVED:")
        for item in results["prompts_archived"]:
            report.append(f"  ✅ {item}")
        report.append("")
    
    if results["agents_archived"]:
        report.append("📁 AGENTS ARCHIVED:")
        for item in results["agents_archived"]:
            report.append(f"  ✅ {item}")
        report.append("")
    
    if results["folders_preserved"]:
        report.append("🔒 PRODUCTION ASSETS PRESERVED:")
        for item in results["folders_preserved"][:10]:  # Show first 10
            report.append(f"  ✅ {item}")
        if len(results["folders_preserved"]) > 10:
            preserved_count = len(results["folders_preserved"]) - 10
            report.append(f"  ... and {preserved_count} more")
        report.append("")
    
    if results["errors"]:
        report.append("⚠️ ERRORS:")
        for error in results["errors"]:
            report.append(f"  ❌ {error}")
        report.append("")
    
    report.append("━" * 60)
    report.append(f"✅ Archived: {len(results['prompts_archived']) + len(results['agents_archived'])} items")
    report.append(f"🔒 Preserved: {len(results['folders_preserved'])} assets")
    report.append(f"❌ Errors: {len(results['errors'])}")
    report.append("━" * 60)
    
    return "\n".join(report)
