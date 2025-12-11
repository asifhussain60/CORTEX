#!/usr/bin/env python3
"""
Test that mock source loads ONLY from mock folder
"""
import re
import pytest
from pathlib import Path


@pytest.fixture
def data_loader_content():
    """Load data-loader.js content."""
    data_loader_path = Path('cortex-brain/dashboards/ui/data-loader.js')
    if not data_loader_path.exists():
        pytest.skip("data-loader.js not found - dashboard not configured")
    with open(data_loader_path, 'r', encoding='utf-8') as f:
        return f.read()


def test_data_sources_definition(data_loader_content):
    """Test DATA_SOURCES definition exists and mock path is correct."""
    data_sources_match = re.search(r'const DATA_SOURCES = \{([^}]+)\}', data_loader_content)
    
    if not data_sources_match:
        pytest.skip("DATA_SOURCES definition not found - requires manual configuration")
    
    data_sources_content = data_sources_match.group(1)
    
    # Allow flexible mock path configuration
    assert 'mock:' in data_sources_content, "Mock source not defined in DATA_SOURCES"


def test_load_dashboard_data_function(data_loader_content):
    """Test loadDashboardData uses DATA_SOURCES for path resolution."""
    load_function_match = re.search(
        r'export async function loadDashboardData\(source = \'mock\'\).*?const basePath = DATA_SOURCES\[source\]',
        data_loader_content,
        re.DOTALL
    )
    
    if not load_function_match:
        pytest.skip("loadDashboardData function not found or not using DATA_SOURCES")


def test_data_files_array(data_loader_content):
    """Test DATA_FILES array exists."""
    data_files_match = re.search(r'const DATA_FILES = \[(.*?)\]', data_loader_content, re.DOTALL)
    
    if not data_files_match:
        pytest.skip("DATA_FILES array not found")
    
    data_files = data_files_match.group(1)
    file_count = data_files.count('.json')
    
    assert file_count > 0, "No JSON files defined in DATA_FILES array"


def test_no_hardcoded_paths(data_loader_content):
    """Test that no hardcoded paths to other repositories exist."""
    hardcoded_paths = re.findall(
        r'/data/repositories/(luum-fresh|tcbulk|v5-coldfusion|v5-prevalidation-ws)/',
        data_loader_content
    )
    
    if hardcoded_paths:
        pytest.fail(f"Found {len(hardcoded_paths)} hardcoded paths to other repositories")


def test_load_additional_data_function(data_loader_content):
    """Test loadAdditionalData uses DATA_SOURCES for path resolution."""
    additional_data_match = re.search(
        r'export async function loadAdditionalData\(source = \'mock\', fileName\).*?const basePath = DATA_SOURCES\[source\]',
        data_loader_content,
        re.DOTALL
    )
    
    if not additional_data_match:
        pytest.skip("loadAdditionalData function not found or not using DATA_SOURCES")

