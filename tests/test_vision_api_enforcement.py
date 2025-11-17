"""
Vision API Automatic Triggering Enforcement Tests

CRITICAL: These tests MUST pass to ensure Vision API automatically engages when images are attached.
Any failure indicates a regression that breaks automatic image detection.

Test Coverage:
1. Intent Router integration (automatic engagement)
2. Image detection across all supported sources
3. Context injection verification
4. Configuration enforcement
5. Edge cases and error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path


@pytest.mark.vision_critical
class TestVisionAPIAutoTrigger:
    """Tests that Vision API automatically triggers on image attachments."""
    
    @pytest.fixture
    def config(self):
        """Standard config with Vision API enabled."""
        return {
            'vision_api': {
                'enabled': True,
                'auto_detect_images': True,
                'auto_analyze_on_detect': True,
                'auto_inject_context': True,
                'max_images_per_request': 5,
                'supported_formats': ['png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp'],
                'max_tokens_per_image': 500,
                'cache_analysis_results': True
            }
        }
    
    @pytest.fixture
    def sample_data_uri(self):
        """Sample 1x1 PNG data URI for testing."""
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    
    def test_intent_router_has_vision_orchestrator(self, config):
        """CRITICAL: Intent Router must have VisionOrchestrator initialized."""
        from src.cortex_agents.intent_router import IntentRouter
        
        router = IntentRouter("test-router", config=config)
        
        assert hasattr(router, 'vision_orchestrator'), \
            "Intent Router MUST have vision_orchestrator attribute"
        assert router.vision_orchestrator is not None, \
            "VisionOrchestrator MUST be initialized in Intent Router"
    
    def test_vision_orchestrator_auto_processes_images(self, config, sample_data_uri):
        """CRITICAL: VisionOrchestrator must automatically process detected images."""
        from src.tier1.vision_orchestrator import VisionOrchestrator
        
        orchestrator = VisionOrchestrator(config)
        
        # Process request with image
        result = orchestrator.process_request(
            user_request=f"Analyze this: {sample_data_uri}",
            context_type='generic'
        )
        
        assert result['images_found'] is True, \
            "VisionOrchestrator MUST detect images in request"
        assert result['images_analyzed'] > 0, \
            "VisionOrchestrator MUST analyze detected images"
        assert len(result['detected_images']) > 0, \
            "VisionOrchestrator MUST return detected images list"
    
    def test_intent_router_processes_images_before_routing(self, config, sample_data_uri):
        """CRITICAL: Intent Router must process images BEFORE routing to agents."""
        from src.cortex_agents.intent_router import IntentRouter
        from src.cortex_agents.base_agent import AgentRequest
        
        router = IntentRouter("test-router", config=config)
        
        # Create request with image
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message=f"Help me understand this screenshot: {sample_data_uri}"
        )
        
        # Mock the vision orchestrator to track if it's called
        original_process = router.vision_orchestrator.process_request
        call_count = 0
        
        def mock_process(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return original_process(*args, **kwargs)
        
        router.vision_orchestrator.process_request = mock_process
        
        # Execute routing
        response = router.execute(request)
        
        assert call_count > 0, \
            "Intent Router MUST call vision_orchestrator.process_request when processing requests"
    
    def test_vision_results_injected_into_context(self, config, sample_data_uri):
        """CRITICAL: Vision analysis results must be injected into request context."""
        from src.cortex_agents.intent_router import IntentRouter
        from src.cortex_agents.base_agent import AgentRequest
        
        router = IntentRouter("test-router", config=config)
        
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message=f"Check this image: {sample_data_uri}"
        )
        
        # Execute - this should detect and analyze image
        router.execute(request)
        
        # Verify context was enriched
        assert request.context is not None, \
            "Request context MUST be created if images detected"
        assert 'vision_analysis' in request.context, \
            "Vision analysis results MUST be injected into request.context['vision_analysis']"
        
        vision_data = request.context['vision_analysis']
        assert vision_data['images_found'] is True, \
            "vision_analysis MUST indicate images were found"
    
    def test_data_uri_detection_triggers_vision(self, config, sample_data_uri):
        """ENFORCEMENT: Data URI images must trigger Vision API."""
        from src.tier1.image_detector import ImageDetector
        
        detector = ImageDetector(config)
        images = detector.detect(f"Analyze: {sample_data_uri}")
        
        assert len(images) > 0, \
            "Data URI images MUST be detected"
        assert images[0].source == 'data_uri', \
            "Source MUST be identified as data_uri"
        assert images[0].format == 'png', \
            "Format MUST be correctly identified"
    
    def test_copilot_attachment_triggers_vision(self, config):
        """ENFORCEMENT: GitHub Copilot Chat attachments must trigger Vision API."""
        from src.tier1.image_detector import ImageDetector
        
        detector = ImageDetector(config)
        
        attachments = [
            {
                'type': 'image',
                'mimeType': 'image/png',
                'data': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
                'name': 'screenshot.png'
            }
        ]
        
        images = detector.detect("Analyze this", attachments)
        
        assert len(images) > 0, \
            "Copilot attachments MUST be detected"
        assert images[0].source == 'copilot_attachment', \
            "Source MUST be identified as copilot_attachment"
    
    def test_multiple_image_formats_supported(self, config):
        """ENFORCEMENT: All documented formats must be supported."""
        from src.tier1.image_detector import ImageDetector
        
        detector = ImageDetector(config)
        supported = config['vision_api']['supported_formats']
        
        # Test each format
        for fmt in ['png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp']:
            assert fmt in supported, \
                f"Format {fmt} MUST be in supported_formats list"
            
            # Test detection for each format
            data_uri = f"data:image/{fmt};base64,iVBORw0KGgo="
            images = detector.detect(f"Test: {data_uri}")
            
            assert len(images) > 0, \
                f"Format {fmt} MUST be detected"
            assert images[0].format == fmt, \
                f"Format {fmt} MUST be correctly identified"
    
    def test_context_aware_prompt_selection(self, config, sample_data_uri):
        """ENFORCEMENT: Correct prompt must be selected based on context."""
        from src.tier1.vision_orchestrator import VisionOrchestrator
        
        orchestrator = VisionOrchestrator(config)
        
        # Test planning context
        result = orchestrator.process_request(
            user_request=f"plan this feature: {sample_data_uri}",
            context_type='planning'
        )
        assert result['images_found'], "Planning context must detect images"
        
        # Test debugging context
        result = orchestrator.process_request(
            user_request=f"debug this error: {sample_data_uri}",
            context_type='debugging'
        )
        assert result['images_found'], "Debugging context must detect images"
        
        # Test ADO context
        result = orchestrator.process_request(
            user_request=f"ado work item: {sample_data_uri}",
            context_type='ado'
        )
        assert result['images_found'], "ADO context must detect images"
    
    def test_disabled_config_prevents_detection(self):
        """ENFORCEMENT: When disabled, Vision API must NOT trigger."""
        config = {
            'vision_api': {
                'enabled': False,  # Disabled
                'auto_detect_images': False,
                'supported_formats': ['png']
            }
        }
        
        from src.tier1.image_detector import ImageDetector
        
        detector = ImageDetector(config)
        data_uri = "data:image/png;base64,iVBORw0KGgo="
        images = detector.detect(f"Test: {data_uri}")
        
        assert len(images) == 0, \
            "When disabled, NO images should be detected"
    
    def test_max_images_limit_enforced(self, config):
        """ENFORCEMENT: max_images_per_request limit must be enforced."""
        config['vision_api']['max_images_per_request'] = 2
        
        from src.tier1.image_detector import ImageDetector
        
        detector = ImageDetector(config)
        
        # Create request with 5 images
        data_uri = "data:image/png;base64,iVBORw0KGgo="
        request = " ".join([f"{data_uri}" for _ in range(5)])
        
        images = detector.detect(request)
        
        assert len(images) <= 2, \
            f"MUST respect max_images_per_request limit (got {len(images)}, expected ≤2)"
    
    def test_vision_error_does_not_block_routing(self, config, sample_data_uri):
        """ENFORCEMENT: Vision API errors must not block request routing."""
        from src.cortex_agents.intent_router import IntentRouter
        from src.cortex_agents.base_agent import AgentRequest
        
        router = IntentRouter("test-router", config=config)
        
        # Force vision orchestrator to fail
        def mock_fail(*args, **kwargs):
            raise Exception("Vision API unavailable")
        
        router.vision_orchestrator.process_request = mock_fail
        
        request = AgentRequest(
            intent="code",
            context={},
            user_message=f"Create a button: {sample_data_uri}"
        )
        
        # Should NOT raise exception - must continue routing
        response = router.execute(request)
        
        assert response.success, \
            "Routing MUST succeed even if Vision API fails"
    
    def test_quick_check_performance(self, config, sample_data_uri):
        """ENFORCEMENT: quick_check must be fast (< 100ms)."""
        import time
        from src.tier1.vision_orchestrator import VisionOrchestrator
        
        orchestrator = VisionOrchestrator(config)
        
        start = time.time()
        result = orchestrator.quick_check(f"Test: {sample_data_uri}")
        elapsed = (time.time() - start) * 1000  # Convert to ms
        
        assert result is True, \
            "quick_check MUST return True for requests with images"
        assert elapsed < 100, \
            f"quick_check MUST complete in <100ms (took {elapsed:.1f}ms)"
    
    def test_configuration_validation(self):
        """ENFORCEMENT: Config file must have all required Vision API settings."""
        import json
        
        config_path = Path("cortex.config.json")
        
        if not config_path.exists():
            pytest.skip("cortex.config.json not found")
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        assert 'vision_api' in config, \
            "Config MUST have vision_api section"
        
        vision = config['vision_api']
        required_keys = [
            'enabled',
            'auto_detect_images',
            'auto_analyze_on_detect',
            'auto_inject_context',
            'max_images_per_request',
            'supported_formats'
        ]
        
        for key in required_keys:
            assert key in vision, \
                f"Config MUST have vision_api.{key} setting"
        
        # Validate types
        assert isinstance(vision['enabled'], bool)
        assert isinstance(vision['auto_detect_images'], bool)
        assert isinstance(vision['auto_analyze_on_detect'], bool)
        assert isinstance(vision['auto_inject_context'], bool)
        assert isinstance(vision['max_images_per_request'], int)
        assert isinstance(vision['supported_formats'], list)
        assert len(vision['supported_formats']) > 0


@pytest.mark.vision_integration
class TestVisionAPIIntegrationFlow:
    """Integration tests for complete Vision API flow."""
    
    @pytest.fixture
    def full_config(self):
        """Full config for integration tests."""
        return {
            'vision_api': {
                'enabled': True,
                'auto_detect_images': True,
                'auto_analyze_on_detect': True,
                'auto_inject_context': True,
                'max_images_per_request': 5,
                'supported_formats': ['png', 'jpg', 'jpeg'],
                'max_tokens_per_image': 500,
                'cache_analysis_results': True
            }
        }
    
    def test_end_to_end_image_processing(self, full_config):
        """INTEGRATION: Complete flow from detection to analysis to injection."""
        from src.tier1.vision_orchestrator import VisionOrchestrator
        
        orchestrator = VisionOrchestrator(full_config)
        
        data_uri = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        result = orchestrator.process_request(
            user_request=f"Analyze this UI mockup: {data_uri}",
            context_type='planning'
        )
        
        # Verify complete flow
        assert result['images_found'] is True, "Step 1: Detection failed"
        assert result['images_analyzed'] > 0, "Step 2: Analysis failed"
        assert len(result['detected_images']) > 0, "Step 3: Image list empty"
        assert len(result['analysis_results']) > 0, "Step 4: No analysis results"
        assert result['context_summary'] != '', "Step 5: Context injection failed"
    
    def test_metrics_tracking(self, full_config):
        """INTEGRATION: Metrics must be tracked correctly."""
        from src.tier1.vision_orchestrator import VisionOrchestrator
        
        orchestrator = VisionOrchestrator(full_config)
        
        data_uri = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        # Process multiple requests
        for i in range(3):
            orchestrator.process_request(
                user_request=f"Request {i}: {data_uri}",
                context_type='generic'
            )
        
        metrics = orchestrator.get_metrics()
        
        assert metrics['total_requests'] >= 3, \
            "Metrics MUST track total requests"
        assert metrics['requests_with_images'] >= 3, \
            "Metrics MUST track requests with images"
        assert metrics['total_images_analyzed'] >= 3, \
            "Metrics MUST track images analyzed"


@pytest.mark.vision_regression
class TestVisionAPIRegression:
    """Regression tests to prevent breaking changes."""
    
    def test_import_stability(self):
        """REGRESSION: All Vision API imports must remain stable."""
        try:
            from src.tier1.image_detector import ImageDetector, ImageAttachment
            from src.tier1.vision_orchestrator import VisionOrchestrator
            from src.tier1.vision_api import VisionAPI
        except ImportError as e:
            pytest.fail(f"REGRESSION: Import failed - {e}")
    
    def test_interface_stability(self):
        """REGRESSION: Public interfaces must remain stable."""
        from src.tier1.image_detector import ImageDetector
        from src.tier1.vision_orchestrator import VisionOrchestrator
        
        config = {'vision_api': {'enabled': True, 'auto_detect_images': True}}
        
        # Check ImageDetector interface
        detector = ImageDetector(config)
        assert hasattr(detector, 'detect'), "ImageDetector.detect() removed"
        assert hasattr(detector, 'has_images'), "ImageDetector.has_images() removed"
        
        # Check VisionOrchestrator interface
        orchestrator = VisionOrchestrator(config)
        assert hasattr(orchestrator, 'process_request'), "VisionOrchestrator.process_request() removed"
        assert hasattr(orchestrator, 'quick_check'), "VisionOrchestrator.quick_check() removed"
        assert hasattr(orchestrator, 'get_metrics'), "VisionOrchestrator.get_metrics() removed"
    
    def test_config_backward_compatibility(self):
        """REGRESSION: Old configs with only 'enabled' must still work."""
        minimal_config = {
            'vision_api': {
                'enabled': True
            }
        }
        
        from src.tier1.vision_orchestrator import VisionOrchestrator
        
        # Should not crash with minimal config
        orchestrator = VisionOrchestrator(minimal_config)
        assert orchestrator.enabled is True


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
