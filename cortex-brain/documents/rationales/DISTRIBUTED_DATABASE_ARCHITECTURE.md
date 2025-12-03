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
