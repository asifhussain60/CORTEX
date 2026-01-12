"""
ScaffoldingRemovalOrchestrator: Extract and remove phase logic from production code

Responsibility: Identify, extract, and remove hardcoded phase references from
MasterOrchestrator and dependent systems. Phase logic moved to optional PlanningModule.

Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class PhaseReference:
    """Represents a single phase reference found in code"""
    file_path: str
    line_number: int
    line_content: str
    phase_keyword: str
    context: str  # surrounding code


class ScaffoldingRemovalOrchestrator:
    """Orchestrator for removing phase references from production code"""

    def __init__(self):
        self.project_root = Path('/Users/asifhussain/PROJECTS/CORTEX')
        self.backup_dir = self.project_root / 'cortex-brain' / 'backups' / 'phase-removal'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.phase_pattern = re.compile(
            r'(phase_[1-5]|current_phase|phase_number)',
            re.IGNORECASE
        )

    def find_phase_references(self) -> Dict[str, List[PhaseReference]]:
        """Find all phase references in core files"""
        core_files = [
            'src/orchestrators/core/master_orchestrator.py',
            'src/orchestrators/core/state_synchronizer.py',
            'src/infrastructure/atomic_state_manager.py',
            'src/database/planning_state_db.py',
            'src/mcp/housekeeping_tools.py',
        ]

        references = {}
        
        for file_path in core_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                file_refs = self._scan_file(full_path)
                if file_refs:
                    references[file_path] = file_refs

        return references

    def _scan_file(self, file_path: Path) -> List[PhaseReference]:
        """Scan a file for phase references"""
        refs = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except (OSError, UnicodeDecodeError):
            return refs

        for i, line in enumerate(lines, 1):
            # Skip comments and docstrings
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
                continue

            # Find phase references
            matches = self.phase_pattern.finditer(line)
            for match in matches:
                ref = PhaseReference(
                    file_path=str(file_path.relative_to(self.project_root)),
                    line_number=i,
                    line_content=line.rstrip(),
                    phase_keyword=match.group(1),
                    context=self._get_context(lines, i)
                )
                refs.append(ref)

        return refs

    def _get_context(self, lines: List[str], line_number: int, context_lines: int = 2) -> str:
        """Get context around a line"""
        start = max(0, line_number - context_lines - 1)
        end = min(len(lines), line_number + context_lines)
        context = ''.join(lines[start:end])
        return context

    def create_backup(self, file_path: str) -> Optional[str]:
        """Create a backup of a file before modifications"""
        source = self.project_root / file_path
        
        if not source.exists():
            return None

        # Create backup with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = source.name
        backup_path = self.backup_dir / f'{timestamp}_{filename}'

        try:
            with open(source, 'r', encoding='utf-8') as src:
                content = src.read()
            with open(backup_path, 'w', encoding='utf-8') as dst:
                dst.write(content)
            return str(backup_path.relative_to(self.project_root))
        except (OSError, IOError):
            return None

    def extract_phase_logic(self) -> Dict:
        """Extract phase logic into isolated structure"""
        extraction = {
            'phase_definitions': {
                'phase_1': 'Foundation Enhancement',
                'phase_2': 'Orchestration Core',
                'phase_3': 'Feature Orchestrators',
                'phase_4': 'Intelligence Layer',
                'phase_4_5': 'Orchestrator Integration & Audit Validation',
                'phase_5': 'CORTEX Cleanup & Decommission',
            },
            'state_transitions': {
                'phase_1_to_2': ['foundation_complete'],
                'phase_2_to_3': ['orchestration_core_complete'],
                'phase_3_to_4': ['features_complete'],
                'phase_4_to_4_5': ['intelligence_complete'],
                'phase_4_5_to_5': ['integration_validated'],
            },
            'gates': {
                'phase_1': {'threshold': 0.88, 'criteria': ['Verification rate >= 88%']},
                'phase_2': {'threshold': 0.85, 'criteria': ['Tests >= 85% passing']},
                'phase_3': {'threshold': 0.80, 'criteria': ['Orchestrators functional']},
                'phase_4': {'threshold': 0.75, 'criteria': ['Intelligence operational']},
                'phase_4_5': {'threshold': 0.85, 'criteria': ['Audit trail complete']},
                'phase_5': {'threshold': 1.0, 'criteria': ['All references removed']},
            },
            'extracted_at': datetime.now().isoformat(),
            'note': 'This logic is now isolated and will be moved to PlanningModule'
        }
        return extraction

    def get_removal_plan(self) -> Dict:
        """Generate a plan for removing phase references"""
        references = self.find_phase_references()
        
        plan = {
            'total_references': sum(len(refs) for refs in references.values()),
            'files_affected': list(references.keys()),
            'reference_details': {
                file: [asdict(ref) for ref in refs]
                for file, refs in references.items()
            },
            'removal_strategy': {
                'step_1': 'Extract phase definitions to PlanningModule',
                'step_2': 'Replace hardcoded phases with capability-based routing',
                'step_3': 'Update database schema to remove phase columns',
                'step_4': 'Migrate state tracking to capability-based model',
                'step_5': 'Create feature flag for legacy phase support',
            },
            'rollback_capability': 'All backups stored in cortex-brain/backups/phase-removal/',
            'generated_at': datetime.now().isoformat(),
        }
        return plan

    def verify_removal_completeness(self) -> Dict:
        """Verify that all phase references have been removed"""
        references = self.find_phase_references()
        
        verification = {
            'timestamp': datetime.now().isoformat(),
            'total_references_found': sum(len(refs) for refs in references.values()),
            'files_checked': [
                'src/orchestrators/core/master_orchestrator.py',
                'src/orchestrators/core/state_synchronizer.py',
                'src/infrastructure/atomic_state_manager.py',
                'src/database/planning_state_db.py',
            ],
            'files_with_issues': list(references.keys()),
            'status': 'CLEAN' if not references else 'REQUIRES_CLEANUP',
            'details': {
                file: {
                    'reference_count': len(refs),
                    'references': [
                        {
                            'line': ref.line_number,
                            'keyword': ref.phase_keyword,
                            'content': ref.line_content[:100]
                        }
                        for ref in refs
                    ]
                }
                for file, refs in references.items()
            }
        }
        return verification
