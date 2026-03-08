"""KnowledgeAcquisitionOrchestrator — 6-step knowledge acquisition pipeline.

Coordinates the KAL (Knowledge Acquisition Layer) pipeline:
  Step 1: assess  — score domain signal coverage via KnowledgeCoverageAssessor
  Step 2: identify — collect missing domains from CoverageResult
  Step 3: synthesize — generate YAML per missing domain via KnowledgeTemplateSynthesizer
  Step 4: validate — schema-check each synthesized YAML via KnowledgeSchemaValidator
  Step 5: register — persist valid YAMLs into cortex-registry/knowledge/INDEX.yaml
  Step 6: re-verify — re-assess coverage; loop up to max_cycles if still below threshold

OPJMixin integration: consults the Operational Pattern Journal before acquisition
and emits URS MILD_REWARD / MILD_PUNISHMENT signals on completion.

Phase: 135-c (GAP-135-04)
CORE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
      CORE-035 (single canonical implementation), CORE-068 (convergence gate)
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ── Lazy imports (all optional — graceful degradation) ────────────────────────
try:
    from cortex.intelligence.learning.opj_mixin import OPJMixin as _OPJBase
except ImportError:
    class _OPJBase:  # type: ignore[no-redef]
        """Null OPJMixin when learning module is unavailable."""
        def _opj_consult(self, *args: Any, **kwargs: Any) -> None: ...
        def _opj_record_success(self, *args: Any, **kwargs: Any) -> None: ...
        def _opj_record_failure(self, *args: Any, **kwargs: Any) -> None: ...
        def _urs_emit_signal(self, *args: Any, **kwargs: Any) -> None: ...

_DEFAULT_THRESHOLD: float = 0.80
_MAX_CYCLES: int = 2


@dataclass
class AcquisitionResult:
    """Result of a KnowledgeAcquisitionOrchestrator.acquire() run.

    Attributes:
        skipped: True when coverage was already at/above threshold.
        acquired_domains: Domain names for which new knowledge was synthesized and registered.
        errors: Non-fatal error strings accumulated during the pipeline.
        cycles: Number of detect→synthesize→re-verify iterations performed.
    """

    skipped: bool = False
    acquired_domains: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    cycles: int = 0


class KnowledgeAcquisitionOrchestrator(_OPJBase):
    """6-step on-demand knowledge acquisition pipeline.

    Triggered when ``IntelligenceFacade.acquire()`` is called, either from
    Stage 1 comprehension (``InteractionOrchestrator._run_kal_coverage_check()``)
    or directly by callers with a pre-computed coverage score.

    Args:
        threshold: Coverage threshold below which acquisition runs (default 0.80).
        index_path: Override for INDEX.yaml path (tests use ``tmp_path``).

    Usage::

        orch = KnowledgeAcquisitionOrchestrator()
        result = orch.acquire(signals=["unknown-domain"], coverage_score=0.0)
        if not result.skipped:
            print(f"Acquired: {result.acquired_domains}")
    """

    def __init__(
        self,
        threshold: float = _DEFAULT_THRESHOLD,
        index_path: Optional[Path] = None,
    ) -> None:
        """Initialise with optional threshold and index path overrides."""
        self.threshold = threshold
        self._index_path = index_path

    def acquire(
        self,
        signals: List[str],
        coverage_score: float,
        intent: str = "IMPLEMENT",
    ) -> AcquisitionResult:
        """Run the 6-step KAL pipeline if coverage is below threshold.

        Args:
            signals: Domain signal strings from ``DomainSignalExtractor.extract()``.
            coverage_score: Pre-computed coverage score (0.0–1.0).
            intent: Intent context forwarded to KnowledgeTemplateSynthesizer.

        Returns:
            :class:`AcquisitionResult` with acquisition summary.
        """
        if coverage_score >= self.threshold:
            logger.debug(
                "KnowledgeAcquisitionOrchestrator: coverage %.2f >= %.2f — skipping",
                coverage_score,
                self.threshold,
            )
            return AcquisitionResult(skipped=True)

        # OPJ consult before pipeline
        try:
            self._opj_consult(pattern_id="knowledge_acquisition", context={"signals": signals})
        except Exception as exc:
            logger.debug("KAL: OPJ consult non-fatal — %s", exc)

        result = self._run_pipeline(signals=signals, intent=intent)

        # URS signal
        try:
            if result.errors:
                self._urs_emit_signal(
                    signal_type="MILD_PUNISHMENT",
                    pattern_id="knowledge_acquisition",
                    source_orchestrator="KnowledgeAcquisitionOrchestrator",
                )
            else:
                self._urs_emit_signal(
                    signal_type="MILD_REWARD",
                    pattern_id="knowledge_acquisition",
                    source_orchestrator="KnowledgeAcquisitionOrchestrator",
                )
        except Exception as exc:
            logger.debug("KAL: URS emit non-fatal — %s", exc)

        return result

    def _run_pipeline(self, signals: List[str], intent: str) -> AcquisitionResult:
        """Execute the 6-step KAL pipeline with convergence loop (CORE-068).

        Args:
            signals: Domain signals to acquire knowledge for.
            intent: Intent context for synthesizer.

        Returns:
            :class:`AcquisitionResult` populated by pipeline execution.
        """
        from cortex.intelligence.knowledge.knowledge_coverage_assessor import KnowledgeCoverageAssessor
        from cortex.intelligence.knowledge.knowledge_template_synthesizer import KnowledgeTemplateSynthesizer
        from cortex.intelligence.knowledge.knowledge_schema_validator import KnowledgeSchemaValidator
        from cortex.intelligence.knowledge.knowledge_index_registrar import KnowledgeIndexRegistrar

        assessor_kwargs: Dict[str, Any] = {"threshold": self.threshold}
        registrar_kwargs: Dict[str, Any] = {}
        if self._index_path:
            assessor_kwargs["index_path"] = self._index_path
            registrar_kwargs["index_path"] = self._index_path

        assessor = KnowledgeCoverageAssessor(**assessor_kwargs)
        synthesizer = KnowledgeTemplateSynthesizer()
        validator = KnowledgeSchemaValidator()
        registrar = KnowledgeIndexRegistrar(**registrar_kwargs)

        acquired: List[str] = []
        errors: List[str] = []
        cycles = 0
        remaining_signals = list(signals)

        for cycle in range(_MAX_CYCLES):
            cycles += 1

            # Step 1: assess current coverage
            assessment = assessor.assess(remaining_signals)
            if not assessment.acquisition_needed:
                logger.debug("KAL cycle %d: coverage %.2f >= threshold — stopping", cycle, assessment.score)
                break

            # Step 2: identify missing domains
            missing = assessment.missing_domains
            if not missing:
                break

            for domain in missing:
                # Step 3: synthesize
                try:
                    yaml_content = synthesizer.synthesize(domain=domain, intent=intent)
                except Exception as exc:
                    msg = f"synthesize({domain}): {exc}"
                    errors.append(msg)
                    logger.warning("KAL: %s", msg)
                    continue

                # Step 4: validate
                validation = validator.validate(yaml_content)
                if not validation.is_valid:
                    msg = f"validate({domain}): {'; '.join(validation.errors)}"
                    errors.append(msg)
                    logger.warning("KAL: %s", msg)
                    continue

                # Step 5: register
                try:
                    knowledge_path = f"{domain}/synthesized-{domain}.yaml"
                    registrar.register(
                        domain=domain,
                        path=knowledge_path,
                        title=f"{domain.replace('-', ' ').title()} (synthesized)",
                        keywords=[domain],
                    )
                    acquired.append(domain)
                    logger.debug("KAL: registered %r", domain)
                except Exception as exc:
                    msg = f"register({domain}): {exc}"
                    errors.append(msg)
                    logger.warning("KAL: %s", msg)

            # Step 6: re-verify — remove newly covered domains from remaining
            remaining_signals = [s for s in remaining_signals if s not in acquired]

        return AcquisitionResult(
            skipped=False,
            acquired_domains=acquired,
            errors=errors,
            cycles=cycles,
        )
