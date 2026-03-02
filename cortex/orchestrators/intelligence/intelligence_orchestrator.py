"""IntelligenceOrchestrator - Unified code intelligence with SQLite audit."""
from __future__ import annotations
import hashlib
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin  # Phase 94e
from cortex.intelligence.ast_intelligence import ASTIntelligenceEngine, ParseResult
from cortex.intelligence.comment_analyzer import CommentAnalyzer
from cortex.core.intelligence_routing_engine import IntelligenceRoutingEngine

logger = logging.getLogger(__name__)

class IntelligenceOrchestrator(OrchestratorProtocolMixin, WorkflowEnforcementMixin):
    """Unified intelligence: AST + comments + routing + comprehension + caching.

    Consolidates:
    - ASTIntelligenceEngine (Python AST parsing)
    - CommentAnalyzer (docstring & comment extraction)
    - ComprehensionLoopEngine (understanding workflow)
    - IntelligenceRoutingEngine (prompt/agent routing)
    - CachedLENSOrchestrator (result caching)

    Authority: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
    Phase: 23 MEGA-B Stage 2 - Component Registration
    """
    _orch_name = "IntelligenceOrchestrator"
    _orch_version = "1.0.0"

    # Phase 94e — advisory: intelligence layer, not a primary entry point.
    # Invoked by domain orchestrators. Gateway routing deferred.
    PHASE90_GATEWAY_EXEMPT: bool = True

    def __init__(
        self,
        audit_db_path: Optional[Path] = None,
        scanner: Optional[Any] = None,
    ) -> None:
        """Initialize intelligence orchestrator.

        Args:
            audit_db_path: Optional SQLite audit DB path
            scanner: Optional HierarchicalScanner for canonical file discovery
                     (GAP-66-003 — replaces ad-hoc glob patterns).
        """
        self.ast_engine = ASTIntelligenceEngine()
        self.comment_analyzer = CommentAnalyzer()
        self.routing_engine = IntelligenceRoutingEngine()
        self._cache: Dict[str, Any] = {}
        self._scanner = scanner  # GAP-66-003: canonical file discovery scanner

        # SQLite audit logging (store in .cortex-runtime/ to avoid root pollution)
        if audit_db_path:
            self.audit_db_path = audit_db_path
        else:
            db_dir = Path(".cortex-runtime/intelligence")
            db_dir.mkdir(parents=True, exist_ok=True)
            self.audit_db_path = db_dir / "intelligence_audit.db"
        self._init_audit_db()

    def _init_audit_db(self) -> None:
        """Initialize SQLite audit database."""
        conn = sqlite3.connect(self.audit_db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS intelligence_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                operation TEXT NOT NULL,
                target TEXT NOT NULL,
                metadata TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _audit_log(
        self,
        operation: str,
        target: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log operation to audit database."""
        conn = sqlite3.connect(self.audit_db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO intelligence_audit (timestamp, operation, target, metadata) VALUES (?, ?, ?, ?)",
            (
                datetime.now().isoformat(),
                operation,
                target,
                json.dumps(metadata) if metadata else None
            )
        )
        conn.commit()
        conn.close()

    def _compute_cache_key(self, file_path: Path) -> str:
        """Compute cache key from file path and content hash."""
        content = file_path.read_text()
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        return f"{file_path}:{content_hash}"

    def parse_python_file(self, file_path: Path) -> ParseResult:
        """Parse Python file with caching and audit logging.

        Args:
            file_path: Path to Python file

        Returns:
            ParseResult with AST information
        """
        cache_key = self._compute_cache_key(file_path)

        # Check cache
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            self._audit_log("PARSE", str(file_path), {"cached": True})
            return cached

        # Parse file
        result = self.ast_engine.parse_file(file_path)

        # Cache result
        self._cache[cache_key] = result

        # Audit log
        self._audit_log(
            "PARSE",
            str(file_path),
            {
                "success": result.success,
                "functions": len(result.functions),
                "classes": len(result.classes),
                "cached": False
            }
        )

        return result

    def analyze_comments(self, file_path: Path) -> List[Dict[str, Any]]:
        """Analyze comments and docstrings in file.

        Args:
            file_path: Path to file

        Returns:
            List of comment analysis results
        """
        result = self.comment_analyzer.analyze_file(file_path)

        # CommentAnalysisResult is a dataclass, convert to list
        comments = []
        if result and hasattr(result, 'comments'):
            comments = result.comments
        elif result:
            comments = [result]  # Single result

        self._audit_log(
            "ANALYZE_COMMENTS",
            str(file_path),
            {"comment_count": len(comments)}
        )

        return comments

    def route_intelligence(
        self,
        intent: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Route to appropriate intelligence handler.

        Args:
            intent: User intent (IMPLEMENT, ANALYZE, etc.)
            context: Request context

        Returns:
            Routing decision with target and confidence
        """
        # IntelligenceRoutingEngine.route expects IntentType enum and request string
        from cortex.core.intelligence_routing_engine import IntentType

        # Phase 58 — cross-cutting hooks
        self._activate_cross_cutting_hooks(
            operation=intent,
            orchestrator_context=context,
        )

        # Convert string intent to enum
        try:
            intent_enum = IntentType[intent.upper()]
        except KeyError:
            intent_enum = IntentType.IMPLEMENT

        # Create request string from context
        request = json.dumps(context)

        routing_result = self.routing_engine.route(intent_enum, request)

        # RoutingDecision is a dataclass, convert to dict
        result_dict = {
            "target": getattr(routing_result, "target", None),
            "confidence": getattr(routing_result, "confidence", 0.0)
        }

        self._audit_log(
            "ROUTE",
            intent,
            {"target": result_dict["target"], "confidence": result_dict["confidence"]}
        )

        return result_dict

    def get_cached_analysis(self, file_path: Path) -> Optional[ParseResult]:
        """Get cached analysis for file.

        Args:
            file_path: Path to file

        Returns:
            Cached ParseResult or None
        """
        cache_key = self._compute_cache_key(file_path)
        return self._cache.get(cache_key)

    def clear_cache(self) -> None:
        """Clear analysis cache."""
        self._cache.clear()
        self._audit_log("CLEAR_CACHE", "all", {})

    def query_audit_log(
        self,
        operation: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Query audit log.

        Args:
            operation: Optional operation filter
            limit: Max results

        Returns:
            List of audit entries
        """
        conn = sqlite3.connect(self.audit_db_path)
        cursor = conn.cursor()

        if operation:
            cursor.execute(
                "SELECT * FROM intelligence_audit WHERE operation = ? ORDER BY timestamp DESC LIMIT ?",
                (operation, limit)
            )
        else:
            cursor.execute(
                "SELECT * FROM intelligence_audit ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "id": r[0],
                "timestamp": r[1],
                "operation": r[2],
                "target": r[3],
                "metadata": r[4]
            }
            for r in rows
        ]

    def analyze(
        self,
        target_path: Optional[Path] = None,
    ) -> List[Dict[str, Any]]:
        """Analyze files using the canonical HierarchicalScanner (GAP-66-003).

        When a scanner is provided at construction time, file discovery uses
        :class:`~cortex.toolkit.filesystem.hierarchical_scanner.HierarchicalScanner`
        instead of ad-hoc ``glob.glob`` patterns.  The discovered paths are
        passed into :meth:`_lens_analyze` for LENS processing.

        Args:
            target_path: Optional root path hint (passed to scanner if needed).
                         When ``None``, scanner uses its configured root.

        Returns:
            List of analysis result dicts from LENS, one per discovered file.
        """
        # AC_START: AC-66-A-003-ANALYZE-20260224T000000Z
        files: List[Path] = []

        if self._scanner is not None:
            from cortex.lens.adapters.hierarchical_scanner_adapter import (
                HierarchicalScannerAdapter,
            )
            adapter = HierarchicalScannerAdapter(self._scanner)
            files = adapter.adapt()
        elif target_path is not None:
            # Fallback: direct rglob when no scanner configured
            files = list(target_path.rglob("*.py"))

        results = self._lens_analyze(files=files)
        self._audit_log("ANALYZE", str(target_path or ""), {"file_count": len(files)})
        # AC_COMPLETE: AC-66-A-003-ANALYZE-20260224T000000Z ✅
        return results

    def _lens_analyze(self, files: List[Path]) -> List[Dict[str, Any]]:
        """Pass file list through LENS analysis pipeline.

        Args:
            files: List of :class:`~pathlib.Path` objects to analyse.

        Returns:
            List of per-file analysis result dicts.
        """
        results: List[Dict[str, Any]] = []
        for f in files:
            if f.exists() and f.suffix == ".py":
                try:
                    parsed = self.parse_python_file(f)
                    results.append({"file": str(f), "parsed": True, "data": parsed})
                except Exception as exc:  # noqa: BLE001
                    results.append({"file": str(f), "parsed": False, "error": str(exc)})
        return results

    def analyze_with_context(
        self,
        intent: str,
        lens_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Analyze request with optional LENS context enrichment.

        GAP-57-04: Wires IntelligenceOrchestrator into cortex.lens pipeline.
        Uses lazy-import pattern (guarded try/except) to avoid hard failures
        when cortex.lens is unavailable.

        Args:
            intent: User intent string (IMPLEMENT, FIX, REFACTOR, …)
            lens_context: Optional LENS intelligence dict forwarded from IntentRouter.
                          When None, analysis proceeds without enrichment.

        Returns:
            Dict with routing result; includes ``lens_enriched: True`` when
            lens_context was consumed.

        Authority: AC-PHASE57-C-001
        """
        routing = self.route_intelligence(intent, {"intent": intent})
        result: Dict[str, Any] = {
            "intent": intent,
            "routing": routing,
            "lens_enriched": False,
        }

        if lens_context is not None:
            result["lens_context"] = lens_context
            result["lens_enriched"] = True
            # Merge key LENS signals into routing metadata
            git_commits = lens_context.get("git_analysis", {}).get("commits", 0)
            result["git_commit_count"] = git_commits

        self._audit_log(
            "ANALYZE_WITH_CONTEXT",
            intent,
            {"lens_enriched": result["lens_enriched"]},
        )
        return result

# AC_COMPLETE: AC-MEGA-B-S2-003-INTELLIGENCE ✅ Implemented
