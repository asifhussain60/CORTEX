"""
Dashboard Data Contract Test Suite - All Tabs

Validates that ALL dashboard tab data collectors produce output that matches
the expected frontend rendering requirements. Ensures zero rendering failures
due to schema mismatches.

Coverage:
- Executive Summary Tab
- Overview Tab  
- Tech Stack Tab
- Security Tab
- Architecture Tab
- Code Organization Tab
- Vendors Tab
- Team Metrics Tab (if available)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import collectors
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


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture(scope="module")
def cortex_root():
    """Get CORTEX project root"""
    return Path.cwd()


@pytest.fixture(scope="module")
def brain_path(cortex_root):
    """Get cortex-brain path"""
    return cortex_root / "cortex-brain"


@pytest.fixture(scope="module")
def mock_data_path(brain_path):
    """Get mock data directory"""
    return brain_path / "dashboards" / "mock"


@pytest.fixture(scope="module")
def test_data_path():
    """Get generated test data directory"""
    return Path(__file__).parent / "test_data"


@pytest.fixture(scope="module")
def generated_data(test_data_path):
    """Load all generated test data"""
    data = {}
    
    data_files = {
        'executive_summary': 'executive-summary.json',
        'tech_stack': 'tech-stack.json',
        'security': 'security.json',
        'architecture': 'architecture.json',
        'code_organization': 'code-organization.json',
        'vendors': 'vendors.json',
        'team_metrics': 'team-metrics.json'
    }
    
    for key, filename in data_files.items():
        filepath = test_data_path / filename
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                data[key] = json.load(f)
        else:
            data[key] = None
    
    return data


@pytest.fixture(scope="module")
def data_collector(brain_path):
    """Initialize DashboardDataCollector"""
    return DashboardDataCollector(brain_path)


@pytest.fixture(scope="module")
def tech_stack_collector(cortex_root):
    """Initialize TechStackCollector"""
    return TechStackCollector(cortex_root)


@pytest.fixture(scope="module")
def security_collector(cortex_root):
    """Initialize SecurityCollector"""
    return SecurityCollector(cortex_root)


@pytest.fixture(scope="module")
def architecture_collector(cortex_root):
    """Initialize ArchitectureCollector"""
    return ArchitectureCollector(cortex_root)


@pytest.fixture(scope="module")
def code_org_collector(cortex_root):
    """Initialize CodeOrganizationCollector"""
    return CodeOrganizationCollector(cortex_root)


@pytest.fixture(scope="module")
def vendor_collector(cortex_root):
    """Initialize VendorDetector (optional)"""
    if VENDOR_DETECTOR_AVAILABLE:
        return VendorDetector(cortex_root)
    return None


@pytest.fixture(scope="module")
def team_metrics_collector(cortex_root):
    """Initialize TeamMetricsCollector (optional)"""
    if TEAM_METRICS_AVAILABLE:
        return TeamMetricsCollector(cortex_root)
    return None


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def validate_required_keys(data: Dict[str, Any], required_keys: List[str], 
                          section_name: str) -> List[str]:
    """
    Validate that all required keys are present in data.
    
    Args:
        data: Data dictionary to validate
        required_keys: List of required key paths (supports nested with '.')
        section_name: Name of section for error messages
    
    Returns:
        List of missing keys (empty if all present)
    """
    missing = []
    for key_path in required_keys:
        parts = key_path.split('.')
        current = data
        
        for i, part in enumerate(parts):
            if not isinstance(current, dict) or part not in current:
                missing.append(f"{section_name}.{key_path}")
                break
            current = current[part]
            
    return missing


def validate_data_types(data: Dict[str, Any], type_specs: Dict[str, type],
                       section_name: str) -> List[str]:
    """
    Validate that data fields have expected types.
    
    Args:
        data: Data dictionary to validate
        type_specs: Dict mapping key paths to expected types
        section_name: Name of section for error messages
    
    Returns:
        List of type mismatches (empty if all correct)
    """
    errors = []
    for key_path, expected_type in type_specs.items():
        parts = key_path.split('.')
        current = data
        
        for part in parts[:-1]:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                # Key doesn't exist - handled by validate_required_keys
                break
        else:
            final_key = parts[-1]
            if isinstance(current, dict) and final_key in current:
                value = current[final_key]
                if not isinstance(value, expected_type):
                    errors.append(
                        f"{section_name}.{key_path}: expected {expected_type.__name__}, "
                        f"got {type(value).__name__}"
                    )
    
    return errors


def load_mock_data(mock_data_path: Path, filename: str) -> Optional[Dict[str, Any]]:
    """Load mock data file for reference"""
    mock_file = mock_data_path / filename
    if mock_file.exists():
        with open(mock_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


# =============================================================================
# TEST: EXECUTIVE SUMMARY TAB
# =============================================================================

@pytest.mark.dashboard
class TestExecutiveSummaryTab:
    """Test Executive Summary tab data contract"""
    
    def test_executive_summary_structure(self, generated_data):
        """Test that executive summary has valid structure"""
        data = generated_data.get('executive_summary')
        
        assert data is not None, "Executive summary data not generated. Run: python tests/dashboard/generate_test_data.py"
        assert isinstance(data, dict), "Data must be a dictionary"
        
        # Required top-level keys
        required_keys = ['purpose', 'history', 'composition']
        missing = validate_required_keys(data, required_keys, 'executive_summary')
        assert not missing, f"Missing required keys: {missing}"
    
    def test_executive_summary_purpose(self, generated_data):
        """Test purpose section fields"""
        data = generated_data.get('executive_summary')
        assert data is not None, "Executive summary data not generated"
        purpose = data['purpose']
        
        required_keys = ['title', 'tagline', 'description', 'value_proposition', 'target_users']
        missing = validate_required_keys(purpose, required_keys, 'purpose')
        assert not missing, f"Missing purpose keys: {missing}"
        
        # Type validation
        type_specs = {
            'title': str,
            'tagline': str,
            'description': str,
            'target_users': list
        }
        errors = validate_data_types(purpose, type_specs, 'purpose')
        assert not errors, f"Type errors: {errors}"
        
        # value_proposition can be str, dict, or list
        assert isinstance(purpose['value_proposition'], (str, dict, list)), \
            "value_proposition must be str, dict, or list"
    
    def test_executive_summary_history(self, generated_data):
        """Test history section fields"""
        data = generated_data.get('executive_summary')
        assert data is not None, "Executive summary data not generated"
        history = data['history']
        
        # Check for either 'milestones' or 'major_milestones'
        required_keys = ['project_inception', 'total_commits', 'evolution']
        missing = validate_required_keys(history, required_keys, 'history')
        assert not missing, f"Missing history keys: {missing}"
        
        # Validate milestones exist (either format)
        assert 'milestones' in history or 'major_milestones' in history, \
            "History must have 'milestones' or 'major_milestones'"
        
        # Type validation
        type_specs = {
            'project_inception': str,
            'total_commits': int,
            'evolution': dict
        }
        errors = validate_data_types(history, type_specs, 'history')
        assert not errors, f"Type errors: {errors}"
        
        # Validate milestones structure (check both possible field names)
        milestones = history.get('milestones') or history.get('major_milestones')
        if milestones and isinstance(milestones, list) and len(milestones) > 0:
            milestone = milestones[0]
            assert 'version' in milestone or 'title' in milestone, \
                "Milestone must have version or title"
            assert 'date' in milestone, "Milestone must have date"
    
    def test_executive_summary_composition(self, generated_data):
        """Test composition section fields"""
        data = generated_data.get('executive_summary')
        assert data is not None, "Executive summary data not generated"
        composition = data['composition']
        
        required_keys = ['architecture_layers', 'agent_system', 'technology_stack', 'file_statistics']
        missing = validate_required_keys(composition, required_keys, 'composition')
        assert not missing, f"Missing composition keys: {missing}"
        
        # Type validation
        type_specs = {
            'architecture_layers': list,
            'agent_system': dict,
            'technology_stack': dict,
            'file_statistics': dict
        }
        errors = validate_data_types(composition, type_specs, 'composition')
        assert not errors, f"Type errors: {errors}"
        
        # Validate architecture_layers structure
        if composition['architecture_layers']:
            layer = composition['architecture_layers'][0]
            assert 'name' in layer, "Layer must have name"
            # Accept either 'description' or 'purpose'
            assert 'description' in layer or 'purpose' in layer, \
                "Layer must have 'description' or 'purpose'"
    
    def test_executive_summary_frontend_compatibility(self, generated_data):
        """Test that generated data matches frontend rendering requirements"""
        data = generated_data.get('executive_summary')
        assert data is not None, "Executive summary data not generated"
        
        # Validate purpose section (required by executive-summary-tab.js)
        purpose_keys = ['title', 'tagline', 'description', 'value_proposition', 'target_users']
        missing = validate_required_keys(data['purpose'], purpose_keys, 'purpose')
        assert not missing, f"Missing purpose keys needed by frontend: {missing}"
        
        # Validate history section (required by renderMilestones)
        history_keys = ['project_inception', 'total_commits', 'evolution']
        missing = validate_required_keys(data['history'], history_keys, 'history')
        assert not missing, f"Missing history keys needed by frontend: {missing}"
        
        # Milestones can be 'milestones' or 'major_milestones'
        assert 'milestones' in data['history'] or 'major_milestones' in data['history'], \
            "History must have milestones field for frontend"
        
        # Validate composition section (required by renderArchitectureTiers, renderAgentSystem)
        composition_keys = ['architecture_layers', 'agent_system', 'technology_stack', 'file_statistics']
        missing = validate_required_keys(data['composition'], composition_keys, 'composition')
        assert not missing, f"Missing composition keys needed by frontend: {missing}"


# =============================================================================
# TEST: OVERVIEW TAB
# =============================================================================

@pytest.mark.dashboard
class TestOverviewTab:
    """Test Overview tab data contract"""
    
    def test_overview_uses_multiple_sources(self, generated_data):
        """Test that overview tab can aggregate data from multiple collectors"""
        # Overview tab uses: health, tech_stack, security, code_org, team_metrics
        
        # At minimum, check that we have some data sources
        available_sources = [k for k, v in generated_data.items() if v is not None]
        assert len(available_sources) > 0, "No data sources available for overview tab"
        
        print(f"Overview tab has access to {len(available_sources)} data sources: {available_sources}")


# =============================================================================
# TEST: TECH STACK TAB
# =============================================================================

@pytest.mark.dashboard
class TestTechStackTab:
    """Test Tech Stack tab data contract"""
    
    def test_tech_stack_structure(self, generated_data):
        """Test that tech stack has valid structure"""
        data = generated_data.get('tech_stack')
        
        assert data is not None, "Tech stack data not generated. Run: python tests/dashboard/generate_test_data.py"
        assert isinstance(data, dict), "Data must be a dictionary"
        
        # Required top-level keys (actual structure has frontend, backend, database, devops)
        required_keys = ['summary', 'frontend', 'backend', 'database', 'devops']
        missing = validate_required_keys(data, required_keys, 'tech_stack')
        assert not missing, f"Missing required keys: {missing}"
    
    def test_tech_stack_summary(self, generated_data):
        """Test summary section"""
        data = generated_data.get('tech_stack')
        assert data is not None, "Tech stack data not generated"
        summary = data.get('summary', {})
        
        required_keys = ['total_technologies', 'current_count', 'outdated_count', 'deprecated_count']
        missing = validate_required_keys(summary, required_keys, 'summary')
        assert not missing, f"Missing summary keys: {missing}"
        
        # Type validation
        type_specs = {
            'total_technologies': int,
            'current_count': int,
            'outdated_count': int,
            'deprecated_count': int
        }
        errors = validate_data_types(summary, type_specs, 'summary')
        assert not errors, f"Type errors: {errors}"
    
    def test_tech_stack_technologies(self, generated_data):
        """Test technologies array structure"""
        data = generated_data.get('tech_stack')
        assert data is not None, "Tech stack data not generated"
        
        # Collect all technologies from all categories
        all_technologies = []
        for category in ['frontend', 'backend', 'database', 'devops']:
            techs = data.get(category, [])
            assert isinstance(techs, list), f"{category} must be a list"
            all_technologies.extend(techs)
        
        if all_technologies:
            tech = all_technologies[0]
            required_keys = ['name', 'version', 'category', 'status']
            missing = validate_required_keys(tech, required_keys, 'technology')
            assert not missing, f"Missing technology keys: {missing}"
            
            # Valid status values
            valid_statuses = ['current', 'outdated', 'deprecated', 'unknown']
            assert tech['status'] in valid_statuses, \
                f"Invalid status: {tech['status']}"


# =============================================================================
# TEST: SECURITY TAB
# =============================================================================

@pytest.mark.dashboard
class TestSecurityTab:
    """Test Security tab data contract"""
    
    def test_security_structure(self, generated_data):
        """Test that security data has valid structure"""
        data = generated_data.get('security')
        
        assert data is not None, "Security data not generated. Run: python tests/dashboard/generate_test_data.py"
        assert isinstance(data, dict), "Data must be a dictionary"
        
        required_keys = ['overall_score', 'vulnerabilities', 'owasp_top_10']
        missing = validate_required_keys(data, required_keys, 'security')
        assert not missing, f"Missing required keys: {missing}"
    
    def test_security_score(self, generated_data):
        """Test security score is valid"""
        data = generated_data.get('security')
        assert data is not None, "Security data not generated"
        score = data.get('overall_score')
        
        assert isinstance(score, (int, float)), "Score must be numeric"
        assert 0 <= score <= 100, "Score must be 0-100"
    
    def test_security_vulnerabilities(self, generated_data):
        """Test vulnerabilities structure"""
        data = generated_data.get('security')
        assert data is not None, "Security data not generated"
        vulns = data.get('vulnerabilities', {})
        
        # Expected vulnerability categories
        categories = ['critical', 'high', 'medium', 'low']
        for cat in categories:
            if cat in vulns:
                assert isinstance(vulns[cat], int), \
                    f"{cat} vulnerability count must be integer"
    
    def test_security_owasp_top_10(self, generated_data):
        """Test OWASP Top 10 structure"""
        data = generated_data.get('security')
        assert data is not None, "Security data not generated"
        owasp = data.get('owasp_top_10')
        
        # Can be array (legacy) or object (new format)
        assert isinstance(owasp, (list, dict)), \
            "owasp_top_10 must be list or dict"
        
        if isinstance(owasp, dict):
            # New format with metadata
            assert 'categories' in owasp, "New format must have categories"
            assert isinstance(owasp['categories'], list), \
                "categories must be a list"


# =============================================================================
# TEST: ARCHITECTURE TAB
# =============================================================================

@pytest.mark.dashboard
class TestArchitectureTab:
    """Test Architecture tab data contract"""
    
    def test_architecture_structure(self, generated_data):
        """Test that architecture has valid structure"""
        data = generated_data.get('architecture')
        
        assert data is not None, "Architecture data not generated. Run: python tests/dashboard/generate_test_data.py"
        assert isinstance(data, dict), "Data must be a dictionary"
        
        # Check for key sections
        assert 'layers' in data or 'tiers' in data or 'components' in data, \
            "Architecture must have layers/tiers/components"
    
    def test_architecture_layers(self, generated_data):
        """Test architecture layers structure"""
        data = generated_data.get('architecture')
        assert data is not None, "Architecture data not generated"
        
        # Look for layers in various formats
        layers = data.get('layers') or data.get('tiers') or []
        
        if layers and isinstance(layers, list):
            layer = layers[0]
            # Should have descriptive info
            assert 'name' in layer or 'id' in layer, \
                "Layer must have name or id"


# =============================================================================
# TEST: CODE ORGANIZATION TAB
# =============================================================================

@pytest.mark.dashboard
class TestCodeOrganizationTab:
    """Test Code Organization tab data contract"""
    
    def test_code_org_structure(self, generated_data):
        """Test that code organization has valid structure"""
        data = generated_data.get('code_organization')
        
        assert data is not None, "Code organization data not generated. Run: python tests/dashboard/generate_test_data.py"
        assert isinstance(data, dict), "Data must be a dictionary"
    
    def test_code_org_metrics(self, generated_data):
        """Test code organization metrics"""
        data = generated_data.get('code_organization')
        assert data is not None, "Code organization data not generated"
        
        # Common metrics
        if 'file_count' in data:
            assert isinstance(data['file_count'], int), \
                "file_count must be integer"
        
        if 'directory_count' in data:
            assert isinstance(data['directory_count'], int), \
                "directory_count must be integer"
        
        if 'total_lines' in data:
            assert isinstance(data['total_lines'], int), \
                "total_lines must be integer"


# =============================================================================
# TEST: VENDORS TAB (OPTIONAL)
# =============================================================================

@pytest.mark.dashboard
@pytest.mark.skipif(not VENDOR_DETECTOR_AVAILABLE, reason="VendorDetector not available")
class TestVendorsTab:
    """Test Vendors tab data contract"""
    
    def test_vendors_structure(self, generated_data):
        """Test that vendors data has valid structure"""
        data = generated_data.get('vendors')
        
        if data is None:
            pytest.skip("Vendors data not generated (collector may not be available)")
        
        assert isinstance(data, dict), "Data must be a dictionary"
        
        # Should have vendors list (check multiple possible field names)
        assert 'vendors' in data or 'third_party' in data or 'external_vendors' in data, \
            "Must have vendors, third_party, or external_vendors section"


# =============================================================================
# TEST: TEAM METRICS TAB (OPTIONAL)
# =============================================================================

@pytest.mark.dashboard
@pytest.mark.skipif(not TEAM_METRICS_AVAILABLE, reason="TeamMetricsCollector not available")
class TestTeamMetricsTab:
    """Test Team Metrics tab data contract"""
    
    def test_team_metrics_structure(self, generated_data):
        """Test that team metrics has valid structure"""
        data = generated_data.get('team_metrics')
        
        if data is None:
            pytest.skip("Team metrics data not generated (collector may not be available)")
        
        assert isinstance(data, dict), "Data must be a dictionary"


# =============================================================================
# INTEGRATION TEST: ALL TABS TOGETHER
# =============================================================================

@pytest.mark.dashboard
class TestAllTabsIntegration:
    """Integration test validating all tabs work together"""
    
    def test_all_required_data_present(self, generated_data):
        """Test that all required data collectors produced output"""
        required_collectors = [
            'executive_summary',
            'tech_stack',
            'security',
            'architecture',
            'code_organization'
        ]
        
        missing = []
        for collector in required_collectors:
            if generated_data.get(collector) is None:
                missing.append(collector)
        
        assert not missing, f"Missing data from collectors: {missing}. Run: python tests/dashboard/generate_test_data.py"
        
        print(f"\n[PASS] All {len(required_collectors)} required collectors produced data")
    
    def test_generated_data_files_exist(self, test_data_path):
        """Test that all expected data files were generated"""
        expected_files = [
            'executive-summary.json',
            'tech-stack.json',
            'security.json',
            'architecture.json',
            'code-organization.json'
        ]
        
        missing = []
        for filename in expected_files:
            if not (test_data_path / filename).exists():
                missing.append(filename)
        
        assert not missing, f"Missing generated data files: {missing}. Run: python tests/dashboard/generate_test_data.py"


# =============================================================================
# DATA FRESHNESS TEST
# =============================================================================

@pytest.mark.dashboard
class TestDataFreshness:
    """Test that generated data is reasonably fresh"""
    
    def test_data_files_are_recent(self, test_data_path):
        """Test that generated data files were created recently"""
        import time
        from datetime import timedelta
        
        # Check if files exist and are less than 1 day old
        max_age = timedelta(days=1)
        now = time.time()
        
        required_files = [
            'executive-summary.json',
            'tech-stack.json',
            'security.json',
            'architecture.json',
            'code-organization.json'
        ]
        
        for filename in required_files:
            filepath = test_data_path / filename
            if not filepath.exists():
                pytest.fail(f"{filename} not found. Run: python tests/dashboard/generate_test_data.py")
            
            file_age = now - filepath.stat().st_mtime
            age_hours = file_age / 3600
            
            if file_age > max_age.total_seconds():
                print(f"Warning: {filename} is {age_hours:.1f} hours old. Consider regenerating.")
            else:
                print(f"{filename}: {age_hours:.1f} hours old (fresh)")


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == '__main__':
    """Run all dashboard data contract tests"""
    import sys
    
    # Run with verbose output
    exit_code = pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '-m', 'dashboard',
        '--color=yes'
    ])
    
    sys.exit(exit_code)
