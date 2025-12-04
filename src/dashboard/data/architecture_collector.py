"""
Architecture Collector

Analyzes project architecture, detects tiers, components, and relationships.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import ast
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from collections import defaultdict

from src.dashboard.data.base_collector import BaseDataCollector


class ArchitectureCollector(BaseDataCollector):
    """
    Collects architecture data from project structure.
    
    Detects:
    - Architecture style (Clean Architecture, MVC, Layered, etc.)
    - Tier structure (presentation, application, domain, infrastructure)
    - Component relationships and dependencies
    - Database schema (tables, relationships)
    
    Data Source: CURRENT STATE ONLY - Real code structure analysis.
    """
    
    def collect(self) -> Optional[Dict[str, Any]]:
        """
        Collect architecture data.
        
        Returns:
            Dict with keys: style, tiers, components, database_schema, summary
        """
        self.logger.info("Collecting architecture data...")
        
        # Detect architecture style
        style = self._detect_architecture_style()
        
        # Analyze tiers
        tiers = self._analyze_tiers()
        
        # Analyze components
        components = self._analyze_components()
        
        # Analyze database schema
        database_schema = self._analyze_database_schema()
        
        architecture_data = {
            "style": style,
            "tiers": tiers,
            "components": components,
            "database_schema": database_schema,
            "summary": {
                "total_components": len(components),
                "total_files": sum(tier["file_count"] for tier in tiers),
                "total_loc": sum(tier["loc"] for tier in tiers),
                "architecture_score": self._calculate_architecture_score(tiers, components)
            }
        }
        
        self.logger.info(f"Architecture analysis complete. Style: {style}")
        return architecture_data
    
    def _detect_architecture_style(self) -> str:
        """
        Detect architecture style from directory structure.
        
        Returns:
            Architecture style name
        """
        src_path = self.project_root / "src"
        if not src_path.exists():
            return "unknown"
        
        # Check for Clean Architecture markers
        if (src_path / "domain").exists() and (src_path / "application").exists():
            return "clean_architecture"
        
        # Check for MVC
        if (src_path / "models").exists() and (src_path / "views").exists() and (src_path / "controllers").exists():
            return "mvc"
        
        # Check for Layered Architecture
        if (src_path / "presentation").exists() or (src_path / "data").exists():
            return "layered_architecture"
        
        # Check for microservices
        if len([d for d in src_path.iterdir() if d.is_dir() and (d / "api").exists()]) > 1:
            return "microservices"
        
        return "modular"
    
    def _analyze_tiers(self) -> List[Dict[str, Any]]:
        """
        Analyze tier structure.
        
        Returns:
            List of tier data (name, path, file_count, loc)
        """
        tiers = []
        src_path = self.project_root / "src"
        
        if not src_path.exists():
            return tiers
        
        # Common tier names
        tier_names = {
            "presentation": ["presentation", "ui", "views", "templates"],
            "application": ["application", "use_cases", "services", "orchestrators"],
            "domain": ["domain", "models", "entities", "core"],
            "infrastructure": ["infrastructure", "data", "repositories", "persistence"],
            "api": ["api", "controllers", "endpoints"]
        }
        
        for tier_type, possible_names in tier_names.items():
            for name in possible_names:
                tier_path = src_path / name
                if tier_path.exists() and tier_path.is_dir():
                    file_count = len(list(tier_path.glob("**/*.py")))
                    loc = self._count_loc_in_directory(tier_path)
                    
                    tiers.append({
                        "name": tier_type,
                        "path": str(tier_path.relative_to(self.project_root)),
                        "file_count": file_count,
                        "loc": loc,
                        "directories": [str(d.name) for d in tier_path.iterdir() if d.is_dir()][:10]
                    })
                    break  # Only add first match per tier type
        
        return tiers
    
    def _analyze_components(self) -> List[Dict[str, Any]]:
        """
        Analyze components and their dependencies.
        
        Returns:
            List of component data
        """
        components = []
        src_path = self.project_root / "src"
        
        if not src_path.exists():
            return components
        
        # Find major components (directories with Python files)
        for component_dir in src_path.iterdir():
            if not component_dir.is_dir() or component_dir.name.startswith('.'):
                continue
            
            py_files = list(component_dir.glob("**/*.py"))
            if not py_files:
                continue
            
            # Determine tier
            tier = self._determine_tier(component_dir.name)
            
            # Count LOC
            loc = self._count_loc_in_directory(component_dir)
            
            # Detect dependencies
            dependencies = self._detect_dependencies(py_files)
            
            components.append({
                "name": component_dir.name,
                "tier": tier,
                "loc": loc,
                "file_count": len(py_files),
                "dependencies": list(dependencies)[:20],  # Limit to top 20
                "path": str(component_dir.relative_to(self.project_root))
            })
        
        return components
    
    def _analyze_database_schema(self) -> Dict[str, Any]:
        """
        Analyze database schema from SQLite files and SQLAlchemy models.
        
        Returns:
            Dict with tables and relationships
        """
        schema = {
            "tables": [],
            "relationships": []
        }
        
        # Find SQLite databases
        db_files = list(self.project_root.glob("**/*.db"))
        
        if db_files:
            import sqlite3
            try:
                conn = sqlite3.connect(str(db_files[0]))
                cursor = conn.cursor()
                
                # Get table names
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                for table in tables:
                    # Get column info
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = cursor.fetchall()
                    
                    schema["tables"].append({
                        "name": table,
                        "column_count": len(columns),
                        "columns": [col[1] for col in columns][:10]  # Limit to 10 columns
                    })
                
                conn.close()
                
            except Exception as e:
                self.logger.warning(f"Error analyzing database: {e}")
        
        # Detect relationships from foreign keys or naming patterns
        for table in schema["tables"]:
            for column in table.get("columns", []):
                if column.endswith("_id"):
                    # Infer relationship from column name
                    related_table = column[:-3] + "s"  # Simple pluralization
                    if any(t["name"] == related_table for t in schema["tables"]):
                        schema["relationships"].append({
                            "from": table["name"],
                            "to": related_table,
                            "type": "many_to_one"
                        })
        
        return schema
    
    def _count_loc_in_directory(self, directory: Path) -> int:
        """Count lines of code in directory (excluding comments and blanks)."""
        total_loc = 0
        
        for py_file in directory.glob("**/*.py"):
            try:
                content = py_file.read_text()
                lines = content.split('\n')
                
                # Count non-blank, non-comment lines
                for line in lines:
                    stripped = line.strip()
                    if stripped and not stripped.startswith('#'):
                        total_loc += 1
                        
            except Exception:
                continue
        
        return total_loc
    
    def _determine_tier(self, directory_name: str) -> str:
        """Determine tier from directory name."""
        tier_mapping = {
            "presentation": "presentation",
            "ui": "presentation",
            "views": "presentation",
            "templates": "presentation",
            "application": "application",
            "use_cases": "application",
            "services": "application",
            "orchestrators": "application",
            "domain": "domain",
            "models": "domain",
            "entities": "domain",
            "core": "domain",
            "infrastructure": "infrastructure",
            "data": "infrastructure",
            "repositories": "infrastructure",
            "api": "api",
            "controllers": "api",
            "endpoints": "api"
        }
        
        return tier_mapping.get(directory_name.lower(), "other")
    
    def _detect_dependencies(self, py_files: List[Path]) -> Set[str]:
        """
        Detect dependencies from import statements.
        
        Args:
            py_files: List of Python files to analyze
            
        Returns:
            Set of dependency module names
        """
        dependencies = set()
        
        for py_file in py_files[:50]:  # Limit to first 50 files for performance
            try:
                content = py_file.read_text()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            # Extract top-level module
                            module = alias.name.split('.')[0]
                            if not module.startswith('src'):  # External dependency
                                dependencies.add(module)
                    
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            module = node.module.split('.')[0]
                            if not module.startswith('src'):
                                dependencies.add(module)
                                
            except Exception:
                continue
        
        return dependencies
    
    def _calculate_architecture_score(
        self, 
        tiers: List[Dict[str, Any]], 
        components: List[Dict[str, Any]]
    ) -> int:
        """
        Calculate architecture quality score.
        
        Args:
            tiers: List of tier data
            components: List of component data
            
        Returns:
            Score 0-100
        """
        score = 70  # Base score
        
        # Bonus for having multiple tiers (separation of concerns)
        if len(tiers) >= 3:
            score += 10
        
        # Bonus for balanced LOC across tiers (no mega-tier)
        if tiers:
            max_loc = max(t["loc"] for t in tiers) if tiers else 0
            avg_loc = sum(t["loc"] for t in tiers) / len(tiers) if tiers else 0
            if avg_loc > 0 and max_loc / avg_loc < 3:  # No tier > 3x average
                score += 10
        
        # Bonus for modular components
        if len(components) >= 5:
            score += 10
        
        return min(score, 100)
