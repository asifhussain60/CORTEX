"""Test KASHKOLE onboarding with full LENS analysis."""

from pathlib import Path
from cortex.orchestrators.support.repository_onboarding_orchestrator import get_repository_onboarding_orchestrator

def main():
    # Test onboarding
    print("Starting KASHKOLE onboarding...")
    orchestrator = get_repository_onboarding_orchestrator()
    result = orchestrator.onboard_repository(
        repo_path=Path("D:/PROJECTS/KASHKOLE"),
        include_dashboard=True,
        update_company_domain=False,
        repo_name="kashkole",
        icon="📿"
    )

    print("=== ONBOARDING RESULT ===")
    print(f"Success: {result.success}")
    print(f"Repo: {result.repo_name}")
    print(f"Error: {result.error}")
    print()
    
    print("=== HOLISTIC CONTEXT ===")
    context = result.holistic_context
    metadata = context.get("metadata", {})
    print(f"Analyzers Enabled: {metadata.get('analyzers_enabled', [])}")
    print(f"Analysis Time: {metadata.get('analysis_time_ms', 0):.2f} ms")
    print(f"Fallback Mode: {metadata.get('fallback_mode', False)}")
    print()
    
    print("=== REPOSITORY SUMMARY ===")
    summary = context.get("repository_summary", {})
    for k, v in summary.items():
        if k != "contributors":
            print(f"  {k}: {v}")
    print()
    
    print("=== CODE ANALYSIS ===")
    code = context.get("code_analysis", {})
    for k, v in code.items():
        if k != "complex_files" and k != "todo_locations":
            print(f"  {k}: {v}")
    print()
    
    print("=== SECURITY ANALYSIS ===")
    security = context.get("security_analysis", {})
    print(f"  P0 Findings: {security.get('p0_count', 0)}")
    print(f"  P1 Findings: {security.get('p1_count', 0)}")
    print(f"  P2 Findings: {security.get('p2_count', 0)}")
    print(f"  Total Findings: {security.get('total_findings', 0)}")
    
    # Show first few P0 findings
    p0_findings = security.get("p0_findings", [])
    if p0_findings:
        print("\n  Top P0 Security Issues:")
        for f in p0_findings[:5]:
            print(f"    - {f.get('description', 'N/A')[:80]}")
            print(f"      Location: {f.get('location', 'N/A')}")
    print()
    
    print("=== CONFIG ANALYSIS ===")
    config = context.get("config_analysis", {})
    print(f"  Files Analyzed: {config.get('files_analyzed', 0)}")
    print(f"  P0 Findings: {config.get('p0_count', 0)}")
    print(f"  P1 Findings: {config.get('p1_count', 0)}")
    print(f"  Total Findings: {config.get('findings_count', 0)}")
    
    # Show top config findings
    config_findings = config.get("findings", [])
    if config_findings:
        print("\n  Top Config Security Issues:")
        for f in config_findings[:10]:
            severity = f.get("severity", "N/A")
            desc = f.get("description", "N/A")[:60]
            file_path = f.get("file_path", "N/A").split("\\")[-1]
            print(f"    - [{severity}] {desc}")
            print(f"      File: {file_path}")
    print()
    
    print("=== LANGUAGE DETECTION ===")
    lang = context.get("language_detection", {})
    if not lang:
        # Try from repository_summary
        lang = {
            "primary_language": summary.get("primary_language", "Unknown"),
            "file_counts_by_language": summary.get("file_counts_by_language", {})
        }
    print(f"  Primary Language: {lang.get('primary_language', 'Unknown')}")
    print(f"  File Counts: {lang.get('file_counts_by_language', {})}")
    print()
    
    print("=== DASHBOARD OUTPUT ===")
    print(f"Dashboard Path: {result.dashboard_path}")
    print(f"Landing Page: {result.landing_page_path}")
    
    # Check if dashboard was generated
    if result.dashboard_path:
        dashboard_file = Path(result.dashboard_path)
        print(f"Dashboard exists: {dashboard_file.exists()}")
        if dashboard_file.exists():
            print(f"Dashboard size: {dashboard_file.stat().st_size} bytes")

if __name__ == "__main__":
    main()
