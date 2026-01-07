"""
Planning/Active Folder Analysis Script.

Analyzes files in cortex-brain/documents/planning/active/* 
to identify any organizational issues.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def analyze_planning_active():
    """Analyze planning/active folders."""
    
    active_path = Path('cortex-brain/documents/planning/active')
    
    if not active_path.exists():
        print("❌ Planning active directory not found")
        return
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'total_plans': 0,
        'total_files': 0,
        'plans': {},
        'issues': []
    }
    
    # Scan each plan folder
    for plan_folder in active_path.iterdir():
        if not plan_folder.is_dir():
            continue
        
        plan_name = plan_folder.name
        results['total_plans'] += 1
        
        plan_info = {
            'name': plan_name,
            'path': str(plan_folder.relative_to('.')),
            'files': [],
            'subfolders': defaultdict(list),
            'total_files': 0,
            'issues': []
        }
        
        # Scan all files in plan
        for item in plan_folder.rglob('*'):
            if item.is_file():
                rel_path = item.relative_to(plan_folder)
                plan_info['total_files'] += 1
                results['total_files'] += 1
                
                file_info = {
                    'path': str(rel_path),
                    'size': item.stat().st_size,
                    'extension': item.suffix
                }
                
                # Check if in subfolder
                if len(rel_path.parts) > 1:
                    subfolder = rel_path.parts[0]
                    plan_info['subfolders'][subfolder].append(str(rel_path))
                else:
                    plan_info['files'].append(file_info)
                
                # Check for issues
                # 1. Files without proper extensions
                if not item.suffix:
                    plan_info['issues'].append({
                        'type': 'no_extension',
                        'file': str(rel_path),
                        'severity': 'LOW'
                    })
                
                # 2. Very large files
                if item.stat().st_size > 1_000_000:  # 1MB
                    plan_info['issues'].append({
                        'type': 'large_file',
                        'file': str(rel_path),
                        'size': item.stat().st_size,
                        'severity': 'MEDIUM'
                    })
                
                # 3. Backup files
                if '.bak' in item.name or 'backup' in item.name.lower():
                    plan_info['issues'].append({
                        'type': 'backup_file',
                        'file': str(rel_path),
                        'severity': 'HIGH',
                        'action': 'Move to archives'
                    })
                
                # 4. Duplicate names across subfolders
                # (would need more complex logic)
        
        results['plans'][plan_name] = plan_info
        
        # Check for missing standard structure
        standard_folders = ['analysis', 'context', 'tracking', 'phases', 'features']
        existing_folders = set(plan_info['subfolders'].keys())
        missing = set(standard_folders) - existing_folders
        
        if missing and plan_info['total_files'] > 5:  # Only flag if plan is substantial
            plan_info['issues'].append({
                'type': 'missing_structure',
                'missing_folders': list(missing),
                'severity': 'LOW',
                'note': f'Plan may benefit from {", ".join(missing)} folders'
            })
    
    return results


def generate_report(results):
    """Generate markdown report."""
    lines = []
    
    lines.append("# 📋 Planning/Active Folders Analysis")
    lines.append(f"\n**Generated:** {results['timestamp']}")
    lines.append(f"**Total Active Plans:** {results['total_plans']}")
    lines.append(f"**Total Files:** {results['total_files']}")
    lines.append("\n---\n")
    
    # Per-plan analysis
    for plan_name, plan_info in sorted(results['plans'].items()):
        lines.append(f"## 📁 {plan_name}")
        lines.append(f"\n**Path:** `{plan_info['path']}`")
        lines.append(f"**Files:** {plan_info['total_files']}")
        
        # Subfolders
        if plan_info['subfolders']:
            lines.append(f"\n### Folder Structure")
            for subfolder, files in sorted(plan_info['subfolders'].items()):
                lines.append(f"- `{subfolder}/` ({len(files)} files)")
        
        # Root files
        if plan_info['files']:
            lines.append(f"\n### Root Files ({len(plan_info['files'])})")
            for file_info in plan_info['files']:
                size_kb = file_info['size'] / 1024
                lines.append(f"- `{file_info['path']}` ({size_kb:.1f} KB)")
        
        # Issues
        if plan_info['issues']:
            lines.append(f"\n### ⚠️ Issues ({len(plan_info['issues'])})")
            for issue in plan_info['issues']:
                severity_emoji = {
                    'HIGH': '🔴',
                    'MEDIUM': '🟡',
                    'LOW': '🔵'
                }.get(issue['severity'], '⚪')
                
                lines.append(f"\n{severity_emoji} **{issue['type'].replace('_', ' ').title()}**")
                
                if 'file' in issue:
                    lines.append(f"- File: `{issue['file']}`")
                if 'action' in issue:
                    lines.append(f"- Action: {issue['action']}")
                if 'missing_folders' in issue:
                    lines.append(f"- Missing: {', '.join(issue['missing_folders'])}")
                if 'note' in issue:
                    lines.append(f"- Note: {issue['note']}")
        
        lines.append("\n---\n")
    
    # Summary of all issues
    all_issues = []
    for plan_info in results['plans'].values():
        all_issues.extend(plan_info['issues'])
    
    if all_issues:
        lines.append("## 📊 Issues Summary\n")
        issue_counts = defaultdict(int)
        for issue in all_issues:
            issue_counts[issue['type']] += 1
        
        for issue_type, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"- **{issue_type.replace('_', ' ').title()}:** {count}")
    
    return '\n'.join(lines)


def main():
    """Main entry point."""
    print("=" * 70)
    print("📋 PLANNING/ACTIVE FOLDERS ANALYSIS")
    print("=" * 70)
    
    # Analyze
    results = analyze_planning_active()
    
    # Generate report
    report_md = generate_report(results)
    
    # Save reports
    report_dir = Path('cortex-brain/cleanup-reports')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # JSON
    json_path = report_dir / f'planning-active-analysis-{timestamp}.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"\n✅ JSON: {json_path}")
    
    # Markdown
    md_path = report_dir / f'planning-active-analysis-{timestamp}.md'
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(report_md)
    print(f"✅ Markdown: {md_path}")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    print(f"  Total Plans: {results['total_plans']}")
    print(f"  Total Files: {results['total_files']}")
    
    total_issues = sum(len(p['issues']) for p in results['plans'].values())
    print(f"  Total Issues: {total_issues}")
    print("=" * 70)
    
    # Display report
    print("\n" + report_md)


if __name__ == "__main__":
    main()
