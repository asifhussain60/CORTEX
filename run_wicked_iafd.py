#!/usr/bin/env python3
"""Execute PlexWorkflowOrchestrator with IAFD enrichment."""

from pathlib import Path
from cortex.orchestrators.support.plex_workflow_orchestrator import (
    PlexWorkflowOrchestrator,
)

# With IAFD enrichment
orchestrator = PlexWorkflowOrchestrator(
    root=Path(r"G:\FLICKS\Wicked"),
    studio_filter="Wicked",
    dry_run=True,  # Dry run to see what would happen
    use_iafd=True,  # Enable IAFD enrichment
    min_rename_confidence=0.85,
    min_match_confidence=0.70,
)

result = orchestrator.run_full_workflow()
print(f"\n{'='*60}")
print(f"WORKFLOW WITH IAFD ENRICHMENT")
print(f"{'='*60}")
print(f"Success: {result.success}")
print(f"Total files: {result.total_files}")
print(f"Scanned: {result.files_scanned}")
print(f"Identified: {result.files_identified}")
print(f"Matched IAFD: {result.files_matched}")
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
                if isinstance(val, dict):
                    print(f"    {key}:")
                    for k2, v2 in val.items():
                        print(f"      {k2}: {v2}")
                else:
                    print(f"    {key}: {val}")

if result.errors:
    print(f"\nErrors ({len(result.errors)}):")
    for err in result.errors[:5]:
        print(f"  [ERROR] {err}")

print(f"{'='*60}")
