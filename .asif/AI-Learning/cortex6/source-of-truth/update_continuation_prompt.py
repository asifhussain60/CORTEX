#!/usr/bin/env python3
"""
Auto-update CONTINUATION-PROMPT.md from tracker state.

This script reads the TODO tracker and updates the continuation prompt
to keep it in sync with the current execution position.

Author: Asif Hussain
Version: 1.0.0
Created: 2026-01-07
"""

import yaml
from pathlib import Path
from datetime import datetime


def update_continuation_prompt():
    """Update CONTINUATION-PROMPT.md with current tracker state."""
    
    base_dir = Path(__file__).parent
    tracker_path = base_dir / "todo" / "00-TODO-CONTINUITY-TRACKER.yaml"
    prompt_path = base_dir / "CONTINUATION-PROMPT.md"
    
    # Load tracker
    with open(tracker_path) as f:
        tracker = yaml.safe_load(f)
    
    current_pos = tracker["current_position"]
    
    # Extract info
    feature = current_pos["feature"]
    phase = current_pos["phase"]
    task = current_pos["task"]
    completed = current_pos["completed_count"]
    last_completed = current_pos.get("last_completed", "N/A")
    
    # Generate prompt content
    content = f"""# CORTEX 6.0 Build - Session Continuation

**Current Position:** {feature}, Phase {phase}, {task}  
**Completed:** {completed} tasks | **Status:** ✅ On track | **Last:** {last_completed}

---

## 🚀 Quick Start

1. **Load State:** Read `.asif/AI-Learning/cortex6/source-of-truth/todo/00-TODO-CONTINUITY-TRACKER.yaml`
2. **Find Position:** Check `current_position` section
3. **Load Feature:** Read `features/{feature}/feature.yaml`
4. **Execute Task:** Follow task instructions
5. **Update Tracker:** Mark COMPLETED, update current_position
6. **Update This File:** Run `python3 update_continuation_prompt.py`

---

## 🛡️ Self-Healing Protocol

**Before Each Task:**
- Review audit logs: `cortex-brain/audit-logs/` (check for errors)
- Validate previous task completion
- Check test results alignment

**During Execution:**
- Log ALL operations (level, category, component, operation, correlation_id)
- TDD if `tdd_required=true` (RED → GREEN → REFACTOR)
- Keep changes <500 lines per commit

**After Task:**
- Verify exit criteria
- Update tracker AND run update script
- Checkpoint every 5 tasks

**Phase/Feature Review:**
- Audit log trace analysis (check ERROR entries)
- Test coverage validation (>80%)
- Immediate remediation if gaps found

---

## 📁 Key Files

| File | Path |
|------|------|
| Tracker | `source-of-truth/todo/00-TODO-CONTINUITY-TRACKER.yaml` |
| Features | `source-of-truth/features/{feature}/feature.yaml` |
| Audit | `cortex-brain/audit-logs/` |
| Risks | `source-of-truth/risk/00-RISK-REGISTRY.yaml` |
| Update | `source-of-truth/update_continuation_prompt.py` |

---

## 🎯 Next Task: {task}

Check `00-TODO-CONTINUITY-TRACKER.yaml` for:
- Task description
- Dependencies
- Estimated time
- Validation criteria

---

**Last Updated:** {datetime.utcnow().isoformat()}Z  
**Executor:** GitHub Copilot → CORTEX (after feat02 Phase 4)
"""
    
    # Write prompt
    with open(prompt_path, "w") as f:
        f.write(content)
    
    print(f"✅ Updated CONTINUATION-PROMPT.md")
    print(f"   Position: {feature}, Phase {phase}, {task}")
    print(f"   Completed: {completed} tasks")


if __name__ == "__main__":
    update_continuation_prompt()
