# src.tier1.session_token

CORTEX Tier 1: Session Token Manager
Provides persistent conversation IDs across chat restarts.

Purpose:
- Generate unique, persistent session tokens
- Store token associations with conversations
- Enable "continue" to resume the exact same conversation
- Track session lifecycle (active, paused, completed)
- Bridge chat restarts with continuous context

Usage:
    from src.tier1.session_token import SessionTokenManager
    
    stm = SessionTokenManager()
    
    # Start a new session
    token = stm.create_session("Implementing auth feature")
    print(f"Session Token: {token}")  # SESSION_20251108_143022_a7b3
    
    # Record conversation association
    stm.associate_conversation(token, "github_copilot_conv_12345")
    
    # Later (even after restart)
    session = stm.get_active_session()
    if session:
        print(f"Resume: {session.description}")
        print(f"Conversation ID: {session.conversation_id}")
    
    # End session
    stm.complete_session(token)
