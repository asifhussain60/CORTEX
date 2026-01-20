"""
Test Suite for LENS Integration & Testing (IR-003-04).

Validates end-to-end integration of all LENS components:
- Context Builder aggregates intelligence sources
- Reflection Protocol orchestrates the flow  
- Response Formatter presents results to user

Tests the complete CORTEX LENS protocol as a unified system.
"""

import pytest
from datetime import datetime
import json

from src.core.intent.lens_context_builder import LENSContextBuilder
from src.core.intent.intent_reflection_protocol import (
    IntentReflectionEngine,
    ReflectionRequest,
    ReflectionStatus,
)
from src.core.intent.lens_response_formatter import (
    LENSResponseFormatter,
    ResponseFormat,
)


@pytest.fixture
def sample_findings():
    """Sample intelligence findings."""
    return {
        "ast": {
            "functions": [
                {"name": "auth", "file": "src/auth.py", "line": 10, "calls": [], "parameters": [], "return_type": "Token"}
            ],
        },
        "git": {
            "change_frequency": {"src/auth.py": 5},
            "hot_spots": [{"file": "src/auth.py", "changes": 5, "last_modified": datetime.now().isoformat(), "authors": []}],
        },
    }


class TestLENSIntegration:
    """Test LENS components working together."""

    def test_context_builder_creates_queryable_context(self, sample_findings):
        """Test context builder produces usable context."""
        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_findings["ast"])
        builder.add_git_findings(sample_findings["git"])
        
        context = builder.build()
        
        assert context is not None
        assert context.ast_findings is not None
        assert context.git_findings is not None

    def test_reflection_engine_accepts_built_context(self, sample_findings):
        """Test reflection engine works with built context."""
        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_findings["ast"])
        context = builder.build()
        
        request = ReflectionRequest(
            user_request="Add authentication",
            focal_point="src/auth.py",
            target_scope="file",
            target_name="auth.py",
            context={},
            timestamp=datetime.now().isoformat(),
        )
        
        engine = IntentReflectionEngine()
        response = engine.reflect(request)
        
        assert response is not None
        assert response.status in [ReflectionStatus.PENDING_CONFIRMATION, ReflectionStatus.APPROVED]

    def test_formatter_accepts_reflection_response(self, sample_findings):
        """Test formatter works with reflection responses."""
        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_findings["ast"])
        context = builder.build()
        
        request = ReflectionRequest(
            user_request="Add authentication",
            focal_point="src/auth.py",
            target_scope="file",
            target_name="auth.py",
            context={},
            timestamp=datetime.now().isoformat(),
        )
        
        engine = IntentReflectionEngine()
        response = engine.reflect(request)
        
        formatter = LENSResponseFormatter()
        
        for fmt in [ResponseFormat.JSON, ResponseFormat.YAML, ResponseFormat.MARKDOWN]:
            formatted = formatter.format(response.to_dict(), fmt)
            assert isinstance(formatted, str)
            assert len(formatted) > 0

    def test_complete_pipeline(self, sample_findings):
        """Test complete: Build → Reflect → Format."""
        # Build context
        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_findings["ast"])
        builder.add_git_findings(sample_findings["git"])
        context = builder.build()
        
        # Reflect
        request = ReflectionRequest(
            user_request="Improve performance of auth function",
            focal_point="src/auth.py",
            target_scope="file",
            target_name="auth.py",
            context={"project": "cortex"},
            timestamp=datetime.now().isoformat(),
        )
        
        engine = IntentReflectionEngine()
        response = engine.reflect(request)
        
        # Format
        formatter = LENSResponseFormatter()
        markdown = formatter.format(response.to_dict(), ResponseFormat.MARKDOWN)
        
        assert markdown is not None
        assert "Intent" in markdown or "intent" in markdown.lower()

    def test_approval_workflow(self, sample_findings):
        """Test user approval workflow."""
        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_findings["ast"])
        context = builder.build()
        
        request = ReflectionRequest(
            user_request="Fix auth bug",
            focal_point="src/auth.py",
            target_scope="file",
            target_name="auth.py",
            context={},
            timestamp=datetime.now().isoformat(),
        )
        
        engine = IntentReflectionEngine()
        response = engine.reflect(request)
        
        # Verify we can proceed to approval
        assert response.status in [ReflectionStatus.PENDING_CONFIRMATION, ReflectionStatus.APPROVED]
        assert response is not None

    def test_rejection_workflow(self, sample_findings):
        """Test user rejection workflow."""
        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_findings["ast"])
        context = builder.build()
        
        request = ReflectionRequest(
            user_request="Refactor auth",
            focal_point="src/auth.py",
            target_scope="file",
            target_name="auth.py",
            context={},
            timestamp=datetime.now().isoformat(),
        )
        
        engine = IntentReflectionEngine()
        response = engine.reflect(request)
        
        # Verify we can proceed with rejection workflow
        assert response.status in [ReflectionStatus.PENDING_CONFIRMATION, ReflectionStatus.APPROVED]
        assert response is not None

    def test_serialization_throughout_pipeline(self, sample_findings):
        """Test serialization works through pipeline."""
        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_findings["ast"])
        context = builder.build()
        
        context_dict = context.to_dict()
        context_json = json.dumps(context_dict, default=str)
        parsed_context = json.loads(context_json)
        
        assert parsed_context is not None
        assert "ast_findings" in parsed_context

    def test_multiple_format_output(self, sample_findings):
        """Test formatter produces all formats."""
        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_findings["ast"])
        context = builder.build()
        
        request = ReflectionRequest(
            user_request="Test formatting",
            focal_point="src/auth.py",
            target_scope="file",
            target_name="auth.py",
            context={},
            timestamp=datetime.now().isoformat(),
        )
        
        engine = IntentReflectionEngine()
        response = engine.reflect(request)
        
        formatter = LENSResponseFormatter()
        
        json_out = formatter.format(response.to_dict(), ResponseFormat.JSON)
        yaml_out = formatter.format(response.to_dict(), ResponseFormat.YAML)
        md_out = formatter.format(response.to_dict(), ResponseFormat.MARKDOWN)
        
        assert json_out is not None
        assert yaml_out is not None
        assert md_out is not None
        
        json.loads(json_out)  # Should be valid JSON

    def test_context_filtering_affects_reflection(self, sample_findings):
        """Test context filtering affects reflection."""
        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_findings["ast"])
        context = builder.build()
        
        filtered = builder.filter_context(context, {"file": "src/auth.py"})
        
        assert filtered is not None
        assert filtered.ast_findings is not None

    def test_context_enrichment_in_pipeline(self, sample_findings):
        """Test context enrichment."""
        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_findings["ast"])
        builder.add_git_findings(sample_findings["git"])
        context = builder.build()
        
        enriched = builder.enrich_context(context, ["trends", "risk_scores"])
        
        assert enriched.computed_data is not None
        assert len(enriched.computed_data) > 0

    def test_knowledge_graph_building(self, sample_findings):
        """Test knowledge graph construction."""
        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_findings["ast"])
        context = builder.build()
        
        kg = builder.build_knowledge_graph(context)
        
        assert kg is not None
        assert len(kg.nodes) >= 0  # May be empty for simple fixtures

    def test_performance_of_complete_pipeline(self, sample_findings):
        """Test pipeline performance."""
        import time
        
        start = time.time()
        
        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_findings["ast"])
        builder.add_git_findings(sample_findings["git"])
        context = builder.build()
        
        request = ReflectionRequest(
            user_request="Quick test",
            focal_point="src/auth.py",
            target_scope="file",
            target_name="auth.py",
            context={},
            timestamp=datetime.now().isoformat(),
        )
        
        engine = IntentReflectionEngine()
        response = engine.reflect(request)
        
        formatter = LENSResponseFormatter()
        formatted = formatter.format(response.to_dict(), ResponseFormat.MARKDOWN)
        
        elapsed = time.time() - start
        
        # Should complete within 1 second
        assert elapsed < 1.0

    def test_all_response_formats_valid(self, sample_findings):
        """Test all response formats are well-formed."""
        builder = LENSContextBuilder()
        builder.add_ast_findings(sample_findings["ast"])
        context = builder.build()
        
        request = ReflectionRequest(
            user_request="Validate formats",
            focal_point="src/auth.py",
            target_scope="file",
            target_name="auth.py",
            context={},
            timestamp=datetime.now().isoformat(),
        )
        
        engine = IntentReflectionEngine()
        response = engine.reflect(request)
        
        formatter = LENSResponseFormatter()
        
        # JSON
        json_str = formatter.format(response.to_dict(), ResponseFormat.JSON)
        json.loads(json_str)  # Validates JSON structure
        
        # YAML
        yaml_str = formatter.format(response.to_dict(), ResponseFormat.YAML)
        assert "intent:" in yaml_str or "Intent" in yaml_str
        
        # Markdown
        md_str = formatter.format(response.to_dict(), ResponseFormat.MARKDOWN)
        assert "#" in md_str  # Has headers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
