"""
Test Script: First-Time Setup Detection

This script validates that CORTEX correctly detects when setup is needed
and provides clear guidance to users.

Author: Asif Hussain
"""

import sys
import tempfile
import shutil
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.entry_point.cortex_entry import CortexEntry


def test_setup_detection_missing_brain():
    """Test that CORTEX detects missing brain structure."""
    print("="*80)
    print("TEST 1: Missing Brain Structure Detection")
    print("="*80)
    
    # Create temporary directory for test
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_brain = Path(temp_dir) / "test-cortex-brain"
        
        print(f"\n1. Testing with non-existent brain path: {temp_brain}")
        
        try:
            # This should trigger the setup detection
            entry = CortexEntry(brain_path=str(temp_brain), enable_logging=False)
            print("   ❌ FAILED: Should have raised RuntimeError")
            return False
        except RuntimeError as e:
            expected_message = "CORTEX setup required"
            if expected_message in str(e):
                print(f"   ✅ PASSED: Correctly detected missing brain")
                print(f"   Message: {e}")
                return True
            else:
                print(f"   ❌ FAILED: Wrong error message: {e}")
                return False
        except Exception as e:
            print(f"   ❌ FAILED: Unexpected error: {e}")
            return False


def test_setup_detection_partial_brain():
    """Test that CORTEX detects incomplete brain structure."""
    print("\n" + "="*80)
    print("TEST 2: Incomplete Brain Structure Detection")
    print("="*80)
    
    # Create temporary directory with partial structure
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_brain = Path(temp_dir) / "test-cortex-brain"
        temp_brain.mkdir(parents=True)
        
        # Create only tier1 directory (missing tier2, tier3, and databases)
        (temp_brain / "tier1").mkdir()
        
        print(f"\n1. Testing with incomplete brain (only tier1 dir): {temp_brain}")
        
        try:
            entry = CortexEntry(brain_path=str(temp_brain), enable_logging=False)
            print("   ❌ FAILED: Should have raised RuntimeError")
            return False
        except RuntimeError as e:
            expected_message = "CORTEX setup required"
            if expected_message in str(e):
                print(f"   ✅ PASSED: Correctly detected incomplete brain")
                print(f"   Message: {e}")
                return True
            else:
                print(f"   ❌ FAILED: Wrong error message: {e}")
                return False
        except Exception as e:
            print(f"   ❌ FAILED: Unexpected error: {e}")
            return False


def test_skip_setup_check():
    """Test that skip_setup_check parameter works."""
    print("\n" + "="*80)
    print("TEST 3: Skip Setup Check Parameter")
    print("="*80)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_brain = Path(temp_dir) / "test-cortex-brain"
        
        print(f"\n1. Testing with skip_setup_check=True: {temp_brain}")
        
        try:
            # This should NOT trigger setup detection
            entry = CortexEntry(
                brain_path=str(temp_brain),
                enable_logging=False,
                skip_setup_check=True
            )
            print("   ✅ PASSED: Skip check worked, no RuntimeError raised")
            return True
        except RuntimeError as e:
            print(f"   ❌ FAILED: Setup check was not skipped: {e}")
            return False
        except Exception as e:
            # Other errors are expected (missing databases, etc.)
            # This is okay - we just want to verify setup check was skipped
            print(f"   ✅ PASSED: Skip check worked (other error expected): {type(e).__name__}")
            return True


def main():
    """Run all tests."""
    print("\n🧠 CORTEX First-Time Setup Detection Tests\n")
    
    results = []
    
    # Run tests
    results.append(("Missing Brain", test_setup_detection_missing_brain()))
    results.append(("Incomplete Brain", test_setup_detection_partial_brain()))
    results.append(("Skip Check", test_skip_setup_check()))
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {test_name}")
    
    print(f"\n   Results: {passed}/{total} tests passed")
    print("="*80)
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
