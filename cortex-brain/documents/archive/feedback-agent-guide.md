# Feedback Agent Guide

**Purpose:** Structured feedback collection and GitHub issue reporting  
**Version:** 1.0  
**Status:** ✅ Production Ready  
**Audience:** CORTEX Users & Administrators

---

## Overview

FeedbackAgent is CORTEX's built-in issue reporting system that collects structured feedback about bugs, gaps, improvements, and questions. It automatically captures context (conversation history, files, environment) and optionally uploads reports to GitHub Gist for team collaboration.

**Key Features:**
- ✅ Structured feedback collection (4 categories: bug, gap, improvement, question)
- ✅ Auto-context capture (conversation, files, environment)
- ✅ Privacy protection (redacts sensitive data)
- ✅ GitHub Gist integration (optional auto-upload)
- ✅ GitHub Issues formatting (ready for copy-paste)

---

## Quick Start

### Report a Bug

```
feedback bug
```

CORTEX will ask for details and create a structured bug report.

### Report Missing Feature (Gap)

```
feedback gap
```

Describe what feature is missing or incomplete.

### Suggest Improvement

```
feedback improvement
```

Share ideas to make CORTEX better.

### Ask Question

```
feedback question
```

Request clarification about CORTEX behavior.

---

## Usage Scenarios

### Scenario 1: Report System Alignment Issue

**User says:** "feedback bug"

**CORTEX asks:** "Describe the bug you encountered"

**User responds:** "System alignment validation crashes when Phase 2 crawlers are present"

**Result:**
- ✅ Creates `CORTEX-FEEDBACK-20251125_183000.md` in `cortex-brain/documents/reports/`
- ✅ Captures conversation context automatically
- ✅ Uploads to GitHub Gist (if configured)
- ✅ Shows GitHub Issues formatted output

**Report Structure:**
```markdown
# CORTEX Feedback Report: Bug

**ID:** CORTEX-FEEDBACK-20251125_183000  
**Type:** Bug  
**Severity:** Medium  
**Date:** November 25, 2025

## Description
System alignment validation crashes when Phase 2 crawlers are present

## Context
- Conversation ID: conv-20251125-180000
- Files Referenced: src/crawlers/multi_app_orchestrator.py
- Environment: macOS, Python 3.11

## Steps to Reproduce
[Auto-extracted from conversation if available]

## Expected Behavior
System alignment should discover and validate all crawlers

## Actual Behavior
Alignment validation throws ModuleNotFoundError

## Suggested Fix
Update OrchestratorScanner to include src/crawlers/ path
```

---

### Scenario 2: Report Documentation Gap

**User says:** "feedback gap"

**CORTEX asks:** "What feature or documentation is missing?"

**User responds:** "No guide file exists for FeedbackAgent"

**Result:**
- ✅ Creates gap report with type="gap"
- ✅ Severity auto-set to "high" (documentation gaps are prioritized)
- ✅ Captures list of missing documentation files

**Report shows:**
```markdown
# CORTEX Feedback Report: Gap

**ID:** CORTEX-FEEDBACK-20251125_183100  
**Type:** Gap  
**Severity:** High  
**Date:** November 25, 2025

## Missing Feature/Documentation
No guide file exists for FeedbackAgent

## Impact
Users cannot discover feedback system capabilities without guide

## Suggested Solution
Create `.github/prompts/modules/feedback-agent-guide.md`

## Priority
High - Affects discoverability and user experience
```

---

### Scenario 3: Suggest Performance Improvement

**User says:** "feedback improvement"

**CORTEX asks:** "Describe the improvement you'd like to see"

**User responds:** "System alignment validation is slow on large codebases (>100 features)"

**Result:**
- ✅ Creates improvement report
- ✅ Captures performance metrics if available
- ✅ Suggests optimization approaches

---

## Configuration

### Enable GitHub Gist Auto-Upload

**File:** `cortex.config.json`

```json
{
  "feedback": {
    "auto_upload_gist": true,
    "github_token": "ghp_your_token_here",
    "gist_visibility": "private"
  }
}
```

**Get GitHub Token:**
1. Go to https://github.com/settings/tokens
2. Generate new token (classic)
3. Check "gist" scope
4. Copy token to config

**Privacy:** Tokens stored locally, never transmitted except to GitHub API.

---

### Configure Feedback Severity Levels

**Severity Mapping:**
- **Critical** - System crashes, data loss, security vulnerabilities
- **High** - Feature broken, major workflow blocked
- **Medium** - Minor issues, workaround available (default)
- **Low** - Nice-to-have improvements, typos

**Auto-Detection:**
FeedbackAgent automatically adjusts severity based on keywords:
- "crash", "error", "broken" → High
- "missing", "gap", "undocumented" → High
- "slow", "improve", "optimize" → Medium
- "typo", "cosmetic", "suggestion" → Low

---

## Integration with CORTEX Workflow

### TDD Workflow Integration

When tests fail during TDD workflow, you can immediately report:

```
feedback bug - Test discovery fails for Phase 2 crawlers
```

FeedbackAgent captures:
- Current test execution context
- Files being tested
- Test output and error messages
- Suggested fixes based on error analysis

---

### Planning Workflow Integration

During feature planning, report gaps:

```
feedback gap - DoR validation missing security checklist validation
```

FeedbackAgent captures:
- Active planning document
- DoR/DoD checklists
- Related features and dependencies

---

### System Alignment Integration

After running `align`, report discovered issues:

```
feedback bug - Alignment scanner doesn't discover crawlers
```

FeedbackAgent captures:
- Alignment report data
- Integration scores
- Missing layers (documentation, tests, wiring)

---

## Advanced Features

### Context Capture

**Automatic Context Collection:**
- Conversation history (last 10 messages)
- Referenced files and line numbers
- Environment details (OS, Python version, CORTEX version)
- Active workflow state (TDD phase, planning stage, etc.)

**Privacy Protection:**
- Auto-redacts passwords, API keys, tokens
- Removes sensitive file paths
- Anonymizes user-specific data (optional)

**Example Context Block:**
```yaml
context:
  conversation_id: conv-20251125-180000
  files_referenced:
    - src/crawlers/multi_app_orchestrator.py (lines 150-175)
    - tests/integration/test_phase_2_integration.py (lines 45-60)
  environment:
    os: macOS 14.0
    python: 3.11.5
    cortex_version: 3.2.0
  workflow_state:
    active_workflow: system_alignment
    phase: validation
    last_command: align
```

---

### GitHub Issues Formatting

**Copy-Paste Ready:**
FeedbackAgent generates reports in GitHub Issues markdown format:

```markdown
**Type:** Bug  
**Severity:** High  
**Component:** System Alignment  

## Description
[User description]

## Steps to Reproduce
1. [Step 1]
2. [Step 2]

## Expected vs Actual
**Expected:** [Expected behavior]  
**Actual:** [Actual behavior]

## Environment
- OS: macOS 14.0
- Python: 3.11.5
- CORTEX: 3.2.0

## Suggested Fix
[Auto-generated or user-provided fix]
```

**Usage:**
1. Run `feedback bug`
2. Open generated report in `cortex-brain/documents/reports/`
3. Copy content
4. Create new issue at https://github.com/asifhussain60/CORTEX/issues
5. Paste content
6. Submit

---

### Gist Auto-Upload

**How It Works:**
1. User runs `feedback bug` command
2. FeedbackAgent creates structured report
3. Report uploaded to GitHub Gist (private by default)
4. Gist URL returned to user
5. User shares Gist URL with team or in Slack

**Benefits:**
- ✅ Easy sharing with team members
- ✅ Collaborative commenting on Gist
- ✅ Version history if report updated
- ✅ Privacy control (public/private)

**Example Output:**
```
✅ Feedback report created: CORTEX-FEEDBACK-20251125_183000.md
✅ Uploaded to GitHub Gist: https://gist.github.com/asifhussain60/abc123xyz
📋 Copy-paste ready for GitHub Issues

Share Gist URL with your team or paste content directly to GitHub Issues.
```

---

## Troubleshooting

### Issue: "GitHub token not configured"

**Cause:** Gist auto-upload enabled but no token in `cortex.config.json`

**Solution:**
1. Disable auto-upload: `"auto_upload_gist": false`
2. OR add GitHub token (see Configuration section)

---

### Issue: "Feedback report created but no context captured"

**Cause:** Conversation tracking not enabled

**Solution:**
Enable conversation tracking:
```
enable conversation tracking
```

Then retry feedback command.

---

### Issue: "Sensitive data not redacted in report"

**Cause:** FeedbackAgent's redaction patterns missed specific format

**Solution:**
1. Manually edit report before sharing
2. Report redaction gap: `feedback gap - Redaction missed [format]`
3. FeedbackAgent will improve patterns

---

## API Reference

### FeedbackAgent Class

```python
from src.agents.feedback_agent import FeedbackAgent

agent = FeedbackAgent(brain_path="/path/to/cortex-brain")

# Create feedback report
result = agent.create_feedback_report(
    user_input="System alignment crashes with Phase 2 crawlers",
    feedback_type="bug",
    severity="high",
    context={
        "conversation_id": "conv-123",
        "files": ["src/crawlers/multi_app_orchestrator.py"]
    },
    auto_upload=True
)

# Result contains:
# - report_id: Unique feedback ID
# - file_path: Path to generated report
# - gist_url: GitHub Gist URL (if uploaded)
# - github_issues_format: Copy-paste ready content
```

---

## Best Practices

### When to Use Feedback Command

**DO use feedback for:**
- ✅ Bugs blocking your work
- ✅ Missing documentation preventing understanding
- ✅ Performance issues slowing workflows
- ✅ Gaps in CORTEX capabilities
- ✅ Questions about unexpected behavior

**DON'T use feedback for:**
- ❌ General questions (use `help` instead)
- ❌ Feature requests unrelated to CORTEX
- ❌ Debugging your application code
- ❌ Configuration issues (use `healthcheck` first)

---

### Writing Good Feedback Reports

**Good Bug Report:**
```
feedback bug - System alignment validation fails when discovering Phase 2 crawlers.
Error: ModuleNotFoundError in OrchestratorScanner.
Expected: All 5 Phase 2 components discovered.
Actual: 0 crawlers discovered, 21 other features found.
```

**Bad Bug Report:**
```
feedback bug - alignment doesn't work
```

**Why?** Good report is specific, includes error message, states expected vs actual behavior.

---

## Related Commands

- `healthcheck` - Validate CORTEX system health before reporting
- `align` - Run system alignment (may reveal reportable issues)
- `show context` - View conversation context before feedback
- `optimize` - Clean brain data if feedback related to performance

---

## Feedback Categories Reference

| Category | Use When | Severity Default | Examples |
|----------|----------|------------------|----------|
| **Bug** | Something broken | High | Crashes, errors, data loss |
| **Gap** | Feature missing | High | No docs, missing functionality |
| **Improvement** | Make better | Medium | Optimize performance, UX polish |
| **Question** | Unclear behavior | Low | "Why does X work this way?" |

---

## Report Storage

**Location:** `cortex-brain/documents/reports/CORTEX-FEEDBACK-*.md`

**Structure:**
```
cortex-brain/documents/reports/
├── CORTEX-FEEDBACK-20251125_183000.md  (bug report)
├── CORTEX-FEEDBACK-20251125_183100.md  (gap report)
├── CORTEX-FEEDBACK-20251125_183200.md  (improvement)
└── CORTEX-FEEDBACK-20251125_183300.md  (question)
```

**Retention:** Reports kept indefinitely (manual cleanup via `cleanup` command)

---

## Success Metrics

**Good Feedback Report Includes:**
1. ✅ Clear, specific description
2. ✅ Steps to reproduce (for bugs)
3. ✅ Expected vs actual behavior
4. ✅ Environment context
5. ✅ Suggested fix (optional but helpful)

**Bad Feedback Report:**
1. ❌ Vague description ("it doesn't work")
2. ❌ No context or examples
3. ❌ Unclear severity
4. ❌ No steps to reproduce

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)  
**Repository:** https://github.com/asifhussain60/CORTEX

**Version:** 1.0  
**Last Updated:** November 25, 2025
