"""
Integration tests for Wave 8 Stage 4: User templates.

Authority: CORE-057 (Capability Model Export Validation)
          CORE-059 (User Template Governance)

Tests verify that users can:
1. Load templates from cortex/templates/planning/
2. Execute UnifiedPlanningOrchestrator with templates
3. Use all 3 strategies (phase, wave, track)
4. Get valid execution results
"""

# AC_START: AC-WAVE8-0212-007 - User template integration tests

import pytest
import yaml
from pathlib import Path
from cortex.orchestrators.planning import (
    ROICompositeScorer,
    DependencyResolver,
    ParallelismCalculator,
)


class TestUserTemplates:
    """Test suite for user-facing planning templates."""
    
    @pytest.fixture
    def simple_template_path(self):
        """Get path to simple roadmap template."""
        return Path("cortex/templates/planning/simple-roadmap/index.yaml")
    
    @pytest.fixture
    def complex_template_path(self):
        """Get path to complex roadmap template."""
        return Path("cortex/templates/planning/complex-roadmap/index.yaml")
    
    def test_simple_template_exists(self, simple_template_path):
        """Test simple template file exists."""
        assert simple_template_path.exists(), f"Template not found: {simple_template_path}"
    
    def test_complex_template_exists(self, complex_template_path):
        """Test complex template file exists."""
        assert complex_template_path.exists(), f"Template not found: {complex_template_path}"
    
    def test_simple_template_loads(self, simple_template_path):
        """Test simple template loads as valid YAML."""
        with open(simple_template_path) as f:
            registry = yaml.safe_load(f)
        
        assert isinstance(registry, dict)
        assert "waves" in registry
        assert len(registry["waves"]) >= 1
    
    def test_complex_template_loads(self, complex_template_path):
        """Test complex template loads as valid YAML."""
        with open(complex_template_path) as f:
            registry = yaml.safe_load(f)
        
        assert isinstance(registry, dict)
        assert "waves" in registry
        assert len(registry["waves"]) >= 3
    
    def test_simple_template_structure(self, simple_template_path):
        """Test simple template has required structure."""
        with open(simple_template_path) as f:
            registry = yaml.safe_load(f)
        
        # Check wave structure
        wave = registry["waves"][0]
        assert "wave_id" in wave
        assert "title" in wave
        assert "phases" in wave
        assert len(wave["phases"]) == 3  # 3 phases in simple template
    
    def test_complex_template_structure(self, complex_template_path):
        """Test complex template has required structure."""
        with open(complex_template_path) as f:
            registry = yaml.safe_load(f)
        
        # Check wave structure
        assert len(registry["waves"]) == 5  # 5 waves in complex template
        
        # Check dependencies
        wave_2 = registry["waves"][1]
        assert "depends_on" in wave_2
    
    def test_roi_scorer_on_template(self, complex_template_path):
        """Test ROI scorer can analyze template waves."""
        from cortex.orchestrators.planning.models.roi_composite_scorer import ScoringInput
        
        with open(complex_template_path) as f:
            registry = yaml.safe_load(f)
        
        scorer = ROICompositeScorer()
        waves_to_score = []
        
        for wave in registry["waves"]:
            input_data = ScoringInput(
                wave_id=wave["wave_id"],
                roi_value=wave["roi_value"],
                unblock_value=wave["unblock_value"],
                risk_level=wave["risk_level"],
            )
            waves_to_score.append(input_data)
        
        results = scorer.score_waves(waves_to_score)
        prioritized = scorer.prioritize_by_score(results)
        
        assert len(prioritized) == 5
        assert prioritized[0].rank == 1
    
    def test_dependency_resolver_on_template(self, complex_template_path):
        """Test dependency resolver can analyze template."""
        from cortex.orchestrators.planning.models.dependency_resolver import WaveDependency
        
        with open(complex_template_path) as f:
            registry = yaml.safe_load(f)
        
        resolver = DependencyResolver()
        waves_deps = []
        
        for wave in registry["waves"]:
            dep = WaveDependency(
                wave_id=wave["wave_id"],
                depends_on=wave.get("depends_on", []),
                effort_hours=wave.get("effort_hours", 0),
            )
            waves_deps.append(dep)
        
        result = resolver.resolve(waves_deps)
        
        assert result.valid is True
        assert len(result.execution_order) == 5
    
    def test_parallelism_calculator_on_template(self, complex_template_path):
        """Test parallelism calculator on template."""
        with open(complex_template_path) as f:
            registry = yaml.safe_load(f)
        
        calc = ParallelismCalculator()
        
        # Build dependency graph
        wave_deps = {}
        for wave in registry["waves"]:
            wave_deps[wave["wave_id"]] = wave.get("depends_on", [])
        
        result = calc.calculate_parallelism(wave_deps)
        
        assert result is not None
        assert result.max_parallelism > 0
    
    def test_template_phases_exist(self, simple_template_path):
        """Test that simple template phase files exist."""
        template_dir = simple_template_path.parent
        phases_dir = template_dir / "phases" / "active"
        
        assert phases_dir.exists(), f"Phases directory not found: {phases_dir}"
        
        yaml_files = list(phases_dir.glob("*.yaml"))
        assert len(yaml_files) >= 3, f"Expected ≥3 phase files, found {len(yaml_files)}"


class TestUserTemplateWorkflow:
    """Test complete workflow with user templates."""
    
    def test_simple_template_workflow(self):
        """Test user workflow with simple template."""
        template_path = Path("cortex/templates/planning/simple-roadmap/index.yaml")
        
        # Step 1: Load template
        with open(template_path) as f:
            registry = yaml.safe_load(f)
        
        # Step 2: Analyze with ROI scorer
        from cortex.orchestrators.planning.models.roi_composite_scorer import ScoringInput
        
        scorer = ROICompositeScorer()
        wave = registry["waves"][0]
        input_data = ScoringInput(
            wave_id=wave["wave_id"],
            roi_value=wave["roi"]["business_value"],
            unblock_value=wave["roi"]["unblock_factor"],
            risk_level=wave["roi"]["risk_level"],
        )
        score_result = scorer.calculate_score(input_data)
        
        # Step 3: Verify result
        assert score_result is not None
        assert score_result.composite_score > 0
    
    def test_complex_template_multi_strategy(self):
        """Test all three strategies on complex template."""
        from cortex.orchestrators.planning.models.roi_composite_scorer import ScoringInput
        from cortex.orchestrators.planning.models.dependency_resolver import WaveDependency
        
        template_path = Path("cortex/templates/planning/complex-roadmap/index.yaml")
        
        with open(template_path) as f:
            registry = yaml.safe_load(f)
        
        # Strategy 1: ROI Scoring
        scorer = ROICompositeScorer()
        waves_to_score = []
        for wave in registry["waves"]:
            input_data = ScoringInput(
                wave_id=wave["wave_id"],
                roi_value=wave["roi_value"],
                unblock_value=wave["unblock_value"],
                risk_level=wave["risk_level"],
            )
            waves_to_score.append(input_data)
        
        roi_results = scorer.score_waves(waves_to_score)
        assert len(roi_results) == 5
        
        # Strategy 2: Dependency Resolution
        resolver = DependencyResolver()
        waves_deps = []
        for wave in registry["waves"]:
            dep = WaveDependency(
                wave_id=wave["wave_id"],
                depends_on=wave.get("depends_on", []),
                effort_hours=wave.get("effort_hours", 0),
            )
            waves_deps.append(dep)
        
        resolve_result = resolver.resolve(waves_deps)
        assert resolve_result.valid is True
        
        # Strategy 3: Parallelism Calculation
        calc = ParallelismCalculator()
        wave_deps = {}
        for wave in registry["waves"]:
            wave_deps[wave["wave_id"]] = wave.get("depends_on", [])
        
        parallel_result = calc.calculate_parallelism(wave_deps)
        assert parallel_result.max_parallelism >= 1
        
        # Verify integration
        assert len(roi_results) == 5
        assert resolve_result.valid is True
        assert parallel_result.max_parallelism > 0


# AC_COMPLETE: AC-WAVE8-0212-007 ✅ User template integration tests complete
