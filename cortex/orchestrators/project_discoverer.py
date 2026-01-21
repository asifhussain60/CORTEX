"""Project Discoverer - PHASE-DEPLOYMENT-004-multi-repo-gov.

Discovers and registers projects under D:\\PROJECTS\\*.

Author: CORTEX Framework
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import sqlite3


class ProjectDiscoverer:
    """Discovers projects and registers them in projects.db.
    
    Scans D:\\PROJECTS\\* for project directories, detects project type,
    and registers with appropriate tier1 profile.
    """
    
    # Project type indicators
    TYPE_INDICATORS = {
        "finops": ["financial", "payment", "billing", "invoice", "kashkole", "finance"],
        "auth": ["session", "auth", "login", "identity", "ksessions", "oauth"],
        "ml": ["model", "training", "ml", "ai", "neural", "predict"],
        "devops": ["ci", "cd", "pipeline", "deploy", "infra", "k8s"],
        "healthcare": ["health", "medical", "patient", "hipaa", "ehr"],
        "legal": ["legal", "contract", "compliance", "gdpr"],
    }
    
    def __init__(self, db_path: str = "cortex_brain/state/projects.db"):
        """Initialize project discoverer.
        
        Args:
            db_path: Path to projects database.
        """
        self.db_path = db_path
    
    def scan(self, base_path: str = "D:\\PROJECTS") -> List[Dict[str, Any]]:
        """Scan base path for projects.
        
        Args:
            base_path: Base directory to scan.
            
        Returns:
            List of discovered project metadata.
        """
        directories = self._list_directories(base_path)
        
        # Filter hidden directories
        directories = [d for d in directories if not d.startswith(".")]
        
        projects = []
        for dir_name in directories:
            project_info = self._analyze_project(base_path, dir_name)
            projects.append(project_info)
        
        return projects
    
    def _list_directories(self, base_path: str) -> List[str]:
        """List directory names under base path.
        
        Args:
            base_path: Path to list.
            
        Returns:
            List of directory names.
        """
        try:
            path = Path(base_path)
            if not path.exists():
                return []
            return [p.name for p in path.iterdir() if p.is_dir()]
        except Exception:
            return []
    
    def _analyze_project(self, base_path: str, dir_name: str) -> Dict[str, Any]:
        """Analyze a project directory.
        
        Args:
            base_path: Parent directory.
            dir_name: Project directory name.
            
        Returns:
            Project metadata.
        """
        project_path = f"{base_path}\\{dir_name}"
        
        # Detect indicators from project structure
        indicators = self._detect_indicators(project_path, dir_name)
        
        return {
            "name": dir_name,
            "path": project_path,
            "type": self.infer_project_type(dir_name, indicators),
            "has_cortex_config": self.has_cortex_config(project_path),
            "indicators": indicators,
        }
    
    def _detect_indicators(self, project_path: str, project_name: str) -> List[str]:
        """Detect project type indicators.
        
        Args:
            project_path: Path to project.
            project_name: Project directory name.
            
        Returns:
            List of detected indicators.
        """
        indicators = [project_name.lower()]
        
        path = Path(project_path)
        
        # Check for common indicators
        if (path / "requirements.txt").exists():
            try:
                content = (path / "requirements.txt").read_text().lower()
                for keyword in ["pandas", "numpy", "sklearn", "tensorflow", "torch"]:
                    if keyword in content:
                        indicators.append("ml")
                        break
            except Exception:
                pass
        
        # Check README for keywords
        for readme in ["README.md", "readme.md", "README.txt"]:
            readme_path = path / readme
            if readme_path.exists():
                try:
                    content = readme_path.read_text().lower()
                    for type_name, keywords in self.TYPE_INDICATORS.items():
                        for keyword in keywords:
                            if keyword in content:
                                indicators.append(type_name)
                                break
                except Exception:
                    pass
                break
        
        return list(set(indicators))
    
    def has_cortex_config(self, project_path: str) -> bool:
        """Check if project has CORTEX config marker.
        
        Args:
            project_path: Path to project.
            
        Returns:
            True if .cortex-config.yaml exists.
        """
        config_paths = [
            Path(project_path) / ".cortex-config.yaml",
            Path(project_path) / ".cortex-version",
            Path(project_path) / "cortex-config.yaml",
        ]
        
        return any(p.exists() for p in config_paths)
    
    def infer_project_type(
        self,
        project_name: str,
        indicators: List[str] = None,
    ) -> str:
        """Infer project type from name and indicators.
        
        Args:
            project_name: Project name.
            indicators: List of detected indicators.
            
        Returns:
            Inferred project type.
        """
        if indicators is None:
            indicators = []
        
        # Combine name and indicators for matching
        all_indicators = [project_name.lower()] + [i.lower() for i in indicators]
        
        for type_name, keywords in self.TYPE_INDICATORS.items():
            for keyword in keywords:
                if any(keyword in ind for ind in all_indicators):
                    return type_name
        
        return "general"
    
    def register_project(
        self,
        project: Dict[str, Any],
        update_existing: bool = False,
    ) -> bool:
        """Register project in database.
        
        Args:
            project: Project metadata to register.
            update_existing: Whether to update if exists.
            
        Returns:
            True if successful.
        """
        if update_existing:
            return self._db_upsert(project)
        return self._db_insert(project)
    
    def _db_insert(self, project: Dict[str, Any]) -> bool:
        """Insert project into database.
        
        Args:
            project: Project metadata.
            
        Returns:
            True if successful.
        """
        try:
            # Ensure directory exists
            db_path = Path(self.db_path)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    project_id TEXT PRIMARY KEY,
                    path TEXT,
                    type TEXT,
                    tier1_profile TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute(
                "INSERT INTO projects (project_id, path, type, tier1_profile) VALUES (?, ?, ?, ?)",
                (
                    project.get("project_id", project.get("name")),
                    project.get("path"),
                    project.get("type"),
                    project.get("tier1_profile", project.get("type")),
                )
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False
    
    def _db_upsert(self, project: Dict[str, Any]) -> bool:
        """Upsert project in database.
        
        Args:
            project: Project metadata.
            
        Returns:
            True if successful.
        """
        try:
            db_path = Path(self.db_path)
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    project_id TEXT PRIMARY KEY,
                    path TEXT,
                    type TEXT,
                    tier1_profile TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute(
                """INSERT OR REPLACE INTO projects 
                   (project_id, path, type, tier1_profile) 
                   VALUES (?, ?, ?, ?)""",
                (
                    project.get("project_id", project.get("name")),
                    project.get("path"),
                    project.get("type"),
                    project.get("tier1_profile", project.get("type")),
                )
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception:
            return False


__all__ = ["ProjectDiscoverer"]
