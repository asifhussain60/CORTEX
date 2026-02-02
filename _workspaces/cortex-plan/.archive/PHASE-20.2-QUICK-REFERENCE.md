# Phase 20.2: Orchestrator Visibility - Quick Reference

**Version:** 1.0 | **Status:** APPROVED ✅ | **Duration:** 9 hours | **Tests:** 43

---

## 🎯 What Is This?

**Orchestrator Activity Bar** — Visual indicators showing which orchestrator is handling your request, stage progress (4-stage flow), and intelligence activation (LENS/Knowledge synthesis). Designed as **TRAINING WHEELS** that can be toggled off once confidence is achieved.

**Philosophy:** Like training wheels on a bicycle — essential during learning, removable after mastery.

---

## 📊 The Problem

| Without Visibility | With Visibility |
|-------------------|-----------------|
| ❌ No idea which orchestrator engaged | ✅ See orchestrator type (🧪 TDD, 🔧 Fix) |
| ❌ Can't tell if LENS/knowledge active | ✅ See intelligence badges (🧠📚) |
| ❌ No stage progress feedback | ✅ See progress dots (●●○○) |
| ❌ Failures occur silently | ✅ Clear failure indicators (●●✗○ ⚠️) |
| ❌ Visibility becomes noise after mastery | ✅ Toggle off when confident |

---

## 🎨 Visual Design

### Response Header Examples

#### Full Visibility (Learning Phase)

```markdown
## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** 🧪 TDDOrchestrator ●●○○ 🧠📚 ✅

---
```

**Breakdown:**
- `🧪 TDDOrchestrator` — Orchestrator type with icon
- `●●○○` — Stage progress (2 of 4 complete)
- `🧠📚` — Intelligence active (LENS + Knowledge)
- `✅` — Success indicator

#### Failure Visibility

```markdown
## 🧠 CORTEX Refactoring
**Author:** Asif Hussain | **Orchestrator:** ♻️ RefactoringOrchestrator ●●✗○ ⚠️

---
```

**Breakdown:**
- `●●✗○` — Failed at stage 3
- `⚠️` — Failure indicator

#### Minimal Visibility (Mature Phase)

```markdown
## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅

---
```

**Breakdown:**
- No rich details (disabled mode)
- Only basic name and success indicator

---

## 🔧 Orchestrator Icons

| Orchestrator | Icon | Usage |
|-------------|------|-------|
| TDDOrchestrator | 🧪 | Test-first implementation |
| FixOrchestrator | 🔧 | Bug remediation |
| RefactoringOrchestrator | ♻️ | Code improvement |
| AnalysisOrchestrator | 🔍 | Code analysis |
| PlanningOrchestrator | 📋 | Feature planning |
| ConversationOrchestrator | 🤝 | Clarification dialog |
| DiscoveryOrchestrator | 🔎 | Feature discovery |
| DocumentationOrchestrator | 📚 | Documentation generation |
| ChallengeOrchestrator | 🎯 | Request enhancement |
| WorkflowOrchestrator | 🔄 | Workflow management |
| LENSOrchestrator | 🧠 | LENS intelligence |

---

## 📊 Stage Progress Indicators

| Display | Meaning |
|---------|---------|
| `●○○○` | Stage 1/4 (Comprehension) |
| `●●○○` | Stage 2/4 (Intent Classification) |
| `●●●○` | Stage 3/4 (Governance Check) |
| `●●●●` | Stage 4/4 (Execution Complete) |
| `●●✗○` | **Failure at Stage 3** |
| `✗○○○` | **Failure at Stage 1** |

### 4-Stage Flow Explained

1. **Comprehension** — Parse user request, extract intent
2. **Intent Classification** — Route to appropriate orchestrator
3. **Governance Check** — Validate against CORE rules
4. **Execution** — Execute orchestrated workflow

---

## 🧠 Intelligence Indicators

| Badge | Meaning |
|-------|---------|
| 🧠 | LENS analysis active (Git history, AST, comments) |
| 📚 | Knowledge synthesis active (45+ YAMLs) |
| 🧠📚 | Full intelligence (LENS + Company + CORTEX) |
| *(none)* | No intelligence layer |

---

## 🎛️ Visibility Modes (Training Wheels)

### Maturity Stages

| Stage | Request Count | Mode | Visibility |
|-------|--------------|------|-----------|
| **Learning** | 0-50 | `full` | ✅ Success details<br>✅ Failure details<br>✅ Intelligence badges<br>✅ Stage progress |
| **Transition** | 50-250 | `failure_only` | ❌ Success details<br>✅ Failure details<br>❌ Intelligence badges<br>✅ Stage progress |
| **Mature** | 250+ | `disabled` | ❌ Success details<br>❌ Failure details<br>❌ Intelligence badges<br>❌ Stage progress |

### Auto-Transition Logic

```python
# Automatically transitions based on usage patterns
request_count = 0       → "full" mode
request_count = 50      → "failure_only" mode
request_count = 250     → "disabled" mode (if 85% confidence achieved)
```

**Notification at 50 requests:**
> 🎓 **Orchestrator Mastery Progress**
> 
> You've made 50 requests with CORTEX! Orchestrator visibility will now
> focus on failures only. You can re-enable full details anytime.

**Notification at 250 requests:**
> 🏆 **Orchestrator Mastery Achieved!**
> 
> You've achieved 85% confidence in CORTEX orchestration patterns.
> Visibility is now disabled to reduce noise.

---

## 🔧 Manual Overrides

### Environment Variable (Highest Priority)

```bash
# Full visibility (override auto-detection)
export CORTEX_ORCHESTRATOR_VISIBILITY=full

# Failure-only mode (debugging)
export CORTEX_ORCHESTRATOR_VISIBILITY=failure_only

# Disabled mode (mature user)
export CORTEX_ORCHESTRATOR_VISIBILITY=disabled
```

### Configuration File (Medium Priority)

```yaml
# config/orchestrator_visibility.yaml
visibility:
  mode: "full"  # Options: full | failure_only | disabled
  auto_detect: true
  maturity_thresholds:
    learning_max: 50
    transition_max: 250

display:
  show_stage_progress: true
  show_intelligence: true
  show_success_details: true
  show_failure_details: true
```

### User Preference (Low Priority)

```yaml
# ~/.cortex/preferences.yaml
orchestrator_visibility:
  mode: "full"
```

### Precedence Order

1. **Environment Variable** (highest)
2. **Config File**
3. **User Preference**
4. **Auto-Detection** (lowest)

---

## 📐 Implementation Overview

### Files Changed

| File | Purpose | Tests |
|------|---------|-------|
| `cortex/brain/core/orchestrator_visibility_controller.py` | Visibility mode management | 15 |
| `cortex/brain/core/response_header_injector.py` | Badge generation | 18 |
| `cortex/brain/core/orchestrator_context.py` | Visibility field tracking | - |
| `config/orchestrator_visibility.yaml` | Configuration file | - |
| `tests/integration/test_orchestrator_visibility_integration.py` | End-to-end tests | 10 |

**Total:** 43 tests across 3 phases

---

## 🚀 Usage Examples

### Example 1: First-Time User (Learning Phase)

**Request:** `/implement user authentication`

**Response Header:**
```markdown
## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** 🧪 TDDOrchestrator ●●○○ 🧠📚 ✅
```

**What This Shows:**
- TDD orchestrator engaged (test-first implementation)
- Stage 2/4 (Intent Classification complete)
- Full intelligence active (LENS + Company Knowledge)
- Execution successful

---

### Example 2: Debugging Failure (Transition Phase)

**Request:** `/fix security vulnerability in auth.py`

**Response Header:**
```markdown
## 🧠 CORTEX Fix
**Author:** Asif Hussain | **Orchestrator:** 🔧 FixOrchestrator ●●✗○ ⚠️
```

**What This Shows:**
- Fix orchestrator engaged
- Failed at stage 3 (Governance Check)
- Failure indicator shown
- (Success details hidden in transition mode)

---

### Example 3: Mature User (Disabled Mode)

**Request:** `/refactor payment processing`

**Response Header:**
```markdown
## 🧠 CORTEX Refactoring
**Author:** Asif Hussain | **Orchestrator:** RefactoringOrchestrator ✅
```

**What This Shows:**
- Minimal visibility (disabled mode)
- Only basic name and success indicator
- No noise, clean interaction

---

## 🧪 Testing Strategy

### Unit Tests (33 tests)

**VisibilityController (15 tests):**
- Precedence order validation
- Maturity stage detection
- Mode determination logic
- User preference persistence
- Confidence score calculation

**ResponseHeaderInjector (18 tests):**
- Badge generation (full/failure_only/disabled)
- Stage progress formatting
- Intelligence badge formatting
- Icon mapping validation
- Orchestration context field population

### Integration Tests (10 tests)

**End-to-End Flow:**
- TDD orchestrator full visibility
- Fix orchestrator failure visibility
- Refactor orchestrator transition mode
- Analysis orchestrator disabled mode
- Maturity transitions (learning → transition → mature)
- Environment variable override
- User preference override
- LENS intelligence badge activation
- Knowledge synthesis badge activation

---

## ⚡ Performance Impact

| Operation | Time Complexity | Latency | Impact |
|-----------|----------------|---------|--------|
| Badge generation | O(1) | <1ms | Negligible |
| Visibility mode lookup | O(1) cached | <1ms | Negligible |
| **Total overhead** | - | **<2ms** | **<0.5%** |

**Optimization Strategies:**
- Cache visibility mode for session (5-minute TTL)
- Cache user request count (updated every 10 requests)
- Cache orchestrator icon mappings (static)
- Skip badge generation if disabled mode

---

## 🔄 Rollout Plan

### Phase 1: Foundation (3 hours)

**Tasks:**
- Implement `VisibilityController` class
- Add `config/orchestrator_visibility.yaml`
- Write 15 unit tests

**Deliverables:**
- `cortex/brain/core/orchestrator_visibility_controller.py`
- `config/orchestrator_visibility.yaml`
- `tests/unit/brain/core/test_orchestrator_visibility_controller.py`

---

### Phase 2: Response Header Enhancement (4 hours)

**Tasks:**
- Enhance `ResponseHeaderInjector` with badge methods
- Add `OrchestrationContext` visibility fields
- Write 18 unit tests

**Deliverables:**
- `cortex/brain/core/response_header_injector.py` (enhanced)
- `cortex/brain/core/orchestrator_context.py` (enhanced)
- `tests/unit/brain/core/test_response_header_injector_visibility.py`

---

### Phase 3: Integration (2 hours)

**Tasks:**
- Wire `VisibilityController` into `MasterOrchestrator`
- Update all orchestrators to populate visibility fields
- Write 10 integration tests

**Deliverables:**
- `cortex/orchestrators/core/master_orchestrator.py` (enhanced)
- `tests/integration/test_orchestrator_visibility_integration.py`

---

**Total Duration:** 9 hours  
**Total Tests:** 43 (15 + 18 + 10)

---

## 🔮 Future Enhancements (Post-MVP)

### Phase 2: MCP Progress Notifications

**Description:** Real-time stage progress via MCP JSON-RPC notifications

**Benefit:** Live updates during long-running operations (e.g., file analysis, test execution)

**Priority:** P2 Medium  
**Duration:** 2 weeks

---

### Phase 3: Interactive Dashboard

**Description:** Web-based orchestrator activity dashboard

**Features:**
- Real-time stage visualization
- Historical request timeline
- Orchestrator usage heatmap
- Intelligence activation patterns

**Priority:** P3 Low  
**Duration:** 4 weeks

---

## 🎓 Learning Path

### Week 1-2 (Learning Phase)

**Goal:** Build confidence in orchestrator patterns

**What You'll See:**
- Full orchestrator badges on every request
- Stage progress dots showing 4-stage flow
- Intelligence indicators (🧠📚) when LENS/Knowledge active
- Clear failure states with stage identification

**Tips:**
- Pay attention to which orchestrator engages for different request types
- Notice when intelligence layers activate (IMPLEMENT/FIX/REFACTOR/ANALYZE intents)
- Observe the 4-stage flow pattern: Comprehension → Intent → Governance → Execution

---

### Week 3-8 (Transition Phase)

**Goal:** Shift focus to failures, success becomes expected

**What You'll See:**
- Success details hidden (minimal badge)
- Failure details still shown (debugging focus)
- Stage progress retained for context
- Intelligence indicators hidden

**Tips:**
- Use failures to refine your request formulation
- Understand governance blocks (stage 3 failures)
- Notice consistency in orchestrator selection

---

### Week 9+ (Mature Phase)

**Goal:** Transparent background orchestration

**What You'll See:**
- Minimal visibility (name + status only)
- Clean, distraction-free interaction
- Orchestration is trusted background process

**Tips:**
- Re-enable full visibility anytime for debugging or teaching others
- Use environment variable for temporary visibility boost
- Celebrate mastery — you've achieved 85% confidence! 🏆

---

## 🛠️ Troubleshooting

### "I'm not seeing orchestrator details"

**Check visibility mode:**
```bash
# Check current mode
cat config/orchestrator_visibility.yaml | grep mode

# Check environment variable
echo $CORTEX_ORCHESTRATOR_VISIBILITY

# Check request count
cat ~/.cortex/usage_stats.yaml
```

**Solution:**
```bash
# Force full visibility
export CORTEX_ORCHESTRATOR_VISIBILITY=full
```

---

### "I want to disable visibility immediately"

**Solution:**
```bash
# Disable all visibility
export CORTEX_ORCHESTRATOR_VISIBILITY=disabled

# Or edit config file
vim config/orchestrator_visibility.yaml
# Set mode: "disabled"
```

---

### "I want failure-only mode permanently"

**Solution:**
```yaml
# ~/.cortex/preferences.yaml
orchestrator_visibility:
  mode: "failure_only"
```

---

## 📚 Key Concepts

### Training Wheels Philosophy

1. **ESSENTIAL during learning** — Provides safety and confidence
2. **REMOVABLE after mastery** — No longer needed, becomes hindrance
3. **GRADUAL transition** — Monitor usage, disable when ready

### Progressive Disclosure

- **Full details** (learning) → **Failure focus** (transition) → **Minimal noise** (mature)
- **User-controlled** transitions via environment variables or config files
- **Auto-detection** based on usage patterns and confidence scores

### Confidence Building

- **Transparency** → Visibility builds understanding
- **Feedback** → Stage progress shows system thinking
- **Trust** → Consistent patterns build confidence
- **Mastery** → Confidence enables removal of training wheels

---

## ✅ Success Criteria

| Criterion | Target | Validation |
|-----------|--------|------------|
| **Badge visibility** | 100% in learning phase | Manual testing (0-50 requests) |
| **Transition detection** | Auto-transition at 50 requests | Integration test |
| **Maturity detection** | Auto-disable at 250 requests (85% confidence) | Integration test |
| **Environment override** | Instant mode change | Unit test |
| **Performance impact** | <2ms overhead | Benchmark test |
| **Test coverage** | 43 tests passing | CI/CD pipeline |
| **User satisfaction** | >85% confidence score | Usage analytics |

---

## 🚀 Getting Started

### 1. Check Current Visibility Mode

```bash
cat config/orchestrator_visibility.yaml
```

### 2. Make First Request (Learning Phase)

```bash
/implement user authentication
```

**Expected Output:**
```markdown
## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** 🧪 TDDOrchestrator ●○○○ 🧠📚 ✅
```

### 3. Observe Stage Progression

Watch the progress dots update as stages complete:
- `●○○○` (Stage 1)
- `●●○○` (Stage 2)
- `●●●○` (Stage 3)
- `●●●●` (Stage 4)

### 4. Trigger Intelligence Layers

Intelligence activates for:
- **IMPLEMENT** intents → TDD orchestrator
- **FIX** intents → Fix orchestrator
- **REFACTOR** intents → Refactoring orchestrator
- **ANALYZE** intents → Analysis orchestrator

### 5. Notice Auto-Transition at 50 Requests

System automatically switches to `failure_only` mode.

### 6. Achieve Mastery at 250 Requests

System automatically disables visibility (if 85% confidence achieved).

---

## 📝 Quick Command Reference

```bash
# Full visibility (override auto-detection)
export CORTEX_ORCHESTRATOR_VISIBILITY=full

# Failure-only mode
export CORTEX_ORCHESTRATOR_VISIBILITY=failure_only

# Disable visibility
export CORTEX_ORCHESTRATOR_VISIBILITY=disabled

# Check current mode
cat config/orchestrator_visibility.yaml | grep mode

# Check request count
cat ~/.cortex/usage_stats.yaml

# Edit user preferences
vim ~/.cortex/preferences.yaml
```

---

## 📖 Related Documentation

- **[PHASE-20.2-ORCHESTRATOR-VISIBILITY.yaml](./PHASE-20.2-ORCHESTRATOR-VISIBILITY.yaml)** — Full technical specification
- **[PHASE-20-LENS-COMPANY-INTEGRATION.yaml](./PHASE-20-LENS-COMPANY-INTEGRATION.yaml)** — LENS + Company Knowledge (triggers intelligence badges)
- **[PHASE-20.5-KNOWLEDGE-SYNTHESIS.yaml](./PHASE-20.5-KNOWLEDGE-SYNTHESIS.yaml)** — Active knowledge synthesis (45+ YAMLs)
- **[cortex-plan-index.md](./cortex-plan-index.md)** — Master plan index

---

## 🎯 Bottom Line

**Orchestrator visibility is TRAINING WHEELS:**

✅ **During Learning:** Full visibility builds confidence and understanding  
✅ **During Transition:** Reduced noise focuses on failures only  
✅ **During Maturity:** Disabled for clean, distraction-free interaction  

**Key Innovation:** Adaptive visibility that responds to user mastery, not a one-size-fits-all solution.

---

*v1.0 — Phase 20.2 Quick Reference | Training Wheels for Orchestrator Mastery*
