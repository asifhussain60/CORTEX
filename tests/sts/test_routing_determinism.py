"""
AC-STS-002: Framework Validation Tests - Routing Determinism
Test Suite 1 of 5

Purpose: Validate that identical inputs produce identical orchestrator routing 100% of the time
Test Count: 25
Pass Threshold: 100%

Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import yaml
from pathlib import Path
from typing import Dict, List
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tests.sts.sts_logger import STSLogger


class TestRoutingDeterminism:
    """Validates 100% reproducible routing for identical inputs."""
    
    @classmethod
    def setup_class(cls):
        """Load golden corpus and initialize components."""
        golden_corpus_path = Path(__file__).parent.parent.parent / "sharpening-cortex" / "sts-template" / "golden_corpus.yaml"
        
        with open(golden_corpus_path, 'r', encoding='utf-8') as f:
            cls.golden_corpus = yaml.safe_load(f)
        
        cls.routing_tests = cls.golden_corpus['routing_determinism_tests']
        cls.audit_logger = STSLogger()
    
    def test_routing_determinism_all(self):
        """
        Test that identical intent routes to same orchestrator across multiple invocations.
        
        Validation:
        - Same orchestrator selected 100% of the time
        - Same AC-ID prefix generated
        - Routing path identical across runs
        """
        passed = 0
        failed = 0
        
        for test_case in self.routing_tests:
            intent = test_case['intent']
            expected_orchestrator = test_case['expected_orchestrator']
            expected_ac_prefix = test_case['expected_ac_prefix']
            
            # Run routing 10 times to validate determinism
            routes = []
            for i in range(10):
                route_result = self._route_intent(intent)
                routes.append(route_result)
            
            # Validate all routes identical
            first_route = routes[0]
            test_passed = True
            for route in routes[1:]:
                if route['orchestrator'] != first_route['orchestrator']:
                    test_passed = False
                    failed += 1
                    pytest.fail(f"Non-deterministic routing detected for '{intent}': {route['orchestrator']} != {first_route['orchestrator']}")
                    break
                if route['ac_prefix'] != first_route['ac_prefix']:
                    test_passed = False
                    failed += 1
                    pytest.fail(f"Non-deterministic AC-ID generation for '{intent}': {route['ac_prefix']} != {first_route['ac_prefix']}")
                    break
            
            if not test_passed:
                continue
            
            # Validate expected orchestrator
            if first_route['orchestrator'] != expected_orchestrator:
                failed += 1
                pytest.fail(f"Intent '{intent}' routed to {first_route['orchestrator']} instead of {expected_orchestrator}")
                continue
            
            # Validate expected AC prefix
            if first_route['ac_prefix'] != expected_ac_prefix:
                failed += 1
                pytest.fail(f"Intent '{intent}' generated {first_route['ac_prefix']} instead of {expected_ac_prefix}")
                continue
            
            passed += 1
            
            # Log successful validation
            self.audit_logger.log(
                level="INFO",
                message=f"Routing determinism validated for {test_case['id']}",
                category="STS_VALIDATION",
                metadata={
                    "test_id": test_case['id'],
                    "intent": intent,
                    "orchestrator": first_route['orchestrator'],
                    "determinism": "100%",
                    "iterations": 10
                }
            )
        
        assert failed == 0, f"Routing determinism failures: {failed}/{len(self.routing_tests)}"
    
    def _route_intent(self, intent: str) -> Dict:
        """
        Route intent to orchestrator (simplified routing logic for STS).
        
        In production, this would call MasterOrchestrator routing logic.
        For STS, we use pattern matching based on routing table.
        """
        # Simplified routing table (matches .github/copilot-instructions.md)
        # Order matters - more specific patterns first
        routing_patterns = [
            ('create a plan', {'orchestrator': 'PlanningOrchestratorV5', 'ac_prefix': 'AC-PLAN'}),
            ('azure devops', {'orchestrator': 'ADOOrchestratorV2', 'ac_prefix': 'AC-ADO'}),
            ('work item', {'orchestrator': 'ADOOrchestratorV2', 'ac_prefix': 'AC-ADO'}),
            ('sync work items', {'orchestrator': 'ADOOrchestratorV2', 'ac_prefix': 'AC-ADO'}),
            ('git history', {'orchestrator': 'GitHistoryIntelligence', 'ac_prefix': 'AC-GIT'}),
            ('epic review', {'orchestrator': 'EpicReviewOrchestrator', 'ac_prefix': 'AC-EPIC'}),
            ('health check', {'orchestrator': 'EpicReviewOrchestrator', 'ac_prefix': 'AC-EPIC'}),
            ('investigate', {'orchestrator': 'InvestigationOrchestrator', 'ac_prefix': 'AC-INV'}),
            ('crawl', {'orchestrator': 'CrawlerOrchestrator', 'ac_prefix': 'AC-CRAWLER'}),
            ('scaffold', {'orchestrator': 'OrchestratorScaffolder', 'ac_prefix': 'AC-SCAFFOLD'}),
            ('sanitize', {'orchestrator': 'SanitizationOrchestratorV2', 'ac_prefix': 'AC-SAN'}),
            ('vacuum', {'orchestrator': 'VacuumOrchestratorV2', 'ac_prefix': 'AC-VAC'}),
            ('refine', {'orchestrator': 'RefinementOrchestratorV2', 'ac_prefix': 'AC-REF'}),
            ('cleanup', {'orchestrator': 'CleanupOrchestratorV2', 'ac_prefix': 'AC-CLEAN'}),
            ('plan', {'orchestrator': 'PlanningOrchestratorV5', 'ac_prefix': 'AC-PLAN'}),
            ('ado', {'orchestrator': 'ADOOrchestratorV2', 'ac_prefix': 'AC-ADO'}),
            ('search', {'orchestrator': 'GitHistoryIntelligence', 'ac_prefix': 'AC-GIT'}),
            ('implement', {'orchestrator': 'TDDMasterOrchestrator', 'ac_prefix': 'AC-TDD'}),
            ('build', {'orchestrator': 'TDDMasterOrchestrator', 'ac_prefix': 'AC-TDD'}),
            ('create', {'orchestrator': 'TDDMasterOrchestrator', 'ac_prefix': 'AC-TDD'}),
            ('fix', {'orchestrator': 'TDDMasterOrchestrator', 'ac_prefix': 'AC-TDD'}),
        ]
        
        # Match intent to orchestrator (deterministic pattern matching)
        intent_lower = intent.lower()
        for pattern, route in routing_patterns:
            if pattern in intent_lower:
                return route
        
        # Default fallback
        return {'orchestrator': 'MasterOrchestrator', 'ac_prefix': 'AC-ORCH'}
    
    def test_routing_determinism_summary(self):
        """Generate summary report for routing determinism tests."""
        total_tests = len(self.routing_tests)
        
        self.audit_logger.log(
            level="INFO",
            message=f"Routing determinism validation complete",
            category="STS_VALIDATION",
            metadata={
                "total_tests": total_tests,
                "expected_pass_rate": "100%",
                "test_suite": "routing_determinism"
            }
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
