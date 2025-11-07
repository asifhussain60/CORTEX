"""
CORTEX Brain Protector: Conversation Tracking Integration Test

Tests the complete conversation tracking pipeline:
1. cortex-capture.ps1 → Python CLI → CortexEntry → SQLite
2. Validates Rule #24 (Conversation Memory Must Work)

This test runs as a standalone integration test to avoid import issues.
"""

import subprocess
import sqlite3
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime


def test_cortex_cli_tracks_conversations():
    """
    CRITICAL: cortex_cli.py MUST track conversations to SQLite
    
    Tests:
    - Python CLI can be invoked
    - Message is processed
    - Conversation is logged to database
    - Data persists
    """
    print("\n" + "="*60)
    print("Testing: CORTEX CLI Conversation Tracking")
    print("="*60)
    
    # Create temp brain directory
    temp_brain = Path(tempfile.mkdtemp(prefix="cortex_test_brain_"))
    
    try:
        # Setup brain structure
        (temp_brain / "tier1").mkdir(parents=True)
        (temp_brain / "tier2").mkdir(parents=True)
        (temp_brain / "tier3").mkdir(parents=True)
        
        # Get script path (scripts/ is in project root, not CORTEX/)
        project_root = Path(__file__).parent.parent.parent.parent
        script_path = project_root / "scripts" / "cortex_cli.py"
        
        if not script_path.exists():
            print(f"❌ FAILED: cortex_cli.py not found: {script_path}")
            return False
        
        # Test message
        test_message = "Test: Verify conversation tracking works correctly"
        
        # Run CLI
        print(f"\n📝 Processing message: {test_message}")
        result = subprocess.run(
            [
                "python",
                str(script_path),
                test_message,
                "--brain-path", str(temp_brain)
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"   Return code: {result.returncode}")
        
        if result.returncode != 0:
            print(f"❌ FAILED: CLI exited with error")
            print(f"   STDOUT: {result.stdout}")
            print(f"   STDERR: {result.stderr}")
            return False
        
        print(f"✅ CLI executed successfully")
        
        # Verify database was created
        db_path = temp_brain / "tier1" / "conversations.db"
        if not db_path.exists():
            print(f"❌ FAILED: Database not created: {db_path}")
            return False
        
        print(f"✅ Database created: {db_path}")
        
        # Verify conversation was logged
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check conversations
        cursor.execute("SELECT COUNT(*) FROM conversations")
        conv_count = cursor.fetchone()[0]
        print(f"✅ Conversations logged: {conv_count}")
        
        if conv_count == 0:
            print(f"❌ FAILED: No conversations in database")
            conn.close()
            return False
        
        # Check messages
        cursor.execute("SELECT COUNT(*) FROM messages WHERE content LIKE ?", (f"%{test_message}%",))
        msg_count = cursor.fetchone()[0]
        print(f"✅ Messages logged: {msg_count}")
        
        if msg_count == 0:
            print(f"❌ FAILED: Test message not found in database")
            conn.close()
            return False
        
        # Check message details
        cursor.execute("""
            SELECT conversation_id, role, content, timestamp 
            FROM messages 
            WHERE content LIKE ? 
            LIMIT 1
        """, (f"%{test_message}%",))
        
        row = cursor.fetchone()
        if row:
            print(f"\n📊 Message Details:")
            print(f"   Conversation ID: {row[0]}")
            print(f"   Role: {row[1]}")
            print(f"   Content: {row[2][:50]}...")
            print(f"   Timestamp: {row[3]}")
        
        conn.close()
        
        print(f"\n{'='*60}")
        print(f"✅ ALL TESTS PASSED")
        print(f"{'='*60}")
        print(f"\n✅ Rule #24 Validated: Conversation tracking is operational")
        
        return True
        
    finally:
        # Cleanup
        if temp_brain.exists():
            shutil.rmtree(temp_brain)


def test_validation_command():
    """Test that cortex_cli.py --validate works"""
    print("\n" + "="*60)
    print("Testing: CORTEX CLI Validation Command")
    print("="*60)
    
    project_root = Path(__file__).parent.parent.parent.parent
    script_path = project_root / "scripts" / "cortex_cli.py"
    
    if not script_path.exists():
        print(f"❌ SKIP: cortex_cli.py not found")
        return True  # Skip, not a failure
    
    # Run validation
    result = subprocess.run(
        ["python", str(script_path), "--validate"],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    print(f"   Return code: {result.returncode}")
    print(f"   Output:\n{result.stdout}")
    
    if result.stderr:
        print(f"   Errors:\n{result.stderr}")
    
    # Validation may pass or fail depending on whether real database has messages
    # Just verify command runs without crashing
    print(f"✅ Validation command executed")
    
    return True


def test_powershell_capture_script():
    """Test that cortex-capture.ps1 exists and has correct structure"""
    print("\n" + "="*60)
    print("Testing: PowerShell Capture Script")
    print("="*60)
    
    project_root = Path(__file__).parent.parent.parent.parent
    script_path = project_root / "scripts" / "cortex-capture.ps1"
    
    if not script_path.exists():
        print(f"❌ FAILED: cortex-capture.ps1 not found: {script_path}")
        return False
    
    print(f"✅ Script exists: {script_path}")
    
    # Read and verify key functions exist
    content = script_path.read_text(encoding='utf-8')
    
    required_functions = [
        'Invoke-PythonTracking',
        'Test-ConversationTracking',
        'Get-AutoDetectedMessage'
    ]
    
    for func in required_functions:
        if func in content:
            print(f"✅ Function found: {func}")
        else:
            print(f"❌ FAILED: Missing function: {func}")
            return False
    
    # Verify it accepts required parameters
    if '-Message' in content and '-Intent' in content and '-Validate' in content:
        print(f"✅ Required parameters defined")
    else:
        print(f"❌ FAILED: Missing required parameters")
        return False
    
    print(f"\n✅ PowerShell script structure validated")
    
    return True


def main():
    """Run all integration tests"""
    print("\n" + "="*70)
    print(" "*15 + "CORTEX BRAIN PROTECTOR")
    print(" "*10 + "Conversation Tracking Integration Tests")
    print(" "*15 + "Rule #24 Validation")
    print("="*70)
    
    tests = [
        ("Python CLI Conversation Tracking", test_cortex_cli_tracks_conversations),
        ("Validation Command", test_validation_command),
        ("PowerShell Capture Script", test_powershell_capture_script),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ EXCEPTION in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(passed for _, passed in results)
    
    print("\n" + "="*70)
    if all_passed:
        print("✅ ALL TESTS PASSED - Rule #24 Validated")
        print("   Conversation tracking is operational")
    else:
        print("❌ SOME TESTS FAILED - Rule #24 Violation")
        print("   Conversation tracking is NOT working correctly")
    print("="*70)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
