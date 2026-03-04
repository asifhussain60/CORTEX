"""
GraphExporter — Export graph to various formats.

Authority: Phase 3 Wave 4 S2 | Export
Purpose: Export knowledge graph to JSON, GraphML, Cytoscape formats
"""
import json
from cortex.intelligence.lens.knowledge_graph.ast_graph_builder import ASTKnowledgeGraph


class GraphExporter:
    """
    Export knowledge graph to different formats.

    Example:
        exporter = GraphExporter(graph)
        json_data = exporter.to_json()
    """

    def __init__(self, graph: ASTKnowledgeGraph) -> None:
        """Initialize exporter with graph."""
        self.graph = graph

    def to_json(self) -> str:
        """
        Export graph as JSON.

        Returns:
            JSON string representation
        """
        data = {
            "nodes": [
                {
                    "name": node.name,
                    "type": node.type,
                    "file_path": node.file_path,
                    "line_number": node.line_number
                }
                for node in self.graph.nodes.values()
            ],
            "relationships": [
                {
                    "source": rel.source,
                    "relation_type": rel.relation_type,
                    "target": rel.target
                }
                for rel in self.graph.relationships
            ]
        }
        return json.dumps(data, indent=2)

    def to_graphml(self) -> str:
        """
        Export graph as GraphML (XML format).

        Returns:
            GraphML XML string
        """
        nodes_xml = ""
        for i, node in enumerate(self.graph.nodes.values()):
            nodes_xml += f'  <node id="n{i}">\n'
            nodes_xml += f'    <data key="name">{node.name}</data>\n'
            nodes_xml += f'    <data key="type">{node.type}</data>\n'
            nodes_xml += '  </node>\n'

        edges_xml = ""
        for i, rel in enumerate(self.graph.relationships):
            # Find node indices
            source_idx = list(self.graph.nodes.keys()).index(rel.source)
            target_idx = list(self.graph.nodes.keys()).index(rel.target)
            edges_xml += f'  <edge id="e{i}" source="n{source_idx}" target="n{target_idx}"/>\n'

        graphml = f"""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <key id="name" for="node" attr.name="name" attr.type="string"/>
  <key id="type" for="node" attr.name="type" attr.type="string"/>
  <graph id="G" edgedefault="directed">
{nodes_xml}{edges_xml}  </graph>
</graphml>"""
        return graphml

    def to_cytoscape(self) -> str:
        """
        Export graph for Cytoscape visualization.

        Returns:
            JSON string in Cytoscape format
        """
        data = {
            "elements": {
                "nodes": [
                    {
                        "data": {
                            "id": node.name,
                            "label": node.name,
                            "type": node.type
                        }
                    }
                    for node in self.graph.nodes.values()
                ],
                "edges": [
                    {
                        "data": {
                            "source": rel.source,
                            "target": rel.target,
                            "label": rel.relation_type
                        }
                    }
                    for rel in self.graph.relationships
                ]
            }
        }
        return json.dumps(data, indent=2)
