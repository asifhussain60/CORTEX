#!/usr/bin/env python3
"""
CORTEX5 Plan Viewer Auto-Updater

Updates plan-viewer.html with current epic progress from markdown.
Extracts metrics, phase status, and commits from 00-cortex5-enhancement-epic.md.

Usage:
    python3 update-plan-viewer.py [--dry-run]

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime


def parse_epic_markdown(epic_path: Path) -> Dict:
    """Extract metrics and status from epic markdown."""
    content = epic_path.read_text()
    
    # Extract overall progress percentage
    progress_match = re.search(r'Epic Completion:\*\*.*?(\d+)%', content)
    progress = int(progress_match.group(1)) if progress_match else 0
    
    # Extract phases completed
    phases_match = re.search(r'\((\d+) of (\d+) phases\)', content)
    if phases_match:
        completed_phases = int(phases_match.group(1))
        total_phases = int(phases_match.group(2))
    else:
        completed_phases, total_phases = 3, 5
    
    # Extract metrics from progress table
    metrics = {
        'lines': 0,
        'tests': 0,
        'files': 0,
        'commits': 0
    }
    
    # Find metrics table - extract LAST column value (Total)
    # Format: | **Lines of Code** | 2,506 | 2,800 | 2,110 | ~1,500 | ~8,916 |
    lines_match = re.search(r'\| \*\*Lines of Code\*\* \|(?:.*?\|){4}\s*~?(\d+,?\d+)\s*\|', content)
    if lines_match:
        metrics['lines'] = int(lines_match.group(1).replace(',', ''))
    
    tests_match = re.search(r'\| \*\*Unit Tests\*\* \|(?:.*?\|){4}\s*~?(\d+)\+?\s*\|', content)
    if tests_match:
        metrics['tests'] = int(tests_match.group(1))
    
    files_match = re.search(r'\| \*\*Files Created\*\* \|(?:.*?\|){4}\s*~?(\d+)\s*\|', content)
    if files_match:
        metrics['files'] = int(files_match.group(1))
    
    # Count commits from the Commits row - last column shows number
    commits_match = re.search(r'\| \*\*Commits\*\* \|(?:.*?\|){4}\s*(\d+)\s*\|', content)
    if commits_match:
        metrics['commits'] = int(commits_match.group(1))
    
    # Extract phase information
    phases = []
    phase_pattern = re.compile(
        r'### Phase (\d+):.*?\n\*\*Status:\*\* (.*?)\n.*?'
        r'\*\*(?:Commit|Actual Lines):\*\*.*?(?:(\w{9})|(\d+,?\d*))',
        re.DOTALL
    )
    
    for match in phase_pattern.finditer(content):
        phase_num = int(match.group(1))
        status = match.group(2).strip()
        commit = match.group(3) if match.group(3) else None
        
        # Determine phase status class
        if 'Complete' in status or '✅' in status:
            status_class = 'complete'
            icon = '✅'
            badge = 'status-complete'
        elif 'In Progress' in status or 'Next' in status or '🔄' in status:
            status_class = 'in-progress'
            icon = '🔄'
            badge = 'status-progress'
        else:
            status_class = 'pending'
            icon = '⏳'
            badge = 'status-pending'
        
        phases.append({
            'number': phase_num,
            'status_class': status_class,
            'icon': icon,
            'badge': badge,
            'commit': commit
        })
    
    return {
        'progress': progress,
        'completed_phases': completed_phases,
        'total_phases': total_phases,
        'metrics': metrics,
        'phases': phases,
        'timestamp': datetime.now().strftime('%B %d, %Y at %I:%M %p')
    }


def update_html(html_path: Path, data: Dict) -> str:
    """Update HTML with extracted data."""
    content = html_path.read_text()
    
    # Update progress percentage
    content = re.sub(
        r'<div class="progress-percentage" id="overallProgress">\d+%</div>',
        f'<div class="progress-percentage" id="overallProgress">{data["progress"]}%</div>',
        content
    )
    
    # Update progress bar
    content = re.sub(
        r'<div class="progress-bar" id="progressBar" style="width: \d+%;">',
        f'<div class="progress-bar" id="progressBar" style="width: {data["progress"]}%;">',
        content
    )
    
    content = re.sub(
        r'(\d+) of (\d+) Phases Complete',
        f'{data["completed_phases"]} of {data["total_phases"]} Phases Complete',
        content
    )
    
    # Update metrics
    metrics = data['metrics']
    content = re.sub(
        r'<div class="metric-value" id="totalLines">\d+,?\d*</div>',
        f'<div class="metric-value" id="totalLines">{metrics["lines"]:,}</div>',
        content
    )
    
    content = re.sub(
        r'<div class="metric-value" id="totalTests">\d+</div>',
        f'<div class="metric-value" id="totalTests">{metrics["tests"]}</div>',
        content
    )
    
    content = re.sub(
        r'<div class="metric-value" id="totalFiles">\d+</div>',
        f'<div class="metric-value" id="totalFiles">{metrics["files"]}</div>',
        content
    )
    
    content = re.sub(
        r'<div class="metric-value" id="totalCommits">\d+</div>',
        f'<div class="metric-value" id="totalCommits">{metrics["commits"]}</div>',
        content
    )
    
    # Update phase cards (Phase 4 and 5 status)
    for phase in data['phases']:
        if phase['number'] == 4:
            # Update Phase 4 card class
            content = re.sub(
                r'(<div class="phase-card )(in-progress|pending|complete)(">[\s\S]*?<span class="phase-icon">)[🔄⏳✅]',
                rf'\g<1>{phase["status_class"]}\g<3>{phase["icon"]}',
                content,
                count=1
            )
        elif phase['number'] == 5:
            # Update Phase 5 card class (appears after Phase 4)
            pattern = r'(<div class="phase-card )(pending|in-progress|complete)(">[\s\S]*?Phase 5:[\s\S]*?<span class="phase-icon">)[⏳🔄✅]'
            content = re.sub(
                pattern,
                rf'\g<1>{phase["status_class"]}\g<3>{phase["icon"]}',
                content,
                count=1
            )
    
    return content


def main():
    """Main execution."""
    dry_run = '--dry-run' in sys.argv
    
    # Paths
    script_dir = Path(__file__).parent
    epic_path = script_dir.parent / '00-cortex5-enhancement-epic.md'
    html_path = script_dir / 'plan-viewer.html'
    
    if not epic_path.exists():
        print(f"❌ Epic file not found: {epic_path}")
        sys.exit(1)
    
    if not html_path.exists():
        print(f"❌ HTML file not found: {html_path}")
        sys.exit(1)
    
    print("🔍 Parsing epic markdown...")
    data = parse_epic_markdown(epic_path)
    
    print(f"\n📊 Extracted Data:")
    print(f"   Progress: {data['progress']}%")
    print(f"   Phases: {data['completed_phases']} of {data['total_phases']}")
    print(f"   Lines: {data['metrics']['lines']:,}")
    print(f"   Tests: {data['metrics']['tests']}")
    print(f"   Files: {data['metrics']['files']}")
    print(f"   Commits: {data['metrics']['commits']}")
    print(f"   Timestamp: {data['timestamp']}")
    
    print("\n🔄 Updating HTML...")
    updated_content = update_html(html_path, data)
    
    if dry_run:
        print("\n🔍 DRY RUN - Changes not saved")
        print("\nPreview of changes:")
        print(f"   Progress: {data['progress']}%")
        print(f"   Phases: {data['completed_phases']} of {data['total_phases']}")
        print(f"   Metrics updated: ✓")
    else:
        html_path.write_text(updated_content)
        print(f"\n✅ Updated: {html_path}")
        print(f"   Progress: {data['progress']}%")
        print(f"   Timestamp: {data['timestamp']}")
        print("\n💡 Next steps:")
        print(f"   1. Open in browser: open {html_path}")
        print(f"   2. Verify changes look correct")
        print(f"   3. Commit: git add {html_path} && git commit -m 'Update plan viewer progress'")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
