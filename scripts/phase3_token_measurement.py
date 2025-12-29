"""
CORTEX Phase 3 - Token Measurement Tool

Purpose: Measure token counts for different documentation approaches
Phase: 3 - Modular Entry Point Validation
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Usage:
    python scripts/phase3_token_measurement.py --all
    python scripts/phase3_token_measurement.py --baseline
    python scripts/phase3_token_measurement.py --modular
    python scripts/phase3_token_measurement.py --export results.json
"""

import tiktoken
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Tuple
import argparse


class TokenMeasurer:
    """Measures token counts for CORTEX documentation files."""
    
    def __init__(self):
        """Initialize with tiktoken encoder for OpenAI models."""
        # Using cl100k_base encoding (GPT-4, GPT-3.5-turbo)
        self.encoder = tiktoken.get_encoding("cl100k_base")
        self.cortex_root = Path(__file__).parent.parent
        
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Number of tokens
        """
        return len(self.encoder.encode(text))
    
    def count_file_tokens(self, file_path: Path) -> Tuple[int, int]:
        """Count tokens in a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Tuple of (line_count, token_count)
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.count('\n') + 1
            tokens = self.count_tokens(content)
            return lines, tokens
    
    def measure_baseline(self) -> Dict:
        """Measure baseline (full cortex.md) token count.
        
        Returns:
            Dict with measurements
        """
        print("\n📊 Measuring BASELINE (Full cortex.md)...")
        cortex_md = self.cortex_root / "prompts" / "user" / "cortex.md"
        
        if not cortex_md.exists():
            print(f"❌ File not found: {cortex_md}")
            return {}
        
        lines, tokens = self.count_file_tokens(cortex_md)
        
        result = {
            "approach": "baseline",
            "file": str(cortex_md.relative_to(self.cortex_root)),
            "lines": lines,
            "tokens": tokens,
            "reduction_percent": 0.0,
            "description": "Full monolithic cortex.md"
        }
        
        print(f"  ✅ File: {result['file']}")
        print(f"  ✅ Lines: {lines:,}")
        print(f"  ✅ Tokens: {tokens:,}")
        
        return result
    
    def measure_modular(self, module_name: str = "story") -> Dict:
        """Measure modular approach (slim + module) token count.
        
        Args:
            module_name: Which module to load (story, setup, technical)
            
        Returns:
            Dict with measurements
        """
        print(f"\n📊 Measuring MODULAR (Slim + {module_name} module)...")
        
        slim_file = self.cortex_root / "prompts" / "user" / "cortex-slim-test.md"
        module_file = self.cortex_root / "prompts" / "shared" / "test" / f"{module_name}-excerpt.md"
        
        if not slim_file.exists():
            print(f"❌ File not found: {slim_file}")
            return {}
        
        if not module_file.exists():
            print(f"❌ File not found: {module_file}")
            return {}
        
        slim_lines, slim_tokens = self.count_file_tokens(slim_file)
        module_lines, module_tokens = self.count_file_tokens(module_file)
        
        total_lines = slim_lines + module_lines
        total_tokens = slim_tokens + module_tokens
        
        # Calculate reduction vs baseline (assuming ~28,000 baseline)
        baseline_tokens = 28000
        reduction = ((baseline_tokens - total_tokens) / baseline_tokens) * 100
        
        result = {
            "approach": "modular",
            "module": module_name,
            "slim_file": str(slim_file.relative_to(self.cortex_root)),
            "module_file": str(module_file.relative_to(self.cortex_root)),
            "slim_lines": slim_lines,
            "slim_tokens": slim_tokens,
            "module_lines": module_lines,
            "module_tokens": module_tokens,
            "total_lines": total_lines,
            "total_tokens": total_tokens,
            "reduction_percent": round(reduction, 1),
            "description": f"Slim entry point + {module_name} excerpt"
        }
        
        print(f"  ✅ Slim file: {result['slim_file']} ({slim_lines} lines, {slim_tokens:,} tokens)")
        print(f"  ✅ Module file: {result['module_file']} ({module_lines} lines, {module_tokens:,} tokens)")
        print(f"  ✅ Total: {total_lines} lines, {total_tokens:,} tokens")
        print(f"  ✅ Reduction: {reduction:.1f}%")
        
        return result
    
    def measure_all_modules(self) -> List[Dict]:
        """Measure all module variations.
        
        Returns:
            List of measurement dicts
        """
        modules = ["story", "setup", "technical"]
        results = []
        
        for module in modules:
            result = self.measure_modular(module)
            if result:
                results.append(result)
        
        return results
    
    def measure_direct_module(self, module_name: str) -> Dict:
        """Measure direct module reference (no slim entry).
        
        Args:
            module_name: Module to measure
            
        Returns:
            Dict with measurements
        """
        print(f"\n📊 Measuring DIRECT MODULE ({module_name} only)...")
        
        module_file = self.cortex_root / "prompts" / "shared" / "test" / f"{module_name}-excerpt.md"
        
        if not module_file.exists():
            print(f"❌ File not found: {module_file}")
            return {}
        
        lines, tokens = self.count_file_tokens(module_file)
        
        baseline_tokens = 28000
        reduction = ((baseline_tokens - tokens) / baseline_tokens) * 100
        
        result = {
            "approach": "direct_module",
            "module": module_name,
            "file": str(module_file.relative_to(self.cortex_root)),
            "lines": lines,
            "tokens": tokens,
            "reduction_percent": round(reduction, 1),
            "description": f"Direct reference to {module_name} excerpt only"
        }
        
        print(f"  ✅ File: {result['file']}")
        print(f"  ✅ Lines: {lines:,}")
        print(f"  ✅ Tokens: {tokens:,}")
        print(f"  ✅ Reduction: {reduction:.1f}%")
        
        return result
    
    def measure_all(self) -> Dict:
        """Measure all approaches comprehensively.
        
        Returns:
            Dict with all measurements
        """
        print("\n" + "="*60)
        print("CORTEX PHASE 3 - TOKEN MEASUREMENT")
        print("="*60)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "baseline": self.measure_baseline(),
            "modular": {
                "story": self.measure_modular("story"),
                "setup": self.measure_modular("setup"),
                "technical": self.measure_modular("technical")
            },
            "direct_module": {
                "story": self.measure_direct_module("story"),
                "setup": self.measure_direct_module("setup"),
                "technical": self.measure_direct_module("technical")
            },
            "summary": {}
        }
        
        # Calculate summary statistics
        baseline_tokens = results["baseline"].get("tokens", 0)
        
        modular_tokens = [
            results["modular"]["story"].get("total_tokens", 0),
            results["modular"]["setup"].get("total_tokens", 0),
            results["modular"]["technical"].get("total_tokens", 0)
        ]
        
        direct_tokens = [
            results["direct_module"]["story"].get("tokens", 0),
            results["direct_module"]["setup"].get("tokens", 0),
            results["direct_module"]["technical"].get("tokens", 0)
        ]
        
        avg_modular = sum(modular_tokens) / len(modular_tokens) if modular_tokens else 0
        avg_direct = sum(direct_tokens) / len(direct_tokens) if direct_tokens else 0
        
        avg_modular_reduction = ((baseline_tokens - avg_modular) / baseline_tokens) * 100 if baseline_tokens > 0 else 0
        avg_direct_reduction = ((baseline_tokens - avg_direct) / baseline_tokens) * 100 if baseline_tokens > 0 else 0
        
        results["summary"] = {
            "baseline_tokens": baseline_tokens,
            "avg_modular_tokens": round(avg_modular, 0),
            "avg_direct_tokens": round(avg_direct, 0),
            "avg_modular_reduction_percent": round(avg_modular_reduction, 1),
            "avg_direct_reduction_percent": round(avg_direct_reduction, 1),
            "best_approach": "direct_module" if avg_direct < avg_modular else "modular",
            "best_reduction_percent": round(max(avg_modular_reduction, avg_direct_reduction), 1)
        }
        
        return results
    
    def print_summary(self, results: Dict):
        """Print summary table of results.
        
        Args:
            results: Results dict from measure_all()
        """
        print("\n" + "="*60)
        print("SUMMARY REPORT")
        print("="*60)
        
        summary = results.get("summary", {})
        
        print(f"\n📊 Baseline (Full cortex.md):")
        print(f"   Tokens: {summary.get('baseline_tokens', 0):,}")
        
        print(f"\n📊 Modular Approach (Slim + Module):")
        print(f"   Avg Tokens: {summary.get('avg_modular_tokens', 0):,.0f}")
        print(f"   Avg Reduction: {summary.get('avg_modular_reduction_percent', 0):.1f}%")
        
        print(f"\n📊 Direct Module Approach (Module Only):")
        print(f"   Avg Tokens: {summary.get('avg_direct_tokens', 0):,.0f}")
        print(f"   Avg Reduction: {summary.get('avg_direct_reduction_percent', 0):.1f}%")
        
        print(f"\n🏆 Best Approach: {summary.get('best_approach', 'unknown').upper()}")
        print(f"   Best Reduction: {summary.get('best_reduction_percent', 0):.1f}%")
        
        print("\n" + "="*60)
        print("DETAILED BREAKDOWN")
        print("="*60)
        
        # Comparison table
        print("\n| Approach | Module | Lines | Tokens | Reduction |")
        print("|----------|--------|-------|--------|-----------|")
        
        baseline = results.get("baseline", {})
        print(f"| Baseline | Full cortex.md | {baseline.get('lines', 0):,} | {baseline.get('tokens', 0):,} | 0% |")
        
        for module in ["story", "setup", "technical"]:
            modular = results.get("modular", {}).get(module, {})
            print(f"| Modular | {module} | {modular.get('total_lines', 0):,} | {modular.get('total_tokens', 0):,} | {modular.get('reduction_percent', 0):.1f}% |")
        
        for module in ["story", "setup", "technical"]:
            direct = results.get("direct_module", {}).get(module, {})
            print(f"| Direct | {module} | {direct.get('lines', 0):,} | {direct.get('tokens', 0):,} | {direct.get('reduction_percent', 0):.1f}% |")
        
        print("")
    
    def export_results(self, results: Dict, output_file: Path):
        """Export results to JSON file.
        
        Args:
            results: Results dict
            output_file: Output file path
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✅ Results exported to: {output_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Measure token counts for CORTEX Phase 3 validation")
    parser.add_argument("--all", action="store_true", help="Measure all approaches")
    parser.add_argument("--baseline", action="store_true", help="Measure baseline only")
    parser.add_argument("--modular", type=str, help="Measure modular approach (story, setup, or technical)")
    parser.add_argument("--direct", type=str, help="Measure direct module approach (story, setup, or technical)")
    parser.add_argument("--export", type=str, help="Export results to JSON file")
    
    args = parser.parse_args()
    
    measurer = TokenMeasurer()
    
    if args.all or not any([args.baseline, args.modular, args.direct]):
        # Default: measure all
        results = measurer.measure_all()
        measurer.print_summary(results)
        
        if args.export:
            output_file = Path(args.export)
            measurer.export_results(results, output_file)
    
    elif args.baseline:
        result = measurer.measure_baseline()
        if args.export:
            output_file = Path(args.export)
            measurer.export_results({"baseline": result, "timestamp": datetime.now().isoformat()}, output_file)
    
    elif args.modular:
        result = measurer.measure_modular(args.modular)
        if args.export:
            output_file = Path(args.export)
            measurer.export_results({"modular": {args.modular: result}, "timestamp": datetime.now().isoformat()}, output_file)
    
    elif args.direct:
        result = measurer.measure_direct_module(args.direct)
        if args.export:
            output_file = Path(args.export)
            measurer.export_results({"direct_module": {args.direct: result}, "timestamp": datetime.now().isoformat()}, output_file)


if __name__ == "__main__":
    main()
