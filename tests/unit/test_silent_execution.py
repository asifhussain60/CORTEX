"""
Tests for Silent Execution Middleware
=====================================
Tests output suppression and verbosity control.

Author: GitHub Copilot (for CORTEX)
Created: 2026-01-08
Feature: feat04-core-orchestration
Phase: 3 Task: 3.1
TDD Phase: RED → GREEN → REFACTOR
"""

import pytest
import sys
from io import StringIO

from src.orchestrators.middleware.silent_execution import (
    SilentExecutionMiddleware,
    OutputLevel,
    OutputMessage
)


class TestSilentExecutionMiddleware:
    """Test silent execution middleware"""
    
    def test_initializes_with_essential_level_by_default(self):
        """Should initialize with ESSENTIAL output level by default"""
        middleware = SilentExecutionMiddleware()
        assert middleware.output_level == OutputLevel.ESSENTIAL
    
    def test_can_set_output_level(self):
        """Should allow setting output level"""
        middleware = SilentExecutionMiddleware(output_level=OutputLevel.SILENT)
        assert middleware.output_level == OutputLevel.SILENT
    
    def test_start_suppression_redirects_stdout(self):
        """Should redirect stdout when suppression starts"""
        middleware = SilentExecutionMiddleware(output_level=OutputLevel.SILENT)
        original_stdout = sys.stdout
        
        middleware.start_suppression()
        assert sys.stdout != original_stdout
        assert middleware._is_suppressing is True
        
        middleware.stop_suppression()
    
    def test_stop_suppression_restores_stdout(self):
        """Should restore stdout when suppression stops"""
        middleware = SilentExecutionMiddleware(output_level=OutputLevel.SILENT)
        original_stdout = sys.stdout
        
        middleware.start_suppression()
        captured = middleware.stop_suppression()
        
        assert sys.stdout == original_stdout
        assert middleware._is_suppressing is False
    
    def test_captures_output_during_suppression(self):
        """Should capture output during suppression"""
        middleware = SilentExecutionMiddleware(output_level=OutputLevel.SILENT)
        
        middleware.start_suppression()
        print("Test output")
        captured = middleware.stop_suppression()
        
        assert "Test output" in captured
    
    def test_capture_message_stores_message(self):
        """Should store captured messages"""
        middleware = SilentExecutionMiddleware()
        
        middleware.capture_message("Test", OutputLevel.ESSENTIAL, "test")
        
        captured = middleware.get_captured_output()
        assert len(captured) == 1
        assert captured[0].content == "Test"
        assert captured[0].level == OutputLevel.ESSENTIAL
    
    def test_should_output_respects_level(self):
        """Should respect output level when deciding to output"""
        middleware = SilentExecutionMiddleware(output_level=OutputLevel.ESSENTIAL)
        
        assert middleware._should_output(OutputLevel.ESSENTIAL) is True
        assert middleware._should_output(OutputLevel.NORMAL) is False
        assert middleware._should_output(OutputLevel.VERBOSE) is False
    
    def test_get_captured_output_filters_by_level(self):
        """Should filter captured output by level"""
        middleware = SilentExecutionMiddleware()
        
        middleware.capture_message("Essential", OutputLevel.ESSENTIAL)
        middleware.capture_message("Normal", OutputLevel.NORMAL)
        middleware.capture_message("Verbose", OutputLevel.VERBOSE)
        
        essential_only = middleware.get_captured_output(OutputLevel.ESSENTIAL)
        assert len(essential_only) == 1
        assert essential_only[0].level == OutputLevel.ESSENTIAL
    
    def test_clear_captured_removes_messages(self):
        """Should clear captured messages"""
        middleware = SilentExecutionMiddleware()
        
        middleware.capture_message("Test", OutputLevel.ESSENTIAL)
        middleware.clear_captured()
        
        assert len(middleware.get_captured_output()) == 0
    
    def test_multiple_suppression_calls_are_safe(self):
        """Should handle multiple start_suppression calls safely"""
        middleware = SilentExecutionMiddleware(output_level=OutputLevel.SILENT)
        
        middleware.start_suppression()
        middleware.start_suppression()  # Should be safe
        middleware.stop_suppression()
        
        assert middleware._is_suppressing is False
