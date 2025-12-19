"""Test script for documentation refresh plugin with Lab Notebook condensation"""

from src.plugins.doc_refresh_plugin import Plugin
from pathlib import Path

# Initialize plugin
plugin = Plugin()
plugin.initialize()

# Load design context
design_context = plugin._load_design_context()

# Test story refresh
story_path = Path('docs/story/CORTEX-STORY/Awakening Of CORTEX.md')
result = plugin._refresh_story_doc(story_path, design_context)

# Display results
print("=" * 60)
print("STORY REFRESH RESULTS")
print("=" * 60)
print(f"Success: {result['success']}")
print(f"Message: {result['message']}")
print()

# Lab Notebook Transformation
if result.get('lab_notebook_transformation'):
    lnt = result['lab_notebook_transformation']
    print("LAB NOTEBOOK TRANSFORMATION:")
    print(f"  Found: {lnt.get('found', False)}")
    if lnt.get('found'):
        print(f"  Original Length: {lnt['original_length']} chars")
        print(f"  Condensed Length: {lnt['condensed_length']} chars")
        print(f"  Reduction: {lnt['reduction_percentage']}%")
        print(f"  Token Savings: {lnt['token_impact']['savings']}")
    print()

# Progressive Recaps
if result.get('progressive_recaps'):
    pr = result['progressive_recaps']
    print("PROGRESSIVE RECAPS:")
    print(f"  Parts Found: {', '.join(pr['found_parts'])}")
    print()
    
    if pr.get('part_2_recap'):
        p2 = pr['part_2_recap']
        print("  PART 2 RECAP (summarizes Part 1):")
        print(f"    Location: {p2['location']}")
        print(f"    Style: {p2['style']}")
        print(f"    Compression: {p2['compression_level']}")
        print(f"    Token Estimate: {p2['token_estimate']}")
        print(f"    Preview: {p2['content'][:150]}...")
        print()
    
    if pr.get('part_3_recap'):
        p3 = pr['part_3_recap']
        print("  PART 3 RECAP (summarizes Part 2 + Part 1):")
        print(f"    Location: {p3['location']}")
        print(f"    Style: {p3['style']}")
        print(f"    Compression: {p3['compression_level']}")
        print(f"    Token Estimate: {p3['token_estimate']}")
        print(f"    Preview: {p3['content'][:150]}...")
        print()

# Milestones
print(f"Milestones Detected: {result['milestones_detected']}")
print()

# Narrative Analysis
if result.get('narrative_analysis'):
    na = result['narrative_analysis']
    print("NARRATIVE ANALYSIS:")
    print(f"  Structure: {na.get('structure')}")
    print(f"  Parts: {na.get('parts_detected')}")
    print(f"  Chapters: {na.get('chapters_detected')}")
    print(f"  Interludes: {na.get('interludes_detected')}")
    print(f"  Tone: {na.get('tone')}")
    print(f"  Warnings: {len(na.get('warnings', []))}")
    print()

# Flow Validation
if result.get('flow_validation'):
    fv = result['flow_validation']
    print("FLOW VALIDATION:")
    print(f"  Valid: {fv.get('valid')}")
    print(f"  Warnings: {len(fv.get('warnings', []))}")
    print(f"  Suggestions: {len(fv.get('suggestions', []))}")
    print()

# Recap Suggestions (first 5)
if result.get('recap_suggestions'):
    print("RECAP SUGGESTIONS (first 5):")
    for i, suggestion in enumerate(result['recap_suggestions'][:5], 1):
        print(f"  {i}. {suggestion}")
    print()

print(f"Action Required: {result.get('action_required')}")
print("=" * 60)
