#!/usr/bin/env python3
"""
P1 Requirements Extractor - Autonomous Execution

Extracts individual feature requirements from feat03-to-feat08/features-summary.yaml
and creates properly structured directories and requirements.yaml files.

Created: 2026-01-08 | Phase P1-T5 through P1-T9
"""

import yaml
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class FeatureRequirementsExtractor:
    """Extract requirements from grouped features-summary.yaml"""
    
    def __init__(self, source_file: Path, output_base: Path):
        self.source_file = source_file
        self.output_base = output_base
        self.features_extracted = []
    
    def extract_all_features(self) -> List[Dict[str, Any]]:
        """
        Parse features-summary.yaml and extract individual features.
        
        Returns:
            List of feature dictionaries with id, name, and requirements
        """
        print(f"📖 Reading {self.source_file}")
        
        with open(self.source_file, 'r') as f:
            content = f.read()
        
        # Split by feature headers
        feature_sections = re.split(
            r'# ={50,}\n# FEATURE: (FEAT\d+-[A-Z-]+)',
            content
        )
        
        features = []
        
        # Process sections (skip first empty section)
        for i in range(1, len(feature_sections), 2):
            feature_id_raw = feature_sections[i]
            feature_content = feature_sections[i + 1] if i + 1 < len(feature_sections) else ""
            
            # Extract feature ID (feat03, feat04, etc.)
            match = re.match(r'FEAT(\d+)', feature_id_raw)
            if not match:
                continue
            
            feature_num = match.group(1)
            feature_id = f"feat{feature_num}"
            
            # Parse YAML content
            try:
                # Find the YAML part (after the comment block)
                yaml_start = feature_content.find('feature:')
                if yaml_start == -1:
                    continue
                
                yaml_content = feature_content[yaml_start:]
                
                # Parse until next feature or EOF
                feature_data = yaml.safe_load(yaml_content)
                
                if feature_data and 'feature' in feature_data:
                    feature_info = feature_data['feature']
                    
                    # Get phases from root level OR feature level
                    phases = feature_data.get('phases', feature_info.get('phases', []))
                    
                    features.append({
                        'id': feature_id,
                        'name': feature_info.get('name', ''),
                        'description': feature_info.get('description', ''),
                        'phases': phases,
                        'deliverables': feature_info.get('deliverables', {}),
                        'raw_data': feature_data
                    })
                    
            except yaml.YAMLError as e:
                print(f"⚠️  Warning: Could not parse {feature_id}: {e}")
                continue
        
        print(f"✅ Extracted {len(features)} features")
        return features
    
    def convert_phases_to_requirements(self, feature: Dict) -> List[Dict]:
        """
        Convert feature phases/tasks to requirements format.
        
        Args:
            feature: Feature dictionary with phases
        
        Returns:
            List of requirements in schema-compliant format
        """
        requirements = []
        req_counter = 1
        
        phases = feature.get('phases', [])
        
        for phase in phases:
            phase_id = phase.get('id', 0)
            phase_name = phase.get('name', '')
            
            # Create phase-level requirement
            phase_req = {
                'requirement_id': f"REQ-{req_counter:03d}",
                'description': f"{phase_name}",
                'acceptance_criteria': [],
                'priority': 'P0_CRITICAL',
                'status': phase.get('status', 'NOT_STARTED'),
                'category': 'TECHNICAL',
                'feature_id': feature['id'],
                'dependencies': [],
                'estimated_hours': phase.get('estimated_hours', 0)
            }
            
            # Extract tasks as acceptance criteria
            tasks = phase.get('tasks', [])
            for task in tasks:
                task_name = task.get('name', '')
                if task_name:
                    phase_req['acceptance_criteria'].append(task_name)
            
            requirements.append(phase_req)
            req_counter += 1
        
        return requirements
    
    def create_feature_directory(self, feature: Dict) -> Path:
        """
        Create feature directory structure.
        
        Args:
            feature: Feature dictionary
        
        Returns:
            Path to created directory
        """
        # Determine directory name
        feature_id = feature['id']
        feature_name_slug = feature['name'].lower().replace(' ', '-').replace('/', '-')
        dir_name = f"{feature_id}-{feature_name_slug}"
        
        feature_dir = self.output_base / dir_name
        feature_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 Created {feature_dir}")
        return feature_dir
    
    def generate_requirements_yaml(self, feature: Dict, output_dir: Path):
        """
        Generate requirements.yaml file for a feature.
        
        Args:
            feature: Feature dictionary
            output_dir: Output directory path
        """
        requirements = self.convert_phases_to_requirements(feature)
        
        # Build requirements YAML structure
        requirements_data = {
            'feature_id': feature['id'],
            'feature_name': feature['name'],
            'description': feature.get('description', ''),
            'created_date': datetime.now().isoformat(),
            'requirements': requirements
        }
        
        # Write to file
        output_file = output_dir / 'requirements.yaml'
        with open(output_file, 'w') as f:
            yaml.dump(requirements_data, f, default_flow_style=False, sort_keys=False)
        
        print(f"  ✅ Generated requirements.yaml ({len(requirements)} requirements)")
        
        self.features_extracted.append({
            'feature_id': feature['id'],
            'feature_name': feature['name'],
            'requirements_count': len(requirements),
            'output_file': str(output_file)
        })
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute full extraction process.
        
        Returns:
            Summary report
        """
        print("\n🛡️🧠 CORTEX Feature Requirements Extraction")
        print("=" * 70)
        print()
        
        # Extract features
        features = self.extract_all_features()
        
        print()
        print(f"📝 Processing {len(features)} features...")
        print()
        
        # Process each feature
        for feature in features:
            print(f"🔄 Processing {feature['id']}: {feature['name']}")
            
            # Create directory
            feature_dir = self.create_feature_directory(feature)
            
            # Generate requirements.yaml
            self.generate_requirements_yaml(feature, feature_dir)
            
            print()
        
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'source_file': str(self.source_file),
            'total_features': len(features),
            'total_requirements': sum(f['requirements_count'] for f in self.features_extracted),
            'features': self.features_extracted
        }
        
        print("=" * 70)
        print(f"✅ EXTRACTION COMPLETE")
        print(f"   Features: {report['total_features']}")
        print(f"   Requirements: {report['total_requirements']}")
        print("=" * 70)
        print()
        
        return report


def main():
    """CLI entry point"""
    source_file = Path('.asif/AI-Learning/cortex6/source-of-truth/features/feat03-to-feat08/features-summary.yaml')
    output_base = Path('.asif/AI-Learning/cortex6/source-of-truth/features')
    
    extractor = FeatureRequirementsExtractor(source_file, output_base)
    report = extractor.execute()
    
    # Save report
    report_file = Path('.asif/AI-Learning/cortex6-fixes/reports/feature-extraction-report.json')
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    import json
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Report saved to: {report_file}")


if __name__ == '__main__':
    main()
