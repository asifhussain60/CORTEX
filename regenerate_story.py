"""
Quick test to regenerate the story with narrator voice
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.plugins.story_generator_plugin import StoryGeneratorPlugin

def main():
    """Regenerate story with narrator voice"""
    print("=" * 80)
    print("Regenerating CORTEX Story with Narrator Voice")
    print("=" * 80)
    print()
    
    # Initialize plugin
    plugin = StoryGeneratorPlugin(config={
        "root_path": str(Path.cwd())
    })
    
    if not plugin.initialize():
        print("❌ Plugin initialization failed")
        return False
    
    # Generate story (NOT dry run - actually create files)
    context = {
        "dry_run": False,  # Actually create files
        "chapters": 10,  # All 10 chapters
        "max_words_per_chapter": 5000
    }
    
    result = plugin.execute(context)
    
    if result.get("success"):
        print("\n✅ Story generation complete!")
        print(f"   Chapters: {result.get('chapters_generated', 0)}")
        print(f"   Total words: {result.get('total_words', 0)}")
        print(f"   Files created: {len(result.get('files_created', []))}")
        return True
    else:
        print("\n❌ Story generation failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
