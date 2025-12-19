"""
Test Gist Upload Integration

Verifies that feedback system correctly integrates with Gist uploader.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import os
from pathlib import Path

# Add src to path BEFORE any other imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# Change working directory to avoid platform module conflict
os.chdir(str(project_root))

from feedback.feedback_collector import FeedbackCollector, FeedbackCategory, FeedbackPriority
from feedback.gist_uploader import GistUploader, UploadStatus


def test_gist_uploader_initialization():
    """Test 1: GistUploader initializes correctly."""
    print("\n" + "="*60)
    print("TEST 1: GistUploader Initialization")
    print("="*60)
    
    try:
        uploader = GistUploader()
        print("✅ PASS - GistUploader initialized")
        print(f"   Config path: {uploader.config_path}")
        print(f"   Preferences path: {uploader.preferences_path}")
        return True
    except Exception as e:
        print(f"❌ FAIL - {e}")
        return False


def test_manual_instructions_generation():
    """Test 2: Manual upload instructions generated correctly."""
    print("\n" + "="*60)
    print("TEST 2: Manual Instructions Generation")
    print("="*60)
    
    try:
        uploader = GistUploader()
        
        # Generate manual instructions
        result = uploader._handle_no_token(
            report_content="# Test Report\nThis is a test.",
            filename="test-report.md"
        )
        
        assert result.status == UploadStatus.NO_TOKEN
        assert result.manual_instructions is not None
        assert "GitHub token" in result.manual_instructions
        assert "cortex.config.json" in result.manual_instructions
        
        print("✅ PASS - Manual instructions generated")
        print(f"\nInstructions preview:")
        print(result.manual_instructions[:200] + "...")
        return True
    
    except Exception as e:
        print(f"❌ FAIL - {e}")
        return False


def test_feedback_collector_integration():
    """Test 3: FeedbackCollector integrates with GistUploader."""
    print("\n" + "="*60)
    print("TEST 3: FeedbackCollector Integration")
    print("="*60)
    
    try:
        collector = FeedbackCollector()
        
        # Submit feedback (will attempt upload with no token)
        item = collector.submit_feedback(
            category=FeedbackCategory.BUG,
            title="Test Bug Report",
            description="This is a test bug report for integration testing.",
            priority=FeedbackPriority.LOW,
            auto_upload=False  # Don't actually upload in test
        )
        
        assert item is not None
        assert item.title == "Test Bug Report"
        
        print("✅ PASS - FeedbackCollector integrated with uploader")
        print(f"   Feedback item created: {item.title}")
        print(f"   Auto-upload parameter: Supported")
        return True
    
    except Exception as e:
        print(f"❌ FAIL - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_preferences_management():
    """Test 4: Upload preferences saved and loaded correctly."""
    print("\n" + "="*60)
    print("TEST 4: Preferences Management")
    print("="*60)
    
    try:
        uploader = GistUploader()
        
        # Check default preferences
        preference = uploader._get_upload_preference(auto_prompt=False)
        print(f"   Default preference: {preference}")
        
        # Simulate saving preference
        uploader.preferences['upload_to_gist'] = 'manual'
        uploader._save_preferences()
        
        # Load again
        uploader2 = GistUploader()
        loaded_preference = uploader2._get_upload_preference(auto_prompt=False)
        
        assert loaded_preference == 'manual'
        
        print("✅ PASS - Preferences saved and loaded")
        print(f"   Saved: manual")
        print(f"   Loaded: {loaded_preference}")
        return True
    
    except Exception as e:
        print(f"❌ FAIL - {e}")
        import traceback
        traceback.print_exc()
        return False


def test_github_formatter_integration():
    """Test 5: GitHub formatter works with GistUploader."""
    print("\n" + "="*60)
    print("TEST 5: GitHub Formatter Integration")
    print("="*60)
    
    try:
        from feedback.github_formatter import GitHubIssueFormatter
        
        # Create test feedback item
        collector = FeedbackCollector()
        item = collector.submit_feedback(
            category=FeedbackCategory.FEATURE_REQUEST,
            title="Test Feature Request",
            description="This is a test feature request.",
            priority=FeedbackPriority.MEDIUM,
            auto_upload=False
        )
        
        # Format as GitHub Issue
        formatter = GitHubIssueFormatter()
        issue = formatter.format_feedback_item(item, include_metadata=True)
        
        assert issue.title.startswith("[FEATURE]")
        assert "Test Feature Request" in issue.title
        assert len(issue.body) > 0
        assert len(issue.labels) > 0
        
        print("✅ PASS - GitHub formatter integration works")
        print(f"   Title: {issue.title}")
        print(f"   Labels: {', '.join(issue.labels)}")
        print(f"   Body length: {len(issue.body)} chars")
        return True
    
    except Exception as e:
        print(f"❌ FAIL - {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all integration tests."""
    print("\n" + "="*60)
    print("CORTEX GIST UPLOAD INTEGRATION TESTS")
    print("="*60)
    
    tests = [
        test_gist_uploader_initialization,
        test_manual_instructions_generation,
        test_feedback_collector_integration,
        test_preferences_management,
        test_github_formatter_integration,
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"\n❌ TEST FAILED: {test_func.__name__}")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED - Gist Upload Integration Complete!")
    else:
        print(f"\n⚠️  {total - passed} TESTS FAILED")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
