"""
CORTEX Vision API Failure Handler
Graceful degradation when Vision API is unavailable

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file
"""

from typing import Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
import os
import re


class FailureType(Enum):
    """Types of Vision API failures"""
    API_DOWN = "API_DOWN"                    # Service unavailable
    RATE_LIMIT = "RATE_LIMIT"                # Rate limit exceeded
    UNSUPPORTED_FORMAT = "UNSUPPORTED_FORMAT"  # Image format not supported
    FILE_TOO_LARGE = "FILE_TOO_LARGE"        # File size exceeds limit
    PROCESSING_ERROR = "PROCESSING_ERROR"    # Error during processing
    TIMEOUT = "TIMEOUT"                      # Request timeout
    AUTH_ERROR = "AUTH_ERROR"                # Authentication failed


@dataclass
class FailureContext:
    """Context information about a failure"""
    failure_type: FailureType
    error_message: str
    image_path: str
    file_size_kb: float
    retry_count: int
    can_retry: bool


@dataclass
class FallbackResult:
    """Results from fallback analysis"""
    image_path: str
    filename_inference: Optional[str]
    manual_input_requested: bool
    queued_for_retry: bool
    suggested_questions: List[str]
    fallback_strategy: str


class VisionFailureHandler:
    """
    Handles Vision API failures with graceful degradation
    
    Strategies:
    1. Filename heuristics (extract meaning from filename)
    2. Manual input request (ask user to describe)
    3. Queue for retry (when rate limited)
    4. Format conversion (for unsupported formats)
    """
    
    # Filename pattern recognition
    FILENAME_PATTERNS = {
        r'login|signin|auth': 'User authentication interface',
        r'dashboard|home|main': 'Main dashboard or home screen',
        r'error|exception|failure': 'Error or exception screen',
        r'mockup|wireframe|design': 'UI mockup or design',
        r'diagram|architecture|schema': 'Technical diagram',
        r'form|input|entry': 'Data entry form',
        r'table|grid|list': 'Data table or list view',
        r'chart|graph|report': 'Data visualization',
        r'settings|config|preferences': 'Settings or configuration',
        r'profile|account|user': 'User profile or account'
    }
    
    # Retry configurations
    RETRY_CONFIGS = {
        FailureType.RATE_LIMIT: {'can_retry': True, 'delay_seconds': 60},
        FailureType.TIMEOUT: {'can_retry': True, 'delay_seconds': 5},
        FailureType.PROCESSING_ERROR: {'can_retry': True, 'delay_seconds': 10},
        FailureType.API_DOWN: {'can_retry': False, 'delay_seconds': 0},
        FailureType.UNSUPPORTED_FORMAT: {'can_retry': False, 'delay_seconds': 0},
        FailureType.FILE_TOO_LARGE: {'can_retry': False, 'delay_seconds': 0},
        FailureType.AUTH_ERROR: {'can_retry': False, 'delay_seconds': 0}
    }
    
    def __init__(self, max_retries: int = 3):
        """
        Initialize failure handler
        
        Args:
            max_retries: Maximum retry attempts per failure type
        """
        self.max_retries = max_retries
        self.retry_queue = []
    
    def handle_failure(self, 
                      failure_type: FailureType,
                      error_message: str,
                      image_path: str,
                      file_size_kb: float,
                      retry_count: int = 0) -> FallbackResult:
        """
        Handle Vision API failure with appropriate fallback
        
        Args:
            failure_type: Type of failure
            error_message: Error message from API
            image_path: Path to image
            file_size_kb: File size in KB
            retry_count: Number of retries attempted
        
        Returns:
            Fallback result
        """
        context = FailureContext(
            failure_type=failure_type,
            error_message=error_message,
            image_path=image_path,
            file_size_kb=file_size_kb,
            retry_count=retry_count,
            can_retry=self._can_retry(failure_type, retry_count)
        )
        
        # Determine fallback strategy
        if context.can_retry:
            return self._queue_for_retry(context)
        elif failure_type == FailureType.UNSUPPORTED_FORMAT:
            return self._suggest_format_conversion(context)
        elif failure_type == FailureType.FILE_TOO_LARGE:
            return self._suggest_resize(context)
        else:
            return self._use_filename_heuristics(context)
    
    def _can_retry(self, failure_type: FailureType, retry_count: int) -> bool:
        """
        Determine if failure can be retried
        
        Args:
            failure_type: Type of failure
            retry_count: Current retry count
        
        Returns:
            True if can retry
        """
        if retry_count >= self.max_retries:
            return False
        
        config = self.RETRY_CONFIGS.get(failure_type, {'can_retry': False})
        return config['can_retry']
    
    def _queue_for_retry(self, context: FailureContext) -> FallbackResult:
        """
        Queue failure for retry
        
        Args:
            context: Failure context
        
        Returns:
            Fallback result
        """
        retry_config = self.RETRY_CONFIGS[context.failure_type]
        delay = retry_config['delay_seconds']
        
        self.retry_queue.append({
            'context': context,
            'retry_after_seconds': delay
        })
        
        return FallbackResult(
            image_path=context.image_path,
            filename_inference=self._infer_from_filename(context.image_path),
            manual_input_requested=False,
            queued_for_retry=True,
            suggested_questions=[
                "What type of screen or feature is shown?",
                "What are the main UI elements visible?"
            ],
            fallback_strategy=f"Queued for retry in {delay}s"
        )
    
    def _suggest_format_conversion(self, context: FailureContext) -> FallbackResult:
        """
        Suggest format conversion for unsupported formats
        
        Args:
            context: Failure context
        
        Returns:
            Fallback result
        """
        ext = os.path.splitext(context.image_path)[1].lower()
        
        return FallbackResult(
            image_path=context.image_path,
            filename_inference=self._infer_from_filename(context.image_path),
            manual_input_requested=True,
            queued_for_retry=False,
            suggested_questions=[
                f"Convert {ext} to PNG or JPG and reattach?",
                "Or describe the image contents manually?"
            ],
            fallback_strategy=f"Unsupported format ({ext}) - conversion needed"
        )
    
    def _suggest_resize(self, context: FailureContext) -> FallbackResult:
        """
        Suggest resizing for large files
        
        Args:
            context: Failure context
        
        Returns:
            Fallback result
        """
        return FallbackResult(
            image_path=context.image_path,
            filename_inference=self._infer_from_filename(context.image_path),
            manual_input_requested=True,
            queued_for_retry=False,
            suggested_questions=[
                f"Reduce image size (currently {context.file_size_kb:.0f} KB) and reattach?",
                "Or describe the image contents manually?"
            ],
            fallback_strategy="File too large - resize needed"
        )
    
    def _use_filename_heuristics(self, context: FailureContext) -> FallbackResult:
        """
        Use filename to infer image purpose
        
        Args:
            context: Failure context
        
        Returns:
            Fallback result
        """
        inference = self._infer_from_filename(context.image_path)
        
        return FallbackResult(
            image_path=context.image_path,
            filename_inference=inference,
            manual_input_requested=True,
            queued_for_retry=False,
            suggested_questions=[
                "Please describe what's shown in the image",
                "What UI elements or features are visible?",
                "What requirements should be captured?"
            ],
            fallback_strategy="Filename-based inference + manual input"
        )
    
    def _infer_from_filename(self, image_path: str) -> Optional[str]:
        """
        Infer image purpose from filename
        
        Args:
            image_path: Path to image
        
        Returns:
            Inferred purpose or None
        """
        filename = os.path.basename(image_path).lower()
        
        for pattern, inference in self.FILENAME_PATTERNS.items():
            if re.search(pattern, filename):
                return inference
        
        return None
    
    def format_failure_notice(self, result: FallbackResult) -> str:
        """
        Format failure notice for user display
        
        Args:
            result: Fallback result
        
        Returns:
            Formatted notice
        """
        lines = [
            "⚠️ **Vision API Notice:**",
            "",
            f"Vision API is currently unavailable for this image.",
            f"Image: `{os.path.basename(result.image_path)}`",
            ""
        ]
        
        # Filename inference
        if result.filename_inference:
            lines.extend([
                "📋 **Filename Inference:**",
                f"   Based on the filename, this appears to be: {result.filename_inference}",
                ""
            ])
        
        # Retry status
        if result.queued_for_retry:
            lines.extend([
                "🔄 **Retry Queued:**",
                f"   This image has been queued for automatic retry.",
                f"   Fallback strategy: {result.fallback_strategy}",
                ""
            ])
        
        # Manual input request
        if result.manual_input_requested:
            lines.extend([
                "💡 **Manual Input Requested:**",
                "   Please help by answering these questions:"
            ])
            for i, question in enumerate(result.suggested_questions, 1):
                lines.append(f"   {i}. {question}")
            lines.append("")
        
        lines.extend([
            "📝 **Proceeding with Planning:**",
            "   I'll continue with the planning workflow.",
            "   You can provide image details as we go."
        ])
        
        return "\n".join(lines)
    
    def process_retry_queue(self) -> List[Tuple[str, FailureContext]]:
        """
        Process items in retry queue
        
        Returns:
            List of (image_path, context) ready for retry
        """
        import time
        current_time = time.time()
        
        ready_for_retry = []
        remaining_queue = []
        
        for item in self.retry_queue:
            context = item['context']
            retry_after = item.get('retry_after_seconds', 0)
            queued_time = item.get('queued_time', current_time)
            
            if current_time - queued_time >= retry_after:
                ready_for_retry.append((context.image_path, context))
            else:
                remaining_queue.append(item)
        
        self.retry_queue = remaining_queue
        return ready_for_retry
    
    def get_retry_status(self) -> str:
        """
        Get status of retry queue
        
        Returns:
            Formatted status string
        """
        if not self.retry_queue:
            return "✅ No items queued for retry"
        
        lines = [
            f"🔄 **Retry Queue Status:**",
            f"   Items queued: {len(self.retry_queue)}"
        ]
        
        for item in self.retry_queue:
            context = item['context']
            lines.append(
                f"   - {os.path.basename(context.image_path)} "
                f"({context.failure_type.value}, attempt {context.retry_count + 1}/{self.max_retries})"
            )
        
        return "\n".join(lines)
