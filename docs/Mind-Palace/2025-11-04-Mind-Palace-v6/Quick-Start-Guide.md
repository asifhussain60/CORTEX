# KDS Mind Palace: Quick Start Guide

**Get Productive in 15 Minutes**

**Purpose:** Practical, step-by-step guide to using the KDS Mind Palace effectively  
**Audience:** Developers, users, anyone working with KDS  
**Reading Time:** 15 minutes  
**Last Updated:** November 4, 2025

---

## 🚀 The 2-Minute Overview

**KDS Mind Palace is a self-learning assistant with a three-tiered brain:**

1. **Core Instincts (Tier 0)** - Permanent rules that never change (TDD, SOLID, quality standards)
2. **Active Memory (Tier 1)** - Your last 20 conversations (so "make it purple" knows what "it" is)
3. **Recollection (Tier 2)** - Learned patterns from past work (error prevention, workflow templates)
4. **Awareness (Tier 3)** - Project health metrics (file hotspots, velocity, productivity patterns)
5. **Imagination (Tier 4)** - Creative ideas and experiments ("what if?" questions)

**The magic:** You use ONE command for everything, and the brain figures out what you need.

---

## ✅ Prerequisites

Before you start:

- [x] KDS installed in your project (`D:\PROJECTS\KDS` or similar)
- [x] PowerShell 5.1+ or PowerShell Core 7+
- [x] Git installed and configured
- [x] Your project has a codebase (KDS will learn from it)

**First time setup?** Run:
```powershell
#file:KDS/prompts/user/kds.md Setup
```

This takes 15-20 minutes and teaches KDS about your project.

---

## 🎯 The Only Command You Need

```markdown
#file:KDS/prompts/user/kds.md

[Tell KDS what you want in plain language]
```

That's it! No need to remember which specialist agent to call. Examples:

```markdown
#file:KDS/prompts/user/kds.md

I want to add a pulse animation to the FAB button
```

```markdown
#file:KDS/prompts/user/kds.md

Continue working on the current task
```

```markdown
#file:KDS/prompts/user/kds.md

Where did I leave off?
```

KDS automatically:
- ✅ Figures out what you're asking for
- ✅ Routes to the right specialist
- ✅ Uses learned patterns from past work
- ✅ Gives proactive warnings based on project history
- ✅ Remembers context across conversations

---

## 🏃 Common Workflows

### Workflow 1: Start a New Feature

**You say:**
```markdown
#file:KDS/prompts/user/kds.md

I want to add invoice PDF export functionality
```

**What happens:**
1. **Brain queries Tier 1-4** - Checks recent conversations, learned patterns, project metrics, captured ideas
2. **Proactive warnings appear** - "⚠️ Similar PDF features took 5-6 days. File XYZ is a hotspot (28% churn)."
3. **Plan created** - Multi-phase plan with architectural discovery, tests, implementation, validation
4. **Session saved** - Your work is tracked so you can resume anytime

**Next steps:**
```markdown
#file:KDS/prompts/user/kds.md

continue
```

---

### Workflow 2: Continue Existing Work

**You say:**
```markdown
#file:KDS/prompts/user/kds.md

continue
```

**What happens:**
1. **Loads active session** - Finds where you left off
2. **Shows current task** - "Phase 2, Task 1: Create InvoiceService.cs"
3. **Executes with TDD** - Creates tests first (RED), implements code (GREEN), refactors
4. **Auto-validates** - Runs tests, checks health, commits changes

**If no active session:**
```
No active session found. Recent sessions:
  1. invoice-export (3 tasks remaining)
  2. dark-mode-toggle (completed)

Select session number or start new work.
```

---

### Workflow 3: Resume After a Break

**Scenario:** You worked on a feature yesterday, closed your IDE, and now you're back.

**You say:**
```markdown
#file:KDS/prompts/user/kds.md

Show me where I left off
```

**What happens:**
1. **Brain checks Tier 1** - Looks at last 20 conversations
2. **Finds most recent work** - "Last conversation: Invoice PDF export"
3. **Shows detailed status**:
   ```
   Session: invoice-export
   Progress: 3/8 tasks (38%)
   
   ✅ Phase 1: Architectural Discovery (complete)
   🔄 Phase 2: Implementation (1/3 tasks done)
      ✅ Task 2.1: Create InvoiceService.cs
      ⏳ Task 2.2: Create API controller
      ⏳ Task 2.3: Create Blazor component
   ⬜ Phase 3: Testing (not started)
   ```

**To continue:**
```markdown
#file:KDS/prompts/user/kds.md

continue
```

---

### Workflow 4: Fix a Copilot Mistake

**Scenario:** Copilot is editing the wrong file.

**You say:**
```markdown
#file:KDS/prompts/user/kds.md

You're modifying the wrong file. The FAB button is in HostControlPanelContent.razor, not HostControlPanel.razor
```

**What happens:**
1. **Error Corrector activates** - Dedicated agent for fixing mistakes
2. **Reverts wrong changes** - Undoes modifications to incorrect file
3. **Loads correct file** - Opens HostControlPanelContent.razor
4. **Updates task** - Changes session to reference correct file
5. **Brain learns** - Adds file confusion pattern to prevent future mistakes

**Next time:**
When you mention "HostControlPanel", brain will warn:
```
⚠️ Did you mean HostControlPanelContent.razor? 
These files are often confused (learned from Session 247).
```

---

### Workflow 5: Create Tests

**You say:**
```markdown
#file:KDS/prompts/user/kds.md

Create visual regression tests for the share button using Percy
```

**What happens:**
1. **Test Generator activates**
2. **Brain checks Tier 2** - Finds existing Percy patterns
3. **Creates tests** - Following proven patterns (component IDs, not text selectors)
4. **Runs tests** - Validates they work
5. **Logs results** - Updates brain with test execution data

**Tests created:**
```typescript
// Tests/UI/share-button-visual.spec.ts
test('Share button displays correctly', async ({ page }) => {
  await page.goto('/host/control-panel/PQ9N5YWW');
  const shareBtn = page.locator('#sidebar-share-btn');
  await percySnapshot(page, 'Share Button - Default State');
});
```

**Note:** KDS uses component IDs (fast, reliable) not text selectors (slow, brittle).

---

### Workflow 6: Check System Health

**You say:**
```markdown
#file:KDS/prompts/user/kds.md

Run all validations and show me the health status
```

**What happens:**
1. **Health Validator runs** - Checks all KDS components
2. **Reports per category:**
   ```
   🏗️ Infrastructure: ✅ All files present
   🤖 Agents: ✅ 10/10 agents operational
   🧠 BRAIN: ✅ All 5 tiers healthy
   💾 Sessions: ✅ 2 active, 0 corrupted
   📚 Knowledge: ✅ 3,247 patterns, 92% avg confidence
   🔧 Scripts: ✅ All executable
   ⚡ Performance: ✅ 287ms avg response time
   ```

**If issues found:**
```
❌ Tier 3 (Awareness): Last updated 2 days ago (stale)
   Recommendation: Run development context collector

⚠️ BRAIN Storage: 487KB (approaching 500KB limit)
   Recommendation: Run pattern consolidation
```

---

### Workflow 7: Commit Changes

**Automatic:** KDS commits after each task completion (Rule #16).

**Manual (if needed):**
```markdown
#file:KDS/prompts/user/kds.md

Commit changes
```

**What happens:**
1. **Analyzes uncommitted files** - Categorizes into KDS auto-generated vs user-created
2. **Updates .gitignore** - Adds BRAIN state files, internal prompts, reports
3. **Resets auto-generated files** - Keeps them out of commits
4. **Creates semantic commit** - `feat: Add invoice PDF export`
5. **Achieves zero uncommitted files** - Clean repository state

**You'll see:**
```
🧠 KDS Smart Commit Handler
═══════════════════════════════════════════════════════

Step 1: Analyzing uncommitted files...
  Modified files: 9
  Untracked files: 11

Step 2: Categorizing files...
  User-created: 3 files
  Auto-generated: 8 files (will reset)

Step 5: Files to commit:
  + KDS/prompts/user/kds.md
  + Services/InvoiceService.cs
  + Controllers/API/InvoiceExportController.cs

Step 7: Committing...
  ✅ Changes committed

═══════════════════════════════════════════════════════
✅ SUCCESS: Zero uncommitted files!
```

---

### Workflow 8: Ask Questions

**You say:**
```markdown
#file:KDS/prompts/user/kds.md

How do I use Playwright to test canvas elements with data-testid selectors?
```

**What happens:**
1. **Knowledge Retriever activates**
2. **Brain checks Tier 4** - Searches captured questions
3. **Finds similar question** - "Question about Playwright canvas testing from 2 weeks ago"
4. **Links to existing answer** - If already answered
5. **OR captures as new question** - If unique

**If new:**
Brain captures in `kds-brain/right-hemisphere/questions-backlog.yaml`:
```yaml
- id: q-047
  question: "How to use Playwright for canvas testing with data-testid?"
  category: "testing"
  priority: "medium"
  captured: "2025-11-04T14:32:00Z"
  answer_location: null  # Will be filled when answered
```

---

### Workflow 9: Launch Health Dashboard

**You say:**
```markdown
#file:KDS/prompts/user/kds.md

launch dashboard
```

**Or run directly:**
```powershell
.\KDS\scripts\launch-dashboard.ps1
```

**What happens:**
1. **API server starts** - In a visible PowerShell window
2. **Browser opens** - Dashboard UI loads
3. **Real-time health monitoring** - Visual feedback for all operations

**Dashboard shows:**
- 🏗️ Infrastructure health
- 🤖 Agent status (10 specialists)
- 🧠 BRAIN system (5-tier status)
- 💾 Session state
- 📚 Knowledge base
- ⚡ Performance metrics

**To stop:** Close the API server PowerShell window or press Ctrl+C

---

### Workflow 10: View Performance Metrics

**You say:**
```markdown
#file:KDS/prompts/user/kds.md

run metrics
```

**What happens:**
1. **Metrics Reporter generates report** - Visual bar charts, trends, recommendations
2. **Saved to** `KDS/reports/metrics/latest.md`
3. **Also archived** `KDS/reports/metrics/YYYY-MM-DD/metrics-{timestamp}.md`

**Report includes:**
```
📊 Quick Stats
Routing Accuracy: 94% ▲ +3% 🟢 Excellent
Learning Efficiency: 92% ▲ +12% 🟢 Excellent

🧠 BRAIN Storage
Tier 1: [████████░░░░░░░░░░░░] 8/20 (40%)
Tier 2: 3,847 entries (+247 this month)
Tier 3: 1,547 commits analyzed

🔥 File Hotspots
HostControlPanelContent.razor  ████████████ 28% churn ⚠️
UserRegistrationLink.razor     ██████████░░ 24% churn ⚠️

💡 Recommendations
1. Continue test-first (96% success rate)
2. Work 10am-12pm (94% peak productivity)
3. Refactor hotspots (>20% churn)
```

**Reading time:** ~90 seconds

---

## 🧠 Understanding Proactive Warnings

**KDS warns you BEFORE problems happen** (not after). This is Tier 3 (Awareness) at work.

### Warning Types

#### File Hotspot Warning
```
⚠️ HostControlPanel.razor is a hotspot (28% churn rate)
   💡 Recommend: Add extra testing, smaller commits
```

**What it means:** This file changes frequently and may be unstable. Extra care needed.

#### Complexity Warning
```
⚠️ PDF features take 50% longer than other exports
   💡 Recommend: Allocate 6-7 days instead of 4-5
```

**What it means:** Based on historical data, this type of feature is complex.

#### Velocity Drop Warning
```
⚠️ Velocity dropped 30% this week
   💡 Recommend: Smaller commits, more frequent testing
```

**What it means:** You're moving slower than usual. Suggest workflow adjustments.

#### Success Pattern
```
✅ Test-first has 96% success rate for exports
   💡 Recommend: Continue TDD workflow
```

**What it means:** Historical data shows this approach works well.

---

## 🎯 Best Practices

### 1. Trust the Brain's Context

**Instead of:**
```markdown
#file:KDS/prompts/user/kds.md

I want to add a pulse animation to the FAB button in HostControlPanelContent.razor at line 247
```

**Just say:**
```markdown
#file:KDS/prompts/user/kds.md

Add a pulse animation to the FAB button
```

The brain will:
- Find the FAB button component (Tier 2 knowledge)
- Know which file it's in
- Suggest related files that often change together

---

### 2. Let Copilot Work in Small Steps

**Instead of:**
```markdown
#file:KDS/prompts/user/kds.md

Implement the entire invoice export feature with PDF generation, email delivery, and audit logging
```

**Say:**
```markdown
#file:KDS/prompts/user/kds.md

I want to add invoice export with PDF and email
```

Then:
```markdown
#file:KDS/prompts/user/kds.md

continue
```

Let KDS break it into phases and execute step-by-step.

---

### 3. Use "Continue" Liberally

After each successful task:
```markdown
#file:KDS/prompts/user/kds.md

continue
```

KDS knows what's next. No need to repeat context.

---

### 4. Correct Mistakes Immediately

If Copilot goes off-track:
```markdown
#file:KDS/prompts/user/kds.md

Wrong file! The component is in HostControlPanelContent.razor
```

Brain will:
- Halt execution immediately
- Revert wrong changes
- Load correct file
- **Learn the pattern** to prevent future confusion

---

### 5. Reference Past Conversations

Within the last 20 conversations, you can say:
```markdown
#file:KDS/prompts/user/kds.md

Make it purple
```

And the brain knows "it" = the FAB button from conversation #247.

---

### 6. Ask Questions Anytime

Don't hesitate:
```markdown
#file:KDS/prompts/user/kds.md

How do I test SignalR hub connections with Playwright?
```

Brain will:
- Check if already answered (deduplication)
- Capture as new question if unique
- Answer or direct you to existing knowledge

---

### 7. Check Health Weekly

```markdown
#file:KDS/prompts/user/kds.md

Run all validations
```

Catches issues before they become problems:
- Stale Tier 3 data
- BRAIN storage bloat
- Degraded routing accuracy
- Event backlog

---

### 8. Review Metrics Monthly

```markdown
#file:KDS/prompts/user/kds.md

run metrics
```

Understand trends:
- Are you getting faster over time? (learning effectiveness)
- Which files need refactoring? (hotspots)
- When are you most productive? (time-of-day patterns)
- Is test-first paying off? (success rate correlation)

---

## 🛠️ Troubleshooting

### Problem: "Intent routing accuracy seems low"

**Symptoms:**
- KDS frequently routes to wrong agent
- You're correcting it often

**Solutions:**
1. Check recent misroutes in `kds-brain/events.jsonl`
2. Run: `#file:KDS/prompts/user/kds.md run metrics` → Check routing accuracy
3. If <85%, add training examples to `intent-router.md`
4. Verify you're using natural language (not technical commands)

---

### Problem: "Brain doesn't remember recent conversations"

**Symptoms:**
- "Make it purple" doesn't know what "it" is
- Context from yesterday is lost

**Solutions:**
1. Check `kds-brain/conversation-history.jsonl` exists
2. Verify last 20 conversations are present (not truncated)
3. Run: `#file:KDS/prompts/user/kds.md Run all validations` → Check Tier 1 health
4. If FIFO queue broken, re-run setup

---

### Problem: "Proactive warnings aren't appearing"

**Symptoms:**
- No warnings about hotspot files
- No velocity estimates

**Solutions:**
1. Check `kds-brain/development-context.yaml` last updated time
2. If >24 hours old, run:
   ```powershell
   .\KDS\scripts\collect-development-context.ps1
   ```
3. Verify Git history exists (Tier 3 needs commits to analyze)
4. Check events.jsonl has sufficient data

---

### Problem: "KDS suggests wrong files"

**Symptoms:**
- File suggestions are inaccurate
- Co-modification warnings don't make sense

**Solutions:**
1. Check `kds-brain/knowledge-graph.yaml` → `file_relationships` section
2. If confidence scores are low (<0.60), need more sample data
3. Work on a few features to build patterns
4. Run: `#file:KDS/prompts/internal/brain-updater.md` (manual update)

---

### Problem: "Performance is slow"

**Symptoms:**
- Routing takes >1 second
- Tier queries are sluggish

**Solutions:**
1. Run: `#file:KDS/prompts/user/kds.md run metrics` → Check response times
2. Check BRAIN storage size (should be <500KB):
   ```powershell
   Get-ChildItem "KDS/kds-brain/*.jsonl", "KDS/kds-brain/*.yaml" | Measure-Object -Property Length -Sum
   ```
3. If >500KB, run consolidation:
   ```powershell
   .\KDS\scripts\consolidate-patterns.ps1
   ```
4. Archive old events (keep last 1000):
   ```powershell
   .\KDS\scripts\archive-events.ps1
   ```

---

### Problem: "BRAIN storage keeps growing"

**Symptoms:**
- `knowledge-graph.yaml` is >400KB
- `events.jsonl` is >200KB

**Solutions:**
1. Archive old events:
   ```powershell
   .\KDS\scripts\archive-events.ps1 -KeepLast 1000
   ```
2. Consolidate low-confidence patterns:
   ```powershell
   .\KDS\scripts\consolidate-patterns.ps1 -MinConfidence 0.60
   ```
3. Prune stale patterns (unused >90 days):
   ```powershell
   .\KDS\scripts\prune-stale-patterns.ps1 -DaysUnused 90
   ```

---

### Problem: "Setup takes too long (>25 minutes)"

**Symptoms:**
- Deep crawler running forever
- Tier 3 collection stuck

**Solutions:**
1. Use quick setup instead:
   ```markdown
   #file:KDS/prompts/user/kds.md Setup --quick
   ```
2. Add skip patterns to exclude large dependencies:
   ```yaml
   # kds-brain/crawler-config.yaml
   skip_patterns:
     - "node_modules/**"
     - "bin/**"
     - "obj/**"
     - "packages/**"
   ```
3. Run targeted crawler later on specific modules

---

### Problem: "Commits aren't automatic"

**Symptoms:**
- Files remain uncommitted after tasks complete
- Have to manually commit

**Solutions:**
1. Verify Rule #16 is active in `governance/rules.md`
2. Check `commit-handler.md` is operational
3. Manually trigger commit:
   ```markdown
   #file:KDS/prompts/user/kds.md Commit changes
   ```
4. Review task completion logs for commit failures

---

## 📚 FAQ

### Q: How does KDS remember context across days/weeks?

**A:** Tier 1 (Active Memory) stores your last 20 complete conversations. As long as you haven't had 20 new conversations since, KDS remembers. When conversation #21 starts, #1 is deleted (FIFO), but patterns are extracted to Tier 2 first.

---

### Q: What happens to my conversations when I start a new project?

**A:** When you run amnesia (switch projects):
- Tier 0 (Core Instincts) → **Preserved** (TDD, SOLID, etc.)
- Tier 1 (Conversations) → **Deleted** (application-specific context)
- Tier 2 (Patterns) → **Partially deleted** (application-specific), generic patterns preserved
- Tier 3 (Metrics) → **Reset** (new project = fresh metrics)
- Tier 4 (Ideas) → **Selectively preserved** (cross-project ideas kept)

---

### Q: Can I undo amnesia?

**A:** Yes! Amnesia creates a backup first. Rollback:
```powershell
$backupDir = "KDS/kds-brain/backups/pre-amnesia-{timestamp}"
Copy-Item -Path "$backupDir/*.yaml" -Destination "KDS/kds-brain/" -Force
Copy-Item -Path "$backupDir/*.jsonl" -Destination "KDS/kds-brain/" -Force
```

---

### Q: How do I know if my brain is healthy?

**A:** Run:
```markdown
#file:KDS/prompts/user/kds.md Run all validations
```

Green (✅) = healthy. Yellow (⚠️) = needs attention. Red (❌) = immediate action required.

---

### Q: What's the difference between "continue" and "resume"?

**A:**
- **Continue** - You have an active session, just keep going (next task)
- **Resume** - You've been away, show me where I left off (status report + continue option)

Both work, but "resume" gives you a status summary first.

---

### Q: Can I have multiple active sessions?

**A:** No. KDS maintains ONE active session at a time for clarity. However, you can pause the current session and resume a different one:
```markdown
#file:KDS/prompts/user/kds.md

Pause current session and resume session "dark-mode-toggle"
```

---

### Q: How do I reset KDS for a new project?

**A:**
```markdown
#file:KDS/prompts/user/kds.md

Reset BRAIN for new application
```

Or:
```powershell
.\KDS\scripts\brain-amnesia.ps1
```

Safely removes application data while preserving KDS intelligence.

---

### Q: What if I don't like a suggestion?

**A:** Just say so!
```markdown
#file:KDS/prompts/user/kds.md

Don't use that pattern. Create a new approach instead.
```

KDS will defer to your judgment and create a fresh plan.

---

### Q: Can I see what the brain knows?

**A:** Yes! Explore:
- `kds-brain/conversation-history.jsonl` - Last 20 conversations
- `kds-brain/knowledge-graph.yaml` - Learned patterns
- `kds-brain/development-context.yaml` - Project metrics
- `kds-brain/events.jsonl` - Raw event stream

Or use the dashboard:
```powershell
.\KDS\scripts\launch-dashboard.ps1
```

---

### Q: How do I export knowledge to share with my team?

**A:**
```powershell
# Export all BRAIN state
Compress-Archive -Path "KDS/kds-brain/*" -DestinationPath "kds-brain-export.zip"

# Share the zip file with your team
# They extract to their KDS/kds-brain/ folder
```

**Note:** This shares learned patterns, not your conversations (privacy preserved).

---

## 🎓 Next Steps

### For Beginners
1. ✅ Read this guide (you're here!)
2. Run your first feature: `#file:KDS/prompts/user/kds.md I want to add [simple feature]`
3. Practice "continue" workflow
4. Try correcting a mistake
5. Check health: `#file:KDS/prompts/user/kds.md Run all validations`

### For Regular Users
1. Explore metrics: `#file:KDS/prompts/user/kds.md run metrics`
2. Launch dashboard: `.\KDS\scripts\launch-dashboard.ps1`
3. Review patterns: `kds-brain/knowledge-graph.yaml`
4. Validate brain health weekly
5. Share learned patterns with team

### For Advanced Users
1. Read **Technical Reference** for deep dive into architecture
2. Customize intent patterns in `intent-router.md`
3. Add custom workflow templates to Tier 2
4. Integrate KDS with CI/CD pipeline
5. Contribute enhancements back to KDS project

---

## 📖 Additional Resources

- **The Memory Keeper** (`The-Memory-Keeper.md`) - Engaging story explaining the architecture
- **Technical Reference** (`Technical-Reference.md`) - Comprehensive technical specifications
- **Visual Blueprints** (`Visual-Blueprint-Prompts.md`) - Gemini image generation prompts *(planned)*
- **Brain Sharpener** (`docs/BRAIN-SHARPENER.md`) - Validation framework for testing brain health
- **Implementation Plan** (`IMPLEMENTATION-PLAN.md`) - Development roadmap
- **Main KDS Documentation** (`prompts/user/kds.md`) - Complete system documentation

---

**Questions? Feedback? Improvements?**

KDS is a living system that learns and evolves. If you discover better workflows or have suggestions, capture them as ideas:

```markdown
#file:KDS/prompts/user/kds.md

Idea: [Your improvement suggestion]
```

The brain's Imagination tier will capture it for future consideration!

---

**Welcome to the KDS Mind Palace. May your conversations be productive, your patterns be learned, and your brain stay sharp.** 🧠✨

**Status:** ✅ Complete  
**Version:** 1.0 (November 2025)  
**Part of:** The KDS Mind Palace Collection  
**Next:** Visual Blueprint Prompts (Gemini diagrams)
