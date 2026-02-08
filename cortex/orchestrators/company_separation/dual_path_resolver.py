"""Phase 47 S2: Dual-Path Resolution for Company/CORTEX.

Implement dual-path resolver: registry first, legacy fallback.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from pathlib import Path
import yaml


@dataclass
class ResolutionResult:
    """Result of path resolution."""

    found: bool
    source: str  # "company_registry", "cortex_master", "legacy", "not_found"
    path: Optional[str]
    content: Optional[Dict[str, Any]]
    resolution_chain: List[str]


class DualPathResolver:
    """Resolver for company/CORTEX dual-path resolution.

    Resolution order:
    1. company/ (highest precedence - company overrides)
    2. _cortex-master/ (CORTEX defaults)
    3. legacy company/ (backward compatibility)
    """

    def __init__(
        self,
        registry_root: str = "/Users/asifhussain/PROJECTS/CORTEX/cortex-registry",
        legacy_root: str = "/Users/asifhussain/PROJECTS/CORTEX/company",
    ):
        """Initialize resolver.

        Args:
            registry_root: Root path to cortex-registry
            legacy_root: Root path to legacy company directory
        """
        self.registry_root = registry_root
        self.legacy_root = legacy_root
        self.company_registry_root = f"{registry_root}/company"
        self.cortex_master_root = f"{registry_root}/_cortex-master"
        self.cache: Dict[str, ResolutionResult] = {}

    def resolve(self, resource_path: str, clear_cache: bool = False) -> ResolutionResult:
        """Resolve a resource using dual-path strategy.

        Args:
            resource_path: Relative path (e.g., "domains/example.yaml")
            clear_cache: Whether to clear resolution cache

        Returns:
            ResolutionResult with resolution details.
        """
        if clear_cache:
            self.cache.clear()

        if resource_path in self.cache:
            return self.cache[resource_path]

        resolution_chain = []

        # Try 1: Company registry (highest precedence)
        company_path = f"{self.company_registry_root}/{resource_path}"
        if self._file_exists(company_path):
            content = self._load_yaml(company_path)
            result = ResolutionResult(
                found=True,
                source="company_registry",
                path=company_path,
                content=content,
                resolution_chain=resolution_chain + ["company_registry ✓"],
            )
            self.cache[resource_path] = result
            return result
        resolution_chain.append("company_registry ✗")

        # Try 2: CORTEX master registry
        cortex_path = f"{self.cortex_master_root}/{resource_path}"
        if self._file_exists(cortex_path):
            content = self._load_yaml(cortex_path)
            result = ResolutionResult(
                found=True,
                source="cortex_master",
                path=cortex_path,
                content=content,
                resolution_chain=resolution_chain + ["cortex_master ✓"],
            )
            self.cache[resource_path] = result
            return result
        resolution_chain.append("cortex_master ✗")

        # Try 3: Legacy company directory (backward compatibility)
        legacy_path = f"{self.legacy_root}/{resource_path}"
        if self._file_exists(legacy_path):
            content = self._load_yaml(legacy_path)
            result = ResolutionResult(
                found=True,
                source="legacy",
                path=legacy_path,
                content=content,
                resolution_chain=resolution_chain + ["legacy ✓"],
            )
            self.cache[resource_path] = result
            return result
        resolution_chain.append("legacy ✗")

        # Not found
        result = ResolutionResult(
            found=False,
            source="not_found",
            path=None,
            content=None,
            resolution_chain=resolution_chain,
        )
        self.cache[resource_path] = result
        return result

    def resolve_all(self, pattern: str) -> List[ResolutionResult]:
        """Resolve all resources matching pattern.

        Args:
            pattern: Glob pattern (e.g., "domains/*.yaml")

        Returns:
            List of ResolutionResult for all matches.
        """
        results = []

        # Check company registry
        company_path = Path(f"{self.company_registry_root}/{pattern}")
        for file in company_path.glob("*"):
            results.append(self.resolve(file.relative_to(self.company_registry_root).__str__()))

        return results

    def get_resolution_stats(self) -> Dict[str, int]:
        """Get statistics about resolutions.

        Returns:
            Dictionary with resolution statistics.
        """
        stats = {
            "total_resolutions": len(self.cache),
            "company_registry_hits": 0,
            "cortex_master_hits": 0,
            "legacy_hits": 0,
            "not_found": 0,
        }

        for result in self.cache.values():
            if result.source == "company_registry":
                stats["company_registry_hits"] += 1
            elif result.source == "cortex_master":
                stats["cortex_master_hits"] += 1
            elif result.source == "legacy":
                stats["legacy_hits"] += 1
            elif result.source == "not_found":
                stats["not_found"] += 1

        return stats

    def _file_exists(self, path: str) -> bool:
        """Check if file exists.

        Args:
            path: File path to check

        Returns:
            True if file exists.
        """
        return Path(path).exists()

    def _load_yaml(self, path: str) -> Dict[str, Any]:
        """Load YAML file.

        Args:
            path: YAML file path

        Returns:
            Dictionary with YAML content or empty dict if load failed.
        """
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}


class MigrationValidator:
    """Validator for company/CORTEX migration.

    Validates that migration doesn't break existing code paths.
    """

    def __init__(self, resolver: DualPathResolver):
        """Initialize validator.

        Args:
            resolver: DualPathResolver instance
        """
        self.resolver = resolver
        self.issues: List[str] = []

    def validate_migration(self, source_dir: str, target_dir: str) -> bool:
        """Validate migration from source to target.

        Args:
            source_dir: Source directory (e.g., "company/")
            target_dir: Target directory (e.g., "cortex-registry/company/")

        Returns:
            True if migration is valid.
        """
        source_path = Path(source_dir)
        target_path = Path(target_dir)

        if not source_path.exists():
            self.issues.append(f"Source directory not found: {source_dir}")
            return False

        # Check all files can be resolved
        for file_path in source_path.rglob("*.yaml"):
            relative = file_path.relative_to(source_path)
            result = self.resolver.resolve(str(relative))

            if not result.found:
                self.issues.append(f"Cannot resolve: {relative}")
                return False

        return len(self.issues) == 0

    def get_issues(self) -> List[str]:
        """Get validation issues.

        Returns:
            List of issue descriptions.
        """
        return self.issues
