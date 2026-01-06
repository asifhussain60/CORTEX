#!/usr/bin/env python3
"""
Architectural Change Wiring Script for CORTEX Upgrade System
Automatically wires orchestrators, manifests, and routing changes.

Author: Asif Hussain
Version: 1.0.0
Date: January 6, 2026
"""

import json
import re
import subprocess
import yaml
from pathlib import Path
from typing import Dict, List, Optional


class ArchitecturalWirer:
    """Wires architectural changes from commit analysis."""

    def __init__(self, workspace_root: Path = Path.cwd()):
        self.workspace_root = workspace_root
        self.master_orch_path = workspace_root / "cortex-brain" / "config" / "master-orchestrator.yaml"
        self.manifests_dir = workspace_root / "cortex-brain" / "manifests" / "orchestrators"

    def load_wiring_queue(self, queue_path: Path) -> Dict:
        """Load wiring action queue from commit analysis."""
        with open(queue_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_master_orchestrator_config(self) -> Dict:
        """Load master orchestrator configuration."""
        with open(self.master_orch_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def save_master_orchestrator_config(self, config: Dict):
        """Save master orchestrator configuration."""
        with open(self.master_orch_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    def register_orchestrator(self, name: str, manifest_path: str, priority: int) -> bool:
        """Register a new orchestrator in master-orchestrator.yaml."""
        try:
            # Load master config
            config = self.load_master_orchestrator_config()

            # Check if already registered
            if "orchestrators" not in config:
                config["orchestrators"] = []

            for orch in config["orchestrators"]:
                if orch.get("name") == name:
                    print(f"⚠️  Orchestrator '{name}' already registered, skipping")
                    return False

            # Load orchestrator manifest to get routing pattern
            manifest_full_path = self.workspace_root / manifest_path
            if not manifest_full_path.exists():
                print(f"❌ Manifest not found: {manifest_path}")
                return False

            with open(manifest_full_path, "r", encoding="utf-8") as f:
                manifest = yaml.safe_load(f)

            # Extract routing pattern
            routing = manifest.get("routing", {})
            pattern = routing.get("pattern", "")
            if not pattern:
                print(f"❌ No routing pattern found in manifest: {manifest_path}")
                return False

            # Add orchestrator to config
            config["orchestrators"].append({
                "name": name,
                "pattern": pattern,
                "priority": priority,
                "manifest": manifest_path,
                "enabled": True
            })

            # Sort by priority (ascending)
            config["orchestrators"].sort(key=lambda x: x.get("priority", 999))

            # Save config
            self.save_master_orchestrator_config(config)

            print(f"✅ Registered orchestrator: {name} (priority {priority})")
            return True

        except Exception as e:
            print(f"❌ Error registering orchestrator '{name}': {e}")
            return False

    def validate_manifest(self, manifest_path: str) -> Dict:
        """Validate orchestrator manifest."""
        errors = []
        warnings = []

        manifest_full_path = self.workspace_root / manifest_path
        if not manifest_full_path.exists():
            errors.append(f"Manifest file not found: {manifest_path}")
            return {"valid": False, "errors": errors, "warnings": warnings}

        try:
            with open(manifest_full_path, "r", encoding="utf-8") as f:
                manifest = yaml.safe_load(f)

            # Check required fields
            required_fields = ["name", "version", "routing", "phases", "outputs"]
            for field in required_fields:
                if field not in manifest:
                    errors.append(f"Missing required field: {field}")

            # Validate routing
            if "routing" in manifest:
                routing = manifest["routing"]
                if "pattern" not in routing:
                    errors.append("Missing routing.pattern")
                else:
                    # Test regex pattern
                    try:
                        re.compile(routing["pattern"])
                    except re.error as e:
                        errors.append(f"Invalid routing pattern regex: {e}")

            # Check audit logging integration
            if "audit_logging" not in manifest:
                warnings.append("No audit logging integration defined")

            # Check brain protection rules
            if "brain_protection" not in manifest:
                warnings.append("No brain protection rules defined")

            # Check knowledge base inheritance
            if "knowledge_base_inheritance" not in manifest:
                warnings.append("No knowledge base inheritance defined")

            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings
            }

        except Exception as e:
            errors.append(f"Error parsing manifest: {e}")
            return {"valid": False, "errors": errors, "warnings": warnings}

    def reload_routing_table(self) -> bool:
        """Reload and validate routing table."""
        try:
            config = self.load_master_orchestrator_config()

            # Validate all patterns
            patterns = []
            for orch in config.get("orchestrators", []):
                pattern = orch.get("pattern", "")
                if not pattern:
                    print(f"⚠️  Orchestrator '{orch.get('name')}' has no pattern")
                    continue

                # Test regex
                try:
                    re.compile(pattern)
                    patterns.append((orch["name"], pattern))
                except re.error as e:
                    print(f"❌ Invalid pattern for '{orch.get('name')}': {e}")
                    return False

            # Check for priority conflicts
            priorities = {}
            for orch in config.get("orchestrators", []):
                priority = orch.get("priority")
                name = orch.get("name")
                if priority in priorities:
                    print(f"⚠️  Priority conflict: {name} and {priorities[priority]} both have priority {priority}")
                priorities[priority] = name

            print(f"✅ Routing table validated: {len(patterns)} patterns")
            return True

        except Exception as e:
            print(f"❌ Error reloading routing table: {e}")
            return False

    def process_wiring_queue(self, queue: Dict, timestamp: str):
        """Process wiring action queue."""
        results = {
            "orchestrators_registered": 0,
            "manifests_validated": 0,
            "routing_reloaded": False,
            "errors": []
        }

        # Process orchestrator registrations
        for action in queue.get("architectural_actions", []):
            if action["type"] == "register_orchestrator":
                success = self.register_orchestrator(
                    name=action["name"],
                    manifest_path=action["manifest"],
                    priority=action["priority"]
                )
                if success:
                    results["orchestrators_registered"] += 1

            elif action["type"] == "validate_manifest":
                validation = self.validate_manifest(action["manifest"])
                if validation["valid"]:
                    results["manifests_validated"] += 1
                else:
                    results["errors"].extend(validation["errors"])

            elif action["type"] == "reload_routing_table":
                success = self.reload_routing_table()
                results["routing_reloaded"] = success

        # Save results
        output_dir = self.workspace_root / "cortex-brain" / "documents" / "upgrades" / timestamp
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "orchestrator-registration-log.json"

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        print(f"\n📊 Wiring Results:")
        print(f"  Orchestrators registered: {results['orchestrators_registered']}")
        print(f"  Manifests validated: {results['manifests_validated']}")
        print(f"  Routing reloaded: {results['routing_reloaded']}")
        print(f"  Errors: {len(results['errors'])}")

        return results


def main():
    """Main entry point."""
    import sys
    from datetime import datetime

    if len(sys.argv) < 2:
        print("Usage: python wire_architectural_changes.py <wiring_queue_path>")
        sys.exit(1)

    queue_path = Path(sys.argv[1])
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    wirer = ArchitecturalWirer()
    queue = wirer.load_wiring_queue(queue_path)
    results = wirer.process_wiring_queue(queue, timestamp)

    if results["errors"]:
        print("\n❌ Wiring completed with errors")
        sys.exit(1)
    else:
        print("\n✅ Wiring completed successfully")
        sys.exit(0)


if __name__ == "__main__":
    main()
