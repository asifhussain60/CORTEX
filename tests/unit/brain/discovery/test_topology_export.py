"""
Unit tests for Topology Export functionality.

Tests export of discovered topology to multiple formats:
- JSON (machine-readable, API consumption)
- YAML (human-readable, configuration)
- Mermaid (flowcharts, diagrams)
- PlantUML (UML diagrams)

Author: Asif Hussain
Phase: 9.3 - Topology Export
AC-ID: DISC-010
"""

import pytest
import json
import yaml
from pathlib import Path
from cortex.brain.discovery.topology_export import (
    TopologyExporter,
    ExportFormat,
    MermaidGenerator,
    PlantUMLGenerator,
)


class TestTopologyExporterInit:
    """Test TopologyExporter initialization."""

    def test_init_creates_exporter(self):
        """Test that TopologyExporter initializes correctly."""
        exporter = TopologyExporter()
        
        assert exporter is not None
        assert hasattr(exporter, 'export')

    def test_supported_formats_defined(self):
        """Test that supported export formats are defined."""
        exporter = TopologyExporter()
        formats = exporter.get_supported_formats()
        
        assert ExportFormat.JSON in formats
        assert ExportFormat.YAML in formats
        assert ExportFormat.MERMAID in formats
        assert ExportFormat.PLANTUML in formats


class TestJSONExport:
    """Test JSON export functionality."""

    def test_export_simple_topology_to_json(self, tmp_path):
        """Test exporting topology to JSON format."""
        exporter = TopologyExporter()
        
        topology = {
            "databases": [{"name": "postgres", "type": "postgresql"}],
            "apis": [{"name": "api", "type": "rest"}],
        }
        
        output_file = tmp_path / "topology.json"
        exporter.export(topology, output_file, ExportFormat.JSON)
        
        assert output_file.exists()
        data = json.loads(output_file.read_text())
        assert data["databases"][0]["name"] == "postgres"
        assert data["apis"][0]["type"] == "rest"

    def test_export_nested_topology_to_json(self, tmp_path):
        """Test exporting complex nested topology to JSON."""
        exporter = TopologyExporter()
        
        topology = {
            "services": {
                "api": {
                    "dependencies": ["database", "cache"],
                    "config": {"port": 8000}
                }
            }
        }
        
        output_file = tmp_path / "complex.json"
        exporter.export(topology, output_file, ExportFormat.JSON)
        
        assert output_file.exists()
        data = json.loads(output_file.read_text())
        assert "services" in data
        assert data["services"]["api"]["dependencies"] == ["database", "cache"]


class TestYAMLExport:
    """Test YAML export functionality."""

    def test_export_topology_to_yaml(self, tmp_path):
        """Test exporting topology to YAML format."""
        exporter = TopologyExporter()
        
        topology = {
            "databases": [{"name": "mysql", "version": "8.0"}],
            "microservices": [{"name": "user-service", "port": 3000}],
        }
        
        output_file = tmp_path / "topology.yaml"
        exporter.export(topology, output_file, ExportFormat.YAML)
        
        assert output_file.exists()
        data = yaml.safe_load(output_file.read_text())
        assert data["databases"][0]["name"] == "mysql"
        assert data["microservices"][0]["port"] == 3000


class TestMermaidExport:
    """Test Mermaid diagram export."""

    def test_generate_mermaid_flowchart(self, tmp_path):
        """Test generating Mermaid flowchart from topology."""
        generator = MermaidGenerator()
        
        topology = {
            "services": [
                {"name": "api", "depends_on": ["db", "cache"]},
                {"name": "db", "depends_on": []},
                {"name": "cache", "depends_on": []},
            ]
        }
        
        output_file = tmp_path / "diagram.mmd"
        mermaid = generator.generate_flowchart(topology, output_file)
        
        assert output_file.exists()
        content = output_file.read_text()
        assert "graph TD" in content or "graph LR" in content
        assert "api" in content
        assert "db" in content

    def test_mermaid_handles_empty_topology(self, tmp_path):
        """Test Mermaid generation with empty topology."""
        generator = MermaidGenerator()
        
        topology = {"services": []}
        
        output_file = tmp_path / "empty.mmd"
        mermaid = generator.generate_flowchart(topology, output_file)
        
        assert output_file.exists()
        content = output_file.read_text()
        assert "graph" in content


class TestPlantUMLExport:
    """Test PlantUML diagram export."""

    def test_generate_plantuml_component_diagram(self, tmp_path):
        """Test generating PlantUML component diagram."""
        generator = PlantUMLGenerator()
        
        topology = {
            "components": [
                {"name": "Frontend", "type": "web"},
                {"name": "Backend", "type": "api"},
                {"name": "Database", "type": "storage"},
            ],
            "connections": [
                {"from": "Frontend", "to": "Backend"},
                {"from": "Backend", "to": "Database"},
            ]
        }
        
        output_file = tmp_path / "components.puml"
        plantuml = generator.generate_component_diagram(topology, output_file)
        
        assert output_file.exists()
        content = output_file.read_text()
        assert "@startuml" in content
        assert "@enduml" in content
        assert "Frontend" in content

    def test_plantuml_handles_no_connections(self, tmp_path):
        """Test PlantUML generation with no connections."""
        generator = PlantUMLGenerator()
        
        topology = {
            "components": [{"name": "Standalone", "type": "service"}],
            "connections": []
        }
        
        output_file = tmp_path / "standalone.puml"
        plantuml = generator.generate_component_diagram(topology, output_file)
        
        assert output_file.exists()
        content = output_file.read_text()
        assert "Standalone" in content


class TestExportIntegration:
    """Test complete export workflow."""

    def test_export_to_multiple_formats(self, tmp_path):
        """Test exporting same topology to multiple formats."""
        exporter = TopologyExporter()
        
        topology = {
            "services": [{"name": "app", "type": "web"}],
            "databases": [{"name": "db", "type": "postgres"}],
        }
        
        # Export to JSON
        json_file = tmp_path / "topology.json"
        exporter.export(topology, json_file, ExportFormat.JSON)
        
        # Export to YAML
        yaml_file = tmp_path / "topology.yaml"
        exporter.export(topology, yaml_file, ExportFormat.YAML)
        
        # Both should exist and contain same data
        assert json_file.exists()
        assert yaml_file.exists()
        
        json_data = json.loads(json_file.read_text())
        yaml_data = yaml.safe_load(yaml_file.read_text())
        
        assert json_data == yaml_data

    def test_export_handles_invalid_format(self, tmp_path):
        """Test export with invalid format raises error."""
        exporter = TopologyExporter()
        
        topology = {"data": "value"}
        output_file = tmp_path / "output.txt"
        
        with pytest.raises((ValueError, AttributeError)):
            exporter.export(topology, output_file, "INVALID_FORMAT")

    def test_mermaid_and_plantuml_export_workflow(self, tmp_path):
        """Test exporting diagrams for visualization."""
        exporter = TopologyExporter()
        
        topology = {
            "services": [
                {"name": "frontend", "depends_on": ["backend"]},
                {"name": "backend", "depends_on": ["database"]},
            ],
            "components": [
                {"name": "Frontend", "type": "web"},
                {"name": "Backend", "type": "api"},
            ],
            "connections": [{"from": "Frontend", "to": "Backend"}]
        }
        
        # Export Mermaid
        mermaid_file = tmp_path / "services.mmd"
        exporter.export(topology, mermaid_file, ExportFormat.MERMAID)
        assert mermaid_file.exists()
        assert "graph" in mermaid_file.read_text()
        
        # Export PlantUML
        plantuml_file = tmp_path / "components.puml"
        exporter.export(topology, plantuml_file, ExportFormat.PLANTUML)
        assert plantuml_file.exists()
        assert "@startuml" in plantuml_file.read_text()
