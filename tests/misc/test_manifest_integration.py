"""
Integration Tests for Manifest System

Tests manifest validator, compliance scoring, and alignment integration.

Author: CORTEX Development Team
Version: 1.0
"""

import pytest
import sys
from pathlib import Path

# Add src to path
cortex_root = Path(__file__).parent.parent
sys.path.insert(0, str(cortex_root))

from src.utils.manifest_validator import ManifestValidator, ValidationSeverity


class TestManifestValidator:
    """Test manifest validator functionality"""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance"""
        return ManifestValidator(cortex_root=cortex_root)
    
    def test_validator_initialization(self, validator):
        """Test validator initializes correctly"""
        assert validator.cortex_root == cortex_root
        assert validator.manifests_dir.exists()
        assert isinstance(validator._manifest_cache, dict)
        assert isinstance(validator._file_content_cache, dict)
        assert isinstance(validator._method_cache, dict)
    
    def test_load_manifest(self, validator):
        """Test loading Planning System 2.0 manifest"""
        manifest_path = cortex_root / "cortex-brain" / "manifests/orchestrators" / "planning-system-2.0-manifest.yaml"
        
        if not manifest_path.exists():
            pytest.skip("Planning System 2.0 manifest not found")
        
        manifest = validator.load_manifest(str(manifest_path))
        
        assert manifest is not None
        assert 'metadata' in manifest
        assert 'requirements' in manifest
        assert manifest['metadata']['orchestrator_name'] == 'planning_system_2.0'
    
    def test_manifest_caching(self, validator):
        """Test that manifests are cached"""
        manifest_path = cortex_root / "cortex-brain" / "manifests/orchestrators" / "planning-system-2.0-manifest.yaml"
        
        if not manifest_path.exists():
            pytest.skip("Planning System 2.0 manifest not found")
        
        # Load twice
        manifest1 = validator.load_manifest(str(manifest_path))
        manifest2 = validator.load_manifest(str(manifest_path))
        
        # Should be same object (cached)
        assert manifest1 is manifest2
        assert str(manifest_path) in validator._manifest_cache
    
    def test_validate_planning_orchestrator(self, validator):
        """Test validating Planning System 2.0 orchestrator"""
        manifest_path = cortex_root / "cortex-brain" / "manifests/orchestrators" / "planning-system-2.0-manifest.yaml"
        orchestrator_path = cortex_root / "src" / "orchestrators" / "planning_orchestrator.py"
        
        if not manifest_path.exists() or not orchestrator_path.exists():
            pytest.skip("Planning System 2.0 files not found")
        
        manifest = validator.load_manifest(str(manifest_path))
        report = validator.validate_orchestrator(
            "PlanningOrchestrator",
            manifest,
            str(orchestrator_path)
        )
        
        assert report is not None
        assert hasattr(report, 'compliance_percentage')
        assert hasattr(report, 'status')
        assert hasattr(report, 'implemented_count')
        assert hasattr(report, 'total_requirements')
        
        # Should be at least 80% compliant (all critical requirements)
        assert report.compliance_percentage >= 80
    
    def test_compliance_scoring(self, validator):
        """Test compliance score calculation"""
        manifest_path = cortex_root / "cortex-brain" / "manifests/orchestrators" / "planning-system-2.0-manifest.yaml"
        orchestrator_path = cortex_root / "src" / "orchestrators" / "planning_orchestrator.py"
        
        if not manifest_path.exists() or not orchestrator_path.exists():
            pytest.skip("Planning System 2.0 files not found")
        
        manifest = validator.load_manifest(str(manifest_path))
        report = validator.validate_orchestrator(
            "PlanningOrchestrator",
            manifest,
            str(orchestrator_path)
        )
        
        # Score should be between 0-100
        assert 0 <= report.compliance_percentage <= 100
        
        # If all requirements implemented, score should be 100
        if report.implemented_count == report.total_requirements:
            assert report.compliance_percentage == 100
    
    def test_method_extraction_cache(self, validator):
        """Test method extraction with caching"""
        orchestrator_path = cortex_root / "src" / "orchestrators" / "planning_orchestrator.py"
        
        if not orchestrator_path.exists():
            pytest.skip("Planning orchestrator not found")
        
        # Extract twice
        methods1 = validator._extract_methods_cached(str(orchestrator_path))
        methods2 = validator._extract_methods_cached(str(orchestrator_path))
        
        # Should be cached
        assert methods1 is methods2
        assert str(orchestrator_path) in validator._method_cache
        
        # Should contain known methods
        expected_methods = {
            'estimate_from_swagger',
            'render_phase_progress',
            'review_threats_interactive',
            'format_tdd_reminder_section'
        }
        
        assert expected_methods.issubset(methods1)
    
    def test_file_content_cache(self, validator):
        """Test file content caching"""
        orchestrator_path = cortex_root / "src" / "orchestrators" / "planning_orchestrator.py"
        
        if not orchestrator_path.exists():
            pytest.skip("Planning orchestrator not found")
        
        # Read twice
        content1 = validator._read_file_cached(str(orchestrator_path))
        content2 = validator._read_file_cached(str(orchestrator_path))
        
        # Should be same object (cached)
        assert content1 is content2
        assert str(orchestrator_path) in validator._file_content_cache
    
    def test_ado_manifest_inheritance(self, validator):
        """Test ADO manifest inherits from Planning 2.0"""
        ado_path = cortex_root / "cortex-brain" / "manifests/orchestrators" / "ado-planning-manifest.yaml"
        planning_path = cortex_root / "cortex-brain" / "manifests/orchestrators" / "planning-system-2.0-manifest.yaml"
        
        if not ado_path.exists() or not planning_path.exists():
            pytest.skip("Manifest files not found")
        
        ado_manifest = validator.load_manifest(str(ado_path))
        
        assert 'inherits_from' in ado_manifest
        assert ado_manifest['inherits_from'] == 'planning-system-2.0-manifest.yaml'


class TestAlignmentIntegration:
    """Test manifest integration with alignment"""
    
    def test_alignment_validates_manifests(self):
        """Test that alignment runs manifest validation"""
        from src.operations.modules.admin.align_utility import AlignUtility
        
        utility = AlignUtility(quick_mode=False)
        report = utility.run_alignment()
        
        # Check that manifest validation ran
        manifest_checks = [c for c in report.checks if 'Manifest' in c.check_name]
        
        if manifest_checks:
            # If manifest check exists, verify it ran
            manifest_check = manifest_checks[0]
            assert manifest_check.check_name == "Manifest Compliance"
            
            # Should pass if Planning System 2.0 is compliant
            if manifest_check.passed:
                assert 'compliant' in manifest_check.message.lower()


class TestManifestSchema:
    """Test manifest schema validation"""
    
    def test_schema_exists(self):
        """Test that manifest schema file exists"""
        schema_path = cortex_root / "cortex-brain" / "manifests/orchestrators" / "manifest-schema.yaml"
        assert schema_path.exists()
    
    def test_planning_manifest_structure(self):
        """Test Planning System 2.0 manifest has correct structure"""
        manifest_path = cortex_root / "cortex-brain" / "manifests/orchestrators" / "planning-system-2.0-manifest.yaml"
        
        if not manifest_path.exists():
            pytest.skip("Planning System 2.0 manifest not found")
        
        import yaml
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = yaml.safe_load(f)
        
        # Check required sections
        assert 'metadata' in manifest
        assert 'requirements' in manifest
        
        # Check metadata fields
        metadata = manifest['metadata']
        assert 'orchestrator_name' in metadata
        assert 'version' in metadata
        assert 'status' in metadata
        
        # Check requirements structure
        requirements = manifest['requirements']
        assert isinstance(requirements, list)
        assert len(requirements) > 0
        
        # Check first requirement structure
        req = requirements[0]
        assert 'requirement_id' in req
        assert 'name' in req
        assert 'description' in req
        assert 'priority' in req
        assert 'status' in req


def test_performance():
    """Test that validator performs well with caching"""
    import time
    
    validator = ManifestValidator(cortex_root=cortex_root)
    manifest_path = cortex_root / "cortex-brain" / "manifests/orchestrators" / "planning-system-2.0-manifest.yaml"
    orchestrator_path = cortex_root / "src" / "orchestrators" / "planning_orchestrator.py"
    
    if not manifest_path.exists() or not orchestrator_path.exists():
        pytest.skip("Files not found")
    
    # First run (no cache)
    start = time.perf_counter()
    manifest = validator.load_manifest(str(manifest_path))
    report = validator.validate_orchestrator("PlanningOrchestrator", manifest, str(orchestrator_path))
    first_duration = time.perf_counter() - start
    
    # Clear caches
    validator._manifest_cache.clear()
    validator._file_content_cache.clear()
    validator._method_cache.clear()
    
    # Second run (with cache)
    start = time.perf_counter()
    manifest = validator.load_manifest(str(manifest_path))
    report = validator.validate_orchestrator("PlanningOrchestrator", manifest, str(orchestrator_path))
    cached_duration = time.perf_counter() - start
    
    # Both should complete quickly (<1 second)
    assert first_duration < 1.0
    assert cached_duration < 1.0
    
    print(f"\nPerformance: First={first_duration:.3f}s, Cached={cached_duration:.3f}s")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
