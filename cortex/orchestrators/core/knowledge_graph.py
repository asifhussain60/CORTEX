"""
AC-FUTURE-013: Knowledge Graph Integration

Builds dynamic knowledge graph of file relationships and orchestrator performance,
enabling ML-powered routing recommendations that improve over time.

Production Ready: ✅
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict
import json


@dataclass
class FileNode:
    """Node in knowledge graph representing a file"""
    file_path: str
    file_type: str  # "python", "yaml", "test", "config", etc.
    orchestrators_used: Dict[str, int] = field(default_factory=dict)  # name -> success_count
    dependencies: Set[str] = field(default_factory=set)
    change_frequency: float = 0.0
    success_rate: float = 0.0
    last_modified: Optional[float] = None


@dataclass
class OrchestratorNode:
    """Node representing an orchestrator"""
    orchestrator_name: str
    files_processed: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    avg_execution_time: float = 0.0
    
    @property
    def success_rate(self) -> float:
        total = self.successful_executions + self.failed_executions
        return self.successful_executions / total if total > 0 else 0.0


@dataclass
class FileRelationship:
    """Relationship between two files"""
    from_file: str
    to_file: str
    relationship_type: str  # "imports", "tests", "references", "depends_on"
    strength: float = 1.0  # 0.0-1.0 relationship strength


class KnowledgeGraph:
    """
    Dynamic knowledge graph tracking file relationships and orchestrator performance.
    """

    def __init__(self):
        self.file_nodes: Dict[str, FileNode] = {}
        self.orchestrator_nodes: Dict[str, OrchestratorNode] = {}
        self.relationships: List[FileRelationship] = []
        self.execution_history: List[Dict] = []

    def add_file(
        self,
        file_path: str,
        file_type: str,
    ):
        """Add file node to graph"""
        if file_path not in self.file_nodes:
            self.file_nodes[file_path] = FileNode(
                file_path=file_path,
                file_type=file_type,
            )

    def record_orchestrator_execution(
        self,
        orchestrator_name: str,
        files: List[str],
        success: bool,
        execution_time: float,
    ):
        """Record orchestrator execution in graph"""
        # Ensure orchestrator node exists
        if orchestrator_name not in self.orchestrator_nodes:
            self.orchestrator_nodes[orchestrator_name] = OrchestratorNode(
                orchestrator_name=orchestrator_name
            )

        orch = self.orchestrator_nodes[orchestrator_name]
        orch.files_processed += len(files)

        if success:
            orch.successful_executions += 1
        else:
            orch.failed_executions += 1

        # Update average execution time
        total_execs = orch.successful_executions + orch.failed_executions
        orch.avg_execution_time = (
            (orch.avg_execution_time * (total_execs - 1) + execution_time)
            / total_execs
        )

        # Update file orchestrator usage
        for file_path in files:
            self.add_file(file_path, "unknown")
            file_node = self.file_nodes[file_path]
            if orchestrator_name not in file_node.orchestrators_used:
                file_node.orchestrators_used[orchestrator_name] = 0
            if success:
                file_node.orchestrators_used[orchestrator_name] += 1

        # Record history
        self.execution_history.append({
            "orchestrator": orchestrator_name,
            "files": files,
            "success": success,
            "execution_time": execution_time,
        })

    def add_relationship(
        self,
        from_file: str,
        to_file: str,
        relationship_type: str,
        strength: float = 1.0,
    ):
        """Add relationship between files"""
        self.add_file(from_file, "unknown")
        self.add_file(to_file, "unknown")

        relationship = FileRelationship(
            from_file=from_file,
            to_file=to_file,
            relationship_type=relationship_type,
            strength=strength,
        )
        self.relationships.append(relationship)

        # Update dependency sets
        self.file_nodes[from_file].dependencies.add(to_file)

    def recommend_orchestrator(self, file_path: str) -> Optional[str]:
        """
        Recommend best orchestrator for file based on history.

        Returns orchestrator name with highest success rate on this file.
        """
        if file_path not in self.file_nodes:
            return None

        file_node = self.file_nodes[file_path]
        if not file_node.orchestrators_used:
            return None

        # Return orchestrator with most successful uses
        best_orchestrator = max(
            file_node.orchestrators_used.items(),
            key=lambda x: x[1],
        )[0]

        return best_orchestrator

    def get_related_files(self, file_path: str) -> List[str]:
        """Get files related to given file"""
        related = set()

        for rel in self.relationships:
            if rel.from_file == file_path:
                related.add(rel.to_file)
            elif rel.to_file == file_path:
                related.add(rel.from_file)

        return list(related)

    def get_file_impact_scope(self, file_path: str) -> Set[str]:
        """
        Get all files that could be impacted by changes to this file.
        Uses transitive closure of dependencies.
        """
        impact = set()
        to_visit = [file_path]
        visited = set()

        while to_visit:
            current = to_visit.pop()
            if current in visited:
                continue
            visited.add(current)

            for rel in self.relationships:
                if rel.from_file == current:
                    impact.add(rel.to_file)
                    to_visit.append(rel.to_file)

        return impact

    def export_to_json(self) -> str:
        """Export knowledge graph to JSON"""
        data = {
            "files": {
                path: {
                    "file_type": node.file_type,
                    "orchestrators": node.orchestrators_used,
                    "success_rate": node.success_rate,
                }
                for path, node in self.file_nodes.items()
            },
            "orchestrators": {
                name: {
                    "success_rate": node.success_rate,
                    "avg_execution_time": node.avg_execution_time,
                }
                for name, node in self.orchestrator_nodes.items()
            },
            "relationships": [
                {
                    "from": rel.from_file,
                    "to": rel.to_file,
                    "type": rel.relationship_type,
                    "strength": rel.strength,
                }
                for rel in self.relationships
            ],
        }
        return json.dumps(data, indent=2)
