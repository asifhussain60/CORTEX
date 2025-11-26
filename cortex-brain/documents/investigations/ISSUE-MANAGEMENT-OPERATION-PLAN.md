# CORTEX 3.0 Issue Management Operation Plan

**Operation:** `issue_management`  
**Phase:** 2 (User Feedback System)  
**Timeline:** Week 6 of 8-week build-ready strategy  
**Type:** Unified operation with modes (vs separate EPMs)  
**Priority:** Essential for MVP build feedback collection

---

## 🎯 Operation Overview

### Purpose
Single operation handling all issue lifecycle: report → review → track → resolve

### Integration Points
- **Storage:** `cortex-brain/issues/` directory with YAML structure
- **Templates:** Response templates for instant help
- **Agents:** Health Validator for auto-diagnosis, Pattern Matcher for similar issues
- **Memory:** Tier 1 conversation tracking, Tier 2 pattern learning

---

## 🔧 Technical Architecture

### Natural Language Triggers

```yaml
operation_name: "issue_management"
natural_language_patterns:
  report_mode:
    - "report issue"
    - "found a bug" 
    - "something's broken"
    - "error in cortex"
    - "problem with"
    - "not working"
  
  review_mode:
    - "show issues"
    - "review issues"
    - "list problems"
    - "issue status"
    - "what's broken"
  
  track_mode:
    - "update issue"
    - "close issue"
    - "issue resolved"
    - "fixed the problem"
    - "mark complete"
```

### Workflow Modes

#### Mode 1: Report (Interactive Issue Collection)

**Trigger:** "report issue" or error detected
**Agent:** Health Validator + Intent Router
**Duration:** 2-5 minutes

```yaml
report_workflow:
  step_1_context_analysis:
    - Auto-detect: Current operation, files, error messages
    - Environment: Python version, OS, CORTEX version
    - Recent: Last 3 conversations from Tier 1
  
  step_2_interactive_gathering:
    - Issue type: bug, feature_request, performance, documentation
    - Severity: critical, high, medium, low
    - Component: operation_name, agent, template_system, brain_tier
    - Reproduction: steps_to_reproduce, expected_vs_actual
  
  step_3_auto_enrichment:
    - Similar issues: Pattern Matcher searches Tier 2
    - Health check: Current system status
    - Suggested tags: Based on context analysis
  
  step_4_storage:
    - File: cortex-brain/issues/YYYY-MM-DD-HHMMSS-{issue_type}.yaml
    - Format: Structured YAML with all context
    - Tier 1: Store conversation for continuity
```

#### Mode 2: Review (Filtered Issue Display)

**Trigger:** "show issues" or "review problems"
**Agent:** Pattern Matcher + Health Validator
**Duration:** < 30 seconds

```yaml
review_workflow:
  filters:
    status: [open, investigating, resolved, closed]
    severity: [critical, high, medium, low]
    component: [cleanup, setup, templates, agents, brain]
    date_range: "last_7_days" | "last_30_days" | "all"
    assignee: "user" | "auto" | "all"
  
  output_format:
    - Critical issues first (blocking build)
    - Grouped by component
    - Each issue: ID, title, severity, age, status
    - Quick actions: view_details, update_status, close
  
  intelligence:
    - Pattern Matcher finds related issues
    - Health Validator suggests resolution priority
    - Auto-tag patterns from Tier 2 knowledge
```

#### Mode 3: Track (Status Updates & Resolution)

**Trigger:** "update issue" or "mark resolved"
**Agent:** Intent Router + Learner
**Duration:** 1-2 minutes

```yaml
track_workflow:
  status_updates:
    - open → investigating → resolved → closed
    - Add resolution notes, time spent, root cause
    - Link to conversations where issue was worked on
  
  resolution_capture:
    - What fixed it: code_change, config_update, user_error
    - Prevention: How to avoid in future
    - Learnings: Store pattern in Tier 2 for similar issues
  
  auto_close:
    - Health check: Verify issue no longer reproduces
    - Age-based: Low priority issues > 30 days
    - Pattern-based: Resolved similar issues suggest auto-close
```

---

## 📂 Storage Schema

### Issue File Format

```yaml
# cortex-brain/issues/2025-11-14-143052-bug.yaml
issue_id: "2025-11-14-143052-bug"
created: "2025-11-14T14:30:52Z"
updated: "2025-11-14T14:35:12Z"

metadata:
  type: "bug"  # bug, feature_request, performance, documentation
  severity: "high"  # critical, high, medium, low
  status: "open"  # open, investigating, resolved, closed
  component: "cleanup"  # operation name or system component
  
context:
  cortex_version: "3.0-MVP"
  python_version: "3.9.6"
  platform: "macOS"
  operation: "cleanup"
  files_involved: ["src/operations/cleanup.py"]
  error_message: "PermissionError: [Errno 13] Permission denied"
  
details:
  title: "Cleanup operation fails with permission error"
  description: |
    When running 'cleanup workspace', getting permission denied on temp files.
    Happens consistently on macOS with .venv directory cleanup.
  
  reproduction_steps:
    - "Say 'cleanup workspace'"
    - "Select standard profile"  
    - "Error occurs during temp file removal"
  
  expected: "Temp files removed successfully"
  actual: "PermissionError on .venv/lib/python3.9/site-packages/"
  
enrichment:
  similar_issues: []  # Pattern Matcher results
  health_check: "passed"  # Health Validator results  
  suggested_tags: ["permissions", "macos", "cleanup", "venv"]
  
resolution:
  status: null
  fixed_by: null
  root_cause: null
  prevention: null
  resolution_notes: null
  time_spent_hours: null
  closed_date: null

conversation_links:
  - conversation_id: "conv_20251114_143052_abc123"
  - tier1_ref: "Recent conversation about cleanup failure"
```

### Issue Directory Structure

```
cortex-brain/issues/
├── index.yaml                    # Issue registry & stats
├── 2025-11-14-143052-bug.yaml   # Individual issues
├── 2025-11-14-150312-feature.yaml
├── resolved/                     # Archive for closed issues
└── templates/                    # Issue templates by type
    ├── bug-template.yaml
    ├── feature-template.yaml
    └── performance-template.yaml
```

---

## 🚀 Implementation Plan (Week 6)

### Day 1-2: Core Operation Structure
- Create `src/operations/issue_management.py`
- Natural language trigger detection
- Mode routing (report/review/track)
- Basic YAML storage system

### Day 3-4: Report Mode Implementation
- Interactive issue gathering workflow
- Context analysis (current operation, files, errors)
- Health Validator integration for auto-diagnosis
- Issue templates and validation

### Day 5: Review Mode Implementation  
- Issue filtering and display
- Pattern Matcher integration for related issues
- Priority ranking and grouping
- Quick action commands

### Day 6-7: Track Mode Implementation
- Status update workflows
- Resolution capture and learning
- Auto-close logic
- Tier 2 pattern storage for issue resolution

---

## 🎯 Success Criteria

### User Experience
- ✅ Natural language: "found a bug" works instantly
- ✅ Context-aware: Auto-detects current operation and files
- ✅ Efficient: Issue reported in < 3 minutes
- ✅ Intelligent: Suggests similar issues and solutions

### Technical Integration
- ✅ Tier 1: Conversation continuity across report/track cycles
- ✅ Tier 2: Pattern learning for issue resolution
- ✅ Agents: Health Validator diagnoses, Pattern Matcher finds similar
- ✅ Templates: Instant help responses for common issue types

### Build Readiness  
- ✅ Essential feedback collection for MVP build users
- ✅ Systematic issue tracking and resolution
- ✅ Quality metrics for continuous improvement
- ✅ User confidence through transparent issue handling

---

## 🔗 Integration with Build Timeline

**Week 1-2:** Test stabilization (100% pass rate)
**Week 3-5:** Core operations implementation (7 operations working)
**Week 6:** **Issue Management operation** ← THIS PHASE
**Week 7-8:** Build creation and initial user testing

**Why Week 6:** Core operations are stable, but before final build release. Perfect timing to add feedback collection before users start testing.

---

## 📊 Expected Impact

### For Development
- **Quality:** Systematic issue tracking and resolution
- **Learning:** Pattern recognition for recurring issues  
- **Efficiency:** Unified workflow vs multiple separate tools
- **Intelligence:** Auto-diagnosis and suggestion system

### For Users (Build Testing)
- **Confidence:** Clear issue reporting process
- **Transparency:** Visible issue status and resolution
- **Speed:** Quick issue reporting with context auto-detection
- **Intelligence:** Suggested solutions from similar past issues

---

## 🎓 Architecture Benefits

### vs Separate EPMs
- **Unified Context:** Same operation accesses all issue data
- **Natural Routing:** "report bug" vs "show issues" routes automatically  
- **Workflow Integration:** Report → Review → Track seamlessly
- **Consistent Interface:** One operation to learn, not two
- **Agent Coordination:** Same agents work across all modes
- **Memory Integration:** Tier 1/2 learning spans entire issue lifecycle

### vs External Tools
- **Zero Setup:** Works immediately with CORTEX installation
- **Context Aware:** Knows current operation, files, conversation
- **Intelligent:** Pattern matching and auto-diagnosis
- **Integrated:** Storage in CORTEX brain, no external dependencies
- **Natural Language:** No new syntax to learn

---

**Author:** Asif Hussain  
**Created:** 2025-11-14  
**Phase:** CORTEX 3.0 Build-Ready Strategy  
**Integration:** Week 6 of 8-week timeline