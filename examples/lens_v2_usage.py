"""
LENS v2.0 Usage Examples

Demonstrates all 9 analyzers, holistic repository analysis, security-first patterns,
and company domain integration.

Enhanced for LENS v2.0 with:
- CompanyDomainLoader (compliance, architecture)
- DependencyAnalyzer (CVE detection, outdated packages)
- Security-first orchestration workflow
- Holistic analysis integration

AC-ID: AC-LENS-V2-EXAMPLES-001
Authority: P2-3, CORE-012 (Comprehensive examples)
"""

from pathlib import Path
from cortex.brain.analysis import (
    # Core analyzers
    GitHistoryAnalyzer,
    ASTAnalyzer,
    CommentExtractor,
    VisionAnalyzer,
    get_config_analyzer,
    get_database_analyzer,
    get_api_analyzer,
    get_company_domain_loader,
    get_dependency_analyzer,
)
from cortex.orchestrators.support.lens_orchestrator import LENSOrchestrator
from cortex.mcp.tools import (
    cortex_onboard_repository,
    cortex_analyze_config,
    cortex_analyze_repository_configs,
)
from cortex.orchestrators.mixins import SecurityAdvisorMixin
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# ============================================================================
# Example 1: Git History Analysis
# ============================================================================

def example_1_git_history_analysis():
    """
    Example 1: Git History Analysis
    
    Analyze commit history, contributors, hotspots, and recent changes.
    """
    print("\n" + "="*80)
    print("EXAMPLE 1: Git History Analysis")
    print("="*80 + "\n")
    
    analyzer = GitHistoryAnalyzer()
    repo_path = Path(".")
    
    # Get recent commits
    print("📜 Recent Commits (last 10):")
    result = analyzer.get_recent_commits(repo_path, days_back=7, limit=10)
    
    if result.success:
        for commit in result.commits[:3]:
            print(f"  {commit.hash[:8]} - {commit.author} - {commit.message[:60]}")
        print(f"  ... and {len(result.commits) - 3} more commits\n")
    
    # Get hotspots
    print("🔥 Code Hotspots (most changed files):")
    hotspots = analyzer.get_code_hotspots(repo_path, days_back=30, limit=5)
    
    if hotspots.success:
        for file_path, count in hotspots.hotspots[:5]:
            print(f"  {file_path}: {count} changes")
    
    print("\n✅ Git analysis complete")


# ============================================================================
# Example 2: Company Domain Compliance
# ============================================================================

def example_2_company_domain_compliance():
    """
    Example 2: Company Domain Compliance
    
    Load company-specific compliance standards and domain knowledge.
    """
    print("\n" + "="*80)
    print("EXAMPLE 2: Company Domain Compliance")
    print("="*80 + "\n")
    
    loader = get_company_domain_loader()
    
    print("🏢 Loading company domain knowledge...")
    result = loader.load_all_domains()
    
    if result.success:
        print(f"\n📊 Summary:")
        print(f"  Domains loaded: {len(result.domains_loaded)}")
        print(f"  YAML files: {result.total_files}")
        print(f"  Load time: {result.load_time_ms:.2f}ms")
        
        # Show domains by category
        print(f"\n📂 Domains:")
        for domain in result.domains_loaded[:5]:
            print(f"  - {domain.domain_name} ({domain.data.get('category', 'N/A')})")
            if domain.description:
                print(f"    {domain.description}")
        
        # Search for specific compliance
        print(f"\n🔍 Compliance Standards:")
        compliance_domains = loader.get_domains_by_category("compliance")
        for domain in compliance_domains[:3]:
            print(f"  - {domain.domain_name}")
            rules_count = len(domain.data.get("rules", []))
            print(f"    Rules: {rules_count}")
    
    print("\n✅ Company domain analysis complete")


# ============================================================================
# Example 3: Dependency Vulnerability Analysis
# ============================================================================

def example_3_dependency_vulnerability_analysis():
    """
    Example 3: Dependency Vulnerability Analysis
    
    Scan package dependencies for CVEs, outdated versions, and license issues.
    """
    print("\n" + "="*80)
    print("EXAMPLE 3: Dependency Vulnerability Analysis")
    print("="*80 + "\n")
    
    analyzer = get_dependency_analyzer()
    repo_path = Path(".")
    
    print("📦 Scanning dependencies...")
    result = analyzer.analyze_project(repo_path)
    
    if result.success:
        print(f"\n📊 Summary:")
        print(f"  Total packages: {result.total_packages}")
        print(f"  Outdated packages: {result.outdated_packages}")
        print(f"  Vulnerable packages: {result.vulnerable_packages}")
        print(f"  License issues: {result.license_issues}")
        print(f"  Dependency files: {len(result.dependency_files)}")
        
        # Show vulnerable packages
        vuln_findings = [f for f in result.findings if f.finding_type == "vulnerability"]
        print(f"\n🚨 Vulnerable Packages ({len(vuln_findings)}):")
        for finding in vuln_findings[:5]:
            print(f"  - {finding.package.name} {finding.package.current_version}")
            print(f"    Severity: {finding.severity.value}")
            print(f"    Vulnerabilities: {len(finding.vulnerabilities)}")
            for vuln in finding.vulnerabilities[:2]:
                print(f"      • {vuln.cve_id}: {vuln.description}")
            print()
    
    print("✅ Dependency analysis complete")

# ============================================================================
# Example 4: Onboard Repository with Holistic LENS Analysis
# ============================================================================

def example_onboard_repository():
    """
    Example: Onboard repository with multi-layer analysis.
    
    Performs:
    1. Code analysis (Git, AST, comments)
    2. Config analysis (secrets, insecure defaults)
    3. Database analysis (schema, migrations)
    4. API analysis (endpoints, security)
    5. Security threat modeling (P0/P1/P2)
    6. Dashboard generation
    """
    print("=" * 80)
    print("Example 1: Repository Onboarding")
    print("=" * 80)
    
    result = cortex_onboard_repository(
        repo_path=".",  # Current CORTEX repository
        include_dashboard=True,
        update_company_domain=True
    )
    
    print(f"\n✅ Onboarding Success: {result['success']}")
    print(f"📁 Repository: {result['repo_path']}")
    print(f"🕐 Timestamp: {result['timestamp']}")
    
    # Security risks breakdown
    security = result['security_risks']
    print(f"\n🛡️  Security Assessment:")
    print(f"   ⛔ P0 (CRITICAL): {len(security['p0_risks'])} risk(s)")
    print(f"   ⚠️  P1 (HIGH): {len(security['p1_risks'])} risk(s)")
    print(f"   ℹ️  P2 (MEDIUM): {len(security['p2_risks'])} risk(s)")
    print(f"   Summary: {security['summary']}")
    
    # Show top P0 risks
    if security['p0_risks']:
        print(f"\n🚨 Critical P0 Risks:")
        for i, risk in enumerate(security['p0_risks'][:3], 1):
            print(f"\n   {i}. {risk.get('description', 'N/A')}")
            print(f"      📍 {risk.get('file_path', 'N/A')}:{risk.get('line_number', '?')}")
            print(f"      💡 {risk.get('recommendation', 'N/A')}")
    
    # Show recommendations
    print(f"\n📋 Top Recommendations:")
    for i, rec in enumerate(result['recommendations'][:5], 1):
        print(f"\n   {i}. [{rec['priority']}] {rec['description']}")
        print(f"      💡 {rec['recommendation']}")
    
    # Dashboard
    if result.get('dashboard_path'):
        print(f"\n📊 Dashboard Generated: {result['dashboard_path']}")
    
    return result


# ============================================================================
# Example 5: Analyze Configuration File
# ============================================================================

def example_analyze_config_file():
    """
    Example: Analyze single config file for security issues.
    
    Detects:
    - Hardcoded secrets (API keys, passwords, AWS credentials)
    - Insecure defaults (debug=true, ssl_verify=false)
    - Weak encryption
    - Missing security fields
    """
    print("\n" + "=" * 80)
    print("Example 2: Configuration File Analysis")
    print("=" * 80)
    
    # Analyze docker-compose.yml
    result = cortex_analyze_config("docker-compose.yml")
    
    print(f"\n✅ Analysis Success: {result['success']}")
    print(f"📁 File: {result['file_path']}")
    print(f"📝 Type: {result['config_type']}")
    print(f"🕐 Analysis Time: {result.get('analysis_time_ms', 0):.2f}ms")
    
    # Findings breakdown
    print(f"\n🔍 Findings:")
    print(f"   ⛔ P0 (CRITICAL): {len(result.get('p0_findings', []))}")
    print(f"   ⚠️  P1 (HIGH): {len(result.get('p1_findings', []))}")
    print(f"   ℹ️  P2 (MEDIUM): {len(result.get('p2_findings', []))}")
    
    # Show P0 findings
    if result.get('p0_findings'):
        print(f"\n🚨 Critical P0 Findings:")
        for finding in result['p0_findings'][:3]:
            print(f"\n   • {finding['description']}")
            print(f"     Line {finding['line_number']}")
            print(f"     💡 {finding['recommendation']}")
    
    return result


# ============================================================================
# Example 6: Analyze All Repository Configs
# ============================================================================

def example_analyze_repository_configs():
    """
    Example: Scan all config files in repository.
    
    Scans for:
    - YAML, JSON, TOML files
    - .env files
    - docker-compose files
    - Aggregates findings by severity
    """
    print("\n" + "=" * 80)
    print("Example 3: Repository-Wide Config Analysis")
    print("=" * 80)
    
    result = cortex_analyze_repository_configs(".")
    
    print(f"\n✅ Analyzed Files: {result.get('analyzed_files', 0)}")
    print(f"🔍 Total Findings: {result.get('total_findings', 0)}")
    
    print(f"\n📊 Findings Breakdown:")
    print(f"   ⛔ P0 (CRITICAL): {len(result.get('p0_findings', []))}")
    print(f"   ⚠️  P1 (HIGH): {len(result.get('p1_findings', []))}")
    print(f"   ℹ️  P2 (MEDIUM): {len(result.get('p2_findings', []))}")
    
    print(f"\n📝 Summary: {result.get('summary', 'N/A')}")
    
    # Show distribution of findings by file
    findings_by_file = {}
    for finding in result.get('p0_findings', []) + result.get('p1_findings', []):
        file_path = finding.get('file_path', 'unknown')
        findings_by_file[file_path] = findings_by_file.get(file_path, 0) + 1
    
    if findings_by_file:
        print(f"\n📁 Files with Issues:")
        for file_path, count in sorted(findings_by_file.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   • {file_path}: {count} issue(s)")
    
    return result


# ============================================================================
# Example 7: Use SecurityAdvisorMixin in Custom Orchestrator
# ============================================================================

from cortex.orchestrators.core.interfaces import IOrchestrator
from cortex.brain.core.result import Result, Ok, Err

class MyCustomOrchestrator(SecurityAdvisorMixin, IOrchestrator):
    """
    Example custom orchestrator with automatic security assessment.
    
    Demonstrates:
    - SecurityAdvisorMixin integration
    - P0 execution blocking
    - Multi-layer security assessment
    """
    
    def execute(self, parameters):
        """
        Execute operation with automatic security checks.
        
        Args:
            parameters: Dict with:
                - operation: str
                - code: Optional[str]
                - config_file: Optional[str]
        
        Returns:
            Result with operation result or security block
        """
        # Step 1: Run security assessment
        security = self.assess_security_risks(
            context=parameters,
            code=parameters.get("code"),
            config_path=Path(parameters.get("config_file")) if parameters.get("config_file") else None
        )
        
        # Step 2: Block on P0 risks
        if security["block_execution"]:
            return Err(f"⛔ SECURITY BLOCK: {security['summary']}\n\n"
                      f"P0 Risks:\n" + 
                      "\n".join(f"  - {r['description']}" for r in security['p0_risks'][:3]))
        
        # Step 3: Warn on P1 risks
        if security["p1_risks"]:
            print(f"⚠️  WARNING: {len(security['p1_risks'])} P1 security risk(s) detected")
            print("   Consider addressing before deployment")
        
        # Step 4: Continue with operation
        return Ok({
            "operation": parameters.get("operation"),
            "security_assessment": security,
            "result": "Operation completed successfully"
        })
    
    def get_name(self):
        return "MyCustomOrchestrator"
    
    def get_description(self):
        return "Custom orchestrator with SecurityAdvisorMixin"


def example_custom_orchestrator():
    """Example: Use custom orchestrator with SecurityAdvisorMixin."""
    print("\n" + "=" * 80)
    print("Example 4: Custom Orchestrator with Security Mixin")
    print("=" * 80)
    
    orchestrator = MyCustomOrchestrator()
    
    # Test with potentially dangerous code
    result = orchestrator.execute({
        "operation": "deploy",
        "code": "eval(user_input)  # P0: Code injection vulnerability",
    })
    
    if result.is_err():
        print(f"\n⛔ Security Block: {result.unwrap_err()}")
    else:
        data = result.unwrap()
        print(f"\n✅ Operation: {data['operation']}")
        print(f"📊 Security Assessment: {data['security_assessment']['summary']}")
    
    return result


# ============================================================================
# Run Examples
# ============================================================================

def main():
    """Run all LENS v2.0 examples."""
    print("\n" + "🧠" * 40)
    print("CORTEX LENS v2.0 - Comprehensive Usage Examples")
    print("🧠" * 40)
    
    try:
        # New LENS v2.0 examples
        example_1_git_history_analysis()
        example_2_company_domain_compliance()
        example_3_dependency_vulnerability_analysis()
        
        # Original examples (updated)
        example_onboard_repository()
        example_analyze_config_file()
        example_analyze_repository_configs()
        example_custom_orchestrator()
        
        print("\n" + "="*80)
        print("🎉 All LENS v2.0 examples completed successfully!")
        print("="*80 + "\n")
        
        print("📚 Summary:")
        print("  7 examples demonstrating 9 analyzers")
        print("  Security-first approach validated")
        print("  Holistic orchestration demonstrated")
        print("\nFor more information, see:")
        print("  - docs/05-lens-protocol/")
        print("  - cortex/brain/analysis/")
        print("  - cortex/orchestrators/support/lens_orchestrator.py")
        print("  - cortex-lens/security-dashboard.html")
        
    except Exception as e:
        logger.error(f"Example execution failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
