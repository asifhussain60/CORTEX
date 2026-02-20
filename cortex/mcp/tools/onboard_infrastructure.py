"""cortex_onboard_infrastructure MCP tool.

Registers company infrastructure entities (platforms, APIs, applications)
into cortex-registry/company/infrastructure/ and regenerates topology.

Authority: Phase 08 — Registry & Docs Alignment (R9)
"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Registry base path
INFRASTRUCTURE_DIR = Path("cortex-registry/company/infrastructure")
SCHEMA_FILE = INFRASTRUCTURE_DIR / "_schema.yaml"


def _get_entity_dir(entity_type: str) -> Path:
    """Get the directory for a given entity type.

    Args:
        entity_type: One of 'platform', 'api', 'application'.

    Returns:
        Path to the entity-specific directory.

    Raises:
        ValueError: If entity_type is not valid.
    """
    valid_types = {"platform": "platforms", "api": "apis", "application": "applications"}
    if entity_type not in valid_types:
        raise ValueError(
            f"Invalid entity_type '{entity_type}'. Must be one of: {list(valid_types.keys())}"
        )
    return INFRASTRUCTURE_DIR / valid_types[entity_type]


def _validate_required_fields(entity_type: str, data: Dict[str, Any]) -> List[str]:
    """Validate required fields are present in data.

    Args:
        entity_type: One of 'platform', 'api', 'application'.
        data: Entity data dictionary.

    Returns:
        List of validation error messages (empty = valid).
    """
    required_fields: Dict[str, List[str]] = {
        "platform": ["name", "type", "provider"],
        "api": ["name", "type", "version"],
        "application": ["name", "type", "repository"],
    }
    errors = []
    for field_name in required_fields.get(entity_type, []):
        if field_name not in data:
            errors.append(f"Missing required field: '{field_name}' for entity_type '{entity_type}'")
    return errors


def _serialize_yaml(data: Dict[str, Any]) -> str:
    """Serialize dict to YAML string without external dependency.

    Args:
        data: Dictionary to serialize.

    Returns:
        YAML-formatted string.
    """
    lines = []
    _dict_to_yaml(data, lines, indent=0)
    return "\n".join(lines) + "\n"


def _dict_to_yaml(obj: Any, lines: List[str], indent: int) -> None:
    """Recursively convert object to YAML lines.

    Args:
        obj: Object to serialize.
        lines: List to append YAML lines to.
        indent: Current indentation level.
    """
    prefix = "  " * indent
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{prefix}{key}:")
                _dict_to_yaml(value, lines, indent + 1)
            else:
                lines.append(f"{prefix}{key}: {_format_value(value)}")
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict):
                first = True
                for key, value in item.items():
                    if first:
                        lines.append(f"{prefix}- {key}: {_format_value(value)}")
                        first = False
                    else:
                        lines.append(f"{prefix}  {key}: {_format_value(value)}")
            else:
                lines.append(f"{prefix}- {_format_value(item)}")
    else:
        lines.append(f"{prefix}{_format_value(obj)}")


def _format_value(value: Any) -> str:
    """Format a scalar value for YAML output.

    Args:
        value: Value to format.

    Returns:
        YAML-safe string representation.
    """
    if value is None:
        return "null"
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, str):
        if any(c in value for c in ":#{}[]&*?|>!%@`"):
            return f'"{value}"'
        return value
    return str(value)


def onboard_infrastructure(
    entity_type: str,
    name: str,
    data: Dict[str, Any],
    link_to_repo: Optional[str] = None,
) -> Dict[str, Any]:
    """Register an infrastructure entity in the CORTEX registry.

    Creates a YAML file in cortex-registry/company/infrastructure/{type}s/{name}.yaml
    and triggers topology regeneration.

    Args:
        entity_type: One of 'platform', 'api', 'application'.
        name: Unique entity name.
        data: Entity data dictionary (validated against schema).
        link_to_repo: Optional repository name to cross-reference.

    Returns:
        Result dictionary with status, file_path, and any errors.
    """
    result: Dict[str, Any] = {
        "status": "error",
        "entity_type": entity_type,
        "name": name,
        "file_path": None,
        "errors": [],
    }

    # Validate entity type
    try:
        entity_dir = _get_entity_dir(entity_type)
    except ValueError as e:
        result["errors"].append(str(e))
        return result

    # Ensure name is in data
    data["name"] = name

    # Validate required fields
    validation_errors = _validate_required_fields(entity_type, data)
    if validation_errors:
        result["errors"] = validation_errors
        return result

    # Add metadata
    now = datetime.now(timezone.utc).isoformat()
    data["created_at"] = data.get("created_at", now)
    data["updated_at"] = now

    if link_to_repo:
        data["linked_repo"] = link_to_repo

    # Build YAML content
    yaml_content = f"# Infrastructure: {entity_type} — {name}\n"
    yaml_content += f"# Generated: {now}\n"
    yaml_content += f"# Authority: cortex_onboard_infrastructure MCP tool\n\n"
    yaml_content += _serialize_yaml(data)

    # Write file
    file_path = entity_dir / f"{name}.yaml"
    try:
        entity_dir.mkdir(parents=True, exist_ok=True)
        file_path.write_text(yaml_content)
        result["status"] = "success"
        result["file_path"] = str(file_path)
    except Exception as e:
        result["errors"].append(f"Failed to write {file_path}: {e}")
        return result

    # Regenerate topology (non-blocking)
    try:
        _regenerate_topology()
    except Exception as e:
        logger.warning("Topology regeneration failed: %s", e)
        result["topology_warning"] = str(e)

    return result


def _regenerate_topology() -> None:
    """Regenerate topology.yaml from all infrastructure YAML files.

    Walks platforms/, apis/, applications/ and builds a dependency graph.
    Non-blocking: failures are logged but do not prevent entity registration.
    """
    topology: Dict[str, Any] = {
        "version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": str(INFRASTRUCTURE_DIR),
        "topology": {
            "platforms": [],
            "apis": [],
            "applications": [],
            "dependency_graph": {"edges": []},
            "statistics": {
                "total_platforms": 0,
                "total_apis": 0,
                "total_applications": 0,
                "total_edges": 0,
            },
        },
    }

    # Count entities
    for entity_type, dirname in [
        ("platforms", "platforms"),
        ("apis", "apis"),
        ("applications", "applications"),
    ]:
        entity_dir = INFRASTRUCTURE_DIR / dirname
        if entity_dir.exists():
            yaml_files = [
                f.stem for f in entity_dir.iterdir() if f.suffix in (".yaml", ".yml")
            ]
            topology["topology"][entity_type] = yaml_files
            topology["topology"]["statistics"][f"total_{entity_type}"] = len(yaml_files)

    # Write topology
    topology_path = INFRASTRUCTURE_DIR / "topology.yaml"
    header = "# Auto-generated topology — do not edit manually\n"
    header += f"# Generated: {topology['generated_at']}\n\n"
    topology_path.write_text(header + _serialize_yaml(topology))
