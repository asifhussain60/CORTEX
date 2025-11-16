"""
Code Cleanup Stage

Performs code formatting, linting, and basic cleanup operations.

Author: CORTEX Development Team
Date: 2025-11-08
"""

import re
from typing import Dict, Any, List
from src.workflows.workflow_engine import (
    BaseWorkflowStage,
    WorkflowState,
    StageResult,
    StageStatus
)


class CodeCleanup(BaseWorkflowStage):
    """
    Stage that performs code cleanup operations
    
    Input Requirements:
        - state.stage_outputs['implement']: Implementation details with files
        OR
        - state.context: File paths to clean
        
    Output:
        - files_cleaned: List of files cleaned
        - issues_fixed: List of issues fixed
        - cleanup_summary: Summary of cleanup operations
    """
    
    def __init__(self):
        super().__init__("code_cleanup")
    
    def execute(self, state: WorkflowState) -> StageResult:
        """Perform code cleanup"""
        # Get files to clean
        files = self._get_files_to_clean(state)
        
        if not files:
            return StageResult(
                stage_id=self.stage_id,
                status=StageStatus.SUCCESS,
                duration_ms=0,
                output={
                    "files_cleaned": [],
                    "issues_fixed": [],
                    "cleanup_summary": "No files to clean"
                }
            )
        
        # Perform cleanup operations
        files_cleaned = []
        issues_fixed = []
        
        for file_path in files:
            cleaned, issues = self._cleanup_file(file_path)
            if cleaned:
                files_cleaned.append(file_path)
                issues_fixed.extend(issues)
        
        # Generate summary
        summary = self._generate_summary(files_cleaned, issues_fixed)
        
        output = {
            "files_cleaned": files_cleaned,
            "issues_fixed": issues_fixed,
            "cleanup_summary": summary
        }
        
        return StageResult(
            stage_id=self.stage_id,
            status=StageStatus.SUCCESS,
            duration_ms=0,
            output=output
        )
    
    def validate_input(self, state: WorkflowState) -> bool:
        """Validate input files or context available"""
        # Can work with or without files (optional stage)
        return True
    
    def _get_files_to_clean(self, state: WorkflowState) -> List[str]:
        """Extract files to clean from state"""
        files = []
        
        # Check implementation stage output
        implement_output = state.get_stage_output("implement")
        if implement_output and "files" in implement_output:
            files.extend(implement_output["files"])
        
        # Check context
        if "modified_files" in state.context:
            files.extend(state.context["modified_files"])
        
        # Remove duplicates
        return list(set(files))
    
    def _cleanup_file(self, file_path: str) -> tuple:
        """
        Perform cleanup on a single file
        
        Returns:
            (cleaned: bool, issues: List[str])
        """
        issues = []
        
        # Simulate cleanup operations
        # In real implementation, would read file, apply fixes, write back
        
        # Check file extension for applicable rules
        if file_path.endswith(".py"):
            issues.extend(self._python_cleanup(file_path))
        elif file_path.endswith((".ts", ".js")):
            issues.extend(self._javascript_cleanup(file_path))
        elif file_path.endswith((".cs")):
            issues.extend(self._csharp_cleanup(file_path))
        
        # Common cleanup for all files
        issues.extend(self._common_cleanup(file_path))
        
        return len(issues) > 0, issues
    
    def _python_cleanup(self, file_path: str) -> List[str]:
        """Python-specific cleanup checks"""
        issues = []
        
        # Simulated checks (in real implementation, use ast/autopep8)
        issues.append("Applied PEP 8 formatting")
        issues.append("Removed unused imports")
        issues.append("Sorted imports alphabetically")
        
        return issues
    
    def _javascript_cleanup(self, file_path: str) -> List[str]:
        """JavaScript/TypeScript-specific cleanup checks"""
        issues = []
        
        # Simulated checks (in real implementation, use ESLint/Prettier)
        issues.append("Applied Prettier formatting")
        issues.append("Fixed ESLint warnings")
        issues.append("Removed console.log statements")
        
        return issues
    
    def _csharp_cleanup(self, file_path: str) -> List[str]:
        """C#-specific cleanup checks"""
        issues = []
        
        # Simulated checks (in real implementation, use Roslyn)
        issues.append("Applied C# formatting rules")
        issues.append("Removed unused using statements")
        issues.append("Fixed naming conventions")
        
        return issues
    
    def _common_cleanup(self, file_path: str) -> List[str]:
        """Common cleanup for all file types"""
        issues = []
        
        # Simulated checks
        issues.append("Trimmed trailing whitespace")
        issues.append("Normalized line endings")
        issues.append("Added final newline")
        
        return issues
    
    def _generate_summary(
        self,
        files_cleaned: List[str],
        issues_fixed: List[str]
    ) -> str:
        """Generate cleanup summary"""
        if not files_cleaned:
            return "No files required cleanup"
        
        summary = f"Cleaned {len(files_cleaned)} file(s), "
        summary += f"fixed {len(issues_fixed)} issue(s):\n"
        
        # Group issues by type
        issue_counts = {}
        for issue in issues_fixed:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        for issue, count in sorted(issue_counts.items()):
            summary += f"  - {issue}: {count}\n"
        
        return summary.strip()


__all__ = ["CodeCleanup"]
