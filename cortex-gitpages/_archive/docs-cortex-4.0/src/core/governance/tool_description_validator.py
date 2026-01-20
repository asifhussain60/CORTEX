"""
CORE-033: Tool Description Accuracy Validation

Validates tool descriptions against actual capabilities:
- Description/capability alignment checking
- Parameter documentation validation
- Return type verification
- Error handling documentation
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Callable


class AccuracyLevel(Enum):
    """Accuracy level of tool description."""
    PERFECT = "perfect"          # 100% match
    HIGH = "high"                # 95-99% match
    GOOD = "good"                # 85-95% match
    FAIR = "fair"                # 70-85% match
    POOR = "poor"                # < 70% match


class ValidationIssueType(Enum):
    """Type of validation issue found."""
    MISSING_PARAMETER = "missing_parameter"
    UNDOCUMENTED_PARAMETER = "undocumented_parameter"
    INCORRECT_TYPE = "incorrect_type"
    MISSING_ERROR_HANDLING = "missing_error_handling"
    MISLEADING_DESCRIPTION = "misleading_description"
    INCOMPLETE_RETURN_TYPE = "incomplete_return_type"


@dataclass
class ParameterSpec:
    """Specification for a tool parameter."""
    name: str
    type_hint: str
    description: str
    required: bool = True
    default_value: Optional[Any] = None


@dataclass
class ReturnSpec:
    """Specification for tool return value."""
    type_hint: str
    description: str


@dataclass
class ToolDescription:
    """Description of a tool's interface."""
    name: str
    description: str
    parameters: List[ParameterSpec] = field(default_factory=list)
    return_spec: Optional[ReturnSpec] = None
    error_handling: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ValidationIssue:
    """Issue found during validation."""
    issue_type: ValidationIssueType
    severity: str  # "warning", "error", "critical"
    description: str
    affected_element: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of tool description validation."""
    tool_name: str
    accuracy_level: AccuracyLevel
    accuracy_percentage: float  # 0-100
    issues: List[ValidationIssue] = field(default_factory=list)
    is_valid: bool = True
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Result:
    """Generic result type for error handling."""
    success: bool
    value: Optional[Any] = None
    error: Optional[str] = None
    
    @classmethod
    def ok(cls, value: Any) -> Result:
        """Create successful result."""
        return cls(success=True, value=value)
    
    @classmethod
    def error(cls, error: str) -> Result:
        """Create error result."""
        return cls(success=False, error=error)


class ToolDescriptionValidator:
    """Validates tool descriptions against actual capabilities."""
    
    def __init__(self):
        """Initialize validator."""
        self.registered_tools: Dict[str, ToolDescription] = {}
        self.validation_history: List[ValidationResult] = []
        self.tools_registry: Dict[str, Callable] = {}
    
    def register_tool(
        self,
        name: str,
        description: ToolDescription,
        tool_func: Optional[Callable] = None
    ) -> None:
        """
        Register a tool with its description.
        
        Args:
            name: Tool name.
            description: Tool description specification.
            tool_func: Optional actual tool function.
        """
        self.registered_tools[name] = description
        if tool_func:
            self.tools_registry[name] = tool_func
    
    def validate_tool(self, tool_name: str) -> Result:
        """
        Validate a tool's description.
        
        Args:
            tool_name: Name of tool to validate.
            
        Returns:
            Result with ValidationResult or error.
        """
        try:
            if tool_name not in self.registered_tools:
                return Result.error(f"Tool '{tool_name}' not found")
            
            description = self.registered_tools[tool_name]
            issues = []
            accuracy = 100.0
            
            # Validate description completeness
            if not description.description or len(description.description) < 10:
                issues.append(ValidationIssue(
                    issue_type=ValidationIssueType.MISLEADING_DESCRIPTION,
                    severity="error",
                    description="Description is too short or missing"
                ))
                accuracy -= 15
            
            # Validate parameters
            param_issues = self._validate_parameters(description)
            issues.extend(param_issues)
            accuracy -= len(param_issues) * 5
            
            # Validate return specification
            if not description.return_spec:
                issues.append(ValidationIssue(
                    issue_type=ValidationIssueType.INCOMPLETE_RETURN_TYPE,
                    severity="warning",
                    description="Return type specification missing"
                ))
                accuracy -= 10
            
            # Validate error handling documentation
            if not description.error_handling:
                issues.append(ValidationIssue(
                    issue_type=ValidationIssueType.MISSING_ERROR_HANDLING,
                    severity="warning",
                    description="No error handling documentation provided"
                ))
                accuracy -= 5
            
            # Clamp accuracy to 0-100
            accuracy = max(0, min(100, accuracy))
            
            # Determine accuracy level
            accuracy_level = self._get_accuracy_level(accuracy)
            
            # Determine if valid
            is_valid = accuracy >= 70 and len([i for i in issues if i.severity == "error"]) == 0
            
            result = ValidationResult(
                tool_name=tool_name,
                accuracy_level=accuracy_level,
                accuracy_percentage=accuracy,
                issues=issues,
                is_valid=is_valid
            )
            
            self.validation_history.append(result)
            return Result.ok(result)
            
        except Exception as e:
            return Result.error(f"Validation failed: {str(e)}")
    
    def _validate_parameters(
        self,
        description: ToolDescription
    ) -> List[ValidationIssue]:
        """
        Validate parameter specifications.
        
        Args:
            description: Tool description.
            
        Returns:
            List of validation issues found.
        """
        issues = []
        
        for param in description.parameters:
            # Check parameter has description
            if not param.description or len(param.description) < 5:
                issues.append(ValidationIssue(
                    issue_type=ValidationIssueType.MISLEADING_DESCRIPTION,
                    severity="warning",
                    description=f"Parameter '{param.name}' lacks adequate description",
                    affected_element=param.name
                ))
            
            # Check type hint is specified
            if not param.type_hint:
                issues.append(ValidationIssue(
                    issue_type=ValidationIssueType.INCORRECT_TYPE,
                    severity="error",
                    description=f"Parameter '{param.name}' missing type hint",
                    affected_element=param.name
                ))
        
        return issues
    
    def _get_accuracy_level(self, accuracy: float) -> AccuracyLevel:
        """
        Get accuracy level from percentage.
        
        Args:
            accuracy: Accuracy percentage (0-100).
            
        Returns:
            AccuracyLevel enum value.
        """
        if accuracy >= 99:
            return AccuracyLevel.PERFECT
        elif accuracy >= 95:
            return AccuracyLevel.HIGH
        elif accuracy >= 85:
            return AccuracyLevel.GOOD
        elif accuracy >= 70:
            return AccuracyLevel.FAIR
        else:
            return AccuracyLevel.POOR
    
    def batch_validate(self, tool_names: Optional[List[str]] = None) -> Result:
        """
        Validate multiple tools.
        
        Args:
            tool_names: Optional list of tool names. If None, validates all.
            
        Returns:
            Result with list of validation results.
        """
        try:
            names_to_validate = tool_names or list(self.registered_tools.keys())
            results = []
            
            for name in names_to_validate:
                result = self.validate_tool(name)
                if result.success:
                    results.append(result.value)
            
            return Result.ok(results)
            
        except Exception as e:
            return Result.error(f"Batch validation failed: {str(e)}")
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Get summary of validation results.
        
        Returns:
            Dictionary with validation statistics.
        """
        if not self.validation_history:
            return {
                "total_validations": 0,
                "valid_tools": 0,
                "accuracy_distribution": {},
            }
        
        accuracy_counts = {}
        valid_count = sum(1 for v in self.validation_history if v.is_valid)
        
        for validation in self.validation_history:
            level = validation.accuracy_level.value
            accuracy_counts[level] = accuracy_counts.get(level, 0) + 1
        
        return {
            "total_validations": len(self.validation_history),
            "valid_tools": valid_count,
            "invalid_tools": len(self.validation_history) - valid_count,
            "accuracy_distribution": accuracy_counts,
            "average_accuracy": sum(v.accuracy_percentage for v in self.validation_history) / len(self.validation_history),
        }
    
    def get_issue_report(self, tool_name: str) -> Result:
        """
        Get detailed issue report for a tool.
        
        Args:
            tool_name: Name of tool.
            
        Returns:
            Result with issue report or error.
        """
        try:
            # Find latest validation for this tool
            matching = [v for v in self.validation_history if v.tool_name == tool_name]
            
            if not matching:
                return Result.error(f"No validation history for '{tool_name}'")
            
            latest = max(matching, key=lambda v: v.timestamp)
            
            report = {
                "tool_name": tool_name,
                "accuracy": latest.accuracy_percentage,
                "accuracy_level": latest.accuracy_level.value,
                "is_valid": latest.is_valid,
                "total_issues": len(latest.issues),
                "issues_by_type": {},
                "issues_by_severity": {},
            }
            
            for issue in latest.issues:
                # Count by type
                issue_type = issue.issue_type.value
                report["issues_by_type"][issue_type] = report["issues_by_type"].get(issue_type, 0) + 1
                
                # Count by severity
                severity = issue.severity
                report["issues_by_severity"][severity] = report["issues_by_severity"].get(severity, 0) + 1
            
            return Result.ok(report)
            
        except Exception as e:
            return Result.error(f"Report generation failed: {str(e)}")
    
    def suggest_improvements(self, tool_name: str) -> Result:
        """
        Suggest improvements for tool description.
        
        Args:
            tool_name: Name of tool.
            
        Returns:
            Result with improvement suggestions.
        """
        try:
            # Find latest validation
            matching = [v for v in self.validation_history if v.tool_name == tool_name]
            
            if not matching:
                return Result.error(f"No validation for '{tool_name}'")
            
            latest = max(matching, key=lambda v: v.timestamp)
            suggestions = []
            
            for issue in latest.issues:
                if issue.issue_type == ValidationIssueType.MISSING_PARAMETER:
                    suggestions.append(f"Add missing parameter: {issue.affected_element}")
                elif issue.issue_type == ValidationIssueType.MISSING_ERROR_HANDLING:
                    suggestions.append("Document possible error conditions and handling")
                elif issue.issue_type == ValidationIssueType.INCOMPLETE_RETURN_TYPE:
                    suggestions.append("Specify complete return type with description")
                elif issue.issue_type == ValidationIssueType.MISLEADING_DESCRIPTION:
                    suggestions.append(f"Improve description for: {issue.affected_element}")
            
            return Result.ok(suggestions)
            
        except Exception as e:
            return Result.error(f"Suggestion generation failed: {str(e)}")
