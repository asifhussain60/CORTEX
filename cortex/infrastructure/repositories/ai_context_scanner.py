"""
AIContextScanner — scan a repository for AI development artifacts.

Phase 121 Sub-phase A | GAP-121-01, GAP-121-08.
Authority: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
           CORE-028 (snake_case), CORE-035 (single canonical implementation).
"""
from __future__ import annotations

from dataclasses import dataclass, field
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)

# Default location of vendor patterns config (relative to workspace root)
_DEFAULT_PATTERNS_PATH = (
    Path(__file__).parent.parent.parent.parent
    / "cortex-registry"
    / "config"
    / "ai-vendor-patterns.yaml"
)


@dataclass
class VendorInfo:
    """Detection result for a single AI vendor."""

    vendor: str
    confidence: float
    files_found: List[str] = field(default_factory=list)
    has_instructions: bool = False
    has_prompts: bool = False
    has_agents: bool = False


@dataclass
class AIContextResult:
    """Full AI context scan result for a repository."""

    vendors: List[VendorInfo] = field(default_factory=list)
    primary_vendor: Optional[str] = None
    total_ai_files: int = 0
    prompt_inventory: List[Dict[str, Any]] = field(default_factory=list)
    agent_inventory: List[Dict[str, Any]] = field(default_factory=list)


class AIContextScanner:
    """
    Scan a repository for AI development artifacts.

    Detects vendor-specific instruction files, prompts, and agents
    using YAML-driven detection patterns (cortex-registry/config/ai-vendor-patterns.yaml).
    Returns a structured :class:`AIContextResult` describing all AI context found.

    Example::

        scanner = AIContextScanner()
        result = scanner.scan(Path("/path/to/repo"))
        print(result.primary_vendor)
    """

    def __init__(
        self,
        patterns_yaml_path: Optional[Path] = None,
    ) -> None:
        """
        Initialise the scanner.

        Args:
            patterns_yaml_path: Override path to ai-vendor-patterns.yaml.
                Defaults to cortex-registry/config/ai-vendor-patterns.yaml.
        """
        path = patterns_yaml_path or _DEFAULT_PATTERNS_PATH
        self._patterns: Dict[str, Any] = self._load_patterns(path)

    # ── Public API ────────────────────────────────────────────────────────────

    def scan(self, repo_path: Path) -> AIContextResult:
        """
        Scan *repo_path* for AI development artifacts.

        Args:
            repo_path: Absolute path to the repository root.

        Returns:
            :class:`AIContextResult` with vendor breakdown, inventories, and
            a primary_vendor selection.
        """
        result = AIContextResult()

        for vendor_key, vendor_config in self._patterns.items():
            vendor_name: str = vendor_config.get("vendor", vendor_key)
            extractors: Dict[str, bool] = vendor_config.get("content_extractors", {})
            weight: float = float(vendor_config.get("confidence_weight", 0.8))
            detection_patterns: List[str] = vendor_config.get("detection_files", [])

            found = self._detect_vendor_files(repo_path, detection_patterns)
            if not found:
                continue

            confidence = self._compute_confidence(found, weight)
            info = VendorInfo(
                vendor=vendor_name,
                confidence=confidence,
                files_found=[str(Path(f).relative_to(repo_path)) for f in found],
            )

            # Instruction file detection
            instruction_patterns = [
                p for p in detection_patterns
                if "instruction" in p.lower() or "CLAUDE" in p or "AGENTS" in p
                or ".cursorrules" in p or ".clinerules" in p or ".windsurfrules" in p
                or ".aider" in p or "copilot-instructions" in p
            ]
            info.has_instructions = bool(
                self._detect_vendor_files(repo_path, instruction_patterns)
            )

            # Prompt inventory
            if extractors.get("prompt_inventory"):
                prompts = self._build_prompt_inventory(repo_path, found)
                info.has_prompts = bool(prompts)
                result.prompt_inventory.extend(prompts)

            # Agent inventory
            if extractors.get("agent_inventory"):
                agents = self._build_agent_inventory(repo_path, found)
                info.has_agents = bool(agents)
                result.agent_inventory.extend(agents)

            result.vendors.append(info)

        if result.vendors:
            result.primary_vendor = self._select_primary_vendor(result.vendors)
            result.total_ai_files = sum(len(v.files_found) for v in result.vendors)

        return result

    # ── Private helpers ───────────────────────────────────────────────────────

    def _load_patterns(self, yaml_path: Path) -> Dict[str, Any]:
        """Load vendor detection patterns from YAML config."""
        try:
            with open(yaml_path, "r", encoding="utf-8") as fh:
                return yaml.safe_load(fh) or {}
        except (FileNotFoundError, yaml.YAMLError) as exc:
            logger.warning("ai-vendor-patterns.yaml not loaded: %s", exc)
            return {}

    def _detect_vendor_files(
        self, repo_path: Path, patterns: List[str]
    ) -> List[Path]:
        """
        Resolve glob patterns relative to *repo_path* and return existing files.

        Args:
            repo_path: Repository root.
            patterns: List of glob patterns (e.g. '.github/prompts/*.md').

        Returns:
            List of found :class:`Path` objects.
        """
        found: List[Path] = []
        for pattern in patterns:
            if "**" in pattern or "*" in pattern:
                # Use rglob / glob
                if pattern.startswith("."):
                    parts = pattern.split("/", 1)
                    if len(parts) == 2:
                        base_dir = repo_path / parts[0]
                        if base_dir.is_dir():
                            found.extend(base_dir.glob(parts[1]))
                    else:
                        found.extend(repo_path.glob(pattern))
                else:
                    found.extend(repo_path.glob(pattern))
            else:
                candidate = repo_path / pattern
                if candidate.exists():
                    found.append(candidate)
        return [f for f in found if f.is_file()]

    def _compute_confidence(self, found_files: List[Path], weight: float) -> float:
        """
        Compute a confidence score (0.0–1.0) based on file count and weight.

        More files = higher confidence, capped at 1.0.

        Args:
            found_files: Detected files for this vendor.
            weight: Vendor-level confidence weight from YAML config.

        Returns:
            Confidence score between 0.0 and 1.0.
        """
        file_bonus = min(len(found_files) * 0.1, 0.3)
        return min(weight + file_bonus, 1.0)

    def _build_prompt_inventory(
        self, repo_path: Path, found_files: List[Path]
    ) -> List[Dict[str, Any]]:
        """
        Build a prompt inventory from detected prompt files.

        Args:
            repo_path: Repository root.
            found_files: Files found during vendor detection.

        Returns:
            List of prompt descriptors.
        """
        prompts: List[Dict[str, Any]] = []
        for f in found_files:
            if "prompt" in f.name.lower() or "prompts" in str(f).lower():
                purpose = self._extract_first_heading(f)
                prompts.append({
                    "file": str(f.relative_to(repo_path)),
                    "purpose": purpose,
                    "size_bytes": f.stat().st_size,
                })
        return prompts

    def _build_agent_inventory(
        self, repo_path: Path, found_files: List[Path]
    ) -> List[Dict[str, Any]]:
        """
        Build an agent inventory from detected agent files.

        Args:
            repo_path: Repository root.
            found_files: Files found during vendor detection.

        Returns:
            List of agent descriptors.
        """
        agents: List[Dict[str, Any]] = []
        for f in found_files:
            if "agent" in str(f).lower():
                specialization = self._extract_first_heading(f)
                agents.append({
                    "file": str(f.relative_to(repo_path)),
                    "specialization": specialization,
                    "trigger_keywords": [],
                })
        return agents

    def _extract_first_heading(self, file_path: Path) -> str:
        """Extract the first H1 heading from a markdown file as a purpose string."""
        try:
            for line in file_path.read_text(encoding="utf-8", errors="ignore").splitlines():
                stripped = line.strip()
                if stripped.startswith("# "):
                    return stripped[2:].strip()
            return file_path.stem.replace("-", " ").replace("_", " ").title()
        except OSError:
            return file_path.stem

    def _select_primary_vendor(self, vendors: List[VendorInfo]) -> str:
        """Select the vendor with the most files found (highest file count wins)."""
        return max(vendors, key=lambda v: len(v.files_found)).vendor


__all__ = ["AIContextScanner", "AIContextResult", "VendorInfo"]
