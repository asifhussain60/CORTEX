"""
CORTEX Supply Chain Security Module

Purpose: Software Bill of Materials (SBOM) generation, dependency tracking,
         vulnerability monitoring, and supply chain security management.

Version: 1.0.0
Author: CORTEX Development Team
Created: December 30, 2025
Status: Phase 5 Security Enhancement

Features:
- SBOM generation (CycloneDX, SPDX formats)
- Dependency vulnerability scanning
- License compliance checking
- Supply chain risk assessment
- Dependency freshness tracking
- Malicious package detection
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import re
import hashlib

logger = logging.getLogger(__name__)


class SBOMFormat(Enum):
    """Supported SBOM formats."""
    CYCLONEDX = "cyclonedx"
    SPDX = "spdx"
    SWID = "swid"


class LicenseCategory(Enum):
    """License risk categories."""
    PERMISSIVE = "permissive"      # MIT, Apache, BSD
    WEAK_COPYLEFT = "weak_copyleft"  # LGPL, MPL
    STRONG_COPYLEFT = "strong_copyleft"  # GPL, AGPL
    COMMERCIAL = "commercial"
    UNKNOWN = "unknown"


class DependencyRisk(Enum):
    """Dependency risk levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


@dataclass
class Dependency:
    """Software dependency representation."""
    name: str
    version: str
    ecosystem: str  # npm, pypi, nuget, maven, etc.
    purl: str  # Package URL (pkg:npm/lodash@4.17.21)
    licenses: List[str] = field(default_factory=list)
    direct: bool = True
    dependencies: List[str] = field(default_factory=list)  # Transitive deps
    hash_sha256: Optional[str] = None
    repository_url: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None


@dataclass
class Vulnerability:
    """Vulnerability in a dependency."""
    vuln_id: str  # CVE, GHSA, etc.
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    cvss_score: float
    title: str
    description: str
    affected_versions: str
    fixed_version: Optional[str] = None
    references: List[str] = field(default_factory=list)
    published_date: Optional[str] = None


@dataclass
class DependencyAuditResult:
    """Result of dependency audit."""
    dependency: Dependency
    vulnerabilities: List[Vulnerability] = field(default_factory=list)
    license_risk: LicenseCategory = LicenseCategory.UNKNOWN
    outdated: bool = False
    latest_version: Optional[str] = None
    risk_score: float = 0.0
    risk_level: DependencyRisk = DependencyRisk.MINIMAL


@dataclass
class SBOMDocument:
    """Software Bill of Materials document."""
    format: SBOMFormat
    spec_version: str
    serial_number: str
    timestamp: str
    tool_name: str
    tool_version: str
    component_name: str
    component_version: str
    components: List[Dependency]
    vulnerabilities: List[Vulnerability] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class SupplyChainSecurity:
    """
    Supply chain security management for CORTEX.
    
    Provides:
    - SBOM generation in industry-standard formats
    - Dependency vulnerability scanning
    - License compliance checking
    - Supply chain risk assessment
    - Malicious package detection patterns
    """
    
    # License classification
    LICENSE_CATEGORIES = {
        'MIT': LicenseCategory.PERMISSIVE,
        'Apache-2.0': LicenseCategory.PERMISSIVE,
        'BSD-2-Clause': LicenseCategory.PERMISSIVE,
        'BSD-3-Clause': LicenseCategory.PERMISSIVE,
        'ISC': LicenseCategory.PERMISSIVE,
        'CC0-1.0': LicenseCategory.PERMISSIVE,
        'Unlicense': LicenseCategory.PERMISSIVE,
        'LGPL-2.1': LicenseCategory.WEAK_COPYLEFT,
        'LGPL-3.0': LicenseCategory.WEAK_COPYLEFT,
        'MPL-2.0': LicenseCategory.WEAK_COPYLEFT,
        'EPL-2.0': LicenseCategory.WEAK_COPYLEFT,
        'GPL-2.0': LicenseCategory.STRONG_COPYLEFT,
        'GPL-3.0': LicenseCategory.STRONG_COPYLEFT,
        'AGPL-3.0': LicenseCategory.STRONG_COPYLEFT,
    }
    
    # Malicious package indicators
    MALICIOUS_INDICATORS = [
        r'typosquat',  # Similar to popular package names
        r'install.*script.*download',  # Download during install
        r'eval\s*\(\s*base64',  # Base64 eval
        r'process\.env.*password|token|key|secret',  # Credential harvesting
        r'crypto.*miner',  # Cryptomining
        r'reverse.*shell',  # Reverse shells
    ]
    
    def __init__(
        self,
        project_path: Optional[Path] = None,
        cache_path: Optional[Path] = None
    ):
        """Initialize supply chain security module."""
        self.project_path = project_path or Path.cwd()
        self.cache_path = cache_path or self.project_path / 'cortex-brain' / 'cache' / 'supply-chain'
        self.cache_path.mkdir(parents=True, exist_ok=True)
        logger.info("📦 Supply Chain Security module initialized")
    
    def _generate_serial_number(self) -> str:
        """Generate unique SBOM serial number."""
        timestamp = datetime.now().isoformat()
        hash_input = f"{self.project_path}:{timestamp}"
        return f"urn:uuid:{hashlib.md5(hash_input.encode()).hexdigest()}"
    
    def _detect_ecosystem(self, file_path: Path) -> Optional[str]:
        """Detect package ecosystem from manifest file."""
        ecosystem_map = {
            'package.json': 'npm',
            'package-lock.json': 'npm',
            'yarn.lock': 'npm',
            'requirements.txt': 'pypi',
            'Pipfile': 'pypi',
            'Pipfile.lock': 'pypi',
            'pyproject.toml': 'pypi',
            'poetry.lock': 'pypi',
            'Gemfile': 'rubygems',
            'Gemfile.lock': 'rubygems',
            'go.mod': 'golang',
            'go.sum': 'golang',
            'Cargo.toml': 'cargo',
            'Cargo.lock': 'cargo',
            'pom.xml': 'maven',
            'build.gradle': 'maven',
            'composer.json': 'packagist',
            'composer.lock': 'packagist',
            '*.csproj': 'nuget',
            'packages.config': 'nuget',
        }
        
        filename = file_path.name
        return ecosystem_map.get(filename)
    
    def _generate_purl(self, name: str, version: str, ecosystem: str) -> str:
        """Generate Package URL (PURL)."""
        return f"pkg:{ecosystem}/{name}@{version}"
    
    def scan_dependencies(self) -> List[Dependency]:
        """
        Scan project for all dependencies.
        
        Returns:
            List of discovered dependencies
        """
        dependencies = []
        
        # Python: requirements.txt
        req_file = self.project_path / 'requirements.txt'
        if req_file.exists():
            dependencies.extend(self._parse_requirements_txt(req_file))
        
        # Python: pyproject.toml
        pyproject = self.project_path / 'pyproject.toml'
        if pyproject.exists():
            dependencies.extend(self._parse_pyproject_toml(pyproject))
        
        # Node.js: package.json
        package_json = self.project_path / 'package.json'
        if package_json.exists():
            dependencies.extend(self._parse_package_json(package_json))
        
        # .NET: *.csproj
        for csproj in self.project_path.rglob('*.csproj'):
            dependencies.extend(self._parse_csproj(csproj))
        
        return dependencies
    
    def _parse_requirements_txt(self, file_path: Path) -> List[Dependency]:
        """Parse Python requirements.txt."""
        dependencies = []
        
        try:
            content = file_path.read_text()
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith('#') or line.startswith('-'):
                    continue
                
                # Parse: package==version or package>=version
                match = re.match(r'^([a-zA-Z0-9_-]+)(?:[=<>!~]+)?([0-9a-zA-Z.\-_]+)?', line)
                if match:
                    name = match.group(1)
                    version = match.group(2) or 'unknown'
                    
                    dependencies.append(Dependency(
                        name=name,
                        version=version,
                        ecosystem='pypi',
                        purl=self._generate_purl(name, version, 'pypi'),
                        direct=True
                    ))
        except Exception as e:
            logger.warning(f"Error parsing {file_path}: {e}")
        
        return dependencies
    
    def _parse_pyproject_toml(self, file_path: Path) -> List[Dependency]:
        """Parse Python pyproject.toml."""
        dependencies = []
        
        try:
            content = file_path.read_text()
            
            # Simple regex parsing for dependencies
            dep_section = re.search(r'\[tool\.poetry\.dependencies\](.*?)(?:\[|$)', content, re.DOTALL)
            if dep_section:
                for line in dep_section.group(1).splitlines():
                    match = re.match(r'^([a-zA-Z0-9_-]+)\s*=\s*["\']?([^"\']+)', line.strip())
                    if match:
                        name = match.group(1)
                        if name == 'python':
                            continue
                        version = match.group(2).strip('"\'')
                        
                        dependencies.append(Dependency(
                            name=name,
                            version=version,
                            ecosystem='pypi',
                            purl=self._generate_purl(name, version, 'pypi'),
                            direct=True
                        ))
        except Exception as e:
            logger.warning(f"Error parsing {file_path}: {e}")
        
        return dependencies
    
    def _parse_package_json(self, file_path: Path) -> List[Dependency]:
        """Parse Node.js package.json."""
        dependencies = []
        
        try:
            data = json.loads(file_path.read_text())
            
            for dep_type in ['dependencies', 'devDependencies']:
                deps = data.get(dep_type, {})
                for name, version in deps.items():
                    # Clean version string
                    clean_version = re.sub(r'^[\^~>=<]', '', version)
                    
                    dependencies.append(Dependency(
                        name=name,
                        version=clean_version,
                        ecosystem='npm',
                        purl=self._generate_purl(name, clean_version, 'npm'),
                        direct=True
                    ))
        except Exception as e:
            logger.warning(f"Error parsing {file_path}: {e}")
        
        return dependencies
    
    def _parse_csproj(self, file_path: Path) -> List[Dependency]:
        """Parse .NET csproj file."""
        dependencies = []
        
        try:
            content = file_path.read_text()
            
            # Find PackageReference elements
            pattern = r'<PackageReference\s+Include="([^"]+)"\s+Version="([^"]+)"'
            for match in re.finditer(pattern, content):
                name = match.group(1)
                version = match.group(2)
                
                dependencies.append(Dependency(
                    name=name,
                    version=version,
                    ecosystem='nuget',
                    purl=self._generate_purl(name, version, 'nuget'),
                    direct=True
                ))
        except Exception as e:
            logger.warning(f"Error parsing {file_path}: {e}")
        
        return dependencies
    
    def generate_sbom(
        self,
        format: SBOMFormat = SBOMFormat.CYCLONEDX,
        component_name: Optional[str] = None,
        component_version: str = "1.0.0"
    ) -> SBOMDocument:
        """
        Generate Software Bill of Materials.
        
        Args:
            format: SBOM format (CycloneDX, SPDX)
            component_name: Name of the component being documented
            component_version: Version of the component
            
        Returns:
            SBOMDocument with all dependencies
        """
        dependencies = self.scan_dependencies()
        
        sbom = SBOMDocument(
            format=format,
            spec_version="1.5" if format == SBOMFormat.CYCLONEDX else "2.3",
            serial_number=self._generate_serial_number(),
            timestamp=datetime.now().isoformat(),
            tool_name="CORTEX Supply Chain Security",
            tool_version="1.0.0",
            component_name=component_name or self.project_path.name,
            component_version=component_version,
            components=dependencies,
            metadata={
                'generated_by': 'CORTEX',
                'project_path': str(self.project_path),
                'total_dependencies': len(dependencies),
            }
        )
        
        logger.info(f"📋 Generated SBOM: {len(dependencies)} components")
        return sbom
    
    def export_sbom_cyclonedx(self, sbom: SBOMDocument) -> str:
        """Export SBOM in CycloneDX JSON format."""
        components = []
        
        for dep in sbom.components:
            components.append({
                "type": "library",
                "bom-ref": dep.purl,
                "name": dep.name,
                "version": dep.version,
                "purl": dep.purl,
                "licenses": [{"license": {"id": lic}} for lic in dep.licenses] if dep.licenses else [],
                "externalReferences": [
                    {"type": "vcs", "url": dep.repository_url}
                ] if dep.repository_url else []
            })
        
        cyclonedx = {
            "bomFormat": "CycloneDX",
            "specVersion": sbom.spec_version,
            "serialNumber": sbom.serial_number,
            "version": 1,
            "metadata": {
                "timestamp": sbom.timestamp,
                "tools": [{
                    "vendor": "CORTEX",
                    "name": sbom.tool_name,
                    "version": sbom.tool_version
                }],
                "component": {
                    "type": "application",
                    "name": sbom.component_name,
                    "version": sbom.component_version
                }
            },
            "components": components
        }
        
        return json.dumps(cyclonedx, indent=2)
    
    def export_sbom_spdx(self, sbom: SBOMDocument) -> str:
        """Export SBOM in SPDX JSON format."""
        packages = []
        
        for i, dep in enumerate(sbom.components):
            packages.append({
                "SPDXID": f"SPDXRef-Package-{i}",
                "name": dep.name,
                "versionInfo": dep.version,
                "downloadLocation": dep.repository_url or "NOASSERTION",
                "licenseConcluded": dep.licenses[0] if dep.licenses else "NOASSERTION",
                "licenseDeclared": dep.licenses[0] if dep.licenses else "NOASSERTION",
                "copyrightText": "NOASSERTION",
                "externalRefs": [{
                    "referenceCategory": "PACKAGE-MANAGER",
                    "referenceType": "purl",
                    "referenceLocator": dep.purl
                }]
            })
        
        spdx = {
            "spdxVersion": f"SPDX-{sbom.spec_version}",
            "dataLicense": "CC0-1.0",
            "SPDXID": "SPDXRef-DOCUMENT",
            "name": sbom.component_name,
            "documentNamespace": sbom.serial_number,
            "creationInfo": {
                "created": sbom.timestamp,
                "creators": [f"Tool: {sbom.tool_name}-{sbom.tool_version}"]
            },
            "packages": packages
        }
        
        return json.dumps(spdx, indent=2)
    
    def audit_dependencies(
        self,
        dependencies: Optional[List[Dependency]] = None
    ) -> List[DependencyAuditResult]:
        """
        Audit dependencies for vulnerabilities and risks.
        
        Args:
            dependencies: List of dependencies to audit (scans if not provided)
            
        Returns:
            List of audit results
        """
        if dependencies is None:
            dependencies = self.scan_dependencies()
        
        results = []
        
        for dep in dependencies:
            audit_result = DependencyAuditResult(
                dependency=dep,
                license_risk=self._assess_license_risk(dep.licenses),
            )
            
            # Calculate risk score
            risk_score = 0.0
            
            # License risk
            license_risk_weights = {
                LicenseCategory.PERMISSIVE: 0,
                LicenseCategory.WEAK_COPYLEFT: 20,
                LicenseCategory.STRONG_COPYLEFT: 40,
                LicenseCategory.COMMERCIAL: 30,
                LicenseCategory.UNKNOWN: 50,
            }
            risk_score += license_risk_weights.get(audit_result.license_risk, 50)
            
            # Vulnerability simulation (in production, call actual vulnerability database)
            # For demo, we'll flag certain known-vulnerable versions
            known_vulns = self._check_known_vulnerabilities(dep)
            audit_result.vulnerabilities = known_vulns
            
            # Add vulnerability risk
            for vuln in known_vulns:
                if vuln.severity == 'CRITICAL':
                    risk_score += 40
                elif vuln.severity == 'HIGH':
                    risk_score += 25
                elif vuln.severity == 'MEDIUM':
                    risk_score += 10
                elif vuln.severity == 'LOW':
                    risk_score += 5
            
            audit_result.risk_score = min(100, risk_score)
            
            # Determine risk level
            if audit_result.risk_score >= 80:
                audit_result.risk_level = DependencyRisk.CRITICAL
            elif audit_result.risk_score >= 60:
                audit_result.risk_level = DependencyRisk.HIGH
            elif audit_result.risk_score >= 40:
                audit_result.risk_level = DependencyRisk.MEDIUM
            elif audit_result.risk_score >= 20:
                audit_result.risk_level = DependencyRisk.LOW
            else:
                audit_result.risk_level = DependencyRisk.MINIMAL
            
            results.append(audit_result)
        
        return results
    
    def _assess_license_risk(self, licenses: List[str]) -> LicenseCategory:
        """Assess license risk category."""
        if not licenses:
            return LicenseCategory.UNKNOWN
        
        for lic in licenses:
            if lic in self.LICENSE_CATEGORIES:
                return self.LICENSE_CATEGORIES[lic]
        
        return LicenseCategory.UNKNOWN
    
    def _check_known_vulnerabilities(self, dep: Dependency) -> List[Vulnerability]:
        """
        Check for known vulnerabilities.
        
        Note: In production, this would query NVD, OSV, GitHub Advisory, etc.
        This is a simplified demo with hardcoded examples.
        """
        vulnerabilities = []
        
        # Example: lodash < 4.17.21 has prototype pollution
        if dep.name.lower() == 'lodash' and dep.version < '4.17.21':
            vulnerabilities.append(Vulnerability(
                vuln_id='CVE-2021-23337',
                severity='HIGH',
                cvss_score=7.2,
                title='Prototype Pollution in lodash',
                description='lodash before 4.17.21 is vulnerable to prototype pollution.',
                affected_versions='<4.17.21',
                fixed_version='4.17.21',
                references=['https://nvd.nist.gov/vuln/detail/CVE-2021-23337'],
                published_date='2021-02-15'
            ))
        
        # Example: requests < 2.32.0 has security issue
        if dep.name.lower() == 'requests' and dep.version < '2.32.0':
            vulnerabilities.append(Vulnerability(
                vuln_id='CVE-2024-35195',
                severity='MEDIUM',
                cvss_score=5.3,
                title='Proxy credential leak in requests',
                description='Requests library may leak proxy credentials in certain conditions.',
                affected_versions='<2.32.0',
                fixed_version='2.32.0',
                references=['https://nvd.nist.gov/vuln/detail/CVE-2024-35195'],
                published_date='2024-05-20'
            ))
        
        return vulnerabilities
    
    def detect_typosquatting(self, package_name: str) -> List[str]:
        """
        Detect potential typosquatting packages.
        
        Args:
            package_name: Package name to check
            
        Returns:
            List of potential typosquatting variants
        """
        popular_packages = {
            'numpy', 'pandas', 'requests', 'django', 'flask', 
            'tensorflow', 'pytorch', 'lodash', 'express', 'react'
        }
        
        suspicious = []
        
        for popular in popular_packages:
            # Check for close matches (simple Levenshtein-like check)
            if package_name != popular and self._is_similar(package_name, popular):
                suspicious.append(f"Similar to popular package '{popular}'")
        
        return suspicious
    
    def _is_similar(self, s1: str, s2: str) -> bool:
        """Check if two strings are suspiciously similar."""
        # Simple check: same length with 1-2 char difference
        if abs(len(s1) - len(s2)) <= 1:
            diff = sum(1 for a, b in zip(s1, s2) if a != b)
            if diff <= 2:
                return True
        return False
    
    def generate_supply_chain_report(self) -> Dict[str, Any]:
        """Generate comprehensive supply chain security report."""
        dependencies = self.scan_dependencies()
        audit_results = self.audit_dependencies(dependencies)
        
        # Aggregate stats
        total = len(audit_results)
        by_risk = {}
        by_license = {}
        vulnerable_count = 0
        critical_vulns = []
        
        for result in audit_results:
            # Risk distribution
            risk = result.risk_level.value
            by_risk[risk] = by_risk.get(risk, 0) + 1
            
            # License distribution
            lic = result.license_risk.value
            by_license[lic] = by_license.get(lic, 0) + 1
            
            # Vulnerability count
            if result.vulnerabilities:
                vulnerable_count += 1
                for vuln in result.vulnerabilities:
                    if vuln.severity == 'CRITICAL':
                        critical_vulns.append({
                            'package': result.dependency.name,
                            'vuln_id': vuln.vuln_id,
                            'fixed_version': vuln.fixed_version
                        })
        
        return {
            'summary': {
                'total_dependencies': total,
                'vulnerable_packages': vulnerable_count,
                'critical_vulnerabilities': len(critical_vulns),
                'scan_timestamp': datetime.now().isoformat(),
            },
            'risk_distribution': by_risk,
            'license_distribution': by_license,
            'critical_issues': critical_vulns,
            'recommendations': self._generate_recommendations(audit_results),
            'audit_results': [
                {
                    'package': r.dependency.name,
                    'version': r.dependency.version,
                    'risk_level': r.risk_level.value,
                    'risk_score': r.risk_score,
                    'vulnerabilities': len(r.vulnerabilities),
                    'license': r.license_risk.value,
                }
                for r in audit_results
            ]
        }
    
    def _generate_recommendations(
        self,
        audit_results: List[DependencyAuditResult]
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        critical_count = sum(1 for r in audit_results if r.risk_level == DependencyRisk.CRITICAL)
        high_count = sum(1 for r in audit_results if r.risk_level == DependencyRisk.HIGH)
        
        if critical_count > 0:
            recommendations.append(
                f"🚨 CRITICAL: {critical_count} packages require immediate attention"
            )
        
        if high_count > 0:
            recommendations.append(
                f"⚠️ HIGH: {high_count} packages should be reviewed this sprint"
            )
        
        for result in audit_results:
            if result.vulnerabilities:
                for vuln in result.vulnerabilities:
                    if vuln.fixed_version:
                        recommendations.append(
                            f"Upgrade {result.dependency.name} to {vuln.fixed_version} "
                            f"(fixes {vuln.vuln_id})"
                        )
        
        # License recommendations
        copyleft_packages = [
            r.dependency.name for r in audit_results 
            if r.license_risk == LicenseCategory.STRONG_COPYLEFT
        ]
        if copyleft_packages:
            recommendations.append(
                f"Review copyleft licenses in: {', '.join(copyleft_packages[:5])}"
            )
        
        return recommendations


# CLI Interface
if __name__ == "__main__":
    import sys
    
    scs = SupplyChainSecurity(
        project_path=Path(sys.argv[1] if len(sys.argv) > 1 else '.')
    )
    
    # Generate SBOM
    sbom = scs.generate_sbom()
    print(f"Generated SBOM with {len(sbom.components)} components")
    
    # Export to file
    cyclonedx = scs.export_sbom_cyclonedx(sbom)
    Path('sbom.json').write_text(cyclonedx)
    print("Exported to sbom.json")
    
    # Generate report
    report = scs.generate_supply_chain_report()
    print(f"\nSupply Chain Report:")
    print(f"  Total dependencies: {report['summary']['total_dependencies']}")
    print(f"  Vulnerable: {report['summary']['vulnerable_packages']}")
    print(f"  Critical: {report['summary']['critical_vulnerabilities']}")
    
    print("\nRecommendations:")
    for rec in report['recommendations'][:5]:
        print(f"  • {rec}")
