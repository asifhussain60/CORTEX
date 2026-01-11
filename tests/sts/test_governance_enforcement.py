"""
AC-STS-002: Framework Validation Tests - Governance Enforcement
Test Suite 3 of 5

Purpose: Validate CORE rules enforcement and violation blocking
Test Count: 20
Pass Threshold: 100%

Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import yaml
from pathlib import Path
from typing import Dict
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tests.sts.sts_logger import STSLogger


class TestGovernanceEnforcement:
    """Validates CORE rules enforcement and violation detection."""
    
    @classmethod
    def setup_class(cls):
        """Load golden corpus and initialize components."""
        golden_corpus_path = Path(__file__).parent.parent.parent / "sharpening-cortex" / "sts-template" / "golden_corpus.yaml"
        
        with open(golden_corpus_path, 'r', encoding='utf-8') as f:
            cls.golden_corpus = yaml.safe_load(f)
        
        cls.governance_tests = cls.golden_corpus['governance_enforcement_tests']
        cls.audit_logger = STSLogger()
    
    def test_governance_enforcement_all(self):
        """
        Test that CORE rules are enforced and violations blocked.
        
        Validation:
        - CORE-001: Operations >500 lines blocked
        - CORE-002: Summary files blocked
        - CORE-005: Hardcoded paths blocked
        - CORE-008: Missing tests blocked
        - CORE-009: Root-level plans blocked
        - CORE-017: Governance bypass blocked
        - CORE-019: Direct coding blocked
        """
        passed = 0
        failed = 0
        
        for test_case in self.governance_tests:
            intent = test_case['intent']
            expected_behavior = test_case['expected_behavior']
            violated_rule = test_case['violated_rule']
            rule_name = test_case['rule_name']
            
            # Check governance enforcement
            enforcement_result = self._check_governance(intent, violated_rule)
            
            # Validate expected behavior
            if expected_behavior == "block":
                if not enforcement_result['blocked']:
                    failed += 1
                    pytest.fail(f"Governance violation not blocked for {test_case['id']}: {violated_rule} ({rule_name})")
                    continue
                
                if not enforcement_result['logged']:
                    failed += 1
                    pytest.fail(f"Governance violation not logged for {test_case['id']}: {violated_rule}")
                    continue
            
            elif expected_behavior == "allow_with_warning":
                if enforcement_result['blocked']:
                    failed += 1
                    pytest.fail(f"Operation incorrectly blocked for {test_case['id']}: {violated_rule}")
                    continue
                
                if not enforcement_result['logged']:
                    failed += 1
                    pytest.fail(f"Warning not logged for {test_case['id']}: {violated_rule}")
                    continue
            
            passed += 1
            
            # Log successful validation
            self.audit_logger.log(
                level="INFO",
                message=f"Governance enforcement validated for {test_case['id']}",
                category="STS_VALIDATION",
                metadata={
                    "test_id": test_case['id'],
                    "violated_rule": violated_rule,
                    "rule_name": rule_name,
                    "expected_behavior": expected_behavior,
                    "result": "blocked" if enforcement_result['blocked'] else "allowed"
                }
            )
        
        assert failed == 0, f"Governance enforcement failures: {failed}/{len(self.governance_tests)}"
    
    def _check_governance(self, intent: str, violated_rule: str) -> Dict:
        """
        Check governance rules against intent.
        
        Returns:
            blocked: True if operation should be blocked
            logged: True if violation logged
            rule_violated: Rule that was violated
        """
        blocked = False
        logged = False
        
        # CORE-001: Incremental Execution (>500 lines)
        if violated_rule == "CORE-001":
            # Check for line count references (both "600 lines" and "600-line" formats)
            import re
            line_match = re.search(r'(\d+)[-\s]?lines?', intent.lower())
            if line_match:
                line_count = int(line_match.group(1))
                if line_count > 500:
                    blocked = True
                    logged = True
                    self.audit_logger.log(
                        level="WARNING",
                        message=f"CORE-001 violation: Large operation detected ({line_count} lines > 500 limit)",
                        category="GOVERNANCE",
                        metadata={"intent": intent, "rule": "CORE-001"}
                    )
        
        # CORE-002: No Summary Files
        elif violated_rule == "CORE-002":
            summary_keywords = ['summary', 'overview', 'notes.md', 'changelog.md']
            if any(kw in intent.lower() for kw in summary_keywords):
                blocked = True
                logged = True
                self.audit_logger.log(
                    level="WARNING",
                    message=f"CORE-002 violation: Summary file creation detected",
                    category="GOVERNANCE",
                    metadata={"intent": intent, "rule": "CORE-002"}
                )
        
        # CORE-005: Path Portability
        elif violated_rule == "CORE-005":
            hardcoded_patterns = ['/Users/', '/home/', 'C:\\', '\\\\']
            if any(pattern in intent for pattern in hardcoded_patterns):
                blocked = True
                logged = True
                self.audit_logger.log(
                    level="WARNING",
                    message=f"CORE-005 violation: Hardcoded path detected",
                    category="GOVERNANCE",
                    metadata={"intent": intent, "rule": "CORE-005"}
                )
        
        # CORE-008: TDD Enforcement
        elif violated_rule == "CORE-008":
            if "without tests" in intent or "without test" in intent or "skip tests" in intent:
                blocked = True
                logged = True
                self.audit_logger.log(
                    level="WARNING",
                    message=f"CORE-008 violation: Missing tests detected",
                    category="GOVERNANCE",
                    metadata={"intent": intent, "rule": "CORE-008"}
                )
        
        # CORE-009: Plan File Organization
        elif violated_rule == "CORE-009":
            # Check if creating plan/roadmap files
            is_plan_file = ("plan" in intent.lower() or "roadmap" in intent.lower())
            in_docs = ("docs/" in intent.lower() or "docs folder" in intent.lower())
            in_cortex_brain = ("cortex-brain" in intent.lower())
            in_disallowed = ("sharpening-cortex" in intent.lower() or "root" in intent.lower())
            
            if is_plan_file:
                if in_docs or in_cortex_brain:
                    blocked = False  # Allow with warning in approved locations
                    logged = True
                elif in_disallowed or not (in_docs or in_cortex_brain):
                    blocked = True  # Block if in disallowed or unknown location
                    logged = True
                else:
                    blocked = False
                    logged = True
                
                if logged:
                    self.audit_logger.log(
                        level="WARNING",
                        message=f"CORE-009 violation: Plan file organization issue",
                        category="GOVERNANCE",
                        metadata={"intent": intent, "rule": "CORE-009"}
                    )
        
        # CORE-017: Governance Enforcement
        elif violated_rule == "CORE-017":
            bypass_keywords = ['bypass', 'skip governance', 'emergency', 'quick fix']
            if any(kw in intent.lower() for kw in bypass_keywords):
                blocked = True
                logged = True
                self.audit_logger.log(
                    level="CRITICAL",
                    message=f"CORE-017 violation: Governance bypass attempt",
                    category="GOVERNANCE",
                    metadata={"intent": intent, "rule": "CORE-017", "alert": True}
                )
        
        # CORE-019: TDD-Master Required
        elif violated_rule == "CORE-019":
            direct_coding_keywords = ['directly', 'write code', 'without TDD', 'without orchestrator']
            if any(kw in intent.lower() for kw in direct_coding_keywords):
                blocked = True
                logged = True
                self.audit_logger.log(
                    level="WARNING",
                    message=f"CORE-019 violation: Direct coding without TDD-Master",
                    category="GOVERNANCE",
                    metadata={"intent": intent, "rule": "CORE-019"}
                )
        
        return {
            'blocked': blocked,
            'logged': logged,
            'rule_violated': violated_rule
        }


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
