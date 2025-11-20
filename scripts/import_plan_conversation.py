"""Import plan.md conversation to CORTEX brain"""
from src.tier1.working_memory import WorkingMemory
import sys
import re

# Read plan.md
with open(r'd:\PROJECTS\CORTEX\.github\CopilotChats\plan.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Split by speaker markers
user_turns = []
assistant_turns = []

# Find all user messages
user_matches = list(re.finditer(r'^asifhussain60: (.+?)(?=^(?:GitHub Copilot:|asifhussain60:)|\Z)', content, re.MULTILINE | re.DOTALL))
for match in user_matches:
    user_turns.append(match.group(1).strip())

# Find all assistant messages  
assistant_matches = list(re.finditer(r'^GitHub Copilot: (.+?)(?=^(?:asifhussain60:|GitHub Copilot:)|\Z)', content, re.MULTILINE | re.DOTALL))
for match in assistant_matches:
    assistant_turns.append(match.group(1).strip())

# Interleave turns (assumption: alternating user/assistant)
turns = []
for i in range(max(len(user_turns), len(assistant_turns))):
    if i < len(user_turns):
        turns.append({'user': user_turns[i]})
    if i < len(assistant_turns):
        turns.append({'assistant': assistant_turns[i]})

# Import to CORTEX
print(f"Found {len(turns)} conversation turns")
wm = WorkingMemory()
result = wm.import_conversation(
    conversation_turns=turns,
    import_source='plan.md',
    workspace_path=r'd:\PROJECTS\CORTEX'
)

print(f'\n✅ Import Complete')
print(f'Success: {result["success"]}')
print(f'Conversation ID: {result["conversation_id"]}')
print(f'Quality Score: {result["quality_score"]}/10')
print(f'Quality Level: {result["quality_level"]}')
print(f'Turns Imported: {result["turns_imported"]}')
