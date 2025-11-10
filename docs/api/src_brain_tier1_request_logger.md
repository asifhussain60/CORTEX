# src.brain.tier1.request_logger

Raw Request Logger
-----------------
Logs ALL raw user requests and agent responses for debugging and learning purposes.

This module provides privacy-aware logging that:
- Stores complete request/response pairs
- Redacts sensitive information (API keys, passwords, tokens)
- Enables replay for debugging
- Supports learning from user patterns
- Maintains separate log from conversation history (for raw data preservation)

Design Philosophy:
- Privacy First: Automatic redaction of sensitive data
- Debugging: Complete context for issue reproduction
- Learning: Identify user intent patterns and common tasks
- Separation: Raw logs separate from structured conversation history

Example Usage:
    from src.brain.tier1.request_logger import RequestLogger
    
    logger = RequestLogger(db_path="cortex-brain/cortex-brain.db")
    
    # Log raw request/response
    logger.log_raw_request(
        raw_request="Fix the auth bug using my API key abc123xyz",
        raw_response="Fixed authentication issue",
        agent_name="copilot",
        conversation_id="uuid-here"
    )
    # Stored as: "Fix the auth bug using my API key [REDACTED]"

## Functions

### `get_request_logger(db_path)`

Convenience function to get a RequestLogger instance.

Args:
    db_path: Path to SQLite database

Returns:
    Initialized RequestLogger instance

Example:
    from src.brain.tier1.request_logger import get_request_logger
    
    logger = get_request_logger()
    logger.log_raw_request(...)
