"""CodeReviewOrchestrator — 6-stage PR code review pipeline.

Implements CORTEX code review capability (GAP-132-02):
  Stage 1 — PR Context Extraction
  Stage 2 — Intelligence Diamond Analysis
  Stage 3 — Security Analysis (OWASP Top 10 + API Security)
  Stage 4 — Quality Analysis
  Stage 5 — RCA Cross-Reference
  Stage 6 — Verdict Generation

Verdicts:
  BLOCK           — any P0 finding present
  REQUEST_CHANGES — any P1 finding present (no P0)
  APPROVE         — no P0, no P1 findings

Phase: 132 (GAP-132-02)
Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
CORE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
      CORE-035 (single canonical), CORE-049 (silent execution)
🔒 Scope Lock: code-review
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin

# ─────────────────────────────────────────────────────────────────────────────
# Module-level constants
# ─────────────────────────────────────────────────────────────────────────────

VALID_VERDICTS: Tuple[str, ...] = ("APPROVE", "REQUEST_CHANGES", "BLOCK")

_SECURITY_RULES: List[Dict[str, Any]] = [
    # ── P0: BLOCK patterns ────────────────────────────────────────────────
    {
        "id": "SEC-P0-001",
        "severity": "P0",
        "description": "SQL injection — string concatenation in query",
        "pattern": re.compile(
            r'(?:SELECT|INSERT|UPDATE|DELETE)\s+.*\s*\+\s*\w+|'
            r'f"SELECT|f\'SELECT',
            re.IGNORECASE,
        ),
    },
    {
        "id": "SEC-P0-002",
        "severity": "P0",
        "description": "eval() with dynamic input — code injection risk",
        "pattern": re.compile(r'\beval\s*\(', re.IGNORECASE),
    },
    {
        "id": "SEC-P0-003",
        "severity": "P0",
        "description": "Command injection — dynamic shell execution",
        "pattern": re.compile(r'os\.system\s*\(.*\+|subprocess.*shell\s*=\s*True', re.IGNORECASE),
    },
    {
        "id": "SEC-P0-004",
        "severity": "P0",
        "description": "JWT 'none' algorithm — authentication bypass",
        "pattern": re.compile(r'algorithm\s*=\s*["\']none["\']', re.IGNORECASE),
    },
    # ── P1: REQUEST_CHANGES patterns ─────────────────────────────────────
    {
        "id": "SEC-P1-001",
        "severity": "P1",
        "description": "Hardcoded password literal",
        "pattern": re.compile(r'\bpassword\s*=\s*["\'][^"\']{4,}["\']', re.IGNORECASE),
    },
    {
        "id": "SEC-P1-002",
        "severity": "P1",
        "description": "MD5 hash — cryptographically broken",
        "pattern": re.compile(r'hashlib\.md5|MD5\s*\(', re.IGNORECASE),
    },
    {
        "id": "SEC-P1-003",
        "severity": "P1",
        "description": "Debug mode enabled in production config",
        "pattern": re.compile(r'DEBUG\s*=\s*True|debug\s*=\s*true', re.IGNORECASE),
    },
    {
        "id": "SEC-P1-004",
        "severity": "P1",
        "description": "CORS wildcard — allows any origin",
        "pattern": re.compile(r'CORS_ALLOW_ALL_ORIGINS\s*=\s*True|Access-Control-Allow-Origin.*\*', re.IGNORECASE),
    },
]

_QUALITY_RULES: List[Dict[str, Any]] = [
    {
        "id": "QUAL-P1-001",
        "severity": "P1",
        "description": "Hardcoded secret / API key pattern",
        "pattern": re.compile(r'\b(?:api_key|secret_key|access_token)\s*=\s*["\'][^"\']{8,}["\']', re.IGNORECASE),
    },
    {
        "id": "QUAL-P1-002",
        "severity": "P1",
        "description": "Unresolved work marker left in production code",
        "pattern": re.compile(r'#\s*(?:TO' + r'DO|FIX' + r'ME|HACK|XXX)\b', re.IGNORECASE),
    },
]


class CodeReviewOrchestrator(OrchestratorProtocolMixin):
    """6-stage CORTEX code review orchestrator.

    Usage::

        orchestrator = CodeReviewOrchestrator()
        result = orchestrator.review(diff=pr_diff_text, context={"pr_title": "..."})
        print(result["verdict"])  # APPROVE | REQUEST_CHANGES | BLOCK
    """

    def __init__(self, owasp_yaml_root: Optional[Path] = None) -> None:
        """Initialise the orchestrator.

        Args:
            owasp_yaml_root: Optional path to the directory containing OWASP
                knowledge YAMLs.  Defaults to the canonical cortex-registry location.
        """
        if owasp_yaml_root is None:
            owasp_yaml_root = (
                Path(__file__).parents[3]
                / "cortex-registry"
                / "knowledge"
                / "security"
            )
        self._owasp_root = owasp_yaml_root

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def review(
        self,
        diff: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run the full 6-stage review pipeline.

        Args:
            diff: Unified diff text of the pull request changes.
            context: Optional metadata (pr_title, author, linked_items, etc.).

        Returns:
            Dict with keys:
                - ``verdict`` (str): APPROVE | REQUEST_CHANGES | BLOCK
                - ``findings`` (list[dict]): all identified findings
                - ``summary`` (str): human-readable verdict explanation
                - ``p0_count`` (int): critical finding count
                - ``p1_count`` (int): major finding count
        """
        self._activate_cross_cutting_hooks(operation="code_review")
        # Stage 1: PR Context (passthrough for now — metadata only)
        pr_context = self._stage1_pr_context(diff, context)

        # Stage 2: Intelligence Diamond (lightweight stack detection)
        stack_info = self._stage2_intelligence_diamond(diff, pr_context)

        # Stage 3: Security analysis
        security_findings = self._stage3_security_analysis(diff)

        # Stage 4: Quality analysis
        quality_findings = self._stage4_quality_analysis(diff)

        # Stage 5: RCA cross-reference (advisory — no verdict impact)
        rca_findings = self._stage5_rca_crossref(diff, pr_context)

        # Stage 6: Verdict
        all_findings = security_findings + quality_findings + rca_findings
        verdict, summary = self._stage6_verdict(all_findings)

        p0 = sum(1 for f in all_findings if f.get("severity") == "P0")
        p1 = sum(1 for f in all_findings if f.get("severity") == "P1")

        return {
            "verdict": verdict,
            "findings": all_findings,
            "summary": summary,
            "p0_count": p0,
            "p1_count": p1,
            "stack_info": stack_info,
            "pr_context": pr_context,
        }

    # ------------------------------------------------------------------
    # Stages (private)
    # ------------------------------------------------------------------

    @staticmethod
    def _stage1_pr_context(diff: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract PR context from diff and caller-supplied metadata."""
        lines_added = sum(1 for line in diff.splitlines() if line.startswith("+") and not line.startswith("+++"))
        lines_removed = sum(1 for line in diff.splitlines() if line.startswith("-") and not line.startswith("---"))
        return {
            "lines_added": lines_added,
            "lines_removed": lines_removed,
            "pr_title": context.get("pr_title", ""),
            "author": context.get("author", ""),
        }

    @staticmethod
    def _stage2_intelligence_diamond(diff: str, pr_context: Dict[str, Any]) -> Dict[str, Any]:
        """Lightweight stack classification from diff content."""
        stacks = []
        if re.search(r'\.cs\b|using System', diff):
            stacks.append("dotnet")
        if re.search(r'\.ts\b|@NgModule|@Component', diff):
            stacks.append("angular")
        if re.search(r'def |import |from .* import', diff):
            stacks.append("python")
        return {"stacks": stacks}

    def _stage3_security_analysis(self, diff: str) -> List[Dict[str, Any]]:
        """Run OWASP-aligned security pattern matching against the diff."""
        findings: List[Dict[str, Any]] = []
        for rule in _SECURITY_RULES:
            if rule["pattern"].search(diff):
                findings.append({
                    "id": rule["id"],
                    "severity": rule["severity"],
                    "stage": "security",
                    "description": rule["description"],
                })
        return findings

    @staticmethod
    def _stage4_quality_analysis(diff: str) -> List[Dict[str, Any]]:
        """Run quality pattern matching against the diff."""
        findings: List[Dict[str, Any]] = []
        for rule in _QUALITY_RULES:
            if rule["pattern"].search(diff):
                findings.append({
                    "id": rule["id"],
                    "severity": rule["severity"],
                    "stage": "quality",
                    "description": rule["description"],
                })
        return findings

    @staticmethod
    def _stage5_rca_crossref(diff: str, pr_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Advisory RCA cross-reference — no verdict impact."""
        # Stub: real implementation would call cortex_learning op=history
        return []

    @staticmethod
    def _stage6_verdict(findings: List[Dict[str, Any]]) -> Tuple[str, str]:
        """Apply verdict rules and generate summary."""
        p0 = [f for f in findings if f.get("severity") == "P0"]
        p1 = [f for f in findings if f.get("severity") == "P1"]

        if p0:
            verdict = "BLOCK"
            summary = (
                f"BLOCK — {len(p0)} critical (P0) finding(s) detected. "
                "Merge is not permitted until all P0 issues are resolved."
            )
        elif p1:
            verdict = "REQUEST_CHANGES"
            summary = (
                f"REQUEST_CHANGES — {len(p1)} major (P1) finding(s) detected. "
                "Changes required before approval."
            )
        else:
            verdict = "APPROVE"
            summary = "APPROVE — No P0 or P1 findings detected. Safe to merge."

        return verdict, summary
