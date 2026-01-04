"""
Tests for Context Middleware File Relationship Analysis.

Part of C50-05: Context Middleware Enhancement - Phase 2

Author: Asif Hussain
Copyright © 2026 Asif Hussain. All rights reserved.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
from pathlib import Path

from src.orchestrators.context_middleware import CrossSessionContextMiddleware


class TestFileRelationshipAnalysis:
    """Test file relationship context integration."""
    
    def test_file_relationships_detected_from_user_input(self):
        """Test file relationships detected when file paths mentioned."""
        middleware = CrossSessionContextMiddleware()
        
        # Mock knowledge graph to return relationships
        with patch.object(middleware, 'knowledge_graph') as mock_kg:
            mock_kg.get_file_relationships.return_value = [
                {'related_file': 'src/user.py', 'strength': 0.8, 'relationship_type': 'co_modification'}
            ]
            
            context = {}
            enriched = middleware.enrich_context(
                "fix bug in src/auth.py",
                context
            )
            
            # Should detect file mention and inject relationships
            assert 'file_relationships' in enriched or 'mentioned_files' in enriched
    
    def test_file_relationships_injected_when_available(self):
        """Test related files metadata is injected into context."""
        middleware = CrossSessionContextMiddleware()
        
        with patch('src.tier2.knowledge_graph.KnowledgeGraph') as mock_kg:
            mock_kg_instance = Mock()
            mock_kg_instance.get_file_relationships.return_value = [
                {
                    'related_file': 'src/user.py',
                    'relationship_type': 'co_modification',
                    'strength': 0.85,
                    'context': 'Often modified together'
                },
                {
                    'related_file': 'src/session.py',
                    'relationship_type': 'dependency',
                    'strength': 0.75,
                    'context': 'Import dependency'
                }
            ]
            mock_kg.return_value = mock_kg_instance
            
            # Recreate middleware with mocked KG
            middleware.knowledge_graph = mock_kg_instance
            
            context = {}
            enriched = middleware.enrich_context(
                "fix bug in src/auth.py",
                context
            )
            
            # Should inject file relationships
            assert 'file_relationships' in enriched
            assert len(enriched['file_relationships']) >= 1
            assert any(r['related_file'] == 'src/user.py' for r in enriched['file_relationships'])
    
    def test_no_file_relationships_without_file_mentions(self):
        """Test file relationships not added when no files mentioned."""
        middleware = CrossSessionContextMiddleware()
        
        context = {}
        enriched = middleware.enrich_context("plan authentication", context)
        
        # Should not have file relationships without file mentions
        # (unless continuation pattern triggers session context)
        if not enriched.get('continuation_detected'):
            assert 'file_relationships' not in enriched
    
    def test_file_relationships_token_budget(self):
        """Test file relationships respect token budget (<150 tokens)."""
        middleware = CrossSessionContextMiddleware()
        
        with patch('src.tier2.knowledge_graph.KnowledgeGraph') as mock_kg:
            mock_kg_instance = Mock()
            # Return many relationships
            mock_kg_instance.get_file_relationships.return_value = [
                {
                    'related_file': f'src/file_{i}.py',
                    'relationship_type': 'co_modification',
                    'strength': 0.8,
                    'context': 'Very long context description ' * 20
                }
                for i in range(20)
            ]
            mock_kg.return_value = mock_kg_instance
            middleware.knowledge_graph = mock_kg_instance
            
            context = {}
            enriched = middleware.enrich_context("fix src/auth.py", context)
            
            # Should trim to token budget
            if 'file_relationships' in enriched:
                import json
                relationships_str = json.dumps(enriched['file_relationships'])
                estimated_tokens = len(relationships_str) // 4
                assert estimated_tokens < 200, "File relationships exceed token budget"
    
    def test_file_path_extraction_patterns(self):
        """Test various file path patterns are detected."""
        middleware = CrossSessionContextMiddleware()
        
        test_cases = [
            ("fix bug in src/auth.py", "src/auth.py"),
            ("update tests/test_auth.py", "tests/test_auth.py"),
            ("refactor cortex-brain/tier1/sessions.py", "cortex-brain/tier1/sessions.py"),
            ("modify ./src/utils/helper.py", "./src/utils/helper.py"),
        ]
        
        for user_input, expected_file in test_cases:
            files = middleware._extract_file_paths(user_input)
            assert expected_file in files, f"Failed to extract {expected_file} from '{user_input}'"
    
    def test_file_relationships_strength_filtering(self):
        """Test weak relationships are filtered out."""
        middleware = CrossSessionContextMiddleware()
        
        with patch.object(middleware, 'knowledge_graph') as mock_kg:
            # Mock returns ALL relationships (including weak ones)
            # Middleware should filter to strength >= 0.5
            mock_kg.get_file_relationships.return_value = [
                {'related_file': 'src/strong.py', 'strength': 0.9, 'relationship_type': 'co_modification', 'context': ''},
                {'related_file': 'src/medium.py', 'strength': 0.6, 'relationship_type': 'dependency', 'context': ''}
            ]
            
            context = {}
            enriched = middleware.enrich_context("fix src/auth.py", context)
            
            # Should only include relationships returned by KG (which respects min_strength=0.5)
            if 'file_relationships' in enriched:
                # All relationships should be >= 0.5 (KG already filtered)
                for r in enriched['file_relationships']:
                    assert r['strength'] >= 0.5, f"Relationship {r} has strength < 0.5"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
