"""
Pytest configuration and fixtures for dashboard testing.

CORTEX Phase 18.1 - Test Infrastructure
Author: Asif Hussain
"""

import json
from pathlib import Path
from typing import Dict, Any

import pytest
from bs4 import BeautifulSoup


@pytest.fixture
def dashboard_path() -> Path:
    """Return path to generated dashboard.html"""
    return Path(__file__).parent.parent / "dashboard.html"


@pytest.fixture
def dashboard_html(dashboard_path: Path) -> str:
    """Load dashboard HTML content"""
    if not dashboard_path.exists():
        pytest.skip(f"Dashboard not found: {dashboard_path}")
    return dashboard_path.read_text(encoding="utf-8")


@pytest.fixture
def dashboard_soup(dashboard_html: str) -> BeautifulSoup:
    """Parse dashboard HTML with BeautifulSoup"""
    return BeautifulSoup(dashboard_html, "html.parser")


@pytest.fixture
def simulation_data_path() -> Path:
    """Return path to simulation data directory"""
    return Path(__file__).parent.parent / "repo-simulation"


@pytest.fixture
def repo_tiers() -> list[str]:
    """Return list of simulation tiers"""
    return ["repo-S", "repo-M", "repo-L", "repo-XL", "repo-enterprise"]


@pytest.fixture
def tier_data(simulation_data_path: Path, request) -> Dict[str, Any]:
    """Load JSON data for a specific tier (use with indirect parametrization)"""
    tier = request.param
    data_file = simulation_data_path / tier / "data.json"
    
    if not data_file.exists():
        pytest.skip(f"Data file not found: {data_file}")
    
    with open(data_file, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def expected_chart_types() -> Dict[str, list[str]]:
    """Return expected chart types per tab"""
    return {
        "overview": ["health-score-gauge", "metrics-cards"],
        "architecture": ["directory-treemap", "dependency-force-graph", "layer-diagram"],
        "quality": ["complexity-histogram", "quality-radar", "loc-bar-chart"],
        "vulnerabilities": ["vulnerability-pie-chart"],
        "dependencies": ["dependency-tree"],
        "testing": ["testing-pyramid"],
    }
