#!/usr/bin/env python3
"""
Phase 81 S2 Task 2: Add agent metadata to all core agents
Script to batch add YAML front-matter metadata to agent specs
"""

import os
import re
from typing import Dict

AGENTS_METADATA = {
    "cortex-digest.md": {
        "agent_id": "cortex-digest",
        "version": "1.5",
        "status": "active",
        "layer": "core",
        "capabilities": ["session_learning", "pattern_extraction", "knowledge_synthesis"],
        "modes_served": ["DIGEST"],
        "mcp_tools": ["cortex_digest_session"],
        "collaborators": ["cortex-architect"],
        "priority": "P1",
        "token_cost_estimate": 2500,
        "created_date": "2026-02-08",
    },
    "cortex-environment-setup.md": {
        "agent_id": "cortex-environment-setup",
        "version": "1.8",
        "status": "active",
        "layer": "core",
        "capabilities": ["environment_validation", "dependency_checking", "mcp_setup"],
        "modes_served": ["PRE-FLIGHT"],
        "mcp_tools": ["cortex_validate_environment", "cortex_validate_venv"],
        "collaborators": [],
        "priority": "P0",
        "token_cost_estimate": 1800,
        "created_date": "2026-02-08",
    },
    "cortex-holistic-validator.md": {
        "agent_id": "cortex-holistic-validator",
        "version": "2.3",
        "status": "active",
        "layer": "core",
        "capabilities": ["holistic_validation", "phase_validation", "governance_checking"],
        "modes_served": ["AUDIT", "DESIGN"],
        "mcp_tools": ["cortex_validate_compliance", "cortex_audit_remediation_plan"],
        "collaborators": ["cortex-auditor", "cortex-designer"],
        "priority": "P0",
        "token_cost_estimate": 3200,
        "created_date": "2026-02-08",
    },
    "cortex-interactive.md": {
        "agent_id": "cortex-interactive",
        "version": "1.4",
        "status": "active",
        "layer": "core",
        "capabilities": ["user_interaction", "request_refinement", "context_clarification"],
        "modes_served": ["INTERACTIVE"],
        "mcp_tools": ["cortex_process_request"],
        "collaborators": ["cortex-architect"],
        "priority": "P2",
        "token_cost_estimate": 1600,
        "created_date": "2026-02-08",
    },
    "cortex-phase-resolver.md": {
        "agent_id": "cortex-phase-resolver",
        "version": "1.0",
        "status": "active",
        "layer": "core",
        "capabilities": ["phase_resolution", "session_continuity", "context_extraction"],
        "modes_served": ["PLAN"],
        "mcp_tools": ["cortex_resolve_phase"],
        "collaborators": ["cortex-master-plan-auditor"],
        "priority": "P0",
        "token_cost_estimate": 2300,
        "created_date": "2026-02-04",
    },
    "cortex-storyteller.md": {
        "agent_id": "cortex-storyteller",
        "version": "1.2",
        "status": "active",
        "layer": "core",
        "capabilities": ["response_formatting", "narrative_structure", "clarity_optimization"],
        "modes_served": ["INTERACTIVE"],
        "mcp_tools": [],
        "collaborators": ["cortex-architect"],
        "priority": "P2",
        "token_cost_estimate": 1200,
        "created_date": "2026-02-08",
    },
}


def format_metadata_yaml(metadata: Dict) -> str:
    """Format metadata dictionary as YAML front-matter."""
    yaml_lines = ["---"]
    
    for key in ["agent_id", "version", "status", "layer", "capabilities", "modes_served", 
                "mcp_tools", "collaborators", "priority", "token_cost_estimate", 
                "created_date", "last_updated"]:
        if key == "last_updated":
            yaml_lines.append(f'{key}: "2026-02-11"')
        elif key == "maintainer":
            yaml_lines.append(f'{key}: "Asif Hussain"')
        elif key in metadata:
            value = metadata[key]
            if isinstance(value, list):
                if value:
                    yaml_lines.append(f"{key}:")
                    for item in value:
                        yaml_lines.append(f"  - {item}")
                else:
                    yaml_lines.append(f"{key}: []")
            elif isinstance(value, (int, float)):
                yaml_lines.append(f"{key}: {value}")
            else:
                yaml_lines.append(f'{key}: "{value}"')
    
    yaml_lines.append('maintainer: "Asif Hussain"')
    yaml_lines.append("---")
    return "\n".join(yaml_lines)


def add_metadata_to_agent(filepath: str, metadata: Dict) -> bool:
    """Add YAML front-matter to agent file if not already present."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check if metadata already exists
    if content.startswith('---'):
        print(f"✓ {os.path.basename(filepath)}: Metadata already present")
        return False
    
    # Prepare new content with metadata
    yaml_block = format_metadata_yaml(metadata)
    new_content = yaml_block + "\n\n" + content
    
    # Write back
    with open(filepath, 'w') as f:
        f.write(new_content)
    
    print(f"✓ {os.path.basename(filepath)}: Metadata added")
    return True


def main():
    """Add metadata to all core agents."""
    base_dir = ".github/agents/core"
    
    if not os.path.isdir(base_dir):
        print(f"Error: {base_dir} not found")
        return 1
    
    print("Phase 81 S2 T2: Adding Agent Metadata\n")
    
    updated_count = 0
    for filename, metadata in AGENTS_METADATA.items():
        filepath = os.path.join(base_dir, filename)
        
        if os.path.isfile(filepath):
            if add_metadata_to_agent(filepath, metadata):
                updated_count += 1
        else:
            print(f"✗ {filename}: File not found")
    
    print(f"\nUpdated {updated_count}/{len(AGENTS_METADATA)} agents")
    return 0


if __name__ == "__main__":
    exit(main())
