"""
Test Command Documentation Routing Validation

Validates that WiringValidator correctly detects documented-but-not-routed commands.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from src.validation.wiring_validator import WiringValidator


class TestCommandDocumentationRouting:
    """Test suite for command documentation routing validation."""
    
    @pytest.fixture
    def validator(self):
        """Create wiring validator instance."""
        project_root = Path(__file__).parent.parent
        return WiringValidator(project_root)
    
    def test_extract_documented_commands(self, validator):
        """Test extraction of documented commands from CORTEX.prompt.md."""
        commands = validator._extract_documented_commands()
        
        # Should find documented commands
        assert len(commands) > 0, "Should extract documented commands"
        
        # Verify structure
        for cmd in commands:
            assert "command" in cmd
            assert "description" in cmd
            assert "source_file" in cmd
            
        # Verify specific commands exist
        command_names = [c["command"] for c in commands]
        assert any("cache" in cmd.lower() for cmd in command_names), \
            "Should find cache commands in documentation"
    
    def test_extract_routing_triggers(self, validator):
        """Test extraction of routing triggers from response-templates.yaml."""
        triggers = validator._extract_routing_triggers()
        
        # Should find trigger groups
        assert len(triggers) > 0, "Should extract routing triggers"
        
        # Should have _triggers suffix
        for key in triggers.keys():
            assert key.endswith("_triggers"), f"Trigger group {key} should end with _triggers"
        
        # Should have cache triggers (after fix)
        assert "cache_status_triggers" in triggers or \
               "cache_clear_triggers" in triggers, \
            "Should have cache management triggers"
    
    def test_validate_command_documentation(self, validator):
        """Test full command documentation validation."""
        results = validator.validate_command_documentation()
        
        # Should return proper structure
        assert "total_documented_commands" in results
        assert "commands_with_routing" in results
        assert "documented_but_not_routed" in results
        assert "validation_passed" in results
        
        # Should have found some commands
        assert results["total_documented_commands"] > 0
        
        # After fix, cache commands should have routing
        if results["documented_but_not_routed"]:
            print("\n⚠️ Commands documented but not routed:")
            for cmd in results["documented_but_not_routed"]:
                print(f"   • {cmd['command']} (suggested: {cmd['suggested_trigger_group']})")
    
    def test_suggest_trigger_group_name(self, validator):
        """Test trigger group name suggestion."""
        # Test various command formats
        assert validator._suggest_trigger_group_name("cache status") == "cache_status_triggers"
        assert validator._suggest_trigger_group_name("plan ado") == "plan_ado_triggers"
        assert validator._suggest_trigger_group_name("system alignment") == "system_alignment_triggers"
        
        # Test with special characters
        assert validator._suggest_trigger_group_name("cache-clear") == "cacheclear_triggers"
        assert validator._suggest_trigger_group_name("cache.status") == "cachestatus_triggers"
    
    def test_cache_commands_now_routed(self, validator):
        """Test that cache commands are properly routed after fix."""
        results = validator.validate_command_documentation()
        
        # Check if cache commands are still in documented_but_not_routed
        cache_commands_missing = [
            cmd for cmd in results["documented_but_not_routed"]
            if "cache" in cmd["command"].lower()
        ]
        
        # After applying fix, this should be empty
        assert len(cache_commands_missing) == 0, \
            f"Cache commands should be routed after fix, found: {cache_commands_missing}"


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
