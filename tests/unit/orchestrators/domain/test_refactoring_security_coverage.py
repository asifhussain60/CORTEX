"""
RefactoringOrchestrator Security & Coverage Tests — TDD RED phase (CORE-008)

AC_START: AC-ENH-STS-2026-02-22-002
Tests for ENH-STS-03 and ENH-STS-04:
  - ENH-STS-03: Security hardening checks (weak crypto, missing rate-limit, broken JWT)
  - ENH-STS-04: Test coverage density gate (per-class test file, test/LOC ratio)

CORE-008: Tests written BEFORE implementation.
"""

from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# ENH-STS-03 — Security Hardening Checks
# ─────────────────────────────────────────────────────────────────────────────


class TestSecurityHardeningChecks:
    """ENH-STS-03: LENS-driven security hardening gate for REFACTOR mode."""

    def test_check_security_hardening_returns_ok_on_clean_source(self) -> None:
        """Clean source code (no issues) → Ok with empty violations list."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )

        orchestrator = RefactoringOrchestrator()
        clean_source = textwrap.dedent("""
            using BCrypt.Net;
            public class AuthService {
                public string HashPassword(string pw) {
                    return BCrypt.Net.BCrypt.HashPassword(pw);
                }
            }
        """)

        result = orchestrator.check_security_hardening(
            source_code=clean_source,
            language="csharp",
        )

        assert result.is_ok()
        report = result.unwrap()
        assert isinstance(report["violations"], list)
        assert report["clean"] is True

    def test_check_security_hardening_detects_sha256_for_passwords(self) -> None:
        """SHA256 used in password context → P1 violation."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )

        orchestrator = RefactoringOrchestrator()
        bad_source = textwrap.dedent("""
            using System.Security.Cryptography;
            public class UserService {
                public string HashPassword(string password) {
                    using var sha = SHA256.Create();
                    var hash = sha.ComputeHash(Encoding.UTF8.GetBytes(password));
                    return Convert.ToBase64String(hash);
                }
            }
        """)

        result = orchestrator.check_security_hardening(
            source_code=bad_source,
            language="csharp",
        )

        assert result.is_ok()
        report = result.unwrap()
        assert report["clean"] is False
        severities = [v["severity"] for v in report["violations"]]
        assert "P1" in severities
        rules = [v["rule"] for v in report["violations"]]
        assert any("weak_password_hash" in r for r in rules)

    def test_check_security_hardening_detects_md5_for_passwords(self) -> None:
        """MD5 in password context → P1 violation."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )

        orchestrator = RefactoringOrchestrator()
        bad_source = textwrap.dedent("""
            public class Auth {
                public string HashPassword(string password) {
                    using var md5 = MD5.Create();
                    return BitConverter.ToString(md5.ComputeHash(Encoding.UTF8.GetBytes(password)));
                }
            }
        """)

        result = orchestrator.check_security_hardening(
            source_code=bad_source,
            language="csharp",
        )

        assert result.is_ok()
        report = result.unwrap()
        assert report["clean"] is False
        assert any("weak_password_hash" in v["rule"] for v in report["violations"])

    def test_check_security_hardening_detects_jwt_config_without_middleware(self) -> None:
        """JWT config key present but no AddAuthentication call → P0 violation."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )

        orchestrator = RefactoringOrchestrator()
        # appsettings-style JSON without middleware wiring
        bad_source = textwrap.dedent("""
            {
              "Jwt": { "Secret": "REPLACE-WITH-ENV-VARIABLE", "ExpiryMinutes": 60 }
            }
        """)

        result = orchestrator.check_security_hardening(
            source_code=bad_source,
            language="json",
            context_hints={"has_jwt_config": True, "has_jwt_middleware": False},
        )

        assert result.is_ok()
        report = result.unwrap()
        assert report["clean"] is False
        assert any("incomplete_jwt" in v["rule"] for v in report["violations"])
        p0_violations = [v for v in report["violations"] if v["severity"] == "P0"]
        assert len(p0_violations) >= 1

    def test_check_security_hardening_detects_missing_rate_limiting(self) -> None:
        """Login endpoint present but no rate limiting middleware → P1 violation."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )

        orchestrator = RefactoringOrchestrator()
        bad_source = textwrap.dedent("""
            app.MapPost("/api/login", async (LoginRequest req, IUserService svc) => {
                return await svc.LoginAsync(req.Email, req.Password);
            });
        """)

        result = orchestrator.check_security_hardening(
            source_code=bad_source,
            language="csharp",
            context_hints={"has_rate_limiting": False, "has_sensitive_endpoints": True},
        )

        assert result.is_ok()
        report = result.unwrap()
        assert report["clean"] is False
        assert any("missing_rate_limiting" in v["rule"] for v in report["violations"])

    def test_check_security_hardening_accepts_bcrypt(self) -> None:
        """BCrypt.HashPassword → no weak_password_hash violation."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )

        orchestrator = RefactoringOrchestrator()
        good_source = textwrap.dedent("""
            public string HashPassword(string password) {
                return BCrypt.Net.BCrypt.HashPassword(password, workFactor: 12);
            }
        """)

        result = orchestrator.check_security_hardening(
            source_code=good_source,
            language="csharp",
        )

        assert result.is_ok()
        report = result.unwrap()
        assert not any("weak_password_hash" in v["rule"] for v in report["violations"])

    def test_check_security_hardening_typescript_detects_localstorage_token(self) -> None:
        """Storing JWT in localStorage → P1 violation (XSS risk)."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )

        orchestrator = RefactoringOrchestrator()
        bad_ts = textwrap.dedent("""
            const token = await loginUser(email, password);
            localStorage.setItem('token', token);
        """)

        result = orchestrator.check_security_hardening(
            source_code=bad_ts,
            language="typescript",
        )

        assert result.is_ok()
        report = result.unwrap()
        assert report["clean"] is False
        assert any("localstorage_token" in v["rule"] for v in report["violations"])

    def test_check_security_hardening_unsupported_language_returns_err(self) -> None:
        """Unknown language returns Err."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )

        orchestrator = RefactoringOrchestrator()
        result = orchestrator.check_security_hardening(
            source_code="some code",
            language="cobol",
        )

        assert result.is_err()

    def test_check_security_hardening_report_has_required_keys(self) -> None:
        """Report dict always contains violations, clean, violation_count, language."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )

        orchestrator = RefactoringOrchestrator()
        result = orchestrator.check_security_hardening(
            source_code="public class Foo {}",
            language="csharp",
        )

        assert result.is_ok()
        report = result.unwrap()
        for key in ("violations", "clean", "violation_count", "language"):
            assert key in report, f"Missing key: {key}"


# ─────────────────────────────────────────────────────────────────────────────
# ENH-STS-04 — Test Coverage Density Gate
# ─────────────────────────────────────────────────────────────────────────────


class TestCoverageDensityGate:
    """ENH-STS-04: Per-class test coverage and test/LOC ratio enforcement."""

    def test_check_test_coverage_density_returns_ok_when_all_covered(
        self, tmp_path: Path
    ) -> None:
        """Every service class has a matching test class → Ok, complete=True."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )

        # Build minimal directory structure
        services = tmp_path / "Services"
        tests = tmp_path / "Tests" / "Services"
        services.mkdir(parents=True)
        tests.mkdir(parents=True)

        (services / "UserService.cs").write_text("public class UserService {}")
        (services / "AccountService.cs").write_text("public class AccountService {}")
        (tests / "UserServiceTests.cs").write_text("public class UserServiceTests {}")
        (tests / "AccountServiceTests.cs").write_text("public class AccountServiceTests {}")

        orchestrator = RefactoringOrchestrator()
        result = orchestrator.check_test_coverage_density(
            service_dir=services,
            test_dir=tests,
            service_suffix="Service",
            test_suffix="Tests",
        )

        assert result.is_ok()
        report = result.unwrap()
        assert report["complete"] is True
        assert report["missing_test_classes"] == []

    def test_check_test_coverage_density_detects_missing_test_class(
        self, tmp_path: Path
    ) -> None:
        """AccountService has no AccountServiceTests → reported as missing."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )

        services = tmp_path / "Services"
        tests = tmp_path / "Tests" / "Services"
        services.mkdir(parents=True)
        tests.mkdir(parents=True)

        (services / "UserService.cs").write_text("public class UserService {}")
        (services / "AccountService.cs").write_text("public class AccountService {}")
        (services / "ReportService.cs").write_text("public class ReportService {}")
        # Only UserService has a test
        (tests / "UserServiceTests.cs").write_text("public class UserServiceTests {}")

        orchestrator = RefactoringOrchestrator()
        result = orchestrator.check_test_coverage_density(
            service_dir=services,
            test_dir=tests,
            service_suffix="Service",
            test_suffix="Tests",
        )

        assert result.is_ok()
        report = result.unwrap()
        assert report["complete"] is False
        missing = report["missing_test_classes"]
        assert "AccountServiceTests" in missing
        assert "ReportServiceTests" in missing
        assert len(missing) == 2

    def test_check_test_coverage_density_empty_service_dir_is_ok(
        self, tmp_path: Path
    ) -> None:
        """No service files → vacuously complete."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )

        services = tmp_path / "Services"
        tests = tmp_path / "Tests"
        services.mkdir(parents=True)
        tests.mkdir(parents=True)

        orchestrator = RefactoringOrchestrator()
        result = orchestrator.check_test_coverage_density(
            service_dir=services,
            test_dir=tests,
            service_suffix="Service",
            test_suffix="Tests",
        )

        assert result.is_ok()
        assert result.unwrap()["complete"] is True

    def test_check_test_coverage_density_nonexistent_dir_returns_err(
        self, tmp_path: Path
    ) -> None:
        """Non-existent service_dir returns Err."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )

        orchestrator = RefactoringOrchestrator()
        result = orchestrator.check_test_coverage_density(
            service_dir=tmp_path / "does_not_exist",
            test_dir=tmp_path / "also_missing",
            service_suffix="Service",
            test_suffix="Tests",
        )

        assert result.is_err()

    def test_check_test_coverage_density_report_has_required_keys(
        self, tmp_path: Path
    ) -> None:
        """Report always contains complete, missing_test_classes, coverage_pct, checked."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )

        services = tmp_path / "Svc"
        tests = tmp_path / "Tests"
        services.mkdir()
        tests.mkdir()
        (services / "FooService.cs").write_text("class FooService {}")
        (tests / "FooServiceTests.cs").write_text("class FooServiceTests {}")

        orchestrator = RefactoringOrchestrator()
        result = orchestrator.check_test_coverage_density(
            service_dir=services,
            test_dir=tests,
            service_suffix="Service",
            test_suffix="Tests",
        )

        assert result.is_ok()
        report = result.unwrap()
        for key in ("complete", "missing_test_classes", "coverage_pct", "checked"):
            assert key in report, f"Missing key: {key}"

    def test_check_test_coverage_density_coverage_pct_correct(
        self, tmp_path: Path
    ) -> None:
        """2 services, 1 test class → 50% coverage_pct."""
        from cortex.orchestrators.domain.refactoring_orchestrator import (
            RefactoringOrchestrator,
        )

        services = tmp_path / "S"
        tests = tmp_path / "T"
        services.mkdir()
        tests.mkdir()
        (services / "AService.cs").write_text("class AService {}")
        (services / "BService.cs").write_text("class BService {}")
        (tests / "AServiceTests.cs").write_text("class AServiceTests {}")

        orchestrator = RefactoringOrchestrator()
        result = orchestrator.check_test_coverage_density(
            service_dir=services,
            test_dir=tests,
            service_suffix="Service",
            test_suffix="Tests",
        )

        report = result.unwrap()
        assert report["coverage_pct"] == 50.0


# AC_COMPLETE: AC-ENH-STS-2026-02-22-002 ✅ (RED phase — tests expected to FAIL)
