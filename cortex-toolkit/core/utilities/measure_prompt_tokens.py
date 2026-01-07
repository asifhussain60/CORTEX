"""
CORTEX Prompt Token Baseline Measurement

Measures token count for all CORTEX prompt files to establish optimization baseline.
Tracks changes over time to demonstrate token reduction effectiveness.

Usage:
    python scripts/measure_prompt_tokens.py
    python scripts/measure_prompt_tokens.py --compare baseline.json

Author: Asif Hussain
Created: December 15, 2025
Version: 1.0.0
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import argparse


# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False
    print("⚠️  Warning: tiktoken not installed. Using approximate counting (4 chars = 1 token)")
    print("   Install with: pip install tiktoken")


@dataclass
class FileTokenMetrics:
    """Token metrics for a single file."""
    file_path: str
    relative_path: str
    tokens: int
    lines: int
    characters: int
    timestamp: str
    
    @property
    def tokens_per_line(self) -> float:
        return self.tokens / self.lines if self.lines > 0 else 0.0


@dataclass
class BaselineReport:
    """Complete baseline report."""
    measurement_date: str
    cortex_version: str
    total_files: int
    total_tokens: int
    total_lines: int
    total_characters: int
    files: List[FileTokenMetrics]
    tokenizer: str  # 'tiktoken' or 'approximate'
    
    @property
    def avg_tokens_per_file(self) -> float:
        return self.total_tokens / self.total_files if self.total_files > 0 else 0.0
    
    @property
    def avg_tokens_per_line(self) -> float:
        return self.total_tokens / self.total_lines if self.total_lines > 0 else 0.0


class PromptTokenCounter:
    """Count tokens in CORTEX prompt files."""
    
    def __init__(self, use_tiktoken: bool = True):
        """
        Initialize token counter.
        
        Args:
            use_tiktoken: Use tiktoken if available (more accurate)
        """
        self.use_tiktoken = use_tiktoken and HAS_TIKTOKEN
        
        if self.use_tiktoken:
            # Use cl100k_base encoding (GPT-4, Claude)
            self.encoding = tiktoken.get_encoding("cl100k_base")
            print("✅ Using tiktoken with cl100k_base encoding")
        else:
            self.encoding = None
            print("ℹ️  Using approximate counting (4 chars ≈ 1 token)")
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.
        
        Args:
            text: Text to count
        
        Returns:
            Token count
        """
        if self.use_tiktoken:
            return len(self.encoding.encode(text))
        else:
            # Approximate: 1 token ≈ 4 characters
            return len(text) // 4
    
    def measure_file(self, file_path: Path, root_path: Path) -> FileTokenMetrics:
        """
        Measure tokens in a single file.
        
        Args:
            file_path: Path to file
            root_path: Root path for relative path calculation
        
        Returns:
            FileTokenMetrics with measurements
        """
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        return FileTokenMetrics(
            file_path=str(file_path),
            relative_path=str(file_path.relative_to(root_path)),
            tokens=self.count_tokens(content),
            lines=len(lines),
            characters=len(content),
            timestamp=datetime.now().isoformat()
        )
    
    def measure_directory(
        self,
        directory: Path,
        patterns: List[str] = None,
        exclude_patterns: List[str] = None
    ) -> List[FileTokenMetrics]:
        """
        Measure all files in directory matching patterns.
        
        Args:
            directory: Directory to scan
            patterns: File patterns to include (e.g., ['*.md', '*.txt'])
            exclude_patterns: Patterns to exclude
        
        Returns:
            List of FileTokenMetrics
        """
        if patterns is None:
            patterns = ['*.md', '*.txt', '*.yaml', '*.yml']
        
        if exclude_patterns is None:
            exclude_patterns = ['**/node_modules/**', '**/.venv/**', '**/archive/**']
        
        metrics = []
        
        for pattern in patterns:
            for file_path in directory.rglob(pattern):
                # Check exclusions
                if any(file_path.match(excl) for excl in exclude_patterns):
                    continue
                
                try:
                    file_metrics = self.measure_file(file_path, directory)
                    metrics.append(file_metrics)
                    print(f"  ✓ {file_metrics.relative_path}: {file_metrics.tokens:,} tokens")
                except Exception as e:
                    print(f"  ✗ {file_path.name}: Error - {e}")
        
        return metrics


def measure_cortex_prompts(cortex_root: Path) -> BaselineReport:
    """
    Measure all CORTEX prompt files.
    
    Args:
        cortex_root: Path to CORTEX root directory
    
    Returns:
        BaselineReport with complete measurements
    """
    print("=" * 80)
    print("📊 CORTEX Prompt Token Baseline Measurement")
    print("=" * 80)
    print()
    
    counter = PromptTokenCounter()
    
    # Measure key directories
    directories = {
        '.github/prompts': ['*.md'],
        'cortex-brain': ['*.md', '*.yaml', '*.yml'],
        'cortex-brain/response-templates': ['*.yaml', '*.yml'],
        'cortex-brain/tier0': ['*.yaml', '*.yml'],
        'cortex-brain/tier1': ['*.md', '*.yaml'],
        'cortex-brain/tier2': ['*.md', '*.yaml'],
        'cortex-brain/tier3': ['*.md', '*.yaml'],
    }
    
    all_metrics = []
    
    for dir_path, patterns in directories.items():
        full_path = cortex_root / dir_path
        if not full_path.exists():
            print(f"⚠️  Skipping {dir_path} (not found)")
            continue
        
        print(f"\n📁 Measuring {dir_path}:")
        metrics = counter.measure_directory(full_path, patterns)
        all_metrics.extend(metrics)
    
    # Calculate totals
    total_tokens = sum(m.tokens for m in all_metrics)
    total_lines = sum(m.lines for m in all_metrics)
    total_chars = sum(m.characters for m in all_metrics)
    
    report = BaselineReport(
        measurement_date=datetime.now().isoformat(),
        cortex_version="3.9.0",
        total_files=len(all_metrics),
        total_tokens=total_tokens,
        total_lines=total_lines,
        total_characters=total_chars,
        files=all_metrics,
        tokenizer='tiktoken' if counter.use_tiktoken else 'approximate'
    )
    
    return report


def print_summary(report: BaselineReport) -> None:
    """Print summary of baseline measurements."""
    print()
    print("=" * 80)
    print("📊 BASELINE SUMMARY")
    print("=" * 80)
    print()
    print(f"Measurement Date: {report.measurement_date}")
    print(f"CORTEX Version:   {report.cortex_version}")
    print(f"Tokenizer:        {report.tokenizer}")
    print()
    print(f"Total Files:      {report.total_files:,}")
    print(f"Total Tokens:     {report.total_tokens:,}")
    print(f"Total Lines:      {report.total_lines:,}")
    print(f"Total Characters: {report.total_characters:,}")
    print()
    print(f"Avg Tokens/File:  {report.avg_tokens_per_file:,.1f}")
    print(f"Avg Tokens/Line:  {report.avg_tokens_per_line:.2f}")
    print()
    
    # Top 10 largest files
    print("📈 Top 10 Largest Files:")
    print()
    sorted_files = sorted(report.files, key=lambda f: f.tokens, reverse=True)[:10]
    for i, file in enumerate(sorted_files, 1):
        pct = (file.tokens / report.total_tokens) * 100
        print(f"  {i:2d}. {file.relative_path}")
        print(f"      {file.tokens:,} tokens ({pct:.1f}%) | {file.lines:,} lines | {file.tokens_per_line:.1f} tok/line")
    
    print()


def compare_baselines(baseline1: BaselineReport, baseline2: BaselineReport) -> None:
    """Compare two baseline reports."""
    print()
    print("=" * 80)
    print("🔍 BASELINE COMPARISON")
    print("=" * 80)
    print()
    
    token_diff = baseline2.total_tokens - baseline1.total_tokens
    token_diff_pct = (token_diff / baseline1.total_tokens) * 100 if baseline1.total_tokens > 0 else 0
    
    file_diff = baseline2.total_files - baseline1.total_files
    
    print(f"Baseline 1: {baseline1.measurement_date}")
    print(f"Baseline 2: {baseline2.measurement_date}")
    print()
    print(f"Token Change:   {token_diff:+,} ({token_diff_pct:+.1f}%)")
    print(f"File Change:    {file_diff:+,}")
    print()
    
    if token_diff < 0:
        print(f"✅ Token reduction achieved: {abs(token_diff):,} tokens saved!")
    elif token_diff > 0:
        print(f"⚠️  Token increase: {token_diff:,} tokens added")
    else:
        print(f"ℹ️  No token change")
    
    # File-by-file comparison
    print()
    print("📊 File-Level Changes:")
    print()
    
    # Create lookup maps
    baseline1_map = {f.relative_path: f for f in baseline1.files}
    baseline2_map = {f.relative_path: f for f in baseline2.files}
    
    all_files = set(baseline1_map.keys()) | set(baseline2_map.keys())
    
    changes = []
    for file_path in all_files:
        f1 = baseline1_map.get(file_path)
        f2 = baseline2_map.get(file_path)
        
        if f1 and f2:
            diff = f2.tokens - f1.tokens
            if diff != 0:
                changes.append((file_path, f1.tokens, f2.tokens, diff))
        elif f2:
            changes.append((file_path, 0, f2.tokens, f2.tokens))
        elif f1:
            changes.append((file_path, f1.tokens, 0, -f1.tokens))
    
    # Sort by absolute change
    changes.sort(key=lambda x: abs(x[3]), reverse=True)
    
    for file_path, old_tokens, new_tokens, diff in changes[:15]:
        if diff < 0:
            print(f"  ✅ {file_path}")
            print(f"     {old_tokens:,} → {new_tokens:,} tokens ({diff:,}, {(diff/old_tokens)*100:.1f}%)")
        elif diff > 0:
            print(f"  ⚠️  {file_path}")
            print(f"     {old_tokens:,} → {new_tokens:,} tokens ({diff:+,}, {(diff/old_tokens)*100 if old_tokens else 0:+.1f}%)")
    
    if len(changes) > 15:
        print(f"  ... and {len(changes) - 15} more files")
    
    print()


def save_baseline(report: BaselineReport, output_path: Path) -> None:
    """Save baseline report to JSON."""
    data = asdict(report)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"💾 Baseline saved to: {output_path}")


def load_baseline(baseline_path: Path) -> BaselineReport:
    """Load baseline report from JSON."""
    with open(baseline_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Convert file dicts back to FileTokenMetrics
    files = [FileTokenMetrics(**f) for f in data['files']]
    data['files'] = files
    
    return BaselineReport(**data)


def main():
    parser = argparse.ArgumentParser(description='Measure CORTEX prompt token counts')
    parser.add_argument('--compare', type=str, help='Compare with baseline JSON file')
    parser.add_argument('--output', type=str, default='cortex-token-baseline.json',
                       help='Output JSON file (default: cortex-token-baseline.json)')
    parser.add_argument('--root', type=str, default='.',
                       help='CORTEX root directory (default: current directory)')
    
    args = parser.parse_args()
    
    cortex_root = Path(args.root).resolve()
    
    if not (cortex_root / 'cortex-brain').exists():
        print("❌ Error: cortex-brain directory not found")
        print(f"   Searched in: {cortex_root}")
        sys.exit(1)
    
    # Measure current state
    current_report = measure_cortex_prompts(cortex_root)
    print_summary(current_report)
    
    # Compare if requested
    if args.compare:
        baseline_path = Path(args.compare)
        if not baseline_path.exists():
            print(f"❌ Error: Baseline file not found: {baseline_path}")
            sys.exit(1)
        
        baseline_report = load_baseline(baseline_path)
        compare_baselines(baseline_report, current_report)
    
    # Save current baseline
    output_path = cortex_root / args.output
    save_baseline(current_report, output_path)
    
    print()
    print("=" * 80)
    print("✅ Measurement Complete")
    print("=" * 80)


if __name__ == '__main__':
    main()
