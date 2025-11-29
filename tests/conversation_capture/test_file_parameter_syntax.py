"""
Test #file: parameter syntax for direct conversation import

Verifies that when users provide files via #file: syntax (GitHub Copilot style)
or file: syntax, the system directly imports the conversation without creating
a capture template.

Example:
  "Follow instructions in CORTEX.prompt.md. I want to capture #file:chori.md"
  "capture conversation #file:chori.md"
  "capture conversation file:chori.md"
"""

import pytest
from pathlib import Path
import tempfile
import os

from src.conversation_capture.command_processor import CaptureCommandProcessor


@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary workspace with sample conversation file"""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    
    brain = tmp_path / "brain"
    brain.mkdir()
    (brain / "conversation-captures").mkdir()
    
    # Create tier1 directory for WorkingMemory database
    tier1 = brain / "tier1"
    tier1.mkdir()
    
    # Create sample conversation file
    chori_content = """
You: Can you help me understand the planning system?

Copilot: I'd be happy to help explain the planning system. It's a multi-phase approach where we:

1. Detect planning triggers like "plan a feature"
2. Create planning files in cortex-brain/documents/planning/
3. Generate phase breakdowns with tasks
4. Track progress in the database

You: How does the two-way sync work?

Copilot: The two-way sync ensures that:
- File changes automatically update the database
- Database status changes update file metadata
- Plan resolution works with both DB and filesystem fallbacks
- Integrity validation detects orphaned records or files

Files involved:
- plan_sync_manager.py (sync logic)
- planning_file_manager.py (file operations)
"""
    
    chori_file = workspace / "chori.md"
    chori_file.write_text(chori_content)
    
    return {
        'workspace': workspace,
        'brain': brain,
        'chori_file': chori_file
    }


@pytest.fixture
def command_processor(temp_workspace):
    """Create command processor for testing"""
    return CaptureCommandProcessor(
        brain_path=str(temp_workspace['brain']),
        workspace_root=str(temp_workspace['workspace'])
    )


class TestFileParameterSyntaxDetection:
    """Test detection of #file: and file: parameter syntax"""
    
    def test_detect_github_copilot_file_syntax(self, command_processor):
        """Test detection of GitHub Copilot #file: syntax"""
        result = command_processor._match_command_pattern(
            "capture conversation #file:chori.md"
        )
        
        assert result is not None
        assert result['command'] == 'capture'
        assert 'files' in result['params']
        assert 'chori.md' in result['params']['files']
        assert result['params']['mode'] == 'direct'
    
    def test_detect_plain_file_syntax(self, command_processor):
        """Test detection of plain file: syntax"""
        result = command_processor._match_command_pattern(
            "capture conversation file:chori.md"
        )
        
        assert result is not None
        assert result['command'] == 'capture'
        assert 'files' in result['params']
        assert 'chori.md' in result['params']['files']
        assert result['params']['mode'] == 'direct'
    
    def test_detect_multiple_files(self, command_processor):
        """Test detection of multiple file parameters"""
        result = command_processor._match_command_pattern(
            "capture conversation #file:chori.md #file:other.md"
        )
        
        assert result is not None
        assert result['command'] == 'capture'
        assert len(result['params']['files']) == 2
        assert 'chori.md' in result['params']['files']
        assert 'other.md' in result['params']['files']
    
    def test_mixed_file_syntax(self, command_processor):
        """Test mixed #file: and file: syntax"""
        result = command_processor._match_command_pattern(
            "capture conversation #file:chori.md file:other.md"
        )
        
        assert result is not None
        assert len(result['params']['files']) == 2
    
    def test_no_file_parameters_uses_template_mode(self, command_processor):
        """Test that absence of file parameters defaults to template mode"""
        result = command_processor._match_command_pattern(
            "capture conversation"
        )
        
        assert result is not None
        assert result['command'] == 'capture'
        assert result['params']['mode'] == 'template'
        assert 'files' not in result['params']


class TestDirectImportFromFile:
    """Test direct import workflow (bypasses template creation)"""
    
    def test_direct_import_single_file(self, command_processor, temp_workspace):
        """Test direct import of single file"""
        chori_file = temp_workspace['chori_file']
        
        result = command_processor.process_command(
            f"capture conversation #file:{chori_file}"
        )
        
        assert result['handled'] is True
        assert result['success'] is True
        assert result['operation'] == 'direct_import_completed'
        
        # Verify brain integration
        brain_data = result['brain_integration']
        assert brain_data['tier'] == 'Tier 1 Working Memory'
        assert brain_data['successful_imports'] == 1
        assert brain_data['failed_imports'] == 0
    
    def test_direct_import_relative_path(self, command_processor):
        """Test direct import with relative path"""
        result = command_processor.process_command(
            "capture conversation #file:chori.md"
        )
        
        assert result['handled'] is True
        assert result['success'] is True
        assert result['operation'] == 'direct_import_completed'
    
    def test_direct_import_bypasses_template_creation(self, command_processor, temp_workspace):
        """Verify that direct import does NOT create capture template files"""
        chori_file = temp_workspace['chori_file']
        capture_dir = temp_workspace['brain'] / "conversation-captures"
        
        # Count files before
        files_before = list(capture_dir.glob("capture_*.md"))
        
        # Run direct import
        result = command_processor.process_command(
            f"capture conversation #file:{chori_file}"
        )
        
        # Count files after
        files_after = list(capture_dir.glob("capture_*.md"))
        
        # Verify NO template files were created
        assert len(files_after) == len(files_before), \
            "Direct import should not create capture template files"
        
        # Verify import succeeded
        assert result['success'] is True
        assert result['operation'] == 'direct_import_completed'
    
    def test_direct_import_nonexistent_file(self, command_processor):
        """Test direct import with file that doesn't exist"""
        result = command_processor.process_command(
            "capture conversation #file:nonexistent.md"
        )
        
        assert result['handled'] is True
        assert result['success'] is False
        assert result['operation'] == 'direct_import_failed'


class TestNaturalLanguageWithFileParameter:
    """Test natural language commands that include file parameters"""
    
    def test_verbose_command_with_file(self, command_processor, temp_workspace):
        """Test: 'Follow instructions in CORTEX.prompt.md. I want to capture #file:chori.md'"""
        chori_file = temp_workspace['chori_file']
        
        result = command_processor.process_command(
            f"Follow instructions in CORTEX.prompt.md. I want to capture conversation #file:{chori_file}"
        )
        
        assert result['handled'] is True
        assert result['success'] is True
        assert result['operation'] == 'direct_import_completed'
    
    def test_concise_command_with_file(self, command_processor, temp_workspace):
        """Test: 'capture #file:chori.md'"""
        chori_file = temp_workspace['chori_file']
        
        result = command_processor.process_command(
            f"capture conversation #file:{chori_file}"
        )
        
        assert result['handled'] is True
        assert result['success'] is True
    
    def test_command_with_context_and_file(self, command_processor, temp_workspace):
        """Test: 'Review the planning conversation in #file:chori.md and capture it'"""
        chori_file = temp_workspace['chori_file']
        
        result = command_processor.process_command(
            f"capture conversation about planning #file:{chori_file}"
        )
        
        assert result['handled'] is True
        assert result['success'] is True


class TestBackwardCompatibility:
    """Verify template mode still works (backward compatibility)"""
    
    def test_template_mode_without_file_parameter(self, command_processor):
        """Test that template mode still works when no file parameter provided"""
        result = command_processor.process_command(
            "capture conversation"
        )
        
        assert result['handled'] is True
        assert result['success'] is True
        assert result['operation'] == 'capture_created'
        assert 'capture_id' in result
        assert 'file_path' in result
    
    def test_template_mode_with_hint(self, command_processor):
        """Test template mode with topic hint"""
        result = command_processor.process_command(
            "capture conversation about authentication"
        )
        
        assert result['handled'] is True
        assert result['success'] is True
        assert result['operation'] == 'capture_created'


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
