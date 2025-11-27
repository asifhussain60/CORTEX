"""
CORTEX 3.0 - Auto-Detection & Quality Scoring (Feature 5 - Final Phase)
========================================================================

Completes Feature 5 with automatic conversation detection and intelligent quality scoring.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Feature: Feature 5 - Final Phase (Week 3)
Effort: 12 hours (auto-detection + quality scoring)
Dependencies: Existing conversation capture system
"""

import os
import sys
import json
import re
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import logging

# Add CORTEX to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


@dataclass
class ConversationQualityMetrics:
    """Quality scoring metrics for conversations"""
    length_score: float  # 0-1 based on message count/length
    depth_score: float   # 0-1 based on conversation depth/complexity
    entity_score: float  # 0-1 based on entities detected
    context_score: float # 0-1 based on technical context
    overall_score: float # 0-1 overall quality
    issues: List[str]    # Quality issues detected
    suggestions: List[str] # Improvement suggestions


class AutoDetectionEngine:
    """
    Automatic conversation detection and quality scoring.
    
    Features:
    - Real-time conversation monitoring
    - Automatic end-of-conversation detection
    - Intelligent quality scoring
    - Learning from user feedback
    - Integration with manual capture system
    """
    
    def __init__(self, brain_path: str):
        self.brain_path = Path(brain_path)
        self.logger = logging.getLogger('cortex.auto_detection')
        
        # Auto-detection settings
        self.idle_threshold_seconds = 180  # 3 minutes of inactivity
        self.min_conversation_length = 2   # Minimum 2 exchanges
        self.quality_threshold = 0.6       # Minimum quality score
        
        # Activity monitoring
        self.last_activity = None
        self.current_conversation = []
        self.monitoring_active = False
        
        # Quality scoring weights
        self.quality_weights = {
            'length': 0.25,    # Message count and length
            'depth': 0.30,     # Conversation complexity
            'entity': 0.25,    # Technical entities
            'context': 0.20    # Technical context
        }
    
    def start_monitoring(self) -> bool:
        """Start automatic conversation monitoring"""
        try:
            self.monitoring_active = True
            self.last_activity = datetime.now()
            self.current_conversation = []
            
            self.logger.info("Auto-detection monitoring started")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}")
            return False
    
    def stop_monitoring(self) -> bool:
        """Stop automatic conversation monitoring"""
        try:
            self.monitoring_active = False
            
            # Process any remaining conversation
            if self.current_conversation:
                self._process_detected_conversation()
            
            self.logger.info("Auto-detection monitoring stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop monitoring: {e}")
            return False
    
    def register_activity(self, message: str, role: str = 'user') -> Dict[str, Any]:
        """
        Register conversation activity (message sent/received).
        
        Args:
            message: Message content
            role: 'user' or 'assistant'
            
        Returns:
            Detection status and any triggered actions
        """
        try:
            if not self.monitoring_active:
                return {'monitoring': False}
            
            # Update activity timestamp
            current_time = datetime.now()
            self.last_activity = current_time
            
            # Add message to current conversation
            self.current_conversation.append({
                'role': role,
                'content': message,
                'timestamp': current_time.isoformat()
            })
            
            # Check for conversation patterns
            detection_result = self._analyze_conversation_patterns()
            
            return {
                'monitoring': True,
                'activity_registered': True,
                'message_count': len(self.current_conversation),
                'patterns': detection_result
            }
            
        except Exception as e:
            self.logger.error(f"Failed to register activity: {e}")
            return {'error': str(e)}
    
    def check_idle_detection(self) -> Optional[Dict[str, Any]]:
        """
        Check if conversation should be automatically captured due to inactivity.
        
        Returns:
            Capture recommendation if conversation detected
        """
        try:
            if not self.monitoring_active or not self.last_activity:
                return None
            
            # Calculate idle time
            idle_seconds = (datetime.now() - self.last_activity).total_seconds()
            
            if idle_seconds >= self.idle_threshold_seconds and self.current_conversation:
                return self._process_detected_conversation()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to check idle detection: {e}")
            return None
    
    def score_conversation_quality(self, conversation: List[Dict[str, Any]]) -> ConversationQualityMetrics:
        """
        Score conversation quality using multiple metrics.
        
        Args:
            conversation: List of message dictionaries
            
        Returns:
            Quality metrics and scoring
        """
        try:
            # Calculate individual scores
            length_score = self._calculate_length_score(conversation)
            depth_score = self._calculate_depth_score(conversation)
            entity_score = self._calculate_entity_score(conversation)
            context_score = self._calculate_context_score(conversation)
            
            # Calculate weighted overall score
            overall_score = (
                length_score * self.quality_weights['length'] +
                depth_score * self.quality_weights['depth'] +
                entity_score * self.quality_weights['entity'] +
                context_score * self.quality_weights['context']
            )
            
            # Identify issues and suggestions
            issues = self._identify_quality_issues(conversation, {
                'length': length_score,
                'depth': depth_score,
                'entity': entity_score,
                'context': context_score
            })
            
            suggestions = self._generate_quality_suggestions(issues)
            
            return ConversationQualityMetrics(
                length_score=length_score,
                depth_score=depth_score,
                entity_score=entity_score,
                context_score=context_score,
                overall_score=overall_score,
                issues=issues,
                suggestions=suggestions
            )
            
        except Exception as e:
            self.logger.error(f"Failed to score conversation quality: {e}")
            return ConversationQualityMetrics(0, 0, 0, 0, 0, ['Scoring failed'], [])
    
    def _analyze_conversation_patterns(self) -> Dict[str, Any]:
        """Analyze current conversation for patterns and completion indicators"""
        if not self.current_conversation:
            return {}
        
        patterns = {
            'message_count': len(self.current_conversation),
            'user_messages': len([m for m in self.current_conversation if m['role'] == 'user']),
            'assistant_messages': len([m for m in self.current_conversation if m['role'] == 'assistant']),
            'completion_indicators': []
        }
        
        # Check for completion indicators
        last_message = self.current_conversation[-1]['content'].lower()
        
        completion_phrases = [
            'thank you', 'thanks', 'perfect', 'great', 'awesome',
            'that works', 'got it', 'understood', 'makes sense',
            'will do', 'sounds good', 'appreciate it'
        ]
        
        for phrase in completion_phrases:
            if phrase in last_message:
                patterns['completion_indicators'].append(f"Completion phrase: '{phrase}'")
        
        # Check for task completion
        task_completion_phrases = [
            'done', 'finished', 'completed', 'working now',
            'fixed', 'resolved', 'implemented', 'tested'
        ]
        
        for phrase in task_completion_phrases:
            if phrase in last_message:
                patterns['completion_indicators'].append(f"Task completion: '{phrase}'")
        
        return patterns
    
    def _process_detected_conversation(self) -> Dict[str, Any]:
        """Process and recommend capture for detected conversation"""
        try:
            # Score conversation quality
            quality_metrics = self.score_conversation_quality(self.current_conversation)
            
            # Check if conversation meets quality threshold
            should_capture = (
                len(self.current_conversation) >= self.min_conversation_length and
                quality_metrics.overall_score >= self.quality_threshold
            )
            
            result = {
                'conversation_detected': True,
                'message_count': len(self.current_conversation),
                'quality_score': quality_metrics.overall_score,
                'should_capture': should_capture,
                'quality_metrics': {
                    'length_score': quality_metrics.length_score,
                    'depth_score': quality_metrics.depth_score,
                    'entity_score': quality_metrics.entity_score,
                    'context_score': quality_metrics.context_score,
                    'issues': quality_metrics.issues,
                    'suggestions': quality_metrics.suggestions
                }
            }
            
            if should_capture:
                result['capture_recommendation'] = {
                    'message': f"High-quality conversation detected (score: {quality_metrics.overall_score:.2f})",
                    'action': 'Run /CORTEX Capture to save this conversation',
                    'auto_capture_available': True
                }
            else:
                result['skip_reason'] = self._get_skip_reason(quality_metrics)
            
            # Reset for next conversation
            self.current_conversation = []
            self.last_activity = None
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to process detected conversation: {e}")
            return {'error': str(e)}
    
    def _calculate_length_score(self, conversation: List[Dict[str, Any]]) -> float:
        """Calculate score based on conversation length"""
        message_count = len(conversation)
        total_length = sum(len(msg['content']) for msg in conversation)
        
        # Score based on message count (optimal: 4-20 messages)
        if message_count < 2:
            count_score = 0.2
        elif message_count <= 4:
            count_score = 0.6
        elif message_count <= 20:
            count_score = 1.0
        else:
            count_score = max(0.7, 1.0 - (message_count - 20) * 0.05)
        
        # Score based on total length (optimal: 500-5000 chars)
        if total_length < 100:
            length_score = 0.3
        elif total_length <= 5000:
            length_score = 1.0
        else:
            length_score = max(0.5, 1.0 - (total_length - 5000) * 0.0001)
        
        return (count_score + length_score) / 2
    
    def _calculate_depth_score(self, conversation: List[Dict[str, Any]]) -> float:
        """Calculate score based on conversation depth/complexity"""
        all_text = ' '.join(msg['content'] for msg in conversation).lower()
        
        depth_indicators = {
            'technical_terms': ['implementation', 'algorithm', 'architecture', 'design',
                               'function', 'method', 'class', 'module', 'component'],
            'problem_solving': ['error', 'issue', 'problem', 'fix', 'solution',
                               'debug', 'troubleshoot', 'resolve'],
            'learning': ['learn', 'understand', 'explain', 'clarify', 'example',
                        'how does', 'why does', 'what is'],
            'collaboration': ['let me', 'can you', 'would you', 'please',
                             'help me', 'show me', 'guide me']
        }
        
        total_score = 0
        for category, terms in depth_indicators.items():
            category_score = min(1.0, sum(1 for term in terms if term in all_text) / len(terms))
            total_score += category_score
        
        return min(1.0, total_score / len(depth_indicators))
    
    def _calculate_entity_score(self, conversation: List[Dict[str, Any]]) -> float:
        """Calculate score based on technical entities mentioned"""
        all_text = ' '.join(msg['content'] for msg in conversation)
        
        # File patterns
        file_matches = re.findall(r'\b[a-zA-Z0-9_-]+\.\w+\b', all_text)
        
        # Class/type patterns
        class_matches = re.findall(r'\b[A-Z][a-zA-Z0-9]*(?:Controller|Service|Manager|Component)?\b', all_text)
        
        # Function patterns
        function_matches = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\s*\(', all_text)
        
        # Technology patterns
        tech_patterns = ['python', 'javascript', 'typescript', 'react', 'node',
                        'sql', 'api', 'rest', 'json', 'yaml', 'git', 'docker']
        tech_matches = [term for term in tech_patterns if term in all_text.lower()]
        
        total_entities = len(file_matches) + len(class_matches) + len(function_matches) + len(tech_matches)
        
        # Normalize score (optimal: 5-20 entities)
        if total_entities == 0:
            return 0.1
        elif total_entities <= 5:
            return total_entities / 5 * 0.8
        elif total_entities <= 20:
            return 1.0
        else:
            return max(0.7, 1.0 - (total_entities - 20) * 0.02)
    
    def _calculate_context_score(self, conversation: List[Dict[str, Any]]) -> float:
        """Calculate score based on technical context and coherence"""
        all_text = ' '.join(msg['content'] for msg in conversation).lower()
        
        context_indicators = {
            'code_related': ['code', 'function', 'variable', 'syntax', 'logic'],
            'development': ['project', 'feature', 'requirement', 'specification'],
            'debugging': ['error', 'exception', 'bug', 'fail', 'broken'],
            'planning': ['design', 'architecture', 'plan', 'strategy', 'approach'],
            'documentation': ['document', 'readme', 'guide', 'manual', 'help']
        }
        
        context_scores = []
        for category, terms in context_indicators.items():
            score = min(1.0, sum(1 for term in terms if term in all_text) / len(terms))
            if score > 0:
                context_scores.append(score)
        
        # Return average score of present contexts
        return sum(context_scores) / len(context_scores) if context_scores else 0.2
    
    def _identify_quality_issues(self, conversation: List[Dict[str, Any]], scores: Dict[str, float]) -> List[str]:
        """Identify specific quality issues"""
        issues = []
        
        if scores['length'] < 0.5:
            if len(conversation) < 2:
                issues.append("Conversation too short (less than 2 exchanges)")
            else:
                total_length = sum(len(msg['content']) for msg in conversation)
                if total_length < 100:
                    issues.append("Messages too brief (less than 100 total characters)")
        
        if scores['depth'] < 0.4:
            issues.append("Limited technical depth or problem-solving content")
        
        if scores['entity'] < 0.3:
            issues.append("Few technical entities (files, functions, technologies) mentioned")
        
        if scores['context'] < 0.4:
            issues.append("Weak technical context or coherence")
        
        return issues
    
    def _generate_quality_suggestions(self, issues: List[str]) -> List[str]:
        """Generate improvement suggestions based on issues"""
        suggestions = []
        
        for issue in issues:
            if "too short" in issue:
                suggestions.append("Consider capturing longer conversations with more detail")
            elif "brief" in issue:
                suggestions.append("Look for conversations with more substantial exchanges")
            elif "technical depth" in issue:
                suggestions.append("Focus on conversations involving problem-solving or technical discussions")
            elif "technical entities" in issue:
                suggestions.append("Prioritize conversations mentioning specific files, functions, or technologies")
            elif "technical context" in issue:
                suggestions.append("Capture conversations with clear technical context and coherent topics")
        
        if not suggestions:
            suggestions.append("Conversation quality is good - consider capturing")
        
        return suggestions
    
    def _get_skip_reason(self, quality_metrics: ConversationQualityMetrics) -> str:
        """Get reason for skipping conversation capture"""
        if quality_metrics.overall_score < self.quality_threshold:
            return f"Quality score {quality_metrics.overall_score:.2f} below threshold {self.quality_threshold}"
        else:
            return "Conversation does not meet minimum requirements"


# Export for use in conversation capture system
__all__ = ['AutoDetectionEngine', 'ConversationQualityMetrics']