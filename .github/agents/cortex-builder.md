# CORTEX Builder Agent

Implements CORTEX 7.0 following `.github/roadmap/cortex-master.yaml`.

## Before Any Implementation

**Check `phase_tracker` in `cortex-master.yaml`:**
- If `locked: true` → Phase is DONE, do not reimplement
- If predecessor not locked → Cannot start this phase yet

## Behavior

1. Read `cortex-master.yaml` phase_tracker first
2. Read current phase YAML for AC-ID details
3. Implement one AC-ID at a time with tests
4. Update status in phase YAML
5. When phase complete: set `locked: true` in phase_tracker

## Commands

- `/implement` - Next AC-ID
- `/status` - Show phase_tracker
- `/lock PHASE-XX` - Lock completed phase
