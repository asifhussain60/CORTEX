# Master Plan Presentation Layer — CI/CD Integration Guide

**Authority:** cortex-architect.prompt.md § User Response Template — Golden Format  
**Version:** 1.0 | **Updated:** 2026-02-19  
**Purpose:** Enable CI/CD integration of the 5-section presentation layer for automated status reporting, dashboards, and executive communication.

---

## Overview

The CORTEX refactor master plan now includes a `presentation` section that follows the 5-section User Response Template format (Summary → Analysis → Recommendation → Benefits & Risks → Next Steps). This guide explains how to extract, validate, and display this presentation layer through CI/CD automation.

### Key Features

✅ **Automated Extraction** — Parses presentation YAML on every commit  
✅ **JSON Output** — Machine-readable format for dashboard integration  
✅ **Markdown Reports** — Human-readable executive summaries for PRs and dashboards  
✅ **Schema Validation** — Ensures presentation layer structure integrity  
✅ **Artifact Storage** — 30-day retention for historical tracking  

---

## Architecture

```
cortex-refactor-master.yaml (YAML)
    ↓
    [Workflow: master-plan-presentation.yml]
    ├── extract-master-plan-presentation.py → master-plan-presentation.json
    ├── generate-master-plan-report.py → master-plan-report.md
    └── Schema validation (pyyaml + jsonschema)
    ↓
Artifacts (30-day retention)
    ├── master-plan-presentation.json (for dashboards)
    └── master-plan-report.md (for PRs/status)
```

---

## Workflow: master-plan-presentation.yml

**Trigger:** 
- Push to `cortex-registry/planning/cortex-refactor-master.yaml` on `CORTEX-GPT` branch
- Manual trigger via `workflow_dispatch`

**Jobs:**

### 1. extract-presentation
Extracts the presentation section from the master plan YAML.

**Steps:**
1. Checkout code
2. Set up Python 3.9
3. Install pyyaml
4. Run `scripts/extract-master-plan-presentation.py`
   - Loads master plan YAML
   - Extracts presentation section
   - Counts phase statuses (complete/in_progress/pending)
   - Extracts health metrics (P0/P1 issues, regression status)
   - Outputs `master-plan-presentation.json`

**Output:** `master-plan-presentation.json`
```json
{
  "summary": "Executive overview (2 sentences)",
  "current_state": "Detailed current state description",
  "key_findings": ["Finding 1", "Finding 2", ...],
  "blockers": {"P0": [...], "P1": [...]},
  "recommendation": "Primary strategy",
  "next_steps_immediate": ["Step 1", "Step 2", ...],
  "phase_counts": {
    "complete": 8,
    "in_progress": 1,
    "pending": 2,
    "total": 11
  },
  "health": {
    "p0_issues": 0,
    "p1_issues": 3,
    "regression_status": "Status text"
  }
}
```

### 2. generate-master-plan-report
Converts JSON presentation to markdown report.

**Steps:**
1. Run `scripts/generate-master-plan-report.py`
   - Reads `master-plan-presentation.json`
   - Builds markdown report with:
     - Executive summary
     - Phase progress table
     - Current state
     - Health status
     - Key findings (bullet list)
     - Recommendation
     - Next steps (numbered list)
   - Outputs `master-plan-report.md`

**Output:** `master-plan-report.md` (markdown)

### 3. validate-presentation
Validates presentation schema and YAML syntax.

**Checks:**
- ✅ `presentation` section exists
- ✅ Required fields present (summary, analysis, recommendation, next_steps)
- ✅ Analysis subsections valid (current_state, baseline_vs_targets, key_findings, blockers_and_risks)
- ✅ Recommendation subsections valid (primary_strategy, execution_path)
- ✅ Next_steps has immediate and later arrays
- ✅ YAML syntax is valid

**Output:** Validation status in workflow logs

### 4. notify-status
Notifies stakeholders of status update.

**Actions:**
- Downloads presentation artifacts
- Displays completion status
- Available for webhook integration (future)

---

## Scripts

### extract-master-plan-presentation.py

**Purpose:** Parse master plan YAML and extract presentation layer  
**Input:** `cortex-registry/planning/cortex-refactor-master.yaml`  
**Output:** `master-plan-presentation.json`  

**Usage:**
```bash
python3 scripts/extract-master-plan-presentation.py
```

**Key Functions:**
- Loads YAML with PyYAML
- Counts phases by status
- Extracts health metrics
- Outputs structured JSON

### generate-master-plan-report.py

**Purpose:** Convert presentation JSON to markdown report  
**Input:** `master-plan-presentation.json`  
**Output:** `master-plan-report.md`  

**Usage:**
```bash
python3 scripts/generate-master-plan-report.py
```

**Output Format:**
```markdown
# 📊 CORTEX Master Plan Status

## Executive Summary
{summary}

## Phase Progress
- ✅ Complete: 8/11
- 🔵 In Progress: 1
- ⚪ Pending: 2

## Current State
{current_state}

## Health Status
- P0 Issues: 0
- P1 Issues: 3
- Regression: {status}

## Key Findings
- {finding_1}
- {finding_2}
...

## Recommendation
{recommendation}

## Next Steps (Immediate)
1. {step_1}
2. {step_2}
...
```

---

## Integration Points

### 1. GitHub Artifacts

**Location:** `.github/artifacts/` (30-day retention)

**Files:**
- `master-plan-presentation.json` — For dashboard ingestion
- `master-plan-report.md` — For human review

**Download:**
```bash
# In CI/CD step
uses: actions/download-artifact@v3
with:
  name: master-plan-presentation
```

### 2. PR Comments (Future)

Configure workflow to post report to PR:
```yaml
- name: Comment on PR
  if: github.event_name == 'pull_request'
  uses: actions/github-script@v6
  with:
    script: |
      const report = fs.readFileSync('master-plan-report.md', 'utf8');
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: report
      });
```

### 3. Dashboard Integration (Future)

Parse `master-plan-presentation.json` in dashboards:
```python
import json
import requests

# Download artifact
artifact = requests.get(
    "https://api.github.com/repos/asifhussain60/CORTEX/actions/artifacts"
)

# Parse presentation
presentation = json.load(artifact.json()['artifacts'][0])
phase_progress = presentation['phase_counts']
health = presentation['health']

# Display in dashboard
display_status(phase_progress, health)
```

### 4. Slack Notifications (Future)

Post status to Slack:
```yaml
- name: Notify Slack
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "Master Plan Status Updated",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": ${{ toJSON(steps.extract.outputs.summary) }}
            }
          }
        ]
      }
```

---

## Maintenance

### On Each Phase Completion

1. Update `cortex-refactor-master.yaml`:
   - Mark phase as `complete`
   - Update counters (complete/in_progress/pending)
   - Add completion details (tests, duration, commits)
   - Update health status if needed

2. Sync presentation section:
   - Update `presentation.summary` with new status
   - Update `presentation.analysis.current_state` phase list
   - Update `presentation.recommendation.execution_path` if strategy changed
   - Add new blockers/risks to `presentation.analysis.blockers_and_risks`
   - Update `presentation.next_steps.immediate`

3. Workflow runs automatically:
   - Extracts updated presentation
   - Generates new report
   - Validates schema
   - Stores artifacts

### Manual Runs

Trigger manually via GitHub Actions:
```bash
gh workflow run master-plan-presentation.yml
```

---

## Troubleshooting

### Workflow Fails with YAML Error

**Symptom:** `Invalid YAML in master plan`

**Solution:**
```bash
# Validate locally
python3 -c "import yaml; yaml.safe_load(open('cortex-registry/planning/cortex-refactor-master.yaml'))"

# Fix syntax errors
# Ensure presentation section is properly indented
# Check for missing colons, quotes, etc.
```

### Missing Presentation Section

**Symptom:** Workflow runs but skips extraction

**Solution:**
```bash
# Ensure presentation section exists in master plan
# Required structure:
# presentation:
#   summary: |
#     ...
#   analysis:
#     ...
#   recommendation:
#     ...
#   benefits_and_risks_analysis:
#     ...
#   next_steps:
#     ...
```

### JSON Parsing Error

**Symptom:** `generate-master-plan-report.py` fails with JSON decode error

**Solution:**
```bash
# Validate JSON output
python3 -c "import json; json.load(open('master-plan-presentation.json'))"

# Ensure extract script ran successfully
# Check for Unicode/encoding issues in presentation text
```

---

## Future Enhancements

- [ ] Dashboard integration (fetch and display artifacts)
- [ ] Slack notifications on status changes
- [ ] PR comments with automated reports
- [ ] Historical tracking (store timestamped reports)
- [ ] Email summaries (weekly digest)
- [ ] Webhook triggers for external systems
- [ ] Diff detection (highlight changes between runs)

---

## Related Documentation

- **Master Plan:** `cortex-registry/planning/cortex-refactor-master.yaml`
- **Response Template:** `.github/templates/cortex-response-templates.md`
- **Architect Prompt:** `.github/prompts/cortex-architect.prompt.md`
- **Workflows:** `.github/workflows/`

---

**Last Updated:** 2026-02-19  
**Authority:** cortex-architect.prompt.md § User Response Template — Golden Format
