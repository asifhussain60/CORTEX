"""
CORTEX Persona Detection System
================================

Intelligent user persona detection for adaptive response templates.

Version: 1.0
Date: 2026-01-04
Status: Design Specification
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple
import re


class Persona(Enum):
    """User persona types."""
    LEADERSHIP = "leadership"
    PRODUCT_OWNER = "product_owner"
    DEVELOPER = "developer"
    UNKNOWN = "unknown"


@dataclass
class PersonaSignals:
    """Signals used for persona detection."""
    
    # Explicit role identification
    explicit_role: Optional[str] = None
    
    # Language patterns
    business_terms: List[str] = None
    agile_terms: List[str] = None
    technical_terms: List[str] = None
    
    # Question types
    strategic_questions: int = 0
    workflow_questions: int = 0
    technical_questions: int = 0
    
    # Tools mentioned
    business_tools: List[str] = None
    pm_tools: List[str] = None
    dev_tools: List[str] = None
    
    # Time horizon
    long_term_focus: int = 0  # Quarterly/annual
    sprint_focus: int = 0     # 2-4 weeks
    daily_focus: int = 0      # Immediate tasks
    
    # Metric preferences
    business_metrics: int = 0  # ROI, cost, revenue
    delivery_metrics: int = 0  # Velocity, quality
    code_metrics: int = 0      # Coverage, complexity


class PersonaDetector:
    """
    Analyzes conversation context to determine user persona.
    
    Uses multiple signals:
    - Explicit role identification
    - Language patterns
    - Question types
    - Tools mentioned
    - Time horizon
    - Metric preferences
    """
    
    # Pattern definitions
    LEADERSHIP_PATTERNS = {
        'roles': r'\b(cto|ceo|vp|director|executive|business owner|head of)\b',
        'business_terms': [
            'roi', 'cost', 'budget', 'revenue', 'profit', 'investment',
            'strategic', 'competitive advantage', 'market', 'scale',
            'risk', 'compliance', 'governance', 'enterprise'
        ],
        'questions': [
            r"what'?s the roi",
            r"how (?:does|will) (?:this|it) scale",
            r"what'?s the (?:business )?(?:value|impact)",
            r"(?:cost|budget|investment)",
            r"risk",
        ],
        'tools': ['powerbi', 'tableau', 'excel', 'strategic planning'],
        'metrics': ['roi', 'cost reduction', 'time-to-market', 'market share']
    }
    
    PRODUCT_OWNER_PATTERNS = {
        'roles': r'\b(product owner|po|scrum master|agile coach|product manager)\b',
        'agile_terms': [
            'sprint', 'backlog', 'user story', 'velocity', 'burndown',
            'standup', 'retrospective', 'planning', 'estimation',
            'acceptance criteria', 'done', 'ready'
        ],
        'questions': [
            r"(?:integrate|sync) (?:with )?(?:ado|azure devops)",
            r"sprint",
            r"backlog",
            r"velocity",
            r"planning",
            r"estimation",
        ],
        'tools': ['azure devops', 'ado', 'jira', 'confluence', 'trello'],
        'metrics': ['velocity', 'sprint burndown', 'team capacity']
    }
    
    DEVELOPER_PATTERNS = {
        'roles': r'\b(developer|engineer|programmer|dev|tech lead|architect)\b',
        'technical_terms': [
            'tdd', 'test', 'debug', 'refactor', 'code', 'function',
            'class', 'api', 'git', 'commit', 'branch', 'merge',
            'ci/cd', 'pipeline', 'deploy', 'build', 'coverage'
        ],
        'questions': [
            r"how (?:do|can) i (?:use|run|implement)",
            r"what command",
            r"how (?:does|do) (?:tdd|debugging|refactoring)",
            r"(?:code|function|class|test)",
            r"integrate with (?:git|ide|vscode)",
        ],
        'tools': ['vscode', 'git', 'github', 'docker', 'kubernetes', 'jenkins'],
        'metrics': ['test coverage', 'code quality', 'build time']
    }
    
    def __init__(self, confidence_threshold: float = 0.6):
        """
        Initialize persona detector.
        
        Args:
            confidence_threshold: Minimum confidence score (0-1) to select persona
        """
        self.confidence_threshold = confidence_threshold
        
    def detect_persona(
        self,
        conversation_history: List[str],
        current_message: str,
        user_profile: Optional[Dict] = None
    ) -> Tuple[Persona, float, Dict[Persona, float]]:
        """
        Detect user persona from conversation context.
        
        Args:
            conversation_history: Previous messages in conversation
            current_message: Current user message
            user_profile: Optional user profile data (saved role, etc.)
            
        Returns:
            Tuple of (detected_persona, confidence, all_scores)
        """
        # Extract signals
        signals = self._extract_signals(
            conversation_history + [current_message],
            user_profile
        )
        
        # Calculate scores
        scores = self._calculate_scores(signals)
        
        # Select persona
        persona, confidence = self._select_persona(scores)
        
        return persona, confidence, scores
    
    def _extract_signals(
        self,
        messages: List[str],
        user_profile: Optional[Dict]
    ) -> PersonaSignals:
        """Extract signals from messages and profile."""
        signals = PersonaSignals()
        
        # Combine all messages
        full_text = " ".join(messages).lower()
        
        # Check for explicit role identification
        if user_profile and 'role' in user_profile:
            signals.explicit_role = user_profile['role'].lower()
        else:
            # Check in messages
            for pattern_dict in [
                self.LEADERSHIP_PATTERNS,
                self.PRODUCT_OWNER_PATTERNS,
                self.DEVELOPER_PATTERNS
            ]:
                match = re.search(pattern_dict['roles'], full_text, re.IGNORECASE)
                if match:
                    signals.explicit_role = match.group(0)
                    break
        
        # Extract language patterns
        signals.business_terms = [
            term for term in self.LEADERSHIP_PATTERNS['business_terms']
            if term in full_text
        ]
        signals.agile_terms = [
            term for term in self.PRODUCT_OWNER_PATTERNS['agile_terms']
            if term in full_text
        ]
        signals.technical_terms = [
            term for term in self.DEVELOPER_PATTERNS['technical_terms']
            if term in full_text
        ]
        
        # Count question types
        for question_pattern in self.LEADERSHIP_PATTERNS['questions']:
            if re.search(question_pattern, full_text, re.IGNORECASE):
                signals.strategic_questions += 1
                
        for question_pattern in self.PRODUCT_OWNER_PATTERNS['questions']:
            if re.search(question_pattern, full_text, re.IGNORECASE):
                signals.workflow_questions += 1
                
        for question_pattern in self.DEVELOPER_PATTERNS['questions']:
            if re.search(question_pattern, full_text, re.IGNORECASE):
                signals.technical_questions += 1
        
        # Identify tools mentioned
        signals.business_tools = [
            tool for tool in self.LEADERSHIP_PATTERNS['tools']
            if tool in full_text
        ]
        signals.pm_tools = [
            tool for tool in self.PRODUCT_OWNER_PATTERNS['tools']
            if tool in full_text
        ]
        signals.dev_tools = [
            tool for tool in self.DEVELOPER_PATTERNS['tools']
            if tool in full_text
        ]
        
        # Analyze time horizon
        if any(term in full_text for term in [
            'quarterly', 'annual', 'year', 'long-term', 'strategic', 'roadmap'
        ]):
            signals.long_term_focus += 1
            
        if any(term in full_text for term in [
            'sprint', 'iteration', 'next week', 'this week', 'backlog'
        ]):
            signals.sprint_focus += 1
            
        if any(term in full_text for term in [
            'today', 'now', 'immediate', 'currently', 'right now'
        ]):
            signals.daily_focus += 1
        
        # Count metric preferences
        for metric in self.LEADERSHIP_PATTERNS['metrics']:
            if metric in full_text:
                signals.business_metrics += 1
                
        for metric in self.PRODUCT_OWNER_PATTERNS['metrics']:
            if metric in full_text:
                signals.delivery_metrics += 1
                
        for metric in self.DEVELOPER_PATTERNS['metrics']:
            if metric in full_text:
                signals.code_metrics += 1
        
        return signals
    
    def _calculate_scores(self, signals: PersonaSignals) -> Dict[Persona, float]:
        """Calculate confidence scores for each persona."""
        scores = {
            Persona.LEADERSHIP: 0.0,
            Persona.PRODUCT_OWNER: 0.0,
            Persona.DEVELOPER: 0.0,
        }
        
        # Weight different signals
        WEIGHTS = {
            'explicit_role': 0.5,      # Strongest signal
            'language': 0.15,
            'questions': 0.15,
            'tools': 0.10,
            'time_horizon': 0.05,
            'metrics': 0.05,
        }
        
        # Leadership scoring
        if signals.explicit_role:
            if re.search(
                self.LEADERSHIP_PATTERNS['roles'],
                signals.explicit_role,
                re.IGNORECASE
            ):
                scores[Persona.LEADERSHIP] += WEIGHTS['explicit_role']
        
        scores[Persona.LEADERSHIP] += (
            WEIGHTS['language'] * len(signals.business_terms or []) / 10 +
            WEIGHTS['questions'] * signals.strategic_questions / 3 +
            WEIGHTS['tools'] * len(signals.business_tools or []) / 2 +
            WEIGHTS['time_horizon'] * signals.long_term_focus +
            WEIGHTS['metrics'] * signals.business_metrics / 2
        )
        
        # Product Owner scoring
        if signals.explicit_role:
            if re.search(
                self.PRODUCT_OWNER_PATTERNS['roles'],
                signals.explicit_role,
                re.IGNORECASE
            ):
                scores[Persona.PRODUCT_OWNER] += WEIGHTS['explicit_role']
        
        scores[Persona.PRODUCT_OWNER] += (
            WEIGHTS['language'] * len(signals.agile_terms or []) / 10 +
            WEIGHTS['questions'] * signals.workflow_questions / 3 +
            WEIGHTS['tools'] * len(signals.pm_tools or []) / 2 +
            WEIGHTS['time_horizon'] * signals.sprint_focus +
            WEIGHTS['metrics'] * signals.delivery_metrics / 2
        )
        
        # Developer scoring
        if signals.explicit_role:
            if re.search(
                self.DEVELOPER_PATTERNS['roles'],
                signals.explicit_role,
                re.IGNORECASE
            ):
                scores[Persona.DEVELOPER] += WEIGHTS['explicit_role']
        
        scores[Persona.DEVELOPER] += (
            WEIGHTS['language'] * len(signals.technical_terms or []) / 10 +
            WEIGHTS['questions'] * signals.technical_questions / 3 +
            WEIGHTS['tools'] * len(signals.dev_tools or []) / 2 +
            WEIGHTS['time_horizon'] * signals.daily_focus +
            WEIGHTS['metrics'] * signals.code_metrics / 2
        )
        
        # Normalize scores to 0-1 range
        max_score = max(scores.values()) if scores.values() else 1.0
        if max_score > 0:
            scores = {
                persona: score / max_score
                for persona, score in scores.items()
            }
        
        return scores
    
    def _select_persona(
        self,
        scores: Dict[Persona, float]
    ) -> Tuple[Persona, float]:
        """Select persona based on confidence scores."""
        # Find highest scoring persona
        best_persona = max(scores.items(), key=lambda x: x[1])
        persona, confidence = best_persona
        
        # If confidence below threshold, return UNKNOWN
        if confidence < self.confidence_threshold:
            return Persona.UNKNOWN, confidence
        
        return persona, confidence


# Example usage
if __name__ == "__main__":
    detector = PersonaDetector(confidence_threshold=0.6)
    
    # Example 1: Leadership
    messages = [
        "What is CORTEX?",
        "I'm a CTO and want to understand the ROI and business value."
    ]
    persona, confidence, scores = detector.detect_persona(messages, messages[-1])
    print(f"Persona: {persona.value}, Confidence: {confidence:.2f}")
    print(f"All scores: {scores}\n")
    
    # Example 2: Product Owner
    messages = [
        "How does CORTEX integrate with Azure DevOps?",
        "I'm a product owner trying to improve sprint velocity."
    ]
    persona, confidence, scores = detector.detect_persona(messages, messages[-1])
    print(f"Persona: {persona.value}, Confidence: {confidence:.2f}")
    print(f"All scores: {scores}\n")
    
    # Example 3: Developer
    messages = [
        "How do I use the TDD orchestrator?",
        "I want to improve my test coverage and code quality."
    ]
    persona, confidence, scores = detector.detect_persona(messages, messages[-1])
    print(f"Persona: {persona.value}, Confidence: {confidence:.2f}")
    print(f"All scores: {scores}\n")
