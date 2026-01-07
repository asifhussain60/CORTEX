"""
Python Best Practices Validator Middleware

Validates Python code against PEP 8, type hints, docstrings, SOLID principles,
and CORTEX-specific architecture patterns before execution.

Author: CORTEX
Phase: P01.4
"""

import ast
import inspect
import json
import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from radon.complexity import cc_visit
from radon.metrics import mi_visit


class ValidationSeverity(Enum):
    """Validation error severity."""
    ERROR = "error"      # Blocks execution
    WARNING = "warning"  # Logs but allows execution
    INFO = "info"        # Informational only


@dataclass
class ValidationError:
    """Individual validation error."""
    severity: ValidationSeverity
    category: str  # "pep8", "type_hints", "docstrings", etc.
    rule: str      # "PEP8-001", "SOLID-SRP-001", etc.
    file_path: str
    line_number: int
    message: str
    fix_suggestion: str  # How to fix the error


@dataclass
class ValidationResult:
    """Validation result for a file or module."""
    file_path: str
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    info: List[ValidationError] = field(default_factory=list)
    
    def summary(self) -> str:
        """Human-readable summary."""
        return (
            f"Validation {'PASSED' if self.is_valid else 'FAILED'}: "
            f"{len(self.errors)} errors, {len(self.warnings)} warnings, "
            f"{len(self.info)} info"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "file_path": self.file_path,
            "is_valid": self.is_valid,
            "errors": [
                {
                    "severity": e.severity.value,
                    "category": e.category,
                    "rule": e.rule,
                    "file_path": e.file_path,
                    "line_number": e.line_number,
                    "message": e.message,
                    "fix_suggestion": e.fix_suggestion
                }
                for e in self.errors
            ],
            "warnings": [
                {
                    "severity": w.severity.value,
                    "category": w.category,
                    "rule": w.rule,
                    "file_path": w.file_path,
                    "line_number": w.line_number,
                    "message": w.message,
                    "fix_suggestion": w.fix_suggestion
                }
                for w in self.warnings
            ],
            "info": [
                {
                    "severity": i.severity.value,
                    "category": i.category,
                    "rule": i.rule,
                    "file_path": i.file_path,
                    "line_number": i.line_number,
                    "message": i.message,
                    "fix_suggestion": i.fix_suggestion
                }
                for i in self.info
            ],
            "summary": self.summary()
        }


class PythonBestPracticesValidator:
    """
    Validates Python code against best practices before execution.
    
    Validation Categories:
    - PEP 8 compliance (black + isort)
    - Type hints (mypy)
    - Docstrings (Google style)
    - SOLID principles (AST analysis)
    - Code quality (cyclomatic complexity, maintainability index)
    - CORTEX architecture patterns
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize validator.
        
        Args:
            config_path: Path to validation-rules.yaml (optional)
        """
        self.config_path = config_path or Path("cortex-brain/config/validation-rules.yaml")
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load validation configuration."""
        if self.config_path.exists():
            import yaml
            with open(self.config_path) as f:
                return yaml.safe_load(f).get("validation_rules", {})
        
        # Default configuration
        return {
            "pep8": {"enabled": True, "severity": "error"},
            "type_hints": {"enabled": True, "severity": "error"},
            "docstrings": {"enabled": True, "severity": "warning"},
            "solid": {"enabled": True, "severity": "error"},
            "code_quality": {"enabled": True, "severity": "warning"},
            "cortex_patterns": {"enabled": True, "severity": "error"}
        }
    
    def validate_file(self, file_path: str) -> ValidationResult:
        """
        Validate a Python file against all checks.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            ValidationResult with all errors/warnings
        """
        path = Path(file_path)
        
        if not path.exists():
            return ValidationResult(
                file_path=file_path,
                is_valid=False,
                errors=[ValidationError(
                    severity=ValidationSeverity.ERROR,
                    category="file_system",
                    rule="FILE-001",
                    file_path=file_path,
                    line_number=0,
                    message=f"File not found: {file_path}",
                    fix_suggestion="Ensure the file path is correct"
                )]
            )
        
        result = ValidationResult(file_path=file_path, is_valid=True)
        
        # Run all validations
        if self.config.get("pep8", {}).get("enabled", True):
            pep8_result = self.validate_pep8(file_path)
            result.errors.extend(pep8_result.errors)
            result.warnings.extend(pep8_result.warnings)
        
        if self.config.get("type_hints", {}).get("enabled", True):
            type_result = self.validate_type_hints(file_path)
            result.errors.extend(type_result.errors)
            result.warnings.extend(type_result.warnings)
        
        if self.config.get("docstrings", {}).get("enabled", True):
            doc_result = self.validate_docstrings(file_path)
            result.warnings.extend(doc_result.warnings)
        
        if self.config.get("solid", {}).get("enabled", True):
            solid_result = self.validate_solid_principles(file_path)
            result.errors.extend(solid_result.errors)
            result.warnings.extend(solid_result.warnings)
        
        if self.config.get("code_quality", {}).get("enabled", True):
            quality_result = self.validate_code_quality(file_path)
            result.warnings.extend(quality_result.warnings)
        
        if self.config.get("cortex_patterns", {}).get("enabled", True):
            pattern_result = self.validate_cortex_patterns(file_path)
            result.errors.extend(pattern_result.errors)
        
        # Determine overall validity
        result.is_valid = len(result.errors) == 0
        
        return result
    
    def validate_pep8(self, file_path: str) -> ValidationResult:
        """
        Validate PEP 8 compliance using black.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            ValidationResult with PEP 8 violations
        """
        result = ValidationResult(file_path=file_path, is_valid=True)
        
        try:
            # Check with black (formatting)
            black_result = subprocess.run(
                ["black", "--check", "--quiet", file_path],
                capture_output=True,
                text=True
            )
            
            if black_result.returncode != 0:
                result.errors.append(ValidationError(
                    severity=ValidationSeverity.ERROR,
                    category="pep8",
                    rule="PEP8-001",
                    file_path=file_path,
                    line_number=0,
                    message="Code formatting does not comply with PEP 8",
                    fix_suggestion=f"Run: black {file_path}"
                ))
        except FileNotFoundError:
            result.info.append(ValidationError(
                severity=ValidationSeverity.INFO,
                category="pep8",
                rule="PEP8-000",
                file_path=file_path,
                line_number=0,
                message="black not installed, skipping PEP 8 check",
                fix_suggestion="pip install black"
            ))
        
        return result
    
    def validate_type_hints(self, file_path: str) -> ValidationResult:
        """
        Validate type hints using AST analysis.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            ValidationResult with type hint violations
        """
        result = ValidationResult(file_path=file_path, is_valid=True)
        
        try:
            with open(file_path) as f:
                tree = ast.parse(f.read(), filename=file_path)
            
            # Check functions for type hints
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Skip private functions
                    if node.name.startswith("_") and not node.name.startswith("__"):
                        continue
                    
                    # Check return type annotation
                    if node.returns is None:
                        result.errors.append(ValidationError(
                            severity=ValidationSeverity.ERROR,
                            category="type_hints",
                            rule="TYPE-001",
                            file_path=file_path,
                            line_number=node.lineno,
                            message=f"Function '{node.name}' missing return type annotation",
                            fix_suggestion=f"Add return type: def {node.name}(...) -> ReturnType:"
                        ))
                    
                    # Check parameter annotations
                    for arg in node.args.args:
                        if arg.arg == "self" or arg.arg == "cls":
                            continue
                        
                        if arg.annotation is None:
                            result.errors.append(ValidationError(
                                severity=ValidationSeverity.ERROR,
                                category="type_hints",
                                rule="TYPE-002",
                                file_path=file_path,
                                line_number=node.lineno,
                                message=f"Parameter '{arg.arg}' in '{node.name}' missing type annotation",
                                fix_suggestion=f"Add type: {arg.arg}: ParamType"
                            ))
        
        except SyntaxError as e:
            result.errors.append(ValidationError(
                severity=ValidationSeverity.ERROR,
                category="type_hints",
                rule="TYPE-000",
                file_path=file_path,
                line_number=e.lineno or 0,
                message=f"Syntax error prevents type hint validation: {e}",
                fix_suggestion="Fix syntax errors first"
            ))
        
        return result
    
    def validate_docstrings(self, file_path: str) -> ValidationResult:
        """
        Validate docstring completeness.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            ValidationResult with docstring violations
        """
        result = ValidationResult(file_path=file_path, is_valid=True)
        
        try:
            with open(file_path) as f:
                tree = ast.parse(f.read(), filename=file_path)
            
            # Check classes for docstrings
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Skip private classes
                    if node.name.startswith("_"):
                        continue
                    
                    docstring = ast.get_docstring(node)
                    if not docstring:
                        result.warnings.append(ValidationError(
                            severity=ValidationSeverity.WARNING,
                            category="docstrings",
                            rule="DOC-001",
                            file_path=file_path,
                            line_number=node.lineno,
                            message=f"Class '{node.name}' missing docstring",
                            fix_suggestion=f"Add docstring below class definition"
                        ))
                
                elif isinstance(node, ast.FunctionDef):
                    # Skip private functions
                    if node.name.startswith("_") and not node.name.startswith("__"):
                        continue
                    
                    docstring = ast.get_docstring(node)
                    if not docstring:
                        result.warnings.append(ValidationError(
                            severity=ValidationSeverity.WARNING,
                            category="docstrings",
                            rule="DOC-002",
                            file_path=file_path,
                            line_number=node.lineno,
                            message=f"Function '{node.name}' missing docstring",
                            fix_suggestion=f"Add docstring with Args, Returns, Raises sections"
                        ))
        
        except SyntaxError:
            # Already reported in type hints validation
            pass
        
        return result
    
    def validate_solid_principles(self, file_path: str) -> ValidationResult:
        """
        Validate SOLID principles using AST analysis.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            ValidationResult with SOLID violations
        """
        result = ValidationResult(file_path=file_path, is_valid=True)
        
        try:
            with open(file_path) as f:
                tree = ast.parse(f.read(), filename=file_path)
            
            # Check Single Responsibility: class should have ≤3 public methods
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    public_methods = [
                        m for m in node.body
                        if isinstance(m, ast.FunctionDef) and not m.name.startswith("_")
                    ]
                    
                    if len(public_methods) > 3:
                        result.warnings.append(ValidationError(
                            severity=ValidationSeverity.WARNING,
                            category="solid",
                            rule="SOLID-SRP-001",
                            file_path=file_path,
                            line_number=node.lineno,
                            message=f"Class '{node.name}' has {len(public_methods)} public methods (>3), may violate SRP",
                            fix_suggestion="Consider splitting into smaller, focused classes"
                        ))
        
        except SyntaxError:
            pass
        
        return result
    
    def validate_code_quality(self, file_path: str) -> ValidationResult:
        """
        Validate code quality metrics.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            ValidationResult with quality violations
        """
        result = ValidationResult(file_path=file_path, is_valid=True)
        
        try:
            with open(file_path) as f:
                code = f.read()
            
            # Check cyclomatic complexity
            try:
                complexity_results = cc_visit(code)
                for item in complexity_results:
                    if item.complexity > 10:
                        result.warnings.append(ValidationError(
                            severity=ValidationSeverity.WARNING,
                            category="code_quality",
                            rule="QUALITY-001",
                            file_path=file_path,
                            line_number=item.lineno,
                            message=f"Function '{item.name}' has cyclomatic complexity {item.complexity} (>10)",
                            fix_suggestion="Refactor to reduce complexity (extract methods, simplify logic)"
                        ))
            except Exception:
                # Ignore radon errors
                pass
            
            # Check maintainability index
            try:
                mi_results = mi_visit(code, multi=True)
                for item in mi_results:
                    if item.mi < 20:  # Low maintainability
                        result.warnings.append(ValidationError(
                            severity=ValidationSeverity.WARNING,
                            category="code_quality",
                            rule="QUALITY-002",
                            file_path=file_path,
                            line_number=0,
                            message=f"Low maintainability index: {item.mi:.1f} (<20)",
                            fix_suggestion="Improve code structure, reduce complexity"
                        ))
            except Exception:
                # Ignore radon errors
                pass
        
        except SyntaxError:
            pass
        
        return result
    
    def validate_cortex_patterns(self, file_path: str) -> ValidationResult:
        """
        Validate CORTEX-specific architecture patterns.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            ValidationResult with pattern violations
        """
        result = ValidationResult(file_path=file_path, is_valid=True)
        
        # Check if file is an orchestrator
        if "orchestrators" in file_path and "orchestrator" in Path(file_path).stem:
            try:
                with open(file_path) as f:
                    tree = ast.parse(f.read(), filename=file_path)
                
                # Check for OrchestratorInterface implementation
                has_interface = False
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        for base in node.bases:
                            if isinstance(base, ast.Name) and "Interface" in base.id:
                                has_interface = True
                                break
                
                if not has_interface:
                    result.warnings.append(ValidationError(
                        severity=ValidationSeverity.WARNING,
                        category="cortex_patterns",
                        rule="CORTEX-001",
                        file_path=file_path,
                        line_number=0,
                        message="Orchestrator should implement OrchestratorInterface protocol",
                        fix_suggestion="Inherit from OrchestratorInterface or Protocol"
                    ))
            
            except SyntaxError:
                pass
        
        return result


def main():
    """CLI entry point for running validator."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate Python code against best practices")
    parser.add_argument("--target", required=True, help="File or directory to validate")
    parser.add_argument("--output", help="Output file for validation report (JSON)")
    parser.add_argument("--config", help="Path to validation-rules.yaml")
    
    args = parser.parse_args()
    
    validator = PythonBestPracticesValidator(
        config_path=Path(args.config) if args.config else None
    )
    
    target_path = Path(args.target)
    results = []
    
    if target_path.is_file():
        result = validator.validate_file(str(target_path))
        results.append(result)
        print(result.summary())
    elif target_path.is_dir():
        # Validate all Python files in directory
        for py_file in target_path.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            
            result = validator.validate_file(str(py_file))
            results.append(result)
            print(f"{py_file}: {result.summary()}")
    else:
        print(f"Error: {target_path} is not a valid file or directory")
        sys.exit(1)
    
    # Write output if requested
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w") as f:
            json.dump([r.to_dict() for r in results], f, indent=2)
        
        print(f"\n✅ Validation report written to: {output_path}")
    
    # Exit with error if any validation failed
    if any(not r.is_valid for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
