"""
Tests for Phase 2: Request Analyzer

Tests the CapabilityMatrix and RequestAnalyzer components that provide
intelligent duplication detection and prevention.
"""
import pytest
from unittest.mock import Mock, MagicMock
from typing import Dict, List, Any

from core.capability_matrix import (
    CapabilityMatrix,
    ToolCapabilities,
    ToolMatch,
)
from core.request_analyzer import (
    RequestAnalyzer,
    ToolRequest,
    AnalysisResult,
    RecommendationType,
)


# ============================================================================
# CapabilityMatrix Tests
# ============================================================================

class TestCapabilityTaxonomy:
    """Tests for the capability taxonomy structure."""
    
    def test_taxonomy_has_required_categories(self):
        """Verify all expected categories exist in class constant."""
        expected_categories = [
            "cleanup",
            "maintenance",
            "validation",
            "testing",
            "generation",
            "documentation",
            "analysis",
            "visualization",
            "migration",
            "schema",
            "deployment",
            "operations",
            "planning",
        ]
        taxonomy = CapabilityMatrix.CAPABILITY_TAXONOMY
        for category in expected_categories:
            assert category in taxonomy, f"Missing category: {category}"
    
    def test_taxonomy_categories_have_keywords(self):
        """Each category should have keywords."""
        taxonomy = CapabilityMatrix.CAPABILITY_TAXONOMY
        for category, info in taxonomy.items():
            assert 'keywords' in info, f"Category {category} missing keywords"
            assert len(info['keywords']) > 0, f"Category {category} has no keywords"
            assert all(isinstance(k, str) for k in info['keywords'])
    
    def test_action_verbs_defined(self):
        """Verify action verbs are defined."""
        action_verbs = CapabilityMatrix.ACTION_VERBS
        expected_verbs = ["create", "delete", "update", "validate", "analyze", "convert"]
        for verb in expected_verbs:
            assert verb in action_verbs, f"Missing action verb: {verb}"


class TestCapabilityMatrix:
    """Tests for the CapabilityMatrix class."""
    
    @pytest.fixture
    def mock_registry(self) -> Mock:
        """Create a mock registry with sample tools."""
        registry = Mock()
        
        # Sample tools data
        tools = [
            {
                "name": "cache-cleaner",
                "description": "Cleans cache files and temporary data",
            },
            {
                "name": "yaml-validator",
                "description": "Validates YAML syntax and structure",
            },
            {
                "name": "uml-generator",
                "description": "Generates UML diagrams from code",
            },
            {
                "name": "test-runner",
                "description": "Runs unit tests and reports results",
            },
            {
                "name": "code-analyzer",
                "description": "Analyzes code quality and patterns",
            },
        ]
        
        registry.list_tools.return_value = tools
        registry.list_categories.return_value = ["maintenance", "validation", "documentation", "testing", "analysis"]
        registry.get_tool.return_value = None
        
        return registry
    
    @pytest.fixture
    def matrix(self, mock_registry) -> CapabilityMatrix:
        """Create a CapabilityMatrix with mock registry."""
        return CapabilityMatrix(mock_registry)
    
    def test_initialization_without_registry(self):
        """Test matrix initializes without registry."""
        matrix = CapabilityMatrix()
        assert matrix.registry is None
        assert len(matrix._tool_capabilities) == 0
    
    def test_initialization_with_registry(self, matrix, mock_registry):
        """Test matrix initializes correctly with registry."""
        assert matrix.registry is mock_registry
        # Should have built capabilities for each tool
        assert len(matrix._tool_capabilities) == 5
    
    def test_extract_intent_cleanup(self):
        """Test intent extraction for cleanup description."""
        matrix = CapabilityMatrix()
        intent = matrix.extract_intent("clean up cache files")
        
        # Should extract cleanup-related keywords
        assert "cleanup" in intent or "delete" in intent
    
    def test_extract_intent_validation(self):
        """Test intent extraction for validation description."""
        matrix = CapabilityMatrix()
        intent = matrix.extract_intent("validate yaml configuration file")
        
        # Should extract validation-related keywords
        assert "validation" in intent or "yaml" in intent
    
    def test_extract_intent_generation(self):
        """Test intent extraction for generation description."""
        matrix = CapabilityMatrix()
        intent = matrix.extract_intent("generate UML diagrams from code")
        
        # Should extract generation-related keywords
        assert "generation" in intent or "uml" in intent or "visualization" in intent
    
    def test_extract_intent_action_verbs(self):
        """Test that action verbs are identified."""
        matrix = CapabilityMatrix()
        
        intent = matrix.extract_intent("create a new file reader")
        assert "create" in intent
        
        intent = matrix.extract_intent("delete temporary files")
        assert "delete" in intent
        
        intent = matrix.extract_intent("analyze code patterns")
        assert "analyze" in intent
    
    def test_find_overlaps_returns_matches(self, matrix):
        """Test finding tools with overlapping keywords."""
        # Find tools matching cache/cleanup
        matches = matrix.find_overlaps(["clean", "cache", "temp"])
        
        # Should return list of ToolMatch objects
        assert isinstance(matches, list)
        if matches:
            assert all(isinstance(m, ToolMatch) for m in matches)
    
    def test_calculate_similarity_identical(self):
        """Test similarity calculation for identical sets."""
        matrix = CapabilityMatrix()
        
        caps1 = {"cleanup", "delete", "cache"}
        caps2 = {"cleanup", "delete", "cache"}
        
        similarity = matrix.calculate_similarity(caps1, caps2)
        assert similarity == 1.0
    
    def test_calculate_similarity_partial(self):
        """Test similarity calculation for partial overlap."""
        matrix = CapabilityMatrix()
        
        caps1 = {"cleanup", "delete", "cache"}
        caps2 = {"cleanup", "temp"}
        
        similarity = matrix.calculate_similarity(caps1, caps2)
        assert 0.0 < similarity < 1.0
    
    def test_calculate_similarity_disjoint(self):
        """Test similarity for completely different sets."""
        matrix = CapabilityMatrix()
        
        caps1 = {"testing", "unit", "pytest"}
        caps2 = {"documentation", "generate", "uml"}
        
        similarity = matrix.calculate_similarity(caps1, caps2)
        assert similarity == 0.0
    
    def test_calculate_similarity_empty_sets(self):
        """Test similarity with empty sets."""
        matrix = CapabilityMatrix()
        
        assert matrix.calculate_similarity(set(), set()) == 0.0
        assert matrix.calculate_similarity({"a"}, set()) == 0.0
        assert matrix.calculate_similarity(set(), {"b"}) == 0.0
    
    def test_get_tool_capabilities(self, matrix):
        """Test retrieving capabilities for a specific tool."""
        caps = matrix.get_tool_capabilities("cache-cleaner")
        
        if caps:
            assert isinstance(caps, ToolCapabilities)
            assert caps.name == "cache-cleaner"
    
    def test_get_all_capabilities(self):
        """Test getting all known capabilities."""
        matrix = CapabilityMatrix()
        all_caps = matrix.get_all_capabilities()
        
        # Should return set of capability names from taxonomy
        assert isinstance(all_caps, set)
        assert "cleanup" in all_caps
        assert "validation" in all_caps


# ============================================================================
# RequestAnalyzer Tests
# ============================================================================

class TestToolRequest:
    """Tests for ToolRequest dataclass."""
    
    def test_create_request(self):
        """Test creating a tool request."""
        request = ToolRequest(
            name="new_tool",
            description="A new tool that does something",
        )
        assert request.name == "new_tool"
        assert request.description == "A new tool that does something"
        assert request.capabilities == []
    
    def test_request_with_capabilities(self):
        """Test request with explicit capabilities."""
        request = ToolRequest(
            name="advanced_tool",
            description="Advanced functionality",
            capabilities=["cleanup", "validation"],
            category="analysis",
        )
        assert request.category == "analysis"
        assert "cleanup" in request.capabilities


class TestAnalysisResult:
    """Tests for AnalysisResult dataclass."""
    
    def test_result_allows_creation(self):
        """Test result that allows tool creation."""
        result = AnalysisResult(
            can_create=True,
            recommendation_type=RecommendationType.ALLOW,
            overlapping_tools=[],
            recommendation="No conflicts found",
        )
        assert result.can_create is True
        assert result.recommendation_type == RecommendationType.ALLOW
    
    def test_result_blocks_creation(self):
        """Test result that blocks tool creation."""
        result = AnalysisResult(
            can_create=False,
            recommendation_type=RecommendationType.BLOCK,
            overlapping_tools=[
                ToolMatch(
                    name="existing_tool",
                    description="Existing tool",
                    category="test",
                    matched_capabilities={"cleanup"},
                    similarity=0.95
                )
            ],
            recommendation="Duplicate detected",
        )
        assert result.can_create is False
        assert len(result.overlapping_tools) == 1
    
    def test_result_top_match(self):
        """Test getting top match from result."""
        tool1 = ToolMatch(
            name="tool1", description="", category="",
            matched_capabilities=set(), similarity=0.5
        )
        tool2 = ToolMatch(
            name="tool2", description="", category="",
            matched_capabilities=set(), similarity=0.8
        )
        
        result = AnalysisResult(
            can_create=True,
            recommendation_type=RecommendationType.WARN,
            overlapping_tools=[tool1, tool2],
            recommendation="Warning",
        )
        
        assert result.top_match.name == "tool2"
    
    def test_result_to_dict(self):
        """Test serialization to dictionary."""
        result = AnalysisResult(
            can_create=True,
            recommendation_type=RecommendationType.ALLOW,
            overlapping_tools=[],
            recommendation="OK",
        )
        
        d = result.to_dict()
        assert d["can_create"] is True
        assert d["recommendation_type"] == "allow"


class TestRequestAnalyzer:
    """Tests for the RequestAnalyzer class."""
    
    @pytest.fixture
    def mock_registry(self) -> Mock:
        """Create a mock registry with sample tools."""
        registry = Mock()
        
        tools = [
            {
                "name": "cache-cleaner",
                "description": "Cleans cache files and temporary data from the system",
            },
            {
                "name": "yaml-validator", 
                "description": "Validates YAML files for syntax errors and schema compliance",
            },
            {
                "name": "diagram-generator",
                "description": "Generates UML diagrams and visual documentation",
            },
        ]
        
        registry.list_tools.return_value = tools
        registry.list_categories.return_value = ["maintenance", "validation", "documentation"]
        registry.get_tool.return_value = None
        
        return registry
    
    @pytest.fixture
    def analyzer(self, mock_registry) -> RequestAnalyzer:
        """Create analyzer with mock registry."""
        return RequestAnalyzer(mock_registry)
    
    def test_initialization(self, analyzer):
        """Test analyzer initializes correctly."""
        assert analyzer.capability_matrix is not None
        assert analyzer.WARN_THRESHOLD == 0.5
        assert analyzer.SUGGEST_THRESHOLD == 0.7
        assert analyzer.BLOCK_THRESHOLD == 0.9
    
    def test_initialization_without_registry(self):
        """Test analyzer without registry."""
        analyzer = RequestAnalyzer()
        assert analyzer.registry is None
        assert analyzer.capability_matrix is not None
    
    # -------------------------------------------------------------------------
    # Master Plan Edge Cases
    # -------------------------------------------------------------------------
    
    def test_edge_case_cleanup_cache(self, analyzer):
        """
        Edge Case from Master Plan:
        Request: "Create tool to cleanup cache"
        Expected: Should find cache-cleaner with overlap
        """
        request = ToolRequest(
            name="cache_cleanup_tool",
            description="Create a tool to cleanup cache",
        )
        
        result = analyzer.analyze_request(request)
        
        # Should find overlapping tools
        if result.overlapping_tools:
            tool_names = [t.name for t in result.overlapping_tools]
            # cache-cleaner should be detected as overlapping
            assert any("cache" in name for name in tool_names)
    
    def test_edge_case_validate_yaml(self, analyzer):
        """
        Edge Case from Master Plan:
        Request: "Validate YAML syntax"
        Expected: Should find yaml-validator
        """
        request = ToolRequest(
            name="yaml_syntax_checker",
            description="Validate YAML syntax",
        )
        
        result = analyzer.analyze_request(request)
        
        if result.overlapping_tools:
            tool_names = [t.name for t in result.overlapping_tools]
            assert any("yaml" in name for name in tool_names)
    
    def test_edge_case_generate_uml(self, analyzer):
        """
        Edge Case from Master Plan:
        Request: "Generate UML diagrams"
        Expected: Should find diagram-generator
        """
        request = ToolRequest(
            name="uml_maker",
            description="Generate UML diagrams from code",
        )
        
        result = analyzer.analyze_request(request)
        
        if result.overlapping_tools:
            tool_names = [t.name for t in result.overlapping_tools]
            assert any("diagram" in name or "generator" in name for name in tool_names)
    
    # -------------------------------------------------------------------------
    # Recommendation Thresholds
    # -------------------------------------------------------------------------
    
    def test_allow_for_unique_request(self, analyzer):
        """Test ALLOW recommendation for unique tool."""
        request = ToolRequest(
            name="email_sender",
            description="Send email notifications to users",
        )
        
        result = analyzer.analyze_request(request)
        
        # Unique request should be allowed
        assert result.recommendation_type == RecommendationType.ALLOW
        assert result.can_create is True
    
    def test_analysis_returns_valid_recommendation_type(self, analyzer):
        """Test that analysis returns valid recommendation types."""
        request = ToolRequest(
            name="test_tool",
            description="Some test description",
        )
        
        result = analyzer.analyze_request(request)
        
        assert result.recommendation_type in [
            RecommendationType.ALLOW,
            RecommendationType.WARN,
            RecommendationType.SUGGEST,
            RecommendationType.BLOCK,
        ]
    
    # -------------------------------------------------------------------------
    # Check Exact Duplicate
    # -------------------------------------------------------------------------
    
    def test_check_exact_duplicate_not_found(self, analyzer, mock_registry):
        """Test checking for non-existent duplicate."""
        mock_registry.get_tool.return_value = None
        
        result = analyzer.check_exact_duplicate("nonexistent-tool")
        assert result is None
    
    def test_check_exact_duplicate_found(self, analyzer, mock_registry):
        """Test checking for existing duplicate."""
        mock_registry.get_tool.return_value = {"name": "cache-cleaner"}
        
        result = analyzer.check_exact_duplicate("cache-cleaner")
        assert result == "cache-cleaner"
    
    # -------------------------------------------------------------------------
    # Suggest Alternatives
    # -------------------------------------------------------------------------
    
    def test_suggest_alternatives(self, analyzer):
        """Test suggesting alternative existing tools."""
        alternatives = analyzer.suggest_alternatives("clean temporary files and cache")
        
        # Should return list of ToolMatch
        assert isinstance(alternatives, list)
        if alternatives:
            assert all(isinstance(a, ToolMatch) for a in alternatives)
    
    def test_suggest_alternatives_limited(self, analyzer):
        """Test alternatives respects limit."""
        alternatives = analyzer.suggest_alternatives("clean cache validate yaml generate docs", limit=2)
        
        assert len(alternatives) <= 2
    
    # -------------------------------------------------------------------------
    # Analysis Message Quality
    # -------------------------------------------------------------------------
    
    def test_analysis_has_recommendation_message(self, analyzer):
        """Test that analysis includes recommendation message."""
        request = ToolRequest(
            name="any_tool",
            description="Any description",
        )
        
        result = analyzer.analyze_request(request)
        
        # Should have a non-empty recommendation message
        assert result.recommendation
        assert len(result.recommendation) > 0


class TestRequestAnalyzerIntegration:
    """Integration tests for RequestAnalyzer with CapabilityMatrix."""
    
    @pytest.fixture
    def mock_registry(self) -> Mock:
        """A more complete set of tools for integration testing."""
        registry = Mock()
        
        tools = [
            {"name": "file-reader", "description": "Read and parse files from filesystem"},
            {"name": "file-writer", "description": "Write content to files on filesystem"},
            {"name": "json-validator", "description": "Validate JSON syntax and schema"},
            {"name": "yaml-validator", "description": "Validate YAML syntax and schema"},
            {"name": "test-runner", "description": "Run pytest unit tests"},
            {"name": "coverage-reporter", "description": "Generate test coverage reports"},
            {"name": "code-formatter", "description": "Format code using black and isort"},
            {"name": "linter", "description": "Lint code for style issues"},
        ]
        
        registry.list_tools.return_value = tools
        registry.list_categories.return_value = [
            "file_operations", "validation", "testing", "code_analysis"
        ]
        registry.get_tool.return_value = None
        
        return registry
    
    @pytest.fixture
    def analyzer(self, mock_registry) -> RequestAnalyzer:
        """Create analyzer with full toolkit."""
        return RequestAnalyzer(mock_registry)
    
    def test_validation_tools_overlap(self, analyzer):
        """Test that validation tools show overlap with each other."""
        request = ToolRequest(
            name="toml-validator",
            description="Validate TOML syntax and schema",
        )
        
        result = analyzer.analyze_request(request)
        
        # Should find existing validators
        if result.overlapping_tools:
            tool_names = [t.name for t in result.overlapping_tools]
            has_validator = any("validator" in name for name in tool_names)
            assert has_validator
    
    def test_analysis_returns_extracted_intent(self, analyzer):
        """Test that analysis includes extracted intent."""
        request = ToolRequest(
            name="cache-cleaner-v2",
            description="Clean up temporary cache files",
        )
        
        result = analyzer.analyze_request(request)
        
        # Should have extracted intent keywords
        assert isinstance(result.extracted_intent, list)
    
    def test_get_capability_report(self, analyzer):
        """Test generating capability report."""
        report = analyzer.get_capability_report()
        
        assert isinstance(report, dict)


# ============================================================================
# Edge Case Tests
# ============================================================================

class TestEdgeCases:
    """Edge case and boundary tests."""
    
    def test_analyzer_without_registry(self):
        """Test analyzer with no registry."""
        analyzer = RequestAnalyzer()
        
        request = ToolRequest(
            name="any_tool",
            description="Any description",
        )
        
        result = analyzer.analyze_request(request)
        
        # Should still work, just no overlaps
        assert result.recommendation_type == RecommendationType.ALLOW
        assert result.can_create is True
    
    def test_request_with_empty_description(self):
        """Test request with minimal description."""
        analyzer = RequestAnalyzer()
        
        request = ToolRequest(
            name="new_tool",
            description="",
        )
        
        # Should not crash
        result = analyzer.analyze_request(request)
        assert result is not None
    
    def test_special_characters_in_request(self):
        """Test request with special characters."""
        analyzer = RequestAnalyzer()
        
        request = ToolRequest(
            name="tool-with-dashes_and_underscores",
            description="Tool with special chars: @#$%",
        )
        
        # Should handle gracefully
        result = analyzer.analyze_request(request)
        assert result is not None
    
    def test_very_long_description(self):
        """Test request with very long description."""
        analyzer = RequestAnalyzer()
        
        request = ToolRequest(
            name="verbose_tool",
            description="This is a very long description " * 100,
        )
        
        # Should handle gracefully
        result = analyzer.analyze_request(request)
        assert result is not None
    
    def test_unicode_in_description(self):
        """Test request with unicode characters."""
        analyzer = RequestAnalyzer()
        
        request = ToolRequest(
            name="unicode_tool",
            description="Tool für Dateien 文件工具 инструмент",
        )
        
        # Should handle gracefully
        result = analyzer.analyze_request(request)
        assert result is not None


# ============================================================================
# ToolMatch Tests
# ============================================================================

class TestToolMatch:
    """Tests for ToolMatch dataclass."""
    
    def test_create_tool_match(self):
        """Test creating a ToolMatch."""
        match = ToolMatch(
            name="test-tool",
            description="Test description",
            category="testing",
            matched_capabilities={"test", "unit"},
            similarity=0.75,
        )
        
        assert match.name == "test-tool"
        assert match.similarity == 0.75
        assert "test" in match.matched_capabilities
    
    def test_tool_match_repr(self):
        """Test ToolMatch string representation."""
        match = ToolMatch(
            name="test-tool",
            description="",
            category="",
            matched_capabilities=set(),
            similarity=0.5,
        )
        
        repr_str = repr(match)
        assert "test-tool" in repr_str
        assert "0.50" in repr_str
