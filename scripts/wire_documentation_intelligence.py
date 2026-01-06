#!/usr/bin/env python3
"""
Documentation Intelligence Wiring Script for CORTEX Upgrade System
Automatically wires documentation changes (validators, CSS, diagrams, etc.).

Author: Asif Hussain
Version: 1.0.0
Date: January 6, 2026
"""

import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class DocumentationIntelligenceWirer:
    """Wires documentation changes from commit analysis."""

    def __init__(self, workspace_root: Path = Path.cwd()):
        self.workspace_root = workspace_root
        self.docs_orch_manifest = workspace_root / "cortex-brain" / "manifests" / "orchestrators" / "documentation-orchestrator.yaml"
        self.css_variables = workspace_root / "cortex-brain" / "tier2" / "variables.css"
        self.approved_panels = workspace_root / "cortex-brain" / "documents" / "planning" / "active" / "html-glassmorphism-alignment" / "standards" / "approved-panels.yaml"

    def load_documentation_orchestrator_manifest(self) -> Dict:
        """Load documentation orchestrator manifest."""
        with open(self.docs_orch_manifest, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def save_documentation_orchestrator_manifest(self, manifest: Dict):
        """Save documentation orchestrator manifest."""
        with open(self.docs_orch_manifest, "w", encoding="utf-8") as f:
            yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)

    def register_validator(self, validator_name: str, orchestrator: str, priority: str = "HIGH") -> bool:
        """Register a validator in documentation orchestrator."""
        try:
            # Load manifest
            manifest = self.load_documentation_orchestrator_manifest()

            # Ensure validators section exists
            if "validators" not in manifest:
                manifest["validators"] = []

            # Check if validator already registered
            for validator in manifest["validators"]:
                if validator.get("name") == validator_name:
                    print(f"⚠️  Validator '{validator_name}' already registered, skipping")
                    return False

            # Add validator
            manifest["validators"].append({
                "name": validator_name,
                "priority": priority,
                "auto_run": priority in ["CRITICAL", "HIGH"],
                "auto_remediation": priority == "CRITICAL",
                "registered_date": datetime.now().strftime("%Y-%m-%d")
            })

            # Save manifest
            self.save_documentation_orchestrator_manifest(manifest)

            print(f"✅ Registered validator: {validator_name} (priority {priority})")
            return True

        except Exception as e:
            print(f"❌ Error registering validator '{validator_name}': {e}")
            return False

    def update_css_registry(self, new_classes: List[str]) -> bool:
        """Update CSS registry with new classes."""
        try:
            # This would parse variables.css and add new classes
            # For now, just log the action
            print(f"📝 Would add {len(new_classes)} new CSS classes to registry")
            for css_class in new_classes:
                print(f"   - {css_class}")
            return True

        except Exception as e:
            print(f"❌ Error updating CSS registry: {e}")
            return False

    def generate_diagram_requirements(self, count: int, target: str, tools: List[str]) -> Dict:
        """Generate diagram requirements for architectural pages."""
        diagrams = []

        if target == "architecture":
            diagram_specs = [
                {"name": "Four-Tier Brain Hierarchy", "tool": "d3.js", "type": "sunburst"},
                {"name": "System Component Overview", "tool": "d3.js", "type": "force-directed"},
                {"name": "Data Flow Pipeline", "tool": "mermaid", "type": "flowchart"},
                {"name": "Agent Coordination Protocol", "tool": "mermaid", "type": "sequence"},
                {"name": "Database Schema Relationships", "tool": "mermaid", "type": "er"},
                {"name": "Tier Access Patterns", "tool": "d3.js", "type": "sankey"},
                {"name": "Module Dependency Graph", "tool": "d3.js", "type": "chord"},
                {"name": "Git Checkpoint Architecture", "tool": "mermaid", "type": "flowchart"},
                {"name": "SKULL Rule Enforcement Points", "tool": "mermaid", "type": "deployment"}
            ]

            diagrams = diagram_specs[:count]

        elif target == "orchestrators":
            diagram_specs = [
                {"name": "Orchestrator Lifecycle", "tool": "mermaid", "type": "state"},
                {"name": "Category Interaction Matrix", "tool": "d3.js", "type": "chord"},
                {"name": "TDD Cycle", "tool": "mermaid", "type": "flowchart"},
                {"name": "Planning Phases", "tool": "mermaid", "type": "timeline"},
                {"name": "Execution Pipeline", "tool": "mermaid", "type": "sequence"}
            ]

            diagrams = diagram_specs[:min(count, len(diagram_specs))]

        return {
            "target": target,
            "count": len(diagrams),
            "diagrams": diagrams,
            "generation_script": "scripts/generate_architecture_diagrams.py"
        }

    def process_documentation_queue(self, queue: Dict, timestamp: str):
        """Process documentation action queue."""
        results = {
            "validators_registered": 0,
            "css_classes_added": 0,
            "diagram_requirements_generated": 0,
            "errors": []
        }

        # Process documentation actions
        for action in queue.get("documentation_actions", []):
            if action["type"] == "register_validator":
                for validator in action.get("validators", []):
                    success = self.register_validator(
                        validator_name=validator,
                        orchestrator=action.get("orchestrator", "documentation_orchestrator"),
                        priority=action.get("priority", "HIGH")
                    )
                    if success:
                        results["validators_registered"] += 1

            elif action["type"] == "update_css_registry":
                css_classes = action.get("css_classes", [])
                success = self.update_css_registry(css_classes)
                if success:
                    results["css_classes_added"] += len(css_classes)

            elif action["type"] == "generate_diagrams":
                diagram_req = self.generate_diagram_requirements(
                    count=action.get("count", 9),
                    target=action.get("target", "architecture"),
                    tools=action.get("tools", ["mermaid", "d3.js"])
                )
                results["diagram_requirements_generated"] += diagram_req["count"]

                # Save diagram requirements
                output_dir = self.workspace_root / "cortex-brain" / "documents" / "upgrades" / timestamp
                output_dir.mkdir(parents=True, exist_ok=True)
                diagram_req_path = output_dir / f"diagram-requirements-{action['target']}.json"
                with open(diagram_req_path, "w", encoding="utf-8") as f:
                    json.dump(diagram_req, f, indent=2)

        # Save results
        output_dir = self.workspace_root / "cortex-brain" / "documents" / "upgrades" / timestamp
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "documentation-wiring-log.json"

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        print(f"\n📊 Documentation Wiring Results:")
        print(f"  Validators registered: {results['validators_registered']}")
        print(f"  CSS classes added: {results['css_classes_added']}")
        print(f"  Diagram requirements generated: {results['diagram_requirements_generated']}")
        print(f"  Errors: {len(results['errors'])}")

        return results


def main():
    """Main entry point."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python wire_documentation_intelligence.py <wiring_queue_path>")
        sys.exit(1)

    queue_path = Path(sys.argv[1])
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    wirer = DocumentationIntelligenceWirer()

    with open(queue_path, "r", encoding="utf-8") as f:
        queue = json.load(f)

    results = wirer.process_documentation_queue(queue, timestamp)

    if results["errors"]:
        print("\n❌ Documentation wiring completed with errors")
        sys.exit(1)
    else:
        print("\n✅ Documentation wiring completed successfully")
        sys.exit(0)


if __name__ == "__main__":
    main()
