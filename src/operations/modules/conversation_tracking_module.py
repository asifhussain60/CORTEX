"""
Conversation Tracking Setup Module

Enables ambient conversation capture for CORTEX.

SOLID Principles:
- Single Responsibility: Only handles conversation tracking setup
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import subprocess
import os
import sys
from pathlib import Path
from typing import Dict, Any, Tuple, List
from datetime import datetime

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationStatus,
    OperationPhase
)


class ConversationTrackingModule(BaseOperationModule):
    """
    Setup module for conversation tracking (ambient capture).
    
    Responsibilities:
    1. Check if ambient capture daemon is available
    2. Verify daemon dependencies installed
    3. Start daemon if not running
    4. Provide status and instructions
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="conversation_tracking",
            name="Conversation Tracking Setup",
            description="Enable ambient conversation capture daemon",
            phase=OperationPhase.FEATURES,
            priority=20,  # After brain initialization
            dependencies=["brain_initialization"],
            optional=True,  # Optional feature
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate prerequisites for conversation tracking.
        
        Checks:
        1. Project root exists
        2. Brain initialized (conversation database exists)
        """
        issues = []
        
        # Check project root
        project_root = context.get('project_root')
        if not project_root:
            issues.append("Project root not found in context")
            return False, issues
        
        # Check brain initialization
        brain_initialized = context.get('brain_initialized', False)
        if not brain_initialized:
            issues.append("Brain must be initialized before enabling conversation tracking")
            return False, issues
        
        return True, []
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute conversation tracking setup.
        
        Steps:
        1. Check if daemon script exists
        2. Check if daemon is already running
        3. Start daemon if needed
        4. Verify daemon started successfully
        """
        start_time = datetime.now()
        project_root = Path(context['project_root'])
        
        try:
            # Find daemon script
            daemon_script = project_root / "scripts" / "cortex" / "auto_capture_daemon.py"
            if not daemon_script.exists():
                self.log_warning("Ambient capture daemon script not found")
                return OperationResult(
                    success=True,
                    status=OperationStatus.SKIPPED,
                    message="Conversation tracking unavailable (daemon script not found)",
                    data={'daemon_available': False},
                    warnings=["Ambient capture daemon not available"],
                    duration_seconds=(datetime.now() - start_time).total_seconds()
                )
            
            # Check if daemon is already running
            is_running = self._is_daemon_running()
            if is_running:
                self.log_info("Ambient capture daemon already running")
                
                context['conversation_tracking_enabled'] = True
                context['daemon_status'] = 'running'
                
                return OperationResult(
                    success=True,
                    status=OperationStatus.SUCCESS,
                    message="Conversation tracking already enabled",
                    data={
                        'daemon_available': True,
                        'daemon_running': True,
                        'daemon_script': str(daemon_script)
                    },
                    duration_seconds=(datetime.now() - start_time).total_seconds()
                )
            
            # Attempt to start daemon (best effort - don't block on failure)
            self.log_info("Starting ambient capture daemon...")
            start_success, start_output = self._start_daemon(daemon_script)
            
            if not start_success:
                self.log_warning(f"Could not start daemon: {start_output}")
                return OperationResult(
                    success=True,
                    status=OperationStatus.WARNING,
                    message="Conversation tracking setup incomplete",
                    data={
                        'daemon_available': True,
                        'daemon_running': False,
                        'daemon_script': str(daemon_script),
                        'start_output': start_output
                    },
                    warnings=[
                        "Could not start ambient capture daemon automatically",
                        f"Manual start: python {daemon_script}"
                    ],
                    duration_seconds=(datetime.now() - start_time).total_seconds()
                )
            
            # Verify daemon started
            import time
            time.sleep(2)  # Give daemon time to start
            is_running_now = self._is_daemon_running()
            
            if is_running_now:
                self.log_info("Ambient capture daemon started successfully")
                
                context['conversation_tracking_enabled'] = True
                context['daemon_status'] = 'running'
                
                return OperationResult(
                    success=True,
                    status=OperationStatus.SUCCESS,
                    message="Conversation tracking enabled successfully",
                    data={
                        'daemon_available': True,
                        'daemon_running': True,
                        'daemon_script': str(daemon_script),
                        'started_now': True
                    },
                    duration_seconds=(datetime.now() - start_time).total_seconds()
                )
            else:
                self.log_warning("Daemon started but not responding")
                return OperationResult(
                    success=True,
                    status=OperationStatus.WARNING,
                    message="Daemon started but verification failed",
                    data={
                        'daemon_available': True,
                        'daemon_running': False,
                        'daemon_script': str(daemon_script)
                    },
                    warnings=["Daemon may still be starting up"],
                    duration_seconds=(datetime.now() - start_time).total_seconds()
                )
            
        except Exception as e:
            self.log_error(f"Conversation tracking setup failed: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Conversation tracking setup failed: {str(e)}",
                errors=[str(e)],
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )
    
    def _is_daemon_running(self) -> bool:
        """Check if ambient capture daemon is running."""
        try:
            if sys.platform.startswith('win'):
                # Windows: check for python process running auto_capture_daemon
                result = subprocess.run(
                    ['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return 'auto_capture_daemon' in result.stdout
            else:
                # Unix: check for process
                result = subprocess.run(
                    ['pgrep', '-f', 'auto_capture_daemon'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return result.returncode == 0
        except subprocess.SubprocessError:
            return False
    
    def _start_daemon(self, daemon_script: Path) -> Tuple[bool, str]:
        """Start the ambient capture daemon."""
        try:
            if sys.platform.startswith('win'):
                # Windows: start detached process
                subprocess.Popen(
                    [sys.executable, str(daemon_script)],
                    creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.DETACHED_PROCESS,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                # Unix: start background process
                subprocess.Popen(
                    [sys.executable, str(daemon_script)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
            return True, "Daemon start command issued"
        except subprocess.SubprocessError as e:
            return False, str(e)
