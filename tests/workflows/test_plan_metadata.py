"""
Tests for Plan Metadata extraction system.

Tests YAML frontmatter parsing from Markdown plan files.
"""
import pytest
from pathlib import Path
from datetime import datetime
from src.workflows.plan_metadata import PlanMetadata, PlanMetadataExtractor, PlanMetadataError


class TestPlanMetadataModel:
    """Test PlanMetadata data model."""
    
    def test_plan_metadata_initialization(self):
        """Should initialize with all required fields."""
        metadata = PlanMetadata(
            plan_id="TEST-001",
            title="Test Plan",
            status="proposed",
            priority="high",
            created_date=datetime(2025, 12, 3),
            estimated_hours=10
        )
        
        assert metadata.plan_id == "TEST-001"
        assert metadata.title == "Test Plan"
        assert metadata.status == "proposed"
        assert metadata.priority == "high"
        assert metadata.created_date == datetime(2025, 12, 3)
        assert metadata.estimated_hours == 10
    
    def test_plan_metadata_with_optional_fields(self):
        """Should support optional fields."""
        metadata = PlanMetadata(
            plan_id="TEST-001",
            title="Test Plan",
            status="in-progress",
            priority="medium",
            created_date=datetime(2025, 12, 3),
            estimated_hours=20,
            updated_date=datetime(2025, 12, 4),
            actual_hours=15,
            completion_percentage=75,
            assigned_to="Developer"
        )
        
        assert metadata.updated_date == datetime(2025, 12, 4)
        assert metadata.actual_hours == 15
        assert metadata.completion_percentage == 75
        assert metadata.assigned_to == "Developer"


class TestPlanMetadataExtractor:
    """Test PlanMetadataExtractor functionality."""
    
    def test_extract_from_valid_frontmatter(self, tmp_path):
        """Should extract metadata from valid YAML frontmatter."""
        plan_file = tmp_path / "test-plan.md"
        plan_file.write_text("""---
plan_id: TEST-001
title: Test Plan
status: proposed
priority: high
created_date: 2025-12-03T00:00:00Z
estimated_hours: 10
---

# Test Plan Content

This is a test plan.
""")
        
        extractor = PlanMetadataExtractor()
        metadata = extractor.extract(plan_file)
        
        assert metadata.plan_id == "TEST-001"
        assert metadata.title == "Test Plan"
        assert metadata.status == "proposed"
        assert metadata.priority == "high"
        assert metadata.estimated_hours == 10
    
    def test_extract_with_optional_fields(self, tmp_path):
        """Should extract optional fields when present."""
        plan_file = tmp_path / "test-plan.md"
        plan_file.write_text("""---
plan_id: TEST-002
title: Advanced Plan
status: in-progress
priority: medium
created_date: 2025-12-03T00:00:00Z
updated_date: 2025-12-04T00:00:00Z
estimated_hours: 20
actual_hours: 15
completion_percentage: 75
assigned_to: Developer
tags: [feature, enhancement]
---

# Content here
""")
        
        extractor = PlanMetadataExtractor()
        metadata = extractor.extract(plan_file)
        
        assert metadata.actual_hours == 15
        assert metadata.completion_percentage == 75
        assert metadata.assigned_to == "Developer"
    
    def test_extract_fails_on_missing_frontmatter(self, tmp_path):
        """Should raise error when no frontmatter found."""
        plan_file = tmp_path / "no-frontmatter.md"
        plan_file.write_text("# Just a regular markdown file\n\nNo frontmatter here.")
        
        extractor = PlanMetadataExtractor()
        
        with pytest.raises(PlanMetadataError, match="No YAML frontmatter found"):
            extractor.extract(plan_file)
    
    def test_extract_fails_on_invalid_yaml(self, tmp_path):
        """Should raise error on malformed YAML."""
        plan_file = tmp_path / "bad-yaml.md"
        plan_file.write_text("""---
plan_id: TEST-003
title: Bad Plan
status: [unclosed array
---

# Content
""")
        
        extractor = PlanMetadataExtractor()
        
        with pytest.raises(PlanMetadataError, match="Invalid YAML"):
            extractor.extract(plan_file)
    
    def test_extract_fails_on_missing_required_field(self, tmp_path):
        """Should raise error when required field missing."""
        plan_file = tmp_path / "missing-field.md"
        plan_file.write_text("""---
plan_id: TEST-004
title: Incomplete Plan
status: proposed
# Missing: priority, created_date, estimated_hours
---

# Content
""")
        
        extractor = PlanMetadataExtractor()
        
        with pytest.raises(PlanMetadataError, match="Missing required field"):
            extractor.extract(plan_file)
    
    def test_extract_handles_datetime_formats(self, tmp_path):
        """Should parse multiple datetime formats."""
        plan_file = tmp_path / "datetime-formats.md"
        plan_file.write_text("""---
plan_id: TEST-005
title: DateTime Test
status: proposed
priority: low
created_date: 2025-12-03
estimated_hours: 5
---

# Content
""")
        
        extractor = PlanMetadataExtractor()
        metadata = extractor.extract(plan_file)
        
        assert metadata.created_date.year == 2025
        assert metadata.created_date.month == 12
        assert metadata.created_date.day == 3
    
    def test_extract_validates_status_enum(self, tmp_path):
        """Should validate status is one of allowed values."""
        plan_file = tmp_path / "invalid-status.md"
        plan_file.write_text("""---
plan_id: TEST-006
title: Invalid Status
status: invalid_status
priority: high
created_date: 2025-12-03T00:00:00Z
estimated_hours: 10
---

# Content
""")
        
        extractor = PlanMetadataExtractor()
        
        with pytest.raises(PlanMetadataError, match="Invalid status"):
            extractor.extract(plan_file)
    
    def test_extract_validates_priority_enum(self, tmp_path):
        """Should validate priority is one of allowed values."""
        plan_file = tmp_path / "invalid-priority.md"
        plan_file.write_text("""---
plan_id: TEST-007
title: Invalid Priority
status: proposed
priority: invalid_priority
created_date: 2025-12-03T00:00:00Z
estimated_hours: 10
---

# Content
""")
        
        extractor = PlanMetadataExtractor()
        
        with pytest.raises(PlanMetadataError, match="Invalid priority"):
            extractor.extract(plan_file)
    
    def test_extract_validates_completion_percentage(self, tmp_path):
        """Should validate completion_percentage is 0-100."""
        plan_file = tmp_path / "invalid-completion.md"
        plan_file.write_text("""---
plan_id: TEST-008
title: Invalid Completion
status: in-progress
priority: high
created_date: 2025-12-03T00:00:00Z
estimated_hours: 10
completion_percentage: 150
---

# Content
""")
        
        extractor = PlanMetadataExtractor()
        
        with pytest.raises(PlanMetadataError, match="Completion percentage must be 0-100"):
            extractor.extract(plan_file)
    
    def test_extract_file_not_found(self):
        """Should raise error when file doesn't exist."""
        extractor = PlanMetadataExtractor()
        
        with pytest.raises(PlanMetadataError, match="File not found"):
            extractor.extract(Path("/nonexistent/file.md"))
    
    def test_to_dict_conversion(self, tmp_path):
        """Should convert metadata to dictionary."""
        plan_file = tmp_path / "test-plan.md"
        plan_file.write_text("""---
plan_id: TEST-009
title: Dict Test
status: proposed
priority: high
created_date: 2025-12-03T00:00:00Z
estimated_hours: 10
---

# Content
""")
        
        extractor = PlanMetadataExtractor()
        metadata = extractor.extract(plan_file)
        metadata_dict = metadata.to_dict()
        
        assert isinstance(metadata_dict, dict)
        assert metadata_dict["plan_id"] == "TEST-009"
        assert metadata_dict["title"] == "Dict Test"
        assert metadata_dict["status"] == "proposed"
