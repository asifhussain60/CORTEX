"""
Test Suite for Phase 3: TDD Workflow Enhancement - Tier Feeding
Part of CORTEX 3.6.0 Implementation

Tests deliverables 3.1, 3.2, 3.3:
- RED/GREEN/REFACTOR phase tier feeding
- Pattern learning from TDD cycles
- Real-time development context updates

Author: Asif Hussain
Created: December 1, 2025
"""

import pytest
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Test imports - will be implemented
from src.orchestrators.tdd_orchestrator import TDDOrchestrator, TDDPhase, TDDWorkRequest
from src.tier1.working_memory import WorkingMemory
from src.tier2.knowledge_graph import KnowledgeGraph
from src.tier3.context_intelligence import ContextIntelligence


# ============================================================================
# DELIVERABLE 3.1: Development Phase Insight Extraction
# ============================================================================


class TestRedPhaseTierFeeding:
    """Test RED phase extracts test requirements to Tier 1"""
    
    @pytest.fixture
    def tdd_orchestrator(self, tmp_path):
        """Create TDD orchestrator with temporary brain"""
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir(parents=True, exist_ok=True)
        return TDDOrchestrator(brain_path=brain_path)
    
    def test_red_phase_captures_test_intent(self, tdd_orchestrator):
        """Test that RED phase extracts test intent to Tier 1"""
        # Arrange
        work_request = TDDWorkRequest(
            feature_name="User Authentication",
            test_file_path="tests/test_auth.py",
            implementation_file_path="src/auth.py",
            requirements=["User can login with valid credentials"]
        )
        
        # Act
        chunks = tdd_orchestrator.break_into_chunks(work_request.__dict__)
        red_chunk = [c for c in chunks if c.metadata.get('phase') == TDDPhase.RED.value][0]
        result = tdd_orchestrator.execute_chunk(red_chunk)
        
        # Assert
        assert result['success'] is True
        
        # Verify Tier 1 captured test intent (use orchestrator's tier1)
        tier1_data = tdd_orchestrator.tier1.get_recent_test_intents(limit=1)
        assert len(tier1_data) > 0
        assert "login with valid credentials" in tier1_data[0]['requirement'].lower()
    
    def test_red_phase_captures_edge_cases(self, tdd_orchestrator):
        """Test that RED phase extracts edge cases to Tier 1"""
        # Arrange
        work_request = TDDWorkRequest(
            feature_name="Input Validation",
            test_file_path="tests/test_validation.py",
            implementation_file_path="src/validation.py",
            requirements=[
                "Reject empty input",
                "Reject input exceeding max length",
                "Accept valid input within range"
            ]
        )
        
        # Act
        chunks = tdd_orchestrator.break_into_chunks(work_request.__dict__)
        red_chunks = [c for c in chunks if c.metadata.get('phase') == TDDPhase.RED.value]
        
        for chunk in red_chunks[:3]:  # Execute first 3 RED chunks
            tdd_orchestrator.execute_chunk(chunk)
        
        # Assert
        edge_cases = tdd_orchestrator.tier1.get_edge_cases_for_feature("Input Validation")
        assert len(edge_cases) >= 3
        assert any("empty" in case['description'].lower() for case in edge_cases)
        assert any("max length" in case['description'].lower() for case in edge_cases)
    
    def test_red_phase_no_circular_dependency(self, tdd_orchestrator):
        """Test that RED phase does not rely on git commit messages"""
        # Arrange
        work_request = TDDWorkRequest(
            feature_name="File Upload",
            test_file_path="tests/test_upload.py",
            implementation_file_path="src/upload.py",
            requirements=["Upload file with size validation"]
        )
        
        # Act
        chunks = tdd_orchestrator.break_into_chunks(work_request.__dict__)
        red_chunk = [c for c in chunks if c.metadata.get('phase') == TDDPhase.RED.value][0]
        
        # Execute RED chunk BEFORE any commit
        result = tdd_orchestrator.execute_chunk(red_chunk)
        
        # Assert
        assert result['success'] is True
        
        # Verify Tier 1 has data without needing git commits
        tier1_data = tdd_orchestrator.tier1.get_recent_test_intents(limit=1)
        assert len(tier1_data) > 0
        # No git commit should have been made yet
        assert tier1_data[0].get('source') != 'git_commit'
        assert tier1_data[0].get('source') == 'tdd_red_phase'


class TestGreenPhaseTierFeeding:
    """Test GREEN phase extracts implementation patterns to Tier 2"""
    
    @pytest.fixture
    def tdd_orchestrator(self, tmp_path):
        """Create TDD orchestrator with temporary brain"""
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir(parents=True, exist_ok=True)
        return TDDOrchestrator(brain_path=brain_path)
    
    def test_green_phase_captures_implementation_pattern(self, tdd_orchestrator):
        """Test that GREEN phase extracts implementation patterns to Tier 2"""
        # Arrange
        work_request = TDDWorkRequest(
            feature_name="Data Validation",
            test_file_path="tests/test_validator.py",
            implementation_file_path="src/validator.py",
            requirements=["Validate email format"]
        )
        
        # Act - Execute RED then GREEN
        chunks = tdd_orchestrator.break_into_chunks(work_request.__dict__)
        green_chunk = [c for c in chunks if c.metadata.get('phase') == TDDPhase.GREEN.value][0]
        result = tdd_orchestrator.execute_chunk(green_chunk)
        
        # Assert
        assert result['success'] is True
        
        # Verify Tier 2 learned the implementation pattern
        patterns = tdd_orchestrator.tier2.search_patterns(query="email validation", limit=5)
        assert len(patterns) > 0
        pattern = patterns[0]
        assert 'email' in pattern['title'].lower() or 'validation' in pattern['title'].lower()
        assert pattern['pattern_type'] == 'implementation'
    
    def test_green_phase_captures_dependencies(self, tdd_orchestrator):
        """Test that GREEN phase captures implementation dependencies"""
        # Arrange
        work_request = TDDWorkRequest(
            feature_name="Database Connection",
            test_file_path="tests/test_db.py",
            implementation_file_path="src/database.py",
            requirements=["Connect to database with retry logic"]
        )
        
        # Act
        chunks = tdd_orchestrator.break_into_chunks(work_request.__dict__)
        green_chunk = [c for c in chunks if c.metadata.get('phase') == TDDPhase.GREEN.value][0]
        result = tdd_orchestrator.execute_chunk(green_chunk)
        
        # Assert
        dependencies = tdd_orchestrator.tier2.get_implementation_dependencies(feature="Database Connection")
        assert len(dependencies) > 0
        assert any('retry' in dep['description'].lower() for dep in dependencies)
    
    def test_green_phase_captures_decisions(self, tdd_orchestrator):
        """Test that GREEN phase captures implementation decisions"""
        # Arrange
        work_request = TDDWorkRequest(
            feature_name="Cache Strategy",
            test_file_path="tests/test_cache.py",
            implementation_file_path="src/cache.py",
            requirements=["Implement LRU cache with TTL"]
        )
        
        # Act
        chunks = tdd_orchestrator.break_into_chunks(work_request.__dict__)
        green_chunk = [c for c in chunks if c.metadata.get('phase') == TDDPhase.GREEN.value][0]
        result = tdd_orchestrator.execute_chunk(green_chunk)
        
        # Assert
        decisions = tdd_orchestrator.tier2.get_implementation_decisions(feature="Cache Strategy")
        assert len(decisions) > 0
        decision = decisions[0]
        assert 'lru' in decision['decision'].lower() or 'ttl' in decision['decision'].lower()
        assert decision['rationale'] is not None


class TestRefactorPhaseTierFeeding:
    """Test REFACTOR phase extracts improvements to Tier 3"""
    
    @pytest.fixture
    def tdd_orchestrator(self, tmp_path):
        """Create TDD orchestrator with temporary brain"""
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir(parents=True, exist_ok=True)
        return TDDOrchestrator(brain_path=brain_path)
    
    def test_refactor_phase_captures_improvements(self, tdd_orchestrator):
        """Test that REFACTOR phase captures code improvements"""
        # Arrange
        work_request = TDDWorkRequest(
            feature_name="String Parser",
            test_file_path="tests/test_parser.py",
            implementation_file_path="src/parser.py",
            requirements=["Parse comma-separated values"]
        )
        
        # Act - Execute RED, GREEN, then REFACTOR
        chunks = tdd_orchestrator.break_into_chunks(work_request.__dict__)
        refactor_chunk = [c for c in chunks if c.metadata.get('phase') == TDDPhase.REFACTOR.value][0]
        result = tdd_orchestrator.execute_chunk(refactor_chunk)
        
        # Assert
        assert result['success'] is True
        
        # Verify Tier 3 captured improvements
        improvements = tdd_orchestrator.tier3.get_recent_improvements(limit=5)
        assert len(improvements) > 0
        improvement = improvements[0]
        assert improvement['improvement_type'] in ['performance', 'readability', 'maintainability']
    
    def test_refactor_phase_captures_performance_gains(self, tdd_orchestrator):
        """Test that REFACTOR phase measures performance gains"""
        # Arrange
        work_request = TDDWorkRequest(
            feature_name="Data Processor",
            test_file_path="tests/test_processor.py",
            implementation_file_path="src/processor.py",
            requirements=["Process large dataset efficiently"]
        )
        
        # Act
        chunks = tdd_orchestrator.break_into_chunks(work_request.__dict__)
        refactor_chunk = [c for c in chunks if c.metadata.get('phase') == TDDPhase.REFACTOR.value][0]
        result = tdd_orchestrator.execute_chunk(refactor_chunk)
        
        # Assert
        metrics = tdd_orchestrator.tier3.get_performance_metrics(feature="Data Processor")
        assert len(metrics) > 0
        metric = metrics[0]
        assert 'before_ms' in metric
        assert 'after_ms' in metric
        assert 'improvement_percent' in metric
    
    def test_refactor_phase_captures_simplifications(self, tdd_orchestrator):
        """Test that REFACTOR phase tracks code simplifications"""
        # Arrange
        work_request = TDDWorkRequest(
            feature_name="Complex Algorithm",
            test_file_path="tests/test_algorithm.py",
            implementation_file_path="src/algorithm.py",
            requirements=["Implement sorting algorithm"]
        )
        
        # Act
        chunks = tdd_orchestrator.break_into_chunks(work_request.__dict__)
        refactor_chunk = [c for c in chunks if c.metadata.get('phase') == TDDPhase.REFACTOR.value][0]
        result = tdd_orchestrator.execute_chunk(refactor_chunk)
        
        # Assert
        simplifications = tdd_orchestrator.tier3.get_complexity_changes(feature="Complex Algorithm")
        assert len(simplifications) > 0
        simplification = simplifications[0]
        assert 'before_complexity' in simplification
        assert 'after_complexity' in simplification
        # Refactoring should reduce complexity
        assert simplification['after_complexity'] <= simplification['before_complexity']


# ============================================================================
# DELIVERABLE 3.2: Pattern Learning from TDD Cycles
# ============================================================================


class TestPatternLearning:
    """Test Tier 2 learns patterns from completed TDD cycles"""
    
    @pytest.fixture
    def tdd_orchestrator(self, tmp_path):
        """Create TDD orchestrator (includes tier2)"""
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir(parents=True, exist_ok=True)
        return TDDOrchestrator(brain_path=brain_path)
    
    def test_stores_tdd_cycle_as_pattern(self, tdd_orchestrator):
        """Test completed TDD cycles are stored as patterns"""
        # Arrange
        tdd_cycle = {
            'feature': 'User Registration',
            'test_strategy': 'happy_path_first',
            'implementation_approach': 'minimal_then_extend',
            'refactoring_type': 'extract_method'
        }
        
        # Act
        pattern_id = tdd_orchestrator.tier2.store_tdd_cycle_pattern(
            feature=tdd_cycle['feature'],
            test_strategy=tdd_cycle['test_strategy'],
            implementation_approach=tdd_cycle['implementation_approach'],
            refactoring_type=tdd_cycle['refactoring_type']
        )
        
        # Assert
        assert pattern_id is not None
        stored_pattern = tdd_orchestrator.tier2.get_pattern(pattern_id)
        assert stored_pattern['title'] == 'User Registration'
        assert stored_pattern['pattern_type'] == 'tdd_cycle'
    
    def test_pattern_includes_test_strategy(self, tdd_orchestrator):
        """Test patterns include test strategy"""
        # Arrange
        tdd_orchestrator.tier2.store_tdd_cycle_pattern(
            feature='Input Validation',
            test_strategy='edge_cases_first',
            implementation_approach='defensive_programming',
            refactoring_type='consolidate_conditionals'
        )
        
        # Act
        patterns = tdd_orchestrator.tier2.search_patterns(query="Input Validation")
        
        # Assert
        assert len(patterns) > 0
        pattern = patterns[0]
        context = json.loads(pattern['context_json'])
        assert context['test_strategy'] == 'edge_cases_first'
    
    def test_pattern_includes_implementation_approach(self, tdd_orchestrator):
        """Test patterns include implementation approach"""
        # Arrange
        tdd_orchestrator.tier2.store_tdd_cycle_pattern(
            feature='API Client',
            test_strategy='mock_external_services',
            implementation_approach='dependency_injection',
            refactoring_type='extract_interface'
        )
        
        # Act
        patterns = tdd_orchestrator.tier2.search_patterns(query="API Client")
        
        # Assert
        pattern = patterns[0]
        context = json.loads(pattern['context_json'])
        assert context['implementation_approach'] == 'dependency_injection'
    
    def test_pattern_includes_refactoring_type(self, tdd_orchestrator):
        """Test patterns include refactoring type"""
        # Arrange
        tdd_orchestrator.tier2.store_tdd_cycle_pattern(
            feature='Data Parser',
            test_strategy='property_based_testing',
            implementation_approach='functional_style',
            refactoring_type='replace_temp_with_query'
        )
        
        # Act
        patterns = tdd_orchestrator.tier2.search_patterns(query="Data Parser")
        
        # Assert
        pattern = patterns[0]
        context = json.loads(pattern['context_json'])
        assert context['refactoring_type'] == 'replace_temp_with_query'
    
    def test_future_tdd_cycles_suggest_patterns(self, tdd_orchestrator):
        """Test future TDD cycles get pattern suggestions"""
        # Arrange - Store historical patterns
        tdd_orchestrator.tier2.store_tdd_cycle_pattern(
            feature='User Authentication',
            test_strategy='security_focused',
            implementation_approach='fail_secure',
            refactoring_type='extract_security_checks'
        )
        tdd_orchestrator.tier2.store_tdd_cycle_pattern(
            feature='User Authorization',
            test_strategy='security_focused',
            implementation_approach='fail_secure',
            refactoring_type='consolidate_role_checks'
        )
        
        # Act - Search for similar patterns
        suggestions = tdd_orchestrator.tier2.suggest_patterns_for_feature("User Password Reset")
        
        # Assert
        assert len(suggestions) > 0
        # Should suggest security-focused patterns
        security_patterns = [s for s in suggestions if 'security' in s['context'].lower()]
        assert len(security_patterns) > 0
    
    def test_pattern_matching_uses_fts5(self, tdd_orchestrator):
        """Test pattern matching uses FTS5 semantic search"""
        # Arrange - Store patterns with semantic similarity
        tdd_orchestrator.tier2.store_tdd_cycle_pattern(
            feature='Email Validator',
            test_strategy='regex_testing',
            implementation_approach='regex_based',
            refactoring_type='extract_regex_patterns'
        )
        tdd_orchestrator.tier2.store_tdd_cycle_pattern(
            feature='Phone Validator',
            test_strategy='regex_testing',
            implementation_approach='regex_based',
            refactoring_type='extract_regex_patterns'
        )
        
        # Act - Search with related term (not exact match)
        results = tdd_orchestrator.tier2.fts5_search("validation")
        
        # Assert - FTS5 should find semantically related patterns
        assert len(results) >= 2
        titles = [r['title'] for r in results]
        assert any('Validator' in title for title in titles)


# ============================================================================
# DELIVERABLE 3.3: Real-Time Development Context Updates
# ============================================================================


class TestRealTimeContextUpdates:
    """Test Tier 3 updates during development, not post-commit"""
    
    @pytest.fixture
    def tdd_orchestrator(self, tmp_path):
        """Create TDD orchestrator (includes tier3)"""
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir(parents=True, exist_ok=True)
        return TDDOrchestrator(brain_path=brain_path)
    
    def test_green_phase_calculates_complexity_metrics(self, tdd_orchestrator):
        """Test complexity metrics calculated during GREEN phase"""
        # Arrange
        work_request = TDDWorkRequest(
            feature_name="Business Logic",
            test_file_path="tests/test_logic.py",
            implementation_file_path="src/logic.py",
            requirements=["Calculate discount based on rules"]
        )
        
        # Act - Execute GREEN phase
        chunks = tdd_orchestrator.break_into_chunks(work_request.__dict__)
        green_chunk = [c for c in chunks if c.metadata.get('phase') == TDDPhase.GREEN.value][0]
        result = tdd_orchestrator.execute_chunk(green_chunk)
        
        # Assert - Tier 3 should have metrics BEFORE commit
        metrics = tdd_orchestrator.tier3.get_code_metrics(file_path="src/logic.py")
        assert metrics is not None
        assert 'cyclomatic_complexity' in metrics
        assert 'cognitive_complexity' in metrics
        assert metrics['measured_at'] is not None
        # Verify this was captured during GREEN, not from git
        assert metrics['source'] == 'tdd_green_phase'
    
    def test_refactor_phase_measures_impact(self, tdd_orchestrator):
        """Test refactoring impact measured during REFACTOR phase"""
        # Arrange - Simulate GREEN phase with initial complexity
        tdd_orchestrator.tier3.store_code_metrics(
            file_path="src/calculator.py",
            cyclomatic_complexity=8,
            cognitive_complexity=12,
            lines_of_code=150,
            source='tdd_green_phase'
        )
        
        work_request = TDDWorkRequest(
            feature_name="Calculator",
            test_file_path="tests/test_calculator.py",
            implementation_file_path="src/calculator.py",
            requirements=["Add complex calculation"]
        )
        
        # Act - Execute REFACTOR phase
        chunks = tdd_orchestrator.break_into_chunks(work_request.__dict__)
        refactor_chunk = [c for c in chunks if c.metadata.get('phase') == TDDPhase.REFACTOR.value][0]
        result = tdd_orchestrator.execute_chunk(refactor_chunk)
        
        # Assert - Tier 3 should have before/after comparison
        impact = tdd_orchestrator.tier3.get_refactoring_impact(file_path="src/calculator.py")
        assert impact is not None
        assert 'before' in impact
        assert 'after' in impact
        assert 'improvement_percent' in impact
        # Refactoring should improve (reduce) complexity
        assert impact['after']['cyclomatic_complexity'] <= impact['before']['cyclomatic_complexity']
    
    def test_hotspot_detection_updates_realtime(self, tdd_orchestrator):
        """Test hotspot detection updates in real-time"""
        # Arrange - Simulate multiple edits to same file
        work_requests = [
            TDDWorkRequest(
                feature_name="Auth Feature 1",
                test_file_path="tests/test_auth.py",
                implementation_file_path="src/auth.py",
                requirements=["Implement login"]
            ),
            TDDWorkRequest(
                feature_name="Auth Feature 2",
                test_file_path="tests/test_auth.py",
                implementation_file_path="src/auth.py",
                requirements=["Implement logout"]
            ),
            TDDWorkRequest(
                feature_name="Auth Feature 3",
                test_file_path="tests/test_auth.py",
                implementation_file_path="src/auth.py",
                requirements=["Implement password reset"]
            )
        ]
        
        # Act - Execute multiple TDD cycles on same file
        for work_request in work_requests:
            chunks = tdd_orchestrator.break_into_chunks(work_request.__dict__)
            green_chunk = [c for c in chunks if c.metadata.get('phase') == TDDPhase.GREEN.value][0]
            tdd_orchestrator.execute_chunk(green_chunk)
        
        # Assert - src/auth.py should be detected as hotspot
        hotspots = tdd_orchestrator.tier3.get_hotspots(limit=5)
        assert len(hotspots) > 0
        auth_hotspot = [h for h in hotspots if 'auth.py' in h['file_path']]
        assert len(auth_hotspot) > 0
        assert auth_hotspot[0]['edit_count'] >= 3
        # Verify detection happened in real-time, not from git log
        assert auth_hotspot[0]['detection_source'] == 'tdd_realtime'
    
    def test_metrics_stored_before_commit(self, tdd_orchestrator):
        """Test metrics are stored in Tier 3 before any git commit"""
        # Arrange
        work_request = TDDWorkRequest(
            feature_name="New Feature",
            test_file_path="tests/test_new.py",
            implementation_file_path="src/new_feature.py",
            requirements=["Implement new feature"]
        )
        
        # Act - Execute GREEN phase (no git commit yet)
        chunks = tdd_orchestrator.break_into_chunks(work_request.__dict__)
        green_chunk = [c for c in chunks if c.metadata.get('phase') == TDDPhase.GREEN.value][0]
        result = tdd_orchestrator.execute_chunk(green_chunk)
        
        # Assert - Tier 3 should have data BEFORE commit
        all_metrics = tdd_orchestrator.tier3.get_all_metrics(source='tdd_green_phase')
        assert len(all_metrics) > 0
        # Verify timestamp is during GREEN phase, not post-commit
        metric = all_metrics[0]
        assert metric['captured_at'] is not None
        assert (datetime.now() - metric['captured_at']).total_seconds() < 5  # Within 5 seconds


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestFullTDDCycleIntegration:
    """Test full RED→GREEN→REFACTOR cycle feeds all tiers"""
    
    @pytest.fixture
    def orchestrator(self, tmp_path):
        """Create orchestrator with all tiers"""
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir(parents=True, exist_ok=True)
        return TDDOrchestrator(brain_path=brain_path)
    
    @pytest.fixture
    def all_tiers(self, orchestrator):
        """Return orchestrator's tier instances"""
        return {
            'tier1': orchestrator.tier1,
            'tier2': orchestrator.tier2,
            'tier3': orchestrator.tier3
        }
    
    def test_complete_tdd_cycle_feeds_all_tiers(self, orchestrator, all_tiers):
        """Test RED→GREEN→REFACTOR cycle feeds Tier 1, 2, and 3"""
        # Arrange
        work_request = TDDWorkRequest(
            feature_name="Complete Feature",
            test_file_path="tests/test_complete.py",
            implementation_file_path="src/complete.py",
            requirements=["Implement complete feature with validation"]
        )
        
        # Act - Execute full TDD cycle
        chunks = orchestrator.break_into_chunks(work_request.__dict__)
        
        for chunk in chunks:
            orchestrator.execute_chunk(chunk)
        
        # Assert - All tiers should have data
        
        # Tier 1: Test intents from RED phase
        tier1_data = all_tiers['tier1'].get_recent_test_intents(limit=5)
        assert len(tier1_data) > 0, "Tier 1 should have test intents from RED phase"
        
        # Tier 2: Implementation patterns from GREEN phase
        tier2_data = all_tiers['tier2'].search_patterns(query="Complete Feature")
        assert len(tier2_data) > 0, "Tier 2 should have patterns from GREEN phase"
        
        # Tier 3: Metrics and improvements from REFACTOR phase
        tier3_data = all_tiers['tier3'].get_code_metrics(file_path="src/complete.py")
        assert tier3_data is not None, "Tier 3 should have metrics from REFACTOR phase"
    
    def test_extraction_performance_overhead(self, orchestrator, all_tiers):
        """Test tier feeding adds <2% performance overhead"""
        import time
        
        # Arrange
        work_request = TDDWorkRequest(
            feature_name="Performance Test",
            test_file_path="tests/test_perf.py",
            implementation_file_path="src/perf.py",
            requirements=["Simple feature for performance testing"]
        )
        
        # Act - Measure with tier feeding
        start_with_feeding = time.time()
        chunks = orchestrator.break_into_chunks(work_request.__dict__)
        for chunk in chunks[:3]:  # Execute first 3 chunks
            orchestrator.execute_chunk(chunk)
        time_with_feeding = time.time() - start_with_feeding
        
        # Act - Measure without tier feeding (disable)
        orchestrator.disable_tier_feeding()
        start_without_feeding = time.time()
        chunks = orchestrator.break_into_chunks(work_request.__dict__)
        for chunk in chunks[:3]:
            orchestrator.execute_chunk(chunk)
        time_without_feeding = time.time() - start_without_feeding
        
        # Assert - Overhead should be < 2%
        if time_without_feeding > 0:
            overhead_percent = ((time_with_feeding - time_without_feeding) / time_without_feeding) * 100
            assert overhead_percent < 2.0, f"Performance overhead {overhead_percent}% exceeds 2% limit"
    
    def test_pattern_suggestions_work_correctly(self, orchestrator, all_tiers):
        """Test pattern suggestions from Tier 2 work correctly"""
        # Arrange - Execute TDD cycle to create patterns
        work_request_1 = TDDWorkRequest(
            feature_name="Security Check",
            test_file_path="tests/test_security.py",
            implementation_file_path="src/security.py",
            requirements=["Implement authentication check"]
        )
        
        chunks = orchestrator.break_into_chunks(work_request_1.__dict__)
        for chunk in chunks:
            orchestrator.execute_chunk(chunk)
        
        # Act - Start new similar feature
        work_request_2 = TDDWorkRequest(
            feature_name="Authorization Check",
            test_file_path="tests/test_authorization.py",
            implementation_file_path="src/authorization.py",
            requirements=["Implement permission check"]
        )
        
        suggestions = all_tiers['tier2'].suggest_patterns_for_feature("Authorization Check")
        
        # Assert - Should suggest security-related patterns
        assert len(suggestions) > 0, "Should have pattern suggestions from previous TDD cycles"
        security_suggestions = [s for s in suggestions if 'security' in s['title'].lower()]
        assert len(security_suggestions) > 0, "Should suggest related security patterns"
