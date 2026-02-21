"""
Cross-Reference Validator for CORTEX Registry
ENH-068: Data Integrity Validation System

Detects contradictions across registry YAML files:
- Timestamp inconsistencies
- Metric accuracy violations
- Dependency graph errors
- Status consistency issues
"""
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Set
from datetime import datetime
from enum import Enum
import yaml


class ContradictionType(Enum):
    """Types of contradictions that can be detected"""
    TIMESTAMP = "timestamp"
    METRIC = "metric"
    DEPENDENCY = "dependency"
    STATUS = "status"


class ContradictionSeverity(Enum):
    """Severity levels for contradictions"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class ContradictionReport:
    """Report of detected contradiction"""
    file_path: Path
    contradiction_type: ContradictionType
    severity: ContradictionSeverity
    details: str
    suggested_fix: str
    confidence: float  # 0.0-1.0
    
    def __str__(self) -> str:
        return (
            f"[{self.severity.value}] {self.contradiction_type.value.upper()}\n"
            f"File: {self.file_path}\n"
            f"Issue: {self.details}\n"
            f"Fix: {self.suggested_fix}\n"
            f"Confidence: {self.confidence:.0%}"
        )


class CrossReferenceValidator:
    """Validates data integrity across registry files"""
    
    def __init__(self) -> None:
        """Initialize instance."""
        self.reports: List[ContradictionReport] = []
        self.files_data: Dict[Path, Dict[str, Any]] = {}
    
    def validate_registry(self, registry_path: Path) -> List[ContradictionReport]:
        """
        Main validation entry point
        
        Args:
            registry_path: Path to registry directory
        
        Returns:
            List of contradiction reports
        """
        self.reports = []
        self.files_data = {}
        
        # Load all YAML files
        yaml_files = list(registry_path.glob("*.yaml")) + list(registry_path.glob("*.yml"))
        
        for file_path in yaml_files:
            try:
                with open(file_path, 'r') as f:
                    data = yaml.safe_load(f)
                    if data:
                        self.files_data[file_path] = data
            except Exception as e:
                # Skip files that can't be parsed
                continue
        
        # Run validations
        for file_path, data in self.files_data.items():
            self.reports.extend(self._check_timestamps(file_path, data))
            self.reports.extend(self._check_metrics(file_path, data))
            self.reports.extend(self._check_status(file_path, data))
        
        # Cross-file validations
        self.reports.extend(self._check_dependencies(list(self.files_data.items())))
        
        return self.reports
    
    def _check_timestamps(
        self, 
        file_path: Path, 
        data: Dict[str, Any]
    ) -> List[ContradictionReport]:
        """Validate timestamp consistency"""
        from datetime import timezone
        reports = []
        
        completion_date = data.get('completion_date')
        last_updated = data.get('last_updated')
        
        if completion_date and last_updated:
            try:
                # Parse dates - handle both date-only and datetime formats
                if isinstance(completion_date, str):
                    # Try parsing as datetime first, then as simple date
                    try:
                        comp_dt = datetime.fromisoformat(completion_date.replace('Z', '+00:00'))
                        # If naive datetime, add UTC timezone
                        if comp_dt.tzinfo is None:
                            comp_dt = comp_dt.replace(tzinfo=timezone.utc)
                    except ValueError:
                        # Simple date format like "2026-02-15" - convert to datetime with UTC timezone
                        comp_dt = datetime.strptime(completion_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                else:
                    comp_dt = completion_date
                
                if isinstance(last_updated, str):
                    updated_dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                    # If naive datetime, add UTC timezone
                    if updated_dt.tzinfo is None:
                        updated_dt = updated_dt.replace(tzinfo=timezone.utc)
                else:
                    updated_dt = last_updated
                
                # Completion date should not be after last_updated
                if comp_dt > updated_dt:
                    reports.append(ContradictionReport(
                        file_path=file_path,
                        contradiction_type=ContradictionType.TIMESTAMP,
                        severity=ContradictionSeverity.HIGH,
                        details=f"completion_date ({completion_date}) is after last_updated ({last_updated})",
                        suggested_fix="Update last_updated to be >= completion_date",
                        confidence=0.95
                    ))
            except Exception:
                # Skip invalid date formats
                pass
        
        return reports
    
    def _check_metrics(
        self, 
        file_path: Path, 
        data: Dict[str, Any]
    ) -> List[ContradictionReport]:
        """Validate metric accuracy"""
        reports = []
        
        tests_total = data.get('tests_total')
        tests_passing = data.get('tests_passing')
        
        # Check tests_passing <= tests_total
        if tests_total is not None and tests_passing is not None:
            if tests_passing > tests_total:
                reports.append(ContradictionReport(
                    file_path=file_path,
                    contradiction_type=ContradictionType.METRIC,
                    severity=ContradictionSeverity.CRITICAL,
                    details=f"tests_passing ({tests_passing}) exceeds tests_total ({tests_total})",
                    suggested_fix="Verify test counts or update tests_total",
                    confidence=1.0
                ))
        
        # Check for negative values
        if tests_total is not None and tests_total < 0:
            reports.append(ContradictionReport(
                file_path=file_path,
                contradiction_type=ContradictionType.METRIC,
                severity=ContradictionSeverity.HIGH,
                details=f"tests_total is negative ({tests_total})",
                suggested_fix="Set tests_total to valid positive value",
                confidence=1.0
            ))
        
        if tests_passing is not None and tests_passing < 0:
            reports.append(ContradictionReport(
                file_path=file_path,
                contradiction_type=ContradictionType.METRIC,
                severity=ContradictionSeverity.HIGH,
                details=f"tests_passing is negative ({tests_passing})",
                suggested_fix="Set tests_passing to valid positive value",
                confidence=1.0
            ))
        
        return reports
    
    def _check_status(
        self, 
        file_path: Path, 
        data: Dict[str, Any]
    ) -> List[ContradictionReport]:
        """Validate status consistency"""
        reports = []
        
        status = data.get('status')
        completion_date = data.get('completion_date')
        
        # Status=complete should have completion_date
        if status == 'complete' and not completion_date:
            reports.append(ContradictionReport(
                file_path=file_path,
                contradiction_type=ContradictionType.STATUS,
                severity=ContradictionSeverity.MEDIUM,
                details="status is 'complete' but completion_date is missing",
                suggested_fix="Add completion_date or change status to 'pending'",
                confidence=0.90
            ))
        
        # Status=pending should not have completion_date
        if status in ['pending', 'ready', 'blocked'] and completion_date:
            reports.append(ContradictionReport(
                file_path=file_path,
                contradiction_type=ContradictionType.STATUS,
                severity=ContradictionSeverity.MEDIUM,
                details=f"status is '{status}' but completion_date is set ({completion_date})",
                suggested_fix="Remove completion_date or change status to 'complete'",
                confidence=0.85
            ))
        
        return reports
    
    def _check_dependencies(
        self, 
        all_files: List[tuple[Path, Dict[str, Any]]]
    ) -> List[ContradictionReport]:
        """Validate dependency graph consistency"""
        reports = []
        
        # Build wave_id -> file_path mapping
        wave_ids: Dict[str, Path] = {}
        dependencies_graph: Dict[str, Set[str]] = {}
        
        for file_path, data in all_files:
            wave_id = data.get('wave_id')
            if wave_id:
                wave_ids[wave_id] = file_path
                deps = data.get('dependencies', [])
                if deps:
                    dependencies_graph[wave_id] = set(deps)
        
        # Check for missing dependencies
        for wave_id, deps in dependencies_graph.items():
            for dep in deps:
                if dep not in wave_ids:
                    reports.append(ContradictionReport(
                        file_path=wave_ids[wave_id],
                        contradiction_type=ContradictionType.DEPENDENCY,
                        severity=ContradictionSeverity.HIGH,
                        details=f"Dependency '{dep}' does not exist in registry",
                        suggested_fix=f"Remove '{dep}' from dependencies or add the missing wave file",
                        confidence=0.95
                    ))
        
        # Check for circular dependencies
        def has_cycle(node: str, visited: Set[str], rec_stack: Set[str]) -> bool:
            """Check if dependency graph contains cycles."""
            visited.add(node)
            rec_stack.add(node)
            
            if node in dependencies_graph:
                for neighbor in dependencies_graph[node]:
                    if neighbor not in visited:
                        if has_cycle(neighbor, visited, rec_stack):
                            return True
                    elif neighbor in rec_stack:
                        return True
            
            rec_stack.remove(node)
            return False
        
        visited: Set[str] = set()
        for wave_id in dependencies_graph.keys():
            if wave_id not in visited:
                if has_cycle(wave_id, visited, set()):
                    reports.append(ContradictionReport(
                        file_path=wave_ids[wave_id],
                        contradiction_type=ContradictionType.DEPENDENCY,
                        severity=ContradictionSeverity.CRITICAL,
                        details=f"Circular dependency detected involving '{wave_id}'",
                        suggested_fix="Break the circular dependency chain",
                        confidence=1.0
                    ))
        
        return reports
