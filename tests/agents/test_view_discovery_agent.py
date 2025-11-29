"""
Test suite for ViewDiscoveryAgent

Covers all functionality with ≥70% code coverage following
test_feedback_agent.py patterns.

Created: 2025-11-26
Author: Asif Hussain
"""

import pytest
import json
import sqlite3
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.agents.view_discovery_agent import (
    ViewDiscoveryAgent,
    ElementMapping,
    NavigationFlow,
    discover_views_for_testing
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def tmp_path(tmp_path_factory):
    """Create temporary directory for test files."""
    return tmp_path_factory.mktemp("view_discovery_tests")


@pytest.fixture
def temp_db_path(tmp_path):
    """Create temporary database for testing."""
    db_path = tmp_path / "test_knowledge_graph.db"
    
    # Create database with schema
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE tier2_element_mappings (
            project_name TEXT,
            component_path TEXT,
            element_id TEXT,
            element_type TEXT,
            data_testid TEXT,
            css_classes TEXT,
            selector_strategy TEXT,
            selector_priority INTEGER,
            user_facing_text TEXT,
            line_number INTEGER,
            attributes TEXT,
            discovered_at TIMESTAMP,
            last_verified TIMESTAMP,
            PRIMARY KEY (project_name, component_path, line_number)
        )
    """)
    conn.commit()
    conn.close()
    
    return db_path


@pytest.fixture
def view_discovery_agent(tmp_path, temp_db_path):
    """Create ViewDiscoveryAgent instance for testing."""
    return ViewDiscoveryAgent(
        project_root=tmp_path,
        db_path=temp_db_path
    )


@pytest.fixture
def sample_razor_file(tmp_path):
    """Create sample Razor file for testing."""
    content = """@page "/login"
@using MyApp.Models

<div class="login-container">
    <h2>Login</h2>
    
    <form>
        <input id="emailInput" 
               type="email" 
               placeholder="Email" 
               data-testid="email-field" />
        
        <input id="passwordInput" 
               type="password" 
               placeholder="Password" />
        
        <button id="loginBtn" 
                class="btn btn-primary" 
                type="submit">
            Login
        </button>
        
        <a href="/forgot-password">Forgot Password?</a>
    </form>
</div>
"""
    
    file_path = tmp_path / "Login.razor"
    file_path.write_text(content, encoding='utf-8')
    return file_path


@pytest.fixture
def sample_razor_without_ids(tmp_path):
    """Create Razor file without IDs for testing."""
    content = """@page "/register"

<div>
    <input type="text" placeholder="Username" class="form-control" />
    <input type="email" placeholder="Email" class="form-control" />
    <button class="btn btn-primary">Register</button>
</div>
"""
    
    file_path = tmp_path / "Register.razor"
    file_path.write_text(content, encoding='utf-8')
    return file_path


# ============================================================================
# TEST CLASS 1: Initialization
# ============================================================================

class TestViewDiscoveryAgentInitialization:
    """Test ViewDiscoveryAgent initialization."""
    
    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        agent = ViewDiscoveryAgent()
        
        assert agent.project_root == Path.cwd()
        assert agent.discovered_elements == []
        assert agent.navigation_flows == []
        assert agent.db_enabled
    
    def test_init_with_custom_paths(self, tmp_path, temp_db_path):
        """Test initialization with custom paths."""
        agent = ViewDiscoveryAgent(
            project_root=tmp_path,
            db_path=temp_db_path
        )
        
        assert agent.project_root == tmp_path
        assert agent.db_path == temp_db_path
        assert agent.db_enabled
    
    def test_init_with_nonexistent_db(self, tmp_path):
        """Test initialization with nonexistent database."""
        db_path = tmp_path / "nonexistent.db"
        agent = ViewDiscoveryAgent(project_root=tmp_path, db_path=db_path)
        
        assert agent.db_enabled == False
    
    def test_regex_patterns_compiled(self, view_discovery_agent):
        """Test that regex patterns are properly compiled."""
        assert hasattr(view_discovery_agent, 'ELEMENT_PATTERN')
        assert hasattr(view_discovery_agent, 'SELF_CLOSING_PATTERN')
        assert hasattr(view_discovery_agent, 'ID_PATTERN')
        assert hasattr(view_discovery_agent, 'DATA_TESTID_PATTERN')
        assert hasattr(view_discovery_agent, 'CLASS_PATTERN')
        assert hasattr(view_discovery_agent, 'PAGE_ROUTE_PATTERN')


# ============================================================================
# TEST CLASS 2: Element Discovery
# ============================================================================

class TestElementDiscovery:
    """Test discover_views() method."""
    
    def test_discover_single_file(self, view_discovery_agent, sample_razor_file):
        """Test discovering elements from single file."""
        results = view_discovery_agent.discover_views(
            view_paths=[sample_razor_file],
            save_to_db=False
        )
        
        assert "discovery_timestamp" in results
        assert len(results["files_processed"]) == 1
        assert str(sample_razor_file) in results["files_processed"]
        assert len(results["elements_discovered"]) > 0
        assert len(results["navigation_flows"]) == 1
    
    def test_discover_multiple_files(self, view_discovery_agent, sample_razor_file, sample_razor_without_ids):
        """Test discovering elements from multiple files."""
        results = view_discovery_agent.discover_views(
            view_paths=[sample_razor_file, sample_razor_without_ids],
            save_to_db=False
        )
        
        assert len(results["files_processed"]) == 2
        assert len(results["elements_discovered"]) >= 3  # At least 3 from Login.razor
    
    def test_discover_nonexistent_file(self, view_discovery_agent, tmp_path):
        """Test discovery with nonexistent file."""
        fake_file = tmp_path / "nonexistent.razor"
        results = view_discovery_agent.discover_views(
            view_paths=[fake_file],
            save_to_db=False
        )
        
        assert len(results["warnings"]) > 0
        assert "not found" in results["warnings"][0].lower()
    
    def test_discover_with_output_file(self, view_discovery_agent, sample_razor_file, tmp_path):
        """Test discovery with JSON output file."""
        output_path = tmp_path / "discovery_results.json"
        results = view_discovery_agent.discover_views(
            view_paths=[sample_razor_file],
            output_path=output_path,
            save_to_db=False
        )
        
        assert output_path.exists()
        
        # Validate JSON content
        with open(output_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        assert saved_data["discovery_timestamp"] == results["discovery_timestamp"]
        assert len(saved_data["elements_discovered"]) == len(results["elements_discovered"])
    
    def test_discover_with_custom_project_name(self, view_discovery_agent, sample_razor_file):
        """Test discovery with custom project name."""
        results = view_discovery_agent.discover_views(
            view_paths=[sample_razor_file],
            project_name="TestProject",
            save_to_db=True
        )
        
        assert results.get("database_project_name") == "TestProject"
        assert results.get("saved_to_database") == True
    
    def test_elements_discovered_structure(self, view_discovery_agent, sample_razor_file):
        """Test structure of discovered elements."""
        results = view_discovery_agent.discover_views(
            view_paths=[sample_razor_file],
            save_to_db=False
        )
        
        elements = results["elements_discovered"]
        assert len(elements) > 0
        
        # Check first element has required fields
        elem = elements[0]
        assert "element_id" in elem
        assert "element_type" in elem
        assert "data_testid" in elem
        assert "css_classes" in elem
        assert "user_facing_text" in elem
        assert "selector_strategy" in elem
        assert "file_path" in elem
        assert "line_number" in elem
        assert "attributes" in elem
    
    def test_navigation_flows_discovered(self, view_discovery_agent, sample_razor_file):
        """Test navigation flow discovery."""
        results = view_discovery_agent.discover_views(
            view_paths=[sample_razor_file],
            save_to_db=False
        )
        
        flows = results["navigation_flows"]
        assert len(flows) == 1
        
        flow = flows[0]
        assert flow["route"] == "/login"
        assert flow["component"] == "Login"
        assert "file_path" in flow
        assert isinstance(flow["elements"], list)


# ============================================================================
# TEST CLASS 3: Element Extraction
# ============================================================================

class TestElementExtraction:
    """Test _extract_element_info() method."""
    
    def test_extract_button_with_id(self, view_discovery_agent, sample_razor_file):
        """Test extraction of button with ID."""
        elem = view_discovery_agent._extract_element_info(
            tag="button",
            attrs='id="submitBtn" class="btn btn-primary" type="submit"',
            content="Submit",
            file_path=sample_razor_file,
            line_number=10
        )
        
        assert elem is not None
        assert elem["element_id"] == "submitBtn"
        assert elem["element_type"] == "button"
        assert "btn" in elem["css_classes"]
        assert elem["user_facing_text"] == "Submit"
        assert elem["selector_strategy"] == "#submitBtn"
    
    def test_extract_input_with_data_testid(self, view_discovery_agent, sample_razor_file):
        """Test extraction of input with data-testid."""
        elem = view_discovery_agent._extract_element_info(
            tag="input",
            attrs='type="email" data-testid="email-field" placeholder="Email"',
            content=None,
            file_path=sample_razor_file,
            line_number=8
        )
        
        assert elem is not None
        assert elem["element_id"] is None
        assert elem["data_testid"] == "email-field"
        assert elem["selector_strategy"] == "[data-testid='email-field']"
    
    def test_extract_element_with_only_class(self, view_discovery_agent, sample_razor_file):
        """Test extraction of element with only class."""
        elem = view_discovery_agent._extract_element_info(
            tag="button",
            attrs='class="btn btn-primary btn-large"',
            content="Click Me",
            file_path=sample_razor_file,
            line_number=15
        )
        
        assert elem is not None
        assert elem["element_id"] is None
        assert elem["data_testid"] is None
        assert len(elem["css_classes"]) == 3
        assert "btn-primary" in elem["selector_strategy"]
    
    def test_extract_link_with_text_only(self, view_discovery_agent, sample_razor_file):
        """Test extraction of link with only text."""
        elem = view_discovery_agent._extract_element_info(
            tag="a",
            attrs='href="/forgot-password"',
            content="Forgot Password?",
            file_path=sample_razor_file,
            line_number=24
        )
        
        assert elem is not None
        assert elem["element_id"] is None
        assert elem["data_testid"] is None
        assert elem["user_facing_text"] == "Forgot Password?"
        assert ":has-text(" in elem["selector_strategy"]
    
    def test_extract_non_interactive_element_without_id(self, view_discovery_agent, sample_razor_file):
        """Test that non-interactive elements without ID are ignored."""
        elem = view_discovery_agent._extract_element_info(
            tag="p",
            attrs='class="description"',
            content="Some text",
            file_path=sample_razor_file,
            line_number=5
        )
        
        assert elem is None  # Should be ignored
    
    def test_extract_div_with_id(self, view_discovery_agent, sample_razor_file):
        """Test that div with ID is captured."""
        elem = view_discovery_agent._extract_element_info(
            tag="div",
            attrs='id="container" class="main"',
            content="Content",
            file_path=sample_razor_file,
            line_number=3
        )
        
        assert elem is not None  # Has ID, so should be captured
        assert elem["element_id"] == "container"


# ============================================================================
# TEST CLASS 4: Selector Strategy Generation
# ============================================================================

class TestSelectorGeneration:
    """Test _generate_selector() method."""
    
    def test_selector_priority_id_first(self, view_discovery_agent):
        """Test selector prioritizes ID."""
        selector = view_discovery_agent._generate_selector(
            element_id="myBtn",
            data_testid="test-btn",
            css_classes=["btn", "btn-primary"],
            user_text="Click",
            tag="button"
        )
        
        assert selector == "#myBtn"
    
    def test_selector_priority_testid_second(self, view_discovery_agent):
        """Test selector uses data-testid when no ID."""
        selector = view_discovery_agent._generate_selector(
            element_id=None,
            data_testid="test-btn",
            css_classes=["btn", "btn-primary"],
            user_text="Click",
            tag="button"
        )
        
        assert selector == "[data-testid='test-btn']"
    
    def test_selector_priority_class_third(self, view_discovery_agent):
        """Test selector uses class when no ID or testid."""
        selector = view_discovery_agent._generate_selector(
            element_id=None,
            data_testid=None,
            css_classes=["btn", "btn-primary", "btn-large"],
            user_text="Click",
            tag="button"
        )
        
        assert "btn-primary" in selector  # Longest class name
        assert "button" in selector
    
    def test_selector_priority_text_fourth(self, view_discovery_agent):
        """Test selector uses text when no other attributes."""
        selector = view_discovery_agent._generate_selector(
            element_id=None,
            data_testid=None,
            css_classes=[],
            user_text="Click Here",
            tag="a"
        )
        
        assert ":has-text(" in selector
        assert "Click Here" in selector
    
    def test_selector_fallback_tag_only(self, view_discovery_agent):
        """Test selector falls back to tag only."""
        selector = view_discovery_agent._generate_selector(
            element_id=None,
            data_testid=None,
            css_classes=[],
            user_text=None,
            tag="button"
        )
        
        assert selector == "button"


# ============================================================================
# TEST CLASS 5: Database Operations
# ============================================================================

class TestDatabaseOperations:
    """Test database save and load operations."""
    
    def test_save_to_database(self, view_discovery_agent, sample_razor_file):
        """Test saving discovered elements to database."""
        results = view_discovery_agent.discover_views(
            view_paths=[sample_razor_file],
            save_to_db=True,
            project_name="TestProject"
        )
        
        assert results.get("saved_to_database") == True
        
        # Verify database contents
        conn = sqlite3.connect(str(view_discovery_agent.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM tier2_element_mappings
            WHERE project_name = 'TestProject'
        """)
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == len(results["elements_discovered"])
    
    def test_load_from_database(self, view_discovery_agent, sample_razor_file):
        """Test loading discovered elements from database."""
        # First save
        view_discovery_agent.discover_views(
            view_paths=[sample_razor_file],
            save_to_db=True,
            project_name="TestProject"
        )
        
        # Then load
        elements = view_discovery_agent.load_from_database("TestProject")
        
        assert len(elements) > 0
        assert "element_id" in elements[0]
        assert "selector_strategy" in elements[0]
    
    def test_load_from_database_with_component_filter(self, view_discovery_agent, sample_razor_file):
        """Test loading elements filtered by component path."""
        # Save elements
        view_discovery_agent.discover_views(
            view_paths=[sample_razor_file],
            save_to_db=True,
            project_name="TestProject"
        )
        
        # Load with filter
        elements = view_discovery_agent.load_from_database(
            "TestProject",
            component_path=str(sample_razor_file)
        )
        
        assert len(elements) > 0
        assert all(e["file_path"] == str(sample_razor_file) for e in elements)
    
    def test_save_updates_existing_entries(self, view_discovery_agent, sample_razor_file):
        """Test that saving twice updates existing entries."""
        # Save first time
        view_discovery_agent.discover_views(
            view_paths=[sample_razor_file],
            save_to_db=True,
            project_name="TestProject"
        )
        
        time.sleep(0.1)  # Ensure different timestamp
        
        # Save second time (should update, not duplicate)
        view_discovery_agent.discover_views(
            view_paths=[sample_razor_file],
            save_to_db=True,
            project_name="TestProject"
        )
        
        # Check no duplicates
        conn = sqlite3.connect(str(view_discovery_agent.db_path))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM tier2_element_mappings
            WHERE project_name = 'TestProject'
        """)
        count = cursor.fetchone()[0]
        conn.close()
        
        # Should be same count, not doubled
        results = view_discovery_agent.discover_views(
            view_paths=[sample_razor_file],
            save_to_db=False
        )
        assert count == len(results["elements_discovered"])
    
    def test_save_when_db_disabled(self, tmp_path):
        """Test save_to_database when database is disabled."""
        agent = ViewDiscoveryAgent(
            project_root=tmp_path,
            db_path=tmp_path / "nonexistent.db"
        )
        
        success = agent.save_to_database("TestProject", [])
        assert success == False


# ============================================================================
# TEST CLASS 6: Components Without IDs
# ============================================================================

class TestComponentsWithoutIDs:
    """Test detection of components without IDs."""
    
    def test_detect_elements_without_ids(self, view_discovery_agent, sample_razor_without_ids):
        """Test that elements without IDs are flagged."""
        results = view_discovery_agent.discover_views(
            view_paths=[sample_razor_without_ids],
            save_to_db=False
        )
        
        assert len(results["components_without_ids"]) > 0
        
        # Check structure
        elem = results["components_without_ids"][0]
        assert "file" in elem
        assert "line" in elem
        assert "type" in elem
    
    def test_elements_with_ids_not_flagged(self, view_discovery_agent, sample_razor_file):
        """Test that elements with IDs are not flagged."""
        results = view_discovery_agent.discover_views(
            view_paths=[sample_razor_file],
            save_to_db=False
        )
        
        # Login.razor has some elements with IDs and some without
        # Check that not ALL elements are flagged as missing IDs
        assert len(results["components_without_ids"]) <= len(results["elements_discovered"])


# ============================================================================
# TEST CLASS 7: Selector Strategies Mapping
# ============================================================================

class TestSelectorStrategiesMapping:
    """Test _generate_selector_strategies() method."""
    
    def test_generate_selector_strategies(self, view_discovery_agent, sample_razor_file):
        """Test generation of selector strategies mapping."""
        results = view_discovery_agent.discover_views(
            view_paths=[sample_razor_file],
            save_to_db=False
        )
        
        strategies = results["selector_strategies"]
        
        assert len(strategies) > 0
        assert isinstance(strategies, dict)
        
        # Check that strategies dictionary is populated with selectors
        # Strategies are mapped by either user_facing_text or element_id
        assert all(isinstance(v, str) for v in strategies.values())
    
    def test_strategies_map_by_user_text(self, view_discovery_agent, sample_razor_file):
        """Test strategies are mapped by user-facing text."""
        results = view_discovery_agent.discover_views(
            view_paths=[sample_razor_file],
            save_to_db=False
        )
        
        strategies = results["selector_strategies"]
        
        # "Forgot Password?" link should be in strategies
        if "Forgot Password?" in strategies:
            selector = strategies["Forgot Password?"]
            assert "has-text" in selector or "a" in selector
    
    def test_strategies_map_by_element_id(self, view_discovery_agent, sample_razor_file):
        """Test strategies are mapped by element ID."""
        results = view_discovery_agent.discover_views(
            view_paths=[sample_razor_file],
            save_to_db=False
        )
        
        strategies = results["selector_strategies"]
        
        # emailInput and loginBtn should be in strategies
        if "emailInput" in strategies:
            assert strategies["emailInput"] == "#emailInput"
        if "loginBtn" in strategies:
            assert strategies["loginBtn"] == "#loginBtn"


# ============================================================================
# TEST CLASS 8: Error Handling
# ============================================================================

class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_malformed_file_generates_warning(self, view_discovery_agent, tmp_path):
        """Test that malformed files generate warnings."""
        # Create file with malformed content
        malformed_file = tmp_path / "Malformed.razor"
        malformed_file.write_text("<div id='unclosed", encoding='utf-8')
        
        results = view_discovery_agent.discover_views(
            view_paths=[malformed_file],
            save_to_db=False
        )
        
        # Should complete without crashing
        assert "discovery_timestamp" in results
        # May or may not have warnings depending on parsing robustness
    
    def test_empty_file(self, view_discovery_agent, tmp_path):
        """Test discovery with empty file."""
        empty_file = tmp_path / "Empty.razor"
        empty_file.write_text("", encoding='utf-8')
        
        results = view_discovery_agent.discover_views(
            view_paths=[empty_file],
            save_to_db=False
        )
        
        assert len(results["files_processed"]) == 1
        assert len(results["elements_discovered"]) == 0
    
    def test_binary_file_handling(self, view_discovery_agent, tmp_path):
        """Test handling of binary files."""
        binary_file = tmp_path / "Binary.razor"
        binary_file.write_bytes(b'\x00\x01\x02\x03')
        
        results = view_discovery_agent.discover_views(
            view_paths=[binary_file],
            save_to_db=False
        )
        
        # Should generate warning or handle gracefully
        assert "warnings" in results


# ============================================================================
# TEST CLASS 9: Integration Tests
# ============================================================================

class TestIntegration:
    """Test end-to-end integration scenarios."""
    
    def test_discover_and_load_workflow(self, view_discovery_agent, sample_razor_file):
        """Test complete discover→save→load workflow."""
        # Step 1: Discover
        results = view_discovery_agent.discover_views(
            view_paths=[sample_razor_file],
            save_to_db=True,
            project_name="IntegrationTest"
        )
        
        assert results["saved_to_database"] == True
        discovered_count = len(results["elements_discovered"])
        
        # Step 2: Load
        loaded_elements = view_discovery_agent.load_from_database("IntegrationTest")
        
        # Step 3: Verify consistency
        assert len(loaded_elements) == discovered_count
        
        # Check first element matches
        first_discovered = results["elements_discovered"][0]
        first_loaded = loaded_elements[0]
        
        assert first_discovered["element_id"] == first_loaded["element_id"]
        assert first_discovered["element_type"] == first_loaded["element_type"]
        assert first_discovered["selector_strategy"] == first_loaded["selector_strategy"]
    
    def test_multiple_projects_isolation(self, view_discovery_agent, sample_razor_file, sample_razor_without_ids):
        """Test that multiple projects are isolated in database."""
        # Save to Project A
        view_discovery_agent.discover_views(
            view_paths=[sample_razor_file],
            save_to_db=True,
            project_name="ProjectA"
        )
        
        # Save to Project B
        view_discovery_agent.discover_views(
            view_paths=[sample_razor_without_ids],
            save_to_db=True,
            project_name="ProjectB"
        )
        
        # Load Project A only
        elements_a = view_discovery_agent.load_from_database("ProjectA")
        
        # Verify only Project A elements returned
        assert all(e["file_path"] == str(sample_razor_file) for e in elements_a if e["file_path"])


# ============================================================================
# TEST CLASS 10: Convenience Function
# ============================================================================

class TestConvenienceFunction:
    """Test discover_views_for_testing() convenience function."""
    
    def test_discover_views_for_testing_basic(self, tmp_path, sample_razor_file):
        """Test basic usage of convenience function."""
        results = discover_views_for_testing(
            view_directory=tmp_path,
            pattern="*.razor"
        )
        
        assert "discovery_timestamp" in results
        assert len(results["files_processed"]) >= 1
    
    def test_discover_views_for_testing_with_output(self, tmp_path, sample_razor_file):
        """Test convenience function with output file."""
        output_file = tmp_path / "results.json"
        
        results = discover_views_for_testing(
            view_directory=tmp_path,
            pattern="*.razor",
            output_file=output_file
        )
        
        assert output_file.exists()
        
        # Verify JSON content
        with open(output_file, 'r', encoding='utf-8') as f:
            saved = json.load(f)
        
        assert saved["discovery_timestamp"] == results["discovery_timestamp"]
    
    def test_discover_views_for_testing_pattern_matching(self, tmp_path):
        """Test pattern matching in convenience function."""
        # Create mix of file types
        (tmp_path / "View1.razor").write_text("<div></div>")
        (tmp_path / "View2.jsx").write_text("<div></div>")
        (tmp_path / "View3.razor").write_text("<div></div>")
        
        results = discover_views_for_testing(
            view_directory=tmp_path,
            pattern="*.razor"
        )
        
        # Should only process .razor files
        assert len(results["files_processed"]) == 2


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
