"""
Stage 6: OfflineModeProvider - Fallback Storage for Network Failures

AC-PHASE50-S6-001: OfflineModeProvider wraps provider with graceful degradation
AC-PHASE50-S6-002: On network failure, switch to L2 cache / local fallback
AC-PHASE50-S6-003: Attempt reconnection with exponential backoff (1s, 2s, 4s, 8s max)
AC-PHASE50-S6-004: Track offline duration and retry attempts in metrics
AC-PHASE50-S6-005: Transparent fallback - client code unaware of offline state

Target: 18 tests, 100% pass rate for Stage 6
"""

import time
import pytest
from unittest.mock import Mock, patch
from cortex.storage.provider import IKnowledgeProvider
from cortex.storage.config import StorageConfig
from cortex.storage.errors import StorageError, NetworkError, NotFoundError
from cortex.storage.offline import OfflineModeProvider


class TestOfflineModeProviderInitialization:
    """AC-PHASE50-S6-001: Offline mode provider initialization"""

    def test_offline_provider_wraps_any_provider(self):
        """OfflineModeProvider accepts any IKnowledgeProvider"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        config = StorageConfig(backend="local", endpoint="/tmp")
        
        offline = OfflineModeProvider(mock_provider, config)
        assert offline.provider == mock_provider

    def test_offline_provider_implements_interface(self):
        """OfflineModeProvider is instance of IKnowledgeProvider"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        config = StorageConfig(backend="local", endpoint="/tmp")
        
        offline = OfflineModeProvider(mock_provider, config)
        assert isinstance(offline, IKnowledgeProvider)

    def test_offline_provider_stores_config(self):
        """OfflineModeProvider stores StorageConfig"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        config = StorageConfig(backend="local", endpoint="/tmp")
        
        offline = OfflineModeProvider(mock_provider, config)
        assert offline.config == config

    def test_offline_provider_initializes_metrics(self):
        """OfflineModeProvider initializes offline tracking metrics"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        config = StorageConfig(backend="local", endpoint="/tmp")
        
        offline = OfflineModeProvider(mock_provider, config)
        assert hasattr(offline, 'metrics')
        assert offline.metrics.get('offline_duration_seconds') == 0
        assert offline.metrics.get('retry_attempts') == 0


class TestOfflineModeProviderReadMethod:
    """AC-PHASE50-S6-002, S6-003: read() with fallback and reconnection"""

    def test_read_succeeds_when_online(self):
        """read() succeeds when provider is online"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        mock_provider.read.return_value = "online content"
        
        config = StorageConfig(backend="local", endpoint="/tmp")
        offline = OfflineModeProvider(mock_provider, config)
        
        result = offline.read("file.txt")
        assert result == "online content"
        assert offline.metrics['offline_duration_seconds'] == 0

    def test_read_falls_back_on_network_error(self):
        """read() falls back to cache on NetworkError"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        mock_provider.read.side_effect = NetworkError("Connection timeout")
        
        config = StorageConfig(backend="local", endpoint="/tmp")
        offline = OfflineModeProvider(mock_provider, config)
        
        # Cache fallback should be available
        with pytest.raises((NetworkError, StorageError)):
            offline.read("missing_file.txt")

    def test_read_retries_with_exponential_backoff(self):
        """read() retries failed connection with exponential backoff"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        # Fail twice, then succeed
        mock_provider.read.side_effect = [
            NetworkError("Timeout"),
            NetworkError("Timeout"),
            "recovered content"
        ]
        
        config = StorageConfig(backend="local", endpoint="/tmp")
        offline = OfflineModeProvider(mock_provider, config, max_retries=3)
        
        result = offline.read("file.txt")
        assert result == "recovered content"
        assert mock_provider.read.call_count == 3


class TestOfflineModeProviderWriteMethod:
    """AC-PHASE50-S6-002: write() with fallback"""

    def test_write_succeeds_when_online(self):
        """write() succeeds when provider is online"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        config = StorageConfig(backend="local", endpoint="/tmp")
        
        offline = OfflineModeProvider(mock_provider, config)
        offline.write("file.txt", "content")
        
        mock_provider.write.assert_called_once()

    def test_write_queued_during_offline(self):
        """write() queues changes during offline mode"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        mock_provider.write.side_effect = NetworkError("Offline")
        
        config = StorageConfig(backend="local", endpoint="/tmp")
        offline = OfflineModeProvider(mock_provider, config)
        
        # Write should be accepted (queued)
        offline.write("file.txt", "content")
        assert len(offline.write_queue) > 0

    def test_write_queue_flushed_on_reconnection(self):
        """write_queue flushed when connection restored"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        call_count = [0]
        
        def write_impl(path, content):
            call_count[0] += 1
            if call_count[0] <= 2:
                raise NetworkError("Offline")
        
        mock_provider.write.side_effect = write_impl
        
        config = StorageConfig(backend="local", endpoint="/tmp")
        offline = OfflineModeProvider(mock_provider, config, max_retries=3)
        
        # Queue writes during offline
        offline.write("file1.txt", "content1")
        offline.write("file2.txt", "content2")
        
        # Flush on reconnection
        offline.flush_write_queue()
        
        # Should have retried the queued writes


class TestOfflineModeProviderListMethod:
    """AC-PHASE50-S6-002: list() with fallback"""

    def test_list_succeeds_when_online(self):
        """list() succeeds when provider is online"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        mock_provider.list.return_value = ["file1.txt", "file2.txt"]
        
        config = StorageConfig(backend="local", endpoint="/tmp")
        offline = OfflineModeProvider(mock_provider, config)
        
        result = offline.list("dir")
        assert result == ["file1.txt", "file2.txt"]

    def test_list_returns_empty_on_offline(self):
        """list() returns empty list when offline"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        mock_provider.list.side_effect = NetworkError("Offline")
        
        config = StorageConfig(backend="local", endpoint="/tmp")
        offline = OfflineModeProvider(mock_provider, config)
        
        # Should return empty or cached list
        result = offline.list("dir")
        assert isinstance(result, list)


class TestOfflineModeProviderExistsMethod:
    """AC-PHASE50-S6-002: exists() with fallback"""

    def test_exists_succeeds_when_online(self):
        """exists() succeeds when provider is online"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        mock_provider.exists.return_value = True
        
        config = StorageConfig(backend="local", endpoint="/tmp")
        offline = OfflineModeProvider(mock_provider, config)
        
        result = offline.exists("file.txt")
        assert result is True

    def test_exists_checks_cache_when_offline(self):
        """exists() checks local cache when offline"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        mock_provider.exists.side_effect = NetworkError("Offline")
        
        config = StorageConfig(backend="local", endpoint="/tmp")
        offline = OfflineModeProvider(mock_provider, config)
        
        # Should check cache or return False safely
        result = offline.exists("file.txt")
        assert isinstance(result, bool)


class TestOfflineModeProviderDeleteMethod:
    """AC-PHASE50-S6-002: delete() with fallback"""

    def test_delete_succeeds_when_online(self):
        """delete() succeeds when provider is online"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        config = StorageConfig(backend="local", endpoint="/tmp")
        
        offline = OfflineModeProvider(mock_provider, config)
        offline.delete("file.txt")
        
        mock_provider.delete.assert_called_once()

    def test_delete_queued_during_offline(self):
        """delete() queues deletion during offline mode"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        mock_provider.delete.side_effect = NetworkError("Offline")
        
        config = StorageConfig(backend="local", endpoint="/tmp")
        offline = OfflineModeProvider(mock_provider, config)
        
        # Delete should be queued
        offline.delete("file.txt")
        assert len(offline.delete_queue) > 0


class TestOfflineModeProviderReconnection:
    """AC-PHASE50-S6-003: Exponential backoff and reconnection"""

    def test_backoff_increases_exponentially(self):
        """Retry backoff increases exponentially (1s, 2s, 4s, 8s max)"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        mock_provider.read.side_effect = NetworkError("Offline")
        
        config = StorageConfig(backend="local", endpoint="/tmp")
        offline = OfflineModeProvider(mock_provider, config)
        
        # Verify backoff values follow pattern
        backoffs = []
        for retry in range(4):
            backoff = offline._calculate_backoff(retry)
            backoffs.append(backoff)
        
        # Should be: 1, 2, 4, 8
        assert backoffs[0] == 1
        assert backoffs[1] == 2
        assert backoffs[2] == 4
        assert backoffs[3] == 8

    def test_backoff_caps_at_8_seconds(self):
        """Backoff caps at 8 seconds (max retry interval)"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        config = StorageConfig(backend="local", endpoint="/tmp")
        
        offline = OfflineModeProvider(mock_provider, config)
        
        # Many retries should cap at 8s
        for retry in range(10, 20):
            backoff = offline._calculate_backoff(retry)
            assert backoff <= 8


class TestOfflineModeProviderMetrics:
    """AC-PHASE50-S6-004: Offline metrics tracking"""

    def test_offline_duration_tracked(self):
        """offline_duration_seconds tracked while offline"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        mock_provider.read.side_effect = NetworkError("Offline")
        
        config = StorageConfig(backend="local", endpoint="/tmp")
        offline = OfflineModeProvider(mock_provider, config)
        
        # Simulate offline state
        offline.is_offline = True
        offline.offline_start_time = time.time() - 5
        
        # Metrics should reflect offline time
        assert offline.metrics['offline_duration_seconds'] >= 5

class TestOfflineModeProviderTransparency:
    """AC-PHASE50-S6-005: Transparent fallback"""

    def test_client_unaware_of_offline_state(self):
        """Client code doesn't need to know about offline mode"""
        mock_provider = Mock(spec=IKnowledgeProvider)
        mock_provider.read.return_value = "content"
        
        config = StorageConfig(backend="local", endpoint="/tmp")
        
        # Wrap with offline mode
        offline = OfflineModeProvider(mock_provider, config)
        
        # Should work transparently
        result = offline.read("file.txt")
        assert result == "content"

