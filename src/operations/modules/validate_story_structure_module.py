"""
Validate Story Structure Module - Story Refresh Operation

This module validates the CORTEX story Markdown structure to ensure
it meets documentation standards.

Author: Asif Hussain
Version: 2.0 (Universal Operations Architecture)
"""

import logging
import re
from pathlib import Path
from typing import Dict, Any, List
from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationPhase,
    OperationStatus
)

logger = logging.getLogger(__name__)


class ValidateStoryStructureModule(BaseOperationModule):
    """
    Validate story Markdown structure.
    
    This module ensures the CORTEX story has proper Markdown formatting
    and meets documentation standards.
    
    What it does:
        1. Validates Markdown syntax
        2. Checks for required sections
        3. Verifies heading hierarchy
        4. Checks for common issues
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="validate_story_structure",
            name="Validate Story Structure",
            description="Ensure story has proper Markdown structure",
            phase=OperationPhase.VALIDATION,
            priority=10,
            dependencies=["apply_narrator_voice"],
            optional=True,
            version="1.0",
            tags=["story", "validation"]
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate that transformed story is available.
        
        Args:
            context: Must contain 'transformed_story'
        
        Returns:
            (is_valid, issues_list)
        """
        issues = []
        
        if 'transformed_story' not in context:
            issues.append("transformed_story not found in context")
        elif not context['transformed_story']:
            issues.append("transformed_story is empty")
        
        return len(issues) == 0, issues
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Validate story structure.
        
        Args:
            context: Shared context dictionary
                - Input: transformed_story (str)
                - Output: validation_results (dict), is_valid (bool)
        
        Returns:
            OperationResult with validation status
        """
        try:
            story_content = context['transformed_story']
            
            logger.info("Validating story structure...")
            
            lines = story_content.split('\n')
            issues = []
            warnings = []
            
            # Check for title (H1)
            h1_pattern = re.compile(r'^# .+')
            h1_found = any(h1_pattern.match(line) for line in lines[:10])
            if not h1_found:
                issues.append("No H1 title found in first 10 lines")
            
            # Check for headings hierarchy
            heading_pattern = re.compile(r'^(#{1,6}) .+')
            headings = []
            for i, line in enumerate(lines):
                match = heading_pattern.match(line)
                if match:
                    level = len(match.group(1))
                    headings.append((i + 1, level, line))
            
            if len(headings) < 3:
                warnings.append(f"Only {len(headings)} headings found - story may lack structure")
            
            # Check for broken heading hierarchy (e.g., H1 → H3 without H2)
            for i in range(1, len(headings)):
                prev_level = headings[i-1][1]
                curr_level = headings[i][1]
                if curr_level > prev_level + 1:
                    warnings.append(
                        f"Heading hierarchy skip at line {headings[i][0]}: "
                        f"H{prev_level} → H{curr_level}"
                    )
            
            # Check for minimum content
            non_empty_lines = [line for line in lines if line.strip()]
            if len(non_empty_lines) < 100:
                warnings.append(f"Story only has {len(non_empty_lines)} non-empty lines")
            
            # Check for common Markdown issues
            # - Multiple consecutive blank lines
            consecutive_blank = 0
            for i, line in enumerate(lines):
                if not line.strip():
                    consecutive_blank += 1
                    if consecutive_blank > 3:
                        warnings.append(f"More than 3 consecutive blank lines around line {i + 1}")
                        consecutive_blank = 0  # Reset to avoid spam
                else:
                    consecutive_blank = 0
            
            # Store validation results
            validation_results = {
                'has_title': h1_found,
                'heading_count': len(headings),
                'line_count': len(lines),
                'non_empty_line_count': len(non_empty_lines),
                'issues': issues,
                'warnings': warnings
            }
            
            context['validation_results'] = validation_results
            context['is_valid'] = len(issues) == 0
            
            # Determine success
            if issues:
                logger.warning(f"Story structure validation failed with {len(issues)} issues")
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message=f"Story structure validation failed ({len(issues)} issues)",
                    data=validation_results,
                    errors=issues,
                    warnings=warnings
                )
            else:
                logger.info(f"Story structure validated: {len(headings)} headings, {len(warnings)} warnings")
                return OperationResult(
                    success=True,
                    status=OperationStatus.SUCCESS,
                    message=f"Story structure valid ({len(headings)} headings, {len(warnings)} warnings)",
                    data=validation_results,
                    warnings=warnings
                )
        
        except Exception as e:
            logger.error(f"Story structure validation failed: {e}", exc_info=True)
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Story structure validation error: {e}",
                errors=[str(e)]
            )
    
    def rollback(self, context: Dict[str, Any]) -> bool:
        """
        Rollback validation (no-op).
        
        Args:
            context: Shared context dictionary
        
        Returns:
            True (always succeeds)
        """
        logger.debug("Rollback story structure validation (no-op)")
        
        context.pop('validation_results', None)
        context.pop('is_valid', None)
        
        return True
    
    def should_run(self, context: Dict[str, Any]) -> bool:
        """
        Determine if module should run.
        
        Args:
            context: Shared context dictionary
        
        Returns:
            True if not in quick profile
        """
        profile = context.get('profile', 'standard')
        return profile != 'quick'
    
    def get_progress_message(self) -> str:
        """Get progress message."""
        return "Validating story structure..."
