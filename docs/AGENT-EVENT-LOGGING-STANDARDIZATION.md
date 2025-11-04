# Agent Event Logging Standardization Plan

**Date:** 2025-11-04  
**Purpose:** Standardize event logging across all 10 KDS specialist agents  
**Status:** 🎯 READY FOR IMPLEMENTATION  
**Priority:** HIGH - Required for automatic BRAIN learning

---

## 🎯 Objective

Ensure ALL 10 KDS specialist agents properly log events to `events.jsonl` following the standard format defined in `KDS/kds-brain/README.md`.

**Why This Matters:**
- ✅ Enables automatic BRAIN learning
- ✅ Triggers automatic BRAIN updates (50 event threshold)
- ✅ Feeds knowledge graph with quality data
- ✅ Enables progressive intelligence in Weeks 2-4

---

## 📋 Standard Event Format

```jsonl
{"timestamp":"ISO8601","event":"event_type",...additional_fields}
```

**Required Fields:**
- `timestamp` - ISO 8601 format (e.g., "2025-11-04T15:45:53Z")
- `event` - Event type from standard list (see below)

**Optional Common Fields:**
- `session_id` - Current session identifier
- `agent` - Agent name (e.g., "work-planner", "code-executor")
- `confidence` - Confidence score (0.0-1.0)
- `success` - Boolean success indicator

---

## 📊 Standard Event Types by Category

### Planning Events
```json
{"timestamp":"...","event":"planning_session","agent":"work-planner","session_id":"...","feature":"...","phases_created":N,"tasks_created":N}
{"timestamp":"...","event":"pattern_matched","pattern":"...","confidence":0.85}
{"timestamp":"...","event":"workflow_template_used","template":"..."}
```

### Execution Events
```json
{"timestamp":"...","event":"file_modified","file":"...","session":"...","task":"...","lines_changed":N}
{"timestamp":"...","event":"files_modified_together","files":["...","..."],"session":"..."}
{"timestamp":"...","event":"task_completed","task_id":"...","duration_minutes":N,"success":true}
```

### Testing Events
```json
{"timestamp":"...","event":"test_created","test_file":"...","test_type":"unit|integration|ui","session":"..."}
{"timestamp":"...","event":"test_passed","test_file":"...","test_name":"..."}
{"timestamp":"...","event":"test_failed","test_file":"...","test_name":"...","reason":"..."}
```

### Validation Events
```json
{"timestamp":"...","event":"validation_passed","category":"linting|build|tests","session":"..."}
{"timestamp":"...","event":"validation_failed","category":"...","reason":"...","session":"..."}
{"timestamp":"...","event":"validation_insight","category":"...","insight":"...","confidence":0.90}
```

### Routing Events
```json
{"timestamp":"...","event":"intent_detected","intent":"plan|execute|test|validate","phrase":"...","confidence":0.95,"success":true}
{"timestamp":"...","event":"routing_decision","from":"...","to":"...","reason":"..."}
```

### Correction Events
```json
{"timestamp":"...","event":"correction","type":"file_mismatch|dependency|logic","incorrect":"...","correct":"...","frequency":N}
{"timestamp":"...","event":"rollback_performed","reason":"...","files_affected":["..."]}
```

### Session Events
```json
{"timestamp":"...","event":"session_started","session_id":"...","feature":"..."}
{"timestamp":"...","event":"session_completed","session_id":"...","duration_minutes":N,"tasks_completed":N}
{"timestamp":"...","event":"session_resumed","session_id":"...","last_task":"..."}
```

### Brain Events
```json
{"timestamp":"...","event":"brain_updated","events_processed":N,"patterns_learned":N,"duration_seconds":N}
{"timestamp":"...","event":"knowledge_graph_query","query_type":"...","result_confidence":0.85}
```

### Workflow Events
```json
{"timestamp":"...","event":"workflow_success","workflow":"...","pattern":"...","steps":["..."],"success_rate":0.95}
{"timestamp":"...","event":"workflow_pattern","name":"...","frequency":N,"success_rate":0.90}
```

---

## 🤖 Agent-by-Agent Implementation Checklist

### 1. Intent Router (intent-router.md)

**Events to Log:**
- ✅ `intent_detected` - When intent is identified
- ✅ `routing_decision` - When routing to specialist agent
- ✅ `knowledge_graph_query` - When querying BRAIN for confidence

**Implementation:**
```markdown
After intent detection:
  Log: {"timestamp":"...","event":"intent_detected","intent":"plan","phrase":"add button","confidence":0.95,"success":true}
  
After routing decision:
  Log: {"timestamp":"...","event":"routing_decision","from":"router","to":"work-planner","reason":"PLAN intent detected"}
```

**Status:** ❌ NOT IMPLEMENTED

---

### 2. Work Planner (work-planner.md)

**Events to Log:**
- ✅ `planning_session` - When plan is created
- ✅ `pattern_matched` - When similar patterns found (Week 3+)
- ✅ `workflow_template_used` - When template applied (Week 3+)

**Implementation:**
```markdown
After plan creation:
  Log: {"timestamp":"...","event":"planning_session","agent":"work-planner","session_id":"...","feature":"...","phases_created":3,"tasks_created":8}
  
After pattern matching (Week 3+):
  Log: {"timestamp":"...","event":"pattern_matched","pattern":"export_feature_workflow","confidence":0.85}
```

**Status:** ✅ PARTIALLY IMPLEMENTED (planning_session only, logged manually in Week 2 planning)

---

### 3. Code Executor (code-executor.md)

**Events to Log:**
- ✅ `file_modified` - When file is changed
- ✅ `files_modified_together` - When multiple files changed in same task
- ✅ `task_completed` - When task finishes
- ✅ `tdd_phase_complete` - When RED/GREEN/REFACTOR phase finishes (Week 2+)

**Implementation:**
```markdown
After modifying file:
  Log: {"timestamp":"...","event":"file_modified","file":"HostControlPanelContent.razor","session":"fab-button","task":"Add button","lines_changed":23}
  
After modifying multiple files:
  Log: {"timestamp":"...","event":"files_modified_together","files":["Component.razor","styles.css"],"session":"..."}
  
After task completion:
  Log: {"timestamp":"...","event":"task_completed","task_id":"1.1","duration_minutes":15,"success":true}
```

**Status:** ❌ NOT IMPLEMENTED

---

### 4. Test Generator (test-generator.md)

**Events to Log:**
- ✅ `test_created` - When test file is created
- ✅ `test_passed` - When test passes
- ✅ `test_failed` - When test fails

**Implementation:**
```markdown
After creating test:
  Log: {"timestamp":"...","event":"test_created","test_file":"Tests/UI/button.spec.ts","test_type":"ui","session":"..."}
  
After running tests:
  Log: {"timestamp":"...","event":"test_passed","test_file":"...","test_name":"should render button"}
  Log: {"timestamp":"...","event":"test_failed","test_file":"...","test_name":"...","reason":"Element not found"}
```

**Status:** ❌ NOT IMPLEMENTED

---

### 5. Health Validator (health-validator.md)

**Events to Log:**
- ✅ `validation_passed` - When validation succeeds
- ✅ `validation_failed` - When validation fails
- ✅ `validation_insight` - When interesting pattern discovered

**Implementation:**
```markdown
After validation check:
  Log: {"timestamp":"...","event":"validation_passed","category":"linting","session":"..."}
  Log: {"timestamp":"...","event":"validation_failed","category":"build","reason":"Syntax error","session":"..."}
  
When discovering insight:
  Log: {"timestamp":"...","event":"validation_insight","category":"performance","insight":"Long-running tests detected","confidence":0.90}
```

**Status:** ❌ NOT IMPLEMENTED

---

### 6. Change Governor (change-governor.md)

**Events to Log:**
- ✅ `governance_review` - When reviewing KDS changes
- ✅ `violation_detected` - When rule violation found
- ✅ `approval_granted` - When change approved

**Implementation:**
```markdown
After governance review:
  Log: {"timestamp":"...","event":"governance_review","files_reviewed":3,"violations":0,"approved":true}
  
When violation detected:
  Log: {"timestamp":"...","event":"violation_detected","rule":"Rule #8","file":"agent.md","reason":"Missing TDD workflow"}
```

**Status:** ❌ NOT IMPLEMENTED

---

### 7. Error Corrector (error-corrector.md)

**Events to Log:**
- ✅ `correction` - When user corrects a mistake
- ✅ `rollback_performed` - When reverting changes

**Implementation:**
```markdown
After correction:
  Log: {"timestamp":"...","event":"correction","type":"file_mismatch","incorrect":"HostControlPanel.razor","correct":"HostControlPanelContent.razor","frequency":1}
  
After rollback:
  Log: {"timestamp":"...","event":"rollback_performed","reason":"Wrong file modified","files_affected":["HostControlPanel.razor"]}
```

**Status:** ❌ NOT IMPLEMENTED

---

### 8. Session Resumer (session-resumer.md)

**Events to Log:**
- ✅ `session_resumed` - When session is resumed

**Implementation:**
```markdown
After resuming session:
  Log: {"timestamp":"...","event":"session_resumed","session_id":"...","last_task":"2.3","next_task":"2.4"}
```

**Status:** ❌ NOT IMPLEMENTED

---

### 9. Screenshot Analyzer (screenshot-analyzer.md)

**Events to Log:**
- ✅ `screenshot_analyzed` - When screenshot is processed
- ✅ `requirements_extracted` - When requirements are extracted

**Implementation:**
```markdown
After analysis:
  Log: {"timestamp":"...","event":"screenshot_analyzed","elements_detected":5,"confidence":0.85}
  Log: {"timestamp":"...","event":"requirements_extracted","count":3,"type":"UI requirements"}
```

**Status:** ❌ NOT IMPLEMENTED

---

### 10. Commit Handler (commit-handler.md)

**Events to Log:**
- ✅ `commit_created` - When commit is made
- ✅ `files_committed` - When files are committed together

**Implementation:**
```markdown
After commit:
  Log: {"timestamp":"...","event":"commit_created","session_id":"...","files_count":3,"commit_hash":"abc123"}
  Log: {"timestamp":"...","event":"files_committed","files":["file1.md","file2.yaml"],"session":"..."}
```

**Status:** ❌ NOT IMPLEMENTED

---

## 🔧 Implementation Approach

### Phase 1: Add Event Logging to All Agents (Immediate)

**For each agent:**
1. Identify key decision points (intent detection, file modifications, validations, etc.)
2. Add event logging calls at those points
3. Use standard event format
4. Include appropriate fields (session_id, confidence, etc.)

**Example Implementation Pattern:**

```markdown
## 📝 Event Logging (NEW - Week 1 Requirement)

After each significant action, log to events.jsonl:

```powershell
$event = @{
    timestamp = (Get-Date).ToUniversalTime().ToString("o")
    event = "intent_detected"
    intent = "plan"
    phrase = "add button"
    confidence = 0.95
    success = $true
} | ConvertTo-Json -Compress
Add-Content -Path "KDS/kds-brain/events.jsonl" -Value $event
```

**Required Events:**
- `intent_detected` - After intent is identified
- `routing_decision` - After routing to specialist agent
```

### Phase 2: Verify Event Count Triggers (Automatic Update)

**Ensure Rule #16 Step 5 includes:**
```markdown
Step 5: Check event count
  - Count unprocessed events in events.jsonl
  - IF count >= 50 OR (24 hours passed AND count >= 10):
    - Invoke brain-updater.md automatically
    - Log brain update event
```

### Phase 3: Test Event Flow

**Validation Test:**
```powershell
# Test 1: Events are logged
$beforeCount = (Get-Content "KDS/kds-brain/events.jsonl" | Measure-Object).Count
Invoke-KDS "Create test plan"
$afterCount = (Get-Content "KDS/kds-brain/events.jsonl" | Measure-Object).Count
$afterCount | Should -BeGreaterThan $beforeCount

# Test 2: Event format is valid
$lastEvent = Get-Content "KDS/kds-brain/events.jsonl" -Tail 1 | ConvertFrom-Json
$lastEvent.timestamp | Should -Not -BeNullOrEmpty
$lastEvent.event | Should -Not -BeNullOrEmpty

# Test 3: Automatic update triggers
# Add 50 events manually
1..50 | ForEach-Object {
    $event = @{timestamp=(Get-Date).ToUniversalTime().ToString("o");event="test"} | ConvertTo-Json -Compress
    Add-Content "KDS/kds-brain/events.jsonl" -Value $event
}
# Next agent action should trigger brain-updater
Invoke-KDS "Test action"
# Verify brain updated
$kgLastUpdate = (Get-Content "KDS/kds-brain/knowledge-graph.yaml" | Select-String "last_updated").Line
$kgLastUpdate | Should -Match (Get-Date).ToString("yyyy-MM-dd")
```

---

## ✅ Success Criteria

### Phase 1 Complete When:
- [ ] All 10 agents have event logging implemented
- [ ] All agents use standard event format
- [ ] All agents include appropriate event types
- [ ] No agent logs duplicate or malformed events

### Phase 2 Complete When:
- [ ] Rule #16 Step 5 includes event count check
- [ ] 50 event threshold triggers automatic brain update
- [ ] 24-hour + 10 events triggers automatic brain update
- [ ] Brain update events are logged

### Phase 3 Complete When:
- [ ] Validation tests pass
- [ ] Event flow verified from agent → events.jsonl → brain-updater → knowledge-graph.yaml
- [ ] Automatic triggers working
- [ ] No performance degradation (<50ms overhead per event)

---

## 📊 Expected Impact

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Agents Logging Events** | 0/10 | 10/10 | ✅ 100% |
| **BRAIN Updates** | Manual only | Automatic | ✅ Continuous |
| **Event Coverage** | 0% | 95%+ | ✅ Comprehensive |
| **Learning Latency** | >24 hours | <1 hour (50 events) | ✅ 24x faster |
| **Knowledge Graph Growth** | Stalled | Active | ✅ Progressive |

---

## 🎯 Next Steps

1. **Immediate:** Update all 10 agents with event logging
2. **Short-term:** Implement automatic update triggers
3. **Medium-term:** Test event flow with Week 2 implementation
4. **Long-term:** Monitor BRAIN health and event quality

---

**Status:** 🎯 READY FOR IMPLEMENTATION  
**Owner:** Code Executor (LEFT brain with TDD automation - Week 2)  
**Dependencies:** Week 1 hemisphere structure (✅ COMPLETE)  
**Target:** Complete before beginning Week 2 Phase 1 (TDD automation)

---

**Version:** 1.0  
**Last Updated:** 2025-11-04  
**Related Documents:**
- `KDS/kds-brain/README.md` - Event logging standard
- `KDS/KDS-V6-WEEK1-COMPLETE.md` - Week 1 completion report
- `KDS/KDS-V6-PROGRESSIVE-INTELLIGENCE-PLAN.md` - Overall progressive plan
