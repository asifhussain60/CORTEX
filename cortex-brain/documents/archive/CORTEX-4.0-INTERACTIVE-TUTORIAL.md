# 🎓 CORTEX 4.0 Interactive Tutorial

**Version:** 4.0.0  
**Author:** Asif Hussain  
**Last Updated:** December 27, 2025  
**Estimated Time:** 45-60 minutes  
**Difficulty:** Beginner to Advanced

---

## 📋 Table of Contents

1. [Welcome & Prerequisites](#welcome--prerequisites)
2. [Module 1: First Contact - Getting Help](#module-1-first-contact---getting-help)
3. [Module 2: Understanding CORTEX Architecture](#module-2-understanding-cortex-architecture)
4. [Module 3: System Health & Maintenance](#module-3-system-health--maintenance)
5. [Module 4: Planning System - Your First Feature](#module-4-planning-system---your-first-feature)
6. [Module 5: TDD Mastery Workflow](#module-5-tdd-mastery-workflow)
7. [Module 6: Code Sanitization](#module-6-code-sanitization)
8. [Module 7: ADO Operations](#module-7-ado-operations)
9. [Module 8: CORTEX Toolkit](#module-8-cortex-toolkit)
10. [Module 9: Advanced Operations](#module-9-advanced-operations)
11. [Module 10: Best Practices & Tips](#module-10-best-practices--tips)
12. [Graduation & Next Steps](#graduation--next-steps)

---

## 🎯 Welcome & Prerequisites

### What You'll Learn

By the end of this tutorial, you'll be able to:
- ✅ Navigate CORTEX's 4-tier brain architecture
- ✅ Use system operations (align, healthcheck, optimize, cleanup)
- ✅ Create and execute feature plans with TDD
- ✅ Sanitize code for public sharing
- ✅ Generate ADO work items
- ✅ Leverage the CORTEX Toolkit (55+ tools)
- ✅ Apply Brain Protection (SKULL) rules
- ✅ Understand orchestrators and agents

### Prerequisites

**Required:**
- VS Code with GitHub Copilot
- Python 3.8+
- Git installed
- Basic command line knowledge

**Setup Verification:**

```bash
# Run this in Copilot Chat:
"healthcheck"
```

**Expected Output:** System status report showing all tiers operational.

If you see errors, run: `"align"` to auto-fix issues.

---

## 🚀 Module 1: First Contact - Getting Help

**Duration:** 5 minutes  
**Goal:** Learn CORTEX's help system and command discovery

### Exercise 1.1: Basic Help

**Try this in Copilot Chat:**

```
help
```

**What to observe:**
- 📋 Command categories (System, Planning, Development, Analytics)
- 🎯 Quick reference table
- 🔍 Natural language examples

### Exercise 1.2: Command Search

**Try this:**

```
What commands help me plan a feature?
```

**What to observe:**
- CORTEX understands natural language
- Returns relevant operations: `plan`, `plan ado`, `tdd`
- Shows examples and usage patterns

### Exercise 1.3: Operation Details

**Try this:**

```
Tell me about the planning system
```

**What to observe:**
- Detailed workflow explanation
- Phases and execution method
- Complexity-based routing (HIGH→incremental, LOW→skeleton)
- Auto-TDD integration

### ✅ Checkpoint 1

You should now be able to:
- [x] Access help system
- [x] Search for commands by intent
- [x] Understand operation metadata

**Troubleshooting:**
- If help doesn't work → Run `"align"` first
- If commands not found → Check `cortex-operations.yaml` exists

---

## 🏗️ Module 2: Understanding CORTEX Architecture

**Duration:** 10 minutes  
**Goal:** Explore the 4-tier brain and execution model

### The 4-Tier Brain

```
cortex-brain/
├── tier0/  # Governance (SKULL rules)
├── tier1/  # Working memory (70-conv FIFO)
├── tier2/  # Knowledge graph (patterns)
├── tier3/  # Dev context (metrics, hotspots)
```

### Exercise 2.1: Explore Tier 0 (Governance)

**Read this file:**

```bash
# In Copilot Chat:
"Show me the brain protection rules"
```

**Or manually open:** `cortex-brain/brain-protection-rules.yaml`

**Key rules to understand:**
- **TDD_ENFORCEMENT:** Tests must fail first (RED phase)
- **HOLISTIC_CODE_DISCOVERY_ENFORCEMENT:** Search before create
- **GIT_ISOLATION_ENFORCEMENT:** CORTEX code stays in CORTEX repo
- **REFACTOR_CODE_CLEANUP_ENFORCEMENT:** Remove orphaned code

### Exercise 2.2: Explore Tier 1 (Working Memory)

**Try this:**

```
What's in my working memory?
```

**What to observe:**
- Recent conversations (70-conversation FIFO buffer)
- Context retention across sessions
- Sub-100ms query performance

### Exercise 2.3: Execution Methods

CORTEX operations use 3 execution methods:

| Method | Purpose | Example Operations |
|--------|---------|-------------------|
| `cli_wrapper` | File I/O, git, system ops | align, healthcheck, optimize |
| `copilot_chat` | Interactive workflows | planning, tdd, ado |
| `internal` | Infrastructure (not user-facing) | Orchestrators, utilities |

**Try this:**

```
What execution method does "plan" use?
```

**Expected:** `copilot_chat` (interactive multi-turn workflow)

### ✅ Checkpoint 2

You should now understand:
- [x] 4-tier brain architecture
- [x] Brain Protection (SKULL) rules
- [x] Execution method differences
- [x] Where code lives (separation of concerns)

---

## 🔧 Module 3: System Health & Maintenance

**Duration:** 10 minutes  
**Goal:** Master system operations and diagnostics

### Exercise 3.1: Healthcheck

**Run this:**

```
healthcheck
```

**What to observe:**
- System status across all tiers
- Database connectivity
- Configuration validation
- Test pass rate
- Recommendation engine output

### Exercise 3.2: Alignment (Auto-Fix)

**Run this:**

```
align
```

**What happens:**
- Auto-fixes configuration issues
- Repairs broken file paths
- Updates stale references
- Validates SKULL compliance
- Generates alignment report

**Report location:** `cortex-brain/documents/reports/alignment-report-{timestamp}.md`

### Exercise 3.3: Cleanup

**Run this:**

```
cleanup
```

**What it does:**
- Removes orphaned test files
- Deletes duplicate code
- Cleans up temporary artifacts
- Prunes stale cache entries
- Archives legacy 3.0 files

### Exercise 3.4: Optimize

**Run this:**

```
optimize
```

**What it optimizes:**
- Response template efficiency
- Database indices
- Knowledge graph queries
- Token usage patterns
- Conversation context retrieval

### Exercise 3.5: Full Maintenance Workflow

**Run this (Admin only):**

```
system maintenance
```

**7 phases:**
1. Pre-healthcheck (baseline)
2. Align (auto-fix)
3. Cleanup (remove waste)
4. Optimize (performance)
5. Vacuum (database)
6. Refresh prompts (regenerate)
7. Post-healthcheck (validation)

**Duration:** ~5-10 minutes  
**Completion:** Shows `# 🎉 CONGRATULATIONS` when all phases complete

### ✅ Checkpoint 3

You should now be able to:
- [x] Check system health
- [x] Auto-fix issues with align
- [x] Clean up workspace
- [x] Optimize performance
- [x] Run full maintenance (admin)

---

## 📋 Module 4: Planning System - Your First Feature

**Duration:** 15 minutes  
**Goal:** Create and execute a feature plan with TDD

### Exercise 4.1: Simple Plan (Low Complexity)

**Try this:**

```
plan a simple user profile page with name and email fields
```

**What happens:**
1. CORTEX analyzes complexity → LOW
2. Generates skeleton plan (4-5 phases)
3. Includes TDD phase automatically
4. Shows DoR (Definition of Ready) checklist
5. Presents execution options

**Plan structure:**
```yaml
Phase 1: Setup & Configuration
Phase 2: Core Implementation  
Phase 3: TDD (RED→GREEN→REFACTOR)
Phase 4: Documentation
Phase 5: DoD Validation
```

### Exercise 4.2: Complex Plan (High Complexity)

**Try this:**

```
plan a secure authentication system with OAuth2, JWT tokens, and role-based access control
```

**What happens:**
1. CORTEX detects security/auth keywords → HIGH complexity
2. Generates incremental plan (8-12 phases)
3. Breaks down into smaller deliverables
4. Includes acceptance criteria gates
5. Per-phase TDD cycles

**Plan structure:**
```yaml
Phase 1: Requirements & Architecture
Phase 2: Database Schema (TDD)
Phase 3: OAuth2 Integration (TDD)
Phase 4: JWT Token Service (TDD)
Phase 5: RBAC Middleware (TDD)
Phase 6: API Endpoints (TDD)
Phase 7: Security Testing
Phase 8: Integration Testing
Phase 9: Documentation
Phase 10: DoD Validation
```

### Exercise 4.3: Execute Plan Autonomously

**After generating a plan, try this:**

```
execute all phases autonomously
```

**What happens:**
- Orchestrator runs each phase sequentially
- Pauses at acceptance criteria gates
- Runs TDD cycles (RED→GREEN→REFACTOR)
- Updates progress tracker automatically
- Shows completion with `# 🎉 CONGRATULATIONS`

### Exercise 4.4: View Plan Manifests

**Location:** `cortex-brain/orchestrator-manifests/planning-system-manifest.yaml`

**Key sections:**
- **compliance_requirements:** DoR/DoD checklists
- **complexity_routing:** AUTO-DETECTION rules
- **tdd_integration:** Mandatory test coverage
- **acceptance_gates:** Phase validation criteria

### ✅ Checkpoint 4

You should now be able to:
- [x] Generate low-complexity skeleton plans
- [x] Generate high-complexity incremental plans
- [x] Execute plans autonomously
- [x] Understand DoR/DoD compliance
- [x] Navigate plan manifests

---

## 🧪 Module 5: TDD Mastery Workflow

**Duration:** 10 minutes  
**Goal:** Master the RED→GREEN→REFACTOR cycle

### The TDD Philosophy

CORTEX enforces **strict TDD**:
1. **RED:** Write failing test FIRST
2. **GREEN:** Write minimal code to pass
3. **REFACTOR:** Improve code quality

**Brain Protection:** Tests must fail before implementation (RED_PHASE_VALIDATION)

### Exercise 5.1: Start TDD Workflow

**Try this:**

```
start tdd for a calculator with add and subtract functions
```

**What happens:**
1. CORTEX detects test framework (pytest, unittest, jest, etc.)
2. Creates test file structure
3. Enters RED phase
4. Guides you through each phase

### Exercise 5.2: RED Phase (Failing Tests)

**CORTEX will:**
- Generate failing test cases
- Verify tests fail (exit code ≠ 0)
- Block progression until RED confirmed

**Example test (Python):**

```python
# test_calculator.py
def test_add():
    calc = Calculator()  # Doesn't exist yet
    assert calc.add(2, 3) == 5

def test_subtract():
    calc = Calculator()
    assert calc.subtract(5, 3) == 2
```

**Run tests:**

```bash
pytest test_calculator.py  # Should FAIL
```

### Exercise 5.3: GREEN Phase (Minimal Implementation)

**CORTEX will:**
- Generate minimal passing code
- Run tests until all pass
- Enforce no over-engineering

**Example implementation:**

```python
# calculator.py
class Calculator:
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b
```

**Run tests:**

```bash
pytest test_calculator.py  # Should PASS
```

### Exercise 5.4: REFACTOR Phase (Quality Improvement)

**CORTEX will:**
- Score code quality (0-10 scale)
- Check SOLID/DRY/KISS/YAGNI principles
- Suggest refactorings
- Verify tests still pass

**Quality checks:**
- Cyclomatic complexity
- Code duplication
- Naming conventions
- Documentation coverage

### Exercise 5.5: Adaptive Technology Discovery

**Try TDD with different languages:**

```
start tdd for a TypeScript service
```

**CORTEX will:**
- Detect TypeScript
- Use Jest/Mocha
- Apply TS-specific patterns
- Store learned patterns in Tier 2

**Supported:** Python, JavaScript, TypeScript, Java, C#, Go, Rust, PHP, Ruby, Kotlin, Swift (11+ languages)

### ✅ Checkpoint 5

You should now be able to:
- [x] Start TDD workflows
- [x] Write failing tests (RED)
- [x] Implement minimal code (GREEN)
- [x] Refactor with quality checks
- [x] Use TDD across multiple languages

---

## 🧹 Module 6: Code Sanitization

**Duration:** 8 minutes  
**Goal:** Remove company-specific data for public sharing

### Use Case

You want to share your project on GitHub but it contains:
- Company names
- Internal URLs
- API endpoints
- Project-specific terminology

### Exercise 6.1: Analyze for Sanitization

**Try this:**

```
sanitize analyze ./my-project
```

**What it does:**
- Scans codebase for sensitive patterns
- Identifies company names, URLs, proprietary terms
- Generates mapping suggestions
- Estimates transformation scope

### Exercise 6.2: Create Sanitization Mapping

**CORTEX generates:** `sanitization-mapping.yaml`

```yaml
transformations:
  company_names:
    "Acme Corp": "Company"
    "Acme": "Org"
  
  domains:
    "acme.com": "example.com"
    "acme-internal.com": "internal.example.com"
  
  projects:
    "project-phoenix": "project-alpha"
    "phoenix": "alpha"
  
  api_endpoints:
    "/api/acme/v1": "/api/generic/v1"
```

### Exercise 6.3: Execute Sanitization

**Try this:**

```
sanitize execute ./my-project
```

**5-phase workflow:**
1. **Analyze:** Scan for patterns
2. **Mapping:** Load transformation rules
3. **Transform:** Apply substitutions to all files
4. **Validate:** Run builds/tests
5. **Report:** Generate audit log

**Output:**
- Sanitized codebase (in-place or new directory)
- `sanitization-audit-report.md`
- Backup of original files
- Mapping reference file

### Exercise 6.4: Verify Sanitization

**CORTEX will:**
- Run all tests (ensure functionality preserved)
- Check build success
- Validate no sensitive data leaked
- Generate confidence score

### ✅ Checkpoint 6

You should now be able to:
- [x] Analyze code for sensitive data
- [x] Create transformation mappings
- [x] Execute sanitization workflows
- [x] Validate sanitized output
- [x] Review audit reports

---

## 📊 Module 7: ADO Operations

**Duration:** 8 minutes  
**Goal:** Generate Azure DevOps work items from code

### Exercise 7.1: Generate ADO Story

**Try this:**

```
plan ado story for user authentication feature
```

**What CORTEX generates:**

```markdown
# User Story
**Title:** Implement User Authentication Feature

**As a** user  
**I want** to securely log in to the application  
**So that** I can access my personalized dashboard

## Acceptance Criteria
- [ ] Users can register with email/password
- [ ] Users can log in with valid credentials
- [ ] Invalid credentials show error message
- [ ] Session persists across page refreshes
- [ ] Logout clears session

## Technical Notes
- Use JWT for session management
- Hash passwords with bcrypt
- Implement rate limiting (5 attempts/minute)

## Test Strategy
- Unit tests for auth service
- Integration tests for API endpoints
- E2E tests for login flow

## Effort Estimate
Story Points: 8
```

### Exercise 7.2: Generate ADO Feature

**Try this:**

```
plan ado feature for e-commerce payment processing
```

**What CORTEX generates:**

```markdown
# Feature
**Title:** E-Commerce Payment Processing

## Description
Comprehensive payment processing system supporting multiple payment methods, refunds, and transaction history.

## Child Stories
1. Payment Gateway Integration (SP: 13)
2. Credit Card Processing (SP: 8)
3. PayPal Integration (SP: 5)
4. Refund Processing (SP: 5)
5. Transaction History UI (SP: 3)

## Dependencies
- PCI compliance certification
- Payment gateway API credentials
- SSL certificate

## Timeline
Epic Points: 34
Estimated Sprints: 3-4
```

### Exercise 7.3: Generate ADO Task

**Try this:**

```
plan ado task for database migration script
```

**What CORTEX generates:**

```markdown
# Task
**Title:** Create Database Migration Script v2.3

## Description
Add new columns to users table for OAuth integration.

## Steps
1. Create migration file `migrations/v2.3_add_oauth_fields.sql`
2. Add columns: `oauth_provider`, `oauth_id`, `oauth_token`
3. Update ORM models
4. Write rollback script
5. Test on dev environment

## Acceptance Criteria
- [ ] Migration runs without errors
- [ ] Rollback script tested
- [ ] ORM models updated
- [ ] Dev environment validated

## Hours
Estimated: 4 hours
```

### Exercise 7.4: Generate Completion Summary

**After implementing a feature, try this:**

```
generate ado summary for the authentication feature implementation
```

**What CORTEX generates:**

```markdown
# Implementation Summary: User Authentication Feature

## Work Completed
- ✅ JWT service implemented
- ✅ Password hashing with bcrypt
- ✅ Login/logout endpoints
- ✅ Rate limiting middleware
- ✅ Session management

## Test Coverage
- Unit tests: 24 tests (100% coverage)
- Integration tests: 12 tests
- E2E tests: 5 scenarios

## Code Review Notes
- All SOLID principles applied
- Security best practices followed
- Documentation complete

## Deployment Checklist
- [ ] Environment variables configured
- [ ] Database migrations run
- [ ] SSL certificates installed
- [ ] Rate limiting configured
```

### ✅ Checkpoint 7

You should now be able to:
- [x] Generate ADO stories
- [x] Generate ADO features
- [x] Generate ADO tasks
- [x] Create completion summaries
- [x] Understand ADO manifest inheritance

---

## 🛠️ Module 8: CORTEX Toolkit

**Duration:** 10 minutes  
**Goal:** Leverage 55+ Python tools for cross-repository operations

### Toolkit Overview

**Location:** `cortex-toolkit/`  
**Registry:** `cortex-toolkit/toolkit-manifest.yaml`  
**Documentation:** `docs/cortex-toolkit/README.md`

**8 Categories:**
1. Brain Operations (7 tools)
2. CLI Wrappers (9 tools)
3. System Operations (11 tools)
4. Planning Tools (8 tools)
5. Analytics (6 tools)
6. Testing (5 tools)
7. Migration (4 tools)
8. Utilities (5 tools)

### Exercise 8.1: Explore Toolkit Registry

**Read this file:**

```bash
# Open in VS Code:
cortex-toolkit/toolkit-manifest.yaml
```

**What to observe:**
- Tool categorization
- Relative import paths
- Usage examples
- Dependencies

### Exercise 8.2: Use CLI Wrappers

**All system operations have CLI wrappers:**

```bash
# In Copilot Chat:
"align"    # Invokes cortex-toolkit/cli/wrappers/align_wrapper.py
"cleanup"  # Invokes cortex-toolkit/cli/wrappers/cleanup_wrapper.py
```

**Wrapper benefits:**
- Consistent error handling
- Logging and telemetry
- Progress visualization
- Rollback on failure

### Exercise 8.3: Brain Operations

**Try these:**

```
# Query working memory
"What's in tier 1?"

# Query knowledge graph
"What patterns have you learned about authentication?"

# Query dev context
"What are my code hotspots?"
```

**Behind the scenes:**
- `cortex-toolkit/brain/tier1_query.py`
- `cortex-toolkit/brain/tier2_graph_query.py`
- `cortex-toolkit/brain/tier3_metrics.py`

### Exercise 8.4: Analytics Tools

**Try these:**

```
# Code complexity
"analyze complexity of src/"

# Test coverage
"what's my test coverage?"

# Technical debt
"show technical debt"
```

**Tools used:**
- `cortex-toolkit/analytics/complexity_analyzer.py`
- `cortex-toolkit/analytics/coverage_reporter.py`
- `cortex-toolkit/analytics/debt_tracker.py`

### Exercise 8.5: Cross-Repository Usage

**Key insight:** Toolkit works from ANY repo!

```bash
# From your user project:
cd ~/my-app

# Use CORTEX tools:
"plan a payment integration feature"  # Works!
"start tdd for OrderService"          # Works!
"sanitize ./src"                       # Works!
```

**How it works:**
- CORTEX detects context (CORTEX repo vs. user repo)
- Adapts behavior (admin ops disabled in user repos)
- Uses relative imports (portable across systems)

### ✅ Checkpoint 8

You should now be able to:
- [x] Navigate toolkit registry
- [x] Use CLI wrappers
- [x] Query brain operations
- [x] Run analytics tools
- [x] Use toolkit from any repository

---

## 🎓 Module 9: Advanced Operations

**Duration:** 8 minutes  
**Goal:** Master admin operations and advanced workflows

### Exercise 9.1: Architectural Review

**Admin only:**

```
review
```

**6-phase analysis:**
1. **Structure:** Analyze folder organization
2. **Modularity:** Check separation of concerns
3. **Testing:** Validate test coverage
4. **Documentation:** Check completeness
5. **Performance:** Identify bottlenecks
6. **Security:** Scan for vulnerabilities

**Output:** 0-100 score with detailed recommendations

### Exercise 9.2: System Refinement

**Admin only:**

```
refine
```

**7-phase workflow:**
1. **Discovery:** AST-based code analysis
2. **SKULL Review:** Test optimization
3. **Documentation:** Gap analysis and fixes
4. **Code Quality:** SOLID/DRY/KISS enforcement
5. **Architecture:** Pattern consistency
6. **Performance:** Optimization opportunities
7. **Validation:** Regression testing

**Duration:** 20-30 minutes

### Exercise 9.3: Upgrade System

**All users:**

```
upgrade cortex
```

**9-phase workflow:**
1. **Check:** Detect available updates
2. **Backup:** Preserve all brain tiers
3. **Download:** Fetch new version
4. **Validate:** Verify integrity
5. **Migrate:** Update schemas
6. **Test:** Run validation suite
7. **Rollback (if needed):** Restore backup
8. **Commit:** Finalize upgrade
9. **Verify:** Post-upgrade healthcheck

**Brain Protection:** Zero data loss, automatic rollback on failure

### Exercise 9.4: Deploy to Publish

**Admin only:**

```
deploy
```

**What it does:**
- Generates static documentation site (MkDocs)
- Creates GitHub Pages deployment
- Updates README files
- Publishes toolkit documentation
- Creates release notes

### ✅ Checkpoint 9

You should now be able to:
- [x] Run architectural reviews
- [x] Execute system refinement
- [x] Upgrade CORTEX safely
- [x] Deploy documentation
- [x] Understand admin vs. user tiers

---

## 💡 Module 10: Best Practices & Tips

**Duration:** 5 minutes  
**Goal:** Learn expert workflows and avoid common pitfalls

### Best Practices

#### 1. Always Search Before Creating

**SKULL Rule:** `HOLISTIC_CODE_DISCOVERY_ENFORCEMENT`

**Do this:**

```
# Before creating new feature:
"search codebase for existing authentication code"
"grep for similar implementations"
```

**Why:** Prevents duplication, discovers reusable patterns

#### 2. RED Phase is Mandatory

**SKULL Rule:** `RED_PHASE_VALIDATION`

**Do this:**

```
# Always start with failing tests:
"start tdd for UserService"  # CORTEX enforces RED first
```

**Why:** Proves tests actually validate behavior

#### 3. Use Document Organization

**SKULL Rule:** Document structure enforcement

**Do this:**

```
# Store in proper category:
cortex-brain/documents/reports/     # Status reports
cortex-brain/documents/planning/    # Feature plans
cortex-brain/documents/analysis/    # Code analysis
```

**Why:** Findability, organization, AI context retrieval

#### 4. Git Isolation

**SKULL Rule:** `GIT_ISOLATION_ENFORCEMENT`

**Do this:**

```
# CORTEX code in CORTEX repo:
/Users/you/PROJECTS/CORTEX/src/

# User app code in user repo:
/Users/you/PROJECTS/my-app/src/

# User app tests in user repo:
/Users/you/PROJECTS/my-app/tests/
```

**Why:** Prevents accidental commits, maintains boundaries

#### 5. Regular Maintenance

**Do this:**

```
# Weekly:
"healthcheck"
"cleanup"

# Monthly:
"system maintenance"  # Full 7-phase
```

**Why:** Prevents technical debt accumulation

### Common Pitfalls

#### ❌ Skipping RED Phase

```
# DON'T:
implement code without tests

# DO:
"start tdd"  # Enforces RED→GREEN→REFACTOR
```

#### ❌ Creating Root-Level Docs

```
# DON'T:
CORTEX/summary.md

# DO:
cortex-brain/documents/summaries/project-summary.md
```

#### ❌ Bypassing SKULL Rules

```
# DON'T:
ignore brain protector warnings

# DO:
fix violations and re-run operation
```

#### ❌ Manual File Operations

```
# DON'T:
manually copy/paste code between repos

# DO:
use toolkit tools: "sanitize", "migrate"
```

### Pro Tips

**1. Complexity Auto-Detection:**

```
# Mention these keywords for HIGH complexity routing:
"security", "authentication", "payment", "migration", "API gateway"
```

**2. Manifest Exploration:**

```
# Learn operation details:
cortex-brain/orchestrator-manifests/planning-system-manifest.yaml
cortex-brain/orchestrator-manifests/tdd-orchestrator-manifest.yaml
```

**3. Template Customization:**

```
# Edit response templates:
cortex-brain/response-templates-v4.yaml
```

**4. Toolkit Extension:**

```
# Add your own tools:
cortex-toolkit/custom/my_tool.py
# Register in: cortex-toolkit/toolkit-manifest.yaml
```

### ✅ Checkpoint 10

You should now know:
- [x] Search before creating (HOLISTIC discovery)
- [x] RED phase is mandatory (TDD enforcement)
- [x] Document organization rules
- [x] Git isolation boundaries
- [x] Regular maintenance schedule
- [x] Common pitfalls to avoid

---

## 🎉 Graduation & Next Steps

### Congratulations! 🎓

You've completed the CORTEX 4.0 Interactive Tutorial!

### What You've Mastered

- ✅ **Architecture:** 4-tier brain (Tier 0-3)
- ✅ **System Operations:** align, healthcheck, optimize, cleanup
- ✅ **Planning System:** LOW/HIGH complexity routing, auto-TDD
- ✅ **TDD Mastery:** RED→GREEN→REFACTOR cycle
- ✅ **Code Sanitization:** 5-phase transformation workflow
- ✅ **ADO Operations:** Stories, features, tasks, summaries
- ✅ **CORTEX Toolkit:** 55+ tools across 8 categories
- ✅ **Advanced Operations:** review, refine, upgrade, deploy
- ✅ **Best Practices:** SKULL rules, document organization, git isolation

### Recommended Next Steps

#### Beginner → Intermediate

1. **Practice planning:** Create 5-10 feature plans with varying complexity
2. **Master TDD:** Implement 3 features using full RED→GREEN→REFACTOR
3. **Explore toolkit:** Try all 8 tool categories
4. **Document learning:** Use `cortex-brain/documents/learning/` for notes

#### Intermediate → Advanced

1. **Sanitize a project:** Share one of your apps publicly
2. **Generate ADO backlog:** Create 10 work items from existing code
3. **Run refinement:** Execute full 7-phase refinement
4. **Customize templates:** Tailor response templates to your style

#### Advanced → Expert

1. **Create custom tools:** Extend toolkit with your utilities
2. **Contribute patterns:** Add learned patterns to Tier 2
3. **Optimize workflows:** Measure and improve operation performance
4. **Mentor others:** Guide teammates through this tutorial

### Reference Materials

**Essential Reads:**
- `.github/prompts/CORTEX.prompt.md` - Complete instructions
- `cortex-brain/brain-protection-rules.yaml` - SKULL rules
- `cortex-brain/response-templates-v4.yaml` - 62 templates
- `docs/cortex-toolkit/README.md` - Comprehensive toolkit guide

**Guides:**
- `cortex-brain/documents/implementation-guides/orchestrator-development-guide.md`
- `cortex-brain/documents/implementation-guides/progress-monitoring-quick-start.md`
- `cortex-brain/CODE-SANITIZATION-QUICK-REF.md`

**Manifests:**
- `cortex-operations.yaml` - All 300+ operations
- `cortex-toolkit/toolkit-manifest.yaml` - 55 tools
- `cortex-brain/orchestrator-manifests/` - Workflow specs

### Support & Community

**Need Help?**

```
# In Copilot Chat:
"help"                    # Show all commands
"help planning"           # Category-specific help
"what's new in 4.0?"     # Version changes
"troubleshoot [issue]"   # Problem solving
```

**Report Issues:**
- GitHub: [github.com/asifhussain60/CORTEX/issues](https://github.com/asifhussain60/CORTEX/issues)
- Documentation: [github.com/asifhussain60/CORTEX](https://github.com/asifhussain60/CORTEX)

### Final Exercise: Validate Your Learning

**Try this comprehensive workflow:**

```
1. "healthcheck"              # Validate system
2. "plan a blog platform"     # Generate feature plan
3. "execute all phases"       # Run end-to-end
4. "sanitize ./blog"          # Prepare for sharing
5. "generate ado summary"     # Create work item
6. "what's my test coverage?" # Check quality
7. "optimize"                 # Improve performance
```

**Success Criteria:**
- All commands execute without errors
- Plan completes with ✅ ALL WORK COMPLETE
- Tests pass (100% pass rate)
- Sanitization produces clean output
- Coverage report shows >80%

### Keep Learning

CORTEX evolves continuously. Stay updated:

```
# Check for updates:
"upgrade cortex"

# View changelog:
"what's new?"

# Regenerate docs:
"deploy"  # (admin only)
```

---

## 📊 Tutorial Completion Checklist

**Mark your progress:**

- [ ] Module 1: First Contact (help system)
- [ ] Module 2: Architecture (4-tier brain)
- [ ] Module 3: System Health (align, healthcheck, optimize, cleanup)
- [ ] Module 4: Planning System (low/high complexity)
- [ ] Module 5: TDD Mastery (RED→GREEN→REFACTOR)
- [ ] Module 6: Code Sanitization (5-phase workflow)
- [ ] Module 7: ADO Operations (stories, features, tasks)
- [ ] Module 8: CORTEX Toolkit (55+ tools)
- [ ] Module 9: Advanced Operations (review, refine, upgrade)
- [ ] Module 10: Best Practices (SKULL rules, tips)
- [ ] Final Exercise: Comprehensive workflow validation

**When all boxes are checked, you're ready to use CORTEX in production!**

---

## 📝 Notes & Feedback

**Use this space to record your learning:**

```
Key insights:
- 

Questions to explore:
- 

Custom workflows discovered:
- 

Tools I use most:
- 
```

---

**Tutorial Version:** 4.0.0  
**Author:** Asif Hussain  
**Copyright © 2025 Asif Hussain. All rights reserved.**  
**GitHub:** [github.com/asifhussain60/CORTEX](https://github.com/asifhussain60/CORTEX)
