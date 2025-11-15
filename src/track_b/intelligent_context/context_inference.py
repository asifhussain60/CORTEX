"""
CORTEX 3.0 Track B: Context Inference Engine
============================================

Advanced context inference system that builds understanding of development
context from multiple sources and provides intelligent insights.

Key Features:
- Multi-source context fusion
- Semantic understanding of development activity
- Intent prediction and recommendation
- Contextual memory and learning
- Integration with CORTEX brain tiers

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import logging
import json
from collections import defaultdict, deque
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum


class ContextType(Enum):
    """Types of development context."""
    CURRENT_TASK = "current_task"
    PROJECT_STATE = "project_state"
    DEVELOPMENT_FOCUS = "development_focus"
    WORKFLOW_STATE = "workflow_state"
    TECHNICAL_CONTEXT = "technical_context"
    TEMPORAL_CONTEXT = "temporal_context"


class ConfidenceLevel(Enum):
    """Confidence levels for context inference."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class ContextSignal:
    """Individual signal contributing to context inference."""
    source: str  # 'file_change', 'git_commit', 'terminal_command'
    signal_type: str
    content: str
    timestamp: datetime
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InferredContext:
    """Represents inferred development context."""
    context_id: str
    context_type: ContextType
    confidence: ConfidenceLevel
    title: str
    description: str
    evidence_signals: List[ContextSignal]
    inferred_at: datetime
    expires_at: Optional[datetime]
    related_files: List[Path]
    related_concepts: List[str]
    predictions: List[Dict[str, Any]]
    recommendations: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class DevelopmentSession:
    """Represents a development session context."""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    primary_focus: str
    files_worked_on: Set[Path]
    commands_executed: List[str]
    commits_made: List[Dict[str, Any]]
    context_switches: int
    productivity_score: float


class ContextInference:
    """
    Context inference engine for CORTEX Track B
    
    Analyzes multiple streams of development activity to infer
    current context, predict next actions, and provide recommendations.
    """
    
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.logger = logging.getLogger("cortex.track_b.context_inference")
        
        # Context storage
        self.active_contexts: Dict[str, InferredContext] = {}
        self.context_history: List[InferredContext] = []
        
        # Signal processing
        self.signal_queue: deque = deque(maxlen=1000)
        self.signal_processors = self._initialize_signal_processors()
        
        # Session tracking
        self.current_session: Optional[DevelopmentSession] = None
        self.session_history: List[DevelopmentSession] = []
        
        # Context patterns and learning
        self.context_patterns: Dict[str, Dict[str, Any]] = {}
        self.concept_graph: Dict[str, Set[str]] = defaultdict(set)
        
        # Configuration
        self.signal_weights = self._initialize_signal_weights()
        self.context_timeout = timedelta(minutes=30)
        self.session_timeout = timedelta(minutes=15)
    
    def _initialize_signal_processors(self) -> Dict[str, callable]:
        """Initialize signal processing functions."""
        return {
            'file_change': self._process_file_change_signal,
            'git_operation': self._process_git_signal,
            'terminal_command': self._process_terminal_signal,
        }
    
    def _initialize_signal_weights(self) -> Dict[str, float]:
        """Initialize weights for different signal types."""
        return {
            'file_change': 1.0,
            'git_commit': 2.0,
            'terminal_build': 1.5,
            'terminal_test': 1.5,
            'terminal_debug': 2.0,
            'file_create': 1.2,
            'file_delete': 1.2,
            'import_change': 0.8,
            'function_add': 1.3,
            'function_modify': 1.1,
            'class_add': 1.4,
        }
    
    def add_signal(self, signal: ContextSignal):
        """Add a new context signal for processing."""
        try:
            self.signal_queue.append(signal)
            
            # Process signal immediately
            self._process_signal(signal)
            
            # Update session tracking
            self._update_current_session(signal)
            
            # Trigger context inference
            self._infer_current_context()
            
        except Exception as e:
            self.logger.error(f"Error adding context signal: {e}")
    
    def _process_signal(self, signal: ContextSignal):
        """Process a context signal and extract meaning."""
        try:
            processor = self.signal_processors.get(signal.source)
            if processor:
                processor(signal)
            else:
                self.logger.warning(f"No processor for signal source: {signal.source}")
        except Exception as e:
            self.logger.error(f"Error processing signal: {e}")
    
    def _process_file_change_signal(self, signal: ContextSignal):
        """Process file change signals."""
        try:
            # Extract file information
            file_path = signal.metadata.get('file_path')
            change_type = signal.metadata.get('change_type', 'modified')
            
            if not file_path:
                return
            
            file_path = Path(file_path)
            
            # Update concept graph
            self._update_concept_graph_from_file(file_path, signal)
            
            # Determine signal importance
            if change_type in ['created', 'deleted']:
                signal.weight *= 1.2
            
            # Check for architectural significance
            if self._is_architecturally_significant_file(file_path):
                signal.weight *= 1.5
                
            # Update signal metadata
            signal.metadata.update({
                'file_extension': file_path.suffix,
                'file_name': file_path.name,
                'relative_path': str(file_path.relative_to(self.workspace_path))
            })
            
        except Exception as e:
            self.logger.error(f"Error processing file change signal: {e}")
    
    def _process_git_signal(self, signal: ContextSignal):
        """Process git operation signals."""
        try:
            operation = signal.metadata.get('event_type', 'unknown')
            
            if operation == 'commit':
                # Analyze commit message for intent
                message = signal.metadata.get('message', '')
                intent = self._analyze_commit_intent(message)
                signal.metadata['inferred_intent'] = intent
                
                # Weight based on commit size
                files_changed = len(signal.metadata.get('files_changed', []))
                if files_changed > 10:
                    signal.weight *= 1.3  # Large commits are significant
                elif files_changed == 1:
                    signal.weight *= 0.9  # Small commits are less significant
            
            elif operation in ['merge', 'rebase']:
                signal.weight *= 2.0  # Integration operations are very significant
                
        except Exception as e:
            self.logger.error(f"Error processing git signal: {e}")
    
    def _process_terminal_signal(self, signal: ContextSignal):
        """Process terminal command signals."""
        try:
            command = signal.content
            command_type = signal.metadata.get('command_type', 'other')
            
            # Analyze command intent
            intent = self._analyze_command_intent(command, command_type)
            signal.metadata['inferred_intent'] = intent
            
            # Weight based on command type
            type_weights = {
                'build': 1.5,
                'test': 1.5,
                'git': 1.2,
                'file': 0.8,
                'package': 1.3,
                'other': 1.0
            }
            
            signal.weight *= type_weights.get(command_type, 1.0)
            
            # Check for error conditions
            exit_code = signal.metadata.get('exit_code')
            if exit_code and exit_code != 0:
                signal.weight *= 1.4  # Failed commands are more significant
                signal.metadata['is_error'] = True
                
        except Exception as e:
            self.logger.error(f"Error processing terminal signal: {e}")
    
    def _update_concept_graph_from_file(self, file_path: Path, signal: ContextSignal):
        """Update concept graph based on file changes."""
        try:
            # Extract concepts from file path
            concepts = set()
            
            # File name concepts
            file_stem = file_path.stem.lower()
            concepts.add(file_stem)
            
            # Directory concepts
            for part in file_path.parts[:-1]:  # Exclude filename
                if part not in ['.', '..', 'src', 'lib', 'tests']:
                    concepts.add(part.lower())
            
            # Programming language concept
            if file_path.suffix:
                concepts.add(f"language:{file_path.suffix[1:]}")
            
            # Connect concepts in the graph
            for concept in concepts:
                for other_concept in concepts:
                    if concept != other_concept:
                        self.concept_graph[concept].add(other_concept)
                        
        except Exception as e:
            self.logger.error(f"Error updating concept graph: {e}")
    
    def _analyze_commit_intent(self, commit_message: str) -> str:
        """Analyze commit message to infer intent."""
        message_lower = commit_message.lower()
        
        intent_patterns = {
            'feature': ['add', 'implement', 'create', 'new', 'feature'],
            'fix': ['fix', 'bug', 'issue', 'resolve', 'correct'],
            'refactor': ['refactor', 'restructure', 'reorganize', 'clean'],
            'update': ['update', 'upgrade', 'modify', 'change'],
            'documentation': ['doc', 'readme', 'comment', 'documentation'],
            'test': ['test', 'testing', 'spec', 'coverage'],
            'performance': ['performance', 'optimize', 'speed', 'efficient'],
            'security': ['security', 'auth', 'permission', 'encrypt']
        }
        
        for intent, keywords in intent_patterns.items():
            if any(keyword in message_lower for keyword in keywords):
                return intent
        
        return 'maintenance'
    
    def _analyze_command_intent(self, command: str, command_type: str) -> str:
        """Analyze command to infer developer intent."""
        command_lower = command.lower()
        
        if command_type == 'test':
            if 'debug' in command_lower or 'verbose' in command_lower:
                return 'debugging'
            elif 'coverage' in command_lower:
                return 'quality_assurance'
            else:
                return 'validation'
        elif command_type == 'build':
            if 'clean' in command_lower:
                return 'maintenance'
            elif 'release' in command_lower or 'prod' in command_lower:
                return 'deployment'
            else:
                return 'development'
        elif command_type == 'git':
            return 'version_control'
        elif command_type == 'package':
            return 'dependency_management'
        
        return 'exploration'
    
    def _is_architecturally_significant_file(self, file_path: Path) -> bool:
        """Check if file is architecturally significant."""
        significant_files = {
            'package.json', 'requirements.txt', 'Cargo.toml', 'pom.xml',
            'Dockerfile', 'docker-compose.yml', 'Makefile', 'CMakeLists.txt',
            'main.py', 'index.js', 'app.py', 'server.py'
        }
        
        significant_dirs = {'src', 'lib', 'core', 'api', 'services'}
        
        if file_path.name in significant_files:
            return True
        
        if any(part in significant_dirs for part in file_path.parts):
            return True
        
        return False
    
    def _update_current_session(self, signal: ContextSignal):
        """Update current development session."""
        try:
            current_time = signal.timestamp
            
            # Check if we need to start a new session
            if (self.current_session is None or 
                current_time - self.current_session.start_time > self.session_timeout):
                
                # End previous session if it exists
                if self.current_session:
                    self.current_session.end_time = current_time
                    self.session_history.append(self.current_session)
                
                # Start new session
                self.current_session = DevelopmentSession(
                    session_id=f"session_{current_time.strftime('%Y%m%d_%H%M%S')}",
                    start_time=current_time,
                    end_time=None,
                    primary_focus="unknown",
                    files_worked_on=set(),
                    commands_executed=[],
                    commits_made=[],
                    context_switches=0,
                    productivity_score=0.0
                )
            
            # Update current session
            if signal.source == 'file_change':
                file_path = signal.metadata.get('file_path')
                if file_path:
                    self.current_session.files_worked_on.add(Path(file_path))
            
            elif signal.source == 'terminal_command':
                self.current_session.commands_executed.append(signal.content)
            
            elif signal.source == 'git_operation' and signal.metadata.get('event_type') == 'commit':
                self.current_session.commits_made.append(signal.metadata)
            
            # Update primary focus based on activity
            self._update_session_focus()
            
        except Exception as e:
            self.logger.error(f"Error updating current session: {e}")
    
    def _update_session_focus(self):
        """Update the primary focus of current session."""
        if not self.current_session:
            return
        
        try:
            # Analyze recent activity to determine focus
            recent_signals = list(self.signal_queue)[-20:]  # Last 20 signals
            
            # Count activity types
            activity_counts = defaultdict(int)
            
            for signal in recent_signals:
                if signal.source == 'file_change':
                    file_path = signal.metadata.get('file_path', '')
                    if 'test' in file_path.lower():
                        activity_counts['testing'] += 1
                    elif file_path.endswith(('.py', '.js', '.java', '.cpp')):
                        activity_counts['coding'] += 1
                    elif file_path.endswith(('.md', '.txt', '.rst')):
                        activity_counts['documentation'] += 1
                
                elif signal.source == 'terminal_command':
                    command_type = signal.metadata.get('command_type', 'other')
                    if command_type == 'test':
                        activity_counts['testing'] += 2
                    elif command_type == 'build':
                        activity_counts['building'] += 2
                    elif command_type == 'git':
                        activity_counts['version_control'] += 1
            
            # Determine primary focus
            if activity_counts:
                primary_focus = max(activity_counts.items(), key=lambda x: x[1])[0]
                self.current_session.primary_focus = primary_focus
                
        except Exception as e:
            self.logger.error(f"Error updating session focus: {e}")
    
    def _infer_current_context(self):
        """Infer current development context from recent signals."""
        try:
            if not self.signal_queue:
                return
            
            # Analyze recent signals (last 10)
            recent_signals = list(self.signal_queue)[-10:]
            
            # Infer different types of context
            contexts = []
            
            # Current task context
            task_context = self._infer_current_task(recent_signals)
            if task_context:
                contexts.append(task_context)
            
            # Development focus context
            focus_context = self._infer_development_focus(recent_signals)
            if focus_context:
                contexts.append(focus_context)
            
            # Workflow state context
            workflow_context = self._infer_workflow_state(recent_signals)
            if workflow_context:
                contexts.append(workflow_context)
            
            # Update active contexts
            for context in contexts:
                self.active_contexts[context.context_id] = context
            
            # Clean up expired contexts
            self._cleanup_expired_contexts()
            
        except Exception as e:
            self.logger.error(f"Error inferring current context: {e}")
    
    def _infer_current_task(self, signals: List[ContextSignal]) -> Optional[InferredContext]:
        """Infer current task from recent activity."""
        try:
            if not signals:
                return None
            
            # Analyze file patterns and changes
            file_signals = [s for s in signals if s.source == 'file_change']
            if not file_signals:
                return None
            
            # Group by file type and changes
            files_by_type = defaultdict(list)
            for signal in file_signals:
                file_path = signal.metadata.get('file_path', '')
                if file_path:
                    ext = Path(file_path).suffix
                    files_by_type[ext].append(signal)
            
            # Determine task type
            task_type = "development"
            confidence = ConfidenceLevel.MEDIUM
            
            if '.py' in files_by_type or '.js' in files_by_type:
                if any('test' in s.metadata.get('file_path', '') for s in file_signals):
                    task_type = "testing"
                else:
                    task_type = "coding"
            elif '.md' in files_by_type or '.txt' in files_by_type:
                task_type = "documentation"
            
            # Create context
            context_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Get related files
            related_files = []
            for signal in file_signals:
                file_path = signal.metadata.get('file_path')
                if file_path:
                    related_files.append(Path(file_path))
            
            # Generate predictions
            predictions = self._generate_task_predictions(task_type, related_files)
            
            # Generate recommendations
            recommendations = self._generate_task_recommendations(task_type, signals)
            
            return InferredContext(
                context_id=context_id,
                context_type=ContextType.CURRENT_TASK,
                confidence=confidence,
                title=f"Current Task: {task_type.title()}",
                description=f"Working on {task_type} task involving {len(related_files)} files",
                evidence_signals=signals[-3:],  # Last 3 signals as evidence
                inferred_at=datetime.now(),
                expires_at=datetime.now() + self.context_timeout,
                related_files=related_files,
                related_concepts=[task_type],
                predictions=predictions,
                recommendations=recommendations,
                metadata={'task_type': task_type, 'file_count': len(related_files)}
            )
            
        except Exception as e:
            self.logger.error(f"Error inferring current task: {e}")
            return None
    
    def _infer_development_focus(self, signals: List[ContextSignal]) -> Optional[InferredContext]:
        """Infer development focus area."""
        try:
            # Analyze concepts from signals
            concepts = set()
            for signal in signals:
                file_path = signal.metadata.get('file_path', '')
                if file_path:
                    path_parts = Path(file_path).parts
                    concepts.update(part.lower() for part in path_parts if part not in ['.', '..'])
            
            if not concepts:
                return None
            
            # Find most common concepts
            concept_counts = Counter()
            for concept in concepts:
                if concept in self.concept_graph:
                    concept_counts[concept] += len(self.concept_graph[concept])
                else:
                    concept_counts[concept] += 1
            
            if not concept_counts:
                return None
            
            primary_concept = concept_counts.most_common(1)[0][0]
            
            context_id = f"focus_{primary_concept}"
            
            return InferredContext(
                context_id=context_id,
                context_type=ContextType.DEVELOPMENT_FOCUS,
                confidence=ConfidenceLevel.MEDIUM,
                title=f"Development Focus: {primary_concept.title()}",
                description=f"Current development activity centered around {primary_concept}",
                evidence_signals=signals,
                inferred_at=datetime.now(),
                expires_at=datetime.now() + self.context_timeout,
                related_files=[],
                related_concepts=list(concepts),
                predictions=[],
                recommendations=[],
                metadata={'primary_concept': primary_concept, 'concept_strength': concept_counts[primary_concept]}
            )
            
        except Exception as e:
            self.logger.error(f"Error inferring development focus: {e}")
            return None
    
    def _infer_workflow_state(self, signals: List[ContextSignal]) -> Optional[InferredContext]:
        """Infer current workflow state."""
        try:
            if not signals:
                return None
            
            # Analyze recent terminal commands and git operations
            terminal_signals = [s for s in signals if s.source == 'terminal_command']
            git_signals = [s for s in signals if s.source == 'git_operation']
            
            workflow_state = "development"
            confidence = ConfidenceLevel.LOW
            
            # Determine workflow state from commands
            if terminal_signals:
                last_command = terminal_signals[-1]
                command_type = last_command.metadata.get('command_type', 'other')
                
                if command_type == 'test':
                    workflow_state = "testing"
                    confidence = ConfidenceLevel.HIGH
                elif command_type == 'build':
                    workflow_state = "building"
                    confidence = ConfidenceLevel.HIGH
                
            # Check git operations
            if git_signals:
                last_git = git_signals[-1]
                operation = last_git.metadata.get('event_type', 'unknown')
                
                if operation == 'commit':
                    workflow_state = "committing"
                    confidence = ConfidenceLevel.HIGH
                elif operation in ['merge', 'rebase']:
                    workflow_state = "integrating"
                    confidence = ConfidenceLevel.HIGH
            
            context_id = f"workflow_{workflow_state}"
            
            return InferredContext(
                context_id=context_id,
                context_type=ContextType.WORKFLOW_STATE,
                confidence=confidence,
                title=f"Workflow State: {workflow_state.title()}",
                description=f"Currently in {workflow_state} phase of development workflow",
                evidence_signals=terminal_signals + git_signals,
                inferred_at=datetime.now(),
                expires_at=datetime.now() + timedelta(minutes=10),  # Workflow state expires quickly
                related_files=[],
                related_concepts=[workflow_state],
                predictions=[],
                recommendations=[],
                metadata={'workflow_state': workflow_state}
            )
            
        except Exception as e:
            self.logger.error(f"Error inferring workflow state: {e}")
            return None
    
    def _generate_task_predictions(self, task_type: str, related_files: List[Path]) -> List[Dict[str, Any]]:
        """Generate predictions for current task."""
        predictions = []
        
        try:
            if task_type == "coding":
                predictions.extend([
                    {
                        'type': 'next_action',
                        'description': 'Likely to run tests after code changes',
                        'probability': 0.7,
                        'suggested_action': 'Run test suite'
                    },
                    {
                        'type': 'workflow',
                        'description': 'May need to commit changes soon',
                        'probability': 0.6,
                        'suggested_action': 'Review changes for commit'
                    }
                ])
            
            elif task_type == "testing":
                predictions.extend([
                    {
                        'type': 'next_action',
                        'description': 'Likely to fix failing tests',
                        'probability': 0.8,
                        'suggested_action': 'Investigate test failures'
                    }
                ])
                
        except Exception as e:
            self.logger.error(f"Error generating task predictions: {e}")
        
        return predictions
    
    def _generate_task_recommendations(self, task_type: str, signals: List[ContextSignal]) -> List[str]:
        """Generate recommendations for current task."""
        recommendations = []
        
        try:
            if task_type == "coding":
                recommendations.extend([
                    "Consider writing tests for new functionality",
                    "Check code style and documentation",
                    "Run static analysis tools"
                ])
            
            elif task_type == "testing":
                recommendations.extend([
                    "Ensure test coverage is adequate",
                    "Consider edge cases and error conditions"
                ])
            
            elif task_type == "documentation":
                recommendations.extend([
                    "Update relevant code examples",
                    "Check for outdated information"
                ])
                
        except Exception as e:
            self.logger.error(f"Error generating task recommendations: {e}")
        
        return recommendations
    
    def _cleanup_expired_contexts(self):
        """Remove expired contexts."""
        try:
            current_time = datetime.now()
            
            expired_contexts = [
                context_id for context_id, context in self.active_contexts.items()
                if context.expires_at and context.expires_at < current_time
            ]
            
            for context_id in expired_contexts:
                context = self.active_contexts.pop(context_id)
                self.context_history.append(context)
            
            # Limit history size
            if len(self.context_history) > 100:
                self.context_history = self.context_history[-100:]
                
        except Exception as e:
            self.logger.error(f"Error cleaning up expired contexts: {e}")
    
    def get_current_context(self) -> Optional[InferredContext]:
        """Get the most relevant current context."""
        if not self.active_contexts:
            return None
        
        # Return context with highest confidence
        return max(
            self.active_contexts.values(),
            key=lambda ctx: (ctx.confidence.value, ctx.inferred_at)
        )
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get summary of current context state."""
        current_context = self.get_current_context()
        
        return {
            'current_context': {
                'title': current_context.title if current_context else None,
                'type': current_context.context_type.value if current_context else None,
                'confidence': current_context.confidence.value if current_context else None
            } if current_context else None,
            'active_contexts': len(self.active_contexts),
            'current_session': {
                'focus': self.current_session.primary_focus if self.current_session else None,
                'files_worked_on': len(self.current_session.files_worked_on) if self.current_session else 0,
                'duration_minutes': int((datetime.now() - self.current_session.start_time).total_seconds() / 60) if self.current_session else 0
            },
            'signals_processed': len(self.signal_queue),
            'concept_graph_size': len(self.concept_graph)
        }