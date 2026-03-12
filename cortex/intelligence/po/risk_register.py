"""Risk Register — automated risk detection and scoring from work items (GAP-129-12)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

_PATTERNS_FILE = (
    Path(__file__).parent.parent.parent.parent
    / "cortex-registry"
    / "knowledge"
    / "po"
    / "risk-signal-patterns.yaml"
)


class RiskRegister:
    """Scans work items for risk signals and produces a scored risk list.

    Risk score = likelihood (1-5) × impact (1-5), max 25.
    High risk: score >= 15
    Medium risk: score >= 6
    Low risk: score < 6
    """

    def __init__(self, patterns_file: Path | None = None) -> None:
        self._patterns_file = Path(patterns_file) if patterns_file else _PATTERNS_FILE
        self._patterns: List[Dict[str, Any]] = self._load_patterns()

    def scan(self, work_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Scan work items and return a scored risk list.

        Returns:
            list of risk entries:
                story_id, title, risk_signal, likelihood, impact, score, level
        """
        risks: List[Dict[str, Any]] = []
        for item in work_items:
            text = (
                f"{item.get('title', '')} {item.get('description', '')} {item.get('tags', '')}"
            ).lower()
            for pattern in self._patterns:
                regexp = pattern.get("pattern", "")
                if regexp and re.search(regexp, text, re.IGNORECASE):
                    likelihood = int(pattern.get("likelihood", 3))
                    impact = int(pattern.get("impact", 3))
                    score = likelihood * impact
                    risks.append(
                        {
                            "story_id": item.get("story_id", ""),
                            "title": item.get("title", ""),
                            "risk_signal": pattern.get("signal", "unknown"),
                            "likelihood": likelihood,
                            "impact": impact,
                            "score": score,
                            "level": self._level(score),
                        }
                    )
        return sorted(risks, key=lambda r: r["score"], reverse=True)

    def high_risk_count(self, work_items: List[Dict[str, Any]]) -> int:
        """Return the count of high-risk findings."""
        return sum(1 for r in self.scan(work_items) if r["level"] == "HIGH")

    def summary(self, work_items: List[Dict[str, Any]]) -> Dict[str, int]:
        """Return counts by risk level: HIGH / MEDIUM / LOW."""
        risks = self.scan(work_items)
        return {
            "HIGH": sum(1 for r in risks if r["level"] == "HIGH"),
            "MEDIUM": sum(1 for r in risks if r["level"] == "MEDIUM"),
            "LOW": sum(1 for r in risks if r["level"] == "LOW"),
            "total": len(risks),
        }

    @staticmethod
    def _level(score: int) -> str:
        if score >= 15:
            return "HIGH"
        if score >= 6:
            return "MEDIUM"
        return "LOW"

    def _load_patterns(self) -> List[Dict[str, Any]]:
        """Load risk signal patterns from YAML. Falls back to built-ins if file missing."""
        if self._patterns_file.exists() and yaml is not None:
            try:
                data = yaml.safe_load(self._patterns_file.read_text())
                return data.get("patterns", [])
            except Exception:
                pass
        return self._builtin_patterns()

    @staticmethod
    def _builtin_patterns() -> List[Dict[str, Any]]:
        return [
            {"signal": "external_dependency", "pattern": r"\bexternal\b|\bthird.party\b|\bvendor\b", "likelihood": 4, "impact": 4},
            {"signal": "compliance_tag", "pattern": r"\bcompliance\b|\bgdpr\b|\bsox\b|\bpci\b|\baudit\b", "likelihood": 3, "impact": 5},
            {"signal": "blocked_item", "pattern": r"\bblocked\b|\bimpediment\b|\bwaiting.on\b", "likelihood": 4, "impact": 3},
            {"signal": "scope_expansion", "pattern": r"\bin.scope\b|\bexpand\b|\badd to this\b|\balso include\b", "likelihood": 3, "impact": 3},
            {"signal": "missing_ac", "pattern": r"\bno acceptance criteria\b|\bac not defined\b|\btbd\b", "likelihood": 3, "impact": 4},
            {"signal": "security_concern", "pattern": r"\bsecurity\b|\bauth\b|\bpermission\b|\bvulnerability\b", "likelihood": 2, "impact": 5},
        ]
