# AC-FILENAME-FACTORY-INTEGRATION: Master Orchestrator Wiring Guide

**Authority:** CORTEX Master Orchestrator | **Phase:** Integration Ready | **Date:** 2026-01-25

---

## 🎯 Objective

Wire FilenameFactory system into Master Orchestrator to enforce CORE-028/CORE-038 on ALL file creation with zero exceptions.

---

## 🔌 Integration Points

### 1. IntentRouter Enhancement

Add FILE_CREATION as new IntentType:

```python
class IntentType(Enum):
    # ... existing types ...
    FILE_CREATION = "file_creation"  # ← NEW
```

Add FILE_CREATION to routing rules:

```python
ROUTING_RULES = {
    # ... existing rules ...
    IntentType.FILE_CREATION: {
        "handler": "FilenameFactory",
        "priority": "critical",
        "phases": ["validate_filename", "validate_path", "suggest_fix"],
    }
}
```

### 2. MasterOrchestrator Stage 3 Extension

Add FILE_CREATION intent handling:

```python
# In MasterOrchestrator.route_intent()
if intent_type == IntentType.FILE_CREATION:
    # Extract file parameters from context
    filename = context.get("filename")
    filepath = context.get("filepath")
    file_type = context.get("file_type")
    
    # Validate
    name_result = self.filename_validator.validate(filename)
    path_result = self.path_enforcer.validate_path(Path(filepath), file_type)
    
    # Block if violations
    if not name_result.is_valid or not path_result.is_valid:
        return self._build_violation_response(
            name_violations=name_result.violations,
            path_violations=path_result.violations,
            filename=filename,
            filepath=filepath
        )
    
    # Allow and log
    self.audit_logger.log_file_creation_approved(filename, filepath)
    return Ok({"action": "allow", "path": filepath})
```

### 3. Pre-Write Hook Integration

Add to file write operations:

```python
# In cortex/infrastructure/file_manager.py or similar
async def write_file(path: Path, content: str) -> Result:
    """Write file with governance validation."""
    
    # Stage 1: Validate filename
    filename_result = validator.validate(path.name)
    if not filename_result.is_valid:
        violations = format_violations(filename_result.violations)
        return Err(f"CORE-028 violation: {violations}")
    
    # Stage 2: Validate path placement
    path_result = enforcer.validate_path(path, path.suffix.lstrip("."))
    if not path_result.is_valid:
        violations = format_violations(path_result.violations)
        return Err(f"CORE-038 violation: {violations}")
    
    # Stage 3: Log to audit trail
    audit_logger.log_ac_start(ac_id="AC_FILE_WRITE", details={
        "filename": path.name,
        "filepath": str(path),
        "action": "write"
    })
    
    try:
        # Stage 4: Perform write
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        
        # Stage 5: Log completion
        audit_logger.log_ac_complete(ac_id="AC_FILE_WRITE", result="success")
        return Ok({"path": str(path), "status": "created"})
    
    except Exception as e:
        audit_logger.log_ac_complete(ac_id="AC_FILE_WRITE", result=f"error: {e}")
        return Err(f"Write failed: {e}")
```

### 4. Violation Response Format

Standardize violation responses:

```python
@dataclass
class FileCreationViolationResponse:
    """Response when file creation violates governance."""
    success: bool = False
    action: str = "blocked"
    violations: Dict[str, List[Dict]] = field(default_factory=dict)
    suggestions: Dict[str, str] = field(default_factory=dict)
    remediation_steps: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to user-friendly format."""
        return {
            "success": False,
            "status": "BLOCKED",
            "violations": self.violations,
            "suggestions": self.suggestions,
            "next_steps": self.remediation_steps,
            "rule": "CORE-028 (filename) / CORE-038 (placement)"
        }


def build_violation_response(
    filename_violations: List[NamingViolation],
    path_violations: List[PlacementViolation],
    filename: str,
    filepath: str
) -> FileCreationViolationResponse:
    """Build user-friendly violation response."""
    
    # Format naming violations
    naming_violations = [
        {
            "code": v.code,
            "message": v.message,
            "suggestion": v.suggestion,
            "rule": "CORE-028"
        }
        for v in filename_violations
    ]
    
    # Format path violations
    placement_violations = [
        {
            "code": v.code,
            "message": v.message,
            "suggested_path": v.suggested_path,
            "rule": "CORE-038"
        }
        for v in path_violations
    ]
    
    # Build remediation steps
    steps = []
    if filename_violations:
        steps.append(f"Rename file to: {filename_violations[0].suggestion}")
    if path_violations:
        steps.append(f"Move to: {path_violations[0].suggested_path}")
    
    return FileCreationViolationResponse(
        violations={
            "naming": naming_violations,
            "placement": placement_violations
        },
        suggestions={
            "filename": filename_violations[0].suggestion if filename_violations else None,
            "filepath": path_violations[0].suggested_path if path_violations else None
        },
        remediation_steps=steps
    )
```

---

## 🔗 Wiring Checklist

### Step 1: Add Dependencies to Master Orchestrator

```python
# In master_orchestrator.py imports
from cortex.governance.filename_factory import (
    FilenameValidator,
    FilenameFactory,
    FilePathEnforcer,
)

# In MasterOrchestrator.__init__()
self.filename_validator = FilenameValidator()
self.filename_factory = FilenameFactory()
self.file_path_enforcer = FilePathEnforcer()
```

### Step 2: Register FILE_CREATION Intent

```python
# In IntentRouter.classify_intent()
if "file" in description.lower() and ("create" in description.lower() or "write" in description.lower()):
    return IntentType.FILE_CREATION
```

### Step 3: Add FILE_CREATION Handler

```python
# In MasterOrchestrator.execute_stage_3()
if intent_type == IntentType.FILE_CREATION:
    result = self._handle_file_creation(operation_context)
    return result
```

### Step 4: Create File Creation Handler Method

```python
def _handle_file_creation(self, context: OperationContext) -> Result:
    """Handle FILE_CREATION intent with governance enforcement."""
    
    # Extract parameters
    filename = context.get("filename")
    filepath = context.get("filepath")
    file_type = context.get("file_type")
    
    # Validate
    return self._validate_and_handle_file(filename, filepath, file_type)

def _validate_and_handle_file(
    self,
    filename: str,
    filepath: str,
    file_type: str
) -> Result:
    """Validate file against CORE-028/CORE-038."""
    
    # Validate filename
    filename_result = self.filename_validator.validate(filename)
    
    # Validate path
    path_result = self.file_path_enforcer.validate_path(
        Path(filepath),
        file_type
    )
    
    # Check for violations
    all_violations = (
        (filename_result.violations if not filename_result.is_valid else []) +
        (path_result.violations if not path_result.is_valid else [])
    )
    
    if all_violations:
        # Log violation
        self.audit_logger.log_governance_violation(
            ac_id="AC_FILE_CREATION_BLOCKED",
            violations=[{
                "code": v.code,
                "message": v.message,
                "suggested_fix": getattr(v, 'suggestion', None) or getattr(v, 'suggested_path', None)
            } for v in all_violations]
        )
        
        # Build response
        response = build_violation_response(
            filename_violations=filename_result.violations,
            path_violations=path_result.violations,
            filename=filename,
            filepath=filepath
        )
        return Err(response.to_dict())
    
    # Log approval
    self.audit_logger.log_ac_start(
        ac_id="AC_FILE_CREATION_APPROVED",
        details={"filename": filename, "filepath": filepath}
    )
    
    return Ok({
        "action": "allow_creation",
        "filename": filename,
        "filepath": filepath,
        "rule_compliance": {
            "CORE-028": "PASS",
            "CORE-038": "PASS"
        }
    })
```

### Step 5: Wire MCP Tools

Register the MCP tools for Claude integration:

```python
# In MasterOrchestrator.expose_mcp_tools()
mcp_tools = [
    "suggest-compliant-filename",
    "validate-filename",
    "validate-filepath",
    "suggest-compliant-path",
]
self.mcp_registry.register_tools(mcp_tools)
```

---

## 🧪 Integration Test Cases

### Test 1: Valid File Creation

```python
def test_valid_file_creation():
    """FILE_CREATION intent with compliant filename/path."""
    orchestrator = MasterOrchestrator.instance()
    
    result = orchestrator.execute({
        "intent": "FILE_CREATION",
        "filename": "cortex-vacuum-exec.py",
        "filepath": "/cortex/governance/cortex-vacuum-exec.py",
        "file_type": "py"
    })
    
    assert result.is_ok()
    assert result.value["action"] == "allow_creation"
```

### Test 2: Invalid Filename (CamelCase)

```python
def test_invalid_filename_camelcase():
    """FILE_CREATION intent with CamelCase filename."""
    orchestrator = MasterOrchestrator.instance()
    
    result = orchestrator.execute({
        "intent": "FILE_CREATION",
        "filename": "CortexVacuumExecutor.py",
        "filepath": "/cortex/governance/CortexVacuumExecutor.py",
        "file_type": "py"
    })
    
    assert result.is_err()
    error = result.err()
    assert error["violations"]["naming"]
    assert error["suggestions"]["filename"] == "cortex-vacuum-executor.py"
```

### Test 3: Invalid Path (Root Level)

```python
def test_invalid_path_root_level():
    """FILE_CREATION intent with root-level file."""
    orchestrator = MasterOrchestrator.instance()
    
    result = orchestrator.execute({
        "intent": "FILE_CREATION",
        "filename": "cortex-vacuum-exec.py",
        "filepath": "/cortex/cortex-vacuum-exec.py",  # NOT in subfolder
        "file_type": "py"
    })
    
    assert result.is_err()
    error = result.err()
    assert error["violations"]["placement"]
    assert error["suggestions"]["filepath"].startswith("/cortex/governance/")
```

### Test 4: Suggestion Flow

```python
def test_suggestion_flow():
    """User gets suggestions when attempting invalid file creation."""
    orchestrator = MasterOrchestrator.instance()
    
    # Invalid attempt
    result = orchestrator.execute({
        "intent": "FILE_CREATION",
        "filename": "CortexVacuum_Executor.py",
        "filepath": "/cortex/cortex-file.py",
        "file_type": "py"
    })
    
    assert result.is_err()
    error = result.err()
    
    # Verify suggestions
    assert "remediation_steps" in error
    assert len(error["remediation_steps"]) > 0
    assert error["suggestions"]["filename"]
    assert error["suggestions"]["filepath"]
```

---

## 📊 Audit Trail Integration

All FILE_CREATION operations logged:

```python
# Successful creation
{
    "ac_id": "AC_FILE_CREATION_APPROVED",
    "timestamp": "2026-01-25T10:30:00Z",
    "filename": "cortex-vacuum-exec.py",
    "filepath": "/cortex/governance/cortex-vacuum-exec.py",
    "validation": {
        "CORE-028": "PASS",
        "CORE-038": "PASS"
    },
    "action": "allow_creation",
    "status": "success"
}

# Failed creation
{
    "ac_id": "AC_FILE_CREATION_BLOCKED",
    "timestamp": "2026-01-25T10:30:00Z",
    "filename": "CortexVacuum.py",
    "filepath": "/cortex/CortexVacuum.py",
    "violations": [
        {
            "code": "CORE-028",
            "message": "Must use kebab-case",
            "suggestion": "cortex-vacuum.py"
        },
        {
            "code": "CORE-038",
            "message": "Must be in subfolder",
            "suggested_path": "/cortex/governance/cortex-vacuum.py"
        }
    ],
    "action": "block_creation",
    "status": "blocked"
}
```

---

## 🚀 Deployment Steps

1. **Merge AC-FILENAME-FACTORY-001** → Ensures factory is available
2. **Update IntentRouter** → Add FILE_CREATION intent type
3. **Update MasterOrchestrator** → Add FILE_CREATION handler
4. **Test integration** → Run integration test suite
5. **Wire pre-write hook** → Add to file write operations
6. **Enable audit logging** → Capture all decisions
7. **Deploy to production** → Enable factory-based enforcement
8. **Monitor violations** → Track governance decisions

---

## 📞 Success Criteria

- ✅ FILE_CREATION intent routed correctly
- ✅ Invalid filenames blocked with suggestions
- ✅ Invalid paths blocked with suggestions
- ✅ Valid files created successfully
- ✅ All decisions logged to audit trail
- ✅ MCP tools discoverable and functional
- ✅ Zero exceptions to enforcement
- ✅ No files bypass validation

---

**Status:** INTEGRATION READY  
**Dependencies:** AC-FILENAME-FACTORY-001 (COMPLETE)  
**Next Phase:** Master Orchestrator wiring
