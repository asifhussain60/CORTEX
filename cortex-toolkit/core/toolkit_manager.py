"""
CORTEX Toolkit Manager

Central orchestration layer for all toolkit operations.
Provides validation, execution, recovery, and dependency management.
"""
import asyncio
import sys
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

# Handle imports for both installed package and direct use
try:
    from shared.toolkit_registry import ToolkitRegistry
except ImportError:
    # Try adding parent to path
    parent_path = str(Path(__file__).parent.parent)
    if parent_path not in sys.path:
        sys.path.insert(0, parent_path)
    from shared.toolkit_registry import ToolkitRegistry

from .gate_keeper import GateKeeper
from .request_analyzer import RequestAnalyzer, ToolRequest, RecommendationType
from .recovery_manager import (
    RecoveryManager,
    ExecutionContext as RecoveryContext,
    RollbackResult,
)
from .dependency_manager import (
    DependencyManager,
    DependencyCheck,
    DependencyGraph,
    CircularDependencyError,
    UnmetDependencyError,
)
from .manifest_schema import (
    ManifestSchema,
    ValidationResult,
    PRIVILEGE_LEVELS,
    VALID_CAPABILITIES,
)
from .security_guard import (
    SecurityGuard,
    SanitizeResult,
    SecurityViolation,
    Severity,
    PrivilegeLevel,
)
from .audit_logger import (
    AuditLogger,
    ExecutionEvent as AuditExecutionEvent,
    SecurityEvent,
)
from .exceptions import (
    ToolkitError,
    ToolNotFoundError,
    ValidationError,
    ExecutionError,
    SecurityViolationError,
)

logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """Status of tool execution."""
    SUCCESS = "success"
    FAILED = "failed"
    VALIDATION_FAILED = "validation_failed"
    BLOCKED = "blocked"
    TIMEOUT = "timeout"


@dataclass
class ExecutionContext:
    """Context for tool execution."""
    tool: str
    args: List[str] = field(default_factory=list)
    working_dir: Optional[Path] = None
    timeout: Optional[int] = None  # seconds
    capture_output: bool = True
    env_vars: Dict[str, str] = field(default_factory=dict)
    dry_run: bool = False
    skip_validation: bool = False
    checkpoint_enabled: bool = True
    
    def __post_init__(self):
        if self.working_dir is None:
            self.working_dir = Path.cwd()


@dataclass
class ExecutionResult:
    """Result of tool execution."""
    status: ExecutionStatus
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    duration_ms: int = 0
    checkpoint_id: Optional[str] = None
    validation_result: Optional[Any] = None
    error: Optional[str] = None
    tool: str = ""
    args: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def success(self) -> bool:
        """Check if execution was successful."""
        return self.status == ExecutionStatus.SUCCESS and self.exit_code == 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "status": self.status.value,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "duration_ms": self.duration_ms,
            "checkpoint_id": self.checkpoint_id,
            "error": self.error,
            "tool": self.tool,
            "args": self.args,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class CreationCheck:
    """Result of checking if a tool can be created."""
    can_create: bool
    reason: str
    overlapping_tools: List[str] = field(default_factory=list)
    similarity_scores: Dict[str, float] = field(default_factory=dict)
    recommendation: str = ""


@dataclass
class ToolSpec:
    """Specification for a new tool."""
    name: str
    description: str
    command: str
    script_path: str
    category: str
    capabilities: List[str] = field(default_factory=list)
    platforms: List[str] = field(default_factory=lambda: ["windows", "linux", "macos"])
    requires_admin: bool = False
    execution_method: str = "cli"
    depends_on: List[str] = field(default_factory=list)


class ToolkitManager:
    """
    Central orchestration layer for all toolkit operations.
    
    Features:
    - Pre-execution validation via GateKeeper
    - Security checks and argument sanitization
    - Rate limiting
    - Execution context management
    - Future: Recovery/rollback, dependency management
    
    Usage:
        manager = ToolkitManager()
        result = await manager.execute('align', ['--check-only'])
        if result.success:
            print(result.stdout)
    """
    
    def __init__(self, toolkit_root: Optional[Path] = None):
        """
        Initialize ToolkitManager.
        
        Args:
            toolkit_root: Path to toolkit root. Auto-discovers if None.
        """
        self.registry = ToolkitRegistry(toolkit_root)
        self.gate_keeper = GateKeeper(self.registry)
        
        # Phase 2: Request Analyzer for duplication prevention
        self.request_analyzer = RequestAnalyzer(self.registry)
        
        # Phase 3: Recovery Manager for checkpoint/rollback
        self.recovery_manager = RecoveryManager(
            self.registry.toolkit_root,
            max_checkpoints=50
        )
        
        # Phase 4: Dependency Manager for tool dependency graph
        self.dependency_manager = DependencyManager(self.registry)
        
        # Phase 5: Manifest Schema for v2 validation and migration
        self.manifest_schema = ManifestSchema(self.registry.toolkit_root)
        
        # Phase 6: Security Guard for input sanitization
        self.security_guard = SecurityGuard()
        
        # Phase 6: Audit Logger for tamper-evident audit trail
        self.audit_logger = AuditLogger(toolkit_root=self.registry.toolkit_root)
        
        self._execution_history: List[ExecutionResult] = []
        self._max_history = 100
        
        logger.info(f"ToolkitManager initialized with root: {self.registry.toolkit_root}")
    
    async def execute(
        self,
        tool: str,
        args: Optional[List[str]] = None,
        context: Optional[ExecutionContext] = None
    ) -> ExecutionResult:
        """
        Execute tool with full validation and recovery support.
        
        Args:
            tool: Tool name to execute.
            args: Command-line arguments.
            context: Execution context (optional).
            
        Returns:
            ExecutionResult with status, output, and metadata.
            
        Raises:
            ValidationError: If validation fails and skip_validation is False.
        """
        args = args or []
        
        # Build execution context
        if context is None:
            context = ExecutionContext(tool=tool, args=args)
        else:
            context.tool = tool
            context.args = args
        
        start_time = datetime.now()
        
        # Validate unless explicitly skipped
        if not context.skip_validation:
            validation = self.gate_keeper.validate_execution(tool, args)
            
            if not validation.passed:
                result = ExecutionResult(
                    status=ExecutionStatus.VALIDATION_FAILED,
                    exit_code=-1,
                    validation_result=validation,
                    error="Validation failed",
                    tool=tool,
                    args=args,
                    duration_ms=self._calc_duration_ms(start_time)
                )
                self._record_execution(result)
                return result
        
        # Dry run mode - don't actually execute
        if context.dry_run:
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                exit_code=0,
                stdout=f"[DRY RUN] Would execute: {tool} {' '.join(args)}",
                tool=tool,
                args=args,
                duration_ms=self._calc_duration_ms(start_time)
            )
        
        # Execute the tool
        try:
            result = await self._execute_tool(context)
            result.duration_ms = self._calc_duration_ms(start_time)
            self._record_execution(result)
            return result
            
        except Exception as e:
            logger.exception(f"Execution error for {tool}")
            result = ExecutionResult(
                status=ExecutionStatus.FAILED,
                exit_code=-1,
                error=str(e),
                tool=tool,
                args=args,
                duration_ms=self._calc_duration_ms(start_time)
            )
            self._record_execution(result)
            return result
    
    def execute_sync(
        self,
        tool: str,
        args: Optional[List[str]] = None,
        context: Optional[ExecutionContext] = None
    ) -> ExecutionResult:
        """
        Synchronous wrapper for execute().
        
        Convenience method for non-async code.
        """
        return asyncio.run(self.execute(tool, args, context))
    
    async def _execute_tool(self, context: ExecutionContext) -> ExecutionResult:
        """
        Internal method to execute a tool.
        
        Args:
            context: Execution context.
            
        Returns:
            ExecutionResult from execution.
        """
        tool_info = self.registry.get_tool(context.tool)
        if not tool_info:
            raise ToolNotFoundError(context.tool)
        
        execution_method = tool_info.get("execution_method", "cli")
        
        if execution_method == "copilot_chat":
            # These tools are meant for Copilot Chat, not direct execution
            return ExecutionResult(
                status=ExecutionStatus.BLOCKED,
                exit_code=-1,
                error=f"Tool '{context.tool}' is a copilot_chat tool and cannot be executed directly",
                tool=context.tool,
                args=context.args
            )
        
        # Resolve script path
        if execution_method == "cli_wrapper":
            script_path = self.registry.resolve_wrapper_path(context.tool)
        else:
            script_path = self.registry.resolve_script_path(context.tool)
        
        if not script_path or not script_path.exists():
            raise ToolNotFoundError(
                context.tool, 
                similar_tools=[f"Script not found: {script_path}"]
            )
        
        # Build command
        cmd = [sys.executable, str(script_path)] + context.args
        
        # Set up environment
        env = None
        if context.env_vars:
            import os
            env = os.environ.copy()
            env.update(context.env_vars)
        
        # Execute in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self._run_subprocess(cmd, context, env)
        )
        
        return result
    
    def _run_subprocess(
        self, 
        cmd: List[str], 
        context: ExecutionContext,
        env: Optional[Dict[str, str]] = None
    ) -> ExecutionResult:
        """Run subprocess and capture result."""
        try:
            result = subprocess.run(
                cmd,
                cwd=context.working_dir,
                capture_output=context.capture_output,
                timeout=context.timeout,
                text=True,
                env=env
            )
            
            status = ExecutionStatus.SUCCESS if result.returncode == 0 else ExecutionStatus.FAILED
            
            return ExecutionResult(
                status=status,
                exit_code=result.returncode,
                stdout=result.stdout or "",
                stderr=result.stderr or "",
                tool=context.tool,
                args=context.args
            )
            
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                status=ExecutionStatus.TIMEOUT,
                exit_code=-1,
                error=f"Execution timed out after {context.timeout}s",
                tool=context.tool,
                args=context.args
            )
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                exit_code=-1,
                error=str(e),
                tool=context.tool,
                args=context.args
            )
    
    def can_create_tool(self, tool_spec: ToolSpec) -> CreationCheck:
        """
        Check if a new tool should be created or existing used.
        
        Uses RequestAnalyzer (Phase 2) for semantic analysis of
        intent and capability overlap detection.
        
        Args:
            tool_spec: Specification for the proposed tool.
            
        Returns:
            CreationCheck with recommendation based on semantic analysis.
        """
        # First check for exact name duplicate
        exact_dup = self.request_analyzer.check_exact_duplicate(tool_spec.name)
        if exact_dup:
            return CreationCheck(
                can_create=False,
                reason=f"Tool '{tool_spec.name}' already exists",
                overlapping_tools=[exact_dup],
                recommendation=f"Use existing tool: {exact_dup}"
            )
        
        # Use RequestAnalyzer for semantic analysis
        request = ToolRequest(
            name=tool_spec.name,
            description=tool_spec.description,
            capabilities=tool_spec.capabilities,
            category=tool_spec.category
        )
        
        analysis = self.request_analyzer.analyze_request(request)
        
        # Map analysis result to CreationCheck
        overlapping_names = [t.name for t in analysis.overlapping_tools]
        
        if analysis.recommendation_type == RecommendationType.BLOCK:
            return CreationCheck(
                can_create=False,
                reason=analysis.recommendation,
                overlapping_tools=overlapping_names,
                similarity_scores=analysis.similarity_scores,
                recommendation=f"Use existing tool instead: {overlapping_names[0] if overlapping_names else 'unknown'}"
            )
        
        if analysis.recommendation_type == RecommendationType.SUGGEST:
            return CreationCheck(
                can_create=True,
                reason="Significant overlap with existing tools detected",
                overlapping_tools=overlapping_names,
                similarity_scores=analysis.similarity_scores,
                recommendation=analysis.recommendation
            )
        
        if analysis.recommendation_type == RecommendationType.WARN:
            return CreationCheck(
                can_create=True,
                reason="Some overlap detected - review existing tools",
                overlapping_tools=overlapping_names,
                similarity_scores=analysis.similarity_scores,
                recommendation=analysis.recommendation
            )
        
        # ALLOW - no significant overlap
        return CreationCheck(
            can_create=True,
            reason="No overlapping tools found",
            overlapping_tools=[],
            recommendation="Tool creation is recommended"
        )
    
    def register_tool(self, tool_spec: ToolSpec) -> bool:
        """
        Register a new tool after validation.
        
        Note: This is a placeholder - actual registration would modify the manifest.
        
        Args:
            tool_spec: Tool specification.
            
        Returns:
            True if registered successfully.
            
        Raises:
            DuplicationWarning: If tool overlaps with existing.
        """
        check = self.can_create_tool(tool_spec)
        if not check.can_create:
            logger.warning(f"Cannot register tool: {check.reason}")
            return False
        
        logger.info(f"Tool '{tool_spec.name}' would be registered (not implemented)")
        return True
    
    def validate_tool(self, tool: str, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Validate a tool without executing.
        
        Args:
            tool: Tool name.
            args: Arguments to validate.
            
        Returns:
            Validation result as dictionary.
        """
        validation = self.gate_keeper.validate_execution(tool, args or [], skip_rate_limit=True)
        return validation.to_dict()
    
    def get_execution_history(self, limit: int = 10) -> List[Dict]:
        """Get recent execution history."""
        return [r.to_dict() for r in self._execution_history[-limit:]]
    
    def _record_execution(self, result: ExecutionResult):
        """Record execution in history."""
        self._execution_history.append(result)
        
        # Trim history
        if len(self._execution_history) > self._max_history:
            self._execution_history = self._execution_history[-self._max_history:]
    
    def _calc_duration_ms(self, start: datetime) -> int:
        """Calculate duration in milliseconds."""
        return int((datetime.now() - start).total_seconds() * 1000)
    
    # Convenience methods
    
    def list_tools(self, category: Optional[str] = None) -> List[Dict]:
        """List available tools."""
        return self.registry.list_tools(category)
    
    def list_categories(self) -> List[str]:
        """List tool categories."""
        return self.registry.list_categories()
    
    def get_tool_info(self, name: str) -> Optional[Dict]:
        """Get tool information."""
        return self.registry.get_tool(name)
    
    def reset_rate_limits(self, tool: Optional[str] = None):
        """Reset rate limits for testing/maintenance."""
        self.gate_keeper.reset_rate_limits(tool)
    
    # =========================================================================
    # Phase 3: Recovery Manager Integration
    # =========================================================================
    
    # Patterns that indicate destructive operations
    DESTRUCTIVE_TOOL_PATTERNS = {
        'cleanup', 'delete', 'remove', 'purge', 'migrate', 'reset',
        'overwrite', 'replace', 'sweep', 'clear', 'drop', 'truncate'
    }
    
    def _is_destructive_tool(self, tool: str) -> bool:
        """
        Check if a tool is potentially destructive.
        
        Args:
            tool: Tool name to check.
            
        Returns:
            True if tool should create checkpoint before execution.
        """
        tool_lower = tool.lower()
        
        # Check tool name against patterns
        for pattern in self.DESTRUCTIVE_TOOL_PATTERNS:
            if pattern in tool_lower:
                return True
        
        # Check manifest for explicit destructive flag
        tool_info = self.registry.get_tool(tool)
        if tool_info:
            return tool_info.get('destructive', False)
        
        return False
    
    def create_checkpoint(
        self,
        tool: str,
        args: List[str],
        affected_paths: Optional[List[Path]] = None,
    ) -> Optional[str]:
        """
        Create a checkpoint before tool execution.
        
        Args:
            tool: Tool name.
            args: Tool arguments.
            affected_paths: Paths that may be modified.
            
        Returns:
            Checkpoint ID if created, None otherwise.
        """
        if affected_paths is None:
            affected_paths = []
        
        context = RecoveryContext(
            tool=tool,
            args=args,
            affected_paths=affected_paths,
            is_destructive=self._is_destructive_tool(tool),
        )
        
        checkpoint = self.recovery_manager.create_checkpoint(context)
        logger.info(f"Created checkpoint {checkpoint.id} for {tool}")
        return checkpoint.id
    
    def rollback(self, checkpoint_id: str) -> RollbackResult:
        """
        Rollback to a previous checkpoint.
        
        Args:
            checkpoint_id: ID of checkpoint to restore.
            
        Returns:
            RollbackResult with success status and details.
        """
        result = self.recovery_manager.rollback(checkpoint_id)
        if result.success:
            logger.info(f"Rollback successful to checkpoint {checkpoint_id}")
        else:
            logger.error(f"Rollback failed: {result.errors}")
        return result
    
    def list_checkpoints(self, limit: int = 10) -> List[Dict]:
        """
        List recent checkpoints.
        
        Args:
            limit: Maximum number to return.
            
        Returns:
            List of checkpoint info as dictionaries.
        """
        from .checkpoint import Checkpoint
        checkpoints = self.recovery_manager.list_checkpoints(limit)
        return [
            {
                'id': cp.id,
                'timestamp': cp.timestamp.isoformat(),
                'tool': cp.tool,
                'args': cp.args,
                'state': cp.state.value,
            }
            for cp in checkpoints
        ]
    
    # =========================================================================
    # Phase 4: Dependency Manager Integration
    # =========================================================================
    
    def check_dependencies(self, tool: str) -> DependencyCheck:
        """
        Check if a tool's dependencies are satisfied.
        
        Args:
            tool: Tool name to check.
            
        Returns:
            DependencyCheck with satisfaction status.
        """
        return self.dependency_manager.validate_dependencies(tool)
    
    def get_execution_order(self, tools: List[str]) -> List[str]:
        """
        Get topologically sorted execution order for tools.
        
        Args:
            tools: List of tools to execute.
            
        Returns:
            List of tools in execution order (dependencies first).
            
        Raises:
            CircularDependencyError: If circular dependencies exist.
        """
        return self.dependency_manager.get_execution_order(tools)
    
    def detect_circular_dependencies(self) -> List[List[str]]:
        """
        Detect circular dependencies in the toolkit.
        
        Returns:
            List of cycles (each cycle is a list of tool names).
        """
        return self.dependency_manager.detect_circular()
    
    def get_dependency_tree(self, tool: str) -> Dict[str, Any]:
        """
        Get dependency tree for a tool.
        
        Args:
            tool: Tool name.
            
        Returns:
            Nested dictionary representing dependency tree.
        """
        return self.dependency_manager.get_dependency_tree(tool)
    
    def get_all_dependencies(self, tool: str) -> List[str]:
        """
        Get all transitive dependencies of a tool.
        
        Args:
            tool: Tool name.
            
        Returns:
            List of all dependency names.
        """
        return self.dependency_manager.get_all_dependencies(tool)
    
    # =========================================================================
    # Phase 5: Manifest Schema Methods
    # =========================================================================
    
    def validate_manifest(self, manifest: Dict[str, Any]) -> ValidationResult:
        """
        Validate a manifest against the v2 schema.
        
        Args:
            manifest: Manifest dictionary to validate.
            
        Returns:
            ValidationResult with is_valid, errors, and warnings.
        """
        return self.manifest_schema.validate(manifest)
    
    def get_tool_input_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get input schema for a tool.
        
        Args:
            tool_name: Name of the tool.
            
        Returns:
            JSON Schema for tool input, or None if not defined.
        """
        tool = self.registry.get_tool(tool_name)
        if tool:
            return tool.get("input_schema")
        return None
    
    def get_tool_output_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get output schema for a tool.
        
        Args:
            tool_name: Name of the tool.
            
        Returns:
            JSON Schema for tool output, or None if not defined.
        """
        tool = self.registry.get_tool(tool_name)
        if tool:
            return tool.get("output_schema")
        return None
    
    def validate_tool_input(
        self, 
        tool_name: str, 
        input_data: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate input data against a tool's input schema.
        
        Args:
            tool_name: Name of the tool.
            input_data: Input data to validate.
            
        Returns:
            ValidationResult.
        """
        tool = self.registry.get_tool(tool_name)
        if not tool:
            return ValidationResult(
                is_valid=False,
                errors=[f"Tool not found: {tool_name}"]
            )
        return self.manifest_schema.validate_input(tool, input_data)
    
    def migrate_manifest_to_v2(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate a v1 manifest to v2 format.
        
        Args:
            manifest: V1 format manifest.
            
        Returns:
            V2 format manifest.
        """
        return self.manifest_schema.migrate_to_v2(manifest)
    
    def get_manifest_version(self, manifest: Dict[str, Any]) -> int:
        """
        Detect the version of a manifest.
        
        Args:
            manifest: Manifest dictionary.
            
        Returns:
            Version number (1 or 2).
        """
        return self.manifest_schema.detect_version(manifest)
    
    # =========================================================================
    # Phase 6: Security Methods
    # =========================================================================
    
    def sanitize_arguments(
        self, 
        args: List[str],
        allow_absolute: bool = False
    ) -> SanitizeResult:
        """
        Sanitize and validate command-line arguments.
        
        Args:
            args: List of arguments to validate.
            allow_absolute: Whether to allow absolute paths.
            
        Returns:
            SanitizeResult with safety status and violations.
        """
        return self.security_guard.sanitize_arguments(args, allow_absolute)
    
    def check_privilege_level(
        self,
        tool_name: str,
        current_level: str = "user"
    ) -> bool:
        """
        Check if current privilege level allows tool execution.
        
        Args:
            tool_name: Name of the tool.
            current_level: Current user's privilege level.
            
        Returns:
            True if execution is allowed.
        """
        tool = self.registry.get_tool(tool_name)
        if not tool:
            return False
        
        # Get required level from tool security config
        security = tool.get("security", {})
        required_level = security.get("privilege_level", "user")
        
        result = self.security_guard.check_privilege(
            tool_name,
            required_level=required_level,
            current_level=current_level
        )
        return result.allowed
    
    def log_execution_event(
        self,
        tool: str,
        args: List[str],
        status: str,
        exit_code: int,
        duration_ms: int,
        checkpoint_id: Optional[str] = None
    ) -> None:
        """
        Log a tool execution event to the audit trail.
        
        Args:
            tool: Tool name.
            args: Command arguments.
            status: Execution status.
            exit_code: Exit code.
            duration_ms: Duration in milliseconds.
            checkpoint_id: Optional checkpoint ID.
        """
        event = AuditExecutionEvent(
            tool=tool,
            args=args,
            status=status,
            exit_code=exit_code,
            duration_ms=duration_ms,
            checkpoint_id=checkpoint_id
        )
        self.audit_logger.log_execution(event)
    
    def log_security_event(
        self,
        event_type: str,
        tool: str,
        blocked: bool = True,
        severity: str = "medium",
        violation_type: Optional[str] = None
    ) -> None:
        """
        Log a security event to the audit trail.
        
        Args:
            event_type: Type of security event.
            tool: Tool name.
            blocked: Whether the action was blocked.
            severity: Event severity.
            violation_type: Type of security violation.
        """
        event = SecurityEvent(
            event_type=event_type,
            tool=tool,
            blocked=blocked,
            severity=severity,
            violation_type=violation_type
        )
        self.audit_logger.log_security(event)
    
    def get_audit_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the audit log.
        
        Returns:
            Dictionary with audit statistics.
        """
        return self.audit_logger.get_statistics()

