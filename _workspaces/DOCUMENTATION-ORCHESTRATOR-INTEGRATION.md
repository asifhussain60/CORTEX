# CORTEX Documentation Integration Guide
**Version:** 5.0 | **Target:** MasterOrchestrator Integration | **Status:** ✅ READY

---

## 🔗 Integration with CORTEX Master System

The new one-shot documentation generation system (`cortex-doc-v5.prompt.md`) integrates seamlessly with CORTEX governance:

---

## 📋 Intent Classification Integration

When user invokes `/doc-fresh-generate`:

### Step 1: CORTEX LENS Processing
```python
# From CORTEX.prompt.md Stage 1-2
intent_classification = {
    "intent": "DOCUMENT - FRESH GENERATION",
    "handler": "DocumentationOrchestrator",
    "confidence": "🟢 High (95%)",
    "scope": "SYSTEM",
    "impact": "🔴 High (Regenerates docs/)",
    "entities": ["docs/", "_workspaces/reports/"],
    "rules": ["CORE-012", "CORE-027", "CORE-026"],
    "workflow": "7-Phase pipeline (end-to-end)"
}
```

### Step 2: DoR Approval Gate
```
Display classification ✅
Wait for: "proceed" or "yes" ✅
Execute ALL phases automatically ✅
```

### Step 3: Enforcement Orchestrator
```python
# From CORTEX.prompt.md Stage 3
enforcement_checks = {
    "GovernanceEnforcementAgent": {
        "CORE-012": "✅ PASSED (docstrings generated)",
        "CORE-029": "✅ PASSED (response header enforced)",
    },
    "SecurityCheckpointAgent": {
        "CORE-026": "✅ PASSED (git checkpoint created)",
        "CORE-027": "✅ PASSED (audit trail logged)",
    },
    "ComplianceValidationAgent": {
        "TIER-1": "✅ PASSED (phase readiness verified)"
    }
}
# Result: PASS → Proceed to execution
```

### Step 4: Execute with Governance
```python
# From CORTEX.prompt.md Stage 4-5
ac_log_start = {
    "timestamp": "2026-01-25 10:30:00",
    "operation_id": "doc-fresh-generate-001",
    "ac_id": "AC_DOC_FRESH_001",
    "phase": "Documentation",
    "orchestrator": "DocumentationOrchestrator"
}

# Execute phases 1-7...

ac_log_complete = {
    "timestamp": "2026-01-25 10:42:00",
    "operation_id": "doc-fresh-generate-001",
    "ac_id": "AC_DOC_FRESH_001",
    "result": "✅ SUCCESS",
    "files_generated": 26,
    "diagrams_created": 10,
    "duration_minutes": 12
}
```

---

## 🧠 MasterOrchestrator Wiring

### Current Status
The DocumentationOrchestrator needs to be wired into MasterOrchestrator:

```python
# cortex/orchestrators/core/master_orchestrator.py

class MasterOrchestrator:
    """Main orchestrator coordinating all operations."""
    
    def initialize(self):
        """Wire all orchestrators."""
        # Currently wired (3/23):
        self.planning = PlanningOrchestrator()
        self.refactoring = RefactoringOrchestrator()
        # ... more
        
        # NEEDED: Wire DocumentationOrchestrator
        self.documentation = DocumentationOrchestrator()  # <- ADD THIS
    
    async def handle_command(self, command: str):
        """Route command to appropriate orchestrator."""
        
        # NEEDED: Add routing for doc-fresh-generate
        if command == "/doc-fresh-generate":
            return await self.documentation.fresh_generate()
        
        # ... other commands
```

### Orchestrator Implementation Template

```python
# cortex/orchestrators/documentation/documentation_orchestrator.py

from cortex.brain.core.governance_registry import GovernanceRegistry
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger

class DocumentationOrchestrator(BaseOrchestrator):
    """Fresh documentation generation orchestrator."""
    
    def __init__(self):
        super().__init__()
        self.governance = GovernanceRegistry()
        self.logger = EnhancedAuditLogger("DocumentationOrchestrator")
    
    async def fresh_generate(self) -> Result:
        """Execute 7-phase fresh generation pipeline."""
        
        # AC_START
        ac_id = self.logger.log_operation_start(
            "doc_fresh_generate",
            phase="Documentation"
        )
        
        try:
            # Phase 1: PRE-CLEANUP
            await self._phase_1_precleanup()
            
            # Phase 2: DISCOVERY
            inventory = await self._phase_2_discovery()
            
            # Phase 3: GENERATION
            docs = await self._phase_3_generation(inventory)
            
            # Phase 4: DIAGRAMS
            diagrams = await self._phase_4_diagrams(inventory)
            
            # Phase 5: BUILD
            build_result = await self._phase_5_build()
            if build_result.is_err():
                return build_result
            
            # Phase 6: VALIDATION
            validation = await self._phase_6_validation()
            if validation.is_err():
                return validation
            
            # Phase 7: REPORTING
            report = await self._phase_7_reporting()
            
            # AC_COMPLETE
            self.logger.log_operation_complete(
                ac_id,
                {
                    "files_generated": len(docs),
                    "diagrams_created": len(diagrams),
                    "status": "success"
                }
            )
            
            return Ok({
                "docs": docs,
                "diagrams": diagrams,
                "report": report
            })
        
        except Exception as e:
            self.logger.log_operation_error(ac_id, str(e))
            return Err(f"Documentation generation failed: {e}")
    
    async def _phase_1_precleanup(self):
        """Delete old docs, preserve infrastructure."""
        pass
    
    async def _phase_2_discovery(self):
        """Scan codebase for components."""
        pass
    
    async def _phase_3_generation(self, inventory):
        """Generate markdown files."""
        pass
    
    async def _phase_4_diagrams(self, inventory):
        """Generate Mermaid + D3.js diagrams."""
        pass
    
    async def _phase_5_build(self):
        """Build mkdocs with --strict."""
        pass
    
    async def _phase_6_validation(self):
        """Validate all links."""
        pass
    
    async def _phase_7_reporting(self):
        """Generate report and commit."""
        pass
    
    def get_mcp_tools(self) -> List[str]:
        """Export MCP tools for discovery."""
        return [
            "documentation_generate",
            "documentation_validate",
            "diagram_generate"
        ]
```

---

## 🎼 Orchestrator Registration

### In orchestrator registry:
```python
# cortex/orchestrators/__init__.py

from cortex.orchestrators.documentation.documentation_orchestrator import (
    DocumentationOrchestrator
)

ORCHESTRATORS = {
    "documentation": DocumentationOrchestrator,
    # ... others
}
```

### In MasterOrchestrator initialization:
```python
# cortex/orchestrators/core/master_orchestrator.py

async def initialize(self):
    """Initialize all orchestrators."""
    
    for name, OrchestratorClass in ORCHESTRATORS.items():
        orchestrator = OrchestratorClass()
        setattr(self, name, orchestrator)
        
        # Expose MCP tools from each orchestrator
        if hasattr(orchestrator, 'get_mcp_tools'):
            tools = orchestrator.get_mcp_tools()
            self.mcp_registry.register_tools(name, tools)
```

---

## 🔧 MCP Tool Registration

### Tool Definitions

```yaml
# cortex/mcp/tools/documentation_tools.yaml

tools:
  
  - id: "doc_fresh_generate"
    name: "Fresh Documentation Generation"
    description: "Execute one-shot fresh documentation generation pipeline"
    category: "documentation"
    entry_point: "DocumentationOrchestrator.fresh_generate"
    parameters:
      none
    returns:
      - docs: List[str]
      - diagrams: List[str]
      - report: str
    requires_approval: true
    workflow: "7-phase end-to-end"
  
  - id: "doc_validate"
    name: "Documentation Validation"
    description: "Validate generated documentation links and references"
    category: "documentation"
    entry_point: "DocumentationOrchestrator.validate"
    parameters:
      - path: "docs/"
    requires_approval: false
```

---

## 📊 Integration Checklist

### Code Changes Needed

- [ ] Create `cortex/orchestrators/documentation/`
- [ ] Implement `DocumentationOrchestrator` class
- [ ] Implement 7 phase methods
- [ ] Add to orchestrator registry
- [ ] Wire into `MasterOrchestrator.initialize()`
- [ ] Create MCP tool definitions
- [ ] Register MCP tools in MCP registry
- [ ] Add audit logging (AC_START/COMPLETE)
- [ ] Add governance checks (CORE-012, 027, 026, 029)

### Testing

- [ ] Unit tests for each phase
- [ ] Integration test for full pipeline
- [ ] Test serve script preservation
- [ ] Test build validation
- [ ] Test link validation
- [ ] Test report generation
- [ ] Test git commit

### Documentation

- [ ] Update orchestrator catalog
- [ ] Add to API reference
- [ ] Add to MCP tools reference
- [ ] Update architecture docs
- [ ] Add usage examples

---

## 🚀 Deployment Steps

### Step 1: Implement DocumentationOrchestrator
```bash
# Create implementation
cp cortex-doc-v5.prompt.md \
   cortex/orchestrators/documentation/documentation_orchestrator.py
```

### Step 2: Wire to MasterOrchestrator
```python
# Update MasterOrchestrator.initialize()
self.documentation = DocumentationOrchestrator()
```

### Step 3: Register MCP Tools
```python
# Register in MCP tool registry
registry.register_tool("doc_fresh_generate", "documentation")
```

### Step 4: Test
```bash
pytest tests/orchestrators/documentation/ -v
```

### Step 5: Deploy
```bash
git commit -m "feat: fresh documentation generation orchestrator

- Implement DocumentationOrchestrator with 7-phase pipeline
- Wire to MasterOrchestrator
- Register MCP tools
- Add governance compliance (CORE-012, 027, 026, 029)
- Automatic end-to-end execution without stopping"
```

---

## 📈 Success Metrics

After integration is complete:

| Metric | Target | Status |
|--------|--------|--------|
| Command works | `/doc-fresh-generate` | Deploy when ready |
| Approval gate | Single "proceed" | ✅ Specified |
| Phases execute | All 7 end-to-end | ✅ Specified |
| Files generated | 16+ markdown | ✅ Specified |
| Diagrams created | 10 (6 Mermaid + 4 D3.js) | ✅ Specified |
| Build status | Zero warnings/errors | ✅ Specified |
| Link validation | 100% valid | ✅ Specified |
| Serve scripts | Preserved | ✅ Specified |
| Report generated | YAML summary | ✅ Specified |
| Git commit created | With summary | ✅ Specified |

---

## 🎯 Relationship to cortex-impl-map.yaml

This DocumentationOrchestrator is a **high-value orchestrator** that should be prioritized for integration:

```yaml
# Entry in cortex-impl-map.yaml

orchestrators:
  - name: DocumentationOrchestrator
    status: "READY FOR IMPLEMENTATION"
    effort: "20 hours"
    priority: "HIGH"
    reason: "One-shot documentation generation with zero-interaction model"
    dependencies: []
    delivers:
      - Fresh documentation generation
      - Automatic diagram creation
      - Build validation
      - Link validation
      - Governance compliance
    references:
      - Prompt: "cortex-doc-v5.prompt.md"
      - Transformation: "_workspaces/DOCUMENTATION-PROMPT-TRANSFORMATION-v5.md"
      - QuickStart: "_workspaces/DOCUMENTATION-FRESH-GENERATION-QUICK-START.md"
```

---

## ✅ Status

**Integration Guide:** ✅ COMPLETE

**Ready for Implementation:**
- ✅ Prompt specification complete (`cortex-doc-v5.prompt.md`)
- ✅ 7-phase pipeline defined
- ✅ MCP tool definitions ready
- ✅ Governance compliance specified
- ✅ Testing checklist provided
- ✅ Deployment steps documented

**Next:** Implement in Phase 1 of CORTEX transformation roadmap

---
