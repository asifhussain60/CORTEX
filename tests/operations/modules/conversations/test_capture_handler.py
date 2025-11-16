"""
Tests for Conversation Capture Handler (Feature 5 - Phase 1)

Tests the first step of two-step conversation capture workflow.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from src.operations.modules.conversations.capture_handler import ConversationCaptureHandler


@pytest.fixture
def temp_cortex_brain():
    """Create temporary CORTEX brain directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        brain_path = Path(tmpdir) / "cortex-brain"
        brain_path.mkdir(parents=True, exist_ok=True)
        yield brain_path


@pytest.fixture
def capture_handler(temp_cortex_brain):
    """Create ConversationCaptureHandler instance"""
    return ConversationCaptureHandler(temp_cortex_brain)


class TestConversationCaptureHandler:
    """Test suite for ConversationCaptureHandler"""
    
    def test_initialization(self, temp_cortex_brain):
        """Test handler initialization creates captures directory"""
        handler = ConversationCaptureHandler(temp_cortex_brain)
        
        assert handler.cortex_brain_path == temp_cortex_brain
        assert handler.captures_dir.exists()
        assert handler.captures_dir == temp_cortex_brain / "documents" / "conversation-captures"
    
    def test_capture_conversation_with_description(self, capture_handler):
        """Test capturing conversation with custom description"""
        result = capture_handler.capture_conversation(description="roadmap planning")
        
        assert result["success"] is True
        assert "roadmap-planning" in result["filename"]
        assert datetime.now().strftime("%Y%m%d") in result["filename"]
        assert result["filename"].endswith(".md")
        
        # Check file was created
        file_path = Path(result["absolute_path"])
        assert file_path.exists()
        
        # Check content has template
        content = file_path.read_text(encoding="utf-8")
        assert "# Conversation Capture" in content
        assert "Topic:** roadmap planning" in content
        assert "Paste your conversation here" in content  # Matches both with and without ellipsis
    
    def test_capture_conversation_without_description(self, capture_handler):
        """Test capturing conversation with auto-generated description"""
        result = capture_handler.capture_conversation()
        
        assert result["success"] is True
        assert "conversation" in result["filename"]
        assert datetime.now().strftime("%Y%m%d") in result["filename"]
        
        # File should exist
        file_path = Path(result["absolute_path"])
        assert file_path.exists()
    
    def test_capture_conversation_sanitizes_special_characters(self, capture_handler):
        """Test description sanitization removes special characters"""
        result = capture_handler.capture_conversation(description="API Design & Implementation!")
        
        assert result["success"] is True
        # Special characters should be removed/replaced
        assert "&" not in result["filename"]
        assert "!" not in result["filename"]
        assert "api-design" in result["filename"].lower()
    
    def test_capture_conversation_duplicate_filename(self, capture_handler):
        """Test handling of duplicate filename (file already exists)"""
        description = "test-duplicate"
        
        # Create first file
        result1 = capture_handler.capture_conversation(description=description)
        assert result1["success"] is True
        
        # Try to create same file again
        result2 = capture_handler.capture_conversation(description=description)
        assert result2["success"] is False
        assert result2["error"] == "file_exists"
        assert "already exists" in result2["message"]
    
    def test_capture_conversation_with_metadata(self, capture_handler):
        """Test capturing conversation with custom metadata"""
        result = capture_handler.capture_conversation(
            description="feature-planning",
            topic="Authentication System",
            metadata={"priority": "high", "complexity": "medium"}
        )
        
        assert result["success"] is True
        
        # Check metadata in file
        file_path = Path(result["absolute_path"])
        content = file_path.read_text(encoding="utf-8")
        assert "Topic:** Authentication System" in content
        assert "Priority:** high" in content
        assert "Complexity:** medium" in content
    
    def test_capture_conversation_template_structure(self, capture_handler):
        """Test generated template has required structure"""
        result = capture_handler.capture_conversation(description="test")
        
        file_path = Path(result["absolute_path"])
        content = file_path.read_text(encoding="utf-8")
        
        # Check required sections
        assert "# Conversation Capture" in content
        assert "**Date:**" in content
        assert "**Time:**" in content
        assert "**Topic:**" in content
        assert "**Participants:**" in content
        assert "**Status:**" in content
        assert "## Instructions" in content
        assert "## Conversation Content" in content
        assert "Paste your conversation here" in content  # Matches both with and without ellipsis
        assert "Captured:**" in content
    
    def test_list_pending_captures(self, capture_handler):
        """Test listing pending capture files"""
        # Create a few pending captures
        capture_handler.capture_conversation(description="test1")
        capture_handler.capture_conversation(description="test2")
        
        result = capture_handler.list_pending_captures()
        
        assert result["success"] is True
        assert result["count"] == 2
        assert len(result["pending_files"]) == 2
        
        # Check file info structure
        file_info = result["pending_files"][0]
        assert "filename" in file_info
        assert "path" in file_info
        assert "created" in file_info
        assert "size_bytes" in file_info
    
    def test_list_pending_captures_empty(self, capture_handler):
        """Test listing pending captures when none exist"""
        result = capture_handler.list_pending_captures()
        
        assert result["success"] is True
        assert result["count"] == 0
        assert len(result["pending_files"]) == 0
    
    def test_capture_returns_proper_message(self, capture_handler):
        """Test capture returns user-friendly message"""
        result = capture_handler.capture_conversation(description="test")
        
        assert "Empty conversation file created" in result["message"]
        assert "Open the file" in result["message"]
        assert "Paste your conversation content" in result["message"]
        assert "Save the file" in result["message"]
        assert "/CORTEX Import" in result["message"]
    
    def test_capture_creates_directory_if_missing(self, temp_cortex_brain):
        """Test handler creates captures directory if it doesn't exist"""
        # Remove captures directory
        captures_dir = temp_cortex_brain / "documents" / "conversation-captures"
        if captures_dir.exists():
            import shutil
            shutil.rmtree(captures_dir)
        
        # Handler should create it
        handler = ConversationCaptureHandler(temp_cortex_brain)
        assert captures_dir.exists()
    
    def test_capture_handles_long_descriptions(self, capture_handler):
        """Test handling of very long descriptions"""
        long_description = "This is a very long description that should be handled gracefully " * 10
        
        result = capture_handler.capture_conversation(description=long_description)
        
        assert result["success"] is True
        # Filename should be sanitized but still valid
        assert len(result["filename"]) < 300  # Reasonable limit
