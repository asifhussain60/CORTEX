"""
RCA (Root Cause Analysis) Utility

Fast, lightweight root cause analysis management.
Replaces heavy orchestrator (1,174 lines) with focused utility (~650 lines).

Core Operations:
- Create RCA analysis
- Load existing RCA
- Update RCA fields
- Add Why question/answer (5 Whys methodology)
- Generate report
- List RCAs by status

Version: 3.0.0 (Utility Migration)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import yaml
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
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
    CORTEX_ROOT = Path(__file__).resolve().parents[4]


# ===== ENUMS & DATACLASSES =====

class RCAStatus(Enum):
    """RCA analysis status states."""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    APPROVED = "approved"


class WhyDepth(Enum):
    """Depth levels for 5 Whys analysis."""
    WHY_1 = 1
    WHY_2 = 2
    WHY_3 = 3
    WHY_4 = 4
    WHY_5 = 5


@dataclass
class IncidentDetails:
    """Structured incident information."""
    incident_id: str
    title: str
    description: str
    occurred_at: str
    detected_at: str
    severity: str = "medium"  # low, medium, high, critical
    impact: str = ""
    affected_systems: List[str] = field(default_factory=list)
    resolved_at: Optional[str] = None


@dataclass
class WhyQuestion:
    """A single Why question in the 5 Whys chain."""
    depth: int  # 1-5
    question: str
    answer: str = ""
    confidence: float = 0.0
    evidence: List[str] = field(default_factory=list)


@dataclass
class RootCause:
    """Identified root cause with supporting evidence."""
    description: str
    confidence: float
    evidence: List[str]
    category: str = "technical"  # technical, process, human
    why_chain: List[WhyQuestion] = field(default_factory=list)


@dataclass
class CorrectiveAction:
    """Action to address the root cause."""
    action_id: str
    description: str
    action_type: str  # immediate, short_term, long_term
    owner: str = ""
    status: str = "pending"
    priority: str = "medium"  # low, medium, high, critical


@dataclass
class RCAAnalysis:
    """Complete RCA analysis structure."""
    analysis_id: str
    incident: IncidentDetails
    status: RCAStatus
    
    # 5 Whys
    why_questions: List[WhyQuestion] = field(default_factory=list)
    current_depth: int = 0
    
    # Root Cause
    root_causes: List[RootCause] = field(default_factory=list)
    
    # Actions
    corrective_actions: List[CorrectiveAction] = field(default_factory=list)
    
    # Metadata
    analyst: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None


@dataclass
class RCAResult:
    """Result of RCA operation."""
    success: bool
    message: str
    analysis_id: Optional[str] = None
    analysis: Optional[RCAAnalysis] = None
    report_path: Optional[Path] = None
    errors: List[str] = field(default_factory=list)


# ===== DIRECTORY MANAGEMENT =====

def _get_rca_dirs() -> Dict[str, Path]:
    """Get RCA directory paths."""
    base_dir = CORTEX_ROOT / "cortex-brain" / "documents" / "investigations" / "rca"
    
    dirs = {
        "base": base_dir,
        "draft": base_dir / "draft",
        "in_progress": base_dir / "in_progress",
        "completed": base_dir / "completed",
        "approved": base_dir / "approved",
        "reports": CORTEX_ROOT / "cortex-brain" / "documents" / "reports" / "rca"
    }
    
    for dir_path in dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)
    
    return dirs


def _get_status_dir(status: RCAStatus) -> Path:
    """Get directory for RCA status."""
    dirs = _get_rca_dirs()
    return dirs[status.value.replace("_", "_")]


def _slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    import re
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


# ===== CORE OPERATION 1: CREATE RCA =====

def create_rca(
    incident_id: str,
    title: str,
    description: str,
    occurred_at: str,
    detected_at: str,
    **kwargs
) -> RCAResult:
    """
    Create new RCA analysis.
    
    Args:
        incident_id: Unique incident identifier
        title: Incident title
        description: Incident description
        occurred_at: When incident occurred (ISO format)
        detected_at: When incident was detected (ISO format)
        **kwargs: Additional incident fields
        
    Returns:
        RCAResult with creation outcome
    """
    logger.info(f"🔍 Creating RCA: {title}")
    
    try:
        # Create incident details
        incident = IncidentDetails(
            incident_id=incident_id,
            title=title,
            description=description,
            occurred_at=occurred_at,
            detected_at=detected_at,
            **{k: v for k, v in kwargs.items() if k in ['severity', 'impact', 'affected_systems', 'resolved_at']}
        )
        
        # Generate analysis ID
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        slug = _slugify(title)[:30]
        analysis_id = f"rca-{timestamp}-{slug}"
        
        # Create analysis
        analysis = RCAAnalysis(
            analysis_id=analysis_id,
            incident=incident,
            status=RCAStatus.DRAFT,
            analyst=kwargs.get('analyst', 'CORTEX')
        )
        
        # Save to file
        file_path = _get_status_dir(RCAStatus.DRAFT) / f"{analysis_id}.yaml"
        _save_analysis(analysis, file_path)
        
        return RCAResult(
            success=True,
            message=f"RCA created: {analysis_id}",
            analysis_id=analysis_id,
            analysis=analysis
        )
        
    except Exception as e:
        return RCAResult(
            success=False,
            message=f"Failed to create RCA: {str(e)}",
            errors=[str(e)]
        )


def _save_analysis(analysis: RCAAnalysis, file_path: Path):
    """Save analysis to YAML file."""
    data = {
        "analysis_id": analysis.analysis_id,
        "status": analysis.status.value,
        "incident": {
            "incident_id": analysis.incident.incident_id,
            "title": analysis.incident.title,
            "description": analysis.incident.description,
            "occurred_at": analysis.incident.occurred_at,
            "detected_at": analysis.incident.detected_at,
            "severity": analysis.incident.severity,
            "impact": analysis.incident.impact,
            "affected_systems": analysis.incident.affected_systems,
            "resolved_at": analysis.incident.resolved_at
        },
        "why_questions": [
            {
                "depth": wq.depth,
                "question": wq.question,
                "answer": wq.answer,
                "confidence": wq.confidence,
                "evidence": wq.evidence
            }
            for wq in analysis.why_questions
        ],
        "current_depth": analysis.current_depth,
        "root_causes": [
            {
                "description": rc.description,
                "confidence": rc.confidence,
                "evidence": rc.evidence,
                "category": rc.category
            }
            for rc in analysis.root_causes
        ],
        "corrective_actions": [
            {
                "action_id": ca.action_id,
                "description": ca.description,
                "action_type": ca.action_type,
                "owner": ca.owner,
                "status": ca.status,
                "priority": ca.priority
            }
            for ca in analysis.corrective_actions
        ],
        "analyst": analysis.analyst,
        "created_at": analysis.created_at,
        "updated_at": analysis.updated_at,
        "completed_at": analysis.completed_at
    }
    
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)


# ===== CORE OPERATION 2: LOAD RCA =====

def load_rca(analysis_id: str) -> RCAResult:
    """
    Load existing RCA analysis.
    
    Args:
        analysis_id: Analysis identifier
        
    Returns:
        RCAResult with loaded analysis
    """
    logger.info(f"📂 Loading RCA: {analysis_id}")
    
    try:
        # Search for analysis across all status directories
        dirs = _get_rca_dirs()
        yaml_path = None
        
        for status_name in ["draft", "in_progress", "completed", "approved"]:
            potential_path = dirs[status_name] / f"{analysis_id}.yaml"
            if potential_path.exists():
                yaml_path = potential_path
                break
        
        if not yaml_path:
            return RCAResult(
                success=False,
                message=f"RCA not found: {analysis_id}",
                errors=[f"No file found for {analysis_id}"]
            )
        
        # Load YAML
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Reconstruct analysis
        incident = IncidentDetails(**data["incident"])
        
        why_questions = [
            WhyQuestion(**wq)
            for wq in data.get("why_questions", [])
        ]
        
        root_causes = [
            RootCause(**rc)
            for rc in data.get("root_causes", [])
        ]
        
        corrective_actions = [
            CorrectiveAction(**ca)
            for ca in data.get("corrective_actions", [])
        ]
        
        analysis = RCAAnalysis(
            analysis_id=data["analysis_id"],
            incident=incident,
            status=RCAStatus(data["status"]),
            why_questions=why_questions,
            current_depth=data.get("current_depth", 0),
            root_causes=root_causes,
            corrective_actions=corrective_actions,
            analyst=data.get("analyst", ""),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            completed_at=data.get("completed_at")
        )
        
        return RCAResult(
            success=True,
            message=f"RCA loaded: {analysis_id}",
            analysis_id=analysis_id,
            analysis=analysis
        )
        
    except Exception as e:
        return RCAResult(
            success=False,
            message=f"Failed to load RCA: {str(e)}",
            errors=[str(e)]
        )


# ===== CORE OPERATION 3: UPDATE RCA =====

def update_rca(
    analysis_id: str,
    **updates
) -> RCAResult:
    """
    Update RCA analysis fields.
    
    Args:
        analysis_id: Analysis identifier
        **updates: Fields to update
        
    Returns:
        RCAResult with update outcome
    """
    logger.info(f"✏️ Updating RCA: {analysis_id}")
    
    try:
        # Load existing analysis
        load_result = load_rca(analysis_id)
        if not load_result.success:
            return load_result
        
        analysis = load_result.analysis
        old_status = analysis.status
        
        # Apply updates
        for key, value in updates.items():
            if key == "status" and isinstance(value, str):
                analysis.status = RCAStatus(value)
            elif hasattr(analysis, key):
                setattr(analysis, key, value)
        
        # Update timestamp
        analysis.updated_at = datetime.now().isoformat()
        
        # Handle status change (move file)
        old_path = _get_status_dir(old_status) / f"{analysis_id}.yaml"
        new_path = _get_status_dir(analysis.status) / f"{analysis_id}.yaml"
        
        if old_status != analysis.status:
            _save_analysis(analysis, new_path)
            if old_path.exists():
                old_path.unlink()
        else:
            _save_analysis(analysis, old_path)
        
        return RCAResult(
            success=True,
            message=f"RCA updated: {analysis_id}",
            analysis_id=analysis_id,
            analysis=analysis
        )
        
    except Exception as e:
        return RCAResult(
            success=False,
            message=f"Failed to update RCA: {str(e)}",
            errors=[str(e)]
        )


# ===== CORE OPERATION 4: ADD WHY QUESTION =====

def add_why_question(
    analysis_id: str,
    question: str,
    answer: Optional[str] = None,
    evidence: Optional[List[str]] = None
) -> RCAResult:
    """
    Add Why question to 5 Whys chain.
    
    Args:
        analysis_id: Analysis identifier
        question: Why question
        answer: Answer (optional)
        evidence: Supporting evidence (optional)
        
    Returns:
        RCAResult with update outcome
    """
    logger.info(f"❓ Adding Why question to RCA: {analysis_id}")
    
    try:
        # Load analysis
        load_result = load_rca(analysis_id)
        if not load_result.success:
            return load_result
        
        analysis = load_result.analysis
        
        # Determine depth
        next_depth = len(analysis.why_questions) + 1
        if next_depth > 5:
            return RCAResult(
                success=False,
                message="Maximum 5 Why questions reached",
                errors=["5 Whys methodology limits depth to 5"]
            )
        
        # Create Why question
        why_q = WhyQuestion(
            depth=next_depth,
            question=question,
            answer=answer or "",
            evidence=evidence or []
        )
        
        analysis.why_questions.append(why_q)
        analysis.current_depth = next_depth
        analysis.updated_at = datetime.now().isoformat()
        
        # Save
        file_path = _get_status_dir(analysis.status) / f"{analysis_id}.yaml"
        _save_analysis(analysis, file_path)
        
        return RCAResult(
            success=True,
            message=f"Why question {next_depth} added",
            analysis_id=analysis_id,
            analysis=analysis
        )
        
    except Exception as e:
        return RCAResult(
            success=False,
            message=f"Failed to add Why question: {str(e)}",
            errors=[str(e)]
        )


# ===== CORE OPERATION 5: GENERATE REPORT =====

def generate_report(analysis_id: str) -> RCAResult:
    """
    Generate RCA report.
    
    Args:
        analysis_id: Analysis identifier
        
    Returns:
        RCAResult with report path
    """
    logger.info(f"📄 Generating RCA report: {analysis_id}")
    
    try:
        # Load analysis
        load_result = load_rca(analysis_id)
        if not load_result.success:
            return load_result
        
        analysis = load_result.analysis
        
        # Generate report markdown
        report_content = _generate_report_markdown(analysis)
        
        # Save report
        dirs = _get_rca_dirs()
        report_path = dirs["reports"] / f"{analysis_id}-report.md"
        report_path.write_text(report_content, encoding='utf-8')
        
        return RCAResult(
            success=True,
            message=f"Report generated: {analysis_id}",
            analysis_id=analysis_id,
            analysis=analysis,
            report_path=report_path
        )
        
    except Exception as e:
        return RCAResult(
            success=False,
            message=f"Failed to generate report: {str(e)}",
            errors=[str(e)]
        )


def _generate_report_markdown(analysis: RCAAnalysis) -> str:
    """Generate markdown report for RCA."""
    severity_icons = {"low": "🟢", "medium": "🟡", "high": "🔴", "critical": "🔴⚠️"}
    severity_icon = severity_icons.get(analysis.incident.severity, "⚪")
    
    content = f"""# Root Cause Analysis Report

**Analysis ID:** {analysis.analysis_id}  
**Date:** {analysis.created_at}  
**Analyst:** {analysis.analyst}  
**Status:** {analysis.status.value.upper()}

---

## Executive Summary

{severity_icon} **Severity:** {analysis.incident.severity.upper()}

**Incident:** {analysis.incident.title}

**Root Cause Summary:**
{analysis.root_causes[0].description if analysis.root_causes else "(Analysis in progress)"}

---

## Incident Details

**Incident ID:** {analysis.incident.incident_id}  
**Occurred:** {analysis.incident.occurred_at}  
**Detected:** {analysis.incident.detected_at}  
**Resolved:** {analysis.incident.resolved_at or "(Not yet resolved)"}

**Description:**
{analysis.incident.description}

**Impact:**
{analysis.incident.impact if analysis.incident.impact else "(Not specified)"}

**Affected Systems:**
"""
    
    if analysis.incident.affected_systems:
        for system in analysis.incident.affected_systems:
            content += f"- {system}\n"
    else:
        content += "- (None specified)\n"
    
    content += "\n---\n\n## 5 Whys Analysis\n\n"
    
    if analysis.why_questions:
        for wq in analysis.why_questions:
            content += f"### Why {wq.depth}: {wq.question}\n\n"
            content += f"**Answer:** {wq.answer if wq.answer else '(Not answered)'}\n\n"
            if wq.evidence:
                content += "**Evidence:**\n"
                for evidence in wq.evidence:
                    content += f"- {evidence}\n"
                content += "\n"
            if wq.confidence > 0:
                conf_bar = "█" * int(wq.confidence / 10) + "░" * (10 - int(wq.confidence / 10))
                content += f"**Confidence:** {wq.confidence:.1f}% [{conf_bar}]\n\n"
    else:
        content += "(No Why questions added yet)\n\n"
    
    content += "---\n\n## Root Causes\n\n"
    
    if analysis.root_causes:
        for i, rc in enumerate(analysis.root_causes, 1):
            content += f"### Root Cause {i}: {rc.description}\n\n"
            content += f"**Category:** {rc.category.upper()}\n"
            content += f"**Confidence:** {rc.confidence:.1f}%\n\n"
            if rc.evidence:
                content += "**Evidence:**\n"
                for evidence in rc.evidence:
                    content += f"- {evidence}\n"
                content += "\n"
    else:
        content += "(Root causes not yet identified)\n\n"
    
    content += "---\n\n## Corrective Actions\n\n"
    
    if analysis.corrective_actions:
        for ca in analysis.corrective_actions:
            priority_icon = {"low": "🟢", "medium": "🟡", "high": "🔴", "critical": "🔴⚠️"}.get(ca.priority, "⚪")
            content += f"### {priority_icon} {ca.description}\n\n"
            content += f"**Type:** {ca.action_type}\n"
            content += f"**Owner:** {ca.owner or '(Not assigned)'}\n"
            content += f"**Status:** {ca.status.upper()}\n"
            content += f"**Priority:** {ca.priority.upper()}\n\n"
    else:
        content += "(No corrective actions defined yet)\n\n"
    
    content += f"---\n\n**Report Generated:** {datetime.now().isoformat()}\n"
    
    return content


# ===== CORE OPERATION 6: LIST RCAs =====

def list_rcas(status: Optional[RCAStatus] = None) -> RCAResult:
    """
    List RCA analyses by status.
    
    Args:
        status: Filter by status (None = all)
        
    Returns:
        RCAResult with list of analyses
    """
    logger.info(f"📋 Listing RCAs (status: {status.value if status else 'all'})")
    
    try:
        analyses = []
        dirs = _get_rca_dirs()
        
        # Determine which directories to search
        if status:
            search_dirs = {status.value: _get_status_dir(status)}
        else:
            search_dirs = {
                "draft": dirs["draft"],
                "in_progress": dirs["in_progress"],
                "completed": dirs["completed"],
                "approved": dirs["approved"]
            }
        
        # Scan directories
        for status_name, dir_path in search_dirs.items():
            for yaml_path in dir_path.glob("*.yaml"):
                try:
                    with open(yaml_path, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                    
                    incident = IncidentDetails(**data["incident"])
                    
                    analysis = RCAAnalysis(
                        analysis_id=data["analysis_id"],
                        incident=incident,
                        status=RCAStatus(data["status"]),
                        current_depth=data.get("current_depth", 0),
                        analyst=data.get("analyst", ""),
                        created_at=data["created_at"],
                        updated_at=data["updated_at"]
                    )
                    analyses.append(analysis)
                except Exception as e:
                    logger.warning(f"Failed to load {yaml_path.name}: {e}")
        
        # Sort by updated date
        analyses.sort(key=lambda x: x.updated_at, reverse=True)
        
        message = f"Found {len(analyses)} RCA(s)"
        if status:
            message += f" with status '{status.value}'"
        
        return RCAResult(
            success=True,
            message=message,
            analysis=analyses[0] if analyses else None
        )
        
    except Exception as e:
        return RCAResult(
            success=False,
            message=f"Failed to list RCAs: {str(e)}",
            errors=[str(e)]
        )


# ===== CLI TEST EXECUTION =====

if __name__ == "__main__":
    print("=" * 60)
    print("RCA Utility - Direct Test")
    print("=" * 60)
    
    # Test 1: Create RCA
    print("\n[Test 1] Create RCA...")
    result = create_rca(
        incident_id="INC-12345",
        title="Database Connection Timeout",
        description="Production database experienced connection timeouts causing service disruption.",
        occurred_at="2024-12-02T14:30:00",
        detected_at="2024-12-02T14:35:00",
        severity="high",
        impact="20% of API requests failed",
        affected_systems=["database", "api-gateway"]
    )
    
    print(f"Success: {result.success}")
    print(f"Message: {result.message}")
    print(f"Analysis ID: {result.analysis_id}")
    
    if not result.success:
        print("❌ Creation failed")
        exit(1)
    
    analysis_id = result.analysis_id
    
    # Test 2: Add Why question
    print("\n" + "=" * 60)
    print("[Test 2] Add Why question...")
    why_result = add_why_question(
        analysis_id,
        question="Why did the database connections timeout?",
        answer="Connection pool was exhausted",
        evidence=["Connection pool metrics showing 100% utilization"]
    )
    
    print(f"Success: {why_result.success}")
    print(f"Message: {why_result.message}")
    
    # Test 3: Generate report
    print("\n" + "=" * 60)
    print("[Test 3] Generate report...")
    report_result = generate_report(analysis_id)
    
    print(f"Success: {report_result.success}")
    print(f"Message: {report_result.message}")
    if report_result.report_path:
        print(f"Report: {report_result.report_path}")
    
    # Test 4: List RCAs
    print("\n" + "=" * 60)
    print("[Test 4] List RCAs...")
    list_result = list_rcas(status=RCAStatus.DRAFT)
    
    print(f"Success: {list_result.success}")
    print(f"Message: {list_result.message}")
    
    # Cleanup
    print("\n" + "=" * 60)
    print("[Cleanup] Removing test RCA...")
    yaml_path = _get_status_dir(RCAStatus.DRAFT) / f"{analysis_id}.yaml"
    report_path = _get_rca_dirs()["reports"] / f"{analysis_id}-report.md"
    
    if yaml_path.exists():
        yaml_path.unlink()
    if report_path.exists():
        report_path.unlink()
    print("✅ Test RCA removed")
    
    print("\n" + "=" * 60)
    print("✅ Utility tests complete")
    print("=" * 60)
