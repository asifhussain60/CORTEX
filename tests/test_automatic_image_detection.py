"""
Test automatic image detection and Vision API integration.

Tests:
1. Image detection from various sources
2. Vision orchestrator coordination
3. Intent router integration
4. Configuration settings
"""

import pytest
import json
from pathlib import Path


def test_image_detector_import():
    """Test that ImageDetector can be imported."""
    try:
        from src.tier1.image_detector import ImageDetector, ImageAttachment
        assert ImageDetector is not None
        assert ImageAttachment is not None
    except ImportError as e:
        pytest.fail(f"Failed to import ImageDetector: {e}")


def test_vision_orchestrator_import():
    """Test that VisionOrchestrator can be imported."""
    try:
        from src.tier1.vision_orchestrator import VisionOrchestrator
        assert VisionOrchestrator is not None
    except ImportError as e:
        pytest.fail(f"Failed to import VisionOrchestrator: {e}")


def test_image_detector_initialization():
    """Test ImageDetector initialization with config."""
    from src.tier1.image_detector import ImageDetector
    
    config = {
        'vision_api': {
            'auto_detect_images': True,
            'max_images_per_request': 5,
            'supported_formats': ['png', 'jpg', 'jpeg']
        }
    }
    
    detector = ImageDetector(config)
    assert detector.auto_detect is True
    assert detector.max_images == 5
    assert 'png' in detector.supported_formats


def test_vision_orchestrator_initialization():
    """Test VisionOrchestrator initialization."""
    from src.tier1.vision_orchestrator import VisionOrchestrator
    
    config = {
        'vision_api': {
            'enabled': True,
            'auto_detect_images': True,
            'auto_analyze_on_detect': True
        }
    }
    
    orchestrator = VisionOrchestrator(config)
    assert orchestrator.enabled is True
    assert orchestrator.auto_detect is True
    assert orchestrator.auto_analyze is True


def test_data_uri_detection():
    """Test detection of data URI images."""
    from src.tier1.image_detector import ImageDetector
    
    config = {
        'vision_api': {
            'auto_detect_images': True,
            'max_images_per_request': 5,
            'supported_formats': ['png', 'jpg', 'jpeg']
        }
    }
    
    detector = ImageDetector(config)
    
    # Sample data URI
    data_uri = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    
    request = f"Analyze this image: {data_uri}"
    
    images = detector.detect(request)
    
    assert len(images) == 1
    assert images[0].source == 'data_uri'
    assert images[0].format == 'png'


def test_quick_check():
    """Test quick image detection check."""
    from src.tier1.image_detector import ImageDetector
    
    config = {
        'vision_api': {
            'auto_detect_images': True,
            'max_images_per_request': 5,
            'supported_formats': ['png', 'jpg', 'jpeg']
        }
    }
    
    detector = ImageDetector(config)
    
    # Request with image
    data_uri = "data:image/png;base64,iVBORw0KGgo="
    request_with_image = f"Check this: {data_uri}"
    
    # Request without image
    request_without_image = "Just a text request"
    
    assert detector.has_images(request_with_image) is True
    assert detector.has_images(request_without_image) is False


def test_copilot_attachment_detection():
    """Test detection of GitHub Copilot Chat attachments."""
    from src.tier1.image_detector import ImageDetector
    
    config = {
        'vision_api': {
            'auto_detect_images': True,
            'max_images_per_request': 5,
            'supported_formats': ['png', 'jpg', 'jpeg']
        }
    }
    
    detector = ImageDetector(config)
    
    # Simulate Copilot attachment
    attachments = [
        {
            'type': 'image',
            'mimeType': 'image/png',
            'data': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
            'name': 'screenshot.png',
            'size': 1024
        }
    ]
    
    images = detector.detect("Analyze this", attachments)
    
    assert len(images) == 1
    assert images[0].source == 'copilot_attachment'
    assert images[0].format == 'png'
    assert images[0].size_bytes == 1024


def test_max_images_limit():
    """Test that max_images_per_request is enforced."""
    from src.tier1.image_detector import ImageDetector
    
    config = {
        'vision_api': {
            'auto_detect_images': True,
            'max_images_per_request': 2,
            'supported_formats': ['png']
        }
    }
    
    detector = ImageDetector(config)
    
    # Create request with 3 images
    data_uri = "data:image/png;base64,iVBORw0KGgo="
    request = f"{data_uri} and {data_uri} and {data_uri}"
    
    images = detector.detect(request)
    
    # Should only detect 2 (max limit)
    assert len(images) == 2


def test_vision_orchestrator_quick_check():
    """Test VisionOrchestrator quick check method."""
    from src.tier1.vision_orchestrator import VisionOrchestrator
    
    config = {
        'vision_api': {
            'enabled': True,
            'auto_detect_images': True,
            'auto_analyze_on_detect': True,
            'supported_formats': ['png']
        }
    }
    
    orchestrator = VisionOrchestrator(config)
    
    data_uri = "data:image/png;base64,iVBORw0KGgo="
    request_with_image = f"Analyze: {data_uri}"
    request_without_image = "Just text"
    
    assert orchestrator.quick_check(request_with_image) is True
    assert orchestrator.quick_check(request_without_image) is False


def test_config_validation():
    """Test that config is properly loaded and validated."""
    config_path = Path("cortex.config.json")
    
    if not config_path.exists():
        pytest.skip("cortex.config.json not found")
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Check vision_api section exists
    assert 'vision_api' in config
    
    # Check new auto-detection settings
    vision_config = config['vision_api']
    assert 'auto_detect_images' in vision_config
    assert 'auto_analyze_on_detect' in vision_config
    assert 'auto_inject_context' in vision_config
    assert 'max_images_per_request' in vision_config
    assert 'supported_formats' in vision_config
    
    # Check types
    assert isinstance(vision_config['auto_detect_images'], bool)
    assert isinstance(vision_config['max_images_per_request'], int)
    assert isinstance(vision_config['supported_formats'], list)


def test_context_aware_prompts():
    """Test that orchestrator selects correct prompts based on context."""
    from src.tier1.vision_orchestrator import VisionOrchestrator
    
    config = {
        'vision_api': {
            'enabled': True,
            'auto_detect_images': True,
            'auto_analyze_on_detect': True
        }
    }
    
    orchestrator = VisionOrchestrator(config)
    
    # Check default prompts exist
    assert 'generic' in orchestrator.default_prompts
    assert 'planning' in orchestrator.default_prompts
    assert 'debugging' in orchestrator.default_prompts
    assert 'ado' in orchestrator.default_prompts
    
    # Check prompts are different
    assert orchestrator.default_prompts['planning'] != orchestrator.default_prompts['debugging']


def test_disabled_auto_detection():
    """Test that detection is disabled when config says so."""
    from src.tier1.image_detector import ImageDetector
    
    config = {
        'vision_api': {
            'auto_detect_images': False,
            'max_images_per_request': 5,
            'supported_formats': ['png']
        }
    }
    
    detector = ImageDetector(config)
    
    data_uri = "data:image/png;base64,iVBORw0KGgo="
    request = f"Analyze: {data_uri}"
    
    images = detector.detect(request)
    
    # Should return empty list when disabled
    assert len(images) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
