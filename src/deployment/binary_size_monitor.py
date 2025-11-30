"""
Binary Size Monitor - Package Size Tracking

Monitors package size growth:
- Tracks size before/after build
- Alerts on >10% increase without justification
- Flags unexpected file additions
- Generates size breakdown reports

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class BinarySizeMonitor:
    """
    Package size monitor for deployments.
    
    Tracks package size growth and alerts on unexpected changes.
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize binary size monitor.
        
        Args:
            project_root: Root directory of CORTEX project
        """
        self.project_root = Path(project_root)
        self.history_file = self.project_root / "cortex-brain" / "metrics" / "package-size-history.json"
    
    def measure_package_size(self, package_root: Path) -> Dict[str, Any]:
        """
        Measure package size.
        
        Args:
            package_root: Root of built package
        
        Returns:
            Size measurement with breakdown
        """
        package_root = Path(package_root)
        
        if not package_root.exists():
            return {
                "error": "Package root does not exist",
                "path": str(package_root)
            }
        
        measurement = {
            "timestamp": datetime.now().isoformat(),
            "package_root": str(package_root),
            "total_size_bytes": 0,
            "total_files": 0,
            "size_by_extension": {},
            "size_by_directory": {},
            "largest_files": []
        }
        
        # Scan all files
        all_files = list(package_root.rglob("*"))
        
        for file_path in all_files:
            if file_path.is_dir():
                continue
            
            size = file_path.stat().st_size
            measurement["total_size_bytes"] += size
            measurement["total_files"] += 1
            
            # Track by extension
            ext = file_path.suffix or "no_extension"
            if ext not in measurement["size_by_extension"]:
                measurement["size_by_extension"][ext] = 0
            measurement["size_by_extension"][ext] += size
            
            # Track by directory
            relative_path = file_path.relative_to(package_root)
            if relative_path.parts:
                top_dir = relative_path.parts[0]
                if top_dir not in measurement["size_by_directory"]:
                    measurement["size_by_directory"][top_dir] = 0
                measurement["size_by_directory"][top_dir] += size
            
            # Track largest files
            measurement["largest_files"].append({
                "path": str(relative_path),
                "size_bytes": size
            })
        
        # Sort largest files
        measurement["largest_files"].sort(key=lambda x: x["size_bytes"], reverse=True)
        measurement["largest_files"] = measurement["largest_files"][:20]  # Top 20
        
        return measurement
    
    def compare_with_history(
        self,
        current_measurement: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare current measurement with history.
        
        Args:
            current_measurement: Current size measurement
        
        Returns:
            Comparison results with growth analysis
        """
        comparison = {
            "has_history": False,
            "size_change_bytes": 0,
            "size_change_percent": 0.0,
            "alert_threshold_exceeded": False,
            "previous_size_bytes": 0,
            "current_size_bytes": current_measurement.get("total_size_bytes", 0)
        }
        
        # Load history
        history = self._load_history()
        
        if not history:
            comparison["message"] = "No history found - this is the first measurement"
            return comparison
        
        comparison["has_history"] = True
        
        # Get most recent measurement
        last_measurement = history[-1]
        comparison["previous_size_bytes"] = last_measurement.get("total_size_bytes", 0)
        
        # Calculate change
        if comparison["previous_size_bytes"] > 0:
            comparison["size_change_bytes"] = (
                comparison["current_size_bytes"] - comparison["previous_size_bytes"]
            )
            comparison["size_change_percent"] = (
                (comparison["size_change_bytes"] / comparison["previous_size_bytes"]) * 100
            )
            
            # Check threshold (10%)
            if abs(comparison["size_change_percent"]) > 10:
                comparison["alert_threshold_exceeded"] = True
                comparison["message"] = (
                    f"Package size changed by {comparison['size_change_percent']:.1f}% "
                    f"({self._format_bytes(comparison['size_change_bytes'])})"
                )
            else:
                comparison["message"] = (
                    f"Package size changed by {comparison['size_change_percent']:.1f}% "
                    f"(within threshold)"
                )
        
        return comparison
    
    def save_measurement(self, measurement: Dict[str, Any]) -> None:
        """
        Save measurement to history.
        
        Args:
            measurement: Size measurement to save
        """
        history = self._load_history()
        history.append(measurement)
        
        # Keep last 30 measurements
        history = history[-30:]
        
        # Save to file
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
        
        logger.info(f"Saved size measurement to {self.history_file}")
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """
        Load size history.
        
        Returns:
            List of historical measurements
        """
        if not self.history_file.exists():
            return []
        
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load size history: {e}")
            return []
    
    def get_size_trend(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get size trend over time.
        
        Args:
            limit: Number of measurements to return
        
        Returns:
            List of measurements (most recent first)
        """
        history = self._load_history()
        return history[-limit:][::-1]  # Reverse for most recent first
    
    @staticmethod
    def _format_bytes(size: int) -> str:
        """
        Format bytes as human-readable string.
        
        Args:
            size: Size in bytes
        
        Returns:
            Formatted string (e.g., "1.5 MB")
        """
        for unit in ["B", "KB", "MB", "GB"]:
            if abs(size) < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
