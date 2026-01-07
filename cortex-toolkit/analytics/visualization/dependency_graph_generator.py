#!/usr/bin/env python3
"""
CORTEX Dependency Graph Generator
Extracts feature dependencies from vision data and generates graph data for visualization.

Usage:
    python scripts/dependency_graph_generator.py

Outputs:
    - docs/gh-pages/assets/data/dependency-graph.json (for D3.js force-directed graph)
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Set


class DependencyGraphGenerator:
    """Generates dependency graph data from CORTEX vision and enhancement metadata."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.nodes = []
        self.links = []
        self.node_id_map = {}
        
    def load_cortex_4_vision(self) -> Dict[str, Any]:
        """Load CORTEX 4.0 vision from YAML file."""
        vision_file = self.repo_root / 'cortex-brain' / 'documents' / 'planning' / 'cortex-4.0-vision.yaml'
        
        if not vision_file.exists():
            print(f"Warning: Vision file not found at {vision_file}", file=sys.stderr)
            return {'strategic_goals': [], 'roadmap': {'milestones': []}}
        
        try:
            import yaml
            with open(vision_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading CORTEX 4.0 vision: {e}", file=sys.stderr)
            return {'strategic_goals': [], 'roadmap': {'milestones': []}}
    
    def extract_nodes_from_goals(self, goals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract nodes from strategic goals."""
        nodes = []
        
        for idx, goal in enumerate(goals):
            node_id = f"goal-{idx}"
            goal_name = goal.get('goal', 'Unknown Goal')
            
            # Determine status (mock data - would be from git/project tracking in real system)
            status = self.infer_status(goal_name, idx)
            
            node = {
                'id': node_id,
                'name': goal_name,
                'type': 'strategic_goal',
                'category': goal.get('category', 'uncategorized'),
                'status': status,
                'priority': self.get_priority_from_index(idx),
                'description': f"{goal_name} - {goal.get('category', '')} capability",
                'metrics': goal.get('success_metrics', {})
            }
            
            nodes.append(node)
            self.node_id_map[goal_name] = node_id
        
        return nodes
    
    def infer_status(self, goal_name: str, index: int) -> str:
        """Infer feature status based on name and position."""
        # Simple heuristic: earlier goals are further along
        if index < 2:
            return 'in-progress'
        elif index < 4:
            return 'planned'
        else:
            return 'future'
    
    def get_priority_from_index(self, index: int) -> str:
        """Determine priority based on strategic goal position."""
        if index < 2:
            return 'HIGH'
        elif index < 4:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def extract_links_from_dependencies(self, goals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract dependency links between goals."""
        links = []
        
        for idx, goal in enumerate(goals):
            source_id = f"goal-{idx}"
            dependencies = goal.get('dependencies', [])
            
            for dep in dependencies:
                # Find target node by dependency name
                target_id = self.find_node_by_name(dep)
                
                if target_id:
                    links.append({
                        'source': source_id,
                        'target': target_id,
                        'type': 'depends_on',
                        'strength': 'strong'
                    })
                else:
                    # Create dependency node if it doesn't exist
                    dep_id = f"dep-{len(self.nodes)}"
                    self.nodes.append({
                        'id': dep_id,
                        'name': dep,
                        'type': 'dependency',
                        'category': 'infrastructure',
                        'status': 'external',
                        'priority': 'MEDIUM',
                        'description': f"External dependency: {dep}"
                    })
                    self.node_id_map[dep] = dep_id
                    
                    links.append({
                        'source': source_id,
                        'target': dep_id,
                        'type': 'depends_on',
                        'strength': 'medium'
                    })
        
        return links
    
    def find_node_by_name(self, name: str) -> str:
        """Find node ID by name (case-insensitive partial match)."""
        name_lower = name.lower()
        
        # Exact match in map
        if name in self.node_id_map:
            return self.node_id_map[name]
        
        # Partial match in existing nodes
        for node in self.nodes:
            if name_lower in node['name'].lower():
                return node['id']
        
        return None
    
    def add_milestone_nodes(self, milestones: List[Dict[str, Any]]) -> None:
        """Add milestone nodes to the graph."""
        for idx, milestone in enumerate(milestones):
            node_id = f"milestone-{idx}"
            
            node = {
                'id': node_id,
                'name': milestone.get('name', f"Milestone {idx+1}"),
                'type': 'milestone',
                'category': 'timeline',
                'status': 'planned',
                'priority': 'HIGH',
                'description': f"Target: {milestone.get('target', 'TBD')}",
                'target_quarter': milestone.get('target', 'TBD')
            }
            
            self.nodes.append(node)
            
            # Link milestone to its key features
            for feature_name in milestone.get('key_features', []):
                feature_id = self.find_node_by_name(feature_name)
                
                if feature_id:
                    self.links.append({
                        'source': feature_id,
                        'target': node_id,
                        'type': 'delivers_in',
                        'strength': 'strong'
                    })
    
    def calculate_graph_statistics(self) -> Dict[str, Any]:
        """Calculate graph metrics."""
        # Count by type
        type_counts = {}
        for node in self.nodes:
            node_type = node['type']
            type_counts[node_type] = type_counts.get(node_type, 0) + 1
        
        # Count by status
        status_counts = {}
        for node in self.nodes:
            status = node['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Analyze dependencies
        dependency_counts = {}
        for node in self.nodes:
            node_id = node['id']
            incoming = len([l for l in self.links if l['target'] == node_id])
            outgoing = len([l for l in self.links if l['source'] == node_id])
            dependency_counts[node_id] = {
                'incoming': incoming,
                'outgoing': outgoing,
                'total': incoming + outgoing
            }
        
        # Find most connected nodes
        sorted_nodes = sorted(
            dependency_counts.items(),
            key=lambda x: x[1]['total'],
            reverse=True
        )[:5]
        
        most_connected = [
            {
                'id': node_id,
                'name': next((n['name'] for n in self.nodes if n['id'] == node_id), 'Unknown'),
                'connections': counts['total']
            }
            for node_id, counts in sorted_nodes
        ]
        
        return {
            'total_nodes': len(self.nodes),
            'total_links': len(self.links),
            'nodes_by_type': type_counts,
            'nodes_by_status': status_counts,
            'most_connected': most_connected,
            'avg_connections_per_node': len(self.links) * 2 / len(self.nodes) if self.nodes else 0
        }
    
    def generate_graph_data(self) -> Dict[str, Any]:
        """Generate complete dependency graph data."""
        print("Loading CORTEX 4.0 vision...")
        vision = self.load_cortex_4_vision()
        
        print("Extracting nodes from strategic goals...")
        goals = vision.get('strategic_goals', [])
        self.nodes = self.extract_nodes_from_goals(goals)
        
        print(f"Extracted {len(self.nodes)} goal nodes")
        
        print("Extracting dependency links...")
        self.links = self.extract_links_from_dependencies(goals)
        
        print(f"Extracted {len(self.links)} dependency links")
        
        print("Adding milestone nodes...")
        milestones = vision.get('roadmap', {}).get('milestones', [])
        self.add_milestone_nodes(milestones)
        
        print(f"Total nodes: {len(self.nodes)}, Total links: {len(self.links)}")
        
        print("Calculating graph statistics...")
        statistics = self.calculate_graph_statistics()
        
        graph_data = {
            'generated_at': datetime.now().isoformat(),
            'nodes': self.nodes,
            'links': self.links,
            'statistics': statistics,
            'metadata': {
                'version': '1.0.0',
                'source': 'CORTEX 4.0 vision YAML',
                'layout': 'force-directed',
                'node_types': list(set(n['type'] for n in self.nodes)),
                'link_types': list(set(l['type'] for l in self.links))
            }
        }
        
        return graph_data
    
    def save_graph_data(self, data: Dict[str, Any]) -> None:
        """Save graph data to JSON file."""
        output_dir = self.repo_root / 'docs' / 'gh-pages' / 'assets' / 'data'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / 'dependency-graph.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Dependency graph data saved to: {output_file}")
        print(f"   Size: {output_file.stat().st_size / 1024:.1f} KB")
    
    def generate_analysis_report(self, data: Dict[str, Any]) -> None:
        """Generate human-readable dependency analysis report."""
        output_dir = self.repo_root / 'cortex-brain' / 'documents' / 'analysis'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / 'dependency-analysis.md'
        
        stats = data['statistics']
        
        report = f"""# CORTEX Dependency Graph Analysis
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Source:** CORTEX 4.0 Vision Strategic Goals  
**Graph Type:** Force-Directed Dependency Network

---

## 📊 Graph Statistics

### Overall Metrics
- **Total Nodes:** {stats['total_nodes']}
- **Total Links:** {stats['total_links']}
- **Average Connections per Node:** {stats['avg_connections_per_node']:.2f}
- **Graph Density:** {(stats['total_links'] / (stats['total_nodes'] * (stats['total_nodes'] - 1))) * 100 if stats['total_nodes'] > 1 else 0:.1f}%

### Nodes by Type
"""
        
        for node_type, count in stats['nodes_by_type'].items():
            percentage = (count / stats['total_nodes']) * 100
            report += f"- **{node_type.replace('_', ' ').title()}:** {count} ({percentage:.1f}%)\n"
        
        report += "\n### Nodes by Status\n"
        
        for status, count in stats['nodes_by_status'].items():
            percentage = (count / stats['total_nodes']) * 100
            report += f"- **{status.replace('_', ' ').title()}:** {count} ({percentage:.1f}%)\n"
        
        report += f"""
---

## 🔗 Most Connected Features

These features have the highest number of dependencies and are critical to the roadmap:

"""
        
        for idx, node in enumerate(stats['most_connected'], 1):
            report += f"{idx}. **{node['name']}** - {node['connections']} connections\n"
        
        report += f"""
---

## 📋 All Nodes

"""
        
        for node in data['nodes']:
            report += f"""### {node['name']}
- **Type:** {node['type'].replace('_', ' ').title()}
- **Category:** {node['category']}
- **Status:** {node['status']}
- **Priority:** {node['priority']}
- **Description:** {node['description']}

"""
        
        report += """---

## 🔄 Dependency Relationships

"""
        
        for link in data['links']:
            source_name = next((n['name'] for n in data['nodes'] if n['id'] == link['source']), 'Unknown')
            target_name = next((n['name'] for n in data['nodes'] if n['id'] == link['target']), 'Unknown')
            report += f"- **{source_name}** {link['type'].replace('_', ' ')} **{target_name}** (strength: {link['strength']})\n"
        
        report += """
---

## 🎯 Key Insights

### Critical Path Analysis
Features with high incoming dependencies should be prioritized to unblock downstream work.

### Dependency Clusters
Features in the same category often depend on each other, suggesting opportunities for parallel development.

### External Dependencies
External dependencies (infrastructure, third-party services) should be validated early to avoid blockers.

---

*This analysis helps identify critical features, potential bottlenecks, and optimal development sequencing.*
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ Dependency analysis report saved to: {output_file}")
        print(f"   Size: {output_file.stat().st_size / 1024:.1f} KB")


def main():
    """Main entry point."""
    repo_root = Path(__file__).parent.parent
    
    print("=" * 70)
    print("CORTEX Dependency Graph Generator")
    print("=" * 70)
    print()
    
    generator = DependencyGraphGenerator(repo_root)
    
    try:
        # Generate graph data
        graph_data = generator.generate_graph_data()
        
        # Save to JSON file
        generator.save_graph_data(graph_data)
        
        # Generate analysis report
        generator.generate_analysis_report(graph_data)
        
        print("\n✅ Dependency graph generation complete!")
        print("\n📊 Summary:")
        print(f"   - Nodes: {graph_data['statistics']['total_nodes']}")
        print(f"   - Links: {graph_data['statistics']['total_links']}")
        print(f"   - Node types: {', '.join(graph_data['metadata']['node_types'])}")
        print(f"   - Link types: {', '.join(graph_data['metadata']['link_types'])}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
