"""
Test suite for DependencyAnalyzer.

Tests package dependency analysis, vulnerability detection, license checking,
and support for multiple package managers (Python, Node.js, Java, .NET).

AC-ID: AC-LENS-V2-DEPENDENCY-001
Authority: CORE-008 (TDD)
"""

import pytest
from pathlib import Path
from cortex.brain.analysis.dependency_analyzer import (
    DependencyAnalyzer,
    DependencyType,
    VulnerabilitySeverity,
    LicenseCategory,
    PackageInfo,
    Vulnerability,
    DependencyFinding,
    DependencyAnalysisResult,
    get_dependency_analyzer
)
import json


class TestDependencyAnalyzer:
    """Test suite for DependencyAnalyzer."""
    
    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create temporary project with dependency files."""
        project_dir = tmp_path / "test-project"
        project_dir.mkdir()
        
        # Python requirements.txt
        requirements = """
# Production dependencies
requests==2.28.0
flask>=2.0.0
django==3.2.10
numpy==1.21.0

# Dev dependencies
pytest==7.1.0
black==22.3.0
"""
        (project_dir / "requirements.txt").write_text(requirements)
        
        # Node.js package.json
        package_json = {
            "name": "test-app",
            "version": "1.0.0",
            "dependencies": {
                "express": "^4.17.1",
                "lodash": "4.17.20",
                "axios": "~0.21.0"
            },
            "devDependencies": {
                "jest": "^27.0.0",
                "eslint": "^8.0.0"
            }
        }
        (project_dir / "package.json").write_text(json.dumps(package_json, indent=2))
        
        # Java pom.xml
        pom_xml = """<?xml version="1.0" encoding="UTF-8"?>
<project>
    <dependencies>
        <dependency>
            <groupId>org.springframework</groupId>
            <artifactId>spring-core</artifactId>
            <version>5.3.0</version>
        </dependency>
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
            <version>4.13.2</version>
        </dependency>
    </dependencies>
</project>
"""
        (project_dir / "pom.xml").write_text(pom_xml)
        
        return project_dir
    
    @pytest.fixture
    def vulnerability_db(self, tmp_path):
        """Create vulnerability database."""
        vuln_db = {
            "django": [
                {
                    "cve_id": "CVE-2021-45115",
                    "severity": "high",
                    "description": "Denial-of-service in file uploads",
                    "affected_versions": "3.2.0-3.2.10",
                    "fixed_version": "3.2.11",
                    "cvss_score": 7.5,
                    "published_date": "2022-01-04"
                }
            ],
            "lodash": [
                {
                    "cve_id": "CVE-2020-8203",
                    "severity": "high",
                    "description": "Prototype pollution vulnerability",
                    "affected_versions": "<4.17.21",
                    "fixed_version": "4.17.21",
                    "cvss_score": 7.4,
                    "published_date": "2020-07-15"
                }
            ],
            "axios": [
                {
                    "cve_id": "CVE-2021-3749",
                    "severity": "medium",
                    "description": "SSRF vulnerability",
                    "affected_versions": "0.21.0-0.21.1",
                    "fixed_version": "0.21.2",
                    "cvss_score": 5.9,
                    "published_date": "2021-08-31"
                }
            ]
        }
        
        vuln_db_path = tmp_path / "vulnerabilities.json"
        vuln_db_path.write_text(json.dumps(vuln_db, indent=2))
        return vuln_db_path
    
    def test_init(self):
        """Test initialization."""
        analyzer = DependencyAnalyzer()
        assert analyzer._vulnerability_db == {}
        assert analyzer._license_db == {}
    
    def test_analyze_project_success(self, temp_project):
        """Test analyzing entire project."""
        analyzer = DependencyAnalyzer()
        result = analyzer.analyze_project(temp_project)
        
        assert result.success is True
        assert result.total_packages > 0
        assert len(result.dependency_files) == 3  # requirements.txt, package.json, pom.xml
        assert len(result.packages) > 0
    
    def test_analyze_project_nonexistent_path(self):
        """Test analyzing nonexistent project."""
        analyzer = DependencyAnalyzer()
        result = analyzer.analyze_project(Path("C:/___NONEXISTENT_XYZ___"))
        
        assert result.success is False
        assert "not found" in result.error.lower()
    
    def test_analyze_requirements_txt(self, temp_project):
        """Test analyzing Python requirements.txt."""
        analyzer = DependencyAnalyzer()
        req_file = temp_project / "requirements.txt"
        result = analyzer.analyze_requirements_txt(req_file)
        
        assert result.success is True
        assert result.total_packages == 6  # 6 packages in requirements.txt
        assert len(result.packages) == 6
        
        # Check specific packages
        package_names = {p.name for p in result.packages}
        assert "requests" in package_names
        assert "flask" in package_names
        assert "django" in package_names
        assert "numpy" in package_names
        assert "pytest" in package_names
        assert "black" in package_names
    
    def test_analyze_requirements_txt_package_versions(self, temp_project):
        """Test parsing package versions correctly."""
        analyzer = DependencyAnalyzer()
        req_file = temp_project / "requirements.txt"
        result = analyzer.analyze_requirements_txt(req_file)
        
        # Find specific packages
        requests_pkg = next(p for p in result.packages if p.name == "requests")
        assert requests_pkg.current_version == "2.28.0"
        
        flask_pkg = next(p for p in result.packages if p.name == "flask")
        assert flask_pkg.current_version == "2.0.0"
    
    def test_analyze_requirements_txt_not_found(self):
        """Test analyzing nonexistent requirements.txt."""
        analyzer = DependencyAnalyzer()
        result = analyzer.analyze_requirements_txt(Path("C:/___NONEXISTENT_XYZ___/requirements.txt"))
        
        assert result.success is False
        assert "not found" in result.error.lower()
    
    def test_analyze_package_json(self, temp_project):
        """Test analyzing Node.js package.json."""
        analyzer = DependencyAnalyzer()
        pkg_file = temp_project / "package.json"
        result = analyzer.analyze_package_json(pkg_file)
        
        assert result.success is True
        assert result.total_packages == 5  # 3 prod + 2 dev
        
        # Check production dependencies
        prod_deps = [p for p in result.packages if not p.is_dev]
        assert len(prod_deps) == 3
        
        prod_names = {p.name for p in prod_deps}
        assert "express" in prod_names
        assert "lodash" in prod_names
        assert "axios" in prod_names
        
        # Check dev dependencies
        dev_deps = [p for p in result.packages if p.is_dev]
        assert len(dev_deps) == 2
        
        dev_names = {p.name for p in dev_deps}
        assert "jest" in dev_names
        assert "eslint" in dev_names
    
    def test_analyze_package_json_version_cleaning(self, temp_project):
        """Test version cleaning (strip ^~>=<)."""
        analyzer = DependencyAnalyzer()
        pkg_file = temp_project / "package.json"
        result = analyzer.analyze_package_json(pkg_file)
        
        # express version should be cleaned from ^4.17.1 to 4.17.1
        express_pkg = next(p for p in result.packages if p.name == "express")
        assert express_pkg.current_version == "4.17.1"
        
        # axios version should be cleaned from ~0.21.0 to 0.21.0
        axios_pkg = next(p for p in result.packages if p.name == "axios")
        assert axios_pkg.current_version == "0.21.0"
    
    def test_analyze_package_json_not_found(self):
        """Test analyzing nonexistent package.json."""
        analyzer = DependencyAnalyzer()
        result = analyzer.analyze_package_json(Path("C:/___NONEXISTENT_XYZ___/package.json"))
        
        assert result.success is False
        assert "not found" in result.error.lower()
    
    def test_parse_pom_xml(self, temp_project):
        """Test parsing Java pom.xml."""
        analyzer = DependencyAnalyzer()
        pom_file = temp_project / "pom.xml"
        packages = analyzer._parse_pom_xml(pom_file)
        
        assert len(packages) == 2
        
        package_names = {p.name for p in packages}
        assert "org.springframework:spring-core" in package_names
        assert "junit:junit" in package_names
        
        spring_pkg = next(p for p in packages if "spring-core" in p.name)
        assert spring_pkg.current_version == "5.3.0"
        assert spring_pkg.dependency_type == DependencyType.JAVA
    
    def test_load_vulnerability_database(self, vulnerability_db):
        """Test loading vulnerability database."""
        analyzer = DependencyAnalyzer()
        count = analyzer.load_vulnerability_database(vulnerability_db)
        
        assert count == 3  # django, lodash, axios
        assert "django" in analyzer._vulnerability_db
        assert "lodash" in analyzer._vulnerability_db
        assert "axios" in analyzer._vulnerability_db
    
    def test_load_vulnerability_database_not_found(self):
        """Test loading nonexistent vulnerability database."""
        analyzer = DependencyAnalyzer()
        count = analyzer.load_vulnerability_database(Path("C:/___NONEXISTENT_XYZ___/vulns.json"))
        
        assert count == 0
    
    def test_check_vulnerabilities(self, vulnerability_db):
        """Test checking package for vulnerabilities."""
        analyzer = DependencyAnalyzer()
        analyzer.load_vulnerability_database(vulnerability_db)
        
        # Django has vulnerability
        django_pkg = PackageInfo(
            name="django",
            current_version="3.2.10",
            dependency_type=DependencyType.PYTHON
        )
        vulns = analyzer._check_vulnerabilities(django_pkg)
        
        assert len(vulns) == 1
        assert vulns[0].cve_id == "CVE-2021-45115"
        assert vulns[0].severity == VulnerabilitySeverity.HIGH
        assert vulns[0].fixed_version == "3.2.11"
    
    def test_check_vulnerabilities_no_match(self, vulnerability_db):
        """Test checking package with no vulnerabilities."""
        analyzer = DependencyAnalyzer()
        analyzer.load_vulnerability_database(vulnerability_db)
        
        safe_pkg = PackageInfo(
            name="safe-package",
            current_version="1.0.0",
            dependency_type=DependencyType.PYTHON
        )
        vulns = analyzer._check_vulnerabilities(safe_pkg)
        
        assert len(vulns) == 0
    
    def test_analyze_requirements_with_vulnerabilities(self, temp_project, vulnerability_db):
        """Test analyzing requirements.txt with vulnerability detection."""
        analyzer = DependencyAnalyzer()
        analyzer.load_vulnerability_database(vulnerability_db)
        
        req_file = temp_project / "requirements.txt"
        result = analyzer.analyze_requirements_txt(req_file)
        
        assert result.success is True
        assert result.vulnerable_packages == 1  # django
        assert len(result.findings) == 1
        
        finding = result.findings[0]
        assert finding.package.name == "django"
        assert finding.finding_type == "vulnerability"
        assert finding.severity == VulnerabilitySeverity.HIGH
        assert len(finding.vulnerabilities) == 1
    
    def test_analyze_package_json_with_vulnerabilities(self, temp_project, vulnerability_db):
        """Test analyzing package.json with vulnerability detection."""
        analyzer = DependencyAnalyzer()
        analyzer.load_vulnerability_database(vulnerability_db)
        
        pkg_file = temp_project / "package.json"
        result = analyzer.analyze_package_json(pkg_file)
        
        assert result.success is True
        assert result.vulnerable_packages == 2  # lodash, axios
        
        vuln_findings = [f for f in result.findings if f.finding_type == "vulnerability"]
        assert len(vuln_findings) == 2
    
    def test_get_package_info(self):
        """Test getting package info."""
        analyzer = DependencyAnalyzer()
        info = analyzer.get_package_info("requests", DependencyType.PYTHON)
        
        assert info is not None
        assert info.name == "requests"
        assert info.dependency_type == DependencyType.PYTHON
    
    def test_get_dependency_analyzer_singleton(self):
        """Test get_dependency_analyzer() returns singleton."""
        analyzer1 = get_dependency_analyzer()
        analyzer2 = get_dependency_analyzer()
        
        assert analyzer1 is analyzer2
    
    def test_package_info_dataclass(self):
        """Test PackageInfo dataclass."""
        pkg = PackageInfo(
            name="requests",
            current_version="2.28.0",
            latest_version="2.31.0",
            dependency_type=DependencyType.PYTHON,
            is_direct=True,
            is_dev=False,
            license="Apache-2.0",
            license_category=LicenseCategory.PERMISSIVE
        )
        
        assert pkg.name == "requests"
        assert pkg.current_version == "2.28.0"
        assert pkg.latest_version == "2.31.0"
        assert pkg.dependency_type == DependencyType.PYTHON
        assert pkg.is_direct is True
        assert pkg.is_dev is False
        assert pkg.license == "Apache-2.0"
        assert pkg.license_category == LicenseCategory.PERMISSIVE
    
    def test_vulnerability_dataclass(self):
        """Test Vulnerability dataclass."""
        vuln = Vulnerability(
            cve_id="CVE-2021-12345",
            severity=VulnerabilitySeverity.CRITICAL,
            description="Test vulnerability",
            affected_versions="1.0.0-1.2.0",
            fixed_version="1.2.1",
            cvss_score=9.8,
            published_date="2021-06-15"
        )
        
        assert vuln.cve_id == "CVE-2021-12345"
        assert vuln.severity == VulnerabilitySeverity.CRITICAL
        assert vuln.description == "Test vulnerability"
        assert vuln.affected_versions == "1.0.0-1.2.0"
        assert vuln.fixed_version == "1.2.1"
        assert vuln.cvss_score == 9.8
        assert vuln.published_date == "2021-06-15"
    
    def test_dependency_finding_dataclass(self):
        """Test DependencyFinding dataclass."""
        pkg = PackageInfo(name="test", current_version="1.0.0")
        finding = DependencyFinding(
            package=pkg,
            finding_type="outdated",
            severity=VulnerabilitySeverity.INFO,
            message="Package is outdated",
            recommendation="Update to 2.0.0"
        )
        
        assert finding.package == pkg
        assert finding.finding_type == "outdated"
        assert finding.severity == VulnerabilitySeverity.INFO
        assert finding.message == "Package is outdated"
        assert finding.recommendation == "Update to 2.0.0"
    
    def test_dependency_analysis_result_dataclass(self):
        """Test DependencyAnalysisResult dataclass."""
        result = DependencyAnalysisResult(
            success=True,
            total_packages=10,
            outdated_packages=3,
            vulnerable_packages=2,
            license_issues=1
        )
        
        assert result.success is True
        assert result.total_packages == 10
        assert result.outdated_packages == 3
        assert result.vulnerable_packages == 2
        assert result.license_issues == 1
    
    def test_find_dependency_files(self, temp_project):
        """Test finding all dependency files in project."""
        analyzer = DependencyAnalyzer()
        files = analyzer._find_dependency_files(temp_project)
        
        assert len(files) >= 3
        file_names = {f.name for f in files}
        assert "requirements.txt" in file_names
        assert "package.json" in file_names
        assert "pom.xml" in file_names
    
    def test_parse_requirements_comments_and_empty_lines(self, tmp_path):
        """Test parsing requirements.txt skips comments and empty lines."""
        req_content = """
# This is a comment
requests==2.28.0

# Another comment
flask>=2.0.0

"""
        req_file = tmp_path / "requirements.txt"
        req_file.write_text(req_content)
        
        analyzer = DependencyAnalyzer()
        packages = analyzer._parse_requirements_txt(req_file)
        
        assert len(packages) == 2
        package_names = {p.name for p in packages}
        assert "requests" in package_names
        assert "flask" in package_names
    
    def test_dependency_type_enum(self):
        """Test DependencyType enum."""
        assert DependencyType.PYTHON.value == "python"
        assert DependencyType.NODEJS.value == "nodejs"
        assert DependencyType.JAVA.value == "java"
        assert DependencyType.DOTNET.value == "dotnet"
    
    def test_vulnerability_severity_enum(self):
        """Test VulnerabilitySeverity enum."""
        assert VulnerabilitySeverity.CRITICAL.value == "critical"
        assert VulnerabilitySeverity.HIGH.value == "high"
        assert VulnerabilitySeverity.MEDIUM.value == "medium"
        assert VulnerabilitySeverity.LOW.value == "low"
        assert VulnerabilitySeverity.INFO.value == "info"
    
    def test_license_category_enum(self):
        """Test LicenseCategory enum."""
        assert LicenseCategory.PERMISSIVE.value == "permissive"
        assert LicenseCategory.COPYLEFT.value == "copyleft"
        assert LicenseCategory.PROPRIETARY.value == "proprietary"
        assert LicenseCategory.UNKNOWN.value == "unknown"
