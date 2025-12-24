        RED Phase Purpose:
        - Validates test actually tests something (not false positive)
        - Forces specification before implementation
        - Prevents over-engineering (only implement what's needed)

        Workflow:
        1. Write test for desired behavior
        2. Run test → MUST FAIL (no implementation yet)
        3. Confirm failure message is meaningful
        4. Only then proceed to GREEN phase

    - rule_id: "GREEN_PHASE_VALIDATION"
      name: "GREEN Phase Validation (Minimal Implementation)"
      severity: "blocked"
      description: "Implementation must pass previously failing tests with minimal code"

      detection:
        keywords:
          - "skip green phase"
          - "implement everything at once"
          - "over-engineer"
          - "add features not in test"
        scope: ["intent", "description"]

      alternatives:
        - "Implement ONLY what makes test pass"
        - "Resist adding extra features (YAGNI)"
        - "Save improvements for REFACTOR phase"

      evidence_template: "Intent: '{intent}'"

      rationale: |
        GREEN Phase Purpose:
        - Minimal implementation (simplest code to pass test)
        - Prevents over-engineering and scope creep
        - Forces incremental development

        Workflow:
        1. Test is RED (failing)
        2. Write simplest code to make test GREEN (passing)
        3. Run test → MUST PASS
        4. Do NOT add features beyond test requirements
        5. Proceed to REFACTOR phase for improvements

    - rule_id: "SOLID_SRP"
      name: "Single Responsibility Principle"
      severity: "blocked"
      description: "Class/function violates Single Responsibility Principle"

      detection:
        keywords:
          - "class does too much"
          - "multiple responsibilities"
          - "god class"
          - "long method"
        scope: ["analysis", "description"]

      alternatives:
        - "Extract separate classes for each responsibility"
        - "Split into smaller, focused functions"
        - "Use composition over inheritance"

      evidence_template: "Violation: '{description}'"

      rationale: |
        SRP Enforcement:
        - Each class should have ONE reason to change
        - Functions should do ONE thing well
        - Improves testability and maintainability

        Indicators of Violation:
        - Class > 250 lines
        - Function > 30 lines
        - Class name contains "And" or "Manager"
        - Multiple import groups (data, network, UI)

    - rule_id: "SOLID_DIP"
      name: "Dependency Inversion Principle"
      severity: "blocked"
      description: "Code depends on concrete implementations instead of abstractions"

      detection:
        keywords:
          - "concrete dependency"
          - "tight coupling"
          - "cannot mock"
          - "hard to test"
        scope: ["analysis", "description"]

      alternatives:
        - "Depend on interfaces/protocols, not classes"
        - "Inject dependencies via constructor"
        - "Use dependency injection framework"

      evidence_template: "Violation: '{description}'"

      rationale: |
        DIP Enforcement:
        - High-level modules shouldn't depend on low-level modules
        - Both should depend on abstractions (interfaces)
        - Enables testing with mocks

        Example:
        ❌ BAD:
        class UserService:
            def __init__(self):
                self.db = PostgresDatabase()  # Concrete dependency

        ✅ GOOD:
        class UserService:
            def __init__(self, db: IDatabase):  # Abstract dependency
                self.db = db

    - rule_id: "SECURITY_INJECTION"
      name: "Security - Injection Prevention"
      severity: "blocked"
      description: "Code vulnerable to SQL injection, XSS, or command injection"

      detection:
        keywords:
          - "string concatenation"
          - "execute raw sql"
          - "eval("
          - "exec("
          - "innerHTML"
        scope: ["code", "description"]

      alternatives:
        - "Use parameterized queries (SQL)"
        - "Use prepared statements"
        - "Sanitize user input"
        - "Use template engines with auto-escaping"

      evidence_template: "Security risk: '{description}'"

      rationale: |
        Injection Prevention:
        - NEVER concatenate user input into SQL/commands
        - ALWAYS use parameterized queries
        - ALWAYS validate and sanitize input

        Example:
        ❌ BAD:
        query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL injection

        ✅ GOOD:
        query = "SELECT * FROM users WHERE id = ?"
        cursor.execute(query, (user_id,))  # Parameterized

    - rule_id: "SECURITY_AUTHENTICATION"
      name: "Security - Authentication Best Practices"
      severity: "blocked"
      description: "Authentication/authorization implementation has security issues"

      detection:
        keywords:
          - "plaintext password"
          - "hardcoded secret"
          - "no authentication"
          - "skip authorization"
        scope: ["code", "description"]

      alternatives:
        - "Hash passwords with bcrypt/argon2"
        - "Use environment variables for secrets"
        - "Implement proper authentication middleware"
        - "Check authorization before resource access"

      evidence_template: "Security risk: '{description}'"

      rationale: |
        Authentication Security:
        - NEVER store plaintext passwords
        - NEVER hardcode secrets in code
        - ALWAYS verify authentication before protected operations
        - ALWAYS check authorization (user can access resource)

        Example:
        ❌ BAD:
        password = user_input  # Plaintext storage
        API_KEY = "sk-1234567890"  # Hardcoded secret

        ✅ GOOD:
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())
        API_KEY = os.getenv("API_KEY")  # Environment variable

    - rule_id: "THREAT_MODELING_ENFORCEMENT"
      name: "Security - Threat Modeling Required"
      severity: "blocked"
      description: "Planning workflow executed without STRIDE threat analysis"

      detection:
        keywords:
          - "skip threat"
          - "bypass threat"
          - "no threat analysis"
          - "threat analysis disabled"
        scope: ["intent", "flags", "workflow"]
        workflow_triggers:
          - operation: "planning"
            required_stages: ["threat_analysis"]
            stage_config:
              name: "threat_analysis"
              required: true
              timeout: 600
              on_failure: "block"  # Override YAML's "warn" with governance "block"

      alternatives:
        - "Execute STRIDE threat analysis (Stage 4 in planning_with_threats.yaml)"
        - "Use --allow-skip-threats flag for exceptional cases (triggers warning)"
        - "Review identified threats and mitigations before proceeding"

      evidence_template: "Threat modeling required: '{description}'"

      rationale: |
        Threat Modeling Enforcement:
        - ALL planning workflows MUST execute STRIDE threat analysis
        - Stage 4 (threat_analysis) in planning_with_threats.yaml MUST complete successfully
        - Threats must be identified, documented, and mitigations defined
        - Bypass only allowed with explicit --allow-skip-threats flag (triggers governance warning)

        STRIDE Framework:
        - Spoofing: Identity verification vulnerabilities
        - Tampering: Data integrity risks
        - Repudiation: Non-repudiation gaps
        - Information Disclosure: Confidentiality breaches
        - Denial of Service: Availability threats
        - Elevation of Privilege: Authorization bypass

        Example workflow enforcement:
        ❌ BLOCKED:
        User: "plan authentication feature"
        CORTEX: Executes planning WITHOUT threat analysis
        BrainProtector: BLOCKED - THREAT_MODELING_ENFORCEMENT violated

        ✅ ALLOWED:
        User: "plan authentication feature"
        CORTEX: Executes planning_with_threats.yaml (includes Stage 4: threat_analysis)
        ThreatModelerAgent: Identifies 8 threats (2 CRITICAL, 3 HIGH, 3 MEDIUM)
        BrainProtector: PASSED - Threat analysis completed

        ✅ ALLOWED (with warning):
        User: "plan authentication feature --allow-skip-threats"
        CORTEX: Skips threat analysis per user request
        BrainProtector: WARNING - Threat analysis bypassed (user accepted risk)

      exceptions:
        - flag: "--allow-skip-threats"
          action: "warn"
          message: "Threat analysis bypassed by user request (not recommended - security risks unassessed)"
        - condition: "workflow == 'planning_with_threats.yaml'"
          action: "enforce_stage_completion"
          stage: "threat_analysis"
          on_failure: "block"  # Override workflow's on_failure="warn"

    - rule_id: "BRAIN_ARCHITECTURE_INTEGRITY"
      name: "Brain Architecture Integrity"
      severity: "blocked"
      description: "Changes threaten 4-tier brain architecture integrity"

      detection:
        keywords:
          - "merge tiers"
          - "monolithic database"
          - "skip tier"
          - "bypass brain"
        scope: ["intent", "description"]

      alternatives:
        - "Preserve Tier 0-3 separation"
        - "Use distributed database architecture"
        - "Follow brain integration patterns"

      evidence_template: "Architecture risk: '{description}'"

      rationale: |
        Brain Architecture Protection:
        - Tier 0: Instincts (immutable, <10ms)
        - Tier 1: Working memory (conversation context, <100ms)
        - Tier 2: Knowledge graph (learned patterns, <150ms)
        - Tier 3: Development context (project-specific, <1ms cached)

        Threats:
        - Merging tiers into monolithic database
        - Bypassing tier hierarchy
        - Direct access to tier internals
        - Synchronous blocking on slow tiers

    - rule_id: "DEFINITION_OF_DONE"
      name: "Definition of Done"
      severity: "blocked"
      description: "Attempt to bypass Definition of Done (zero errors, zero warnings)"

      detection:
        keywords:
          - "skip validation"
          - "bypass done"
          - "disable error check"
          - "allow warnings"
        scope: ["intent", "description"]

      alternatives:
        - "Fix all warnings before proceeding"
        - "Add exception rule if truly needed"
        - "Update test to expect new behavior"

      evidence_template: "Description: '{description}'"

    - rule_id: "DEFINITION_OF_READY"
      name: "Definition of Ready"
      severity: "blocked"
      description: "Work item does not meet DoR criteria"

      detection:
        keywords:
          - "skip DoR"
          - "bypass ready"
          - "start without requirements"
        scope: ["intent", "description"]

      alternatives:
        - "Define acceptance criteria first"
        - "Get stakeholder clarification"
        - "Create refined user story"

      evidence_template: "Missing DoR criteria: '{description}'"

    - rule_id: "BRAIN_PROTECTION_TESTS_MANDATORY"
      name: "Brain Protection Tests - 100% Pass Rate Mandatory"
      severity: "blocked"
      description: "Brain protection tests MUST pass - no exceptions"

      detection:
        keywords:
          - "skip brain protection"
          - "ignore test failures"
          - "brain tests failing"
          - "disable brain tests"
          - "bypass protection tests"
          - "xfail brain"
          - "skip tier0 tests"
        scope: ["intent", "description"]

      alternatives:
        - "Fix the failing tests immediately"
        - "Revert changes that broke protection"
        - "Do not proceed until 100% pass rate achieved"

      evidence_template: "Brain protection tests are CRITICAL. Intent: '{intent}'"

      rationale: |
        Brain protection tests validate core CORTEX integrity:
        - Path handling (cross-platform compatibility)
        - Protection layer logic (architectural safeguards)
        - Conversation tracking (memory system)
        - YAML configuration loading (governance rules)

        If these fail, CORTEX has fundamental issues that MUST be resolved.
        100% pass rate is MANDATORY before any other work continues.

    - rule_id: "MACHINE_READABLE_FORMATS"
      name: "Use Machine-Readable Formats for Efficiency"
      severity: "warning"
      description: "Non-user files should use YAML/JSON, not Markdown"

      detection:
        combined_keywords:
          markdown_creation:
            - "create markdown"
            - "new .md"
            - "add .md"
          structured_data:
            - "structured data"
            - "configuration"
            - "capability matrix"
            - "status table"
            - "metrics"
            - "statistics"
            - "code example"
            - "implementation pattern"
        scope: ["intent", "description"]
        logic: "AND"  # Both conditions must be true

      alternatives:
        - "Use YAML for structured data (capabilities, rules, config)"
        - "Use JSON for metrics, statistics, logs"
        - "Reserve Markdown for user-facing narratives only"
        - "Use code files with docstrings for examples"

      evidence_template: "Description: '{description}'"

      rationale: |
        CORTEX 2.0 efficiency principles:

        USE MARKDOWN FOR:
        - User guides and tutorials
        - Narrative documentation (stories, history)
        - Architecture explanations
        - Design rationale

        USE YAML/JSON FOR:
        - Structured data (capabilities, status, priorities)
        - Configuration and rules
        - Metrics and statistics
        - Patterns and templates
        - API schemas

        USE CODE FILES FOR:
        - Implementation examples
        - Code snippets and patterns
        - Reusable templates

        Benefits:
        - 60% token reduction in context injection
        - Automated validation and schema checking
        - Better version control diffs
        - Direct machine consumption
        - No documentation drift

    - rule_id: "ACTIVE_NARRATOR_VOICE"
      name: "Active Narrator Voice (Not Passive Documentation)"
      severity: "warning"
      description: "Story uses passive/clinical narrator voice instead of active storytelling"

      detection:
        passive_verbs:
          - "Asif Codeinstein designed"
          - "Asif Codeinstein created"
          - "Asif Codeinstein wrote"
          - "Asif Codeinstein implemented"
          - "Asif Codeinstein developed"
          - "He wrote routines"
          - "He created routines"
          - "He implemented"
          - "He developed"

        documentary_markers:
          - "One evening, while"
          - "One morning, while"
          - "One day, while"
          - "One night, while"
          - "After completing"
          - "After finishing"
          - ", while reviewing"
          - "During the"

        scope: ["file_content"]
        file_patterns:
          - "docs/story/**/*.md"
          - "prompts/shared/story.md"

      alternatives:
        - "Use active storytelling: 'So Asif built' (adds momentum)"
        - "Show immediate action: 'grabbed keyboard and coded' (not 'wrote routines')"
        - "Vivid scene-setting: 'That evening, knee-deep in' (not 'One evening, while')"
        - "Present-tense urgency: 'The refactor complete, Asif leaned back' (not 'After completing')"
        - "Energy verbs: 'dove into', 'attacked', 'grabbed', 'swept' (not 'designed', 'created')"

      evidence_template: |
        Passive narrator detected: '{match}'

        Story should be ACTIVE third-person narrative, not clinical documentation.

        Examples:
        ❌ "Asif Codeinstein designed..." ← documentation
        ✅ "So Asif built..." ← storytelling

        ❌ "He wrote routines for..." ← neutral observer  
        ✅ "He grabbed his keyboard and..." ← immediate action

        ❌ "One evening, while reviewing..." ← documentary
        ✅ "That evening, knee-deep in..." ← vivid scene

      rationale: |
        CORTEX story is a COMEDY told by an energetic narrator, not a memoir or
        technical documentation. Third-person is CORRECT, but it must be ACTIVE
        storytelling with personality, immediacy, and energy.

        The narrator is a CHARACTER in the story—witty, observant, timing jokes.
        Not a clinical observer reporting facts.

        TRANSFORMATION PATTERNS:

        Passive → Active:
        - "designed a system" → "So Asif built a system"
        - "wrote routines for" → "grabbed his keyboard and coded"
        - "One evening, while reviewing" → "That evening, knee-deep in"
        - "made a decision" → "stared at the screen and decided"
        - "implemented the feature" → "dove into implementing"
        - "After completing X, he" → "X complete, Asif leaned back and"

        PRESERVE:
        - Third-person perspective (it's a STORY about Asif, not BY Asif)
        - Narrator personality and comedy
        - Technical content and accuracy
        - Character name "Asif Codeinstein"

        AVOID:
        - First-person memoir style ("I designed...")
        - Clinical/academic tone ("The system was designed to...")
        - Passive voice constructions
        - Documentary-style time markers

    - rule_id: "CORTEX_PROMPT_FILE_PROTECTION"
      name: "CORTEX.prompt.md Protection (Never Rename, Safe Update)"
      severity: "blocked"
      description: "Prevent renaming CORTEX.prompt.md and enforce safe update procedure"

      detection:
        combined_keywords:
          rename_attempt:
            - "rename CORTEX.prompt.md"
            - "CORTEX.prompt.md to"
            - "move CORTEX.prompt.md"
            - "cortex-lite"
            - "cortex-backup"
            - "cortex-fixed"
            - "CORTEX-"
          or_unsafe_edit:
            - "edit CORTEX.prompt.md directly"
            - "modify in place"
        scope: ["intent", "description", "file_operation"]
        logic: "OR"

      alternatives:
        - "Use safe update: temp file → optimize → DELETE original → copy → delete temp"
        - "Create .github/prompts/temp-cortex-update.md with optimized content"
        - "DELETE ALL content of CORTEX.prompt.md (clear file completely)"
        - "Copy complete instructions from temp to CORTEX.prompt.md"
        - "Delete temporary file after successful copy"

      evidence_template: |
        🚨 CORTEX.prompt.md PROTECTION VIOLATION

        Attempted: '{operation}'

        CRITICAL: CORTEX.prompt.md is the GitHub Copilot integration entry point!

        ❌ NEVER:
        - Rename to cortex-lite.prompt.md
        - Rename to cortex-backup.prompt.md  
        - Rename to cortex-fixed.prompt.md
        - Add ANY prefix or suffix
        - Edit directly (risky, no rollback)

        ✅ SAFE UPDATE PROCEDURE:
        1. Create: .github/prompts/temp-cortex-update.md
        2. Generate optimized content in temp file
        3. DELETE ALL content of CORTEX.prompt.md
        4. Copy complete instructions from temp
        5. Delete temp-cortex-update.md

        Why? Filename stability + Atomic updates + Rollback capability

      rationale: |
        CORTEX_PROMPT_FILE_PROTECTION: Entry Point Stability

        CORTEX.prompt.md is the SINGLE entry point for GitHub Copilot Chat.
        Its exact filename (.github/prompts/CORTEX.prompt.md) is:
        - Hardcoded in GitHub Copilot discovery
        - Referenced throughout all documentation
        - Critical for `/CORTEX` command to work

        Why This Protection Matters:

        1. GitHub Copilot Discovery:
           Copilot looks for .github/prompts/CORTEX.prompt.md
           ANY rename → integration breaks completely
           No fallback mechanism exists

        2. Documentation References:
           - README.md references CORTEX.prompt.md
           - Setup guides reference CORTEX.prompt.md
           - Quick start tutorials reference CORTEX.prompt.md
           All references break if renamed

        3. User Confusion:
           Multiple prompt files create:
           - "Which one do I use?"
           - "Is cortex-lite the new version?"
           - Cognitive overhead increases

        4. Git History Fragmentation:
           Rename creates new file in git
           Old file shows as deleted
           History split across filenames

        Safe Update Procedure:

        Step 1: Create Temporary File
        ```
        .github/prompts/temp-cortex-update.md
        ```
        - Contains new optimized content
        - Reviewable before applying
        - Acts as backup if issues occur

        Step 2: Generate Optimized Content
        - Apply token optimizations
        - Restructure sections
        - Update documentation references
        - Add new features

        Step 3: Clear Original (Atomic Update)
        ```python
        # DELETE ALL content
        Path('.github/prompts/CORTEX.prompt.md').write_text('')
        ```
        - Prevents partial updates
        - Ensures clean slate
        - No merge conflicts

        Step 4: Copy Complete Instructions
        ```python
        content = Path('temp-cortex-update.md').read_text()
        Path('CORTEX.prompt.md').write_text(content)
        ```
        - Atomic replacement
        - No partial content risk

        Step 5: Delete Temporary File
        ```python
        Path('temp-cortex-update.md').unlink()
        ```
        - Clean up
        - Single source of truth

        Benefits:
        - Filename NEVER changes (stability)
        - Atomic updates (no half-updated states)
        - Review capability (temp file inspection)
        - Rollback support (restore from temp)
        - Clean git history (single file evolution)

        Real Incident Pattern Prevented:
        Developer: "I'll create CORTEX-lite.prompt.md"
        Result: Two prompt files coexist
        User confusion: "Which is current?"
        Maintenance nightmare: Multiple files diverge

        This rule BLOCKS any rename attempt.
        Exception: Temporary files for update workflow ARE encouraged.

    - rule_id: "GIT_CHECKPOINT_ENFORCEMENT"
      name: "Git Checkpoint Before Development Work"
      severity: "blocked"
      description: "Require git checkpoint (commit/tag) before starting any development work"

      detection:
        combined_keywords:
          development_start:
            - "implement feature"
            - "start development"
            - "begin implementation"
            - "fix bug"
            - "refactor code"
            - "add functionality"
            - "create new"
            - "modify existing"
          and_no_checkpoint:
            - "no checkpoint"
            - "skip checkpoint"
            - "without commit"
            - "uncommitted changes"
        scope: ["intent", "description", "git_status"]
        logic: "AND"

      alternatives:
        - "Create git checkpoint: git commit -m 'checkpoint: before [feature] development'"
        - "Create git tag: git tag -a checkpoint-YYYY-MM-DD-HH-MM -m 'Checkpoint before [feature]'"
        - "Stash changes if needed: git stash save 'WIP: checkpoint before [feature]'"
        - "Use git_checkpoint_module for automated checkpoint creation"

      evidence_template: "#file:documents/evidence-templates/git/GIT_CHECKPOINT_ENFORCEMENT.md"

      rationale: "#file:documents/rationales/GIT_CHECKPOINT_ENFORCEMENT.md"
        ```
        - Saves uncommitted changes
        - Useful for quick experiments
        - Recoverable: git stash pop
        - Local only (not pushed)

        Automated Checkpoint Module:

        ```python
        from src.operations.modules.git_checkpoint_module import GitCheckpointModule

        checkpoint = GitCheckpointModule()
        result = checkpoint.execute({
            'message': 'before authentication implementation',
            'checkpoint_type': 'commit'  # or 'tag'
        })
        ```

        When Checkpoints Are Required:
        - ✅ Before implementing new features
        - ✅ Before refactoring existing code
        - ✅ Before fixing bugs (capture broken state)
        - ✅ Before exploratory changes
        - ✅ Before risky architectural changes
        - ❌ NOT for trivial changes (typo fixes, comments)
        - ❌ NOT for documentation-only updates

        Verification Process:

        1. Pre-Development Check:
           ```python
           git_status = subprocess.run(['git', 'status', '--porcelain'], 
                                      capture_output=True, text=True)
           if git_status.stdout.strip():
               raise CheckpointViolation("Uncommitted changes detected")
           ```

        2. Checkpoint Creation:
           ```python
           subprocess.run(['git', 'commit', '-m', 'checkpoint: before feature'])
           # OR
           subprocess.run(['git', 'tag', '-a', 'checkpoint-[timestamp]'])
           ```

        3. Checkpoint Verification:
           ```python
           verify = subprocess.run(['git', 'log', '-1', '--oneline'], 
                                  capture_output=True, text=True)
           assert 'checkpoint:' in verify.stdout.lower()
           ```

        Integration Points:
        - BrainProtector: Validates checkpoint before development
        - HealthValidator: Checks for uncommitted changes
        - OptimizeOperation: Enforces checkpoint before changes
        - CommitHandler: Can create checkpoints automatically

        Real Incident Patterns Prevented:

        Scenario 1: Lost Refactoring Work
        Developer: Starts major refactor without checkpoint
        Result: Code breaks, no way to recover working state
        Prevention: Checkpoint required → rollback available

        Scenario 2: Exploratory Regression
        Developer: Tries experimental approach, causes regression
        Result: Can't identify what changed, debugging nightmare
        Prevention: Checkpoint shows exact diff of changes

        Scenario 3: Merge Conflict Chaos
        Developer: Multiple changes without checkpoints
        Result: Massive merge conflicts, unclear resolution
        Prevention: Checkpoints provide integration points

        This rule BLOCKS development work without checkpoint.
        Exception: Documentation-only changes don't require checkpoints.

    - rule_id: "PREVENT_DIRTY_STATE_WORK"
      name: "Prevent Development on Dirty Branches"
      severity: "warning"
      description: "Never work on branches with uncommitted changes without explicit user consent"

      detection:
        combined_keywords:
          development_work:
            - "implement"
            - "refactor"
            - "fix"
            - "modify"
            - "create"
            - "update"
          and_dirty_state:
            - "uncommitted changes"
            - "modified files"
            - "untracked files"
            - "staged changes"
        scope: ["intent", "description", "git_status"]
        logic: "AND"

      alternatives:
        - "Commit your changes first (recommended): git add . && git commit -m 'description'"
        - "Stash changes and continue: git stash save 'WIP: description'"
        - "Proceed anyway with explicit consent: CORTEX will checkpoint current state"
        - "Review changes first: git status && git diff"

      evidence_template: "#file:documents/evidence-templates/git/PREVENT_DIRTY_STATE_WORK.md"

      rationale: "#file:documents/rationales/PREVENT_DIRTY_STATE_WORK.md"

# Layer 2: Tier Boundary Protection
- layer_id: "tier_boundary"
  name: "Tier Boundary Protection"
  description: "Data stored in correct tier"
  priority: 2

  rules:
    - rule_id: "TIER0_APPLICATION_DATA"
      name: "No Application Data in Tier 0"
      severity: "blocked"
      description: "Application-specific path in Tier 0 (immutable governance)"

      detection:
        path_patterns:
          - "tier0/**"
          - "governance/**"
        contains_any: "{{application_paths}}"

      alternatives:
        - "Store in Tier 2 with scope='application'"
        - "Keep generic principles in Tier 0"
        - "Create application-specific tier"

      evidence: "Tier 0 is for generic CORTEX principles only"

    - rule_id: "TIER2_CONVERSATION_DATA"
      name: "No Conversation Data in Tier 2"
      severity: "warning"
      description: "Conversation data should be in Tier 1, not Tier 2"

      detection:
        path_patterns:
          - "tier2/**"
        contains: "conversation"

      alternatives:
        - "Move to Tier 1 (conversation-history.jsonl)"
        - "Store aggregated patterns in Tier 2"
        - "Keep raw data in Tier 1, patterns in Tier 2"

      evidence: "Tier 2 is for aggregated patterns, not raw conversations"

# Layer 3: SOLID Compliance
- layer_id: "solid_compliance"
  name: "SOLID Compliance"
  description: "No God Objects, proper separation"
  priority: 3

  rules:
    - rule_id: "SINGLE_RESPONSIBILITY"
      name: "Single Responsibility Principle"
      severity: "warning"
      description: "Potential God Object pattern detected (adding multiple responsibilities)"

      detection:
        keywords:
          - "add mode"
          - "add switch"
          - "handle all"
          - "do everything"
        scope: ["intent"]

      alternatives:
        - "Create dedicated agent for new responsibility"
        - "Use composition instead of adding modes"
        - "Extract to separate module"

      evidence_template: "Intent: '{intent}'"

    - rule_id: "DEPENDENCY_INVERSION"
      name: "Dependency Inversion Principle"
      severity: "warning"
      description: "Hardcoded dependency detected (violates DIP)"

      detection:
        keywords:
          - "hardcode path"
          - "fixed path"
          - "absolute path"
          - "inline config"
        scope: ["description"]

      alternatives:
        - "Use dependency injection"
        - "Load from configuration file"
        - "Pass as parameter"

      evidence_template: "Description: '{description}'"

    - rule_id: "OPEN_CLOSED"
      name: "Open/Closed Principle"
      severity: "warning"
      description: "Modifying existing behavior instead of extending"

      detection:
        keywords:
          - "change behavior"
          - "modify existing"
          - "alter functionality"
        scope: ["intent", "description"]

      alternatives:
        - "Create new implementation via extension"
        - "Use strategy pattern"
        - "Add decorator or wrapper"

      evidence_template: "Consider extension over modification"

    - rule_id: "CORTEX_WORKSPACE_ISOLATION"
      name: "CORTEX Workspace Isolation"
      severity: "blocked"
      description: "All CORTEX-generated documentation for application repos MUST be within CORTEX/Workspaces/ folder"

      detection:
        combined_keywords:
          cortex_generation:
            - "onboard application"
            - "generate documentation"
            - "create docs"
            - "application onboarding"
          root_output:
            - "/docs/"
            - "\\docs\\"
            - "root_path / 'docs'"
            - "project_root / 'docs'"
        scope: ["code", "file_path", "intent"]
        logic: "AND"

      verification_required:
        - type: "output_path_validation"
          description: "Verify all generated files within CORTEX/Workspaces/"
          requirement: "Output paths MUST contain 'CORTEX/Workspaces/[app-name]/'"

        - type: "no_root_pollution"
          description: "Verify no files created in application repository root or docs/"
          requirement: "git status MUST show zero new files outside CORTEX/"

        - type: "workspace_structure"
          description: "Verify proper workspace folder structure created"
          requirement: "CORTEX/Workspaces/[app-name]/{docs,diagrams,references}/"

      alternatives:
        - "Use CORTEX/Workspaces/[app-name]/docs/ for all generated documentation"
        - "Use CORTEX/Workspaces/[app-name]/diagrams/ for architecture diagrams"
        - "Use CORTEX/Workspaces/[app-name]/references/ for quick references"
        - "Add .gitignore: CORTEX/ (exclude entire CORTEX folder from user repo)"

      evidence_template: |
        CORTEX documentation generated outside workspace isolation!

        File: '{file_path}'
        Expected: CORTEX/Workspaces/[app-name]/...
        Actual: {actual_location}

        CRITICAL: NO cortex documentation should exist outside CORTEX folder

        Proper Structure:
        user-repo/
        ├── CORTEX/                          ← CORTEX folder (git-ignored)
        │   └── Workspaces/                  ← All app documentation here
        │       └── MyApp/                   ← App-specific workspace
        │           ├── docs/                ← Generated docs
        │           ├── diagrams/            ← Architecture diagrams
        │           └── references/          ← Quick references
        ├── src/                             ← User application code
        └── .gitignore                       ← Must include "CORTEX/"

        Why This Matters:
        - Clean separation (CORTEX artifacts ≠ application code)
        - Easy cleanup (delete CORTEX/ removes all CORTEX files)
        - No git pollution (CORTEX/ excluded via .gitignore)
        - Portability (CORTEX workspace self-contained)

      rationale: |
        CORTEX_WORKSPACE_ISOLATION: Repository Organization Standard

        Real incident (2025-11-17):
        - User: "onboarding app creates docs in repo root, not CORTEX folder"
        - Published onboarding generates: user-repo/docs/onboarding.md
        - CORTEX artifacts polluting user's application repository
        - Cleanup difficult (which docs are CORTEX vs application?)
        - .gitignore cannot exclude selectively

        Why Workspace Isolation Critical:

        1. Repository Cleanliness:
           - User repo = user's application code only
           - CORTEX artifacts = temporary scaffolding
           - Clear boundary prevents confusion
           Example: docs/ could be user's actual docs or CORTEX-generated

        2. Easy Cleanup:
           - Delete CORTEX/ → all CORTEX artifacts gone
           - No hunting for scattered CORTEX files
           - Uninstall = single folder removal
           Example: rm -rf CORTEX/ vs finding 47 scattered files

        3. Git Isolation:
           - Add "CORTEX/" to .gitignore once
           - No CORTEX artifacts ever committed to user repo
           - No accidental commits of temporary scaffolding
           Example: CORTEX workspace excluded, user code included

        4. Portability:
           - CORTEX workspace self-contained
           - Can backup/restore entire CORTEX state
           - Can sync across machines if desired
           Example: Copy CORTEX/ to new machine = full context restored

        5. Multi-Application Support:
           - CORTEX can work with multiple applications
           - Each app gets isolated workspace
           - No cross-contamination of artifacts
           Example: CORTEX/Workspaces/AppA/, CORTEX/Workspaces/AppB/

        Proper Workspace Structure:

        ```
        user-application-repo/
        ├── CORTEX/                          ← Git-ignored CORTEX folder
        │   ├── .cortex-metadata.json        ← Workspace metadata
        │   └── Workspaces/                  ← All application workspaces
        │       ├── MyApp/                   ← Application-specific workspace
        │       │   ├── docs/                ← Generated documentation
        │       │   │   ├── onboarding.md
        │       │   │   ├── architecture-overview.md
        │       │   │   └── quick-reference.md
        │       │   ├── diagrams/            ← Architecture diagrams
        │       │   │   ├── component-diagram.mmd
        │       │   │   ├── data-flow.mmd
        │       │   │   └── images/          ← Rendered images
        │       │   ├── references/          ← Quick references
        │       │   │   └── api-quick-ref.md
        │       │   └── analysis/            ← Code analysis reports
        │       │       └── complexity-report.json
        │       └── AnotherApp/              ← Another application
        │           └── docs/
        │               └── onboarding.md
        ├── src/                             ← User's actual application code
        │   └── MyApp/
        ├── tests/                           ← User's tests
        ├── README.md                        ← User's README
        └── .gitignore                       ← Must include "CORTEX/"
        ```

        Implementation Changes Required:

        1. PageGenerator (src/epm/modules/page_generator.py):
           Before:
           ```python
           self.output_path = root_path / "docs"
           ```

           After:
           ```python
           app_name = context.get('app_name', 'UnknownApp')
           self.output_path = root_path / "CORTEX" / "Workspaces" / app_name / "docs"
           ```

        2. DiagramGenerator (src/epm/modules/diagram_generator.py):
           Before:
           ```python
           self.output_path = root_path / "docs"
           ```

           After:
           ```python
           app_name = context.get('app_name', 'UnknownApp')
           self.output_path = root_path / "CORTEX" / "Workspaces" / app_name / "diagrams"
           ```

        3. ImagePromptGenerator (src/epm/modules/image_prompt_generator.py):
           Before:
           ```python
           self.output_dir = Path(output_dir)  # Typically docs/diagrams
           ```

           After:
           ```python
           app_name = context.get('app_name', 'UnknownApp')
           self.output_dir = root_path / "CORTEX" / "Workspaces" / app_name / "diagrams"
           ```

        4. Onboarding Orchestrator Context:
           Add app_name to session context:
           ```python
           session_context = {
               "app_name": self._detect_app_name(root_path),  # From solution file, csproj, package.json
               "profile": profile.value,
               "project_root": self.project_root,
               ...
           }
           ```

        5. .gitignore Creation:
           Onboarding MUST create/update user repo's .gitignore:
           ```gitignore
           # CORTEX AI Assistant (local workspace, not committed)
           CORTEX/
           ```

        Benefits:
        - Clean separation: CORTEX ≠ Application
        - Easy uninstall: Delete CORTEX/ folder
        - No git pollution: Single .gitignore entry
        - Multi-app support: Isolated workspaces
        - Portable: Self-contained CORTEX state

        Enforcement:
        - Brain Protector blocks operations writing outside CORTEX/
        - Integration tests verify output paths
        - Onboarding validates workspace structure
        - Design sync validates isolation maintained

        Exception: Shared CORTEX Installation
        If user wants to share CORTEX across projects (not per-repo):
        - Install CORTEX once (e.g., ~/CORTEX/)
        - Each repo references shared CORTEX
        - Workspaces still isolated: ~/CORTEX/Workspaces/[app-name]/
        - This is advanced configuration (document separately)

    - rule_id: "CODE_STYLE_CONSISTENCY"
      name: "Adopt User's Code Style"
      severity: "warning"
      description: "Generated code should match existing codebase style conventions"

      detection:
        combined_keywords:
          code_generation:
            - "generate code"
            - "create file"
            - "implement"
            - "write function"
            - "add class"
          style_mismatch:
            - "different style"
            - "inconsistent formatting"
            - "foreign conventions"
        scope: ["code", "file_content"]
        logic: "AND"

      alternatives:
        - "Analyze existing codebase style before generating"
        - "Match indentation (tabs vs spaces, 2 vs 4 spaces)"
        - "Match naming conventions (camelCase, snake_case, PascalCase)"
        - "Match bracket style (K&R, Allman, etc.)"
        - "Match quote style (single vs double quotes)"
        - "Match comment style and documentation format"
        - "Use linter configs (.editorconfig, .pylintrc, etc.) if available"

      evidence_template: |
        Code style inconsistency detected: '{mismatch}'

        User's codebase style:
        - Indentation: {user_indent}
        - Naming: {user_naming}
        - Quotes: {user_quotes}
        - Brackets: {user_brackets}

        Generated code should blend seamlessly with existing style.

      rationale: |
        CODE_STYLE_CONSISTENCY: Developer Experience Principle

        **CRITICAL HIERARCHY: Best Practices > Style Preferences**

        When generating code, CORTEX MUST:
        1. ✅ ALWAYS follow SOLID principles (non-negotiable)
        2. ✅ ALWAYS follow proper OOP design (non-negotiable)
        3. ✅ ALWAYS follow security best practices (non-negotiable)
        4. ✅ ALWAYS follow DRY, KISS, YAGNI principles (non-negotiable)
        5. ✅ THEN adapt to user's style preferences (adaptive layer)

        This means: If user's style conflicts with best practices, 
        CORTEX follows best practices and explains why.

        Example Scenarios:

        ✅ ADAPT TO USER STYLE (No conflict with best practices):
        User's code:
        ```python
        def calculate_total(items):  # No type hints
            total = 0
            for item in items:
                total += item['price']
            return total
        ```

        CORTEX generates (matching style):
        ```python
        def calculate_tax(total, rate):  # Match: No type hints
            return total * rate          # Match: Simple style
        ```

        ⚡ OVERRIDE USER STYLE (Conflicts with best practices):
        User's code:
        ```python
        def do_everything(data):  # God method violating SRP
            process(data)
            validate(data)
            save(data)
            email(data)
            log(data)
        ```

        CORTEX generates (SOLID over style):
        ```python
        # CORTEX: I noticed your code has a God method pattern.
        # I'll demonstrate Single Responsibility Principle instead:

        def process_data(data):
            return processor.process(data)

        def save_processed_data(processed_data):
            return repository.save(processed_data)

        # Explanation: Each function has one clear responsibility.
        # This makes testing easier and code more maintainable.
        ```

        When CORTEX generates code, it should feel like the user wrote it,
        not like a foreign AI dropped it in. Consistency builds trust and
        reduces cognitive friction.

        What to Match (When No Conflict with Best Practices):

        1. Indentation:
           - Tabs vs spaces
           - 2 spaces vs 4 spaces
           - Consistent nesting

        2. Naming Conventions:
           - Python: snake_case for functions/variables
           - JavaScript: camelCase for functions, PascalCase for classes
           - C#: PascalCase for public, camelCase for private
           - Project-specific prefixes (e.g., 'cortex_', 'internal_')

        3. Quote Style:
           - Python: Single vs double (PEP 8 prefers single for strings)
           - JavaScript: Consistency with existing files
           - Template literals vs concatenation

        4. Bracket/Brace Style:
           - K&R: Opening brace same line `function() {`
           - Allman: Opening brace new line
           ```
           function()
           {
           ```
           - Consistent in Python (implicit via PEP 8)

        5. Documentation:
           - Docstring style (Google, NumPy, reStructuredText)
           - Comment density and placement
           - Type hints (Python 3.5+)
           - JSDoc vs inline comments

        6. Import Organization:
           - Standard library, third-party, local (PEP 8)
           - Alphabetical vs functional grouping
           - Relative vs absolute imports

        7. Line Length:
           - 80 chars (classic PEP 8)
           - 100 chars (modern)
           - 120 chars (widescreen)

        8. Trailing Commas:
           - Multi-line lists/dicts
           - Function parameters

        Detection Strategy:

        1. Sample Existing Files:
           ```python
           def detect_code_style(project_path):
               samples = glob(f"{project_path}/**/*.py", recursive=True)[:10]

               styles = {
                   'indent': detect_indent(samples),
                   'naming': detect_naming(samples),
                   'quotes': detect_quotes(samples),
                   'line_length': detect_line_length(samples)
               }

               return styles
           ```

        2. Read Config Files:
           - .editorconfig (universal)
           - pyproject.toml (Python)
           - .eslintrc (JavaScript)
           - .prettierrc (JavaScript/TypeScript)
           - .pylintrc (Python)
           - tslint.json (TypeScript)

        3. Use Existing Formatters:
           - Black (Python - opinionated)
           - Prettier (JavaScript - opinionated)
           - autopep8 (Python - PEP 8)
           - Ruff (Python - fast linter)

        Example Detection:

        ```python
        # User's existing code
        def calculate_total(items: list[dict]) -> float:
            '''Calculate total price from items.'''
            total = 0.0
            for item in items:
                total += item['price']
            return total

        # CORTEX should generate:
        def calculate_tax(total: float, rate: float) -> float:
            '''Calculate tax amount.'''  # Match docstring style
            tax = total * rate            # Match naming (snake_case)
            return tax                    # Match simplicity

        # ❌ NOT this (different style):
        def CalculateTax(Total: float, Rate: float) -> float:
            """Calculate tax amount."""  # Different docstring quotes
            Tax = Total * Rate            # Different naming (PascalCase)
            return Tax
        ```

        Integration with CORTEX:

        1. Style Analyzer Module:
           - Runs on project first scan
           - Stores detected style in Tier 2 knowledge graph
           - Updated when major style changes detected

        2. Code Generator Hook:
           - Before generating, load project style profile
           - Apply style template to generated code
           - Run formatter if available (black, prettier)

        3. Validation:
           - Compare generated code against style profile
           - Flag deviations before presenting to user
           - Suggest corrections

        Override Scenarios:

        When to IGNORE user's style:
        - User explicitly requests specific style
        - Generating config/scaffold with tool's conventions
        - Creating new project (use CORTEX defaults)
        - Fixing style issues (user asked for cleanup)

        User Experience:

        ✅ GOOD:
        User: "Add a function to calculate tax"
        CORTEX: [Analyzes existing code]
        CORTEX: [Generates function matching user's style]
        User: "Perfect, looks like I wrote it!"

        ❌ BAD:
        User: "Add a function to calculate tax"
        CORTEX: [Generates code in default style]
        User: "This doesn't match my codebase style at all"
        User: [Has to reformat manually]

        Metrics:
        - Style consistency score (0-100%)
        - User acceptance rate (accepting vs modifying)
        - Manual reformatting frequency

        This rule ensures CORTEX acts as a seamless extension of the
        developer, not a foreign entity imposing its own conventions.

    - rule_id: "NO_EMOJIS_IN_SCRIPTS"
      name: "No Emojis in Generated Scripts"
      severity: "warning"
      description: "Scripts (Python, PowerShell, Bash, etc.) should not contain emojis"

      detection:
        combined_keywords:
          script_generation:
            - "generate script"
            - "create .py"
            - "create .ps1"
            - "create .sh"
            - "write script"
          emoji_usage:
            - "✅"
            - "❌"
            - "⚠️"
            - "🔍"
            - "📊"
            - "🧠"
            - "emoji"
        scope: ["code", "file_content"]
        logic: "AND"

      alternatives:
        - "Use plain text markers: [OK], [FAIL], [WARN]"
        - "Use ASCII art or text symbols: +, -, *, !"
        - "Reserve emojis for documentation and user-facing text only"
        - "Use logging levels: INFO, ERROR, WARNING instead of emojis"

      evidence_template: |
        Emoji detected in script: '{file_path}'

        Emojis found: {emoji_list}

        Scripts should use plain text for maximum compatibility:
        - Encoding issues across platforms
        - Terminal rendering problems
        - Copy/paste issues in some editors
        - Professional appearance

      rationale: |
        NO_EMOJIS_IN_SCRIPTS: Code Quality Standard

        Why Emojis Don't Belong in Scripts:

        1. Encoding Issues:
           - UTF-8 encoding not universal in all environments
           - PowerShell ISE may not render correctly
           - Windows cmd.exe has encoding problems
           - Remote SSH sessions may lose emojis

        2. Terminal Compatibility:
           - Some terminals don't support Unicode emojis
           - CI/CD logs may show broken characters
           - Legacy systems show question marks
           - Screen readers struggle with emojis

        3. Professional Standards:
           - Scripts are code, not social media
           - Emojis reduce professional appearance
           - Industry standard: plain text markers
           - Easier to grep/search logs

        4. Copy/Paste Problems:
           - Email clients may corrupt emojis
           - Documentation tools may strip emojis
           - Version control diffs show weird bytes
           - Stack Overflow code samples break

        What to Use Instead:

        ❌ Emoji-Based:
        ```python
        print("✅ Test passed")
        print("❌ Test failed")
        print("⚠️ Warning detected")
        ```

        ✅ Plain Text:
        ```python
        print("[OK] Test passed")
        print("[FAIL] Test failed")
        print("[WARN] Warning detected")
        ```

        ✅ Logging Levels:
        ```python
        logger.info("Test passed")
        logger.error("Test failed")
        logger.warning("Warning detected")
        ```

        ✅ ASCII Symbols:
        ```python
        print("+ Test passed")
        print("- Test failed")
        print("! Warning detected")
        ```

        Allowed Emoji Usage:
        - Documentation (README.md, guides)
        - User-facing messages (GitHub Copilot Chat responses)
        - Markdown files (story.md, setup-guide.md)
        - Comments in code (sparingly, for clarity)

        Not Allowed:
        - Python scripts (.py)
        - PowerShell scripts (.ps1)
        - Bash scripts (.sh)
        - Batch files (.bat, .cmd)
        - Any executable script files

        Example Violation:
        ```python
        # ❌ BAD
        def run_tests():
            print("🧪 Running tests...")
            if all_pass:
                print("✅ All tests passed!")
            else:
                print("❌ Some tests failed!")

        # ✅ GOOD
        def run_tests():
            print("[TEST] Running tests...")
            if all_pass:
                print("[OK] All tests passed!")
            else:
                print("[FAIL] Some tests failed!")
        ```

        This maintains code professionalism and ensures scripts work
        universally across all platforms and environments.

    - rule_id: "NO_ROOT_SUMMARY_DOCUMENTS"
      name: "No Documents in Repository Root - STRICT ENFORCEMENT"
      severity: "blocked"
      description: "ALL documentation MUST be in cortex-brain/documents/, NEVER repository root - applies to both standalone and embedded CORTEX installations"

      detection:
        combined_keywords:
          root_level_creation:
            - "create file in root"
            - "save to repository root"
            - ".md in d:\\PROJECTS\\CORTEX\\"
            - ".md in d:\\PROJECTS\\NOOR CANVAS\\"
            - ".md in /Users/asifhussain/PROJECTS/CORTEX/"
            - ".md in /Users/"
            - ".md in /home/"
            - "repository_root / "
            - "project_root / "
            - "workspace_root / "
          summary_markers:
            - "summary"
            - "report"
            - "analysis"
            - "status"
            - "completion"
            - "investigation"
            - "update"
            - "changelog"
            - "notes"
            - "documentation"
        scope: ["intent", "file_path", "operation"]
        logic: "AND"

      verification_required:
        - type: "path_validation"
          description: "Verify document created in cortex-brain/documents/"
          requirement: "File path MUST contain 'cortex-brain/documents/'"

        - type: "category_check"
          description: "Verify document placed in appropriate category"
          requirement: "Must be in reports/, analysis/, summaries/, etc."

      alternatives:
        - "Use CORTEX/cortex-brain/documents/reports/ for completion reports"
        - "Use CORTEX/cortex-brain/documents/analysis/ for investigations"
        - "Use CORTEX/cortex-brain/documents/summaries/ for quick overviews"
        - "Use CORTEX/cortex-brain/documents/conversation-captures/ for strategic conversations"
        - "Use CORTEX/cortex-brain/documents/planning/ for planning documents"
        - "See CORTEX/cortex-brain/documents/README.md for full structure"

      evidence_template: |
        🚨 REPOSITORY ROOT POLLUTION DETECTED - OPERATION BLOCKED

        Attempted File: '{file_path}'
        Expected Location: CORTEX/cortex-brain/documents/{category}/

        ❌ ABSOLUTELY FORBIDDEN:
        - d:\PROJECTS\CORTEX\summary.md ← ROOT (WRONG)
        - d:\PROJECTS\NOOR CANVAS\update.md ← ROOT (WRONG)
        - /Users/asifhussain/PROJECTS/CORTEX/report.md ← ROOT (WRONG)
        - Any file directly in repository root directory

        ✅ REQUIRED STRUCTURE:
        - Reports → CORTEX/cortex-brain/documents/reports/
        - Analysis → CORTEX/cortex-brain/documents/analysis/
        - Summaries → CORTEX/cortex-brain/documents/summaries/
        - Investigations → CORTEX/cortex-brain/documents/investigations/
        - Planning → CORTEX/cortex-brain/documents/planning/

        Repository root is STRICTLY RESERVED for:
        - README.md (project introduction)
        - LICENSE (legal)
        - Package files (package.json, requirements.txt, setup.py)
        - Configuration (cortex.config.json, .gitignore)
        - Build scripts (build.py, Makefile)

        This rule applies to:
        - Standalone CORTEX installations (CORTEX/ repo)
        - Embedded CORTEX installations (NOOR-CANVAS/CORTEX/)
        - All development environments

      rationale: |
        NO_ROOT_SUMMARY_DOCUMENTS: Repository Organization Standard - STRICT ENFORCEMENT

        Real incident (2025-11-25 - dev environment):
        - CORTEX created files in repository root instead of CORTEX folder
        - User: "Found another issue in CORTEX in dev environment. CORTEX was 
          creating files in the root of the repo instead of the CORTEX folder."
        - User: "Add a rule to make this forbidden. No summary, update, reports 
          should be created in the root of the repo."
        - Result: Upgraded from "warning" to "blocked" severity

        Why Root-Level Documents Are BLOCKED:

        1. Repository Clutter (Critical Issue):
           - Root directory becomes unnavigable with accumulated documents
           - Hard to find important files (README, LICENSE, package.json)
           - Git status becomes noisy (dozens of unrelated files)
           - New contributors confused by file soup
           - Professional appearance destroyed

        2. Loss of Context:
           - No categorization = documents impossible to find
           - "Which report is the latest?" ← unanswerable
           - "Where's the security analysis?" ← lost in root
           - Search becomes time-consuming guessing game
           - Historical context lost (no folder-based organization)

        3. Merge Conflicts:
           - Multiple people creating documents in root simultaneously
           - Filename collisions extremely likely
           - No clear ownership or hierarchy
           - Git conflicts on unrelated files

        4. Violates CORTEX Organization Mandate:
           - CORTEX has structured document system (cortex-brain/documents/)
           - Category-based organization already exists and works
           - Ignoring structure creates technical debt
           - Future migration becomes expensive

        5. Embedded Installation Chaos:
           - When CORTEX embedded in user repo (e.g., NOOR-CANVAS/CORTEX/)
           - Root-level CORTEX files pollute user's application repository
           - User repo becomes mixed CORTEX + application artifacts
           - Cleanup difficult (which files are CORTEX vs application?)

        CORTEX Document Structure (MANDATORY):

        ```
        CORTEX/                           ← CORTEX folder (standalone or embedded)
          cortex-brain/
            documents/
              ├── reports/                # Implementation completion, status reports
              │   ├── CORTEX-3.0-FINAL-REPORT.md
              │   ├── PHASE-0-COMPLETION-REPORT.md
              │   └── ISSUE-67-FIX-REPORT.md
              │
              ├── analysis/               # Deep investigations, performance analysis
              │   ├── ROUTER-PERFORMANCE-ANALYSIS.md
              │   ├── TOKEN-OPTIMIZATION-ANALYSIS.md
              │   └── SECURITY-AUDIT-2025-11-25.md
              │
              ├── summaries/              # Quick overviews, daily progress
              │   ├── TIER3-IMPLEMENTATION-SUMMARY.md
              │   ├── WEEKLY-PROGRESS-SUMMARY.md
              │   └── SPRINT-23-SUMMARY.md
              │
              ├── investigations/         # Research findings, explorations
              │   ├── CORTEX-3.0-INVESTIGATION.md
              │   └── FEATURE-FEASIBILITY-STUDY.md
              │
              ├── planning/               # Roadmaps, implementation plans
              │   ├── CORTEX-4.0-ROADMAP.yaml
              │   └── MIGRATION-PLAN.yaml
              │
              ├── conversation-captures/  # Strategic conversations
              │   └── CONVERSATION-CAPTURE-2025-11-25-ARCHITECTURE.md
              │
              └── implementation-guides/  # How-to guides
                  └── CORTEX-INTEGRATION-GUIDE.md
        ```

        Standalone vs Embedded Installations:

        **Standalone (CORTEX repository):**
        ```
        d:\PROJECTS\CORTEX\
          ├── README.md                   ✅ Allowed in root
          ├── LICENSE                     ✅ Allowed in root
          ├── cortex-brain/
          │   └── documents/
          │       └── reports/
          │           └── REPORT.md       ✅ Correct location
          └── WRONG-SUMMARY.md            ❌ BLOCKED
        ```

        **Embedded (CORTEX inside user repo):**
        ```
        d:\PROJECTS\NOOR-CANVAS\
          ├── README.md                   ✅ User's file
          ├── CORTEX/
          │   ├── cortex-brain/
          │   │   └── documents/
          │   │       └── reports/
          │   │           └── REPORT.md   ✅ Correct location
          │   └── WRONG-UPDATE.md         ❌ BLOCKED (CORTEX root)
          └── WRONG-SUMMARY.md            ❌ BLOCKED (user repo root)
        ```

        What IS Allowed in Repository Root:
        - README.md (project introduction)
        - LICENSE (legal requirement)
        - Package files (package.json, requirements.txt, setup.py, Cargo.toml)
        - Configuration (cortex.config.json, .editorconfig, .gitignore)
        - Build scripts (build.py, Makefile, build.sh)
        - CI/CD (Jenkinsfile, .github/workflows/)
        - Version control (.gitattributes)

        What is NEVER Allowed in Repository Root:
        - Summaries (SUMMARY-*.md)
        - Reports (REPORT-*.md, *-COMPLETE.md)
        - Analysis (*-ANALYSIS.md)
        - Status updates (STATUS-*.md, UPDATE-*.md)
        - Investigation reports (INVESTIGATION-*.md)
        - Planning documents (PLAN-*.md, ROADMAP-*.md)
        - Notes (NOTES-*.md, TODO-*.md)
        - Any documentation files

        Enforcement Strategy:
        - Severity: "blocked" (hard stop, not warning)
        - Detection: File path analysis + intent keywords
        - Pre-flight: Validate path before file creation
        - Post-flight: Validate no root files after operations

        Integration Points:
        - BrainProtector: Validates before document creation
        - create_file tool: Path validation interceptor
        - FileValidator: Post-operation verification
        - DocumentationOrchestrator: Enforces structure

        This rule BLOCKS operations that violate structure.
        No exceptions, no warnings, no bypass mechanism.

    - rule_id: "YAML_ONLY_PLANNING"
      name: "YAML-Only Planning Documents (No Markdown Plans)"
      severity: "blocked"
      description: "ALL planning documents MUST be created in YAML format, NEVER Markdown - prevents documentation bloat and enforces machine-readable standards"

      detection:
        combined_keywords:
          planning_document:
            - "plan"
            - "planning"
            - "roadmap"
            - "design"
            - "consolidation"
            - "implementation plan"
            - "comprehensive plan"
          and_markdown_format:
            - ".md"
            - "markdown"
            - "create markdown plan"
          not_user_facing:
            - "!story"
            - "!guide"
            - "!tutorial"
        scope: ["file_path", "description", "operation"]
        logic: "AND"

      verification_required:
        - type: "format_validation"
          description: "Verify plan document created as YAML, not Markdown"
          requirement: "File extension MUST be .yaml, NOT .md"

        - type: "location_validation"
          description: "Verify plan placed in planning folder"
          requirement: "File path MUST be cortex-brain/documents/planning/"

        - type: "schema_validation"
          description: "Verify YAML follows structured planning schema"
          requirement: "YAML MUST validate against planning schema"

      alternatives:
        - "Create YAML plan in cortex-brain/documents/planning/[name].yaml"
        - "Use structured YAML schemas for all planning documents"
        - "Reference existing YAML plans: YAML-PHASE-TRACKER-DESIGN.yaml"
        - "Use cortex-brain/CORTEX-UNIFIED-ARCHITECTURE.yaml as template"

      evidence_template: |
        🚨 MARKDOWN PLANNING DOCUMENT DETECTED

        File: '{file_path}'
        Type: Planning Document (should be YAML)

        VIOLATION: Planning documents MUST be YAML format, NOT Markdown

        ❌ WRONG:
        - DOCUMENTATION-CONSOLIDATION-COMPREHENSIVE-PLAN.md
        - IMPLEMENTATION-PLAN.md
        - FEATURE-DESIGN.md
        - ARCHITECTURE-PLAN.md

        ✅ CORRECT:
        - documentation-consolidation-plan.yaml
        - implementation-plan.yaml
        - feature-design.yaml
        - architecture-plan.yaml

        Why YAML-Only Planning?

        1. **Prevents Documentation Bloat**
           - Markdown plans tend to be verbose (10-50 pages)
           - YAML enforces concise structured format
           - Token efficiency (YAML 60-80% smaller than MD)

        2. **Machine-Readable**
           - YAML can be parsed and processed programmatically
           - Enables automated validation and tracking
           - Integrates with CORTEX brain systems

        3. **Consistency**
           - Enforced schema structure
           - Standard fields across all plans
           - No "wall of text" formatting variations

        4. **Searchability**
           - Structured queries on plan fields
           - Easy to filter and aggregate
           - Better brain integration

        Correct Location:
        - cortex-brain/documents/planning/[plan-name].yaml

        Exception:
        - User-facing documentation (stories, guides, tutorials) CAN be Markdown
        - Internal planning/design MUST be YAML

      rationale: |
        YAML_ONLY_PLANNING: Documentation Bloat Prevention

        Real incident (2025-11-18):
        - CORTEX created: DOCUMENTATION-CONSOLIDATION-COMPREHENSIVE-PLAN.md
        - File size: 23KB (extensive markdown document)
        - User: "why is CORTEX still generating md plans instead of yaml plans?"
        - User: "Add to tier 0 that planning should ALWAYS done using yaml files NEVER MD to prevent documentation bloat"

        Problem with Markdown Plans:
        - Verbose "comprehensive" documents (10-50 pages typical)
        - Heavy token cost to read/process
        - Difficult to parse programmatically
        - No enforced structure (inconsistent formats)
        - Accumulates as "documentation debt"

        YAML Planning Benefits:
        - Enforced concise structure
        - 60-80% token reduction vs Markdown
        - Machine-readable for automation
        - Consistent schema across all plans
        - Easy to validate and query

        Implementation:
        - CORTEX creates planning YAML schemas
        - Validation against JSON Schema
        - Brain integration for automated tracking
        - Markdown reserved ONLY for user-facing docs (stories, guides)

        Related Rules:
        - MACHINE_READABLE_FORMATS (Tier 0 instinct)
        - NO_ROOT_SUMMARY_DOCUMENTS (Layer 3)

        Reference Examples:
        - cortex-brain/documents/planning/YAML-PHASE-TRACKER-DESIGN.yaml
        - cortex-brain/CORTEX-UNIFIED-ARCHITECTURE.yaml
        - cortex-operations.yaml

        User Feedback:
        "Add to tier 0 of cortex that planning should ALWAYS done using yaml files NEVER MD 
        to prevent documentation bloat" - Asif Hussain, 2025-11-18
        │
        ├── investigations/       # Research, architecture investigations
        │   ├── AUTH-FEATURE-INVESTIGATION.md
        │   └── DATABASE-MIGRATION-INVESTIGATION.md
        │
        ├── planning/             # Roadmaps, implementation plans
        │   ├── CORTEX-4.0-PLANNING.md
        │   └── features/
        │       └── PLAN-2025-11-17-authentication.md
        │
        ├── conversation-captures/ # Strategic conversation captures
        │   └── CONVERSATION-CAPTURE-2025-11-14-AUTHENTICATION.md
        │
        └── implementation-guides/  # How-to guides, integration docs
            └── CORTEX-SETUP-GUIDE.md
        ```

        Benefits of Organized Structure:
        - Easy to find related documents
        - Clear ownership and purpose
        - Searchable by category
        - No root-level clutter
        - Professional appearance

        Root Directory Reserved For:
        ```
        CORTEX/
        ├── README.md              ✅ Project overview
        ├── LICENSE                ✅ Legal
        ├── package.json           ✅ Dependencies
        ├── requirements.txt       ✅ Python packages
        ├── cortex.config.json     ✅ Configuration
        ├── setup.py               ✅ Installation
        ├── mkdocs.yml             ✅ Docs build config
        └── .gitignore             ✅ Git config
        ```

        Example Violations:

        ❌ BAD:
        ```
        d:\PROJECTS\CORTEX\INVESTIGATION-ANALYSIS-REPORT.md
        d:\PROJECTS\CORTEX\CORTEX-3.0-IMPLEMENTATION-COMPLETE.md
        d:\PROJECTS\CORTEX\COMPREHENSIVE-CORTEX-ANALYSIS-REPORT.md
        ```

        ✅ GOOD:
        ```
        d:\PROJECTS\CORTEX\cortex-brain\documents\analysis\INVESTIGATION-ANALYSIS-REPORT.md
        d:\PROJECTS\CORTEX\cortex-brain\documents\reports\CORTEX-3.0-IMPLEMENTATION-COMPLETE.md
        d:\PROJECTS\CORTEX\cortex-brain\documents\analysis\COMPREHENSIVE-CORTEX-ANALYSIS-REPORT.md
        ```

        Enforcement:
        - Brain Protector challenges root-level document creation
        - Suggests appropriate category automatically
        - Provides full path template
        - References cortex-brain/documents/README.md for guidelines

        Override Cases (Rare):
        - User explicitly requests root-level placement
        - Temporary scaffolding during setup
        - Files intended for repository metadata (CHANGELOG.md, CONTRIBUTING.md)

        This maintains clean repository structure and ensures documents
        are findable, organized, and maintainable long-term.

# Layer 4: Hemisphere Specialization
- layer_id: "hemisphere_specialization"
  name: "Hemisphere Specialization"
  description: "Strategic vs tactical separation"
  priority: 4

  rules:
    - rule_id: "LEFT_BRAIN_TACTICAL"
      name: "Left Brain Tactical Only"
      severity: "warning"
      description: "Strategic planning logic in tactical executor"

      detection:
        files:
          - "code-executor.md"
          - "test-generator.md"
          - "error-corrector.md"
        keywords:
          - "create plan"
          - "estimate time"
          - "assess risk"
          - "strategy"
        scope: ["intent"]

      alternatives:
        - "Move planning logic to work-planner.md"
        - "Keep execution logic in code-executor.md"
        - "Use corpus callosum for coordination"

      evidence: "LEFT brain should execute, not plan"

    - rule_id: "RIGHT_BRAIN_STRATEGIC"
      name: "Right Brain Strategic Only"
      severity: "warning"
      description: "Tactical execution logic in strategic planner"

      detection:
        files:
          - "work-planner.md"
          - "intent-router.md"
        keywords:
          - "write code"
          - "run test"
          - "execute"
          - "implement"
        scope: ["intent"]

      alternatives:
        - "Delegate execution to LEFT brain agents"
        - "Keep planning in RIGHT brain"
        - "Use agent coordination"

      evidence: "RIGHT brain should plan, not execute"

# Layer 5: SKULL Protection (Safety, Knowledge, Validation & Learning)
- layer_id: "skull_protection"
  name: "SKULL Protection Layer"
  description: "Test validation and quality enforcement (prevents November 9th incident)"
  priority: 5

  rules:
    - rule_id: "SKULL_TEST_BEFORE_CLAIM"
      name: "Test Before Claim (SKULL-001)"
      severity: "blocked"
      description: "Never claim a fix is complete without test validation"

      detection:
        keywords:
          - "fixed ✅"
          - "complete ✅"
          - "done ✅"
          - "implemented ✅"
        without_keywords:
          - "test passed"
          - "test verified"
          - "validated by test"
          - "pytest"
        scope: ["response"]

      alternatives:
        - "Create automated test before claiming fix"
        - "Run test and include results in response"
        - "Show test output: 'Fixed ✅ (Verified by: test_button_color)'"

      evidence_template: "Claim: '{match}' without test validation"

      rationale: |
        SKULL-001: Test Before Claim

        Real incident (2025-11-09):
        - CSS fixes claimed "Fixed ✅" three times
        - Vision API claimed "Auto-engages ✅" 
        - Zero tests run to validate
        - User had to report "not working" each time

        SKULL prevents this by BLOCKING any success claim without test validation.

    - rule_id: "SKULL_INTEGRATION_VERIFICATION"
      name: "Integration Verification (SKULL-002)"
      severity: "blocked"
      description: "Integration must be tested end-to-end"

      detection:
        keywords:
          - "integration complete"
          - "components connected"
          - "API integrated"
          - "auto-engages"
        without_keywords:
          - "end-to-end test"
          - "integration test"
          - "e2e test"
        scope: ["description"]

      alternatives:
        - "Create end-to-end integration test"
        - "Test full call chain: A → B → C"
        - "Verify actual execution path, not just config"

      evidence_template: "Integration claim without E2E test: '{match}'"

      rationale: |
        SKULL-002: Integration Verification

        Real incident (2025-11-09):
        - Vision API "integration" claimed complete
        - Only config was changed
        - No test of actual call chain
        - Vision API was never actually called

        SKULL prevents this by requiring end-to-end integration tests.

    - rule_id: "SKULL_VISUAL_REGRESSION"
      name: "Visual Regression (SKULL-003)"
      severity: "warning"
      description: "CSS/UI changes require visual validation"

      detection:
        keywords:
          - "css fixed"
          - "style updated"
          - "color changed"
          - "UI improved"
        without_keywords:
          - "visual test"
          - "computed style"
          - "playwright"
          - "browser test"
        scope: ["description"]

      alternatives:
        - "Add visual regression test (Playwright/Puppeteer)"
        - "Verify computed style in browser"
        - "Include before/after screenshot comparison"

      evidence_template: "CSS/UI change without visual test: '{match}'"

      rationale: |
        SKULL-003: Visual Regression

        Real incident (2025-11-09):
        - CSS rules applied to fix title color
        - Claimed "Fixed ✅" without checking browser
        - Cache wasn't cleared, changes not visible
        - Repeated 3 times with same approach

        SKULL prevents this by requiring visual validation of CSS changes.

    - rule_id: "SKULL_RETRY_WITHOUT_LEARNING"
      name: "Retry Without Learning (SKULL-004)"
      severity: "warning"
      description: "Must diagnose failures before retrying same approach"

      detection:
        combined_keywords:
          retry_marker:
            - "try again"
            - "retry"
            - "attempt 2"
            - "attempt 3"
          no_diagnosis:
            - "same fix"
            - "reapply"
            - "rebuild again"
        without_keywords:
          - "diagnosed"
          - "root cause"
          - "cache cleared"
          - "verified"
        scope: ["description"]
        logic: "AND"

      alternatives:
        - "Diagnose WHY previous fix failed"
        - "Check: file contents, browser cache, build output, computed styles"
        - "Change approach based on diagnosis"
        - "Add test to prevent regression"

      evidence_template: "Retry without diagnosis: '{description}'"

      rationale: |
        SKULL-004: Retry Without Learning

        Real incident (2025-11-09):
        - CSS fix applied
        - User: "didn't work"
        - Same CSS fix applied again
        - User: "still didn't work"  
        - Same CSS fix applied THIRD time
        - No diagnosis of why it failed

        SKULL prevents this by requiring root cause analysis before retries.

    - rule_id: "SKULL_TRANSFORMATION_VERIFICATION"
      name: "Transformation Verification (SKULL-005)"
      severity: "blocked"
      description: "Operations claiming transformation MUST produce measurable changes"

      detection:
        combined_keywords:
          transformation_claim:
            - "transformation complete"
            - "refresh complete"
            - "converted"
            - "updated documentation"
            - "generated"
          success_claim:
            - "success"
            - "completed successfully"
            - "fixed ✅"
            - "done ✅"
        scope: ["description", "log_output"]
        logic: "AND"

      verification_required:
        - type: "file_hash_comparison"
          description: "Compare file hash before/after operation"
          requirement: "Hashes MUST differ for transformation operations"

        - type: "git_diff_check"
          description: "Verify git diff shows actual changes"
          requirement: "git diff MUST show modifications, not empty output"

        - type: "content_analysis"
          description: "Validate transformation logic executed"
          requirement: "Operation MUST NOT be pass-through (input != output)"

      alternatives:
        - "Implement actual transformation logic (not pass-through)"
        - "Mark operation as 'validation-only' if no transformation needed"
        - "Add integration test verifying file changes occur"
        - "Change success message to reflect pass-through behavior"

      evidence_template: "Operation '{operation_name}' claims transformation but produces no changes"

      rationale: |
        SKULL-005: Transformation Verification

        Real incident (2025-11-10):
        - refresh_cortex_story operation executed
        - Module apply_narrator_voice_module.py claims "transformation complete"
        - Returns success=True with "Narrator voice transformation complete"
        - BUT: Line 123 does `context['transformed_story'] = story_content` (pass-through!)
        - File hash unchanged after operation
        - git diff shows NO changes
        - User discovers operation is fake

        Impact:
        - User trust degradation (claims success but does nothing)
        - Status inflation (operations marked READY when incomplete)
        - Integration failures (downstream operations expect real data)

        SKULL-005 prevents this by:
        1. Detecting transformation + success claims in output
        2. Requiring file hash comparison test
        3. Blocking completion without measurable changes
        4. Forcing honest status reporting (PARTIAL vs READY)

        Implementation:
        - Add @verify_transformation decorator to operation modules
        - Integration tests MUST check before/after file state
        - CI fails if transformation claims success but git diff empty
        - Status documents distinguish architecture vs implementation

    - rule_id: "SKULL_PRIVACY_PROTECTION"
      name: "Privacy Protection (SKULL-006)"
      severity: "blocked"
      description: "Publish operations MUST NOT include files with machine-specific paths or private data"

      detection:
        patterns:
          - "AHHOME"
          - ".coverage.*.* "
          - "C:\\\\"
          - "D:\\\\"
          - "/home/[a-z]+"
          - "/Users/[a-z]+"
        file_types:
          - "**/*.log"
          - "**/logs/**"
          - "**/.coverage.*"
          - "**/health-reports/**"
          - "**/__pycache__/**"
        scope: ["published_files"]

      verification_required:
        - type: "privacy_scan"
          description: "Scan all published files for machine-specific paths"
          requirement: "Zero files with absolute paths (C:\\, D:\\, /home/, AHHOME)"

        - type: "exclusion_test"
          description: "Test that publish script excludes privacy-leaking files"
          requirement: "Test MUST verify .coverage.*, logs/, health-reports/ excluded"

        - type: "config_sanitization"
          description: "Verify config files use template values, not real paths"
          requirement: "cortex.config.json MUST use placeholders, not AHHOME paths"

      alternatives:
        - "Add file patterns to EXCLUDE_PATTERNS in publish script"
        - "Create .publishignore file with privacy exclusions"
        - "Add pre-publish scan that fails on privacy leak"
        - "Use template configs with placeholder paths"

      evidence_template: "Published file contains privacy data: '{file_path}' - found '{privacy_leak}'"

      rationale: |
        SKULL-006: Privacy Protection

        Real incident (2025-11-12):
        - User runs publish script
        - Discovers .coverage.AHHOME.12345.XgvxuuYx in publish/CORTEX/
        - 7 coverage files with machine name exposed
        - logs/ambient_capture.log contains C:\Windows\Temp paths
        - cortex.config.json contains AHHOME machine paths
        - health-reports/ has user-specific diagnostic data

        Impact:
        - Privacy violation (machine names, usernames exposed)
        - Distribution bloat (unnecessary test artifacts)
        - Professionalism degradation (dev artifacts in user package)

        SKULL-006 prevents this by:
        1. Scanning published files for machine-specific patterns
        2. Requiring publish script exclude logs, coverage, health data
        3. Blocking publish if privacy leaks detected
        4. Enforcing template configs instead of real paths

        Implementation:
        - Add EXCLUDE_PATTERNS to publish script (logs, coverage, health)
        - Create test_publish_privacy.py that scans for leaks
        - Add pre-publish hook that runs privacy scan
        - Use cortex.config.template.json instead of cortex.config.json

    - rule_id: "GIT_COMMIT_PRIVACY_VALIDATION"
      name: "Git Commit Privacy Validation (Tier 0 Instinct)"
      severity: "blocked"
      description: "Git commits MUST NOT contain files with absolute paths or machine-specific data"

      detection:
        patterns:
          - "C:\\\\"
          - "D:\\\\"
          - "/home/[a-z]+"
          - "/Users/[a-z]+"
          - "AHHOME"
          - "HOSTNAME"
          - "[A-Z]+-PC"  # Machine names like DESKTOP-PC, LAPTOP-PC
        scope: ["staged_files", "git_diff"]

      verification_required:
        - type: "pre_commit_privacy_scan"
          description: "Scan all staged files for absolute paths before commit"
          requirement: "Zero files with absolute paths (C:\\, D:\\, /home/, /Users/, machine names)"

        - type: "git_diff_validation"
          description: "Validate git diff contains only relative paths"
          requirement: "All file references MUST use relative paths from repo root"

        - type: "merge_content_validation"
          description: "Validate merged content does not introduce privacy leaks"
          requirement: "Git merge operations MUST scan resulting files before accepting"

      alternatives:
        - "Use relative paths: src/, cortex-brain/, tests/"
        - "Use Path() objects with relative references"
        - "Use environment variables: os.getenv('CORTEX_ROOT')"
        - "Use config templates with placeholders: {{CORTEX_ROOT}}"

      evidence_template: "Staged file '{file_path}' line {line_num} contains absolute path: '{privacy_leak}'"

      rationale: |
        Git Commit Privacy Validation (Tier 0 Instinct)

        Issue identified (2025-11-28):
        - Git merge operations could include files with machine-specific paths
        - No validation of staged files before commit
        - SKULL-006 enforced privacy for publish, but not for git commits
        - Privacy leaks in git history when files pushed to remote

        Examples of violations:
        ❌ C:\PROJECTS\CORTEX\src\module.py (Windows absolute path)
        ❌ D:\Work\data.json (alternate drive)
        ❌ /home/asif/code/file.py (Unix home directory)
        ❌ /Users/asif/Desktop/temp.log (macOS user directory)
        ❌ AHHOME environment variable references

        Impact:
        - Privacy violation (exposes usernames, machine names, file structure)
        - Git history contamination (absolute paths persist in history)
        - Merge conflicts when paths differ across machines
        - Unprofessional git log (machine-specific references)

        This Tier 0 instinct prevents privacy leaks by:
        1. Scanning staged files before EVERY commit
        2. Blocking commits with absolute path violations
        3. Validating merge results before accepting
        4. Integration with PhaseCheckpointManager for automatic enforcement
        5. Providing actionable error messages with file + line numbers

        Implementation (git-enhancements-feature-plan.md):
        - PhaseCheckpointManager.validate_staged_files_privacy()
        - Pre-commit hook: git diff --cached | scan for patterns
        - Error message shows file, line number, and violation
        - Suggests remediation: relative paths, env vars, config templates
        - Checkpoint creation blocked until violations resolved

        Test coverage:
        - test_validate_staged_files_blocks_absolute_paths()
        - test_validate_staged_files_blocks_unix_home_paths()
        - test_validate_staged_files_blocks_machine_names()
        - test_checkpoint_creation_fails_on_privacy_violation()

        This extends SKULL-006 from publish-time to commit-time enforcement.

    - rule_id: "SKULL_HEADER_FOOTER_IN_RESPONSE"
      name: "Faculty Integrity Check (SKULL-007)"
      severity: "blocked"
      description: "Publish package MUST contain ALL essential CORTEX faculties for full operation"

      detection:
        missing_faculties:
          - "Tier 0 (SKULL) not found"
          - "Tier 1 (Memory) not found"
          - "Tier 2 (Knowledge) not found"
          - "Tier 3 (Context) not found"
          - "Agents missing"
          - "Operations missing"
          - "Entry point missing"
        scope: ["published_files"]

      verification_required:
        - type: "comprehensive_faculty_test"
          description: "Test that verifies ALL CORTEX faculties exist in publish package"
          requirement: "test_cortex_fully_operational MUST pass"

        - type: "tier_verification"
          description: "Verify all 4 tiers (Tier 0-3) present"
          requirement: "brain_protector.py, conversation_manager.py, knowledge_graph/, context_intelligence.py"

        - type: "agent_verification"
          description: "Verify 10 specialist agents present"
          requirement: "cortex_agents/ directory with base_agent.py and agent implementations"

        - type: "entry_point_verification"
          description: "Verify GitHub Copilot integration files"
          requirement: "CORTEX.prompt.md and copilot-instructions.md in .github/"

        - type: "documentation_verification"
          description: "Verify user documentation present"
          requirement: "story.md, setup-guide.md, technical-reference.md, etc."

      alternatives:
        - "Use inclusion-based publish (copy ONLY essential files)"
        - "Create comprehensive faculty test that blocks publish if faculties missing"
        - "Maintain ESSENTIAL_FILES list of required CORTEX components"

      evidence_template: "Published CORTEX missing faculty: '{faculty_name}' - file not found: '{file_path}'"

      rationale: |
        SKULL-007: Faculty Integrity Check

        Real incident (2025-11-12):
        - Exclusion-based publish script too aggressive
        - Excluded 97.9% of files (good for privacy!)
        - BUT also excluded essential faculties:
          ❌ All 10 specialist agents missing
          ❌ Tier 1 conversation_tracker.py missing
          ❌ Entry points (CORTEX.prompt.md) missing
          ❌ Plugin system missing
        - Published CORTEX was incomplete and non-functional

        Impact:
        - Users copy broken CORTEX to their application
        - CORTEX cannot coordinate work (no agents)
        - CORTEX cannot remember (no Tier 1)
        - Copilot cannot find CORTEX (no entry points)
        - Result: Complete failure, wasted user time

        SKULL-007 prevents this by:
        1. Comprehensive test that verifies ALL faculties present
        2. Blocking publish if any faculty missing
        3. Listing exact files required for each faculty
        4. Testing BEFORE deployment (not discovery by users)

        The Brilliant Fix:
        Instead of exclusion-based publish (exclude dev files),
        switch to INCLUSION-based publish (include ONLY essentials):

        Benefits:
        - Simpler logic (copy what's needed vs exclude what's not)
        - Guaranteed completeness (explicit list of essentials)
        - No accidental omissions (inclusion list is exhaustive)
        - Better maintainability (clear intent)

        Implementation:
        - Create test_publish_faculties.py with test_cortex_fully_operational()
        - Test checks: Tier 0-3, Agents, Operations, Plugins, Entry Points, Docs
        - Publish script copies ONLY essential directories
        - Test runs BEFORE declaring publish complete

        Result:
        - Package size: 393 files, 3.8 MB (perfect!)
        - All faculties present: ✅
        - No privacy leaks: ✅  
        - CORTEX fully operational: ✅

    - rule_id: "SKULL_HEADER_FOOTER_IN_RESPONSE_LEGACY"
      name: "Header/Footer in Copilot Response (Legacy)"
      severity: "blocked"
      description: "Operation orchestrators MUST include formatted headers/footers in Copilot Chat response"

      detection:
        combined_keywords:
          orchestrator_execution:
            - "execute operation"
            - "orchestrator.execute"
            - "operation complete"
          missing_header_footer:
            - "formatted_header: None"
            - "formatted_footer: None"
            - "no header in response"
        scope: ["code", "test_output"]
        logic: "AND"

      verification_required:
        - type: "result_object_check"
          description: "Verify OperationResult contains formatted_header/footer"
          requirement: "result.formatted_header MUST NOT be None"

        - type: "response_formatter_check"
          description: "Verify ResponseFormatter uses stored headers"
          requirement: "Chat response MUST include header/footer in code blocks"

        - type: "visual_inspection"
          description: "Verify header appears in Copilot Chat window"
          requirement: "User MUST see copyright header + purpose + accomplishments"

      alternatives:
        - "Use format_minimalist_header() and store in result.formatted_header"
        - "Use format_completion_footer() and store in result.formatted_footer"
        - "Ensure ResponseFormatter wraps headers in code blocks for display"
        - "Add integration test verifying header presence in formatted response"

      evidence_template: |
        Operation '{operation_name}' executed but headers not in Copilot response

        Expected in Copilot Chat:
        ```
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
          CORTEX {operation_name} Orchestrator v{version}
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        Profile: {profile} │ Mode: {mode} │ Started: {timestamp}

        📋 Purpose: {purpose}

        © 2024-2025 Asif Hussain │ Proprietary │ github.com/asifhussain60/CORTEX
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        ```

        Actual: Header missing or only in terminal

      rationale: |
        SKULL-006: Header/Footer in Copilot Response

        Real incident (2025-11-11):
        - User: "why is header not being displayed?"
        - Headers printing to terminal (stdout) correctly
        - But GitHub Copilot Chat response had NO header
        - ResponseFormatter suppressing headers after first operation
        - User specified they want header "in the copilot response in the chat window"

        Root Cause:
        1. Orchestrators print headers to stdout (terminal visibility)
        2. But stdout doesn't reach Copilot Chat window
        3. ResponseFormatter has _first_operation_shown flag (header suppression)
        4. User sees execution in terminal, but Chat response lacks context

        Why This Matters:
        - Copyright attribution must be visible to user
        - Purpose/profile provides context for what operation did
        - Accomplishments show value delivered
        - Headers make operations feel professional and informative
        - Chat is primary interface (terminal is secondary)

        Solution:
        1. Orchestrators generate formatted headers/footers
        2. Store in OperationResult.formatted_header/footer
        3. ResponseFormatter checks for stored headers (priority)
        4. Wraps headers in code blocks for proper display
        5. Also prints to terminal for immediate visibility

        SKULL-006 enforces this by:
        - Requiring formatted_header/footer in OperationResult
        - Integration tests verify headers in formatted response
        - Blocking completion if headers missing from Chat output
        - Ensuring copyright/attribution always visible

        Implementation:
        ```python
        # In orchestrator execute():
        formatted_header = format_minimalist_header(...)
        print(formatted_header)  # Terminal visibility

        # ... operation logic ...

        formatted_footer = format_completion_footer(...)
        print(formatted_footer)  # Terminal visibility

        return OperationResult(
            success=True,
            formatted_header=formatted_header,  # For Copilot Chat
            formatted_footer=formatted_footer   # For Copilot Chat
        )
        ```

    - rule_id: "SKULL_ALL_TESTS_MUST_PASS"
      name: "All Tests Must Pass (SKULL-007)"
      severity: "blocked"
      description: "Test suite MUST have 100% pass rate before claiming any work complete"

      detection:
        keywords:
          - "fixed ✅"
          - "complete ✅"
          - "done ✅"
          - "implemented ✅"
          - "ready for review"
          - "PR ready"
        with_test_failures:
          - "failed"
          - "FAILED"
          - "ERROR"
          - "test failures"
          - "X passed, Y failed"
        scope: ["response", "test_output"]

      verification_required:
        - type: "full_test_suite"
          description: "Run complete test suite (not just new tests)"
          requirement: "pytest exit code MUST be 0 (100% pass rate)"

        - type: "no_skipped_critical_tests"
          description: "Verify no critical tests are skipped"
          requirement: "Core functionality tests MUST run (not skipped)"

        - type: "test_count_validation"
          description: "Ensure test count doesn't decrease unexpectedly"
          requirement: "Total tests should increase or stay same (not decrease)"

      alternatives:
        - "Fix ALL failing tests before claiming completion"
        - "Mark work as 'IN PROGRESS' until tests pass"
        - "Revert changes if they break existing tests"
        - "Fix pre-existing failures first (clean baseline)"

      evidence_template: |
        Work claimed complete but tests failing!

        Test Results: {test_summary}
        - Passed: {passed_count}
        - Failed: {failed_count}  ❌
        - Skipped: {skipped_count}

        SKULL-007 VIOLATION: Cannot claim "done ✅" with {failed_count} failures

      rationale: |
        SKULL-007: All Tests Must Pass

        Real incident (2025-11-11):
        - User: "are all tests passing?"
        - Agent: Ran tests, found 123 failed, 337 passed
        - Agent response: "No, not all tests are passing" (honest)
        - BUT: Agent claimed SKULL-006 work "complete ✅" earlier
        - Pre-existing failures create false confidence

        Why Pre-existing Failures Are Dangerous:
        1. Mask New Regressions:
           - Can't tell if new code broke something
           - "Already broken" becomes acceptable
           - Technical debt accumulates silently

        2. Create False Confidence:
           - "My tests pass" ≠ "All tests pass"
           - Incomplete validation of changes
           - Integration issues hidden

        3. Compound Over Time:
           - Each feature adds more failures
           - "Just one more broken test" mentality
           - Eventually unmaintainable

        4. Undermine Trust:
           - Claims of completion ring hollow
           - Quality standards erode
           - Testing becomes performative

        Examples from Current Failures:
        - 123 failed tests (51% failure rate!)
        - Categories: Agent internals, platform issues, schema errors
        - Some tests testing wrong APIs (implementation changed)
        - Some tests have environmental dependencies
        - All must be fixed before claiming ANY work complete

        SKULL-007 Enforcement:
        1. BLOCKING severity - cannot proceed with failures
        2. Requires full test suite run (not just new tests)
        3. Exit code 0 mandatory (100% pass rate)
        4. No "works on my machine" exceptions
        5. No "will fix later" promises

        Allowed Exceptions:
        - Known flaky tests marked with @pytest.mark.flaky
        - Platform-specific tests properly skipped on other platforms
        - Optional feature tests when feature disabled in config

        Not Allowed:
        - "These failures are unrelated to my work"
        - "I'll fix them in next PR"
        - "Tests are broken, not my code"
        - "Only my new tests need to pass"

        Implementation Strategy:
        1. Fix critical blockers first (schema, imports)
        2. Fix by category (agents, ambient, tier1)
        3. Update tests if implementation changed
        4. Mark truly optional tests appropriately
        5. Achieve 100% pass rate
        6. Maintain 100% going forward

        This is NOT optional. This is core quality engineering.

    - rule_id: "SKULL_MULTI_TRACK_VALIDATION"
      name: "Multi-Track Configuration Validation (SKULL-008)"
      severity: "blocked"
      description: "Multi-track mode MUST have valid configuration with proper phase distribution"

      detection:
        keywords:
          - "enable multi-track"
          - "activate multi-track"
          - "create tracks"
          - "split tracks"
          - "multi-machine mode"
        scope: ["intent", "description"]

      verification_required:
        - type: "track_balance_check"
          description: "Verify workload balanced across tracks"
          requirement: "Track estimated hours MUST not differ by >30%"

        - type: "dependency_isolation_check"
          description: "Verify no cross-track dependencies"
          requirement: "Phase groups MUST be self-contained per track"

        - type: "machine_assignment_check"
          description: "Verify each machine assigned to exactly one track"
          requirement: "No machine overlap, no unassigned machines"

        - type: "fun_name_uniqueness"
          description: "Verify track names are unique and generated properly"
          requirement: "Track names MUST be deterministic and collision-free"

      alternatives:
        - "Run track distribution algorithm to validate balance"
        - "Use PhaseDistributor.distribute() to check dependency isolation"
        - "Verify machine count matches track count"
        - "Test track name generation for collision resistance"

      evidence_template: |
        Multi-track mode validation failed!

        Configuration Issues:
        - Track balance: {balance_check}
        - Dependencies: {dependency_check}
        - Machines: {machine_check}
        - Track names: {name_check}

        SKULL-008: Multi-track MUST be properly configured before use

      rationale: |
        SKULL-008: Multi-Track Configuration Validation

        Multi-track mode is powerful but requires careful setup:

        1. Workload Balance:
           - Tracks with vastly different hours → bottlenecks
           - One machine idle while other overloaded
           - Race metrics meaningless if unfair
           Example: Track A (10h) vs Track B (40h) = broken

        2. Dependency Isolation:
           - Track A waiting on Track B output → blocked
           - Cross-dependencies defeat parallel development
           - Must group dependent phases on same track
           Example: "setup" phases must complete before "processing"

        3. Machine Assignment:
           - Machine assigned to multiple tracks → confusion
           - Unassigned machines → wasted capacity
           - Clear 1:1 or 1:N mapping required
           Example: AHHOME on both tracks = which context?

        4. Track Name Uniqueness:
           - Collision-resistant generation
           - Deterministic (same input → same name)
           - Human-memorable for commands
           Example: Hash collision → wrong track loaded

        Why This Matters:
        - Prevents split-mode failures mid-development
        - Ensures race metrics are meaningful
        - Maintains track isolation guarantees
        - Makes "continue implementation for [track]" reliable

        Validation Points:

        Pre-Initialization:
        - Check machine count > 0
        - Verify operations.yaml accessible
        - Validate module definitions exist

        Post-Distribution:
        - Balance check: max_hours/min_hours < 1.3 (30% tolerance)
        - Dependency check: No phase in track requires other track's output
        - Machine check: Each machine in exactly one track
        - Name check: All track names unique and deterministic

        Integration Test Required:
        ```python
        def test_multi_track_validation():
            # Setup
            machines = ["AHHOME", "Mac"]
            config = create_multi_track_config(machines, modules)

            # Balance check
            hours = [t.estimated_hours for t in config.tracks.values()]
            assert max(hours) / min(hours) < 1.3, "Imbalanced tracks"

            # Dependency check
            for track in config.tracks.values():
                deps = get_phase_dependencies(track.phases)
                assert all(d in track.phases for d in deps), "Cross-track dep"

            # Machine check
            all_machines = [m for t in config.tracks.values() for m in t.machines]
            assert len(all_machines) == len(set(all_machines)), "Duplicate machine"

            # Name check
            names = [t.track_name for t in config.tracks.values()]
            assert len(names) == len(set(names)), "Duplicate track name"
        ```

        Enforcement:
        - CLI script validates before writing config
        - Design sync validates before split
        - Continue command validates track exists
        - Consolidation validates all tracks present

    - rule_id: "SKULL_TRACK_ISOLATION"
      name: "Track Work Isolation (SKULL-009)"
      severity: "blocked"
      description: "Work on Track A MUST NOT modify Track B's assigned modules"

      detection:
        combined_keywords:
          track_context:
            - "continue implementation for"
            - "working on track"
            - "active track"
          cross_modification:
            - "modified module"
            - "updated file"
            - "changed"
        scope: ["intent", "log_output"]
        logic: "AND"

      verification_required:
        - type: "module_ownership_check"
          description: "Verify modified modules belong to active track"
          requirement: "All changed files MUST be in active track's module list"

        - type: "phase_boundary_check"
          description: "Verify work stays within assigned phases"
          requirement: "Modified files MUST belong to active track's phases"

        - type: "git_diff_validation"
          description: "Verify git changes match track scope"
          requirement: "git diff MUST only show files from active track"

      alternatives:
        - "Filter implementation state by active track"
        - "Validate module ownership before allowing changes"
        - "Add pre-commit hook checking track boundaries"
        - "Switch to correct track before making changes"

      evidence_template: |
        Track isolation violation detected!

        Active Track: {active_track}
        Modified Files: {modified_files}
        Violations: {violations}

        Files belong to: {actual_track}

        SKULL-009: Tracks MUST NOT cross-modify each other's work

      rationale: |
        SKULL-009: Track Work Isolation

        Core principle: Each track is an isolated development context.

        Why Isolation Matters:

        1. Prevents Merge Conflicts:
           - Two machines editing same file → disaster
           - Track A changes conflicting with Track B changes
           - Consolidation becomes manual merge nightmare
           Example: Both tracks fix same module differently

        2. Maintains Race Integrity:
           - Track A can't "cheat" by doing Track B's work
           - Progress metrics stay meaningful
           - Velocity calculations remain accurate
           Example: Track A does Track B's modules → unfair race

        3. Enables True Parallel Development:
           - No coordination needed during work
           - No "wait for Track A to finish" scenarios
           - Maximum throughput achieved
           Example: Both machines working simultaneously without blocking

        4. Simplifies Context Management:
           - Each machine sees only relevant modules
           - Copilot context smaller and focused
           - Fewer tokens, faster responses
           Example: Track A context excludes Track B's 50 modules

        Enforcement Mechanism:

        1. Pre-Modification Check:
           ```python
           def validate_module_ownership(module_id, active_track):
               if module_id not in active_track.modules:
                   raise TrackIsolationError(
                       f"Module {module_id} belongs to different track"
                   )
           ```

        2. Git Pre-Commit Hook:
           ```bash
           # Check if modified files belong to active track
           active_track=$(get_active_track)
           for file in $(git diff --cached --name-only); do
               if ! track_owns_file "$active_track" "$file"; then
                   echo "Error: $file not in active track"
                   exit 1
               fi
           done
           ```

        3. Design Sync Validation:
           - Compare git log with track assignments
           - Flag any cross-track modifications
           - Require explicit override with justification

        Allowed Cross-Track Work:
        - Shared files (cortex.config.json)
        - Documentation updates (README.md)
        - Test fixtures (tests/fixtures/)

        Not Allowed:
        - Modifying other track's modules
        - Changing other track's phase files
        - Updating other track's status in design doc

        Override Process:
        If cross-track work truly needed:
        1. Document why isolation must break
        2. Get explicit user approval
        3. Log violation for consolidation review
        4. Merge carefully during consolidation

        Integration Test:
        ```python
        def test_track_isolation():
            # Setup two tracks
            config = setup_multi_track(['AHHOME', 'Mac'])
            track_a = config.tracks['track_1']
            track_b = config.tracks['track_2']

            # Simulate Track A trying to modify Track B's module
            with pytest.raises(TrackIsolationError):
                modify_module(track_b.modules[0], active_track=track_a)

            # Verify Track A can modify own modules
            modify_module(track_a.modules[0], active_track=track_a)  # OK
        ```

    - rule_id: "SKULL_CONSOLIDATION_INTEGRITY"
      name: "Track Consolidation Integrity (SKULL-010)"
      severity: "blocked"
      description: "Consolidation MUST merge all track progress accurately without data loss"

      detection:
        keywords:
          - "consolidate tracks"
          - "merge tracks"
          - "reset to single-track"
          - "design sync consolidation"
        scope: ["intent", "operation_name"]

      verification_required:
        - type: "progress_preservation_check"
          description: "Verify no completed modules lost in merge"
          requirement: "Consolidated count MUST equal sum of track counts"

        - type: "conflict_resolution_audit"
          description: "Log all conflict resolutions with justification"
          requirement: "Conflicts MUST be documented in archive"

        - type: "archive_completeness_check"
          description: "Verify split docs archived before deletion"
          requirement: "All split docs MUST exist in archive before removal"

        - type: "git_commit_validation"
          description: "Verify consolidation tracked in git history"
          requirement: "Git commit MUST reference both tracks and merge details"

      alternatives:
        - "Run consolidation with --verify flag"
        - "Review conflict resolution log before committing"
        - "Keep split docs until archive verified"
        - "Add integration test for consolidation accuracy"

      evidence_template: |
        Consolidation integrity check failed!

        Pre-Consolidation:
        - Track A: {track_a_completed}/{track_a_total} modules
        - Track B: {track_b_completed}/{track_b_total} modules
        - Total: {pre_total_completed} modules

        Post-Consolidation:
        - Unified: {post_total_completed} modules

        Discrepancy: {discrepancy} modules
        Conflicts Resolved: {conflicts}
        Archive Status: {archive_status}

        SKULL-010: Consolidation MUST preserve all progress

      rationale: |
        SKULL-010: Track Consolidation Integrity

        Consolidation is the critical merge operation - must be perfect.

        What Can Go Wrong:

        1. Progress Loss:
           - Track A shows module complete
           - Consolidation misses it
           - User loses work (demoralizing)
           Example: Track A completed 15 modules, only 12 appear in merge

        2. Conflict Mishandling:
           - Both tracks modified same module
           - Wrong version selected
           - Work overwritten silently
           Example: Track A's fix lost, Track B's bug remains

        3. Archive Failure:
           - Split docs deleted before archiving
           - No way to audit merge decisions
           - Can't roll back if issues found
           Example: User wants to see what Track A had, archive empty

        4. Git History Gaps:
           - Consolidation not committed properly
           - Can't trace what was merged when
           - Audit trail incomplete
           Example: Merge happened, git log says nothing

        Consolidation Algorithm:

        ```python
        def consolidate_tracks(track_config, impl_state):
            # Step 1: Collect all track progress
            all_modules = {}
            for track in track_config.tracks.values():
                for module_id in track.modules:
                    status = get_module_status(module_id, impl_state)

                    # Conflict detection
                    if module_id in all_modules:
                        conflict = resolve_conflict(
                            all_modules[module_id],
                            status,
                            strategy='latest_timestamp'
                        )
                        log_conflict_resolution(module_id, conflict)
                        all_modules[module_id] = conflict.winner
                    else:
                        all_modules[module_id] = status

            # Step 2: Validate counts
            pre_count = sum(t.metrics.modules_completed for t in track_config.tracks.values())
            post_count = sum(1 for s in all_modules.values() if s.completed)

            if pre_count != post_count:
                raise ConsolidationError(
                    f"Progress mismatch: {pre_count} → {post_count}"
                )

            # Step 3: Archive split docs
            archive_dir = create_archive_directory()
            for status_file in get_split_design_docs():
                archive_file(status_file, archive_dir)

            # Step 4: Generate consolidated doc
            consolidated = generate_consolidated_document(
                all_modules,
                track_config,
                archive_reference=archive_dir
            )

            # Step 5: Git commit with full details
            commit_message = f"""design: consolidate multi-track progress

            Tracks merged:
            - {track_config.tracks['track_1'].track_name}: {track_config.tracks['track_1'].metrics.completion_percentage}%
            - {track_config.tracks['track_2'].track_name}: {track_config.tracks['track_2'].metrics.completion_percentage}%

            Total progress: {post_count}/{len(all_modules)} modules ({post_count/len(all_modules)*100:.0f}%)
            Conflicts resolved: {len(get_conflicts())}
            Archive: {archive_dir.name}

            [design_sync consolidation]
            """

            git_commit(consolidated, commit_message)

            return consolidated
        ```

        Conflict Resolution Strategy:

        Default: Latest Timestamp Wins
        - Simple, deterministic, predictable
        - Assumes most recent work is correct
        - Logged for audit

        Example:
        ```
        Module: platform_detection
        - Track A: marked complete 2025-11-11 14:00
        - Track B: marked complete 2025-11-11 15:00
        Winner: Track B (later timestamp)
        Logged: conflict-resolution.yaml
        ```

        Archive Structure:
        ```
        cortex-brain/archived-tracks/20251111-164530/
        ├── CORTEX2-STATUS-SPLIT.MD       # Original split doc
        ├── track-1-history.jsonl         # Track A progress log
        ├── track-2-history.jsonl         # Track B progress log
        ├── conflicts-resolved.yaml       # Conflict resolution log
        └── consolidation-report.md       # Summary of merge
        ```

        Integration Test:
        ```python
        def test_consolidation_integrity():
            # Setup: Two tracks with overlapping work
            config = create_multi_track(['AHHOME', 'Mac'])
            track_a_complete = mark_modules_complete(config.tracks['track_1'], [0, 1, 2])
            track_b_complete = mark_modules_complete(config.tracks['track_2'], [3, 4, 5])

            # Introduce conflict: both complete module 2
            mark_complete(config.tracks['track_1'], 'module_2', timestamp='14:00')
            mark_complete(config.tracks['track_2'], 'module_2', timestamp='15:00')

            # Consolidate
            consolidated = consolidate_tracks(config, impl_state)

            # Verify counts
            assert consolidated.modules_completed == 6, "Progress lost"

            # Verify conflict handled
            conflicts = get_conflict_log()
            assert 'module_2' in conflicts, "Conflict not logged"
            assert conflicts['module_2']['winner'] == 'track_2', "Wrong winner"

            # Verify archive
            archive = get_latest_archive()
            assert archive.exists(), "Archive missing"
            assert (archive / 'CORTEX2-STATUS-SPLIT.MD').exists(), "Split doc not archived"

            # Verify git
            commit = get_latest_commit()
            assert 'consolidate multi-track' in commit.message
            assert 'track_1' in commit.message
            assert 'track_2' in commit.message
        ```

        User Experience:
        ```
        $ /CORTEX design sync

        🏁 Multi-Track Mode: Running design sync consolidation
           Will merge all tracks into unified status

        [Phase 1/6] Discovering live implementation state...
        ✅ Track A (Blazing Phoenix): 8/15 modules (53%)
        ✅ Track B (Swift Falcon): 12/18 modules (67%)

        [Phase 5/6] Consolidating tracks...
        ⚙️  Merging progress from 2 tracks...
        ⚠️  Conflict detected: platform_detection
            Track A: complete @ 14:00
            Track B: complete @ 15:00
            Resolution: Track B wins (latest timestamp)

        ✅ Consolidated 2 tracks into unified document
           Combined: 20/33 modules (61%)
           Conflicts resolved: 1 (logged)
           Archive: cortex-brain/archived-tracks/20251111-164530/

        [Phase 6/6] Committing changes...
        💾 Git commit: 7a3b9c2 "design: consolidate multi-track progress"

        Design Sync ✅ COMPLETED in 4.2s
           • Merged 2 tracks: Blazing Phoenix (53%) + Swift Falcon (67%)
           • Combined progress: 20/33 modules (61%)
           • Conflicts resolved: 1
           • Archived split docs
           • Reset to single-track mode
        ```

# Layer 6: Knowledge Quality
- layer_id: "knowledge_quality"
  name: "Knowledge Quality"
  description: "Pattern validation and confidence thresholds"
  priority: 6

  rules:
    - rule_id: "MIN_OCCURRENCES"
      name: "Minimum Occurrences for High Confidence"
      severity: "warning"
      description: "High confidence (>0.50) with single occurrence"

      detection:
        combined_keywords:
          high_confidence:
            - "confidence: 1.0"
            - "confidence=1.0"
            - "confidence: 0.95"
          single_event:
            - "first occurrence"
            - "single event"
            - "occurrences: 1"
        scope: ["description"]
        logic: "AND"  # Both conditions must be true

      alternatives:
        - "Start with confidence ≤0.50 for single event"
        - "Wait for 3+ occurrences before high confidence"
        - "Mark as provisional pattern"

      evidence: "Require 3+ occurrences for confidence >0.50"

    - rule_id: "PATTERN_VALIDATION"
      name: "Pattern Validation"
      severity: "warning"
      description: "Pattern lacks validation evidence"

      detection:
        keywords:
          - "add pattern without validation"
          - "no evidence"
          - "unverified pattern"
        scope: ["description"]

      alternatives:
        - "Add validation test"
        - "Link to source documentation"
        - "Mark as hypothesis for validation"

      evidence: "Patterns require empirical validation"

# Layer 7: Commit Integrity
- layer_id: "commit_integrity"
  name: "Commit Integrity"
  description: "Brain state files excluded from commits"
  priority: 7

  rules:
    - rule_id: "BRAIN_STATE_GITIGNORE"
      name: "Brain State Files Not Committed"
      severity: "warning"
      description: "Brain state file should not be committed"

      detection:
        files: "{{brain_state_files}}"
        keywords:
          - "commit"
        scope: ["intent"]

      alternatives:
        - "Add to .gitignore"
        - "Keep local-only"
        - "Export as snapshot if needed for sharing"

      evidence: "Add to .gitignore to prevent pollution"

    - rule_id: "TEMP_FILES_COMMIT"
      name: "Temporary Files Not Committed"
      severity: "warning"
      description: "Temporary or generated files should not be committed"

      detection:
        path_patterns:
          - "**/*.tmp"
          - "**/temp_*"
          - "**/__pycache__/**"
          - "**/node_modules/**"
        keywords:
          - "commit"
        scope: ["intent"]

      alternatives:
        - "Update .gitignore"
        - "Clean before commit"
        - "Use .gitkeep for empty directories"

      evidence: "Temporary files pollute repository"

# Layer 8: Git Isolation (CRITICAL)
- layer_id: "git_isolation"
  name: "Git Isolation Enforcement"
  description: "CORTEX code MUST NEVER be committed to user application repositories"
  priority: 8

  rules:
    - rule_id: "GIT_ISOLATION_ENFORCEMENT"
      name: "CORTEX Code Isolation from User Repos"
      severity: "blocked"
      description: "CRITICAL: CORTEX source code, brain files, or internal components being committed to user application repository"

      detection:
        path_patterns:
          - "**/src/tier0/**"
          - "**/src/tier1/**"
          - "**/src/tier2/**"
          - "**/src/tier3/**"
          - "**/src/cortex_agents/**"
          - "**/src/plugins/**"
          - "**/src/crawlers/**"
          - "**/cortex-brain/**"
          - "**/prompts/**"
          - "**/scripts/cortex/**"
          - "**/CORTEX/**"
        in_repo: "user_application"  # Detection: not in CORTEX repo

      alternatives:
        - "Keep CORTEX as separate repository/package"
        - "Install CORTEX via pip/npm (when distributed)"
        - "Use git submodule if local development required"
        - "Ensure .gitignore excludes CORTEX directories"

      evidence_template: |
        🚨 CRITICAL VIOLATION: Git Isolation Breach

        CORTEX code detected in user application repository!
        File: '{path}'

        CORTEX MUST remain isolated from user application code:
        - User App Repo: Application-specific code only
        - CORTEX Repo: Framework code (separate repository)
        - Knowledge Sharing: Via exported YAML (team-knowledge/)

        Brain knowledge (cortex-brain/) is LOCAL ONLY - never committed anywhere.

      rationale: |
        GIT_ISOLATION_ENFORCEMENT: Core CORTEX Principle

        CORTEX operates as a SEPARATE cognitive layer:

        ❌ NEVER DO THIS:
        UserApp/
        ├── src/                    # User's application code
        ├── cortex-brain/           # ❌ WRONG - Don't commit brain!
        ├── src/tier0/              # ❌ WRONG - Don't copy CORTEX code!
        ├── src/cortex_agents/      # ❌ WRONG - Keep CORTEX separate!
        └── .git/

        ✅ CORRECT SETUP:
        UserApp/
        ├── src/                    # User's application code
        ├── team-knowledge/         # ✅ OK - Exported YAML patterns
        ├── .gitignore              # ✅ Must include: cortex-brain/
        └── .git/

        CORTEX/ (separate repo)
        ├── src/tier0/              # ✅ CORTEX framework code
        ├── src/cortex_agents/      # ✅ Agent system
        ├── cortex-brain/           # ✅ Local brain (not in git)
        └── .git/

        Why This Matters:
        1. Separation of Concerns: Framework vs. Application
        2. Licensing: CORTEX proprietary, user code their own license
        3. Updates: CORTEX updates don't pollute user repos
        4. Security: Brain knowledge stays local, never exposed
        5. Clarity: Clear boundary between "your code" and "framework"

        Git Hooks (setup during init):
        - pre-commit: Scans for CORTEX paths, blocks commit if found
        - pre-push: Double-check no CORTEX code being pushed

        Exception: team-knowledge/ YAML exports allowed (knowledge sharing)

    - rule_id: "GIT_HOOKS_INSTALLATION"
      name: "Git Hooks Must Be Installed During Setup"
      severity: "blocked"
      description: "Setup process must install git hooks to prevent accidental CORTEX code commits"

      detection:
        keywords:
          - "skip git hooks"
          - "disable hooks"
          - "bypass hook installation"
        scope: ["intent", "description"]

      alternatives:
        - "Run 'cortex init' to install hooks automatically"
        - "Manually run setup script with hooks enabled"
        - "Never bypass hook installation (critical protection)"

      evidence_template: "Git hooks are MANDATORY for CORTEX isolation protection"

      rationale: |
        Git hooks provide automatic enforcement:

        pre-commit hook:
        - Scans staged files for CORTEX paths
        - Blocks commit if any CORTEX code detected
        - Shows clear error message with alternatives

        pre-push hook:
        - Final safety check before push
        - Prevents accidental exposure of CORTEX code

        Installation: Automatic during 'cortex init'
        Location: UserApp/.git/hooks/ (user's repo, not CORTEX repo)
