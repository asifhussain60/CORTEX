"""
CORTEX 3.0 Track B: Pattern Detector
====================================

Advanced pattern detection system that learns from development workflows
and identifies recurring patterns, anti-patterns, and optimization opportunities.

Key Features:
- Workflow pattern recognition
- Code pattern analysis
- Performance bottleneck detection
- Development habit analysis
- Adaptive pattern learning

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import logging
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass
from enum import Enum


class PatternType(Enum):
    """Types of patterns that can be detected."""
    WORKFLOW = "workflow"
    CODE = "code"
    PERFORMANCE = "performance"
    ARCHITECTURAL = "architectural"
    BEHAVIORAL = "behavioral"
    TEMPORAL = "temporal"


class PatternConfidence(Enum):
    """Confidence levels for pattern detection."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class DetectedPattern:
    """Represents a detected development pattern."""
    pattern_id: str
    pattern_type: PatternType
    confidence: PatternConfidence
    name: str
    description: str
    frequency: int
    first_seen: datetime
    last_seen: datetime
    examples: List[Dict[str, Any]]
    impact_analysis: Dict[str, Any]
    suggestions: List[str]
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class PatternContext:
    """Context information for pattern analysis."""
    time_window: timedelta
    file_types: Set[str]
    directories: Set[str]
    authors: Set[str]
    event_types: Set[str]


class PatternDetector:
    """
    Advanced pattern detection system for CORTEX Track B
    
    Analyzes development activity to identify patterns, anti-patterns,
    and opportunities for optimization and improvement.
    """
    
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.logger = logging.getLogger("cortex.track_b.pattern_detector")
        
        # Pattern storage
        self.detected_patterns: Dict[str, DetectedPattern] = {}
        self.pattern_cache = PatternCache()
        
        # Event history for analysis
        self.event_history: List[Dict[str, Any]] = []
        self.max_history_size = 10000
        
        # Pattern analysis rules
        self.pattern_rules = self._initialize_pattern_rules()
        
        # Learning parameters
        self.min_frequency_threshold = 3
        self.min_confidence_threshold = 0.6
        self.pattern_decay_days = 30
    
    def _initialize_pattern_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize pattern detection rules."""
        return {
            'frequent_file_editing': {
                'type': PatternType.WORKFLOW,
                'description': 'Files that are edited frequently',
                'min_frequency': 5,
                'time_window': timedelta(days=7),
                'impact': 'maintenance_hotspot'
            },
            'large_commit_pattern': {
                'type': PatternType.WORKFLOW,
                'description': 'Pattern of making large commits',
                'threshold': 20,  # files per commit
                'impact': 'review_difficulty'
            },
            'test_skip_pattern': {
                'type': PatternType.BEHAVIORAL,
                'description': 'Pattern of skipping tests',
                'keywords': ['skip', 'ignore', 'disable'],
                'impact': 'quality_risk'
            },
            'import_chaos': {
                'type': PatternType.CODE,
                'description': 'Inconsistent import organization',
                'file_types': {'.py', '.js', '.ts'},
                'impact': 'maintainability'
            },
            'performance_pattern': {
                'type': PatternType.PERFORMANCE,
                'description': 'Patterns indicating performance issues',
                'keywords': ['slow', 'timeout', 'memory', 'cpu'],
                'impact': 'performance_degradation'
            },
            'architecture_violation': {
                'type': PatternType.ARCHITECTURAL,
                'description': 'Violations of architectural patterns',
                'anti_patterns': ['circular_imports', 'tight_coupling'],
                'impact': 'technical_debt'
            },
            'late_night_coding': {
                'type': PatternType.TEMPORAL,
                'description': 'Pattern of coding late at night',
                'time_range': (22, 6),  # 10 PM to 6 AM
                'impact': 'code_quality_risk'
            },
            'quick_fix_pattern': {
                'type': PatternType.BEHAVIORAL,
                'description': 'Pattern of making quick fixes without proper testing',
                'keywords': ['quick', 'fix', 'hotfix', 'temp'],
                'impact': 'technical_debt'
            },
            'copy_paste_pattern': {
                'type': PatternType.CODE,
                'description': 'Code duplication patterns',
                'similarity_threshold': 0.8,
                'impact': 'maintainability'
            },
            'dependency_bloat': {
                'type': PatternType.ARCHITECTURAL,
                'description': 'Pattern of adding too many dependencies',
                'files': ['package.json', 'requirements.txt', 'Cargo.toml'],
                'impact': 'complexity_increase'
            }
        }
    
    def add_event(self, event: Dict[str, Any]):
        """Add a development event for pattern analysis."""
        try:
            # Ensure event has required fields
            if 'timestamp' not in event:
                event['timestamp'] = datetime.now().isoformat()
            if 'event_id' not in event:
                event['event_id'] = f"evt_{len(self.event_history)}"
            
            self.event_history.append(event)
            
            # Limit history size
            if len(self.event_history) > self.max_history_size:
                self.event_history = self.event_history[-self.max_history_size:]
            
            # Trigger incremental pattern analysis
            self._analyze_recent_patterns()
            
        except Exception as e:
            self.logger.error(f"Error adding event: {e}")
    
    def analyze_patterns(self, context: Optional[PatternContext] = None) -> List[DetectedPattern]:
        """Perform comprehensive pattern analysis."""
        try:
            self.logger.info("Starting comprehensive pattern analysis")
            
            if not self.event_history:
                self.logger.warning("No events available for pattern analysis")
                return []
            
            # Apply each pattern rule
            new_patterns = []
            
            for rule_name, rule_config in self.pattern_rules.items():
                patterns = self._apply_pattern_rule(rule_name, rule_config, context)
                new_patterns.extend(patterns)
            
            # Update detected patterns
            for pattern in new_patterns:
                self.detected_patterns[pattern.pattern_id] = pattern
            
            # Clean up old patterns
            self._cleanup_old_patterns()
            
            # Return all current patterns
            patterns = list(self.detected_patterns.values())
            
            self.logger.info(f"Pattern analysis complete. Found {len(patterns)} patterns.")
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error in pattern analysis: {e}")
            return []
    
    def _analyze_recent_patterns(self):
        """Analyze patterns in recent events only."""
        try:
            # Only analyze last 100 events for performance
            recent_events = self.event_history[-100:]
            
            if len(recent_events) < 5:
                return
            
            # Quick pattern checks on recent events
            self._check_frequent_file_pattern(recent_events)
            self._check_temporal_patterns(recent_events)
            
        except Exception as e:
            self.logger.error(f"Error in recent pattern analysis: {e}")
    
    def _apply_pattern_rule(self, rule_name: str, rule_config: Dict[str, Any], context: Optional[PatternContext]) -> List[DetectedPattern]:
        """Apply a specific pattern rule to the event history."""
        patterns = []
        
        try:
            pattern_type = rule_config['type']
            
            if rule_name == 'frequent_file_editing':
                patterns.extend(self._detect_frequent_file_editing(rule_config))
            elif rule_name == 'large_commit_pattern':
                patterns.extend(self._detect_large_commit_pattern(rule_config))
            elif rule_name == 'test_skip_pattern':
                patterns.extend(self._detect_test_skip_pattern(rule_config))
            elif rule_name == 'import_chaos':
                patterns.extend(self._detect_import_chaos(rule_config))
            elif rule_name == 'performance_pattern':
                patterns.extend(self._detect_performance_pattern(rule_config))
            elif rule_name == 'late_night_coding':
                patterns.extend(self._detect_late_night_coding(rule_config))
            elif rule_name == 'quick_fix_pattern':
                patterns.extend(self._detect_quick_fix_pattern(rule_config))
            elif rule_name == 'copy_paste_pattern':
                patterns.extend(self._detect_copy_paste_pattern(rule_config))
            elif rule_name == 'dependency_bloat':
                patterns.extend(self._detect_dependency_bloat(rule_config))
                
        except Exception as e:
            self.logger.error(f"Error applying pattern rule {rule_name}: {e}")
        
        return patterns
    
    def _detect_frequent_file_editing(self, rule_config: Dict[str, Any]) -> List[DetectedPattern]:
        """Detect files that are edited frequently."""
        patterns = []
        
        try:
            time_window = rule_config.get('time_window', timedelta(days=7))
            min_frequency = rule_config.get('min_frequency', 5)
            
            cutoff_time = datetime.now() - time_window
            
            # Count file edit frequency
            file_edit_counts = Counter()
            
            for event in self.event_history:
                event_time = datetime.fromisoformat(event['timestamp'])
                if event_time < cutoff_time:
                    continue
                
                if event.get('type') == 'file_change' and event.get('change_type') == 'modified':
                    file_path = event.get('file_path', '')
                    if file_path:
                        file_edit_counts[file_path] += 1
            
            # Find files edited more than threshold
            for file_path, count in file_edit_counts.items():
                if count >= min_frequency:
                    pattern_id = f"frequent_edit_{hash(file_path)}"
                    
                    # Get examples
                    examples = [
                        event for event in self.event_history[-50:]
                        if event.get('file_path') == file_path and event.get('type') == 'file_change'
                    ][:3]
                    
                    pattern = DetectedPattern(
                        pattern_id=pattern_id,
                        pattern_type=PatternType.WORKFLOW,
                        confidence=self._calculate_confidence(count, min_frequency),
                        name=f"Frequent File Editing: {Path(file_path).name}",
                        description=f"File '{Path(file_path).name}' has been edited {count} times in {time_window.days} days",
                        frequency=count,
                        first_seen=datetime.now() - time_window,
                        last_seen=datetime.now(),
                        examples=examples,
                        impact_analysis={
                            'type': rule_config.get('impact', 'maintenance_hotspot'),
                            'severity': 'high' if count > min_frequency * 2 else 'medium',
                            'affected_files': [file_path]
                        },
                        suggestions=[
                            "Consider refactoring this file if it's changed frequently",
                            "Check if the file has too many responsibilities",
                            "Review if changes indicate design issues"
                        ],
                        tags=['hotspot', 'maintenance']
                    )
                    
                    patterns.append(pattern)
                    
        except Exception as e:
            self.logger.error(f"Error detecting frequent file editing: {e}")
        
        return patterns
    
    def _detect_large_commit_pattern(self, rule_config: Dict[str, Any]) -> List[DetectedPattern]:
        """Detect pattern of making large commits."""
        patterns = []
        
        try:
            threshold = rule_config.get('threshold', 20)
            
            large_commits = []
            for event in self.event_history:
                if event.get('type') == 'git_operation' and event.get('event_type') == 'commit':
                    files_changed = len(event.get('files_changed', []))
                    if files_changed >= threshold:
                        large_commits.append(event)
            
            if len(large_commits) >= self.min_frequency_threshold:
                pattern_id = "large_commit_pattern"
                
                avg_files = sum(len(commit.get('files_changed', [])) for commit in large_commits) / len(large_commits)
                
                pattern = DetectedPattern(
                    pattern_id=pattern_id,
                    pattern_type=PatternType.WORKFLOW,
                    confidence=self._calculate_confidence(len(large_commits), self.min_frequency_threshold),
                    name="Large Commit Pattern",
                    description=f"Pattern of making large commits detected ({len(large_commits)} commits, avg {avg_files:.1f} files)",
                    frequency=len(large_commits),
                    first_seen=datetime.fromisoformat(large_commits[-1]['timestamp']),
                    last_seen=datetime.fromisoformat(large_commits[0]['timestamp']),
                    examples=large_commits[:3],
                    impact_analysis={
                        'type': rule_config.get('impact', 'review_difficulty'),
                        'severity': 'high',
                        'average_files_per_commit': avg_files
                    },
                    suggestions=[
                        "Break large changes into smaller, focused commits",
                        "Use feature branches for complex changes",
                        "Commit logical units of work separately"
                    ],
                    tags=['commits', 'workflow', 'review']
                )
                
                patterns.append(pattern)
                
        except Exception as e:
            self.logger.error(f"Error detecting large commit pattern: {e}")
        
        return patterns
    
    def _detect_late_night_coding(self, rule_config: Dict[str, Any]) -> List[DetectedPattern]:
        """Detect pattern of coding late at night."""
        patterns = []
        
        try:
            time_range = rule_config.get('time_range', (22, 6))
            start_hour, end_hour = time_range
            
            late_night_events = []
            
            for event in self.event_history:
                event_time = datetime.fromisoformat(event['timestamp'])
                hour = event_time.hour
                
                # Check if event occurred during late night hours
                if start_hour <= hour <= 23 or 0 <= hour <= end_hour:
                    late_night_events.append(event)
            
            if len(late_night_events) >= self.min_frequency_threshold:
                pattern_id = "late_night_coding"
                
                # Calculate percentage of late night activity
                total_events = len([e for e in self.event_history if e.get('type') in ['file_change', 'git_operation']])
                late_night_percentage = (len(late_night_events) / total_events * 100) if total_events > 0 else 0
                
                pattern = DetectedPattern(
                    pattern_id=pattern_id,
                    pattern_type=PatternType.TEMPORAL,
                    confidence=self._calculate_confidence(len(late_night_events), self.min_frequency_threshold),
                    name="Late Night Coding Pattern",
                    description=f"{late_night_percentage:.1f}% of coding activity occurs between {start_hour}:00 and {end_hour}:00",
                    frequency=len(late_night_events),
                    first_seen=datetime.fromisoformat(late_night_events[-1]['timestamp']),
                    last_seen=datetime.fromisoformat(late_night_events[0]['timestamp']),
                    examples=late_night_events[:3],
                    impact_analysis={
                        'type': rule_config.get('impact', 'code_quality_risk'),
                        'severity': 'medium' if late_night_percentage > 20 else 'low',
                        'percentage': late_night_percentage
                    },
                    suggestions=[
                        "Consider adjusting work schedule for better code quality",
                        "Review late-night commits for potential issues",
                        "Use extra care when coding during late hours"
                    ],
                    tags=['timing', 'productivity', 'quality']
                )
                
                patterns.append(pattern)
                
        except Exception as e:
            self.logger.error(f"Error detecting late night coding: {e}")
        
        return patterns
    
    def _check_frequent_file_pattern(self, events: List[Dict[str, Any]]):
        """Quick check for frequent file editing patterns in recent events."""
        try:
            # Count file modifications in recent events
            file_counts = Counter()
            
            for event in events:
                if event.get('type') == 'file_change' and event.get('change_type') == 'modified':
                    file_path = event.get('file_path', '')
                    if file_path:
                        file_counts[file_path] += 1
            
            # Update pattern cache
            for file_path, count in file_counts.items():
                self.pattern_cache.update_file_frequency(file_path, count)
                
        except Exception as e:
            self.logger.error(f"Error checking frequent file pattern: {e}")
    
    def _check_temporal_patterns(self, events: List[Dict[str, Any]]):
        """Quick check for temporal patterns in recent events."""
        try:
            current_hour = datetime.now().hour
            
            if 22 <= current_hour <= 23 or 0 <= current_hour <= 6:
                # Late night activity detected
                self.pattern_cache.increment_late_night_activity()
                
        except Exception as e:
            self.logger.error(f"Error checking temporal patterns: {e}")
    
    def _detect_test_skip_pattern(self, rule_config: Dict[str, Any]) -> List[DetectedPattern]:
        """Detect pattern of skipping tests.""" 
        patterns = []
        # Implementation would analyze commit messages and code changes for test-skipping patterns
        return patterns
    
    def _detect_import_chaos(self, rule_config: Dict[str, Any]) -> List[DetectedPattern]:
        """Detect inconsistent import organization."""
        patterns = []
        # Implementation would analyze import statements across files
        return patterns
    
    def _detect_performance_pattern(self, rule_config: Dict[str, Any]) -> List[DetectedPattern]:
        """Detect patterns indicating performance issues."""
        patterns = []
        # Implementation would analyze commit messages and file changes for performance keywords
        return patterns
    
    def _detect_quick_fix_pattern(self, rule_config: Dict[str, Any]) -> List[DetectedPattern]:
        """Detect pattern of making quick fixes without proper testing."""
        patterns = []
        # Implementation would analyze commit messages for quick fix keywords
        return patterns
    
    def _detect_copy_paste_pattern(self, rule_config: Dict[str, Any]) -> List[DetectedPattern]:
        """Detect code duplication patterns."""
        patterns = []
        # Implementation would analyze code similarity across files
        return patterns
    
    def _detect_dependency_bloat(self, rule_config: Dict[str, Any]) -> List[DetectedPattern]:
        """Detect pattern of adding too many dependencies."""
        patterns = []
        # Implementation would track dependency file changes
        return patterns
    
    def _calculate_confidence(self, frequency: int, threshold: int) -> PatternConfidence:
        """Calculate confidence level based on frequency."""
        ratio = frequency / threshold
        
        if ratio >= 3.0:
            return PatternConfidence.VERY_HIGH
        elif ratio >= 2.0:
            return PatternConfidence.HIGH
        elif ratio >= 1.5:
            return PatternConfidence.MEDIUM
        else:
            return PatternConfidence.LOW
    
    def _cleanup_old_patterns(self):
        """Remove patterns that haven't been seen recently."""
        try:
            cutoff_time = datetime.now() - timedelta(days=self.pattern_decay_days)
            
            patterns_to_remove = [
                pattern_id for pattern_id, pattern in self.detected_patterns.items()
                if pattern.last_seen < cutoff_time
            ]
            
            for pattern_id in patterns_to_remove:
                del self.detected_patterns[pattern_id]
                
            if patterns_to_remove:
                self.logger.debug(f"Cleaned up {len(patterns_to_remove)} old patterns")
                
        except Exception as e:
            self.logger.error(f"Error cleaning up old patterns: {e}")
    
    def get_patterns_by_type(self, pattern_type: PatternType) -> List[DetectedPattern]:
        """Get patterns filtered by type."""
        return [p for p in self.detected_patterns.values() if p.pattern_type == pattern_type]
    
    def get_high_impact_patterns(self) -> List[DetectedPattern]:
        """Get patterns with high impact on development."""
        high_impact = []
        
        for pattern in self.detected_patterns.values():
            impact = pattern.impact_analysis.get('severity', 'low')
            if impact in ['high', 'critical']:
                high_impact.append(pattern)
        
        return sorted(high_impact, key=lambda p: p.frequency, reverse=True)
    
    def export_patterns(self) -> Dict[str, Any]:
        """Export patterns for analysis or storage."""
        return {
            'patterns': [
                {
                    'pattern_id': p.pattern_id,
                    'type': p.pattern_type.value,
                    'confidence': p.confidence.value,
                    'name': p.name,
                    'description': p.description,
                    'frequency': p.frequency,
                    'first_seen': p.first_seen.isoformat(),
                    'last_seen': p.last_seen.isoformat(),
                    'impact_analysis': p.impact_analysis,
                    'suggestions': p.suggestions,
                    'tags': p.tags
                }
                for p in self.detected_patterns.values()
            ],
            'export_timestamp': datetime.now().isoformat(),
            'total_events_analyzed': len(self.event_history)
        }


class PatternCache:
    """Cache for pattern analysis to improve performance."""
    
    def __init__(self):
        self.file_frequencies: Dict[str, int] = defaultdict(int)
        self.late_night_count = 0
        self.last_reset = datetime.now()
        self.reset_interval = timedelta(hours=24)
    
    def update_file_frequency(self, file_path: str, count: int):
        """Update file modification frequency."""
        self.file_frequencies[file_path] += count
        self._check_reset()
    
    def increment_late_night_activity(self):
        """Increment late night activity counter."""
        self.late_night_count += 1
        self._check_reset()
    
    def _check_reset(self):
        """Reset cache if interval has passed."""
        if datetime.now() - self.last_reset > self.reset_interval:
            self.file_frequencies.clear()
            self.late_night_count = 0
            self.last_reset = datetime.now()