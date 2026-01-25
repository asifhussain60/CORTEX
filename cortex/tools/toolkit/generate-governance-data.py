#!/usr/bin/env python3
"""
Data generator for governance pyramid visualization.

Generates dynamic data structure for the D3.js Sunburst diagram
showing CORTEX governance tiers and rules.

Usage:
    python generate-governance-data.py > governance-data.json
"""

import json
from dataclasses import dataclass, asdict
from typing import List


@dataclass
class GovernanceRule:
    """Represents a single governance rule."""
    id: str
    name: str
    description: str
    category: str
    tier: int
    impact: str  # HIGH, MEDIUM, LOW


@dataclass
class GovernanceTier:
    """Represents a tier in the governance hierarchy."""
    tier_number: int
    tier_name: str
    tier_description: str
    rule_count: int
    color: str
    rules: List[GovernanceRule]


class GovernanceDataGenerator:
    """Generates governance pyramid data structure."""

    TIERS_DATA = [
        {
            "tier_number": 0,
            "tier_name": "Tier 0: Immutable Governance",
            "tier_description": "29 CORE Rules - Immutable foundation",
            "color": "#2196F3",
            "rules": [
                ("CORE-001", "Intent Classification", "Parse request through LENS", "Classification", "HIGH"),
                ("CORE-008", "TDD First", "Tests BEFORE code implementation", "Development", "HIGH"),
                ("CORE-011", "Type Hints", "Type hints MANDATORY for all functions", "Code Quality", "HIGH"),
                ("CORE-012", "Docstrings", "Google-style docstrings required", "Documentation", "MEDIUM"),
                ("CORE-013", "Error Handling", "No bare except clauses allowed", "Reliability", "HIGH"),
                ("CORE-026", "Git Checkpoints", "Git checkpoint before major changes", "Version Control", "MEDIUM"),
                ("CORE-027", "Audit Trail", "AC_START → AC_EXECUTE → AC_COMPLETE", "Audit", "HIGH"),
                ("CORE-029", "Response Header", "Response header enforcement", "Output", "MEDIUM"),
                ("CORE-014", "Imports", "Proper import organization required", "Code Quality", "MEDIUM"),
                ("CORE-015", "Naming", "Clear, consistent naming conventions", "Code Quality", "MEDIUM"),
                ("CORE-016", "Comments", "Meaningful comments for complex logic", "Documentation", "LOW"),
                ("CORE-017", "DRY Principle", "Don't Repeat Yourself", "Code Quality", "MEDIUM"),
                ("CORE-018", "SOLID", "SOLID principles compliance", "Architecture", "HIGH"),
                ("CORE-019", "Security", "Security best practices", "Security", "HIGH"),
                ("CORE-020", "Performance", "Performance considerations", "Performance", "MEDIUM"),
            ]
        },
        {
            "tier_number": 1,
            "tier_name": "Tier 1: Acceptance Criteria",
            "tier_description": "AC validation and phase specifications",
            "color": "#00BCD4",
            "rules": [
                ("AC-001", "DoR Validation", "Definition of Ready check", "Validation", "HIGH"),
                ("AC-002", "AC-ID Mapping", "Acceptance Criteria identification", "Validation", "HIGH"),
                ("AC-003", "Phase Specs", "Phase specifications defined", "Planning", "MEDIUM"),
                ("AC-004", "Success Metrics", "Success criteria defined", "Measurement", "MEDIUM"),
            ]
        },
        {
            "tier_number": 2,
            "tier_name": "Tier 2: Response Templates",
            "tier_description": "Output formatting and boundaries",
            "color": "#4CAF50",
            "rules": [
                ("RT-001", "Response Headers", "CORTEX branding and tracking", "Formatting", "MEDIUM"),
                ("RT-002", "DoR Display", "Standard DoR table format", "Formatting", "MEDIUM"),
                ("RT-003", "Hallucination Prevention", "Boundary checks for accuracy", "Validation", "HIGH"),
                ("RT-004", "Format Standards", "Consistent output formatting", "Formatting", "MEDIUM"),
                ("RT-005", "Documentation", "Generated documentation format", "Documentation", "MEDIUM"),
                ("RT-006", "Examples", "Code examples included", "Documentation", "LOW"),
                ("RT-007", "Error Display", "Error message formatting", "Error Handling", "MEDIUM"),
                ("RT-008", "Status Reporting", "Status and progress reporting", "Monitoring", "MEDIUM"),
            ]
        },
        {
            "tier_number": 3,
            "tier_name": "Tier 3: Knowledge & Practices",
            "tier_description": "35+ YAML best practices",
            "color": "#FFC107",
            "rules": [
                ("KP-001", "TDD Patterns", "Test-driven development patterns", "Development", "HIGH"),
                ("KP-002", "Refactoring", "Refactoring strategies and patterns", "Development", "MEDIUM"),
                ("KP-003", "API Design", "RESTful API design patterns", "Architecture", "MEDIUM"),
                ("KP-004", "CORTEX Architecture", "CORTEX-specific patterns", "Architecture", "HIGH"),
                ("KP-005", "Integration", "Integration best practices", "Architecture", "MEDIUM"),
                ("KP-006", "Error Recovery", "Error recovery and retry logic", "Reliability", "HIGH"),
                ("KP-007", "State Management", "State management patterns", "Architecture", "MEDIUM"),
                ("KP-008", "Logging", "Comprehensive logging strategies", "Observability", "MEDIUM"),
                ("KP-009", "Testing", "Testing best practices and coverage", "QA", "HIGH"),
                ("KP-010", "Performance", "Performance optimization guide", "Performance", "MEDIUM"),
            ]
        }
    ]

    def generate(self) -> dict:
        """Generate the complete governance data structure."""
        tiers = []

        for tier_info in self.TIERS_DATA:
            rules = [
                GovernanceRule(
                    id=rule[0],
                    name=rule[1],
                    description=rule[2],
                    category=rule[3],
                    tier=tier_info["tier_number"],
                    impact=rule[4]
                )
                for rule in tier_info["rules"]
            ]

            tier = GovernanceTier(
                tier_number=tier_info["tier_number"],
                tier_name=tier_info["tier_name"],
                tier_description=tier_info["tier_description"],
                rule_count=len(rules),
                color=tier_info["color"],
                rules=rules
            )
            tiers.append(tier)

        return {
            "title": "CORTEX Governance Pyramid",
            "description": "Hierarchical governance structure with 29 CORE rules across 4 tiers",
            "total_rules": sum(tier.rule_count for tier in tiers),
            "tiers": [asdict(tier) for tier in tiers]
        }


def main():
    """Generate and output governance data."""
    generator = GovernanceDataGenerator()
    data = generator.generate()

    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
