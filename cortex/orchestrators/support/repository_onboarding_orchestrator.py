"""
RepositoryOnboardingOrchestrator — Scans and onboards external repositories.

Phase 28.2: Repository scanning, profile generation, and domain detection.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class RepositoryNotFoundError(FileNotFoundError):
    """Raised when the target repository path does not exist."""


class RepositoryOnboardingOrchestrator:
    """Orchestrates the onboarding of an external repository into CORTEX."""

    def scan_repository(self, repo_path: "str | Path") -> Dict[str, Any]:
        """Scan repository structure and detect tech stack."""
        root = Path(repo_path)
        if not root.exists():
            raise RepositoryNotFoundError(f"Repository not found: {repo_path}")

        py_files = list(root.rglob("*.py"))
        ts_files = list(root.rglob("*.ts"))
        js_files = list(root.rglob("*.js"))
        go_files = list(root.rglob("*.go"))
        java_files = list(root.rglob("*.java"))

        structure = {
            "python_files": len(py_files),
            "ts_files": len(ts_files),
            "js_files": len(js_files),
            "go_files": len(go_files),
            "java_files": len(java_files),
            "total_files": sum(
                len(f) for f in (py_files, ts_files, js_files, go_files, java_files)
            ),
        }

        tech_stack: List[str] = []
        if py_files:
            tech_stack.append("python")
        if ts_files:
            tech_stack.append("typescript")
        if js_files:
            tech_stack.append("javascript")
        if go_files:
            tech_stack.append("go")
        if java_files:
            tech_stack.append("java")

        return {
            "status": "success",
            "repo_path": str(repo_path),
            "structure": structure,
            "tech_stack": tech_stack,
        }

    def detect_company_domains(
        self, repo_path: "str | Path"
    ) -> Tuple[bool, Optional[Path], List[str]]:
        """Detect company domain structure. Returns (has_domains, domains_path, detected_domains)."""
        root = Path(repo_path)
        if not root.exists():
            return False, None, []
        company_dir = root / "company" / "domains"
        if company_dir.exists():
            domains = [d.name for d in company_dir.iterdir() if d.is_dir()]
            return True, company_dir, domains
        # Alternative: top-level directories named like domains
        domains = []
        return False, None, domains

    def analyze_tech_stack(self, repo_path: "str | Path") -> Dict[str, Any]:
        """Identify languages, frameworks, and dependencies."""
        root = Path(repo_path)
        languages: List[str] = []
        frameworks: List[str] = []

        if root.exists():
            if list(root.rglob("*.py")):
                languages.append("Python")
            if list(root.rglob("*.ts")):
                languages.append("TypeScript")
            if list(root.rglob("*.js")):
                languages.append("JavaScript")
            if list(root.rglob("*.go")):
                languages.append("Go")
            if (root / "requirements.txt").exists():
                frameworks.append("pip")
            if (root / "package.json").exists():
                frameworks.append("npm/node")
            if (root / "pyproject.toml").exists():
                frameworks.append("pyproject")

        primary = languages[0] if languages else "unknown"
        return {
            "primary_language": primary,
            "languages": languages,
            "frameworks": frameworks,
        }

    def generate_profile(self, repo_path: "str | Path") -> "Any":
        """Generate a RepositoryProfile from scan results."""
        from cortex.intelligence.onboarded_repos import RepositoryProfile
        root = Path(repo_path)
        scan = self.scan_repository(root)
        return RepositoryProfile(
            name=root.name,
            path=str(root),
            onboarded_at=datetime.utcnow(),
        )

    def onboard_repository_with_profile(
        self,
        repo_path: "str | Path",
        profile_store: "Any",
    ) -> "Any":
        """Full onboarding: scan → profile → save."""
        profile = self.generate_profile(repo_path)
        profile_store.save(profile)
        return profile

    def assess_security_baseline(
        self, repo_path: "str | Path"
    ) -> Dict[str, Any]:
        """Assess basic security posture of the repository."""
        root = Path(repo_path)
        issues: List[str] = []
        vulnerabilities: List[str] = []

        if root.exists():
            if not (root / ".gitignore").exists():
                issues.append("missing .gitignore")
            for sensitive in ("secrets.py", "credentials.py", ".env"):
                if (root / sensitive).exists():
                    issues.append(f"potential sensitive file: {sensitive}")
                    vulnerabilities.append(sensitive)

        return {
            "status": "success",
            "issues": issues,
            "severity": "high" if vulnerabilities else "low",
            "baseline_passed": len(issues) == 0,
            "secrets_management": "gitignore" if (root / ".gitignore").exists() else "none",
            "vulnerabilities_detected": vulnerabilities,
        }

    def extract_standards(
        self, repo_path: "str | Path"
    ) -> Dict[str, Any]:
        """Extract coding standards from the repository."""
        root = Path(repo_path)
        standards: List[str] = []
        test_patterns: List[str] = []
        coding_style: List[str] = []

        if root.exists():
            if (root / "pyproject.toml").exists():
                standards.append("pyproject.toml")
                coding_style.append("pyproject")
            if (root / ".flake8").exists() or (root / "setup.cfg").exists():
                standards.append("flake8")
                coding_style.append("flake8")
            if list(root.rglob("test_*.py")) or list(root.rglob("*_test.py")):
                test_patterns.append("pytest")

        return {
            "status": "success",
            "standards": standards,
            "coding_style": coding_style,
            "test_patterns": test_patterns,
            "count": len(standards),
        }

    def detect_test_framework(
        self, repo_path: "str | Path"
    ) -> Dict[str, Any]:
        """Detect test framework used in the repository."""
        root = Path(repo_path)
        framework = "unknown"
        has_tests = False

        if root.exists():
            test_files = list(root.rglob("test_*.py")) + list(root.rglob("*_test.py"))
            has_tests = len(test_files) > 0
            if (root / "pytest.ini").exists() or (root / "pyproject.toml").exists():
                framework = "pytest"
            elif test_files:
                framework = "pytest"  # default assumption

        return {
            "has_tests": has_tests,
            "test_framework": framework,
            "test_file_count": len(list(root.rglob("test_*.py"))) if root.exists() else 0,
        }

    def analyze_dependencies(
        self, repo_path: "str | Path"
    ) -> List[str]:
        """Parse dependencies from requirements.txt, pyproject.toml, package.json."""
        root = Path(repo_path)
        deps: List[str] = []

        if not root.exists():
            return deps

        req_file = root / "requirements.txt"
        if req_file.exists():
            for line in req_file.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    deps.append(line.split("==")[0].split(">=")[0].strip())

        return deps



class RepositoryOnboardingOrchestrator:
    """Orchestrates the onboarding of an external repository into CORTEX."""

    def scan_repository(self, repo_path: "str | Path") -> Dict[str, Any]:
        """Scan repository structure and detect tech stack."""
        root = Path(repo_path)
        structure: Dict[str, Any] = {}
        tech_stack: List[str] = []
        languages: List[str] = []

        if root.exists():
            py_files = list(root.rglob("*.py"))
            ts_files = list(root.rglob("*.ts"))
            js_files = list(root.rglob("*.js"))
            go_files = list(root.rglob("*.go"))
            java_files = list(root.rglob("*.java"))

            structure = {
                "python_files": len(py_files),
                "ts_files": len(ts_files),
                "js_files": len(js_files),
                "go_files": len(go_files),
                "java_files": len(java_files),
                "total_files": sum(
                    len(f) for f in (py_files, ts_files, js_files, go_files, java_files)
                ),
            }

            if py_files:
                tech_stack.append("python")
                languages.append("Python")
            if ts_files:
                tech_stack.append("typescript")
                languages.append("TypeScript")
            if js_files:
                tech_stack.append("javascript")
                languages.append("JavaScript")
            if go_files:
                tech_stack.append("go")
                languages.append("Go")
            if java_files:
                tech_stack.append("java")
                languages.append("Java")

            # Detect frameworks
            if (root / "requirements.txt").exists() or (root / "pyproject.toml").exists():
                tech_stack.append("pip")
            if (root / "package.json").exists():
                tech_stack.append("npm")

        return {
            "status": "success",
            "repo_path": str(repo_path),
            "structure": structure,
            "tech_stack": tech_stack,
            "languages": languages,
        }

    def detect_company_domains(
        self, repo_path: "str | Path"
    ) -> Dict[str, Any]:
        """Detect company domain structure from repository layout."""
        root = Path(repo_path)
        domains: List[str] = []

        if root.exists():
            for item in root.iterdir():
                if item.is_dir() and not item.name.startswith("."):
                    domains.append(item.name)

        return {
            "status": "success",
            "domains": domains,
            "count": len(domains),
        }

    def generate_profile(
        self, scan_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate an onboarding profile from scan results."""
        return {
            "status": "success",
            "profile": {
                "tech_stack": scan_results.get("tech_stack", []),
                "languages": scan_results.get("languages", []),
                "structure": scan_results.get("structure", {}),
                "onboarded": True,
            },
        }

    def assess_security_baseline(
        self, repo_path: "str | Path"
    ) -> Dict[str, Any]:
        """Assess basic security posture of the repository."""
        root = Path(repo_path)
        issues: List[str] = []

        if root.exists():
            # Check for common security indicators
            if not (root / ".gitignore").exists():
                issues.append("missing .gitignore")
            for sensitive in ("secrets.py", "credentials.py", ".env"):
                if (root / sensitive).exists():
                    issues.append(f"potential sensitive file: {sensitive}")

        return {
            "status": "success",
            "issues": issues,
            "severity": "high" if any("credential" in i for i in issues) else "low",
            "baseline_passed": len(issues) == 0,
        }

    def extract_standards(
        self, repo_path: "str | Path"
    ) -> Dict[str, Any]:
        """Extract coding standards from the repository."""
        root = Path(repo_path)
        standards: List[str] = []

        if root.exists():
            if (root / "pyproject.toml").exists():
                standards.append("pyproject.toml")
            if (root / ".flake8").exists() or (root / "setup.cfg").exists():
                standards.append("flake8")
            if (root / ".eslintrc.json").exists() or (root / ".eslintrc.js").exists():
                standards.append("eslint")

        return {
            "status": "success",
            "standards": standards,
            "count": len(standards),
        }
