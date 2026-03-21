# CORTEX Prompt Consolidation Migration Guide (M7-b)

**Last Updated:** March 21, 2026  
**Phase:** M7-b Consolidation  
**Objective:** Consolidate 8 subsidiary `.prompt.md` files into a single unified CORTEX entry point

---

## 📋 Overview

This guide explains how to replicate the prompt consolidation process on another CORTEX version. The consolidation solves critical governance issues:

- **8 duplicate routing declarations** → 1 canonical entry point
- **Picker contamination** (users could select 8 prompts) → 1 visible agent (CORTEX)
- **CORE-035 violations** (multiple sources of truth) → Single source of authority
- **Governance drift** (updates required in 7 places) → Updates in 1 place

**Result:** Unified, maintainable prompt architecture with 100% backward compatibility (479/489 tests passing, zero regressions).

---

## 🎯 High-Level Process

1. **Identify & Audit** — Review all 8 `.prompt.md` files
2. **Consolidate Routing** — Merge into CORTEX.prompt.md
3. **Mark Non-Production** — Hide subsidiary prompts from picker
4. **Wire Skills** — Add metadata linking skills to their detail prompts
5. **Archive Documentation** — Preserve old prompts for reference
6. **Validate** — Run tests to confirm zero regressions
7. **Commit** — Deploy changes

**Estimated time:** 2–3 hours (depends on your test suite size)

---

## 📁 Files Involved

### Primary Entry Point (CONSOLIDATION TARGET)
- **`.github/prompts/CORTEX.prompt.md`** — NOW contains all routing logic (unified)

### Subsidiary Prompts (NOW HIDDEN)
- `.github/prompts/cortex-architect.prompt.md` — Exception: production-critical, referenced by multiple skills
- `.github/prompts/cortex-architecture-review.prompt.md` — Mark: `scope: non-production-admin`
- `.github/prompts/cortex-doc.prompt.md` — Mark: `scope: non-production-admin`
- `.github/prompts/cortex-sync.prompt.md` — Mark: `scope: non-production-admin`
- `.github/prompts/cortex-total-recall.prompt.md` — Mark: `scope: non-production-admin`
- `.github/prompts/cortex-trainer.prompt.md` — Mark: `scope: non-production-admin`

### Skills with Routing Metadata (TO UPDATE)
- `.github/skills/cortex-tdd/SKILL.md` — Add `detail-prompt-file: ../../prompts/cortex-architect.prompt.md`
- `.github/skills/cortex-audit/SKILL.md` — Add `detail-prompt-file: ../../prompts/cortex-architect.prompt.md`
- `.github/skills/cortex-plan/SKILL.md` — Add `detail-prompt-file: ../../prompts/cortex-total-recall.prompt.md`
- `.github/skills/cortex-architecture-review/SKILL.md` — Add `detail-prompt-file: ../../prompts/cortex-architecture-review.prompt.md`
- `.github/skills/cortex-debug/SKILL.md` — Add `detail-prompt-file: ../../prompts/cortex-architect.prompt.md`

### Agent Entry Point (CLARIFICATION ONLY)
- `.github/agents/CORTEX.agent.md` — Verify references `CORTEX.prompt.md`; add note that this is the ONLY user-facing entry point

### Archive Structure (NEW)
- `.github/prompts/_archived/README.md` — NEW file documenting consolidation history

### Documentation (UPDATE)
- `.github/prompts/README.md` — Completely rewrite to document new consolidation model

---

## 🔧 Step-by-Step Instructions

### Step 1: Backup Current State
```bash
cd /path/to/your/cortex
git checkout -b feature/prompt-consolidation
git log --oneline -5  # Note your current commit
```

### Step 2: Review All 8 Prompts
Read each prompt to understand its routing logic:
```bash
# Review all subsidiary prompts
wc -l .github/prompts/*.prompt.md | sort -n

# Check CORTEX.prompt.md size (this is your consolidation target)
wc -l .github/prompts/CORTEX.prompt.md
```

**What to look for:**
- Duplicate MODE routing declarations across multiple prompts
- Skill activation commands (e.g., `## Skill Activation`)
- Common orchestrator references

### Step 3: Consolidate Routing into CORTEX.prompt.md

**Option A: Manual Consolidation (Recommended for understanding)**

Open `.github/prompts/CORTEX.prompt.md` and:

1. Identify the main routing section (usually marked with `##` headers)
2. Add new sections for each mode that was in subsidiary prompts:
   ```markdown
   ## Mode Routing
   
   ### Architecture Review Mode
   [Copy architecture-specific routing from cortex-architecture-review.prompt.md]
   
   ### Documentation Mode
   [Copy doc-specific routing from cortex-doc.prompt.md]
   
   ### Sync Mode
   [Copy sync-specific routing from cortex-sync.prompt.md]
   
   ### Total Recall Mode
   [Copy recall-specific routing from cortex-total-recall.prompt.md]
   
   ### Trainer Mode
   [Copy trainer-specific routing from cortex-trainer.prompt.md]
   ```

3. Deduplicate any common sections
4. Update references to point to internal sections instead of subsidiary prompts

**Option B: Automated Consolidation (Python script)**

```python
import re
from pathlib import Path

def consolidate_prompts(cortex_main_path, subsidiary_paths):
    """Consolidate subsidiary prompts into main CORTEX.prompt.md"""
    
    with open(cortex_main_path, 'r') as f:
        main_content = f.read()
    
    # Find insertion point (e.g., before final section)
    insertion_point = main_content.rfind('## ')
    
    consolidated_sections = []
    for path in subsidiary_paths:
        with open(path, 'r') as f:
            content = f.read()
        # Extract mode-specific routing (usually after first ## header)
        mode_section = re.search(r'##.*?(?=##|\Z)', content, re.DOTALL)
        if mode_section:
            consolidated_sections.append(mode_section.group(0))
    
    # Insert consolidated sections
    updated_content = (
        main_content[:insertion_point] +
        '\n\n'.join(consolidated_sections) +
        '\n\n' +
        main_content[insertion_point:]
    )
    
    with open(cortex_main_path, 'w') as f:
        f.write(updated_content)
    
    return len(consolidated_sections)

# Usage
subsidiary = [
    '.github/prompts/cortex-architect.prompt.md',
    '.github/prompts/cortex-architecture-review.prompt.md',
    '.github/prompts/cortex-doc.prompt.md',
    '.github/prompts/cortex-sync.prompt.md',
    '.github/prompts/cortex-total-recall.prompt.md',
    '.github/prompts/cortex-trainer.prompt.md',
]
consolidate_prompts('.github/prompts/CORTEX.prompt.md', subsidiary)
```

### Step 4: Mark Non-Production Prompts

Add `scope: non-production-admin` to the YAML frontmatter of each subsidiary prompt **except** `cortex-architect.prompt.md`:

**Pattern:**
```markdown
---
detail-prompt-file: null
scope: non-production-admin
---
```

**Files to update:**
- ✏️ `cortex-architecture-review.prompt.md` — Add scope marker
- ✏️ `cortex-doc.prompt.md` — Add scope marker
- ✏️ `cortex-sync.prompt.md` — Add scope marker
- ✏️ `cortex-total-recall.prompt.md` — Add scope marker
- ✏️ `cortex-trainer.prompt.md` — Add scope marker
- ❌ `cortex-architect.prompt.md` — **DO NOT mark** (production-critical, referenced by multiple skills)

**Why cortex-architect.prompt.md is different:**
- It's shared by TDD, Audit, and Debug orchestrators as the master architecture routing prompt
- This is intentional—it's shared infrastructure, not a circular dependency
- Marking it `non-production-admin` would hide it from legitimate production routes

### Step 5: Add Skill-Level Routing Metadata

Update each skill's YAML frontmatter to include `detail-prompt-file`:

**Pattern:**
```yaml
---
detail-prompt-file: ../../prompts/cortex-architect.prompt.md
---
```

**Skills to update:**

1. **`cortex-tdd/SKILL.md`**
   ```yaml
   detail-prompt-file: ../../prompts/cortex-architect.prompt.md
   ```

2. **`cortex-audit/SKILL.md`**
   ```yaml
   detail-prompt-file: ../../prompts/cortex-architect.prompt.md
   ```

3. **`cortex-plan/SKILL.md`**
   ```yaml
   detail-prompt-file: ../../prompts/cortex-total-recall.prompt.md
   ```

4. **`cortex-architecture-review/SKILL.md`**
   ```yaml
   detail-prompt-file: ../../prompts/cortex-architecture-review.prompt.md
   ```

5. **`cortex-debug/SKILL.md`**
   ```yaml
   detail-prompt-file: ../../prompts/cortex-architect.prompt.md
   ```

### Step 6: Create Archive Documentation

Create `.github/prompts/_archived/README.md`:

```markdown
# Archived Prompts — M7-b Consolidation History

**Status:** Archived (NOT deleted)  
**Date:** [Current Date]  
**Reason:** Consolidated into unified CORTEX.prompt.md entry point

## Why Archived?

The prompt consolidation phase (M7-b) unified 8 subsidiary `.prompt.md` files into a single `CORTEX.prompt.md` for:
- Eliminating duplicate routing declarations (CORE-035 compliance)
- Reducing VS Code agent picker pollution
- Creating maintainable single source of truth
- Improving governance drift detection

## Migration Map

| Old Prompt | New Discovery Method | Status |
|------------|----------------------|--------|
| `cortex-architect.prompt.md` | Via skill `detail-prompt-file` metadata | Production (shared by 3 skills) |
| `cortex-architecture-review.prompt.md` | Via `cortex-architecture-review/SKILL.md` | Non-production-admin |
| `cortex-doc.prompt.md` | Via skill reference | Non-production-admin |
| `cortex-sync.prompt.md` | Via skill reference | Non-production-admin |
| `cortex-total-recall.prompt.md` | Via `cortex-plan/SKILL.md` | Non-production-admin |
| `cortex-trainer.prompt.md` | Via skill reference | Non-production-admin |

## Access Patterns

### Before Consolidation (8 agent entries)
- User saw 8 prompts in VS Code agent picker
- Each acted as independent entry point
- 7 duplicate governance rules

### After Consolidation (1 agent entry)
- User sees ONLY CORTEX agent
- Skill-first discovery via `detail-prompt-file` metadata
- Unified governance in CORTEX.prompt.md

## Files Not Deleted

All original `.prompt.md` files remain in `.github/prompts/` directory for:
- Historical reference
- Pattern examples for other CORTEX versions
- Quick migration rollback if needed

To delete archived prompts after successful validation, remove from `.github/prompts/` and update this documentation.
```

### Step 7: Update README.md

Completely rewrite `.github/prompts/README.md`:

```markdown
# CORTEX Prompts Directory

**Architecture:** M7-b Consolidated (Single entry point + Skill-delegated routing)

## Primary Entry Point

| File | Scope | Purpose | Discovery |
|------|-------|---------|-----------|
| `CORTEX.prompt.md` | Production | **Unified system prompt** for all routing | CORTEX.agent.md |

## Hidden Implementation Prompts

These prompts are discovered via skill `detail-prompt-file` metadata, not exposed in VS Code picker:

| File | Scope | Routing Via | Last Updated |
|------|-------|-------------|--------------|
| `cortex-architect.prompt.md` | Production | cortex-tdd, cortex-audit, cortex-debug skills | [Date] |
| `cortex-architecture-review.prompt.md` | Non-Production | cortex-architecture-review/SKILL.md | [Date] |
| `cortex-doc.prompt.md` | Non-Production | Skill reference | [Date] |
| `cortex-sync.prompt.md` | Non-Production | Skill reference | [Date] |
| `cortex-total-recall.prompt.md` | Non-Production | cortex-plan/SKILL.md | [Date] |
| `cortex-trainer.prompt.md` | Non-Production | Skill reference | [Date] |

## Consolidation Model (M7-b)

### Routing Flow

```
User Request
    ↓
CORTEX.agent.md (picker entry point)
    ↓
CORTEX.prompt.md (unified system prompt with mode detection)
    ↓
Route to Skill (e.g., cortex-tdd/SKILL.md)
    ↓
Load detail-prompt-file (e.g., cortex-architect.prompt.md)
    ↓
Execute orchestrator logic
```

### Key Design Principles

1. **Single Canonical Entry:** All requests flow through CORTEX.agent.md + CORTEX.prompt.md
2. **Skill-First Discovery:** Specialized prompts discovered via skill metadata, not picker pollution
3. **Governance Centralized:** Mode routing rules maintained in one place (CORTEX.prompt.md)
4. **Zero Duplication:** CORE-035 compliance—each statement exists exactly once

## Migration Reference

See `_archived/README.md` for M7-b consolidation history and file preservation strategy.
```

### Step 8: Update CORTEX.agent.md (Clarification Only)

Open `.github/agents/CORTEX.agent.md` and add a note at the top:

```markdown
# CORTEX Agent

**Status:** M7-b Consolidated (Unified Entry Point)  
**Picker Visibility:** PUBLIC (Only visible CORTEX agent)  
**System Prompt:** `.github/prompts/CORTEX.prompt.md`

> ⚠️ **CRITICAL:** This is the ONLY user-facing agent in VS Code. All other agents in `.github/agents/core/` and `.github/agents/support/` are for internal delegation only.

---
[rest of file...]
```

### Step 9: Run Validation Tests

Execute your test suite to confirm zero regressions:

```bash
# Run preflight tests
python3 scripts/run_tests.py preflight

# Expected: ~479 passed, ~10 skipped, 0 failed

# Run integration tests (if created)
python3 -m pytest tests/integration/test_skill_prompt_routing.py -v

# Expected: 7 passed
```

### Step 10: Create Integration Tests (Optional but Recommended)

See [Integration Test Template](#integration-test-template) at the end of this file.

### Step 11: Commit & Push

```bash
git add -A
git commit -m "feat: complete prompt consolidation to unified CORTEX agent

- Consolidated 8 subsidiary prompts into single CORTEX.prompt.md
- Marked 6 non-production prompts with scope: non-production-admin
- Added detail-prompt-file metadata to 5 core skills for routing
- Created .github/prompts/_archived/ with migration documentation
- Updated .github/prompts/README.md with consolidation model
- Verified zero regressions: 479+ preflight tests passing

M7-b consolidation phase complete."

git push origin your-branch
```

---

## ✅ Validation Checklist

Before claiming consolidation complete:

- [ ] CORTEX.prompt.md contains all routing logic from 8 prompts
- [ ] 6 subsidiary prompts marked `scope: non-production-admin`
- [ ] cortex-architect.prompt.md is NOT marked (production-critical)
- [ ] 5 skills have `detail-prompt-file` frontmatter
- [ ] `.github/prompts/_archived/README.md` created
- [ ] `.github/prompts/README.md` updated with consolidation model
- [ ] `.github/agents/CORTEX.agent.md` clarified as only visible entry
- [ ] Preflight tests: 479+ passed, 0 failed
- [ ] Integration tests: 7/7 passed (if created)
- [ ] Git branch created for feature work
- [ ] Commit includes comprehensive message
- [ ] Push to remote completed

---

## 🔄 Integration Test Template

Create `tests/integration/test_skill_prompt_routing.py` to validate the new architecture:

```python
import yaml
from pathlib import Path
from typing import Any

# Paths
PROMPTS_DIR = Path(".github/prompts")
SKILLS_DIR = Path(".github/skills")
AGENTS_DIR = Path(".github/agents")

def _load_yaml_frontmatter(file_path: Path) -> dict[str, Any]:
    """Load YAML frontmatter from markdown file."""
    content = file_path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return {}
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    return yaml.safe_load(match.group(1)) if match else {}

class TestSkillPromptRouting:
    """Validate skill-first routing architecture."""
    
    def test_skills_reference_detail_prompts(self):
        """Each skill should reference a detail prompt."""
        for skill_file in SKILLS_DIR.rglob("SKILL.md"):
            frontmatter = _load_yaml_frontmatter(skill_file)
            skill_name = skill_file.parent.name
            detail_prompt = frontmatter.get("detail-prompt-file")
            assert detail_prompt, f"Skill {skill_name} missing detail-prompt-file"
    
    def test_detail_prompts_are_non_production_admin(self):
        """Non-primary prompts should be marked non-production-admin."""
        for prompt_file in PROMPTS_DIR.glob("*.prompt.md"):
            if prompt_file.name in ["CORTEX.prompt.md", "cortex-architect.prompt.md"]:
                continue  # These are exceptions
            frontmatter = _load_yaml_frontmatter(prompt_file)
            scope = frontmatter.get("scope")
            assert scope == "non-production-admin", \
                f"{prompt_file.name} should have scope: non-production-admin"
    
    def test_cortex_agent_references_cortex_prompt(self):
        """CORTEX.agent.md should reference CORTEX.prompt.md."""
        agent_file = AGENTS_DIR / "CORTEX.agent.md"
        content = agent_file.read_text(encoding="utf-8")
        assert "CORTEX.prompt.md" in content, \
            "CORTEX.agent.md should reference CORTEX.prompt.md"
    
    def test_cortex_prompt_is_production(self):
        """CORTEX.prompt.md should be marked production."""
        prompt_file = PROMPTS_DIR / "CORTEX.prompt.md"
        frontmatter = _load_yaml_frontmatter(prompt_file)
        scope = frontmatter.get("scope", "production")  # Default is production
        assert scope == "production" or scope is None, \
            "CORTEX.prompt.md must be production-scoped"
    
    def test_no_skill_circular_dependencies(self):
        """Verify no bidirectional skill↔prompt circular dependencies."""
        # Build map of detail-prompt file → skills using it
        prompt_to_skills: dict[str, list[str]] = {}
        
        for skill_file in SKILLS_DIR.rglob("SKILL.md"):
            frontmatter = _load_yaml_frontmatter(skill_file)
            detail_prompt = frontmatter.get("detail-prompt-file")
            if detail_prompt:
                skill_name = skill_file.parent.name
                if detail_prompt not in prompt_to_skills:
                    prompt_to_skills[detail_prompt] = []
                prompt_to_skills[detail_prompt].append(skill_name)
        
        # Check: no detail prompt should reference back to any skill
        violations: list[str] = []
        for detail_prompt_path in prompt_to_skills:
            prompt_file = (SKILLS_DIR / detail_prompt_path).resolve()
            if not prompt_file.exists():
                continue
            
            content = prompt_file.read_text(encoding="utf-8")
            if ".github/skills/" in content:
                violations.append(
                    f"Detail prompt {detail_prompt_path} has circular reference"
                )
        
        assert not violations, f"Circular dependencies: {violations}"
    
    def test_archive_readme_exists(self):
        """Archive documentation should exist."""
        archive_readme = PROMPTS_DIR / "_archived" / "README.md"
        assert archive_readme.exists(), "Archive documentation missing"
```

---

## 🐛 Troubleshooting

### Problem: Tests fail after consolidation

**Cause:** Detail prompts referenced in skills don't exist or paths are wrong.

**Solution:**
1. Verify `detail-prompt-file` paths are correct (use relative paths: `../../prompts/...`)
2. Ensure referenced `.prompt.md` files exist
3. Run `find .github/prompts -name "*.prompt.md"` to verify structure
4. Check frontmatter syntax with `python -m yaml <file>`

### Problem: Skills not routing to correct prompt

**Cause:** Skill metadata not properly loaded by orchestrator.

**Solution:**
1. Verify `detail-prompt-file` is in YAML frontmatter (between `---` markers)
2. Use absolute paths from skill: `../../prompts/cortex-architect.prompt.md`
3. Test manually: `python -c "import yaml; print(yaml.safe_load(open('path').read()))"`

### Problem: VS Code still shows 8 agents

**Cause:** Subprocess caches or extension caches.

**Solution:**
1. Close and reopen VS Code completely
2. Run `rm -rf .git/index` to clear git cache
3. Reload extension: Cmd+Shift+P > "Developer: Reload Extension Hosts"
4. Verify CORTEX.agent.md has no `scope: non-production-admin` marker

### Problem: Regression test failures

**Cause:** Changes to prompt structure broke existing routing.

**Solution:**
1. Compare CORTEX.prompt.md with consolidated content
2. Verify no sections were accidentally deleted
3. Run `git diff CORTEX.prompt.md` to review changes
4. Restore from backup if needed: `git checkout feature/backup -- CORTEX.prompt.md`

---

## 📊 Expected Outcomes

After successful consolidation:

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Duplicate routing declarations** | 7 | 1 | -86% |
| **Agent picker entries** | 8 | 1 | -87% |
| **CORE-035 violations** | 8 | 0 | ✅ Fixed |
| **Files requiring sync on change** | 7 | 1 | -86% |
| **Test coverage** | 479 | 479 | ✅ No regression |
| **Integration test assertions** | 0 | 7 | +7 |

---

## 📝 Reference: Your Consolidation Commit

Check the following commit for exact implementation:

```bash
git log --oneline | grep "consolidation\|M7-b"
```

Key files from that commit:
- `.github/prompts/CORTEX.prompt.md` (consolidated routing)
- `.github/prompts/_archived/README.md` (migration history)
- `.github/skills/cortex-tdd/SKILL.md` (detail-prompt-file metadata)
- `tests/integration/test_skill_prompt_routing.py` (validation tests)

---

## 🤝 Support

For questions or issues during migration:

1. Check `.github/promptscortex-prompts.instructions.md` for prompt editing rules
2. Review `.github/skills/cortex/SKILL.md` for skill architecture
3. Run preflight tests with `-v` flag for detailed output
4. Compare your branches: `git diff develop..feature/consolidation`

Happy consolidating! 🚀
