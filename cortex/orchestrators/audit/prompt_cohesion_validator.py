"""
PromptCohesionValidator - AUDIT Mode P1.5 Cohesion Check.

Validates consistency across 3 key prompt files:
- copilot-instructions.md (GitHub Copilot)
- CORTEX.prompt.md (Production agent)
- cortex-architect.prompt.md (Architect/AUDIT/DESIGN modes)

Checks:
1. Version drift (P1.5-001): Detect files >7 days out of sync
2. CORE rules consistency (P1.5-002): Validate all CORE rules match
3. MCP-FIRST enforcement (P1.5-003): Verify MCP gateway enforcement

Author: Asif Hussain
Date: 2026-02-07
Phase: 39 Stage 1
"""

import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass


# Constants (REFACTOR: Extracted magic numbers)
VERSION_DRIFT_THRESHOLD_DAYS = 7
"""Maximum days between prompt updates before drift is flagged."""

CRITICAL_CORE_RULES = [
    "CORE-002",  # NO markdown file generation
    "CORE-008",  # TDD mandatory
    "CORE-028",  # File naming conventions
    "CORE-029",  # Response header mandatory
    "CORE-030",  # Implementation Truth
    "CORE-035",  # Single canonical implementation
]
"""CORE rules that MUST be consistently enforced across all prompts."""

PROMPT_FILES = [
    ".github/copilot-instructions.md",
    ".github/prompts/CORTEX.prompt.md",
    ".github/prompts/cortex-architect.prompt.md",
]
"""Core prompt files monitored for cohesion."""


@dataclass
class PromptMetadata:
    """Metadata extracted from prompt file."""
    file_path: str
    version: Optional[str]
    updated: Optional[str]
    core_rules: List[str]
    mcp_rules: List[str]
    has_preflight: bool
    has_gate: bool
    tool_routing: Dict[str, str]
    intent_mappings: Dict[str, str]


# AC_START: AC-PHASE39-001
# Description: PromptCohesionValidator GREEN phase implementation
# Author: Asif Hussain
# Date: 2026-02-07


class PromptCohesionValidator:
    """
    Validate prompt file cohesion across CORTEX architecture.
    
    Ensures:
    - Version synchronization (≤7 day drift)
    - CORE rules consistency
    - MCP-FIRST enforcement alignment
    
    Usage:
        validator = PromptCohesionValidator()
        result = validator.validate_all()
        
        if not result["cohesive"]:
            print(result["issues"])
    """
    
    def __init__(self, repo_root: Optional[Path] = None):
        """
        Initialize validator.
        
        Args:
            repo_root: Repository root path (auto-detected if None)
        """
        self.repo_root = repo_root or Path.cwd()
        self.prompt_files = [
            ".github/copilot-instructions.md",
            ".github/prompts/CORTEX.prompt.md",
            ".github/prompts/cortex-architect.prompt.md"
        ]
        self.key_core_rules = [
            "CORE-002", "CORE-008", "CORE-028", 
            "CORE-029", "CORE-030", "CORE-035"
        ]
        self.key_mcp_rules = ["MCP-FIRST", "MCP-GATE", "ARCH-012"]
    
    def validate_all(self) -> Dict[str, Any]:
        """
        Run all validation checks.
        
        Returns:
            Dict with:
            - cohesive: bool (all checks passed)
            - issues: List[str] (human-readable issues)
            - details: Dict (detailed check results)
        """
        # Extract metadata from all prompts
        metadata = {}
        for file_path in self.prompt_files:
            full_path = self.repo_root / file_path
            if full_path.exists():
                content = full_path.read_text()
                metadata[file_path] = self.extract_metadata(content, file_path)
        
        # Run checks
        version_drift = self.check_version_drift(metadata)
        core_consistency = self.check_core_rules_consistency(metadata)
        mcp_enforcement = self.check_mcp_enforcement(metadata)
        
        # Aggregate results
        issues = []
        
        if version_drift["has_drift"]:
            for file in version_drift["drifted_files"]:
                days = version_drift["drift_days"][file]
                issues.append(
                    f"P1.5-001: {file} version drift "
                    f"({days} days > {VERSION_DRIFT_THRESHOLD_DAYS} day threshold)"
                )
        
        if not core_consistency["consistent"]:
            for file, missing in core_consistency["missing_rules"].items():
                issues.append(f"P1.5-002: {file} missing CORE rules: {', '.join(missing)}")
        
        if not mcp_enforcement["consistent"]:
            if mcp_enforcement["missing_preflight"]:
                issues.append(f"P1.5-003: Missing MCP PRE-FLIGHT in {mcp_enforcement['missing_preflight']}")
            if mcp_enforcement["missing_gate"]:
                issues.append(f"P1.5-003: Missing MCP-GATE in {mcp_enforcement['missing_gate']}")
        
        return {
            "cohesive": len(issues) == 0,
            "issues": issues,
            "details": {
                "version_drift": version_drift,
                "core_consistency": core_consistency,
                "mcp_enforcement": mcp_enforcement
            }
        }
    
    def extract_metadata(self, content: str, file_path: str) -> PromptMetadata:
        """
        Extract metadata from prompt file.
        
        Args:
            content: Prompt file content
            file_path: File path for identification
            
        Returns:
            PromptMetadata object
        """
        # Extract version and updated date
        version = self._extract_version(content)
        updated = self._extract_updated_date(content)
        
        # Extract CORE rules
        core_rules = self.extract_core_rules(content)
        
        # Extract MCP rules
        mcp_rules = self._extract_mcp_rules(content)
        
        # Check MCP sections
        has_preflight = "MCP PRE-FLIGHT" in content or "MCP-FIRST" in content
        has_gate = "MCP-GATE" in content or "cortex_process_request" in content
        
        # Extract tool routing
        tool_routing = self._extract_tool_routing(content)
        
        # Extract intent mappings
        intent_mappings = self._extract_intent_mappings(content)
        
        return PromptMetadata(
            file_path=file_path,
            version=version,
            updated=updated,
            core_rules=core_rules,
            mcp_rules=mcp_rules,
            has_preflight=has_preflight,
            has_gate=has_gate,
            tool_routing=tool_routing,
            intent_mappings=intent_mappings
        )
    
    def _extract_version(self, content: str) -> Optional[str]:
        """Extract version number from prompt header."""
        match = re.search(r'\*\*Version:\*\*\s+([\d.]+)', content)
        return match.group(1) if match else None
    
    def _extract_updated_date(self, content: str) -> Optional[str]:
        """Extract updated date from prompt header."""
        match = re.search(r'\*\*Updated:\*\*\s+([\d-]+)', content)
        return match.group(1) if match else None
    
    def extract_core_rules(self, content: str) -> List[str]:
        """
        Extract CORE rule IDs from prompt content.
        
        Args:
            content: Prompt file content
            
        Returns:
            List of CORE rule IDs (e.g., ['CORE-002', 'CORE-008'])
        """
        rules = []
        for rule in self.key_core_rules:
            if rule in content:
                rules.append(rule)
        return rules
    
    def _extract_mcp_rules(self, content: str) -> List[str]:
        """Extract MCP-specific rules."""
        rules = []
        for rule in self.key_mcp_rules:
            if rule in content:
                rules.append(rule)
        return rules
    
    def _extract_tool_routing(self, content: str) -> Dict[str, str]:
        """Extract intent → tool routing."""
        routing = {}
        
        # Look for IMPLEMENT → cortex_process_request patterns
        if "IMPLEMENT" in content and "cortex_process_request" in content:
            routing["IMPLEMENT"] = "cortex_process_request"
        
        if "FIX" in content and "cortex_process_request" in content:
            routing["FIX"] = "cortex_process_request"
        
        return routing
    
    def _extract_intent_mappings(self, content: str) -> Dict[str, str]:
        """Extract intent → orchestrator mappings."""
        mappings = {}
        
        # Pattern: IMPLEMENT → TDDOrchestrator
        pattern = r'(\w+)\s+→\s+(\w+Orchestrator)'
        matches = re.findall(pattern, content)
        
        for intent, orchestrator in matches:
            mappings[intent] = orchestrator
        
        return mappings
    
    def check_version_drift(self, metadata: Dict[str, PromptMetadata]) -> Dict[str, Any]:
        """
        Check for version drift beyond threshold.
        
        Args:
            metadata: Dict of file_path → PromptMetadata
            
        Returns:
            Dict with:
            - has_drift: bool
            - drifted_files: List[str]
            - drift_days: Dict[str, int]
            - missing_versions: List[str]
            - missing_dates: List[str]
        """
        has_drift = False
        drifted_files = []
        drift_days = {}
        missing_versions = []
        missing_dates = []
        
        today = datetime.now()
        
        for file_path, meta in metadata.items():
            # Check for missing metadata
            if meta.version is None:
                missing_versions.append(file_path)
            
            if meta.updated is None:
                missing_dates.append(file_path)
                continue
            
            # Calculate drift using constant threshold
            try:
                updated_date = datetime.strptime(meta.updated, "%Y-%m-%d")
                days_diff = (today - updated_date).days
                
                if days_diff > VERSION_DRIFT_THRESHOLD_DAYS:
                    has_drift = True
                    drifted_files.append(file_path)
                    drift_days[file_path] = days_diff
            except ValueError:
                missing_dates.append(file_path)
        
        return {
            "has_drift": has_drift,
            "drifted_files": drifted_files,
            "drift_days": drift_days,
            "missing_versions": missing_versions,
            "missing_dates": missing_dates
        }
    
    def check_core_rules_consistency(self, metadata: Dict[str, PromptMetadata]) -> Dict[str, Any]:
        """
        Check CORE rules consistency across prompts.
        
        Args:
            metadata: Dict of file_path → PromptMetadata
            
        Returns:
            Dict with:
            - consistent: bool
            - missing_rules: Dict[file_path, List[rule_id]]
        """
        consistent = True
        missing_rules = {}
        
        # Find rules present in all files
        all_rules = set()
        for meta in metadata.values():
            all_rules.update(meta.core_rules)
        
        # Check each file has all rules
        for file_path, meta in metadata.items():
            missing = [rule for rule in self.key_core_rules if rule not in meta.core_rules]
            if missing:
                consistent = False
                missing_rules[file_path] = missing
        
        return {
            "consistent": consistent,
            "missing_rules": missing_rules
        }
    
    def check_mcp_enforcement(self, metadata: Dict[str, PromptMetadata]) -> Dict[str, Any]:
        """
        Check MCP-FIRST enforcement alignment.
        
        Args:
            metadata: Dict of file_path → PromptMetadata
            
        Returns:
            Dict with:
            - consistent: bool
            - missing_preflight: List[file_path]
            - missing_gate: List[file_path]
        """
        consistent = True
        missing_preflight = []
        missing_gate = []
        
        for file_path, meta in metadata.items():
            if not meta.has_preflight:
                consistent = False
                missing_preflight.append(file_path)
            
            if not meta.has_gate:
                consistent = False
                missing_gate.append(file_path)
        
        return {
            "consistent": consistent,
            "missing_preflight": missing_preflight,
            "missing_gate": missing_gate
        }


# AC_COMPLETE: AC-PHASE39-001 GREEN ✅ Version drift detection implemented
# AC_COMPLETE: AC-PHASE39-002 GREEN ✅ CORE rules consistency implemented
# AC_COMPLETE: AC-PHASE39-003 GREEN ✅ MCP enforcement validation implemented
