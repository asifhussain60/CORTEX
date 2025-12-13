"""
Image Context Middleware for CORTEX

Automatically detects image attachments in Copilot Chat context and triggers
Vision API analysis without explicit user request.

Design Goal: Eliminate user friction - "I have to keep explicitly stating this"

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
Version: 1.0

Features:
- Automatic image attachment detection (<500ms)
- Context-aware Vision API engagement
- Seamless integration with existing infrastructure
- Zero user configuration required

Usage:
    from src.operations.utilities.image_context_middleware import ImageContextMiddleware
    
    middleware = ImageContextMiddleware(config)
    
    # Check for images and auto-engage Vision API
    result = middleware.process_context(
        user_message="What should I do here?",
        attachments=copilot_chat_attachments
    )
    
    if result['vision_engaged']:
        print(f"Analyzed {result['images_analyzed']} images automatically")
        print(result['analysis_summary'])
"""

import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class ImageContextMiddleware:
    """
    Middleware to automatically detect and analyze images in Copilot Chat context.
    
    Integrates with existing Vision API infrastructure:
    - src/tier1/vision_orchestrator.py
    - src/tier1/image_detector.py
    - src/tier1/vision_api.py
    - src/cortex_agents/screenshot_analyzer.py
    
    Performance: <500ms engagement time
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize image context middleware.
        
        Args:
            config: Configuration dictionary (loads from cortex.config.json if None)
        """
        self.logger = logging.getLogger(__name__)
        
        # Load config
        if config is None:
            config = self._load_config()
        
        self.config = config
        
        # Vision API settings
        vision_config = config.get('vision_api', {})
        self.enabled = vision_config.get('enabled', False)
        self.auto_engage = vision_config.get('auto_engage_on_image', True)
        self.max_engagement_time_ms = vision_config.get('max_engagement_time_ms', 500)
        
        # Initialize Vision infrastructure
        self.vision_orchestrator = None
        if self.enabled:
            try:
                from src.tier1.vision_orchestrator import VisionOrchestrator
                self.vision_orchestrator = VisionOrchestrator(config)
                self.logger.info("🎭 Image context middleware initialized with Vision API")
            except Exception as e:
                self.logger.warning(f"Could not initialize Vision API: {e}")
                self.enabled = False
        
        # Metrics
        self.total_requests = 0
        self.requests_with_images = 0
        self.auto_engagements = 0
        self.avg_engagement_time_ms = 0
    
    def _load_config(self) -> Dict:
        """
        Load configuration from cortex.config.json.
        
        Returns:
            Configuration dictionary
        """
        try:
            from src.config import CortexConfig
            import json
            
            cortex_config = CortexConfig()
            config_file = cortex_config.root_path / "cortex.config.json"
            
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load config: {e}")
        
        return {}
    
    def detect_images_in_context(
        self,
        user_message: str,
        attachments: Optional[List[Dict]] = None,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Detect if images are present in Copilot Chat context.
        
        Checks multiple sources:
        1. Explicit attachments parameter
        2. Context dictionary (image_base64, image_path, etc.)
        3. User message references to images/screenshots
        
        Args:
            user_message: User's text message
            attachments: Optional list of attachment objects
            context: Optional context dictionary
        
        Returns:
            {
                'has_images': bool,
                'image_count': int,
                'image_sources': List[str],  # ['attachment', 'context', 'reference']
                'detection_time_ms': float
            }
        """
        start_time = time.perf_counter()
        
        result = {
            'has_images': False,
            'image_count': 0,
            'image_sources': [],
            'detection_time_ms': 0
        }
        
        # Check 1: Explicit attachments
        if attachments:
            image_attachments = [
                a for a in attachments
                if a.get('type', '').lower() in ['image', 'png', 'jpg', 'jpeg', 'gif', 'bmp']
                or a.get('mime_type', '').startswith('image/')
            ]
            if image_attachments:
                result['has_images'] = True
                result['image_count'] += len(image_attachments)
                result['image_sources'].append('attachment')
        
        # Check 2: Context dictionary
        if context:
            image_keys = [
                'image_base64', 'image_path', 'image_data', 'screenshot',
                'image_url', 'image_file'
            ]
            has_context_images = any(
                key in context for key in image_keys
            ) or any(
                k.startswith('image') for k in context.keys()
            )
            
            if has_context_images:
                result['has_images'] = True
                result['image_count'] += 1
                if 'context' not in result['image_sources']:
                    result['image_sources'].append('context')
        
        # Check 3: Message references (lower confidence)
        message_lower = user_message.lower()
        image_references = [
            'screenshot', 'image', 'picture', 'photo', 'see this',
            'look at this', 'attached', 'shown here'
        ]
        has_message_reference = any(ref in message_lower for ref in image_references)
        
        if has_message_reference and result['image_count'] == 0:
            # Only count message references if no actual images found yet
            # This prevents false positives
            result['has_images'] = True
            result['image_count'] = 1  # Estimate
            result['image_sources'].append('message_reference')
        
        end_time = time.perf_counter()
        result['detection_time_ms'] = (end_time - start_time) * 1000
        
        return result
    
    def infer_analysis_context(self, user_message: str) -> str:
        """
        Infer what type of image analysis to perform based on user message.
        
        Args:
            user_message: User's text message
        
        Returns:
            Context type: 'generic', 'planning', 'debugging', 'ado'
        """
        message_lower = user_message.lower()
        
        # Planning context
        planning_keywords = [
            'plan', 'implement', 'build', 'create', 'feature',
            'ui', 'interface', 'component', 'design'
        ]
        if any(kw in message_lower for kw in planning_keywords):
            return 'planning'
        
        debugging_keywords = [
            'error', 'bug', 'issue', 'problem', 'fail', 'crash',
            'exception', 'stack trace', 'warning'
        ]
        if any(kw in message_lower for kw in debugging_keywords):
            return 'debugging'
        
        # ADO context
        ado_keywords = [
            'ado', 'work item', 'story', 'task', 'feature',
            'azure devops', 'backlog'
        ]
        if any(kw in message_lower for kw in ado_keywords):
            return 'ado'
        
        # Default to generic
        return 'generic'
    
    def process_context(
        self,
        user_message: str,
        attachments: Optional[List[Dict]] = None,
        context: Optional[Dict] = None,
        force_engage: bool = False
    ) -> Dict[str, Any]:
        """
        Process Copilot Chat context and auto-engage Vision API if images detected.
        
        This is the main entry point for automatic image analysis.
        
        Args:
            user_message: User's text message
            attachments: Optional list of attachment objects
            context: Optional context dictionary
            force_engage: Force Vision API engagement even if auto_engage disabled
        
        Returns:
            {
                'vision_engaged': bool,
                'images_detected': int,
                'images_analyzed': int,
                'analysis_summary': str,  # Human-readable summary
                'analysis_data': Dict,     # Structured data for agents
                'engagement_time_ms': float,
                'detection_time_ms': float,
                'within_sla': bool,       # <500ms requirement
                'errors': List[str]
            }
        """
        self.total_requests += 1
        start_time = time.perf_counter()
        
        result = {
            'vision_engaged': False,
            'images_detected': 0,
            'images_analyzed': 0,
            'analysis_summary': '',
            'analysis_data': {},
            'engagement_time_ms': 0,
            'detection_time_ms': 0,
            'within_sla': True,
            'errors': []
        }
        
        try:
            # Step 1: Detect images
            detection_result = self.detect_images_in_context(
                user_message, attachments, context
            )
            result['detection_time_ms'] = detection_result['detection_time_ms']
            
            if not detection_result['has_images']:
                # No images - return early
                return result
            
            result['images_detected'] = detection_result['image_count']
            self.requests_with_images += 1
            
            self.logger.info(
                f"🎭 Images detected: {detection_result['image_count']} "
                f"(sources: {', '.join(detection_result['image_sources'])})"
            )
            
            # Step 2: Check if should auto-engage
            should_engage = (
                self.enabled and
                (self.auto_engage or force_engage) and
                self.vision_orchestrator is not None
            )
            
            if not should_engage:
                result['analysis_summary'] = (
                    f"📷 {detection_result['image_count']} image(s) detected "
                    f"(Vision API disabled or not configured)"
                )
                return result
            
            # Step 3: Infer analysis context
            analysis_context = self.infer_analysis_context(user_message)
            
            self.logger.info(
                f"🎭 Auto-engaging Vision API (context: {analysis_context})"
            )
            
            # Step 4: Engage Vision API
            vision_result = self.vision_orchestrator.process_request(
                user_request=user_message,
                attachments=attachments,
                context_type=analysis_context
            )
            
            # Step 5: Process results
            result['vision_engaged'] = True
            result['images_analyzed'] = vision_result.get('images_analyzed', 0)
            result['analysis_summary'] = vision_result.get('context_summary', '')
            result['analysis_data'] = vision_result.get('context_data', {})
            
            if vision_result.get('errors'):
                result['errors'].extend(vision_result['errors'])
            
            # Update metrics
            self.auto_engagements += 1
            
        except Exception as e:
            self.logger.error(f"Image context processing failed: {e}")
            result['errors'].append(str(e))
        
        # Calculate total engagement time
        end_time = time.perf_counter()
        result['engagement_time_ms'] = (end_time - start_time) * 1000
        
        # Check SLA (<500ms)
        result['within_sla'] = result['engagement_time_ms'] < self.max_engagement_time_ms
        
        if not result['within_sla']:
            self.logger.warning(
                f"Vision engagement exceeded SLA: {result['engagement_time_ms']:.1f}ms "
                f"(target: {self.max_engagement_time_ms}ms)"
            )
        
        # Update running average
        if self.auto_engagements > 0:
            self.avg_engagement_time_ms = (
                (self.avg_engagement_time_ms * (self.auto_engagements - 1) +
                 result['engagement_time_ms']) / self.auto_engagements
            )
        
        return result
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get middleware performance metrics.
        
        Returns:
            {
                'total_requests': int,
                'requests_with_images': int,
                'auto_engagements': int,
                'engagement_rate': float,  # % of requests with images that engaged Vision
                'avg_engagement_time_ms': float,
                'within_sla_rate': float
            }
        """
        engagement_rate = 0
        if self.requests_with_images > 0:
            engagement_rate = (self.auto_engagements / self.requests_with_images) * 100
        
        return {
            'total_requests': self.total_requests,
            'requests_with_images': self.requests_with_images,
            'auto_engagements': self.auto_engagements,
            'engagement_rate': engagement_rate,
            'avg_engagement_time_ms': self.avg_engagement_time_ms,
            'enabled': self.enabled,
            'auto_engage': self.auto_engage
        }


# Global middleware instance (lazy initialization)
_middleware_instance = None


def get_middleware(config: Optional[Dict] = None) -> ImageContextMiddleware:
    """
    Get global middleware instance (singleton pattern).
    
    Args:
        config: Optional configuration (only used on first call)
    
    Returns:
        ImageContextMiddleware instance
    """
    global _middleware_instance
    
    if _middleware_instance is None:
        _middleware_instance = ImageContextMiddleware(config)
    
    return _middleware_instance
