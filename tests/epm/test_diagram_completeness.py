"""
Comprehensive Diagram Completeness Tests

Validates that ALL diagrams defined in master-diagram-list.yaml are generated correctly.
This test prevents regressions where diagram count drops silently.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import yaml

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.epm.modules.image_prompt_generator import ImagePromptGenerator


class TestDiagramCompleteness(unittest.TestCase):
    """
    Comprehensive tests that validate ALL diagrams are generated.
    
    These tests are the PRIMARY DEFENSE against diagram generation regressions.
    If diagram count drops, these tests MUST FAIL.
    """
    
    @classmethod
    def setUpClass(cls):
        """Load master diagram configuration"""
        config_path = Path(__file__).parent.parent.parent / "cortex-brain" / "doc-generation-config" / "master-diagram-list.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Master diagram config not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            cls.master_config = yaml.safe_load(f)
        
        cls.expected_diagrams = cls.master_config['diagrams']
        cls.metadata = cls.master_config['metadata']
    
    def setUp(self):
        """Create temporary directory for tests"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.output_dir = self.temp_dir / "diagrams"
        self.generator = ImagePromptGenerator(self.output_dir)
        
        # Test data
        self.capabilities = {
            "tiers": [
                {"id": 0, "name": "Instinct", "storage_type": "YAML"},
                {"id": 1, "name": "Memory", "storage_type": "SQLite"},
                {"id": 2, "name": "Knowledge", "storage_type": "SQLite"},
                {"id": 3, "name": "Context", "storage_type": "SQLite"}
            ],
            "agents": [
                {"name": "Test Agent", "role": "Testing", "hemisphere": "LEFT"}
            ],
            "plugins": [
                {"name": "Test Plugin", "description": "Test description"}
            ]
        }
        self.modules = []
    
    def tearDown(self):
        """Clean up temporary directory"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_master_config_exists(self):
        """Test that master diagram configuration exists and is valid"""
        self.assertIsNotNone(self.master_config)
        self.assertIn('diagrams', self.master_config)
        self.assertIn('metadata', self.master_config)
        self.assertIn('validation', self.master_config)
    
    def test_master_config_diagram_count(self):
        """Test that master config has expected number of diagrams"""
        expected_count = self.metadata['total_diagrams']
        actual_count = len(self.expected_diagrams)
        
        self.assertEqual(
            actual_count,
            expected_count,
            f"Master config metadata says {expected_count} diagrams but found {actual_count}"
        )
    
    def test_all_diagrams_have_required_fields(self):
        """Test that all diagrams in config have required fields"""
        required_fields = ['id', 'name', 'title', 'type', 'format', 'required', 'generator_method', 'description', 'outputs']
        
        for diagram in self.expected_diagrams:
            for field in required_fields:
                self.assertIn(
                    field,
                    diagram,
                    f"Diagram {diagram.get('id', 'UNKNOWN')} missing required field: {field}"
                )
    
    def test_diagram_ids_are_sequential(self):
        """Test that diagram IDs are sequential (01, 02, 03, ...)"""
        expected_ids = [f"{i:02d}" for i in range(1, len(self.expected_diagrams) + 1)]
        actual_ids = [d['id'] for d in self.expected_diagrams]
        
        self.assertEqual(
            actual_ids,
            expected_ids,
            f"Diagram IDs are not sequential. Expected: {expected_ids}, Got: {actual_ids}"
        )
    
    def test_diagram_names_follow_convention(self):
        """Test that all diagram names follow kebab-case convention"""
        import re
        pattern = re.compile(r'^[a-z]+(-[a-z]+)*$')
        
        for diagram in self.expected_diagrams:
            name = diagram['name']
            self.assertTrue(
                pattern.match(name),
                f"Diagram name '{name}' does not follow kebab-case convention"
            )
    
    def test_all_required_diagrams_generated(self):
        """
        CRITICAL TEST: Validates that ALL required diagrams are generated.
        
        This is the PRIMARY DEFENSE against regressions.
        If this test fails, diagram generation is broken.
        """
        # Generate diagrams
        result = self.generator.generate_all(self.capabilities, self.modules)
        
        # Get required diagrams from master config
        required_diagrams = [d for d in self.expected_diagrams if d['required']]
        
        # Validate each required diagram was generated
        for diagram in required_diagrams:
            diagram_id = f"{diagram['id']}-{diagram['name']}"
            
            # Check prompt file
            prompt_file = self.output_dir / "prompts" / f"{diagram_id}.md"
            self.assertTrue(
                prompt_file.exists(),
                f"CRITICAL: Required diagram PROMPT missing: {diagram_id}.md"
            )
            
            # Check narrative file
            narrative_file = self.output_dir / "narratives" / f"{diagram_id}.md"
            self.assertTrue(
                narrative_file.exists(),
                f"CRITICAL: Required diagram NARRATIVE missing: {diagram_id}.md"
            )
    
    def test_generated_diagram_count_matches_master_config(self):
        """
        CRITICAL TEST: Validates that the number of generated diagrams matches master config.
        
        This catches regressions where diagram generation silently drops files.
        """
        # Generate diagrams
        result = self.generator.generate_all(self.capabilities, self.modules)
        
        # Get expected count from master config
        expected_required_count = self.metadata['required_diagrams']
        
        # Count generated files
        prompts_dir = self.output_dir / "prompts"
        generated_prompts = list(prompts_dir.glob("*.md"))
        
        # We should have at least the required count
        # (May have optional diagrams too)
        self.assertGreaterEqual(
            len(generated_prompts),
            expected_required_count,
            f"CRITICAL REGRESSION: Expected at least {expected_required_count} diagrams, got {len(generated_prompts)}"
        )
    
    def test_no_extra_diagrams_generated(self):
        """Test that no unexpected diagrams are generated"""
        # Generate diagrams
        result = self.generator.generate_all(self.capabilities, self.modules)
        
        # Get expected diagram IDs
        expected_ids = set(f"{d['id']}-{d['name']}" for d in self.expected_diagrams)
        
        # Get generated diagram IDs
        prompts_dir = self.output_dir / "prompts"
        generated_files = list(prompts_dir.glob("*.md"))
        
        # Exclude README and STYLE-GUIDE
        generated_ids = set(
            f.stem for f in generated_files 
            if f.name not in ['README.md', 'STYLE-GUIDE.md']
        )
        
        # Check for extra files
        extra_diagrams = generated_ids - expected_ids
        
        self.assertEqual(
            len(extra_diagrams),
            0,
            f"Unexpected diagrams generated: {extra_diagrams}"
        )
    
    def test_prompts_and_narratives_match(self):
        """Test that every prompt has a corresponding narrative"""
        # Generate diagrams
        result = self.generator.generate_all(self.capabilities, self.modules)
        
        prompts_dir = self.output_dir / "prompts"
        narratives_dir = self.output_dir / "narratives"
        
        prompt_files = set(f.stem for f in prompts_dir.glob("*.md") if f.name not in ['README.md', 'STYLE-GUIDE.md'])
        narrative_files = set(f.stem for f in narratives_dir.glob("*.md") if f.name not in ['README.md', 'STYLE-GUIDE.md'])
        
        # Every prompt should have a narrative
        missing_narratives = prompt_files - narrative_files
        self.assertEqual(
            len(missing_narratives),
            0,
            f"Prompts missing corresponding narratives: {missing_narratives}"
        )
        
        # Every narrative should have a prompt
        missing_prompts = narrative_files - prompt_files
        self.assertEqual(
            len(missing_prompts),
            0,
            f"Narratives missing corresponding prompts: {missing_prompts}"
        )
    
    def test_diagram_categories_represented(self):
        """Test that all diagram categories from metadata are represented"""
        categories = self.metadata['categories']
        
        for category, expected_count in categories.items():
            actual_count = sum(1 for d in self.expected_diagrams if d['type'] == category)
            
            self.assertEqual(
                actual_count,
                expected_count,
                f"Category '{category}' should have {expected_count} diagrams but has {actual_count}"
            )
    
    def test_readme_and_style_guide_generated(self):
        """Test that supporting documentation is generated"""
        # Generate diagrams
        result = self.generator.generate_all(self.capabilities, self.modules)
        
        readme_path = self.output_dir / "README.md"
        self.assertTrue(readme_path.exists(), "README.md not generated")
        
        style_guide_path = self.output_dir / "STYLE-GUIDE.md"
        self.assertTrue(style_guide_path.exists(), "STYLE-GUIDE.md not generated")
    
    def test_prompt_files_have_minimum_content(self):
        """Test that prompt files have substantial content"""
        # Generate diagrams
        result = self.generator.generate_all(self.capabilities, self.modules)
        
        prompts_dir = self.output_dir / "prompts"
        min_length = self.master_config['validation']['quality_checks']['prompt_length_min']
        
        for diagram in self.expected_diagrams:
            if not diagram['required']:
                continue
            
            diagram_id = f"{diagram['id']}-{diagram['name']}"
            prompt_file = prompts_dir / f"{diagram_id}.md"
            
            if not prompt_file.exists():
                continue
            
            content = prompt_file.read_text(encoding='utf-8')
            
            self.assertGreater(
                len(content),
                min_length,
                f"Prompt {diagram_id}.md is too short (< {min_length} chars)"
            )
    
    def test_narrative_files_have_minimum_content(self):
        """Test that narrative files have substantial content"""
        # Generate diagrams
        result = self.generator.generate_all(self.capabilities, self.modules)
        
        narratives_dir = self.output_dir / "narratives"
        min_length = self.master_config['validation']['quality_checks']['narrative_length_min']
        
        for diagram in self.expected_diagrams:
            if not diagram['required']:
                continue
            
            diagram_id = f"{diagram['id']}-{diagram['name']}"
            narrative_file = narratives_dir / f"{diagram_id}.md"
            
            if not narrative_file.exists():
                continue
            
            content = narrative_file.read_text(encoding='utf-8')
            
            self.assertGreater(
                len(content),
                min_length,
                f"Narrative {diagram_id}.md is too short (< {min_length} chars)"
            )
    
    def test_prompts_include_ai_instructions(self):
        """Test that all prompts include AI generation instructions"""
        # Generate diagrams
        result = self.generator.generate_all(self.capabilities, self.modules)
        
        prompts_dir = self.output_dir / "prompts"
        
        for diagram in self.expected_diagrams:
            if not diagram['required']:
                continue
            
            diagram_id = f"{diagram['id']}-{diagram['name']}"
            prompt_file = prompts_dir / f"{diagram_id}.md"
            
            if not prompt_file.exists():
                continue
            
            content = prompt_file.read_text(encoding='utf-8')
            
            # Check for AI instruction keywords
            ai_keywords = ['AI Generation', 'ChatGPT', 'DALL-E', 'Generate', 'Create']
            has_ai_instructions = any(keyword in content for keyword in ai_keywords)
            
            self.assertTrue(
                has_ai_instructions,
                f"Prompt {diagram_id}.md missing AI generation instructions"
            )
    
    def test_result_dictionary_completeness(self):
        """Test that result dictionary has all expected data"""
        result = self.generator.generate_all(self.capabilities, self.modules)
        
        # Check structure
        self.assertIn('success', result)
        self.assertIn('diagrams_generated', result)
        self.assertIn('prompts_dir', result)
        self.assertIn('narratives_dir', result)
        self.assertIn('generated_dir', result)
        self.assertIn('results', result)
        
        # Check success
        self.assertTrue(result['success'], "Generation reported failure")
        
        # Check diagram count
        expected_count = self.metadata['required_diagrams']
        self.assertGreaterEqual(
            result['diagrams_generated'],
            expected_count,
            f"Result reports {result['diagrams_generated']} diagrams, expected at least {expected_count}"
        )


class TestDiagramRegressionProtection(unittest.TestCase):
    """
    Tests specifically designed to catch regressions in diagram generation.
    
    These tests fail loudly if diagram count drops below expected values.
    """
    
    def test_minimum_diagram_count_protection(self):
        """
        CRITICAL REGRESSION TEST: Ensures we never drop below 17 diagrams.
        
        This test MUST FAIL if diagram count drops.
        """
        config_path = Path(__file__).parent.parent.parent / "cortex-brain" / "doc-generation-config" / "master-diagram-list.yaml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            master_config = yaml.safe_load(f)
        
        total_diagrams = master_config['metadata']['total_diagrams']
        
        # CRITICAL THRESHOLD: We must have at least 17 diagrams
        MINIMUM_DIAGRAM_COUNT = 17
        
        self.assertGreaterEqual(
            total_diagrams,
            MINIMUM_DIAGRAM_COUNT,
            f"CRITICAL REGRESSION: Diagram count dropped to {total_diagrams} (minimum: {MINIMUM_DIAGRAM_COUNT})"
        )
    
    def test_no_missing_diagram_ids(self):
        """Test that there are no gaps in diagram ID sequence"""
        config_path = Path(__file__).parent.parent.parent / "cortex-brain" / "doc-generation-config" / "master-diagram-list.yaml"
        
        with open(config_path, 'r', encoding='utf-8') as f:
            master_config = yaml.safe_load(f)
        
        diagrams = master_config['diagrams']
        ids = [int(d['id']) for d in diagrams]
        
        # Check for gaps
        for i in range(1, max(ids) + 1):
            self.assertIn(
                i,
                ids,
                f"Missing diagram ID: {i:02d}"
            )


if __name__ == '__main__':
    # Run with verbose output
    unittest.main(verbosity=2)
