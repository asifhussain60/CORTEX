"""
IntelligenceWiringBridges — lightweight adapters for Phase 66-B P1 gaps.

Provides thin bridge functions and classes that wire intelligence components
(LENS, BrainTiers, ResponseTemplate, RetrievalOptimizer) into the toolkit
and workflow layers without requiring heavy restructuring.

Authority: GAP-66-006, GAP-66-009, GAP-66-010, GAP-66-011, GAP-66-012,
           GAP-66-015, GAP-66-016 | Phase 66-B | SWEEP-66-INTELLIGENCE-MATRIX
CORE-011: type hints on all functions
CORE-012: docstrings on all public APIs

AC_START: AC-66-B-WIRING-BRIDGES-20260224T000000Z
"""
from __future__ import annotations

from typing import Any, Dict, List

# ──────────────────────────────────────────────────────────────────────────────
# GAP-66-006: LENS → BatchProcessor semantic index pipe
# ──────────────────────────────────────────────────────────────────────────────


def lens_pipe_to_batch(
    lens_results: List[Dict[str, Any]],
    batch_processor: Any,
) -> int:
    """Pipe LENS semantic analysis results into a BatchProcessor for indexing.

    Adds each LENS file result as a batch item, enabling downstream consumers
    to process results in bounded batches (GAP-66-006).

    Args:
        lens_results: List of per-file dicts from LENS analysis.
        batch_processor: A :class:`~cortex.toolkit.batch.batch_processor.BatchProcessor`
                         instance to receive items.

    Returns:
        Number of items added to the batch.
    """
    count = 0
    for result in lens_results:
        batch_processor.add(result)
        count += 1
    return count


# ──────────────────────────────────────────────────────────────────────────────
# GAP-66-009: T1 Learned → DomainAdapter enrichment hint
# ──────────────────────────────────────────────────────────────────────────────


def t1_enrich_domain_adapter_context(
    t1_patterns: List[str],
    domain_adapter_context: Dict[str, Any],
) -> Dict[str, Any]:
    """Inject T1 persistent learned patterns into DomainAdapter context.

    Merges T1 learned domain patterns (file naming, module organisation, etc.)
    into the ``domain_adapter_context`` dict so that
    :class:`~cortex.toolkit.adapters.domain_adapter.DomainAdapter` resolution
    benefits from historical knowledge (GAP-66-009).

    Args:
        t1_patterns: List of pattern strings from BrainTier T1 persistent
                     learning store.
        domain_adapter_context: Existing context dict passed to DomainAdapter.

    Returns:
        Updated context dict with ``t1_patterns`` merged in.
    """
    enriched = dict(domain_adapter_context)
    enriched["t1_patterns"] = t1_patterns
    enriched["t1_enriched"] = True
    return enriched


# ──────────────────────────────────────────────────────────────────────────────
# GAP-66-010: T2 adaptive context → BatchProcessor injection
# ──────────────────────────────────────────────────────────────────────────────


def t2_inject_session_context(
    t2_context: Dict[str, Any],
    batch_metadata: Dict[str, Any],
) -> Dict[str, Any]:
    """Inject T2 adaptive session context into BatchProcessor metadata.

    Enriches DocGen pipeline batch metadata with T2 session signals
    (current intent, active phase, priority scoring weights) for improved
    content quality ranking (GAP-66-010).

    Args:
        t2_context: Session context from BrainTier T2.
        batch_metadata: Existing BatchProcessor metadata dict.

    Returns:
        Updated metadata dict with T2 context merged in.
    """
    enriched = dict(batch_metadata)
    enriched["t2_context"] = t2_context
    enriched["t2_enriched"] = True
    return enriched


# ──────────────────────────────────────────────────────────────────────────────
# GAP-66-011: T2 adaptive context → AuditFixPipeline Stage 2 priority scoring
# ──────────────────────────────────────────────────────────────────────────────


def t2_score_audit_findings(
    findings: List[Dict[str, Any]],
    t2_context: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Re-score audit findings using T2 adaptive session context.

    Boosts findings that overlap with active T2 session intent/phase,
    enabling Stage 2 of AuditFixPipeline to prioritise contextually relevant
    violations (GAP-66-011).

    Args:
        findings: List of audit finding dicts (from Stage 2 19-point scan).
        t2_context: T2 adaptive context including active intent and phase.

    Returns:
        Findings list with ``t2_priority_boost`` added to matching entries.
    """
    active_phase = t2_context.get("active_phase", "")
    active_intent = t2_context.get("intent", "").lower()
    scored = []
    for finding in findings:
        f = dict(finding)
        desc = str(f.get("description", "")).lower()
        phase = str(f.get("phase", ""))
        if active_phase and phase == active_phase:
            f["t2_priority_boost"] = True
        elif active_intent and active_intent in desc:
            f["t2_priority_boost"] = True
        else:
            f["t2_priority_boost"] = False
        scored.append(f)
    return scored


# ──────────────────────────────────────────────────────────────────────────────
# GAP-66-012: ResponseTemplate headers on BatchProcessor stage completions
# ──────────────────────────────────────────────────────────────────────────────


def apply_response_template_to_stage(
    stage_name: str,
    stage_result: Any,
    success: bool = True,
) -> str:
    """Wrap a pipeline stage completion in a ResponseTemplate header.

    Applies :meth:`~cortex.orchestrators.intelligence.response_template_generator.ResponseTemplate.create_header`
    to produce AC-marker-consistent section headers for BatchProcessor stage
    output (GAP-66-012).

    Args:
        stage_name: Display name for the stage (e.g., ``"DocGen Stage 1 Discovery"``).
        stage_result: Stage output data to include in the formatted response.
        success: Whether the stage succeeded.

    Returns:
        Formatted markdown string with stage header and result summary.
    """
    from cortex.orchestrators.intelligence.response_template_generator import ResponseTemplate

    title = f"{stage_name} {'Complete' if success else 'Failed'}"
    return ResponseTemplate.format_response(data=stage_result, title=title)


# ──────────────────────────────────────────────────────────────────────────────
# GAP-66-015/016: RetrievalOptimizer scoring → DocGen stage_2 / AuditFix
# ──────────────────────────────────────────────────────────────────────────────


def retrieval_optimizer_score_results(
    results: List[Dict[str, Any]],
    query: str,
) -> List[Dict[str, Any]]:
    """Rank results by RetrievalOptimizer relevance score.

    Adds a ``retrieval_score`` key to each result dict based on keyword
    overlap with ``query``.  Used by DocGenPlaybook stage_2 (GAP-66-015)
    and AuditFixPipeline (GAP-66-016) to surface the most relevant findings.

    Args:
        results: List of result dicts, each having at least a ``content`` or
                 ``description`` key.
        query: Query string to score against.

    Returns:
        Results list sorted descending by ``retrieval_score``.
    """
    query_words = set(query.lower().split())
    scored: List[Dict[str, Any]] = []
    for result in results:
        content = str(result.get("content", result.get("description", ""))).lower()
        content_words = set(content.split())
        overlap = len(query_words & content_words)
        total = max(len(query_words), 1)
        score = round(overlap / total, 4)
        r = dict(result)
        r["retrieval_score"] = score
        scored.append(r)
    return sorted(scored, key=lambda x: x["retrieval_score"], reverse=True)


# ──────────────────────────────────────────────────────────────────────────────
# GAP-66-018: LENS domain context → DomainAdapter resolution hints
# ──────────────────────────────────────────────────────────────────────────────


def lens_enrich_domain_adapter(
    lens_context: Dict[str, Any],
    adapter_context: Dict[str, Any],
) -> Dict[str, Any]:
    """Inject LENS domain context into a DomainAdapter context dict.

    Merges the ``lens_context`` (language, domain, file_type, etc.) produced
    by the LENS pipeline into the ``adapter_context`` used by T1 DomainAdapter
    to generate resolution hints.  Sets ``lens_enriched = True`` as a sentinel.

    Args:
        lens_context: Context dict from the LENS analysis pass (arbitrary keys).
        adapter_context: Existing DomainAdapter context to enrich.

    Returns:
        Enriched copy of ``adapter_context`` with ``lens_context`` and
        ``lens_enriched`` keys added.

    Authority: GAP-66-018 (Phase 66-C)
    """
    result = dict(adapter_context)
    result["lens_context"] = lens_context
    result["lens_enriched"] = True
    return result


# ──────────────────────────────────────────────────────────────────────────────
# GAP-66-019: T3 strategic mode → HierarchicalScanner full-depth scan
# ──────────────────────────────────────────────────────────────────────────────


def t3_strategic_deep_scan(
    scanner: Any,
    analysis_target: str = "architecture",
) -> Dict[str, Any]:
    """Run a T3 strategic full-depth scan using HierarchicalScanner.

    Invokes ``scanner.scan()`` (no arguments — uses scanner's own root
    configuration) and collects the resulting file list for T3 strategic
    reasoning.  Returns a summary dict consumed by the IntelligenceOrchestrator
    when operating in T3 scratch mode.

    Args:
        scanner: A ``HierarchicalScanner`` instance (or compatible duck type).
        analysis_target: Label identifying what is being analysed
                         (e.g. ``"architecture"``, ``"governance"``).

    Returns:
        Dict with keys:
        - ``files_scanned`` (int): number of files returned by the scanner.
        - ``analysis_target`` (str): echoed from the argument.
        - ``files`` (list): raw list of scanned file objects.

    Authority: GAP-66-019 (Phase 66-C)
    """
    files = scanner.scan()
    return {
        "files_scanned": len(files),
        "analysis_target": analysis_target,
        "files": files,
    }


# AC_COMPLETE: AC-66-B-WIRING-BRIDGES-20260224T000000Z ✅
# AC_COMPLETE: AC-66-C-GAP-018-019-BRIDGES-20260224T000000Z ✅
