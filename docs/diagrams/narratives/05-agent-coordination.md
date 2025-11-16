# Agent Coordination Narrative

## For Leadership

This sequence diagram shows CORTEX agents working together like a well-orchestrated team.

**The Process:**
1. **You make a request** → Intent Router understands what you need
2. **Planner creates strategy** → Work Planner breaks work into phases
3. **Executors implement** → Code Executor + Test Generator work in tandem
4. **Validators verify quality** → Health Validator ensures standards met
5. **System learns** → Knowledge Graph captures patterns for future use

**Key Insight:** Multiple specialists collaborate automatically. You make one request, CORTEX coordinates 5-6 agents behind the scenes.

## For Developers

**Architecture Pattern:** Message-driven agent choreography

**Coordination Mechanism:**
- **Corpus Callosum** acts as message broker
- Agents communicate via coordination-queue.jsonl
- Asynchronous with acknowledgments
- No direct agent-to-agent coupling

**Example Workflow:**

```
User: "Add authentication to dashboard"

Step 1: Intent Router (RIGHT)
  ↓ message: {"intent": "PLAN", "confidence": 0.88}

Step 2: Work Planner (RIGHT)
  ↓ Creates 3-phase plan
  ↓ message: {"phase": 1, "tasks": [...]}

Step 3: Corpus Callosum
  ↓ Routes to LEFT hemisphere
  ↓ message: {"target": "code-executor", "plan": ...}

Step 4: Code Executor (LEFT)
  ↓ Requests test creation first (TDD)
  ↓ message: {"action": "generate_tests", "feature": "auth"}

Step 5: Test Generator (LEFT)
  ↓ Creates failing tests
  ↓ Tests: RED ❌ (expected)

Step 6: Code Executor (LEFT)
  ↓ Implements feature
  ↓ Tests: GREEN ✅

Step 7: Health Validator (LEFT)
  ↓ Validates DoD
  ↓ Result: PASS ✅

Step 8: Knowledge Graph (RIGHT)
  ↓ Stores "authentication_workflow" pattern
  ↓ Learning complete
```

**Message Structure:**
```json
{
  "from": "work-planner",
  "to": "code-executor",
  "type": "task_assignment",
  "timestamp": "2025-11-16T10:30:00Z",
  "payload": {
    "phase": 1,
    "tasks": ["Create AuthService", "Add login endpoint"],
    "success_criteria": ["All tests pass"]
  }
}
```

## Key Takeaways

1. **Asynchronous coordination** - Agents don't block each other
2. **Message-based** - Clear communication protocol
3. **Hemispheric separation** - Strategy (RIGHT) vs execution (LEFT)
4. **Learning loop** - Execution results inform future planning
5. **Quality gates** - Multiple validation checkpoints

## Usage Scenarios

**Scenario 1: Simple Feature**
- 3 agents involved (Router → Executor → Validator)
- ~1 second total time
- Minimal coordination overhead

**Scenario 2: Complex Feature (shown in diagram)**
- 6+ agents involved
- ~3 seconds total time
- Full planning and validation pipeline

**Scenario 3: Risky Change**
- Brain Protector intervenes early
- Challenges request before execution
- Saves wasted effort

*Version: 1.0*  
*Last Updated: November 16, 2025*
