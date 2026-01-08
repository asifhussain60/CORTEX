# Phase 1: Knowledge Extension Layer

**Epic:** cortex5-enhancement-epic-v2  
**Phase:** 1 of 11  
**Track:** Track 1 (Core Intelligence)  
**Duration:** 2 weeks  
**Dependencies:** None (foundation phase)  
**Status:** 🟡 NOT STARTED

---

## 🎯 Phase Objective

**Goal:** Enable CORTEX to integrate company-specific knowledge (architecture guides, tech stacks, API catalogs, coding standards) without corrupting CORTEX core capabilities.

**Why This Matters:**  
Companies need CORTEX to understand their specific technology choices (e.g., .NET instead of Python, Azure instead of AWS, company-specific API patterns). Without this phase, CORTEX generates Python-based solutions even when the company uses .NET.

---

## 📋 Deliverables

### 1. Company Knowledge Folder Structure

**Location:** `cortex-brain/tier2/company-knowledge/{company-id}/`

**Structure:**
```
company-knowledge/
├── company_abc/
│   ├── architecture.md          # Architecture patterns & principles
│   ├── tech-stack.yaml          # Technology stack (languages, frameworks, tools)
│   ├── api-catalog.json         # Internal API inventory
│   ├── coding-standards.md      # Coding standards & best practices
│   └── governance.yaml          # Company-specific governance rules
└── company_xyz/
    └── ... (same structure)
```

**Success Criteria:**
- ✅ Folder structure created
- ✅ Schema validated (architecture.md, tech-stack.yaml required)
- ✅ Sample company (company_abc) created with realistic data

### 2. CompanyKnowledgeProvider Implementation

**File:** `src/knowledge/company_knowledge_provider.py`

**Class:** `CompanyKnowledgeProvider`

**Methods:**
```python
query_architecture(company_id: str, topic: str) -> Dict
query_tech_stack(company_id: str) -> Dict
query_api_catalog(company_id: str, api_name: Optional[str]) -> List[Dict]
query_coding_standards(company_id: str, language: str) -> Dict
merge_with_cortex_knowledge(cortex_knowledge: Dict, company_knowledge: Dict) -> Dict
```

**Success Criteria:**
- ✅ Class queries company knowledge files
- ✅ Returns structured data (not raw Markdown)
- ✅ Handles missing company gracefully (fallback to CORTEX)
- ✅ 100% test coverage

### 3. Knowledge Merge Logic

**File:** `src/knowledge/knowledge_merger.py`

**Class:** `KnowledgeMerger`

**Merge Strategy:**
1. Query CORTEX core knowledge (baseline)
2. Query company knowledge (overrides)
3. Merge: Company-defined fields override CORTEX, undefined fields use CORTEX defaults
4. Validate merge result (no conflicts, all required fields present)

**Example:**
```yaml
# CORTEX Knowledge
language: Python
framework: Flask
authentication: OAuth2

# Company ABC Knowledge
language: .NET
framework: Minimal APIs
# authentication not defined (uses CORTEX default)

# Merged Result
language: .NET          # Company override
framework: Minimal APIs # Company override
authentication: OAuth2  # CORTEX default (company undefined)
```

**Success Criteria:**
- ✅ Merge logic implemented and tested
- ✅ Company overrides CORTEX where explicitly defined
- ✅ CORTEX fills gaps where company undefined
- ✅ Validation prevents conflicts

### 4. Integration with Orchestrators

**Modified Files:**
- `src/orchestrators/planning/planning_orchestrator_v5.py`
- `src/orchestrators/base/base_orchestrator_v4_1.py`

**Changes:**
- Add `CompanyKnowledgeProvider` to orchestrator base class
- Update `_discover_context()` to query both CORTEX + company knowledge
- Pass merged knowledge to phase execution

**Success Criteria:**
- ✅ Planning orchestrator queries company knowledge
- ✅ Generated plans use company tech stack (not CORTEX defaults)
- ✅ No changes to core CORTEX knowledge files

---

## 🚀 Implementation Steps

### Step 1: Create Knowledge Folder Structure (Day 1-2)

**Tasks:**
1. Create `cortex-brain/tier2/company-knowledge/` directory
2. Create `company_abc/` subdirectory (sample company)
3. Create schema files: `architecture.md`, `tech-stack.yaml`, `api-catalog.json`, `coding-standards.md`
4. Populate with realistic sample data (.NET tech stack)

**Commands:**
```bash
mkdir -p cortex-brain/tier2/company-knowledge/company_abc
touch cortex-brain/tier2/company-knowledge/company_abc/{architecture.md,tech-stack.yaml,api-catalog.json,coding-standards.md,governance.yaml}
```

**Validation:**
- Run: `ls -R cortex-brain/tier2/company-knowledge/`
- Verify: All files created

### Step 2: Implement CompanyKnowledgeProvider (Day 3-5)

**Tasks:**
1. Create `src/knowledge/` directory
2. Create `company_knowledge_provider.py`
3. Implement class with methods (query_architecture, query_tech_stack, etc.)
4. Add YAML/JSON parsing logic
5. Write unit tests (test_company_knowledge_provider.py)

**Test Cases:**
- Query existing company → returns data
- Query non-existent company → returns None (graceful)
- Query specific tech stack component → returns filtered data
- Merge CORTEX + company knowledge → correct merge

**Validation:**
- Run: `pytest tests/test_company_knowledge_provider.py`
- Coverage: >95%

### Step 3: Build Knowledge Merger (Day 6-8)

**Tasks:**
1. Create `knowledge_merger.py`
2. Implement `merge()` method with priority logic
3. Handle edge cases (missing fields, type mismatches)
4. Write merge validation tests (100+ cases)

**Test Scenarios:**
- Company overrides all fields → 100% company
- Company defines 50% fields → 50% company, 50% CORTEX
- Company defines conflicting types → validation error
- Empty company knowledge → 100% CORTEX

**Validation:**
- Run: `pytest tests/test_knowledge_merger.py`
- All 100+ tests pass

### Step 4: Integrate with Orchestrators (Day 9-10)

**Tasks:**
1. Update `BaseOrchestratorV4_1` to include `CompanyKnowledgeProvider`
2. Modify `_discover_context()` in Planning v5 to call provider
3. Pass merged knowledge to phase execution
4. Test end-to-end (create plan with company knowledge)

**Test:**
```bash
python -m src.main "plan API using company ABC architecture"
```

**Expected Output:**
- Plan uses .NET (not Python)
- Plan uses Minimal APIs (not Flask)
- Plan includes company-specific API patterns

**Validation:**
- Generated plan contains company tech stack
- No CORTEX core files modified

---

## 📊 Success Criteria (Phase-Level)

**Must achieve all 4 for phase completion:**

1. ✅ **Company knowledge folder created** with schema-compliant structure
2. ✅ **CompanyKnowledgeProvider operational** - queries company knowledge correctly
3. ✅ **Merge logic validated** - company overrides CORTEX where defined
4. ✅ **Integration tested** - Planning orchestrator uses company knowledge

**Validation Command:**
```bash
python -m pytest tests/test_phase1_integration.py -v
```

---

## ⚠️ Risks & Mitigations

### Risk 1: Company knowledge format inconsistency

**Impact:** Different companies use incompatible formats  
**Mitigation:** Enforce strict YAML schema validation  
**Contingency:** Validation layer rejects non-compliant knowledge

### Risk 2: Merge logic incorrect (company doesn't override)

**Impact:** Plans ignore company knowledge  
**Mitigation:** 100+ merge test cases covering edge cases  
**Contingency:** Fallback to explicit override flags if merge fails

### Risk 3: Performance degradation (file I/O overhead)

**Impact:** Knowledge queries slow down orchestrators  
**Mitigation:** Add caching layer (Phase 11)  
**Contingency:** Load all company knowledge at startup (in-memory)

---

## 📚 References

**Implementation Examples:**
- Knowledge Library: `src/knowledge/knowledge_library.py` (existing CORTEX knowledge)
- Phase -1 Discovery: `src/orchestrators/planning/phases/phase_minus_one.py` (context discovery pattern)

**Schema Examples:**
- Tech Stack: `cortex-brain/tier3/tech-stack.yaml` (CORTEX tech stack)
- Governance: `cortex-brain/brain-protection-rules.yaml` (CORTEX rules)

**Documentation:**
- CORTEX Architecture: `cortex-brain/documents/cortex-architecture-quick-ref.md`
- Tier 2 Knowledge Graph: `cortex-brain/tier2/knowledge-graph.yaml`

---

## 🎉 Phase Completion Checklist

Before marking this phase complete, verify:

- [ ] Company knowledge folder structure created and validated
- [ ] CompanyKnowledgeProvider class implemented with all methods
- [ ] Knowledge merge logic tested with 100+ cases (>95% pass rate)
- [ ] Integration tested with Planning orchestrator (end-to-end)
- [ ] Unit tests pass (>95% coverage)
- [ ] Integration tests pass (all scenarios)
- [ ] Documentation updated (architecture docs, API reference)
- [ ] No CORTEX core files modified (Git diff verification)
- [ ] Performance acceptable (<50ms overhead for knowledge queries)
- [ ] Sample company (company_abc) created with realistic data

**Approval:** Phase 1 complete when all checkboxes ✅

---

**Phase Owner:** CORTEX Planning System v5  
**Created:** 2026-01-06  
**Status:** 🟡 Ready to start  
**Next:** Phase 2 (Orchestrator Registry System)
