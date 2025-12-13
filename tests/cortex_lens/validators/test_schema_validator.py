"""
Tests for Schema Validator

Tests data validation, schema compliance, error detection,
and completeness calculations.
"""

import pytest
from src.cortex_lens.validators.schema_validator import SchemaValidator


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def validator():
    """Create SchemaValidator instance"""
    return SchemaValidator()


@pytest.fixture
def valid_minimal_data():
    """Minimal valid data structure"""
    return {
        'metadata': {
            'repo_name': 'test-repo',
            'repo_type': 'console_app',
            'scan_timestamp': '2025-12-13T08:00:00',
            'cortex_version': '1.0.0'
        },
        'classification': {
            'primary_type': 'console_app',
            'confidence': 0.8
        }
    }


@pytest.fixture
def valid_complete_data():
    """Complete valid data structure with all sections"""
    return {
        'metadata': {
            'repo_name': 'test-repo',
            'repo_type': 'console_app',
            'scan_timestamp': '2025-12-13T08:00:00',
            'cortex_version': '1.0.0',
            'total_files': 150,
            'total_loc': 5000
        },
        'classification': {
            'primary_type': 'console_app',
            'confidence': 0.8,
            'secondary_types': [],
            'confidence_scores': {
                'console_app': 0.8,
                'api_service': 0.3
            }
        },
        'architecture': {
            'layers': ['presentation', 'business', 'data'],
            'pattern': 'layered'
        },
        'entities': {
            'classes': [
                {'name': 'MyClass', 'methods': 5, 'loc': 150}
            ],
            'functions': [
                {'name': 'my_function', 'complexity': 3}
            ]
        },
        'metrics': {
            'health_score': 75,
            'complexity_avg': 3.5,
            'test_coverage': 80
        },
        'security': {
            'vulnerabilities': [],
            'risk_level': 'low'
        },
        'comments': {
            'docstrings': 50,
            'inline_comments': 120,
            'total_comment_lines': 170
        },
        'narrative': {
            'summary': 'Test repository for console applications',
            'capabilities': ['CLI commands', 'Data processing'],
            'recommendations': ['Improve test coverage']
        }
    }


@pytest.fixture
def sample_classification():
    """Sample classification result"""
    return {
        'primary_type': 'console_app',
        'confidence_scores': {
            'console_app': 0.8
        }
    }


# ============================================================================
# Test Initialization
# ============================================================================

class TestValidatorInitialization:
    """Test SchemaValidator initialization"""
    
    def test_initialization(self, validator):
        """Validator should initialize correctly"""
        assert validator is not None
        assert hasattr(validator, 'validate')


# ============================================================================
# Test Valid Data
# ============================================================================

class TestValidData:
    """Test validation of valid data structures"""
    
    def test_validate_minimal_data(self, validator, valid_minimal_data, sample_classification):
        """Minimal valid data should pass validation"""
        result = validator.validate(valid_minimal_data, sample_classification)
        
        assert result['valid'] is True
        assert len(result['errors']) == 0
        assert result['completeness'] >= 0
        assert 'sections_present' in result
        assert 'total_sections' in result
    
    def test_validate_complete_data(self, validator, valid_complete_data, sample_classification):
        """Complete data should pass validation with 100% completeness"""
        result = validator.validate(valid_complete_data, sample_classification)
        
        assert result['valid'] is True
        assert len(result['errors']) == 0
        assert result['completeness'] == 100.0
        assert result['sections_present'] == 8
        assert result['total_sections'] == 8
    
    def test_validate_returns_correct_structure(self, validator, valid_minimal_data, sample_classification):
        """Result should contain all expected fields"""
        result = validator.validate(valid_minimal_data, sample_classification)
        
        assert 'valid' in result
        assert 'errors' in result
        assert 'warnings' in result
        assert 'completeness' in result
        assert 'sections_present' in result
        assert 'total_sections' in result
        
        assert isinstance(result['valid'], bool)
        assert isinstance(result['errors'], list)
        assert isinstance(result['warnings'], list)
        assert isinstance(result['completeness'], (int, float))


# ============================================================================
# Test Missing Required Sections
# ============================================================================

class TestMissingRequiredSections:
    """Test validation with missing required sections"""
    
    def test_missing_metadata_section(self, validator, sample_classification):
        """Missing metadata section should fail validation"""
        data = {
            'classification': {
                'primary_type': 'console_app'
            }
        }
        
        result = validator.validate(data, sample_classification)
        
        assert result['valid'] is False
        assert len(result['errors']) > 0
        assert any('metadata' in error.lower() for error in result['errors'])
    
    def test_missing_classification_section(self, validator, sample_classification):
        """Missing classification section should fail validation"""
        data = {
            'metadata': {
                'repo_name': 'test-repo',
                'repo_type': 'console_app',
                'scan_timestamp': '2025-12-13T08:00:00',
                'cortex_version': '1.0.0'
            }
        }
        
        result = validator.validate(data, sample_classification)
        
        assert result['valid'] is False
        assert len(result['errors']) > 0
        assert any('classification' in error.lower() for error in result['errors'])
    
    def test_missing_both_required_sections(self, validator, sample_classification):
        """Missing both required sections should fail with multiple errors"""
        data = {
            'entities': {
                'classes': []
            }
        }
        
        result = validator.validate(data, sample_classification)
        
        assert result['valid'] is False
        assert len(result['errors']) >= 2
        assert any('metadata' in error.lower() for error in result['errors'])
        assert any('classification' in error.lower() for error in result['errors'])


# ============================================================================
# Test Missing Required Fields
# ============================================================================

class TestMissingRequiredFields:
    """Test validation with missing required fields"""
    
    def test_missing_metadata_repo_name(self, validator, sample_classification):
        """Missing repo_name should fail validation"""
        data = {
            'metadata': {
                'repo_type': 'console_app',
                'scan_timestamp': '2025-12-13T08:00:00',
                'cortex_version': '1.0.0'
            },
            'classification': {
                'primary_type': 'console_app'
            }
        }
        
        result = validator.validate(data, sample_classification)
        
        assert result['valid'] is False
        assert any('repo_name' in error for error in result['errors'])
    
    def test_missing_metadata_repo_type(self, validator, sample_classification):
        """Missing repo_type should fail validation"""
        data = {
            'metadata': {
                'repo_name': 'test-repo',
                'scan_timestamp': '2025-12-13T08:00:00',
                'cortex_version': '1.0.0'
            },
            'classification': {
                'primary_type': 'console_app'
            }
        }
        
        result = validator.validate(data, sample_classification)
        
        assert result['valid'] is False
        assert any('repo_type' in error for error in result['errors'])
    
    def test_missing_metadata_timestamp(self, validator, sample_classification):
        """Missing scan_timestamp should fail validation"""
        data = {
            'metadata': {
                'repo_name': 'test-repo',
                'repo_type': 'console_app',
                'cortex_version': '1.0.0'
            },
            'classification': {
                'primary_type': 'console_app'
            }
        }
        
        result = validator.validate(data, sample_classification)
        
        assert result['valid'] is False
        assert any('scan_timestamp' in error for error in result['errors'])
    
    def test_missing_metadata_version(self, validator, sample_classification):
        """Missing cortex_version should fail validation"""
        data = {
            'metadata': {
                'repo_name': 'test-repo',
                'repo_type': 'console_app',
                'scan_timestamp': '2025-12-13T08:00:00'
            },
            'classification': {
                'primary_type': 'console_app'
            }
        }
        
        result = validator.validate(data, sample_classification)
        
        assert result['valid'] is False
        assert any('cortex_version' in error for error in result['errors'])
    
    def test_missing_all_metadata_fields(self, validator, sample_classification):
        """Missing all metadata fields should generate multiple errors"""
        data = {
            'metadata': {},
            'classification': {
                'primary_type': 'console_app'
            }
        }
        
        result = validator.validate(data, sample_classification)
        
        assert result['valid'] is False
        assert len(result['errors']) >= 4  # 4 required metadata fields
    
    def test_missing_primary_type(self, validator, sample_classification):
        """Missing primary_type should fail validation"""
        data = {
            'metadata': {
                'repo_name': 'test-repo',
                'repo_type': 'console_app',
                'scan_timestamp': '2025-12-13T08:00:00',
                'cortex_version': '1.0.0'
            },
            'classification': {
                'confidence': 0.8
            }
        }
        
        result = validator.validate(data, sample_classification)
        
        assert result['valid'] is False
        assert any('primary_type' in error for error in result['errors'])


# ============================================================================
# Test Warnings
# ============================================================================

class TestWarnings:
    """Test warning conditions"""
    
    def test_missing_confidence_generates_warning(self, validator, sample_classification):
        """Missing confidence should generate warning but not fail"""
        data = {
            'metadata': {
                'repo_name': 'test-repo',
                'repo_type': 'console_app',
                'scan_timestamp': '2025-12-13T08:00:00',
                'cortex_version': '1.0.0'
            },
            'classification': {
                'primary_type': 'console_app'
            }
        }
        
        result = validator.validate(data, sample_classification)
        
        # Should still be valid (warnings don't fail validation)
        assert result['valid'] is True
        assert len(result['warnings']) > 0
        assert any('confidence' in warning.lower() for warning in result['warnings'])


# ============================================================================
# Test Completeness Calculation
# ============================================================================

class TestCompletenessCalculation:
    """Test completeness percentage calculation"""
    
    def test_completeness_with_two_sections(self, validator, valid_minimal_data, sample_classification):
        """Two sections should give 25% completeness (2/8)"""
        result = validator.validate(valid_minimal_data, sample_classification)
        
        assert result['sections_present'] == 2
        assert result['total_sections'] == 8
        assert result['completeness'] == 25.0
    
    def test_completeness_with_all_sections(self, validator, valid_complete_data, sample_classification):
        """All 8 sections should give 100% completeness"""
        result = validator.validate(valid_complete_data, sample_classification)
        
        assert result['sections_present'] == 8
        assert result['total_sections'] == 8
        assert result['completeness'] == 100.0
    
    def test_completeness_with_partial_sections(self, validator, sample_classification):
        """Partial sections should calculate correctly"""
        data = {
            'metadata': {'repo_name': 'test', 'repo_type': 'console_app', 'scan_timestamp': '2025-12-13', 'cortex_version': '1.0'},
            'classification': {'primary_type': 'console_app'},
            'architecture': {'layers': []},
            'entities': {'classes': []},
            'metrics': {'health_score': 75}
        }
        
        result = validator.validate(data, sample_classification)
        
        assert result['sections_present'] == 5
        assert result['completeness'] == 62.5  # 5/8 * 100
    
    def test_empty_sections_not_counted(self, validator, sample_classification):
        """Empty sections should not be counted"""
        data = {
            'metadata': {'repo_name': 'test', 'repo_type': 'console_app', 'scan_timestamp': '2025-12-13', 'cortex_version': '1.0'},
            'classification': {'primary_type': 'console_app'},
            'architecture': {},  # Empty - should not count
            'entities': None,  # Falsy - should not count
            'metrics': {}  # Empty - should not count
        }
        
        result = validator.validate(data, sample_classification)
        
        # Only metadata and classification should count (both non-empty)
        assert result['sections_present'] == 2
        assert result['completeness'] == 25.0


# ============================================================================
# Test Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_empty_data_dict(self, validator, sample_classification):
        """Empty data dict should fail validation"""
        data = {}
        
        result = validator.validate(data, sample_classification)
        
        assert result['valid'] is False
        assert len(result['errors']) >= 2  # Missing metadata and classification
        assert result['completeness'] == 0.0
    
    def test_none_data(self, validator, sample_classification):
        """None data should not crash"""
        # This should raise an error or handle gracefully
        # Depending on implementation, adjust assertion
        try:
            result = validator.validate(None, sample_classification)
            # If it doesn't crash, check it marked as invalid
            assert result['valid'] is False
        except (TypeError, AttributeError):
            # It's OK if it raises an error for None input
            pass
    
    def test_extra_sections_allowed(self, validator, valid_minimal_data, sample_classification):
        """Extra sections should not affect validation"""
        data = valid_minimal_data.copy()
        data['custom_section'] = {'custom_field': 'value'}
        
        result = validator.validate(data, sample_classification)
        
        assert result['valid'] is True
    
    def test_nested_empty_dicts(self, validator, sample_classification):
        """Nested empty dicts should be handled"""
        data = {
            'metadata': {
                'repo_name': 'test',
                'repo_type': 'console_app',
                'scan_timestamp': '2025-12-13',
                'cortex_version': '1.0',
                'extra': {}
            },
            'classification': {
                'primary_type': 'console_app',
                'details': {}
            }
        }
        
        result = validator.validate(data, sample_classification)
        
        assert result['valid'] is True


# ============================================================================
# Test Multiple Errors
# ============================================================================

class TestMultipleErrors:
    """Test handling of multiple validation errors"""
    
    def test_multiple_missing_fields(self, validator, sample_classification):
        """Multiple missing fields should generate multiple errors"""
        data = {
            'metadata': {
                'repo_name': 'test'
                # Missing: repo_type, scan_timestamp, cortex_version
            },
            'classification': {}  # Missing: primary_type
        }
        
        result = validator.validate(data, sample_classification)
        
        assert result['valid'] is False
        assert len(result['errors']) >= 4
    
    def test_errors_are_descriptive(self, validator, sample_classification):
        """Error messages should be descriptive"""
        data = {
            'metadata': {
                'repo_name': 'test'
            },
            'classification': {}
        }
        
        result = validator.validate(data, sample_classification)
        
        # Check that errors contain field names
        errors_text = ' '.join(result['errors'])
        assert 'repo_type' in errors_text or 'metadata' in errors_text
