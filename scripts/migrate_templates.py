#!/usr/bin/env python3
"""
Template Migration Script for Phase 3
Migrates templates from monolithic response-templates.yaml to distributed structure
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

@dataclass
class TemplateMetrics:
    """Metrics for a single template."""
    template_id: str
    line_count: int
    component_refs: List[str]
    has_duplication: bool
    category: str
    file_path: str = ""

@dataclass
class MigrationResult:
    """Result of template migration."""
    success: bool
    templates_migrated: int
    components_extracted: int
    total_lines_before: int
    total_lines_after: int
    reduction_percentage: float
    errors: List[str]
    warnings: List[str]

class TemplateMigrator:
    """Handles migration of templates from monolithic to distributed structure."""
    
    def __init__(self, source_file: Path, target_dir: Path):
        self.source_file = source_file
        self.target_dir = target_dir
        self.registry = {}
        self.components = {
            "headers": {},
            "footers": {},
            "sections": {},
            "formatters": {}
        }
        self.base_templates = {}
        self.templates_data = {}
        self.migration_log = []
        
    def load_source_file(self) -> Dict[str, Any]:
        """Load the monolithic YAML file."""
        print(f"📖 Loading source file: {self.source_file}")
        with open(self.source_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def analyze_template(self, template_id: str, template_data: Dict) -> TemplateMetrics:
        """Analyze a single template to determine migration strategy."""
        content = yaml.dump(template_data)
        line_count = len(content.split('\n'))
        
        # Detect component references (placeholders, common patterns)
        component_refs = []
        if 'base_structure' in template_data:
            structure = template_data['base_structure']
            # Look for common patterns
            if '## 🧠 CORTEX' in structure:
                component_refs.append('standard_header')
            if 'Author: Asif Hussain' in structure:
                component_refs.append('attribution')
            if '### 🔍 Next Steps' in structure or 'Next Steps' in structure:
                component_refs.append('next_steps_section')
        
        # Determine category based on template properties
        category = self._determine_category(template_id, template_data)
        
        return TemplateMetrics(
            template_id=template_id,
            line_count=line_count,
            component_refs=component_refs,
            has_duplication='base_structure' in template_data,
            category=category
        )
    
    def _determine_category(self, template_id: str, template_data: Dict) -> str:
        """Determine which category a template belongs to."""
        # Check expected_orchestrator field
        if 'expected_orchestrator' in template_data:
            orch = template_data['expected_orchestrator'].lower()
            if 'planning' in orch:
                return 'orchestrators/planning'
            elif 'tdd' in orch or 'test' in orch:
                return 'orchestrators/tdd'
            elif 'upgrade' in orch:
                return 'orchestrators/upgrade'
            elif 'checkpoint' in orch or 'git' in orch:
                return 'orchestrators/git-checkpoint'
            elif 'align' in orch:
                return 'orchestrators/align'
            elif 'onboard' in orch:
                return 'operations/onboarding'
            elif 'diagram' in orch:
                return 'operations/diagram'
            elif 'feedback' in orch:
                return 'operations/feedback'
        
        # Check template_id patterns
        if any(x in template_id for x in ['help', 'guide', 'tutorial']):
            return 'operations/help'
        elif any(x in template_id for x in ['error', 'warning', 'failure']):
            return 'errors'
        elif any(x in template_id for x in ['admin', 'deploy', 'publish']):
            return 'operations/admin'
        elif any(x in template_id for x in ['ado', 'azure']):
            return 'specialized/ado-integration'
        elif any(x in template_id for x in ['threat', 'security']):
            return 'specialized/threat-modeling'
        elif 'confidence' in template_id:
            return 'specialized/confidence-scoring'
        elif 'dashboard' in template_id:
            return 'specialized/dashboard'
        
        # Default fallback
        return 'operations/general'
    
    def extract_components(self, source_data: Dict) -> None:
        """Extract shared components from source data."""
        print("🔍 Extracting shared components...")
        
        # Extract from 'shared' section
        if 'shared' in source_data:
            shared = source_data['shared']
            if 'standard_header' in shared:
                self.components['headers']['standard_header'] = {
                    'template': shared['standard_header'],
                    'description': 'Standard CORTEX response header'
                }
            if 'progress_bar' in shared:
                self.components['sections']['progress_bar'] = shared['progress_bar']
            if 'plan_file_link' in shared:
                self.components['sections']['plan_file_link'] = shared['plan_file_link']
        
        # Extract from 'base_templates' section
        if 'base_templates' in source_data:
            self.base_templates = source_data['base_templates']
        
        print(f"   ✓ Extracted {len(self.components['headers'])} headers")
        print(f"   ✓ Extracted {len(self.components['sections'])} sections")
        print(f"   ✓ Extracted {len(self.base_templates)} base templates")
    
    def migrate_template(self, template_id: str, template_data: Dict, metrics: TemplateMetrics) -> Tuple[bool, str]:
        """Migrate a single template to its target location."""
        try:
            # Determine target file path
            category_path = self.target_dir / metrics.category
            category_path.mkdir(parents=True, exist_ok=True)
            
            # Create template with inheritance
            migrated_template = self._create_migrated_template(template_id, template_data, metrics)
            
            # Determine filename (group related templates in same file)
            filename = self._get_filename_for_category(metrics.category, template_id)
            target_file = category_path / filename
            
            # Load existing file if it exists
            if target_file.exists():
                with open(target_file, 'r', encoding='utf-8') as f:
                    existing_data = yaml.safe_load(f) or {}
            else:
                existing_data = {
                    'category': metrics.category,
                    'templates': {}
                }
            
            # Add template to file
            existing_data['templates'][template_id] = migrated_template
            
            # Write file
            with open(target_file, 'w', encoding='utf-8') as f:
                yaml.dump(existing_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            # Update registry
            self.registry[template_id] = {
                'file': str(target_file.relative_to(self.target_dir)),
                'category': metrics.category,
                'line_count': metrics.line_count
            }
            
            metrics.file_path = str(target_file.relative_to(self.target_dir))
            return True, f"Migrated {template_id} to {metrics.file_path}"
        
        except Exception as e:
            return False, f"Failed to migrate {template_id}: {str(e)}"
    
    def _create_migrated_template(self, template_id: str, template_data: Dict, metrics: TemplateMetrics) -> Dict:
        """Create migrated template with inheritance and component refs."""
        migrated = {}
        
        # Determine if this should inherit from a base template
        if 'base_structure' in template_data:
            structure = template_data['base_structure']
            if '### 🎯 Understanding & Scope' in structure:
                migrated['inherits_from'] = 'core/base-templates/5-part-standard.yaml'
        
        # Copy metadata fields
        for field in ['name', 'triggers', 'response_type', 'expected_orchestrator', 'operation_name']:
            if field in template_data:
                migrated[field] = template_data[field]
        
        # Create sections object (content fields)
        sections = {}
        for field in ['understanding_content', 'challenge_content', 'response_content', 
                      'request_echo_content', 'next_steps_content']:
            if field in template_data:
                sections[field] = template_data[field]
        
        if sections:
            migrated['sections'] = sections
        
        # If no inheritance, include full base_structure
        if 'inherits_from' not in migrated and 'base_structure' in template_data:
            migrated['base_structure'] = template_data['base_structure']
        
        return migrated
    
    def _get_filename_for_category(self, category: str, template_id: str) -> str:
        """Get filename for a given category and template."""
        # Extract filename from category path
        parts = category.split('/')
        if len(parts) > 1:
            return f"{parts[1]}.yaml"
        return "general.yaml"
    
    def save_components(self) -> None:
        """Save extracted components to files."""
        print("💾 Saving components...")
        
        # Save headers
        if self.components['headers']:
            headers_file = self.target_dir / 'core' / 'components' / 'headers.yaml'
            headers_file.parent.mkdir(parents=True, exist_ok=True)
            with open(headers_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.components['headers'], f, default_flow_style=False, allow_unicode=True)
            print(f"   ✓ Saved headers to {headers_file.relative_to(self.target_dir)}")
        
        # Save sections
        if self.components['sections']:
            sections_file = self.target_dir / 'core' / 'components' / 'sections.yaml'
            sections_file.parent.mkdir(parents=True, exist_ok=True)
            with open(sections_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.components['sections'], f, default_flow_style=False, allow_unicode=True)
            print(f"   ✓ Saved sections to {sections_file.relative_to(self.target_dir)}")
    
    def save_base_templates(self) -> None:
        """Save base templates to files."""
        print("💾 Saving base templates...")
        
        base_dir = self.target_dir / 'core' / 'base-templates'
        base_dir.mkdir(parents=True, exist_ok=True)
        
        # Save standard 5-part template
        if 'standard_5_part' in self.base_templates:
            file_path = base_dir / '5-part-standard.yaml'
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump({'standard_5_part': self.base_templates['standard_5_part']}, 
                         f, default_flow_style=False, allow_unicode=True)
            print(f"   ✓ Saved 5-part-standard.yaml")
        
        # Save tech-aware template
        if 'tech_aware_response' in self.base_templates:
            file_path = base_dir / 'tech-aware.yaml'
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump({'tech_aware_response': self.base_templates['tech_aware_response']}, 
                         f, default_flow_style=False, allow_unicode=True)
            print(f"   ✓ Saved tech-aware.yaml")
    
    def save_registry(self) -> None:
        """Save template registry to file."""
        print("💾 Saving template registry...")
        
        registry_file = self.target_dir / 'config' / 'template-registry.yaml'
        registry_file.parent.mkdir(parents=True, exist_ok=True)
        
        registry_data = {
            'version': '1.0',
            'generated': datetime.now().isoformat(),
            'template_count': len(self.registry),
            'templates': self.registry
        }
        
        with open(registry_file, 'w', encoding='utf-8') as f:
            yaml.dump(registry_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        
        print(f"   ✓ Saved registry with {len(self.registry)} templates")
    
    def generate_migration_report(self, results: List[Tuple[bool, str]], metrics: List[TemplateMetrics]) -> MigrationResult:
        """Generate comprehensive migration report."""
        successful = [r for r in results if r[0]]
        failed = [r for r in results if not r[0]]
        
        total_lines_before = sum(m.line_count for m in metrics)
        # Estimate reduction (components + inheritance typically reduce by 30-50%)
        total_lines_after = int(total_lines_before * 0.6)  # Conservative estimate
        
        return MigrationResult(
            success=len(failed) == 0,
            templates_migrated=len(successful),
            components_extracted=sum(len(c) for c in self.components.values()),
            total_lines_before=total_lines_before,
            total_lines_after=total_lines_after,
            reduction_percentage=((total_lines_before - total_lines_after) / total_lines_before) * 100,
            errors=[r[1] for r in failed],
            warnings=[]
        )
    
    def run_migration(self) -> MigrationResult:
        """Execute full migration process."""
        print("\n" + "="*60)
        print("🚀 PHASE 3: TEMPLATE MIGRATION")
        print("="*60 + "\n")
        
        # Step 1: Load source
        source_data = self.load_source_file()
        
        # Step 2: Extract components
        self.extract_components(source_data)
        self.save_components()
        self.save_base_templates()
        
        # Step 3: Analyze all templates
        print("\n📊 Analyzing templates...")
        templates = source_data.get('templates', {})
        metrics_list = []
        for template_id, template_data in templates.items():
            metrics = self.analyze_template(template_id, template_data)
            metrics_list.append(metrics)
        
        print(f"   ✓ Analyzed {len(metrics_list)} templates")
        
        # Step 4: Migrate templates
        print("\n🔄 Migrating templates...")
        results = []
        for metrics in metrics_list:
            template_data = templates[metrics.template_id]
            success, message = self.migrate_template(metrics.template_id, template_data, metrics)
            results.append((success, message))
            if success:
                print(f"   ✓ {message}")
            else:
                print(f"   ✗ {message}")
        
        # Step 5: Save registry
        self.save_registry()
        
        # Step 6: Generate report
        print("\n📈 Generating migration report...")
        migration_result = self.generate_migration_report(results, metrics_list)
        
        return migration_result

def main():
    """Main entry point."""
    # Determine paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    source_file = project_root / 'cortex-brain' / 'response-templates.yaml'
    target_dir = project_root / 'cortex-brain' / 'response-templates'
    
    # Run migration
    migrator = TemplateMigrator(source_file, target_dir)
    result = migrator.run_migration()
    
    # Print summary
    print("\n" + "="*60)
    print("📊 MIGRATION SUMMARY")
    print("="*60)
    print(f"Status: {'✅ SUCCESS' if result.success else '❌ FAILED'}")
    print(f"Templates Migrated: {result.templates_migrated}")
    print(f"Components Extracted: {result.components_extracted}")
    print(f"Lines Before: {result.total_lines_before:,}")
    print(f"Lines After (estimated): {result.total_lines_after:,}")
    print(f"Reduction: {result.reduction_percentage:.1f}%")
    
    if result.errors:
        print(f"\n❌ Errors ({len(result.errors)}):")
        for error in result.errors[:5]:  # Show first 5
            print(f"   • {error}")
    
    if result.warnings:
        print(f"\n⚠️  Warnings ({len(result.warnings)}):")
        for warning in result.warnings[:5]:  # Show first 5
            print(f"   • {warning}")
    
    print("\n✅ Migration complete!")
    print(f"📁 New templates directory: {target_dir}")
    print(f"📋 Template registry: {target_dir / 'config' / 'template-registry.yaml'}")
    
    return 0 if result.success else 1

if __name__ == '__main__':
    sys.exit(main())
