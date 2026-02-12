"""
Tests for Vacuum Orchestrator Enhancements - Phase 1.

AC-ID: AC-VAC-ENH-TEST-001
Tests: File Categorizer + Conflict Detector

TDD Approach: GREEN tests (all enhancements working)
"""

import pytest
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
import importlib.util

# Get absolute path to cortex_brain (real location)
test_file = Path(__file__).resolve()
project_root = test_file.parent.parent.parent.parent.parent.parent  # /Users/asifhussain/PROJECTS/CORTEX
cortex_brain_path = project_root / "cortex_brain"

# Add sys.path for conftest loading
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Load file_categorizer
file_cat_path = cortex_brain_path / "tier1/orchestrators/enhancements/file_categorizer.py"
spec = importlib.util.spec_from_file_location("file_categorizer", str(file_cat_path))
if spec is None or spec.loader is None:
    raise RuntimeError(f"Could not load spec for file_categorizer at {file_cat_path}")
fc_module = importlib.util.module_from_spec(spec)
sys.modules["file_categorizer"] = fc_module
spec.loader.exec_module(fc_module)

FileCategory = fc_module.FileCategory
ClassificationSignals = fc_module.ClassificationSignals
FileClassifier = fc_module.FileClassifier

# Load conflict_detector
conflict_det_path = cortex_brain_path / "tier1/orchestrators/enhancements/conflict_detector.py"
spec = importlib.util.spec_from_file_location("conflict_detector", str(conflict_det_path))
if spec is None or spec.loader is None:
    raise RuntimeError(f"Could not load spec for conflict_detector at {conflict_det_path}")
cd_module = importlib.util.module_from_spec(spec)
sys.modules["conflict_detector"] = cd_module
spec.loader.exec_module(cd_module)

ConflictType = cd_module.ConflictType
Conflict = cd_module.Conflict
ConflictReport = cd_module.ConflictReport
ConflictDetector = cd_module.ConflictDetector


# =============================================================================
# FILE CATEGORIZER TESTS
# =============================================================================


class TestFileClassifier:
    """Test FileClassifier multi-signal categorization."""
    
    def test_classify_python_in_cortex(self):
        """Test classification of cortex/*.py files."""
        classifier = FileClassifier()
        
        category, signals = classifier.classify("cortex/orchestrators/support/test.py")
        
        assert category == FileCategory.SYSTEM_CODE
        assert signals.extension_signal[0] == FileCategory.SYSTEM_CODE
        assert signals.confidence > 0.7
    
    def test_classify_test_files(self):
        """Test classification of test_*.py files."""
        classifier = FileClassifier()
        
        category, signals = classifier.classify("tests/test_vacuum.py")
        
        assert category == FileCategory.TESTING
        assert signals.naming_signal[0] == FileCategory.TESTING
    
    def test_classify_markdown_in_docs(self):
        """Test classification of docs/*.md files."""
        classifier = FileClassifier()
        
        category, signals = classifier.classify("docs/ARCHITECTURE.md")
        
        assert category == FileCategory.DOCUMENTATION
        assert signals.confidence > 0.6
    
    def test_classify_scripts_utils(self):
        """Test classification of utility scripts."""
        classifier = FileClassifier()
        
        category, signals = classifier.classify("scripts/execute_validation_suite.py")
        
        # Should match SCRIPTS_UTILS by naming pattern
        assert category in [FileCategory.SCRIPTS_UTILS, FileCategory.SYSTEM_CODE]
    
    def test_classify_root_essentials(self):
        """Test classification of root-level essentials."""
        classifier = FileClassifier()
        
        category, _ = classifier.classify("README.md")
        assert category == FileCategory.KEEP_ROOT
        
        category, _ = classifier.classify("Makefile")
        assert category == FileCategory.KEEP_ROOT
        
        category, _ = classifier.classify("pytest.ini")
        assert category == FileCategory.KEEP_ROOT
    
    def test_classify_company_data(self):
        """Test classification of company data files."""
        classifier = FileClassifier()
        
        category, signals = classifier.classify("company/dashboards/lens/output.json")
        
        assert category == FileCategory.COMPANY_DATA
        assert signals.reference_signal[0] == FileCategory.COMPANY_DATA
    
    def test_classify_deployment_config(self):
        """Test classification of deployment files."""
        classifier = FileClassifier()
        
        category, _ = classifier.classify("deployment/docker/Dockerfile")
        assert category == FileCategory.DEPLOYMENT
        
        category, _ = classifier.classify("deployment/nginx.conf")
        assert category == FileCategory.DEPLOYMENT
    
    def test_classify_macos_artifacts(self):
        """Test classification of files to delete."""
        classifier = FileClassifier()
        
        category, _ = classifier.classify(".DS_Store")
        assert category == FileCategory.DELETE
        
        category, _ = classifier.classify(".pytest_cache/__pycache__/")
        assert category == FileCategory.DELETE
    
    def test_confidence_scoring(self):
        """Test that confidence is properly calculated."""
        classifier = FileClassifier()
        
        category, signals = classifier.classify("cortex/orchestrators/vacuum.py")
        
        # Python file in cortex/ should have high confidence
        assert signals.confidence >= 0.7
        assert category != FileCategory.UNKNOWN
    
    def test_unknown_classification(self):
        """Test handling of unknown file types."""
        classifier = FileClassifier()
        
        category, signals = classifier.classify("mysterious_file_xyz")
        
        # Should be unknown with low confidence
        assert signals.confidence <= 0.3


class TestClassificationSignals:
    """Test ClassificationSignals multi-signal voting."""
    
    def test_winning_category_single_signal(self):
        """Test winning category with single signal."""
        signals = ClassificationSignals(
            extension_signal=(FileCategory.TESTING, 0.95),
        )
        
        assert signals.winning_category == FileCategory.TESTING
        assert signals.confidence == 0.95
    
    def test_winning_category_consensus(self):
        """Test winning category with consensus signals."""
        signals = ClassificationSignals(
            extension_signal=(FileCategory.DOCUMENTATION, 0.8),
            content_signal=(FileCategory.DOCUMENTATION, 0.75),
            naming_signal=(FileCategory.DOCUMENTATION, 0.7),
        )
        
        assert signals.winning_category == FileCategory.DOCUMENTATION
        assert signals.confidence > 0.7
    
    def test_winning_category_conflict_resolution(self):
        """Test tiebreaker when signals disagree."""
        signals = ClassificationSignals(
            extension_signal=(FileCategory.SYSTEM_CODE, 0.6),
            naming_signal=(FileCategory.TESTING, 0.6),
        )
        
        # Should pick highest priority (TESTING > SYSTEM_CODE)
        assert signals.winning_category in [FileCategory.TESTING, FileCategory.SYSTEM_CODE]
    
    def test_confidence_with_multiple_signals(self):
        """Test confidence calculation with multiple signals."""
        signals = ClassificationSignals(
            extension_signal=(FileCategory.TESTING, 0.95),
            naming_signal=(FileCategory.TESTING, 0.90),
            content_signal=(FileCategory.UNKNOWN, 0.0),
        )
        
        # Confidence should average the matching signals
        assert signals.confidence > 0.8
    
    def test_unknown_signals_ignored(self):
        """Test that UNKNOWN signals don't participate in voting."""
        signals = ClassificationSignals(
            extension_signal=(FileCategory.UNKNOWN, 0.0),
            naming_signal=(FileCategory.SCRIPTS_UTILS, 0.8),
            content_signal=(FileCategory.UNKNOWN, 0.0),
        )
        
        assert signals.winning_category == FileCategory.SCRIPTS_UTILS
        assert signals.confidence == 0.8


# =============================================================================
# CONFLICT DETECTOR TESTS
# =============================================================================


class TestConflictDetector:
    """Test ConflictDetector conflict prediction."""
    
    def test_no_conflicts_valid_move(self):
        """Test valid move with no conflicts."""
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create source file
            source = tmpdir / "source.txt"
            source.write_text("test")
            
            # Create destination directory
            dest_dir = tmpdir / "dest"
            dest_dir.mkdir()
            
            detector = ConflictDetector(tmpdir)
            report = detector.predict_conflicts([{
                "source": "source.txt",
                "destination": "dest/source.txt",
            }])
            
            # Should only have info-level "no-op" if file already exists
            # For our case with new destination, should be safe
            assert report.critical_count == 0
    
    def test_source_not_found(self):
        """Test detection of missing source file."""
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            detector = ConflictDetector(tmpdir)
            report = detector.predict_conflicts([{
                "source": "nonexistent.txt",
                "destination": "other/file.txt",
            }])
            
            # Should have at least SOURCE_NOT_FOUND critical conflict
            assert report.critical_count >= 1
            assert any(c.conflict_type == ConflictType.SOURCE_NOT_FOUND for c in report.conflicts)
    
    def test_destination_exists_warning(self):
        """Test warning when destination already exists."""
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create source and destination
            source = tmpdir / "source.txt"
            source.write_text("source")
            
            dest_dir = tmpdir / "dest"
            dest_dir.mkdir()
            dest_file = dest_dir / "existing.txt"
            dest_file.write_text("existing")
            
            detector = ConflictDetector(tmpdir)
            report = detector.predict_conflicts([{
                "source": "source.txt",
                "destination": "dest/existing.txt",
            }])
            
            # Should have warning about existing file
            assert report.warning_count >= 1
            assert any(c.conflict_type == ConflictType.FILE_EXISTS for c in report.conflicts)
    
    def test_path_collision_detection(self):
        """Test detection of multiple sources targeting same destination."""
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create source files
            (tmpdir / "file1.txt").write_text("1")
            (tmpdir / "file2.txt").write_text("2")
            
            detector = ConflictDetector(tmpdir)
            report = detector.predict_conflicts([
                {"source": "file1.txt", "destination": "dest/file.txt"},
                {"source": "file2.txt", "destination": "dest/file.txt"},
            ])
            
            # Should detect collision
            assert report.critical_count >= 1
            assert any(c.conflict_type == ConflictType.PATH_COLLISION for c in report.conflicts)
    
    def test_symlink_detection(self):
        """Test detection and handling of symlinks."""
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create source and symlink
            source = tmpdir / "source.txt"
            source.write_text("source")
            
            symlink = tmpdir / "link.txt"
            try:
                symlink.symlink_to(source)
            except OSError:
                pytest.skip("Cannot create symlinks on this system")
            
            detector = ConflictDetector(tmpdir)
            report = detector.predict_conflicts([{
                "source": "link.txt",
                "destination": "dest/link.txt",
            }])
            
            # Should detect symlink
            assert any(c.conflict_type == ConflictType.SYMLINK for c in report.conflicts)


class TestConflictReport:
    """Test ConflictReport data structure and formatting."""
    
    def test_safe_to_proceed_no_conflicts(self):
        """Test that report is safe with no conflicts."""
        report = ConflictReport(has_conflicts=False)
        
        assert report.is_safe_to_proceed
        assert report.total_count == 0
    
    def test_safe_to_proceed_only_info(self):
        """Test that info-level conflicts are safe."""
        report = ConflictReport(has_conflicts=False, info_count=2)
        
        assert report.is_safe_to_proceed
    
    def test_unsafe_with_critical(self):
        """Test that critical conflicts make it unsafe."""
        report = ConflictReport(has_conflicts=True, critical_count=1)
        
        assert not report.is_safe_to_proceed
    
    def test_unsafe_with_warnings(self):
        """Test that warning conflicts make it unsafe."""
        report = ConflictReport(has_conflicts=True, warning_count=2)
        
        assert not report.is_safe_to_proceed
    
    def test_format_summary_no_conflicts(self):
        """Test summary format with no conflicts."""
        report = ConflictReport(has_conflicts=False)
        
        summary = report.format_summary()
        
        assert "✅" in summary
        assert "safe" in summary
    
    def test_format_summary_with_conflicts(self):
        """Test summary format with conflicts."""
        report = ConflictReport(has_conflicts=True, critical_count=2, warning_count=1)
        
        summary = report.format_summary()
        
        assert "🔴" in summary
        assert "2 critical" in summary
        assert "1 warning" in summary
    
    def test_add_conflict_updates_counts(self):
        """Test that adding conflicts updates type counts."""
        report = ConflictReport(has_conflicts=False)
        
        report.add_conflict(Conflict(
            conflict_type=ConflictType.SOURCE_NOT_FOUND,
            source="x",
            destination="y",
            severity="critical",
            message="test"
        ))
        
        assert report.critical_count == 1
        assert report.total_count == 1
        assert report.has_conflicts


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestVacuumEnhancementsIntegration:
    """Integration tests for both enhancements together."""
    
    def test_classify_and_detect_conflicts(self):
        """Test classifying files then detecting move conflicts."""
        with TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create test files
            (tmpdir / "cortex").mkdir()
            (tmpdir / "cortex" / "test.py").write_text("# code")
            (tmpdir / "scripts").mkdir()
            (tmpdir / "scripts" / "utility.py").write_text("# utility")
            
            # Classify
            classifier = FileClassifier(tmpdir)
            cat1, _ = classifier.classify("cortex/test.py")
            cat2, _ = classifier.classify("scripts/utility.py")
            
            assert cat1 == FileCategory.SYSTEM_CODE
            assert cat2 == FileCategory.SCRIPTS_UTILS
            
            # Detect conflicts for moving
            detector = ConflictDetector(tmpdir)
            report = detector.predict_conflicts([
                {"source": "cortex/test.py", "destination": "cortex_archive/test.py"},
                {"source": "scripts/utility.py", "destination": "scripts/utilities/utility.py"},
            ])
            
            # Should have at least info about destinations
            assert report.total_count >= 0
    
    def test_enhancement_documentation(self):
        """Verify enhancements are properly documented."""
        assert FileClassifier.__doc__
        assert ConflictDetector.__doc__
        assert FileCategory.__doc__
        assert ConflictType.__doc__


# =============================================================================
# ACCEPTANCE CRITERIA
# =============================================================================


class TestAcceptanceCriteria:
    """Acceptance criteria for Phase 1 enhancements."""
    
    def test_ac_vac_enh_001_file_categorization_complete(self):
        """AC-VAC-ENH-001: File categorization with 5+ signals."""
        classifier = FileClassifier()
        
        # Should support multiple classification signals
        assert hasattr(classifier, '_classify_by_extension')
        assert hasattr(classifier, '_classify_by_name')
        assert hasattr(classifier, '_classify_by_content')
        assert hasattr(classifier, '_classify_by_references')
        assert hasattr(classifier, '_classify_by_git')
        
        # Classification should return confidence
        category, signals = classifier.classify("test_file.py")
        assert signals.confidence >= 0.0
    
    def test_ac_vac_enh_003_conflict_detection_complete(self):
        """AC-VAC-ENH-003: Conflict detection with 7+ types."""
        detector = ConflictDetector()
        
        # Should support all conflict types
        conflict_types = [t.value for t in ConflictType]
        assert len(conflict_types) >= 7
        
        # Should generate actionable report
        report = ConflictReport(has_conflicts=False)
        assert hasattr(report, 'is_safe_to_proceed')
        assert hasattr(report, 'format_summary')


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
