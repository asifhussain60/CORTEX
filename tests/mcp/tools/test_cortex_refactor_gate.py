"""
CortexRefactor MCP Tool — ENH-STS Gate Operation Tests (CORE-008)

AC_START: AC-ENH-STS-GATE-MCP-2026-02-22

Tests for the new `gate` operation on the `cortex_refactor` MCP tool,
which wires the four ENH-STS Software Transformation Session gates:
  ENH-STS-01  check_functional_completeness  — dropped endpoint detection
  ENH-STS-02  write_refactor_session_trace   — AC_START / AC_COMPLETE audit
  ENH-STS-03  check_security_hardening       — weak crypto / incomplete auth
  ENH-STS-04  check_test_coverage_density    — every Service has a TestClass

CORE-008: All tests written BEFORE implementation (RED phase).
CORE-011: All functions type-annotated.
CORE-012: All public APIs have docstrings.
CORE-028: snake_case filenames only.
"""
from __future__ import annotations

import asyncio
import textwrap
import uuid
from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def run(coro: Any) -> Any:
    """Run an async coroutine in a blocking context."""
    return asyncio.get_event_loop().run_until_complete(coro)


def _make_tool() -> Any:
    """Instantiate CortexRefactor."""
    from cortex.mcp.tools.operations import CortexRefactor
    return CortexRefactor()


# ─────────────────────────────────────────────────────────────────────────────
# 1. Tool metadata — gate must be advertised
# ─────────────────────────────────────────────────────────────────────────────

class TestCortexRefactorGateAdvertised:
    """Verify gate operation is advertised in tool metadata."""

    def test_gate_in_supported_operations(self) -> None:
        """gate must appear in supported_operations list."""
        tool = _make_tool()
        assert "gate" in tool.supported_operations

    def test_gate_in_parameters_enum(self) -> None:
        """gate must appear in the operation parameter enum."""
        tool = _make_tool()
        op_param = next(p for p in tool.parameters if p.name == "operation")
        assert "gate" in (op_param.enum or [])

    def test_gate_parameters_documented(self) -> None:
        """All ENH-STS gate params must be present in parameters list."""
        tool = _make_tool()
        param_names = {p.name for p in tool.parameters}
        required_gate_params = {
            "source_items", "target_items",   # ENH-STS-01
            "session_id", "trace_action", "trace_metadata",  # ENH-STS-02
            "source_code", "language", "context_hints",       # ENH-STS-03
            "service_dir", "test_dir",                         # ENH-STS-04
        }
        assert required_gate_params.issubset(param_names), (
            f"Missing gate params: {required_gate_params - param_names}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# 2. Gate — all params absent → all gates skipped, status PASS
# ─────────────────────────────────────────────────────────────────────────────

class TestCortexRefactorGateSkipsWhenNoParams:
    """When no gate-specific params are provided, all gates skip gracefully."""

    def test_gate_with_no_params_returns_pass(self) -> None:
        """gate with only target → all 4 gates skipped → overall PASS."""
        tool = _make_tool()
        result = run(tool.execute(operation="gate", target="cortex-sts/CortexLabs/BadMonolith"))

        assert result.success is True
        data = result.data
        assert data["overall_status"] == "PASS"
        assert data["p0_count"] == 0
        assert data["total_violations"] == 0

    def test_gate_skipped_gates_have_skipped_key(self) -> None:
        """Each skipped gate result has {'skipped': True, 'reason': ...}."""
        tool = _make_tool()
        result = run(tool.execute(operation="gate", target="some/repo"))

        gate_results = result.data["gate_results"]
        for key in [
            "ENH-STS-01_functional_completeness",
            "ENH-STS-02_session_trace",
            "ENH-STS-03_security_hardening",
            "ENH-STS-04_test_coverage_density",
        ]:
            assert key in gate_results, f"Expected gate key missing: {key}"
            assert gate_results[key].get("skipped") is True
            assert "reason" in gate_results[key]

    def test_gate_metadata_shows_four_gates_run(self) -> None:
        """metadata.sts_gates_run == 4 regardless of skip status."""
        tool = _make_tool()
        result = run(tool.execute(operation="gate", target="repo"))
        assert result.metadata["sts_gates_run"] == 4
        assert result.metadata["operation"] == "gate"


# ─────────────────────────────────────────────────────────────────────────────
# 3. ENH-STS-01 — Functional Completeness
# ─────────────────────────────────────────────────────────────────────────────

class TestCortexRefactorGateENHSTS01:
    """ENH-STS-01: gate surfaces functional gaps as P0 violations."""

    def test_sts01_pass_when_all_items_present(self) -> None:
        """No gaps → ENH-STS-01 complete=True → overall PASS."""
        tool = _make_tool()
        items = ["GET /api/users", "POST /api/transactions", "POST /api/accounts/transfer"]
        result = run(tool.execute(
            operation="gate",
            target="repo",
            source_items=items,
            target_items=items,
        ))

        assert result.success is True
        assert result.data["overall_status"] == "PASS"
        fc = result.data["gate_results"]["ENH-STS-01_functional_completeness"]
        assert fc["complete"] is True
        assert fc["gap_count"] == 0

    def test_sts01_block_when_endpoint_dropped(self) -> None:
        """Dropped endpoint → P0 blocking issue → overall BLOCK."""
        tool = _make_tool()
        source = ["GET /api/users", "POST /api/accounts/transfer", "GET /api/admin/stats"]
        target = ["GET /api/users"]  # missing two endpoints

        result = run(tool.execute(
            operation="gate",
            target="repo",
            source_items=source,
            target_items=target,
        ))

        assert result.success is False
        assert result.data["overall_status"] == "BLOCK"
        assert result.data["p0_count"] >= 1
        fc = result.data["gate_results"]["ENH-STS-01_functional_completeness"]
        assert fc["complete"] is False
        assert "POST /api/accounts/transfer" in fc["gaps"]
        assert "GET /api/admin/stats" in fc["gaps"]

    def test_sts01_blocking_issue_message_cites_enh_sts_01(self) -> None:
        """P0 message must reference ENH-STS-01 for traceability."""
        tool = _make_tool()
        result = run(tool.execute(
            operation="gate",
            target="repo",
            source_items=["POST /api/accounts/transfer"],
            target_items=[],
        ))

        issues = result.data["blocking_issues"]
        assert any("ENH-STS-01" in i for i in issues)

    def test_sts01_gap_count_matches_missing_items(self) -> None:
        """gap_count equals the number of items in source not in target."""
        tool = _make_tool()
        source = [f"endpoint_{i}" for i in range(5)]
        target = source[:2]  # 3 missing

        result = run(tool.execute(
            operation="gate",
            target="repo",
            source_items=source,
            target_items=target,
        ))

        fc = result.data["gate_results"]["ENH-STS-01_functional_completeness"]
        assert fc["gap_count"] == 3


# ─────────────────────────────────────────────────────────────────────────────
# 4. ENH-STS-02 — Session Traceability
# ─────────────────────────────────────────────────────────────────────────────

class TestCortexRefactorGateENHSTS02:
    """ENH-STS-02: gate writes AC_START/AC_COMPLETE to audit DB."""

    def test_sts02_persisted_true_on_successful_trace(self) -> None:
        """Successful trace write → persisted=True in gate result."""
        tool = _make_tool()
        sid = str(uuid.uuid4())

        with patch(
            "cortex.orchestrators.domain.refactoring_orchestrator."
            "RefactoringOrchestrator.write_refactor_session_trace",
        ) as mock_trace:
            from cortex.core.result import Ok
            mock_trace.return_value = Ok(None)

            result = run(tool.execute(
                operation="gate",
                target="cortex-sts/CortexLabs/BadMonolith",
                session_id=sid,
                trace_action="AC_START",
                trace_metadata={"smells_catalogued": 25},
            ))

        tr = result.data["gate_results"]["ENH-STS-02_session_trace"]
        assert tr["persisted"] is True
        assert tr["action"] == "AC_START"
        assert tr["session_id"] == sid
        assert tr["error"] is None

    def test_sts02_persisted_false_on_trace_failure(self) -> None:
        """Failed trace write → persisted=False, P1 warning in blocking_issues."""
        tool = _make_tool()
        sid = str(uuid.uuid4())

        with patch(
            "cortex.orchestrators.domain.refactoring_orchestrator."
            "RefactoringOrchestrator.write_refactor_session_trace",
        ) as mock_trace:
            from cortex.core.result import Err
            mock_trace.return_value = Err("DB unavailable")

            result = run(tool.execute(
                operation="gate",
                target="some/repo",
                session_id=sid,
                trace_action="AC_COMPLETE",
            ))

        tr = result.data["gate_results"]["ENH-STS-02_session_trace"]
        assert tr["persisted"] is False
        assert tr["error"] == "DB unavailable"
        # P1 — should warn but not BLOCK alone
        issues = result.data["blocking_issues"]
        assert any("ENH-STS-02" in i for i in issues)

    def test_sts02_ac_complete_with_real_repo_path(self) -> None:
        """AC_COMPLETE must record actual repo path (not 'source/repo' placeholder)."""
        tool = _make_tool()
        sid = str(uuid.uuid4())
        real_source = "cortex-sts/CortexLabs/BadMonolith"

        captured: dict = {}

        def capture_trace(action, source_repo, target_repo, session_id, metadata=None):
            captured.update({"source_repo": source_repo, "target_repo": target_repo})
            from cortex.core.result import Ok
            return Ok(None)

        with patch(
            "cortex.orchestrators.domain.refactoring_orchestrator."
            "RefactoringOrchestrator.write_refactor_session_trace",
            side_effect=capture_trace,
        ):
            run(tool.execute(
                operation="gate",
                target=real_source,
                session_id=sid,
                trace_action="AC_COMPLETE",
                trace_metadata={"smells_addressed": 25, "files_created": 87},
            ))

        assert captured["source_repo"] == real_source
        assert captured["source_repo"] != "source/repo", (
            "AC_COMPLETE must use real repo path — 'source/repo' is a placeholder"
        )

    def test_sts02_skipped_when_session_id_absent(self) -> None:
        """No session_id → ENH-STS-02 skipped with reason."""
        tool = _make_tool()
        result = run(tool.execute(
            operation="gate",
            target="repo",
            trace_action="AC_COMPLETE",
            # session_id intentionally absent
        ))

        tr = result.data["gate_results"]["ENH-STS-02_session_trace"]
        assert tr.get("skipped") is True

    def test_sts02_skipped_when_trace_action_absent(self) -> None:
        """No trace_action → ENH-STS-02 skipped with reason."""
        tool = _make_tool()
        result = run(tool.execute(
            operation="gate",
            target="repo",
            session_id=str(uuid.uuid4()),
            # trace_action intentionally absent
        ))

        tr = result.data["gate_results"]["ENH-STS-02_session_trace"]
        assert tr.get("skipped") is True


# ─────────────────────────────────────────────────────────────────────────────
# 5. ENH-STS-03 — Security Hardening
# ─────────────────────────────────────────────────────────────────────────────

class TestCortexRefactorGateENHSTS03:
    """ENH-STS-03: gate surfaces weak crypto and incomplete auth as P0."""

    _SHA256_SOURCE = textwrap.dedent("""
        public string HashPassword(string password) {
            using var sha = SHA256.Create();
            return Convert.ToBase64String(sha.ComputeHash(Encoding.UTF8.GetBytes(password)));
        }
    """)

    _BCRYPT_SOURCE = textwrap.dedent("""
        public string HashPassword(string password) {
            return BCrypt.Net.BCrypt.HashPassword(password, workFactor: 12);
        }
    """)

    def test_sts03_detects_sha256_password_hashing(self) -> None:
        """SHA256 in password context → weak_password_hash P1 violation → WARN."""
        tool = _make_tool()
        result = run(tool.execute(
            operation="gate",
            target="repo",
            source_code=self._SHA256_SOURCE,
            language="csharp",
        ))

        sh = result.data["gate_results"]["ENH-STS-03_security_hardening"]
        assert sh["violation_count"] >= 1
        rules = [v["rule"] for v in sh["violations"]]
        assert "weak_password_hash" in rules

    def test_sts03_passes_with_bcrypt(self) -> None:
        """BCrypt source → no violations → PASS."""
        tool = _make_tool()
        result = run(tool.execute(
            operation="gate",
            target="repo",
            source_code=self._BCRYPT_SOURCE,
            language="csharp",
        ))

        sh = result.data["gate_results"]["ENH-STS-03_security_hardening"]
        assert sh["clean"] is True
        assert sh["violation_count"] == 0

    def test_sts03_detects_incomplete_jwt_via_context_hints(self) -> None:
        """JWT config present + no middleware → incomplete_jwt P0 violation."""
        tool = _make_tool()
        result = run(tool.execute(
            operation="gate",
            target="repo",
            source_code="// appsettings loaded",
            language="csharp",
            context_hints={
                "has_jwt_config": True,
                "has_jwt_middleware": False,
                "has_sensitive_endpoints": True,
                "has_rate_limiting": True,
            },
        ))

        sh = result.data["gate_results"]["ENH-STS-03_security_hardening"]
        rules = [v["rule"] for v in sh["violations"]]
        assert "incomplete_jwt" in rules

    def test_sts03_detects_missing_rate_limiting_via_context_hints(self) -> None:
        """Sensitive endpoints + no rate limiting → missing_rate_limiting P1 violation."""
        tool = _make_tool()
        result = run(tool.execute(
            operation="gate",
            target="repo",
            source_code="// minimal",
            language="csharp",
            context_hints={
                "has_jwt_config": False,
                "has_jwt_middleware": False,
                "has_sensitive_endpoints": True,
                "has_rate_limiting": False,
            },
        ))

        sh = result.data["gate_results"]["ENH-STS-03_security_hardening"]
        rules = [v["rule"] for v in sh["violations"]]
        assert "missing_rate_limiting" in rules

    def test_sts03_p0_incomplete_jwt_sets_block_status(self) -> None:
        """P0 from ENH-STS-03 (incomplete_jwt) sets overall_status=BLOCK."""
        tool = _make_tool()
        result = run(tool.execute(
            operation="gate",
            target="repo",
            source_code="",
            language="csharp",
            context_hints={"has_jwt_config": True, "has_jwt_middleware": False},
        ))

        # incomplete_jwt is P0 — must block
        assert result.data["overall_status"] == "BLOCK"
        assert result.success is False

    def test_sts03_runs_with_language_and_no_source_code(self) -> None:
        """language supplied with no source_code → gate still runs (context-hint checks work
        even with empty source text).  Result is clean (no violations)."""
        tool = _make_tool()
        result = run(tool.execute(
            operation="gate",
            target="repo",
            language="csharp",
            # source_code absent — context_hints also absent
        ))

        sh = result.data["gate_results"]["ENH-STS-03_security_hardening"]
        # Gate ran — not skipped
        assert sh.get("skipped") is not True
        assert sh["clean"] is True
        assert sh["violation_count"] == 0

    def test_sts03_skipped_when_no_language(self) -> None:
        """Missing language → ENH-STS-03 skipped."""
        tool = _make_tool()
        result = run(tool.execute(
            operation="gate",
            target="repo",
            source_code="some code",
            # language absent
        ))

        sh = result.data["gate_results"]["ENH-STS-03_security_hardening"]
        assert sh.get("skipped") is True


# ─────────────────────────────────────────────────────────────────────────────
# 6. ENH-STS-04 — Test Coverage Density
# ─────────────────────────────────────────────────────────────────────────────

class TestCortexRefactorGateENHSTS04:
    """ENH-STS-04: gate surfaces missing XxxServiceTests as P1 violations."""

    def test_sts04_pass_when_all_services_have_tests(self, tmp_path: Path) -> None:
        """All services covered → complete=True → no P1 violation."""
        svc_dir = tmp_path / "Services"
        test_dir = tmp_path / "Tests" / "Services"
        svc_dir.mkdir(parents=True)
        test_dir.mkdir(parents=True)

        (svc_dir / "UserService.cs").write_text("class UserService {}")
        (svc_dir / "AccountService.cs").write_text("class AccountService {}")
        (test_dir / "UserServiceTests.cs").write_text("class UserServiceTests {}")
        (test_dir / "AccountServiceTests.cs").write_text("class AccountServiceTests {}")

        tool = _make_tool()
        result = run(tool.execute(
            operation="gate",
            target="repo",
            service_dir=str(svc_dir),
            test_dir=str(test_dir),
        ))

        assert result.success is True
        tc = result.data["gate_results"]["ENH-STS-04_test_coverage_density"]
        assert tc["complete"] is True
        assert tc["missing_test_classes"] == []

    def test_sts04_warns_when_service_lacks_test_class(self, tmp_path: Path) -> None:
        """AccountService missing test class → P1 warning in blocking_issues."""
        svc_dir = tmp_path / "Services"
        test_dir = tmp_path / "Tests" / "Services"
        svc_dir.mkdir(parents=True)
        test_dir.mkdir(parents=True)

        (svc_dir / "UserService.cs").write_text("class UserService {}")
        (svc_dir / "AccountService.cs").write_text("class AccountService {}")
        (svc_dir / "ReportService.cs").write_text("class ReportService {}")
        # Only UserService has a test — Account and Report are missing
        (test_dir / "UserServiceTests.cs").write_text("class UserServiceTests {}")

        tool = _make_tool()
        result = run(tool.execute(
            operation="gate",
            target="repo",
            service_dir=str(svc_dir),
            test_dir=str(test_dir),
        ))

        tc = result.data["gate_results"]["ENH-STS-04_test_coverage_density"]
        assert tc["complete"] is False
        assert "AccountServiceTests" in tc["missing_test_classes"]
        assert "ReportServiceTests" in tc["missing_test_classes"]

        issues = result.data["blocking_issues"]
        assert any("ENH-STS-04" in i for i in issues)

    def test_sts04_does_not_block_on_p1(self, tmp_path: Path) -> None:
        """ENH-STS-04 is P1 (WARN) — alone must not set BLOCK status."""
        svc_dir = tmp_path / "Services"
        test_dir = tmp_path / "Tests"
        svc_dir.mkdir(parents=True)
        test_dir.mkdir(parents=True)
        (svc_dir / "AccountService.cs").write_text("")  # no test

        tool = _make_tool()
        result = run(tool.execute(
            operation="gate",
            target="repo",
            service_dir=str(svc_dir),
            test_dir=str(test_dir),
        ))

        # P1 → WARN, not BLOCK
        assert result.data["overall_status"] == "WARN"
        assert result.data["p0_count"] == 0

    def test_sts04_skipped_when_no_service_dir(self) -> None:
        """No service_dir → ENH-STS-04 skipped."""
        tool = _make_tool()
        result = run(tool.execute(
            operation="gate",
            target="repo",
            test_dir="/some/test/dir",
        ))

        tc = result.data["gate_results"]["ENH-STS-04_test_coverage_density"]
        assert tc.get("skipped") is True

    def test_sts04_skipped_when_no_test_dir(self) -> None:
        """No test_dir → ENH-STS-04 skipped."""
        tool = _make_tool()
        result = run(tool.execute(
            operation="gate",
            target="repo",
            service_dir="/some/service/dir",
        ))

        tc = result.data["gate_results"]["ENH-STS-04_test_coverage_density"]
        assert tc.get("skipped") is True


# ─────────────────────────────────────────────────────────────────────────────
# 7. Combined gate — FinTrack scenario (mirrors real BadMonolith gaps)
# ─────────────────────────────────────────────────────────────────────────────

class TestCortexRefactorGateCombinedFinTrackScenario:
    """Integration: simulate the actual FinTrack BadMonolith → Refactored gaps."""

    FINTRACK_SOURCE_ENDPOINTS = [
        "GET /api/users",
        "GET /api/users/search",
        "POST /api/users",
        "GET /api/transactions",
        "GET /api/transactions/search",
        "POST /api/transactions",
        "GET /api/accounts",
        "POST /api/accounts/transfer",  # ← dropped in Refactored
        "GET /api/reports",
        "POST /api/reports/generate",
        "POST /api/auth/login",
        "GET /api/admin/stats",          # ← dropped in Refactored
        "DELETE /api/admin/users/{id}",  # ← dropped in Refactored
        "GET /api/analytics/summary",    # ← dropped in Refactored
        "GET /api/health",
    ]

    FINTRACK_TARGET_ENDPOINTS = [
        "GET /api/v1/users",
        "POST /api/v1/users",
        "DELETE /api/v1/users/{id}",
        "POST /api/v1/users/login",
        "GET /api/v1/transactions",
        "POST /api/v1/transactions",
        "GET /api/v1/accounts",
        "POST /api/v1/accounts",
        "DELETE /api/v1/accounts/{id}",
        "GET /api/v1/reports/user/{userId}",
        "GET /api/v1/health",
    ]

    def test_fintrack_gate_detects_four_dropped_endpoints(self) -> None:
        """Real FinTrack gap: 4 endpoints dropped from BadMonolith → P0 BLOCK."""
        tool = _make_tool()
        result = run(tool.execute(
            operation="gate",
            target="cortex-sts/CortexLabs/BadMonolith",
            source_items=self.FINTRACK_SOURCE_ENDPOINTS,
            target_items=self.FINTRACK_TARGET_ENDPOINTS,
        ))

        assert result.data["overall_status"] == "BLOCK"
        fc = result.data["gate_results"]["ENH-STS-01_functional_completeness"]
        # transfer + admin/stats + admin/delete + analytics — all must surface
        assert fc["gap_count"] >= 4

    def test_fintrack_gate_detects_sha256_and_jwt_gaps(self) -> None:
        """Real FinTrack gap: SHA256 hashing + JWT config without middleware."""
        tool = _make_tool()
        fintrack_service_code = textwrap.dedent("""
            public static string HashPassword(string password) {
                var salt = RandomString(16);
                using var sha = SHA256.Create();
                var hash = sha.ComputeHash(Encoding.UTF8.GetBytes(salt + password));
                return $"{salt}:{Convert.ToBase64String(hash)}";
            }
        """)

        result = run(tool.execute(
            operation="gate",
            target="cortex-sts/CortexLabs/Refactored",
            source_code=fintrack_service_code,
            language="csharp",
            context_hints={
                "has_jwt_config": True,       # appsettings.json has JWT section
                "has_jwt_middleware": False,   # AddAuthentication absent from Program.cs
                "has_sensitive_endpoints": True,
                "has_rate_limiting": False,
            },
        ))

        sh = result.data["gate_results"]["ENH-STS-03_security_hardening"]
        rules = [v["rule"] for v in sh["violations"]]
        assert "weak_password_hash" in rules
        assert "incomplete_jwt" in rules

    def test_fintrack_full_gate_would_have_blocked_original_refactoring(
        self, tmp_path: Path
    ) -> None:
        """Simulate running the full gate on FinTrack: must produce BLOCK."""
        # Set up real FinTrack missing-test scenario
        svc_dir = tmp_path / "Application" / "Services"
        test_dir = tmp_path / "Tests" / "Services"
        svc_dir.mkdir(parents=True)
        test_dir.mkdir(parents=True)

        for svc in ["UserService.cs", "TransactionService.cs", "AccountService.cs", "ReportService.cs"]:
            (svc_dir / svc).write_text(f"public class {svc.replace('.cs','')} {{}}")

        # Only User + Transaction tested — Account + Report missing
        (test_dir / "UserServiceTests.cs").write_text("class UserServiceTests {}")
        (test_dir / "TransactionServiceTests.cs").write_text("class TransactionServiceTests {}")

        tool = _make_tool()
        result = run(tool.execute(
            operation="gate",
            target="cortex-sts/CortexLabs/BadMonolith",
            # ENH-STS-01: dropped endpoints
            source_items=self.FINTRACK_SOURCE_ENDPOINTS,
            target_items=self.FINTRACK_TARGET_ENDPOINTS,
            # ENH-STS-03: weak crypto + JWT gap
            source_code="SHA256.Create().ComputeHash(password)",
            language="csharp",
            context_hints={"has_jwt_config": True, "has_jwt_middleware": False},
            # ENH-STS-04: missing test classes
            service_dir=str(svc_dir),
            test_dir=str(test_dir),
        ))

        # Multiple P0s: dropped endpoints + incomplete JWT
        assert result.data["overall_status"] == "BLOCK"
        assert result.data["p0_count"] >= 2
        assert result.success is False


# AC_COMPLETE: AC-ENH-STS-GATE-MCP-2026-02-22
