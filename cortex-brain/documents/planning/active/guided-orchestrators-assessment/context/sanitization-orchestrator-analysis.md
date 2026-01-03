# Sanitization Orchestrator Evaluation

**Orchestrator Name:** Code Sanitization Orchestrator  
**Current Type:** 📋 GUIDED  
**Evaluator:** Asif Hussain (CORTEX AI)  
**Evaluation Date:** January 3, 2026

---

## 🔍 Current Implementation Analysis

### 1. Location & Structure

**Manifest File:** `cortex-brain/manifests/orchestrators/code-sanitization-manifest.yaml`  
**Prompt File(s):** [Not found - manifest-based orchestration]  
**Supporting Files:** None currently (planned implementation)

**Current Status:** Active manifest (Version 1.0.0)

### 2. Current Workflow Description

**Phase Structure:**
```
Phase 1: Discovery & Analysis - Scan codebase, identify domain-specific terms
Phase 2: Generate Transformation Mapping - Create domain→generic mappings (USER APPROVAL)
Phase 3: Execute Transformation - Apply mappings, backup files, rename
Phase 4: Build & Test Validation - Verify builds + tests pass
Phase 5: Generate Audit Report - Document transformation with traceability
```

**Total Phases:** 5 (well-defined linear progression)  
**Linear vs Branching:** Linear with conditional rollback (validation failure → auto-rollback)

### 3. Current Capabilities

**Primary Functions:**
- Scan codebase for domain-specific terminology
- Detect sensitive data (API keys, credentials, PII/PHI)
- Generate generic replacement mappings (domain→generic)
- Transform code (namespaces, classes, variables, documentation)
- Rename files and directories
- Validate transformation (build + test parity)
- Rollback on validation failure
- Generate audit trail

**Key Operations:**
- **AST Manipulation:** Transform namespaces, using statements, imports (C#, Python, TypeScript)
- **Regex Replacement:** Documentation, configuration files
- **Structure-Aware Transformation:** JSON, YAML, XML, OpenAPI specs
- **Multi-language Support:** C#, Python, TypeScript, Markdown, config files
- **Backup Management:** Create backup before transformation
- **Build System Detection:** .NET, Python, Node.js
- **Test Execution:** Run tests, compare pass rates

### 4. Integration Points

**Dependencies:**
- Master Orchestrator: ⏸️ Not configured (planned)
- BaseOrchestrator: ⏸️ N/A (GUIDED, not yet converted)
- PlanningStateDB: ⏸️ Not integrated (would benefit from state tracking)
- Other Orchestrators: None currently

**Tool Calls Used:**
- File system operations (read, write, rename, backup)
- AST parsing (Roslyn for C#, ast for Python, TypeScript parser)
- Regex matching (sensitive data detection)
- Build system execution (dotnet build, pytest, npm)
- Test execution (dotnet test, pytest, npm test)

---

## 📊 Decision Matrix Scoring

### Criterion 1: Operation Complexity (Weight: 30%)

**Assessment:**
- **AST manipulation:** ✅ YES
  - Transform C# namespaces (using Roslyn)
  - Update Python imports (ast module)
  - Modify TypeScript imports
  - Preserve code structure while transforming identifiers
  
- **Multi-phase workflow:** ✅ YES - **5 phases** with conditional rollback
  - Linear progression: Analyze → Map → Transform → Validate → Report
  - Conditional branch: Validation failure → Automatic rollback to backup
  
- **Complex algorithms:** ✅ YES
  - Sensitive data detection (API keys, credentials, PII patterns)
  - Namespace conflict resolution
  - Dependency graph analysis (ensure no broken references)
  - Build system auto-detection
  - Test result comparison (pass rate parity)
  
- **Multi-file analysis:** ✅ YES
  - Workspace-wide terminology scanning
  - Cross-file reference tracking (namespace dependencies)
  - Bulk transformation across all file types

**Raw Score:** **9/10** (Very High Complexity)

**Rationale:**
- AST manipulation (+3): Multi-language (C#, Python, TypeScript)
- Multi-phase workflow (+2): 5 phases with rollback logic
- Complex algorithms (+2): Sensitive data detection, conflict resolution
- Multi-file analysis (+2): Workspace-wide transformation
- **Total:** 9 operational complexity indicators

**Weighted Score:** 9 × 0.30 = **2.70**

---

### Criterion 2: State Management (Weight: 25%)

**Assessment:**
- **Requires rollback:** ✅ YES - **CRITICAL**
  - Validation failure → Automatic rollback to backup
  - Build failure → Restore pre-transformation state
  - Test regression → Revert transformation
  - Manual abort → Rollback capability
  
- **Multi-phase state:** ✅ YES - **5 phases** with persistence needs
  - Track: original files backed up
  - Track: transformation mappings applied
  - Track: files renamed
  - Track: validation results
  
- **Progress persistence:** ✅ BENEFICIAL
  - Resume sanitization after interruption
  - Track which files already transformed
  - Store mapping dictionary for consistency
  
- **Transaction boundaries:** ✅ YES
  - Atomic transformation: All files transformed or none
  - Atomic validation: Build + tests must both pass
  - Backup creation before any changes

**Raw Score:** **10/10** (Critical State Management)

**Rationale:**
- Requires rollback (+4): Validation failures require complete revert
- Multi-phase state (+3): 5 phases with complex state tracking
- Progress persistence (+2): Resumption beneficial for large codebases
- Transaction boundaries (+1): Multiple atomic operations required
- **Total:** All state management indicators present (critical safety requirements)

**Weighted Score:** 10 × 0.25 = **2.50**

---

### Criterion 3: User Interaction (Weight: 20%)

**Assessment:**
- **Automation level:** Minimal Interaction (1 approval gate)
  - Approval gate 1: Transformation mapping approval (Phase 2)
    - User reviews domain→generic mappings
    - Can modify suggestions before transformation
    - Critical safety gate (prevent unwanted changes)
  - Otherwise autonomous execution
  
- **Approval gates:** 1 primary gate (Phase 2 mapping approval)
  - Additional implicit approval: Run command initiates full workflow
  - User can abort before Phase 3 execution
  
- **Conversational elements:** ⏸️ NO
  - Not exploratory or iterative
  - Deterministic workflow: analyze → map → transform → validate → report
  
- **Iterative refinement:** ⏸️ LIMITED
  - User can modify mappings in Phase 2
  - Otherwise linear execution

**Raw Score:** **8/10** (Minimal Interaction)

**Rationale:**
- Mostly automated workflow (80% autonomous)
- 1 strategic approval gate (mapping review for safety)
- Not conversational or exploratory
- Fits autonomous model with pre-execution approval

**Weighted Score:** 8 × 0.20 = **1.60**

---

### Criterion 4: Maintenance Cost (Weight: 15%)

**Assessment:**
- **Logic complexity:** ✅ Complex
  - Multi-language AST transformation logic
  - Regex pattern library for sensitive data
  - Build system detection heuristics
  - Test result comparison algorithms
  - Namespace conflict resolution
  
- **Update frequency:** ✅ Regularly expected
  - New file types supported (Java, Go, Rust)
  - Enhanced sensitive data patterns (new API key formats)
  - Additional build system support
  - Improved conflict resolution
  
- **Debug difficulty:** ✅ Hard with manifests
  - Current YAML approach difficult to test transformation logic
  - Python implementation enables unit tests for each transformation
  - IDE support for debugging AST operations
  
- **Test coverage:** ⏸️ None currently (manifest-based)
  - AUTONOMOUS enables 100% test coverage requirement
  - Critical for data safety (ensure no sensitive data leaks)

**Raw Score:** **10/10** (High Maintenance Benefits from Python)

**Rationale:**
- Complex logic benefits from IDE support, debugging, unit tests
- Regular updates expected (new languages, patterns, build systems)
- Python significantly easier to maintain for complex transformations
- Test coverage critical for security (sensitive data handling)

**Weighted Score:** 10 × 0.15 = **1.50**

---

### Criterion 5: Code Reusability (Weight: 10%)

**Assessment:**
- **Shared utilities:** ✅ Moderate reuse potential
  - **AST Transformation Library:** Reusable by Debug (marker injection), Refinement (code improvements)
  - **Sensitive Data Detector:** Reusable pattern for security scans
  - **Backup/Rollback Manager:** Generic pattern for safe file operations
  - **Build System Detector:** Useful for TDD, Debug orchestrators
  
- **Used by other orchestrators:** 🟡 Potential for 2-3
  - Debug: AST transformation patterns
  - Vacuum: Safe file operations with rollback
  - Refinement: Code transformation utilities
  
- **Potential for reuse:** ✅ Moderate
  - Sanitization logic is somewhat domain-specific
  - But utilities (AST, backup, validation) are generic
  
- **Unique vs generic logic:** ~50% unique (sanitization-specific), 50% reusable (AST, backup, validation)

**Raw Score:** **7/10** (Moderate Reusability)

**Rationale:**
- AST transformation patterns reusable
- Backup/rollback utilities generic
- Sensitive data detection somewhat specific
- Build system detection already useful for other orchestrators

**Weighted Score:** 7 × 0.10 = **0.70**

---

## 🎯 Final Score & Recommendation

| Criterion | Weight | Raw Score | Weighted Score |
|-----------|--------|-----------|----------------|
| Operation Complexity | 30% | 9/10 | 2.70 |
| State Management | 25% | 10/10 | 2.50 |
| User Interaction | 20% | 8/10 | 1.60 |
| Maintenance Cost | 15% | 10/10 | 1.50 |
| Code Reusability | 10% | 7/10 | 0.70 |
| **TOTAL** | **100%** | **44/50** | **9.00/10** |

---

### Recommendation: ✅ **AUTONOMOUS** (STRONG)

**Confidence Level:** ✅ **HIGH**

**Primary Rationale:**
Sanitization Orchestrator scores **9.00/10** - firmly in STRONG AUTONOMOUS territory. The critical state management requirements (rollback on validation failure), complex multi-language AST transformation, and security-critical operations (sensitive data handling) make this an ideal candidate for AUTONOMOUS conversion. The 5-phase workflow with transaction boundaries requires database state tracking that only AUTONOMOUS architecture provides.

**Key Decision Factors:**
1. **Critical Rollback Requirements (10/10):** Validation failures MUST trigger complete rollback to backup - requires transactional database state
2. **Multi-Language AST Complexity (9/10):** Transform C#, Python, TypeScript code - Python provides first-class AST support
3. **Security-Critical Operations (10/10):** Sensitive data detection requires exhaustive testing - AUTONOMOUS enables 100% coverage
4. **Maintenance Benefits (10/10):** Complex transformation logic easier to maintain in Python than YAML manifests

**Strategic Alignment:**
- 5-phase workflow maps cleanly to BaseOrchestrator v4.1 phase execution model
- Approval gate (Phase 2 mapping approval) fits autonomous approval hook pattern
- Master Orchestrator routing enables deterministic sanitization invocation
- State database supports resumption for large codebase transformations

---

## 🏗️ Migration Roadmap

### Effort Estimate

**Total Duration:** 2 days

**Phase Breakdown:**
- **Day 1:** Core SanitizationOrchestratorV2 + Transformation Engine (8 hours)
  - BaseOrchestrator v4.1 scaffolding
  - Multi-language AST transformation engine (C#/Python/TypeScript)
  - Sensitive data detector (regex pattern library)
  - Mapping generator (domain→generic)
  - Backup/rollback manager
  
- **Day 2:** Validation + Testing + Master Orchestrator Integration (8 hours)
  - Build system detector + executor
  - Test execution + comparison
  - 100% test coverage (unit + integration)
  - Master Orchestrator routing configuration
  - Response template integration
  - Documentation

### Implementation Strategy

**New Files to Create:**
```
src/orchestrators/sanitization/
├── sanitization_orchestrator_v2.py    # Main orchestrator (BaseOrchestrator v4.1)
├── ast_transformer.py                 # Multi-language AST transformation
├── sensitive_data_detector.py         # Pattern-based sensitive data scanner
├── mapping_generator.py               # Domain→generic mapping generation
├── backup_manager.py                  # Backup creation + rollback
├── build_validator.py                 # Build + test execution
└── __init__.py

cortex-brain/manifests/orchestrators/
└── sanitization-orchestrator-v2.yaml  # Configuration manifest (AUTONOMOUS)

cortex-brain/templates/sanitization/
├── analysis_complete.jinja2           # Phase 1 complete
├── mapping_approval.jinja2            # Phase 2 approval required
├── transformation_progress.jinja2     # Phase 3 progress
├── validation_complete.jinja2         # Phase 4 complete
└── sanitization_report.jinja2         # Phase 5 final report

tests/orchestrators/sanitization/
├── test_sanitization_orchestrator_v2.py
├── test_ast_transformer.py
├── test_sensitive_data_detector.py
├── test_mapping_generator.py
├── test_backup_manager.py
└── test_build_validator.py
```

### Key Components

1. **Core Orchestrator:** SanitizationOrchestratorV2
   - 5-phase workflow state machine
   - Approval gate at Phase 2 (mapping approval)
   - Automatic rollback on validation failure
   - DoR: Source directory valid, write permissions
   - DoD: Build passes, test parity, zero sensitive data leaks, audit report generated

2. **AST Transformer:**
   - Multi-language support (C#/Roslyn, Python/ast, TypeScript)
   - Namespace/import transformation
   - Variable/class/function renaming
   - Preserve code structure and formatting
   - Conflict detection (namespace collisions)

3. **Sensitive Data Detector:**
   - Regex pattern library:
     - API keys (AWS, Azure, Google, GitHub)
     - Credentials (passwords, tokens, secrets)
     - PII/PHI (emails, SSNs, phone numbers)
     - Connection strings
     - Company-specific identifiers
   - Confidence scoring for detections
   - False positive filtering

4. **Mapping Generator:**
   - Domain terminology extraction from codebase
   - Generic name suggestions (payment, customer, account_type)
   - Conflict resolution (ensure unique generic names)
   - User-editable mapping dictionary
   - Preview diff generation

5. **Backup Manager:**
   - Create timestamped backup before transformation
   - Track original file locations
   - Atomic rollback (restore all files on validation failure)
   - Backup retention (30 days default)
   - Cleanup old backups

6. **Build Validator:**
   - Auto-detect build system (.NET, Python, Node.js)
   - Execute build command
   - Run test suite
   - Compare test pass rates (original vs sanitized)
   - Generate validation report

### Master Orchestrator Integration

**Routing Pattern:**
```yaml
- pattern: "^(sanitize|sanitization|make.*generic).*$"
  orchestrator: sanitization_orchestrator_v2
  confidence: 1.0
  match_type: regex
  priority: 40
  metadata:
    description: "Code Sanitization v2 (Domain→Generic Transformation)"
    autonomous: true
    lifecycle_hooks:
      - pre_execution: validate_source_directory
      - post_execution: cleanup_temp_files
    security:
      sensitive_data_handling: true
      audit_logging: true
```

### Testing Strategy

**Test Coverage Requirements:**
- Unit tests: **100% coverage** (all components)
- Integration tests: **6 scenarios**
  1. C# codebase sanitization (namespace transformation)
  2. Python codebase sanitization (import transformation)
  3. TypeScript codebase sanitization (import transformation)
  4. Multi-language codebase (mixed C#/Python/TypeScript)
  5. Validation failure → automatic rollback
  6. Sensitive data detection (API keys, credentials)
  
- End-to-end tests: **3 workflows**
  1. Full sanitization: analyze → map → transform → validate → report
  2. User mapping modification (override generated mappings)
  3. Rollback on validation failure

**Critical Test Cases:**
1. **Sensitive Data Leakage Prevention:** Ensure zero API keys/credentials in sanitized code
2. **Namespace Conflict Resolution:** Unique generic names generated
3. **Build Parity:** Sanitized code builds without errors
4. **Test Parity:** Test pass rate ≥ original
5. **Rollback Integrity:** Validation failure → complete restore to original
6. **Multi-Language:** C#/Python/TypeScript transformations all work
7. **Documentation Update:** Comments/docs reflect generic terminology
8. **Backup Creation:** Timestamped backup before transformation

### SKULL Enforcement

**Applicable Rules:**
- `HOLISTIC_CODE_DISCOVERY_ENFORCEMENT`: Scan entire workspace before transforming
  - Application: Phase 1 discovers all files, dependencies before creating mappings
  
- `GIT_CHECKPOINT_ENFORCEMENT`: Checkpoint after successful sanitization
  - Application: Git checkpoint after Phase 5 complete (audit report generated)
  
- `REFACTOR_CODE_CLEANUP_ENFORCEMENT`: Cleanup temporary files
  - Application: Remove backup after retention period, cleanup intermediate artifacts
  
- `PROGRESS_TRACKER_ENFORCEMENT`: Visual progress tracking
  - Application: Response templates show phase progression (Phase 1/5, Phase 2/5, etc.)
  
- `OPERATIONAL_READINESS_ENFORCEMENT`: DoR/DoD checklists
  - Application: DoR (source valid, write permissions), DoD (build passes, test parity, audit report)

**Additional Security Rules:**
- **SENSITIVE_DATA_VALIDATION:** Verify zero sensitive data in sanitized code
- **AUDIT_TRAIL_REQUIRED:** Generate detailed transformation audit report
- **ROLLBACK_CAPABILITY_MANDATORY:** All transformations must support rollback

---

## 📊 Risk Assessment

### Risks of Converting to AUTONOMOUS

**Technical Risks:**
- **Risk 1:** AST transformation breaks code syntax
  - **Mitigation:** Comprehensive test suite, validation phase catches issues before deployment
  
- **Risk 2:** Sensitive data detector misses some patterns
  - **Mitigation:** Extensive regex pattern library, confidence scoring, manual review option
  
- **Risk 3:** Rollback fails to restore original state
  - **Mitigation:** Test rollback extensively, verify backup integrity before transformation

**Resource Risks:**
- Development time: 2 days investment (16 hours engineering time)
- Testing complexity: Requires test codebases in multiple languages
- **Mitigation:** Use existing CORTEX codebase for testing (C#/Python/TypeScript present)

**Maintenance Risks:**
- **Risk 1:** New language support requires AST parser additions
  - **Mitigation:** Extensible architecture, clear API for adding new languages

### Risks of Remaining GUIDED

**Technical Risks:**
- **Risk 1:** Manifest-based approach cannot express complex transformation logic
  - **Impact:** Error-prone transformations, no rollback, inconsistent sanitization
  
- **Risk 2:** No state persistence for multi-phase workflow
  - **Impact:** Cannot resume sanitization for large codebases, lose progress on failure
  
- **Risk 3:** Security risk: Difficult to test sensitive data detection in manifests
  - **Impact:** Potential for sensitive data leaks in sanitized code

**Operational Risks:**
- **Risk 1:** Low code reusability (AST transformation logic not shared)
  - **Impact:** Duplicate implementation if Debug/Refinement need code transformation

**Verdict:** Risks of remaining GUIDED **significantly outweigh** risks of converting to AUTONOMOUS (especially security risks).

---

## 📝 Additional Notes

### Security Considerations

Sanitization is **security-critical** - sensitive data leaks can cause:
- API key exposure → Unauthorized access
- Credential leaks → Security breaches
- PII/PHI exposure → Compliance violations (GDPR, HIPAA)

**AUTONOMOUS benefits for security:**
- 100% test coverage requirement → Exhaustive validation
- Python unit tests → Test each regex pattern independently
- Transactional rollback → Safe failure handling
- Audit logging → Complete traceability

### Alignment with Existing Manifest

Current `code-sanitization-manifest.yaml` (v1.0.0) provides excellent foundation:
- Well-defined 5-phase workflow
- Clear transformation rules (domain→generic mappings)
- Rollback capabilities specified
- Quality gates defined

**Migration will preserve:**
- Phase structure (5 phases unchanged)
- Approval gate (mapping approval in Phase 2)
- Rollback logic (validation failure → restore)
- Audit reporting requirements

### Synergy with Other Migrations

1. **Debug Orchestrator v2 (Approved):** Can reuse AST transformation patterns
2. **Vacuum Orchestrator v2 (Complete):** Can share backup/rollback utilities
3. **Refinement (TBD):** May benefit from code transformation patterns

---

## ✅ Approval

**Evaluator:** Asif Hussain (CORTEX AI)  
**Date:** January 3, 2026  
**Status:** ✅ **RECOMMENDATION COMPLETE**

**Recommendation:** ✅ **AUTONOMOUS CONVERSION APPROVED**

**Next Steps:**
1. Present evaluation to stakeholders (Engineering, Security, Compliance teams)
2. Generate migration plan via Planning v5: `/CORTEX Plan Sanitization Orchestrator v2 Migration`
3. Schedule 2-day implementation window
4. Execute migration with 100% test coverage requirement (especially sensitive data detection)
5. Security review before activation (ensure no data leak vulnerabilities)
6. Progressive activation after successful validation

**Comments:**
Sanitization Orchestrator scores 9.00/10 - firmly in STRONG AUTONOMOUS territory. The combination of security-critical operations, multi-language AST transformation, and mandatory rollback capabilities make this textbook autonomous material. The existing manifest provides excellent foundation for migration. Security considerations (sensitive data handling) strongly favor exhaustive Python unit testing over manifest-based approach.
