"""
Tests for Direct Conversation Import

Tests streamlined file import workflow that bypasses verbose two-step capture.
"""

import pytest
from pathlib import Path
from src.operations.modules.conversations.direct_import import DirectConversationImport


@pytest.fixture
def cortex_brain_path(tmp_path):
    """Create temporary cortex-brain directory."""
    brain_path = tmp_path / "cortex-brain"
    brain_path.mkdir()
    
    # Create conversation-captures directory
    captures_dir = brain_path / "documents" / "conversation-captures"
    captures_dir.mkdir(parents=True)
    
    return brain_path


@pytest.fixture
def sample_conversation_file(cortex_brain_path):
    """Create sample conversation file."""
    captures_dir = cortex_brain_path / "documents" / "conversation-captures"
    file_path = captures_dir / "20251116-test-conversation.md"
    
    content = """# Conversation Capture: Test Conversation

**Date:** 2025-11-16
**Topic:** Test Conversation
**Participants:** User, GitHub Copilot

---

## Conversation Content

asifhussain60: How do I test direct import?

GitHub Copilot: To test direct import, create a DirectConversationImport instance and call import_from_file_reference with your file path.

asifhussain60: Got it, thanks!

GitHub Copilot: You're welcome! The streamlined workflow bypasses the verbose capture step.
"""
    
    file_path.write_text(content, encoding="utf-8")
    return file_path


@pytest.fixture
def direct_importer(cortex_brain_path):
    """Create DirectConversationImport instance."""
    return DirectConversationImport(cortex_brain_path)


def test_extract_file_path_from_file_reference(direct_importer, sample_conversation_file):
    """Test extracting file path from #file: reference."""
    user_request = f"/CORTEX capture conversation #file:{sample_conversation_file.name}"
    project_root = sample_conversation_file.parent.parent.parent
    
    extracted_path = direct_importer._extract_file_path(user_request, project_root)
    
    assert extracted_path is not None
    assert extracted_path.exists()
    assert extracted_path.name == sample_conversation_file.name


def test_extract_file_path_from_natural_language(direct_importer, sample_conversation_file):
    """Test extracting file path from natural language."""
    user_request = f"import conversation from {sample_conversation_file.name}"
    project_root = sample_conversation_file.parent.parent.parent
    
    extracted_path = direct_importer._extract_file_path(user_request, project_root)
    
    assert extracted_path is not None
    assert extracted_path.exists()


def test_import_from_file_reference_success(direct_importer, sample_conversation_file):
    """Test successful direct import from file reference."""
    user_request = f"/CORTEX capture conversation #file:{sample_conversation_file.name}"
    project_root = sample_conversation_file.parent.parent.parent
    
    result = direct_importer.import_from_file_reference(
        user_request=user_request,
        project_root=project_root
    )
    
    assert result["success"] is True
    assert "conversation_id" in result
    assert result["messages_imported"] > 0
    assert "✅" in result["message"]


def test_import_from_file_reference_file_not_found(direct_importer, cortex_brain_path):
    """Test import with non-existent file."""
    user_request = "/CORTEX capture conversation #file:nonexistent.md"
    project_root = cortex_brain_path
    
    result = direct_importer.import_from_file_reference(
        user_request=user_request,
        project_root=project_root
    )
    
    assert result["success"] is False
    assert result["error"] == "file_not_found"


def test_import_from_file_reference_no_file_reference(direct_importer):
    """Test import without file reference."""
    user_request = "/CORTEX capture conversation"
    
    result = direct_importer.import_from_file_reference(
        user_request=user_request
    )
    
    assert result["success"] is False
    assert result["error"] == "no_file_reference"


def test_import_from_content(direct_importer):
    """Test importing from pre-loaded content."""
    content = """
asifhussain60: Test message 1

GitHub Copilot: Response 1

asifhussain60: Test message 2

GitHub Copilot: Response 2
"""
    
    result = direct_importer.import_from_content(
        content=content,
        source_description="test-conversation"
    )
    
    assert result["success"] is True
    assert result["messages_imported"] > 0


def test_resolve_path_absolute(direct_importer, sample_conversation_file):
    """Test resolving absolute path."""
    resolved = direct_importer._resolve_path(
        str(sample_conversation_file),
        project_root=None
    )
    
    assert resolved is not None
    assert resolved == sample_conversation_file


def test_resolve_path_relative_to_project_root(direct_importer, sample_conversation_file):
    """Test resolving relative path from project root."""
    project_root = sample_conversation_file.parent.parent.parent
    relative_path = sample_conversation_file.relative_to(project_root)
    
    resolved = direct_importer._resolve_path(
        str(relative_path),
        project_root=project_root
    )
    
    assert resolved is not None
    assert resolved.exists()


def test_resolve_path_common_location(direct_importer, sample_conversation_file):
    """Test resolving path from common location."""
    project_root = sample_conversation_file.parent.parent.parent
    
    # Use just filename - should find in conversation-captures
    resolved = direct_importer._resolve_path(
        sample_conversation_file.name,
        project_root=project_root
    )
    
    assert resolved is not None
    assert resolved.exists()
    assert resolved.name == sample_conversation_file.name


def test_multiple_file_reference_patterns(direct_importer, sample_conversation_file):
    """Test various file reference patterns."""
    project_root = sample_conversation_file.parent.parent.parent
    
    patterns = [
        f"#file:{sample_conversation_file.name}",
        f"from {sample_conversation_file.name}",
        f"import {sample_conversation_file.name}",
        f"capture {sample_conversation_file.name}",
    ]
    
    for pattern in patterns:
        extracted = direct_importer._extract_file_path(pattern, project_root)
        assert extracted is not None, f"Pattern failed: {pattern}"
        assert extracted.exists()
