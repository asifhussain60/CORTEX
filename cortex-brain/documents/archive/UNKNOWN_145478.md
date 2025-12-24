        NAMESPACE-001: Protected CORTEX Namespace

        Critical architectural boundary preventing knowledge contamination.

        Why This Matters:
        1. Framework Integrity: CORTEX patterns must remain pure
        2. Multi-Project Support: Each workspace isolated
        3. Knowledge Quality: No user app patterns in framework brain
        4. Upgradability: CORTEX can update without breaking user data

        Protected Namespaces:
        - cortex.tier_architecture (4-tier brain system)
        - cortex.agent_patterns (10 specialist agents)
        - cortex.operations (universal operations)
        - cortex.plugins (plugin system)

        Allowed Namespaces:
        - workspace.<project>.* (your application patterns)
        - workspace.myapp.security (JWT, OAuth patterns)
        - workspace.myapp.architecture (file structure, tech stack)

        This rule is BLOCKING severity - violations stop execution immediately.

    - rule_id: "NAMESPACE-002"
      name: "Workspace Isolation"
      severity: "warning"
      description: "Isolate workspace patterns by owner/project"

      detection:
        combined_keywords:
          cross_workspace:
            - "workspace.projectA"
            - "workspace.projectB"
          shared_pattern:
            - "pattern applies to both"
            - "copy to other project"
        scope: ["intent", "description"]
        logic: "AND"

      alternatives:
        - "Store pattern in each workspace separately"
        - "Use cortex.* for truly generic framework patterns"
        - "Create explicit cross-workspace link if needed"

      evidence_template: |
        CROSS-WORKSPACE CONTAMINATION RISK

        Pattern appears to span multiple workspaces: '{description}'

        Best Practices:
        - workspace.projectA.* → Project A only
        - workspace.projectB.* → Project B only
        - cortex.* → Framework generic knowledge

        If truly shared, use explicit relationship links, not duplicate storage.

      rationale: |
        NAMESPACE-002: Workspace Isolation

        Each workspace (project) should have isolated knowledge.

        Benefits:
        1. Clean Separation: No cross-project contamination
        2. Parallel Development: Multiple projects on same machine
        3. Easier Cleanup: Delete workspace.projectA.* removes all traces
        4. Privacy: Project A can't see Project B patterns

        Example Structure:
        - workspace.ksessions.* → KSESSIONS project patterns
        - workspace.noor.* → NOOR Canvas project patterns
        - workspace.cortex.* → CORTEX development patterns (meta!)

        This rule is WARNING severity - allowed but discouraged.

    - rule_id: "NAMESPACE-003"
      name: "No Namespace Mixing"
      severity: "blocked"
      description: "Prevent patterns from spanning multiple namespaces"

      detection:
        combined_keywords:
          multi_namespace:
            - "namespaces=['cortex."
            - "namespaces=['workspace.a', 'workspace.b']"
          pattern_storage:
            - "store_pattern"
            - "learn_pattern"
        scope: ["code"]
        logic: "AND"

      alternatives:
        - "Store pattern in single primary namespace"
        - "Use relationship links for cross-namespace references"
        - "Duplicate pattern if truly applicable to both (rare)"

      evidence_template: |
        NAMESPACE MIXING VIOLATION

        Pattern assigned to multiple namespaces: '{namespaces}'

        A pattern MUST belong to exactly ONE namespace.

        If pattern applies to multiple contexts, use explicit links:
        - Primary: workspace.myapp.auth_pattern
        - Link: cortex.security_patterns → workspace.myapp.auth_pattern

        This maintains clear ownership and prevents ambiguity.

      rationale: |
        NAMESPACE-003: No Namespace Mixing

        Single Ownership Principle: Each pattern has ONE home.

        Why Single Namespace:
        1. Clear Ownership: No ambiguity about who maintains pattern
        2. Clean Deletion: Removing workspace.* removes all patterns
        3. No Orphans: Pattern lifecycle tied to single namespace
        4. Simpler Queries: No multi-namespace resolution logic

        Cross-Namespace References:
        Use relationship links instead of multi-namespace patterns:

        ❌ BAD:
        learn_pattern(
            ...,
            namespaces=["cortex.security", "workspace.myapp.security"]
        )

        ✅ GOOD:
        # Store in primary namespace
        pattern_id = learn_pattern(
            ...,
            namespaces=["workspace.myapp.security"]
        )

        # Link to generic pattern
        create_relationship(
            from_pattern="cortex.security_best_practices",
            to_pattern=pattern_id,
            relationship_type="implements"
        )

        This rule is BLOCKING severity - multi-namespace patterns rejected.

# Layer 9: Database Architecture Enforcement
- layer_id: "database_architecture"
  name: "Distributed Database Architecture"
  description: "CORTEX uses tier-specific databases, never monolithic cortex-brain.db"
  priority: 9

  rules:
    - rule_id: "DISTRIBUTED_DATABASE_ARCHITECTURE"
      name: "Use Tier-Specific Databases (Never Monolithic)"
      severity: "blocked"
      description: "Code referencing monolithic cortex-brain.db instead of tier-specific databases"

      detection:
        combined_keywords:
          monolithic_reference:
            - "cortex-brain/cortex-brain.db"
            - "cortex-brain.db"
            - 'db_path: str = "cortex-brain.db"'
            - "default='cortex-brain/cortex-brain.db'"
          not_test_file:
            - "!**/tests/**"
            - "!**/test-*.py"
            - "!**/benchmark-*.ts"
        scope: ["code", "file_path"]
        logic: "AND"

      alternatives:
        - "Tier 1 (Conversations): Use cortex-brain/tier1/conversations.db"
        - "Tier 1 (Working Memory): Use cortex-brain/tier1/working_memory.db"
        - "Tier 2 (Knowledge Graph): Use cortex-brain/tier2/knowledge_graph.db"
        - "Tier 3 (Context): Use cortex-brain/tier3/context.db"
        - "Use ConfigManager to get correct tier-specific path"

      evidence_template: |
        🚨 DATABASE ARCHITECTURE VIOLATION

        Monolithic database reference detected: '{path}'

        CORTEX uses distributed database architecture:
        ❌ WRONG: cortex-brain/cortex-brain.db (doesn't exist!)

        ✅ CORRECT:
        - Tier 1: cortex-brain/tier1/conversations.db (chat history)
        - Tier 1: cortex-brain/tier1/working_memory.db (active context)
        - Tier 2: cortex-brain/tier2/knowledge_graph.db (learned patterns)
        - Tier 3: cortex-brain/tier3/context.db (development metrics)

        File: {file}
        Line: {line}

      rationale: |
        DISTRIBUTED_DATABASE_ARCHITECTURE: Core CORTEX 2.0 Design

        CORTEX 2.0 migrated from monolithic to distributed database architecture.

        ❌ OLD (CORTEX 1.0):
        cortex-brain/
        └── cortex-brain.db  # Monolithic (conversations + knowledge + context)

        ✅ NEW (CORTEX 2.0):
        cortex-brain/
        ├── tier1/
        │   ├── conversations.db       # Last 20 conversations
        │   └── working_memory.db      # Active session context
        ├── tier2/
        │   └── knowledge_graph.db     # Learned patterns + capabilities
        └── tier3/
            └── context.db             # Git metrics + test coverage + health

        Why Distributed?

        1. Separation of Concerns:
           - Tier 1: Conversational data (fast, frequently accessed)
           - Tier 2: Strategic knowledge (periodic reads, rare writes)
           - Tier 3: Development context (external data sources)

        2. Performance:
           - Smaller databases = faster queries
           - No lock contention between tiers
           - Independent backup/restore per tier

        3. Scalability:
           - Each tier can scale independently
           - Can distribute across different storage
           - Clear upgrade paths per tier

        4. Maintainability:
           - Schema changes isolated to tier
           - Migrations simpler (per-tier)
           - Clear ownership boundaries

        Common Violations:

        1. Hardcoded Default Paths:
           ```python
           # ❌ WRONG
           def __init__(self, db_path: str = "cortex-brain.db"):
               pass

           # ✅ CORRECT
           def __init__(self, db_path: str = None):
               if db_path is None:
                   db_path = ConfigManager.get_tier1_conversations_path()
           ```

        2. Migration Scripts Still Using Old Path:
           ```python
           # ❌ WRONG
           parser.add_argument('--db-path', default='cortex-brain/cortex-brain.db')

           # ✅ CORRECT
           parser.add_argument('--tier', choices=['tier1', 'tier2', 'tier3'])
           db_path = get_tier_database_path(args.tier)
           ```

        3. Documentation References:
           ```markdown
           ❌ WRONG: "Creates cortex-brain.db in KSESSIONS"
           ✅ CORRECT: "Creates tier-specific databases: tier1/conversations.db, tier2/knowledge_graph.db, tier3/context.db"
           ```

        Files Commonly Affected:
        - src/router.py (routing logic)
        - src/context_injector.py (context management)
        - src/brain/tier1/request_logger.py (conversation logging)
        - src/brain/tier1/tier1_api.py (Tier 1 API)
        - src/brain/tier1/__init__.py (Tier 1 initialization)
        - scripts/cortex/migrate-*.py (migration scripts)

        How to Fix:

        1. Identify which tier the code needs:
           - Conversations/history → Tier 1 (conversations.db)
           - Working memory/session → Tier 1 (working_memory.db)
           - Patterns/capabilities → Tier 2 (knowledge_graph.db)
           - Git/tests/health → Tier 3 (context.db)

        2. Use ConfigManager for paths:
           ```python
           from src.config import ConfigManager

           config = ConfigManager()
           conversations_db = config.get_tier1_conversations_path()
           knowledge_db = config.get_tier2_knowledge_path()
           context_db = config.get_tier3_context_path()
           ```

        3. Update tests to use tier-specific paths:
           ```python
           # Test fixtures should mirror production structure
           @pytest.fixture
           def tier1_db(tmp_path):
               return tmp_path / "tier1" / "conversations.db"
           ```

        4. Update documentation references:
           - README.md
           - Architecture docs
           - Setup guides
           - Migration instructions

        Exception: Test Files
        - Test files (tests/**, test-*.py, benchmark-*.ts) can use custom paths
        - Use clear naming: test-cortex-brain.db (not cortex-brain.db)

        Integration Test Required:
        ```python
        def test_no_monolithic_references():
            """Ensure no production code references cortex-brain.db"""
            violations = []

            for file in Path('src').rglob('*.py'):
                content = file.read_text()
                if 'cortex-brain.db' in content:
                    violations.append(str(file))

            assert not violations, (
                f"Monolithic DB references found: {violations}\n"
                f"Use tier-specific paths instead!"
            )
        ```

        Optimize Operation Validation:
        The optimize_cortex_orchestrator should validate:
        - ✅ All tier databases exist
        - ✅ No references to cortex-brain.db in src/
        - ✅ ConfigManager returns correct paths
        - ✅ Migration scripts use tier-specific args
        - ✅ Documentation reflects distributed architecture
