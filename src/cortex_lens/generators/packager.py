"""
Packager

Packages dashboard and exports data in multiple formats.
"""

import logging
import json
import zipfile
from pathlib import Path
from typing import Dict, Any, List
from .base import BaseGenerator

logger = logging.getLogger(__name__)


class Packager(BaseGenerator):
    """
    Package dashboards and export data
    
    Creates distribution packages and multi-format exports.
    """
    
    def generate(
        self,
        data: Dict[str, Any],
        output_path: Path,
        **kwargs
    ) -> Path:
        """Not used directly - use package() method"""
        raise NotImplementedError("Use package() method instead")
    
    def package(self, dashboard_path: Path) -> Path:
        """
        Create distribution ZIP of dashboard
        
        Args:
            dashboard_path: Path to dashboard directory
            
        Returns:
            Path to ZIP file
        """
        logger.info("Creating distribution package...")
        
        zip_path = dashboard_path.parent / f"{dashboard_path.name}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add all files in dashboard directory
            for file_path in dashboard_path.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(dashboard_path.parent)
                    zf.write(file_path, arcname)
        
        logger.info(f"✅ Package created: {zip_path}")
        
        return zip_path
    
    def export(
        self,
        data: Dict[str, Any],
        formats: List[str],
        output_dir: Path
    ) -> Dict[str, Path]:
        """
        Export data in multiple formats
        
        Args:
            data: Analysis data to export
            formats: List of formats ['json', 'yaml', 'csv', 'html']
            output_dir: Output directory
            
        Returns:
            Dictionary of {format: path}
        """
        logger.info(f"Exporting data in formats: {', '.join(formats)}")
        
        exports = {}
        
        if 'all' in formats:
            formats = ['json', 'yaml', 'csv']
        
        if 'json' in formats:
            json_path = self._export_json(data, output_dir)
            exports['json'] = json_path
        
        if 'yaml' in formats:
            yaml_path = self._export_yaml(data, output_dir)
            exports['yaml'] = yaml_path
        
        if 'csv' in formats:
            csv_path = self._export_csv(data, output_dir)
            exports['csv'] = csv_path
        
        logger.info(f"✅ Exported {len(exports)} formats")
        
        return exports
    
    def _export_json(self, data: Dict[str, Any], output_dir: Path) -> Path:
        """Export to JSON"""
        json_path = output_dir / 'data' / 'analysis.json'
        json_path.parent.mkdir(parents=True, exist_ok=True)
        
        with json_path.open('w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 JSON: {json_path}")
        return json_path
    
    def _export_yaml(self, data: Dict[str, Any], output_dir: Path) -> Path:
        """Export to YAML"""
        try:
            import yaml
            
            yaml_path = output_dir / 'data' / 'analysis.yaml'
            yaml_path.parent.mkdir(parents=True, exist_ok=True)
            
            with yaml_path.open('w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(f"💾 YAML: {yaml_path}")
            return yaml_path
            
        except ImportError:
            logger.warning("PyYAML not installed - YAML export skipped")
            return None
    
    def _export_csv(self, data: Dict[str, Any], output_dir: Path) -> Path:
        """Export metrics to CSV"""
        import csv
        
        csv_path = output_dir / 'data' / 'metrics.csv'
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        
        rows = [['Metric', 'Value']]
        
        # Flatten data for CSV
        metadata = data.get('metadata', {})
        for key, value in metadata.items():
            if not isinstance(value, (dict, list)):
                rows.append([f"metadata.{key}", str(value)])
        
        health = data.get('health', {})
        for key, value in health.items():
            if not isinstance(value, (dict, list)):
                rows.append([f"health.{key}", str(value)])
        
        with csv_path.open('w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        
        logger.info(f"💾 CSV: {csv_path}")
        return csv_path
