"""
CORTEX Performance Profiling Script

Profiles all major CORTEX operations and tier query times to identify bottlenecks.

Target Performance Metrics:
- Tier 1 (Working Memory): ≤50ms query time
- Tier 2 (Knowledge Graph): ≤150ms pattern search
- Tier 3 (Context Intelligence): ≤500ms analysis
- Operations: <5s total, <1s for help command

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import cProfile
import pstats
import io
import time
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.operations import execute_operation
from src.config import config as cortex_config


class PerformanceProfiler:
    """Profile CORTEX operations and tier performance."""
    
    def __init__(self):
        """Initialize profiler."""
        self.config = {
            'cortex_root': cortex_config.root_path
        }
        self.results = {
            'tier_queries': {},
            'operations': {},
            'hotspots': [],
            'summary': {}
        }
    
    def profile_tier1_queries(self) -> Dict[str, float]:
        """
        Profile Tier 1 (Working Memory) query performance.
        
        Target: ≤50ms per query
        
        Returns:
            Dict of query times in milliseconds
        """
        print("\n" + "="*70)
        print("PROFILING TIER 1 (WORKING MEMORY)")
        print("="*70)
        
        results = {}
        
        try:
            from src.tier1.conversation_manager import ConversationManager
            cortex_root = Path(self.config.get('cortex_root', Path.cwd()))
            db_path = cortex_root / 'cortex-brain' / 'tier1' / 'conversations.db'
            
            if not db_path.exists():
                print(f"⚠️  Database not found: {db_path}")
                return results
            
            cm = ConversationManager(db_path)
            
            # Test 1: Get recent conversations
            start = time.perf_counter()
            conversations = cm.get_recent_conversations(limit=20)
            elapsed = (time.perf_counter() - start) * 1000
            results['get_recent_conversations'] = elapsed
            print(f"✓ get_recent_conversations(20): {elapsed:.2f}ms {'✅' if elapsed <= 50 else '⚠️ SLOW'}")
            
            # Test 2: Get conversation by ID (if any exist)
            if conversations:
                conv_id = conversations[0]['conversation_id']
                start = time.perf_counter()
                conv = cm.get_conversation(conv_id)
                elapsed = (time.perf_counter() - start) * 1000
                results['get_conversation_by_id'] = elapsed
                print(f"✓ get_conversation(id): {elapsed:.2f}ms {'✅' if elapsed <= 50 else '⚠️ SLOW'}")
            
            # Test 3: Get messages for conversation
            if conversations:
                conv_id = conversations[0]['conversation_id']
                start = time.perf_counter()
                messages = cm.get_messages(conv_id)
                elapsed = (time.perf_counter() - start) * 1000
                results['get_messages'] = elapsed
                print(f"✓ get_messages(id): {elapsed:.2f}ms {'✅' if elapsed <= 50 else '⚠️ SLOW'}")
            
            # Test 4: Get active conversation
            start = time.perf_counter()
            active = cm.get_active_conversation('profiler-test')
            elapsed = (time.perf_counter() - start) * 1000
            results['get_active_conversation'] = elapsed
            print(f"✓ get_active_conversation(): {elapsed:.2f}ms {'✅' if elapsed <= 50 else '⚠️ SLOW'}")
            
        except Exception as e:
            print(f"❌ Tier 1 profiling failed: {e}")
        
        return results
    
    def profile_tier2_queries(self) -> Dict[str, float]:
        """
        Profile Tier 2 (Knowledge Graph) query performance.
        
        Target: ≤150ms per pattern search
        
        Returns:
            Dict of query times in milliseconds
        """
        print("\n" + "="*70)
        print("PROFILING TIER 2 (KNOWLEDGE GRAPH)")
        print("="*70)
        
        results = {}
        
        try:
            from src.tier2 import KnowledgeGraph, PatternType
            cortex_root = Path(self.config.get('cortex_root', Path.cwd()))
            kg_path = cortex_root / 'cortex-brain' / 'tier2' / 'knowledge_graph.db'
            
            if not kg_path.exists():
                print(f"⚠️  Database not found: {kg_path}")
                return results
            
            kg = KnowledgeGraph(kg_path)
            
            # Test 1: Get patterns by type (workflow)
            start = time.perf_counter()
            patterns = kg.get_patterns_by_type(PatternType.WORKFLOW)
            elapsed = (time.perf_counter() - start) * 1000
            results['get_patterns_by_type'] = elapsed
            print(f"✓ get_patterns_by_type(WORKFLOW): {elapsed:.2f}ms {'✅' if elapsed <= 150 else '⚠️ SLOW'}")
            
            # Test 2: Full-text search (FTS5)
            start = time.perf_counter()
            search_results = kg.search_patterns('authentication', limit=10)
            elapsed = (time.perf_counter() - start) * 1000
            results['search_patterns_fts'] = elapsed
            print(f"✓ search_patterns(FTS): {elapsed:.2f}ms {'✅' if elapsed <= 150 else '⚠️ SLOW'}")
            
            # Test 3: Find patterns by tag
            start = time.perf_counter()
            tagged = kg.find_patterns_by_tag('test')
            elapsed = (time.perf_counter() - start) * 1000
            results['find_patterns_by_tag'] = elapsed
            print(f"✓ find_patterns_by_tag('test'): {elapsed:.2f}ms {'✅' if elapsed <= 150 else '⚠️ SLOW'}")
            
            # Test 4: Get related patterns (if any exist)
            if patterns:
                pattern_id = patterns[0].pattern_id
                start = time.perf_counter()
                related = kg.get_related_patterns(pattern_id, limit=10)
                elapsed = (time.perf_counter() - start) * 1000
                results['get_related_patterns'] = elapsed
                print(f"✓ get_related_patterns(): {elapsed:.2f}ms {'✅' if elapsed <= 150 else '⚠️ SLOW'}")
            
        except Exception as e:
            print(f"❌ Tier 2 profiling failed: {e}")
        
        return results
    
    def profile_tier3_queries(self) -> Dict[str, float]:
        """
        Profile Tier 3 (Context Intelligence) query performance.
        
        Target: ≤500ms per analysis
        
        Returns:
            Dict of query times in milliseconds
        """
        print("\n" + "="*70)
        print("PROFILING TIER 3 (CONTEXT INTELLIGENCE)")
        print("="*70)
        
        results = {}
        
        try:
            from src.tier3.context_intelligence import ContextIntelligence
            cortex_root = Path(self.config.get('cortex_root', Path.cwd()))
            
            # Initialize context intelligence (will create DB if needed)
            # Pass None to use default path: cortex-brain/tier3/context.db
            ci = ContextIntelligence(db_path=None)
            
            # Test 1: Get git metrics
            start = time.perf_counter()
            metrics = ci.get_git_metrics(days=30)
            elapsed = (time.perf_counter() - start) * 1000
            results['get_git_metrics_30d'] = elapsed
            print(f"✓ get_git_metrics(30d): {elapsed:.2f}ms {'✅' if elapsed <= 500 else '⚠️ SLOW'}")
            
            # Test 2: Analyze file hotspots
            start = time.perf_counter()
            hotspots = ci.analyze_file_hotspots(days=30)
            elapsed = (time.perf_counter() - start) * 1000
            results['analyze_file_hotspots'] = elapsed
            print(f"✓ analyze_file_hotspots(30d): {elapsed:.2f}ms {'✅' if elapsed <= 500 else '⚠️ SLOW'}")
            
            # Test 3: Get unstable files
            start = time.perf_counter()
            unstable = ci.get_unstable_files(limit=10)
            elapsed = (time.perf_counter() - start) * 1000
            results['get_unstable_files'] = elapsed
            print(f"✓ get_unstable_files(10): {elapsed:.2f}ms {'✅' if elapsed <= 500 else '⚠️ SLOW'}")
            
            # Test 4: Calculate commit velocity
            start = time.perf_counter()
            velocity = ci.calculate_commit_velocity(window_days=7)
            elapsed = (time.perf_counter() - start) * 1000
            results['calculate_commit_velocity'] = elapsed
            print(f"✓ calculate_commit_velocity(7d): {elapsed:.2f}ms {'✅' if elapsed <= 500 else '⚠️ SLOW'}")
            
            # Test 5: Get context summary (comprehensive)
            start = time.perf_counter()
            summary = ci.get_context_summary()
            elapsed = (time.perf_counter() - start) * 1000
            results['get_context_summary'] = elapsed
            print(f"✓ get_context_summary(): {elapsed:.2f}ms {'✅' if elapsed <= 500 else '⚠️ SLOW'}")
            
        except Exception as e:
            print(f"❌ Tier 3 profiling failed: {e}")
        
        return results
    
    def profile_operation(self, operation_name: str, natural_language: str) -> Tuple[float, str]:
        """
        Profile a CORTEX operation.
        
        Args:
            operation_name: Name of operation for reporting
            natural_language: Natural language command to execute
            
        Returns:
            Tuple of (execution_time_ms, profiler_stats)
        """
        print(f"\n⏱️  Profiling: {operation_name}")
        
        # Create profiler
        profiler = cProfile.Profile()
        
        # Profile execution
        start = time.perf_counter()
        profiler.enable()
        try:
            result = execute_operation(natural_language)
            profiler.disable()
            elapsed = (time.perf_counter() - start) * 1000
            
            # Get stats
            s = io.StringIO()
            ps = pstats.Stats(profiler, stream=s)
            ps.strip_dirs()
            ps.sort_stats('cumulative')
            ps.print_stats(20)  # Top 20 functions
            
            status = '✅' if elapsed < 5000 else ('⚠️' if elapsed < 10000 else '❌ SLOW')
            print(f"  Duration: {elapsed:.2f}ms {status}")
            
            return elapsed, s.getvalue()
            
        except Exception as e:
            profiler.disable()
            print(f"  ❌ Failed: {e}")
            return -1, str(e)
    
    def profile_all_operations(self) -> Dict[str, Tuple[float, str]]:
        """Profile all major CORTEX operations."""
        print("\n" + "="*70)
        print("PROFILING CORTEX OPERATIONS")
        print("="*70)
        
        operations = {
            'help_command': 'help',
            'cleanup_quick': 'cleanup workspace',
            'story_refresh': 'refresh story',
            'demo_quick': 'demo quick',
            'environment_setup': 'setup environment'
        }
        
        results = {}
        for name, command in operations.items():
            try:
                elapsed, stats = self.profile_operation(name, command)
                results[name] = (elapsed, stats)
                time.sleep(0.5)  # Brief pause between operations
            except Exception as e:
                print(f"  ❌ Profiling {name} failed: {e}")
                results[name] = (-1, str(e))
        
        return results
    
    def analyze_hotspots(self, operation_stats: Dict[str, Tuple[float, str]]) -> List[Dict]:
        """
        Analyze profiling data to identify performance hotspots.
        
        Args:
            operation_stats: Dict of operation profiling results
            
        Returns:
            List of hotspot dictionaries
        """
        print("\n" + "="*70)
        print("ANALYZING PERFORMANCE HOTSPOTS")
        print("="*70)
        
        hotspots = []
        
        for op_name, (elapsed, stats) in operation_stats.items():
            if elapsed < 0:
                continue
            
            # Parse top functions from stats
            lines = stats.split('\n')
            for line in lines[5:15]:  # Skip headers, get top 10
                if line.strip() and not line.startswith('---'):
                    parts = line.split()
                    if len(parts) >= 6:
                        try:
                            cumtime = float(parts[3])
                            if cumtime > 0.1:  # More than 100ms
                                hotspots.append({
                                    'operation': op_name,
                                    'function': parts[-1],
                                    'cumulative_time_s': cumtime,
                                    'percentage': (cumtime / (elapsed/1000)) * 100
                                })
                        except (ValueError, IndexError):
                            continue
        
        # Sort by cumulative time
        hotspots.sort(key=lambda x: x['cumulative_time_s'], reverse=True)
        
        # Show top 10
        print("\n🔥 Top 10 Performance Hotspots:")
        for i, hotspot in enumerate(hotspots[:10], 1):
            print(f"{i}. {hotspot['function']}")
            print(f"   Operation: {hotspot['operation']}")
            print(f"   Time: {hotspot['cumulative_time_s']:.3f}s ({hotspot['percentage']:.1f}%)")
        
        return hotspots
    
    def generate_report(self) -> Dict:
        """Generate comprehensive performance report."""
        print("\n" + "="*70)
        print("GENERATING PERFORMANCE REPORT")
        print("="*70)
        
        # Profile tiers
        self.results['tier_queries']['tier1'] = self.profile_tier1_queries()
        self.results['tier_queries']['tier2'] = self.profile_tier2_queries()
        self.results['tier_queries']['tier3'] = self.profile_tier3_queries()
        
        # Profile operations
        self.results['operations'] = self.profile_all_operations()
        
        # Analyze hotspots
        self.results['hotspots'] = self.analyze_hotspots(self.results['operations'])
        
        # Calculate summary
        self.results['summary'] = self._calculate_summary()
        
        return self.results
    
    def _calculate_summary(self) -> Dict:
        """Calculate summary statistics."""
        summary = {
            'tier1_avg_ms': 0,
            'tier2_avg_ms': 0,
            'tier3_avg_ms': 0,
            'operations_avg_ms': 0,
            'tier1_target_met': False,
            'tier2_target_met': False,
            'tier3_target_met': False,
            'operations_target_met': False
        }
        
        # Tier 1 average
        tier1 = self.results['tier_queries'].get('tier1', {})
        if tier1:
            summary['tier1_avg_ms'] = sum(tier1.values()) / len(tier1)
            summary['tier1_target_met'] = summary['tier1_avg_ms'] <= 50
        
        # Tier 2 average
        tier2 = self.results['tier_queries'].get('tier2', {})
        if tier2:
            summary['tier2_avg_ms'] = sum(tier2.values()) / len(tier2)
            summary['tier2_target_met'] = summary['tier2_avg_ms'] <= 150
        
        # Tier 3 average
        tier3 = self.results['tier_queries'].get('tier3', {})
        if tier3:
            summary['tier3_avg_ms'] = sum(tier3.values()) / len(tier3)
            summary['tier3_target_met'] = summary['tier3_avg_ms'] <= 500
        
        # Operations average
        ops = self.results.get('operations', {})
        if ops:
            times = [t for t, _ in ops.values() if t > 0]
            if times:
                summary['operations_avg_ms'] = sum(times) / len(times)
                summary['operations_target_met'] = summary['operations_avg_ms'] <= 5000
        
        return summary
    
    def save_report(self, output_path: Path):
        """Save performance report to JSON file."""
        # Convert stats strings to summary for JSON
        report = {
            'tier_queries': self.results['tier_queries'],
            'operations': {
                name: {
                    'duration_ms': elapsed,
                    'stats_summary': stats[:500]  # First 500 chars
                }
                for name, (elapsed, stats) in self.results['operations'].items()
            },
            'hotspots': self.results['hotspots'][:20],  # Top 20
            'summary': self.results['summary']
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✅ Report saved: {output_path}")
    
    def print_summary(self):
        """Print performance summary."""
        print("\n" + "="*70)
        print("PERFORMANCE SUMMARY")
        print("="*70)
        
        summary = self.results['summary']
        
        print("\n📊 Tier Performance:")
        print(f"  Tier 1 (Working Memory):    {summary['tier1_avg_ms']:.2f}ms {'✅ PASS' if summary['tier1_target_met'] else '❌ FAIL'} (target: ≤50ms)")
        print(f"  Tier 2 (Knowledge Graph):   {summary['tier2_avg_ms']:.2f}ms {'✅ PASS' if summary['tier2_target_met'] else '❌ FAIL'} (target: ≤150ms)")
        print(f"  Tier 3 (Context):           {summary['tier3_avg_ms']:.2f}ms {'✅ PASS' if summary['tier3_target_met'] else '❌ FAIL'} (target: ≤500ms)")
        
        print("\n⚙️  Operations Performance:")
        print(f"  Average:                    {summary['operations_avg_ms']:.2f}ms {'✅ PASS' if summary['operations_target_met'] else '❌ FAIL'} (target: <5000ms)")
        
        ops = self.results.get('operations', {})
        for name, (elapsed, _) in ops.items():
            if elapsed > 0:
                status = '✅' if elapsed < 5000 else '⚠️'
                print(f"    {name:25s} {elapsed:.2f}ms {status}")
        
        # Overall verdict
        all_pass = (summary['tier1_target_met'] and 
                   summary['tier2_target_met'] and 
                   summary['tier3_target_met'] and 
                   summary['operations_target_met'])
        
        print("\n" + "="*70)
        if all_pass:
            print("✅ ALL PERFORMANCE TARGETS MET!")
        else:
            print("⚠️  SOME PERFORMANCE TARGETS NOT MET - OPTIMIZATION NEEDED")
        print("="*70)


def main():
    """Main profiling entry point."""
    print("="*70)
    print("CORTEX PERFORMANCE PROFILER")
    print("="*70)
    print("\nTarget Metrics:")
    print("  • Tier 1 queries: ≤50ms")
    print("  • Tier 2 queries: ≤150ms")
    print("  • Tier 3 queries: ≤500ms")
    print("  • Operations: <5s")
    print()
    
    profiler = PerformanceProfiler()
    
    # Generate full report
    results = profiler.generate_report()
    
    # Print summary
    profiler.print_summary()
    
    # Save detailed report
    cortex_root = Path(profiler.config.get('cortex_root', Path.cwd()))
    output_path = cortex_root / 'logs' / f'performance-report-{time.strftime("%Y%m%d-%H%M%S")}.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    profiler.save_report(output_path)
    
    print(f"\n📄 Full report: {output_path}")
    print("\nNext steps:")
    print("  1. Review hotspots and identify optimization targets")
    print("  2. Add missing database indexes (see 18-performance-optimization.md)")
    print("  3. Implement caching for frequently accessed data")
    print("  4. Create performance regression tests")


if __name__ == '__main__':
    main()
