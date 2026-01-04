"""
CORTEX 5.0 Planner Mode Detector

Purpose: Automatically detect whether a plan directory represents an Epic
         (hierarchical multi-plan coordination) or Feature (single-plan execution).

Version: 5.0.0
Author: Asif Hussain
Created: January 4, 2026

Detection Logic:
- Epic Mode: Multiple NN-{name}/ child folders with own 00-*.md plans
- Feature Mode: Single plan with context/, artifacts/, reports/, tracking/
"""

import logging
import re
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


class PlannerMode(Enum):
    """Planning system operational modes."""
    EPIC = "epic"          # Multi-plan strategic coordination
    FEATURE = "feature"    # Single-plan tactical execution
    UNKNOWN = "unknown"    # Cannot determine mode


def detect_planner_mode(plan_path: Path) -> PlannerMode:
    """
    Detect planning mode based on folder structure analysis.
    
    Epic Mode Indicators:
    - Multiple immediate child folders matching pattern: NN-{name}/ or NNA-{name}/
    - Master plan file: 00-MASTER-*.md or 00-EPIC-*.md in root
    - tracking/ folder with epic-progress-tracker.json
    - Child folders contain their own 00-*.md plan files
    - Typically 2+ child plans (minimum for epic coordination)
    
    Feature Mode Indicators:
    - Single plan file: 00-{feature-name}.md in root
    - Standard subfolders: context/, artifacts/, reports/, tracking/
    - tracking/progress-tracker.json (not epic-progress-tracker.json)
    - No NN-{name}/ child plan folders
    
    Args:
        plan_path: Path to plan directory to analyze
        
    Returns:
        PlannerMode enum value (EPIC, FEATURE, or UNKNOWN)
        
    Examples:
        >>> detect_planner_mode(Path("CORTEX-5.0"))
        PlannerMode.EPIC
        
        >>> detect_planner_mode(Path("test-coverage-sprint"))
        PlannerMode.FEATURE
    """
    # Validate path exists and is directory
    if not plan_path.exists():
        logger.warning(f"Path does not exist: {plan_path}")
        return PlannerMode.UNKNOWN
    
    if not plan_path.is_dir():
        logger.warning(f"Path is not a directory: {plan_path}")
        return PlannerMode.UNKNOWN
    
    # Find master plan file(s)
    master_plans = list(plan_path.glob("00-*.md"))
    if not master_plans:
        logger.debug(f"No master plan found in {plan_path}")
        return PlannerMode.UNKNOWN
    
    # Check for epic-style child plan folders
    # Pattern: NN-{name}/ or NNA-{name}/ (e.g., "01-", "00A-", "02B-")
    child_plan_pattern = re.compile(r'^\d{2}[A-Z]?-')
    
    child_plan_folders = [
        d for d in plan_path.iterdir()
        if d.is_dir() and child_plan_pattern.match(d.name)
    ]
    
    logger.debug(f"Found {len(child_plan_folders)} potential child plan folders")
    
    # Check if child folders contain their own master plans
    child_plans_with_master = []
    for child_folder in child_plan_folders:
        child_master_plans = list(child_folder.glob("00-*.md"))
        if child_master_plans:
            child_plans_with_master.append((child_folder, child_master_plans[0]))
            logger.debug(f"Child plan found: {child_folder.name}")
    
    # Check for tracker files
    tracking_dir = plan_path / "tracking"
    epic_tracker = tracking_dir / "epic-progress-tracker.json"
    feature_tracker = tracking_dir / "progress-tracker.json"
    
    has_epic_tracker = epic_tracker.exists()
    has_feature_tracker = feature_tracker.exists()
    
    # Check for feature-mode standard folders
    has_context = (plan_path / "context").exists()
    has_artifacts = (plan_path / "artifacts").exists()
    has_reports = (plan_path / "reports").exists()
    
    # Decision Logic
    # ---------------
    
    # Strong Epic indicators
    if len(child_plans_with_master) >= 2 and has_epic_tracker:
        logger.info(f"Detected EPIC mode: {len(child_plans_with_master)} child plans with epic tracker")
        return PlannerMode.EPIC
    
    # Epic by structure alone (missing tracker)
    if len(child_plans_with_master) >= 2:
        logger.info(f"Detected EPIC mode: {len(child_plans_with_master)} child plans (no epic tracker)")
        return PlannerMode.EPIC
    
    # Strong Feature indicators
    if has_context and has_feature_tracker and len(child_plans_with_master) == 0:
        logger.info("Detected FEATURE mode: standard folder structure with feature tracker")
        return PlannerMode.FEATURE
    
    # Feature by structure (common pattern)
    if has_context and (has_artifacts or has_reports) and len(child_plans_with_master) == 0:
        logger.info("Detected FEATURE mode: standard folder structure")
        return PlannerMode.FEATURE
    
    # Ambiguous case - default to Feature if has standard folders
    if has_context or has_artifacts or has_reports:
        logger.warning("Ambiguous structure, defaulting to FEATURE mode")
        return PlannerMode.FEATURE
    
    # Completely ambiguous
    logger.warning(f"Cannot determine planner mode for {plan_path}")
    return PlannerMode.UNKNOWN


def analyze_plan_structure(plan_path: Path) -> dict:
    """
    Perform detailed analysis of plan directory structure.
    
    Useful for debugging mode detection or providing detailed diagnostics.
    
    Args:
        plan_path: Path to plan directory
        
    Returns:
        Dictionary containing structural analysis
    """
    analysis = {
        "path": str(plan_path),
        "exists": plan_path.exists(),
        "is_dir": plan_path.is_dir() if plan_path.exists() else False,
        "master_plans": [],
        "child_plan_folders": [],
        "child_plans_with_master": [],
        "tracking": {
            "has_tracking_dir": False,
            "has_epic_tracker": False,
            "has_feature_tracker": False
        },
        "standard_folders": {
            "context": False,
            "artifacts": False,
            "reports": False
        },
        "detected_mode": "unknown"
    }
    
    if not plan_path.exists() or not plan_path.is_dir():
        return analysis
    
    # Master plans
    master_plans = list(plan_path.glob("00-*.md"))
    analysis["master_plans"] = [p.name for p in master_plans]
    
    # Child plan folders
    child_plan_pattern = re.compile(r'^\d{2}[A-Z]?-')
    child_plan_folders = [
        d.name for d in plan_path.iterdir()
        if d.is_dir() and child_plan_pattern.match(d.name)
    ]
    analysis["child_plan_folders"] = child_plan_folders
    
    # Child plans with master plans
    for folder_name in child_plan_folders:
        folder_path = plan_path / folder_name
        child_masters = list(folder_path.glob("00-*.md"))
        if child_masters:
            analysis["child_plans_with_master"].append({
                "folder": folder_name,
                "master_plan": child_masters[0].name
            })
    
    # Tracking files
    tracking_dir = plan_path / "tracking"
    analysis["tracking"]["has_tracking_dir"] = tracking_dir.exists()
    if tracking_dir.exists():
        analysis["tracking"]["has_epic_tracker"] = (tracking_dir / "epic-progress-tracker.json").exists()
        analysis["tracking"]["has_feature_tracker"] = (tracking_dir / "progress-tracker.json").exists()
    
    # Standard folders
    analysis["standard_folders"]["context"] = (plan_path / "context").exists()
    analysis["standard_folders"]["artifacts"] = (plan_path / "artifacts").exists()
    analysis["standard_folders"]["reports"] = (plan_path / "reports").exists()
    
    # Detected mode
    mode = detect_planner_mode(plan_path)
    analysis["detected_mode"] = mode.value
    
    return analysis


def validate_epic_structure(plan_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate that an epic plan has proper structure.
    
    Args:
        plan_path: Path to epic plan directory
        
    Returns:
        Tuple of (is_valid, list of validation errors)
    """
    errors = []
    
    # Check mode
    mode = detect_planner_mode(plan_path)
    if mode != PlannerMode.EPIC:
        errors.append(f"Not detected as epic mode (detected: {mode.value})")
        return False, errors
    
    # Check master plan
    master_plans = list(plan_path.glob("00-*.md"))
    if not master_plans:
        errors.append("Missing master plan file (00-*.md)")
    elif len(master_plans) > 1:
        errors.append(f"Multiple master plans found: {[p.name for p in master_plans]}")
    
    # Check tracking directory
    tracking_dir = plan_path / "tracking"
    if not tracking_dir.exists():
        errors.append("Missing tracking/ directory")
    else:
        # Check for epic tracker
        epic_tracker = tracking_dir / "epic-progress-tracker.json"
        if not epic_tracker.exists():
            errors.append("Missing tracking/epic-progress-tracker.json")
    
    # Check child plans
    child_plan_pattern = re.compile(r'^\d{2}[A-Z]?-')
    child_plan_folders = [
        d for d in plan_path.iterdir()
        if d.is_dir() and child_plan_pattern.match(d.name)
    ]
    
    if len(child_plan_folders) < 2:
        errors.append(f"Epic requires at least 2 child plans (found {len(child_plan_folders)})")
    
    # Validate each child plan
    for child_folder in child_plan_folders:
        child_masters = list(child_folder.glob("00-*.md"))
        if not child_masters:
            errors.append(f"Child plan {child_folder.name} missing master plan (00-*.md)")
        
        child_tracking = child_folder / "tracking"
        if not child_tracking.exists():
            errors.append(f"Child plan {child_folder.name} missing tracking/ directory")
    
    return len(errors) == 0, errors


def validate_feature_structure(plan_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate that a feature plan has proper structure.
    
    Args:
        plan_path: Path to feature plan directory
        
    Returns:
        Tuple of (is_valid, list of validation errors)
    """
    errors = []
    
    # Check mode
    mode = detect_planner_mode(plan_path)
    if mode != PlannerMode.FEATURE:
        errors.append(f"Not detected as feature mode (detected: {mode.value})")
        return False, errors
    
    # Check master plan
    master_plans = list(plan_path.glob("00-*.md"))
    if not master_plans:
        errors.append("Missing master plan file (00-*.md)")
    elif len(master_plans) > 1:
        errors.append(f"Multiple master plans found: {[p.name for p in master_plans]}")
    
    # Check standard folders (at least one should exist)
    has_context = (plan_path / "context").exists()
    has_artifacts = (plan_path / "artifacts").exists()
    has_reports = (plan_path / "reports").exists()
    has_tracking = (plan_path / "tracking").exists()
    
    if not (has_context or has_artifacts or has_reports or has_tracking):
        errors.append("Missing standard folders (context/, artifacts/, reports/, or tracking/)")
    
    # Check for feature tracker if tracking exists
    if has_tracking:
        feature_tracker = plan_path / "tracking" / "progress-tracker.json"
        if not feature_tracker.exists():
            errors.append("tracking/ exists but missing progress-tracker.json")
    
    # Check for child plans (shouldn't have any)
    child_plan_pattern = re.compile(r'^\d{2}[A-Z]?-')
    child_plan_folders = [
        d for d in plan_path.iterdir()
        if d.is_dir() and child_plan_pattern.match(d.name)
    ]
    
    if child_plan_folders:
        errors.append(
            f"Feature plan should not have child plans (found: {[d.name for d in child_plan_folders]})"
        )
    
    return len(errors) == 0, errors


# Export public API
__all__ = [
    "PlannerMode",
    "detect_planner_mode",
    "analyze_plan_structure",
    "validate_epic_structure",
    "validate_feature_structure"
]
