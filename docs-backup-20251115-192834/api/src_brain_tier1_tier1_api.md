# src.brain.tier1.tier1_api

Tier 1 Unified API
-----------------
High-level wrapper combining all Tier 1 components (ConversationManager,
EntityExtractor, FileTracker) into a single, easy-to-use interface.

This is the PRIMARY entry point for CORTEX agents to interact with Tier 1 storage.

Design Philosophy:
- Single Responsibility: This class ONLY coordinates Tier 1 components
- Auto-extraction: Automatically extracts entities and tracks files from conversations
- Smart defaults: Reasonable defaults for all operations
- Performance: <100ms for common operations

Example Usage:
    from src.brain.tier1.tier1_api import Tier1API
    
    # Initialize
    api = Tier1API(db_path="cortex-brain/cortex-brain.db")
    
    # Log a conversation (auto-extracts entities and tracks files)
    conv_id = api.log_conversation(
        agent_name="copilot",
        request="Fix bug in auth.py",
        response="Fixed authentication issue",
        related_files=["src/auth.py"]
    )
    
    # Search conversations
    results = api.search("authentication bug")
    
    # Get co-modified files
    patterns = api.get_file_patterns("src/auth.py", min_confidence=0.3)

## Functions

### `get_tier1_api(db_path)`

Convenience function to get a Tier1API instance.

Args:
    db_path: Path to SQLite database

Returns:
    Initialized Tier1API instance

Example:
    from src.brain.tier1.tier1_api import get_tier1_api
    
    api = get_tier1_api()
    api.log_conversation(...)
