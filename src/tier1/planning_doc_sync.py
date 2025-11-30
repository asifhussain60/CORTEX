"""
CORTEX Tier 1: Planning Document Sync Engine
Auto-synchronizes SQLite conversation state to markdown planning documents

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import logging

logger = logging.getLogger(__name__)


class PlanningDocSyncEngine:
    """
    Synchronizes SQLite conversation state to markdown planning documents
    
    Architecture:
        SQLite (Source of Truth) → Sync Engine → Markdown (User Projection)
    
    Features:
        - Template-based rendering (Jinja2)
        - Auto-sync on conversation events
        - Progress tracking
        - Entity summaries
        - Recent message history
    
    Usage:
        sync_engine = PlanningDocSyncEngine()
        sync_engine.sync_planning_doc(conversation_id="conv-001")
    """
    
    def __init__(self, template_dir: Optional[Path] = None):
        """
        Initialize sync engine with template directory
        
        Args:
            template_dir: Directory containing Jinja2 templates
                         (default: cortex-brain/templates/planning)
        """
        if template_dir is None:
            project_root = Path(__file__).parent.parent.parent
            template_dir = project_root / "cortex-brain" / "templates" / "planning"
        
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=False,  # Markdown doesn't need HTML escaping
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters
        self.jinja_env.filters['format_datetime'] = self._format_datetime
        self.jinja_env.filters['progress_percentage'] = self._progress_percentage
        self.jinja_env.filters['truncate_content'] = self._truncate_content
    
    def sync_planning_doc(
        self,
        conversation_id: str,
        conversation_manager,
        force: bool = False
    ) -> Optional[Path]:
        """
        Regenerate planning document from SQLite conversation state
        
        Args:
            conversation_id: Conversation to sync
            conversation_manager: ConversationManager instance
            force: Force regeneration even if unchanged
            
        Returns:
            Path to generated planning document or None if no planning doc associated
        """
        try:
            # Load conversation from SQLite
            conversation = conversation_manager.get_conversation(conversation_id)
            if not conversation:
                logger.warning(f"Conversation not found: {conversation_id}")
                return None
            
            # Check if conversation has planning document
            context = json.loads(conversation.get('context', '{}')) if conversation.get('context') else {}
            planning_doc_path = context.get('planning_doc')
            
            if not planning_doc_path:
                logger.debug(f"No planning document for conversation: {conversation_id}")
                return None
            
            planning_doc_path = Path(planning_doc_path)
            
            # Check if sync needed (unless forced)
            if not force and planning_doc_path.exists():
                # Check if conversation modified after last sync
                last_sync = context.get('last_sync')
                if last_sync:
                    # Simple check: if no new messages since last sync, skip
                    # (More sophisticated: compare timestamps)
                    pass  # For MVP, always sync
            
            # Load planning session (if exists)
            session_id = context.get('session_id')
            session = None
            if session_id:
                session = conversation_manager.load_planning_session(session_id)
            
            # Calculate progress
            progress = self._calculate_progress(conversation, session)
            
            # Get entity summary
            entities_summary = self._get_entities_summary(conversation_id, conversation_manager)
            
            # Prepare template context
            template_context = {
                'conversation': conversation,
                'session': session,
                'progress': progress,
                'entities': entities_summary,
                'sync_time': datetime.now(),
                'conversation_id': conversation_id
            }
            
            # Render template
            markdown = self._render_template('feature_planning.md.jinja', template_context)
            
            # Write to file
            planning_doc_path.parent.mkdir(parents=True, exist_ok=True)
            planning_doc_path.write_text(markdown, encoding='utf-8')
            
            # Update last_sync timestamp in conversation context
            context['last_sync'] = datetime.now().isoformat()
            conversation_manager._update_conversation_context(conversation_id, context)
            
            logger.info(f"Synced planning document: {planning_doc_path}")
            return planning_doc_path
            
        except Exception as e:
            logger.error(f"Error syncing planning document for {conversation_id}: {e}", exc_info=True)
            return None
    
    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render Jinja2 template with context
        
        Args:
            template_name: Template filename
            context: Template variables
            
        Returns:
            Rendered markdown content
        """
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**context)
        except TemplateNotFound:
            logger.error(f"Template not found: {template_name}")
            # Return basic markdown if template missing
            return self._render_basic_markdown(context)
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {e}", exc_info=True)
            return self._render_basic_markdown(context)
    
    def _render_basic_markdown(self, context: Dict[str, Any]) -> str:
        """
        Fallback: Render basic markdown without template
        
        Args:
            context: Template variables
            
        Returns:
            Basic markdown content
        """
        conversation = context['conversation']
        progress = context.get('progress', {})
        
        markdown = f"""# {conversation.get('goal', 'Planning Session')}

**Conversation ID:** {context['conversation_id']}  
**Started:** {conversation.get('start_time', 'Unknown')}  
**Status:** {conversation.get('status', 'unknown')}  
**Progress:** {progress.get('completed', 0)}/{progress.get('total', 0)} tasks

---

## 📋 Planning Information

This planning document is auto-generated from conversation state.

**Message Count:** {conversation.get('message_count', 0)}  
**Last Updated:** {context['sync_time'].strftime('%Y-%m-%d %H:%M:%S')}

---

*Auto-generated by CORTEX Planning Doc Sync Engine*  
*Template: feature_planning.md.jinja (not found, using fallback)*
"""
        return markdown
    
    def _calculate_progress(
        self,
        conversation: Dict[str, Any],
        session: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate conversation/planning progress
        
        Args:
            conversation: Conversation data
            session: Planning session data (optional)
            
        Returns:
            Progress dictionary with completed/total/percentage
        """
        progress = {
            'total': 0,
            'completed': 0,
            'percentage': 0,
            'status': conversation.get('status', 'unknown')
        }
        
        if session:
            # Count questions answered
            questions = session.get('questions', [])
            answers = session.get('answers', [])
            
            answered_question_ids = {a['question_id'] for a in answers if not a.get('skipped', False)}
            
            progress['total'] = len(questions)
            progress['completed'] = len(answered_question_ids)
            
            if progress['total'] > 0:
                progress['percentage'] = int((progress['completed'] / progress['total']) * 100)
        
        return progress
    
    def _get_entities_summary(
        self,
        conversation_id: str,
        conversation_manager
    ) -> Dict[str, List[str]]:
        """
        Get summary of entities discussed in conversation
        
        Args:
            conversation_id: Conversation ID
            conversation_manager: ConversationManager instance
            
        Returns:
            Dictionary with entity types as keys, unique values as lists
        """
        entities = conversation_manager.get_entities(conversation_id)
        
        summary = {}
        for entity in entities:
            entity_type = entity.get('entity_type', 'unknown')
            entity_value = entity.get('entity_value', '')
            
            if entity_type not in summary:
                summary[entity_type] = []
            
            if entity_value not in summary[entity_type]:
                summary[entity_type].append(entity_value)
        
        return summary
    
    # Custom Jinja2 filters
    
    @staticmethod
    def _format_datetime(value: Any, format: str = '%Y-%m-%d %H:%M:%S') -> str:
        """Format datetime string"""
        if not value:
            return 'N/A'
        
        if isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                return dt.strftime(format)
            except:
                return value
        
        if isinstance(value, datetime):
            return value.strftime(format)
        
        return str(value)
    
    @staticmethod
    def _progress_percentage(progress: Dict[str, Any]) -> int:
        """Calculate progress percentage"""
        return progress.get('percentage', 0)
    
    @staticmethod
    def _truncate_content(content: str, max_length: int = 200) -> str:
        """Truncate content with ellipsis"""
        if not content:
            return ''
        
        if len(content) <= max_length:
            return content
        
        return content[:max_length] + '...'
