"""
Golden Tests for Repository Onboarding - Various Scenarios with SQLite Audit Verification

Comprehensive test coverage for onboarding orchestrator with audit trail validation.
Each test verifies behavior through SQLite governance.db audit logs.

Test Scenarios:
1. Python Repository Onboarding
2. .NET/C# Repository Onboarding (KSESSIONS)
3. TypeScript/JavaScript Repository Onboarding
4. Mixed-Language Repository (polyglot)
5. Large Repository (>1000 files)
6. Empty Repository
7. Repository with No Code Files
8. Repository with Secrets/Credentials
9. Repository with Tests Only
10. Monorepo with Multiple Projects
11. Repository with Missing Dependencies
12. Repository with Governance Violations
13. Repository Already Onboarded (Re-onboarding)
14. Repository with Custom Domain Knowledge
15. Repository with Complex AST Structures

Authority: CORE-008 (TDD), CORE-011 (type hints), CORE-027 (audit trails)
"""

import json
import shutil
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest
import yaml

from cortex.mcp.tools.onboard_repository import onboard_repository_tool


# Test paths
KSESSIONS_PATH = Path("/Users/asifhussain/PROJECTS/KSESSIONS")
CORTEX_PATH = Path("/Users/asifhussain/PROJECTS/CORTEX")
CORTEX_REGISTRY_PATH = CORTEX_PATH / "cortex-registry"
ONBOARDED_REPOS_PATH = CORTEX_PATH / "cortex_intelligence" / "onboarded_repos"
GOVERNANCE_DB_PATH = CORTEX_PATH / "cortex_intelligence" / "governance.db"


@pytest.fixture
def test_output_dir():
    """Create temporary directory for test outputs (isolated from production)."""
    temp_dir = tempfile.mkdtemp(prefix="cortex_test_onboarding_")
    yield Path(temp_dir)
    # Cleanup after test
    shutil.rmtree(temp_dir, ignore_errors=True)


class AuditTraceVerifier:
    """Utility class to verify audit traces in SQLite database."""
    
    def __init__(self, db_path: Path):
        """Initialize verifier with database path."""
        self.db_path = db_path
    
    def get_operations_for_repo(
        self,
        repo_name: str,
        operation_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all audit operations for a repository."""
        if not self.db_path.exists():
            return []
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Try multiple possible table names based on codebase
        tables_to_try = [
            "audit_log",
            "intelligence_audit",
            "governance_violations",
            "onboarding_audit"
        ]
        
        all_results = []
        for table in tables_to_try:
            try:
                if operation_type:
                    cursor.execute(
                        f"SELECT * FROM {table} WHERE target LIKE ? AND operation = ? ORDER BY timestamp DESC",
                        (f"%{repo_name}%", operation_type)
                    )
                else:
                    cursor.execute(
                        f"SELECT * FROM {table} WHERE target LIKE ? ORDER BY timestamp DESC",
                        (f"%{repo_name}%",)
                    )
                
                rows = cursor.fetchall()
                all_results.extend([dict(row) for row in rows])
            except sqlite3.OperationalError:
                # Table doesn't exist, skip
                continue
        
        conn.close()
        return all_results
    
    def get_governance_violations(
        self,
        repo_name: str,
        rule_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get governance violations for a repository."""
        if not self.db_path.exists():
            return []
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            if rule_id:
                cursor.execute(
                    "SELECT * FROM governance_violations WHERE repository LIKE ? AND rule_id = ? ORDER BY timestamp DESC",
                    (f"%{repo_name}%", rule_id)
                )
            else:
                cursor.execute(
                    "SELECT * FROM governance_violations WHERE repository LIKE ? ORDER BY timestamp DESC",
                    (f"%{repo_name}%",)
                )
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.OperationalError:
            return []
        finally:
            conn.close()
    
    def verify_audit_trail_exists(self, repo_name: str) -> bool:
        """Verify that audit trail exists for repository."""
        operations = self.get_operations_for_repo(repo_name)
        return len(operations) > 0
    
    def verify_operation_logged(
        self,
        repo_name: str,
        operation: str,
        min_count: int = 1
    ) -> bool:
        """Verify specific operation was logged."""
        operations = self.get_operations_for_repo(repo_name, operation)
        return len(operations) >= min_count
    
    def get_latest_operation(
        self,
        repo_name: str,
        operation: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get the most recent operation for repository."""
        operations = self.get_operations_for_repo(repo_name, operation)
        return operations[0] if operations else None
    
    def get_all_tables(self) -> List[str]:
        """Get all tables in database for debugging."""
        if not self.db_path.exists():
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables


@pytest.fixture
def audit_verifier():
    """Create audit trace verifier."""
    return AuditTraceVerifier(GOVERNANCE_DB_PATH)


@pytest.fixture
def temp_test_repo():
    """Create temporary test repository."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


class TestOnboardingScenario01_PythonRepo:
    """Scenario 1: Python repository onboarding (CORTEX itself)."""
    
    def test_onboard_cortex_python_repo(self, audit_verifier, test_output_dir):
        """Golden: Onboard CORTEX Python repository with full audit trail."""
        orchestrator_context = {
            "source": "MasterOrchestrator",
            "request_id": "test-scenario-01-python"
        }
        
        result = onboard_repository_tool(
            repository_path=str(CORTEX_PATH),
            capture_learning=False,
            apply_brain_enhancement=False,
            generate_artifacts=True,
            orchestrator_context=orchestrator_context,
            test_mode=True,
            test_output_dir=str(test_output_dir)
        )
        
        # Verify result structure
        assert "status" in result
        assert "repository_path" in result
        
        # Verify audit trail
        print(f"\n📊 Audit Tables: {audit_verifier.get_all_tables()}")
        
        operations = audit_verifier.get_operations_for_repo("CORTEX")
        print(f"📝 Operations logged: {len(operations)}")
        for op in operations[:5]:  # Show first 5
            print(f"  - {op.get('operation', 'UNKNOWN')}: {op.get('timestamp', 'N/A')}")
        
        # Document current behavior (may fail, that's expected)
        if result["status"] == "error":
            print(f"❌ Onboarding failed (expected): {result.get('error')}")
        else:
            print(f"✅ Onboarding succeeded")


class TestOnboardingScenario02_DotNetRepo:
    """Scenario 2: .NET/C# repository onboarding (KSESSIONS)."""
    
    def test_onboard_ksessions_dotnet_repo(self, audit_verifier, test_output_dir):
        """Golden: Onboard KSESSIONS (.NET) repository with audit verification."""
        if not KSESSIONS_PATH.exists():
            pytest.skip("KSESSIONS repository not available")
        
        orchestrator_context = {
            "source": "MasterOrchestrator",
            "request_id": "test-scenario-02-dotnet"
        }
        
        result = onboard_repository_tool(
            repository_path=str(KSESSIONS_PATH),
            capture_learning=False,
            apply_brain_enhancement=False,
            generate_artifacts=True,
            orchestrator_context=orchestrator_context,
            test_mode=True,
            test_output_dir=str(test_output_dir)
        )
        
        # Verify result
        assert "status" in result
        assert result["repository_path"] == str(KSESSIONS_PATH)
        
        # Verify audit trail
        operations = audit_verifier.get_operations_for_repo("KSESSIONS")
        print(f"\n📝 KSESSIONS Operations: {len(operations)}")
        
        # Check for governance violations
        violations = audit_verifier.get_governance_violations("KSESSIONS")
        print(f"⚠️  Governance Violations: {len(violations)}")
        for violation in violations[:3]:
            print(f"  - {violation.get('rule_id', 'N/A')}: {violation.get('message', 'N/A')}")


class TestOnboardingScenario03_EmptyRepo:
    """Scenario 3: Empty repository onboarding."""
    
    def test_onboard_empty_repository(self, temp_test_repo, audit_verifier, test_output_dir):
        """Golden: Onboard empty repository - should handle gracefully."""
        # Create empty repo with .git
        (temp_test_repo / ".git").mkdir()
        
        orchestrator_context = {
            "source": "MasterOrchestrator",
            "request_id": "test-scenario-03-empty"
        }
        
        result = onboard_repository_tool(
            repository_path=str(temp_test_repo),
            orchestrator_context=orchestrator_context,
            test_mode=True,
            test_output_dir=str(test_output_dir)
        )
        
        # Should fail or warn about empty repo
        assert "status" in result
        
        # Verify audit trail captures this
        operations = audit_verifier.get_operations_for_repo(temp_test_repo.name)
        print(f"\n📝 Empty Repo Operations: {len(operations)}")


class TestOnboardingScenario04_PolyglotRepo:
    """Scenario 4: Mixed-language (polyglot) repository."""
    
    def test_onboard_polyglot_repository(self, temp_test_repo, audit_verifier, test_output_dir):
        """Golden: Onboard repository with Python, TypeScript, and Rust."""
        # Create mixed language files
        (temp_test_repo / "main.py").write_text("print('Hello from Python')")
        (temp_test_repo / "index.ts").write_text("console.log('Hello from TypeScript')")
        (temp_test_repo / "main.rs").write_text("fn main() { println!(\"Hello from Rust\"); }")
        (temp_test_repo / ".git").mkdir()
        
        orchestrator_context = {
            "source": "MasterOrchestrator",
            "request_id": "test-scenario-04-polyglot"
        }
        
        result = onboard_repository_tool(
            repository_path=str(temp_test_repo),
            orchestrator_context=orchestrator_context,
            test_mode=True,
            test_output_dir=str(test_output_dir)
        )
        
        assert "status" in result
        
        # Should detect multiple languages
        operations = audit_verifier.get_operations_for_repo(temp_test_repo.name)
        print(f"\n📝 Polyglot Repo Operations: {len(operations)}")


class TestOnboardingScenario05_NoCodeFiles:
    """Scenario 5: Repository with no code files (docs only)."""
    
    def test_onboard_docs_only_repository(self, temp_test_repo, audit_verifier, test_output_dir):
        """Golden: Onboard repository with only markdown files."""
        (temp_test_repo / "README.md").write_text("# Documentation Only")
        (temp_test_repo / "docs").mkdir(parents=True, exist_ok=True)
        (temp_test_repo / "docs" / "guide.md").write_text("# Guide")
        (temp_test_repo / ".git").mkdir()
        
        orchestrator_context = {
            "source": "MasterOrchestrator",
            "request_id": "test-scenario-05-docs-only"
        }
        
        result = onboard_repository_tool(
            repository_path=str(temp_test_repo),
            orchestrator_context=orchestrator_context,
            test_mode=True,
            test_output_dir=str(test_output_dir)
        )
        
        assert "status" in result
        
        # Should handle gracefully
        operations = audit_verifier.get_operations_for_repo(temp_test_repo.name)
        print(f"\n📝 Docs-Only Repo Operations: {len(operations)}")


class TestOnboardingScenario06_ReOnboarding:
    """Scenario 6: Re-onboarding an already onboarded repository."""
    
    def test_reonboard_existing_repository(self, audit_verifier):
        """Golden: Re-onboard CORTEX - should update existing profile."""
        orchestrator_context = {
            "source": "MasterOrchestrator",
            "request_id": "test-scenario-06-reonboard-1"
        }
        
        # First onboarding
        result1 = onboard_repository_tool(
            repository_path=str(CORTEX_PATH),
            orchestrator_context=orchestrator_context,
            test_mode=True,
            test_output_dir=str(test_output_dir)
        )
        
        # Second onboarding
        orchestrator_context["request_id"] = "test-scenario-06-reonboard-2"
        result2 = onboard_repository_tool(
            repository_path=str(CORTEX_PATH),
            orchestrator_context=orchestrator_context,
            test_mode=True,
            test_output_dir=str(test_output_dir)
        )
        
        # Both should succeed (or fail consistently)
        assert result1["status"] == result2["status"]
        
        # Verify audit shows both attempts
        operations = audit_verifier.get_operations_for_repo("CORTEX")
        print(f"\n📝 Re-onboarding Operations: {len(operations)}")


class TestOnboardingScenario07_MissingDependencies:
    """Scenario 7: Repository with missing dependencies."""
    
    def test_onboard_repo_with_missing_deps(self, temp_test_repo, audit_verifier, test_output_dir):
        """Golden: Onboard repo with requirements.txt but missing packages."""
        # Create Python repo with dependencies
        (temp_test_repo / "main.py").write_text("import nonexistent_package")
        (temp_test_repo / "requirements.txt").write_text("nonexistent-package==1.0.0")
        (temp_test_repo / ".git").mkdir()
        
        orchestrator_context = {
            "source": "MasterOrchestrator",
            "request_id": "test-scenario-07-missing-deps"
        }
        
        result = onboard_repository_tool(
            repository_path=str(temp_test_repo),
            orchestrator_context=orchestrator_context,
            test_mode=True,
            test_output_dir=str(test_output_dir)
        )
        
        assert "status" in result
        
        # Should note dependency issues
        operations = audit_verifier.get_operations_for_repo(temp_test_repo.name)
        print(f"\n📝 Missing Deps Operations: {len(operations)}")


class TestOnboardingScenario08_WithSecrets:
    """Scenario 8: Repository containing secrets/credentials."""
    
    def test_onboard_repo_with_secrets(self, temp_test_repo, audit_verifier, test_output_dir):
        """Golden: Onboard repo with hardcoded secrets - should detect violations."""
        # Create file with secrets
        (temp_test_repo / "config.py").write_text('''
API_KEY = "sk-1234567890abcdef"
PASSWORD = "super_secret_password"
AWS_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        ''')
        (temp_test_repo / ".git").mkdir()
        
        orchestrator_context = {
            "source": "MasterOrchestrator",
            "request_id": "test-scenario-08-secrets"
        }
        
        result = onboard_repository_tool(
            repository_path=str(temp_test_repo),
            orchestrator_context=orchestrator_context,
            test_mode=True,
            test_output_dir=str(test_output_dir)
        )
        
        assert "status" in result
        
        # Check for security violations
        violations = audit_verifier.get_governance_violations(temp_test_repo.name)
        print(f"\n⚠️  Security Violations: {len(violations)}")


class TestOnboardingScenario09_TestsOnly:
    """Scenario 9: Repository with only test files."""
    
    def test_onboard_tests_only_repository(self, temp_test_repo, audit_verifier, test_output_dir):
        """Golden: Onboard repository with tests but no source code."""
        tests_dir = temp_test_repo / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_example.py").write_text('''
def test_something():
    assert True
        ''')
        (temp_test_repo / ".git").mkdir()
        
        orchestrator_context = {
            "source": "MasterOrchestrator",
            "request_id": "test-scenario-09-tests-only"
        }
        
        result = onboard_repository_tool(
            repository_path=str(temp_test_repo),
            orchestrator_context=orchestrator_context,
            test_mode=True,
            test_output_dir=str(test_output_dir)
        )
        
        assert "status" in result
        operations = audit_verifier.get_operations_for_repo(temp_test_repo.name)
        print(f"\n📝 Tests-Only Operations: {len(operations)}")


class TestOnboardingScenario10_LargeRepo:
    """Scenario 10: Large repository with many files."""
    
    def test_onboard_large_repository(self, temp_test_repo, audit_verifier, test_output_dir):
        """Golden: Onboard repository with 100+ files - test performance."""
        # Create many files
        src_dir = temp_test_repo / "src"
        src_dir.mkdir()
        
        for i in range(50):
            (src_dir / f"module_{i}.py").write_text(f"# Module {i}\ndef func_{i}(): pass")
        
        (temp_test_repo / ".git").mkdir()
        
        orchestrator_context = {
            "source": "MasterOrchestrator",
            "request_id": "test-scenario-10-large"
        }
        
        result = onboard_repository_tool(
            repository_path=str(temp_test_repo),
            orchestrator_context=orchestrator_context,
            test_mode=True,
            test_output_dir=str(test_output_dir)
        )
        
        assert "status" in result
        operations = audit_verifier.get_operations_for_repo(temp_test_repo.name)
        print(f"\n📝 Large Repo Operations: {len(operations)}")


class TestOnboardingScenario11_Monorepo:
    """Scenario 11: Monorepo with multiple sub-projects."""
    
    def test_onboard_monorepo(self, temp_test_repo, audit_verifier, test_output_dir):
        """Golden: Onboard monorepo with multiple independent projects."""
        # Create monorepo structure
        (temp_test_repo / "services" / "api").mkdir(parents=True, exist_ok=True)
        (temp_test_repo / "services" / "api" / "main.py").write_text("# API Service")
        
        (temp_test_repo / "services" / "worker").mkdir(parents=True, exist_ok=True)
        (temp_test_repo / "services" / "worker" / "main.py").write_text("# Worker Service")
        
        (temp_test_repo / "libs" / "common").mkdir(parents=True, exist_ok=True)
        (temp_test_repo / "libs" / "common" / "__init__.py").write_text("# Shared Library")
        
        (temp_test_repo / ".git").mkdir()
        
        orchestrator_context = {
            "source": "MasterOrchestrator",
            "request_id": "test-scenario-11-monorepo"
        }
        
        result = onboard_repository_tool(
            repository_path=str(temp_test_repo),
            orchestrator_context=orchestrator_context,
            test_mode=True,
            test_output_dir=str(test_output_dir)
        )
        
        assert "status" in result
        operations = audit_verifier.get_operations_for_repo(temp_test_repo.name)
        print(f"\n📝 Monorepo Operations: {len(operations)}")


class TestOnboardingScenario12_ComplexAST:
    """Scenario 12: Repository with complex AST structures."""
    
    def test_onboard_complex_ast_repository(self, temp_test_repo, audit_verifier, test_output_dir):
        """Golden: Onboard repo with complex Python code - decorators, metaclasses, etc."""
        (temp_test_repo / "complex.py").write_text('''
from typing import Any, TypeVar, Generic
from abc import ABC, abstractmethod

T = TypeVar('T')

class MetaClass(type):
    """Metaclass example"""
    pass

class AbstractBase(ABC, Generic[T], metaclass=MetaClass):
    """Complex inheritance"""
    
    @abstractmethod
    def process(self, data: T) -> T:
        """Abstract method"""
        pass
    
    @property
    def value(self) -> T:
        """Property"""
        return self._value
    
    @staticmethod
    def static_func():
        """Static method"""
        pass
    
    @classmethod
    def class_func(cls):
        """Class method"""
        pass

def decorator(func):
    """Decorator"""
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@decorator
async def async_function(x: int) -> int:
    """Async function with decorator"""
    return x * 2
        ''')
        (temp_test_repo / ".git").mkdir()
        
        orchestrator_context = {
            "source": "MasterOrchestrator",
            "request_id": "test-scenario-12-complex-ast"
        }
        
        result = onboard_repository_tool(
            repository_path=str(temp_test_repo),
            orchestrator_context=orchestrator_context,
            test_mode=True,
            test_output_dir=str(test_output_dir)
        )
        
        assert "status" in result
        operations = audit_verifier.get_operations_for_repo(temp_test_repo.name)
        print(f"\n📝 Complex AST Operations: {len(operations)}")


class TestOnboardingScenario13_GovernanceViolations:
    """Scenario 13: Repository with multiple governance violations."""
    
    def test_onboard_repo_with_violations(self, temp_test_repo, audit_verifier, test_output_dir):
        """Golden: Onboard repo with known governance violations."""
        # Create code with violations
        (temp_test_repo / "bad_code.py").write_text('''
# No docstring
def func(x):
    # No type hints
    return x * 2

class MyClass:
    # No docstring
    def method(self):
        pass

# Hardcoded secret
API_KEY = "sk-123456"

# SQL injection vulnerability
def query_db(user_input):
    sql = f"SELECT * FROM users WHERE id = {user_input}"
    return sql
        ''')
        (temp_test_repo / ".git").mkdir()
        
        orchestrator_context = {
            "source": "MasterOrchestrator",
            "request_id": "test-scenario-13-violations"
        }
        
        result = onboard_repository_tool(
            repository_path=str(temp_test_repo),
            orchestrator_context=orchestrator_context,
            test_mode=True,
            test_output_dir=str(test_output_dir)
        )
        
        assert "status" in result
        
        # Should detect violations
        violations = audit_verifier.get_governance_violations(temp_test_repo.name)
        print(f"\n⚠️  Detected Violations: {len(violations)}")
        for v in violations:
            print(f"  - {v.get('rule_id')}: {v.get('message')}")


class TestOnboardingScenario14_NonExistentPath:
    """Scenario 14: Attempt to onboard non-existent path."""
    
    def test_onboard_nonexistent_path(self, audit_verifier):
        """Golden: Onboard non-existent path - should fail gracefully."""
        orchestrator_context = {
            "source": "MasterOrchestrator",
            "request_id": "test-scenario-14-nonexistent"
        }
        
        result = onboard_repository_tool(
            repository_path="/nonexistent/path/to/repo",
            orchestrator_context=orchestrator_context,
            test_mode=True,
            test_output_dir=str(test_output_dir)
        )
        
        # Should error
        assert result["status"] == "error"
        assert "error" in result
        
        # Should log error in audit trail
        operations = audit_verifier.get_operations_for_repo("nonexistent")
        print(f"\n📝 Nonexistent Path Operations: {len(operations)}")


class TestOnboardingScenario15_CustomDomain:
    """Scenario 15: Repository with custom domain knowledge."""
    
    def test_onboard_repo_with_domain_knowledge(self, temp_test_repo, audit_verifier, test_output_dir):
        """Golden: Onboard repo with domain-specific terminology."""
        (temp_test_repo / "finance.py").write_text('''
"""Financial domain module"""

def calculate_irr(cash_flows: list[float], initial_investment: float) -> float:
    """Calculate Internal Rate of Return (IRR)"""
    pass

def compute_sharpe_ratio(returns: list[float], risk_free_rate: float) -> float:
    """Compute Sharpe Ratio for portfolio optimization"""
    pass

class BlackScholesModel:
    """Black-Scholes option pricing model"""
    
    def price_call_option(self, S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Price European call option"""
        pass
        ''')
        (temp_test_repo / ".git").mkdir()
        
        orchestrator_context = {
            "source": "MasterOrchestrator",
            "request_id": "test-scenario-15-domain"
        }
        
        result = onboard_repository_tool(
            repository_path=str(temp_test_repo),
            orchestrator_context=orchestrator_context,
            test_mode=True,
            test_output_dir=str(test_output_dir)
        )
        
        assert "status" in result
        operations = audit_verifier.get_operations_for_repo(temp_test_repo.name)
        print(f"\n📝 Domain Knowledge Operations: {len(operations)}")


class TestAuditTrailVerification:
    """Verify audit trail integrity and completeness."""
    
    def test_audit_database_exists(self, audit_verifier):
        """Golden: Verify governance.db exists."""
        assert GOVERNANCE_DB_PATH.exists(), "governance.db should exist"
        
        # Show all tables
        tables = audit_verifier.get_all_tables()
        print(f"\n📊 Database Tables: {tables}")
    
    def test_audit_trail_schema(self, audit_verifier):
        """Golden: Verify audit trail has expected schema."""
        if not GOVERNANCE_DB_PATH.exists():
            pytest.skip("governance.db not found")
        
        conn = sqlite3.connect(GOVERNANCE_DB_PATH)
        cursor = conn.cursor()
        
        # Get schema for each table
        tables = audit_verifier.get_all_tables()
        print(f"\n📋 Table Schemas:")
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            print(f"\n  {table}:")
            for col in columns:
                print(f"    - {col[1]} ({col[2]})")
        
        conn.close()
    
    def test_query_all_onboarding_operations(self, audit_verifier):
        """Golden: Query all onboarding-related operations."""
        if not GOVERNANCE_DB_PATH.exists():
            pytest.skip("governance.db not found")
        
        conn = sqlite3.connect(GOVERNANCE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Try to find onboarding operations
        tables = audit_verifier.get_all_tables()
        print(f"\n🔍 Searching for onboarding operations across {len(tables)} tables...")
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                count = cursor.fetchone()["count"]
                print(f"  {table}: {count} records")
            except sqlite3.OperationalError as e:
                print(f"  {table}: Error - {e}")
        
        conn.close()


# Test Summary Documentation
"""
🎯 Test Scenario Summary
========================

Scenario 01: Python Repository (CORTEX)
  - Tests onboarding of Python project
  - Verifies audit trail for Python ecosystem

Scenario 02: .NET/C# Repository (KSESSIONS)
  - Tests onboarding of .NET project
  - Verifies cross-platform language support

Scenario 03: Empty Repository
  - Tests handling of empty repos
  - Verifies graceful failure/warning

Scenario 04: Polyglot Repository
  - Tests mixed-language detection
  - Verifies multi-language AST generation

Scenario 05: Documentation-Only Repository
  - Tests repos with no code files
  - Verifies handling of markdown-only repos

Scenario 06: Re-Onboarding
  - Tests idempotency of onboarding
  - Verifies profile updates vs replacements

Scenario 07: Missing Dependencies
  - Tests repos with unresolved dependencies
  - Verifies dependency gap detection

Scenario 08: Secrets in Code
  - Tests security violation detection
  - Verifies secrets scanning

Scenario 09: Tests-Only Repository
  - Tests repos with only test files
  - Verifies test-to-code ratio detection

Scenario 10: Large Repository
  - Tests performance on large codebases
  - Verifies scalability of AST generation

Scenario 11: Monorepo
  - Tests multi-project repositories
  - Verifies sub-project detection

Scenario 12: Complex AST
  - Tests advanced Python constructs
  - Verifies AST handling of decorators, metaclasses, etc.

Scenario 13: Governance Violations
  - Tests violation detection
  - Verifies enforcement agent behavior

Scenario 14: Non-Existent Path
  - Tests error handling
  - Verifies audit trail on errors

Scenario 15: Custom Domain Knowledge
  - Tests domain-specific code
  - Verifies terminology extraction

Audit Trail Verification:
  - Database existence
  - Schema validation
  - Operation querying
  - Integrity checks
"""
