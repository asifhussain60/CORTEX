# AC_START: AC-PHASE59-S4-003
# Dashboard Generator for ML Pattern Visualization
# Purpose: Generate visualization data for clustering results

"""
Dashboard Generator for ML Pattern Clustering

Transforms clustering results and fingerprints into dashboard-ready data.
"""

import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass
class DashboardRepository:
    """Dashboard representation of a repository."""

    id: str
    complexity: float
    modularity: float
    component_count: int
    cluster: int


@dataclass
class DashboardCluster:
    """Dashboard representation of a cluster."""

    id: int
    repository_count: int
    avg_complexity: float
    avg_modularity: float
    repositories: List[str]


class DashboardGenerator:
    """
    Generates visualization data for clustering results.

    Produces:
    - Repository metrics for plotting
    - Cluster metadata
    - Interactive dashboard data
    """

    def generate(
        self,
        fingerprints: Dict[str, Dict[str, Any]],
        clusters: Dict[str, List[str]],
    ) -> Dict[str, Any]:
        """
        Generate dashboard data from fingerprints and clusters.

        Args:
            fingerprints: Dict mapping repo_id to fingerprint data
            clusters: Dict mapping cluster_id (str) to list of repo_ids

        Returns:
            Dashboard data dictionary
        """
        repos = []
        cluster_metrics = {}

        # Process each cluster
        for cluster_id_str, repo_ids in clusters.items():
            cluster_id = int(cluster_id_str)
            cluster_metrics[cluster_id] = {
                "complexity_values": [],
                "modularity_values": [],
                "repos": repo_ids,
            }

            # Process repositories in this cluster
            for repo_id in repo_ids:
                if repo_id not in fingerprints:
                    continue

                fp = fingerprints[repo_id]
                complexity = fp.get("total_complexity", 0.5)
                modularity = fp.get("total_modularity", 0.75)
                component_count = fp.get("component_count", 1)

                repos.append({
                    "id": repo_id,
                    "complexity": complexity,
                    "modularity": modularity,
                    "component_count": component_count,
                    "cluster": cluster_id,
                })

                cluster_metrics[cluster_id]["complexity_values"].append(complexity)
                cluster_metrics[cluster_id]["modularity_values"].append(modularity)

        # Calculate cluster statistics
        clusters_data = []
        for cluster_id, metrics in cluster_metrics.items():
            if metrics["complexity_values"]:
                avg_complexity = sum(metrics["complexity_values"]) / len(
                    metrics["complexity_values"]
                )
                avg_modularity = sum(metrics["modularity_values"]) / len(
                    metrics["modularity_values"]
                )
            else:
                avg_complexity = 0.5
                avg_modularity = 0.75

            clusters_data.append({
                "id": cluster_id,
                "repository_count": len(metrics["repos"]),
                "avg_complexity": avg_complexity,
                "avg_modularity": avg_modularity,
                "repositories": metrics["repos"],
            })

        return {
            "repos": repos,
            "clusters": clusters_data,
            "summary": {
                "total_repositories": len(repos),
                "total_clusters": len(clusters),
                "avg_cluster_size": len(repos) / len(clusters) if clusters else 0,
            },
        }

    def to_json(self, data: Dict[str, Any]) -> str:
        """
        Convert dashboard data to JSON string.

        Args:
            data: Dashboard data dictionary

        Returns:
            JSON string
        """
        return json.dumps(data, indent=2)

    def to_html(self, data: Dict[str, Any]) -> str:
        """
        Generate standalone HTML dashboard.

        Args:
            data: Dashboard data dictionary

        Returns:
            HTML string for visualization
        """
        repos_json = json.dumps(data.get("repos", []))
        clusters_json = json.dumps(data.get("clusters", []))
        summary = data.get("summary", {})

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>CORTEX Pattern Clustering Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f1419; color: #e0e0e0; }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 8px; margin-bottom: 30px; }}
        h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .summary {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 30px; }}
        .metric {{ background: #1e2329; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .metric-label {{ color: #999; margin-top: 8px; font-size: 0.9em; }}
        .repos-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; margin-bottom: 30px; }}
        .repo-card {{ background: #1e2329; padding: 15px; border-radius: 8px; border: 1px solid #2d3139; }}
        .repo-name {{ font-weight: bold; margin-bottom: 10px; }}
        .metric-row {{ display: flex; justify-content: space-between; margin: 5px 0; font-size: 0.9em; }}
        .metric-row .label {{ color: #999; }}
        .metric-row .value {{ color: #667eea; font-weight: 500; }}
        .cluster-section {{ margin-bottom: 30px; }}
        .cluster-title {{ font-size: 1.3em; font-weight: bold; margin-bottom: 15px; padding: 10px; background: #1e2329; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎯 CORTEX Pattern Clustering Dashboard</h1>
            <p>ML-based architectural pattern analysis and repository clustering</p>
        </header>

        <div class="summary">
            <div class="metric">
                <div class="metric-value">{summary.get('total_repositories', 0)}</div>
                <div class="metric-label">Total Repositories</div>
            </div>
            <div class="metric">
                <div class="metric-value">{summary.get('total_clusters', 0)}</div>
                <div class="metric-label">Clusters Found</div>
            </div>
            <div class="metric">
                <div class="metric-value">{summary.get('avg_cluster_size', 0):.1f}</div>
                <div class="metric-label">Avg Cluster Size</div>
            </div>
        </div>

        {self._generate_cluster_sections(data)}

    </div>

    <script>
        const repos = {repos_json};
        const clusters = {clusters_json};
        console.log('Dashboard data loaded:', repos.length, 'repositories,', clusters.length, 'clusters');
    </script>
</body>
</html>
"""
        return html

    def _generate_cluster_sections(self, data: Dict[str, Any]) -> str:
        """Generate HTML for cluster sections."""
        clusters = data.get("clusters", [])
        repos_by_id = {r["id"]: r for r in data.get("repos", [])}

        html = ""
        for cluster in clusters:
            repos_html = ""
            for repo_id in cluster["repositories"]:
                repo = repos_by_id.get(repo_id, {})
                repos_html += f"""
            <div class="repo-card">
                <div class="repo-name">{repo_id}</div>
                <div class="metric-row">
                    <span class="label">Complexity:</span>
                    <span class="value">{repo.get('complexity', 0):.2f}</span>
                </div>
                <div class="metric-row">
                    <span class="label">Modularity:</span>
                    <span class="value">{repo.get('modularity', 0):.2f}</span>
                </div>
                <div class="metric-row">
                    <span class="label">Components:</span>
                    <span class="value">{repo.get('component_count', 0)}</span>
                </div>
            </div>
            """

            html += f"""
        <div class="cluster-section">
            <div class="cluster-title">Cluster {cluster['id']} ({cluster['repository_count']} repos)</div>
            <div class="repos-grid">
                {repos_html}
            </div>
        </div>
        """

        return html


# AC_COMPLETE: AC-PHASE59-S4-003 ✅ Dashboard Generator Implementation
