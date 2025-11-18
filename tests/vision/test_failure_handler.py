"""
Tests for CORTEX Vision API Failure Handler

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file
"""

import pytest
import os

from src.vision.failure_handler import (
    VisionFailureHandler,
    FailureType,
    FailureContext,
    FallbackResult
)


class TestVisionFailureHandler:
    """Test vision failure handling"""
    
    def test_handle_rate_limit_failure(self):
        """Test handling of rate limit failure"""
        handler = VisionFailureHandler()
        
        result = handler.handle_failure(
            failure_type=FailureType.RATE_LIMIT,
            error_message="Rate limit exceeded",
            image_path="login-screen.png",
            file_size_kb=150.0,
            retry_count=0
        )
        
        assert result.queued_for_retry is True
        assert result.manual_input_requested is False
        assert "retry" in result.fallback_strategy.lower()
    
    def test_handle_unsupported_format(self):
        """Test handling of unsupported format"""
        handler = VisionFailureHandler()
        
        result = handler.handle_failure(
            failure_type=FailureType.UNSUPPORTED_FORMAT,
            error_message="Format not supported",
            image_path="diagram.bmp",
            file_size_kb=200.0,
            retry_count=0
        )
        
        assert result.queued_for_retry is False
        assert result.manual_input_requested is True
        assert "conversion" in result.fallback_strategy.lower()
        assert any("Convert" in q for q in result.suggested_questions)
    
    def test_handle_file_too_large(self):
        """Test handling of large file"""
        handler = VisionFailureHandler()
        
        result = handler.handle_failure(
            failure_type=FailureType.FILE_TOO_LARGE,
            error_message="File size exceeds limit",
            image_path="screenshot.png",
            file_size_kb=5000.0,
            retry_count=0
        )
        
        assert result.queued_for_retry is False
        assert result.manual_input_requested is True
        assert "resize" in result.fallback_strategy.lower()
        assert any("5000" in q for q in result.suggested_questions)
    
    def test_handle_api_down(self):
        """Test handling of API unavailable"""
        handler = VisionFailureHandler()
        
        result = handler.handle_failure(
            failure_type=FailureType.API_DOWN,
            error_message="Service unavailable",
            image_path="mockup.png",
            file_size_kb=100.0,
            retry_count=0
        )
        
        assert result.queued_for_retry is False
        assert result.manual_input_requested is True
    
    def test_filename_inference_login(self):
        """Test filename inference for login screens"""
        handler = VisionFailureHandler()
        
        inference = handler._infer_from_filename("user-login-form.png")
        
        assert inference is not None
        assert "authentication" in inference.lower()
    
    def test_filename_inference_dashboard(self):
        """Test filename inference for dashboards"""
        handler = VisionFailureHandler()
        
        inference = handler._infer_from_filename("main-dashboard-view.png")
        
        assert inference is not None
        assert "dashboard" in inference.lower()
    
    def test_filename_inference_error(self):
        """Test filename inference for errors"""
        handler = VisionFailureHandler()
        
        inference = handler._infer_from_filename("error-message-screenshot.png")
        
        assert inference is not None
        assert "error" in inference.lower()
    
    def test_filename_inference_no_match(self):
        """Test filename inference with no pattern match"""
        handler = VisionFailureHandler()
        
        inference = handler._infer_from_filename("IMG_1234.png")
        
        assert inference is None
    
    def test_retry_limit_enforcement(self):
        """Test that retry limit is enforced"""
        handler = VisionFailureHandler(max_retries=2)
        
        # First retry should be allowed
        result1 = handler.handle_failure(
            failure_type=FailureType.TIMEOUT,
            error_message="Timeout",
            image_path="test.png",
            file_size_kb=100.0,
            retry_count=0
        )
        assert result1.queued_for_retry is True
        
        # Second retry should be allowed
        result2 = handler.handle_failure(
            failure_type=FailureType.TIMEOUT,
            error_message="Timeout",
            image_path="test.png",
            file_size_kb=100.0,
            retry_count=1
        )
        assert result2.queued_for_retry is True
        
        # Third retry should not be allowed
        result3 = handler.handle_failure(
            failure_type=FailureType.TIMEOUT,
            error_message="Timeout",
            image_path="test.png",
            file_size_kb=100.0,
            retry_count=2
        )
        assert result3.queued_for_retry is False
    
    def test_retry_queue_management(self):
        """Test retry queue management"""
        handler = VisionFailureHandler()
        
        # Queue two failures
        handler.handle_failure(
            failure_type=FailureType.RATE_LIMIT,
            error_message="Rate limited",
            image_path="test1.png",
            file_size_kb=100.0
        )
        handler.handle_failure(
            failure_type=FailureType.TIMEOUT,
            error_message="Timeout",
            image_path="test2.png",
            file_size_kb=100.0
        )
        
        assert len(handler.retry_queue) == 2
    
    def test_format_failure_notice(self):
        """Test failure notice formatting"""
        handler = VisionFailureHandler()
        
        result = FallbackResult(
            image_path="login-mockup.png",
            filename_inference="User authentication interface",
            manual_input_requested=True,
            queued_for_retry=False,
            suggested_questions=["What UI elements are shown?"],
            fallback_strategy="Filename inference + manual input"
        )
        
        notice = handler.format_failure_notice(result)
        
        assert "Vision API Notice" in notice
        assert "login-mockup.png" in notice
        assert "User authentication interface" in notice
        assert "Manual Input Requested" in notice
        assert "What UI elements are shown?" in notice
    
    def test_retry_status_empty(self):
        """Test retry status with empty queue"""
        handler = VisionFailureHandler()
        
        status = handler.get_retry_status()
        
        assert "No items queued" in status
    
    def test_retry_status_with_items(self):
        """Test retry status with queued items"""
        handler = VisionFailureHandler()
        
        handler.handle_failure(
            failure_type=FailureType.RATE_LIMIT,
            error_message="Rate limited",
            image_path="test.png",
            file_size_kb=100.0
        )
        
        status = handler.get_retry_status()
        
        assert "Retry Queue Status" in status
        assert "Items queued: 1" in status
        assert "test.png" in status
    
    def test_suggested_questions_for_manual_input(self):
        """Test that appropriate questions are suggested"""
        handler = VisionFailureHandler()
        
        result = handler.handle_failure(
            failure_type=FailureType.API_DOWN,
            error_message="Service down",
            image_path="form.png",
            file_size_kb=100.0
        )
        
        # Should have suggested questions
        assert len(result.suggested_questions) > 0
        assert result.manual_input_requested is True
    
    def test_different_retry_delays(self):
        """Test that different failures have different retry delays"""
        handler = VisionFailureHandler()
        
        # Rate limit should have longer delay
        rate_config = handler.RETRY_CONFIGS[FailureType.RATE_LIMIT]
        timeout_config = handler.RETRY_CONFIGS[FailureType.TIMEOUT]
        
        assert rate_config['delay_seconds'] > timeout_config['delay_seconds']
    
    def test_non_retryable_failures(self):
        """Test that certain failures are not retryable"""
        handler = VisionFailureHandler()
        
        non_retryable = [
            FailureType.API_DOWN,
            FailureType.UNSUPPORTED_FORMAT,
            FailureType.FILE_TOO_LARGE,
            FailureType.AUTH_ERROR
        ]
        
        for failure_type in non_retryable:
            can_retry = handler._can_retry(failure_type, 0)
            assert can_retry is False


class TestFailureContext:
    """Test FailureContext dataclass"""
    
    def test_context_creation(self):
        """Test failure context creation"""
        context = FailureContext(
            failure_type=FailureType.RATE_LIMIT,
            error_message="Rate limit exceeded",
            image_path="test.png",
            file_size_kb=150.0,
            retry_count=1,
            can_retry=True
        )
        
        assert context.failure_type == FailureType.RATE_LIMIT
        assert context.retry_count == 1
        assert context.can_retry is True


class TestFallbackResult:
    """Test FallbackResult dataclass"""
    
    def test_result_creation(self):
        """Test fallback result creation"""
        result = FallbackResult(
            image_path="test.png",
            filename_inference="Login screen",
            manual_input_requested=True,
            queued_for_retry=False,
            suggested_questions=["Question 1"],
            fallback_strategy="Manual input"
        )
        
        assert result.image_path == "test.png"
        assert result.filename_inference == "Login screen"
        assert result.manual_input_requested is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
