"""
Evidence Bundle Generator - Create lightweight evidence for AC implementation.

This module generates 3-file evidence bundles:
1. implementation.py - The actual implementation
2. tests.py - Unit tests proving AC satisfaction
3. evidence.json - Metadata and audit trail

AC-ID: AC-EVIDENCE-001
Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class EvidenceMetadata:
    """Evidence bundle metadata."""
    ac_id: str
    feature_name: str
    implementation_file: str
    test_file: str
    created_at: str
    author: str = "CORTEX 6.0"
    requirements_met: List[str] = None
    tests_passed: bool = False
    test_count: int = 0
    coverage_percent: float = 0.0
    audit_trail: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.requirements_met is None:
            self.requirements_met = []
        if self.audit_trail is None:
            self.audit_trail = []


@dataclass
class EvidenceBundle:
    """Complete evidence bundle."""
    ac_id: str
    bundle_path: Path
    implementation_path: Path
    test_path: Path
    evidence_path: Path
    metadata: EvidenceMetadata


class EvidenceBundleGenerator:
    """
    Evidence Bundle Generator.
    
    Creates lightweight 3-file evidence bundles proving AC implementation.
    
    Structure:
    ```
    cortex-brain/tier1/evidence-bundles/{AC-ID}/
        ├── implementation.py   (actual code)
        ├── tests.py           (unit tests)
        └── evidence.json      (metadata + audit)
    ```
    
    Acceptance Criteria:
    - AC-EVIDENCE-001: 3-file bundle generation
    - AC-EVIDENCE-002: Evidence validation
    - AC-EVIDENCE-003: Evidence storage
    """
    
    def __init__(
        self,
        evidence_base_path: Path,
        workspace_root: Optional[Path] = None
    ):
        """
        Initialize Evidence Bundle Generator.
        
        Args:
            evidence_base_path: Base path for evidence bundles
            workspace_root: Workspace root (for relative paths)
        """
        self.logger = logging.getLogger("cortex.tools.evidence_bundle_generator")
        self.evidence_base_path = Path(evidence_base_path)
        self.workspace_root = Path(workspace_root) if workspace_root else Path.cwd()
        
        # Ensure base path exists
        self.evidence_base_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"EvidenceBundleGenerator initialized at {evidence_base_path}")
    
    def create_bundle(
        self,
        ac_id: str,
        feature_name: str,
        implementation_code: str,
        test_code: str,
        requirements_met: List[str],
        tests_passed: bool = False,
        test_count: int = 0,
        coverage_percent: float = 0.0,
        audit_trail: Optional[List[Dict[str, Any]]] = None
    ) -> EvidenceBundle:
        """
        Create evidence bundle for AC-ID implementation.
        
        Args:
            ac_id: Acceptance criteria ID
            feature_name: Feature name
            implementation_code: Implementation code
            test_code: Test code
            requirements_met: List of requirements satisfied
            tests_passed: Whether tests passed
            test_count: Number of tests
            coverage_percent: Test coverage percentage
            audit_trail: Audit trail entries
            
        Returns:
            EvidenceBundle with paths to all files
        """
        try:
            # Create bundle directory
            bundle_dir = self.evidence_base_path / ac_id
            bundle_dir.mkdir(parents=True, exist_ok=True)
            
            # File paths
            impl_path = bundle_dir / "implementation.py"
            test_path = bundle_dir / "tests.py"
            evidence_path = bundle_dir / "evidence.json"
            
            # Write implementation
            impl_path.write_text(implementation_code, encoding='utf-8')
            self.logger.debug(f"Wrote implementation: {impl_path}")
            
            # Write tests
            test_path.write_text(test_code, encoding='utf-8')
            self.logger.debug(f"Wrote tests: {test_path}")
            
            # Create metadata
            metadata = EvidenceMetadata(
                ac_id=ac_id,
                feature_name=feature_name,
                implementation_file=str(impl_path.relative_to(self.workspace_root)),
                test_file=str(test_path.relative_to(self.workspace_root)),
                created_at=datetime.now().isoformat() + "Z",
                requirements_met=requirements_met,
                tests_passed=tests_passed,
                test_count=test_count,
                coverage_percent=coverage_percent,
                audit_trail=audit_trail or []
            )
            
            # Write evidence.json
            evidence_data = asdict(metadata)
            evidence_path.write_text(
                json.dumps(evidence_data, indent=2),
                encoding='utf-8'
            )
            self.logger.debug(f"Wrote evidence: {evidence_path}")
            
            # Create bundle
            bundle = EvidenceBundle(
                ac_id=ac_id,
                bundle_path=bundle_dir,
                implementation_path=impl_path,
                test_path=test_path,
                evidence_path=evidence_path,
                metadata=metadata
            )
            
            self.logger.info(f"Created evidence bundle for {ac_id} at {bundle_dir}")
            return bundle
            
        except Exception as e:
            self.logger.error(f"Failed to create evidence bundle for {ac_id}: {e}")
            raise
    
    def validate_bundle(self, ac_id: str) -> bool:
        """
        Validate that evidence bundle exists and is complete.
        
        Args:
            ac_id: Acceptance criteria ID
            
        Returns:
            True if bundle is valid
        """
        try:
            bundle_dir = self.evidence_base_path / ac_id
            
            if not bundle_dir.exists():
                self.logger.warning(f"Bundle directory not found: {bundle_dir}")
                return False
            
            # Check required files
            impl_path = bundle_dir / "implementation.py"
            test_path = bundle_dir / "tests.py"
            evidence_path = bundle_dir / "evidence.json"
            
            if not impl_path.exists():
                self.logger.warning(f"Implementation file missing: {impl_path}")
                return False
            
            if not test_path.exists():
                self.logger.warning(f"Test file missing: {test_path}")
                return False
            
            if not evidence_path.exists():
                self.logger.warning(f"Evidence file missing: {evidence_path}")
                return False
            
            # Validate evidence.json structure
            evidence_data = json.loads(evidence_path.read_text(encoding='utf-8'))
            required_fields = ['ac_id', 'feature_name', 'implementation_file', 'test_file', 'created_at']
            
            for field in required_fields:
                if field not in evidence_data:
                    self.logger.warning(f"Evidence missing field: {field}")
                    return False
            
            self.logger.info(f"Evidence bundle validated: {ac_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Bundle validation failed for {ac_id}: {e}")
            return False
    
    def load_bundle(self, ac_id: str) -> Optional[EvidenceBundle]:
        """
        Load existing evidence bundle.
        
        Args:
            ac_id: Acceptance criteria ID
            
        Returns:
            EvidenceBundle or None if not found
        """
        try:
            bundle_dir = self.evidence_base_path / ac_id
            
            if not self.validate_bundle(ac_id):
                return None
            
            # Load metadata
            evidence_path = bundle_dir / "evidence.json"
            evidence_data = json.loads(evidence_path.read_text(encoding='utf-8'))
            
            metadata = EvidenceMetadata(**evidence_data)
            
            # Create bundle
            bundle = EvidenceBundle(
                ac_id=ac_id,
                bundle_path=bundle_dir,
                implementation_path=bundle_dir / "implementation.py",
                test_path=bundle_dir / "tests.py",
                evidence_path=evidence_path,
                metadata=metadata
            )
            
            self.logger.info(f"Loaded evidence bundle: {ac_id}")
            return bundle
            
        except Exception as e:
            self.logger.error(f"Failed to load bundle for {ac_id}: {e}")
            return None
    
    def list_bundles(self) -> List[str]:
        """
        List all evidence bundles.
        
        Returns:
            List of AC-IDs with evidence bundles
        """
        try:
            bundles = []
            
            for item in self.evidence_base_path.iterdir():
                if item.is_dir() and self.validate_bundle(item.name):
                    bundles.append(item.name)
            
            self.logger.info(f"Found {len(bundles)} evidence bundles")
            return sorted(bundles)
            
        except Exception as e:
            self.logger.error(f"Failed to list bundles: {e}")
            return []
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """
        Generate summary report of all evidence bundles.
        
        Returns:
            Summary report with statistics
        """
        bundles = self.list_bundles()
        
        total_passed = 0
        total_tests = 0
        coverage_sum = 0.0
        
        bundle_details = []
        
        for ac_id in bundles:
            bundle = self.load_bundle(ac_id)
            if bundle:
                if bundle.metadata.tests_passed:
                    total_passed += 1
                total_tests += bundle.metadata.test_count
                coverage_sum += bundle.metadata.coverage_percent
                
                bundle_details.append({
                    'ac_id': ac_id,
                    'feature_name': bundle.metadata.feature_name,
                    'tests_passed': bundle.metadata.tests_passed,
                    'test_count': bundle.metadata.test_count,
                    'coverage_percent': bundle.metadata.coverage_percent,
                    'created_at': bundle.metadata.created_at
                })
        
        return {
            'total_bundles': len(bundles),
            'passed_count': total_passed,
            'total_tests': total_tests,
            'average_coverage': coverage_sum / len(bundles) if bundles else 0.0,
            'bundles': bundle_details,
            'generated_at': datetime.now().isoformat() + "Z"
        }
