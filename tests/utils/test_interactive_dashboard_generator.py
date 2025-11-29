"""
Tests for Interactive Dashboard Generator

Tests D3.js dashboard generation, validation, and export functionality.

Author: Asif Hussain
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
from pathlib import Path
import json
import time
from datetime import datetime
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.utils.interactive_dashboard_generator import InteractiveDashboardGenerator


# Test Fixtures

@pytest.fixture
def sample_dashboard_data():
    """Sample valid dashboard data."""
    return {
        "metadata": {
            "generatedAt": datetime.utcnow().isoformat() + "Z",
            "version": "3.4.0",
            "operationType": "system_alignment",
            "author": "CORTEX"
        },
        "overview": {
            "executiveSummary": "System validation completed successfully with 95% health score. All 7 layers passed validation with no critical errors. Minor warnings detected in 2 components.",
            "keyMetrics": [
                {
                    "label": "System Health",
                    "value": "95%",
                    "trend": "up",
                    "trendValue": "+3%",
                    "status": "healthy"
                },
                {
                    "label": "Layers Passed",
                    "value": "7/7",
                    "trend": "stable",
                    "status": "healthy"
                },
                {
                    "label": "Critical Errors",
                    "value": "0",
                    "trend": "down",
                    "trendValue": "-2",
                    "status": "healthy"
                },
                {
                    "label": "Warnings",
                    "value": "2",
                    "trend": "stable",
                    "status": "warning"
                },
                {
                    "label": "Processing Time",
                    "value": "3.2s",
                    "trend": "down",
                    "trendValue": "-0.5s",
                    "status": "healthy"
                }
            ],
            "statusIndicator": {
                "status": "healthy",
                "message": "All systems operational with no critical issues"
            }
        },
        "visualizations": {
            "forceGraph": {
                "nodes": [
                    {"id": "node1", "group": 1, "label": "Node 1"},
                    {"id": "node2", "group": 1, "label": "Node 2"}
                ],
                "links": [
                    {"source": "node1", "target": "node2", "value": 1}
                ]
            },
            "timeSeries": {
                "labels": ["2025-11-21", "2025-11-22", "2025-11-23", "2025-11-24", "2025-11-25"],
                "datasets": [
                    {
                        "label": "System Health",
                        "data": [88, 90, 92, 94, 95],
                        "borderColor": "rgb(75, 192, 192)",
                        "backgroundColor": "rgba(75, 192, 192, 0.2)"
                    }
                ]
            }
        },
        "diagrams": [
            {
                "title": "System Architecture",
                "mermaidCode": "graph TD\nA[Start] --> B[End]",
                "type": "flowchart",
                "description": "Test diagram"
            }
        ],
        "dataTable": [
            {
                "name": "Item 1",
                "type": "Test",
                "status": "healthy",
                "health": 95,
                "lastUpdated": "2025-11-28"
            },
            {
                "name": "Item 2",
                "type": "Test",
                "status": "warning",
                "health": 80,
                "lastUpdated": "2025-11-28"
            }
        ],
        "recommendations": [
            {
                "priority": "high",
                "title": "Test Recommendation",
                "rationale": "This is a test recommendation for validation",
                "steps": [
                    "Step 1: Do something",
                    "Step 2: Verify result",
                    "Step 3: Document findings"
                ],
                "expectedImpact": "+10% improvement",
                "estimatedEffort": "2-3 hours",
                "relatedResources": ["/docs/test-guide.md"]
            }
        ]
    }


@pytest.fixture
def generator():
    """Dashboard generator instance."""
    return InteractiveDashboardGenerator()


@pytest.fixture
def temp_output_dir(tmp_path):
    """Temporary output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


# Test 1: Dashboard Generation Success

def test_generate_dashboard_success(generator, sample_dashboard_data, temp_output_dir):
    """Test successful dashboard generation."""
    output_file = temp_output_dir / "test-dashboard.html"
    
    success = generator.generate_dashboard(
        title="Test Dashboard",
        data=sample_dashboard_data,
        output_file=str(output_file)
    )
    
    assert success is True
    assert output_file.exists()
    assert output_file.stat().st_size > 0


# Test 2: HTML Structure Validation

def test_dashboard_html_structure(generator, sample_dashboard_data, temp_output_dir):
    """Test dashboard HTML contains required elements."""
    output_file = temp_output_dir / "test-dashboard.html"
    
    generator.generate_dashboard(
        title="Test Dashboard",
        data=sample_dashboard_data,
        output_file=str(output_file)
    )
    
    html_content = output_file.read_text(encoding="utf-8")
    
    # Check required elements
    assert '<title>Test Dashboard</title>' in html_content
    assert 'dashboard-tabs' in html_content
    assert 'data-tab="overview"' in html_content
    assert 'data-tab="visualizations"' in html_content
    assert 'data-tab="diagrams"' in html_content
    assert 'data-tab="data"' in html_content
    assert 'data-tab="recommendations"' in html_content
    assert 'export-controls' in html_content
    
    # Check D3.js and Chart.js libraries
    assert 'd3.v7.min.js' in html_content
    assert 'chart.js' in html_content
    assert 'mermaid' in html_content
    
    # Check CSP headers
    assert 'Content-Security-Policy' in html_content


# Test 3: Data Validation - Missing Required Keys

def test_validation_missing_metadata(generator, sample_dashboard_data, temp_output_dir):
    """Test validation fails with missing metadata."""
    invalid_data = sample_dashboard_data.copy()
    del invalid_data["metadata"]
    
    output_file = temp_output_dir / "test-dashboard.html"
    
    success = generator.generate_dashboard(
        title="Test Dashboard",
        data=invalid_data,
        output_file=str(output_file)
    )
    
    assert success is False


def test_validation_missing_overview(generator, sample_dashboard_data, temp_output_dir):
    """Test validation fails with missing overview."""
    invalid_data = sample_dashboard_data.copy()
    del invalid_data["overview"]
    
    output_file = temp_output_dir / "test-dashboard.html"
    
    success = generator.generate_dashboard(
        title="Test Dashboard",
        data=invalid_data,
        output_file=str(output_file)
    )
    
    assert success is False


# Test 4: Key Metrics Count Validation

def test_validation_insufficient_metrics(generator, sample_dashboard_data, temp_output_dir):
    """Test validation fails with <5 key metrics."""
    invalid_data = sample_dashboard_data.copy()
    invalid_data["overview"]["keyMetrics"] = [
        {"label": "Test", "value": "100", "status": "healthy"}
    ]  # Only 1 metric (need 5-10)
    
    output_file = temp_output_dir / "test-dashboard.html"
    
    success = generator.generate_dashboard(
        title="Test Dashboard",
        data=invalid_data,
        output_file=str(output_file)
    )
    
    assert success is False


def test_validation_excessive_metrics(generator, sample_dashboard_data, temp_output_dir):
    """Test validation fails with >10 key metrics."""
    invalid_data = sample_dashboard_data.copy()
    invalid_data["overview"]["keyMetrics"] = [
        {"label": f"Metric {i}", "value": str(i), "status": "healthy"}
        for i in range(15)  # 15 metrics (need 5-10)
    ]
    
    output_file = temp_output_dir / "test-dashboard.html"
    
    success = generator.generate_dashboard(
        title="Test Dashboard",
        data=invalid_data,
        output_file=str(output_file)
    )
    
    assert success is False


# Test 5: Force Graph Structure Validation

def test_validation_missing_force_graph_nodes(generator, sample_dashboard_data, temp_output_dir):
    """Test validation fails with missing force graph nodes."""
    invalid_data = sample_dashboard_data.copy()
    del invalid_data["visualizations"]["forceGraph"]["nodes"]
    
    output_file = temp_output_dir / "test-dashboard.html"
    
    success = generator.generate_dashboard(
        title="Test Dashboard",
        data=invalid_data,
        output_file=str(output_file)
    )
    
    assert success is False


# Test 6: Data Injection

def test_data_injection(generator, sample_dashboard_data, temp_output_dir):
    """Test dashboard data is properly injected."""
    output_file = temp_output_dir / "test-dashboard.html"
    
    generator.generate_dashboard(
        title="Test Dashboard",
        data=sample_dashboard_data,
        output_file=str(output_file)
    )
    
    html_content = output_file.read_text(encoding="utf-8")
    
    # Check data is injected
    assert sample_dashboard_data["overview"]["executiveSummary"] in html_content or \
           json.dumps(sample_dashboard_data) in html_content


# Test 7: HTML Escaping

def test_html_escaping(generator, sample_dashboard_data, temp_output_dir):
    """Test HTML special characters are escaped."""
    output_file = temp_output_dir / "test-dashboard.html"
    
    generator.generate_dashboard(
        title="Test <script>alert('XSS')</script>",
        data=sample_dashboard_data,
        output_file=str(output_file)
    )
    
    html_content = output_file.read_text(encoding="utf-8")
    
    # Check script tag is escaped
    assert '<script>alert' not in html_content
    assert '&lt;script&gt;' in html_content or 'Test &lt;script&gt;alert' in html_content


# Test 8: Performance - Generation Time

def test_generation_performance(generator, sample_dashboard_data, temp_output_dir):
    """Test dashboard generation completes in <5 seconds."""
    output_file = temp_output_dir / "test-dashboard.html"
    
    start = time.time()
    generator.generate_dashboard(
        title="Performance Test Dashboard",
        data=sample_dashboard_data,
        output_file=str(output_file)
    )
    duration = time.time() - start
    
    assert duration < 5.0, f"Generation took {duration:.2f}s (target: <5s)"


# Test 9: File Size

def test_file_size_under_limit(generator, sample_dashboard_data, temp_output_dir):
    """Test generated HTML file is <2MB."""
    output_file = temp_output_dir / "test-dashboard.html"
    
    generator.generate_dashboard(
        title="File Size Test Dashboard",
        data=sample_dashboard_data,
        output_file=str(output_file)
    )
    
    file_size_mb = output_file.stat().st_size / (1024 * 1024)
    assert file_size_mb < 2.0, f"File size {file_size_mb:.2f}MB exceeds 2MB limit"


# Test 10: Multiple Dashboards

def test_multiple_dashboard_generation(generator, sample_dashboard_data, temp_output_dir):
    """Test generating multiple dashboards sequentially."""
    for i in range(3):
        output_file = temp_output_dir / f"test-dashboard-{i}.html"
        
        success = generator.generate_dashboard(
            title=f"Test Dashboard {i}",
            data=sample_dashboard_data,
            output_file=str(output_file)
        )
        
        assert success is True
        assert output_file.exists()


# Test 11: Empty Data Arrays

def test_empty_diagrams_array(generator, sample_dashboard_data, temp_output_dir):
    """Test validation fails with empty diagrams array."""
    invalid_data = sample_dashboard_data.copy()
    invalid_data["diagrams"] = []
    
    output_file = temp_output_dir / "test-dashboard.html"
    
    success = generator.generate_dashboard(
        title="Test Dashboard",
        data=invalid_data,
        output_file=str(output_file)
    )
    
    assert success is False


def test_empty_data_table_array(generator, sample_dashboard_data, temp_output_dir):
    """Test validation fails with empty dataTable array."""
    invalid_data = sample_dashboard_data.copy()
    invalid_data["dataTable"] = []
    
    output_file = temp_output_dir / "test-dashboard.html"
    
    success = generator.generate_dashboard(
        title="Test Dashboard",
        data=invalid_data,
        output_file=str(output_file)
    )
    
    assert success is False


# Test 12: Executive Summary Length

def test_executive_summary_min_length(generator, sample_dashboard_data, temp_output_dir):
    """Test dashboard generation with minimum length summary."""
    data = sample_dashboard_data.copy()
    data["overview"]["executiveSummary"] = "A" * 100  # Minimum 100 chars
    
    output_file = temp_output_dir / "test-dashboard.html"
    
    success = generator.generate_dashboard(
        title="Test Dashboard",
        data=data,
        output_file=str(output_file)
    )
    
    assert success is True


# Test 13: PDF Export (if Playwright available)

def test_export_to_pdf(generator, sample_dashboard_data, temp_output_dir):
    """Test PDF export functionality."""
    html_file = temp_output_dir / "test-dashboard.html"
    pdf_file = temp_output_dir / "test-dashboard.pdf"
    
    # Generate dashboard first
    generator.generate_dashboard(
        title="PDF Export Test",
        data=sample_dashboard_data,
        output_file=str(html_file)
    )
    
    # Attempt PDF export (may skip if Playwright not installed)
    try:
        success = generator.export_to_pdf(str(html_file), str(pdf_file))
        
        if success:
            assert pdf_file.exists()
            assert pdf_file.stat().st_size > 0
        else:
            pytest.skip("Playwright not available for PDF export")
    except ImportError:
        pytest.skip("Playwright not installed")


# Test 14: PNG Export (if Playwright available)

def test_export_to_png(generator, sample_dashboard_data, temp_output_dir):
    """Test PNG export functionality."""
    html_file = temp_output_dir / "test-dashboard.html"
    png_file = temp_output_dir / "test-dashboard.png"
    
    # Generate dashboard first
    generator.generate_dashboard(
        title="PNG Export Test",
        data=sample_dashboard_data,
        output_file=str(html_file)
    )
    
    # Attempt PNG export (may skip if Playwright not installed)
    try:
        success = generator.export_to_png(str(html_file), str(png_file))
        
        if success:
            assert png_file.exists()
            assert png_file.stat().st_size > 0
        else:
            pytest.skip("Playwright not available for PNG export")
    except ImportError:
        pytest.skip("Playwright not installed")


# Test 15: Template Loading

def test_template_not_found(generator, sample_dashboard_data, temp_output_dir):
    """Test error handling when template file missing."""
    # Temporarily change template path to non-existent file
    original_path = generator.template_path
    generator.template_path = Path("/nonexistent/path/template.html")
    
    output_file = temp_output_dir / "test-dashboard.html"
    
    success = generator.generate_dashboard(
        title="Test Dashboard",
        data=sample_dashboard_data,
        output_file=str(output_file)
    )
    
    assert success is False
    
    # Restore original path
    generator.template_path = original_path


# Integration Test: Complete Workflow

def test_complete_workflow(generator, sample_dashboard_data, temp_output_dir):
    """Test complete dashboard generation and validation workflow."""
    output_file = temp_output_dir / "complete-workflow-dashboard.html"
    
    # Generate dashboard
    success = generator.generate_dashboard(
        title="Complete Workflow Test",
        data=sample_dashboard_data,
        output_file=str(output_file)
    )
    
    assert success is True
    assert output_file.exists()
    
    # Validate HTML structure
    html_content = output_file.read_text(encoding="utf-8")
    
    required_elements = [
        'dashboard-tabs',
        'overview-tab',
        'visualizations-tab',
        'diagrams-tab',
        'data-tab',
        'recommendations-tab',
        'export-controls',
        'd3.v7.min.js',
        'chart.js',
        'mermaid'
    ]
    
    for element in required_elements:
        assert element in html_content, f"Missing required element: {element}"
    
    # Validate data injection
    assert sample_dashboard_data["overview"]["executiveSummary"] in html_content or \
           'dashboardData' in html_content
    
    # Validate file size
    file_size_mb = output_file.stat().st_size / (1024 * 1024)
    assert file_size_mb < 2.0
    
    print(f"✅ Complete workflow test passed (file size: {file_size_mb:.2f}MB)")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
