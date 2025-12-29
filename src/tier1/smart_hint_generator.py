"""
CORTEX 3.0 - Smart Hint Generator

Purpose: Generate contextual hints for valuable conversation capture.
Shows hints only when quality threshold is met (reduces noise).

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

from typing import Optional
from dataclasses import dataclass
from datetime import datetime

from src.tier1.conversation_quality import QualityScore, SemanticElements


@dataclass
class SmartHint:
    """Smart hint for conversation capture."""
    should_show: bool
    hint_text: str
    conversation_id: str
    suggested_filename: str
    quality_level: str


class SmartHintGenerator:
    """
    Generates smart hints for conversation capture.
    
    Based on CORTEX 3.0 Hybrid Capture design:
    - Shows hints only for GOOD/EXCELLENT conversations
    - Provides one-click capture suggestion
    - Generates human-readable quality summary
    - Stays in chat context (no context switching)
    """
    
    def __init__(self, vault_path: str = "cortex-brain/conversation-vault"):
        """
        Initialize hint generator.
        
        Args:
            vault_path: Path to conversation vault directory
        """
        self.vault_path = vault_path
    
    def generate_hint(
        self, 
        quality: QualityScore, 
        user_prompt: str
    ) -> SmartHint:
        """
        Generate smart hint based on conversation quality.
        
        Args:
            quality: Quality score from ConversationQualityAnalyzer
            user_prompt: User's original prompt (for filename generation)
            
        Returns:
            SmartHint with conditional display and capture instructions
        """
        if not quality.should_show_hint:
            return SmartHint(
                should_show=False,
                hint_text="",
                conversation_id="",
                suggested_filename="",
                quality_level=quality.level
            )
        
        # Generate conversation ID
        conv_id = self._generate_conversation_id()
        
        # Generate suggested filename
        filename = self._generate_filename(user_prompt, conv_id)
        
        # Build hint text
        hint_text = self._build_hint_text(quality, filename)
        
        return SmartHint(
            should_show=True,
            hint_text=hint_text,
            conversation_id=conv_id,
            suggested_filename=filename,
            quality_level=quality.level
        )
    
    def _generate_conversation_id(self) -> str:
        """Generate unique conversation ID."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        return f"conv-{timestamp}"
    
    def _generate_filename(self, user_prompt: str, conv_id: str) -> str:
        """
        Generate suggested filename from user prompt.
        
        Args:
            user_prompt: User's message
            conv_id: Conversation ID
            
        Returns:
            Sanitized filename with date and topic
        """
        # Extract topic from prompt (first 5 words, sanitized)
        words = user_prompt.lower().split()[:5]
        topic = "-".join(w for w in words if w.isalnum())
        
        # Truncate if too long
        if len(topic) > 50:
            topic = topic[:50]
        
        # Build filename
        date_str = datetime.now().strftime("%Y-%m-%d")
        return f"{date_str}-{topic}.md"
    
    def _build_hint_text(self, quality: QualityScore, filename: str) -> str:
        """
        Build formatted hint text.
        
        Args:
            quality: Quality assessment
            filename: Suggested filename
            
        Returns:
            Formatted hint text with capture instructions
        """
        # Build quality summary
        elements_list = self._format_semantic_elements(quality.elements)
        
        hint = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 **CORTEX LEARNING OPPORTUNITY**

This conversation has {quality.level.lower()} strategic value:
{elements_list}

📸 **Capture for future reference?**
   → Say: **"capture conversation"**
   → I'll save this discussion automatically
   → File will be created: `{self.vault_path}/{filename}`
   → Review now or import to brain later

Quality Score: {quality.total_score}/10 ({quality.level})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        return hint.strip()
    
    def _format_semantic_elements(self, elements: SemanticElements) -> str:
        """Format semantic elements as bullet list."""
        items = []
        
        if elements.multi_phase_planning:
            items.append(f"  • Multi-phase planning: {elements.phase_count} phases")
        
        if elements.challenge_accept_flow:
            items.append("  • Challenge/Accept reasoning")
        
        if elements.design_decisions:
            items.append("  • Design decisions")
        
        if elements.file_references > 0:
            items.append(f"  • File references: {elements.file_references}")
        
        if elements.next_steps_provided:
            items.append("  • Next steps provided")
        
        if elements.code_implementation:
            items.append("  • Code implementation")
        
        if elements.architectural_discussion:
            items.append("  • Architectural discussion")
        
        if not items:
            items.append("  • Strategic content detected")
        
        return "\n".join(items)
    
    def generate_compact_hint(self, quality: QualityScore) -> Optional[str]:
        """
        Generate compact hint for inline display.
        
        Args:
            quality: Quality assessment
            
        Returns:
            One-line hint text or None if shouldn't show
        """
        if not quality.should_show_hint:
            return None
        
        return (
            f"💡 **Tip:** This conversation has {quality.level.lower()} strategic value "
            f"({quality.total_score}/10). Say **'capture conversation'** to save for future reference."
        )


def create_hint_generator(config: dict = None) -> SmartHintGenerator:
    """
    Factory function to create hint generator with config.
    
    Args:
        config: Optional configuration dict with 'vault_path' key
        
    Returns:
        Configured SmartHintGenerator instance
    """
    vault_path = "cortex-brain/conversation-vault"
    
    if config and 'vault_path' in config:
        vault_path = config['vault_path']
    
    return SmartHintGenerator(vault_path=vault_path)
