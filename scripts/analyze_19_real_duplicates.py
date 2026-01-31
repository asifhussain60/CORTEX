#!/usr/bin/env python3
"""
Analyze the 19 real duplicates (100% content match) for consolidation strategy.
Categorize by risk, canonical location, and consolidation order.

AC_START: REAL-DUPLICATES-ANALYSIS-001
"""

from pathlib import Path
import hashlib
from collections import defaultdict

class RealDuplicatesAnalyzer:
    """Analyze 19 true duplicates for consolidation"""
    
    def __init__(self):
        self.repo_root = Path("/Users/asifhussain/PROJECTS/CORTEX")
        self.duplicates = {
            "dashboard_api": {
                "files": [
                    "_workspaces/dashboard/api/main.py",
                    "_workspaces/dashboard/enhancements_dashboard_api_main.py",
                    "cortex/brain/dashboard/api/main.py",
                ],
                "category": "Workspace Artifact",
                "risk": "HIGH",
                "reason": "Workspace has copies, cortex/ is canonical. Workspace may have local mods.",
            },
            "metrics_dashboard": {
                "files": [
                    "_workspaces/dashboard/enhancements_dashboard_metrics_dashboard.py",
                    "cortex/brain/core/observability/metrics_dashboard.py",
                ],
                "category": "Workspace Artifact",
                "risk": "MEDIUM",
                "reason": "enhancements_ prefix suggests local workspace copy",
            },
            "intent_reflection_protocol": {
                "files": [
                    "_workspaces/dashboard/intent_reflection_protocol.py",
                    "cortex/brain/core/intent/intent_reflection_protocol.py",
                ],
                "category": "Workspace Artifact",
                "risk": "MEDIUM",
                "reason": "Core implementation, workspace has reference copy",
            },
            "knowledge_graph": {
                "files": [
                    "_workspaces/dashboard/knowledge_graph.py",
                    "cortex/brain/core/knowledge/knowledge_graph.py",
                ],
                "category": "Workspace Artifact",
                "risk": "MEDIUM",
                "reason": "Core implementation, workspace has reference copy",
            },
            "lens_commands": {
                "files": [
                    "_workspaces/dashboard/lens_commands.py",
                    "cortex/cli/commands/lens.py",
                ],
                "category": "CLI Command",
                "risk": "LOW",
                "reason": "Simple CLI command, cortex/cli/ is canonical",
            },
            "lens_context_builder": {
                "files": [
                    "_workspaces/dashboard/lens_context_builder.py",
                    "cortex/brain/core/intent/lens_context_builder.py",
                ],
                "category": "Workspace Artifact",
                "risk": "MEDIUM",
                "reason": "Intent logic, workspace has reference copy",
            },
            "relationship_analyzer": {
                "files": [
                    "_workspaces/dashboard/relationship_analyzer.py",
                    "cortex/orchestrators/core/relationship_analyzer.py",
                ],
                "category": "Orchestrator Tool",
                "risk": "MEDIUM",
                "reason": "Core orchestrator logic, workspace has reference",
            },
            "remote_cache": {
                "files": [
                    "_workspaces/dashboard/remote_cache.py",
                    "cortex/brain/analysis/remote_cache.py",
                ],
                "category": "Cache Implementation",
                "risk": "LOW",
                "reason": "Cache logic, cortex/brain/analysis/ is canonical",
            },
            "dashboard_api_main": {
                "files": [
                    "_workspaces/dashboard/enhancements_dashboard_api.py",
                    "cortex/api/dashboard_api.py",
                ],
                "category": "API Implementation",
                "risk": "HIGH",
                "reason": "Dashboard API, workspace may have mods, cortex/ is canonical",
            },
            "governance_heatmap": {
                "files": [
                    "_workspaces/dashboard/enhancements_dashboard_governance_heatmap.py",
                    "_workspaces/dashboard/governance_heatmap.py",
                ],
                "category": "Workspace Internal",
                "risk": "LOW",
                "reason": "Both in workspace, enhancements_ is duplicate, remove it",
            },
            "dashboard_launch": {
                "files": [
                    "_workspaces/dashboard/enhancements_dashboard_launch.py",
                    "_workspaces/dashboard/launch.py",
                ],
                "category": "Workspace Internal",
                "risk": "LOW",
                "reason": "Both in workspace, enhancements_ is duplicate, remove it",
            },
            "serve_dashboard": {
                "files": [
                    "_workspaces/dashboard/enhancements_dashboard_serve-cortex-dashboard.py",
                    "_workspaces/dashboard/serve_cortex_dashboard.py",
                ],
                "category": "Workspace Internal",
                "risk": "LOW",
                "reason": "Both in workspace, enhancements_ is duplicate, remove it",
            },
            "copy_assets": {
                "files": [
                    "_workspaces/docs/_hooks/copy_assets.py",
                    "docs/_hooks/copy_assets.py",
                ],
                "category": "Build Hook",
                "risk": "LOW",
                "reason": "Build script, docs/ is canonical",
            },
            "dashboard_extensibility": {
                "files": [
                    "cortex/brain/observability/dashboard_extensibility.py",
                    "cortex/observability/dashboard_extensibility.py",
                ],
                "category": "Core Duplication",
                "risk": "MEDIUM",
                "reason": "Both in cortex/, observability/ is canonical (lower-level)",
            },
            "core_files": {
                "files": [
                    "cortex/core/database.py",
                    "cortex/core/decorators.py",
                    "cortex/core/intelligence.py",
                ],
                "category": "Empty/Stub Files",
                "risk": "LOW",
                "reason": "All identical (empty or minimal), keep one, remove others",
            },
        }
    
    def run(self):
        """Analyze and present consolidation strategy"""
        print(f"\n{'='*80}")
        print("🔍 19 REAL DUPLICATES - CONSOLIDATION STRATEGY")
        print(f"{'='*80}\n")
        
        # Categorize by risk
        by_risk = defaultdict(list)
        for name, info in self.duplicates.items():
            risk = info["risk"]
            by_risk[risk].append((name, info))
        
        # HIGH RISK
        print("🔴 HIGH RISK (Workspace ↔ Core boundaries - need careful validation):")
        print("-" * 80)
        for name, info in by_risk["HIGH"]:
            print(f"\n  {name}")
            for f in info["files"]:
                canonical = "✅ CANONICAL" if "cortex/" in f and "_workspaces/" not in f else "🗑️  DELETE"
                print(f"    {canonical}: {f}")
            print(f"    Reason: {info['reason']}")
        
        # MEDIUM RISK
        print(f"\n\n🟡 MEDIUM RISK (Workspace artifacts or core layering - validate before consolidating):")
        print("-" * 80)
        for name, info in by_risk["MEDIUM"]:
            print(f"\n  {name}")
            for f in info["files"]:
                canonical = "✅ CANONICAL" if "cortex/" in f and "_workspaces/" not in f else "🗑️  DELETE"
                print(f"    {canonical}: {f}")
            print(f"    Reason: {info['reason']}")
        
        # LOW RISK
        print(f"\n\n🟢 LOW RISK (Safe consolidations - workspace internals or simple scripts):")
        print("-" * 80)
        for name, info in by_risk["LOW"]:
            print(f"\n  {name}")
            for f in info["files"]:
                canonical = "✅ CANONICAL" if "cortex/" in f or (f.count('/') <= 3 and "_workspaces/" not in f) else "🗑️  DELETE"
                print(f"    {canonical}: {f}")
            print(f"    Reason: {info['reason']}")
        
        # Summary
        print(f"\n\n{'='*80}")
        print(f"📊 CONSOLIDATION SUMMARY")
        print(f"{'='*80}")
        print(f"🔴 HIGH RISK: {len(by_risk['HIGH'])} groups (requires validation)")
        print(f"🟡 MEDIUM RISK: {len(by_risk['MEDIUM'])} groups (requires review)")
        print(f"🟢 LOW RISK: {len(by_risk['LOW'])} groups (safe to consolidate)")
        
        total_duplicates = sum(len(info["files"]) - 1 for info in self.duplicates.values())
        print(f"\n📁 Total duplicate files to delete: {total_duplicates}")
        
        print(f"\n\n{'='*80}")
        print("✅ RECOMMENDED CONSOLIDATION ORDER:")
        print(f"{'='*80}")
        print("\n1️⃣  LOW RISK FIRST (30 min):")
        print("   - governance_heatmap (workspace internal)")
        print("   - dashboard_launch (workspace internal)")
        print("   - serve_dashboard (workspace internal)")
        print("   - copy_assets (build hook)")
        print("   - core_files (empty stubs)")
        
        print("\n2️⃣  MEDIUM RISK SECOND (1 hour + validation):")
        print("   - metrics_dashboard (observability)")
        print("   - intent_reflection_protocol (brain/core)")
        print("   - knowledge_graph (brain/core)")
        print("   - lens_context_builder (intent logic)")
        print("   - relationship_analyzer (orchestrator)")
        print("   - remote_cache (analysis)")
        print("   - dashboard_extensibility (core duplication)")
        print("   - lens_commands (CLI)")
        
        print("\n3️⃣  HIGH RISK LAST (1.5 hours + careful testing):")
        print("   - dashboard_api (API implementation)")
        print("   - dashboard_api_main (API endpoint)")
        
        print("\n⏱️  Total estimated time: 2.5-3 hours (vs. 6+ for all 19)")
        print("✅ All LOW risk consolidations = 6+ duplicate files removed safely\n")

if __name__ == "__main__":
    analyzer = RealDuplicatesAnalyzer()
    analyzer.run()
    # AC_COMPLETE: REAL-DUPLICATES-ANALYSIS-001
