"""Tier2 Governance: Tool Description Validator

Implements CORE-033: Tool Description Accuracy Validation.
Validates tool descriptions match actual capabilities and parameters.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class AccuracyLevel(Enum):
    """Validation accuracy levels."""
    PERFECT = "perfect"  # 99%+
    HIGH = "high"  # 95-98%
    GOOD = "good"  # 85-94%
    FAIR = "fair"  # 70-84%
    POOR = "poor"  # <70%


class ValidationIssueType(Enum):
    """Validation issue types."""
    MISSING_DESCRIPTION = "missing_description"
    SHORT_DESCRIPTION = "short_description"
    MISSING_RETURN_SPEC = "missing_return_spec"
    MISSING_ERROR_HANDLING = "missing_error_handling"
    MISSING_PARAM_DESCRIPTION = "missing_param_description"
    INCORRECT_TYPE = "incorrect_type"


@dataclass
class ParameterSpec:
    """Parameter specification."""
    name: str
    type_hint: str
    description: str
    required: bool = True
    default_value: Any = None


@dataclass
class ReturnSpec:
    """Return value specification."""
    type_hint: str
    description: str


@dataclass
class ValidationIssue:
    """Validation issue."""
    issue_type: ValidationIssueType
    severity: str
    message: str
    affected_element: str = ""


@dataclass
class ValidationResult:
    """Validation result."""
    is_valid: bool
    accuracy_percentage: float
    accuracy_level: AccuracyLevel
    issues: List[ValidationIssue] = field(default_factory=list)


@dataclass
class ToolDescription:
    """Tool description."""
    name: str
    description: str
    parameters: List[ParameterSpec] = field(default_factory=list)
    return_spec: Optional[ReturnSpec] = None
    error_handling: List[str] = field(default_factory=list)


@dataclass
class Result:
    """Generic result wrapper."""
    success: bool
    value: Any = None
    error: Optional[str] = None


class ToolDescriptionValidator:
    """Validate tool descriptions.
    
    Ensures tool descriptions accurately reflect:
    - Tool capabilities and purpose
    - Parameter specifications and types
    - Return value specifications
    - Error handling documentation
    """
    
    def __init__(self):
        """Initialize the validator."""
        self.registered_tools: Dict[str, ToolDescription] = {}
        self.validation_history: Dict[str, ValidationResult] = {}
    
    def register_tool(self, tool_name: str, description: ToolDescription) -> None:
        """Register a tool for validation.
        
        Args:
            tool_name: Name of the tool
            description: Tool description object
        """
        self.registered_tools[tool_name] = description
    
    def validate_tool(self, tool_name: str) -> Result:
        """Validate a tool's description.
        
        Args:
            tool_name: Name of tool to validate
            
        Returns:
            Result with ValidationResult
        """
        if tool_name not in self.registered_tools:
            return Result(success=False, error=f"Tool '{tool_name}' not found")
        
        desc = self.registered_tools[tool_name]
        issues = []
        
        # Validate description
        if not desc.description:
            issues.append(ValidationIssue(
                issue_type=ValidationIssueType.MISSING_DESCRIPTION,
                severity="critical",
                message="Tool description is missing",
                affected_element="description"
            ))
        elif len(desc.description) < 10:
            issues.append(ValidationIssue(
                issue_type=ValidationIssueType.SHORT_DESCRIPTION,
                severity="high",
                message="Tool description is too short",
                affected_element="description"
            ))
        
        # Validate parameters
        issues.extend(self._validate_parameters(desc))
        
        # Validate return specification
        if desc.return_spec is None:
            issues.append(ValidationIssue(
                issue_type=ValidationIssueType.MISSING_RETURN_SPEC,
                severity="medium",
                message="Return specification is missing",
                affected_element="return_spec"
            ))
        
        # Validate error handling documentation
        if not desc.error_handling:
            issues.append(ValidationIssue(
                issue_type=ValidationIssueType.MISSING_ERROR_HANDLING,
                severity="low",
                message="Error handling documentation is missing",
                affected_element="error_handling"
            ))
        
        # Calculate accuracy
        accuracy = self._calculate_accuracy(desc, issues)
        level = self._get_accuracy_level(accuracy)
        is_valid = accuracy >= 70.0
        
        result = ValidationResult(
            is_valid=is_valid,
            accuracy_percentage=accuracy,
            accuracy_level=level,
            issues=issues
        )
        
        # Store in history
        self.validation_history[tool_name] = result
        
        return Result(success=True, value=result)
    
    def _validate_parameters(self, desc: ToolDescription) -> List[ValidationIssue]:
        """Validate parameter specifications.
        
        Args:
            desc: Tool description
            
        Returns:
            List of validation issues
        """
        issues = []
        
        for param in desc.parameters:
            # Check description
            if not param.description or len(param.description) < 5:
                issues.append(ValidationIssue(
                    issue_type=ValidationIssueType.MISSING_PARAM_DESCRIPTION,
                    severity="medium",
                    message=f"Parameter '{param.name}' lacks proper description",
                    affected_element=param.name
                ))
            
            # Check type hint
            if not param.type_hint:
                issues.append(ValidationIssue(
                    issue_type=ValidationIssueType.INCORRECT_TYPE,
                    severity="high",
                    message=f"Parameter '{param.name}' lacks type hint",
                    affected_element=param.name
                ))
        
        return issues
    
    def _calculate_accuracy(self, desc: ToolDescription, issues: List[ValidationIssue]) -> float:
        """Calculate accuracy percentage.
        
        Args:
            desc: Tool description
            issues: List of issues found
            
        Returns:
            Accuracy percentage (0-100)
        """
        # Start with perfect score
        score = 100.0
        
        # Deduct points for issues
        for issue in issues:
            if issue.severity == "critical":
                score -= 25
            elif issue.severity == "high":
                score -= 15
            elif issue.severity == "medium":
                score -= 10
            elif issue.severity == "low":
                score -= 5
        
        # Ensure score doesn't go below 0
        return max(0.0, score)
    
    def _get_accuracy_level(self, percentage: float) -> AccuracyLevel:
        """Get accuracy level from percentage.
        
        Args:
            percentage: Accuracy percentage
            
        Returns:
            AccuracyLevel enum
        """
        if percentage >= 99:
            return AccuracyLevel.PERFECT
        elif percentage >= 95:
            return AccuracyLevel.HIGH
        elif percentage >= 85:
            return AccuracyLevel.GOOD
        elif percentage >= 70:
            return AccuracyLevel.FAIR
        else:
            return AccuracyLevel.POOR
    
    def batch_validate(self, tool_names: Optional[List[str]] = None) -> Result:
        """Validate multiple tools.
        
        Args:
            tool_names: Optional list of tool names (validates all if None)
            
        Returns:
            Result with list of ValidationResults
        """
        if tool_names is None:
            tool_names = list(self.registered_tools.keys())
        
        results = []
        for tool_name in tool_names:
            result = self.validate_tool(tool_name)
            if result.success:
                results.append(result.value)
        
        return Result(success=True, value=results)
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get validation summary statistics.
        
        Returns:
            Summary dictionary
        """
        if not self.validation_history:
            return {
                "total_validations": 0,
                "valid_tools": 0,
                "average_accuracy": 0.0
            }
        
        valid_count = sum(1 for r in self.validation_history.values() if r.is_valid)
        avg_accuracy = sum(r.accuracy_percentage for r in self.validation_history.values()) / len(self.validation_history)
        
        return {
            "total_validations": len(self.validation_history),
            "valid_tools": valid_count,
            "invalid_tools": len(self.validation_history) - valid_count,
            "average_accuracy": avg_accuracy
        }
    
    def get_issue_report(self, tool_name: str) -> Result:
        """Get issue report for a tool.
        
        Args:
            tool_name: Name of tool
            
        Returns:
            Result with issue report dictionary
        """
        if tool_name not in self.validation_history:
            return Result(success=False, error=f"Tool '{tool_name}' has not been validated")
        
        result = self.validation_history[tool_name]
        
        # Group issues by type
        issues_by_type: Dict[str, List[ValidationIssue]] = {}
        for issue in result.issues:
            issue_type = issue.issue_type.value
            if issue_type not in issues_by_type:
                issues_by_type[issue_type] = []
            issues_by_type[issue_type].append(issue)
        
        report = {
            "tool_name": tool_name,
            "is_valid": result.is_valid,
            "accuracy": result.accuracy_percentage,
            "total_issues": len(result.issues),
            "issues_by_type": issues_by_type
        }
        
        return Result(success=True, value=report)
    
    def suggest_improvements(self, tool_name: str) -> Result:
        """Suggest improvements for a tool.
        
        Args:
            tool_name: Name of tool
            
        Returns:
            Result with list of improvement suggestions
        """
        if tool_name not in self.validation_history:
            return Result(success=False, error=f"Tool '{tool_name}' has not been validated")
        
        result = self.validation_history[tool_name]
        suggestions = []
        
        for issue in result.issues:
            if issue.issue_type == ValidationIssueType.SHORT_DESCRIPTION:
                suggestions.append("Expand tool description to at least 20 characters with clear purpose")
            elif issue.issue_type == ValidationIssueType.MISSING_RETURN_SPEC:
                suggestions.append("Add return specification with type hint and description")
            elif issue.issue_type == ValidationIssueType.MISSING_ERROR_HANDLING:
                suggestions.append("Document possible exceptions and error conditions")
            elif issue.issue_type == ValidationIssueType.MISSING_PARAM_DESCRIPTION:
                suggestions.append(f"Add description for parameter: {issue.affected_element}")
            elif issue.issue_type == ValidationIssueType.INCORRECT_TYPE:
                suggestions.append(f"Add type hint for parameter: {issue.affected_element}")
        
        return Result(success=True, value=suggestions)


__all__ = [
    "ParameterSpec",
    "ToolDescription",
    "ToolDescriptionValidator",
    "ReturnSpec",
    "AccuracyLevel",
    "ValidationIssueType",
    "ValidationIssue",
    "ValidationResult",
    "Result"
]
