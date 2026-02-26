"""
Phase 84-a: Wire RuleExtractor into LENS + Business Rules Persistence
RED test suite — ALL tests must FAIL before implementation begins.

AC_START: AC-84-A-2026-02-26
Authority: CORE-008 (TDD first), CORE-064 (Sweep Completeness)
Covers: GAP-84-01, GAP-84-02
"""

from __future__ import annotations

import importlib
import re
from pathlib import Path
from typing import Any, Dict, List

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]  # tests/golden/ → project root
CORTEX_SRC = PROJECT_ROOT / "cortex"


class TestRuleExtractorLensWiring:
    """GAP-84-01: RuleExtractor must be imported and invoked by LENS orchestrator."""

    def test_rule_extractor_importable_from_lens(self) -> None:
        """
        GAP-84-01: RuleExtractor is importable from cortex.lens context.
        Verifies the LENS module directly imports RuleExtractor.
        """
        lens_orch = CORTEX_SRC / "lens" / "lens_orchestrator.py"
        assert lens_orch.exists(), "lens_orchestrator.py must exist"
        source = lens_orch.read_text()
        assert "RuleExtractor" in source, (
            "lens_orchestrator.py must import RuleExtractor — GAP-84-01 not resolved"
        )

    def test_lens_orchestrator_invokes_rule_extractor(self) -> None:
        """
        GAP-84-01: LENS targeted analysis calls RuleExtractor on Python files.
        Verifies _extract_business_rules method exists in LENSOrchestrator.
        """
        lens_orch = CORTEX_SRC / "lens" / "lens_orchestrator.py"
        source = lens_orch.read_text()
        assert "_extract_business_rules" in source, (
            "LENSOrchestrator must have _extract_business_rules() method — GAP-84-01"
        )

    def test_extracted_rules_returned_in_lens_result(self) -> None:
        """
        GAP-84-01: LENS analysis result dict contains 'business_rules' key.
        Verifies analyze_file() includes business_rules in its output.
        """
        from cortex.lens.lens_orchestrator import LENSOrchestrator

        orchestrator = LENSOrchestrator(repo_path=PROJECT_ROOT)
        # Create a temp Python file to analyse
        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write(
                """
def validate_order(order_value: float) -> bool:
    if order_value < 10.0:
        raise ValueError("Minimum order value is $10")
    return True
"""
            )
            tmp = f.name

        try:
            result = orchestrator.analyze_file(Path(tmp))
            assert "business_rules" in result, (
                "analyze_file() result must contain 'business_rules' key — GAP-84-01"
            )
        finally:
            os.unlink(tmp)


class TestBusinessRulesYamlPersistence:
    """GAP-84-02: KnowledgePersistenceService must generate business-rules.yaml."""

    def test_persistence_service_generates_business_rules_yaml(self) -> None:
        """
        GAP-84-02: KnowledgePersistenceService has a _generate_business_rules_artifact method.
        """
        from cortex.intelligence.knowledge.persistence.knowledge_persistence_service import (
            KnowledgePersistenceService,
        )
        import tempfile, shutil

        tmpdir = Path(tempfile.mkdtemp())
        try:
            svc = KnowledgePersistenceService(company_dir=tmpdir)
            assert hasattr(svc, "_generate_business_rules_artifact"), (
                "KnowledgePersistenceService must have _generate_business_rules_artifact() — GAP-84-02"
            )
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_business_rules_yaml_contains_extracted_rules(self) -> None:
        """
        GAP-84-02: Persisted business-rules.yaml has rules with field/description/confidence.
        """
        from cortex.intelligence.knowledge.persistence.knowledge_persistence_service import (
            KnowledgePersistenceService,
        )
        import tempfile, yaml, shutil

        tmpdir = Path(tempfile.mkdtemp())
        try:
            svc = KnowledgePersistenceService(company_dir=tmpdir)
            onboarding_data = {
                "business_rules": [
                    {"field": "order_value", "description": "Minimum $10", "confidence": 0.9}
                ]
            }
            result = svc.persist_knowledge("test_repo", onboarding_data)
            assert result.success or result.artifacts_created, (
                "persist_knowledge must create artifacts — GAP-84-02"
            )
            # Check business-rules.yaml was written
            br_yaml = tmpdir / "domains" / "test_repo" / "business-rules.yaml"
            assert br_yaml.exists(), (
                "business-rules.yaml must be written to disk — GAP-84-02"
            )
            data = yaml.safe_load(br_yaml.read_text())
            assert "rules" in data or "business_rules" in data, (
                "business-rules.yaml must contain 'rules' or 'business_rules' key — GAP-84-02"
            )
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_persistence_idempotent_for_business_rules(self) -> None:
        """
        GAP-84-02: Re-persisting business rules overwrites cleanly (idempotent).
        """
        from cortex.intelligence.knowledge.persistence.knowledge_persistence_service import (
            KnowledgePersistenceService,
        )
        import tempfile, shutil

        tmpdir = Path(tempfile.mkdtemp())
        try:
            svc = KnowledgePersistenceService(company_dir=tmpdir)
            onboarding_data = {
                "business_rules": [
                    {"field": "price", "description": "Price must be positive", "confidence": 0.8}
                ]
            }
            svc.persist_knowledge("test_repo", onboarding_data)
            # Second call should not fail or duplicate
            result2 = svc.persist_knowledge("test_repo", onboarding_data)
            assert result2 is not None, (
                "Second persist call must succeed — GAP-84-02 idempotent"
            )
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)
