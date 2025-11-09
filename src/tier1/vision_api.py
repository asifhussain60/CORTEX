"""
Vision API Integration for CORTEX

Provides image analysis capabilities using GitHub Copilot's built-in vision API.
Includes token budgeting, image preprocessing, and result caching.

Design Document: cortex-brain/cortex-2.0-design/31-vision-api-integration.md
"""

import base64
import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from pathlib import Path
import re

try:
    from PIL import Image
    import io
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class VisionAPI:
    """
    GitHub Copilot Vision API integration with token management.
    
    Features:
    - Image preprocessing (downscale, compress)
    - Token cost estimation
    - Budget enforcement (500 token hard limit)
    - Result caching (24 hour TTL)
    - Graceful fallback on errors
    
    Example:
        vision = VisionAPI(config)
        result = vision.analyze_image(
            image_data="data:image/png;base64,...",
            prompt="Extract button colors and labels"
        )
        
        if result['success']:
            print(f"Analysis: {result['analysis']}")
            print(f"Tokens used: {result['tokens_used']}")
    """
    
    def __init__(self, config: Dict):
        """
        Initialize Vision API.
        
        Args:
            config: Configuration dictionary with vision_api settings
        """
        self.logger = logging.getLogger(__name__)
        
        # Feature flag
        self.enabled = config.get('vision_api', {}).get('enabled', False)
        
        # Token budgets
        self.max_tokens = config.get('vision_api', {}).get('max_tokens_per_image', 500)
        self.warn_threshold = config.get('vision_api', {}).get('warn_threshold_tokens', 400)
        
        # Image preprocessing
        self.max_image_size = config.get('vision_api', {}).get('max_image_size_bytes', 2_000_000)
        self.downscale_threshold = config.get('vision_api', {}).get('downscale_threshold', 1920)
        self.jpeg_quality = config.get('vision_api', {}).get('jpeg_quality', 85)
        
        # Caching
        self.cache_enabled = config.get('vision_api', {}).get('cache_analysis_results', True)
        self.cache_ttl_hours = config.get('vision_api', {}).get('cache_ttl_hours', 24)
        self.cache = {}  # Simple in-memory cache {hash: {result, timestamp}}
        
        # Metrics
        self.total_requests = 0
        self.total_tokens_used = 0
        self.cache_hits = 0
        
        if not PIL_AVAILABLE and self.enabled:
            self.logger.warning(
                "PIL/Pillow not available. Image preprocessing disabled. "
                "Install with: pip install Pillow"
            )
    
    def analyze_image(self, image_data: str, prompt: str) -> Dict:
        """
        Analyze image using GitHub Copilot vision API.
        
        Args:
            image_data: Base64-encoded image (data URI format)
            prompt: Natural language analysis request
            
        Returns:
            {
                'success': bool,
                'analysis': str,           # Natural language response
                'extracted_data': dict,    # Structured data
                'tokens_used': int,
                'processing_time_ms': int,
                'cached': bool,
                'error': str (if failed)
            }
        """
        start_time = datetime.now()
        
        try:
            # Check if enabled
            if not self.enabled:
                return self._error_response(
                    "Vision API disabled. Set vision_api.enabled=true in config.",
                    start_time
                )
            
            # Validate image data
            if not self._validate_image_data(image_data):
                return self._error_response(
                    "Invalid image data format. Expected data URI (data:image/...).",
                    start_time
                )
            
            # Check cache
            cache_key = self._get_cache_key(image_data, prompt)
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                self.cache_hits += 1
                self.logger.info(f"Vision API cache hit (key: {cache_key[:16]}...)")
                return {
                    **cached_result,
                    'cached': True,
                    'tokens_used': 0,  # No tokens used for cache hit
                    'processing_time_ms': (datetime.now() - start_time).total_seconds() * 1000
                }
            
            # Preprocess image
            processed_image, preprocessing_info = self._preprocess_image(image_data)
            
            # Estimate token cost
            estimated_tokens = self._estimate_tokens(processed_image)
            
            # Enforce budget
            if estimated_tokens > self.max_tokens:
                return self._error_response(
                    f"Image too large: estimated {estimated_tokens} tokens "
                    f"(limit: {self.max_tokens}). Try a smaller image or lower resolution.",
                    start_time,
                    estimated_tokens=estimated_tokens
                )
            
            # Warn if approaching limit
            if estimated_tokens > self.warn_threshold:
                self.logger.warning(
                    f"Vision API token warning: {estimated_tokens} tokens "
                    f"(threshold: {self.warn_threshold})"
                )
            
            # Call vision API
            result = self._call_vision_api(processed_image, prompt)
            
            if not result['success']:
                return result
            
            # Update metrics
            self.total_requests += 1
            self.total_tokens_used += result['tokens_used']
            
            # Cache result
            if self.cache_enabled:
                self._cache_result(cache_key, result)
            
            # Add metadata
            result['preprocessing'] = preprocessing_info
            result['estimated_tokens'] = estimated_tokens
            result['processing_time_ms'] = (datetime.now() - start_time).total_seconds() * 1000
            result['cached'] = False
            
            return result
            
        except Exception as e:
            self.logger.error(f"Vision API error: {e}", exc_info=True)
            return self._error_response(str(e), start_time)
    
    def _validate_image_data(self, image_data: str) -> bool:
        """Validate image data format."""
        if not image_data or not isinstance(image_data, str):
            return False
        
        # Check data URI format
        if not image_data.startswith('data:image/'):
            return False
        
        # Check supported formats
        supported = ['png', 'jpeg', 'jpg', 'webp']
        for fmt in supported:
            if f'image/{fmt}' in image_data.lower():
                return True
        
        return False
    
    def _preprocess_image(self, image_data: str) -> Tuple[str, Dict]:
        """
        Preprocess image to reduce token cost.
        
        Returns:
            (processed_image_data, preprocessing_info)
        """
        if not PIL_AVAILABLE:
            return image_data, {'preprocessed': False, 'reason': 'PIL not available'}
        
        try:
            # Extract base64 data
            base64_match = re.search(r'base64,(.+)', image_data)
            if not base64_match:
                return image_data, {'preprocessed': False, 'reason': 'Invalid format'}
            
            base64_data = base64_match.group(1)
            image_bytes = base64.b64decode(base64_data)
            
            # Open image
            img = Image.open(io.BytesIO(image_bytes))
            original_size = img.size
            original_format = img.format
            
            # Check if preprocessing needed
            needs_downscale = img.width > self.downscale_threshold
            needs_compress = len(image_bytes) > self.max_image_size
            
            if not needs_downscale and not needs_compress:
                return image_data, {
                    'preprocessed': False,
                    'reason': 'Within limits',
                    'original_size': original_size
                }
            
            # Downscale if needed
            if needs_downscale:
                ratio = self.downscale_threshold / img.width
                new_size = (self.downscale_threshold, int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert to RGB (for JPEG compression)
            if img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')
            
            # Compress to JPEG
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=self.jpeg_quality, optimize=True)
            compressed_bytes = output.getvalue()
            
            # Re-encode to base64
            new_base64 = base64.b64encode(compressed_bytes).decode('utf-8')
            new_data_uri = f"data:image/jpeg;base64,{new_base64}"
            
            preprocessing_info = {
                'preprocessed': True,
                'original_size': original_size,
                'new_size': img.size,
                'original_bytes': len(image_bytes),
                'new_bytes': len(compressed_bytes),
                'reduction_percent': round((1 - len(compressed_bytes) / len(image_bytes)) * 100, 1),
                'downscaled': needs_downscale,
                'compressed': True
            }
            
            self.logger.info(
                f"Image preprocessed: {original_size} → {img.size}, "
                f"{len(image_bytes)} → {len(compressed_bytes)} bytes "
                f"({preprocessing_info['reduction_percent']}% reduction)"
            )
            
            return new_data_uri, preprocessing_info
            
        except Exception as e:
            self.logger.warning(f"Image preprocessing failed: {e}")
            return image_data, {'preprocessed': False, 'reason': f'Error: {e}'}
    
    def _estimate_tokens(self, image_data: str) -> int:
        """
        Estimate token cost for image.
        
        GitHub Copilot Vision uses ~85 tokens per 512x512 tile.
        Formula: (width/512) * (height/512) * 85
        """
        try:
            if not PIL_AVAILABLE:
                # Rough estimate based on data size
                base64_match = re.search(r'base64,(.+)', image_data)
                if base64_match:
                    base64_len = len(base64_match.group(1))
                    # Very rough: 1MB ≈ 250 tokens
                    return int((base64_len * 0.75) / 1_000_000 * 250)
                return 250  # Default estimate
            
            # Extract and decode image
            base64_match = re.search(r'base64,(.+)', image_data)
            if not base64_match:
                return 250
            
            base64_data = base64_match.group(1)
            image_bytes = base64.b64decode(base64_data)
            img = Image.open(io.BytesIO(image_bytes))
            
            # Calculate tiles
            width_tiles = max(1, img.width / 512)
            height_tiles = max(1, img.height / 512)
            estimated = int(width_tiles * height_tiles * 85)
            
            return estimated
            
        except Exception as e:
            self.logger.warning(f"Token estimation failed: {e}")
            return 250  # Safe default
    
    def _call_vision_api(self, image_data: str, prompt: str) -> Dict:
        """
        Call GitHub Copilot Vision API.
        
        NOTE: This is a PLACEHOLDER implementation.
        Actual implementation depends on GitHub Copilot API access.
        
        For production, this would integrate with:
        - GitHub Copilot Chat API
        - Or use OpenAI Vision API as fallback
        - Or use Claude Vision API as fallback
        """
        # PLACEHOLDER: Simulate vision API call
        # In production, replace with actual API integration
        
        self.logger.info(f"Vision API call (MOCK): prompt='{prompt[:50]}...'")
        
        # Simulate processing time
        import time
        time.sleep(0.5)
        
        # Return mock successful response
        # In production, this would be the actual API response
        return {
            'success': True,
            'analysis': self._generate_mock_analysis(prompt),
            'extracted_data': self._extract_mock_data(prompt),
            'tokens_used': 220,  # Mock token count
            'api_provider': 'mock'  # Would be 'github_copilot' in production
        }
    
    def _generate_mock_analysis(self, prompt: str) -> str:
        """Generate mock analysis text (replace with real API)."""
        if 'color' in prompt.lower():
            return """
            **Visual Analysis:**
            The image contains a button with the following color characteristics:
            - Background: #3B82F6 (vibrant blue)
            - Text: #FFFFFF (white)
            - Border: #2563EB (darker blue)
            - Saturation: 65% (good vibrancy)
            
            The button appears well-designed with good contrast (WCAG AA compliant).
            """
        elif 'mockup' in prompt.lower() or 'layout' in prompt.lower():
            return """
            **Layout Analysis:**
            The mockup shows a 3-column layout:
            - Left: Navigation sidebar (240px width)
            - Center: Main content area (flexible width)
            - Right: Activity feed (320px width)
            
            Components identified:
            - Header with logo and search
            - Card-based content layout
            - Responsive grid system
            """
        else:
            return """
            **UI Analysis:**
            The screenshot shows a typical web interface with:
            - Navigation elements
            - Interactive buttons
            - Form inputs
            - Text content
            
            Elements appear to follow standard UI patterns.
            """
    
    def _extract_mock_data(self, prompt: str) -> Dict:
        """Extract structured data from analysis (replace with real API)."""
        if 'color' in prompt.lower():
            return {
                'colors': {
                    'primary': '#3B82F6',
                    'text': '#FFFFFF',
                    'border': '#2563EB'
                },
                'contrast_ratio': 4.8,
                'wcag_compliant': True
            }
        elif 'mockup' in prompt.lower():
            return {
                'layout': {
                    'type': '3-column',
                    'columns': [
                        {'name': 'sidebar', 'width': '240px'},
                        {'name': 'main', 'width': 'flexible'},
                        {'name': 'activity', 'width': '320px'}
                    ]
                },
                'components': ['header', 'cards', 'grid']
            }
        else:
            return {
                'elements': ['navigation', 'buttons', 'inputs', 'text'],
                'element_count': 12
            }
    
    def _get_cache_key(self, image_data: str, prompt: str) -> str:
        """Generate cache key from image and prompt."""
        combined = f"{image_data[:1000]}{prompt}"  # Use first 1000 chars of image
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict]:
        """Retrieve cached result if not expired."""
        if not self.cache_enabled:
            return None
        
        if cache_key not in self.cache:
            return None
        
        cached = self.cache[cache_key]
        timestamp = cached['timestamp']
        
        # Check if expired
        age = datetime.now() - timestamp
        if age > timedelta(hours=self.cache_ttl_hours):
            del self.cache[cache_key]
            return None
        
        return cached['result']
    
    def _cache_result(self, cache_key: str, result: Dict):
        """Cache analysis result."""
        self.cache[cache_key] = {
            'result': result,
            'timestamp': datetime.now()
        }
        
        # Cleanup old entries (simple LRU)
        if len(self.cache) > 100:  # Max 100 cached results
            oldest_key = min(self.cache.items(), key=lambda x: x[1]['timestamp'])[0]
            del self.cache[oldest_key]
    
    def _error_response(self, error_msg: str, start_time: datetime, **kwargs) -> Dict:
        """Create error response."""
        return {
            'success': False,
            'error': error_msg,
            'tokens_used': 0,
            'processing_time_ms': (datetime.now() - start_time).total_seconds() * 1000,
            'cached': False,
            **kwargs
        }
    
    def get_metrics(self) -> Dict:
        """Get Vision API usage metrics."""
        cache_hit_rate = 0.0
        if self.total_requests > 0:
            cache_hit_rate = (self.cache_hits / (self.total_requests + self.cache_hits)) * 100
        
        avg_tokens = 0.0
        if self.total_requests > 0:
            avg_tokens = self.total_tokens_used / self.total_requests
        
        return {
            'total_requests': self.total_requests,
            'total_tokens_used': self.total_tokens_used,
            'average_tokens_per_request': round(avg_tokens, 1),
            'cache_hits': self.cache_hits,
            'cache_hit_rate_percent': round(cache_hit_rate, 1),
            'estimated_cost_usd': round(self.total_tokens_used * 0.00003, 4),  # $0.03/1K tokens
            'cache_size': len(self.cache)
        }
    
    def clear_cache(self):
        """Clear cached results."""
        self.cache.clear()
        self.logger.info("Vision API cache cleared")
