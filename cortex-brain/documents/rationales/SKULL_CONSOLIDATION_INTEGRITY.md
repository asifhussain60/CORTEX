SKULL-010: Track Consolidation Integrity

Consolidation is the critical merge operation - must be perfect.

What Can Go Wrong:

1. Progress Loss:
   - Track A shows module complete
   - Consolidation misses it
   - User loses work (demoralizing)
   Example: Track A completed 15 modules, only 12 appear in merge

2. Conflict Mishandling:
   - Both tracks modified same module
   - Wrong version selected
   - Work overwritten silently
   Example: Track A's fix lost, Track B's bug remains

3. Archive Failure:
   - Split docs deleted before archiving
   - No way to audit merge decisions
   - Can't roll back if issues found
   Example: User wants to see what Track A had, archive empty

4. Git History Gaps:
   - Consolidation not committed properly
   - Can't trace what was merged when
   - Audit trail incomplete
   Example: Merge happened, git log says nothing

Consolidation Algorithm:

```python
def consolidate_tracks(track_config, impl_state):
    # Step 1: Collect all track progress
    all_modules = {}
    for track in track_config.tracks.values():
        for module_id in track.modules:
            status = get_module_status(module_id, impl_state)
            
            # Conflict detection
            if module_id in all_modules:
                conflict = resolve_conflict(
                    all_modules[module_id],
                    status,
                    strategy='latest_timestamp'
                )
                log_conflict_resolution(module_id, conflict)
                all_modules[module_id] = conflict.winner
            else:
                all_modules[module_id] = status
    
    # Step 2: Validate counts
    pre_count = sum(t.metrics.modules_completed for t in track_config.tracks.values())
    post_count = sum(1 for s in all_modules.values() if s.completed)
    
    if pre_count != post_count:
        raise ConsolidationError(
            f"Progress mismatch: {pre_count} → {post_count}"
        )
    
    # Step 3: Archive split docs
    archive_dir = create_archive_directory()
    for status_file in get_split_design_docs():
        archive_file(status_file, archive_dir)
    
    # Step 4: Generate consolidated doc
    consolidated = generate_consolidated_document(
        all_modules,
        track_config,
        archive_reference=archive_dir
    )
    
    # Step 5: Git commit with full details
    commit_message = f"""design: consolidate multi-track progress
    
    Tracks merged:
    - {track_config.tracks['track_1'].track_name}: {track_config.tracks['track_1'].metrics.completion_percentage}%
    - {track_config.tracks['track_2'].track_name}: {track_config.tracks['track_2'].metrics.completion_percentage}%
    
    Total progress: {post_count}/{len(all_modules)} modules ({post_count/len(all_modules)*100:.0f}%)
    Conflicts resolved: {len(get_conflicts())}
    Archive: {archive_dir.name}
    
    [design_sync consolidation]
    """
    
    git_commit(consolidated, commit_message)
    
    return consolidated
```

Conflict Resolution Strategy:

Default: Latest Timestamp Wins
- Simple, deterministic, predictable
- Assumes most recent work is correct
- Logged for audit

Example:
```
Module: platform_detection
- Track A: marked complete 2025-11-11 14:00
- Track B: marked complete 2025-11-11 15:00
Winner: Track B (later timestamp)
Logged: conflict-resolution.yaml
```

Archive Structure:
```
cortex-brain/archived-tracks/20251111-164530/
├── CORTEX2-STATUS-SPLIT.MD       # Original split doc
├── track-1-history.jsonl         # Track A progress log
├── track-2-history.jsonl         # Track B progress log
├── conflicts-resolved.yaml       # Conflict resolution log
└── consolidation-report.md       # Summary of merge
```

Integration Test:
```python
def test_consolidation_integrity():
    # Setup: Two tracks with overlapping work
    config = create_multi_track(['AHHOME', 'Mac'])
    track_a_complete = mark_modules_complete(config.tracks['track_1'], [0, 1, 2])
    track_b_complete = mark_modules_complete(config.tracks['track_2'], [3, 4, 5])
    
    # Introduce conflict: both complete module 2
    mark_complete(config.tracks['track_1'], 'module_2', timestamp='14:00')
    mark_complete(config.tracks['track_2'], 'module_2', timestamp='15:00')
    
    # Consolidate
    consolidated = consolidate_tracks(config, impl_state)
    
    # Verify counts
    assert consolidated.modules_completed == 6, "Progress lost"
    
    # Verify conflict handled
    conflicts = get_conflict_log()
    assert 'module_2' in conflicts, "Conflict not logged"
    assert conflicts['module_2']['winner'] == 'track_2', "Wrong winner"
    
    # Verify archive
    archive = get_latest_archive()
    assert archive.exists(), "Archive missing"
    assert (archive / 'CORTEX2-STATUS-SPLIT.MD').exists(), "Split doc not archived"
    
    # Verify git
    commit = get_latest_commit()
    assert 'consolidate multi-track' in commit.message
    assert 'track_1' in commit.message
    assert 'track_2' in commit.message
```

User Experience:
```
$ /CORTEX design sync

🏁 Multi-Track Mode: Running design sync consolidation
   Will merge all tracks into unified status

[Phase 1/6] Discovering live implementation state...
✅ Track A (Blazing Phoenix): 8/15 modules (53%)
✅ Track B (Swift Falcon): 12/18 modules (67%)

[Phase 5/6] Consolidating tracks...
⚙️  Merging progress from 2 tracks...
⚠️  Conflict detected: platform_detection
    Track A: complete @ 14:00
    Track B: complete @ 15:00
    Resolution: Track B wins (latest timestamp)

✅ Consolidated 2 tracks into unified document
   Combined: 20/33 modules (61%)
   Conflicts resolved: 1 (logged)
   Archive: cortex-brain/archived-tracks/20251111-164530/

[Phase 6/6] Committing changes...
💾 Git commit: 7a3b9c2 "design: consolidate multi-track progress"

Design Sync ✅ COMPLETED in 4.2s
   • Merged 2 tracks: Blazing Phoenix (53%) + Swift Falcon (67%)
   • Combined progress: 20/33 modules (61%)
   • Conflicts resolved: 1
   • Archived split docs
   • Reset to single-track mode
```
