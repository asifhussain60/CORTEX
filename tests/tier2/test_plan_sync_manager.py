"""
Tests for Planning Two-Way Sync Manager

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import time
from pathlib import Path
from src.operations.modules.planning.plan_sync_manager import PlanSyncManager, PlanningFileWatcher


@pytest.fixture
def temp_planning_dir():
    """Create temporary planning directory structure"""
    with tempfile.TemporaryDirectory() as tmpdir:
        planning_root = Path(tmpdir) / "cortex-brain" / "documents" / "planning"
        
        # Create structure
        (planning_root / "features" / "active").mkdir(parents=True)
        (planning_root / "features" / "approved").mkdir(parents=True)
        (planning_root / "ado" / "active").mkdir(parents=True)
        
        yield planning_root


@pytest.fixture
def temp_db():
    """Create temporary database"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    yield db_path
    
    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def sync_manager(temp_db, temp_planning_dir):
    """Create PlanSyncManager instance"""
    manager = PlanSyncManager(db_path=temp_db, planning_root=temp_planning_dir)
    yield manager
    
    # Cleanup: Close any open database connections
    if manager.observer:
        manager.stop_file_watcher()
    
    import sqlite3
    import time
    # Force close all connections
    try:
        conn = sqlite3.connect(str(manager.db_path))
        conn.close()
    except:
        pass
    
    # Wait a moment for cleanup
    time.sleep(0.1)


def test_database_initialization(sync_manager):
    """Test database schema creation"""
    import sqlite3
    
    conn = sqlite3.connect(str(sync_manager.db_path))
    cursor = conn.cursor()
    
    # Check tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    assert 'plans' in tables
    
    # Check indexes exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
    indexes = [row[0] for row in cursor.fetchall()]
    
    assert 'idx_plans_status' in indexes
    assert 'idx_plans_type' in indexes
    
    conn.close()


def test_sync_file_to_database(sync_manager, temp_planning_dir):
    """Test syncing file changes to database"""
    # Create planning file
    file_path = temp_planning_dir / "features" / "active" / "PLAN-test-authentication.md"
    file_path.write_text("""# Authentication Feature

**Status:** Active

## Overview
Implement user authentication with JWT tokens
""", encoding='utf-8')
    
    # Sync to database
    result = sync_manager.sync_file_to_database(file_path)
    
    assert result['success'] is True
    assert result['action'] in ['created', 'updated']
    assert 'plan_id' in result
    
    # Verify in database
    import sqlite3
    conn = sqlite3.connect(str(sync_manager.db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM plans WHERE file_path = ?", (str(file_path),))
    plan = cursor.fetchone()
    
    assert plan is not None
    assert plan['title'] == 'Authentication Feature'
    assert plan['status'] == 'active'
    assert plan['plan_type'] == 'feature'
    
    conn.close()


def test_sync_database_to_file(sync_manager, temp_planning_dir):
    """Test syncing database status to file"""
    # Create file
    file_path = temp_planning_dir / "features" / "active" / "PLAN-test-dashboard.md"
    file_path.write_text("""# Dashboard Feature

**Status:** Active

## Overview
Create user dashboard
""", encoding='utf-8')
    
    # Sync to DB first
    sync_result = sync_manager.sync_file_to_database(file_path)
    plan_id = sync_result['plan_id']
    
    # Update DB status
    import sqlite3
    conn = sqlite3.connect(str(sync_manager.db_path))
    cursor = conn.cursor()
    cursor.execute("UPDATE plans SET status = ? WHERE plan_id = ?", ('approved', plan_id))
    conn.commit()
    conn.close()
    
    # Sync back to file
    result = sync_manager.sync_database_to_file(plan_id)
    
    assert result['success'] is True
    
    # Verify file updated
    content = file_path.read_text(encoding='utf-8')
    assert '**Status:** Approved' in content


def test_resolve_plan_by_name(sync_manager, temp_planning_dir):
    """Test finding plan by name"""
    # Create file
    file_path = temp_planning_dir / "features" / "active" / "PLAN-test-search-feature.md"
    file_path.write_text("""# Search Feature

**Status:** Active

## Overview
Add search functionality
""", encoding='utf-8')
    
    # Sync to DB
    sync_manager.sync_file_to_database(file_path)
    
    # Search by partial name
    result = sync_manager.resolve_plan_by_name("search")
    
    assert result is not None
    assert 'Search Feature' in result['title']
    assert result['status'] == 'active'
    assert result['file_path'] == str(file_path)


def test_resolve_plan_filesystem_fallback(sync_manager, temp_planning_dir):
    """Test filesystem fallback when not in database"""
    # Create file WITHOUT syncing to DB
    file_path = temp_planning_dir / "features" / "active" / "PLAN-test-orphan.md"
    file_path.write_text("""# Orphan Feature

**Status:** Active

## Overview
Not in database
""", encoding='utf-8')
    
    # Search should find via filesystem
    result = sync_manager.resolve_plan_by_name("orphan")
    
    assert result is not None
    assert 'Orphan Feature' in result['title']
    assert result['source'] == 'filesystem'


def test_validate_sync_integrity_orphaned_db_record(sync_manager, temp_planning_dir):
    """Test detecting orphaned database records"""
    # Create file and sync
    file_path = temp_planning_dir / "features" / "active" / "PLAN-test-deleted.md"
    file_path.write_text("""# Deleted Feature

**Status:** Active
""", encoding='utf-8')
    
    sync_manager.sync_file_to_database(file_path)
    
    # Delete file
    file_path.unlink()
    
    # Validate integrity
    report = sync_manager.validate_sync_integrity()
    
    assert len(report['orphaned_db_records']) == 1
    assert report['issues_found'] >= 1


def test_validate_sync_integrity_orphaned_file(sync_manager, temp_planning_dir):
    """Test detecting orphaned files"""
    # Create file WITHOUT syncing
    file_path = temp_planning_dir / "features" / "active" / "PLAN-test-orphan-file.md"
    file_path.write_text("""# Orphan File

**Status:** Active
""", encoding='utf-8')
    
    # Validate integrity
    report = sync_manager.validate_sync_integrity()
    
    assert len(report['orphaned_files']) >= 1
    assert str(file_path) in report['orphaned_files']


def test_validate_sync_integrity_status_divergence(sync_manager, temp_planning_dir):
    """Test detecting status divergence"""
    # Create file and sync
    file_path = temp_planning_dir / "features" / "active" / "PLAN-test-diverge.md"
    file_path.write_text("""# Divergent Feature

**Status:** Active
""", encoding='utf-8')
    
    sync_result = sync_manager.sync_file_to_database(file_path)
    plan_id = sync_result['plan_id']
    
    # Update DB status
    import sqlite3
    conn = sqlite3.connect(str(sync_manager.db_path))
    cursor = conn.cursor()
    cursor.execute("UPDATE plans SET status = ? WHERE plan_id = ?", ('approved', plan_id))
    conn.commit()
    conn.close()
    
    # File still says "active"
    # Validate should detect divergence
    report = sync_manager.validate_sync_integrity()
    
    assert len(report['status_divergence']) >= 1


def test_file_watcher_start_stop(sync_manager, temp_planning_dir):
    """Test file watcher lifecycle"""
    # Start watcher
    sync_manager.start_file_watcher()
    
    assert sync_manager.observer is not None
    assert sync_manager.watcher is not None
    
    # Stop watcher
    sync_manager.stop_file_watcher()
    
    assert sync_manager.observer is None


def test_extract_file_metadata(sync_manager, temp_planning_dir):
    """Test metadata extraction from file"""
    # Create file
    file_path = temp_planning_dir / "ado" / "active" / "ADO-12345-test-feature.md"
    file_path.write_text("""# ADO-12345: Test Feature

**Status:** Active

## Overview
Test feature
""", encoding='utf-8')
    
    # Extract metadata
    metadata = sync_manager._extract_file_metadata(file_path)
    
    assert metadata is not None
    assert 'ADO-12345' in metadata['title']
    assert metadata['status'] == 'active'
    assert metadata['plan_type'] == 'ado'


def test_update_file_status(sync_manager):
    """Test updating status in file content"""
    content = """# Test Feature

**Status:** Active

## Overview
Test content
"""
    
    # Update to approved
    updated = sync_manager._update_file_status(content, 'approved')
    
    assert '**Status:** Approved' in updated
    assert '**Status:** Active' not in updated


def test_file_watcher_detects_modification(sync_manager, temp_planning_dir):
    """Test file watcher detects and syncs modifications"""
    # Create file
    file_path = temp_planning_dir / "features" / "active" / "PLAN-test-watch.md"
    file_path.write_text("""# Watch Test

**Status:** Active
""", encoding='utf-8')
    
    # Sync initially
    sync_manager.sync_file_to_database(file_path)
    
    # Start watcher
    sync_manager.start_file_watcher()
    
    # Modify file
    file_path.write_text("""# Watch Test - Modified

**Status:** Active

## New Section
Added content
""", encoding='utf-8')
    
    # Wait for watcher to trigger (debounce + processing)
    time.sleep(2)
    
    # Check database updated
    import sqlite3
    conn = sqlite3.connect(str(sync_manager.db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT title FROM plans WHERE file_path = ?", (str(file_path),))
    plan = cursor.fetchone()
    
    assert plan is not None
    assert 'Modified' in plan['title']
    
    conn.close()
    
    # Stop watcher
    sync_manager.stop_file_watcher()


def test_sync_nonexistent_file(sync_manager):
    """Test syncing nonexistent file returns error"""
    result = sync_manager.sync_file_to_database(Path("/nonexistent/file.md"))
    
    assert result['success'] is False
    assert 'error' in result


def test_sync_database_to_nonexistent_file(sync_manager):
    """Test syncing to nonexistent file returns error"""
    # Insert fake plan
    import sqlite3
    conn = sqlite3.connect(str(sync_manager.db_path))
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO plans (plan_id, title, file_path, status, plan_type)
        VALUES (?, ?, ?, ?, ?)
    """, ('fake_plan', 'Fake Plan', '/nonexistent/file.md', 'active', 'feature'))
    conn.commit()
    conn.close()
    
    result = sync_manager.sync_database_to_file('fake_plan')
    
    assert result['success'] is False
    assert 'error' in result
