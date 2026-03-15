"""AutoPlanGenerator — CAPE sub-phase 136-b.

Coordinates RoadmapPatternSelector → PhaseFileScaffolder → write to
``cortex-registry/planning/phases/planned/`` (or a configurable directory
for testing).

Author: CORTEX Framework
Compliance: CORE-008, CORE-011, CORE-012, CORE-035, CORE-064
AC-ID: AC-136-CAPE-002c
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.orchestrators.domain.roadmap_pattern_selector import TriageResult
from cortex.orchestrators.domain.phase_file_scaffolder import PhaseFileScaffolder
from cortex.orchestrators.domain.roadmap_pattern_selector import RoadmapPatternSelector

# Default output directory (THIN INDEX CONTRACT — always planned/)
_DEFAULT_OUTPUT_DIR = str(
    Path(__file__).parents[3]
    / "cortex-registry"
    / "planning"
    / "phases"
    / "planned"
)

_SLUG_RE = re.compile(r"[^a-z0-9]+")


@dataclass
class PlanGenerationResult:
    """Result of :meth:`AutoPlanGenerator.generate_phase_plan`.

    Attributes:
        phase_id:      Generated phase identifier slug.
        file_path:     Absolute path of the written YAML file.
        template_name: Roadmap template that was selected.
    """

    phase_id: str
    file_path: str
    template_name: str


class AutoPlanGenerator:
    """Generate and persist a CORTEX phase YAML from a request + triage.

    Composes :class:`~cortex.orchestrators.domain.roadmap_pattern_selector.RoadmapPatternSelector`
    and :class:`~cortex.orchestrators.domain.phase_file_scaffolder.PhaseFileScaffolder`
    to produce a ready-to-use phase YAML file.

    Args:
        output_dir: Directory where the phase YAML will be written.
                    Defaults to ``cortex-registry/planning/phases/planned/``.

    Usage::

        generator = AutoPlanGenerator()
        result = generator.generate_phase_plan(
            title="My Feature",
            triage=triage_result,
            gaps=[{"id": "GAP-001", "title": "First gap"}],
            intent="IMPLEMENT",
        )
        # result.file_path — absolute path to the written YAML
    """

    def __init__(self, output_dir: Optional[str] = None) -> None:
        self._output_dir = output_dir or _DEFAULT_OUTPUT_DIR
        self._selector = RoadmapPatternSelector()
        self._scaffolder = PhaseFileScaffolder()

    def generate_phase_plan(
        self,
        *,
        title: str,
        triage: TriageResult,
        gaps: List[Dict[str, Any]],
        intent: str,
    ) -> PlanGenerationResult:
        """Generate and write a phase YAML file.

        Args:
            title:  Human-readable phase title (used to derive the phase ID slug).
            triage: :class:`TriageResult` from
                    :class:`~cortex.orchestrators.core.complexity_triage_engine.ComplexityTriageEngine`.
            gaps:   List of gap dicts with ``id`` and ``title`` keys.
            intent: Upper-case intent string (e.g. ``"IMPLEMENT"``, ``"REFACTOR"``).

        Returns:
            :class:`PlanGenerationResult` with ``phase_id``, ``file_path``,
            and ``template_name``.
        """
        selection = self._selector.select(triage=triage, intent=intent)
        phase_id = self._slugify(title)
        yaml_content = self._scaffolder.scaffold(
            phase_id=phase_id,
            title=title,
            triage=triage,
            gaps=gaps,
        )

        Path(self._output_dir).mkdir(parents=True, exist_ok=True)
        file_path = str(Path(self._output_dir) / f"{phase_id}.yaml")
        with open(file_path, "w", encoding="utf-8") as fh:
            fh.write(yaml_content)

        return PlanGenerationResult(
            phase_id=phase_id,
            file_path=file_path,
            template_name=selection.template_name,
        )

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    @staticmethod
    def _slugify(title: str) -> str:
        """Convert a human title to a lowercase, dash-separated slug.

        Args:
            title: Raw title string.

        Returns:
            URL-safe slug (letters, digits, dashes only).
        """
        lower = title.lower()
        slug = _SLUG_RE.sub("-", lower).strip("-")
        return slug
