"""
Code Organization Collector

Analyzes code organization, complexity, and identifies hotspots.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import ast
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import subprocess

from src.dashboard.data.base_collector import BaseDataCollector


class CodeOrganizationCollector(BaseDataCollector):
    """
    Collects code organization metrics and identifies hotspots.
    
    Analyzes:
    - File complexity (cyclomatic complexity, LOC)
    - Change frequency (git history)
    - Hotspot identification (high complexity + high change frequency)
    - Module structure
    
    Data Source: CURRENT STATE ONLY - Real code metrics from analysis.
    """
    
    def collect(self) -> Optional[Dict[str, Any]]:
        """
        Collect code organization data.
        
        Returns:
            Dict with keys: heatmap, hotspots, module_structure, summary
        """
        self.logger.info("Collecting code organization data...")
        
        # Generate complexity heatmap
        heatmap = self._generate_heatmap()
        
        # Identify hotspots
        hotspots = self._identify_hotspots(heatmap)
        
        # Analyze module structure
        module_structure = self._analyze_module_structure()
        
        code_org_data = {
            "heatmap": heatmap,
            "hotspots": hotspots,
            "module_structure": module_structure,
            "summary": {
                "total_files": len(heatmap),
                "high_complexity_files": len([f for f in heatmap if f["complexity"] > 20]),
                "hotspot_count": len(hotspots),
                "avg_complexity": sum(f["complexity"] for f in heatmap) / len(heatmap) if heatmap else 0
            }
        }
        
        self.logger.info(f"Code organization analysis complete. {len(hotspots)} hotspots identified")
        return code_org_data
    
    def _generate_heatmap(self) -> List[Dict[str, Any]]:
        """
        Generate complexity heatmap for all Python files.
        
        Returns:
            List of file data with complexity, LOC, change frequency
        """
        heatmap = []
        src_path = self.project_root / "src"
        
        if not src_path.exists():
            return heatmap
        
        # Analyze all Python files
        for py_file in src_path.glob("**/*.py"):
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue
            
            try:
                complexity = self._calculate_complexity(py_file)
                loc = self._count_loc(py_file)
                change_freq = self._get_change_frequency(py_file)
                last_modified = self._get_last_modified(py_file)
                
                # Calculate risk score (complexity × change_frequency)
                risk_score = min(complexity * (change_freq / 10), 100)
                
                heatmap.append({
                    "file": str(py_file.relative_to(self.project_root)),
                    "complexity": complexity,
                    "loc": loc,
                    "change_frequency": change_freq,
                    "last_modified": last_modified,
                    "risk_score": int(risk_score)
                })
                
            except Exception as e:
                self.logger.debug(f"Error analyzing {py_file}: {e}")
                continue
        
        # Sort by risk score descending
        heatmap.sort(key=lambda x: x["risk_score"], reverse=True)
        
        return heatmap
    
    def _calculate_complexity(self, file_path: Path) -> int:
        """
        Calculate cyclomatic complexity for a file.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            Cyclomatic complexity score
        """
        try:
            content = file_path.read_text()
            tree = ast.parse(content)
            
            complexity = 1  # Base complexity
            
            for node in ast.walk(tree):
                # Count decision points
                if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                    complexity += 1
                elif isinstance(node, ast.BoolOp):
                    complexity += len(node.values) - 1
                elif isinstance(node, (ast.And, ast.Or)):
                    complexity += 1
            
            return complexity
            
        except Exception as e:
            self.logger.debug(f"Error calculating complexity for {file_path}: {e}")
            return 0
    
    def _count_loc(self, file_path: Path) -> int:
        """Count lines of code (excluding comments and blanks)."""
        try:
            content = file_path.read_text()
            lines = content.split('\n')
            
            loc = 0
            for line in lines:
                stripped = line.strip()
                if stripped and not stripped.startswith('#'):
                    loc += 1
            
            return loc
            
        except Exception:
            return 0
    
    def _get_change_frequency(self, file_path: Path) -> int:
        """
        Get change frequency from git history.
        
        Args:
            file_path: Path to file
            
        Returns:
            Number of commits modifying this file
        """
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "--", str(file_path)],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
            
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass
        
        return 0
    
    def _get_last_modified(self, file_path: Path) -> str:
        """
        Get last modified date from git.
        
        Args:
            file_path: Path to file
            
        Returns:
            ISO format date string
        """
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%ai", "--", str(file_path)],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split()[0]
            
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass
        
        # Fallback to file system modification time
        try:
            mtime = file_path.stat().st_mtime
            return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
        except Exception:
            return "unknown"
    
    def _identify_hotspots(self, heatmap: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify hotspots (high complexity + high change frequency).
        
        Args:
            heatmap: List of file data
            
        Returns:
            List of hotspot files
        """
        # Files with risk score > 50 are considered hotspots
        hotspots = [
            {
                "file": f["file"],
                "risk_score": f["risk_score"],
                "complexity": f["complexity"],
                "change_frequency": f["change_frequency"],
                "recommendation": self._generate_recommendation(f)
            }
            for f in heatmap 
            if f["risk_score"] > 50
        ]
        
        return hotspots[:20]  # Top 20 hotspots
    
    def _generate_recommendation(self, file_data: Dict[str, Any]) -> str:
        """
        Generate refactoring recommendation for a file.
        
        Args:
            file_data: File metrics data
            
        Returns:
            Recommendation string
        """
        complexity = file_data["complexity"]
        change_freq = file_data["change_frequency"]
        loc = file_data["loc"]
        
        if complexity > 50 and loc > 500:
            return "High complexity & large file - consider splitting into smaller modules"
        elif complexity > 30:
            return "High complexity - refactor to reduce cyclomatic complexity"
        elif change_freq > 50:
            return "Frequent changes - stabilize with comprehensive tests"
        elif loc > 1000:
            return "Large file - consider breaking into smaller components"
        else:
            return "Monitor for complexity growth"
    
    def _analyze_module_structure(self) -> Dict[str, Any]:
        """
        Analyze module structure and organization.
        
        Returns:
            Dict with module hierarchy and metrics
        """
        structure = {
            "modules": [],
            "depth": 0,
            "total_directories": 0
        }
        
        src_path = self.project_root / "src"
        if not src_path.exists():
            return structure
        
        # Analyze directory structure
        for root, dirs, files in os.walk(src_path):
            root_path = Path(root)
            
            # Skip venv and cache directories
            dirs[:] = [d for d in dirs if d not in ['venv', '__pycache__', '.git']]
            
            if not files:
                continue
            
            py_files = [f for f in files if f.endswith('.py')]
            if not py_files:
                continue
            
            structure["modules"].append({
                "path": str(root_path.relative_to(self.project_root)),
                "file_count": len(py_files),
                "subdirectories": len(dirs)
            })
            
            # Calculate depth
            depth = len(root_path.relative_to(src_path).parts)
            structure["depth"] = max(structure["depth"], depth)
        
        structure["total_directories"] = len(structure["modules"])
        
        return structure
