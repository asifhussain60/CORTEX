"""
Conversational Channel Adapter
===============================

Purpose: Adapter for integrating with dual_channel_memory.py ConversationalChannel.
Provides clean interface for storing and retrieving conversations in Tier 1.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file

Phase 2: Real Tier 1 Storage Integration
- Replaced mock list storage with WorkingMemory persistence
- SQLite-backed storage with ACID guarantees
- Cross-session persistence support
- Backward-compatible API (all existing tests pass)
"""

from typing import Dict, List, Optional
from datetime import datetime
import logging
import json
import sqlite3
from pathlib import Path


logger = logging.getLogger(__name__)


class ConversationalChannelAdapter:
    """
    Adapter for ConversationalChannel from dual_channel_memory.py.
    
    Phase 2: Real Tier 1 storage integration complete.
    
    Responsibilities:
    - Store parsed conversations in Tier 1 via WorkingMemory
    - Preserve semantic metadata (entities, intents, patterns)
    - Support quality-based filtering
    - Provide retrieval interface for imported conversations
    - Persist conversations across sessions (SQLite)
    
    Integration: Uses WorkingMemory.import_conversation() for real persistence.
    """
    
    def __init__(self, working_memory=None):
        """
        Initialize ConversationalChannelAdapter with real Tier 1 storage.
        
        Args:
            working_memory: Optional WorkingMemory instance. If None, creates default instance.
        
        Phase 2: Now uses real SQLite storage instead of mock list.
        """
        if working_memory is None:
            # Import here to avoid circular dependencies
            from ...tier1.working_memory import WorkingMemory
            working_memory = WorkingMemory()
        
        self.working_memory = working_memory
        logger.info("ConversationalChannelAdapter initialized (Tier 1 storage mode)")
    
    def store_conversation(
        self,
        conversation: Dict,
        source: str,
        quality_threshold: Optional[float] = None
    ) -> Dict:
        """
        Store conversation via WorkingMemory (real Tier 1 persistence).
        
        Args:
            conversation: Parsed conversation with semantic data
            source: Source identifier (e.g., "manual_import", "clipboard")
            quality_threshold: Minimum quality score (optional filter)
        
        Returns:
            Storage result dictionary with conversation_id
        
        Phase 2: Now uses WorkingMemory.import_conversation() for real persistence.
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
        
        # Transform conversation messages to import format
        messages = conversation.get("messages", [])
        
        # Pair user/assistant messages into conversation turns
        conversation_turns = []
        i = 0
        while i < len(messages):
            turn = {}
            
            # Get user message
            if i < len(messages) and messages[i]["role"] == "user":
                turn["user"] = messages[i]["content"]
                i += 1
            
            # Get assistant message
            if i < len(messages) and messages[i]["role"] == "assistant":
                turn["assistant"] = messages[i]["content"]
                i += 1
            
            # Only add turn if we have at least one message
            if turn:
                conversation_turns.append(turn)
        
        # Use WorkingMemory.import_conversation() for real persistence
        try:
            result = self.working_memory.import_conversation(
                conversation_turns=conversation_turns,
                import_source=source,
                workspace_path=None,  # Optional - could be passed in future
                import_date=datetime.now()
            )
            
            logger.info(
                f"Conversation stored in Tier 1: {result['conversation_id']} "
                f"(quality={result['quality_score']:.1f}, source={source})"
            )
            
            return {
                "conversation_id": result["conversation_id"],
                "stored": True,
                "storage_location": "tier1_working_memory",
                "message_count": len(messages),
                "quality_score": result["quality_score"]
            }
        
        except Exception as e:
            logger.error(f"Failed to store conversation: {e}", exc_info=True)
            return {
                "conversation_id": None,
                "stored": False,
                "reason": f"storage_error: {str(e)}"
            }
    
    def retrieve_conversation(self, conversation_id: str) -> Optional[Dict]:
        """
        Retrieve conversation by ID from Tier 1 storage.
        
        Args:
            conversation_id: Conversation identifier
        
        Returns:
            Full conversation record with conversation_id and conversation, or None if not found
        
        Phase 2: Queries WorkingMemory SQLite database.
        """
        try:
            # Get conversation metadata
            conv = self.working_memory.get_conversation(conversation_id)
            if not conv:
                return None
            
            # Get messages
            messages = self.working_memory.get_messages(conversation_id)
            
            # Normalize message format for backward compatibility
            # Remove 'metadata' field if present and normalize timestamps
            normalized_messages = []
            for msg in messages:
                normalized_msg = {
                    "role": msg["role"],
                    "content": msg["content"],
                    "timestamp": msg.get("timestamp", ""),
                    "metadata": {}  # Always include empty metadata for compatibility
                }
                # Remove ISO 'T' separator and microseconds if present for compatibility
                if "T" in normalized_msg["timestamp"]:
                    # Convert '2025-11-15T08:01:37.155052' to '2025-11-15T08:01:37'
                    timestamp_str = normalized_msg["timestamp"]
                    # Keep the T but remove microseconds
                    if "." in timestamp_str:
                        normalized_msg["timestamp"] = timestamp_str.split(".")[0]
                
                normalized_messages.append(normalized_msg)
            
            # Parse semantic elements from JSON
            semantic_elements = {}
            if hasattr(conv, 'semantic_elements') and conv.semantic_elements:
                try:
                    semantic_elements = json.loads(conv.semantic_elements)
                except json.JSONDecodeError:
                    semantic_elements = {}
            
            # Reconstruct format for backward compatibility
            return {
                "conversation_id": conversation_id,
                "source": conv.import_source if hasattr(conv, 'import_source') else "unknown",
                "stored_at": conv.created_at.isoformat() if hasattr(conv.created_at, 'isoformat') else str(conv.created_at),
                "conversation": {
                    "messages": normalized_messages,
                    "semantic_data": semantic_elements,
                    "metadata": {
                        "message_count": len(normalized_messages),
                        "title": conv.title
                    }
                },
                "quality_score": conv.quality_score if hasattr(conv, 'quality_score') else 0.0
            }
        
        except Exception as e:
            logger.error(f"Failed to retrieve conversation {conversation_id}: {e}", exc_info=True)
            return None
    
    def query_by_quality(
        self,
        min_quality: float,
        max_quality: float = 10.0,
        limit: int = 10
    ) -> List[Dict]:
        """
        Query conversations by quality score range from Tier 1 storage.
        
        Args:
            min_quality: Minimum quality score
            max_quality: Maximum quality score
            limit: Maximum results to return
        
        Returns:
            List of conversation dictionaries
        
        Phase 2: Queries WorkingMemory SQLite with quality filters.
        """
        try:
            conn = sqlite3.connect(self.working_memory.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT conversation_id
                FROM conversations
                WHERE conversation_type = 'imported'
                  AND quality_score >= ?
                  AND quality_score <= ?
                ORDER BY quality_score DESC
                LIMIT ?
            """, (min_quality, max_quality, limit))
            
            results = []
            for row in cursor.fetchall():
                conv_id = row[0]
                record = self.retrieve_conversation(conv_id)
                if record and "conversation" in record:
                    results.append(record["conversation"])
            
            conn.close()
            return results
        
        except Exception as e:
            logger.error(f"Failed to query by quality: {e}", exc_info=True)
            return []
    
    def query_by_entities(
        self,
        entity_type: str,
        entity_value: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Query conversations mentioning specific entities from Tier 1 storage.
        
        Args:
            entity_type: Entity type (file, class, function)
            entity_value: Entity value to search for
            limit: Maximum results
        
        Returns:
            List of matching conversations
        
        Phase 2: Queries WorkingMemory SQLite with entity filters.
        """
        try:
            conn = sqlite3.connect(self.working_memory.db_path)
            cursor = conn.cursor()
            
            # Query semantic_elements JSON column
            cursor.execute("""
                SELECT conversation_id, semantic_elements
                FROM conversations
                WHERE conversation_type = 'imported'
                ORDER BY created_at DESC
            """)
            
            results = []
            for row in cursor.fetchall():
                conv_id, semantic_json = row
                
                # Parse semantic data
                try:
                    semantic_data = json.loads(semantic_json) if semantic_json else {}
                except json.JSONDecodeError:
                    semantic_data = {}
                
                entities = semantic_data.get("entities", [])
                
                # Check if entity matches
                for entity in entities:
                    if (entity.get("type") == entity_type and 
                        entity_value.lower() in str(entity.get("value", "")).lower()):
                        
                        record = self.retrieve_conversation(conv_id)
                        if record and "conversation" in record:
                            results.append(record["conversation"])
                            break
                
                if len(results) >= limit:
                    break
            
            conn.close()
            return results
        
        except Exception as e:
            logger.error(f"Failed to query by entities: {e}", exc_info=True)
            return []
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about stored conversations from Tier 1 storage.
        
        Returns:
            Statistics dictionary with conversation counts and quality distribution
        
        Phase 2: Queries WorkingMemory SQLite for real statistics.
        """
        try:
            conn = sqlite3.connect(self.working_memory.db_path)
            cursor = conn.cursor()
            
            # Query imported conversations only
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    AVG(quality_score) as avg_quality,
                    SUM(message_count) as total_messages
                FROM conversations
                WHERE conversation_type = 'imported'
            """)
            
            row = cursor.fetchone()
            total_conversations = row[0] if row else 0
            avg_quality = row[1] if row and row[1] else 0.0
            total_messages = row[2] if row and row[2] else 0
            
            # Count entities from semantic_elements
            cursor.execute("""
                SELECT semantic_elements
                FROM conversations
                WHERE conversation_type = 'imported'
            """)
            
            total_entities = 0
            quality_scores = []
            for row in cursor.fetchall():
                semantic_json = row[0]
                try:
                    semantic_data = json.loads(semantic_json) if semantic_json else {}
                except json.JSONDecodeError:
                    semantic_data = {}
                
                entities = semantic_data.get("entities", [])
                total_entities += len(entities)
                
                quality = semantic_data.get("quality_score", 0)
                if quality > 0:
                    quality_scores.append(quality)
            
            conn.close()
            
            return {
                "total_conversations": total_conversations,
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
        
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}", exc_info=True)
            return {
                "total_conversations": 0,
                "avg_quality_score": 0.0,
                "total_messages": 0,
                "total_entities": 0,
                "quality_distribution": {
                    "excellent (9-10)": 0,
                    "good (7-9)": 0,
                    "fair (5-7)": 0,
                    "poor (<5)": 0
                }
            }
    
    def _generate_conversation_id(self, conversation: Dict) -> str:
        """
        Generate unique conversation ID.
        
        Format: conv_YYYYMMDD_HHMMSS_<hash>
        
        Note: This method is deprecated in Phase 2 as WorkingMemory.import_conversation()
        generates its own IDs. Kept for backward compatibility.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Simple hash from first message
        messages = conversation.get("messages", [])
        if messages:
            first_msg = messages[0]["content"][:50]
            hash_val = abs(hash(first_msg)) % 10000
            return f"conv_{timestamp}_{hash_val:04d}"
        
        return f"conv_{timestamp}_0000"
