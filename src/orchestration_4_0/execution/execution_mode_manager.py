"""
Execution Mode Manager - Adaptive execution mode selection

Author: Asif Hussain
Version: 1.1
Created: December 21, 2025
Updated: December 21, 2025

Features:
- Smart mode selection based on user experience + operation risk
- Automatic escalation after failures
- User profile tracking
- Integration with Phase 2 autonomous execution
- Comprehensive logging and error handling
- Performance optimization with caching
"""

import logging
import time
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock

from .execution_mode import ExecutionMode


@dataclass
class User:
    """User profile for experience tracking"""
    user_id: str
    completed_operations: int
    successful_operations: int
    days_since_first_use: int
    first_used_at: datetime
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.completed_operations == 0:
            return 1.0
        return self.successful_operations / self.completed_operations


@dataclass
class Operation:
    """Operation metadata for risk assessment"""
    name: str
    category: str
    estimated_duration: int  # seconds
    requires_validation: bool = True
    
    def validate(self):
        """Placeholder for operation validation"""
        return type('ValidationResult', (), {'is_valid': True, 'errors': []})()
    
    def get_plan(self) -> str:
        """Placeholder for operation plan"""
        return f"Execute {self.name} operation"
    
    def execute(self):
        """Placeholder for operation execution"""
        return Result(success=True, mode_used=ExecutionMode.SUPERVISED)
    
    def execute_with_retries(self, max_retries: int = 3):
        """Placeholder for autonomous execution with retries"""
        return Result(success=True, mode_used=ExecutionMode.AUTONOMOUS)


@dataclass
class Result:
    """Operation execution result"""
    success: bool
    mode_used: Optional[ExecutionMode] = None
    reason: Optional[str] = None
    errors: Optional[list] = None


@dataclass
class Execution:
    """Execution tracking"""
    operation: Operation
    mode: ExecutionMode
    failure_count: int = 0


@dataclass
class EscalationResult:
    """Mode escalation result"""
    escalated: bool
    old_mode: Optional[ExecutionMode] = None
    new_mode: Optional[ExecutionMode] = None
    message: Optional[str] = None


class ModeSelector:
    """
    Selects appropriate execution mode based on context
    
    Decision factors:
    - User experience level (0.0-1.0)
    - Operation risk score (0.0-1.0)
    - Operation category
    """
    
    # Risk weights for operation categories
    RISK_WEIGHTS = {
        "deploy": 0.9,
        "production": 0.9,
        "delete": 0.8,
        "cleanup": 0.1,
        "healthcheck": 0.1,
        "plan": 0.3,
        "test": 0.2
    }
    
    def calculate_risk_score(self, operation: Operation) -> float:
        """
        Calculate operation risk score
        
        Args:
            operation: Operation to assess
            
        Returns:
            float: Risk score 0.0 (low) to 1.0 (high)
        """
        op_name = operation.name.lower()
        
        # Check for high-risk keywords
        for keyword, weight in self.RISK_WEIGHTS.items():
            if keyword in op_name:
                return weight
        
        # Default medium risk
        return 0.5
    
    def get_user_experience_level(self, user: User) -> float:
        """
        Calculate user experience level
        
        Args:
            user: User profile
            
        Returns:
            float: Experience level 0.0 (novice) to 1.0 (expert)
            
        Experience formula:
        - 40% weight: operations completed (max 100)
        - 30% weight: days active (max 30)
        - 30% weight: success rate (only if user has operations)
        """
        operations = user.completed_operations
        days_active = user.days_since_first_use
        
        # New users should have 0.0 experience
        if operations == 0:
            return 0.0
        
        success_rate = user.success_rate
        
        experience = min(
            (operations / 100) * 0.4 +
            (days_active / 30) * 0.3 +
            success_rate * 0.3,
            1.0
        )
        return experience
    
    def select_mode(self, operation: Operation, user: User) -> ExecutionMode:
        """
        Select appropriate execution mode
        
        Decision matrix:
        - New users (0 operations): Always human-in-loop
        - High risk (risk > 0.7): Always supervised
        - Experienced + low risk (exp > 0.7, risk < 0.3): Autonomous
        - Default: Supervised
        
        Args:
            operation: Operation to execute
            user: User profile
            
        Returns:
            ExecutionMode: Recommended mode
        """
        risk = self.calculate_risk_score(operation)
        experience = self.get_user_experience_level(user)
        
        # Decision matrix
        if user.completed_operations == 0:
            # New users (0 operations) always human-in-loop
            return ExecutionMode.HUMAN_IN_LOOP
        elif risk > 0.7:
            # High-risk always supervised
            return ExecutionMode.SUPERVISED
        elif experience > 0.7 and risk < 0.3:
            # Experienced + low risk = autonomous
            return ExecutionMode.AUTONOMOUS
        else:
            # Default to supervised
            return ExecutionMode.SUPERVISED


class ModeEscalator:
    """
    Handles execution mode escalation on failures
    
    Escalation path:
    AUTONOMOUS → SUPERVISED → HUMAN_IN_LOOP
    """
    
    MAX_RETRIES = 3
    
    def should_escalate(self, execution: Execution) -> bool:
        """
        Check if mode escalation is needed
        
        Args:
            execution: Current execution state
            
        Returns:
            bool: True if escalation needed (failure_count >= MAX_RETRIES)
        """
        return execution.failure_count >= self.MAX_RETRIES
    
    def escalate_mode(self, current_mode: ExecutionMode) -> ExecutionMode:
        """
        Escalate to more restrictive execution mode
        
        Args:
            current_mode: Current execution mode
            
        Returns:
            ExecutionMode: Escalated mode
        """
        escalation_path = {
            ExecutionMode.AUTONOMOUS: ExecutionMode.SUPERVISED,
            ExecutionMode.SUPERVISED: ExecutionMode.HUMAN_IN_LOOP,
            ExecutionMode.HUMAN_IN_LOOP: ExecutionMode.HUMAN_IN_LOOP  # Can't escalate further
        }
        return escalation_path[current_mode]
    
    def get_escalation_message(self, old_mode: ExecutionMode, new_mode: ExecutionMode) -> str:
        """
        Generate user-friendly escalation message
        
        Args:
            old_mode: Previous execution mode
            new_mode: New execution mode after escalation
            
        Returns:
            str: Formatted escalation message
        """
        return (
            f"⚠️  Escalating execution mode: {old_mode.value} → {new_mode.value}\n"
            f"Reason: {self.MAX_RETRIES} consecutive failures detected\n"
            f"Action: Switching to {new_mode.description}"
        )


class UserProfile:
    """
    User profile management for experience tracking
    
    TODO: Integrate with Brain Tier 3 for persistence
    """
    
    def __init__(self, user_id: str, brain=None):
        self.user_id = user_id
        self._cache = {}
    
    def get_user(self) -> User:
        """
        Get or create user record
        
        Returns:
            User: User profile with experience data
        """
        # user_data = self.brain.tier3.get_user_profile(self.user_id)
        
        # For now, return mock data
        if self.user_id not in self._cache:
            self._cache[self.user_id] = self._create_new_user()
        return self._cache[self.user_id]
    
    def update_operation_stats(self, operation: str, success: bool):
        """
        Update user stats after operation
        
        Args:
            operation: Operation name
            success: Whether operation succeeded
        """
        user = self.get_user()
        user.completed_operations += 1
        if success:
            user.successful_operations += 1
        
        # self.brain.tier3.save_user_profile(self.user_id, user.__dict__)
        self._cache[self.user_id] = user
    
    def _create_new_user(self) -> User:
        """Create new user with defaults"""
        return User(
            user_id=self.user_id,
            completed_operations=0,
            successful_operations=0,
            days_since_first_use=0,
            first_used_at=datetime.now()
        )


class ExecutionModeManager:
    """
    Main manager for adaptive execution modes
    
    Features:
    - Smart mode selection based on user experience + risk
    - Automatic escalation after failures
    - User profile tracking
    - Integration with Phase 2 autonomous execution
    
    Usage:
        manager = ExecutionModeManager(config, user_profile)
        mode = manager.get_mode_for_operation(operation)
        result = manager.execute_with_mode(operation, mode)
    """
    
    def __init__(self, config: Dict[str, Any], user_profile: UserProfile):
        """
        Initialize execution mode manager
        
        Args:
            config: Configuration dictionary
            user_profile: User profile manager
        """
        self.selector = ModeSelector()
        self.escalator = ModeEscalator()
        self.config = config
        self.user_profile = user_profile
    
    def get_mode_for_operation(self, operation: Operation) -> ExecutionMode:
        """
        Get recommended execution mode for operation
        
        Args:
            operation: Operation to execute
            
        Returns:
            ExecutionMode: Recommended mode
        """
        # Check for user override in config
        if self.config.get("force_mode"):
            return ExecutionMode(self.config["force_mode"])
        
        # Use selector logic
        user = self.user_profile.get_user()
        return self.selector.select_mode(operation, user)
    
    def execute_with_mode(self, operation: Operation, mode: ExecutionMode) -> Result:
        """
        Execute operation with specified mode
        
        Args:
            operation: Operation to execute
            mode: Execution mode to use
            
        Returns:
            Result: Execution result
        """
        if mode == ExecutionMode.HUMAN_IN_LOOP:
            return self._execute_human_in_loop(operation)
        elif mode == ExecutionMode.SUPERVISED:
            return self._execute_supervised(operation)
        elif mode == ExecutionMode.AUTONOMOUS:
            return self._execute_autonomous(operation)
        else:
            raise ValueError(f"Unknown execution mode: {mode}")
    
    def handle_failure(self, execution: Execution) -> EscalationResult:
        """
        Handle execution failure with escalation logic
        
        Args:
            execution: Current execution state
            
        Returns:
            EscalationResult: Escalation decision and details
        """
        if self.escalator.should_escalate(execution):
            new_mode = self.escalator.escalate_mode(execution.mode)
            message = self.escalator.get_escalation_message(execution.mode, new_mode)
            
            return EscalationResult(
                escalated=True,
                old_mode=execution.mode,
                new_mode=new_mode,
                message=message
            )
        
        return EscalationResult(escalated=False)
    
    def _execute_human_in_loop(self, operation: Operation) -> Result:
        """
        Execute with human approval after each step
        
        TODO: Integrate with Phase 2 autonomous execution framework
        
        Args:
            operation: Operation to execute
            
        Returns:
            Result: Execution result
        """
        print(f"🛑 Pausing for approval: {operation.name}")
        approval = input("Continue? (y/n): ")
        if approval.lower() == 'y':
            result = operation.execute()
            self.user_profile.update_operation_stats(operation.name, result.success)
            return result
        else:
            return Result(success=False, reason="User cancelled", mode_used=ExecutionMode.HUMAN_IN_LOOP)
    
    def _execute_supervised(self, operation: Operation) -> Result:
        """
        Execute with validation, require final approval
        
        TODO: Integrate with Phase 2 autonomous execution framework
        
        Args:
            operation: Operation to execute
            
        Returns:
            Result: Execution result
        """
        # Validate operation first
        validation = operation.validate()
        if not validation.is_valid:
            return Result(success=False, errors=validation.errors, mode_used=ExecutionMode.SUPERVISED)
        
        # Show plan, require approval
        print(f"📋 Execution plan: {operation.get_plan()}")
        approval = input("Approve execution? (y/n): ")
        if approval.lower() == 'y':
            result = operation.execute()
            self.user_profile.update_operation_stats(operation.name, result.success)
            return result
        else:
            return Result(success=False, reason="User rejected plan", mode_used=ExecutionMode.SUPERVISED)
    
    def _execute_autonomous(self, operation: Operation) -> Result:
        """
        Execute fully autonomous with self-healing
        
        TODO: Integrate with Phase 2 autonomous execution framework
        
        Args:
            operation: Operation to execute
            
        Returns:
            Result: Execution result
        """
        result = operation.execute_with_retries(max_retries=3)
        self.user_profile.update_operation_stats(operation.name, result.success)
        return result
