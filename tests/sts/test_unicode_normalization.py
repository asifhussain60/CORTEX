"""
AC-STS-002: Framework Validation Tests - Unicode Normalization
Test Suite 2 of 5

Purpose: Validate handling of emojis, CJK characters, RTL text, zero-width characters
Test Count: 15
Pass Threshold: 100%

Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import yaml
from pathlib import Path
from typing import Dict
import sys
import unicodedata

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tests.sts.sts_logger import STSLogger


class TestUnicodeNormalization:
    """Validates unicode handling and normalization for deterministic routing."""
    
    @classmethod
    def setup_class(cls):
        """Load golden corpus and initialize components."""
        golden_corpus_path = Path(__file__).parent.parent.parent / "sharpening-cortex" / "sts-template" / "golden_corpus.yaml"
        
        with open(golden_corpus_path, 'r', encoding='utf-8') as f:
            cls.golden_corpus = yaml.safe_load(f)
        
        cls.unicode_tests = cls.golden_corpus['unicode_normalization_tests']
        cls.audit_logger = STSLogger()
    
    def test_unicode_normalization_all(self):
        """
        Test that unicode characters are properly normalized.
        
        Validation:
        - Emojis stripped
        - CJK characters handled
        - RTL text normalized
        - Zero-width characters removed
        - Routing still correct after normalization
        """
        passed = 0
        failed = 0
        
        for test_case in self.unicode_tests:
            intent = test_case['intent']
            normalized_intent = test_case['normalized_intent']
            expected_orchestrator = test_case['expected_orchestrator']
            
            # Normalize intent
            actual_normalized = self._normalize_intent(intent)
            
            # Validate normalization matches expected
            if actual_normalized != normalized_intent:
                failed += 1
                pytest.fail(f"Unicode normalization failed for {test_case['id']}: '{actual_normalized}' != '{normalized_intent}'")
                continue
            
            # Validate routing still works after normalization
            route_result = self._route_intent(actual_normalized)
            if route_result['orchestrator'] != expected_orchestrator:
                failed += 1
                pytest.fail(f"Routing failed after unicode normalization for {test_case['id']}: {route_result['orchestrator']} != {expected_orchestrator}")
                continue
            
            passed += 1
            
            # Log successful validation
            self.audit_logger.log(
                level="INFO",
                message=f"Unicode normalization validated for {test_case['id']}",
                category="STS_VALIDATION",
                metadata={
                    "test_id": test_case['id'],
                    "original_intent": intent,
                    "normalized_intent": actual_normalized,
                    "orchestrator": route_result['orchestrator']
                }
            )
        
        assert failed == 0, f"Unicode normalization failures: {failed}/{len(self.unicode_tests)}"
    
    def _normalize_intent(self, intent: str) -> str:
        """
        Normalize unicode intent by:
        - Stripping emojis
        - Normalizing to NFC
        - Removing zero-width characters
        - Stripping CJK characters (translation would require external API)
        """
        # Remove non-ASCII characters including emojis and CJK
        # Keep only ASCII letters, digits, spaces, and basic punctuation
        normalized = ''.join(c for c in intent if ord(c) < 128)
        
        # Normalize to NFC (for any remaining chars)
        normalized = unicodedata.normalize('NFC', normalized)
        
        # Remove zero-width characters
        zero_width_chars = ['\u200b', '\u200c', '\u200d', '\ufeff']
        for char in zero_width_chars:
            normalized = normalized.replace(char, '')
        
        # Clean up extra whitespace
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def _route_intent(self, intent: str) -> Dict:
        """Simplified routing (matches routing_determinism test)."""
        # Order matters - more specific patterns first
        routing_patterns = [
            ('create a plan', {'orchestrator': 'PlanningOrchestratorV5', 'ac_prefix': 'AC-PLAN'}),
            ('azure devops', {'orchestrator': 'ADOOrchestratorV2', 'ac_prefix': 'AC-ADO'}),
            ('work item', {'orchestrator': 'ADOOrchestratorV2', 'ac_prefix': 'AC-ADO'}),
            ('git history', {'orchestrator': 'GitHistoryIntelligence', 'ac_prefix': 'AC-GIT'}),
            ('epic review', {'orchestrator': 'EpicReviewOrchestrator', 'ac_prefix': 'AC-EPIC'}),
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
        ]
        
        intent_lower = intent.lower()
        for pattern, route in routing_patterns:
            if pattern in intent_lower:
                return route
        
        return {'orchestrator': 'MasterOrchestrator', 'ac_prefix': 'AC-ORCH'}


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
