"""
CORTEX 3.0 Track B Phase 4 - Enhanced Continue Command Implementation

Intelligent continuation system using temporal context analysis, timeline reconstruction,
and multi-session awareness for seamless workflow resumption.

NEW - Phase 4 Implementation: Smart continue functionality with dual-channel data
integration, context reconstruction, and enhanced narrative-driven continuation.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import yaml
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from pathlib import Path
import logging

from .narrative_engine import TemporalContextAnalyzer, ContextElement
from .integration_system import MockDataIntegrationSystem

logger = logging.getLogger(__name__)


@dataclass
class ContinueContext:
    """Context data structure for continue command operations"""
    session_timeline: Dict[str, Any]
    last_activity: Optional[datetime]
    active_files: List[str]
    pending_decisions: List[Dict[str, Any]]
    workflow_state: Dict[str, Any]
    narrative_context: str
    confidence_score: float
    reconstruction_metadata: Dict[str, Any]


@dataclass
class ContinuationSuggestion:
    """Smart suggestion for workflow continuation"""
    suggestion_type: str  # 'resume_task', 'continue_implementation', 'resolve_decision', 'new_context'
    description: str
    priority: int  # 1 = highest priority
    context_basis: str
    suggested_actions: List[str]
    confidence: float
    estimated_effort_minutes: Optional[int]
    dependencies: List[str]


class EnhancedContinueCommand:
    """
    Enhanced Continue Command Implementation for Track B Phase 4.
    
    Provides intelligent workflow resumption using temporal context analysis,
    dual-channel data integration, and narrative-driven context reconstruction.
    
    Key Capabilities:
    - Timeline reconstruction from conversation and daemon data
    - Multi-session workflow awareness
    - Context-aware continuation suggestions
    - Decision point identification and resolution
    - Narrative-driven progress summaries
    """
    
    def __init__(self, data_source_dir: str = None, context_window_hours: int = 24):
        """Initialize enhanced continue command system"""
        self.data_source_dir = Path(data_source_dir) if data_source_dir else Path.cwd() / "data"
        self.context_window_hours = context_window_hours
        
        # Initialize components
        self.temporal_analyzer = TemporalContextAnalyzer()
        self.integration_system = MockDataIntegrationSystem()
        
        # Cache for context reconstruction
        self._context_cache = {}
        self._last_analysis_time = None
        
        logger.info(f"Enhanced Continue Command initialized - Phase 4 Implementation")
    
    def execute_continue_command(self, user_request: str = "continue", 
                                context_hints: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute enhanced continue command with intelligent context reconstruction.
        
        Args:
            user_request: User's continue request (default: "continue")
            context_hints: Optional hints about desired continuation context
            
        Returns:
            Dict containing continuation context, suggestions, and narrative summary
        """
        
        logger.info(f"Executing enhanced continue command: '{user_request}'")
        execution_start = datetime.now()
        
        # Step 1: Load and analyze recent context data
        context_data = self._load_recent_context_data()
        
        # Step 2: Perform temporal context analysis
        temporal_analysis = self._perform_temporal_analysis(context_data)
        
        # Step 3: Reconstruct current context state
        continue_context = self._reconstruct_continue_context(
            temporal_analysis, context_hints or {}
        )
        
        # Step 4: Generate intelligent continuation suggestions
        continuation_suggestions = self._generate_continuation_suggestions(
            continue_context, user_request
        )
        
        # Step 5: Create narrative summary of current state
        narrative_summary = self._create_narrative_summary(
            continue_context, temporal_analysis
        )
        
        # Step 6: Determine recommended next actions
        recommended_actions = self._determine_recommended_actions(
            continuation_suggestions, continue_context
        )
        
        execution_time = (datetime.now() - execution_start).total_seconds() * 1000
        
        continue_result = {
            "continue_command_result": {
                "status": "success",
                "execution_time_ms": execution_time,
                "timestamp": execution_start.isoformat(),
                "user_request": user_request
            },
            "current_context": {
                "session_timeline": continue_context.session_timeline,
                "last_activity": continue_context.last_activity.isoformat() if continue_context.last_activity else None,
                "active_files": continue_context.active_files,
                "workflow_state": continue_context.workflow_state,
                "confidence_score": continue_context.confidence_score
            },
            "narrative_summary": narrative_summary,
            "continuation_suggestions": [
                {
                    "type": suggestion.suggestion_type,
                    "description": suggestion.description,
                    "priority": suggestion.priority,
                    "actions": suggestion.suggested_actions,
                    "confidence": suggestion.confidence,
                    "effort_minutes": suggestion.estimated_effort_minutes
                }
                for suggestion in continuation_suggestions
            ],
            "recommended_actions": recommended_actions,
            "pending_decisions": continue_context.pending_decisions,
            "temporal_insights": {
                "work_sessions_identified": len(temporal_analysis.get("work_sessions", [])),
                "activity_patterns": temporal_analysis.get("activity_patterns", {}),
                "context_switches": temporal_analysis.get("context_switches", [])
            },
            "next_steps_guidance": self._create_next_steps_guidance(
                continuation_suggestions, continue_context
            )
        }
        
        # Cache result for performance
        self._update_context_cache(continue_result)
        
        logger.info(f"Enhanced continue command completed: {execution_time:.1f}ms")
        return continue_result
    
    def _load_recent_context_data(self) -> List[ContextElement]:
        """Load recent context data from dual-channel sources"""
        
        # Calculate time window for context loading
        cutoff_time = datetime.now() - timedelta(hours=self.context_window_hours)
        
        # In production: Load from conversation DB and daemon capture files
        # For Phase 4 development: Use mock data integration system
        try:
            # Use integration system to generate realistic context data
            mock_conversations = self.integration_system.mock_data.generate_conversations(count=10)
            mock_captures = self.integration_system.mock_data.generate_daemon_captures(count=20)
            
            # Extract context elements from mock data
            context_elements = self.integration_system.context_weaver.extract_context_elements(
                mock_conversations, mock_captures
            )
            
            # Filter by time window
            recent_context = [
                elem for elem in context_elements 
                if elem.timestamp >= cutoff_time
            ]
            
            logger.info(f"Loaded {len(recent_context)} recent context elements")
            return recent_context
            
        except Exception as e:
            logger.error(f"Error loading recent context data: {e}")
            return []
    
    def _perform_temporal_analysis(self, context_data: List[ContextElement]) -> Dict[str, Any]:
        """Perform enhanced temporal context analysis"""
        
        if not context_data:
            logger.warning("No context data available for temporal analysis")
            return {
                "work_sessions": [],
                "activity_patterns": {},
                "context_switches": [],
                "timeline_visualization": {}
            }
        
        try:
            # Use TemporalContextAnalyzer for sophisticated analysis
            temporal_analysis = self.temporal_analyzer.analyze_temporal_patterns(context_data)
            
            # Enhance with continue-specific analysis
            enhanced_analysis = temporal_analysis.copy()
            enhanced_analysis.update({
                "continuation_readiness": self._assess_continuation_readiness(temporal_analysis),
                "workflow_momentum": self._calculate_workflow_momentum(temporal_analysis),
                "context_coherence": self._evaluate_context_coherence(context_data),
                "decision_points": self._identify_decision_points(context_data)
            })
            
            return enhanced_analysis
            
        except Exception as e:
            logger.error(f"Error in temporal analysis: {e}")
            return {"error": str(e)}
    
    def _reconstruct_continue_context(self, temporal_analysis: Dict[str, Any], 
                                     context_hints: Dict[str, Any]) -> ContinueContext:
        """Reconstruct comprehensive continue context from temporal analysis"""
        
        # Extract session timeline
        session_timeline = temporal_analysis.get("timeline_visualization", {})
        
        # Determine last activity
        work_sessions = temporal_analysis.get("work_sessions", [])
        last_activity = None
        if work_sessions:
            last_session = max(work_sessions, key=lambda s: s.get("end_time", ""))
            if last_session.get("end_time"):
                last_activity = datetime.fromisoformat(last_session["end_time"])
        
        # Identify active files from recent activity
        active_files = []
        for session in work_sessions[-3:]:  # Last 3 sessions
            session_files = session.get("files_involved", [])
            active_files.extend(session_files)
        active_files = list(set(active_files))  # Remove duplicates
        
        # Extract pending decisions
        pending_decisions = temporal_analysis.get("decision_points", [])
        
        # Determine workflow state
        workflow_state = {
            "current_phase": self._infer_current_phase(temporal_analysis),
            "momentum_level": temporal_analysis.get("workflow_momentum", 0.5),
            "context_coherence": temporal_analysis.get("context_coherence", 0.5),
            "session_continuity": len(work_sessions) > 0,
            "recent_activity_hours": self._calculate_hours_since_last_activity(last_activity)
        }
        
        # Generate narrative context
        narrative_context = self._generate_context_narrative(temporal_analysis, context_hints)
        
        # Calculate confidence score
        confidence_score = self._calculate_context_confidence(
            temporal_analysis, len(active_files), len(pending_decisions)
        )
        
        # Create reconstruction metadata
        reconstruction_metadata = {
            "analysis_timestamp": datetime.now().isoformat(),
            "data_sources": ["conversations", "daemon_captures"],
            "context_window_hours": self.context_window_hours,
            "sessions_analyzed": len(work_sessions),
            "temporal_patterns_found": len(temporal_analysis.get("activity_patterns", {}))
        }
        
        return ContinueContext(
            session_timeline=session_timeline,
            last_activity=last_activity,
            active_files=active_files,
            pending_decisions=pending_decisions,
            workflow_state=workflow_state,
            narrative_context=narrative_context,
            confidence_score=confidence_score,
            reconstruction_metadata=reconstruction_metadata
        )
    
    def _generate_continuation_suggestions(self, continue_context: ContinueContext,
                                          user_request: str) -> List[ContinuationSuggestion]:
        """Generate intelligent continuation suggestions"""
        
        suggestions = []
        
        # 1. Resume last active task
        if continue_context.active_files and continue_context.last_activity:
            hours_since = self._calculate_hours_since_last_activity(continue_context.last_activity)
            
            if hours_since <= 4:  # Recent activity
                suggestions.append(ContinuationSuggestion(
                    suggestion_type="resume_task",
                    description=f"Resume work on {', '.join(continue_context.active_files[:3])}",
                    priority=1,
                    context_basis="Recent file activity detected",
                    suggested_actions=[
                        f"Review changes in {continue_context.active_files[0]}" if continue_context.active_files else "Review recent changes",
                        "Continue implementation from last session",
                        "Run tests to validate current state"
                    ],
                    confidence=0.8,
                    estimated_effort_minutes=30,
                    dependencies=["file_access", "development_environment"]
                ))
        
        # 2. Address pending decisions
        if continue_context.pending_decisions:
            high_priority_decisions = [d for d in continue_context.pending_decisions if d.get("priority", 3) <= 2]
            if high_priority_decisions:
                decision = high_priority_decisions[0]
                suggestions.append(ContinuationSuggestion(
                    suggestion_type="resolve_decision",
                    description=f"Resolve pending decision: {decision.get('description', 'Unknown decision')}",
                    priority=2,
                    context_basis="High-priority pending decision identified",
                    suggested_actions=[
                        "Review decision context and options",
                        "Consider impact and trade-offs",
                        "Make decision and document rationale",
                        "Update affected code/documentation"
                    ],
                    confidence=0.7,
                    estimated_effort_minutes=45,
                    dependencies=["decision_context"]
                ))
        
        # 3. Continue implementation based on workflow state
        current_phase = continue_context.workflow_state.get("current_phase", "development")
        if current_phase == "implementation":
            suggestions.append(ContinuationSuggestion(
                suggestion_type="continue_implementation",
                description="Continue active implementation phase",
                priority=2,
                context_basis="Implementation phase detected in workflow state",
                suggested_actions=[
                    "Review implementation progress",
                    "Continue coding from last checkpoint",
                    "Add tests for new functionality",
                    "Update documentation as needed"
                ],
                confidence=0.6,
                estimated_effort_minutes=60,
                dependencies=["codebase_access"]
            ))
        
        # 4. New context suggestion if low confidence
        if continue_context.confidence_score < 0.5:
            suggestions.append(ContinuationSuggestion(
                suggestion_type="new_context",
                description="Start fresh context due to low continuation confidence",
                priority=3,
                context_basis="Low confidence in context reconstruction",
                suggested_actions=[
                    "Review recent project status",
                    "Identify current priorities",
                    "Plan next development phase",
                    "Set up fresh development context"
                ],
                confidence=0.9,
                estimated_effort_minutes=20,
                dependencies=["project_overview"]
            ))
        
        # Sort suggestions by priority
        suggestions.sort(key=lambda s: s.priority)
        
        return suggestions
    
    def _create_narrative_summary(self, continue_context: ContinueContext,
                                 temporal_analysis: Dict[str, Any]) -> str:
        """Create narrative summary of current development state"""
        
        # Use narrative context as base
        narrative_parts = [continue_context.narrative_context]
        
        # Add session summary
        work_sessions = temporal_analysis.get("work_sessions", [])
        if work_sessions:
            recent_sessions = work_sessions[-3:]  # Last 3 sessions
            session_summary = f"Recent development activity spans {len(recent_sessions)} work sessions. "
            
            if continue_context.last_activity:
                hours_since = self._calculate_hours_since_last_activity(continue_context.last_activity)
                if hours_since < 1:
                    session_summary += "Development was very recent (< 1 hour ago). "
                elif hours_since < 8:
                    session_summary += f"Last activity was {hours_since:.1f} hours ago. "
                else:
                    session_summary += f"Last development session was {hours_since:.1f} hours ago. "
            
            narrative_parts.append(session_summary)
        
        # Add file activity summary
        if continue_context.active_files:
            file_summary = f"Active development involves {len(continue_context.active_files)} files: "
            file_list = ", ".join(continue_context.active_files[:3])
            if len(continue_context.active_files) > 3:
                file_list += f" (and {len(continue_context.active_files) - 3} others)"
            file_summary += file_list + ". "
            narrative_parts.append(file_summary)
        
        # Add workflow state summary
        workflow_state = continue_context.workflow_state
        momentum = workflow_state.get("momentum_level", 0.5)
        coherence = workflow_state.get("context_coherence", 0.5)
        
        if momentum > 0.7:
            narrative_parts.append("Development momentum is high - good time to continue. ")
        elif momentum < 0.3:
            narrative_parts.append("Development momentum is low - consider planning or context review. ")
        
        if coherence > 0.7:
            narrative_parts.append("Context is coherent and ready for continuation. ")
        elif coherence < 0.3:
            narrative_parts.append("Context may need clarification before continuing. ")
        
        # Add pending decisions summary
        if continue_context.pending_decisions:
            decision_count = len(continue_context.pending_decisions)
            narrative_parts.append(f"There are {decision_count} pending decisions that may need attention. ")
        
        return "".join(narrative_parts).strip()
    
    def _determine_recommended_actions(self, suggestions: List[ContinuationSuggestion],
                                      context: ContinueContext) -> List[Dict[str, Any]]:
        """Determine top recommended actions for user"""
        
        # Take top 3 suggestions
        top_suggestions = suggestions[:3]
        
        recommended_actions = []
        for i, suggestion in enumerate(top_suggestions):
            action = {
                "rank": i + 1,
                "action": suggestion.description,
                "rationale": suggestion.context_basis,
                "estimated_effort": f"{suggestion.estimated_effort_minutes} minutes" if suggestion.estimated_effort_minutes else "Unknown",
                "confidence": f"{suggestion.confidence:.1%}",
                "next_steps": suggestion.suggested_actions[:3]  # Top 3 steps
            }
            recommended_actions.append(action)
        
        return recommended_actions
    
    def _create_next_steps_guidance(self, suggestions: List[ContinuationSuggestion],
                                   context: ContinueContext) -> Dict[str, Any]:
        """Create structured next steps guidance"""
        
        if not suggestions:
            return {
                "primary_guidance": "No specific continuation suggestions available",
                "immediate_action": "Review project status and set priorities",
                "confidence": "low"
            }
        
        primary_suggestion = suggestions[0]
        
        guidance = {
            "primary_guidance": primary_suggestion.description,
            "immediate_action": primary_suggestion.suggested_actions[0] if primary_suggestion.suggested_actions else "Begin with context review",
            "confidence": "high" if primary_suggestion.confidence > 0.7 else "medium" if primary_suggestion.confidence > 0.4 else "low",
            "estimated_duration": f"{primary_suggestion.estimated_effort_minutes} minutes" if primary_suggestion.estimated_effort_minutes else "Variable",
            "alternative_paths": [
                {
                    "description": suggestion.description,
                    "confidence": f"{suggestion.confidence:.1%}"
                }
                for suggestion in suggestions[1:3]  # Show 2 alternatives
            ]
        }
        
        return guidance
    
    # Helper methods for context analysis
    def _assess_continuation_readiness(self, temporal_analysis: Dict[str, Any]) -> float:
        """Assess readiness for workflow continuation (0.0 - 1.0)"""
        work_sessions = temporal_analysis.get("work_sessions", [])
        
        if not work_sessions:
            return 0.2  # Low readiness without session history
        
        recent_sessions = [s for s in work_sessions if self._is_recent_session(s)]
        
        # Factors for readiness
        session_recency = len(recent_sessions) / max(len(work_sessions), 1)
        session_coherence = len(work_sessions) > 1  # Multiple sessions show coherent work
        activity_diversity = len(set(s.get("primary_activity", "") for s in work_sessions)) > 1
        
        readiness = (session_recency * 0.5 + session_coherence * 0.3 + activity_diversity * 0.2)
        return min(1.0, readiness)
    
    def _calculate_workflow_momentum(self, temporal_analysis: Dict[str, Any]) -> float:
        """Calculate current workflow momentum (0.0 - 1.0)"""
        work_sessions = temporal_analysis.get("work_sessions", [])
        
        if not work_sessions:
            return 0.0
        
        # Recent activity boosts momentum
        recent_sessions = [s for s in work_sessions if self._is_recent_session(s)]
        recency_factor = len(recent_sessions) / len(work_sessions)
        
        # Session frequency
        if len(work_sessions) >= 2:
            session_frequency = 1.0 / max(self._average_session_gap_hours(work_sessions), 1)
            frequency_factor = min(1.0, session_frequency / 8)  # 8 hours = good frequency
        else:
            frequency_factor = 0.5
        
        momentum = (recency_factor * 0.6 + frequency_factor * 0.4)
        return min(1.0, momentum)
    
    def _evaluate_context_coherence(self, context_data: List[ContextElement]) -> float:
        """Evaluate coherence of context data (0.0 - 1.0)"""
        if not context_data:
            return 0.0
        
        # Check for consistent file/entity patterns
        all_entities = []
        for elem in context_data:
            all_entities.extend(elem.entities)
        
        if not all_entities:
            return 0.3  # Minimal coherence without entities
        
        # Entity repetition indicates coherent work
        entity_counts = {}
        for entity in all_entities:
            entity_counts[entity] = entity_counts.get(entity, 0) + 1
        
        repeated_entities = sum(1 for count in entity_counts.values() if count > 1)
        coherence = repeated_entities / max(len(entity_counts), 1)
        
        return min(1.0, coherence)
    
    def _identify_decision_points(self, context_data: List[ContextElement]) -> List[Dict[str, Any]]:
        """Identify decision points from context data"""
        decision_points = []
        
        # Look for decision-indicating patterns in content
        decision_keywords = [
            "should we", "need to decide", "options are", "choice between",
            "TODO", "FIXME", "consider", "alternative"
        ]
        
        for elem in context_data:
            content_lower = elem.content.lower()
            for keyword in decision_keywords:
                if keyword in content_lower:
                    decision_points.append({
                        "description": elem.content[:100] + "..." if len(elem.content) > 100 else elem.content,
                        "timestamp": elem.timestamp.isoformat(),
                        "source": elem.source_type,
                        "entities": elem.entities,
                        "priority": 2,  # Medium priority by default
                        "keyword_match": keyword
                    })
                    break  # One decision per context element
        
        return decision_points
    
    def _infer_current_phase(self, temporal_analysis: Dict[str, Any]) -> str:
        """Infer current development phase from temporal analysis"""
        work_sessions = temporal_analysis.get("work_sessions", [])
        
        if not work_sessions:
            return "planning"
        
        recent_session = work_sessions[-1]
        primary_activity = recent_session.get("primary_activity", "development")
        
        # Map activities to phases
        activity_to_phase = {
            "coding": "implementation",
            "testing": "testing",
            "debugging": "debugging",
            "planning": "planning",
            "documentation": "documentation",
            "development": "implementation"
        }
        
        return activity_to_phase.get(primary_activity, "development")
    
    def _calculate_hours_since_last_activity(self, last_activity: Optional[datetime]) -> float:
        """Calculate hours since last activity"""
        if not last_activity:
            return float('inf')
        
        return (datetime.now() - last_activity).total_seconds() / 3600
    
    def _calculate_context_confidence(self, temporal_analysis: Dict[str, Any],
                                     active_files_count: int,
                                     pending_decisions_count: int) -> float:
        """Calculate confidence in context reconstruction"""
        
        # Base confidence from temporal analysis quality
        work_sessions = temporal_analysis.get("work_sessions", [])
        base_confidence = 0.3 if work_sessions else 0.1
        
        # Boost confidence with more data
        if active_files_count > 0:
            base_confidence += 0.2
        
        if len(work_sessions) > 1:
            base_confidence += 0.2
        
        # Recent activity boosts confidence
        continuation_readiness = temporal_analysis.get("continuation_readiness", 0.0)
        base_confidence += continuation_readiness * 0.3
        
        return min(1.0, base_confidence)
    
    def _is_recent_session(self, session: Dict[str, Any], hours_threshold: int = 24) -> bool:
        """Check if session is recent within threshold"""
        end_time_str = session.get("end_time", "")
        if not end_time_str:
            return False
        
        try:
            end_time = datetime.fromisoformat(end_time_str)
            return (datetime.now() - end_time).total_seconds() / 3600 <= hours_threshold
        except:
            return False
    
    def _average_session_gap_hours(self, work_sessions: List[Dict[str, Any]]) -> float:
        """Calculate average gap between sessions in hours"""
        if len(work_sessions) < 2:
            return 24.0  # Default
        
        gaps = []
        for i in range(1, len(work_sessions)):
            prev_end = work_sessions[i-1].get("end_time", "")
            curr_start = work_sessions[i].get("start_time", "")
            
            if prev_end and curr_start:
                try:
                    prev_time = datetime.fromisoformat(prev_end)
                    curr_time = datetime.fromisoformat(curr_start)
                    gap_hours = (curr_time - prev_time).total_seconds() / 3600
                    gaps.append(gap_hours)
                except:
                    continue
        
        return sum(gaps) / len(gaps) if gaps else 24.0
    
    def _generate_context_narrative(self, temporal_analysis: Dict[str, Any],
                                    context_hints: Dict[str, Any]) -> str:
        """Generate narrative description of current context"""
        
        narrative_parts = []
        
        # Base narrative from temporal analysis
        work_sessions = temporal_analysis.get("work_sessions", [])
        if work_sessions:
            narrative_parts.append(f"Development work has progressed through {len(work_sessions)} distinct sessions. ")
            
            recent_session = work_sessions[-1]
            activity = recent_session.get("primary_activity", "development")
            narrative_parts.append(f"The most recent session focused on {activity}. ")
        
        # Add context hints if provided
        if context_hints:
            hint_text = context_hints.get("user_intent", "")
            if hint_text:
                narrative_parts.append(f"User context: {hint_text}. ")
        
        # Default context if no specific narrative
        if not narrative_parts:
            narrative_parts.append("Development context is being reconstructed from available data. ")
        
        return "".join(narrative_parts)
    
    def _update_context_cache(self, continue_result: Dict[str, Any]):
        """Update context cache for performance optimization"""
        self._context_cache = {
            "result": continue_result,
            "timestamp": datetime.now(),
            "version": "track_b_phase_4"
        }
        self._last_analysis_time = datetime.now()


# Convenience function for executing continue command
def execute_enhanced_continue(user_request: str = "continue", 
                            context_hints: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Convenience function to execute enhanced continue command.
    
    Args:
        user_request: User's continue request
        context_hints: Optional context hints for continuation
        
    Returns:
        Comprehensive continue command result
    """
    continue_system = EnhancedContinueCommand()
    return continue_system.execute_continue_command(user_request, context_hints)


if __name__ == "__main__":
    # Test enhanced continue command functionality
    print("Testing Enhanced Continue Command (Track B Phase 4)...")
    
    result = execute_enhanced_continue("continue with implementation")
    
    print(f"\\nContinue Command Result:")
    print(f"Execution Time: {result['continue_command_result']['execution_time_ms']:.1f}ms")
    print(f"Confidence Score: {result['current_context']['confidence_score']:.2f}")
    print(f"Active Files: {len(result['current_context']['active_files'])}")
    print(f"Continuation Suggestions: {len(result['continuation_suggestions'])}")
    print(f"\\nPrimary Recommendation: {result['next_steps_guidance']['primary_guidance']}")