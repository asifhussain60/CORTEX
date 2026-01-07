# 🏋️ CORTEX 4.0 Practice Exercises

**Version:** 4.0.0  
**Author:** Asif Hussain  
**Last Updated:** December 27, 2025  
**Total Exercises:** 30  
**Difficulty Levels:** Beginner, Intermediate, Advanced

---

## 📋 Exercise Categories

1. [System Operations](#system-operations-exercises) (6 exercises)
2. [Planning System](#planning-system-exercises) (5 exercises)
3. [TDD Mastery](#tdd-mastery-exercises) (5 exercises)
4. [Code Sanitization](#code-sanitization-exercises) (4 exercises)
5. [ADO Operations](#ado-operations-exercises) (4 exercises)
6. [CORTEX Toolkit](#cortex-toolkit-exercises) (6 exercises)

---

## 🔧 System Operations Exercises

### Exercise 1.1: Daily Startup Routine

**Difficulty:** Beginner  
**Duration:** 3 minutes

**Task:**
1. Run healthcheck
2. If errors found, run align
3. Verify all tiers operational
4. Document any warnings

**Success Criteria:**
- ✅ Healthcheck returns 100% operational
- ✅ Zero errors or warnings
- ✅ All databases accessible

**Commands:**
```
healthcheck
align
healthcheck
```

---

### Exercise 1.2: Weekly Cleanup

**Difficulty:** Beginner  
**Duration:** 5 minutes

**Task:**
1. Run healthcheck (baseline)
2. Run cleanup
3. Note files removed
4. Run healthcheck (validation)
5. Compare before/after metrics

**Success Criteria:**
- ✅ At least 5 orphaned files removed
- ✅ No test failures introduced
- ✅ Disk space reclaimed

**Commands:**
```
healthcheck
cleanup
healthcheck
```

---

### Exercise 1.3: Performance Optimization

**Difficulty:** Intermediate  
**Duration:** 8 minutes

**Task:**
1. Measure baseline query performance (Tier 1/2)
2. Run optimize
3. Measure post-optimization performance
4. Calculate improvement percentage
5. Document optimizations applied

**Success Criteria:**
- ✅ Query time reduced by >20%
- ✅ Database indices rebuilt
- ✅ Cache hit rate improved

**Commands:**
```
what's my tier 1 query performance?
optimize
what's my tier 1 query performance?
```

---

### Exercise 1.4: Configuration Drift Resolution

**Difficulty:** Intermediate  
**Duration:** 10 minutes

**Task:**
1. Manually corrupt `cortex.config.json` (change a path)
2. Run healthcheck (should fail)
3. Run align
4. Verify auto-fix restored correct configuration
5. Document what was fixed

**Success Criteria:**
- ✅ Align detects corrupted config
- ✅ Auto-fix restores valid paths
- ✅ Healthcheck passes after align

**Commands:**
```
# Manual: Edit cortex.config.json
healthcheck
align
healthcheck
```

---

### Exercise 1.5: Full Maintenance Workflow

**Difficulty:** Advanced  
**Duration:** 15 minutes

**Task:**
1. Run system maintenance (7 phases)
2. Monitor each phase completion
3. Analyze final healthcheck report
4. Calculate total improvements
5. Document lessons learned

**Success Criteria:**
- ✅ All 7 phases complete
- ✅ Shows `# 🎉 CONGRATULATIONS`
- ✅ Zero errors in final healthcheck
- ✅ Measurable performance gains

**Commands:**
```
system maintenance
```

---

### Exercise 1.6: System Integrity Validation

**Difficulty:** Advanced  
**Duration:** 20 minutes

**Task:**
1. Run system integrity check
2. Review master plan alignment
3. Validate test pass rate (100%)
4. Check documentation completeness
5. Verify manifest accuracy
6. Fix any issues found

**Success Criteria:**
- ✅ Master plan 100% aligned
- ✅ All tests passing
- ✅ Documentation complete
- ✅ Manifests validated

**Commands:**
```
system integrity
```

---

## 📋 Planning System Exercises

### Exercise 2.1: Simple Feature Plan

**Difficulty:** Beginner  
**Duration:** 5 minutes

**Task:**
Create a plan for: "A contact form with name, email, and message fields"

**Expected Outcome:**
- LOW complexity detected
- 4-5 phase skeleton plan
- TDD phase included
- DoR/DoD checklist

**Commands:**
```
plan a contact form with name, email, and message fields
```

**Validation:**
- Plan has <6 phases
- TDD phase present
- Acceptance criteria defined

---

### Exercise 2.2: Medium Complexity Plan

**Difficulty:** Intermediate  
**Duration:** 8 minutes

**Task:**
Create a plan for: "A dashboard with charts, filters, and real-time data updates"

**Expected Outcome:**
- MEDIUM complexity detected
- 6-8 phase conditional plan
- Multiple TDD phases
- Phase dependencies mapped

**Commands:**
```
plan a dashboard with charts, filters, and real-time data updates
```

**Validation:**
- Plan has 6-8 phases
- TDD in multiple phases
- Real-time considerations addressed

---

### Exercise 2.3: High Complexity Plan

**Difficulty:** Advanced  
**Duration:** 12 minutes

**Task:**
Create a plan for: "A secure multi-tenant SaaS platform with OAuth2, role-based access, and audit logging"

**Expected Outcome:**
- HIGH complexity detected
- 10+ phase incremental plan
- Security considerations
- Acceptance gates between phases

**Commands:**
```
plan a secure multi-tenant SaaS platform with OAuth2, role-based access, and audit logging
```

**Validation:**
- Plan has 10+ phases
- Security keywords triggered HIGH routing
- Per-phase acceptance criteria
- Audit logging addressed

---

### Exercise 2.4: Autonomous Execution

**Difficulty:** Advanced  
**Duration:** 20 minutes

**Task:**
1. Generate plan for: "A REST API for managing tasks with CRUD operations"
2. Execute all phases autonomously
3. Monitor progress tracker
4. Verify TDD cycles complete
5. Validate DoD checklist

**Expected Outcome:**
- Plan completes end-to-end
- All tests passing
- DoD 100% complete
- Shows `# 🎉 CONGRATULATIONS`

**Commands:**
```
plan a REST API for managing tasks with CRUD operations
execute all phases autonomously
```

**Validation:**
- All phases marked complete
- Test coverage >80%
- API endpoints functional

---

### Exercise 2.5: Plan Modification

**Difficulty:** Advanced  
**Duration:** 15 minutes

**Task:**
1. Generate plan for a feature
2. Review generated phases
3. Request modifications: "Add a performance optimization phase"
4. Execute modified plan
5. Verify custom phase included

**Expected Outcome:**
- CORTEX incorporates custom phase
- Phase integrates with existing workflow
- TDD still enforced

**Commands:**
```
plan a blog post management system
# Review plan
Add a performance optimization phase before DoD
execute all phases autonomously
```

**Validation:**
- Custom phase appears in plan
- Execution includes custom phase
- No regression introduced

---

## 🧪 TDD Mastery Exercises

### Exercise 3.1: Basic TDD Cycle

**Difficulty:** Beginner  
**Duration:** 10 minutes

**Task:**
Implement a `Calculator` class with `add()` and `subtract()` methods using TDD.

**Expected Outcome:**
- RED: Tests fail (class doesn't exist)
- GREEN: Tests pass (minimal implementation)
- REFACTOR: Code quality score >8/10

**Commands:**
```
start tdd for a Calculator class with add and subtract methods
```

**Validation:**
- [ ] RED phase confirmed (tests fail)
- [ ] GREEN phase confirmed (tests pass)
- [ ] REFACTOR improves quality
- [ ] Final tests 100% passing

---

### Exercise 3.2: Multi-Language TDD

**Difficulty:** Intermediate  
**Duration:** 15 minutes

**Task:**
Implement TDD for a `UserService` in 3 languages: Python, TypeScript, Java

**Expected Outcome:**
- CORTEX adapts to each language
- Uses appropriate test frameworks
- Applies language-specific patterns

**Commands:**
```
# Python
start tdd for UserService in Python

# TypeScript
start tdd for UserService in TypeScript

# Java
start tdd for UserService in Java
```

**Validation:**
- [ ] Python uses pytest
- [ ] TypeScript uses Jest
- [ ] Java uses JUnit
- [ ] All 3 pass TDD cycle

---

### Exercise 3.3: TDD with External Dependencies

**Difficulty:** Advanced  
**Duration:** 20 minutes

**Task:**
Implement TDD for a service that calls an external API (mock the API)

**Expected Outcome:**
- Tests use mocking/stubbing
- External API isolated
- Tests run without network

**Commands:**
```
start tdd for a WeatherService that calls an external weather API
```

**Validation:**
- [ ] API calls mocked
- [ ] Tests run offline
- [ ] Error handling tested
- [ ] All edge cases covered

---

### Exercise 3.4: Refactoring Complex Code

**Difficulty:** Advanced  
**Duration:** 25 minutes

**Task:**
1. Implement a feature with TDD
2. Intentionally create high complexity (nested loops, long functions)
3. Run REFACTOR phase
4. Verify CORTEX improves quality

**Expected Outcome:**
- Initial quality score <6/10
- CORTEX suggests refactorings
- Final quality score >8/10

**Commands:**
```
start tdd for a complex order processing system
# Implement with high complexity
# Run REFACTOR phase
```

**Validation:**
- [ ] Complexity reduced
- [ ] SOLID principles applied
- [ ] Tests still pass
- [ ] Code more maintainable

---

### Exercise 3.5: TDD Coverage Validation

**Difficulty:** Intermediate  
**Duration:** 15 minutes

**Task:**
1. Implement feature with TDD
2. Check coverage report
3. Identify untested branches
4. Add missing tests
5. Achieve >90% coverage

**Expected Outcome:**
- Coverage report generated
- Missing branches identified
- Tests added for all branches
- >90% coverage achieved

**Commands:**
```
start tdd for a ShoppingCart class
what's my test coverage for ShoppingCart?
# Add missing tests
what's my test coverage for ShoppingCart?
```

**Validation:**
- [ ] Coverage >90%
- [ ] All branches tested
- [ ] Edge cases covered

---

## 🧹 Code Sanitization Exercises

### Exercise 4.1: Basic Sanitization

**Difficulty:** Beginner  
**Duration:** 10 minutes

**Task:**
Create a sample project with company names, then sanitize it.

**Steps:**
1. Create `demo-app/` with hardcoded "Acme Corp"
2. Run sanitization analysis
3. Review mapping suggestions
4. Execute sanitization
5. Verify "Acme Corp" removed

**Commands:**
```
sanitize analyze ./demo-app
sanitize execute ./demo-app
```

**Validation:**
- [ ] All "Acme Corp" replaced
- [ ] Tests still pass
- [ ] Audit report generated

---

### Exercise 4.2: Multi-Domain Sanitization

**Difficulty:** Intermediate  
**Duration:** 15 minutes

**Task:**
Sanitize a project with:
- Company names (3 variations)
- Internal URLs (5 endpoints)
- Project codenames (2 names)

**Expected Outcome:**
- Mapping file with 10+ transformations
- All sensitive data removed
- Build successful

**Commands:**
```
sanitize analyze ./complex-app
# Review mapping
sanitize execute ./complex-app
```

**Validation:**
- [ ] 10+ transformations applied
- [ ] URLs anonymized
- [ ] Codenames replaced
- [ ] Tests pass

---

### Exercise 4.3: Sanitization with API Keys

**Difficulty:** Advanced  
**Duration:** 20 minutes

**Task:**
Sanitize a project containing:
- Hardcoded API keys
- Database credentials
- Internal IP addresses

**Expected Outcome:**
- All secrets removed
- Replaced with placeholders
- .env.example created
- Security scan clean

**Commands:**
```
sanitize analyze ./api-project
# Review security findings
sanitize execute ./api-project
verify no secrets leaked
```

**Validation:**
- [ ] No secrets in code
- [ ] .env.example present
- [ ] Security scan clean

---

### Exercise 4.4: Large Codebase Sanitization

**Difficulty:** Advanced  
**Duration:** 30 minutes

**Task:**
Sanitize a 10,000+ line codebase with:
- 50+ files
- Multiple languages (Python, TypeScript)
- Complex domain terminology

**Expected Outcome:**
- Transformation mapping >50 rules
- All files processed
- No functionality broken
- Audit report comprehensive

**Commands:**
```
sanitize analyze ./large-app
sanitize execute ./large-app
run all tests
```

**Validation:**
- [ ] All files sanitized
- [ ] Tests 100% passing
- [ ] Build successful
- [ ] Audit complete

---

## 📊 ADO Operations Exercises

### Exercise 5.1: Generate User Story

**Difficulty:** Beginner  
**Duration:** 5 minutes

**Task:**
Generate an ADO User Story for: "User can reset their password via email"

**Expected Outcome:**
- Story title, description
- Acceptance criteria (5+ items)
- Test strategy
- Effort estimate (story points)

**Commands:**
```
plan ado story for user password reset via email
```

**Validation:**
- [ ] Story formatted correctly
- [ ] Acceptance criteria clear
- [ ] Test strategy included
- [ ] Story points estimated

---

### Exercise 5.2: Generate Feature with Child Stories

**Difficulty:** Intermediate  
**Duration:** 10 minutes

**Task:**
Generate an ADO Feature for: "E-commerce checkout flow" with 5 child stories

**Expected Outcome:**
- Feature overview
- 5 child stories listed
- Dependencies mapped
- Timeline estimated

**Commands:**
```
plan ado feature for e-commerce checkout flow
```

**Validation:**
- [ ] Feature comprehensive
- [ ] 5+ child stories
- [ ] Dependencies clear
- [ ] Timeline reasonable

---

### Exercise 5.3: Generate Task Breakdown

**Difficulty:** Intermediate  
**Duration:** 8 minutes

**Task:**
Generate an ADO Task for: "Implement caching layer with Redis"

**Expected Outcome:**
- Task title, description
- Step-by-step breakdown
- Acceptance criteria
- Hour estimate

**Commands:**
```
plan ado task for implementing caching layer with Redis
```

**Validation:**
- [ ] Steps actionable
- [ ] Criteria testable
- [ ] Hours realistic
- [ ] Technical details included

---

### Exercise 5.4: Generate Completion Summary

**Difficulty:** Advanced  
**Duration:** 15 minutes

**Task:**
After implementing a feature, generate ADO completion summary with:
- Work completed
- Test coverage
- Code review notes
- Deployment checklist

**Expected Outcome:**
- Comprehensive summary
- Metrics included
- Deployment ready

**Commands:**
```
# After feature implementation
generate ado summary for authentication feature
```

**Validation:**
- [ ] All sections complete
- [ ] Metrics accurate
- [ ] Deployment checklist included

---

## 🛠️ CORTEX Toolkit Exercises

### Exercise 6.1: Brain Operations

**Difficulty:** Beginner  
**Duration:** 8 minutes

**Task:**
Query all 4 brain tiers:
1. Tier 0: SKULL rules
2. Tier 1: Recent conversations
3. Tier 2: Learned patterns
4. Tier 3: Code hotspots

**Commands:**
```
show me brain protection rules
what's in my working memory?
what patterns have you learned about authentication?
what are my code hotspots?
```

**Validation:**
- [ ] Tier 0 returns SKULL rules
- [ ] Tier 1 shows conversations
- [ ] Tier 2 shows patterns
- [ ] Tier 3 shows metrics

---

### Exercise 6.2: Analytics Tools

**Difficulty:** Intermediate  
**Duration:** 12 minutes

**Task:**
Run full analytics suite:
1. Complexity analysis
2. Test coverage
3. Technical debt
4. Code duplication

**Commands:**
```
analyze complexity of src/
what's my test coverage?
show technical debt
find duplicate code
```

**Validation:**
- [ ] Complexity report generated
- [ ] Coverage >80%
- [ ] Debt items identified
- [ ] Duplicates found

---

### Exercise 6.3: CLI Wrapper Exploration

**Difficulty:** Beginner  
**Duration:** 10 minutes

**Task:**
Execute all 9 CLI wrappers:
1. align
2. healthcheck
3. optimize
4. cleanup
5. review
6. deploy
7. regenerate_prompts
8. upgrade
9. refine

**Commands:**
```
align
healthcheck
optimize
cleanup
# (admin only: review, deploy, regenerate_prompts, refine)
upgrade cortex --check
```

**Validation:**
- [ ] All wrappers execute successfully
- [ ] Consistent output format
- [ ] Progress visualization

---

### Exercise 6.4: Custom Tool Creation

**Difficulty:** Advanced  
**Duration:** 30 minutes

**Task:**
Create a custom toolkit tool:
1. Create `cortex-toolkit/custom/my_analyzer.py`
2. Register in `toolkit-manifest.yaml`
3. Implement functionality (e.g., dependency analyzer)
4. Test with sample project
5. Document usage

**Expected Outcome:**
- Tool follows toolkit patterns
- Registered properly
- Works from any repo

**Validation:**
- [ ] Tool created
- [ ] Manifest updated
- [ ] Tool functional
- [ ] Documentation complete

---

### Exercise 6.5: Cross-Repository Usage

**Difficulty:** Intermediate  
**Duration:** 15 minutes

**Task:**
1. Navigate to user project (outside CORTEX)
2. Use 5 CORTEX toolkit tools
3. Verify tools work correctly
4. Compare behavior vs. CORTEX repo

**Commands:**
```bash
cd ~/my-user-project
# In Copilot Chat:
plan a feature
start tdd
what's my test coverage?
analyze complexity
healthcheck
```

**Validation:**
- [ ] All tools work from user repo
- [ ] Admin ops disabled (expected)
- [ ] Context properly detected

---

### Exercise 6.6: Toolkit Performance

**Difficulty:** Advanced  
**Duration:** 20 minutes

**Task:**
Measure toolkit performance:
1. Baseline query times (Tier 1/2)
2. Run optimize
3. Measure post-optimization
4. Calculate improvements
5. Document bottlenecks

**Commands:**
```
# Measure baseline
time tier 1 query for "authentication"
optimize
# Measure after
time tier 1 query for "authentication"
```

**Validation:**
- [ ] Baseline measured
- [ ] Optimization applied
- [ ] >20% improvement
- [ ] Bottlenecks identified

---

## 📊 Exercise Completion Tracker

**Mark your progress:**

### System Operations (6/6)
- [ ] Exercise 1.1: Daily Startup
- [ ] Exercise 1.2: Weekly Cleanup
- [ ] Exercise 1.3: Performance Optimization
- [ ] Exercise 1.4: Configuration Drift
- [ ] Exercise 1.5: Full Maintenance
- [ ] Exercise 1.6: System Integrity

### Planning System (5/5)
- [ ] Exercise 2.1: Simple Plan
- [ ] Exercise 2.2: Medium Complexity
- [ ] Exercise 2.3: High Complexity
- [ ] Exercise 2.4: Autonomous Execution
- [ ] Exercise 2.5: Plan Modification

### TDD Mastery (5/5)
- [ ] Exercise 3.1: Basic TDD Cycle
- [ ] Exercise 3.2: Multi-Language TDD
- [ ] Exercise 3.3: TDD with Dependencies
- [ ] Exercise 3.4: Refactoring Complex Code
- [ ] Exercise 3.5: TDD Coverage Validation

### Code Sanitization (4/4)
- [ ] Exercise 4.1: Basic Sanitization
- [ ] Exercise 4.2: Multi-Domain
- [ ] Exercise 4.3: API Keys/Secrets
- [ ] Exercise 4.4: Large Codebase

### ADO Operations (4/4)
- [ ] Exercise 5.1: User Story
- [ ] Exercise 5.2: Feature with Children
- [ ] Exercise 5.3: Task Breakdown
- [ ] Exercise 5.4: Completion Summary

### CORTEX Toolkit (6/6)
- [ ] Exercise 6.1: Brain Operations
- [ ] Exercise 6.2: Analytics Tools
- [ ] Exercise 6.3: CLI Wrappers
- [ ] Exercise 6.4: Custom Tool Creation
- [ ] Exercise 6.5: Cross-Repository Usage
- [ ] Exercise 6.6: Toolkit Performance

**Total:** 0/30 exercises complete

---

## 🎓 Completion Certificate

**When all 30 exercises are complete, you've earned:**

```
╔═══════════════════════════════════════════════════╗
║                                                   ║
║       CORTEX 4.0 PRACTICE MASTERY CERTIFICATE    ║
║                                                   ║
║   This certifies that [YOUR NAME]                ║
║   has successfully completed all 30 exercises    ║
║   in the CORTEX 4.0 Practice Suite.              ║
║                                                   ║
║   Exercises Completed: 30/30                     ║
║   Completion Date: [DATE]                        ║
║                                                   ║
║   Skills Mastered:                               ║
║   ✓ System Operations                            ║
║   ✓ Planning System                              ║
║   ✓ TDD Mastery                                  ║
║   ✓ Code Sanitization                            ║
║   ✓ ADO Operations                               ║
║   ✓ CORTEX Toolkit                               ║
║                                                   ║
║   Issued by: Asif Hussain                        ║
║   CORTEX Version: 4.0.0                          ║
║                                                   ║
╚═══════════════════════════════════════════════════╝
```

---

**Practice Exercises Version:** 4.0.0  
**Author:** Asif Hussain  
**Copyright © 2025 Asif Hussain. All rights reserved.**  
**GitHub:** [github.com/asifhussain60/CORTEX](https://github.com/asifhussain60/CORTEX)
