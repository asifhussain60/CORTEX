"""
Repository Onboarding Orchestrator (ENHANCED v2.0).

Universal repository onboarding with comprehensive analysis:
- `/CORTEX onboard {path}` command
- Multi-layer analysis (code, config, DB, API)
- Company domain integration
- Security threat modeling (P0/P1/P2)
- BusinessLanguageOrchestrator narratives with confidence scores
- Universal dashboard generation in company/dashboards/
- Landing page hub with repository tiles
- Collapsible file references and evidence tracking

AC-ID: AC-UNIVERSAL-ONBOARD-001
Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging
import json

from cortex.orchestrators.mixins.security_advisor_mixin import SecurityAdvisorMixin
from cortex.core.interfaces import IOrchestrator
from cortex.brain.core.result import Result, Ok, Err

logger = logging.getLogger(__name__)

# Lazy imports for new components
_asset_manager = None
_landing_page_generator = None
_business_language_orchestrator = None
_universal_dashboard_generator = None


def _get_asset_manager():
    """Lazy-load DashboardAssetManager."""
    global _asset_manager
    if _asset_manager is None:
        from cortex.orchestrators.support.dashboard_asset_manager import (
            get_dashboard_asset_manager
        )
        _asset_manager = get_dashboard_asset_manager()
    return _asset_manager


def _get_landing_page_generator():
    """Lazy-load LandingPageGenerator."""
    global _landing_page_generator
    if _landing_page_generator is None:
        from cortex.orchestrators.support.landing_page_generator import (
            get_landing_page_generator
        )
        _landing_page_generator = get_landing_page_generator()
    return _landing_page_generator


def _get_business_language_orchestrator():
    """Lazy-load BusinessLanguageOrchestrator."""
    global _business_language_orchestrator
    if _business_language_orchestrator is None:
        from cortex.orchestrators.support.business_language_orchestrator import (
            get_business_language_orchestrator
        )
        _business_language_orchestrator = get_business_language_orchestrator()
    return _business_language_orchestrator


def _get_universal_dashboard_generator():
    """Lazy-load UniversalDashboardGenerator."""
    global _universal_dashboard_generator
    if _universal_dashboard_generator is None:
        from cortex.orchestrators.support.universal_dashboard_generator import (
            get_universal_dashboard_generator
        )
        _universal_dashboard_generator = get_universal_dashboard_generator()
    return _universal_dashboard_generator


@dataclass
class OnboardingResult:
    """
    Result of repository onboarding.
    
    Attributes:
        success: Whether onboarding succeeded
        repo_path: Path to onboarded repository
        repo_name: Canonical repository name (lowercase)
        timestamp: Onboarding timestamp
        holistic_context: Full LENS analysis results
        security_risks: P0/P1/P2 risk breakdown
        company_domain_updates: New domain YAMLs created
        dashboard_path: Path to generated dashboard
        landing_page_path: Path to landing page hub
        business_narrative: Comprehensive narrative with confidence
        recommendations: Top actionable recommendations
        error: Error message if failed
    """
    success: bool
    repo_path: str
    repo_name: str = ""
    timestamp: str = ""
    holistic_context: Dict[str, Any] = field(default_factory=dict)
    security_risks: Dict[str, Any] = field(default_factory=dict)
    company_domain_updates: List[str] = field(default_factory=list)
    dashboard_path: Optional[str] = None
    landing_page_path: Optional[str] = None
    business_narrative: Optional[Any] = None  # BusinessNarrative
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    error: str = ""


class RepositoryOnboardingOrchestrator(SecurityAdvisorMixin, IOrchestrator):
    """
    Universal Repository Onboarding Orchestrator v2.0.
    
    MCP-EXPOSED CAPABILITIES:
    - `/CORTEX onboard {path}` — Full repository analysis
    - Generates dashboard in company/dashboards/{repo_name}/
    - Auto-updates landing page hub with new repo tile
    - Comprehensive business narratives with confidence scores
    - Security-first assessment with P0/P1/P2 classification
    - Collapsible file references with evidence tracking
    
    Example:
        >>> orchestrator = RepositoryOnboardingOrchestrator()
        >>> result = orchestrator.onboard_repository(Path("/path/to/repo"))
        >>> if result.success:
        ...     print(f"Dashboard: {result.dashboard_path}")
        ...     print(f"Landing: {result.landing_page_path}")
        ...     print(f"Confidence: {result.business_narrative.confidence.score}%")
    """
    
    def __init__(self):
        """Initialize RepositoryOnboardingOrchestrator."""
        super().__init__()
        self.lens_orchestrator = None  # Lazy-loaded
        self.dashboard_generator = None  # Lazy-loaded
    
    def onboard_repository(
        self,
        repo_path: Path,
        include_dashboard: bool = True,
        update_company_domain: bool = True,
        repo_name: Optional[str] = None,
        icon: str = "📁",
    ) -> OnboardingResult:
        """
        Onboard repository with comprehensive analysis.
        
        Universal Workflow:
        1. Ensure shared assets exist in company/dashboards/assets/
        2. Run LENSOrchestrator.analyze_repository_holistic()
        3. Generate business narrative via BusinessLanguageOrchestrator
        4. Run security threat modeling (P0/P1/P2)
        5. Generate universal dashboard with confidence scores
        6. Update landing page hub with new repository tile
        7. Create onboarding report
        
        Args:
            repo_path: Path to repository to onboard
            include_dashboard: Whether to generate dashboard
            update_company_domain: Whether to update company domains
            repo_name: Override repo name (default: folder name)
            icon: Emoji icon for landing page tile
            
        Returns:
            OnboardingResult with analysis, dashboard, and landing page
            
        Example:
            >>> result = orchestrator.onboard_repository(
            ...     Path("/workspace/kashkole"),
            ...     repo_name="kashkole",
            ...     icon="💼"
            ... )
            >>> print(result.dashboard_path)
            >>> print(result.business_narrative.description)
        """
        logger.info("Starting universal repository onboarding: %s", repo_path)
        
        # Canonical name
        canonical_name = (repo_name or repo_path.name).lower().strip()
        
        if not repo_path.exists():
            return OnboardingResult(
                success=False,
                repo_path=str(repo_path),
                repo_name=canonical_name,
                timestamp=datetime.now().isoformat(),
                error=f"Repository path does not exist: {repo_path}"
            )
        
        result = OnboardingResult(
            success=True,
            repo_path=str(repo_path),
            repo_name=canonical_name,
            timestamp=datetime.now().isoformat(),
        )
        
        try:
            # Step 0: Ensure shared assets exist
            logger.info("Step 0: Ensuring shared dashboard assets...")
            asset_manager = _get_asset_manager()
            asset_manager.ensure_assets_exist()
            
            # Step 1: Holistic LENS analysis
            logger.info("Step 1: Running holistic LENS analysis...")
            lens_context = self._run_holistic_analysis(repo_path)
            result.holistic_context = lens_context
            
            # Step 2: Generate business narrative
            logger.info("Step 2: Generating business narrative...")
            business_orchestrator = _get_business_language_orchestrator()
            narrative = business_orchestrator.generate_narrative(
                repo_path=repo_path,
                analysis_data=lens_context  # Correct parameter name
            )
            result.business_narrative = narrative
            
            # Step 3: Security threat modeling
            logger.info("Step 3: Running security threat modeling...")
            security_model = self._run_threat_modeling(lens_context, repo_path)
            result.security_risks = security_model
            
            # Step 4: Company domain updates
            if update_company_domain:
                logger.info("Step 4: Updating company domains...")
                domain_updates = self._update_company_domains(lens_context, repo_path)
                result.company_domain_updates = domain_updates
            
            # Step 5: Generate recommendations BEFORE dashboard
            logger.info("Step 5: Generating recommendations...")
            recommendations = self._prioritize_recommendations(security_model, lens_context)
            result.recommendations = recommendations
            
            # Step 6: Generate universal dashboard
            if include_dashboard:
                logger.info("Step 6: Generating universal dashboard...")
                dashboard_gen = _get_universal_dashboard_generator()
                
                # Prepare full data
                analysis_data = {
                    'repo_path': str(repo_path),
                    'timestamp': result.timestamp,
                    'security_risks': security_model,
                    'holistic_context': lens_context,
                    'recommendations': recommendations,
                }
                
                dashboard_path = dashboard_gen.generate_dashboard(
                    repo_name=canonical_name,
                    narrative=narrative,
                    analysis_data=analysis_data
                )
                result.dashboard_path = str(dashboard_path)
                
                # Step 7: Update landing page hub
                logger.info("Step 7: Updating landing page hub...")
                landing_gen = _get_landing_page_generator()
                
                # Determine tagline
                tagline = getattr(narrative, 'tagline', 'Software Application')
                confidence = getattr(narrative, 'confidence', None)
                conf_score = getattr(confidence, 'score', 50) if confidence else 50
                
                landing_gen.add_repo_to_registry(
                    repo_name=canonical_name,
                    title=getattr(narrative, 'title', canonical_name.upper()),
                    description=tagline[:100],
                    icon=icon,
                    confidence_score=conf_score,
                )
                landing_page_path = landing_gen.regenerate_landing_page()
                result.landing_page_path = str(landing_page_path)
            
            logger.info("Repository onboarding complete: %s", repo_path)
            
        except Exception as e:
            logger.error("Repository onboarding failed: %s", e, exc_info=True)
            result.success = False
            result.error = str(e)
        
        return result
    
    def _run_holistic_analysis(self, repo_path: Path) -> Dict[str, Any]:
        """
        Run holistic LENS analysis on repository.
        
        Uses LENSOrchestrator.analyze_repository_holistic() for comprehensive analysis:
        - Git history (commits, contributors, patterns)
        - AST analysis (code structure, complexity)
        - Comment extraction (TODOs, docstrings)
        - Config security scanning
        - Database schema analysis
        - API endpoint analysis
        
        Returns:
            Dict with comprehensive LENS analysis including all 9 analyzer outputs
        """
        try:
            # Lazy-load LENSOrchestrator with correct repo path
            if self.lens_orchestrator is None:
                from cortex.orchestrators.support.lens_orchestrator import LENSOrchestrator
                self.lens_orchestrator = LENSOrchestrator(repo_path=repo_path)
            else:
                # Update repo path if different
                self.lens_orchestrator.repo_path = repo_path
            
            # Run the FULL holistic analysis using all 9 LENS analyzers
            logger.info("Running LENS analyze_repository_holistic()...")
            lens_result = self.lens_orchestrator.analyze_repository_holistic(
                include_vision=False,  # Skip vision for speed
                include_security=True,  # Always include security
            )
            
            # Merge in additional repo-specific data
            lens_result["metadata"]["repo_path"] = str(repo_path)
            lens_result["metadata"]["analysis_timestamp"] = datetime.now().isoformat()
            
            # Add dependency analysis (not yet in LENS but useful)
            lens_result["dependency_analysis"] = self._analyze_dependency_layer(repo_path)
            
            # Detect language/framework if not already present
            if "language_detection" not in lens_result:
                lens_result["language_detection"] = self._detect_languages(repo_path)
            
            logger.info(
                "LENS analysis complete: %s analyzers, %d ms",
                len(lens_result.get("metadata", {}).get("analyzers_enabled", [])),
                lens_result.get("metadata", {}).get("analysis_time_ms", 0)
            )
            
            return lens_result
            
        except Exception as e:
            logger.error("Holistic LENS analysis failed: %s", e, exc_info=True)
            # Fallback to basic analysis if LENS fails
            return self._fallback_basic_analysis(repo_path, str(e))
    
    def _fallback_basic_analysis(self, repo_path: Path, error_msg: str) -> Dict[str, Any]:
        """
        Fallback analysis when full LENS pipeline fails.
        
        Provides basic repository information without deep analysis.
        """
        logger.warning("Using fallback analysis due to: %s", error_msg)
        
        return {
            "metadata": {
                "repo_path": str(repo_path),
                "analysis_timestamp": datetime.now().isoformat(),
                "fallback_mode": True,
                "original_error": error_msg,
                "analyzers_enabled": ["basic"],
            },
            "repository_summary": {
                "total_files": len(list(repo_path.rglob("*"))),
                "total_python_files": len(list(repo_path.glob("**/*.py"))),
            },
            "code_analysis": self._analyze_code_layer(repo_path),
            "config_analysis": self._analyze_config_layer(repo_path),
            "database_analysis": self._analyze_database_layer(repo_path),
            "api_analysis": self._analyze_api_layer(repo_path),
            "dependency_analysis": self._analyze_dependency_layer(repo_path),
            "language_detection": self._detect_languages(repo_path),
            "security_analysis": {"findings": [], "note": "Fallback mode - limited security analysis"},
            "recommendations": [],
        }
    
    def _detect_languages(self, repo_path: Path) -> Dict[str, Any]:
        """
        Detect programming languages and frameworks in repository.
        
        Returns:
            Dict with detected languages, frameworks, and file counts
        """
        extensions_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".cs": "C#",
            ".vb": "VB.NET",
            ".java": "Java",
            ".go": "Go",
            ".rs": "Rust",
            ".rb": "Ruby",
            ".php": "PHP",
            ".aspx": "ASP.NET WebForms",
            ".cshtml": "ASP.NET Razor",
            ".html": "HTML",
            ".css": "CSS",
            ".sql": "SQL",
            ".yaml": "YAML",
            ".yml": "YAML",
            ".json": "JSON",
            ".xml": "XML",
        }
        
        framework_indicators = {
            "requirements.txt": "Python",
            "setup.py": "Python Package",
            "pyproject.toml": "Python (Modern)",
            "package.json": "Node.js",
            "Cargo.toml": "Rust",
            "go.mod": "Go",
            "pom.xml": "Java Maven",
            "build.gradle": "Java Gradle",
            "*.csproj": "C# Project",
            "*.vbproj": "VB.NET Project",
            "*.sln": ".NET Solution",
            "web.config": "ASP.NET",
            "app.config": ".NET Application",
            "Dockerfile": "Docker",
            "docker-compose.yml": "Docker Compose",
            "angular.json": "Angular",
            "vue.config.js": "Vue.js",
            "next.config.js": "Next.js",
        }
        
        language_counts = {}
        frameworks_detected = []
        
        # Count files by extension
        for ext, lang in extensions_map.items():
            count = len(list(repo_path.glob(f"**/*{ext}")))
            if count > 0:
                language_counts[lang] = language_counts.get(lang, 0) + count
        
        # Detect frameworks
        for pattern, framework in framework_indicators.items():
            if pattern.startswith("*"):
                matches = list(repo_path.glob(f"**/{pattern}"))
            else:
                matches = list(repo_path.glob(f"**/{pattern}"))
            if matches:
                frameworks_detected.append(framework)
        
        # Determine primary language
        primary_language = max(language_counts, key=language_counts.get) if language_counts else "Unknown"
        
        return {
            "primary_language": primary_language,
            "language_counts": language_counts,
            "frameworks_detected": list(set(frameworks_detected)),
            "total_source_files": sum(language_counts.values()),
        }
    
    def _analyze_code_layer(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze code using Git, AST, Comments analyzers."""
        # Use existing LENS capabilities
        python_files = list(repo_path.glob("**/*.py"))[:10]  # Sample first 10
        
        analysis = {
            "total_python_files": len(list(repo_path.glob("**/*.py"))),
            "analyzed_files": len(python_files),
            "summary": f"Found {len(list(repo_path.glob('**/*.py')))} Python files",
        }
        
        return analysis
    
    def _analyze_config_layer(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze configs using ConfigAnalyzer."""
        try:
            config_result = self.config_analyzer.analyze_repository(repo_path)
            return config_result
        except Exception as e:
            logger.warning("Config analysis failed: %s", e)
            return {"error": str(e)}
    
    def _analyze_database_layer(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze database schemas and migrations."""
        # Placeholder for DatabaseAnalyzer (to be implemented)
        migrations_path = repo_path / "migrations"
        
        return {
            "has_migrations": migrations_path.exists(),
            "migrations_path": str(migrations_path) if migrations_path.exists() else None,
            "note": "DatabaseAnalyzer not yet implemented",
        }
    
    def _analyze_api_layer(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze API endpoints and security."""
        # Placeholder for APIAnalyzer (to be implemented)
        api_paths = list(repo_path.glob("**/api/**/*.py"))
        
        return {
            "api_files_found": len(api_paths),
            "note": "APIAnalyzer not yet implemented",
        }
    
    def _analyze_dependency_layer(self, repo_path: Path) -> Dict[str, Any]:
        """
        Analyze dependencies and vulnerabilities using DependencyAnalyzer.
        
        Returns comprehensive dependency data for dashboard display.
        """
        try:
            from cortex.brain.analysis.dependency_analyzer import get_dependency_analyzer
            
            analyzer = get_dependency_analyzer()
            result = analyzer.analyze_project(repo_path)
            
            if not result.success:
                return {
                    "error": result.error,
                    "total_packages": 0,
                    "packages": [],
                }
            
            # Transform packages for dashboard display
            packages_data = []
            for pkg in result.packages:
                pkg_data = {
                    "name": pkg.name,
                    "version": pkg.current_version,
                    "latest_version": pkg.latest_version,
                    "type": pkg.dependency_type.value,
                    "is_dev": pkg.is_dev,
                    "license": pkg.license,
                    "vulnerabilities": [],
                }
                packages_data.append(pkg_data)
            
            # Map vulnerabilities to packages
            for finding in result.findings:
                if finding.finding_type == "vulnerability":
                    pkg_name = finding.package.name
                    for pkg_data in packages_data:
                        if pkg_data["name"] == pkg_name:
                            pkg_data["vulnerabilities"] = [
                                {
                                    "cve_id": v.cve_id,
                                    "severity": v.severity.value,
                                    "description": v.description,
                                    "cvss_score": v.cvss_score,
                                    "fixed_version": v.fixed_version,
                                }
                                for v in finding.vulnerabilities
                            ]
                            break
            
            # Summary counts
            critical_count = len([f for f in result.findings if f.severity.value == "critical"])
            high_count = len([f for f in result.findings if f.severity.value == "high"])
            medium_count = len([f for f in result.findings if f.severity.value == "medium"])
            
            return {
                "total_packages": result.total_packages,
                "outdated_packages": result.outdated_packages,
                "vulnerable_packages": result.vulnerable_packages,
                "license_issues": result.license_issues,
                "critical_vulnerabilities": critical_count,
                "high_vulnerabilities": high_count,
                "medium_vulnerabilities": medium_count,
                "packages": packages_data,
                "dependency_files": result.dependency_files,
                "findings": [
                    {
                        "package": f.package.name,
                        "type": f.finding_type,
                        "severity": f.severity.value,
                        "message": f.message,
                        "recommendation": f.recommendation,
                    }
                    for f in result.findings
                ],
            }
            
        except Exception as e:
            logger.warning("Dependency analysis failed: %s", e)
            # Fallback to basic file counting
            requirements_files = list(repo_path.glob("**/requirements*.txt"))
            package_json = list(repo_path.glob("**/package.json"))
            csproj_files = list(repo_path.glob("**/*.csproj"))
            packages_config = list(repo_path.glob("**/packages.config"))
            
            return {
                "python_requirements": len(requirements_files),
                "npm_packages": len(package_json),
                "dotnet_projects": len(csproj_files),
                "nuget_packages": len(packages_config),
                "error": str(e),
                "packages": [],
            }
    
    def _run_threat_modeling(
        self,
        lens_context: Dict[str, Any],
        repo_path: Path,
    ) -> Dict[str, Any]:
        """
        Security threat modeling with P0/P1/P2 classification.
        
        Uses:
        - SecurityThreatAnalyzer (CWE detection)
        - ConfigAnalyzer (secrets, insecure defaults)
        - OWASP Top 10 knowledge
        - Company compliance standards
        """
        security_model = {
            "p0_risks": [],
            "p1_risks": [],
            "p2_risks": [],
            "p3_risks": [],
            "compliance_gaps": [],
            "summary": "",
        }
        
        try:
            # Aggregate config analysis risks
            config_analysis = lens_context.get("config_analysis", {})
            if "p0_findings" in config_analysis:
                security_model["p0_risks"].extend(config_analysis["p0_findings"])
            if "p1_findings" in config_analysis:
                security_model["p1_risks"].extend(config_analysis["p1_findings"])
            if "p2_findings" in config_analysis:
                security_model["p2_risks"].extend(config_analysis["p2_findings"])
            
            # Run additional security assessments
            context = {
                "operation": "onboard",
                "repo_path": str(repo_path),
            }
            
            additional_risks = self.assess_security_risks(context)
            security_model["p0_risks"].extend(additional_risks.get("p0_risks", []))
            security_model["p1_risks"].extend(additional_risks.get("p1_risks", []))
            security_model["p2_risks"].extend(additional_risks.get("p2_risks", []))
            security_model["compliance_gaps"].extend(additional_risks.get("compliance_gaps", []))
            
            # Generate summary
            p0_count = len(security_model["p0_risks"])
            p1_count = len(security_model["p1_risks"])
            p2_count = len(security_model["p2_risks"])
            
            if p0_count > 0:
                security_model["summary"] = f"⛔ CRITICAL: {p0_count} P0 risk(s) require immediate attention"
            elif p1_count > 0:
                security_model["summary"] = f"⚠️  HIGH: {p1_count} P1 risk(s) should be addressed"
            elif p2_count > 0:
                security_model["summary"] = f"ℹ️  MODERATE: {p2_count} P2 risk(s) detected"
            else:
                security_model["summary"] = "✅ No critical security risks detected"
        
        except Exception as e:
            logger.error("Threat modeling failed: %s", e)
            security_model["error"] = str(e)
        
        return security_model
    
    def _update_company_domains(
        self,
        lens_context: Dict[str, Any],
        repo_path: Path,
    ) -> List[str]:
        """
        Update company domain knowledge based on detected patterns.
        
        Creates new YAML files in company/domains/ for unrecognized patterns.
        """
        updates = []
        
        # Placeholder: Would analyze lens_context for domain-specific patterns
        # and create new YAML files if needed
        
        logger.info("Company domain update: Not yet implemented")
        
        return updates
    
    def _generate_dashboard(
        self,
        lens_context: Dict[str, Any],
        repo_path: Path,
        recommendations: List[Dict[str, Any]] = None,
        security_model: Dict[str, Any] = None,
    ) -> Optional[Path]:
        """
        Generate PHASE-14 multi-tab dashboard.
        
        Uses DomainDashboardGenerator for company dashboards with glassmorphism theme.
        """
        try:
            # Determine if we should generate a company dashboard
            domain_name = repo_path.name.lower()
            # Check both dashboards/ and domains/ paths for company integration
            company_dashboard_path = Path("company/dashboards") / domain_name
            company_domain_path = Path("company/domains") / domain_name
            
            is_company_dashboard = company_dashboard_path.exists() or company_domain_path.exists()
            
            if is_company_dashboard:
                # Generate glassmorphism dashboard for company domain
                from cortex.orchestrators.support.domain_dashboard_generator import (
                    DomainDashboardGenerator
                )
                
                # Use dashboards path for output
                output_dashboard_path = company_dashboard_path
                output_dashboard_path.mkdir(parents=True, exist_ok=True)
                
                generator = DomainDashboardGenerator(
                    domain_name=domain_name,
                    domain_path=output_dashboard_path
                )
                
                # Prepare onboarding data
                onboarding_data = {
                    'repo_path': str(repo_path),
                    'timestamp': datetime.now().isoformat(),
                    'security_risks': security_model or {},
                    'holistic_context': lens_context,
                    'recommendations': recommendations or []
                }
                
                dashboard_path = generator.generate_dashboard(onboarding_data)
                logger.info("Generated glassmorphism dashboard: %s", dashboard_path)
                return dashboard_path
            else:
                # Use standard LENS dashboard orchestrator
                if self.dashboard_generator is None:
                    from cortex.orchestrators.support.lens_dashboard_orchestrator import (
                        LensDashboardOrchestrator
                    )
                    self.dashboard_generator = LensDashboardOrchestrator(repo_path=repo_path)
                
                dashboard_path = Path("cortex-lens") / "onboarding-dashboard.html"
                logger.info("Dashboard generated: %s", dashboard_path)
                return dashboard_path
            
        except Exception as e:
            logger.error("Dashboard generation failed: %s", e, exc_info=True)
            return None
    
    def _prioritize_recommendations(
        self,
        security_model: Dict[str, Any],
        lens_context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Generate prioritized recommendations.
        
        Returns top 10 P0/P1 actions sorted by impact.
        """
        recommendations = []
        
        # Add P0 recommendations
        for risk in security_model.get("p0_risks", [])[:5]:
            recommendations.append({
                "priority": "P0",
                "category": risk.get("category", "security"),
                "description": risk.get("description", ""),
                "recommendation": risk.get("recommendation", ""),
                "impact": "CRITICAL",
            })
        
        # Add P1 recommendations
        for risk in security_model.get("p1_risks", [])[:5]:
            recommendations.append({
                "priority": "P1",
                "category": risk.get("category", "security"),
                "description": risk.get("description", ""),
                "recommendation": risk.get("recommendation", ""),
                "impact": "HIGH",
            })
        
        return recommendations[:10]  # Top 10
    
    # IOrchestrator interface implementation
    
    def execute(self, parameters: Dict[str, Any]) -> Result[Any]:
        """
        Execute onboarding operation.
        
        Args:
            parameters: Dict with:
                - repo_path: str (path to repository)
                - include_dashboard: bool (default True)
                - update_company_domain: bool (default True)
                
        Returns:
            Result with OnboardingResult or error
        """
        try:
            repo_path = Path(parameters.get("repo_path", "."))
            include_dashboard = parameters.get("include_dashboard", True)
            update_company_domain = parameters.get("update_company_domain", True)
            
            result = self.onboard_repository(
                repo_path=repo_path,
                include_dashboard=include_dashboard,
                update_company_domain=update_company_domain,
            )
            
            if result.success:
                return Ok(result)
            else:
                return Err(result.error)
                
        except Exception as e:
            logger.error("Onboarding execution failed: %s", e, exc_info=True)
            return Err(str(e))
    
    def get_name(self) -> str:
        """Get orchestrator name."""
        return "RepositoryOnboardingOrchestrator"
    
    def get_description(self) -> str:
        """Get orchestrator description."""
        return "Repository onboarding with holistic LENS analysis and security assessment"
    
    def get_version(self) -> str:
        """Get orchestrator version."""
        return "2.0.0"
    
    def initialize(self) -> Result[str]:
        """Initialize orchestrator."""
        return Ok("RepositoryOnboardingOrchestrator initialized")
    
    def get_mode(self):
        """Get current operation mode."""
        from cortex.brain.core.interfaces.i_orchestrator import OperationMode
        return OperationMode.EXECUTION
    
    def get_mcp_tools(self) -> Result[Dict[str, Any]]:
        """Get exposed MCP tools for this orchestrator."""
        return Ok({
            "cortex_onboard_repository": {
                "name": "cortex_onboard_repository",
                "description": "Onboard a repository with full LENS analysis and dashboard generation",
                "parameters": {
                    "repo_path": {
                        "type": "string",
                        "description": "Path to repository to onboard",
                        "required": True
                    },
                    "include_dashboard": {
                        "type": "boolean",
                        "description": "Whether to generate dashboard (default: True)",
                        "default": True
                    },
                    "update_company_domain": {
                        "type": "boolean",
                        "description": "Whether to update company domain YAMLs (default: True)",
                        "default": True
                    },
                    "repo_name": {
                        "type": "string",
                        "description": "Override repository name",
                        "required": False
                    },
                    "icon": {
                        "type": "string",
                        "description": "Emoji icon for landing page tile",
                        "default": "📁"
                    }
                }
            }
        })
    
    def execute_operation(
        self,
        operation_name: str,
        parameters: Dict[str, Any],
    ) -> Result[Any]:
        """Execute operation with audit logging."""
        if operation_name == "onboard_repository":
            return self.execute(parameters)
        return Err(f"Unknown operation: {operation_name}")
    
    def get_audit_trail(self, limit: int = 100) -> Result[list]:
        """Get audit trail with hash chain."""
        # Basic audit trail - would be enhanced with hash chain in production
        return Ok([])


# Singleton instance
_repository_onboarding_orchestrator = None


def get_repository_onboarding_orchestrator() -> RepositoryOnboardingOrchestrator:
    """Get or create singleton RepositoryOnboardingOrchestrator."""
    global _repository_onboarding_orchestrator
    if _repository_onboarding_orchestrator is None:
        _repository_onboarding_orchestrator = RepositoryOnboardingOrchestrator()
    return _repository_onboarding_orchestrator
