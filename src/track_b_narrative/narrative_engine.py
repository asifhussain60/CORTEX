"""
CORTEX 3.0 Track B Phase 4 - Narrative Engine

Core narrative generation engine with story templates, context weaving,
and decision rationale extraction. Works with mock dual-channel data
during development phase (Weeks 8-15).

Key Features:
- Story template system for coherent narratives
- Context weaving algorithm for connecting development events  
- Decision rationale extraction from conversation patterns
- Integration with existing narrative_intelligence.py

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import json
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from pathlib import Path

from .mock_data import MockConversation, MockDaemonCapture, DualChannelMockData
from ..tier1.narrative_intelligence import (
    NarrativeIntelligence, StoryType, NarrativeStyle, 
    StoryElement, DevelopmentNarrative
)

logger = logging.getLogger(__name__)


@dataclass
class StoryTemplate:
    """Template for generating consistent story structures"""
    template_id: str
    name: str
    story_type: StoryType
    narrative_style: NarrativeStyle
    structure: List[str]  # Ordered list of story sections
    prompts: Dict[str, str]  # Section -> prompt mapping
    context_requirements: List[str]  # Required context elements
    success_criteria: Dict[str, Any]  # Quality metrics


@dataclass  
class ContextElement:
    """Contextual element extracted from dual-channel data"""
    element_id: str
    timestamp: datetime
    source_type: str  # "conversation", "daemon_capture"
    content: str
    entities: List[str]
    relationships: List[str]  # Connections to other elements
    confidence: float
    metadata: Dict[str, Any]


@dataclass
class DecisionRationale:
    """Extracted decision rationale from development flow"""
    decision_id: str
    timestamp: datetime
    decision_type: str  # "architectural", "implementation", "bug_fix", "feature"
    context_summary: str
    options_considered: List[str]
    chosen_approach: str
    reasoning: str
    outcome_observed: Optional[str]
    confidence: float


class StoryTemplateSystem:
    """
    Advanced story template system for narrative generation.
    
    Provides structured templates for different types of development stories,
    ensuring consistent and coherent narrative output.
    """
    
    def __init__(self, template_dir: str = None):
        """Initialize story template system"""
        self.template_dir = Path(template_dir) if template_dir else Path.cwd() / "story_templates"
        self.templates: Dict[str, StoryTemplate] = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Load default story templates"""
        
        # Development Progress Template
        dev_progress = StoryTemplate(
            template_id="dev_progress_technical",
            name="Technical Development Progress",
            story_type=StoryType.DEVELOPMENT_PROGRESS,
            narrative_style=NarrativeStyle.TECHNICAL,
            structure=[
                "overview",
                "key_achievements", 
                "technical_decisions",
                "challenges_resolved",
                "code_evolution",
                "next_steps"
            ],
            prompts={
                "overview": "Summarize the overall development progress and main objectives achieved.",
                "key_achievements": "List the significant features, fixes, or improvements completed.",
                "technical_decisions": "Describe important architectural or implementation decisions made.",
                "challenges_resolved": "Explain problems encountered and how they were solved.",
                "code_evolution": "Show how the codebase evolved through specific changes.",
                "next_steps": "Identify upcoming work and logical next development phases."
            },
            context_requirements=[
                "conversations", "file_changes", "git_commits", "time_range"
            ],
            success_criteria={
                "coherence_score": 0.8,
                "completeness_score": 0.9,
                "technical_depth": 0.7
            }
        )
        
        # Feature Journey Template  
        feature_journey = StoryTemplate(
            template_id="feature_journey_storytelling", 
            name="Feature Development Story",
            story_type=StoryType.FEATURE_JOURNEY,
            narrative_style=NarrativeStyle.STORYTELLING,
            structure=[
                "motivation",
                "initial_approach",
                "discovery_process", 
                "implementation_journey",
                "testing_validation",
                "final_outcome"
            ],
            prompts={
                "motivation": "What drove the need for this feature? What problem was being solved?",
                "initial_approach": "How did the development team initially plan to implement this?",
                "discovery_process": "What was learned during investigation and planning?",
                "implementation_journey": "Tell the story of how the feature was built, including pivots.",
                "testing_validation": "How was the feature validated and what feedback was incorporated?",
                "final_outcome": "What was delivered and how does it solve the original problem?"
            },
            context_requirements=[
                "feature_conversations", "implementation_files", "test_files"
            ],
            success_criteria={
                "narrative_flow": 0.8,
                "engagement_score": 0.7,
                "completeness_score": 0.8
            }
        )
        
        # Problem Resolution Template
        problem_resolution = StoryTemplate(
            template_id="problem_resolution_chronological",
            name="Bug Fix & Problem Resolution", 
            story_type=StoryType.PROBLEM_RESOLUTION,
            narrative_style=NarrativeStyle.CHRONOLOGICAL,
            structure=[
                "problem_identification",
                "investigation_process",
                "root_cause_analysis", 
                "solution_design",
                "implementation_steps",
                "verification_testing",
                "lessons_learned"
            ],
            prompts={
                "problem_identification": "How was the problem first discovered or reported?",
                "investigation_process": "What steps were taken to understand and reproduce the issue?", 
                "root_cause_analysis": "What was determined to be the underlying cause?",
                "solution_design": "How was the fix designed and what alternatives were considered?",
                "implementation_steps": "What specific changes were made to resolve the issue?",
                "verification_testing": "How was the fix validated and tested?",
                "lessons_learned": "What insights were gained for preventing similar issues?"
            },
            context_requirements=[
                "bug_report", "debug_conversations", "fix_commits", "test_results"  
            ],
            success_criteria={
                "problem_clarity": 0.9,
                "solution_completeness": 0.8,
                "chronological_accuracy": 0.9
            }
        )
        
        # Store templates
        self.templates[dev_progress.template_id] = dev_progress
        self.templates[feature_journey.template_id] = feature_journey  
        self.templates[problem_resolution.template_id] = problem_resolution
        
        logger.info(f"Loaded {len(self.templates)} default story templates")
    
    def get_template(self, template_id: str) -> Optional[StoryTemplate]:
        """Get story template by ID"""
        return self.templates.get(template_id)
    
    def get_templates_by_type(self, story_type: StoryType) -> List[StoryTemplate]:
        """Get all templates for a story type"""
        return [t for t in self.templates.values() if t.story_type == story_type]
    
    def generate_story_structure(self, template_id: str, context_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate story structure using template and context"""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")
            
        # Validate context requirements
        missing_context = []
        for req in template.context_requirements:
            if req not in context_data:
                missing_context.append(req)
        
        if missing_context:
            logger.warning(f"Missing context for template {template_id}: {missing_context}")
        
        # Generate content for each section
        story_sections = {}
        for section in template.structure:
            prompt = template.prompts.get(section, f"Generate content for {section}")
            
            # Use context weaving to generate section content
            content = self._generate_section_content(section, prompt, context_data)
            story_sections[section] = content
            
        return story_sections
    
    def _generate_section_content(self, section: str, prompt: str, context_data: Dict[str, Any]) -> str:
        """Generate content for a story section using context"""
        # This is where context weaving algorithm applies the prompt to available context
        # For now, return a placeholder that shows the structure
        
        relevant_context = self._extract_relevant_context(section, context_data)
        
        content = f"{prompt}\\n\\nBased on available context:\\n"
        
        if relevant_context:
            for item in relevant_context[:3]:  # Top 3 most relevant
                content += f"- {item}\\n"
        else:
            content += "- [Context analysis would be applied here]\\n"
            
        return content
    
    def _extract_relevant_context(self, section: str, context_data: Dict[str, Any]) -> List[str]:
        """Extract context relevant to a specific story section"""
        # Simplified relevance matching for mock data phase
        relevant_items = []
        
        if "conversations" in context_data:
            for conv in context_data["conversations"]:
                if hasattr(conv, 'messages'):
                    for msg in conv.messages:
                        if len(msg.get('content', '')) > 20:  # Non-trivial content
                            relevant_items.append(f"Conversation: {msg['content'][:100]}...")
                            
        if "file_changes" in context_data:
            for change in context_data["file_changes"]:
                if hasattr(change, 'file_path'):
                    relevant_items.append(f"File modified: {change.file_path}")
                    
        return relevant_items


class ContextWeavingEngine:
    """
    Advanced context weaving algorithm for narrative generation.
    
    Analyzes dual-channel data to identify relationships, patterns,
    and narrative threads that connect development events into coherent stories.
    """
    
    def __init__(self, mock_data: DualChannelMockData = None):
        """Initialize context weaving engine"""
        self.mock_data = mock_data or DualChannelMockData()
        self.context_cache: Dict[str, List[ContextElement]] = {}
        
    def extract_context_elements(self, conversations: List[MockConversation], 
                                captures: List[MockDaemonCapture]) -> List[ContextElement]:
        """Extract contextual elements from dual-channel data"""
        elements = []
        
        # Process conversations
        for conv in conversations:
            for i, msg in enumerate(conv.messages):
                element = ContextElement(
                    element_id=f"conv_{conv.conversation_id}_{i}",
                    timestamp=conv.timestamp,
                    source_type="conversation",
                    content=msg.get('content', ''),
                    entities=conv.entities_extracted,
                    relationships=conv.files_mentioned,
                    confidence=0.8,
                    metadata={
                        "conversation_id": conv.conversation_id,
                        "message_role": msg.get('role', 'unknown'),
                        "session_type": conv.session_type
                    }
                )
                elements.append(element)
        
        # Process daemon captures
        for capture in captures:
            element = ContextElement(
                element_id=f"capture_{capture.capture_id}",
                timestamp=capture.timestamp,
                source_type="daemon_capture", 
                content=f"{capture.event_type}: {capture.file_path}",
                entities=[capture.file_path],
                relationships=[],
                confidence=0.9,  # High confidence for file system events
                metadata={
                    "capture_id": capture.capture_id,
                    "event_type": capture.event_type,
                    "change_type": capture.change_type,
                    "git_metadata": capture.git_metadata
                }
            )
            elements.append(element)
            
        # Sort by timestamp for chronological processing
        elements.sort(key=lambda x: x.timestamp)
        
        return elements
    
    def weave_context_narrative(self, elements: List[ContextElement], 
                              time_window: timedelta = timedelta(hours=24)) -> Dict[str, Any]:
        """Weave context elements into narrative threads"""
        
        # Group elements by time proximity
        narrative_threads = self._identify_narrative_threads(elements, time_window)
        
        # Analyze relationships between threads  
        thread_relationships = self._analyze_thread_relationships(narrative_threads)
        
        # Generate narrative structure
        narrative_structure = self._create_narrative_structure(narrative_threads, thread_relationships)
        
        return {
            "narrative_threads": narrative_threads,
            "thread_relationships": thread_relationships, 
            "narrative_structure": narrative_structure,
            "context_summary": self._summarize_context(elements),
            "weaving_metadata": {
                "total_elements": len(elements),
                "threads_identified": len(narrative_threads),
                "time_span": self._calculate_time_span(elements),
                "confidence": self._calculate_overall_confidence(elements)
            }
        }
    
    def _identify_narrative_threads(self, elements: List[ContextElement], 
                                  time_window: timedelta) -> Dict[str, List[ContextElement]]:
        """Identify narrative threads based on temporal and semantic proximity"""
        threads = {}
        current_thread_id = 0
        
        for element in elements:
            # Find existing thread within time window
            matching_thread = None
            
            for thread_id, thread_elements in threads.items():
                if thread_elements:
                    last_element = thread_elements[-1]
                    time_diff = abs(element.timestamp - last_element.timestamp)
                    
                    if time_diff <= time_window:
                        # Check semantic similarity (simplified)
                        if self._has_semantic_connection(element, last_element):
                            matching_thread = thread_id
                            break
            
            # Add to existing thread or create new one
            if matching_thread:
                threads[matching_thread].append(element)
            else:
                thread_id = f"thread_{current_thread_id}"
                threads[thread_id] = [element]
                current_thread_id += 1
                
        return threads
    
    def _has_semantic_connection(self, elem1: ContextElement, elem2: ContextElement) -> bool:
        """Check if two elements have semantic connection"""
        # Simple entity overlap check for mock phase
        common_entities = set(elem1.entities) & set(elem2.entities)
        common_relationships = set(elem1.relationships) & set(elem2.relationships)
        
        return len(common_entities) > 0 or len(common_relationships) > 0
    
    def _analyze_thread_relationships(self, threads: Dict[str, List[ContextElement]]) -> Dict[str, Any]:
        """Analyze relationships between narrative threads"""
        relationships = {}
        
        thread_ids = list(threads.keys())
        for i, thread_id in enumerate(thread_ids):
            relationships[thread_id] = {
                "depends_on": [],
                "influences": [],
                "parallel_to": [],
                "strength": 0.0
            }
            
            # Check relationships with other threads
            for j, other_thread_id in enumerate(thread_ids):
                if i != j:
                    relationship_strength = self._calculate_thread_relationship_strength(
                        threads[thread_id], threads[other_thread_id]
                    )
                    
                    if relationship_strength > 0.3:
                        relationships[thread_id]["influences"].append({
                            "thread_id": other_thread_id,
                            "strength": relationship_strength
                        })
                        
        return relationships
    
    def _calculate_thread_relationship_strength(self, thread1: List[ContextElement], 
                                              thread2: List[ContextElement]) -> float:
        """Calculate relationship strength between two threads"""
        if not thread1 or not thread2:
            return 0.0
            
        # Simple overlap-based calculation for mock phase
        all_entities_1 = set()
        all_entities_2 = set()
        
        for elem in thread1:
            all_entities_1.update(elem.entities)
        for elem in thread2:
            all_entities_2.update(elem.entities)
            
        overlap = len(all_entities_1 & all_entities_2)
        total_unique = len(all_entities_1 | all_entities_2)
        
        return overlap / max(total_unique, 1)
    
    def _create_narrative_structure(self, threads: Dict[str, List[ContextElement]], 
                                  relationships: Dict[str, Any]) -> Dict[str, Any]:
        """Create overall narrative structure from threads and relationships"""
        
        # Identify main narrative arc (longest/most connected thread)
        main_thread = max(threads.items(), key=lambda x: len(x[1]))[0]
        
        # Create chronological sequence
        all_elements = []
        for thread_elements in threads.values():
            all_elements.extend(thread_elements)
        all_elements.sort(key=lambda x: x.timestamp)
        
        return {
            "main_thread": main_thread,
            "chronological_sequence": [elem.element_id for elem in all_elements],
            "narrative_arc": {
                "beginning": all_elements[0].element_id if all_elements else None,
                "middle": all_elements[len(all_elements)//2].element_id if all_elements else None,
                "end": all_elements[-1].element_id if all_elements else None
            },
            "complexity_score": len(threads) * 0.1 + sum(len(t) for t in threads.values()) * 0.01
        }
    
    def _summarize_context(self, elements: List[ContextElement]) -> Dict[str, Any]:
        """Generate summary of context elements"""
        if not elements:
            return {}
            
        entity_counts = {}
        source_type_counts = {}
        
        for elem in elements:
            # Count entities
            for entity in elem.entities:
                entity_counts[entity] = entity_counts.get(entity, 0) + 1
            
            # Count source types
            source_type_counts[elem.source_type] = source_type_counts.get(elem.source_type, 0) + 1
        
        return {
            "total_elements": len(elements),
            "top_entities": sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "source_distribution": source_type_counts,
            "time_span_hours": self._calculate_time_span(elements),
            "average_confidence": sum(elem.confidence for elem in elements) / len(elements)
        }
    
    def _calculate_time_span(self, elements: List[ContextElement]) -> float:
        """Calculate time span of elements in hours"""
        if not elements:
            return 0.0
            
        timestamps = [elem.timestamp for elem in elements]
        time_span = max(timestamps) - min(timestamps)
        return time_span.total_seconds() / 3600
    
    def _calculate_overall_confidence(self, elements: List[ContextElement]) -> float:
        """Calculate overall confidence score for context weaving"""
        if not elements:
            return 0.0
            
        return sum(elem.confidence for elem in elements) / len(elements)


class DecisionRationaleExtractor:
    """
    Extracts decision rationales from development conversations and code changes.
    
    Identifies moments where decisions were made, options considered,
    and reasoning behind choices for inclusion in narrative generation.
    """
    
    def __init__(self):
        """Initialize decision rationale extractor"""
        self.decision_patterns = {
            "architectural": ["architecture", "design", "structure", "pattern", "approach"],
            "implementation": ["implement", "code", "function", "method", "algorithm"],
            "bug_fix": ["bug", "fix", "error", "issue", "problem", "debug"],
            "feature": ["feature", "add", "new", "enhance", "improvement"]
        }
        
    def extract_decisions(self, conversations: List[MockConversation], 
                         captures: List[MockDaemonCapture]) -> List[DecisionRationale]:
        """Extract decision rationales from dual-channel data"""
        decisions = []
        
        # Process conversations for decision points
        for conv in conversations:
            decision = self._analyze_conversation_for_decisions(conv)
            if decision:
                decisions.append(decision)
        
        # Process captures for implementation decisions
        for capture in captures:
            decision = self._analyze_capture_for_decisions(capture)
            if decision:
                decisions.append(decision)
                
        return sorted(decisions, key=lambda x: x.timestamp)
    
    def _analyze_conversation_for_decisions(self, conversation: MockConversation) -> Optional[DecisionRationale]:
        """Analyze conversation for decision points"""
        
        # Look for decision indicators in messages
        decision_indicators = []
        full_content = ""
        
        for msg in conversation.messages:
            content = msg.get('content', '').lower()
            full_content += content + " "
            
            # Check for decision keywords
            for decision_type, keywords in self.decision_patterns.items():
                for keyword in keywords:
                    if keyword in content:
                        decision_indicators.append((decision_type, keyword))
        
        if not decision_indicators:
            return None
            
        # Determine primary decision type
        decision_counts = {}
        for decision_type, _ in decision_indicators:
            decision_counts[decision_type] = decision_counts.get(decision_type, 0) + 1
            
        primary_decision_type = max(decision_counts.items(), key=lambda x: x[1])[0]
        
        # Extract decision details (simplified for mock phase)
        decision_id = f"decision_{conversation.conversation_id}"
        
        return DecisionRationale(
            decision_id=decision_id,
            timestamp=conversation.timestamp,
            decision_type=primary_decision_type,
            context_summary=f"Decision made during conversation about {', '.join(conversation.files_mentioned)}",
            options_considered=["Option A (mentioned in conversation)", "Option B (alternative considered)"],
            chosen_approach=f"{primary_decision_type} approach based on conversation",
            reasoning="Analysis of conversation content suggests this decision rationale",
            outcome_observed=None,  # Would be filled by later analysis
            confidence=0.7
        )
    
    def _analyze_capture_for_decisions(self, capture: MockDaemonCapture) -> Optional[DecisionRationale]:
        """Analyze daemon capture for implementation decisions"""
        
        # Only process git commits as they indicate completed decisions
        if capture.event_type != "git_commit" or not capture.git_metadata:
            return None
            
        commit_msg = capture.git_metadata.get("message", "").lower()
        
        # Check if commit message indicates a decision
        decision_type = None
        for dec_type, keywords in self.decision_patterns.items():
            for keyword in keywords:
                if keyword in commit_msg:
                    decision_type = dec_type
                    break
            if decision_type:
                break
                
        if not decision_type:
            return None
            
        decision_id = f"decision_commit_{capture.capture_id}"
        
        return DecisionRationale(
            decision_id=decision_id,
            timestamp=capture.timestamp,
            decision_type=decision_type,
            context_summary=f"Implementation decision reflected in commit to {capture.file_path}",
            options_considered=["Previous implementation", "New implementation (committed)"],
            chosen_approach=f"Committed changes to {capture.file_path}",
            reasoning=f"Commit message: {capture.git_metadata.get('message', 'No message')}",
            outcome_observed="Changes committed to repository",
            confidence=0.8
        )


# Integration with existing narrative intelligence
def enhance_narrative_intelligence_with_track_b(narrative_intelligence: NarrativeIntelligence,
                                               mock_data: DualChannelMockData = None) -> Dict[str, Any]:
    """
    Enhance existing narrative intelligence with Track B Phase 4 capabilities.
    
    This function bridges the new Track B narrative engine with the existing
    tier1/narrative_intelligence.py system.
    """
    
    # Initialize Track B components
    template_system = StoryTemplateSystem()
    context_engine = ContextWeavingEngine(mock_data)
    decision_extractor = DecisionRationaleExtractor()
    
    # Load mock data
    if not mock_data:
        mock_data = DualChannelMockData()
    
    conversations = mock_data.load_mock_conversations()
    captures = mock_data.load_mock_captures()
    
    # Generate enhanced context
    context_elements = context_engine.extract_context_elements(conversations, captures)
    woven_context = context_engine.weave_context_narrative(context_elements)
    decisions = decision_extractor.extract_decisions(conversations, captures)
    
    # Integration results
    integration_results = {
        "track_b_components": {
            "story_templates": len(template_system.templates),
            "context_elements": len(context_elements),
            "narrative_threads": len(woven_context.get("narrative_threads", {})),
            "decisions_extracted": len(decisions)
        },
        "mock_data_stats": {
            "conversations": len(conversations),
            "captures": len(captures),
            "time_span_hours": woven_context.get("weaving_metadata", {}).get("time_span", 0)
        },
        "enhancement_capabilities": [
            "Story template system for consistent narratives",
            "Context weaving for connecting development events", 
            "Decision rationale extraction for development insights",
            "Mock data integration for development phase"
        ],
        "integration_status": "ready_for_continue_command_enhancement"
    }
    
    return integration_results