"""
CORTEX Startup Profiler Script

Profile CORTEX initialization to identify slow paths and optimization opportunities.

Usage:
    python scripts/profile_startup.py
    python scripts/profile_startup.py --export report.md

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import time
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.performance_profiler import get_global_profiler


def profile_cortex_startup():
    """Profile CORTEX component initialization."""
    
    profiler = get_global_profiler()
    profiler.clear()
    
    print("🔍 Profiling CORTEX startup...")
    print()
    
    # Profile Tier 0 (Brain Protection)
    with profiler.measure("tier0_init"):
        with profiler.measure("tier0.brain_protector"):
            from src.tier0.brain_protector import BrainProtector
            protector = BrainProtector()
        
        with profiler.measure("tier0.governance"):
            from src.tier0.governance_engine import GovernanceEngine
            governance = GovernanceEngine()
    
    # Profile Tier 1 (Working Memory)
    with profiler.measure("tier1_init"):
        with profiler.measure("tier1.working_memory"):
            from src.tier1.working_memory import WorkingMemory
            memory = WorkingMemory()
        
        with profiler.measure("tier1.smart_recommendations"):
            from src.tier1.smart_recommendations import SmartRecommendations
            recommender = SmartRecommendations()
    
    # Profile Tier 2 (Knowledge Graph)
    with profiler.measure("tier2_init"):
        with profiler.measure("tier2.knowledge_graph"):
            from src.tier2.knowledge_graph import KnowledgeGraph
            kg = KnowledgeGraph()
    
    # Profile Template System
    with profiler.measure("template_system_init"):
        with profiler.measure("templates.template_validator"):
            from src.validators.template_validator import TemplateValidator
            validator = TemplateValidator()
    
    # Profile Vision API
    with profiler.measure("vision_init"):
        with profiler.measure("vision.vision_api"):
            from src.vision import VisionAPIIntegration
            vision = VisionAPIIntegration()
    
    # Profile Workflows (lightweight - skip instantiation, just import)
    with profiler.measure("workflows_init"):
        with profiler.measure("workflows.imports"):
            from src.workflows.tdd_workflow import TDDWorkflow
            from src.workflows.feature_workflow import FeatureCreationWorkflow
    
    # Profile YAML Cache
    with profiler.measure("utils_init"):
        with profiler.measure("utils.yaml_cache"):
            from src.utils.yaml_cache import YAMLCache
            cache = YAMLCache()
    
    print("✅ Profiling complete!")
    print()
    
    return profiler


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Profile CORTEX startup")
    parser.add_argument(
        "--export",
        help="Export report to markdown file",
        default=None
    )
    parser.add_argument(
        "--threshold",
        help="Slow operation threshold in ms",
        type=float,
        default=100.0
    )
    
    args = parser.parse_args()
    
    # Run profiling
    profiler = profile_cortex_startup()
    
    # Print report
    profiler.print_report()
    
    # Export if requested
    if args.export:
        profiler.export_report(args.export)
        print(f"\n📄 Report exported to: {args.export}")
    
    # Show slow operations
    slow_ops = profiler.get_slow_operations(threshold_ms=args.threshold)
    if slow_ops:
        print(f"\n⚠️ Found {len(slow_ops)} operations slower than {args.threshold}ms:")
        for op in slow_ops[:5]:  # Show top 5
            print(f"  • {op['operation']}: {op['avg_ms']:.2f}ms")
    else:
        print(f"\n✅ All operations faster than {args.threshold}ms!")


if __name__ == "__main__":
    main()
