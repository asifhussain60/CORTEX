"""
Tests for TypeExtractor - Type hint analysis
"""

import ast
import pytest

from src.orchestration_4_0.orchestrators.documentation.extractors.type_extractor import TypeExtractor


@pytest.fixture
def extractor():
    """Create a TypeExtractor instance"""
    return TypeExtractor()


class TestTypeExtractor:
    """Tests for TypeExtractor class"""
    
    def test_extract_simple_type(self, extractor):
        """Test extracting simple type"""
        annotation = ast.parse("x: int").body[0].annotation
        type_info = extractor.extract_type_info(annotation)
        
        assert type_info['raw'] == 'int'
        assert type_info['base'] == 'int'
        assert type_info['args'] == []
        assert type_info['optional'] is False
        assert type_info['complexity'] == 0
    
    def test_extract_none_type(self, extractor):
        """Test extracting None annotation"""
        type_info = extractor.extract_type_info(None)
        
        assert type_info['raw'] == 'Any'
        assert type_info['base'] == 'Any'
        assert type_info['optional'] is False
    
    def test_extract_generic_type(self, extractor):
        """Test extracting generic type"""
        annotation = ast.parse("x: List[int]").body[0].annotation
        type_info = extractor.extract_type_info(annotation)
        
        assert type_info['base'] == 'List'
        assert 'int' in type_info['args']
        assert type_info['complexity'] == 2
    
    def test_extract_optional_type(self, extractor):
        """Test extracting Optional type"""
        annotation = ast.parse("x: Optional[str]").body[0].annotation
        type_info = extractor.extract_type_info(annotation)
        
        assert type_info['optional'] is True
        assert 'Optional[' in type_info['raw']
    
    def test_extract_union_type(self, extractor):
        """Test extracting Union type"""
        annotation = ast.parse("x: Union[str, None]").body[0].annotation
        type_info = extractor.extract_type_info(annotation)
        
        assert type_info['optional'] is True
        assert 'Union[' in type_info['raw']
    
    def test_extract_dict_type(self, extractor):
        """Test extracting Dict with multiple type args"""
        annotation = ast.parse("x: Dict[str, int]").body[0].annotation
        type_info = extractor.extract_type_info(annotation)
        
        assert type_info['base'] == 'Dict'
        assert len(type_info['args']) == 2
        assert 'str' in type_info['args']
        assert 'int' in type_info['args']
        assert type_info['complexity'] == 3
    
    def test_extract_nested_generic(self, extractor):
        """Test extracting nested generic types"""
        annotation = ast.parse("x: List[Dict[str, Any]]").body[0].annotation
        type_info = extractor.extract_type_info(annotation)
        
        assert type_info['base'] == 'List'
        assert type_info['complexity'] >= 4
    
    def test_calculate_complexity_simple(self, extractor):
        """Test complexity calculation for simple types"""
        annotation = ast.parse("x: str").body[0].annotation
        complexity = extractor._calculate_complexity(annotation)
        assert complexity == 0
    
    def test_calculate_complexity_generic(self, extractor):
        """Test complexity calculation for generic types"""
        annotation = ast.parse("x: List[int]").body[0].annotation
        complexity = extractor._calculate_complexity(annotation)
        assert complexity == 2
    
    def test_calculate_complexity_nested(self, extractor):
        """Test complexity calculation for nested types"""
        annotation = ast.parse("x: Dict[str, List[int]]").body[0].annotation
        complexity = extractor._calculate_complexity(annotation)
        assert complexity >= 4
    
    def test_format_type_for_docs_simple(self, extractor):
        """Test formatting simple type for docs"""
        type_info = {'raw': 'int', 'base': 'int', 'args': [], 'optional': False, 'complexity': 0}
        formatted = extractor.format_type_for_docs(type_info)
        assert formatted == 'int'
    
    def test_format_type_for_docs_optional(self, extractor):
        """Test formatting Optional type for docs"""
        type_info = {'raw': 'Optional[str]', 'base': 'Optional', 'args': ['str'], 'optional': True, 'complexity': 2}
        formatted = extractor.format_type_for_docs(type_info)
        assert 'Optional' in formatted or '|' in formatted
    
    def test_extract_return_type_description(self, extractor):
        """Test extracting return type description from docstring"""
        docstring = """
        Sample function
        
        Returns:
            The result of the operation
        """
        description = extractor.extract_return_type_description(docstring)
        assert description == "The result of the operation"
    
    def test_extract_return_type_description_none(self, extractor):
        """Test extracting return description when none exists"""
        docstring = "Simple docstring without returns section"
        description = extractor.extract_return_type_description(docstring)
        assert description is None
    
    def test_extract_param_descriptions(self, extractor):
        """Test extracting parameter descriptions from docstring"""
        docstring = """
        Sample function
        
        Args:
            param1: First parameter description
            param2: Second parameter description
                with continuation
        """
        descriptions = extractor.extract_param_descriptions(docstring)
        
        assert 'param1' in descriptions
        assert descriptions['param1'] == "First parameter description"
        assert 'param2' in descriptions
        assert "Second parameter description with continuation" in descriptions['param2']
    
    def test_extract_param_descriptions_empty(self, extractor):
        """Test extracting param descriptions when none exist"""
        docstring = "Simple docstring without args section"
        descriptions = extractor.extract_param_descriptions(docstring)
        assert descriptions == {}
    
    def test_extract_param_descriptions_with_types(self, extractor):
        """Test extracting param descriptions with type annotations"""
        docstring = """
        Sample function
        
        Args:
            name: The name parameter
            count: The count parameter
            optional: An optional parameter
        
        Returns:
            Result value
        """
        descriptions = extractor.extract_param_descriptions(docstring)
        
        assert len(descriptions) == 3
        assert 'name' in descriptions
        assert 'count' in descriptions
        assert 'optional' in descriptions
