#!/usr/bin/env python3
"""
Verify Documentation Accuracy Script
Ensures documentation accurately reflects implementation status.

Scans HTML/MD files for phrases that imply implementation completion,
cross-references with progress-tracker.json, reports violations.

Usage:
  python scripts/verify_documentation_accuracy.py              # Report violations
  python scripts/verify_documentation_accuracy.py --fix        # Auto-fix violations
  python scripts/verify_documentation_accuracy.py --phase 1    # Check specific phase only
"""

import json
import re
from pathlib import Path
from typing import List, Tuple, Dict
import sys
from src.utils.project_root import get_project_root

# Phrases that imply something is implemented/operational
IMPLEMENTED_PHRASES = [
    r'\bis implemented\b',
    r'\bcurrently running\b',
    r'\bis operational\b',
    r'\bhas been deployed\b',
    r'\bis active\b',
    r'\bthe system (?:now )?(?:uses|enforces|tracks|logs)\b',
    r'\bautomatically (?:logs|tracks|enforces|validates)\b',
    r'\benforcement is active\b',
    r'\bvalidation occurs\b',
    r'\bthe orchestrator (?:handles|manages|processes)\b',
]

# Acceptable qualifiers that indicate design/plan
ACCEPTABLE_QUALIFIERS = [
    r'\bwill be implemented\b',
    r'\bis planned\b',
    r'\bis designed to\b',
    r'\bwhen implemented\b',
    r'\bupon completion\b',
    r'\bafter Phase \d+\b',
    r'\bin the future\b',
    r'\bonce operational\b',
]

# Files to exclude from scanning
EXCLUDE_PATTERNS = [
    'index.html',
    'index-preview.html',
    'cortex-plan-viewer.html',
    'README.md',
]


def load_progress_tracker() -> Dict:
    """Load current implementation status from progress tracker."""
    tracker_path = Path("get_project_root()/cortex-brain/tier1/tracking/progress-tracker.json")
    
    try:
        with open(tracker_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"⚠️  Warning: Could not load progress tracker: {e}")
        return {}


def get_implementation_status(tracker: Dict) -> Dict[str, str]:
    """Extract phase implementation status from tracker."""
    status = {}
    
    # Get current phase
    current = tracker.get('current_phase', {})
    if current:
        phase_num = current.get('number', 1)
        phase_status = current.get('status', 'unknown')
        status[f'phase_{phase_num}'] = phase_status
    
    # Get other phases (if they exist in tracker)
    for i in range(1, 5):
        phase_key = f'phase_{i}'
        if phase_key not in status:
            # Infer status based on current phase
            current_num = current.get('number', 1)
            if i < current_num:
                status[phase_key] = 'completed'
            elif i == current_num:
                status[phase_key] = current.get('status', 'unknown')
            else:
                status[phase_key] = f'blocked_by_phase_{i-1}'
    
    return status


def scan_file_for_violations(filepath: Path, phase_status: Dict[str, str]) -> List[Tuple[int, str, str]]:
    """
    Scan file for implementation claims that violate actual status.
    
    Returns: List of (line_number, violating_text, suggestion)
    """
    violations = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"  ⚠️  Could not read {filepath.name}: {e}")
        return []
    
    for line_num, line in enumerate(lines, start=1):
        # Skip if line has acceptable qualifier
        has_qualifier = any(re.search(pattern, line, re.IGNORECASE) for pattern in ACCEPTABLE_QUALIFIERS)
        if has_qualifier:
            continue
        
        # Check for implemented phrases
        for pattern in IMPLEMENTED_PHRASES:
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                violating_text = match.group(0)
                
                # Generate suggestion
                suggestion = generate_suggestion(violating_text)
                
                violations.append((line_num, violating_text, suggestion))
    
    return violations


def generate_suggestion(violating_text: str) -> str:
    """Generate fix suggestion for violating text."""
    lower_text = violating_text.lower()
    
    if 'is implemented' in lower_text:
        return violating_text.replace('is implemented', 'will be implemented')
    elif 'currently running' in lower_text:
        return violating_text.replace('currently running', 'is designed to run')
    elif 'is operational' in lower_text:
        return violating_text.replace('is operational', 'will be operational')
    elif 'has been deployed' in lower_text:
        return violating_text.replace('has been deployed', 'is planned for deployment')
    elif 'is active' in lower_text:
        return violating_text.replace('is active', 'will be active')
    elif 'the system' in lower_text:
        return violating_text.replace('the system', 'the system will')
    elif 'automatically' in lower_text:
        return f"(when implemented) {violating_text}"
    elif 'enforcement is active' in lower_text:
        return violating_text.replace('enforcement is active', 'enforcement will be active')
    elif 'validation occurs' in lower_text:
        return violating_text.replace('validation occurs', 'validation will occur')
    elif 'orchestrator' in lower_text:
        return f"(once operational) {violating_text}"
    else:
        return f"Add qualifier: 'is planned to', 'will', or 'when implemented'"


def apply_fix_to_file(filepath: Path, violations: List[Tuple[int, str, str]]) -> int:
    """
    Apply automated fixes to file.
    
    Returns: Number of fixes applied
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"    ⚠️  Could not read file for fixing: {e}")
        return 0
    
    fixes_applied = 0
    for line_num, violating_text, suggestion in violations:
        # Only apply fix if suggestion is a direct replacement
        if 'will be' in suggestion or 'is designed to' in suggestion or 'is planned' in suggestion:
            if violating_text in content:
                content = content.replace(violating_text, suggestion, 1)
                fixes_applied += 1
    
    if fixes_applied > 0:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"    ⚠️  Could not write fixes: {e}")
            return 0
    
    return fixes_applied


def scan_documentation(docs_dir: Path, phase_status: Dict[str, str], fix: bool = False, phase_filter: str = None) -> None:
    """Main scanning logic."""
    print(f"🔍 Scanning Documentation for Accuracy Violations\n")
    
    # Display current phase status
    print("Current Implementation Status:")
    for phase, status in phase_status.items():
        status_emoji = {
            'ready_to_implement': '🟡',
            'in_progress': '🔵',
            'completed': '🟢',
            'blocked_by_phase_1': '🔴',
            'blocked_by_phase_2': '🔴',
            'blocked_by_phase_3': '🔴',
        }.get(status, '⚪')
        print(f"  {status_emoji} {phase}: {status}")
    print()
    
    # Get all HTML and MD files
    html_files = list(docs_dir.rglob('*.html'))
    md_files = list(Path("get_project_root()/cortex-brain/documents").rglob('*.md'))
    all_files = html_files + md_files
    
    # Filter out excluded files
    files_to_scan = [f for f in all_files if f.name not in EXCLUDE_PATTERNS]
    
    print(f"Found {len(files_to_scan)} files to scan\n")
    
    total_violations = 0
    total_fixed = 0
    
    for filepath in sorted(files_to_scan):
        # Phase filtering (if specified)
        if phase_filter:
            content_sample = filepath.read_text(encoding='utf-8', errors='ignore')[:500]
            if f"Phase {phase_filter}" not in content_sample and f"phase-{phase_filter}" not in filepath.name:
                continue
        
        violations = scan_file_for_violations(filepath, phase_status)
        
        if violations:
            relative_path = filepath.relative_to(Path("get_project_root()"))
            print(f"⚠️  {relative_path}")
            
            for line_num, violating_text, suggestion in violations:
                print(f"    Line {line_num}: '{violating_text}'")
                print(f"             → Suggest: '{suggestion}'")
            
            total_violations += len(violations)
            
            if fix:
                fixes = apply_fix_to_file(filepath, violations)
                if fixes > 0:
                    print(f"    ✅ Applied {fixes} automated fixes")
                    total_fixed += fixes
            
            print()
    
    # Summary
    print("\n" + "="*60)
    if total_violations == 0:
        print("✅ No accuracy violations found!")
    else:
        print(f"📊 Summary:")
        print(f"  Total violations: {total_violations}")
        if fix:
            print(f"  Automated fixes applied: {total_fixed}")
            print(f"  Manual review needed: {total_violations - total_fixed}")
        else:
            print(f"  Run with --fix to apply automated corrections")
    print("="*60)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify documentation accuracy against implementation status")
    parser.add_argument('--fix', action='store_true', help='Apply automated fixes')
    parser.add_argument('--phase', type=str, help='Filter to specific phase (e.g., "1", "2")')
    
    args = parser.parse_args()
    
    # Load progress tracker
    tracker = load_progress_tracker()
    if not tracker:
        print("❌ Could not load progress tracker. Exiting.")
        sys.exit(1)
    
    phase_status = get_implementation_status(tracker)
    
    # Scan documentation
    docs_dir = Path("get_project_root()/docs")
    scan_documentation(docs_dir, phase_status, fix=args.fix, phase_filter=args.phase)


if __name__ == '__main__':
    main()
