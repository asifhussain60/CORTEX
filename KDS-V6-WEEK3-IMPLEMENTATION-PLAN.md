# KDS v6.0 Week 3 Implementation Plan
# Right Brain Pattern Matching & Recognition

## 🎯 Objective

Build Right Brain pattern matching capability using Week 2's TDD automation to demonstrate progressive intelligence.

**Key Innovation:** The brain uses test-first development to build its own pattern recognition system!

---

## 📊 Current Status

**Baseline:** 6/49 tests passing (12.2%)
- ✅ Work-planner has some pattern awareness (4 tests)
- ✅ Coordination queue exists (1 test)
- ✅ Week 3 validation suite exists (1 test)
- ❌ Pattern infrastructure missing (43 tests failing)

**Week 2 Foundation Available:**
- ✅ TDD automation (RED→GREEN→REFACTOR)
- ✅ Test creation and execution
- ✅ Validation and rollback
- ✅ Left hemisphere execution state

---

## 🏗️ Implementation Phases

### Phase 0: Test Infrastructure (TDD Foundation)
**Duration:** 30 minutes
**TDD Approach:** Create test fixtures FIRST

**Tasks:**
1. Create pattern library directory structure
2. Create pattern schema (`pattern.schema.json`)
3. Create sample pattern fixtures for testing
4. Create workflow template fixtures
5. Create coordination message schema

**Deliverables:**
```
kds-brain/right-hemisphere/
├── patterns/
│   └── .gitkeep
├── workflow-templates/
│   └── .gitkeep
├── schemas/
│   ├── pattern.schema.json
│   └── workflow-template.schema.json
kds-brain/corpus-callosum/
└── schemas/
    └── coordination-message.schema.json
tests/fixtures/patterns/
├── sample-export-pattern.yaml
├── sample-crud-pattern.yaml
└── sample-workflow-template.yaml
```

**Validation:** Group 1 tests should pass (7 tests)

---

### Phase 1: Pattern Matching Scripts (RED→GREEN→REFACTOR)
**Duration:** 2-3 hours
**TDD Approach:** Tests FIRST, then implementation

**Using Week 2 TDD Automation:**
```powershell
# Step 1: Create tests (RED)
.\scripts\left-brain\create-tests.ps1 `
    -FeatureConfig "tests\fixtures\week3\pattern-matcher-feature.yaml" `
    -OutputPath "tests\unit\right-brain\pattern-matcher.tests.ps1"

# Step 2: Verify tests fail (RED validation)
.\scripts\left-brain\verify-red-phase.ps1 `
    -TestFile "tests\unit\right-brain\pattern-matcher.tests.ps1"

# Step 3: Implement code (GREEN)
.\scripts\left-brain\implement-code.ps1 `
    -FeatureConfig "tests\fixtures\week3\pattern-matcher-feature.yaml" `
    -OutputPath "scripts\right-brain\match-pattern.ps1"

# Step 4: Auto-run tests (GREEN validation)
.\scripts\left-brain\auto-test-runner.ps1 `
    -TestFile "tests\unit\right-brain\pattern-matcher.tests.ps1"

# Step 5: Refactor (REFACTOR)
.\scripts\left-brain\refactor-code.ps1 `
    -File "scripts\right-brain\match-pattern.ps1"
```

**Scripts to Create (TDD):**
1. `match-pattern.ps1` - Find similar patterns by query
2. `create-pattern.ps1` - Create new pattern from template
3. `analyze-similarity.ps1` - Calculate semantic similarity

**Deliverables:**
- 3 scripts with full test coverage
- Tests pass for pattern matching (Group 2: 8 tests)

**Validation:** Group 2 tests should pass (8 tests)

---

### Phase 2: Workflow Template Generation (RED→GREEN→REFACTOR)
**Duration:** 2-3 hours
**TDD Approach:** Tests FIRST, then implementation

**Using Week 2 TDD Automation:**
```powershell
# Full TDD cycle for template generator
.\scripts\left-brain\run-tdd-cycle.ps1 `
    -FeatureConfig "tests\fixtures\week3\template-generator-feature.yaml"
```

**Scripts to Create (TDD):**
1. `generate-workflow-template.ps1` - Create workflow from pattern
2. `validate-workflow-template.ps1` - Validate template structure

**Template Structure:**
```yaml
template_id: export_feature_workflow
pattern_id: export_feature
phases:
  - phase_0: architectural_discovery
  - phase_1: test_infrastructure_tdd
  - phase_2: service_layer
  - phase_3: api_endpoint
  - phase_4: ui_component
tdd_required: true
risk_assessment:
  - file_hotspot_check
  - dependency_analysis
architectural_guidance:
  - follow_existing_export_patterns
  - maintain_separation_of_concerns
```

**Deliverables:**
- 2 scripts with full test coverage
- Templates include TDD workflow
- Tests pass for template generation (Group 3: 7 tests)

**Validation:** Group 3 tests should pass (7 tests)

---

### Phase 3: Pattern Learning & Storage (RED→GREEN→REFACTOR)
**Duration:** 2-3 hours
**TDD Approach:** Tests FIRST, then implementation

**Using Week 2 TDD Automation:**
```powershell
# Full TDD cycle for pattern extractor
.\scripts\left-brain\run-tdd-cycle.ps1 `
    -FeatureConfig "tests\fixtures\week3\pattern-extractor-feature.yaml"
```

**Scripts to Create (TDD):**
1. `extract-pattern.ps1` - Extract pattern from completed work
2. `update-pattern-library.ps1` - Store pattern in library

**Pattern Extraction Logic:**
```powershell
# Analyze completed session
$session = Get-SessionHistory -SessionId $SessionId

# Extract components
$components = @(
    $session.files_created | Group-Object { $_.type }
    $session.tests_created
    $session.phases_completed
)

# Generate pattern
$pattern = @{
    pattern_id = Generate-PatternId
    feature_components = $components
    workflow_phases = $session.phases
    success_metrics = $session.metrics
    reusable_components = Identify-Reusable $components
}

# Validate and store
Validate-Pattern $pattern
Store-InLibrary $pattern
```

**Deliverables:**
- 2 scripts with full test coverage
- Pattern learning from history
- Tests pass for pattern storage (Group 4: 6 tests)

**Validation:** Group 4 tests should pass (6 tests)

---

### Phase 4: Work Planner Integration (RED→GREEN→REFACTOR)
**Duration:** 1-2 hours
**TDD Approach:** Tests FIRST for integration points

**Integration Points in work-planner.md:**

1. **Pattern Query on Planning:**
```markdown
## Step 1: Query Pattern Library

Before creating plan, check for similar patterns:

```powershell
$similarPatterns = .\scripts\right-brain\match-pattern.ps1 `
    -Query $UserRequest `
    -MinimumSimilarity 0.7

if ($similarPatterns.matches_found) {
    Write-Host "📚 Found similar pattern: $($similarPatterns.pattern_id)" -ForegroundColor Cyan
    Write-Host "   Similarity: $($similarPatterns.similarity_score * 100)%" -ForegroundColor Yellow
    
    # Generate workflow from template
    $workflow = .\scripts\right-brain\generate-workflow-template.ps1 `
        -PatternId $similarPatterns.pattern_id
    
    # Adapt to current request
    $adaptedPlan = Adapt-WorkflowToRequest $workflow $UserRequest
} else {
    # Create new plan from scratch
    $adaptedPlan = Create-NewPlan $UserRequest
}
```
```

2. **Coordination Message:**
```powershell
# Send plan to left hemisphere
$message = @{
    from = "RIGHT"
    to = "LEFT"
    type = "PLAN_READY"
    plan_file = "right-hemisphere/active-plan.yaml"
    timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
}

Add-CoordinationMessage $message
```

3. **Feedback Learning:**
```powershell
# Receive execution feedback
$feedback = Get-LatestCoordinationMessage -Type "EXECUTION_COMPLETE"

if ($feedback.success) {
    # Extract and store new pattern
    .\scripts\right-brain\extract-pattern.ps1 -SessionId $feedback.session_id
}
```

**Deliverables:**
- work-planner.md fully integrated with pattern system
- Tests pass for integration (Group 5: 7 tests)

**Validation:** Group 5 tests should pass (7 tests)

---

### Phase 5: Corpus Callosum Coordination (RED→GREEN→REFACTOR)
**Duration:** 1-2 hours
**TDD Approach:** Tests FIRST for message routing

**Using Week 2 TDD Automation:**
```powershell
# Full TDD cycle for coordination processor
.\scripts\left-brain\run-tdd-cycle.ps1 `
    -FeatureConfig "tests\fixtures\week3\coordination-processor-feature.yaml"
```

**Script to Create (TDD):**
1. `process-coordination.ps1` - Route messages between hemispheres

**Coordination Flow:**
```
RIGHT BRAIN                    CORPUS CALLOSUM                    LEFT BRAIN
    |                                 |                                |
    |----[PLAN_READY]--------------->|                                |
    |                                 |------[PLAN_READY]------------>|
    |                                 |                                |
    |                                 |<-----[PHASE_1_COMPLETE]-------|
    |<----[PHASE_1_COMPLETE]----------|                                |
    |                                 |                                |
    |----[APPROVE_PHASE_2]---------->|                                |
    |                                 |------[APPROVE_PHASE_2]------->|
```

**Message Schema:**
```json
{
  "message_id": "uuid",
  "from": "LEFT|RIGHT",
  "to": "LEFT|RIGHT",
  "type": "PLAN_READY|PHASE_COMPLETE|APPROVE_PHASE|FEEDBACK",
  "payload": {},
  "timestamp": "ISO8601"
}
```

**Deliverables:**
- Coordination processor with full test coverage
- Message validation and routing
- Tests pass for coordination (Group 6: 6 tests)

**Validation:** Group 6 tests should pass (6 tests)

---

### Phase 6: E2E Integration & Validation
**Duration:** 1-2 hours
**Goal:** All 49 tests passing (100%)

**End-to-End Test:**
```powershell
# Simulate full pattern-based planning workflow
$result = Test-PatternBasedPlanning `
    -Query "I want to add invoice export" `
    -ExpectPattern "export_feature"

# Verify:
# ✅ Pattern matched (similarity > 0.7)
# ✅ Workflow template generated
# ✅ Coordination messages sent
# ✅ Work planner used pattern
# ✅ All 49 tests passing
```

**Deliverables:**
- All Week 3 validation tests passing (Group 7: 5 tests)
- Total: 49/49 tests (100%)

**Validation:** Group 7 tests should pass (5 tests)

---

## 📝 TDD Workflow Summary

For EACH script in Week 3:

```
1. RED Phase:
   - Create tests FIRST (using Week 2 automation)
   - Run tests → Verify they FAIL
   - Log to execution-state.jsonl

2. GREEN Phase:
   - Implement minimum code to pass
   - Run tests → Verify they PASS
   - Log to execution-state.jsonl

3. REFACTOR Phase:
   - Optimize code while tests stay green
   - Run tests → Verify they STILL PASS
   - Log to execution-state.jsonl

4. Validation:
   - All tests green
   - Code committed
   - Pattern extracted for future use
```

---

## 🎯 Success Criteria

### Week 3 Complete When:

- [x] Pattern library infrastructure created (7 tests)
- [ ] Pattern matching scripts implemented (8 tests)
- [ ] Workflow template generation working (7 tests)
- [ ] Pattern learning functional (6 tests)
- [ ] Work planner integrated (7 tests)
- [ ] Corpus callosum coordination operational (6 tests)
- [ ] E2E pattern-based planning validated (5 tests)
- [ ] **ALL 49 tests passing (100%)**

### Capability Validation:

```markdown
#file:KDS/prompts/user/kds.md

I want to add invoice export functionality

Expected:
✅ RIGHT brain queries pattern library
✅ Finds similar "export_feature" pattern (87% match)
✅ Generates workflow from template
✅ Sends coordination message to LEFT
✅ LEFT brain executes using TDD automation
✅ Pattern extracted and stored
✅ Future "export" requests are faster!
```

---

## 💡 Key Insights

### Progressive Intelligence in Action:

1. **Week 1:** Brain structure created (hemispheres, corpus callosum)
2. **Week 2:** Left brain learned TDD automation
3. **Week 3:** Right brain uses LEFT's TDD to build pattern matching
4. **Meta-Learning:** Brain uses test-first to build its own intelligence!

### Benefits:

- 🚀 **Faster planning:** Pattern reuse vs. from-scratch
- 📊 **Better accuracy:** Proven workflows vs. untested
- 🧠 **Self-improvement:** Brain learns from every feature
- ✅ **Quality:** TDD ensures pattern matcher is tested

---

## 🚀 Next Steps

After Week 3 complete:
- Week 4: Cross-hemisphere learning (hemispheres teach each other)
- Week 5: Proactive intelligence (brain predicts issues)
- Week 6: Full autonomy (brain self-optimizes)

---

## 📊 Progress Tracking

Run validation test to track progress:

```powershell
.\tests\v6-progressive\week3-validation.ps1

# Current: 6/49 (12.2%)
# Target:  49/49 (100%)
```

**Let's build Week 3 using Week 2's TDD automation!** 🎉
