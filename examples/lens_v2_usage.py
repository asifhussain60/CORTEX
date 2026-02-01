"""
LENS v2.0 Usage Examples

Demonstrates new LENS v2.0 capabilities:
- Repository onboarding with holistic analysis
- Configuration security analysis
- Security-first orchestrator development
"""

from pathlib import Path
from cortex.mcp.tools import (
    cortex_onboard_repository,
    cortex_analyze_config,
    cortex_analyze_repository_configs,
)
from cortex.brain.analysis import get_config_analyzer
from cortex.orchestrators.mixins import SecurityAdvisorMixin


# ============================================================================
# Example 1: Onboard Repository with Holistic LENS Analysis
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
# Example 2: Analyze Configuration File
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
# Example 3: Analyze All Repository Configs
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
# Example 4: Use SecurityAdvisorMixin in Custom Orchestrator
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

if __name__ == "__main__":
    print("\n")
    print("██╗     ███████╗███╗   ██╗███████╗    ██╗   ██╗██████╗     ██████╗ ")
    print("██║     ██╔════╝████╗  ██║██╔════╝    ██║   ██║╚════██╗   ██╔═████╗")
    print("██║     █████╗  ██╔██╗ ██║███████╗    ██║   ██║ █████╔╝   ██║██╔██║")
    print("██║     ██╔══╝  ██║╚██╗██║╚════██║    ╚██╗ ██╔╝██╔═══╝    ████╔╝██║")
    print("███████╗███████╗██║ ╚████║███████║     ╚████╔╝ ███████╗██╗╚██████╔╝")
    print("╚══════╝╚══════╝╚═╝  ╚═══╝╚══════╝      ╚═══╝  ╚══════╝╚═╝ ╚═════╝ ")
    print("\nHolistic Intelligence System - Security-First Repository Analysis\n")
    
    try:
        # Example 1: Repository onboarding
        # example_onboard_repository()
        
        # Example 2: Single config file analysis
        example_analyze_config_file()
        
        # Example 3: Repository-wide config scan
        example_analyze_repository_configs()
        
        # Example 4: Custom orchestrator with security mixin
        example_custom_orchestrator()
        
        print("\n" + "=" * 80)
        print("✅ All examples completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()
