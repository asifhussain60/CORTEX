#!/usr/bin/env python3
"""Run Plex workflow on Wicked library"""

from cortex.mcp.tools.video_library_tool import cortex_plex_workflow_full

print('=' * 100)
print('RUNNING PLEX WORKFLOW ON G:\FLICKS\Wicked')
print('=' * 100)
print()
print('Mode: DRY-RUN (preview mode, no modifications)')
print()

result = cortex_plex_workflow_full(
    root_path='G:\\FLICKS\\Wicked',
    studio_filter='Wicked',
    dry_run=True,
    use_iafd=False,
    min_match_confidence=0.75,
    min_rename_confidence=0.80,
    auto_organize=False
)

print('WORKFLOW RESULTS')
print('-' * 100)
print(f'Success: {result["success"]}')
print(f'Total files: {result["total_files"]}')
print(f'Scanned: {result["files_scanned"]}')
print(f'Identified: {result["files_identified"]}')
print(f'Renamed (proposed): {result["files_renamed"]}')
print(f'Tagged (proposed): {result["files_tagged"]}')
print(f'Duration: {result["duration_seconds"]:.2f} seconds')
print()

print('STEP RESULTS')
print('-' * 100)
for step in result['steps']:
    status_symbol = 'OK' if step['status'] == 'success' else 'FAIL'
    print(f'[{status_symbol}] {step["name"]}: {step["status"]} ({step["duration_ms"]:.1f}ms)')
    if step['error']:
        print(f'     Error: {step["error"]}')
    if step['details']:
        for key, val in step['details'].items():
            if key != 'results':
                print(f'     {key}: {val}')

if result['errors']:
    print()
    print('ERRORS')
    print('-' * 100)
    for err in result['errors']:
        print(f'  - {err}')

print()
print('=' * 100)
print('DRY-RUN COMPLETE - Ready for production execution')
print('=' * 100)
