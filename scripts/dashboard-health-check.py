#!/usr/bin/env python3
"""
CORTEX Dashboard Health Check
Verifies all dashboard components are working correctly
"""

import sys
import subprocess
import time
import requests
import json
from pathlib import Path

class DashboardHealthCheck:
    def __init__(self):
        self.results = []
        self.api_base = "http://localhost:8000"
        self.frontend_base = "http://localhost:8080"
    
    def log(self, status, message):
        """Log check results"""
        symbol = "✓" if status else "✗"
        self.results.append((status, message))
        print(f"{symbol} {message}")
    
    def check_api_health(self):
        """Check if API backend is running"""
        try:
            response = requests.get(f"{self.api_base}/api/health", timeout=2)
            if response.status_code == 200:
                self.log(True, "API backend running on port 8000")
                return True
            else:
                self.log(False, f"API returned status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.log(False, "Cannot connect to API on port 8000")
            self.log(False, "  → Start with: python -m uvicorn src.dashboard.api.main:app --port 8000 --reload")
            return False
        except Exception as e:
            self.log(False, f"API check failed: {e}")
            return False
    
    def check_api_endpoints(self):
        """Check all API endpoints"""
        endpoints = [
            ('/api/health', 'Health Check'),
            ('/api/brain/tiers', 'Brain Tiers'),
            ('/api/brain/metrics', 'SSOT Metrics'),
            ('/api/audit/entries?limit=5', 'Audit Entries'),
            ('/api/orchestrators', 'Orchestrators'),
        ]
        
        all_ok = True
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{self.api_base}{endpoint}", timeout=2)
                if response.status_code == 200:
                    self.log(True, f"  {name} endpoint responding")
                else:
                    self.log(False, f"  {name} returned status {response.status_code}")
                    all_ok = False
            except Exception as e:
                self.log(False, f"  {name} failed: {e}")
                all_ok = False
        
        return all_ok
    
    def check_frontend_server(self):
        """Check if frontend server is running"""
        try:
            response = requests.get(self.frontend_base, timeout=2)
            if response.status_code == 200:
                self.log(True, "Frontend server running on port 8080")
                return True
            else:
                self.log(False, f"Frontend returned status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.log(False, "Cannot connect to frontend on port 8080")
            self.log(False, "  → Start with: cd src/dashboard/frontend && python -m http.server 8080")
            return False
        except Exception as e:
            self.log(False, f"Frontend check failed: {e}")
            return False
    
    def check_frontend_assets(self):
        """Check if frontend assets are accessible"""
        assets = [
            ('/index.html', 'Main HTML'),
            ('/css/glassmorphism.css', 'Glassmorphism CSS'),
            ('/css/animations.css', 'Animation CSS'),
            ('/js/utils/api-client.js', 'API Client'),
            ('/js/components/brain/brain-map.js', 'Brain Map Component'),
            ('/js/components/neural/neural-pulse.js', 'Neural Pulse Component'),
            ('/js/components/temporal/audit-timeline.js', 'Audit Timeline Component'),
            ('/js/components/orchestrator/orchestrator-grid.js', 'Orchestrator Grid Component'),
            ('/js/app.js', 'App Initialization'),
        ]
        
        all_ok = True
        for asset, name in assets:
            try:
                response = requests.get(f"{self.frontend_base}{asset}", timeout=2)
                if response.status_code == 200:
                    self.log(True, f"  {name} loaded")
                else:
                    self.log(False, f"  {name} returned status {response.status_code}")
                    all_ok = False
            except Exception as e:
                self.log(False, f"  {name} failed: {e}")
                all_ok = False
        
        return all_ok
    
    def check_tests(self):
        """Run dashboard tests"""
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', 
                 'tests/unit/dashboard/test_api_endpoints.py', '-v', '--tb=short'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Count passed tests
                passed = result.stdout.count(' PASSED')
                self.log(True, f"All {passed} dashboard tests passing")
                return True
            else:
                self.log(False, "Some tests failed")
                print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
                return False
        except subprocess.TimeoutExpired:
            self.log(False, "Tests timed out")
            return False
        except Exception as e:
            self.log(False, f"Test execution failed: {e}")
            return False
    
    def run_all_checks(self):
        """Run all health checks"""
        print("\n" + "="*60)
        print("CORTEX Neural Observatory Dashboard Health Check")
        print("="*60 + "\n")
        
        print("1. Checking API Backend...")
        api_ok = self.check_api_health()
        
        if api_ok:
            print("\n2. Checking API Endpoints...")
            self.check_api_endpoints()
        
        print("\n3. Checking Frontend Server...")
        frontend_ok = self.check_frontend_server()
        
        if frontend_ok:
            print("\n4. Checking Frontend Assets...")
            self.check_frontend_assets()
        
        print("\n5. Running Dashboard Tests...")
        self.check_tests()
        
        print("\n" + "="*60)
        print("Summary")
        print("="*60)
        
        passed = sum(1 for status, _ in self.results if status)
        total = len(self.results)
        
        print(f"Passed: {passed}/{total}")
        
        if passed == total:
            print("\n✓ All checks passed! Dashboard is ready.")
            print(f"\n  Open your browser to: {self.frontend_base}")
            return 0
        else:
            print("\n✗ Some checks failed. See above for details.")
            return 1

if __name__ == '__main__':
    checker = DashboardHealthCheck()
    exit_code = checker.run_all_checks()
    sys.exit(exit_code)
