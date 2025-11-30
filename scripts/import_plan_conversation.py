"""
Import plan.md conversation to CORTEX brain with validation.

Fixed Issues:
- Validates conversation was actually parsed (no empty imports)
- Handles malformed conversation formats gracefully
- Provides clear error messages
"""
import sys
import re
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tier1.working_memory import WorkingMemory

def parse_conversation(content: str):
    """
    Parse conversation with improved pattern matching.
    
    Returns list of turn dicts, each with 'user' and 'assistant' keys.
    Format: [{'user': '...', 'assistant': '...'}, ...]
    """
    messages = []
    lines = content.split('\n')
    current_speaker = None
    current_message = []
    
    for line in lines:
        if line.startswith('asifhussain60: '):
            # Save previous message if exists
            if current_speaker and current_message:
                message_text = '\n'.join(current_message).strip()
                if message_text:
                    messages.append({
                        'speaker': current_speaker,
                        'text': message_text
                    })
            
            # Start new user message
            current_speaker = 'user'
            current_message = [line.replace('asifhussain60: ', '', 1)]
            
        elif line.startswith('GitHub Copilot: '):
            # Save previous message if exists
            if current_speaker and current_message:
                message_text = '\n'.join(current_message).strip()
                if message_text:
                    messages.append({
                        'speaker': current_speaker,
                        'text': message_text
                    })
            
            # Start new assistant message
            current_speaker = 'assistant'
            current_message = [line.replace('GitHub Copilot: ', '', 1)]
            
        else:
            # Continue current message
            if current_speaker:
                current_message.append(line)
    
    # Don't forget the last message
    if current_speaker and current_message:
        message_text = '\n'.join(current_message).strip()
        if message_text:
            messages.append({
                'speaker': current_speaker,
                'text': message_text
            })
    
    # Now pair up user/assistant messages into turns
    turns = []
    i = 0
    while i < len(messages):
        msg = messages[i]
        
        if msg['speaker'] == 'user':
            # Look for following assistant message
            if i + 1 < len(messages) and messages[i + 1]['speaker'] == 'assistant':
                turns.append({
                    'user': msg['text'],
                    'assistant': messages[i + 1]['text']
                })
                i += 2  # Skip both messages
            else:
                # User message without response - skip it
                print(f'   Warning: Skipping unpaired user message at index {i}')
                i += 1
        else:
            # Assistant message without user prompt - skip it
            print(f'   Warning: Skipping unpaired assistant message at index {i}')
            i += 1
    
    return turns

# Read plan.md
plan_path = Path(__file__).resolve().parent.parent / '.github' / 'CopilotChats' / 'plan.md'
if not plan_path.exists():
    print(f'❌ Error: plan.md not found at {plan_path}')
    sys.exit(1)

with open(plan_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Parse conversation
turns = parse_conversation(content)

# CRITICAL VALIDATION: Don't import empty conversations
if len(turns) == 0:
    print('❌ Error: No conversation turns found in plan.md')
    print('   The file may be empty or not formatted correctly.')
    print('   Expected format:')
    print('   asifhussain60: [message]')
    print('   GitHub Copilot: [response]')
    sys.exit(1)

# Show what was parsed
print(f'✅ Parsed {len(turns)} conversation turns from plan.md')
print(f'   First turn: {list(turns[0].keys())[0]} ({len(list(turns[0].values())[0])} chars)')

# Import to CORTEX
wm = WorkingMemory()
result = wm.import_conversation(
    conversation_turns=turns,
    import_source='plan.md',
    workspace_path=str(Path(__file__).resolve().parent.parent)
)

# Display results
print(f'\n{"✅" if result["success"] else "❌"} Import {"Complete" if result["success"] else "Failed"}')
print(f'   Success: {result["success"]}')

if 'error' in result:
    print(f'   Error: {result["error"]}')

print(f'   Conversation ID: {result.get("conversation_id")}')
print(f'   Quality Score: {result.get("quality_score", 0)}/10')
print(f'   Quality Level: {result.get("quality_level", "UNKNOWN")}')
print(f'   Turns Imported: {result.get("turns_imported", 0)}')
