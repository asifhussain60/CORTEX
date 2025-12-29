"""
Analyze CopilotChats.md conversation structure and extract semantic patterns.
Compare with ambient daemon capture capabilities.

CORTEX 2.0 - Dual-Channel Learning Analysis
"""
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Read CopilotChats.md
copilot_chats = (Path(__file__).resolve().parent.parent / ".github" / "CopilotChats.md").read_text(encoding='utf-8')

# Parse conversations (split by user prompts)
conversations = re.split(r'^asifhussain60:', copilot_chats, flags=re.MULTILINE)

# Analyze conversation structure
analysis = {
    'total_conversations': len(conversations) - 1,  # First split is before first prompt
    'patterns_found': [],
    'semantic_elements': {
        'challenges_offered': 0,
        'alternatives_proposed': 0,
        'phase_planning': 0,
        'design_decisions': 0,
        'next_steps_provided': 0
    },
    'technical_context': [],
    'files_mentioned': []
}

for conv in conversations[1:]:  # Skip empty first split
    # Look for CORTEX response template patterns
    if 'CORTEX' in conv:
        analysis['patterns_found'].append('cortex_template')
    if 'Challenge:' in conv:
        analysis['semantic_elements']['challenges_offered'] += 1
        # Extract challenge reasoning
        challenge_match = re.search(r'Challenge: (.*?)(?=\n\n|\n[A-Z])', conv, re.DOTALL)
        if challenge_match:
            analysis['patterns_found'].append(f"Challenge: {challenge_match.group(1)[:100]}")
    if 'Alternative' in conv or 'Better solution' in conv:
        analysis['semantic_elements']['alternatives_proposed'] += 1
    if 'Phase' in conv and ('Phase 1' in conv or 'Phase 2' in conv):
        analysis['semantic_elements']['phase_planning'] += 1
    if 'Next Steps:' in conv:
        analysis['semantic_elements']['next_steps_provided'] += 1
    
    # Extract file mentions
    file_refs = re.findall(r'`([a-zA-Z0-9_\-/.]+\.(py|md|yaml|json|ps1))`', conv)
    analysis['files_mentioned'].extend([f[0] for f in file_refs])
    
    # Look for design decisions
    if any(keyword in conv for keyword in ['architecture', 'design', 'approach', 'strategy']):
        analysis['semantic_elements']['design_decisions'] += 1

# Deduplicate files
analysis['files_mentioned'] = list(set(analysis['files_mentioned']))

print("=" * 80)
print("COPILOT CONVERSATIONS ANALYSIS")
print("=" * 80)
print(f"\nTotal conversations: {analysis['total_conversations']}")
print(f"\nSemantic Elements Found:")
for element, count in analysis['semantic_elements'].items():
    print(f"  - {element.replace('_', ' ').title()}: {count}")

print(f"\nFiles mentioned: {len(analysis['files_mentioned'])}")
print("Sample files:")
for file in analysis['files_mentioned'][:10]:
    print(f"  - {file}")

print(f"\nPattern samples:")
for i, pattern in enumerate(analysis['patterns_found'][:5], 1):
    print(f"  {i}. {pattern}")

# Now analyze what ambient daemon captures
print("\n" + "=" * 80)
print("AMBIENT DAEMON CAPABILITIES")
print("=" * 80)

daemon_capabilities = {
    'file_changes': {
        'description': 'Monitors file modifications, creates, deletes',
        'data_captured': ['file path', 'event type', 'timestamp', 'pattern (REFACTOR/FEATURE/BUGFIX)', 'activity score'],
        'smart_filtering': 'Filters noise (cache, build artifacts, generated files)',
        'pattern_detection': 'Classifies change type via git diff analysis'
    },
    'terminal_commands': {
        'description': 'Tracks meaningful shell commands',
        'data_captured': ['command', 'command type', 'timestamp'],
        'security': 'Redacts passwords, tokens, credentials',
        'filtering': 'Only captures meaningful commands (pytest, git, build, etc.)'
    },
    'git_operations': {
        'description': 'Captures git commits, merges, checkouts',
        'data_captured': ['hook type', 'timestamp'],
        'integration': 'Git hooks installed in .git/hooks/'
    },
    'vscode_state': {
        'description': 'Periodic capture of open files',
        'data_captured': ['open files', 'active file (limited)'],
        'frequency': 'Every 60 seconds'
    }
}

for capability, details in daemon_capabilities.items():
    print(f"\n{capability.replace('_', ' ').title()}:")
    print(f"  Description: {details['description']}")
    print(f"  Captures: {', '.join(details['data_captured'])}")

# Comparison matrix
print("\n" + "=" * 80)
print("COMPARISON: MANUAL CONVERSATIONS vs AMBIENT DAEMON")
print("=" * 80)

comparison = [
    ('Strategic Planning', 'Copilot conversations capture phase breakdowns, alternatives, risk analysis', 'Ambient daemon sees file changes, not WHY'),
    ('Design Rationale', 'Conversations show challenges, trade-offs, decisions', 'Daemon captures WHAT changed, not decision process'),
    ('Context Continuity', 'Conversations preserve multi-turn discussion flow', 'Daemon captures discrete events, must infer connections'),
    ('Implementation Detail', 'Daemon excels: precise file changes, line-level diffs', 'Conversations discuss high-level, miss exact changes'),
    ('Execution Proof', 'Daemon captures terminal commands, test runs, git commits', 'Conversations may discuss plans that never executed'),
    ('Temporal Accuracy', 'Daemon timestamps are precise, event-driven', 'Conversations timestamped at batch end, not per-message'),
    ('Pattern Learning', 'Conversations show repeated templates (CORTEX format)', 'Daemon learns code patterns (refactor vs feature)'),
]

print("\n{:25s}| {:50s} | {}".format("Dimension", "Copilot Conversations", "Ambient Daemon"))
print("-" * 110)
for dimension, copilot, daemon in comparison:
    print("{:25s}| {:50s} | {}".format(dimension, copilot, daemon))

# Complementarity analysis
print("\n" + "=" * 80)
print("COMPLEMENTARITY ANALYSIS")
print("=" * 80)

print("\nWhat Conversations ADD to Daemon:")
print("  1. Strategic intent & planning phases")
print("  2. Design alternatives & trade-off analysis")
print("  3. Challenge/accept reasoning")
print("  4. Multi-step next actions")
print("  5. Natural language context for 'why' decisions")

print("\nWhat Daemon ADDS to Conversations:")
print("  1. Precise file change events (line-level)")
print("  2. Proof of execution (commands run, tests passed)")
print("  3. Real-time temporal accuracy")
print("  4. Automatic pattern classification (REFACTOR/FEATURE/BUGFIX)")
print("  5. No manual intervention required")

print("\nRECOMMENDATION:")
print("  Build DUAL-CHANNEL learning system:")
print("  - Channel 1 (Ambient): Automatic, high-frequency, execution-focused")
print("  - Channel 2 (Manual): Strategic, planning-focused, context-rich")
print("  - Fusion: Cross-reference conversation plans with daemon execution proof")

# Calculate value score
copilot_value = sum(analysis['semantic_elements'].values())
print(f"\nSemantic Value Score:")
print(f"  Copilot conversations: {copilot_value} semantic elements across {analysis['total_conversations']} conversations")
print(f"  Average per conversation: {copilot_value / max(1, analysis['total_conversations']):.1f} semantic elements")
print(f"  Files referenced: {len(analysis['files_mentioned'])}")

print("\nAnalysis complete!")
