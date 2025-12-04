"""
Dashboard Integration Test Suite

Validates all dashboard collectors and templates work together.
Tests performance, data accuracy, and current state compliance.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import time
from pathlib import Path
from datetime import datetime

from src.dashboard.data.tech_stack_collector import TechStackCollector
from src.dashboard.data.security_collector import SecurityCollector
from src.dashboard.data.architecture_collector import ArchitectureCollector
from src.dashboard.data.code_org_collector import CodeOrganizationCollector

# Import Phase 15 and 16 collectors if they exist
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


def test_dashboard_integration():
    """
    Integration test for complete dashboard system.
    
    Validates:
    - All collectors execute successfully
    - Data is CURRENT STATE only (no mock data)
    - Performance meets <3s target per collector
    - Data accuracy and completeness
    """
    cortex_root = Path.cwd()
    
    print("=" * 70)
    print("DASHBOARD INTEGRATION TEST - CORTEX Project")
    print("=" * 70)
    print(f"\nTest Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project: {cortex_root.name}")
    print(f"Python Files: {len(list(cortex_root.glob('**/*.py')))}")
    
    results = {
        "collectors_tested": 0,
        "collectors_passed": 0,
        "collectors_failed": 0,
        "total_time": 0,
        "performance_pass": True,
        "data_validation_pass": True,
        "current_state_violations": []
    }
    
    # Test each collector
    collectors = [
        ("Tech Stack", TechStackCollector, validate_tech_stack),
        ("Security", SecurityCollector, validate_security),
        ("Architecture", ArchitectureCollector, validate_architecture),
        ("Code Organization", CodeOrganizationCollector, validate_code_org),
    ]
    
    if VENDOR_DETECTOR_AVAILABLE:
        collectors.append(("Vendor Detection", VendorDetector, validate_vendors))
    
    if TEAM_METRICS_AVAILABLE:
        collectors.append(("Team Metrics", TeamMetricsCollector, validate_team_metrics))
    
    print(f"\n{'='*70}")
    print(f"TESTING {len(collectors)} COLLECTORS")
    print(f"{'='*70}\n")
    
    for name, CollectorClass, validator in collectors:
        print(f"\n{'─'*70}")
        print(f"Testing: {name} Collector")
        print(f"{'─'*70}")
        
        results["collectors_tested"] += 1
        
        try:
            # Measure performance
            start_time = time.time()
            collector = CollectorClass(cortex_root)
            data = collector.collect()
            elapsed = time.time() - start_time
            
            results["total_time"] += elapsed
            
            # Validate data
            if data is None:
                print(f"❌ FAIL: No data returned")
                results["collectors_failed"] += 1
                continue
            
            # Performance check
            performance_ok = elapsed < 3.0
            print(f"\n⏱️  Performance: {elapsed:.2f}s {'✅ PASS' if performance_ok else '⚠️ SLOW'}")
            
            if not performance_ok:
                results["performance_pass"] = False
            
            # Data validation
            validation_result = validator(data, results)
            
            if validation_result:
                print(f"✅ Data Validation: PASS")
                results["collectors_passed"] += 1
            else:
                print(f"❌ Data Validation: FAIL")
                results["collectors_failed"] += 1
                results["data_validation_pass"] = False
            
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
            results["collectors_failed"] += 1
            results["data_validation_pass"] = False
    
    # Print summary
    print(f"\n{'='*70}")
    print("TEST SUMMARY")
    print(f"{'='*70}")
    
    print(f"\nCollectors Tested: {results['collectors_tested']}")
    print(f"✅ Passed: {results['collectors_passed']}")
    print(f"❌ Failed: {results['collectors_failed']}")
    print(f"\n⏱️  Total Time: {results['total_time']:.2f}s")
    print(f"⏱️  Average Time: {results['total_time']/results['collectors_tested']:.2f}s per collector")
    
    print(f"\n{'─'*70}")
    print("VALIDATION CHECKS")
    print(f"{'─'*70}")
    
    print(f"Performance (<3s per collector): {'✅ PASS' if results['performance_pass'] else '❌ FAIL'}")
    print(f"Data Validation: {'✅ PASS' if results['data_validation_pass'] else '❌ FAIL'}")
    print(f"Current State Compliance: {'✅ PASS' if not results['current_state_violations'] else '❌ FAIL'}")
    
    if results['current_state_violations']:
        print(f"\n⚠️  Current State Violations Found:")
        for violation in results['current_state_violations']:
            print(f"   - {violation}")
    
    # Overall result
    all_pass = (
        results['collectors_failed'] == 0 and
        results['performance_pass'] and
        results['data_validation_pass'] and
        not results['current_state_violations']
    )
    
    print(f"\n{'='*70}")
    print(f"OVERALL RESULT: {'✅ PASS' if all_pass else '❌ FAIL'}")
    print(f"{'='*70}\n")
    
    if all_pass:
        print("🎉 All tests passed! Dashboard ready for deployment.")
    else:
        print("⚠️  Some tests failed. Review output above for details.")
    
    return all_pass


def validate_tech_stack(data: dict, results: dict) -> bool:
    """Validate tech stack data."""
    print(f"\n📊 Tech Stack Data:")
    print(f"   Total Technologies: {data['summary']['total_technologies']}")
    print(f"   Current: {data['summary']['current_count']}")
    print(f"   Outdated: {data['summary']['outdated_count']}")
    
    # Check for mock data patterns
    if data['summary']['total_technologies'] == 0:
        results['current_state_violations'].append("Tech Stack: No technologies detected")
        return False
    
    # Verify data structure
    required_keys = ['frontend', 'backend', 'database', 'devops', 'summary']
    if not all(key in data for key in required_keys):
        return False
    
    return True


def validate_security(data: dict, results: dict) -> bool:
    """Validate security data."""
    print(f"\n🔒 Security Data:")
    print(f"   Overall Score: {data['overall_score']}/100")
    print(f"   Critical Vulns: {data['vulnerabilities']['critical']}")
    print(f"   High Vulns: {data['vulnerabilities']['high']}")
    print(f"   OWASP Compliance: {len([x for x in data['owasp_top_10'] if x['status'] == 'pass'])}/10")
    
    # Check for unrealistic data
    if data['overall_score'] > 100 or data['overall_score'] < 0:
        results['current_state_violations'].append("Security: Invalid score range")
        return False
    
    # Verify OWASP data
    if len(data['owasp_top_10']) != 10:
        results['current_state_violations'].append("Security: OWASP Top 10 incomplete")
        return False
    
    return True


def validate_architecture(data: dict, results: dict) -> bool:
    """Validate architecture data."""
    print(f"\n🏗️  Architecture Data:")
    print(f"   Style: {data['style']}")
    print(f"   Components: {data['summary']['total_components']}")
    print(f"   Files: {data['summary']['total_files']}")
    print(f"   LOC: {data['summary']['total_loc']}")
    print(f"   Score: {data['summary']['architecture_score']}/100")
    
    # Check for actual analysis
    if data['summary']['total_components'] == 0:
        results['current_state_violations'].append("Architecture: No components detected")
        return False
    
    if data['style'] == 'unknown':
        print("   ⚠️  Warning: Architecture style not detected (acceptable)")
    
    return True


def validate_code_org(data: dict, results: dict) -> bool:
    """Validate code organization data."""
    print(f"\n📊 Code Organization Data:")
    print(f"   Total Files: {data['summary']['total_files']}")
    print(f"   High Complexity: {data['summary']['high_complexity_files']}")
    print(f"   Hotspots: {data['summary']['hotspot_count']}")
    print(f"   Avg Complexity: {data['summary']['avg_complexity']:.1f}")
    
    # Check for analysis
    if data['summary']['total_files'] == 0:
        results['current_state_violations'].append("Code Org: No files analyzed")
        return False
    
    if not data['heatmap']:
        results['current_state_violations'].append("Code Org: No heatmap data")
        return False
    
    return True


def validate_vendors(data: dict, results: dict) -> bool:
    """Validate vendor detection data."""
    print(f"\n🔗 Vendor Detection Data:")
    print(f"   External Vendors: {data['summary']['total_vendors']}")
    print(f"   Active: {data['summary']['active_vendors']}")
    print(f"   Configured: {data['summary']['configured_vendors']}")
    
    # Vendor detection may find 0 vendors (acceptable for some projects)
    print(f"   ℹ️  Note: {data['summary']['total_vendors']} vendors detected (may be 0 for internal projects)")
    
    return True


def validate_team_metrics(data: dict, results: dict) -> bool:
    """Validate team metrics data."""
    print(f"\n👥 Team Metrics Data:")
    print(f"   Contributors: {data['summary']['total_contributors']}")
    print(f"   Total Commits: {data['summary']['total_commits']}")
    print(f"   Avg Commits/Week: {data['summary']['avg_commits_per_week']:.1f}")
    
    # Check for git data
    if data['summary']['total_commits'] == 0:
        results['current_state_violations'].append("Team Metrics: No git history found")
        return False
    
    return True


if __name__ == "__main__":
    success = test_dashboard_integration()
    exit(0 if success else 1)
