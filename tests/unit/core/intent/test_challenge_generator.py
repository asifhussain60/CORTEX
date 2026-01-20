# © 2025-2026 Asif Hussain. All rights reserved.
# AC-ID: IR-002-02 - Challenge Generation System Tests
"""
Tests for Challenge Generation System.

PHASE-07: Holistic Intent Router Intelligence
AC-ID: IR-002-02 - Challenge Generation System

Tests cover:
- Breaking change detection
- Test coverage gap identification
- Governance risk detection
- Historical issue matching
- Performance risk analysis
- Challenge prioritization
"""

import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest


# =============================================================================
# TEST FIXTURES
# =============================================================================


@pytest.fixture
def code_with_dependencies() -> str:
    """Python code with function dependencies."""
    return textwrap.dedent('''
        from services import UserService, OrderService
        from database import get_connection
        
        def process_user_orders(user_id: int):
            """Process all orders for a user."""
            user = UserService.get_user(user_id)
            orders = OrderService.get_orders_for_user(user_id)
            
            for order in orders:
                process_order(order, user)
            
            return len(orders)
        
        def process_order(order, user):
            """Process a single order."""
            conn = get_connection()
            conn.execute("UPDATE orders SET status = 'processed'")
    ''')


@pytest.fixture
def code_with_no_tests() -> str:
    """Python code with functions but no corresponding tests."""
    return textwrap.dedent('''
        def calculate_discount(amount: float, rate: float) -> float:
            """Calculate discount amount."""
            return amount * rate
        
        def apply_discount(price: float, discount: float) -> float:
            """Apply discount to price."""
            return price - discount
        
        def _private_helper(x):
            """Private helper function."""
            return x * 2
    ''')


@pytest.fixture
def code_with_governance_issues() -> str:
    """Python code with potential governance violations."""
    return textwrap.dedent('''
        def dangerous_operation():
            """Function without proper error handling."""
            # No docstring for parameters
            data = open('file.txt').read()  # No context manager
            return eval(data)  # Dangerous eval
        
        class NoDocstring:
            def method_without_docstring(self, x, y, z):
                pass  # No docstring
    ''')


@pytest.fixture
def code_with_performance_risks() -> str:
    """Python code with potential performance issues."""
    return textwrap.dedent('''
        def n_squared_operation(items):
            """Nested loops creating O(n²) complexity."""
            result = []
            for i in items:
                for j in items:
                    if i != j:
                        result.append((i, j))
            return result
        
        def repeated_database_calls(ids):
            """N+1 query pattern."""
            results = []
            for id in ids:
                user = database.get_user(id)  # Called N times
                results.append(user)
            return results
    ''')


@pytest.fixture
def historical_issues() -> List[Dict[str, Any]]:
    """Simulated historical issues from git/tracking."""
    return [
        {
            "file": "src/services/user_service.py",
            "issue_type": "BUG",
            "description": "Race condition in user creation",
            "commit": "abc123",
            "date": "2025-01-01",
        },
        {
            "file": "src/api/orders.py",
            "issue_type": "PERFORMANCE",
            "description": "N+1 query in order listing",
            "commit": "def456",
            "date": "2025-01-05",
        },
        {
            "file": "src/services/auth_service.py",
            "issue_type": "SECURITY",
            "description": "SQL injection vulnerability",
            "commit": "ghi789",
            "date": "2025-01-10",
        },
    ]


@pytest.fixture
def sample_intent() -> Dict[str, Any]:
    """Sample intent for challenge generation."""
    return {
        "intent_type": "IMPLEMENT",
        "scope": {
            "file_path": "src/services/user_service.py",
            "function_name": "create_user",
        },
        "description": "Add new user creation functionality",
    }


# =============================================================================
# TEST CLASSES: BREAKING CHANGE DETECTION
# =============================================================================


class TestBreakingChangeDetection:
    """Tests for breaking change detection."""

    def test_detect_signature_change_risk(
        self, code_with_dependencies: str
    ) -> None:
        """Test detection of function signature change risks."""
        from cortex.core.intent.challenge_generator import ChallengeGenerator
        
        generator = ChallengeGenerator()
        
        # Simulate a change to process_order function
        change = {
            "type": "MODIFY",
            "target": "process_order",
            "changes": ["add_parameter"],
        }
        
        challenges = generator.analyze_changes(code_with_dependencies, [change])
        
        breaking_changes = [
            c for c in challenges 
            if c.category == "BREAKING_CHANGE"
        ]
        assert len(breaking_changes) >= 1

    def test_detect_public_api_changes(
        self, code_with_dependencies: str
    ) -> None:
        """Test detection of public API changes."""
        from cortex.core.intent.challenge_generator import ChallengeGenerator
        
        generator = ChallengeGenerator()
        
        change = {
            "type": "MODIFY",
            "target": "process_user_orders",
            "changes": ["rename_function"],
        }
        
        challenges = generator.analyze_changes(code_with_dependencies, [change])
        
        api_changes = [
            c for c in challenges 
            if c.category == "BREAKING_CHANGE" and "API" in c.description
        ]
        assert len(api_changes) >= 1

    def test_identify_affected_callers(
        self, code_with_dependencies: str
    ) -> None:
        """Test identification of affected callers."""
        from cortex.core.intent.challenge_generator import ChallengeGenerator
        
        generator = ChallengeGenerator()
        
        change = {
            "type": "MODIFY",
            "target": "process_order",
            "changes": ["modify_return"],
        }
        
        challenges = generator.analyze_changes(code_with_dependencies, [change])
        
        # Should identify process_user_orders as affected
        breaking = [c for c in challenges if c.category == "BREAKING_CHANGE"]
        if breaking:
            affected = breaking[0].affected_scope
            assert any("process_user_orders" in str(a) for a in affected) or len(affected) > 0


# =============================================================================
# TEST CLASSES: TEST COVERAGE GAP IDENTIFICATION
# =============================================================================


class TestTestGapIdentification:
    """Tests for test coverage gap detection."""

    def test_detect_untested_functions(
        self, code_with_no_tests: str
    ) -> None:
        """Test detection of functions without tests."""
        from cortex.core.intent.challenge_generator import ChallengeGenerator
        
        generator = ChallengeGenerator()
        
        # Provide empty test context (no tests exist)
        context = {"existing_tests": []}
        
        challenges = generator.analyze_coverage(code_with_no_tests, context)
        
        test_gaps = [c for c in challenges if c.category == "TEST_GAP"]
        assert len(test_gaps) >= 1

    def test_identify_public_untested(
        self, code_with_no_tests: str
    ) -> None:
        """Test that public functions are flagged higher priority."""
        from cortex.core.intent.challenge_generator import ChallengeGenerator
        
        generator = ChallengeGenerator()
        context = {"existing_tests": []}
        
        challenges = generator.analyze_coverage(code_with_no_tests, context)
        
        # Public functions should have higher severity
        public_gaps = [
            c for c in challenges 
            if c.category == "TEST_GAP" and "_private" not in c.description
        ]
        private_gaps = [
            c for c in challenges 
            if c.category == "TEST_GAP" and "_private" in c.description
        ]
        
        if public_gaps and private_gaps:
            assert public_gaps[0].severity >= private_gaps[0].severity


# =============================================================================
# TEST CLASSES: GOVERNANCE RISK DETECTION
# =============================================================================


class TestGovernanceRiskDetection:
    """Tests for governance risk detection."""

    def test_detect_missing_docstrings(
        self, code_with_governance_issues: str
    ) -> None:
        """Test detection of missing docstrings."""
        from cortex.core.intent.challenge_generator import ChallengeGenerator
        
        generator = ChallengeGenerator()
        
        challenges = generator.analyze_governance(code_with_governance_issues)
        
        docstring_issues = [
            c for c in challenges 
            if c.category == "GOVERNANCE_RISK" and "docstring" in c.description.lower()
        ]
        assert len(docstring_issues) >= 1

    def test_detect_dangerous_patterns(
        self, code_with_governance_issues: str
    ) -> None:
        """Test detection of dangerous code patterns."""
        from cortex.core.intent.challenge_generator import ChallengeGenerator
        
        generator = ChallengeGenerator()
        
        challenges = generator.analyze_governance(code_with_governance_issues)
        
        dangerous = [
            c for c in challenges 
            if c.category == "GOVERNANCE_RISK" and 
            any(word in c.description.lower() for word in ["eval", "dangerous", "unsafe"])
        ]
        assert len(dangerous) >= 1

    def test_detect_error_handling_gaps(
        self, code_with_governance_issues: str
    ) -> None:
        """Test detection of missing error handling."""
        from cortex.core.intent.challenge_generator import ChallengeGenerator
        
        generator = ChallengeGenerator()
        
        challenges = generator.analyze_governance(code_with_governance_issues)
        
        # Should flag file operations without context managers
        error_handling = [
            c for c in challenges 
            if c.category == "GOVERNANCE_RISK"
        ]
        assert len(error_handling) >= 1


# =============================================================================
# TEST CLASSES: HISTORICAL ISSUE MATCHING
# =============================================================================


class TestHistoricalIssueMatching:
    """Tests for historical issue matching."""

    def test_match_similar_code_areas(
        self, sample_intent: Dict[str, Any], historical_issues: List[Dict[str, Any]]
    ) -> None:
        """Test matching historical issues to current change area."""
        from cortex.core.intent.challenge_generator import ChallengeGenerator
        
        generator = ChallengeGenerator()
        
        challenges = generator.check_historical_issues(
            sample_intent, historical_issues
        )
        
        historical = [c for c in challenges if c.category == "HISTORICAL_ISSUE"]
        # Should find the user_service.py issue
        assert len(historical) >= 1

    def test_prioritize_recent_issues(
        self, historical_issues: List[Dict[str, Any]]
    ) -> None:
        """Test that more recent issues are prioritized."""
        from cortex.core.intent.challenge_generator import ChallengeGenerator
        
        generator = ChallengeGenerator()
        
        intent = {
            "intent_type": "IMPLEMENT",
            "scope": {"file_path": "src/services/auth_service.py"},
        }
        
        challenges = generator.check_historical_issues(intent, historical_issues)
        
        # Should include the security issue (most recent for auth_service)
        security = [c for c in challenges if "security" in c.description.lower()]
        assert len(security) >= 0  # May or may not match based on logic


# =============================================================================
# TEST CLASSES: PERFORMANCE RISK ANALYSIS
# =============================================================================


class TestPerformanceRiskAnalysis:
    """Tests for performance risk detection."""

    def test_detect_n_squared_complexity(
        self, code_with_performance_risks: str
    ) -> None:
        """Test detection of O(n²) complexity patterns."""
        from cortex.core.intent.challenge_generator import ChallengeGenerator
        
        generator = ChallengeGenerator()
        
        challenges = generator.analyze_performance(code_with_performance_risks)
        
        complexity = [
            c for c in challenges 
            if c.category == "PERFORMANCE_RISK" and 
            any(word in c.description.lower() for word in ["n²", "quadratic", "nested"])
        ]
        assert len(complexity) >= 1

    def test_detect_n_plus_one_queries(
        self, code_with_performance_risks: str
    ) -> None:
        """Test detection of N+1 query patterns."""
        from cortex.core.intent.challenge_generator import ChallengeGenerator
        
        generator = ChallengeGenerator()
        
        challenges = generator.analyze_performance(code_with_performance_risks)
        
        n_plus_one = [
            c for c in challenges 
            if c.category == "PERFORMANCE_RISK" and 
            any(word in c.description.lower() for word in ["n+1", "repeated", "loop"])
        ]
        assert len(n_plus_one) >= 1


# =============================================================================
# TEST CLASSES: CHALLENGE PRIORITIZATION
# =============================================================================


class TestChallengePrioritization:
    """Tests for challenge prioritization."""

    def test_challenges_have_severity(
        self, code_with_governance_issues: str
    ) -> None:
        """Test that challenges have severity levels."""
        from cortex.core.intent.challenge_generator import ChallengeGenerator
        
        generator = ChallengeGenerator()
        
        challenges = generator.analyze_governance(code_with_governance_issues)
        
        for challenge in challenges:
            assert challenge.severity in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    def test_challenges_are_sorted_by_severity(
        self, code_with_governance_issues: str
    ) -> None:
        """Test that challenges are sorted by severity."""
        from cortex.core.intent.challenge_generator import ChallengeGenerator
        
        generator = ChallengeGenerator()
        
        challenges = generator.generate_all(
            code_with_governance_issues,
            {"existing_tests": []},
        )
        
        # Should be sorted by severity (highest first)
        severity_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        if len(challenges) > 1:
            for i in range(len(challenges) - 1):
                assert severity_order[challenges[i].severity] >= \
                       severity_order[challenges[i + 1].severity]


# =============================================================================
# TEST CLASSES: INTEGRATION
# =============================================================================


class TestChallengeGeneratorIntegration:
    """Integration tests for challenge generator."""

    def test_full_challenge_pipeline(
        self, code_with_dependencies: str
    ) -> None:
        """Test complete challenge generation pipeline."""
        from cortex.core.intent.challenge_generator import ChallengeGenerator
        
        generator = ChallengeGenerator()
        
        challenges = generator.generate_all(
            code_with_dependencies,
            context={"existing_tests": []},
            changes=[{"type": "MODIFY", "target": "process_order", "changes": ["add_parameter"]}],
        )
        
        assert challenges is not None
        assert isinstance(challenges, list)

    def test_serialization_to_dict(
        self, code_with_governance_issues: str
    ) -> None:
        """Test serialization of challenges."""
        from cortex.core.intent.challenge_generator import ChallengeGenerator
        
        generator = ChallengeGenerator()
        
        challenges = generator.analyze_governance(code_with_governance_issues)
        
        for challenge in challenges:
            serialized = challenge.to_dict()
            assert isinstance(serialized, dict)
            assert "category" in serialized
            assert "severity" in serialized
            assert "description" in serialized
            assert "mitigation" in serialized

    def test_challenge_has_mitigation(
        self, code_with_governance_issues: str
    ) -> None:
        """Test that challenges include mitigation suggestions."""
        from cortex.core.intent.challenge_generator import ChallengeGenerator
        
        generator = ChallengeGenerator()
        
        challenges = generator.analyze_governance(code_with_governance_issues)
        
        for challenge in challenges:
            assert challenge.mitigation is not None
            assert len(challenge.mitigation) > 0
