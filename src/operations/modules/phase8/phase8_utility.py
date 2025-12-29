"""
Phase 8 Operations Utility

Lightweight Phase 8 operations for final integration and cleanup.

Core Operations:
- handle_integration_cleanup: Final cleanup before deployment
- handle_completion_report: Generate Phase 8 completion report
- handle_phase8_status: Show Phase 8 progress
- calculate_cleanup_metrics: File size and category analysis
- generate_completion_report: Report content generation

Version: 3.0.0 (Migrated from Phase8OperationHandler)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime


def calculate_cleanup_metrics(files: List[Path]) -> Dict[str, Any]:
    """
    Calculate cleanup metrics for files
    
    Args:
        files: List of files to analyze
        
    Returns:
        Dict with size, count, categories
        
    Example:
        >>> metrics = calculate_cleanup_metrics([Path("test.log")])
        >>> print(metrics["total_files"])
        1
    """
    total_size = 0
    categories = {'cache': 0, 'backup': 0, 'temp': 0, 'logs': 0, 'other': 0}
    
    for file in files:
        try:
            size = file.stat().st_size
            total_size += size
            
            # Categorize
            file_str = str(file)
            if 'cache' in file_str:
                categories['cache'] += 1
            elif 'backup' in file_str:
                categories['backup'] += 1
            elif 'temp' in file_str or file.suffix == '.tmp':
                categories['temp'] += 1
            elif 'log' in file_str or file.suffix == '.log':
                categories['logs'] += 1
            else:
                categories['other'] += 1
        except OSError:
            pass
    
    # Convert to readable format
    if total_size > 1024 * 1024:
        size_str = f"{total_size / (1024 * 1024):.1f} MB"
    elif total_size > 1024:
        size_str = f"{total_size / 1024:.1f} KB"
    else:
        size_str = f"{total_size} bytes"
    
    return {
        'total_files': len(files),
        'total_size': total_size,
        'size_str': size_str,
        'categories': categories
    }


def generate_completion_report() -> str:
    """
    Generate Phase 8 completion report content
    
    Returns:
        Markdown formatted report
        
    Example:
        >>> report = generate_completion_report()
        >>> print("Phase 8" in report)
        True
    """
    return f"""# Phase 8: Final Integration & Cleanup - Completion Report

**Author:** Asif Hussain
**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Status:** In Progress

## Deliverables Status

- [x] 8.1.1 RED - CLI help test
- [x] 8.1.1 GREEN - Implement CLI help
- [x] 8.1.1 REFACTOR - Clean CLI code
- [ ] 8.1.2 RED - Integration cleanup test
- [ ] 8.1.2 GREEN - Basic cleanup orchestrator
- [ ] 8.1.2 REFACTOR - Cleanup orchestrator polish
- [ ] 8.2 RED - Final cleanup validation
- [ ] 8.2 GREEN - Cleanup implementation
- [ ] 8.3 RED - Report generation test
- [ ] 8.3 GREEN - Report generator
- [ ] 8.4 RED - End-to-end integration test
- [ ] 8.4 GREEN - Full integration
- [ ] Phase 8 COMPLETE - Documentation & validation

## Test Coverage

**Phase 8.1 Tests:** 8/8 passing (100%)
**Total CORTEX Tests:** 318+ passing

## Implementation Notes

### 8.1.1 CLI Integration (Complete)
- Added Phase 8 operations to help text
- Implemented CLI argument parsing
- Created Phase8OperationHandler
- All tests passing

### Cross-Platform Readiness
- LF enforcement via .gitattributes
- pathlib exclusively for paths
- No POSIX-only commands

## Git Checkpoints

- Phase 8.1.1 RED: Tests created
- Phase 8.1.1 GREEN: CLI implementation
- Phase 8.1.1 REFACTOR: Extracted handler

## Next Steps

1. Phase 8.1.2 RED - Write cleanup tests
2. Phase 8.1.2 GREEN - Implement cleanup
3. Phase 8.1.2 REFACTOR - Polish error handling

---

**Progress:** 23% (3/13 deliverables)
**Est. Remaining:** 37 hours
"""


def handle_integration_cleanup(
    brain_path: str,
    dry_run: bool = True,
    profile: str = "standard"
) -> Dict[str, Any]:
    """
    Handle integration cleanup operation
    
    Args:
        brain_path: Path to CORTEX brain directory
        dry_run: If True, no actual changes
        profile: Cleanup profile (quick/standard/comprehensive)
        
    Returns:
        Dict with cleanup results
        
    Example:
        >>> result = handle_integration_cleanup("/path/to/brain")
        >>> print(result["dry_run"])
        True
    """
    brain = Path(brain_path)
    
    if not brain.exists():
        return {
            "success": False,
            "error": "Brain path not found",
            "brain_path": str(brain)
        }
    
    # Detect files to clean (simplified for utility)
    files_to_clean = []
    
    # Look for cache files
    cache_dir = brain / "cache"
    if cache_dir.exists():
        files_to_clean.extend(list(cache_dir.glob("*.cache")))
    
    # Look for backup files
    backup_dir = brain / "backups"
    if backup_dir.exists():
        files_to_clean.extend(list(backup_dir.glob("*.bak")))
    
    # Calculate metrics
    metrics = calculate_cleanup_metrics(files_to_clean)
    
    # Perform cleanup if not dry run
    cleaned_files = []
    if not dry_run:
        for file in files_to_clean:
            try:
                if file.exists():
                    file.unlink()
                    cleaned_files.append(str(file))
            except Exception:
                pass
    
    return {
        "success": True,
        "dry_run": dry_run,
        "profile": profile,
        "files_detected": len(files_to_clean),
        "files_cleaned": len(cleaned_files),
        "metrics": metrics
    }


def handle_completion_report(
    brain_path: str,
    output_path: str = None
) -> Dict[str, Any]:
    """
    Handle completion report generation
    
    Args:
        brain_path: Path to CORTEX brain
        output_path: Optional custom output path
        
    Returns:
        Dict with report path and success status
        
    Example:
        >>> result = handle_completion_report("/path/to/brain")
        >>> print(result["success"])
        True
    """
    brain = Path(brain_path)
    
    if not brain.exists():
        return {
            "success": False,
            "error": "Brain path not found"
        }
    
    # Resolve output path
    if output_path:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
    else:
        reports_dir = brain / "documents" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        output = reports_dir / "PHASE-8-COMPLETION-REPORT.md"
    
    # Generate report
    report_content = generate_completion_report()
    
    # Write report
    try:
        output.write_text(report_content, encoding='utf-8')
        return {
            "success": True,
            "report_path": str(output)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def handle_phase8_status() -> Dict[str, Any]:
    """
    Handle Phase 8 status query
    
    Returns:
        Dict with progress information
        
    Example:
        >>> status = handle_phase8_status()
        >>> print(status["total_deliverables"])
        13
    """
    total_deliverables = 13
    completed_deliverables = 3  # 8.1.1 complete
    progress_percent = int((completed_deliverables / total_deliverables) * 100)
    remaining = total_deliverables - completed_deliverables
    estimated_hours = remaining * 3.5
    
    return {
        "total_deliverables": total_deliverables,
        "completed_deliverables": completed_deliverables,
        "progress_percent": progress_percent,
        "remaining_deliverables": remaining,
        "estimated_hours": estimated_hours
    }


# CLI for testing
if __name__ == "__main__":
    import time
    import tempfile
    
    print("🧪 Testing Phase 8 Operations Utility...")
    start_test = time.time()
    
    # Create temp brain directory
    with tempfile.TemporaryDirectory() as temp_dir:
        brain_path = Path(temp_dir) / "cortex-brain"
        brain_path.mkdir()
        
        # Create test files
        cache_dir = brain_path / "cache"
        cache_dir.mkdir()
        (cache_dir / "test.cache").write_text("test")
        
        # Test 1: Calculate metrics
        print("Testing metrics calculation...")
        test_files = list(cache_dir.glob("*.cache"))
        metrics = calculate_cleanup_metrics(test_files)
        assert metrics["total_files"] == 1, "Should find 1 file"
        print(f"✅ Metrics: {metrics['total_files']} files, {metrics['size_str']}")
        
        # Test 2: Integration cleanup (dry run)
        print("Testing integration cleanup...")
        result = handle_integration_cleanup(str(brain_path), dry_run=True)
        assert result["success"], "Should succeed"
        assert result["dry_run"], "Should be dry run"
        print(f"✅ Cleanup (dry run): {result['files_detected']} files detected")
        
        # Test 3: Completion report
        print("Testing completion report...")
        result = handle_completion_report(str(brain_path))
        assert result["success"], "Should succeed"
        assert Path(result["report_path"]).exists(), "Report should exist"
        print(f"✅ Report: {result['report_path']}")
        
        # Test 4: Phase8 status
        print("Testing Phase 8 status...")
        status = handle_phase8_status()
        assert status["total_deliverables"] == 13, "Should have 13 deliverables"
        print(f"✅ Status: {status['progress_percent']}% complete")
    
    elapsed = time.time() - start_test
    print(f"\n⚡ All tests passed in {elapsed:.3f}s")
    print(f"📊 Operations: 5 core functions tested")
