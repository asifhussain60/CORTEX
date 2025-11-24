"""
CORTEX Operation: Resume Conversation
Resume previous conversation from new chat session

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import re
import logging

logger = logging.getLogger(__name__)


class ResumeConversationOperation:
    """
    Resume conversation from new chat session
    
    Features:
        - Keyword-based conversation search
        - Multiple match selection
        - Auto-resume for single matches
        - Planning document opening
        - Full context restoration
        - Next steps suggestions
    
    Usage:
        operation = ResumeConversationOperation(conversation_manager)
        result = operation.execute("resume authentication work")
    """
    
    def __init__(self, conversation_manager):
        """
        Initialize resume operation
        
        Args:
            conversation_manager: ConversationManager instance
        """
        self.conversation_manager = conversation_manager
    
    def execute(self, user_query: str) -> Dict[str, Any]:
        """
        Resume conversation based on user query
        
        Args:
            user_query: Natural language query (e.g., "resume authentication work")
            
        Returns:
            Resume context dictionary with:
                - action: 'resumed', 'select_conversation', or 'error'
                - conversation_id: ID of resumed conversation (if resumed)
                - title: Conversation title
                - summary: Generated summary
                - recent_messages: Last 5 messages
                - entities: Entities discussed
                - files: Files modified
                - next_steps: Suggested next steps
                - options: List of conversations to choose from (if select_conversation)
                - error: Error message (if error)
        """
        try:
            # Extract keywords from user query
            keywords = self._extract_keywords(user_query)
            
            # Search conversations
            results = self._search_conversations(keywords)
            
            if len(results) == 0:
                return {
                    "action": "error",
                    "error": f"No matching conversations found for '{user_query}'",
                    "suggestion": "Try different keywords or check active conversations with 'list conversations'"
                }
            
            if len(results) == 1:
                # Only one match - auto-resume
                return self._resume(results[0])
            
            # Multiple matches - present options
            return {
                "action": "select_conversation",
                "query": user_query,
                "match_count": len(results),
                "options": [
                    {
                        "conversation_id": r["conversation_id"],
                        "title": r["goal"] or "Untitled Conversation",
                        "started": r["start_time"],
                        "status": r["status"],
                        "message_count": r["message_count"],
                        "entities": self._get_entities_preview(r["conversation_id"])
                    }
                    for r in results[:10]  # Limit to 10 options
                ]
            }
            
        except Exception as e:
            logger.error(f"Error executing resume operation: {e}", exc_info=True)
            return {
                "action": "error",
                "error": f"Failed to resume conversation: {str(e)}"
            }
    
    def resume_by_id(self, conversation_id: str) -> Dict[str, Any]:
        """
        Resume specific conversation by ID
        
        Args:
            conversation_id: Conversation ID to resume
            
        Returns:
            Resume context dictionary
        """
        try:
            conversation = self.conversation_manager.get_conversation(conversation_id)
            if not conversation:
                return {
                    "action": "error",
                    "error": f"Conversation not found: {conversation_id}"
                }
            
            return self._resume(conversation)
            
        except Exception as e:
            logger.error(f"Error resuming conversation {conversation_id}: {e}", exc_info=True)
            return {
                "action": "error",
                "error": f"Failed to resume conversation: {str(e)}"
            }
    
    def _resume(self, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resume specific conversation (internal)
        
        Args:
            conversation: Conversation dictionary from database
            
        Returns:
            Resume context with full details
        """
        conversation_id = conversation["conversation_id"]
        
        # Load full conversation details
        full_context = self.conversation_manager.get_conversation(conversation_id)
        
        # Get planning document path (if exists)
        import json
        context = json.loads(full_context.get('context', '{}')) if full_context.get('context') else {}
        planning_doc = context.get('planning_doc')
        
        # Prepare resume context
        return {
            "action": "resumed",
            "conversation_id": conversation_id,
            "title": full_context.get("goal", "Untitled Conversation"),
            "summary": self._generate_summary(full_context),
            "started": full_context.get("start_time"),
            "status": full_context.get("status"),
            "message_count": full_context.get("message_count", 0),
            "recent_messages": full_context["messages"][-5:] if full_context.get("messages") else [],
            "entities": full_context.get("entities", []),
            "files": full_context.get("files", []),
            "next_steps": self._suggest_next_steps(full_context),
            "planning_doc": planning_doc,
            "outcome": full_context.get("outcome")
        }
    
    def _extract_keywords(self, user_query: str) -> List[str]:
        """
        Extract search keywords from user query
        
        Args:
            user_query: Natural language query
            
        Returns:
            List of keywords for search
        """
        # Remove common resume command words
        stop_words = {'resume', 'continue', 'our', 'my', 'the', 'work', 'on', 'from', 'last', 'previous'}
        
        # Extract words
        words = re.findall(r'\w+', user_query.lower())
        
        # Filter stop words and short words
        keywords = [w for w in words if w not in stop_words and len(w) >= 3]
        
        return keywords
    
    def _search_conversations(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Search conversations by keywords
        
        Args:
            keywords: List of search keywords
            
        Returns:
            List of matching conversations (sorted by relevance)
        """
        # Build search query (simple keyword matching in goal/outcome)
        # For MVP: Search in conversation goal and outcome fields
        # Future: Use FTS5 or semantic search
        
        all_conversations = self.conversation_manager.get_recent_conversations(limit=50)
        
        # Score conversations by keyword matches
        scored_conversations = []
        for conv in all_conversations:
            score = 0
            searchable_text = (
                (conv.get('title', '') or '') + ' ' +
                (conv.get('outcome', '') or '')
            ).lower()
            
            for keyword in keywords:
                if keyword in searchable_text:
                    score += 1
            
            if score > 0:
                scored_conversations.append((score, conv))
        
        # Sort by score (descending)
        scored_conversations.sort(key=lambda x: x[0], reverse=True)
        
        # Return conversations only (without scores)
        return [conv for score, conv in scored_conversations]
    
    def _get_entities_preview(self, conversation_id: str) -> Dict[str, List[str]]:
        """
        Get preview of entities for a conversation
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Dictionary with entity types and values (limited)
        """
        entities = self.conversation_manager.get_entities(conversation_id)
        
        preview = {}
        for entity in entities[:10]:  # Limit to 10 entities
            entity_type = entity.get('entity_type', 'unknown')
            entity_value = entity.get('entity_value', '')
            
            if entity_type not in preview:
                preview[entity_type] = []
            
            if len(preview[entity_type]) < 5:  # Max 5 per type
                preview[entity_type].append(entity_value)
        
        return preview
    
    def _generate_summary(self, conversation: Dict[str, Any]) -> str:
        """
        Generate conversation summary
        
        Args:
            conversation: Conversation data
            
        Returns:
            Summary string
        """
        summary_parts = []
        
        # Basic info
        message_count = conversation.get('message_count', 0)
        summary_parts.append(f"Conversation with {message_count} messages")
        
        # Status
        status = conversation.get('status', 'unknown')
        if status == 'active':
            summary_parts.append("currently in progress")
        elif status == 'completed':
            summary_parts.append("completed")
        
        # Entities
        entities = conversation.get('entities', [])
        if entities:
            entity_count = len(entities)
            summary_parts.append(f"{entity_count} entities discussed")
        
        # Files
        files = conversation.get('files', [])
        if files:
            file_count = len(files)
            summary_parts.append(f"{file_count} files modified")
        
        return ", ".join(summary_parts) + "."
    
    def _suggest_next_steps(self, conversation: Dict[str, Any]) -> List[str]:
        """
        Suggest next steps based on conversation state
        
        Args:
            conversation: Conversation data
            
        Returns:
            List of suggested next steps
        """
        next_steps = []
        
        status = conversation.get('status', 'unknown')
        
        if status == 'active':
            # Active conversation - continue work
            next_steps.append("Continue where you left off")
            
            entities = conversation.get('entities', [])
            if entities:
                recent_entity = entities[0].get('entity_value', '')
                next_steps.append(f"Review recent discussion about '{recent_entity}'")
            
            files = conversation.get('files', [])
            if files:
                recent_file = files[0].get('file_path', '')
                next_steps.append(f"Review changes to `{recent_file}`")
        
        elif status == 'completed':
            # Completed conversation - review or extend
            next_steps.append("Review completed conversation")
            next_steps.append("Start new related conversation if needed")
            
            outcome = conversation.get('outcome')
            if outcome:
                next_steps.append(f"Outcome: {outcome}")
        
        else:
            # Unknown status
            next_steps.append("Review conversation details")
            next_steps.append("Determine next actions")
        
        return next_steps[:5]  # Limit to 5 next steps
