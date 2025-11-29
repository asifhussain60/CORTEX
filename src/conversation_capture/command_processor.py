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
                    
                    # Handle capture ID extraction for import/status commands
                    if match.groups() and command_type in ['import', 'capture_status']:
                        params['capture_id'] = match.group(1)
                    
                    # Handle capture command (both template and direct mode)
                    if command_type == 'capture':
                        # Check for file: parameters (direct import mode)
                        # Support both #file: (GitHub Copilot style) and file: syntax
                        file_matches = re.findall(r'(?:#file:|file:)([^\s]+)', user_input, re.IGNORECASE)
                        if file_matches:
                            params['files'] = file_matches
                            params['mode'] = 'direct'
                        else:
                            params['mode'] = 'template'
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
        """Handle capture conversation command (template mode or direct mode)"""
        
        # Check if files were provided (direct mode)
        if params.get('files'):
            return self._handle_direct_import(params['files'])
        
        # Template mode (existing behavior)
        user_hint = params.get('hint', '')
        result = self.capture_manager.create_capture_file(user_hint)
        
        if result['success']:
            # Prepare VS Code file opening
            file_path = result['file_path']
            
            return {
                'handled': True,
                'success': True,
                'operation': 'capture_created',
                'capture_id': result['capture_id'],
                'file_path': file_path,
                'open_in_vscode': True,  # Signal to open file in VS Code
                'response': self._format_capture_success_response(result),
                'next_steps': [
                    f"File opened: {Path(file_path).name}",
                    "Right-click in Copilot Chat and select 'Copy Conversation'",
                    "Paste conversation into the blank file",
                    "Save the file (Cmd+S / Ctrl+S)",
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
    
    def _handle_direct_import(self, file_paths: List[str]) -> Dict[str, Any]:
        """Handle direct file import mode (no template creation)"""
        result = self.capture_manager.import_files_directly(file_paths)
        
        if result['success']:
            return {
                'handled': True,
                'success': True,
                'operation': 'direct_import_completed',
                'response': self._format_direct_import_response(result),
                'brain_integration': {
                    'tier': 'Tier 1 Working Memory',
                    'total_files': result['total_files'],
                    'successful_imports': result['successful_imports'],
                    'failed_imports': result['failed_imports']
                }
            }
        else:
            return {
                'handled': True,
                'success': False,
                'operation': 'direct_import_failed',
                'error': 'All file imports failed',
                'response': self._format_direct_import_failure_response(result),
                'suggestions': [
                    'Check that files exist and are readable',
                    'Verify files contain valid conversation format',
                    'Use absolute paths or paths relative to workspace root'
                ]
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
        file_path = Path(result['file_path'])
        file_name = file_path.name
        
        # Create vscode:// link for opening file
        vscode_link = f"vscode://file/{file_path.absolute()}"
        
        return f"""
🎯 **Blank Conversation Capture File Created!**

📋 **Capture Details**
**Capture ID:** `{result['capture_id']}`
**File Name:** `{file_name}`

� **File Location:** 
`{result['file_path']}`

🔗 **Quick Actions:**
• [📝 Open File in VS Code]({vscode_link})
• File has been opened automatically in VS Code

📝 **Next Steps:**

1. **Right-click in the GitHub Copilot Chat panel**
2. **Select "Copy Conversation"** from the context menu
3. **Switch to the opened blank file** in VS Code
4. **Paste (Cmd+V / Ctrl+V)** the conversation into the file
5. **Save the file** (Cmd+S / Ctrl+S)
6. **Return here and say:** `import conversation {result['capture_id']}`

💡 **Tips:**
• The file is completely blank - just paste your conversation directly
• Include the entire conversation for best context learning
• CORTEX will extract patterns, entities, and intents automatically
• Your conversation will be indexed for future reference

⚡ **Why This Matters:**
CORTEX learns from your successful conversations to improve accuracy and provide better suggestions in future interactions.

✅ **Ready:** Waiting for you to paste and save the conversation...
        """.strip()
    
    def _format_import_success_response(self, result: Dict[str, Any]) -> str:
        """Format success response for conversation import"""
        return f"""
🧠 **Conversation Successfully Captured & Learned!** 

✅ **Brain Learning Complete**

**📊 Capture Summary:**
- **Conversation ID:** `{result['conversation_id']}`
- **Messages Processed:** {result['messages_imported']} 
- **Entities Extracted:** {result['entities_extracted']} (files, classes, functions, patterns)
- **Storage Location:** Tier 1 Working Memory
- **Intent Classified:** Auto-detected for smart routing

🎓 **What CORTEX Learned:**
• **Successful Patterns** - Your working approaches and solutions
• **Context References** - What "it", "this", "that" refer to
• **Code Entities** - Files, classes, functions you're working with
• **Problem-Solution Pairs** - How you solved specific issues
• **Conversation Flow** - How you interact with AI assistants

🔗 **Context Continuity NOW ACTIVE**
CORTEX now remembers this conversation! Future requests benefit from:
- **Reference Resolution:** "Make it purple" → CORTEX knows what "it" is
- **Context Continuation:** "Continue with next feature" → Full context available
- **Pattern Recognition:** Similar requests get better suggestions
- **Smart Routing:** Requests automatically routed to right agent

📈 **Memory Integration:**
- Available for next **20 conversation sessions** (FIFO rotation)
- Automatically linked to related past conversations
- Entities indexed for instant lookup and smart suggestions
- Patterns learned to improve future accuracy

🎯 **Learning Impact:**
• **Accuracy Improvement:** Your patterns help CORTEX understand your style
• **Faster Responses:** Pre-learned context speeds up processing
• **Better Suggestions:** Past successes inform future recommendations
• **Failure Avoidance:** CORTEX learns what didn't work to avoid repeating

🎉 **Amnesia Problem SOLVED!** Persistent memory across all future sessions.

💡 **Pro Tip:** Capture successful conversations regularly to continuously improve CORTEX's accuracy and personalization to your workflow.
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


    def _format_direct_import_response(self, result: Dict[str, Any]) -> str:
        """Format success response for direct file import"""
        response = f"""
🧠 **Direct Import Completed!** 

✅ **Batch Import Summary**
- **Total Files:** {result['total_files']}
- **Successful:** {result['successful_imports']}
- **Failed:** {result['failed_imports']}

📊 **Import Details:**
"""
        
        for item in result['results']:
            if item['success']:
                response += f"\n✅ `{Path(item['file']).name}`"
                response += f"\n   - Conversation ID: `{item['conversation_id']}`"
                response += f"\n   - Messages: {item['messages_imported']}"
                response += f"\n   - Entities: {item['entities_extracted']}"
            else:
                response += f"\n❌ `{Path(item['file']).name}`"
                response += f"\n   - Error: {item['error']}"
        
        response += """

🔗 **Context Continuity NOW ACTIVE**
All imported conversations are now in CORTEX working memory!

🎉 **No template files created** - Direct import mode!
"""
        
        return response.strip()
    
    def _format_direct_import_failure_response(self, result: Dict[str, Any]) -> str:
        """Format failure response for direct file import"""
        response = f"""
❌ **Direct Import Failed**

**Summary:**
- **Total Files:** {result['total_files']}
- **Successful:** {result['successful_imports']}
- **Failed:** {result['failed_imports']}

**Failure Details:**
"""
        
        for item in result['results']:
            if not item['success']:
                response += f"\n❌ `{Path(item['file']).name}`"
                response += f"\n   - Error: {item['error']}"
        
        response += """

💡 **Troubleshooting Tips:**
- Verify files exist and are readable
- Check file paths (use absolute or workspace-relative paths)
- Ensure files contain valid conversation format (You:/Copilot: structure)
- Try importing files one at a time to isolate issues
"""
        
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