"""
Generate Mock Dashboard Data

Creates realistic mock data files for dashboard development and testing.

Usage:
    python scripts/generate_mock_dashboard_data.py --scenario healthy
    python scripts/generate_mock_dashboard_data.py --scenario warning
    python scripts/generate_mock_dashboard_data.py --scenario critical

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.dashboard.data.mock_data_generator import MockDataGenerator, HealthScenario


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def ensure_directory(path: Path) -> None:
    """Create directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Ensured directory exists: {path}")


def save_json(data: dict, file_path: Path) -> None:
    """Save data to JSON file with pretty formatting."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved: {file_path} ({file_path.stat().st_size} bytes)")


def generate_mock_dashboard_data(scenario: str = "healthy") -> None:
    """
    Generate all mock data files for specified scenario.
    
    Args:
        scenario: "healthy", "warning", or "critical"
    """
    logger.info(f"Starting mock data generation with scenario: {scenario}")
    
    # Create output directory
    output_dir = project_root / "cortex-brain" / "dashboards" / "mock"
    ensure_directory(output_dir)
    
    # Generate all mock data
    try:
        scenario_enum = HealthScenario(scenario.lower())
        generator = MockDataGenerator(scenario=scenario_enum)
        all_data = generator.generate_all()
        
        logger.info(f"Generated {len(all_data)} data files")
        
        # Save each data file
        file_mapping = {
            "health_data": "health-data.json",
            "tech_stack": "tech-stack.json",
            "security": "security.json",
            "architecture": "architecture.json",
            "code_organization": "code-organization.json",
            "team_metrics": "team-metrics.json",
            "vendors": "vendors.json"
        }
        
        for data_key, file_name in file_mapping.items():
            if data_key in all_data:
                file_path = output_dir / file_name
                save_json(all_data[data_key], file_path)
            else:
                logger.warning(f"Missing data key: {data_key}")
        
        # Create metadata file
        metadata = {
            "generated_at": all_data["health_data"]["last_scan"],
            "scenario": scenario,
            "generator_version": "1.0.0",
            "files": list(file_mapping.values())
        }
        save_json(metadata, output_dir / "metadata.json")
        
        logger.info("✅ Mock data generation complete!")
        logger.info(f"📁 Output directory: {output_dir}")
        logger.info(f"📊 Files created: {len(file_mapping) + 1}")
        
        # Print summary
        print("\n" + "="*60)
        print("✅ MOCK DATA GENERATION COMPLETE")
        print("="*60)
        print(f"Scenario: {scenario.upper()}")
        print(f"Output: {output_dir}")
        print(f"\nFiles created:")
        for file_name in file_mapping.values():
            file_path = output_dir / file_name
            if file_path.exists():
                print(f"  ✓ {file_name} ({file_path.stat().st_size:,} bytes)")
        print(f"  ✓ metadata.json")
        print("="*60)
        
    except ValueError as e:
        logger.error(f"Invalid scenario: {scenario}. Must be 'healthy', 'warning', or 'critical'")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error generating mock data: {e}", exc_info=True)
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate mock dashboard data for testing and development",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate healthy scenario (default)
  python scripts/generate_mock_dashboard_data.py
  
  # Generate warning scenario
  python scripts/generate_mock_dashboard_data.py --scenario warning
  
  # Generate critical scenario
  python scripts/generate_mock_dashboard_data.py --scenario critical

Scenarios:
  healthy  - 90/100 health score, minimal issues, optimal state
  warning  - 65/100 health score, moderate issues, needs attention
  critical - 35/100 health score, severe issues, urgent action required
        """
    )
    
    parser.add_argument(
        '--scenario',
        type=str,
        default='healthy',
        choices=['healthy', 'warning', 'critical'],
        help='Health scenario variant (default: healthy)'
    )
    
    args = parser.parse_args()
    
    generate_mock_dashboard_data(scenario=args.scenario)


if __name__ == '__main__':
    main()
