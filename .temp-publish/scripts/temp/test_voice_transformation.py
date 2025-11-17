"""Test voice transformation on Awakening Of CORTEX story"""
import sys
sys.path.insert(0, 'src')
from plugins.doc_refresh_plugin import Plugin
from pathlib import Path

# Initialize plugin with voice transformation enabled
plugin = Plugin()
plugin.config = {
    'transform_narrative_voice': True,
    'voice_transformation_mode': 'mixed',
    'story_recap_enabled': False  # Focus on voice transformation only
}
plugin.initialize()

# Execute on story document
story_path = Path('docs/story/CORTEX-STORY/Awakening Of CORTEX.md')
result = plugin._refresh_story_doc(story_path, {'design_docs': []})

# Display transformation results
if result.get('voice_transformation'):
    vt = result['voice_transformation']
    print(f'\n✅ Voice Transformation Analysis Complete')
    print(f'Transformations Found: {vt["transformations_found"]}')
    print(f'Mode: {vt["mode"]}\n')
    print('=' * 60)
    print('PATTERNS TO TRANSFORM:')
    print('=' * 60)
    for i, pattern in enumerate(vt['patterns'], 1):
        print(f'\n{i}. Type: {pattern["type"]}')
        print(f'   BEFORE: {pattern["original"]}')
        print(f'   AFTER:  {pattern["transformed"]}')
        print()
    
    print('\n' + '=' * 60)
    print('TRANSFORMATION EXAMPLES:')
    print('=' * 60)
    for example in vt['examples']:
        print(f'\nBEFORE: {example["before"]}')
        print(f'AFTER:  {example["after"]}')
else:
    print('❌ No voice transformation data found')
    print(f'Result: {result}')
