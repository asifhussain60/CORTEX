"""Benchmark script to measure parallel vs sequential performance."""
import time
import tempfile
import shutil
from pathlib import Path
from src.intelligence.executive_summary_orchestrator import ExecutiveSummaryOrchestrator

def create_test_repo():
    """Create a test repository with README and git history."""
    repo_dir = tempfile.mkdtemp(prefix="benchmark_repo_")
    repo_path = Path(repo_dir)
    
    # Create README with substantial content
    readme_content = """# Benchmark Test Repository

## Overview
This is a test repository for benchmarking parallel processing performance.

## Features
- Feature 1: Authentication and authorization
- Feature 2: Data processing pipeline
- Feature 3: REST API endpoints
- Feature 4: Database integration
- Feature 5: Caching layer

## Tech Stack
- Python 3.8+
- FastAPI
- PostgreSQL
- Redis
- Docker

## Installation
```bash
pip install -r requirements.txt
```

## Usage
Run the application with:
```bash
python main.py
```

## Testing
Execute tests with:
```bash
pytest tests/
```
"""
    readme_path = repo_path / "README.md"
    readme_path.write_text(readme_content, encoding='utf-8')
    
    return str(repo_path)

def benchmark_sequential(repo_path, iterations=3):
    """Benchmark sequential execution."""
    orchestrator = ExecutiveSummaryOrchestrator()
    times = []
    
    print(f"\n🔄 Running SEQUENTIAL benchmark ({iterations} iterations)...")
    for i in range(iterations):
        start = time.perf_counter()
        summary = orchestrator.generate_summary(
            repo_path=repo_path,
            include_readme=True,
            include_git=True,  # Include git for realistic load
            include_domains=True,
            git_days=30,  # 30 days of history
            parallel=False  # SEQUENTIAL
        )
        elapsed = time.perf_counter() - start
        times.append(elapsed)
        print(f"  Iteration {i+1}: {elapsed:.2f}s")
    
    avg = sum(times) / len(times)
    print(f"  📊 Average: {avg:.2f}s")
    return avg

def benchmark_parallel(repo_path, iterations=3):
    """Benchmark parallel execution."""
    orchestrator = ExecutiveSummaryOrchestrator()
    times = []
    
    print(f"\n⚡ Running PARALLEL benchmark ({iterations} iterations)...")
    for i in range(iterations):
        start = time.perf_counter()
        summary = orchestrator.generate_summary(
            repo_path=repo_path,
            include_readme=True,
            include_git=True,  # Include git for realistic load
            include_domains=True,
            git_days=30,  # 30 days of history
            parallel=True  # PARALLEL
        )
        elapsed = time.perf_counter() - start
        times.append(elapsed)
        print(f"  Iteration {i+1}: {elapsed:.2f}s")
    
    avg = sum(times) / len(times)
    print(f"  📊 Average: {avg:.2f}s")
    return avg

def main():
    print("=" * 60)
    print("PARALLEL PROCESSING PERFORMANCE BENCHMARK")
    print("=" * 60)
    
    # Create test repository
    print("\n📁 Creating test repository...")
    repo_path = create_test_repo()
    print(f"   Repository: {repo_path}")
    
    try:
        # Benchmark sequential
        seq_time = benchmark_sequential(repo_path, iterations=3)
        
        # Benchmark parallel
        par_time = benchmark_parallel(repo_path, iterations=3)
        
        # Calculate improvement
        improvement = ((seq_time - par_time) / seq_time) * 100
        speedup = seq_time / par_time
        
        # Results
        print("\n" + "=" * 60)
        print("📊 RESULTS")
        print("=" * 60)
        print(f"Sequential Average:  {seq_time:.2f}s")
        print(f"Parallel Average:    {par_time:.2f}s")
        print(f"Improvement:         {improvement:.1f}% faster")
        print(f"Speedup:             {speedup:.2f}x")
        
        if par_time < seq_time:
            print("\n✅ OPTIMIZATION SUCCESSFUL - Parallel is faster!")
        else:
            print("\n⚠️  WARNING - Parallel slower (threading overhead?)")
        
        # Target assessment
        target_improvement = 70.0  # 3x = ~70% improvement
        if improvement >= target_improvement:
            print(f"🎯 TARGET MET: {improvement:.1f}% >= {target_improvement}% target")
        else:
            print(f"⚠️  TARGET MISSED: {improvement:.1f}% < {target_improvement}% target")
        
    finally:
        # Cleanup
        shutil.rmtree(repo_path, ignore_errors=True)
        print(f"\n🧹 Cleaned up test repository")

if __name__ == "__main__":
    main()
