#!/usr/bin/env python3
"""Execute PlexWorkflowOrchestrator on Wicked library with production settings."""

from pathlib import Path
from cortex.orchestrators.support.plex_workflow_orchestrator import (
    PlexWorkflowOrchestrator,
)

# Production run: actually rename, tag, and organize files
orchestrator = PlexWorkflowOrchestrator(
    root=Path(r"G:\FLICKS\Wicked"),
    studio_filter="Wicked",
    dry_run=False,  # Actually modify files
    use_iafd=False,  # Start without IAFD (faster for first pass)
    min_rename_confidence=0.85,
    min_match_confidence=0.80,
)

result = orchestrator.run_full_workflow()
print(f"\n{'='*60}")
print(f"PRODUCTION WORKFLOW EXECUTION")
print(f"{'='*60}")
print(f"Success: {result.success}")
print(f"Total files: {result.total_files}")
print(f"Scanned: {result.files_scanned}")
print(f"Identified: {result.files_identified}")
print(f"Matched: {result.files_matched}")
print(f"Files renamed: {result.files_renamed}")
print(f"Files tagged: {result.files_tagged}")
print(f"Organized: {result.files_organized}")
print(f"Duration: {result.duration_seconds:.2f}s")

if result.step_results:
    print(f"\n{'='*60}")
    print(f"STEP DETAILS")
    print(f"{'='*60}")
    for step in result.step_results:
        status_icon = "[OK]" if step.status == "success" else "[FAIL]"
        print(f"{status_icon} {step.name}: {step.status} ({step.duration_ms:.1f}ms)")
        if step.details:
            for key, val in step.details.items():
                print(f"    {key}: {val}")

if result.errors:
    print(f"\nErrors ({len(result.errors)}):")
    for err in result.errors:
        print(f"  [ERROR] {err}")

if result.warnings:
    print(f"\nWarnings ({len(result.warnings)}):")
    for warn in result.warnings:
        print(f"  [WARN] {warn}")

print(f"{'='*60}")
