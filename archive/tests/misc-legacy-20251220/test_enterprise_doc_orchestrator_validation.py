"""
Tests to enforce Enterprise Documentation Orchestrator implementation rules

These tests validate:
1. IMAGE-CATALOG.yaml structure and completeness
2. Organized image folder structure (4 categories)
3. MkDocs diagram pages exist and reference images correctly
4. Single story source enforcement (no variants)
5. Orchestrator integration with IMAGE-CATALOG.yaml

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import pytest
import yaml
from pathlib import Path


# Test fixtures
@pytest.fixture
def workspace_root():
    """Get workspace root directory"""
    return Path(__file__).parent.parent


@pytest.fixture
def image_catalog_path(workspace_root):
    """Get IMAGE-CATALOG.yaml path"""
    return workspace_root / "docs" / "images" / "diagrams" / "IMAGE-CATALOG.yaml"


@pytest.fixture
def image_catalog_data(image_catalog_path):
    """Load IMAGE-CATALOG.yaml data"""
    with open(image_catalog_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture
def docs_path(workspace_root):
    """Get docs directory"""
    return workspace_root / "docs"


@pytest.fixture
def diagrams_path(docs_path):
    """Get diagrams directory"""
    return docs_path / "images" / "diagrams"


@pytest.fixture
def orchestrator_path(workspace_root):
    """Get orchestrator file path"""
    return workspace_root / "cortex-brain" / "admin" / "scripts" / "documentation" / "enterprise_documentation_orchestrator.py"


# ============================================================================
# TEST 1: IMAGE-CATALOG.yaml Validation
# ============================================================================

class TestImageCatalog:
    """Tests for IMAGE-CATALOG.yaml structure and completeness"""
    
    def test_catalog_file_exists(self, image_catalog_path):
        """IMAGE-CATALOG.yaml must exist"""
        assert image_catalog_path.exists(), f"IMAGE-CATALOG.yaml not found at {image_catalog_path}"
    
    def test_catalog_has_required_top_level_keys(self, image_catalog_data):
        """Catalog must have required top-level structure"""
        required_keys = ['catalog_version', 'total_images', 'categories', 'images', 
                        'category_metadata', 'generation_info', 'usage']
        
        for key in required_keys:
            assert key in image_catalog_data, f"Missing required key: {key}"
    
    def test_catalog_version_valid(self, image_catalog_data):
        """Catalog version must be specified"""
        assert image_catalog_data['catalog_version'] == "1.0", "Catalog version must be 1.0"
    
    def test_total_images_count(self, image_catalog_data):
        """Total images must be 14"""
        assert image_catalog_data['total_images'] == 14, "Expected 14 total images"
    
    def test_categories_complete(self, image_catalog_data):
        """Must have all 4 categories"""
        expected_categories = ['architectural', 'integration', 'operational', 'strategic']
        assert image_catalog_data['categories'] == expected_categories, \
            f"Categories must be {expected_categories}"
    
    def test_images_array_count(self, image_catalog_data):
        """Images array must contain 14 entries"""
        assert len(image_catalog_data['images']) == 14, \
            f"Expected 14 image entries, got {len(image_catalog_data['images'])}"
    
    def test_each_image_has_required_fields(self, image_catalog_data):
        """Each image entry must have required metadata fields"""
        required_fields = ['id', 'filename', 'category', 'path', 'title', 'description',
                          'dalle_prompt_file', 'narrative_file', 'mkdocs_pages', 
                          'mermaid_diagram', 'dimensions', 'color_theme']
        
        for idx, image in enumerate(image_catalog_data['images']):
            for field in required_fields:
                assert field in image, \
                    f"Image {idx} ({image.get('id', 'unknown')}) missing field: {field}"
    
    def test_image_categories_valid(self, image_catalog_data):
        """All image categories must be one of the 4 valid categories"""
        valid_categories = {'architectural', 'integration', 'operational', 'strategic'}
        
        for image in image_catalog_data['images']:
            assert image['category'] in valid_categories, \
                f"Image {image['id']} has invalid category: {image['category']}"
    
    def test_category_distribution(self, image_catalog_data):
        """Verify expected distribution of images across categories"""
        expected_distribution = {
            'architectural': 3,
            'integration': 3,
            'operational': 4,
            'strategic': 4
        }
        
        actual_distribution = {}
        for image in image_catalog_data['images']:
            category = image['category']
            actual_distribution[category] = actual_distribution.get(category, 0) + 1
        
        assert actual_distribution == expected_distribution, \
            f"Image distribution mismatch. Expected {expected_distribution}, got {actual_distribution}"
    
    def test_category_metadata_complete(self, image_catalog_data):
        """Category metadata must exist for all 4 categories"""
        category_meta = image_catalog_data['category_metadata']
        
        for category in ['architectural', 'integration', 'operational', 'strategic']:
            assert category in category_meta, f"Missing metadata for category: {category}"
            
            # Check required metadata fields
            meta = category_meta[category]
            assert 'color' in meta, f"Category {category} missing color"
            assert 'description' in meta, f"Category {category} missing description"
            assert 'page' in meta, f"Category {category} missing page"
            assert 'icon' in meta, f"Category {category} missing icon"
    
    def test_color_themes_match_metadata(self, image_catalog_data):
        """Image color themes must match category metadata"""
        category_colors = {
            cat: meta['color'] 
            for cat, meta in image_catalog_data['category_metadata'].items()
        }
        
        for image in image_catalog_data['images']:
            expected_color = category_colors[image['category']]
            assert image['color_theme'] == expected_color, \
                f"Image {image['id']} color {image['color_theme']} doesn't match category color {expected_color}"


# ============================================================================
# TEST 2: Organized Image Folder Structure
# ============================================================================

class TestImageFolderStructure:
    """Tests for organized image folder structure"""
    
    def test_category_folders_exist(self, diagrams_path):
        """All 4 category folders must exist"""
        categories = ['architectural', 'integration', 'operational', 'strategic']
        
        for category in categories:
            category_path = diagrams_path / category
            assert category_path.exists() and category_path.is_dir(), \
                f"Category folder missing: {category_path}"
    
    def test_all_images_exist_in_catalog(self, diagrams_path, image_catalog_data):
        """All images referenced in catalog must exist on disk"""
        missing_images = []
        
        for image in image_catalog_data['images']:
            # Path in catalog is relative to workspace root
            image_path = Path(image['path'])
            full_path = diagrams_path.parent.parent.parent / image_path
            
            if not full_path.exists():
                missing_images.append(str(image_path))
        
        assert len(missing_images) == 0, \
            f"Missing {len(missing_images)} images: {missing_images}"
    
    def test_no_images_in_root_diagrams_folder(self, diagrams_path):
        """PNG images should not exist in root diagrams folder (must be in categories)"""
        root_pngs = list(diagrams_path.glob("*.png"))
        
        assert len(root_pngs) == 0, \
            f"Found {len(root_pngs)} PNG files in root diagrams folder (should be in categories): {root_pngs}"
    
    def test_image_count_per_category(self, diagrams_path, image_catalog_data):
        """Verify actual image count matches catalog per category"""
        expected_counts = {
            'architectural': 3,
            'integration': 3,
            'operational': 4,
            'strategic': 4
        }
        
        for category, expected_count in expected_counts.items():
            category_path = diagrams_path / category
            actual_pngs = list(category_path.glob("*.png"))
            
            assert len(actual_pngs) == expected_count, \
                f"Category {category} has {len(actual_pngs)} PNGs, expected {expected_count}"


# ============================================================================
# TEST 3: MkDocs Diagram Pages
# ============================================================================

class TestMkDocsDiagramPages:
    """Tests for MkDocs diagram pages"""
    
    def test_all_diagram_pages_exist(self, docs_path):
        """All 4 diagram pages must exist"""
        pages = [
            'architecture-diagrams.md',
            'integration-diagrams.md',
            'operational-diagrams.md',
            'planning-diagrams.md'
        ]
        
        for page in pages:
            page_path = docs_path / page
            assert page_path.exists(), f"Diagram page missing: {page_path}"
    
    def test_diagram_pages_reference_images(self, docs_path, image_catalog_data):
        """Diagram pages must reference images from their category"""
        page_category_mapping = {
            'architecture-diagrams.md': 'architectural',
            'integration-diagrams.md': 'integration',
            'operational-diagrams.md': 'operational',
            'planning-diagrams.md': 'strategic'
        }
        
        for page_name, category in page_category_mapping.items():
            page_path = docs_path / page_name
            content = page_path.read_text(encoding='utf-8')
            
            # Get images for this category
            category_images = [
                img for img in image_catalog_data['images'] 
                if img['category'] == category
            ]
            
            # Verify each image is referenced in the page
            for image in category_images:
                image_ref = f"images/diagrams/{category}/{image['filename']}"
                assert image_ref in content, \
                    f"Page {page_name} missing reference to {image['filename']}"
    
    def test_mkdocs_yaml_has_visual_diagrams_section(self, workspace_root):
        """mkdocs.yml must have Visual Diagrams navigation section"""
        mkdocs_path = workspace_root / "mkdocs.yml"
        
        assert mkdocs_path.exists(), "mkdocs.yml not found"
        
        content = mkdocs_path.read_text(encoding='utf-8')
        
        # Check for Visual Diagrams section
        assert 'Visual Diagrams:' in content, "mkdocs.yml missing 'Visual Diagrams:' section"
        assert 'architecture-diagrams.md' in content, "mkdocs.yml missing architecture-diagrams.md"
        assert 'integration-diagrams.md' in content, "mkdocs.yml missing integration-diagrams.md"
        assert 'operational-diagrams.md' in content, "mkdocs.yml missing operational-diagrams.md"
        assert 'planning-diagrams.md' in content, "mkdocs.yml missing planning-diagrams.md"


# ============================================================================
# TEST 4: Single Story Source Enforcement
# ============================================================================

class TestSingleStorySource:
    """Tests for single story source enforcement"""
    
    def test_master_story_exists(self, workspace_root):
        """Master story must exist in organized location"""
        master_story = workspace_root / "cortex-brain" / "documents" / "stories" / "hilarious.md"
        
        assert master_story.exists(), \
            f"Master story not found at {master_story}"
    
    def test_no_story_variants_in_copilot_chats(self, workspace_root):
        """No story variants should exist in .github/CopilotChats/"""
        copilot_chats = workspace_root / ".github" / "CopilotChats"
        
        if copilot_chats.exists():
            # Check for common variant names
            variants = [
                'hilarious.md',  # Should be moved
                'storytest.md',  # Should be deleted
                'The-CORTEX-Story.md',  # Should be deleted
                'story.md'  # Should not exist
            ]
            
            found_variants = []
            for variant in variants:
                variant_path = copilot_chats / variant
                if variant_path.exists():
                    found_variants.append(variant)
            
            assert len(found_variants) == 0, \
                f"Found story variants in .github/CopilotChats/: {found_variants}"
    
    def test_no_story_variants_in_docs(self, workspace_root):
        """No story variants should exist in docs/"""
        docs_path = workspace_root / "docs"
        
        # Check for story files in docs root
        story_files = [
            'The-CORTEX-Story.md',
            'storytest.md',
            'story.md'
        ]
        
        found_files = []
        for story_file in story_files:
            story_path = docs_path / story_file
            if story_path.exists():
                found_files.append(story_file)
        
        assert len(found_files) == 0, \
            f"Found story variants in docs/: {found_files}"
    
    def test_orchestrator_references_correct_path(self, orchestrator_path):
        """Orchestrator must reference correct master story path"""
        content = orchestrator_path.read_text(encoding='utf-8')
        
        # Should reference organized location
        assert 'cortex-brain" / "documents" / "stories" / "hilarious.md' in content or \
               'cortex-brain/documents/stories/hilarious.md' in content, \
            "Orchestrator doesn't reference correct master story path"
        
        # Should NOT reference old location
        assert '.github" / "CopilotChats" / "hilarious.md' not in content and \
               '.github/CopilotChats/hilarious.md' not in content, \
            "Orchestrator still references old story location"
    
    def test_orchestrator_has_no_inline_fallback_story(self, orchestrator_path):
        """Orchestrator must not contain inline fallback story"""
        content = orchestrator_path.read_text(encoding='utf-8')
        
        # Check for suspicious inline story markers
        inline_story_markers = [
            '"""The Awakening of CORTEX',  # Inline story start
            "'''The Awakening of CORTEX",  # Alternative quote style
        ]
        
        for marker in inline_story_markers:
            assert marker not in content, \
                f"Orchestrator contains inline story (marker: {marker})"


# ============================================================================
# TEST 5: Orchestrator Image Catalog Integration
# ============================================================================

class TestOrchestratorImageCatalogIntegration:
    """Tests for orchestrator integration with IMAGE-CATALOG.yaml"""
    
    def test_orchestrator_references_image_catalog(self, orchestrator_path):
        """Orchestrator must reference IMAGE-CATALOG.yaml in documentation"""
        content = orchestrator_path.read_text(encoding='utf-8')
        
        # Check for IMAGE-CATALOG.yaml references
        assert 'IMAGE-CATALOG.yaml' in content, \
            "Orchestrator doesn't reference IMAGE-CATALOG.yaml"
    
    def test_image_guidance_method_mentions_catalog(self, orchestrator_path):
        """_create_image_generation_instructions must mention catalog"""
        content = orchestrator_path.read_text(encoding='utf-8')
        
        # Find the method
        assert '_create_image_generation_instructions' in content, \
            "Method _create_image_generation_instructions not found"
        
        # Extract method content (simple check)
        method_start = content.find('def _create_image_generation_instructions')
        method_end = content.find('\n    def ', method_start + 1)
        method_content = content[method_start:method_end]
        
        assert 'IMAGE-CATALOG.yaml' in method_content, \
            "_create_image_generation_instructions doesn't mention IMAGE-CATALOG.yaml"
    
    def test_image_guidance_documents_categories(self, orchestrator_path):
        """Image guidance must document 4 category folders"""
        content = orchestrator_path.read_text(encoding='utf-8')
        
        # Find the method
        method_start = content.find('def _create_image_generation_instructions')
        method_end = content.find('\n    def ', method_start + 1)
        method_content = content[method_start:method_end]
        
        # Check for category mentions
        categories = ['architectural', 'integration', 'operational', 'strategic']
        for category in categories:
            assert category in method_content, \
                f"_create_image_generation_instructions doesn't mention category: {category}"


# ============================================================================
# INTEGRATION TEST
# ============================================================================

class TestIntegration:
    """End-to-end integration tests"""
    
    def test_complete_image_pipeline(self, workspace_root, image_catalog_data):
        """Test complete image pipeline from catalog to documentation"""
        # 1. Verify catalog exists and is valid
        catalog_path = workspace_root / "docs" / "images" / "diagrams" / "IMAGE-CATALOG.yaml"
        assert catalog_path.exists()
        
        # 2. Verify all images in catalog exist on disk
        for image in image_catalog_data['images']:
            image_path = workspace_root / image['path']
            assert image_path.exists(), f"Image file missing: {image['path']}"
        
        # 3. Verify each image is referenced in its category's documentation page
        page_mapping = {
            'architectural': 'architecture-diagrams.md',
            'integration': 'integration-diagrams.md',
            'operational': 'operational-diagrams.md',
            'strategic': 'planning-diagrams.md'
        }
        
        for category, page_name in page_mapping.items():
            page_path = workspace_root / "docs" / page_name
            assert page_path.exists(), f"Documentation page missing: {page_name}"
            
            page_content = page_path.read_text(encoding='utf-8')
            
            # Get images for this category
            category_images = [img for img in image_catalog_data['images'] if img['category'] == category]
            
            # Verify all images referenced
            for image in category_images:
                assert image['filename'] in page_content, \
                    f"Image {image['filename']} not referenced in {page_name}"
        
        # 4. Verify MkDocs can find all pages
        mkdocs_path = workspace_root / "mkdocs.yml"
        mkdocs_content = mkdocs_path.read_text(encoding='utf-8')
        
        for page_name in page_mapping.values():
            assert page_name in mkdocs_content, \
                f"MkDocs navigation missing page: {page_name}"
    
    def test_story_pipeline(self, workspace_root):
        """Test complete story pipeline from master to orchestrator"""
        # 1. Verify master story exists
        master_story = workspace_root / "cortex-brain" / "documents" / "stories" / "hilarious.md"
        assert master_story.exists()
        
        # 2. Verify no variants
        variant_locations = [
            workspace_root / ".github" / "CopilotChats",
            workspace_root / "docs",
            workspace_root / "cortex-brain" / "archives"
        ]
        
        story_variant_names = ['storytest.md', 'The-CORTEX-Story.md', 'story.md']
        
        for location in variant_locations:
            if location.exists():
                for variant in story_variant_names:
                    variant_path = location / variant
                    assert not variant_path.exists(), \
                        f"Story variant found: {variant_path}"
        
        # 3. Verify orchestrator references correct path
        orchestrator = workspace_root / "cortex-brain" / "admin" / "scripts" / "documentation" / "enterprise_documentation_orchestrator.py"
        orchestrator_content = orchestrator.read_text(encoding='utf-8')
        
        assert 'cortex-brain' in orchestrator_content and 'documents' in orchestrator_content and 'stories' in orchestrator_content, \
            "Orchestrator doesn't reference organized story location"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
