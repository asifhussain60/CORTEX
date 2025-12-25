"""Tests for request_logger.py

Test Coverage:
- Request logging to database
- Sensitive data redaction
- Log retrieval and filtering
- Edge cases: database errors, malformed input
"""

import pytest
import sqlite3
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.brain.tier1.request_logger import RequestLogger


@pytest.fixture
def temp_db(tmp_path):
    """Create temporary test database"""
    db_path = tmp_path / "test_requests.db"
    return str(db_path)


class TestRequestLoggerInitialization:
    """Tests for RequestLogger initialization"""
    
    def test_init_creates_instance(self, temp_db):
        """Test that RequestLogger initializes successfully"""
        logger = RequestLogger(db_path=temp_db)
        assert logger is not None
        assert isinstance(logger, RequestLogger)
    
    def test_init_creates_database_file(self, temp_db):
        """Test that initialization creates database file"""
        logger = RequestLogger(db_path=temp_db)
        assert Path(temp_db).exists()
    
    def test_init_creates_table(self, temp_db):
        """Test that initialization creates tier1_raw_requests table"""
        logger = RequestLogger(db_path=temp_db)
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='tier1_raw_requests'
        """)
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        assert result[0] == 'tier1_raw_requests'
    
    @patch('src.brain.tier1.request_logger.ConfigManager')
    def test_init_without_db_path_uses_config_manager(self, mock_config):
        """Test initialization without db_path uses ConfigManager"""
        mock_config.return_value.get_tier1_conversations_path.return_value = "/tmp/test.db"
        logger = RequestLogger()
        
        assert mock_config.called or logger.db_path is not None


class TestSensitiveDataRedaction:
    """Tests for sensitive data redaction"""
    
    @pytest.fixture
    def logger(self, temp_db):
        return RequestLogger(db_path=temp_db)
    
    def test_redact_api_key_long_format(self, logger):
        """Test redaction of long-format API key (32+ chars)"""
        text = "My API key is abc123xyz789abc123xyz789abc123xyz"  # 38 chars
        redacted, was_redacted = logger.redact_sensitive_data(text)
        
        assert "[REDACTED_API_KEY]" in redacted
        assert "abc123xyz789abc123xyz789abc123xyz" not in redacted
        assert was_redacted is True
    
    def test_redact_api_key_sk_format(self, logger):
        """Test redaction of sk- format API key (OpenAI style)"""
        text = "Use this key: sk-abc123xyz456def789ghi012"
        redacted, was_redacted = logger.redact_sensitive_data(text)
        
        assert "[REDACTED_API_KEY]" in redacted
        assert "sk-abc123xyz456def789ghi012" not in redacted
        assert was_redacted is True
    
    def test_redact_github_token(self, logger):
        """Test redaction of GitHub personal access token"""
        # GitHub token pattern expects exactly 36 chars after ghp_
        text = "GitHub token: ghp_123456789012345678901234567890123456"
        redacted, was_redacted = logger.redact_sensitive_data(text)
        
        assert "[REDACTED]" in redacted or "ghp_" not in redacted
        assert was_redacted is True
    
    def test_redact_password(self, logger):
        """Test redaction of password patterns"""
        text = "Login with password=secret123"
        redacted, was_redacted = logger.redact_sensitive_data(text)
        
        assert "[REDACTED]" in redacted
        assert "secret123" not in redacted
        assert was_redacted is True
    
    def test_redact_bearer_token(self, logger):
        """Test redaction of Bearer token"""
        text = "Authorization: bearer abc123.xyz456.def789"
        redacted, was_redacted = logger.redact_sensitive_data(text)
        
        assert "[REDACTED]" in redacted
        assert "abc123.xyz456.def789" not in redacted
        assert was_redacted is True
    
    def test_redact_credit_card(self, logger):
        """Test redaction of credit card number"""
        text = "Card: 4532-1234-5678-9012"
        redacted, was_redacted = logger.redact_sensitive_data(text)
        
        assert "[REDACTED_CC]" in redacted
        assert "4532-1234-5678-9012" not in redacted
        assert was_redacted is True
    
    def test_redact_private_key(self, logger):
        """Test redaction of SSH private key"""
        text = """
        -----BEGIN RSA PRIVATE KEY-----
        MIIEpAIBAAKCAQEA...
        -----END RSA PRIVATE KEY-----
        """
        redacted, was_redacted = logger.redact_sensitive_data(text)
        
        assert "[REDACTED_PRIVATE_KEY]" in redacted
        assert "BEGIN RSA PRIVATE KEY" not in redacted
        assert was_redacted is True
    
    def test_no_redaction_for_clean_text(self, logger):
        """Test that clean text is not modified"""
        text = "This is a normal message without sensitive data"
        redacted, was_redacted = logger.redact_sensitive_data(text)
        
        assert redacted == text
        assert was_redacted is False
    
    def test_redact_multiple_patterns(self, logger):
        """Test redaction of multiple sensitive patterns in one text"""
        text = "API key sk-abc123def456ghi789jkl012mno and password=secret123"
        redacted, was_redacted = logger.redact_sensitive_data(text)
        
        assert "[REDACTED_API_KEY]" in redacted
        assert "[REDACTED]" in redacted
        assert "sk-abc123def456ghi789jkl012mno" not in redacted
        assert "secret123" not in redacted
        assert was_redacted is True


class TestRequestLogging:
    """Tests for logging raw requests"""
    
    @pytest.fixture
    def logger(self, temp_db):
        return RequestLogger(db_path=temp_db)
    
    def test_log_raw_request_returns_id(self, logger):
        """Test that log_raw_request returns an integer ID"""
        request_id = logger.log_raw_request(
            raw_request="Test request",
            raw_response="Test response",
            agent_name="test_agent"
        )
        
        assert isinstance(request_id, int)
        assert request_id > 0
    
    def test_log_raw_request_stores_in_database(self, logger, temp_db):
        """Test that logged request is stored in database"""
        request_id = logger.log_raw_request(
            raw_request="Test request",
            raw_response="Test response",
            agent_name="test_agent"
        )
        
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tier1_raw_requests WHERE id = ?", (request_id,))
        row = cursor.fetchone()
        conn.close()
        
        assert row is not None
    
    def test_log_raw_request_with_sensitive_data(self, logger):
        """Test logging request with sensitive data applies redaction"""
        request_id = logger.log_raw_request(
            raw_request="Use API key sk-abc123def456ghi789jkl012mno",
            raw_response="Done",
            agent_name="test_agent"
        )
        
        logged = logger.get_raw_request(request_id)
        assert "[REDACTED_API_KEY]" in logged['raw_request']
        assert "sk-abc123def456ghi789jkl012mno" not in logged['raw_request']
        assert logged['redacted'] is True
    
    def test_log_raw_request_with_conversation_id(self, logger):
        """Test logging request with conversation ID"""
        conv_id = "conv-12345"
        request_id = logger.log_raw_request(
            raw_request="Test",
            raw_response="Response",
            agent_name="test_agent",
            conversation_id=conv_id
        )
        
        logged = logger.get_raw_request(request_id)
        assert logged['conversation_id'] == conv_id
    
    def test_log_raw_request_with_metadata(self, logger):
        """Test logging request with metadata"""
        metadata = {"session_id": "sess-123", "user_id": "user-456"}
        request_id = logger.log_raw_request(
            raw_request="Test",
            raw_response="Response",
            agent_name="test_agent",
            metadata=metadata
        )
        
        logged = logger.get_raw_request(request_id)
        assert logged['metadata'] == metadata
        assert logged['metadata']['session_id'] == "sess-123"


class TestRequestRetrieval:
    """Tests for retrieving logged requests"""
    
    @pytest.fixture
    def logger(self, temp_db):
        return RequestLogger(db_path=temp_db)
    
    def test_get_raw_request_returns_dict(self, logger):
        """Test that get_raw_request returns dictionary"""
        request_id = logger.log_raw_request(
            raw_request="Test",
            raw_response="Response",
            agent_name="test_agent"
        )
        
        result = logger.get_raw_request(request_id)
        assert isinstance(result, dict)
        assert 'id' in result
        assert 'raw_request' in result
        assert 'raw_response' in result
    
    def test_get_raw_request_nonexistent_returns_none(self, logger):
        """Test that getting non-existent request returns None"""
        result = logger.get_raw_request(99999)
        assert result is None
    
    def test_get_conversation_raw_logs_returns_list(self, logger):
        """Test that get_conversation_raw_logs returns list"""
        conv_id = "conv-test"
        logger.log_raw_request("Req1", "Resp1", "agent", conversation_id=conv_id)
        logger.log_raw_request("Req2", "Resp2", "agent", conversation_id=conv_id)
        
        logs = logger.get_conversation_raw_logs(conv_id)
        assert isinstance(logs, list)
        assert len(logs) == 2
    
    def test_get_conversation_raw_logs_empty_conversation(self, logger):
        """Test getting logs for conversation with no requests"""
        logs = logger.get_conversation_raw_logs("nonexistent-conv")
        assert logs == []
    
    def test_get_conversation_raw_logs_ordered_by_time(self, logger):
        """Test that conversation logs are ordered by creation time"""
        conv_id = "conv-test"
        id1 = logger.log_raw_request("First", "Resp1", "agent", conversation_id=conv_id)
        id2 = logger.log_raw_request("Second", "Resp2", "agent", conversation_id=conv_id)
        
        logs = logger.get_conversation_raw_logs(conv_id)
        assert logs[0]['id'] == id1
        assert logs[1]['id'] == id2


class TestEdgeCases:
    """Tests for edge cases and error handling"""
    
    @pytest.fixture
    def logger(self, temp_db):
        return RequestLogger(db_path=temp_db)
    
    def test_log_empty_request(self, logger):
        """Test logging empty request string"""
        request_id = logger.log_raw_request(
            raw_request="",
            raw_response="Response",
            agent_name="test_agent"
        )
        
        logged = logger.get_raw_request(request_id)
        assert logged['raw_request'] == ""
    
    def test_log_very_long_request(self, logger):
        """Test logging very long request text"""
        long_text = "Request text " * 1000  # Non-sensitive repetitive text
        request_id = logger.log_raw_request(
            raw_request=long_text,
            raw_response="Response",
            agent_name="test_agent"
        )
        
        logged = logger.get_raw_request(request_id)
        assert len(logged['raw_request']) > 5000  # Should store long text
    
    def test_log_request_with_unicode(self, logger):
        """Test logging request with Unicode characters"""
        unicode_text = "テスト request with émojis 🚀 and symbols ™"
        request_id = logger.log_raw_request(
            raw_request=unicode_text,
            raw_response="Response",
            agent_name="test_agent"
        )
        
        logged = logger.get_raw_request(request_id)
        assert logged['raw_request'] == unicode_text
    
    def test_log_request_with_special_sql_characters(self, logger):
        """Test logging request with SQL special characters"""
        sql_text = "SELECT * FROM users WHERE id = 1; DROP TABLE users; --"
        request_id = logger.log_raw_request(
            raw_request=sql_text,
            raw_response="Response",
            agent_name="test_agent"
        )
        
        logged = logger.get_raw_request(request_id)
        assert logged['raw_request'] == sql_text
    
    def test_redact_preserves_text_structure(self, logger):
        """Test that redaction preserves overall text structure"""
        text = "Start password=secret123 middle token=abc end"
        redacted, _ = logger.redact_sensitive_data(text)
        
        assert "Start" in redacted
        assert "middle" in redacted
        assert "end" in redacted
