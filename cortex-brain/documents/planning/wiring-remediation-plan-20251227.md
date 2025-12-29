# CORTEX Wiring Remediation Plan

**Created:** December 27, 2025  
**Author:** Asif Hussain  
**Status:** 🔧 Ready for Execution  
**Baseline Analysis:** unwired-components-analysis-20251227_142913.md

---

## 📊 Situation Analysis

**Current State:**
- **Total Components:** 119
- **Wired:** 44 (37.0%)
- **Unwired:** 75 (63.0%)

**Breakdown by Category:**
| Category | Total | Wired | Unwired | % Wired | Priority |
|----------|-------|-------|---------|---------|----------|
| **Orchestrators** | 46 | 18 | 28 | 39.1% | 🔥 CRITICAL |
| **Agents** | 10 | 2 | 8 | 20.0% | 🔥 HIGH |
| **Operation Modules** | 40 | 17 | 23 | 42.5% | ⚠️ MEDIUM |
| **Setup Modules** | 10 | 7 | 3 | 70.0% | 💡 LOW |
| **Plugins** | 13 | 0 | 13 | 0.0% | 💡 LOW |

---

## 🎯 Remediation Strategy

### Phased Approach (4 Phases)

**Phase 1: CRITICAL Orchestrators** (Week 1-2)
- Wire user-facing orchestrators with clear use cases
- Target: 12 high-value orchestrators
- Expected improvement: 37% → 47% overall wiring

**Phase 2: HIGH Agents** (Week 3)
- Wire agents with established AgentType enums
- Target: 5 core agents
- Expected improvement: 47% → 51% overall wiring

**Phase 3: MEDIUM Operation Modules** (Week 4)
- Link modules to parent operations
- Target: 15 high-impact modules
- Expected improvement: 51% → 63% overall wiring

**Phase 4: LOW Setup & Plugins** (Week 5)
- Wire remaining setup modules and plugins
- Target: 10 components
- Expected improvement: 63% → 71% overall wiring

---

## 🔥 Phase 1: Critical Orchestrators (12 Components)

### Priority 1A: User-Facing Operations (HIGH IMPACT)

#### 1. GitCheckpointOrchestrator ⭐⭐⭐
**File:** `src/orchestrators/git_checkpoint_orchestrator.py`  
**Use Case:** Automated git commits during TDD workflow (RED→GREEN→REFACTOR)  
**Wiring Tasks:**
- [ ] Add `git_checkpoint` operation to `cortex-operations.yaml`
  - Natural language: "git checkpoint", "commit progress", "save checkpoint"
  - Modules: `git_checkpoint_orchestrator`
  - Category: `development`
- [ ] Create response template in `response-templates-v4.yaml`
  - Expected orchestrator: `GitCheckpointOrchestrator`
  - Response profile: `operational`
- [ ] Add integration test: `tests/integration/test_git_checkpoint_wiring.py`
- [ ] Validate: `copilot chat "git checkpoint"`

**Time Estimate:** 2 hours  
**Dependencies:** None  
**Success Criteria:** Natural language command triggers orchestrator, commits created with proper messages

---

#### 2. SystemIntegrityOrchestrator ⭐⭐⭐
**File:** `src/orchestrators/system/system_integrity_orchestrator.py`  
**Use Case:** 8-phase integrity check (plan alignment, tests, docs, organization, repair, cleanup)  
**Wiring Tasks:**
- [ ] Verify `system_integrity` operation exists in `cortex-operations.yaml` (already present)
- [ ] Add response template in `response-templates-v4.yaml`
  - Expected orchestrator: `SystemIntegrityOrchestrator`
  - Triggers from operation: "system integrity", "validate system", "check integrity"
- [ ] Update deployment_tier to `admin` (already correct)
- [ ] Validate: `copilot chat "system integrity"`

**Time Estimate:** 1 hour  
**Dependencies:** Operation already defined, needs template wiring  
**Success Criteria:** Natural language triggers 8-phase workflow

---

#### 3. DesignSyncOrchestrator ⭐⭐⭐
**File:** `src/operations/modules/design_sync/design_sync_orchestrator.py`  
**Use Case:** Sync design documents with implementation reality  
**Wiring Tasks:**
- [ ] Add `design_sync` operation to `cortex-operations.yaml`
  - Natural language: "design sync", "sync design", "align design docs"
  - Modules: `design_sync_orchestrator`
  - Category: `documentation`
- [ ] Create response template
- [ ] Add integration test
- [ ] Validate: `copilot chat "design sync"`

**Time Estimate:** 2 hours  
**Dependencies:** None  
**Success Criteria:** Detects design/implementation gaps, generates sync reports

---

#### 4. DiagramRegenerationOrchestrator ⭐⭐
**File:** `src/operations/modules/diagrams/diagram_regeneration_orchestrator.py`  
**Use Case:** Regenerate architecture diagrams from code  
**Wiring Tasks:**
- [ ] Add `regenerate_diagrams` operation
  - Natural language: "regenerate diagrams", "update diagrams", "refresh architecture diagrams"
  - Modules: `diagram_regeneration_orchestrator`
  - Category: `documentation`
- [ ] Create response template
- [ ] Add integration test
- [ ] Validate: `copilot chat "regenerate diagrams"`

**Time Estimate:** 2 hours  
**Dependencies:** None  
**Success Criteria:** Diagrams updated from latest codebase

---

#### 5. ApplicationHealthOrchestrator ⭐⭐
**File:** `src/orchestrators/application_health_orchestrator.py`  
**Use Case:** Comprehensive application health monitoring  
**Wiring Tasks:**
- [ ] Add `app_health` operation
  - Natural language: "app health", "check application", "health status"
  - Modules: `application_health_orchestrator`
  - Category: `monitoring`
- [ ] Create response template
- [ ] Add integration test
- [ ] Validate: `copilot chat "app health"`

**Time Estimate:** 2 hours  
**Dependencies:** None  
**Success Criteria:** Returns health metrics, identifies issues

---

### Priority 1B: Internal Operations (MEDIUM IMPACT)

#### 6. VacuumOrchestrator ⭐
**File:** `src/operations/modules/vacuum/vacuum_orchestrator.py`  
**Use Case:** SQLite database optimization  
**Wiring Tasks:**
- [ ] Add `vacuum` operation
  - Natural language: "vacuum databases", "optimize db", "clean databases"
  - Modules: `vacuum_orchestrator`
  - Category: `maintenance`
- [ ] Create response template
- [ ] Validate: `copilot chat "vacuum databases"`

**Time Estimate:** 1.5 hours

---

#### 7-12. Additional Orchestrators (Lower Priority)
- HolisticCleanupOrchestrator (cleanup operation wrapper)
- UserCleanupOrchestrator (user-specific cleanup)
- PublishBranchOrchestrator (branch publishing automation)
- BrainTuningOrchestrator (brain optimization)
- VisionAPIValidationOrchestrator (Vision API testing)
- ArchitecturalReviewOrchestrator (architecture analysis)

**Time Estimate:** 1.5 hours each (9 hours total)

---

## 🔥 Phase 2: Core Agents (5 Components)

### Priority 2A: Agents with AgentType Enums

#### 1. ProfileAgent ⭐⭐⭐
**File:** `src/cortex_agents/profile_agent.py`  
**Status:** Has AgentType.PROFILE enum, NOT wired in AgentExecutor  
**Use Case:** User profiling and preference management  
**Wiring Tasks:**
- [ ] Add to `AgentExecutor._get_agent_instance()`:
  ```python
  elif agent_type == AgentType.PROFILE:
      agent = ProfileAgent(
          name="ProfileAgent",
          tier1_api=self.tier1,
          tier2_kg=self.tier2,
          tier3_context=self.tier3
      )
  ```
- [ ] Add intent routing in `IntentRouter` for "profile" keywords
- [ ] Create response template with `expected_agent: ProfileAgent`
- [ ] Add test: `tests/agents/test_profile_agent_wiring.py`
- [ ] Validate: Agent handles profile-related requests

**Time Estimate:** 2 hours  
**Success Criteria:** "show my profile" routes to ProfileAgent

---

#### 2. RCAAgent ⭐⭐
**File:** `src/cortex_agents/rca_agent.py`  
**Status:** Has AgentType enum, NOT wired in executor  
**Use Case:** Root cause analysis for issues  
**Wiring Tasks:**
- [ ] Add AgentType.RCA to executor
- [ ] Add intent routing for "root cause", "why did X fail"
- [ ] Create response template
- [ ] Add tests
- [ ] Validate: Issue analysis requests route to RCA

**Time Estimate:** 2 hours

---

#### 3-5. Additional Agents
- LearningCaptureAgent (conversation learning)
- ComplianceDashboardAgent (compliance monitoring)
- WelcomeBannerAgent (onboarding greeting)

**Time Estimate:** 1.5 hours each (4.5 hours total)

---

## ⚠️ Phase 3: Operation Modules (15 Components)

### Strategy: Link Modules to Parent Operations

**Approach:**
1. Identify parent operation for each module
2. Add module to `modules:` list in operation definition
3. Verify OperationFactory auto-registers class
4. Test operation execution includes module

### High-Impact Modules

#### 1. GitCheckpointModule ⭐⭐⭐
**File:** `src/operations/modules/git_checkpoint_module.py`  
**Parent Operation:** `git_checkpoint` (to be created in Phase 1)  
**Wiring Task:**
- [ ] Add to `git_checkpoint` operation modules list
- [ ] Verify class name follows convention (GitCheckpointModule)
- [ ] Test: Operation instantiates module

**Time Estimate:** 30 minutes

---

#### 2. RemoveObsoleteTestsModule ⭐⭐
**File:** `src/operations/modules/cleanup/remove_obsolete_tests_module.py`  
**Parent Operation:** `cleanup` or `system_integrity`  
**Time Estimate:** 30 minutes

---

#### 3-15. Additional Modules (Bulk Wiring)
- ConversationCaptureModule → `conversation_tracking`
- VacuumSQLiteDatabasesModule → `vacuum`
- RemoveOrphanedFilesModule → `cleanup`
- ClearPythonCacheModule → `cleanup`
- RemoveOldLogsModule → `cleanup`
- ScanTemporaryFilesModule → `cleanup`
- HardcodedDataCleanerModule → `refine`
- EnhancedFeedbackModule → `feedback_operation` (new)
- GenerateStoryChaptersModule → `story_generation` (new)
- RefreshDesignDocsModule → `design_sync`
- ContextDisplayModule → `context_management` (new)
- AdminDashboardLauncherModule → `dashboard_launcher`
- GenerateImagePromptsModule → `story_generation`
- DeployDocsPreviewModule → `docs_preview` (new)

**Time Estimate:** 30 minutes each (6.5 hours total)

---

## 💡 Phase 4: Setup Modules & Plugins (16 Components)

### Setup Modules (3)

#### 1. UserProfileModule
**File:** `src/setup/modules/user_profile_module.py`  
**Wiring Tasks:**
- [ ] Add import to `src/setup/module_factory.py`
- [ ] Register: `register_module_class('user_profile', UserProfileModule)`
- [ ] Add to `src/setup/setup_modules.yaml`:
  ```yaml
  - module_id: user_profile
    name: User Profile Setup
    phase: CORE
    priority: 5
    dependencies: []
  ```
- [ ] Test: `setup_orchestrator` loads module

**Time Estimate:** 1 hour

---

#### 2-3. Additional Setup Modules
- PathConfigurationModule
- PythonEnvironmentModule

**Time Estimate:** 1 hour each (2 hours total)

---

### Plugins (13) - DEFERRED

**Rationale:** Plugins require deeper architectural review:
- Current plugin system may need refactoring
- 0% wiring suggests systemic issue, not individual plugin problems
- Recommend separate investigation into plugin architecture

**Action:** Create separate task: "Plugin System Architecture Review"

---

## 📋 Implementation Checklist Template

For each component, use this checklist:

### Orchestrator Wiring
- [ ] **cortex-operations.yaml**: Add operation definition
  - operation_id
  - name
  - description
  - natural_language triggers
  - modules list
  - category
  - deployment_tier
  - execution_method
- [ ] **response-templates-v4.yaml**: Add template
  - expected_orchestrator: ClassName
  - response_profile: operational/strategic
  - triggers list
- [ ] **Integration Test**: Create test file
  - Test natural language routing
  - Test orchestrator instantiation
  - Test basic execution
- [ ] **Manual Validation**: Copilot Chat command
- [ ] **Documentation**: Update operation guide

### Agent Wiring
- [ ] **AgentType Enum**: Add if missing
- [ ] **AgentExecutor**: Add to `_get_agent_instance()`
- [ ] **IntentRouter**: Add routing triggers
- [ ] **Response Template**: Add template with expected_agent
- [ ] **Agent Test**: Create test file
- [ ] **Manual Validation**: Test routing decision
- [ ] **Documentation**: Update agent guide

### Module Wiring
- [ ] **Parent Operation**: Identify or create
- [ ] **cortex-operations.yaml**: Add to modules list
- [ ] **Class Name**: Verify naming convention
- [ ] **Metadata**: Verify module_id
- [ ] **Factory Test**: Verify auto-registration
- [ ] **Execution Test**: Test module executes in operation

---

## 🎖️ Success Metrics

### Per Phase
| Phase | Target Wiring % | Components Wired | Time Budget |
|-------|----------------|------------------|-------------|
| Phase 1 | 47% (+10%) | 12 orchestrators | 16 hours |
| Phase 2 | 51% (+4%) | 5 agents | 10 hours |
| Phase 3 | 63% (+12%) | 15 modules | 8 hours |
| Phase 4 | 71% (+8%) | 3 setup modules | 3 hours |
| **TOTAL** | **71%** | **35 components** | **37 hours** |

### Overall Goals
- **Primary:** 71% wiring coverage (44 → 79 components)
- **Stretch:** 80% wiring coverage (95 components)
- **Quality:** All wired components validated with tests
- **Documentation:** Wiring guide and troubleshooting doc created

---

## 🚨 Risk Mitigation

### Risks

1. **Breaking Existing Functionality**
   - Mitigation: Run full test suite after each phase
   - Rollback: Git checkpoint before each wiring batch

2. **Circular Dependencies**
   - Mitigation: Wire in dependency order
   - Resolution: Use lazy loading where needed

3. **Performance Degradation**
   - Mitigation: Monitor component load times
   - Resolution: Implement caching for registries

4. **Template Conflicts**
   - Mitigation: Check for duplicate triggers before adding
   - Resolution: Use more specific natural language patterns

---

## 🔄 Validation Process

### After Each Component
1. Run component-specific tests
2. Test natural language routing
3. Verify no import errors
4. Check logs for warnings

### After Each Phase
1. Run full test suite: `pytest tests/`
2. Run align utility: `align validate_feature_wiring`
3. Test 5 random natural language commands
4. Review wiring coverage report
5. Git checkpoint: "Phase N wiring complete"

### Final Validation
1. Generate new wiring analysis report
2. Compare baseline vs. final metrics
3. Test all newly wired components
4. Update deployment manifest
5. Document lessons learned

---

## 📚 Documentation Deliverables

1. **Wiring Best Practices Guide**
   - `cortex-brain/documents/guides/component-wiring-guide.md`
   - Standards for orchestrator/agent/module wiring
   - Common pitfalls and solutions

2. **Troubleshooting Guide**
   - `cortex-brain/documents/guides/unwired-component-detection.md`
   - How to detect unwired components
   - How to diagnose wiring issues

3. **CI/CD Integration**
   - Add wiring validation to deployment gates
   - Automated wiring coverage reporting

4. **Lessons Learned**
   - Update `cortex-brain/lessons-learned.yaml`
   - Capture insights for future development

---

## 🎯 Next Steps

1. **Review & Approve Plan** (this document)
2. **Start Phase 1** (Critical Orchestrators)
   - Begin with GitCheckpointOrchestrator (highest impact)
   - Complete Priority 1A before moving to 1B
3. **Track Progress** via todo list
4. **Update Plan** as needed based on discoveries
5. **Celebrate Milestones** 🎉

---

**Plan Status:** ✅ READY FOR EXECUTION  
**Total Estimated Time:** 37 hours (1 week with full focus)  
**Expected Outcome:** 37% → 71% wiring coverage (+34% improvement)
