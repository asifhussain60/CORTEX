"""
Phase 2.3 Production Validation Script

Tests EnhancedExecutiveSummaryAggregator on 3 production repos:
1. CORTEX (local) - Large Python project with comprehensive README
2. luum-fresh (local) - Real-world production codebase
3. Mock data - Minimal test case

Measures:
- Quality score improvement (baseline vs enhanced)
- Performance (<30s target)
- Summary specificity (>200 chars, no generic phrases)
- Source integration (how many sources used)

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import sys
import time
import json
from pathlib import Path
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.dashboard.aggregators.executive_summary_aggregator import ExecutiveSummaryAggregator
from src.dashboard.aggregators.enhanced_executive_summary_aggregator import EnhancedExecutiveSummaryAggregator


class ProductionValidator:
    """Validates enhanced aggregator on production repositories."""
    
    def __init__(self):
        self.results = []
        self.cortex_path = Path("C:/PROJECTS/CORTEX")
        self.luum_path = Path("C:/PROJECTS/luum-fresh")
        self.mock_path = Path("cortex-brain/dashboards/data/repos/mock")
    
    def validate_repo(
        self,
        repo_name: str,
        repo_path: Path,
        data_dir: Path
    ) -> Dict[str, Any]:
        """Validate both baseline and enhanced aggregators on a repository."""
        print(f"\n{'='*70}")
        print(f"Validating: {repo_name}")
        print(f"{'='*70}")
        
        if not repo_path.exists():
            print(f"⚠️  Repository not found: {repo_path}")
            return {
                "repo": repo_name,
                "status": "skipped",
                "reason": "Repository not found"
            }
        
        # Prepare data directory
        if not data_dir.exists():
            print(f"⚠️  Data directory not found: {data_dir}")
            return {
                "repo": repo_name,
                "status": "skipped",
                "reason": "Data directory not found"
            }
        
        result = {
            "repo": repo_name,
            "repo_path": str(repo_path),
            "data_dir": str(data_dir),
            "baseline": {},
            "enhanced": {},
            "improvement": {},
            "status": "success"
        }
        
        # Test baseline aggregator
        print("\n📊 Baseline ExecutiveSummaryAggregator:")
        try:
            baseline_start = time.time()
            baseline_agg = ExecutiveSummaryAggregator(data_dir)
            baseline_result = baseline_agg.aggregate()
            baseline_time = time.time() - baseline_start
            
            baseline_summary = baseline_result.get("what_it_does", "")
            baseline_len = len(baseline_summary) if isinstance(baseline_summary, str) else len(str(baseline_summary))
            
            result["baseline"] = {
                "time_seconds": round(baseline_time, 2),
                "summary_length": baseline_len,
                "has_tagline": "tagline" in baseline_result,
                "has_composition": "composition" in baseline_result,
                "quality_score": self._estimate_quality_baseline(baseline_result)
            }
            
            print(f"   ⏱️  Time: {baseline_time:.2f}s")
            print(f"   📏 Summary length: {baseline_len} chars")
            print(f"   ⭐ Quality score: {result['baseline']['quality_score']}/10")
            
        except Exception as e:
            print(f"   ❌ Baseline failed: {e}")
            result["baseline"]["error"] = str(e)
        
        # Test enhanced aggregator
        print("\n🚀 Enhanced ExecutiveSummaryAggregator:")
        try:
            enhanced_start = time.time()
            enhanced_agg = EnhancedExecutiveSummaryAggregator(data_dir, repo_path)
            enhanced_result = enhanced_agg.aggregate()
            enhanced_time = time.time() - enhanced_start
            
            what_it_does = enhanced_result.get("what_it_does", {})
            enhanced_summary = what_it_does.get("summary", "")
            enhanced_len = len(enhanced_summary)
            
            # Check for generic phrases
            generic_phrases = [
                "software application",
                "this system",
                "modern technologies"
            ]
            has_generic = any(phrase in enhanced_summary.lower() for phrase in generic_phrases)
            
            result["enhanced"] = {
                "time_seconds": round(enhanced_time, 2),
                "summary_length": enhanced_len,
                "quality_score": enhanced_result.get("quality_score", 0),
                "sources_used": len(enhanced_result.get("intelligence_sources_used", [])),
                "source_list": enhanced_result.get("intelligence_sources_used", []),
                "has_generic_phrases": has_generic,
                "key_points_count": len(what_it_does.get("key_points", [])),
                "source_priority": what_it_does.get("source_priority", [])
            }
            
            print(f"   ⏱️  Time: {enhanced_time:.2f}s")
            print(f"   📏 Summary length: {enhanced_len} chars")
            print(f"   ⭐ Quality score: {result['enhanced']['quality_score']}/10")
            print(f"   🔗 Sources used: {result['enhanced']['sources_used']} ({', '.join(result['enhanced']['source_list'])})")
            print(f"   🎯 Key points: {result['enhanced']['key_points_count']}")
            print(f"   🚫 Has generic phrases: {has_generic}")
            print(f"   📋 Priority order: {' > '.join(result['enhanced']['source_priority'][:3])}")
            
            # Sample summary
            print(f"\n   📝 Summary preview:")
            print(f"      {enhanced_summary[:200]}{'...' if len(enhanced_summary) > 200 else ''}")
            
        except Exception as e:
            print(f"   ❌ Enhanced failed: {e}")
            import traceback
            traceback.print_exc()
            result["enhanced"]["error"] = str(e)
        
        # Calculate improvements
        if "error" not in result["baseline"] and "error" not in result["enhanced"]:
            result["improvement"] = {
                "quality_delta": result["enhanced"]["quality_score"] - result["baseline"]["quality_score"],
                "length_delta": result["enhanced"]["summary_length"] - result["baseline"]["summary_length"],
                "time_delta": result["enhanced"]["time_seconds"] - result["baseline"]["time_seconds"],
                "percentage_improvement": round(
                    ((result["enhanced"]["quality_score"] - result["baseline"]["quality_score"]) / 
                     max(result["baseline"]["quality_score"], 1)) * 100, 1
                )
            }
            
            print(f"\n📈 Improvements:")
            print(f"   Quality: +{result['improvement']['quality_delta']} points ({result['improvement']['percentage_improvement']}% improvement)")
            print(f"   Length: +{result['improvement']['length_delta']} chars")
            print(f"   Time: +{result['improvement']['time_delta']:.2f}s")
        
        return result
    
    def _estimate_quality_baseline(self, baseline_result: Dict[str, Any]) -> int:
        """Estimate quality score for baseline (doesn't have quality_score field)."""
        score = 3  # Baseline starts at 3/10
        
        what_it_does = baseline_result.get("what_it_does", "")
        if isinstance(what_it_does, str):
            if len(what_it_does) > 100:
                score += 1
        
        if baseline_result.get("tagline"):
            score += 1
        
        return min(score, 10)
    
    def run_validation(self):
        """Run validation on all repositories."""
        print("🧪 Phase 2.3 Production Validation")
        print("Testing EnhancedExecutiveSummaryAggregator vs Baseline\n")
        
        # Validate CORTEX
        cortex_data = self.cortex_path / "cortex-brain" / "dashboards" / "data" / "repos" / "CORTEX"
        if cortex_data.exists():
            self.results.append(self.validate_repo("CORTEX", self.cortex_path, cortex_data))
        
        # Validate luum-fresh
        luum_data = self.cortex_path / "cortex-brain" / "dashboards" / "data" / "repos" / "luum-fresh"
        if luum_data.exists():
            self.results.append(self.validate_repo("luum-fresh", self.luum_path, luum_data))
        
        # Validate mock
        mock_data = self.mock_path
        if mock_data.exists():
            self.results.append(self.validate_repo("mock", self.mock_path, mock_data))
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print validation summary."""
        print(f"\n\n{'='*70}")
        print("📊 VALIDATION SUMMARY")
        print(f"{'='*70}\n")
        
        successful = [r for r in self.results if r.get("status") == "success"]
        skipped = [r for r in self.results if r.get("status") == "skipped"]
        
        print(f"✅ Successful validations: {len(successful)}/{len(self.results)}")
        if skipped:
            print(f"⚠️  Skipped: {len(skipped)} ({', '.join(r['repo'] for r in skipped)})")
        
        if successful:
            print("\n📈 Quality Improvements:")
            for result in successful:
                if "improvement" in result and result["improvement"]:
                    imp = result["improvement"]
                    print(f"   {result['repo']:15} → +{imp['quality_delta']} points ({imp['percentage_improvement']:+.1f}%)")
            
            print("\n⏱️  Performance:")
            for result in successful:
                if "enhanced" in result and "time_seconds" in result["enhanced"]:
                    time_s = result["enhanced"]["time_seconds"]
                    status = "✓" if time_s < 30 else "⚠️"
                    print(f"   {result['repo']:15} → {time_s:.2f}s {status}")
            
            print("\n🔗 Source Integration:")
            for result in successful:
                if "enhanced" in result and "sources_used" in result["enhanced"]:
                    sources = result["enhanced"]["sources_used"]
                    source_list = ', '.join(result["enhanced"]["source_list"])
                    print(f"   {result['repo']:15} → {sources}/5 sources ({source_list})")
            
            print("\n🎯 Average Metrics:")
            improvements = [r for r in successful if "improvement" in r and "quality_delta" in r.get("improvement", {})]
            if improvements:
                avg_quality_delta = sum(r["improvement"]["quality_delta"] for r in improvements) / len(improvements)
            else:
                avg_quality_delta = 0
            
            enhanced_results = [r for r in successful if "enhanced" in r and "time_seconds" in r["enhanced"]]
            avg_time = sum(r["enhanced"]["time_seconds"] for r in enhanced_results) / len(enhanced_results) if enhanced_results else 0
            avg_sources = sum(r["enhanced"]["sources_used"] for r in enhanced_results) / len(enhanced_results) if enhanced_results else 0
            
            print(f"   Quality improvement: +{avg_quality_delta:.1f} points")
            print(f"   Average time: {avg_time:.2f}s")
            print(f"   Average sources: {avg_sources:.1f}/5")
        
        print(f"\n{'='*70}")
        
        # Save results
        results_file = Path("cortex-brain/documents/reports/phase-2.3-production-validation.json")
        results_file.parent.mkdir(parents=True, exist_ok=True)
        results_file.write_text(json.dumps(self.results, indent=2))
        print(f"\n💾 Detailed results saved: {results_file}")


if __name__ == "__main__":
    validator = ProductionValidator()
    validator.run_validation()
