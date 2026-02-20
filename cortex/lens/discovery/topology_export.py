"""
Topology Export for Discovery System.

Exports discovered topology to multiple formats:
- JSON: Machine-readable, API consumption
- YAML: Human-readable, configuration files
- Mermaid: Flowcharts and diagrams
- PlantUML: UML component diagrams

Author: Asif Hussain
Phase: 9.3 - Topology Export
AC-ID: DISC-010
"""

import json
import logging
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


logger = logging.getLogger(__name__)


class ExportFormat(Enum):
    """Supported export formats."""

    JSON = "json"
    YAML = "yaml"
    MERMAID = "mermaid"
    PLANTUML = "plantuml"


class MermaidGenerator:
    """Generates Mermaid diagrams from topology data.

    Examples:
        >>> generator = MermaidGenerator()
        >>> topology = {"services": [{"name": "api", "depends_on": ["db"]}]}
        >>> generator.generate_flowchart(topology, Path("diagram.mmd"))
    """

    def generate_flowchart(self, topology: Dict, output_file: Path) -> str:
        """Generate Mermaid flowchart from topology.

        Args:
            topology: Topology data dictionary
            output_file: Output file path

        Returns:
            Generated Mermaid diagram content
        """
        lines = ["graph TD"]

        # Extract services and dependencies
        services = topology.get("services", [])

        if not services:
            lines.append("    Empty[No services discovered]")
        else:
            for service in services:
                service_name = service.get("name", "Unknown")
                service_id = service_name.replace("-", "_").replace(" ", "_")

                # Add service node
                lines.append(f"    {service_id}[{service_name}]")

                # Add dependencies
                for dep in service.get("depends_on", []):
                    dep_id = dep.replace("-", "_").replace(" ", "_")
                    lines.append(f"    {service_id} --> {dep_id}")

        content = "\n".join(lines)
        output_file.write_text(content)
        logger.info(f"Mermaid diagram exported to {output_file}")

        return content


class PlantUMLGenerator:
    """Generates PlantUML diagrams from topology data.

    Examples:
        >>> generator = PlantUMLGenerator()
        >>> topology = {"components": [{"name": "API", "type": "web"}]}
        >>> generator.generate_component_diagram(topology, Path("diagram.puml"))
    """

    def generate_component_diagram(self, topology: Dict, output_file: Path) -> str:
        """Generate PlantUML component diagram from topology.

        Args:
            topology: Topology data dictionary
            output_file: Output file path

        Returns:
            Generated PlantUML diagram content
        """
        lines = ["@startuml", ""]

        # Extract components
        components = topology.get("components", [])
        connections = topology.get("connections", [])

        # Add components
        for component in components:
            name = component.get("name", "Unknown")
            comp_type = component.get("type", "component")
            lines.append(f"component [{name}] as {name}")

        lines.append("")

        # Add connections
        for connection in connections:
            from_comp = connection.get("from", "")
            to_comp = connection.get("to", "")
            if from_comp and to_comp:
                lines.append(f"{from_comp} --> {to_comp}")

        lines.append("")
        lines.append("@enduml")

        content = "\n".join(lines)
        output_file.write_text(content)
        logger.info(f"PlantUML diagram exported to {output_file}")

        return content


class TopologyExporter:
    """Exports topology to multiple formats.

    Supports JSON, YAML, Mermaid, and PlantUML exports for visualization
    and API consumption.

    Examples:
        >>> exporter = TopologyExporter()
        >>> topology = {"databases": [{"name": "postgres"}]}
        >>> exporter.export(topology, Path("topology.json"), ExportFormat.JSON)
        >>> exporter.export(topology, Path("topology.yaml"), ExportFormat.YAML)
    """

    def __init__(self):
        """Initialize topology exporter."""
        self.mermaid_generator = MermaidGenerator()
        self.plantuml_generator = PlantUMLGenerator()
        logger.info("TopologyExporter initialized")

    def get_supported_formats(self) -> List[ExportFormat]:
        """Get list of supported export formats.

        Returns:
            List of ExportFormat enums
        """
        return [
            ExportFormat.JSON,
            ExportFormat.YAML,
            ExportFormat.MERMAID,
            ExportFormat.PLANTUML,
        ]

    def export(self, topology: Dict[str, Any], output_file: Path, format: ExportFormat) -> None:
        """Export topology to specified format.

        Args:
            topology: Topology data to export
            output_file: Output file path
            format: Export format (JSON, YAML, MERMAID, PLANTUML)

        Raises:
            ValueError: If format is not supported
        """
        if format == ExportFormat.JSON:
            self._export_json(topology, output_file)
        elif format == ExportFormat.YAML:
            self._export_yaml(topology, output_file)
        elif format == ExportFormat.MERMAID:
            self._export_mermaid(topology, output_file)
        elif format == ExportFormat.PLANTUML:
            self._export_plantuml(topology, output_file)
        else:
            raise ValueError(f"Unsupported export format: {format}")

        logger.info(f"Topology exported to {output_file} ({format.value})")

    def _export_json(self, topology: Dict, output_file: Path) -> None:
        """Export topology to JSON format.

        Args:
            topology: Topology data
            output_file: Output file path
        """
        output_file.write_text(json.dumps(topology, indent=2))

    def _export_yaml(self, topology: Dict, output_file: Path) -> None:
        """Export topology to YAML format.

        Args:
            topology: Topology data
            output_file: Output file path

        Raises:
            ImportError: If PyYAML is not installed
        """
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML required for YAML export: pip install pyyaml")

        import yaml
        output_file.write_text(yaml.dump(topology, default_flow_style=False, sort_keys=False))

    def _export_mermaid(self, topology: Dict, output_file: Path) -> None:
        """Export topology to Mermaid diagram format.

        Args:
            topology: Topology data
            output_file: Output file path
        """
        self.mermaid_generator.generate_flowchart(topology, output_file)

    def _export_plantuml(self, topology: Dict, output_file: Path) -> None:
        """Export topology to PlantUML diagram format.

        Args:
            topology: Topology data
            output_file: Output file path
        """
        self.plantuml_generator.generate_component_diagram(topology, output_file)
