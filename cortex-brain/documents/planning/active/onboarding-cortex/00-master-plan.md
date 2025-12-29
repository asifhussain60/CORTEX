# 🎓 CORTEX Onboarding Master Plan

**Version:** 1.0.0  
**Status:** Active  
**Created:** 2025-12-29  
**Author:** Asif Hussain  
**Website:** https://asifhussain60.github.io/CORTEX/

---

## 🎯 Mission

Create a comprehensive onboarding experience that transforms new users from CORTEX beginners to confident practitioners within 60 minutes, covering installation, core concepts, practical workflows, and troubleshooting.

---

## 👥 Target Audience

### Primary Personas

1. **New Developer** (60% of users)
   - First time using CORTEX
   - Familiar with GitHub Copilot
   - Wants quick wins and practical examples

2. **Team Lead** (25% of users)
   - Evaluating CORTEX for team adoption
   - Needs understanding of architecture and workflows
   - Concerned about team productivity and learning curve

3. **AI Enthusiast** (15% of users)
   - Interested in AI-enhanced development
   - Wants to understand the "brain" architecture
   - Excited about multi-agent orchestration

---

## 📚 Learning Objectives

By completing this onboarding, users will:

1. ✅ **Install and configure** CORTEX in under 5 minutes
2. ✅ **Understand** the 4-tier brain architecture and SKULL protection
3. ✅ **Execute** their first planning operation with proper folder structure
4. ✅ **Master** the TDD workflow (RED→GREEN→REFACTOR)
5. ✅ **Navigate** documentation and find help resources
6. ✅ **Troubleshoot** common issues independently

---

## 🗺️ Onboarding Journey Map

### Phase 1: Quick Start (5 minutes)
**Goal:** Get CORTEX running with first successful command

```
Install → Configure → Test → First Command
```

**Deliverables:**
- CORTEX installed via pip
- Configuration validated
- `cortex help` executed successfully
- User sees their first CORTEX response

**Exit Criteria:**
- Installation verified
- Help command returns expected output
- User has workspace context established

---

### Phase 2: Core Concepts (10 minutes)
**Goal:** Understand CORTEX architecture and principles

**Topics:**
1. **4-Tier Brain Architecture**
   - Tier 0: Governance (brain protection rules, manifests)
   - Tier 1: Working Memory (conversation context, session tracking)
   - Tier 2: Knowledge Graph (relationships, lessons learned)
   - Tier 3: Development Context (project-specific memory)

2. **SKULL Protection System**
   - TDD_ENFORCEMENT: RED→GREEN→REFACTOR mandatory
   - HOLISTIC_DISCOVERY: Search before create
   - REFACTOR_CLEANUP: Remove orphaned code
   - GIT_ISOLATION: CORTEX code separate from user repos

3. **Response Templates v4.0**
   - Adaptive response tiers (INSTANT → COMPREHENSIVE)
   - Operation routing and intent classification
   - Token optimization strategies

**Deliverables:**
- Architecture diagram reviewed
- SKULL rules understood
- Response format examples seen

**Exit Criteria:**
- User can explain 4-tier brain in 30 seconds
- User understands why TDD is enforced
- User knows where to find templates

---

### Phase 3: First Planning Operation (15 minutes)
**Goal:** Successfully create a plan using toolkit integration

**Hands-On Exercise:**
```bash
# Say in Copilot Chat:
plan "user authentication feature"
```

**What Happens:**
1. CORTEX parses request via `CORTEX.prompt.md`
2. Planning Orchestrator activates
3. Toolkit `plan_scaffold_generator.py` creates folders:
   ```
   planning/active/user-authentication-feature/
   ├── 00-master-plan.md
   ├── context/
   ├── reports/
   ├── artifacts/
   └── tracking/
       └── progress-tracker.json
   ```
4. Master plan generated with DoR/DoD
5. Progress tracker initialized

**Deliverables:**
- Complete plan folder structure
- Master plan with phases
- Progress tracker JSON

**Exit Criteria:**
- User successfully created a plan
- User can navigate folder structure
- User understands progress tracking

---

### Phase 4: TDD Workflow (20 minutes)
**Goal:** Master RED→GREEN→REFACTOR cycle

**Hands-On Exercise:**
Build a simple calculator feature using TDD

**Steps:**

1. **RED Phase - Write Failing Test**
   ```python
   def test_calculator_add():
       calc = Calculator()
       assert calc.add(2, 3) == 5
   ```
   Run: `start tdd`
   Expected: Test fails (Calculator doesn't exist)

2. **GREEN Phase - Minimal Implementation**
   ```python
   class Calculator:
       def add(self, a, b):
           return a + b
   ```
   Run: `continue tdd`
   Expected: Test passes

3. **REFACTOR Phase - Improve Code**
   ```python
   class Calculator:
       """Simple calculator with type hints."""
       def add(self, a: int, b: int) -> int:
           """Add two integers."""
           return a + b
   ```
   Run: `complete tdd`
   Expected: Tests still pass, code improved

**Deliverables:**
- Working Calculator class
- Passing tests
- Git checkpoint created

**Exit Criteria:**
- User completed full TDD cycle
- User understands RED→GREEN→REFACTOR
- User can repeat process independently

---

### Phase 5: Documentation Navigation (5 minutes)
**Goal:** Know where to find help

**Key Resources:**

1. **Primary Entry Point**
   - `.github/prompts/CORTEX.prompt.md` - Intent router

2. **Operation Guides**
   - `.github/prompts/modules/` - Individual operation docs
   - `cortex-brain/manifests/orchestrators/` - Orchestrator specs

3. **Learning Paths**
   - `cortex-brain/documents/learning-paths/README.md`
   - Quick Start (10 min), Deep Dive (60 min), Mastery (4 hours)

4. **Troubleshooting**
   - `cortex-brain/documents/troubleshooting/` - Common issues
   - Health reports: `system maintenance`

5. **Web Documentation**
   - https://asifhussain60.github.io/CORTEX/
   - Architecture diagrams, API docs, examples

**Deliverables:**
- Bookmarked key resources
- Found answer to sample question

**Exit Criteria:**
- User can find docs for any operation
- User knows where to get help
- User understands learning path options

---

### Phase 6: Common Operations (10 minutes)
**Goal:** Execute 5 most common CORTEX operations

**Operations to Practice:**

1. **Plan a Feature**
   ```
   plan "add user profile page"
   ```

2. **Start TDD Workflow**
   ```
   start tdd
   ```

3. **Run System Maintenance**
   ```
   system maintenance
   ```

4. **Get Help**
   ```
   help
   ```

5. **Sanitize Code** (remove company-specific data)
   ```
   sanitize src/
   ```

**Deliverables:**
- Each operation executed successfully
- Results reviewed and understood

**Exit Criteria:**
- User comfortable with command syntax
- User understands natural language interface
- User can chain operations

---

## 🔧 Installation Guide

### Prerequisites
- Python 3.9+
- Git
- GitHub Copilot (VS Code extension)
- 500MB free disk space

### Installation Steps

**Method 1: Production Install (Recommended)**
```bash
pip install cortex-ai
cortex "version"
```

**Method 2: Development Install**
```bash
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX
pip install -e .
cortex "version"
```

**Verification:**
```bash
cortex "help"
# Should show operation list
```

---

## ⚙️ Configuration

### Basic Configuration

CORTEX auto-configures on first run. Verify with:
```bash
cortex "healthcheck"
```

### Custom Configuration (Optional)

Edit `cortex.config.json`:
```json
{
  "cortex_root": "/path/to/CORTEX",
  "enable_folder_structure": true,
  "enable_git_checkpoints": true,
  "tdd_enabled": true
}
```

---

## 🎨 Key Concepts

### 1. Natural Language Interface

CORTEX uses natural language, not slash commands:

✅ **Correct:**
```
plan user authentication
start tdd
system maintenance
```

❌ **Incorrect:**
```
/plan user-auth
/tdd start
/maintenance
```

### 2. Intent Routing

All requests go through `CORTEX.prompt.md` intent router:
- Removes meta-directives
- Classifies intent
- Routes to correct orchestrator
- Returns formatted response

### 3. Folder Structure

All plans use canonical 4-folder structure:
```
planning/active/{PLAN_NAME}/
├── 00-master-plan.md    # Human-readable plan
├── context/             # Background info, requirements
├── reports/             # Progress reports, phase completions
├── artifacts/           # Supporting files, diagrams
└── tracking/            # progress-tracker.json
```

Created by: `cortex-toolkit/core/utilities/plan_scaffold_generator.py`

### 4. TDD Enforcement

CORTEX enforces Test-Driven Development:
1. **RED:** Write failing test first
2. **GREEN:** Write minimal code to pass
3. **REFACTOR:** Improve without breaking tests

**Why?** 94% success rate with TDD vs 67% without (empirical data from CORTEX usage).

---

## 🚨 Troubleshooting

### Common Issues

**1. Import Error: "No module named cortex"**
```bash
# Solution: Reinstall
pip install --upgrade cortex-ai
```

**2. Planning Folder Not Created**
```bash
# Verify toolkit is accessible
python3 cortex-toolkit/core/utilities/plan_scaffold_generator.py --list

# If missing, check cortex_root in config
```

**3. TDD Workflow Not Starting**
```bash
# Check configuration
cortex "healthcheck"

# Verify tdd_enabled = true in config
```

**4. Response Templates Not Loading**
```bash
# Verify template files exist
ls -l cortex-brain/response-templates-v4.yaml

# Regenerate if missing
python3 cortex-toolkit/documentation/regenerate_prompts.py
```

### Getting Help

1. **System Health Check:**
   ```
   system maintenance
   ```

2. **Documentation:**
   - Web: https://asifhussain60.github.io/CORTEX/
   - Local: `.github/prompts/modules/`

3. **Community:**
   - GitHub Issues: https://github.com/asifhussain60/CORTEX/issues
   - Discussions: https://github.com/asifhussain60/CORTEX/discussions

---

## 📊 Success Metrics

**Onboarding Complete When:**

- [ ] User installed CORTEX successfully
- [ ] User executed 5+ operations independently
- [ ] User created a plan with proper folder structure
- [ ] User completed full TDD cycle
- [ ] User can find documentation without assistance
- [ ] User troubleshot 1+ issues independently
- [ ] User feels confident using CORTEX daily

**Time Investment:**
- Minimum: 30 minutes (Quick Path)
- Recommended: 60 minutes (Standard Path)
- Deep Dive: 120 minutes (Comprehensive Path)

---

## 🎯 Next Steps After Onboarding

### Beginner Path
1. Review hands-on tutorial (`tutorial` command)
2. Build 3 features using planning + TDD
3. Explore response templates
4. Read SKULL brain protection rules

### Intermediate Path
1. Study 4-tier brain architecture
2. Create custom orchestrator
3. Contribute to knowledge graph
4. Optimize token usage

### Advanced Path
1. Understand Phase 2.5 agentic enhancements
2. Build multi-agent workflows
3. Integrate external tools
4. Contribute to CORTEX evolution

---

## 📝 Appendix

### A. Command Quick Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `plan [feature]` | Create planning folder | `plan user authentication` |
| `start tdd` | Begin TDD workflow | `start tdd` |
| `system maintenance` | Health check | `system maintenance` |
| `help` | Show operations | `help` |
| `sanitize [dir]` | Remove company data | `sanitize src/` |

### B. Folder Structure Conventions

- **active/** - Work in progress
- **completed/** - Finished plans
- **archive/** - Historical reference
- **temp-plans/** - Experimental ideas

### C. Response Format Tiers

| Tier | Tokens | Use Case |
|------|--------|----------|
| INSTANT | <50 | Quick answers |
| FOCUSED | 50-200 | Explanations + next steps |
| STRUCTURED | 200-600 | Context + changes + next |
| COMPREHENSIVE | 600+ | Full documentation |

---

## ✅ Completion Checklist

Use this to track your onboarding progress:

**Phase 1: Quick Start**
- [ ] Installed CORTEX
- [ ] Ran `cortex help`
- [ ] Saw first response

**Phase 2: Core Concepts**
- [ ] Reviewed 4-tier brain diagram
- [ ] Read SKULL protection rules
- [ ] Understood response templates

**Phase 3: First Planning Operation**
- [ ] Created a plan
- [ ] Verified folder structure
- [ ] Reviewed progress tracker

**Phase 4: TDD Workflow**
- [ ] Wrote failing test (RED)
- [ ] Implemented minimal code (GREEN)
- [ ] Refactored with improvements (REFACTOR)

**Phase 5: Documentation Navigation**
- [ ] Found CORTEX.prompt.md
- [ ] Located operation guides
- [ ] Bookmarked web docs

**Phase 6: Common Operations**
- [ ] Planned a feature
- [ ] Started TDD
- [ ] Ran maintenance
- [ ] Got help
- [ ] Sanitized code

---

## 🎓 Certificate of Completion

```
┌────────────────────────────────────────────────────────────┐
│                                                            │
│              🧠 CORTEX ONBOARDING COMPLETE 🎉               │
│                                                            │
│  Congratulations! You've mastered the fundamentals of      │
│  CORTEX and are ready to build amazing software with       │
│  AI-enhanced development workflows.                        │
│                                                            │
│  Completed: [DATE]                                         │
│  User: [NAME]                                              │
│                                                            │
│  Next: Explore advanced topics in learning-paths/          │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

**Author:** Asif Hussain  
**GitHub:** github.com/asifhussain60/CORTEX  
**Website:** https://asifhussain60.github.io/CORTEX/  
**License:** Source-Available (Use Allowed, No Contributions)
