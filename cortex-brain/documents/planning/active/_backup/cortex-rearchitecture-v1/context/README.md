🧠 CORTEX - Context Artifacts Index
Author: Asif Hussain | GitHub: github.com/asifhussain60/CORTEX

---

# Context Artifacts

This folder contains historical and discovery context for the **cortex-rearchitecture-v1** plan.

---

## 📋 Current Contents

### Phase 0 Completion

**governance-completion-summary.md** - Complete summary of Phase 0 (Governance Foundation) outcomes:
- SKULL rule implementation
- Test harness creation (16 tests)
- Copyright utility development
- Semantic naming quality enforcement

---

## 🎯 Purpose of Context Artifacts

Context artifacts provide the **"why"** and **"how"** behind code changes:

1. **Git History** (`git-history.yaml`) - Who changed what, when, and why
   - Commit messages and authors
   - File change frequency
   - Security-critical comments
   - Business rule documentation

2. **AST Analysis** (`ast-analysis.yaml`) - Code structure and dependencies
   - Class hierarchies
   - Function call graphs
   - Import relationships
   - Complexity metrics

3. **Comments & TODOs** (`comments.yaml`) - Extracted inline documentation
   - TODO comments (actionable items)
   - FIXME warnings (known issues)
   - Business rule comments
   - Expert knowledge (who knows this code)

4. **Code Graph** (`code-graph.json`) - Dependency relationships
   - Module dependencies
   - Function call chains
   - Circular dependency detection
   - Impact analysis (what breaks if X changes)

5. **Context Index** (`context-index.yaml`) - Master index of all artifacts
   - When each artifact was created
   - What triggered its generation
   - Relevance scores
   - Cross-references

---

## 📊 When Context is Gathered

Context artifacts are generated during:

1. **Pre-Planning Discovery** (Phase 1) - Before creating new plan
   - Check for existing plans
   - Identify related work
   - Reuse previous context

2. **Temp Plan Creation** (Tier 1-2) - Initial context gathering
   - Git blame analysis
   - Basic AST scan
   - Comment extraction

3. **Temp → Active Promotion** (Tier 3-4) - Full context gathering
   - Complete git history
   - Deep AST analysis
   - Comprehensive comment extraction
   - Dependency graph generation

4. **Phase Execution** - Context updates during implementation
   - New commits analyzed
   - Code changes reflected
   - Dependency updates

---

## 🔗 How to Use Context Artifacts

### For CORTEX Orchestrators

```python
# Load git history context
with open(plan_folder / "context" / "git-history.yaml") as f:
    git_context = yaml.safe_load(f)

# Find security-critical files
security_files = [
    file for file in git_context['files']
    if 'security' in file['comments'].lower()
]

# Identify expert for this module
expert = git_context['files'][target_file]['primary_author']
```

### For Human Reviewers

- **Starting work?** Read `context-index.yaml` for overview
- **Security changes?** Check `git-history.yaml` for critical comments
- **Refactoring?** Review `code-graph.json` for impact analysis
- **Understanding code?** Read `comments.yaml` for business rules

---

## 🎨 Office Filing System Analogy

**Physical Office:** Background Research Manila Folder

```
Project Folder (Hanging Folder)
├── Background Research (Manila Folder)
│   ├── Previous Reports (git history)
│   ├── Org Chart (AST structure)
│   ├── Meeting Notes (comments)
│   └── Vendor Relationships (code graph)
```

**CORTEX Equivalent:** context/ Subfolder

```
cortex-rearchitecture-v1/ (Plan Folder)
├── context/ (Background Research)
│   ├── git-history.yaml (previous work)
│   ├── ast-analysis.yaml (code structure)
│   ├── comments.yaml (inline knowledge)
│   └── code-graph.json (relationships)
```

---

## 📝 Notes

- Context artifacts are **immutable snapshots** at time of generation
- Updates create new files with timestamps (e.g., `git-history-20251215.yaml`)
- Old context preserved for historical reference
- Context copied when plans are versioned (v1 → v2)

---

**Last Updated:** December 15, 2025  
**Next Update:** After Phase 1 (Visual Tracker Migration)
