SKULL-008: Multi-Track Configuration Validation

Multi-track mode is powerful but requires careful setup:

1. Workload Balance:
   - Tracks with vastly different hours → bottlenecks
   - One machine idle while other overloaded
   - Race metrics meaningless if unfair
   Example: Track A (10h) vs Track B (40h) = broken

2. Dependency Isolation:
   - Track A waiting on Track B output → blocked
   - Cross-dependencies defeat parallel development
   - Must group dependent phases on same track
   Example: "setup" phases must complete before "processing"

3. Machine Assignment:
   - Machine assigned to multiple tracks → confusion
   - Unassigned machines → wasted capacity
   - Clear 1:1 or 1:N mapping required
   Example: AHHOME on both tracks = which context?

4. Track Name Uniqueness:
   - Collision-resistant generation
   - Deterministic (same input → same name)
   - Human-memorable for commands
   Example: Hash collision → wrong track loaded

Why This Matters:
- Prevents split-mode failures mid-development
- Ensures race metrics are meaningful
- Maintains track isolation guarantees
- Makes "continue implementation for [track]" reliable

Validation Points:

Pre-Initialization:
- Check machine count > 0
- Verify operations.yaml accessible
- Validate module definitions exist

Post-Distribution:
- Balance check: max_hours/min_hours < 1.3 (30% tolerance)
- Dependency check: No phase in track requires other track's output
- Machine check: Each machine in exactly one track
- Name check: All track names unique and deterministic

Integration Test Required:
```python
def test_multi_track_validation():
    # Setup
    machines = ["AHHOME", "Mac"]
    config = create_multi_track_config(machines, modules)
    
    # Balance check
    hours = [t.estimated_hours for t in config.tracks.values()]
    assert max(hours) / min(hours) < 1.3, "Imbalanced tracks"
    
    # Dependency check
    for track in config.tracks.values():
        deps = get_phase_dependencies(track.phases)
        assert all(d in track.phases for d in deps), "Cross-track dep"
    
    # Machine check
    all_machines = [m for t in config.tracks.values() for m in t.machines]
    assert len(all_machines) == len(set(all_machines)), "Duplicate machine"
    
    # Name check
    names = [t.track_name for t in config.tracks.values()]
    assert len(names) == len(set(names)), "Duplicate track name"
```

Enforcement:
- CLI script validates before writing config
- Design sync validates before split
- Continue command validates track exists
- Consolidation validates all tracks present
