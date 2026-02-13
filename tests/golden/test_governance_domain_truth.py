"""
Governance + Domain Truth Test (WAVE-10 Track 1, Deliverable T1-D4)

Purpose:
    Verify governance violations are detected and domain rules apply correctly.
    Tests that governance enforcement and domain knowledge systems work together.
    
    Checks: CORE rule violations detected, domain precedence applied,
    audit trail captures governance decisions.

Authority:
    - WAVE-10 Track 1 Golden Path Tests
    - ENH-089+ phase delivery
    - Audit Truth Layer verification

AC-ID: AC-WAVE10-T1-D4-001
"""

import pytest
import sqlite3
import tempfile
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class GovernanceViolation:
    """Record of a governance violation."""
    rule_id: str
    violation_type: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    detected_at: str


@dataclass
class DomainRuleApplication:
    """Result of applying domain rules."""
    rule_id: str
    domain: str
    applied: bool
    precedence_level: int


@dataclass
class GovernanceDomainResult:
    """Result of governance + domain verification."""
    violations_detected: List[GovernanceViolation]
    domain_rules_applied: List[DomainRuleApplication]
    total_violations: int
    total_domain_rules: int
    enforcement_successful: bool


class MockGovernanceEngine:
    """Mock governance enforcement engine."""
    
    CORE_RULES = [
        ("CORE-008", "TDD_MANDATORY", "CRITICAL"),
        ("CORE-011", "TYPE_HINTS_REQUIRED", "HIGH"),
        ("CORE-012", "DOCSTRINGS_REQUIRED", "HIGH"),
        ("CORE-027", "AUDIT_TRAIL_REQUIRED", "CRITICAL"),
        ("CORE-035", "SINGLE_CANONICAL", "HIGH"),
    ]
    
    def __init__(self, audit_db_path: str):
        """Initialize with audit database path."""
        self.audit_db_path = audit_db_path
    
    def detect_violations(self, code_repository: Dict[str, Any]) -> List[GovernanceViolation]:
        """Detect governance violations in repository."""
        violations = []
        timestamp = datetime.now().isoformat()
        
        # Simulate violation detection
        if not code_repository.get("has_tests"):
            violation = GovernanceViolation(
                rule_id="CORE-008",
                violation_type="TDD_MANDATORY",
                severity="CRITICAL",
                detected_at=timestamp
            )
            violations.append(violation)
            self._log_audit("violation_detected", "CORE-008", {
                "violation_type": "TDD_MANDATORY",
                "severity": "CRITICAL",
                "timestamp": timestamp
            })
        
        if not code_repository.get("has_type_hints"):
            violation = GovernanceViolation(
                rule_id="CORE-011",
                violation_type="TYPE_HINTS_REQUIRED",
                severity="HIGH",
                detected_at=timestamp
            )
            violations.append(violation)
            self._log_audit("violation_detected", "CORE-011", {
                "violation_type": "TYPE_HINTS_REQUIRED",
                "severity": "HIGH",
                "timestamp": timestamp
            })
        
        if not code_repository.get("has_docstrings"):
            violation = GovernanceViolation(
                rule_id="CORE-012",
                violation_type="DOCSTRINGS_REQUIRED",
                severity="HIGH",
                detected_at=timestamp
            )
            violations.append(violation)
            self._log_audit("violation_detected", "CORE-012", {
                "violation_type": "DOCSTRINGS_REQUIRED",
                "severity": "HIGH",
                "timestamp": timestamp
            })
        
        if not code_repository.get("has_audit_trail"):
            violation = GovernanceViolation(
                rule_id="CORE-027",
                violation_type="AUDIT_TRAIL_REQUIRED",
                severity="CRITICAL",
                detected_at=timestamp
            )
            violations.append(violation)
            self._log_audit("violation_detected", "CORE-027", {
                "violation_type": "AUDIT_TRAIL_REQUIRED",
                "severity": "CRITICAL",
                "timestamp": timestamp
            })
        
        return violations
    
    def apply_domain_rules(self, domain: str) -> List[DomainRuleApplication]:
        """Apply domain-specific rules."""
        applications = []
        timestamp = datetime.now().isoformat()
        
        domain_rules = {
            "cortex": [
                {"rule": "ARCH-001", "precedence": 10},
                {"rule": "ARCH-002", "precedence": 9},
                {"rule": "ARCH-003", "precedence": 8},
            ],
            "company": [
                {"rule": "COMPANY-RULE-1", "precedence": 5},
                {"rule": "COMPANY-RULE-2", "precedence": 4},
            ]
        }
        
        if domain in domain_rules:
            for rule in domain_rules[domain]:
                application = DomainRuleApplication(
                    rule_id=rule["rule"],
                    domain=domain,
                    applied=True,
                    precedence_level=rule["precedence"]
                )
                applications.append(application)
                self._log_audit("domain_rule_applied", rule["rule"], {
                    "domain": domain,
                    "precedence": rule["precedence"],
                    "timestamp": timestamp
                })
        
        return applications
    
    def _log_audit(self, operation: str, rule_id: str, metadata: Dict):
        """Log operation to audit database."""
        conn = sqlite3.connect(self.audit_db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        metadata_json = json.dumps(metadata)
        
        cursor.execute("""
            INSERT INTO audit (timestamp, operation, rule_id, source, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (timestamp, operation, rule_id, "governance", metadata_json))
        
        conn.commit()
        conn.close()


class TestGovernanceTruth:
    """Governance Enforcement Truth Test with Audit Verification."""
    
    @pytest.fixture
    def audit_db_path(self):
        """Create temporary audit database for test."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        # Initialize schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                operation TEXT NOT NULL,
                rule_id TEXT,
                source TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
        
        yield db_path
        Path(db_path).unlink()
    
    @pytest.fixture
    def engine(self, audit_db_path):
        """Initialize governance engine with test audit database."""
        return MockGovernanceEngine(audit_db_path=audit_db_path)
    
    def test_governance_violations_detected(self, engine, audit_db_path):
        """
        RED PHASE: Test must fail if:
        1. violations not detected when violations exist
        2. audit log doesn't record violation_detected operations
        3. violation metadata missing required fields
        
        GREEN PHASE: Test passes when:
        1. all violations detected
        2. audit trail complete
        3. severity levels correct
        """
        # Setup: Repository with violations
        non_compliant_repo = {
            "has_tests": False,
            "has_type_hints": False,
            "has_docstrings": True,
            "has_audit_trail": False,
        }
        
        # Execute
        violations = engine.detect_violations(non_compliant_repo)
        
        # Assert: Violations detected
        assert len(violations) == 3, "Should detect 3 violations"
        
        # Assert: Specific violations
        violation_rules = [v.rule_id for v in violations]
        assert "CORE-008" in violation_rules  # TDD missing
        assert "CORE-011" in violation_rules  # Type hints missing
        assert "CORE-027" in violation_rules  # Audit trail missing
        
        # Audit Verification
        conn = sqlite3.connect(audit_db_path)
        cursor = conn.cursor()
        
        # Query violation detections
        cursor.execute(
            "SELECT COUNT(*) FROM audit WHERE operation = 'violation_detected'"
        )
        violation_count = cursor.fetchone()[0]
        
        # RED phase
        assert violation_count == 3, f"Expected 3 violation detections, got {violation_count}"
        
        # Query violation metadata
        cursor.execute(
            "SELECT metadata FROM audit WHERE operation = 'violation_detected' AND rule_id = 'CORE-008'"
        )
        metadata = cursor.fetchone()
        
        # RED phase
        assert metadata is not None, "CORE-008 violation metadata should exist"
        data = json.loads(metadata[0])
        assert data["violation_type"] == "TDD_MANDATORY"
        assert data["severity"] == "CRITICAL"
        
        conn.close()
    
    def test_compliant_repository_no_violations(self, engine, audit_db_path):
        """Verify compliant repository produces no violations."""
        # Setup: Compliant repository
        compliant_repo = {
            "has_tests": True,
            "has_type_hints": True,
            "has_docstrings": True,
            "has_audit_trail": True,
        }
        
        # Execute
        violations = engine.detect_violations(compliant_repo)
        
        # Assert
        assert len(violations) == 0, "Compliant repository should have no violations"
        
        # Audit check: No violations recorded
        conn = sqlite3.connect(audit_db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) FROM audit WHERE operation = 'violation_detected'"
        )
        violation_count = cursor.fetchone()[0]
        
        assert violation_count == 0, "No violation audit entries should exist"
        
        conn.close()


class TestDomainRulesTruth:
    """Domain Rules Application Truth Test."""
    
    @pytest.fixture
    def audit_db_path(self):
        """Create temporary audit database for test."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        # Initialize schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                operation TEXT NOT NULL,
                rule_id TEXT,
                source TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
        
        yield db_path
        Path(db_path).unlink()
    
    def test_cortex_domain_rules_applied(self, audit_db_path):
        """Verify CORTEX domain rules applied correctly."""
        engine = MockGovernanceEngine(audit_db_path)
        
        # Execute
        applications = engine.apply_domain_rules("cortex")
        
        # Assert: All 3 CORTEX domain rules applied
        assert len(applications) == 3, "Should apply 3 CORTEX domain rules"
        
        # Assert: Precedence levels correct
        applications_sorted = sorted(applications, key=lambda a: a.precedence_level, reverse=True)
        assert applications_sorted[0].precedence_level == 10
        assert applications_sorted[1].precedence_level == 9
        assert applications_sorted[2].precedence_level == 8
        
        # Audit Verification
        conn = sqlite3.connect(audit_db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) FROM audit WHERE operation = 'domain_rule_applied'"
        )
        count = cursor.fetchone()[0]
        
        assert count == 3, "Audit should record 3 domain rule applications"
        
        conn.close()
    
    def test_company_domain_rules_applied(self, audit_db_path):
        """Verify company domain rules applied correctly."""
        engine = MockGovernanceEngine(audit_db_path)
        
        # Execute
        applications = engine.apply_domain_rules("company")
        
        # Assert: All 2 company domain rules applied
        assert len(applications) == 2, "Should apply 2 company domain rules"
        
        # Assert: Applied successfully
        for app in applications:
            assert app.applied is True
            assert app.domain == "company"
        
        # Audit Verification
        conn = sqlite3.connect(audit_db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) FROM audit WHERE operation = 'domain_rule_applied' "
            "AND source = 'governance'"
        )
        count = cursor.fetchone()[0]
        
        assert count == 2, "Audit should record 2 company domain rule applications"
        
        conn.close()
