# 🎯 KDS Quick Reference Cheatsheet

**One Command for Everything:** `#file:KDS/prompts/user/kds.md [your request]`

---

## 🚀 Common Commands

### Start New Work
```markdown
#file:KDS/prompts/user/kds.md

I want to add a pulse animation to the FAB button
```
→ Creates plan with phases/tasks

### Continue Work
```markdown
#file:KDS/prompts/user/kds.md

Continue working on the current task
```
→ Executes next task in plan

### Resume After Break
```markdown
#file:KDS/prompts/user/kds.md

Show me where I left off
```
→ Shows completed tasks + next steps

### Fix Mistakes
```markdown
#file:KDS/prompts/user/kds.md

You're working on the wrong file. Use HostControlPanelContent.razor instead
```
→ Halts, reverts, corrects course

### Create Tests
```markdown
#file:KDS/prompts/user/kds.md

Create visual regression tests for the share button
```
→ Generates Playwright tests

### Check Health
```markdown
#file:KDS/prompts/user/kds.md

Run all validations and show me the health status
```
→ Reports system health

### Analyze Screenshots
```markdown
#file:KDS/prompts/user/kds.md

Analyze this screenshot and extract requirements

[Attach image in chat]
```
→ Extracts design specs from image

### Commit Changes
```markdown
#file:KDS/prompts/user/kds.md

Commit changes
```
→ Smart commit with auto-categorization

### View Metrics
```markdown
#file:KDS/prompts/user/kds.md

run metrics
```
→ Performance report with trends

### Launch Dashboard
```markdown
#file:KDS/prompts/user/kds.md

launch dashboard
```
→ Opens health monitoring dashboard

### Ask Questions
```markdown
#file:KDS/prompts/user/kds.md

How do I test canvas elements with Playwright?
```
→ Searches KDS knowledge base

---

## 🧠 BRAIN System (Self-Learning)

### Three Tiers

| Tier | Storage | Purpose | Capacity |
|------|---------|---------|----------|
| **1** | conversation-history.jsonl | Last 20 conversations | FIFO queue |
| **2** | knowledge-graph.yaml | Learned patterns | 3,847 entries |
| **3** | development-context.yaml | Project metrics | 1,249 commits |

### What BRAIN Learns

✅ Intent patterns ("add button" → PLAN)  
✅ File relationships (co-modification)  
✅ Common mistakes (file confusions)  
✅ Workflow patterns (UI = plan→execute→test)  
✅ Conversation context ("Make it purple" knows what "it" is)  
✅ Git velocity (commits/week, churn rate)  
✅ Test patterns (success rates, flaky tests)  
✅ Work patterns (productive times, correlations)

### Auto-Learning Triggers

- **50+ events** → Brain updates Tier 2
- **24 hours** → Brain updates if 10+ events
- **1+ hour since last** → Brain updates Tier 3 (throttled)

---

## 🎭 Specialist Agents

| Agent | Trigger Phrase | What It Does |
|-------|---------------|--------------|
| **Planner** | "I want to add..." | Creates phases/tasks |
| **Executor** | "Continue" | Implements code (test-first) |
| **Tester** | "Test..." | Playwright/MSTest/Percy tests |
| **Validator** | "Check health" | System health checks |
| **Corrector** | "Wrong file..." | Fixes errors, reverts |
| **Resumer** | "Where was I?" | Shows session state |
| **Screenshot** | "Analyze image" | Extracts requirements |
| **Committer** | "Commit" | Smart git commits |
| **Governor** | [Auto] | Reviews KDS changes |
| **Knowledge** | "How do I..." | Searches KDS docs |

---

## 📊 Dashboard Features

**Launch:** `.\KDS\scripts\launch-dashboard.ps1` or task: `kds: launch dashboard`

### 7 Health Categories
- 🏗️ Infrastructure (files, directories)
- 🤖 Agents & Prompts (10 specialists)
- 🧠 BRAIN System (3 tiers)
- 💾 Session State (active/history)
- 📚 Knowledge Base (graph, patterns)
- 🔧 Scripts & Tools (PowerShell)
- ⚡ Performance (response times)

### Actions
- 🔄 **Refresh** - Live health checks
- 📋 **Copy** - Export JSON report
- 📊 **Export** - Download report

---

## 🧪 Testing Protocols

### Component IDs (REQUIRED)
```html
<button data-testid="canvas-save-button">Save</button>
```
Format: `{feature}-{element}-{action}`

### Playwright Test Creation
```markdown
#file:KDS/prompts/user/kds.md

Create Playwright test for canvas save button
```
→ Uses component IDs, creates orchestration script

### Visual Regression (Percy)
- Auto-detects when screenshots needed
- Integrates with Playwright tests
- Baseline comparison

---

## 📐 Workflow Patterns

### TDD Workflow
1. **RED** - Write failing test
2. **GREEN** - Make test pass
3. **REFACTOR** - Clean up (tests stay green)

### Multi-Phase Features
```
Phase 1: Backend (Tasks 1a-1c)
Phase 2: Frontend (Tasks 2a-2d)
Phase 3: Tests (Tasks 3a-3b)
```

### Session Continuity
- Auto-saves after each task
- Resume in new chat sessions
- Zero context re-explanation

---

## 🎯 Smart Commit System

**Auto-categorizes files:**
- 🧠 BRAIN state → .gitignore
- 📝 Internal prompts → .gitignore
- 📊 Reports → .gitignore
- 📚 User docs → Commit
- 💻 Code changes → Commit

**Semantic commit format:**
```
feat(kds): Add dashboard refresh
fix(ui): Correct button alignment
docs(readme): Update setup steps
```

---

## 🔍 BRAIN Queries

### Routing Intelligence
- High confidence (≥0.85) → Auto-route
- Medium (≥0.70) → Ask user
- Low (<0.70) → Pattern match

### Protection Thresholds
```yaml
ask_user_threshold: 0.70
auto_route_threshold: 0.85
minimum_occurrences: 3
anomaly_detection: true
```

### Proactive Warnings
```
⚠️ HostControlPanel.razor is unstable (28% churn)
⚠️ This file often modified with noor-canvas.css
⚠️ Velocity dropped 68% this week
⚠️ Flaky test detected: fab-button.spec.ts
```

---

## 🛡️ Key Rules (Top 5)

| # | Rule | What It Means |
|---|------|---------------|
| **16** | Mandatory Post-Task | Auto-publish, cleanup, verify after every task |
| **17** | Challenge Authority | KDS questions harmful requests |
| **3** | Delete Over Archive | Trust git, delete obsolete files |
| **8** | Test-First Always | RED → GREEN → REFACTOR |
| **15** | UI Test IDs | Always add `data-testid` for Playwright |

---

## 📈 Metrics Reporter

**Shows:**
- 🎯 Routing accuracy (94% ↑)
- 🧠 BRAIN health score
- 📊 Knowledge graph growth
- 🔥 File hotspots (high churn)
- 📈 Code velocity trends
- ✅ Test-first impact (96% success)
- ⏰ Productivity patterns
- 💡 Actionable recommendations

**Report saved to:** `KDS/reports/metrics/latest.md`

---

## 🔄 Development Context (Tier 3)

### Tracked Metrics
```yaml
Git Activity: 1,249 commits, 30 days
Code Changes: Lines added/deleted, velocity
File Hotspots: Churn rate, stability
Test Activity: Pass rates, coverage
Work Patterns: Productive times, focus duration
Correlations: Commit size vs success, test-first vs rework
```

### Auto-Collection
- **Trigger:** After BRAIN updates (Tier 2)
- **Throttle:** Only if >1 hour since last collection
- **Duration:** 2-5 minutes (git analysis)

---

## 🎨 Architectural Principles

### SOLID Compliance
- **S**ingle Responsibility - Each agent has ONE job
- **O**pen/Closed - Easy to extend (add intents)
- **L**iskov - (N/A for agents)
- **I**nterface Segregation - Dedicated agents, no modes
- **D**ependency Inversion - Abstractions for file/test/session

### Architectural Thinking
✅ Discover existing patterns FIRST  
✅ Design solutions aligned from start  
❌ NEVER create monoliths to refactor later  
❌ NEVER use temporary locations

---

## 🚀 Setup (New Projects)

```markdown
#file:KDS/prompts/user/kds.md

Setup
```

**Duration:** 15-20 minutes

**What it does:**
1. Validates environment
2. Runs deep codebase crawler
3. Initializes 3-tier BRAIN
4. Collects development context
5. Populates knowledge graph
6. Runs health validation

**Modes:**
- `Setup` - Full (recommended)
- `Setup --quick` - Minimal (3-5 min)
- `Setup --import path` - Migrate from old KDS

---

## 💡 Pro Tips

### Multi-Intent Requests
```markdown
Add PDF export and validate
```
→ Routes to planner + validator

### Reference Resolution
```markdown
Make it purple
```
→ BRAIN remembers "it" from conversation history

### Challenge Mode
KDS will stop you if your request:
- Duplicates existing functionality
- Violates governance rules
- Harms KDS design

### Conversation Memory
- Last **20 conversations** preserved
- FIFO queue (oldest deleted when 21st starts)
- Active conversation NEVER deleted
- No time limits (preserved until FIFO)

---

## 📚 Knowledge Base

### 4 Categories
1. **test-patterns/** - Successful strategies
2. **test-data/** - Validated fixtures (session-212)
3. **ui-mappings/** - Component IDs, selectors
4. **workflows/** - End-to-end flows

### Publishing
**Auto-publishes after successful tests**
- What worked ✅
- What didn't work ❌
- Success rate
- Reuse count

---

## 🔗 Quick Links

- **Dashboard:** `.\KDS\scripts\launch-dashboard.ps1`
- **Metrics:** `#file:KDS/prompts/user/kds.md run metrics`
- **Health:** `#file:KDS/prompts/user/kds.md validate`
- **Resume:** `#file:KDS/prompts/user/kds.md resume`
- **Commit:** `.\KDS\scripts\commit-kds-changes.ps1`

---

## 🎓 Learning Curve

```
Day 1:   Use universal entry point, basic commands
Week 1:  Understand BRAIN learning, test-first workflow
Month 1: Leverage conversation history, metrics
Month 3: BRAIN highly optimized, proactive warnings active
```

---

**Version:** 5.0 (SOLID Refactor + BRAIN Integration)  
**Last Updated:** 2025-11-04  
**Full Docs:** `KDS/prompts/user/kds.md` (2,653 lines)

---

## 🎯 The One Rule to Remember

**Just use:** `#file:KDS/prompts/user/kds.md [what you want]`

KDS figures out everything else automatically. 🚀
