# OneDrive Site Restructure: Reporting Focus

**Date:** December 11, 2025  
**Purpose:** Transform RA-Domain OneDrive dashboard from recommendation tool → pure data reporting tool  
**Audience:** Executives & Managers learning about repository from high-level → details

---

## 🎯 Core Principle

**BEFORE:** "Here's what's wrong and how to fix it" (Recommendations, sprint plans, action items)  
**AFTER:** "Here's what exists" (Metrics, findings, data visualization)

**Key Change:** Remove ALL prescriptive content - no "should", "recommend", "action item", "sprint", "roadmap"

---

## 📊 Test Coverage Gap KPI (NEW)

### Data Source
✅ **EXTRACTED VIA AST:** `gap-analysis-prioritized.json` & `regulatory-risk-heatmap.json`

### KPI Card Content
```html
<div class="kpi critical">
    <h3>Test Coverage Gaps</h3>
    <div class="value">6</div>
    <div class="target">Components At Risk</div>
    <div class="trend down">$950k Exposure</div>
    <p style="font-size: 0.875rem; color: var(--text-secondary);">
        1 CRITICAL | 1 HIGH | 2 MEDIUM | 2 LOW risk components
    </p>
</div>
```

### Detail Page: `managers/test-coverage-gaps.html`
**Content (Data Only):**
- Risk matrix table (CRITICAL → LOW)
- Component breakdown (P0-P2)
- Financial exposure by risk level
- Test scenarios needed count
- Regulatory risk classification

**Removed:**
- Sprint velocity tracker
- Quarterly roadmap timeline
- Recommended test types
- Action items

---

## 🔄 Page-by-Page Restructure

### 1. `index.html` (Executive Dashboard)
**KEEP:**
- 8 KPI cards (metrics only)
- Quick links grid
- CORTEX branding footer

**REMOVE:**
- ❌ N/A - Already clean

**ADD:**
- ✅ New "Test Coverage Gaps" KPI (replace generic "Test Coverage")

---

### 2. `managers/test-coverage-roadmap.html` → `managers/test-coverage-gaps.html`
**RENAME FILE:** Roadmap implies action plan

**KEEP:**
- Current coverage: 8.6% (19 tests / 220 files)
- Gap analysis: 81.4% missing
- Untested files list
- Risk matrix (CRITICAL/HIGH/MEDIUM/LOW)
- Financial exposure: $950k total

**REMOVE:**
- ❌ "Quarterly Roadmap" section (lines 72-110)
- ❌ "Sprint Velocity Tracker" table (lines 259-305)
- ❌ "Target" metrics (90% coverage goal)
- ❌ "12 sprints @ 8 tests/sprint" language
- ❌ All mentions of "Q1 2025", "Sprint 50-61"

**REPLACE WITH:**
- Component-by-component gap breakdown
- Test scenario counts (not "needed" - just "unimplemented")
- Business impact statements (facts, not recommendations)

---

### 3. `managers/weekly-scorecard.html` → `managers/team-metrics.html`
**RENAME FILE:** "Scorecard" OK but "Weekly" implies tracking over time

**KEEP:**
- Test coverage: 8.6%
- Bus factor: 1 person (Carryover domain)
- Documentation score: 30/100
- Technical debt: $83k estimated
- Team capacity: 174 hours

**REMOVE:**
- ❌ "Sprint Goals (Week 50)" section (lines 72-109)
- ❌ "Sprint Velocity" KPI (lines 52-60)
- ❌ "Action Items (This Week)" section (lines 240-272)
- ❌ "Recommendation:" callout (line 236)
- ❌ All sprint/roadmap terminology

**REPLACE WITH:**
- Current state metrics
- Resource allocation (hours per component)
- Technical debt distribution chart
- Knowledge ownership matrix

---

### 4. `developers/onboarding-guide.html`
**KEEP:**
- 5-step learning path structure (educational, not prescriptive)
- Key files reference table
- Complexity hotspots data
- FAQ section

**REMOVE:**
- ❌ "Next Steps After Onboarding" section (lines 381-412)
- ❌ "Success Criteria:" language (line 175)
- ❌ References to "9-month roadmap" (line 347)
- ❌ "Tech Lead creating README in Sprint 51" (line 375)

**REPLACE WITH:**
- "Learning Resources" (not "Next Steps")
- "Completion Indicators" (not "Success Criteria")
- Remove future-tense references

---

### 5. `developers/complexity-heatmap.html`
**KEEP:**
- Top 10 large files table (>500 LOC)
- Complexity scores per file
- Method count breakdown
- Refactoring cost estimates

**REMOVE:**
- ❌ "3-Phase Refactoring Roadmap" section (if exists)
- ❌ "Recommended" patterns/approaches
- ❌ Sprint timelines

**REPLACE WITH:**
- "Complexity Analysis" (factual breakdown)
- "Refactoring Scope Estimates" (effort, not plan)

---

### 6. `developers/knowledge-ownership.html`
**KEEP:**
- Bus factor matrix (who owns what)
- Knowledge silo identification
- Coverage gaps by component

**REMOVE:**
- ❌ "Q1 2025 Knowledge Transfer Plan" (if exists)
- ❌ "Recommended pair programming" sessions
- ❌ Action items for documentation

**REPLACE WITH:**
- "Knowledge Distribution Report"
- "Single Points of Failure" (data only)

---

### 7. `product/capability-catalog.html`
**KEEP:**
- 4 core capabilities
- Use case breakdown
- Regulatory compliance mapping
- Integration points (45 NuGet packages)

**REMOVE:**
- ❌ "Roadmap Alignment" references
- ❌ "Recommended features"
- ❌ Future enhancement plans

**REPLACE WITH:**
- "Current Capabilities" (as-is state)
- "Compliance Coverage" (what's implemented)

---

### 8. `regulatory/p0-issues-tracker.html`
**KEEP:**
- 9 P0 issues list
- IRS/HIPAA/PCI-DSS violations
- Risk classification
- Affected components

**REMOVE:**
- ❌ "Remediation Plans"
- ❌ "Sprint assignments"
- ❌ "Action items"

**REPLACE WITH:**
- "Issue Status" (Open/Closed only)
- "Impact Analysis" (what's affected, not what to do)

---

## 🎨 Terminology Changes

### Global Find & Replace

| BEFORE (Prescriptive) | AFTER (Descriptive) |
|----------------------|---------------------|
| "Roadmap" | "Analysis" or "Report" |
| "Sprint 50-61" | Remove entirely |
| "Recommended" | "Observed" or "Identified" |
| "Action Items" | "Findings" |
| "Next Steps" | "Learning Resources" |
| "Target: 90%" | "Gap: 81.4%" (show delta, not goal) |
| "Should" | "Currently" |
| "Q1 2025 Plan" | "Current State (Q4 2024)" |
| "Success Criteria" | "Completion Indicators" |
| "Phase 1-3" | Remove or convert to "Areas 1-3" |

---

## 📁 File Renaming

| OLD NAME | NEW NAME |
|----------|----------|
| `managers/test-coverage-roadmap.html` | `managers/test-coverage-gaps.html` |
| `managers/weekly-scorecard.html` | `managers/team-metrics.html` |
| (Others stay same) | |

---

## 🔧 Implementation Checklist

### Phase 1: Data Extraction (COMPLETE ✅)
- [x] Identify test coverage gap data in AST outputs
- [x] Confirm `gap-analysis-prioritized.json` has all data
- [x] Confirm `regulatory-risk-heatmap.json` has risk matrix

### Phase 2: KPI Card Creation
- [ ] Add "Test Coverage Gaps" KPI to `index.html`
- [ ] Update link to point to `managers/test-coverage-gaps.html`
- [ ] Update card content to show 6 components, $950k exposure

### Phase 3: File Restructure
- [ ] Rename `test-coverage-roadmap.html` → `test-coverage-gaps.html`
- [ ] Rename `weekly-scorecard.html` → `team-metrics.html`
- [ ] Update all internal links to new filenames

### Phase 4: Content Removal (Per Page)
- [ ] `index.html` - Add new KPI, update links
- [ ] `managers/test-coverage-gaps.html` - Remove roadmap/sprint sections
- [ ] `managers/team-metrics.html` - Remove action items/sprint goals
- [ ] `developers/onboarding-guide.html` - Remove next steps section
- [ ] `developers/complexity-heatmap.html` - Remove refactoring roadmap
- [ ] `developers/knowledge-ownership.html` - Remove transfer plan
- [ ] `product/capability-catalog.html` - Remove roadmap alignment
- [ ] `regulatory/p0-issues-tracker.html` - Remove remediation plans

### Phase 5: Terminology Cleanup
- [ ] Global find/replace for prescriptive terms
- [ ] Convert "should/recommended" to "currently/observed"
- [ ] Remove all sprint/quarter references

### Phase 6: Deployment
- [ ] Copy updated files to OneDrive
- [ ] Test all internal links
- [ ] Verify no broken navigation

---

## 📊 Test Coverage Gaps Detail Page Structure

### New File: `managers/test-coverage-gaps.html`

**Header:**
- Title: "Test Coverage Gap Analysis"
- Subtitle: "Untested components with regulatory risk exposure"
- Last Updated: December 11, 2025

**Section 1: Summary Metrics**
```
┌─────────────────────────────────────┐
│ Total Coverage:  8.6% (19/220 files)│
│ Gap:            81.4% (201 untested)│
│ Risk Exposure:  $950,000            │
│ Components:     6 at-risk areas     │
└─────────────────────────────────────┘
```

**Section 2: Risk Matrix**
Table with columns:
- Risk Level | Component | Files Untested | Test Scenarios | Business Impact | Financial Exposure

Rows:
1. CRITICAL | CarryoverDollarsDomainService | 1 file | 15 scenarios | IRS compliance failure | $500k
2. HIGH | BalanceCalculationService | 2 files | 12 scenarios | Incorrect balances | $200k
3. MEDIUM | ClaimsProcessingService | 2 files | 20 scenarios | Processing errors | $100k
4. MEDIUM | CardTransactionService | 2 files | 18 scenarios | Fraud risk | $80k
5. LOW | PlanManagementService | 3 files | 15 scenarios | Setup errors | $50k
6. LOW | ReportingService | 2 files | 10 scenarios | Report inaccuracies | $20k

**Section 3: Component Breakdown (Expandable)**
For each component:
- Files affected
- Test scenarios unimplemented
- Business impact statement
- Regulatory risk classification

**Section 4: Untested Files List**
- 201 untested files grouped by project
- LOC count per file
- Complexity score

**NO ROADMAP, NO SPRINT PLAN, NO ACTION ITEMS**

---

## ✅ Success Criteria for Restructure

1. **No Prescriptive Language:** Zero instances of "should", "recommend", "action item"
2. **No Timeline References:** Zero mentions of sprints, quarters, phases (as plans)
3. **Data-First:** Every statement backed by AST-extracted data
4. **Executive Clarity:** High-level metrics drill down to technical details
5. **No Broken Links:** All navigation works after file renames

---

## 🎯 Final State Vision

**Executives/Managers can:**
- See high-level KPIs (8 cards on dashboard)
- Click to drill into specific areas
- Understand current state without being told what to do
- Export/share data for their own planning

**Developers can:**
- Learn about repository structure
- Identify complexity hotspots
- Understand ownership distribution
- Find key files to start working on

**What They CANNOT Do (By Design):**
- Get sprint plans (that's their job to create)
- See recommendations (present facts, not opinions)
- Find action items (data informs their decisions)

---

**Prepared by:** CORTEX AI Assistant  
**Approved by:** User (Asif Hussain)  
**Implementation Status:** Phase 1 COMPLETE, Phase 2-6 PENDING
