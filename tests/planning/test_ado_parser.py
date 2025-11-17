"""
Test ADO Template Parser
CORTEX 2.1 - Simplified ADO System

Tests for parsing, DoD generation, and SQLite storage.
"""

import pytest
import json
import sqlite3
from pathlib import Path
from src.planning.ado_parser import ADOTemplateParser


@pytest.fixture
def parser(tmp_path):
    """Create parser with temporary database."""
    db_path = tmp_path / "test_ado.db"
    return ADOTemplateParser(str(db_path))


@pytest.fixture
def sample_template(tmp_path):
    """Create sample ADO template file."""
    template_content = """# ADO Work Item Planning

## 📋 ADO Information

**ADO Number:**  
ADO-12345

**Type:** [Select ONE - delete others]
- Feature

## 🎯 Acceptance Criteria

1. User can login with email and password
2. Session persists across page refreshes  
3. Invalid credentials show clear error message
4. Forgot password link navigates to reset flow

## 📝 Technical Notes

- Integrate with existing AuthService
- Use JWT tokens for session management
- Add rate limiting to prevent brute force attacks
"""
    template_file = tmp_path / "ADO-12345-feature.md"
    template_file.write_text(template_content)
    return template_file


def test_parse_template_success(parser, sample_template):
    """Test successful template parsing."""
    parsed = parser.parse_template(sample_template)
    
    assert parsed["ado_number"] == "ADO-12345"
    assert parsed["type"] == "Feature"
    assert len(parsed["acceptance_criteria"]) == 4
    assert "login with email and password" in parsed["acceptance_criteria"][0]
    assert parsed["technical_notes"] is not None
    assert "JWT tokens" in parsed["technical_notes"]


def test_parse_template_missing_ado_number(parser, tmp_path):
    """Test error when ADO number is missing."""
    bad_template = tmp_path / "bad.md"
    bad_template.write_text("# ADO Work Item\n\nNo ADO number here!")
    
    with pytest.raises(ValueError, match="ADO number not found"):
        parser.parse_template(bad_template)


def test_parse_template_missing_type(parser, tmp_path):
    """Test error when type is not selected."""
    bad_template = tmp_path / "bad.md"
    bad_template.write_text("""
# ADO Work Item

**ADO Number:** ADO-12345
**Type:** [Select ONE - delete others]
- Bug
- Feature
- Task

## Acceptance Criteria
1. Something
""")
    
    with pytest.raises(ValueError, match="Type not selected"):
        parser.parse_template(bad_template)


def test_parse_template_no_acceptance_criteria(parser, tmp_path):
    """Test error when acceptance criteria are not filled."""
    bad_template = tmp_path / "bad.md"
    bad_template.write_text("""
# ADO Work Item

**ADO Number:** ADO-12345
**Type:** Feature

## 🎯 Acceptance Criteria

1. [First acceptance criterion]
2. [Second acceptance criterion]
""")
    
    with pytest.raises(ValueError, match="No acceptance criteria filled"):
        parser.parse_template(bad_template)


def test_generate_dod_feature(parser):
    """Test DoD generation for Feature type."""
    criteria = [
        "User can login",
        "Session persists",
        "Error messages clear"
    ]
    dod = parser.generate_dod("Feature", criteria)
    
    assert len(dod) > 0
    assert any("acceptance criteria met" in item.lower() for item in dod)
    assert any("code reviewed" in item.lower() for item in dod)
    assert any("tests" in item.lower() for item in dod)
    # First 3 items should verify AC
    assert "Verified: User can login" in dod[0]


def test_generate_dod_bug(parser):
    """Test DoD generation for Bug type."""
    criteria = ["Login fails with 500 error"]
    dod = parser.generate_dod("Bug", criteria)
    
    assert len(dod) > 0
    assert any("root cause" in item.lower() for item in dod)
    assert any("regression" in item.lower() for item in dod)
    assert any("fix" in item.lower() for item in dod)


def test_generate_dod_task(parser):
    """Test DoD generation for Task type."""
    criteria = ["Update documentation"]
    dod = parser.generate_dod("Task", criteria)
    
    assert len(dod) > 0
    assert any("completed" in item.lower() for item in dod)


def test_import_to_database(parser, sample_template):
    """Test importing parsed data to SQLite."""
    parsed = parser.parse_template(sample_template)
    ado_id = parser.import_to_database(parsed, sample_template)
    
    # Verify UUID format
    assert len(ado_id) == 36
    assert ado_id.count('-') == 4
    
    # Verify database entry
    retrieved = parser.get_ado_by_number("ADO-12345")
    assert retrieved is not None
    assert retrieved["ado_number"] == "ADO-12345"
    assert retrieved["type"] == "Feature"
    assert retrieved["status"] == "planning"
    assert len(retrieved["acceptance_criteria"]) == 4
    assert len(retrieved["generated_dod"]) > 0


def test_import_duplicate_ado_number(parser, sample_template):
    """Test error when importing duplicate ADO number."""
    parsed = parser.parse_template(sample_template)
    parser.import_to_database(parsed, sample_template)
    
    # Try to import again
    with pytest.raises(ValueError, match="already exists"):
        parser.import_to_database(parsed, sample_template)


def test_get_ado_by_number(parser, sample_template):
    """Test retrieving ADO by number."""
    parsed = parser.parse_template(sample_template)
    parser.import_to_database(parsed, sample_template)
    
    retrieved = parser.get_ado_by_number("ADO-12345")
    assert retrieved is not None
    assert retrieved["ado_number"] == "ADO-12345"
    
    # Non-existent ADO
    not_found = parser.get_ado_by_number("ADO-99999")
    assert not_found is None


def test_list_active_ados(parser, sample_template, tmp_path):
    """Test listing active ADO items."""
    # Create first ADO
    parsed1 = parser.parse_template(sample_template)
    parser.import_to_database(parsed1, sample_template)
    
    # Create second ADO
    template2 = tmp_path / "ADO-67890-bug.md"
    template2.write_text("""
# ADO Work Item

**ADO Number:** ADO-67890
**Type:** Bug

## 🎯 Acceptance Criteria

1. Login error fixed
2. Tests passing
""")
    parsed2 = parser.parse_template(template2)
    parser.import_to_database(parsed2, template2)
    
    # List active ADOs
    active = parser.list_active_ados()
    assert len(active) == 2
    ado_numbers = [ado["ado_number"] for ado in active]
    assert "ADO-12345" in ado_numbers
    assert "ADO-67890" in ado_numbers


def test_update_status(parser, sample_template):
    """Test updating ADO status."""
    parsed = parser.parse_template(sample_template)
    parser.import_to_database(parsed, sample_template)
    
    # Update to in-progress
    parser.update_status("ADO-12345", "in-progress")
    retrieved = parser.get_ado_by_number("ADO-12345")
    assert retrieved["status"] == "in-progress"
    
    # Update to completed
    parser.update_status("ADO-12345", "completed")
    retrieved = parser.get_ado_by_number("ADO-12345")
    assert retrieved["status"] == "completed"
    assert retrieved["completed_at"] is not None


def test_update_status_invalid(parser, sample_template):
    """Test error with invalid status."""
    parsed = parser.parse_template(sample_template)
    parser.import_to_database(parsed, sample_template)
    
    with pytest.raises(ValueError, match="Invalid status"):
        parser.update_status("ADO-12345", "invalid-status")


def test_dod_items_stored_separately(parser, sample_template):
    """Test that DoD items are stored in separate table."""
    parsed = parser.parse_template(sample_template)
    ado_id = parser.import_to_database(parsed, sample_template)
    
    # Check DoD items table
    with sqlite3.connect(parser.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT dod_item, is_completed FROM ado_dod_items WHERE ado_id = ?",
            (ado_id,)
        )
        dod_items = cursor.fetchall()
    
    assert len(dod_items) > 0
    # All should be uncompleted initially
    assert all(item[1] == 0 for item in dod_items)


def test_activity_log_on_creation(parser, sample_template):
    """Test that activity is logged on ADO creation."""
    parsed = parser.parse_template(sample_template)
    ado_id = parser.import_to_database(parsed, sample_template)
    
    # Check activity log
    with sqlite3.connect(parser.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT activity_type, notes FROM ado_activity WHERE ado_id = ?",
            (ado_id,)
        )
        activities = cursor.fetchall()
    
    assert len(activities) > 0
    assert activities[0][0] == "created"
    assert "ADO-12345" in activities[0][1]


def test_technical_notes_optional(parser, tmp_path):
    """Test that technical notes are optional."""
    template = tmp_path / "minimal.md"
    template.write_text("""
# ADO Work Item

**ADO Number:** ADO-11111
**Type:** Task

## 🎯 Acceptance Criteria

1. Complete the task
2. Verify completion

## 📝 Technical Notes

[Optional implementation context]
""")
    
    parsed = parser.parse_template(template)
    assert parsed["technical_notes"] is None or parsed["technical_notes"] == ""
