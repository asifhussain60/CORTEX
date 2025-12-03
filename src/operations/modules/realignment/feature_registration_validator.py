"""
Feature Registration Validator for CORTEX Align Orchestrator v2.0

This module validates that all operations and modules are properly registered
in cortex-operations.yaml. Part of the Intelligent Maintenance System.

Author: Asif Hussain
Date: December 3, 2025
Version: 1.0.0
"""

import yaml
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Results from feature registration validation."""
    passed: bool
    unregistered_operations: List[str] = field(default_factory=list)
    unregistered_modules: List[Dict[str, str]] = field(default_factory=list)
    registered_operations: List[str] = field(default_factory=list)
    registered_modules: List[str] = field(default_factory=list)
    total_operations_found: int = 0
    total_modules_found: int = 0
    total_registered_operations: int = 0
    total_registered_modules: int = 0
    severity: str = "PASS"
    message: str = ""
    
    @property
    def unregistered_count(self) -> int:
        """Total count of unregistered items."""
        return len(self.unregistered_operations) + len(self.unregistered_modules)
    
    @property
    def registration_percentage(self) -> float:
        """Percentage of items properly registered."""
        total = self.total_operations_found + self.total_modules_found
        if total == 0:
            return 100.0
        registered = len(self.registered_operations) + len(self.registered_modules)
        return (registered / total) * 100.0


class FeatureRegistrationValidator:
    """Validates feature registration integrity across CORTEX."""
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize the validator.
        
        Args:
            project_root: Path to CORTEX project root. If None, auto-detects.
        """
        self.project_root = project_root or self._detect_project_root()
        self.operations_dir = self.project_root / "src" / "operations"
        self.modules_dir = self.operations_dir / "modules"
        self.operations_yaml = self.project_root / "cortex-operations.yaml"
        
        # Excluded files that shouldn't be registered
        self.excluded_files = {
            "__init__.py",
            "base_operation_module.py",
            "base_operation.py",
            "operation_base.py"
        }
        
        # Excluded module patterns
        self.excluded_module_patterns = {
            "__pycache__",
            "test_",
            ".pyc",
            "__init__"
        }
    
    def _detect_project_root(self) -> Path:
        """Auto-detect CORTEX project root."""
        current = Path.cwd()
        
        # Check if we're in CORTEX directory
        if (current / "cortex-operations.yaml").exists():
            return current
        
        # Check parent directories
        for parent in current.parents:
            if (parent / "cortex-operations.yaml").exists():
                return parent
        
        raise FileNotFoundError(
            "Cannot detect CORTEX project root. "
            "Ensure cortex-operations.yaml exists."
        )
    
    def scan_operations_directory(self) -> List[str]:
        """
        Scan src/operations/ for entry point files.
        
        Returns:
            List of operation names (file stems without .py extension)
        """
        operations = []
        
        if not self.operations_dir.exists():
            logger.warning(f"Operations directory not found: {self.operations_dir}")
            return operations
        
        for file in self.operations_dir.glob("*.py"):
            if file.name not in self.excluded_files:
                operations.append(file.stem)
        
        logger.info(f"Found {len(operations)} operation files in {self.operations_dir}")
        return sorted(operations)
    
    def scan_operation_modules(self) -> List[Dict[str, str]]:
        """
        Scan src/operations/modules/*/ for utility modules.
        
        Returns:
            List of dicts with 'category', 'module', and 'path' keys
        """
        modules = []
        
        if not self.modules_dir.exists():
            logger.warning(f"Modules directory not found: {self.modules_dir}")
            return modules
        
        for category_dir in self.modules_dir.iterdir():
            if not category_dir.is_dir():
                continue
            
            if any(pattern in category_dir.name for pattern in self.excluded_module_patterns):
                continue
            
            for file in category_dir.glob("*_utility.py"):
                if any(pattern in file.name for pattern in self.excluded_module_patterns):
                    continue
                
                modules.append({
                    "category": category_dir.name,
                    "module": file.stem,
                    "path": f"{category_dir.name}/{file.stem}"
                })
        
        logger.info(f"Found {len(modules)} utility modules in {self.modules_dir}")
        return sorted(modules, key=lambda x: x["path"])
    
    def load_registered_operations(self) -> Dict[str, Any]:
        """
        Load registered operations from cortex-operations.yaml.
        
        Returns:
            Dictionary of operations from YAML
        """
        if not self.operations_yaml.exists():
            raise FileNotFoundError(
                f"cortex-operations.yaml not found at {self.operations_yaml}"
            )
        
        with open(self.operations_yaml, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data or 'operations' not in data:
            raise ValueError("Invalid cortex-operations.yaml: missing 'operations' key")
        
        return data['operations']
    
    def is_module_registered(self, module_info: Dict[str, str], 
                           registered_ops: Dict[str, Any]) -> bool:
        """
        Check if a module is registered under any operation.
        
        Args:
            module_info: Dict with 'category', 'module', 'path'
            registered_ops: Registered operations from YAML
        
        Returns:
            True if module is registered, False otherwise
        """
        module_name = module_info["module"]
        module_path = module_info["path"]
        
        for op_data in registered_ops.values():
            if 'modules' not in op_data:
                continue
            
            modules = op_data['modules']
            if not isinstance(modules, list):
                continue
            
            # Check if module name or path is in the modules list
            if module_name in modules or module_path in modules:
                return True
            
            # Check if module name appears in any module path
            for registered_module in modules:
                if module_name in str(registered_module):
                    return True
        
        return False
    
    def identify_unregistered(self) -> Dict[str, Any]:
        """
        Find operations and modules that exist but aren't registered.
        
        Returns:
            Dict with 'operations' and 'modules' lists of unregistered items
        """
        # Scan filesystem
        actual_ops = self.scan_operations_directory()
        actual_modules = self.scan_operation_modules()
        
        # Load registered items
        registered = self.load_registered_operations()
        registered_names = set(registered.keys())
        
        # Find unregistered operations
        unregistered_ops = [
            op for op in actual_ops 
            if op not in registered_names
        ]
        
        # Find unregistered modules
        unregistered_modules = [
            mod for mod in actual_modules
            if not self.is_module_registered(mod, registered)
        ]
        
        # Find registered items for statistics
        registered_ops = [op for op in actual_ops if op in registered_names]
        registered_module_count = len(actual_modules) - len(unregistered_modules)
        
        return {
            'operations': unregistered_ops,
            'modules': unregistered_modules,
            'registered_operations': registered_ops,
            'registered_module_count': registered_module_count,
            'total_operations': len(actual_ops),
            'total_modules': len(actual_modules)
        }
    
    def validate(self) -> ValidationResult:
        """
        Execute validation and return comprehensive results.
        
        Returns:
            ValidationResult with all validation data
        """
        try:
            unregistered = self.identify_unregistered()
            
            # Determine if validation passed
            passed = (
                len(unregistered['operations']) == 0 and 
                len(unregistered['modules']) == 0
            )
            
            # Determine severity
            if len(unregistered['operations']) > 0:
                severity = 'ERROR'
                message = f"{len(unregistered['operations'])} unregistered operations found"
            elif len(unregistered['modules']) > 0:
                severity = 'WARNING'
                message = f"{len(unregistered['modules'])} unregistered modules found"
            else:
                severity = 'PASS'
                message = "All features properly registered"
            
            return ValidationResult(
                passed=passed,
                unregistered_operations=unregistered['operations'],
                unregistered_modules=unregistered['modules'],
                registered_operations=unregistered['registered_operations'],
                registered_modules=[],  # Populated in detail reports
                total_operations_found=unregistered['total_operations'],
                total_modules_found=unregistered['total_modules'],
                total_registered_operations=len(unregistered['registered_operations']),
                total_registered_modules=unregistered['registered_module_count'],
                severity=severity,
                message=message
            )
        
        except Exception as e:
            logger.error(f"Validation failed: {e}", exc_info=True)
            return ValidationResult(
                passed=False,
                severity='ERROR',
                message=f"Validation error: {str(e)}"
            )
    
    def generate_report(self, result: ValidationResult) -> str:
        """
        Generate a formatted report from validation results.
        
        Args:
            result: ValidationResult to format
        
        Returns:
            Formatted markdown report
        """
        report_lines = [
            "# Feature Registration Validation Report",
            "",
            f"**Status:** {'✅ PASS' if result.passed else '❌ FAIL'}",
            f"**Severity:** {result.severity}",
            f"**Registration Rate:** {result.registration_percentage:.1f}%",
            "",
            "## Summary",
            "",
            f"- **Operations Found:** {result.total_operations_found}",
            f"- **Operations Registered:** {result.total_registered_operations}",
            f"- **Operations Unregistered:** {len(result.unregistered_operations)}",
            "",
            f"- **Modules Found:** {result.total_modules_found}",
            f"- **Modules Registered:** {result.total_registered_modules}",
            f"- **Modules Unregistered:** {len(result.unregistered_modules)}",
            "",
        ]
        
        if result.unregistered_operations:
            report_lines.extend([
                "## ⚠️ Unregistered Operations",
                "",
                "The following operations exist but are not registered in cortex-operations.yaml:",
                ""
            ])
            for op in result.unregistered_operations:
                report_lines.append(f"- `{op}` (src/operations/{op}.py)")
            report_lines.append("")
        
        if result.unregistered_modules:
            report_lines.extend([
                "## ⚠️ Unregistered Modules",
                "",
                "The following modules exist but are not registered under any operation:",
                ""
            ])
            for mod in result.unregistered_modules:
                report_lines.append(
                    f"- `{mod['module']}` (src/operations/modules/{mod['path']}.py)"
                )
            report_lines.append("")
        
        if result.passed:
            report_lines.extend([
                "## ✅ All Clear",
                "",
                "All operations and modules are properly registered in cortex-operations.yaml.",
                ""
            ])
        else:
            report_lines.extend([
                "## 🔧 Recommended Actions",
                "",
                "1. Run `align discover-features` to see detailed feature information",
                "2. Run `align register-features` for interactive registration",
                "3. Or run `align register-features --auto` to auto-register all",
                ""
            ])
        
        return "\n".join(report_lines)


def main():
    """CLI entry point for standalone validation."""
    import sys
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        validator = FeatureRegistrationValidator()
        result = validator.validate()
        
        print(validator.generate_report(result))
        
        # Exit with appropriate code
        sys.exit(0 if result.passed else 1)
    
    except Exception as e:
        logger.error(f"Validation failed: {e}", exc_info=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
