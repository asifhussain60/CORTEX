"""
CORTEX Brain Integrity Checker

Detects and repairs corruption in brain data structures:
- Conversation history corruption
- Knowledge graph inconsistencies
- Development context staleness
- Cross-tier data leakage

Part of Brain Protection Layer
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Created: 2025-11-11
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import json
import yaml
import sqlite3
import hashlib
from datetime import datetime, timedelta


class IntegrityStatus(Enum):
    """Integrity check status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CORRUPTED = "corrupted"
    MISSING = "missing"


@dataclass
class IntegrityIssue:
    """An integrity issue discovered."""
    component: str  # "tier1", "tier2", "tier3", "cross_tier"
    issue_type: str
    severity: str  # "info", "warning", "error", "critical"
    message: str
    affected_data: Optional[str] = None
    auto_repairable: bool = False
    repair_action: Optional[str] = None


@dataclass
class IntegrityReport:
    """Integrity check report."""
    status: IntegrityStatus
    timestamp: str
    issues: List[IntegrityIssue]
    metadata: Dict[str, Any]
    auto_repairs_applied: int = 0


class IntegrityChecker:
    """
    Checks and repairs brain data integrity.
    
    Checks:
    1. Data corruption (malformed JSON/YAML)
    2. Schema violations (missing required fields)
    3. Stale data (outdated timestamps)
    4. Cross-tier leakage (data in wrong tier)
    5. Orphaned references (broken links)
    """
    
    def __init__(self, brain_root: Optional[Path] = None, auto_repair: bool = False):
        """
        Initialize Integrity Checker.
        
        Args:
            brain_root: Path to cortex-brain directory
            auto_repair: Whether to automatically repair issues
        """
        if brain_root is None:
            project_root = Path(__file__).parent.parent.parent
            brain_root = project_root / "cortex-brain"
        
        self.brain_root = Path(brain_root)
        self.auto_repair = auto_repair
        
        # Define data structure paths
        self.data_paths = {
            "tier1_history": self.brain_root / "conversation-history.jsonl",
            "tier1_context": self.brain_root / "conversation-context.jsonl",
            "tier2_knowledge": self.brain_root / "knowledge-graph.yaml",
            "tier3_dev_context": self.brain_root / "development-context.yaml"
        }
    
    def check_all(self) -> IntegrityReport:
        """
        Run all integrity checks.
        
        Returns:
            IntegrityReport with findings
        """
        issues = []
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "auto_repair_enabled": self.auto_repair,
            "checks_run": []
        }
        
        # Check Tier 1: Conversation History
        issues.extend(self._check_tier1_history())
        metadata["checks_run"].append("tier1_history")
        
        # Check Tier 1: Conversation Context
        issues.extend(self._check_tier1_context())
        metadata["checks_run"].append("tier1_context")
        
        # Check Tier 2: Knowledge Graph
        issues.extend(self._check_tier2_knowledge())
        metadata["checks_run"].append("tier2_knowledge")
        
        # Check Tier 3: Development Context
        issues.extend(self._check_tier3_context())
        metadata["checks_run"].append("tier3_context")
        
        # Check cross-tier consistency
        issues.extend(self._check_cross_tier_consistency())
        metadata["checks_run"].append("cross_tier_consistency")
        
        # Determine overall status
        if not issues:
            status = IntegrityStatus.HEALTHY
        elif any(i.severity == "critical" for i in issues):
            status = IntegrityStatus.CORRUPTED
        elif any(i.severity == "error" for i in issues):
            status = IntegrityStatus.DEGRADED
        else:
            status = IntegrityStatus.HEALTHY
        
        metadata["total_issues"] = len(issues)
        metadata["critical_count"] = sum(1 for i in issues if i.severity == "critical")
        metadata["error_count"] = sum(1 for i in issues if i.severity == "error")
        metadata["warning_count"] = sum(1 for i in issues if i.severity == "warning")
        
        return IntegrityReport(
            status=status,
            timestamp=metadata["timestamp"],
            issues=issues,
            metadata=metadata,
            auto_repairs_applied=0
        )
    
    def _check_tier1_history(self) -> List[IntegrityIssue]:
        """Check Tier 1 conversation history integrity."""
        issues = []
        history_path = self.data_paths["tier1_history"]
        
        # Check if file exists
        if not history_path.exists():
            issues.append(IntegrityIssue(
                component="tier1_history",
                issue_type="missing_file",
                severity="warning",
                message="Conversation history file not found",
                affected_data=str(history_path),
                auto_repairable=True,
                repair_action="Initialize empty conversation history"
            ))
            
            if self.auto_repair:
                self._repair_missing_history(history_path)
            
            return issues
        
        # Check file corruption
        try:
            with open(history_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Validate JSON Lines format
            for i, line in enumerate(lines, 1):
                if not line.strip():
                    continue
                
                try:
                    entry = json.loads(line)
                    
                    # Check required fields
                    required_fields = ["timestamp", "conversation_id", "role", "content"]
                    missing_fields = [f for f in required_fields if f not in entry]
                    
                    if missing_fields:
                        issues.append(IntegrityIssue(
                            component="tier1_history",
                            issue_type="missing_required_fields",
                            severity="error",
                            message=f"Line {i} missing fields: {', '.join(missing_fields)}",
                            affected_data=f"Line {i}",
                            auto_repairable=False
                        ))
                    
                    # Check timestamp validity
                    if "timestamp" in entry:
                        try:
                            datetime.fromisoformat(entry["timestamp"])
                        except ValueError:
                            issues.append(IntegrityIssue(
                                component="tier1_history",
                                issue_type="invalid_timestamp",
                                severity="warning",
                                message=f"Line {i} has invalid timestamp format",
                                affected_data=f"Line {i}: {entry.get('timestamp')}"
                            ))
                
                except json.JSONDecodeError as e:
                    issues.append(IntegrityIssue(
                        component="tier1_history",
                        issue_type="json_corruption",
                        severity="critical",
                        message=f"Line {i} is not valid JSON: {e}",
                        affected_data=f"Line {i}",
                        auto_repairable=False
                    ))
        
        except Exception as e:
            issues.append(IntegrityIssue(
                component="tier1_history",
                issue_type="read_error",
                severity="critical",
                message=f"Failed to read conversation history: {e}",
                affected_data=str(history_path)
            ))
        
        return issues
    
    def _check_tier1_context(self) -> List[IntegrityIssue]:
        """Check Tier 1 conversation context integrity."""
        issues = []
        context_path = self.data_paths["tier1_context"]
        
        if not context_path.exists():
            issues.append(IntegrityIssue(
                component="tier1_context",
                issue_type="missing_file",
                severity="info",
                message="Conversation context file not found (optional)",
                affected_data=str(context_path),
                auto_repairable=True,
                repair_action="Initialize empty context"
            ))
            return issues
        
        # Similar checks as history
        try:
            with open(context_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                if not line.strip():
                    continue
                
                try:
                    json.loads(line)
                except json.JSONDecodeError as e:
                    issues.append(IntegrityIssue(
                        component="tier1_context",
                        issue_type="json_corruption",
                        severity="error",
                        message=f"Line {i} is not valid JSON: {e}",
                        affected_data=f"Line {i}"
                    ))
        
        except Exception as e:
            issues.append(IntegrityIssue(
                component="tier1_context",
                issue_type="read_error",
                severity="error",
                message=f"Failed to read conversation context: {e}",
                affected_data=str(context_path)
            ))
        
        return issues
    
    def _check_tier2_knowledge(self) -> List[IntegrityIssue]:
        """Check Tier 2 knowledge graph integrity."""
        issues = []
        knowledge_path = self.data_paths["tier2_knowledge"]
        
        if not knowledge_path.exists():
            issues.append(IntegrityIssue(
                component="tier2_knowledge",
                issue_type="missing_file",
                severity="warning",
                message="Knowledge graph file not found",
                affected_data=str(knowledge_path),
                auto_repairable=True,
                repair_action="Initialize empty knowledge graph"
            ))
            
            if self.auto_repair:
                self._repair_missing_knowledge_graph(knowledge_path)
            
            return issues
        
        # Check YAML corruption
        try:
            with open(knowledge_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Validate structure
            if data is None:
                issues.append(IntegrityIssue(
                    component="tier2_knowledge",
                    issue_type="empty_file",
                    severity="warning",
                    message="Knowledge graph is empty",
                    affected_data=str(knowledge_path),
                    auto_repairable=True,
                    repair_action="Initialize with default structure"
                ))
            elif not isinstance(data, dict):
                issues.append(IntegrityIssue(
                    component="tier2_knowledge",
                    issue_type="invalid_structure",
                    severity="error",
                    message="Knowledge graph must be a dictionary at root",
                    affected_data=str(knowledge_path)
                ))
            else:
                # Check for patterns section
                if "patterns" not in data:
                    issues.append(IntegrityIssue(
                        component="tier2_knowledge",
                        issue_type="missing_section",
                        severity="info",
                        message="Knowledge graph missing 'patterns' section",
                        affected_data=str(knowledge_path),
                        auto_repairable=True,
                        repair_action="Add 'patterns' section"
                    ))
                
                # Check confidence values
                patterns = data.get("patterns", {})
                for pattern_id, pattern_data in patterns.items():
                    if isinstance(pattern_data, dict):
                        confidence = pattern_data.get("confidence", 0)
                        if not (0 <= confidence <= 1):
                            issues.append(IntegrityIssue(
                                component="tier2_knowledge",
                                issue_type="invalid_confidence",
                                severity="warning",
                                message=f"Pattern '{pattern_id}' has invalid confidence: {confidence}",
                                affected_data=pattern_id,
                                auto_repairable=True,
                                repair_action="Clamp confidence to [0, 1] range"
                            ))
        
        except yaml.YAMLError as e:
            issues.append(IntegrityIssue(
                component="tier2_knowledge",
                issue_type="yaml_corruption",
                severity="critical",
                message=f"Failed to parse knowledge graph YAML: {e}",
                affected_data=str(knowledge_path)
            ))
        except Exception as e:
            issues.append(IntegrityIssue(
                component="tier2_knowledge",
                issue_type="read_error",
                severity="error",
                message=f"Failed to read knowledge graph: {e}",
                affected_data=str(knowledge_path)
            ))
        
        return issues
    
    def _check_tier3_context(self) -> List[IntegrityIssue]:
        """Check Tier 3 development context integrity."""
        issues = []
        context_path = self.data_paths["tier3_dev_context"]
        
        if not context_path.exists():
            issues.append(IntegrityIssue(
                component="tier3_context",
                issue_type="missing_file",
                severity="warning",
                message="Development context file not found",
                affected_data=str(context_path),
                auto_repairable=True,
                repair_action="Initialize empty development context"
            ))
            
            if self.auto_repair:
                self._repair_missing_dev_context(context_path)
            
            return issues
        
        # Check YAML corruption and staleness
        try:
            with open(context_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if data is None:
                issues.append(IntegrityIssue(
                    component="tier3_context",
                    issue_type="empty_file",
                    severity="info",
                    message="Development context is empty",
                    affected_data=str(context_path)
                ))
            elif isinstance(data, dict):
                # Check for last_updated timestamp
                if "last_updated" in data:
                    try:
                        last_updated = datetime.fromisoformat(data["last_updated"])
                        age_hours = (datetime.now() - last_updated).total_seconds() / 3600
                        
                        if age_hours > 24:
                            issues.append(IntegrityIssue(
                                component="tier3_context",
                                issue_type="stale_data",
                                severity="warning",
                                message=f"Development context is {age_hours:.1f} hours old",
                                affected_data=str(context_path),
                                auto_repairable=True,
                                repair_action="Refresh development context"
                            ))
                    except ValueError:
                        issues.append(IntegrityIssue(
                            component="tier3_context",
                            issue_type="invalid_timestamp",
                            severity="warning",
                            message="Development context has invalid last_updated timestamp",
                            affected_data=data.get("last_updated")
                        ))
        
        except yaml.YAMLError as e:
            issues.append(IntegrityIssue(
                component="tier3_context",
                issue_type="yaml_corruption",
                severity="critical",
                message=f"Failed to parse development context YAML: {e}",
                affected_data=str(context_path)
            ))
        except Exception as e:
            issues.append(IntegrityIssue(
                component="tier3_context",
                issue_type="read_error",
                severity="error",
                message=f"Failed to read development context: {e}",
                affected_data=str(context_path)
            ))
        
        return issues
    
    def _check_cross_tier_consistency(self) -> List[IntegrityIssue]:
        """Check consistency across tiers."""
        issues = []
        
        # Check for conversation IDs in Tier 1 that have patterns in Tier 2
        try:
            # Load Tier 1 conversation IDs
            history_path = self.data_paths["tier1_history"]
            conversation_ids = set()
            
            if history_path.exists():
                with open(history_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            try:
                                entry = json.loads(line)
                                if "conversation_id" in entry:
                                    conversation_ids.add(entry["conversation_id"])
                            except json.JSONDecodeError:
                                pass
            
            # Check Tier 2 for raw conversation data
            knowledge_path = self.data_paths["tier2_knowledge"]
            if knowledge_path.exists():
                with open(knowledge_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                
                # Check for conversation ID references (potential leakage)
                for conv_id in conversation_ids:
                    if str(conv_id).lower() in content:
                        issues.append(IntegrityIssue(
                            component="cross_tier",
                            issue_type="tier_boundary_violation",
                            severity="warning",
                            message=f"Conversation ID {conv_id} found in Tier 2 (should only be in Tier 1)",
                            affected_data=f"Conversation ID: {conv_id}",
                            auto_repairable=False
                        ))
                        break  # Report once, not for every ID
        
        except Exception as e:
            issues.append(IntegrityIssue(
                component="cross_tier",
                issue_type="consistency_check_error",
                severity="warning",
                message=f"Failed to check cross-tier consistency: {e}",
                affected_data=str(e)
            ))
        
        return issues
    
    def _repair_missing_history(self, path: Path):
        """Repair missing conversation history file."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                # Initialize with header comment
                pass
        except Exception as e:
            print(f"Failed to repair missing history: {e}")
    
    def _repair_missing_knowledge_graph(self, path: Path):
        """Repair missing knowledge graph file."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            default_structure = {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "patterns": {},
                "confidence_threshold": 0.50,
                "min_occurrences": 3
            }
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(default_structure, f, default_flow_style=False)
        except Exception as e:
            print(f"Failed to repair missing knowledge graph: {e}")
    
    def _repair_missing_dev_context(self, path: Path):
        """Repair missing development context file."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            default_structure = {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "git_status": {},
                "test_coverage": {},
                "project_health": {}
            }
            with open(path, 'w', encoding='utf-8') as f:
                yaml.dump(default_structure, f, default_flow_style=False)
        except Exception as e:
            print(f"Failed to repair missing development context: {e}")
    
    def generate_report(self, integrity_report: IntegrityReport) -> str:
        """
        Generate human-readable integrity report.
        
        Args:
            integrity_report: Integrity check results
        
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 70)
        report.append("CORTEX BRAIN INTEGRITY REPORT")
        report.append("=" * 70)
        report.append(f"Timestamp: {integrity_report.timestamp}")
        report.append(f"Status: {integrity_report.status.value.upper()}")
        report.append("")
        
        # Summary
        if integrity_report.status == IntegrityStatus.HEALTHY:
            report.append("✅ Brain integrity is HEALTHY")
        elif integrity_report.status == IntegrityStatus.DEGRADED:
            report.append("⚠️  Brain integrity is DEGRADED")
        elif integrity_report.status == IntegrityStatus.CORRUPTED:
            report.append("❌ Brain integrity is CORRUPTED")
        
        report.append(f"Total Issues: {len(integrity_report.issues)}")
        report.append(f"  • Critical: {integrity_report.metadata.get('critical_count', 0)}")
        report.append(f"  • Errors: {integrity_report.metadata.get('error_count', 0)}")
        report.append(f"  • Warnings: {integrity_report.metadata.get('warning_count', 0)}")
        
        if integrity_report.auto_repairs_applied > 0:
            report.append(f"Auto-Repairs Applied: {integrity_report.auto_repairs_applied}")
        
        report.append("")
        report.append("=" * 70)
        report.append("")
        
        # Issues by component
        if integrity_report.issues:
            components = {}
            for issue in integrity_report.issues:
                if issue.component not in components:
                    components[issue.component] = []
                components[issue.component].append(issue)
            
            for component, issues in components.items():
                report.append(f"{component.upper()}:")
                for issue in issues:
                    severity_icon = {
                        "critical": "❌",
                        "error": "⚠️",
                        "warning": "⚠️",
                        "info": "ℹ️"
                    }.get(issue.severity, "•")
                    
                    report.append(f"  {severity_icon} [{issue.severity.upper()}] {issue.message}")
                    
                    if issue.affected_data:
                        report.append(f"      Affected: {issue.affected_data}")
                    
                    if issue.auto_repairable and issue.repair_action:
                        report.append(f"      Repair: {issue.repair_action}")
                
                report.append("")
        else:
            report.append("✅ No integrity issues detected")
            report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)


def check_brain_integrity(auto_repair: bool = False) -> bool:
    """
    Convenience function to check brain integrity.
    
    Args:
        auto_repair: Whether to automatically repair issues
    
    Returns:
        True if brain is healthy
    """
    checker = IntegrityChecker(auto_repair=auto_repair)
    result = checker.check_all()
    print(checker.generate_report(result))
    return result.status in [IntegrityStatus.HEALTHY, IntegrityStatus.DEGRADED]


if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Check CORTEX brain integrity")
    parser.add_argument("--auto-repair", action="store_true", help="Automatically repair issues")
    args = parser.parse_args()
    
    healthy = check_brain_integrity(auto_repair=args.auto_repair)
    sys.exit(0 if healthy else 1)
