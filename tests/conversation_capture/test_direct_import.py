"""
Test Direct Import Mode for Conversation Capture

Tests the new direct file import functionality that bypasses template creation.
"""

import pytest
from pathlib import Path
from datetime import datetime, timezone
import tempfile
import os

from src.conversation_capture.command_processor import CaptureCommandProcessor
from src.conversation_capture.capture_manager import ConversationCaptureManager
from src.tier1.working_memory import WorkingMemory


@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary workspace for testing"""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    
    brain = tmp_path / "brain"
    brain.mkdir()
    (brain / "conversation-captures").mkdir()
    
    # Create tier1 directory for WorkingMemory database
    tier1 = brain / "tier1"
    tier1.mkdir()
    
    return {
        'workspace': workspace,
        'brain': brain
    }


@pytest.fixture
def sample_conversation_file(temp_workspace):
    """Create a sample conversation file"""
    content = """
You: Can you help me understand how the authentication works?

Copilot: I'd be happy to help you understand the authentication system. Based on the code, here's how it works:

The authentication uses JWT tokens with the following flow:
1. User submits credentials to /api/auth/login
2. AuthService validates credentials against database
3. If valid, JWT token is generated and returned
4. Client includes token in Authorization header for subsequent requests

You: What about password hashing?

Copilot: Good question! The system uses bcrypt for password hashing:

- Passwords are hashed using bcrypt with 10 rounds (salt factor)
- Original passwords are never stored in database
- During login, bcrypt compares submitted password with stored hash
- This protects user passwords even if database is compromised

Files involved:
- AuthService.cs (password hashing)
- LoginController.cs (authentication endpoint)
- JwtTokenGenerator.cs (token creation)
"""
    
    file_path = temp_workspace['workspace'] / "conversation_auth.txt"
    file_path.write_text(content)
    
    return file_path


@pytest.fixture
def multiple_conversation_files(temp_workspace):
    """Create multiple conversation files for batch testing"""
    files = []
    
    # File 1: Simple conversation
    content1 = """
You: Add a button to the dashboard

Copilot: I'll add a button to the dashboard for you.
"""
    file1 = temp_workspace['workspace'] / "conv1.txt"
    file1.write_text(content1)
    files.append(file1)
    
    # File 2: Complex conversation
    content2 = """
You: How do I optimize the database queries?

Copilot: Here are several ways to optimize your database queries:

1. Add indexes on frequently queried columns
2. Use SELECT with specific columns instead of SELECT *
3. Implement query caching for repeated queries
4. Consider pagination for large result sets

You: Can you show me an example of adding an index?

Copilot: Sure! Here's how to add an index in your migration:

```csharp
migrationBuilder.CreateIndex(
    name: "IX_Users_Email",
    table: "Users",
    column: "Email");
```
"""
    file2 = temp_workspace['workspace'] / "conv2.txt"
    file2.write_text(content2)
    files.append(file2)
    
    return files


@pytest.fixture
def command_processor(temp_workspace):
    """Create command processor for testing"""
    return CaptureCommandProcessor(
        brain_path=temp_workspace['brain'],
        workspace_root=temp_workspace['workspace']
    )


class TestDirectImportCommandDetection:
    """Test command detection for direct import mode"""
    
    def test_detect_single_file_parameter(self, command_processor):
        """Test detection of single file parameter"""
        result = command_processor.process_command(
            "/CORTEX capture conversation file:conversation.txt"
        )
        
        assert result['handled'] is True
        assert result['operation'] in ['direct_import_completed', 'direct_import_failed']
    
    def test_detect_multiple_file_parameters(self, command_processor):
        """Test detection of multiple file parameters"""
        result = command_processor.process_command(
            "/CORTEX capture conversation file:conv1.txt file:conv2.txt"
        )
        
        assert result['handled'] is True
        assert result['operation'] in ['direct_import_completed', 'direct_import_failed']
    
    def test_no_file_parameters_uses_template_mode(self, command_processor):
        """Test that no file parameters uses template mode"""
        result = command_processor.process_command(
            "/CORTEX capture conversation"
        )
        
        assert result['handled'] is True
        assert result['operation'] == 'capture_created'  # Template mode


class TestDirectImportSingleFile:
    """Test direct import of single file"""
    
    def test_import_valid_conversation_file(self, command_processor, sample_conversation_file):
        """Test importing a valid conversation file"""
        result = command_processor.process_command(
            f"/CORTEX capture conversation file:{sample_conversation_file}"
        )
        
        assert result['handled'] is True
        assert result['success'] is True
        assert result['operation'] == 'direct_import_completed'
        
        # Check brain integration
        brain_data = result['brain_integration']
        assert brain_data['tier'] == 'Tier 1 Working Memory'
        assert brain_data['total_files'] == 1
        assert brain_data['successful_imports'] == 1
        assert brain_data['failed_imports'] == 0
    
    def test_import_nonexistent_file(self, command_processor):
        """Test importing a file that doesn't exist"""
        result = command_processor.process_command(
            "/CORTEX capture conversation file:nonexistent.txt"
        )
        
        assert result['handled'] is True
        assert result['success'] is False
        assert result['operation'] == 'direct_import_failed'
        
        brain_data = result['brain_integration']
        assert brain_data['total_files'] == 1
        assert brain_data['successful_imports'] == 0
        assert brain_data['failed_imports'] == 1
    
    def test_import_empty_file(self, command_processor, temp_workspace):
        """Test importing an empty file"""
        empty_file = temp_workspace['workspace'] / "empty.txt"
        empty_file.write_text("")
        
        result = command_processor.process_command(
            f"/CORTEX capture conversation file:{empty_file}"
        )
        
        assert result['handled'] is True
        assert result['success'] is False  # No valid messages
        assert result['operation'] == 'direct_import_failed'


class TestDirectImportBatchFiles:
    """Test batch import of multiple files"""
    
    def test_import_multiple_valid_files(self, command_processor, multiple_conversation_files):
        """Test importing multiple valid files"""
        file_params = ' '.join([f"file:{f}" for f in multiple_conversation_files])
        result = command_processor.process_command(
            f"/CORTEX capture conversation {file_params}"
        )
        
        assert result['handled'] is True
        assert result['success'] is True
        assert result['operation'] == 'direct_import_completed'
        
        brain_data = result['brain_integration']
        assert brain_data['total_files'] == 2
        assert brain_data['successful_imports'] == 2
        assert brain_data['failed_imports'] == 0
    
    def test_import_mixed_valid_invalid_files(self, command_processor, sample_conversation_file):
        """Test importing mix of valid and invalid files"""
        result = command_processor.process_command(
            f"/CORTEX capture conversation file:{sample_conversation_file} file:nonexistent.txt"
        )
        
        assert result['handled'] is True
        # Considered success if at least one file imported
        assert result['success'] is True
        
        brain_data = result['brain_integration']
        assert brain_data['total_files'] == 2
        assert brain_data['successful_imports'] == 1
        assert brain_data['failed_imports'] == 1


class TestCaptureManagerDirectImport:
    """Test ConversationCaptureManager direct import methods"""
    
    def test_validate_file_valid(self, temp_workspace, sample_conversation_file):
        """Test file validation for valid file"""
        manager = ConversationCaptureManager(
            brain_path=temp_workspace['brain'],
            workspace_root=temp_workspace['workspace']
        )
        
        error = manager._validate_file(str(sample_conversation_file))
        assert error is None
    
    def test_validate_file_nonexistent(self, temp_workspace):
        """Test file validation for nonexistent file"""
        manager = ConversationCaptureManager(
            brain_path=temp_workspace['brain'],
            workspace_root=temp_workspace['workspace']
        )
        
        error = manager._validate_file("nonexistent.txt")
        assert error is not None
        assert "not found" in error.lower()
    
    def test_validate_file_directory(self, temp_workspace):
        """Test file validation for directory"""
        manager = ConversationCaptureManager(
            brain_path=temp_workspace['brain'],
            workspace_root=temp_workspace['workspace']
        )
        
        dir_path = temp_workspace['workspace'] / "testdir"
        dir_path.mkdir()
        
        error = manager._validate_file(str(dir_path))
        assert error is not None
        assert "not a file" in error.lower()
    
    def test_read_file_content_utf8(self, temp_workspace):
        """Test reading UTF-8 encoded file"""
        manager = ConversationCaptureManager(
            brain_path=temp_workspace['brain'],
            workspace_root=temp_workspace['workspace']
        )
        
        test_file = temp_workspace['workspace'] / "test.txt"
        test_content = "Test conversation with UTF-8: こんにちは 你好"
        test_file.write_text(test_content, encoding='utf-8')
        
        content = manager._read_file_content(str(test_file))
        assert content is not None
        assert content == test_content
    
    def test_import_files_directly_single(self, temp_workspace, sample_conversation_file):
        """Test direct import of single file"""
        manager = ConversationCaptureManager(
            brain_path=temp_workspace['brain'],
            workspace_root=temp_workspace['workspace']
        )
        
        result = manager.import_files_directly([str(sample_conversation_file)])
        
        assert result['success'] is True
        assert result['total_files'] == 1
        assert result['successful_imports'] == 1
        assert result['failed_imports'] == 0
        assert len(result['results']) == 1
        
        # Check first result
        first = result['results'][0]
        assert first['success'] is True
        assert 'conversation_id' in first
        assert first['messages_imported'] > 0
    
    def test_import_files_directly_batch(self, temp_workspace, multiple_conversation_files):
        """Test direct import of multiple files"""
        manager = ConversationCaptureManager(
            brain_path=temp_workspace['brain'],
            workspace_root=temp_workspace['workspace']
        )
        
        file_paths = [str(f) for f in multiple_conversation_files]
        result = manager.import_files_directly(file_paths)
        
        assert result['success'] is True
        assert result['total_files'] == 2
        assert result['successful_imports'] == 2
        assert result['failed_imports'] == 0
        assert len(result['results']) == 2


class TestBackwardCompatibility:
    """Test that template mode still works (backward compatibility)"""
    
    def test_template_mode_without_files(self, command_processor):
        """Test that template mode works when no files provided"""
        result = command_processor.process_command(
            "/CORTEX capture conversation"
        )
        
        assert result['handled'] is True
        assert result['operation'] == 'capture_created'
        assert 'capture_id' in result
        assert 'file_path' in result
    
    def test_import_template_mode(self, command_processor, temp_workspace, sample_conversation_file):
        """Test importing via template mode (traditional workflow)"""
        # Step 1: Create capture
        create_result = command_processor.process_command(
            "/CORTEX capture conversation"
        )
        
        assert create_result['success'] is True
        capture_id = create_result['capture_id']
        
        # Step 2: Simulate user pasting content
        capture_file = Path(create_result['file_path'])
        capture_file.write_text(sample_conversation_file.read_text())
        
        # Step 3: Import
        import_result = command_processor.process_command(
            f"/CORTEX import {capture_id}"
        )
        
        assert import_result['handled'] is True
        assert import_result['success'] is True
        assert import_result['operation'] == 'import_completed'
