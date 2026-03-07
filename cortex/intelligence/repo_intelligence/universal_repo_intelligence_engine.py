"""UniversalRepoIntelligenceEngine — orchestrates the 8-extractor pipeline.

Runs all registered extractors against a repository root and assembles
the results into an :class:`OnboardingManifest`.

Phase: 132 (GAP-132-01)
Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
CORE: CORE-011 (type hints), CORE-012 (docstrings), CORE-035 (single canonical)
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from cortex.intelligence.repo_intelligence.base_extractor import BaseExtractor
from cortex.intelligence.repo_intelligence.onboarding_manifest import OnboardingManifest
from cortex.intelligence.repo_intelligence.solution_topology_extractor import SolutionTopologyExtractor
from cortex.intelligence.repo_intelligence.castle_windsor_extractor import CastleWindsorExtractor
from cortex.intelligence.repo_intelligence.nhibernate_extractor import NHibernateExtractor
from cortex.intelligence.repo_intelligence.nservicebus_extractor import NServiceBusExtractor
from cortex.intelligence.repo_intelligence.angular_extractor import AngularExtractor
from cortex.intelligence.repo_intelligence.aspnet_route_extractor import AspNetRouteExtractor
from cortex.intelligence.repo_intelligence.bounded_context_extractor import BoundedContextExtractor
from cortex.intelligence.repo_intelligence.tfm_classifier_extractor import TfmClassifierExtractor


class UniversalRepoIntelligenceEngine:
    """Orchestrate all 8 extractors and produce an :class:`OnboardingManifest`.

    Usage::

        engine = UniversalRepoIntelligenceEngine()
        manifest = engine.analyze(Path("/path/to/repo"))
        print(manifest.to_json())
    """

    def __init__(self, extractors: List[BaseExtractor] | None = None) -> None:
        """Initialise with the default 8-extractor pipeline.

        Args:
            extractors: Optional override list of extractors.  Defaults to
                the canonical 8-extractor suite.
        """
        self._extractors: List[BaseExtractor] = extractors or [
            SolutionTopologyExtractor(),
            CastleWindsorExtractor(),
            NHibernateExtractor(),
            NServiceBusExtractor(),
            AngularExtractor(),
            AspNetRouteExtractor(),
            BoundedContextExtractor(),
            TfmClassifierExtractor(),
        ]

    def analyze(self, repo_path: Path) -> OnboardingManifest:
        """Run all extractors and return an :class:`OnboardingManifest`.

        Args:
            repo_path: Absolute path to the repository root.  Path need not
                exist — each extractor returns empty results gracefully.

        Returns:
            Populated :class:`OnboardingManifest`.
        """
        repo_path = Path(repo_path)
        extractor_results = {}

        for extractor in self._extractors:
            try:
                result = extractor.extract(repo_path)
            except Exception:  # noqa: BLE001
                result = {}
            extractor_results[extractor.name] = result

        summary = self._build_summary(extractor_results)
        return OnboardingManifest(
            repo_path=repo_path,
            extractor_results=extractor_results,
            summary=summary,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_summary(results: dict) -> str:
        """Build a concise text summary from extractor results.

        Args:
            results: Extractor name → result dict mapping.

        Returns:
            Multi-line summary string.
        """
        lines = []
        topo = results.get("solution_topology", {})
        if topo.get("projects_found", 0):
            lines.append(f"Projects: {topo['projects_found']} (.sln)")
        tfm = results.get("tfm_classifier", {})
        if tfm.get("frameworks_found", 0):
            lines.append(f"TFMs: {', '.join(tfm.get('frameworks', []))}")
        angular = results.get("angular", {})
        if angular.get("modules_found", 0):
            lines.append(f"Angular modules: {angular['modules_found']}, components: {angular.get('components_found', 0)}")
        nsb = results.get("nservicebus", {})
        if nsb.get("handlers_found", 0):
            lines.append(f"NServiceBus handlers: {nsb['handlers_found']}, sagas: {nsb.get('sagas_found', 0)}")
        bc = results.get("bounded_contexts", {})
        if bc.get("contexts_found", 0):
            lines.append(f"Bounded contexts: {bc['contexts_found']}")
        return "\n".join(lines) if lines else "No significant artefacts detected."
