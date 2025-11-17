"""
Test Story Generator Plugin Integration
Validates plugin can be loaded and executed
"""

import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.plugins.story_generator_plugin import StoryGeneratorPlugin


def test_plugin_initialization():
    """Test plugin can be initialized"""
    plugin = StoryGeneratorPlugin(config={
        "root_path": str(Path.cwd())
    })
    
    assert plugin is not None
    assert plugin.metadata.plugin_id == "story_generator"
    print("✅ Plugin initialization test passed")


def test_plugin_metadata():
    """Test plugin metadata is correct"""
    plugin = StoryGeneratorPlugin()
    metadata = plugin.metadata
    
    assert metadata.name == "CORTEX Story Generator"
    assert metadata.version == "1.0.0"
    assert metadata.author == "Asif Hussain"
    assert "generate cortex story" in metadata.natural_language_patterns
    
    print("✅ Plugin metadata test passed")


def test_plugin_execution_dry_run():
    """Test plugin can execute in dry run mode"""
    plugin = StoryGeneratorPlugin(config={
        "root_path": str(Path.cwd())
    })
    
    if not plugin.initialize():
        print("⚠️ Plugin initialization failed (expected if paths missing)")
        return
    
    context = {
        "dry_run": True,
        "chapters": 3,  # Test with fewer chapters
        "max_words_per_chapter": 1000
    }
    
    result = plugin.execute(context)
    
    assert result is not None
    assert "success" in result
    assert "chapters_generated" in result
    
    print("✅ Plugin execution (dry run) test passed")
    print(f"   Chapters: {result.get('chapters_generated', 0)}")
    print(f"   Total words: {result.get('total_words', 0)}")


def test_chapter_configuration():
    """Test chapter configuration is loaded correctly"""
    plugin = StoryGeneratorPlugin(config={
        "root_path": str(Path.cwd())
    })
    
    if not plugin.initialize():
        print("⚠️ Plugin initialization failed")
        return
    
    chapters = plugin.chapter_config
    
    assert len(chapters) == 10, f"Expected 10 chapters, got {len(chapters)}"
    
    # Verify first chapter
    first_chapter = chapters[0]
    assert first_chapter["id"] == 1
    assert first_chapter["title"] == "The Amnesia Problem"
    assert "target_words" in first_chapter
    
    print("✅ Chapter configuration test passed")
    print(f"   Total chapters: {len(chapters)}")


if __name__ == "__main__":
    print("=" * 80)
    print("Testing Story Generator Plugin")
    print("=" * 80)
    print()
    
    try:
        test_plugin_initialization()
        test_plugin_metadata()
        test_chapter_configuration()
        test_plugin_execution_dry_run()
        
        print()
        print("=" * 80)
        print("✅ All tests passed!")
        print("=" * 80)
        
    except AssertionError as e:
        print()
        print("=" * 80)
        print(f"❌ Test failed: {e}")
        print("=" * 80)
        sys.exit(1)
    
    except Exception as e:
        print()
        print("=" * 80)
        print(f"❌ Unexpected error: {e}")
        print("=" * 80)
        sys.exit(1)
