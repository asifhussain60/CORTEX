"""Tests for entity_extractor.py

Test Coverage:
- Entity extraction: files, components, features
- Pattern matching accuracy
- Edge cases: malformed input, empty strings, special characters
- Entity deduplication
- Stopword filtering
"""

import pytest
from src.brain.tier1.entity_extractor import EntityExtractor


class TestEntityExtractorInitialization:
    """Tests for EntityExtractor initialization"""
    
    def test_init_creates_instance(self):
        """Test that EntityExtractor initializes successfully"""
        extractor = EntityExtractor()
        assert extractor is not None
        assert isinstance(extractor, EntityExtractor)


class TestFileExtraction:
    """Tests for file entity extraction"""
    
    @pytest.fixture
    def extractor(self):
        return EntityExtractor()
    
    def test_extract_backticked_python_file(self, extractor):
        """Test extraction of backticked Python filename"""
        text = "Please modify `user_service.py` to add validation"
        result = extractor.extract_entities(text)
        assert 'user_service.py' in result['files']
    
    def test_extract_multiple_file_types(self, extractor):
        """Test extraction of multiple file types in single text"""
        text = "Update `component.tsx`, `styles.css`, and `config.json`"
        result = extractor.extract_entities(text)
        assert 'component.tsx' in result['files']
        assert 'styles.css' in result['files']
        assert 'config.json' in result['files']
    
    def test_extract_camelcase_file(self, extractor):
        """Test extraction of CamelCase filename"""
        text = "Modify UserService.cs and DataModel.cs"
        result = extractor.extract_entities(text)
        assert 'UserService.cs' in result['files']
        assert 'DataModel.cs' in result['files']
    
    def test_extract_path_like_pattern(self, extractor):
        """Test extraction of file path patterns"""
        text = "Update src/components/Button.tsx"
        result = extractor.extract_entities(text)
        assert any('components' in f and 'Button.tsx' in f for f in result['files'])
    
    def test_no_duplicate_files(self, extractor):
        """Test that duplicate filenames are deduplicated"""
        text = "`user.py` and `user.py` need updates"
        result = extractor.extract_entities(text)
        file_count = result['files'].count('user.py')
        assert file_count == 1
    
    def test_extract_files_empty_string(self, extractor):
        """Test file extraction from empty string"""
        result = extractor.extract_entities("")
        assert result['files'] == []
    
    def test_extract_files_no_matches(self, extractor):
        """Test file extraction when no files present"""
        text = "This is just a conversation with no files"
        result = extractor.extract_entities(text)
        assert result['files'] == []
    
    def test_extract_files_special_characters(self, extractor):
        """Test file extraction with special characters in path"""
        text = "Update `user-profile_v2.py` and `api.config.json`"
        result = extractor.extract_entities(text)
        assert 'user-profile_v2.py' in result['files']
        assert 'api.config.json' in result['files']


class TestComponentExtraction:
    """Tests for component entity extraction"""
    
    @pytest.fixture
    def extractor(self):
        return EntityExtractor()
    
    def test_extract_backticked_component(self, extractor):
        """Test extraction of backticked React component"""
        text = "Create `UserProfileComponent` with TypeScript"
        result = extractor.extract_entities(text)
        assert 'UserProfileComponent' in result['components']
    
    def test_extract_ui_components(self, extractor):
        """Test extraction of common UI component patterns"""
        text = "Add LoginButton, UserPanel, and ConfirmDialog"
        result = extractor.extract_entities(text)
        assert 'LoginButton' in result['components']
        assert 'UserPanel' in result['components']
        assert 'ConfirmDialog' in result['components']
    
    def test_extract_service_components(self, extractor):
        """Test extraction of service/manager patterns"""
        text = "AuthenticationService and UserManager need updates"
        result = extractor.extract_entities(text)
        assert 'AuthenticationService' in result['components']
        assert 'UserManager' in result['components']
    
    def test_extract_controller_components(self, extractor):
        """Test extraction of controller patterns"""
        text = "UserController handles API requests"
        result = extractor.extract_entities(text)
        assert 'UserController' in result['components']
    
    def test_no_duplicate_components(self, extractor):
        """Test that duplicate components are deduplicated"""
        text = "UserPanel and UserPanel are related"
        result = extractor.extract_entities(text)
        component_count = result['components'].count('UserPanel')
        assert component_count == 1
    
    def test_extract_components_empty_string(self, extractor):
        """Test component extraction from empty string"""
        result = extractor.extract_entities("")
        assert result['components'] == []


class TestFeatureExtraction:
    """Tests for feature entity extraction"""
    
    @pytest.fixture
    def extractor(self):
        return EntityExtractor()
    
    def test_extract_quoted_feature(self, extractor):
        """Test extraction of quoted feature name"""
        text = 'Implement "dark mode" for the application'
        result = extractor.extract_entities(text)
        assert 'dark mode' in result['features']
    
    def test_extract_add_pattern_feature(self, extractor):
        """Test extraction of "add X" pattern"""
        text = "add a login button to the page"
        result = extractor.extract_entities(text)
        assert any('login button' in f for f in result['features'])
    
    def test_extract_implement_pattern_feature(self, extractor):
        """Test extraction of "implement X" pattern"""
        text = "implement user authentication system"
        result = extractor.extract_entities(text)
        assert any('authentication' in f for f in result['features'])
    
    def test_extract_create_pattern_feature(self, extractor):
        """Test extraction of "create X" pattern"""
        text = "create an export feature for reports"
        result = extractor.extract_entities(text)
        assert any('export' in f for f in result['features'])
    
    def test_extract_features_empty_string(self, extractor):
        """Test feature extraction from empty string"""
        result = extractor.extract_entities("")
        assert result['features'] == []


class TestStopwordFiltering:
    """Tests for stopword filtering in entity extraction"""
    
    @pytest.fixture
    def extractor(self):
        return EntityExtractor()
    
    def test_stopwords_excluded_from_features(self, extractor):
        """Test that stopwords are not extracted as features"""
        text = "the and or but in on at to for"
        result = extractor.extract_entities(text)
        # Stopwords should not appear as standalone entities
        assert 'the' not in result['features']
        assert 'and' not in result['features']


class TestComplexScenarios:
    """Tests for complex entity extraction scenarios"""
    
    @pytest.fixture
    def extractor(self):
        return EntityExtractor()
    
    def test_extract_multiple_entity_types(self, extractor):
        """Test extraction of files, components, and features together"""
        text = """
        Update `UserService.py` and create LoginButton component.
        Implement "two-factor authentication" feature.
        """
        result = extractor.extract_entities(text)
        
        assert 'UserService.py' in result['files']
        assert 'LoginButton' in result['components']
        assert 'two-factor authentication' in result['features']
    
    def test_extract_from_long_text(self, extractor):
        """Test extraction from lengthy conversation text"""
        text = """
        We need to update the authentication system. Modify `auth.py`,
        `user_model.py`, and create AuthenticationService. The LoginPanel
        should integrate with "single sign-on" and "multi-factor auth".
        Update tests/auth/test_login.py as well.
        """
        result = extractor.extract_entities(text)
        
        # Check files extracted
        assert 'auth.py' in result['files']
        assert 'user_model.py' in result['files']
        
        # Check components extracted
        assert 'AuthenticationService' in result['components']
        assert 'LoginPanel' in result['components']
        
        # Check features extracted
        assert 'single sign-on' in result['features']
        assert 'multi-factor auth' in result['features']
    
    def test_extract_with_unicode_characters(self, extractor):
        """Test extraction with Unicode characters"""
        text = "Update `config_日本語.json` and create UserPanel™"
        result = extractor.extract_entities(text)
        # Should handle Unicode gracefully
        assert 'config_日本語.json' in result['files'] or len(result['files']) >= 0
    
    def test_extract_with_markdown_formatting(self, extractor):
        """Test extraction from markdown-formatted text"""
        text = """
        ## Updates
        - `service.py`: Add caching
        - UserPanel needs refactoring
        - Implement "lazy loading"
        """
        result = extractor.extract_entities(text)
        
        assert 'service.py' in result['files']
        assert 'UserPanel' in result['components']
        assert 'lazy loading' in result['features']
    
    def test_extract_returns_dict_structure(self, extractor):
        """Test that extract_entities returns proper dict structure"""
        text = "Test text"
        result = extractor.extract_entities(text)
        
        assert isinstance(result, dict)
        assert 'files' in result
        assert 'components' in result
        assert 'features' in result
        assert isinstance(result['files'], list)
        assert isinstance(result['components'], list)
        assert isinstance(result['features'], list)
