"""
CORTEX Confidence-Aware Response Generator

Generates responses with confidence indicators based on Knowledge Graph patterns.
Integrates confidence scoring with response template system.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from ..cognitive.confidence_scorer import ConfidenceScorer, ConfidenceScore, ConfidenceLevel
from ..tier2.knowledge_graph import KnowledgeGraph
from .template_loader import TemplateLoader
from .template_renderer import TemplateRenderer


class ConfidenceResponseGenerator:
    """
    Generate responses with confidence indicators
    
    Integrates:
    - Knowledge Graph pattern search with confidence metadata
    - Confidence Scorer for calculating display percentages
    - Template Renderer for formatting responses
    """
    
    def __init__(
        self,
        knowledge_graph: Optional[KnowledgeGraph] = None,
        template_loader: Optional[TemplateLoader] = None,
        template_renderer: Optional[TemplateRenderer] = None
    ):
        """
        Initialize confidence response generator
        
        Args:
            knowledge_graph: Knowledge Graph instance (creates new if None)
            template_loader: Template loader instance (creates new if None)
            template_renderer: Template renderer instance (creates new if None)
        """
        from pathlib import Path
        
        self.knowledge_graph = knowledge_graph or KnowledgeGraph()
        
        # Create template loader with default path if not provided
        if template_loader is None:
            project_root = Path(__file__).parent.parent.parent
            template_file = project_root / "cortex-brain" / "response-templates.yaml"
            self.template_loader = TemplateLoader(template_file)
        else:
            self.template_loader = template_loader
        
        self.template_renderer = template_renderer or TemplateRenderer()
        self.confidence_scorer = ConfidenceScorer()
    
    def generate_response_with_confidence(
        self,
        user_request: str,
        operation_type: str,
        pattern_query: Optional[str] = None,
        min_confidence: float = 0.5,
        base_template_name: str = "success_general",
        **template_context
    ) -> Dict[str, Any]:
        """
        Generate response with confidence indicator
        
        Args:
            user_request: User's request text
            operation_type: Type of operation (Feature Implementation, Planning, etc.)
            pattern_query: Query for Knowledge Graph (defaults to user_request)
            min_confidence: Minimum pattern confidence threshold
            base_template_name: Base template to use for response
            **template_context: Additional context for template rendering
        
        Returns:
            Dict with:
            - response: Formatted response string
            - confidence_score: ConfidenceScore object (or None)
            - patterns_used: Number of patterns applied
            - metadata: Additional metadata
        """
        # Search Knowledge Graph for matching patterns
        pattern_query = pattern_query or user_request
        patterns = self.knowledge_graph.search_patterns(
            query=pattern_query,
            min_confidence=min_confidence,
            limit=10,
            include_confidence_metadata=True
        )
        
        # Determine confidence display strategy
        if not patterns:
            return self._generate_without_patterns(
                user_request=user_request,
                operation_type=operation_type,
                base_template_name=base_template_name,
                **template_context
            )
        
        # Calculate confidence from best pattern
        best_pattern = patterns[0]
        confidence_score = self._calculate_pattern_confidence(best_pattern, patterns)
        
        # Select confidence template based on level
        confidence_indicator = self._format_confidence_indicator(confidence_score)
        
        # Generate full response with confidence display
        return self._generate_with_confidence(
            user_request=user_request,
            operation_type=operation_type,
            confidence_indicator=confidence_indicator,
            confidence_score=confidence_score,
            patterns=patterns,
            base_template_name=base_template_name,
            **template_context
        )
    
    def _calculate_pattern_confidence(
        self,
        best_pattern: Dict[str, Any],
        all_patterns: List[Dict[str, Any]]
    ) -> ConfidenceScore:
        """
        Calculate confidence score from pattern data
        
        Args:
            best_pattern: Highest-ranked pattern from Knowledge Graph
            all_patterns: All matching patterns
        
        Returns:
            ConfidenceScore object with percentage and metadata
        """
        # Parse last_used datetime
        last_used = None
        if best_pattern.get("last_used"):
            try:
                last_used = datetime.fromisoformat(best_pattern["last_used"])
            except (ValueError, TypeError):
                last_used = None
        
        # Calculate confidence using scorer
        confidence_score = self.confidence_scorer.calculate_confidence(
            base_confidence=best_pattern.get("confidence", 0.5),
            usage_count=best_pattern.get("usage_count", 0),
            success_rate=best_pattern.get("success_rate", 0.0),
            last_used=last_used,
            pattern_count=len(all_patterns)
        )
        
        return confidence_score
    
    def _format_confidence_indicator(self, confidence_score: ConfidenceScore) -> str:
        """
        Format confidence indicator using appropriate template
        
        Args:
            confidence_score: ConfidenceScore object
        
        Returns:
            Formatted confidence indicator string
        """
        # Select template based on confidence level
        template_map = {
            ConfidenceLevel.VERY_HIGH: "confidence_high",
            ConfidenceLevel.HIGH: "confidence_high",
            ConfidenceLevel.MEDIUM: "confidence_medium",
            ConfidenceLevel.LOW: "confidence_low",
            ConfidenceLevel.VERY_LOW: "confidence_low"
        }
        
        template_name = template_map.get(confidence_score.level, "confidence_medium")
        
        try:
            template = self.template_loader.load_template(template_name)
            
            # Prepare context for confidence template
            context = {
                "confidence_display": confidence_score.format_display(),
                "pattern_count": confidence_score.pattern_count,
                "detailed_explanation": confidence_score.format_detailed()
            }
            
            return self.template_renderer.render(template, context=context)
        except Exception:
            # Fallback to simple format if template loading fails
            return confidence_score.format_detailed()
    
    def _generate_with_confidence(
        self,
        user_request: str,
        operation_type: str,
        confidence_indicator: str,
        confidence_score: ConfidenceScore,
        patterns: List[Dict[str, Any]],
        base_template_name: str,
        **template_context
    ) -> Dict[str, Any]:
        """
        Generate response with confidence indicator included
        
        Args:
            user_request: User's request
            operation_type: Operation type
            confidence_indicator: Formatted confidence indicator
            confidence_score: ConfidenceScore object
            patterns: Matching patterns from Knowledge Graph
            base_template_name: Base template name
            **template_context: Additional template context
        
        Returns:
            Response dictionary with confidence metadata
        """
        # Build complete context for template
        full_context = {
            "operation_type": operation_type,
            "confidence_indicator": confidence_indicator,
            **template_context
        }
        
        # Load and render base template
        try:
            template = self.template_loader.load_template(base_template_name)
            response_text = self.template_renderer.render(template, context=full_context)
        except Exception as e:
            # Fallback response if template fails
            response_text = f"""# CORTEX {operation_type}
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

{confidence_indicator}

## My Understanding Of Your Request
{user_request}

## Challenge
✓ **Accept**
Processing your request using learned patterns.

## Response
[Response content]

## Your Request
{user_request}

## Next Steps
[Next steps]
"""
        
        return {
            "response": response_text,
            "confidence_score": confidence_score,
            "patterns_used": len(patterns),
            "metadata": {
                "confidence_percentage": confidence_score.percentage,
                "confidence_level": confidence_score.level.value,
                "pattern_count": confidence_score.pattern_count,
                "usage_history": confidence_score.usage_history,
                "best_pattern_id": patterns[0]["pattern_id"] if patterns else None
            }
        }
    
    def _generate_without_patterns(
        self,
        user_request: str,
        operation_type: str,
        base_template_name: str,
        **template_context
    ) -> Dict[str, Any]:
        """
        Generate response for new territory (no patterns available)
        
        Args:
            user_request: User's request
            operation_type: Operation type
            base_template_name: Base template name
            **template_context: Additional template context
        
        Returns:
            Response dictionary without confidence scoring
        """
        # Load "no patterns" confidence template
        try:
            conf_template = self.template_loader.load_template("confidence_none")
            confidence_indicator = self.template_renderer.render(conf_template)
        except Exception:
            confidence_indicator = "ℹ️ **New Territory:** No learned patterns available for this request.\n\nGenerating fresh response using CORTEX capabilities."
        
        # Build context
        full_context = {
            "operation_type": operation_type,
            "confidence_indicator": confidence_indicator,
            **template_context
        }
        
        # Load and render base template
        try:
            template = self.template_loader.load_template(base_template_name)
            response_text = self.template_renderer.render(template, context=full_context)
        except Exception:
            response_text = f"""# CORTEX {operation_type}
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

{confidence_indicator}

## My Understanding Of Your Request
{user_request}

## Challenge
⚡ **Challenge**
This is new territory for CORTEX. No previous patterns exist.

## Response
[Fresh response content]

## Your Request
{user_request}

## Next Steps
[Next steps]
"""
        
        return {
            "response": response_text,
            "confidence_score": None,
            "patterns_used": 0,
            "metadata": {
                "confidence_percentage": None,
                "confidence_level": "New Territory",
                "pattern_count": 0,
                "usage_history": 0,
                "best_pattern_id": None
            }
        }
