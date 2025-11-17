"""
Apply Narrator Voice Module - Story Refresh Operation

This module transforms the technical CORTEX story into a narrator-driven
narrative voice, making it more engaging and accessible.

Author: Asif Hussain
Version: 2.0 (Universal Operations Architecture)
"""

import logging
from pathlib import Path
from typing import Dict, Any, List
from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationPhase,
    OperationStatus
)
from src.config import config

logger = logging.getLogger(__name__)


class ApplyNarratorVoiceModule(BaseOperationModule):
    """
    Validate story structure (VALIDATION-ONLY MODULE).
    
    IMPORTANT: This is a VALIDATION module, not a transformation module.
    
    What it does:
        1. Validates story structure is correct
        2. Checks read time (15-20 minute target)
        3. Ensures narrator voice format is preserved
        4. Does NOT transform content
    
    SKULL-005 Compliance: Marked as validation-only operation.
    The story at prompts/shared/story.md is already in narrator voice.
    This module validates it meets publication standards.
    
    Future Enhancement (Phase 6+):
    - AI-based narrator voice enhancement
    - Intelligent summarization to hit read time target
    - Engagement optimization
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="apply_narrator_voice",
            name="Validate Story Structure",  # Honest name
            description="Validate story structure and read time (validation-only, no transformation)",
            phase=OperationPhase.PROCESSING,
            priority=10,
            dependencies=["load_story_template"],
            optional=False,
            version="1.1",  # Updated for SKULL-005 compliance
            tags=["story", "validation", "required"]  # Changed from transformation to validation
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate that story content is available.
        
        Args:
            context: Must contain 'story_content'
        
        Returns:
            (is_valid, issues_list)
        """
        issues = []
        
        if 'story_content' not in context:
            issues.append("story_content not found in context")
        elif not context['story_content']:
            issues.append("story_content is empty")
        
        return len(issues) == 0, issues
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Validate story structure (VALIDATION-ONLY OPERATION).
        
        IMPORTANT: This module is currently a VALIDATION-ONLY operation.
        It does NOT transform content - it validates the existing narrator voice
        story is properly structured and ready for publication.
        
        SKULL-005 Compliance: Marked as validation-only, not transformation.
        
        Args:
            context: Shared context dictionary
                - Input: story_content (str)
                - Output: transformed_story (str) - SAME as input (validation only)
        
        Returns:
            OperationResult with validation status
        """
        try:
            story_content = context['story_content']
            
            logger.warning(
                "⚠️  VALIDATION-ONLY: This module validates story structure but does NOT transform content. "
                "The story at prompts/shared/story.md is already in narrator voice. "
                "This operation validates it's ready for publication."
            )
            
            # Validate story length against 15-20 minute read time target
            validation = self._validate_read_time(story_content)
            
            # VALIDATION ONLY - No transformation applied
            # The source story is already in narrator voice format
            # This module validates structure and read time compliance
            
            # Validate story structure
            lines = story_content.split('\n')
            has_title = any(line.startswith('# ') for line in lines[:10])
            has_content = len(lines) > 50
            
            if not has_title:
                logger.warning("Story does not have a clear title in first 10 lines")
            
            if not has_content:
                return OperationResult(
                    success=False,
                    status=OperationStatus.FAILED,
                    message="Story content too short (validation failed)",
                    errors=["Story must have at least 50 lines"]
                )
            
            # HONEST STATUS: This is validation-only, not transformation
            context['transformed_story'] = story_content  # Same as input - validation only
            context['transformation_applied'] = False  # NO transformation
            context['transformation_method'] = 'validation-only'  # Explicitly marked
            context['operation_type'] = 'validation'  # For status reporting
            
            # Add read time validation to context for reporting
            context['read_time_validation'] = validation
            
            logger.info(
                f"✅ Story validation complete: {len(lines)} lines validated. "
                f"No transformation applied (source already in narrator voice)."
            )
            
            # Check configuration for enforcement mode
            story_config = config.get('story_refresh', {})
            fail_on_critical = story_config.get('fail_on_critical_length', False)
            
            # Collect warnings from read time validation
            warnings = []
            if validation['status'] in ['slightly_short', 'slightly_long']:
                warnings.append(validation['message'])
                warnings.extend(validation.get('recommendations', []))
            
            # If read time is critically wrong, check enforcement mode
            if validation['status'] in ['too_short', 'too_long']:
                if fail_on_critical:
                    # BLOCKING mode: Return error and stop pipeline
                    return OperationResult(
                        success=False,
                        status=OperationStatus.FAILED,
                        message=validation['message'],
                        errors=[f"Story length validation failed: {validation['message']}"],
                        warnings=validation.get('recommendations', [])
                    )
                else:
                    # WARNING mode: Continue but warn user
                    warnings.append(f"CRITICAL: {validation['message']}")
                    warnings.extend(validation.get('recommendations', []))
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=f"Story structure validated ({len(lines)} lines, {validation['word_count']} words, {validation['read_time']} min) - VALIDATION ONLY, no transformation",
                data={
                    'line_count': len(lines),
                    'character_count': len(story_content),
                    'transformation_method': 'validation-only',  # Honest reporting
                    'operation_type': 'validation',  # Not transformation
                    'has_title': has_title,
                    'has_content': has_content,
                    'word_count': validation['word_count'],
                    'read_time_minutes': validation['read_time'],
                    'read_time_status': validation['status']
                },
                warnings=warnings
            )
        
        except Exception as e:
            logger.error(f"Failed to apply narrator voice: {e}", exc_info=True)
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Narrator voice transformation failed: {e}",
                errors=[str(e)]
            )
    
    def rollback(self, context: Dict[str, Any]) -> bool:
        """
        Rollback narrator voice transformation.
        
        Args:
            context: Shared context dictionary
        
        Returns:
            True (always succeeds)
        """
        logger.debug("Rollback narrator voice transformation")
        
        # Clear transformation data from context
        context.pop('transformed_story', None)
        context.pop('transformation_applied', None)
        context.pop('transformation_method', None)
        
        return True
    
    def should_run(self, context: Dict[str, Any]) -> bool:
        """
        Determine if module should run.
        
        Args:
            context: Shared context dictionary
        
        Returns:
            True (always run for story refresh)
        """
        return True
    
    def get_progress_message(self) -> str:
        """Get progress message."""
        return "Applying narrator voice transformation..."
    
    def _validate_read_time(self, story_content: str) -> Dict[str, Any]:
        """
        Validate story against configurable read time target.
        
        Reads configuration from cortex.config.json:
        - story_refresh.target_read_time_min (default: 25 minutes)
        - story_refresh.target_read_time_max (default: 30 minutes)
        - story_refresh.words_per_minute (default: 200 wpm)
        - story_refresh.tolerance_percent (default: 7%)
        - story_refresh.extended_tolerance_percent (default: 20%)
        
        Args:
            story_content: Story text to validate
            
        Returns:
            Dict with word_count, read_time, status, message, recommendations
        """
        # Load configuration
        story_config = config.get('story_refresh', {})
        
        # Get configured values with defaults
        min_minutes = story_config.get('target_read_time_min', 25)
        max_minutes = story_config.get('target_read_time_max', 30)
        wpm = story_config.get('words_per_minute', 200)
        tolerance = story_config.get('tolerance_percent', 7)
        extended_tolerance = story_config.get('extended_tolerance_percent', 20)
        
        # Count words (filter empty strings)
        words = [w for w in story_content.split() if w.strip()]
        word_count = len(words)
        read_time = round(word_count / wpm, 1)
        
        # Calculate thresholds based on config
        min_target = min_minutes * wpm
        max_target = max_minutes * wpm
        min_acceptable = int(min_target * (1 - tolerance / 100))
        max_acceptable = int(max_target * (1 + tolerance / 100))
        min_warning = int(min_target * (1 - extended_tolerance / 100))
        max_warning = int(max_target * (1 + extended_tolerance / 100))
        
        # Determine status
        if min_acceptable <= word_count <= max_acceptable:
            return {
                'word_count': word_count,
                'read_time': read_time,
                'status': 'optimal',
                'message': f"Story length optimal: {word_count} words ({read_time} min)",
                'recommendations': [],
                'config': {'min': min_minutes, 'max': max_minutes, 'wpm': wpm}
            }
        
        if min_warning <= word_count < min_acceptable:
            deficit = min_acceptable - word_count
            return {
                'word_count': word_count,
                'read_time': read_time,
                'status': 'slightly_short',
                'message': f"Story slightly short: {word_count} words ({read_time} min)",
                'recommendations': [
                    f"Consider adding {deficit} words to reach optimal range ({min_acceptable:,}+ words)"
                ],
                'config': {'min': min_minutes, 'max': max_minutes, 'wpm': wpm}
            }
        
        if max_acceptable < word_count <= max_warning:
            excess = word_count - max_acceptable
            return {
                'word_count': word_count,
                'read_time': read_time,
                'status': 'slightly_long',
                'message': f"Story slightly long: {word_count} words ({read_time} min)",
                'recommendations': [
                    f"Consider trimming {excess} words to reach optimal range (<{max_acceptable:,} words)"
                ],
                'config': {'min': min_minutes, 'max': max_minutes, 'wpm': wpm}
            }
        
        if word_count < min_warning:
            deficit = min_target - word_count
            return {
                'word_count': word_count,
                'read_time': read_time,
                'status': 'too_short',
                'message': f"Story too short: {word_count} words ({read_time} min) - Target: {min_target:,}-{max_target:,} words ({min_minutes}-{max_minutes} min)",
                'recommendations': [
                    f"Need to add ~{deficit:,} words to meet minimum target",
                    "Consider using fuller story version from docs/story/CORTEX-STORY/",
                    "Or expand technical details and examples"
                ],
                'config': {'min': min_minutes, 'max': max_minutes, 'wpm': wpm}
            }
        
        # word_count > max_warning
        excess = word_count - max_target
        return {
            'word_count': word_count,
            'read_time': read_time,
            'status': 'too_long',
            'message': f"Story too long: {word_count} words ({read_time} min) - Target: {min_target:,}-{max_target:,} words ({min_minutes}-{max_minutes} min)",
            'recommendations': [
                f"Need to trim ~{excess:,} words to meet maximum target",
                "Consider condensing technical sections",
                "Remove redundant explanations",
                "Or use AI-based summarization for quality"
            ],
            'config': {'min': min_minutes, 'max': max_minutes, 'wpm': wpm}
        }
