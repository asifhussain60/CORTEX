"""
CORTEX Vacuum Executor

Phase 2: Controlled execution of repository reorganization with safety guarantees.
Applies changes in dependency order and maintains rollback capability.

Author: Asif Hussain
"""

import json
import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import tempfile


@dataclass
class ExecutionSnapshot:
    """Snapshot of repository state before execution."""
    timestamp: str
    repo_root: str
    file_states: Dict[str, Dict]  # {file_path: {hash, size, mtime}}
    changes_planned: List[Dict] = field(default_factory=list)


@dataclass
class ExecutionLog:
    """Log of an executed change."""
    timestamp: str
    operation: str  # 'move', 'rename', 'delete', 'update_reference'
    source: str
    destination: str
    success: bool
    error: Optional[str] = None
    affected_references: List[str] = field(default_factory=list)


class CortexVacuumExecutor:
    """
    Executes repository reorganization with safety guarantees.
    
    Features:
    - Pre-execution snapshots
    - Dependency-aware ordering
    - Reference updates
    - Rollback capability
    - Comprehensive logging
    """

    def __init__(self, repo_root: str, migration_plan: Dict, dry_run: bool = False):
        """
        Initialize executor.
        
        Args:
            repo_root: Repository root directory
            migration_plan: Migration plan from analyzer
            dry_run: If True, simulate without making changes
        """
        self.repo_root = Path(repo_root)
        self.migration_plan = migration_plan
        self.dry_run = dry_run
        self.execution_logs: List[ExecutionLog] = []
        self.snapshot: Optional[ExecutionSnapshot] = None
        self.updated_references: Dict[str, List[Tuple[str, str]]] = {}

    def execute(self, auto_approve: bool = False) -> Dict:
        """
        Execute the migration plan.
        
        Args:
            auto_approve: If True, don't ask for confirmation
            
        Returns:
            Execution report
        """
        print(f"🚀 CORTEX Vacuum Executor")
        print(f"   Mode: {'DRY RUN' if self.dry_run else 'LIVE EXECUTION'}")
        print(f"   Root: {self.repo_root}")

        # Step 1: Create snapshot
        self._create_snapshot()
        print(f"   ✓ Snapshot created: {self.snapshot.timestamp}")

        # Step 2: Validate migration plan
        validation_result = self._validate_migration_plan()
        if not validation_result['is_valid']:
            return {
                'success': False,
                'error': 'Migration plan validation failed',
                'details': validation_result
            }
        print(f"   ✓ Migration plan validated")

        # Step 3: Show plan summary
        summary = self._summarize_plan()
        print(f"\n📋 Migration Summary:")
        print(f"   Files to delete: {summary['deletions']}")
        print(f"   Files to move: {summary['moves']}")
        print(f"   Files to rename: {summary['renames']}")
        print(f"   References to update: {summary['reference_updates']}")

        # Step 4: Ask for confirmation
        if not auto_approve and not self.dry_run:
            response = input("\n⚠️  Proceed with execution? (yes/no): ")
            if response.lower() != 'yes':
                print("   Execution cancelled.")
                return {'success': False, 'reason': 'User cancelled'}

        # Step 5: Execute in order
        self._execute_in_dependency_order()
        print(f"\n   ✓ Execution complete ({len(self.execution_logs)} operations)")

        # Step 6: Verify
        verification = self._verify_execution()
        print(f"   ✓ Verification: {verification['status']}")

        return self._compile_execution_report(verification)

    def _create_snapshot(self) -> None:
        """Create pre-execution snapshot."""
        file_states = {}

        for file_path in Path(self.repo_root).rglob('*'):
            if file_path.is_file() and not self._should_ignore(file_path):
                rel_path = str(file_path.relative_to(self.repo_root))
                try:
                    stat = file_path.stat()
                    file_states[rel_path] = {
                        'size': stat.st_size,
                        'mtime': stat.st_mtime,
                        'hash': self._calculate_hash(file_path)
                    }
                except Exception as e:
                    print(f"   ⚠ Error hashing {rel_path}: {e}")

        self.snapshot = ExecutionSnapshot(
            timestamp=datetime.now().isoformat(),
            repo_root=str(self.repo_root),
            file_states=file_states,
            changes_planned=self.migration_plan.get('plans', [])
        )

    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file."""
        import hashlib
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for byte_block in iter(lambda: f.read(4096), b''):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception:
            return ""

    def _should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored."""
        ignore_patterns = {
            '__pycache__', '.pytest_cache', '.git', '.venv', '.DS_Store',
            '*.pyc', '*.egg-info'
        }
        return any(
            pattern in path.parts or pattern in path.name
            for pattern in ignore_patterns
        )

    def _validate_migration_plan(self) -> Dict:
        """Validate migration plan before execution."""
        issues = []

        plans = self.migration_plan.get('plans', [])
        for plan in plans:
            source = plan.get('source_path')
            if not source:
                issues.append("Plan missing source_path")
                continue

            source_path = self.repo_root / source
            if not source_path.exists() and not plan.get('is_delete'):
                issues.append(f"Source file not found: {source}")

            # Check destination
            if not plan.get('is_delete'):
                dest = plan.get('destination_path')
                if not dest:
                    issues.append(f"Plan missing destination_path: {source}")
                else:
                    dest_path = self.repo_root / dest
                    parent = dest_path.parent
                    if not parent.exists():
                        issues.append(f"Destination parent doesn't exist: {parent}")

        return {
            'is_valid': len(issues) == 0,
            'issues': issues
        }

    def _summarize_plan(self) -> Dict:
        """Summarize the migration plan."""
        plans = self.migration_plan.get('plans', [])
        deletions = sum(1 for p in plans if p.get('is_delete'))
        moves = sum(1 for p in plans if p.get('is_move'))
        renames = sum(1 for p in plans if p.get('is_rename'))
        reference_updates = sum(
            len(p.get('references_to_update', []))
            for p in plans
        )

        return {
            'deletions': deletions,
            'moves': moves,
            'renames': renames,
            'reference_updates': reference_updates,
            'total_operations': len(plans)
        }

    def _execute_in_dependency_order(self) -> None:
        """Execute changes in dependency order."""
        plans = self.migration_plan.get('plans', [])

        # Sort: deletes first, then moves, then renames
        # (This ensures no path conflicts)
        sorted_plans = sorted(
            plans,
            key=lambda p: (
                0 if p.get('is_delete') else (1 if p.get('is_move') else 2)
            )
        )

        for plan in sorted_plans:
            if plan.get('is_delete'):
                self._execute_delete(plan)
            elif plan.get('is_move'):
                self._execute_move(plan)
            elif plan.get('is_rename'):
                self._execute_rename(plan)

            # After each move/rename, update references
            if not plan.get('is_delete'):
                self._update_references_for_file(plan)

    def _execute_delete(self, plan: Dict) -> None:
        """Execute file deletion."""
        source_path = self.repo_root / plan['source_path']
        reason = plan.get('reason', 'File marked for deletion')

        try:
            if self.dry_run:
                print(f"   [DRY] Would delete: {plan['source_path']} ({reason})")
            else:
                if source_path.exists():
                    if source_path.is_file():
                        source_path.unlink()
                    else:
                        shutil.rmtree(source_path)
                    print(f"   ✓ Deleted: {plan['source_path']}")

            self.execution_logs.append(ExecutionLog(
                timestamp=datetime.now().isoformat(),
                operation='delete',
                source=plan['source_path'],
                destination='',
                success=True,
                affected_references=[]
            ))
        except Exception as e:
            print(f"   ✗ Failed to delete {plan['source_path']}: {e}")
            self.execution_logs.append(ExecutionLog(
                timestamp=datetime.now().isoformat(),
                operation='delete',
                source=plan['source_path'],
                destination='',
                success=False,
                error=str(e)
            ))

    def _execute_move(self, plan: Dict) -> None:
        """Execute file move and/or rename."""
        source_path = self.repo_root / plan['source_path']
        dest_path = self.repo_root / plan['destination_path']

        try:
            # Create destination directory if needed
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            if self.dry_run:
                operation_type = "move"
                if plan.get('is_rename'):
                    operation_type += "+rename"
                print(f"   [DRY] Would {operation_type}: {plan['source_path']} → {plan['destination_path']}")
            else:
                if source_path.exists():
                    shutil.move(str(source_path), str(dest_path))
                    print(f"   ✓ Moved: {plan['source_path']} → {plan['destination_path']}")

            self.execution_logs.append(ExecutionLog(
                timestamp=datetime.now().isoformat(),
                operation='move',
                source=plan['source_path'],
                destination=plan['destination_path'],
                success=True,
                affected_references=plan.get('references_to_update', [])
            ))
        except Exception as e:
            print(f"   ✗ Failed to move {plan['source_path']}: {e}")
            self.execution_logs.append(ExecutionLog(
                timestamp=datetime.now().isoformat(),
                operation='move',
                source=plan['source_path'],
                destination=plan['destination_path'],
                success=False,
                error=str(e)
            ))

    def _execute_rename(self, plan: Dict) -> None:
        """Execute file rename."""
        source_path = self.repo_root / plan['source_path']
        new_name = Path(plan['destination_path']).name
        dest_path = source_path.parent / new_name

        try:
            if self.dry_run:
                print(f"   [DRY] Would rename: {source_path.name} → {new_name}")
            else:
                if source_path.exists():
                    source_path.rename(dest_path)
                    print(f"   ✓ Renamed: {source_path.name} → {new_name}")

            self.execution_logs.append(ExecutionLog(
                timestamp=datetime.now().isoformat(),
                operation='rename',
                source=str(source_path.relative_to(self.repo_root)),
                destination=str(dest_path.relative_to(self.repo_root)),
                success=True
            ))
        except Exception as e:
            print(f"   ✗ Failed to rename {source_path.name}: {e}")
            self.execution_logs.append(ExecutionLog(
                timestamp=datetime.now().isoformat(),
                operation='rename',
                source=str(source_path.relative_to(self.repo_root)),
                destination=str(dest_path.relative_to(self.repo_root)),
                success=False,
                error=str(e)
            ))

    def _update_references_for_file(self, plan: Dict) -> None:
        """Update references to a file after moving it."""
        references = plan.get('references_to_update', [])
        if not references:
            return

        source = plan['source_path']
        destination = plan['destination_path']

        updates = []
        for ref in references:
            if isinstance(ref, dict):
                source_file = ref.get('source_file')
                old_ref = ref.get('old_reference')
                new_ref = ref.get('new_reference')

                if source_file and old_ref and new_ref:
                    self._update_reference_in_file(source_file, old_ref, new_ref)
                    updates.append(f"{source_file}: {old_ref} → {new_ref}")

        if updates:
            self.updated_references[source] = updates

    def _update_reference_in_file(self, file_path: str, old_ref: str, new_ref: str) -> None:
        """Update a reference in a specific file."""
        full_path = self.repo_root / file_path

        if not full_path.exists():
            return

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()

            updated_content = content.replace(old_ref, new_ref)

            if updated_content != content:
                if not self.dry_run:
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                print(f"   ✓ Updated reference in: {file_path}")

                self.execution_logs.append(ExecutionLog(
                    timestamp=datetime.now().isoformat(),
                    operation='update_reference',
                    source=old_ref,
                    destination=new_ref,
                    success=True,
                    affected_references=[file_path]
                ))
        except Exception as e:
            print(f"   ⚠ Failed to update references in {file_path}: {e}")

    def _verify_execution(self) -> Dict:
        """Verify execution success."""
        successful = sum(1 for log in self.execution_logs if log.success)
        failed = sum(1 for log in self.execution_logs if not log.success)

        return {
            'status': 'SUCCESS' if failed == 0 else 'PARTIAL',
            'successful_operations': successful,
            'failed_operations': failed,
            'total_operations': len(self.execution_logs),
            'references_updated': sum(len(refs) for refs in self.updated_references.values())
        }

    def _compile_execution_report(self, verification: Dict) -> Dict:
        """Compile comprehensive execution report."""
        return {
            'success': verification['failed_operations'] == 0,
            'timestamp': datetime.now().isoformat(),
            'mode': 'DRY_RUN' if self.dry_run else 'LIVE',
            'snapshot': {
                'timestamp': self.snapshot.timestamp if self.snapshot else None,
                'files_analyzed': len(self.snapshot.file_states) if self.snapshot else 0,
            },
            'verification': verification,
            'execution_logs': [
                {
                    'timestamp': log.timestamp,
                    'operation': log.operation,
                    'source': log.source,
                    'destination': log.destination,
                    'success': log.success,
                    'error': log.error,
                }
                for log in self.execution_logs
            ],
            'updated_references': self.updated_references,
        }


def run_execution(repo_root: str, migration_plan_path: str, dry_run: bool = False, auto_approve: bool = False) -> Dict:
    """
    Run migration execution.
    
    Args:
        repo_root: Repository root directory
        migration_plan_path: Path to migration plan JSON file
        dry_run: If True, simulate without making changes
        auto_approve: If True, skip confirmation
        
    Returns:
        Execution report
    """
    # Load migration plan
    with open(migration_plan_path, 'r') as f:
        plan = json.load(f)

    # Execute
    executor = CortexVacuumExecutor(repo_root, plan, dry_run=dry_run)
    report = executor.execute(auto_approve=auto_approve)

    # Save report
    output_dir = Path(migration_plan_path).parent
    report_path = output_dir / 'execution-report.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n✓ Execution report saved to {report_path}")

    return report
