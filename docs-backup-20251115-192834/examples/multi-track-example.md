# Example Multi-Track Configuration

This shows what gets added to `cortex.config.json` when you run:

```bash
python scripts/cortex/setup_multi_track.py --machines AHHOME "Asifs-MacBook-Pro.local"
```

## Generated Configuration

```json
{
  "design_tracks": {
    "mode": "multi",
    "tracks": {
      "track_1": {
        "name": "Blazing Phoenix",
        "emoji": "🔥",
        "color": "Red",
        "machines": ["AHHOME"],
        "phases": [
          "PREPARATION",
          "PRE_VALIDATION",
          "ENVIRONMENT"
        ],
        "modules": [
          "load_story_template",
          "project_validation",
          "platform_detection",
          "git_sync"
        ],
        "estimated_hours": 18.5,
        "velocity_target": 4.0
      },
      "track_2": {
        "name": "Swift Falcon",
        "emoji": "⚡",
        "color": "Blue",
        "machines": ["Asifs-MacBook-Pro.local"],
        "phases": [
          "DEPENDENCIES",
          "FEATURES",
          "PROCESSING"
        ],
        "modules": [
          "python_dependencies",
          "vision_api",
          "apply_narrator_voice",
          "brain_initialization"
        ],
        "estimated_hours": 21.0,
        "velocity_target": 4.5
      }
    },
    "race_metrics": {
      "enabled": true,
      "display_leaderboard": true,
      "velocity_window_hours": 24
    }
  }
}
```

## Example Split Design Document

### File: `cortex-brain/cortex-2.0-design/CORTEX2-STATUS-SPLIT.MD`

```markdown
# CORTEX 2.0 Implementation - Multi-Track Race

## 🏁 Race Dashboard (Live)
| Track | Machine | Progress | Velocity | Status | ETA |
|-------|---------|----------|----------|--------|-----|
| 🔥 Blazing Phoenix | AHHOME | 2/4 (50%) | 4.2 mod/day | 🚀 | Nov 12 |
| ⚡ Swift Falcon | Mac | 3/4 (75%) | 5.1 mod/day | 🔥 | Nov 12 |

**🏆 Current Leader:** ⚡ Swift Falcon (+1 module)

---

## 🔥 Blazing Phoenix Track (AHHOME)
**Assigned Phases:** PREPARATION, PRE_VALIDATION, ENVIRONMENT  
**Estimated Hours:** 18.5h  
**Target Velocity:** 4.0 modules/day

### PREPARATION Phase (Status: IN PROGRESS (50%))

- [x] load_story_template
- [ ] scan_docstrings

### PRE_VALIDATION Phase (Status: NOT STARTED)

- [ ] project_validation

### ENVIRONMENT Phase (Status: IN PROGRESS (50%))

- [x] platform_detection
- [ ] git_sync

---

## ⚡ Swift Falcon Track (Mac)
**Assigned Phases:** DEPENDENCIES, FEATURES, PROCESSING  
**Estimated Hours:** 21.0h  
**Target Velocity:** 4.5 modules/day

### DEPENDENCIES Phase (Status: COMPLETED ✅)

- [x] python_dependencies

### FEATURES Phase (Status: COMPLETED ✅)

- [x] vision_api

### PROCESSING Phase (Status: IN PROGRESS (50%))

- [x] apply_narrator_voice
- [ ] brain_initialization

---

*Last Updated: 2025-11-11 14:30*  
*CORTEX Version: 2.0*  
*Mode: Multi-Track (2 tracks active)*
```

## Example Consolidated Document

### File: `cortex-brain/cortex-2.0-design/CORTEX2-STATUS.MD`

```markdown
# CORTEX 2.0 Implementation - Unified Status

*Last Synchronized: 2025-11-11 16:45 (design_sync)*  
*Merged Tracks: Blazing Phoenix (50%), Swift Falcon (75%)*

## Overall Progress
**Total Modules:** 8  
**Implemented:** 5 (63%)

---

### PREPARATION Phase (COMPLETED ✅)
- [x] load_story_template

### PRE_VALIDATION Phase (NOT STARTED)
- [ ] project_validation

### ENVIRONMENT Phase (IN PROGRESS (50%))
- [x] platform_detection
- [ ] git_sync

### DEPENDENCIES Phase (COMPLETED ✅)
- [x] python_dependencies

### FEATURES Phase (COMPLETED ✅)
- [x] vision_api

### PROCESSING Phase (IN PROGRESS (50%))
- [x] apply_narrator_voice
- [ ] brain_initialization

---

## Track Archive
*Previous multi-track configuration archived to `cortex-brain/archived-tracks/20251111-164530/`*  
*Tracks merged: 🔥 Blazing Phoenix, ⚡ Swift Falcon*

*CORTEX Version: 2.0*  
*Mode: Single-Track (consolidated from 2 tracks)*
```

## Usage Examples

### On Windows Machine (AHHOME)

```bash
# 1. Check what track I'm on
python scripts/cortex/setup_multi_track.py --show

# Output:
#    🔥 Blazing Phoenix
#       Machine: AHHOME
#       Progress: 2/4 (50%)
#       Velocity: 4.2 modules/day
#       Status: 🚀

# 2. Continue working on my track
/CORTEX continue implementation for blazing-phoenix

# 3. Sync my progress
/CORTEX design sync
```

### On Mac Machine

```bash
# 1. Check what track I'm on
python scripts/cortex/setup_multi_track.py --show

# Output:
#    ⚡ Swift Falcon
#       Machine: Mac
#       Progress: 3/4 (75%)
#       Velocity: 5.1 modules/day
#       Status: 🔥

# 2. Continue working on my track
/CORTEX continue implementation for swift-falcon

# 3. Sync my progress
/CORTEX design sync
```

### Consolidation (Any Machine)

```bash
# When both tracks near completion, consolidate
/CORTEX design sync

# Output:
# 🏁 Multi-Track Mode: Running design sync consolidation
#    Will merge all tracks into unified status
#
# [Phase 1/6] Discovering live implementation state...
# ✅ Discovered: 8 modules, 5 implemented (63%)
#
# [Phase 5/6] Transforming documents...
# ✅ Consolidated 2 tracks into unified document
#
# [Phase 6/6] Committing changes and generating report...
# ✅ Committed changes: 7a3b9c2
#
# Design Sync ✅ COMPLETED in 3.2s
#    • Discovered 8 modules (63% implemented)
#    • Consolidated 2 status files → 1 source of truth
#    • Merged 2 tracks: Blazing Phoenix (50%) + Swift Falcon (75%)
#    • Committed changes: 7a3b9c2
```

---

**Note:** All examples show actual output format from the implemented system.
