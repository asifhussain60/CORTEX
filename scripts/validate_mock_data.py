"""
Validate Mock Dashboard Data

Validates that generated mock data matches expected schema structure.

Usage:
    python scripts/validate_mock_data.py

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_json(file_path: Path) -> Dict[str, Any]:
    """Load JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_health_data(data: Dict[str, Any]) -> List[str]:
    """Validate health-data.json structure."""
    errors = []
    
    required_fields = ['overall_health_score', 'status', 'last_scan', 'summary', 'metrics', 'trends']
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    if 'summary' in data:
        summary_fields = ['total_files', 'total_loc', 'test_coverage', 'critical_issues', 'warnings']
        for field in summary_fields:
            if field not in data['summary']:
                errors.append(f"Missing summary field: {field}")
    
    return errors


def validate_tech_stack(data: Dict[str, Any]) -> List[str]:
    """Validate tech-stack.json structure."""
    errors = []
    
    required_fields = ['frontend', 'backend', 'database', 'devops', 'summary']
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    # Validate tech entry structure
    for category in ['frontend', 'backend', 'database', 'devops']:
        if category in data and data[category]:
            tech = data[category][0]
            tech_fields = ['name', 'version', 'latest', 'status', 'category', 'cve_count']
            for field in tech_fields:
                if field not in tech:
                    errors.append(f"Missing tech field in {category}: {field}")
    
    if 'summary' in data:
        summary_fields = ['total_technologies', 'current_count', 'outdated_count', 'last_scan']
        for field in summary_fields:
            if field not in data['summary']:
                errors.append(f"Missing summary field: {field}")
    
    return errors


def validate_security(data: Dict[str, Any]) -> List[str]:
    """Validate security.json structure."""
    errors = []
    
    required_fields = ['overall_score', 'last_scan', 'vulnerabilities', 'owasp_top_10', 'compliance', 'summary']
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    if 'vulnerabilities' in data:
        vuln_fields = ['total', 'critical', 'high', 'medium', 'low']
        for field in vuln_fields:
            if field not in data['vulnerabilities']:
                errors.append(f"Missing vulnerabilities field: {field}")
    
    if 'owasp_top_10' in data:
        owasp_fields = ['pass_count', 'warn_count', 'fail_count', 'categories']
        for field in owasp_fields:
            if field not in data['owasp_top_10']:
                errors.append(f"Missing owasp_top_10 field: {field}")
    
    return errors


def validate_architecture(data: Dict[str, Any]) -> List[str]:
    """Validate architecture.json structure."""
    errors = []
    
    required_fields = ['style', 'score', 'last_scan', 'tiers', 'components', 'database_schema', 'summary']
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    if 'tiers' in data and data['tiers']:
        tier = data['tiers'][0]
        tier_fields = ['name', 'component_count', 'loc']
        for field in tier_fields:
            if field not in tier:
                errors.append(f"Missing tier field: {field}")
    
    if 'summary' in data:
        summary_fields = ['total_components', 'total_loc', 'average_complexity', 'tier_count']
        for field in summary_fields:
            if field not in data['summary']:
                errors.append(f"Missing summary field: {field}")
    
    return errors


def validate_code_organization(data: Dict[str, Any]) -> List[str]:
    """Validate code-organization.json structure."""
    errors = []
    
    required_fields = ['heatmap', 'hotspots', 'complexity_distribution', 'summary']
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    if 'hotspots' in data and data['hotspots']:
        hotspot = data['hotspots'][0]
        hotspot_fields = ['file', 'loc', 'complexity', 'change_frequency', 'risk_score', 'recommendation']
        for field in hotspot_fields:
            if field not in hotspot:
                errors.append(f"Missing hotspot field: {field}")
    
    if 'summary' in data:
        summary_fields = ['total_files', 'total_loc', 'avg_complexity', 'hotspots_count', 'last_scan']
        for field in summary_fields:
            if field not in data['summary']:
                errors.append(f"Missing summary field: {field}")
    
    return errors


def validate_team_metrics(data: Dict[str, Any]) -> List[str]:
    """Validate team-metrics.json structure."""
    errors = []
    
    required_fields = ['contributors', 'velocity', 'commit_trends', 'summary']
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    if 'contributors' in data and data['contributors']:
        contributor = data['contributors'][0]
        contrib_fields = ['name', 'email', 'commits', 'lines_added', 'lines_deleted']
        for field in contrib_fields:
            if field not in contributor:
                errors.append(f"Missing contributor field: {field}")
    
    if 'summary' in data:
        summary_fields = ['total_contributors', 'total_commits', 'avg_commits_per_week', 'last_scan']
        for field in summary_fields:
            if field not in data['summary']:
                errors.append(f"Missing summary field: {field}")
    
    return errors


def validate_vendors(data: Dict[str, Any]) -> List[str]:
    """Validate vendors.json structure."""
    errors = []
    
    required_fields = ['vendors', 'by_category', 'by_status', 'summary']
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    if 'vendors' in data and data['vendors']:
        vendor = data['vendors'][0]
        vendor_fields = ['name', 'category', 'status', 'cost_tier', 'detection_method', 'files_using']
        for field in vendor_fields:
            if field not in vendor:
                errors.append(f"Missing vendor field: {field}")
    
    if 'summary' in data:
        summary_fields = ['total_vendors', 'active_vendors', 'last_scan']
        for field in summary_fields:
            if field not in data['summary']:
                errors.append(f"Missing summary field: {field}")
    
    return errors


def main():
    """Main validation entry point."""
    project_root = Path(__file__).parent.parent
    mock_dir = project_root / "cortex-brain" / "dashboards" / "mock"
    
    if not mock_dir.exists():
        logger.error(f"Mock directory not found: {mock_dir}")
        sys.exit(1)
    
    logger.info("Starting mock data validation...")
    logger.info(f"Mock directory: {mock_dir}\n")
    
    validators = {
        "health-data.json": validate_health_data,
        "tech-stack.json": validate_tech_stack,
        "security.json": validate_security,
        "architecture.json": validate_architecture,
        "code-organization.json": validate_code_organization,
        "team-metrics.json": validate_team_metrics,
        "vendors.json": validate_vendors
    }
    
    all_valid = True
    results = []
    
    for file_name, validator in validators.items():
        file_path = mock_dir / file_name
        
        if not file_path.exists():
            logger.error(f"❌ {file_name} - File not found")
            all_valid = False
            results.append((file_name, ["File not found"]))
            continue
        
        try:
            data = load_json(file_path)
            errors = validator(data)
            
            if errors:
                logger.error(f"❌ {file_name} - {len(errors)} validation errors")
                for error in errors:
                    logger.error(f"   • {error}")
                all_valid = False
                results.append((file_name, errors))
            else:
                logger.info(f"✅ {file_name} - Valid")
                results.append((file_name, []))
        
        except json.JSONDecodeError as e:
            logger.error(f"❌ {file_name} - Invalid JSON: {e}")
            all_valid = False
            results.append((file_name, [f"Invalid JSON: {e}"]))
        except Exception as e:
            logger.error(f"❌ {file_name} - Validation error: {e}")
            all_valid = False
            results.append((file_name, [f"Validation error: {e}"]))
    
    # Print summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    valid_count = sum(1 for _, errors in results if not errors)
    total_count = len(results)
    
    print(f"Files validated: {total_count}")
    print(f"Valid: {valid_count}")
    print(f"Invalid: {total_count - valid_count}")
    
    if all_valid:
        print("\n✅ All mock data files are valid!")
        print("="*60)
        sys.exit(0)
    else:
        print("\n❌ Some mock data files have validation errors")
        print("="*60)
        sys.exit(1)


if __name__ == '__main__':
    main()
