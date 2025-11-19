# Chapter 04: Context Intelligence

*Part of The Intern with Amnesia - The CORTEX Story*  
*Author: Asif Hussain | © 2024-2025*  
*Generated: November 19, 2025*

---

## Overview

**Concept:** Understanding project structure and development patterns  
**Technical Mapping:** Tier 3 Development Context (git analysis, file relationships)

---

## The Story

Like your brain's ability to see patterns in your daily life and optimize accordingly, Tier 3 provides **the balcony view of your entire development process**. It analyzes your project's health and your own productivity patterns.

**Git Activity Analysis (Last 30 Days):**
- **Commit Velocity** - Example: 1,237 commits analyzed, 42 commits/week average
- **File Hotspots** - Example: `HostControlPanelContent.razor` has 28% churn rate (unstable!)
- **Change Patterns** - Example: Smaller commits (<200 lines) have 94% success rate vs 67% for large commits
- **Contributor Activity** - Tracks who works on what, identifies knowledge silos
- **Branch Health** - Identifies long-lived branches, merge conflicts, stale work

**Code Health Metrics:**
- **Lines Added/Deleted** - Velocity trends showing if project is growing sustainably
- **Stability Classification** - Files marked as stable, unstable, or volatile based on change frequency
- **Test Coverage Trends** - Example: Coverage improved 72% → 76% this month (improving!)
- **Build Success Rates** - Example: 97% clean builds last week (excellent health)

**CORTEX Usage Intelligence (Your Productivity Patterns):**
- **Session Patterns** - Example: 10am-12pm sessions have 94% success rate vs 2pm sessions at 81%
- **Intent Distribution** - Example: PLAN (35%), EXECUTE (45%), TEST (15%), VALIDATE (5%)
- **Workflow Effectiveness** - Example: Test-first workflow reduces rework by 68%
- **Focus Duration** - Example: Sessions <60 min have 89% success vs >60 min at 67% (suggests breaks help)

**Proactive Warnings:**
```
⚠️ File Alert: HostControlPanel.razor is a hotspot (28% churn rate)
   Recommendation: Add extra testing before changes
                  Consider smaller, incremental modifications
                  Review recent changes for instability causes

✅ Optimal Time: 10am-12pm sessions have 94% success rate
   Current Time: 2:30pm (81% success rate historically)
   Suggestion: Consider scheduling complex work for morning sessions

📊 Velocity Alert: Commit velocity down 68% this week
   Recommendation: Try smaller commits (they have higher success rates)
                  More frequent testing reduces debugging time
                  Consider pair programming for complex features

🎯 Focus Pattern: Your last 5 sessions >60 minutes had 67% success
   Recommendation: Try 45-minute focused work blocks with breaks
                  Sessions <60 min show 89% success rate for you
```

**Storage:** `cortex-brain/tier3/context-intelligence.db` (SQLite), `cortex-brain/tier3/git-analysis.jsonl`  
**Performance:** <200ms analysis (target), 156ms actual ⚡

---

---

## Technical Deep Dive

### Tier 3 Development Context (git analysis, file relationships)


**Tier 3 Architecture:**
- Context intelligence: `cortex-brain/tier3/context-intelligence.db`
- Git analysis: `cortex-brain/tier3/git-analysis.jsonl`
- Analyzes last 30 days of git history
- Performance: <200ms analysis target, 156ms actual

**Analysis Capabilities:**
- Commit velocity tracking
- File hotspot identification
- Change pattern recognition
- Contributor activity analysis
- Code health metrics
- Proactive warnings


---

## Key Takeaways

- Tier 3 analyzes git history for project insights
- File hotspots and change patterns identified automatically
- Proactive warnings prevent common mistakes
- Productivity patterns optimized over time


---

## Next Chapter

**[Chapter 05: Dual Hemisphere Brain](./05-dual-hemisphere-brain.md)**

*Separating strategic memory from operational execution*
