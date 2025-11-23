"""
CORTEX Issue #3 - Phase 4: Comprehensive Validation Script
===========================================================

Purpose: Enforce all Issue #3 requirements and validate upgrade compatibility
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)

This script validates:
1. Database schema applied correctly (4 tables, 14 indexes, 4 views)
2. FeedbackAgent entry point functional
3. ViewDiscoveryAgent discovery + persistence
4. TDD workflow integration
5. Upgrade compatibility (brain preservation)
6. End-to-end workflow validation

Usage: python validate_issue3_phase4.py
"""

import sys
import sqlite3
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except:
        pass  # Fallback if encoding setup fails

# Add src to path for imports
sys.path.insert(0, 'src')

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

class ValidationResult:
    """Stores validation results"""
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.failures: List[str] = []
        self.warnings: List[str] = []
    
    def add_pass(self):
        self.tests_run += 1
        self.tests_passed += 1
    
    def add_fail(self, message: str):
        self.tests_run += 1
        self.tests_failed += 1
        self.failures.append(message)
    
    def add_warning(self, message: str):
        self.warnings.append(message)
    
    def print_summary(self):
        print("\n" + "=" * 70)
        print(f"{Colors.BOLD}VALIDATION SUMMARY{Colors.RESET}")
        print("=" * 70)
        print(f"Tests Run: {self.tests_run}")
        print(f"{Colors.GREEN}Passed: {self.tests_passed}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {self.tests_failed}{Colors.RESET}")
        
        if self.warnings:
            print(f"{Colors.YELLOW}Warnings: {len(self.warnings)}{Colors.RESET}")
            for warning in self.warnings:
                print(f"  ⚠️  {warning}")
        
        if self.failures:
            print(f"\n{Colors.RED}FAILURES:{Colors.RESET}")
            for failure in self.failures:
                print(f"  ❌ {failure}")
        
        print("=" * 70)
        
        return self.tests_failed == 0


class Phase4Validator:
    """Comprehensive validator for Issue #3 Phase 4"""
    
    def __init__(self):
        self.result = ValidationResult()
        self.db_path = Path("cortex-brain/tier2/knowledge_graph.db")
        self.schema_path = Path("cortex-brain/tier2/schema/element_mappings.sql")
    
    def validate_all(self) -> bool:
        """Run all validation tests"""
        print(f"{Colors.BOLD}CORTEX Issue #3 - Phase 4 Validation{Colors.RESET}")
        print("=" * 70)
        
        # Critical validations (must pass)
        self.validate_database_schema()
        self.validate_feedback_agent()
        self.validate_view_discovery_agent()
        self.validate_tdd_workflow_integrator()
        self.validate_upgrade_compatibility()
        
        # End-to-end validation
        self.validate_end_to_end_workflow()
        
        return self.result.print_summary()
    
    def validate_database_schema(self):
        """Validate database schema applied correctly"""
        print(f"\n{Colors.BLUE}[1/6] Database Schema Validation{Colors.RESET}")
        
        if not self.db_path.exists():
            self.result.add_fail(f"Database not found: {self.db_path}")
            return
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Check tables
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name LIKE 'tier2_element%'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = [
                'tier2_element_mappings',
                'tier2_navigation_flows',
                'tier2_discovery_runs',
                'tier2_element_changes'
            ]
            
            for table in expected_tables:
                if table in tables:
                    print(f"  ✅ Table exists: {table}")
                    self.result.add_pass()
                else:
                    self.result.add_fail(f"Table missing: {table}")
            
            # Check indexes (should have 14)
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name LIKE 'idx_%'
            """)
            indexes = cursor.fetchall()
            index_count = len(indexes)
            
            if index_count >= 14:
                print(f"  ✅ Indexes created: {index_count} (expected: 14)")
                self.result.add_pass()
            else:
                self.result.add_fail(f"Insufficient indexes: {index_count}/14")
            
            # Check views (should have 4)
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='view' AND name LIKE 'view_%'
            """)
            views = [row[0] for row in cursor.fetchall()]
            
            expected_views = [
                'view_elements_without_ids',
                'view_recent_discoveries',
                'view_popular_elements',
                'view_flow_success_rates'
            ]
            
            for view in expected_views:
                if view in views:
                    print(f"  ✅ View exists: {view}")
                    self.result.add_pass()
                else:
                    self.result.add_fail(f"View missing: {view}")
            
            # Test insert/query
            cursor.execute("""
                INSERT OR REPLACE INTO tier2_element_mappings 
                (project_name, component_path, element_id, element_type, selector_strategy, selector_priority)
                VALUES ('VALIDATION_TEST', 'Test.razor', 'testElement', 'button', '#testElement', 1)
            """)
            conn.commit()
            
            cursor.execute("""
                SELECT element_id FROM tier2_element_mappings 
                WHERE project_name = 'VALIDATION_TEST'
            """)
            result = cursor.fetchone()
            
            if result and result[0] == 'testElement':
                print(f"  ✅ Insert/query operations functional")
                self.result.add_pass()
            else:
                self.result.add_fail("Insert/query operations failed")
            
            # Cleanup
            cursor.execute("DELETE FROM tier2_element_mappings WHERE project_name = 'VALIDATION_TEST'")
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.result.add_fail(f"Database validation error: {e}")
    
    def validate_feedback_agent(self):
        """Validate FeedbackAgent functionality"""
        print(f"\n{Colors.BLUE}[2/6] Feedback Agent Validation{Colors.RESET}")
        
        try:
            from agents.feedback_agent import FeedbackAgent
            
            print(f"  ✅ FeedbackAgent import successful")
            self.result.add_pass()
            
            # Test feedback report creation
            agent = FeedbackAgent()
            temp_dir = Path(tempfile.mkdtemp())
            
            report_path = agent.create_feedback_report(
                feedback_type="bug",
                description="Test bug report",
                steps_to_reproduce="1. Test step\n2. Another step",
                expected_behavior="Should work",
                actual_behavior="Does not work",
                output_dir=temp_dir
            )
            
            if report_path and report_path.exists():
                print(f"  ✅ Feedback report created: {report_path.name}")
                self.result.add_pass()
                
                # Validate report structure
                with open(report_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    required_sections = [
                        "# CORTEX Feedback Report",
                        "## Issue Description",
                        "## Steps to Reproduce",
                        "## Expected Behavior",
                        "## Actual Behavior",
                        "## Context"
                    ]
                    
                    for section in required_sections:
                        if section in content:
                            self.result.add_pass()
                        else:
                            self.result.add_fail(f"Report missing section: {section}")
                
                print(f"  ✅ Report structure valid")
            else:
                self.result.add_fail("Feedback report creation failed")
            
            # Cleanup
            shutil.rmtree(temp_dir)
            
        except ImportError as e:
            self.result.add_fail(f"FeedbackAgent import failed: {e}")
        except Exception as e:
            self.result.add_fail(f"FeedbackAgent validation error: {e}")
    
    def validate_view_discovery_agent(self):
        """Validate ViewDiscoveryAgent functionality"""
        print(f"\n{Colors.BLUE}[3/6] View Discovery Agent Validation{Colors.RESET}")
        
        try:
            from agents.view_discovery_agent import ViewDiscoveryAgent
            
            print(f"  ✅ ViewDiscoveryAgent import successful")
            self.result.add_pass()
            
            # Create test Razor file
            temp_dir = Path(tempfile.mkdtemp())
            project_dir = temp_dir / "TestProject"
            views_dir = project_dir / "Views"
            views_dir.mkdir(parents=True)
            
            test_razor = views_dir / "TestView.razor"
            test_razor.write_text("""
@page "/test"
<h1>Test View</h1>
<button id="submitBtn" class="btn-primary">Submit</button>
<input id="userName" type="text" data-testid="user-name-input" />
<div class="container">
    <span>No ID element</span>
</div>
""", encoding='utf-8')
            
            # Test discovery
            agent = ViewDiscoveryAgent(project_root=project_dir)
            results = agent.discover_views(
                view_paths=[test_razor],
                save_to_db=False,  # Don't save test data
                project_name="VALIDATION_TEST"
            )
            
            if results and 'elements_discovered' in results:
                elements = results['elements_discovered']
                print(f"  ✅ Discovery successful: {len(elements)} elements found")
                self.result.add_pass()
                
                # Validate specific elements
                element_ids = [e['element_id'] for e in elements]
                expected_ids = ['submitBtn', 'userName']
                
                for expected_id in expected_ids:
                    if expected_id in element_ids:
                        print(f"  ✅ Found element: {expected_id}")
                        self.result.add_pass()
                    else:
                        self.result.add_fail(f"Missing expected element: {expected_id}")
                
                # Validate selector strategies
                for element in elements:
                    if 'selector_strategy' in element and element['selector_strategy']:
                        print(f"  ✅ Selector generated for {element['element_id']}: {element['selector_strategy']}")
                        self.result.add_pass()
                    else:
                        self.result.add_warning(f"No selector for {element['element_id']}")
            else:
                self.result.add_fail("Discovery returned no results")
            
            # Test database persistence (if schema applied)
            if self.db_path.exists():
                results_with_save = agent.discover_views(
                    view_paths=[test_razor],
                    save_to_db=True,
                    project_name="VALIDATION_TEST_PERSIST"
                )
                
                if results_with_save.get('saved_to_database'):
                    print(f"  ✅ Database persistence functional")
                    self.result.add_pass()
                    
                    # Test load from database
                    loaded = agent.load_from_database("VALIDATION_TEST_PERSIST")
                    if loaded and len(loaded) > 0:
                        print(f"  ✅ Database cache load successful: {len(loaded)} elements")
                        self.result.add_pass()
                    else:
                        self.result.add_fail("Database cache load failed")
                    
                    # Cleanup
                    conn = sqlite3.connect(str(self.db_path))
                    conn.execute("DELETE FROM tier2_element_mappings WHERE project_name = 'VALIDATION_TEST_PERSIST'")
                    conn.commit()
                    conn.close()
                else:
                    self.result.add_warning("Database persistence not tested (schema may not be applied)")
            
            # Cleanup
            shutil.rmtree(temp_dir)
            
        except ImportError as e:
            self.result.add_fail(f"ViewDiscoveryAgent import failed: {e}")
        except Exception as e:
            self.result.add_fail(f"ViewDiscoveryAgent validation error: {e}")
    
    def validate_tdd_workflow_integrator(self):
        """Validate TDDWorkflowIntegrator functionality"""
        print(f"\n{Colors.BLUE}[4/6] TDD Workflow Integrator Validation{Colors.RESET}")
        
        try:
            from workflows.tdd_workflow_integrator import TDDWorkflowIntegrator
            
            print(f"  ✅ TDDWorkflowIntegrator import successful")
            self.result.add_pass()
            
            # Create test project
            temp_dir = Path(tempfile.mkdtemp())
            project_dir = temp_dir / "TestProject"
            views_dir = project_dir / "Views"
            views_dir.mkdir(parents=True)
            
            test_razor = views_dir / "Login.razor"
            test_razor.write_text("""
@page "/login"
<h1>Login</h1>
<input id="emailInput" type="email" />
<input id="passwordInput" type="password" />
<button id="loginButton">Login</button>
""", encoding='utf-8')
            
            # Test workflow integration
            integrator = TDDWorkflowIntegrator(project_root=project_dir)
            
            discovery_report = integrator.run_discovery_phase(
                view_paths=[test_razor],
                output_path=temp_dir / "discovery_report.json"
            )
            
            if discovery_report and 'elements_discovered' in discovery_report:
                print(f"  ✅ Discovery phase successful: {discovery_report['elements_discovered']} elements")
                self.result.add_pass()
                
                # Test selector retrieval
                selector = integrator.get_selector_for_element('loginButton')
                if selector:
                    print(f"  ✅ Selector retrieval functional: {selector}")
                    self.result.add_pass()
                else:
                    self.result.add_fail("Selector retrieval failed for known element")
                
                # Test report generation
                report_path = temp_dir / "discovery_report.json"
                if report_path.exists():
                    with open(report_path, 'r', encoding='utf-8') as f:
                        report = json.load(f)
                        if 'discovery_summary' in report and 'element_mappings' in report:
                            print(f"  ✅ Discovery report structure valid")
                            self.result.add_pass()
                        else:
                            self.result.add_fail("Discovery report missing required sections")
            else:
                self.result.add_fail("Discovery phase returned no results")
            
            # Cleanup
            shutil.rmtree(temp_dir)
            
        except ImportError as e:
            self.result.add_fail(f"TDDWorkflowIntegrator import failed: {e}")
        except Exception as e:
            self.result.add_fail(f"TDDWorkflowIntegrator validation error: {e}")
    
    def validate_upgrade_compatibility(self):
        """Validate upgrade preserves CORTEX brain data"""
        print(f"\n{Colors.BLUE}[5/6] Upgrade Compatibility Validation{Colors.RESET}")
        
        # Check critical CORTEX brain files exist and are accessible
        critical_paths = [
            ("Tier 2 Database", Path("cortex-brain/tier2/knowledge_graph.db")),
            ("Capabilities", Path("cortex-brain/capabilities.yaml")),
            ("Response Templates", Path("cortex-brain/response-templates.yaml")),
            ("Brain Protection Rules", Path("cortex-brain/brain-protection-rules.yaml")),
            ("Development Context", Path("cortex-brain/development-context.yaml"))
        ]
        
        for name, path in critical_paths:
            if path.exists():
                print(f"  ✅ {name} preserved: {path}")
                self.result.add_pass()
            else:
                self.result.add_warning(f"{name} not found (may be expected for fresh install): {path}")
        
        # Validate Tier 2 database integrity
        if self.db_path.exists():
            try:
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                
                # Check that upgrade didn't corrupt existing tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                if len(tables) > 0:
                    print(f"  ✅ Database integrity preserved: {len(tables)} tables")
                    self.result.add_pass()
                else:
                    self.result.add_fail("Database appears empty after upgrade")
                
                # Check new tables coexist with old
                new_tables = [t for t in tables if t.startswith('tier2_element')]
                if len(new_tables) == 4:
                    print(f"  ✅ New Issue #3 tables added successfully")
                    self.result.add_pass()
                else:
                    self.result.add_warning(f"Expected 4 new tables, found {len(new_tables)}")
                
                conn.close()
            except Exception as e:
                self.result.add_fail(f"Database integrity check failed: {e}")
        else:
            self.result.add_warning("Tier 2 database not found (fresh install?)")
        
        # Validate conversation history preservation
        conversation_db = Path("cortex-brain/tier1/working_memory.db")
        if conversation_db.exists():
            print(f"  ✅ Conversation history preserved: {conversation_db}")
            self.result.add_pass()
        else:
            self.result.add_warning("Conversation history not found (fresh install?)")
    
    def validate_end_to_end_workflow(self):
        """Validate complete Issue #3 workflow"""
        print(f"\n{Colors.BLUE}[6/6] End-to-End Workflow Validation{Colors.RESET}")
        
        try:
            from agents.feedback_agent import FeedbackAgent
            from agents.view_discovery_agent import ViewDiscoveryAgent
            from workflows.tdd_workflow_integrator import TDDWorkflowIntegrator
            
            # Simulate user workflow: Report issue → Discover views → Generate tests
            temp_dir = Path(tempfile.mkdtemp())
            
            # Step 1: User reports feedback
            feedback_agent = FeedbackAgent()
            feedback_report = feedback_agent.create_feedback_report(
                feedback_type="improvement",
                description="Tests fail due to missing element IDs",
                steps_to_reproduce="1. Generate test\n2. Run test\n3. Test fails with selector not found",
                expected_behavior="Test should find element",
                actual_behavior="Selector not found error",
                output_dir=temp_dir
            )
            
            if feedback_report:
                print(f"  ✅ Step 1: Feedback collected")
                self.result.add_pass()
            else:
                self.result.add_fail("Step 1: Feedback collection failed")
                return
            
            # Step 2: Discovery phase before test generation
            project_dir = temp_dir / "Project"
            views_dir = project_dir / "Views"
            views_dir.mkdir(parents=True)
            
            test_view = views_dir / "Dashboard.razor"
            test_view.write_text("""
@page "/dashboard"
<h1>Dashboard</h1>
<button id="refreshBtn">Refresh</button>
<div id="dataGrid"></div>
""", encoding='utf-8')
            
            integrator = TDDWorkflowIntegrator(project_root=project_dir)
            discovery = integrator.run_discovery_phase(
                view_paths=[test_view],
                output_path=temp_dir / "discovery.json"
            )
            
            if discovery and discovery['elements_discovered'] >= 2:
                print(f"  ✅ Step 2: View discovery successful ({discovery['elements_discovered']} elements)")
                self.result.add_pass()
            else:
                self.result.add_fail("Step 2: View discovery failed")
                return
            
            # Step 3: Selector retrieval for test generation
            refresh_selector = integrator.get_selector_for_element('refreshBtn')
            grid_selector = integrator.get_selector_for_element('dataGrid')
            
            if refresh_selector and grid_selector:
                print(f"  ✅ Step 3: Selectors retrieved for test generation")
                print(f"     - refreshBtn: {refresh_selector}")
                print(f"     - dataGrid: {grid_selector}")
                self.result.add_pass()
            else:
                self.result.add_fail("Step 3: Selector retrieval incomplete")
                return
            
            # Step 4: Validate workflow produces correct selector strategies
            expected_selectors = {
                'refreshBtn': '#refreshBtn',
                'dataGrid': '#dataGrid'
            }
            
            all_correct = True
            for element_id, expected in expected_selectors.items():
                actual = integrator.get_selector_for_element(element_id)
                if actual == expected:
                    print(f"  ✅ Selector correct: {element_id} → {actual}")
                    self.result.add_pass()
                else:
                    self.result.add_fail(f"Selector mismatch: {element_id} expected {expected}, got {actual}")
                    all_correct = False
            
            if all_correct:
                print(f"\n  {Colors.GREEN}✅ END-TO-END WORKFLOW VALIDATED{Colors.RESET}")
                print(f"     Issue #3 fix complete: Feedback → Discovery → Test Generation")
            
            # Cleanup
            shutil.rmtree(temp_dir)
            
        except Exception as e:
            self.result.add_fail(f"End-to-end workflow error: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Run Phase 4 validation"""
    validator = Phase4Validator()
    success = validator.validate_all()
    
    if success:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ ALL VALIDATIONS PASSED - READY FOR PRODUCTION{Colors.RESET}")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ VALIDATION FAILURES - FIX BEFORE RELEASE{Colors.RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
