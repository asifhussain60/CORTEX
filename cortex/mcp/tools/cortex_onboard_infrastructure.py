"""
MCP Tool: cortex_onboard_infrastructure

Registers infrastructure entities (platforms, APIs, applications) into the
infrastructure catalog. Supports YAML generation and topology updates.

Authority: Phase 08 — Registry & Docs Alignment
"""

from typing import Dict, Any, Optional, Literal
from pathlib import Path
import yaml
from datetime import datetime


class InfrastructureOnboardingTool:
    """MCP tool for infrastructure catalog management."""

    def __init__(self, registry_path: str = "cortex-registry/company/infrastructure"):
        """Initialize with infrastructure catalog path."""
        self.registry_path = Path(registry_path)
        self.platforms_dir = self.registry_path / "platforms"
        self.apis_dir = self.registry_path / "apis"
        self.applications_dir = self.registry_path / "applications"
        self.topology_file = self.registry_path / "topology.yaml"

    def onboard_infrastructure(
        self,
        entity_type: Literal["platform", "api", "application"],
        name: str,
        data: Dict[str, Any],
        link_to_repo: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Register infrastructure entity into catalog.

        Args:
            entity_type: Type of entity (platform, api, or application)
            name: Entity name (becomes filename)
            data: Entity data as dictionary
            link_to_repo: Optional GitHub repository URL

        Returns:
            Result dictionary with status and created file path
        """
        # Validate entity type
        if entity_type not in ["platform", "api", "application"]:
            return {
                "success": False,
                "error": f"Invalid entity_type: {entity_type}. Must be platform, api, or application.",
            }

        # Add standard fields
        data["name"] = name
        data["created_at"] = datetime.utcnow().isoformat() + "Z"
        data["last_updated"] = data["created_at"]
        if link_to_repo:
            data["owner_repo"] = link_to_repo

        try:
            # Determine target directory
            if entity_type == "platform":
                target_dir = self.platforms_dir
            elif entity_type == "api":
                target_dir = self.apis_dir
            else:  # application
                target_dir = self.applications_dir

            # Ensure directory exists
            target_dir.mkdir(parents=True, exist_ok=True)

            # Write YAML file
            filename = f"{name.lower().replace(' ', '-')}.yaml"
            filepath = target_dir / filename

            with open(filepath, "w") as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)

            # Regenerate topology
            self._regenerate_topology()

            return {
                "success": True,
                "entity_type": entity_type,
                "name": name,
                "file": str(filepath),
                "message": f"Successfully onboarded {entity_type}: {name}",
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to onboard {entity_type} '{name}': {str(e)}",
            }

    def _regenerate_topology(self) -> None:
        """Regenerate topology.yaml from platform/api/application YAMLs."""
        try:
            topology = {
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat() + "Z",
                    "version": "1.0",
                },
                "platforms": {},
                "apis": {},
                "applications": {},
                "dependency_graph": {},
            }

            # Load all platforms
            if self.platforms_dir.exists():
                for platform_file in self.platforms_dir.glob("*.yaml"):
                    try:
                        with open(platform_file) as f:
                            platform_data = yaml.safe_load(f)
                            if platform_data and "name" in platform_data:
                                topology["platforms"][platform_data["name"]] = {
                                    "type": platform_data.get("type", "unknown"),
                                    "provider": platform_data.get("provider", "unknown"),
                                }
                    except Exception:
                        pass

            # Load all APIs
            if self.apis_dir.exists():
                for api_file in self.apis_dir.glob("*.yaml"):
                    try:
                        with open(api_file) as f:
                            api_data = yaml.safe_load(f)
                            if api_data and "name" in api_data:
                                topology["apis"][api_data["name"]] = {
                                    "type": api_data.get("type", "rest"),
                                    "version": api_data.get("version", "1.0"),
                                }
                    except Exception:
                        pass

            # Load all applications
            if self.applications_dir.exists():
                for app_file in self.applications_dir.glob("*.yaml"):
                    try:
                        with open(app_file) as f:
                            app_data = yaml.safe_load(f)
                            if app_data and "name" in app_data:
                                topology["applications"][app_data["name"]] = {
                                    "type": app_data.get("type", "unknown"),
                                    "platform": app_data.get("platform", "unknown"),
                                }
                                # Build dependency relationships
                                if app_data.get("apis_consumed"):
                                    topology["dependency_graph"][app_data["name"]] = {
                                        "consumes": app_data["apis_consumed"],
                                        "dependencies": app_data.get("dependencies", {}).get("internal_services", []),
                                    }
                    except Exception:
                        pass

            # Write topology file
            with open(self.topology_file, "w") as f:
                yaml.dump(topology, f, default_flow_style=False, sort_keys=False)

        except Exception as e:
            # Non-blocking — log but don't fail
            print(f"Warning: Could not regenerate topology.yaml: {e}")

    def list_infrastructure(
        self, entity_type: Literal["platform", "api", "application", "all"] = "all"
    ) -> Dict[str, Any]:
        """
        List all infrastructure entities.

        Args:
            entity_type: Filter by type or "all"

        Returns:
            Dictionary with entities grouped by type
        """
        result = {
            "platforms": [],
            "apis": [],
            "applications": [],
        }

        try:
            if entity_type in ["platform", "all"] and self.platforms_dir.exists():
                for f in self.platforms_dir.glob("*.yaml"):
                    try:
                        with open(f) as fp:
                            data = yaml.safe_load(fp)
                            if data:
                                result["platforms"].append(data["name"])
                    except Exception:
                        pass

            if entity_type in ["api", "all"] and self.apis_dir.exists():
                for f in self.apis_dir.glob("*.yaml"):
                    try:
                        with open(f) as fp:
                            data = yaml.safe_load(fp)
                            if data:
                                result["apis"].append(data["name"])
                    except Exception:
                        pass

            if entity_type in ["application", "all"] and self.applications_dir.exists():
                for f in self.applications_dir.glob("*.yaml"):
                    try:
                        with open(f) as fp:
                            data = yaml.safe_load(fp)
                            if data:
                                result["applications"].append(data["name"])
                    except Exception:
                        pass

            return {
                "success": True,
                "entities": result,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# MCP Tool interface
def cortex_onboard_infrastructure(
    entity_type: Literal["platform", "api", "application"],
    name: str,
    data: Dict[str, Any],
    link_to_repo: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Public MCP tool for onboarding infrastructure entities.

    Parameters:
        entity_type (str): Type of entity — "platform", "api", or "application"
        name (str): Entity name (becomes filename in registry)
        data (dict): Entity metadata (follows infrastructure schema)
        link_to_repo (str, optional): GitHub repository URL for owner_repo field

    Returns:
        dict: Result with status, file path, and messages

    Example:
        >>> from cortex.mcp.tools import cortex_onboard_infrastructure
        >>> cortex_onboard_infrastructure(
        ...     entity_type="api",
        ...     name="cortex-orchestration-api",
        ...     data={
        ...         "type": "rest",
        ...         "version": "1.0.0",
        ...         "base_url": "https://api.cortex.internal/v1",
        ...         "endpoints": ["/orchestrate", "/validate", "/execute"],
        ...         "consumers": ["dashboard", "cli"],
        ...         "auth": "jwt",
        ...     },
        ...     link_to_repo="https://github.com/asifhussain60/cortex"
        ... )
    """
    tool = InfrastructureOnboardingTool()
    return tool.onboard_infrastructure(entity_type, name, data, link_to_repo)
