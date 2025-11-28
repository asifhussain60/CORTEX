"""
Sync Operation Visual Feedback System

Provides real-time visualization for sync/commit operations with network diagram
and file flow representation.

Author: Asif Hussain
Created: 2025-11-28
Version: 1.0.0
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path


class SyncVisualizer:
    """
    Visual feedback for sync/commit operations.
    
    Features:
    - Network diagram showing local ↔ remote synchronization
    - File flow visualization (added/modified/deleted)
    - Operation status indicators (pull, merge, push)
    - Conflict detection and resolution visualization
    - Real-time progress updates via WebSocket
    """
    
    def __init__(self, operation_id: str):
        """
        Initialize sync visualizer.
        
        Args:
            operation_id: Unique identifier for this sync operation
        """
        self.operation_id = operation_id
        self.start_time = datetime.now()
        self.files_data: List[Dict[str, Any]] = []
        self.operations_data: List[Dict[str, Any]] = []
        self.conflicts_data: List[Dict[str, Any]] = []
        self.metrics = {
            'files_added': 0,
            'files_modified': 0,
            'files_deleted': 0,
            'conflicts_detected': 0,
            'conflicts_resolved': 0,
            'total_duration': 0
        }
    
    def track_file_change(
        self,
        file_path: str,
        change_type: str,
        size_bytes: int,
        status: str = 'pending'
    ) -> None:
        """
        Track a file change during sync operation.
        
        Args:
            file_path: Path to the file
            change_type: 'added', 'modified', or 'deleted'
            size_bytes: File size in bytes
            status: Current status ('pending', 'syncing', 'complete', 'failed')
        """
        self.files_data.append({
            'id': f"file-{len(self.files_data)}",
            'path': file_path,
            'type': change_type,
            'size': size_bytes,
            'status': status,
            'timestamp': datetime.now().isoformat()
        })
        
        # Update metrics
        if change_type == 'added':
            self.metrics['files_added'] += 1
        elif change_type == 'modified':
            self.metrics['files_modified'] += 1
        elif change_type == 'deleted':
            self.metrics['files_deleted'] += 1
    
    def track_operation(
        self,
        operation_name: str,
        status: str,
        duration_ms: float = 0.0,
        message: str = ""
    ) -> None:
        """
        Track a sync operation step (pull, merge, push).
        
        Args:
            operation_name: Name of operation ('pull', 'merge', 'push', 'commit')
            status: Operation status ('pending', 'running', 'complete', 'failed')
            duration_ms: Operation duration in milliseconds
            message: Status message or error description
        """
        self.operations_data.append({
            'id': f"op-{len(self.operations_data)}",
            'name': operation_name,
            'status': status,
            'duration': duration_ms,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
    
    def track_conflict(
        self,
        file_path: str,
        conflict_type: str,
        resolution: Optional[str] = None
    ) -> None:
        """
        Track a merge conflict.
        
        Args:
            file_path: Path to conflicted file
            conflict_type: Type of conflict ('content', 'rename', 'delete')
            resolution: How conflict was resolved (None if unresolved)
        """
        conflict_id = f"conflict-{len(self.conflicts_data)}"
        self.conflicts_data.append({
            'id': conflict_id,
            'file': file_path,
            'type': conflict_type,
            'resolution': resolution,
            'status': 'resolved' if resolution else 'unresolved',
            'timestamp': datetime.now().isoformat()
        })
        
        # Update metrics
        self.metrics['conflicts_detected'] += 1
        if resolution:
            self.metrics['conflicts_resolved'] += 1
    
    def generate_network_diagram_data(self) -> Dict[str, Any]:
        """
        Generate data for D3.js network diagram.
        
        Returns:
            Dict with nodes and links for network visualization
        """
        nodes = [
            {'id': 'local', 'label': 'Local Repository', 'type': 'source'},
            {'id': 'remote', 'label': 'Remote Repository', 'type': 'target'}
        ]
        
        links = []
        
        # Add file nodes and links based on operations
        for op in self.operations_data:
            if op['name'] == 'push':
                links.append({
                    'source': 'local',
                    'target': 'remote',
                    'label': f"Push ({self.metrics['files_added'] + self.metrics['files_modified']} files)",
                    'status': op['status'],
                    'type': 'push'
                })
            elif op['name'] == 'pull':
                links.append({
                    'source': 'remote',
                    'target': 'local',
                    'label': 'Pull (sync)',
                    'status': op['status'],
                    'type': 'pull'
                })
        
        return {
            'nodes': nodes,
            'links': links,
            'metadata': {
                'operation_id': self.operation_id,
                'total_files': len(self.files_data),
                'conflicts': len(self.conflicts_data)
            }
        }
    
    def generate_file_flow_data(self) -> Dict[str, Any]:
        """
        Generate data for file flow visualization.
        
        Returns:
            Dict with file changes grouped by type
        """
        return {
            'added': [f for f in self.files_data if f['type'] == 'added'],
            'modified': [f for f in self.files_data if f['type'] == 'modified'],
            'deleted': [f for f in self.files_data if f['type'] == 'deleted'],
            'total_size_bytes': sum(f['size'] for f in self.files_data),
            'metrics': self.metrics
        }
    
    def generate_operations_timeline(self) -> List[Dict[str, Any]]:
        """
        Generate timeline data for operation steps.
        
        Returns:
            List of operations with timestamps and durations
        """
        return sorted(self.operations_data, key=lambda x: x['timestamp'])
    
    def generate_conflicts_summary(self) -> Dict[str, Any]:
        """
        Generate conflict resolution summary.
        
        Returns:
            Dict with conflict data and resolution status
        """
        return {
            'conflicts': self.conflicts_data,
            'total': len(self.conflicts_data),
            'resolved': self.metrics['conflicts_resolved'],
            'unresolved': self.metrics['conflicts_detected'] - self.metrics['conflicts_resolved'],
            'resolution_rate': (
                self.metrics['conflicts_resolved'] / self.metrics['conflicts_detected'] * 100
                if self.metrics['conflicts_detected'] > 0 else 100.0
            )
        }
    
    def generate_websocket_message(self, event_type: str) -> Dict[str, Any]:
        """
        Generate WebSocket message for real-time updates.
        
        Args:
            event_type: Type of event ('file_change', 'operation_update', 'conflict_detected')
        
        Returns:
            WebSocket message dict
        """
        self.metrics['total_duration'] = (datetime.now() - self.start_time).total_seconds()
        
        return {
            'type': 'sync_update',
            'operation_id': self.operation_id,
            'event_type': event_type,
            'timestamp': datetime.now().isoformat(),
            'data': {
                'network_diagram': self.generate_network_diagram_data(),
                'file_flow': self.generate_file_flow_data(),
                'operations': self.generate_operations_timeline(),
                'conflicts': self.generate_conflicts_summary(),
                'metrics': self.metrics
            }
        }
    
    def generate_html_dashboard(self, output_path: Path) -> str:
        """
        Generate HTML dashboard with sync visualization.
        
        Args:
            output_path: Path to save HTML file
        
        Returns:
            Path to generated HTML file
        """
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sync Operation - {self.operation_id}</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            color: #0066cc;
        }}
        .metric-label {{
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }}
        #network-diagram, #file-flow, #operations-timeline, #conflicts {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .node {{
            stroke: #fff;
            stroke-width: 2px;
        }}
        .node.source {{
            fill: #0066cc;
        }}
        .node.target {{
            fill: #00cc66;
        }}
        .link {{
            stroke: #999;
            stroke-width: 2px;
        }}
        .link.push {{
            stroke: #0066cc;
        }}
        .link.pull {{
            stroke: #00cc66;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Sync Operation Dashboard</h1>
        <p>Operation ID: {self.operation_id} | Duration: {self.metrics['total_duration']:.2f}s</p>
        
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value">{self.metrics['files_added']}</div>
                <div class="metric-label">Files Added</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{self.metrics['files_modified']}</div>
                <div class="metric-label">Files Modified</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{self.metrics['files_deleted']}</div>
                <div class="metric-label">Files Deleted</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{self.metrics['conflicts_resolved']}/{self.metrics['conflicts_detected']}</div>
                <div class="metric-label">Conflicts Resolved</div>
            </div>
        </div>
        
        <div id="network-diagram">
            <h2>Network Diagram</h2>
            <svg width="800" height="400"></svg>
        </div>
        
        <div id="file-flow">
            <h2>File Changes</h2>
            <div id="file-flow-chart"></div>
        </div>
        
        <div id="operations-timeline">
            <h2>Operations Timeline</h2>
            <div id="timeline-chart"></div>
        </div>
        
        <div id="conflicts">
            <h2>Conflicts</h2>
            <div id="conflicts-list"></div>
        </div>
    </div>
    
    <script>
        // Network diagram data
        const networkData = {json.dumps(self.generate_network_diagram_data(), indent=2)};
        
        // Render network diagram
        const svg = d3.select("#network-diagram svg");
        const width = 800;
        const height = 400;
        
        const simulation = d3.forceSimulation(networkData.nodes)
            .force("link", d3.forceLink(networkData.links).id(d => d.id))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2));
        
        const link = svg.append("g")
            .selectAll("line")
            .data(networkData.links)
            .join("line")
            .attr("class", d => `link ${{d.type}}`)
            .attr("stroke-dasharray", d => d.status === 'complete' ? '0' : '5,5');
        
        const node = svg.append("g")
            .selectAll("circle")
            .data(networkData.nodes)
            .join("circle")
            .attr("class", d => `node ${{d.type}}`)
            .attr("r", 30)
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));
        
        const label = svg.append("g")
            .selectAll("text")
            .data(networkData.nodes)
            .join("text")
            .text(d => d.label)
            .attr("font-size", 12)
            .attr("dx", 35);
        
        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            
            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
            
            label
                .attr("x", d => d.x)
                .attr("y", d => d.y);
        }});
        
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}
        
        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}
        
        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
        
        // File flow data
        const fileFlowData = {json.dumps(self.generate_file_flow_data(), indent=2)};
        
        // Render file flow (simple table for now)
        const fileFlowDiv = d3.select("#file-flow-chart");
        fileFlowDiv.html(`
            <table style="width:100%; border-collapse: collapse;">
                <tr>
                    <th style="border-bottom: 2px solid #ddd; padding: 10px; text-align: left;">Type</th>
                    <th style="border-bottom: 2px solid #ddd; padding: 10px; text-align: left;">Count</th>
                    <th style="border-bottom: 2px solid #ddd; padding: 10px; text-align: left;">Total Size</th>
                </tr>
                <tr>
                    <td style="padding: 10px;">Added</td>
                    <td style="padding: 10px;">${{fileFlowData.added.length}}</td>
                    <td style="padding: 10px;">${{(fileFlowData.added.reduce((sum, f) => sum + f.size, 0) / 1024).toFixed(2)}} KB</td>
                </tr>
                <tr>
                    <td style="padding: 10px;">Modified</td>
                    <td style="padding: 10px;">${{fileFlowData.modified.length}}</td>
                    <td style="padding: 10px;">${{(fileFlowData.modified.reduce((sum, f) => sum + f.size, 0) / 1024).toFixed(2)}} KB</td>
                </tr>
                <tr>
                    <td style="padding: 10px;">Deleted</td>
                    <td style="padding: 10px;">${{fileFlowData.deleted.length}}</td>
                    <td style="padding: 10px;">-</td>
                </tr>
            </table>
        `);
    </script>
</body>
</html>
"""
        
        output_path.write_text(html_content, encoding='utf-8')
        return str(output_path)


if __name__ == "__main__":
    # Example usage
    visualizer = SyncVisualizer("sync-20251128-001")
    
    # Simulate sync operations
    visualizer.track_operation("commit", "complete", 150.0, "Committed 5 files")
    visualizer.track_operation("pull", "running", 0.0, "Pulling from origin...")
    
    # Simulate file changes
    visualizer.track_file_change("src/main.py", "modified", 5120, "complete")
    visualizer.track_file_change("tests/test_new.py", "added", 2048, "complete")
    visualizer.track_file_change("old_file.txt", "deleted", 0, "complete")
    
    # Simulate conflict
    visualizer.track_conflict("src/config.py", "content", "manual merge")
    
    # Generate outputs
    print("WebSocket Message:")
    print(json.dumps(visualizer.generate_websocket_message("operation_update"), indent=2))
    
    output_file = Path("sync-dashboard-example.html")
    html_path = visualizer.generate_html_dashboard(output_file)
    print(f"\nGenerated HTML dashboard: {html_path}")
