#!/usr/bin/env python3
"""
CORTEX Conversation Import Tool
Imports conversation from CopilotChats.md into Tier 1 memory

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import re
from datetime import datetime
from pathlib import Path

# Add CORTEX root to Python path
CORTEX_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(CORTEX_ROOT))

try:
    from src.tier1.working_memory import WorkingMemory
    print("✅ WorkingMemory import successful")
except ImportError as e:
    print(f"❌ Failed to import WorkingMemory: {e}")
    sys.exit(1)

def parse_conversation_file(file_path):
    """Parse CopilotChats.md and extract conversation data"""
    print(f"📖 Reading conversation from: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by conversation turns
    conversations = []
    current_conversation = []
    
    # Pattern to match user messages vs assistant responses
    user_pattern = r'^(asifhussain60:.*?)(?=^GitHub Copilot:|\Z)'
    assistant_pattern = r'^(GitHub Copilot:.*?)(?=^asifhussain60:|\Z)'
    
    # Split content into messages
    lines = content.split('\n')
    current_message = []
    current_speaker = None
    
    for line in lines:
        if line.startswith('asifhussain60:'):
            # Save previous message if exists
            if current_message and current_speaker:
                conversations.append({
                    'speaker': current_speaker,
                    'content': '\n'.join(current_message).strip()
                })
            
            current_speaker = 'user'
            current_message = [line[14:].strip()]  # Remove "asifhussain60: "
            
        elif line.startswith('GitHub Copilot:'):
            # Save previous message if exists
            if current_message and current_speaker:
                conversations.append({
                    'speaker': current_speaker,
                    'content': '\n'.join(current_message).strip()
                })
            
            current_speaker = 'assistant'
            current_message = [line[15:].strip()]  # Remove "GitHub Copilot: "
            
        else:
            # Continue current message
            if current_message:
                current_message.append(line)
    
    # Add final message
    if current_message and current_speaker:
        conversations.append({
            'speaker': current_speaker,
            'content': '\n'.join(current_message).strip()
        })
    
    print(f"📝 Parsed {len(conversations)} conversation turns")
    return conversations

def import_to_tier1(conversations):
    """Import parsed conversations into CORTEX Tier 1 memory"""
    print("🧠 Importing conversation into CORTEX Tier 1 memory...")
    
    try:
        wm = WorkingMemory()
        print("✅ WorkingMemory instantiated successfully")
        
        # Create conversation pairs (user message + assistant response)
        conversation_pairs = []
        for i in range(0, len(conversations), 2):
            if i + 1 < len(conversations):
                user_msg = conversations[i]
                assistant_msg = conversations[i + 1]
                
                if user_msg['speaker'] == 'user' and assistant_msg['speaker'] == 'assistant':
                    conversation_pairs.append({
                        'user_message': user_msg['content'],
                        'assistant_response': assistant_msg['content'],
                        'timestamp': datetime.now(),
                        'intent': detect_intent(user_msg['content']),
                        'entities': extract_entities(user_msg['content'], assistant_msg['content'])
                    })
        
        print(f"💾 Using import_conversation method for {len(conversation_pairs)} conversation pairs...")
        
        # Use import_conversation method (CORTEX 3.0 dual-channel memory)
        for i, pair in enumerate(conversation_pairs, 1):
            try:
                # Prepare conversation turn for import_conversation
                conversation_turns = [{
                    'user': pair['user_message'],
                    'assistant': pair['assistant_response']
                }]
                
                result = wm.import_conversation(
                    conversation_turns=conversation_turns,
                    import_source="/Users/asifhussain/PROJECTS/CORTEX/.github/CopilotChats.md",
                    workspace_path="/Users/asifhussain/PROJECTS/CORTEX",
                    import_date=datetime.now()
                )
                
                print(f"  ✅ Imported conversation {i}: {result['conversation_id']} (quality: {result['quality_level']})")
                
            except Exception as e:
                print(f"  ❌ Failed to import conversation {i}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing to Tier 1: {e}")
        return False

def detect_intent(user_message):
    """Simple intent detection based on keywords"""
    message_lower = user_message.lower()
    
    if any(word in message_lower for word in ['plan', 'planning', 'design']):
        return 'PLAN'
    elif any(word in message_lower for word in ['fix', 'debug', 'error', 'problem']):
        return 'FIX'
    elif any(word in message_lower for word in ['test', 'validate', 'check']):
        return 'TEST'
    elif any(word in message_lower for word in ['implement', 'create', 'add', 'build']):
        return 'EXECUTE'
    elif any(word in message_lower for word in ['continue', 'resume', 'proceed']):
        return 'CONTINUE'
    elif any(word in message_lower for word in ['status', 'health', 'show']):
        return 'STATUS'
    else:
        return 'GENERAL'

def extract_entities(user_message, assistant_response):
    """Extract entities from conversation"""
    entities = []
    
    # Extract file references
    file_pattern = r'(?:file://|#file:)?([^/\s]*\.(?:py|md|yaml|json|js|ts|cs|razor))'
    for match in re.finditer(file_pattern, user_message + ' ' + assistant_response):
        entities.append({
            'type': 'file',
            'value': match.group(1)
        })
    
    # Extract CORTEX-specific terms
    cortex_terms = ['daemon', 'singleton', 'tier1', 'tier 1', 'memory', 'conversation', 'brain', 'cortex']
    for term in cortex_terms:
        if term.lower() in (user_message + ' ' + assistant_response).lower():
            entities.append({
                'type': 'concept',
                'value': term
            })
    
    return entities

def test_memory_retrieval():
    """Test that imported conversations can be retrieved"""
    print("\n🔍 Testing memory retrieval...")
    
    try:
        wm = WorkingMemory()
        
        # Get recent conversations using correct API
        recent = wm.get_recent_conversations(limit=5)
        print(f"📚 Found {len(recent)} recent conversations in memory")
        
        for i, conv in enumerate(recent, 1):
            # Conversation objects have attributes, not dict keys
            print(f"  {i}. ID: {conv.conversation_id} - Title: {conv.title}")
        
        # Test search functionality using correct API (no limit parameter)
        print("\n🔍 Testing search functionality...")
        search_results = wm.search_conversations(keyword="CORTEX")
        print(f"🔍 Search for 'CORTEX' found {len(search_results)} results")
        
        for i, result in enumerate(search_results[:3], 1):  # Show first 3
            print(f"  {i}. {result.conversation_id}: {result.title}")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory retrieval test failed: {e}")
        return False

def main():
    """Main import process"""
    print("🧠 CORTEX Conversation Import Tool")
    print("=" * 50)
    
    # File path
    copilot_chats_file = CORTEX_ROOT / ".github" / "CopilotChats.md"
    
    if not copilot_chats_file.exists():
        print(f"❌ File not found: {copilot_chats_file}")
        return False
    
    # Parse conversations
    conversations = parse_conversation_file(copilot_chats_file)
    
    if not conversations:
        print("❌ No conversations found to import")
        return False
    
    # Import to Tier 1
    success = import_to_tier1(conversations)
    
    if success:
        print("\n✅ Conversation import completed successfully!")
        
        # Test memory retrieval
        test_success = test_memory_retrieval()
        
        if test_success:
            print("\n🎉 CORTEX brain memory is now functional!")
            print("💡 Next: Try starting a new conversation and say 'continue' to test memory continuity")
        else:
            print("\n⚠️ Import succeeded but memory retrieval test failed")
        
    else:
        print("\n❌ Conversation import failed")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)