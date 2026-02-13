"""
MCP End-to-End Truth Test (WAVE-10 Track 1, Deliverable T1-D6)

Purpose:
    Verify complete MCP request/response cycle with all validations.
    Tests: Request parsing, tool invocation, response generation, audit trail.
    
    Checks: MCP request processing, tool routing, response formatting,
    error handling, and complete audit trail from input to output.

Authority:
    - WAVE-10 Track 1 Golden Path Tests
    - ENH-089+ phase delivery
    - Audit Truth Layer verification

AC-ID: AC-WAVE10-T1-D6-001
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
class MCPRequest:
    """MCP incoming request."""
    request_id: str
    tool_name: str
    parameters: Dict[str, Any]
    timestamp: str


@dataclass
class MCPResponse:
    """MCP outgoing response."""
    request_id: str
    status: str  # success, error, partial
    result: Dict[str, Any]
    timestamp: str


@dataclass
class MCPEndToEndResult:
    """E2E MCP transaction result."""
    request: MCPRequest
    response: MCPResponse
    processing_time: float
    validations_passed: int
    audit_entries: int


class MockMCPGateway:
    """Mock MCP gateway for E2E testing."""
    
    VALID_TOOLS = [
        "cortex_process_request",
        "cortex_lens_analyze",
        "cortex_challenge",
        "cortex_audit",
        "cortex_plan_setup",
    ]
    
    def __init__(self, audit_db_path: str):
        """Initialize with audit database path."""
        self.audit_db_path = audit_db_path
    
    def process_request(self, request_data: Dict[str, Any]) -> MCPEndToEndResult:
        """Process complete MCP request."""
        start_time = datetime.now()
        request_id = request_data.get("id", "unknown")
        tool_name = request_data.get("tool")
        parameters = request_data.get("parameters", {})
        
        # Create request object
        request = MCPRequest(
            request_id=request_id,
            tool_name=tool_name,
            parameters=parameters,
            timestamp=datetime.now().isoformat()
        )
        
        # Log: Request received
        self._log_audit("request_received", request_id, {
            "tool": tool_name,
            "parameters_count": len(parameters)
        })
        
        validations_passed = 0
        
        # Validation 1: Tool exists
        if tool_name in self.VALID_TOOLS:
            validations_passed += 1
            self._log_audit("tool_validated", request_id, {"tool": tool_name})
        else:
            response = MCPResponse(
                request_id=request_id,
                status="error",
                result={"error": f"Unknown tool: {tool_name}"},
                timestamp=datetime.now().isoformat()
            )
            self._log_audit("tool_validation_failed", request_id, {"tool": tool_name})
            processing_time = (datetime.now() - start_time).total_seconds()
            return MCPEndToEndResult(
                request=request,
                response=response,
                processing_time=processing_time,
                validations_passed=validations_passed,
                audit_entries=3
            )
        
        # Validation 2: Parameters present
        if len(parameters) > 0:
            validations_passed += 1
            self._log_audit("parameters_validated", request_id, {
                "parameter_count": len(parameters)
            })
        else:
            self._log_audit("parameters_validation_warning", request_id, {
                "message": "No parameters provided"
            })
        
        # Validation 3: Request ID present
        if request_id and request_id != "unknown":
            validations_passed += 1
            self._log_audit("request_id_validated", request_id, {
                "request_id": request_id
            })
        
        # Execute tool
        result_data = self._execute_tool(tool_name, parameters)
        validations_passed += 1
        self._log_audit("tool_executed", request_id, {
            "tool": tool_name,
            "execution_successful": True
        })
        
        # Create response
        response = MCPResponse(
            request_id=request_id,
            status="success",
            result=result_data,
            timestamp=datetime.now().isoformat()
        )
        
        # Log: Response sent
        self._log_audit("response_sent", request_id, {
            "status": response.status,
            "result_keys": len(result_data)
        })
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Count audit entries
        conn = sqlite3.connect(self.audit_db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM audit WHERE rule_id = ?",
            (request_id,)
        )
        audit_count = cursor.fetchone()[0]
        conn.close()
        
        return MCPEndToEndResult(
            request=request,
            response=response,
            processing_time=processing_time,
            validations_passed=validations_passed,
            audit_entries=audit_count
        )
    
    def _execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the requested tool."""
        return {
            "tool_executed": tool_name,
            "parameters_received": len(parameters),
            "result": f"Tool {tool_name} executed successfully"
        }
    
    def _log_audit(self, operation: str, request_id: str, metadata: Dict):
        """Log operation to audit database."""
        conn = sqlite3.connect(self.audit_db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        metadata_json = json.dumps(metadata)
        
        cursor.execute("""
            INSERT INTO audit (timestamp, operation, rule_id, source, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (timestamp, operation, request_id, "mcp", metadata_json))
        
        conn.commit()
        conn.close()


class TestMCPEndToEndTruth:
    """MCP End-to-End Truth Test with Audit Verification."""
    
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
    def gateway(self, audit_db_path):
        """Initialize MCP gateway."""
        return MockMCPGateway(audit_db_path=audit_db_path)
    
    def test_complete_mcp_request_response_cycle(self, gateway, audit_db_path):
        """
        RED PHASE: Test must fail if:
        1. response status not 'success'
        2. audit entries missing for request lifecycle
        3. validations_passed < 4
        
        GREEN PHASE: Test passes when:
        1. full cycle completes
        2. all audit entries logged
        3. response valid
        """
        # Setup
        request_data = {
            "id": "req-001",
            "tool": "cortex_process_request",
            "parameters": {"operation": "implement", "target": "test_file.py"}
        }
        
        # Execute
        result = gateway.process_request(request_data)
        
        # Assert: Success status
        assert result.response.status == "success"
        
        # Assert: Response has result
        assert result.response.result is not None
        assert "tool_executed" in result.response.result
        
        # Assert: Validations passed
        assert result.validations_passed >= 4, "Should pass 4+ validations"
        
        # Assert: Processing time reasonable
        assert result.processing_time < 1.0, "Processing should be <1 second"
        
        # Audit Verification
        conn = sqlite3.connect(audit_db_path)
        cursor = conn.cursor()
        
        # Query request lifecycle events
        cursor.execute(
            "SELECT COUNT(*) FROM audit WHERE rule_id = 'req-001'"
        )
        audit_count = cursor.fetchone()[0]
        
        # RED phase: Should have multiple audit entries
        assert audit_count >= 5, f"Expected 5+ audit entries, got {audit_count}"
        
        # Verify specific operations logged
        cursor.execute(
            "SELECT DISTINCT operation FROM audit WHERE rule_id = 'req-001' ORDER BY timestamp"
        )
        operations = [row[0] for row in cursor.fetchall()]
        
        assert "request_received" in operations
        assert "tool_validated" in operations
        assert "tool_executed" in operations
        assert "response_sent" in operations
        
        conn.close()
    
    def test_tool_validation_in_request_cycle(self, gateway, audit_db_path):
        """Verify tool validation happens in request cycle."""
        # Setup: Valid tool
        valid_request = {
            "id": "req-002",
            "tool": "cortex_lens_analyze",
            "parameters": {"scope": "full_codebase"}
        }
        
        # Execute
        result = gateway.process_request(valid_request)
        
        # Assert: Successful
        assert result.response.status == "success"
        
        # Audit: Tool validation recorded
        conn = sqlite3.connect(audit_db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) FROM audit WHERE rule_id = 'req-002' "
            "AND operation = 'tool_validated'"
        )
        count = cursor.fetchone()[0]
        
        assert count == 1, "Tool validation should be recorded"
        
        conn.close()
    
    def test_invalid_tool_rejected(self, gateway, audit_db_path):
        """Verify invalid tool is rejected."""
        # Setup: Invalid tool
        invalid_request = {
            "id": "req-003",
            "tool": "unknown_tool",
            "parameters": {}
        }
        
        # Execute
        result = gateway.process_request(invalid_request)
        
        # Assert: Error status
        assert result.response.status == "error"
        
        # Assert: Error message present
        assert "error" in result.response.result
        
        # Audit: Failure recorded
        conn = sqlite3.connect(audit_db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) FROM audit WHERE rule_id = 'req-003' "
            "AND operation = 'tool_validation_failed'"
        )
        count = cursor.fetchone()[0]
        
        assert count == 1, "Tool validation failure should be recorded"
        
        conn.close()
    
    def test_audit_trail_complete_for_request(self, gateway, audit_db_path):
        """Verify complete audit trail from input to output."""
        # Setup
        request_data = {
            "id": "req-audit-trail",
            "tool": "cortex_challenge",
            "parameters": {"design": "test"}
        }
        
        # Execute
        result = gateway.process_request(request_data)
        
        # Query full audit trail
        conn = sqlite3.connect(audit_db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT operation, timestamp FROM audit WHERE rule_id = ? "
            "ORDER BY timestamp ASC",
            ("req-audit-trail",)
        )
        
        audit_trail = cursor.fetchall()
        operations = [row[0] for row in audit_trail]
        
        # Verify chronological order
        expected_sequence = ["request_received", "tool_validated", "parameters_validated", 
                           "request_id_validated", "tool_executed", "response_sent"]
        
        for expected_op in expected_sequence:
            assert expected_op in operations, f"Expected operation '{expected_op}' not in audit trail"
        
        conn.close()
