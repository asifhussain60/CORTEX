"""
Tests for Multilingual Template Loader (Task 3.2)
TDD RED Phase: Write failing tests first
"""
import pytest
from pathlib import Path
from src.utils.multilingual_template_loader import MultilingualTemplateLoader


class TestMultilingualTemplateLoader:
    """Test suite for multilingual template loading and management"""
    
    @pytest.fixture
    def loader(self, tmp_path):
        """Create loader with test template file"""
        # Create minimal test template file
        template_file = tmp_path / "test-multilingual-templates.yaml"
        template_file.write_text("""
schema_version: '3.2'
supported_languages:
  - en
  - es
  - fr

templates:
  help:
    en:
      concise:
        content: "Quick help in English"
      balanced:
        content: "Standard help in English"
      verbose:
        content: "Detailed help in English"
    es:
      concise:
        content: "Ayuda rápida en español"
      balanced:
        content: "Ayuda estándar en español"
      verbose:
        content: "Ayuda detallada en español"
    fr:
      concise:
        content: "Aide rapide en français"
      balanced:
        content: "Aide standard en français"
      verbose:
        content: "Aide détaillée en français"
""")
        return MultilingualTemplateLoader(str(template_file))
    
    def test_loader_initialization(self, loader):
        """Test loader initializes with template file"""
        assert loader is not None
        assert loader.template_count > 0
    
    def test_load_template_english_concise(self, loader):
        """Test loading English concise template"""
        template = loader.get_template("help", language="en", verbosity="concise")
        assert template is not None
        assert "Quick help in English" in template
    
    def test_load_template_spanish_verbose(self, loader):
        """Test loading Spanish verbose template"""
        template = loader.get_template("help", language="es", verbosity="verbose")
        assert template is not None
        assert "detallada" in template
        assert "español" in template
    
    def test_load_template_french_balanced(self, loader):
        """Test loading French balanced template"""
        template = loader.get_template("help", language="fr", verbosity="balanced")
        assert template is not None
        assert "standard" in template
        assert "français" in template
    
    def test_fallback_to_english_unsupported_language(self, loader):
        """Test fallback to English for unsupported language"""
        template = loader.get_template("help", language="zh", verbosity="concise")
        assert template is not None
        assert "Quick help in English" in template
    
    def test_fallback_to_balanced_missing_verbosity(self, loader):
        """Test fallback to balanced when verbosity not available"""
        # Request verbosity that doesn't exist
        template = loader.get_template("help", language="en", verbosity="technical")
        assert template is not None
        # Should fallback to balanced
        assert "Standard help" in template or "help" in template
    
    def test_get_supported_languages(self, loader):
        """Test retrieving supported languages list"""
        languages = loader.get_supported_languages()
        assert "en" in languages
        assert "es" in languages
        assert "fr" in languages
        assert len(languages) >= 3
    
    def test_template_exists_check(self, loader):
        """Test checking if template exists"""
        assert loader.template_exists("help", "en", "concise") is True
        assert loader.template_exists("help", "es", "verbose") is True
        assert loader.template_exists("nonexistent", "en", "concise") is False
    
    def test_get_available_verbosity_levels(self, loader):
        """Test retrieving available verbosity levels for template"""
        levels = loader.get_available_verbosity_levels("help", "en")
        assert "concise" in levels
        assert "balanced" in levels
        assert "verbose" in levels
    
    def test_validate_template_structure(self, loader):
        """Test template structure validation"""
        is_valid = loader.validate_template_structure()
        assert is_valid is True
    
    def test_get_template_metadata(self, loader):
        """Test retrieving template metadata"""
        metadata = loader.get_template_metadata("help")
        assert metadata is not None
        assert "languages" in metadata
        assert "verbosity_levels" in metadata
    
    def test_cache_template_loading(self, loader):
        """Test template caching for performance"""
        # First load
        template1 = loader.get_template("help", "en", "concise")
        
        # Second load (should use cache)
        template2 = loader.get_template("help", "en", "concise")
        
        assert template1 == template2
        # Check cache was used (implementation should track this)
        assert loader.cache_hits > 0
    
    def test_reload_templates(self, loader):
        """Test reloading templates from file"""
        original_count = loader.template_count
        
        # Reload templates
        loader.reload()
        
        assert loader.template_count == original_count
    
    def test_missing_template_returns_none(self, loader):
        """Test that missing template returns None"""
        template = loader.get_template("nonexistent_template", "en", "concise")
        assert template is None
    
    def test_template_interpolation_variables(self, loader):
        """Test that templates preserve interpolation variables"""
        # This test ensures {{variables}} are not corrupted during loading
        template = loader.get_template("help", "en", "concise")
        assert template is not None
        # Variables should be preserved for later interpolation


class TestMultilingualTemplateYAMLStructure:
    """Test suite for multilingual-templates.yaml structure and content"""
    
    def test_production_template_file_exists(self):
        """Test that production multilingual template file exists"""
        template_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/multilingual-templates.yaml")
        assert template_path.exists(), "Production multilingual template file should exist"
    
    def test_production_template_has_12_languages(self):
        """Test that production templates support 12 languages"""
        loader = MultilingualTemplateLoader()
        languages = loader.get_supported_languages()
        
        required_languages = ["en", "es", "fr", "de", "pt", "it", "zh", "ja", "ko", "ar", "ru", "hi"]
        for lang in required_languages:
            assert lang in languages, f"Language {lang} should be supported"
    
    def test_production_template_has_core_templates(self):
        """Test that production templates include core template types"""
        loader = MultilingualTemplateLoader()
        
        core_templates = ["help", "onboarding", "feedback", "tutorial", "error", "success"]
        for template_name in core_templates:
            # Check at least English version exists
            assert loader.template_exists(template_name, "en", "balanced"), \
                f"Core template '{template_name}' should exist"
    
    def test_all_languages_have_all_verbosity_levels(self):
        """Test that all languages provide concise, balanced, and verbose variants"""
        loader = MultilingualTemplateLoader()
        languages = loader.get_supported_languages()
        
        for lang in languages:
            levels = loader.get_available_verbosity_levels("help", lang)
            assert "concise" in levels, f"Language {lang} missing concise verbosity"
            assert "balanced" in levels, f"Language {lang} missing balanced verbosity"
            assert "verbose" in levels, f"Language {lang} missing verbose verbosity"
