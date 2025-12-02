"""
TDD Utility

Fast, lightweight Test-Driven Development workflow management.
Replaces heavy orchestrator (602 lines) with focused utility (~400 lines).

Core Operations:
- State machine (RED → GREEN → REFACTOR → COMPLETE)
- Test execution and validation
- Test file generation
- Implementation tracking

Version: 3.0.0 (Utility Migration)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import subprocess
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import CORTEX config
try:
    from src.config import config
    CORTEX_ROOT = Path(config.root_path)
except ImportError:
    # Fallback if config not available
    CORTEX_ROOT = Path(__file__).resolve().parents[4]


class TDDPhase(Enum):
    """TDD cycle phases."""
    IDLE = "idle"
    RED = "red"  # Write failing test
    GREEN = "green"  # Implement code to pass
    REFACTOR = "refactor"  # Improve code quality
    COMPLETE = "complete"  # Feature complete


@dataclass
class TDDResult:
    """Result of TDD operation."""
    success: bool
    message: str
    phase: TDDPhase = TDDPhase.IDLE
    test_passed: Optional[bool] = None
    test_output: Optional[str] = None
    details: Optional[str] = None
    errors: List[str] = field(default_factory=list)


@dataclass
class TDDSession:
    """TDD session state."""
    session_id: str
    feature_name: str
    test_file: Path
    impl_file: Path
    current_phase: TDDPhase = TDDPhase.IDLE
    tests_written: int = 0
    tests_passing: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


# ===== CORE OPERATION 1: START TDD SESSION =====

def start_tdd_session(
    feature_name: str,
    test_file: Path,
    impl_file: Path
) -> TDDResult:
    """
    Start new TDD session.
    
    Args:
        feature_name: Name of feature being developed
        test_file: Path to test file
        impl_file: Path to implementation file
        
    Returns:
        TDDResult with session creation outcome
    """
    logger.info(f"🧪 Starting TDD session: {feature_name}")
    
    try:
        # Generate session ID
        session_id = f"tdd-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Create session object
        session = TDDSession(
            session_id=session_id,
            feature_name=feature_name,
            test_file=test_file,
            impl_file=impl_file,
            current_phase=TDDPhase.RED
        )
        
        # Save session state
        session_file = CORTEX_ROOT / ".cortex" / "tdd" / f"{session_id}.json"
        session_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(session_file, 'w') as f:
            json.dump({
                "session_id": session.session_id,
                "feature_name": session.feature_name,
                "test_file": str(session.test_file),
                "impl_file": str(session.impl_file),
                "current_phase": session.current_phase.value,
                "tests_written": session.tests_written,
                "tests_passing": session.tests_passing,
                "created_at": session.created_at,
                "updated_at": session.updated_at
            }, f, indent=2)
        
        details = f"Session ID: {session_id}\nPhase: RED\nTest file: {test_file}\nImplementation: {impl_file}"
        
        return TDDResult(
            success=True,
            message=f"TDD session started: {session_id}",
            phase=TDDPhase.RED,
            details=details
        )
        
    except Exception as e:
        return TDDResult(
            success=False,
            message=f"Failed to start TDD session: {str(e)}",
            errors=[str(e)]
        )


# ===== CORE OPERATION 2: RUN TESTS =====

def run_tests(
    test_file: Path,
    test_name: Optional[str] = None
) -> TDDResult:
    """
    Run tests and return results.
    
    Args:
        test_file: Path to test file
        test_name: Optional specific test to run
        
    Returns:
        TDDResult with test execution outcome
    """
    logger.info(f"🧪 Running tests: {test_file.name}")
    
    try:
        if not test_file.exists():
            return TDDResult(
                success=False,
                message=f"Test file not found: {test_file}",
                errors=[f"File does not exist: {test_file}"]
            )
        
        # Build pytest command
        cmd = ["pytest", str(test_file), "-v"]
        if test_name:
            cmd.extend(["-k", test_name])
        
        # Run tests
        result = subprocess.run(
            cmd,
            cwd=CORTEX_ROOT,
            capture_output=True,
            text=True,
            check=False
        )
        
        # Parse results
        test_passed = result.returncode == 0
        output = result.stdout + "\n" + result.stderr
        
        # Determine phase based on results
        if test_passed:
            phase = TDDPhase.GREEN
            message = "✅ All tests passed - GREEN phase"
        else:
            phase = TDDPhase.RED
            message = "❌ Tests failed - RED phase"
        
        details = f"Exit code: {result.returncode}\nOutput length: {len(output)} chars"
        
        return TDDResult(
            success=True,
            message=message,
            phase=phase,
            test_passed=test_passed,
            test_output=output,
            details=details
        )
        
    except FileNotFoundError:
        return TDDResult(
            success=False,
            message="pytest not found - install with: pip install pytest",
            errors=["pytest command not available"]
        )
    except Exception as e:
        return TDDResult(
            success=False,
            message=f"Test execution failed: {str(e)}",
            errors=[str(e)]
        )


# ===== CORE OPERATION 3: TRANSITION PHASE =====

def transition_phase(
    session_id: str,
    target_phase: TDDPhase,
    validation: bool = True
) -> TDDResult:
    """
    Transition TDD session to new phase.
    
    Args:
        session_id: Session identifier
        target_phase: Phase to transition to
        validation: Whether to validate transition is legal
        
    Returns:
        TDDResult with transition outcome
    """
    logger.info(f"🔄 Transitioning to {target_phase.value.upper()} phase")
    
    try:
        # Load session
        session_file = CORTEX_ROOT / ".cortex" / "tdd" / f"{session_id}.json"
        
        if not session_file.exists():
            return TDDResult(
                success=False,
                message=f"Session not found: {session_id}",
                errors=[f"No session file: {session_file}"]
            )
        
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        current_phase = TDDPhase(session_data["current_phase"])
        
        # Validate transition if requested
        if validation:
            valid_transitions = {
                TDDPhase.IDLE: [TDDPhase.RED],
                TDDPhase.RED: [TDDPhase.GREEN, TDDPhase.REFACTOR],
                TDDPhase.GREEN: [TDDPhase.REFACTOR, TDDPhase.RED],
                TDDPhase.REFACTOR: [TDDPhase.RED, TDDPhase.COMPLETE],
                TDDPhase.COMPLETE: []
            }
            
            if target_phase not in valid_transitions.get(current_phase, []):
                return TDDResult(
                    success=False,
                    message=f"Invalid transition: {current_phase.value} → {target_phase.value}",
                    phase=current_phase,
                    errors=[f"Cannot transition from {current_phase.value} to {target_phase.value}"]
                )
        
        # Update session
        session_data["current_phase"] = target_phase.value
        session_data["updated_at"] = datetime.now().isoformat()
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        return TDDResult(
            success=True,
            message=f"Phase transition: {current_phase.value} → {target_phase.value}",
            phase=target_phase,
            details=f"Session updated: {session_id}"
        )
        
    except Exception as e:
        return TDDResult(
            success=False,
            message=f"Phase transition failed: {str(e)}",
            errors=[str(e)]
        )


# ===== CORE OPERATION 4: GET SESSION STATUS =====

def get_session_status(session_id: str) -> TDDResult:
    """
    Get current TDD session status.
    
    Args:
        session_id: Session identifier
        
    Returns:
        TDDResult with session status
    """
    logger.info(f"📊 Getting session status: {session_id}")
    
    try:
        session_file = CORTEX_ROOT / ".cortex" / "tdd" / f"{session_id}.json"
        
        if not session_file.exists():
            return TDDResult(
                success=False,
                message=f"Session not found: {session_id}",
                errors=[f"No session file: {session_file}"]
            )
        
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        phase = TDDPhase(session_data["current_phase"])
        
        details = f"""Session: {session_id}
Feature: {session_data['feature_name']}
Phase: {phase.value.upper()}
Tests Written: {session_data['tests_written']}
Tests Passing: {session_data['tests_passing']}
Created: {session_data['created_at']}
Updated: {session_data['updated_at']}"""
        
        return TDDResult(
            success=True,
            message=f"Session active: {phase.value.upper()} phase",
            phase=phase,
            details=details
        )
        
    except Exception as e:
        return TDDResult(
            success=False,
            message=f"Failed to get session status: {str(e)}",
            errors=[str(e)]
        )


# ===== CORE OPERATION 5: GENERATE TEST SKELETON =====

def generate_test_skeleton(
    feature_name: str,
    test_file: Path,
    impl_file: Path
) -> TDDResult:
    """
    Generate test file skeleton.
    
    Args:
        feature_name: Name of feature
        test_file: Path to test file
        impl_file: Path to implementation file
        
    Returns:
        TDDResult with skeleton generation outcome
    """
    logger.info(f"📝 Generating test skeleton: {test_file.name}")
    
    try:
        if test_file.exists():
            return TDDResult(
                success=False,
                message=f"Test file already exists: {test_file.name}",
                errors=["File exists - use different name or remove existing file"]
            )
        
        # Extract class name from implementation file
        impl_stem = impl_file.stem
        class_name = "".join(word.title() for word in impl_stem.split("_"))
        
        # Generate skeleton
        skeleton = f"""# Test file for {feature_name}
# Generated by CORTEX TDD Utility

import pytest
from pathlib import Path
import sys

# Add source to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from {impl_stem} import {class_name}


class Test{class_name}:
    \"\"\"Test suite for {feature_name}\"\"\"
    
    @pytest.fixture
    def instance(self):
        \"\"\"Create test instance\"\"\"
        return {class_name}()
    
    def test_placeholder(self, instance):
        \"\"\"Placeholder test - replace with actual tests\"\"\"
        assert instance is not None
"""
        
        # Create test file
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text(skeleton)
        
        return TDDResult(
            success=True,
            message=f"Test skeleton created: {test_file.name}",
            phase=TDDPhase.RED,
            details=f"File: {test_file}\nClass: Test{class_name}\nLines: {len(skeleton.splitlines())}"
        )
        
    except Exception as e:
        return TDDResult(
            success=False,
            message=f"Skeleton generation failed: {str(e)}",
            errors=[str(e)]
        )


# ===== CORE OPERATION 6: UPDATE SESSION METRICS =====

def update_session_metrics(
    session_id: str,
    tests_written: Optional[int] = None,
    tests_passing: Optional[int] = None
) -> TDDResult:
    """
    Update TDD session metrics.
    
    Args:
        session_id: Session identifier
        tests_written: Number of tests written (optional)
        tests_passing: Number of tests passing (optional)
        
    Returns:
        TDDResult with update outcome
    """
    logger.info(f"📊 Updating session metrics: {session_id}")
    
    try:
        session_file = CORTEX_ROOT / ".cortex" / "tdd" / f"{session_id}.json"
        
        if not session_file.exists():
            return TDDResult(
                success=False,
                message=f"Session not found: {session_id}",
                errors=[f"No session file: {session_file}"]
            )
        
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        # Update metrics
        if tests_written is not None:
            session_data["tests_written"] = tests_written
        if tests_passing is not None:
            session_data["tests_passing"] = tests_passing
        
        session_data["updated_at"] = datetime.now().isoformat()
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        details = f"Tests written: {session_data['tests_written']}\nTests passing: {session_data['tests_passing']}"
        
        return TDDResult(
            success=True,
            message="Session metrics updated",
            details=details
        )
        
    except Exception as e:
        return TDDResult(
            success=False,
            message=f"Metrics update failed: {str(e)}",
            errors=[str(e)]
        )


# ===== CORE OPERATION 7: COMPLETE SESSION =====

def complete_session(session_id: str) -> TDDResult:
    """
    Complete TDD session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        TDDResult with completion outcome
    """
    logger.info(f"✅ Completing session: {session_id}")
    
    try:
        session_file = CORTEX_ROOT / ".cortex" / "tdd" / f"{session_id}.json"
        
        if not session_file.exists():
            return TDDResult(
                success=False,
                message=f"Session not found: {session_id}",
                errors=[f"No session file: {session_file}"]
            )
        
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        # Update to COMPLETE phase
        session_data["current_phase"] = TDDPhase.COMPLETE.value
        session_data["updated_at"] = datetime.now().isoformat()
        session_data["completed_at"] = datetime.now().isoformat()
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        details = f"""Session: {session_id}
Feature: {session_data['feature_name']}
Tests Written: {session_data['tests_written']}
Tests Passing: {session_data['tests_passing']}
Duration: {session_data['created_at']} → {session_data['completed_at']}"""
        
        return TDDResult(
            success=True,
            message=f"TDD session completed: {session_id}",
            phase=TDDPhase.COMPLETE,
            details=details
        )
        
    except Exception as e:
        return TDDResult(
            success=False,
            message=f"Session completion failed: {str(e)}",
            errors=[str(e)]
        )


# CLI test execution
if __name__ == "__main__":
    print("=" * 60)
    print("TDD Utility - Direct Test")
    print("=" * 60)
    
    # Test 1: Start session
    print("\n[Test 1] Start TDD session...")
    test_file = Path(CORTEX_ROOT / "tests" / "test_example.py")
    impl_file = Path(CORTEX_ROOT / "src" / "example.py")
    
    result = start_tdd_session(
        feature_name="Example Feature",
        test_file=test_file,
        impl_file=impl_file
    )
    
    print(f"Success: {result.success}")
    print(f"Message: {result.message}")
    print(f"Phase: {result.phase.value}")
    if result.details:
        print(f"\nDetails:\n{result.details}")
    
    if not result.success:
        print("❌ Session creation failed")
        exit(1)
    
    # Extract session ID from details
    session_id = result.details.split("Session ID: ")[1].split("\n")[0]
    
    # Test 2: Get session status
    print("\n" + "=" * 60)
    print("[Test 2] Get session status...")
    status_result = get_session_status(session_id)
    
    print(f"Success: {status_result.success}")
    print(f"Message: {status_result.message}")
    print(f"Phase: {status_result.phase.value}")
    
    # Test 3: Transition phase
    print("\n" + "=" * 60)
    print("[Test 3] Transition to GREEN phase...")
    transition_result = transition_phase(session_id, TDDPhase.GREEN)
    
    print(f"Success: {transition_result.success}")
    print(f"Message: {transition_result.message}")
    print(f"Phase: {transition_result.phase.value}")
    
    # Test 4: Update metrics
    print("\n" + "=" * 60)
    print("[Test 4] Update session metrics...")
    metrics_result = update_session_metrics(session_id, tests_written=3, tests_passing=3)
    
    print(f"Success: {metrics_result.success}")
    print(f"Message: {metrics_result.message}")
    if metrics_result.details:
        print(f"Details:\n{metrics_result.details}")
    
    # Test 5: Complete session
    print("\n" + "=" * 60)
    print("[Test 5] Complete session...")
    complete_result = complete_session(session_id)
    
    print(f"Success: {complete_result.success}")
    print(f"Message: {complete_result.message}")
    print(f"Phase: {complete_result.phase.value}")
    
    # Cleanup
    print("\n" + "=" * 60)
    print("[Cleanup] Removing test session...")
    session_file = CORTEX_ROOT / ".cortex" / "tdd" / f"{session_id}.json"
    if session_file.exists():
        session_file.unlink()
        print("✅ Test session removed")
    
    print("\n" + "=" * 60)
    print("✅ Utility tests complete")
    print("=" * 60)
