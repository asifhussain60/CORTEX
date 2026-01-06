"""Profile enhanced aggregator performance"""
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.dashboard.aggregators.enhanced_executive_summary_aggregator import EnhancedExecutiveSummaryAggregator

data_dir = Path('cortex-brain/dashboards/data/repos/luum-fresh')
repo_path = Path('C:/PROJECTS/luum-fresh')

print('🔍 Profiling EnhancedExecutiveSummaryAggregator on luum-fresh\n')

t0 = time.time()
agg = EnhancedExecutiveSummaryAggregator(data_dir, repo_path)
print(f'⏱️  Init: {time.time()-t0:.2f}s')

# Profile individual extraction methods
print('\n📊 Individual Source Extraction:')

t1 = time.time()
git_insights = agg._extract_git_insights()
print(f'   Git commits: {time.time()-t1:.2f}s')

t2 = time.time()
readme_insights = agg._extract_readme_insights()
print(f'   README: {time.time()-t2:.2f}s')

t3 = time.time()
docstring_insights = agg._extract_docstring_insights()
print(f'   Docstrings: {time.time()-t3:.2f}s')

t4 = time.time()
domain_insights = agg._extract_domain_insights()
print(f'   Business domains: {time.time()-t4:.2f}s')

print(f'\n⏱️  Subtotal: {time.time()-t0:.2f}s')

# Full aggregate
t5 = time.time()
result = agg.aggregate()
print(f'⏱️  Full aggregate: {time.time()-t5:.2f}s')
print(f'⏱️  TOTAL: {time.time()-t0:.2f}s')

print(f'\n⭐ Quality: {result.get("quality_score")}/10')
print(f'🔗 Sources: {len(result.get("intelligence_sources_used", []))}/5')
