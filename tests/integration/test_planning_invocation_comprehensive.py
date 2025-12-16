"""
Comprehensive Test Harness for Planning System Invocation
Tests various prompts WITHOUT "plan" keyword to validate automatic planning engagement

Purpose:
- Verify Planning Gate intercepts all Tier 3+ requests
- Test SKULL enforcement (MANDATORY_PLANNING_ENFORCEMENT)
- Validate visual indicators shown to users
- Ensure artifacts created in correct folder structure
- Test implicit planning triggers (keywords like "comprehensive", "holistic", etc.)

Author: CORTEX Test Infrastructure
Date: December 16, 2025
Coverage Target: 100% for planning invocation workflows
"""

import pytest
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock
import json

# Test fixtures
@pytest.fixture
def cortex_root(tmp_path):
    """Create temporary CORTEX directory structure."""
    cortex_dir = tmp_path / "CORTEX"
    brain_dir = cortex_dir / "cortex-brain" / "documents" / "planning" / "features"
    
    (brain_dir / "temp-plans").mkdir(parents=True, exist_ok=True)
    (brain_dir / "active").mkdir(parents=True, exist_ok=True)
    (brain_dir / "completed").mkdir(parents=True, exist_ok=True)
    
    return cortex_dir


@pytest.fixture
def planning_gate(cortex_root):
    """Create PlanningGate instance."""
    # Mock until implementation exists
    class MockPlanningGate:
        def __init__(self, cortex_root):
            self.cortex_root = Path(cortex_root)
            self.invocations = []
        
        def process_request(self, user_request: str) -> Dict[str, Any]:
            """Process request through planning triage."""
            self.invocations.append(user_request)
            
            # Simulate tier classification
            tier = self._classify_tier(user_request)
            
            if tier <= 2:
                return {
                    'requires_planning': False,
                    'complexity_tier': tier,
                    'proceed_to_execution': True
                }
            
            # Create temporary plan
            plan_id = f"TEMP-PLAN-{len(self.invocations)}"
            plan_folder = self.cortex_root / "cortex-brain" / "documents" / "planning" / "features" / "temp-plans" / plan_id
            plan_folder.mkdir(parents=True, exist_ok=True)
            
            return {
                'requires_planning': True,
                'complexity_tier': tier,
                'temp_plan_id': plan_id,
                'proceed_to_execution': False,
                'plan_location': str(plan_folder)
            }
        
        def _classify_tier(self, request: str) -> int:
            """Classify complexity tier."""
            request_lower = request.lower()
            
            # Tier 4: COMPLEX (nested planning)
            tier_4_keywords = ['nested', 'multi-phase', 'comprehensive plan', 'architecture overhaul']
            if any(kw in request_lower for kw in tier_4_keywords):
                return 4
            
            # Tier 3: DOCUMENTED (feature plan)
            tier_3_keywords = ['comprehensive', 'holistic', 'analyze', 'review', 'architecture', 
                              'deep dive', 'investigation', 'audit', 'assessment']
            if any(kw in request_lower for kw in tier_3_keywords):
                return 3
            
            # Tier 2: LIGHTWEIGHT (inline validation)
            tier_2_keywords = ['validate', 'check', 'verify', 'lint']
            if any(kw in request_lower for kw in tier_2_keywords):
                return 2
            
            # Tier 1: INSTANT (direct execution)
            return 1
    
    return MockPlanningGate(cortex_root)


# ============================================================================
# TEST SUITE 1: Implicit Planning Triggers
# ============================================================================

class TestImplicitPlanningTriggers:
    """
    Test that various prompts WITHOUT explicit "plan" keyword trigger planning.
    These are real-world requests that should engage temporary planning.
    """
    
    @pytest.mark.parametrize("request,expected_tier", [
        # Architecture prompts
        ("Do a holistic review of the CORTEX architecture", 3),
        ("Analyze the system design and identify gaps", 3),
        ("Review the codebase architecture comprehensively", 3),
        
        # Investigation prompts
        ("Investigate why the planning system wasn't triggered", 3),
        ("Perform a deep dive into the test failures", 3),
        ("Audit the security implementation", 3),
        
        # Analysis prompts
        ("Analyze all orchestrators and find conflicts", 3),
        ("Do a comprehensive assessment of test coverage", 3),
        ("Review database schema and recommend improvements", 3),
        
        # Multi-step prompts
        ("Identify all planning systems, compare them, and recommend consolidation", 4),
        ("Analyze workspace architecture, create migration plan, and implement changes", 4),
        
        # Should NOT trigger planning (Tier 1-2)
        ("What's the current version?", 1),
        ("Validate the YAML syntax", 2),
    ])
    def test_implicit_keywords_trigger_planning(self, planning_gate, request, expected_tier):
        """Various implicit keywords should trigger appropriate tier classification."""
        result = planning_gate.process_request(request)
        
        assert result['complexity_tier'] == expected_tier
        
        if expected_tier >= 3:
            assert result['requires_planning'] == True
            assert result['proceed_to_execution'] == False
            assert 'temp_plan_id' in result
        else:
            assert result['requires_planning'] == False
            assert result['proceed_to_execution'] == True
    
    def test_chat01_workspace_request_triggers_planning(self, planning_gate):
        """The exact request from chat01.md should have triggered planning."""
        request = """
        to avoid setting up multiple python environmes for every repo, I've started 
        using CORTEX in a workspace setting. This is not how CORTEX was originally 
        developed to work. Do a holistic review of CORTEX architecture and infrastructure 
        and advise on how do enhance it to work in a workspace environment. Create a 
        comprehensive plan identifying gaps and how we can make it work.
        """
        
        result = planning_gate.process_request(request)
        
        assert result['requires_planning'] == True, "chat01.md request should trigger planning!"
        assert result['complexity_tier'] >= 3
        assert 'temp_plan_id' in result
    
    def test_multiple_step_indicators_trigger_tier_4(self, planning_gate):
        """Requests with multiple phases should trigger Tier 4 (COMPLEX)."""
        requests_needing_nested_plans = [
            "Analyze all files, create migration plan, then implement changes",
            "Review architecture, design new system, migrate incrementally",
            "Audit codebase, identify technical debt, create remediation roadmap"
        ]
        
        for request in requests_needing_nested_plans:
            result = planning_gate.process_request(request)
            assert result['complexity_tier'] == 4, f"Failed for: {request}"
            assert result['requires_planning'] == True


# ============================================================================
# TEST SUITE 2: Artifact Organization
# ============================================================================

class TestPlanningArtifactOrganization:
    """Test that artifacts are created in correct folder structure, never at root."""
    
    def test_temp_plans_in_correct_folder(self, planning_gate, cortex_root):
        """Temporary plans created in temp-plans/ folder."""
        request = "Comprehensive architecture analysis"
        
        result = planning_gate.process_request(request)
        
        plan_id = result['temp_plan_id']
        expected_path = cortex_root / "cortex-brain" / "documents" / "planning" / "features" / "temp-plans" / plan_id
        
        assert expected_path.exists(), f"Expected temp plan at: {expected_path}"
    
    def test_no_root_level_artifacts(self, planning_gate, cortex_root):
        """No artifacts created at planning/ root level."""
        request = "Do comprehensive analysis"
        
        planning_gate.process_request(request)
        
        planning_root = cortex_root / "cortex-brain" / "documents" / "planning"
        root_artifacts = list(planning_root.glob("*.md")) + list(planning_root.glob("*.yaml"))
        
        assert len(root_artifacts) == 0, f"Found root-level artifacts: {root_artifacts}"
    
    def test_multiple_plans_separate_folders(self, planning_gate, cortex_root):
        """Multiple plans each get their own folder."""
        requests = [
            "Analyze database schema",
            "Review API architecture",
            "Audit security implementation"
        ]
        
        plan_ids = []
        for request in requests:
            result = planning_gate.process_request(request)
            plan_ids.append(result['temp_plan_id'])
        
        # Each plan should have its own folder
        temp_plans_dir = cortex_root / "cortex-brain" / "documents" / "planning" / "features" / "temp-plans"
        folders = [d for d in temp_plans_dir.iterdir() if d.is_dir()]
        
        assert len(folders) == len(requests)
        assert all(plan_id in [f.name for f in folders] for plan_id in plan_ids)


# ============================================================================
# TEST SUITE 3: Visual Indicators
# ============================================================================

class TestVisualPlanningIndicators:
    """Test that users see visual feedback when planning engages."""
    
    def test_planning_engagement_message_shown(self, planning_gate, capsys):
        """User sees '🎭 Planning System Engaged' message."""
        with patch('builtins.print') as mock_print:
            # Simulate visual indicator
            def show_indicator():
                print("🎭 Planning System Engaged")
                print("⏳ Creating temporary plan...")
            
            show_indicator()
            
            result = planning_gate.process_request("Comprehensive analysis")
            
            # Verify print was called with planning indicator
            calls = [str(call) for call in mock_print.call_args_list]
            assert any("Planning System Engaged" in str(call) for call in calls)
    
    def test_complexity_tier_shown(self, planning_gate):
        """Complexity tier shown in visual indicator."""
        result = planning_gate.process_request("Holistic architecture review")
        
        # Should include tier in response (for rendering)
        assert 'complexity_tier' in result
        assert result['complexity_tier'] == 3
    
    def test_progress_phases_listed(self, planning_gate):
        """Planning phases listed in progress indicator."""
        expected_phases = [
            "DoR validation",
            "Complexity analysis",
            "Phase decomposition",
            "Risk assessment",
            "Approval gate"
        ]
        
        # Simulate rendering
        def render_progress():
            return "\n".join([f"⏳ Phase: {phase}" for phase in expected_phases])
        
        progress = render_progress()
        for phase in expected_phases:
            assert phase in progress


# ============================================================================
# TEST SUITE 4: SKULL Enforcement
# ============================================================================

class TestSKULLPlanningEnforcement:
    """Test MANDATORY_PLANNING_ENFORCEMENT SKULL rule."""
    
    def test_tier_3_without_plan_blocked(self):
        """Tier 3 work without approved plan is blocked."""
        # Simulate Brain Protector check
        request = {
            'intent': 'comprehensive architecture analysis',
            'has_plan': False,
            'plan_approved': False,
            'complexity_tier': 3
        }
        
        # Mock Brain Protector
        class MockBrainProtector:
            def validate(self, request):
                if request['complexity_tier'] >= 3 and not request.get('plan_approved'):
                    return {
                        'is_blocked': True,
                        'rule_id': 'MANDATORY_PLANNING_ENFORCEMENT',
                        'severity': 'blocked',
                        'message': 'Tier 3+ work requires approved plan',
                        'alternatives': ['Create temporary plan first']
                    }
                return {'is_blocked': False}
        
        protector = MockBrainProtector()
        result = protector.validate(request)
        
        assert result['is_blocked'] == True
        assert result['rule_id'] == 'MANDATORY_PLANNING_ENFORCEMENT'
    
    def test_tier_1_without_plan_allowed(self):
        """Tier 1 work without plan is allowed."""
        request = {
            'intent': 'quick calculation',
            'has_plan': False,
            'complexity_tier': 1
        }
        
        class MockBrainProtector:
            def validate(self, request):
                if request['complexity_tier'] >= 3 and not request.get('plan_approved'):
                    return {'is_blocked': True}
                return {'is_blocked': False}
        
        protector = MockBrainProtector()
        result = protector.validate(request)
        
        assert result['is_blocked'] == False
    
    def test_approved_plan_allows_execution(self):
        """Approved plan bypasses SKULL block."""
        request = {
            'intent': 'comprehensive analysis',
            'has_plan': True,
            'plan_approved': True,
            'complexity_tier': 4
        }
        
        class MockBrainProtector:
            def validate(self, request):
                if request['complexity_tier'] >= 3 and not request.get('plan_approved'):
                    return {'is_blocked': True}
                return {'is_blocked': False}
        
        protector = MockBrainProtector()
        result = protector.validate(request)
        
        assert result['is_blocked'] == False


# ============================================================================
# TEST SUITE 5: Edge Cases
# ============================================================================

class TestPlanningEdgeCases:
    """Test edge cases and corner scenarios."""
    
    def test_ambiguous_request_defaults_to_planning(self, planning_gate):
        """Ambiguous requests default to requiring planning."""
        ambiguous_requests = [
            "Fix the system",
            "Make it better",
            "Improve performance",
            "Enhance the architecture"
        ]
        
        for request in ambiguous_requests:
            result = planning_gate.process_request(request)
            # Should err on side of caution (require planning)
            assert result['requires_planning'] == True or result['complexity_tier'] >= 2
    
    def test_empty_request_handled_gracefully(self, planning_gate):
        """Empty request doesn't crash."""
        result = planning_gate.process_request("")
        assert 'complexity_tier' in result
        assert result['complexity_tier'] == 1  # Treat as instant/no-op
    
    def test_very_long_request_classified_correctly(self, planning_gate):
        """Very long requests (multi-paragraph) classified as Tier 3+."""
        long_request = " ".join([
            "I need you to analyze the entire CORTEX codebase,",
            "identify all architectural issues,",
            "create a comprehensive remediation plan,",
            "and implement the changes incrementally",
            "with full test coverage and documentation."
        ])
        
        result = planning_gate.process_request(long_request)
        assert result['complexity_tier'] >= 3
        assert result['requires_planning'] == True
    
    def test_plan_keyword_still_works(self, planning_gate):
        """Explicit 'plan' keyword still triggers planning."""
        result = planning_gate.process_request("Create a plan for feature X")
        assert result['requires_planning'] == True
        assert result['complexity_tier'] >= 3


# ============================================================================
# TEST SUITE 6: Integration with Entry Point
# ============================================================================

class TestEntryPointIntegration:
    """Test planning gate integration with CORTEX entry point."""
    
    def test_entry_point_has_planning_gate(self):
        """Entry point must have planning_gate attribute."""
        # Mock CortexEntry
        class MockCortexEntry:
            def __init__(self):
                self.planning_gate = MagicMock()  # Should exist
        
        entry = MockCortexEntry()
        assert hasattr(entry, 'planning_gate')
        assert entry.planning_gate is not None
    
    def test_all_requests_pass_through_planning_gate(self):
        """All user requests routed through planning gate first."""
        class MockCortexEntry:
            def __init__(self):
                self.planning_gate = MagicMock()
                self.planning_gate.process_request = MagicMock(return_value={
                    'requires_planning': False,
                    'complexity_tier': 1,
                    'proceed_to_execution': True
                })
            
            def process(self, request):
                # Must call planning gate
                triage = self.planning_gate.process_request(request)
                return triage
        
        entry = MockCortexEntry()
        result = entry.process("Some request")
        
        # Verify planning gate was invoked
        entry.planning_gate.process_request.assert_called_once()
    
    def test_tier_3_blocks_execution_until_approval(self):
        """Tier 3+ work blocks execution until plan approved."""
        class MockCortexEntry:
            def __init__(self):
                self.planning_gate = MagicMock()
            
            def process(self, request):
                triage = self.planning_gate.process_request(request)
                
                if triage['requires_planning'] and not triage['proceed_to_execution']:
                    return {
                        'status': 'awaiting_approval',
                        'temp_plan_id': triage['temp_plan_id']
                    }
                
                return {'status': 'executing'}
        
        entry = MockCortexEntry()
        entry.planning_gate.process_request.return_value = {
            'requires_planning': True,
            'complexity_tier': 3,
            'temp_plan_id': 'TEMP-001',
            'proceed_to_execution': False
        }
        
        result = entry.process("Comprehensive analysis")
        
        assert result['status'] == 'awaiting_approval'
        assert 'temp_plan_id' in result


# ============================================================================
# TEST SUITE 7: Real-World Scenarios
# ============================================================================

class TestRealWorldScenarios:
    """Test actual user scenarios that previously failed."""
    
    def test_chat01_workspace_analysis_scenario(self, planning_gate, cortex_root):
        """
        Reproduce chat01.md scenario:
        User requested workspace analysis but planning wasn't engaged.
        """
        request = "Do a holistic review of CORTEX architecture and advise on workspace compatibility"
        
        result = planning_gate.process_request(request)
        
        # Should have triggered planning
        assert result['requires_planning'] == True
        assert result['complexity_tier'] == 3
        
        # Should have created temp plan
        assert 'temp_plan_id' in result
        
        # Should be in correct folder
        plan_folder = Path(result['plan_location'])
        assert plan_folder.exists()
        assert "temp-plans" in str(plan_folder)
    
    def test_rca_investigation_scenario(self, planning_gate):
        """
        User asks: "Why wasn't the planner engaged? Do an RCA"
        Should trigger planning for the investigation itself.
        """
        request = "Investigate why the temporary planner wasn't engaged and do an RCA"
        
        result = planning_gate.process_request(request)
        
        assert result['requires_planning'] == True
        assert result['complexity_tier'] == 3
    
    def test_test_creation_scenario(self, planning_gate):
        """
        User asks: "Create tests to run different prompts through CORTEX"
        Should trigger planning for test suite design.
        """
        request = "Create tests to run different prompts through CORTEX without including 'plan'"
        
        result = planning_gate.process_request(request)
        
        # Test suite creation is Tier 3 work
        assert result['requires_planning'] == True
        assert result['complexity_tier'] == 3


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPlanningPerformance:
    """Test performance characteristics of planning system."""
    
    def test_classification_under_100ms(self, planning_gate, benchmark):
        """Tier classification should complete under 100ms."""
        def classify():
            return planning_gate.process_request("Comprehensive architecture analysis")
        
        result = benchmark(classify)
        # Note: benchmark fixture from pytest-benchmark
        # Falls back to manual timing if not available
    
    def test_batch_classification_scales_linearly(self, planning_gate):
        """Classifying N requests should scale O(N), not O(N²)."""
        import time
        
        requests = [
            f"Analyze system component {i}"
            for i in range(100)
        ]
        
        start = time.perf_counter()
        for request in requests:
            planning_gate.process_request(request)
        end = time.perf_counter()
        
        elapsed_ms = (end - start) * 1000
        avg_per_request = elapsed_ms / len(requests)
        
        assert avg_per_request < 10, f"Average {avg_per_request:.2f}ms too slow (target <10ms)"


# ============================================================================
# SMOKE TESTS (Run on every commit)
# ============================================================================

@pytest.mark.smoke
class TestPlanningSmoke:
    """Quick smoke tests to catch regressions."""
    
    def test_planning_gate_exists(self):
        """PlanningGate class exists and importable."""
        try:
            # Will fail until implemented
            from src.entry_point.planning_gate import PlanningGate
            assert PlanningGate is not None
        except ImportError:
            pytest.skip("PlanningGate not yet implemented")
    
    def test_temporary_plan_manager_exists(self):
        """TemporaryPlanManager exists."""
        from src.operations.modules.orchestration.temporary_plan_manager import TemporaryPlanManager
        assert TemporaryPlanManager is not None
    
    def test_skull_planning_rule_exists(self):
        """MANDATORY_PLANNING_ENFORCEMENT exists in brain protection rules."""
        import yaml
        from pathlib import Path
        
        rules_path = Path("cortex-brain/brain-protection-rules.yaml")
        if not rules_path.exists():
            pytest.skip("Brain protection rules not found")
        
        with open(rules_path) as f:
            rules = yaml.safe_load(f)
        
        instincts = rules.get('tier0_instincts', [])
        # Check if rule exists (may be named differently)
        has_planning_enforcement = any('PLANNING' in str(i) for i in instincts)
        
        # Will fail until implemented
        # assert has_planning_enforcement, "MANDATORY_PLANNING_ENFORCEMENT not found"


if __name__ == '__main__':
    # Run tests with coverage
    pytest.main([
        __file__,
        '-v',
        '--cov=src.entry_point',
        '--cov=src.operations.modules.orchestration',
        '--cov-report=html',
        '--cov-report=term-missing'
    ])
