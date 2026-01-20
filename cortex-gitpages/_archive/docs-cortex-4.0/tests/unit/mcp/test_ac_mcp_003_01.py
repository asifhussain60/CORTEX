"""
AC-MCP-003-01: MCP Configuration Files Tests

Tests for MCP configuration files for Claude Desktop and VS Code integration.

Compliance: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
"""

import pytest
import json
from pathlib import Path


class TestClaudeDesktopConfig:
    """Test Claude Desktop configuration file."""
    
    def test_claude_config_exists(self) -> None:
        """Test that claude_desktop_config.json exists."""
        config_path = Path("mcp-config/claude-desktop.json")
        assert config_path.exists()
    
    def test_claude_config_valid_json(self) -> None:
        """Test that claude_desktop_config.json is valid JSON."""
        config_path = Path("mcp-config/claude-desktop.json")
        with open(config_path) as f:
            config = json.load(f)
        
        assert isinstance(config, dict)
    
    def test_claude_config_has_mcp_servers(self) -> None:
        """Test that claude_desktop_config.json has mcpServers."""
        config_path = Path("mcp-config/claude-desktop.json")
        with open(config_path) as f:
            config = json.load(f)
        
        assert "mcpServers" in config
        assert isinstance(config["mcpServers"], dict)
    
    def test_claude_config_has_cortex_server(self) -> None:
        """Test that claude_desktop_config.json defines cortex server."""
        config_path = Path("mcp-config/claude-desktop.json")
        with open(config_path) as f:
            config = json.load(f)
        
        cortex_config = config["mcpServers"]["cortex"]
        assert cortex_config is not None
    
    def test_claude_config_cortex_command(self) -> None:
        """Test that cortex server has command."""
        config_path = Path("mcp-config/claude-desktop.json")
        with open(config_path) as f:
            config = json.load(f)
        
        cortex_config = config["mcpServers"]["cortex"]
        assert "command" in cortex_config
        assert cortex_config["command"] == "python"
    
    def test_claude_config_cortex_args(self) -> None:
        """Test that cortex server has args."""
        config_path = Path("mcp-config/claude-desktop.json")
        with open(config_path) as f:
            config = json.load(f)
        
        cortex_config = config["mcpServers"]["cortex"]
        assert "args" in cortex_config
        assert isinstance(cortex_config["args"], list)
        assert "-m" in cortex_config["args"]
        assert "src.mcp" in cortex_config["args"]
    
    def test_claude_config_cortex_cwd(self) -> None:
        """Test that cortex server has cwd."""
        config_path = Path("mcp-config/claude-desktop.json")
        with open(config_path) as f:
            config = json.load(f)
        
        cortex_config = config["mcpServers"]["cortex"]
        assert "cwd" in cortex_config
    
    def test_claude_config_cortex_env(self) -> None:
        """Test that cortex server has environment variables."""
        config_path = Path("mcp-config/claude-desktop.json")
        with open(config_path) as f:
            config = json.load(f)
        
        cortex_config = config["mcpServers"]["cortex"]
        assert "env" in cortex_config
        assert isinstance(cortex_config["env"], dict)


class TestVSCodeConfig:
    """Test VS Code configuration file."""
    
    def test_vscode_config_exists(self) -> None:
        """Test that vscode_mcp.json exists."""
        config_path = Path("mcp-config/vscode-mcp.json")
        assert config_path.exists()
    
    def test_vscode_config_valid_json(self) -> None:
        """Test that vscode_mcp.json is valid JSON."""
        config_path = Path("mcp-config/vscode-mcp.json")
        with open(config_path) as f:
            config = json.load(f)
        
        assert isinstance(config, dict)
    
    def test_vscode_config_has_mcp_servers(self) -> None:
        """Test that vscode_mcp.json has mcpServers."""
        config_path = Path("mcp-config/vscode-mcp.json")
        with open(config_path) as f:
            config = json.load(f)
        
        assert "mcpServers" in config
        assert isinstance(config["mcpServers"], dict)
    
    def test_vscode_config_has_cortex_server(self) -> None:
        """Test that vscode_mcp.json defines cortex server."""
        config_path = Path("mcp-config/vscode-mcp.json")
        with open(config_path) as f:
            config = json.load(f)
        
        cortex_config = config["mcpServers"]["cortex"]
        assert cortex_config is not None
    
    def test_vscode_config_cortex_command(self) -> None:
        """Test that cortex server has command."""
        config_path = Path("mcp-config/vscode-mcp.json")
        with open(config_path) as f:
            config = json.load(f)
        
        cortex_config = config["mcpServers"]["cortex"]
        assert "command" in cortex_config
        assert cortex_config["command"] == "python"
    
    def test_vscode_config_cortex_args(self) -> None:
        """Test that cortex server has args."""
        config_path = Path("mcp-config/vscode-mcp.json")
        with open(config_path) as f:
            config = json.load(f)
        
        cortex_config = config["mcpServers"]["cortex"]
        assert "args" in cortex_config
        assert isinstance(cortex_config["args"], list)


class TestMCPReadme:
    """Test MCP README documentation."""
    
    def test_readme_exists(self) -> None:
        """Test that README.md exists."""
        readme_path = Path("mcp-config/README.md")
        assert readme_path.exists()
    
    def test_readme_has_content(self) -> None:
        """Test that README.md has content."""
        readme_path = Path("mcp-config/README.md")
        with open(readme_path) as f:
            content = f.read()
        
        assert len(content) > 100
        assert "# MCP Configuration" in content or "MCP" in content
    
    def test_readme_has_claude_section(self) -> None:
        """Test that README.md has Claude Desktop section."""
        readme_path = Path("mcp-config/README.md")
        with open(readme_path) as f:
            content = f.read()
        
        assert "Claude" in content
    
    def test_readme_has_vscode_section(self) -> None:
        """Test that README.md has VS Code section."""
        readme_path = Path("mcp-config/README.md")
        with open(readme_path) as f:
            content = f.read()
        
        assert "VS Code" in content or "VS Code" in content.replace(" ", "")
    
    def test_readme_has_troubleshooting(self) -> None:
        """Test that README.md has troubleshooting section."""
        readme_path = Path("mcp-config/README.md")
        with open(readme_path) as f:
            content = f.read()
        
        assert "troubleshoot" in content.lower() or "Troubleshoot" in content


class TestConfigurationCompatibility:
    """Test configuration compatibility."""
    
    def test_both_configs_have_same_server_name(self) -> None:
        """Test that both configs define 'cortex' server."""
        with open(Path("mcp-config/claude-desktop.json")) as f:
            claude_config = json.load(f)
        
        with open(Path("mcp-config/vscode-mcp.json")) as f:
            vscode_config = json.load(f)
        
        assert "cortex" in claude_config["mcpServers"]
        assert "cortex" in vscode_config["mcpServers"]
    
    def test_both_configs_use_python_command(self) -> None:
        """Test that both configs use python command."""
        with open(Path("mcp-config/claude-desktop.json")) as f:
            claude_config = json.load(f)
        
        with open(Path("mcp-config/vscode-mcp.json")) as f:
            vscode_config = json.load(f)
        
        assert claude_config["mcpServers"]["cortex"]["command"] == "python"
        assert vscode_config["mcpServers"]["cortex"]["command"] == "python"
    
    def test_configs_have_valid_module_path(self) -> None:
        """Test that configs point to valid module path."""
        with open(Path("mcp-config/claude-desktop.json")) as f:
            claude_config = json.load(f)
        
        args = claude_config["mcpServers"]["cortex"]["args"]
        assert len(args) >= 2
        assert args[0] == "-m"
        assert args[1] == "src.mcp"


class TestConfigurationValues:
    """Test specific configuration values."""
    
    def test_claude_config_command_is_string(self) -> None:
        """Test that command value is a string."""
        with open(Path("mcp-config/claude-desktop.json")) as f:
            config = json.load(f)
        
        assert isinstance(config["mcpServers"]["cortex"]["command"], str)
    
    def test_claude_config_args_are_strings(self) -> None:
        """Test that all args are strings."""
        with open(Path("mcp-config/claude-desktop.json")) as f:
            config = json.load(f)
        
        args = config["mcpServers"]["cortex"]["args"]
        for arg in args:
            assert isinstance(arg, str)
    
    def test_vscode_config_args_are_strings(self) -> None:
        """Test that all args are strings in VS Code config."""
        with open(Path("mcp-config/vscode-mcp.json")) as f:
            config = json.load(f)
        
        args = config["mcpServers"]["cortex"]["args"]
        for arg in args:
            assert isinstance(arg, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
