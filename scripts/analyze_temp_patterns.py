"""
CORTEX Temporary File Pattern Analyzer
Scans workspace to identify cleanup candidates based on actual file patterns.
"""

import json
import os
import yaml
from pathlib import Path
from collections import defaultdict
import re
from datetime import datetime

def load_patterns_config(config_file='cortex-brain/cleanup-detection-patterns.yaml'):
    """Load detection patterns from YAML configuration."""
    with open(config_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def analyze_patterns(scan_file='temp_file_scan.json', config_file='cortex-brain/cleanup-detection-patterns.yaml'):
    """Analyze file patterns from workspace scan."""
    
    # Load configuration
    config = load_patterns_config(config_file)
    
    # Load scan data
    with open(scan_file, 'r', encoding='utf-8') as f:
        files = json.load(f)
    
    patterns = defaultdict(list)
    temporal_keywords = config['temporal_keywords']
    
    for file_info in files:
        path = file_info['FullName']
        name = os.path.basename(path).lower()
        
        # Extension patterns
        ext = Path(path).suffix
        if ext:
            patterns['extensions'].append(ext)
        
        # Temporal keywords in filename
        for keyword in temporal_keywords:
            if keyword in name:
                patterns[f'keyword_{keyword}'].append(path)
        
        # Backup patterns (.bak, .backup, .old)
        if any(name.endswith(suffix) for suffix in config['temporary_extensions']):
            patterns['backup_extensions'].append(path)
        
        # Dated files (from regex config)
        if re.search(config['regex_patterns']['dated_files'], name):
            patterns['dated_files'].append(path)
        
        # Numbered versions (from regex config)
        if re.search(config['regex_patterns']['versioned_files'], name):
            patterns['versioned_files'].append(path)
        
        # UPPERCASE naming (from regex config)
        if re.search(config['regex_patterns']['uppercase_docs'], os.path.basename(path)):
            patterns['uppercase_files'].append(path)
    
    # Summary report
    print('🔍 PATTERN DISCOVERY RESULTS')
    print('=' * 80)
    print(f'\nConfiguration loaded from: {config_file}')
    print(f'Total files scanned: {len(files)}')
    print(f'\nUnique extensions: {len(set(patterns["extensions"]))}')
    print(f'\nTop 20 extensions by frequency:')
    
    ext_counts = defaultdict(int)
    for ext in patterns['extensions']:
        ext_counts[ext] += 1
    
    for ext, count in sorted(ext_counts.items(), key=lambda x: x[1], reverse=True)[:20]:
        print(f'  {ext:20s} {count:5d} files')
    
    print(f'\n📊 TEMPORAL PATTERN MATCHES:')
    for key in sorted(patterns.keys()):
        if key.startswith('keyword_'):
            keyword = key.replace('keyword_', '')
            count = len(patterns[key])
            if count > 0:
                print(f'  {keyword:15s} {count:5d} files')
    
    print(f'\n🔄 BACKUP/VERSION PATTERNS:')
    print(f'  Backup extensions: {len(patterns["backup_extensions"])} files')
    print(f'  Dated files:       {len(patterns["dated_files"])} files')
    print(f'  Versioned files:   {len(patterns["versioned_files"])} files')
    print(f'  UPPERCASE docs:    {len(patterns["uppercase_files"])} files')
    
    # Show sample files from each category
    print(f'\n📋 SAMPLE FILES BY PATTERN:')
    
    sample_categories = [
        ('backup_extensions', 'Backup Extensions'),
        ('dated_files', 'Dated Files'),
        ('versioned_files', 'Versioned Files'),
        ('uppercase_files', 'UPPERCASE Docs'),
        ('keyword_backup', 'Contains "backup"'),
        ('keyword_temp', 'Contains "temp"'),
        ('keyword_old', 'Contains "old"'),
        ('keyword_summary', 'Contains "summary"'),
        ('keyword_report', 'Contains "report"'),
    ]
    
    for key, label in sample_categories:
        if key in patterns and patterns[key]:
            print(f'\n{label}: ({len(patterns[key])} files)')
            for path in patterns[key][:5]:  # Show first 5
                rel_path = path.replace('D:\\PROJECTS\\CORTEX\\', '')
                print(f'  • {rel_path}')
            if len(patterns[key]) > 5:
                print(f'  ... and {len(patterns[key]) - 5} more')
    
    # Save detailed results
    output_file = 'pattern_analysis.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({k: v for k, v in patterns.items() if k != 'extensions'}, f, indent=2)
    
    print(f'\n✅ Detailed analysis saved to: {output_file}')
    print(f'✅ Full file list in: {scan_file}')
    print(f'✅ Pattern configuration: {config_file}')
    
    # Return statistics for programmatic use
    return {
        'total_files': len(files),
        'pattern_matches': {k: len(v) for k, v in patterns.items() if k != 'extensions'},
        'config': config_file
    }

if __name__ == '__main__':
    stats = analyze_patterns()
