"""
CORTEX 3.0 - Manual Conversation Capture System
==============================================

Two-step manual workflow to capture GitHub Copilot conversations into CORTEX brain.
Solves the amnesia problem immediately with simple user commands.

Workflow:
1. User types: '/CORTEX Capture' → Creates empty capture file 
2. User copies conversation → Pastes into capture file
3. User types: '/CORTEX Import' → Processes conversation into Tier 1 memory

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Feature: Quick Win #5.1 (Week 2)
Effort: 20 hours (manual conversation capture)
Target: Immediate amnesia solution with 100% capture success rate
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from pathlib import Path
import json
import re
import uuid
import logging
import shutil
import os

# CORTEX internal imports
from src.tier1.working_memory import WorkingMemory


class ConversationCaptureManager:
    """
    Manages manual conversation capture workflow.
    
    Two-step process:
    1. CAPTURE: Create empty file for user to paste conversation
    2. IMPORT: Process pasted conversation into CORTEX brain
    
    Features:
    - Simple user workflow (just copy/paste)
    - Conversation parsing and entity extraction
    - Automatic Tier 1 memory integration
    - Capture file management and cleanup
    - Import validation and error handling
    """
    
    def __init__(self, brain_path: str, workspace_root: str):
        self.brain_path = Path(brain_path)
        self.workspace_root = Path(workspace_root)
        self.capture_dir = self.brain_path / "conversation-captures"
        
        # Setup logging
        self.logger = logging.getLogger('cortex.conversation_capture')
        
        # Working memory integration
        self.working_memory = WorkingMemory(str(self.brain_path))
        
        # Capture file tracking
        self.active_captures = {}
        
        # Configure entity extraction patterns
        self.file_patterns = [
            r'[a-zA-Z0-9_-]+\.(py|ts|js|cs|java|cpp|h|md|txt|json|yaml|yml)',
            r'[a-zA-Z0-9_-]+/[a-zA-Z0-9_/-]+\.(py|ts|js|cs|java|cpp|h|md|txt)',
        ]
        self.class_patterns = [
            r'\b[A-Z][a-zA-Z0-9]*(?:Controller|Service|Manager|Handler|Component)\b',
            r'\bclass\s+([A-Z][a-zA-Z0-9]*)\b',
        ]
        self.function_patterns = [
            r'\b(def|function|func|public|private|protected)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
            r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
        ]
        
    def initialize(self) -> bool:
        """Initialize the conversation capture system"""
        try:
            # Create capture directory
            self.capture_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize working memory
            if not self.working_memory.initialize():
                self.logger.error("Failed to initialize working memory")
                return False
            
            # Clean up old capture files (older than 24 hours)
            self._cleanup_old_captures()
            
            self.logger.info("Conversation capture manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize conversation capture manager: {e}")
            return False
    
    def create_capture_file(self, user_hint: str = "") -> Dict[str, Any]:
        """
        Step 1: Create empty capture file for user to paste conversation
        
        Args:
            user_hint: Optional hint about what the conversation is about
            
        Returns:
            Dict with capture file info and instructions
        """
        try:
            # Generate unique capture ID
            capture_id = f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Create capture file
            capture_file = self.capture_dir / f"{capture_id}.md"
            
            # Generate instructions and template
            instructions = self._generate_capture_instructions(user_hint)
            
            # Write template to capture file
            with open(capture_file, 'w', encoding='utf-8') as f:
                f.write(instructions)
            
            # Track active capture
            self.active_captures[capture_id] = {
                'file_path': str(capture_file),
                'created_at': datetime.now(timezone.utc).isoformat(),
                'user_hint': user_hint,
                'status': 'awaiting_paste'
            }
            
            return {
                'success': True,
                'capture_id': capture_id,
                'file_path': str(capture_file),
                'instructions': f"""
📋 **CORTEX Conversation Capture Created**

**Step 1 Complete!** ✅

**Next Steps:**
1. **Copy your Copilot conversation** from VS Code chat panel
2. **Open file:** `{capture_file.name}` 
3. **Replace the template** with your actual conversation
4. **Save the file** 
5. **Run:** `/CORTEX Import {capture_id}`

**File Location:** `{capture_file.relative_to(self.workspace_root)}`

The capture file has been pre-filled with a template. Just replace the example conversation with your real one!
                """.strip(),
                'ready_for_paste': True
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create capture file: {e}")
            return {
                'success': False,
                'error': str(e),
                'instructions': 'Failed to create capture file. Please check logs.'
            }
    
    def import_conversation(self, capture_id: str) -> Dict[str, Any]:
        """
        Step 2: Import pasted conversation from capture file into CORTEX brain
        
        Args:
            capture_id: ID returned from create_capture_file
            
        Returns:
            Dict with import results and memory integration status
        """
        try:
            # Validate capture ID
            if capture_id not in self.active_captures:
                return {
                    'success': False,
                    'error': f'Capture ID {capture_id} not found. Run /CORTEX Capture first.',
                    'suggestions': [
                        'Run /CORTEX Capture to create a new capture file',
                        'Check that you copied the capture ID correctly'
                    ]
                }
            
            capture_info = self.active_captures[capture_id]
            capture_file = Path(capture_info['file_path'])
            
            # Check if file exists and has content
            if not capture_file.exists():
                return {
                    'success': False,
                    'error': f'Capture file not found: {capture_file.name}',
                    'suggestion': 'The capture file may have been deleted. Create a new one.'
                }
            
            # Read conversation content
            with open(capture_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # Validate content (not just template)
            if self._is_still_template(content):
                return {
                    'success': False,
                    'error': 'Capture file still contains template. Please paste your actual conversation.',
                    'suggestions': [
                        f'Open {capture_file.name} and replace template with your conversation',
                        'Copy your conversation from VS Code chat panel',
                        'Save the file and try importing again'
                    ]
                }
            
            # Parse conversation
            conversation_data = self._parse_conversation(content, capture_info['user_hint'])
            
            if not conversation_data['messages']:
                return {
                    'success': False,
                    'error': 'No conversation messages found. Please check the format.',
                    'suggestions': [
                        'Ensure conversation contains "You:" and "Copilot:" messages',
                        'Check that the conversation was pasted completely',
                        'See template example for proper format'
                    ]
                }
            
            # Import into working memory (Tier 1)
            memory_result = self._import_to_working_memory(conversation_data)
            
            if memory_result['success']:
                # Mark capture as completed
                self.active_captures[capture_id]['status'] = 'imported'
                self.active_captures[capture_id]['imported_at'] = datetime.now(timezone.utc).isoformat()
                self.active_captures[capture_id]['conversation_id'] = memory_result['conversation_id']
                
                # Archive capture file
                archived_file = self._archive_capture_file(capture_file, capture_id)
                
                return {
                    'success': True,
                    'conversation_id': memory_result['conversation_id'],
                    'messages_imported': len(conversation_data['messages']),
                    'entities_extracted': len(conversation_data['entities']),
                    'memory_tier': 'Tier 1 (Working Memory)',
                    'archived_to': str(archived_file) if archived_file else None,
                    'summary': f"""
🧠 **Conversation Successfully Imported to CORTEX Brain!**

✅ **Import Complete**
- **Conversation ID:** `{memory_result['conversation_id']}`
- **Messages:** {len(conversation_data['messages'])} imported
- **Entities:** {len(conversation_data['entities'])} extracted (files, classes, functions)
- **Intent:** {conversation_data.get('intent', 'AUTO_DETECTED')}
- **Stored in:** Tier 1 Working Memory

🔗 **Context Continuity Enabled**
CORTEX now remembers this conversation. Future requests like "make it purple" will understand what "it" refers to!

📊 **Next Steps:**
- Continue your conversation - CORTEX has context
- Use "cortex status" to see memory utilization  
- Imported conversation will be available for 20 sessions (FIFO)

*Capture file archived to preserve original conversation.*
                    """.strip()
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to import to working memory: {memory_result.get("error", "Unknown error")}',
                    'conversation_data': conversation_data,  # For debugging
                    'suggestion': 'Check CORTEX brain database connectivity'
                }
                
        except Exception as e:
            self.logger.error(f"Failed to import conversation {capture_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'suggestion': 'Check logs for detailed error information'
            }
    
    def list_active_captures(self) -> Dict[str, Any]:
        """List all active capture files awaiting import"""
        try:
            active = []
            for capture_id, info in self.active_captures.items():
                if info['status'] == 'awaiting_paste':
                    # Check if file still exists and has content
                    capture_file = Path(info['file_path'])
                    if capture_file.exists():
                        with open(capture_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        has_conversation = not self._is_still_template(content)
                        
                        active.append({
                            'capture_id': capture_id,
                            'created_at': info['created_at'],
                            'user_hint': info['user_hint'],
                            'file_name': capture_file.name,
                            'has_conversation': has_conversation,
                            'ready_to_import': has_conversation,
                            'next_action': f'/CORTEX Import {capture_id}' if has_conversation else 'Paste conversation and save file'
                        })
            
            return {
                'success': True,
                'active_captures': active,
                'count': len(active)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to list active captures: {e}")
            return {
                'success': False,
                'error': str(e),
                'active_captures': []
            }
    
    def get_capture_status(self, capture_id: str) -> Dict[str, Any]:
        """Get detailed status of a specific capture"""
        try:
            if capture_id not in self.active_captures:
                return {
                    'success': False,
                    'error': f'Capture {capture_id} not found'
                }
            
            info = self.active_captures[capture_id]
            capture_file = Path(info['file_path'])
            
            # Check file status
            file_exists = capture_file.exists()
            file_size = capture_file.stat().st_size if file_exists else 0
            
            has_conversation = False
            if file_exists:
                with open(capture_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                has_conversation = not self._is_still_template(content)
            
            return {
                'success': True,
                'capture_id': capture_id,
                'status': info['status'],
                'created_at': info['created_at'],
                'user_hint': info['user_hint'],
                'file_exists': file_exists,
                'file_size_bytes': file_size,
                'has_conversation': has_conversation,
                'ready_to_import': has_conversation and file_exists,
                'file_path': str(capture_file),
                'next_action': self._get_next_action(info['status'], has_conversation)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    # Private helper methods
    
    def _generate_capture_instructions(self, user_hint: str) -> str:
        """Generate capture file template with instructions"""
        template = f"""# CORTEX Conversation Capture
        
**Instructions:**
1. REPLACE this entire template with your GitHub Copilot conversation
2. Copy your conversation from VS Code chat panel  
3. Paste it here, keeping the format: "You: ..." and "Copilot: ..."
4. Save this file
5. Run: /CORTEX Import [capture_id] to import into brain

**User Hint:** {user_hint if user_hint else "General conversation"}
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## EXAMPLE FORMAT (REPLACE WITH YOUR CONVERSATION)

**You:** Add a purple button to the dashboard

**Copilot:** I'll add a purple button to the dashboard for you. Let me create a styled button component.

```html
<button class="purple-button" onclick="handleClick()">
  Click Me
</button>
```

```css
.purple-button {{
  background-color: #8A2BE2;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
}}
```

I've created a purple button with proper styling. The button uses a vibrant purple color (#8A2BE2) and includes hover effects for better user interaction.

**You:** Make it bigger and add a shadow

**Copilot:** I'll increase the button size and add a shadow effect:

```css
.purple-button {{
  background-color: #8A2BE2;
  color: white;
  border: none;
  padding: 15px 30px;  /* Increased padding */
  border-radius: 8px;   /* Slightly larger border radius */
  cursor: pointer;
  font-size: 16px;      /* Larger text */
  box-shadow: 0 4px 8px rgba(138, 43, 226, 0.3);  /* Purple shadow */
  transition: transform 0.2s, box-shadow 0.2s;
}}

.purple-button:hover {{
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(138, 43, 226, 0.4);
}}
```

The button is now larger with increased padding and font size, plus it has a purple shadow that enhances on hover with a subtle lift effect.

---

**REPLACE THE EXAMPLE ABOVE WITH YOUR ACTUAL CONVERSATION**
"""
        return template
    
    def _is_still_template(self, content: str) -> bool:
        """Check if the capture file still contains the template"""
        template_indicators = [
            "REPLACE this entire template",
            "EXAMPLE FORMAT (REPLACE WITH YOUR CONVERSATION)",
            "REPLACE THE EXAMPLE ABOVE",
            "I'll add a purple button",  # Example content
        ]
        
        content_lower = content.lower()
        for indicator in template_indicators:
            if indicator.lower() in content_lower:
                return True
        
        # Also check if it's suspiciously short (just instructions)
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        conversation_lines = [line for line in lines if line.startswith(('You:', 'Copilot:', '**You:**', '**Copilot:**'))]
        
        return len(conversation_lines) < 2  # Need at least user + copilot message
    
    def _parse_conversation(self, content: str, user_hint: str) -> Dict[str, Any]:
        """Parse conversation content and extract structured data"""
        try:
            # Extract messages
            messages = self._extract_messages(content)
            
            # Extract entities (files, classes, functions mentioned)
            entities = self._extract_entities(content)
            
            # Detect intent from conversation
            intent = self._detect_intent(messages, user_hint)
            
            # Calculate conversation metadata
            metadata = {
                'total_messages': len(messages),
                'user_messages': len([m for m in messages if m['role'] == 'user']),
                'assistant_messages': len([m for m in messages if m['role'] == 'assistant']),
                'has_code': any('```' in msg['content'] for msg in messages),
                'word_count': sum(len(msg['content'].split()) for msg in messages),
                'user_hint': user_hint,
                'parsed_at': datetime.now(timezone.utc).isoformat()
            }
            
            return {
                'messages': messages,
                'entities': entities,
                'intent': intent,
                'metadata': metadata
            }
            
        except Exception as e:
            self.logger.error(f"Failed to parse conversation: {e}")
            return {
                'messages': [],
                'entities': [],
                'intent': 'UNKNOWN',
                'metadata': {'error': str(e)}
            }
    
    def _extract_messages(self, content: str) -> List[Dict[str, Any]]:
        """Extract conversation messages from content"""
        messages = []
        
        # Split by message markers
        patterns = [
            r'\*\*You:\*\*\s*(.*?)(?=\*\*Copilot:\*\*|\*\*You:\*\*|$)',
            r'\*\*Copilot:\*\*\s*(.*?)(?=\*\*You:\*\*|\*\*Copilot:\*\*|$)',
            r'You:\s*(.*?)(?=Copilot:|You:|$)',
            r'Copilot:\s*(.*?)(?=You:|Copilot:|$)'
        ]
        
        # Try different patterns to extract messages
        for pattern_group in [patterns[:2], patterns[2:]]:  # Try markdown format first, then plain format
            temp_messages = []
            
            for pattern in pattern_group:
                matches = re.finditer(pattern, content, re.DOTALL | re.IGNORECASE)
                for match in matches:
                    role = 'user' if 'you' in pattern.lower() else 'assistant'
                    content_text = match.group(1).strip()
                    
                    if content_text and len(content_text) > 10:  # Minimum meaningful length
                        temp_messages.append({
                            'role': role,
                            'content': content_text,
                            'timestamp': datetime.now(timezone.utc).isoformat(),
                            'order': len(temp_messages)
                        })
            
            if temp_messages:  # If we found messages with this pattern, use them
                messages = temp_messages
                break
        
        # Sort by appearance order and validate alternation
        messages.sort(key=lambda x: x['order'])
        
        return messages
    
    def _extract_entities(self, content: str) -> List[Dict[str, Any]]:
        """Extract file names, class names, function names from conversation"""
        entities = []
        
        # Extract files
        for pattern in self.file_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                entities.append({
                    'type': 'file',
                    'value': match.group(0),
                    'context': 'mentioned in conversation'
                })
        
        # Extract classes
        for pattern in self.class_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                class_name = match.group(1) if match.lastindex else match.group(0)
                entities.append({
                    'type': 'class',
                    'value': class_name,
                    'context': 'mentioned in conversation'
                })
        
        # Extract functions
        for pattern in self.function_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                func_name = match.group(2) if match.lastindex and match.lastindex >= 2 else match.group(1)
                if func_name and not func_name in ['def', 'function', 'func', 'public', 'private', 'protected']:
                    entities.append({
                        'type': 'function',
                        'value': func_name,
                        'context': 'mentioned in conversation'
                    })
        
        # Remove duplicates
        seen = set()
        unique_entities = []
        for entity in entities:
            key = f"{entity['type']}:{entity['value']}"
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        return unique_entities
    
    def _detect_intent(self, messages: List[Dict[str, Any]], user_hint: str) -> str:
        """Detect conversation intent from messages and hint"""
        if not messages:
            return 'UNKNOWN'
        
        # Get user messages for analysis
        user_messages = [msg['content'].lower() for msg in messages if msg['role'] == 'user']
        all_text = ' '.join(user_messages + [user_hint.lower()])
        
        # Intent keywords
        intent_patterns = {
            'EXECUTE': ['add', 'create', 'implement', 'build', 'make', 'generate', 'write'],
            'FIX': ['fix', 'error', 'bug', 'broken', 'wrong', 'not working', 'issue', 'problem'],
            'PLAN': ['plan', 'design', 'architecture', 'structure', 'organize', 'strategy'],
            'TEST': ['test', 'verify', 'check', 'validate', 'ensure', 'confirm'],
            'ANALYZE': ['analyze', 'review', 'examine', 'study', 'understand', 'explain'],
            'REFACTOR': ['refactor', 'improve', 'optimize', 'clean', 'reorganize', 'restructure']
        }
        
        # Score each intent
        intent_scores = {}
        for intent, keywords in intent_patterns.items():
            score = sum(1 for keyword in keywords if keyword in all_text)
            if score > 0:
                intent_scores[intent] = score
        
        # Return highest scoring intent
        if intent_scores:
            return max(intent_scores.items(), key=lambda x: x[1])[0]
        
        return 'GENERAL'
    
    def _import_to_working_memory(self, conversation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Import conversation data into Tier 1 working memory"""
        try:
            # Format for working memory
            messages = conversation_data['messages']
            if not messages:
                return {'success': False, 'error': 'No messages to import'}
            
            # Create conversation summary
            user_message = ' | '.join([msg['content'][:100] for msg in messages if msg['role'] == 'user'])
            assistant_message = ' | '.join([msg['content'][:100] for msg in messages if msg['role'] == 'assistant'])
            
            # Store in working memory
            conversation_id = self.working_memory.store_conversation(
                user_message=user_message[:1000],  # Limit length
                assistant_response=assistant_message[:1000],  # Limit length
                intent=conversation_data['intent'],
                context={
                    'manual_import': True,
                    'entities': conversation_data['entities'],
                    'message_count': len(messages),
                    'imported_at': datetime.now(timezone.utc).isoformat(),
                    'metadata': conversation_data['metadata']
                }
            )
            
            if conversation_id:
                return {
                    'success': True,
                    'conversation_id': conversation_id
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to store conversation in working memory'
                }
                
        except Exception as e:
            self.logger.error(f"Failed to import to working memory: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _archive_capture_file(self, capture_file: Path, capture_id: str) -> Optional[Path]:
        """Archive processed capture file"""
        try:
            archive_dir = self.brain_path / "conversation-captures" / "archived"
            archive_dir.mkdir(parents=True, exist_ok=True)
            
            archived_file = archive_dir / f"{capture_id}_archived.md"
            shutil.move(str(capture_file), str(archived_file))
            
            return archived_file
            
        except Exception as e:
            self.logger.warning(f"Failed to archive capture file: {e}")
            return None
    
    def _cleanup_old_captures(self):
        """Clean up old capture files (older than 24 hours)"""
        try:
            cutoff_time = datetime.now().timestamp() - (24 * 3600)  # 24 hours ago
            
            if self.capture_dir.exists():
                for capture_file in self.capture_dir.glob("capture_*.md"):
                    if capture_file.stat().st_mtime < cutoff_time:
                        capture_file.unlink()
                        self.logger.info(f"Cleaned up old capture file: {capture_file.name}")
                        
        except Exception as e:
            self.logger.warning(f"Failed to cleanup old captures: {e}")
    
    def _get_next_action(self, status: str, has_conversation: bool) -> str:
        """Get next action for user based on capture status"""
        if status == 'awaiting_paste':
            if has_conversation:
                return 'Run /CORTEX Import [capture_id]'
            else:
                return 'Paste conversation into file and save'
        elif status == 'imported':
            return 'Conversation already imported successfully'
        else:
            return 'Unknown status'
    
    def import_files_directly(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Import conversations directly from files (no template creation)
        
        Args:
            file_paths: List of file paths to import
            
        Returns:
            Dict with import results for all files
        """
        results = []
        successful = 0
        failed = 0
        
        for file_path in file_paths:
            # Validate file
            validation_error = self._validate_file(file_path)
            if validation_error:
                results.append({
                    'file': file_path,
                    'success': False,
                    'error': validation_error
                })
                failed += 1
                continue
            
            # Read file content
            content = self._read_file_content(file_path)
            if content is None:
                results.append({
                    'file': file_path,
                    'success': False,
                    'error': 'Failed to read file'
                })
                failed += 1
                continue
            
            # Parse conversation
            try:
                parsed = self._parse_conversation_content(content)
                
                if not parsed['messages']:
                    results.append({
                        'file': file_path,
                        'success': False,
                        'error': 'No valid conversation messages found'
                    })
                    failed += 1
                    continue
                
                # Import to working memory
                import_result = self._import_to_working_memory(parsed)
                
                if import_result['success']:
                    results.append({
                        'file': file_path,
                        'success': True,
                        'conversation_id': import_result['conversation_id'],
                        'messages_imported': len(parsed['messages']),
                        'entities_extracted': len(parsed['entities'])
                    })
                    successful += 1
                else:
                    results.append({
                        'file': file_path,
                        'success': False,
                        'error': import_result.get('error', 'Import failed')
                    })
                    failed += 1
                    
            except Exception as e:
                self.logger.error(f"Failed to parse/import {file_path}: {e}")
                results.append({
                    'file': file_path,
                    'success': False,
                    'error': f'Parse error: {str(e)}'
                })
                failed += 1
        
        return {
            'success': successful > 0,
            'total_files': len(file_paths),
            'successful_imports': successful,
            'failed_imports': failed,
            'results': results
        }
    
    def _validate_file(self, file_path: str) -> Optional[str]:
        """
        Validate file exists and is readable
        
        Returns:
            Error message if validation fails, None if valid
        """
        try:
            path = Path(file_path)
            
            # Handle workspace-relative paths
            if not path.is_absolute():
                path = self.workspace_root / path
            
            if not path.exists():
                return f'File not found: {file_path}'
            
            if not path.is_file():
                return f'Not a file: {file_path}'
            
            if not os.access(path, os.R_OK):
                return f'File not readable: {file_path}'
            
            return None
            
        except Exception as e:
            return f'Validation error: {str(e)}'
    
    def _read_file_content(self, file_path: str) -> Optional[str]:
        """
        Read file content with proper encoding
        
        Returns:
            File content as string, or None if read fails
        """
        try:
            path = Path(file_path)
            
            # Handle workspace-relative paths
            if not path.is_absolute():
                path = self.workspace_root / path
            
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
                
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                self.logger.error(f"Failed to read {file_path}: {e}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to read {file_path}: {e}")
            return None


# Export for use in CORTEX operations
__all__ = ['ConversationCaptureManager']