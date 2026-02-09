"""
AC_START: AC-PROMPT-CLEANUP-001
Description: PromptCoherenceValidator - Detect drift between agent capabilities and prompt documentation.
Author: Asif Hussain
Phase: 56 - LENS/Intelligence Hybrid Architecture + Audit Enhancement
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional
import yaml
import re
from difflib import SequenceMatcher


@dataclass
class CoherenceIssue:
    """Represents a coherence violation between prompts and agents."""
    severity: str  # "CRITICAL" | "WARNING" | "INFO"
    category: str
    file_path: str
    description: str
    evidence: str
    auto_fix: Optional[str] = None


class PromptCoherenceValidator:
    """
    Validates coherence between .github/prompts/ and .github/agents/.
    
    Detects:
    - Version drift (prompt version != agent version)
    - CORE rule inconsistencies
    - Duplicate sections between files
    - MCP enforcement mismatches
    - Deprecated orchestrator references
    - Missing audit checks
    
    Usage:
        validator = PromptCoherenceValidator()
        issues = validator.validate_all()
        for issue in issues:
            print(f"{issue.severity}: {issue.description}")
    """
    
    def __init__(self, workspace_root: Path = None):
        """Initialize validator with CORTEX workspace root."""
        self.workspace_root = workspace_root or Path("d:/PROJECTS/CORTEX")
        self.prompts_dir = self.workspace_root / ".github" / "prompts"
        self.agents_dir = self.workspace_root / ".github" / "agents" / "core"
        self.issues: List[CoherenceIssue] = []
    
    def validate_all(self) -> List[CoherenceIssue]:
        """
        Run all coherence validation checks.
        
        Returns:
            List of CoherenceIssue objects found
        """
        self.issues = []
        
        # Check 1: Version drift
        self._check_version_drift()
        
        # Check 2: CORE rule consistency
        self._check_core_rule_consistency()
        
        # Check 3: MCP enforcement alignment
        self._check_mcp_enforcement()
        
        # Check 4: Deprecated orchestrator references
        self._check_deprecated_orchestrators()
        
        # Check 5: Duplicate sections
        self._check_duplicate_sections()
        
        # Check 6: Audit check completeness
        self._check_audit_check_coverage()
        
        return self.issues
    
    def _check_version_drift(self):
        """Detect version mismatches between prompts and agents."""
        architect_prompt = self.prompts_dir / "cortex-architect.prompt.md"
        auditor_agent = self.agents_dir / "cortex-auditor.md"
        
        if not architect_prompt.exists() or not auditor_agent.exists():
            self.issues.append(CoherenceIssue(
                severity="CRITICAL",
                category="Version Drift",
                file_path=str(architect_prompt),
                description="Missing prompt or agent files",
                evidence=f"architect_prompt.exists={architect_prompt.exists()}, auditor_agent.exists={auditor_agent.exists()}"
            ))
            return
        
        # Extract versions from markdown headers
        prompt_version = self._extract_version(architect_prompt)
        agent_version = self._extract_version(auditor_agent)
        
        if prompt_version != agent_version:
            self.issues.append(CoherenceIssue(
                severity="WARNING",
                category="Version Drift",
                file_path=str(architect_prompt),
                description=f"Version mismatch: Architect prompt v{prompt_version} vs Auditor agent v{agent_version}",
                evidence=f"Prompt header: {prompt_version}, Agent header: {agent_version}",
                auto_fix="Sync versions in YAML frontmatter or markdown headers"
            ))
    
    def _check_core_rule_consistency(self):
        """Verify CORE rules match across prompts and agents."""
        # Load CORE rules from both sources
        architect_rules = self._extract_core_rules(self.prompts_dir / "cortex-architect.prompt.md")
        auditor_rules = self._extract_core_rules(self.agents_dir / "cortex-auditor.md")
        
        # Find rules in architect but not in auditor
        missing_in_auditor = architect_rules - auditor_rules
        
        if missing_in_auditor:
            self.issues.append(CoherenceIssue(
                severity="WARNING",
                category="CORE Rule Inconsistency",
                file_path=str(self.agents_dir / "cortex-auditor.md"),
                description=f"Auditor missing {len(missing_in_auditor)} CORE rules from Architect prompt",
                evidence=f"Missing rules: {', '.join(sorted(missing_in_auditor))}",
                auto_fix="Add missing CORE rules to auditor P1 checklist"
            ))
    
    def _check_mcp_enforcement(self):
        """Validate MCP-FIRST enforcement consistency."""
        architect_prompt = self.prompts_dir / "cortex-architect.prompt.md"
        
        if not architect_prompt.exists():
            return
        
        content = architect_prompt.read_text(encoding="utf-8")
        
        # Check for MCP pre-flight enforcement
        if "MCP PRE-FLIGHT CHECK" not in content:
            self.issues.append(CoherenceIssue(
                severity="CRITICAL",
                category="MCP Enforcement",
                file_path=str(architect_prompt),
                description="Missing MCP PRE-FLIGHT CHECK section in architect prompt",
                evidence="Section not found in cortex-architect.prompt.md",
                auto_fix="Add MCP PRE-FLIGHT CHECK section enforcing MCP availability before IMPLEMENT/FIX/REFACTOR"
            ))
        
        # Check for native tool restrictions
        if "COPILOT NATIVE TOOL RESTRICTIONS" not in content:
            self.issues.append(CoherenceIssue(
                severity="CRITICAL",
                category="MCP Enforcement",
                file_path=str(architect_prompt),
                description="Missing COPILOT NATIVE TOOL RESTRICTIONS section",
                evidence="GAP-001 enforcement not documented",
                auto_fix="Add tool restriction matrix blocking create_file/replace_string_in_file for IMPLEMENT intents"
            ))
    
    def _check_deprecated_orchestrators(self):
        """Find references to deprecated orchestrators (AC-PROMPT-CLEANUP-001)."""
        wiring_yaml = self.workspace_root / "cortex" / "__wiring_contract__.yaml"
        
        if not wiring_yaml.exists():
            return
        
        # Load active orchestrators from wiring
        with open(wiring_yaml, 'r', encoding='utf-8') as f:
            wiring_data = yaml.safe_load(f)
        
        active_orchestrators = set()
        if wiring_data and 'orchestrators' in wiring_data:
            for orch in wiring_data['orchestrators']:
                active_orchestrators.add(orch.get('name', ''))
        
        # Check prompts for references to non-wired orchestrators
        for prompt_file in self.prompts_dir.glob("*.md"):
            content = prompt_file.read_text(encoding="utf-8")
            
            # Extract orchestrator references (simple pattern matching)
            referenced = set(re.findall(r'(\w+Orchestrator)', content))
            
            deprecated = referenced - active_orchestrators
            if deprecated:
                self.issues.append(CoherenceIssue(
                    severity="WARNING",
                    category="Deprecated Orchestrators",
                    file_path=str(prompt_file),
                    description=f"References to {len(deprecated)} un-wired orchestrators",
                    evidence=f"Orchestrators: {', '.join(sorted(deprecated))}",
                    auto_fix="Remove deprecated orchestrator references or add to wiring.yaml"
                ))
    
    def _check_duplicate_sections(self):
        """Detect duplicate content across prompt files (AC-PROMPT-CLEANUP-005)."""
        prompt_files = list(self.prompts_dir.glob("*.md"))
        
        for i, file1 in enumerate(prompt_files):
            content1 = file1.read_text(encoding="utf-8")
            sections1 = self._extract_sections(content1)
            
            for file2 in prompt_files[i+1:]:
                content2 = file2.read_text(encoding="utf-8")
                sections2 = self._extract_sections(content2)
                
                # Find similar sections (>80% similarity)
                for sec1_title, sec1_content in sections1.items():
                    for sec2_title, sec2_content in sections2.items():
                        similarity = SequenceMatcher(None, sec1_content, sec2_content).ratio()
                        
                        if similarity > 0.8 and len(sec1_content) > 200:
                            self.issues.append(CoherenceIssue(
                                severity="INFO",
                                category="Duplicate Sections",
                                file_path=str(file1),
                                description=f"Duplicate content in {file1.name} and {file2.name}",
                                evidence=f"Section '{sec1_title}' has {similarity:.1%} similarity with '{sec2_title}'",
                                auto_fix="Extract to shared reference file or consolidate"
                            ))
    
    def _check_audit_check_coverage(self):
        """Verify all P0-P3 checks are documented in both prompt and agent."""
        architect_checks = self._extract_audit_checks(self.prompts_dir / "cortex-architect.prompt.md")
        auditor_checks = self._extract_audit_checks(self.agents_dir / "cortex-auditor.md")
        
        # Find checks in architect but not in auditor
        missing = architect_checks - auditor_checks
        
        if missing:
            self.issues.append(CoherenceIssue(
                severity="WARNING",
                category="Audit Check Coverage",
                file_path=str(self.agents_dir / "cortex-auditor.md"),
                description=f"Auditor missing {len(missing)} checks from Architect prompt",
                evidence=f"Missing checks: {', '.join(sorted(list(missing)[:5]))}...",
                auto_fix="Add missing checks to cortex-auditor.md P1-P3 sections"
            ))
    
    # Helper methods
    
    def _extract_version(self, file_path: Path) -> str:
        """Extract version from markdown header."""
        content = file_path.read_text(encoding="utf-8")
        match = re.search(r'[vV]ersion:?\s*(\d+\.\d+)', content)
        return match.group(1) if match else "unknown"
    
    def _extract_core_rules(self, file_path: Path) -> set:
        """Extract CORE rule references (e.g., CORE-008, CORE-027)."""
        if not file_path.exists():
            return set()
        
        content = file_path.read_text(encoding="utf-8")
        return set(re.findall(r'CORE-\d{3}', content))
    
    def _extract_sections(self, content: str) -> Dict[str, str]:
        """Extract markdown sections (## Header → content)."""
        sections = {}
        current_section = None
        current_content = []
        
        for line in content.split('\n'):
            if line.startswith('## '):
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line[3:].strip()
                current_content = []
            elif current_section:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _extract_audit_checks(self, file_path: Path) -> set:
        """Extract audit check names from tables."""
        if not file_path.exists():
            return set()
        
        content = file_path.read_text(encoding="utf-8")
        
        # Extract check names from markdown tables (| CheckName | ...)
        checks = set()
        in_table = False
        
        for line in content.split('\n'):
            if '|' in line and '---' not in line:
                in_table = True
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 2 and parts[1]:  # First column is check name
                    checks.add(parts[1])
        
        return checks


# AC_COMPLETE: AC-PROMPT-CLEANUP-001 ✅ PromptCoherenceValidator implemented with 6 validation checks
