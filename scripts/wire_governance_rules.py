#!/usr/bin/env python3
"""
Governance Rule Integration Script for CORTEX Upgrade System
Automatically wires governance rules into brain protection system.

Author: Asif Hussain
Version: 1.0.0
Date: January 6, 2026
"""

import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class GovernanceRuleWirer:
    """Wires governance rules from commit analysis into brain protection system."""

    CATEGORIES = [
        "TDD_ENFORCEMENT",
        "HOLISTIC_DISCOVERY",
        "REFACTOR_CLEANUP",
        "GIT_ISOLATION",
        "PLANNING_ISOLATION",
        "HAND_OFF_PROTOCOL",
        "DOCUMENTATION_STANDARDS",
        "CSS_GOVERNANCE",
        "AUDIT_LOGGING"
    ]

    PRIORITY_LEVELS = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    ENFORCEMENT_ACTIONS = ["BLOCK", "WARN", "LOG"]

    def __init__(self, workspace_root: Path = Path.cwd()):
        self.workspace_root = workspace_root
        self.brain_protection_path = workspace_root / "cortex-brain" / "brain-protection-rules.yaml"

    def load_brain_protection_rules(self) -> Dict:
        """Load brain protection rules."""
        with open(self.brain_protection_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def save_brain_protection_rules(self, rules: Dict):
        """Save brain protection rules."""
        with open(self.brain_protection_path, "w", encoding="utf-8") as f:
            yaml.dump(rules, f, default_flow_style=False, sort_keys=False)

    def add_governance_rule(
        self,
        rule_name: str,
        category: str,
        priority: str,
        description: str,
        enforcement_action: str = "WARN",
        validation_hooks: List[str] = None
    ) -> bool:
        """Add a new governance rule to brain protection system."""
        try:
            # Load current rules
            rules = self.load_brain_protection_rules()

            # Validate inputs
            if category not in self.CATEGORIES:
                print(f"⚠️  Unknown category: {category}, using DOCUMENTATION_STANDARDS")
                category = "DOCUMENTATION_STANDARDS"

            if priority not in self.PRIORITY_LEVELS:
                print(f"⚠️  Invalid priority: {priority}, using MEDIUM")
                priority = "MEDIUM"

            if enforcement_action not in self.ENFORCEMENT_ACTIONS:
                print(f"⚠️  Invalid enforcement action: {enforcement_action}, using WARN")
                enforcement_action = "WARN"

            # Check if rule already exists
            for cat_rules in rules.values():
                if isinstance(cat_rules, dict) and "rules" in cat_rules:
                    for rule in cat_rules["rules"]:
                        if rule.get("name") == rule_name:
                            print(f"⚠️  Rule '{rule_name}' already exists, skipping")
                            return False

            # Ensure category exists
            if category not in rules:
                rules[category] = {
                    "description": f"{category} governance rules",
                    "rules": []
                }

            # Add rule
            new_rule = {
                "name": rule_name,
                "priority": priority,
                "description": description,
                "enforcement": enforcement_action,
                "validation_hooks": validation_hooks or [],
                "added_date": datetime.now().strftime("%Y-%m-%d")
            }

            rules[category]["rules"].append(new_rule)

            # Save rules
            self.save_brain_protection_rules(rules)

            print(f"✅ Added governance rule: {rule_name} (priority {priority}, category {category})")
            return True

        except Exception as e:
            print(f"❌ Error adding governance rule '{rule_name}': {e}")
            return False

    def validate_governance_rules(self) -> Dict:
        """Validate all governance rules."""
        errors = []
        warnings = []

        try:
            rules = self.load_brain_protection_rules()

            # Check for rule name conflicts
            rule_names = set()
            for category, cat_data in rules.items():
                if isinstance(cat_data, dict) and "rules" in cat_data:
                    for rule in cat_data["rules"]:
                        name = rule.get("name")
                        if name in rule_names:
                            errors.append(f"Duplicate rule name: {name}")
                        rule_names.add(name)

                        # Validate priority
                        priority = rule.get("priority")
                        if priority not in self.PRIORITY_LEVELS:
                            errors.append(f"Invalid priority for rule '{name}': {priority}")

                        # Validate enforcement action
                        enforcement = rule.get("enforcement")
                        if enforcement not in self.ENFORCEMENT_ACTIONS:
                            errors.append(f"Invalid enforcement action for rule '{name}': {enforcement}")

            return {
                "valid": len(errors) == 0,
                "total_rules": len(rule_names),
                "errors": errors,
                "warnings": warnings
            }

        except Exception as e:
            errors.append(f"Error validating governance rules: {e}")
            return {"valid": False, "errors": errors, "warnings": warnings}

    def process_governance_queue(self, queue: Dict, timestamp: str):
        """Process governance action queue."""
        results = {
            "rules_added": 0,
            "validation_passed": False,
            "errors": []
        }

        # Process governance actions
        for action in queue.get("governance_actions", []):
            if action["type"] == "add_governance_rule":
                success = self.add_governance_rule(
                    rule_name=action["rule"],
                    category=action.get("category", "DOCUMENTATION_STANDARDS"),
                    priority=action["priority"],
                    description=action["description"],
                    enforcement_action=action.get("enforcement", "WARN"),
                    validation_hooks=action.get("validation_hooks", [])
                )
                if success:
                    results["rules_added"] += 1

        # Validate all rules
        validation = self.validate_governance_rules()
        results["validation_passed"] = validation["valid"]
        if not validation["valid"]:
            results["errors"].extend(validation["errors"])

        # Save results
        output_dir = self.workspace_root / "cortex-brain" / "documents" / "upgrades" / timestamp
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "governance-rules-added.json"

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        print(f"\n📊 Governance Wiring Results:")
        print(f"  Rules added: {results['rules_added']}")
        print(f"  Validation passed: {results['validation_passed']}")
        print(f"  Errors: {len(results['errors'])}")

        return results


def main():
    """Main entry point."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python wire_governance_rules.py <wiring_queue_path>")
        sys.exit(1)

    queue_path = Path(sys.argv[1])
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    wirer = GovernanceRuleWirer()

    with open(queue_path, "r", encoding="utf-8") as f:
        queue = json.load(f)

    results = wirer.process_governance_queue(queue, timestamp)

    if results["errors"]:
        print("\n❌ Governance wiring completed with errors")
        sys.exit(1)
    else:
        print("\n✅ Governance wiring completed successfully")
        sys.exit(0)


if __name__ == "__main__":
    main()
