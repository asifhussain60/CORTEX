"""
Phase 84-b: YAML-Backed BusinessKnowledgeRepository + Enforcement Agent + INDEX Entry
RED test suite — ALL tests must FAIL before implementation begins.

AC_START: AC-84-B-2026-02-26
Authority: CORE-008 (TDD first), CORE-064 (Sweep Completeness)
Covers: GAP-84-03, GAP-84-04, GAP-84-05
"""

from __future__ import annotations

from pathlib import Path
import shutil
import tempfile

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CORTEX_SRC = PROJECT_ROOT / "cortex"
REGISTRY = PROJECT_ROOT / "cortex-registry"


class TestYAMLBackedBusinessKnowledgeRepository:
    """GAP-84-03: BusinessKnowledgeRepository must persist to YAML, not memory only."""

    def test_yaml_backed_repository_loads_from_file(self) -> None:
        """
        GAP-84-03: Repository reads business-rules.yaml from disk.
        """
        from cortex.intelligence.knowledge.business_knowledge_repository import (
            BusinessKnowledgeRepository,
        )
        import yaml

        tmpdir = Path(tempfile.mkdtemp())
        try:
            rules_file = tmpdir / "business-rules.yaml"
            rules_file.write_text(yaml.dump({
                "rules": [{"field": "price", "description": "Must be positive", "confidence": 0.9}]
            }))
            repo = BusinessKnowledgeRepository(rules_path=rules_file)
            rules = repo.get_rules()
            assert len(rules) > 0, (
                "BusinessKnowledgeRepository must load rules from YAML file — GAP-84-03"
            )
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_yaml_backed_repository_survives_restart(self) -> None:
        """
        GAP-84-03: Data persists across instances — constructor accepts rules_path.
        """
        from cortex.intelligence.knowledge.business_knowledge_repository import (
            BusinessKnowledgeRepository,
        )
        import yaml

        tmpdir = Path(tempfile.mkdtemp())
        try:
            rules_file = tmpdir / "business-rules.yaml"
            data = {"rules": [{"field": "email", "description": "Must contain @", "confidence": 0.95}]}
            rules_file.write_text(yaml.dump(data))

            repo1 = BusinessKnowledgeRepository(rules_path=rules_file)
            count1 = len(repo1.get_rules())

            repo2 = BusinessKnowledgeRepository(rules_path=rules_file)
            count2 = len(repo2.get_rules())

            assert count1 == count2, (
                "Rules must be consistent across instances — GAP-84-03 persistence"
            )
            assert count1 > 0, "Must load at least one rule — GAP-84-03"
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_yaml_backed_repository_query_by_domain(self) -> None:
        """
        GAP-84-03: Filter rules by domain (billing/auth/compliance).
        """
        from cortex.intelligence.knowledge.business_knowledge_repository import (
            BusinessKnowledgeRepository,
        )
        import yaml

        tmpdir = Path(tempfile.mkdtemp())
        try:
            rules_file = tmpdir / "business-rules.yaml"
            data = {
                "rules": [
                    {"field": "invoice_amount", "description": "Must be positive", "domain": "billing", "confidence": 0.9},
                    {"field": "token", "description": "Must not be expired", "domain": "auth", "confidence": 0.95},
                ]
            }
            rules_file.write_text(yaml.dump(data))
            repo = BusinessKnowledgeRepository(rules_path=rules_file)
            billing_rules = repo.query_by_domain("billing")
            assert len(billing_rules) >= 1, (
                "query_by_domain('billing') must return matching rules — GAP-84-03"
            )
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class TestBusinessRuleEnforcementAgent:
    """GAP-84-04: EnforcementOrchestrator must include BusinessRuleEnforcementAgent."""

    def test_enforcement_agent_loads_business_rules(self) -> None:
        """
        GAP-84-04: BusinessRuleEnforcementAgent exists and loads rules.
        """
        from cortex.governance.business_rule_enforcement_agent import (
            BusinessRuleEnforcementAgent,
        )

        agent = BusinessRuleEnforcementAgent()
        assert hasattr(agent, "load_rules"), (
            "BusinessRuleEnforcementAgent must have load_rules() — GAP-84-04"
        )

    def test_enforcement_agent_blocks_on_violation(self) -> None:
        """
        GAP-84-04: Agent blocks when a change violates an extracted business rule.
        """
        from cortex.governance.business_rule_enforcement_agent import (
            BusinessRuleEnforcementAgent,
        )
        import yaml
        import tempfile, shutil

        tmpdir = Path(tempfile.mkdtemp())
        try:
            rules_file = tmpdir / "business-rules.yaml"
            rules_file.write_text(yaml.dump({
                "rules": [{"field": "price", "description": "Must be positive (>0)", "confidence": 0.9, "domain": "billing"}]
            }))
            agent = BusinessRuleEnforcementAgent(rules_path=rules_file)
            result = agent.enforce_change("Set price to -5")
            assert result.get("allowed") is False or result.get("violations"), (
                "Agent must detect violation when change conflicts with rule — GAP-84-04"
            )
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_enforcement_agent_passes_clean_change(self) -> None:
        """
        GAP-84-04: Agent passes when no violation detected.
        """
        from cortex.governance.business_rule_enforcement_agent import (
            BusinessRuleEnforcementAgent,
        )
        import yaml
        import tempfile, shutil

        tmpdir = Path(tempfile.mkdtemp())
        try:
            rules_file = tmpdir / "business-rules.yaml"
            rules_file.write_text(yaml.dump({"rules": []}))
            agent = BusinessRuleEnforcementAgent(rules_path=rules_file)
            result = agent.enforce_change("Update UI color scheme")
            assert result.get("allowed") is True, (
                "Agent must allow change when no rules violated — GAP-84-04"
            )
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class TestIndexYamlBusinessRulesDomain:
    """GAP-84-05: INDEX.yaml must have business-rules domain entry."""

    def test_index_yaml_has_business_rules_domain(self) -> None:
        """
        GAP-84-05: cortex-registry/knowledge INDEX.yaml contains business-rules.
        """
        import yaml

        index_candidates = list(REGISTRY.glob("**/INDEX.yaml"))
        assert index_candidates, "INDEX.yaml must exist in cortex-registry/ — GAP-84-05"

        for index_file in index_candidates:
            data = yaml.safe_load(index_file.read_text())
            domains = data if isinstance(data, list) else data.get("domains", data)
            domain_names = []
            if isinstance(domains, list):
                for d in domains:
                    if isinstance(d, dict):
                        domain_names.append(d.get("name", "") or d.get("id", ""))
                    else:
                        domain_names.append(str(d))
            elif isinstance(domains, dict):
                domain_names = list(domains.keys())
            if any("business" in n.lower() or "rules" in n.lower() for n in domain_names):
                return  # Found

        pytest.fail("INDEX.yaml does not contain a business-rules domain entry — GAP-84-05")

    def test_knowledge_router_routes_business_rules(self) -> None:
        """
        GAP-84-05: IntelligentKnowledgeRouter recognizes billing/finance keywords.
        """
        from cortex.intelligence.knowledge.router import IntelligentKnowledgeRouter

        router = IntelligentKnowledgeRouter()
        domain = router.route_query("billing invoice payment validation")
        assert domain and ("business" in domain.lower() or "finance" in domain.lower() or "billing" in domain.lower()), (
            f"Router must route billing query to business/finance domain, got '{domain}' — GAP-84-05"
        )
