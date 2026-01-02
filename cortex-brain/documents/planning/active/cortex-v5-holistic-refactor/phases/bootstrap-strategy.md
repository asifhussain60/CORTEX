# Bootstrap Strategy: Building Planning System v5

**Document Type:** Implementation Strategy  
**Plan:** CORTEX v5.0 Holistic Refactor  
**Created:** January 2, 2026

---

## 🎯 The Bootstrap Problem

**Challenge:** We need Planning System v5 to create high-quality plans for complex migrations, but Planning System v5 doesn't exist yet.

**Solution:** Use traditional planning approach to build Planning System v5, then immediately use v5 to plan all remaining migrations.

---

## 📐 Bootstrap Phases

### Phase 0: Foundation Setup (1 day)

**Goal:** Create project structure and establish naming standards

**Deliverables:**
- `src/mcp/` - MCP protocol layer skeleton
- `src/database/` - Database utilities and schema files
- `src/orchestrators/base_orchestrator_v4_1.py` - Base class stub
- `cortex-brain/database/` - Database storage location
- `tests/orchestrators/` - Test structure

**Key Decision:** Filename standardization (kebab-case vs snake_case)

### Phase 1: MCP Tool Infrastructure (2 days)

**Goal:** Create universal orchestrator invocation mechanism

**Deliverables:**
- `src/mcp/server.py` - MCP protocol server
- `src/mcp/tools/invoke_orchestrator.py` - Tool implementation
- `src/mcp/registry.py` - Orchestrator registry
- `cortex-brain/config/mcp-server.yaml` - Server configuration

**Integration Points:**
- CORTEX.prompt.md intent routing
- LLMIntentClassifier
- Response template system

**Testing:**
- Unit tests for registry
- Integration test: CORTEX → MCP → Orchestrator → Response
- Mock orchestrator for testing

### Phase 2: Planning State Database (1.5 days)

**Goal:** Implement single source of truth for plan state

**Deliverables:**
- `src/database/planning_state.py` - Database interface
- `cortex-brain/database/planning_state.db` - SQLite database
- `src/database/migrations/001_initial_schema.sql` - Schema definition
- `scripts/migrate_existing_plans.py` - Migration script

**Schema Tables:**
- plans
- phases
- tasks
- artifacts
- validations
- state_snapshots

**Testing:**
- Transaction rollback tests
- Snapshot creation/recovery tests
- Concurrent access tests

### Phase 3: BaseOrchestrator v4.1 (1.5 days)

**Goal:** Config-driven orchestrator foundation

**Deliverables:**
- `src/orchestrators/base_orchestrator_v4_1.py` - Base class implementation
- `src/utils/template_renderer.py` - Jinja2 rendering
- `src/utils/validator.py` - Validation checkpoint execution
- `templates/` - Template directory with base templates

**Core Methods:**
```python
class BaseOrchestratorV41:
    def load_config(self) -> dict
    def execute_phase(self, phase_config: dict)
    def validate_phase(self, phase_config: dict) -> bool
    def render_template(self, template: str, context: dict) -> str
    def record_progress(self, phase_id: str, progress: int)
    def create_snapshot(self, snapshot_type: str)
```

**Testing:**
- Mock orchestrator extends base class
- Config loading tests
- Template rendering tests
- Validation execution tests

### Phase 4: Planning Orchestrator v5 (2 days)

**Goal:** Pure Python planning implementation

**Deliverables:**
- `src/orchestrators/planning_orchestrator_v5.py` - Implementation
- `cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml` - Pure config manifest
- `templates/master-plan-v5.jinja2` - Master plan template
- `templates/discovery-summary.jinja2` - Context summary template
- `schemas/ast-structure.json` - AST validation schema

**Core Features:**
1. **Context Discovery** - workspace_search integration
2. **Architecture Analysis** - AST parsing
3. **Plan Generation** - Template-driven
4. **Folder Creation** - Atomic filesystem ops
5. **Progress Tracking** - Database updates
6. **Validation** - Automated checkpoints

**Testing:**
- End-to-end test: Create sample plan
- Phase execution tests
- Template rendering tests
- Validation tests

---

## 🔄 Transition Point

**When Phase 4 completes:**

```
cortex-v5-holistic-refactor/
├── 00-MASTER-PLAN-V5.md (this document)
├── architecture/ (design docs)
├── context/ (source plan analysis)
├── tracking/ (bootstrap progress)
└── future-structure/
    ├── src/
    │   ├── mcp/ ✅ Complete
    │   ├── database/ ✅ Complete
    │   └── orchestrators/
    │       ├── base_orchestrator_v4_1.py ✅ Complete
    │       └── planning_orchestrator_v5.py ✅ Complete
    ├── cortex-brain/
    │   ├── database/planning_state.db ✅ Complete
    │   └── manifests/orchestrators/
    │       └── planning-system-5.0-manifest.yaml ✅ Complete
    └── templates/ ✅ Complete
```

**At this point:**
- Planning System v5 is operational
- User can invoke: `/CORTEX Plan [feature]`
- System creates properly structured plans
- All plans use v5 folder structure

---

## 🚀 Post-Bootstrap: Using Planning System v5

### Phase 5: Use v5 to Plan Migrations (0.5 days)

**Commands to execute:**
```
/CORTEX Plan ADO Orchestrator v2 migration
/CORTEX Plan Vacuum Orchestrator v2 migration
/CORTEX Plan Cleanup Orchestrator v2 migration
/CORTEX Plan Agent layer MCP integration
/CORTEX Plan GUIDED orchestrator assessment
```

**Output:**
```
cortex-brain/documents/planning/active/
├── ado-orchestrator-v2-migration/
│   ├── 00-MASTER-PLAN-V5.md
│   ├── context/
│   ├── artifacts/
│   ├── reports/
│   └── tracking/
├── vacuum-orchestrator-v2-migration/
│   └── ... (same structure)
├── cleanup-orchestrator-v2-migration/
│   └── ... (same structure)
├── agent-mcp-integration/
│   └── ... (same structure)
└── guided-orchestrators-assessment/
    └── ... (same structure)
```

**Each plan will include:**
- ✅ Visual progress tracking
- ✅ Database-backed state management
- ✅ Proper folder structure
- ✅ Validation checkpoints
- ✅ Implementation artifacts in `future-structure/`

### Phase 6: Execute Migration Plans (24 days)

Execute each generated plan sequentially:

1. **ADO Orchestrator v2** (~3 days)
   - Strip manifest to config-only
   - Implement pure Python logic
   - Add database state management
   - Migrate to MCP tool invocation

2. **Vacuum Orchestrator v2** (~2.5 days)
   - Convert to config-driven
   - Implement file organization logic
   - Add rollback capability

3. **Cleanup Orchestrator v2** (~2 days)
   - Pure config manifest
   - Python-owned cache cleanup
   - Database tracking

4. **Agent MCP Integration** (~4 days)
   - Connect agents to MCP protocol
   - Unified invocation interface
   - Response template integration

5. **GUIDED Orchestrators Assessment** (~12.5 days)
   - Evaluate TDD, Debug, Refactor, Sanitization orchestrators
   - Determine which benefit from pure autonomous approach
   - Implement transformations where beneficial

---

## 📊 Progress Metrics

### Bootstrap Phase Success Criteria

✅ **Phase 0 Complete:**
- [ ] Project structure created
- [ ] Naming standards documented
- [ ] Test structure established

✅ **Phase 1 Complete:**
- [ ] MCP server operational
- [ ] invoke_orchestrator tool working
- [ ] Registry validates orchestrators
- [ ] Integration test passes

✅ **Phase 2 Complete:**
- [ ] Database schema created
- [ ] Transaction tests pass
- [ ] Snapshot recovery works
- [ ] Migration script tested

✅ **Phase 3 Complete:**
- [ ] BaseOrchestrator v4.1 implemented
- [ ] Config loading works
- [ ] Template rendering works
- [ ] Validation execution works
- [ ] Unit tests pass

✅ **Phase 4 Complete:**
- [ ] Planning Orchestrator v5 implemented
- [ ] Config-only manifest created
- [ ] Templates created
- [ ] End-to-end test passes
- [ ] Sample plan generated successfully

### Migration Phase Success Criteria

✅ **Phase 5 Complete:**
- [ ] 5 migration plans generated
- [ ] All plans have proper v5 structure
- [ ] All plans in database
- [ ] Validation checkpoints defined

✅ **Phase 6 Complete:**
- [ ] All AUTONOMOUS orchestrators migrated
- [ ] All agents integrated with MCP
- [ ] GUIDED orchestrators assessed
- [ ] 100% test coverage

---

## 🔧 Risk Mitigation

### Risk: Bootstrap Complexity

**Mitigation:** 
- Keep Phase 0-4 scope minimal
- Use existing Planning Orchestrator v4 as reference
- Incremental testing at each phase

### Risk: Template Quality

**Mitigation:**
- Reuse existing template structure
- Validate template output against examples
- User acceptance testing on first v5 plan

### Risk: Database Performance

**Mitigation:**
- SQLite is proven technology
- Index key columns
- Benchmark with 100 concurrent plans

### Risk: MCP Tool Integration Issues

**Mitigation:**
- Start with simple test orchestrator
- Mock external dependencies
- Comprehensive error handling

---

## 📚 Dependencies

**External:**
- SQLite 3.35+ (built into Python)
- Jinja2 3.1+ (already in requirements.txt)
- jsonschema 4.0+ (add to requirements.txt)

**Internal:**
- LLMIntentClassifier (existing)
- Response template system (existing)
- Workspace search APIs (existing)
- AST parsing utilities (existing)

---

## 🎯 Success Indicators

**We know bootstrap succeeded when:**
1. User runs `/CORTEX Plan test-feature`
2. Planning System v5 creates:
   - Proper folder structure (7 subfolders)
   - 00-MASTER-PLAN-V5.md with visual progress
   - Database record in planning_state.db
   - Context artifacts in context/
3. CORTEX displays autonomous_execution_progress template
4. No manual intervention required

**We know migration succeeded when:**
1. All 4 AUTONOMOUS orchestrators use MCP tool invocation
2. All manifests are config-only (no natural language)
3. All orchestrators use database state management
4. Test coverage ≥ 90%
5. Zero execution ambiguity (Python owns all logic)

---

## 📋 Rollback Plan

**If bootstrap fails:**
1. Revert to Planning Orchestrator v4
2. Use traditional planning for migrations
3. Analyze failure point
4. Redesign problematic component
5. Retry bootstrap

**If migration fails:**
1. Each orchestrator has independent rollback
2. Database snapshots allow point-in-time recovery
3. Archive failed implementation to `cortex-brain/archives/failed-migrations/`
4. Document lessons learned
5. Adjust approach based on failure analysis

---

## 🔗 References

- Main plan: `00-MASTER-PLAN-V5.md`
- Architecture principles: `architecture/pure-autonomous-principles.md`
- Database schema: `architecture/database-schema.md`
- Config specification: `architecture/config-specification.md`
- Source plan: `cortex-brain/documents/planning/active/autonomous-orchestrator-v5/00-MASTER-PLAN-V5.md`
