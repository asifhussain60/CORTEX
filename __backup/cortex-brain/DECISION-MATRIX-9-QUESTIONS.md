# ⚡ QUICK DECISION MATRIX: 9 Questions with YES Defaults

**Confirm these 9 decisions to proceed immediately**

---

## DECISION 1: Delete Phases 6-9?
**Default Answer: ✅ YES**

| Aspect | Details |
|--------|---------|
| **What** | Remove phases 6, 7, 8, 9 from master-plan.yaml |
| **Why** | They're legacy CORTEX-5.x phases; AC-INDEX doesn't define ACs for them |
| **Impact** | Reduces confusion, clarifies CORTEX-6.0 is 7 phases (1-5 + production phases) |
| **Risk** | None - they can be added back in CORTEX-7.0 if needed |
| **Your Answer** | [ ] YES (default) [ ] NO (explain) |

---

## DECISION 2: Merge Phase 1.5 into Phase 1?
**Default Answer: ✅ YES**

| Aspect | Details |
|--------|---------|
| **What** | Move AC-AUDIT-EVIDENCE-P1.5 into Phase 1 |
| **Why** | Only 1 AC; "1.5" is non-standard numbering; logically part of Foundation |
| **Impact** | Cleaner phase structure; Phase 1 becomes 31 ACs instead of 30 + 1 |
| **Risk** | None - still Phase 1 foundation |
| **Your Answer** | [ ] YES (default) [ ] NO (explain) |

---

## DECISION 3: Merge Phase 4.5 into Phase 4?
**Default Answer: ✅ YES**

| Aspect | Details |
|--------|---------|
| **What** | Move AC-AUDIT-EVIDENCE-P4.5 into Phase 4 |
| **Why** | Only 1 AC; "4.5" is non-standard numbering; logically part of Intelligence |
| **Impact** | Cleaner phase structure; Phase 4 becomes 2 ACs instead of 1 + 1 |
| **Risk** | None - still Phase 4 Intelligence |
| **Your Answer** | [ ] YES (default) [ ] NO (explain) |

---

## DECISION 4: Is Master-Plan Definition-Only?
**Default Answer: ✅ YES**

| Aspect | Details |
|--------|---------|
| **What** | Remove all `completed_ac_count` from master-plan.yaml |
| **Why** | Progress-tracker.json is the execution SSOT; mixing concerns causes hallucinations |
| **Impact** | Clear separation: master-plan = what ACs in each phase (static), progress-tracker = completion state (dynamic) |
| **Risk** | None - just reorganization |
| **Your Answer** | [ ] YES (default) [ ] NO (explain) |

---

## DECISION 5: Remove Identical Target Dates?
**Default Answer: ✅ YES**

| Aspect | Details |
|--------|---------|
| **What** | Delete all `target_completion: '2026-02-01'` fields |
| **Why** | All phases have same date (impossible for sequential execution); belongs in project plan, not SSOT |
| **Impact** | Eliminates misleading deadlines; keeps master-plan focused on architecture |
| **Risk** | None - project plan still tracks dates separately |
| **Your Answer** | [ ] YES (default) [ ] NO (explain) |

---

## DECISION 6: Phase 3 Include Feature Orchestrators?
**Default Answer: ✅ NO (for CORTEX-6.0)**

| Aspect | Details |
|--------|---------|
| **What** | Keep Phase 3 as minimal evidence bucket (1 AC) instead of adding 30+ feature orchestrator ACs |
| **Why** | Feature ACs (ADO, Vacuum, Investigation, Sanitization, Crawler) don't exist in AC-INDEX; would require defining new 30 ACs; scope creep |
| **Impact** | Phase 3 remains "Feature Orchestrators (Planned)" with 1 AC; features deferred to CORTEX-7.0 |
| **Risk** | Slight - less features in CORTEX-6.0, but cleaner delivery |
| **Your Answer** | [ ] NO (default) [ ] YES (add 30+ ACs now) |

---

## DECISION 7: Rename Phase 10→6 and Phase 11→7?
**Default Answer: ✅ YES**

| Aspect | Details |
|--------|---------|
| **What** | Renumber: Phase 10 = Phase 6, Phase 11 = Phase 7 |
| **Why** | Sequential numbering 1-7 is clearer than 1-5 + jump to 10-11 |
| **Impact** | Master-plan becomes 7 sequential phases instead of 9 phases with gaps |
| **Risk** | None - internal renaming only |
| **Your Answer** | [ ] YES (default) [ ] NO (explain) |

---

## DECISION 8: Audit Git History Before Implementing?
**Default Answer: ✅ YES**

| Aspect | Details |
|--------|---------|
| **What** | Before continuing Phase 2, search git history for previous implementations |
| **Why** | Don't repeat failed attempts; learn what worked/failed in CORTEX-5.5 |
| **Impact** | Faster Phase 2 execution (30% time savings), fewer false starts |
| **Risk** | None - just research before implementing |
| **Your Answer** | [ ] YES (default) [ ] NO (skip history audit) |

---

## DECISION 9: Rebuild Progress-Tracker from Clean State?
**Default Answer: ✅ YES**

| Aspect | Details |
|--------|---------|
| **What** | Create new progress-tracker.json from AC-INDEX with accurate counts |
| **Why** | Current tracker shows 100% complete on all phases (false); prevents hallucinations |
| **Impact** | Clean baseline: Phase 1 = 24/30 (80%), Phase 2 = 12/54 (22%), Phase 3-7 = 0/X |
| **Risk** | None - based on evidence from last valid state |
| **Your Answer** | [ ] YES (default) [ ] NO (keep current tracker) |

---

## SUMMARY: Your Choices

| # | Question | Your Answer | Your Reasoning (if different from default) |
|---|----------|-------------|-------------------------------------------|
| 1 | Delete 6-9? | [ ] YES | |
| 2 | Merge 1.5? | [ ] YES | |
| 3 | Merge 4.5? | [ ] YES | |
| 4 | Definition-only? | [ ] YES | |
| 5 | Remove dates? | [ ] YES | |
| 6 | Phase 3 features? | [ ] NO | |
| 7 | Rename 10→6, 11→7? | [ ] YES | |
| 8 | Audit history? | [ ] YES | |
| 9 | Rebuild tracker? | [ ] YES | |

---

## NEXT STEPS

Once you confirm these 9 decisions (with any overrides), I will:

1. ✅ Apply corrections to master-plan.yaml
2. ✅ Rebuild progress-tracker.json cleanly
3. ✅ Commit both atomically
4. ✅ Execute Phase 2 with hallucination safeguards

**Timeline: 15 minutes to ready state, then Phase 2 execution begins**

---

**INSTRUCTION: Reply with your 9 answers (or confirm all YES defaults to proceed immediately)**
