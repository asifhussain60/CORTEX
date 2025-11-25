"""
Image Attachment Detector for CORTEX

Automatically detects image attachments in user requests and triggers Vision API analysis.
Supports: data URIs, file paths, base64 strings, and GitHub Copilot Chat attachments.

Design Document: cortex-brain/cortex-3.0-design/vision-api-auto-detection.md
"""

import re
import base64
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ImageAttachment:
    """Represents a detected image attachment."""
    source: str  # 'data_uri', 'file_path', 'base64', 'url'
    format: str  # 'png', 'jpeg', 'jpg', 'webp', 'gif'
    data: str  # Data URI format (data:image/...)
    size_bytes: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    original_reference: str = ""  # Original text that referenced the image


class ImageDetector:
    """
    Detects image attachments in user requests.
    
    Supports multiple attachment formats:
    - Data URIs: data:image/png;base64,...
    - File paths: /path/to/image.png, C:/images\\screenshot.jpg
    - Base64 strings: (with format hints)
    - URLs: http://example.com/image.png
    - GitHub Copilot Chat attachments (special markers)
    
    Example:
        detector = ImageDetector(config)
        images = detector.detect(user_request, attachments)
        
        for img in images:
            print(f"Found {img.format} image from {img.source}")
    """
    
    def __init__(self, config: Dict):
        """
        Initialize image detector.
        
        Args:
            config: Configuration dictionary
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Detection settings
        vision_config = config.get('vision_api', {})
        self.auto_detect = vision_config.get('auto_detect_images', True)
        self.max_images = vision_config.get('max_images_per_request', 5)
        self.supported_formats = vision_config.get(
            'supported_formats',
            ['png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp']
        )
        
        # Compile regex patterns for efficiency
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for image detection."""
        # Data URI pattern
        self.data_uri_pattern = re.compile(
            r'data:image/(png|jpeg|jpg|webp|gif|bmp);base64,([A-Za-z0-9+/=]+)',
            re.IGNORECASE
        )
        
        # File path pattern (cross-platform)
        self.file_path_pattern = re.compile(
            r'(?:^|\s)([A-Z]:\\[^\s]+\.(?:png|jpg|jpeg|webp|gif|bmp)|'
            r'/[^\s]+\.(?:png|jpg|jpeg|webp|gif|bmp)|'
            r'\./[^\s]+\.(?:png|jpg|jpeg|webp|gif|bmp))',
            re.IGNORECASE | re.MULTILINE
        )
        
        # URL pattern
        self.url_pattern = re.compile(
            r'https?://[^\s]+\.(?:png|jpg|jpeg|webp|gif|bmp)(?:\?[^\s]*)?',
            re.IGNORECASE
        )
        
        # Base64 string with format hint
        self.base64_hint_pattern = re.compile(
            r'\[(?:image|screenshot|png|jpg|jpeg):base64\]\s*([A-Za-z0-9+/=]{100,})',
            re.IGNORECASE
        )
        
        # GitHub Copilot Chat attachment marker
        self.copilot_attachment_pattern = re.compile(
            r'#attachment:([^\s]+)',
            re.IGNORECASE
        )
    
    def detect(
        self,
        user_request: str,
        attachments: Optional[List[Dict]] = None
    ) -> List[ImageAttachment]:
        """
        Detect all images in user request and attachments.
        
        Args:
            user_request: User's text request
            attachments: Optional list of attachment objects from chat interface
            
        Returns:
            List of ImageAttachment objects (empty if none found)
        """
        if not self.auto_detect:
            return []
        
        detected_images = []
        
        try:
            # 1. Check for data URIs in text
            detected_images.extend(self._detect_data_uris(user_request))
            
            # 2. Check for file paths
            detected_images.extend(self._detect_file_paths(user_request))
            
            # 3. Check for URLs
            detected_images.extend(self._detect_urls(user_request))
            
            # 4. Check for base64 with format hints
            detected_images.extend(self._detect_base64_hints(user_request))
            
            # 5. Check for GitHub Copilot Chat attachments
            if attachments:
                detected_images.extend(self._detect_copilot_attachments(attachments))
            
            # 6. Check for attachment markers in text
            detected_images.extend(self._detect_attachment_markers(user_request))
            
            # Limit to max_images
            if len(detected_images) > self.max_images:
                self.logger.warning(
                    f"Found {len(detected_images)} images, limiting to {self.max_images}"
                )
                detected_images = detected_images[:self.max_images]
            
            if detected_images:
                self.logger.info(
                    f"Detected {len(detected_images)} image(s): "
                    f"{[img.source for img in detected_images]}"
                )
            
            return detected_images
            
        except Exception as e:
            self.logger.error(f"Image detection error: {e}", exc_info=True)
            return []
    
    def _detect_data_uris(self, text: str) -> List[ImageAttachment]:
        """Detect data URI images in text."""
        images = []
        
        for match in self.data_uri_pattern.finditer(text):
            format_type = match.group(1).lower()
            base64_data = match.group(2)
            
            if format_type not in self.supported_formats:
                continue
            
            data_uri = match.group(0)
            
            # Estimate size
            size_bytes = len(base64_data) * 3 // 4  # Base64 to bytes conversion
            
            images.append(ImageAttachment(
                source='data_uri',
                format=format_type,
                data=data_uri,
                size_bytes=size_bytes,
                original_reference=data_uri[:100] + '...'
            ))
        
        return images
    
    def _detect_file_paths(self, text: str) -> List[ImageAttachment]:
        """Detect file path references to images."""
        images = []
        
        for match in self.file_path_pattern.finditer(text):
            file_path = match.group(1)
            path = Path(file_path)
            
            # Check if file exists
            if not path.exists():
                self.logger.warning(f"Image file not found: {file_path}")
                continue
            
            # Check format
            format_type = path.suffix.lower().lstrip('.')
            if format_type not in self.supported_formats:
                continue
            
            # Read and convert to data URI
            try:
                with open(path, 'rb') as f:
                    image_bytes = f.read()
                
                base64_data = base64.b64encode(image_bytes).decode('utf-8')
                data_uri = f"data:image/{format_type};base64,{base64_data}"
                
                images.append(ImageAttachment(
                    source='file_path',
                    format=format_type,
                    data=data_uri,
                    size_bytes=len(image_bytes),
                    original_reference=file_path
                ))
            except Exception as e:
                self.logger.error(f"Failed to read image file {file_path}: {e}")
        
        return images
    
    def _detect_urls(self, text: str) -> List[ImageAttachment]:
        """Detect image URLs in text."""
        images = []
        
        for match in self.url_pattern.finditer(text):
            url = match.group(0)
            
            # Extract format from URL
            format_match = re.search(r'\.(\w+)(?:\?|$)', url)
            if not format_match:
                continue
            
            format_type = format_match.group(1).lower()
            if format_type not in self.supported_formats:
                continue
            
            # Note: Actual URL fetching would happen in Vision API
            # Here we just register that a URL was found
            images.append(ImageAttachment(
                source='url',
                format=format_type,
                data=url,  # Store URL directly
                original_reference=url
            ))
        
        return images
    
    def _detect_base64_hints(self, text: str) -> List[ImageAttachment]:
        """Detect base64 strings with format hints."""
        images = []
        
        for match in self.base64_hint_pattern.finditer(text):
            base64_data = match.group(1)
            
            # Try to infer format from hint
            hint_text = match.group(0).lower()
            if 'png' in hint_text:
                format_type = 'png'
            elif 'jpg' in hint_text or 'jpeg' in hint_text:
                format_type = 'jpeg'
            else:
                format_type = 'png'  # Default
            
            data_uri = f"data:image/{format_type};base64,{base64_data}"
            size_bytes = len(base64_data) * 3 // 4
            
            images.append(ImageAttachment(
                source='base64',
                format=format_type,
                data=data_uri,
                size_bytes=size_bytes,
                original_reference='[base64 data]'
            ))
        
        return images
    
    def _detect_copilot_attachments(self, attachments: List[Dict]) -> List[ImageAttachment]:
        """
        Detect images from GitHub Copilot Chat attachments.
        
        Args:
            attachments: List of attachment objects from chat interface
                Format: [{'type': 'image', 'data': '...', 'mimeType': '...'}]
        """
        images = []
        
        for attachment in attachments:
            # Check if it's an image attachment
            if attachment.get('type') != 'image':
                continue
            
            mime_type = attachment.get('mimeType', '')
            if not mime_type.startswith('image/'):
                continue
            
            # Extract format from mime type
            format_type = mime_type.split('/')[-1].lower()
            if format_type not in self.supported_formats:
                continue
            
            # Get image data
            data = attachment.get('data', '')
            if not data:
                continue
            
            # Ensure it's in data URI format
            if not data.startswith('data:'):
                data = f"data:{mime_type};base64,{data}"
            
            # Extract size if provided
            size_bytes = attachment.get('size')
            width = attachment.get('width')
            height = attachment.get('height')
            
            images.append(ImageAttachment(
                source='copilot_attachment',
                format=format_type,
                data=data,
                size_bytes=size_bytes,
                width=width,
                height=height,
                original_reference=attachment.get('name', '[copilot attachment]')
            ))
        
        return images
    
    def _detect_attachment_markers(self, text: str) -> List[ImageAttachment]:
        """
        Detect attachment markers in text (e.g., #attachment:image1).
        
        These are references to attachments that should be resolved separately.
        """
        images = []
        
        for match in self.copilot_attachment_pattern.finditer(text):
            attachment_id = match.group(1)
            
            # This would be resolved by the chat interface
            # For now, just log that we found a reference
            self.logger.info(f"Found attachment reference: {attachment_id}")
            
            # Placeholder - actual resolution happens in orchestrator
            images.append(ImageAttachment(
                source='attachment_marker',
                format='unknown',
                data='',  # To be resolved
                original_reference=f"#attachment:{attachment_id}"
            ))
        
        return images
    
    def has_images(self, user_request: str, attachments: Optional[List[Dict]] = None) -> bool:
        """
        Quick check if request has any images.
        
        Args:
            user_request: User's text request
            attachments: Optional list of attachments
            
        Returns:
            True if images detected, False otherwise
        """
        if not self.auto_detect:
            return False
        
        # Quick regex checks (faster than full detection)
        if self.data_uri_pattern.search(user_request):
            return True
        
        if self.file_path_pattern.search(user_request):
            return True
        
        if self.url_pattern.search(user_request):
            return True
        
        if attachments:
            for attachment in attachments:
                if attachment.get('type') == 'image':
                    return True
        
        return False
    
    def get_image_context_summary(self, images: List[ImageAttachment]) -> str:
        """
        Generate summary of detected images for context injection.
        
        Args:
            images: List of detected images
            
        Returns:
            Human-readable summary string
        """
        if not images:
            return ""
        
        summary_parts = [f"📸 Detected {len(images)} image(s):"]
        
        for i, img in enumerate(images, 1):
            size_str = f"{img.size_bytes / 1024:.1f}KB" if img.size_bytes else "unknown size"
            dim_str = f"{img.width}x{img.height}" if img.width and img.height else ""
            
            summary = f"  {i}. {img.format.upper()} from {img.source}"
            if dim_str:
                summary += f" ({dim_str})"
            summary += f" [{size_str}]"
            
            summary_parts.append(summary)
        
        return "\n".join(summary_parts)
