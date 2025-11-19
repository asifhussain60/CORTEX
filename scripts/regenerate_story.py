"""Quick script to regenerate story with fixed chapters"""
from pathlib import Path
from src.plugins.story_generator_plugin import StoryGeneratorPlugin

plugin = StoryGeneratorPlugin({'root_path': Path.cwd()})
plugin.initialize()
result = plugin.execute({'dry_run': False, 'chapters': 10})
print(f"\n✅ Success: {result['success']}")
print(f"Chapters: {result.get('chapters_generated', 0)}")
print(f"Total words: {result.get('total_words', 0):,}")
