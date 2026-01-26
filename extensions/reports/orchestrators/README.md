# Orchestrator Reports
**Purpose:** Orchestrator-specific reports and metrics  
**Authority:** AC-REPORTS-CONSOLIDATION-001

## Report Types
- Orchestrator health and status
- Registry wiring validation
- MCP tool integration status
- Orchestrator performance metrics
- Feature implementation tracking per orchestrator

## Naming Pattern
`{orchestrator}-{metric|aspect}-{date}.{md|yaml}`

**Examples:**
- `planning-orchestrator-v2-status.md`
- `tdd-orchestrator-test-coverage.yaml`
- `orchestrator-registry-wiring-status.md`
- `orchestrator-health-check-daily.yaml`
- `mcp-tools-availability-matrix.md`

## Format Guide
- Use **Markdown (.md)** for narrative status reports
- Use **YAML (.yaml)** for metrics and health checks

## Key Orchestrators
- PlanningOrchestrator
- TDDOrchestrator
- RefactoringOrchestrator
- MasterOrchestrator
- IntentRouter
- DocumentationOrchestrator
- (See cortex-impl-map.yaml for full list)

---

See `reports/README.md` for complete guidelines.
