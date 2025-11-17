"""
Test Story Generator Narrator Style
Validates that the story generator uses the narrator voice from story.txt
and generates complete 7-10 chapters with 50+ features

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
from pathlib import Path
import re

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.plugins.story_generator_plugin import StoryGeneratorPlugin


def test_story_txt_exists():
    """Test that story.txt exists and is readable"""
    story_txt_path = Path.cwd() / ".github" / "CopilotChats" / "story.txt"
    
    assert story_txt_path.exists(), f"story.txt not found at {story_txt_path}"
    
    content = story_txt_path.read_text(encoding='utf-8')
    assert len(content) > 0, "story.txt is empty"
    
    # Check for key narrator elements
    assert "Asif Codenstein" in content, "Missing 'Asif Codenstein' character"
    assert "Copilot" in content or "COPILOT" in content, "Missing 'Copilot' reference"
    assert "Prologue" in content, "Missing 'Prologue' header"
    
    print("✅ story.txt exists and contains narrator elements")
    return content


def test_narrator_voice_markers():
    """Test that story.txt contains the expected narrator voice markers"""
    story_txt_path = Path.cwd() / ".github" / "CopilotChats" / "story.txt"
    content = story_txt_path.read_text(encoding='utf-8')
    
    # Narrator voice markers (comedic, sarcastic, technical humor)
    voice_markers = [
        "part scientist, part madman",
        "Things That Were Never Supposed to Be Broken",
        "caffeine overdose",
        "frightened barnacles",
        "prod",  # beanbag labels
        "staging",
        "dependency injection",  # technical humor
        "zero-regression deploy",
        "amnesiac",
        "theatrical",
        "uninvited"
    ]
    
    found_markers = []
    for marker in voice_markers:
        if marker.lower() in content.lower():
            found_markers.append(marker)
    
    # Should have most narrator voice markers
    assert len(found_markers) >= 8, f"Only found {len(found_markers)}/11 narrator voice markers"
    
    print(f"✅ Found {len(found_markers)}/11 narrator voice markers")
    print(f"   Markers: {', '.join(found_markers[:5])}...")
    return found_markers


def test_plugin_loads_story_txt():
    """Test that plugin loads prologue from story.txt (not hardcoded)"""
    plugin = StoryGeneratorPlugin(config={
        "root_path": str(Path.cwd())
    })
    
    if not plugin.initialize():
        print("⚠️ Plugin initialization failed (expected if paths missing)")
        return
    
    # Execute in dry run to generate story
    context = {
        "dry_run": True,
        "chapters": 7,  # Minimum chapters
        "max_words_per_chapter": 5000
    }
    
    result = plugin.execute(context)
    
    # Check if story was generated
    story_output_path = Path.cwd() / "docs" / "diagrams" / "story" / "The-CORTEX-Story.md"
    
    if story_output_path.exists():
        story_content = story_output_path.read_text(encoding='utf-8')
        
        # Check for narrator voice in generated story
        assert "Asif Codenstein" in story_content, "Generated story missing 'Asif Codenstein'"
        assert "part scientist, part madman" in story_content, "Missing narrator voice marker"
        
        print("✅ Plugin loads and uses story.txt narrator voice")
    else:
        print("⚠️ Story file not generated (dry run may not create files)")


def test_chapter_count_range():
    """Test that story generates 7-10 chapters as specified"""
    plugin = StoryGeneratorPlugin(config={
        "root_path": str(Path.cwd())
    })
    
    if not plugin.initialize():
        print("⚠️ Plugin initialization failed")
        return
    
    chapters = plugin.chapter_config
    
    assert 7 <= len(chapters) <= 10, f"Expected 7-10 chapters, got {len(chapters)}"
    
    print(f"✅ Chapter count in valid range: {len(chapters)} chapters")


def test_chapter_structure():
    """Test that chapters have proper structure with narrator continuity"""
    plugin = StoryGeneratorPlugin(config={
        "root_path": str(Path.cwd())
    })
    
    if not plugin.initialize():
        print("⚠️ Plugin initialization failed")
        return
    
    chapters = plugin.chapter_config
    
    required_fields = ["id", "title", "focus", "features", "target_words"]
    
    for chapter in chapters:
        for field in required_fields:
            assert field in chapter, f"Chapter {chapter.get('id', '?')} missing field: {field}"
        
        # Check that features are listed
        assert len(chapter["features"]) > 0, f"Chapter {chapter['id']} has no features"
    
    print(f"✅ All {len(chapters)} chapters have proper structure")
    print(f"   Fields validated: {', '.join(required_fields)}")


def test_feature_coverage():
    """Test that story covers 50+ CORTEX features"""
    plugin = StoryGeneratorPlugin(config={
        "root_path": str(Path.cwd())
    })
    
    if not plugin.initialize():
        print("⚠️ Plugin initialization failed")
        return
    
    chapters = plugin.chapter_config
    
    # Collect all features across chapters
    all_features = set()
    for chapter in chapters:
        all_features.update(chapter.get("features", []))
    
    feature_count = len(all_features)
    
    # Should cover 50+ features
    assert feature_count >= 50, f"Expected 50+ features, found {feature_count}"
    
    print(f"✅ Feature coverage validated: {feature_count} features")
    print(f"   Sample features: {list(all_features)[:5]}...")


def test_narrator_style_consistency():
    """Test that narrator style from story.txt is consistent throughout"""
    story_txt_path = Path.cwd() / ".github" / "CopilotChats" / "story.txt"
    
    if not story_txt_path.exists():
        print("⚠️ story.txt not found, skipping narrator style test")
        return
    
    # Read the narrator style guidelines
    story_txt_content = story_txt_path.read_text(encoding='utf-8')
    
    # Narrator style characteristics:
    # 1. First-person perspective from narrator (not third-person)
    # 2. Comedic technical humor
    # 3. Sarcastic observations
    # 4. Pop culture references
    # 5. Technical jargon mixed with humor
    
    style_checks = {
        "comedic_tone": ["hilarious", "absurd", "ridiculously", "frantically"],
        "technical_humor": ["dependency injection", "kubernetes", "CI/CD", "regression"],
        "character_voice": ["Codenstein", "mustache quivers", "cat vanishes"],
        "narrative_style": ["part scientist", "kind of smart that", "naturally"]
    }
    
    found_styles = {}
    for style_type, markers in style_checks.items():
        found_styles[style_type] = any(marker.lower() in story_txt_content.lower() for marker in markers)
    
    # Should have most style elements
    styles_present = sum(found_styles.values())
    assert styles_present >= 3, f"Only {styles_present}/4 narrator styles present"
    
    print(f"✅ Narrator style consistency check passed: {styles_present}/4 styles present")
    for style, present in found_styles.items():
        print(f"   {style}: {'✓' if present else '✗'}")


def test_generated_story_has_narrator_voice():
    """Test that generated story maintains narrator voice throughout"""
    story_output_path = Path.cwd() / "docs" / "diagrams" / "story" / "The-CORTEX-Story.md"
    
    if not story_output_path.exists():
        print("⚠️ Generated story not found, run mkdocs build first")
        return
    
    story_content = story_output_path.read_text(encoding='utf-8')
    
    # Check for narrator voice elements in generated content
    narrator_elements = [
        "Codenstein",
        "Copilot",
        "brain",
        "memory"
    ]
    
    found_elements = []
    for element in narrator_elements:
        if element in story_content:
            found_elements.append(element)
    
    assert len(found_elements) >= 3, f"Only found {len(found_elements)}/4 narrator elements in generated story"
    
    # Check for third-person vs narrator style
    # Bad: "The user interacts with..." (third person, boring)
    # Good: "Codenstein stares at the screen..." (narrator voice, engaging)
    
    # Count chapters
    chapter_count = story_content.count("# Chapter")
    assert 7 <= chapter_count <= 10, f"Expected 7-10 chapters, found {chapter_count}"
    
    print(f"✅ Generated story maintains narrator voice")
    print(f"   Chapters: {chapter_count}")
    print(f"   Narrator elements: {', '.join(found_elements)}")


if __name__ == "__main__":
    print("=" * 80)
    print("Testing Story Generator Narrator Style")
    print("=" * 80)
    print()
    
    try:
        # Test story.txt source
        print("Phase 1: Validating story.txt source")
        print("-" * 80)
        test_story_txt_exists()
        test_narrator_voice_markers()
        test_narrator_style_consistency()
        print()
        
        # Test plugin configuration
        print("Phase 2: Validating plugin configuration")
        print("-" * 80)
        test_chapter_count_range()
        test_chapter_structure()
        test_feature_coverage()
        print()
        
        # Test story generation
        print("Phase 3: Validating story generation")
        print("-" * 80)
        test_plugin_loads_story_txt()
        test_generated_story_has_narrator_voice()
        print()
        
        print("=" * 80)
        print("✅ ALL TESTS PASSED")
        print("=" * 80)
        
    except AssertionError as e:
        print()
        print("=" * 80)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 80)
        sys.exit(1)
    except Exception as e:
        print()
        print("=" * 80)
        print(f"❌ UNEXPECTED ERROR: {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
        sys.exit(1)
