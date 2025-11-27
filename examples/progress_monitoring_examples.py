"""
Progress Monitoring Examples

Demonstrates various usage patterns for the universal progress monitoring system.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import sys
import time
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import with_progress, yield_progress


# ============================================================================
# EXAMPLE 1: Simple File Processing
# ============================================================================

@with_progress(operation_name="File Processing")
def process_files(file_paths: List[Path]) -> Dict[str, Any]:
    """
    Process a list of files with automatic progress monitoring.
    
    Progress activates automatically if processing takes >5 seconds.
    """
    results = []
    
    for i, path in enumerate(file_paths, 1):
        # Update progress (auto-starts monitor if >5s elapsed)
        yield_progress(i, len(file_paths), f"Processing {path.name}")
        
        # Simulate work
        time.sleep(0.1)  # Replace with actual file processing
        
        results.append({
            'file': path.name,
            'status': 'processed'
        })
    
    return {
        'total': len(results),
        'processed': len([r for r in results if r['status'] == 'processed'])
    }


# ============================================================================
# EXAMPLE 2: Multi-Phase Operation
# ============================================================================

@with_progress(
    operation_name="System Alignment",
    hang_timeout=60.0,  # Longer timeout for complex operations
    threshold_seconds=3.0  # Lower threshold for demo
)
def align_system_multi_phase() -> Dict[str, Any]:
    """
    Multi-phase operation with progress tracking across phases.
    
    Each phase updates progress relative to total work.
    """
    # Phase 1: Scanning
    scan_items = 30
    for i in range(1, scan_items + 1):
        yield_progress(i, 100, f"Phase 1: Scanning item {i}")
        time.sleep(0.05)
    
    # Phase 2: Analysis
    analysis_items = 40
    for i in range(1, analysis_items + 1):
        current = scan_items + i
        yield_progress(current, 100, f"Phase 2: Analyzing item {i}")
        time.sleep(0.05)
    
    # Phase 3: Fixing
    fix_items = 30
    for i in range(1, fix_items + 1):
        current = scan_items + analysis_items + i
        yield_progress(current, 100, f"Phase 3: Fixing issue {i}")
        time.sleep(0.05)
    
    return {
        'scanned': scan_items,
        'analyzed': analysis_items,
        'fixed': fix_items
    }


# ============================================================================
# EXAMPLE 3: Database Operations
# ============================================================================

@with_progress(
    operation_name="Database Migration",
    threshold_seconds=1.0  # Lower threshold for demo
)
def migrate_database_tables(table_names: List[str]) -> Dict[str, Any]:
    """
    Database migration with progress monitoring.
    
    Lower threshold (2s) since database ops are typically slower.
    """
    migrated = []
    
    for i, table in enumerate(table_names, 1):
        yield_progress(i, len(table_names), f"Migrating table: {table}")
        
        # Simulate database migration
        time.sleep(0.2)
        
        migrated.append(table)
    
    return {
        'total_tables': len(table_names),
        'migrated': len(migrated)
    }


# ============================================================================
# EXAMPLE 4: Fast Operation (No Progress)
# ============================================================================

@with_progress(threshold_seconds=5.0)
def quick_validation(items: List[str]) -> bool:
    """
    Fast operation that completes before threshold.
    
    Progress monitoring won't activate - operation completes too quickly.
    """
    for i, item in enumerate(items, 1):
        # This will be called but monitoring won't start
        yield_progress(i, len(items), f"Validating {item}")
        time.sleep(0.01)  # Fast operation
    
    return True


# ============================================================================
# EXAMPLE 5: Nested Operations (Orchestrator Pattern)
# ============================================================================

class ExampleOrchestrator:
    """Example orchestrator with progress monitoring"""
    
    @with_progress(
        operation_name="Complete System Check",
        threshold_seconds=1.0  # Lower threshold for demo
    )
    def run_complete_check(self) -> Dict[str, Any]:
        """
        Orchestrator running multiple sub-operations.
        
        Only the outer operation shows progress - nested operations
        detect existing monitor and don't create new ones.
        """
        steps = [
            ("Validate configuration", self._validate_config),
            ("Check dependencies", self._check_dependencies),
            ("Analyze codebase", self._analyze_code),
            ("Generate report", self._generate_report)
        ]
        
        results = {}
        
        for i, (step_name, step_func) in enumerate(steps, 1):
            yield_progress(i, len(steps), step_name)
            results[step_name] = step_func()
        
        return results
    
    def _validate_config(self) -> Dict:
        time.sleep(0.5)
        return {'valid': True}
    
    def _check_dependencies(self) -> Dict:
        time.sleep(0.5)
        return {'missing': []}
    
    def _analyze_code(self) -> Dict:
        time.sleep(0.5)
        return {'issues': 0}
    
    def _generate_report(self) -> Dict:
        time.sleep(0.5)
        return {'generated': True}


# ============================================================================
# EXAMPLE 6: Error Handling
# ============================================================================

@with_progress(operation_name="File Processing with Errors")
def process_with_error_handling(files: List[Path]) -> Dict[str, Any]:
    """
    Demonstrates error handling with progress monitoring.
    
    Monitor automatically reports failure if exception occurs.
    """
    processed = []
    errors = []
    
    for i, file in enumerate(files, 1):
        yield_progress(i, len(files), f"Processing {file.name}")
        
        try:
            # Simulate processing that might fail
            if i == 5:
                raise ValueError(f"Failed to process {file.name}")
            
            time.sleep(0.1)
            processed.append(file.name)
            
        except Exception as e:
            errors.append({'file': file.name, 'error': str(e)})
            # Continue processing other files
    
    if errors:
        # Will trigger monitor.fail() automatically
        raise RuntimeError(f"Processing failed: {len(errors)} errors")
    
    return {
        'processed': len(processed),
        'errors': len(errors)
    }


# ============================================================================
# USAGE DEMONSTRATION
# ============================================================================

def demo_all_examples():
    """Run all examples to demonstrate progress monitoring"""
    
    print("=" * 70)
    print("Progress Monitoring Examples")
    print("=" * 70)
    
    # Example 1: Simple file processing
    print("\n1. Simple File Processing (70 files, ~7s)")
    files = [Path(f"file_{i}.py") for i in range(70)]
    result = process_files(files)
    print(f"Result: {result}")
    
    # Example 2: Multi-phase
    print("\n2. Multi-Phase Operation (~5s)")
    result = align_system_multi_phase()
    print(f"Result: {result}")
    
    # Example 3: Database
    print("\n3. Database Migration (10 tables, ~2s)")
    tables = [f"table_{i}" for i in range(10)]
    result = migrate_database_tables(tables)
    print(f"Result: {result}")
    
    # Example 4: Fast operation
    print("\n4. Fast Operation (no progress shown)")
    items = ["item_1", "item_2", "item_3"]
    result = quick_validation(items)
    print(f"Result: {result}")
    
    # Example 5: Orchestrator
    print("\n5. Orchestrator Pattern (~2s)")
    orchestrator = ExampleOrchestrator()
    result = orchestrator.run_complete_check()
    print(f"Result: {len(result)} steps completed")
    
    print("\n" + "=" * 70)
    print("All examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    demo_all_examples()
