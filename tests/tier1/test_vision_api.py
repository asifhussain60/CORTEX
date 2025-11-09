"""
Tests for Vision API Integration

Validates image preprocessing, token estimation, budget enforcement,
and caching mechanisms.
"""

import pytest
import base64
from datetime import datetime, timedelta
from src.tier1.vision_api import VisionAPI


class TestVisionAPIBasics:
    """Test basic Vision API functionality."""
    
    def test_vision_api_initialization(self):
        """Test Vision API initialization with config."""
        config = {
            'vision_api': {
                'enabled': True,
                'max_tokens_per_image': 500,
                'max_image_size_bytes': 2000000
            }
        }
        
        vision = VisionAPI(config)
        
        assert vision.enabled is True
        assert vision.max_tokens == 500
        assert vision.max_image_size == 2000000
    
    def test_vision_api_disabled_by_default(self):
        """Test Vision API is disabled without config."""
        vision = VisionAPI({})
        
        assert vision.enabled is False
    
    def test_analyze_image_when_disabled(self):
        """Test error response when Vision API disabled."""
        vision = VisionAPI({'vision_api': {'enabled': False}})
        
        result = vision.analyze_image(
            image_data="data:image/png;base64,abc123",
            prompt="Analyze this"
        )
        
        assert result['success'] is False
        assert 'disabled' in result['error'].lower()


class TestImageValidation:
    """Test image data validation."""
    
    def test_validate_valid_png(self):
        """Test validation of valid PNG data URI."""
        vision = VisionAPI({'vision_api': {'enabled': True}})
        
        valid_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        assert vision._validate_image_data(valid_data) is True
    
    def test_validate_valid_jpeg(self):
        """Test validation of valid JPEG data URI."""
        vision = VisionAPI({'vision_api': {'enabled': True}})
        
        valid_data = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwA/AAAA/9k="
        
        assert vision._validate_image_data(valid_data) is True
    
    def test_validate_invalid_format(self):
        """Test rejection of invalid format."""
        vision = VisionAPI({'vision_api': {'enabled': True}})
        
        assert vision._validate_image_data("not a data uri") is False
        assert vision._validate_image_data("data:text/plain;base64,abc") is False
        assert vision._validate_image_data("") is False
        assert vision._validate_image_data(None) is False


class TestTokenEstimation:
    """Test token cost estimation."""
    
    def test_estimate_tokens_for_small_image(self):
        """Test token estimation for small image."""
        vision = VisionAPI({'vision_api': {'enabled': True}})
        
        # 1x1 pixel image (smallest possible)
        small_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        estimated = vision._estimate_tokens(small_image)
        
        assert estimated > 0
        assert estimated < 200  # Small image should be <200 tokens
    
    def test_estimate_tokens_without_pil(self):
        """Test token estimation fallback without PIL."""
        vision = VisionAPI({'vision_api': {'enabled': True}})
        
        # Should still provide an estimate
        image_data = "data:image/png;base64,abc123"
        estimated = vision._estimate_tokens(image_data)
        
        assert estimated > 0
        assert isinstance(estimated, int)


class TestBudgetEnforcement:
    """Test token budget enforcement."""
    
    def test_reject_image_exceeding_budget(self):
        """Test rejection of image exceeding token budget."""
        config = {
            'vision_api': {
                'enabled': True,
                'max_tokens_per_image': 100  # Very low limit for testing
            }
        }
        
        vision = VisionAPI(config)
        
        # Use a larger base64 string to trigger budget limit
        large_image = "data:image/png;base64," + ("A" * 10000)
        
        result = vision.analyze_image(large_image, "Analyze this")
        
        assert result['success'] is False
        assert 'too large' in result['error'].lower()
        assert 'estimated_tokens' in result
    
    def test_accept_image_within_budget(self):
        """Test acceptance of image within budget."""
        config = {
            'vision_api': {
                'enabled': True,
                'max_tokens_per_image': 500
            }
        }
        
        vision = VisionAPI(config)
        
        # Small image should pass
        small_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        result = vision.analyze_image(small_image, "Analyze colors")
        
        # Should succeed (mock implementation)
        assert result['success'] is True


class TestCaching:
    """Test result caching mechanism."""
    
    def test_cache_analysis_result(self):
        """Test caching of successful analysis."""
        config = {
            'vision_api': {
                'enabled': True,
                'cache_analysis_results': True
            }
        }
        
        vision = VisionAPI(config)
        
        image_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        prompt = "Analyze this button"
        
        # First call
        result1 = vision.analyze_image(image_data, prompt)
        assert result1['success'] is True
        assert result1['cached'] is False
        assert result1['tokens_used'] > 0
        
        # Second call should be cached
        result2 = vision.analyze_image(image_data, prompt)
        assert result2['success'] is True
        assert result2['cached'] is True
        assert result2['tokens_used'] == 0  # No tokens used for cache hit
    
    def test_cache_expiration(self):
        """Test cache TTL expiration."""
        config = {
            'vision_api': {
                'enabled': True,
                'cache_analysis_results': True,
                'cache_ttl_hours': 0.0001  # Very short TTL for testing
            }
        }
        
        vision = VisionAPI(config)
        
        image_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        # First call
        result1 = vision.analyze_image(image_data, "Test")
        assert result1['cached'] is False
        
        # Manually expire cache
        import time
        time.sleep(0.5)
        
        # Force cache check - should be expired
        cache_key = vision._get_cache_key(image_data, "Test")
        cached_result = vision._get_cached_result(cache_key)
        assert cached_result is None
    
    def test_cache_disabled(self):
        """Test behavior when caching disabled."""
        config = {
            'vision_api': {
                'enabled': True,
                'cache_analysis_results': False
            }
        }
        
        vision = VisionAPI(config)
        
        image_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        # Both calls should process (not cached)
        result1 = vision.analyze_image(image_data, "Test")
        result2 = vision.analyze_image(image_data, "Test")
        
        assert result1['cached'] is False
        assert result2['cached'] is False


class TestMetrics:
    """Test metrics collection."""
    
    def test_metrics_collection(self):
        """Test Vision API metrics tracking."""
        config = {'vision_api': {'enabled': True}}
        vision = VisionAPI(config)
        
        image_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        # Make some requests
        vision.analyze_image(image_data, "Test 1")
        vision.analyze_image(image_data, "Test 2")  # Should be cached
        
        metrics = vision.get_metrics()
        
        assert metrics['total_requests'] >= 1
        assert metrics['cache_hits'] >= 1
        assert metrics['total_tokens_used'] > 0
        assert 'cache_hit_rate_percent' in metrics
        assert 'estimated_cost_usd' in metrics
    
    def test_cache_hit_rate_calculation(self):
        """Test cache hit rate calculation."""
        config = {'vision_api': {'enabled': True}}
        vision = VisionAPI(config)
        
        image_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        # First call (miss)
        vision.analyze_image(image_data, "Test")
        
        # Second call (hit)
        vision.analyze_image(image_data, "Test")
        
        metrics = vision.get_metrics()
        
        # 1 request + 1 cache hit = 50% cache hit rate
        assert metrics['cache_hit_rate_percent'] == 50.0


class TestIntegration:
    """Test end-to-end integration scenarios."""
    
    def test_full_analysis_workflow(self):
        """Test complete analysis workflow."""
        config = {
            'vision_api': {
                'enabled': True,
                'max_tokens_per_image': 500,
                'cache_analysis_results': True
            }
        }
        
        vision = VisionAPI(config)
        
        # Analyze image
        image_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        prompt = "Extract button colors and labels"
        
        result = vision.analyze_image(image_data, prompt)
        
        # Verify result structure
        assert result['success'] is True
        assert 'analysis' in result
        assert 'extracted_data' in result
        assert 'tokens_used' in result
        assert 'processing_time_ms' in result
        assert isinstance(result['tokens_used'], int)
        assert result['tokens_used'] > 0
    
    def test_error_recovery(self):
        """Test graceful error handling."""
        config = {'vision_api': {'enabled': True}}
        vision = VisionAPI(config)
        
        # Invalid image data
        result = vision.analyze_image("invalid", "Test")
        
        assert result['success'] is False
        assert 'error' in result
        assert result['tokens_used'] == 0
