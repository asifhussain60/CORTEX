# © 2025-2026 Asif Hussain. All rights reserved.
# AC-ID: IR-002-03 - Recommendation Engine Tests
"""
Tests for Recommendation Engine.

PHASE-07: Holistic Intent Router Intelligence
AC-ID: IR-002-03 - Recommendation Engine

Tests cover:
- Best practice matching
- Alternative approach finding
- Test strategy suggestion
- Documentation recommendations
- Governance compliance recommendations
- Recommendation prioritization
"""

import textwrap
from typing import Any, Dict, List

import pytest


# =============================================================================
# TEST FIXTURES
# =============================================================================


@pytest.fixture
def code_needing_patterns() -> str:
    """Python code that could benefit from design patterns."""
    return textwrap.dedent('''
        class DatabaseConnection:
            """A database connection class that should be singleton."""
            
            def __init__(self, url):
                self.url = url
                self.connection = None
            
            def connect(self):
                if self.connection is None:
                    self.connection = create_connection(self.url)
                return self.connection
        
        def get_database():
            """Gets a database connection - recreates each time."""
            return DatabaseConnection("sqlite:///app.db")
    ''')


@pytest.fixture
def code_needing_error_handling() -> str:
    """Python code lacking proper error handling."""
    return textwrap.dedent('''
        def read_config(path):
            """Read config from file."""
            with open(path) as f:
                return json.load(f)
        
        def process_user_input(data):
            """Process user input."""
            value = int(data['value'])
            return value * 2
    ''')


@pytest.fixture
def code_with_api_endpoint() -> str:
    """Python code with API endpoint needing tests."""
    return textwrap.dedent('''
        from flask import Flask, request, jsonify
        
        app = Flask(__name__)
        
        @app.route('/api/users/<int:user_id>', methods=['GET'])
        def get_user(user_id):
            """Get user by ID."""
            user = User.query.get(user_id)
            if not user:
                return jsonify(error="Not found"), 404
            return jsonify(user.to_dict())
        
        @app.route('/api/users', methods=['POST'])
        def create_user():
            """Create new user."""
            data = request.json
            user = User(**data)
            db.session.add(user)
            db.session.commit()
            return jsonify(user.to_dict()), 201
    ''')


@pytest.fixture
def code_without_docstrings() -> str:
    """Python code missing documentation."""
    return textwrap.dedent('''
        class OrderProcessor:
            def process(self, order):
                validated = self._validate(order)
                if validated:
                    return self._submit(order)
                return None
            
            def _validate(self, order):
                return order.amount > 0
            
            def _submit(self, order):
                return order
    ''')


@pytest.fixture
def intent_context() -> Dict[str, Any]:
    """Sample intent context for testing."""
    return {
        "action": "implement",
        "target": "user_service",
        "phase": "PHASE-07",
        "governance_rules": ["CORE-011", "CORE-012"]
    }


# =============================================================================
# TEST CLASSES: BEST PRACTICE MATCHING
# =============================================================================


class TestBestPracticeMatching:
    """Tests for best practice recommendation matching."""

    def test_suggest_singleton_pattern(
        self, code_needing_patterns: str
    ) -> None:
        """Test suggestion of singleton pattern."""
        from src.core.intent.recommendation_engine import RecommendationEngine, RecommendationType
        
        engine = RecommendationEngine()
        
        result = engine.analyze(code_needing_patterns)
        
        pattern_recs = [
            r for r in result.recommendations 
            if r.recommendation_type == RecommendationType.BEST_PRACTICE and "singleton" in r.title.lower()
        ]
        assert len(pattern_recs) >= 1

    def test_suggest_error_handling(
        self, code_needing_error_handling: str
    ) -> None:
        """Test suggestion of error handling patterns."""
        from src.core.intent.recommendation_engine import RecommendationEngine, RecommendationType
        
        engine = RecommendationEngine()
        
        result = engine.analyze(code_needing_error_handling)
        
        error_recs = [
            r for r in result.recommendations 
            if any(word in r.title.lower() for word in ["error", "exception", "handling"])
        ]
        assert len(error_recs) >= 1

    def test_recommend_context_managers(
        self, code_needing_patterns: str
    ) -> None:
        """Test recommendation of context manager usage."""
        from src.core.intent.recommendation_engine import RecommendationEngine
        
        engine = RecommendationEngine()
        
        # Add code with resource management needs
        code = textwrap.dedent('''
            def save_data(data):
                f = open("file.txt", "w")
                f.write(data)
                f.close()  # Manual close
        ''')
        
        result = engine.analyze(code)
        
        context_recs = [
            r for r in result.recommendations 
            if "context" in r.description.lower() or "with" in r.description.lower()
        ]
        assert len(context_recs) >= 1


# =============================================================================
# TEST CLASSES: ALTERNATIVE APPROACH FINDING
# =============================================================================


class TestAlternativeFinding:
    """Tests for alternative approach recommendations."""

    def test_suggest_list_comprehension(self) -> None:
        """Test suggestion of list comprehension over loop."""
        from src.core.intent.recommendation_engine import RecommendationEngine, RecommendationType
        
        engine = RecommendationEngine()
        
        code = textwrap.dedent('''
            def transform_items(items):
                result = []
                for item in items:
                    result.append(item * 2)
                return result
        ''')
        
        result = engine.analyze(code)
        
        comp_recs = [
            r for r in result.recommendations 
            if r.recommendation_type == RecommendationType.ALTERNATIVE
        ]
        assert len(comp_recs) >= 1

    def test_suggest_dict_get(self) -> None:
        """Test suggestion of dict.get() over key access."""
        from src.core.intent.recommendation_engine import RecommendationEngine, RecommendationType
        
        engine = RecommendationEngine()
        
        code = textwrap.dedent('''
            def get_value(data, key):
                if key in data:
                    return data[key]
                return None
        ''')
        
        result = engine.analyze(code)
        
        dict_recs = [
            r for r in result.recommendations 
            if "get" in r.description.lower() or "dict" in r.description.lower()
        ]
        assert len(dict_recs) >= 1


# =============================================================================
# TEST CLASSES: TEST STRATEGY SUGGESTION
# =============================================================================


class TestTestStrategySuggestion:
    """Tests for test strategy recommendations."""

    def test_suggest_api_tests(
        self, code_with_api_endpoint: str
    ) -> None:
        """Test suggestion of API endpoint tests."""
        from src.core.intent.recommendation_engine import RecommendationEngine, RecommendationType
        
        engine = RecommendationEngine()
        
        result = engine.analyze(code_with_api_endpoint)
        
        test_recs = [
            r for r in result.recommendations 
            if r.recommendation_type == RecommendationType.TEST_STRATEGY
        ]
        assert len(test_recs) >= 1

    def test_suggest_edge_case_tests(
        self, code_needing_error_handling: str
    ) -> None:
        """Test suggestion of edge case testing."""
        from src.core.intent.recommendation_engine import RecommendationEngine, RecommendationType
        
        engine = RecommendationEngine()
        
        result = engine.analyze(code_needing_error_handling)
        
        edge_recs = [
            r for r in result.recommendations 
            if r.recommendation_type == RecommendationType.TEST_STRATEGY
        ]
        assert len(edge_recs) >= 1


# =============================================================================
# TEST CLASSES: DOCUMENTATION RECOMMENDATIONS
# =============================================================================


class TestDocumentationRecommendations:
    """Tests for documentation recommendations."""

    def test_suggest_class_docstring(
        self, code_without_docstrings: str
    ) -> None:
        """Test suggestion of class documentation."""
        from src.core.intent.recommendation_engine import RecommendationEngine, RecommendationType
        
        engine = RecommendationEngine()
        
        result = engine.analyze(code_without_docstrings)
        
        doc_recs = [
            r for r in result.recommendations 
            if r.recommendation_type == RecommendationType.DOCUMENTATION
        ]
        assert len(doc_recs) >= 1

    def test_suggest_api_documentation(
        self, code_with_api_endpoint: str
    ) -> None:
        """Test suggestion of API documentation."""
        from src.core.intent.recommendation_engine import RecommendationEngine, RecommendationType
        
        engine = RecommendationEngine()
        
        result = engine.analyze(code_with_api_endpoint)
        
        api_doc_recs = [
            r for r in result.recommendations 
            if r.recommendation_type == RecommendationType.DOCUMENTATION
        ]
        assert len(api_doc_recs) >= 1


# =============================================================================
# TEST CLASSES: GOVERNANCE COMPLIANCE
# =============================================================================


class TestGovernanceCompliance:
    """Tests for governance compliance recommendations."""

    def test_suggest_type_hints(
        self, code_without_docstrings: str
    ) -> None:
        """Test suggestion of type hint addition."""
        from src.core.intent.recommendation_engine import RecommendationEngine, RecommendationType
        
        engine = RecommendationEngine()
        
        result = engine.analyze(code_without_docstrings)
        
        type_recs = [
            r for r in result.recommendations 
            if r.recommendation_type == RecommendationType.GOVERNANCE
        ]
        assert len(type_recs) >= 1


# =============================================================================
# TEST CLASSES: PRIORITIZATION
# =============================================================================


class TestRecommendationPrioritization:
    """Tests for recommendation prioritization."""

    def test_recommendations_have_priority(
        self, code_needing_patterns: str
    ) -> None:
        """Test that recommendations have priority levels."""
        from src.core.intent.recommendation_engine import RecommendationEngine, Priority
        
        engine = RecommendationEngine()
        
        result = engine.analyze(code_needing_patterns)
        
        for rec in result.recommendations:
            assert rec.priority in [Priority.LOW, Priority.MEDIUM, Priority.HIGH]

    def test_recommendations_sorted_by_priority(
        self, code_needing_patterns: str
    ) -> None:
        """Test that recommendations are sorted by priority."""
        from src.core.intent.recommendation_engine import RecommendationEngine
        
        engine = RecommendationEngine()
        
        result = engine.analyze(code_needing_patterns)
        
        if len(result.recommendations) > 1:
            for i in range(len(result.recommendations) - 1):
                # Priority.HIGH = 1, MEDIUM = 2, LOW = 3, so lower value = higher priority
                assert result.recommendations[i].priority.value <= \
                       result.recommendations[i + 1].priority.value


# =============================================================================
# TEST CLASSES: CONTEXT-AWARE RECOMMENDATIONS
# =============================================================================


class TestContextAwareRecommendations:
    """Tests for context-aware recommendations."""

    def test_recommend_based_on_intent(
        self, intent_context: Dict[str, Any]
    ) -> None:
        """Test recommendations based on intent context."""
        from src.core.intent.recommendation_engine import RecommendationEngine
        
        engine = RecommendationEngine()
        
        code = "def create_user(data): pass"
        
        result = engine.analyze(code, intent=str(intent_context))
        
        # Should have contextually relevant recommendations
        assert result is not None
        assert hasattr(result, 'recommendations')


# =============================================================================
# TEST CLASSES: INTEGRATION
# =============================================================================


class TestRecommendationEngineIntegration:
    """Integration tests for recommendation engine."""

    def test_full_recommendation_pipeline(
        self, code_needing_patterns: str
    ) -> None:
        """Test complete recommendation pipeline."""
        from src.core.intent.recommendation_engine import RecommendationEngine, RecommendationResult
        
        engine = RecommendationEngine()
        
        result = engine.analyze(code_needing_patterns)
        
        assert result is not None
        assert isinstance(result, RecommendationResult)
        assert hasattr(result, 'recommendations')
        assert isinstance(result.recommendations, list)

    def test_serialization_to_dict(
        self, code_needing_patterns: str
    ) -> None:
        """Test serialization of recommendations."""
        from src.core.intent.recommendation_engine import RecommendationEngine
        
        engine = RecommendationEngine()
        
        result = engine.analyze(code_needing_patterns)
        
        for rec in result.recommendations:
            serialized = rec.to_dict()
            assert isinstance(serialized, dict)
            assert "type" in serialized
            assert "priority" in serialized
            assert "title" in serialized
            assert "description" in serialized
            assert "rationale" in serialized

    def test_recommendation_has_rationale(
        self, code_needing_patterns: str
    ) -> None:
        """Test that recommendations include rationale."""
        from src.core.intent.recommendation_engine import RecommendationEngine
        
        engine = RecommendationEngine()
        
        result = engine.analyze(code_needing_patterns)
        
        for rec in result.recommendations:
            assert rec.rationale is not None
            assert len(rec.rationale) > 0
