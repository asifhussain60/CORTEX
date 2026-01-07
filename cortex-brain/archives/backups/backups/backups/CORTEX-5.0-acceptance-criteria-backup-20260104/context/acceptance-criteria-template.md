# Phase-Level Acceptance Criteria Template

**Purpose:** Define clear DoR (Definition of Ready) and DoD (Definition of Done) validation checkpoints for each phase within CORTEX sub-plans.

**Created:** January 4, 2026  
**Author:** Asif Hussain  
**Applies To:** All CORTEX-5.0 sub-plans

---

## 📋 Template Structure

### Phase Template

```markdown
## Phase {N}: {Phase Name}

**Duration:** {Estimated Hours/Days}  
**Dependencies:** {Previous Phase or Prerequisites}  
**Governance Checkpoint:** {Yes/No - if yes, specify Tier 0/Tier 2 consultation}

### Definition of Ready (DoR)

**Entry Criteria - ALL must be true before phase can begin:**

- [ ] {Criterion 1 - specific, measurable}
- [ ] {Criterion 2 - specific, measurable}
- [ ] {Criterion 3 - specific, measurable}
- [ ] Governance consultation complete (if applicable)
- [ ] Previous phase DoD validated
- [ ] Required resources/tools available

**DoR Validation:** 
- Automated: {Script/Command to verify}
- Manual: {Checklist/Review process}

### Implementation Tasks

1. {Task 1 with acceptance criterion}
   - **AC:** {What success looks like}
   
2. {Task 2 with acceptance criterion}
   - **AC:** {What success looks like}

### Definition of Done (DoD)

**Exit Criteria - ALL must be true before phase completes:**

- [ ] {Criterion 1 - specific, measurable, testable}
- [ ] {Criterion 2 - specific, measurable, testable}
- [ ] {Criterion 3 - specific, measurable, testable}
- [ ] All implementation tasks complete
- [ ] Tests written and passing (if code phase)
- [ ] Documentation updated
- [ ] Governance validation passed (if applicable)
- [ ] Code reviewed (if applicable)
- [ ] Artifacts committed to git

**DoD Validation:**
- Automated: {Test suite/Script to verify}
- Manual: {Review/Sign-off process}

### Artifacts Generated

- `{artifact-1-path}` - {Description}
- `{artifact-2-path}` - {Description}

### Rollback Plan (if phase fails)

- {Step to undo phase changes}
- {How to return to previous stable state}
```

---

## 📝 Concrete Example: Sub-Plan 03 Phase 1

```markdown
## Phase 1: Governance Query Utilities Implementation

**Duration:** 4-6 hours  
**Dependencies:** None (foundation phase)  
**Governance Checkpoint:** Yes - Tier 0 consultation required

### Definition of Ready (DoR)

**Entry Criteria:**

- [x] `brain-protection-rules.yaml` accessible
- [x] `knowledge-graph.yaml` accessible
- [x] `lessons-learned.yaml` accessible
- [x] Tier 0 governance query requirements understood
- [x] Test framework (pytest) configured
- [x] Python environment with PyYAML installed

**DoR Validation:**
- Automated: `python -c "import yaml; print('PyYAML OK')"`
- Manual: Verify all YAML files exist and are valid

### Implementation Tasks

1. Create `governance_query_utils.py` module
   - **AC:** Module exports `query_tier0()`, `query_tier2()`, `query_lessons_learned()` functions
   
2. Implement Tier 0 query function
   - **AC:** Function accepts `rule_category` parameter, returns list of matching rules
   
3. Implement Tier 2 query function
   - **AC:** Function accepts `pattern_name` parameter, returns related knowledge graph entries
   
4. Implement lessons-learned query
   - **AC:** Function accepts `feature_name` parameter, returns past learnings

5. Write comprehensive tests
   - **AC:** ≥90% coverage for governance_query_utils.py

### Definition of Done (DoD)

**Exit Criteria:**

- [x] `governance_query_utils.py` created (120+ lines)
- [x] All 3 query functions implemented
- [x] Test coverage ≥90% (test_governance_query_utils.py)
- [x] All tests passing (pytest exit code 0)
- [x] Type hints added (mypy validation passing)
- [x] Docstrings for all public functions
- [x] Governance checkpoint: Tier 0 validation confirms no rule violations
- [x] Code review completed (if team size >1)
- [x] Committed to git with message: "Phase 1: Governance Query Utilities"

**DoD Validation:**
- Automated: `pytest tests/governance/test_governance_query_utils.py -v --cov`
- Manual: Code review checklist completed

### Artifacts Generated

- `src/governance/governance_query_utils.py` - Core query utilities
- `tests/governance/test_governance_query_utils.py` - 15+ test cases
- `context/phase-1-governance-consultation.md` - Tier 0 validation report

### Rollback Plan

1. `git reset --hard HEAD~1` (if committed)
2. Delete `governance_query_utils.py` and tests
3. Return to Phase 0 Discovery
```

---

## 🛡️ Governance Integration

### When to Add Governance Checkpoints

**REQUIRED for these phase types:**
- File creation/modification phases (Tier 0: `HOLISTIC_DISCOVERY`, `GIT_ISOLATION`)
- Architecture changes (Tier 0: `PLANNING_ISOLATION`, `DOCUMENT_ORGANIZATION`)
- Test implementation (Tier 0: `TDD_ENFORCEMENT`)
- Refactoring phases (Tier 0: `REFACTOR_CLEANUP`)

**Governance DoR/DoD Template:**

```markdown
### Governance Validation (DoR)

- [ ] Tier 0 rules consulted: {list applicable rule IDs}
- [ ] No blocking violations detected
- [ ] Knowledge graph queried for similar patterns
- [ ] Lessons learned reviewed

### Governance Validation (DoD)

- [ ] Tier 0 validation passed
- [ ] No new governance violations introduced
- [ ] Knowledge graph updated (if applicable)
- [ ] Lessons learned updated (if applicable)
```

---

## 📊 Acceptance Criteria Quality Checklist

**Use this to validate your phase AC are high-quality:**

- [ ] **Specific:** No vague terms like "good", "sufficient", "adequate"
- [ ] **Measurable:** Includes numbers, percentages, or clear binary states
- [ ] **Testable:** Can be verified via automated test or reproducible manual check
- [ ] **Achievable:** Can be completed within phase duration estimate
- [ ] **Relevant:** Directly contributes to sub-plan goal
- [ ] **Time-bound:** Phase duration is realistic
- [ ] **SMART compliant:** Combines all above attributes

### Anti-Patterns to Avoid

❌ "Code is clean" → ✅ "Code passes linting (flake8) with 0 errors"  
❌ "Tests are good" → ✅ "Test coverage ≥80% with 0 failing tests"  
❌ "Documentation exists" → ✅ "README.md contains usage examples, API reference, and troubleshooting section"  
❌ "Performance is acceptable" → ✅ "API response time p95 <200ms under 1000 req/s load"

---

## 🔄 Continuous Validation

### Runtime Governance (NEW - Enhancement #1)

For phases that modify code, add runtime governance checks:

```python
# At start of phase
governance_result = governance_checkpoint(
    phase_name="Phase 1",
    operation_type="file_creation",
    target_files=["src/governance/governance_query_utils.py"]
)

if not governance_result.passed:
    raise GovernanceViolationError(governance_result.violations)

# At end of phase
final_validation = governance_checkpoint(
    phase_name="Phase 1",
    operation_type="phase_completion",
    artifacts=phase_artifacts
)
```

### AC Validation Agent (Enhancement #3)

For critical phases, run AC validation agent:

```bash
# After phase completion
python src/agents/ac_validator_agent.py \
    --phase "Phase 1" \
    --sub-plan "03-knowledge-library-phase" \
    --criteria-file "context/acceptance-criteria.md"
```

---

## 📝 Usage Instructions

### For Plan Authors

1. **Copy template** above for each phase in your sub-plan
2. **Fill in specifics** - replace `{placeholders}` with actual values
3. **Add governance checkpoints** if phase modifies files/architecture
4. **Review against quality checklist** to ensure AC are SMART
5. **Validate DoR before starting** phase
6. **Validate DoD before marking complete**

### For Plan Executors

1. **Check DoR** before starting work
2. **Execute tasks** in order
3. **Run validation** after each task
4. **Check DoD** before marking phase complete
5. **Generate artifacts** and commit to git
6. **Update progress tracker** with phase completion

### For Reviewers

1. **Verify DoR** was checked before phase started
2. **Validate DoD** checklist is 100% complete
3. **Run automated validation** scripts
4. **Review artifacts** for quality
5. **Approve phase completion** if all criteria met

---

## 📚 References

- **CORTEX-5.0 Master Plan:** `00-MASTER-REMEDIATION-PLAN.md` (Epic-level AC)
- **Planning System v5 Manifest:** `planning-system-5.0-manifest.yaml` (Phase structure)
- **Brain Protection Rules:** `brain-protection-rules.yaml` (Governance reference)
- **Response Templates:** `response-templates-v4.yaml` (DoR/DoD formatting)

---

**Last Updated:** January 4, 2026  
**Maintained By:** CORTEX Planning System v5  
**Status:** ✅ TEMPLATE READY FOR USE
