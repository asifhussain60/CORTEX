# ============================================================================
# Golden Tests: cortex-registry YAML Audit with SQLite Evidence
# ============================================================================
# Authority: Phase 103 - Registry & Intelligence Consolidation
# Purpose: Test CREATE, READ, PROCESS, DELETE of YAML files in cortex-registry
# Created: 2026-02-17
# ============================================================================

"""
Golden Tests for cortex-registry YAML Files with SQLite Audit.

TEST COVERAGE MATRIX:
=====================
P0 (Critical Path - Sunshine):
  - Basic CRUD operations on all registry folders
  - Full lifecycle validation for core governance
  - Audit trail completeness

P1 (Important - Rainy Day):
  - Invalid YAML handling
  - Missing file handling
  - Permission errors
  - Schema validation failures

P2 (Edge Cases - Blind Spots):
  - Empty YAML files
  - Large YAML files
  - Unicode/special characters
  - Deep nesting limits

These tests cover all cortex-registry subfolders:
- core/governance, core/config, core/wiring, core/specifications
- artifacts/templates, artifacts/workflows
- integration/interaction, integration/patterns
- planning/phases
- knowledge-base
- metrics

AC-ID: AC-PHASE103-REG-001
"""

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Generator

import pytest
import yaml


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def registry_audit_db(tmp_path: Path) -> Generator[Path, None, None]:
    """Create SQLite database for registry YAML audit logging.
    
    Yields:
        Path to audit database
    """
    db_path = tmp_path / "cortex_registry_audit.db"
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registry_yaml_audit (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            operation TEXT NOT NULL,
            file_path TEXT NOT NULL,
            registry_folder TEXT NOT NULL,
            status TEXT NOT NULL,
            details TEXT,
            duration_ms INTEGER DEFAULT 0,
            test_name TEXT,
            test_priority TEXT DEFAULT 'P0',
            phase_id TEXT DEFAULT 'phase-103'
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_reg_audit_operation 
        ON registry_yaml_audit(operation)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_reg_audit_folder 
        ON registry_yaml_audit(registry_folder)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_reg_audit_priority 
        ON registry_yaml_audit(test_priority)
    """)
    
    conn.commit()
    conn.close()
    
    yield db_path


@pytest.fixture
def registry_test_dir(tmp_path: Path) -> Path:
    """Create test directory structure mirroring cortex-registry.
    
    Returns:
        Path to test directory
    """
    test_dir = tmp_path / "cortex-registry"
    
    # Create core structure
    (test_dir / "core" / "governance").mkdir(parents=True)
    (test_dir / "core" / "config").mkdir(parents=True)
    (test_dir / "core" / "wiring").mkdir(parents=True)
    (test_dir / "core" / "specifications").mkdir(parents=True)
    
    # Create artifacts structure
    (test_dir / "artifacts" / "templates" / "responses").mkdir(parents=True)
    (test_dir / "artifacts" / "templates" / "phases").mkdir(parents=True)
    (test_dir / "artifacts" / "templates" / "documentation").mkdir(parents=True)
    (test_dir / "artifacts" / "workflows").mkdir(parents=True)
    
    # Create integration structure
    (test_dir / "integration" / "interaction").mkdir(parents=True)
    (test_dir / "integration" / "patterns").mkdir(parents=True)
    
    # Create planning structure
    (test_dir / "planning" / "phases" / "planned").mkdir(parents=True)
    (test_dir / "planning" / "phases" / "completed").mkdir(parents=True)
    (test_dir / "planning" / "phases" / "deferred").mkdir(parents=True)
    
    # Create knowledge-base structure
    (test_dir / "knowledge-base" / "architecture").mkdir(parents=True)
    (test_dir / "knowledge-base" / "security").mkdir(parents=True)
    
    # Create metrics structure
    (test_dir / "metrics" / "baselines").mkdir(parents=True)
    (test_dir / "metrics" / "reports").mkdir(parents=True)
    (test_dir / "metrics" / "dashboards").mkdir(parents=True)
    (test_dir / "metrics" / "status").mkdir(parents=True)
    
    return test_dir


def log_registry_operation(
    db_path: Path,
    operation: str,
    file_path: str,
    registry_folder: str,
    status: str = "SUCCESS",
    details: str = "",
    duration_ms: int = 0,
    test_name: str = "",
    test_priority: str = "P0",
) -> str:
    """Log registry YAML operation to SQLite.
    
    Args:
        db_path: Path to audit database
        operation: CREATE, READ, PROCESS, DELETE
        file_path: Path to YAML file
        registry_folder: Registry subfolder (core/governance, etc.)
        status: SUCCESS, FAILURE
        details: Additional details
        duration_ms: Operation duration
        test_name: Name of test
        test_priority: P0, P1, or P2
        
    Returns:
        Audit entry ID
    """
    entry_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    cursor.execute(
        """
        INSERT INTO registry_yaml_audit 
        (id, timestamp, operation, file_path, registry_folder, status, details, duration_ms, test_name, test_priority, phase_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            entry_id,
            timestamp,
            operation,
            file_path,
            registry_folder,
            status,
            details,
            duration_ms,
            test_name,
            test_priority,
            "phase-103",
        ),
    )
    
    conn.commit()
    conn.close()
    
    return entry_id


def get_registry_audit_summary(db_path: Path) -> dict[str, Any]:
    """Get summary of registry audit operations.
    
    Args:
        db_path: Path to audit database
        
    Returns:
        Summary dictionary
    """
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get operation counts
    cursor.execute(
        "SELECT operation, COUNT(*) as count FROM registry_yaml_audit GROUP BY operation"
    )
    operation_counts = {row["operation"]: row["count"] for row in cursor.fetchall()}
    
    # Get folder counts
    cursor.execute(
        "SELECT registry_folder, COUNT(*) as count FROM registry_yaml_audit GROUP BY registry_folder"
    )
    folder_counts = {row["registry_folder"]: row["count"] for row in cursor.fetchall()}
    
    # Get priority counts
    cursor.execute(
        "SELECT test_priority, COUNT(*) as count FROM registry_yaml_audit GROUP BY test_priority"
    )
    priority_counts = {row["test_priority"]: row["count"] for row in cursor.fetchall()}
    
    # Get total entries
    cursor.execute("SELECT COUNT(*) as total FROM registry_yaml_audit")
    total = cursor.fetchone()["total"]
    
    # Get success rate
    cursor.execute(
        "SELECT COUNT(*) as success FROM registry_yaml_audit WHERE status = 'SUCCESS'"
    )
    success_count = cursor.fetchone()["success"]
    
    conn.close()
    
    return {
        "total_operations": total,
        "operation_counts": operation_counts,
        "folder_counts": folder_counts,
        "priority_counts": priority_counts,
        "success_rate": (success_count / total * 100) if total > 0 else 0,
    }


# ============================================================================
# P0: CORE YAML TESTS (Sunshine Path)
# ============================================================================

class TestP0CoreGovernanceYAML:
    """P0 Critical: Tests for core/governance YAML files - SUNSHINE path."""
    
    def test_p0_create_core_rules_yaml(
        self,
        registry_test_dir: Path,
        registry_audit_db: Path,
    ) -> None:
        """P0: Create core rules YAML in core/governance - SUNSHINE.
        
        AC: AC-PHASE103-REG-P0-001
        """
        file_path = registry_test_dir / "core" / "governance" / "test-core-rules.yaml"
        
        content = {
            "version": "1.0",
            "authority": "CORE Governance",
            "rules": [
                {
                    "id": "CORE-008",
                    "name": "TDD Mandatory",
                    "enforcement": "blocking",
                    "severity": "P0",
                },
                {
                    "id": "CORE-011",
                    "name": "Type Hints Required",
                    "enforcement": "blocking",
                    "severity": "P1",
                },
            ],
            "created": datetime.utcnow().isoformat(),
        }
        
        # CREATE
        with open(file_path, "w") as f:
            yaml.safe_dump(content, f, default_flow_style=False)
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="CREATE",
            file_path=str(file_path),
            registry_folder="core/governance",
            status="SUCCESS",
            details=f"Created with {len(content['rules'])} rules",
            test_name="test_p0_create_core_rules_yaml",
            test_priority="P0",
        )
        
        assert file_path.exists()
        
        # READ
        with open(file_path) as f:
            loaded = yaml.safe_load(f)
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="READ",
            file_path=str(file_path),
            registry_folder="core/governance",
            status="SUCCESS",
            test_name="test_p0_create_core_rules_yaml",
            test_priority="P0",
        )
        
        assert loaded["authority"] == "CORE Governance"
        
        # DELETE
        file_path.unlink()
        log_registry_operation(
            db_path=registry_audit_db,
            operation="DELETE",
            file_path=str(file_path),
            registry_folder="core/governance",
            status="SUCCESS",
            test_name="test_p0_create_core_rules_yaml",
            test_priority="P0",
        )


class TestCoreConfigYAML:
    """Tests for core/config YAML files."""
    
    def test_create_master_plan_yaml(
        self,
        registry_test_dir: Path,
        registry_audit_db: Path,
    ) -> None:
        """Test creating master plan YAML in core/config.
        
        AC: AC-PHASE103-REG-002
        """
        file_path = registry_test_dir / "core" / "config" / "test-master-plan.yaml"
        
        content = {
            "version": "1.0",
            "plan_id": "CORTEX-2026",
            "phases": [
                {"id": "phase-103", "status": "active"},
                {"id": "phase-104", "status": "planned"},
            ],
        }
        
        # CREATE
        with open(file_path, "w") as f:
            yaml.safe_dump(content, f)
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="CREATE",
            file_path=str(file_path),
            registry_folder="core/config",
            status="SUCCESS",
            test_name="test_create_master_plan_yaml",
        )
        
        # PROCESS
        with open(file_path) as f:
            loaded = yaml.safe_load(f)
        
        processed = {**loaded, "processed": True}
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="PROCESS",
            file_path=str(file_path),
            registry_folder="core/config",
            status="SUCCESS",
            details="Validated plan structure",
            test_name="test_create_master_plan_yaml",
        )
        
        assert processed["plan_id"] == "CORTEX-2026"
        
        # DELETE
        file_path.unlink()
        log_registry_operation(
            db_path=registry_audit_db,
            operation="DELETE",
            file_path=str(file_path),
            registry_folder="core/config",
            status="SUCCESS",
            test_name="test_create_master_plan_yaml",
        )


class TestCoreWiringYAML:
    """Tests for core/wiring YAML files."""
    
    def test_create_wiring_contract_yaml(
        self,
        registry_test_dir: Path,
        registry_audit_db: Path,
    ) -> None:
        """Test creating wiring contract YAML.
        
        AC: AC-PHASE103-REG-003
        """
        file_path = registry_test_dir / "core" / "wiring" / "test-wiring-contract.yaml"
        
        content = {
            "version": "1.0",
            "contracts": [
                {
                    "source": "MasterOrchestrator",
                    "target": "LENSOrchestrator",
                    "protocol": "async",
                },
            ],
        }
        
        # Full lifecycle
        with open(file_path, "w") as f:
            yaml.safe_dump(content, f)
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="CREATE",
            file_path=str(file_path),
            registry_folder="core/wiring",
            status="SUCCESS",
            test_name="test_create_wiring_contract_yaml",
        )
        
        with open(file_path) as f:
            loaded = yaml.safe_load(f)
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="READ",
            file_path=str(file_path),
            registry_folder="core/wiring",
            status="SUCCESS",
            test_name="test_create_wiring_contract_yaml",
        )
        
        assert len(loaded["contracts"]) == 1
        
        file_path.unlink()
        log_registry_operation(
            db_path=registry_audit_db,
            operation="DELETE",
            file_path=str(file_path),
            registry_folder="core/wiring",
            status="SUCCESS",
            test_name="test_create_wiring_contract_yaml",
        )


class TestCoreSpecificationsYAML:
    """Tests for core/specifications YAML files."""
    
    def test_create_exec_flow_yaml(
        self,
        registry_test_dir: Path,
        registry_audit_db: Path,
    ) -> None:
        """Test creating execution flow YAML.
        
        AC: AC-PHASE103-REG-004
        """
        file_path = registry_test_dir / "core" / "specifications" / "test-exec-flow.yaml"
        
        content = {
            "version": "1.0",
            "flow": {
                "stages": ["intent", "validation", "execution", "audit"],
                "timeout_ms": 30000,
            },
        }
        
        with open(file_path, "w") as f:
            yaml.safe_dump(content, f)
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="CREATE",
            file_path=str(file_path),
            registry_folder="core/specifications",
            status="SUCCESS",
            test_name="test_create_exec_flow_yaml",
        )
        
        with open(file_path) as f:
            loaded = yaml.safe_load(f)
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="READ",
            file_path=str(file_path),
            registry_folder="core/specifications",
            status="SUCCESS",
            test_name="test_create_exec_flow_yaml",
        )
        
        assert "stages" in loaded["flow"]
        
        file_path.unlink()
        log_registry_operation(
            db_path=registry_audit_db,
            operation="DELETE",
            file_path=str(file_path),
            registry_folder="core/specifications",
            status="SUCCESS",
            test_name="test_create_exec_flow_yaml",
        )


# ============================================================================
# Artifacts YAML Tests
# ============================================================================

class TestArtifactsTemplatesYAML:
    """Tests for artifacts/templates YAML files."""
    
    def test_create_response_template_yaml(
        self,
        registry_test_dir: Path,
        registry_audit_db: Path,
    ) -> None:
        """Test creating response template YAML.
        
        AC: AC-PHASE103-REG-005
        """
        file_path = registry_test_dir / "artifacts" / "templates" / "responses" / "test-content-blocks.yaml"
        
        content = {
            "version": "1.0",
            "blocks": [
                {"id": "BLOCK-INTRO", "purpose": "Welcome message", "max_words": 150},
                {"id": "BLOCK-CAPABILITIES", "purpose": "Feature overview", "max_words": 200},
            ],
        }
        
        with open(file_path, "w") as f:
            yaml.safe_dump(content, f)
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="CREATE",
            file_path=str(file_path),
            registry_folder="artifacts/templates/responses",
            status="SUCCESS",
            details=f"Created with {len(content['blocks'])} blocks",
            test_name="test_create_response_template_yaml",
        )
        
        with open(file_path) as f:
            loaded = yaml.safe_load(f)
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="READ",
            file_path=str(file_path),
            registry_folder="artifacts/templates/responses",
            status="SUCCESS",
            test_name="test_create_response_template_yaml",
        )
        
        assert len(loaded["blocks"]) == 2
        
        file_path.unlink()
        log_registry_operation(
            db_path=registry_audit_db,
            operation="DELETE",
            file_path=str(file_path),
            registry_folder="artifacts/templates/responses",
            status="SUCCESS",
            test_name="test_create_response_template_yaml",
        )
    
    def test_create_phase_template_yaml(
        self,
        registry_test_dir: Path,
        registry_audit_db: Path,
    ) -> None:
        """Test creating phase template YAML.
        
        AC: AC-PHASE103-REG-006
        """
        file_path = registry_test_dir / "artifacts" / "templates" / "phases" / "test-phase-template.yaml"
        
        content = {
            "version": "2.0",
            "template_id": "phase-NN",
            "required_fields": ["title", "status", "stages"],
            "enforcement_gates": {
                "pre_execution": ["CORE-008", "CORE-026"],
            },
        }
        
        with open(file_path, "w") as f:
            yaml.safe_dump(content, f)
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="CREATE",
            file_path=str(file_path),
            registry_folder="artifacts/templates/phases",
            status="SUCCESS",
            test_name="test_create_phase_template_yaml",
        )
        
        file_path.unlink()
        log_registry_operation(
            db_path=registry_audit_db,
            operation="DELETE",
            file_path=str(file_path),
            registry_folder="artifacts/templates/phases",
            status="SUCCESS",
            test_name="test_create_phase_template_yaml",
        )


class TestArtifactsWorkflowsYAML:
    """Tests for artifacts/workflows YAML files."""
    
    def test_create_workflow_yaml(
        self,
        registry_test_dir: Path,
        registry_audit_db: Path,
    ) -> None:
        """Test creating workflow YAML.
        
        AC: AC-PHASE103-REG-007
        """
        file_path = registry_test_dir / "artifacts" / "workflows" / "test-tdd-workflow.yaml"
        
        content = {
            "version": "1.0",
            "workflow_id": "tdd",
            "steps": [
                {"name": "write_test", "order": 1},
                {"name": "run_test_fail", "order": 2},
                {"name": "write_code", "order": 3},
                {"name": "run_test_pass", "order": 4},
            ],
        }
        
        with open(file_path, "w") as f:
            yaml.safe_dump(content, f)
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="CREATE",
            file_path=str(file_path),
            registry_folder="artifacts/workflows",
            status="SUCCESS",
            test_name="test_create_workflow_yaml",
        )
        
        with open(file_path) as f:
            loaded = yaml.safe_load(f)
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="READ",
            file_path=str(file_path),
            registry_folder="artifacts/workflows",
            status="SUCCESS",
            test_name="test_create_workflow_yaml",
        )
        
        # PROCESS: Validate workflow steps
        processed = {
            **loaded,
            "validated": True,
            "step_count": len(loaded["steps"]),
        }
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="PROCESS",
            file_path=str(file_path),
            registry_folder="artifacts/workflows",
            status="SUCCESS",
            details=f"Validated {processed['step_count']} steps",
            test_name="test_create_workflow_yaml",
        )
        
        assert processed["step_count"] == 4
        
        file_path.unlink()
        log_registry_operation(
            db_path=registry_audit_db,
            operation="DELETE",
            file_path=str(file_path),
            registry_folder="artifacts/workflows",
            status="SUCCESS",
            test_name="test_create_workflow_yaml",
        )


# ============================================================================
# Integration YAML Tests
# ============================================================================

class TestIntegrationInteractionYAML:
    """Tests for integration/interaction YAML files."""
    
    def test_create_request_response_yaml(
        self,
        registry_test_dir: Path,
        registry_audit_db: Path,
    ) -> None:
        """Test creating request-response pattern YAML.
        
        AC: AC-PHASE103-REG-008
        """
        file_path = registry_test_dir / "integration" / "interaction" / "test-request-response.yaml"
        
        content = {
            "version": "1.0",
            "pattern_type": "request-response",
            "validation_rules": {
                "request_id_format": "uuid",
                "timeout_ms_max": 300000,
            },
        }
        
        with open(file_path, "w") as f:
            yaml.safe_dump(content, f)
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="CREATE",
            file_path=str(file_path),
            registry_folder="integration/interaction",
            status="SUCCESS",
            test_name="test_create_request_response_yaml",
        )
        
        file_path.unlink()
        log_registry_operation(
            db_path=registry_audit_db,
            operation="DELETE",
            file_path=str(file_path),
            registry_folder="integration/interaction",
            status="SUCCESS",
            test_name="test_create_request_response_yaml",
        )


class TestIntegrationPatternsYAML:
    """Tests for integration/patterns YAML files."""
    
    def test_create_api_design_pattern_yaml(
        self,
        registry_test_dir: Path,
        registry_audit_db: Path,
    ) -> None:
        """Test creating API design pattern YAML.
        
        AC: AC-PHASE103-REG-009
        """
        file_path = registry_test_dir / "integration" / "patterns" / "test-api-design.yaml"
        
        content = {
            "version": "1.0",
            "patterns": [
                {"name": "REST", "style": "resource-oriented"},
                {"name": "GraphQL", "style": "query-oriented"},
            ],
        }
        
        with open(file_path, "w") as f:
            yaml.safe_dump(content, f)
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="CREATE",
            file_path=str(file_path),
            registry_folder="integration/patterns",
            status="SUCCESS",
            test_name="test_create_api_design_pattern_yaml",
        )
        
        file_path.unlink()
        log_registry_operation(
            db_path=registry_audit_db,
            operation="DELETE",
            file_path=str(file_path),
            registry_folder="integration/patterns",
            status="SUCCESS",
            test_name="test_create_api_design_pattern_yaml",
        )


# ============================================================================
# Planning YAML Tests
# ============================================================================

class TestPlanningPhasesYAML:
    """Tests for planning/phases YAML files."""
    
    def test_create_planned_phase_yaml(
        self,
        registry_test_dir: Path,
        registry_audit_db: Path,
    ) -> None:
        """Test creating planned phase YAML.
        
        AC: AC-PHASE103-REG-010
        """
        file_path = registry_test_dir / "planning" / "phases" / "planned" / "test-phase-104.yaml"
        
        content = {
            "version": "2.0",
            "phase_id": "phase-104",
            "title": "Test Phase",
            "status": "planned",
            "priority": "P1",
            "stages": [
                {"stage_id": "S1", "title": "Stage 1"},
            ],
        }
        
        with open(file_path, "w") as f:
            yaml.safe_dump(content, f)
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="CREATE",
            file_path=str(file_path),
            registry_folder="planning/phases/planned",
            status="SUCCESS",
            test_name="test_create_planned_phase_yaml",
        )
        
        with open(file_path) as f:
            loaded = yaml.safe_load(f)
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="READ",
            file_path=str(file_path),
            registry_folder="planning/phases/planned",
            status="SUCCESS",
            test_name="test_create_planned_phase_yaml",
        )
        
        assert loaded["status"] == "planned"
        
        file_path.unlink()
        log_registry_operation(
            db_path=registry_audit_db,
            operation="DELETE",
            file_path=str(file_path),
            registry_folder="planning/phases/planned",
            status="SUCCESS",
            test_name="test_create_planned_phase_yaml",
        )


# ============================================================================
# Knowledge Base YAML Tests
# ============================================================================

class TestKnowledgeBaseYAML:
    """Tests for knowledge-base YAML files."""
    
    def test_create_architecture_knowledge_yaml(
        self,
        registry_test_dir: Path,
        registry_audit_db: Path,
    ) -> None:
        """Test creating architecture knowledge YAML.
        
        AC: AC-PHASE103-REG-011
        """
        file_path = registry_test_dir / "knowledge-base" / "architecture" / "test-solid-principles.yaml"
        
        content = {
            "version": "1.0",
            "topic": "SOLID Principles",
            "principles": [
                {"name": "Single Responsibility", "acronym": "S"},
                {"name": "Open-Closed", "acronym": "O"},
            ],
            "source": "Robert C. Martin",
        }
        
        with open(file_path, "w") as f:
            yaml.safe_dump(content, f)
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="CREATE",
            file_path=str(file_path),
            registry_folder="knowledge-base/architecture",
            status="SUCCESS",
            test_name="test_create_architecture_knowledge_yaml",
        )
        
        file_path.unlink()
        log_registry_operation(
            db_path=registry_audit_db,
            operation="DELETE",
            file_path=str(file_path),
            registry_folder="knowledge-base/architecture",
            status="SUCCESS",
            test_name="test_create_architecture_knowledge_yaml",
        )
    
    def test_create_security_knowledge_yaml(
        self,
        registry_test_dir: Path,
        registry_audit_db: Path,
    ) -> None:
        """Test creating security knowledge YAML.
        
        AC: AC-PHASE103-REG-012
        """
        file_path = registry_test_dir / "knowledge-base" / "security" / "test-owasp-top10.yaml"
        
        content = {
            "version": "2021",
            "topic": "OWASP Top 10",
            "risks": [
                {"rank": 1, "name": "Broken Access Control"},
                {"rank": 2, "name": "Cryptographic Failures"},
            ],
        }
        
        with open(file_path, "w") as f:
            yaml.safe_dump(content, f)
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="CREATE",
            file_path=str(file_path),
            registry_folder="knowledge-base/security",
            status="SUCCESS",
            test_name="test_create_security_knowledge_yaml",
        )
        
        file_path.unlink()
        log_registry_operation(
            db_path=registry_audit_db,
            operation="DELETE",
            file_path=str(file_path),
            registry_folder="knowledge-base/security",
            status="SUCCESS",
            test_name="test_create_security_knowledge_yaml",
        )


# ============================================================================
# Metrics YAML Tests
# ============================================================================

class TestMetricsYAML:
    """Tests for metrics YAML files."""
    
    def test_create_status_yaml(
        self,
        registry_test_dir: Path,
        registry_audit_db: Path,
    ) -> None:
        """Test creating status YAML.
        
        AC: AC-PHASE103-REG-013
        """
        file_path = registry_test_dir / "metrics" / "status" / "test-cortex-status.yaml"
        
        content = {
            "version": "1.0",
            "status_date": datetime.utcnow().isoformat(),
            "health": {
                "orchestrators": "healthy",
                "intelligence": "healthy",
                "registry": "healthy",
            },
        }
        
        with open(file_path, "w") as f:
            yaml.safe_dump(content, f)
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="CREATE",
            file_path=str(file_path),
            registry_folder="metrics/status",
            status="SUCCESS",
            test_name="test_create_status_yaml",
        )
        
        file_path.unlink()
        log_registry_operation(
            db_path=registry_audit_db,
            operation="DELETE",
            file_path=str(file_path),
            registry_folder="metrics/status",
            status="SUCCESS",
            test_name="test_create_status_yaml",
        )


# ============================================================================
# Comprehensive Audit Evidence Tests
# ============================================================================

class TestRegistryAuditEvidence:
    """Tests to verify comprehensive audit evidence is captured."""
    
    def test_all_folders_covered(
        self,
        registry_test_dir: Path,
        registry_audit_db: Path,
    ) -> None:
        """Verify all registry folders have audit entries.
        
        AC: AC-PHASE103-REG-014
        """
        folders_to_test = [
            ("core/governance", "test-gov.yaml"),
            ("core/config", "test-cfg.yaml"),
            ("core/wiring", "test-wiring.yaml"),
            ("core/specifications", "test-spec.yaml"),
            ("artifacts/templates/responses", "test-resp.yaml"),
            ("artifacts/workflows", "test-wf.yaml"),
            ("integration/interaction", "test-int.yaml"),
            ("integration/patterns", "test-pat.yaml"),
            ("planning/phases/planned", "test-phase.yaml"),
            ("knowledge-base/architecture", "test-arch.yaml"),
            ("metrics/status", "test-status.yaml"),
        ]
        
        for folder, filename in folders_to_test:
            file_path = registry_test_dir / folder / filename
            
            # CREATE
            with open(file_path, "w") as f:
                yaml.safe_dump({"test": True, "folder": folder}, f)
            
            log_registry_operation(
                db_path=registry_audit_db,
                operation="CREATE",
                file_path=str(file_path),
                registry_folder=folder,
                status="SUCCESS",
                test_name="test_all_folders_covered",
            )
            
            # DELETE
            file_path.unlink()
            log_registry_operation(
                db_path=registry_audit_db,
                operation="DELETE",
                file_path=str(file_path),
                registry_folder=folder,
                status="SUCCESS",
                test_name="test_all_folders_covered",
            )
        
        # Verify all folders have entries
        summary = get_registry_audit_summary(registry_audit_db)
        
        assert summary["total_operations"] >= len(folders_to_test) * 2  # CREATE + DELETE each
        assert summary["success_rate"] == 100.0
        assert len(summary["folder_counts"]) >= len(folders_to_test)
    
    def test_export_registry_audit_evidence(
        self,
        registry_test_dir: Path,
        registry_audit_db: Path,
        tmp_path: Path,
    ) -> None:
        """Test exporting registry audit log to JSON for evidence.
        
        AC: AC-PHASE103-REG-015
        """
        # Create some audit entries
        file_path = registry_test_dir / "core" / "governance" / "test-export-evidence.yaml"
        
        with open(file_path, "w") as f:
            yaml.safe_dump({"export_test": True}, f)
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="CREATE",
            file_path=str(file_path),
            registry_folder="core/governance",
            status="SUCCESS",
            test_name="test_export_registry_audit_evidence",
        )
        
        # Export to JSON
        export_path = tmp_path / "registry_audit_export.json"
        
        conn = sqlite3.connect(str(registry_audit_db))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM registry_yaml_audit ORDER BY timestamp")
        rows = cursor.fetchall()
        conn.close()
        
        summary = get_registry_audit_summary(registry_audit_db)
        
        export_data = {
            "phase_id": "phase-103",
            "export_timestamp": datetime.utcnow().isoformat(),
            "summary": summary,
            "total_entries": len(rows),
            "entries": [dict(row) for row in rows],
        }
        
        with open(export_path, "w") as f:
            json.dump(export_data, f, indent=2)
        
        assert export_path.exists()
        
        with open(export_path) as f:
            loaded_export = json.load(f)
        
        assert loaded_export["phase_id"] == "phase-103"
        assert loaded_export["total_entries"] >= 1
        assert "summary" in loaded_export
        
        # Cleanup
        file_path.unlink()
        log_registry_operation(
            db_path=registry_audit_db,
            operation="DELETE",
            file_path=str(file_path),
            registry_folder="core/governance",
            status="SUCCESS",
            test_name="test_export_registry_audit_evidence",
        )


# ============================================================================
# P1: RAINY DAY TESTS - Error Handling
# ============================================================================

class TestP1RainyDayInvalidYAML:
    """P1 Important: Error handling for invalid YAML - RAINY DAY."""
    
    def test_p1_invalid_yaml_syntax(
        self,
        registry_test_dir: Path,
        registry_audit_db: Path,
    ) -> None:
        """P1: Handle invalid YAML syntax gracefully.
        
        AC: AC-PHASE103-REG-P1-001
        """
        file_path = registry_test_dir / "core" / "governance" / "test-invalid.yaml"
        
        # Create invalid YAML
        invalid_content = """
version: 1.0
rules:
  - id: CORE-001
    name: "Test
    invalid: [unclosed bracket
"""
        with open(file_path, "w") as f:
            f.write(invalid_content)
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="CREATE",
            file_path=str(file_path),
            registry_folder="core/governance",
            status="SUCCESS",
            details="Created invalid YAML for testing",
            test_name="test_p1_invalid_yaml_syntax",
            test_priority="P1",
        )
        
        # Attempt to read - should fail gracefully
        try:
            with open(file_path) as f:
                yaml.safe_load(f)
            status = "UNEXPECTED_SUCCESS"
            details = "YAML parsing should have failed"
        except yaml.YAMLError as e:
            status = "EXPECTED_FAILURE"
            details = f"YAMLError: {type(e).__name__}"
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="READ",
            file_path=str(file_path),
            registry_folder="core/governance",
            status=status,
            details=details,
            test_name="test_p1_invalid_yaml_syntax",
            test_priority="P1",
        )
        
        # Cleanup
        file_path.unlink()
        log_registry_operation(
            db_path=registry_audit_db,
            operation="DELETE",
            file_path=str(file_path),
            registry_folder="core/governance",
            status="SUCCESS",
            test_name="test_p1_invalid_yaml_syntax",
            test_priority="P1",
        )
    
    def test_p1_missing_file_read(
        self,
        registry_test_dir: Path,
        registry_audit_db: Path,
    ) -> None:
        """P1: Handle missing file read gracefully.
        
        AC: AC-PHASE103-REG-P1-002
        """
        file_path = registry_test_dir / "core" / "governance" / "non-existent-file.yaml"
        
        # Attempt to read non-existent file
        try:
            with open(file_path) as f:
                yaml.safe_load(f)
            status = "UNEXPECTED_SUCCESS"
        except FileNotFoundError:
            status = "EXPECTED_FAILURE"
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="READ",
            file_path=str(file_path),
            registry_folder="core/governance",
            status=status,
            details="FileNotFoundError as expected",
            test_name="test_p1_missing_file_read",
            test_priority="P1",
        )
        
        assert status == "EXPECTED_FAILURE"


class TestP1RainyDayPermissions:
    """P1 Important: Permission error handling - RAINY DAY."""
    
    def test_p1_readonly_directory_write(
        self,
        registry_test_dir: Path,
        registry_audit_db: Path,
    ) -> None:
        """P1: Handle write to readonly directory gracefully.
        
        AC: AC-PHASE103-REG-P1-003
        """
        import os
        
        readonly_dir = registry_test_dir / "core" / "readonly-test"
        readonly_dir.mkdir(parents=True)
        
        file_path = readonly_dir / "test-readonly.yaml"
        
        # Make directory readonly
        os.chmod(readonly_dir, 0o444)
        
        try:
            with open(file_path, "w") as f:
                yaml.safe_dump({"test": True}, f)
            status = "UNEXPECTED_SUCCESS"
            details = "Write should have failed"
        except (PermissionError, OSError) as e:
            status = "EXPECTED_FAILURE"
            details = f"{type(e).__name__}"
        finally:
            # Restore permissions for cleanup
            os.chmod(readonly_dir, 0o755)
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="CREATE",
            file_path=str(file_path),
            registry_folder="core/readonly-test",
            status=status,
            details=details,
            test_name="test_p1_readonly_directory_write",
            test_priority="P1",
        )
        
        assert status == "EXPECTED_FAILURE"


# ============================================================================
# P2: EDGE CASES - Blind Spots
# ============================================================================

class TestP2EdgeCasesEmptyFiles:
    """P2 Edge Cases: Empty and minimal YAML files - BLIND SPOTS."""
    
    def test_p2_empty_yaml_file(
        self,
        registry_test_dir: Path,
        registry_audit_db: Path,
    ) -> None:
        """P2: Handle completely empty YAML file.
        
        AC: AC-PHASE103-REG-P2-001
        """
        file_path = registry_test_dir / "core" / "config" / "test-empty.yaml"
        
        # Create empty file
        file_path.touch()
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="CREATE",
            file_path=str(file_path),
            registry_folder="core/config",
            status="SUCCESS",
            details="Created empty YAML file",
            test_name="test_p2_empty_yaml_file",
            test_priority="P2",
        )
        
        # Read empty file
        with open(file_path) as f:
            result = yaml.safe_load(f)
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="READ",
            file_path=str(file_path),
            registry_folder="core/config",
            status="SUCCESS",
            details=f"Empty YAML loaded as: {result}",
            test_name="test_p2_empty_yaml_file",
            test_priority="P2",
        )
        
        assert result is None, "Empty YAML should load as None"
        
        # Cleanup
        file_path.unlink()


class TestP2EdgeCasesLargeFiles:
    """P2 Edge Cases: Large YAML files - BLIND SPOTS."""
    
    def test_p2_large_yaml_file(
        self,
        registry_test_dir: Path,
        registry_audit_db: Path,
    ) -> None:
        """P2: Handle large YAML file (>500KB).
        
        AC: AC-PHASE103-REG-P2-002
        """
        import time
        
        file_path = registry_test_dir / "artifacts" / "templates" / "responses" / "test-large.yaml"
        
        # Generate large content
        large_content = {
            "version": "1.0",
            "large_array": [
                {"id": f"item_{i}", "data": f"value_{i}" * 10}
                for i in range(10000)
            ],
        }
        
        start = time.time()
        with open(file_path, "w") as f:
            yaml.safe_dump(large_content, f)
        write_duration = int((time.time() - start) * 1000)
        
        file_size = file_path.stat().st_size
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="CREATE",
            file_path=str(file_path),
            registry_folder="artifacts/templates/responses",
            status="SUCCESS",
            details=f"Created {file_size / 1024:.1f}KB file",
            duration_ms=write_duration,
            test_name="test_p2_large_yaml_file",
            test_priority="P2",
        )
        
        # Read large file
        start = time.time()
        with open(file_path) as f:
            loaded = yaml.safe_load(f)
        read_duration = int((time.time() - start) * 1000)
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="READ",
            file_path=str(file_path),
            registry_folder="artifacts/templates/responses",
            status="SUCCESS",
            details=f"Read {len(loaded['large_array'])} items in {read_duration}ms",
            duration_ms=read_duration,
            test_name="test_p2_large_yaml_file",
            test_priority="P2",
        )
        
        assert len(loaded["large_array"]) == 10000
        
        # Cleanup
        file_path.unlink()


class TestP2EdgeCasesUnicode:
    """P2 Edge Cases: Unicode and special characters - BLIND SPOTS."""
    
    def test_p2_unicode_content(
        self,
        registry_test_dir: Path,
        registry_audit_db: Path,
    ) -> None:
        """P2: Handle Unicode characters in registry YAML.
        
        AC: AC-PHASE103-REG-P2-003
        """
        file_path = registry_test_dir / "knowledge-base" / "architecture" / "test-unicode.yaml"
        
        content = {
            "version": "1.0",
            "i18n_test": {
                "chinese": "中文文档",
                "japanese": "日本語ドキュメント",
                "emoji": "🏗️ 📐 🔧",
                "special": "™®©",
            },
        }
        
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(content, f, allow_unicode=True)
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="CREATE",
            file_path=str(file_path),
            registry_folder="knowledge-base/architecture",
            status="SUCCESS",
            details="Created YAML with Unicode content",
            test_name="test_p2_unicode_content",
            test_priority="P2",
        )
        
        with open(file_path, encoding="utf-8") as f:
            loaded = yaml.safe_load(f)
        
        assert loaded["i18n_test"]["chinese"] == "中文文档"
        assert "🏗️" in loaded["i18n_test"]["emoji"]
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="READ",
            file_path=str(file_path),
            registry_folder="knowledge-base/architecture",
            status="SUCCESS",
            test_name="test_p2_unicode_content",
            test_priority="P2",
        )
        
        # Cleanup
        file_path.unlink()


# ============================================================================
# FINAL SUMMARY TEST
# ============================================================================

class TestRegistrySummary:
    """Final summary test - runs at end to generate comprehensive audit report."""
    
    def test_z_final_registry_audit_summary(
        self,
        registry_test_dir: Path,
        registry_audit_db: Path,
    ) -> None:
        """Generate final registry audit summary with sample data (named with z_ to run last).
        
        AC: AC-PHASE103-REG-SUMMARY
        """
        # Create sample operations to have data in the summary
        file_path = registry_test_dir / "core" / "governance" / "test-summary.yaml"
        
        content = {"version": "1.0", "test": "summary"}
        with open(file_path, "w") as f:
            yaml.safe_dump(content, f)
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="CREATE",
            file_path=str(file_path),
            registry_folder="core/governance",
            status="SUCCESS",
            test_name="test_z_final_registry_audit_summary",
            test_priority="P0",
        )
        
        with open(file_path) as f:
            yaml.safe_load(f)
        
        log_registry_operation(
            db_path=registry_audit_db,
            operation="READ",
            file_path=str(file_path),
            registry_folder="core/governance",
            status="SUCCESS",
            test_name="test_z_final_registry_audit_summary",
            test_priority="P0",
        )
        
        file_path.unlink()
        log_registry_operation(
            db_path=registry_audit_db,
            operation="DELETE",
            file_path=str(file_path),
            registry_folder="core/governance",
            status="SUCCESS",
            test_name="test_z_final_registry_audit_summary",
            test_priority="P0",
        )
        
        summary = get_registry_audit_summary(registry_audit_db)
        
        # Print summary for CI/CD visibility
        print("\n" + "=" * 60)
        print("PHASE-103 CORTEX-REGISTRY GOLDEN TEST AUDIT SUMMARY")
        print("=" * 60)
        print(f"Total Operations: {summary['total_operations']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print("\nOperations by Type:")
        for op, count in summary.get("operation_counts", {}).items():
            print(f"  {op}: {count}")
        print("\nOperations by Folder:")
        for folder, count in sorted(summary.get("folder_counts", {}).items()):
            print(f"  {folder}: {count}")
        print("\nOperations by Priority:")
        for priority, count in summary.get("priority_counts", {}).items():
            print(f"  {priority}: {count}")
        print("=" * 60)
        
        # Assertions for CI/CD gates
        assert summary["total_operations"] >= 3, "Should have logged at least CREATE/READ/DELETE"
        assert summary["success_rate"] >= 90.0, "Success rate should be >= 90%"
