# End-to-End Request Flow

**Purpose:** Complete documentation of the CORTEX request lifecycle  
**Audience:** All Technical Stakeholders  
**Last Updated:** 2026-02-10

---

## Table of Contents

- [Overview](#overview)
- [Request Lifecycle Diagram](#request-lifecycle-diagram)
- [Stage 1: Request Reception](#stage-1-request-reception)
- [Stage 2: Authentication & Authorization](#stage-2-authentication--authorization)
- [Stage 3: Intent Classification](#stage-3-intent-classification)
- [Stage 4: Context Enrichment](#stage-4-context-enrichment)
- [Stage 5: Governance Validation](#stage-5-governance-validation)
- [Stage 6: Orchestrator Execution](#stage-6-orchestrator-execution)
- [Stage 7: Result Processing](#stage-7-result-processing)
- [Stage 8: Response Delivery](#stage-8-response-delivery)
- [Timing Analysis](#timing-analysis)
- [Related Documents](#related-documents)

---

## Overview

This document traces a complete request through CORTEX, from client submission to response delivery. Understanding this flow is essential for architects, developers, and operations teams.

---

## Request Lifecycle Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    END-TO-END REQUEST FLOW                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  CLIENT                                                          │
│  ┌────────────────────────────────────────────────────────────┐│
│  │ POST /mcp/execute                                          ││
│  │ {"method": "tools/call", "params": {"name": "cortex_..."}} ││
│  └────────────────────────────────────────────────────────────┘│
│                              │                                   │
│                              ▼                                   │
│  STAGE 1: RECEPTION (5ms)                                       │
│  ┌────────────────────────────────────────────────────────────┐│
│  │ MCP Gateway → JSON-RPC Parse → Request Validation          ││
│  └────────────────────────────────────────────────────────────┘│
│                              │                                   │
│                              ▼                                   │
│  STAGE 2: AUTHENTICATION (10ms)                                 │
│  ┌────────────────────────────────────────────────────────────┐│
│  │ API Key Check → Rate Limit → Session Context               ││
│  └────────────────────────────────────────────────────────────┘│
│                              │                                   │
│                              ▼                                   │
│  STAGE 3: CLASSIFICATION (25ms)                                 │
│  ┌────────────────────────────────────────────────────────────┐│
│  │ IntentRouter → Keyword Analysis → Confidence Scoring       ││
│  └────────────────────────────────────────────────────────────┘│
│                              │                                   │
│                              ▼                                   │
│  STAGE 4: ENRICHMENT (50-200ms)                                │
│  ┌────────────────────────────────────────────────────────────┐│
│  │ LENS → Git + AST + Comments → Context Synthesis            ││
│  └────────────────────────────────────────────────────────────┘│
│                              │                                   │
│                              ▼                                   │
│  STAGE 5: GOVERNANCE (100ms)                                    │
│  ┌────────────────────────────────────────────────────────────┐│
│  │ EnforcementOrchestrator → 7 Agents → Pre-Execution Gate   ││
│  └────────────────────────────────────────────────────────────┘│
│                              │                                   │
│                              ▼                                   │
│  STAGE 6: EXECUTION (varies)                                    │
│  ┌────────────────────────────────────────────────────────────┐│
│  │ Target Orchestrator → Operation Execution → Results        ││
│  └────────────────────────────────────────────────────────────┘│
│                              │                                   │
│                              ▼                                   │
│  STAGE 7: PROCESSING (20ms)                                     │
│  ┌────────────────────────────────────────────────────────────┐│
│  │ Result Aggregation → Quality Scoring → Audit Logging       ││
│  └────────────────────────────────────────────────────────────┘│
│                              │                                   │
│                              ▼                                   │
│  STAGE 8: DELIVERY (10ms)                                       │
│  ┌────────────────────────────────────────────────────────────┐│
│  │ Header Injection → JSON-RPC Response → Client              ││
│  └────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Stage 1: Request Reception

### Entry Point

```python
# MCP Gateway receives request
@app.route("/mcp/execute", methods=["POST"])
async def execute_mcp_tool(request: Request) -> Response:
    """
    Main MCP tool execution endpoint.
    
    Accepts JSON-RPC 2.0 requests and routes to tool handlers.
    """
    # Parse JSON-RPC request
    try:
        body = await request.json()
        mcp_request = MCPRequest(**body)
    except Exception as e:
        return json_rpc_error(-32700, f"Parse error: {e}")
    
    # Validate request structure
    if mcp_request.jsonrpc != "2.0":
        return json_rpc_error(-32600, "Invalid JSON-RPC version")
    
    if not mcp_request.method:
        return json_rpc_error(-32600, "Missing method")
    
    # Proceed to authentication
    return await process_authenticated_request(mcp_request)
```

### Request Validation

| Check | Validation | Error Code |
|-------|------------|------------|
| JSON Parse | Valid JSON body | -32700 |
| JSON-RPC Version | "2.0" exactly | -32600 |
| Method Present | Non-empty string | -32600 |
| Params Valid | Object or array | -32602 |

---

## Stage 2: Authentication & Authorization

### API Key Validation

```python
async def authenticate_request(request: Request) -> AuthResult:
    """
    Validate API key and establish session.
    """
    # Extract API key
    api_key = request.headers.get("X-CORTEX-API-KEY")
    
    if not api_key:
        return AuthResult(
            success=False,
            error="Missing API key"
        )
    
    # Validate key
    key_info = await validate_api_key(api_key)
    
    if not key_info.valid:
        return AuthResult(
            success=False,
            error="Invalid API key"
        )
    
    # Check rate limit
    if not await check_rate_limit(key_info.client_id):
        return AuthResult(
            success=False,
            error="Rate limit exceeded"
        )
    
    # Create session context
    session = SessionContext(
        client_id=key_info.client_id,
        permissions=key_info.permissions,
        rate_limit=key_info.rate_limit
    )
    
    return AuthResult(success=True, session=session)
```

### Rate Limiting

| Client Type | Requests/Min | Burst |
|-------------|--------------|-------|
| Standard | 60 | 10 |
| Premium | 120 | 20 |
| Enterprise | Unlimited | 100 |

---

## Stage 3: Intent Classification

### Classification Flow

```python
async def classify_intent(
    request: str,
    session: SessionContext
) -> RoutingDecision:
    """
    Classify user intent and determine routing.
    """
    router = IntentRouter()
    
    # Keyword analysis
    keyword_scores = router.analyze_keywords(request)
    
    # Get preliminary intent
    primary_intent = router.get_primary_intent(keyword_scores)
    
    # Check for composite intents
    composite = CompositeIntentDetector().detect(request, primary_intent)
    
    # Calculate confidence
    confidence = router.calculate_confidence(
        keyword_scores=keyword_scores,
        request_clarity=router.measure_clarity(request)
    )
    
    return RoutingDecision(
        intent_type=primary_intent,
        composite_intents=composite,
        confidence_score=confidence.overall,
        target_handler=router.get_target_orchestrator(primary_intent)
    )
```

---

## Stage 4: Context Enrichment

### LENS Analysis

```python
async def enrich_context(
    request: str,
    routing: RoutingDecision,
    session: SessionContext
) -> UnifiedIntelligenceContext:
    """
    Enrich request with LENS intelligence.
    """
    lens = LENSOrchestrator(repo_path=session.workspace_path)
    
    # Check cache first
    cache_key = f"{session.workspace_path}:{request[:100]}"
    if cached := await lens_cache.get(cache_key):
        return cached
    
    # Run analyzers in parallel
    git_task = asyncio.create_task(
        lens.git_analyzer.analyze_recent(hours=24)
    )
    ast_task = asyncio.create_task(
        lens.ast_analyzer.analyze_workspace()
    )
    comment_task = asyncio.create_task(
        lens.comment_extractor.extract_todos()
    )
    
    git_result, ast_result, comment_result = await asyncio.gather(
        git_task, ast_task, comment_task
    )
    
    # Synthesize context
    context = UnifiedIntelligenceContext(
        file_context=ast_result,
        git_insights=git_result,
        comment_analysis=comment_result,
        routing_decision=routing
    )
    
    # Cache result
    await lens_cache.set(cache_key, context, ttl=3600)
    
    return context
```

---

## Stage 5: Governance Validation

### Pre-Execution Gate

```python
async def validate_governance(
    request: str,
    context: UnifiedIntelligenceContext,
    routing: RoutingDecision
) -> GovernanceResult:
    """
    Run pre-execution governance checks.
    """
    enforcement = EnforcementOrchestrator()
    
    # Run all agents
    results = await enforcement.validate_all(
        request=request,
        context=context,
        intent=routing.intent_type
    )
    
    # Check for blockers
    blockers = [r for r in results if r.status == "BLOCKED"]
    
    if blockers:
        return GovernanceResult(
            passed=False,
            blockers=blockers,
            warnings=[r for r in results if r.status == "WARNING"]
        )
    
    return GovernanceResult(
        passed=True,
        warnings=[r for r in results if r.status == "WARNING"]
    )
```

### Agent Validation Order

| Order | Agent | Rules |
|-------|-------|-------|
| 1 | GovernanceEnforcementAgent | CORE-008, 011, 012, 013 |
| 2 | SecurityCheckpointAgent | CORE-025, 026, 027 |
| 3 | ComplianceValidationAgent | Tier 1 rules |
| 4 | FileNamingEnforcementAgent | CORE-028 |
| 5 | IncrementalExecutionAgent | CORE-001, 004 |
| 6 | MarkdownSuppressionAgent | CORE-002 |
| 7 | ArchitectureIntegrityAgent | CORE-017-020, 032-041 |

---

## Stage 6: Orchestrator Execution

### Execution Delegation

```python
async def execute_operation(
    routing: RoutingDecision,
    context: UnifiedIntelligenceContext,
    governance: GovernanceResult
) -> OperationResult:
    """
    Execute operation via target orchestrator.
    """
    master = MasterOrchestrator.instance()
    
    # Get target orchestrator
    orchestrator = routing.target_orchestrator
    
    if not orchestrator:
        # Try fallback chain
        for fallback in routing.fallback_orchestrators:
            if fallback.is_available():
                orchestrator = fallback
                break
    
    if not orchestrator:
        return OperationResult(
            success=False,
            error="No available orchestrator"
        )
    
    # Execute with timeout
    try:
        result = await asyncio.wait_for(
            orchestrator.execute_operation(
                operation_name=routing.intent_type.value,
                parameters={"request": request, "context": context}
            ),
            timeout=30.0
        )
        return result
    except asyncio.TimeoutError:
        return OperationResult(
            success=False,
            error="Operation timed out"
        )
```

---

## Stage 7: Result Processing

### Result Aggregation

```python
async def process_result(
    result: OperationResult,
    context: UnifiedIntelligenceContext,
    session: SessionContext
) -> ProcessedResult:
    """
    Process and enrich operation result.
    """
    # Quality scoring
    quality = ResponseQualityScorer().score(result)
    
    # Audit logging
    audit_id = await EnhancedAuditLogger().log(
        operation=result.operation,
        status=result.status,
        artifacts=result.artifacts,
        session_id=session.session_id
    )
    
    # Metrics emission
    await emit_metrics(
        operation=result.operation,
        duration=result.duration,
        success=result.success
    )
    
    return ProcessedResult(
        result=result,
        quality_score=quality,
        audit_id=audit_id
    )
```

---

## Stage 8: Response Delivery

### Response Formatting

```python
async def deliver_response(
    processed: ProcessedResult,
    request_id: str
) -> Response:
    """
    Format and deliver final response.
    """
    # Inject response header
    header = ResponseHeaderInjector().inject(
        orchestrator=processed.result.orchestrator,
        operation=processed.result.operation
    )
    
    # Build JSON-RPC response
    response = MCPResponse(
        jsonrpc="2.0",
        result={
            "header": header,
            "status": "success" if processed.result.success else "error",
            "data": processed.result.data,
            "audit_id": processed.audit_id
        },
        id=request_id
    )
    
    return Response(
        content=response.to_json(),
        media_type="application/json"
    )
```

---

## Timing Analysis

### Stage Breakdown

| Stage | Target | Typical | Notes |
|-------|--------|---------|-------|
| 1. Reception | 5ms | 3ms | JSON parsing |
| 2. Authentication | 10ms | 8ms | Key validation |
| 3. Classification | 25ms | 15ms | Intent routing |
| 4. Enrichment (cached) | 50ms | 30ms | Cache hit |
| 4. Enrichment (uncached) | 200ms | 150ms | Full LENS |
| 5. Governance | 100ms | 80ms | 7 agents |
| 6. Execution | varies | — | Operation dependent |
| 7. Processing | 20ms | 15ms | Quality + audit |
| 8. Delivery | 10ms | 5ms | Response format |

### Total Latency (excluding execution)

| Scenario | Target | Typical |
|----------|--------|---------|
| **Cache Hit** | < 220ms | 160ms |
| **Cache Miss** | < 370ms | 280ms |

---

## Error Handling

### Error Types

| Error Type | Stage | Response |
|------------|-------|----------|
| Parse Error | 1 | -32700 |
| Auth Error | 2 | -32001 |
| Rate Limit | 2 | -32002 |
| Classification Error | 3 | -32003 |
| Governance Block | 5 | -32004 |
| Execution Error | 6 | -32005 |
| Timeout | 6 | -32006 |

---

## Related Documents

- [MasterOrchestrator](master-orchestrator.md) — Coordination details
- [IntentRouter](intent-router.md) — Classification details
- [LENS Overview](../lens/overview.md) — Context enrichment
- [Governance](../capabilities/governance-compliance.md) — Validation

---

*Part of CORTEX Architecture Documentation*
