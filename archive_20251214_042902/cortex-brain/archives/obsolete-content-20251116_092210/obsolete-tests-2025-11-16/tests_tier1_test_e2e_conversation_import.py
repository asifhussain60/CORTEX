"""
End-to-End Validation: Real Conversation Import

Tests the complete import workflow with the actual Milestone 1 completion conversation.

Author: Asif Hussain
Copyright: © 2024-2025
"""

import pytest
from pathlib import Path
from src.tier1.working_memory import WorkingMemory
from src.tier1.migration_add_conversation_import import migrate_add_conversation_import


def test_e2e_milestone_1_conversation_import(tmp_path):
    """
    E2E test with real Milestone 1 completion conversation.
    
    This validates the entire system works end-to-end.
    """
    # Setup
    db_path = tmp_path / "e2e-test.db"
    wm = WorkingMemory(db_path)
    migrate_add_conversation_import(str(db_path))
    
    # Real conversation data from Milestone 1 completion
    conversation_turns = [
        {
            'user': 'Follow instructions in CORTEX.prompt.md. Complete Milestone 1',
            'assistant': '''
            🧠 CORTEX Phase B Milestone 1 Completion
            
            🎯 My Understanding: You want to complete Milestone 1 of Path 1 Phase B.
            
            ⚠️ **Challenge:** ✓ **Accept** - Good timing with clear roadmap ready.
            
            💬 Response: I'll systematically fix tests, build vault storage, and validate E2E.
            
            📝 Your Request: Complete Milestone 1
            
            🔍 Next Steps:
               1. Fix conversation import tests (10/10 passing)
               2. Build vault storage system  
               3. Write user documentation
               4. End-to-end validation
            '''
        },
        {
            'user': 'proceed',
            'assistant': '''
            Fixed ConversationManager API compatibility.
            Updated MessageStore usage from store_message to add_messages.
            Applied migration in test fixtures.
            
            Result: 10/10 tests passing! ✅
            '''
        },
        {
            'user': 'continue',
            'assistant': '''
            Built conversation vault storage with:
            - ConversationVaultManager for file management
            - Metadata indexing system
            - Quality-based filtering
            - Vault statistics
            
            Result: 9/9 vault tests passing! ✅
            '''
        }
    ]
    
    # Import
    result = wm.import_conversation(
        conversation_turns=conversation_turns,
        import_source="copilot-chat-milestone-1-completion.md",
        workspace_path="/d/PROJECTS/CORTEX"
    )
    
    # Validate results
    assert result['conversation_id'] is not None
    assert result['turns_imported'] == 3
    assert result['quality_level'] in ['EXCELLENT', 'GOOD']
    assert result['quality_score'] >= 6  # Should be GOOD at minimum
    
    # Verify semantic elements detected
    elements = result['semantic_elements']
    assert elements['multi_phase_planning'] == True  # "Phase B Milestone 1", "Next Steps", etc.
    assert elements['phase_count'] >= 3  # Detected multiple phases
    assert elements['challenge_accept_flow'] == True  # "Challenge: Accept"
    assert elements['next_steps_provided'] == True  # Has "Next Steps" section
    
    # Verify database storage
    import sqlite3
    import json
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT conversation_id, conversation_type, quality_score, semantic_elements
        FROM conversations
        WHERE conversation_id = ?
    """, (result['conversation_id'],))
    
    row = cursor.fetchone()
    assert row is not None
    assert row[1] == 'imported'  # conversation_type
    assert row[2] == result['quality_score']  # quality_score
    
    # Verify semantic elements stored as JSON
    stored_elements = json.loads(row[3]) if row[3] else {}
    assert stored_elements.get('multi_phase_planning') == True
    
    conn.close()
    
    print("\n" + "="*70)
    print("🎉 E2E VALIDATION COMPLETE!")
    print("="*70)
    print(f"✅ Conversation imported: {result['conversation_id']}")
    print(f"✅ Quality detected: {result['quality_level']} ({result['quality_score']} points)")
    print(f"✅ Turns processed: {result['turns_imported']}")
    print(f"✅ Semantic elements: {sum(1 for v in elements.values() if v)}")
    print("="*70)
    print("\n🏆 Milestone 1 Complete: Conversation Import System VALIDATED")
    print("="*70 + "\n")


def test_e2e_quick_fix_conversation(tmp_path):
    """
    E2E test with a simple low-quality conversation for contrast.
    
    Validates that quality scoring correctly identifies quick fixes.
    """
    db_path = tmp_path / "e2e-quick-fix.db"
    wm = WorkingMemory(db_path)
    migrate_add_conversation_import(str(db_path))
    
    # Simple quick fix conversation
    conversation_turns = [
        {
            'user': 'Change button color to purple',
            'assistant': 'Updated `styles/button.css` with purple color.'
        }
    ]
    
    result = wm.import_conversation(
        conversation_turns=conversation_turns,
        import_source="quick-fix.md"
    )
    
    # Should be LOW or FAIR quality
    assert result['quality_level'] in ['LOW', 'FAIR']
    assert result['quality_score'] <= 5
    assert result['turns_imported'] == 1
    
    print(f"\n✅ Quick fix correctly scored as {result['quality_level']} ({result['quality_score']} points)")


if __name__ == "__main__":
    # Run E2E validation
    import tempfile
    import shutil
    
    print("\n" + "="*70)
    print("CORTEX 3.0 - Milestone 1 E2E Validation")
    print("="*70 + "\n")
    
    tmp_dir = Path(tempfile.mkdtemp())
    
    try:
        test_e2e_milestone_1_conversation_import(tmp_dir)
        test_e2e_quick_fix_conversation(tmp_dir)
        
        print("\n" + "="*70)
        print("✅ ALL E2E TESTS PASSED")
        print("="*70 + "\n")
        
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
