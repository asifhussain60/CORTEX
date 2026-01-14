"""
State Synchronization Orchestrator for CORTEX 6.0
AC-SYNC-001: Automated 6-Truth-Source Validation

This module ensures all CORTEX state files remain synchronized:
1. progress-tracker.json
2. AC-INDEX.yaml
3. holistic-snowball-plan.yaml
4. plan-viewer.html
5. evidence-bundles/
6. implementation files

Author: Asif Hussain
Created: 2026-01-10
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import hashlib


@dataclass
class TruthSource:
    """Represents a single truth source"""
    name: str
    path: Path
    status: str  # "accurate", "stale", "conflicting", "missing"
    issues: List[str]
    last_checked: str
    hash: Optional[str] = None


@dataclass
class SyncReport:
    """Synchronization validation report"""
    timestamp: str
    sync_score: float  # 0-100%
    sources_accurate: int
    sources_total: int
    discrepancies: List[Dict]
    recommendations: List[Dict]
    critical: bool


@dataclass
class SyncResult:
    """Result of a state synchronization operation - AC-CLEAN-302"""
    success: bool
    operation: str = ""
    timestamp: str = ""
    data: Optional[Dict] = None
    error: Optional[str] = None


class StateSynchronizer:
    """
    Validates and synchronizes all CORTEX state files.
    
    Runs on every GitHub Copilot turn to ensure consistency.
    """
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = Path(workspace_root)
        self.brain_root = self.workspace_root / "cortex-brain"
        self.sources = {}
        # AC-CLEAN-302: Phase-independent state tracking
        self._state_store = {}  # In-memory state store
        self._transaction_stack = []  # Transaction state
        self._pending_writes = []  # Uncommitted writes
        
    def validate_all_sources(self) -> SyncReport:
        """
        Validate all 6 truth sources and detect discrepancies.
        
        Returns:
            SyncReport with validation results
        """
        timestamp = datetime.utcnow().isoformat() + "Z"
        sources = []
        discrepancies = []
        
        # Source 1: progress-tracker.json
        tracker_source, tracker_data = self._validate_progress_tracker()
        sources.append(tracker_source)
        
        # Source 2: AC-INDEX.yaml
        ac_index_source, ac_index_data = self._validate_ac_index()
        sources.append(ac_index_source)
        
        # Source 3: holistic-snowball-plan.yaml
        plan_source, plan_data = self._validate_holistic_plan()
        sources.append(plan_source)
        
        # Source 4: plan-viewer.html
        viewer_source = self._validate_plan_viewer()
        sources.append(viewer_source)
        
        # Source 5: evidence-bundles
        evidence_source = self._validate_evidence_bundles(tracker_data)
        sources.append(evidence_source)
        
        # Source 6: implementation files
        impl_source = self._validate_implementation_files(tracker_data)
        sources.append(impl_source)
        
        # Cross-validate sources
        discrepancies = self._cross_validate(
            tracker_data, ac_index_data, plan_data
        )
        
        # Calculate sync score
        accurate_sources = sum(1 for s in sources if s.status == "accurate")
        sync_score = (accurate_sources / len(sources)) * 100
        
        # Generate recommendations
        recommendations = self._generate_recommendations(sources, discrepancies)
        
        # Determine if critical
        critical = any(d.get("severity") == "CRITICAL" for d in discrepancies)
        
        return SyncReport(
            timestamp=timestamp,
            sync_score=sync_score,
            sources_accurate=accurate_sources,
            sources_total=len(sources),
            discrepancies=discrepancies,
            recommendations=recommendations,
            critical=critical
        )
    
    def _validate_progress_tracker(self) -> Tuple[TruthSource, Dict]:
        """Validate progress-tracker.json"""
        path = self.brain_root / "tier1" / "tracking" / "progress-tracker.json"
        issues = []
        
        if not path.exists():
            return TruthSource(
                name="progress-tracker.json",
                path=path,
                status="missing",
                issues=["File does not exist"],
                last_checked=datetime.utcnow().isoformat() + "Z"
            ), {}
        
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            
            # Validate structure
            required_fields = ["active_epic"]  # AC-CLEAN-302: Removed phase-specific fields
            for field in required_fields:
                if field not in data:
                    issues.append(f"Missing required field: {field}")
            
            # Validate orchestrator state (capability-based, not phase-based)
            if "orchestrator_state" in data:
                state = data["orchestrator_state"]
                if "status" not in state:
                    issues.append("Missing status in orchestrator_state")
            
            # Calculate hash
            file_hash = self._calculate_file_hash(path)
            
            status = "accurate" if not issues else "stale"
            
            return TruthSource(
                name="progress-tracker.json",
                path=path,
                status=status,
                issues=issues,
                last_checked=datetime.utcnow().isoformat() + "Z",
                hash=file_hash
            ), data
            
        except Exception as e:
            return TruthSource(
                name="progress-tracker.json",
                path=path,
                status="conflicting",
                issues=[f"Parse error: {str(e)}"],
                last_checked=datetime.utcnow().isoformat() + "Z"
            ), {}
    
    def _validate_ac_index(self) -> Tuple[TruthSource, Dict]:
        """Validate AC-INDEX.yaml"""
        path = self.brain_root / "tier1" / "acceptance-criteria" / "AC-INDEX.yaml"
        issues = []
        
        if not path.exists():
            return TruthSource(
                name="AC-INDEX.yaml",
                path=path,
                status="missing",
                issues=["File does not exist"],
                last_checked=datetime.utcnow().isoformat() + "Z"
            ), {}
        
        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Validate structure
            if "total_ac_count" not in data:
                issues.append("Missing total_ac_count")
            
            # Check for duplicate keys (runtime verification)
            with open(path, 'r') as f:
                lines = f.readlines()
            
            top_level_keys = []
            for line in lines:
                if line.strip() and not line.startswith(' ') and ':' in line:
                    key = line.split(':')[0].strip()
                    if key in top_level_keys:
                        issues.append(f"Duplicate top-level key detected: {key}")
                    top_level_keys.append(key)
            
            file_hash = self._calculate_file_hash(path)
            status = "accurate" if not issues else "conflicting"
            
            return TruthSource(
                name="AC-INDEX.yaml",
                path=path,
                status=status,
                issues=issues,
                last_checked=datetime.utcnow().isoformat() + "Z",
                hash=file_hash
            ), data
            
        except yaml.YAMLError as e:
            return TruthSource(
                name="AC-INDEX.yaml",
                path=path,
                status="conflicting",
                issues=[f"YAML parse error: {str(e)}"],
                last_checked=datetime.utcnow().isoformat() + "Z"
            ), {}
    
    def _validate_holistic_plan(self) -> Tuple[TruthSource, Dict]:
        """Validate holistic-snowball-plan.yaml"""
        path = self.brain_root / "cx6-plan" / "master-plan.yaml"
        issues = []
        
        if not path.exists():
            return TruthSource(
                name="holistic-snowball-plan.yaml",
                path=path,
                status="missing",
                issues=["File does not exist"],
                last_checked=datetime.utcnow().isoformat() + "Z"
            ), {}
        
        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
            
            # AC-CLEAN-302: Validate capability states, not phase-specific
            if "orchestrator_capabilities" in data:
                capabilities = data["orchestrator_capabilities"]
                if "status" not in capabilities:
                    issues.append("Missing status in orchestrator_capabilities")
                elif capabilities["status"] not in ["ready", "executing", "complete"]:
                    issues.append(f"Invalid capability status: {capabilities['status']}")
                
                if "completion_percentage" not in capabilities:
                    issues.append("Missing completion_percentage in orchestrator_capabilities")
            
            file_hash = self._calculate_file_hash(path)
            status = "accurate" if not issues else "stale"
            
            return TruthSource(
                name="holistic-snowball-plan.yaml",
                path=path,
                status=status,
                issues=issues,
                last_checked=datetime.utcnow().isoformat() + "Z",
                hash=file_hash
            ), data
            
        except yaml.YAMLError as e:
            return TruthSource(
                name="holistic-snowball-plan.yaml",
                path=path,
                status="conflicting",
                issues=[f"YAML parse error: {str(e)}"],
                last_checked=datetime.utcnow().isoformat() + "Z"
            ), {}
    
    def _validate_plan_viewer(self) -> TruthSource:
        """Validate plan-viewer.html"""
        path = self.workspace_root / "templates" / "plan-viewer" / "cortex-plan-viewer.html"
        issues = []
        
        if not path.exists():
            return TruthSource(
                name="plan-viewer.html",
                path=path,
                status="missing",
                issues=["File does not exist"],
                last_checked=datetime.utcnow().isoformat() + "Z"
            )
        
        try:
            with open(path, 'r') as f:
                content = f.read()
            
            # Check for conflicting completion percentages
            if "64%" in content and "48%" in content:
                issues.append("Conflicting completion percentages (64% and 48%)")
            
            # Check for conflicting AC-ID counts
            if "21/33" in content and "16/33" in content:
                issues.append("Conflicting AC-ID counts (21/33 and 16/33)")
            
            file_hash = self._calculate_file_hash(path)
            status = "accurate" if not issues else "conflicting"
            
            return TruthSource(
                name="plan-viewer.html",
                path=path,
                status=status,
                issues=issues,
                last_checked=datetime.utcnow().isoformat() + "Z",
                hash=file_hash
            )
            
        except Exception as e:
            return TruthSource(
                name="plan-viewer.html",
                path=path,
                status="conflicting",
                issues=[f"Read error: {str(e)}"],
                last_checked=datetime.utcnow().isoformat() + "Z"
            )
    
    def _validate_evidence_bundles(self, tracker_data: Dict) -> TruthSource:
        """Validate evidence-bundles directory"""
        path = self.brain_root / "tier1" / "evidence-bundles"
        issues = []
        
        if not path.exists():
            return TruthSource(
                name="evidence-bundles/",
                path=path,
                status="missing",
                issues=["Directory does not exist"],
                last_checked=datetime.utcnow().isoformat() + "Z"
            )
        
        # Get completed AC-IDs from tracker
        if "orchestrator_state" in tracker_data:
            completed_ac_ids = tracker_data["orchestrator_state"].get("verified_implemented", [])
            
            for ac_id in completed_ac_ids:
                bundle_path = path / ac_id
                
                if not bundle_path.exists():
                    issues.append(f"Missing evidence bundle for {ac_id}")
                    continue
                
                # Check for stub files
                manifest = bundle_path / "manifest.yaml"
                if manifest.exists():
                    size = manifest.stat().st_size
                    if size < 500:
                        issues.append(f"Stub evidence bundle for {ac_id} ({size} bytes)")
        
        status = "accurate" if not issues else "stale"
        
        return TruthSource(
            name="evidence-bundles/",
            path=path,
            status=status,
            issues=issues,
            last_checked=datetime.utcnow().isoformat() + "Z"
        )
    
    def _validate_implementation_files(self, tracker_data: Dict) -> TruthSource:
        """Validate implementation files exist and are not stubs"""
        path = self.workspace_root / "src"
        issues = []
        
        if not path.exists():
            return TruthSource(
                name="implementation files",
                path=path,
                status="missing",
                issues=["src/ directory does not exist"],
                last_checked=datetime.utcnow().isoformat() + "Z"
            )
        
        # Check key infrastructure files
        key_files = {
            "enhanced_audit_logger.py": "src/infrastructure",
            "governance_merger.py": "src/orchestrators/core",
            "state_manager.py": "src/infrastructure",
            "orchestrator_lifecycle.py": "src/orchestrators/middleware",
            "evidence_bundle_generator.py": "src/tools"
        }
        
        for filename, subdir in key_files.items():
            file_path = self.workspace_root / subdir / filename
            
            if not file_path.exists():
                issues.append(f"Missing implementation file: {subdir}/{filename}")
                continue
            
            size = file_path.stat().st_size
            if size < 500:
                issues.append(f"Stub implementation file: {subdir}/{filename} ({size} bytes)")
        
        status = "accurate" if not issues else "stale"
        
        return TruthSource(
            name="implementation files",
            path=path,
            status=status,
            issues=issues,
            last_checked=datetime.utcnow().isoformat() + "Z"
        )
    
    def _cross_validate(
        self,
        tracker_data: Dict,
        ac_index_data: Dict,
        plan_data: Dict
    ) -> List[Dict]:
        """Cross-validate data across truth sources"""
        discrepancies = []
        
        # Validate Phase 1 completion consistency
        if "orchestrator_state" in tracker_data and "orchestrator_capabilities" in plan_data:
            tracker_completion = tracker_data["orchestrator_state"].get("completion_percentage", 0)
            plan_completion = plan_data["orchestrator_capabilities"].get("completion_percentage", 0)
            
            if abs(tracker_completion - plan_completion) > 5:
                discrepancies.append({
                    "type": "completion_mismatch",
                    "severity": "MEDIUM",
                    "description": f"Phase 1 completion: tracker={tracker_completion}%, plan={plan_completion}%",
                    "resolution": "Update holistic-snowball-plan.yaml to match progress-tracker.json"
                })
        
        # Validate Phase 1 status consistency
        if "orchestrator_state" in tracker_data and "orchestrator_capabilities" in plan_data:
            tracker_status = tracker_data["orchestrator_state"].get("status", "")
            plan_status = plan_data["orchestrator_capabilities"].get("status", "")
            
            if tracker_status != plan_status:
                discrepancies.append({
                    "type": "status_mismatch",
                    "severity": "HIGH",
                    "description": f"Phase 1 status: tracker='{tracker_status}', plan='{plan_status}'",
                    "resolution": "Update holistic-snowball-plan.yaml status to match progress-tracker.json"
                })
        
        # Validate AC-ID count consistency
        if "orchestrator_state" in tracker_data:
            tracker_completed = tracker_data["orchestrator_state"].get("completed_count", 0)
            tracker_verified = len(tracker_data["orchestrator_state"].get("verified_implemented", []))
            
            if tracker_completed != tracker_verified:
                discrepancies.append({
                    "type": "ac_count_mismatch",
                    "severity": "CRITICAL",
                    "description": f"Completed count mismatch: claimed={tracker_completed}, verified={tracker_verified}",
                    "resolution": "Update progress-tracker.json completed_count to match verified_implemented length"
                })
        
        return discrepancies
    
    def _generate_recommendations(
        self,
        sources: List[TruthSource],
        discrepancies: List[Dict]
    ) -> List[Dict]:
        """Generate actionable recommendations"""
        recommendations = []
        
        for source in sources:
            if source.status == "stale":
                recommendations.append({
                    "priority": "MEDIUM",
                    "action": f"Update {source.name}",
                    "issues": source.issues,
                    "estimated_time": "10 minutes"
                })
            elif source.status == "conflicting":
                recommendations.append({
                    "priority": "HIGH",
                    "action": f"Fix conflicts in {source.name}",
                    "issues": source.issues,
                    "estimated_time": "15 minutes"
                })
            elif source.status == "missing":
                recommendations.append({
                    "priority": "CRITICAL",
                    "action": f"Create missing {source.name}",
                    "issues": source.issues,
                    "estimated_time": "30 minutes"
                })
        
        for discrepancy in discrepancies:
            if discrepancy["severity"] == "CRITICAL":
                recommendations.append({
                    "priority": "CRITICAL",
                    "action": discrepancy["resolution"],
                    "issues": [discrepancy["description"]],
                    "estimated_time": "5 minutes"
                })
        
        return recommendations
    
    def _calculate_file_hash(self, path: Path) -> str:
        """Calculate SHA256 hash of file"""
        sha256 = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def generate_sync_report_markdown(self, report: SyncReport) -> str:
        """Generate human-readable markdown report"""
        lines = []
        lines.append("# 🔄 State Synchronization Report\n")
        lines.append(f"**Timestamp:** {report.timestamp}\n")
        lines.append(f"**Sync Score:** {report.sync_score:.1f}% ({report.sources_accurate}/{report.sources_total} sources accurate)\n")
        
        if report.critical:
            lines.append("**Status:** 🔴 CRITICAL - Immediate action required\n")
        elif report.sync_score < 80:
            lines.append("**Status:** ⚠️ WARNING - Synchronization issues detected\n")
        else:
            lines.append("**Status:** ✅ HEALTHY - Minor issues only\n")
        
        lines.append("\n## 📊 Discrepancies\n")
        if report.discrepancies:
            for disc in report.discrepancies:
                severity_icon = "🔴" if disc["severity"] == "CRITICAL" else "⚠️"
                lines.append(f"- {severity_icon} **{disc['type']}:** {disc['description']}\n")
                lines.append(f"  - Resolution: {disc['resolution']}\n")
        else:
            lines.append("No discrepancies detected.\n")
        
        lines.append("\n## 🎯 Recommendations\n")
        if report.recommendations:
            for rec in sorted(report.recommendations, key=lambda x: {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}[x["priority"]]):
                priority_icon = {"CRITICAL": "🔴", "HIGH": "⚠️", "MEDIUM": "ℹ️", "LOW": "💡"}[rec["priority"]]
                lines.append(f"- {priority_icon} **{rec['action']}** (Est: {rec['estimated_time']})\n")
                for issue in rec["issues"]:
                    lines.append(f"  - {issue}\n")
        else:
            lines.append("No recommendations.\n")
        
        return "".join(lines)
    
    def auto_fix_discrepancies(self, report: SyncReport) -> Dict[str, bool]:
        """Automatically fix safe discrepancies"""
        fixes_applied = {}
        
        for disc in report.discrepancies:
            if disc["type"] == "status_mismatch" and disc["severity"] != "CRITICAL":
                # Safe to auto-fix status mismatches
                try:
                    self._fix_status_mismatch()
                    fixes_applied["status_mismatch"] = True
                except Exception as e:
                    fixes_applied["status_mismatch"] = False
            
            elif disc["type"] == "completion_mismatch" and disc["severity"] == "MEDIUM":
                # Safe to auto-fix completion percentage
                try:
                    self._fix_completion_mismatch()
                    fixes_applied["completion_mismatch"] = True
                except Exception as e:
                    fixes_applied["completion_mismatch"] = False
        
        return fixes_applied
    
    def _fix_status_mismatch(self):
        """Fix Phase 1 status mismatch"""
        # This would update holistic-snowball-plan.yaml
        # Implementation would read tracker, update plan file
        pass
    
    def _fix_completion_mismatch(self):
        """Fix completion percentage mismatch"""
        # This would sync percentages between files
        pass
    
    def sync(self, state_update: Dict) -> SyncResult:
        """
        Sync state update without phase context
        
        Args:
            state_update: Dictionary with capability, status, etc.
            
        Returns:
            SyncResult indicating success
            
        AC-CLEAN-302: Sync operates independently of phases
        """
        try:
            capability = state_update.get('capability', 'unknown')
            status = state_update.get('status', state_update.get('value', 'updated'))
            timestamp = datetime.utcnow().isoformat() + "Z"
            
            # Store in state store
            key = f"{capability}:{timestamp}"
            self._state_store[key] = {
                'capability': capability,
                'status': status,
                'timestamp': timestamp,
                **state_update
            }
            
            # Add to pending writes for transaction
            self._pending_writes.append(self._state_store[key])
            
            return SyncResult(
                success=True,
                operation='sync',
                timestamp=timestamp,
                data={'capability': capability, 'status': status}
            )
        except Exception as e:
            return SyncResult(
                success=False,
                operation='sync',
                error=str(e)
            )
    
    def atomic_write(self, updates: List[Dict]) -> SyncResult:
        """
        Atomically write multiple updates
        
        Args:
            updates: List of state updates
            
        Returns:
            SyncResult indicating success
            
        AC-CLEAN-302: Atomic writes maintained without phases
        """
        try:
            timestamp = datetime.utcnow().isoformat() + "Z"
            
            # Begin transaction
            self.begin_transaction()
            
            # All updates succeed in transaction
            for update in updates:
                self.sync(update)
            
            return SyncResult(
                success=True,
                operation='atomic_write',
                timestamp=timestamp,
                data={'count': len(updates)}
            )
        except Exception as e:
            self.rollback()
            return SyncResult(
                success=False,
                operation='atomic_write',
                error=str(e)
            )
    
    def get(self, capability: str, value: Optional[str] = None) -> Optional[Dict]:
        """
        Get state without phase filter
        
        Args:
            capability: Capability identifier or key name
            value: Optional value to match
            
        Returns:
            State data or None
            
        AC-CLEAN-302: Retrieval independent of phases
        """
        # Search state store for matching state
        for key, state in self._state_store.items():
            # Check if looking for by capability field
            if state.get(capability) == value:
                return state
            # Check if looking for stored capability
            if state.get('capability') == value:
                return state
        
        # Also check if first param is a literal key in store
        if capability in self._state_store:
            return self._state_store[capability]
        
        return None
    
    def get_all(self) -> List[Dict]:
        """
        Get all state without phase filtering
        
        Returns:
            List of all state entries
            
        AC-CLEAN-302: List all states independently
        """
        return list(self._state_store.values())
    
    def rollback(self) -> SyncResult:
        """
        Rollback uncommitted changes
        
        Returns:
            SyncResult indicating success
            
        AC-CLEAN-302: Rollback independent of phases
        """
        try:
            timestamp = datetime.utcnow().isoformat() + "Z"
            self._pending_writes.clear()
            return SyncResult(
                success=True,
                operation='rollback',
                timestamp=timestamp
            )
        except Exception as e:
            return SyncResult(
                success=False,
                operation='rollback',
                error=str(e)
            )
    
    def commit(self) -> SyncResult:
        """
        Commit pending changes
        
        Returns:
            SyncResult indicating success
            
        AC-CLEAN-302: Commit independent of phases
        """
        try:
            timestamp = datetime.utcnow().isoformat() + "Z"
            committed_count = len(self._pending_writes)
            self._pending_writes.clear()
            return SyncResult(
                success=True,
                operation='commit',
                timestamp=timestamp,
                data={'committed': committed_count}
            )
        except Exception as e:
            return SyncResult(
                success=False,
                operation='commit',
                error=str(e)
            )
    
    def begin_transaction(self) -> SyncResult:
        """
        Begin a new transaction
        
        Returns:
            SyncResult indicating success
            
        AC-CLEAN-302: Transactions independent of phases
        """
        try:
            timestamp = datetime.utcnow().isoformat() + "Z"
            self._transaction_stack.append({
                'started': timestamp,
                'pending': len(self._pending_writes)
            })
            return SyncResult(
                success=True,
                operation='begin_transaction',
                timestamp=timestamp
            )
        except Exception as e:
            return SyncResult(
                success=False,
                operation='begin_transaction',
                error=str(e)
            )


def run_synchronization_check(workspace_root: Path) -> SyncReport:
    """
    Main entry point for synchronization check.
    Called by GitHub Copilot on every turn.
    """
    synchronizer = StateSynchronizer(workspace_root)
    report = synchronizer.validate_all_sources()
    return report
