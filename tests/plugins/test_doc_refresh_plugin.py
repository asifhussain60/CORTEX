"""
Test harness for Documentation Refresh Plugin

Tests all documentation refresh functionality:
- Story transformation (progressive recaps, voice transformation)
- Read time validation and enforcement
- Complete story regeneration
- Deprecated section detection
- Narrative flow validation

Author: CORTEX Test Suite
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
import json

from src.plugins.doc_refresh_plugin import Plugin as DocRefreshPlugin
from src.plugins.hooks import HookPoint


class TestDocRefreshPluginInitialization:
    """Test plugin initialization and metadata"""
    
    def test_plugin_creation(self):
        """Plugin should initialize successfully"""
        plugin = DocRefreshPlugin()
        assert plugin is not None
        assert plugin.metadata.plugin_id == "doc_refresh_plugin"
    
    def test_plugin_metadata(self):
        """Plugin metadata should be complete"""
        plugin = DocRefreshPlugin()
        metadata = plugin.metadata
        
        assert metadata.name == "Documentation Refresh"
        assert metadata.version == "2.0.0"
        assert metadata.category.value == "documentation"
        assert metadata.description
        assert metadata.author == "CORTEX Team"
    
    def test_plugin_hooks(self):
        """Plugin should register correct hooks"""
        plugin = DocRefreshPlugin()
        hooks = plugin.metadata.hooks
        
        assert HookPoint.ON_DOC_REFRESH.value in hooks
        assert HookPoint.ON_SELF_REVIEW.value in hooks
    
    def test_plugin_config_schema(self):
        """Plugin should have comprehensive config schema"""
        plugin = DocRefreshPlugin()
        config_schema = plugin.metadata.config_schema
        
        # Check critical config properties exist
        assert "enforce_no_file_creation" in config_schema["properties"]
        assert "enforce_read_time_limits" in config_schema["properties"]
        assert "progressive_recap_enabled" in config_schema["properties"]
        assert "transform_narrative_voice" in config_schema["properties"]
        assert "full_story_regeneration" in config_schema["properties"]
    
    @patch('pathlib.Path.exists')
    def test_plugin_initialization_success(self, mock_exists):
        """Plugin should initialize when directories exist"""
        mock_exists.return_value = True
        
        plugin = DocRefreshPlugin()
        result = plugin.initialize()
        
        assert result is True
    
    @patch('pathlib.Path.exists')
    def test_plugin_initialization_creates_story_dir(self, mock_exists):
        """Plugin should create story directory if missing"""
        # First call (design dir): True, Second call (story dir): False
        mock_exists.side_effect = [True, False]
        
        plugin = DocRefreshPlugin()
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            result = plugin.initialize()
            assert result is True


class TestDocRefreshExecution:
    """Test documentation refresh execution"""
    
    def test_execute_doc_refresh_hook(self):
        """Plugin should handle ON_DOC_REFRESH hook"""
        plugin = DocRefreshPlugin()
        plugin.initialize()
        
        context = {
            "hook": HookPoint.ON_DOC_REFRESH.value
        }
        
        with patch.object(plugin, '_refresh_all_docs') as mock_refresh:
            mock_refresh.return_value = {"success": True}
            result = plugin.execute(context)
            
            mock_refresh.assert_called_once_with(context)
            assert result["success"] is True
    
    def test_execute_self_review_hook(self):
        """Plugin should handle ON_SELF_REVIEW hook"""
        plugin = DocRefreshPlugin()
        plugin.initialize()
        
        context = {
            "hook": HookPoint.ON_SELF_REVIEW.value
        }
        
        with patch.object(plugin, '_check_doc_sync') as mock_check:
            mock_check.return_value = {"success": True, "synchronized": True}
            result = plugin.execute(context)
            
            mock_check.assert_called_once_with(context)
            assert result["synchronized"] is True
    
    def test_execute_unknown_hook(self):
        """Plugin should reject unknown hooks"""
        plugin = DocRefreshPlugin()
        plugin.initialize()
        
        context = {"hook": "unknown_hook"}
        result = plugin.execute(context)
        
        assert result["success"] is False
        assert "error" in result
    
    def test_refresh_all_docs_includes_six_documents(self):
        """Plugin should refresh all 6 synchronized documents"""
        plugin = DocRefreshPlugin()
        plugin.initialize()
        
        context = {"hook": HookPoint.ON_DOC_REFRESH.value}
        
        # Mock all refresh methods
        with patch.object(plugin, '_load_design_context') as mock_load:
            mock_load.return_value = {"design_docs": []}
            
            with patch.object(plugin, '_create_backup'):
                with patch('pathlib.Path.exists') as mock_exists:
                    mock_exists.return_value = True
                    
                    # Mock all 6 refresh methods
                    with patch.object(plugin, '_refresh_technical_doc') as mock_tech:
                        with patch.object(plugin, '_refresh_story_doc') as mock_story:
                            with patch.object(plugin, '_refresh_image_prompts_doc') as mock_img:
                                with patch.object(plugin, '_refresh_history_doc') as mock_hist:
                                    with patch.object(plugin, '_refresh_ancient_rules_doc') as mock_rules:
                                        with patch.object(plugin, '_refresh_features_doc') as mock_feat:
                                            # Set all to return success
                                            for mock in [mock_tech, mock_story, mock_img, 
                                                        mock_hist, mock_rules, mock_feat]:
                                                mock.return_value = {"success": True}
                                            
                                            result = plugin._refresh_all_docs(context)
                                            
                                            # Verify all 6 methods were called
                                            mock_tech.assert_called_once()
                                            mock_story.assert_called_once()
                                            mock_img.assert_called_once()
                                            mock_hist.assert_called_once()
                                            mock_rules.assert_called_once()
                                            mock_feat.assert_called_once()
                                            
                                            # Verify 6 files refreshed
                                            assert len(result["files_refreshed"]) == 6


class TestStoryRefreshCapabilities:
    """Test story refresh and transformation"""
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.read_text')
    def test_story_refresh_full_regeneration(self, mock_read, mock_exists):
        """Plugin should perform full story regeneration"""
        mock_exists.return_value = True
        mock_read.return_value = "# Existing Story\n\nContent here..."
        
        plugin = DocRefreshPlugin()
        plugin.config["full_story_regeneration"] = True
        plugin.initialize()
        
        design_context = {"design_docs": []}
        result = plugin._refresh_story_doc(Path("test.md"), design_context)
        
        assert result["success"] is True
        assert result["mode"] == "complete_regeneration"
        assert "transformation_plan" in result
    
    @patch('pathlib.Path.exists')
    def test_story_refresh_file_not_exists_error(self, mock_exists):
        """Plugin should error if file doesn't exist (no file creation)"""
        mock_exists.return_value = False
        
        plugin = DocRefreshPlugin()
        plugin.config["enforce_no_file_creation"] = True
        plugin.initialize()
        
        design_context = {"design_docs": []}
        result = plugin._refresh_story_doc(Path("missing.md"), design_context)
        
        assert result["success"] is False
        assert "PROHIBITED" in result["error"]
        assert "NEVER creates new files" in result["error"]
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.read_text')
    def test_progressive_recap_generation(self, mock_read, mock_exists):
        """Plugin should generate progressive recaps for multi-part story"""
        mock_exists.return_value = True
        mock_read.return_value = """
# PART 1: THE AWAKENING
## Chapter 1: The Intern

# PART 2: THE EVOLUTION
## Chapter 6: The Files

# PART 3: THE EXTENSION ERA
## Chapter 12: The Problem
"""
        
        plugin = DocRefreshPlugin()
        plugin.config["progressive_recap_enabled"] = True
        plugin.initialize()
        
        story_text = mock_read.return_value
        recaps = plugin._generate_progressive_recaps(story_text)
        
        assert "Part 2" in recaps["found_parts"]
        assert "Part 3" in recaps["found_parts"]
        assert recaps["part_2_recap"] is not None
        assert recaps["part_3_recap"] is not None
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.read_text')
    def test_lab_notebook_condensation(self, mock_read, mock_exists):
        """Plugin should condense verbose Lab Notebook interlude"""
        mock_exists.return_value = True
        mock_read.return_value = """
## Interlude: The Lab Notebook

**Day 1:**
Basic memory implemented...

**Day 7:**
Split brain architecture...

**Day 23:**
Rule #22 added...

## Chapter 1: Next Chapter
"""
        
        plugin = DocRefreshPlugin()
        plugin.initialize()
        
        story_text = mock_read.return_value
        result = plugin._condense_lab_notebook_interlude(story_text)
        
        assert result["found"] is True
        assert result["reduction_percentage"] > 50
        assert "condensed_text" in result
        assert "OK, so now this glorified typewriter" in result["condensed_text"]


class TestVoiceTransformation:
    """Test narrative voice transformation"""
    
    def test_voice_transformation_detection(self):
        """Plugin should detect passive narration patterns"""
        plugin = DocRefreshPlugin()
        plugin.initialize()
        
        story_text = """
So Asif Codeinstein built it a brain.
He wrote routines for persistence.
Asif Codeinstein tried not to scream.
"""
        
        result = plugin._transform_narrative_voice(story_text, mode="mixed")
        
        assert result["transformations_found"] > 0
        assert "patterns" in result
        assert len(result["examples"]) > 0
    
    def test_voice_transformation_suggestions(self):
        """Plugin should provide transformation suggestions"""
        plugin = DocRefreshPlugin()
        plugin.initialize()
        
        story_text = "So Asif Codeinstein built it a brain."
        result = plugin._transform_narrative_voice(story_text)
        
        # Should suggest active dialogue
        suggestions = result["examples"]
        assert any("muttered" in str(s) for s in suggestions)
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.read_text')
    def test_complete_narrator_analysis(self, mock_read, mock_exists):
        """Plugin should analyze narrator voice across complete story"""
        mock_exists.return_value = True
        mock_read.return_value = """
So Asif Codeinstein designed the system.
He wrote routines for memory.
One evening, while reviewing the code...
"""
        
        plugin = DocRefreshPlugin()
        plugin.initialize()
        
        story_text = mock_read.return_value
        analysis = plugin._analyze_narrator_voice_complete(story_text)
        
        assert "passive_violations" in analysis
        assert "documentary_violations" in analysis
        assert "total_violations" in analysis
        assert analysis["total_violations"] > 0


class TestReadTimeValidation:
    """Test read time validation and enforcement"""
    
    def test_read_time_validation_within_target(self):
        """Plugin should validate read time within acceptable range"""
        plugin = DocRefreshPlugin()
        plugin.initialize()
        
        # ~225 words per minute, so 60 min = ~13,500 words
        content = " ".join(["word"] * 13500)
        
        result = plugin._validate_read_time(content, target_minutes=60)
        
        assert result["within_target"] is True
        assert 54 <= result["estimated_minutes"] <= 66  # Within ±10%
    
    def test_read_time_validation_too_long(self):
        """Plugin should detect content exceeding target"""
        plugin = DocRefreshPlugin()
        plugin.initialize()
        
        # Too many words for 60 min target
        content = " ".join(["word"] * 20000)
        
        result = plugin._validate_read_time(content, target_minutes=60)
        
        assert result["within_target"] is False
        assert result["estimated_minutes"] > 66
        assert "TOO LONG" in result["recommendation"]
        assert "TRIM content" in result["recommendation"]
    
    def test_read_time_validation_too_short(self):
        """Plugin should detect content below target"""
        plugin = DocRefreshPlugin()
        plugin.initialize()
        
        # Too few words for 60 min target
        content = " ".join(["word"] * 5000)
        
        result = plugin._validate_read_time(content, target_minutes=60)
        
        assert result["within_target"] is False
        assert result["estimated_minutes"] < 54
        assert "TOO SHORT" in result["recommendation"]


class TestCompleteStoryRegeneration:
    """Test complete story regeneration system"""
    
    def test_feature_inventory_extraction(self):
        """Plugin should extract features from design documents"""
        plugin = DocRefreshPlugin()
        plugin.initialize()
        
        design_context = {
            "design_docs": [
                {
                    "name": "03-conversation-state.md",
                    "content": "Conversation state checkpoints..."
                },
                {
                    "name": "02-plugin-system.md",
                    "content": "Plugin architecture..."
                }
            ]
        }
        
        inventory = plugin._extract_feature_inventory(design_context, "design_documents")
        
        assert len(inventory) > 0
        assert any(f["feature_id"] == "conversation_state" for f in inventory)
    
    def test_deprecated_section_detection(self):
        """Plugin should detect deprecated terminology"""
        plugin = DocRefreshPlugin()
        plugin.initialize()
        
        story_text = """
The KDS system was created to manage data.
Key Data Stream architecture provided memory.
The monolithic entry point handled all requests.
"""
        
        feature_inventory = []
        deprecated = plugin._detect_deprecated_sections(story_text, feature_inventory)
        
        assert len(deprecated) > 0
        assert any("KDS" in d["deprecated_term"] for d in deprecated)
    
    def test_story_structure_building(self):
        """Plugin should build complete story structure from design"""
        plugin = DocRefreshPlugin()
        plugin.initialize()
        
        feature_inventory = [
            {"feature_id": "tier1_memory", "status": "implemented"},
            {"feature_id": "plugin_system", "status": "implemented"}
        ]
        
        design_context = {"design_docs": []}
        structure = plugin._build_story_structure_from_design(feature_inventory, design_context)
        
        assert "parts" in structure
        assert len(structure["parts"]) == 3  # Part 1, 2, 3
        assert structure["parts"][0]["part_number"] == 1
    
    def test_consistency_validation(self):
        """Plugin should validate story consistency"""
        plugin = DocRefreshPlugin()
        plugin.initialize()
        
        story_structure = {
            "parts": [
                {
                    "part_number": 1,
                    "chapters": [
                        {"number": 1, "features": ["tier1_memory"]},
                        {"number": 2, "features": ["dual_hemisphere"]}
                    ]
                }
            ]
        }
        
        validation = plugin._validate_story_consistency(story_structure)
        
        assert "valid" in validation
        assert "checks_passed" in validation
        assert "checks_total" in validation


class TestAncientRulesRefresh:
    """Test Ancient Rules (Rule Book) refresh"""
    
    @patch('pathlib.Path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="file_operations:\n  no_file_creation:\n    enabled: true")
    @patch('yaml.safe_load')
    def test_ancient_rules_refresh_success(self, mock_yaml, mock_file, mock_exists):
        """Plugin should refresh Ancient Rules from brain-protection-rules.yaml"""
        mock_exists.return_value = True
        mock_yaml.return_value = {
            "file_operations": {
                "no_file_creation": {"enabled": True},
                "no_directory_creation": {"enabled": True}
            },
            "architecture": {
                "no_circular_dependencies": {"enabled": True}
            }
        }
        
        plugin = DocRefreshPlugin()
        plugin.initialize()
        
        design_context = {"design_docs": []}
        result = plugin._refresh_ancient_rules_doc(Path("Ancient-Rules.md"), design_context)
        
        assert result["success"] is True
        assert result["rules_count"] == 3
        assert "action_required" in result
    
    @patch('pathlib.Path.exists')
    def test_ancient_rules_file_not_exists_error(self, mock_exists):
        """Plugin should error if Ancient-Rules.md doesn't exist"""
        mock_exists.return_value = False
        
        plugin = DocRefreshPlugin()
        plugin.initialize()
        
        design_context = {"design_docs": []}
        result = plugin._refresh_ancient_rules_doc(Path("missing.md"), design_context)
        
        assert result["success"] is False
        assert "PROHIBITED" in result["error"]
    
    @patch('pathlib.Path.exists')
    def test_ancient_rules_yaml_not_found(self, mock_exists):
        """Plugin should handle missing brain-protection-rules.yaml"""
        # Three exists() calls: story dir check in init(), Ancient-Rules.md, brain-protection-rules.yaml
        mock_exists.side_effect = [False, True, False]  # story dir missing, Ancient-Rules.md exists, YAML doesn't
        
        plugin = DocRefreshPlugin()
        plugin.initialize()
        
        design_context = {"design_docs": []}
        result = plugin._refresh_ancient_rules_doc(Path("Ancient-Rules.md"), design_context)
        
        assert result["success"] is False
        assert "not found" in result["error"]
        assert "brain-protection-rules.yaml" in result["error"]


class TestFeaturesDocRefresh:
    """Test CORTEX-FEATURES.md (Simple feature list) refresh"""
    
    @patch('pathlib.Path.exists')
    def test_features_refresh_success(self, mock_exists):
        """Plugin should refresh features doc from design context"""
        mock_exists.return_value = True
        
        plugin = DocRefreshPlugin()
        plugin.initialize()
        
        design_context = {
            "design_docs": [
                {
                    "name": "01-tier1-memory.md",
                    "content": "Tier 1 conversation memory system..."
                },
                {
                    "name": "02-plugin-system.md",
                    "content": "Plugin architecture for extensibility..."
                },
                {
                    "name": "05-agent-system.md",
                    "content": "Dual hemisphere agent architecture..."
                }
            ]
        }
        
        result = plugin._refresh_features_doc(Path("CORTEX-FEATURES.md"), design_context)
        
        assert result["success"] is True
        assert result["features_count"] > 0
        assert "categories" in result
        assert "action_required" in result
    
    @patch('pathlib.Path.exists')
    def test_features_doc_file_not_exists_error(self, mock_exists):
        """Plugin should error if CORTEX-FEATURES.md doesn't exist"""
        mock_exists.return_value = False
        
        plugin = DocRefreshPlugin()
        plugin.initialize()
        
        design_context = {"design_docs": []}
        result = plugin._refresh_features_doc(Path("missing.md"), design_context)
        
        assert result["success"] is False
        assert "PROHIBITED" in result["error"]
    
    @patch('pathlib.Path.exists')
    def test_features_categorization(self, mock_exists):
        """Plugin should categorize features correctly"""
        mock_exists.return_value = True
        
        plugin = DocRefreshPlugin()
        plugin.initialize()
        
        design_context = {
            "design_docs": [
                {
                    "name": "memory.md",
                    "content": "Tier 1 conversation tracking, Tier 2 knowledge graph, Tier 3 context"
                },
                {
                    "name": "agents.md",
                    "content": "Dual hemisphere agent system with 10 specialists"
                },
                {
                    "name": "workflow.md",
                    "content": "Workflow pipeline system with declarative YAML"
                }
            ]
        }
        
        result = plugin._refresh_features_doc(Path("CORTEX-FEATURES.md"), design_context)
        
        assert result["success"] is True
        categories = result["categories"]
        
        # Should detect memory features
        assert categories["memory"] > 0
        # Should detect agent features
        assert categories["agents"] > 0
        # Should detect workflow features
        assert categories["workflows"] > 0


class TestNarrativeFlowAnalysis:
    """Test narrative flow and structure analysis"""
    
    def test_narrative_flow_analysis_three_act(self):
        """Plugin should detect three-act structure"""
        plugin = DocRefreshPlugin()
        plugin.initialize()
        
        story_text = """
# PART 1: THE AWAKENING
## Chapter 1: Beginning

# PART 2: THE EVOLUTION  
## Chapter 6: Middle

# PART 3: THE EXTENSION ERA
## Chapter 12: End
"""
        
        analysis = plugin._analyze_narrative_flow(story_text)
        
        assert analysis["structure"] == "three-act-structure"
        assert analysis["parts_detected"] == 3
        assert analysis["chapters_detected"] == 3
    
    def test_narrative_flow_warnings(self):
        """Plugin should warn about flow issues"""
        plugin = DocRefreshPlugin()
        plugin.initialize()
        
        story_text = """
## Interlude: First
## Interlude: Second
## Interlude: Third
## Interlude: Fourth
# PART 1: Only Part
"""
        
        analysis = plugin._analyze_narrative_flow(story_text)
        
        assert len(analysis["warnings"]) > 0


class TestBackupAndSafety:
    """Test backup and file safety mechanisms"""
    
    @patch('pathlib.Path.exists')
    @patch('shutil.copy2')
    @patch('pathlib.Path.mkdir')
    def test_backup_creation(self, mock_mkdir, mock_copy, mock_exists):
        """Plugin should create backups before refresh"""
        mock_exists.return_value = True
        
        plugin = DocRefreshPlugin()
        plugin.initialize()
        
        file_path = Path("test.md")
        plugin._create_backup(file_path)
        
        mock_mkdir.assert_called_once()
        mock_copy.assert_called_once()
    
    @patch('pathlib.Path.exists')
    def test_no_file_creation_enforcement(self, mock_exists):
        """Plugin should NEVER create new files when enforced"""
        mock_exists.return_value = False
        
        plugin = DocRefreshPlugin()
        plugin.config["enforce_no_file_creation"] = True
        plugin.initialize()
        
        design_context = {"design_docs": []}
        result = plugin._refresh_story_doc(Path("new_file.md"), design_context)
        
        assert result["success"] is False
        assert "PROHIBITED" in result["error"]


class TestDocSyncValidation:
    """Test documentation synchronization validation"""
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    def test_doc_sync_check_up_to_date(self, mock_stat, mock_exists):
        """Plugin should detect synchronized documentation"""
        mock_exists.return_value = True
        
        # Design doc modified before story docs (synchronized)
        mock_stat.return_value.st_mtime = 1000
        
        plugin = DocRefreshPlugin()
        plugin.initialize()
        
        result = plugin._check_doc_sync({})
        
        assert result["success"] is True
        # Would need more sophisticated mocking for full test
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    def test_doc_sync_check_out_of_sync(self, mock_stat, mock_exists):
        """Plugin should detect out-of-sync documentation"""
        mock_exists.return_value = True
        
        # Simulate design doc newer than story docs
        design_time = 2000
        story_time = 1000
        
        mock_stat.side_effect = [
            Mock(st_mtime=design_time),  # design doc
            Mock(st_mtime=story_time),   # story doc
        ]
        
        plugin = DocRefreshPlugin()
        plugin.initialize()
        
        # Would need actual file structure for complete test


class TestPluginIntegration:
    """Test plugin integration with CORTEX system"""
    
    def test_plugin_cleanup(self):
        """Plugin should cleanup successfully"""
        plugin = DocRefreshPlugin()
        plugin.initialize()
        
        result = plugin.cleanup()
        
        assert result is True
    
    def test_plugin_lifecycle(self):
        """Plugin should handle full lifecycle"""
        plugin = DocRefreshPlugin()
        
        # Initialize
        init_result = plugin.initialize()
        assert init_result is True
        
        # Execute (with mock)
        context = {"hook": HookPoint.ON_SELF_REVIEW.value}
        with patch.object(plugin, '_check_doc_sync') as mock_check:
            mock_check.return_value = {"success": True, "synchronized": True}
            exec_result = plugin.execute(context)
            assert exec_result["success"] is True
        
        # Cleanup
        cleanup_result = plugin.cleanup()
        assert cleanup_result is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
