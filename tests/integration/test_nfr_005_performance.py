"""
NFR-005: Performance Benchmarks
Validates that CORTEX core operations meet performance thresholds.

ACs:
- NFR-005-01: MasterOrchestrator initialization < 50ms
- NFR-005-02: Governance registry rule lookup < 10ms
- NFR-005-03: Orchestrator registry scan < 500ms

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import time
import pytest
from src.orchestrators.core.master_orchestrator import MasterOrchestrator
from src.orchestrators.core.orchestrator_registry import OrchestratorRegistry
from src.core.governance_registry import GovernanceRegistry
from src.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


class TestPerformanceBenchmarks:
    """Performance benchmarks for CORTEX core operations."""

    def test_orchestrator_initialization_under_50ms(self):
        """AC-NFR-005-01: MasterOrchestrator initializes in < 50ms"""
        orchestrator = MasterOrchestrator.instance()
        
        start = time.perf_counter()
        result = orchestrator.initialize()
        end = time.perf_counter()
        
        elapsed_ms = (end - start) * 1000
        assert elapsed_ms < 50, f"Orchestrator init took {elapsed_ms:.2f}ms, expected < 50ms"
        assert result.is_ok()

    def test_governance_rule_lookup_under_10ms(self):
        """AC-NFR-005-02: Governance rule lookup < 10ms"""
        registry = GovernanceRegistry.instance()
        rules = registry.get_all_rules()
        
        # Find a rule to lookup
        rule_id = None
        if isinstance(rules, dict):
            for tier_rules in rules.values():
                if isinstance(tier_rules, dict):
                    for rule_list in tier_rules.values():
                        if rule_list and len(rule_list) > 0:
                            rule_id = rule_list[0].rule_id
                            break
        
        if rule_id:
            start = time.perf_counter()
            result = registry.get_rule(rule_id)
            end = time.perf_counter()
            
            elapsed_ms = (end - start) * 1000
            assert elapsed_ms < 10, f"Rule lookup took {elapsed_ms:.2f}ms, expected < 10ms"
            assert result.is_ok()

    def test_orchestrator_registry_scan_under_500ms(self):
        """AC-NFR-005-03: Orchestrator registry scan < 500ms"""
        registry = OrchestratorRegistry.instance()
        
        start = time.perf_counter()
        # Scan registry - get_all will enumerate registered orchestrators
        orchestrators = registry.get_all()
        end = time.perf_counter()
        
        elapsed_ms = (end - start) * 1000
        assert elapsed_ms < 500, f"Registry scan took {elapsed_ms:.2f}ms, expected < 500ms"
        assert orchestrators is not None
        assert isinstance(orchestrators, list)

    def test_orchestrator_registry_domains_fast(self):
        """Bonus: Verify getting all domains from registry is fast"""
        registry = OrchestratorRegistry.instance()
        
        start = time.perf_counter()
        domains = registry.get_domains()
        end = time.perf_counter()
        
        elapsed_ms = (end - start) * 1000
        assert elapsed_ms < 10, f"Domains retrieval took {elapsed_ms:.2f}ms, expected < 10ms"
        assert domains is not None
        assert isinstance(domains, list)

    def test_governance_rule_retrieval_all_rules_fast(self):
        """Bonus: Verify retrieving all rules is fast"""
        registry = GovernanceRegistry.instance()
        
        start = time.perf_counter()
        rules = registry.get_all_rules()
        end = time.perf_counter()
        
        elapsed_ms = (end - start) * 1000
        assert elapsed_ms < 50, f"All rules retrieval took {elapsed_ms:.2f}ms, expected < 50ms"
        assert rules is not None
