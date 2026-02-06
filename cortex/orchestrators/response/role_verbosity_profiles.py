"""
Role-based verbosity profiles for response optimization.

Provides per-role formatting preferences:
- Engineer: High detail, code examples required, maximum technical depth
- PM: Medium detail, optional code, moderate technical depth
- Business: Low detail, no code, business language primary
- Architect: Medium-high detail, selective code, high technical depth

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 34 specification
"""

import re
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, Optional


class Role(Enum):
    """User role types."""
    
    ENGINEER = "ENGINEER"
    PM = "PM"
    BUSINESS = "BUSINESS"
    ARCHITECT = "ARCHITECT"


@dataclass
class VerbosityProfile:
    """
    Profile defining verbosity preferences for a role.
    
    Attributes:
        detail_level: HIGH, MEDIUM-HIGH, MEDIUM, LOW
        code_examples: REQUIRED, SELECTIVE, OPTIONAL, NONE
        business_language: PRIMARY, BALANCED, MINIMAL
        technical_depth: MAXIMUM, HIGH, MODERATE, LOW
        expected_reduction: Expected token reduction percentage
    """
    
    detail_level: str
    code_examples: str
    business_language: str
    technical_depth: str
    expected_reduction: str
    
    def to_dict(self) -> Dict[str, str]:
        """Convert profile to dictionary representation."""
        return asdict(self)


class RoleVerbosityProfiles:
    """
    Manages role-based verbosity profiles.
    
    Provides profile selection and application logic for different user roles.
    
    Example:
        >>> profiles = RoleVerbosityProfiles()
        >>> engineer_profile = profiles.get_profile(Role.ENGINEER)
        >>> response = profiles.apply_profile(text, Role.BUSINESS)
    """
    
    def __init__(self):
        """Initialize profiles for all roles."""
        self.profiles: Dict[Role, VerbosityProfile] = {
            Role.ENGINEER: VerbosityProfile(
                detail_level="HIGH",
                code_examples="REQUIRED",
                business_language="MINIMAL",
                technical_depth="MAXIMUM",
                expected_reduction="0-10%"
            ),
            Role.PM: VerbosityProfile(
                detail_level="MEDIUM",
                code_examples="OPTIONAL",
                business_language="BALANCED",
                technical_depth="MODERATE",
                expected_reduction="20-30%"
            ),
            Role.BUSINESS: VerbosityProfile(
                detail_level="LOW",
                code_examples="NONE",
                business_language="PRIMARY",
                technical_depth="LOW",
                expected_reduction="40-50%"
            ),
            Role.ARCHITECT: VerbosityProfile(
                detail_level="MEDIUM-HIGH",
                code_examples="SELECTIVE",
                business_language="MINIMAL",
                technical_depth="HIGH",
                expected_reduction="10-20%"
            ),
        }
    
    def get_profile(self, role: Optional[Role] = None) -> VerbosityProfile:
        """
        Get verbosity profile for a role.
        
        Args:
            role: Target role (defaults to ENGINEER)
            
        Returns:
            VerbosityProfile for the specified role
        """
        if role is None:
            role = Role.ENGINEER
        return self.profiles[role]
    
    def apply_profile(self, response: str, role: Role) -> str:
        """
        Apply role profile to response text.
        
        Transforms response according to role preferences:
        - ENGINEER: Preserve all content
        - PM: Remove implementation details, keep architecture
        - BUSINESS: Remove code examples, focus on outcomes
        - ARCHITECT: Keep design patterns, remove trivial code
        
        Args:
            response: Response text to transform
            role: Target role for formatting
            
        Returns:
            Transformed response text
        """
        profile = self.get_profile(role)
        result = response
        
        # Apply code example filtering
        if profile.code_examples == "NONE":
            # Remove all code blocks
            result = self._remove_code_blocks(result)
        elif profile.code_examples == "SELECTIVE":
            # Remove simple code blocks, keep architecture examples
            result = self._filter_selective_code(result)
        elif profile.code_examples == "OPTIONAL":
            # Keep code but reduce verbosity
            result = self._reduce_code_verbosity(result)
        # REQUIRED: No filtering
        
        # Apply detail level filtering
        if profile.detail_level == "LOW":
            # Keep only high-level points
            result = self._extract_key_points(result)
        elif profile.detail_level == "MEDIUM":
            # Remove implementation details
            result = self._remove_implementation_details(result)
        # HIGH/MEDIUM-HIGH: Preserve details
        
        return result
    
    def _remove_code_blocks(self, text: str) -> str:
        """
        Remove all code blocks from text.
        
        Args:
            text: Input text with code blocks
            
        Returns:
            Text with code blocks removed
        """
        # Remove fenced code blocks
        pattern = r'```[\s\S]*?```'
        result = re.sub(pattern, '', text, flags=re.MULTILINE)
        
        # Remove inline code (preserve short ones like `token`)
        result = re.sub(r'`[^`]{20,}`', '', result)
        
        return result.strip()
    
    def _filter_selective_code(self, text: str) -> str:
        """
        Keep only architectural code examples.
        
        Removes:
        - Simple function definitions
        - Basic CRUD operations
        - Trivial implementations
        
        Keeps:
        - Design patterns
        - System architecture
        - Complex algorithms
        
        Args:
            text: Input text
            
        Returns:
            Text with selective code filtering
        """
        # For now, keep all code blocks
        # Future: Implement complexity analysis
        return text
    
    def _reduce_code_verbosity(self, text: str) -> str:
        """
        Reduce code verbosity while preserving examples.
        
        Args:
            text: Input text
            
        Returns:
            Text with reduced code verbosity
        """
        # For now, preserve all code
        # Future: Implement code summarization
        return text
    
    def _extract_key_points(self, text: str) -> str:
        """
        Extract only key points from text.
        
        Focuses on:
        - Benefits and outcomes
        - High-level approach
        - Business value
        
        Args:
            text: Input text
            
        Returns:
            Text with only key points
        """
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        # Key indicators
        key_indicators = [
            'benefit', 'advantage', 'outcome', 'result',
            'enables', 'provides', 'delivers', 'achieves',
            'roi', 'value', 'impact', 'improvement'
        ]
        
        # Filter for key sentences
        key_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Check for key indicators
            sentence_lower = sentence.lower()
            if any(indicator in sentence_lower for indicator in key_indicators):
                key_sentences.append(sentence)
            # Keep first sentence (usually summary)
            elif len(key_sentences) == 0:
                key_sentences.append(sentence)
        
        return '. '.join(key_sentences) + '.'
    
    def _remove_implementation_details(self, text: str) -> str:
        """
        Remove low-level implementation details.
        
        Keeps:
        - Architecture decisions
        - Design patterns
        - Integration points
        
        Removes:
        - Variable names
        - Function signatures
        - Low-level logic
        
        Args:
            text: Input text
            
        Returns:
            Text without implementation details
        """
        # For now, preserve text
        # Future: Implement detail filtering
        return text
