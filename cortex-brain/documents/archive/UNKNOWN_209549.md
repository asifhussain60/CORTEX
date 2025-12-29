    Operational readiness validation required!

    Operation: '{operation}'
    Status: '{status}'

    ❌ BLOCKED: Cannot declare deployment/upgrade complete without operational validation

    **Real-World Failure (upgrade-issue.md):**
    - User upgraded CORTEX (files copied successfully)
    - NumPy failed to install (missing C compiler)
    - Tests not discoverable (incorrect path)
    - Manual verification took 45+ minutes
    - Declared "success" but CORTEX was not operational

    **Required Validation Gates:**

    Gate 1: Environment Prerequisites
    - [ ] Python 3.8+ available
    - [ ] pip functional
    - [ ] git available
    - [ ] Disk space sufficient (500+ MB)
    - [ ] Write permissions verified
    - [ ] C compiler available (optional, warn if missing)

    Gate 2: Core Dependencies
    - [ ] pytest installed and importable
    - [ ] PyYAML installed and importable
    - [ ] watchdog installed and importable
    - [ ] psutil installed and importable
    - [ ] send2trash installed and importable

    Gate 3: Optional Dependencies (warn only)
    - [ ] NumPy installed (ML features)
    - [ ] scikit-learn installed (ML features)
    - [ ] pandas installed (data analysis)

    Gate 4: Core Imports
    - [ ] from tier1.working_memory import WorkingMemory
    - [ ] from tier3.development_context import DevelopmentContext
    - [ ] No import errors

    Gate 5: Database Accessibility
    - [ ] cortex-brain/tier1/working_memory.db exists
    - [ ] cortex-brain/tier2/knowledge_graph.db exists (or auto-init)
    - [ ] cortex-brain/tier3/development_context.db exists

    Gate 6: Configuration Validation
    - [ ] cortex-operations.yaml exists and valid
    - [ ] response-templates.yaml exists and valid
    - [ ] brain-protection-rules.yaml exists and valid

    Gate 7: Test Suite Validation
    - [ ] pytest --collect-only succeeds
    - [ ] At least 10 tests discovered
    - [ ] Smoke test passes (optional, warn only)

    **Rollback Triggers (Critical Failures):**
    - Core dependency import fails
    - Core module import fails
    - Tier 1 or Tier 3 database missing
    - Operations config invalid
    - Response templates invalid
    - Brain protection rules invalid

    **Success Criteria:**
    ✅ ALL gates pass (or warnings only)
    ✅ Time to operational: <5 minutes
    ✅ Zero manual intervention required
    ✅ User sees clear validation summary

    **Implementation:**
    - upgrade_orchestrator.py: Call _validate_dependencies(), _validate_operational_readiness(), _validate_test_suite()
    - validate_deployment.py: Add check_environment_prerequisites()
    - Bootstrap verification: Enhanced with operational checks
    - Auto-rollback: If critical checks fail

  rationale: |
    OPERATIONAL_READINESS_ENFORCEMENT: User Trust & Time Savings

    **Problem Scenario (From upgrade-issue.md):**

    Timeline:
    - Minute 0-5: Backup & file copy (SUCCESS)
    - Minute 5-25: NumPy build failure (20 min wasted)
    - Minute 25-35: Test discovery failure (10 min wasted)
    - Minute 35-45: Manual verification (15 min wasted)
    - Total: 45+ minutes to operational state

    Root Cause:
    - Deployment validated SOURCE repository health
    - Did NOT validate TARGET environment readiness
    - Assumed "files copied = operational"
    - No environment prerequisites check
    - No dependency installation validation
    - No operational smoke test

    Impact:
    - Poor user experience ("Where are the tests?")
    - Wasted time on manual troubleshooting
    - Eroded trust in upgrade process
    - Risk of incomplete installation

    **Correct Approach:**

    1. **Pre-Flight Environment Check:**
       - Check Python version (3.8+)
       - Check pip availability
       - Check git availability
       - Check disk space (500+ MB)
       - Check write permissions
       - Check C compiler (warn if missing)
       - BLOCK if critical checks fail

    2. **Post-Copy Dependency Validation:**
       - Install core dependencies (pytest, PyYAML, etc.)
       - Verify all imports successful
       - Warn if optional deps fail (NumPy, scikit-learn)
       - ROLLBACK if core deps fail

    3. **Operational Readiness Validation:**
       - Test core imports (tier1, tier2, tier3)
       - Verify databases accessible
       - Validate config files (YAML syntax)
       - Run pytest --collect-only
       - ROLLBACK if operational checks fail

    4. **Success Declaration:**
       - Only after ALL gates pass
       - Show validation summary
       - Display time to operational
       - List any warnings (optional deps)

    **Benefits:**
    - Time to operational: 45 min → <5 min (90% reduction)
    - Manual intervention: Required → None (100% reduction)
    - User confidence: Low → High
    - Rollback safety: Automatic on failure

    **Metrics:**
    - Environment validation: <30 seconds
    - Dependency validation: <2 minutes
    - Operational validation: <1 minute
    - Total overhead: <5 minutes
    - User time saved: 40+ minutes

    **Edge Cases:**
    - Windows without C compiler: Warn, continue (NumPy skipped)
    - Tests not found: Warn, continue (non-critical)
    - Optional deps fail: Warn, continue (graceful degradation)
    - Core imports fail: ERROR, rollback (critical)

    This rule ensures CORTEX is ACTUALLY operational, not just "deployed".

- rule_id: "DEBUG_MARKER_REMOVAL_ENFORCEMENT"
  name: "Debug Marker Removal Enforcement"
  severity: "blocked"
  description: "Git commits containing debug markers (MARKER, DEBUG, FIXME, TODO, BREAKPOINT) MUST be blocked to prevent debugging artifacts from reaching production"

  detection:
    combined_keywords:
      commit_attempt:
        - "git commit"
        - "commit changes"
        - "stage files"
        - "ready to commit"
      marker_patterns:
        - "# MARKER:"
        - "# DEBUG:"
        - "# FIXME:"
        - "# TODO:"
        - "# BREAKPOINT:"
    scope: ["intent", "file_content"]
    logic: "AND"

  alternatives:
    - "STEP 1: Run debug marker scanner: python src/utils/debug_markers.py scan src/"
    - "STEP 2: Review found markers and determine if they should be removed"
    - "STEP 3: Remove markers: python src/utils/debug_markers.py remove <file>"
    - "STEP 4: Or manually remove marker comments from code"
    - "STEP 5: Verify markers removed: python src/utils/debug_markers.py scan src/"
    - "STEP 6: Stage cleaned files: git add <files>"
    - "STEP 7: Retry commit (pre-commit hook will validate)"

  evidence_template: |
    Debug markers detected in staged files!

    Operation: '{operation}'
    Markers found: {marker_count}

    ❌ BLOCKED: Cannot commit code with debug markers

    **Why Debug Markers Must Be Removed:**

    1. **Production Readiness**
       - Debug markers indicate incomplete/temporary code
       - MARKER: Used during development to track execution
       - DEBUG: Code meant for debugging only
       - FIXME: Temporary fixes needing proper implementation
       - TODO: Incomplete implementations
       - BREAKPOINT: Execution pause points

    2. **Code Quality**
       - Markers clutter codebase
       - Confuse future developers
       - Indicate lack of review
       - Suggest rushed implementation

    3. **Professional Standards**
       - Clean code ready for review
       - No debugging artifacts
       - Proper implementation complete
       - Ready for production

    **Marker Types Detected:**

    {marker_details}

    **Automated Removal Available:**

    ```bash
    # Scan for all markers
    python src/utils/debug_markers.py scan src/

    # Remove from specific file
    python src/utils/debug_markers.py remove src/orchestrators/example.py

    # Dry-run to see what would be removed
    python src/utils/debug_markers.py remove src/orchestrators/example.py --dry-run
    ```

    **Git Pre-Commit Hook Protection:**

    The git pre-commit hook automatically scans staged Python files for markers:
    - Located: `.git/hooks/pre-commit`
    - Auto-scans: All staged .py files
    - Blocks commit: If any markers found
    - Clear guidance: Shows exact locations

    **Manual Removal:**

    1. Open files listed above
    2. Find lines with markers (MARKER:, DEBUG:, etc.)
    3. Remove marker comments
    4. Ensure code still functions
    5. Stage cleaned files: git add <files>
    6. Retry commit

    **Exceptions:**

    - If marker is intentional (e.g., TODO in documentation): Convert to proper format
    - If marker is critical for tracking: Move to issue tracker or planning document
    - If fixing marker is complex: Create separate task and remove marker

    **Benefits of Clean Commits:**
    - Professional code quality
    - Clear git history
    - Production-ready code
    - Easy code review
    - No confusion for future developers

    **Pre-Commit Hook Installation:**

    Copy the hook to your .git/hooks directory:
    ```bash
    cp scripts/git-hooks/pre-commit .git/hooks/pre-commit
    chmod +x .git/hooks/pre-commit  # Unix/Mac only
    ```

    The hook will automatically validate all future commits.

- rule_id: "TOKEN_EFFICIENCY_ENFORCEMENT"
  name: "Token Efficiency Enforcement"
  severity: "blocked"
  description: "Governance files MUST stay within token budget to prevent GitHub Copilot premature summarization. Total budget: 17K tokens (CORTEX.prompt.md 5K + brain-protection-rules.yaml 8K + response-templates.yaml 3K + copilot-instructions.md 1K). Current baseline: 98K tokens causing summarization every 3rd statement."

  detection:
    combined_keywords:
      governance_file_changes:
        - ".github/prompts/CORTEX.prompt.md"
        - "cortex-brain/brain-protection-rules.yaml"
        - "cortex-brain/response-templates.yaml"
        - ".github/copilot-instructions.md"
      size_indicators:
        - "added lines"
        - "expanded section"
        - "new content"
        - "documentation update"
    scope: ["intent", "file_content", "commit_changes"]
    logic: "AND"

  validation_thresholds:
    cortex_prompt_md:
      file: ".github/prompts/CORTEX.prompt.md"
      max_tokens: 5000
      current_tokens: 23000  # Phase 0 baseline
      target_tokens: 5000    # Phase 4 goal
      char_to_token_ratio: 4  # ~4 chars per token
      max_chars: 20000

    brain_protection_rules_yaml:
      file: "cortex-brain/brain-protection-rules.yaml"
      max_tokens: 8000
      current_tokens: 60000  # Phase 0 baseline
      target_tokens: 8000    # Phase 4 goal
      char_to_token_ratio: 4
      max_chars: 32000

    response_templates_yaml:
      file: "cortex-brain/response-templates.yaml"
      max_tokens: 3000
      current_tokens: 10000  # Phase 0 baseline
      target_tokens: 3000    # Phase 4 goal
      char_to_token_ratio: 4
      max_chars: 12000

    copilot_instructions_md:
      file: ".github/copilot-instructions.md"
      max_tokens: 1000
      current_tokens: 5000   # Phase 0 baseline
      target_tokens: 1000    # Phase 4 goal
      char_to_token_ratio: 4
      max_chars: 4000

  optimization_strategy:
    phase_1_modularization:
      target: "88.8% reduction (98K → 11K)"
      duration: "Week 1"
      techniques:
        - "Extract detailed guides to separate .md files"
        - "Use #file: references in CORTEX.prompt.md"
        - "Module structure: modules/[feature]-guide.md"
        - "Keep only summaries in main files"

    phase_2_template_compression:
      target: "94.9% reduction (98K → 5K)"
      duration: "Week 2"
      techniques:
        - "YAML anchor inheritance for templates"
        - "Shared base components (header, footer)"
        - "Placeholder-based content injection"
        - "Remove duplicate formatting instructions"

    phase_3_lazy_loading:
      target: "96.9% reduction (98K → 3K)"
      duration: "Week 3"
      techniques:
        - "Load SKULL rules on-demand when triggered"
        - "Index-based rule lookup (rule_id → file location)"
        - "Cache loaded rules in session memory"
        - "Minimize base load to index + metadata"

    phase_4_reference_compression:
      target: "98.0% reduction (98K → 2K)"
      duration: "Week 4"
      techniques:
        - "Convert inline examples to reference pointers"
        - "Store code samples in separate files"
        - "Use symbolic references (REF-001 → example file)"
        - "Load examples only when user needs details"

  alternatives:
    - "STEP 1: Check token budget BEFORE adding content: align governance-tokens validate"
    - "STEP 2: If over budget, identify content for extraction: align governance-tokens analyze"
    - "STEP 3: Extract to separate module: Move content to .github/prompts/modules/[feature]-guide.md"
    - "STEP 4: Replace with reference: Use #file:modules/[feature]-guide.md in CORTEX.prompt.md"
    - "STEP 5: Validate reduction: align governance-tokens validate (must be green)"
    - "STEP 6: Commit optimized files (both main file and new module)"

  evidence_template: "#file:documents/evidence-templates/architecture/TOKEN_EFFICIENCY_ENFORCEMENT.md"

  rationale: |
    TOKEN_EFFICIENCY_ENFORCEMENT: Prevent GitHub Copilot Premature Summarization

    **Root Cause Analysis:**

    **Problem:** GitHub Copilot summarizes conversation every 3rd user statement
    - Symptom: "I'm summarizing our conversation to save space..."
    - Frequency: Every 3 statements instead of 20+
    - Impact: Interrupts workflow, loses context nuance
    - User frustration: "Why does it summarize so often?"

    **Measurement:**

    Baseline token consumption (Phase 0):
    1. CORTEX.prompt.md: 23,000 tokens (91,472 characters)
    2. brain-protection-rules.yaml: 60,000 tokens (238,909 characters)
    3. response-templates.yaml: 10,000 tokens (39,823 characters)
    4. copilot-instructions.md: 5,000 tokens (19,127 characters)

    Total: 98,000 tokens (389,331 characters)
    GitHub Copilot context window: 200,000 tokens
    CORTEX baseline consumption: 49% of available context

    **Why This Causes Premature Summarization:**

    1. Context window fills quickly:
       - 49% consumed by CORTEX before user interaction
       - Only 51% (102K tokens) available for conversation
       - Average user statement: 200-500 tokens
       - Average CORTEX response: 1,000-2,000 tokens
       - 3 exchanges = ~7,500 tokens
       - Total used: 98K + 7.5K = 105.5K (52.8% of 200K)
       - Trigger threshold: >50% usage → summarize

    2. Comparison with optimal state:
       - Optimal baseline: 17K tokens (8.5% of context)
       - Available for conversation: 183K tokens (91.5%)
       - 24+ exchanges before hitting 50% threshold
       - Result: Normal summarization frequency (20+ statements)

    **Token Budget Rationale:**

    **Total Budget: 17,000 tokens (8.5% of context window)**

    Allocation:
    1. CORTEX.prompt.md: 5,000 tokens
       - Entry point + high-level navigation
       - Summaries only, details in modules
       - 78.3% reduction from 23K

    2. brain-protection-rules.yaml: 8,000 tokens
       - Tier 0 instinct index + metadata
       - Full rules loaded on-demand
       - 86.7% reduction from 60K

    3. response-templates.yaml: 3,000 tokens
       - Base template structures only
       - Content via placeholder injection
       - 70.0% reduction from 10K

    4. copilot-instructions.md: 1,000 tokens
       - Minimal project overview
       - Reference to CORTEX.prompt.md
       - 80.0% reduction from 5K

    **Enforcement Mechanism:**

    1. Pre-Commit Validation:
       - Git hook checks token count on commit
       - Blocks commit if any file exceeds budget
       - Shows overage details + optimization tips

    2. CI/CD Deployment Gate (Gate 16):
       - Automated validation in deployment pipeline
       - Fails build if token budget exceeded
       - Reports overage to team
       - Prevents production deployment

    3. align CLI Tool:
       - Manual validation: align governance-tokens validate
       - Analysis: align governance-tokens analyze
       - Automated fixes: align governance-tokens optimize

    4. CORTEX Tests:
       - tests/tier0/test_token_efficiency_enforcement.py
       - 19 test cases covering all rules
       - Runs in CI/CD pipeline
       - Must pass for merge approval

    **Success Criteria:**

    Phase 0 (Current): 98K tokens, summarizes every 3 statements
    Phase 1 (Week 1): 11K tokens, summarizes every 9 statements
    Phase 2 (Week 2): 5K tokens, summarizes every 19 statements
    Phase 3 (Week 3): 3K tokens, summarizes every 32 statements
    Phase 4 (Week 4): 2K tokens, summarizes every 49 statements

    **Benefits:**

    1. User Experience:
       - No interruptions during workflow
       - Maintains context nuance longer
       - Natural conversation flow
       - Fewer "summarizing..." messages

    2. Development Efficiency:
       - More context available for CORTEX responses
       - Better code generation accuracy
       - Fewer context-loss errors
       - Reduced need for re-explanation

    3. System Performance:
       - Faster initial load (smaller base)
       - Reduced token processing cost
       - More efficient context utilization
       - Better cache hit rates

    **Historical Context:**

    This rule was created in response to user complaints about:
    - "CORTEX summarizes too often" (December 2025)
    - "Loses context mid-conversation" (December 2025)
    - "Can't maintain complex discussions" (December 2025)

    Investigation revealed 98K token baseline as root cause.
    Solution: 4-phase optimization strategy reducing to 2K tokens (98% reduction).
