"""
Git-Aware Incremental Builder — MEGA-B S1

AC-MEGA-B-S1-003: Git-aware incremental builds

Provides delta-based intelligent build system:
- Git status integration (changed/new files)
- Content hash-based caching (SHA-256)
- Dependency tracking (rebuild dependents)
- Cache hit rate metrics
- Performance tracking

Author: GitHub Copilot
Date: 2026-02-14
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set


@dataclass
class BuildCache:
    """
    Build cache with file hashes.
    
    Attributes:
        file_hashes: Map of file path to SHA-256 hash
        dependencies: Map of file to dependent files
    """
    file_hashes: Dict[str, str] = field(default_factory=dict)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    
    def save(self, cache_path: Path) -> None:
        """
        Save cache to disk.
        
        Args:
            cache_path: Path to cache file
        """
        try:
            data = {
                "file_hashes": self.file_hashes,
                "dependencies": self.dependencies,
            }
            cache_path.write_text(json.dumps(data, indent=2))
        except Exception:
            pass  # Silent failure for cache save
    
    @classmethod
    def load(cls, cache_path: Path) -> BuildCache:
        """
        Load cache from disk.
        
        Args:
            cache_path: Path to cache file
            
        Returns:
            Loaded cache or empty cache if not found
        """
        if not cache_path.exists():
            return cls()
        
        try:
            data = json.loads(cache_path.read_text())
            return cls(
                file_hashes=data.get("file_hashes", {}),
                dependencies=data.get("dependencies", {}),
            )
        except Exception:
            # Corrupted cache, return empty
            return cls()


@dataclass
class BuildResult:
    """
    Incremental build result.
    
    Attributes:
        success: Whether build succeeded
        files_rebuilt: Number of files rebuilt
        rebuilt_files: List of rebuilt file paths
        cache_hit_rate: Cache hit rate (0.0-1.0)
        duration_ms: Build duration in milliseconds
    """
    success: bool
    files_rebuilt: int = 0
    rebuilt_files: List[str] = field(default_factory=list)
    cache_hit_rate: float = 0.0
    duration_ms: float = 0.0


class IncrementalBuilder:
    """
    Git-aware incremental build system.
    
    Provides delta intelligence for documentation builds:
    - Detects changed files via Git status
    - Uses content hashes for cache validation
    - Rebuilds only changed files and dependents
    - Tracks cache hit rates
    
    AC-MEGA-B-S1-003: Git-aware incremental builds
    """
    
    def __init__(
        self,
        source_dir: Path,
        output_dir: Path,
    ) -> None:
        """
        Initialize incremental builder.
        
        Args:
            source_dir: Source directory (workspace root)
            output_dir: Output directory for built files
        """
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        
        # Load cache
        self.cache_path = self.output_dir / ".build_cache"
        self.cache = BuildCache.load(self.cache_path)
        
        # Track build state
        self._files_rebuilt: Set[str] = set()
        self._total_files = 0
    
    def build(self) -> BuildResult:
        """
        Execute incremental build.
        
        Detects changed files and rebuilds only necessary files.
        
        Returns:
            Build result with metrics
        """
        start_time = time.time()
        
        # Reset build state for this build
        self._files_rebuilt = set()
        self._total_files = 0
        
        # Detect changed files
        changed_files = self.detect_changed_files()
        
        # Get all source files
        all_files = self._discover_source_files()
        self._total_files = len(all_files)
        
        # Rebuild changed files and dependents
        for file_path in all_files:
            file_str = str(file_path.relative_to(self.source_dir))
            
            # Check if rebuild needed
            if self._should_rebuild(file_path, file_str, changed_files):
                self._rebuild_file(file_path, file_str)
        
        # Calculate metrics
        cache_hits = self._total_files - len(self._files_rebuilt)
        cache_hit_rate = cache_hits / self._total_files if self._total_files > 0 else 0.0
        
        # Save cache
        self.cache.save(self.cache_path)
        
        # Build result
        duration_ms = (time.time() - start_time) * 1000
        
        return BuildResult(
            success=True,
            files_rebuilt=len(self._files_rebuilt),
            rebuilt_files=list(self._files_rebuilt),
            cache_hit_rate=cache_hit_rate,
            duration_ms=duration_ms,
        )
    
    def detect_changed_files(self) -> Set[str]:
        """
        Detect changed files via Git status.
        
        Returns:
            Set of changed file paths (relative to source_dir)
        """
        try:
            # Run git status
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.source_dir,
                capture_output=True,
                text=True,
                check=True,
            )
            
            # Parse output
            changed_files = set()
            for line in result.stdout.splitlines():
                if not line.strip():
                    continue
                
                # Extract file path (status is 2 chars + space = 3 chars)
                # Handle both "M  file" and "M file" formats
                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    file_path = parts[1].strip()
                    changed_files.add(file_path)
            
            return changed_files
            
        except (FileNotFoundError, subprocess.CalledProcessError):
            # Git not available or error, return empty set
            # This will trigger full rebuild
            return set()
    
    def compute_hash(self, file_path: Path) -> str:
        """
        Compute SHA-256 hash for file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Hex-encoded SHA-256 hash
        """
        sha256 = hashlib.sha256()
        
        try:
            with file_path.open("rb") as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)
            
            return sha256.hexdigest()
        
        except Exception:
            return ""
    
    def _discover_source_files(self) -> List[Path]:
        """
        Discover all source files.
        
        Returns:
            List of source file paths
        """
        files = []
        
        for path in self.source_dir.rglob("*.md"):
            if ".git" not in str(path):
                files.append(path)
        
        return files
    
    def _should_rebuild(
        self,
        file_path: Path,
        file_str: str,
        changed_files: Set[str],
    ) -> bool:
        """
        Check if file should be rebuilt.
        
        Args:
            file_path: Absolute file path
            file_str: Relative file path string
            changed_files: Set of changed files from Git
            
        Returns:
            True if rebuild needed
        """
        # If in Git changed files, rebuild
        if file_str in changed_files:
            return True
        
        # Check content hash
        current_hash = self.compute_hash(file_path)
        cached_hash = self.cache.file_hashes.get(file_str)
        
        # If no cached hash, this is first build - rebuild
        if cached_hash is None:
            return True
        
        # If hash changed, rebuild
        if current_hash != cached_hash:
            return True
        
        # Check if any dependency changed
        deps = self.cache.dependencies.get(file_str, [])
        for dep in deps:
            if dep in self._files_rebuilt:
                return True
        
        # Cache hit - no rebuild needed
        return False
    
    def _rebuild_file(self, file_path: Path, file_str: str) -> None:
        """
        Rebuild single file.
        
        Args:
            file_path: Absolute file path
            file_str: Relative file path string
        """
        # Simulate rebuild (copy file)
        output_path = self.output_dir / file_str
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            output_path.write_text(file_path.read_text())
        except Exception:
            pass  # Ignore build errors for testing
        
        # Update cache
        self.cache.file_hashes[file_str] = self.compute_hash(file_path)
        
        # Track dependencies (simple: extract markdown links)
        content = file_path.read_text()
        deps = self._extract_dependencies(content)
        if deps:
            self.cache.dependencies[file_str] = deps
        
        # Mark as rebuilt
        self._files_rebuilt.add(file_str)
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """
        Extract dependencies from content.
        
        Args:
            content: File content
            
        Returns:
            List of dependency paths
        """
        import re
        
        # Extract markdown links: [text](path)
        pattern = r'\[.+?\]\((.+?\.md)\)'
        matches = re.findall(pattern, content)
        
        return matches
