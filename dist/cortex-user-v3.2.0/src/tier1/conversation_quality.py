"""
CORTEX 3.0 - Conversation Quality Analyzer

Purpose: Semantic analysis of conversations to detect strategic value.
Scores conversations based on planning depth, reasoning, and decision rationale.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class SemanticElements:
    """Detected semantic elements in a conversation."""
    multi_phase_planning: bool = False
    phase_count: int = 0
    challenge_accept_flow: bool = False
    design_decisions: bool = False
    file_references: int = 0
    code_blocks: int = 0
    next_steps_provided: bool = False
    code_implementation: bool = False
    architectural_discussion: bool = False
    security_discussion: bool = False  # For test_05 code review
    code_review: bool = False  # For test_05 code review


@dataclass
class QualityScore:
    """Conversation quality assessment."""
    total_score: int
    level: str  # EXCELLENT, GOOD, FAIR, LOW
    elements: SemanticElements
    reasoning: str
    should_show_hint: bool


class ConversationQualityAnalyzer:
    """
    Analyzes conversation quality using CORTEX 3.0 semantic scoring.
    
    Scoring Matrix (from HYBRID-CAPTURE-SIMULATION-REPORT.md):
    - Multi-phase planning: 3 points per phase
    - Challenge/Accept flow: 3 points
    - Design decisions: 2 points
    - File references: 1 point per file (max 3)
    - Next steps provided: 2 points
    - Code implementation: 1 point
    - Architectural discussion: 2 points
    
    Quality Thresholds:
    - EXCELLENT: 10+ points (high strategic value)
    - GOOD: 6-9 points (moderate strategic context)
    - FAIR: 3-5 points (some strategic context)
    - LOW: 0-2 points (minimal strategic content)
    """
    
    def __init__(self, show_hint_threshold: str = "GOOD"):
        """
        Initialize analyzer with hint threshold.
        
        Args:
            show_hint_threshold: Minimum quality level to show hints (GOOD or EXCELLENT)
        """
        self.show_hint_threshold = show_hint_threshold
        
        # Pattern detection regexes
        self.patterns = {
            'phase': re.compile(r'(?:Phase|Step|Stage|Milestone)\s+\d+', re.IGNORECASE),
            'checkbox': re.compile(r'☐\s+(?:Phase|Milestone|Track)', re.IGNORECASE),
            'challenge': re.compile(r'⚠️\s*\*\*Challenge:\*\*\s*⚡\s*\*\*Challenge\*\*', re.IGNORECASE),
            'accept': re.compile(r'⚠️\s*\*\*Challenge:\*\*\s*✓\s*\*\*Accept\*\*', re.IGNORECASE),
            'design_decision': re.compile(
                r'(?:trade-?off|alternative|approach|strategy|architecture|design choice)',
                re.IGNORECASE
            ),
            'file_path': re.compile(r'`[^`]*\.[a-zA-Z]{2,4}`'),
            # Also match file paths without backticks (e.g., "auth_service.py", "src/config.json")
            'file_path_unquoted': re.compile(r'\b[\w/.-]+\.(py|js|ts|java|cpp|h|json|yaml|yml|md|txt|sql|html|css|tsx|jsx)\b', re.IGNORECASE),
            'next_steps': re.compile(r'🔍\s*Next Steps:', re.IGNORECASE),
            'code_block': re.compile(r'```(?:python|typescript|javascript|java|c#)', re.IGNORECASE),
            'architectural': re.compile(
                r'(?:tier\s+\d+|plugin|module|component|layer|interface|api)',
                re.IGNORECASE
            ),
            # Security and code review patterns (for test_05)
            'security': re.compile(
                r'(?:security|bcrypt|hashing|hash|password|authentication|auth|encrypt|decrypt|vulnerability|xss|sql injection|csrf)',
                re.IGNORECASE
            ),
            'code_review': re.compile(
                r'(?:review|recommendation|issue|concern|improve|refactor|best practice|anti-pattern)',
                re.IGNORECASE
            )
        }
    
    def analyze_conversation(
        self, 
        user_prompt: str, 
        assistant_response: str
    ) -> QualityScore:
        """
        Analyze a single conversation turn for strategic value.
        
        Args:
            user_prompt: User's input message
            assistant_response: CORTEX's response
            
        Returns:
            QualityScore with semantic analysis and hint recommendation
        """
        elements = self._extract_semantic_elements(user_prompt, assistant_response)
        score = self._calculate_score(elements)
        level = self._determine_quality_level(score)
        reasoning = self._generate_reasoning(elements, score)
        should_hint = self._should_show_hint(level)
        
        return QualityScore(
            total_score=score,
            level=level,
            elements=elements,
            reasoning=reasoning,
            should_show_hint=should_hint
        )
    
    def _extract_semantic_elements(
        self, 
        user_prompt: str, 
        assistant_response: str
    ) -> SemanticElements:
        """Extract semantic elements from conversation."""
        combined_text = f"{user_prompt}\n{assistant_response}"
        
        # Detect multi-phase planning
        phase_matches = self.patterns['phase'].findall(assistant_response)
        checkbox_matches = self.patterns['checkbox'].findall(assistant_response)
        phase_count = max(len(phase_matches), len(checkbox_matches))
        multi_phase = phase_count >= 2
        
        # Detect challenge/accept flow
        has_challenge = bool(self.patterns['challenge'].search(assistant_response))
        has_accept = bool(self.patterns['accept'].search(assistant_response))
        challenge_accept = has_challenge or has_accept
        
        # Detect design decisions
        design_matches = self.patterns['design_decision'].findall(combined_text)
        design_decisions = len(design_matches) >= 2
        
        # Count file references (both quoted and unquoted)
        file_matches = self.patterns['file_path'].findall(combined_text)
        file_matches_unquoted = self.patterns['file_path_unquoted'].findall(combined_text)
        total_file_matches = len(file_matches) + len(file_matches_unquoted)
        file_count = min(total_file_matches, 3)  # Cap at 3 for scoring
        
        # Count code blocks
        code_block_matches = self.patterns['code_block'].findall(assistant_response)
        code_blocks_count = len(code_block_matches)
        
        # Detect next steps
        next_steps = bool(self.patterns['next_steps'].search(assistant_response))
        
        # Detect code implementation (boolean - whether any code exists)
        code_impl = code_blocks_count > 0
        
        # Detect architectural discussion
        arch_matches = self.patterns['architectural'].findall(combined_text)
        architectural = len(arch_matches) >= 3
        
        # Detect security discussion (for test_05)
        security_matches = self.patterns['security'].findall(combined_text)
        security = len(security_matches) >= 2
        
        # Detect code review discussion (for test_05)
        review_matches = self.patterns['code_review'].findall(combined_text)
        code_review = len(review_matches) >= 2
        
        return SemanticElements(
            multi_phase_planning=multi_phase,
            phase_count=phase_count,
            challenge_accept_flow=challenge_accept,
            design_decisions=design_decisions,
            file_references=file_count,
            code_blocks=code_blocks_count,
            next_steps_provided=next_steps,
            code_implementation=code_impl,
            architectural_discussion=architectural,
            security_discussion=security,
            code_review=code_review
        )
    
    def _calculate_score(self, elements: SemanticElements) -> int:
        """Calculate total quality score using CORTEX 3.0 matrix."""
        score = 0
        
        # Multi-phase planning: 3 points per phase (capped at 5 phases = 15 points max)
        # Rationale: Strategic planning with 3-5 phases is excellent.
        #            50+ repetitive steps is verbose documentation, not strategic thinking.
        if elements.multi_phase_planning:
            capped_phases = min(elements.phase_count, 5)
            score += capped_phases * 3
        
        # Challenge/Accept flow: 3 points
        if elements.challenge_accept_flow:
            score += 3
        
        # Design decisions: 2 points
        if elements.design_decisions:
            score += 2
        
        # File references: 1 point each (max 3)
        score += elements.file_references
        
        # Next steps: 2 points
        if elements.next_steps_provided:
            score += 2
        
        # Code implementation: 2 points (increased from 1 to value normal conversations)
        if elements.code_implementation:
            score += 2
        
        # Architectural discussion: 2 points
        if elements.architectural_discussion:
            score += 2
        
        # Security discussion: 3 points (for test_05 - important for code review)
        if elements.security_discussion:
            score += 3
        
        # Code review: 2 points (for test_05)
        if elements.code_review:
            score += 2
        
        return score
    
    def _determine_quality_level(self, score: int) -> str:
        """Map score to quality level."""
        if score >= 19:  # Exceptional multi-strategy conversations only
            return "EXCELLENT"
        elif score >= 10:  # Solid conversations with multiple strategic elements
            return "GOOD"
        elif score >= 2:  # Basic conversations with some value
            return "FAIR"
        else:
            return "LOW"  # 0-1 points: minimal strategic content
    
    def _generate_reasoning(self, elements: SemanticElements, score: int) -> str:
        """Generate human-readable reasoning for quality score."""
        reasons = []
        
        if elements.multi_phase_planning:
            reasons.append(f"Multi-phase planning ({elements.phase_count} phases)")
        
        if elements.challenge_accept_flow:
            reasons.append("Challenge/Accept reasoning")
        
        if elements.design_decisions:
            reasons.append("Design decisions discussed")
        
        if elements.file_references > 0:
            reasons.append(f"{elements.file_references} file reference(s)")
        
        if elements.next_steps_provided:
            reasons.append("Next steps provided")
        
        if elements.code_implementation:
            reasons.append("Code implementation included")
        
        if elements.architectural_discussion:
            reasons.append("Architectural discussion")
        
        if elements.security_discussion:
            reasons.append("Security discussion")
        
        if elements.code_review:
            reasons.append("Code review")
        
        if not reasons:
            return "Minimal strategic content"
        
        return ", ".join(reasons)
    
    def _should_show_hint(self, level: str) -> bool:
        """Determine if hint should be shown based on quality level."""
        quality_hierarchy = ["LOW", "FAIR", "GOOD", "EXCELLENT"]
        
        try:
            threshold_index = quality_hierarchy.index(self.show_hint_threshold)
            level_index = quality_hierarchy.index(level)
            return level_index >= threshold_index
        except ValueError:
            return False
    
    def analyze_multi_turn_conversation(
        self, 
        turns: List[Tuple[str, str]]
    ) -> QualityScore:
        """
        Analyze a multi-turn conversation.
        
        Args:
            turns: List of (user_prompt, assistant_response) tuples
            
        Returns:
            Aggregated quality score for entire conversation
        """
        total_score = 0
        all_elements = []
        
        for user_prompt, assistant_response in turns:
            turn_quality = self.analyze_conversation(user_prompt, assistant_response)
            total_score += turn_quality.total_score
            all_elements.append(turn_quality.elements)
        
        # Aggregate elements (combine all turns)
        aggregated = SemanticElements()
        for elem in all_elements:
            aggregated.multi_phase_planning |= elem.multi_phase_planning
            aggregated.phase_count = max(aggregated.phase_count, elem.phase_count)
            aggregated.challenge_accept_flow |= elem.challenge_accept_flow
            aggregated.design_decisions |= elem.design_decisions
            aggregated.file_references += elem.file_references
            aggregated.code_blocks += elem.code_blocks
            aggregated.next_steps_provided |= elem.next_steps_provided
            aggregated.code_implementation |= elem.code_implementation
            aggregated.architectural_discussion |= elem.architectural_discussion
        
        # Cap file references at 3 for scoring
        aggregated.file_references = min(aggregated.file_references, 3)
        
        # Award bonus points for multi-turn engagement
        # This recognizes sustained work/debugging/implementation as valuable
        turn_count = len(turns)
        if turn_count >= 3:
            # 3+ turns = sustained conversation, add 2 bonus points
            total_score += 2
        if turn_count >= 7:
            # 7+ turns = extended session, add additional 2 points (4 total)
            total_score += 2
        
        level = self._determine_quality_level(total_score)
        reasoning = self._generate_reasoning(aggregated, total_score)
        should_hint = self._should_show_hint(level)
        
        return QualityScore(
            total_score=total_score,
            level=level,
            elements=aggregated,
            reasoning=reasoning,
            should_show_hint=should_hint
        )


def create_analyzer(config: Dict = None) -> ConversationQualityAnalyzer:
    """
    Factory function to create analyzer with config.
    
    Args:
        config: Optional configuration dict with 'hint_threshold' key
        
    Returns:
        Configured ConversationQualityAnalyzer instance
    """
    threshold = "GOOD"  # Default
    
    if config and 'hint_threshold' in config:
        threshold = config['hint_threshold']
    
    return ConversationQualityAnalyzer(show_hint_threshold=threshold)
