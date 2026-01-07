# Source Plan Reference

**Implementation Based On:** `autonomous-orchestrator-v5/00-MASTER-PLAN-V5.md`

## Source Plan Details

- **Plan Name:** Autonomous Orchestrator v5.0 - Pure Autonomous Architecture
- **Strategy:** Option 1 - Machine-Readable Config + Python Ownership
- **Created:** January 2, 2026
- **Status:** Architecture defined, ready for implementation

## Key Architectural Decisions from Source

### 1. Pure Autonomous Architecture
- Python orchestrator owns ALL execution logic
- Manifests contain ONLY data structures (YAML/JSON)
- Zero natural language instructions in configuration
- CORTEX acts as thin client (route → invoke → display)

### 2. Database State Management
- SQLite database for transactional state
- ACID transactions for atomic phases
- Single source of truth for plan status
- Recovery from failures at any point

### 3. Config-Driven Behavior
- YAML defines folder templates, validation schemas, output formats
- Jinja2 templates for all output generation
- Config schema versioning
- Validation on config load

### 4. MCP Tool Integration
- Universal `invoke_orchestrator()` MCP tool
- Registry maps orchestrator names to Python classes
- Parameters: `orchestrator_name`, `user_request`
- Returns execution summary for CORTEX display

### 5. Hand-Off Protocol
- CORTEX.prompt.md detects intent
- Invokes MCP tool and STOPS
- Python orchestrator executes independently
- CORTEX displays summary using `autonomous_execution_progress` template

## Implementation Scope

This plan implements the architecture for all 4 AUTONOMOUS orchestrators:

1. **Planning System v5.0** - Context discovery, plan generation, folder creation
2. **ADO Operations v2.0** - Work item generation, acceptance criteria, estimation
3. **Vacuum v2.0** - Filesystem scanning, safe deletion, reorganization
4. **Cleanup v2.0** - Cache management, log rotation, bloat removal

## Custom Additions in This Implementation

### Filename Validation (20-Character Limit)
- **Requirement:** User specified monitoring filenames with ≤20 character limit
- **Implementation:** Phase 0, Task 0.1
- **Integration Points:**
  - BaseOrchestrator file creation methods
  - Database CHECK constraint
  - Pre-creation validation hooks
  - Post-creation audit scans
  - Auto-fix suggestions

### Monitoring Strategy
- Validate before file creation
- Audit after phase completion
- Weekly compliance reports
- Auto-shorten long filenames
- Database constraint enforcement

## Source Plan Files Referenced

- `autonomous-orchestrator-v5/00-MASTER-PLAN-V5.md` - Main plan
- `autonomous-orchestrator-v5/architecture/option-1-analysis.md` - Architecture analysis
- `autonomous-orchestrator-v5/architecture/database-schema.md` - Database design
- `autonomous-orchestrator-v5/architecture/config-specification.md` - Config format
- `autonomous-orchestrator-v5/README.md` - Plan overview

## Alignment Check

This implementation plan:
- ✅ Follows Pure Autonomous architecture (Option 1)
- ✅ Implements all 4 AUTONOMOUS orchestrators
- ✅ Uses SQLite for state management
- ✅ Removes natural language from manifests
- ✅ Integrates MCP tool protocol
- ✅ Updates CORTEX.prompt.md intent routing
- ✅ Adds custom filename validation (user requirement)
- ✅ Includes REFACTOR phase (SKULL rules)
- ✅ Requires TDD (tests before implementation)
- ✅ Uses `autonomous_execution_progress` response template

## Differences from Source

### Additional Features
1. **Filename Validation System** - Not in original plan, user requirement
   - 20-character limit enforcement
   - Auto-shortening algorithm
   - Compliance monitoring
   - Database constraints

### Enhanced Scope
- More detailed task breakdowns
- Specific file paths for all deliverables
- Integration points clearly mapped
- Validation criteria for each task

### Timeline Adjustment
- Source: ~27 days (estimated)
- This plan: 27 days (detailed with task hours)
- No change in overall duration

## Success Criteria Alignment

Both plans share identical success criteria:
- Zero ambiguity in execution flow
- Atomic phase operations with rollback
- Single source of truth (database)
- Deterministic output (templates + data)
- 100% test coverage
- Plans resumable from any phase

## Next Steps

1. Review this implementation plan
2. Confirm alignment with source architecture
3. Begin Phase 0: Foundation Setup
4. Create filename validation utility
5. Set up project structure
