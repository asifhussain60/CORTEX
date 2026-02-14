#!/usr/bin/env python3
"""
Batch nomenclature cleanup script for CORTEX.

Authority: CORE-042 (Hierarchical Terminology)
Purpose: Replace wave/initiative terminology with phase-centric hierarchy
"""

import re
from pathlib import Path
from typing import List, Tuple
import sys


# AC_START: AC-NOMENCLATURE-002
# Description: Batch nomenclature replacement


class NomenclatureCleanup:
    """Handle systematic nomenclature cleanup."""
    
    def __init__(self, dry_run: bool = False):
        """Initialize cleanup handler."""
        self.dry_run = dry_run
        self.replacements = 0
        self.files_modified = 0
        
    def get_replacements(self) -> List[Tuple[str, str, str]]:
        """
        Get list of (pattern, replacement, description) tuples.
        
        Returns:
            List of replacement specifications
        """
        return [
            # Wave terminology - comprehensive patterns
            (r'\bWave-\d+\b', lambda m: f'Phase-{m.group(0)[5:]}', 'Wave-N → Phase-N'),
            (r'\bWave \d+\b', lambda m: f'Phase {m.group(0)[5:]}', 'Wave N → Phase N'),
            (r'\bwave-based plans?\b', 'phase-based plans', 'wave-based → phase-based'),
            (r'\bwave metadata\b', 'phase metadata', 'wave metadata → phase metadata'),
            (r'\bwave registry\b', 'phase registry', 'wave registry → phase registry'),
            (r'\bWave Lifecycle\b', 'Phase Lifecycle', 'Wave Lifecycle → Phase Lifecycle'),
            (r'\bWave Registration\b', 'Phase Registration', 'Wave Registration → Phase Registration'),
            (r'\bWave Execution\b', 'Phase Execution', 'Wave Execution → Phase Execution'),
            (r'\bWave Structure\b', 'Phase Structure', 'Wave Structure → Phase Structure'),
            (r'\bwave can start\b', 'phase can start', 'wave can start → phase can start'),
            (r'\bwave must\b', 'phase must', 'wave must → phase must'),
            (r'\bwave status\b', 'phase status', 'wave status → phase status'),
            (r'\bwave progress\b', 'phase progress', 'wave progress → phase progress'),
            (r'\bwave execution\b', 'phase execution', 'wave execution → phase execution'),
            (r'\bwave orchestration\b', 'phase orchestration', 'wave orchestration → phase orchestration'),
            (r'\bwave plan\b', 'phase plan', 'wave plan → phase plan'),
            (r'\bwave order\b', 'phase order', 'wave order → phase order'),
            (r'\bwave numbers\b', 'phase numbers', 'wave numbers → phase numbers'),
            (r'\bwave entries\b', 'phase entries', 'wave entries → phase entries'),
            (r'\bWaveArchitectureAgent\b', 'PhaseArchitectureAgent', 'WaveArchitectureAgent → PhaseArchitectureAgent'),
            (r'\bwave IDs\b', 'phase IDs', 'wave IDs → phase IDs'),
            (r'\bwave_id\b', 'phase_id', 'wave_id → phase_id'),
            (r'\bwave\.id\b', 'phase.id', 'wave.id → phase.id'),
            (r'\bwaves\[\b', 'phases[', 'waves[ → phases['),
            (r'\bget_wave_status\b', 'get_phase_status', 'get_wave_status → get_phase_status'),
            (r'\bget_wave_progress\b', 'get_phase_progress', 'get_wave_progress → get_phase_progress'),
            (r'\bwave: Wave\b', 'phase: Phase', 'wave: Wave → phase: Phase'),
            (r'\bdependent waves\b', 'dependent phases', 'dependent waves → dependent phases'),
            (r'\bdependent wave\b', 'dependent phase', 'dependent wave → dependent phase'),
            (r'\bOther wave\b', 'Other phase', 'Other wave → Other phase'),
            (r'\bwave organization\b', 'phase organization', 'wave organization → phase organization'),
            (r'\bwave reorganization\b', 'phase reorganization', 'wave reorganization → phase reorganization'),
            (r'\bwave starts\b', 'phase starts', 'wave starts → phase starts'),
            (r'\bwave start condition\b', 'phase start condition', 'wave start condition → phase start condition'),
            (r'\bwave files\b', 'phase files', 'wave files → phase files'),
            (r'\bwave renumbering\b', 'phase renumbering', 'wave renumbering → phase renumbering'),
            (r'\bnew waves\b', 'new phases', 'new waves → new phases'),
            (r'\bsame wave\b', 'same phase', 'same wave → same phase'),
            (r'\bwithin same wave\b', 'within same phase', 'within same wave → within same phase'),
            (r'\bsame wave\b', 'same phase', 'same wave → same phase'),
            (r'\bWave Creation\b', 'Phase Creation', 'Wave Creation → Phase Creation'),
            (r'\bWave Readiness\b', 'Phase Readiness', 'Wave Readiness → Phase Readiness'),
            (r'\bWave Closure\b', 'Phase Closure', 'Wave Closure → Phase Closure'),
            (r'\bNext Wave Planning\b', 'Next Phase Planning', 'Next Wave Planning → Next Phase Planning'),
            (r'\bcompleted wave\b', 'completed phase', 'completed wave → phase'),
            (r'\bsuccessor wave\b', 'successor phase', 'successor wave → phase'),
            (r'\bmark_wave_blocked\b', 'mark_phase_blocked', 'mark_wave_blocked → mark_phase_blocked'),
            (r'\bmark_wave_ready\b', 'mark_phase_ready', 'mark_wave_ready → mark_phase_ready'),
            (r'\bWave YAML\b', 'Phase YAML', 'Wave YAML → Phase YAML'),
            (r'\bparent_wave\b', 'parent_phase', 'parent_wave → parent_phase'),
            (r'\bcurrent_phase\.parent_wave\b', 'current_task.parent_phase', 'parent_wave → parent_phase'),
            
            # Track terminology → Stage terminology
            (r'\bTrack-\d+\b', lambda m: f'Stage-{m.group(0)[6:]}', 'Track-N → Stage-N'),
            (r'\bTrack \d+\b', lambda m: f'Stage {m.group(0)[6:]}', 'Track N → Stage N'),
            (r'\btrack execution\b', 'stage execution', 'track execution → stage execution'),
            (r'\bparallel track\b', 'parallel stage', 'parallel track → stage'),
            (r'\bTrack executor\b', 'Stage executor', 'Track executor → Stage executor'),
            (r'\btrack_id\b', 'stage_id', 'track_id → stage_id'),
            (r'\bmax_parallel_tracks\b', 'max_parallel_stages', 'max_parallel_tracks → max_parallel_stages'),
            (r'\bwithin track\b', 'within stage', 'within track → within stage'),
            (r'\bTrack Parallelism\b', 'Stage Parallelism', 'Track Parallelism → Stage Parallelism'),
            (r'\bparent_track\b', 'parent_stage', 'parent_track → parent_stage'),
            (r'\btrack records\b', 'stage records', 'track records → stage records'),
            (r'\bTrack assignments\b', 'Stage assignments', 'Track assignments → Stage assignments'),
            (r'\btracks?\b', 'stages', 'tracks → stages'),
            (r'\bTracks:\b', 'Stages:', 'Tracks: → Stages:'),
            
            # Initiative terminology → Phase terminology (simplified)
            (r'\bINITIATIVE→PHASE\b', 'PHASE', 'INITIATIVE→PHASE → PHASE'),
            (r'\bINITIATIVE→\b', '', 'Remove INITIATIVE→ prefix'),
            
            # Completed waves → completed phases (in comments/docs)
            (r'\bcompleted waves\b', 'completed phases', 'completed waves → completed phases'),
            (r'\bobsolete-wave-guides\b', 'obsolete-plans', 'obsolete-wave-guides → obsolete-plans'),
        ]
    
    def process_file(self, file_path: Path) -> bool:
        """
        Process single file for nomenclature cleanup.
        
        Args:
            file_path: Path to file to process
        
        Returns:
            True if file was modified, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            file_replacements = 0
            
            for pattern, replacement, desc in self.get_replacements():
                regex = re.compile(pattern, re.IGNORECASE if isinstance(replacement, str) else 0)
                
                # Handle both string and lambda replacements
                if callable(replacement):
                    new_content = regex.sub(replacement, content)
                else:
                    new_content = regex.sub(replacement, content)
                
                if new_content != content:
                    matches = len(regex.findall(content))
                    file_replacements += matches
                    content = new_content
            
            if content != original_content:
                if not self.dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                
                self.replacements += file_replacements
                self.files_modified += 1
                
                status = "[DRY RUN]" if self.dry_run else "[MODIFIED]"
                print(f"{status} {file_path} ({file_replacements} replacements)")
                return True
            
            return False
        
        except (UnicodeDecodeError, PermissionError) as e:
            print(f"[SKIP] {file_path}: {e}")
            return False
    
    def process_directory(
        self, 
        root: Path, 
        extensions: List[str] = None,
        exclude_dirs: List[str] = None
    ) -> None:
        """
        Process all files in directory.
        
        Args:
            root: Root directory to process
            extensions: File extensions to include
            exclude_dirs: Directory names to exclude
        """
        if not root.exists():
            print(f"[SKIP] Directory not found: {root}")
            return
        
        extensions = extensions or ['.md', '.yaml', '.yml']
        exclude_dirs = exclude_dirs or ['archive', '.archive', '_archive', 'obsolete']
        
        print(f"\n📁 Processing: {root}")
        
        for file_path in root.rglob('*'):
            # Skip excluded directories
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue
            
            # Only process specified file types
            if file_path.suffix not in extensions:
                continue
            
            if file_path.is_file():
                self.process_file(file_path)
    
    def run(self, target_dirs: List[Path]) -> None:
        """
        Run cleanup on multiple directories.
        
        Args:
            target_dirs: List of directories to process
        """
        print("=" * 70)
        print("CORTEX Nomenclature Cleanup")
        print("=" * 70)
        print(f"Mode: {'DRY RUN' if self.dry_run else 'MODIFY FILES'}")
        print(f"Targets: {len(target_dirs)} directories")
        print("=" * 70)
        
        for target_dir in target_dirs:
            self.process_directory(target_dir)
        
        print("\n" + "=" * 70)
        print(f"✅ Cleanup {'simulation' if self.dry_run else 'complete'}")
        print(f"📝 Files modified: {self.files_modified}")
        print(f"🔄 Total replacements: {self.replacements}")
        print("=" * 70)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Clean up wave/initiative nomenclature in CORTEX'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    parser.add_argument(
        '--target',
        choices=['registry', 'prompts', 'agents', 'all'],
        default='all',
        help='Target directory to process'
    )
    
    args = parser.parse_args()
    
    # Get workspace root
    workspace_root = Path(__file__).parent.parent
    
    # Define target directories
    targets = {
        'registry': workspace_root / 'cortex-registry' / '_cortex-master',
        'prompts': workspace_root / '.github' / 'prompts',
        'agents': workspace_root / '.github' / 'agents',
    }
    
    # Select targets
    if args.target == 'all':
        target_dirs = list(targets.values())
    else:
        target_dirs = [targets[args.target]]
    
    # Run cleanup
    cleanup = NomenclatureCleanup(dry_run=args.dry_run)
    cleanup.run(target_dirs)


if __name__ == '__main__':
    main()


# AC_COMPLETE: AC-NOMENCLATURE-002 ✅ Batch cleanup script complete
