"""
Unit Tests for Modular Template System
Tests all core components, blocks, and orchestrator-specific templates
"""

import pytest
from pathlib import Path
import yaml
from src.response_templates.template_loader_v5 import (
    ModularTemplateLoader,
    IncludeLoader,
    load_template_with_includes
)


# Test fixtures
@pytest.fixture
def template_base_path():
    """Base path for response templates"""
    return Path(__file__).parent.parent / "cortex-brain" / "response-templates"


@pytest.fixture
def loader(template_base_path):
    """ModularTemplateLoader instance"""
    return ModularTemplateLoader(template_base_path)


# ============================================================================
# Core Component Tests
# ============================================================================

class TestCoreComponents:
    """Tests for Tier 1 core components"""
    
    def test_progress_bar_config_structure(self, loader):
        """Test progress-bar-config.yaml structure"""
        config = loader.load_core_component("progress-bar-config")
        
        assert "progress_bar" in config
        assert config["progress_bar"]["width"] == 10
        assert config["progress_bar"]["filled_char"] == "█"
        assert config["progress_bar"]["empty_char"] == "░"
        
        # Test icons
        icons = config["progress_bar"]["icons"]
        assert icons["complete"] == "✅"
        assert icons["in_progress"] == "🔄"
        assert icons["pending"] == "⏳"
        assert icons["failed"] == "❌"
        assert icons["skipped"] == "⏸️"
    
    def test_status_indicators_structure(self, loader):
        """Test status-indicators.yaml structure"""
        indicators = loader.load_core_component("status-indicators")
        
        assert "status_icons" in indicators
        assert indicators["status_icons"]["success"] == "✅"
        assert indicators["status_icons"]["failed"] == "❌"
        assert indicators["status_icons"]["warning"] == "⚠️"
        
        # Test orchestrator icons
        assert "orchestrator_icons" in indicators
        assert indicators["orchestrator_icons"]["planning"] == "🛡️"
        assert indicators["orchestrator_icons"]["tdd"] == "🔬"
    
    def test_formatting_library_structure(self, loader):
        """Test formatting-library.yaml structure"""
        formatting = loader.load_core_component("formatting-library")
        
        assert "patterns" in formatting
        assert "lists" in formatting
        assert "visual_progress" in formatting
        assert "branding" in formatting
        
        # Test specific patterns
        assert "file_link" in formatting["patterns"]
        assert "code_block" in formatting["patterns"]
        assert "metric" in formatting["patterns"]
    
    def test_section_library_structure(self, loader):
        """Test section-library.yaml structure"""
        sections = loader.load_core_component("section-library")
        
        assert "sections" in sections
        
        # Test key sections exist
        required_sections = [
            "understanding", "approach", "response", "changes", 
            "next_steps", "context", "analysis"
        ]
        for section in required_sections:
            assert section in sections["sections"]
            section_data = sections["sections"][section]
            assert "emoji" in section_data
            assert "title" in section_data
            assert "when_to_use" in section_data
            assert "content_guidelines" in section_data
    
    def test_template_renderer_api_structure(self, loader):
        """Test template-renderer-api.yaml structure"""
        api = loader.load_core_component("template-renderer-api")
        
        assert "implementation_helpers" in api
        assert "progress_helpers" in api
        
        # Test helper methods exist
        helpers = api["implementation_helpers"]
        assert "methods" in helpers
        assert "select_blocks" in helpers["methods"]
        assert "generate_progress_bar" in helpers["methods"]


# ============================================================================
# Standard Block Tests
# ============================================================================

class TestStandardBlocks:
    """Tests for Tier 2 standard blocks"""
    
    def test_headers_structure(self, loader):
        """Test headers.yaml structure"""
        headers = loader.load_block("headers")
        
        assert "cortex_header" in headers
        assert "cortex_header_shield" in headers
        
        # Test block IDs
        assert headers["cortex_header"]["block_id"] == "BLK-STD-001"
        assert headers["cortex_header_shield"]["block_id"] == "BLK-STD-002"
    
    def test_validation_status_structure(self, loader):
        """Test validation-status.yaml structure"""
        validation = loader.load_block("validation-status")
        
        assert "validation_status_dor_dod" in validation
        assert validation["validation_status_dor_dod"]["block_id"] == "BLK-STD-004"
    
    def test_phase_progress_table_structure(self, loader):
        """Test phase-progress-table.yaml structure"""
        progress = loader.load_block("phase-progress-table")
        
        assert "progress_tracker_standard" in progress
        assert progress["progress_tracker_standard"]["block_id"] == "BLK-STD-006"
        
        # Test config
        config = progress["progress_tracker_standard"]["config"]
        assert config["bar_width"] == 10
        assert config["filled_char"] == "█"
    
    def test_plan_file_link_structure(self, loader):
        """Test plan-file-link.yaml structure"""
        links = loader.load_block("plan-file-link")
        
        assert "plan_file_link" in links
        assert links["plan_file_link"]["block_id"] == "BLK-STD-008"
    
    def test_next_action_structure(self, loader):
        """Test next-action.yaml structure"""
        action = loader.load_block("next-action")
        
        assert "next_action" in action
        assert action["next_action"]["block_id"] == "BLK-STD-011"
        
        # Test SKULL rule enforcement
        rules = action["next_action"]["rules"]
        assert "EXACTLY ONE action per response" in rules
    
    def test_progress_bar_inline_structure(self, loader):
        """Test progress-bar-inline.yaml structure"""
        bar = loader.load_block("progress-bar-inline")
        
        assert "progress_bar_inline" in bar
        assert bar["progress_bar_inline"]["block_id"] == "BLK-STD-014"


# ============================================================================
# Orchestrator Block Tests
# ============================================================================

class TestOrchestratorBlocks:
    """Tests for Tier 3 orchestrator-specific blocks"""
    
    def test_planning_threat_analysis(self, loader):
        """Test planning/threat-analysis.yaml"""
        threat = loader.load_orchestrator_block("planning", "threat-analysis")
        
        assert "threat_analysis" in threat
        assert threat["threat_analysis"]["block_id"] == "BLK-PLN-001"
        assert threat["orchestrator"] == "planning"  # Check root level
    
    def test_planning_plan_summary(self, loader):
        """Test planning/plan-summary.yaml"""
        summary = loader.load_orchestrator_block("planning", "plan-summary")
        
        assert "plan_summary_table" in summary
        assert summary["plan_summary_table"]["block_id"] == "BLK-PLN-002"
    
    def test_ado_work_item_summary(self, loader):
        """Test ado/work-item-summary.yaml"""
        work_items = loader.load_orchestrator_block("ado", "work-item-summary")
        
        assert "work_item_summary" in work_items
        assert work_items["work_item_summary"]["block_id"] == "BLK-ADO-001"
        assert work_items["orchestrator"] == "ado"  # Check root level
    
    def test_tdd_cycle_status(self, loader):
        """Test tdd/tdd-cycle-status.yaml"""
        tdd = loader.load_orchestrator_block("tdd", "tdd-cycle-status")
        
        assert "tdd_cycle_status" in tdd
        assert tdd["tdd_cycle_status"]["block_id"] == "BLK-TDD-001"
        assert tdd["orchestrator"] == "tdd"  # Check root level
    
    def test_tdd_test_results(self, loader):
        """Test tdd/test-results.yaml"""
        results = loader.load_orchestrator_block("tdd", "test-results")
        
        assert "test_results_summary" in results
        assert results["test_results_summary"]["block_id"] == "BLK-TDD-002"
    
    def test_debug_bug_hypothesis(self, loader):
        """Test debug/bug-hypothesis.yaml"""
        debug = loader.load_orchestrator_block("debug", "bug-hypothesis")
        
        assert "bug_hypothesis" in debug
        assert debug["bug_hypothesis"]["block_id"] == "BLK-DBG-001"
    
    def test_lens_analytics_summary(self, loader):
        """Test lens/analytics-summary.yaml"""
        lens = loader.load_orchestrator_block("lens", "analytics-summary")
        
        assert "analytics_summary" in lens
        assert lens["analytics_summary"]["block_id"] == "BLK-LNS-001"
    
    def test_refinement_improvement_areas(self, loader):
        """Test refinement/improvement-areas.yaml"""
        refinement = loader.load_orchestrator_block("refinement", "improvement-areas")
        
        assert "improvement_areas" in refinement
        assert refinement["improvement_areas"]["block_id"] == "BLK-RFN-001"
    
    def test_sanitization_findings(self, loader):
        """Test sanitization/sanitization-findings.yaml"""
        sanitization = loader.load_orchestrator_block("sanitization", "sanitization-findings")
        
        assert "sanitization_findings" in sanitization
        assert sanitization["sanitization_findings"]["block_id"] == "BLK-SNT-001"
    
    def test_documentation_doc_summary(self, loader):
        """Test documentation/doc-summary.yaml"""
        docs = loader.load_orchestrator_block("documentation", "doc-summary")
        
        assert "doc_summary" in docs
        assert docs["doc_summary"]["block_id"] == "BLK-DOC-001"


# ============================================================================
# Loader Functionality Tests
# ============================================================================

class TestLoaderFunctionality:
    """Tests for ModularTemplateLoader functionality"""
    
    def test_cache_functionality(self, loader):
        """Test template caching works"""
        # First load
        config1 = loader.load_core_component("progress-bar-config")
        stats1 = loader.get_cache_stats()
        
        # Second load (should use cache)
        config2 = loader.load_core_component("progress-bar-config")
        stats2 = loader.get_cache_stats()
        
        assert config1 == config2
        assert stats2["cached_files"] >= stats1["cached_files"]
    
    def test_cache_disable(self, loader):
        """Test cache can be disabled"""
        loader.disable_cache()
        stats = loader.get_cache_stats()
        
        assert stats["cache_enabled"] is False
        assert stats["cached_files"] == 0
    
    def test_cache_clear(self, loader):
        """Test cache can be cleared"""
        # Load some templates
        loader.load_core_component("progress-bar-config")
        loader.load_block("headers")
        
        # Clear cache
        loader.clear_cache()
        stats = loader.get_cache_stats()
        
        assert stats["cached_files"] == 0
    
    def test_file_not_found_error(self, loader):
        """Test appropriate error for missing files"""
        with pytest.raises(FileNotFoundError):
            loader.load_core_component("nonexistent-file")


# ============================================================================
# Integration Tests
# ============================================================================

class TestTemplateIntegration:
    """Integration tests for template composition"""
    
    def test_all_core_components_loadable(self, loader):
        """Test all core components can be loaded"""
        core_files = [
            "progress-bar-config",
            "status-indicators",
            "formatting-library",
            "section-library",
            "template-renderer-api"
        ]
        
        for component in core_files:
            data = loader.load_core_component(component)
            assert data is not None
            assert isinstance(data, dict)
    
    def test_all_standard_blocks_loadable(self, loader):
        """Test all standard blocks can be loaded"""
        block_files = [
            "headers",
            "validation-status",
            "phase-progress-table",
            "plan-file-link",
            "next-action",
            "progress-bar-inline",
            "section-wrappers"
        ]
        
        for block in block_files:
            data = loader.load_block(block)
            assert data is not None
            assert isinstance(data, dict)
    
    def test_all_orchestrator_blocks_loadable(self, loader):
        """Test all orchestrator blocks can be loaded"""
        orchestrator_blocks = [
            ("planning", "threat-analysis"),
            ("planning", "plan-summary"),
            ("planning", "plan-structure"),
            ("planning", "deliverables-matrix"),
            ("ado", "work-item-summary"),
            ("ado", "ado-links"),
            ("ado", "story-points-breakdown"),
            ("tdd", "tdd-cycle-status"),
            ("tdd", "test-results"),
            ("tdd", "coverage-metrics"),
            ("debug", "bug-hypothesis"),
            ("debug", "root-cause-analysis"),
            ("debug", "fix-verification"),
            ("lens", "analytics-summary"),
            ("lens", "health-metrics"),
            ("lens", "system-recommendations"),
            ("refinement", "improvement-areas"),
            ("refinement", "code-quality-delta"),
            ("sanitization", "sanitization-findings"),
            ("documentation", "doc-summary"),
            ("documentation", "coverage-report")
        ]
        
        for orchestrator, block in orchestrator_blocks:
            data = loader.load_orchestrator_block(orchestrator, block)
            assert data is not None
            assert isinstance(data, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
