# Class Diagrams - Toolkit Manager

**Document:** Artifacts - UML Class Diagrams  
**Created:** December 31, 2025  
**Author:** Asif Hussain

---

## 📊 Core Architecture (Mermaid)

```mermaid
classDiagram
    class ToolkitManager {
        -ToolkitRegistry registry
        -GateKeeper gate_keeper
        -RequestAnalyzer request_analyzer
        -RecoveryManager recovery_manager
        -DependencyManager dependency_manager
        -AuditLogger audit_logger
        +execute(tool, args, context) ExecutionResult
        +can_create_tool(spec) CreationCheck
        +register_tool(spec) bool
        +list_tools(category) List~Dict~
    }

    class GateKeeper {
        -ToolkitRegistry registry
        -SecurityGuard security
        -rate_limits Dict
        +validate_execution(tool, args) ValidationResult
        -_check_tool_exists(tool) Check
        -_check_platform_support(tool) Check
        -_check_dependencies(tool) Check
        -_check_permissions(tool) Check
        -_check_rate_limit(tool) Check
        -_sanitize_arguments(args) Check
    }

    class RequestAnalyzer {
        -ToolkitRegistry registry
        -CapabilityMatrix capability_matrix
        +analyze_request(request) AnalysisResult
        +find_overlapping_tools(capability) List~ToolMatch~
        -_extract_intent(description) List~str~
        -_calculate_similarity(caps1, caps2) float
        -_generate_recommendation(overlaps) str
    }

    class CapabilityMatrix {
        -Dict~str,List~ CAPABILITY_KEYWORDS
        -Dict~str,List~ tool_capabilities
        +find_overlaps(intent) List~ToolMatch~
        +get_tool_capabilities(tool) List~str~
        +add_tool_capabilities(tool, caps) void
    }

    class RecoveryManager {
        -Path toolkit_root
        -Path checkpoint_dir
        +create_checkpoint(context) Checkpoint
        +rollback(checkpoint_id) RollbackResult
        +list_checkpoints(limit) List~Checkpoint~
        -_capture_state(paths) Dict
        -_persist_checkpoint(checkpoint) void
        -_prune_old_checkpoints() void
    }

    class Checkpoint {
        +str id
        +datetime timestamp
        +str tool
        +List~str~ args
        +List~Path~ affected_paths
        +Optional~str~ git_sha
        +Dict~str,str~ state_snapshot
        +to_json() str
        +from_json(data) Checkpoint
    }

    class DependencyManager {
        -ToolkitRegistry registry
        -Dict~str,List~ graph
        +build_graph() Dict
        +detect_circular() List~List~
        +get_execution_order(tools) List~str~
        +validate_dependencies(tool) DependencyCheck
    }

    class SecurityGuard {
        -List~str~ FORBIDDEN_PATTERNS
        +sanitize_arguments(args) SanitizeResult
        +check_privilege_level(tool) bool
        -_match_patterns(arg) List~str~
    }

    class AuditLogger {
        -Path log_path
        +log_execution(event) void
        +log_security_event(event) void
        +get_recent_logs(limit) List~Dict~
        -_append_to_audit_log(record) void
        -_hash_args(args) str
    }

    class ToolkitRegistry {
        +Path toolkit_root
        +Dict manifest
        +str version
        +list_categories() List~str~
        +list_tools(category) List~Dict~
        +get_tool(name) Optional~Dict~
        +invoke_tool(name, args) int
    }

    ToolkitManager --> GateKeeper
    ToolkitManager --> RequestAnalyzer
    ToolkitManager --> RecoveryManager
    ToolkitManager --> DependencyManager
    ToolkitManager --> AuditLogger
    ToolkitManager --> ToolkitRegistry
    
    GateKeeper --> SecurityGuard
    GateKeeper --> ToolkitRegistry
    
    RequestAnalyzer --> CapabilityMatrix
    RequestAnalyzer --> ToolkitRegistry
    
    RecoveryManager --> Checkpoint
    
    DependencyManager --> ToolkitRegistry
```

---

## 📦 Data Classes

```mermaid
classDiagram
    class ExecutionContext {
        +Path project_root
        +str tool
        +List~str~ args
        +List~Path~ affected_paths
        +bool cli_mode
        +datetime timestamp
        +Optional~str~ user
    }

    class ExecutionResult {
        +str status
        +int exit_code
        +str output
        +str error
        +float duration_ms
        +Optional~str~ checkpoint_id
    }

    class ValidationResult {
        +bool passed
        +List~Check~ checks
        +List~str~ errors
        +List~str~ warnings
    }

    class Check {
        +str name
        +bool passed
        +str message
        +str severity
    }

    class AnalysisResult {
        +bool can_create
        +List~ToolMatch~ overlapping_tools
        +str recommendation
        +float highest_overlap
    }

    class ToolMatch {
        +str tool_name
        +List~str~ capabilities
        +float similarity
        +str recommendation
    }

    class ToolRequest {
        +str name
        +str description
        +List~str~ capabilities
        +str category
        +Dict metadata
    }

    class CreationCheck {
        +bool allowed
        +str reason
        +List~ToolMatch~ alternatives
    }

    class RollbackResult {
        +bool success
        +str message
        +List~Path~ restored_paths
        +List~str~ errors
    }

    class DependencyCheck {
        +bool satisfied
        +List~str~ missing
        +List~str~ circular
    }

    class SanitizeResult {
        +bool safe
        +List~SecurityViolation~ violations
    }

    class SecurityViolation {
        +int arg_index
        +str pattern
        +str severity
        +str description
    }
```

---

## 🔄 Sequence Diagram: Tool Execution

```mermaid
sequenceDiagram
    participant User
    participant Manager as ToolkitManager
    participant Gate as GateKeeper
    participant Security as SecurityGuard
    participant Recovery as RecoveryManager
    participant Registry as ToolkitRegistry
    participant Audit as AuditLogger

    User->>Manager: execute("align", ["--check"])
    
    Manager->>Gate: validate_execution("align", args)
    Gate->>Gate: _check_tool_exists()
    Gate->>Gate: _check_platform_support()
    Gate->>Security: sanitize_arguments(args)
    Security-->>Gate: SanitizeResult(safe=True)
    Gate-->>Manager: ValidationResult(passed=True)
    
    Manager->>Recovery: create_checkpoint(context)
    Recovery-->>Manager: Checkpoint(id="abc123")
    
    Manager->>Registry: invoke_tool("align", args)
    Registry-->>Manager: exit_code=0
    
    Manager->>Audit: log_execution(event)
    
    Manager-->>User: ExecutionResult(status="success")
```

---

## 🛡️ Sequence Diagram: Security Rejection

```mermaid
sequenceDiagram
    participant User
    participant Manager as ToolkitManager
    participant Gate as GateKeeper
    participant Security as SecurityGuard

    User->>Manager: execute("cleanup", ["; rm -rf /"])
    
    Manager->>Gate: validate_execution("cleanup", args)
    Gate->>Security: sanitize_arguments(args)
    Security->>Security: _match_patterns("; rm -rf /")
    Security-->>Gate: SanitizeResult(safe=False, violations=[...])
    Gate-->>Manager: ValidationResult(passed=False)
    
    Manager-->>User: ExecutionResult(status="blocked", error="Security violation")
```

---

## 📁 File Structure

```
cortex-toolkit/
├── core/
│   ├── __init__.py              # Public API exports
│   ├── toolkit_manager.py       # Phase 1: Central manager
│   ├── gate_keeper.py           # Phase 1: Validation
│   ├── exceptions.py            # Phase 1: Custom exceptions
│   ├── request_analyzer.py      # Phase 2: Duplication check
│   ├── capability_matrix.py     # Phase 2: Capability mapping
│   ├── recovery_manager.py      # Phase 3: Checkpoint/rollback
│   ├── checkpoint.py            # Phase 3: Checkpoint model
│   ├── dependency_manager.py    # Phase 4: Graph validation
│   ├── security_guard.py        # Phase 6: Input sanitization
│   └── audit_logger.py          # Phase 6: Audit trail
├── schemas/
│   └── manifest-v2.schema.json  # Phase 5: JSON Schema
├── migration/
│   └── migrate_manifest.py      # Phase 5: v1→v2 migration
├── logs/
│   └── audit.jsonl              # Phase 6: Audit log
└── .checkpoints/                # Phase 3: Checkpoint storage
```

---

## 🔗 Related Documents
- [Master Plan](../00-master-plan.md)
- [Current Architecture](../context/current-architecture.md)
