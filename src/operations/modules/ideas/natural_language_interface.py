"""
CORTEX 3.0 - Feature 1: IDEA Capture System - Natural Language Interface

Purpose: Natural language processing for IDEA capture commands integrated
         with CORTEX's Intent Router and Response Template system.

Architecture:
- Pattern recognition: "idea:", "remember:", "task:", "note:"
- Context extraction: Current file, conversation, operation
- Intent routing: Capture vs. retrieval vs. management
- Response templates: User-friendly feedback and confirmation

Integration Points:
- Intent Router: Extends with IDEA-specific patterns
- Response Templates: IDEA capture and management responses
- Context Provider: Active file, line, operation tracking

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

from src.operations.modules.ideas.idea_queue import IdeaQueue, IdeaCapture


logger = logging.getLogger(__name__)


@dataclass
class IdeaCommand:
    """Parsed idea command with intent and parameters."""
    command_type: str                    # capture, show, work, complete, delete
    raw_input: str                      # Original user input
    idea_text: Optional[str] = None     # Text to capture
    idea_id: Optional[str] = None       # ID for management commands
    filter_type: Optional[str] = None   # component, project, priority
    filter_value: Optional[str] = None  # auth, CORTEX, high, etc.
    priority: Optional[str] = None      # For priority updates


class IdeaNaturalLanguageInterface:
    """
    Natural language interface for IDEA capture system.
    
    Recognizes patterns like:
    - "idea: add rate limiting"
    - "remember: fix the bug in auth"
    - "task: update documentation"
    - "show ideas"
    - "show auth ideas" 
    - "work on idea 5"
    - "complete idea 3"
    """
    
    def __init__(self, idea_queue: Optional[IdeaQueue] = None):
        """
        Initialize natural language interface.
        
        Args:
            idea_queue: IdeaQueue instance (creates default if None)
        """
        self.idea_queue = idea_queue or IdeaQueue()
        
        # Capture patterns (high priority for instant recognition)
        self.capture_patterns = [
            r'^(idea|remember|task|note):\s*(.+)$',
            r'^(save|capture)\s+(idea|thought):\s*(.+)$',
            r'^(add to ideas?|note this):\s*(.+)$',
        ]
        
        # Management patterns
        self.management_patterns = [
            r'^show\s+(all\s+)?ideas?$',
            r'^show\s+(\w+)\s+ideas?$',                    # show auth ideas
            r'^show\s+idea\s+(\w+)$',                       # show idea 5
            r'^show\s+(high|medium|low)\s+priority$',       # show high priority
            r'^work\s+on\s+idea\s+(\w+)$',                 # work on idea 5
            r'^complete\s+idea\s+(\w+)$',                   # complete idea 3
            r'^delete\s+idea\s+(\w+)$',                     # delete idea 7
            r'^prioritize\s+idea\s+(\w+)\s+(high|medium|low)$'  # prioritize idea 2 high
        ]
        
        # Context keywords for better component detection
        self.component_keywords = {
            'auth': ['auth', 'authentication', 'login', 'password', 'token', 'security'],
            'api': ['api', 'endpoint', 'route', 'request', 'response', 'service'],
            'ui': ['ui', 'interface', 'component', 'button', 'form', 'modal'],
            'testing': ['test', 'spec', 'coverage', 'unit test', 'integration'],
            'docs': ['doc', 'documentation', 'readme', 'guide', 'manual']
        }
        
        logger.info("IdeaNaturalLanguageInterface initialized")
    
    def process_input(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process user input for IDEA-related commands.
        
        Args:
            user_input: Raw user input text
            context: Optional context (active file, conversation, etc.)
            
        Returns:
            Dict with processing results:
            - handled: bool (whether this was an IDEA command)
            - command: IdeaCommand object (if handled)
            - response: str (user-friendly response)
            - idea_id: str (if idea was captured)
        """
        start_time = datetime.now()
        
        try:
            # Parse command
            command = self._parse_command(user_input.strip())
            
            if not command:
                return {
                    'handled': False,
                    'command': None,
                    'response': '',
                    'idea_id': None
                }
            
            # Execute command
            result = self._execute_command(command, context)
            
            # Performance tracking
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            if command.command_type == 'capture' and processing_time > 10.0:
                logger.warning(f"Capture processing took {processing_time:.1f}ms")
            
            logger.debug(f"Processed IDEA command '{command.command_type}' in {processing_time:.1f}ms")
            
            return {
                'handled': True,
                'command': command,
                'response': result['response'],
                'idea_id': result.get('idea_id'),
                'ideas': result.get('ideas'),
                'processing_time_ms': processing_time
            }
        
        except Exception as e:
            logger.error(f"Failed to process IDEA input '{user_input}': {e}")
            return {
                'handled': False,
                'command': None,
                'response': f"Error processing idea command: {e}",
                'idea_id': None
            }
    
    def _parse_command(self, user_input: str) -> Optional[IdeaCommand]:
        """Parse user input into IdeaCommand."""
        input_lower = user_input.lower()
        
        # Check capture patterns first (most common, need fastest recognition)
        for pattern in self.capture_patterns:
            match = re.match(pattern, input_lower, re.IGNORECASE)
            if match:
                if len(match.groups()) == 2:
                    # Pattern: "idea: text" - extract original case text
                    original_match = re.match(pattern, user_input, re.IGNORECASE)
                    return IdeaCommand(
                        command_type='capture',
                        raw_input=user_input,
                        idea_text=original_match.group(2).strip()
                    )
                elif len(match.groups()) == 3:
                    # Pattern: "save idea: text" - extract original case text
                    original_match = re.match(pattern, user_input, re.IGNORECASE)
                    return IdeaCommand(
                        command_type='capture',
                        raw_input=user_input,
                        idea_text=original_match.group(3).strip()
                    )
        
        # Check management patterns
        for pattern in self.management_patterns:
            match = re.match(pattern, input_lower, re.IGNORECASE)
            if match:
                return self._parse_management_command(match, user_input)
        
        return None
    
    def _parse_management_command(self, match, raw_input: str) -> IdeaCommand:
        """Parse management command from regex match."""
        groups = match.groups()
        matched_text = match.group(0)
        
        # Determine command type based on matched text
        if 'show' in matched_text.lower():
            # Check for specific idea ID pattern like "show idea abc123"
            if 'idea ' in matched_text.lower() and len(groups) >= 1 and groups[0]:
                return IdeaCommand(
                    command_type='show',
                    raw_input=raw_input,
                    idea_id=groups[0].strip()
                )
            # Check for priority filter like "show high priority"
            elif 'priority' in matched_text.lower() and len(groups) >= 1 and groups[0]:
                return IdeaCommand(
                    command_type='show',
                    raw_input=raw_input,
                    filter_type='priority',
                    filter_value=groups[0].strip()
                )
            # Check for component filter like "show auth ideas"
            elif len(groups) >= 1 and groups[0] and groups[0].strip() not in ['all', '']:
                return IdeaCommand(
                    command_type='show',
                    raw_input=raw_input,
                    filter_type='component',
                    filter_value=groups[0].strip()
                )
            # Default "show ideas" or "show all ideas"
            else:
                return IdeaCommand(
                    command_type='show',
                    raw_input=raw_input
                )
        
        elif 'work' in matched_text.lower() and 'on' in matched_text.lower():
            idea_id = groups[0].strip() if groups and groups[0] else None
            return IdeaCommand(
                command_type='work',
                raw_input=raw_input,
                idea_id=idea_id
            )
        
        elif 'complete' in matched_text.lower():
            idea_id = groups[0].strip() if groups and groups[0] else None
            return IdeaCommand(
                command_type='complete',
                raw_input=raw_input,
                idea_id=idea_id
            )
        
        elif 'delete' in matched_text.lower():
            idea_id = groups[0].strip() if groups and groups[0] else None
            return IdeaCommand(
                command_type='delete',
                raw_input=raw_input,
                idea_id=idea_id
            )
        
        elif 'prioritize' in matched_text.lower():
            idea_id = groups[0].strip() if groups and groups[0] else None
            priority = groups[1].strip() if len(groups) > 1 and groups[1] else None
            return IdeaCommand(
                command_type='prioritize',
                raw_input=raw_input,
                idea_id=idea_id,
                priority=priority
            )
        
        # Default fallback
        return IdeaCommand(
            command_type='unknown',
            raw_input=raw_input
        )
    
    def _execute_command(
        self,
        command: IdeaCommand,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute parsed command."""
        
        if command.command_type == 'capture':
            return self._execute_capture(command, context)
        
        elif command.command_type == 'show':
            return self._execute_show(command)
        
        elif command.command_type == 'work':
            return self._execute_work(command)
        
        elif command.command_type == 'complete':
            return self._execute_complete(command)
        
        elif command.command_type == 'delete':
            return self._execute_delete(command)
        
        elif command.command_type == 'prioritize':
            return self._execute_prioritize(command)
        
        else:
            return {
                'response': f"Unknown command type: {command.command_type}",
                'success': False
            }
    
    def _execute_capture(
        self,
        command: IdeaCommand,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute idea capture."""
        try:
            idea_id = self.idea_queue.capture(
                raw_text=command.idea_text,
                context=context
            )
            
            # Generate user-friendly response
            response = f"✅ Captured idea #{idea_id}: \"{command.idea_text}\""
            
            # Add context hint if available
            if context:
                if context.get('active_file'):
                    response += f"\n📁 Context: {context['active_file']}"
                if context.get('active_operation'):
                    response += f" ({context['active_operation']})"
            
            return {
                'response': response,
                'success': True,
                'idea_id': idea_id
            }
        
        except Exception as e:
            logger.error(f"Capture failed: {e}")
            return {
                'response': f"❌ Failed to capture idea: {e}",
                'success': False
            }
    
    def _execute_show(self, command: IdeaCommand) -> Dict[str, Any]:
        """Execute show command."""
        try:
            if command.idea_id:
                # Show specific idea
                idea = self.idea_queue.get_idea(command.idea_id)
                if not idea:
                    return {
                        'response': f"❌ Idea #{command.idea_id} not found",
                        'success': False
                    }
                
                response = self._format_single_idea(idea)
                return {
                    'response': response,
                    'success': True,
                    'ideas': [idea]
                }
            
            else:
                # Show filtered ideas
                ideas = self._get_filtered_ideas(command)
                response = self._format_ideas_list(ideas, command)
                return {
                    'response': response,
                    'success': True,
                    'ideas': ideas
                }
        
        except Exception as e:
            logger.error(f"Show command failed: {e}")
            return {
                'response': f"❌ Failed to show ideas: {e}",
                'success': False
            }
    
    def _execute_work(self, command: IdeaCommand) -> Dict[str, Any]:
        """Execute work on idea command."""
        try:
            idea = self.idea_queue.get_idea(command.idea_id)
            if not idea:
                return {
                    'response': f"❌ Idea #{command.idea_id} not found",
                    'success': False
                }
            
            # TODO: Integration with CORTEX 2.1 Interactive Planning
            response = f"""💡 **Idea #{idea.idea_id}: {idea.raw_text}**

🎯 **Ready to plan implementation?**

This will start CORTEX Interactive Planning to break down this idea into actionable steps.

**Next Steps:**
1. Type "yes" to start planning session
2. Type "later" to save for later planning  
3. Type "show context" to see related ideas

*Note: Planning integration with CORTEX 2.1 coming soon*"""
            
            return {
                'response': response,
                'success': True,
                'ideas': [idea]
            }
        
        except Exception as e:
            logger.error(f"Work command failed: {e}")
            return {
                'response': f"❌ Failed to start work on idea: {e}",
                'success': False
            }
    
    def _execute_complete(self, command: IdeaCommand) -> Dict[str, Any]:
        """Execute complete idea command."""
        try:
            success = self.idea_queue.complete_idea(command.idea_id)
            
            if success:
                idea = self.idea_queue.get_idea(command.idea_id)
                response = f"✅ Completed idea #{command.idea_id}: \"{idea.raw_text if idea else 'Unknown'}\""
                return {
                    'response': response,
                    'success': True
                }
            else:
                return {
                    'response': f"❌ Idea #{command.idea_id} not found",
                    'success': False
                }
        
        except Exception as e:
            logger.error(f"Complete command failed: {e}")
            return {
                'response': f"❌ Failed to complete idea: {e}",
                'success': False
            }
    
    def _execute_delete(self, command: IdeaCommand) -> Dict[str, Any]:
        """Execute delete idea command."""
        try:
            success = self.idea_queue.archive_idea(command.idea_id)  # Archive instead of delete
            
            if success:
                return {
                    'response': f"🗑️ Archived idea #{command.idea_id}",
                    'success': True
                }
            else:
                return {
                    'response': f"❌ Idea #{command.idea_id} not found",
                    'success': False
                }
        
        except Exception as e:
            logger.error(f"Delete command failed: {e}")
            return {
                'response': f"❌ Failed to delete idea: {e}",
                'success': False
            }
    
    def _execute_prioritize(self, command: IdeaCommand) -> Dict[str, Any]:
        """Execute prioritize idea command."""
        try:
            success = self.idea_queue.update_priority(command.idea_id, command.priority)
            
            if success:
                priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}
                emoji = priority_emoji.get(command.priority, '⚪')
                
                return {
                    'response': f"{emoji} Updated idea #{command.idea_id} priority to {command.priority}",
                    'success': True
                }
            else:
                return {
                    'response': f"❌ Idea #{command.idea_id} not found",
                    'success': False
                }
        
        except Exception as e:
            logger.error(f"Prioritize command failed: {e}")
            return {
                'response': f"❌ Failed to update priority: {e}",
                'success': False
            }
    
    def _get_filtered_ideas(self, command: IdeaCommand) -> List[IdeaCapture]:
        """Get ideas based on filter criteria."""
        if command.filter_type == 'component' and command.filter_value:
            return self.idea_queue.filter_by_component(command.filter_value)
        
        elif command.filter_type == 'project' and command.filter_value:
            return self.idea_queue.filter_by_project(command.filter_value)
        
        elif command.filter_type == 'priority' and command.filter_value:
            all_ideas = self.idea_queue.get_all_ideas()
            return [idea for idea in all_ideas if idea.priority == command.filter_value]
        
        else:
            return self.idea_queue.get_all_ideas(status_filter='pending', limit=20)
    
    def _format_ideas_list(self, ideas: List[IdeaCapture], command: IdeaCommand) -> str:
        """Format list of ideas for display."""
        if not ideas:
            filter_desc = ""
            if command.filter_type and command.filter_value:
                filter_desc = f" for {command.filter_value}"
            return f"📭 No ideas found{filter_desc}"
        
        # Group by priority
        high_priority = [idea for idea in ideas if idea.priority == 'high']
        medium_priority = [idea for idea in ideas if idea.priority == 'medium']
        low_priority = [idea for idea in ideas if idea.priority == 'low']
        no_priority = [idea for idea in ideas if not idea.priority]
        
        response_parts = ["💡 **IDEA CAPTURE**", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"]
        
        # High priority ideas
        if high_priority:
            response_parts.append("\n🔴 **HIGH PRIORITY**")
            for idea in high_priority:
                response_parts.append(self._format_idea_line(idea))
        
        # Medium priority ideas  
        if medium_priority:
            response_parts.append("\n🟡 **MEDIUM PRIORITY**")
            for idea in medium_priority:
                response_parts.append(self._format_idea_line(idea))
        
        # Low priority ideas
        if low_priority:
            response_parts.append("\n🟢 **LOW PRIORITY**")
            for idea in low_priority:
                response_parts.append(self._format_idea_line(idea))
        
        # Ideas without priority
        if no_priority:
            response_parts.append("\n⚪ **NEEDS PRIORITIZATION**")
            for idea in no_priority:
                response_parts.append(self._format_idea_line(idea))
        
        # Commands help
        response_parts.extend([
            "\n**Commands:**",
            "• \"work on idea {id}\" - Start planning",
            "• \"complete idea {id}\" - Mark done",
            "• \"show {component} ideas\" - Filter",
            "• \"prioritize idea {id} high\" - Update priority"
        ])
        
        return "\n".join(response_parts)
    
    def _format_idea_line(self, idea: IdeaCapture) -> str:
        """Format single idea for list display."""
        # Truncate long text
        text = idea.raw_text
        if len(text) > 80:
            text = text[:77] + "..."
        
        line = f"{idea.idea_id}. [ ] {text}"
        
        # Add component info
        if idea.component:
            line += f" `{idea.component}`"
        
        # Add context hint
        if idea.active_file:
            file_name = idea.active_file.split('/')[-1]
            line += f" 📁{file_name}"
        
        return line
    
    def _format_single_idea(self, idea: IdeaCapture) -> str:
        """Format single idea for detailed display."""
        priority_emoji = {
            'high': '🔴',
            'medium': '🟡', 
            'low': '🟢'
        }
        
        emoji = priority_emoji.get(idea.priority, '⚪')
        
        response = f"""💡 **Idea #{idea.idea_id}**

{emoji} **{idea.raw_text}**

**Details:**
• Status: {idea.status}
• Created: {idea.timestamp.strftime('%Y-%m-%d %H:%M')}"""
        
        if idea.priority:
            response += f"\n• Priority: {idea.priority}"
        
        if idea.component:
            response += f"\n• Component: {idea.component}"
        
        if idea.project:
            response += f"\n• Project: {idea.project}"
        
        if idea.active_file:
            response += f"\n• Context: {idea.active_file}"
            if idea.active_line:
                response += f" (line {idea.active_line})"
        
        if idea.active_operation:
            response += f"\n• Operation: {idea.active_operation}"
        
        if idea.related_ideas:
            response += f"\n• Related: {', '.join(idea.related_ideas)}"
        
        response += "\n\n**Actions:** work on | complete | delete | prioritize"
        
        return response


def create_idea_interface(config: Optional[Dict[str, Any]] = None) -> IdeaNaturalLanguageInterface:
    """
    Factory function to create IdeaNaturalLanguageInterface.
    
    Args:
        config: Optional configuration dict
            - idea_queue: IdeaQueue instance (optional)
            
    Returns:
        Configured IdeaNaturalLanguageInterface instance
    """
    if not config:
        config = {}
    
    idea_queue = config.get('idea_queue')
    
    return IdeaNaturalLanguageInterface(idea_queue=idea_queue)