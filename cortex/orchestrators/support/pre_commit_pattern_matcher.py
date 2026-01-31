"""
Pre-commit Hook Pattern Matcher Orchestrator

Detects and blocks commits that would create duplication regressions by
matching patterns for:
1. ExecutionContext definitions (outside canonical path)
2. Registry classes (without BaseRegistry inheritance)
3. Orchestrator base classes (outside canonical location)
4. Wiring system implementations (outside Git-backed system)

This orchestrator powers the .git/hooks/pre-commit script to prevent
regressions of 8 duplication categories identified in Phase 8.3A.

Author: Asif Hussain
Date: 2026-01-31
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from cortex.brain.core.orchestrator_base import (
    OrchestratorBase,
    OrchestrationContext,
)
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


class BlockingPattern(Enum):
    """Patterns that trigger pre-commit blocking"""
    
    EXECUTION_CONTEXT = "execution_context"
    REGISTRY = "registry"
    ORCHESTRATOR_BASE = "orchestrator_base"
    WIRING_SYSTEM = "wiring_system"
    NONE = "none"


@dataclass
class PatternCheckResult:
    """Result of pattern check on a file"""
    
    file_path: str
    blocked: bool
    pattern: BlockingPattern = BlockingPattern.NONE
    reason: str = ""
    severity: str = "low"  # low, medium, high, critical
    timestamp: Optional[datetime] = None
    audit_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "file_path": self.file_path,
            "blocked": self.blocked,
            "pattern": self.pattern.value,
            "reason": self.reason,
            "severity": self.severity,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "audit_id": self.audit_id,
            "details": self.details,
        }


class PreCommitPatternMatcher(OrchestratorBase):
    """
    Pre-commit hook pattern matcher orchestrator.
    
    Detects patterns that would introduce duplication regressions and
    blocks commits that match these patterns.
    
    Attributes:
        DOMAIN: Support
        VERSION: 1.0
        STAGES: [analysis, detection, blocking, logging]
    
    Tier: 1
    """
    
    DOMAIN = "support"
    VERSION = "1.0"
    STAGES = ["analysis", "detection", "blocking", "logging"]
    
    # Canonical paths (allowed locations)
    CANONICAL_PATHS = {
        "execution_context": "cortex/brain/core/orchestrator_base.py",
        "orchestrator_base": "cortex/brain/core/orchestrator_base.py",
        "wiring": "cortex/wiring/",
    }
    
    # Patterns to detect
    BLOCKING_PATTERNS = {
        "execution_context": [
            r"class\s+ExecutionContext\b",
            r"class\s+ExecutionCtx\b",
            r"class\s+ExecContext\b",
        ],
        "registry": [
            r"class\s+\w*Registry",
        ],
        "orchestrator_base": [
            r"class\s+(Base|Abstract|Core|Root)?Orchestrator",
            r"class\s+\w*Orchestrator\s*\(",  # Class with inheritance
        ],
        "wiring_system": [
            r"class\s+\w*Wiring",
            r"class\s+\w*Transform",
            r"class\s+\w*Harness",
            r"class\s+\w*Guided",
            r"def\s+wire_",
            r"def\s+apply_wiring",
        ],
    }
    
    def __init__(self, context: Optional[OrchestrationContext] = None) -> None:
        """
        Initialize PreCommitPatternMatcher.
        
        Args:
            context: OrchestrationContext (optional)
        """
        if context is None:
            context = OrchestrationContext(
                orchestrator_id="PreCommitPatternMatcher",
                orchestrator_name="Pre-commit Pattern Matcher",
            )
        
        super().__init__(context)
        
        self.audit_logger = EnhancedAuditLogger()
        self._whitelist: List[str] = self._get_default_whitelist()
        self._next_audit_id = 1
    
    # =====================================================================
    # EXECUTION CONTEXT PATTERN CHECKING
    # =====================================================================
    
    def check_execution_context_pattern(
        self,
        file_path: str,
        file_content: str,
    ) -> PatternCheckResult:
        """
        Check if file defines ExecutionContext outside canonical location.
        
        Args:
            file_path: Path to file
            file_content: File content
            
        Returns:
            PatternCheckResult with blocking decision
        """
        result = PatternCheckResult(
            file_path=file_path,
            blocked=False,
            timestamp=datetime.now(),
            audit_id=self._next_audit_id_str(),
        )
        
        # Check if in whitelist
        if self._is_in_whitelist(file_path):
            result.reason = "Path in whitelist"
            return result
        
        # Check if canonical location
        if file_path.endswith(self.CANONICAL_PATHS["execution_context"]):
            result.reason = "Canonical location"
            return result
        
        # Check patterns
        for pattern in self.BLOCKING_PATTERNS["execution_context"]:
            if re.search(pattern, file_content):
                result.blocked = True
                result.pattern = BlockingPattern.EXECUTION_CONTEXT
                result.severity = "critical"
                result.reason = (
                    f"ExecutionContext defined outside canonical location "
                    f"({self.CANONICAL_PATHS['execution_context']}). "
                    f"Use OrchestrationContext or consolidate to canonical path."
                )
                self._log_blocked_pattern(result)
                return result
        
        result.reason = "No ExecutionContext pattern found"
        return result
    
    # =====================================================================
    # REGISTRY PATTERN CHECKING
    # =====================================================================
    
    def check_registry_pattern(
        self,
        file_path: str,
        file_content: str,
    ) -> PatternCheckResult:
        """
        Check if file defines Registry without BaseRegistry inheritance.
        
        Args:
            file_path: Path to file
            file_content: File content
            
        Returns:
            PatternCheckResult with blocking decision
        """
        result = PatternCheckResult(
            file_path=file_path,
            blocked=False,
            timestamp=datetime.now(),
            audit_id=self._next_audit_id_str(),
        )
        
        # Check if in whitelist
        if self._is_in_whitelist(file_path):
            result.reason = "Path in whitelist"
            return result
        
        # Check for Registry class definition
        registry_match = re.search(r"class\s+(\w*Registry)\b", file_content)
        if not registry_match:
            result.reason = "No Registry pattern found"
            return result
        
        registry_name = registry_match.group(1)
        
        # Check if inherits from BaseRegistry
        inherits_pattern = rf"class\s+{registry_name}\s*\(\s*BaseRegistry"
        if re.search(inherits_pattern, file_content):
            result.reason = "Registry properly inherits from BaseRegistry"
            return result
        
        # Check for singleton pattern (sign of old-style registry)
        singleton_patterns = [
            r"_instance\s*=\s*None",
            r"def\s+__new__\(",
            r"@staticmethod",
            r"@classmethod.*\n.*_instance",
        ]
        has_singleton = any(re.search(p, file_content) for p in singleton_patterns)
        
        if has_singleton or registry_match:
            result.blocked = True
            result.pattern = BlockingPattern.REGISTRY
            result.severity = "high"
            result.reason = (
                f"Registry class '{registry_name}' must inherit from BaseRegistry[T]. "
                f"Consolidate to cortex/core/base_registry.py pattern."
            )
            self._log_blocked_pattern(result)
            return result
        
        result.reason = "Registry pattern validated"
        return result
    
    # =====================================================================
    # ORCHESTRATOR BASE CLASS CHECKING
    # =====================================================================
    
    def check_orchestrator_base_pattern(
        self,
        file_path: str,
        file_content: str,
    ) -> PatternCheckResult:
        """
        Check if file defines orchestrator base class outside canonical location.
        
        Args:
            file_path: Path to file
            file_content: File content
            
        Returns:
            PatternCheckResult with blocking decision
        """
        result = PatternCheckResult(
            file_path=file_path,
            blocked=False,
            timestamp=datetime.now(),
            audit_id=self._next_audit_id_str(),
        )
        
        # Check if in whitelist
        if self._is_in_whitelist(file_path):
            result.reason = "Path in whitelist"
            return result
        
        # Check if canonical location
        if file_path.endswith(self.CANONICAL_PATHS["orchestrator_base"]):
            result.reason = "Canonical location"
            return result
        
        # Check patterns for base orchestrator classes
        base_class_patterns = [
            (r"class\s+BaseOrchestrator\b", "BaseOrchestrator"),
            (r"class\s+AbstractOrchestrator\b", "AbstractOrchestrator"),
            (r"class\s+CoreOrchestrator\b", "CoreOrchestrator"),
            (r"class\s+RootOrchestrator\b", "RootOrchestrator"),
            (r"class\s+Orchestrator\b(?!.*IOrchestrator)", "Orchestrator"),
        ]
        
        for pattern, class_name in base_class_patterns:
            if re.search(pattern, file_content):
                result.blocked = True
                result.pattern = BlockingPattern.ORCHESTRATOR_BASE
                result.severity = "critical"
                result.reason = (
                    f"New base orchestrator class '{class_name}' detected. "
                    f"All orchestrators must inherit from OrchestratorBase "
                    f"({self.CANONICAL_PATHS['orchestrator_base']})."
                )
                self._log_blocked_pattern(result)
                return result
        
        result.reason = "No new base orchestrator class detected"
        return result
    
    # =====================================================================
    # WIRING SYSTEM PATTERN CHECKING
    # =====================================================================
    
    def check_wiring_pattern(
        self,
        file_path: str,
        file_content: str,
    ) -> PatternCheckResult:
        """
        Check if file implements wiring system outside Git-backed system.
        
        Args:
            file_path: Path to file
            file_content: File content
            
        Returns:
            PatternCheckResult with blocking decision
        """
        result = PatternCheckResult(
            file_path=file_path,
            blocked=False,
            timestamp=datetime.now(),
            audit_id=self._next_audit_id_str(),
        )
        
        # Allow changes within canonical wiring system
        if self.CANONICAL_PATHS["wiring"] in file_path:
            result.reason = "Canonical wiring path"
            return result
        
        # Check if in whitelist
        if self._is_in_whitelist(file_path):
            result.reason = "Path in whitelist"
            return result
        
        # Check for legacy wiring file names
        legacy_files = [
            "transform_001",
            "wiring_harness",
            "guided_wiring",
            "wiring_auto_fixer",
        ]
        if any(legacy in file_path.lower() for legacy in legacy_files):
            result.blocked = True
            result.pattern = BlockingPattern.WIRING_SYSTEM
            result.severity = "critical"
            result.reason = (
                f"Legacy wiring system detected in path. "
                f"Use Git-backed YAML system (cortex/wiring/) instead."
            )
            self._log_blocked_pattern(result)
            return result
        
        # Check patterns
        for pattern in self.BLOCKING_PATTERNS["wiring_system"]:
            if re.search(pattern, file_content):
                result.blocked = True
                result.pattern = BlockingPattern.WIRING_SYSTEM
                result.severity = "critical"
                result.reason = (
                    f"New wiring system implementation detected. "
                    f"All wiring must use Git-backed YAML system (cortex/wiring/)."
                )
                self._log_blocked_pattern(result)
                return result
        
        result.reason = "No wiring system pattern detected"
        return result
    
    # =====================================================================
    # BATCH FILE CHECKING
    # =====================================================================
    
    def check_file(
        self,
        file_path: str,
        file_content: str,
    ) -> List[PatternCheckResult]:
        """
        Check all patterns in a single file.
        
        Args:
            file_path: Path to file
            file_content: File content
            
        Returns:
            List of PatternCheckResult for each pattern
        """
        results = []
        
        # Skip non-Python files
        if not file_path.endswith(".py"):
            return results
        
        # Check all patterns
        results.append(self.check_execution_context_pattern(file_path, file_content))
        results.append(self.check_registry_pattern(file_path, file_content))
        results.append(self.check_orchestrator_base_pattern(file_path, file_content))
        results.append(self.check_wiring_pattern(file_path, file_content))
        
        return results
    
    def check_files(
        self,
        files: List[Tuple[str, str]],
    ) -> List[PatternCheckResult]:
        """
        Check multiple files in a commit.
        
        Args:
            files: List of (file_path, file_content) tuples
            
        Returns:
            List of all PatternCheckResult across all files
        """
        all_results = []
        
        for file_path, file_content in files:
            results = self.check_file(file_path, file_content)
            all_results.extend(results)
        
        return all_results
    
    # =====================================================================
    # WHITELIST MANAGEMENT
    # =====================================================================
    
    def _get_default_whitelist(self) -> List[str]:
        """Get default whitelist patterns"""
        return [
            "tests/",
            "test_",
            "_test.py",
            "docs/",
            "migration/",
            "_migration.py",
            "examples/",
            "_example.py",
        ]
    
    def get_default_whitelist(self) -> List[str]:
        """Get default whitelist patterns"""
        return self._get_default_whitelist()
    
    def set_whitelist(self, whitelist: List[str]) -> None:
        """
        Set whitelist patterns.
        
        Args:
            whitelist: List of path patterns to whitelist
        """
        self._whitelist = whitelist
    
    def add_whitelist_entry(self, entry: str) -> None:
        """
        Add entry to whitelist.
        
        Args:
            entry: Path pattern to whitelist
        """
        if entry not in self._whitelist:
            self._whitelist.append(entry)
    
    def _is_in_whitelist(self, file_path: str) -> bool:
        """
        Check if file path is in whitelist.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if in whitelist
        """
        for pattern in self._whitelist:
            if pattern in file_path:
                return True
        return False
    
    # =====================================================================
    # AUDIT LOGGING
    # =====================================================================
    
    def _log_blocked_pattern(self, result: PatternCheckResult) -> None:
        """
        Log blocked pattern to audit trail.
        
        Args:
            result: PatternCheckResult
        """
        # Use operation start/complete for audit trail
        self.audit_logger.log_operation_start(
            ac_id=result.audit_id,
            operation="BLOCK_DUPLICATION_REGRESSION",
            details={
                "file_path": result.file_path,
                "pattern": result.pattern.value,
                "reason": result.reason,
                "severity": result.severity,
            },
        )
    
    def _next_audit_id_str(self) -> str:
        """
        Get next audit ID.
        
        Returns:
            Next audit ID as string
        """
        audit_id = f"PRE-COMMIT-{self._next_audit_id:06d}"
        self._next_audit_id += 1
        return audit_id
    
    # =====================================================================
    # ORCHESTRATOR INTERFACE IMPLEMENTATION
    # =====================================================================
    
    def execute(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute pattern checking (IOrchestrator interface).
        
        Kwargs:
            files: List of (file_path, file_content) tuples
            
        Returns:
            Dict with results
        """
        files = kwargs.get("files", [])
        results = self.check_files(files)
        
        blocked_count = sum(1 for r in results if r.blocked)
        
        return {
            "results": [r.to_dict() for r in results],
            "blocked_count": blocked_count,
            "total_files": len(set(r.file_path for r in results)),
            "should_block_commit": blocked_count > 0,
        }
    
    def execute_async(self, *args: Any, **kwargs: Any) -> None:
        """Async execution not supported"""
        raise NotImplementedError("PreCommitPatternMatcher does not support async")
