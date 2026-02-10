"""
User Response Template for Pull Enhancement Notifications

This template shows users what features were enhanced/added after a git pull,
without requiring a full audit cycle.

Authority: cortex-architect.prompt.md environment setup capabilities
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import yaml
import git
from datetime import datetime


@dataclass
class EnhancementSummary:
    """Summary of enhancements from git pull."""
    category: str  # "Prompts", "Agents", "Orchestrators", "Tools", "Rules"
    count: int
    items: List[str]
    impact: str  # "High", "Medium", "Low"
    description: str


@dataclass
class PullEnhancementReport:
    """Complete pull enhancement report."""
    commits_merged: int
    enhancements: List[EnhancementSummary]
    new_capabilities: List[str]
    deprecated_features: List[str] 
    breaking_changes: List[str]
    total_impact_score: float  # 0-1.0


class PullEnhancementTemplateGenerator:
    """Generates user-facing templates showing what changed after git pull."""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.repo = git.Repo(repo_path)
    
    def analyze_pull_changes(
        self,
        before_commit: str,
        after_commit: str = "HEAD"
    ) -> PullEnhancementReport:
        """
        Analyze changes between two commits to identify enhancements.
        
        Args:
            before_commit: Git commit hash before pull
            after_commit: Git commit hash after pull (default: HEAD)
        
        Returns:
            PullEnhancementReport with categorized changes
        """
        # Get changed files between commits
        changed_files = list(self.repo.iter_commits(
            f"{before_commit}..{after_commit}", 
            paths=None
        ))
        
        enhancements = []
        new_capabilities = []
        deprecated_features = []
        breaking_changes = []
        
        # Analyze prompt changes
        prompt_changes = self._analyze_prompt_changes(before_commit, after_commit)
        if prompt_changes["count"] > 0:
            enhancements.append(EnhancementSummary(
                category="Prompts",
                count=prompt_changes["count"],
                items=prompt_changes["items"],
                impact=prompt_changes["impact"],
                description=f"Updated prompts with new capabilities and modes"
            ))
        
        # Analyze agent changes  
        agent_changes = self._analyze_agent_changes(before_commit, after_commit)
        if agent_changes["count"] > 0:
            enhancements.append(EnhancementSummary(
                category="Agents",
                count=agent_changes["count"], 
                items=agent_changes["items"],
                impact=agent_changes["impact"],
                description=f"New orchestration agents for improved workflows"
            ))
        
        # Analyze MCP tool changes
        tool_changes = self._analyze_mcp_tool_changes(before_commit, after_commit)
        if tool_changes["count"] > 0:
            enhancements.append(EnhancementSummary(
                category="MCP Tools",
                count=tool_changes["count"],
                items=tool_changes["items"], 
                impact="High",  # MCP tools always high impact
                description=f"New MCP tools for enhanced functionality"
            ))
            
        # Calculate total impact score
        impact_score = self._calculate_impact_score(enhancements)
        
        return PullEnhancementReport(
            commits_merged=len(changed_files),
            enhancements=enhancements,
            new_capabilities=new_capabilities,
            deprecated_features=deprecated_features,
            breaking_changes=breaking_changes,
            total_impact_score=impact_score
        )
    
    def _analyze_prompt_changes(self, before: str, after: str) -> Dict[str, Any]:
        """Analyze changes to .github/prompts/ files."""
        prompt_files = [
            ".github/prompts/cortex-architect.prompt.md",
            ".github/prompts/CORTEX.prompt.md", 
            ".github/prompts/response-format-standards.md"
        ]
        
        changed_prompts = []
        impact = "Low"
        
        for prompt_file in prompt_files:
            if self._file_changed_between_commits(prompt_file, before, after):
                changes = self._extract_prompt_changes(prompt_file, before, after)
                if changes:
                    changed_prompts.extend(changes)
                    if any("mode" in c.lower() or "mcp" in c.lower() for c in changes):
                        impact = "High"
                    elif len(changes) > 3:
                        impact = "Medium"
        
        return {
            "count": len(changed_prompts),
            "items": changed_prompts[:5],  # Limit to top 5
            "impact": impact
        }
    
    def _analyze_agent_changes(self, before: str, after: str) -> Dict[str, Any]:
        """Analyze changes to .github/agents/core/ files."""
        agents_dir = Path(".github/agents/core")
        
        if not agents_dir.exists():
            return {"count": 0, "items": [], "impact": "Low"}
        
        changed_agents = []
        new_agents = []
        
        for agent_file in agents_dir.glob("*.md"):
            if self._file_changed_between_commits(str(agent_file), before, after):
                agent_name = agent_file.stem.replace("cortex-", "").replace("-", " ").title()
                changed_agents.append(agent_name)
            elif self._is_new_file(str(agent_file), before):
                new_agents.append(agent_name) 
        
        all_changes = changed_agents + [f"NEW: {a}" for a in new_agents]
        impact = "High" if new_agents else ("Medium" if len(changed_agents) > 2 else "Low")
        
        return {
            "count": len(all_changes),
            "items": all_changes[:5],
            "impact": impact
        }
    
    def _analyze_mcp_tool_changes(self, before: str, after: str) -> Dict[str, Any]:
        """Analyze changes to MCP tools in cortex/mcp/."""
        mcp_files = [
            "cortex/mcp/server.py",
            "cortex/mcp/cortex_tools.py", 
            "cortex/mcp/tools/"
        ]
        
        new_tools = []
        updated_tools = []
        
        # Check for new tool files
        tools_dir = Path("cortex/mcp/tools")
        if tools_dir.exists():
            for tool_file in tools_dir.glob("*.py"):
                if tool_file.name == "__init__.py":
                    continue
                if self._is_new_file(str(tool_file), before):
                    tool_name = tool_file.stem.replace("_", " ").title()
                    new_tools.append(f"NEW: cortex_{tool_file.stem}")
        
        # Check for updates to existing tools
        for mcp_file in mcp_files[:2]:  # Skip directory in this loop
            if self._file_changed_between_commits(mcp_file, before, after):
                updated_tools.append(Path(mcp_file).name)
        
        all_changes = new_tools + updated_tools
        
        return {
            "count": len(all_changes), 
            "items": all_changes,
            "impact": "High" if new_tools else "Medium"
        }
    
    def _file_changed_between_commits(
        self, 
        file_path: str, 
        before: str, 
        after: str
    ) -> bool:
        """Check if file was modified between two commits."""
        try:
            # Get file content at both commits
            before_content = self.repo.git.show(f"{before}:{file_path}")
            after_content = self.repo.git.show(f"{after}:{file_path}")
            return before_content != after_content
        except Exception:
            return False
    
    def _is_new_file(self, file_path: str, before_commit: str) -> bool:
        """Check if file is new (didn't exist in before_commit)."""
        try:
            self.repo.git.show(f"{before_commit}:{file_path}")
            return False  # File existed
        except Exception:
            return True  # File didn't exist
    
    def _extract_prompt_changes(
        self, 
        prompt_file: str, 
        before: str, 
        after: str
    ) -> List[str]:
        """Extract meaningful changes from prompt file."""
        try:
            before_content = self.repo.git.show(f"{before}:{prompt_file}")
            after_content = self.repo.git.show(f"{after}:{prompt_file}")
            
            # Simple heuristic: look for new section headers
            before_headers = [
                line.strip() for line in before_content.split('\n') 
                if line.startswith('#') and len(line.strip()) > 3
            ]
            after_headers = [
                line.strip() for line in after_content.split('\n')
                if line.startswith('#') and len(line.strip()) > 3  
            ]
            
            new_headers = [h for h in after_headers if h not in before_headers]
            return [h.replace('#', '').strip() for h in new_headers[:3]]
            
        except Exception:
            return []
    
    def _calculate_impact_score(self, enhancements: List[EnhancementSummary]) -> float:
        """Calculate overall impact score 0-1.0."""
        if not enhancements:
            return 0.0
        
        impact_weights = {"High": 1.0, "Medium": 0.6, "Low": 0.3}
        category_weights = {
            "MCP Tools": 0.4,  # Highest impact
            "Agents": 0.3,
            "Prompts": 0.2,
            "Orchestrators": 0.3,
            "Rules": 0.1
        }
        
        total_weighted_impact = 0.0
        total_weight = 0.0
        
        for enhancement in enhancements:
            impact_score = impact_weights.get(enhancement.impact, 0.3)
            category_weight = category_weights.get(enhancement.category, 0.2)
            weighted_impact = impact_score * category_weight * enhancement.count
            
            total_weighted_impact += weighted_impact
            total_weight += category_weight
        
        return min(total_weighted_impact / max(total_weight, 1.0), 1.0)
    
    def generate_user_template(self, report: PullEnhancementReport) -> str:
        """Generate markdown template for user notification."""
        if not report.enhancements:
            return self._generate_no_changes_template(report)
        
        return self._generate_enhancements_template(report)
    
    def _generate_enhancements_template(self, report: PullEnhancementReport) -> str:
        """Generate template when enhancements are present."""
        impact_emoji = "🔴" if report.total_impact_score >= 0.7 else (
            "🟡" if report.total_impact_score >= 0.4 else "🔵"
        )
        
        template = f"""## 🆙 CORTEX Enhanced via Pull
**Commits:** {report.commits_merged} merged | **Impact:** {impact_emoji} {report.total_impact_score:.1%}

---

### 🎯 What's New

| Category | Changes | Impact | New Capabilities |
|----------|---------|--------|------------------|"""
        
        for enhancement in report.enhancements:
            impact_icon = {"High": "🔴", "Medium": "🟡", "Low": "🔵"}[enhancement.impact]
            items_str = ", ".join(enhancement.items[:3])
            if len(enhancement.items) > 3:
                items_str += f" (+{len(enhancement.items)-3} more)"
            
            template += f"""
| **{enhancement.category}** | {enhancement.count} updated | {impact_icon} {enhancement.impact} | {items_str} |"""
        
        if report.new_capabilities:
            template += f"""

### ✨ New Capabilities
{self._format_list(report.new_capabilities)}"""
        
        if report.breaking_changes:
            template += f"""

### ⚠️ Breaking Changes
{self._format_list(report.breaking_changes)}"""
        
        template += f"""

### 🚀 How to Explore

**Quick Commands:**
- `/list cortex capabilities` — View all CORTEX capabilities
- `/query what's new in [category]` — Deep dive into specific enhancements  
- `/plan` — See updated phase priorities with new features
- `/audit` — Validate everything is properly wired

**Impact Summary:**
- **High Impact** ({len([e for e in report.enhancements if e.impact == 'High'])} categories): New functionality ready to use
- **Medium Impact** ({len([e for e in report.enhancements if e.impact == 'Medium'])} categories): Enhanced existing features
- **Low Impact** ({len([e for e in report.enhancements if e.impact == 'Low'])} categories): Minor improvements

**Next Steps:**
1. **Try new features** — Use quick commands above to explore
2. **Check compatibility** — Run `/check-env` to verify setup
3. **Update workflows** — New capabilities may improve your existing processes

**Your local work:** Preserved ✅ | **Ecosystem:** Up-to-date ✅
"""
        return template
    
    def _generate_no_changes_template(self, report: PullEnhancementReport) -> str:
        """Generate template when no significant changes."""
        return f"""## ✅ CORTEX Up-to-Date
**Status:** No new enhancements | **Commits:** {report.commits_merged} merged

Your CORTEX environment is current with the latest ecosystem.
All capabilities remain the same as your last session.

**Ready to proceed with your work.**
"""
    
    def _format_list(self, items: List[str]) -> str:
        """Format list of items as markdown."""
        return "\n".join(f"- {item}" for item in items)


# Usage example
def generate_pull_enhancement_template(
    before_commit: str,
    after_commit: str = "HEAD",
    repo_path: str = "."
) -> str:
    """
    Generate user-facing template after git pull.
    
    Args:
        before_commit: Git commit hash before pull
        after_commit: Git commit hash after pull  
        repo_path: Path to CORTEX repository
    
    Returns:
        Markdown template for user notification
    """
    generator = PullEnhancementTemplateGenerator(repo_path)
    report = generator.analyze_pull_changes(before_commit, after_commit)
    return generator.generate_user_template(report)


if __name__ == "__main__":
    # Example usage - would be called by environment setup agent
    template = generate_pull_enhancement_template(
        before_commit="HEAD~5",  # 5 commits ago
        after_commit="HEAD"
    )
    print(template)