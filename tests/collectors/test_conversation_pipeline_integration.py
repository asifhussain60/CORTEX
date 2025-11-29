"""
CORTEX 3.0 - Conversation Pipeline Integration Test
==================================================

Test the conversation pipeline collector to ensure proper integration.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Feature: Task 4 - Conversation Pipeline Integration
Test Target: ConversationCollector functionality
"""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime
import sqlite3

from src.collectors.conversation_collector import (
    ConversationCollector,
    ConversationQuality,
    ConversationMetadata,
    ProcessedConversation
)


class TestConversationPipelineIntegration:
    """Test conversation pipeline collector integration"""
    
    def setup_method(self):
        """Setup test environment"""
        # Create temporary brain directory
        self.temp_brain = tempfile.mkdtemp()
        self.brain_path = Path(self.temp_brain)
        
        # Create necessary subdirectories
        (self.brain_path / "conversation-captures").mkdir()
        (self.brain_path / "conversation-vault").mkdir()
        
        # Initialize collector
        self.collector = ConversationCollector(str(self.brain_path))
    
    def create_test_conversation_file(self, content: str, filename: str = None) -> Path:
        """Create a test conversation file"""
        if filename is None:
            filename = f"2025-11-16-test-conversation.md"
        
        file_path = self.brain_path / "conversation-captures" / filename
        file_path.write_text(content, encoding='utf-8')
        return file_path
    
    def test_conversation_collector_initialization(self):
        """Test collector initializes properly"""
        assert self.collector.collector_id == "conversation_pipeline"
        assert self.collector.name == "Conversation Pipeline Collector"
        assert self.collector.brain_path == self.brain_path
    
    def test_conversation_collector_start(self):
        """Test collector starts and creates necessary structures"""
        success = self.collector.start()
        
        assert success == True
        assert (self.brain_path / "conversation-captures").exists()
        assert (self.brain_path / "conversation-vault").exists()
        assert (self.brain_path / "tier1-working-memory.db").exists()
        
        # Verify database schema
        conn = sqlite3.connect(self.brain_path / "tier1-working-memory.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        assert "conversations" in tables
        
        conn.close()
    
    def test_process_simple_conversation(self):
        """Test processing a simple conversation"""
        conversation_content = """# Test Authentication Discussion

User: How do I implement user authentication?

CORTEX: I'll help you implement authentication with these steps:

1. Create user model with password hashing
2. Implement login/logout endpoints 
3. Add session management
4. Create authentication middleware

User: What about JWT tokens?

CORTEX: JWT tokens are excellent for stateless authentication. Here's the implementation:

```python
import jwt
from datetime import datetime, timedelta

def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, 'secret_key', algorithm='HS256')
```

User: Perfect, let's implement this approach.

CORTEX: I'll create the complete authentication system with JWT tokens, including error handling and security best practices.
"""
        
        # Create test file
        test_file = self.create_test_conversation_file(conversation_content)
        
        # Start collector
        self.collector.start()
        
        # Process the conversation
        metrics = self.collector.collect()
        
        # Verify metrics were generated
        assert len(metrics) > 0
        
        # Check that conversation was processed
        conversation_metrics = [m for m in metrics if m.name == "conversations_processed"]
        assert len(conversation_metrics) == 1
        assert conversation_metrics[0].value == 1
        
        # Verify file was archived (should be moved from captures to vault)
        assert not test_file.exists()  # Original should be gone
        
        # Check vault has the archived file
        vault_files = list((self.brain_path / "conversation-vault").rglob("*.md"))
        assert len(vault_files) == 1
        
        # Verify database storage
        conn = sqlite3.connect(self.brain_path / "tier1-working-memory.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM conversations")
        count = cursor.fetchone()[0]
        assert count == 1
        
        # Get the stored conversation
        cursor.execute("SELECT * FROM conversations")
        row = cursor.fetchone()
        assert row is not None
        
        conn.close()
    
    def test_quality_score_calculation(self):
        """Test quality score calculation for different conversation types"""
        
        # High-quality technical conversation
        high_quality_content = """# Complex Feature Implementation

User: I need to implement a distributed caching system with Redis clustering and automatic failover.

CORTEX: I'll design a comprehensive distributed caching solution:

## Phase 1: Architecture Design
- Redis Sentinel for high availability
- Consistent hashing for data distribution  
- Connection pooling for performance
- Monitoring and alerting integration

## Phase 2: Implementation

```python
import redis
from redis.sentinel import Sentinel
import hashring
import logging

class DistributedCache:
    def __init__(self, sentinels, service_name):
        self.sentinel = Sentinel(sentinels)
        self.master = self.sentinel.master_for(service_name)
        self.slaves = self.sentinel.slave_for(service_name)
        self.ring = hashring.HashRing(self._get_nodes())
    
    def get(self, key):
        node = self.ring.get_node(key)
        return self.slaves.get(f"{node}:{key}")
    
    def set(self, key, value, ttl=3600):
        node = self.ring.get_node(key)
        return self.master.setex(f"{node}:{key}", ttl, value)
```

## Phase 3: Testing Strategy

```python
def test_failover_scenario():
    # Test automatic failover
    cache = DistributedCache(sentinels, 'mymaster')
    
    # Simulate master failure
    with pytest.raises(redis.ConnectionError):
        original_master.shutdown()
    
    # Verify failover worked
    assert cache.set('test_key', 'test_value')
    assert cache.get('test_key') == 'test_value'
```

User: Excellent! How do we handle cache warming and invalidation patterns?

CORTEX: For cache warming and invalidation, I'll implement:

1. **Proactive Cache Warming:**
   - Background jobs to pre-populate frequently accessed data
   - Predictive caching based on usage patterns
   - Gradual warming to avoid thundering herd

2. **Smart Invalidation:**
   - Tag-based invalidation for related data
   - Time-based expiration with jitter
   - Event-driven invalidation via pub/sub

```python
class CacheManager:
    def __init__(self, distributed_cache):
        self.cache = distributed_cache
        self.pubsub = self.cache.master.pubsub()
        
    def warm_cache(self, data_loader, keys):
        # Implement gradual warming
        for key in keys:
            if not self.cache.get(key):
                value = data_loader(key)
                self.cache.set(key, value)
                time.sleep(0.01)  # Prevent overload
    
    def invalidate_by_tag(self, tag):
        # Tag-based invalidation
        pattern = f"tag:{tag}:*"
        keys = self.cache.master.keys(pattern)
        if keys:
            self.cache.master.delete(*keys)
            self.cache.master.publish('cache_invalidated', tag)
```

User: This is exactly what I needed. Let's implement the monitoring and alerting integration too.

CORTEX: I'll add comprehensive monitoring:

```python
import prometheus_client
from datadog import DogStatsdClient

class CacheMetrics:
    def __init__(self):
        self.hit_counter = prometheus_client.Counter(
            'cache_hits_total', 'Total cache hits'
        )
        self.miss_counter = prometheus_client.Counter(
            'cache_misses_total', 'Total cache misses' 
        )
        self.dogstatsd = DogStatsdClient()
    
    def record_hit(self, key):
        self.hit_counter.inc()
        self.dogstatsd.increment('cache.hit', tags=[f'key:{key}'])
    
    def record_miss(self, key):
        self.miss_counter.inc() 
        self.dogstatsd.increment('cache.miss', tags=[f'key:{key}'])
```
"""
        
        test_file = self.create_test_conversation_file(high_quality_content, "high-quality-test.md")
        self.collector.start()
        
        # Process conversation
        processed = self.collector._process_conversation_file(test_file)
        
        assert processed is not None
        assert processed.quality_score >= 7.0  # Should be high quality
        assert processed.quality_level in [ConversationQuality.GOOD, ConversationQuality.EXCELLENT]
        assert processed.strategic_value == True
        assert processed.metadata.code_snippets >= 3
        assert 'python' in processed.metadata.technologies
        assert 'implementation' in processed.metadata.intents
    
    def test_low_quality_conversation(self):
        """Test quality score for simple Q&A"""
        
        low_quality_content = """# Simple Question

User: What is Python?

CORTEX: Python is a programming language.

User: Thanks.

CORTEX: You're welcome.
"""
        
        test_file = self.create_test_conversation_file(low_quality_content, "low-quality-test.md")
        self.collector.start()
        
        processed = self.collector._process_conversation_file(test_file)
        
        assert processed is not None
        assert processed.quality_score < 5.0  # Should be low quality
        assert processed.quality_level in [ConversationQuality.POOR, ConversationQuality.MINIMAL]
        assert processed.strategic_value == False
        assert processed.metadata.code_snippets == 0
    
    def test_metadata_extraction(self):
        """Test metadata extraction from conversation content"""
        
        content = """# Full Stack Development Discussion

User: I'm building a React frontend with a Python Django backend and PostgreSQL database.

CORTEX: Excellent tech stack! Let me help you set up the integration:

```javascript
// React API client
const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json'
  }
});
```

```python
# Django models.py
from django.db import models

class User(models.Model):
    username = models.CharField(max_length=150)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
```

```sql
-- PostgreSQL schema
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

User: How do I handle authentication between React and Django?

CORTEX: I'll implement JWT authentication with Django REST Framework and React:

Files to create:
- authentication/views.py
- frontend/src/auth/AuthService.js  
- config/settings.py
"""
        
        test_file = self.create_test_conversation_file(content, "metadata-test.md")
        self.collector.start()
        
        processed = self.collector._process_conversation_file(test_file)
        
        assert processed is not None
        
        # Check technology detection
        expected_technologies = {'javascript', 'python', 'sql', 'web'}
        assert expected_technologies.issubset(processed.metadata.technologies)
        
        # Check file mentions
        assert len(processed.metadata.files_mentioned) >= 3
        assert any('views.py' in f for f in processed.metadata.files_mentioned)
        assert any('AuthService.js' in f for f in processed.metadata.files_mentioned)
        
        # Check intents
        assert 'implementation' in processed.metadata.intents
        
        # Check code snippets
        assert processed.metadata.code_snippets >= 3
    
    def test_conversation_archival_process(self):
        """Test complete conversation archival process"""
        
        content = """# Test Archival

User: This is a test conversation for archival.

CORTEX: I understand. This conversation will be processed and archived.
"""
        
        test_file = self.create_test_conversation_file(content, "2025-11-16-archival-test.md")
        self.collector.start()
        
        # Process
        metrics = self.collector.collect()
        
        # Verify original file is gone
        assert not test_file.exists()
        
        # Find archived file
        archived_files = list((self.brain_path / "conversation-vault").rglob("*.md"))
        assert len(archived_files) == 1
        
        archived_file = archived_files[0]
        archived_content = archived_file.read_text()
        
        # Verify metadata header was added
        assert "---" in archived_content
        assert "conversation_id:" in archived_content
        assert "quality_score:" in archived_content
        assert "strategic_value:" in archived_content
        
        # Verify original content is preserved
        assert "Test Archival" in archived_content
        assert "test conversation for archival" in archived_content
    
    def test_integration_with_collector_manager(self):
        """Test integration with the collector manager"""
        from src.collectors.manager import CollectorManager
        
        # Initialize manager with our brain path
        manager = CollectorManager(
            brain_path=str(self.brain_path),
            auto_start=False
        )
        
        manager.initialize()
        
        # Check conversation collector is registered
        assert "conversation_pipeline" in manager.collectors
        
        # Start all collectors
        results = manager.start_all_collectors()
        assert results.get("conversation_pipeline") == True
        
        # Create a test conversation
        content = """# Manager Integration Test

User: Testing manager integration.

CORTEX: This test verifies the collector works with the manager.
"""
        
        self.create_test_conversation_file(content, "manager-test.md")
        
        # Collect metrics through manager
        all_metrics = manager.collect_all_metrics()
        
        # Verify conversation metrics are included
        conversation_metrics = all_metrics.get("conversation_pipeline", [])
        assert len(conversation_metrics) > 0
        
        # Check health status
        health_status = manager.get_collector_health()
        conversation_health = health_status.get("conversation_pipeline")
        assert conversation_health is not None
        assert conversation_health.status.value == "active"


# Integration test configuration
@pytest.fixture(scope="module")
def conversation_pipeline_integration():
    """Module-level fixture for conversation pipeline integration tests"""
    return {
        "test_description": "Conversation Pipeline Integration",
        "components_tested": [
            "ConversationCollector", 
            "CollectorManager integration",
            "Tier 1 database storage",
            "Conversation archival process",
            "Quality scoring system",
            "Metadata extraction"
        ],
        "success_criteria": [
            "Conversations are successfully captured and processed",
            "Quality scores are calculated accurately", 
            "Metadata extraction works correctly",
            "Files are properly archived with metadata",
            "Database storage functions properly",
            "Manager integration works seamlessly"
        ]
    }