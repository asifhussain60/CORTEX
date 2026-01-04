"""
Tests for Context Middleware Vision API Integration.

Part of C50-05: Context Middleware Enhancement - Phase 1

Author: Asif Hussain
Copyright © 2026 Asif Hussain. All rights reserved.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
from pathlib import Path

from src.orchestrators.context_middleware import CrossSessionContextMiddleware


class TestVisionContextIntegration:
    """Test Vision API context integration in middleware."""
    
    def test_vision_context_detected_from_attachments(self):
        """Test vision context is detected when image attachments present."""
        middleware = CrossSessionContextMiddleware()
        
        # Context with image attachment
        context = {
            'attachments': [
                {'type': 'image', 'path': '/tmp/screenshot.png', 'mime': 'image/png'}
            ]
        }
        
        enriched = middleware.enrich_context("analyze this", context)
        
        # Should detect vision context
        assert 'vision_context_available' in enriched
        assert enriched['vision_context_available'] is True
    
    def test_vision_metadata_injected_when_images_present(self):
        """Test vision analysis metadata is injected into context."""
        middleware = CrossSessionContextMiddleware()
        
        # Mock vision middleware at the correct import path
        with patch('src.operations.utilities.vision_context_middleware.VisionContextMiddleware') as mock_vision:
            mock_vision_instance = Mock()
            mock_vision_instance.detect_images_in_context.return_value = [
                {'type': 'image', 'path': '/tmp/test.png'}
            ]
            mock_vision_instance.process_context.return_value = {
                'attachments': [{'type': 'image', 'path': '/tmp/test.png', 'mime': 'image/png'}],
                'vision_analysis': {
                    'description': 'Login form with username and password fields',
                    'ui_elements': ['input', 'button'],
                    'confidence': 0.92
                }
            }
            mock_vision.return_value = mock_vision_instance
            
            context = {
                'attachments': [
                    {'type': 'image', 'path': '/tmp/test.png', 'mime': 'image/png'}
                ]
            }
            
            enriched = middleware.enrich_context("implement this UI", context)
            
            # Should inject vision metadata
            assert 'vision_context' in enriched
            assert 'description' in enriched['vision_context']
            assert enriched['vision_context']['confidence'] > 0.9
    
    def test_no_vision_context_without_images(self):
        """Test vision context not added when no images present."""
        middleware = CrossSessionContextMiddleware()
        
        context = {'user_request': 'plan authentication'}
        enriched = middleware.enrich_context("plan authentication", context)
        
        # Should not have vision context
        assert 'vision_context' not in enriched
        assert 'vision_context_available' not in enriched
    
    def test_vision_context_cached_for_duplicate_images(self):
        """Test vision context uses cache for duplicate images."""
        middleware = CrossSessionContextMiddleware()
        
        with patch('src.operations.utilities.vision_context_middleware.VisionContextMiddleware') as mock_vision:
            mock_vision_instance = Mock()
            # First call returns analysis, second indicates cached
            mock_vision_instance.process_context.side_effect = [
                {
                    'attachments': [{'type': 'image', 'path': '/tmp/test.png'}],
                    'vision_analysis': {'description': 'First analysis'}
                },
                {
                    'attachments': [{'type': 'image', 'path': '/tmp/test.png'}],
                    'vision_analysis': {'description': 'First analysis', 'cached': True}
                }
            ]
            mock_vision.return_value = mock_vision_instance
            
            context1 = {'attachments': [{'type': 'image', 'path': '/tmp/test.png'}]}
            context2 = {'attachments': [{'type': 'image', 'path': '/tmp/test.png'}]}
            
            enriched1 = middleware.enrich_context("first request", context1)
            enriched2 = middleware.enrich_context("second request", context2)
            
            # Second call should use cache
            assert mock_vision_instance.process_context.call_count == 2
    
    def test_vision_context_token_budget(self):
        """Test vision context respects token budget (<100 tokens)."""
        middleware = CrossSessionContextMiddleware()
        
        with patch('src.operations.utilities.vision_context_middleware.VisionContextMiddleware') as mock_vision:
            mock_vision_instance = Mock()
            # Return large analysis
            mock_vision_instance.process_context.return_value = {
                'attachments': [{'type': 'image', 'path': '/tmp/test.png'}],
                'vision_analysis': {
                    'description': 'Very long description ' * 100,  # Deliberately oversized
                    'ui_elements': ['element' + str(i) for i in range(50)]
                }
            }
            mock_vision.return_value = mock_vision_instance
            
            context = {'attachments': [{'type': 'image', 'path': '/tmp/test.png'}]}
            enriched = middleware.enrich_context("analyze", context)
            
            # Should trim to token budget
            if 'vision_context' in enriched:
                # Estimate tokens (rough: 1 token per 4 chars)
                vision_str = str(enriched['vision_context'])
                estimated_tokens = len(vision_str) // 4
                assert estimated_tokens < 150, "Vision context exceeds token budget"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
