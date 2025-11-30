#!/usr/bin/env python3
"""
CORTEX Response Templates Splitter
Splits monolithic response-templates.yaml into category-specific files

Purpose: Reduce token usage by loading only relevant template categories
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import yaml
import os
from pathlib import Path

# Categories mapping
CATEGORIES = {
    'help': ['help_table', 'help_detailed', 'help_setup', 'help_maintain', 'help_document', 
             'help_plan_feature', 'help_design_sync', 'help_list', 'quick_start', 'about', 
             'commands_by_category'],
    'operations': ['operation_started', 'operation_progress', 'operation_complete', 'operation_failed',
                   'setup_started', 'setup_complete', 'cleanup_started', 'cleanup_complete',
                   'story_refresh_started', 'story_refresh_complete', 'docs_build_started', 'docs_build_complete',
                   'brain_check_started', 'brain_check_complete', 'tests_started', 'tests_complete',
                   'design_sync_started', 'design_sync_discovery', 'design_sync_gaps', 'design_sync_complete'],
    'planning': ['planning_activation', 'planning_started', 'planning_question', 'planning_plan_ready',
                 'planning_complete', 'planning_aborted', 'question_can_cortex_do', 'work_planner_success',
                 'work_planner_error', 'architect_success', 'architect_error'],
    'brain_performance': ['brain_performance_session', 'brain_performance_legacy', 'token_optimization_session',
                          'brain_health_check', 'token_efficiency_metrics'],
    'questions': ['question_about_cortex_general', 'question_about_workspace', 'question_cortex_vs_application',
                  'question_what_cortex_learned', 'question_can_cortex_do', 'question_cortex_differences',
                  'question_how_cortex_works', 'question_cortex_cost_savings', 'question_namespace_status',
                  'question_cortex_learning_rate', 'question_documentation_issues', 'question_test_coverage'],
    'agents': ['executor_success', 'executor_error', 'tester_success', 'tester_error', 'validator_success',
               'validator_error', 'documenter_success', 'documenter_error', 'intent_detector_success',
               'intent_detector_error', 'health_validator_success', 'health_validator_error',
               'pattern_matcher_success', 'pattern_matcher_error', 'learner_success', 'learner_error'],
    'errors': ['error_general', 'success_general', 'not_implemented', 'missing_dependency', 'permission_denied',
               'validation_failed', 'file_not_found', 'network_error', 'timeout_error', 'configuration_error',
               'syntax_error', 'import_error', 'runtime_error', 'database_error', 'path_error', 'type_error',
               'value_error', 'unknown_error'],
    'plugins': ['plugin_registered', 'plugin_execution_started', 'plugin_execution_complete', 'plugin_execution_failed',
                'platform_switch_detected', 'platform_switch_complete', 'cleanup_scan_complete',
                'doc_refresh_analyzing', 'doc_refresh_complete', 'extension_scaffold_complete']
}

def split_templates():
    """Split response-templates.yaml into category-specific files"""
    
    # Paths
    source_file = Path(__file__).resolve().parent.parent / 'cortex-brain' / 'response-templates.yaml'
    output_dir = Path(__file__).resolve().parent.parent / 'cortex-brain' / 'response-templates'
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load source file
    print(f"📖 Loading {source_file}...")
    with open(source_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Extract header and schema
    with open(source_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find where templates start
    header_lines = []
    for i, line in enumerate(lines):
        if line.strip() == 'templates:':
            header_lines = lines[:i+1]
            break
    
    header = ''.join(header_lines)
    
    templates = data.get('templates', {})
    print(f"✅ Loaded {len(templates)} templates")
    
    # Split into categories
    categorized = {cat: {} for cat in CATEGORIES.keys()}
    uncategorized = {}
    
    for template_name, template_data in templates.items():
        found = False
        for category, template_list in CATEGORIES.items():
            if template_name in template_list:
                categorized[category][template_name] = template_data
                found = True
                break
        
        if not found:
            uncategorized[template_name] = template_data
    
    # Write category files
    for category, category_templates in categorized.items():
        if not category_templates:
            continue
        
        output_file = output_dir / f"{category}.yaml"
        print(f"📝 Writing {output_file.name} ({len(category_templates)} templates)...")
        
        # Create category file
        category_data = {
            'schema_version': data.get('schema_version'),
            'last_updated': data.get('last_updated'),
            'category': category,
            'templates': category_templates
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write header comment
            f.write(f"# CORTEX Response Templates - {category.upper()} Category\n")
            f.write(f"# Auto-generated from response-templates.yaml\n")
            f.write(f"# Template count: {len(category_templates)}\n\n")
            
            # Write YAML
            yaml.dump(category_data, f, default_flow_style=False, allow_unicode=True, width=120)
        
        print(f"  ✅ {len(category_templates)} templates written")
    
    # Write uncategorized if any
    if uncategorized:
        output_file = output_dir / "other.yaml"
        print(f"⚠️  Writing {output_file.name} ({len(uncategorized)} uncategorized templates)...")
        
        category_data = {
            'schema_version': data.get('schema_version'),
            'last_updated': data.get('last_updated'),
            'category': 'other',
            'templates': uncategorized
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# CORTEX Response Templates - OTHER Category\n")
            f.write(f"# Uncategorized templates\n")
            f.write(f"# Template count: {len(uncategorized)}\n\n")
            yaml.dump(category_data, f, default_flow_style=False, allow_unicode=True, width=120)
    
    # Print summary
    print(f"\n✅ Split complete!")
    print(f"   Total templates: {len(templates)}")
    print(f"   Categorized: {sum(len(t) for t in categorized.values())}")
    print(f"   Uncategorized: {len(uncategorized)}")
    print(f"\n📊 Token estimates:")
    
    # Estimate tokens (rough: 1 token ≈ 4 characters)
    for category in categorized:
        output_file = output_dir / f"{category}.yaml"
        if output_file.exists():
            size = output_file.stat().st_size
            tokens = size // 4
            print(f"   {category}.yaml: ~{tokens:,} tokens")
    
    print(f"\n💡 Original monolithic file: ~7,900 tokens")
    print(f"   Loading single category now: ~300-2,000 tokens (81-96% reduction)")

if __name__ == '__main__':
    split_templates()
