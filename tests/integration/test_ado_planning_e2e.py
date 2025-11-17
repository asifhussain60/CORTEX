#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
End-to-End Integration Tests for ADO Planning System

Tests all components working together:
- Database + ADO Manager
- Template Parser + ADO Manager
- Vision API + ADO Manager
- Planning File Manager + ADO Manager
- Complete workflows (create → parse → approve → complete)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain
License: Proprietary
Repository: https://github.com/asifhussain60/CORTEX
"""

import sys
import io

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import os
import sqlite3
import tempfile
import shutil
from pathlib import Path

# Add scripts to path
scripts_path = Path(__file__).parent.parent.parent / 'scripts'
sys.path.insert(0, str(scripts_path))

from ado_manager import ADOManager
from parse_ado_template import ADOTemplateParser, update_ado_from_template
from vision_analyzer import VisionAnalyzer, ImageType
from vision_ado_integration import VisionADOIntegration
from planning_file_manager import PlanningFileManager, FileStatus, create_planning_file_for_ado


class TestADOPlanningSystem:
    """End-to-end integration tests"""
    
    def __init__(self):
        self.test_dir = Path(tempfile.mkdtemp(prefix="cortex_test_"))
        self.db_path = self.test_dir / "test_ado.db"
        self.template_dir = self.test_dir / "templates"
        self.planning_dir = self.test_dir / "planning"
        
        # Create test directories
        self.template_dir.mkdir(parents=True, exist_ok=True)
        self.planning_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database schema
        self._init_test_database()
        
        # Initialize managers
        self.ado_manager = ADOManager(str(self.db_path))
        self.parser = ADOTemplateParser()
        self.vision_analyzer = VisionAnalyzer()  # Uses mock mode by default
        self.vision_integration = VisionADOIntegration(
            ado_manager=self.ado_manager,
            vision_analyzer=self.vision_analyzer
        )
        self.file_manager = PlanningFileManager(str(self.planning_dir))
        
        self.passed = 0
        self.failed = 0
    
    def _init_test_database(self):
        """Initialize test database with schema"""
        import sqlite3
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Create tables (simplified from init_ado_database.py)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ado_work_items (
                ado_number TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                type TEXT NOT NULL,
                priority TEXT,
                status TEXT NOT NULL,
                template_file_path TEXT NOT NULL UNIQUE,
                assigned_to TEXT,
                tags TEXT,
                dor_completed INTEGER DEFAULT 0,
                dod_completed INTEGER DEFAULT 0,
                conversation_ids TEXT,
                related_file_paths TEXT,
                commit_shas TEXT,
                estimated_hours REAL,
                actual_hours REAL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_accessed TEXT NOT NULL,
                completed_at TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ado_activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ado_number TEXT NOT NULL,
                action TEXT NOT NULL,
                field_name TEXT,
                old_value TEXT,
                new_value TEXT,
                notes TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (ado_number) REFERENCES ado_work_items(ado_number)
            )
        """)
        
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS ado_search 
            USING fts5(ado_number, title, tags)
        """)
        
        # Create triggers to keep FTS5 in sync
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS ado_fts_insert AFTER INSERT ON ado_work_items BEGIN
                INSERT INTO ado_search(rowid, ado_number, title, tags)
                VALUES (new.rowid, new.ado_number, new.title, new.tags);
            END
        """)
        
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS ado_fts_update AFTER UPDATE ON ado_work_items BEGIN
                UPDATE ado_search 
                SET title = new.title, tags = new.tags
                WHERE rowid = new.rowid;
            END
        """)
        
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS ado_fts_delete AFTER DELETE ON ado_work_items BEGIN
                DELETE FROM ado_search WHERE rowid = old.rowid;
            END
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ado_status ON ado_work_items(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ado_priority ON ado_work_items(priority)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ado_created ON ado_work_items(created_at)")
        
        conn.commit()
        conn.close()
    
    def cleanup(self):
        """Clean up test directory"""
        # Close database connection first
        if hasattr(self, 'ado_manager') and self.ado_manager:
            self.ado_manager.close()
        
        # Remove test directory
        if self.test_dir.exists():
            import time
            import gc
            # Force garbage collection and wait for locks to release
            gc.collect()
            time.sleep(0.5)
            try:
                shutil.rmtree(self.test_dir)
            except PermissionError as e:
                print(f"⚠️  Warning: Could not delete test directory: {e}")
    
    def assert_true(self, condition: bool, message: str):
        """Assert that condition is true"""
        if condition:
            print(f"  ✅ {message}")
            self.passed += 1
        else:
            print(f"  ❌ {message}")
            self.failed += 1
    
    def test_1_database_operations(self):
        """Test 1: Database and ADO Manager Operations"""
        print("\n1️⃣ Testing Database and ADO Manager Operations...")
        
        # Create ADO
        ado_number = self.ado_manager.create_ado(
            ado_number="ADO-99999",
            ado_type="Feature",
            title="Test Feature",
            priority="High",
            status="planning",
            template_file_path=str(self.template_dir / "test.md")
        )
        
        self.assert_true(ado_number is not None, "ADO created successfully")
        self.assert_true(ado_number.startswith("ADO-"), "ADO number has correct format")
        
        # Retrieve ADO
        ado_item = self.ado_manager.get_ado(ado_number)
        self.assert_true(ado_item is not None, "ADO retrieved from database")
        self.assert_true(ado_item['title'] == "Test Feature", "ADO title matches")
        self.assert_true(ado_item['status'] == "planning", "ADO status matches")
        
        # Update ADO
        success = self.ado_manager.update_ado(
            ado_number,
            dor_completed=50,
            dod_completed=25
        )
        self.assert_true(success, "ADO DoR/DoD updated successfully")
        
        # Update status
        success_status = self.ado_manager.update_status(ado_number, "ready")
        self.assert_true(success_status, "ADO status updated successfully")
        
        # Verify update
        updated = self.ado_manager.get_ado(ado_number)
        self.assert_true(updated['dor_completed'] == 50, "DoR completion updated")
        self.assert_true(updated['dod_completed'] == 25, "DoD completion updated")
        self.assert_true(updated['status'] == "ready", "Status updated")
        
        # Search
        results = self.ado_manager.search_ado("Test")
        self.assert_true(len(results) > 0, "Search returns results")
        self.assert_true(results[0]['ado_number'] == ado_number, "Search finds correct ADO")
        
        return ado_number
    
    def test_2_template_parsing(self):
        """Test 2: Template Parser Integration"""
        print("\n2️⃣ Testing Template Parser Integration...")
        
        # Create test template
        template_content = """# Test ADO

**ADO Number:** ADO-TEST-123
**Title:** Test Feature
**Type:** Feature
**Priority:** High
**Status:** planning

## Definition of Ready (DoR)

- [x] Requirements documented
- [x] Dependencies identified
- [ ] Technical design approved
- [ ] Test strategy defined

## Definition of Done (DoD)

- [x] Code implemented
- [ ] Unit tests written
- [ ] Code reviewed
- [ ] Documentation updated
- [ ] Deployed to staging

## Acceptance Criteria

**Given:** User is on login page
**When:** User enters valid credentials
**Then:** User is logged in successfully

**Given:** User is logged in
**When:** User clicks logout
**Then:** User is logged out

## Risk Analysis

| Risk | Impact | Mitigation |
|------|--------|------------|
| Authentication failure | High | Implement fallback mechanism |
| Performance issues | Medium | Load testing before release |
"""
        
        template_path = self.template_dir / "test_template.md"
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        # Parse template
        parsed = self.parser.parse_file(str(template_path))
        
        self.assert_true(parsed.ado_number == "ADO-TEST-123", "ADO number extracted")
        self.assert_true(parsed.title == "Test Feature", "Title extracted")
        self.assert_true(len(parsed.dor_items) == 4, "DoR items extracted (4 found)")
        self.assert_true(len(parsed.dod_items) == 5, "DoD items extracted (5 found)")
        self.assert_true(parsed.dor_completed == 50, "DoR completion calculated (50%)")
        self.assert_true(parsed.dod_completed == 20, "DoD completion calculated (20%)")
        self.assert_true(len(parsed.acceptance_criteria) == 2, "Acceptance criteria extracted (2 found)")
        self.assert_true(len(parsed.risks) == 2, "Risks extracted (2 found)")
        
        return str(template_path)
    
    def test_3_vision_api_integration(self):
        """Test 3: Vision API Integration"""
        print("\n3️⃣ Testing Vision API Integration...")
        
        # Test UI mockup analysis (mock mode)
        result = self.vision_analyzer.analyze_image(
            "test_mockup.png",
            ImageType.UI_MOCKUP
        )
        
        self.assert_true(result is not None, "Vision API returns result")
        self.assert_true('ui_elements' in result.structured_data, "UI elements in structured data")
        self.assert_true(len(result.structured_data.get('ui_elements', [])) > 0, "UI elements extracted")
        self.assert_true(len(result.structured_data.get('acceptance_criteria', [])) > 0, "Acceptance criteria generated")
        self.assert_true(result.confidence.value != "UNCERTAIN", "Confidence score assigned")
        
        # Test vision + ADO integration
        ado_number, analysis = self.vision_integration.analyze_and_create_ado(
            "test_error.png",
            "ADO-99999",
            str(self.template_dir / "bug.md")
        )
        
        self.assert_true(ado_number is not None, "ADO created from vision analysis")
        self.assert_true(ado_number.startswith("ADO-"), "ADO number format correct")
        
        # Verify ADO was stored
        ado_item = self.ado_manager.get_ado(ado_number)
        self.assert_true(ado_item is not None, "Vision-created ADO stored in database")
        self.assert_true("vision-extracted" in ado_item.get('tags', ''), "Vision tag added")
        
        return ado_number
    
    def test_4_planning_file_lifecycle(self):
        """Test 4: Planning File Manager Lifecycle"""
        print("\n4️⃣ Testing Planning File Manager Lifecycle...")
        
        # Create planning file
        success, file_path = self.file_manager.create_planning_file(
            ado_number="ADO-FILE-TEST",
            title="Test Planning File",
            template_content="# Test\n\nThis is a test planning file.",
            status=FileStatus.PENDING
        )
        
        self.assert_true(success, "Planning file created")
        self.assert_true(Path(file_path).exists(), "Planning file exists on disk")
        
        # Check status
        status = self.file_manager.get_file_status("ADO-FILE-TEST")
        self.assert_true(status == FileStatus.PENDING, "File status is PENDING")
        
        # Move to active
        success, message = self.file_manager.move_to_status(
            "ADO-FILE-TEST",
            FileStatus.ACTIVE
        )
        self.assert_true(success, "File moved to ACTIVE")
        
        # Approve plan
        success, message = self.file_manager.approve_plan(
            "ADO-FILE-TEST",
            "test_user"
        )
        self.assert_true(success, "Plan approved")
        
        # Verify approval
        details = self.file_manager.get_plan_details("ADO-FILE-TEST")
        self.assert_true(details['status'] == "approved", "Status is approved")
        self.assert_true(details['approved_by'] == "test_user", "Approved by recorded")
        
        # Complete plan
        success, message = self.file_manager.complete_plan("ADO-FILE-TEST")
        self.assert_true(success, "Plan completed")
        
        # List completed plans
        completed = self.file_manager.list_plans_by_status(FileStatus.COMPLETED)
        self.assert_true(len(completed) > 0, "Completed plans listed")
        
        return "ADO-FILE-TEST"
    
    def test_5_end_to_end_workflow(self):
        """Test 5: Complete End-to-End Workflow"""
        print("\n5️⃣ Testing Complete End-to-End Workflow...")
        
        # Step 1: Create ADO with template
        ado_number = self.ado_manager.create_ado(
            ado_number="ADO-88888",
            ado_type="Feature",
            title="E2E Test Feature",
            priority="High",
            status="planning",
            template_file_path=str(self.template_dir / "e2e_test.md")
        )
        self.assert_true(ado_number is not None, "E2E: ADO created")
        
        # Step 2: Create planning file
        template_content = f"""# E2E Test Feature

**ADO Number:** {ado_number}
**Title:** E2E Test Feature
**Status:** planning

## Definition of Ready

- [x] Requirements documented
- [x] Design approved
- [ ] Dependencies resolved

## Definition of Done

- [ ] Code complete
- [ ] Tests pass
- [ ] Documentation updated
"""
        
        success, file_path = create_planning_file_for_ado(
            ado_number,
            "E2E Test Feature",
            "Feature",
            str(self.template_dir / "e2e_test.md"),
            manager=self.file_manager
        )
        
        # Write template content to file
        with open(self.template_dir / "e2e_test.md", 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        success, file_path = create_planning_file_for_ado(
            ado_number,
            "E2E Test Feature",
            "Feature",
            str(self.template_dir / "e2e_test.md"),
            manager=self.file_manager
        )
        self.assert_true(success, "E2E: Planning file created")
        
        # Step 3: Parse template and update ADO
        parsed = self.parser.parse_content(template_content)
        self.assert_true(parsed.dor_completed == 67, "E2E: DoR calculated (67%)")
        self.assert_true(parsed.dod_completed == 0, "E2E: DoD calculated (0%)")
        
        # Step 4: Update ADO with parsed data
        success = self.ado_manager.update_ado(
            ado_number,
            dor_completed=parsed.dor_completed,
            dod_completed=parsed.dod_completed
        )
        self.assert_true(success, "E2E: ADO updated with parsed data")
        
        # Step 5: Approve and complete
        success, _ = self.file_manager.approve_plan(ado_number, "e2e_test")
        self.assert_true(success, "E2E: Plan approved")
        
        success = self.ado_manager.update_status(ado_number, "in-progress")
        self.assert_true(success, "E2E: ADO status updated to in-progress")
        
        success = self.ado_manager.update_ado(ado_number, dod_completed=100)
        self.assert_true(success, "E2E: DoD completed")
        
        success = self.ado_manager.update_status(ado_number, "completed")
        self.assert_true(success, "E2E: ADO completed")
        
        success, _ = self.file_manager.complete_plan(ado_number)
        self.assert_true(success, "E2E: Planning file completed")
        
        # Verify final state
        final_ado = self.ado_manager.get_ado(ado_number)
        self.assert_true(final_ado['status'] == "completed", "E2E: Final ADO status is completed")
        self.assert_true(final_ado['dod_completed'] == 100, "E2E: Final DoD is 100%")
        
        final_file_status = self.file_manager.get_file_status(ado_number)
        self.assert_true(final_file_status == FileStatus.COMPLETED, "E2E: Final file status is completed")
        
        return ado_number
    
    def run_all_tests(self):
        """Run all integration tests"""
        print("=" * 70)
        print("ADO Planning System - End-to-End Integration Tests")
        print("=" * 70)
        
        try:
            self.test_1_database_operations()
            self.test_2_template_parsing()
            self.test_3_vision_api_integration()
            self.test_4_planning_file_lifecycle()
            self.test_5_end_to_end_workflow()
            
            print("\n" + "=" * 70)
            print(f"📊 Test Results: {self.passed} passed, {self.failed} failed")
            print("=" * 70)
            
            if self.failed == 0:
                print("\n✅ All integration tests passed!")
                return True
            else:
                print(f"\n❌ {self.failed} test(s) failed")
                return False
                
        finally:
            self.cleanup()
            print(f"\n🧹 Cleaned up test directory: {self.test_dir}")


def main():
    """Run integration tests"""
    tester = TestADOPlanningSystem()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
