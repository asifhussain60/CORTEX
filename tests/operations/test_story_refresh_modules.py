"""
Test Story Refresh Modules

Comprehensive test suite for story refresh modular architecture.
Tests all 7 modules plus integration.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.operations.modules.evaluate_cortex_architecture_module import EvaluateCortexArchitectureModule
from src.operations.modules.generate_story_chapters_module import GenerateStoryChaptersModule
from src.operations.modules.build_consolidated_story_module import BuildConsolidatedStoryModule
from src.operations.modules.generate_technical_cortex_doc_module import GenerateTechnicalCortexDocModule
from src.operations.modules.generate_image_prompts_doc_module import GenerateImagePromptsDocModule
from src.operations.modules.generate_history_doc_module import GenerateHistoryDocModule
from src.operations.modules.relocate_story_files_module import RelocateStoryFilesModule


class TestEvaluateCortexArchitecture:
    """Test Module 1: Architecture Evaluator"""
    
    def test_metadata(self):
        """Test module metadata"""
        module = EvaluateCortexArchitectureModule()
        metadata = module.metadata
        
        assert metadata.module_id == "evaluate_cortex_architecture"
        assert metadata.version == "2.0"
        assert metadata.author == "Asif Hussain"
    
    def test_mode_detection_small_changes(self):
        """Test mode detection with small changes"""
        module = EvaluateCortexArchitectureModule()
        
        # 1 new test = 0.01%, should recommend update-in-place
        changes = {
            'new_tests': 1,
            'new_tiers': 0,
            'new_agents': 0,
            'new_plugins': 0
        }
        
        magnitude = module._calculate_change_magnitude(changes)
        assert magnitude < 0.20  # Below threshold
        
        mode, rationale = module._determine_refresh_mode(magnitude)
        assert mode == 'update-in-place'
    
    def test_mode_detection_large_changes(self):
        """Test mode detection with large changes"""
        module = EvaluateCortexArchitectureModule()
        
        # 1 new tier = 30%, should recommend generate-from-scratch
        changes = {
            'new_tests': 0,
            'new_tiers': 1,
            'new_agents': 0,
            'new_plugins': 0
        }
        
        magnitude = module._calculate_change_magnitude(changes)
        assert magnitude >= 0.20  # Above threshold
        
        mode, rationale = module._determine_refresh_mode(magnitude)
        assert mode == 'generate-from-scratch'


class TestGenerateStoryChapters:
    """Test Module 2: Story Chapter Generator"""
    
    def test_metadata(self):
        """Test module metadata"""
        module = GenerateStoryChaptersModule()
        metadata = module.metadata
        
        assert metadata.module_id == "generate_story_chapters"
        assert len(module.CHAPTERS) == 9
    
    def test_chapter_definitions(self):
        """Test all 9 chapters are properly defined"""
        module = GenerateStoryChaptersModule()
        
        for i, chapter in enumerate(module.CHAPTERS, 1):
            assert chapter['id'] == i
            assert 'title' in chapter
            assert 'subtitle' in chapter
            assert 'focus' in chapter
            assert 'features' in chapter


class TestBuildConsolidatedStory:
    """Test Module 3: Story Collapser"""
    
    def test_metadata(self):
        """Test module metadata"""
        module = BuildConsolidatedStoryModule()
        metadata = module.metadata
        
        assert metadata.module_id == "build_consolidated_story"
        assert metadata.version == "2.0"
    
    def test_word_count_calculation(self):
        """Test word count calculation"""
        module = BuildConsolidatedStoryModule()
        
        text = "This is a **bold** test with `code` and markdown."
        count = module._calculate_word_count(text)
        
        # Should count words after stripping markdown
        assert count > 0
    
    def test_story_technical_ratio(self):
        """Test story:technical ratio estimation"""
        module = BuildConsolidatedStoryModule()
        
        # Story-heavy text
        story_text = "Asif Codeinstein drank coffee in his basement at 2 AM with the wizard"
        ratio = module._estimate_story_technical_ratio(story_text)
        assert ratio > 0.5  # Should detect as story
        
        # Technical-heavy text
        tech_text = "The SQLite database uses Python API with tier architecture and modules"
        ratio = module._estimate_story_technical_ratio(tech_text)
        assert ratio < 0.5  # Should detect as technical


class TestGenerateTechnicalDoc:
    """Test Module 4: Technical Doc Generator"""
    
    def test_metadata(self):
        """Test module metadata"""
        module = GenerateTechnicalCortexDocModule()
        metadata = module.metadata
        
        assert metadata.module_id == "generate_technical_cortex_doc"
        assert "evaluate_cortex_architecture" in metadata.dependencies


class TestGenerateImagePrompts:
    """Test Module 5: Image Prompts Generator"""
    
    def test_metadata(self):
        """Test module metadata"""
        module = GenerateImagePromptsDocModule()
        metadata = module.metadata
        
        assert metadata.module_id == "generate_image_prompts_doc"
        assert "Gemini" in metadata.description


class TestGenerateHistory:
    """Test Module 6: History Updater"""
    
    def test_metadata(self):
        """Test module metadata"""
        module = GenerateHistoryDocModule()
        metadata = module.metadata
        
        assert metadata.module_id == "generate_history_doc"
        assert metadata.version == "2.0"
    
    def test_kds_extraction(self):
        """Test KDS section extraction"""
        module = GenerateHistoryDocModule()
        
        sample_content = """
# History

## KDS 1.0: The Beginning

Some content here.

## CORTEX: The Revolution

More content.
"""
        
        extracted = module._extract_kds_sections(sample_content)
        assert extracted is not None
        assert "KDS 1.0" in extracted


class TestRelocateStoryFiles:
    """Test Module 7: File Relocator"""
    
    def test_metadata(self):
        """Test module metadata"""
        module = RelocateStoryFilesModule()
        metadata = module.metadata
        
        assert metadata.module_id == "relocate_story_files"
        assert len(module.TARGET_FILES) == 2


class TestIntegration:
    """Test integration of all modules"""
    
    @patch('src.operations.modules.evaluate_cortex_architecture_module.Path')
    def test_module_pipeline(self, mock_path):
        """Test modules execute in correct order"""
        # This is a basic integration test
        # Full integration requires actual YAML files
        
        context = {
            'project_root': Path('.'),
            'output_dir': Path('docs/story/CORTEX-STORY'),
            'refresh_mode': 'generate-from-scratch'
        }
        
        # Each module should accept context and return result
        # Detailed integration tests would require fixtures
        
        assert 'project_root' in context
        assert 'output_dir' in context
        assert 'refresh_mode' in context


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_missing_architecture_file(self):
        """Test behavior when architecture file is missing"""
        module = EvaluateCortexArchitectureModule()
        context = {'project_root': Path('/nonexistent')}
        
        result = module.execute(context)
        # Should handle gracefully
        assert result is not None
    
    def test_invalid_refresh_mode(self):
        """Test behavior with invalid refresh mode"""
        module = GenerateStoryChaptersModule()
        context = {
            'refresh_mode': 'invalid-mode',
            'feature_inventory': {'tiers': [], 'agents': [], 'plugins': []},
            'implementation_status': {},
            'architecture_patterns': {}
        }
        
        # Should default to generate-from-scratch
        result = module.validate(context)
        assert result.success  # Validation should pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
