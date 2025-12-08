"""
Phase 2 Validation Script

Validates Phase 2 (Executive Summary Intelligence) completion:
- Git Commit Pattern Analyzer
- README Deep Parser
- Executive Summary Orchestrator

Author: Asif Hussain
Created: 2025-12-08
"""

import sys
from pathlib import Path
import subprocess
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.intelligence.git_commit_analyzer import GitCommitAnalyzer
from src.intelligence.readme_parser import ReadmeParser, find_readme
from src.intelligence.executive_summary_orchestrator import ExecutiveSummaryOrchestrator


def validate_git_commit_analyzer():
    """Validate Git Commit Analyzer on CORTEX repository."""
    print("\n" + "="*80)
    print("TASK 2.1: Git Commit Pattern Analyzer")
    print("="*80)
    
    repo_path = Path(r"C:\PROJECTS\CORTEX")
    analyzer = GitCommitAnalyzer(repo_path)
    
    print(f"\n✓ Analyzer initialized for: {repo_path}")
    
    try:
        # Generate narrative
        narrative = analyzer.analyze_commits(days=90)
        
        print(f"\n📊 Analysis Results:")
        print(f"  - Total commits analyzed: {narrative.velocity_metrics.get('total_commits', 0)}")
        print(f"  - Time period: {narrative.time_period}")
        print(f"  - Top themes: {len(narrative.top_themes)}")
        
        if narrative.top_themes:
            print(f"\n🎯 Top Development Themes:")
            for i, theme in enumerate(narrative.top_themes[:3], 1):
                print(f"  {i}. {theme.theme.title()}: {theme.count} commits ({theme.percentage:.1f}%)")
        
        if narrative.active_areas:
            print(f"\n🔥 Active Development Areas:")
            for area in narrative.active_areas[:5]:
                print(f"  - {area}")
        
        if narrative.feature_evolutions:
            print(f"\n📈 Feature Evolution Detected:")
            for evo in narrative.feature_evolutions[:3]:
                print(f"  - {evo.feature_name}: {' → '.join(evo.stages)}")
        
        print(f"\n💬 Development Summary:")
        print(f"  {narrative.summary[:300]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def validate_readme_parser():
    """Validate README Parser on multiple repositories."""
    print("\n" + "="*80)
    print("TASK 2.2: README Deep Parser & Section Extractor")
    print("="*80)
    
    parser = ReadmeParser()
    test_repos = [
        Path(r"C:\PROJECTS\CORTEX"),
        Path(r"C:\PROJECTS\TCBULK"),
        Path(r"C:\PROJECTS\V5.ColdFusion")
    ]
    
    results = []
    
    for repo_path in test_repos:
        if not repo_path.exists():
            print(f"\n⚠️ Skipping {repo_path.name} (not found)")
            continue
        
        print(f"\n📄 Parsing {repo_path.name}...")
        
        readme_path = find_readme(repo_path)
        if not readme_path:
            print(f"  ⚠️ No README found")
            continue
        
        try:
            metadata = parser.parse_file(readme_path)
            
            print(f"  ✓ Title: {metadata.title}")
            print(f"  ✓ Description: {metadata.description[:100] if metadata.description else 'N/A'}...")
            print(f"  ✓ Purpose: {metadata.purpose[:100] if metadata.purpose else 'N/A'}...")
            print(f"  ✓ Features: {len(metadata.features)} found")
            print(f"  ✓ Sections: {len(metadata.sections)} parsed")
            print(f"  ✓ Technologies: {', '.join(metadata.technologies[:5]) if metadata.technologies else 'None detected'}")
            
            results.append(True)
            
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            results.append(False)
    
    return all(results) if results else False


def validate_executive_summary_orchestrator():
    """Validate Executive Summary Orchestrator integration."""
    print("\n" + "="*80)
    print("TASK 2.3: Executive Summary Integration")
    print("="*80)
    
    orchestrator = ExecutiveSummaryOrchestrator()
    repo_path = Path(r"C:\PROJECTS\CORTEX")
    
    print(f"\n🎯 Generating executive summary for: {repo_path.name}")
    print(f"  - Including: Git history, README, Domains")
    print(f"  - Parallel processing: Enabled")
    
    try:
        summary = orchestrator.generate_summary(
            repo_path,
            include_git=True,
            include_readme=True,
            include_domains=True,
            parallel=True
        )
        
        print(f"\n✅ Executive Summary Generated:")
        print(f"  - Repo: {summary.repo_name}")
        print(f"  - Title: {summary.title}")
        print(f"  - Description: {summary.description[:150] if summary.description else 'N/A'}...")
        print(f"  - Purpose: {summary.purpose[:150] if summary.purpose else 'N/A'}...")
        
        print(f"\n📊 Intelligence Sources:")
        print(f"  - README: {'✓' if summary.has_readme else '✗'}")
        print(f"  - Git History: {'✓' if summary.has_git_history else '✗'}")
        print(f"  - Quality Score: {summary.summary_quality_score:.1f}/10")
        
        if summary.primary_domains:
            print(f"\n🎯 Primary Business Domains:")
            for domain in summary.primary_domains[:5]:
                print(f"  - {domain}")
        
        if summary.capabilities:
            print(f"\n💡 Key Capabilities:")
            for cap in summary.capabilities[:5]:
                print(f"  - {cap}")
        
        if summary.features:
            print(f"\n✨ Features ({len(summary.features)}):")
            for feat in summary.features[:5]:
                print(f"  - {feat}")
        
        if summary.development_focus:
            print(f"\n🔥 Development Focus:")
            print(f"  {summary.development_focus}")
        
        if summary.active_areas:
            print(f"\n📈 Active Areas:")
            for area in summary.active_areas[:5]:
                print(f"  - {area}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_tests():
    """Run pytest tests for Phase 2."""
    print("\n" + "="*80)
    print("RUNNING PHASE 2 TEST SUITE")
    print("="*80)
    
    test_files = [
        "tests/intelligence/test_git_commit_analyzer.py",
        "tests/intelligence/test_readme_parser.py",
        "tests/intelligence/test_executive_summary_orchestrator.py"
    ]
    
    for test_file in test_files:
        print(f"\n🧪 Running {test_file}...")
        result = subprocess.run(
            ["pytest", test_file, "-v", "--tb=short", "-x"],
            capture_output=True,
            text=True
        )
        
        # Extract summary line
        for line in result.stdout.split('\n'):
            if 'passed' in line.lower():
                print(f"  ✓ {line.strip()}")
                break
        
        if result.returncode != 0:
            print(f"  ❌ Tests failed")
            return False
    
    return True


def main():
    """Run all Phase 2 validations."""
    print("\n" + "="*80)
    print("PHASE 2 COMPLETION VALIDATION")
    print("Comprehensive Dashboard Code Intelligence Plan v3.9")
    print("="*80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        'git_analyzer': False,
        'readme_parser': False,
        'orchestrator': False,
        'tests': False
    }
    
    # Validate each component
    results['git_analyzer'] = validate_git_commit_analyzer()
    results['readme_parser'] = validate_readme_parser()
    results['orchestrator'] = validate_executive_summary_orchestrator()
    results['tests'] = run_tests()
    
    # Summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    print(f"\n Task 2.1 - Git Commit Analyzer:          {'✅ PASS' if results['git_analyzer'] else '❌ FAIL'}")
    print(f" Task 2.2 - README Parser:                {'✅ PASS' if results['readme_parser'] else '❌ FAIL'}")
    print(f" Task 2.3 - Executive Summary Orchestrator: {'✅ PASS' if results['orchestrator'] else '❌ FAIL'}")
    print(f" Test Suite:                               {'✅ PASS' if results['tests'] else '❌ FAIL'}")
    
    all_passed = all(results.values())
    
    print(f"\n{'='*80}")
    if all_passed:
        print("🎉 PHASE 2 COMPLETE - All validations passed!")
    else:
        print("⚠️ PHASE 2 INCOMPLETE - Some validations failed")
    print(f"{'='*80}\n")
    
    # Save results
    report = {
        'phase': 2,
        'date': datetime.now().isoformat(),
        'results': results,
        'status': 'complete' if all_passed else 'incomplete'
    }
    
    report_path = Path("cortex-brain/documents/reports/phase2-validation-report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2))
    
    print(f"📄 Validation report saved to: {report_path}")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
