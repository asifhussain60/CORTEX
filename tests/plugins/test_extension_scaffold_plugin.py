"""
Test harness for Extension Scaffold Plugin

Tests VS Code extension project generation:
- Complete project structure creation
- TypeScript file generation
- Python bridge generation
- Configuration files (package.json, tsconfig.json)
- Build scripts and documentation

Author: CORTEX Test Suite
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
import json

from src.plugins.extension_scaffold_plugin import Plugin as ExtensionScaffoldPlugin
from src.plugins.hooks import HookPoint


class TestExtensionScaffoldInitialization:
    """Test plugin initialization and metadata"""
    
    def test_plugin_creation(self):
        """Plugin should initialize successfully"""
        plugin = ExtensionScaffoldPlugin()
        assert plugin is not None
        assert plugin.metadata.plugin_id == "extension_scaffold"
    
    def test_plugin_metadata(self):
        """Plugin metadata should be complete"""
        plugin = ExtensionScaffoldPlugin()
        metadata = plugin.metadata
        
        assert metadata.name == "Extension Scaffold Generator"
        assert metadata.version == "1.0.0"
        assert metadata.category.value == "extension"
        assert metadata.description
        assert metadata.author == "CORTEX Team"
    
    def test_plugin_hooks(self):
        """Plugin should register correct hooks"""
        plugin = ExtensionScaffoldPlugin()
        hooks = plugin.metadata.hooks
        
        assert HookPoint.ON_EXTENSION_SCAFFOLD.value in hooks
    
    def test_plugin_config_schema(self):
        """Plugin should have comprehensive config schema"""
        plugin = ExtensionScaffoldPlugin()
        config_schema = plugin.metadata.config_schema
        
        # Check critical config properties exist
        assert "extension_name" in config_schema["properties"]
        assert "display_name" in config_schema["properties"]
        assert "publisher" in config_schema["properties"]
        assert "output_dir" in config_schema["properties"]
        assert "features" in config_schema["properties"]
    
    def test_plugin_initialization_success(self):
        """Plugin should initialize successfully"""
        plugin = ExtensionScaffoldPlugin()
        result = plugin.initialize()
        
        assert result is True


class TestExtensionGeneration:
    """Test complete extension generation"""
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.mkdir')
    @patch('builtins.open', new_callable=mock_open)
    def test_execute_extension_scaffold_success(self, mock_file, mock_mkdir, mock_exists):
        """Plugin should generate complete extension project"""
        mock_exists.return_value = False  # Output dir doesn't exist
        
        plugin = ExtensionScaffoldPlugin()
        plugin.initialize()
        
        context = {
            "extension_name": "test-extension",
            "display_name": "Test Extension",
            "publisher": "test-publisher",
            "output_dir": "test-output"
        }
        
        result = plugin.execute(context)
        
        assert result["success"] is True
        assert result["extension_name"] == "test-extension"
        assert "features" in result
        assert "next_steps" in result
    
    @patch('pathlib.Path.exists')
    def test_execute_extension_scaffold_dir_exists_error(self, mock_exists):
        """Plugin should error if output directory exists"""
        mock_exists.return_value = True
        
        plugin = ExtensionScaffoldPlugin()
        plugin.initialize()
        
        context = {"output_dir": "existing-dir"}
        result = plugin.execute(context)
        
        assert result["success"] is False
        assert "already exists" in result["error"]
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.mkdir')
    @patch('builtins.open', new_callable=mock_open)
    def test_execute_with_custom_features(self, mock_file, mock_mkdir, mock_exists):
        """Plugin should respect custom feature selection"""
        mock_exists.return_value = False
        
        plugin = ExtensionScaffoldPlugin()
        plugin.initialize()
        
        context = {
            "extension_name": "minimal-ext",
            "features": ["chat_participant", "conversation_capture"]
        }
        
        result = plugin.execute(context)
        
        assert result["success"] is True
        assert set(result["features"]) == {"chat_participant", "conversation_capture"}


class TestDirectoryStructureGeneration:
    """Test directory structure creation"""
    
    @patch('pathlib.Path.mkdir')
    def test_directory_structure_creation(self, mock_mkdir):
        """Plugin should create correct directory structure"""
        plugin = ExtensionScaffoldPlugin()
        plugin.initialize()
        
        output_path = Path("test-extension")
        plugin._create_directory_structure(output_path)
        
        # Should create multiple directories
        assert mock_mkdir.call_count > 5
        
        # Verify key directories
        created_paths = [call[0][0] if call[0] else call[1].get('parents') 
                        for call in mock_mkdir.call_args_list]
        
        # At least these should be created
        assert any("src" in str(p) for p in created_paths)
        assert any("out" in str(p) for p in created_paths)
    
    @patch('pathlib.Path.mkdir')
    def test_directory_structure_nested_creation(self, mock_mkdir):
        """Plugin should create nested directory structure"""
        plugin = ExtensionScaffoldPlugin()
        plugin.initialize()
        
        output_path = Path("test-extension")
        plugin._create_directory_structure(output_path)
        
        # Should use parents=True for nested dirs
        for call in mock_mkdir.call_args_list:
            if call[1]:  # kwargs
                assert call[1].get("parents") is True


class TestPackageJsonGeneration:
    """Test package.json generation"""
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_package_json_generation(self, mock_json_dump, mock_file):
        """Plugin should generate valid package.json"""
        plugin = ExtensionScaffoldPlugin()
        plugin.initialize()
        
        output_path = Path("test-extension")
        plugin._generate_package_json(
            output_path,
            "cortex",
            "CORTEX - Test",
            "cortex-team",
            "https://github.com/test/repo"
        )
        
        # Should write JSON
        mock_json_dump.assert_called_once()
        
        # Extract the package_json dict passed to json.dump
        package_json = mock_json_dump.call_args[0][0]
        
        assert package_json["name"] == "cortex"
        assert package_json["displayName"] == "CORTEX - Test"
        assert package_json["publisher"] == "cortex-team"
        assert package_json["repository"]["url"] == "https://github.com/test/repo"
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_package_json_has_chat_participant(self, mock_json_dump, mock_file):
        """Package.json should include chat participant configuration"""
        plugin = ExtensionScaffoldPlugin()
        plugin.initialize()
        
        output_path = Path("test-extension")
        plugin._generate_package_json(output_path, "cortex", "CORTEX", "pub", "url")
        
        package_json = mock_json_dump.call_args[0][0]
        
        assert "contributes" in package_json
        assert "chatParticipants" in package_json["contributes"]
        
        participants = package_json["contributes"]["chatParticipants"]
        assert len(participants) > 0
        assert participants[0]["id"] == "cortex"
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_package_json_has_commands(self, mock_json_dump, mock_file):
        """Package.json should include CORTEX commands"""
        plugin = ExtensionScaffoldPlugin()
        plugin.initialize()
        
        output_path = Path("test-extension")
        plugin._generate_package_json(output_path, "cortex", "CORTEX", "pub", "url")
        
        package_json = mock_json_dump.call_args[0][0]
        
        commands = package_json["contributes"]["commands"]
        assert len(commands) >= 4
        
        command_ids = [cmd["command"] for cmd in commands]
        assert "cortex.resume" in command_ids
        assert "cortex.checkpoint" in command_ids


class TestTypeScriptGeneration:
    """Test TypeScript file generation"""
    
    @patch('builtins.open', new_callable=mock_open)
    def test_extension_ts_generation(self, mock_file):
        """Plugin should generate extension.ts entry point"""
        plugin = ExtensionScaffoldPlugin()
        plugin.initialize()
        
        output_path = Path("test-extension")
        features = ["chat_participant", "lifecycle_hooks"]
        
        plugin._generate_extension_ts(output_path, features)
        
        # Should write file
        mock_file.assert_called()
        
        # Extract written content
        written_content = "".join(call[0][0] for call in mock_file().write.call_args_list)
        
        assert "import * as vscode from 'vscode'" in written_content
        assert "CortexChatParticipant" in written_content
        assert "BrainBridge" in written_content
    
    @patch('builtins.open', new_callable=mock_open)
    def test_extension_ts_includes_features(self, mock_file):
        """Extension.ts should include selected features"""
        plugin = ExtensionScaffoldPlugin()
        plugin.initialize()
        
        output_path = Path("test-extension")
        features = ["lifecycle_hooks", "checkpoint_system", "token_dashboard"]
        
        plugin._generate_extension_ts(output_path, features)
        
        written_content = "".join(call[0][0] for call in mock_file().write.call_args_list)
        
        assert "LifecycleManager" in written_content
        assert "CheckpointManager" in written_content
        assert "TokenDashboardProvider" in written_content
    
    @patch('builtins.open', new_callable=mock_open)
    def test_chat_participant_ts_generation(self, mock_file):
        """Plugin should generate chatParticipant.ts"""
        plugin = ExtensionScaffoldPlugin()
        plugin.initialize()
        
        output_path = Path("test-extension")
        plugin._generate_chat_participant_ts(output_path)
        
        written_content = "".join(call[0][0] for call in mock_file().write.call_args_list)
        
        assert "CortexChatParticipant" in written_content
        assert "handleRequest" in written_content
        assert "resumeLastConversation" in written_content
    
    @patch('builtins.open', new_callable=mock_open)
    def test_brain_bridge_ts_generation(self, mock_file):
        """Plugin should generate brainBridge.ts"""
        plugin = ExtensionScaffoldPlugin()
        plugin.initialize()
        
        output_path = Path("test-extension")
        plugin._generate_brain_bridge_ts(output_path)
        
        written_content = "".join(call[0][0] for call in mock_file().write.call_args_list)
        
        assert "BrainBridge" in written_content
        assert "captureMessage" in written_content
        assert "routeRequest" in written_content
        assert "IPC" in written_content.lower()


class TestPythonBridgeGeneration:
    """Test Python bridge generation"""
    
    @patch('builtins.open', new_callable=mock_open)
    def test_python_bridge_generation(self, mock_file):
        """Plugin should generate Python IPC bridge"""
        plugin = ExtensionScaffoldPlugin()
        plugin.initialize()
        
        output_path = Path("test-extension")
        plugin._generate_python_bridge(output_path)
        
        written_content = "".join(call[0][0] for call in mock_file().write.call_args_list)
        
        assert "ExtensionBridge" in written_content
        assert "handle_command" in written_content
        assert "capture_message" in written_content
        assert "route_request" in written_content
    
    @patch('builtins.open', new_callable=mock_open)
    def test_python_bridge_has_all_handlers(self, mock_file):
        """Python bridge should implement all command handlers"""
        plugin = ExtensionScaffoldPlugin()
        plugin.initialize()
        
        output_path = Path("test-extension")
        plugin._generate_python_bridge(output_path)
        
        written_content = "".join(call[0][0] for call in mock_file().write.call_args_list)
        
        required_handlers = [
            "_capture_message",
            "_route_request",
            "_get_last_active_conversation",
            "_resume_conversation",
            "_get_token_metrics"
        ]
        
        for handler in required_handlers:
            assert handler in written_content


class TestConfigurationGeneration:
    """Test configuration file generation"""
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_tsconfig_generation(self, mock_json_dump, mock_file):
        """Plugin should generate valid tsconfig.json"""
        plugin = ExtensionScaffoldPlugin()
        plugin.initialize()
        
        output_path = Path("test-extension")
        plugin._generate_tsconfig(output_path)
        
        tsconfig = mock_json_dump.call_args[0][0]
        
        assert "compilerOptions" in tsconfig
        assert tsconfig["compilerOptions"]["module"] == "commonjs"
        assert tsconfig["compilerOptions"]["target"] == "ES2020"
        assert tsconfig["compilerOptions"]["outDir"] == "out"
    
    @patch('builtins.open', new_callable=mock_open)
    def test_vscodeignore_generation(self, mock_file):
        """Plugin should generate .vscodeignore"""
        plugin = ExtensionScaffoldPlugin()
        plugin.initialize()
        
        output_path = Path("test-extension")
        plugin._generate_vscodeignore(output_path)
        
        written_content = "".join(call[0][0] for call in mock_file().write.call_args_list)
        
        assert ".vscode/**" in written_content
        assert "src/**" in written_content
        assert "node_modules/**" in written_content
    
    @patch('builtins.open', new_callable=mock_open)
    def test_gitignore_generation(self, mock_file):
        """Plugin should generate .gitignore"""
        plugin = ExtensionScaffoldPlugin()
        plugin.initialize()
        
        output_path = Path("test-extension")
        plugin._generate_gitignore(output_path)
        
        written_content = "".join(call[0][0] for call in mock_file().write.call_args_list)
        
        assert "node_modules/" in written_content
        assert "out/" in written_content
        assert "*.vsix" in written_content


class TestDocumentationGeneration:
    """Test documentation file generation"""
    
    @patch('builtins.open', new_callable=mock_open)
    def test_readme_generation(self, mock_file):
        """Plugin should generate comprehensive README.md"""
        plugin = ExtensionScaffoldPlugin()
        plugin.initialize()
        
        output_path = Path("test-extension")
        plugin._generate_documentation(output_path, "cortex", "CORTEX Extension")
        
        # Find README.md write call
        readme_calls = [call for call in mock_file.call_args_list 
                       if "README.md" in str(call)]
        
        assert len(readme_calls) > 0
    
    @patch('builtins.open', new_callable=mock_open)
    def test_changelog_generation(self, mock_file):
        """Plugin should generate CHANGELOG.md"""
        plugin = ExtensionScaffoldPlugin()
        plugin.initialize()
        
        output_path = Path("test-extension")
        plugin._generate_documentation(output_path, "cortex", "CORTEX Extension")
        
        # Find CHANGELOG.md write call
        changelog_calls = [call for call in mock_file.call_args_list 
                          if "CHANGELOG.md" in str(call)]
        
        assert len(changelog_calls) > 0


class TestScriptGeneration:
    """Test build/package script generation"""
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.chmod')
    def test_build_script_generation(self, mock_chmod, mock_file):
        """Plugin should generate build scripts"""
        plugin = ExtensionScaffoldPlugin()
        plugin.initialize()
        
        output_path = Path("test-extension")
        plugin._generate_scripts(output_path)
        
        # Should create build.sh and build.ps1
        script_calls = [call for call in mock_file.call_args_list 
                       if "build" in str(call)]
        
        assert len(script_calls) >= 2  # .sh and .ps1
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.chmod')
    def test_build_script_executable(self, mock_chmod, mock_file):
        """Build scripts should be marked executable"""
        plugin = ExtensionScaffoldPlugin()
        plugin.initialize()
        
        output_path = Path("test-extension")
        plugin._generate_scripts(output_path)
        
        # Should chmod .sh files to 0o755
        assert mock_chmod.called


class TestFeatureToggling:
    """Test feature-based generation toggling"""
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.mkdir')
    @patch('builtins.open', new_callable=mock_open)
    def test_minimal_features(self, mock_file, mock_mkdir, mock_exists):
        """Plugin should support minimal feature set"""
        mock_exists.return_value = False
        
        plugin = ExtensionScaffoldPlugin()
        plugin.initialize()
        
        context = {
            "extension_name": "minimal",
            "features": ["chat_participant"]
        }
        
        result = plugin.execute(context)
        
        assert result["success"] is True
        assert result["features"] == ["chat_participant"]
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.mkdir')
    @patch('builtins.open', new_callable=mock_open)
    def test_full_features(self, mock_file, mock_mkdir, mock_exists):
        """Plugin should support all features"""
        mock_exists.return_value = False
        
        plugin = ExtensionScaffoldPlugin()
        plugin.initialize()
        
        context = {
            "extension_name": "full",
            "features": [
                "chat_participant",
                "conversation_capture",
                "lifecycle_hooks",
                "external_monitoring",
                "resume_prompts",
                "checkpoint_system",
                "token_dashboard"
            ]
        }
        
        result = plugin.execute(context)
        
        assert result["success"] is True
        assert len(result["features"]) == 7


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.mkdir')
    @patch('builtins.open', side_effect=IOError("Disk full"))
    def test_execute_handles_io_error(self, mock_file, mock_mkdir, mock_exists):
        """Plugin should handle IO errors gracefully"""
        mock_exists.return_value = False
        
        plugin = ExtensionScaffoldPlugin()
        plugin.initialize()
        
        context = {"extension_name": "test"}
        result = plugin.execute(context)
        
        assert result["success"] is False
        assert "error" in result
    
    def test_execute_with_missing_context(self):
        """Plugin should use defaults when context missing"""
        plugin = ExtensionScaffoldPlugin()
        plugin.initialize()
        
        # Empty context should use config defaults
        context = {}
        
        # This will fail because output_dir exists, but tests default handling
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = False
            with patch('pathlib.Path.mkdir'):
                with patch('builtins.open', new_callable=mock_open):
                    result = plugin.execute(context)
                    
                    # Should use default extension_name from config
                    assert result["extension_name"] == "cortex"


class TestPluginIntegration:
    """Test plugin integration with CORTEX system"""
    
    def test_plugin_cleanup(self):
        """Plugin should cleanup successfully"""
        plugin = ExtensionScaffoldPlugin()
        plugin.initialize()
        
        result = plugin.cleanup()
        
        assert result is True
    
    def test_plugin_lifecycle(self):
        """Plugin should handle full lifecycle"""
        plugin = ExtensionScaffoldPlugin()
        
        # Initialize
        init_result = plugin.initialize()
        assert init_result is True
        
        # Execute (with mocks)
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = False
            with patch('pathlib.Path.mkdir'):
                with patch('builtins.open', new_callable=mock_open):
                    context = {"extension_name": "test"}
                    exec_result = plugin.execute(context)
                    assert exec_result["success"] is True
        
        # Cleanup
        cleanup_result = plugin.cleanup()
        assert cleanup_result is True
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.mkdir')
    @patch('builtins.open', new_callable=mock_open)
    def test_generated_extension_structure(self, mock_file, mock_mkdir, mock_exists):
        """Generated extension should have complete structure"""
        mock_exists.return_value = False
        
        plugin = ExtensionScaffoldPlugin()
        plugin.initialize()
        
        context = {"extension_name": "cortex"}
        result = plugin.execute(context)
        
        assert result["success"] is True
        
        # Verify next steps provided
        assert "next_steps" in result
        assert len(result["next_steps"]) >= 3
        assert any("npm install" in step for step in result["next_steps"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
