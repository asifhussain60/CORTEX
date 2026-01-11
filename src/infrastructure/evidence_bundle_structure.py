"""
AC-EVIDENCE-001: Evidence Bundle Structure

Defines 3-file evidence bundle format for AC validation:
1. manifest.yaml - Bundle metadata + AC-ID reference
2. test_results.json - Test execution results + coverage data
3. audit_trace.jsonl - Audit events linked to this AC

Status: COMPLETE
Author: GitHub Copilot
Version: 1.0.0
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

import yaml

from src.utils.path_utils import project_root


@dataclass
class TestResult:
    """Individual test result."""
    test_name: str
    status: str  # "passed", "failed", "skipped"
    duration: float
    error_message: Optional[str] = None


@dataclass
class TestMetrics:
    """Test execution metrics."""
    total_tests: int
    passed: int
    failed: int
    skipped: int
    duration: float
    coverage_percentage: float


class EvidenceBundleStructure:
    """
    Manages 3-file evidence bundle structure for AC validation.
    
    Bundle files:
    - manifest.yaml: AC-ID, timestamp, status, metrics summary
    - test_results.json: Detailed test execution results
    - audit_trace.jsonl: Newline-delimited JSON audit events
    """
    
    BUNDLE_DIR_NAME = "evidence_bundles"
    MANIFEST_FILENAME = "manifest.yaml"
    TEST_RESULTS_FILENAME = "test_results.json"
    AUDIT_TRACE_FILENAME = "audit_trace.jsonl"
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize evidence bundle system.
        
        Args:
            logger: Logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        
        try:
            project_dir = Path(project_root())
        except Exception:
            project_dir = Path.cwd()
        
        self.bundle_base_dir = project_dir / "cortex-brain" / self.BUNDLE_DIR_NAME
        self.bundle_base_dir.mkdir(parents=True, exist_ok=True)
    
    def create_bundle_directory(self, ac_id: str) -> Path:
        """
        Create evidence bundle directory for AC-ID.
        
        Args:
            ac_id: Acceptance criteria ID (e.g., "AC-AUDIT-001")
            
        Returns:
            Path to created bundle directory
        """
        # Sanitize AC-ID for filesystem
        safe_ac_id = ac_id.replace(" ", "_").replace("/", "_")
        bundle_dir = self.bundle_base_dir / safe_ac_id
        bundle_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Created evidence bundle directory: {bundle_dir}")
        return bundle_dir
    
    def create_manifest(
        self,
        ac_id: str,
        status: str,
        test_metrics: TestMetrics,
        implementation_notes: Optional[str] = None,
        bundle_dir: Optional[Path] = None
    ) -> Dict:
        """
        Create manifest.yaml for evidence bundle.
        
        Args:
            ac_id: Acceptance criteria ID
            status: Status ("implemented", "partial", "planned")
            test_metrics: TestMetrics object with test results
            implementation_notes: Optional implementation notes
            bundle_dir: Bundle directory (auto-created if None)
            
        Returns:
            Dict with manifest data
        """
        if not bundle_dir:
            bundle_dir = self.create_bundle_directory(ac_id)
        
        manifest = {
            "bundle_version": "1.0",
            "ac_id": ac_id,
            "status": status,
            "created_at": datetime.utcnow().isoformat(),
            "evidence": {
                "test_results": f"{self.TEST_RESULTS_FILENAME}",
                "audit_trace": f"{self.AUDIT_TRACE_FILENAME}",
            },
            "metrics": {
                "total_tests": test_metrics.total_tests,
                "passed": test_metrics.passed,
                "failed": test_metrics.failed,
                "skipped": test_metrics.skipped,
                "duration_seconds": test_metrics.duration,
                "coverage_percentage": test_metrics.coverage_percentage,
                "success_rate": (
                    test_metrics.passed / test_metrics.total_tests * 100
                    if test_metrics.total_tests > 0 else 0
                ),
            },
            "implementation_notes": implementation_notes,
        }
        
        # Write manifest
        manifest_path = bundle_dir / self.MANIFEST_FILENAME
        with open(manifest_path, "w") as f:
            yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)
        
        self.logger.info(f"Created manifest for {ac_id}: {manifest_path}")
        return manifest
    
    def create_test_results_file(
        self,
        ac_id: str,
        test_results: List[TestResult],
        metrics: TestMetrics,
        bundle_dir: Optional[Path] = None
    ) -> Dict:
        """
        Create test_results.json with detailed test data.
        
        Args:
            ac_id: Acceptance criteria ID
            test_results: List of TestResult objects
            metrics: TestMetrics object
            bundle_dir: Bundle directory (auto-created if None)
            
        Returns:
            Dict with test results data
        """
        if not bundle_dir:
            bundle_dir = self.create_bundle_directory(ac_id)
        
        results_data = {
            "ac_id": ac_id,
            "timestamp": datetime.utcnow().isoformat(),
            "summary": asdict(metrics),
            "tests": [
                {
                    "name": tr.test_name,
                    "status": tr.status,
                    "duration": tr.duration,
                    "error": tr.error_message,
                }
                for tr in test_results
            ],
        }
        
        # Write test results
        results_path = bundle_dir / self.TEST_RESULTS_FILENAME
        with open(results_path, "w") as f:
            json.dump(results_data, f, indent=2)
        
        self.logger.info(f"Created test results for {ac_id}: {results_path}")
        return results_data
    
    def append_audit_trace(
        self,
        ac_id: str,
        audit_events: List[Dict],
        bundle_dir: Optional[Path] = None
    ) -> None:
        """
        Append audit events to audit_trace.jsonl (newline-delimited JSON).
        
        Args:
            ac_id: Acceptance criteria ID
            audit_events: List of audit event dicts
            bundle_dir: Bundle directory (auto-created if None)
        """
        if not bundle_dir:
            bundle_dir = self.create_bundle_directory(ac_id)
        
        trace_path = bundle_dir / self.AUDIT_TRACE_FILENAME
        
        with open(trace_path, "a") as f:
            for event in audit_events:
                event["ac_id"] = ac_id
                event["timestamp"] = event.get("timestamp", datetime.utcnow().isoformat())
                f.write(json.dumps(event) + "\n")
        
        self.logger.info(
            f"Appended {len(audit_events)} audit events to {ac_id} trace"
        )
    
    def read_bundle(self, ac_id: str) -> Optional[Dict]:
        """
        Read complete evidence bundle for AC-ID.
        
        Args:
            ac_id: Acceptance criteria ID
            
        Returns:
            Dict with all bundle data or None if not found
        """
        safe_ac_id = ac_id.replace(" ", "_").replace("/", "_")
        bundle_dir = self.bundle_base_dir / safe_ac_id
        
        if not bundle_dir.exists():
            self.logger.warning(f"Bundle directory not found: {bundle_dir}")
            return None
        
        try:
            # Read manifest
            manifest_path = bundle_dir / self.MANIFEST_FILENAME
            with open(manifest_path, "r") as f:
                manifest = yaml.safe_load(f)
            
            # Read test results
            results_path = bundle_dir / self.TEST_RESULTS_FILENAME
            with open(results_path, "r") as f:
                test_results = json.load(f)
            
            # Read audit trace
            audit_events = []
            trace_path = bundle_dir / self.AUDIT_TRACE_FILENAME
            if trace_path.exists():
                with open(trace_path, "r") as f:
                    for line in f:
                        if line.strip():
                            audit_events.append(json.loads(line))
            
            return {
                "ac_id": ac_id,
                "manifest": manifest,
                "test_results": test_results,
                "audit_trace": audit_events,
            }
            
        except Exception as e:
            self.logger.error(f"Error reading bundle for {ac_id}: {e}")
            return None
    
    def list_bundles(self) -> List[str]:
        """
        List all evidence bundles in system.
        
        Returns:
            List of AC-IDs with evidence bundles
        """
        bundles = []
        
        if not self.bundle_base_dir.exists():
            return bundles
        
        for bundle_dir in self.bundle_base_dir.iterdir():
            if bundle_dir.is_dir():
                manifest_path = bundle_dir / self.MANIFEST_FILENAME
                if manifest_path.exists():
                    try:
                        with open(manifest_path, "r") as f:
                            manifest = yaml.safe_load(f)
                            ac_id = manifest.get("ac_id", bundle_dir.name)
                            bundles.append(ac_id)
                    except Exception:
                        pass
        
        return sorted(bundles)
    
    def get_bundle_stats(self, ac_id: str) -> Optional[Dict]:
        """
        Get statistics for an evidence bundle.
        
        Args:
            ac_id: Acceptance criteria ID
            
        Returns:
            Dict with bundle statistics
        """
        bundle = self.read_bundle(ac_id)
        if not bundle:
            return None
        
        manifest = bundle["manifest"]
        metrics = manifest.get("metrics", {})
        
        return {
            "ac_id": ac_id,
            "status": manifest.get("status"),
            "created_at": manifest.get("created_at"),
            "test_count": metrics.get("total_tests", 0),
            "test_passed": metrics.get("passed", 0),
            "test_failed": metrics.get("failed", 0),
            "coverage": metrics.get("coverage_percentage", 0),
            "success_rate": metrics.get("success_rate", 0),
            "audit_events": len(bundle.get("audit_trace", [])),
        }
