#!/usr/bin/env python3
"""Test PlexWorkflowOrchestrator on Wicked library."""

from pathlib import Path
from cortex.orchestrators.support.plex_workflow_orchestrator import (
    PlexWorkflowOrchestrator,
)

# Test workflow on Wicked library
orchestrator = PlexWorkflowOrchestrator(
    root=Path(r"G:\FLICKS\Wicked"),
    studio_filter="Wicked",
    dry_run=True,
    use_iafd=False,
)

result = orchestrator.run_full_workflow()
print(f"\n{'='*60}")
print(f"WORKFLOW RESULT")
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
if result.errors:
    print(f"\nErrors ({len(result.errors)}):")
    for err in result.errors:
        print(f"  - {err}")
if result.warnings:
    print(f"\nWarnings ({len(result.warnings)}):")
    for warn in result.warnings:
        print(f"  - {warn}")
print(f"{'='*60}")
