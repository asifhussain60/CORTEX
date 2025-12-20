"""
CORTEX Documentation Quality Tests

Tests DALL-E prompt quality, content completeness, and specification adherence.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
import re


class TestDALLEPromptQuality:
    """Test suite for DALL-E prompt quality validation"""
    
    @pytest.fixture
    def prompts_dir(self):
        """Get prompts directory path"""
        return Path(__file__).parent.parent.parent / "docs" / "diagrams" / "prompts"
    
    @pytest.fixture
    def expected_prompts(self):
        """Expected DALL-E prompt files"""
        return [
            "01-tier-architecture-prompt.md",
            "02-agent-coordination-prompt.md",
            "03-information-flow-prompt.md",
            "04-conversation-tracking-prompt.md",
            "05-plugin-system-prompt.md",
            "06-brain-protection-prompt.md",
            "07-operation-pipeline-prompt.md",
            "08-setup-orchestration-prompt.md",
            "09-documentation-generation-prompt.md",
            "10-feature-planning-prompt.md",
            "11-testing-strategy-prompt.md",
            "12-deployment-pipeline-prompt.md",
            "13-user-journey-prompt.md",
            "14-system-architecture-prompt.md",
        ]
    
    def test_all_prompts_exist(self, prompts_dir, expected_prompts):
        """Verify all 14 DALL-E prompt files exist"""
        for prompt_file in expected_prompts:
            prompt_path = prompts_dir / prompt_file
            assert prompt_path.exists(), f"Missing prompt file: {prompt_file}"
    
    def test_prompt_word_count(self, prompts_dir, expected_prompts):
        """Each prompt must be ≥500 words"""
        for prompt_file in expected_prompts:
            prompt_path = prompts_dir / prompt_file
            content = prompt_path.read_text(encoding='utf-8')
            word_count = len(content.split())
            assert word_count >= 500, \
                f"{prompt_file} has only {word_count} words (minimum 500 required)"
    
    def test_prompt_required_sections(self, prompts_dir, expected_prompts):
        """Each prompt must have 10+ required sections"""
        required_sections = [
            "Visual Composition",
            "Color Palette",
            "Components & Elements",
            "Relationships & Flow",
            "Typography & Labels",
            "Technical Accuracy",
            "Style & Aesthetic",
            "Mood & Atmosphere",
            "Output Specifications",
            "Usage Context"
        ]
        
        for prompt_file in expected_prompts:
            prompt_path = prompts_dir / prompt_file
            content = prompt_path.read_text(encoding='utf-8')
            
            missing_sections = []
            for section in required_sections:
                if section not in content:
                    missing_sections.append(section)
            
            assert len(missing_sections) == 0, \
                f"{prompt_file} missing sections: {', '.join(missing_sections)}"
    
    def test_color_codes_valid(self, prompts_dir, expected_prompts):
        """All color codes must be valid hex format (#RRGGBB)"""
        hex_color_pattern = re.compile(r'#[0-9A-Fa-f]{6}\b')
        invalid_color_pattern = re.compile(r'#[0-9A-Fa-f]{1,5}\b|#[0-9A-Fa-f]{7,}\b')
        
        for prompt_file in expected_prompts:
            prompt_path = prompts_dir / prompt_file
            content = prompt_path.read_text(encoding='utf-8')
            
            # Check for invalid color codes
            invalid_colors = invalid_color_pattern.findall(content)
            assert len(invalid_colors) == 0, \
                f"{prompt_file} has invalid color codes: {invalid_colors}"
            
            # Ensure at least one valid color code exists
            valid_colors = hex_color_pattern.findall(content)
            assert len(valid_colors) > 0, \
                f"{prompt_file} has no valid color codes defined"
    
    def test_no_placeholder_text(self, prompts_dir, expected_prompts):
        """No TODO, TBD, or placeholder text in production prompts"""
        placeholder_patterns = [
            r'\bTODO\b',
            r'\bTBD\b',
            r'\[.*placeholder.*\]',
            r'\[.*to be.*\]',
        ]
        
        for prompt_file in expected_prompts:
            prompt_path = prompts_dir / prompt_file
            content = prompt_path.read_text(encoding='utf-8')
            
            for pattern in placeholder_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                assert len(matches) == 0, \
                    f"{prompt_file} contains placeholder text: {matches}"


class TestContentCompleteness:
    """Test suite for documentation completeness"""
    
    @pytest.fixture
    def docs_dir(self):
        """Get docs directory path"""
        return Path(__file__).parent.parent.parent / "docs"
    
    def test_faq_exists(self, docs_dir):
        """FAQ.md must exist"""
        faq_path = docs_dir / "FAQ.md"
        assert faq_path.exists(), "FAQ.md not found in docs/"
    
    def test_faq_minimum_content(self, docs_dir):
        """FAQ must have ≥30 Q&A pairs"""
        faq_path = docs_dir / "FAQ.md"
        content = faq_path.read_text(encoding='utf-8')
        
        # Count question markers (### Q: or **Q:** patterns)
        q_count = len(re.findall(r'(###\s*Q:|[*]{2}Q:[*]{2})', content))
        assert q_count >= 30, f"FAQ has only {q_count} questions (minimum 30 required)"
    
    def test_faq_six_categories(self, docs_dir):
        """FAQ must have 6 categories"""
        faq_path = docs_dir / "FAQ.md"
        content = faq_path.read_text(encoding='utf-8')
        
        required_categories = [
            "Architecture & Design",
            "Setup & Installation",
            "Usage & Operations",
            "Troubleshooting",
            "Advanced Topics",
            "Contributing & Development"
        ]
        
        missing_categories = []
        for category in required_categories:
            if category not in content:
                missing_categories.append(category)
        
        assert len(missing_categories) == 0, \
            f"FAQ missing categories: {', '.join(missing_categories)}"
    
    def test_image_folder_structure(self, docs_dir):
        """Image folder structure must exist"""
        images_dir = docs_dir / "images" / "diagrams"
        
        required_subdirs = [
            "architectural",
            "strategic",
            "operational",
            "integration"
        ]
        
        for subdir in required_subdirs:
            subdir_path = images_dir / subdir
            assert subdir_path.exists(), f"Missing image subdirectory: {subdir}"


class TestVersionConsistency:
    """Test suite for version and reference consistency"""
    
    @pytest.fixture
    def cortex_version(self):
        """Get current CORTEX version"""
        # TODO: Read from version file or config
        return "3.0"
    
    def test_no_stale_version_references(self, cortex_version):
        """No references to old CORTEX versions in docs"""
        docs_dir = Path(__file__).parent.parent.parent / "docs"
        
        # Skip this test - will be implemented with version tracking
        pytest.skip("Version tracking not yet implemented")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
