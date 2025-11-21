"""
Quick test script to validate story generation pipeline
Tests that hilarious.md master source is read correctly
"""

import sys
from pathlib import Path

# Add CORTEX root to path
cortex_root = Path(__file__).parent
sys.path.insert(0, str(cortex_root))
sys.path.insert(0, str(cortex_root / "cortex-brain" / "admin" / "scripts" / "documentation"))

from enterprise_documentation_orchestrator import EnterpriseDocumentationOrchestrator

def test_story_generation():
    """Test that story generation reads from hilarious.md"""
    print("🧠 CORTEX Story Generation Test")
    print("="*80)
    
    # Initialize orchestrator
    orchestrator = EnterpriseDocumentationOrchestrator(cortex_root)
    
    # Test story generation (dry run)
    print("\n📖 Testing story generation (dry run)...")
    result = orchestrator.execute(
        profile="standard",
        dry_run=False,
        stage="story"
    )
    
    if result.success:
        print("\n✅ Story generation successful!")
        print(f"   Chapters: {result.data.get('story', {}).get('chapters', 0)}")
        print(f"   Source: {result.data.get('story', {}).get('validation', {}).get('source', 'unknown')}")
        print(f"   Style: {result.data.get('story', {}).get('validation', {}).get('style', 'unknown')}")
        
        # Verify hilarious.md was used
        source = result.data.get('story', {}).get('validation', {}).get('source', '')
        if 'hilarious.md' in source:
            print("\n🎉 SUCCESS: Story generated from hilarious.md master source!")
        else:
            print(f"\n⚠️  WARNING: Unexpected source: {source}")
    else:
        print("\n❌ Story generation failed!")
        print(f"   Error: {result.message}")
        for error in result.errors:
            print(f"   - {error}")
    
    print("="*80)

if __name__ == "__main__":
    test_story_generation()
