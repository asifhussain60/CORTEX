"""
Tests for Domain Pattern Analyzer

Validates domain clustering, aggregate detection, and pattern recognition.

Author: CORTEX Architect
Phase: Phase 66 S3
"""

import pytest
from pathlib import Path
from typing import List, Dict, Any


class TestPatternAnalyzer:
    """Test suite for domain pattern analysis"""
    
    def test_domain_clustering_by_prefix(self):
        """Test clustering classes by shared naming prefixes"""
        from cortex_lens.domain_inference.pattern_analyzer import PatternAnalyzer
        
        # Mock AST nodes representing classes
        class_names = [
            "UserRepository",
            "UserService",
            "UserValidator",
            "OrderRepository",
            "OrderService",
            "PaymentProcessor",
            "PaymentValidator"
        ]
        
        analyzer = PatternAnalyzer()
        clusters = analyzer.cluster_by_prefix(class_names, min_cluster_size=2)
        
        assert "User" in clusters
        assert len(clusters["User"]) == 3
        assert "UserRepository" in clusters["User"]
        
        assert "Order" in clusters
        assert len(clusters["Order"]) == 2
        
        assert "Payment" in clusters
        assert len(clusters["Payment"]) == 2
    
    def test_aggregate_root_detection(self):
        """Test identifying aggregate roots in domain clusters"""
        from cortex_lens.domain_inference.pattern_analyzer import PatternAnalyzer
        
        # Mock domain cluster with typical DDD patterns
        user_cluster = {
            "UserRepository": {"type": "repository", "methods": ["save", "find"]},
            "UserService": {"type": "service", "methods": ["create_user", "update_user"]},
            "UserValidator": {"type": "validator", "methods": ["validate_email"]},
            "User": {"type": "entity", "methods": ["__init__", "update_email"]}
        }
        
        analyzer = PatternAnalyzer()
        aggregate_root = analyzer.detect_aggregate_root(user_cluster)
        
        assert aggregate_root == "User"  # Entity class is typically the root
    
    def test_repository_pattern_detection(self):
        """Test detecting repository pattern in codebase"""
        from cortex_lens.domain_inference.pattern_analyzer import PatternAnalyzer
        
        # Mock class definitions
        classes = [
            {
                "name": "UserRepository",
                "methods": ["save", "find_by_id", "delete"],
                "bases": ["BaseRepository"]
            },
            {
                "name": "OrderRepository",
                "methods": ["save", "find_all", "find_by_status"],
                "bases": []
            }
        ]
        
        analyzer = PatternAnalyzer()
        repositories = analyzer.detect_pattern("repository", classes)
        
        assert len(repositories) == 2
        assert "UserRepository" in [r["name"] for r in repositories]
        assert "OrderRepository" in [r["name"] for r in repositories]
    
    def test_service_pattern_detection(self):
        """Test detecting service layer pattern"""
        from cortex_lens.domain_inference.pattern_analyzer import PatternAnalyzer
        
        classes = [
            {
                "name": "UserService",
                "methods": ["create_user", "authenticate", "update_profile"],
                "bases": []
            },
            {
                "name": "OrderService",
                "methods": ["place_order", "cancel_order", "get_order_history"],
                "bases": ["BaseService"]
            }
        ]
        
        analyzer = PatternAnalyzer()
        services = analyzer.detect_pattern("service", classes)
        
        assert len(services) == 2
        assert all("Service" in s["name"] for s in services)
    
    def test_domain_boundary_detection(self):
        """Test identifying bounded context boundaries"""
        from cortex_lens.domain_inference.pattern_analyzer import PatternAnalyzer
        
        # Mock module structure
        modules = {
            "user": ["UserRepository", "UserService", "UserValidator"],
            "order": ["OrderRepository", "OrderService", "OrderValidator"],
            "payment": ["PaymentProcessor", "PaymentValidator"],
            "shared": ["BaseRepository", "ValidationError"]
        }
        
        analyzer = PatternAnalyzer()
        contexts = analyzer.detect_bounded_contexts(modules)
        
        assert len(contexts) >= 3
        assert "user" in [c["name"] for c in contexts]
        assert "order" in [c["name"] for c in contexts]
        assert "shared" not in [c["name"] for c in contexts]  # Shared kernel excluded
    
    def test_naming_convention_analysis(self):
        """Test analyzing naming conventions in domain"""
        from cortex_lens.domain_inference.pattern_analyzer import PatternAnalyzer
        
        class_names = [
            "UserRepository",
            "UserService",
            "UserValidator",
            "user_factory",  # snake_case
            "USER_CONST"     # SCREAMING_CASE
        ]
        
        analyzer = PatternAnalyzer()
        conventions = analyzer.analyze_naming_conventions(class_names)
        
        assert conventions["primary_style"] == "PascalCase"
        assert conventions["consistency_score"] >= 0.6  # 3/5 follow PascalCase
    
    def test_dependency_coupling_analysis(self):
        """Test analyzing coupling between domain clusters"""
        from cortex_lens.domain_inference.pattern_analyzer import PatternAnalyzer
        
        # Mock import relationships
        imports = {
            "UserService": ["UserRepository", "UserValidator"],
            "OrderService": ["OrderRepository", "UserService"],  # Cross-domain
            "PaymentService": ["OrderService", "PaymentValidator"]
        }
        
        analyzer = PatternAnalyzer()
        coupling = analyzer.analyze_coupling(imports, clusters={
            "User": ["UserRepository", "UserService", "UserValidator"],
            "Order": ["OrderRepository", "OrderService"],
            "Payment": ["PaymentService", "PaymentValidator"]
        })
        
        # Should detect cross-domain dependency: Order → User
        cross_domain_deps = coupling["cross_domain"]
        assert len(cross_domain_deps) >= 1
        assert any(d["from"] == "Order" and d["to"] == "User" for d in cross_domain_deps)
    
    def test_confidence_scoring(self):
        """Test confidence scoring for domain inferences"""
        from cortex_lens.domain_inference.pattern_analyzer import PatternAnalyzer
        
        # Strong signals: prefix match + repository + service
        strong_cluster = {
            "prefix_match_count": 4,
            "has_repository": True,
            "has_service": True,
            "has_validator": True,
            "naming_consistency": 0.9
        }
        
        analyzer = PatternAnalyzer()
        confidence = analyzer.calculate_confidence(strong_cluster)
        
        assert confidence >= 0.8  # High confidence
        
        # Weak signals: only 2 classes, no patterns
        weak_cluster = {
            "prefix_match_count": 2,
            "has_repository": False,
            "has_service": False,
            "has_validator": False,
            "naming_consistency": 0.5
        }
        
        confidence_weak = analyzer.calculate_confidence(weak_cluster)
        assert confidence_weak < 0.5  # Low confidence
    
    def test_cortex_domain_detection(self):
        """Test detecting actual CORTEX domains from codebase"""
        from cortex_lens.domain_inference.pattern_analyzer import PatternAnalyzer
        from pathlib import Path
        
        analyzer = PatternAnalyzer()
        
        # Analyze cortex/ directory
        cortex_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex")
        if cortex_path.exists():
            domains = analyzer.analyze_directory(cortex_path)
            
            # CORTEX should have identifiable domains
            domain_names = [d["name"] for d in domains]
            
            # Check for known CORTEX domains
            expected_domains = ["orchestrator", "lens", "governance", "mcp"]
            found_domains = [d for d in expected_domains if any(d in name.lower() for name in domain_names)]
            
            assert len(found_domains) >= 2, f"Expected CORTEX domains, found: {domain_names}"
    
    def test_pattern_confidence_validation(self):
        """Test that confidence scores are properly validated"""
        from cortex_lens.domain_inference.pattern_analyzer import PatternAnalyzer
        
        analyzer = PatternAnalyzer()
        
        # Confidence must be in [0.0, 1.0]
        valid_cluster = {"prefix_match_count": 3, "has_repository": True}
        confidence = analyzer.calculate_confidence(valid_cluster)
        
        assert 0.0 <= confidence <= 1.0, f"Confidence {confidence} out of range"


class TestDomainClusteringIntegration:
    """Integration tests for domain clustering with knowledge graph"""
    
    def test_clustering_with_graph_data(self):
        """Test clustering using real graph node data"""
        from cortex_lens.domain_inference.pattern_analyzer import PatternAnalyzer
        from cortex_lens.knowledge_graph.graph_storage import GraphStorage
        import tempfile
        
        # Create temporary graph
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = Path(tmp.name)
        
        storage = GraphStorage(db_path)
        storage.initialize_schema()
        
        # Insert domain classes
        user_repo_id = storage.insert_node("Class", "UserRepository", {"domain": "user"})
        user_svc_id = storage.insert_node("Class", "UserService", {"domain": "user"})
        order_repo_id = storage.insert_node("Class", "OrderRepository", {"domain": "order"})
        
        # Analyze graph nodes
        analyzer = PatternAnalyzer()
        nodes = storage.query_nodes_by_type("Class")
        clusters = analyzer.cluster_by_prefix([n["name"] for n in nodes], min_cluster_size=2)
        
        assert "User" in clusters
        assert len(clusters["User"]) == 2
        
        # Cleanup
        db_path.unlink()
