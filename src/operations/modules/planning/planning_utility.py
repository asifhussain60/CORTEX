"""
Planning Utility

Fast, lightweight planning management for feature planning workflows.
Replaces heavy orchestrator (2,693 lines) with focused utility (~800 lines).

Core Operations:
- Create plan with metadata
- Load/Save YAML plans
- Validate plans (DoR/DoD)
- Generate Markdown views
- Approve/Complete lifecycle

Version: 3.0.0 (Utility Migration)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import yaml
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import CORTEX config
try:
    from src.config import config
    CORTEX_ROOT = Path(config.root_path)
    BRAIN_PATH = Path(config.brain_path)
except ImportError:
    # Fallback if config not available
    CORTEX_ROOT = Path(__file__).resolve().parents[4]
    BRAIN_PATH = CORTEX_ROOT / "cortex-brain"


@dataclass
class PlanResult:
    """Result of planning operation."""
    success: bool
    message: str
    plan_path: Optional[Path] = None
    plan_data: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)
    details: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of plan validation."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


# ===== HELPER FUNCTIONS =====

def detect_execution_mode(user_input: str) -> str:
    """
    Detect if user wants autonomous (chained) or approval-gated execution.
    
    Autonomous Triggers (case-insensitive):
    - "execute all phases autonomously"
    - "auto chained"
    - "execute all phases auto chained"
    - "all phases without user intervention"
    - "without user intervention"
    - "autonomous execution"
    - "end to end"
    - "run autonomously"
    - "auto execute all"
    
    Args:
        user_input: User's request/command text
        
    Returns:
        "autonomous" if triggers detected, "approval_gated" otherwise
        
    Examples:
        >>> detect_execution_mode("execute all phases autonomously")
        'autonomous'
        >>> detect_execution_mode("create plan for authentication")
        'approval_gated'
    """
    triggers = [
        r"execute\s+all\s+phases\s+autonomously",
        r"auto\s+chained",
        r"execute\s+all\s+phases\s+auto\s+chained",
        r"all\s+phases\s+without\s+(?:user\s+)?intervention",
        r"without\s+(?:user\s+)?intervention",
        r"autonomous(?:ly)?\s+execution?",
        r"end\s+to\s+end",
        r"run\s+autonomously",
        r"auto\s+execute\s+all"
    ]
    
    user_input_lower = user_input.lower()
    for pattern in triggers:
        if re.search(pattern, user_input_lower):
            logger.info(f"Autonomous execution mode detected: matched pattern '{pattern}'")
            return "autonomous"
    
    return "approval_gated"


def _truncate_filename(name: str, max_length: int = 30) -> str:
    """
    Truncate filename to max_length while preserving meaning.
    
    Algorithm:
    - Reserve 9 chars for timestamp: -{YYYYMMDD} (includes hyphen)
    - Reserve 5 chars for extension: .yaml
    - Total overhead: 14 chars
    - Available for name: max_length - 14
    
    For multi-word names:
    - Keep first word complete
    - Abbreviate remaining words to 3 chars each
    - Preserve readability
    
    Args:
        name: Sanitized filename base (lowercase, hyphens only)
        max_length: Maximum total filename length (default: 30)
        
    Returns:
        Truncated filename with timestamp: {name}-{YYYYMMDD}.yaml
        
    Examples:
        "user-authentication-feature" → "user-aut-fea-20251204.yaml"
        "payment-gateway-integration" → "payment-gat-int-20251204.yaml"
        "api" → "api-20251204.yaml"
    """
    timestamp = datetime.now().strftime("%Y%m%d")
    extension = ".yaml"
    
    # Calculate available space for name
    overhead = len(f"-{timestamp}{extension}")  # 14 chars
    available = max_length - overhead
    
    # If name fits, use as-is
    if len(name) <= available:
        return f"{name}-{timestamp}{extension}"
    
    # Multi-word truncation strategy
    words = name.split('-')
    
    if len(words) == 1:
        # Single word - simple truncation
        truncated = name[:available]
        return f"{truncated}-{timestamp}{extension}"
    
    # Multiple words - keep first, abbreviate rest
    result_words = [words[0]]  # Keep first word complete
    remaining_space = available - len(words[0])
    
    for word in words[1:]:
        abbreviated = word[:3]  # 3 chars per word
        test_name = '-'.join(result_words + [abbreviated])
        if len(test_name) <= available:
            result_words.append(abbreviated)
        else:
            break
    
    truncated = '-'.join(result_words)
    return f"{truncated}-{timestamp}{extension}"


# ===== CORE OPERATION 1: CREATE PLAN =====

def create_plan(
    feature_name: str,
    description: str = "",
    author: str = "CORTEX",
    complexity: str = "medium",
    user_input: str = ""
) -> PlanResult:
    """
    Create new plan with metadata.
    
    Args:
        feature_name: Name of feature being planned
        description: Feature description
        author: Plan author name
        complexity: Complexity level (low, medium, high)
        user_input: Original user request (used to detect execution mode)
        
    Returns:
        PlanResult with plan creation outcome
    """
    logger.info(f"📋 Creating plan: {feature_name}")
    
    # Detect execution mode from user input
    execution_mode = detect_execution_mode(user_input) if user_input else "approval_gated"
    logger.info(f"   Execution mode: {execution_mode}")
    
    try:
        # Create plan directory structure
        plans_dir = BRAIN_PATH / "documents" / "planning" / "features" / "active"
        plans_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename from feature name (30 char max)
        safe_name = re.sub(r'[^a-z0-9-]', '-', feature_name.lower())
        safe_name = re.sub(r'-+', '-', safe_name).strip('-')
        filename = _truncate_filename(safe_name, max_length=30)
        plan_path = plans_dir / filename
        
        # Check if plan already exists
        if plan_path.exists():
            return PlanResult(
                success=False,
                message=f"Plan already exists: {filename}",
                plan_path=plan_path
            )
        
        # Create plan structure
        plan_data = {
            "metadata": {
                "feature_name": feature_name,
                "description": description,
                "author": author,
                "created_at": datetime.now().isoformat(),
                "status": "draft",
                "complexity": complexity,
                "version": "1.0.0",
                "execution_mode": execution_mode,
                "tdd_enforced": True,
                "clean_architecture_required": True
            },
            "definition_of_ready": {
                "requirements_clear": False,
                "dependencies_identified": False,
                "design_approved": False,
                "resources_available": False,
                "tdd_test_scenarios_defined": False,
                "clean_architecture_planned": False,
                "solid_principles_reviewed": False
            },
            "phases": [],
            "definition_of_done": {
                "all_tests_passing_green_phase": False,
                "tdd_cycle_completed_red_green_refactor": False,
                "code_coverage_minimum_80_percent": False,
                "clean_architecture_validated": False,
                "solid_principles_verified": False,
                "documentation_complete": False,
                "code_reviewed": False,
                "deployed_to_staging": False
            },
            "risks": []
        }
        
        # Save plan
        with open(plan_path, 'w', encoding='utf-8') as f:
            yaml.dump(plan_data, f, default_flow_style=False, sort_keys=False)
        
        return PlanResult(
            success=True,
            message=f"Plan created: {filename}",
            plan_path=plan_path,
            plan_data=plan_data,
            details=f"Location: {plan_path}"
        )
        
    except Exception as e:
        return PlanResult(
            success=False,
            message=f"Plan creation failed: {str(e)}",
            errors=[str(e)]
        )


# ===== CORE OPERATION 2: LOAD PLAN =====

def load_plan(plan_path: Path) -> PlanResult:
    """
    Load plan from YAML file.
    
    Args:
        plan_path: Path to plan YAML file
        
    Returns:
        PlanResult with loaded plan data
    """
    logger.info(f"📂 Loading plan: {plan_path.name}")
    
    try:
        if not plan_path.exists():
            return PlanResult(
                success=False,
                message=f"Plan not found: {plan_path.name}",
                errors=[f"File does not exist: {plan_path}"]
            )
        
        # Load YAML
        with open(plan_path, 'r', encoding='utf-8') as f:
            plan_data = yaml.safe_load(f)
        
        if not plan_data:
            return PlanResult(
                success=False,
                message="Plan file is empty",
                errors=["YAML file contains no data"]
            )
        
        return PlanResult(
            success=True,
            message=f"Plan loaded: {plan_path.name}",
            plan_path=plan_path,
            plan_data=plan_data
        )
        
    except yaml.YAMLError as e:
        return PlanResult(
            success=False,
            message=f"YAML parsing error: {str(e)}",
            errors=[f"Invalid YAML syntax: {str(e)}"]
        )
    except Exception as e:
        return PlanResult(
            success=False,
            message=f"Plan loading failed: {str(e)}",
            errors=[str(e)]
        )


# ===== CORE OPERATION 3: SAVE PLAN =====

def save_plan(
    plan_data: Dict[str, Any],
    plan_path: Optional[Path] = None
) -> PlanResult:
    """
    Save plan to YAML file.
    
    Args:
        plan_data: Plan dictionary to save
        plan_path: Optional custom path (auto-generated if None)
        
    Returns:
        PlanResult with save outcome
    """
    logger.info("💾 Saving plan")
    
    try:
        # Auto-generate path if not provided
        if plan_path is None:
            metadata = plan_data.get("metadata", {})
            feature_name = metadata.get("feature_name", "unknown")
            safe_name = re.sub(r'[^a-z0-9-]', '-', feature_name.lower())
            safe_name = re.sub(r'-+', '-', safe_name).strip('-')
            filename = _truncate_filename(safe_name, max_length=30)
            
            status = metadata.get("status", "draft")
            if status == "active" or status == "approved":
                plans_dir = BRAIN_PATH / "documents" / "planning" / "features" / "active"
            elif status == "completed":
                plans_dir = BRAIN_PATH / "documents" / "planning" / "features" / "completed"
            else:
                plans_dir = BRAIN_PATH / "documents" / "planning" / "features" / "active"
            
            plans_dir.mkdir(parents=True, exist_ok=True)
            plan_path = plans_dir / filename
        
        # Update modified timestamp
        if "metadata" in plan_data:
            plan_data["metadata"]["modified_at"] = datetime.now().isoformat()
        
        # Save to YAML
        with open(plan_path, 'w', encoding='utf-8') as f:
            yaml.dump(plan_data, f, default_flow_style=False, sort_keys=False)
        
        return PlanResult(
            success=True,
            message=f"Plan saved: {plan_path.name}",
            plan_path=plan_path,
            plan_data=plan_data
        )
        
    except Exception as e:
        return PlanResult(
            success=False,
            message=f"Plan save failed: {str(e)}",
            errors=[str(e)]
        )


# ===== CORE OPERATION 4: VALIDATE PLAN =====

def validate_plan(plan_data: Dict[str, Any]) -> ValidationResult:
    """
    Validate plan structure and content.
    
    Args:
        plan_data: Plan dictionary to validate
        
    Returns:
        ValidationResult with validation outcome
    """
    logger.info("✅ Validating plan")
    
    errors = []
    warnings = []
    
    # Check required top-level fields
    required_fields = ["metadata", "definition_of_ready", "phases", "definition_of_done"]
    for field in required_fields:
        if field not in plan_data:
            errors.append(f"Missing required field: {field}")
    
    # Validate metadata
    if "metadata" in plan_data:
        metadata_errors = _validate_metadata(plan_data["metadata"])
        errors.extend(metadata_errors)
    
    # Validate Definition of Ready
    if "definition_of_ready" in plan_data:
        dor = plan_data["definition_of_ready"]
        if not isinstance(dor, dict):
            errors.append("definition_of_ready must be a dictionary")
        else:
            required_dor = [
                "requirements_clear", "dependencies_identified", "design_approved", 
                "resources_available", "tdd_test_scenarios_defined", "clean_architecture_planned",
                "solid_principles_reviewed"
            ]
            for field in required_dor:
                if field not in dor:
                    warnings.append(f"DoR missing field: {field}")
    
    # Validate phases
    if "phases" in plan_data:
        phase_errors = _validate_phases(plan_data["phases"])
        errors.extend(phase_errors)
    
    # Validate Definition of Done
    if "definition_of_done" in plan_data:
        dod = plan_data["definition_of_done"]
        if not isinstance(dod, dict):
            errors.append("definition_of_done must be a dictionary")
        else:
            required_dod = [
                "all_tests_passing_green_phase", "tdd_cycle_completed_red_green_refactor",
                "code_coverage_minimum_80_percent", "clean_architecture_validated",
                "solid_principles_verified", "documentation_complete", "code_reviewed"
            ]
            for field in required_dod:
                if field not in dod:
                    warnings.append(f"DoD missing field: {field}")
    
    # Check DoR/DoD completion
    if "definition_of_ready" in plan_data:
        dor_complete = all(plan_data["definition_of_ready"].values())
        if not dor_complete:
            warnings.append("Definition of Ready not fully satisfied")
    
    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )


def _validate_metadata(metadata: Dict[str, Any]) -> List[str]:
    """Validate metadata section."""
    errors = []
    
    required_fields = ["feature_name", "author", "created_at", "status"]
    for field in required_fields:
        if field not in metadata:
            errors.append(f"metadata missing required field: {field}")
    
    if "status" in metadata:
        valid_statuses = ["draft", "active", "approved", "in-progress", "completed", "cancelled"]
        if metadata["status"] not in valid_statuses:
            errors.append(f"metadata.status must be one of {valid_statuses}, got: {metadata['status']}")
    
    if "complexity" in metadata:
        valid_complexity = ["low", "medium", "high", "critical"]
        if metadata["complexity"] not in valid_complexity:
            errors.append(f"metadata.complexity must be one of {valid_complexity}")
    
    return errors


def _validate_phases(phases: List[Dict[str, Any]]) -> List[str]:
    """Validate phases section."""
    errors = []
    
    if not isinstance(phases, list):
        errors.append("phases must be a list")
        return errors
    
    if len(phases) == 0:
        # Empty phases is allowed for new plans
        return errors
    
    phase_numbers = []
    task_ids = set()
    
    for idx, phase in enumerate(phases):
        phase_label = f"phases[{idx}]"
        
        # Required phase fields
        required = ["phase_number", "phase_name"]
        for field in required:
            if field not in phase:
                errors.append(f"{phase_label} missing required field: {field}")
        
        # Validate phase number
        if "phase_number" in phase:
            if not isinstance(phase["phase_number"], int) or phase["phase_number"] < 1:
                errors.append(f"{phase_label}.phase_number must be positive integer")
            else:
                phase_numbers.append(phase["phase_number"])
        
        # Validate tasks if present
        if "tasks" in phase:
            task_errors = _validate_tasks(phase["tasks"], task_ids, phase_label)
            errors.extend(task_errors)
    
    # Check phase numbers are sequential
    if phase_numbers:
        phase_numbers.sort()
        expected = list(range(1, len(phase_numbers) + 1))
        if phase_numbers != expected:
            errors.append(f"Phase numbers must be sequential starting from 1, got: {phase_numbers}")
    
    return errors


def _validate_tasks(tasks: List[Dict[str, Any]], task_ids: set, phase_label: str) -> List[str]:
    """Validate tasks within a phase."""
    errors = []
    
    if not isinstance(tasks, list):
        errors.append(f"{phase_label}.tasks must be a list")
        return errors
    
    for idx, task in enumerate(tasks):
        task_label = f"{phase_label}.tasks[{idx}]"
        
        # Required task fields
        required = ["task_id", "task_name", "estimated_hours"]
        for field in required:
            if field not in task:
                errors.append(f"{task_label} missing required field: {field}")
        
        # Validate task_id format (e.g., "1.1", "1.2")
        if "task_id" in task:
            if not re.match(r'^\d+\.\d+$', str(task["task_id"])):
                errors.append(f"{task_label}.task_id must match pattern X.Y (e.g., 1.1)")
            elif task["task_id"] in task_ids:
                errors.append(f"{task_label}.task_id duplicate: {task['task_id']}")
            else:
                task_ids.add(task["task_id"])
        
        # Validate estimated hours
        if "estimated_hours" in task:
            hours = task["estimated_hours"]
            if not isinstance(hours, (int, float)) or hours < 0.25:
                errors.append(f"{task_label}.estimated_hours must be >= 0.25, got: {hours}")
    
    return errors


# ===== CORE OPERATION 5: GENERATE MARKDOWN =====

def generate_markdown(plan_data: Dict[str, Any]) -> str:
    """
    Generate Markdown view from plan data.
    
    Args:
        plan_data: Plan dictionary
        
    Returns:
        Markdown-formatted string
    """
    logger.info("📄 Generating Markdown")
    
    lines = []
    
    # Header
    metadata = plan_data.get("metadata", {})
    feature_name = metadata.get("feature_name", "Unknown Feature")
    lines.append(f"# {feature_name}")
    lines.append("")
    
    # Metadata section
    lines.append("## Metadata")
    lines.append("")
    lines.append(f"- **Author:** {metadata.get('author', 'Unknown')}")
    lines.append(f"- **Created:** {metadata.get('created_at', 'Unknown')}")
    lines.append(f"- **Status:** {metadata.get('status', 'draft').upper()}")
    lines.append(f"- **Complexity:** {metadata.get('complexity', 'medium').capitalize()}")
    if metadata.get("modified_at"):
        lines.append(f"- **Modified:** {metadata.get('modified_at')}")
    lines.append("")
    
    if metadata.get("description"):
        lines.append("## Description")
        lines.append("")
        lines.append(metadata["description"])
        lines.append("")
    
    # Definition of Ready
    lines.append("## Definition of Ready")
    lines.append("")
    dor = plan_data.get("definition_of_ready", {})
    for key, value in dor.items():
        status = "✅" if value else "❌"
        label = key.replace("_", " ").title()
        lines.append(f"- {status} {label}")
    lines.append("")
    
    # Phases
    phases = plan_data.get("phases", [])
    if phases:
        lines.append("## Phases")
        lines.append("")
        
        for phase in phases:
            phase_num = phase.get("phase_number", "?")
            phase_name = phase.get("phase_name", "Unknown")
            lines.append(f"### Phase {phase_num}: {phase_name}")
            lines.append("")
            
            if phase.get("description"):
                lines.append(phase["description"])
                lines.append("")
            
            # Tasks
            tasks = phase.get("tasks", [])
            if tasks:
                lines.append("**Tasks:**")
                lines.append("")
                for task in tasks:
                    task_id = task.get("task_id", "?")
                    task_name = task.get("task_name", "Unknown")
                    hours = task.get("estimated_hours", 0)
                    status = "✅" if task.get("completed", False) else "⏳"
                    lines.append(f"- {status} **{task_id}** - {task_name} ({hours}h)")
                lines.append("")
    
    # Definition of Done
    lines.append("## Definition of Done")
    lines.append("")
    dod = plan_data.get("definition_of_done", {})
    for key, value in dod.items():
        status = "✅" if value else "❌"
        label = key.replace("_", " ").title()
        lines.append(f"- {status} {label}")
    lines.append("")
    
    # Risks
    risks = plan_data.get("risks", [])
    if risks:
        lines.append("## Risks")
        lines.append("")
        for risk in risks:
            risk_id = risk.get("risk_id", "?")
            description = risk.get("description", "Unknown")
            likelihood = risk.get("likelihood", "unknown")
            impact = risk.get("impact", "unknown")
            lines.append(f"### Risk {risk_id}")
            lines.append(f"- **Description:** {description}")
            lines.append(f"- **Likelihood:** {likelihood.capitalize()}")
            lines.append(f"- **Impact:** {impact.capitalize()}")
            if risk.get("mitigation"):
                lines.append(f"- **Mitigation:** {risk['mitigation']}")
            lines.append("")
    
    return "\n".join(lines)


# ===== CORE OPERATION 6: APPROVE PLAN =====

def approve_plan(plan_filename: str) -> PlanResult:
    """
    Approve plan and move to active directory.
    
    Args:
        plan_filename: Name of plan file to approve
        
    Returns:
        PlanResult with approval outcome
    """
    logger.info(f"✅ Approving plan: {plan_filename}")
    
    try:
        # Find plan in active directory
        active_dir = BRAIN_PATH / "documents" / "planning" / "features" / "active"
        plan_path = active_dir / plan_filename
        
        if not plan_path.exists():
            return PlanResult(
                success=False,
                message=f"Plan not found in active directory: {plan_filename}",
                errors=[f"File does not exist: {plan_path}"]
            )
        
        # Load plan
        load_result = load_plan(plan_path)
        if not load_result.success:
            return load_result
        
        plan_data = load_result.plan_data
        
        # Validate plan before approval
        validation = validate_plan(plan_data)
        if not validation.valid:
            return PlanResult(
                success=False,
                message="Plan validation failed - cannot approve",
                errors=validation.errors,
                details=f"Errors: {len(validation.errors)}, Warnings: {len(validation.warnings)}"
            )
        
        # Check Definition of Ready
        dor = plan_data.get("definition_of_ready", {})
        if not all(dor.values()):
            return PlanResult(
                success=False,
                message="Definition of Ready not satisfied - cannot approve",
                errors=["Not all DoR criteria are met"],
                details=f"DoR status: {dor}"
            )
        
        # Update status
        plan_data["metadata"]["status"] = "approved"
        plan_data["metadata"]["approved_at"] = datetime.now().isoformat()
        
        # Save updated plan
        save_result = save_plan(plan_data, plan_path)
        if not save_result.success:
            return save_result
        
        return PlanResult(
            success=True,
            message=f"Plan approved: {plan_filename}",
            plan_path=plan_path,
            plan_data=plan_data,
            details=f"Status: approved, DoR satisfied, Validation passed"
        )
        
    except Exception as e:
        return PlanResult(
            success=False,
            message=f"Plan approval failed: {str(e)}",
            errors=[str(e)]
        )


# ===== CORE OPERATION 7: COMPLETE PLAN =====

def complete_plan(plan_filename: str) -> PlanResult:
    """
    Complete plan and move to completed directory.
    
    Args:
        plan_filename: Name of plan file to complete
        
    Returns:
        PlanResult with completion outcome
    """
    logger.info(f"🎉 Completing plan: {plan_filename}")
    
    try:
        # Find plan in active directory
        active_dir = BRAIN_PATH / "documents" / "planning" / "features" / "active"
        plan_path = active_dir / plan_filename
        
        if not plan_path.exists():
            return PlanResult(
                success=False,
                message=f"Plan not found in active directory: {plan_filename}",
                errors=[f"File does not exist: {plan_path}"]
            )
        
        # Load plan
        load_result = load_plan(plan_path)
        if not load_result.success:
            return load_result
        
        plan_data = load_result.plan_data
        
        # Check Definition of Done
        dod = plan_data.get("definition_of_done", {})
        if not all(dod.values()):
            return PlanResult(
                success=False,
                message="Definition of Done not satisfied - cannot complete",
                errors=["Not all DoD criteria are met"],
                details=f"DoD status: {dod}"
            )
        
        # Update status
        plan_data["metadata"]["status"] = "completed"
        plan_data["metadata"]["completed_at"] = datetime.now().isoformat()
        
        # Move to completed directory
        completed_dir = BRAIN_PATH / "documents" / "planning" / "features" / "completed"
        completed_dir.mkdir(parents=True, exist_ok=True)
        completed_path = completed_dir / plan_filename
        
        # Save to completed directory
        save_result = save_plan(plan_data, completed_path)
        if not save_result.success:
            return save_result
        
        # Remove from active directory
        plan_path.unlink()
        
        return PlanResult(
            success=True,
            message=f"Plan completed: {plan_filename}",
            plan_path=completed_path,
            plan_data=plan_data,
            details=f"Status: completed, DoD satisfied, Moved to: {completed_path.parent.name}/"
        )
        
    except Exception as e:
        return PlanResult(
            success=False,
            message=f"Plan completion failed: {str(e)}",
            errors=[str(e)]
        )


# CLI test execution
if __name__ == "__main__":
    print("=" * 60)
    print("Planning Utility - Direct Test")
    print("=" * 60)
    
    # Test 1: Create plan
    print("\n[Test 1] Create plan...")
    result = create_plan(
        feature_name="Test Feature Planning Utility",
        description="Testing the new lightweight planning utility",
        author="CORTEX Testing",
        complexity="low"
    )
    
    print(f"Success: {result.success}")
    print(f"Message: {result.message}")
    if result.plan_path:
        print(f"Path: {result.plan_path}")
    
    if not result.success:
        print(f"Errors: {result.errors}")
        exit(1)
    
    test_plan_path = result.plan_path
    
    # Test 2: Load plan
    print("\n" + "=" * 60)
    print("[Test 2] Load plan...")
    load_result = load_plan(test_plan_path)
    
    print(f"Success: {load_result.success}")
    print(f"Message: {load_result.message}")
    
    # Test 3: Validate plan
    print("\n" + "=" * 60)
    print("[Test 3] Validate plan...")
    validation = validate_plan(load_result.plan_data)
    
    print(f"Valid: {validation.valid}")
    print(f"Errors: {len(validation.errors)}")
    print(f"Warnings: {len(validation.warnings)}")
    if validation.warnings:
        print("Warnings:")
        for warning in validation.warnings:
            print(f"  - {warning}")
    
    # Test 4: Generate Markdown
    print("\n" + "=" * 60)
    print("[Test 4] Generate Markdown...")
    markdown = generate_markdown(load_result.plan_data)
    
    print(f"Generated {len(markdown)} characters")
    print("\nFirst 300 characters:")
    print(markdown[:300])
    
    # Test 5: Save plan (update)
    print("\n" + "=" * 60)
    print("[Test 5] Save plan...")
    load_result.plan_data["metadata"]["description"] = "Updated description"
    save_result = save_plan(load_result.plan_data, test_plan_path)
    
    print(f"Success: {save_result.success}")
    print(f"Message: {save_result.message}")
    
    # Cleanup test plan
    print("\n" + "=" * 60)
    print("[Cleanup] Removing test plan...")
    if test_plan_path.exists():
        test_plan_path.unlink()
        print("✅ Test plan removed")
    
    print("\n" + "=" * 60)
    print("✅ Utility tests complete")
    print("=" * 60)
