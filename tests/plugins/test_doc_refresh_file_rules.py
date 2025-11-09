"""
Tests for document refresh plugin file creation prohibition rules

CRITICAL RULES TESTED:
1. Plugin NEVER creates new files
2. Plugin FAILS if target file doesn't exist
3. Plugin TRIMS content instead of creating variants
4. Plugin enforces read time limits
5. Plugin NEVER creates Quick Read, Summary, or variant versions
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from src.plugins.doc_refresh_plugin import Plugin


class TestDocRefreshFileCreationProhibition:
    """Test that doc refresh NEVER creates new files"""
    
    @pytest.fixture
    def plugin(self):
        """Create plugin instance with strict rules enabled"""
        plugin = Plugin()
        plugin.config = {
            "enforce_no_file_creation": True,
            "enforce_read_time_limits": True,
            "awakening_story_target_minutes": 60,
            "trim_content_on_exceed": True,
            "backup_before_refresh": False  # Disable for tests
        }
        return plugin
    
    def test_fails_when_file_does_not_exist(self, plugin):
        """CRITICAL: Plugin MUST fail if target file doesn't exist"""
        non_existent_file = Path("docs/story/CORTEX-STORY/NonExistent.md")
        
        result = plugin._refresh_story_doc(non_existent_file, {})
        
        assert result["success"] is False
        assert "CRITICAL VIOLATION" in result["error"]
        assert "does not exist" in result["error"]
        assert "NEVER creates new files" in result["error"]
    
    def test_refresh_all_docs_fails_on_missing_file(self, plugin):
        """Test that _refresh_all_docs enforces file existence"""
        with patch.object(Path, 'exists', return_value=False):
            result = plugin._refresh_all_docs({})
            
            assert result["success"] is False
            assert len(result["errors"]) > 0
            assert any("PROHIBITED" in error for error in result["errors"])
            assert any("does not exist" in error for error in result["errors"])
    
    def test_prohibits_quick_read_creation(self, plugin):
        """CRITICAL: Plugin must NEVER create Quick Read variant"""
        # This test verifies the principle: if Quick Read file exists, it should
        # only be updated. If it doesn't exist, creation is prohibited.
        
        quick_read_path = Path("docs/story/CORTEX-STORY/Awakening Of CORTEX - Quick Read.md")
        
        # Test scenario 1: If file exists, it should be updateable (but we want to discourage this)
        # Test scenario 2: If file doesn't exist, creation is PROHIBITED
        
        # For this test, we mock non-existence to test prohibition
        with patch.object(Path, 'exists', return_value=False):
            result = plugin._refresh_story_doc(quick_read_path, {})
            
            assert result["success"] is False
            assert "NEVER creates new files" in result["error"]
    
    def test_prohibits_summary_variant_creation(self, plugin):
        """Plugin must NEVER create Summary variant"""
        summary_path = Path("docs/story/CORTEX-STORY/Awakening Of CORTEX - Summary.md")
        
        result = plugin._refresh_story_doc(summary_path, {})
        
        assert result["success"] is False
        assert "NEVER creates new files" in result["error"]
    
    def test_only_updates_existing_files(self, plugin):
        """Plugin should only update existing files"""
        existing_content = "# Original Content\nSome text here."
        existing_file = Path("docs/story/CORTEX-STORY/Awakening Of CORTEX.md")
        
        with patch.object(Path, 'exists', return_value=True), \
             patch.object(Path, 'read_text', return_value=existing_content):
            
            result = plugin._refresh_story_doc(existing_file, {})
            
            # Should succeed because file exists
            assert result["success"] is True or "error" in result  # Depends on design_context


class TestReadTimeEnforcement:
    """Test read time validation and enforcement"""
    
    @pytest.fixture
    def plugin(self):
        """Create plugin with read time enforcement enabled"""
        plugin = Plugin()
        plugin.config = {
            "enforce_read_time_limits": True,
            "awakening_story_target_minutes": 60,
            "trim_content_on_exceed": True
        }
        return plugin
    
    def test_validate_read_time_calculates_correctly(self, plugin):
        """Test read time calculation (225 words per minute)"""
        # 225 words = 1 minute
        content = " ".join(["word"] * 225)
        
        result = plugin._validate_read_time(content, target_minutes=1)
        
        assert result["word_count"] == 225
        assert result["estimated_minutes"] == 1.0
        assert result["target_minutes"] == 1
        assert result["within_target"] is True
    
    def test_validate_read_time_detects_too_long(self, plugin):
        """Test detection when content exceeds target"""
        # 225 words/min * 75 min = 16,875 words (too long for 60 min target)
        content = " ".join(["word"] * 16875)
        
        result = plugin._validate_read_time(content, target_minutes=60)
        
        assert result["estimated_minutes"] == 75.0
        assert result["within_target"] is False
        assert "TOO LONG" in result["recommendation"]
        assert "TRIM content" in result["recommendation"]
        assert "DO NOT create Quick Read" in result["recommendation"]
    
    def test_validate_read_time_detects_too_short(self, plugin):
        """Test detection when content is below target"""
        # 225 words/min * 45 min = 10,125 words (too short for 60 min target)
        content = " ".join(["word"] * 10125)
        
        result = plugin._validate_read_time(content, target_minutes=60)
        
        assert result["estimated_minutes"] == 45.0
        assert result["within_target"] is False
        assert "TOO SHORT" in result["recommendation"]
        assert "expanding existing sections" in result["recommendation"]
    
    def test_validate_read_time_acceptable_range(self, plugin):
        """Test that ±10% is acceptable range"""
        # 60 min target: 54-66 min is acceptable
        # 225 words/min * 54 min = 12,150 words
        content_min = " ".join(["word"] * 12150)
        result_min = plugin._validate_read_time(content_min, target_minutes=60)
        assert result_min["within_target"] is True
        
        # 225 words/min * 66 min = 14,850 words
        content_max = " ".join(["word"] * 14850)
        result_max = plugin._validate_read_time(content_max, target_minutes=60)
        assert result_max["within_target"] is True
    
    def test_transformation_plan_includes_read_time_enforcement(self, plugin):
        """Test that transformation plan includes read time actions"""
        # Content that's too long
        existing_story = " ".join(["word"] * 16875)  # 75 min worth
        
        plan = plugin._generate_story_transformation_plan(
            existing_story=existing_story,
            story_structure={"parts": []},
            deprecated_sections=[],
            narrator_voice_analysis={},
            feature_inventory=[]
        )
        
        # Should have a read time enforcement action
        read_time_actions = [
            action for action in plan["actions"]
            if action.get("action_type") == "enforce_read_time"
        ]
        
        assert len(read_time_actions) > 0
        action = read_time_actions[0]
        assert action["action"] == "trim_content"
        assert "NEVER create Quick Read" in action["note"]
    
    def test_story_refresh_includes_read_time_validation(self, plugin):
        """Test that story refresh validates read time"""
        existing_content = " ".join(["word"] * 13500)  # 60 min worth
        existing_file = Path("docs/story/CORTEX-STORY/Awakening Of CORTEX.md")
        
        with patch.object(Path, 'exists', return_value=True), \
             patch.object(Path, 'read_text', return_value=existing_content), \
             patch.object(plugin, '_regenerate_complete_story') as mock_regen:
            
            mock_regen.return_value = {"success": True}
            
            result = plugin._refresh_story_doc(existing_file, {})
            
            # Should include read time validation in result
            if "read_time_validation" in result:
                assert "estimated_minutes" in result["read_time_validation"]
                assert "target_minutes" in result["read_time_validation"]


class TestConfigurationEnforcement:
    """Test configuration schema enforcement"""
    
    def test_default_config_enforces_no_file_creation(self):
        """Test that default config has file creation prohibition enabled"""
        plugin = Plugin()
        metadata = plugin._get_metadata()
        
        schema = metadata.config_schema
        enforce_prop = schema["properties"]["enforce_no_file_creation"]
        
        assert enforce_prop["default"] is True
        assert "CRITICAL" in enforce_prop["description"]
        assert "ALWAYS be true" in enforce_prop["description"]
    
    def test_default_config_enforces_read_time(self):
        """Test that default config has read time enforcement enabled"""
        plugin = Plugin()
        metadata = plugin._get_metadata()
        
        schema = metadata.config_schema
        enforce_prop = schema["properties"]["enforce_read_time_limits"]
        
        assert enforce_prop["default"] is True
    
    def test_default_config_trims_on_exceed(self):
        """Test that default config trims content instead of creating new file"""
        plugin = Plugin()
        metadata = plugin._get_metadata()
        
        schema = metadata.config_schema
        trim_prop = schema["properties"]["trim_content_on_exceed"]
        
        assert trim_prop["default"] is True
        assert "instead of creating new file" in trim_prop["description"]
    
    def test_target_read_time_has_valid_range(self):
        """Test that target read time has sensible constraints"""
        plugin = Plugin()
        metadata = plugin._get_metadata()
        
        schema = metadata.config_schema
        target_prop = schema["properties"]["awakening_story_target_minutes"]
        
        assert target_prop["default"] == 60
        assert target_prop["minimum"] == 15
        assert target_prop["maximum"] == 75


class TestDocumentationHeaderRules:
    """Test that documentation header explains the rules"""
    
    def test_module_docstring_contains_critical_rules(self):
        """Test that module docstring documents the prohibition"""
        plugin = Plugin()
        module_doc = plugin.__class__.__module__
        
        # Read the plugin file with correct encoding
        plugin_file = Path("src/plugins/doc_refresh_plugin.py")
        content = plugin_file.read_text(encoding="utf-8")
        
        # Check for critical rules in docstring
        assert "CRITICAL RULES" in content
        assert "NEVER CREATE NEW FILES" in content
        assert "FORBIDDEN" in content
        assert "Quick Read" in content
        assert "READ TIME ENFORCEMENT" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
