"""
Test Suite for ImageContextMiddleware

RED phase: All tests should FAIL initially (TDD workflow)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from src.operations.utilities.image_context_middleware import ImageContextMiddleware, get_middleware


class TestImageDetection:
    """Test image detection in various contexts"""
    
    def test_detect_images_from_attachments(self):
        """Test detection of images from explicit attachments"""
        middleware = ImageContextMiddleware(config={'vision_api': {'enabled': False}})
        
        attachments = [
            {'type': 'image', 'data': 'base64data'},
            {'type': 'png', 'data': 'base64data'}
        ]
        
        result = middleware.detect_images_in_context(
            user_message="Look at these",
            attachments=attachments
        )
        
        assert result['has_images'] is True
        assert result['image_count'] == 2
        assert 'attachment' in result['image_sources']
        assert result['detection_time_ms'] < 50  # Should be fast
    
    def test_detect_images_from_context(self):
        """Test detection of images from context dictionary"""
        middleware = ImageContextMiddleware(config={'vision_api': {'enabled': False}})
        
        context = {
            'image_base64': 'base64data',
            'user': 'test'
        }
        
        result = middleware.detect_images_in_context(
            user_message="Analyze this",
            context=context
        )
        
        assert result['has_images'] is True
        assert result['image_count'] >= 1
        assert 'context' in result['image_sources']
    
    def test_detect_images_from_message_reference(self):
        """Test detection from message references (lower confidence)"""
        middleware = ImageContextMiddleware(config={'vision_api': {'enabled': False}})
        
        result = middleware.detect_images_in_context(
            user_message="Look at this screenshot I attached"
        )
        
        assert result['has_images'] is True
        assert result['image_count'] >= 1
        assert 'message_reference' in result['image_sources']
    
    def test_no_images_detected(self):
        """Test no false positives when no images present"""
        middleware = ImageContextMiddleware(config={'vision_api': {'enabled': False}})
        
        result = middleware.detect_images_in_context(
            user_message="Just a regular text message"
        )
        
        assert result['has_images'] is False
        assert result['image_count'] == 0
        assert len(result['image_sources']) == 0


class TestContextInference:
    """Test analysis context inference"""
    
    def test_infer_planning_context(self):
        """Test planning context detection"""
        middleware = ImageContextMiddleware(config={'vision_api': {'enabled': False}})
        
        messages = [
            "plan this feature",
            "implement this UI",
            "create component from design"
        ]
        
        for msg in messages:
            context = middleware.infer_analysis_context(msg)
            assert context == 'planning', f"Failed for: {msg}"
    
    def test_infer_debugging_context(self):
        """Test debugging context detection"""
        middleware = ImageContextMiddleware(config={'vision_api': {'enabled': False}})
        
        messages = [
            "error in screenshot",
            "bug shown here",
            "stack trace attached"
        ]
        
        for msg in messages:
            context = middleware.infer_analysis_context(msg)
            assert context == 'debugging', f"Failed for: {msg}"
    
    def test_infer_ado_context(self):
        """Test ADO context detection"""
        middleware = ImageContextMiddleware(config={'vision_api': {'enabled': False}})
        
        messages = [
            "analyze this ADO work item",
            "extract story details",
            "parse Azure DevOps task"
        ]
        
        for msg in messages:
            context = middleware.infer_analysis_context(msg)
            assert context == 'ado', f"Failed for: {msg}"
    
    def test_infer_generic_context(self):
        """Test generic context as fallback"""
        middleware = ImageContextMiddleware(config={'vision_api': {'enabled': False}})
        
        context = middleware.infer_analysis_context("what is this?")
        assert context == 'generic'


class TestAutoEngagement:
    """Test automatic Vision API engagement"""
    
    @patch('src.tier1.vision_orchestrator.VisionOrchestrator')
    def test_auto_engage_when_images_detected(self, mock_orchestrator_class):
        """Test Vision API auto-engages when images detected"""
        # Setup mock
        mock_orchestrator = Mock()
        mock_orchestrator.process_request.return_value = {
            'images_analyzed': 1,
            'context_summary': 'Test summary',
            'context_data': {},
            'errors': []
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        config = {
            'vision_api': {
                'enabled': True,
                'auto_engage_on_image': True
            }
        }
        
        middleware = ImageContextMiddleware(config=config)
        
        attachments = [{'type': 'image', 'data': 'base64'}]
        
        result = middleware.process_context(
            user_message="Analyze this",
            attachments=attachments
        )
        
        assert result['vision_engaged'] is True
        assert result['images_detected'] == 1
        assert result['images_analyzed'] == 1
        assert mock_orchestrator.process_request.called
    
    def test_no_auto_engage_when_disabled(self):
        """Test Vision API does not engage when disabled"""
        config = {
            'vision_api': {
                'enabled': False,
                'auto_engage_on_image': True
            }
        }
        
        middleware = ImageContextMiddleware(config=config)
        
        attachments = [{'type': 'image', 'data': 'base64'}]
        
        result = middleware.process_context(
            user_message="Analyze this",
            attachments=attachments
        )
        
        assert result['vision_engaged'] is False
        assert result['images_detected'] == 1
    
    @patch('src.tier1.vision_orchestrator.VisionOrchestrator')
    def test_force_engage_overrides_auto_engage(self, mock_orchestrator_class):
        """Test force_engage parameter overrides auto_engage setting"""
        mock_orchestrator = Mock()
        mock_orchestrator.process_request.return_value = {
            'images_analyzed': 1,
            'context_summary': 'Forced analysis',
            'context_data': {},
            'errors': []
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        config = {
            'vision_api': {
                'enabled': True,
                'auto_engage_on_image': False  # Disabled
            }
        }
        
        middleware = ImageContextMiddleware(config=config)
        
        attachments = [{'type': 'image', 'data': 'base64'}]
        
        result = middleware.process_context(
            user_message="Analyze this",
            attachments=attachments,
            force_engage=True  # Override
        )
        
        assert result['vision_engaged'] is True
        assert mock_orchestrator.process_request.called


class TestPerformanceRequirements:
    """Test performance requirements (<500ms)"""
    
    @patch('src.tier1.vision_orchestrator.VisionOrchestrator')
    def test_engagement_within_sla(self, mock_orchestrator_class):
        """Test engagement completes within 500ms SLA"""
        # Mock fast response
        mock_orchestrator = Mock()
        mock_orchestrator.process_request.return_value = {
            'images_analyzed': 1,
            'context_summary': 'Fast analysis',
            'context_data': {},
            'errors': []
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        config = {
            'vision_api': {
                'enabled': True,
                'auto_engage_on_image': True,
                'max_engagement_time_ms': 500
            }
        }
        
        middleware = ImageContextMiddleware(config=config)
        
        attachments = [{'type': 'image', 'data': 'base64'}]
        
        result = middleware.process_context(
            user_message="Quick analysis",
            attachments=attachments
        )
        
        assert result['within_sla'] is True
        assert result['engagement_time_ms'] < 500
    
    def test_detection_performance(self):
        """Test detection completes quickly (<50ms)"""
        middleware = ImageContextMiddleware(config={'vision_api': {'enabled': False}})
        
        attachments = [{'type': 'image', 'data': 'base64'} for _ in range(5)]
        
        start = time.perf_counter()
        result = middleware.detect_images_in_context(
            user_message="Multiple images",
            attachments=attachments
        )
        end = time.perf_counter()
        
        elapsed_ms = (end - start) * 1000
        
        assert elapsed_ms < 50  # Should be very fast
        assert result['detection_time_ms'] < 50


class TestMetrics:
    """Test metrics collection"""
    
    def test_metrics_tracking(self):
        """Test metrics are tracked correctly"""
        middleware = ImageContextMiddleware(config={'vision_api': {'enabled': False}})
        
        # Process some requests
        middleware.process_context("just text")  # No images - no image keywords
        middleware.process_context("image here", attachments=[{'type': 'image'}])  # Has image
        middleware.process_context("another", attachments=[{'type': 'png'}])  # Has image
        
        metrics = middleware.get_metrics()
        
        assert metrics['total_requests'] == 3
        assert metrics['requests_with_images'] == 2  # Only 2 had actual images
        assert metrics['enabled'] is False
    
    @patch('src.tier1.vision_orchestrator.VisionOrchestrator')
    def test_engagement_rate_metric(self, mock_orchestrator_class):
        """Test engagement rate calculation"""
        mock_orchestrator = Mock()
        mock_orchestrator.process_request.return_value = {
            'images_analyzed': 1,
            'context_summary': 'Analysis',
            'context_data': {},
            'errors': []
        }
        mock_orchestrator_class.return_value = mock_orchestrator
        
        config = {
            'vision_api': {
                'enabled': True,
                'auto_engage_on_image': True
            }
        }
        
        middleware = ImageContextMiddleware(config=config)
        
        # Process requests with images
        for _ in range(5):
            middleware.process_context(
                "image", attachments=[{'type': 'image', 'data': 'base64'}]
            )
        
        metrics = middleware.get_metrics()
        
        assert metrics['auto_engagements'] == 5
        assert metrics['engagement_rate'] == 100.0  # 5/5 = 100%


class TestErrorHandling:
    """Test error handling"""
    
    @patch('src.tier1.vision_orchestrator.VisionOrchestrator')
    def test_graceful_failure_on_vision_error(self, mock_orchestrator_class):
        """Test graceful handling when Vision API fails"""
        mock_orchestrator = Mock()
        mock_orchestrator.process_request.side_effect = Exception("Vision API error")
        mock_orchestrator_class.return_value = mock_orchestrator
        
        config = {
            'vision_api': {
                'enabled': True,
                'auto_engage_on_image': True
            }
        }
        
        middleware = ImageContextMiddleware(config=config)
        
        attachments = [{'type': 'image', 'data': 'base64'}]
        
        result = middleware.process_context(
            user_message="Analyze this",
            attachments=attachments
        )
        
        # Should not crash
        assert len(result['errors']) > 0
        assert 'Vision API error' in str(result['errors'])


class TestSingletonPattern:
    """Test global middleware instance"""
    
    def test_get_middleware_singleton(self):
        """Test get_middleware returns same instance"""
        instance1 = get_middleware()
        instance2 = get_middleware()
        
        assert instance1 is instance2  # Same object
