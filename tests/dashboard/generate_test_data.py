"""
Dashboard Test Data Generator

Runs all dashboard data collectors ONCE and saves output to JSON files.
Provides progress feedback to prevent perceived hang-ups.

Usage:
    python tests/dashboard/generate_test_data.py
    
Output:
    tests/dashboard/test_data/*.json - Generated data files
    
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.data_collector import DashboardDataCollector
from src.dashboard.data.tech_stack_collector import TechStackCollector
from src.dashboard.data.security_collector import SecurityCollector
from src.dashboard.data.architecture_collector import ArchitectureCollector
from src.dashboard.data.code_org_collector import CodeOrganizationCollector

# Optional collectors
try:
    from src.dashboard.data.vendor_detector import VendorDetector
    VENDOR_DETECTOR_AVAILABLE = True
except ImportError:
    VENDOR_DETECTOR_AVAILABLE = False

try:
    from src.dashboard.data.team_metrics_collector import TeamMetricsCollector
    TEAM_METRICS_AVAILABLE = True
except ImportError:
    TEAM_METRICS_AVAILABLE = False


class TestDataGenerator:
    """Generates test data from all dashboard collectors"""
    
    def __init__(self, output_dir: Path = None):
        """
        Initialize test data generator.
        
        Args:
            output_dir: Directory to save generated data (default: tests/dashboard/test_data)
        """
        self.cortex_root = Path.cwd()
        self.brain_path = self.cortex_root / "cortex-brain"
        
        if output_dir is None:
            self.output_dir = Path(__file__).parent / "test_data"
        else:
            self.output_dir = Path(output_dir)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.results = {
            "success": [],
            "failed": [],
            "skipped": [],
            "start_time": None,
            "end_time": None,
            "total_duration": 0
        }
    
    def print_header(self):
        """Print generation header"""
        print("=" * 80)
        print("CORTEX DASHBOARD TEST DATA GENERATOR")
        print("=" * 80)
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Project: {self.cortex_root.name}")
        print(f"Output Directory: {self.output_dir}")
        print("=" * 80)
        print()
    
    def print_progress(self, collector_name: str, status: str):
        """Print progress update"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        symbols = {
            "START": "[...]",
            "SUCCESS": "[OK]",
            "FAILED": "[FAIL]",
            "SKIP": "[SKIP]"
        }
        symbol = symbols.get(status, "[?]")
        print(f"{timestamp} {symbol} {collector_name}")
    
    def save_json(self, filename: str, data: dict):
        """Save data to JSON file"""
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        return filepath
    
    def collect_executive_summary(self):
        """Collect executive summary data"""
        collector_name = "Executive Summary"
        self.print_progress(collector_name, "START")
        
        try:
            start = time.time()
            collector = DashboardDataCollector(self.brain_path)
            data = collector.collect_executive_summary(self.cortex_root)
            elapsed = time.time() - start
            
            if data:
                filepath = self.save_json("executive-summary.json", data)
                self.results["success"].append({
                    "name": collector_name,
                    "file": str(filepath),
                    "duration": elapsed
                })
                self.print_progress(f"{collector_name} ({elapsed:.2f}s)", "SUCCESS")
            else:
                self.results["failed"].append(collector_name)
                self.print_progress(collector_name, "FAILED")
                
        except Exception as e:
            self.results["failed"].append(collector_name)
            self.print_progress(f"{collector_name}: {str(e)}", "FAILED")
    
    def collect_tech_stack(self):
        """Collect tech stack data"""
        collector_name = "Tech Stack"
        self.print_progress(collector_name, "START")
        
        try:
            start = time.time()
            collector = TechStackCollector(self.cortex_root)
            data = collector.collect()
            elapsed = time.time() - start
            
            if data:
                filepath = self.save_json("tech-stack.json", data)
                self.results["success"].append({
                    "name": collector_name,
                    "file": str(filepath),
                    "duration": elapsed
                })
                self.print_progress(f"{collector_name} ({elapsed:.2f}s)", "SUCCESS")
            else:
                self.results["failed"].append(collector_name)
                self.print_progress(collector_name, "FAILED")
                
        except Exception as e:
            self.results["failed"].append(collector_name)
            self.print_progress(f"{collector_name}: {str(e)}", "FAILED")
    
    def collect_security(self):
        """Collect security data"""
        collector_name = "Security"
        self.print_progress(collector_name, "START")
        print("  (This may take 60-90 seconds - scanning for vulnerabilities...)")
        
        try:
            start = time.time()
            collector = SecurityCollector(self.cortex_root)
            data = collector.collect()
            elapsed = time.time() - start
            
            if data:
                filepath = self.save_json("security.json", data)
                self.results["success"].append({
                    "name": collector_name,
                    "file": str(filepath),
                    "duration": elapsed
                })
                self.print_progress(f"{collector_name} ({elapsed:.2f}s)", "SUCCESS")
            else:
                self.results["failed"].append(collector_name)
                self.print_progress(collector_name, "FAILED")
                
        except Exception as e:
            self.results["failed"].append(collector_name)
            self.print_progress(f"{collector_name}: {str(e)}", "FAILED")
    
    def collect_architecture(self):
        """Collect architecture data"""
        collector_name = "Architecture"
        self.print_progress(collector_name, "START")
        
        try:
            start = time.time()
            collector = ArchitectureCollector(self.cortex_root)
            data = collector.collect()
            elapsed = time.time() - start
            
            if data:
                filepath = self.save_json("architecture.json", data)
                self.results["success"].append({
                    "name": collector_name,
                    "file": str(filepath),
                    "duration": elapsed
                })
                self.print_progress(f"{collector_name} ({elapsed:.2f}s)", "SUCCESS")
            else:
                self.results["failed"].append(collector_name)
                self.print_progress(collector_name, "FAILED")
                
        except Exception as e:
            self.results["failed"].append(collector_name)
            self.print_progress(f"{collector_name}: {str(e)}", "FAILED")
    
    def collect_code_organization(self):
        """Collect code organization data"""
        collector_name = "Code Organization"
        self.print_progress(collector_name, "START")
        
        try:
            start = time.time()
            collector = CodeOrganizationCollector(self.cortex_root)
            data = collector.collect()
            elapsed = time.time() - start
            
            if data:
                filepath = self.save_json("code-organization.json", data)
                self.results["success"].append({
                    "name": collector_name,
                    "file": str(filepath),
                    "duration": elapsed
                })
                self.print_progress(f"{collector_name} ({elapsed:.2f}s)", "SUCCESS")
            else:
                self.results["failed"].append(collector_name)
                self.print_progress(collector_name, "FAILED")
                
        except Exception as e:
            self.results["failed"].append(collector_name)
            self.print_progress(f"{collector_name}: {str(e)}", "FAILED")
    
    def collect_vendors(self):
        """Collect vendors data (optional)"""
        if not VENDOR_DETECTOR_AVAILABLE:
            self.results["skipped"].append("Vendors")
            self.print_progress("Vendors (not available)", "SKIP")
            return
        
        collector_name = "Vendors"
        self.print_progress(collector_name, "START")
        
        try:
            start = time.time()
            collector = VendorDetector(self.cortex_root)
            data = collector.collect()
            elapsed = time.time() - start
            
            if data:
                filepath = self.save_json("vendors.json", data)
                self.results["success"].append({
                    "name": collector_name,
                    "file": str(filepath),
                    "duration": elapsed
                })
                self.print_progress(f"{collector_name} ({elapsed:.2f}s)", "SUCCESS")
            else:
                self.results["failed"].append(collector_name)
                self.print_progress(collector_name, "FAILED")
                
        except Exception as e:
            self.results["failed"].append(collector_name)
            self.print_progress(f"{collector_name}: {str(e)}", "FAILED")
    
    def collect_team_metrics(self):
        """Collect team metrics data (optional)"""
        if not TEAM_METRICS_AVAILABLE:
            self.results["skipped"].append("Team Metrics")
            self.print_progress("Team Metrics (not available)", "SKIP")
            return
        
        collector_name = "Team Metrics"
        self.print_progress(collector_name, "START")
        
        try:
            start = time.time()
            collector = TeamMetricsCollector(self.cortex_root)
            data = collector.collect()
            elapsed = time.time() - start
            
            if data:
                filepath = self.save_json("team-metrics.json", data)
                self.results["success"].append({
                    "name": collector_name,
                    "file": str(filepath),
                    "duration": elapsed
                })
                self.print_progress(f"{collector_name} ({elapsed:.2f}s)", "SUCCESS")
            else:
                self.results["failed"].append(collector_name)
                self.print_progress(collector_name, "FAILED")
                
        except Exception as e:
            self.results["failed"].append(collector_name)
            self.print_progress(f"{collector_name}: {str(e)}", "FAILED")
    
    def generate_all(self):
        """Generate all test data"""
        self.print_header()
        self.results["start_time"] = datetime.now()
        
        print("Phase 1: Collecting Data from All Collectors")
        print("-" * 80)
        
        # Run all collectors
        self.collect_executive_summary()
        self.collect_tech_stack()
        self.collect_security()
        self.collect_architecture()
        self.collect_code_organization()
        self.collect_vendors()
        self.collect_team_metrics()
        
        self.results["end_time"] = datetime.now()
        self.results["total_duration"] = (
            self.results["end_time"] - self.results["start_time"]
        ).total_seconds()
        
        # Print summary
        self.print_summary()
        
        return len(self.results["failed"]) == 0
    
    def print_summary(self):
        """Print generation summary"""
        print()
        print("=" * 80)
        print("DATA GENERATION SUMMARY")
        print("=" * 80)
        
        print(f"\nSuccessful: {len(self.results['success'])}")
        for item in self.results["success"]:
            print(f"  * {item['name']:20s} -> {item['file']} ({item['duration']:.2f}s)")
        
        if self.results["failed"]:
            print(f"\nFailed: {len(self.results['failed'])}")
            for item in self.results["failed"]:
                print(f"  * {item}")
        
        if self.results["skipped"]:
            print(f"\nSkipped: {len(self.results['skipped'])}")
            for item in self.results["skipped"]:
                print(f"  * {item}")
        
        print(f"\nTotal Duration: {self.results['total_duration']:.2f}s")
        print(f"Output Directory: {self.output_dir.absolute()}")
        
        print()
        if self.results["failed"]:
            print("[FAIL] Some collectors failed")
        else:
            print("[PASS] All collectors successful")
        print("=" * 80)
        print()


def main():
    """Main entry point"""
    generator = TestDataGenerator()
    success = generator.generate_all()
    
    if success:
        print("\nNext Step: Run integration tests")
        print("  pytest tests/dashboard/test_all_tabs_data_contract.py -v\n")
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
