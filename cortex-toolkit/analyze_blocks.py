#!/usr/bin/env python3
"""
CORTEX Toolkit: Template Block Analyzer

Analyzes composable blocks usage across orchestrators and identifies optimization opportunities.
Part of Orchestrator Composable Template System.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict


class BlockAnalyzer:
    """Analyzes composable block usage and patterns."""
    
    def __init__(self, cortex_root: Path = None):
        """Initialize analyzer with CORTEX root directory."""
        self.cortex_root = cortex_root or Path(__file__).parent.parent
        self.templates_file = self.cortex_root / "cortex-brain" / "response-templates-v4.yaml"
        self.manifests_dir = self.cortex_root / "cortex-brain" / "manifests" / "orchestrators"
        self.templates_data = None
        self.manifests_data = {}
        
    def load_data(self):
        """Load templates and manifests."""
        with open(self.templates_file, 'r', encoding='utf-8') as f:
            self.templates_data = yaml.safe_load(f)
        
        target_manifests = [
            "planning-system-4.0-manifest.yaml",
            "tdd-orchestrator-v4-manifest.yaml",
            "debug-orchestrator-manifest.yaml",
            "cortex-lens-v3-manifest.yaml",
            "refinement-orchestrator-manifest.yaml",
            "code-sanitization-manifest.yaml",
            "technical-documentation-orchestrator-manifest.yaml",
            "ado-planning-manifest.yaml"
        ]
        
        for manifest_name in target_manifests:
            manifest_path = self.manifests_dir / manifest_name
            if manifest_path.exists():
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    self.manifests_data[manifest_name] = yaml.safe_load(f)
    
    def analyze_block_usage(self) -> Dict:
        """Analyze which blocks are used by which orchestrators."""
        usage = defaultdict(lambda: {"orchestrators": set(), "operations": []})
        
        for manifest_name, manifest_data in self.manifests_data.items():
            if "response_templates" not in manifest_data:
                continue
            
            rt = manifest_data["response_templates"]
            if "operations" not in rt:
                continue
            
            orchestrator = manifest_name.replace("-manifest.yaml", "")
            
            for op_name, op_data in rt["operations"].items():
                if "blocks" not in op_data:
                    continue
                
                blocks = op_data["blocks"]
                all_blocks = []
                
                if "mandatory" in blocks:
                    all_blocks.extend(blocks["mandatory"])
                if "conditional" in blocks:
                    all_blocks.extend(blocks["conditional"])
                if "orchestrator_specific" in blocks:
                    all_blocks.extend(blocks["orchestrator_specific"])
                
                for block in all_blocks:
                    usage[block]["orchestrators"].add(orchestrator)
                    usage[block]["operations"].append(f"{orchestrator}::{op_name}")
        
        return usage
    
    def analyze_shared_blocks(self, usage: Dict) -> List[Dict]:
        """Identify blocks shared across multiple orchestrators."""
        shared_blocks = []
        
        for block, data in usage.items():
            if len(data["orchestrators"]) > 1:
                shared_blocks.append({
                    "block": block,
                    "orchestrator_count": len(data["orchestrators"]),
                    "orchestrators": sorted(data["orchestrators"]),
                    "usage_count": len(data["operations"])
                })
        
        # Sort by orchestrator count (descending)
        shared_blocks.sort(key=lambda x: x["orchestrator_count"], reverse=True)
        
        return shared_blocks
    
    def analyze_orchestrator_specific_blocks(self, usage: Dict) -> Dict[str, List[str]]:
        """Identify blocks used by only one orchestrator."""
        orchestrator_blocks = defaultdict(list)
        
        for block, data in usage.items():
            if len(data["orchestrators"]) == 1:
                orchestrator = list(data["orchestrators"])[0]
                orchestrator_blocks[orchestrator].append(block)
        
        return dict(orchestrator_blocks)
    
    def analyze_block_coverage(self) -> Dict:
        """Analyze which orchestrators use which block categories."""
        coverage = {}
        
        for manifest_name, manifest_data in self.manifests_data.items():
            if "response_templates" not in manifest_data:
                continue
            
            orchestrator = manifest_name.replace("-manifest.yaml", "")
            rt = manifest_data["response_templates"]
            
            if "operations" not in rt:
                continue
            
            coverage[orchestrator] = {
                "operations_count": len(rt["operations"]),
                "uses_mandatory": False,
                "uses_conditional": False,
                "uses_orchestrator_specific": False,
                "total_blocks": set()
            }
            
            for op_name, op_data in rt["operations"].items():
                if "blocks" not in op_data:
                    continue
                
                blocks = op_data["blocks"]
                
                if "mandatory" in blocks and blocks["mandatory"]:
                    coverage[orchestrator]["uses_mandatory"] = True
                    coverage[orchestrator]["total_blocks"].update(blocks["mandatory"])
                
                if "conditional" in blocks and blocks["conditional"]:
                    coverage[orchestrator]["uses_conditional"] = True
                    coverage[orchestrator]["total_blocks"].update(blocks["conditional"])
                
                if "orchestrator_specific" in blocks and blocks["orchestrator_specific"]:
                    coverage[orchestrator]["uses_orchestrator_specific"] = True
                    coverage[orchestrator]["total_blocks"].update(blocks["orchestrator_specific"])
            
            coverage[orchestrator]["total_blocks"] = len(coverage[orchestrator]["total_blocks"])
        
        return coverage
    
    def generate_report(self) -> str:
        """Generate comprehensive analysis report."""
        self.load_data()
        
        usage = self.analyze_block_usage()
        shared_blocks = self.analyze_shared_blocks(usage)
        orchestrator_blocks = self.analyze_orchestrator_specific_blocks(usage)
        coverage = self.analyze_block_coverage()
        
        report = []
        report.append("# Composable Block Analysis Report")
        report.append("")
        report.append(f"**Generated:** 2025-12-31")
        report.append(f"**Total Orchestrators:** {len(self.manifests_data)}")
        report.append(f"**Total Unique Blocks:** {len(usage)}")
        report.append("")
        
        # Shared blocks section
        report.append("## 📊 Shared Blocks (Cross-Orchestrator)")
        report.append("")
        report.append("Blocks used by multiple orchestrators:")
        report.append("")
        report.append("| Block | Orchestrators | Usage Count |")
        report.append("|-------|--------------|-------------|")
        
        for block_info in shared_blocks:
            orchestrators = ", ".join(block_info["orchestrators"])
            report.append(f"| `{block_info['block']}` | {block_info['orchestrator_count']} ({orchestrators}) | {block_info['usage_count']} |")
        
        report.append("")
        
        # Orchestrator-specific blocks
        report.append("## 🎯 Orchestrator-Specific Blocks")
        report.append("")
        report.append("Blocks used by only one orchestrator:")
        report.append("")
        
        for orchestrator, blocks in sorted(orchestrator_blocks.items()):
            report.append(f"### {orchestrator}")
            for block in sorted(blocks):
                report.append(f"- `{block}`")
            report.append("")
        
        # Coverage analysis
        report.append("## 📈 Orchestrator Coverage")
        report.append("")
        report.append("| Orchestrator | Operations | Unique Blocks | Mandatory | Conditional | Orchestrator-Specific |")
        report.append("|--------------|-----------|---------------|-----------|-------------|----------------------|")
        
        for orchestrator, cov in sorted(coverage.items()):
            mandatory = "✅" if cov["uses_mandatory"] else "❌"
            conditional = "✅" if cov["uses_conditional"] else "❌"
            specific = "✅" if cov["uses_orchestrator_specific"] else "❌"
            report.append(f"| {orchestrator} | {cov['operations_count']} | {cov['total_blocks']} | {mandatory} | {conditional} | {specific} |")
        
        report.append("")
        
        # Recommendations
        report.append("## 💡 Optimization Recommendations")
        report.append("")
        
        # Find most reused blocks
        if shared_blocks:
            most_reused = shared_blocks[0]
            report.append(f"1. **Most Reused Block:** `{most_reused['block']}` (used by {most_reused['orchestrator_count']} orchestrators)")
            report.append(f"   - Consider this as core template component")
            report.append("")
        
        # Find least used orchestrators
        min_blocks = min(cov["total_blocks"] for cov in coverage.values())
        lean_orchestrators = [k for k, v in coverage.items() if v["total_blocks"] == min_blocks]
        report.append(f"2. **Leanest Orchestrators:** {', '.join(lean_orchestrators)} ({min_blocks} unique blocks)")
        report.append(f"   - Good templates for simple operations")
        report.append("")
        
        # Find blocks only used once
        singleton_blocks = [block for block, data in usage.items() if len(data["operations"]) == 1]
        if singleton_blocks:
            report.append(f"3. **Single-Use Blocks:** {len(singleton_blocks)} blocks used only once")
            report.append(f"   - Consider if these need to be standalone blocks")
            report.append("")
        
        return "\n".join(report)
    
    def print_report(self):
        """Print report to console."""
        report = self.generate_report()
        print(report)
    
    def save_report(self, output_path: Path = None):
        """Save report to file."""
        if output_path is None:
            output_path = self.cortex_root / "cortex-brain" / "documents" / "analysis" / "block-analysis-report.md"
        
        report = self.generate_report()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ Report saved to: {output_path}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze composable block usage")
    parser.add_argument("--save", action="store_true", help="Save report to file")
    parser.add_argument("--output", type=str, help="Output file path")
    
    args = parser.parse_args()
    
    analyzer = BlockAnalyzer()
    
    if args.save:
        output_path = Path(args.output) if args.output else None
        analyzer.save_report(output_path)
    else:
        analyzer.print_report()


if __name__ == "__main__":
    main()
