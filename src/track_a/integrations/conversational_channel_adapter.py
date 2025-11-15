"""
Conversational Channel Adapter
===============================

Purpose: Adapter for integrating with dual_channel_memory.py ConversationalChannel.
Provides clean interface for storing and retrieving conversations in Tier 1.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


class ConversationalChannelAdapter:
    """
    Adapter for ConversationalChannel from dual_channel_memory.py.
    
    Responsibilities:
    - Store parsed conversations in Tier 1 via ConversationalChannel
    - Preserve semantic metadata (entities, intents, patterns)
    - Support quality-based filtering
    - Provide retrieval interface for imported conversations
    
    Note: This adapter will integrate with src/tier1/dual_channel_memory.py
    once dual-channel architecture is merged. For now, provides mock interface.
    """
    
    def __init__(self):
        """Initialize ConversationalChannelAdapter."""
        self._conversations_stored = []  # Mock storage for Phase 1
        logger.info("ConversationalChannelAdapter initialized (mock mode)")
    
    def store_conversation(
        self,
        conversation: Dict,
        source: str,
        quality_threshold: Optional[float] = None
    ) -> Dict:
        """
        Store conversation via ConversationalChannel.
        
        Args:
            conversation: Parsed conversation with semantic data
            source: Source identifier (e.g., "manual_import", "clipboard")
            quality_threshold: Minimum quality score (optional filter)
        
        Returns:
            Storage result dictionary with conversation_id
        
        Note:
            In production, this will delegate to:
            from src.tier1.dual_channel_memory import ConversationalChannel
            channel.store(conversation)
        """
        # Quality filtering
        quality_score = conversation.get("semantic_data", {}).get("quality_score", 0)
        
        if quality_threshold and quality_score < quality_threshold:
            logger.info(
                f"Conversation below quality threshold "
                f"({quality_score:.1f} < {quality_threshold:.1f}), skipping"
            )
            return {
                "conversation_id": None,
                "stored": False,
                "reason": "below_quality_threshold"
            }
        
        # Generate conversation ID
        conversation_id = self._generate_conversation_id(conversation)
        
        # Add metadata
        storage_record = {
            "conversation_id": conversation_id,
            "source": source,
            "stored_at": datetime.now().isoformat(),
            "conversation": conversation,
            "quality_score": quality_score
        }
        
        # Mock storage (Phase 1)
        self._conversations_stored.append(storage_record)
        
        logger.info(
            f"Conversation stored: {conversation_id} "
            f"(quality={quality_score:.1f}, source={source})"
        )
        
        return {
            "conversation_id": conversation_id,
            "stored": True,
            "storage_location": "conversational_channel",
            "message_count": len(conversation.get("messages", [])),
            "quality_score": quality_score
        }
    
    def retrieve_conversation(self, conversation_id: str) -> Optional[Dict]:
        """
        Retrieve conversation by ID.
        
        Args:
            conversation_id: Conversation identifier
        
        Returns:
            Full conversation record (with conversation_id and conversation) or None if not found
        """
        for record in self._conversations_stored:
            if record["conversation_id"] == conversation_id:
                return record  # Return full record, not just conversation
        
        return None
    
    def query_by_quality(
        self,
        min_quality: float,
        max_quality: float = 10.0,
        limit: int = 10
    ) -> List[Dict]:
        """
        Query conversations by quality score range.
        
        Args:
            min_quality: Minimum quality score
            max_quality: Maximum quality score
            limit: Maximum results to return
        
        Returns:
            List of conversation dictionaries
        """
        results = []
        
        for record in self._conversations_stored:
            quality = record.get("quality_score", 0)
            
            if min_quality <= quality <= max_quality:
                results.append(record["conversation"])
                
                if len(results) >= limit:
                    break
        
        return results
    
    def query_by_entities(
        self,
        entity_type: str,
        entity_value: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Query conversations mentioning specific entities.
        
        Args:
            entity_type: Entity type (file, class, function)
            entity_value: Entity value to search for
            limit: Maximum results
        
        Returns:
            List of matching conversations
        """
        results = []
        
        for record in self._conversations_stored:
            conv = record["conversation"]
            entities = conv.get("semantic_data", {}).get("entities", [])
            
            # Check if entity matches
            for entity in entities:
                if (entity["type"] == entity_type and 
                    entity_value.lower() in entity["value"].lower()):
                    results.append(conv)
                    break
            
            if len(results) >= limit:
                break
        
        return results
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about stored conversations.
        
        Returns:
            Statistics dictionary
        """
        if not self._conversations_stored:
            return {
                "total_conversations": 0,
                "avg_quality_score": 0.0,
                "total_messages": 0,
                "total_entities": 0
            }
        
        total_messages = sum(
            len(r["conversation"].get("messages", []))
            for r in self._conversations_stored
        )
        
        total_entities = sum(
            len(r["conversation"].get("semantic_data", {}).get("entities", []))
            for r in self._conversations_stored
        )
        
        quality_scores = [
            r.get("quality_score", 0)
            for r in self._conversations_stored
        ]
        
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        return {
            "total_conversations": len(self._conversations_stored),
            "avg_quality_score": avg_quality,
            "total_messages": total_messages,
            "total_entities": total_entities,
            "quality_distribution": {
                "excellent (9-10)": sum(1 for q in quality_scores if q >= 9),
                "good (7-9)": sum(1 for q in quality_scores if 7 <= q < 9),
                "fair (5-7)": sum(1 for q in quality_scores if 5 <= q < 7),
                "poor (<5)": sum(1 for q in quality_scores if q < 5)
            }
        }
    
    def _generate_conversation_id(self, conversation: Dict) -> str:
        """
        Generate unique conversation ID.
        
        Format: conv_YYYYMMDD_HHMMSS_<hash>
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Simple hash from first message
        messages = conversation.get("messages", [])
        if messages:
            first_msg = messages[0]["content"][:50]
            hash_val = abs(hash(first_msg)) % 10000
            return f"conv_{timestamp}_{hash_val:04d}"
        
        return f"conv_{timestamp}_0000"
