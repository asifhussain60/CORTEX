"""
Naming Conventions Module - CR-001-01

Defines orchestrator naming conventions and provides linting functionality.

Author: Asif Hussain
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Any, Dict, List, Optional


class NamingConvention(Enum):
    """Naming convention enumeration"""
    
    KEBAB_CASE = "kebab_case"
    SNAKE_CASE = "snake_case"
    PASCAL_CASE = "pascal_case"
    
    @property
    def description(self) -> str:
        """Get convention description"""
        descriptions = {
            NamingConvention.KEBAB_CASE: (
                "Words separated by hyphens, all lowercase (e.g., my-orchestrator)"
            ),
            NamingConvention.SNAKE_CASE: (
                "Words separated by underscores, all lowercase (e.g., my_orchestrator)"
            ),
            NamingConvention.PASCAL_CASE: (
                "Words concatenated with first letter capitalized (e.g., MyOrchestrator)"
            ),
        }
        return descriptions.get(self, "Unknown convention")
    
    @property
    def pattern(self) -> str:
        """Get regex pattern for convention"""
        patterns = {
            NamingConvention.KEBAB_CASE: r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$",
            NamingConvention.SNAKE_CASE: r"^[a-z0-9]([a-z0-9_]*[a-z0-9])?$",
            NamingConvention.PASCAL_CASE: r"^[A-Z][a-zA-Z0-9]*$",
        }
        return patterns.get(self, "")
    
    @property
    def examples(self) -> List[str]:
        """Get convention examples"""
        examples = {
            NamingConvention.KEBAB_CASE: [
                "planning-orchestrator",
                "analysis-engine",
                "validation-processor",
            ],
            NamingConvention.SNAKE_CASE: [
                "planning_orchestrator",
                "analysis_engine",
                "validation_processor",
            ],
            NamingConvention.PASCAL_CASE: [
                "PlanningOrchestrator",
                "AnalysisEngine",
                "ValidationProcessor",
            ],
        }
        return examples.get(self, [])
    
    @property
    def use_cases(self) -> List[str]:
        """Get convention use cases"""
        use_cases = {
            NamingConvention.KEBAB_CASE: [
                "URL paths and identifiers",
                "System object names",
                "CLI command names",
            ],
            NamingConvention.SNAKE_CASE: [
                "Python variable and function names",
                "Database column names",
                "Environment variables",
            ],
            NamingConvention.PASCAL_CASE: [
                "Python class names",
                "Type identifiers",
                "Component names",
            ],
        }
        return use_cases.get(self, [])
    
    @classmethod
    def get_all(cls) -> List["NamingConvention"]:
        """Get all naming conventions"""
        return list(cls)


@dataclass
class NamingViolation:
    """Naming convention violation"""
    
    code: str
    message: str
    severity: str = "ERROR"
    suggestion: Optional[str] = None
    position: Optional[int] = None


@dataclass
class LintResult:
    """Result of linting operation"""
    
    is_valid: bool
    violations: List[NamingViolation] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    name: str = ""
    convention: str = ""


@dataclass
class LintReport:
    """Report of batch linting operations"""
    
    total_names: int = 0
    valid_count: int = 0
    invalid_count: int = 0
    violations: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary
        
        Returns:
            Report as dictionary
        """
        return {
            "summary": {
                "total_names": self.total_names,
                "valid_count": self.valid_count,
                "invalid_count": self.invalid_count,
                "pass_rate": (
                    (self.valid_count / self.total_names * 100)
                    if self.total_names > 0 else 0
                ),
            },
            "violations": self.violations,
            "timestamp": self.timestamp.isoformat(),
        }


class NamingLinter:
    """Linter for orchestrator naming conventions"""
    
    MAX_NAME_LENGTH = 25
    MIN_NAME_LENGTH = 1
    
    def lint(
        self,
        name: str,
        convention: NamingConvention
    ) -> LintResult:
        """Lint a single name
        
        Args:
            name: Name to validate
            convention: Naming convention to check against
            
        Returns:
            Lint result with violations
        """
        violations: List[NamingViolation] = []
        
        # Check length
        if len(name) > self.MAX_NAME_LENGTH:
            violations.append(
                NamingViolation(
                    code="NAMING_LENGTH_EXCEEDS_MAX",
                    message=f"Name exceeds maximum length of {self.MAX_NAME_LENGTH}",
                    severity="ERROR",
                    suggestion=f"Shorten name to {self.MAX_NAME_LENGTH} characters or less",
                )
            )
        
        if len(name) < self.MIN_NAME_LENGTH:
            violations.append(
                NamingViolation(
                    code="NAMING_LENGTH_BELOW_MIN",
                    message="Name is empty",
                    severity="ERROR",
                    suggestion="Provide a non-empty name",
                )
            )
        
        # Check pattern
        pattern = convention.pattern
        if not re.match(pattern, name):
            violations.append(
                NamingViolation(
                    code="NAMING_CONVENTION_VIOLATION",
                    message=f"Name does not match {convention.name} pattern",
                    severity="ERROR",
                    suggestion=self._suggest_fix(name, convention),
                )
            )
        
        return LintResult(
            is_valid=len(violations) == 0,
            violations=violations,
            name=name,
            convention=convention.name,
        )
    
    def lint_batch(
        self,
        names: List[str],
        convention: NamingConvention
    ) -> List[LintResult]:
        """Lint multiple names
        
        Args:
            names: List of names to validate
            convention: Naming convention to check against
            
        Returns:
            List of lint results
        """
        return [self.lint(name, convention) for name in names]
    
    def generate_report(
        self,
        names: List[str],
        convention: NamingConvention
    ) -> LintReport:
        """Generate linting report
        
        Args:
            names: List of names to validate
            convention: Naming convention to check against
            
        Returns:
            Lint report
        """
        results = self.lint_batch(names, convention)
        
        violations_list = []
        for result in results:
            if not result.is_valid:
                for violation in result.violations:
                    violations_list.append({
                        "name": result.name,
                        "code": violation.code,
                        "message": violation.message,
                        "suggestion": violation.suggestion,
                        "severity": violation.severity,
                    })
        
        report = LintReport(
            total_names=len(names),
            valid_count=sum(1 for r in results if r.is_valid),
            invalid_count=sum(1 for r in results if not r.is_valid),
            violations=violations_list,
        )
        
        return report
    
    def get_best_practices(self) -> List[str]:
        """Get naming best practices
        
        Returns:
            List of best practices
        """
        practices = [
            "Use consistent naming convention across all orchestrators",
            "Keep names descriptive and concise (max 25 characters)",
            "Avoid generic names like 'processor', 'handler', 'service'",
            "Include domain or purpose in the name",
            "Use lowercase for system identifiers",
            "Avoid special characters except hyphens/underscores",
            "Make names pronounceable and memorable",
            "Document any custom naming conventions",
        ]
        return practices
    
    def _suggest_fix(
        self,
        name: str,
        convention: NamingConvention
    ) -> str:
        """Suggest fix for naming violation
        
        Args:
            name: Invalid name
            convention: Target convention
            
        Returns:
            Suggested corrected name
        """
        if convention == NamingConvention.KEBAB_CASE:
            # Convert to kebab case
            name = re.sub(r"[_\s]+", "-", name)  # Replace underscores/spaces
            name = re.sub(r"([a-z])([A-Z])", r"\1-\2", name)  # CamelCase
            name = name.lower()
            name = re.sub(r"[^a-z0-9-]", "", name)  # Remove invalid chars
            name = re.sub(r"-+", "-", name)  # Multiple hyphens to single
            name = name.strip("-")  # Remove leading/trailing hyphens
            return name
        
        elif convention == NamingConvention.SNAKE_CASE:
            # Convert to snake case
            name = re.sub(r"[-\s]+", "_", name)  # Replace hyphens/spaces
            name = re.sub(r"([a-z])([A-Z])", r"\1_\2", name)  # CamelCase
            name = name.lower()
            name = re.sub(r"[^a-z0-9_]", "", name)  # Remove invalid chars
            name = re.sub(r"_+", "_", name)  # Multiple underscores to single
            name = name.strip("_")  # Remove leading/trailing underscores
            return name
        
        elif convention == NamingConvention.PASCAL_CASE:
            # Convert to pascal case
            parts = re.split(r"[-_\s]+", name)
            return "".join(p.capitalize() for p in parts if p)
        
        return name
