"""
Golden Tests for Repository Onboarding — Scenario Suite.

Covers 15 onboarding scenarios (Python, .NET, polyglot, empty, large,
secrets, monorepo, governance violations, etc.) with SQLite audit verification.

Authority: CORE-008 (TDD), CORE-011 (type hints), CORE-027 (audit trails)
"""

import json
import shutil
import sqlite3
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

from cortex.mcp.tools.onboard_repository import (
    DASHBOARD_TABS,
    SCHEMA_VERSION,
    onboard_repository_tool,
)


# ============================================================================
# Constants
# ============================================================================

CORTEX_PATH = Path("/Users/asifhussain/PROJECTS/CORTEX")
EXTERNAL_KSESSIONS_PATH = Path("/Users/asifhussain/PROJECTS/KSESSIONS")
GOVERNANCE_DB_PATH = CORTEX_PATH / ".cortex-runtime" / "state" / "governance.db"


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def test_output_dir(tmp_path: Path) -> Path:
    """Isolated output directory — passed to tool via test_mode."""
    return tmp_path


@pytest.fixture
def audit_verifier() -> "AuditTraceVerifier":
    """Create audit trace verifier bound to governance.db."""
    return AuditTraceVerifier(GOVERNANCE_DB_PATH)


@pytest.fixture
def temp_repo(tmp_path: Path):
    """Minimal git repo in a temp directory."""
    repo = tmp_path / "temp_repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    yield repo
    shutil.rmtree(repo, ignore_errors=True)


# ============================================================================
# AuditTraceVerifier
# ============================================================================


class AuditTraceVerifier:
    """Verify audit traces written to the SQLite governance database."""

    _TABLES = ("audit_log", "intelligence_audit", "governance_violations", "onboarding_audit")

    def __init__(self, db_path: Path) -> None:
        """Initialise with path to governance SQLite database."""
        self.db_path = db_path

    def get_all_tables(self) -> List[str]:
        """Return all table names in the database."""
        if not self.db_path.exists():
            return []
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables

    def get_operations_for_repo(
        self,
        repo_name: str,
        operation_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Return audit operations for *repo_name* from all known tables."""
        if not self.db_path.exists():
            return []
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        results: List[Dict[str, Any]] = []
        for table in self._TABLES:
            try:
                if operation_type:
                    cursor.execute(
                        f"SELECT * FROM {table} WHERE target LIKE ? AND operation = ? "
                        f"ORDER BY timestamp DESC",
                        (f"%{repo_name}%", operation_type),
                    )
                else:
                    cursor.execute(
                        f"SELECT * FROM {table} WHERE target LIKE ? ORDER BY timestamp DESC",
                        (f"%{repo_name}%",),
                    )
                results.extend([dict(r) for r in cursor.fetchall()])
            except sqlite3.OperationalError:
                continue
        conn.close()
        return results

    def get_governance_violations(
        self, repo_name: str, rule_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Return governance violations for *repo_name*."""
        if not self.db_path.exists():
            return []
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            if rule_id:
                cursor.execute(
                    "SELECT * FROM governance_violations "
                    "WHERE repository LIKE ? AND rule_id = ? ORDER BY timestamp DESC",
                    (f"%{repo_name}%", rule_id),
                )
            else:
                cursor.execute(
                    "SELECT * FROM governance_violations "
                    "WHERE repository LIKE ? ORDER BY timestamp DESC",
                    (f"%{repo_name}%",),
                )
            rows = [dict(r) for r in cursor.fetchall()]
        except sqlite3.OperationalError:
            rows = []
        conn.close()
        return rows


# ============================================================================
# Scenario 01 — Python Repository (CORTEX itself)
# ============================================================================


class TestOnboardingScenario01_PythonRepo:
    """Scenario 1: Python repository onboarding."""

    def test_onboard_python_repo(
        self, audit_verifier: AuditTraceVerifier, test_output_dir: Path
    ) -> None:
        """Golden: Onboard Python repository — status returned, no crash."""
        result = onboard_repository_tool(
            repository_path=str(CORTEX_PATH),
            capture_learning=False,
            apply_brain_enhancement=False,
            generate_artifacts=True,
            orchestrator_context={
                "source": "MasterOrchestrator",
                "request_id": "scenario-01-python",
            },
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )
        assert "status" in result
        assert "repository_path" in result
        print(f"\n✅ Scenario 01 status: {result['status']}")
        print(f"📊 Audit tables: {audit_verifier.get_all_tables()}")


# ============================================================================
# Scenario 02 — .NET/C# Repository
# ============================================================================


class TestOnboardingScenario02_DotNetRepo:
    """Scenario 2: .NET/C# repository onboarding."""

    def test_onboard_dotnet_repo(
        self, audit_verifier: AuditTraceVerifier, test_output_dir: Path
    ) -> None:
        """Golden: Onboard .NET repo; skip if not available locally."""
        if not EXTERNAL_KSESSIONS_PATH.exists():
            pytest.skip("External .NET repository not available on this machine")

        result = onboard_repository_tool(
            repository_path=str(EXTERNAL_KSESSIONS_PATH),
            capture_learning=False,
            apply_brain_enhancement=False,
            generate_artifacts=True,
            orchestrator_context={
                "source": "MasterOrchestrator",
                "request_id": "scenario-02-dotnet",
            },
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )
        assert "status" in result
        assert result.get("repository_path") == str(EXTERNAL_KSESSIONS_PATH)
        violations = audit_verifier.get_governance_violations(
            EXTERNAL_KSESSIONS_PATH.name
        )
        print(f"\n⚠️  Governance violations: {len(violations)}")


# ============================================================================
# Scenario 03 — Empty Repository
# ============================================================================


class TestOnboardingScenario03_EmptyRepo:
    """Scenario 3: Empty repository onboarding."""

    def test_onboard_empty_repository(
        self,
        temp_repo: Path,
        audit_verifier: AuditTraceVerifier,
        test_output_dir: Path,
    ) -> None:
        """Golden: Empty repo handled gracefully — no crash, status returned."""
        result = onboard_repository_tool(
            repository_path=str(temp_repo),
            orchestrator_context={
                "source": "MasterOrchestrator",
                "request_id": "scenario-03-empty",
            },
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )
        assert "status" in result
        print(f"\n📝 Empty repo status: {result['status']}")


# ============================================================================
# Scenario 04 — Polyglot Repository
# ============================================================================


class TestOnboardingScenario04_PolyglotRepo:
    """Scenario 4: Mixed-language (polyglot) repository."""

    def test_onboard_polyglot_repository(
        self,
        temp_repo: Path,
        audit_verifier: AuditTraceVerifier,
        test_output_dir: Path,
    ) -> None:
        """Golden: Polyglot repo onboards without crash."""
        (temp_repo / "main.py").write_text("print('Python')\n")
        (temp_repo / "index.ts").write_text("console.log('TypeScript');\n")
        (temp_repo / "main.rs").write_text('fn main() { println!("Rust"); }\n')

        result = onboard_repository_tool(
            repository_path=str(temp_repo),
            orchestrator_context={
                "source": "MasterOrchestrator",
                "request_id": "scenario-04-polyglot",
            },
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )
        assert "status" in result


# ============================================================================
# Scenario 05 — Documentation-Only Repository
# ============================================================================


class TestOnboardingScenario05_DocsOnly:
    """Scenario 5: Repository with no code files."""

    def test_onboard_docs_only_repository(
        self,
        temp_repo: Path,
        audit_verifier: AuditTraceVerifier,
        test_output_dir: Path,
    ) -> None:
        """Golden: Docs-only repo returns a status without crash."""
        (temp_repo / "README.md").write_text("# Documentation Only\n")
        docs = temp_repo / "docs"
        docs.mkdir()
        (docs / "guide.md").write_text("# Guide\n")

        result = onboard_repository_tool(
            repository_path=str(temp_repo),
            orchestrator_context={
                "source": "MasterOrchestrator",
                "request_id": "scenario-05-docs-only",
            },
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )
        assert "status" in result


# ============================================================================
# Scenario 06 — Re-Onboarding (Idempotency)
# ============================================================================


class TestOnboardingScenario06_ReOnboarding:
    """Scenario 6: Re-onboarding an already onboarded repository."""

    def test_reonboard_is_idempotent(
        self,
        temp_repo: Path,
        test_output_dir: Path,
    ) -> None:
        """Golden: Two consecutive onboarding calls produce the same status."""
        (temp_repo / "main.py").write_text("# Source\n")

        ctx = {"source": "MasterOrchestrator", "request_id": "scenario-06a"}
        result1 = onboard_repository_tool(
            repository_path=str(temp_repo),
            orchestrator_context=ctx,
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )

        ctx["request_id"] = "scenario-06b"
        result2 = onboard_repository_tool(
            repository_path=str(temp_repo),
            orchestrator_context=ctx,
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )

        assert result1["status"] == result2["status"]
        assert result1["repository_path"] == result2["repository_path"]


# ============================================================================
# Scenario 07 — Missing Dependencies
# ============================================================================


class TestOnboardingScenario07_MissingDependencies:
    """Scenario 7: Repository with unresolvable dependencies."""

    def test_onboard_repo_with_missing_deps(
        self,
        temp_repo: Path,
        test_output_dir: Path,
    ) -> None:
        """Golden: Repo with missing deps returns a status (no crash)."""
        (temp_repo / "main.py").write_text("import nonexistent_package\n")
        (temp_repo / "requirements.txt").write_text("nonexistent-package==1.0.0\n")

        result = onboard_repository_tool(
            repository_path=str(temp_repo),
            orchestrator_context={"source": "MasterOrchestrator", "request_id": "scenario-07"},
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )
        assert "status" in result


# ============================================================================
# Scenario 08 — Secrets Detection
# ============================================================================


class TestOnboardingScenario08_SecretsDetection:
    """Scenario 8: Repository containing hardcoded secrets."""

    def test_onboard_repo_with_secrets(
        self,
        temp_repo: Path,
        audit_verifier: AuditTraceVerifier,
        test_output_dir: Path,
    ) -> None:
        """Golden: Repo with secrets returns status; security tab should note risk."""
        (temp_repo / "config.py").write_text(
            'API_KEY = "sk-1234567890abcdef"\n'
            'PASSWORD = "super_secret_password"\n'
            'AWS_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"\n'
        )

        result = onboard_repository_tool(
            repository_path=str(temp_repo),
            orchestrator_context={"source": "MasterOrchestrator", "request_id": "scenario-08"},
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )
        assert "status" in result
        violations = audit_verifier.get_governance_violations(temp_repo.name)
        print(f"\n⚠️  Security violations: {len(violations)}")


# ============================================================================
# Scenario 09 — Tests-Only Repository
# ============================================================================


class TestOnboardingScenario09_TestsOnly:
    """Scenario 9: Repository with only test files."""

    def test_onboard_tests_only_repository(
        self,
        temp_repo: Path,
        test_output_dir: Path,
    ) -> None:
        """Golden: Tests-only repo returns a status without crash."""
        tests_dir = temp_repo / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_example.py").write_text("def test_something():\n    assert True\n")

        result = onboard_repository_tool(
            repository_path=str(temp_repo),
            orchestrator_context={"source": "MasterOrchestrator", "request_id": "scenario-09"},
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )
        assert "status" in result


# ============================================================================
# Scenario 10 — Large Repository
# ============================================================================


class TestOnboardingScenario10_LargeRepo:
    """Scenario 10: Repository with many source files."""

    def test_onboard_large_repository(
        self,
        temp_repo: Path,
        test_output_dir: Path,
    ) -> None:
        """Golden: 50-file repo onboards without crash (scalability check)."""
        src = temp_repo / "src"
        src.mkdir()
        for i in range(50):
            (src / f"module_{i:03d}.py").write_text(
                f'"""Module {i}."""\n\ndef func_{i}() -> None:\n    pass\n'
            )

        result = onboard_repository_tool(
            repository_path=str(temp_repo),
            orchestrator_context={"source": "MasterOrchestrator", "request_id": "scenario-10"},
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )
        assert "status" in result


# ============================================================================
# Scenario 11 — Monorepo
# ============================================================================


class TestOnboardingScenario11_Monorepo:
    """Scenario 11: Monorepo with multiple sub-projects."""

    def test_onboard_monorepo(
        self,
        temp_repo: Path,
        test_output_dir: Path,
    ) -> None:
        """Golden: Monorepo structure onboards without crash."""
        (temp_repo / "services" / "api").mkdir(parents=True)
        (temp_repo / "services" / "api" / "main.py").write_text("# API\n")
        (temp_repo / "services" / "worker").mkdir(parents=True)
        (temp_repo / "services" / "worker" / "main.py").write_text("# Worker\n")
        (temp_repo / "libs" / "common").mkdir(parents=True)
        (temp_repo / "libs" / "common" / "__init__.py").write_text("# Shared\n")

        result = onboard_repository_tool(
            repository_path=str(temp_repo),
            orchestrator_context={"source": "MasterOrchestrator", "request_id": "scenario-11"},
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )
        assert "status" in result


# ============================================================================
# Scenario 12 — Complex AST
# ============================================================================


class TestOnboardingScenario12_ComplexAST:
    """Scenario 12: Repository with advanced Python constructs."""

    def test_onboard_complex_ast_repository(
        self,
        temp_repo: Path,
        test_output_dir: Path,
    ) -> None:
        """Golden: Complex AST (metaclasses, decorators, async) onboards cleanly."""
        (temp_repo / "complex.py").write_text(
            'from abc import ABC, abstractmethod\n'
            'from typing import TypeVar, Generic\n\n'
            'T = TypeVar("T")\n\n'
            'class Meta(type):\n    pass\n\n'
            'class Base(ABC, Generic[T], metaclass=Meta):\n'
            '    @abstractmethod\n'
            '    def process(self, data: T) -> T: ...\n\n'
            'def decorator(fn):\n'
            '    def wrapper(*a, **kw): return fn(*a, **kw)\n'
            '    return wrapper\n\n'
            '@decorator\n'
            'async def async_fn(x: int) -> int:\n    return x * 2\n'
        )

        result = onboard_repository_tool(
            repository_path=str(temp_repo),
            orchestrator_context={"source": "MasterOrchestrator", "request_id": "scenario-12"},
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )
        assert "status" in result


# ============================================================================
# Scenario 13 — Governance Violations
# ============================================================================


class TestOnboardingScenario13_GovernanceViolations:
    """Scenario 13: Repository with multiple governance violations."""

    def test_onboard_repo_with_violations(
        self,
        temp_repo: Path,
        audit_verifier: AuditTraceVerifier,
        test_output_dir: Path,
    ) -> None:
        """Golden: Repo with CORE violations returns status; violations optionally logged."""
        (temp_repo / "bad_code.py").write_text(
            '# No docstrings, no type hints — CORE-011/CORE-012 violations\n'
            'def func(x):\n    return x * 2\n\n'
            'API_KEY = "sk-123456"\n\n'
            'def query_db(user_input):\n'
            '    sql = f"SELECT * FROM users WHERE id = {user_input}"\n'
            '    return sql\n'
        )

        result = onboard_repository_tool(
            repository_path=str(temp_repo),
            orchestrator_context={"source": "MasterOrchestrator", "request_id": "scenario-13"},
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )
        assert "status" in result
        violations = audit_verifier.get_governance_violations(temp_repo.name)
        print(f"\n⚠️  Detected violations: {len(violations)}")
        for v in violations:
            print(f"  - {v.get('rule_id')}: {v.get('message')}")


# ============================================================================
# Scenario 14 — Non-Existent Path
# ============================================================================


class TestOnboardingScenario14_NonExistentPath:
    """Scenario 14: Attempt to onboard a non-existent path."""

    def test_onboard_nonexistent_path(self, test_output_dir: Path) -> None:
        """Golden: Non-existent path returns status=error with message."""
        result = onboard_repository_tool(
            repository_path="/nonexistent/path/to/repo",
            orchestrator_context={
                "source": "MasterOrchestrator",
                "request_id": "scenario-14-nonexistent",
            },
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )
        assert result["status"] == "error"
        assert "error" in result


# ============================================================================
# Scenario 15 — Custom Domain Knowledge
# ============================================================================


class TestOnboardingScenario15_DomainKnowledge:
    """Scenario 15: Repository with domain-specific financial terminology."""

    def test_onboard_repo_with_domain_knowledge(
        self,
        temp_repo: Path,
        test_output_dir: Path,
    ) -> None:
        """Golden: Domain-rich repo (finance) onboards cleanly."""
        (temp_repo / "finance.py").write_text(
            '"""Financial domain module."""\n\n'
            'def calculate_irr(cash_flows: list[float], initial_investment: float) -> float:\n'
            '    """Calculate Internal Rate of Return."""\n    return 0.0\n\n'
            'def compute_sharpe_ratio(returns: list[float], risk_free_rate: float) -> float:\n'
            '    """Compute Sharpe Ratio."""\n    return 0.0\n\n'
            'class BlackScholesModel:\n'
            '    """Black-Scholes option pricing model."""\n\n'
            '    def price_call_option(self, S: float, K: float, T: float, r: float, sigma: float) -> float:\n'
            '        """Price European call option."""\n        return 0.0\n'
        )

        result = onboard_repository_tool(
            repository_path=str(temp_repo),
            orchestrator_context={
                "source": "MasterOrchestrator",
                "request_id": "scenario-15-domain",
            },
            test_mode=True,
            test_output_dir=str(test_output_dir),
        )
        assert "status" in result


# ============================================================================
# Audit Trail Integrity
# ============================================================================


class TestAuditTrailIntegrity:
    """Verify governance.db audit trail structure and accessibility."""

    def test_audit_database_accessible(self, audit_verifier: AuditTraceVerifier) -> None:
        """Golden: governance.db exists and tables are queryable."""
        if not GOVERNANCE_DB_PATH.exists():
            pytest.skip("governance.db not present — skipping audit tests")
        tables = audit_verifier.get_all_tables()
        print(f"\n📊 Audit DB tables: {tables}")
        assert isinstance(tables, list)

    def test_audit_trail_schema_readable(
        self, audit_verifier: AuditTraceVerifier
    ) -> None:
        """Golden: Each table in governance.db has readable column info."""
        if not GOVERNANCE_DB_PATH.exists():
            pytest.skip("governance.db not present")

        conn = sqlite3.connect(GOVERNANCE_DB_PATH)
        cursor = conn.cursor()
        for table in audit_verifier.get_all_tables():
            cursor.execute(f"PRAGMA table_info({table})")
            cols = cursor.fetchall()
            assert cols, f"Table {table!r} returned no column info"
            print(f"\n  {table}: {[c[1] for c in cols]}")
        conn.close()

    def test_query_operations_by_repo(
        self, audit_verifier: AuditTraceVerifier
    ) -> None:
        """Golden: get_operations_for_repo returns a list (may be empty)."""
        ops = audit_verifier.get_operations_for_repo("nonexistent_repo_for_test")
        assert isinstance(ops, list)
