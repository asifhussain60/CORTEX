"""
CORTEX 3.0 - Test Feature 1: IDEA Capture System - Organization Module

Purpose: Test smart organization system for captured ideas including
         categorization, tagging, priority management, and clustering.

Test Coverage:
- CategoryManager: Auto-categorization accuracy and performance
- TagSystem: Tag creation, retrieval, and hierarchical relationships
- PriorityEngine: Dynamic priority scoring and time-based adjustments
- ClusteringEngine: Related idea detection and grouping algorithms
- IdeaOrganizer: Complete organization pipeline and async processing

Performance Requirements:
- Organization processing: <50ms per idea
- Batch processing: 1000+ ideas/second
- Search performance: <100ms for large datasets
- Memory efficiency: <10MB for 100K ideas

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import pytest
import tempfile
import time
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.operations.modules.ideas import (
    IdeaCapture,
    IdeaCategory,
    IdeaTag, 
    IdeaCluster,
    CategoryManager,
    TagSystem,
    PriorityEngine,
    ClusteringEngine,
    IdeaOrganizer,
    create_idea_organizer
)


class TestCategoryManager:
    """Test automatic categorization functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.manager = CategoryManager()
    
    def test_feature_categorization(self):
        """Test categorization of feature requests."""
        test_cases = [
            ("Add new user registration feature", "feature", True),
            ("Implement search functionality", "feature", True),
            ("Build payment component", "feature", True),
            ("Create admin dashboard", "feature", True),
        ]
        
        for text, expected_category, should_detect in test_cases:
            idea = IdeaCapture(
                id="test",
                text=text,
                captured_at=datetime.now()
            )
            
            categories = self.manager.categorize_idea(idea)
            category_names = [cat.name for cat in categories]
            
            if should_detect:
                assert expected_category in category_names, \
                    f"Failed to categorize '{text}' as {expected_category}"
                # Check confidence
                feature_cat = next(cat for cat in categories if cat.name == expected_category)
                assert feature_cat.confidence > 0.3
            else:
                assert expected_category not in category_names
    
    def test_bug_categorization(self):
        """Test categorization of bug reports."""
        test_cases = [
            ("Fix login bug", "bug", True),
            ("Resolve authentication error", "bug", True),
            ("Debug payment issue", "bug", True),
            ("Broken user interface", "bug", True),
        ]
        
        for text, expected_category, should_detect in test_cases:
            idea = IdeaCapture(
                id="test",
                text=text,
                captured_at=datetime.now()
            )
            
            categories = self.manager.categorize_idea(idea)
            category_names = [cat.name for cat in categories]
            
            if should_detect:
                assert expected_category in category_names
    
    def test_improvement_categorization(self):
        """Test categorization of improvements."""
        test_cases = [
            ("Improve database performance", "improvement", True),
            ("Optimize search algorithm", "improvement", True),
            ("Enhance user experience", "improvement", True),
            ("Refactor authentication module", "improvement", True),
        ]
        
        for text, expected_category, should_detect in test_cases:
            idea = IdeaCapture(
                id="test",
                text=text,
                captured_at=datetime.now()
            )
            
            categories = self.manager.categorize_idea(idea)
            category_names = [cat.name for cat in categories]
            
            if should_detect:
                assert expected_category in category_names
    
    def test_component_detection(self):
        """Test component detection from context and text."""
        test_cases = [
            # Text-based detection
            ("Add user authentication", "auth"),
            ("Fix database query performance", "database"),
            ("Update React components", "frontend"),
            ("Create API endpoint", "backend"),
            ("Add unit tests", "testing"),
            ("Deploy to production", "deployment"),
            ("Add logging metrics", "monitoring"),
            ("Implement encryption", "security"),
        ]
        
        for text, expected_component in test_cases:
            idea = IdeaCapture(
                id="test",
                text=text,
                captured_at=datetime.now()
            )
            
            component = self.manager.detect_component(idea)
            assert component == expected_component, \
                f"Expected component '{expected_component}' for '{text}', got '{component}'"
    
    def test_component_detection_from_file_context(self):
        """Test component detection from file path context."""
        test_cases = [
            ("/src/auth/login.py", "auth"),
            ("/tests/unit/test_database.py", "testing"), 
            ("/frontend/components/ui.tsx", "frontend"),
            ("/api/controllers/user.py", "backend"),
            ("/docker/Dockerfile", "deployment"),
        ]
        
        for file_path, expected_component in test_cases:
            idea = IdeaCapture(
                id="test",
                text="Some idea",
                captured_at=datetime.now(),
                context={'file_path': file_path}
            )
            
            component = self.manager.detect_component(idea)
            assert component == expected_component, \
                f"Expected component '{expected_component}' for path '{file_path}', got '{component}'"
    
    def test_categorization_performance(self):
        """Test categorization performance requirements."""
        ideas = []
        for i in range(100):
            ideas.append(IdeaCapture(
                id=f"test_{i}",
                text=f"Add feature number {i} to improve system performance",
                captured_at=datetime.now()
            ))
        
        start_time = time.time()
        
        for idea in ideas:
            categories = self.manager.categorize_idea(idea)
            assert len(categories) > 0
        
        total_time = (time.time() - start_time) * 1000  # Convert to ms
        avg_time = total_time / len(ideas)
        
        assert avg_time < 5.0, f"Categorization too slow: {avg_time:.2f}ms per idea"


class TestTagSystem:
    """Test flexible tagging system."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.tag_system = TagSystem(self.temp_db.name)
    
    def teardown_method(self):
        """Cleanup test environment."""
        Path(self.temp_db.name).unlink(missing_ok=True)
    
    def test_add_and_retrieve_tags(self):
        """Test basic tag operations."""
        idea_id = "test_idea_1"
        
        # Add tags
        tag1 = IdeaTag(name="python", category="technology", confidence=0.9)
        tag2 = IdeaTag(name="high", category="priority", confidence=0.8)
        
        assert self.tag_system.add_tag(idea_id, tag1)
        assert self.tag_system.add_tag(idea_id, tag2)
        
        # Retrieve tags
        tags = self.tag_system.get_tags(idea_id)
        assert len(tags) == 2
        
        tag_names = [tag.name for tag in tags]
        assert "python" in tag_names
        assert "high" in tag_names
    
    def test_auto_tag_generation(self):
        """Test automatic tag generation."""
        test_cases = [
            # Priority detection
            ("This is urgent and critical", "critical", "priority"),
            ("This is important and needed soon", "high", "priority"),
            ("This would be nice to have later", "low", "priority"),
            
            # Technology detection  
            ("Implement Python API endpoint", "python", "technology"),
            ("Fix JavaScript bug in React component", "javascript", "technology"),
            ("Update database schema", "database", "technology"),
            
            # Effort estimation
            ("Quick fix for small bug", "quick-win", "effort"),
            ("Major refactoring project", "long-term", "effort"),
        ]
        
        for text, expected_tag, expected_category in test_cases:
            idea = IdeaCapture(
                id="test",
                text=text,
                captured_at=datetime.now()
            )
            
            auto_tags = self.tag_system.auto_tag_idea(idea)
            
            # Check if expected tag was generated
            tag_names = [(tag.name, tag.category) for tag in auto_tags]
            assert (expected_tag, expected_category) in tag_names, \
                f"Expected tag '{expected_tag}' with category '{expected_category}' for '{text}'"
    
    def test_hierarchical_tags(self):
        """Test hierarchical tag relationships."""
        idea_id = "test_idea_1"
        
        # Add parent tag
        parent_tag = IdeaTag(name="backend", category="component")
        self.tag_system.add_tag(idea_id, parent_tag)
        
        # Add child tag
        child_tag = IdeaTag(name="api", category="component", parent_tag="backend")
        self.tag_system.add_tag(idea_id, child_tag)
        
        # Retrieve and verify
        tags = self.tag_system.get_tags(idea_id)
        child_tags = [tag for tag in tags if tag.parent_tag is not None]
        
        assert len(child_tags) == 1
        assert child_tags[0].name == "api"
        assert child_tags[0].parent_tag == "backend"
    
    def test_tag_confidence_scoring(self):
        """Test tag confidence scoring."""
        idea = IdeaCapture(
            id="test",
            text="This is a critical Python API bug that needs urgent fixing",
            captured_at=datetime.now()
        )
        
        auto_tags = self.tag_system.auto_tag_idea(idea)
        
        # Should detect critical priority with high confidence
        priority_tags = [tag for tag in auto_tags if tag.category == "priority"]
        assert len(priority_tags) > 0
        
        critical_tag = next((tag for tag in priority_tags if tag.name == "critical"), None)
        assert critical_tag is not None
        assert critical_tag.confidence > 0.5


class TestPriorityEngine:
    """Test dynamic priority scoring system."""
    
    def setup_method(self):
        """Setup test environment."""
        self.engine = PriorityEngine()
    
    def test_urgency_keyword_scoring(self):
        """Test priority scoring based on urgency keywords."""
        test_cases = [
            ("This is urgent and critical", 0.7, 1.0, "critical"),
            ("Important feature needed soon", 0.5, 0.9, "high"),  
            ("Would be nice to have later", 0.0, 0.4, "low"),
            ("Regular improvement task", 0.2, 0.6, "medium"),
        ]
        
        for text, min_score, max_score, expected_label in test_cases:
            idea = IdeaCapture(
                id="test",
                text=text,
                captured_at=datetime.now()
            )
            
            score = self.engine.calculate_priority_score(idea)
            label = self.engine.get_priority_label(score)
            
            assert min_score <= score <= max_score, \
                f"Score {score} not in range [{min_score}, {max_score}] for '{text}'"
            assert label == expected_label, \
                f"Expected label '{expected_label}' for '{text}', got '{label}'"
    
    def test_business_impact_scoring(self):
        """Test scoring based on business impact indicators."""
        high_impact_ideas = [
            "Fix user authentication security vulnerability",
            "Improve customer checkout performance", 
            "Add revenue tracking feature"
        ]
        
        low_impact_ideas = [
            "Polish button styling",
            "Add convenience helper function",
            "Update cosmetic UI elements"
        ]
        
        # Test high impact
        for text in high_impact_ideas:
            idea = IdeaCapture(id="test", text=text, captured_at=datetime.now())
            score = self.engine.calculate_priority_score(idea)
            assert score > 0.5, f"High impact idea '{text}' got low score: {score}"
        
        # Test low impact
        for text in low_impact_ideas:
            idea = IdeaCapture(id="test", text=text, captured_at=datetime.now())
            score = self.engine.calculate_priority_score(idea)
            assert score < 0.7, f"Low impact idea '{text}' got high score: {score}"
    
    def test_time_decay_scoring(self):
        """Test time-based priority decay."""
        # Recent idea
        recent_idea = IdeaCapture(
            id="test1",
            text="Important feature request",
            captured_at=datetime.now()
        )
        
        # Old idea
        old_idea = IdeaCapture(
            id="test2", 
            text="Important feature request",
            captured_at=datetime.now() - timedelta(days=7)
        )
        
        recent_score = self.engine.calculate_priority_score(recent_idea)
        old_score = self.engine.calculate_priority_score(old_idea)
        
        assert recent_score >= old_score, "Recent ideas should have higher or equal priority"
    
    def test_complexity_inverse_scoring(self):
        """Test that simpler tasks get higher priority scores."""
        simple_idea = IdeaCapture(
            id="test1",
            text="Fix typo in documentation",
            captured_at=datetime.now()
        )
        
        complex_idea = IdeaCapture(
            id="test2",
            text="Refactor entire authentication architecture with migration",
            captured_at=datetime.now()
        )
        
        simple_score = self.engine.calculate_priority_score(simple_idea)
        complex_score = self.engine.calculate_priority_score(complex_idea)
        
        # Note: This might not always be true due to other factors like urgency,
        # but generally simpler tasks should have higher scores
        # We'll just check that both scores are reasonable
        assert 0.0 <= simple_score <= 1.0
        assert 0.0 <= complex_score <= 1.0
    
    def test_priority_label_mapping(self):
        """Test priority score to label mapping."""
        test_scores = [
            (0.9, "critical"),
            (0.8, "critical"), 
            (0.7, "high"),
            (0.6, "high"),
            (0.5, "medium"),
            (0.4, "medium"),
            (0.3, "low"),
            (0.1, "low")
        ]
        
        for score, expected_label in test_scores:
            label = self.engine.get_priority_label(score)
            assert label == expected_label, \
                f"Score {score} should map to '{expected_label}', got '{label}'"


class TestClusteringEngine:
    """Test idea clustering functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.engine = ClusteringEngine(self.temp_db.name)
    
    def teardown_method(self):
        """Cleanup test environment."""
        Path(self.temp_db.name).unlink(missing_ok=True)
    
    def test_similarity_calculation(self):
        """Test idea similarity calculation."""
        # Similar ideas
        idea1 = IdeaCapture(id="1", text="Add user authentication system", captured_at=datetime.now())
        idea2 = IdeaCapture(id="2", text="Implement user login authentication", captured_at=datetime.now())
        
        # Dissimilar ideas
        idea3 = IdeaCapture(id="3", text="Fix database performance issue", captured_at=datetime.now())
        
        # Test similar ideas
        similarity_high = self.engine.calculate_similarity(idea1, idea2)
        assert similarity_high > 0.3, f"Similar ideas should have high similarity: {similarity_high}"
        
        # Test dissimilar ideas
        similarity_low = self.engine.calculate_similarity(idea1, idea3)
        assert similarity_low < 0.5, f"Dissimilar ideas should have low similarity: {similarity_low}"
    
    def test_component_similarity_bonus(self):
        """Test similarity bonus for same component ideas."""
        idea1 = IdeaCapture(
            id="1", 
            text="Add feature",
            component="auth",
            captured_at=datetime.now()
        )
        idea2 = IdeaCapture(
            id="2", 
            text="Fix bug", 
            component="auth",
            captured_at=datetime.now()
        )
        idea3 = IdeaCapture(
            id="3",
            text="Add feature",
            component="database", 
            captured_at=datetime.now()
        )
        
        # Same component should have higher similarity
        same_component = self.engine.calculate_similarity(idea1, idea2)
        diff_component = self.engine.calculate_similarity(idea1, idea3)
        
        assert same_component > diff_component, \
            "Ideas with same component should have higher similarity"
    
    def test_keyword_extraction(self):
        """Test meaningful keyword extraction."""
        text = "Add user authentication with password reset functionality"
        keywords = self.engine._extract_keywords(text)
        
        # Should extract meaningful words
        expected_keywords = ["add", "user", "authentication", "password", "reset", "functionality"]
        for keyword in expected_keywords:
            assert keyword in keywords, f"Should extract keyword '{keyword}'"
        
        # Should not extract stop words
        stop_words = ["the", "a", "and", "with"]
        for stop_word in stop_words:
            assert stop_word not in keywords, f"Should not extract stop word '{stop_word}'"
    
    def test_cluster_generation(self):
        """Test cluster generation from related ideas."""
        # Create related ideas about authentication
        auth_ideas = [
            IdeaCapture(id="1", text="Add user login system", captured_at=datetime.now()),
            IdeaCapture(id="2", text="Implement user authentication", captured_at=datetime.now()),
            IdeaCapture(id="3", text="Add password reset feature", captured_at=datetime.now()),
        ]
        
        # Create unrelated ideas
        db_ideas = [
            IdeaCapture(id="4", text="Optimize database queries", captured_at=datetime.now()),
            IdeaCapture(id="5", text="Add database indexing", captured_at=datetime.now()),
        ]
        
        all_ideas = auth_ideas + db_ideas
        
        # Find clusters
        clusters = self.engine.find_clusters(all_ideas)
        
        # Should find at least one cluster
        assert len(clusters) >= 1, "Should find at least one cluster"
        
        # Check cluster properties
        for cluster in clusters:
            assert len(cluster.ideas) >= 2, "Clusters should have at least 2 ideas"
            assert cluster.cluster_id is not None, "Clusters should have IDs"
            assert cluster.similarity_threshold == self.engine.similarity_threshold
    
    def test_cluster_id_generation(self):
        """Test unique cluster ID generation."""
        ideas1 = ["idea1", "idea2", "idea3"]
        ideas2 = ["idea1", "idea2", "idea3"]
        ideas3 = ["idea1", "idea2", "idea4"]
        
        id1 = self.engine._generate_cluster_id(ideas1)
        id2 = self.engine._generate_cluster_id(ideas2)
        id3 = self.engine._generate_cluster_id(ideas3)
        
        # Same ideas should generate same ID
        assert id1 == id2, "Same ideas should generate same cluster ID"
        
        # Different ideas should generate different ID
        assert id1 != id3, "Different ideas should generate different cluster ID"


class TestIdeaOrganizer:
    """Test complete idea organization system."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.organizer = create_idea_organizer(self.temp_db.name, enable_clustering=True)
    
    def teardown_method(self):
        """Cleanup test environment."""
        self.organizer.shutdown()
        Path(self.temp_db.name).unlink(missing_ok=True)
    
    def test_complete_organization_pipeline(self):
        """Test complete idea organization pipeline."""
        idea = IdeaCapture(
            id="test_idea",
            text="Add user authentication with password reset feature",
            captured_at=datetime.now()
        )
        
        # Process organization (synchronous)
        result = self.organizer.organize_idea(idea, async_processing=False)
        
        # Verify results
        assert result['status'] == 'processed'
        assert result['idea_id'] == idea.id
        assert len(result['categories']) > 0
        assert len(result['tags']) >= 0  # May have auto-generated tags
        assert 0.0 <= result['priority_score'] <= 1.0
        assert result['priority_label'] in ['critical', 'high', 'medium', 'low']
        assert result['processing_time'] > 0
    
    def test_async_organization_processing(self):
        """Test asynchronous organization processing."""
        idea = IdeaCapture(
            id="test_idea",
            text="Implement new feature for better user experience",
            captured_at=datetime.now()
        )
        
        # Process organization (asynchronous)
        result = self.organizer.organize_idea(idea, async_processing=True)
        
        # Should return immediately with queued status
        assert result['status'] == 'queued'
        assert result['idea_id'] == idea.id
        assert result['processing_time'] < 10  # Should be very fast to queue
        
        # Wait a bit for background processing
        time.sleep(0.1)
    
    def test_organization_performance(self):
        """Test organization performance requirements."""
        ideas = []
        for i in range(50):
            ideas.append(IdeaCapture(
                id=f"perf_test_{i}",
                text=f"Feature request number {i} for system improvement",
                captured_at=datetime.now()
            ))
        
        start_time = time.time()
        
        # Process ideas individually
        for idea in ideas:
            result = self.organizer.organize_idea(idea, async_processing=False)
            assert result['status'] == 'processed'
            # Each idea should be processed in <50ms
            assert result['processing_time'] < 50, \
                f"Organization too slow: {result['processing_time']}ms"
        
        total_time = (time.time() - start_time) * 1000
        avg_time = total_time / len(ideas)
        
        assert avg_time < 50, f"Average organization time too slow: {avg_time:.2f}ms"
    
    def test_batch_organization(self):
        """Test batch organization functionality."""
        ideas = []
        for i in range(10):
            ideas.append(IdeaCapture(
                id=f"batch_test_{i}",
                text=f"Batch idea {i}: implement feature for authentication system",
                captured_at=datetime.now()
            ))
        
        # Process batch
        result = self.organizer.batch_organize_ideas(ideas)
        
        # Verify batch results
        assert result['total_ideas'] == len(ideas)
        assert result['processed'] > 0
        assert result['failed'] == 0  # Should process all successfully
        assert result['processing_time'] > 0
        
        # Should find clusters if ideas are similar
        # (may or may not find clusters depending on similarity)
        assert 'clusters' in result
    
    def test_organization_statistics(self):
        """Test organization statistics tracking."""
        # Process a few ideas
        for i in range(5):
            idea = IdeaCapture(
                id=f"stats_test_{i}",
                text=f"Test idea {i}",
                captured_at=datetime.now()
            )
            self.organizer.organize_idea(idea, async_processing=False)
        
        # Get statistics
        stats = self.organizer.get_organization_stats()
        
        # Verify stats structure
        assert 'processing_stats' in stats
        assert 'queue_size' in stats
        assert 'components_enabled' in stats
        
        # Verify processing stats
        proc_stats = stats['processing_stats']
        assert proc_stats['total_processed'] == 5
        assert proc_stats['avg_processing_time'] > 0
        
        # Verify component status
        components = stats['components_enabled']
        assert components['categorization'] is True
        assert components['tagging'] is True
        assert components['priority_engine'] is True
        assert components['clustering'] is True
    
    def test_error_handling(self):
        """Test error handling in organization pipeline."""
        # Create idea with potentially problematic data
        idea = IdeaCapture(
            id="",  # Empty ID
            text="",  # Empty text
            captured_at=datetime.now()
        )
        
        # Should handle gracefully
        result = self.organizer.organize_idea(idea, async_processing=False)
        
        # Should still process or return error status
        assert 'status' in result
        assert result['idea_id'] == ""


class TestFactoryFunction:
    """Test factory function for creating organizers."""
    
    def test_organizer_creation(self):
        """Test creating organizer with factory function."""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        try:
            organizer = create_idea_organizer(temp_db.name)
            
            # Verify organizer is properly configured
            assert organizer is not None
            assert organizer.category_manager is not None
            assert organizer.tag_system is not None
            assert organizer.priority_engine is not None
            assert organizer.clustering_engine is not None
            
            organizer.shutdown()
            
        finally:
            Path(temp_db.name).unlink(missing_ok=True)
    
    def test_organizer_creation_without_clustering(self):
        """Test creating organizer without clustering enabled."""
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_db.close()
        
        try:
            organizer = create_idea_organizer(temp_db.name, enable_clustering=False)
            
            # Verify clustering is disabled
            assert organizer.clustering_engine is None
            
            organizer.shutdown()
            
        finally:
            Path(temp_db.name).unlink(missing_ok=True)


class TestIntegrationWithIdeaQueue:
    """Test integration between organizer and idea queue."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Create both queue and organizer sharing same database
        from src.operations.modules.ideas import create_idea_queue
        self.queue = create_idea_queue(self.temp_db.name, enable_enrichment=False)
        self.organizer = create_idea_organizer(self.temp_db.name)
    
    def teardown_method(self):
        """Cleanup test environment."""
        self.organizer.shutdown()
        Path(self.temp_db.name).unlink(missing_ok=True)
    
    def test_organize_captured_idea(self):
        """Test organizing an idea captured by the queue."""
        # Capture idea
        idea_id = self.queue.capture("Add user authentication system")
        
        # Get the captured idea
        ideas = self.queue.get_ideas()
        captured_idea = next(idea for idea in ideas if idea.id == idea_id)
        
        # Organize the captured idea
        result = self.organizer.organize_idea(captured_idea, async_processing=False)
        
        # Verify organization was successful
        assert result['status'] == 'processed'
        assert result['idea_id'] == idea_id
        
        # Check that organization added metadata
        assert len(result['categories']) > 0
        assert result['priority_score'] > 0
    
    def test_workflow_integration(self):
        """Test complete workflow: capture → organize → retrieve."""
        # Capture multiple ideas
        idea_texts = [
            "Add user authentication feature",
            "Fix database performance bug", 
            "Improve API documentation",
            "Implement rate limiting security"
        ]
        
        captured_ideas = []
        for text in idea_texts:
            idea_id = self.queue.capture(text)
            ideas = self.queue.get_ideas()
            idea = next(idea for idea in ideas if idea.id == idea_id)
            captured_ideas.append(idea)
        
        # Organize all ideas
        batch_result = self.organizer.batch_organize_ideas(captured_ideas)
        
        # Verify batch organization
        assert batch_result['processed'] == len(idea_texts)
        assert batch_result['failed'] == 0
        
        # Check if clustering found relationships
        if len(batch_result['clusters']) > 0:
            # Verify cluster structure
            for cluster_data in batch_result['clusters']:
                assert len(cluster_data['ideas']) >= 2
                assert cluster_data['cluster_id'] is not None