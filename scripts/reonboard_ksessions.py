"""
Script to re-onboard KSESSIONS with enhanced orchestrator (Schema v3.0).

This will generate a complete dashboard JSON with:
- All 9 tabs (including new Architecture tab)
- Pre-computed visualizations
- Real AST-based dependency edges
- Data quality / confidence section

AC_START: AC-DASHBOARD-9TAB-015
"""

from pathlib import Path
import json
import sys

from cortex.orchestrators.support.repository_onboarding_orchestrator import (
    RepositoryOnboardingOrchestrator
)
from cortex.models.dashboard_schema import RepoDashboardModel

def main():
    # KSESSIONS repository path
    ksessions_path = Path("D:/PROJECTS/KSESSIONS")
    
    if not ksessions_path.exists():
        print(f"❌ KSESSIONS not found at {ksessions_path}")
        print("   Update path in script if needed")
        return 1
    
    print("🔧 Re-onboarding KSESSIONS with Schema v3.0...")
    print(f"   Source: {ksessions_path}")
    print("")
    
    # Initialize orchestrator
    orchestrator = RepositoryOnboardingOrchestrator()
    
    try:
        print("📊 Running onboarding...")
        result = orchestrator.onboard_repository(
            repo_path=ksessions_path,
            include_dashboard=True,
            update_company_domain=True,
            repo_name="ksessions",
            icon="🔐"
        )
        
        if not result.success:
            print(f"❌ Onboarding failed: {result.error}")
            return 1
        
        # Load generated JSON
        json_path = Path("company/dashboards/ksessions/dashboard-data.json")
        
        if not json_path.exists():
            print(f"❌ Dashboard JSON not generated at {json_path}")
            return 1
        
        print(f"✅ Dashboard JSON generated: {json_path}")
        print("")
        
        # Validate with schema
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        print("🔍 Validating Schema v3.0...")
        model = RepoDashboardModel.from_dict(data)
        
        # Print validation report
        print("")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📋 9-Tab Validation Report")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # Tab 1: Overview
        print(f"✅ Tab 1: Overview")
        print(f"   - Summary: {len(model.overview.summary)} chars")
        print(f"   - Key Findings: {len(model.overview.key_findings)} items")
        
        # Tab 2: Metrics
        print(f"✅ Tab 2: Metrics")
        print(f"   - Health Score: {model.metrics.health_score}/100")
        print(f"   - Risk Score: {model.metrics.risk_score}/100")
        print(f"   - LOC: {model.metrics.loc:,}")
        print(f"   - Files: {model.metrics.files:,}")
        print(f"   - Languages: {len(model.metrics.languages)}")
        print(f"   - Visualizations: {'health_gauge' in model.metrics.visualizations}")
        
        # Tab 3: Security
        print(f"✅ Tab 3: Security")
        print(f"   - Total Vulnerabilities: {model.security.total_count}")
        print(f"   - Critical: {model.security.critical_count}")
        print(f"   - High: {model.security.high_count}")
        
        # Tab 4: Dependencies
        print(f"✅ Tab 4: Dependencies")
        print(f"   - Total: {model.dependencies.total_count}")
        print(f"   - Direct: {model.dependencies.direct_count}")
        print(f"   - Transitive: {model.dependencies.transitive_count}")
        viz = model.dependencies.visualizations.get("dependency_graph", {})
        print(f"   - Graph Nodes: {len(viz.get('nodes', []))}")
        print(f"   - Graph Edges: {len(viz.get('edges', []))}")
        print(f"   - Real Edges: {viz.get('real_edges', 0)}")
        
        # Tab 5: Quality
        print(f"✅ Tab 5: Quality")
        print(f"   - Maintainability: {model.quality.maintainability}/100")
        print(f"   - Readability: {model.quality.readability}/100")
        print(f"   - Code Smells: {len(model.quality.code_smells)}")
        
        # Tab 6: Use Cases
        print(f"✅ Tab 6: Use Cases")
        print(f"   - Total Use Cases: {len(model.use_cases)}")
        
        # Tab 7: LENS
        print(f"✅ Tab 7: LENS")
        print(f"   - Analysis Summary: {len(model.lens.analysis_summary)} chars")
        
        # Tab 8: Refactoring
        print(f"✅ Tab 8: Refactoring")
        print(f"   - Recommendations: {len(model.refactoring.recommendations)}")
        
        # Tab 9: Architecture (NEW)
        print(f"✅ Tab 9: Architecture (NEW)")
        print(f"   - Coupling Score: {model.architecture.coupling_score}/100")
        print(f"   - Cohesion Score: {model.architecture.cohesion_score}/100")
        print(f"   - Total Dependencies: {model.architecture.total_dependencies}")
        print(f"   - Circular Dependencies: {model.architecture.circular_dependencies}")
        layer_viz = model.architecture.visualizations.get("layer_graph", {})
        print(f"   - Layer Graph Nodes: {len(layer_viz.get('nodes', []))}")
        
        # Data Quality (NEW)
        print(f"✅ Data Quality (NEW)")
        print(f"   - Confidence Score: {model.data_quality.confidence_score}/100")
        print(f"   - Coverage: {model.data_quality.coverage_pct:.1f}%")
        print(f"   - Contradictions: {len(model.data_quality.contradictions)}")
        print(f"   - Missing Fields: {len(model.data_quality.missing_fields)}")
        
        if model.data_quality.contradictions:
            print(f"\n   ⚠️  Contradictions Detected:")
            for contradiction in model.data_quality.contradictions:
                print(f"      - {contradiction}")
        
        print("")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # Overall assessment
        if model.data_quality.confidence_score >= 70:
            print("🟢 KSESSIONS JSON: HEALTHY (confidence ≥ 70)")
        elif model.data_quality.confidence_score >= 30:
            print("🟡 KSESSIONS JSON: DEGRADED (confidence 30-69)")
        else:
            print("🔴 KSESSIONS JSON: UNAVAILABLE (confidence < 30)")
        
        print("")
        print(f"✅ Re-onboarding complete!")
        print(f"   JSON path: {json_path}")
        print(f"   Size: {json_path.stat().st_size / 1024:.1f} KB")
        
        return 0
        
    except Exception as e:
        print(f"❌ Onboarding failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

# AC_COMPLETE: AC-DASHBOARD-9TAB-015 ✅ KSESSIONS re-onboarding script

if __name__ == "__main__":
    sys.exit(main())
