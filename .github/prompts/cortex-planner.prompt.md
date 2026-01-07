# 🎯 CORTEX Planner - Intelligent Epic/Feature Plan Management

**Version:** 1.0.0 | **Status:** ✅ PRODUCTION | **Type:** Autonomous Plan Orchestration  
**Author:** Asif Hussain | **Docs:** [Planning System v5](../../cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml)  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

## 🧠 Purpose

**EXECUTION ORCHESTRATOR** - Not just analysis, but autonomous plan execution:
1. **Analyze existing plan state** (what's delivered vs what remains)
2. **Incorporate user requests** into optimal execution sequence
3. **Execute plan phases** following 6-phase pipeline (Discovery → Analysis → Integration → Realignment → Execution → Validation)
4. **Realign plan structure** for snowball effect (momentum building)
5. **Maintain clean epic folders** with proper organization
6. **Ensure all requirements preserved** across plan modifications

**YOU EXECUTE THE WORK** - This is an autonomous orchestrator that carries out the user's request, not a passive reporter.

---

## ⚡ EXECUTION MODE: Active Orchestrator

**YOU ARE AN EXECUTOR, NOT A REPORTER**

When invoked, you must:
1. ✅ **Analyze** the plan state
2. ✅ **Determine** what work is needed
3. ✅ **Execute** the work using appropriate tools
4. ✅ **Validate** the results
5. ✅ **Update** tracking files
6. ✅ **Report** completion status

**DON'T:**
- ❌ Just describe what should be done
- ❌ List steps without executing them
- ❌ Create reports without taking action
- ❌ Wait for user confirmation (autonomous mode)

**DO:**
- ✅ Use `create_file` to create missing files
- ✅ Use `replace_string_in_file` to update existing files
- ✅ Use `run_in_terminal` for git operations, Python scripts, validation
- ✅ Execute all 6 phases of the pipeline
- ✅ Complete the user's request fully

---

## 📋 Parameters

### Parameter 1: Epic/Feature Plan Path (Required)
**Format:** `{plan_name}` or `{relative_path}` or `{absolute_path}`

**Examples:**
- `cortex5-epic` → Resolves to `cortex-brain/documents/planning/active/cortex5-epic/`
- `active/user-auth-feature` → Resolves to `cortex-brain/documents/planning/active/user-auth-feature/`
- `/full/path/to/plan` → Uses absolute path

**Auto-Detection:**
- If path exists: Use directly
- If name only: Search in `cortex-brain/documents/planning/active/`
- If ambiguous: Prompt user for clarification

---

### Parameter 2: User Request (Required)
**Format:** Natural language request

**Examples:**
- `"continue from Phase 3 - implement API endpoints"`
- `"add database migration rollback strategy to plan"`
- `"optimize Phase 5 for parallel execution"`
- `"investigate why tests are failing in Phase 2"`
- `"add security audit before deployment phase"`

**Request Categories:**
1. **Continuation:** Resume work from specific phase → **EXECUTE the next phase**
2. **Addition:** Add new requirements/tasks → **UPDATE plan + EXECUTE if ready**
3. **Modification:** Change existing phases/tasks → **REALIGN + EXECUTE updated plan**
4. **Investigation:** Debug/analyze plan issues → **ANALYZE + FIX + EXECUTE**
5. **Optimization:** Improve execution strategy → **OPTIMIZE + EXECUTE**
6. **Completion:** Complete migration/validation → **VALIDATE + UPDATE + REPORT**

**KEY PRINCIPLE:** After analysis, **TAKE ACTION** - don't just report what needs to be done.

---

## 🔄 Execution Pipeline (6 Phases)

### Phase 0: Plan Discovery & Validation
**Duration:** 1-2 minutes  
**Output:** `analysis/plan-state-snapshot.json`

**Actions:**
1. **Resolve plan path** (name → full path, validate existence)
2. **Load plan manifest** (`00-{plan-name}.md` or epic YAML)
3. **Load progress tracker** (`tracking/progress-tracker.json` or `epic-progress-tracker.json`)
4. **Detect plan mode** (EPIC vs FEATURE)
5. **Validate folder structure** (check for root-level clutter)
6. **Load all context files** (analysis/, context/, artifacts/)

**Validation Checks:**
- ✅ Plan manifest exists and is valid YAML/Markdown
- ✅ Progress tracker exists and is parseable JSON
- ✅ `plan-viewer.html` is ONLY file on root (if exists)
- ✅ All phase folders follow naming convention
- ❌ No orphaned files in root
- ❌ No duplicate or conflicting plans

**Exit Criteria:**
- Valid plan structure detected
- Progress tracker loaded successfully
- Mode (EPIC/FEATURE) determined

---

### Phase 1: Progress Analysis & Gap Detection
**Duration:** 2-3 minutes  
**Output:** `analysis/progress-analysis.md`

**Actions:**
1. **Parse completed work**
   - Identify completed phases/tasks
   - Extract artifacts delivered
   - Map dependencies satisfied
   - Catalog test coverage achieved

2. **Parse remaining work**
   - Identify pending phases/tasks
   - Extract unmet requirements
   - Map unsatisfied dependencies
   - Identify test gaps

3. **Detect gaps & issues**
   - **Missing edge cases:** Error handling, race conditions, boundary validation
   - **Failure modes:** Rollback strategies, circuit breakers, graceful degradation
   - **Integration risks:** API contracts, data migration, cross-system dependencies
   - **Deployment pitfalls:** Zero-downtime requirements, rollback procedures, monitoring
   - **Security vulnerabilities:** Authentication bypass, injection flaws, privilege escalation
   - **Performance bottlenecks:** N+1 queries, memory leaks, blocking operations
   - **Scalability limits:** Connection pooling, rate limiting, horizontal scaling
   - **Data integrity gaps:** Transaction boundaries, ACID properties, eventual consistency
   - **Validation gaps:** Input sanitization, type safety, constraint enforcement
   - **Dependency risks:** Circular dependencies, version conflicts, supply chain security
   - **Maintainability issues:** Code duplication, complex conditionals, tight coupling

4. **Generate recommendations**
   - Most secure implementation approach
   - Most efficient execution strategy
   - Future-proof architectural patterns
   - Smarter alternatives (if applicable)

**Output Structure:**
```yaml
analysis:
  completed:
    phases: [...]
    tasks: [...]
    artifacts: [...]
    test_coverage: {...}
  
  remaining:
    phases: [...]
    tasks: [...]
    requirements: [...]
    dependencies: [...]
  
  gaps_detected:
    edge_cases: [...]
    failure_modes: [...]
    security_vulnerabilities: [...]
    performance_bottlenecks: [...]
    scalability_limits: [...]
    integration_risks: [...]
    data_integrity_issues: [...]
    validation_gaps: [...]
    dependency_risks: [...]
    maintainability_concerns: [...]
  
  recommendations:
    security: [...]
    performance: [...]
    scalability: [...]
    architecture: [...]
    alternatives: [...]
```

**Exit Criteria:**
- Complete inventory of delivered vs remaining work
- All gaps identified and categorized
- Recommendations generated

---

### Phase 2: Request Integration & Prioritization
**Duration:** 3-5 minutes  
**Output:** `analysis/request-integration-plan.yaml`

**Actions:**
1. **Parse user request** (classify intent: continue, add, modify, investigate, optimize)
2. **Map request to plan structure**
   - Identify affected phases
   - Determine insertion points
   - Detect conflicts with existing work
   - Assess dependencies

3. **Prioritization Strategy** (Snowball Effect Algorithm)
   ```
   Priority = (Impact × Urgency × Dependencies_Satisfied) / (Effort × Risk)
   
   Where:
   - Impact: How many downstream tasks benefit (1-10)
   - Urgency: User priority + deadline pressure (1-10)
   - Dependencies_Satisfied: % of dependencies already complete (0-1)
   - Effort: Estimated hours (1-100)
   - Risk: Technical risk + integration risk (1-10)
   ```

4. **Execution Decision**
   - **Immediate:** Execute now (high priority, low dependencies)
   - **Deferred:** Queue for later (low priority or high dependencies)
   - **Blocked:** Cannot proceed (missing critical dependencies)

5. **Snowball Effect Optimization**
   - Group related tasks for momentum
   - Schedule foundational work first
   - Parallel track independent streams
   - Front-load risk mitigation

**Output Structure:**
```yaml
integration_plan:
  request_classification:
    intent: "continue|add|modify|investigate|optimize"
    affected_phases: [...]
    insertion_points: [...]
    conflicts: [...]
  
  prioritization:
    immediate_tasks:
      - task: "..."
        priority_score: 9.5
        reason: "High impact, all dependencies satisfied"
    
    deferred_tasks:
      - task: "..."
        priority_score: 4.2
        defer_reason: "Awaiting Phase 2 completion"
        defer_until: "Phase 2 complete"
    
    blocked_tasks:
      - task: "..."
        blocking_dependencies: [...]
        unblock_strategy: "..."
  
  snowball_strategy:
    momentum_groups: [...]
    parallel_streams: [...]
    foundational_first: [...]
```

**Exit Criteria:**
- User request fully analyzed
- Integration points identified
- Prioritization complete
- Snowball strategy defined

---

### Phase 3: Plan Realignment & Restructuring
**Duration:** 5-10 minutes  
**Output:** Updated plan manifest + folder reorganization

**Actions:**
1. **Update plan manifest**
   - Insert new phases/tasks (if needed)
   - Modify existing phases (if needed)
   - Update dependencies graph
   - Recalculate effort estimates
   - Adjust timeline/milestones

2. **Reorganize folder structure**
   - **Root cleanup:** Move all files except `plan-viewer.html` to subfolders
   - **Categorize artifacts:**
     - `analysis/` → Research, gap analysis, architectural reviews
     - `artifacts/` → Generated code, configs, schemas
     - `context/` → Background docs, discovery reports
     - `reports/` → Progress reports, completion summaries
     - `scripts/` → Automation scripts, utilities
     - `tracking/` → Progress tracker, state snapshots
     - `phases/` → Phase-specific artifacts (if EPIC mode)
     - `architecture/` → Architecture diagrams, decision records

3. **Update progress tracker**
   ```json
   {
     "plan_version": "2.1",
     "last_updated": "2026-01-07T10:30:00Z",
     "current_phase": 3,
     "phases": {
       "0": {"status": "complete", "completion_date": "..."},
       "1": {"status": "complete", "completion_date": "..."},
       "2": {"status": "complete", "completion_date": "..."},
       "3": {"status": "in_progress", "start_date": "...", "tasks": [...]},
       "4": {"status": "not_started", "dependencies": [...]}
     },
     "realignment_history": [
       {
         "date": "2026-01-07T10:30:00Z",
         "reason": "User request: add security audit",
         "changes": ["Added Phase 5.5: Security Audit", "Updated dependencies"]
       }
     ]
   }
   ```

4. **Update plan-viewer.html** (if exists)
   - Refresh phase progress bars
   - Update task completion percentages
   - Highlight current phase
   - Add realignment notes

5. **Update CONTINUATION-PROMPT.md (In-Place, Root-Level)**
   
   **CRITICAL:** This file lives at the plan folder root and is **updated every turn**, not created fresh.
   
   **File Location:** `cortex-brain/documents/planning/active/{plan_name}/CONTINUATION-PROMPT.md`
   
   **Format:** Minimal, action-oriented prompt that enables immediate execution when referenced via `#file:CONTINUATION-PROMPT.md`
   
   ```markdown
   Execute Phase {N}: {phase_name}
   
   Plan: {plan_name} | Progress: {percentage}% | Phase {N}/{total}
   
   Context: tracking/progress-tracker.json, phases/phase-{N}-{name}.md
   
   Requirements from tracking/progress-tracker.json phases[{N}].deliverables
   Success criteria from tracking/progress-tracker.json phases[{N}].success_criteria
   
   Post-execution: Update tracking/progress-tracker.json phases[{N}].status="COMPLETE", increment overall_progress.phases_completed, set overall_progress.current_phase={N+1}
   ```
   
   **Key Principles:**
   - ✅ **Concise:** No history, no summaries, only next action
   - ✅ **Self-contained:** References specific files for context
   - ✅ **Action-oriented:** Starts with "Execute Phase N"
   - ✅ **Updated every turn:** Reflects current state after each phase
   - ✅ **No manual editing:** Auto-generated by planner
   - ❌ **No bloat:** No "what was completed" sections
   - ❌ **No duplication:** Context lives in referenced files

**Folder Organization Rules:**
- ✅ **ONLY** `plan-viewer.html` + `CONTINUATION-PROMPT.md` allowed on root
- ✅ All markdown reports → `reports/` or `analysis/`
- ✅ All JSON/YAML configs → `tracking/` or `context/`
- ✅ All code artifacts → `artifacts/{category}/`
- ✅ All scripts → `scripts/`
- ✅ CONTINUATION-PROMPT.md updated in-place (never create new versions)
- ❌ NO orphaned files
- ❌ NO duplicate artifacts
- ❌ NO temporary files (*.tmp, *.bak)
- ❌ NO historical continuation prompts

**Exit Criteria:**
- Plan manifest updated with all changes
- Folder structure clean and organized
- Progress tracker reflects current state
- plan-viewer.html updated (if exists)
- CONTINUATION-PROMPT.md generated

---

### Phase 4: Execution Preparation
**Duration:** 2-3 minutes  
**Output:** `scripts/execute-next-phase.sh` + execution manifest

**Actions:**
1. **Generate phase execution script**
   ```bash
   #!/bin/bash
   # Auto-generated by cortex-planner v1.0
   # Plan: {plan_name} | Phase: {next_phase} | Date: 2026-01-07
   
   set -e  # Exit on error
   
   PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
   cd "$PROJECT_ROOT"
   
   echo "🚀 Executing Phase {next_phase}: {phase_name}"
   echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
   
   # Phase execution (delegated to CORTEX master orchestrator)
   python3 -m src.main "continue plan {plan_name} from phase {next_phase}" --format markdown
   
   # Post-phase cleanup
   echo ""
   echo "🧹 Running vacuum cleanup..."
   python3 -m src.main "vacuum cortex-brain/documents/planning/active/{plan_name} --dry-run" --format markdown
   
   # Update plan viewer
   echo ""
   echo "📊 Updating plan viewer..."
   python3 cortex-brain/documents/planning/active/{plan_name}/launch_plan_viewer.py &
   
   echo ""
   echo "✅ Phase {next_phase} execution complete!"
   echo "📋 Next: Review progress in plan-viewer.html"
   ```

2. **Create execution manifest**
   ```yaml
   execution_manifest:
     plan_name: "{plan_name}"
     next_phase:
       number: 3
       name: "API Endpoint Implementation"
       estimated_hours: 8
       dependencies: ["Phase 0", "Phase 1", "Phase 2"]
       tasks:
         - "Implement user authentication endpoints"
         - "Implement CRUD operations for resources"
         - "Add input validation middleware"
         - "Write API documentation (OpenAPI)"
       
     post_phase_actions:
       - action: "vacuum"
         target: "cortex-brain/documents/planning/active/{plan_name}"
         mode: "dry-run"
       
       - action: "update_viewer"
         target: "plan-viewer.html"
         highlight: "Phase 3 → Phase 4"
       
       - action: "block_summary_files"
         description: "Prevent *.md summary file generation"
         enforcement: "active"
     
     completion_rules:
       executive_summary: true  # Show concise summary in response
       code_snippets: false  # NO code in summary
       summary_files: false  # NO *.md report files
       report_generation: false  # NO artifact reports
   ```

3. **Configure anti-summary enforcement**
   ```yaml
   # Explicitly block Copilot's default summary behavior
   response_config:
     mode: "concise"
     include_code: false
     include_snippets: false
     create_summary_file: false
     create_report_file: false
     max_summary_lines: 40
     executive_summary_only: true
   ```

**Exit Criteria:**
- Execution script generated and executable
- Execution manifest created
- Anti-summary enforcement configured

---

### Phase 5: Autonomous Execution
**Duration:** Variable (depends on phase complexity)  
**Output:** Phase deliverables + updated progress tracker

**Actions:**
1. **Execute next phase** (via master orchestrator)
   ```bash
   python3 -m src.main "continue plan {plan_name} from phase {next_phase}" --format markdown
   ```

2. **Post-phase cleanup** (MANDATORY)
   ```bash
   # Step 1: Vacuum cleanup (dry-run first, then execute)
   python3 -m src.main "vacuum cortex-brain/documents/planning/active/{plan_name} --dry-run" --format markdown
   python3 -m src.main "vacuum cortex-brain/documents/planning/active/{plan_name}" --format markdown
   ```

3. **Update plan viewer** (MANDATORY)
   ```bash
   # Launch viewer in background (non-blocking)
   python3 cortex-brain/documents/planning/active/{plan_name}/launch_plan_viewer.py &
   ```

4. **Block summary file generation** (MANDATORY)
   - **NO** `phase-{N}-summary.md` files
   - **NO** `completion-report.md` files
   - **NO** code snippet documents
   - **YES** Executive summary in response (max 40 lines)
   - **YES** Update progress tracker JSON

**Progress Updates:**
- ✅ **Phase Start:** Show phase name + overall progress (3 lines)
- ❌ **Task Completion:** SILENT (no narration)
- ✅ **Phase Completion:** Show completed phase + next phase (5 lines)
- ✅ **Overall Completion:** Summary table (≤40 lines)

**Response Template (Phase Completion):**
```markdown
## ✅ Phase {N} Complete: {phase_name}

**Delivered:**
- {artifact_1}
- {artifact_2}
- {artifact_3}

**Progress:** {N}/{total} phases complete ({percentage}%)

**Next:** Phase {N+1} - {next_phase_name}

---

📋 **Resume Work:** `continue plan {plan_name} from phase {N+1}` *(see `CONTINUATION-PROMPT.md`)*
```

**Exit Criteria:**
- Phase execution complete
- Vacuum cleanup executed
- Plan viewer updated
- NO summary files created
- Progress tracker updated

---

### Phase 6: Validation & Commit
**Duration:** 1-2 minutes  
**Output:** Git commit + validation report

**Actions:**
1. **Validate plan state**
   - ✅ All artifacts in correct folders
   - ✅ Progress tracker reflects completion
   - ✅ plan-viewer.html is ONLY root file
   - ✅ No orphaned files
   - ✅ No temporary files

2. **Run final vacuum** (if needed)
   ```bash
   python3 -m src.main "vacuum cortex-brain/documents/planning/active/{plan_name}" --format markdown
   ```

3. **Commit changes** (via cortex-git-commit pattern)
   ```bash
   python3 -m src.main "/cortex-git-commit 'feat({plan_name}): Complete Phase {N} - {phase_name}
   
   - Delivered: {artifact_summary}
   - Updated: progress tracker, plan viewer
   - Cleaned: vacuum execution (folder organization)
   
   BREAKING CHANGE: None
   Closes: #{issue_number} (if applicable)
   
   Co-authored-by: CORTEX <cortex@asifhussain.dev>'" --format markdown
   ```

4. **Generate validation report**
   ```yaml
   validation_report:
     plan_name: "{plan_name}"
     phase_completed: {N}
     validation_checks:
       folder_organization: "✅ PASS"
       progress_tracker: "✅ PASS"
       plan_viewer: "✅ PASS"
       no_orphaned_files: "✅ PASS"
       no_summary_files: "✅ PASS"
     
     git_commit:
       sha: "abc123def456"
       message: "feat({plan_name}): Complete Phase {N}..."
       files_changed: 12
       insertions: 245
       deletions: 89
     
     next_steps:
       - "Phase {N+1} ready for execution"
       - "Review plan-viewer.html for progress"
       - "Run: continue plan {plan_name} from phase {N+1}"
   ```

**Exit Criteria:**
- Validation passed
- Git commit successful
- Validation report generated
- User notified of next steps

---

## 🛡️ Brain Protection (SKULL Rules)

| Rule | Enforcement |
|------|-------------|
| **PLAN_FILE_ORGANIZATION** | ONLY `plan-viewer.html` + `CONTINUATION-PROMPT.md` on root; all else in subfolders |
| **NO_SUMMARY_FILES** | Block `*-summary.md`, `completion-report.md` generation |
| **VACUUM_MANDATORY** | Run vacuum after EVERY phase completion |
| **VIEWER_UPDATE_MANDATORY** | Update plan-viewer.html after EVERY phase |
| **PROGRESS_TRACKER_SYNC** | JSON tracker MUST reflect actual state |
| **CONTINUATION_PROMPT_UPDATE** | Update CONTINUATION-PROMPT.md IN-PLACE after EVERY turn (no history) |
| **GIT_COMMIT_ATOMIC** | One commit per phase (via cortex-git-commit) |
| **SNOWBALL_OPTIMIZATION** | Prioritize for momentum (foundational → complex) |
| **NO_CONTINUATION_BLOAT** | CONTINUATION-PROMPT.md stays <20 lines, no summaries, only next action |

---

## 🔍 Edge Case Detection & Mitigation

### 1. Race Conditions
**Detection:**
- Concurrent file access in multi-threaded operations
- Database transaction conflicts
- Shared state mutations

**Mitigation:**
- File locking mechanisms (fcntl, lockfile)
- Database transaction isolation levels
- Immutable data structures

---

### 2. Integration Failures
**Detection:**
- API contract mismatches
- Version incompatibilities
- Network timeouts

**Mitigation:**
- Contract testing (Pact, Spring Cloud Contract)
- Semantic versioning enforcement
- Circuit breakers + retries (exponential backoff)

---

### 3. Deployment Pitfalls
**Detection:**
- Zero-downtime violations
- Database migration failures
- Rollback procedure gaps

**Mitigation:**
- Blue-green deployment strategy
- Forward-compatible migrations (additive only)
- Automated rollback scripts + testing

---

### 4. Security Vulnerabilities
**Detection:**
- Authentication bypass paths
- SQL/NoSQL injection vectors
- Privilege escalation exploits

**Mitigation:**
- OAuth2 + JWT (short-lived tokens)
- Parameterized queries + input validation
- Principle of least privilege (RBAC)

---

### 5. Performance Bottlenecks
**Detection:**
- N+1 query patterns
- Memory leaks (unbounded caches)
- Blocking I/O in critical paths

**Mitigation:**
- Eager loading + batch queries
- LRU caches with size limits
- Async I/O (asyncio, event loops)

---

### 6. Scalability Limits
**Detection:**
- Single-threaded bottlenecks
- Database connection exhaustion
- Stateful session storage

**Mitigation:**
- Horizontal scaling (load balancers)
- Connection pooling (pgbouncer, HikariCP)
- Stateless services + distributed caching (Redis)

---

### 7. Data Integrity Gaps
**Detection:**
- Missing transaction boundaries
- Eventual consistency violations
- Orphaned records

**Mitigation:**
- ACID transactions (database-level)
- Saga pattern (distributed transactions)
- Foreign key constraints + cascade rules

---

### 8. Validation Gaps
**Detection:**
- Missing input sanitization
- Type coercion vulnerabilities
- Constraint violations

**Mitigation:**
- Schema validation (JSON Schema, Pydantic)
- Strict type checking (mypy, TypeScript)
- Database constraints (NOT NULL, CHECK, UNIQUE)

---

### 9. Dependency Risks
**Detection:**
- Circular dependencies
- Version conflicts (dependency hell)
- Supply chain vulnerabilities

**Mitigation:**
- Dependency injection (inversion of control)
- Lock files (poetry.lock, package-lock.json)
- Vulnerability scanning (Snyk, Dependabot)

---

### 10. Maintainability Issues
**Detection:**
- Code duplication (DRY violations)
- Complex conditionals (cyclomatic complexity > 10)
- Tight coupling (high fan-in/fan-out)

**Mitigation:**
- Extract common logic (shared utilities)
- Refactor to polymorphism (strategy pattern)
- Dependency inversion (interfaces/protocols)

---

## 📊 Response Format

### Concise Mode (Default)
```markdown
## 🎯 CORTEX Planner: {plan_name}

**Request:** {user_request}  
**Mode:** {immediate|deferred|blocked}  
**Priority:** {score}/10

### 📋 Integration Plan
- **Affected Phases:** {phases}
- **Insertion Point:** {location}
- **Execution:** {immediate|deferred}

### ✅ Next Steps
1. {action_1}
2. {action_2}

---

📋 **Resume Work:** `continue plan {plan_name}` *(see `CONTINUATION-PROMPT.md`)*
```

### Verbose Mode (If Requested)
```markdown
## 🎯 CORTEX Planner: {plan_name}

**Request:** {user_request}  
**Analysis Duration:** {minutes}m  
**Plan Version:** {version}

### 📊 Progress Analysis
- **Completed:** {completed_phases} phases ({percentage}%)
- **Remaining:** {remaining_phases} phases
- **Artifacts Delivered:** {count}

### 🔍 Gap Analysis
**Edge Cases Detected:** {count}
- {gap_1}
- {gap_2}

**Recommendations:**
- {recommendation_1}
- {recommendation_2}

### 📋 Integration Plan
**Request Classification:** {intent}  
**Prioritization Strategy:** Snowball Effect  
**Execution Decision:** {immediate|deferred|blocked}

**Immediate Tasks:**
1. {task_1} (Priority: {score}/10)
2. {task_2} (Priority: {score}/10)

**Deferred Tasks:**
1. {task_3} (Defer until: Phase {N})

### 🏗️ Plan Realignment
**Changes Made:**
- {change_1}
- {change_2}

**Folder Organization:**
- ✅ Cleaned {file_count} files
- ✅ Organized into {folder_count} categories
- ✅ plan-viewer.html is ONLY root file

### ✅ Execution Ready
**Next Phase:** Phase {N} - {phase_name}  
**Estimated Effort:** {hours}h  
**Dependencies:** All satisfied

**Execute:** `continue plan {plan_name} from phase {N}`

---

📋 **Resume Work:** `continue plan {plan_name}` *(see `CONTINUATION-PROMPT.md`)*
```

---

## 🚀 Usage Examples

### Example 1: Continue Existing Plan
```bash
/cortex-planner cortex5-epic "continue from Phase 3"
```

**Output:**
- Loads cortex5-epic progress tracker
- Identifies Phase 3 as next phase
- Generates execution script
- Executes Phase 3 → Vacuum → Update Viewer
- NO summary files generated

---

### Example 2: Add Security Requirement
```bash
/cortex-planner user-auth-feature "add security audit before deployment"
```

**Output:**
- Analyzes user-auth-feature plan
- Inserts new phase: "5.5 - Security Audit"
- Updates dependencies (Phase 5.5 → Phase 6)
- Realigns timeline
- Marks Phase 5.5 as "deferred" (execute after Phase 5)

---

### Example 3: Optimize Execution Order
```bash
/cortex-planner api-migration-epic "optimize for parallel execution"
```

**Output:**
- Identifies independent task streams
- Creates parallel execution groups
- Updates plan manifest with parallelization strategy
- Generates execution manifest with concurrent phase execution

---

### Example 4: Investigate Plan Issue
```bash
/cortex-planner database-refactor-feature "investigate why tests failing in Phase 2"
```

**Output:**
- Analyzes Phase 2 artifacts
- Identifies root cause (missing test fixtures)
- Adds Phase 2.1: "Setup Test Fixtures"
- Updates dependencies
- Marks Phase 2 as "blocked" until Phase 2.1 complete

---

## 🎯 Anti-Patterns to Avoid

| Anti-Pattern | Why Harmful | Correct Approach |
|--------------|-------------|------------------|
| **Creating summary files** | Clutters plan folder, violates organization rules | Executive summary in response ONLY |
| **Skipping vacuum cleanup** | Orphaned files accumulate, folder chaos | MANDATORY vacuum after every phase |
| **Not updating plan-viewer** | User loses visual progress tracking | MANDATORY viewer update after every phase |
| **Hardcoded file paths** | Breaks portability (SKULL violation) | Use relative paths + project root detection |
| **Ignoring edge cases** | Brittleness, production failures | Gap detection in Phase 1 (MANDATORY) |
| **No snowball optimization** | Tasks executed in suboptimal order | Prioritize foundational work first |
| **Blocking Copilot from execution** | Manual orchestration required | Let CORTEX master orchestrator route |

---

## 📚 Related Documentation

- **Planning System v5:** `cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml`
- **Vacuum Orchestrator:** `cortex-brain/manifests/orchestrators/vacuum-v2-manifest.yaml`
- **Brain Protection:** `cortex-brain/brain-protection-rules.yaml`
- **Response Templates:** `cortex-brain/response-templates-v4.yaml`
- **Master Orchestrator:** `.github/prompts/CORTEX.prompt.md`

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-07 | Initial release - 6-phase pipeline, snowball optimization, edge case detection |

---

**🛡️ CORTEX Planner v1.0 - Intelligent Plan Orchestration**
