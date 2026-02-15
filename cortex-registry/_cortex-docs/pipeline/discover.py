#!/usr/bin/env python3
"""
CORTEX Documentation Discovery Pipeline

Scans CORTEX codebase to extract:
- Orchestrators (from cortex/orchestrators/)
- MCP Tools (from cortex/mcp/)
- Git timeline (30-day commit clustering)
- Architecture metrics (counts, relationships)

Output: discovery/baseline.yaml
"""

import os
import subprocess
import yaml
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timedelta
import re


class DiscoveryPipeline:
    """Discovers CORTEX components for documentation generation."""
    
    def __init__(self, cortex_root: Path):
        self.cortex_root = cortex_root
        self.baseline = {
            "discovered_at": datetime.now().isoformat(),
            "orchestrators": [],
            "mcp_tools": [],
            "git_timeline": [],
            "metrics": {}
        }
    
    def run(self) -> Dict[str, Any]:
        """Execute full discovery pipeline."""
        print("🔍 Starting CORTEX discovery pipeline...")
        
        self.discover_orchestrators()
        self.discover_mcp_tools()
        self.analyze_git_timeline()
        self.compute_metrics()
        
        print(f"✅ Discovery complete: {len(self.baseline['orchestrators'])} orchestrators, "
              f"{len(self.baseline['mcp_tools'])} MCP tools")
        
        return self.baseline
    
    def discover_orchestrators(self) -> None:
        """Scan cortex/orchestrators/ for orchestrator classes."""
        print("  Scanning orchestrators...")
        
        orchestrators_dir = self.cortex_root / "cortex" / "orchestrators"
        if not orchestrators_dir.exists():
            print(f"  ⚠️  Orchestrators directory not found: {orchestrators_dir}")
            return
        
        for py_file in orchestrators_dir.rglob("*.py"):
            if py_file.name.startswith("_"):
                continue
            
            content = py_file.read_text(encoding="utf-8")
            
            # Find class definitions that look like orchestrators
            class_pattern = r'class\s+(\w+Orchestrator)\s*\([^)]*\):'
            matches = re.finditer(class_pattern, content)
            
            for match in matches:
                orchestrator_name = match.group(1)
                
                # Extract docstring if present
                docstring = self._extract_docstring(content, match.end())
                
                self.baseline["orchestrators"].append({
                    "name": orchestrator_name,
                    "file": str(py_file.relative_to(self.cortex_root)),
                    "description": docstring or f"{orchestrator_name} workflow coordinator",
                    "category": self._categorize_orchestrator(orchestrator_name)
                })
        
        # Sort by name
        self.baseline["orchestrators"].sort(key=lambda x: x["name"])
    
    def discover_mcp_tools(self) -> None:
        """Scan cortex/mcp/ for MCP tool definitions."""
        print("  Scanning MCP tools...")
        
        mcp_dir = self.cortex_root / "cortex" / "mcp"
        if not mcp_dir.exists():
            print(f"  ⚠️  MCP directory not found: {mcp_dir}")
            return
        
        for py_file in mcp_dir.rglob("*.py"):
            if py_file.name.startswith("_"):
                continue
            
            content = py_file.read_text(encoding="utf-8")
            
            # Find @mcp_tool decorated functions
            tool_pattern = r'@mcp[_.]tool\s*(?:\([^)]*\))?\s*\n\s*(?:async\s+)?def\s+(\w+)\s*\('
            matches = re.finditer(tool_pattern, content)
            
            for match in matches:
                tool_name = match.group(1)
                
                # Extract docstring
                docstring = self._extract_docstring(content, match.end())
                
                # Extract intent if mentioned in docstring
                intent = self._extract_intent(docstring)
                
                self.baseline["mcp_tools"].append({
                    "name": tool_name,
                    "file": str(py_file.relative_to(self.cortex_root)),
                    "description": docstring or f"{tool_name} MCP tool",
                    "intent": intent
                })
        
        # Sort by name
        self.baseline["mcp_tools"].sort(key=lambda x: x["name"])
    
    def analyze_git_timeline(self) -> None:
        """Extract 30-day git history with commit clustering."""
        print("  Analyzing git timeline...")
        
        try:
            # Get commits from last 30 days
            since_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            
            result = subprocess.run(
                ["git", "log", f"--since={since_date}", "--oneline", "--no-merges"],
                cwd=self.cortex_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            commits = result.stdout.strip().split("\n")
            if not commits or commits == [""]:
                print("  ⚠️  No git commits found in last 30 days")
                return
            
            # Cluster by phase/feature
            clusters = self._cluster_commits(commits)
            
            self.baseline["git_timeline"] = {
                "period": f"Last 30 days (since {since_date})",
                "total_commits": len(commits),
                "feature_clusters": clusters
            }
            
        except subprocess.CalledProcessError as e:
            print(f"  ⚠️  Git analysis failed: {e}")
    
    def compute_metrics(self) -> None:
        """Compute architecture metrics."""
        print("  Computing metrics...")
        
        self.baseline["metrics"] = {
            "orchestrator_count": len(self.baseline["orchestrators"]),
            "mcp_tool_count": len(self.baseline["mcp_tools"]),
            "core_orchestrators": len([o for o in self.baseline["orchestrators"] 
                                       if o["category"] == "core"]),
            "domain_orchestrators": len([o for o in self.baseline["orchestrators"] 
                                         if o["category"] == "domain"]),
            "support_orchestrators": len([o for o in self.baseline["orchestrators"] 
                                          if o["category"] == "support"]),
        }
    
    def _extract_docstring(self, content: str, start_pos: int) -> str:
        """Extract docstring following a class/function definition."""
        # Look for triple-quoted strings after the position
        match = re.search(r'"""(.*?)"""', content[start_pos:start_pos+1000], re.DOTALL)
        if match:
            return match.group(1).strip()
        
        match = re.search(r"'''(.*?)'''", content[start_pos:start_pos+1000], re.DOTALL)
        if match:
            return match.group(1).strip()
        
        return ""
    
    def _categorize_orchestrator(self, name: str) -> str:
        """Categorize orchestrator by name patterns."""
        core = ["Master", "Intent", "Workflow", "Enforcement", "TDD", "LENS", "Interaction"]
        domain = ["Refactoring", "Planning", "Domain", "Conversation", "Documentation", "Challenge"]
        
        for keyword in core:
            if keyword in name:
                return "core"
        
        for keyword in domain:
            if keyword in name:
                return "domain"
        
        return "support"
    
    def _extract_intent(self, docstring: str) -> str:
        """Extract intent from docstring."""
        intent_keywords = ["IMPLEMENT", "FIX", "REFACTOR", "ANALYZE", "AUDIT", "PLAN", "DESIGN"]
        for keyword in intent_keywords:
            if keyword in docstring.upper():
                return keyword
        return "UNKNOWN"
    
    def _cluster_commits(self, commits: List[str]) -> List[Dict[str, Any]]:
        """Cluster commits by phase/feature keywords."""
        clusters = {}
        
        for commit in commits:
            # Extract keywords from commit message
            keywords = self._extract_keywords(commit)
            
            for keyword in keywords:
                if keyword not in clusters:
                    clusters[keyword] = {"keyword": keyword, "commits": []}
                clusters[keyword]["commits"].append(commit)
        
        # Convert to list and sort by commit count
        result = list(clusters.values())
        result.sort(key=lambda x: len(x["commits"]), reverse=True)
        
        return result[:10]  # Top 10 clusters
    
    def _extract_keywords(self, commit: str) -> List[str]:
        """Extract keywords from commit message."""
        # Common patterns: phase XX, feat:, fix:, docs:, etc.
        keywords = []
        
        # Phase pattern
        phase_match = re.search(r'phase[- ]?(\d+)', commit, re.IGNORECASE)
        if phase_match:
            keywords.append(f"Phase {phase_match.group(1)}")
        
        # Conventional commit prefix
        prefix_match = re.search(r'^[a-f0-9]+\s+(feat|fix|docs|refactor|test|chore|perf|style)', commit, re.IGNORECASE)
        if prefix_match:
            keywords.append(prefix_match.group(1).upper())
        
        # Feature keywords
        feature_keywords = ["MCP", "LENS", "orchestrator", "enforcement", "validation", "testing"]
        for keyword in feature_keywords:
            if keyword.lower() in commit.lower():
                keywords.append(keyword.upper())
        
        return keywords if keywords else ["OTHER"]


def main():
    """Main entry point."""
    cortex_root = Path(__file__).parent.parent.parent
    
    pipeline = DiscoveryPipeline(cortex_root)
    baseline = pipeline.run()
    
    # Write baseline YAML
    output_path = cortex_root / "cortex-registry" / "_cortex-docs" / "discovery" / "baseline.yaml"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with output_path.open("w", encoding="utf-8") as f:
        yaml.dump(baseline, f, default_flow_style=False, allow_unicode=True)
    
    print(f"\n✅ Baseline written to: {output_path}")
    print(f"   📊 {baseline['metrics']['orchestrator_count']} orchestrators")
    print(f"   🛠️  {baseline['metrics']['mcp_tool_count']} MCP tools")
    print(f"   📅 {baseline['git_timeline']['total_commits']} commits (30 days)")


if __name__ == "__main__":
    main()
