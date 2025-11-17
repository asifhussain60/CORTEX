"""
CORTEX Priority 1: Quality Scoring Tests (Expected to FAIL initially)

Tests that validate quality scoring works correctly for NORMAL conversations,
not just CORTEX 5-part formatted responses.

Current Issue: Multi-turn conversations with code/debugging rated LOW instead of FAIR/GOOD

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from src.tier1.conversation_quality import ConversationQualityAnalyzer


class TestMultiTurnConversationQuality:
    """Test quality scoring for multi-turn implementation conversations."""
    
    def setup_method(self):
        self.analyzer = ConversationQualityAnalyzer()
    
    def test_multi_turn_implementation_should_be_good(self):
        """Multi-turn implementation conversation with code should score GOOD or higher."""
        turns = [
            (
                "Add JWT authentication to auth_service.py",
                "I'll add JWT authentication to auth_service.py:\n\n```python\nimport jwt\n\nclass AuthService:\n    def __init__(self):\n        self.secret_key = 'secret'\n    \n    def generate_token(self, user_id):\n        return jwt.encode({'user_id': user_id}, self.secret_key)\n```"
            ),
            (
                "Add token validation method",
                "Here's the validation method:\n\n```python\ndef validate_token(self, token):\n    try:\n        payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])\n        return payload['user_id']\n    except jwt.InvalidTokenError:\n        return None\n```"
            ),
            (
                "Add expiration handling",
                "I'll add expiration:\n\n```python\nfrom datetime import datetime, timedelta\n\ndef generate_token(self, user_id, expires_in=3600):\n    expiry = datetime.utcnow() + timedelta(seconds=expires_in)\n    return jwt.encode({\n        'user_id': user_id,\n        'exp': expiry\n    }, self.secret_key)\n```"
            )
        ]
        
        result = self.analyzer.analyze_multi_turn_conversation(turns)
        
        # Should be GOOD or EXCELLENT due to:
        # - Multi-turn implementation (3 turns)
        # - Code blocks in every turn
        # - File reference (auth_service.py)
        # - Implementation progression (add feature → validate → enhance)
        assert result.level in ["GOOD", "EXCELLENT"], \
            f"Expected GOOD/EXCELLENT for multi-turn implementation, got {result.level} (score: {result.total_score})"
        assert result.total_score >= 6, f"Expected score >= 6, got {result.total_score}"
    
    def test_debugging_conversation_should_be_good(self):
        """Debugging conversation with investigation and fixes should score GOOD."""
        turns = [
            (
                "I'm getting AttributeError: 'NoneType' object has no attribute 'session_id'",
                "Let me check the code where session_id is accessed. This error suggests the session object is None when you're trying to access its session_id attribute."
            ),
            (
                "It's in conversation_manager.py line 45",
                "I see the issue. You need to check if session exists before accessing session_id:\n\n```python\nif session and hasattr(session, 'session_id'):\n    current_session = session.session_id\nelse:\n    current_session = None\n```"
            ),
            (
                "That fixed it, thanks!",
                "Great! The fix prevents the AttributeError by validating the session object exists and has the session_id attribute before accessing it."
            )
        ]
        
        result = self.analyzer.analyze_multi_turn_conversation(turns)
        
        # Should be GOOD due to:
        # - Debugging workflow (error → investigation → fix → confirmation)
        # - Code implementation (fix provided)
        # - File reference (conversation_manager.py)
        # - Multi-turn problem-solving
        assert result.level in ["GOOD", "FAIR"], \
            f"Expected GOOD/FAIR for debugging conversation, got {result.level} (score: {result.total_score})"
        assert result.total_score >= 3, f"Expected score >= 3, got {result.total_score}"
    
    def test_long_conversation_should_be_good(self):
        """Long conversation (10 turns) with implementation details should score GOOD."""
        turns = [
            ("Create a user registration endpoint", "I'll create a user registration endpoint in `api/routes/auth.py`."),
            ("Add password hashing", "I'll add bcrypt password hashing:\n\n```python\nimport bcrypt\nhashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())\n```"),
            ("Validate email format", "Added email validation using regex pattern."),
            ("Check for duplicate emails", "Added database query to check existing users."),
            ("Add error handling", "Added try-except blocks for database errors."),
            ("Return proper HTTP status codes", "Using 201 for success, 400 for validation errors, 409 for duplicates."),
            ("Add logging", "Added logging for registration attempts and failures."),
            ("Write unit tests", "Created test_registration.py with test cases."),
            ("Add API documentation", "Added docstrings and OpenAPI schema."),
            ("Deploy to staging", "Deployed endpoint to staging environment for testing.")
        ]
        
        result = self.analyzer.analyze_multi_turn_conversation(turns)
        
        # Should be GOOD or EXCELLENT due to:
        # - Many turns (10) showing sustained work
        # - Multiple file references
        # - Code implementation
        # - End-to-end feature development
        assert result.level in ["GOOD", "EXCELLENT"], \
            f"Expected GOOD/EXCELLENT for long implementation conversation, got {result.level} (score: {result.total_score})"
        assert result.total_score >= 6, f"Expected score >= 6, got {result.total_score}"


class TestCodeBlockRecognition:
    """Test that code blocks are properly recognized and scored."""
    
    def setup_method(self):
        self.analyzer = ConversationQualityAnalyzer()
    
    def test_python_code_block_adds_points(self):
        """Python code block should contribute to quality score."""
        user = "Show me a function"
        assistant = "```python\ndef example():\n    pass\n```"
        
        result = self.analyzer.analyze_conversation(user, assistant)
        
        assert result.elements.code_implementation, "Should detect code implementation"
        assert result.total_score >= 1, "Code block should add at least 1 point"
    
    def test_multiple_code_blocks_recognized(self):
        """Multiple code blocks in conversation should be recognized."""
        turns = [
            ("Part 1", "```python\ndef func1():\n    pass\n```"),
            ("Part 2", "```javascript\nfunction func2() {}\n```"),
            ("Part 3", "```typescript\nconst func3 = () => {};\n```")
        ]
        
        result = self.analyzer.analyze_multi_turn_conversation(turns)
        
        assert result.elements.code_implementation, "Should detect code in multi-turn"


class TestFileReferenceExtraction:
    """Test that file references are properly extracted and counted."""
    
    def setup_method(self):
        self.analyzer = ConversationQualityAnalyzer()
    
    def test_file_path_with_extension_extracted(self):
        """File paths in backticks should be extracted."""
        user = "Update `auth_service.py` and `user_model.py`"
        assistant = "I'll update those files."
        
        result = self.analyzer.analyze_conversation(user, assistant)
        
        assert result.elements.file_references >= 2, \
            f"Should extract 2 file references, got {result.elements.file_references}"
    
    def test_file_references_contribute_to_score(self):
        """File references should add points to quality score."""
        user = "Check `config.json`, `settings.py`, and `database.sql`"
        assistant = "Checking those files now."
        
        result = self.analyzer.analyze_conversation(user, assistant)
        
        # File references should add 1 point each (max 3)
        assert result.elements.file_references == 3, "Should cap at 3 file references"
        assert result.total_score >= 3, "3 files should add 3 points"


class TestDebuggingWorkflowRecognition:
    """Test that debugging workflows are recognized as valuable."""
    
    def setup_method(self):
        self.analyzer = ConversationQualityAnalyzer()
    
    def test_error_investigation_pattern(self):
        """Error → investigation → fix pattern should score higher."""
        turns = [
            (
                "Getting TypeError: unsupported operand type(s)",
                "This error usually means you're trying to perform an operation on incompatible types. Where is this occurring?"
            ),
            (
                "In calculate_total() function",
                "Let me check the types. Make sure all inputs are numeric:\n\n```python\ntotal = float(price) + float(tax)\n```"
            )
        ]
        
        result = self.analyzer.analyze_multi_turn_conversation(turns)
        
        # Should score FAIR or higher due to:
        # - Problem-solving workflow
        # - Code fix provided
        # - Multi-turn engagement
        assert result.level != "LOW", f"Debugging workflow should not be LOW, got {result.level}"
        assert result.total_score >= 2, f"Expected score >= 2 (code implementation), got {result.total_score}"


class TestImplementationProgressionRecognition:
    """Test that implementation progression is recognized as strategic."""
    
    def setup_method(self):
        self.analyzer = ConversationQualityAnalyzer()
    
    def test_feature_implementation_progression(self):
        """Feature → enhance → test → deploy progression should score well."""
        turns = [
            ("Implement login", "I'll add login functionality to `auth_controller.py`."),
            ("Add validation", "Adding email and password validation."),
            ("Write tests", "Created `test_auth.py` with login tests."),
            ("Deploy", "Deployed to production.")
        ]
        
        result = self.analyzer.analyze_multi_turn_conversation(turns)
        
        # Should be GOOD or FAIR due to:
        # - Multiple file references
        # - Implementation progression
        # - 4-turn development workflow
        assert result.level in ["GOOD", "FAIR"], \
            f"Implementation progression should be GOOD/FAIR, got {result.level}"


class TestNormalConversationVsCORTEXFormat:
    """Test that normal conversations score reasonably, not just CORTEX format."""
    
    def setup_method(self):
        self.analyzer = ConversationQualityAnalyzer()
    
    def test_normal_implementation_not_rated_low(self):
        """Normal implementation without CORTEX format should not be LOW."""
        user = "Add error handling to the API"
        assistant = """I'll add comprehensive error handling:

```python
try:
    result = api_call()
    return {"success": True, "data": result}
except ConnectionError:
    return {"success": False, "error": "Connection failed"}
except TimeoutError:
    return {"success": False, "error": "Request timed out"}
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return {"success": False, "error": "Internal server error"}
```

This handles connection issues, timeouts, and unexpected errors gracefully."""
        
        result = self.analyzer.analyze_conversation(user, assistant)
        
        # Should NOT be LOW - has code implementation
        assert result.level != "LOW", \
            f"Code implementation should not be LOW, got {result.level} (score: {result.total_score})"


class TestCodeReviewConversations:
    """Test that code review conversations are properly scored."""
    
    def setup_method(self):
        self.analyzer = ConversationQualityAnalyzer()
    
    def test_code_review_with_suggestions(self):
        """Code review with suggestions should score FAIR or higher."""
        turns = [
            (
                "Review this code:\n```python\ndef process(data):\n    return data.upper()\n```",
                "The code works but could be improved. Consider adding type hints and error handling:\n\n```python\ndef process(data: str) -> str:\n    if not isinstance(data, str):\n        raise TypeError('data must be a string')\n    return data.upper()\n```"
            ),
            (
                "Good point, I'll add that",
                "Great! Also consider adding a docstring to document the function's purpose and parameters."
            )
        ]
        
        result = self.analyzer.analyze_multi_turn_conversation(turns)
        
        # Should be FAIR or higher due to:
        # - Code blocks (original and improved)
        # - Multi-turn review workflow
        # - Improvement suggestions
        assert result.level in ["GOOD", "FAIR"], \
            f"Code review should be GOOD/FAIR, got {result.level} (score: {result.total_score})"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
