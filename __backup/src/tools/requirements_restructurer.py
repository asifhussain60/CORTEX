"""
Requirements Restructurer Tool

Batch converts requirements YAML files from flat list structure to nested object structure
that complies with requirements-schema.json.

Usage:
    restructurer = RequirementsRestructurer()
    results = restructurer.batch_restructure(base_path, feature_map)
    report = restructurer.generate_summary_report(results)

Created: 2026-01-08 | CORTEX 6.0 P1-T2
"""

import yaml
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
import json
import shutil
from datetime import datetime


@dataclass
class RestructureResult:
    """Result of restructuring a single requirements file."""
    file: str
    success: bool
    requirements_count: int
    error: str = ""
    dry_run: bool = False
    backup_created: bool = False


class RequirementsRestructurer:
    """
    Restructures requirements YAML files to comply with schema.
    
    Converts flat list structures:
        - requirement_id: REQ-001
          description: "..."
    
    To nested object structures:
        feature_id: feat01
        feature_name: "Foundation Layer"
        requirements:
          - requirement_id: REQ-001
            description: "..."
    """
    
    def __init__(self):
        """Initialize restructurer with schema validation support."""
        self.schema_path = Path("cortex-brain/schemas/requirements-schema.json")
    
    def extract_feature_info(self, directory_name: str) -> Tuple[str, str]:
        """
        Extract feature ID and name from directory name.
        
        Args:
            directory_name: e.g., "feat01-foundation" or "feat02-todo-orchestrator"
        
        Returns:
            Tuple of (feature_id, feature_name)
        
        Examples:
            "feat01-foundation" -> ("feat01", "Foundation")
            "feat02-todo-orchestrator" -> ("feat02", "Todo Orchestrator")
        """
        # Extract feature ID (feat01, feat02, etc.)
        match = re.match(r'(feat\d+)', directory_name)
        if not match:
            raise ValueError(f"Cannot extract feature ID from: {directory_name}")
        
        feature_id = match.group(1)
        
        # Extract feature name (everything after feature ID and hyphen)
        name_part = directory_name[len(feature_id):].lstrip('-')
        
        # Convert hyphen-separated to Title Case
        feature_name = ' '.join(word.capitalize() for word in name_part.split('-'))
        
        return feature_id, feature_name
    
    def restructure_yaml_content(
        self,
        yaml_content: str,
        feature_id: str,
        feature_name: str
    ) -> str:
        """
        Restructure YAML content to match schema.
        
        Args:
            yaml_content: Original YAML content (may be flat list or nested)
            feature_id: Feature identifier (e.g., "feat01")
            feature_name: Human-readable feature name
        
        Returns:
            Restructured YAML content as string
        
        Raises:
            yaml.YAMLError: If YAML syntax is invalid
        """
        # Parse YAML
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Invalid YAML syntax: {e}")
        
        # Check if already in correct format
        if isinstance(data, dict) and 'requirements' in data:
            # Already nested - verify it has required fields
            if 'feature_id' not in data:
                data['feature_id'] = feature_id
            if 'feature_name' not in data:
                data['feature_name'] = feature_name
            
            return yaml.dump(data, default_flow_style=False, sort_keys=False)
        
        # Convert flat list to nested structure
        if isinstance(data, list):
            restructured = {
                'feature_id': feature_id,
                'feature_name': feature_name,
                'requirements': data
            }
            
            return yaml.dump(restructured, default_flow_style=False, sort_keys=False)
        
        # Unexpected format
        raise ValueError(f"Unexpected YAML structure: expected list or dict with 'requirements'")
    
    def validate_structure(self, yaml_content: str) -> bool:
        """
        Validate that YAML content has correct structure.
        
        Args:
            yaml_content: YAML content to validate
        
        Returns:
            True if structure is valid, False otherwise
        """
        try:
            data = yaml.safe_load(yaml_content)
            
            # Must be dict
            if not isinstance(data, dict):
                return False
            
            # Must have required top-level keys
            required_keys = ['feature_id', 'feature_name', 'requirements']
            if not all(key in data for key in required_keys):
                return False
            
            # requirements must be a list
            if not isinstance(data['requirements'], list):
                return False
            
            # Each requirement must be a dict with requirement_id
            for req in data['requirements']:
                if not isinstance(req, dict):
                    return False
                if 'requirement_id' not in req:
                    return False
            
            return True
            
        except (yaml.YAMLError, KeyError, TypeError):
            return False
    
    def batch_restructure(
        self,
        base_path: Path,
        feature_map: Dict[str, Dict[str, str]],
        dry_run: bool = False,
        create_backup: bool = True
    ) -> List[RestructureResult]:
        """
        Batch restructure multiple requirements files.
        
        Args:
            base_path: Base directory containing feature subdirectories
            feature_map: Dict mapping directory names to feature info
                Example: {
                    'feat01-foundation': {
                        'feature_id': 'feat01',
                        'feature_name': 'Foundation Layer'
                    }
                }
            dry_run: If True, don't modify files (preview only)
            create_backup: If True, create .bak files before modification
        
        Returns:
            List of RestructureResult objects
        """
        results = []
        
        for dir_name, feature_info in feature_map.items():
            feature_dir = base_path / dir_name
            req_file = feature_dir / "requirements.yaml"
            
            if not req_file.exists():
                results.append(RestructureResult(
                    file=str(req_file),
                    success=False,
                    requirements_count=0,
                    error="File not found"
                ))
                continue
            
            try:
                # Read original content
                original_content = req_file.read_text()
                
                # Restructure
                restructured_content = self.restructure_yaml_content(
                    original_content,
                    feature_info['feature_id'],
                    feature_info['feature_name']
                )
                
                # Count requirements
                parsed = yaml.safe_load(restructured_content)
                req_count = len(parsed.get('requirements', []))
                
                # Dry run - don't modify
                if dry_run:
                    results.append(RestructureResult(
                        file=str(req_file),
                        success=True,
                        requirements_count=req_count,
                        dry_run=True
                    ))
                    continue
                
                # Create backup if requested
                backup_created = False
                if create_backup:
                    backup_file = req_file.with_suffix('.yaml.bak')
                    shutil.copy2(req_file, backup_file)
                    backup_created = True
                
                # Write restructured content
                req_file.write_text(restructured_content)
                
                results.append(RestructureResult(
                    file=str(req_file),
                    success=True,
                    requirements_count=req_count,
                    backup_created=backup_created
                ))
                
            except Exception as e:
                results.append(RestructureResult(
                    file=str(req_file),
                    success=False,
                    requirements_count=0,
                    error=str(e)
                ))
        
        return results
    
    def generate_summary_report(self, results: List[RestructureResult]) -> Dict[str, Any]:
        """
        Generate summary report from restructuring results.
        
        Args:
            results: List of RestructureResult objects
        
        Returns:
            Dict with summary statistics
        """
        total = len(results)
        successful = sum(1 for r in results if r.success)
        failed = total - successful
        total_requirements = sum(r.requirements_count for r in results if r.success)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_files': total,
            'successful': successful,
            'failed': failed,
            'total_requirements': total_requirements,
            'results': [asdict(r) for r in results]
        }


def main():
    """CLI entry point for batch restructuring."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Batch restructure requirements YAML files'
    )
    parser.add_argument(
        'base_path',
        type=Path,
        help='Base directory containing feature subdirectories'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip backup creation'
    )
    parser.add_argument(
        '--report',
        type=Path,
        help='Path to save JSON report'
    )
    
    args = parser.parse_args()
    
    # Auto-detect feature directories
    feature_map = {}
    restructurer = RequirementsRestructurer()
    
    for item in args.base_path.iterdir():
        if item.is_dir() and item.name.startswith('feat'):
            try:
                feature_id, feature_name = restructurer.extract_feature_info(item.name)
                feature_map[item.name] = {
                    'feature_id': feature_id,
                    'feature_name': feature_name
                }
            except ValueError:
                continue
    
    # Execute restructuring
    results = restructurer.batch_restructure(
        args.base_path,
        feature_map,
        dry_run=args.dry_run,
        create_backup=not args.no_backup
    )
    
    # Generate report
    report = restructurer.generate_summary_report(results)
    
    # Print summary
    print("\n" + "="*70)
    print("REQUIREMENTS RESTRUCTURING SUMMARY")
    print("="*70)
    print(f"Total Files: {report['total_files']}")
    print(f"Successful: {report['successful']}")
    print(f"Failed: {report['failed']}")
    print(f"Total Requirements: {report['total_requirements']}")
    print("="*70 + "\n")
    
    # Print individual results
    for result in results:
        status = "✅" if result.success else "❌"
        print(f"{status} {Path(result.file).name}: {result.requirements_count} requirements")
        if result.error:
            print(f"   Error: {result.error}")
    
    # Save report if requested
    if args.report:
        args.report.write_text(json.dumps(report, indent=2))
        print(f"\n📄 Report saved to: {args.report}")


if __name__ == '__main__':
    main()
