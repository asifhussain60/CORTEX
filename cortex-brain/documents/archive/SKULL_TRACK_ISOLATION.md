SKULL-009: Track Work Isolation

Core principle: Each track is an isolated development context.

Why Isolation Matters:

1. Prevents Merge Conflicts:
   - Two machines editing same file → disaster
   - Track A changes conflicting with Track B changes
   - Consolidation becomes manual merge nightmare
   Example: Both tracks fix same module differently

2. Maintains Race Integrity:
   - Track A can't "cheat" by doing Track B's work
   - Progress metrics stay meaningful
   - Velocity calculations remain accurate
   Example: Track A does Track B's modules → unfair race

3. Enables True Parallel Development:
   - No coordination needed during work
   - No "wait for Track A to finish" scenarios
   - Maximum throughput achieved
   Example: Both machines working simultaneously without blocking

4. Simplifies Context Management:
   - Each machine sees only relevant modules
   - Copilot context smaller and focused
   - Fewer tokens, faster responses
   Example: Track A context excludes Track B's 50 modules

Enforcement Mechanism:

1. Pre-Modification Check:
   ```python
   def validate_module_ownership(module_id, active_track):
       if module_id not in active_track.modules:
           raise TrackIsolationError(
               f"Module {module_id} belongs to different track"
           )
   ```

2. Git Pre-Commit Hook:
   ```bash
   # Check if modified files belong to active track
   active_track=$(get_active_track)
   for file in $(git diff --cached --name-only); do
       if ! track_owns_file "$active_track" "$file"; then
           echo "Error: $file not in active track"
           exit 1
       fi
   done
   ```

3. Design Sync Validation:
   - Compare git log with track assignments
   - Flag any cross-track modifications
   - Require explicit override with justification

Allowed Cross-Track Work:
- Shared files (cortex.config.json)
- Documentation updates (README.md)
- Test fixtures (tests/fixtures/)

Not Allowed:
- Modifying other track's modules
- Changing other track's phase files
- Updating other track's status in design doc

Override Process:
If cross-track work truly needed:
1. Document why isolation must break
2. Get explicit user approval
3. Log violation for consolidation review
4. Merge carefully during consolidation

Integration Test:
```python
def test_track_isolation():
    # Setup two tracks
    config = setup_multi_track(['AHHOME', 'Mac'])
    track_a = config.tracks['track_1']
    track_b = config.tracks['track_2']
    
    # Simulate Track A trying to modify Track B's module
    with pytest.raises(TrackIsolationError):
        modify_module(track_b.modules[0], active_track=track_a)
    
    # Verify Track A can modify own modules
    modify_module(track_a.modules[0], active_track=track_a)  # OK
```
