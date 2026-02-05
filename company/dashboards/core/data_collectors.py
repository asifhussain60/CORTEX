"""
Data Collectors for Static Dashboard Generator
Phase 23.2: Comprehensive data collection for all 13 dashboard tabs

Each collector follows a consistent pattern:
1. Input: Repository path or data source
2. Processing: Analysis, metrics, patterns
3. Output: Structured data (dict/list) ready for JSON embedding

Reference: Phase 23 spec lines 258-276 (data_embedding.schema)
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import json


# ============================================================================
# OVERVIEW TAB
# ============================================================================

class OverviewCollector:
    """Collect overview metrics: health score, file counts, LOC, test coverage."""
    
    def collect(self, repo_path: Path) -> Dict[str, Any]:
        """
        Returns:
            {
                "health_score": float (0-100),
                "file_count": int,
                "loc_total": int,
                "loc_python": int,
                "test_coverage": float (0-100),
                "contributors": int,
                "last_commit": str (ISO 8601),
                "primary_language": str
            }
        """
        python_files = list(repo_path.glob("**/*.py"))
        test_files = [f for f in python_files if "test" in f.stem.lower()]
        
        loc_total = sum(len(f.read_text(errors="ignore").splitlines()) for f in python_files)
        loc_python = loc_total
        
        # Simple health score heuristic (can be refined)
        has_tests = len(test_files) > 0
        test_ratio = len(test_files) / len(python_files) if python_files else 0
        health_score = 50.0 + (test_ratio * 50)  # Base 50 + test coverage bonus
        
        return {
            "health_score": round(health_score, 1),
            "file_count": len(python_files),
            "loc_total": loc_total,
            "loc_python": loc_python,
            "test_coverage": round(test_ratio * 100, 1),
            "contributors": 0,  # Requires git log parsing
            "last_commit": datetime.now().isoformat(),
            "primary_language": "Python"
        }


# ============================================================================
# ARCHITECTURE TAB
# ============================================================================

class ArchitectureCollector:
    """Collect architecture data: structure tree, dependency graph, module stats."""
    
    def collect(self, repo_path: Path) -> Dict[str, Any]:
        """
        Returns:
            {
                "structure_tree": list (directory tree),
                "dependency_graph": dict (module -> [dependencies]),
                "module_stats": list (per-module metrics),
                "layers": list (detected layers)
            }
        """
        structure_tree = self._build_structure_tree(repo_path)
        module_stats = self._collect_module_stats(repo_path)
        layers = self._detect_layers(repo_path)
        
        return {
            "structure_tree": structure_tree,
            "dependency_graph": {},  # Requires import parsing
            "module_stats": module_stats,
            "layers": layers
        }
    
    def _build_structure_tree(self, repo_path: Path) -> List[Dict]:
        """Build directory tree representation."""
        tree = []
        for item in sorted(repo_path.iterdir()):
            if item.name.startswith(".") or item.name == "__pycache__":
                continue
            
            node = {
                "name": item.name,
                "type": "directory" if item.is_dir() else "file",
                "path": str(item.relative_to(repo_path))
            }
            
            if item.is_dir():
                # Count files in directory
                py_files = list(item.glob("**/*.py"))
                node["file_count"] = len(py_files)
                node["loc"] = sum(len(f.read_text(errors="ignore").splitlines()) for f in py_files)
            
            tree.append(node)
        
        return tree
    
    def _collect_module_stats(self, repo_path: Path) -> List[Dict]:
        """Collect per-module statistics."""
        modules = []
        for py_file in repo_path.glob("**/*.py"):
            if "test" in py_file.stem.lower():
                continue
            
            content = py_file.read_text(errors="ignore")
            lines = content.splitlines()
            
            modules.append({
                "name": py_file.stem,
                "path": str(py_file.relative_to(repo_path)),
                "loc": len(lines),
                "functions": content.count("def "),
                "classes": content.count("class ")
            })
        
        return modules
    
    def _detect_layers(self, repo_path: Path) -> List[str]:
        """Detect architectural layers (controller, service, repository, etc.)."""
        layers = set()
        
        for py_file in repo_path.glob("**/*.py"):
            path_parts = py_file.parts
            for part in path_parts:
                if part in ["api", "controllers", "views"]:
                    layers.add("Presentation")
                elif part in ["services", "business", "logic"]:
                    layers.add("Business Logic")
                elif part in ["repositories", "dao", "models"]:
                    layers.add("Data Access")
                elif part in ["infrastructure", "config"]:
                    layers.add("Infrastructure")
        
        return sorted(layers)


# ============================================================================
# QUALITY TAB
# ============================================================================

class QualityCollector:
    """Collect quality metrics: complexity, code smells, duplication."""
    
    def collect(self, repo_path: Path) -> Dict[str, Any]:
        """
        Returns:
            {
                "complexity_metrics": dict (avg/max complexity per file),
                "code_smells": list (smell type, location, severity),
                "duplication_ratio": float (0-100),
                "maintainability_index": float (0-100)
            }
        """
        python_files = list(repo_path.glob("**/*.py"))
        
        complexity = self._calculate_complexity(python_files)
        code_smells = self._detect_code_smells(python_files)
        duplication_ratio = self._estimate_duplication(python_files)
        
        return {
            "complexity_metrics": complexity,
            "code_smells": code_smells,
            "duplication_ratio": round(duplication_ratio, 2),
            "maintainability_index": self._calculate_maintainability_index(complexity, code_smells, duplication_ratio)
        }
    
    def _calculate_complexity(self, files: List[Path]) -> Dict[str, Any]:
        """Simple cyclomatic complexity estimate (count branches)."""
        total_branches = 0
        max_complexity_file = None
        max_complexity = 0
        
        for f in files:
            content = f.read_text(errors="ignore")
            branches = (
                content.count("if ") + 
                content.count("elif ") + 
                content.count("for ") + 
                content.count("while ") + 
                content.count("except ")
            )
            total_branches += branches
            
            if branches > max_complexity:
                max_complexity = branches
                max_complexity_file = f.name
        
        return {
            "average": round(total_branches / len(files), 1) if files else 0,
            "max": max_complexity,
            "max_file": max_complexity_file
        }
    
    def _detect_code_smells(self, files: List[Path]) -> List[Dict]:
        """Detect common code smells."""
        smells = []
        
        for f in files:
            content = f.read_text(errors="ignore")
            lines = content.splitlines()
            
            # Long file smell
            if len(lines) > 500:
                smells.append({
                    "type": "Long File",
                    "file": f.name,
                    "severity": "Medium",
                    "metric": f"{len(lines)} lines"
                })
            
            # Too many functions
            func_count = content.count("def ")
            if func_count > 30:
                smells.append({
                    "type": "Too Many Functions",
                    "file": f.name,
                    "severity": "Medium",
                    "metric": f"{func_count} functions"
                })
        
        return smells
    
    def _estimate_duplication(self, files: List[Path]) -> float:
        """Estimate code duplication ratio (simple line-based)."""
        all_lines = []
        for f in files:
            lines = f.read_text(errors="ignore").splitlines()
            all_lines.extend([line.strip() for line in lines if line.strip() and not line.strip().startswith("#")])
        
        if not all_lines:
            return 0.0
        
        unique_lines = len(set(all_lines))
        duplication_ratio = (1 - unique_lines / len(all_lines)) * 100
        return duplication_ratio
    
    def _calculate_maintainability_index(self, complexity: Dict, smells: List[Dict], duplication: float) -> float:
        """Calculate maintainability index (0-100, higher is better)."""
        # Simple heuristic
        base_score = 100
        base_score -= complexity["average"] * 2  # Penalize complexity
        base_score -= len(smells) * 5  # Penalize smells
        base_score -= duplication * 0.5  # Penalize duplication
        return max(0, min(100, base_score))


# ============================================================================
# VULNERABILITIES TAB
# ============================================================================

class VulnerabilitiesCollector:
    """Collect vulnerability data: CVE list, severity counts, risk score."""
    
    def collect(self, repo_path: Path) -> Dict[str, Any]:
        """
        Returns:
            {
                "cve_list": list (CVE-ID, severity, description),
                "severity_counts": dict (critical/high/medium/low counts),
                "risk_score": float (0-100),
                "last_scan": str (ISO 8601)
            }
        """
        # Placeholder: Real implementation would use security scanners
        return {
            "cve_list": [],
            "severity_counts": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "risk_score": 0.0,
            "last_scan": datetime.now().isoformat()
        }


# ============================================================================
# SECURITY TAB
# ============================================================================

class SecurityCollector:
    """Collect security data: OWASP compliance, secret detection, access patterns."""
    
    def collect(self, repo_path: Path) -> Dict[str, Any]:
        """
        Returns:
            {
                "owasp_compliance": dict (Top 10 compliance status),
                "secrets_detected": list (type, location, severity),
                "access_patterns": list (auth mechanisms),
                "security_score": float (0-100)
            }
        """
        secrets = self._detect_secrets(repo_path)
        
        return {
            "owasp_compliance": self._check_owasp_compliance(),
            "secrets_detected": secrets,
            "access_patterns": [],
            "security_score": 100 - len(secrets) * 10  # Simple scoring
        }
    
    def _detect_secrets(self, repo_path: Path) -> List[Dict]:
        """Detect potential hardcoded secrets."""
        secrets = []
        patterns = ["password", "api_key", "secret", "token"]
        
        for py_file in repo_path.glob("**/*.py"):
            content = py_file.read_text(errors="ignore")
            for pattern in patterns:
                if pattern in content.lower() and "=" in content:
                    secrets.append({
                        "type": pattern,
                        "file": py_file.name,
                        "severity": "High"
                    })
        
        return secrets
    
    def _check_owasp_compliance(self) -> Dict[str, str]:
        """Check OWASP Top 10 compliance."""
        return {
            "A01-Broken_Access_Control": "Unknown",
            "A02-Cryptographic_Failures": "Unknown",
            "A03-Injection": "Unknown",
            "A04-Insecure_Design": "Unknown",
            "A05-Security_Misconfiguration": "Unknown",
            "A06-Vulnerable_Components": "Unknown",
            "A07-Authentication_Failures": "Unknown",
            "A08-Data_Integrity_Failures": "Unknown",
            "A09-Logging_Failures": "Unknown",
            "A10-SSRF": "Unknown"
        }


# ============================================================================
# DEPENDENCIES TAB
# ============================================================================

class DependenciesCollector:
    """Collect dependency data: package analysis, version status, license compliance."""
    
    def collect(self, repo_path: Path) -> Dict[str, Any]:
        """
        Returns:
            {
                "packages": list (name, version, license),
                "outdated": list (packages needing updates),
                "license_compliance": dict (license type counts),
                "dependency_graph": dict (package -> dependencies)
            }
        """
        packages = self._parse_requirements(repo_path)
        
        return {
            "packages": packages,
            "outdated": [],
            "license_compliance": self._analyze_licenses(packages),
            "dependency_graph": {}
        }
    
    def _parse_requirements(self, repo_path: Path) -> List[Dict]:
        """Parse requirements.txt for package list."""
        packages = []
        req_file = repo_path / "requirements.txt"
        
        if req_file.exists():
            for line in req_file.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                # Parse package==version
                if "==" in line:
                    name, version = line.split("==", 1)
                else:
                    name, version = line, "latest"
                
                packages.append({
                    "name": name,
                    "version": version,
                    "license": "Unknown"
                })
        
        return packages
    
    def _analyze_licenses(self, packages: List[Dict]) -> Dict[str, int]:
        """Count license types."""
        licenses = {}
        for pkg in packages:
            license_type = pkg.get("license", "Unknown")
            licenses[license_type] = licenses.get(license_type, 0) + 1
        return licenses


# ============================================================================
# TESTING TAB
# ============================================================================

class TestingCollector:
    """Collect testing data: coverage report, test pyramid, mutation testing."""
    
    def collect(self, repo_path: Path) -> Dict[str, Any]:
        """
        Returns:
            {
                "coverage": dict (line/branch coverage %),
                "test_pyramid": dict (unit/integration/e2e counts),
                "test_files": list (test file metadata),
                "mutation_score": float (0-100)
            }
        """
        test_files = list(repo_path.glob("**/test_*.py"))
        all_files = list(repo_path.glob("**/*.py"))
        
        coverage = len(test_files) / len(all_files) * 100 if all_files else 0
        
        return {
            "coverage": {
                "line": round(coverage, 1),
                "branch": 0
            },
            "test_pyramid": self._analyze_test_pyramid(test_files),
            "test_files": [{"name": f.name, "loc": len(f.read_text(errors="ignore").splitlines())} for f in test_files],
            "mutation_score": 0
        }
    
    def _analyze_test_pyramid(self, test_files: List[Path]) -> Dict[str, int]:
        """Categorize tests into unit/integration/e2e."""
        pyramid = {"unit": 0, "integration": 0, "e2e": 0}
        
        for f in test_files:
            if "unit" in str(f):
                pyramid["unit"] += 1
            elif "integration" in str(f):
                pyramid["integration"] += 1
            elif "e2e" in str(f) or "end_to_end" in str(f):
                pyramid["e2e"] += 1
            else:
                pyramid["unit"] += 1  # Default to unit
        
        return pyramid


# ============================================================================
# PATTERNS TAB
# ============================================================================

class PatternsCollector:
    """Collect design patterns: detected patterns, anti-patterns, refactoring candidates."""
    
    def collect(self, repo_path: Path) -> Dict[str, Any]:
        """
        Returns:
            {
                "design_patterns": list (pattern name, locations),
                "anti_patterns": list (anti-pattern name, locations),
                "refactoring_candidates": list (smell, file, reason)
            }
        """
        return {
            "design_patterns": self._detect_design_patterns(repo_path),
            "anti_patterns": [],
            "refactoring_candidates": []
        }
    
    def _detect_design_patterns(self, repo_path: Path) -> List[Dict]:
        """Detect common design patterns (simple heuristics)."""
        patterns = []
        
        for py_file in repo_path.glob("**/*.py"):
            content = py_file.read_text(errors="ignore")
            
            # Singleton pattern
            if "def __new__" in content and "_instance" in content:
                patterns.append({
                    "pattern": "Singleton",
                    "file": py_file.name,
                    "confidence": "Medium"
                })
            
            # Factory pattern
            if "Factory" in py_file.stem or "def create_" in content:
                patterns.append({
                    "pattern": "Factory",
                    "file": py_file.name,
                    "confidence": "Medium"
                })
        
        return patterns


# ============================================================================
# REMAINING COLLECTORS (Stubs)
# ============================================================================

class VendorsCollector:
    """Collect third-party vendor data."""
    def collect(self, repo_path: Path) -> Dict[str, Any]:
        return {"vendors": [], "sdks": [], "integrations": []}


class UseCasesCollector:
    """Collect use case data."""
    def collect(self, repo_path: Path) -> Dict[str, Any]:
        return {"features": [], "user_journeys": [], "api_endpoints": []}


class TimelineCollector:
    """Collect timeline data (requires git)."""
    def collect(self, repo_path: Path) -> Dict[str, Any]:
        return {"commits": [], "releases": [], "burndown": []}


class ImpactCollector:
    """Collect change impact data."""
    def collect(self, repo_path: Path) -> Dict[str, Any]:
        return {"recent_changes": [], "blast_radius": {}, "risk_assessment": {}}


class DatabaseCollector:
    """Collect database schema data."""
    def collect(self, repo_path: Path) -> Dict[str, Any]:
        return {"schemas": [], "tables": [], "queries": [], "performance": {}}


# ============================================================================
# ORCHESTRATOR
# ============================================================================

class ComprehensiveDataCollector:
    """Orchestrate all data collectors for comprehensive dashboard data."""
    
    def __init__(self):
        self.collectors = {
            "overview": OverviewCollector(),
            "architecture": ArchitectureCollector(),
            "quality": QualityCollector(),
            "vulnerabilities": VulnerabilitiesCollector(),
            "security": SecurityCollector(),
            "dependencies": DependenciesCollector(),
            "testing": TestingCollector(),
            "patterns": PatternsCollector(),
            "vendors": VendorsCollector(),
            "usecases": UseCasesCollector(),
            "timeline": TimelineCollector(),
            "impact": ImpactCollector(),
            "database": DatabaseCollector()
        }
    
    def collect_all(self, repo_path: Path) -> Dict[str, Any]:
        """
        Collect data from all collectors.
        
        Returns:
            {
                "overview": {...},
                "architecture": {...},
                "quality": {...},
                ...
            }
        """
        data = {}
        for section, collector in self.collectors.items():
            try:
                data[section] = collector.collect(repo_path)
            except Exception as e:
                # Graceful degradation
                data[section] = {"error": str(e)}
        
        return data
