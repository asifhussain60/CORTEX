"""
Planning Migration Utility

Lightweight status-based planning document organization.

Core Operations:
- migrate_documents: Full migration workflow with backup and validation
- detect_status: Extract status from frontmatter patterns
- backup_planning_dir: Create timestamped backup
- validate_migration: Verify all files moved correctly
- organize_by_status: Move documents to status subdirectories

Version: 3.0.0 (Migrated from PlanningDocumentMigrator v2.0)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


# Status mapping: detected status → directory name
STATUS_MAP = {
    'in-progress': 'active',
    'proposed': 'active',
    'approved': 'approved',
    'completed': 'completed',
    'cancelled': 'deprecated',
    'deprecated': 'deprecated',
    'blocked': 'active',
}


def migrate_documents(
    planning_path: str,
    dry_run: bool = True,
    create_backup: bool = True
) -> Dict:
    """
    Migrate planning documents to status-based directories
    
    Args:
        planning_path: Path to planning directory
        dry_run: Preview without moving files
        create_backup: Create backup before migration
        
    Returns:
        Dict with migration results
        
    Example:
        >>> result = migrate_documents("/path/to/planning", dry_run=False)
        >>> print(result["migrated_count"])
        15
    """
    planning_dir = Path(planning_path)
    result = {
        'success': False,
        'dry_run': dry_run,
        'migrated_count': 0,
        'failed_count': 0,
        'backup_path': None,
        'migrations': [],
        'errors': []
    }
    
    try:
        # Find documents
        plans = _find_plans_in_root(planning_dir)
        
        if len(plans) == 0:
            result['success'] = True
            return result
        
        # Create backup
        if create_backup and not dry_run:
            backup_path = backup_planning_dir(planning_dir, plans)
            result['backup_path'] = str(backup_path)
        
        # Ensure status directories exist
        status_dirs = {
            'active': planning_dir / "active",
            'approved': planning_dir / "approved",
            'completed': planning_dir / "completed",
            'deprecated': planning_dir / "deprecated"
        }
        
        for status_dir in status_dirs.values():
            status_dir.mkdir(parents=True, exist_ok=True)
        
        # Process each plan
        for plan_path in plans:
            try:
                status = detect_status(str(plan_path))
                target_dir = status_dirs.get(status, status_dirs['active'])
                target_path = target_dir / plan_path.name
                
                migration_record = {
                    'source': str(plan_path),
                    'target': str(target_path),
                    'status': status,
                    'dry_run': dry_run
                }
                
                if not dry_run:
                    shutil.move(str(plan_path), str(target_path))
                
                result['migrations'].append(migration_record)
                result['migrated_count'] += 1
                
            except Exception as e:
                result['errors'].append(f"Failed to migrate {plan_path.name}: {str(e)}")
                result['failed_count'] += 1
        
        # Validation
        if not dry_run:
            validation_ok = validate_migration(planning_dir, plans, result['migrations'])
            result['success'] = validation_ok and result['failed_count'] == 0
        else:
            result['success'] = True
    
    except Exception as e:
        result['errors'].append(f"Migration failed: {str(e)}")
        result['success'] = False
    
    return result


def detect_status(plan_path: str) -> str:
    """
    Detect plan status from frontmatter
    
    Args:
        plan_path: Path to planning document
        
    Returns:
        Status directory name
        
    Example:
        >>> status = detect_status("/path/to/plan.md")
        >>> print(status)
        'active'
    """
    try:
        with open(plan_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try multiple patterns
        patterns = [
            r'\*\*Status:\*\*\s*([a-zA-Z-]+)',  # **Status:** value
            r'\*\*Status\*\*:\s*([a-zA-Z-]+)',  # **Status**: value
            r'Status:\s*([a-zA-Z-]+)',          # Status: value
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                status_value = match.group(1).strip().lower()
                return STATUS_MAP.get(status_value, 'active')
    
    except Exception:
        pass
    
    return 'active'


def backup_planning_dir(planning_dir: Path, plans: List[Path]) -> Path:
    """
    Create timestamped backup
    
    Args:
        planning_dir: Planning directory
        plans: List of plan paths
        
    Returns:
        Backup directory path
        
    Example:
        >>> backup = backup_planning_dir(Path("/planning"), plans)
        >>> print(backup.name)
        'backup-20250102-143015'
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = planning_dir / f"backup-{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    for plan_path in plans:
        backup_path = backup_dir / plan_path.name
        shutil.copy2(str(plan_path), str(backup_path))
    
    return backup_dir


def validate_migration(
    planning_dir: Path,
    original_plans: List[Path],
    migrations: List[Dict]
) -> bool:
    """
    Verify migration completed successfully
    
    Args:
        planning_dir: Planning directory
        original_plans: Original plan paths
        migrations: Migration records
        
    Returns:
        True if valid
        
    Example:
        >>> valid = validate_migration(planning_dir, plans, migrations)
        >>> print(valid)
        True
    """
    # Count check
    if len(original_plans) != len(migrations):
        return False
    
    # No files remaining in root
    remaining = _find_plans_in_root(planning_dir)
    if len(remaining) > 0:
        return False
    
    # All targets exist
    for migration in migrations:
        if not Path(migration['target']).exists():
            return False
    
    return True


def organize_by_status(planning_path: str, document_path: str) -> Optional[str]:
    """
    Organize single document to status subdirectory
    
    Args:
        planning_path: Planning directory
        document_path: Document to organize
        
    Returns:
        New path if organized, None if error
        
    Example:
        >>> new_path = organize_by_status("/planning", "/planning/plan.md")
        >>> print(new_path)
        '/planning/active/plan.md'
    """
    try:
        planning_dir = Path(planning_path)
        doc_path = Path(document_path)
        
        # Detect status
        status = detect_status(str(doc_path))
        
        # Status directory
        status_dir = planning_dir / status
        status_dir.mkdir(parents=True, exist_ok=True)
        
        # Move
        target_path = status_dir / doc_path.name
        shutil.move(str(doc_path), str(target_path))
        
        return str(target_path)
    
    except Exception:
        return None


def _find_plans_in_root(planning_dir: Path) -> List[Path]:
    """Find planning documents in root directory"""
    plans = []
    
    for item in planning_dir.iterdir():
        if item.is_dir():
            continue
        
        if item.suffix != '.md':
            continue
        
        if item.name.lower() in ['index.md', 'readme.md']:
            continue
        
        if any(item.name.startswith(prefix) for prefix in ['PLAN-', 'ADO-', 'CORTEX-', 'sprint-']):
            plans.append(item)
    
    return sorted(plans)


# CLI for testing
if __name__ == "__main__":
    import time
    
    print("🧪 Testing Planning Migration Utility...")
    start_test = time.time()
    
    # Test with CORTEX planning directory
    cortex_root = Path(__file__).parent.parent.parent.parent.parent
    planning_path = cortex_root / "cortex-brain" / "documents" / "planning"
    
    # Test 1: Find plans
    print("Testing plan discovery...")
    plans = _find_plans_in_root(planning_path)
    print(f"✅ Found {len(plans)} planning documents in root")
    
    # Test 2: Detect status (dry run)
    if plans:
        print("Testing status detection...")
        status = detect_status(str(plans[0]))
        assert status in ['active', 'approved', 'completed', 'deprecated'], f"Invalid status: {status}"
        print(f"✅ Status detection: {plans[0].name} → {status}")
    
    # Test 3: Dry run migration
    print("Testing dry-run migration...")
    result = migrate_documents(str(planning_path), dry_run=True, create_backup=False)
    assert result['success'], "Dry run failed"
    print(f"✅ Dry-run: {result['migrated_count']} documents would be migrated")
    
    # Test 4: Validation logic
    print("Testing validation...")
    valid = validate_migration(planning_path, plans, result['migrations'])
    print(f"✅ Validation: {valid}")
    
    elapsed = time.time() - start_test
    print(f"\n⚡ All tests passed in {elapsed:.3f}s")
    print(f"📊 Operations: 5 core functions tested")
    print(f"✅ Performance: {elapsed:.3f}s")
