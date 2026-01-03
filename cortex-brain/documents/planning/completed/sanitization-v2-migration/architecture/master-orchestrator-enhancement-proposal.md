# Master Orchestrator Enhancement for Holistic Review Architecture

**Document:** Architecture Enhancement Proposal  
**Date:** January 3, 2026  
**Status:** 🆕 PROPOSED  
**Impact:** Master Orchestrator, Planning System v5, All v2 Orchestrators

---

## 🎯 Proposal Summary

Enhance Master Orchestrator to **automatically trigger holistic reviews** at strategic points during orchestrator execution, making the review-driven architecture systematic rather than manual.

**Current State:** Holistic reviews are manually triggered (phase-by-phase in plan execution)  
**Proposed State:** Master Orchestrator intercepts phase transitions and triggers reviews automatically

---

## 🏗️ Architecture Enhancement

### Current Flow (Manual Reviews)

```
User: "continue with sanitization-v2-migration"
  ↓
Master Orchestrator routes to Planning v5
  ↓
Planning v5 reads progress.json (phase 1 complete)
  ↓
Planning v5 executes phase 2
  ↓
**USER MUST MANUALLY** trigger Review #2
  ↓
Planning v5 continues with phase 3
```

### Enhanced Flow (Automatic Reviews)

```
User: "continue with sanitization-v2-migration"
  ↓
Master Orchestrator routes to Planning v5
  ↓
Planning v5 reads progress.json (phase 1 complete)
  ↓
**Master Orchestrator intercepts** (phase transition detected)
  ↓
Master Orchestrator checks review schedule in progress.json
  ↓
**AUTO-TRIGGER Review #2** (holistic-review-02 pending)
  ↓
HolisticReviewOrchestrator executes review
  ↓
Master Orchestrator returns control to Planning v5
  ↓
Planning v5 continues with phase 2 (with review insights)
```

---

## 🔧 Implementation Design

### 1. HolisticReviewOrchestrator (New Component)

**File:** `src/orchestrators/holistic_review_orchestrator.py`

```python
class HolisticReviewOrchestrator(BaseOrchestratorV4_1):
    """
    Autonomous orchestrator for holistic reviews.
    
    Triggered automatically by Master Orchestrator at phase transitions.
    Reviews all completed work and generates recommendations for future phases.
    
    Workflow:
        1. GATHER - Collect artifacts from completed phases/migrations
        2. ANALYZE - Extract patterns, identify reuse opportunities
        3. RECOMMEND - Generate architecture recommendations
        4. DOCUMENT - Create holistic-review-{N}.md report
        5. INJECT - Add insights to orchestrator context
    """
    
    def execute(self, context: Dict[str, Any]) -> OrchestratorResult:
        """
        Execute holistic review.
        
        Args:
            context:
                - parent_plan_id: Plan being reviewed
                - review_number: Which review (1-5)
                - completed_phases: List of completed phase numbers
                - target_phase: Next phase to execute
                - review_scope: What to analyze (design/implementation/config/etc)
        
        Returns:
            OrchestratorResult with:
                - review_document: Path to holistic-review-{N}.md
                - insights: List of actionable recommendations
                - architectural_improvements: System-wide suggestions
                - code_reuse_opportunities: Identified reusable components
        """
```

**Key Features:**
- ✅ Analyzes all completed work (past phases, sibling migrations)
- ✅ Extracts architectural patterns
- ✅ Identifies code reuse opportunities
- ✅ Generates recommendations for future phases
- ✅ Documents findings in `architecture/holistic-review-{N}.md`
- ✅ Injects insights into next phase's context

---

### 2. Master Orchestrator Enhancement

**File:** `src/orchestrators/master_orchestrator.py` (enhanced)

**New Method:**
```python
def _check_review_schedule(
    self, 
    orchestrator_id: str, 
    context: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Check if holistic review is needed before next phase.
    
    Args:
        orchestrator_id: Current orchestrator being executed
        context: Execution context with progress.json data
    
    Returns:
        Review configuration if review needed, None otherwise
    
    Logic:
        1. Check if orchestrator has review schedule (progress.json)
        2. Compare current phase vs last review
        3. If review pending for next phase → return review config
        4. Otherwise → return None (proceed normally)
    """
    # Check if progress.json has holistic_reviews section
    progress = context.get('progress', {})
    reviews = progress.get('holistic_reviews', {})
    
    if not reviews.get('enabled', False):
        return None  # Reviews not configured
    
    schedule = reviews.get('schedule', [])
    current_phase = progress.get('current_phase', 0)
    
    # Find next pending review
    for review in schedule:
        if review['status'] == 'not_started':
            # Check if review should trigger before next phase
            if self._should_trigger_review(review, current_phase):
                return {
                    'review_number': review['review_number'],
                    'review_name': review['name'],
                    'document_path': review['document'],
                    'scope': review['purpose']
                }
    
    return None
```

**Enhanced `handle_request` Method:**
```python
def handle_request(
    self,
    user_input: str,
    context: Optional[Dict[str, Any]] = None
) -> ExecutionResult:
    """Enhanced with automatic review triggering."""
    
    # [... existing context enrichment ...]
    
    # STEP 3: Route to orchestrator
    match = self.route_request(user_input, enriched_context)
    
    # **NEW: Check if holistic review needed**
    review_config = self._check_review_schedule(
        match.orchestrator_id, 
        enriched_context
    )
    
    if review_config:
        self.logger.info(
            f"Holistic review #{review_config['review_number']} triggered "
            f"before {match.orchestrator_id}"
        )
        
        # Execute holistic review FIRST
        review_result = self.execute_orchestrator(
            orchestrator_id="holistic_review_orchestrator",
            params={
                'parent_plan_id': enriched_context.get('plan_id'),
                'review_number': review_config['review_number'],
                'review_name': review_config['review_name'],
                'document_path': review_config['document_path'],
                'scope': review_config['scope'],
                'completed_phases': enriched_context.get('completed_phases', [])
            },
            context=enriched_context
        )
        
        # Inject review insights into context
        enriched_context['review_insights'] = review_result.artifacts.get('insights', [])
        enriched_context['last_review'] = review_config['review_number']
    
    # STEP 4: Execute target orchestrator (with review insights)
    result = self.execute_orchestrator(
        orchestrator_id=match.orchestrator_id,
        params={...},
        context=enriched_context  # Now includes review insights
    )
    
    return result
```

---

### 3. Progress Tracking Schema Enhancement

**File:** `progress.json` (schema enhancement)

**New Section:**
```json
{
  "holistic_reviews": {
    "enabled": true,
    "auto_trigger": true,
    "schedule": [
      {
        "review_number": 1,
        "name": "Before Design Phase",
        "trigger_condition": "phase_0_complete",
        "status": "completed",
        "document": "architecture/holistic-review-01.md",
        "insights_injected": true
      },
      {
        "review_number": 2,
        "name": "Before Implementation Phase",
        "trigger_condition": "phase_1_complete",
        "status": "not_started",
        "document": "architecture/holistic-review-02.md",
        "auto_trigger_enabled": true
      }
    ]
  }
}
```

**Trigger Conditions:**
```yaml
phase_0_complete:      # Review #1
  - current_phase >= 1
  - review_1_status != 'completed'
  
phase_1_complete:      # Review #2
  - current_phase >= 2
  - review_2_status != 'completed'
  
phase_3_complete:      # Review #3
  - current_phase >= 4
  - review_3_status != 'completed'
```

---

### 4. Configuration Enhancement

**File:** `cortex-brain/config/master-orchestrator.yaml`

**New Section:**
```yaml
# Holistic Review Configuration
holistic_reviews:
  enabled: true
  auto_trigger: true
  orchestrator: "holistic_review_orchestrator"
  priority: 5  # Higher than any other orchestrator (runs first)
  
  trigger_logic:
    - condition: "phase_transition"
      action: "check_review_schedule"
    - condition: "review_pending"
      action: "execute_review_before_phase"
    - condition: "review_complete"
      action: "inject_insights_to_context"
  
  review_context_sources:
    - "completed_phases_artifacts"
    - "sibling_migrations_reports"
    - "parent_plan_context"
    - "knowledge_graph_patterns"
```

---

## 🎯 Benefits

### 1. **Automation**
- ❌ **Before:** User must manually trigger reviews between phases
- ✅ **After:** Reviews trigger automatically at phase transitions

### 2. **Consistency**
- ❌ **Before:** Reviews might be skipped if user forgets
- ✅ **After:** All reviews guaranteed to execute per schedule

### 3. **Context Injection**
- ❌ **Before:** Review insights must be manually read and applied
- ✅ **After:** Insights automatically injected into orchestrator context

### 4. **Pattern Extraction**
- ❌ **Before:** Patterns identified but not systematically applied
- ✅ **After:** Patterns automatically inform future phase execution

### 5. **Architectural Consistency**
- ❌ **Before:** Each phase designed independently
- ✅ **After:** Each phase informed by holistic analysis

---

## 📊 Example Execution Flow

### User Request: "continue with sanitization-v2-migration"

```
[Master Orchestrator] Handling request: "continue with sanitization-v2-migration"
  ↓
[Context Middleware] Loading last 3 sessions... (200 tokens)
  ↓
[Pattern Router] Matched: planning_v5 (continuation detected)
  ↓
[Master Orchestrator] Loading progress.json for sanitization-v2-migration
  ↓
[Review Checker] Current phase: 1 (Design complete)
                 Next phase: 2 (Implementation)
                 Review #2 status: not_started
                 **TRIGGER CONDITION MET**
  ↓
[Master Orchestrator] Auto-triggering Holistic Review #2...
  ↓
[HolisticReviewOrchestrator] EXECUTING REVIEW #2
  ├── PHASE 1: GATHER
  │   ├── Loading Cleanup v2 implementation (800 lines)
  │   ├── Loading Vacuum v2 implementation (2,442 lines)
  │   ├── Loading Sanitization v2 design documents
  │   └── Loading parent plan context
  ├── PHASE 2: ANALYZE
  │   ├── Extracting engine patterns (5 engines × 3 migrations)
  │   ├── Identifying reusable components (FilesystemEngine, SafetyValidator)
  │   ├── Comparing transactional approaches
  │   └── Analyzing test coverage patterns
  ├── PHASE 3: RECOMMEND
  │   ├── Recommendation #1: Reuse FilesystemEngine::create_checkpoint()
  │   ├── Recommendation #2: Extend SafetyValidator for sanitization risks
  │   ├── Recommendation #3: Adopt progressive analysis pattern
  │   └── Recommendation #4: Follow 95%+ coverage standard
  ├── PHASE 4: DOCUMENT
  │   └── Created: architecture/holistic-review-02.md (350 lines)
  └── PHASE 5: INJECT
      └── Added 8 insights to orchestrator context
  ↓
[Master Orchestrator] Review #2 complete in 45s
                      Injecting insights into Planning v5 context...
  ↓
[Planning v5] Resuming Phase 2 (Implementation)
              **Context now includes review insights:**
              - insight_1: "Reuse FilesystemEngine::create_checkpoint()"
              - insight_2: "Extend SafetyValidator class"
              - insight_3: "Progressive analysis: quick→AST→deep"
              ...
  ↓
[Planning v5] Implementing SanitizationOrchestratorV2 (applying insights)
  ↓
[Result] Implementation uses checkpoint system from Vacuum v2 ✅
         Implementation extends SafetyValidator ✅
         Implementation follows progressive analysis ✅
```

---

## 🚀 Implementation Plan

### Phase 1: Core Infrastructure (4 hours)
1. Create `HolisticReviewOrchestrator` class
2. Implement 5-phase review workflow
3. Add review schedule parser

### Phase 2: Master Orchestrator Integration (3 hours)
4. Add `_check_review_schedule()` method
5. Enhance `handle_request()` with review triggering
6. Implement context injection logic

### Phase 3: Configuration & Testing (2 hours)
7. Update `master-orchestrator.yaml` with review config
8. Create unit tests for review triggering
9. Create integration tests for end-to-end flow

### Phase 4: Documentation & Rollout (1 hour)
10. Update CORTEX.prompt.md with review orchestrator
11. Create holistic-review-orchestrator-manifest.yaml
12. Document usage in planning-system-4.0-manifest.yaml

**Total:** 10 hours

---

## ✅ Success Criteria

1. **Automatic Triggering**
   - ✅ Reviews trigger automatically at phase transitions
   - ✅ No manual intervention required

2. **Context Injection**
   - ✅ Review insights appear in orchestrator context
   - ✅ Insights accessible to all phase execution logic

3. **Architectural Consistency**
   - ✅ All migrations use consistent patterns
   - ✅ Code reuse opportunities identified and applied

4. **Documentation Quality**
   - ✅ Each review generates 300-500 line document
   - ✅ Documents include patterns, recommendations, code samples

5. **Performance**
   - ✅ Review execution < 1 minute
   - ✅ Context injection adds < 500 tokens
   - ✅ No impact on orchestrator execution speed

---

## 🎯 Next Steps

1. **Approve Enhancement** - Confirm this approach aligns with CORTEX v5 vision
2. **Update Sanitization Plan** - Add HolisticReviewOrchestrator to Phase 1.5, 3.5, 5.5, 7.5
3. **Implement Core** - Build HolisticReviewOrchestrator (Phase 1)
4. **Integrate Master Orch** - Add review triggering logic (Phase 2)
5. **Test End-to-End** - Validate on Sanitization v2 migration
6. **Rollout System-Wide** - Apply to all future v2 migrations

---

## 📋 Decision Required

**Question:** Should we implement automatic holistic reviews in Master Orchestrator?

**Option A:** ✅ **Implement Now** (Recommended)
- Pros: Systematic, consistent, automated
- Cons: 10 hours development time
- Impact: All future migrations benefit

**Option B:** ⏸️ **Manual Reviews** (Current Approach)
- Pros: No development time
- Cons: Manual, inconsistent, can be forgotten
- Impact: Quality depends on user discipline

**Recommendation:** **Option A (Implement Now)**  
Rationale: The 10-hour investment pays off immediately in Sanitization v2 and all future migrations (Debug v2, Phase 8-10 migrations). Automated reviews ensure architectural consistency and pattern extraction that would otherwise be missed.

---

**Status:** 🆕 AWAITING APPROVAL  
**Impact:** HIGH (affects all future migrations)  
**Complexity:** MEDIUM (well-defined interfaces)  
**Risk:** LOW (additive enhancement, doesn't break existing flow)
