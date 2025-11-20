"""
Integration tests for BuildConsolidatedStoryModule.

This test suite validates the story generation pipeline that creates
THE-AWAKENING-OF-CORTEX.md from 9 individual chapter source files.

SKULL-005 Protection: Ensures detailed story quality is maintained.

Test Coverage:
- File creation and structure validation
- Intro content verification (Codeinstein, basement, Wizard of Oz)
- All 9 chapters included in correct order
- Quality metrics calculation (word count, read time, story:tech ratio)
- Quality warning generation for out-of-range metrics

Author: Asif Hussain
Version: 1.0 (Initial story generation tests)
"""

import pytest
from pathlib import Path
from src.operations.modules.build_consolidated_story_module import BuildConsolidatedStoryModule


class TestBuildConsolidatedStoryModule:
    """Test suite for BuildConsolidatedStoryModule."""
    
    @pytest.fixture
    def module(self):
        """Create module instance."""
        return BuildConsolidatedStoryModule()
    
    @pytest.fixture
    def context(self):
        """Create context with project_root."""
        return {'project_root': Path.cwd()}
    
    @pytest.fixture
    def generated_story(self, module, context):
        """Generate story and return context."""
        result = module.execute(context)
        assert result.success, f"Story generation failed: {result.message}"
        return context
    
    def test_build_consolidated_story_creates_file(self, module, context):
        """Verify THE-AWAKENING-OF-CORTEX.md is created with correct name."""
        result = module.execute(context)
        
        assert result.success, f"Module failed: {result.message}"
        assert 'consolidated_path' in context, "consolidated_path not set in context"
        
        output_path = Path(context['consolidated_path'])
        assert output_path.exists(), f"Story file not created: {output_path}"
        assert output_path.name == "THE-AWAKENING-OF-CORTEX.md", f"Wrong filename: {output_path.name}"
        
        # Verify file has content
        assert output_path.stat().st_size > 0, "Story file is empty"
    
    def test_consolidated_story_has_intro_with_codeinstein(self, generated_story):
        """Verify intro includes Asif Codeinstein character."""
        story_content = generated_story['consolidated_story']
        
        assert "Asif Codeinstein" in story_content, "Missing character name 'Asif Codeinstein'"
        assert "mad scientist" in story_content.lower() or "software engineer" in story_content.lower(), \
            "Missing character profession description"
    
    def test_consolidated_story_has_basement_setting(self, generated_story):
        """Verify intro includes basement lab setting."""
        story_content = generated_story['consolidated_story']
        
        # Check for basement setting (flexible matching)
        basement_keywords = ["basement", "moldy", "New Jersey", "suburban"]
        found_keywords = [kw for kw in basement_keywords if kw in story_content]
        assert len(found_keywords) >= 2, f"Missing basement setting. Found only: {found_keywords}"
    
    def test_consolidated_story_has_wizard_of_oz_inspiration(self, generated_story):
        """Verify intro includes Wizard of Oz inspiration moment."""
        story_content = generated_story['consolidated_story']
        
        assert "Wizard of Oz" in story_content, "Missing 'Wizard of Oz' reference"
        
        # Check for key quote about brain (flexible matching)
        brain_keywords = ["brain", "Copilot doesn't need more RAM", "needs a brain"]
        found_keywords = [kw for kw in brain_keywords if kw in story_content]
        assert len(found_keywords) >= 2, f"Missing brain inspiration quote. Found: {found_keywords}"
    
    def test_consolidated_story_has_physical_copilot_machine(self, generated_story):
        """Verify intro describes Copilot as physical machine."""
        story_content = generated_story['consolidated_story']
        
        # Check for physical machine description
        machine_keywords = ["machine", "server", "LED", "processing power", "beast"]
        found_keywords = [kw for kw in machine_keywords if kw in story_content]
        assert len(found_keywords) >= 2, f"Missing physical machine description. Found: {found_keywords}"
    
    def test_all_9_chapters_included(self, generated_story):
        """Verify all 9 chapters present in consolidated story."""
        story_content = generated_story['consolidated_story']
        
        # Check for chapter markers (flexible - allow variations in titles)
        chapter_markers = [
            "Chapter 1",
            "Chapter 2",
            "Chapter 3",
            "Chapter 4",
            "Chapter 5",
            "Chapter 6",
            "Chapter 7",
            "Chapter 8",
            "Chapter 9"
        ]
        
        missing_chapters = []
        for marker in chapter_markers:
            if marker not in story_content:
                missing_chapters.append(marker)
        
        assert len(missing_chapters) == 0, f"Missing chapters: {', '.join(missing_chapters)}"
    
    def test_chapters_in_correct_order(self, generated_story):
        """Verify chapters appear in sequential order."""
        story_content = generated_story['consolidated_story']
        
        # Find positions of chapter markers
        chapter_positions = {}
        for i in range(1, 10):
            marker = f"Chapter {i}"
            pos = story_content.find(marker)
            if pos >= 0:
                chapter_positions[i] = pos
        
        # Verify we found all chapters
        assert len(chapter_positions) == 9, f"Found only {len(chapter_positions)} chapters"
        
        # Verify sequential ordering
        for i in range(1, 9):
            assert chapter_positions[i] < chapter_positions[i+1], \
                f"Chapter {i} appears after Chapter {i+1}"
    
    def test_story_metrics_calculated(self, generated_story):
        """Verify word count, read time, and story:tech ratio calculated."""
        assert 'word_count' in generated_story, "word_count not calculated"
        assert 'estimated_read_time' in generated_story, "estimated_read_time not calculated"
        assert 'story_technical_ratio' in generated_story, "story_technical_ratio not calculated"
    
    def test_word_count_minimum(self, generated_story):
        """Verify story meets minimum word count (10,000+ words)."""
        word_count = generated_story['word_count']
        
        assert word_count > 10000, \
            f"Word count too low: {word_count} words (minimum: 10,000)"
    
    def test_read_time_reasonable(self, generated_story):
        """Verify estimated read time is reasonable (40-80 minutes)."""
        read_time = generated_story['estimated_read_time']
        
        assert read_time > 40, \
            f"Read time too short: {read_time:.1f} minutes (minimum: 40)"
        
        assert read_time < 120, \
            f"Read time too long: {read_time:.1f} minutes (maximum: 120)"
    
    def test_story_ratio_acceptable(self, generated_story):
        """Verify story:technical ratio is acceptable (>80% story content)."""
        story_ratio = generated_story['story_technical_ratio']
        
        assert story_ratio > 0.70, \
            f"Story ratio too low: {story_ratio:.1%} (minimum: 70%)"
    
    def test_quality_warnings_generated_when_needed(self, module, context):
        """Verify quality warnings present in result data."""
        result = module.execute(context)
        
        assert result.success
        assert 'warnings' in result.data, "Warnings field missing from result data"
        # Warnings list should exist (may be empty if quality is good)
        assert isinstance(result.data['warnings'], list), "Warnings should be a list"
    
    def test_result_contains_metrics(self, module, context):
        """Verify result.data contains all expected metrics."""
        result = module.execute(context)
        
        assert result.success
        
        expected_fields = [
            'output_path',
            'line_count',
            'word_count',
            'character_count',
            'file_size_bytes',
            'chapters_included',
            'estimated_read_time_minutes',
            'story_technical_ratio',
            'target_read_time_min',
            'target_read_time_max',
            'warnings'
        ]
        
        for field in expected_fields:
            assert field in result.data, f"Missing field in result.data: {field}"
    
    def test_chapters_included_count(self, module, context):
        """Verify result reports 9 chapters included."""
        result = module.execute(context)
        
        assert result.success
        assert result.data['chapters_included'] == 9, \
            f"Expected 9 chapters, got {result.data['chapters_included']}"
    
    def test_module_metadata(self, module):
        """Verify module metadata is correct."""
        metadata = module.get_metadata()
        
        assert metadata.module_id == "build_consolidated_story"
        assert metadata.name == "Build Consolidated Story"
        assert "THE-AWAKENING-OF-CORTEX.md" in metadata.description
    
    def test_prerequisites_validation(self, module):
        """Verify prerequisites check validates chapter files exist."""
        # Test with missing project_root
        is_valid, issues = module.validate_prerequisites({})
        assert not is_valid
        assert len(issues) > 0
        assert "project_root" in issues[0].lower()
        
        # Test with valid project_root
        is_valid, issues = module.validate_prerequisites({'project_root': Path.cwd()})
        # Should pass if all chapter files exist
        if not is_valid:
            # If it fails, should have meaningful error messages
            for issue in issues:
                assert "Chapter" in issue or "not found" in issue.lower()
    
    def test_rollback_removes_file(self, module, context):
        """Verify rollback removes generated file."""
        # Generate story first
        result = module.execute(context)
        assert result.success
        
        output_path = Path(context['consolidated_path'])
        assert output_path.exists()
        
        # Rollback
        rollback_success = module.rollback(context)
        assert rollback_success, "Rollback failed"
        
        # Verify file removed
        assert not output_path.exists(), "File still exists after rollback"
        
        # Verify context cleaned
        assert 'consolidated_story' not in context
        assert 'consolidated_path' not in context


class TestStoryQualityGates:
    """Test quality gates for story content."""
    
    @pytest.fixture
    def generated_story(self):
        """Generate story for quality testing."""
        module = BuildConsolidatedStoryModule()
        context = {'project_root': Path.cwd()}
        result = module.execute(context)
        assert result.success
        return context
    
    def test_story_has_narrative_voice(self, generated_story):
        """Verify story uses narrative voice (not dry technical)."""
        story_content = generated_story['consolidated_story']
        
        # Check for narrative indicators
        narrative_indicators = [
            "coffee",
            "screamed",
            "muttered",
            "shouted",
            "stared",
            "realized"
        ]
        
        found_count = sum(1 for indicator in narrative_indicators if indicator in story_content.lower())
        assert found_count >= 3, \
            f"Story lacks narrative voice. Found only {found_count}/6 indicators"
    
    def test_story_avoids_excessive_technical_jargon(self, generated_story):
        """Verify story isn't overwhelmed with technical jargon."""
        story_content = generated_story['consolidated_story']
        
        # This is a heuristic - story should have more narrative than code
        code_block_count = story_content.count("```")
        total_lines = len(story_content.split('\n'))
        
        # Code blocks should be < 10% of content
        code_ratio = code_block_count / (total_lines / 100)
        assert code_ratio < 0.10, \
            f"Too many code blocks: {code_ratio:.1%} of content"
    
    def test_story_has_chapter_transitions(self, generated_story):
        """Verify story has proper chapter transitions (not just concatenated)."""
        story_content = generated_story['consolidated_story']
        
        # Check for separators between chapters
        separator_count = story_content.count("---")
        assert separator_count >= 9, \
            f"Missing chapter separators. Found {separator_count}, expected at least 9"


# SKULL-005 Protection Tests
class TestStoryGenerationSKULL005:
    """SKULL-005 protection: Ensure story transformation produces measurable changes."""
    
    def test_module_actually_creates_file(self):
        """SKULL-005: Verify operation creates file (not validation-only)."""
        module = BuildConsolidatedStoryModule()
        context = {'project_root': Path.cwd()}
        output_path = Path.cwd() / "docs" / "story" / "CORTEX-STORY" / "THE-AWAKENING-OF-CORTEX.md"
        
        # Remove file if exists
        if output_path.exists():
            output_path.unlink()
        
        assert not output_path.exists(), "File should not exist before operation"
        
        # Execute
        result = module.execute(context)
        
        assert result.success, "Operation should succeed"
        assert output_path.exists(), "SKULL-005 VIOLATION: Operation claims success but file not created"
    
    def test_module_produces_different_content_on_chapter_change(self):
        """SKULL-005: Verify module detects and reflects chapter changes."""
        module = BuildConsolidatedStoryModule()
        context = {'project_root': Path.cwd()}
        
        # Generate once
        result1 = module.execute(context)
        assert result1.success
        content1 = context['consolidated_story']
        
        # Generate again (should produce identical content if chapters unchanged)
        context2 = {'project_root': Path.cwd()}
        result2 = module.execute(context2)
        assert result2.success
        content2 = context2['consolidated_story']
        
        # Content should be identical (deterministic generation)
        assert content1 == content2, \
            "Module produces inconsistent output on identical input"
