# Orchestrator Development Guide

**Version:** 3.0 | **Updated:** December 11, 2025  
**Author:** Asif Hussain | **Status:** ✅ PRODUCTION

---

## Overview

This guide explains CORTEX's orchestration architecture, how to create new orchestrators, and how the routing system dispatches to them.

---

## Architecture

### Three-Layer System

```
┌─────────────────────────────────────────┐
│  Layer 1: Entry Point & Routing         │
│  - CortexEntry.process()                │
│  - IntentRouter (natural language)      │
│  - route_operation() (operation ID)     │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│  Layer 2: Execution Method Dispatch     │
│  - cli_wrapper → CLI scripts            │
│  - copilot_chat → Interactive workflows │
│  - internal → Not user-invokable        │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│  Layer 3: Orchestrator Implementations  │
│  - Planning, TDD, Cleanup, etc.         │
│  - Contain workflow logic               │
│  - Called by Layer 2                    │
└─────────────────────────────────────────┘
```

**Key Principle:** Orchestrators are **implementation**, not routing. The routing layer (execution_method) dispatches to orchestrators based on operation configuration.

---

## Orchestrator Types

### 1. User-Facing Orchestrators (16 operations)
**Execution Method:** `copilot_chat`

These are invoked via Copilot Chat and provide interactive, multi-turn workflows.

**Examples:**
- `PlanningOrchestrator` - Feature planning with DoR/DoD validation
- `TDDImplementationOrchestrator` - RED→GREEN→REFACTOR workflow
- `ADOWorkItemOrchestrator` - Create/track ADO work items

**Location:** `src/orchestrators/`

**Characteristics:**
- Interactive user prompts
- Multi-phase workflows
- Checkpoint-driven progress
- Conversation state management

### 2. System Operations (10 operations)
**Execution Method:** `cli_wrapper`

These perform file I/O, git operations, and system maintenance.

**Examples:**
- `AlignmentOrchestrator` - System alignment
- `CleanupOrchestrator` - Code cleanup
- `ReviewOrchestrator` - Architecture review

**Location:** `src/operations/modules/`

**Characteristics:**
- File system operations
- Git operations
- Batch processing
- No user interaction mid-execution

### 3. Internal Orchestrators (286 operations)
**Execution Method:** `internal`

These are called by other orchestrators, not directly by users.

**Examples:**
- Dashboard collectors
- Learning modules
- Utilities and helpers

**Location:** `src/orchestrators/`, `src/operations/utilities/`

**Characteristics:**
- API-only access
- Called by other orchestrators
- No direct user invocation

---

## Creating a New Orchestrator

### Step 1: Determine Execution Method

**Ask yourself:**
1. Does the user interact mid-workflow? → `copilot_chat`
2. Does it perform file/git operations? → `cli_wrapper`
3. Is it only called by other code? → `internal`

### Step 2: Choose Base Class

**For User-Facing (copilot_chat):**
```python
# src/orchestrators/my_new_orchestrator.py

from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class MyNewOrchestrator:
    """
    Description of what this orchestrator does.
    
    Workflow:
    1. Phase 1 description
    2. Phase 2 description
    3. Phase 3 description
    
    Example:
        orchestrator = MyNewOrchestrator(cortex_root="/path/to/CORTEX")
        result = orchestrator.execute_workflow(user_input="...")
    """
    
    def __init__(self, cortex_root: str):
        """
        Initialize orchestrator.
        
        Args:
            cortex_root: Path to CORTEX root directory
        """
        self.cortex_root = Path(cortex_root)
        self.logger = logging.getLogger(__name__)
    
    def execute_workflow(
        self,
        user_input: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Main workflow execution method.
        
        Args:
            user_input: User's request
            **kwargs: Additional parameters
        
        Returns:
            Dict with:
            - success: bool
            - message: str
            - result: Any workflow-specific data
        """
        try:
            self.logger.info(f"Starting workflow: {user_input}")
            
            # Phase 1: Validation
            if not self._validate_input(user_input):
                return {
                    "success": False,
                    "message": "Invalid input",
                    "result": None
                }
            
            # Phase 2: Processing
            result = self._process_workflow(user_input, **kwargs)
            
            # Phase 3: Finalization
            self._finalize(result)
            
            return {
                "success": True,
                "message": "Workflow completed successfully",
                "result": result
            }
            
        except Exception as e:
            self.logger.error(f"Workflow failed: {e}")
            return {
                "success": False,
                "message": str(e),
                "result": None
            }
    
    def _validate_input(self, user_input: str) -> bool:
        """Validate user input."""
        return bool(user_input and user_input.strip())
    
    def _process_workflow(
        self,
        user_input: str,
        **kwargs
    ) -> Any:
        """Main workflow logic."""
        # Implement your workflow here
        return {"processed": True}
    
    def _finalize(self, result: Any) -> None:
        """Finalize workflow (save files, update state, etc.)."""
        pass
```

**For System Operations (cli_wrapper):**
```python
# src/operations/modules/my_category/my_operation_orchestrator.py

from src.operations.modules.base_operation_module import BaseOperationModule, OperationResult
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class MyOperationOrchestrator(BaseOperationModule):
    """
    Description of what this operation does.
    
    Features:
    - Feature 1
    - Feature 2
    - Feature 3
    """
    
    def __init__(self, project_root: str):
        """
        Initialize operation module.
        
        Args:
            project_root: Path to project root
        """
        super().__init__("my_operation", project_root)
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute operation.
        
        Args:
            context: Operation context with parameters
        
        Returns:
            OperationResult with success status and details
        """
        try:
            self.logger.info("Starting operation...")
            
            # Your operation logic here
            
            return OperationResult(
                success=True,
                message="Operation completed successfully",
                data={
                    "files_modified": [],
                    "changes_made": []
                }
            )
            
        except Exception as e:
            self.logger.error(f"Operation failed: {e}")
            return OperationResult(
                success=False,
                message=str(e),
                data=None
            )
```

### Step 3: Register in cortex-operations.yaml

Add your operation to `cortex-operations.yaml`:

```yaml
operations:
  my_new_operation:
    description: "Description of what this does"
    execution_method: copilot_chat  # or cli_wrapper or internal
    natural_language:
      - "create my feature"
      - "do my thing"
      - "run my operation"
    cli_script: "scripts/cli_wrappers/my_operation_wrapper.py"  # Only for cli_wrapper
    category: "feature_category"
    related_operations:
      - other_operation
      - another_operation
```

**Field Descriptions:**
- `description`: What the operation does (1-2 sentences)
- `execution_method`: How it's invoked (cli_wrapper|copilot_chat|internal)
- `natural_language`: Phrases users might say to trigger it
- `cli_script`: Path to CLI wrapper (required for cli_wrapper)
- `category`: Group for organization (planning, tdd, cleanup, etc.)
- `related_operations`: Other operations users might need

### Step 4: Create CLI Wrapper (if cli_wrapper)

If your execution_method is `cli_wrapper`, create:

```python
# scripts/cli_wrappers/my_operation_wrapper.py

"""
CLI Wrapper for My Operation

Usage:
    python scripts/cli_wrappers/my_operation_wrapper.py --project-root /path --option value
"""

import sys
import argparse
import json
from pathlib import Path

# Add CORTEX to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.operations.modules.my_category.my_operation_orchestrator import MyOperationOrchestrator


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="My Operation")
    parser.add_argument("--project-root", required=True, help="Project root directory")
    parser.add_argument("--output", default="text", choices=["text", "json"], help="Output format")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--option", default="default", help="Custom option")
    
    args = parser.parse_args()
    
    # Execute operation
    orchestrator = MyOperationOrchestrator(args.project_root)
    result = orchestrator.execute({
        "option": args.option,
        "verbose": args.verbose
    })
    
    # Output results
    if args.output == "json":
        print(json.dumps(result.to_dict(), indent=2))
    else:
        if result.success:
            print(f"✅ {result.message}")
        else:
            print(f"❌ {result.message}")
            sys.exit(1)


if __name__ == "__main__":
    main()
```

### Step 5: Add to OrchestratorFactory (if needed)

If your orchestrator is used by other orchestrators, add it to the factory:

```python
# src/orchestrators/orchestrator_factory.py

class OrchestratorFactory:
    def get_my_orchestrator(self) -> Optional[IMyOrchestrator]:
        """Get or create My Orchestrator."""
        if self._my_orchestrator is None:
            try:
                from src.orchestrators.my_new_orchestrator import MyNewOrchestrator
                self._my_orchestrator = MyNewOrchestrator(
                    cortex_root=str(self.config.cortex_root)
                )
                logger.info("✅ MyNewOrchestrator initialized via factory")
            except ImportError as e:
                logger.warning(f"⚠️  MyNewOrchestrator not available: {e}")
                self._my_orchestrator = None
        
        return self._my_orchestrator
```

### Step 6: Test Your Orchestrator

**Unit Tests:**
```python
# tests/unit/test_my_orchestrator.py

import pytest
from src.orchestrators.my_new_orchestrator import MyNewOrchestrator


def test_orchestrator_initialization():
    """Test orchestrator can be initialized."""
    orch = MyNewOrchestrator(cortex_root="/tmp")
    assert orch.cortex_root.name == "tmp"


def test_workflow_execution():
    """Test workflow executes successfully."""
    orch = MyNewOrchestrator(cortex_root="/tmp")
    result = orch.execute_workflow("test input")
    assert result["success"] == True


def test_invalid_input_handling():
    """Test invalid input is handled gracefully."""
    orch = MyNewOrchestrator(cortex_root="/tmp")
    result = orch.execute_workflow("")
    assert result["success"] == False
    assert "Invalid input" in result["message"]
```

**Integration Tests:**
```python
# tests/integration/test_my_orchestrator_integration.py

import pytest
from pathlib import Path
from src.orchestrators.my_new_orchestrator import MyNewOrchestrator


@pytest.fixture
def temp_cortex_root(tmp_path):
    """Create temporary CORTEX structure."""
    (tmp_path / "cortex-brain").mkdir()
    return tmp_path


def test_end_to_end_workflow(temp_cortex_root):
    """Test complete workflow from start to finish."""
    orch = MyNewOrchestrator(cortex_root=str(temp_cortex_root))
    
    # Execute workflow
    result = orch.execute_workflow("complete test")
    
    # Verify success
    assert result["success"] == True
    
    # Verify files created (if applicable)
    # assert (temp_cortex_root / "expected_file.txt").exists()
```

---

## Dependency Injection Pattern (V2)

For orchestrators that depend on other orchestrators, use the V2 dependency injection pattern:

```python
class MyOrchestratorV2:
    """
    V2 with dependency injection.
    
    Improvements over V1:
    - Dependencies injected via constructor (testable)
    - Protocol-based interfaces (mockable)
    - Shared configuration via OrchestratorConfig
    - No manual initialization code
    """
    
    def __init__(
        self,
        config: OrchestratorConfig,
        tdd_orchestrator: Optional[ITDDOrchestrator] = None,
        git_checkpoint: Optional[IGitCheckpointOrchestrator] = None
    ):
        """
        Initialize with injected dependencies.
        
        Args:
            config: Shared orchestrator configuration
            tdd_orchestrator: TDD orchestrator (injected for testing)
            git_checkpoint: Git checkpoint (injected for testing)
        """
        self.config = config
        self.tdd_orchestrator = tdd_orchestrator
        self.git_checkpoint = git_checkpoint
```

**Benefits:**
- ✅ Testable (inject mocks)
- ✅ No redundant initialization
- ✅ Shared configuration
- ✅ Protocol-based (no tight coupling)

---

## Common Patterns

### Pattern 1: Checkpoint-Driven Workflow

For multi-phase workflows with user approval:

```python
def execute_incremental(
    self,
    user_input: str,
    checkpoint_callback: Optional[Callable[[str], bool]] = None
) -> Dict[str, Any]:
    """Execute with user checkpoints."""
    
    # Phase 1: Generate skeleton
    skeleton = self._generate_skeleton(user_input)
    
    if checkpoint_callback:
        approved = checkpoint_callback("Phase 1 complete. Continue?")
        if not approved:
            return {"success": False, "message": "User cancelled"}
    
    # Phase 2: Fill details
    details = self._fill_details(skeleton)
    
    if checkpoint_callback:
        approved = checkpoint_callback("Phase 2 complete. Finalize?")
        if not approved:
            return {"success": False, "message": "User cancelled"}
    
    # Phase 3: Finalize
    result = self._finalize(details)
    
    return {"success": True, "result": result}
```

### Pattern 2: File Organization

Always use the document organizer for proper file placement:

```python
from src.workflows.document_organizer import DocumentOrganizer

class MyOrchestrator:
    def __init__(self, cortex_root: str):
        self.document_organizer = DocumentOrganizer(Path(cortex_root))
    
    def save_output(self, content: str, filename: str):
        """Save output with automatic organization."""
        path, message = self.document_organizer.organize_document(
            filename=filename,
            content=content,
            category="reports"  # or planning, analysis, etc.
        )
        return path
```

### Pattern 3: Learning System Integration

Emit learning events for pattern recognition:

```python
from src.learning.event_collector import get_global_collector
from src.learning.event_taxonomy import LearningEvent, EventType

def execute_workflow(self, user_input: str) -> Dict[str, Any]:
    """Execute with learning."""
    collector = get_global_collector()
    
    # Emit start event
    collector.collect_event(
        LearningEvent(
            event_type=EventType.WORKFLOW_START,
            operation_id="my_operation",
            context={"input": user_input}
        )
    )
    
    # Execute workflow
    result = self._process_workflow(user_input)
    
    # Emit completion event
    collector.collect_event(
        LearningEvent(
            event_type=EventType.WORKFLOW_COMPLETE,
            operation_id="my_operation",
            context={"success": result["success"]}
        )
    )
    
    return result
```

---

## Orchestrator Lifecycle

```
1. User Request
   └─> "create my feature"

2. IntentRouter
   └─> Classifies intent (PLAN, TDD, CLEANUP, etc.)

3. route_operation()
   └─> Looks up operation_id in cortex-operations.yaml
   └─> Checks execution_method

4. Execution Method Dispatch
   ├─> cli_wrapper: invoke_cli_wrapper()
   │   └─> Runs CLI wrapper script
   │       └─> Instantiates orchestrator
   │           └─> Executes workflow
   │
   ├─> copilot_chat: Returns chat metadata
   │   └─> Copilot Chat invokes orchestrator directly
   │       └─> Interactive workflow
   │
   └─> internal: Rejects (not user-invokable)

5. Orchestrator Execution
   └─> Workflow phases execute
   └─> Results returned

6. Response Formatting
   └─> ResponseFormatter renders output
   └─> User sees formatted response
```

---

## Migration Guide: V1 → V2

If migrating an existing orchestrator to V2 pattern:

**Before (V1):**
```python
class MyOrchestrator:
    def __init__(self, cortex_root: str):
        self.cortex_root = Path(cortex_root)
        
        # Manual initialization (80+ lines)
        try:
            from src.orchestrators.tdd_implementation_orchestrator import TDDImplementationOrchestrator
            self.tdd = TDDImplementationOrchestrator(cortex_root, cortex_root)
        except ImportError:
            self.tdd = None
        
        # Repeat for each dependency...
```

**After (V2):**
```python
class MyOrchestratorV2:
    def __init__(
        self,
        config: OrchestratorConfig,
        tdd_orchestrator: Optional[ITDDOrchestrator] = None
    ):
        self.config = config
        self.tdd_orchestrator = tdd_orchestrator  # Injected!
```

**Factory Usage:**
```python
# Create via factory (dependencies auto-injected)
factory = OrchestratorFactory(config)
orchestrator = factory.get_my_orchestrator()
```

---

## Best Practices

### ✅ DO

1. **Use dependency injection** for orchestrators that call other orchestrators
2. **Emit learning events** for pattern recognition
3. **Use DocumentOrganizer** for file placement
4. **Add comprehensive docstrings** with examples
5. **Write unit AND integration tests**
6. **Use Protocol interfaces** for testability
7. **Handle exceptions gracefully** with clear error messages
8. **Log at appropriate levels** (INFO for progress, ERROR for failures)

### ❌ DON'T

1. **Don't bypass the routing system** - always go through route_operation()
2. **Don't create root-level files** - use DocumentOrganizer
3. **Don't manually initialize dependencies** - use OrchestratorFactory
4. **Don't mix user/CORTEX code** - respect git isolation
5. **Don't skip tests** - both unit and integration required
6. **Don't hard-code paths** - use config.cortex_root, config.project_root
7. **Don't ignore execution_method** - it determines how orchestrator is called

---

## Debugging Orchestrators

### Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Directly

```python
# Test orchestrator without routing
from src.orchestrators.my_new_orchestrator import MyNewOrchestrator

orch = MyNewOrchestrator(cortex_root="/path/to/CORTEX")
result = orch.execute_workflow("test input")
print(result)
```

### Test via CLI Wrapper

```bash
python scripts/cli_wrappers/my_operation_wrapper.py \
  --project-root /path/to/project \
  --output json \
  --verbose
```

### Test via Routing System

```python
from pathlib import Path
from src.operations.modules.routing.unified_entry_point_utility import route_operation

result = route_operation(
    operation_id="my_operation",
    cortex_root=Path("/path/to/CORTEX"),
    operation_config={
        "execution_method": "cli_wrapper",
        "cli_script": "scripts/cli_wrappers/my_operation_wrapper.py"
    }
)
print(result)
```

---

## Example: Full Orchestrator Implementation

See reference implementations:
- **Planning System:** `src/orchestrators/planning_orchestrator.py` (2852 lines, full-featured)
- **TDD Mastery:** `src/orchestrators/tdd_implementation_orchestrator.py` (197 lines, state machine)
- **Cleanup:** `src/operations/modules/orchestration/cleanup_orchestrator.py` (50 lines, simple)

---

## Summary

**Key Takeaways:**
1. Orchestrators are **implementation**, not routing
2. Routing system (`route_operation()`) dispatches to orchestrators
3. Use V2 dependency injection pattern for new orchestrators
4. Register in `cortex-operations.yaml` with proper `execution_method`
5. Test thoroughly (unit + integration)
6. Follow common patterns (checkpoints, document organization, learning)

**Quick Checklist:**
- [ ] Determined execution_method (cli_wrapper|copilot_chat|internal)
- [ ] Created orchestrator class with proper base class
- [ ] Registered in cortex-operations.yaml
- [ ] Created CLI wrapper (if cli_wrapper)
- [ ] Added to OrchestratorFactory (if needed)
- [ ] Wrote unit tests
- [ ] Wrote integration tests
- [ ] Added comprehensive docstrings
- [ ] Tested end-to-end

---

**Questions?** See `src/orchestrators/README.md` or `.github/prompts/CORTEX.prompt.md`
