"""
Test suite for CORE-033: Tool Description Accuracy Validation.

Validates:
- Tool description/capability alignment
- Parameter documentation
- Return type specification
- Error handling documentation
"""

import pytest
from src.core.governance.tool_description_validator import (
    ToolDescriptionValidator,
    ToolDescription,
    ParameterSpec,
    ReturnSpec,
    AccuracyLevel,
    ValidationIssueType,
)


class TestParameterSpec:
    """Tests for parameter specification."""
    
    def test_create_parameter_spec(self):
        """Test creating parameter specification."""
        param = ParameterSpec(
            name="input",
            type_hint="str",
            description="Input text"
        )
        assert param.name == "input"
        assert param.type_hint == "str"
    
    def test_parameter_with_default(self):
        """Test parameter with default value."""
        param = ParameterSpec(
            name="count",
            type_hint="int",
            description="Number of items",
            required=False,
            default_value=10
        )
        assert param.default_value == 10


class TestReturnSpec:
    """Tests for return specification."""
    
    def test_create_return_spec(self):
        """Test creating return specification."""
        ret = ReturnSpec(
            type_hint="str",
            description="Output result"
        )
        assert ret.type_hint == "str"


class TestToolDescriptionValidator:
    """Tests for tool description validator."""
    
    def test_validator_initialization(self):
        """Test validator initialization."""
        validator = ToolDescriptionValidator()
        assert len(validator.registered_tools) == 0
        assert len(validator.validation_history) == 0
    
    def test_register_tool(self):
        """Test registering a tool."""
        validator = ToolDescriptionValidator()
        desc = ToolDescription(
            name="sample_tool",
            description="A sample tool"
        )
        validator.register_tool("sample_tool", desc)
        assert "sample_tool" in validator.registered_tools
    
    def test_validate_nonexistent_tool(self):
        """Test validation of non-existent tool."""
        validator = ToolDescriptionValidator()
        result = validator.validate_tool("nonexistent")
        assert not result.success
        assert "not found" in result.error
    
    def test_validate_good_description(self):
        """Test validation of good tool description."""
        validator = ToolDescriptionValidator()
        
        desc = ToolDescription(
            name="test_tool",
            description="This is a comprehensive tool description that explains what it does",
            parameters=[
                ParameterSpec(
                    name="input",
                    type_hint="str",
                    description="The input text to process"
                )
            ],
            return_spec=ReturnSpec(
                type_hint="str",
                description="The processed output"
            ),
            error_handling=["ValueError", "TypeError"]
        )
        
        validator.register_tool("test_tool", desc)
        result = validator.validate_tool("test_tool")
        
        assert result.success
        assert result.value.is_valid
        assert result.value.accuracy_percentage >= 85
    
    def test_validate_missing_description(self):
        """Test validation with missing description."""
        validator = ToolDescriptionValidator()
        
        desc = ToolDescription(
            name="bad_tool",
            description=""  # Empty description
        )
        
        validator.register_tool("bad_tool", desc)
        result = validator.validate_tool("bad_tool")
        
        assert result.success
        assert not result.value.is_valid
        assert len(result.value.issues) > 0
    
    def test_validate_missing_return_spec(self):
        """Test validation with missing return specification."""
        validator = ToolDescriptionValidator()
        
        desc = ToolDescription(
            name="no_return_tool",
            description="A tool without return specification"
        )
        
        validator.register_tool("no_return_tool", desc)
        result = validator.validate_tool("no_return_tool")
        
        assert result.success
        assert len(result.value.issues) > 0
    
    def test_validate_missing_error_handling(self):
        """Test validation with missing error handling documentation."""
        validator = ToolDescriptionValidator()
        
        desc = ToolDescription(
            name="no_error_tool",
            description="Tool without error handling docs",
            error_handling=[]
        )
        
        validator.register_tool("no_error_tool", desc)
        result = validator.validate_tool("no_error_tool")
        
        assert result.success
        # Should have warning about missing error handling
        assert any(i.issue_type == ValidationIssueType.MISSING_ERROR_HANDLING for i in result.value.issues)


class TestAccuracyLevelClassification:
    """Tests for accuracy level classification."""
    
    def test_perfect_accuracy(self):
        """Test perfect accuracy classification."""
        validator = ToolDescriptionValidator()
        level = validator._get_accuracy_level(99.5)
        assert level == AccuracyLevel.PERFECT
    
    def test_high_accuracy(self):
        """Test high accuracy classification."""
        validator = ToolDescriptionValidator()
        level = validator._get_accuracy_level(97)
        assert level == AccuracyLevel.HIGH
    
    def test_good_accuracy(self):
        """Test good accuracy classification."""
        validator = ToolDescriptionValidator()
        level = validator._get_accuracy_level(90)
        assert level == AccuracyLevel.GOOD
    
    def test_fair_accuracy(self):
        """Test fair accuracy classification."""
        validator = ToolDescriptionValidator()
        level = validator._get_accuracy_level(75)
        assert level == AccuracyLevel.FAIR
    
    def test_poor_accuracy(self):
        """Test poor accuracy classification."""
        validator = ToolDescriptionValidator()
        level = validator._get_accuracy_level(50)
        assert level == AccuracyLevel.POOR


class TestParameterValidation:
    """Tests for parameter validation."""
    
    def test_validate_parameters_all_documented(self):
        """Test validation of fully documented parameters."""
        validator = ToolDescriptionValidator()
        
        desc = ToolDescription(
            name="documented_tool",
            description="Tool with documented parameters",
            parameters=[
                ParameterSpec(
                    name="param1",
                    type_hint="str",
                    description="First parameter with full documentation"
                ),
                ParameterSpec(
                    name="param2",
                    type_hint="int",
                    description="Second parameter"
                )
            ]
        )
        
        validator.register_tool("documented_tool", desc)
        issues = validator._validate_parameters(desc)
        
        # Should have minimal issues
        assert len(issues) <= 2  # At most missing return spec and error handling
    
    def test_validate_parameters_missing_description(self):
        """Test validation with missing parameter description."""
        validator = ToolDescriptionValidator()
        
        desc = ToolDescription(
            name="undoc_tool",
            description="Tool with undocumented parameters",
            parameters=[
                ParameterSpec(
                    name="param1",
                    type_hint="str",
                    description=""  # Empty description
                )
            ]
        )
        
        validator.register_tool("undoc_tool", desc)
        issues = validator._validate_parameters(desc)
        
        # Should find description issue
        assert any(i.affected_element == "param1" for i in issues)
    
    def test_validate_parameters_missing_type(self):
        """Test validation with missing type hint."""
        validator = ToolDescriptionValidator()
        
        desc = ToolDescription(
            name="untyped_tool",
            description="Tool with untyped parameters",
            parameters=[
                ParameterSpec(
                    name="param1",
                    type_hint="",
                    description="Parameter without type"
                )
            ]
        )
        
        validator.register_tool("untyped_tool", desc)
        issues = validator._validate_parameters(desc)
        
        # Should find type issue
        assert any(i.issue_type == ValidationIssueType.INCORRECT_TYPE for i in issues)


class TestBatchValidation:
    """Tests for batch validation."""
    
    def test_batch_validate_all_tools(self):
        """Test batch validation of all registered tools."""
        validator = ToolDescriptionValidator()
        
        for i in range(3):
            desc = ToolDescription(
                name=f"tool_{i}",
                description=f"Tool {i} description"
            )
            validator.register_tool(f"tool_{i}", desc)
        
        result = validator.batch_validate()
        
        assert result.success
        assert len(result.value) == 3
    
    def test_batch_validate_specific_tools(self):
        """Test batch validation of specific tools."""
        validator = ToolDescriptionValidator()
        
        for i in range(3):
            desc = ToolDescription(
                name=f"tool_{i}",
                description=f"Tool {i} description"
            )
            validator.register_tool(f"tool_{i}", desc)
        
        result = validator.batch_validate(["tool_0", "tool_1"])
        
        assert result.success
        assert len(result.value) == 2


class TestValidationSummary:
    """Tests for validation summary."""
    
    def test_summary_empty_history(self):
        """Test summary with empty validation history."""
        validator = ToolDescriptionValidator()
        summary = validator.get_validation_summary()
        assert summary["total_validations"] == 0
    
    def test_summary_with_validations(self):
        """Test summary with validation history."""
        validator = ToolDescriptionValidator()
        
        desc1 = ToolDescription(
            name="tool1",
            description="Good tool description",
            return_spec=ReturnSpec("str", "Output"),
            error_handling=["ValueError"]
        )
        desc2 = ToolDescription(
            name="tool2",
            description="Tool"  # Short description
        )
        
        validator.register_tool("tool1", desc1)
        validator.register_tool("tool2", desc2)
        
        validator.validate_tool("tool1")
        validator.validate_tool("tool2")
        
        summary = validator.get_validation_summary()
        assert summary["total_validations"] == 2
        assert "average_accuracy" in summary


class TestIssueReport:
    """Tests for issue reporting."""
    
    def test_get_issue_report_valid_tool(self):
        """Test getting issue report for validated tool."""
        validator = ToolDescriptionValidator()
        
        desc = ToolDescription(
            name="test_tool",
            description="A test tool"
        )
        
        validator.register_tool("test_tool", desc)
        validator.validate_tool("test_tool")
        
        result = validator.get_issue_report("test_tool")
        
        assert result.success
        assert "tool_name" in result.value
        assert "issues_by_type" in result.value
    
    def test_get_issue_report_unvalidated_tool(self):
        """Test getting issue report for unvalidated tool."""
        validator = ToolDescriptionValidator()
        
        result = validator.get_issue_report("nonexistent")
        
        assert not result.success


class TestImprovementSuggestions:
    """Tests for improvement suggestions."""
    
    def test_suggest_improvements_for_poor_tool(self):
        """Test suggesting improvements for poorly documented tool."""
        validator = ToolDescriptionValidator()
        
        desc = ToolDescription(
            name="poor_tool",
            description="Bad"  # Very short
        )
        
        validator.register_tool("poor_tool", desc)
        validator.validate_tool("poor_tool")
        
        result = validator.suggest_improvements("poor_tool")
        
        assert result.success
        assert len(result.value) > 0
    
    def test_suggest_improvements_unvalidated_tool(self):
        """Test suggesting improvements for unvalidated tool."""
        validator = ToolDescriptionValidator()
        
        result = validator.suggest_improvements("nonexistent")
        
        assert not result.success


class TestCompleteWorkflow:
    """Integration tests for complete validation workflow."""
    
    def test_end_to_end_tool_validation(self):
        """Test complete tool validation workflow."""
        validator = ToolDescriptionValidator()
        
        # Register a tool
        desc = ToolDescription(
            name="search_tool",
            description="Searches for information in knowledge base",
            parameters=[
                ParameterSpec(
                    name="query",
                    type_hint="str",
                    description="Search query string"
                ),
                ParameterSpec(
                    name="max_results",
                    type_hint="int",
                    description="Maximum results to return",
                    required=False,
                    default_value=10
                )
            ],
            return_spec=ReturnSpec(
                type_hint="List[str]",
                description="List of search results"
            ),
            error_handling=["ValueError", "ConnectionError"]
        )
        
        validator.register_tool("search_tool", desc)
        
        # Validate the tool
        result = validator.validate_tool("search_tool")
        
        assert result.success
        assert result.value.is_valid or result.value.accuracy_percentage >= 70
        
        # Get summary
        summary = validator.get_validation_summary()
        assert summary["total_validations"] == 1


class TestMultipleTools:
    """Tests for managing multiple tools."""
    
    def test_validate_multiple_different_quality(self):
        """Test validating tools of different quality levels."""
        validator = ToolDescriptionValidator()
        
        # Good tool
        good_desc = ToolDescription(
            name="good_tool",
            description="Comprehensive description of what this tool does",
            parameters=[
                ParameterSpec("input", "str", "Input parameter")
            ],
            return_spec=ReturnSpec("str", "Output"),
            error_handling=["ValueError"]
        )
        
        # Poor tool
        poor_desc = ToolDescription(
            name="poor_tool",
            description="Bad"
        )
        
        validator.register_tool("good_tool", good_desc)
        validator.register_tool("poor_tool", poor_desc)
        
        validator.validate_tool("good_tool")
        validator.validate_tool("poor_tool")
        
        summary = validator.get_validation_summary()
        
        assert summary["total_validations"] == 2
        assert summary["valid_tools"] >= 1
