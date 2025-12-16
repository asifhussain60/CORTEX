"""
Master Plan Template - Standardized structure for CORTEX master plans.

This module defines the exact section order and structure for master plans,
derived from cortex-3.9-master.md as the canonical reference.

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
Copyright © 2025 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum


class MasterPlanSection(Enum):
    """Enumeration of master plan sections in canonical order."""
    
    # 1. CORTEX Header (ASCII art)
    CORTEX_HEADER = "cortex_header"
    
    # 2. Title and metadata
    TITLE_METADATA = "title_metadata"
    
    # 3. Request Context
    REQUEST_CONTEXT = "request_context"
    
    # 4. Visual Progress Tracker
    VISUAL_PROGRESS_TRACKER = "visual_progress_tracker"
    
    # 5. Phase Status Table
    PHASE_STATUS_TABLE = "phase_status_table"
    
    # 6. Executive Summary
    EXECUTIVE_SUMMARY = "executive_summary"
    
    # 7. Architectural Changes
    ARCHITECTURAL_CHANGES = "architectural_changes"
    
    # 8. Governance Framework
    GOVERNANCE_FRAMEWORK = "governance_framework"
    
    # 9. Phase Overview
    PHASE_OVERVIEW = "phase_overview"
    
    # 10. Dependency Graph
    DEPENDENCY_GRAPH = "dependency_graph"
    
    # 11. Success Criteria
    SUCCESS_CRITERIA = "success_criteria"
    
    # 12. Deliverables
    DELIVERABLES = "deliverables"
    
    # 13. Risk Analysis
    RISK_ANALYSIS = "risk_analysis"
    
    # 14. Related Documentation
    RELATED_DOCUMENTATION = "related_documentation"
    
    # 15. Execution Strategy
    EXECUTION_STRATEGY = "execution_strategy"
    
    # 16. Version History
    VERSION_HISTORY = "version_history"
    
    # 17. Contact & Support
    CONTACT_SUPPORT = "contact_support"


@dataclass
class MasterPlanTemplate:
    """
    Template for generating master plans with standardized structure.
    
    Canonical order from cortex-3.9-master.md:
    1. CORTEX Header (ASCII art)
    2. Title & Metadata (Plan Name, Type, Status, Created, Last Updated, Completed, Version)
    3. Request Context
    4. Visual Progress Tracker
    5. Phase Status Table
    6. Executive Summary
    7. Architectural Changes
    8. Governance Framework
    9. Phase Overview
    10. Dependency Graph
    11. Success Criteria
    12. Deliverables
    13. Risk Analysis
    14. Related Documentation
    15. Execution Strategy
    16. Version History
    17. Contact & Support
    """
    
    @classmethod
    def get_required_sections(cls) -> List[MasterPlanSection]:
        """Get list of required sections (always present)."""
        return [
            MasterPlanSection.CORTEX_HEADER,
            MasterPlanSection.TITLE_METADATA,
            MasterPlanSection.REQUEST_CONTEXT,
            MasterPlanSection.VISUAL_PROGRESS_TRACKER,
            MasterPlanSection.PHASE_STATUS_TABLE,
            MasterPlanSection.EXECUTIVE_SUMMARY,
            MasterPlanSection.VERSION_HISTORY
        ]
    
    @classmethod
    def get_optional_sections(cls, tier: str) -> List[MasterPlanSection]:
        """Get optional sections based on tier."""
        optional_map = {
            "tier_3": [
                MasterPlanSection.PHASE_OVERVIEW,
                MasterPlanSection.SUCCESS_CRITERIA,
                MasterPlanSection.DELIVERABLES,
                MasterPlanSection.RELATED_DOCUMENTATION
            ],
            "tier_4": [
                MasterPlanSection.ARCHITECTURAL_CHANGES,
                MasterPlanSection.GOVERNANCE_FRAMEWORK,
                MasterPlanSection.PHASE_OVERVIEW,
                MasterPlanSection.DEPENDENCY_GRAPH,
                MasterPlanSection.SUCCESS_CRITERIA,
                MasterPlanSection.DELIVERABLES,
                MasterPlanSection.RISK_ANALYSIS,
                MasterPlanSection.RELATED_DOCUMENTATION,
                MasterPlanSection.EXECUTION_STRATEGY,
                MasterPlanSection.CONTACT_SUPPORT
            ]
        }
        return optional_map.get(tier, [])
    
    @classmethod
    def get_section_order(cls, complexity_tier: int) -> List[MasterPlanSection]:
        """
        Get the canonical section order for a given complexity tier.
        
        Args:
            complexity_tier: Complexity tier (1-4)
            
        Returns:
            Ordered list of sections to include
        """
        sections = list(cls.get_required_sections())
        
        if complexity_tier == 3:
            sections.extend(cls.get_optional_sections("tier_3"))
        elif complexity_tier >= 4:
            sections.extend(cls.get_optional_sections("tier_4"))
        
        # Sort by enum order to maintain canonical sequence
        return sorted(sections, key=lambda s: list(MasterPlanSection).index(s))
    
    @classmethod
    def validate_section_order(cls, actual_sections: List[str]) -> Dict[str, Any]:
        """
        Validate that actual sections follow canonical order.
        
        Args:
            actual_sections: List of section identifiers in actual order
            
        Returns:
            Validation result with errors if any
        """
        errors = []
        warnings = []
        
        # Convert strings to enums
        try:
            actual_enums = [MasterPlanSection(s) for s in actual_sections]
        except ValueError as e:
            errors.append(f"Invalid section identifier: {e}")
            return {
                "valid": False,
                "errors": errors,
                "warnings": warnings
            }
        
        # Check ordering
        expected_order = [list(MasterPlanSection).index(s) for s in actual_enums]
        if expected_order != sorted(expected_order):
            errors.append(
                "Sections not in canonical order. "
                f"Expected: {[s.name for s in sorted(actual_enums, key=lambda x: list(MasterPlanSection).index(x))]}, "
                f"Got: {[s.name for s in actual_enums]}"
            )
        
        # Check for missing required sections
        required_sections = cls.get_required_sections()
        for req_section in required_sections:
            if req_section not in actual_enums:
                warnings.append(f"Missing required section: {req_section.name}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    @staticmethod
    def get_cortex_header() -> str:
        """
        Get the standardized CORTEX header ASCII art.
        
        Returns:
            CORTEX header as markdown comment
        """
        return """<!--
████████████████████████████████████████████████████████████████████████████████
█                                                                              █
█   ██████╗ ██████╗ ██████╗ ████████╗███████╗██╗  ██╗                        █
█  ██╔════╝██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝╚██╗██╔╝                        █
█  ██║     ██║   ██║██████╔╝   ██║   █████╗   ╚███╔╝                         █
█  ██║     ██║   ██║██╔══██╗   ██║   ██╔══╝   ██╔██╗                         █
█  ╚██████╗╚██████╔╝██║  ██║   ██║   ███████╗██╔╝ ██╗                        █
█   ╚═════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝                        █
█                                                                              █
█  AI-Powered Development Intelligence System                                 █
█  Author: Asif Hussain | GitHub: github.com/asifhussain60/CORTEX            █
█  Copyright © 2025 Asif Hussain. All rights reserved.                       █
█                                                                              █
████████████████████████████████████████████████████████████████████████████████
-->"""


# Section templates
SECTION_TEMPLATES = {
    MasterPlanSection.CORTEX_HEADER: MasterPlanTemplate.get_cortex_header,
    
    MasterPlanSection.TITLE_METADATA: lambda plan_id, metadata: f"""# {metadata.get('title', plan_id.replace('-', ' ').title())}

**Plan Name:** {metadata.get('title', plan_id.replace('-', ' ').title())}  
**Type:** Tier {metadata.get('complexity_tier', 'N/A')} {'Complex' if metadata.get('complexity_tier', 0) >= 4 else 'Documented'} Plan  
**Status:** {metadata.get('status', '⏳ In Progress')}  
**Created:** {metadata.get('created', 'TBD')}  
**Last Updated:** {metadata.get('last_updated', 'TBD')}  
**Completed:** {metadata.get('completed', 'TBD')}  
**Version:** {metadata.get('version', '1.0.0')}

---""",
    
    MasterPlanSection.REQUEST_CONTEXT: lambda context: f"""## Request Context

{context}

---""",
    
    MasterPlanSection.EXECUTIVE_SUMMARY: lambda summary, goals, outcomes, autonomous: f"""## 🎯 Executive Summary

{summary}

**Primary Goals:**
{chr(10).join(f'- {goal}' for goal in goals)}

**Key Outcomes:**
{chr(10).join(f'- {outcome}' for outcome in outcomes)}

**Autonomous Execution:**
{autonomous}

---""",
    
    MasterPlanSection.ARCHITECTURAL_CHANGES: lambda changes: f"""## 🏗️ Architectural Changes

{changes}

---""",
    
    MasterPlanSection.GOVERNANCE_FRAMEWORK: lambda framework: f"""## 🛡️ Governance Framework

### New Brain Protection Rules (SKULL System)

{framework}

---""",
    
    MasterPlanSection.PHASE_OVERVIEW: lambda overview: f"""## 📋 Phase Overview

{overview}

---""",
    
    MasterPlanSection.DEPENDENCY_GRAPH: lambda graph: f"""## 🔗 Dependency Graph

{graph}

---""",
    
    MasterPlanSection.SUCCESS_CRITERIA: lambda criteria: f"""## ✅ Success Criteria

{criteria}

---""",
    
    MasterPlanSection.DELIVERABLES: lambda deliverables: f"""## 📁 Deliverables

{deliverables}

---""",
    
    MasterPlanSection.RISK_ANALYSIS: lambda risks: f"""## 🚨 Risk Analysis

{risks}

---""",
    
    MasterPlanSection.RELATED_DOCUMENTATION: lambda docs: f"""## 📖 Related Documentation

{docs}

---""",
    
    MasterPlanSection.EXECUTION_STRATEGY: lambda strategy: f"""## 🚀 Execution Strategy

{strategy}

---""",
    
    MasterPlanSection.VERSION_HISTORY: lambda history: f"""## 🔄 Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
{chr(10).join(f"| {v['version']} | {v['date']} | {v['author']} | {v['changes']} |" for v in history)}

---""",
    
    MasterPlanSection.CONTACT_SUPPORT: lambda contact: f"""## 📞 Contact & Support

{contact}

---"""
}
