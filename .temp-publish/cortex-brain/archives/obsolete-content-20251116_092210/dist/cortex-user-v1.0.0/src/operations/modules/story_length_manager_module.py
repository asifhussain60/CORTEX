"""
Story Length Manager Module

Validates and manages story content length to ensure 15-20 minute read time target.
Provides intelligent recommendations for content that falls outside the target range.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

from typing import Dict, Any, List, Optional
from src.operations.base_operation_module import (
    BaseOperationModule, 
    OperationResult, 
    OperationModuleMetadata, 
    OperationPhase, 
    OperationStatus
)

# Alias for backward compatibility
ModuleResult = OperationResult


class StoryLengthManagerModule(BaseOperationModule):
    """
    Validates story length against 15-20 minute read time target.
    
    Target Specifications:
    - Read Speed: 200 words per minute (industry standard)
    - Target Range: 15-20 minutes = 3,000-4,000 words
    - Acceptable Range: 2,800-4,200 words (±7% tolerance)
    
    Validation Levels:
    - PASS: Within acceptable range (2,800-4,200 words)
    - WARNING: Outside acceptable but within extended range (2,400-4,600 words)
    - ERROR: Far outside target range (< 2,400 or > 4,600 words)
    """
    
    # Configuration constants
    MIN_TARGET_WORDS = 3000  # 15 minutes at 200 wpm
    MAX_TARGET_WORDS = 4000  # 20 minutes at 200 wpm
    WORDS_PER_MINUTE = 200   # Industry standard reading speed
    TOLERANCE_PERCENT = 7    # ±7% tolerance
    EXTENDED_TOLERANCE = 20  # ±20% for warnings
    
    def __init__(self):
        super().__init__()
        self._calculate_thresholds()
    
    def _calculate_thresholds(self):
        """Calculate acceptable and warning thresholds."""
        tolerance = int(self.MIN_TARGET_WORDS * (self.TOLERANCE_PERCENT / 100))
        extended = int(self.MIN_TARGET_WORDS * (self.EXTENDED_TOLERANCE / 100))
        
        self.min_acceptable = self.MIN_TARGET_WORDS - tolerance  # 2,790
        self.max_acceptable = self.MAX_TARGET_WORDS + tolerance  # 4,280
        self.min_warning = self.MIN_TARGET_WORDS - extended      # 2,400
        self.max_warning = self.MAX_TARGET_WORDS + extended      # 4,800
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="story_length_manager",
            name="Story Length Manager",
            description="Validates story length against 15-20 minute read time target",
            phase=OperationPhase.VALIDATION,
            priority=20,
            dependencies=[],
            optional=False,
        )
    
    def get_module_id(self) -> str:
        return "story_length_manager"
    
    def get_description(self) -> str:
        return "Validates story length against 15-20 minute read time target"
    
    def get_required_inputs(self) -> List[str]:
        return ["story_content"]
    
    def get_output_keys(self) -> List[str]:
        return [
            "validated_content",
            "word_count",
            "read_time_minutes",
            "validation_status",
            "recommendations"
        ]
    
    def execute(self, inputs: Dict[str, Any]) -> ModuleResult:
        """
        Validate story length and provide recommendations.
        
        Args:
            inputs: Dict with 'story_content' key containing story text
            
        Returns:
            ModuleResult with validation status and recommendations
        """
        try:
            story_content = inputs.get("story_content", "")
            
            if not story_content or not isinstance(story_content, str):
                return self._create_error_result(
                    "Invalid or missing story content"
                )
            
            # Analyze content metrics
            metrics = self._analyze_content(story_content)
            
            # Validate against targets
            validation = self._validate_metrics(metrics)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(metrics, validation)
            
            # Determine overall status
            if validation["level"] == "ERROR":
                return self._create_error_result(
                    validation["message"],
                    {
                        "validated_content": story_content,
                        "word_count": metrics["word_count"],
                        "read_time_minutes": metrics["read_time"],
                        "validation_status": validation,
                        "recommendations": recommendations
                    }
                )
            
            # Return success or warning
            return ModuleResult(
                success=True,
                data={
                    "validated_content": story_content,
                    "word_count": metrics["word_count"],
                    "read_time_minutes": metrics["read_time"],
                    "validation_status": validation,
                    "recommendations": recommendations
                },
                warnings=validation.get("warnings", []),
                metadata={
                    "target_range": f"{self.MIN_TARGET_WORDS}-{self.MAX_TARGET_WORDS} words",
                    "acceptable_range": f"{self.min_acceptable}-{self.max_acceptable} words",
                    "read_speed": f"{self.WORDS_PER_MINUTE} wpm"
                }
            )
            
        except Exception as e:
            return self._create_error_result(f"Length validation failed: {str(e)}")
    
    def _analyze_content(self, content: str) -> Dict[str, Any]:
        """
        Analyze content metrics.
        
        Args:
            content: Story content string
            
        Returns:
            Dict with word_count, line_count, char_count, read_time
        """
        lines = content.split('\n')
        words = content.split()
        
        # Filter out empty words
        words = [w for w in words if w.strip()]
        
        word_count = len(words)
        read_time = word_count / self.WORDS_PER_MINUTE
        
        return {
            "word_count": word_count,
            "line_count": len(lines),
            "char_count": len(content),
            "read_time": round(read_time, 1)
        }
    
    def _validate_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate metrics against target thresholds.
        
        Args:
            metrics: Content metrics from _analyze_content
            
        Returns:
            Dict with validation level, message, and status
        """
        word_count = metrics["word_count"]
        read_time = metrics["read_time"]
        
        # Check if within acceptable range (PASS)
        if self.min_acceptable <= word_count <= self.max_acceptable:
            return {
                "level": "PASS",
                "status": "optimal",
                "message": f"Story length optimal: {word_count} words ({read_time} min)",
                "warnings": []
            }
        
        # Check if within warning range
        if self.min_warning <= word_count < self.min_acceptable:
            return {
                "level": "WARNING",
                "status": "slightly_short",
                "message": f"Story slightly short: {word_count} words ({read_time} min)",
                "warnings": [
                    f"Story is {self.min_acceptable - word_count} words below optimal range"
                ]
            }
        
        if self.max_acceptable < word_count <= self.max_warning:
            return {
                "level": "WARNING",
                "status": "slightly_long",
                "message": f"Story slightly long: {word_count} words ({read_time} min)",
                "warnings": [
                    f"Story is {word_count - self.max_acceptable} words above optimal range"
                ]
            }
        
        # Outside warning range (ERROR)
        if word_count < self.min_warning:
            return {
                "level": "ERROR",
                "status": "too_short",
                "message": f"Story too short: {word_count} words ({read_time} min) - Target: {self.MIN_TARGET_WORDS}-{self.MAX_TARGET_WORDS} words",
                "warnings": []
            }
        
        # word_count > self.max_warning
        return {
            "level": "ERROR",
            "status": "too_long",
            "message": f"Story too long: {word_count} words ({read_time} min) - Target: {self.MIN_TARGET_WORDS}-{self.MAX_TARGET_WORDS} words",
            "warnings": []
        }
    
    def _generate_recommendations(
        self,
        metrics: Dict[str, Any],
        validation: Dict[str, Any]
    ) -> List[str]:
        """
        Generate actionable recommendations based on validation status.
        
        Args:
            metrics: Content metrics
            validation: Validation results
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        word_count = metrics["word_count"]
        status = validation["status"]
        
        if status == "optimal":
            recommendations.append("✅ Story length is optimal - no changes needed")
            return recommendations
        
        if status == "slightly_short":
            deficit = self.min_acceptable - word_count
            recommendations.extend([
                f"📊 Current: {word_count} words | Target: {self.MIN_TARGET_WORDS}+ words",
                f"➕ Consider adding {deficit} words to reach optimal range",
                "💡 Suggestions:",
                "   - Expand key technical concepts with more detail",
                "   - Add concrete examples or use cases",
                "   - Include more context about architecture decisions"
            ])
        
        elif status == "slightly_long":
            excess = word_count - self.max_acceptable
            recommendations.extend([
                f"📊 Current: {word_count} words | Target: {self.MAX_TARGET_WORDS} words",
                f"➖ Consider trimming {excess} words to reach optimal range",
                "💡 Suggestions:",
                "   - Remove redundant explanations",
                "   - Tighten verbose sections",
                "   - Focus on core narrative elements"
            ])
        
        elif status == "too_short":
            deficit = self.MIN_TARGET_WORDS - word_count
            recommendations.extend([
                f"❌ Current: {word_count} words | Minimum: {self.MIN_TARGET_WORDS} words",
                f"➕ Need to add {deficit} words to meet minimum target",
                "💡 Critical Actions:",
                "   - Review source content for missing sections",
                "   - Consider using fuller story version (docs/story/CORTEX-STORY/Awakening Of CORTEX.md)",
                "   - Expand technical details and examples",
                "   - Add more context about CORTEX capabilities"
            ])
        
        elif status == "too_long":
            excess = word_count - self.MAX_TARGET_WORDS
            recommendations.extend([
                f"❌ Current: {word_count} words | Maximum: {self.MAX_TARGET_WORDS} words",
                f"➖ Need to trim {excess} words to meet maximum target",
                "💡 Critical Actions:",
                "   - Remove non-essential sections",
                "   - Condense technical explanations",
                "   - Consider AI-based summarization for better quality",
                "   - Focus on core narrative flow"
            ])
        
        return recommendations
    
    def _create_error_result(
        self,
        error_message: str,
        partial_data: Optional[Dict[str, Any]] = None
    ) -> ModuleResult:
        """Create error result with optional partial data."""
        return ModuleResult(
            success=False,
            data=partial_data or {},
            errors=[error_message],
            metadata={"module": self.get_module_id()}
        )


def create_module() -> BaseOperationModule:
    """Factory function for module creation."""
    return StoryLengthManagerModule()
