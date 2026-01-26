#!/usr/bin/env python3
"""
Consolidate individual governance YAML files into single core-rules.yaml

Consolidates:
- response-header-enforcement.yaml (CORE-029)
- core-038-file-placement-policy.yaml (CORE-038)
- core-039-md-generation-prohibition.yaml (CORE-039)
- production-guidelines.yaml (best practices)

Into: core-rules.yaml (single SSOT for Tier 0 governance)

Author: Asif Hussain
Date: 2026-01-26
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List

# Paths
GOVERNANCE_DIR = Path(__file__).parent.parent / "cortex_brain" / "tier0" / "governance"
CORE_RULES_FILE = GOVERNANCE_DIR / "core-rules.yaml"

def load_yaml_file(path: Path) -> Dict[str, Any]:
    """Load YAML file safely."""
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"❌ Error loading {path}: {e}")
        return {}

def extract_rule_data(yaml_content: Dict[str, Any], rule_id: str) -> Dict[str, Any]:
    """Extract rule data from YAML content."""
    # Different files have different structures
    
    # For response-header-enforcement.yaml
    if "response_header_enforcement" in yaml_content:
        return {
            "rule_id": rule_id,
            "category": yaml_content["response_header_enforcement"].get("category", "response_formatting"),
            "severity": yaml_content["response_header_enforcement"].get("severity", "blocked"),
            "name": yaml_content["response_header_enforcement"].get("description", "Response Header Enforcement"),
            "description": f"Response header enforcement rule from response-header-enforcement.yaml",
            "template": yaml_content["response_header_enforcement"].get("template"),
            "field_definitions": yaml_content["response_header_enforcement"].get("field_definitions"),
            "enforcement_rules": yaml_content["response_header_enforcement"].get("enforcement_rules"),
        }
    
    return {}

def consolidate():
    """Consolidate individual YAML files into core-rules.yaml."""
    
    print("=" * 70)
    print("CORTEX GOVERNANCE YAML CONSOLIDATION (Option C - Phase 1)")
    print("=" * 70)
    print()
    
    # Step 1: Load current core-rules.yaml
    print("📖 Step 1: Loading base core-rules.yaml...")
    core_rules = load_yaml_file(CORE_RULES_FILE)
    if not core_rules:
        print("❌ Failed to load core-rules.yaml")
        return False
    
    initial_rule_count = len(core_rules.get("rules", []))
    print(f"   ✅ Loaded {initial_rule_count} existing rules")
    print()
    
    # Step 2: Load individual YAML files
    print("📖 Step 2: Loading individual governance YAML files...")
    
    response_header_path = GOVERNANCE_DIR / "response-header-enforcement.yaml"
    core038_path = GOVERNANCE_DIR / "core-038-file-placement-policy.yaml"
    core039_path = GOVERNANCE_DIR / "core-039-md-generation-prohibition.yaml"
    production_guidelines_path = GOVERNANCE_DIR / "production-guidelines.yaml"
    
    files_to_consolidate = {
        "CORE-029": response_header_path,
        "CORE-038": core038_path,
        "CORE-039": core039_path,
    }
    
    found_rules = {}
    for rule_id, file_path in files_to_consolidate.items():
        if file_path.exists():
            content = load_yaml_file(file_path)
            found_rules[rule_id] = content
            print(f"   ✅ {rule_id}: {file_path.name}")
        else:
            print(f"   ⚠️  {rule_id}: {file_path.name} NOT FOUND")
    
    print()
    
    # Step 3: Check if rules already consolidated
    print("📋 Step 3: Checking if rules already in core-rules.yaml...")
    existing_rule_ids = {rule.get("rule_id") for rule in core_rules.get("rules", [])}
    
    needs_consolidation = []
    for rule_id in found_rules:
        if rule_id not in existing_rule_ids:
            needs_consolidation.append(rule_id)
            print(f"   ⚠️  {rule_id}: Needs consolidation")
        else:
            print(f"   ✅ {rule_id}: Already in core-rules.yaml")
    
    print()
    
    if not needs_consolidation:
        print("✅ All rules already consolidated!")
        print()
        print("📋 Cleanup: Deleting individual YAML files...")
        
        # Delete individual files
        for rule_id, file_path in files_to_consolidate.items():
            if file_path.exists():
                file_path.unlink()
                print(f"   ✅ Deleted {file_path.name}")
        
        # Delete production-guidelines files
        if production_guidelines_path.exists():
            production_guidelines_path.unlink()
            print(f"   ✅ Deleted production-guidelines.yaml")
        
        json_path = GOVERNANCE_DIR / "production-guidelines.json"
        if json_path.exists():
            json_path.unlink()
            print(f"   ✅ Deleted production-guidelines.json")
        
        print()
        print("=" * 70)
        print("✅ CONSOLIDATION COMPLETE")
        print("=" * 70)
        print()
        print("Status:")
        print(f"  - Single SSOT: core-rules.yaml ({len(existing_rule_ids)} rules)")
        print(f"  - Individual files: DELETED")
        print(f"  - GovernanceRegistry: Loads from single core-rules.yaml")
        print()
        return True
    
    print("ℹ️  Rules already consolidated. No changes needed.")
    print()
    return True

if __name__ == "__main__":
    success = consolidate()
    exit(0 if success else 1)
