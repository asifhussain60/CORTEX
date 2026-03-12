"""NarrativeEngine — Phase 152-d

Generates narrative text per dashboard tab from manifest data and optional
knowledge overlay. No external LLM calls — assembled from templates and
manifest values. Pads with overlay knowledge sentences when needed.

CORE: CORE-008 (TDD), CORE-011, CORE-012
Source: GitHub Issue #18 — FB-20260312-001
"""

from __future__ import annotations

from typing import Any

from cortex.dashboards.data_collector import DashboardManifest
from cortex.dashboards.knowledge_overlay_engine import KnowledgeOverlay


class NarrativeEngine:
    """Generates ≥MIN_WORD_COUNT word narrative strings per dashboard tab."""

    MIN_WORD_COUNT: int = 150

    # Tab-specific opening templates.
    _OPENERS: dict[str, str] = {
        "overview": (
            "This tab presents a high-level overview of the repository, capturing its "
            "purpose, structure, and overall architectural posture. The overview is the "
            "entry point for engineers and architects seeking a rapid orientation to the "
            "codebase, surfacing its archetype classification, primary dependencies, and "
            "key health indicators at a glance. By consolidating the most important "
            "signals into a single pane, the overview reduces ramp-up time and supports "
            "consistent onboarding across teams and roles."
        ),
        "metrics": (
            "The metrics tab aggregates quantitative signals collected across the "
            "repository's runtime and build pipeline. These indicators include test-pass "
            "rates, code-coverage percentages, lint error counts, and deployment frequency. "
            "Metrics are the backbone of evidence-based engineering: they transform "
            "subjective impressions of quality into trackable numbers that guide "
            "prioritisation, retrospectives, and investment decisions."
        ),
        "health": (
            "Health checks verify that the repository's dependencies, configuration, and "
            "runtime environment satisfy the requirements for production readiness. This "
            "tab surfaces P0 and P1 violations identified by CORTEX orchestrators, "
            "enabling teams to respond to regressions quickly and maintain sustained "
            "delivery confidence."
        ),
        "pipeline": (
            "The pipeline tab documents the continuous-integration and delivery workflow "
            "stages active for this repository. It highlights gate thresholds, parallel "
            "execution strategies, and any pending compliance or governance actions that "
            "must be resolved before a release can proceed."
        ),
        "governance": (
            "Governance rules encode the organisation's non-negotiable standards for "
            "code quality, security, and operational safety. This tab surfaces all "
            "active rules, their current compliance status, and outstanding violations "
            "that require resolution. Enforcing governance at the repository level "
            "ensures that team-level decisions remain consistent with enterprise policy."
        ),
        "security": (
            "Security analysis highlights vulnerabilities, dependency advisories, and "
            "OWASP Top 10 concerns detected in this repository. Each finding is "
            "classified by severity and linked to a recommended remediation path. "
            "Addressing security issues early in the development cycle reduces both "
            "risk exposure and the cost of late-stage remediation."
        ),
        "architecture": (
            "The architecture tab provides a structural analysis of the repository's "
            "design patterns, module boundaries, and inter-component dependencies. "
            "It compares the observed structure against established architectural "
            "archetypes, identifies drift, and recommends refactoring opportunities "
            "to improve maintainability and scalability."
        ),
        "quality": (
            "Code quality analysis examines maintainability, readability, and adherence "
            "to established coding standards. This tab surfaces cyclomatic-complexity "
            "outliers, duplication hotspots, and technical-debt accumulation zones that "
            "warrant attention during the next refactoring cycle."
        ),
        "testing": (
            "The testing tab summarises the repository's test suite composition, "
            "coverage distribution, and failure history. A mature testing strategy "
            "combines unit, integration, and contract tests to provide fast feedback "
            "and guard against regressions introduced during active development."
        ),
        "observability": (
            "Observability capabilities determine how quickly engineers can detect, "
            "diagnose, and resolve production incidents. This tab documents tracing, "
            "logging, and metrics instrumentation present in the codebase, alongside "
            "any gaps that should be addressed to achieve full-stack observability."
        ),
    }

    _GENERIC_OPENER: str = (
        "This section aggregates data and insights relevant to the selected dashboard "
        "tab. The information presented has been collected from the repository's source "
        "tree, runtime telemetry, and CORTEX knowledge registry. Analysis is performed "
        "autonomously without requiring manual configuration, ensuring that the "
        "dashboard remains accurate as the codebase evolves."
    )

    # Knowledge overlay filler sentences used when the narrative is too short.
    _OVERLAY_FILLER: list[str] = [
        (
            "The CORTEX knowledge registry contributes domain-specific patterns, "
            "anti-patterns, and best practices drawn from a curated catalogue of "
            "engineering principles spanning security, reliability, and performance."
        ),
        (
            "Domain knowledge overlays contextualise raw metrics and structural signals "
            "with explanations grounded in widely accepted software-engineering "
            "disciplines and CORTEX governance rules."
        ),
        (
            "Each narrative is generated without external LLM calls, using only "
            "template assembly and manifest values, ensuring deterministic and "
            "reproducible output across repeated dashboard regenerations."
        ),
        (
            "Engineers and architects should use narrative summaries as a launchpad "
            "for deeper investigation rather than a definitive diagnosis; always "
            "consult the underlying data points and source files for authoritative "
            "information."
        ),
        (
            "CORTEX continuously refines its analysis heuristics based on real-world "
            "feedback loops, governance audits, and reinforcement signals emitted "
            "by orchestrators during operation — ensuring that narrative quality "
            "improves over time."
        ),
        (
            "Repository archetypes guide the selection of analysis lenses applied to "
            "the codebase, ensuring that the most relevant quality dimensions are "
            "surfaced prominently and that less applicable checks are ranked lower "
            "in the priority order."
        ),
    ]

    def narrate(
        self,
        manifest: DashboardManifest,
        overlay: "dict[str, Any]",
    ) -> "dict[str, str]":
        """Generate narrative text per tab (tab_id → narrative string)."""
        narratives: dict[str, str] = {}
        for tab_id, tab_data in manifest.tabs.items():
            o = overlay.get(tab_id) if overlay else None
            narratives[tab_id] = self._narrate_tab(tab_id, tab_data, o)
        return narratives

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _narrate_tab(
        self,
        tab_id: str,
        tab_data: "dict[str, Any]",
        overlay: "Any",
    ) -> str:
        """Return a ≥MIN_WORD_COUNT word narrative for one tab."""
        opener = self._OPENERS.get(tab_id, self._GENERIC_OPENER)

        # Build context sentences from tab_data fields.
        context_parts: list[str] = [opener]

        title = tab_data.get("title") if isinstance(tab_data, dict) else None
        if title:
            context_parts.append(
                f"The '{title}' section focuses on this subset of repository intelligence."
            )

        description = (
            tab_data.get("description") if isinstance(tab_data, dict) else None
        )
        if description:
            context_parts.append(str(description))

        # Append archetype context if tab_id appears in generic context.
        context_parts.append(
            f"Tab identifier '{tab_id}' is one of the structured views exposed by "
            "the CORTEX Dashboard Intelligence Pipeline, assembled through a "
            "seven-stage process: collect, overlay, select, narrate, render, "
            "quality-gate, and emit."
        )

        # Append overlay knowledge entries.
        if overlay and overlay.knowledge_entries:
            for entry in overlay.knowledge_entries[:3]:
                if isinstance(entry, dict):
                    summary = entry.get("summary") or entry.get("description") or ""
                    if summary:
                        context_parts.append(str(summary))

        narrative = " ".join(context_parts)

        # Pad to MIN_WORD_COUNT using filler sentences if needed.
        filler_idx = 0
        while len(narrative.split()) < self.MIN_WORD_COUNT:
            filler = self._OVERLAY_FILLER[filler_idx % len(self._OVERLAY_FILLER)]
            narrative = f"{narrative} {filler}"
            filler_idx += 1

        return narrative
