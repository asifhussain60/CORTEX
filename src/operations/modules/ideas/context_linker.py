#!/usr/bin/env python3
"""
CORTEX 3.0 Phase 2 - IDEA Capture System: Context Linker
Ultra-fast idea-to-ecosystem linking system for CORTEX.

Purpose:
    Create intelligent bridges between captured ideas and CORTEX ecosystem:
    - Link ideas to relevant conversations and projects
    - Connect with knowledge graph patterns
    - Associate with active operations
    - Provide context-aware suggestions

Performance Requirements:
    - Context linking: <2ms (average)
    - Context search: <5ms (average)
    - Link resolution: <1ms (average)
"""

import asyncio
import sqlite3
import logging
import json
import yaml
import os
import re
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple, Set
from pathlib import Path
from threading import Lock

from .idea_queue import IdeaCapture, IdeaQueue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ContextLink:
    """Represents a link between an idea and CORTEX ecosystem context."""
    link_id: str
    idea_id: str
    context_type: str  # 'conversation', 'operation', 'knowledge', 'project'
    context_id: str
    context_path: str
    relevance_score: float
    link_reason: str
    created_at: datetime

@dataclass
class ContextMetadata:
    """Metadata about available context sources."""
    source_type: str
    source_path: str
    last_modified: datetime
    content_summary: str
    keywords: Set[str]
    entity_count: int

class ConversationContextAnalyzer:
    """Analyzes conversation captures for idea linking."""
    
    def __init__(self, capture_dir: str):
        self.capture_dir = Path(capture_dir)
        self.conversation_cache = {}
        self.cache_lock = Lock()
    
    async def find_relevant_conversations(self, idea: IdeaCapture, limit: int = 3) -> List[ContextLink]:
        """Find conversations relevant to an idea."""
        start_time = datetime.now()
        links = []
        
        try:
            # Get recent conversation files
            conversations = self._get_recent_conversations()
            
            # Score relevance for each conversation
            for conv_file in conversations[:10]:  # Limit search scope for performance
                relevance = await self._score_conversation_relevance(idea, conv_file)
                if relevance > 0.3:  # Threshold for relevance
                    link = ContextLink(
                        link_id=f"conv_{idea.idea_id}_{conv_file.stem}",
                        idea_id=idea.idea_id,
                        context_type="conversation",
                        context_id=conv_file.stem,
                        context_path=str(conv_file),
                        relevance_score=relevance,
                        link_reason=f"Keyword match with conversation about {self._extract_topic(conv_file)}",
                        created_at=datetime.now()
                    )
                    links.append(link)
            
            # Sort by relevance and limit results
            links.sort(key=lambda x: x.relevance_score, reverse=True)
            links = links[:limit]
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            logger.info(f"Conversation context analysis: {processing_time:.2f}ms, found {len(links)} links")
            
            return links
            
        except Exception as e:
            logger.error(f"Error finding relevant conversations: {e}")
            return []
    
    def _get_recent_conversations(self) -> List[Path]:
        """Get recent conversation files, sorted by modification time."""
        if not self.capture_dir.exists():
            return []
        
        conversations = []
        for file_path in self.capture_dir.glob("*.md"):
            if file_path.is_file():
                conversations.append(file_path)
        
        # Sort by modification time (newest first)
        conversations.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return conversations
    
    async def _score_conversation_relevance(self, idea: IdeaCapture, conv_file: Path) -> float:
        """Score how relevant a conversation is to an idea."""
        try:
            # Use cache for conversation content
            with self.cache_lock:
                if str(conv_file) not in self.conversation_cache:
                    with open(conv_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.conversation_cache[str(conv_file)] = content
                else:
                    content = self.conversation_cache[str(conv_file)]
            
            # Extract keywords from idea
            idea_keywords = self._extract_keywords(idea.raw_text.lower())
            
            # Extract keywords from conversation
            conv_keywords = self._extract_keywords(content.lower())
            
            # Calculate keyword overlap score
            if not idea_keywords:
                return 0.0
            
            overlap = idea_keywords.intersection(conv_keywords)
            overlap_score = len(overlap) / len(idea_keywords)
            
            # Boost score for recent conversations
            file_age_days = (datetime.now() - datetime.fromtimestamp(conv_file.stat().st_mtime)).days
            recency_boost = max(0.1, 1.0 - (file_age_days / 30.0))  # Decay over 30 days
            
            return overlap_score * recency_boost
            
        except Exception as e:
            logger.error(f"Error scoring conversation relevance: {e}")
            return 0.0
    
    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract meaningful keywords from text."""
        # Remove common stopwords and extract meaningful terms
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        # Extract words (3+ characters, not stopwords)
        words = re.findall(r'\b[a-z]{3,}\b', text)
        return {word for word in words if word not in stopwords}
    
    def _extract_topic(self, conv_file: Path) -> str:
        """Extract topic from conversation filename or content."""
        # Extract topic from filename
        filename = conv_file.stem
        if filename.startswith('2025-'):
            # Remove date prefix
            topic = filename[11:]  # Remove "2025-11-XX-"
            return topic.replace('-', ' ').title()
        return filename.replace('-', ' ').title()

class KnowledgeGraphLinker:
    """Links ideas with knowledge graph patterns."""
    
    def __init__(self, knowledge_graph_path: str):
        self.kg_path = Path(knowledge_graph_path)
        self.knowledge_cache = {}
        self.cache_lock = Lock()
        self._load_knowledge_graph()
    
    def _load_knowledge_graph(self):
        """Load and cache knowledge graph data."""
        try:
            if self.kg_path.exists():
                with open(self.kg_path, 'r', encoding='utf-8') as f:
                    self.knowledge_cache = yaml.safe_load(f)
                logger.info(f"Loaded knowledge graph with {len(self.knowledge_cache.get('patterns', {}))} patterns")
        except Exception as e:
            logger.error(f"Error loading knowledge graph: {e}")
            self.knowledge_cache = {}
    
    async def find_knowledge_links(self, idea: IdeaCapture, limit: int = 3) -> List[ContextLink]:
        """Find knowledge graph patterns relevant to an idea."""
        start_time = datetime.now()
        links = []
        
        try:
            patterns = self.knowledge_cache.get('patterns', {})
            if not patterns:
                return links
            
            # Extract idea keywords
            idea_text = idea.raw_text.lower()
            idea_keywords = self._extract_keywords(idea_text)
            
            # Score each knowledge pattern
            for pattern_name, pattern_data in patterns.items():
                relevance = self._score_pattern_relevance(idea_keywords, pattern_data)
                if relevance > 0.2:  # Lower threshold for knowledge patterns
                    link = ContextLink(
                        link_id=f"kg_{idea.idea_id}_{pattern_name}",
                        idea_id=idea.idea_id,
                        context_type="knowledge",
                        context_id=pattern_name,
                        context_path=str(self.kg_path),
                        relevance_score=relevance,
                        link_reason=f"Related to knowledge pattern: {pattern_name}",
                        created_at=datetime.now()
                    )
                    links.append(link)
            
            # Sort by relevance and limit results
            links.sort(key=lambda x: x.relevance_score, reverse=True)
            links = links[:limit]
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            logger.info(f"Knowledge graph linking: {processing_time:.2f}ms, found {len(links)} links")
            
            return links
            
        except Exception as e:
            logger.error(f"Error finding knowledge links: {e}")
            return []
    
    def _score_pattern_relevance(self, idea_keywords: Set[str], pattern_data) -> float:
        """Score relevance between idea and knowledge pattern."""
        try:
            # Convert pattern data to string for keyword extraction
            pattern_text = str(pattern_data).lower()
            pattern_keywords = self._extract_keywords(pattern_text)
            
            # Calculate keyword overlap
            if not idea_keywords:
                return 0.0
            
            overlap = idea_keywords.intersection(pattern_keywords)
            return len(overlap) / len(idea_keywords)
            
        except Exception:
            return 0.0
    
    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract meaningful keywords from text."""
        # Simple keyword extraction (same as ConversationContextAnalyzer)
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
        
        words = re.findall(r'\b[a-z]{3,}\b', text)
        return {word for word in words if word not in stopwords}

class OperationLinker:
    """Links ideas with active CORTEX operations."""
    
    def __init__(self, operations_dir: str):
        self.ops_dir = Path(operations_dir)
        self.operation_cache = {}
        self.cache_lock = Lock()
    
    async def find_operation_links(self, idea: IdeaCapture, limit: int = 2) -> List[ContextLink]:
        """Find operations relevant to an idea."""
        start_time = datetime.now()
        links = []
        
        try:
            # Get operation modules
            operation_files = self._get_operation_files()
            
            # Extract idea keywords
            idea_keywords = self._extract_keywords(idea.raw_text.lower())
            
            # Score each operation
            for op_file in operation_files[:5]:  # Limit for performance
                relevance = await self._score_operation_relevance(idea_keywords, op_file)
                if relevance > 0.2:
                    link = ContextLink(
                        link_id=f"op_{idea.idea_id}_{op_file.stem}",
                        idea_id=idea.idea_id,
                        context_type="operation",
                        context_id=op_file.stem,
                        context_path=str(op_file),
                        relevance_score=relevance,
                        link_reason=f"Related to operation: {op_file.stem}",
                        created_at=datetime.now()
                    )
                    links.append(link)
            
            # Sort by relevance and limit results
            links.sort(key=lambda x: x.relevance_score, reverse=True)
            links = links[:limit]
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            logger.info(f"Operation linking: {processing_time:.2f}ms, found {len(links)} links")
            
            return links
            
        except Exception as e:
            logger.error(f"Error finding operation links: {e}")
            return []
    
    def _get_operation_files(self) -> List[Path]:
        """Get Python operation files."""
        operations = []
        if self.ops_dir.exists():
            for py_file in self.ops_dir.glob("**/*.py"):
                if py_file.is_file() and not py_file.name.startswith('__'):
                    operations.append(py_file)
        return operations
    
    async def _score_operation_relevance(self, idea_keywords: Set[str], op_file: Path) -> float:
        """Score relevance between idea and operation."""
        try:
            # Use cache for operation content
            with self.cache_lock:
                if str(op_file) not in self.operation_cache:
                    with open(op_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.operation_cache[str(op_file)] = content
                else:
                    content = self.operation_cache[str(op_file)]
            
            # Extract keywords from operation
            op_keywords = self._extract_keywords(content.lower())
            
            # Calculate keyword overlap
            if not idea_keywords:
                return 0.0
            
            overlap = idea_keywords.intersection(op_keywords)
            return len(overlap) / len(idea_keywords)
            
        except Exception:
            return 0.0
    
    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract meaningful keywords from text."""
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'class', 'def', 'import', 'from', 'return', 'if', 'else', 'elif', 'for', 'while', 'try', 'except', 'with', 'as', 'pass', 'break', 'continue'}
        
        words = re.findall(r'\b[a-z]{3,}\b', text)
        return {word for word in words if word not in stopwords}

class IdeaContextLinker:
    """Main context linking engine for IDEA system."""
    
    def __init__(self, cortex_root: str, db_path: Optional[str] = None):
        self.cortex_root = Path(cortex_root)
        self.db_path = db_path or str(self.cortex_root / "cortex-brain" / "idea-contexts.db")
        self.db_lock = Lock()
        
        # Initialize context analyzers
        self.conversation_analyzer = ConversationContextAnalyzer(
            self.cortex_root / "cortex-brain" / "conversation-captures"
        )
        self.knowledge_linker = KnowledgeGraphLinker(
            self.cortex_root / "cortex-brain" / "knowledge-graph.yaml"
        )
        self.operation_linker = OperationLinker(
            self.cortex_root / "src" / "operations"
        )
        
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize the context links database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS context_links (
                    link_id TEXT PRIMARY KEY,
                    idea_id TEXT NOT NULL,
                    context_type TEXT NOT NULL,
                    context_id TEXT NOT NULL,
                    context_path TEXT NOT NULL,
                    relevance_score REAL NOT NULL,
                    link_reason TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_idea_id ON context_links(idea_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_context_type ON context_links(context_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_relevance ON context_links(relevance_score)")
            conn.commit()
    
    async def link_idea_to_context(self, idea: IdeaCapture) -> List[ContextLink]:
        """Link an idea to relevant CORTEX ecosystem context."""
        start_time = datetime.now()
        all_links = []
        
        try:
            # Run all analyzers in parallel for maximum performance
            tasks = [
                self.conversation_analyzer.find_relevant_conversations(idea),
                self.knowledge_linker.find_knowledge_links(idea),
                self.operation_linker.find_operation_links(idea)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Collect successful results
            for result in results:
                if isinstance(result, list):
                    all_links.extend(result)
                elif isinstance(result, Exception):
                    logger.error(f"Context linking error: {result}")
            
            # Store links in database
            if all_links:
                self._store_links(all_links)
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            logger.info(f"Complete context linking: {processing_time:.2f}ms, found {len(all_links)} total links")
            
            return all_links
            
        except Exception as e:
            logger.error(f"Error linking idea to context: {e}")
            return []
    
    def _store_links(self, links: List[ContextLink]):
        """Store context links in database."""
        with self.db_lock:
            with sqlite3.connect(self.db_path) as conn:
                for link in links:
                    conn.execute("""
                        INSERT OR REPLACE INTO context_links 
                        (link_id, idea_id, context_type, context_id, context_path, relevance_score, link_reason, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        link.link_id,
                        link.idea_id,
                        link.context_type,
                        link.context_id,
                        link.context_path,
                        link.relevance_score,
                        link.link_reason,
                        link.created_at.isoformat()
                    ))
                conn.commit()
    
    def get_idea_contexts(self, idea_id: str) -> List[ContextLink]:
        """Get all context links for an idea."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT link_id, idea_id, context_type, context_id, context_path, 
                       relevance_score, link_reason, created_at
                FROM context_links 
                WHERE idea_id = ?
                ORDER BY relevance_score DESC
            """, (idea_id,))
            
            links = []
            for row in cursor.fetchall():
                links.append(ContextLink(
                    link_id=row[0],
                    idea_id=row[1],
                    context_type=row[2],
                    context_id=row[3],
                    context_path=row[4],
                    relevance_score=row[5],
                    link_reason=row[6],
                    created_at=datetime.fromisoformat(row[7])
                ))
            return links
    
    def get_context_insights(self, idea_id: str) -> Dict[str, any]:
        """Get context insights summary for an idea."""
        links = self.get_idea_contexts(idea_id)
        
        insights = {
            "total_links": len(links),
            "context_types": {},
            "top_relevance": 0.0,
            "recent_conversations": [],
            "related_operations": [],
            "knowledge_patterns": []
        }
        
        for link in links:
            # Count by context type
            if link.context_type not in insights["context_types"]:
                insights["context_types"][link.context_type] = 0
            insights["context_types"][link.context_type] += 1
            
            # Track top relevance
            insights["top_relevance"] = max(insights["top_relevance"], link.relevance_score)
            
            # Categorize by type
            if link.context_type == "conversation":
                insights["recent_conversations"].append({
                    "topic": link.context_id,
                    "relevance": link.relevance_score
                })
            elif link.context_type == "operation":
                insights["related_operations"].append({
                    "operation": link.context_id,
                    "relevance": link.relevance_score
                })
            elif link.context_type == "knowledge":
                insights["knowledge_patterns"].append({
                    "pattern": link.context_id,
                    "relevance": link.relevance_score
                })
        
        return insights

# Factory function for easy instantiation
def create_context_linker(cortex_root: str) -> IdeaContextLinker:
    """Create a new IdeaContextLinker instance."""
    return IdeaContextLinker(cortex_root)

# Demo function for testing
async def demo_context_linking():
    """Demonstrate context linking capabilities."""
    print("\n🔗 CORTEX IDEA Context Linking Demo")
    print("=" * 50)
    
    # Create context linker
    cortex_root = "/Users/asifhussain/PROJECTS/CORTEX"
    linker = create_context_linker(cortex_root)
    
    # Create sample ideas to test linking
    test_ideas = [
        IdeaCapture(
            idea_id="demo_001",
            raw_text="Need better authentication system for API endpoints",
            timestamp=datetime.now()
        ),
        IdeaCapture(
            idea_id="demo_002", 
            raw_text="CORTEX conversation memory optimization using YAML",
            timestamp=datetime.now()
        ),
        IdeaCapture(
            idea_id="demo_003",
            raw_text="Implement auto-cleanup for obsolete test files",
            timestamp=datetime.now()
        )
    ]
    
    # Link each idea to context
    for idea in test_ideas:
        print(f"\n📝 Linking idea: '{idea.raw_text}'")
        
        start_time = datetime.now()
        links = await linker.link_idea_to_context(idea)
        link_time = (datetime.now() - start_time).total_seconds() * 1000
        
        print(f"⚡ Context linking completed in {link_time:.2f}ms")
        print(f"🔗 Found {len(links)} context links:")
        
        for link in links:
            print(f"  • {link.context_type}: {link.context_id} (relevance: {link.relevance_score:.3f})")
            print(f"    Reason: {link.link_reason}")
        
        # Get context insights
        insights = linker.get_context_insights(idea.idea_id)
        print(f"\n📊 Context Insights:")
        print(f"  • Total links: {insights['total_links']}")
        print(f"  • Context types: {dict(insights['context_types'])}")
        print(f"  • Top relevance: {insights['top_relevance']:.3f}")
        if insights['recent_conversations']:
            print(f"  • Related conversations: {len(insights['recent_conversations'])}")
        if insights['knowledge_patterns']:
            print(f"  • Knowledge patterns: {len(insights['knowledge_patterns'])}")

if __name__ == "__main__":
    asyncio.run(demo_context_linking())