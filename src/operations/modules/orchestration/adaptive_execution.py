"""
Adaptive Execution Framework for CORTEX 4.0

Enables orchestrators to adapt execution behavior based on:
- User intent (explicit mode selection)
- Task complexity (high/medium/low)
- Safety requirements (critical operations)

Execution Modes:
- SUPERVISED: User confirmation required per phase
- AUTONOMOUS: Full automation with auto-rollback
- HYBRID: Conditional confirmation for high-risk actions

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import re


class ExecutionMode(Enum):
    """Execution mode for orchestrators."""
    SUPERVISED = "supervised"
    AUTONOMOUS = "autonomous"
    HYBRID = "hybrid"


@dataclass
class AdaptiveExecutionConfig:
    """Configuration for adaptive execution."""
    default_mode: ExecutionMode = ExecutionMode.SUPERVISED
    enable_auto_rollback: bool = True
    validation_gates: bool = True
    safety_critical_keywords: List[str] = field(default_factory=lambda: [
        "delete", "drop", "truncate", "production", "destroy"
    ])
    high_risk_keywords: List[str] = field(default_factory=lambda: [
        "database", "migration", "deploy", "publish"
    ])


class ExecutionStrategy(ABC):
    """
    Abstract base class for execution strategies.
    
    Implements Strategy Pattern for different execution modes.
    """
    
    def __init__(self, config: Optional[AdaptiveExecutionConfig] = None):
        """Initialize strategy with optional config."""
        self.config = config or AdaptiveExecutionConfig()
        self.checkpoints: List[Dict[str, Any]] = []
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute phase with mode-specific behavior.
        
        Args:
            context: Execution context with phase info
            
        Returns:
            Execution result with confirmation requirements
        """
        pass
    
    def validate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate context before execution.
        
        Args:
            context: Execution context
            
        Returns:
            Validation result
        """
        return {
            "valid": True,
            "errors": [],
            "warnings": [],
            "timestamp": datetime.now().isoformat()
        }
    
    def rollback(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rollback to last checkpoint.
        
        Args:
            context: Current context
            
        Returns:
            Rollback result
        """
        if not self.checkpoints:
            return {
                "success": False,
                "message": "No checkpoints available for rollback"
            }
        
        last_checkpoint = self.checkpoints.pop()
        return {
            "success": True,
            "message": f"Rolled back to checkpoint at {last_checkpoint['timestamp']}",
            "checkpoint": last_checkpoint
        }


class SupervisedStrategy(ExecutionStrategy):
    """
    Supervised execution strategy.
    
    Requires user confirmation before each phase execution.
    Provides maximum control and visibility.
    """
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with user confirmation requirement."""
        # Validate first
        validation = self.validate(context)
        if not validation["valid"]:
            return {
                "status": "validation_failed",
                "errors": validation["errors"],
                "requires_confirmation": False
            }
        
        # SUPERVISED mode always requires confirmation
        return {
            "status": "pending_confirmation",
            "phase": context.get("phase", "unknown"),
            "action": context.get("action", "unknown"),
            "requires_confirmation": True,
            "validation": validation
        }


class AutonomousStrategy(ExecutionStrategy):
    """
    Autonomous execution strategy.
    
    Executes without user confirmation, with automatic rollback on failure.
    Suitable for low-risk, well-tested operations.
    """
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute autonomously without confirmation."""
        # Validate first
        validation = self.validate(context)
        if not validation["valid"]:
            return {
                "status": "validation_failed",
                "errors": validation["errors"],
                "requires_confirmation": False
            }
        
        # Create checkpoint before execution
        if self.config.enable_auto_rollback:
            checkpoint = {
                "phase": context.get("phase"),
                "state": context.copy(),
                "timestamp": datetime.now().isoformat()
            }
            self.checkpoints.append(checkpoint)
        
        # AUTONOMOUS mode does NOT require confirmation
        return {
            "status": "executing",
            "phase": context.get("phase", "unknown"),
            "action": context.get("action", "unknown"),
            "requires_confirmation": False,
            "auto_rollback_enabled": self.config.enable_auto_rollback,
            "validation": validation
        }


class HybridStrategy(ExecutionStrategy):
    """
    Hybrid execution strategy.
    
    Intelligently decides when to require confirmation based on:
    - Risk level of the operation
    - Complexity of the task
    - Safety-critical indicators
    """
    
    def _assess_risk(self, context: Dict[str, Any]) -> str:
        """
        Assess risk level of operation.
        
        Args:
            context: Execution context
            
        Returns:
            Risk level: 'high', 'medium', or 'low'
        """
        # Explicit risk in context
        if "risk" in context:
            return context["risk"]
        
        # Check for safety-critical keywords
        task_text = str(context.get("task", "")).lower()
        action_text = str(context.get("action", "")).lower()
        combined_text = f"{task_text} {action_text}"
        
        for keyword in self.config.safety_critical_keywords:
            if keyword in combined_text:
                return "high"
        
        for keyword in self.config.high_risk_keywords:
            if keyword in combined_text:
                return "medium"
        
        return "low"
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with conditional confirmation."""
        # Validate first
        validation = self.validate(context)
        if not validation["valid"]:
            return {
                "status": "validation_failed",
                "errors": validation["errors"],
                "requires_confirmation": False
            }
        
        # Assess risk
        risk_level = self._assess_risk(context)
        
        # High-risk requires confirmation
        requires_confirmation = risk_level == "high"
        
        # Create checkpoint for non-high-risk operations
        if not requires_confirmation and self.config.enable_auto_rollback:
            checkpoint = {
                "phase": context.get("phase"),
                "state": context.copy(),
                "timestamp": datetime.now().isoformat()
            }
            self.checkpoints.append(checkpoint)
        
        status = "pending_confirmation" if requires_confirmation else "executing"
        
        return {
            "status": status,
            "phase": context.get("phase", "unknown"),
            "action": context.get("action", "unknown"),
            "requires_confirmation": requires_confirmation,
            "risk_level": risk_level,
            "validation": validation
        }


class ModeDetector:
    """
    Intelligent mode detection based on user intent and context.
    
    Analyzes:
    - Explicit user requests ("execute autonomously")
    - Task complexity
    - Safety requirements
    """
    
    def __init__(self, config: Optional[AdaptiveExecutionConfig] = None):
        """Initialize detector with optional config."""
        self.config = config or AdaptiveExecutionConfig()
        
        # Patterns for detecting user intent
        self.autonomous_patterns = [
            r"execute.*autonomously",
            r"run.*automatically",
            r"execute all phases autonomously",
            r"full automation",
            r"no confirmation"
        ]
        
        self.supervised_patterns = [
            r"show.*each step",
            r"confirm.*each",
            r"supervised",
            r"manual",
            r"step.*by.*step"
        ]
    
    def detect_mode(self, context: Dict[str, Any]) -> ExecutionMode:
        """
        Detect appropriate execution mode from context.
        
        Args:
            context: Execution context with user request, complexity, etc.
            
        Returns:
            Detected ExecutionMode
        """
        # Check for explicit user intent
        user_request = context.get("user_request", "").lower()
        
        # Check autonomous patterns
        for pattern in self.autonomous_patterns:
            if re.search(pattern, user_request, re.IGNORECASE):
                # Safety check - never autonomous for safety-critical
                if context.get("safety_critical"):
                    return ExecutionMode.SUPERVISED
                return ExecutionMode.AUTONOMOUS
        
        # Check supervised patterns
        for pattern in self.supervised_patterns:
            if re.search(pattern, user_request, re.IGNORECASE):
                return ExecutionMode.SUPERVISED
        
        # Safety-critical always supervised
        if context.get("safety_critical"):
            return ExecutionMode.SUPERVISED
        
        # Check complexity
        complexity = context.get("complexity", "medium").lower()
        
        if complexity == "high":
            return ExecutionMode.SUPERVISED
        elif complexity == "low":
            return ExecutionMode.AUTONOMOUS
        else:
            # Medium complexity -> HYBRID
            return ExecutionMode.HYBRID


class SafetyGuardrail:
    """
    Safety guardrails for execution.
    
    Provides:
    - Action validation
    - Checkpoint management
    - Rollback support
    """
    
    def __init__(self, config: Optional[AdaptiveExecutionConfig] = None):
        """Initialize guardrail with optional config."""
        self.config = config or AdaptiveExecutionConfig()
        self.checkpoints: List[Dict[str, Any]] = []
        
        # Dangerous action patterns
        self.dangerous_patterns = [
            r"delete\s+all",
            r"drop\s+database",
            r"truncate\s+table",
            r"rm\s+-rf\s+/",
            r"format\s+drive"
        ]
    
    def validate_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate action for safety.
        
        Args:
            action: Action to validate
            
        Returns:
            Validation result with allowed flag
        """
        action_text = str(action.get("action", "")).lower()
        path = str(action.get("path", "")).lower()
        combined = f"{action_text} {path}"
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, combined, re.IGNORECASE):
                return {
                    "allowed": False,
                    "reason": f"Dangerous action detected: {pattern}",
                    "action": action_text
                }
        
        # Check for safety-critical keywords in critical paths
        if path == "/" or path.startswith("/system"):
            for keyword in self.config.safety_critical_keywords:
                if keyword in action_text:
                    return {
                        "allowed": False,
                        "reason": f"Critical path operation: {keyword}",
                        "action": action_text,
                        "path": path
                    }
        
        return {
            "allowed": True,
            "action": action_text,
            "path": path
        }
    
    def create_checkpoint(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create rollback checkpoint.
        
        Args:
            context: Current execution context
            
        Returns:
            Checkpoint data
        """
        checkpoint = {
            "phase": context.get("phase"),
            "state": context.copy(),
            "timestamp": datetime.now().isoformat(),
            "checkpoint_id": len(self.checkpoints)
        }
        
        self.checkpoints.append(checkpoint)
        
        return checkpoint
    
    def restore_checkpoint(self, checkpoint_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Restore from checkpoint.
        
        Args:
            checkpoint_id: Specific checkpoint to restore (None = latest)
            
        Returns:
            Restored checkpoint or None
        """
        if not self.checkpoints:
            return None
        
        if checkpoint_id is None:
            return self.checkpoints.pop()
        
        if 0 <= checkpoint_id < len(self.checkpoints):
            # Restore specific checkpoint and discard later ones
            checkpoint = self.checkpoints[checkpoint_id]
            self.checkpoints = self.checkpoints[:checkpoint_id]
            return checkpoint
        
        return None
