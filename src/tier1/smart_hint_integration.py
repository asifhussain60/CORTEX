"""
CORTEX 3.0 - Smart Hint Integration

Purpose: Integration layer for conversation capture workflow.
Provides unified interface for quality analysis, hint generation, and vault storage.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import os
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime

from src.tier1.conversation_quality import (
    ConversationQualityAnalyzer,
    QualityScore,
    create_analyzer
)
from src.tier1.smart_hint_generator import (
    SmartHintGenerator,
    SmartHint,
    create_hint_generator
)
from src.tier1.conversation_vault import (
    ConversationVaultManager,
    ConversationMetadata,
    ConversationTurn,
    create_vault_manager
)


class SmartHintSystem:
    """
    Unified interface for CORTEX 3.0 smart hint conversation capture.
    
    Workflow:
    1. Analyze conversation quality (semantic scoring)
    2. Generate hint if quality threshold met
    3. On user request, capture to vault
    4. Return hint text for display in response
    
    Usage:
    ```python
    system = SmartHintSystem()
    
    # After generating response
    hint = system.analyze_and_generate_hint(user_prompt, assistant_response)
    
    if hint.should_show:
        print(hint.hint_text)  # Display to user
    
    # When user says "capture conversation"
    filepath = system.capture_conversation(
        user_prompt, 
        assistant_response,
        hint.conversation_id
    )
    ```
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize smart hint system.
        
        Args:
            config: Optional configuration dict
        """
        self.config = config or {}
        
        # Initialize components
        self.analyzer = create_analyzer(self.config.get('quality_analyzer'))
        self.hint_generator = create_hint_generator(self.config.get('hint_generator'))
        self.vault_manager = create_vault_manager(self.config.get('vault_manager'))
        
        # State tracking
        self.current_conversation_id: Optional[str] = None
        self.current_quality: Optional[QualityScore] = None
        self.current_turns: list = []
    
    def analyze_and_generate_hint(
        self,
        user_prompt: str,
        assistant_response: str
    ) -> SmartHint:
        """
        Analyze conversation and generate hint if needed.
        
        Args:
            user_prompt: User's input
            assistant_response: CORTEX's response
            
        Returns:
            SmartHint with conditional display
        """
        # Analyze quality
        quality = self.analyzer.analyze_conversation(user_prompt, assistant_response)
        
        # Generate hint
        hint = self.hint_generator.generate_hint(quality, user_prompt)
        
        # Store for potential capture
        self.current_conversation_id = hint.conversation_id
        self.current_quality = quality
        self.current_turns = [(user_prompt, assistant_response)]
        
        return hint
    
    def capture_conversation(
        self,
        user_prompt: str,
        assistant_response: str,
        conversation_id: Optional[str] = None
    ) -> Tuple[Path, ConversationMetadata]:
        """
        Capture conversation to vault.
        
        Args:
            user_prompt: User's input
            assistant_response: CORTEX's response
            conversation_id: Optional ID (uses current if not provided)
            
        Returns:
            Tuple of (filepath, metadata)
        """
        # Use current ID if not provided
        if conversation_id is None:
            conversation_id = self.current_conversation_id or self._generate_id()
        
        # Use current quality or re-analyze
        if self.current_quality is None:
            quality = self.analyzer.analyze_conversation(user_prompt, assistant_response)
        else:
            quality = self.current_quality
        
        # Build metadata
        metadata = ConversationMetadata(
            conversation_id=conversation_id,
            timestamp=datetime.now().isoformat(),
            quality_score=quality.total_score,
            quality_level=quality.level,
            semantic_elements=self._serialize_elements(quality.elements),
            total_turns=1,
            user_topic=self._extract_topic(user_prompt)
        )
        
        # Build turn
        turn = ConversationTurn(
            turn_number=1,
            user_prompt=user_prompt,
            assistant_response=assistant_response,
            timestamp=datetime.now().isoformat()
        )
        
        # Generate filename
        filename = self.hint_generator._generate_filename(user_prompt, conversation_id)
        
        # Create file
        filepath = self.vault_manager.create_conversation_file(
            metadata=metadata,
            turns=[turn],
            filename=filename
        )
        
        return filepath, metadata
    
    def capture_multi_turn_conversation(
        self,
        turns: list[Tuple[str, str]],
        topic: str
    ) -> Tuple[Path, ConversationMetadata]:
        """
        Capture multi-turn conversation.
        
        Args:
            turns: List of (user_prompt, assistant_response) tuples
            topic: Conversation topic/title
            
        Returns:
            Tuple of (filepath, metadata)
        """
        # Analyze entire conversation
        quality = self.analyzer.analyze_multi_turn_conversation(turns)
        
        conversation_id = self._generate_id()
        
        # Build metadata
        metadata = ConversationMetadata(
            conversation_id=conversation_id,
            timestamp=datetime.now().isoformat(),
            quality_score=quality.total_score,
            quality_level=quality.level,
            semantic_elements=self._serialize_elements(quality.elements),
            total_turns=len(turns),
            user_topic=topic
        )
        
        # Build turns
        turn_objects = [
            ConversationTurn(
                turn_number=i + 1,
                user_prompt=user_prompt,
                assistant_response=assistant_response,
                timestamp=datetime.now().isoformat()
            )
            for i, (user_prompt, assistant_response) in enumerate(turns)
        ]
        
        # Generate filename
        filename = self.hint_generator._generate_filename(topic, conversation_id)
        
        # Create file
        filepath = self.vault_manager.create_conversation_file(
            metadata=metadata,
            turns=turn_objects,
            filename=filename
        )
        
        return filepath, metadata
    
    def get_vault_stats(self) -> Dict:
        """Get vault statistics."""
        return self.vault_manager.get_vault_stats()
    
    def list_recent_conversations(self, limit: int = 5) -> list:
        """List recent captured conversations."""
        return self.vault_manager.list_conversations(limit=limit)
    
    def _generate_id(self) -> str:
        """Generate conversation ID."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        return f"conv-{timestamp}"
    
    def _extract_topic(self, user_prompt: str) -> str:
        """Extract topic from user prompt."""
        # Simple extraction: first line or first 60 chars
        topic = user_prompt.split('\n')[0].strip()
        if len(topic) > 60:
            topic = topic[:57] + "..."
        return topic or "Untitled Conversation"
    
    def _serialize_elements(self, elements) -> Dict:
        """Convert SemanticElements to dict."""
        return {
            'multi_phase_planning': elements.multi_phase_planning,
            'phase_count': elements.phase_count,
            'challenge_accept_flow': elements.challenge_accept_flow,
            'design_decisions': elements.design_decisions,
            'file_references': elements.file_references,
            'next_steps_provided': elements.next_steps_provided,
            'code_implementation': elements.code_implementation,
            'architectural_discussion': elements.architectural_discussion
        }


# Global instance for easy access
_smart_hint_system: Optional[SmartHintSystem] = None


def get_smart_hint_system(config: Dict = None) -> SmartHintSystem:
    """
    Get or create global SmartHintSystem instance.
    
    Args:
        config: Optional configuration
        
    Returns:
        SmartHintSystem instance
    """
    global _smart_hint_system
    
    if _smart_hint_system is None:
        _smart_hint_system = SmartHintSystem(config)
    
    return _smart_hint_system


def analyze_response_for_hint(
    user_prompt: str,
    assistant_response: str
) -> Optional[str]:
    """
    Convenience function for use in response templates.
    
    Returns hint text if should be shown, None otherwise.
    
    Args:
        user_prompt: User's message
        assistant_response: Assistant's response
        
    Returns:
        Hint text or None
    """
    system = get_smart_hint_system()
    hint = system.analyze_and_generate_hint(user_prompt, assistant_response)
    
    return hint.hint_text if hint.should_show else None


def capture_current_conversation(
    user_prompt: str,
    assistant_response: str
) -> str:
    """
    Convenience function to capture conversation.
    
    Returns confirmation message.
    
    Args:
        user_prompt: User's message
        assistant_response: Assistant's response
        
    Returns:
        Confirmation message with filepath
    """
    system = get_smart_hint_system()
    filepath, metadata = system.capture_conversation(user_prompt, assistant_response)
    
    return f"""✅ **Conversation captured successfully!**

📁 **File:** `{filepath}`  
🆔 **ID:** `{metadata.conversation_id}`  
⭐ **Quality:** {metadata.quality_level} ({metadata.quality_score}/10)  
📊 **Turns:** {metadata.total_turns}

You can import this to Tier 1 memory anytime by saying:
```
import conversation {metadata.conversation_id}
```
"""
