# CORTEX Roadmap Restructure

**Date:** 2025-11-13  
**Action:** Updated CORTEX 3.0 design + Created CORTEX 2.0 Feature Planning spec  
**Reason:** Clarify manual vs extension paths, prioritize feature planning capability

---

## 📋 Changes Summary

### 1. CORTEX 3.0 Dual-Channel Memory - Clarified Implementation Paths

**File:** `cortex-brain/CORTEX-3.0-DUAL-CHANNEL-MEMORY-DESIGN.md`

**Changes:**

#### Two-Path Approach (Section 3.0.1)

**Before:** Single "Manual Conversation Import" section, separate "VS Code Extension Auto-Export" section  
**After:** Combined into "Conversation Import (Two-Path Approach)" with clear distinction:

- **Path 1: Manual Import (MVP - Available Now)**
  - User exports Copilot Chat manually
  - Says "import conversation from file"
  - ✅ Works today with existing plugin
  - ✅ No extension development needed
  - ✅ Sufficient for CORTEX 3.0 MVP

- **Path 2: One-Click Capture (Future - Extension Required)**
  - Auto-detection scoring on CORTEX responses
  - Smart hints when quality ≥ 6
  - VS Code extension accesses live chat
  - ⏳ Deferred post-MVP (not essential)
  - ⏳ Better UX but manual path is sufficient

**Rationale:** Clarifies that manual export→import is fully functional and sufficient for 3.0. Extension integration enhances UX but is not a blocker.

#### Timeline Reduction: 16 weeks → 14 weeks

**Before:** 6 phases including "Phase 5: VS Code Extension (4 weeks)"  
**After:** 6 phases with tutorials moved to Phase 3, extension deferred

**New Timeline:**
- Phase 1: Foundation (2 weeks)
- Phase 2: Fusion Basics (3 weeks)
- **Phase 3: User Enablement & Tutorials (2 weeks)** ← NEW
- Phase 4: Fusion Advanced (3 weeks)
- Phase 5: Narrative Generation (2 weeks)
- Phase 6: Optimization & Polish (2 weeks)
- **Future:** Extension Integration (4+ weeks, post-MVP)

**Total:** 14 weeks (~3.5 months) for MVP

#### Executive Summary Updates

**Before:** No timeline mentioned  
**After:** "Timeline: 14 weeks (~3.5 months) for MVP with manual import. Extension integration (one-click capture) deferred post-MVP."

**Before:** Single recommendation  
**After:** "Implementation Approach: MVP (14 weeks) - Manual import path (Path 1) - full functionality. Future Enhancement - Extension integration (Path 2) - improved UX but not essential"

### 2. CORTEX 2.0 Feature Planning - New Specification Created

**File:** `cortex-brain/CORTEX-2.0-FEATURE-PLANNING.md` ← NEW

**Purpose:** Bring interactive feature planning into CORTEX 2.0 (current release)

**Scope:**

**Problem:** Users struggle to break down complex features into actionable tasks

**Solution:** Interactive planning workflow:
1. User says "let's plan a feature"
2. Work Planner asks clarifying questions (what, why, who, constraints)
3. Pattern Matcher searches for similar past features
4. System breaks down into phases with tasks
5. Generates roadmap with dependencies and risks
6. Saves to database + markdown file
7. Immediately executable via "start Phase X"

**Timeline:** 4 weeks
- Week 1-2: Core planning workflow (questions, breakdown, storage)
- Week 3: Execution integration (Executor + Daemon tracking)
- Week 4: Advanced features (dependencies, risks, polish)

**Integration:** Uses existing agents (Work Planner, Pattern Matcher, Architect, Executor)

**Storage:**
- Database: `feature_plans`, `feature_phases`, `feature_risks` tables
- Files: `cortex-brain/feature-plans/*.md`

**Example UX:**
```
User: "Let's plan a feature"
CORTEX: [Asks questions about what, why, who, constraints]
User: "Add authentication to dashboard..."
CORTEX: [Breaks into 4 phases, identifies risks, generates roadmap]
User: "Start Phase 1"
CORTEX: [Executes with full plan context]
```

### 3. Roadmap Priority Decision Required

**Two Options:**

**Option A: CORTEX 2.0 Feature Planning First (4 weeks)**
- ✅ Immediate value (helps with current work)
- ✅ Shorter timeline (faster ROI)
- ✅ No new architecture (uses existing agents)
- ✅ Enables better planning for 3.0 work itself
- ⏳ Then proceed to CORTEX 3.0 (14 weeks)

**Option B: CORTEX 3.0 Dual-Channel First (14 weeks)**
- ✅ Strategic investment (long-term memory improvement)
- ✅ Validated prototype (simulation proves it works)
- ✅ Clear MVP path (manual import sufficient)
- ⏳ Longer timeline before value delivery
- ⏳ Feature planning deferred

**Option C: Parallel Tracks**
- ✅ Maximum speed to value
- ⚠️ Risk: Context switching overhead
- ⚠️ Risk: Resource constraints (if solo developer)

---

## 📊 Decision Matrix

| Criterion | 2.0 Feature Planning First | 3.0 Dual-Channel First | Parallel |
|-----------|---------------------------|------------------------|----------|
| **Time to Value** | ✅ 4 weeks | ⏳ 14 weeks | ✅ 4 weeks (partial) |
| **Immediate Utility** | ✅ High (helps all future work) | ⏳ Medium (learning accumulates) | ✅ High |
| **Complexity** | ✅ Low (existing agents) | ⏳ Medium (new fusion layer) | ⚠️ High (multi-tasking) |
| **Risk** | ✅ Low (proven patterns) | ✅ Low (prototype validated) | ⚠️ Medium (switching cost) |
| **Dependencies** | ✅ None | ✅ None | ✅ Independent |
| **Learning Value** | ✅ Immediate (use for 3.0 planning) | ⏳ Accumulates over time | ✅ Immediate |

---

## 🎯 Recommendation

**Suggested Priority: Option A (2.0 Feature Planning First)**

**Rationale:**

1. **Faster ROI:** 4 weeks vs 14 weeks to first value delivery
2. **Immediate utility:** Every future feature benefits from planning capability
3. **Meta-benefit:** Use feature planning to plan CORTEX 3.0 implementation itself
4. **Lower risk:** Uses proven agents, no new architecture
5. **Natural progression:** Planning → Execution → Memory (logical flow)

**Sequence:**
1. **Weeks 1-4:** CORTEX 2.0 Feature Planning implementation
2. **Week 5:** Use feature planning to plan CORTEX 3.0 (meta!)
3. **Weeks 6-19:** CORTEX 3.0 Dual-Channel Memory implementation
4. **Post-MVP:** Extension integration for one-click capture

**Total timeline:** ~5 months (4 weeks + 14 weeks + 1 week planning buffer)

---

## 📝 Next Steps

### Immediate Actions

1. ☐ **User Decision:** Approve Option A, B, or C
2. ☐ **Review:** CORTEX 2.0 Feature Planning design (`CORTEX-2.0-FEATURE-PLANNING.md`)
3. ☐ **Review:** Updated CORTEX 3.0 design (`CORTEX-3.0-DUAL-CHANNEL-MEMORY-DESIGN.md`)
4. ☐ **Confirm:** Implementation order and timeline

### If Option A Approved (Feature Planning First)

**Week 1:**
1. ☐ Review Work Planner agent current code
2. ☐ Design interactive questioning flow
3. ☐ Create Tier 1 schema migration (feature_plans tables)
4. ☐ Set up `cortex-brain/feature-plans/` directory

**Week 2:**
1. ☐ Implement questioning logic
2. ☐ Add Pattern Matcher integration
3. ☐ Build storage layer (database + markdown)
4. ☐ Test with real feature (e.g., "plan cleanup enhancement")

**Week 3:**
1. ☐ Integrate Executor agent with plans
2. ☐ Add daemon event tracking for progress
3. ☐ Implement "continue" command with plan context

**Week 4:**
1. ☐ Add dependency analysis
2. ☐ Add risk analysis
3. ☐ Polish UX and documentation
4. ☐ Production release

**Week 5:**
1. ☐ **Meta-usage:** Use feature planning to plan CORTEX 3.0 implementation!
2. ☐ Validate feature planning works for complex projects
3. ☐ Begin CORTEX 3.0 Phase 1

---

## 🔄 Architecture Impact

### CORTEX 2.0 Additions (If Feature Planning Approved)

**New Components:**
- Enhanced Work Planner agent (interactive mode)
- Pattern Matcher integration
- Feature plan storage (Tier 1 + files)
- Execution tracking integration

**Modified Components:**
- Executor agent (reads plan context)
- Ambient daemon (updates plan progress)
- "Continue" command (plan-aware)

**No Breaking Changes:** All additive, backward compatible

### CORTEX 3.0 Changes (Updated Design)

**Clarified:**
- Two-path approach (manual MVP, extension future)
- 14-week timeline (vs 16 weeks before)
- Tutorial phase moved to Phase 3
- Extension integration deferred post-MVP

**No Architecture Changes:** Core dual-channel design unchanged, only implementation approach clarified

---

## 📚 Reference Documents

### Created/Updated Files

1. **`cortex-brain/CORTEX-3.0-DUAL-CHANNEL-MEMORY-DESIGN.md`** (UPDATED)
   - Clarified two-path approach
   - Updated timeline (16→14 weeks)
   - Moved tutorials to Phase 3
   - Deferred extension to post-MVP

2. **`cortex-brain/CORTEX-2.0-FEATURE-PLANNING.md`** (NEW)
   - Complete feature planning specification
   - 4-week implementation roadmap
   - Database schema design
   - Example user flows

3. **`cortex-brain/ROADMAP-RESTRUCTURE-2025-11-13.md`** (THIS FILE)
   - Summary of changes
   - Decision matrix
   - Next steps

### Related Files (Unchanged)

- `cortex-brain/CONVERSATION-IMPORT-ANALYSIS.md` - Original analysis
- `cortex-brain/CORTEX-3.0-EXECUTIVE-SUMMARY.md` - High-level vision
- `cortex-brain/HYBRID-CAPTURE-SIMULATION-REPORT.md` - Validation results
- `scripts/simulate_hybrid_capture.py` - Working simulation
- `src/plugins/conversation_import_plugin.py` - Working prototype

---

## ✅ Approval Checklist

**Before proceeding, confirm:**

- [ ] CORTEX 3.0 two-path approach understood (manual MVP, extension later)
- [ ] CORTEX 3.0 timeline acceptable (14 weeks for MVP)
- [ ] CORTEX 2.0 Feature Planning design reviewed
- [ ] Implementation priority decided (Option A/B/C)
- [ ] Resource allocation confirmed (time, focus)

---

*Restructure Date: 2025-11-13*  
*Status: Awaiting User Decision*  
*Recommendation: Option A (Feature Planning First)*
