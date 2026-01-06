#!/usr/bin/env python3
"""
Git Commit Intelligence Analyzer for CORTEX Upgrade System
Extracts architectural changes, governance rules, and documentation intelligence from git history.

Author: Asif Hussain
Version: 1.0.0
Date: January 6, 2026
"""

import json
import re
import subprocess
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional


@dataclass
class CommitEnhancement:
    """Structured enhancement data from a commit."""
    commit_hash: str
    author: str
    date: str
    title: str
    body: str
    category: str  # architectural, governance, documentation, orchestrator, audit_logging
    subsystems: List[str]  # List of affected subsystems
    governance_rules: List[Dict]  # New/modified governance rules
    architectural_changes: List[Dict]  # Architectural changes to wire
    documentation_intelligence: List[Dict]  # Documentation modifications
    files_changed: List[str]  # List of modified files


class GitCommitAnalyzer:
    """Analyzes git commits to extract enhancement intelligence."""

    # Category detection patterns
    CATEGORY_PATTERNS = {
        "architectural": [
            r"architecture", r"architectural", r"arch:", r"BaseOrchestrator",
            r"routing", r"entry point", r"master orchestrator", r"infrastructure"
        ],
        "governance": [
            r"governance", r"brain protection", r"SKULL", r"brain-protection-rules",
            r"compliance", r"validation", r"enforcement"
        ],
        "documentation": [
            r"docs:", r"documentation", r"glassmorphism", r"Level 1", r"Level 2",
            r"HTML", r"CSS", r"validators", r"template"
        ],
        "orchestrator": [
            r"orchestrator", r"upgrade", r"vacuum", r"cleanup", r"investigation",
            r"planning", r"ado", r"tdd", r"refinement", r"maintenance"
        ],
        "audit_logging": [
            r"audit", r"logging", r"AuditLogger", r"event types", r"metrics"
        ]
    }

    # Subsystem patterns
    SUBSYSTEM_PATTERNS = {
        "src/orchestrators/": "orchestrators",
        ".github/prompts/": "prompts",
        "cortex-brain/documents/": "documentation",
        "src/logging/": "audit_logging",
        "cortex-brain/config/": "configuration",
        "cortex-brain/tier0/": "governance",
        "docs/": "html_views",
        "tests/": "testing",
        "src/core/": "core_architecture",
        "cortex-brain/manifests/": "manifests"
    }

    # Governance rule patterns
    GOVERNANCE_PATTERNS = {
        "PYTHON_ONLY_GENERATION": r"PYTHON[_\s]*ONLY[_\s]*GENERATION",
        "CSS_REGISTRY_ENFORCEMENT": r"CSS[_\s]*REGISTRY[_\s]*ENFORCEMENT",
        "INLINE_STYLE_PROHIBITION": r"INLINE[_\s]*STYLE[_\s]*PROHIBITION",
        "GIT_CHECKPOINT_REQUIRED": r"GIT[_\s]*CHECKPOINT[_\s]*REQUIRED",
        "STATE_PERSISTENCE": r"STATE[_\s]*PERSISTENCE",
        "TDD_ENFORCEMENT": r"TDD[_\s]*ENFORCEMENT",
        "HOLISTIC_DISCOVERY": r"HOLISTIC[_\s]*DISCOVERY",
        "REFACTOR_CLEANUP": r"REFACTOR[_\s]*CLEANUP",
        "GIT_ISOLATION": r"GIT[_\s]*ISOLATION",
        "PLANNING_ISOLATION": r"PLANNING[_\s]*ISOLATION",
        "HAND_OFF_PROTOCOL": r"HAND[_\s]*OFF[_\s]*PROTOCOL"
    }

    def __init__(self, repo_path: Path = Path.cwd()):
        self.repo_path = repo_path

    def get_commits(self, branch: str = "CORTEX-5.0", limit: int = 100) -> List[Dict]:
        """Fetch git commits with full details."""
        try:
            cmd = [
                "git", "log", branch,
                "--pretty=format:%H|||%an|||%ad|||%s|||%b",
                "--date=short",
                f"-{limit}"
            ]
            result = subprocess.run(
                cmd, cwd=self.repo_path, capture_output=True, text=True, check=True,
                encoding="utf-8", errors="replace"
            )
            
            commits = []
            for line in result.stdout.strip().split("\n"):
                if not line.strip():
                    continue
                parts = line.split("|||")
                if len(parts) >= 5:
                    commits.append({
                        "hash": parts[0],
                        "author": parts[1],
                        "date": parts[2],
                        "title": parts[3],
                        "body": parts[4] if len(parts) > 4 else ""
                    })
            return commits
        except subprocess.CalledProcessError as e:
            print(f"Error fetching commits: {e}")
            return []

    def get_commit_files(self, commit_hash: str) -> List[str]:
        """Get list of files changed in a commit."""
        try:
            cmd = ["git", "show", "--name-only", "--pretty=format:", commit_hash]
            result = subprocess.run(
                cmd, cwd=self.repo_path, capture_output=True, text=True, check=True,
                encoding="utf-8", errors="replace"
            )
            return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
        except subprocess.CalledProcessError:
            return []

    def categorize_commit(self, title: str, body: str) -> str:
        """Categorize commit based on title and body."""
        text = f"{title} {body}".lower()
        
        scores = defaultdict(int)
        for category, patterns in self.CATEGORY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    scores[category] += 1
        
        if not scores:
            return "general"
        
        return max(scores, key=scores.get)

    def identify_subsystems(self, files: List[str]) -> List[str]:
        """Identify affected subsystems from file paths."""
        subsystems = set()
        for file in files:
            for path_pattern, subsystem in self.SUBSYSTEM_PATTERNS.items():
                if file.startswith(path_pattern):
                    subsystems.add(subsystem)
                    break
        return sorted(list(subsystems))

    def extract_governance_rules(self, title: str, body: str) -> List[Dict]:
        """Extract governance rules mentioned in commit."""
        text = f"{title}\n{body}"
        rules = []
        
        for rule_name, pattern in self.GOVERNANCE_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                # Extract context around the rule
                lines = text.split("\n")
                context = []
                for i, line in enumerate(lines):
                    if re.search(pattern, line, re.IGNORECASE):
                        # Get 2 lines before and after
                        start = max(0, i - 2)
                        end = min(len(lines), i + 3)
                        context = lines[start:end]
                        break
                
                rules.append({
                    "rule_name": rule_name,
                    "context": "\n".join(context),
                    "priority": self._get_rule_priority(text, rule_name)
                })
        
        return rules

    def _get_rule_priority(self, text: str, rule_name: str) -> str:
        """Extract priority level for a governance rule."""
        priorities = {
            "CRITICAL": ["critical", "zero tolerance", "block"],
            "HIGH": ["high priority", "mandatory", "required"],
            "MEDIUM": ["medium", "recommended", "should"],
            "LOW": ["low", "optional", "consider"]
        }
        
        # Find text around rule name
        pattern = f"{rule_name}.{{0,200}}"
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            return "MEDIUM"
        
        snippet = match.group(0).lower()
        for priority, keywords in priorities.items():
            if any(kw in snippet for kw in keywords):
                return priority
        
        return "MEDIUM"

    def extract_architectural_changes(self, title: str, body: str, files: List[str]) -> List[Dict]:
        """Extract architectural changes that need wiring."""
        changes = []
        
        # Pattern 1: New orchestrator
        if any(f.startswith("src/orchestrators/") and f.endswith("_orchestrator.py") for f in files):
            orchestrator_files = [f for f in files if f.startswith("src/orchestrators/") and f.endswith("_orchestrator.py")]
            for orch_file in orchestrator_files:
                name = Path(orch_file).stem.replace("_orchestrator", "")
                changes.append({
                    "type": "new_orchestrator",
                    "name": name,
                    "file": orch_file,
                    "action": "register_in_master_orchestrator",
                    "manifest": f"cortex-brain/manifests/orchestrators/{name}.yaml"
                })
        
        # Pattern 2: Manifest changes
        if any(f.startswith("cortex-brain/manifests/orchestrators/") for f in files):
            manifest_files = [f for f in files if f.startswith("cortex-brain/manifests/orchestrators/")]
            for manifest in manifest_files:
                changes.append({
                    "type": "orchestrator_manifest_update",
                    "file": manifest,
                    "action": "validate_and_reload_routing"
                })
        
        # Pattern 3: Master orchestrator config
        if "cortex-brain/config/master-orchestrator.yaml" in files:
            changes.append({
                "type": "master_orchestrator_update",
                "file": "cortex-brain/config/master-orchestrator.yaml",
                "action": "reload_routing_table"
            })
        
        # Pattern 4: Audit logger changes
        if any(f.startswith("src/logging/") or "audit" in f.lower() for f in files):
            changes.append({
                "type": "audit_logger_update",
                "action": "verify_event_types_and_metrics",
                "files": [f for f in files if "audit" in f.lower() or f.startswith("src/logging/")]
            })
        
        # Pattern 5: BaseOrchestrator changes
        if any("base_orchestrator" in f.lower() for f in files):
            changes.append({
                "type": "base_orchestrator_update",
                "action": "validate_all_orchestrator_inheritance",
                "critical": True
            })
        
        return changes

    def extract_documentation_intelligence(self, title: str, body: str, files: List[str]) -> List[Dict]:
        """Extract documentation modification patterns."""
        intelligence = []
        
        # Pattern 1: Glassmorphism changes
        if re.search(r"glassmorphism|glass.*morphism", f"{title} {body}", re.IGNORECASE):
            intelligence.append({
                "type": "glassmorphism_pattern",
                "description": "Glassmorphism theme updates detected",
                "action": "update_css_registry",
                "affected_files": [f for f in files if f.endswith(".css") or f.endswith(".html")]
            })
        
        # Pattern 2: Validator changes
        if re.search(r"validator|validation", f"{title} {body}", re.IGNORECASE):
            validators = []
            # Extract validator names
            validator_pattern = r"(\w+Validator)"
            validators = re.findall(validator_pattern, body)
            intelligence.append({
                "type": "validator_update",
                "validators": list(set(validators)),
                "action": "register_validators_in_documentation_orchestrator"
            })
        
        # Pattern 3: Level 1/Level 2 view changes
        if re.search(r"Level [12]|L[12] view", f"{title} {body}", re.IGNORECASE):
            level = "1" if "Level 1" in body or "L1" in body else "2"
            intelligence.append({
                "type": f"level_{level}_view_update",
                "description": f"Level {level} HTML view modifications",
                "action": "run_template_compliance_validator",
                "affected_files": [f for f in files if f.startswith("docs/") and f.endswith(".html")]
            })
        
        # Pattern 4: Uniqueness enforcement
        if re.search(r"uniqueness|overlap|differentiation", f"{title} {body}", re.IGNORECASE):
            intelligence.append({
                "type": "uniqueness_enforcement",
                "description": "Content uniqueness requirements",
                "action": "run_uniqueness_validator",
                "threshold": self._extract_threshold(body)
            })
        
        # Pattern 5: Diagram requirements
        if re.search(r"diagram|mermaid|d3\.js|visualization", f"{title} {body}", re.IGNORECASE):
            count = self._extract_diagram_count(body)
            intelligence.append({
                "type": "diagram_requirement",
                "count": count,
                "action": "generate_architectural_diagrams",
                "tools": ["mermaid", "d3.js"]
            })
        
        return intelligence

    def _extract_threshold(self, text: str) -> float:
        """Extract overlap threshold percentage."""
        match = re.search(r"<(\d+)%|(\d+)%\s*overlap", text, re.IGNORECASE)
        if match:
            return float(match.group(1) or match.group(2)) / 100
        return 0.3  # Default 30%

    def _extract_diagram_count(self, text: str) -> int:
        """Extract required diagram count."""
        match = re.search(r"(\d+)\+?\s*diagrams?", text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 9  # Default minimum

    def analyze_commit(self, commit: Dict) -> CommitEnhancement:
        """Analyze a single commit and extract enhancement intelligence."""
        files = self.get_commit_files(commit["hash"])
        category = self.categorize_commit(commit["title"], commit["body"])
        subsystems = self.identify_subsystems(files)
        governance_rules = self.extract_governance_rules(commit["title"], commit["body"])
        architectural_changes = self.extract_architectural_changes(commit["title"], commit["body"], files)
        documentation_intelligence = self.extract_documentation_intelligence(commit["title"], commit["body"], files)
        
        return CommitEnhancement(
            commit_hash=commit["hash"],
            author=commit["author"],
            date=commit["date"],
            title=commit["title"],
            body=commit["body"],
            category=category,
            subsystems=subsystems,
            governance_rules=governance_rules,
            architectural_changes=architectural_changes,
            documentation_intelligence=documentation_intelligence,
            files_changed=files
        )

    def analyze_commits(self, branch: str = "CORTEX-5.0", limit: int = 100) -> List[CommitEnhancement]:
        """Analyze multiple commits and return enhancement intelligence."""
        commits = self.get_commits(branch, limit)
        enhancements = []
        
        for commit in commits:
            enhancement = self.analyze_commit(commit)
            enhancements.append(enhancement)
        
        return enhancements

    def generate_report(self, enhancements: List[CommitEnhancement], output_path: Path):
        """Generate comprehensive analysis report."""
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_commits": len(enhancements),
            "summary": self._generate_summary(enhancements),
            "enhancements": [asdict(e) for e in enhancements]
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Analysis report generated: {output_path}")

    def _generate_summary(self, enhancements: List[CommitEnhancement]) -> Dict:
        """Generate summary statistics."""
        categories = defaultdict(int)
        subsystems = defaultdict(int)
        governance_rules_count = 0
        architectural_changes_count = 0
        documentation_intelligence_count = 0
        
        for e in enhancements:
            categories[e.category] += 1
            for subsystem in e.subsystems:
                subsystems[subsystem] += 1
            governance_rules_count += len(e.governance_rules)
            architectural_changes_count += len(e.architectural_changes)
            documentation_intelligence_count += len(e.documentation_intelligence)
        
        return {
            "categories": dict(categories),
            "subsystems": dict(subsystems),
            "governance_rules_extracted": governance_rules_count,
            "architectural_changes_extracted": architectural_changes_count,
            "documentation_intelligence_extracted": documentation_intelligence_count
        }


def main():
    """Main entry point."""
    import sys
    
    # Fix Windows console encoding for emojis
    if sys.platform == "win32":
        import codecs
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, errors="replace")
    
    analyzer = GitCommitAnalyzer()
    
    print("Analyzing git commits...")
    enhancements = analyzer.analyze_commits(limit=100)
    
    print(f"Analyzed {len(enhancements)} commits")
    
    # Generate report
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_path = Path(f"cortex-brain/documents/upgrades/{timestamp}/commit-analysis.json")
    analyzer.generate_report(enhancements, output_path)
    
    # Print summary
    summary = analyzer._generate_summary(enhancements)
    print("\nSummary:")
    print(f"  Categories: {summary['categories']}")
    print(f"  Subsystems: {summary['subsystems']}")
    print(f"  Governance Rules: {summary['governance_rules_extracted']}")
    print(f"  Architectural Changes: {summary['architectural_changes_extracted']}")
    print(f"  Documentation Intelligence: {summary['documentation_intelligence_extracted']}")


if __name__ == "__main__":
    main()
