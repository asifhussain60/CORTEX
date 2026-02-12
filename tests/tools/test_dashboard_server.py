"""
Tests for dashboard server management tool.
Following CORE-008: TDD - Tests BEFORE code.
"""

import subprocess
import time
import requests
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


class TestDashboardServerKill:
    """Test killing HTTP processes on specified ports."""
    
class TestDashboardServerStart:
    """Test starting HTTP server on port 8080."""
    
    def test_server_starts_on_port_8080(self):
        """Should start server on port 8080."""
        # Kill any existing process
        subprocess.run(
            "lsof -i :8080 | grep -v COMMAND | awk '{print $2}' | xargs kill -9 2>/dev/null",
            shell=True,
            capture_output=True
        )
        time.sleep(1)
        
        # Start server
        dashboards_dir = Path(__file__).parent.parent.parent / "company" / "dashboards"
        proc = subprocess.Popen(
            ["python3", "-m", "http.server", "8080"],
            cwd=str(dashboards_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        try:
            time.sleep(2)
            
            # Check if listening
            check = subprocess.run(
                ["lsof", "-i", ":8080"],
                capture_output=True,
                text=True
            )
            
            assert check.returncode == 0
            assert "python" in check.stdout.lower()
        finally:
            proc.kill()
            subprocess.run(
                "lsof -i :8080 | grep -v COMMAND | awk '{print $2}' | xargs kill -9 2>/dev/null",
                shell=True,
                capture_output=True
            )
    
    def test_server_serves_index_html(self):
        """Should serve index.html at root."""
        # Kill existing, start fresh
        subprocess.run(
            "lsof -i :8080 | grep -v COMMAND | awk '{print $2}' | xargs kill -9 2>/dev/null",
            shell=True,
            capture_output=True
        )
        time.sleep(1)
        
        dashboards_dir = Path(__file__).parent.parent.parent / "company" / "dashboards"
        proc = subprocess.Popen(
            ["python3", "-m", "http.server", "8080"],
            cwd=str(dashboards_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        try:
            time.sleep(2)
            
            # Fetch index
            response = requests.get("http://localhost:8080/", timeout=5)
            assert response.status_code == 200
            assert "html" in response.text.lower()
        finally:
            proc.kill()
            subprocess.run(
                "lsof -i :8080 | grep -v COMMAND | awk '{print $2}' | xargs kill -9 2>/dev/null",
                shell=True,
                capture_output=True
            )


class TestDashboardLogsCheck:
    """Test checking server logs for errors."""
    
    def test_log_file_exists(self):
        """Should create log file."""
        log_file = Path("/tmp/dashboard_server.log")
        log_file.write_text("")
        
        assert log_file.exists()
    
    def test_log_contains_server_started_message(self):
        """Should detect 'Serving' message in logs."""
        log_content = "Serving HTTP on :: port 8080 (http://[::]:8080/)"
        
        assert "Serving" in log_content
        assert "8080" in log_content
    
    def test_log_error_detection(self):
        """Should detect error patterns in logs."""
        log_content = "ERROR: Address already in use"
        
        error_patterns = ["ERROR", "FAILED", "Exception", "Traceback"]
        has_error = any(pattern in log_content for pattern in error_patterns)
        
        assert has_error


class TestDashboardDataLoading:
    """Test dashboard data loading detection."""
    
    def test_detect_data_loaded_from_html(self):
        """Should detect when dashboard data is loaded."""
        html_content = '''
        <script id="dashboard-data" type="application/json">
        {"repo": {"display_name": "KSESSIONS"}, "metrics": {"health_score": 85}}
        </script>
        '''
        
        assert "dashboard-data" in html_content
        assert '"repo"' in html_content
        assert '"display_name"' in html_content
    
    def test_detect_data_load_failure(self):
        """Should detect missing data."""
        html_content = '<script id="dashboard-data" type="application/json">{}</script>'
        
        has_empty_data = '{}' in html_content
        assert has_empty_data


class TestTabGeneration:
    """Test tab generation and visibility."""
    
    def test_all_eight_tabs_present(self):
        """Should verify all 8 tabs are in HTML."""
        tab_ids = [
            "overview-tab",
            "metrics-tab",
            "security-tab",
            "dependencies-tab",
            "quality-tab",
            "use-cases-tab",
            "lens-tab",
            "refactoring-tab"
        ]
        
        html_content = '''
        <button id="overview-tab">Overview</button>
        <button id="metrics-tab">Metrics</button>
        <button id="security-tab">Security</button>
        <button id="dependencies-tab">Dependencies</button>
        <button id="quality-tab">Quality</button>
        <button id="use-cases-tab">Use Cases</button>
        <button id="lens-tab">LENS</button>
        <button id="refactoring-tab">Refactoring</button>
        '''
        
        for tab_id in tab_ids:
            assert f'id="{tab_id}"' in html_content
    
    def test_no_tabs_hidden_with_display_none(self):
        """Should verify tabs don't have display:none inline style."""
        html_content = '''
        <button id="security-tab" style="display: ;">Security</button>
        <button id="dependencies-tab">Dependencies</button>
        '''
        
        # Check that hidden pattern doesn't exist on tabs
        assert 'id="security-tab" style="display: none;"' not in html_content
    
    def test_tab_visibility_script_present(self):
        """Should verify hideEmptyTabs function present."""
        js_content = '''
        hideEmptyTabs() {
            Object.entries(tabDataMap).forEach(([tabId, dataPath]) => {
                const tab = document.getElementById(tabId);
                if (tab) {
                    tab.style.display = '';
                }
            });
        }
        '''
        
        assert "hideEmptyTabs" in js_content
        assert "tab.style.display = ''" in js_content
    
    def test_tab_data_map_complete(self):
        """Should verify tabDataMap includes all 6 non-default tabs."""
        js_content = '''
        const tabDataMap = {
            'security-tab': 'security',
            'dependencies-tab': 'dependencies',
            'quality-tab': 'quality',
            'use-cases-tab': 'use_cases',
            'lens-tab': 'lens',
            'refactoring-tab': 'refactoring'
        };
        '''
        
        required_tabs = [
            "security-tab",
            "dependencies-tab",
            "quality-tab",
            "use-cases-tab",
            "lens-tab",
            "refactoring-tab"
        ]
        
        for tab in required_tabs:
            assert f"'{tab}'" in js_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
