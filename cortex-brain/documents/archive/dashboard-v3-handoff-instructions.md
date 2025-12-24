# Dashboard v3 Enhancement - Handoff Instructions

**Branch:** `admin-dashboard`  
**Date:** December 8, 2025  
**Status:** Planning Complete, Ready for Implementation  
**Next Phase:** 7.4 (Business Capability Intelligence)

---

## 🎯 Current State

**Completed:**
- ✅ Phases 1-6: Overview Tab (production-ready, 47 tests passing)
- ✅ Planning for Phases 7.4-7.7: Business Intelligence + New Tabs
- ✅ Updated plan document with complete specifications

**Not Yet Started:**
- ⏳ Phase 7.4: Business Capability Intelligence
- ⏳ Phase 7.5: Recommendations Tab
- ⏳ Phase 7.6: Use Cases Tab
- ⏳ Phase 7.7: Integration & Testing

---

## 📁 Key Files

### Planning Document
**Location:** `cortex-brain/documents/planning/dashboard-v3-narrative-executive-summary-plan.md`

**Contents:**
- Complete specifications for Phases 7.4-7.7
- Technical architecture details
- Data schemas (JSON examples)
- UI component designs
- Test requirements
- Timeline estimates

**Read This First:** All implementation details are in this file.

### Configuration Files (To Be Created)

**Phase 7.5:**
- `cortex-brain/config/e2e-criteria-config.json` - Extensible E2E prioritization criteria

---

## 🚀 Getting Started on Another Machine

### Step 1: Pull Latest Code

```bash
cd C:\PROJECTS\CORTEX  # Or your CORTEX path
git fetch origin
git checkout admin-dashboard
git pull origin admin-dashboard
```

### Step 2: Verify Environment

```bash
# Check Python version (3.8+ required)
python --version

# Install dependencies
pip install -r requirements.txt

# Run existing tests to ensure environment is working
pytest tests/integration/test_overview_tab.py -v
```

**Expected:** 47 tests should pass (26 backend + 21 integration)

### Step 3: Review Plan

```bash
# Open the plan document
code cortex-brain/documents/planning/dashboard-v3-narrative-executive-summary-plan.md

# Navigate to line 1313+ for Phases 7.4-7.7 specifications
```

**Key Sections:**
- Line 1313-1650: Phase 7.4 (Business Capability Intelligence)
- Line 1651-1850: Phase 7.5 (Recommendations Tab)
- Line 1851-2050: Phase 7.6 (Use Cases Tab)
- Line 2051-2100: Phase 7.7 (Integration)

---

## 📋 Implementation Order

### Phase 7.4: Business Capability Intelligence (12 hours)

**Day 1-3: Create these files**

1. **Backend Collector** (5 hours)
   ```
   src/dashboard/data/business_capability_detector.py
   ```
   - Class: `BusinessCapabilityDetector`
   - Methods: `detect()`, `extract_entities()`, `detect_patterns()`, `score_confidence()`
   - Output: `business-capabilities.json`

2. **Semantic Analyzer** (4 hours)
   ```
   src/dashboard/intelligence/semantic_analyzer.py
   ```
   - Extends: `ASTDocstringExtractor`
   - Methods: `analyze_method_intent()`, `infer_business_value()`

3. **Narrative Integration** (3 hours)
   ```
   Update: src/dashboard/data/narrative_consolidator.py
   ```
   - Add business capabilities to Executive Summary tab

**Tests:** `tests/dashboard/test_business_capability_detector.py`

**Git Checkpoint:** Commit after Phase 7.4 complete

---

### Phase 7.5: Recommendations Tab (14 hours)

**Day 4-6: Create these files**

1. **Backend Collector** (6 hours)
   ```
   src/dashboard/data/recommendation_collector.py
   ```
   - Class: `RecommendationCollector`
   - Output: `recommendations.json`

2. **E2E Prioritizer** (8 hours)
   ```
   src/dashboard/intelligence/e2e_test_prioritizer.py
   cortex-brain/config/e2e-criteria-config.json
   ```
   - Class: `E2ETestPrioritizer`
   - Extensible criteria system

3. **Frontend UI**
   ```
   static/js/components/RecommendationsTab.js
   static/js/components/E2EPriorityMatrix.js
   static/css/recommendations.css
   ```

**Tests:** `tests/dashboard/test_recommendation_collector.py`

**Git Checkpoint:** Commit after Phase 7.5 complete

---

### Phase 7.6: Use Cases Tab (14 hours)

**Day 7-9: Create these files**

1. **Backend Collector** (4 hours)
   ```
   src/dashboard/data/use_case_collector.py
   ```
   - Class: `UseCaseCollector`
   - Output: `use-cases.json`

2. **Frontend Views** (10 hours)
   ```
   static/js/components/UseCasesTab.js
   static/js/components/RoleMatrixView.js
   static/js/components/ProcessWorkflowView.js
   static/js/components/DomainHierarchyView.js
   static/css/use-cases.css
   ```

**Tests:** `tests/dashboard/test_use_case_collector.py`

**Git Checkpoint:** Commit after Phase 7.6 complete

---

### Phase 7.7: Integration (6 hours)

**Day 10: Wire everything together**

1. **HTML Updates** (2 hours)
   ```
   Update: templates/index.html
   Update: static/js/app.js
   ```
   - Add "Recommendations" tab button
   - Add "Use Cases" tab button
   - Add tab content containers

2. **Data Loader** (1 hour)
   ```
   Update: static/js/data-loader.js
   ```
   - Add `fetch('/data/recommendations.json')`
   - Add `fetch('/data/use-cases.json')`

3. **Integration Tests** (3 hours)
   ```
   tests/integration/test_new_tabs.py
   ```
   - 21 tests total

**Git Checkpoint:** Commit after all tests pass

---

## 🧪 Testing Strategy

### Backend Tests (Run after each phase)

```bash
# Test specific collector
pytest tests/dashboard/test_business_capability_detector.py -v

# Test all dashboard collectors
pytest tests/dashboard/ -v

# Run with coverage
pytest --cov=src/dashboard tests/dashboard/ --cov-report=term-missing
```

**Target:** 80%+ coverage

### Integration Tests (Run after Phase 7.7)

```bash
# Test new tabs end-to-end
pytest tests/integration/test_new_tabs.py -v

# Test entire dashboard
pytest tests/integration/ -v
```

**Target:** All 68 tests passing (47 existing + 21 new)

### Manual Testing (After each phase)

```bash
# Generate test data
python scripts/generate_dashboard_data.py

# Launch dashboard
python scripts/launch_dashboard.py

# Open browser to http://localhost:8082
# Click through new tabs
```

---

## 📊 Data Schemas

### Business Capabilities (`business-capabilities.json`)

```json
{
  "capabilities": [
    {
      "name": "User Authentication",
      "confidence": 95,
      "evidence": ["LoginController.cs", "AuthService.cs"],
      "patterns": ["authentication", "session_management"],
      "entities": ["User", "Session", "Token"],
      "endpoints": ["POST /api/auth/login"],
      "business_value": "critical"
    }
  ],
  "summary": {
    "total_capabilities": 8,
    "high_confidence": 5,
    "domain_models": ["User", "Product", "Order"]
  }
}
```

### Recommendations (`recommendations.json`)

```json
{
  "health_improvements": [...],
  "performance": [...],
  "security": [...],
  "technical_debt": [...],
  "e2e_testing": {
    "p0_critical": [
      {
        "scenario": "User Login & Authentication",
        "files": ["LoginController.cs"],
        "score": 92,
        "criteria_breakdown": {...},
        "risk": "Security breach",
        "recommendation": "Create E2E test"
      }
    ],
    "p1_high": [...],
    "p2_medium": [...],
    "p3_low": [...]
  }
}
```

### Use Cases (`use-cases.json`)

```json
{
  "use_cases": [
    {
      "id": "uc-001",
      "name": "User Login",
      "description": "Authenticate user",
      "roles": ["end_user", "manager"],
      "domain": "security_authentication",
      "process": "user_onboarding",
      "process_step": 1,
      "steps": ["Enter credentials", "Validate", "Generate token"],
      "endpoints": ["POST /api/auth/login"],
      "files": ["LoginController.cs"],
      "complexity": 15,
      "status": "implemented",
      "test_coverage": 85,
      "business_value": "critical"
    }
  ],
  "metadata": {
    "roles": [...],
    "domains": [...],
    "processes": [...]
  }
}
```

---

## 🔍 Troubleshooting

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'src'`

**Solution:**
```bash
# Ensure PYTHONPATH includes CORTEX root
cd C:\PROJECTS\CORTEX
set PYTHONPATH=%CD%
python -m pytest tests/
```

### Test Failures

**Problem:** Tests fail with `FileNotFoundError`

**Solution:**
```bash
# Generate required data files
python scripts/generate_dashboard_data.py --all
```

### Dashboard Not Loading

**Problem:** Port 8082 already in use

**Solution:**
```bash
# Dashboard auto-tries ports 8080-8089
# Or manually specify:
python scripts/launch_dashboard.py --port 8085
```

---

## 📞 Contact & Questions

**Plan Author:** AI Assistant (GitHub Copilot)  
**Plan Date:** December 8, 2025  
**Plan Location:** `cortex-brain/documents/planning/dashboard-v3-narrative-executive-summary-plan.md`

**For Questions:**
1. Read the plan document (line 1313+)
2. Check existing collectors in `src/dashboard/data/` for patterns
3. Review Overview Tab implementation (Phases 1-6) as reference
4. Ask specific questions about unclear sections

---

## ✅ Verification Checklist

Before starting implementation, verify:

- [ ] Git branch is `admin-dashboard`
- [ ] Latest code pulled from remote
- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Existing tests pass (47 tests in `tests/integration/test_overview_tab.py`)
- [ ] Plan document reviewed (`dashboard-v3-narrative-executive-summary-plan.md`)
- [ ] Data schemas understood (see above)

**Ready to start Phase 7.4!**

---

## 📈 Progress Tracking

Update this section as you complete phases:

- [ ] Phase 7.4: Business Capability Intelligence (12 hours)
  - [ ] Backend collector
  - [ ] Semantic analyzer
  - [ ] Narrative integration
  - [ ] Tests passing

- [ ] Phase 7.5: Recommendations Tab (14 hours)
  - [ ] Recommendation collector
  - [ ] E2E prioritizer
  - [ ] Frontend UI
  - [ ] Tests passing

- [ ] Phase 7.6: Use Cases Tab (14 hours)
  - [ ] Use case collector
  - [ ] Role matrix view
  - [ ] Process workflow view
  - [ ] Domain hierarchy view
  - [ ] Tests passing

- [ ] Phase 7.7: Integration (6 hours)
  - [ ] HTML updates
  - [ ] Data loader updates
  - [ ] Integration tests
  - [ ] All 68 tests passing

**Total Progress:** 0 / 46 hours (0%)

**Estimated Completion:** TBD (9 work days)
