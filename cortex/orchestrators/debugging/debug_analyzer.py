"""
CORTEX Debug Analyzer
=====================

Intelligent analysis of captured debug logs to identify:
- Race conditions (out-of-order execution)
- Integration breakages (missing dependencies, DOM issues)
- Timing issues (async operations completing incorrectly)
- Error patterns and root causes

Author: CORTEX
Version: 1.0.0
Phase: Phase 21.5 - Universal Debugging
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import json
import logging
import re
from collections import defaultdict

logger = logging.getLogger(__name__)

CORTEX_DEBUG_MARKER = "CORTEX_DEBUG_"


class IssueSeverity(Enum):
    """Issue severity levels."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class IssueType(Enum):
    """Types of detected issues."""
    RACE_CONDITION = "race_condition"
    INTEGRATION_BREAK = "integration_break"
    TIMING_ISSUE = "timing_issue"
    MISSING_DEPENDENCY = "missing_dependency"
    DOM_ERROR = "dom_error"
    ASYNC_ERROR = "async_error"
    LOAD_ORDER = "load_order"
    DATA_FLOW = "data_flow"
    INITIALIZATION = "initialization"
    UNKNOWN = "unknown"


@dataclass
class DetectedIssue:
    """Represents a detected issue with full context."""
    
    issue_type: IssueType
    severity: IssueSeverity
    title: str
    description: str
    file: Optional[str] = None
    line: Optional[int] = None
    related_files: List[str] = field(default_factory=list)
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    fix: Optional[str] = None
    fix_code: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.issue_type.value,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "file": self.file,
            "line": self.line,
            "related_files": self.related_files,
            "evidence": self.evidence,
            "fix": self.fix,
            "fix_code": self.fix_code,
        }


@dataclass
class RaceCondition:
    """Represents a detected race condition."""
    
    description: str
    files: List[str]
    sequence: str
    expected_order: List[str]
    actual_order: List[str]
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    fix: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "files": self.files,
            "sequence": self.sequence,
            "expected_order": self.expected_order,
            "actual_order": self.actual_order,
            "evidence": self.evidence,
            "fix": self.fix,
        }


@dataclass
class IntegrationBreak:
    """Represents an integration breakage."""
    
    description: str
    component: str
    dependency: str
    error_message: Optional[str] = None
    fix: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "component": self.component,
            "dependency": self.dependency,
            "error_message": self.error_message,
            "fix": self.fix,
        }


class DebugAnalyzer:
    """
    Intelligent analyzer for captured debug logs.
    
    Detects:
    - Race conditions via execution order analysis
    - Integration breakages via error pattern matching
    - Timing issues via async operation tracking
    - Root causes via call chain analysis
    """
    
    # Known error patterns and their fixes
    ERROR_PATTERNS = {
        r"(\w+) is not defined": {
            "type": IssueType.MISSING_DEPENDENCY,
            "severity": IssueSeverity.CRITICAL,
            "fix_template": "Ensure {0} is loaded before this script. Check script loading order in HTML.",
        },
        r"Cannot read propert(?:y|ies)) ['\"](\w+)['\"] of (null|undefined)": {
            "type": IssueType.DOM_ERROR,
            "severity": IssueSeverity.HIGH,
            "fix_template": "Element is null/undefined when accessing '{0}'. Add null check or wait for DOM ready.",
        },
        r"(\w+) not loaded\. Include (\w+)\.js": {
            "type": IssueType.LOAD_ORDER,
            "severity": IssueSeverity.CRITICAL,
            "fix_template": "Add <script src=\"{1}.js\"></script> before scripts that depend on it.",
        },
        r"Failed to (load|fetch) resource.*404": {
            "type": IssueType.MISSING_DEPENDENCY,
            "severity": IssueSeverity.HIGH,
            "fix_template": "Resource not found. Check file path and ensure file exists.",
        },
        r"Container ['\"](\w+)['\"] not found": {
            "type": IssueType.DOM_ERROR,
            "severity": IssueSeverity.HIGH,
            "fix_template": "Add element with id=\"{0}\" to HTML, or wait for DOM to load.",
        },
        r"NetworkError|net::ERR_": {
            "type": IssueType.INTEGRATION_BREAK,
            "severity": IssueSeverity.HIGH,
            "fix_template": "Network request failed. Check CORS settings, server status, and URL.",
        },
        r"SyntaxError": {
            "type": IssueType.INTEGRATION_BREAK,
            "severity": IssueSeverity.CRITICAL,
            "fix_template": "JavaScript syntax error. Check for missing brackets, quotes, or semicolons.",
        },
        r"TypeError.*is not a function": {
            "type": IssueType.MISSING_DEPENDENCY,
            "severity": IssueSeverity.HIGH,
            "fix_template": "Function is undefined. Check import/export statements and load order.",
        },
    }
    
    # Expected initialization order for common patterns
    EXPECTED_ORDERS = {
        "data_loading": ["DataAdapter", "DataLoader", "DataBinder", "Render"],
        "dom_init": ["DOMContentLoaded", "QuerySelectors", "EventListeners", "Init"],
        "async_flow": ["Start", "Await", "Then", "Complete"],
    }
    
    def __init__(
        self,
        session_id: str,
        output_dir: Path,
    ):
        self.session_id = session_id
        self.output_dir = Path(output_dir)
        
        logger.info(f"DebugAnalyzer initialized for session {session_id}")
    
    def analyze(
        self,
        cortex_markers: List[Dict[str, Any]],
        errors: List[Dict[str, Any]],
        warnings: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Analyze captured logs to detect issues.
        
        Args:
            cortex_markers: CORTEX debug markers captured
            errors: Error logs captured
            warnings: Warning logs captured
        
        Returns:
            Analysis results with detected issues
        """
        logger.info(f"Analyzing {len(cortex_markers)} markers, {len(errors)} errors, {len(warnings)} warnings")
        
        issues: List[DetectedIssue] = []
        race_conditions: List[RaceCondition] = []
        integration_breaks: List[IntegrationBreak] = []
        
        # 1. Analyze error patterns
        for error in errors:
            issue = self._analyze_error(error)
            if issue:
                issues.append(issue)
        
        # 2. Analyze execution order (race conditions)
        race_issues = self._detect_race_conditions(cortex_markers)
        race_conditions.extend(race_issues)
        for race in race_issues:
            issues.append(DetectedIssue(
                issue_type=IssueType.RACE_CONDITION,
                severity=IssueSeverity.HIGH,
                title=f"Race condition: {race.description}",
                description=race.sequence,
                related_files=race.files,
                evidence=race.evidence,
                fix=race.fix,
            ))
        
        # 3. Detect integration breakages
        int_breaks = self._detect_integration_breaks(cortex_markers, errors)
        integration_breaks.extend(int_breaks)
        for brk in int_breaks:
            issues.append(DetectedIssue(
                issue_type=IssueType.INTEGRATION_BREAK,
                severity=IssueSeverity.HIGH,
                title=f"Integration break: {brk.component} → {brk.dependency}",
                description=brk.description,
                related_files=[brk.component, brk.dependency],
                fix=brk.fix,
            ))
        
        # 4. Analyze timing issues
        timing_issues = self._detect_timing_issues(cortex_markers)
        issues.extend(timing_issues)
        
        # 5. Analyze data flow issues
        data_issues = self._detect_data_flow_issues(cortex_markers)
        issues.extend(data_issues)
        
        # Sort by severity
        severity_order = {
            IssueSeverity.CRITICAL: 0,
            IssueSeverity.HIGH: 1,
            IssueSeverity.MEDIUM: 2,
            IssueSeverity.LOW: 3,
            IssueSeverity.INFO: 4,
        }
        issues.sort(key=lambda x: severity_order.get(x.severity, 5))
        
        result = {
            "session_id": self.session_id,
            "analysis_time": datetime.now().isoformat(),
            "issues": [i.to_dict() for i in issues],
            "race_conditions": [r.to_dict() for r in race_conditions],
            "integration_breaks": [b.to_dict() for b in integration_breaks],
            "summary": {
                "total_issues": len(issues),
                "critical": len([i for i in issues if i.severity == IssueSeverity.CRITICAL]),
                "high": len([i for i in issues if i.severity == IssueSeverity.HIGH]),
                "medium": len([i for i in issues if i.severity == IssueSeverity.MEDIUM]),
                "low": len([i for i in issues if i.severity == IssueSeverity.LOW]),
                "race_conditions": len(race_conditions),
                "integration_breaks": len(integration_breaks),
            }
        }
        
        # Save analysis
        self._save_analysis(result)
        
        return result
    
    def _analyze_error(self, error: Dict[str, Any]) -> Optional[DetectedIssue]:
        """Analyze a single error for known patterns."""
        message = error.get("message", "")
        
        for pattern, info in self.ERROR_PATTERNS.items():
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                fix = info["fix_template"].format(*match.groups()) if match.groups() else info["fix_template"]
                
                return DetectedIssue(
                    issue_type=info["type"],
                    severity=info["severity"],
                    title=f"Error: {message[:80]}...",
                    description=message,
                    evidence=[error],
                    fix=fix,
                )
        
        # Unknown error
        if "error" in message.lower() or "exception" in message.lower():
            return DetectedIssue(
                issue_type=IssueType.UNKNOWN,
                severity=IssueSeverity.MEDIUM,
                title=f"Error: {message[:80]}...",
                description=message,
                evidence=[error],
                fix="Review error message and stack trace for root cause.",
            )
        
        return None
    
    def _detect_race_conditions(self, markers: List[Dict[str, Any]]) -> List[RaceCondition]:
        """Detect race conditions from execution order."""
        race_conditions = []
        
        # Group markers by file
        by_file = defaultdict(list)
        for marker in markers:
            parsed = marker.get("parsed_marker", {})
            if parsed:
                by_file[parsed.get("file", "unknown")].append(parsed)
        
        # Check for common race condition patterns
        
        # Pattern 1: Data accessed before load complete
        for file, file_markers in by_file.items():
            phases = [m.get("phase", "") for m in file_markers]
            
            # Check if DOM accessed before data loaded
            dom_indices = [i for i, p in enumerate(phases) if p == "DOM"]
            data_indices = [i for i, p in enumerate(phases) if p in ("DATA", "ASYNC")]
            
            for dom_idx in dom_indices:
                for data_idx in data_indices:
                    if dom_idx < data_idx:
                        race_conditions.append(RaceCondition(
                            description="DOM accessed before data loaded",
                            files=[file],
                            sequence=f"DOM access at marker {dom_idx} before data load at marker {data_idx}",
                            expected_order=["DATA/ASYNC", "DOM"],
                            actual_order=["DOM", "DATA/ASYNC"],
                            evidence=[file_markers[dom_idx], file_markers[data_idx]] if dom_idx < len(file_markers) and data_idx < len(file_markers) else [],
                            fix="Wait for data to load before accessing DOM elements. Use async/await or Promise chains.",
                        ))
                        break
        
        # Pattern 2: Event handlers attached before elements exist
        for file, file_markers in by_file.items():
            phases = [m.get("phase", "") for m in file_markers]
            messages = [m.get("message", "") for m in file_markers]
            
            event_indices = [i for i, p in enumerate(phases) if p == "EVENT"]
            init_indices = [i for i, m in enumerate(messages) if "ENTER init" in m or "ENTER constructor" in m]
            
            for event_idx in event_indices:
                if init_indices and event_idx < min(init_indices):
                    race_conditions.append(RaceCondition(
                        description="Event listener added before initialization",
                        files=[file],
                        sequence=f"Event listener at marker {event_idx} before init",
                        expected_order=["init", "addEventListener"],
                        actual_order=["addEventListener", "init"],
                        evidence=[file_markers[event_idx]] if event_idx < len(file_markers) else [],
                        fix="Attach event listeners inside DOMContentLoaded or after init() completes.",
                    ))
        
        return race_conditions
    
    def _detect_integration_breaks(
        self,
        markers: List[Dict[str, Any]],
        errors: List[Dict[str, Any]],
    ) -> List[IntegrationBreak]:
        """Detect integration breakages between components."""
        breaks = []
        
        # Check for missing script errors
        for error in errors:
            message = error.get("message", "")
            
            # Pattern: "X not loaded"
            match = re.search(r"(\w+)\s+not\s+loaded", message, re.IGNORECASE)
            if match:
                component = match.group(1)
                breaks.append(IntegrationBreak(
                    description=f"Component {component} is required but not loaded",
                    component="unknown",
                    dependency=component,
                    error_message=message,
                    fix=f"Add <script src=\"js/{component}.js\"></script> before dependent scripts.",
                ))
            
            # Pattern: "X is not defined"
            match = re.search(r"(\w+)\s+is\s+not\s+defined", message, re.IGNORECASE)
            if match:
                var_name = match.group(1)
                breaks.append(IntegrationBreak(
                    description=f"Variable/class {var_name} is not defined",
                    component="unknown",
                    dependency=var_name,
                    error_message=message,
                    fix=f"Ensure {var_name} is defined or imported before use. Check script loading order.",
                ))
        
        return breaks
    
    def _detect_timing_issues(self, markers: List[Dict[str, Any]]) -> List[DetectedIssue]:
        """Detect timing issues in async operations."""
        issues = []
        
        # Group ASYNC markers
        async_markers = [m for m in markers if m.get("parsed_marker", {}).get("phase") == "ASYNC"]
        
        # Check for AWAIT without completion
        await_starts = [m for m in async_markers if "AWAIT" in m.get("parsed_marker", {}).get("message", "")]
        
        # If we have many awaits but errors, likely timing issue
        if len(await_starts) > 3:
            issues.append(DetectedIssue(
                issue_type=IssueType.TIMING_ISSUE,
                severity=IssueSeverity.MEDIUM,
                title="Multiple async operations detected",
                description=f"Found {len(await_starts)} async operations. Check for race conditions.",
                evidence=await_starts[:5],
                fix="Consider using Promise.all() for parallel operations or sequential await for dependencies.",
            ))
        
        return issues
    
    def _detect_data_flow_issues(self, markers: List[Dict[str, Any]]) -> List[DetectedIssue]:
        """Detect data flow issues."""
        issues = []
        
        # Check for data-related markers followed by errors
        data_markers = [m for m in markers if m.get("parsed_marker", {}).get("phase") in ("DATA", "ASYNC")]
        
        # Look for "No data found" or similar messages
        for marker in markers:
            message = marker.get("message", "") or marker.get("parsed_marker", {}).get("message", "")
            if "no data" in message.lower() or "empty" in message.lower():
                issues.append(DetectedIssue(
                    issue_type=IssueType.DATA_FLOW,
                    severity=IssueSeverity.HIGH,
                    title="Data flow issue: Empty or missing data",
                    description=message,
                    evidence=[marker],
                    fix="Check data source path, verify data file exists, and ensure correct format.",
                ))
        
        return issues
    
    def generate_fix_plan(
        self,
        issues: List[Dict[str, Any]],
        race_conditions: List[Dict[str, Any]],
        integration_breaks: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Generate a prioritized fix plan."""
        fix_plan = {
            "generated_at": datetime.now().isoformat(),
            "session_id": self.session_id,
            "priority_order": [],
            "by_priority": {
                "P0_critical": [],
                "P1_high": [],
                "P2_medium": [],
                "P3_low": [],
            },
            "estimated_time": "unknown",
        }
        
        # Organize by priority
        for issue in issues:
            severity = issue.get("severity", "MEDIUM")
            fix_item = {
                "title": issue.get("title", "Unknown issue"),
                "file": issue.get("file"),
                "fix": issue.get("fix", "Review and fix manually"),
                "type": issue.get("type"),
            }
            
            if severity == "CRITICAL":
                fix_plan["by_priority"]["P0_critical"].append(fix_item)
                fix_plan["priority_order"].append(("P0", fix_item["title"]))
            elif severity == "HIGH":
                fix_plan["by_priority"]["P1_high"].append(fix_item)
                fix_plan["priority_order"].append(("P1", fix_item["title"]))
            elif severity == "MEDIUM":
                fix_plan["by_priority"]["P2_medium"].append(fix_item)
                fix_plan["priority_order"].append(("P2", fix_item["title"]))
            else:
                fix_plan["by_priority"]["P3_low"].append(fix_item)
                fix_plan["priority_order"].append(("P3", fix_item["title"]))
        
        # Add race condition fixes
        for race in race_conditions:
            fix_plan["by_priority"]["P1_high"].append({
                "title": f"Race condition: {race.get('description', 'Unknown')}",
                "files": race.get("files", []),
                "fix": race.get("fix", "Fix execution order"),
                "type": "race_condition",
            })
        
        # Add integration break fixes
        for brk in integration_breaks:
            fix_plan["by_priority"]["P0_critical"].append({
                "title": f"Integration: {brk.get('description', 'Unknown')}",
                "component": brk.get("component"),
                "dependency": brk.get("dependency"),
                "fix": brk.get("fix", "Fix integration"),
                "type": "integration_break",
            })
        
        # Estimate time
        p0_count = len(fix_plan["by_priority"]["P0_critical"])
        p1_count = len(fix_plan["by_priority"]["P1_high"])
        total_minutes = (p0_count * 30) + (p1_count * 15)
        fix_plan["estimated_time"] = f"{total_minutes} minutes"
        
        return fix_plan
    
    def _save_analysis(self, result: Dict[str, Any]):
        """Save analysis result to disk."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        analysis_path = self.output_dir / "analysis-report.json"
        with open(analysis_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        logger.info(f"Analysis saved to {analysis_path}")
