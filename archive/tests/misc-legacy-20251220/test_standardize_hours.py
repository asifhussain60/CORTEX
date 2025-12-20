"""
Tests for hour standardization functionality in UnifiedPlanGenerator.

Test Coverage:
- Hours only (≤8h): "4h" → "4h"
- Hours to hours+days (>8h): "16h" → "16h (2d)"
- Days to hours+days: "2d" → "16h (2d)"
- Hours+minutes to decimal: "1h 30m" → "1.5h"
- Missing values: "-" → "-"
- Complex formats: "3d 4h" → "28h (3.5d)"
"""

import pytest
from src.operations.modules.planning.unified_plan_generator import UnifiedPlanGenerator


class TestStandardizeHours:
    """Test suite for hour standardization."""

    @pytest.fixture
    def generator(self):
        """Create UnifiedPlanGenerator instance."""
        return UnifiedPlanGenerator()

    def test_hours_only_less_than_8h(self, generator):
        """Test hours ≤8h remain as hours only."""
        assert generator.standardize_hours("4h") == "4h"
        assert generator.standardize_hours("8h") == "8h"
        assert generator.standardize_hours("1h") == "1h"
        assert generator.standardize_hours("0.5h") == "0.50h"

    def test_hours_only_greater_than_8h(self, generator):
        """Test hours >8h get day notation in parentheses."""
        assert generator.standardize_hours("16h") == "16h (2d)"
        assert generator.standardize_hours("24h") == "24h (3d)"
        assert generator.standardize_hours("32h") == "32h (4d)"
        assert generator.standardize_hours("12h") == "12h (1.50d)"

    def test_days_to_hours_with_day_notation(self, generator):
        """Test days converted to hours with day notation."""
        assert generator.standardize_hours("2d") == "16h (2d)"
        assert generator.standardize_hours("1d") == "8h (1d)"
        assert generator.standardize_hours("3d") == "24h (3d)"
        assert generator.standardize_hours("0.5d") == "4h (0.5d)"

    def test_hours_and_minutes_to_decimal(self, generator):
        """Test hours+minutes converted to decimal hours."""
        assert generator.standardize_hours("1h 30m") == "1.50h"
        assert generator.standardize_hours("2h 15m") == "2.25h"
        assert generator.standardize_hours("4h 45m") == "4.75h"
        assert generator.standardize_hours("0h 30m") == "0.50h"

    def test_complex_formats(self, generator):
        """Test complex formats with days and hours."""
        assert generator.standardize_hours("3d 4h") == "28h (3.50d)"
        assert generator.standardize_hours("1d 8h") == "16h (2d)"
        assert generator.standardize_hours("2d 2h") == "18h (2.25d)"

    def test_missing_values(self, generator):
        """Test missing/invalid values return dash."""
        assert generator.standardize_hours("-") == "-"
        assert generator.standardize_hours("") == "-"
        assert generator.standardize_hours(None) == "-"

    def test_edge_cases(self, generator):
        """Test edge cases and boundary conditions."""
        # Exactly 8h boundary
        assert generator.standardize_hours("8h") == "8h"
        
        # Just over 8h
        assert generator.standardize_hours("9h") == "9h (1.12d)"
        
        # Large values
        assert generator.standardize_hours("10d") == "80h (10d)"
        
        # Fractional days
        assert generator.standardize_hours("1.5d") == "12h (1.50d)"
