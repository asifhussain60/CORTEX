"""
Pytest Configuration for Dashboard Testing

Provides fixtures for Selenium WebDriver, dashboard server, and test data.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
import time
import socket
import threading
import http.server
import socketserver
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait


# Dashboard server configuration
DASHBOARD_PORT = 8080
DASHBOARD_DIR = Path(__file__).parent.parent


def find_free_port(start_port=8080, max_attempts=10):
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("localhost", port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"No free port found in range {start_port}-{start_port + max_attempts}")


class DashboardServer:
    """HTTP server for serving dashboard files during testing."""
    
    def __init__(self, port):
        self.port = port
        self.thread = None
        self.httpd = None
        
    def start(self):
        """Start the HTTP server in a background thread."""
        Handler = http.server.SimpleHTTPRequestHandler
        
        class CustomHandler(Handler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(DASHBOARD_DIR), **kwargs)
            
            def log_message(self, format, *args):
                pass  # Suppress server logs during testing
        
        self.httpd = socketserver.TCPServer(("localhost", self.port), CustomHandler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        time.sleep(0.5)  # Wait for server to be ready
        
    def stop(self):
        """Stop the HTTP server."""
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()


@pytest.fixture(scope="session")
def dashboard_server():
    """Start dashboard HTTP server for the test session."""
    port = find_free_port()
    server = DashboardServer(port)
    server.start()
    yield f"http://localhost:{port}"
    server.stop()


@pytest.fixture(scope="function")
def chrome_driver():
    """Create Chrome WebDriver instance with headless options."""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-file-access-from-files")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(5)
    
    yield driver
    
    driver.quit()


@pytest.fixture(scope="function")
def wait(chrome_driver):
    """Create WebDriverWait instance for explicit waits."""
    return WebDriverWait(chrome_driver, 10)


@pytest.fixture(scope="session")
def mock_data_path():
    """Path to mock data directory."""
    # PHASE 2 REFACTOR: mock data moved to data/repositories/mock
    return DASHBOARD_DIR / "data" / "repositories" / "mock"


@pytest.fixture(scope="session")
def test_data():
    """Load test data from mock directory."""
    import json
    mock_path = DASHBOARD_DIR.parent / "data" / "mock"
    
    data = {}
    for json_file in mock_path.glob("*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            data[json_file.stem] = json.load(f)
    
    return data


# Test markers
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "slow: Slow-running tests")
    config.addinivalue_line("markers", "component: Component-level tests")
