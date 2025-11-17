"""
Tier 2: Knowledge Graph Tests

Tests the knowledge graph functionality that learns from past interactions,
stores patterns, and provides intelligence for future operations.

Key Features Tested:
- Pattern storage and retrieval
- Confidence scoring and decay
- Workflow template learning
- File relationship mapping
- Intent pattern matching
- Performance validation

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import json


# ============================================================================
# Mock Knowledge Graph Implementation
# ============================================================================

@dataclass
class Pattern:
    """Represents a learned pattern in the knowledge graph"""
    pattern_id: str
    pattern_type: str  # 'intent', 'workflow', 'file_relationship', 'validation'
    content: Dict[str, Any]
    confidence: float
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    source: str = "user_interaction"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def decay_confidence(self, days_since_last_access: int) -> float:
        """Calculate confidence decay based on time since last access"""
        # Decay formula: confidence * exp(-0.1 * days)
        import math
        decay_factor = math.exp(-0.1 * days_since_last_access)
        return self.confidence * decay_factor
    
    def boost_confidence(self, boost_amount: float = 0.05) -> None:
        """Boost confidence when pattern is validated"""
        self.confidence = min(1.0, self.confidence + boost_amount)
        self.access_count += 1
        self.last_accessed = datetime.now()


@dataclass
class WorkflowTemplate:
    """Represents a workflow pattern learned from successful executions"""
    template_id: str
    name: str
    steps: List[str]
    success_rate: float
    usage_count: int
    avg_duration_seconds: float
    prerequisites: List[str] = field(default_factory=list)
    common_errors: List[str] = field(default_factory=list)


@dataclass
class FileRelationship:
    """Represents relationship between files learned from edit patterns"""
    file_a: str
    file_b: str
    relationship_type: str  # 'implements', 'depends_on', 'tested_by', 'documented_by'
    confidence: float
    co_edit_count: int
    last_co_edited: datetime


class KnowledgeGraph:
    """Mock knowledge graph for testing Tier 2 functionality"""
    
    def __init__(self, max_patterns: int = 1000):
        self.max_patterns = max_patterns
        self.patterns: Dict[str, Pattern] = {}
        self.workflow_templates: Dict[str, WorkflowTemplate] = {}
        self.file_relationships: List[FileRelationship] = []
        self.intent_patterns: Dict[str, List[Pattern]] = {}  # intent -> patterns
    
    # Pattern Storage
    def store_pattern(self, pattern: Pattern) -> str:
        """Store a pattern in the knowledge graph"""
        if len(self.patterns) >= self.max_patterns:
            # Evict lowest confidence pattern
            self._evict_lowest_confidence()
        
        self.patterns[pattern.pattern_id] = pattern
        
        # Index by intent if it's an intent pattern
        if pattern.pattern_type == 'intent':
            intent = pattern.content.get('intent')
            if intent:
                if intent not in self.intent_patterns:
                    self.intent_patterns[intent] = []
                self.intent_patterns[intent].append(pattern)
        
        return pattern.pattern_id
    
    def retrieve_pattern(self, pattern_id: str) -> Optional[Pattern]:
        """Retrieve a pattern by ID"""
        pattern = self.patterns.get(pattern_id)
        if pattern:
            pattern.access_count += 1
            pattern.last_accessed = datetime.now()
        return pattern
    
    def search_patterns(self, pattern_type: Optional[str] = None, 
                       min_confidence: float = 0.0) -> List[Pattern]:
        """Search patterns by type and confidence threshold"""
        results = []
        for pattern in self.patterns.values():
            if pattern_type and pattern.pattern_type != pattern_type:
                continue
            if pattern.confidence < min_confidence:
                continue
            results.append(pattern)
        
        # Sort by confidence descending
        results.sort(key=lambda p: p.confidence, reverse=True)
        return results
    
    # Confidence Management
    def apply_confidence_decay(self) -> Dict[str, int]:
        """Apply confidence decay to all patterns based on last access time"""
        stats = {
            'patterns_decayed': 0,
            'patterns_removed': 0
        }
        
        now = datetime.now()
        patterns_to_remove = []
        
        for pattern_id, pattern in self.patterns.items():
            days_since_access = (now - pattern.last_accessed).days
            if days_since_access > 0:
                new_confidence = pattern.decay_confidence(days_since_access)
                
                if new_confidence < 0.1:  # Remove very low confidence patterns
                    patterns_to_remove.append(pattern_id)
                    stats['patterns_removed'] += 1
                else:
                    pattern.confidence = new_confidence
                    stats['patterns_decayed'] += 1
        
        # Remove low confidence patterns
        for pattern_id in patterns_to_remove:
            del self.patterns[pattern_id]
        
        return stats
    
    # Workflow Templates
    def store_workflow_template(self, template: WorkflowTemplate) -> str:
        """Store a workflow template learned from successful executions"""
        self.workflow_templates[template.template_id] = template
        return template.template_id
    
    def find_workflow_template(self, intent: str) -> Optional[WorkflowTemplate]:
        """Find best workflow template for an intent"""
        # In real implementation, would use similarity matching
        candidates = [t for t in self.workflow_templates.values() 
                     if intent.lower() in t.name.lower()]
        
        if not candidates:
            return None
        
        # Return highest success rate
        return max(candidates, key=lambda t: t.success_rate)
    
    # File Relationships
    def store_file_relationship(self, relationship: FileRelationship) -> None:
        """Store a file relationship learned from edit patterns"""
        # Check if relationship exists
        existing = self._find_relationship(relationship.file_a, relationship.file_b, 
                                          relationship.relationship_type)
        
        if existing:
            # Update existing relationship
            existing.confidence = min(1.0, existing.confidence + 0.1)
            existing.co_edit_count += 1
            existing.last_co_edited = relationship.last_co_edited
        else:
            # Add new relationship
            self.file_relationships.append(relationship)
    
    def get_related_files(self, file_path: str, relationship_type: Optional[str] = None,
                         min_confidence: float = 0.5) -> List[FileRelationship]:
        """Get files related to a given file"""
        results = []
        for rel in self.file_relationships:
            if rel.file_a == file_path or rel.file_b == file_path:
                if relationship_type and rel.relationship_type != relationship_type:
                    continue
                if rel.confidence < min_confidence:
                    continue
                results.append(rel)
        
        # Sort by confidence descending
        results.sort(key=lambda r: r.confidence, reverse=True)
        return results
    
    # Intent Pattern Matching
    def predict_intent(self, user_input: str) -> List[Dict[str, Any]]:
        """Predict intent based on learned patterns"""
        results = []
        
        for intent, patterns in self.intent_patterns.items():
            best_match = None
            highest_confidence = 0.0
            
            for pattern in patterns:
                # Simple matching: check if pattern keywords in input
                keywords = pattern.content.get('keywords', [])
                if any(kw.lower() in user_input.lower() for kw in keywords):
                    if pattern.confidence > highest_confidence:
                        highest_confidence = pattern.confidence
                        best_match = pattern
            
            if best_match:
                results.append({
                    'intent': intent,
                    'confidence': best_match.confidence,
                    'pattern_id': best_match.pattern_id,
                    'usage_count': best_match.access_count
                })
        
        # Sort by confidence descending
        results.sort(key=lambda r: r['confidence'], reverse=True)
        return results
    
    # Utility Methods
    def _evict_lowest_confidence(self) -> None:
        """Evict pattern with lowest confidence to make room"""
        if not self.patterns:
            return
        
        lowest_pattern = min(self.patterns.values(), key=lambda p: p.confidence)
        del self.patterns[lowest_pattern.pattern_id]
    
    def _find_relationship(self, file_a: str, file_b: str, 
                          rel_type: str) -> Optional[FileRelationship]:
        """Find existing relationship between two files"""
        for rel in self.file_relationships:
            if ((rel.file_a == file_a and rel.file_b == file_b) or
                (rel.file_a == file_b and rel.file_b == file_a)):
                if rel.relationship_type == rel_type:
                    return rel
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge graph statistics"""
        return {
            'total_patterns': len(self.patterns),
            'patterns_by_type': self._count_by_type(),
            'avg_confidence': sum(p.confidence for p in self.patterns.values()) / len(self.patterns) if self.patterns else 0.0,
            'total_workflow_templates': len(self.workflow_templates),
            'total_file_relationships': len(self.file_relationships),
            'total_intents_learned': len(self.intent_patterns)
        }
    
    def _count_by_type(self) -> Dict[str, int]:
        """Count patterns by type"""
        counts = {}
        for pattern in self.patterns.values():
            counts[pattern.pattern_type] = counts.get(pattern.pattern_type, 0) + 1
        return counts


# ============================================================================
# Test: Pattern Storage and Retrieval
# ============================================================================

class TestPatternStorage:
    """Test pattern storage and retrieval operations"""
    
    def test_store_and_retrieve_pattern(self):
        """Should store and retrieve patterns correctly"""
        kg = KnowledgeGraph()
        
        pattern = Pattern(
            pattern_id="pattern_001",
            pattern_type="intent",
            content={'intent': 'PLAN', 'keywords': ['plan', 'feature', 'design']},
            confidence=0.85,
            created_at=datetime.now(),
            last_accessed=datetime.now()
        )
        
        # Store pattern
        pattern_id = kg.store_pattern(pattern)
        assert pattern_id == "pattern_001"
        assert len(kg.patterns) == 1
        
        # Retrieve pattern
        retrieved = kg.retrieve_pattern("pattern_001")
        assert retrieved is not None
        assert retrieved.pattern_id == "pattern_001"
        assert retrieved.confidence == 0.85
        assert retrieved.access_count == 1  # Incremented on retrieval
    
    def test_pattern_capacity_limit(self):
        """Should evict lowest confidence pattern when at capacity"""
        kg = KnowledgeGraph(max_patterns=3)
        
        # Store 3 patterns
        for i in range(3):
            pattern = Pattern(
                pattern_id=f"pattern_{i:03d}",
                pattern_type="intent",
                content={},
                confidence=0.5 + (i * 0.1),  # 0.5, 0.6, 0.7
                created_at=datetime.now(),
                last_accessed=datetime.now()
            )
            kg.store_pattern(pattern)
        
        assert len(kg.patterns) == 3
        
        # Store 4th pattern (should evict lowest confidence)
        new_pattern = Pattern(
            pattern_id="pattern_003",
            pattern_type="intent",
            content={},
            confidence=0.8,
            created_at=datetime.now(),
            last_accessed=datetime.now()
        )
        kg.store_pattern(new_pattern)
        
        assert len(kg.patterns) == 3
        assert "pattern_000" not in kg.patterns  # Lowest confidence evicted
        assert "pattern_003" in kg.patterns
    
    def test_search_patterns_by_type(self):
        """Should search patterns by type"""
        kg = KnowledgeGraph()
        
        # Store different pattern types
        kg.store_pattern(Pattern("p1", "intent", {}, 0.8, datetime.now(), datetime.now()))
        kg.store_pattern(Pattern("p2", "workflow", {}, 0.9, datetime.now(), datetime.now()))
        kg.store_pattern(Pattern("p3", "intent", {}, 0.7, datetime.now(), datetime.now()))
        
        # Search for intent patterns
        results = kg.search_patterns(pattern_type="intent")
        assert len(results) == 2
        assert all(p.pattern_type == "intent" for p in results)
        
        # Results should be sorted by confidence (highest first)
        assert results[0].confidence > results[1].confidence
    
    def test_search_patterns_by_confidence(self):
        """Should filter patterns by confidence threshold"""
        kg = KnowledgeGraph()
        
        kg.store_pattern(Pattern("p1", "intent", {}, 0.9, datetime.now(), datetime.now()))
        kg.store_pattern(Pattern("p2", "intent", {}, 0.7, datetime.now(), datetime.now()))
        kg.store_pattern(Pattern("p3", "intent", {}, 0.5, datetime.now(), datetime.now()))
        
        # Search with confidence threshold
        results = kg.search_patterns(min_confidence=0.75)
        assert len(results) == 1
        assert results[0].confidence == 0.9


# ============================================================================
# Test: Confidence Scoring and Decay
# ============================================================================

class TestConfidenceManagement:
    """Test confidence scoring and decay mechanisms"""
    
    def test_confidence_boost(self):
        """Should boost confidence when pattern is validated"""
        pattern = Pattern("p1", "intent", {}, 0.7, datetime.now(), datetime.now())
        
        initial_confidence = pattern.confidence
        initial_access_count = pattern.access_count
        
        pattern.boost_confidence(0.1)
        
        assert pattern.confidence == min(1.0, initial_confidence + 0.1)
        assert pattern.access_count == initial_access_count + 1
    
    def test_confidence_boost_capped_at_100(self):
        """Should cap confidence at 1.0"""
        pattern = Pattern("p1", "intent", {}, 0.95, datetime.now(), datetime.now())
        
        pattern.boost_confidence(0.1)
        
        assert pattern.confidence == 1.0  # Capped at 1.0
    
    def test_confidence_decay_calculation(self):
        """Should calculate confidence decay based on time"""
        pattern = Pattern("p1", "intent", {}, 0.9, datetime.now(), datetime.now())
        
        # Test decay after 10 days
        decayed = pattern.decay_confidence(days_since_last_access=10)
        
        # Should decay: 0.9 * exp(-0.1 * 10) ≈ 0.331
        assert 0.3 < decayed < 0.4
        assert decayed < pattern.confidence  # Should be lower
    
    def test_apply_confidence_decay_to_graph(self):
        """Should apply decay to all patterns in graph"""
        kg = KnowledgeGraph()
        
        # Store patterns with different last access times
        old_date = datetime.now() - timedelta(days=30)
        kg.store_pattern(Pattern("p1", "intent", {}, 0.9, old_date, old_date))
        kg.store_pattern(Pattern("p2", "intent", {}, 0.8, datetime.now(), datetime.now()))
        
        # Apply decay
        stats = kg.apply_confidence_decay()
        
        # Old pattern should have decayed and been removed (30 days -> very low confidence)
        assert stats['patterns_removed'] >= 1
        assert "p1" not in kg.patterns
        assert "p2" in kg.patterns  # Recent pattern should remain


# ============================================================================
# Test: Workflow Templates
# ============================================================================

class TestWorkflowTemplates:
    """Test workflow template learning and retrieval"""
    
    def test_store_workflow_template(self):
        """Should store workflow templates"""
        kg = KnowledgeGraph()
        
        template = WorkflowTemplate(
            template_id="wf_001",
            name="Feature Implementation Workflow",
            steps=["Plan", "Design", "Implement", "Test", "Review"],
            success_rate=0.92,
            usage_count=45,
            avg_duration_seconds=3600.0
        )
        
        template_id = kg.store_workflow_template(template)
        assert template_id == "wf_001"
        assert len(kg.workflow_templates) == 1
    
    def test_find_workflow_template_by_intent(self):
        """Should find best workflow template for an intent"""
        kg = KnowledgeGraph()
        
        kg.store_workflow_template(WorkflowTemplate(
            "wf_1", "Feature Implementation Workflow", [], 0.85, 30, 3600.0
        ))
        kg.store_workflow_template(WorkflowTemplate(
            "wf_2", "Bug Fix Workflow", [], 0.95, 50, 1800.0
        ))
        
        # Find template for feature intent
        template = kg.find_workflow_template("feature implementation")
        assert template is not None
        assert "feature" in template.name.lower()
    
    def test_workflow_template_with_prerequisites(self):
        """Should store workflow templates with prerequisites"""
        template = WorkflowTemplate(
            template_id="wf_003",
            name="Deploy to Production",
            steps=["Build", "Test", "Deploy"],
            success_rate=0.98,
            usage_count=100,
            avg_duration_seconds=1200.0,
            prerequisites=["tests_passing", "code_reviewed", "staging_validated"]
        )
        
        assert len(template.prerequisites) == 3
        assert "tests_passing" in template.prerequisites


# ============================================================================
# Test: File Relationships
# ============================================================================

class TestFileRelationships:
    """Test file relationship mapping and retrieval"""
    
    def test_store_file_relationship(self):
        """Should store file relationships"""
        kg = KnowledgeGraph()
        
        rel = FileRelationship(
            file_a="src/services/auth.py",
            file_b="tests/test_auth.py",
            relationship_type="tested_by",
            confidence=0.9,
            co_edit_count=15,
            last_co_edited=datetime.now()
        )
        
        kg.store_file_relationship(rel)
        assert len(kg.file_relationships) == 1
    
    def test_update_existing_relationship(self):
        """Should update existing relationship instead of duplicating"""
        kg = KnowledgeGraph()
        
        rel1 = FileRelationship(
            "file_a.py", "file_b.py", "depends_on", 
            0.7, 5, datetime.now()
        )
        kg.store_file_relationship(rel1)
        
        # Store same relationship again
        rel2 = FileRelationship(
            "file_a.py", "file_b.py", "depends_on",
            0.8, 1, datetime.now()
        )
        kg.store_file_relationship(rel2)
        
        # Should only have 1 relationship (updated)
        assert len(kg.file_relationships) == 1
        assert kg.file_relationships[0].confidence > 0.7  # Boosted
        assert kg.file_relationships[0].co_edit_count == 6  # Incremented
    
    def test_get_related_files(self):
        """Should retrieve files related to a given file"""
        kg = KnowledgeGraph()
        
        kg.store_file_relationship(FileRelationship(
            "src/main.py", "src/utils.py", "depends_on", 0.9, 10, datetime.now()
        ))
        kg.store_file_relationship(FileRelationship(
            "src/main.py", "tests/test_main.py", "tested_by", 0.85, 20, datetime.now()
        ))
        kg.store_file_relationship(FileRelationship(
            "src/other.py", "src/utils.py", "depends_on", 0.7, 5, datetime.now()
        ))
        
        # Get all relationships for src/main.py
        related = kg.get_related_files("src/main.py")
        assert len(related) == 2
        
        # Results should be sorted by confidence
        assert related[0].confidence >= related[1].confidence
    
    def test_filter_relationships_by_type(self):
        """Should filter relationships by type"""
        kg = KnowledgeGraph()
        
        kg.store_file_relationship(FileRelationship(
            "file_a.py", "file_b.py", "depends_on", 0.9, 10, datetime.now()
        ))
        kg.store_file_relationship(FileRelationship(
            "file_a.py", "test_a.py", "tested_by", 0.85, 20, datetime.now()
        ))
        
        # Get only "tested_by" relationships
        related = kg.get_related_files("file_a.py", relationship_type="tested_by")
        assert len(related) == 1
        assert related[0].relationship_type == "tested_by"
    
    def test_filter_relationships_by_confidence(self):
        """Should filter relationships by confidence threshold"""
        kg = KnowledgeGraph()
        
        kg.store_file_relationship(FileRelationship(
            "file_a.py", "file_b.py", "depends_on", 0.9, 10, datetime.now()
        ))
        kg.store_file_relationship(FileRelationship(
            "file_a.py", "file_c.py", "depends_on", 0.4, 5, datetime.now()
        ))
        
        # Get only high confidence relationships
        related = kg.get_related_files("file_a.py", min_confidence=0.5)
        assert len(related) == 1
        assert related[0].confidence >= 0.5


# ============================================================================
# Test: Intent Pattern Matching
# ============================================================================

class TestIntentPrediction:
    """Test intent prediction based on learned patterns"""
    
    def test_predict_intent_from_patterns(self):
        """Should predict intent based on learned patterns"""
        kg = KnowledgeGraph()
        
        # Store intent patterns
        kg.store_pattern(Pattern(
            "p1", "intent",
            {'intent': 'PLAN', 'keywords': ['plan', 'design', 'feature']},
            0.9, datetime.now(), datetime.now()
        ))
        kg.store_pattern(Pattern(
            "p2", "intent",
            {'intent': 'EXECUTE', 'keywords': ['implement', 'code', 'build']},
            0.85, datetime.now(), datetime.now()
        ))
        
        # Predict intent
        predictions = kg.predict_intent("help me plan a new feature")
        
        assert len(predictions) > 0
        assert predictions[0]['intent'] == 'PLAN'
        assert predictions[0]['confidence'] > 0.8
    
    def test_intent_prediction_sorted_by_confidence(self):
        """Should return predictions sorted by confidence"""
        kg = KnowledgeGraph()
        
        kg.store_pattern(Pattern(
            "p1", "intent",
            {'intent': 'TEST', 'keywords': ['test', 'validate']},
            0.7, datetime.now(), datetime.now()
        ))
        kg.store_pattern(Pattern(
            "p2", "intent",
            {'intent': 'PLAN', 'keywords': ['plan', 'test']},
            0.9, datetime.now(), datetime.now()
        ))
        
        predictions = kg.predict_intent("help me plan tests")
        
        # Should match both but PLAN has higher confidence
        assert len(predictions) >= 2
        assert predictions[0]['confidence'] >= predictions[1]['confidence']
    
    def test_no_intent_match_returns_empty(self):
        """Should return empty list when no intent matches"""
        kg = KnowledgeGraph()
        
        kg.store_pattern(Pattern(
            "p1", "intent",
            {'intent': 'PLAN', 'keywords': ['plan', 'design']},
            0.9, datetime.now(), datetime.now()
        ))
        
        predictions = kg.predict_intent("show me the weather")
        
        assert len(predictions) == 0


# ============================================================================
# Test: Statistics and Performance
# ============================================================================

class TestKnowledgeGraphStatistics:
    """Test statistics and performance metrics"""
    
    def test_get_statistics(self):
        """Should return comprehensive statistics"""
        kg = KnowledgeGraph()
        
        # Populate graph
        kg.store_pattern(Pattern("p1", "intent", {}, 0.9, datetime.now(), datetime.now()))
        kg.store_pattern(Pattern("p2", "workflow", {}, 0.8, datetime.now(), datetime.now()))
        kg.store_workflow_template(WorkflowTemplate("wf1", "Test", [], 0.9, 10, 100.0))
        kg.store_file_relationship(FileRelationship("a", "b", "depends_on", 0.9, 5, datetime.now()))
        
        stats = kg.get_statistics()
        
        assert stats['total_patterns'] == 2
        assert stats['total_workflow_templates'] == 1
        assert stats['total_file_relationships'] == 1
        assert 'avg_confidence' in stats
        assert 'patterns_by_type' in stats
    
    def test_patterns_by_type_count(self):
        """Should count patterns by type correctly"""
        kg = KnowledgeGraph()
        
        kg.store_pattern(Pattern("p1", "intent", {}, 0.9, datetime.now(), datetime.now()))
        kg.store_pattern(Pattern("p2", "intent", {}, 0.8, datetime.now(), datetime.now()))
        kg.store_pattern(Pattern("p3", "workflow", {}, 0.7, datetime.now(), datetime.now()))
        
        stats = kg.get_statistics()
        
        assert stats['patterns_by_type']['intent'] == 2
        assert stats['patterns_by_type']['workflow'] == 1
    
    def test_performance_retrieval_speed(self):
        """Should retrieve patterns quickly (<50ms for 100 patterns)"""
        import time
        
        kg = KnowledgeGraph()
        
        # Store 100 patterns
        for i in range(100):
            kg.store_pattern(Pattern(
                f"p{i:03d}", "intent", {}, 0.8, datetime.now(), datetime.now()
            ))
        
        # Measure retrieval time
        start = time.time()
        for i in range(100):
            kg.retrieve_pattern(f"p{i:03d}")
        end = time.time()
        
        avg_time_ms = ((end - start) / 100) * 1000
        assert avg_time_ms < 50  # Should be fast


# ============================================================================
# Test: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_retrieve_nonexistent_pattern(self):
        """Should return None for nonexistent pattern"""
        kg = KnowledgeGraph()
        
        result = kg.retrieve_pattern("does_not_exist")
        
        assert result is None
    
    def test_empty_graph_statistics(self):
        """Should handle statistics on empty graph"""
        kg = KnowledgeGraph()
        
        stats = kg.get_statistics()
        
        assert stats['total_patterns'] == 0
        assert stats['avg_confidence'] == 0.0
    
    def test_search_patterns_empty_graph(self):
        """Should return empty list when searching empty graph"""
        kg = KnowledgeGraph()
        
        results = kg.search_patterns(pattern_type="intent")
        
        assert len(results) == 0
    
    def test_get_related_files_no_relationships(self):
        """Should return empty list when no relationships exist"""
        kg = KnowledgeGraph()
        
        related = kg.get_related_files("nonexistent_file.py")
        
        assert len(related) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
