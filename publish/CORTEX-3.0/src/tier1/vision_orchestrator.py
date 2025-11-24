"""
Vision API Orchestrator for CORTEX

Coordinates automatic image detection, Vision API analysis, and context injection.
Integrates with intent router to provide seamless image analysis in conversations.

Design Document: cortex-brain/cortex-3.0-design/vision-api-auto-detection.md
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from .image_detector import ImageDetector, ImageAttachment
from .vision_api import VisionAPI


class VisionOrchestrator:
    """
    Orchestrates automatic image detection and analysis.
    
    Workflow:
    1. Detect images in user request
    2. Analyze each image with Vision API
    3. Inject analysis results into context
    4. Generate summary for response
    
    Example:
        orchestrator = VisionOrchestrator(config)
        
        result = orchestrator.process_request(
            user_request="analyze this screenshot",
            attachments=[{'type': 'image', 'data': '...'}]
        )
        
        if result['images_found']:
            print(f"Analyzed {result['images_analyzed']} images")
            print(result['context_summary'])
    """
    
    def __init__(self, config: Dict):
        """
        Initialize Vision orchestrator.
        
        Args:
            config: Configuration dictionary
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Initialize components
        self.detector = ImageDetector(config)
        self.vision_api = VisionAPI(config)
        
        # Settings
        vision_config = config.get('vision_api', {})
        self.enabled = vision_config.get('enabled', False)
        self.auto_detect = vision_config.get('auto_detect_images', True)
        self.auto_analyze = vision_config.get('auto_analyze_on_detect', True)
        self.inject_context = vision_config.get('auto_inject_context', True)
        
        # Default prompts for different contexts
        self.default_prompts = {
            'generic': "Analyze this image and describe what you see. Extract any text, UI elements, colors, or important details.",
            'planning': "Extract UI elements, buttons, inputs, labels, and layout structure. Identify components that would need to be implemented.",
            'debugging': "Analyze this screenshot for errors, warnings, or issues. Extract error messages, stack traces, and relevant context.",
            'ado': "Extract ADO work item details: ID number, title, description, acceptance criteria, status, and any other structured information."
        }
        
        # Metrics
        self.total_requests = 0
        self.requests_with_images = 0
        self.total_images_analyzed = 0
    
    def process_request(
        self,
        user_request: str,
        attachments: Optional[List[Dict]] = None,
        context_type: str = 'generic',
        custom_prompt: Optional[str] = None
    ) -> Dict:
        """
        Process user request with automatic image detection and analysis.
        
        Args:
            user_request: User's text request
            attachments: Optional list of attachment objects
            context_type: Type of analysis ('generic', 'planning', 'debugging', 'ado')
            custom_prompt: Optional custom analysis prompt (overrides context_type)
            
        Returns:
            {
                'images_found': bool,
                'images_analyzed': int,
                'images_failed': int,
                'detected_images': List[ImageAttachment],
                'analysis_results': List[Dict],
                'context_summary': str,  # For injection into conversation
                'context_data': Dict,     # Structured data for agents
                'processing_time_ms': float,
                'errors': List[str]
            }
        """
        start_time = datetime.now()
        self.total_requests += 1
        
        result = {
            'images_found': False,
            'images_analyzed': 0,
            'images_failed': 0,
            'detected_images': [],
            'analysis_results': [],
            'context_summary': '',
            'context_data': {},
            'processing_time_ms': 0,
            'errors': []
        }
        
        try:
            # Check if feature is enabled
            if not self.enabled or not self.auto_detect:
                return result
            
            # 1. Detect images
            detected_images = self.detector.detect(user_request, attachments)
            
            if not detected_images:
                return result
            
            result['images_found'] = True
            result['detected_images'] = detected_images
            self.requests_with_images += 1
            
            self.logger.info(
                f"Processing request with {len(detected_images)} image(s) "
                f"[context: {context_type}]"
            )
            
            # 2. Analyze images (if auto_analyze enabled)
            if not self.auto_analyze:
                result['context_summary'] = self.detector.get_image_context_summary(detected_images)
                return result
            
            # Determine analysis prompt
            analysis_prompt = custom_prompt or self.default_prompts.get(
                context_type,
                self.default_prompts['generic']
            )
            
            # Analyze each image
            analysis_results = []
            for i, image in enumerate(detected_images, 1):
                try:
                    # Skip if no data (e.g., unresolved attachment marker)
                    if not image.data:
                        result['errors'].append(
                            f"Image {i} ({image.original_reference}): No data available"
                        )
                        result['images_failed'] += 1
                        continue
                    
                    # Analyze with Vision API
                    self.logger.info(
                        f"Analyzing image {i}/{len(detected_images)} "
                        f"({image.format} from {image.source})"
                    )
                    
                    analysis = self.vision_api.analyze_image(
                        image_data=image.data,
                        prompt=analysis_prompt
                    )
                    
                    if analysis['success']:
                        result['images_analyzed'] += 1
                        self.total_images_analyzed += 1
                        
                        # Add image metadata to analysis
                        analysis['image_metadata'] = {
                            'source': image.source,
                            'format': image.format,
                            'size_bytes': image.size_bytes,
                            'original_reference': image.original_reference
                        }
                        
                        analysis_results.append(analysis)
                    else:
                        result['images_failed'] += 1
                        error_msg = f"Image {i}: {analysis.get('error', 'Unknown error')}"
                        result['errors'].append(error_msg)
                        self.logger.error(error_msg)
                
                except Exception as e:
                    result['images_failed'] += 1
                    error_msg = f"Image {i} analysis failed: {e}"
                    result['errors'].append(error_msg)
                    self.logger.error(error_msg, exc_info=True)
            
            result['analysis_results'] = analysis_results
            
            # 3. Generate context summary
            if self.inject_context and analysis_results:
                result['context_summary'] = self._generate_context_summary(
                    detected_images,
                    analysis_results
                )
                result['context_data'] = self._extract_context_data(analysis_results)
            
            # Calculate processing time
            result['processing_time_ms'] = (
                datetime.now() - start_time
            ).total_seconds() * 1000
            
            self.logger.info(
                f"Vision processing complete: {result['images_analyzed']} analyzed, "
                f"{result['images_failed']} failed, "
                f"{result['processing_time_ms']:.0f}ms"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Vision orchestrator error: {e}", exc_info=True)
            result['errors'].append(f"Orchestrator error: {e}")
            result['processing_time_ms'] = (
                datetime.now() - start_time
            ).total_seconds() * 1000
            return result
    
    def _generate_context_summary(
        self,
        images: List[ImageAttachment],
        analysis_results: List[Dict]
    ) -> str:
        """
        Generate human-readable summary for context injection.
        
        Args:
            images: List of detected images
            analysis_results: List of Vision API analysis results
            
        Returns:
            Formatted summary string
        """
        summary_parts = [
            "📸 **Vision API Analysis Results**",
            f"Found {len(images)} image(s), analyzed {len(analysis_results)}\n"
        ]
        
        for i, (image, analysis) in enumerate(zip(images, analysis_results), 1):
            # Image header
            summary_parts.append(f"**Image {i}:** {image.format.upper()} from {image.source}")
            
            # Analysis text
            analysis_text = analysis.get('analysis', '').strip()
            if analysis_text:
                # Truncate if too long
                if len(analysis_text) > 500:
                    analysis_text = analysis_text[:497] + "..."
                summary_parts.append(analysis_text)
            
            # Extracted data
            extracted = analysis.get('extracted_data', {})
            if extracted:
                summary_parts.append("\n**Extracted Data:**")
                for key, value in extracted.items():
                    if isinstance(value, dict):
                        summary_parts.append(f"  • {key}: {len(value)} items")
                    elif isinstance(value, list):
                        summary_parts.append(f"  • {key}: {len(value)} items")
                    else:
                        summary_parts.append(f"  • {key}: {value}")
            
            # Token usage
            tokens = analysis.get('tokens_used', 0)
            if tokens:
                cached = " (cached)" if analysis.get('cached') else ""
                summary_parts.append(f"\n*Tokens: {tokens}{cached}*")
            
            summary_parts.append("")  # Blank line between images
        
        return "\n".join(summary_parts)
    
    def _extract_context_data(self, analysis_results: List[Dict]) -> Dict:
        """
        Extract structured data from analysis results for agent consumption.
        
        Args:
            analysis_results: List of Vision API analysis results
            
        Returns:
            Structured data dictionary
        """
        context_data = {
            'images': [],
            'all_extracted_data': [],
            'combined_text': [],
            'ui_elements': [],
            'colors': [],
            'errors': [],
            'ado_items': []
        }
        
        for i, analysis in enumerate(analysis_results, 1):
            # Store full analysis
            context_data['images'].append({
                'index': i,
                'analysis': analysis.get('analysis', ''),
                'metadata': analysis.get('image_metadata', {})
            })
            
            # Extract structured data
            extracted = analysis.get('extracted_data', {})
            if extracted:
                context_data['all_extracted_data'].append(extracted)
                
                # Parse common patterns
                if 'colors' in extracted:
                    context_data['colors'].extend(extracted['colors'])
                
                if 'ui_elements' in extracted or 'elements' in extracted:
                    elements = extracted.get('ui_elements', extracted.get('elements', []))
                    context_data['ui_elements'].extend(elements)
                
                if 'errors' in extracted or 'error_messages' in extracted:
                    errors = extracted.get('errors', extracted.get('error_messages', []))
                    context_data['errors'].extend(errors)
                
                if 'ado' in extracted or 'work_item' in extracted:
                    ado_data = extracted.get('ado', extracted.get('work_item', {}))
                    context_data['ado_items'].append(ado_data)
            
            # Extract text content
            analysis_text = analysis.get('analysis', '').strip()
            if analysis_text:
                context_data['combined_text'].append(analysis_text)
        
        # Join combined text
        context_data['combined_text'] = '\n\n'.join(context_data['combined_text'])
        
        return context_data
    
    def quick_check(
        self,
        user_request: str,
        attachments: Optional[List[Dict]] = None
    ) -> bool:
        """
        Quick check if request has images (without full analysis).
        
        Args:
            user_request: User's text request
            attachments: Optional list of attachments
            
        Returns:
            True if images detected, False otherwise
        """
        if not self.enabled or not self.auto_detect:
            return False
        
        return self.detector.has_images(user_request, attachments)
    
    def get_metrics(self) -> Dict:
        """
        Get Vision orchestrator usage metrics.
        
        Returns:
            Metrics dictionary
        """
        image_rate = 0.0
        if self.total_requests > 0:
            image_rate = (self.requests_with_images / self.total_requests) * 100
        
        avg_images = 0.0
        if self.requests_with_images > 0:
            avg_images = self.total_images_analyzed / self.requests_with_images
        
        return {
            'total_requests': self.total_requests,
            'requests_with_images': self.requests_with_images,
            'image_detection_rate_percent': round(image_rate, 1),
            'total_images_analyzed': self.total_images_analyzed,
            'average_images_per_request': round(avg_images, 2),
            'vision_api_metrics': self.vision_api.get_metrics()
        }
    
    def analyze_specific_image(
        self,
        image_data: str,
        prompt: str,
        context_type: str = 'generic'
    ) -> Dict:
        """
        Analyze a specific image with custom prompt (manual analysis).
        
        Args:
            image_data: Image data URI or file path
            prompt: Analysis prompt
            context_type: Context type for logging
            
        Returns:
            Analysis result dictionary
        """
        try:
            # If file path, convert to data URI
            if not image_data.startswith('data:'):
                from pathlib import Path
                import base64
                
                path = Path(image_data)
                if not path.exists():
                    return {
                        'success': False,
                        'error': f'File not found: {image_data}'
                    }
                
                with open(path, 'rb') as f:
                    image_bytes = f.read()
                
                format_type = path.suffix.lstrip('.').lower()
                base64_data = base64.b64encode(image_bytes).decode('utf-8')
                image_data = f"data:image/{format_type};base64,{base64_data}"
            
            # Analyze with Vision API
            self.logger.info(f"Manual image analysis [context: {context_type}]")
            result = self.vision_api.analyze_image(image_data, prompt)
            
            if result['success']:
                self.total_images_analyzed += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"Manual analysis error: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
