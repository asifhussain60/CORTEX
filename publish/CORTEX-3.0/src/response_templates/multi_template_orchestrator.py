"""Multi-Template Response Orchestrator for CORTEX.

This module enables intelligent selection and composition of multiple relevant templates
based on user context, with proper conflict resolution and priority handling.

Author: Asif Hussain
Version: 1.0
"""

import re
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from collections import Counter

from .template_loader import Template
from .template_registry import TemplateRegistry
from .template_renderer import TemplateRenderer


@dataclass
class TemplateScore:
    """Represents a template with its relevance score."""
    template: Template
    score: float
    matched_keywords: Set[str] = field(default_factory=set)
    matched_triggers: List[str] = field(default_factory=list)
    context_match: bool = False
    

@dataclass
class CompositionRule:
    """Rules for composing multiple templates together."""
    allow_merge: bool = True
    section_priority: Dict[str, int] = field(default_factory=dict)
    deduplicate_sections: bool = True
    max_templates: int = 3
    min_relevance_score: float = 0.3


class RelevanceScorer:
    """Scores templates for relevance to user query and context."""
    
    def __init__(self):
        """Initialize relevance scorer."""
        self.keyword_weight = 0.4
        self.trigger_weight = 0.3
        self.context_weight = 0.2
        self.category_weight = 0.1
        
    def score_template(
        self,
        template: Template,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> TemplateScore:
        """Score a template's relevance to query and context.
        
        Args:
            template: Template to score
            query: User query
            context: Optional context dictionary
            
        Returns:
            TemplateScore object with relevance score
        """
        context = context or {}
        query_lower = query.lower()
        
        # Initialize score components
        keyword_score = 0.0
        trigger_score = 0.0
        context_score = 0.0
        category_score = 0.0
        
        matched_keywords = set()
        matched_triggers = []
        
        # Extract query keywords (simple tokenization)
        query_keywords = set(re.findall(r'\w+', query_lower))
        
        # Score keyword matches in template content
        content_lower = template.content.lower()
        content_keywords = set(re.findall(r'\w+', content_lower))
        
        keyword_matches = query_keywords & content_keywords
        matched_keywords = keyword_matches
        
        if keyword_matches:
            keyword_score = len(keyword_matches) / max(len(query_keywords), 1)
        
        # Score trigger matches
        for trigger in template.triggers:
            if trigger.lower() in query_lower:
                trigger_score = 1.0
                matched_triggers.append(trigger)
                break
        
        # Score context match (check if template supports context keys)
        if context:
            template_placeholders = set(re.findall(r'\{\{(\w+)\}\}', template.content))
            context_keys = set(context.keys())
            context_matches = template_placeholders & context_keys
            
            if template_placeholders:
                context_score = len(context_matches) / len(template_placeholders)
        
        # Score category relevance
        if template.metadata and 'category' in template.metadata:
            category = template.metadata['category'].lower()
            if any(cat_word in query_lower for cat_word in category.split()):
                category_score = 1.0
        
        # Calculate weighted total score
        total_score = (
            keyword_score * self.keyword_weight +
            trigger_score * self.trigger_weight +
            context_score * self.context_weight +
            category_score * self.category_weight
        )
        
        return TemplateScore(
            template=template,
            score=total_score,
            matched_keywords=matched_keywords,
            matched_triggers=matched_triggers,
            context_match=context_score > 0
        )
    
    def score_templates(
        self,
        templates: List[Template],
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[TemplateScore]:
        """Score multiple templates and return ranked list.
        
        Args:
            templates: List of templates to score
            query: User query
            context: Optional context dictionary
            
        Returns:
            List of TemplateScore objects, sorted by score descending
        """
        scored_templates = [
            self.score_template(template, query, context)
            for template in templates
        ]
        
        # Sort by score descending
        scored_templates.sort(key=lambda x: x.score, reverse=True)
        
        return scored_templates


class TemplateCompositor:
    """Composes multiple templates into coherent response."""
    
    def __init__(self):
        """Initialize template compositor."""
        self.section_header_pattern = re.compile(r'^(#+\s+.+|[🧠🎯⚠️💬📝🔍]\s+\*\*.+\*\*)', re.MULTILINE)
    
    def compose(
        self,
        scored_templates: List[TemplateScore],
        rule: CompositionRule,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Compose multiple templates into single response.
        
        Args:
            scored_templates: List of scored templates
            rule: Composition rules
            context: Optional context for rendering
            
        Returns:
            Composed response string
        """
        context = context or {}
        
        # Filter by minimum score and max count
        eligible_templates = [
            st for st in scored_templates
            if st.score >= rule.min_relevance_score
        ][:rule.max_templates]
        
        if not eligible_templates:
            return ""
        
        # If only one template, render directly
        if len(eligible_templates) == 1:
            renderer = TemplateRenderer()
            return renderer.render(eligible_templates[0].template, context)
        
        # Compose multiple templates
        return self._merge_templates(eligible_templates, rule, context)
    
    def _merge_templates(
        self,
        scored_templates: List[TemplateScore],
        rule: CompositionRule,
        context: Dict[str, Any]
    ) -> str:
        """Merge multiple templates with deduplication and priority.
        
        Args:
            scored_templates: List of scored templates
            rule: Composition rules
            context: Rendering context
            
        Returns:
            Merged template string
        """
        renderer = TemplateRenderer()
        sections = {}
        
        # Extract sections from each template
        for st in scored_templates:
            rendered = renderer.render(st.template, context)
            template_sections = self._extract_sections(rendered)
            
            for section_name, section_content in template_sections.items():
                if section_name not in sections:
                    sections[section_name] = []
                
                sections[section_name].append({
                    'content': section_content,
                    'score': st.score,
                    'template_id': st.template.template_id
                })
        
        # Deduplicate and prioritize sections
        merged_sections = {}
        for section_name, section_variants in sections.items():
            if rule.deduplicate_sections and len(section_variants) > 1:
                # Use highest scoring variant
                section_variants.sort(key=lambda x: x['score'], reverse=True)
                merged_sections[section_name] = section_variants[0]['content']
            else:
                # Combine all variants
                merged_sections[section_name] = '\n\n'.join(
                    v['content'] for v in section_variants
                )
        
        # Apply section priority ordering
        ordered_sections = self._order_sections(merged_sections, rule.section_priority)
        
        # Assemble final response
        return '\n\n'.join(ordered_sections.values())
    
    def _extract_sections(self, content: str) -> Dict[str, str]:
        """Extract sections from template content.
        
        Args:
            content: Template content
            
        Returns:
            Dictionary of section_name -> section_content
        """
        sections = {}
        lines = content.split('\n')
        current_section = 'header'
        current_content = []
        
        for line in lines:
            if self.section_header_pattern.match(line):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = line.strip()
                current_content = [line]
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _order_sections(
        self,
        sections: Dict[str, str],
        priority: Dict[str, int]
    ) -> Dict[str, str]:
        """Order sections by priority.
        
        Args:
            sections: Dictionary of sections
            priority: Section priority mapping (higher = first)
            
        Returns:
            Ordered dictionary of sections
        """
        if not priority:
            return sections
        
        # Sort by priority (higher first), then alphabetically
        sorted_items = sorted(
            sections.items(),
            key=lambda x: (-priority.get(x[0], 0), x[0])
        )
        
        return dict(sorted_items)


class ConflictResolver:
    """Resolves conflicts when templates overlap or contradict."""
    
    def __init__(self):
        """Initialize conflict resolver."""
        self.priority_map = {
            'error': 100,  # Error templates highest priority
            'security': 90,
            'planning': 80,
            'execution': 70,
            'validation': 60,
            'help': 50,
            'status': 40,
            'general': 30
        }
    
    def resolve_conflicts(
        self,
        scored_templates: List[TemplateScore]
    ) -> List[TemplateScore]:
        """Resolve conflicts between templates.
        
        Args:
            scored_templates: List of scored templates
            
        Returns:
            Filtered list with conflicts resolved
        """
        if len(scored_templates) <= 1:
            return scored_templates
        
        # Group by response_type
        by_type = {}
        for st in scored_templates:
            response_type = getattr(st.template, 'response_type', 'general')
            if response_type not in by_type:
                by_type[response_type] = []
            by_type[response_type].append(st)
        
        # Keep highest priority from each type
        resolved = []
        for response_type, templates in by_type.items():
            priority = self.priority_map.get(response_type, 0)
            
            # Sort by score within type
            templates.sort(key=lambda x: x.score, reverse=True)
            
            # Keep top template from this type
            if templates:
                resolved.append(templates[0])
        
        # Sort final list by priority and score
        resolved.sort(
            key=lambda x: (
                -self.priority_map.get(
                    getattr(x.template, 'response_type', 'general'),
                    0
                ),
                -x.score
            )
        )
        
        return resolved
    
    def detect_redundancy(
        self,
        templates: List[Template]
    ) -> List[Tuple[int, int]]:
        """Detect redundant template pairs.
        
        Args:
            templates: List of templates
            
        Returns:
            List of (index1, index2) pairs that are redundant
        """
        redundant_pairs = []
        
        for i, template1 in enumerate(templates):
            for j, template2 in enumerate(templates[i+1:], start=i+1):
                if self._are_redundant(template1, template2):
                    redundant_pairs.append((i, j))
        
        return redundant_pairs
    
    def _are_redundant(self, template1: Template, template2: Template) -> bool:
        """Check if two templates are redundant.
        
        Args:
            template1: First template
            template2: Second template
            
        Returns:
            True if templates are redundant
        """
        # Check trigger overlap
        triggers1 = set(t.lower() for t in template1.triggers)
        triggers2 = set(t.lower() for t in template2.triggers)
        
        trigger_overlap = len(triggers1 & triggers2) / max(len(triggers1), len(triggers2), 1)
        
        # Check content similarity (simple word overlap)
        words1 = set(re.findall(r'\w+', template1.content.lower()))
        words2 = set(re.findall(r'\w+', template2.content.lower()))
        
        content_overlap = len(words1 & words2) / max(len(words1), len(words2), 1)
        
        # Consider redundant if high overlap
        return trigger_overlap > 0.7 or content_overlap > 0.8


class ResponseBlender:
    """Blends multiple template outputs into coherent response."""
    
    def __init__(self):
        """Initialize response blender."""
        self.transition_phrases = [
            "Additionally,",
            "Furthermore,",
            "Moreover,",
            "In addition to this,",
            "Building on this,"
        ]
    
    def blend(
        self,
        composed_content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Blend composed content into final response.
        
        Args:
            composed_content: Composed template content
            metadata: Optional metadata about composition
            
        Returns:
            Final blended response
        """
        if not composed_content:
            return ""
        
        # Add smooth transitions between sections if needed
        content = self._add_transitions(composed_content)
        
        # Ensure proper formatting
        content = self._format_response(content)
        
        return content
    
    def _add_transitions(self, content: str) -> str:
        """Add smooth transitions between major sections.
        
        Args:
            content: Composed content
            
        Returns:
            Content with transitions
        """
        # This is a simple implementation
        # Can be enhanced with NLP for better transitions
        return content
    
    def _format_response(self, content: str) -> str:
        """Format final response for consistency.
        
        Args:
            content: Response content
            
        Returns:
            Formatted content
        """
        # Remove excessive blank lines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Ensure consistent spacing around headers
        content = re.sub(r'([^\n])\n(#+\s)', r'\1\n\n\2', content)
        content = re.sub(r'(#+\s.+)\n([^\n])', r'\1\n\n\2', content)
        
        return content.strip()


class MultiTemplateOrchestrator:
    """Orchestrates multi-template response generation."""
    
    def __init__(self, template_registry: TemplateRegistry):
        """Initialize multi-template orchestrator.
        
        Args:
            template_registry: Template registry instance
        """
        self.registry = template_registry
        self.scorer = RelevanceScorer()
        self.compositor = TemplateCompositor()
        self.resolver = ConflictResolver()
        self.blender = ResponseBlender()
        
        # Default composition rule
        self.default_rule = CompositionRule(
            allow_merge=True,
            deduplicate_sections=True,
            max_templates=3,
            min_relevance_score=0.3,
            section_priority={
                '🧠 **CORTEX': 100,  # Header always first
                '🎯 **My Understanding': 90,
                '⚠️ **Challenge:': 80,
                '💬 **Response:': 70,
                '📝 **Your Request:': 60,
                '🔍 **Next Steps:': 50
            }
        )
    
    def generate_response(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        rule: Optional[CompositionRule] = None
    ) -> str:
        """Generate multi-template response for query.
        
        Args:
            query: User query
            context: Optional context dictionary
            rule: Optional composition rules (uses default if None)
            
        Returns:
            Composed response string
        """
        context = context or {}
        rule = rule or self.default_rule
        
        # Get all templates
        all_templates = self.registry.list_templates()
        
        if not all_templates:
            return "No templates available."
        
        # Score templates for relevance
        scored_templates = self.scorer.score_templates(all_templates, query, context)
        
        # Resolve conflicts
        resolved_templates = self.resolver.resolve_conflicts(scored_templates)
        
        # Compose templates
        composed = self.compositor.compose(resolved_templates, rule, context)
        
        # Blend into final response
        final_response = self.blender.blend(composed)
        
        return final_response
    
    def get_relevant_templates(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        top_n: int = 5,
        min_score: float = 0.3
    ) -> List[TemplateScore]:
        """Get top N relevant templates for query.
        
        Args:
            query: User query
            context: Optional context dictionary
            top_n: Number of top templates to return
            min_score: Minimum relevance score
            
        Returns:
            List of top N TemplateScore objects
        """
        all_templates = self.registry.list_templates()
        scored_templates = self.scorer.score_templates(all_templates, query, context)
        
        # Filter by minimum score
        eligible = [st for st in scored_templates if st.score >= min_score]
        
        return eligible[:top_n]
    
    def explain_selection(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Explain why templates were selected for query.
        
        Args:
            query: User query
            context: Optional context dictionary
            
        Returns:
            Dictionary with explanation details
        """
        relevant_templates = self.get_relevant_templates(query, context)
        
        explanation = {
            'query': query,
            'context_provided': bool(context),
            'templates_scored': self.registry.get_template_count(),
            'relevant_templates': [],
            'selection_reasoning': []
        }
        
        for st in relevant_templates:
            template_info = {
                'template_id': st.template.template_id,
                'score': round(st.score, 3),
                'matched_keywords': list(st.matched_keywords),
                'matched_triggers': st.matched_triggers,
                'context_match': st.context_match
            }
            explanation['relevant_templates'].append(template_info)
            
            # Build reasoning
            reasons = []
            if st.matched_triggers:
                reasons.append(f"Matched triggers: {', '.join(st.matched_triggers)}")
            if st.matched_keywords:
                reasons.append(f"Keyword overlap: {len(st.matched_keywords)} words")
            if st.context_match:
                reasons.append("Context data available")
            
            explanation['selection_reasoning'].append({
                'template': st.template.template_id,
                'reasons': reasons
            })
        
        return explanation
