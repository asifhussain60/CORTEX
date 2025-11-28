# Multi-Repository CORTEX Setup Guide

**Purpose:** Use one CORTEX installation across multiple repositories  
**Version:** 1.0  
**Author:** Asif Hussain  
**Created:** 2025-11-28

---

## Overview

This guide shows how to use a single CORTEX installation (from REPO_A) to work with multiple repositories (REPO_B, REPO_C, etc.) using the hybrid approach.

**Benefits:**
- ✅ Single CORTEX installation (~100MB)
- ✅ Repository-specific learning (isolated namespaces)
- ✅ Shared knowledge graph
- ✅ One upgrade updates all
- ✅ Consistent configuration

---

## Step 1: Verify CORTEX Installation (REPO_A)

**Check your CORTEX installation location:**

```bash
# Navigate to REPO_A
cd ~/PROJECTS/REPO_A

# Verify CORTEX exists
ls CORTEX/.github/prompts/CORTEX.prompt.md

# Expected output: File exists
```

**Get absolute path:**

```bash
# Get full path to CORTEX
CORTEX_PATH=$(cd CORTEX && pwd)
echo $CORTEX_PATH

# Example output: /Users/asifhussain/PROJECTS/REPO_A/CORTEX
```

---

## Step 2: Set Up REPO_B Entry Point

**Create copilot-instructions.md in REPO_B:**

```bash
# Navigate to REPO_B
cd ~/PROJECTS/REPO_B

# Create .github directory if needed
mkdir -p .github

# Create entry point file
cat > .github/copilot-instructions.md << 'EOF'
# GitHub Copilot Instructions for REPO_B

**CORTEX Entry Point:** Load `~/PROJECTS/REPO_A/CORTEX/.github/prompts/CORTEX.prompt.md`

**Repository:** REPO_B  
**CORTEX Location:** Shared installation at ~/PROJECTS/REPO_A/CORTEX  
**Learning Namespace:** `workspace.REPO_B.*` (isolated in Tier 3)

---

## How to Use CORTEX

**Just talk naturally - CORTEX figures out what you need:**

```
"plan authentication feature"
"start tdd workflow"
"review architecture"
```

**All CORTEX commands work across repositories:**
- `plan [feature]` - Feature planning with DoR/DoD
- `start tdd` - TDD workflow (RED→GREEN→REFACTOR)
- `discover views` - Auto-extract UI element IDs
- `feedback` - Report issues to CORTEX team
- `help` - Show all available commands

**Repository-Specific Context:**

CORTEX automatically learns your REPO_B patterns:
- Architecture preferences
- Code conventions
- Testing patterns
- Critical files
- Workflow preferences

**Storage:** All REPO_B-specific learning stored in:
`~/PROJECTS/REPO_A/CORTEX/cortex-brain/tier3/context.db`
Namespace: `workspace.REPO_B.*`

**Isolation:** REPO_B learning stays separate from REPO_A - no cross-contamination.

---

## Project Context

**Detected (Auto-filled by CORTEX):**
- Language: [Will be detected on first use]
- Framework: [Will be detected on first use]
- Build System: [Will be detected on first use]
- Test Framework: [Will be detected on first use]

**🧠 CORTEX learns these over time through observation**

---

## Quick Commands

- `help` - Show all CORTEX commands
- `tutorial` - Interactive hands-on tutorial
- `show context` - View what CORTEX remembers about REPO_B
- `update profile` - Change interaction mode/experience level
- `healthcheck` - Validate CORTEX system health

---

**CORTEX Version:** 3.2.1  
**Installation Type:** Shared (Hybrid Approach)  
**Brain Learning:** Enabled (Tier 3 namespace: workspace.REPO_B.*)

EOF

echo "✅ Entry point created: .github/copilot-instructions.md"
```

---

## Step 3: Validate Setup

**Test CORTEX access from REPO_B:**

```bash
# Still in REPO_B directory
cd ~/PROJECTS/REPO_B

# Test CORTEX can be accessed
python ~/PROJECTS/REPO_A/CORTEX/src/cortex_entry.py --version

# Expected output: CORTEX v3.2.1
```

**Test namespace isolation:**

```bash
# Check Tier 3 storage
sqlite3 ~/PROJECTS/REPO_A/CORTEX/cortex-brain/tier3/context.db "SELECT DISTINCT namespace FROM patterns;"

# Expected output should eventually include:
# workspace.REPO_A.*
# workspace.REPO_B.*
```

---

## Step 4: First Use in REPO_B

**Open REPO_B in VS Code:**

```bash
cd ~/PROJECTS/REPO_B
code .
```

**In GitHub Copilot Chat, say:**

```
help
```

**CORTEX will:**
1. ✅ Detect you're in REPO_B (via working directory)
2. ✅ Load shared CORTEX from REPO_A
3. ✅ Create `workspace.REPO_B.*` namespace in Tier 3
4. ✅ Start learning REPO_B-specific patterns
5. ✅ Show help menu with all commands

**Test a command:**

```
show context
```

**Expected output:**
```
## 🧠 CORTEX Context Status

**Repository:** REPO_B
**Namespace:** workspace.REPO_B.*
**Conversations:** 0 (first use - will learn over time)
**Context Quality:** N/A (no data yet)

CORTEX is now observing REPO_B patterns and will learn:
- Your code conventions
- Architecture preferences
- Testing patterns
- Critical files
```

---

## Step 5: Add More Repositories

**Repeat Step 2 for REPO_C, REPO_D, etc.:**

```bash
# For each new repository
cd ~/PROJECTS/REPO_C
mkdir -p .github

# Copy entry point template
cp ~/PROJECTS/REPO_B/.github/copilot-instructions.md .github/

# Update repository name
sed -i '' 's/REPO_B/REPO_C/g' .github/copilot-instructions.md
```

**Result:**

```
~/PROJECTS/
├── REPO_A/CORTEX/                    # Shared CORTEX installation
│   └── cortex-brain/tier3/context.db # Contains all namespaces:
│                                       # - workspace.REPO_A.*
│                                       # - workspace.REPO_B.*
│                                       # - workspace.REPO_C.*
├── REPO_B/.github/copilot-instructions.md → Points to REPO_A/CORTEX
├── REPO_C/.github/copilot-instructions.md → Points to REPO_A/CORTEX
└── REPO_D/.github/copilot-instructions.md → Points to REPO_A/CORTEX
```

---

## Benefits

**Disk Space:**
- Before: 100MB × 4 repos = 400MB
- After: 100MB total (75% savings)

**Upgrade:**
- Before: Upgrade 4 separate installations
- After: Upgrade once in REPO_A (affects all repos)

**Learning:**
- Before: Isolated learning per repo (no cross-repo insights)
- After: Isolated learning per repo + shared knowledge graph

**Configuration:**
- Before: Manage 4 separate configs (drift risk)
- After: One config file (consistency guaranteed)

---

## Namespace Isolation

**How CORTEX Keeps Repositories Separate:**

Each repository gets its own namespace in Tier 3:

```sql
-- REPO_A patterns
INSERT INTO patterns (namespace, pattern_type, pattern_data)
VALUES ('workspace.REPO_A.copilot_instructions', 'architecture', '...');

-- REPO_B patterns (different namespace)
INSERT INTO patterns (namespace, pattern_type, pattern_data)
VALUES ('workspace.REPO_B.copilot_instructions', 'architecture', '...');
```

**Query Isolation:**

When CORTEX works in REPO_B, it only queries `workspace.REPO_B.*` patterns:

```python
# Auto-detected namespace per repository
namespace = f"workspace.{repo_name}.copilot_instructions"

# Only retrieves REPO_B patterns
patterns = tier3.query_patterns(namespace=namespace)
```

**No Cross-Contamination:**
- REPO_A conventions don't affect REPO_B
- REPO_B test patterns stay separate from REPO_A
- Each repo learns independently

**Shared Knowledge:**
- CORTEX features available to all repos
- Bug fixes benefit all repos
- Upgrade once, all repos updated

---

## Troubleshooting

### Issue: "CORTEX not found"

**Symptom:** Error when running CORTEX commands from REPO_B

**Cause:** Path to CORTEX in copilot-instructions.md is incorrect

**Fix:**

```bash
# Verify CORTEX path
ls ~/PROJECTS/REPO_A/CORTEX/.github/prompts/CORTEX.prompt.md

# Update copilot-instructions.md with correct path
cd ~/PROJECTS/REPO_B
nano .github/copilot-instructions.md

# Update this line:
**CORTEX Entry Point:** Load `~/PROJECTS/REPO_A/CORTEX/.github/prompts/CORTEX.prompt.md`
```

---

### Issue: "Namespace not isolated"

**Symptom:** REPO_B learning affects REPO_A

**Cause:** Namespace detection not working

**Fix:**

```bash
# Check namespace detection
cd ~/PROJECTS/REPO_B
python ~/PROJECTS/REPO_A/CORTEX/src/cortex_entry.py --check-namespace

# Should output: workspace.REPO_B.*
```

---

### Issue: "Permission denied"

**Symptom:** Cannot write to Tier 3 database

**Cause:** File permissions on shared CORTEX

**Fix:**

```bash
# Make Tier 3 writable
chmod -R u+w ~/PROJECTS/REPO_A/CORTEX/cortex-brain/tier3/
```

---

## FAQ

**Q: Can I have different CORTEX versions per repo?**  
A: No, with hybrid approach all repos share one CORTEX version. If you need different versions, use embedded installation (separate CORTEX per repo).

**Q: What happens if I delete CORTEX from REPO_A?**  
A: All repositories lose CORTEX access. Restore CORTEX to REPO_A or move it to a new location and update all copilot-instructions.md files.

**Q: Can I move CORTEX to a different location?**  
A: Yes! Move CORTEX, then update copilot-instructions.md in all repositories to point to new location.

**Q: How do I upgrade CORTEX?**  
A: Upgrade once in REPO_A: `cd ~/PROJECTS/REPO_A/CORTEX && git pull origin main`. All repositories benefit immediately.

**Q: Can I share CORTEX across different machines?**  
A: Not directly. Each machine needs its own CORTEX installation. Use git to sync CORTEX code, but brain data stays local.

**Q: Does this work with embedded CORTEX?**  
A: This guide is specifically for shared installation. Embedded (REPO/CORTEX/) is a different pattern - each repo gets its own CORTEX copy.

---

## Advanced: Shared CORTEX in Different Location

**If you prefer CORTEX in a central location (not inside REPO_A):**

```bash
# Create central CORTEX location
mkdir -p ~/CORTEX-SHARED
cd ~/CORTEX-SHARED

# Clone CORTEX
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX
pip install -e .

# Update all repository entry points
cd ~/PROJECTS/REPO_A
nano .github/copilot-instructions.md
# Change: ~/CORTEX-SHARED/CORTEX/.github/prompts/CORTEX.prompt.md

cd ~/PROJECTS/REPO_B
nano .github/copilot-instructions.md
# Change: ~/CORTEX-SHARED/CORTEX/.github/prompts/CORTEX.prompt.md
```

**Benefits:**
- CORTEX not tied to any specific repository
- Can delete REPO_A without affecting CORTEX
- Cleaner separation of concerns

---

## Summary

**What You Achieved:**

✅ Single CORTEX installation serves all repositories  
✅ Repository-specific learning (isolated namespaces)  
✅ 75% disk space savings  
✅ One upgrade updates all  
✅ Consistent configuration  
✅ No code duplication

**Next Steps:**

1. Use CORTEX normally in REPO_B: `plan [feature]`, `start tdd`, etc.
2. Add more repositories using Step 5
3. Upgrade CORTEX in REPO_A when new versions release
4. Monitor namespace isolation: `show context` in each repo

---

**Version:** 1.0  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)
