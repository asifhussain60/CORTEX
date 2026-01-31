"""
Phase 8 Test Suite: Comprehensive Tests for Intelligent Routing & Edge Case Detection

Tests all Phase 8 components:
- Semantic Ranking Engine
- Disambiguation UI
- NLP Enhancement (Embedding Cache, Synonym Expansion, A/B Testing)
- Microsoft Stack Analyzers (C#, SQL, Angular)
- Unified Edge Case Detector
- Routing Health Checks

AC-ID: AC-PHASE-8-TESTS
CORE-008: TDD - Tests for all Phase 8 components

Author: Asif Hussain
Created: 2026-01-30
"""

import pytest
from pathlib import Path
from cortex.orchestrators.core.semantic_ranking import SemanticRankingEngine, RankedCandidate
from cortex.orchestrators.core.disambiguation_ui import DisambiguationUI, DisambiguationResult
from cortex.orchestrators.core.intent_router import IntentType
from cortex.brain.nlp.embedding_cache import EmbeddingCache
from cortex.brain.nlp.synonym_expansion_service import SynonymExpansionService
from cortex.brain.nlp.ab_testing_framework import ABTestingFramework, Variant
from cortex.brain.analysis.csharp_analyzer import CSharpASTAnalyzer
from cortex.brain.analysis.sql_oracle_analyzer import SQLOracleAnalyzer
from cortex.brain.analysis.angular_typescript_analyzer import AngularTypeScriptAnalyzer
from cortex.brain.analysis.unified_edge_case_detector import (
    UnifiedEdgeCaseDetector,
    EdgeCaseSeverity,
)
from cortex.testing.routing_health_checks import RoutingHealthChecker


# ============================================================================
# PHASE 8.3: SEMANTIC RANKING TESTS
# ============================================================================

class TestSemanticRankingEngine:
    """Tests for SemanticRankingEngine."""
    
    def test_initialization(self):
        """Test engine initialization."""
        engine = SemanticRankingEngine()
        assert engine is not None
        assert len(engine.synonym_groups) > 0
    
    def test_synonym_matching(self):
        """Test synonym expansion and matching."""
        from cortex.wiring import get_registry
        engine = SemanticRankingEngine()
        registry = get_registry()
        
        # Get actual orchestrator instances
        orchestrators = registry.list_orchestrators()
        if not orchestrators or len(orchestrators) < 2:
            pytest.skip("Not enough orchestrators available in registry")
        
        # Pick first two orchestrators
        candidates = [
            (name, registry.resolve_orchestrator(name), 0.5)
            for name in orchestrators[:2]
        ]
        
        context = {"keywords": ["create"]}  # Synonym of implement
        
        ranked = engine.rank_candidates(candidates, context, IntentType.IMPLEMENT)
        assert len(ranked) > 0
        assert ranked[0].total_confidence > 0
    
    def test_intent_affinity_scoring(self):
        """Test intent affinity increases confidence."""
        from cortex.wiring import get_registry
        engine = SemanticRankingEngine()
        registry = get_registry()
        
        orchestrators = registry.list_orchestrators()
        if "TDDOrchestrator" not in orchestrators:
            pytest.skip("TDDOrchestrator not available")
        
        candidates = [
            ("TDDOrchestrator", registry.resolve_orchestrator("TDDOrchestrator"), 0.5)
        ]
        context = {"keywords": ["implement"]}
        
        ranked = engine.rank_candidates(candidates, context, IntentType.IMPLEMENT)
        assert len(ranked) > 0
        # Should have higher confidence due to intent alignment
        assert ranked[0].total_confidence >= 0.5
    
    def test_match_reasons_generated(self):
        """Test match reasons are generated."""
        from cortex.wiring import get_registry
        engine = SemanticRankingEngine()
        registry = get_registry()
        
        orchestrators = registry.list_orchestrators()
        if "TDDOrchestrator" not in orchestrators:
            pytest.skip("TDDOrchestrator not available")
        
        candidates = [
            ("TDDOrchestrator", registry.resolve_orchestrator("TDDOrchestrator"), 0.5)
        ]
        context = {"keywords": ["implement"]}
        
        ranked = engine.rank_candidates(candidates, context, IntentType.IMPLEMENT)
        assert len(ranked) > 0
        assert len(ranked[0].match_reasons) > 0


class TestDisambiguationUI:
    """Tests for DisambiguationUI."""
    
    def test_auto_select_high_confidence(self):
        """Test auto-selection for high confidence."""
        from cortex.wiring import get_registry
        ui = DisambiguationUI()
        registry = get_registry()
        
        orchestrators = registry.list_orchestrators()
        if not orchestrators or len(orchestrators) < 2:
            pytest.skip("Not enough orchestrators available")
        
        names = orchestrators[:2]
        
        candidates = [
            RankedCandidate(
                orchestrator_name=names[0],
                orchestrator_instance=registry.resolve_orchestrator(names[0]),
                base_confidence=0.8,
                semantic_score=0.15,
                total_confidence=0.95,
                match_reasons=["strong match"],
            ),
            RankedCandidate(
                orchestrator_name=names[1],
                orchestrator_instance=registry.resolve_orchestrator(names[1]),
                base_confidence=0.5,
                semantic_score=0.10,
                total_confidence=0.60,
                match_reasons=["weak match"],
            ),
        ]
        context = {"operation": "implement"}
        
        result = ui.prompt_selection(candidates, context)
        assert result.selected_orchestrator == names[0]
        assert result.confidence == 0.95
        assert result.auto_selected is True
    
    def test_disambiguation_below_threshold(self):
        """Test disambiguation when confidence is below threshold."""
        from cortex.wiring import get_registry
        ui = DisambiguationUI()
        registry = get_registry()
        
        orchestrators = registry.list_orchestrators()
        if not orchestrators or len(orchestrators) < 2:
            pytest.skip("Not enough orchestrators available")
        
        names = orchestrators[:2]
        
        candidates = [
            RankedCandidate(
                orchestrator_name=names[0],
                orchestrator_instance=registry.resolve_orchestrator(names[0]),
                base_confidence=0.6,
                semantic_score=0.15,
                total_confidence=0.75,
                match_reasons=["match1"],
            ),
            RankedCandidate(
                orchestrator_name=names[1],
                orchestrator_instance=registry.resolve_orchestrator(names[1]),
                base_confidence=0.55,
                semantic_score=0.15,
                total_confidence=0.70,
                match_reasons=["match2"],
            ),
        ]
        context = {"operation": "implement"}
        
        result = ui.prompt_selection(candidates, context)
        # Should still select but not auto
        assert result.selected_orchestrator is not None
        assert result.auto_selected is False


# ============================================================================
# PHASE 8.4: NLP ENHANCEMENT TESTS
# ============================================================================

class TestEmbeddingCache:
    """Tests for EmbeddingCache."""
    
    def test_cache_set_get(self):
        """Test basic cache operations."""
        cache = EmbeddingCache(max_size=10, ttl_seconds=3600)
        
        embedding = [0.1, 0.2, 0.3]
        cache.set("test", embedding)
        
        retrieved = cache.get("test")
        assert retrieved == embedding
    
    def test_cache_miss(self):
        """Test cache miss returns None."""
        cache = EmbeddingCache()
        result = cache.get("nonexistent")
        assert result is None
    
    def test_cache_hit_tracking(self):
        """Test hit/miss tracking."""
        cache = EmbeddingCache()
        
        cache.set("test", [0.1, 0.2])
        cache.get("test")  # Hit
        cache.get("missing")  # Miss
        
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
    
    def test_lru_eviction(self):
        """Test LRU eviction when cache is full."""
        cache = EmbeddingCache(max_size=2)
        
        cache.set("first", [0.1])
        cache.set("second", [0.2])
        cache.set("third", [0.3])  # Should evict "first"
        
        assert cache.get("first") is None  # Evicted
        assert cache.get("second") is not None
        assert cache.get("third") is not None


class TestSynonymExpansionService:
    """Tests for SynonymExpansionService."""
    
    def test_expansion(self):
        """Test synonym expansion."""
        service = SynonymExpansionService()
        
        result = service.expand("implement")
        assert "implement" in result.synonyms
        assert "create" in result.synonyms or "build" in result.synonyms
        assert result.expansion_count > 0
    
    def test_batch_expansion(self):
        """Test batch keyword expansion."""
        service = SynonymExpansionService()
        
        expanded = service.expand_keywords(["implement", "fix"])
        assert "implement" in expanded
        assert "fix" in expanded
        assert len(expanded) > 2  # Should have synonyms
    
    def test_custom_synonym_group(self):
        """Test adding custom synonym group."""
        service = SynonymExpansionService()
        
        service.add_synonym_group("testing", {"test", "verify", "validate"})
        result = service.expand("test")
        
        assert "test" in result.synonyms
        assert "verify" in result.synonyms


class TestABTestingFramework:
    """Tests for ABTestingFramework."""
    
    def test_record_decision(self):
        """Test recording decisions."""
        framework = ABTestingFramework()
        
        framework.record_decision(
            variant=Variant.CONTROL,
            orchestrator="TDDOrchestrator",
            confidence=0.75,
            latency_ms=10.0,
            keywords=["implement"],
        )
        
        assert len(framework.decisions[Variant.CONTROL]) == 1
    
    def test_results_calculation(self):
        """Test A/B test results calculation."""
        framework = ABTestingFramework()
        
        # Control
        framework.record_decision(
            Variant.CONTROL, "TDDOrchestrator", 0.70, 10.0, ["implement"]
        )
        
        # Treatment
        framework.record_decision(
            Variant.TREATMENT, "TDDOrchestrator", 0.85, 15.0, ["implement"]
        )
        
        results = framework.get_results()
        assert results.control_avg_confidence == 0.70
        assert results.treatment_avg_confidence == 0.85
        assert results.treatment_improvement > 0


# ============================================================================
# PHASE 8.5: EDGE CASE DETECTION TESTS
# ============================================================================

class TestCSharpASTAnalyzer:
    """Tests for CSharpASTAnalyzer."""
    
    def test_initialization(self):
        """Test analyzer initialization."""
        analyzer = CSharpASTAnalyzer()
        assert analyzer is not None
    
    def test_class_detection(self, tmp_path):
        """Test C# class detection."""
        analyzer = CSharpASTAnalyzer()
        test_file = tmp_path / "test.cs"
        test_file.write_text("""
        public class UserService {
            public void GetUser() { }
        }
        """)
        
        result = analyzer.analyze_file(test_file)
        assert result.class_count > 0
    
    def test_null_check_edge_case(self, tmp_path):
        """Test missing null check detection."""
        analyzer = CSharpASTAnalyzer()
        test_file = tmp_path / "test.cs"
        test_file.write_text("""
        public void Process(string input) {
            int length = input.Length;  // No null check!
        }
        """)
        
        result = analyzer.analyze_file(test_file)
        # Should detect potential null reference
        assert any(ec["type"] == "missing_null_check" for ec in result.edge_cases)


class TestSQLOracleAnalyzer:
    """Tests for SQLOracleAnalyzer."""
    
    def test_initialization(self):
        """Test analyzer initialization."""
        analyzer = SQLOracleAnalyzer()
        assert analyzer is not None
    
    def test_sql_injection_detection(self, tmp_path):
        """Test SQL injection vulnerability detection."""
        analyzer = SQLOracleAnalyzer()
        test_file = tmp_path / "test.sql"
        test_file.write_text("""
        EXECUTE IMMEDIATE 'SELECT * FROM users WHERE id = ' || user_input;
        """)
        
        result = analyzer.analyze_file(test_file)
        # Should detect SQL injection risk
        critical_cases = [ec for ec in result.edge_cases if ec["severity"] == "critical"]
        assert len(critical_cases) > 0


class TestAngularTypeScriptAnalyzer:
    """Tests for AngularTypeScriptAnalyzer."""
    
    def test_initialization(self):
        """Test analyzer initialization."""
        analyzer = AngularTypeScriptAnalyzer()
        assert analyzer is not None
    
    def test_memory_leak_detection(self, tmp_path):
        """Test memory leak detection."""
        analyzer = AngularTypeScriptAnalyzer()
        test_file = tmp_path / "test.component.ts"
        test_file.write_text("""
        export class UserComponent {
            ngOnInit() {
                this.subscription = this.service.getData().subscribe();
            }
            // No ngOnDestroy - memory leak!
        }
        """)
        
        result = analyzer.analyze_file(test_file)
        # Should detect potential memory leak
        assert any(ec["type"] == "memory_leak" for ec in result.edge_cases)


class TestUnifiedEdgeCaseDetector:
    """Tests for UnifiedEdgeCaseDetector."""
    
    def test_initialization(self):
        """Test detector initialization."""
        detector = UnifiedEdgeCaseDetector()
        assert detector is not None
        assert len(detector.remediations) >= 12
        assert len(detector.impacts) >= 12
    
    def test_edge_case_aggregation(self):
        """Test edge case aggregation."""
        detector = UnifiedEdgeCaseDetector()
        
        # Mock edge cases
        csharp_cases = [
            {"type": "missing_null_check", "severity": "medium", "line": 10, "message": "Test"}
        ]
        sql_cases = [
            {"type": "sql_injection", "severity": "critical", "line": 5, "message": "Test"}
        ]
        
        detector.add_edge_cases(csharp_cases, "C#")
        detector.add_edge_cases(sql_cases, "SQL")
        
        assert len(detector.edge_cases) == 2
    
    def test_priority_scoring(self):
        """Test priority score calculation."""
        detector = UnifiedEdgeCaseDetector()
        
        # Critical severity should have high priority
        critical_score = detector._calculate_priority(EdgeCaseSeverity.CRITICAL, 5)
        low_score = detector._calculate_priority(EdgeCaseSeverity.LOW, 5)
        
        assert critical_score > low_score
        assert critical_score >= 50  # Minimum for critical
    
    def test_severity_filtering(self):
        """Test filtering by severity."""
        detector = UnifiedEdgeCaseDetector()
        
        cases = [
            {"type": "sql_injection", "severity": "critical", "line": 1, "message": "Test"},
            {"type": "select_star", "severity": "medium", "line": 2, "message": "Test"},
        ]
        detector.add_edge_cases(cases, "SQL")
        
        critical = detector.get_by_severity(EdgeCaseSeverity.CRITICAL)
        assert len(critical) >= 1
    
    def test_top_priority_extraction(self):
        """Test top priority extraction."""
        detector = UnifiedEdgeCaseDetector()
        
        cases = [
            {"type": "sql_injection", "severity": "critical", "line": 1, "message": "Test"},
            {"type": "missing_null_check", "severity": "medium", "line": 2, "message": "Test"},
            {"type": "any_type", "severity": "low", "line": 3, "message": "Test"},
        ]
        detector.add_edge_cases(cases, "Mixed")
        
        top_5 = detector.get_top_priority(5)
        # Critical should be first
        assert top_5[0].severity == EdgeCaseSeverity.CRITICAL


# ============================================================================
# PHASE 8.6: ROUTING HEALTH CHECKS TESTS
# ============================================================================

class TestRoutingHealthChecker:
    """Tests for RoutingHealthChecker."""
    
    def test_initialization(self):
        """Test health checker initialization."""
        checker = RoutingHealthChecker()
        assert checker is not None
    
    def test_all_checks_run(self):
        """Test all 6 health checks execute."""
        checker = RoutingHealthChecker()
        results = checker.run_all_checks()
        
        # Should have 6 checks
        assert len(results) == 6
        
        # Verify check IDs
        check_ids = [r.check_id for r in results]
        assert "ROUTE-001" in check_ids  # Routing coverage
        assert "ROUTE-002" in check_ids  # Confidence thresholds
        assert "ROUTE-003" in check_ids  # Enforcement rules
        assert "ROUTE-004" in check_ids  # Edge case detector
        assert "ROUTE-005" in check_ids  # Semantic ranking
        assert "ROUTE-006" in check_ids  # NLP cache
    
    def test_report_formatting(self):
        """Test report formatting."""
        checker = RoutingHealthChecker()
        checker.run_all_checks()
        
        report = checker.format_report()
        assert "ROUTING HEALTH CHECK REPORT" in report
        assert len(report) > 0


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestPhase8Integration:
    """Integration tests for Phase 8 components."""
    
    def test_full_edge_case_pipeline(self, tmp_path):
        """Test complete edge case detection pipeline."""
        # Create test files
        csharp_file = tmp_path / "test.cs"
        csharp_file.write_text("public class Test { }")
        
        sql_file = tmp_path / "test.sql"
        sql_file.write_text("SELECT * FROM users;")
        
        angular_file = tmp_path / "test.ts"
        angular_file.write_text("export class Component { }")
        
        # Run analyzers
        csharp_analyzer = CSharpASTAnalyzer()
        sql_analyzer = SQLOracleAnalyzer()
        angular_analyzer = AngularTypeScriptAnalyzer()
        
        csharp_result = csharp_analyzer.analyze_file(csharp_file)
        sql_result = sql_analyzer.analyze_file(sql_file)
        angular_result = angular_analyzer.analyze_file(angular_file)
        
        # Aggregate
        detector = UnifiedEdgeCaseDetector()
        detector.add_edge_cases(csharp_result.edge_cases, "C#")
        detector.add_edge_cases(sql_result.edge_cases, "SQL")
        detector.add_edge_cases(angular_result.edge_cases, "Angular")
        
        # Verify aggregation worked
        stats = detector.get_summary_stats()
        assert stats["total_edge_cases"] >= 0
    
    def test_semantic_ranking_with_synonyms(self):
        """Test semantic ranking with synonym expansion."""
        from cortex.wiring import get_registry
        
        # Create synonym service
        synonym_service = SynonymExpansionService()
        
        # Expand keywords
        expanded = synonym_service.expand_keywords(["create"])
        
        # Rank with expanded keywords
        engine = SemanticRankingEngine()
        registry = get_registry()
        orchestrators = registry.list_orchestrators()
        
        if not orchestrators or len(orchestrators) < 2:
            pytest.skip("Not enough orchestrators available")
        
        names = orchestrators[:2]
        candidates = [
            (name, registry.resolve_orchestrator(name), 0.5)
            for name in names
        ]
        context = {"keywords": list(expanded)}
        
        ranked = engine.rank_candidates(candidates, context, IntentType.IMPLEMENT)
        
        # Should have ranked candidates
        assert len(ranked) > 0
        assert ranked[0].total_confidence > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
