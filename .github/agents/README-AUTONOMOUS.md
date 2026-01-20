# CORTEX Autonomous Documentation Restructuring

## Overview

The documentation restructuring process has been redesigned for **autonomous operation** without requiring user input at each phase.

### What Changed

| Aspect | Old (Interactive) | New (Autonomous) |
|--------|------------------|------------------|
| **Execution Model** | Interactive prompts at each phase | Continuous automated execution |
| **User Input** | Required confirmation at Steps 3-5 | Zero interruptions |
| **Discovery** | Manual review of findings in chat | Automatic scanning and categorization |
| **File Actions** | Discussed before moving | Executed automatically |
| **Triggers** | Manual `/cortex-builder` command | Scheduled + file change triggers |
| **Agent Type** | Single interactive session | Autonomous agent process |

---

## Autonomous Components

### 1. **Doc Restructuring Agent** (`doc-restructuring-agent.py`)

Pure Python agent that performs all operations autonomously:

```python
# Core capabilities:
- Phase 0: Root + recursive directory scan
- Phase 1: Automatic file categorization  
- Phase 2: Intelligent action assignment
- Phase 3: Autonomous execution (move/archive/protect)
- Phase 4: Report generation
```

**No user interaction required** - all decisions are data-driven based on:
- File location patterns
- File naming conventions  
- Category rules
- Protection filters

### 2. **Scheduler** (`doc-restructuring-scheduler.yaml`)

Orchestrates autonomous execution:

```yaml
Triggers:
  - Scheduled: Weekly Sunday 2 AM UTC
  - File-based: Detects new .md files in non-docs folders
  - Manual: Can be triggered on-demand

Execution Flow:
  Phase 0: Scan → 
  Phase 1: Analyze → 
  Phase 2: Execute (NO APPROVAL NEEDED) → 
  Phase 3: Report
```

---

## How It Works

### Autonomous Execution Flow

```
[Trigger Event] 
    ↓
[Phase 0: Scan Repository]
  - Recursively find all .md, .txt files
  - Filter out protected files
  - Output: scan-results.json
    ↓
[Phase 1: Analyze & Categorize]
  - Classify files by location/naming
  - Assign actions (move/archive/protect/review)
  - Generate statistics
  - Output: analysis-results.json
    ↓
[Phase 2: Execute (AUTONOMOUS - NO APPROVAL)]
  - Move files to docs/ with proper structure
  - Archive old phase/analysis files
  - Preserve protected files
  - No user confirmation needed
    ↓
[Phase 3: Report]
  - Generate comprehensive report
  - Create git commit with changes
  - Send notifications
  - Log all actions
    ↓
[Complete]
```

### Key Differences from Interactive Mode

**Interactive (Old):**
```
1. User runs: /cortex-builder review #file:roadmap
2. Agent scans and reports findings
3. User reviews findings in chat
4. User confirms: "Yes, proceed with moving files"
5. Agent executes
6. User gets report
```

**Autonomous (New):**
```
1. Scheduler detects new .md files outside docs/
2. Agent scans repository
3. Agent analyzes and categorizes
4. Agent executes moves/archives automatically
5. Agent commits changes to git
6. Notification sent (no user action needed)
```

---

## Running Autonomously

### Option 1: Scheduled (Automatic)
The agent runs automatically on schedule. No action needed.

### Option 2: Manual Trigger
```bash
# Trigger immediately (async)
python .github/agents/doc-restructuring-agent.py --run-now

# Or via GitHub Actions
gh workflow run doc-restructuring.yml
```

### Option 3: Integrated with CI/CD
```yaml
# .github/workflows/doc-restructuring.yml
on:
  schedule:
    - cron: '0 2 * * 0'  # Weekly
  push:
    paths:
      - '**.md'
      - '**.txt'

jobs:
  restructure:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run autonomous doc restructuring
        run: |
          python .github/agents/doc-restructuring-agent.py \
            --root=${{ github.workspace }} \
            --auto-commit
```

---

## Safety Guardrails

Even though autonomous, safety is built-in:

### Protected Files (Never Moved)
```
- requirements.txt
- pytest.ini
- cortex-config.yaml
- .github/workflows/**
- .github/prompts/**
- cortex/**/*.py (source code)
- All Python files in src/
```

### Safety Features
- **Dry-run first**: Preview all changes before execution
- **Backup**: Git backup created before any changes
- **Protection filter**: Respects .gitignore and protected patterns
- **Logging**: Full audit trail of all actions
- **Rollback**: Can revert changes via git if needed
- **Rate limiting**: Max 200 changes per run

---

## Monitoring & Reports

### Execution Log
```
.github/agents/doc-restructuring.log
- Timestamp, level, message for each action
- Review for any issues or manual review items
```

### Analysis Report
```
.github/agents/doc-restructuring-report.json
{
  "timestamp": "2026-01-20T...",
  "analysis": {
    "total_files": 45,
    "by_category": {...},
    "by_action": {...}
  },
  "execution": {
    "moved": 12,
    "archived": 8,
    "protected": 25
  }
}
```

### Git Commit
```
Commit: "Autonomous: Documentation restructuring - Phase [DATE]"
Changes: All file moves and archives tracked
Branch: auto/doc-restructuring-[DATE]
PR: Auto-created for review (optional)
```

---

## Customization

### Modify Scan Patterns
Edit `doc-restructuring-agent.py`:
```python
DOC_EXTENSIONS = {'.md', '.txt', '.rst', '.adoc'}
CONFIG_EXTENSIONS = {'.yaml', '.yml', '.json'}
```

### Adjust Categories
Edit `_categorize_file()` method to add/modify logic:
```python
def _categorize_file(self, file_path: Path) -> FileCategory:
    # Add custom patterns here
```

### Add Protected Patterns
Edit `ProtectionFilter` class:
```python
PROTECTED_PATTERNS = {
    'my-critical-file.md',  # Add here
    # ...
}
```

---

## Troubleshooting

### Agent Not Running
```bash
# Check if scheduler is enabled
cat .github/agents/doc-restructuring-scheduler.yaml | grep -A5 trigger

# Run manually to test
python .github/agents/doc-restructuring-agent.py --scan --root=.
```

### Files Not Moving
Check the log:
```bash
tail -f .github/agents/doc-restructuring.log

# Look for:
- "is_protected=true" → file is protected
- "Error" → check error message
- "skipped" → might need to adjust categories
```

### Need to Exclude More Files
Add to `PROTECTED_PATTERNS` in agent:
```python
PROTECTED_PATTERNS.add('my-special-file.md')
```

---

## Integration with User Workflows

### Still Works with Chat Commands
```
User: /cortex-builder analyze-docs
→ Calls same agent script
→ Returns results in chat
→ User can request changes
→ Agent executes if autonomous mode enabled
```

### Hybrid Mode (Recommended)
- **Autonomous background**: Weekly scan & archive
- **Interactive on-demand**: User triggers analysis, reviews, decides
- **Both use same agent**: Consistent behavior

---

## Future Enhancements

- [ ] Machine learning for better categorization
- [ ] Semantic analysis of doc content
- [ ] Auto-generation of cross-references
- [ ] Integration with doc build system
- [ ] Automatic table of contents generation
- [ ] Dead link detection and correction
- [ ] Documentation quality scoring

---

## Related Files

- [Agent Script](doc-restructuring-agent.py)
- [Scheduler Config](doc-restructuring-scheduler.yaml)  
- [Execution Log](doc-restructuring.log)
- [Reports](doc-restructuring-report.json)
- [Original Prompt](../prompts/cortex-doc.prompt.md)

---

**Status**: Ready for autonomous deployment  
**Last Updated**: 2026-01-20  
**Maintenance**: Review execution logs weekly
