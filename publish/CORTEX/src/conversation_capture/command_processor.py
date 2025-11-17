"""
CORTEX 3.0 - Conversation Capture Commands
==========================================

Natural language command interface for manual conversation capture.
Integrates with CORTEX prompt system for seamless user experience.

Commands:
- "capture conversation" → Create capture file
- "import conversation [capture_id]" → Import conversation to brain
- "list captures" → Show active capture files
- "capture status [capture_id]" → Check specific capture

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Feature: Quick Win #5.1 (Week 2) - Command Interface
Effort: 4 hours (command integration)
Target: Natural language interface for capture workflow
"""

from typing import Dict, Any, Optional, List
import re
from pathlib import Path

from .capture_manager import ConversationCaptureManager


class CaptureCommandProcessor:
    """
    Processes natural language commands for conversation capture.
    
    Integrates with CORTEX response template system to provide
    intelligent routing and helpful responses.
    """
    
    def __init__(self, brain_path: str, workspace_root: str):
        self.brain_path = brain_path
        self.workspace_root = workspace_root
        self.capture_manager = ConversationCaptureManager(brain_path, workspace_root)
        
        # Command patterns
        self.command_patterns = {
            'capture': [
                r'capture\s+conversation',
                r'create\s+capture',
                r'start\s+capture',
                r'capture\s+(this\s+)?chat',
                r'/cortex\s+capture'
            ],
            'import': [
                r'import\s+conversation\s+(\w+)',
                r'import\s+capture\s+(\w+)',
                r'process\s+capture\s+(\w+)',
                r'/cortex\s+import\s+(\w+)'
            ],
            'list_captures': [
                r'list\s+captures?',
                r'show\s+captures?',
                r'active\s+captures?',
                r'capture\s+files?'
            ],
            'capture_status': [
                r'capture\s+status\s+(\w+)',
                r'check\s+capture\s+(\w+)',
                r'status\s+of\s+(\w+)'
            ]
        }
    
    def initialize(self) -> bool:
        """Initialize the capture command processor"""
        return self.capture_manager.initialize()
    
    def process_command(self, user_input: str) -> Dict[str, Any]:
        """
        Process natural language command for conversation capture
        
        Args:
            user_input: User's natural language input
            
        Returns:
            Dict with command result and response
        """
        user_input = user_input.strip().lower()
        
        # Match against command patterns
        command_match = self._match_command_pattern(user_input)
        
        if not command_match:
            return {
                'handled': False,
                'suggestion': 'Try: "capture conversation", "import conversation [id]", or "list captures"'
            }
        
        command_type = command_match['command']
        params = command_match['params']
        
        try:
            if command_type == 'capture':
                return self._handle_capture_command(params)
            elif command_type == 'import':
                return self._handle_import_command(params)
            elif command_type == 'list_captures':
                return self._handle_list_captures_command()
            elif command_type == 'capture_status':
                return self._handle_status_command(params)
            else:
                return {
                    'handled': False,
                    'error': f'Unknown command type: {command_type}'
                }
                
        except Exception as e:
            return {
                'handled': True,
                'success': False,
                'error': f'Command processing failed: {str(e)}',
                'suggestion': 'Please check logs for detailed error information'
            }
    
    def _match_command_pattern(self, user_input: str) -> Optional[Dict[str, Any]]:
        """Match user input against command patterns"""
        for command_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, user_input, re.IGNORECASE)
                if match:
                    params = {}
                    if match.groups():
                        if command_type in ['import', 'capture_status']:
                            params['capture_id'] = match.group(1)
                        elif command_type == 'capture':
                            # Extract optional hint from input
                            hint_match = re.search(r'about\s+(.*)', user_input, re.IGNORECASE)
                            if hint_match:
                                params['hint'] = hint_match.group(1)
                    
                    return {
                        'command': command_type,
                        'params': params,
                        'matched_pattern': pattern
                    }
        return None
    
    def _handle_capture_command(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle capture conversation command"""
        user_hint = params.get('hint', '')
        result = self.capture_manager.create_capture_file(user_hint)
        
        if result['success']:
            return {
                'handled': True,
                'success': True,
                'operation': 'capture_created',
                'capture_id': result['capture_id'],
                'response': self._format_capture_success_response(result),
                'next_steps': [
                    f"Open file: {Path(result['file_path']).name}",
                    "Replace template with your actual conversation",
                    "Save the file",
                    f"Run: import conversation {result['capture_id']}"
                ]
            }
        else:
            return {
                'handled': True,
                'success': False,
                'operation': 'capture_failed',
                'error': result['error'],
                'response': f"❌ Failed to create capture file: {result['error']}",
                'suggestion': 'Check CORTEX brain directory permissions'
            }
    
    def _handle_import_command(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle import conversation command"""
        capture_id = params.get('capture_id')
        if not capture_id:
            return {
                'handled': True,
                'success': False,
                'operation': 'import_failed',
                'error': 'Missing capture ID',
                'response': '❌ Please specify capture ID: "import conversation [capture_id]"',
                'suggestion': 'Use "list captures" to see available capture IDs'
            }
        
        result = self.capture_manager.import_conversation(capture_id)
        
        if result['success']:
            return {
                'handled': True,
                'success': True,
                'operation': 'import_completed',
                'conversation_id': result['conversation_id'],
                'response': self._format_import_success_response(result),
                'brain_integration': {
                    'tier': 'Tier 1 Working Memory',
                    'messages_count': result['messages_imported'],
                    'entities_count': result['entities_extracted']
                }
            }
        else:
            return {
                'handled': True,
                'success': False,
                'operation': 'import_failed',
                'error': result['error'],
                'response': f"❌ Import failed: {result['error']}",
                'suggestions': result.get('suggestions', [])
            }
    
    def _handle_list_captures_command(self) -> Dict[str, Any]:
        """Handle list captures command"""
        result = self.capture_manager.list_active_captures()
        
        if result['success']:
            return {
                'handled': True,
                'success': True,
                'operation': 'list_captures',
                'captures': result['active_captures'],
                'response': self._format_list_captures_response(result)
            }
        else:
            return {
                'handled': True,
                'success': False,
                'operation': 'list_failed',
                'error': result['error'],
                'response': f"❌ Failed to list captures: {result['error']}"
            }
    
    def _handle_status_command(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle capture status command"""
        capture_id = params.get('capture_id')
        if not capture_id:
            return {
                'handled': True,
                'success': False,
                'error': 'Missing capture ID',
                'response': '❌ Please specify capture ID: "capture status [capture_id]"'
            }
        
        result = self.capture_manager.get_capture_status(capture_id)
        
        if result['success']:
            return {
                'handled': True,
                'success': True,
                'operation': 'status_check',
                'status': result,
                'response': self._format_status_response(result)
            }
        else:
            return {
                'handled': True,
                'success': False,
                'operation': 'status_failed',
                'error': result['error'],
                'response': f"❌ Status check failed: {result['error']}"
            }
    
    def _format_capture_success_response(self, result: Dict[str, Any]) -> str:
        """Format success response for capture creation"""
        file_name = Path(result['file_path']).name
        return f"""
🎯 **Conversation Capture File Created Successfully!**

📋 **Step 1 Complete** ✅

**Capture ID:** `{result['capture_id']}`
**File Created:** `{file_name}`

📝 **Next Steps:**
1. **Open the capture file** (it has a template to guide you)
2. **Copy your Copilot conversation** from VS Code chat panel
3. **Replace the template** with your actual conversation
4. **Save the file**
5. **Run:** `import conversation {result['capture_id']}`

💡 **Tip:** The capture file includes an example format. Just replace the example with your real conversation!

🚀 **Ready for Step 2:** Once you've pasted your conversation, run the import command to add it to CORTEX brain.
        """.strip()
    
    def _format_import_success_response(self, result: Dict[str, Any]) -> str:
        """Format success response for conversation import"""
        return f"""
🧠 **Conversation Successfully Imported to CORTEX Brain!** 

✅ **Memory Integration Complete**

**📊 Import Summary:**
- **Conversation ID:** `{result['conversation_id']}`
- **Messages Imported:** {result['messages_imported']} 
- **Entities Extracted:** {result['entities_extracted']} (files, classes, functions)
- **Storage Location:** Tier 1 Working Memory
- **Intent Detected:** Auto-classified for better routing

🔗 **Context Continuity NOW ACTIVE**
CORTEX now remembers this conversation! Future requests like:
- "Make it purple" → CORTEX knows what "it" refers to
- "Continue with the next feature" → CORTEX has full context
- "Fix that bug we discussed" → CORTEX remembers the bug

📈 **Memory Status:**
- Available for next **20 conversation sessions** (FIFO queue)
- Automatically linked to related conversations
- Entities indexed for smart routing

🎉 **Amnesia Problem SOLVED!** Your conversations now have persistent memory.
        """.strip()
    
    def _format_list_captures_response(self, result: Dict[str, Any]) -> str:
        """Format response for listing active captures"""
        captures = result['active_captures']
        
        if not captures:
            return """
📋 **No Active Capture Files**

No capture files are currently awaiting import.

**To create a new capture:**
- Run: `capture conversation`
- Or: `capture conversation about [topic]`

**Need help?** Try: `cortex help capture`
            """.strip()
        
        response = f"📋 **Active Conversation Captures** ({len(captures)} total)\n\n"
        
        for i, capture in enumerate(captures, 1):
            status_emoji = "✅" if capture['ready_to_import'] else "📝"
            created_time = capture['created_at'][:19].replace('T', ' ')  # Format timestamp
            
            response += f"""
**{i}. Capture `{capture['capture_id']}`** {status_emoji}
- **Created:** {created_time}
- **Topic:** {capture['user_hint'] or 'General conversation'}  
- **File:** `{capture['file_name']}`
- **Status:** {'Ready to import' if capture['ready_to_import'] else 'Awaiting conversation paste'}
- **Next Action:** `{capture['next_action']}`

"""
        
        response += """
**Commands:**
- `import conversation [capture_id]` - Import ready captures
- `capture status [capture_id]` - Check specific capture
- `capture conversation` - Create new capture
        """
        
        return response.strip()
    
    def _format_status_response(self, result: Dict[str, Any]) -> str:
        """Format response for capture status check"""
        status_emoji = {
            'awaiting_paste': '📝',
            'imported': '✅'
        }.get(result['status'], '❓')
        
        created_time = result['created_at'][:19].replace('T', ' ')
        
        response = f"""
📊 **Capture Status: `{result['capture_id']}`** {status_emoji}

**General Info:**
- **Status:** {result['status'].replace('_', ' ').title()}
- **Created:** {created_time}
- **Topic:** {result['user_hint'] or 'General conversation'}

**File Status:**
- **Exists:** {'✅ Yes' if result['file_exists'] else '❌ No'}
- **Size:** {result['file_size_bytes']} bytes
- **Has Conversation:** {'✅ Yes' if result['has_conversation'] else '📝 Still template'}
- **Ready to Import:** {'✅ Yes' if result['ready_to_import'] else '❌ No'}

**Next Action:** {result['next_action']}
        """
        
        if result['status'] == 'imported':
            response += "\n\n🎉 **This conversation has been successfully imported to CORTEX brain!**"
        elif not result['has_conversation']:
            response += "\n\n💡 **Next Steps:** Open the capture file, paste your conversation, and save."
        
        return response.strip()


def process_capture_command(user_input: str, brain_path: str, workspace_root: str) -> Dict[str, Any]:
    """
    Convenience function for processing capture commands.
    
    This is the main entry point for the conversation capture system
    from CORTEX response templates and operations.
    """
    processor = CaptureCommandProcessor(brain_path, workspace_root)
    
    if not processor.initialize():
        return {
            'handled': False,
            'error': 'Failed to initialize conversation capture system',
            'suggestion': 'Check CORTEX brain directory and permissions'
        }
    
    return processor.process_command(user_input)


# Export for use in CORTEX operations and response templates
__all__ = ['CaptureCommandProcessor', 'process_capture_command']