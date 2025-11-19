# Agent System Narrative

## For Leadership

CORTEX uses a brain-inspired architecture with two specialized teams working together:

**LEFT Brain Team (Executors)** - Like skilled craftspeople, they implement features with precision. They write code, create tests, fix bugs, and ensure quality. Think "builders."

**RIGHT Brain Team (Strategists)** - Like architects and project managers, they plan work, analyze requirements, and protect project quality. Think "planners."

The **Corpus Callosum** is the communication bridge - LEFT brain executes RIGHT brain's plans, RIGHT brain learns from LEFT brain's results.

## For Developers

**Architecture Pattern:** Distributed agent system with hemisphere specialization

**Agent Responsibilities:**

LEFT Hemisphere (Tactical):
1. **Code Executor** - Implements features (TDD enforced)
2. **Test Generator** - Creates test suites (RED phase)
3. **Error Corrector** - Fixes bugs (learns from Tier 2)
4. **Health Validator** - Enforces DoD (zero errors/warnings)
5. **Commit Handler** - Creates semantic commits

RIGHT Hemisphere (Strategic):
1. **Intent Router** - Detects user intent (PLAN, EXECUTE, etc.)
2. **Work Planner** - Creates multi-phase roadmaps
3. **Screenshot Analyzer** - Extracts requirements from images
4. **Change Governor** - Protects architecture
5. **Brain Protector** - Enforces Rule #22 (challenge changes)

**Coordination:**
- Message-based (corpus-callosum/coordination-queue.jsonl)
- Asynchronous with acknowledgments
- Both hemispheres must agree on major actions

## Key Takeaways

1. **Separation of concerns** - Strategy vs execution
2. **Coordinated autonomy** - Agents collaborate but don't interfere
3. **Learning loop** - Execution results feed strategic planning
4. **Quality gates** - Multiple validation layers

## Usage Scenarios

**Scenario 1: Simple Request ("Add a button")**
1. RIGHT: Intent Router → EXECUTE detected
2. RIGHT: Routes to LEFT Code Executor
3. LEFT: Code Executor implements with TDD
4. LEFT: Health Validator checks quality
5. LEFT: Commit Handler saves work
6. RIGHT: Knowledge Graph learns pattern

**Scenario 2: Risky Request ("Delete brain data")**
1. RIGHT: Intent Router → PROTECT detected
2. RIGHT: Brain Protector challenges request
3. RIGHT: Offers safer alternatives
4. User approves alternative
5. LEFT: Executes safe cleanup

*Version: 1.0*  
*Last Updated: November 19, 2025*
