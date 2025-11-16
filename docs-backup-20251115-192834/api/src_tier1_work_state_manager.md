# src.tier1.work_state_manager

CORTEX Tier 1: Work State Manager
Tracks in-progress work to enable seamless "continue" functionality.

Purpose:
- Record current task being worked on
- Track files being modified
- Monitor last activity timestamp
- Persist state across sessions
- Enable proactive resume prompts

Usage:
    from src.tier1.work_state_manager import WorkStateManager
    
    wsm = WorkStateManager()
    
    # Start tracking a new task
    wsm.start_task("Implement user authentication", ["src/auth.py", "tests/test_auth.py"])
    
    # Update progress
    wsm.update_progress("Added login endpoint", files_touched=["src/auth.py"])
    
    # Check if there's incomplete work
    if wsm.has_incomplete_work():
        state = wsm.get_current_state()
        print(f"Resume: {state.task_description}")
    
    # Mark task complete
    wsm.complete_task()
