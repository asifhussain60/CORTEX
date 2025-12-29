"""
Tests for Context Validator

Phase 5 Task 5.8: Context Validator Tests
Comprehensive test suite for context validation with auto-retrieval.

Test Coverage:
- Basic validation (required/optional context)
- Auto-retrieval from knowledge graph
- Context inference strategies
- Quality assessment (completeness, freshness, types)
- Edge cases and error handling

Author: CORTEX Development Team
Version: 1.0.0
Created: 2025-12-21
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from src.orchestration_4_0.frameworks.context_validator import (
    ContextValidator,
    ContextValidation,
    ContextQuality
)


class TestBasicValidation:
    """Test basic context validation"""
    
    @pytest.mark.asyncio
    async def test_validate_all_required_present(self):
        """Test validation when all required context is present"""
        validator = ContextValidator()
        
        context = {
            'project_root': '/path/to/project',
            'language': 'python',
            'framework': 'flask'
        }
        
        execution_plan = {
            'required_context': ['project_root', 'language'],
            'optional_context': ['framework']
        }
        
        result = await validator.validate_context_sufficiency(context, execution_plan)
        
        assert result.is_valid()
        assert result.has_requirements
        assert len(result.missing_required) == 0
        assert len(result.missing_optional) == 0
        assert result.quality in [ContextQuality.EXCELLENT, ContextQuality.GOOD]
    
    @pytest.mark.asyncio
    async def test_validate_missing_required(self):
        """Test validation when required context is missing (and cannot be inferred)"""
        validator = ContextValidator()
        
        context = {
            'language': 'python'
        }
        
        execution_plan = {
            'required_context': ['project_root', 'language', 'repository_url'],
            'optional_context': ['framework']
        }
        
        result = await validator.validate_context_sufficiency(context, execution_plan)
        
        assert not result.is_valid()
        assert not result.has_requirements
        assert 'project_root' in result.missing_required
        assert 'repository_url' in result.missing_required
        assert result.quality == ContextQuality.INSUFFICIENT
    
    @pytest.mark.asyncio
    async def test_validate_missing_optional_only(self):
        """Test validation when only optional context is missing"""
        validator = ContextValidator()
        
        context = {
            'project_root': '/path/to/project',
            'language': 'python'
        }
        
        execution_plan = {
            'required_context': ['project_root', 'language'],
            'optional_context': ['framework', 'version', 'author']
        }
        
        result = await validator.validate_context_sufficiency(context, execution_plan)
        
        assert result.is_valid()
        assert result.has_requirements
        assert len(result.missing_required) == 0
        assert len(result.missing_optional) == 3
        assert result.quality in [ContextQuality.ACCEPTABLE, ContextQuality.GOOD]


class TestAutoRetrieval:
    """Test auto-retrieval from knowledge graph"""
    
    @pytest.mark.asyncio
    async def test_retrieve_from_knowledge_graph(self):
        """Test successful retrieval from knowledge graph"""
        # Mock knowledge graph
        mock_kg = Mock()
        mock_kg.query = AsyncMock(return_value='/inferred/project/root')
        
        validator = ContextValidator(knowledge_graph=mock_kg)
        
        context = {
            'language': 'python'
        }
        
        execution_plan = {
            'required_context': ['project_root', 'language'],
            'optional_context': []
        }
        
        result = await validator.validate_context_sufficiency(context, execution_plan)
        
        # Should have retrieved project_root
        assert result.is_valid()
        assert 'project_root' in result.context
        assert 'project_root' in result.retrieved_items
        assert result.context['project_root'] == '/inferred/project/root'
        
        # Verify knowledge graph was queried
        mock_kg.query.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_retrieve_multiple_items(self):
        """Test retrieval of multiple missing items"""
        # Mock knowledge graph with multiple responses
        mock_kg = Mock()
        
        async def mock_query(category, key, hint):
            responses = {
                'project_root': '/project/root',
                'test_framework': 'pytest'
            }
            return responses.get(key)
        
        mock_kg.query = AsyncMock(side_effect=mock_query)
        
        validator = ContextValidator(knowledge_graph=mock_kg)
        
        context = {
            'language': 'python'
        }
        
        execution_plan = {
            'required_context': ['project_root', 'language', 'test_framework'],
            'optional_context': []
        }
        
        result = await validator.validate_context_sufficiency(context, execution_plan)
        
        assert result.is_valid()
        assert len(result.retrieved_items) == 2
        assert result.context['project_root'] == '/project/root'
        assert result.context['test_framework'] == 'pytest'
    
    @pytest.mark.asyncio
    async def test_retrieval_failure_graceful(self):
        """Test graceful handling when retrieval fails"""
        # Mock knowledge graph that returns None
        mock_kg = Mock()
        mock_kg.query = AsyncMock(return_value=None)
        
        validator = ContextValidator(knowledge_graph=mock_kg)
        
        context = {
            'language': 'python'
        }
        
        execution_plan = {
            'required_context': ['project_root', 'language'],
            'optional_context': []
        }
        
        result = await validator.validate_context_sufficiency(context, execution_plan)
        
        # Should still be invalid (couldn't retrieve)
        assert not result.is_valid()
        assert 'project_root' in result.missing_required


class TestContextInference:
    """Test context inference strategies"""
    
    @pytest.mark.asyncio
    async def test_infer_project_root_from_file_path(self):
        """Test inferring project root from file path"""
        validator = ContextValidator()
        
        context = {
            'file_path': '/home/user/project/src/main.py',
            'language': 'python'
        }
        
        execution_plan = {
            'required_context': ['project_root', 'language'],
            'optional_context': []
        }
        
        result = await validator.validate_context_sufficiency(context, execution_plan)
        
        assert result.is_valid()
        assert 'project_root' in result.context
        assert result.context['project_root'] == '/home/user/project'
        assert 'project_root' in result.retrieved_items
    
    @pytest.mark.asyncio
    async def test_infer_repository_name_from_url(self):
        """Test inferring repository name from URL"""
        validator = ContextValidator()
        
        context = {
            'repository_url': 'https://github.com/user/my-repo.git',
            'language': 'python'
        }
        
        execution_plan = {
            'required_context': ['repository_name', 'language'],
            'optional_context': []
        }
        
        result = await validator.validate_context_sufficiency(context, execution_plan)
        
        assert result.is_valid()
        assert result.context['repository_name'] == 'my-repo'
    
    @pytest.mark.asyncio
    async def test_infer_using_defaults(self):
        """Test inference using default values"""
        validator = ContextValidator()
        
        context = {
            'project_root': '/project'
        }
        
        execution_plan = {
            'required_context': ['project_root', 'language', 'test_framework'],
            'optional_context': []
        }
        
        result = await validator.validate_context_sufficiency(context, execution_plan)
        
        assert result.is_valid()
        assert result.context['language'] == 'python'
        assert result.context['test_framework'] == 'pytest'
    
    @pytest.mark.asyncio
    async def test_infer_count_from_collection(self):
        """Test inferring count from collection"""
        validator = ContextValidator()
        
        context = {
            'files': ['a.py', 'b.py', 'c.py'],
            'language': 'python'
        }
        
        execution_plan = {
            'required_context': ['file_count', 'language'],
            'optional_context': []
        }
        
        result = await validator.validate_context_sufficiency(context, execution_plan)
        
        assert result.is_valid()
        assert result.context['file_count'] == 3


class TestQualityAssessment:
    """Test context quality assessment"""
    
    @pytest.mark.asyncio
    async def test_detect_empty_values(self):
        """Test detection of empty or None values"""
        validator = ContextValidator()
        
        context = {
            'project_root': '/project',
            'language': None,
            'framework': '',
            'files': []
        }
        
        execution_plan = {
            'required_context': ['project_root'],
            'optional_context': []
        }
        
        result = await validator.validate_context_sufficiency(context, execution_plan)
        
        assert result.is_valid()
        assert len(result.quality_issues) >= 3
        assert any('None' in issue for issue in result.quality_issues)
        assert any('empty' in issue.lower() for issue in result.quality_issues)
    
    @pytest.mark.asyncio
    async def test_detect_stale_timestamp(self):
        """Test detection of stale timestamps"""
        validator = ContextValidator()
        
        old_timestamp = datetime.now() - timedelta(days=5)
        
        context = {
            'project_root': '/project',
            'timestamp': old_timestamp
        }
        
        execution_plan = {
            'required_context': ['project_root'],
            'optional_context': []
        }
        
        result = await validator.validate_context_sufficiency(context, execution_plan)
        
        assert result.is_valid()
        assert any('stale' in issue.lower() for issue in result.quality_issues)
    
    @pytest.mark.asyncio
    async def test_check_type_requirements(self):
        """Test type checking against requirements"""
        validator = ContextValidator()
        
        context = {
            'project_root': '/project',
            'file_count': '10',  # Should be int
            'complexity': 5.5
        }
        
        execution_plan = {
            'required_context': ['project_root', 'file_count'],
            'optional_context': [],
            'context_types': {
                'file_count': int,
                'complexity': float
            }
        }
        
        result = await validator.validate_context_sufficiency(context, execution_plan)
        
        assert result.is_valid()
        assert any('file_count' in issue for issue in result.quality_issues)
        assert any('should be int' in issue for issue in result.quality_issues)
    
    @pytest.mark.asyncio
    async def test_check_value_constraints(self):
        """Test value constraint validation"""
        validator = ContextValidator()
        
        context = {
            'project_root': '/project',
            'complexity': 150,
            'priority': 'urgent'
        }
        
        execution_plan = {
            'required_context': ['project_root', 'complexity'],
            'optional_context': [],
            'context_constraints': {
                'complexity': {'min': 0, 'max': 100},
                'priority': {'allowed': ['low', 'medium', 'high']}
            }
        }
        
        result = await validator.validate_context_sufficiency(context, execution_plan)
        
        assert result.is_valid()
        assert len(result.quality_issues) >= 2
        assert any('exceeds maximum' in issue for issue in result.quality_issues)
        assert any('not in allowed list' in issue for issue in result.quality_issues)


class TestQualityScoring:
    """Test quality scoring system"""
    
    @pytest.mark.asyncio
    async def test_excellent_quality(self):
        """Test excellent quality (all present, no issues)"""
        validator = ContextValidator()
        
        context = {
            'project_root': '/project',
            'language': 'python',
            'framework': 'flask'
        }
        
        execution_plan = {
            'required_context': ['project_root', 'language'],
            'optional_context': ['framework']
        }
        
        result = await validator.validate_context_sufficiency(context, execution_plan)
        
        assert result.quality == ContextQuality.EXCELLENT
        assert result.get_quality_score() == 100.0
    
    @pytest.mark.asyncio
    async def test_good_quality(self):
        """Test good quality (required + some optional, minor issues)"""
        validator = ContextValidator()
        
        context = {
            'project_root': '/project',
            'language': 'python',
            'framework': ''  # Empty value (minor issue)
        }
        
        execution_plan = {
            'required_context': ['project_root', 'language'],
            'optional_context': ['framework']
        }
        
        result = await validator.validate_context_sufficiency(context, execution_plan)
        
        assert result.quality == ContextQuality.GOOD
        score = result.get_quality_score()
        assert 70 <= score < 100
    
    @pytest.mark.asyncio
    async def test_acceptable_quality(self):
        """Test acceptable quality (required only, some issues)"""
        validator = ContextValidator()
        
        context = {
            'project_root': '/project',
            'language': None,  # Quality issue
            'version': ''      # Quality issue
        }
        
        execution_plan = {
            'required_context': ['project_root'],
            'optional_context': ['framework', 'version']
        }
        
        result = await validator.validate_context_sufficiency(context, execution_plan)
        
        # After inference, should be acceptable
        score = result.get_quality_score()
        assert score > 0


class TestMetrics:
    """Test metrics tracking"""
    
    @pytest.mark.asyncio
    async def test_metrics_initialization(self):
        """Test metrics are initialized correctly"""
        validator = ContextValidator()
        metrics = validator.get_metrics()
        
        assert metrics['total_validations'] == 0
        assert metrics['valid_contexts'] == 0
        assert metrics['auto_retrievals'] == 0
        assert metrics['inference_attempts'] == 0
    
    @pytest.mark.asyncio
    async def test_metrics_track_validations(self):
        """Test validation counts are tracked"""
        validator = ContextValidator()
        
        context = {'project_root': '/project'}
        execution_plan = {'required_context': ['project_root'], 'optional_context': []}
        
        await validator.validate_context_sufficiency(context, execution_plan)
        await validator.validate_context_sufficiency(context, execution_plan)
        
        metrics = validator.get_metrics()
        assert metrics['total_validations'] == 2
        assert metrics['valid_contexts'] == 2
    
    @pytest.mark.asyncio
    async def test_metrics_track_retrievals(self):
        """Test retrieval counts are tracked"""
        mock_kg = Mock()
        mock_kg.query = AsyncMock(return_value='/project/root')
        
        validator = ContextValidator(knowledge_graph=mock_kg)
        
        context = {'language': 'python'}
        execution_plan = {'required_context': ['project_root', 'language'], 'optional_context': []}
        
        await validator.validate_context_sufficiency(context, execution_plan)
        
        metrics = validator.get_metrics()
        assert metrics['auto_retrievals'] >= 1
    
    @pytest.mark.asyncio
    async def test_metrics_reset(self):
        """Test metrics can be reset"""
        validator = ContextValidator()
        
        context = {'project_root': '/project'}
        execution_plan = {'required_context': ['project_root'], 'optional_context': []}
        
        await validator.validate_context_sufficiency(context, execution_plan)
        
        validator.reset_metrics()
        metrics = validator.get_metrics()
        
        assert metrics['total_validations'] == 0
        assert metrics['valid_contexts'] == 0


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    @pytest.mark.asyncio
    async def test_empty_context(self):
        """Test validation with empty context"""
        validator = ContextValidator()
        
        context = {}
        execution_plan = {
            'required_context': ['project_root'],
            'optional_context': []
        }
        
        result = await validator.validate_context_sufficiency(context, execution_plan)
        
        assert not result.is_valid()
        assert 'project_root' in result.missing_required
    
    @pytest.mark.asyncio
    async def test_empty_requirements(self):
        """Test validation with no requirements"""
        validator = ContextValidator()
        
        context = {'project_root': '/project'}
        execution_plan = {
            'required_context': [],
            'optional_context': []
        }
        
        result = await validator.validate_context_sufficiency(context, execution_plan)
        
        assert result.is_valid()
        assert result.quality == ContextQuality.EXCELLENT
    
    @pytest.mark.asyncio
    async def test_knowledge_graph_exception(self):
        """Test graceful handling of knowledge graph exceptions"""
        mock_kg = Mock()
        mock_kg.query = AsyncMock(side_effect=Exception("Connection error"))
        
        validator = ContextValidator(knowledge_graph=mock_kg)
        
        context = {'language': 'python'}
        execution_plan = {'required_context': ['project_root', 'language'], 'optional_context': []}
        
        # Should not raise exception
        result = await validator.validate_context_sufficiency(context, execution_plan)
        
        assert not result.is_valid()
    
    @pytest.mark.asyncio
    async def test_invalid_timestamp_format(self):
        """Test handling of invalid timestamp formats"""
        validator = ContextValidator()
        
        context = {
            'project_root': '/project',
            'timestamp': 'invalid-date'
        }
        
        execution_plan = {'required_context': ['project_root'], 'optional_context': []}
        
        result = await validator.validate_context_sufficiency(context, execution_plan)
        
        assert result.is_valid()
        assert any('timestamp' in issue.lower() for issue in result.quality_issues)
    
    @pytest.mark.asyncio
    async def test_type_string_conversion(self):
        """Test type string to type conversion"""
        validator = ContextValidator()
        
        context = {
            'project_root': '/project',
            'count': '10'
        }
        
        execution_plan = {
            'required_context': ['project_root'],
            'optional_context': [],
            'context_types': {
                'count': 'int'  # String type specification
            }
        }
        
        result = await validator.validate_context_sufficiency(context, execution_plan)
        
        assert result.is_valid()
        assert any('count' in issue for issue in result.quality_issues)
