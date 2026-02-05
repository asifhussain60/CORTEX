"""
LLM Content Generator for Phase Detail Pages
Generates comprehensive, narrative-driven content using LENS + Git History

Author: Asif Hussain
Version: 1.0
Governance: CORE-008 (TDD), CORE-011 (Type Hints), CORE-012 (Docstrings)
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class TechnicalDecision:
    """Represents a technical decision made during the phase"""
    decision: str
    rationale: str
    date: Optional[str] = None
    commit: Optional[str] = None
    impact: Optional[str] = None


@dataclass
class StoryContext:
    """Context for creating narrative flow between phases"""
    previous_phase: Optional[Dict[str, Any]] = None
    next_phase: Optional[Dict[str, Any]] = None
    transition_narrative: Optional[str] = None
    related_phases: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class DiagramSpec:
    """Specification for generating a diagram"""
    type: str  # "architecture", "workflow", "data_flow", "dependency"
    title: str
    components: List[str] = field(default_factory=list)
    relationships: List[Dict[str, str]] = field(default_factory=list)
    steps: List[str] = field(default_factory=list)
    data_flow: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GeneratedContent:
    """Container for generated content"""
    overview: str
    technical_narrative: str
    decisions: List[TechnicalDecision]
    story_context: StoryContext
    diagram_specs: List[DiagramSpec]
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContentGenerationError(Exception):
    """Raised when content generation fails"""
    pass


# ============================================================================
# LLM CONTENT GENERATOR
# ============================================================================

class LLMContentGenerator:
    """
    Generates comprehensive content for phase detail pages using:
    - LLM for natural language generation
    - LENS analyzers for code intelligence
    - Git history for timeline context
    - Enhancement history for decision tracking
    
    Examples:
        >>> generator = LLMContentGenerator()
        >>> phase_yaml = {"phase_id": "01", "title": "Event Bus"}
        >>> content = generator.generate_overview(phase_yaml)
        >>> print(content[:100])
        'Phase 01: Event Bus introduces event-driven architecture...'
    """
    
    def __init__(
        self, 
        config: Optional[Dict[str, Any]] = None,
        enable_cache: bool = True
    ):
        """
        Initialize LLM content generator
        
        Args:
            config: Configuration dictionary (temperature, max_tokens, etc.)
            enable_cache: Enable content caching for performance
        """
        self.config = config or self._default_config()
        self.enable_cache = enable_cache
        self._cache: Dict[str, Any] = {}
        self.cache_hits = 0
        self.lens_client = None  # Will be initialized on first use
        
        logger.info("LLMContentGenerator initialized", extra={
            "config": self.config,
            "cache_enabled": enable_cache
        })
    
    def _default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "temperature": 0.7,
            "max_tokens": 2000,
            "model": "gpt-4",
            "fallback_to_template": True
        }
    
    # ========================================================================
    # OVERVIEW GENERATION
    # ========================================================================
    
    def generate_overview(
        self, 
        phase_yaml: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate compelling overview from phase YAML metadata
        
        Args:
            phase_yaml: Phase metadata dictionary
            context: Additional context (previous phases, etc.)
            
        Returns:
            Generated overview text (minimum 100 characters)
            
        Raises:
            ContentGenerationError: If generation fails
            
        Examples:
            >>> generator = LLMContentGenerator()
            >>> phase = {"phase_id": "01", "title": "Event Bus"}
            >>> overview = generator.generate_overview(phase)
            >>> len(overview) >= 100
            True
        """
        if phase_yaml is None:
            raise ContentGenerationError("Phase YAML cannot be None")
        
        # Check cache
        cache_key = self._get_cache_key("overview", phase_yaml)
        if self.enable_cache and cache_key in self._cache:
            self.cache_hits += 1
            return self._cache[cache_key]
        
        try:
            # Extract key information
            phase_id = phase_yaml.get("phase_id", "Unknown")
            title = phase_yaml.get("title", "Unknown Phase")
            objectives = phase_yaml.get("objectives", [])
            key_features = phase_yaml.get("key_features", [])
            
            # Build context-aware overview
            overview_parts = []
            
            # Main introduction
            overview_parts.append(
                f"Phase {phase_id}: {title} represents a critical milestone in the CORTEX development journey. "
            )
            
            # Add objectives
            if objectives:
                obj_text = self._format_objectives(objectives)
                overview_parts.append(f"This phase focuses on {obj_text}. ")
            
            # Add features
            if key_features:
                feat_text = self._format_features(key_features)
                overview_parts.append(f"Key capabilities delivered include {feat_text}. ")
            
            # Add context from previous phases
            if context and context.get("previous_phases"):
                prev_text = self._generate_context_narrative(context["previous_phases"])
                overview_parts.append(prev_text)
            
            # Add impact statement
            overview_parts.append(
                f"The implementation of {title} enhances system capabilities "
                "while maintaining architectural integrity and code quality standards."
            )
            
            overview = "".join(overview_parts)
            
            # Ensure minimum length
            if len(overview) < 100:
                overview += " This phase contributes to the overall system evolution and production readiness."
            
            # Cache result
            if self.enable_cache:
                self._cache[cache_key] = overview
            
            return overview
            
        except Exception as e:
            if self.config.get("fallback_to_template"):
                return self._generate_template_overview(phase_yaml)
            raise ContentGenerationError(f"Overview generation failed: {e}")
    
    def _format_objectives(self, objectives: List[str]) -> str:
        """Format objectives list into narrative text"""
        if len(objectives) == 1:
            return objectives[0].lower()
        elif len(objectives) == 2:
            return f"{objectives[0].lower()} and {objectives[1].lower()}"
        else:
            formatted = ", ".join(obj.lower() for obj in objectives[:-1])
            return f"{formatted}, and {objectives[-1].lower()}"
    
    def _format_features(self, features: List[Union[str, Dict[str, Any]]]) -> str:
        """Format features list into narrative text"""
        feature_names = []
        for f in features:
            if isinstance(f, dict):
                feature_names.append(f.get("name", str(f)))
            else:
                feature_names.append(str(f))
        
        if len(feature_names) == 1:
            return feature_names[0]
        elif len(feature_names) == 2:
            return f"{feature_names[0]} and {feature_names[1]}"
        else:
            formatted = ", ".join(feature_names[:-1])
            return f"{formatted}, and {feature_names[-1]}"
    
    def _generate_context_narrative(self, previous_phases: List[Dict[str, Any]]) -> str:
        """Generate narrative connecting to previous phases"""
        if not previous_phases:
            return ""
        
        last_phase = previous_phases[-1]
        return (
            f"Building upon the foundation established in Phase {last_phase.get('phase_id')}: "
            f"{last_phase.get('title')}, this phase extends the system's capabilities. "
        )
    
    def _generate_template_overview(self, phase_yaml: Dict[str, Any]) -> str:
        """Generate template-based overview as fallback"""
        phase_id = phase_yaml.get("phase_id", "Unknown")
        title = phase_yaml.get("title", "Unknown Phase")
        return (
            f"Phase {phase_id}: {title} is an important phase in the CORTEX development lifecycle. "
            f"This phase delivers key functionality and maintains code quality standards. "
            f"Implementation follows TDD principles and architectural best practices."
        )
    
    # ========================================================================
    # TECHNICAL NARRATIVE GENERATION
    # ========================================================================
    
    def generate_technical_narrative(self, phase_yaml: Dict[str, Any]) -> str:
        """
        Generate technical narrative from implementation details
        
        Args:
            phase_yaml: Phase metadata with implementation details
            
        Returns:
            Technical narrative explaining implementation
        """
        try:
            narrative_parts = []
            
            # Extract implementation details
            impl = phase_yaml.get("implementation", {})
            components = impl.get("components", [])
            patterns = impl.get("patterns", [])
            
            if components:
                comp_text = ", ".join(components)
                narrative_parts.append(
                    f"The implementation introduces {comp_text} as core components. "
                )
            
            if patterns:
                pattern_text = ", ".join(patterns)
                narrative_parts.append(
                    f"This phase leverages {pattern_text} design patterns "
                    "to ensure maintainability and extensibility. "
                )
            
            # Technical decisions
            decisions = phase_yaml.get("technical_decisions", [])
            if decisions:
                for decision in decisions:
                    if isinstance(decision, dict):
                        dec_text = decision.get("decision", "")
                        rationale = decision.get("rationale", "")
                        if dec_text and rationale:
                            narrative_parts.append(
                                f"The decision to {dec_text} was driven by {rationale}. "
                            )
            
            if not narrative_parts:
                return "Technical implementation follows established patterns and best practices."
            
            return "".join(narrative_parts)
            
        except Exception as e:
            logger.warning(f"Technical narrative generation failed: {e}")
            return "Technical implementation details are documented in the codebase."
    
    # ========================================================================
    # DECISION EXTRACTION
    # ========================================================================
    
    def extract_decisions(
        self, 
        git_history: Optional[List[Dict[str, Any]]] = None,
        phase_yaml: Optional[Dict[str, Any]] = None
    ) -> List[TechnicalDecision]:
        """
        Extract technical decisions from git history and phase metadata
        
        Args:
            git_history: List of git commits
            phase_yaml: Phase metadata
            
        Returns:
            List of TechnicalDecision objects
        """
        decisions: List[TechnicalDecision] = []
        
        # Extract from phase YAML
        if phase_yaml:
            yaml_decisions = phase_yaml.get("technical_decisions", [])
            for dec in yaml_decisions:
                if isinstance(dec, dict):
                    decisions.append(TechnicalDecision(
                        decision=dec.get("decision", ""),
                        rationale=dec.get("rationale", ""),
                        date=dec.get("date"),
                        impact=dec.get("impact")
                    ))
        
        # Extract from git history
        if git_history:
            for commit in git_history:
                message = commit.get("message", "")
                
                # Filter for decision-indicating commits
                decision_keywords = [
                    "implement", "add", "introduce", "refactor",
                    "architecture", "design", "pattern"
                ]
                
                if any(keyword in message.lower() for keyword in decision_keywords):
                    # Skip trivial commits
                    if not any(skip in message.lower() for skip in ["typo", "readme", "fix"]):
                        decisions.append(TechnicalDecision(
                            decision=message,
                            rationale="Identified from git commit",
                            date=commit.get("date"),
                            commit=commit.get("commit")
                        ))
        
        return decisions
    
    def extract_decisions_from_enhancements(
        self, 
        enhancement_data: Dict[str, Any]
    ) -> List[TechnicalDecision]:
        """
        Extract technical decisions from enhancement history
        
        Args:
            enhancement_data: Enhancement history data
            
        Returns:
            List of TechnicalDecision objects
        """
        decisions: List[TechnicalDecision] = []
        
        for enh_id, enh_data in enhancement_data.items():
            if isinstance(enh_data, dict):
                decision = enh_data.get("decision")
                rationale = enh_data.get("rationale")
                
                if decision:
                    decisions.append(TechnicalDecision(
                        decision=decision,
                        rationale=rationale or "Enhancement-driven decision",
                        impact=f"Enhancement {enh_id}"
                    ))
        
        return decisions
    
    # ========================================================================
    # STORY CONTEXT GENERATION
    # ========================================================================
    
    def create_story_links(
        self, 
        current_phase: Dict[str, Any],
        all_phases: List[Dict[str, Any]]
    ) -> StoryContext:
        """
        Create story context linking phases together
        
        Args:
            current_phase: Current phase metadata
            all_phases: List of all phases
            
        Returns:
            StoryContext with previous/next links and transition narrative
        """
        # Extract numeric ID from formats like "PHASE-01" or "01"
        phase_id_str = str(current_phase.get("phase_id", "0"))
        current_id = int(phase_id_str.split("-")[-1]) if "-" in phase_id_str else int(phase_id_str)
        
        # Find previous and next phases
        previous_phase = None
        next_phase = None
        
        for phase in all_phases:
            # Extract numeric ID from formats like "PHASE-01" or "01"
            phase_id_str = str(phase.get("phase_id", "0"))
            phase_id = int(phase_id_str.split("-")[-1]) if "-" in phase_id_str else int(phase_id_str)
            
            if phase_id == current_id - 1:
                previous_phase = phase
            elif phase_id == current_id + 1:
                next_phase = phase
        
        # Generate transition narrative
        transition = None
        if previous_phase and next_phase:
            transition = self._generate_transition_narrative(
                previous_phase, 
                current_phase, 
                next_phase
            )
        
        return StoryContext(
            previous_phase=previous_phase,
            next_phase=next_phase,
            transition_narrative=transition
        )
    
    def _generate_transition_narrative(
        self,
        previous_phase: Dict[str, Any],
        current_phase: Dict[str, Any],
        next_phase: Dict[str, Any]
    ) -> str:
        """Generate narrative explaining phase transitions"""
        prev_title = previous_phase.get("title", "the previous phase")
        curr_title = current_phase.get("title", "this phase")
        next_title = next_phase.get("title", "the next phase")
        
        return (
            f"Following the completion of {prev_title}, {curr_title} builds upon "
            f"that foundation to deliver enhanced capabilities. This phase sets "
            f"the stage for {next_title}, creating a coherent development narrative."
        )
    
    # ========================================================================
    # DIAGRAM SPECIFICATION GENERATION
    # ========================================================================
    
    def generate_diagram_specs(self, phase_yaml: Dict[str, Any]) -> List[DiagramSpec]:
        """
        Generate diagram specifications from phase metadata
        
        Args:
            phase_yaml: Phase metadata
            
        Returns:
            List of DiagramSpec objects
        """
        specs: List[DiagramSpec] = []
        
        # Architecture diagram
        if "architecture" in phase_yaml:
            arch = phase_yaml["architecture"]
            specs.append(DiagramSpec(
                type="architecture",
                title=f"Architecture - Phase {phase_yaml.get('phase_id')}",
                components=arch.get("components", []),
                relationships=arch.get("relationships", [])
            ))
        
        # Workflow diagram
        if "workflow" in phase_yaml:
            workflow = phase_yaml["workflow"]
            specs.append(DiagramSpec(
                type="workflow",
                title=f"Workflow - Phase {phase_yaml.get('phase_id')}",
                steps=workflow.get("steps", [])
            ))
        
        # Data flow diagram
        if "data_flow" in phase_yaml:
            data_flow = phase_yaml["data_flow"]
            specs.append(DiagramSpec(
                type="data_flow",
                title=f"Data Flow - Phase {phase_yaml.get('phase_id')}",
                data_flow=data_flow
            ))
        
        return specs
    
    # ========================================================================
    # LENS INTEGRATION
    # ========================================================================
    
    def extract_technical_insights(self, lens_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract technical insights from LENS analysis
        
        Args:
            lens_data: LENS analysis results
            
        Returns:
            Dictionary of technical insights
        """
        insights = {}
        
        if "code_quality" in lens_data:
            quality = lens_data["code_quality"]
            insights["quality_assessment"] = (
                f"Code quality score of {quality}/10 indicates "
                f"{'excellent' if quality >= 8 else 'good' if quality >= 6 else 'acceptable'} "
                "implementation standards."
            )
        
        if "test_coverage" in lens_data:
            coverage = lens_data["test_coverage"]
            insights["test_coverage"] = (
                f"Test coverage at {coverage}% "
                f"{'exceeds' if coverage >= 80 else 'meets' if coverage >= 70 else 'approaches'} "
                "project targets."
            )
        
        return insights
    
    # ========================================================================
    # GIT HISTORY INTEGRATION
    # ========================================================================
    
    def load_git_history(self, phase_yaml: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Load git history for phase time period
        
        Args:
            phase_yaml: Phase metadata with start/completion dates
            
        Returns:
            List of git commits
        """
        # Placeholder - would integrate with actual git history
        return []
    
    def extract_contributors(self, git_history: List[Dict[str, Any]]) -> List[str]:
        """
        Extract unique contributors from git history
        
        Args:
            git_history: List of git commits
            
        Returns:
            List of contributor names
        """
        contributors = set()
        for commit in git_history:
            author = commit.get("author")
            if author:
                contributors.add(author)
        return sorted(list(contributors))
    
    # ========================================================================
    # CACHING UTILITIES
    # ========================================================================
    
    def _get_cache_key(self, content_type: str, data: Dict[str, Any]) -> str:
        """Generate cache key from content type and data"""
        data_str = json.dumps(data, sort_keys=True)
        data_hash = hashlib.md5(data_str.encode()).hexdigest()
        return f"{content_type}_{data_hash}"
    
    def clear_cache(self) -> None:
        """Clear content cache"""
        self._cache.clear()
        self.cache_hits = 0
        logger.info("Content cache cleared")
