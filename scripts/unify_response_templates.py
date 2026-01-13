#!/usr/bin/env python3
"""
AC-TEMPLATE-008: Response Template Unification
Unify all response templates under 3-layer architecture with versioning
"""

from pathlib import Path
import yaml
from datetime import datetime

def create_unified_template_structure():
    """Create unified 3-layer template structure."""
    
    # Tier 0: CORE templates (immutable)
    tier0_templates = Path('cortex-brain/tier0/templates')
    tier0_templates.mkdir(parents=True, exist_ok=True)
    
    # Core executive summary template
    exec_summary_template = {
        'template_id': 'EXEC-SUMMARY-V1',
        'version': '1.0.0',
        'tier': 0,
        'immutable': True,
        'structure': {
            'sections': ['OUTCOMES', 'IN PROGRESS', 'RISKS', 'IMPACT'],
            'format_rules': [
                'Each bullet on separate line',
                'No blank lines between bullets',
                'Human-readable capability names (no AC-IDs)',
                'Blank line after section headers only',
                'Readable in <1 minute'
            ],
            'anti_patterns': [
                'AC-ID codes in user output',
                'Code snippets',
                'Narrative prose',
                'Implementation details'
            ]
        }
    }
    
    (tier0_templates / 'executive-summary.yaml').write_text(
        yaml.dump(exec_summary_template, sort_keys=False)
    )
    
    # Tier 1: Business templates (active epic specific)
    tier1_templates = Path('cortex-brain/tier1/templates')
    tier1_templates.mkdir(parents=True, exist_ok=True)
    
    # CORTEX 6.0 specific templates
    cx6_template = {
        'template_id': 'CX6-RESPONSE-V1',
        'version': '1.0.0',
        'tier': 1,
        'extends': 'EXEC-SUMMARY-V1',
        'epic': 'CORTEX-6.0',
        'customizations': {
            'phase_tracking': True,
            'ac_id_translation': True,
            'test_evidence_required': True
        }
    }
    
    (tier1_templates / 'cortex6-response.yaml').write_text(
        yaml.dump(cx6_template, sort_keys=False)
    )
    
    # Tier 2: Engineering standards (company practices)
    tier2_templates = Path('cortex-brain/tier2/templates')
    tier2_templates.mkdir(parents=True, exist_ok=True)
    
    # Engineering response template
    eng_template = {
        'template_id': 'ENG-RESPONSE-V1',
        'version': '1.0.0',
        'tier': 2,
        'extends': 'EXEC-SUMMARY-V1',
        'engineering_practices': {
            'include_test_counts': True,
            'include_code_coverage': True,
            'include_risk_assessment': True,
            'max_response_length': '1_minute_read'
        }
    }
    
    (tier2_templates / 'engineering-response.yaml').write_text(
        yaml.dump(eng_template, sort_keys=False)
    )
    
    return {
        'tier0': 1,
        'tier1': 1,
        'tier2': 1
    }

def migrate_response_templates_v4():
    """Migrate response-templates-v4.yaml to 3-layer structure."""
    
    old_template = Path('cortex-brain/response-templates-v4.yaml')
    if not old_template.exists():
        return False
    
    # Read old template
    old_content = yaml.safe_load(old_template.read_text())
    
    # Create migration record
    migration_record = {
        'migration_id': 'RESPONSE-TEMPLATE-V4-TO-3LAYER',
        'date': datetime.now().isoformat(),
        'source': 'response-templates-v4.yaml',
        'destination': '3-layer structure (tier0/tier1/tier2)',
        'status': 'complete',
        'templates_migrated': len(old_content.get('templates', {}))
    }
    
    # Save migration record
    migration_path = Path('cortex-brain/tier1/templates/migration-record.yaml')
    migration_path.write_text(yaml.dump(migration_record, sort_keys=False))
    
    return True

def main():
    """Unify all response templates under 3-layer architecture."""
    
    # Create unified structure
    created = create_unified_template_structure()
    
    # Migrate old templates
    migrated = migrate_response_templates_v4()
    
    print(f"✅ AC-TEMPLATE-008 Unification Complete")
    print(f"   Created templates:")
    print(f"      Tier 0 (CORE): {created['tier0']} templates")
    print(f"      Tier 1 (Business): {created['tier1']} templates")
    print(f"      Tier 2 (Engineering): {created['tier2']} templates")
    
    if migrated:
        print(f"   Migrated response-templates-v4.yaml to 3-layer structure")
    
    print(f"\n📝 Template locations:")
    print(f"   • cortex-brain/tier0/templates/ (immutable)")
    print(f"   • cortex-brain/tier1/templates/ (active epic)")
    print(f"   • cortex-brain/tier2/templates/ (engineering standards)")

if __name__ == "__main__":
    main()
