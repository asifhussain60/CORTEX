# Complete Data Flow Narrative

## For Leadership

The Complete Data Flow shows how information travels through CORTEX from user request to learned intelligence, demonstrating the system's end-to-end operation.

**Input Phase** - User makes request in natural language: "Add authentication to login page." No commands to memorize, no syntax rules.

**Intelligence Phase** - CORTEX analyzes request across all brain tiers:
- Tier 1: Recent conversation context ("what login page?" - checks working memory)
- Tier 2: Similar past work ("we did authentication before, here's the pattern")
- Tier 3: Project health ("login page file is stable, safe to modify")

**Execution Phase** - Appropriate agent executes with full context:
- Work Planner creates strategy if complex
- Code Executor implements with TDD (RED → GREEN → REFACTOR)
- Test Generator ensures comprehensive coverage
- Health Validator confirms Definition of Done

**Learning Phase** - Success gets captured for future reuse:
- Patterns extracted (what files, what steps, what worked)
- Relationships tracked (files that changed together)
- Context updated (git metrics, file stability)

**Business Impact:** Every interaction makes CORTEX smarter. Knowledge accumulates, delivery accelerates, quality improves. The system learns your domain over time.

## For Developers

**End-to-End Flow:**

```
User Request
    ↓
┌─────────────────────────────────────┐
│ PHASE 1: INTENT DETECTION           │
│                                     │
│ Intent Router analyzes request:    │
│ • Parse natural language            │
│ • Extract entities (files, features)│
│ • Detect intent (PLAN/EXECUTE/etc) │
│ • Calculate confidence (70-95%)     │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ PHASE 2: CONTEXT RETRIEVAL          │
│                                     │
│ Query CORTEX Brain (Parallel):     │
│                                     │
│ Tier 1: Working Memory              │
│ • Last 20 conversations             │
│ • Entity references                 │
│ • "What did 'it' refer to?"         │
│                                     │
│ Tier 2: Knowledge Graph             │
│ • Similar past work                 │
│ • Proven workflows                  │
│ • File relationships                │
│                                     │
│ Tier 3: Context Intelligence        │
│ • File stability metrics            │
│ • Git commit patterns               │
│ • Session productivity data         │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ PHASE 3: DECISION MAKING            │
│                                     │
│ Right Brain (Strategic):            │
│ • Should we plan first? (Work Planner)│
│ • Any architectural risks? (Governor)│
│ • Brain protection needed? (Protector)│
│                                     │
│ Corpus Callosum:                    │
│ • Coordinate hemispheres            │
│ • Pass tasks to execution           │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ PHASE 4: EXECUTION                  │
│                                     │
│ Left Brain (Tactical):              │
│                                     │
│ Test Generator:                     │
│ • Write failing tests (RED)         │
│                                     │
│ Code Executor:                      │
│ • Implement feature (GREEN)         │
│ • Refactor code (REFACTOR)          │
│                                     │
│ Error Corrector:                    │
│ • Fix any syntax errors             │
│ • Prevent "wrong file" mistakes     │
│                                     │
│ Health Validator:                   │
│ • Run all tests                     │
│ • Check for errors/warnings         │
│ • Validate Definition of Done       │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ PHASE 5: LEARNING & STORAGE         │
│                                     │
│ Capture for Future Reuse:           │
│                                     │
│ → Tier 1 (Conversation)             │
│   • Store full conversation         │
│   • Track entities mentioned        │
│   • Index for fast search           │
│                                     │
│ → Tier 2 (Pattern Learning)         │
│   • Extract workflow pattern        │
│   • Calculate success confidence    │
│   • Update file relationships       │
│                                     │
│ → Tier 3 (Context Update)           │
│   • Analyze git commits made        │
│   • Update file stability metrics   │
│   • Track session productivity      │
│                                     │
│ → Tier 4 (Event Log)                │
│   • Record agent actions            │
│   • Store performance metrics       │
│   • Create audit trail              │
└─────────────────────────────────────┘
    ↓
Result Returned to User
```

**Detailed Phase Breakdown:**

**Phase 1: Intent Detection (45ms avg)**
```python
def detect_intent(user_request):
    # Parse request
    entities = extract_entities(user_request)
    keywords = extract_keywords(user_request)
    
    # Check Tier 2 for learned intent patterns
    learned_patterns = knowledge_graph.find_intent_patterns(keywords)
    
    # Combine signals
    confidence_signals = [
        keyword_match_score(keywords),
        learned_pattern_score(learned_patterns),
        context_continuity_score(tier1.get_recent())
    ]
    
    intent = determine_intent(confidence_signals)
    confidence = calculate_confidence(confidence_signals)
    
    return {
        "intent": intent,  # PLAN, EXECUTE, TEST, etc.
        "confidence": confidence,
        "entities": entities,
        "suggested_agent": route_to_agent(intent)
    }
```

**Phase 2: Context Retrieval (150ms avg, parallel)**
```python
async def retrieve_context(request, entities):
    # Query all tiers in parallel
    tier1_task = asyncio.create_task(
        tier1.search_conversations(entities)
    )
    tier2_task = asyncio.create_task(
        tier2.search_patterns(request)
    )
    tier3_task = asyncio.create_task(
        tier3.analyze_files(entities.files)
    )
    
    # Wait for all
    tier1_results = await tier1_task  # 18ms
    tier2_results = await tier2_task  # 92ms
    tier3_results = await tier3_task  # 156ms
    
    # Combine context
    return {
        "recent_conversations": tier1_results,
        "similar_patterns": tier2_results,
        "file_metrics": tier3_results,
        "total_time": 156  # max of parallel queries
    }
```

**Phase 3: Decision Making (89ms avg)**
```python
def make_decision(intent, context):
    # Right brain strategic analysis
    if intent == "EXECUTE":
        # Check if planning needed first
        complexity = estimate_complexity(context)
        if complexity > 0.7:
            return {
                "action": "PLAN_FIRST",
                "agent": "work-planner",
                "reason": "High complexity detected"
            }
    
    # Check brain protection
    if affects_cortex_core(context):
        challenge = brain_protector.validate_change(context)
        if not challenge.allowed:
            return {
                "action": "BLOCKED",
                "reason": challenge.reason,
                "alternatives": challenge.alternatives
            }
    
    # Proceed with execution
    return {
        "action": "EXECUTE",
        "agent": route_to_agent(intent),
        "plan": create_execution_plan(context)
    }
```

**Phase 4: Execution (varies by complexity)**
```python
def execute_feature(plan, context):
    # TDD workflow
    test_generator.write_failing_tests(plan)  # RED
    assert all_tests_fail(), "Tests must fail initially"
    
    code_executor.implement_feature(plan)  # GREEN
    assert all_tests_pass(), "Tests must pass"
    
    code_executor.refactor(plan)  # REFACTOR
    assert all_tests_still_pass(), "Tests must still pass"
    
    # Validate health
    health = health_validator.check_system()
    assert health.errors == 0, "Zero errors required"
    assert health.warnings == 0, "Zero warnings required"
    
    # Commit if all passed
    commit_handler.create_semantic_commit(plan)
    
    return {
        "success": True,
        "tests_passed": health.tests_passed,
        "files_modified": plan.files
    }
```

**Phase 5: Learning & Storage (120ms avg)**
```python
async def capture_learning(request, execution_result):
    # Store in all tiers (parallel)
    tier1_task = asyncio.create_task(
        tier1.store_conversation(request, execution_result)
    )
    
    tier2_task = asyncio.create_task(
        tier2.extract_pattern(request, execution_result)
    )
    
    tier3_task = asyncio.create_task(
        tier3.update_metrics(execution_result.files)
    )
    
    tier4_task = asyncio.create_task(
        tier4.log_event(execution_result)
    )
    
    # Wait for all storage operations
    await asyncio.gather(tier1_task, tier2_task, tier3_task, tier4_task)
    
    return {"learning_captured": True}
```

**Performance Metrics (End-to-End):**

| Phase | Operations | Avg Time | % of Total |
|-------|-----------|----------|------------|
| Intent Detection | Parsing, keyword extraction | 45ms | 8% |
| Context Retrieval | Query 3 tiers (parallel) | 156ms | 28% |
| Decision Making | Brain protection, routing | 89ms | 16% |
| Execution | TDD workflow, validation | 240ms | 43% |
| Learning & Storage | Store 4 tiers (parallel) | 120ms | 21% |
| **Total** | | **560ms** | **100%** |

*Note: Execution time varies significantly by feature complexity (simple: 100ms, complex: 5-10 minutes)*

## Key Takeaways

1. **Parallel processing** - Tier queries and storage happen concurrently
2. **Intelligent caching** - Frequent queries cached for speed
3. **Progressive enhancement** - Each interaction improves future performance
4. **Fail-safe execution** - Brain protection prevents risky changes
5. **Complete audit trail** - Every action logged in Tier 4

## Usage Scenarios

**Scenario 1: Simple Feature (Fast Path)**
```
User: "Make the button purple"

Flow:
  1. Intent Detection: EXECUTE (95% confidence) - 45ms
  2. Context Retrieval: "button" from Tier 1 recent context - 18ms
  3. Decision: Direct execution (low complexity) - 30ms
  4. Execution: Modify CSS, run tests - 120ms
  5. Learning: Store pattern "color_change" - 80ms

Total: 293ms (sub-second response)
```

**Scenario 2: Complex Feature (Planned Path)**
```
User: "Add user authentication with OAuth"

Flow:
  1. Intent Detection: PLAN (88% confidence) - 45ms
  2. Context Retrieval: Similar auth patterns from Tier 2 - 156ms
  3. Decision: Plan first (high complexity) - 89ms
  4. Planning: Interactive questions, phase breakdown - 5 min
  5. Execution: Multi-phase TDD implementation - 30 min
  6. Learning: Store "oauth_auth_workflow" pattern - 120ms

Total: ~35 minutes (with planning and validation)
```

**Scenario 3: Risky Change (Protected Path)**
```
User: "Delete all brain data"

Flow:
  1. Intent Detection: PROTECT (99% confidence) - 45ms
  2. Context Retrieval: No relevant patterns - 156ms
  3. Decision: BLOCKED by Brain Protector - 89ms
  4. Challenge: Suggest safer alternatives - 50ms
  5. No execution or learning (blocked)

Total: 340ms (rapid protection response)
```

*Version: 1.0*  
*Last Updated: November 17, 2025*
