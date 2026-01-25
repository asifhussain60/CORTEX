# Orchestrator Reference

## Complete Orchestrator Registry

### Core Orchestrators (5)

**MasterOrchestrator**
- Purpose: Main execution hub
- Entry: `cortex.orchestrators.core.master_orchestrator`
- Coordinates all operations
- Handles complex workflows

**IntentRouter**
- Purpose: Request classification
- Entry: `cortex.orchestrators.core.intent_router`
- Uses LENS framework
- Routes to appropriate handler

**TDDOrchestrator**
- Purpose: Test-driven development
- Entry: `cortex.orchestrators.core.tdd_orchestrator`
- RED → GREEN → REFACTOR cycle
- Integrated knowledge injection

**WorkflowOrchestrator**
- Purpose: Complex workflow management
- Entry: `cortex.orchestrators.core.workflow_orchestrator`
- Multi-step operations
- State management

**InteractionOrchestrator**
- Purpose: Multi-turn conversations
- Entry: `cortex.orchestrators.core.interaction_orchestrator`
- Conversation state tracking
- Challenge integration

### Domain Orchestrators (4)

**RefactoringOrchestrator**
- Purpose: Code refactoring automation
- Complexity analysis
- Safe transformation

**PlanningOrchestrator**
- Purpose: Project planning
- Roadmap generation
- Phase management

**DomainOrchestrator**
- Purpose: Domain-specific operations
- Business logic handling
- Industry-specific patterns

**ConversationOrchestrator**
- Purpose: Dialogue management
- Turn-by-turn processing
- Context preservation

### Support Orchestrators (4)

**OnboardingOrchestrator**
- Purpose: Project onboarding
- Environment setup
- Dependency resolution

**SetupOrchestrator**
- Purpose: Configuration management
- Environment initialization
- Profile setup

**UpgradeOrchestrator**
- Purpose: Version upgrades
- Backward compatibility
- Migration support

**RollbackOrchestrator**
- Purpose: Change rollback
- State recovery
- History preservation

## Orchestrator Pattern

All orchestrators follow:

```python
class {Name}Orchestrator(BaseOrchestrator):
    async def execute(self, context: Context) -> Result:
        # AC_START: Log operation
        self.logger.log_operation_start()
        
        # Apply CORE rules
        self._validate_core_rules()
        
        # Execute logic
        result = await self._execute_logic(context)
        
        # AC_COMPLETE: Log completion
        self.logger.log_operation_complete()
        
        return result
```

---

Next: [MCP Tools](../03-api-reference/mcp-tools.md)
