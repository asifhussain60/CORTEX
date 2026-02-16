# ============================================================================
# PHASE 100 INTEGRATION: Workflow Template Auto-Selection
# ============================================================================
# Authority: Phase 100 Stage 1 + CORE-019 (MasterOrchestrator routing)
# Purpose: Extends IntentRouter + MasterOrchestrator to auto-select workflow
#          templates based on user request analysis (Vision API integration)
# ============================================================================

## 📊 INTEGRATION ARCHITECTURE

### END-TO-END FLOW: Screenshot → Template → Execution

```
┌───────────────────────────────────────────────────────────────────────────┐
│ USER REQUEST (VS Code Copilot Chat)                                       │
│ "Fix the black box, move 'Manage' section left"                          │
│ + Screenshot attached (hero-section.png)                                  │
└────────────────────────────┬──────────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────────────────┐
│ STAGE 1: MCP Gateway (Entry Point)                                         │
│ • Receives request via cortex_process_request MCP tool                     │
│ • Extracts attachments (screenshot, context files)                         │
│ • Routes to MasterOrchestrator.execute_operation()                         │
└────────────────────────────┬───────────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────────────────┐
│ STAGE 2: IntentRouter Classification (MANDATORY - CORE-019)                │
│ • Classifies intent: FIX + REFACTOR (composite intent)                     │
│ • Detects visual change request (screenshot present)                       │
│ • Confidence: 0.92 (high)                                                  │
│ • Routing target: "frontend-visual-workflow"                               │
└────────────────────────────┬───────────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────────────────┐
│ STAGE 3: WorkflowTemplateRegistry (NEW - Phase 100 S1)                     │
│ • Auto-discovery triggered by IntentRouter metadata                        │
│ • Search criteria:                                                         │
│   - intent: ["FIX", "REFACTOR"]                                            │
│   - has_screenshot: true                                                   │
│   - category: "frontend" or "tdd"                                          │
│   - tags: ["visual-testing", "tdd"]                                        │
│ • Template discovered: "tdd/frontend-visual-tdd"                           │
│ • Confidence: 0.95 (exact match)                                           │
└────────────────────────────┬───────────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────────────────┐
│ STAGE 4: Template Validation (EnforcementOrchestrator)                     │
│ • Load metadata: cortex-registry/workflows/tdd/frontend-visual-tdd/       │
│ • Validate governance gates:                                               │
│   ✅ CORE-008: Template has golden tests                                  │
│   ✅ CORE-028: Filename compliant (33 chars)                              │
│   ✅ CORE-035: No duplicate templates                                     │
│   ✅ CORE-048: Holistic validation gates present                          │
│   ✅ Required orchestrators available                                     │
│   ✅ Security scan passed                                                 │
│ • Run golden tests (sunshine + rainy + edge + blindspot)                  │
│ • Governance score: 9.8/10                                                 │
└────────────────────────────┬───────────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────────────────┐
│ STAGE 5: WorkflowComposer Execution (Existing - Phase 84)                  │
│ • Load workflow.yaml from template directory                               │
│ • Parse 5 stages:                                                          │
│   1. Vision Analysis (LENSOrchestrator + VisionAnalyzer)                  │
│      → Analyze screenshot (atomic mode)                                    │
│      → Extract: "black box at (150, 200), 'Manage' at (300, 250)"        │
│   2. Challenge Generation (ChallengeEngine)                                │
│      → Generate design challenges                                          │
│      → Validate: "Move section left - accessibility OK?"                  │
│   3. TDD Cycle (TDDOrchestrator)                                          │
│      → RED: Write failing test for layout change                          │
│      → GREEN: Implement CSS/HTML changes                                  │
│      → REFACTOR: Clean up, extract utilities                              │
│   4. Holistic Validation (EnforcementOrchestrator)                        │
│      → Verify: Zero lint errors, 95%+ coverage, no regressions            │
│   5. Deploy Preview (DeploymentOrchestrator)                              │
│      → Generate staging URL                                                │
│      → Run Lighthouse audit                                                │
└────────────────────────────┬───────────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────────────────┐
│ STAGE 6: Results + Audit Trail                                             │
│ • Execution duration: 28 minutes                                           │
│ • Tests passing: 37/37 (100%)                                              │
│ • Lighthouse score: 96 (maintained)                                        │
│ • Audit trail: AC_START → AC_COMPLETE with full lineage                   │
│ • Preview URL: https://cortex-staging.example.com/preview/abc123          │
│ • User notification: "✅ Layout fixed + deployed to staging"              │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔗 INTEGRATION POINTS (Code Changes Required)

### 1. IntentRouter Enhancement (NEW)

**File:** `cortex/orchestrators/core/intent_router.py`

**Add:** Visual context detection + workflow template routing

```python
class IntentRouter(IOrchestrator):
    def __init__(self):
        self.workflow_registry = None  # Lazy load
        
    def classify_intent_with_workflow_suggestion(
        self, 
        request: str, 
        attachments: List[Dict[str, Any]] = None
    ) -> Tuple[IntentType, Optional[str]]:
        """
        Classify intent AND suggest workflow template if applicable.
        
        NEW: Detects visual change requests (screenshot attachments)
        and recommends appropriate workflow templates.
        
        Args:
            request: User's natural language request
            attachments: List of attachments (screenshots, files, etc.)
        
        Returns:
            (intent_type, template_id or None)
            
        Example:
            request = "Fix the black box, move Manage section left"
            attachments = [{"type": "image", "path": "hero.png"}]
            
            → Returns: (IntentType.FIX, "tdd/frontend-visual-tdd")
        """
        # Standard intent classification
        intent = self._classify_intent(request)
        
        # NEW: Check for visual context
        has_screenshot = any(
            att.get("type") == "image" 
            for att in (attachments or [])
        )
        
        if has_screenshot and intent in [IntentType.FIX, IntentType.REFACTOR, IntentType.IMPLEMENT]:
            # Lazy load workflow registry
            if self.workflow_registry is None:
                from cortex.orchestrators.workflow.template_registry import (
                    WorkflowTemplateRegistry
                )
                self.workflow_registry = WorkflowTemplateRegistry()
            
            # Search for matching template
            templates = self.workflow_registry.search(
                query=request,
                filters={
                    "intent": [intent.value],
                    "has_visual_analysis": True,
                    "category": ["frontend", "tdd"]
                }
            )
            
            if templates:
                # Return best match
                best_template = templates[0]  # Sorted by relevance
                self.logger.info(
                    f"Auto-selected workflow template: {best_template.template_id}"
                )
                return (intent, best_template.template_id)
        
        return (intent, None)
```

---

### 2. MasterOrchestrator Integration (UPDATE)

**File:** `cortex/orchestrators/core/master_orchestrator.py`

**Update:** Stage 2 to check for workflow template suggestions

```python
class MasterOrchestrator(IOrchestrator):
    def execute_operation(
        self, 
        operation_name: str, 
        parameters: Dict[str, Any]
    ) -> Result[Any]:
        """Execute operation with workflow template auto-selection."""
        
        # Stage 1: Context comprehension (existing)
        comprehension_result = self._stage1_comprehension(operation_name, parameters)
        
        # Stage 2: Intent classification + workflow suggestion (ENHANCED)
        intent, template_id = self.intent_router.classify_intent_with_workflow_suggestion(
            request=parameters.get("request", ""),
            attachments=parameters.get("attachments", [])
        )
        
        # NEW: If template suggested, use cortex_workflow tool instead
        if template_id:
            self.logger.info(
                f"Auto-routing to workflow template: {template_id}"
            )
            
            # Invoke cortex_workflow MCP tool internally
            from cortex.mcp.tools.operations import CortexWorkflow
            workflow_tool = CortexWorkflow()
            
            workflow_result = workflow_tool.execute(
                operation="execute",
                template_id=template_id,
                parameters={
                    "request": parameters.get("request"),
                    "attachments": parameters.get("attachments"),
                    "mode": "full"  # full TDD cycle
                },
                orchestrator_context={
                    "intent": intent.value,
                    "confidence": 0.95,
                    "auto_selected": True
                }
            )
            
            return Ok(workflow_result.data)
        
        # Otherwise: Standard orchestrator routing (existing)
        return self._execute_standard_flow(intent, parameters)
```

---

### 3. MCP Tool Integration (NEW)

**File:** `cortex/mcp/tools/operations.py`

**Add:** cortex_workflow tool that WorkflowTemplateRegistry calls

```python
class CortexWorkflow(ConsolidatedTool):
    """Execute workflow templates with governance validation."""
    
    @property
    def name(self) -> str:
        return "cortex_workflow"
    
    async def execute(self, **params) -> ToolResult:
        """
        Execute workflow operation.
        
        Operations:
        - execute: Run template end-to-end
        - list: List all templates
        - search: Find templates by query
        - validate: Check template governance
        - preview: Show template structure
        """
        validate_orchestrator_context(params.get("orchestrator_context"))
        
        operation = params.get("operation", "list")
        
        if operation == "execute":
            return await self._execute_template(params)
        elif operation == "list":
            return await self._list_templates(params)
        elif operation == "search":
            return await self._search_templates(params)
        elif operation == "validate":
            return await self._validate_template(params)
        elif operation == "preview":
            return await self._preview_template(params)
    
    async def _execute_template(self, params: Dict) -> ToolResult:
        """
        Execute template via WorkflowComposer + validation.
        
        Example:
            params = {
                "template_id": "tdd/frontend-visual-tdd",
                "parameters": {
                    "request": "Fix black box",
                    "attachments": [{"type": "image", "path": "hero.png"}]
                }
            }
        """
        template_id = params.get("template_id")
        
        # 1. Discover template
        from cortex.orchestrators.workflow.template_registry import (
            WorkflowTemplateRegistry
        )
        registry = WorkflowTemplateRegistry()
        template = registry.discover_template(template_id)
        
        if not template:
            return ToolResult(
                success=False, 
                error=f"Template not found: {template_id}"
            )
        
        # 2. Validate (governance + golden tests)
        validation = registry.validate_template(template)
        if not validation.passed:
            return ToolResult(
                success=False, 
                error=f"Template validation failed: {validation.errors}"
            )
        
        # 3. Execute via WorkflowComposer
        from cortex.orchestrators.workflow.workflow_composer import WorkflowComposer
        composer = WorkflowComposer(template_path=template.file_path)
        result = composer.execute(parameters=params.get("parameters", {}))
        
        # 4. Audit verification
        audit_result = self._verify_audit_trail(composer)
        
        return ToolResult(
            success=result.success,
            data={
                "execution": result,
                "audit": audit_result,
                "golden_tests": validation.test_results,
                "template_id": template_id,
                "duration": result.duration_seconds,
            }
        )
```

---

## 🤖 USER SCENARIOS (How It Works)

### Scenario 1: Screenshot + Fix Request

**User Input (VS Code Copilot Chat):**
```
"Fix the black box, move the section with title 'Manage' to the left"
[Attaches: hero-section.png]
```

**CORTEX Flow:**
1. **IntentRouter** detects:
   - Intent: `FIX` + `REFACTOR` (composite)
   - Visual context: Screenshot attached
   - Recommends: `tdd/frontend-visual-tdd`

2. **WorkflowTemplateRegistry** validates:
   - Template exists: ✅
   - Golden tests passing: ✅
   - Governance score: 9.8/10 ✅

3. **WorkflowComposer** executes:
   - Stage 1: Vision API extracts "black box at (150, 200)"
   - Stage 2: Challenge: "Is move accessible?"
   - Stage 3: TDD cycle (RED → GREEN → REFACTOR)
   - Stage 4: Holistic validation (lint, coverage, regression)
   - Stage 5: Deploy preview to staging

4. **User receives:**
   ```
   ✅ Layout Fixed + Deployed

   Duration: 28 minutes
   Tests: 37/37 passing
   Lighthouse: 96 (maintained)
   Preview: https://cortex-staging.example.com/preview/abc123

   Changes:
   • Fixed black box visibility (hero-cta-001)
   • Moved 'Manage' section left (nav-item-manage)
   • Updated responsive breakpoints
   • Zero accessibility regressions
   ```

---

### Scenario 2: Add New Chart Section

**User Input:**
```
"Add a new section below Customer Report that displays a chart"
[Attaches: customer-report.png]
```

**CORTEX Flow:**
1. **IntentRouter** detects:
   - Intent: `IMPLEMENT`
   - Visual context: Screenshot attached
   - Recommends: `tdd/frontend-visual-tdd`

2. **WorkflowComposer** executes:
   - Stage 1: Vision API identifies "Customer Report at (200, 400)"
   - Stage 2: Challenge: "Chart data source? Accessibility?"
   - Stage 3: TDD cycle
     - RED: Test for new chart component
     - GREEN: Implement chart with react-chartjs-2
     - REFACTOR: Extract ChartSection component
   - Stage 4: Validation (95% coverage, WCAG 2.1 AA)
   - Stage 5: Deploy preview

3. **User receives:**
   ```
   ✅ Chart Section Implemented

   Duration: 32 minutes
   Tests: 42/42 passing
   New component: ChartSection.tsx
   Preview: https://cortex-staging.example.com/preview/xyz789

   Features:
   • Line chart with responsive scaling
   • Accessible (ARIA labels, keyboard nav)
   • Dark mode support
   • Data fetched from /api/customer-metrics
   ```

---

### Scenario 3: Refactor Without Screenshot

**User Input:**
```
"Refactor the authentication module to use JWT tokens"
```

**CORTEX Flow:**
1. **IntentRouter** detects:
   - Intent: `REFACTOR`
   - Visual context: None
   - Template: None (standard TDD flow)

2. **MasterOrchestrator** routes to:
   - **TDDOrchestrator** (standard refactoring workflow)
   - No WorkflowComposer involved
   - Direct orchestrator execution

3. **User receives:**
   ```
   ✅ Authentication Refactored to JWT

   Duration: 18 minutes
   Tests: 28/28 passing
   Changes: 
   • Replaced session tokens with JWT
   • Added token refresh mechanism
   • Updated middleware for JWT validation
   ```

**Key Point:** Workflow templates only trigger when:
- Visual context detected (screenshot)
- Intent matches template category
- Template confidence > 0.80

Otherwise, standard orchestrator routing applies.

---

## 🔄 AUTOMATIC vs. MANUAL Template Selection

### Automatic (Transparent to User)

**Triggers:**
- User attaches screenshot
- Intent is IMPLEMENT/FIX/REFACTOR
- WorkflowTemplateRegistry finds matching template

**User sees:** Seamless execution (no "choose template" prompt)

**Example:**
```
User: "Fix layout bug" + [screenshot]
CORTEX: [Internally uses frontend-visual-tdd template]
Result: "✅ Layout fixed + deployed to staging"
```

---

### Manual (Explicit Template Request)

**User invokes cortex_workflow directly:**

```
User: "List available workflow templates for frontend"
CORTEX: cortex_workflow(operation="list", category="frontend")

Response:
1. frontend/component-testing
2. frontend/visual-regression-suite  
3. frontend/performance-lighthouse
4. tdd/frontend-visual-tdd

User: "Execute tdd/frontend-visual-tdd for hero section"
CORTEX: cortex_workflow(
    operation="execute", 
    template_id="tdd/frontend-visual-tdd",
    parameters={"target": "hero-section.html"}
)
```

---

## 📝 PHASE 100 UPDATES REQUIRED

### Stage 1: WorkflowTemplateRegistry (6h)

**Add:** `search()` method with visual context filtering

```python
def search(
    self, 
    query: str, 
    filters: Dict[str, Any] = None
) -> List[WorkflowTemplate]:
    """
    Semantic search with visual context filtering.
    
    Filters:
    - intent: ["IMPLEMENT", "FIX", "REFACTOR"]
    - has_visual_analysis: bool
    - category: ["tdd", "frontend", "api", etc.]
    - tags: List[str]
    - confidence_threshold: float (default 0.80)
    """
    pass
```

---

### Stage 2: MCP Tool (4h)

**Implement:** `cortex_workflow` with 5 operations

Already covered above in **MCP Tool Integration** section.

---

### Stage 4: Fix Phase 99 + Migrate (2h)

**Rename:** 
- From: `phase-99-vision-api-dogfooding-workflow.yaml`
- To: `cortex-registry/workflows/tdd/frontend-visual-tdd/workflow.yaml`

**Ensure:** Metadata includes:
```yaml
visual_analysis: true
requires_screenshot: true
```

---

## ✅ SUMMARY: How User Gets Value

1. **User attaches screenshot** → IntentRouter detects visual context
2. **WorkflowTemplateRegistry** → Auto-selects appropriate template
3. **WorkflowComposer** → Executes 5-stage TDD workflow
4. **EnforcementOrchestrator** → Validates governance + golden tests
5. **User receives** → Fixed layout + deployed preview + audit trail

**Key Innovation:** Users don't need to know workflow templates exist. CORTEX intelligently routes based on request context (screenshot presence, intent type, domain).

**Fallback:** If no template matches, standard orchestrator routing applies (existing behavior preserved).

---

**End of Integration Analysis**
