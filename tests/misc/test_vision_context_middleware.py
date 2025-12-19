"""
Test suite for VisionContextMiddleware

Tests automatic vision API engagement when images are detected in context.
Validates image detection, GPT-4V integration, and caching mechanisms.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
"""

import pytest
import time
from unittest.mock import patch, MagicMock, Mock
from pathlib import Path


class TestVisionContextMiddlewareImageDetection:
    """Test suite for image detection in context"""
    
    def test_detect_images_in_context_png(self):
        """Test detection of PNG images in context"""
        from src.operations.utilities.vision_context_middleware import VisionContextMiddleware
        
        middleware = VisionContextMiddleware()
        
        context = {
            'attachments': [
                {'type': 'image', 'path': '/path/to/diagram.png', 'mime': 'image/png'},
                {'type': 'text', 'content': 'Some text'}
            ]
        }
        
        images = middleware.detect_images_in_context(context)
        
        assert len(images) == 1
        assert images[0]['path'] == '/path/to/diagram.png'
        assert images[0]['mime'] == 'image/png'
    
    def test_detect_images_in_context_multiple_formats(self):
        """Test detection of PNG, JPG, and JPEG images"""
        from src.operations.utilities.vision_context_middleware import VisionContextMiddleware
        
        middleware = VisionContextMiddleware()
        
        context = {
            'attachments': [
                {'type': 'image', 'path': '/img1.png', 'mime': 'image/png'},
                {'type': 'image', 'path': '/img2.jpg', 'mime': 'image/jpeg'},
                {'type': 'image', 'path': '/img3.jpeg', 'mime': 'image/jpeg'},
                {'type': 'pdf', 'path': '/doc.pdf', 'mime': 'application/pdf'}
            ]
        }
        
        images = middleware.detect_images_in_context(context)
        
        assert len(images) == 3
        assert all(img['mime'] in ['image/png', 'image/jpeg'] for img in images)
    
    def test_detect_images_no_images_returns_empty(self):
        """Test no images detected in text-only context"""
        from src.operations.utilities.vision_context_middleware import VisionContextMiddleware
        
        middleware = VisionContextMiddleware()
        
        context = {
            'attachments': [
                {'type': 'text', 'content': 'Text only'},
                {'type': 'pdf', 'path': '/doc.pdf'}
            ]
        }
        
        images = middleware.detect_images_in_context(context)
        
        assert len(images) == 0


class TestVisionContextMiddlewareAutoEngagement:
    """Test suite for automatic vision API engagement"""
    
    @patch('src.operations.utilities.vision_context_middleware.GPT4VisionClient')
    def test_auto_engagement_triggers_on_image(self, mock_vision_client):
        """Test that vision API is automatically called when images present"""
        from src.operations.utilities.vision_context_middleware import VisionContextMiddleware
        
        mock_client = MagicMock()
        mock_client.analyze_image.return_value = {
            'description': 'Test analysis',
            'objects': ['object1', 'object2']
        }
        mock_vision_client.return_value = mock_client
        
        middleware = VisionContextMiddleware()
        
        context = {
            'attachments': [
                {'type': 'image', 'path': '/diagram.png', 'mime': 'image/png'}
            ],
            'user_message': 'What is this diagram showing?'
        }
        
        result = middleware.process_context(context)
        
        # Should have triggered vision analysis
        assert mock_client.analyze_image.called
        assert result['vision_analysis'] is not None
        assert 'Test analysis' in str(result['vision_analysis'])
    
    @patch('src.operations.utilities.vision_context_middleware.GPT4VisionClient')
    def test_auto_engagement_performance_under_500ms(self, mock_vision_client):
        """Test that auto-engagement completes in <500ms"""
        from src.operations.utilities.vision_context_middleware import VisionContextMiddleware
        
        mock_client = MagicMock()
        mock_client.analyze_image.return_value = {'description': 'Fast analysis'}
        mock_vision_client.return_value = mock_client
        
        middleware = VisionContextMiddleware()
        
        context = {
            'attachments': [
                {'type': 'image', 'path': '/img.png', 'mime': 'image/png'}
            ]
        }
        
        start_time = time.time()
        middleware.process_context(context)
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Should complete in <500ms
        assert elapsed_ms < 500, f"Engagement took {elapsed_ms:.0f}ms, exceeds 500ms limit"


class TestVisionContextMiddlewareSkipLogic:
    """Test suite for skipping analysis when already exists"""
    
    @patch('src.operations.utilities.vision_context_middleware.GPT4VisionClient')
    def test_skip_if_analysis_exists_in_context(self, mock_vision_client):
        """Test that vision analysis is skipped if already in context"""
        from src.operations.utilities.vision_context_middleware import VisionContextMiddleware
        
        mock_client = MagicMock()
        mock_vision_client.return_value = mock_client
        
        middleware = VisionContextMiddleware()
        
        context = {
            'attachments': [
                {'type': 'image', 'path': '/img.png', 'mime': 'image/png'}
            ],
            'vision_analysis': {
                'description': 'Existing analysis',
                'timestamp': '2025-12-13T10:00:00'
            }
        }
        
        result = middleware.process_context(context)
        
        # Should NOT call analyze_image since analysis exists
        assert not mock_client.analyze_image.called
        assert result['vision_analysis']['description'] == 'Existing analysis'


class TestVisionContextMiddlewareLogging:
    """Test suite for API call logging"""
    
    @patch('src.operations.utilities.vision_context_middleware.GPT4VisionClient')
    @patch('src.operations.utilities.vision_context_middleware.logger')
    def test_logs_api_call_info(self, mock_logger, mock_vision_client):
        """Test that vision API calls are logged for tracking"""
        from src.operations.utilities.vision_context_middleware import VisionContextMiddleware
        
        mock_client = MagicMock()
        mock_client.analyze_image.return_value = {'description': 'Test'}
        mock_vision_client.return_value = mock_client
        
        middleware = VisionContextMiddleware()
        
        context = {
            'attachments': [
                {'type': 'image', 'path': '/img.png', 'mime': 'image/png'}
            ]
        }
        
        middleware.process_context(context)
        
        # Should log the vision API engagement
        assert mock_logger.info.called
        log_message = str(mock_logger.info.call_args)
        assert 'vision' in log_message.lower() or 'image' in log_message.lower()


class TestVisionContextMiddlewareIntegration:
    """Test suite for orchestrator integration"""
    
    def test_middleware_decorator_available(self):
        """Test that @with_vision_context_middleware decorator exists"""
        from src.operations.utilities.vision_context_middleware import with_vision_context_middleware
        
        # Decorator should be importable
        assert callable(with_vision_context_middleware)
        
        # Test decorator on dummy function
        @with_vision_context_middleware
        def dummy_orchestrator(context):
            return context
        
        # Decorated function should be callable
        result = dummy_orchestrator({'test': 'data'})
        assert result is not None
    
    @patch('src.operations.utilities.vision_context_middleware.GPT4VisionClient')
    def test_decorator_auto_analyzes_images(self, mock_vision_client):
        """Test that decorator automatically analyzes images in context"""
        from src.operations.utilities.vision_context_middleware import with_vision_context_middleware
        
        mock_client = MagicMock()
        mock_client.analyze_image.return_value = {'description': 'Auto-analyzed'}
        mock_vision_client.return_value = mock_client
        
        @with_vision_context_middleware
        def test_orchestrator(context):
            return context
        
        context = {
            'attachments': [
                {'type': 'image', 'path': '/img.png', 'mime': 'image/png'}
            ]
        }
        
        result = test_orchestrator(context)
        
        # Should have vision_analysis added by decorator
        assert 'vision_analysis' in result
        assert mock_client.analyze_image.called


class TestVisionContextMiddlewareCaching:
    """Test suite for duplicate image caching"""
    
    @patch('src.operations.utilities.vision_context_middleware.GPT4VisionClient')
    def test_caching_duplicate_images(self, mock_vision_client):
        """Test that duplicate images use cached analysis"""
        from src.operations.utilities.vision_context_middleware import VisionContextMiddleware
        
        mock_client = MagicMock()
        mock_client.analyze_image.return_value = {'description': 'Cached analysis'}
        mock_vision_client.return_value = mock_client
        
        middleware = VisionContextMiddleware()
        
        # First call - should analyze
        context1 = {
            'attachments': [
                {'type': 'image', 'path': '/same_img.png', 'mime': 'image/png'}
            ]
        }
        
        result1 = middleware.process_context(context1)
        first_call_count = mock_client.analyze_image.call_count
        
        # Second call with same image - should use cache
        context2 = {
            'attachments': [
                {'type': 'image', 'path': '/same_img.png', 'mime': 'image/png'}
            ]
        }
        
        result2 = middleware.process_context(context2)
        second_call_count = mock_client.analyze_image.call_count
        
        # Should NOT have called API again
        assert second_call_count == first_call_count, "Cache not working - API called twice for same image"
        assert result2['vision_analysis']['description'] == 'Cached analysis'
