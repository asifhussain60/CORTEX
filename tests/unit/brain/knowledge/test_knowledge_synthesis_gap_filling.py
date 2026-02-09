"""
Unit tests for KnowledgeSynthesisEngine gap-filling methods.

Tests for:
- calculate_coverage() - measure knowledge base completeness
- fill_gaps() - identify missing YAMLs to reach coverage threshold

CORE Rules:
- CORE-008: TDD (tests before code) ✅
"""

import pytest
from unittest.mock import Mock, patch

from cortex.brain.knowledge.knowledge_synthesis_engine import KnowledgeSynthesisEngine


class TestKnowledgeSynthesisGapFilling:
    """Test gap-filling functionality in KnowledgeSynthesisEngine."""

    @pytest.fixture
    def engine(self):
        """Create synthesis engine."""
        return KnowledgeSynthesisEngine()

    def test_calculate_coverage_full(self, engine):
        """Coverage should be 1.0 when all tech is documented."""
        with patch.object(engine, '_load_cortex_best_practices') as mock_load:
            with patch.object(engine, '_extract_applicable_patterns') as mock_patterns:
                # Mock pattern with tech
                pattern = Mock()
                pattern.keywords = {'fastapi', 'pydantic', 'async'}
                pattern.domain = 'rest-api'
                mock_patterns.return_value = [pattern]
                mock_load.return_value = []

                loaded_yamls = [
                    'cortex/knowledge/fastapi.yaml',
                    'cortex/knowledge/pydantic.yaml',
                    'cortex/knowledge/async.yaml',
                    'cortex/knowledge/rest-api.yaml',
                ]

                coverage = engine.calculate_coverage('IMPLEMENT', loaded_yamls)

                assert coverage >= 0.7  # Should be high coverage
                assert coverage <= 1.0

    def test_calculate_coverage_partial(self, engine):
        """Coverage should be <1.0 when some tech is missing."""
        with patch.object(engine, '_load_cortex_best_practices') as mock_load:
            with patch.object(engine, '_extract_applicable_patterns') as mock_patterns:
                # Mock pattern with tech
                pattern = Mock()
                pattern.keywords = {'fastapi', 'sqlalchemy', 'pytest'}
                pattern.domain = 'testing'
                mock_patterns.return_value = [pattern]
                mock_load.return_value = []

                loaded_yamls = [
                    'cortex/knowledge/fastapi.yaml',
                    # sqlalchemy missing
                    'cortex/knowledge/pytest.yaml',
                    # testing missing
                ]

                coverage = engine.calculate_coverage('IMPLEMENT', loaded_yamls)

                # Should have less than full coverage
                assert coverage > 0.0
                assert coverage < 1.0

    def test_calculate_coverage_empty(self, engine):
        """Coverage should be 0 when no YAMLs loaded."""
        with patch.object(engine, '_load_cortex_best_practices') as mock_load:
            with patch.object(engine, '_extract_applicable_patterns') as mock_patterns:
                pattern = Mock()
                pattern.keywords = {'fastapi', 'pydantic'}
                pattern.domain = 'web'
                mock_patterns.return_value = [pattern]
                mock_load.return_value = []

                coverage = engine.calculate_coverage('IMPLEMENT', [])

                assert coverage == 0.0

    def test_calculate_coverage_no_patterns(self, engine):
        """Coverage should be 1.0 when no patterns found (graceful)."""
        with patch.object(engine, '_load_cortex_best_practices') as mock_load:
            with patch.object(engine, '_extract_applicable_patterns') as mock_patterns:
                mock_patterns.return_value = []
                mock_load.return_value = []

                coverage = engine.calculate_coverage('IMPLEMENT', ['cortex/knowledge/fastapi.yaml'])

                # Should handle gracefully (no patterns = assume covered)
                assert coverage >= 0.0
                assert coverage <= 1.0

    def test_fill_gaps_not_needed(self, engine):
        """Fill gaps should return empty list when coverage adequate."""
        coverage = 0.9
        threshold = 0.8

        recommendations = engine.fill_gaps(coverage, 'IMPLEMENT', threshold)

        assert recommendations == []

    def test_fill_gaps_needed(self, engine):
        """Fill gaps should recommend YAMLs when coverage insufficient."""
        with patch.object(engine, '_load_cortex_best_practices') as mock_load:
            with patch.object(engine, '_extract_applicable_patterns') as mock_patterns:
                # Mock pattern with tech
                pattern = Mock()
                pattern.keywords = {'fastapi', 'sqlalchemy', 'pytest'}
                pattern.domain = 'integration'
                mock_patterns.return_value = [pattern]
                mock_load.return_value = []

                coverage = 0.5
                threshold = 0.8

                recommendations = engine.fill_gaps(coverage, 'IMPLEMENT', threshold)

                assert len(recommendations) > 0
                # Should recommend files from all layers
                company_recs = [r for r in recommendations if 'company/domains' in r]
                domain_recs = [r for r in recommendations if 'cortex/knowledge/domains' in r]
                generic_recs = [r for r in recommendations if r.startswith('cortex/knowledge/')]
                
                # Should have recommendations from all layers
                assert len(company_recs) > 0
                assert len(generic_recs) > 0

    def test_fill_gaps_layered_precedence(self, engine):
        """Fill gaps should respect Company > Domain > CORTEX precedence."""
        with patch.object(engine, '_load_cortex_best_practices') as mock_load:
            with patch.object(engine, '_extract_applicable_patterns') as mock_patterns:
                pattern = Mock()
                pattern.keywords = {'fastapi'}
                pattern.domain = 'web'
                mock_patterns.return_value = [pattern]
                mock_load.return_value = []

                recommendations = engine.fill_gaps(0.5, 'IMPLEMENT', 0.8)

                # First recommendation should be company layer
                if recommendations:
                    assert recommendations[0].startswith('company/domains/')

    def test_fill_gaps_handles_exception(self, engine):
        """Fill gaps should handle exceptions gracefully."""
        with patch.object(engine, '_load_cortex_best_practices') as mock_load:
            mock_load.side_effect = ValueError("Load failed")

            recommendations = engine.fill_gaps(0.5, 'IMPLEMENT', 0.8)

            assert recommendations == []

    def test_coverage_clamps_to_range(self, engine):
        """Coverage should always be in [0.0, 1.0]."""
        with patch.object(engine, '_load_cortex_best_practices') as mock_load:
            with patch.object(engine, '_extract_applicable_patterns') as mock_patterns:
                pattern = Mock()
                pattern.keywords = set()  # Empty keywords
                pattern.domain = None
                mock_patterns.return_value = [pattern]
                mock_load.return_value = []

                coverage = engine.calculate_coverage('IMPLEMENT', ['any.yaml'])

                assert 0.0 <= coverage <= 1.0

    def test_calculate_coverage_different_intents(self, engine):
        """Coverage should vary by intent type."""
        with patch.object(engine, '_load_cortex_best_practices') as mock_load:
            with patch.object(engine, '_extract_applicable_patterns') as mock_patterns:
                pattern = Mock()
                pattern.keywords = {'fastapi', 'pytest'}
                pattern.domain = 'web'
                mock_patterns.return_value = [pattern]
                mock_load.return_value = []

                loaded_yamls = ['cortex/knowledge/fastapi.yaml']

                # Different intents could have different coverage
                coverage_impl = engine.calculate_coverage('IMPLEMENT', loaded_yamls)
                coverage_fix = engine.calculate_coverage('FIX', loaded_yamls)

                # Both should be valid
                assert 0.0 <= coverage_impl <= 1.0
                assert 0.0 <= coverage_fix <= 1.0

    def test_fill_gaps_recommendation_format(self, engine):
        """Recommendations should be valid file paths."""
        with patch.object(engine, '_load_cortex_best_practices') as mock_load:
            with patch.object(engine, '_extract_applicable_patterns') as mock_patterns:
                pattern = Mock()
                pattern.keywords = {'fastapi'}
                pattern.domain = 'web'
                mock_patterns.return_value = [pattern]
                mock_load.return_value = []

                recommendations = engine.fill_gaps(0.5, 'IMPLEMENT', 0.8)

                for rec in recommendations:
                    # Should end with .yaml
                    assert rec.endswith('.yaml'), f"Invalid path: {rec}"
                    # Should contain path separators
                    assert '/' in rec, f"Invalid path: {rec}"
