"""
CORTEX Tier 1 Context Formatter

Converts raw Tier 1 conversation data into LLM-friendly, token-efficient summaries.

Key Responsibilities:
- Format recent conversations into concise summaries (<500 tokens)
- Extract active entities (files, classes, methods) for pronoun resolution
- Resolve pronouns ("it", "that", "this") to actual entities
- Provide temporal context (when work was done)
- Identify current work context

Performance Target: <50ms formatting time

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import re
import logging

logger = logging.getLogger(__name__)


class ContextFormatter:
    """
    Formats Tier 1 conversation data into token-efficient LLM context
    
    Token Budget: <500 tokens per injection
    - Recent conversations: ~300 tokens (3-5 conversations)
    - Active entities: ~100 tokens
    - Current task: ~100 tokens
    """
    
    def __init__(self):
        """Initialize context formatter"""
        self.max_conversations = 5
        self.max_summary_length = 300  # characters per conversation
    
    def format_recent_conversations(self, conversations: List[Dict]) -> str:
        """
        Convert recent conversations into concise summary
        
        Args:
            conversations: List of conversation dicts from Tier 1
                [
                    {
                        'conversation_id': 'conv_123',
                        'summary': 'Added authentication system',
                        'created_at': '2025-11-17T14:30:00',
                        'entities': ['AuthService.cs', 'LoginController.cs'],
                        'intent': 'EXECUTE',
                        'status': 'in_progress'
                    },
                    ...
                ]
        
        Returns:
            Formatted string like:
            ---
            Recent Work Context (Last 5 Conversations):
            
            1. [2 hours ago] Added authentication system
               Files: AuthService.cs, LoginController.cs
               Status: In progress (Phase 2 of 4)
            
            2. [Yesterday] Fixed null reference bug
               Files: UserRepository.cs
               Status: Complete, tests passing
            ---
        """
        if not conversations:
            return "No recent conversation history."
        
        # Limit to max conversations
        conversations = conversations[:self.max_conversations]
        
        lines = ["---", "Recent Work Context (Last 5 Conversations):", ""]
        
        for idx, conv in enumerate(conversations, 1):
            # Calculate time ago
            time_ago = self._format_time_ago(conv.get('created_at'))
            
            # Get summary (truncate if needed)
            summary = conv.get('summary', 'No summary')
            if summary and len(summary) > self.max_summary_length:
                summary = summary[:self.max_summary_length] + "..."
            elif not summary:
                summary = "No summary"
            
            # Format entities
            entities = conv.get('entities', [])
            if entities is None:
                entities = []
            files = [e for e in entities if self._is_file(e)]
            files_str = ", ".join(files[:5]) if files else "None"
            
            # Status
            status = conv.get('status', 'unknown')
            status_display = self._format_status(status, conv)
            
            # Build conversation entry
            lines.append(f"{idx}. [{time_ago}] {summary}")
            lines.append(f"   Files: {files_str}")
            lines.append(f"   Status: {status_display}")
            lines.append("")
        
        lines.append("---")
        return "\n".join(lines)
    
    def extract_active_entities(self, conversations: List[Dict]) -> Dict[str, Any]:
        """
        Identify files/classes/methods actively being worked on
        
        Args:
            conversations: Recent conversations from Tier 1
        
        Returns:
            {
                'files': ['AuthService.cs', 'LoginController.cs'],
                'classes': ['AuthService', 'JwtTokenGenerator'],
                'methods': ['ValidateCredentials', 'GenerateToken'],
                'ui_components': ['FAB button', 'login form'],
                'current_task': 'Phase 2: JWT implementation',
                'most_recent_entity': 'AuthService.cs'  # For "it" resolution
            }
        """
        active_entities = {
            'files': [],
            'classes': [],
            'methods': [],
            'ui_components': [],
            'current_task': None,
            'most_recent_entity': None
        }
        
        if not conversations:
            return active_entities
        
        # Track entity frequency (more mentions = more active)
        entity_counts = {}
        
        for conv in conversations[:3]:  # Focus on last 3 conversations
            entities = conv.get('entities', [])
            
            for entity in entities:
                entity_counts[entity] = entity_counts.get(entity, 0) + 1
                
                # Categorize entity
                if self._is_file(entity):
                    if entity not in active_entities['files']:
                        active_entities['files'].append(entity)
                elif self._is_class(entity):
                    if entity not in active_entities['classes']:
                        active_entities['classes'].append(entity)
                elif self._is_method(entity):
                    if entity not in active_entities['methods']:
                        active_entities['methods'].append(entity)
                elif self._is_ui_component(entity):
                    if entity not in active_entities['ui_components']:
                        active_entities['ui_components'].append(entity)
        
        # Limit to most active (top 5 each)
        active_entities['files'] = active_entities['files'][:5]
        active_entities['classes'] = active_entities['classes'][:5]
        active_entities['methods'] = active_entities['methods'][:5]
        active_entities['ui_components'] = active_entities['ui_components'][:5]
        
        # Extract current task from most recent conversation
        if conversations:
            most_recent = conversations[0]
            active_entities['current_task'] = most_recent.get('summary', '')
            
            # Get most recent entity (for "it" resolution)
            recent_entities = most_recent.get('entities', [])
            if recent_entities:
                active_entities['most_recent_entity'] = recent_entities[0]
        
        return active_entities
    
    def resolve_pronouns(self, user_request: str, active_entities: Dict) -> str:
        """
        Resolve "it", "that", "this" to actual entities
        
        Args:
            user_request: User's request text
            active_entities: Dict from extract_active_entities()
        
        Returns:
            Modified request with pronouns resolved
        
        Examples:
            Input: "Make it purple"
            Active entities: {'most_recent_entity': 'FAB button'}
            Output: "Make the FAB button purple"
            
            Input: "Refactor that"
            Active entities: {'most_recent_entity': 'AuthService.cs'}
            Output: "Refactor AuthService.cs"
        """
        if not active_entities:
            return user_request
        
        # Get most recent entity for resolution
        most_recent = active_entities.get('most_recent_entity')
        if not most_recent:
            # Try to get any entity
            for entity_type in ['ui_components', 'files', 'classes', 'methods']:
                entities = active_entities.get(entity_type, [])
                if entities:
                    most_recent = entities[0]
                    break
        
        if not most_recent:
            return user_request  # No entities to resolve to
        
        # Pronoun patterns to match (case insensitive)
        pronoun_patterns = [
            (r'\bit\b', 'it'),
            (r'\bthat\b', 'that'),
            (r'\bthis\b', 'this'),
            (r'\bthe same\b', 'the same'),
            (r'\bthem\b', 'them')
        ]
        
        resolved = user_request
        
        for pattern, pronoun in pronoun_patterns:
            if re.search(pattern, resolved, re.IGNORECASE):
                # Determine article
                article = self._get_article(most_recent)
                
                # Replace pronoun with entity
                if pronoun in ['it', 'that', 'this', 'the same']:
                    replacement = f"{article}{most_recent}"
                else:  # them
                    replacement = most_recent
                
                resolved = re.sub(
                    pattern, 
                    replacement, 
                    resolved, 
                    count=1,  # Only replace first occurrence
                    flags=re.IGNORECASE
                )
                
                logger.info(f"Resolved pronoun '{pronoun}' to '{most_recent}'")
                break  # Only resolve first pronoun
        
        return resolved
    
    def format_context_summary(self, 
                               conversations: List[Dict],
                               active_entities: Dict,
                               include_header: bool = True) -> str:
        """
        Create complete context summary for display to user
        
        Args:
            conversations: Recent conversations
            active_entities: Extracted entities
            include_header: Whether to include emoji header
        
        Returns:
            Formatted summary string ready for display
        """
        lines = []
        
        if include_header:
            lines.append("🧠 **Context Loaded**")
            lines.append("")
        
        # Recent work
        if conversations:
            recent_summary = conversations[0].get('summary', 'No summary')
            lines.append("📚 **Recent Work:**")
            lines.append(f"   • {recent_summary}")
            
            if len(conversations) > 1:
                lines.append(f"   • Plus {len(conversations) - 1} earlier conversation(s)")
            lines.append("")
        
        # Active files
        files = active_entities.get('files', [])
        if files:
            lines.append("📄 **Active Files:**")
            for file in files[:3]:
                lines.append(f"   • {file}")
            lines.append("")
        
        # Current task
        current_task = active_entities.get('current_task')
        if current_task:
            lines.append("🎯 **Current Task:**")
            lines.append(f"   {current_task}")
            lines.append("")
        
        return "\n".join(lines)
    
    # Helper methods
    
    def _format_time_ago(self, timestamp_str: Optional[str]) -> str:
        """Format timestamp as human-readable 'time ago'"""
        if not timestamp_str:
            return "Unknown time"
        
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            now = datetime.now(timestamp.tzinfo)
            delta = now - timestamp
            
            if delta < timedelta(minutes=1):
                return "Just now"
            elif delta < timedelta(hours=1):
                minutes = int(delta.total_seconds() / 60)
                return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
            elif delta < timedelta(days=1):
                hours = int(delta.total_seconds() / 3600)
                return f"{hours} hour{'s' if hours != 1 else ''} ago"
            elif delta < timedelta(days=7):
                days = int(delta.total_seconds() / 86400)
                return f"{days} day{'s' if days != 1 else ''} ago"
            else:
                return timestamp.strftime("%Y-%m-%d")
        except Exception as e:
            logger.warning(f"Error parsing timestamp {timestamp_str}: {e}")
            return "Unknown time"
    
    def _format_status(self, status: str, conv: Dict) -> str:
        """Format conversation status for display"""
        if status is None:
            status = 'unknown'
        
        status_map = {
            'complete': 'Complete ✅',
            'in_progress': 'In progress 🔄',
            'blocked': 'Blocked ⛔',
            'planning': 'Planning 📋'
        }
        
        base_status = status_map.get(status.lower() if status else 'unknown', status.title() if status else 'Unknown')
        
        # Add phase info if available
        metadata = conv.get('metadata', {})
        phase_info = metadata.get('phase_info', '')
        if phase_info:
            base_status += f" ({phase_info})"
        
        return base_status
    
    def _is_file(self, entity: str) -> bool:
        """Check if entity is a file"""
        file_extensions = [
            '.cs', '.py', '.js', '.ts', '.jsx', '.tsx',
            '.java', '.cpp', '.h', '.css', '.html',
            '.yaml', '.json', '.xml', '.md'
        ]
        return any(entity.endswith(ext) for ext in file_extensions)
    
    def _is_method(self, entity: str) -> bool:
        """Check if entity is a method (has parentheses or specific patterns)"""
        if '(' in entity or ')' in entity:
            return True
        if self._is_file(entity):
            return False
        
        # Method patterns - check BEFORE class patterns
        # Common method prefixes
        method_prefixes = ['^Get[A-Z]', '^Set[A-Z]', '^Is[A-Z]', '^Has[A-Z]', 
                          '^Create[A-Z]', '^Delete[A-Z]', '^Update[A-Z]', '^Find[A-Z]']
        if any(re.match(pattern, entity) for pattern in method_prefixes):
            return True
        
        # Method patterns like "GetUserById"
        if re.match(r'^[A-Z][a-z]+By[A-Z]', entity):
            return True
        
        # camelCase pattern (starts with lowercase)
        if re.match(r'^[a-z][a-zA-Z0-9]*$', entity):
            return True
        
        return False
    
    def _is_class(self, entity: str) -> bool:
        """Check if entity is a class (PascalCase, no extension)"""
        if self._is_file(entity) or self._is_method(entity):
            return False
        # PascalCase pattern: starts with uppercase, has at least one lowercase
        # This handles both AuthService and JwtTokenGenerator
        return bool(re.match(r'^[A-Z][a-z]+([A-Z][a-z]*)*$', entity))
    
    def _is_ui_component(self, entity: str) -> bool:
        """Check if entity is a UI component"""
        ui_keywords = [
            'button', 'form', 'input', 'dialog', 'modal',
            'panel', 'menu', 'navbar', 'sidebar', 'tab',
            'card', 'dropdown', 'checkbox', 'radio'
        ]
        entity_lower = entity.lower()
        return any(keyword in entity_lower for keyword in ui_keywords)
    
    def _get_article(self, entity: str) -> str:
        """Get appropriate article for entity"""
        if self._is_file(entity):
            return ""  # Files don't need articles
        elif self._is_ui_component(entity):
            return "the "  # "the button", "the form"
        else:
            return ""  # Classes and methods typically no article
