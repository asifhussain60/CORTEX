"""
Integration tests for Image Prompt Generator with EPM pipeline

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.epm.modules.image_prompt_generator import ImagePromptGenerator


class TestImagePromptIntegration(unittest.TestCase):
    """Integration tests for image prompt generator with EPM"""
    
    def setUp(self):
        """Create temporary directory for tests"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.output_dir = self.temp_dir / "diagrams"
        self.generator = ImagePromptGenerator(self.output_dir)
    
    def tearDown(self):
        """Clean up temporary directory"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_directory_structure_creation(self):
        """Test that 3-part directory structure is created"""
        # Act
        self.generator._create_directory_structure()
        
        # Assert
        self.assertTrue((self.output_dir / "prompts").exists())
        self.assertTrue((self.output_dir / "narratives").exists())
        self.assertTrue((self.output_dir / "generated").exists())
    
    def test_minimal_capabilities_data(self):
        """Test generation with minimal capabilities data"""
        # Arrange
        capabilities = {
            "tiers": [
                {"id": 0, "name": "Instinct", "storage_type": "YAML"},
                {"id": 1, "name": "Memory", "storage_type": "SQLite"}
            ],
            "agents": [
                {"name": "Test Agent", "role": "Testing", "hemisphere": "LEFT"}
            ],
            "plugins": [
                {"name": "Test Plugin", "description": "Test description"}
            ]
        }
        modules = []
        
        # Act
        result = self.generator.generate_all(capabilities, modules)
        
        # Assert
        self.assertTrue(result['success'])
        self.assertEqual(result['diagrams_generated'], 6)
        self.assertTrue((self.output_dir / "prompts").exists())
        self.assertTrue((self.output_dir / "narratives").exists())
        self.assertTrue((self.output_dir / "generated").exists())
    
    def test_readme_generation(self):
        """Test that README.md is generated"""
        # Arrange
        capabilities = {"tiers": [], "agents": [], "plugins": []}
        modules = []
        
        # Act
        self.generator.generate_all(capabilities, modules)
        
        # Assert
        readme_path = self.output_dir / "README.md"
        self.assertTrue(readme_path.exists())
        
        # Verify README content
        content = readme_path.read_text(encoding='utf-8')
        self.assertIn("CORTEX Diagram Generation Workflow", content)
        self.assertIn("Directory Structure", content)
        self.assertIn("prompts/", content)
        self.assertIn("narratives/", content)
        self.assertIn("generated/", content)
    
    def test_style_guide_generation(self):
        """Test that STYLE-GUIDE.md is generated"""
        # Arrange
        capabilities = {"tiers": [], "agents": [], "plugins": []}
        modules = []
        
        # Act
        self.generator.generate_all(capabilities, modules)
        
        # Assert
        style_guide_path = self.output_dir / "STYLE-GUIDE.md"
        self.assertTrue(style_guide_path.exists())
        
        # Verify style guide content
        content = style_guide_path.read_text(encoding='utf-8')
        self.assertIn("Color Palette", content)
        self.assertIn("#6B46C1", content)  # Tier 0 purple
        self.assertIn("#3B82F6", content)  # Tier 1 blue
        self.assertIn("#10B981", content)  # Tier 2 green
        self.assertIn("#F59E0B", content)  # Tier 3 orange
    
    def test_tier_architecture_prompt_generation(self):
        """Test tier architecture prompt file generation"""
        # Arrange
        capabilities = {
            "tiers": [
                {"id": 0, "name": "Instinct", "storage_type": "YAML"},
                {"id": 1, "name": "Memory", "storage_type": "SQLite"},
                {"id": 2, "name": "Knowledge", "storage_type": "SQLite"},
                {"id": 3, "name": "Context", "storage_type": "SQLite"}
            ],
            "agents": [],
            "plugins": []
        }
        modules = []
        
        # Act
        result = self.generator.generate_all(capabilities, modules)
        
        # Assert
        prompt_path = self.output_dir / "prompts" / "01-tier-architecture.md"
        self.assertTrue(prompt_path.exists())
        
        # Verify prompt content
        content = prompt_path.read_text(encoding='utf-8')
        self.assertIn("Diagram 01: CORTEX 4-Tier Brain Architecture", content)
        self.assertIn("AI Generation Instructions", content)
        self.assertIn("Tier 0", content)
        self.assertIn("Tier 1", content)
        self.assertIn("Tier 2", content)
        self.assertIn("Tier 3", content)
    
    def test_tier_architecture_narrative_generation(self):
        """Test tier architecture narrative file generation"""
        # Arrange
        capabilities = {
            "tiers": [
                {"id": 0, "name": "Instinct", "storage_type": "YAML"}
            ],
            "agents": [],
            "plugins": []
        }
        modules = []
        
        # Act
        result = self.generator.generate_all(capabilities, modules)
        
        # Assert
        narrative_path = self.output_dir / "narratives" / "01-tier-architecture.md"
        self.assertTrue(narrative_path.exists())
        
        # Verify narrative content
        content = narrative_path.read_text(encoding='utf-8')
        self.assertIn("Tier Architecture Narrative", content)
        self.assertIn("For Leadership", content)
        self.assertIn("For Developers", content)
        self.assertIn("Key Takeaways", content)
    
    def test_color_palette_consistency(self):
        """Test that color palette is consistent across all prompts"""
        # Arrange
        capabilities = {
            "tiers": [
                {"id": 0, "name": "Instinct", "storage_type": "YAML"}
            ],
            "agents": [
                {"name": "Test", "role": "Test", "hemisphere": "LEFT"}
            ],
            "plugins": [
                {"name": "Test", "description": "Test"}
            ]
        }
        modules = []
        
        # Act
        self.generator.generate_all(capabilities, modules)
        
        # Assert - Check color codes in prompts
        expected_colors = {
            '#6B46C1',  # Tier 0 purple
            '#3B82F6',  # Tier 1 blue / LEFT brain
            '#10B981',  # Tier 2 green
            '#F59E0B',  # Tier 3 orange / RIGHT brain
            '#6B7280'   # Connections gray
        }
        
        # Read all prompt files
        prompts_dir = self.output_dir / "prompts"
        for prompt_file in prompts_dir.glob("*.md"):
            content = prompt_file.read_text(encoding='utf-8')
            
            # At least one color should be mentioned
            has_color = any(color in content for color in expected_colors)
            self.assertTrue(has_color, f"No color codes found in {prompt_file.name}")
    
    def test_all_six_diagrams_generated(self):
        """Test that all 6 diagram types are generated"""
        # Arrange
        capabilities = {"tiers": [], "agents": [], "plugins": []}
        modules = []
        
        # Act
        result = self.generator.generate_all(capabilities, modules)
        
        # Assert
        expected_ids = [
            "01-tier-architecture",
            "02-agent-system",
            "03-plugin-architecture",
            "04-memory-flow",
            "05-agent-coordination",
            "06-basement-scene"
        ]
        
        prompts_dir = self.output_dir / "prompts"
        narratives_dir = self.output_dir / "narratives"
        
        for diagram_id in expected_ids:
            # Check prompt file
            prompt_file = prompts_dir / f"{diagram_id}.md"
            self.assertTrue(prompt_file.exists(), f"Missing prompt: {diagram_id}.md")
            
            # Check narrative file
            narrative_file = narratives_dir / f"{diagram_id}.md"
            self.assertTrue(narrative_file.exists(), f"Missing narrative: {diagram_id}.md")
    
    def test_result_dictionary_structure(self):
        """Test that result dictionary has correct structure"""
        # Arrange
        capabilities = {"tiers": [], "agents": [], "plugins": []}
        modules = []
        
        # Act
        result = self.generator.generate_all(capabilities, modules)
        
        # Assert
        self.assertIn('success', result)
        self.assertIn('diagrams_generated', result)
        self.assertIn('prompts_dir', result)
        self.assertIn('narratives_dir', result)
        self.assertIn('generated_dir', result)
        self.assertIn('results', result)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['diagrams_generated'], 6)
        self.assertEqual(len(result['results']), 6)


class TestEPMDocGeneratorIntegration(unittest.TestCase):
    """Test EPM doc_generator.py integration"""
    
    def test_image_prompt_generator_import(self):
        """Test that ImagePromptGenerator can be imported"""
        try:
            from src.epm.doc_generator import DocumentationGenerator
            # If we get here, import succeeded
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import DocumentationGenerator: {e}")
    
    def test_doc_generator_has_image_prompt_generator_attribute(self):
        """Test that DocumentationGenerator has image_prompt_generator"""
        from src.epm.doc_generator import DocumentationGenerator
        
        temp_dir = Path(tempfile.mkdtemp())
        try:
            doc_gen = DocumentationGenerator(temp_dir, profile="comprehensive")
            self.assertTrue(hasattr(doc_gen, 'image_prompt_generator'))
        finally:
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    unittest.main()
