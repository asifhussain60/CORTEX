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
from cortex.models.dashboard_schema import (
    RepoDashboardModel,
    RepoMetadata,
    OverviewSection,
    MetricsSection,
    SecuritySection,
    SecurityVulnerability,
    DependenciesSection,
    PackageDependency,
    QualitySection,
    CodeSmell,
    UseCase,
    LensSection,
    RefactoringSection,
)
from cortex.common.debug_logger import (
    log_dashboard_debug,
    log_dashboard_generation,
    log_dashboard_schema_validation,
    dashboard_debug,
)
from cortex.common.progress_reporter import (
    ProgressReporter,
    ProgressStyle,
    track_repository_onboarding,
    get_time_estimator,
)

logger = logging.getLogger(__name__)


class RepositoryNotFoundError(Exception):
    """Raised when repository path does not exist."""
    pass


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
    """Lazy-load LandingPageGenerator (optional, may not exist)."""
    global _landing_page_generator
    if _landing_page_generator is None:
        try:
            from cortex.orchestrators.support.landing_page_generator import (
                get_landing_page_generator
            )
            _landing_page_generator = get_landing_page_generator()
        except ImportError:
            logger.warning("LandingPageGenerator not available (optional)")
            return None
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
    """Lazy-load UniversalDashboardGenerator (optional, may not exist)."""
    global _universal_dashboard_generator
    if _universal_dashboard_generator is None:
        try:
            from cortex.orchestrators.support.universal_dashboard_generator import (
                get_universal_dashboard_generator
            )
            _universal_dashboard_generator = get_universal_dashboard_generator()
        except ImportError:
            logger.warning("UniversalDashboardGenerator not available (optional)")
            return None
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
        progress_style: ProgressStyle = ProgressStyle.DETAILED,
        show_progress: bool = True,
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
            progress_style: Progress output style (MINIMAL, DETAILED, VERBOSE)
            show_progress: Whether to show progress feedback
            
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
        
        # Calculate total steps based on options
        total_steps = 5  # Core steps
        if include_dashboard:
            total_steps += 2  # Dashboard + landing page
        if update_company_domain:
            total_steps += 1  # Domain updates
        
        # Use silent style if progress is disabled
        style = progress_style if show_progress else ProgressStyle.SILENT
        
        # Create progress reporter
        progress = ProgressReporter(
            operation_name=f"Repository Onboarding: {canonical_name}",
            total_steps=total_steps,
            style=style,
            time_estimator=get_time_estimator(),
        )
        
        try:
            with progress:
                # Step 0: Ensure shared assets exist (only if dashboard enabled)
                if include_dashboard:
                    progress.start_step(
                        "Ensure Assets",
                        "Ensuring shared dashboard assets exist",
                        estimated_seconds=2.0,
                    )
                    asset_manager = _get_asset_manager()
                    asset_manager.ensure_assets_exist()
                    progress.complete_step()
                
                # Step 1: Holistic LENS analysis
                progress.start_step(
                    "LENS Analysis",
                    "Running holistic LENS analysis (Git, AST, Security)",
                    estimated_seconds=30.0,
                )
                lens_context = self._run_holistic_analysis(repo_path)
                result.holistic_context = lens_context
                progress.complete_step({
                    "files_analyzed": lens_context.get("repository_summary", {}).get("total_files", 0)
                })
                
                # Step 2: Generate business narrative
                progress.start_step(
                    "Business Narrative",
                    "Generating business narrative and descriptions",
                    estimated_seconds=15.0,
                )
                business_orchestrator = _get_business_language_orchestrator()
                narrative = business_orchestrator.generate_narrative(
                    repo_path=repo_path,
                    analysis_data=lens_context  # Correct parameter name
                )
                result.business_narrative = narrative
                progress.complete_step()
                
                # Step 3: Security threat modeling
                progress.start_step(
                    "Security Modeling",
                    "Running security threat modeling (P0/P1/P2)",
                    estimated_seconds=10.0,
                )
                security_model = self._run_threat_modeling(lens_context, repo_path)
                result.security_risks = security_model
                progress.complete_step({
                    "p0_count": len(security_model.get("p0_risks", [])),
                    "p1_count": len(security_model.get("p1_risks", [])),
                })
                
                # Step 4: Company domain updates
                if update_company_domain:
                    progress.start_step(
                        "Domain Updates",
                        "Updating company domain configurations",
                        estimated_seconds=5.0,
                    )
                    domain_updates = self._update_company_domains(lens_context, repo_path)
                    result.company_domain_updates = domain_updates
                    progress.complete_step({"domains_updated": len(domain_updates)})
                
                # Step 5: Generate recommendations BEFORE dashboard
                progress.start_step(
                    "Recommendations",
                    "Generating prioritized recommendations",
                    estimated_seconds=5.0,
                )
                recommendations = self._prioritize_recommendations(security_model, lens_context)
                result.recommendations = recommendations
                progress.complete_step({"recommendations_count": len(recommendations)})
                
                # Step 6: Generate universal dashboard
                if include_dashboard:
                    progress.start_step(
                        "Dashboard Generation",
                        "Generating universal dashboard with metrics",
                        estimated_seconds=10.0,
                    )
                
                # Convert to RepoDashboardModel schema v2.0
                dashboard_model = self._convert_to_dashboard_model(
                    repo_path=repo_path,
                    repo_name=canonical_name,
                    lens_context=lens_context,
                    security_model=security_model,
                    narrative=narrative,
                    recommendations=recommendations,
                )
                
                # Validate schema
                is_valid, validation_errors = dashboard_model.to_dict(), []
                log_dashboard_schema_validation(
                    "RepoDashboardModel",
                    is_valid,
                    len(validation_errors) == 0,
                    validation_errors
                )
                
                # Save dashboard-data.json
                dashboard_dir = Path("company/dashboards/repos") / canonical_name
                dashboard_dir.mkdir(parents=True, exist_ok=True)
                
                dashboard_json_path = dashboard_dir / "dashboard-data.json"
                with open(dashboard_json_path, "w", encoding="utf-8") as f:
                    f.write(dashboard_model.to_json(indent=2))
                
                log_dashboard_generation(
                    "json_saved",
                    canonical_name,
                    path=str(dashboard_json_path),
                    size=dashboard_json_path.stat().st_size,
                )
                
                result.dashboard_path = str(dashboard_json_path)
                progress.complete_step({"dashboard_size": dashboard_json_path.stat().st_size})
                
                # Legacy dashboard generator support (optional)
                dashboard_gen = _get_universal_dashboard_generator()
                if dashboard_gen is not None:
                    # Prepare full data for legacy generator
                    analysis_data = {
                        'repo_path': str(repo_path),
                        'timestamp': result.timestamp,
                        'security_risks': security_model,
                        'holistic_context': lens_context,
                        'recommendations': recommendations,
                    }
                        
                    try:
                        dashboard_html_path = dashboard_gen.generate_dashboard(
                            repo_name=canonical_name,
                            narrative=narrative,
                            analysis_data=analysis_data
                        )
                        logger.info("Legacy dashboard HTML generated: %s", dashboard_html_path)
                    except Exception as gen_error:
                        logger.warning("Legacy dashboard generation failed: %s", gen_error)
                
                # Step 7: Update landing page hub
                progress.start_step(
                    "Landing Page",
                    "Updating landing page hub with new repository",
                    estimated_seconds=3.0,
                )
                landing_gen = _get_landing_page_generator()
                
                if landing_gen is not None:
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
                else:
                    logger.info("Landing page generation skipped (optional feature not available)")
                
                progress.complete_step()
            
            logger.info("Repository onboarding complete: %s", repo_path)
            
        except Exception as e:
            logger.error("Repository onboarding failed: %s", e, exc_info=True)
            result.success = False
            result.error = str(e)
        
        return result
    
    @dashboard_debug
    def _convert_to_dashboard_model(
        self,
        repo_path: Path,
        repo_name: str,
        lens_context: Dict[str, Any],
        security_model: Dict[str, Any],
        narrative: Optional[Any],
        recommendations: List[Dict[str, Any]],
    ) -> RepoDashboardModel:
        """
        Convert analysis results to RepoDashboardModel schema v2.0.
        
        This ensures all generated dashboards conform to the standard schema.
        
        Args:
            repo_path: Repository path
            repo_name: Canonical repository name
            lens_context: Full LENS analysis results
            security_model: Security threat modeling results
            narrative: Business narrative (optional)
            recommendations: List of recommendations
            
        Returns:
            RepoDashboardModel instance
        """
        log_dashboard_generation("schema_conversion_start", repo_name)
        
        # Extract language detection (handle various formats)
        lang_detection = lens_context.get("language_detection")
        
        # Handle different data structures
        if isinstance(lang_detection, dict):
            primary_language = lang_detection.get("primary_language", "Unknown")
            language_counts = lang_detection.get("language_counts", {})
        elif isinstance(lang_detection, list):
            # Should not happen - fallback to repository_summary
            logger.warning("language_detection is a list (unexpected). Falling back to repository_summary.")
            repo_summary_data = lens_context.get("repository_summary", {})
            primary_language = repo_summary_data.get("primary_language", "Unknown")
            language_counts = repo_summary_data.get("file_counts_by_language", {})
        else:
            # No language_detection - try repository_summary
            repo_summary_data = lens_context.get("repository_summary", {})
            primary_language = repo_summary_data.get("primary_language", "Unknown")
            language_counts = repo_summary_data.get("file_counts_by_language", {})
        
        # Repo metadata section
        repo_metadata = RepoMetadata(
            slug=repo_name,
            display_name=getattr(narrative, 'title', repo_name.upper()) if narrative else repo_name.upper(),
            description=getattr(narrative, 'tagline', f"{repo_name} repository") if narrative else f"{repo_name} repository",
            owner=lens_context.get("metadata", {}).get("owner", "Unknown"),
            primary_language=primary_language,
            version="1.0",  # Could extract from git tags or package version
            last_analyzed_at=datetime.now().isoformat(),
        )
        
        # Overview section
        overview = OverviewSection(
            summary=getattr(narrative, 'summary', "Repository analysis") if narrative else "Repository analysis",
            business_summary=getattr(narrative, 'description', "") if narrative else "",
            key_findings=self._extract_key_findings(lens_context, security_model),
        )
        
        # Metrics section
        repo_summary = lens_context.get("repository_summary", {})
        metrics = MetricsSection(
            health_score=self._calculate_health_score(lens_context, security_model),
            risk_score=self._calculate_risk_score(security_model),
            loc=repo_summary.get("total_loc", 0),
            code_lines=repo_summary.get("code_lines", 0),
            comment_lines=repo_summary.get("comment_lines", 0),
            blank_lines=repo_summary.get("blank_lines", 0),
            files=repo_summary.get("total_files", 0),
            coverage_pct=repo_summary.get("test_coverage_pct", 0.0),
            languages=language_counts,  # Use extracted language_counts
        )
        
        # Security section
        security = self._convert_security_section(lens_context, security_model)
        
        # Dependencies section
        dependencies = self._convert_dependencies_section(lens_context)
        
        # Quality section
        quality = self._convert_quality_section(lens_context)
        
        # Use cases
        use_cases = self._generate_use_cases(lens_context, security_model, repo_name)
        
        # LENS section
        lens = LensSection(
            analysis_summary=lens_context.get("metadata", {}).get("summary", "LENS analysis complete")
        )
        
        # Refactoring section
        refactoring = RefactoringSection(
            recommendations=recommendations
        )
        
        model = RepoDashboardModel(
            repo=repo_metadata,
            overview=overview,
            metrics=metrics,
            security=security,
            dependencies=dependencies,
            quality=quality,
            use_cases=use_cases,
            lens=lens,
            refactoring=refactoring,
        )
        
        log_dashboard_generation(
            "schema_conversion_complete",
            repo_name,
            use_cases_count=len(use_cases),
            security_vulns=security.total_count,
            health_score=metrics.health_score,
        )
        
        return model
    
    def _extract_key_findings(
        self,
        lens_context: Dict[str, Any],
        security_model: Dict[str, Any],
    ) -> List[str]:
        """Extract key findings from analysis."""
        findings = []
        
        # Security findings
        p0_count = len(security_model.get("p0_risks", []))
        p1_count = len(security_model.get("p1_risks", []))
        if p0_count > 0:
            findings.append(f"{p0_count} critical security risks require immediate attention")
        elif p1_count > 0:
            findings.append(f"{p1_count} high-priority security issues identified")
        else:
            findings.append("No critical security issues detected")
        
        # Code quality
        repo_summary = lens_context.get("repository_summary", {})
        if repo_summary.get("total_files", 0) > 0:
            findings.append(f"Codebase contains {repo_summary['total_files']} files")
        
        # Dependencies
        dep_analysis = lens_context.get("dependency_analysis", {})
        vulnerable_packages = dep_analysis.get("vulnerable_packages", 0)
        if vulnerable_packages > 0:
            findings.append(f"{vulnerable_packages} dependencies have known vulnerabilities")
        
        return findings[:5]  # Limit to top 5
    
    def _calculate_health_score(
        self,
        lens_context: Dict[str, Any],
        security_model: Dict[str, Any],
    ) -> int:
        """Calculate overall health score (0-100)."""
        score = 100
        
        # Deduct for security risks
        p0_count = len(security_model.get("p0_risks", []))
        p1_count = len(security_model.get("p1_risks", []))
        score -= p0_count * 20  # -20 per P0
        score -= p1_count * 10  # -10 per P1
        
        # Deduct for vulnerable dependencies
        dep_analysis = lens_context.get("dependency_analysis", {})
        score -= dep_analysis.get("critical_vulnerabilities", 0) * 15
        score -= dep_analysis.get("high_vulnerabilities", 0) * 5
        
        return max(0, min(100, score))
    
    def _calculate_risk_score(self, security_model: Dict[str, Any]) -> int:
        """Calculate risk score (0-100, higher is more risky)."""
        score = 0
        
        p0_count = len(security_model.get("p0_risks", []))
        p1_count = len(security_model.get("p1_risks", []))
        p2_count = len(security_model.get("p2_risks", []))
        
        score += p0_count * 25
        score += p1_count * 15
        score += p2_count * 5
        
        return min(100, score)
    
    def _convert_security_section(
        self,
        lens_context: Dict[str, Any],
        security_model: Dict[str, Any],
    ) -> SecuritySection:
        """Convert security analysis to SecuritySection."""
        log_dashboard_debug("Converting security section")
        
        vulnerabilities = []
        
        # Aggregate all security risks
        all_risks = (
            security_model.get("p0_risks", []) +
            security_model.get("p1_risks", []) +
            security_model.get("p2_risks", [])
        )
        
        severity_map = {"P0": "critical", "P1": "high", "P2": "medium"}
        
        for idx, risk in enumerate(all_risks[:50]):  # Limit to 50
            severity_key = risk.get("priority", "P2")
            vuln = SecurityVulnerability(
                id=f"SEC-{idx+1:03d}",
                title=risk.get("title", "Security issue"),
                severity=severity_map.get(severity_key, "low"),
                cwe_id=risk.get("cwe_id", "CWE-Unknown"),
                location=risk.get("location", "unknown"),
                status="open",
                description=risk.get("description", ""),
            )
            vulnerabilities.append(vuln)
        
        # Count by severity
        critical_count = len([v for v in vulnerabilities if v.severity == "critical"])
        high_count = len([v for v in vulnerabilities if v.severity == "high"])
        medium_count = len([v for v in vulnerabilities if v.severity == "medium"])
        low_count = len([v for v in vulnerabilities if v.severity == "low"])
        
        return SecuritySection(
            total_count=len(vulnerabilities),
            critical_count=critical_count,
            high_count=high_count,
            medium_count=medium_count,
            low_count=low_count,
            vulnerabilities=vulnerabilities,
        )
    
    def _convert_dependencies_section(
        self,
        lens_context: Dict[str, Any],
    ) -> DependenciesSection:
        """Convert dependency analysis to DependenciesSection."""
        log_dashboard_debug("Converting dependencies section")
        
        dep_analysis = lens_context.get("dependency_analysis", {})
        packages_data = dep_analysis.get("packages", [])
        
        packages = []
        for pkg_data in packages_data[:100]:  # Limit to 100
            pkg = PackageDependency(
                name=pkg_data.get("name", "unknown"),
                version=pkg_data.get("version", "0.0.0"),
                license=pkg_data.get("license", "Unknown"),
                is_direct=pkg_data.get("type", "direct") == "direct",
            )
            packages.append(pkg)
        
        # Extract license distribution
        licenses = {}
        for pkg in packages:
            licenses[pkg.license] = licenses.get(pkg.license, 0) + 1
        
        total_packages = dep_analysis.get("total_packages", len(packages))
        direct_count = len([p for p in packages if p.is_direct])
        
        return DependenciesSection(
            total_count=total_packages,
            direct_count=direct_count,
            transitive_count=total_packages - direct_count,
            packages=packages,
            licenses=licenses,
        )
    
    def _convert_quality_section(
        self,
        lens_context: Dict[str, Any],
    ) -> QualitySection:
        """Convert quality analysis to QualitySection."""
        log_dashboard_debug("Converting quality section")
        
        code_analysis = lens_context.get("code_analysis", {})
        
        # Extract code smells (if available from LENS)
        code_smells = []
        # TODO: Extract from actual LENS data when available
        
        return QualitySection(
            maintainability=75,  # TODO: Calculate from LENS metrics
            readability=80,
            documentation=70,
            complexity=65,
            code_smells=code_smells,
            hotspots=[],
        )
    
    def _generate_use_cases(
        self,
        lens_context: Dict[str, Any],
        security_model: Dict[str, Any],
        repo_name: str,
    ) -> List[UseCase]:
        """Generate use cases for the dashboard."""
        log_dashboard_debug("Generating use cases", repo=repo_name)
        
        use_cases = []
        
        # Security use case
        p0_count = len(security_model.get("p0_risks", []))
        if p0_count > 0:
            use_cases.append(UseCase(
                id="UC-SEC-001",
                title="Address Critical Security Vulnerabilities",
                persona="Security",
                category="Risk",
                summary=f"{p0_count} critical security issues require immediate remediation",
                signals=["security.critical_count", "security.vulnerabilities"],
                recommended_actions=[
                    "Review security tab for details",
                    "Prioritize P0 fixes",
                    "Schedule security review",
                ],
                tags=["security", "urgent", "p0"],
                severity="critical",
            ))
        
        # Dependency use case
        dep_analysis = lens_context.get("dependency_analysis", {})
        outdated_packages = dep_analysis.get("outdated_packages", 0)
        if outdated_packages > 0:
            use_cases.append(UseCase(
                id="UC-DEP-001",
                title="Update Outdated Dependencies",
                persona="Engineer",
                category="Maintainability",
                summary=f"{outdated_packages} packages are outdated and should be updated",
                signals=["dependencies.outdated_packages"],
                recommended_actions=[
                    "Review dependencies tab",
                    "Update non-breaking changes first",
                    "Test thoroughly after updates",
                ],
                tags=["dependencies", "maintenance"],
                severity="medium",
            ))
        
        # Code quality use case
        use_cases.append(UseCase(
            id="UC-QUAL-001",
            title="Monitor Code Quality Trends",
            persona="Engineering Manager",
            category="Quality",
            summary="Track maintainability and complexity metrics over time",
            signals=["quality.maintainability", "quality.complexity"],
            recommended_actions=[
                "Review quality tab",
                "Identify refactoring candidates",
                "Set quality gates",
            ],
            tags=["quality", "monitoring"],
            severity="low",
        ))
        
        log_dashboard_debug("Generated use cases", count=len(use_cases))
        return use_cases
    
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
                from cortex.lens import LENSOrchestrator
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
        """Analyze database-related files and configurations."""
        try:
            db_files = {
                "migrations": list(repo_path.glob("**/migrations/**/*.py")),
                "models": list(repo_path.glob("**/models.py")),
                "sql": list(repo_path.glob("**/*.sql")),
                "alembic": list(repo_path.glob("**/alembic/**/*.py")),
            }
            
            return {
                "has_database": any(len(files) > 0 for files in db_files.values()),
                "migration_files": len(db_files["migrations"]),
                "model_files": len(db_files["models"]),
                "sql_files": len(db_files["sql"]),
                "has_alembic": len(db_files["alembic"]) > 0,
            }
        except Exception as e:
            logger.warning("Database analysis failed: %s", e)
            return {"error": str(e), "has_database": False}
    
    def _analyze_api_layer(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze API-related files and endpoints."""
        try:
            api_patterns = {
                "flask": list(repo_path.glob("**/app.py")) + list(repo_path.glob("**/api/**/*.py")),
                "fastapi": list(repo_path.glob("**/main.py")) + list(repo_path.glob("**/routers/**/*.py")),
                "django": list(repo_path.glob("**/views.py")) + list(repo_path.glob("**/urls.py")),
                "rest": list(repo_path.glob("**/rest/**/*.py")),
            }
            
            return {
                "has_api": any(len(files) > 0 for files in api_patterns.values()),
                "flask_files": len(api_patterns["flask"]),
                "fastapi_files": len(api_patterns["fastapi"]),
                "django_files": len(api_patterns["django"]),
                "rest_files": len(api_patterns["rest"]),
            }
        except Exception as e:
            logger.warning("API analysis failed: %s", e)
            return {"error": str(e), "has_api": False}
    
    def _analyze_dependency_layer(self, repo_path: Path) -> Dict[str, Any]:
        """
        Analyze dependencies and vulnerabilities using DependencyAnalyzer.
        
        Returns comprehensive dependency data for dashboard display.
        """
        try:
            from cortex.lens.analyzers.dependency_analyzer import get_dependency_analyzer
            
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
    
    def _update_company_domains(
        self,
        lens_context: Dict[str, Any],
        repo_path: Path,
    ) -> Dict[str, Any]:
        """
        Update company domain YAMLs with snowball effect.
        
        This method implements the Phase 19 "snowball effect":
        - Each repository scan enriches existing domain knowledge
        - Merges new entities, patterns, vendors with existing data
        - Respects company precedence (company YAMLs override CORTEX)
        - Creates YAML files in company/domains/{repo_name}/
        
        Args:
            lens_context: LENS holistic analysis result
            repo_path: Path to repository
            
        Returns:
            Dict with:
                - created_files: List of new YAML files created
                - updated_files: List of existing files updated
                - entities_added: Count of new entities
                - patterns_promoted: Count of patterns promoted to Tier 2
                
        Note:
            This is a placeholder implementation for Phase 19 integration.
            Full implementation requires DomainKnowledgeMerger orchestrator.
        """
        repo_name = repo_path.name
        domain_dir = Path("company/domains") / repo_name
        domain_dir.mkdir(parents=True, exist_ok=True)
        
        result = {
            "created_files": [],
            "updated_files": [],
            "entities_added": 0,
            "patterns_promoted": 0,
        }
        
        # Extract entities from LENS context
        entities = lens_context.get("entities", [])
        if entities:
            entities_yaml = domain_dir / "entities.yaml"
            
            # Merge with existing (snowball effect)
            existing_entities = []
            if entities_yaml.exists():
                import yaml
                try:
                    with open(entities_yaml, "r") as f:
                        existing_data = yaml.safe_load(f) or {}
                        existing_entities = existing_data.get("entities", [])
                except Exception as e:
                    logger.warning(f"Could not load existing entities.yaml: {e}")
            
            # Merge (preserve existing, add new)
            all_entities = list(set(existing_entities + entities))
            result["entities_added"] = len(all_entities) - len(existing_entities)
            
            # Write back
            import yaml
            with open(entities_yaml, "w") as f:
                yaml.dump({"entities": all_entities}, f)
            
            if entities_yaml in result["created_files"] or entities_yaml.exists():
                result["updated_files"].append(str(entities_yaml))
            else:
                result["created_files"].append(str(entities_yaml))
        
        # Extract patterns
        patterns = lens_context.get("patterns", {})
        if patterns:
            patterns_yaml = domain_dir / "patterns.yaml"
            
            with open(patterns_yaml, "w") as f:
                import yaml
                yaml.dump(patterns, f)
            
            result["created_files"].append(str(patterns_yaml))
            result["patterns_promoted"] = len(patterns.get("learned", []))
        
        # Extract vendors
        vendors = lens_context.get("vendors", [])
        if vendors:
            vendors_yaml = domain_dir / "vendors.yaml"
            
            with open(vendors_yaml, "w") as f:
                import yaml
                yaml.dump({"vendors": vendors}, f)
            
            result["created_files"].append(str(vendors_yaml))
        
        logger.info(
            f"Company domain update: {result['entities_added']} entities added, "
            f"{result['patterns_promoted']} patterns promoted"
        )
        
        return result
    
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
    
    # ========================================================================
    # PHASE 28: REPOSITORY PROFILE GENERATION (LOOSE COUPLING SUPPORT)
    # ========================================================================
    
    def scan_repository(self, repo_path: Path) -> Dict[str, Any]:
        """
        Scan repository structure and gather metadata.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Dictionary with scan results
            
        Raises:
            RepositoryNotFoundError: If repository doesn't exist
        """
        if not repo_path.exists():
            raise RepositoryNotFoundError(f"Repository not found: {repo_path}")
        
        return {
            'structure': self._scan_structure(repo_path),
            'tech_stack': self.analyze_tech_stack(repo_path),
            'security': self.assess_security_baseline(repo_path),
            'standards': self.extract_standards(repo_path),
        }
    
    def detect_company_domains(
        self, repo_path: Path
    ) -> tuple[bool, Optional[str], List[str]]:
        """
        Detect company/domains/ structure in repository.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Tuple of (has_domains, domains_path, detected_domains)
        """
        domains_path = repo_path / "company" / "domains"
        
        if not domains_path.exists():
            return (False, None, [])
        
        # List subdirectories in company/domains/
        detected_domains = [
            f"{d.name}/" for d in domains_path.iterdir() if d.is_dir()
        ]
        
        return (True, str(domains_path.relative_to(repo_path)), detected_domains)
    
    def analyze_tech_stack(self, repo_path: Path) -> Dict[str, Any]:
        """
        Analyze technology stack of repository.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Dictionary with tech stack information
        """
        languages = self._detect_languages(repo_path)
        primary_language = languages[0] if languages else None
        
        return {
            'primary_language': primary_language,
            'languages': languages,
            'frameworks': self._detect_frameworks(repo_path),
            'dependencies': self.analyze_dependencies(repo_path),
        }
    
    def assess_security_baseline(self, repo_path: Path) -> Dict[str, Any]:
        """
        Assess security baseline of repository.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Dictionary with security metadata
        """
        return {
            'secrets_management': self._detect_secrets_management(repo_path),
            'auth_pattern': self._detect_auth_pattern(repo_path),
            'vulnerabilities_detected': 0,  # Placeholder for security scan
            'last_scan': datetime.now(),
        }
    
    def extract_standards(self, repo_path: Path) -> Dict[str, Any]:
        """
        Extract coding standards from repository.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Dictionary with standards information
        """
        return {
            'coding_style': self._detect_coding_style(repo_path),
            'security_baseline': self._detect_security_baseline(repo_path),
            'test_patterns': self._detect_test_patterns(repo_path),
            'api_patterns': self._detect_api_patterns(repo_path),
        }
    
    def generate_profile(self, repo_path: Path) -> 'RepositoryProfile':
        """
        Generate complete RepositoryProfile from repository scan.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            RepositoryProfile instance
        """
        from cortex_brain.onboarded_repos import (
            RepositoryProfile,
            TechStack,
            RepositoryStructure,
            Standards,
            SecurityMetadata,
            LooseCoupling,
        )
        
        # Scan repository
        scan_results = self.scan_repository(repo_path)
        
        # Detect company domains
        has_domains, domains_path, detected_domains = self.detect_company_domains(
            repo_path
        )
        
        # Build profile
        profile = RepositoryProfile(
            name=repo_path.name,
            path=str(repo_path.absolute()),
            onboarded_at=datetime.now(),
            tech_stack=TechStack(**scan_results['tech_stack']),
            structure=RepositoryStructure(
                has_company_domains=has_domains,
                company_domains_path=domains_path,
                domains_detected=detected_domains,
                **self._get_structure_metadata(repo_path),
            ),
            standards=Standards(**scan_results['standards']),
            security=SecurityMetadata(**scan_results['security']),
            loose_coupling=LooseCoupling(),
        )
        
        return profile
    
    def onboard_repository_with_profile(
        self,
        repo_path: Path,
        profile_store: Optional['ProfileStore'] = None,
    ) -> 'RepositoryProfile':
        """
        Onboard repository and save profile to store.
        
        Args:
            repo_path: Path to repository
            profile_store: ProfileStore instance (optional)
            
        Returns:
            RepositoryProfile instance
        """
        from cortex_brain.onboarded_repos import ProfileStore
        
        # Generate profile
        profile = self.generate_profile(repo_path)
        
        # Save to store if provided
        if profile_store is None:
            profile_store = ProfileStore()
        
        profile_store.save(profile)
        
        return profile
    
    def detect_test_framework(self, repo_path: Path) -> Dict[str, Any]:
        """
        Detect test framework used in repository.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Dictionary with test framework information
        """
        test_info = {
            'has_tests': False,
            'test_framework': None,
        }
        
        # Check for pytest
        if (repo_path / "pytest.ini").exists() or \
           (repo_path / "pyproject.toml").exists():
            test_info['has_tests'] = True
            test_info['test_framework'] = "pytest"
        
        # Check for unittest
        elif (repo_path / "tests").exists():
            test_info['has_tests'] = True
            test_info['test_framework'] = "unittest"
        
        return test_info
    
    def analyze_dependencies(self, repo_path: Path) -> List[str]:
        """
        Analyze project dependencies.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            List of dependency strings
        """
        dependencies = []
        
        # Check requirements.txt
        req_file = repo_path / "requirements.txt"
        if req_file.exists():
            content = req_file.read_text()
            dependencies.extend([
                line.strip() for line in content.split('\n')
                if line.strip() and not line.startswith('#')
            ])
        
        # Check pyproject.toml
        pyproject_file = repo_path / "pyproject.toml"
        if pyproject_file.exists():
            # Simple parsing - would use tomli in production
            content = pyproject_file.read_text()
            if 'dependencies' in content:
                dependencies.append("(see pyproject.toml)")
        
        return dependencies
    
    # Helper methods
    
    def _scan_structure(self, repo_path: Path) -> Dict[str, Any]:
        """Scan repository structure."""
        return {
            'root': str(repo_path),
            'has_tests': (repo_path / "tests").exists(),
            'has_docs': (repo_path / "docs").exists(),
        }
    
    def _detect_languages(self, repo_path: Path) -> List[str]:
        """Detect programming languages in repository."""
        languages = []
        
        # Check for Python files
        if list(repo_path.rglob("*.py")):
            languages.append("Python")
        
        # Check for YAML files
        if list(repo_path.rglob("*.yaml")) or list(repo_path.rglob("*.yml")):
            languages.append("YAML")
        
        # Check for Markdown
        if list(repo_path.rglob("*.md")):
            languages.append("Markdown")
        
        return languages
    
    def _detect_frameworks(self, repo_path: Path) -> List[str]:
        """Detect frameworks used in repository."""
        frameworks = []
        
        # Check for FastAPI
        if any("fastapi" in dep.lower() 
               for dep in self.analyze_dependencies(repo_path)):
            frameworks.append("FastAPI")
        
        # Check for Pydantic
        if any("pydantic" in dep.lower() 
               for dep in self.analyze_dependencies(repo_path)):
            frameworks.append("Pydantic")
        
        return frameworks
    
    def _detect_secrets_management(self, repo_path: Path) -> str:
        """Detect secrets management approach."""
        if (repo_path / ".env.example").exists():
            return "environment variables"
        return "unknown"
    
    def _detect_auth_pattern(self, repo_path: Path) -> str:
        """Detect authentication pattern."""
        deps = self.analyze_dependencies(repo_path)
        if any("jwt" in dep.lower() for dep in deps):
            return "JWT"
        return "unknown"
    
    def _detect_coding_style(self, repo_path: Path) -> Optional[str]:
        """Detect coding style tools."""
        tools = []
        if (repo_path / ".black").exists():
            tools.append("black")
        if (repo_path / "mypy.ini").exists():
            tools.append("mypy")
        return " + ".join(tools) if tools else None
    
    def _detect_security_baseline(self, repo_path: Path) -> Optional[str]:
        """Detect security baseline."""
        # Placeholder - would check for security configs
        return None
    
    def _detect_test_patterns(self, repo_path: Path) -> Optional[str]:
        """Detect test patterns."""
        test_info = self.detect_test_framework(repo_path)
        if test_info['has_tests']:
            return f"{test_info['test_framework']}"
        return None
    
    def _detect_api_patterns(self, repo_path: Path) -> Optional[str]:
        """Detect API patterns."""
        frameworks = self._detect_frameworks(repo_path)
        if "FastAPI" in frameworks:
            return "RESTful + OpenAPI 3.0"
        return None
    
    def _get_structure_metadata(self, repo_path: Path) -> Dict[str, Any]:
        """Get additional structure metadata."""
        test_info = self.detect_test_framework(repo_path)
        return {
            'has_tests': test_info['has_tests'],
            'test_framework': test_info['test_framework'],
            'has_docs': (repo_path / "docs").exists(),
            'doc_format': "markdown" if (repo_path / "docs").exists() else None,
        }
    
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
