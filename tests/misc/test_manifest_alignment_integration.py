"""
Integration Tests for Manifest System with Alignment

Tests the complete workflow:
1. Manifest creation/loading
2. Orchestrator validation
3. Alignment integration
4. Caching optimization
5. Multi-orchestrator validation

Author: CORTEX Development Team
Version: 1.0
Created: 2025-12-08
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from src.utils.manifest_validator import (
    ManifestValidator,
    ValidationReport,
    ValidationSeverity,
    ValidationIssue
)


class TestManifestValidatorIntegration:
    """Integration tests for ManifestValidator"""
    
    @pytest.fixture
    def cortex_root(self, tmp_path):
        """Create temporary CORTEX structure"""
        root = tmp_path / "CORTEX"
        root.mkdir()
        
        # Create manifest directory
        manifest_dir = root / "cortex-brain" / "manifests" / "orchestrators"
        manifest_dir.mkdir(parents=True)
        
        # Create orchestrators directory
        orch_dir = root / "src" / "orchestrators"
        orch_dir.mkdir(parents=True)
        
        return root
    
    @pytest.fixture
    def sample_manifest(self, cortex_root):
        """Create sample manifest file"""
        manifest_dir = cortex_root / "cortex-brain" / "manifests" / "orchestrators"
        manifest_path = manifest_dir / "test-manifest.yaml"
        
        manifest_content = """
schema_version: "1.0"

metadata:
  orchestrator_name: "test_orchestrator"
  version: "1.0.0"
  description: "Test orchestrator"
  status: "active"

requirements:
  - requirement_id: "REQ-001"
    name: "Test Feature 1"
    status: "implemented"
    priority: "critical"
    validation_method: "method_exists"
    validation_criteria: "TestOrchestrator.feature_one()"
  
  - requirement_id: "REQ-002"
    name: "Test Feature 2"
    status: "missing"
    priority: "high"
    validation_method: "method_exists"
    validation_criteria: "TestOrchestrator.feature_two()"

integrations:
  - integration_id: "INT-001"
    target_component: "TestAgent"
    integration_type: "required"
    status: "implemented"

quality_gates:
  - gate_id: "GATE-001"
    name: "Input Validation"
    gate_type: "pre_execution"
    status: "implemented"
"""
        manifest_path.write_text(manifest_content)
        return str(manifest_path)
    
    @pytest.fixture
    def sample_orchestrator(self, cortex_root):
        """Create sample orchestrator file"""
        orch_dir = cortex_root / "src" / "orchestrators"
        orch_path = orch_dir / "test_orchestrator.py"
        
        orch_content = """
class TestOrchestrator:
    def __init__(self):
        self.name = "Test"
    
    def feature_one(self):
        return "Feature 1 implemented"
    
    # feature_two is intentionally missing
"""
        orch_path.write_text(orch_content)
        return str(orch_path)
    
    def test_manifest_loading(self, cortex_root, sample_manifest):
        """Test manifest loading with caching"""
        validator = ManifestValidator(cortex_root=str(cortex_root))
        
        # First load
        manifest1 = validator.load_manifest(sample_manifest)
        assert manifest1 is not None
        assert manifest1['metadata']['orchestrator_name'] == 'test_orchestrator'
        
        # Second load (from cache)
        manifest2 = validator.load_manifest(sample_manifest)
        assert manifest2 is manifest1  # Same object reference (cached)
    
    def test_orchestrator_validation(self, cortex_root, sample_manifest, sample_orchestrator):
        """Test orchestrator validation against manifest"""
        validator = ManifestValidator(cortex_root=str(cortex_root))
        
        # Load test orchestrator module
        import sys
        sys.path.insert(0, str(cortex_root / "src" / "orchestrators"))
        from test_orchestrator import TestOrchestrator
        
        # Validate against orchestrator (uses test-manifest.yaml automatically)
        report = validator.validate_orchestrator(
            "test",  # Will load test-manifest.yaml
            TestOrchestrator()
        )
        
        assert report is not None
        assert report.orchestrator_name == "test"
        assert len(report.issues) > 0  # Should have issues (missing feature_two)
        assert report.compliance_percentage < 100
        
        # Check for specific missing requirement
        missing_req = [i for i in report.issues if i.item_id == "REQ-002"]
        assert len(missing_req) == 1
        assert missing_req[0].severity == ValidationSeverity.HIGH
    
    def test_validation_caching(self, cortex_root, sample_manifest, sample_orchestrator):
        """Test validation report caching"""
        validator = ManifestValidator(cortex_root=str(cortex_root))
        
        # Load test orchestrator
        import sys
        sys.path.insert(0, str(cortex_root / "src" / "orchestrators"))
        from test_orchestrator import TestOrchestrator
        
        instance = TestOrchestrator()
        
        # First validation
        report1 = validator.validate_orchestrator("test", instance)
        
        # Second validation (cache test - same results)
        report2 = validator.validate_orchestrator("test", instance)
        
        assert report1.compliance_percentage == report2.compliance_percentage
        assert len(report1.issues) == len(report2.issues)
    
    def test_compliance_properties(self, cortex_root, sample_manifest, sample_orchestrator):
        """Test ValidationReport properties for alignment integration"""
        validator = ManifestValidator(cortex_root=str(cortex_root))
        
        # Load test orchestrator
        import sys
        sys.path.insert(0, str(cortex_root / "src" / "orchestrators"))
        from test_orchestrator import TestOrchestrator
        
        report = validator.validate_orchestrator("test", TestOrchestrator())
        
        # Test required properties
        assert hasattr(report, 'compliance_percentage')
        assert hasattr(report, 'status')
        assert hasattr(report, 'requirement_id')
        assert hasattr(report, 'total_requirements')
        assert hasattr(report, 'implemented_count')
        
        # Test property values
        assert isinstance(report.compliance_percentage, float)
        assert report.status in ["Compliant", "Drift Detected", "Non-Compliant"]
        assert report.requirement_id == "test_manifest"  # Uses orchestrator name


class TestAlignmentIntegration:
    """Test manifest validation integration with alignment utility"""
    
    def test_alignment_utility_has_manifest_validator(self):
        """Test that alignment utility has manifest validator integrated"""
        from src.operations.modules.admin.align_utility import AlignUtility
        
        # Create utility (uses real config)
        utility = AlignUtility(force_full=True, quick_mode=False)
        
        # Should have manifest validator attributes
        assert hasattr(utility, 'manifest_validator')
        assert hasattr(utility, 'manifest_validation_enabled')
        
        # Check if validator is properly initialized
        if utility.manifest_validation_enabled:
            assert utility.manifest_validator is not None
    
    def test_validate_manifest_compliance_method_exists(self):
        """Test that alignment utility has validate_manifest_compliance method"""
        from src.operations.modules.admin.align_utility import AlignUtility
        
        utility = AlignUtility(force_full=True, quick_mode=True)
        
        # Method should exist
        assert hasattr(utility, 'validate_manifest_compliance')
        assert callable(utility.validate_manifest_compliance)


class TestPerformanceOptimization:
    """Test caching and performance optimizations"""
    
    def test_file_content_caching(self, tmp_path):
        """Test file content caching reduces I/O"""
        root = tmp_path / "CORTEX"
        root.mkdir()
        
        validator = ManifestValidator(cortex_root=str(root))
        
        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text("def test_method(): pass")
        
        # First read
        content1 = validator._read_file_cached(str(test_file))
        assert content1 is not None
        
        # Second read (from cache)
        content2 = validator._read_file_cached(str(test_file))
        assert content2 is content1  # Same object reference
        
        # Cache should contain entry
        assert str(test_file) in validator._file_content_cache
    
    def test_method_extraction_caching(self, tmp_path):
        """Test method extraction caching"""
        root = tmp_path / "CORTEX"
        root.mkdir()
        
        validator = ManifestValidator(cortex_root=str(root))
        
        # Create test file with methods
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def method_one():
    pass

def method_two():
    pass

class TestClass:
    def method_three(self):
        pass
""")
        
        # First extraction
        methods1 = validator._extract_methods_cached(str(test_file))
        assert 'method_one' in methods1
        assert 'method_two' in methods1
        assert 'method_three' in methods1
        
        # Second extraction (from cache)
        methods2 = validator._extract_methods_cached(str(test_file))
        assert methods2 is methods1  # Same object reference
    
    def test_cache_hit_rate(self, tmp_path):
        """Test cache hit rate for repeated validations"""
        root = tmp_path / "CORTEX"
        root.mkdir()
        
        manifest_dir = root / "cortex-brain" / "manifests" / "orchestrators"
        manifest_dir.mkdir(parents=True)
        
        validator = ManifestValidator(cortex_root=str(root))
        
        # Create manifest
        manifest_path = manifest_dir / "test.yaml"
        manifest_path.write_text("""
schema_version: "1.0"
metadata:
  orchestrator_name: "test"
  version: "1.0.0"
requirements: []
""")
        
        # Multiple loads should use cache
        for _ in range(5):
            manifest = validator.load_manifest(str(manifest_path))
            assert manifest is not None
        
        # Should only have one cached entry
        assert len(validator._manifest_cache) == 1


class TestMultiOrchestratorValidation:
    """Test validation across multiple orchestrators"""
    
    def test_validate_all_orchestrators(self, tmp_path):
        """Test validating multiple orchestrators"""
        root = tmp_path / "CORTEX"
        root.mkdir()
        
        manifest_dir = root / "cortex-brain" / "manifests" / "orchestrators"
        manifest_dir.mkdir(parents=True)
        
        orch_dir = root / "src" / "orchestrators"
        orch_dir.mkdir(parents=True)
        
        validator = ManifestValidator(cortex_root=str(root))
        
        # Create multiple manifests
        for i in range(3):
            manifest_path = manifest_dir / f"orch{i}-manifest.yaml"
            manifest_path.write_text(f"""
schema_version: "1.0"
metadata:
  orchestrator_name: "orch{i}"
  version: "1.0.0"
requirements: []
""")
        
        # Should be able to load all
        reports = []
        for i in range(3):
            manifest_path = manifest_dir / f"orch{i}-manifest.yaml"
            manifest = validator.load_manifest(str(manifest_path))
            assert manifest is not None
            reports.append(manifest)
        
        assert len(reports) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
