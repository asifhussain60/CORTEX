#!/usr/bin/env python3
"""Display and save the story transformation plan"""
import json
from src.plugins.doc_refresh_plugin import Plugin

# Execute plugin
plugin = Plugin()
plugin.initialize()
result = plugin.execute({'hook': 'on_doc_refresh'})

# Get transformation plan
plan = result.get('transformation_plans', {}).get('Awakening Of CORTEX.md', {})

# Save to file
with open('cortex-brain/story-transformation-plan.json', 'w') as f:
    json.dump(plan, f, indent=2)

print('✅ Transformation plan saved to cortex-brain/story-transformation-plan.json')
print()

# Display summary
print('📊 TRANSFORMATION PLAN SUMMARY')
print('=' * 60)
print()

actions = plan.get('actions', [])
deprecated_action = next((a for a in actions if a.get('action_type') == 'remove_deprecated'), {})
voice_action = next((a for a in actions if a.get('action_type') == 'fix_narrator_voice'), {})
structure_action = next((a for a in actions if a.get('action_type') == 'regenerate_structure'), {})

print(f'🗑️  DEPRECATED SECTIONS: {deprecated_action.get("count", 0)}')
if deprecated_action.get('sections'):
    for section in deprecated_action['sections'][:3]:  # Show first 3
        print(f'   Line {section["line"]}: {section["deprecated_term"]}')
        print(f'   → {section["replacement"]}')
        print()

print(f'📝 NARRATOR VOICE VIOLATIONS: {voice_action.get("count", 0)}')
print(f'   - Passive voice: {voice_action.get("passive_violations", 0)}')
print(f'   - Documentary tone: {voice_action.get("documentary_violations", 0)}')
print()

print(f'🏗️  STORY STRUCTURE:')
print(f'   - Parts: {structure_action.get("parts", 0)}')
print(f'   - Chapters: {structure_action.get("total_chapters", 0)}')
print()

print(f'⚠️  TOTAL ACTIONS REQUIRED: {plan.get("estimated_changes", 0)}')
print(f'📋 REVIEW REQUIRED: {plan.get("review_required", False)}')
