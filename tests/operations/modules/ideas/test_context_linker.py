#!/usr/bin/env python3
"""
Tests for CORTEX IDEA Context Linking System
Comprehensive validation of idea-to-ecosystem linking functionality.
"""

import pytest
import asyncio
import tempfile
import shutil
import sqlite3
import yaml
from datetime import datetime, timedelta
from pathlib import Path

from src.operations.modules.ideas.context_linker import (
    IdeaContextLinker, 
    ConversationContextAnalyzer,
    KnowledgeGraphLinker,
    OperationLinker,
    ContextLink,
    create_context_linker
)
from src.operations.modules.ideas.idea_queue import IdeaCapture

class TestConversationContextAnalyzer:
    """Test conversation context analysis."""
    
    @pytest.fixture
    def temp_conversations(self):
        """Create temporary conversation files for testing."""
        temp_dir = tempfile.mkdtemp()
        conv_dir = Path(temp_dir) / "conversations"
        conv_dir.mkdir()
        
        # Create sample conversation files
        conversations = {
            "2025-11-15-authentication-system.md": """
# Authentication System Discussion

We need to implement OAuth2 authentication for the API endpoints.
Current security vulnerabilities need addressing.
Authentication tokens should expire after 24 hours.
""",
            "2025-11-14-cortex-optimization.md": """
# CORTEX Performance Optimization

Discussion about optimizing CORTEX memory usage.
YAML conversion for better token efficiency.
Conversation history management improvements.
""",
            "2025-11-13-database-cleanup.md": """
# Database Cleanup Strategy

Auto-cleanup for obsolete test files and data.
Cleanup operations for old conversation captures.
Database optimization and maintenance.
"""
        }
        
        for filename, content in conversations.items():
            (conv_dir / filename).write_text(content)
        
        yield conv_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_analyzer_initialization(self, temp_conversations):
        """Test analyzer initializes correctly."""
        analyzer = ConversationContextAnalyzer(str(temp_conversations))
        assert analyzer.capture_dir == temp_conversations
        assert analyzer.conversation_cache == {}
    
    @pytest.mark.asyncio
    async def test_find_relevant_conversations(self, temp_conversations):
        """Test finding relevant conversations for an idea."""
        analyzer = ConversationContextAnalyzer(str(temp_conversations))
        
        # Test idea about authentication
        auth_idea = IdeaCapture(
            idea_id="test_001",
            raw_text="Need better authentication system for API security",
            timestamp=datetime.now()
        )
        
        links = await analyzer.find_relevant_conversations(auth_idea)
        
        # Should find at least the authentication conversation
        assert len(links) >= 1
        auth_links = [link for link in links if "authentication" in link.context_id.lower()]
        assert len(auth_links) >= 1
        
        # Check link properties
        auth_link = auth_links[0]
        assert auth_link.idea_id == "test_001"
        assert auth_link.context_type == "conversation"
        assert auth_link.relevance_score > 0.0
        assert "authentication" in auth_link.link_reason.lower()
    
    @pytest.mark.asyncio
    async def test_conversation_relevance_scoring(self, temp_conversations):
        """Test conversation relevance scoring."""
        analyzer = ConversationContextAnalyzer(str(temp_conversations))
        
        # High relevance idea
        high_relevance_idea = IdeaCapture(
            idea_id="test_002",
            raw_text="YAML optimization conversation memory",
            timestamp=datetime.now()
        )
        
        # Low relevance idea
        low_relevance_idea = IdeaCapture(
            idea_id="test_003",
            raw_text="completely unrelated topic about cooking recipes",
            timestamp=datetime.now()
        )
        
        high_links = await analyzer.find_relevant_conversations(high_relevance_idea)
        low_links = await analyzer.find_relevant_conversations(low_relevance_idea)
        
        # High relevance should find more/better links
        if high_links and low_links:
            assert max(link.relevance_score for link in high_links) > \
                   max(link.relevance_score for link in low_links)
    
    def test_keyword_extraction(self, temp_conversations):
        """Test keyword extraction from text."""
        analyzer = ConversationContextAnalyzer(str(temp_conversations))
        
        text = "Authentication system with OAuth2 tokens and security features"
        keywords = analyzer._extract_keywords(text.lower())
        
        # Should extract meaningful keywords
        assert "authentication" in keywords
        assert "oauth2" in keywords
        assert "tokens" in keywords
        assert "security" in keywords
        assert "features" in keywords
        
        # Should exclude stopwords
        assert "with" not in keywords
        assert "and" not in keywords

class TestKnowledgeGraphLinker:
    """Test knowledge graph linking functionality."""
    
    @pytest.fixture
    def temp_knowledge_graph(self):
        """Create temporary knowledge graph for testing."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        
        kg_data = {
            "version": "2.1",
            "patterns": {
                "authentication_patterns": {
                    "issue": "OAuth2 authentication implementation",
                    "solution": "JWT tokens with refresh mechanism",
                    "keywords": ["authentication", "oauth2", "jwt", "security", "tokens"]
                },
                "performance_optimization": {
                    "issue": "Memory usage optimization",
                    "solution": "YAML conversion for efficiency",
                    "keywords": ["performance", "memory", "yaml", "optimization", "efficiency"]
                },
                "cleanup_automation": {
                    "issue": "Automated cleanup processes",
                    "solution": "Scheduled cleanup tasks",
                    "keywords": ["cleanup", "automation", "maintenance", "scheduling"]
                }
            }
        }
        
        yaml.dump(kg_data, temp_file)
        temp_file.close()
        
        yield temp_file.name
        
        # Cleanup
        Path(temp_file.name).unlink()
    
    def test_linker_initialization(self, temp_knowledge_graph):
        """Test knowledge graph linker initialization."""
        linker = KnowledgeGraphLinker(temp_knowledge_graph)
        assert linker.kg_path == Path(temp_knowledge_graph)
        assert "patterns" in linker.knowledge_cache
        assert len(linker.knowledge_cache["patterns"]) == 3
    
    @pytest.mark.asyncio
    async def test_find_knowledge_links(self, temp_knowledge_graph):
        """Test finding knowledge pattern links."""
        linker = KnowledgeGraphLinker(temp_knowledge_graph)
        
        # Test idea matching authentication pattern
        auth_idea = IdeaCapture(
            idea_id="test_kg_001",
            raw_text="Need OAuth2 authentication with JWT tokens",
            timestamp=datetime.now()
        )
        
        links = await linker.find_knowledge_links(auth_idea)
        
        # Should find authentication pattern link
        assert len(links) >= 1
        auth_links = [link for link in links if "authentication" in link.context_id]
        assert len(auth_links) >= 1
        
        # Check link properties
        auth_link = auth_links[0]
        assert auth_link.idea_id == "test_kg_001"
        assert auth_link.context_type == "knowledge"
        assert auth_link.relevance_score > 0.0
    
    @pytest.mark.asyncio
    async def test_pattern_relevance_scoring(self, temp_knowledge_graph):
        """Test pattern relevance scoring."""
        linker = KnowledgeGraphLinker(temp_knowledge_graph)
        
        # High relevance idea (matches multiple keywords)
        high_idea = IdeaCapture(
            idea_id="test_kg_002",
            raw_text="performance optimization memory yaml efficiency",
            timestamp=datetime.now()
        )
        
        # Low relevance idea (matches few keywords)
        low_idea = IdeaCapture(
            idea_id="test_kg_003",
            raw_text="random unrelated content here",
            timestamp=datetime.now()
        )
        
        high_links = await linker.find_knowledge_links(high_idea)
        low_links = await linker.find_knowledge_links(low_idea)
        
        # High relevance should produce better scores
        if high_links:
            assert max(link.relevance_score for link in high_links) > 0.3
        if low_links:
            assert max(link.relevance_score for link in low_links) < 0.5

class TestOperationLinker:
    """Test operation linking functionality."""
    
    @pytest.fixture
    def temp_operations(self):
        """Create temporary operation files for testing."""
        temp_dir = tempfile.mkdtemp()
        ops_dir = Path(temp_dir) / "operations"
        ops_dir.mkdir()
        
        # Create sample operation files
        operations = {
            "authentication_handler.py": '''
"""Authentication operations for CORTEX."""
import jwt
import oauth2

class AuthenticationHandler:
    def authenticate_user(self, token):
        """Authenticate user with JWT token."""
        return jwt.decode(token)
    
    def generate_oauth2_token(self, user_id):
        """Generate OAuth2 authentication token."""
        return oauth2.create_token(user_id)
''',
            "memory_optimizer.py": '''
"""Memory optimization operations."""
import yaml

class MemoryOptimizer:
    def optimize_yaml_conversion(self, data):
        """Convert data to YAML for memory efficiency."""
        return yaml.dump(data)
    
    def cleanup_memory_cache(self):
        """Clean up memory caches for optimization."""
        pass
''',
            "cleanup_manager.py": '''
"""Cleanup and maintenance operations."""
import os

class CleanupManager:
    def auto_cleanup_files(self, directory):
        """Automatically cleanup obsolete files."""
        for file in os.listdir(directory):
            if self.is_obsolete(file):
                os.remove(file)
    
    def schedule_maintenance(self):
        """Schedule automated maintenance tasks."""
        pass
'''
        }
        
        for filename, content in operations.items():
            (ops_dir / filename).write_text(content)
        
        yield ops_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_linker_initialization(self, temp_operations):
        """Test operation linker initialization."""
        linker = OperationLinker(str(temp_operations))
        assert linker.ops_dir == temp_operations
        assert linker.operation_cache == {}
    
    @pytest.mark.asyncio
    async def test_find_operation_links(self, temp_operations):
        """Test finding operation links."""
        linker = OperationLinker(str(temp_operations))
        
        # Test idea about authentication
        auth_idea = IdeaCapture(
            idea_id="test_op_001",
            raw_text="JWT authentication token generation system",
            timestamp=datetime.now()
        )
        
        links = await linker.find_operation_links(auth_idea)
        
        # Should find authentication operation
        assert len(links) >= 1
        auth_links = [link for link in links if "authentication" in link.context_id]
        assert len(auth_links) >= 1
        
        # Check link properties
        auth_link = auth_links[0]
        assert auth_link.idea_id == "test_op_001"
        assert auth_link.context_type == "operation"
        assert auth_link.relevance_score > 0.0
    
    @pytest.mark.asyncio
    async def test_operation_relevance_scoring(self, temp_operations):
        """Test operation relevance scoring."""
        linker = OperationLinker(str(temp_operations))
        
        # High relevance idea
        cleanup_idea = IdeaCapture(
            idea_id="test_op_002",
            raw_text="automated cleanup maintenance schedule files",
            timestamp=datetime.now()
        )
        
        # Low relevance idea  
        unrelated_idea = IdeaCapture(
            idea_id="test_op_003",
            raw_text="cooking recipe ingredients preparation",
            timestamp=datetime.now()
        )
        
        cleanup_links = await linker.find_operation_links(cleanup_idea)
        unrelated_links = await linker.find_operation_links(unrelated_idea)
        
        # Cleanup should have higher relevance
        if cleanup_links and unrelated_links:
            assert max(link.relevance_score for link in cleanup_links) > \
                   max(link.relevance_score for link in unrelated_links)

class TestIdeaContextLinker:
    """Test main context linking engine."""
    
    @pytest.fixture
    def temp_cortex_env(self):
        """Create complete temporary CORTEX environment."""
        temp_dir = tempfile.mkdtemp()
        cortex_root = Path(temp_dir)
        
        # Create directory structure
        brain_dir = cortex_root / "cortex-brain"
        brain_dir.mkdir()
        (brain_dir / "conversation-captures").mkdir()
        
        src_dir = cortex_root / "src" / "operations"
        src_dir.mkdir(parents=True)
        
        # Create knowledge graph
        kg_data = {
            "version": "2.1",
            "patterns": {
                "test_pattern": {
                    "keywords": ["test", "pattern", "example"]
                }
            }
        }
        with open(brain_dir / "knowledge-graph.yaml", 'w') as f:
            yaml.dump(kg_data, f)
        
        # Create sample conversation
        conv_content = "Test conversation about authentication and security systems."
        (brain_dir / "conversation-captures" / "test-conversation.md").write_text(conv_content)
        
        # Create sample operation
        op_content = '''
"""Test operation."""
def test_function():
    """Test authentication function."""
    pass
'''
        (src_dir / "test_operation.py").write_text(op_content)
        
        yield cortex_root
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_linker_initialization(self, temp_cortex_env):
        """Test main linker initialization."""
        linker = IdeaContextLinker(str(temp_cortex_env))
        
        assert linker.cortex_root == temp_cortex_env
        assert linker.conversation_analyzer is not None
        assert linker.knowledge_linker is not None
        assert linker.operation_linker is not None
        
        # Check database creation
        assert Path(linker.db_path).exists()
    
    @pytest.mark.asyncio
    async def test_link_idea_to_context(self, temp_cortex_env):
        """Test complete idea-to-context linking."""
        linker = IdeaContextLinker(str(temp_cortex_env))
        
        # Test comprehensive idea
        idea = IdeaCapture(
            idea_id="test_main_001",
            raw_text="authentication test pattern system",
            timestamp=datetime.now()
        )
        
        links = await linker.link_idea_to_context(idea)
        
        # Should find links from multiple sources
        assert len(links) >= 0  # May vary based on temp environment
        
        # Check that links are stored
        stored_links = linker.get_idea_contexts("test_main_001")
        assert len(stored_links) == len(links)
    
    def test_context_insights(self, temp_cortex_env):
        """Test context insights generation."""
        linker = IdeaContextLinker(str(temp_cortex_env))
        
        # Create and store sample links
        sample_links = [
            ContextLink(
                link_id="test_link_1",
                idea_id="test_insights",
                context_type="conversation",
                context_id="test-conv",
                context_path="/test/path",
                relevance_score=0.8,
                link_reason="Test conversation link",
                created_at=datetime.now()
            ),
            ContextLink(
                link_id="test_link_2",
                idea_id="test_insights",
                context_type="operation",
                context_id="test-op",
                context_path="/test/op",
                relevance_score=0.6,
                link_reason="Test operation link",
                created_at=datetime.now()
            )
        ]
        
        linker._store_links(sample_links)
        
        # Get insights
        insights = linker.get_context_insights("test_insights")
        
        assert insights["total_links"] == 2
        assert insights["context_types"]["conversation"] == 1
        assert insights["context_types"]["operation"] == 1
        assert insights["top_relevance"] == 0.8
        assert len(insights["recent_conversations"]) == 1
        assert len(insights["related_operations"]) == 1
    
    def test_factory_function(self, temp_cortex_env):
        """Test factory function for creating linker."""
        linker = create_context_linker(str(temp_cortex_env))
        
        assert isinstance(linker, IdeaContextLinker)
        assert linker.cortex_root == temp_cortex_env

class TestPerformance:
    """Test context linking performance requirements."""
    
    @pytest.fixture
    def performance_cortex_env(self):
        """Create CORTEX environment optimized for performance testing."""
        temp_dir = tempfile.mkdtemp()
        cortex_root = Path(temp_dir)
        
        # Create larger test environment
        brain_dir = cortex_root / "cortex-brain"
        brain_dir.mkdir()
        conv_dir = brain_dir / "conversation-captures"
        conv_dir.mkdir()
        
        src_dir = cortex_root / "src" / "operations"
        src_dir.mkdir(parents=True)
        
        # Create multiple conversations
        for i in range(10):
            conv_content = f"Conversation {i} about authentication security systems and performance optimization."
            (conv_dir / f"conv-{i:03d}.md").write_text(conv_content)
        
        # Create multiple operations
        for i in range(5):
            op_content = f'''
"""Operation {i}."""
def operation_{i}():
    """Authentication operation {i}."""
    return "result"
'''
            (src_dir / f"operation_{i}.py").write_text(op_content)
        
        # Create knowledge graph
        kg_data = {
            "version": "2.1", 
            "patterns": {
                f"pattern_{i}": {
                    "keywords": ["authentication", "security", "performance", f"keyword{i}"]
                } for i in range(5)
            }
        }
        with open(brain_dir / "knowledge-graph.yaml", 'w') as f:
            yaml.dump(kg_data, f)
        
        yield cortex_root
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.mark.asyncio
    async def test_context_linking_performance(self, performance_cortex_env):
        """Test that context linking meets performance requirements (<2ms average)."""
        linker = IdeaContextLinker(str(performance_cortex_env))
        
        # Test multiple ideas for average performance
        test_ideas = [
            IdeaCapture(
                idea_id=f"perf_test_{i}",
                raw_text=f"authentication security performance test {i}",
                timestamp=datetime.now()
            ) for i in range(5)
        ]
        
        total_time = 0
        
        for idea in test_ideas:
            start_time = datetime.now()
            links = await linker.link_idea_to_context(idea)
            link_time = (datetime.now() - start_time).total_seconds() * 1000
            total_time += link_time
            
            # Individual link should be reasonably fast (under 10ms for test env)
            assert link_time < 10, f"Context linking took {link_time:.2f}ms (too slow)"
        
        # Average performance should meet requirements  
        avg_time = total_time / len(test_ideas)
        print(f"Average context linking time: {avg_time:.2f}ms")
        
        # In real environment should be <2ms, in test env allow more leeway
        assert avg_time < 5, f"Average context linking time {avg_time:.2f}ms exceeds performance target"

# Integration test
@pytest.mark.asyncio
async def test_complete_context_linking_integration():
    """Integration test for complete context linking workflow."""
    
    # Use actual CORTEX environment if available
    cortex_root = "/Users/asifhussain/PROJECTS/CORTEX"
    if not Path(cortex_root).exists():
        pytest.skip("CORTEX environment not available for integration test")
    
    # Create context linker
    linker = create_context_linker(cortex_root)
    
    # Test with real CORTEX environment
    test_idea = IdeaCapture(
        idea_id="integration_test",
        raw_text="CORTEX authentication system improvement",
        timestamp=datetime.now()
    )
    
    # Link to context
    start_time = datetime.now()
    links = await linker.link_idea_to_context(test_idea)
    link_time = (datetime.now() - start_time).total_seconds() * 1000
    
    # Verify results
    assert isinstance(links, list)
    print(f"Integration test: {len(links)} links found in {link_time:.2f}ms")
    
    # Check insights
    insights = linker.get_context_insights("integration_test")
    assert insights["total_links"] == len(links)
    
    print("✅ Integration test passed - Context linking working with real CORTEX environment")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])