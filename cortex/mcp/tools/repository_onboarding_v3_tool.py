"""
MCP Tool for Phase 21 Enterprise Repository Intelligence (SQLite v3.0).

Extends existing cortex_onboard_repository with SQLite-first architecture:
- Complete LENS analysis (security, architecture, metrics)
- LLM business language generation (use cases, impact, personas)
- SQLite dashboard.sqlite generation (13 tabs)
- Registry update (landing page tile)
- Validation pipeline

AC-ID: AC-P21-MCP-ONBOARD-001
Authority: PHASE-21-ENTERPRISE-REPOSITORY-INTELLIGENCE.yaml
"""

from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import json
import sqlite3

from cortex.mcp.decorators import mcp_tool

logger = logging.getLogger(__name__)


@mcp_tool(
    name="cortex_onboard_repository_v3",
    description="Onboard repository with LENS analysis + LLM business language + SQLite dashboard (Phase 21)",
    parameters={
        "repo_path": "string",
        "output_dir": "string",
        "slug": "string",
        "generate_business_language": "boolean",
        "update_registry": "boolean",
        "validate": "boolean",
    }
)
def cortex_onboard_repository_v3(
    repo_path: str,
    output_dir: str,
    slug: Optional[str] = None,
    generate_business_language: bool = True,
    update_registry: bool = True,
    validate: bool = True,
) -> Dict[str, Any]:
    """
    Onboard repository with full Phase 21 intelligence pipeline.
    
    Pipeline Steps:
    1. Schema Enhancement Check: Verify dashboard_schema_v3.py completeness
    2. LENS Analysis: Run complete repository scan (security, architecture, metrics)
    3. LLM Business Language: Generate use cases, personas, business impact
    4. SQLite Aggregation: Combine LENS + LLM into dashboard.sqlite
    5. Registry Update: Add tile to registry.sqlite landing page
    6. Validation: Verify database integrity, FTS5, views
    
    Args:
        repo_path: Path to repository to analyze (absolute or relative)
        output_dir: Directory for dashboard.sqlite and metadata.json
        slug: Repository slug (defaults to dirname of repo_path)
        generate_business_language: Whether to invoke LLM for business context
        update_registry: Whether to add/update registry tile
        validate: Whether to run post-generation validation
        
    Returns:
        Dict with:
        - success: bool
        - repo_path: str
        - slug: str
        - dashboard_path: str (path to dashboard.sqlite)
        - metadata_path: str (path to metadata.json)
        - registry_updated: bool
        - stats: Dict[str, int] (row counts per table)
        - validation_results: Dict[str, Any]
        - timestamp: str (ISO 8601)
        - error: str (if failed)
        
    Example:
        >>> result = cortex_onboard_repository_v3(
        ...     repo_path="/workspace/cortex",
        ...     output_dir="/data/dashboards/cortex",
        ...     slug="cortex"
        ... )
        >>> print(f"Dashboard: {result['dashboard_path']}")
        >>> print(f"Use cases: {result['stats']['use_cases']}")
    """
    start_time = datetime.now()
    repo_path_obj = Path(repo_path).resolve()
    output_dir_obj = Path(output_dir).resolve()
    
    # Default slug to directory name
    if not slug:
        slug = repo_path_obj.name.lower().replace(" ", "-")
    
    dashboard_path = output_dir_obj / "dashboard.sqlite"
    metadata_path = output_dir_obj / "metadata.json"
    
    try:
        # Step 1: Schema Enhancement Check
        logger.info(f"[P21-ONBOARD] Step 1: Schema Enhancement Check for {slug}")
        schema_check = _check_schema_enhancement()
        if not schema_check["valid"]:
            return {
                "success": False,
                "error": f"Schema validation failed: {schema_check['error']}",
                "repo_path": str(repo_path_obj),
                "slug": slug,
            }
        
        # Step 2: LENS Analysis
        logger.info(f"[P21-ONBOARD] Step 2: LENS Analysis for {slug}")
        lens_result = _run_lens_analysis(repo_path_obj)
        if not lens_result["success"]:
            return {
                "success": False,
                "error": f"LENS analysis failed: {lens_result['error']}",
                "repo_path": str(repo_path_obj),
                "slug": slug,
            }
        
        # Step 3: LLM Business Language Generation (optional)
        llm_result = None
        if generate_business_language:
            logger.info(f"[P21-ONBOARD] Step 3: LLM Business Language Generation for {slug}")
            llm_result = _generate_business_language(lens_result["data"], repo_path_obj)
            if not llm_result["success"]:
                logger.warning(f"LLM generation failed: {llm_result['error']}, continuing without business context")
        
        # Step 4: SQLite Aggregation
        logger.info(f"[P21-ONBOARD] Step 4: SQLite Aggregation for {slug}")
        output_dir_obj.mkdir(parents=True, exist_ok=True)
        
        aggregation_result = _aggregate_to_sqlite(
            lens_data=lens_result["data"],
            llm_data=llm_result["data"] if llm_result and llm_result["success"] else None,
            repo_path=repo_path_obj,
            dashboard_path=dashboard_path,
            slug=slug,
        )
        
        if not aggregation_result["success"]:
            return {
                "success": False,
                "error": f"SQLite aggregation failed: {aggregation_result['error']}",
                "repo_path": str(repo_path_obj),
                "slug": slug,
            }
        
        # Step 5: Registry Update (optional)
        registry_updated = False
        if update_registry:
            logger.info(f"[P21-ONBOARD] Step 5: Registry Update for {slug}")
            registry_result = _update_registry(
                slug=slug,
                repo_path=repo_path_obj,
                dashboard_path=dashboard_path,
                stats=aggregation_result["stats"],
            )
            registry_updated = registry_result["success"]
            if not registry_updated:
                logger.warning(f"Registry update failed: {registry_result['error']}")
        
        # Step 6: Validation (optional)
        validation_results = {}
        if validate:
            logger.info(f"[P21-ONBOARD] Step 6: Validation for {slug}")
            validation_results = _validate_dashboard(dashboard_path)
        
        # Generate metadata.json
        metadata = {
            "slug": slug,
            "repo_path": str(repo_path_obj),
            "generated_at": datetime.now().isoformat(),
            "lens_analysis": {
                "files_analyzed": lens_result["data"].get("files_analyzed", 0),
                "total_vulnerabilities": lens_result["data"].get("total_vulnerabilities", 0),
                "total_code_smells": lens_result["data"].get("total_code_smells", 0),
            },
            "business_language_generated": llm_result is not None and llm_result["success"],
            "stats": aggregation_result["stats"],
        }
        metadata_path.write_text(json.dumps(metadata, indent=2))
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        return {
            "success": True,
            "repo_path": str(repo_path_obj),
            "slug": slug,
            "dashboard_path": str(dashboard_path),
            "metadata_path": str(metadata_path),
            "registry_updated": registry_updated,
            "stats": aggregation_result["stats"],
            "validation_results": validation_results,
            "elapsed_seconds": round(elapsed, 2),
            "timestamp": datetime.now().isoformat(),
        }
        
    except Exception as e:
        logger.error(f"cortex_onboard_repository_v3 failed: {e}", exc_info=True)
        return {
            "success": False,
            "repo_path": str(repo_path_obj),
            "slug": slug,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


def _check_schema_enhancement() -> Dict[str, Any]:
    """
    Verify dashboard_schema_v3.py has all required models and enums.
    
    Returns:
        Dict with:
        - valid: bool
        - missing_models: List[str]
        - error: str (if invalid)
    """
    try:
        from cortex.models.dashboard_schema_v3 import (
            RepoSummary, UseCase, MetricsSummary, Vulnerability,
            Package, CodeSmell, Entity, Relationship, Component,
            FileEntry, TestResult, LENSInsight, RefactoringSuggestion,
            SeverityLevel, UseCaseType, ImpactLevel, TestStatus,
            SQLiteSchemaGenerator
        )
        
        # Verify schema generator can produce SQL
        schema_sql = SQLiteSchemaGenerator.generate_full_schema()
        if not schema_sql or len(schema_sql) < 1000:
            return {
                "valid": False,
                "error": "Schema generator produced incomplete SQL",
            }
        
        return {"valid": True, "missing_models": []}
        
    except ImportError as e:
        return {
            "valid": False,
            "error": f"Failed to import dashboard_schema_v3: {e}",
            "missing_models": [str(e)],
        }


def _run_lens_analysis(repo_path: Path) -> Dict[str, Any]:
    """
    Run complete LENS analysis (security, architecture, metrics).
    
    Delegates to existing cortex_onboard_repository (LENS v2.0).
    
    Returns:
        Dict with:
        - success: bool
        - data: Dict (LENS analysis results)
        - error: str (if failed)
    """
    try:
        from cortex.orchestrators.support.repository_onboarding_orchestrator import (
            get_repository_onboarding_orchestrator
        )
        
        orchestrator = get_repository_onboarding_orchestrator()
        result = orchestrator.onboard_repository(
            repo_path=repo_path,
            include_dashboard=False,  # We'll generate SQLite separately
            update_company_domain=False,
        )
        
        if not result.success:
            return {
                "success": False,
                "error": result.error or "LENS analysis failed",
            }
        
        # Extract relevant data from holistic context
        lens_data = {
            "files_analyzed": result.holistic_context.get("code_analysis", {}).get("files_analyzed", 0),
            "total_vulnerabilities": len(result.security_risks.get("p0_risks", [])) +
                                      len(result.security_risks.get("p1_risks", [])) +
                                      len(result.security_risks.get("p2_risks", [])),
            "vulnerabilities": result.security_risks,
            "recommendations": result.recommendations,
            "total_code_smells": 0,  # Extract from code_analysis if available
            "holistic_context": result.holistic_context,
        }
        
        return {
            "success": True,
            "data": lens_data,
        }
        
    except Exception as e:
        logger.error(f"LENS analysis failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
        }


def _generate_business_language(lens_data: Dict[str, Any], repo_path: Path) -> Dict[str, Any]:
    """
    Generate business language context via LLM (use cases, personas, impact).
    
    Placeholder for Phase 21 LLM integration.
    
    Args:
        lens_data: LENS analysis results
        repo_path: Repository path
        
    Returns:
        Dict with:
        - success: bool
        - data: Dict (use cases, personas, business impact)
        - error: str (if failed)
    """
    try:
        # TODO: Integrate with LLM orchestrator for business language generation
        # For now, generate placeholder data
        
        business_data = {
            "use_cases": [
                {
                    "id": "uc-001",
                    "title": f"Repository Analysis - {repo_path.name}",
                    "description": "Automated analysis and intelligence extraction from repository",
                    "use_case_type": "OPERATIONAL",
                    "impact_level": "HIGH",
                    "persona": "DevOps Engineer",
                    "business_value": "Automated code quality assessment",
                    "technical_implementation": "LENS crawler + SQLite aggregation",
                }
            ],
            "personas": ["DevOps Engineer", "Security Analyst", "Engineering Manager"],
            "business_impact": "Automated repository intelligence enables data-driven decisions",
        }
        
        return {
            "success": True,
            "data": business_data,
        }
        
    except Exception as e:
        logger.error(f"LLM business language generation failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
        }


def _aggregate_to_sqlite(
    lens_data: Dict[str, Any],
    llm_data: Optional[Dict[str, Any]],
    repo_path: Path,
    dashboard_path: Path,
    slug: str,
) -> Dict[str, Any]:
    """
    Aggregate LENS + LLM data into dashboard.sqlite.
    
    Args:
        lens_data: LENS analysis results
        llm_data: LLM business language (optional)
        repo_path: Repository path
        dashboard_path: Output dashboard.sqlite path
        slug: Repository slug
        
    Returns:
        Dict with:
        - success: bool
        - stats: Dict[str, int] (row counts per table)
        - error: str (if failed)
    """
    try:
        from cortex.visualization.sqlite_data_generator import SQLiteDataGenerator
        from cortex.models.dashboard_schema_v3 import (
            RepoSummary, UseCase, MetricsSummary, Vulnerability,
            Package, CodeSmell, Entity, Relationship, Component,
            FileEntry, TestResult, LENSInsight, RefactoringSuggestion,
            SeverityLevel, UseCaseType, ImpactLevel, TestStatus,
        )
        
        # Construct complete dashboard data structure
        dashboard_data = {
            "repo_summary": RepoSummary(
                slug=slug,
                name=repo_path.name,
                description=f"Repository intelligence for {repo_path.name}",
                repository_url=str(repo_path),
                primary_language="Python",  # TODO: Detect from LENS
                total_lines_of_code=lens_data.get("holistic_context", {}).get("code_analysis", {}).get("total_lines", 0),
                total_files=lens_data.get("files_analyzed", 0),
                analysis_timestamp=datetime.now().isoformat(),
            ),
            "use_cases": [],
            "metrics_summary": MetricsSummary(
                slug=slug,
                total_files=lens_data.get("files_analyzed", 0),
                total_lines=lens_data.get("holistic_context", {}).get("code_analysis", {}).get("total_lines", 0),
                average_complexity=5.0,  # TODO: Calculate from LENS
                high_complexity_files=0,
                code_duplication_percentage=0.0,
                test_coverage_percentage=0.0,
                total_vulnerabilities=lens_data.get("total_vulnerabilities", 0),
                critical_vulnerabilities=len(lens_data.get("vulnerabilities", {}).get("p0_risks", [])),
                total_code_smells=lens_data.get("total_code_smells", 0),
                major_code_smells=0,
            ),
            "vulnerabilities": [],
            "packages": [],
            "code_smells": [],
            "entities": [],
            "relationships": [],
            "components": [],
            "files": [],
            "test_results": [],
            "lens_insights": [],
            "refactoring_suggestions": [],
        }
        
        # Populate use cases from LLM data
        if llm_data and "use_cases" in llm_data:
            for uc_data in llm_data["use_cases"]:
                dashboard_data["use_cases"].append(UseCase(
                    id=uc_data.get("id", f"uc-{len(dashboard_data['use_cases']) + 1}"),
                    title=uc_data.get("title", ""),
                    description=uc_data.get("description", ""),
                    use_case_type=UseCaseType(uc_data.get("use_case_type", "OPERATIONAL")),
                    impact_level=ImpactLevel(uc_data.get("impact_level", "MEDIUM")),
                    persona=uc_data.get("persona", ""),
                    business_value=uc_data.get("business_value", ""),
                    technical_implementation=uc_data.get("technical_implementation", ""),
                ))
        
        # Populate vulnerabilities from LENS security risks
        vuln_id = 1
        for severity, risks in lens_data.get("vulnerabilities", {}).items():
            if severity in ["p0_risks", "p1_risks", "p2_risks"]:
                severity_map = {"p0_risks": "CRITICAL", "p1_risks": "HIGH", "p2_risks": "MEDIUM"}
                for risk in risks:
                    dashboard_data["vulnerabilities"].append(Vulnerability(
                        id=f"vuln-{vuln_id:03d}",
                        title=risk.get("description", "Unknown vulnerability"),
                        description=risk.get("recommendation", ""),
                        severity=SeverityLevel(severity_map[severity]),
                        cwe_id=risk.get("cwe_id"),
                        affected_file=risk.get("file_path", ""),
                        line_number=risk.get("line_number", 0),
                        remediation=risk.get("recommendation", ""),
                    ))
                    vuln_id += 1
        
        # Generate SQLite database
        generator = SQLiteDataGenerator(dashboard_path)
        generator.generate(dashboard_data, backup_existing=True)
        
        # Get row counts
        stats = generator.get_database_stats()
        
        return {
            "success": True,
            "stats": stats,
        }
        
    except Exception as e:
        logger.error(f"SQLite aggregation failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
        }


def _update_registry(
    slug: str,
    repo_path: Path,
    dashboard_path: Path,
    stats: Dict[str, int],
) -> Dict[str, Any]:
    """
    Update registry.sqlite with new repository tile.
    
    Args:
        slug: Repository slug
        repo_path: Repository path
        dashboard_path: Path to dashboard.sqlite
        stats: Row counts from dashboard
        
    Returns:
        Dict with:
        - success: bool
        - registry_id: int (if successful)
        - error: str (if failed)
    """
    try:
        from cortex.visualization.registry_manager_v3 import RegistryManagerV3
        
        # Default registry path
        registry_path = Path(__file__).parent.parent.parent.parent / "company" / "dashboards" / "registry.sqlite"
        
        manager = RegistryManagerV3(registry_path)
        registry_id = manager.add_repository(
            slug=slug,
            name=repo_path.name,
            description=f"Repository intelligence for {repo_path.name}",
            dashboard_url=f"/dashboards/{slug}/",
            total_files=stats.get("total_files", 0),
            total_vulnerabilities=stats.get("total_vulnerabilities", 0),
            critical_vulnerabilities=stats.get("critical_vulnerabilities", 0),
            total_use_cases=stats.get("total_use_cases", 0),
            analysis_timestamp=datetime.now().isoformat(),
        )
        
        return {
            "success": True,
            "registry_id": registry_id,
        }
        
    except Exception as e:
        logger.error(f"Registry update failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
        }


def _validate_dashboard(dashboard_path: Path) -> Dict[str, Any]:
    """
    Validate dashboard.sqlite integrity.
    
    Checks:
    - Database file exists and is valid SQLite
    - All required tables present
    - FTS5 tables functional
    - Views return data
    - No orphaned foreign keys
    
    Args:
        dashboard_path: Path to dashboard.sqlite
        
    Returns:
        Dict with validation results:
        - database_valid: bool
        - tables_present: List[str]
        - missing_tables: List[str]
        - fts_functional: bool
        - views_functional: bool
        - foreign_key_violations: List[Dict]
    """
    try:
        if not dashboard_path.exists():
            return {
                "database_valid": False,
                "error": "Dashboard file does not exist",
            }
        
        conn = sqlite3.connect(dashboard_path)
        cursor = conn.cursor()
        
        # Check all required tables
        required_tables = [
            "repo_summary", "use_cases", "metrics_summary", "vulnerabilities",
            "packages", "code_smells", "entities", "relationships", "components",
            "files", "test_results", "lens_insights", "refactoring_suggestions",
            "use_cases_fts", "packages_fts", "files_fts",
        ]
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = {row[0] for row in cursor.fetchall()}
        
        tables_present = [t for t in required_tables if t in existing_tables]
        missing_tables = [t for t in required_tables if t not in existing_tables]
        
        # Check FTS5 functionality
        fts_functional = True
        try:
            cursor.execute("SELECT COUNT(*) FROM use_cases_fts WHERE use_cases_fts MATCH 'test'")
            cursor.fetchone()
        except Exception as e:
            fts_functional = False
            logger.warning(f"FTS5 check failed: {e}")
        
        # Check views functionality
        views_functional = True
        try:
            cursor.execute("SELECT COUNT(*) FROM executive_kpis")
            cursor.fetchone()
        except Exception as e:
            views_functional = False
            logger.warning(f"Views check failed: {e}")
        
        # Check foreign key violations
        cursor.execute("PRAGMA foreign_key_check")
        fk_violations = [{"table": row[0], "rowid": row[1]} for row in cursor.fetchall()]
        
        conn.close()
        
        return {
            "database_valid": True,
            "tables_present": tables_present,
            "missing_tables": missing_tables,
            "fts_functional": fts_functional,
            "views_functional": views_functional,
            "foreign_key_violations": fk_violations,
        }
        
    except Exception as e:
        logger.error(f"Dashboard validation failed: {e}", exc_info=True)
        return {
            "database_valid": False,
            "error": str(e),
        }
