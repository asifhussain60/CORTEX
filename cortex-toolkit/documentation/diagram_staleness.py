#!/usr/bin/env python3
"""
CORTEX Diagram Staleness Checker

Detects diagrams (D3.js, Mermaid) that may be outdated based on:
- Diagram file age
- Related source code changes since diagram was last modified

Author: Asif Hussain
Version: 1.1.0

Security:
- Git subprocess with timeout (prevents hanging)
- Path validation
- Atomic file writes
"""

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def git_available() -> bool:
    """Check if git is available on the system."""
    return shutil.which("git") is not None


def safe_path(project_root: Path, user_path: str) -> Path:
    """Validate path stays within project root."""
    resolved = (project_root / user_path).resolve()
    if not str(resolved).startswith(str(project_root.resolve())):
        raise ValueError(f"Path escapes project root: {user_path}")
    return resolved


class DiagramStalenessChecker:
    """Check diagram freshness against source code changes."""
    
    # Source paths that affect diagrams
    SOURCE_PATHS = [
        "src/orchestrators/",
        "src/cortex_agents/",
        "cortex-brain/manifests/",
        "cortex-brain/tier0/",
        "cortex-brain/tier1/",
        "cortex-brain/tier2/",
        "cortex-brain/tier3/"
    ]
    
    def __init__(self, project_root: Path, max_age_days: int = 30):
        self.project_root = project_root
        self.docs_dir = project_root / "docs"
        self.max_age_days = max_age_days
        self.diagram_manifest: List[Dict[str, Any]] = []
        
    def find_diagrams(self) -> List[Dict[str, Any]]:
        """Find all HTML files containing D3.js or Mermaid diagrams."""
        diagrams = []
        
        if not self.docs_dir.exists():
            return diagrams
            
        for html_file in self.docs_dir.rglob("*.html"):
            try:
                content = html_file.read_text(encoding='utf-8')
                
                has_d3 = bool(re.search(r'd3\.\w+|d3\.js|<script.*d3', content, re.IGNORECASE))
                has_mermaid = bool(re.search(r'mermaid|```mermaid', content, re.IGNORECASE))
                
                if has_d3 or has_mermaid:
                    stat = html_file.stat()
                    diagrams.append({
                        "path": str(html_file.relative_to(self.project_root)),
                        "abs_path": str(html_file),
                        "has_d3": has_d3,
                        "has_mermaid": has_mermaid,
                        "diagram_types": self._detect_diagram_types(content),
                        "modified": datetime.fromtimestamp(stat.st_mtime),
                        "age_days": (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).days
                    })
            except Exception as e:
                print(f"Warning: Could not read {html_file}: {e}")
                
        return diagrams
    
    def _detect_diagram_types(self, content: str) -> List[str]:
        """Detect specific diagram types in content."""
        types = []
        
        # D3.js patterns
        if re.search(r'forceSimulation|forceManyBody|forceLink', content):
            types.append("d3-force")
        if re.search(r'd3\.hierarchy|d3\.tree|d3\.cluster', content):
            types.append("d3-tree")
        if re.search(r'd3\.arc|d3\.pie', content):
            types.append("d3-pie")
        if re.search(r'\.selectAll.*enter\(\)', content):
            types.append("d3-data-join")
            
        # Mermaid patterns
        if re.search(r'flowchart|graph\s+(TB|BT|LR|RL)', content, re.IGNORECASE):
            types.append("mermaid-flowchart")
        if re.search(r'sequenceDiagram', content, re.IGNORECASE):
            types.append("mermaid-sequence")
        if re.search(r'classDiagram', content, re.IGNORECASE):
            types.append("mermaid-class")
        if re.search(r'stateDiagram', content, re.IGNORECASE):
            types.append("mermaid-state")
            
        return types if types else ["unknown"]
    
    def get_source_changes_since(self, since_date: datetime) -> List[Dict[str, Any]]:
        """Get source file changes since a given date using git."""
        changes = []
        
        # Check if git is available
        if not git_available():
            print("Warning: Git not available, skipping source change detection")
            return changes
        
        try:
            # Format date for git
            date_str = since_date.strftime("%Y-%m-%d")
            
            # Get changed files from git (with timeout to prevent hanging)
            result = subprocess.run(
                ["git", "log", f"--since={date_str}", "--name-only", "--pretty=format:"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            if result.returncode == 0:
                files = set(f.strip() for f in result.stdout.splitlines() if f.strip())
                
                for source_path in self.SOURCE_PATHS:
                    matching = [f for f in files if f.startswith(source_path)]
                    if matching:
                        changes.extend([{"path": f, "source_area": source_path} for f in matching])
                        
        except Exception as e:
            print(f"Warning: Could not get git history: {e}")
            
        return changes
    
    def check_staleness(self) -> List[Dict[str, Any]]:
        """Check all diagrams for staleness."""
        diagrams = self.find_diagrams()
        stale_diagrams = []
        
        print(f"🔍 Checking {len(diagrams)} diagram files...")
        
        for diagram in diagrams:
            # Check age
            is_old = diagram["age_days"] > self.max_age_days
            
            # Check for related source changes
            source_changes = []
            if is_old:
                source_changes = self.get_source_changes_since(diagram["modified"])
            
            is_stale = is_old and len(source_changes) > 0
            
            diagram_result = {
                **diagram,
                "modified": diagram["modified"].isoformat(),
                "is_stale": is_stale,
                "staleness_reason": None,
                "related_changes": len(source_changes) if is_old else 0
            }
            
            if is_stale:
                diagram_result["staleness_reason"] = f"Diagram is {diagram['age_days']} days old with {len(source_changes)} source changes"
                stale_diagrams.append(diagram_result)
            
            self.diagram_manifest.append(diagram_result)
        
        return stale_diagrams
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate staleness report."""
        stale = self.check_staleness()
        
        report = {
            "version": "1.0",
            "generated": datetime.now().isoformat(),
            "generator": "diagram_staleness.py",
            "settings": {
                "max_age_days": self.max_age_days,
                "source_paths_monitored": self.SOURCE_PATHS,
                "git_available": git_available()
            },
            "summary": {
                "total_diagrams": len(self.diagram_manifest),
                "stale_diagrams": len(stale),
                "d3_diagrams": len([d for d in self.diagram_manifest if d["has_d3"]]),
                "mermaid_diagrams": len([d for d in self.diagram_manifest if d["has_mermaid"]]),
                "healthy_diagrams": len([d for d in self.diagram_manifest if not d["is_stale"]])
            },
            "stale_diagrams": stale,
            "all_diagrams": self.diagram_manifest
        }
        
        # Add checksum
        content_for_hash = json.dumps(report, sort_keys=True, default=str)
        report["_checksum"] = hashlib.sha256(content_for_hash.encode()).hexdigest()[:16]
        
        return report
    
    def save_manifest(self, output_path: Path, report: Dict[str, Any]) -> None:
        """Save diagram manifest to JSON with atomic write."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Atomic write using temp file
        fd, temp_path = tempfile.mkstemp(suffix='.json', dir=output_path.parent)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
            shutil.move(temp_path, output_path)
        except Exception:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise
        
        print(f"\n✅ Diagram manifest saved to: {output_path}")
    
    def print_report(self, report: Dict[str, Any]) -> None:
        """Print human-readable report."""
        summary = report["summary"]
        
        print("\n" + "="*60)
        print("📊 DIAGRAM STALENESS REPORT")
        print("="*60)
        print(f"\n📈 Summary:")
        print(f"   Total diagrams found:  {summary['total_diagrams']}")
        print(f"   D3.js diagrams:        {summary['d3_diagrams']}")
        print(f"   Mermaid diagrams:      {summary['mermaid_diagrams']}")
        print(f"   Healthy diagrams:      {summary['healthy_diagrams']} ✅")
        print(f"   Stale diagrams:        {summary['stale_diagrams']} ⚠️")
        
        if report["stale_diagrams"]:
            print(f"\n⚠️  STALE DIAGRAMS (need update):")
            print("-"*60)
            for diagram in report["stale_diagrams"]:
                print(f"\n   📄 {diagram['path']}")
                print(f"      Types: {', '.join(diagram['diagram_types'])}")
                print(f"      Age: {diagram['age_days']} days")
                print(f"      Reason: {diagram['staleness_reason']}")
        else:
            print(f"\n✅ All diagrams are up to date!")
        
        print("\n" + "="*60)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CORTEX Diagram Staleness Checker")
    parser.add_argument("--max-age", "-a", type=int, default=30,
                       help="Maximum diagram age in days before flagging (default: 30)")
    parser.add_argument("--output", "-o",
                       default="cortex-brain/documents/diagram-manifest.json",
                       help="Output manifest file path")
    parser.add_argument("--project-root", "-p", default=None,
                       help="Project root directory (default: auto-detect)")
    parser.add_argument("--quiet", "-q", action="store_true",
                       help="Only output JSON, no console report")
    
    args = parser.parse_args()
    
    # Auto-detect project root
    if args.project_root:
        project_root = Path(args.project_root)
    else:
        script_path = Path(__file__).resolve()
        project_root = script_path.parent.parent.parent
        
        if not (project_root / "cortex-brain").exists():
            print("Error: Could not find project root. Use --project-root option.")
            sys.exit(1)
    
    if not args.quiet:
        print(f"🔍 CORTEX Diagram Staleness Checker")
        print(f"   Project root: {project_root}")
        print(f"   Max age: {args.max_age} days")
    
    checker = DiagramStalenessChecker(project_root, max_age_days=args.max_age)
    report = checker.generate_report()
    
    output_path = project_root / args.output
    checker.save_manifest(output_path, report)
    
    if not args.quiet:
        checker.print_report(report)
    
    # Exit with code 1 if stale diagrams found
    if report["summary"]["stale_diagrams"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
