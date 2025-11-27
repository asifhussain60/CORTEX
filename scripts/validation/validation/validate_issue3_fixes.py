"""
Quick validation script for Issue #3 fixes
Runs basic tests without pytest framework
"""

import sys
from pathlib import Path
import tempfile
import shutil

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from agents.feedback_agent import FeedbackAgent
from agents.view_discovery_agent import ViewDiscoveryAgent

def test_feedback_agent():
    """Test FeedbackAgent basic functionality."""
    print("\n🧪 Testing FeedbackAgent...")
    
    temp_dir = Path(tempfile.mkdtemp())
    try:
        brain_path = temp_dir / "cortex-brain"
        agent = FeedbackAgent(brain_path=str(brain_path))
        
        result = agent.create_feedback_report(
            user_input="Test feedback: TDD workflow needs improvement",
            feedback_type="improvement",
            severity="medium"
        )
        
        assert result["success"] is True, "Feedback creation should succeed"
        assert "CORTEX-FEEDBACK-" in result["feedback_id"], "Should have feedback ID"
        assert Path(result["file_path"]).exists(), "Report file should exist"
        
        print(f"✅ FeedbackAgent test passed!")
        print(f"   - Created report: {result['feedback_id']}")
        print(f"   - File path: {result['file_path']}")
        
        return True
        
    except Exception as e:
        print(f"❌ FeedbackAgent test failed: {e}")
        return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_view_discovery_agent():
    """Test ViewDiscoveryAgent basic functionality."""
    print("\n🧪 Testing ViewDiscoveryAgent...")
    
    temp_dir = Path(tempfile.mkdtemp())
    try:
        # Create test Razor file
        views_dir = temp_dir / "Views"
        views_dir.mkdir()
        
        test_razor = views_dir / "TestPage.razor"
        test_razor.write_text("""
@page "/test"

<h1>Test Page</h1>
<button id="testButton" class="btn">Click Me</button>
<input id="testInput" type="text" />
<button data-testid="submit-btn">Submit</button>
""", encoding='utf-8')
        
        # Run discovery
        agent = ViewDiscoveryAgent(project_root=temp_dir)
        results = agent.discover_views([test_razor])
        
        assert len(results["elements_discovered"]) > 0, "Should discover elements"
        assert len(results["files_processed"]) == 1, "Should process 1 file"
        
        # Check for specific elements
        element_ids = [e["element_id"] for e in results["elements_discovered"] if e["element_id"]]
        assert "testButton" in element_ids, "Should find testButton ID"
        assert "testInput" in element_ids, "Should find testInput ID"
        
        # Check selector strategies
        strategies = results["selector_strategies"]
        assert "testButton" in strategies, "Should have strategy for testButton"
        assert strategies["testButton"] == "#testButton", "Should use ID selector"
        
        print(f"✅ ViewDiscoveryAgent test passed!")
        print(f"   - Discovered {len(results['elements_discovered'])} elements")
        print(f"   - Found element IDs: {element_ids}")
        print(f"   - Selector strategies: {len(strategies)} mappings")
        
        return True
        
    except Exception as e:
        print(f"❌ ViewDiscoveryAgent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    """Run all validation tests."""
    print("=" * 70)
    print("CORTEX Issue #3 Fix - Validation Tests")
    print("=" * 70)
    
    results = []
    
    # Test 1: FeedbackAgent
    results.append(("FeedbackAgent", test_feedback_agent()))
    
    # Test 2: ViewDiscoveryAgent
    results.append(("ViewDiscoveryAgent", test_view_discovery_agent()))
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Issue #3 fixes are working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
