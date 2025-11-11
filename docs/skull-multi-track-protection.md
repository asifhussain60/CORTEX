# CORTEX Multi-Track SKULL Protection Rules

**Version:** 1.0  
**Date:** 2025-11-11  
**Layer:** SKULL Protection (Layer 5)

---

## 🛡️ Overview

Three new SKULL rules added to protect multi-track development integrity:

- **SKULL-008:** Multi-Track Configuration Validation
- **SKULL-009:** Track Work Isolation
- **SKULL-010:** Track Consolidation Integrity

---

## 🔒 SKULL-008: Multi-Track Configuration Validation

**Severity:** BLOCKED

### Purpose
Validates multi-track configuration before allowing split mode activation.

### What It Checks

1. **Workload Balance**
   - Track estimated hours must not differ by >30%
   - Prevents one track finishing while other still has 80% remaining
   - Example: Track A (10h) vs Track B (40h) = BLOCKED

2. **Dependency Isolation**
   - Phase groups must be self-contained per track
   - No cross-track dependencies (Track A waiting on Track B)
   - Example: Both tracks have "setup" phase = BLOCKED (dependency violation)

3. **Machine Assignment**
   - Each machine assigned to exactly one track
   - No overlap, no unassigned machines
   - Example: AHHOME on both tracks = BLOCKED

4. **Track Name Uniqueness**
   - Generated names must be unique and deterministic
   - Same input always produces same name
   - Example: Hash collision → wrong track loaded = BLOCKED

### Detection Triggers

```yaml
keywords:
  - "enable multi-track"
  - "activate multi-track"
  - "create tracks"
  - "split tracks"
  - "multi-machine mode"
```

### Validation Requirements

```python
def validate_multi_track_config(config, modules):
    # 1. Balance check
    hours = [t.estimated_hours for t in config.tracks.values()]
    assert max(hours) / min(hours) < 1.3, "Imbalanced tracks (>30% difference)"
    
    # 2. Dependency check
    for track in config.tracks.values():
        deps = get_phase_dependencies(track.phases)
        assert all(d in track.phases for d in deps), "Cross-track dependency detected"
    
    # 3. Machine check
    all_machines = [m for t in config.tracks.values() for m in t.machines]
    assert len(all_machines) == len(set(all_machines)), "Duplicate machine assignment"
    
    # 4. Name check
    names = [t.track_name for t in config.tracks.values()]
    assert len(names) == len(set(names)), "Duplicate track name"
```

### Why It Matters

**Prevents:**
- Split-mode failures mid-development
- Unfair race metrics (unbalanced workload)
- Deadlocks (circular dependencies)
- Context confusion (machine on multiple tracks)

**Example Violation:**

```
🛡️ BLOCKED: Multi-Track Configuration Validation Failed

Track Balance Check:
- Track A (Blazing Phoenix): 12.5 hours
- Track B (Swift Falcon): 42.0 hours
- Imbalance: 336% (exceeds 30% threshold)

SKULL-008: Tracks must be balanced within 30% for fair distribution
```

---

## 🚧 SKULL-009: Track Work Isolation

**Severity:** BLOCKED

### Purpose
Ensures work on Track A never modifies Track B's assigned modules.

### What It Checks

1. **Module Ownership**
   - All modified files must belong to active track's module list
   - No cross-track modifications allowed
   - Example: Track A editing Track B's module = BLOCKED

2. **Phase Boundary**
   - Work must stay within assigned phases
   - Can't work on other track's phases
   - Example: Track A working on Track B's "PROCESSING" phase = BLOCKED

3. **Git Diff Validation**
   - `git diff` must only show files from active track
   - Pre-commit hook enforces this
   - Example: Track A commit includes Track B files = BLOCKED

### Detection Triggers

```yaml
combined_keywords:
  track_context:
    - "continue implementation for"
    - "working on track"
    - "active track"
  cross_modification:
    - "modified module"
    - "updated file"
    - "changed"
```

### Enforcement Mechanism

**Pre-Modification Check:**
```python
def validate_module_ownership(module_id, active_track):
    if module_id not in active_track.modules:
        raise TrackIsolationError(
            f"Module '{module_id}' belongs to different track. "
            f"Active track: {active_track.track_name}"
        )
```

**Git Pre-Commit Hook:**
```bash
#!/bin/bash
# Installed in .git/hooks/pre-commit

active_track=$(python -c "from src.operations.modules.design_sync import get_active_track; print(get_active_track())")

for file in $(git diff --cached --name-only); do
    if ! python -c "from src.operations.modules.design_sync import track_owns_file; exit(0 if track_owns_file('$active_track', '$file') else 1)"; then
        echo "❌ Error: $file not in active track '$active_track'"
        echo "   Switch to correct track or remove file from commit"
        exit 1
    fi
done
```

### Why It Matters

**Prevents:**
1. Merge conflicts (two machines editing same file)
2. Race metric cheating (Track A doing Track B's work)
3. Context pollution (Track A seeing Track B's 50 modules)
4. Consolidation nightmares (conflicting changes)

**Enables:**
- True parallel development (zero coordination)
- Focused context (smaller token count)
- Fair race metrics (accurate velocity)
- Clean consolidation (no conflicts)

### Allowed Exceptions

Cross-track work permitted for:
- Shared config files (`cortex.config.json`)
- Root documentation (`README.md`)
- Test fixtures (`tests/fixtures/`)

### Example Violation

```
🛡️ BLOCKED: Track Isolation Violation

Active Track: 🔥 Blazing Phoenix
Modified Files:
  ❌ src/operations/modules/apply_narrator_voice_module.py
  ❌ src/operations/modules/validate_story_structure_module.py

These files belong to: ⚡ Swift Falcon

SKULL-009: Tracks must not cross-modify each other's work

Options:
  1. Switch to Swift Falcon track: /CORTEX continue implementation for swift-falcon
  2. Revert changes to these files
  3. Request track reassignment (requires justification)
```

---

## ✅ SKULL-010: Track Consolidation Integrity

**Severity:** BLOCKED

### Purpose
Ensures consolidation merges all track progress accurately without data loss.

### What It Checks

1. **Progress Preservation**
   - Consolidated count must equal sum of track counts
   - No completed modules lost in merge
   - Example: 8 + 12 = 20, but consolidated shows 19 = BLOCKED

2. **Conflict Resolution Audit**
   - All conflicts must be logged with justification
   - Archive must contain resolution details
   - Example: Module conflict resolved but not logged = BLOCKED

3. **Archive Completeness**
   - Split docs must be archived before deletion
   - All track history preserved
   - Example: Split doc deleted, archive empty = BLOCKED

4. **Git Commit Validation**
   - Consolidation must be tracked in git history
   - Commit message must reference both tracks
   - Example: Merge happened, git log silent = BLOCKED

### Detection Triggers

```yaml
keywords:
  - "consolidate tracks"
  - "merge tracks"
  - "reset to single-track"
  - "design sync consolidation"
```

### Consolidation Algorithm

```python
def consolidate_tracks(track_config, impl_state):
    # Step 1: Collect all track progress
    all_modules = {}
    conflicts = []
    
    for track in track_config.tracks.values():
        for module_id in track.modules:
            status = get_module_status(module_id, impl_state)
            
            if module_id in all_modules:
                # Conflict detected
                conflict = {
                    'module_id': module_id,
                    'track_a': all_modules[module_id],
                    'track_b': status,
                    'resolution': 'latest_timestamp',
                    'winner': status if status.timestamp > all_modules[module_id].timestamp else all_modules[module_id]
                }
                conflicts.append(conflict)
                all_modules[module_id] = conflict['winner']
            else:
                all_modules[module_id] = status
    
    # Step 2: Validate counts
    pre_count = sum(t.metrics.modules_completed for t in track_config.tracks.values())
    post_count = sum(1 for s in all_modules.values() if s.completed)
    
    if pre_count != post_count:
        raise ConsolidationError(
            f"Progress mismatch! Pre: {pre_count}, Post: {post_count}"
        )
    
    # Step 3: Archive split docs
    archive_dir = create_archive_directory()
    for status_file in get_split_design_docs():
        archive_file(status_file, archive_dir)
        log_archive(status_file, archive_dir)
    
    # Step 4: Log conflicts
    if conflicts:
        conflict_log = archive_dir / 'conflicts-resolved.yaml'
        conflict_log.write_text(yaml.dump(conflicts))
    
    # Step 5: Generate consolidated doc
    consolidated = generate_consolidated_document(
        all_modules,
        track_config,
        archive_reference=archive_dir
    )
    
    # Step 6: Git commit with full details
    commit_message = f"""design: consolidate multi-track progress

Tracks merged:
- {track_config.tracks['track_1'].track_name}: {track_config.tracks['track_1'].metrics.completion_percentage}%
- {track_config.tracks['track_2'].track_name}: {track_config.tracks['track_2'].metrics.completion_percentage}%

Total progress: {post_count}/{len(all_modules)} modules ({post_count/len(all_modules)*100:.0f}%)
Conflicts resolved: {len(conflicts)}
Archive: {archive_dir.name}

[design_sync consolidation]
"""
    
    git_commit(consolidated, commit_message)
    
    return consolidated
```

### Conflict Resolution Strategy

**Default:** Latest Timestamp Wins

- Simple, deterministic, predictable
- Assumes most recent work is correct
- All conflicts logged for audit

**Example:**
```yaml
# conflicts-resolved.yaml
- module_id: platform_detection
  track_a:
    name: Blazing Phoenix
    timestamp: 2025-11-11 14:00:00
    status: completed
  track_b:
    name: Swift Falcon
    timestamp: 2025-11-11 15:00:00
    status: completed
  resolution: latest_timestamp
  winner: track_b
  reason: Swift Falcon completed later (15:00 > 14:00)
```

### Archive Structure

```
cortex-brain/archived-tracks/20251111-164530/
├── CORTEX2-STATUS-SPLIT.MD       # Original split doc
├── track-1-history.jsonl         # Blazing Phoenix progress log
├── track-2-history.jsonl         # Swift Falcon progress log
├── conflicts-resolved.yaml       # Conflict resolution log (if any)
└── consolidation-report.md       # Summary of merge
```

### Why It Matters

**Prevents:**
- Progress loss (modules disappearing)
- Conflict mishandling (wrong version kept)
- Archive failure (can't audit merge)
- Git history gaps (untraceable merge)

**Ensures:**
- 100% progress preservation
- Transparent conflict resolution
- Complete audit trail
- Rollback capability

### Example Violation

```
🛡️ BLOCKED: Consolidation Integrity Check Failed

Pre-Consolidation:
- Track A (Blazing Phoenix): 8/15 modules (53%)
- Track B (Swift Falcon): 12/18 modules (67%)
- Total Expected: 20 modules

Post-Consolidation:
- Unified: 19 modules

❌ Discrepancy: 1 module lost in merge!

Missing Module: apply_narrator_voice_module
Last Seen: Track B @ 2025-11-11 15:30

SKULL-010: Consolidation must preserve all progress

Actions:
  1. Review consolidation logic for data loss bug
  2. Restore missing module from Track B history
  3. Re-run consolidation with verification
  4. Add integration test for this scenario
```

---

## 🧪 Integration Tests Required

### SKULL-008: Configuration Validation

```python
def test_skull_008_track_balance():
    """Verify SKULL-008 blocks imbalanced track distribution."""
    # Create imbalanced config (70% difference)
    config = MultiTrackConfig(
        mode='multi',
        tracks={
            'track_1': MachineTrack(estimated_hours=10.0),
            'track_2': MachineTrack(estimated_hours=40.0)
        }
    )
    
    # Should be blocked by SKULL-008
    with pytest.raises(SkullProtectionError) as exc:
        validate_multi_track_config(config)
    
    assert "SKULL-008" in str(exc.value)
    assert "Imbalanced tracks" in str(exc.value)

def test_skull_008_dependency_isolation():
    """Verify SKULL-008 blocks cross-track dependencies."""
    # Create config with cross-dependency
    config = create_config_with_dependency(
        track_1_phases=['ENVIRONMENT'],
        track_2_phases=['DEPENDENCIES']  # Depends on ENVIRONMENT
    )
    
    with pytest.raises(SkullProtectionError) as exc:
        validate_multi_track_config(config)
    
    assert "SKULL-008" in str(exc.value)
    assert "Cross-track dependency" in str(exc.value)
```

### SKULL-009: Track Isolation

```python
def test_skull_009_module_ownership():
    """Verify SKULL-009 blocks cross-track modifications."""
    config = create_multi_track(['AHHOME', 'Mac'])
    track_a = config.tracks['track_1']
    track_b = config.tracks['track_2']
    
    # Track A trying to modify Track B's module
    with pytest.raises(TrackIsolationError) as exc:
        modify_module(track_b.modules[0], active_track=track_a)
    
    assert "SKULL-009" in str(exc.value)
    assert "belongs to different track" in str(exc.value)

def test_skull_009_git_pre_commit_hook():
    """Verify git hook blocks cross-track commits."""
    config = create_multi_track(['AHHOME', 'Mac'])
    set_active_track(config.tracks['track_1'])
    
    # Stage Track B's file
    track_b_file = config.tracks['track_2'].modules[0]
    git_add(track_b_file)
    
    # Pre-commit hook should block
    result = run_git_commit("Test commit")
    assert result.returncode != 0
    assert "SKULL-009" in result.stderr
```

### SKULL-010: Consolidation Integrity

```python
def test_skull_010_progress_preservation():
    """Verify SKULL-010 detects progress loss."""
    config = create_multi_track_with_progress(
        track_1_completed=8,
        track_2_completed=12
    )
    
    # Mock consolidation that loses 1 module
    with mock.patch('consolidate', return_value={'completed': 19}):
        with pytest.raises(ConsolidationError) as exc:
            consolidate_tracks(config, impl_state)
        
        assert "SKULL-010" in str(exc.value)
        assert "Progress mismatch" in str(exc.value)
        assert "20" in str(exc.value)  # Expected
        assert "19" in str(exc.value)  # Actual

def test_skull_010_conflict_logging():
    """Verify SKULL-010 requires conflict logging."""
    config = create_multi_track_with_conflict(
        module='platform_detection',
        track_1_timestamp='14:00',
        track_2_timestamp='15:00'
    )
    
    result = consolidate_tracks(config, impl_state)
    
    # Verify conflict logged
    archive = get_latest_archive()
    conflicts = yaml.safe_load((archive / 'conflicts-resolved.yaml').read_text())
    
    assert len(conflicts) == 1
    assert conflicts[0]['module_id'] == 'platform_detection'
    assert conflicts[0]['winner'] == 'track_2'  # Latest timestamp
```

---

## 📋 Summary

**SKULL-008: Configuration Validation**
- Validates before split
- Ensures fair workload, no dependencies
- BLOCKS bad configs

**SKULL-009: Track Isolation**
- Enforces during work
- Prevents cross-track modifications
- BLOCKS boundary violations

**SKULL-010: Consolidation Integrity**
- Validates during merge
- Preserves all progress, logs conflicts
- BLOCKS incomplete merges

**Together:** These rules ensure multi-track development is reliable, fair, and safe.

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary

*Built for CORTEX 2.0 - Multi-Track Development System*
