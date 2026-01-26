# Phase 2 Adapter Implementation Guide - Step-by-Step

**Date:** 2026-01-26  
**AC-ID:** AC-MCP-ORCHESTRATOR-002  
**Status:** 🟡 IMPLEMENTATION READY

---

## 🎯 Quick Start: Creating Your First Adapter

### Step 1: Choose Your Orchestrator
Start with **MasterOrchestrator** as the first adapter (most straightforward).

### Step 2: Understand the Pattern

All adapters follow this simple 4-method interface:

```python
class {Name}OrchestratorAdapter(IOrchestratorAdapter):
    """MCP adapter for {Name}Orchestrator"""
    
    def __init__(self, orchestrator: {OrchestratorClass}):
        self.orchestrator = orchestrator
        self._logger = logging.getLogger(self.__class__.__name__)
    
    def get_capabilities(self) -> List[CapabilityMetadata]:
        """Expose orchestrator capabilities"""
        # Return list of CapabilityMetadata
    
    def execute_capability(
        self,
        capability_name: str,
        parameters: Dict[str, Any],
        context: ExecutionContext
    ) -> CapabilityResponse:
        """Execute a capability"""
        # Call orchestrator method, return result
    
    def is_healthy(self) -> bool:
        """Check if orchestrator is healthy"""
        # Return health status
    
    def get_status(self) -> Dict[str, Any]:
        """Get detailed status information"""
        # Return status dict
```

---

## 📋 MasterOrchestratorAdapter - Complete Example

This is your template. Copy this pattern for all other adapters.

### File Location
Add to: `/Users/asifhussain/PROJECTS/CORTEX/cortex/orchestrators/core/master_orchestrator.py`

**Add at the end of the file (after MasterOrchestrator class):**

```python
# ============================================================================
# MCP Adapter for MasterOrchestrator (AC-MCP-ORCHESTRATOR-002)
# ============================================================================

class MasterOrchestratorAdapter(IOrchestratorAdapter):
    """
    MCP adapter for MasterOrchestrator.
    
    Exposes master orchestrator capabilities via MCP for:
    - Operation execution with governance
    - Status reporting
    - Orchestrator delegation
    """
    
    def __init__(self, orchestrator: MasterOrchestrator):
        """Initialize adapter with MasterOrchestrator instance"""
        self.orchestrator = orchestrator
        self._logger = logging.getLogger(self.__class__.__name__)
    
    def get_capabilities(self) -> List['CapabilityMetadata']:
        """
        Expose MasterOrchestrator capabilities.
        
        Returns:
            List of CapabilityMetadata for all exposed capabilities
        """
        from cortex.mcp import CapabilityMetadata
        
        return [
            CapabilityMetadata(
                name="master/execute_operation",
                orchestrator="master_orchestrator",
                description="Execute a CORTEX operation with full governance enforcement",
                input_schema={
                    "type": "object",
                    "properties": {
                        "intent": {
                            "type": "string",
                            "description": "The operation intent (implement, fix, test, etc.)"
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Operation-specific parameters"
                        }
                    },
                    "required": ["intent"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "result": {"type": ["object", "null"]},
                        "error": {"type": ["string", "null"]},
                        "execution_time_ms": {"type": "number"},
                        "audit_trail": {"type": "object"}
                    }
                },
                routing_keywords=["execute", "orchestrate", "master", "operation"],
                confidence_threshold=0.95,
                tags={"core", "orchestration", "governance"}
            ),
            CapabilityMetadata(
                name="master/get_status",
                orchestrator="master_orchestrator",
                description="Get current MasterOrchestrator status and health",
                input_schema={"type": "object", "properties": {}},
                output_schema={
                    "type": "object",
                    "properties": {
                        "healthy": {"type": "boolean"},
                        "domain_orchestrators": {"type": "integer"},
                        "operations_processed": {"type": "integer"},
                        "last_operation": {"type": ["string", "null"]},
                        "details": {"type": "object"}
                    }
                },
                routing_keywords=["status", "health", "master"],
                confidence_threshold=0.9,
                tags={"core", "monitoring"}
            ),
            CapabilityMetadata(
                name="master/validate_operation",
                orchestrator="master_orchestrator",
                description="Validate operation intent and parameters before execution",
                input_schema={
                    "type": "object",
                    "properties": {
                        "intent": {"type": "string"},
                        "parameters": {"type": "object"}
                    },
                    "required": ["intent"]
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "valid": {"type": "boolean"},
                        "errors": {"type": "array"},
                        "warnings": {"type": "array"},
                        "governance_violations": {"type": "array"}
                    }
                },
                routing_keywords=["validate", "check", "governance"],
                confidence_threshold=0.85,
                tags={"core", "validation", "governance"}
            ),
        ]
    
    def execute_capability(
        self,
        capability_name: str,
        parameters: Dict[str, Any],
        context: 'ExecutionContext'
    ) -> 'CapabilityResponse':
        """
        Execute a MasterOrchestrator capability.
        
        Args:
            capability_name: Name of capability to execute
            parameters: Input parameters for capability
            context: Execution context (repo, user, session info)
        
        Returns:
            CapabilityResponse with result or error
        """
        from cortex.mcp import CapabilityResponse
        from datetime import datetime
        
        import time
        start_time = time.time()
        
        try:
            if capability_name == "master/execute_operation":
                # Execute the operation
                intent = parameters.get("intent")
                op_params = parameters.get("parameters", {})
                
                if not intent:
                    return CapabilityResponse(
                        request_id=context.session_id,
                        success=False,
                        error="Missing 'intent' parameter",
                        error_code="INVALID_PARAMS",
                        duration_ms=(time.time() - start_time) * 1000,
                        orchestrator="master_orchestrator",
                        execution_timestamp=datetime.now(),
                        metadata={"capability": capability_name}
                    )
                
                # Call orchestrator
                result = self.orchestrator.execute_operation(intent, op_params)
                
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=True,
                    result={
                        "operation_result": result,
                        "intent": intent
                    },
                    duration_ms=(time.time() - start_time) * 1000,
                    orchestrator="master_orchestrator",
                    execution_timestamp=datetime.now(),
                    metadata={
                        "capability": capability_name,
                        "context_type": context.context_type.value
                    }
                )
            
            elif capability_name == "master/get_status":
                # Get status
                status = self.orchestrator.get_status()
                
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=True,
                    result=status,
                    duration_ms=(time.time() - start_time) * 1000,
                    orchestrator="master_orchestrator",
                    execution_timestamp=datetime.now(),
                    metadata={"capability": capability_name}
                )
            
            elif capability_name == "master/validate_operation":
                # Validate operation
                intent = parameters.get("intent")
                op_params = parameters.get("parameters", {})
                
                # Simple validation
                errors = []
                warnings = []
                governance_violations = []
                
                if not intent:
                    errors.append("Missing 'intent' parameter")
                
                valid = len(errors) == 0
                
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=True,
                    result={
                        "valid": valid,
                        "errors": errors,
                        "warnings": warnings,
                        "governance_violations": governance_violations
                    },
                    duration_ms=(time.time() - start_time) * 1000,
                    orchestrator="master_orchestrator",
                    execution_timestamp=datetime.now(),
                    metadata={"capability": capability_name}
                )
            
            else:
                # Unknown capability
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=False,
                    error=f"Unknown capability: {capability_name}",
                    error_code="UNKNOWN_CAPABILITY",
                    duration_ms=(time.time() - start_time) * 1000,
                    orchestrator="master_orchestrator",
                    execution_timestamp=datetime.now(),
                    metadata={"capability": capability_name}
                )
        
        except Exception as e:
            self._logger.error(f"Error executing {capability_name}: {e}", exc_info=True)
            
            return CapabilityResponse(
                request_id=context.session_id,
                success=False,
                error=str(e),
                error_code="EXECUTION_ERROR",
                duration_ms=(time.time() - start_time) * 1000,
                orchestrator="master_orchestrator",
                execution_timestamp=datetime.now(),
                metadata={
                    "capability": capability_name,
                    "error_type": type(e).__name__
                }
            )
    
    def is_healthy(self) -> bool:
        """
        Check if MasterOrchestrator is healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            status = self.orchestrator.get_status()
            return status.get("healthy", False)
        except Exception as e:
            self._logger.error(f"Health check failed: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get detailed MasterOrchestrator status.
        
        Returns:
            Status dictionary with health and operational details
        """
        try:
            return self.orchestrator.get_status()
        except Exception as e:
            self._logger.error(f"Failed to get status: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "message": "Failed to retrieve status"
            }
```

---

## 📝 Imports Required at Top of File

Add these imports to `master_orchestrator.py` if not already present:

```python
from typing import List, Dict, Any
from datetime import datetime
import time
from cortex.mcp import IOrchestratorAdapter, CapabilityResponse, ExecutionContext, CapabilityMetadata
```

---

## 🔄 Pattern for Other Orchestrators

### TDDOrchestratorAdapter Example

Add to: `/Users/asifhussain/PROJECTS/CORTEX/cortex/orchestrators/core/tdd_orchestrator.py`

```python
class TDDOrchestratorAdapter(IOrchestratorAdapter):
    """MCP adapter for TDDOrchestrator"""
    
    def __init__(self, orchestrator: TDDOrchestrator):
        self.orchestrator = orchestrator
        self._logger = logging.getLogger(self.__class__.__name__)
    
    def get_capabilities(self) -> List[CapabilityMetadata]:
        """Expose TDD capabilities"""
        from cortex.mcp import CapabilityMetadata
        
        return [
            CapabilityMetadata(
                name="tdd/generate_tests",
                orchestrator="tdd_orchestrator",
                description="Generate unit tests for code",
                input_schema={
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Code to test"},
                        "test_framework": {"type": "string", "description": "pytest, unittest, etc."}
                    },
                    "required": ["code"]
                },
                output_schema={"type": "object"},
                routing_keywords=["test", "tdd", "unit", "generate"],
                confidence_threshold=0.9,
                tags={"core", "testing", "tdd"}
            ),
            CapabilityMetadata(
                name="tdd/run_tests",
                orchestrator="tdd_orchestrator",
                description="Run unit tests and report results",
                input_schema={
                    "type": "object",
                    "properties": {
                        "test_path": {"type": "string", "description": "Path to tests"},
                        "framework": {"type": "string", "description": "Test framework"}
                    },
                    "required": ["test_path"]
                },
                output_schema={"type": "object"},
                routing_keywords=["run", "execute", "test"],
                confidence_threshold=0.9,
                tags={"core", "testing"}
            ),
        ]
    
    def execute_capability(
        self,
        capability_name: str,
        parameters: Dict[str, Any],
        context: ExecutionContext
    ) -> CapabilityResponse:
        """Execute TDD capability"""
        from cortex.mcp import CapabilityResponse
        from datetime import datetime
        import time
        
        start_time = time.time()
        
        try:
            if capability_name == "tdd/generate_tests":
                code = parameters.get("code")
                framework = parameters.get("test_framework", "pytest")
                
                result = self.orchestrator.generate_tests(code, framework)
                
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=True,
                    result={"tests": result},
                    duration_ms=(time.time() - start_time) * 1000,
                    orchestrator="tdd_orchestrator",
                    execution_timestamp=datetime.now(),
                    metadata={"capability": capability_name}
                )
            
            else:
                return CapabilityResponse(
                    request_id=context.session_id,
                    success=False,
                    error=f"Unknown capability: {capability_name}",
                    error_code="UNKNOWN_CAPABILITY",
                    duration_ms=(time.time() - start_time) * 1000,
                    orchestrator="tdd_orchestrator",
                    execution_timestamp=datetime.now()
                )
        
        except Exception as e:
            self._logger.error(f"Error: {e}", exc_info=True)
            
            return CapabilityResponse(
                request_id=context.session_id,
                success=False,
                error=str(e),
                error_code="EXECUTION_ERROR",
                duration_ms=(time.time() - start_time) * 1000,
                orchestrator="tdd_orchestrator",
                execution_timestamp=datetime.now()
            )
    
    def is_healthy(self) -> bool:
        """Check health"""
        try:
            return self.orchestrator.is_healthy()
        except:
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get status"""
        try:
            return self.orchestrator.get_status()
        except Exception as e:
            return {"healthy": False, "error": str(e)}
```

---

## ✅ Checklist for Each Adapter

- [ ] Adapter class created with 4 required methods
- [ ] `get_capabilities()` returns list of CapabilityMetadata (2-5 capabilities minimum)
- [ ] `execute_capability()` properly routes to orchestrator methods
- [ ] Error handling for unknown capabilities
- [ ] Error handling for execution exceptions
- [ ] `is_healthy()` checks orchestrator status
- [ ] `get_status()` returns detailed status dict
- [ ] All type hints present (100% coverage)
- [ ] Google-style docstrings on all methods
- [ ] 0 lint errors (Pylance strict)
- [ ] Proper imports at top of file
- [ ] ExecutionContext properly used and passed
- [ ] Execution timing measured and reported
- [ ] Request ID and session ID tracked

---

## 🔍 Testing Your Adapter

Create a simple test:

```python
# In tests/orchestrators/test_mcp_adapters.py

from cortex.mcp import ExecutionContext, CapabilityRequest, ContextType
from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator, MasterOrchestratorAdapter

def test_master_adapter_capabilities():
    """Test MasterOrchestratorAdapter capability discovery"""
    master = MasterOrchestrator()
    adapter = MasterOrchestratorAdapter(master)
    
    capabilities = adapter.get_capabilities()
    
    assert len(capabilities) > 0
    assert any(c.name == "master/execute_operation" for c in capabilities)
    assert all(hasattr(c, 'name') and hasattr(c, 'description') for c in capabilities)

def test_master_adapter_execute():
    """Test MasterOrchestratorAdapter execution"""
    master = MasterOrchestrator()
    adapter = MasterOrchestratorAdapter(master)
    
    context = ExecutionContext(
        context_type=ContextType.SINGLE_REPO,
        repository_path="/tmp/test"
    )
    
    request = CapabilityRequest(
        capability_name="master/get_status",
        parameters={},
        context=context
    )
    
    response = adapter.execute_capability(
        request.capability_name,
        request.parameters,
        context
    )
    
    assert response.success
    assert response.orchestrator == "master_orchestrator"
    assert response.duration_ms > 0

def test_master_adapter_health():
    """Test MasterOrchestratorAdapter health check"""
    master = MasterOrchestrator()
    adapter = MasterOrchestratorAdapter(master)
    
    healthy = adapter.is_healthy()
    assert isinstance(healthy, bool)
    
    status = adapter.get_status()
    assert isinstance(status, dict)
```

---

## 🚀 Next Steps After Creating First Adapter

1. ✅ Create MasterOrchestratorAdapter (THIS SECTION)
2. ⏳ Test it in isolation
3. ⏳ Create TDDOrchestratorAdapter
4. ⏳ Create IntentRouterAdapter
5. ⏳ Create remaining 20 adapters
6. ⏳ Wire into bootstrap sequence
7. ⏳ Create integration tests
8. ⏳ API/CLI endpoints

---

## 📊 Expected Results After First 3 Adapters

```
✅ 3 adapters created & tested
✅ 9+ capabilities exposed
✅ Capability discovery working
✅ Execution routing working
✅ Health monitoring working
✅ Ready to scale to remaining 20 adapters
```

---

## Need Help?

- **Integration Guide:** `docs/ac-mcp-orchestrator-integration-guide.md`
- **Integration Roadmap:** `docs/priority-2-integration-roadmap.md`
- **System Status:** `docs/cortex-system-status-report-2026-01-26.md`
- **MCP Server:** `cortex/mcp/orchestrator_mcp_server.py` (reference implementation)

