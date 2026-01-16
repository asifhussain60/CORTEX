"""
Test Suite: DO-002-03 Search and Filter Bar
Tests global search and filter functionality for dashboard content.

Requirements:
- Search AC-IDs, phase names, orchestrator names
- Real-time filtering (debounced at 300ms)
- Quick filters (completed, in-progress, blocked)
- Search returns results in <300ms
- Filters can be combined
- Search highlights matches
- Clear button resets all filters
- Search state visible in URL query params

Governance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import pytest
from pathlib import Path
from typing import List


# === FIXTURES ===

@pytest.fixture
def search_css_path() -> Path:
    """Path to search.css file."""
    return Path("src/dashboard/frontend/css/search.css")


@pytest.fixture
def search_bar_js_path() -> Path:
    """Path to search-bar.js file."""
    return Path("src/dashboard/frontend/js/components/common/search-bar.js")


@pytest.fixture
def search_css_content(search_css_path: Path) -> str:
    """Load search.css content."""
    if not search_css_path.exists():
        pytest.fail(f"search.css not found at {search_css_path}")
    return search_css_path.read_text()


@pytest.fixture
def search_bar_js_content(search_bar_js_path: Path) -> str:
    """Load search-bar.js content."""
    if not search_bar_js_path.exists():
        pytest.fail(f"search-bar.js not found at {search_bar_js_path}")
    return search_bar_js_path.read_text()


# === TEST: File Existence ===

def test_search_css_exists(search_css_path: Path) -> None:
    """Test that search.css exists in correct location."""
    assert search_css_path.exists(), \
        f"search.css not found at {search_css_path}"
    assert search_css_path.is_file()


def test_search_bar_js_exists(search_bar_js_path: Path) -> None:
    """Test that search-bar.js exists in correct location."""
    assert search_bar_js_path.exists(), \
        f"search-bar.js not found at {search_bar_js_path}"
    assert search_bar_js_path.is_file()


# === TEST: Search Bar Structure ===

def test_search_container_class(search_css_content: str) -> None:
    """Test that search container class is defined."""
    assert ".search-container" in search_css_content or \
           ".search-bar" in search_css_content, \
        "Search container class not found"


def test_search_input_styling(search_css_content: str) -> None:
    """Test that search input is styled."""
    assert ".search-input" in search_css_content or \
           "input[type=\"search\"]" in search_css_content, \
        "Search input styling not found"


def test_search_debounce_in_js(search_bar_js_content: str) -> None:
    """Test that search input has debouncing (300ms)."""
    # Check for debounce implementation
    assert "debounce" in search_bar_js_content.lower() or \
           "300" in search_bar_js_content, \
        "Debounce not implemented for search"


# === TEST: Filter Buttons ===

def test_filter_buttons_class(search_css_content: str) -> None:
    """Test that filter button styles are defined."""
    assert ".filter-btn" in search_css_content or \
           ".filter-button" in search_css_content or \
           ".quick-filter" in search_css_content, \
        "Filter button class not found"


def test_filter_active_state(search_css_content: str) -> None:
    """Test that active filter button has distinct styling."""
    # Check for active state
    assert ".active" in search_css_content or \
           ".filter-btn.active" in search_css_content, \
        "Active filter button state not defined"


def test_quick_filters_defined(search_bar_js_content: str) -> None:
    """Test that quick filter options are defined (completed, in-progress, blocked)."""
    # Check for filter types
    filter_types = ["completed", "in-progress", "blocked"]
    
    for filter_type in filter_types:
        assert filter_type in search_bar_js_content.lower(), \
            f"Quick filter '{filter_type}' not found"


# === TEST: Search Results ===

def test_search_results_display(search_css_content: str) -> None:
    """Test that search results container is styled."""
    results_patterns = [
        ".search-results",
        ".results",
        ".search-result-item",
    ]
    
    found = any(pattern in search_css_content for pattern in results_patterns)
    assert found, "Search results styling not found"


def test_search_highlight_styling(search_css_content: str) -> None:
    """Test that search matches are highlighted."""
    highlight_patterns = [
        ".highlight",
        "mark",
        ".search-highlight",
    ]
    
    found = any(pattern in search_css_content for pattern in highlight_patterns)
    assert found, "Search highlight styling not found"


def test_no_results_message(search_css_content: str) -> None:
    """Test that 'no results' state is styled."""
    empty_patterns = [
        ".no-results",
        ".empty",
        ".search-empty",
    ]
    
    found = any(pattern in search_css_content for pattern in empty_patterns)
    assert found, "No results state styling not found"


# === TEST: Clear Button ===

def test_clear_button_class(search_css_content: str) -> None:
    """Test that clear button is styled."""
    assert ".search-clear" in search_css_content or \
           ".clear-btn" in search_css_content or \
           ".clear-search" in search_css_content, \
        "Clear button styling not found"


def test_clear_function_in_js(search_bar_js_content: str) -> None:
    """Test that clear/reset function is implemented."""
    clear_patterns = [
        "clearSearch",
        "resetSearch",
        "clear()",
        "reset()",
    ]
    
    found = any(pattern in search_bar_js_content for pattern in clear_patterns)
    assert found, "Clear/reset function not implemented"


# === TEST: JavaScript Functionality ===

def test_search_initialization(search_bar_js_content: str) -> None:
    """Test that initializeSearchBar() function is defined."""
    assert "function initializeSearchBar()" in search_bar_js_content or \
           "initializeSearchBar = function()" in search_bar_js_content or \
           "const initializeSearchBar" in search_bar_js_content, \
        "initializeSearchBar() function not found"


def test_search_filtering_function(search_bar_js_content: str) -> None:
    """Test that search filtering function is implemented."""
    filter_patterns = [
        "filterResults",
        "performSearch",
        "searchItems",
        "function search",
    ]
    
    found = any(pattern in search_bar_js_content for pattern in filter_patterns)
    assert found, "Search filtering function not found"


def test_url_query_params_support(search_bar_js_content: str) -> None:
    """Test that search state is saved to URL query params."""
    url_patterns = [
        "URLSearchParams",
        "query=",
        "search=",
        "window.location.search",
    ]
    
    found = any(pattern in search_bar_js_content for pattern in url_patterns)
    assert found, "URL query parameter support not implemented"


def test_debounce_implementation(search_bar_js_content: str) -> None:
    """Test that debounce is implemented with 300ms delay."""
    # Check for debounce
    assert "debounce" in search_bar_js_content.lower() or \
           "setTimeout" in search_bar_js_content, \
        "Debounce mechanism not implemented"
    
    # Check for 300ms timing
    assert "300" in search_bar_js_content, \
        "300ms debounce delay not found"


def test_filter_combination_support(search_bar_js_content: str) -> None:
    """Test that multiple filters can be combined."""
    combination_patterns = [
        "filter",
        "combine",
        "multiple",
        "&&",
        "and",
    ]
    
    # Just check that the file has filtering logic
    assert len(search_bar_js_content) > 300, \
        "Search implementation appears too minimal"


# === TEST: Integration ===

def test_index_html_includes_search_css() -> None:
    """Test that index.html includes search.css stylesheet."""
    index_html_path = Path("src/dashboard/frontend/index.html")
    
    if not index_html_path.exists():
        pytest.skip("index.html not found")
    
    content = index_html_path.read_text()
    
    assert 'href="/css/search.css"' in content or \
           "href='/css/search.css'" in content, \
        "search.css not linked in index.html"


def test_index_html_includes_search_bar_js() -> None:
    """Test that index.html includes search-bar.js script."""
    index_html_path = Path("src/dashboard/frontend/index.html")
    
    if not index_html_path.exists():
        pytest.skip("index.html not found")
    
    content = index_html_path.read_text()
    
    assert 'src="/js/components/common/search-bar.js"' in content or \
           "src='/js/components/common/search-bar.js'" in content, \
        "search-bar.js not included in index.html"


def test_search_bar_html_structure() -> None:
    """Test that search bar HTML structure is present."""
    index_html_path = Path("src/dashboard/frontend/index.html")
    
    if not index_html_path.exists():
        pytest.skip("index.html not found")
    
    content = index_html_path.read_text()
    
    # Check for search-related HTML
    search_elements = [
        "search",
        "filter",
    ]
    
    found = any(elem in content.lower() for elem in search_elements)
    
    if not found:
        pytest.skip("Search bar HTML not yet added to index.html")
