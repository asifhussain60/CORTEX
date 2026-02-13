"""
Tests for BlindSpotDetector.

Validates detection of untested code paths, error handlers, and dead code.
"""

import pytest
from pathlib import Path
from typing import List, Set
from cortex.orchestrators.intelligence.blind_spot_detector import (
    BlindSpotDetector,
    BlindSpot,
    BlindSpotType,
    CoverageData,
)


class TestBlindSpotDetectorInitialization:
    """Test BlindSpotDetector initialization."""

    def test_detector_initialization_default(self):
        """Test detector initializes with default configuration."""
        detector = BlindSpotDetector()
        
        assert detector is not None
        assert detector.min_coverage_threshold == 80.0
        assert detector.include_dead_code is True

    def test_detector_initialization_custom_threshold(self):
        """Test detector initializes with custom coverage threshold."""
        detector = BlindSpotDetector(min_coverage_threshold=90.0)
        
        assert detector.min_coverage_threshold == 90.0

    def test_detector_initialization_invalid_threshold(self):
        """Test detector rejects invalid coverage threshold."""
        with pytest.raises(ValueError, match="Coverage threshold must be between 0 and 100"):
            BlindSpotDetector(min_coverage_threshold=150.0)


class TestFindUncoveredBranches:
    """Test finding uncovered code branches."""

    def test_find_uncovered_branches_with_gaps(self):
        """Test detection of uncovered branches in code with gaps."""
        detector = BlindSpotDetector()
        coverage_data = CoverageData(
            file_path=Path("cortex/example.py"),
            covered_lines={1, 2, 3, 5, 6},
            missing_lines={4, 7, 8, 9},
            branch_coverage=0.60,  # 60% branch coverage
        )
        
        blind_spots = detector.find_uncovered_branches(coverage_data)
        
        assert len(blind_spots) > 0
        assert all(spot.type == BlindSpotType.UNCOVERED_BRANCH for spot in blind_spots)
        assert all(spot.file_path == Path("cortex/example.py") for spot in blind_spots)

    def test_find_uncovered_branches_fully_covered(self):
        """Test no blind spots when branches are fully covered."""
        detector = BlindSpotDetector(min_coverage_threshold=80.0)
        coverage_data = CoverageData(
            file_path=Path("cortex/example.py"),
            covered_lines={1, 2, 3, 4, 5},
            missing_lines=set(),
            branch_coverage=1.0,  # 100% branch coverage
        )
        
        blind_spots = detector.find_uncovered_branches(coverage_data)
        
        assert len(blind_spots) == 0

    def test_find_uncovered_branches_threshold_filtering(self):
        """Test threshold filtering excludes well-covered files."""
        detector = BlindSpotDetector(min_coverage_threshold=90.0)
        coverage_data = CoverageData(
            file_path=Path("cortex/example.py"),
            covered_lines={1, 2, 3, 4, 5, 6, 7, 8, 9},
            missing_lines={10},  # 90% coverage
            branch_coverage=0.90,
        )
        
        blind_spots = detector.find_uncovered_branches(coverage_data)
        
        # Should not flag files meeting threshold
        assert len(blind_spots) == 0


class TestFindUntestedErrorHandlers:
    """Test finding untested error handlers."""

    def test_find_untested_error_handlers_with_gaps(self):
        """Test detection of untested except blocks."""
        detector = BlindSpotDetector()
        file_content = """
def process_data(data):
    try:
        result = validate(data)
    except ValueError:
        log_error("Validation failed")  # Line 5 - untested
    except KeyError:
        log_error("Missing key")  # Line 7 - untested
    return result
"""
        coverage_data = CoverageData(
            file_path=Path("cortex/processor.py"),
            covered_lines={1, 2, 3, 4, 8},
            missing_lines={5, 7},  # except blocks not covered
            branch_coverage=0.50,
        )
        
        blind_spots = detector.find_untested_error_handlers(
            coverage_data, file_content
        )
        
        assert len(blind_spots) >= 2
        assert all(
            spot.type == BlindSpotType.UNTESTED_ERROR_HANDLER 
            for spot in blind_spots
        )
        assert any("ValueError" in spot.description for spot in blind_spots)
        assert any("KeyError" in spot.description for spot in blind_spots)

    def test_find_untested_error_handlers_all_tested(self):
        """Test no blind spots when error handlers are tested."""
        detector = BlindSpotDetector()
        file_content = """
def process_data(data):
    try:
        result = validate(data)
    except ValueError:
        log_error("Validation failed")
    return result
"""
        coverage_data = CoverageData(
            file_path=Path("cortex/processor.py"),
            covered_lines={1, 2, 3, 4, 5, 6},
            missing_lines=set(),
            branch_coverage=1.0,
        )
        
        blind_spots = detector.find_untested_error_handlers(
            coverage_data, file_content
        )
        
        assert len(blind_spots) == 0


class TestFindDeadCodePaths:
    """Test finding dead code paths."""

    def test_find_dead_code_with_unreachable_blocks(self):
        """Test detection of dead code after return statements."""
        detector = BlindSpotDetector()
        file_content = """
def calculate(x):
    if x < 0:
        return -1
        print("Never executed")  # Line 5 - dead code
    return x * 2
"""
        coverage_data = CoverageData(
            file_path=Path("cortex/calculator.py"),
            covered_lines={1, 2, 3, 4, 6},
            missing_lines={5},  # Line 5 (print statement) is uncovered dead code
            branch_coverage=0.75,
        )
        
        blind_spots = detector.find_dead_code_paths(coverage_data, file_content)
        
        assert len(blind_spots) > 0
        assert all(spot.type == BlindSpotType.DEAD_CODE for spot in blind_spots)


    def test_find_dead_code_disabled_detection(self):
        """Test dead code detection can be disabled."""
        detector = BlindSpotDetector(include_dead_code=False)
        file_content = """
def calculate(x):
    return x
    print("Dead code")
"""
        coverage_data = CoverageData(
            file_path=Path("cortex/calculator.py"),
            covered_lines={1, 2},
            missing_lines={3},
            branch_coverage=1.0,
        )
        
        blind_spots = detector.find_dead_code_paths(coverage_data, file_content)
        
        assert len(blind_spots) == 0


class TestAnalyzeFile:
    """Test comprehensive file analysis."""

    def test_analyze_file_multiple_blind_spot_types(self):
        """Test file analysis detects multiple blind spot types."""
        detector = BlindSpotDetector()
        file_content = """
def process(data):
    try:
        if data:
            return validate(data)
        else:
            return None  # Uncovered branch (line 7)
    except ValueError:
        log_error("Failed")  # Untested error handler (line 9)
    return -1
    print("Dead code")  # Dead code (line 11)
"""
        coverage_data = CoverageData(
            file_path=Path("cortex/processor.py"),
            covered_lines={1, 2, 3, 4, 5, 10},
            missing_lines={7, 9, 11},  # else branch, except handler, dead code
            branch_coverage=0.50,
        )
        
        blind_spots = detector.analyze_file(coverage_data, file_content)
        
        # Should find all three types
        types_found = {spot.type for spot in blind_spots}
        assert BlindSpotType.UNCOVERED_BRANCH in types_found
        assert BlindSpotType.UNTESTED_ERROR_HANDLER in types_found
        assert BlindSpotType.DEAD_CODE in types_found

    def test_analyze_file_clean_code(self):
        """Test file analysis returns empty for clean code."""
        detector = BlindSpotDetector()
        file_content = """
def add(a, b):
    return a + b
"""
        coverage_data = CoverageData(
            file_path=Path("cortex/math.py"),
            covered_lines={1, 2},
            missing_lines=set(),
            branch_coverage=1.0,
        )
        
        blind_spots = detector.analyze_file(coverage_data, file_content)
        
        assert len(blind_spots) == 0
