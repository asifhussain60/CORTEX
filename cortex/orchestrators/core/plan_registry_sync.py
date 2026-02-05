"""
CORTEX Plan Registry Sync Orchestrator
Purpose: Autonomous AUDIT mode variance detection + dashboard sync
Authority: Phase 6 implementation (cortex-registry/_cortex-master/meta/audit-sync-implementation.md)
Status: PHASE 6 - AUDIT Sync Implementation
"""

import json
import yaml
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class PlanRegistrySyncOrchestrator:
    """
    Detects variance between index.yaml and plan-summary.json, triggers dashboard sync.
    
    Variance Thresholds:
    - >20%: Silent auto-sync (no user notification)
    - 10-20%: Notify user + sync
    - <10%: No action (data is current)
    """
    
    REGISTRY_ROOT = Path(__file__).parent.parent.parent.parent / "cortex-registry" / "_cortex-master"
    INDEX_FILE = REGISTRY_ROOT / "index.yaml"
    PLAN_SUMMARY_FILE = REGISTRY_ROOT / "dashboard" / "data" / "plan-summary.json"
    
    VARIANCE_THRESHOLDS = {
        "silent_sync": 0.20,      # >20%: silent sync
        "warning_sync": 0.10,      # 10-20%: warn + sync
        "no_action": 0.10          # <10%: no action
    }
    
    AUDIT_INTERVAL = timedelta(minutes=5)  # AUDIT runs every 5 minutes
    SYNC_DEBOUNCE = timedelta(seconds=60)  # Max 1 sync per 60 seconds
    
    def __init__(self):
        self.last_sync_time = None
        self.index_cache = None
        self.summary_cache = None
    
    def calculate_variance(self) -> Tuple[float, Dict]:
        """
        Calculate variance between index.yaml (source) and plan-summary.json (derived).
        
        Returns:
            Tuple[variance_score (0-1.0), details_dict]
        
        Formula:
            variance = |expected_metrics - actual_metrics| / expected_metrics
        """
        try:
            index_data = self._load_index()
            summary_data = self._load_summary()
            
            if not index_data or not summary_data:
                logger.error("Failed to load registry files")
                return 0.0, {"error": "Missing registry files"}
            
            # Extract metrics from both sources
            index_metrics = self._extract_metrics(index_data)
            summary_metrics = self._extract_metrics_from_summary(summary_data)
            
            # Calculate variance for each metric
            variances = []
            details = {}
            
            for key in index_metrics.keys():
                if key in summary_metrics:
                    expected = index_metrics[key]
                    actual = summary_metrics[key]
                    
                    if expected > 0:
                        variance_value = abs(expected - actual) / expected
                        variances.append(variance_value)
                        details[key] = {
                            "expected": expected,
                            "actual": actual,
                            "variance": variance_value
                        }
            
            # Overall variance: average of all individual variances
            overall_variance = sum(variances) / len(variances) if variances else 0.0
            details["overall_variance"] = overall_variance
            details["last_checked"] = datetime.utcnow().isoformat() + "Z"
            
            return overall_variance, details
            
        except Exception as e:
            logger.error(f"Variance calculation failed: {e}")
            return 0.0, {"error": str(e)}
    
    def should_trigger_sync(self, variance_score: float) -> Tuple[bool, str]:
        """
        Determine if variance exceeds thresholds and should trigger sync.
        
        Args:
            variance_score: Calculated variance (0-1.0)
        
        Returns:
            Tuple[should_sync (bool), reason (str)]
        """
        # Check debounce (don't sync more than once per 60 seconds)
        if self.last_sync_time:
            time_since_last_sync = datetime.utcnow() - self.last_sync_time
            if time_since_last_sync < self.SYNC_DEBOUNCE:
                return False, f"Debounce active (last sync {time_since_last_sync.total_seconds():.0f}s ago)"
        
        # Check variance thresholds
        if variance_score > self.VARIANCE_THRESHOLDS["silent_sync"]:
            return True, "SILENT_SYNC (variance >20%)"
        elif variance_score > self.VARIANCE_THRESHOLDS["warning_sync"]:
            return True, "WARN_SYNC (variance 10-20%)"
        else:
            return False, f"ACCEPTABLE (variance {variance_score*100:.1f}% <10%)"
    
    def update_dashboard_metrics(self, index_data: Dict) -> bool:
        """
        Update plan-summary.json with fresh metrics from index.yaml.
        
        Args:
            index_data: Parsed index.yaml content
        
        Returns:
            bool: Success status
        """
        try:
            # Load existing summary
            summary_data = self._load_summary()
            if not summary_data:
                summary_data = self._create_default_summary()
            
            # Extract fresh metrics from index
            phases_active = len(index_data.get("phases", {}).get("active", []))
            phases_completed = len(index_data.get("phases", {}).get("completed", []))
            enhancements_active = len(index_data.get("enhancements", {}).get("active", []))
            
            # Update metadata
            summary_data["metadata"]["last_updated"] = datetime.utcnow().isoformat() + "Z"
            summary_data["metadata"]["sync_timestamp"] = datetime.utcnow().isoformat() + "Z"
            summary_data["metadata"]["next_audit"] = (datetime.utcnow() + self.AUDIT_INTERVAL).isoformat() + "Z"
            
            # Update statistics
            total_phases = phases_active + phases_completed
            completion_rate = (phases_completed / total_phases) if total_phases > 0 else 0.0
            
            summary_data["statistics"]["total_phases"] = total_phases
            summary_data["statistics"]["active_phases"] = phases_active
            summary_data["statistics"]["completed_phases"] = phases_completed
            summary_data["statistics"]["active_enhancements"] = enhancements_active
            summary_data["statistics"]["completion_rate"] = round(completion_rate, 2)
            summary_data["statistics"]["overall_status"] = "PRODUCTION_READY" if completion_rate >= 0.85 else "IN_PROGRESS"
            
            # Recalculate variance
            variance, details = self.calculate_variance()
            summary_data["metadata"]["variance_score"] = round(variance, 3)
            summary_data["metadata"]["variance_details"] = details
            
            # Write updated summary
            self.PLAN_SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(self.PLAN_SUMMARY_FILE, 'w') as f:
                json.dump(summary_data, f, indent=2)
            
            logger.info(f"Dashboard metrics updated (variance: {variance*100:.1f}%)")
            self.last_sync_time = datetime.utcnow()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update dashboard metrics: {e}")
            return False
    
    def emit_sync_event(self, variance_score: float, reason: str) -> Dict:
        """
        Emit event signal for dashboard polling to detect.
        
        Args:
            variance_score: Calculated variance
            reason: Reason for sync (SILENT_SYNC, WARN_SYNC, etc.)
        
        Returns:
            Event metadata dict
        """
        event = {
            "event_type": "PLAN_REGISTRY_SYNC",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "variance_score": variance_score,
            "sync_reason": reason,
            "debounce_interval_seconds": self.SYNC_DEBOUNCE.total_seconds(),
            "next_check": (datetime.utcnow() + self.AUDIT_INTERVAL).isoformat() + "Z"
        }
        
        logger.info(f"Sync event emitted: {reason} (variance: {variance_score*100:.1f}%)")
        return event
    
    # ==================== Private Helpers ====================
    
    def _load_index(self) -> Optional[Dict]:
        """Load and parse index.yaml."""
        try:
            with open(self.INDEX_FILE, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load index.yaml: {e}")
            return None
    
    def _load_summary(self) -> Optional[Dict]:
        """Load and parse plan-summary.json."""
        try:
            with open(self.PLAN_SUMMARY_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load plan-summary.json: {e}")
            return None
    
    def _extract_metrics(self, index_data: Dict) -> Dict:
        """Extract phase/enhancement counts from index.yaml."""
        phases = index_data.get("phases", {})
        enhancements = index_data.get("enhancements", {})
        
        return {
            "active_phases": len(phases.get("active", [])),
            "completed_phases": len(phases.get("completed", [])),
            "active_enhancements": len(enhancements.get("active", [])),
            "planned_enhancements": len(enhancements.get("planned", []))
        }
    
    def _extract_metrics_from_summary(self, summary_data: Dict) -> Dict:
        """Extract phase/enhancement counts from plan-summary.json."""
        stats = summary_data.get("statistics", {})
        
        return {
            "active_phases": stats.get("active_phases", 0),
            "completed_phases": stats.get("completed_phases", 0),
            "active_enhancements": len(summary_data.get("active_enhancements", [])),
            "planned_enhancements": 0  # Not tracked in summary yet
        }
    
    def _create_default_summary(self) -> Dict:
        """Create default plan-summary.json structure."""
        return {
            "metadata": {
                "version": "1.0",
                "created": datetime.utcnow().isoformat() + "Z",
                "last_updated": datetime.utcnow().isoformat() + "Z",
                "sync_timestamp": datetime.utcnow().isoformat() + "Z",
                "next_audit": (datetime.utcnow() + self.AUDIT_INTERVAL).isoformat() + "Z",
                "variance_score": 0.0
            },
            "statistics": {
                "total_phases": 19,
                "active_phases": 0,
                "completed_phases": 0,
                "active_enhancements": 0,
                "completion_rate": 0.0,
                "overall_status": "INITIALIZING"
            },
            "active_phases": [],
            "completed_phases_2026": [],
            "completed_phases_2025": [],
            "active_enhancements": [],
            "registry_config": {
                "auto_sync_enabled": True,
                "variance_threshold": 0.10,
                "debounce_interval": 60
            }
        }


# ==================== Public API ====================

def execute_plan_registry_sync() -> Dict:
    """
    Execute full sync cycle: calculate variance → check thresholds → update metrics → emit event.
    
    Called by AUDIT mode after P1 infrastructure checks.
    
    Returns:
        Status dict with variance, action taken, and metrics
    """
    orchestrator = PlanRegistrySyncOrchestrator()
    
    # Step 1: Load index (source of truth)
    index_data = orchestrator._load_index()
    if not index_data:
        return {"status": "FAILED", "reason": "Cannot load index.yaml"}
    
    # Step 2: Calculate variance
    variance_score, details = orchestrator.calculate_variance()
    
    # Step 3: Check thresholds
    should_sync, reason = orchestrator.should_trigger_sync(variance_score)
    
    # Step 4: Update metrics if syncing
    sync_executed = False
    if should_sync:
        sync_executed = orchestrator.update_dashboard_metrics(index_data)
    
    # Step 5: Emit event
    event = orchestrator.emit_sync_event(variance_score, reason)
    
    return {
        "status": "SUCCESS",
        "variance_score": variance_score,
        "should_sync": should_sync,
        "sync_executed": sync_executed,
        "reason": reason,
        "event": event,
        "details": details
    }


if __name__ == "__main__":
    # Test execution
    result = execute_plan_registry_sync()
    print(json.dumps(result, indent=2))
