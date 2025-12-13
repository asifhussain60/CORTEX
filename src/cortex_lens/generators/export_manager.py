"""
Export Utilities - Convert analysis data to multiple formats.

Features:
- JSON export (structured data)
- HTML export (standalone dashboard)
- Markdown export (documentation)
- CSV export (metrics)
- ZIP packaging (distribution)

Author: Asif Hussain
Date: December 2025
"""

import json
import logging
import zipfile
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ExportManager:
    """
    Manages exports of analysis data to multiple formats.
    
    Supported formats:
    - JSON: Complete structured data
    - HTML: Interactive dashboard
    - Markdown: Human-readable report
    - CSV: Metrics tables
    - ZIP: Complete package
    """
    
    def __init__(self):
        """Initialize export manager."""
        pass
    
    def export_json(
        self,
        analysis_data: Dict[str, Any],
        output_path: Path
    ) -> Path:
        """
        Export analysis data as JSON.
        
        Args:
            analysis_data: Complete analysis results
            output_path: Path to write JSON file
            
        Returns:
            Path to created JSON file
        """
        logger.info(f"💾 Exporting to JSON: {output_path}")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, default=str)
        
        logger.info(f"✅ JSON export complete: {output_path}")
        return output_path
    
    def export_markdown(
        self,
        analysis_data: Dict[str, Any],
        output_path: Path,
        repository_name: str = "Repository"
    ) -> Path:
        """
        Export analysis data as Markdown report.
        
        Args:
            analysis_data: Complete analysis results
            output_path: Path to write Markdown file
            repository_name: Name of analyzed repository
            
        Returns:
            Path to created Markdown file
        """
        logger.info(f"📝 Exporting to Markdown: {output_path}")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        markdown = self._generate_markdown_report(analysis_data, repository_name)
        
        output_path.write_text(markdown, encoding='utf-8')
        
        logger.info(f"✅ Markdown export complete: {output_path}")
        return output_path
    
    def export_csv_metrics(
        self,
        analysis_data: Dict[str, Any],
        output_dir: Path
    ) -> list[Path]:
        """
        Export metrics as CSV files.
        
        Args:
            analysis_data: Complete analysis results
            output_dir: Directory to write CSV files
            
        Returns:
            List of created CSV file paths
        """
        logger.info(f"📊 Exporting CSV metrics to: {output_dir}")
        
        output_dir.mkdir(parents=True, exist_ok=True)
        csv_files = []
        
        # Complexity metrics CSV
        complexity_path = output_dir / 'complexity_metrics.csv'
        self._export_complexity_csv(analysis_data.get('complexity', {}), complexity_path)
        csv_files.append(complexity_path)
        
        # Security findings CSV
        security_path = output_dir / 'security_findings.csv'
        self._export_security_csv(analysis_data.get('security', {}), security_path)
        csv_files.append(security_path)
        
        # Dependencies CSV
        deps_path = output_dir / 'dependencies.csv'
        self._export_dependencies_csv(analysis_data.get('dependencies', {}), deps_path)
        csv_files.append(deps_path)
        
        logger.info(f"✅ CSV export complete: {len(csv_files)} files")
        return csv_files
    
    def create_distribution_package(
        self,
        dashboard_dir: Path,
        output_path: Path
    ) -> Path:
        """
        Create ZIP package with dashboard and data.
        
        Args:
            dashboard_dir: Directory containing dashboard files
            output_path: Path to write ZIP file
            
        Returns:
            Path to created ZIP file
        """
        logger.info(f"📦 Creating distribution package: {output_path}")
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in dashboard_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(dashboard_dir)
                    zipf.write(file_path, arcname)
        
        logger.info(f"✅ Distribution package created: {output_path}")
        return output_path
    
    def _generate_markdown_report(
        self,
        analysis_data: Dict[str, Any],
        repository_name: str
    ) -> str:
        """Generate Markdown report from analysis data."""
        
        classification = analysis_data.get('classification', {})
        health_data = analysis_data.get('health', {})
        security_data = analysis_data.get('security', {})
        complexity_data = analysis_data.get('complexity', {})
        coverage_data = analysis_data.get('test_coverage', {})
        
        md = f"""# 🧠 CORTEX Lens Analysis Report

**Repository:** {repository_name}  
**Type:** {classification.get('repo_type', 'unknown').replace('_', ' ').title()}  
**Primary Language:** {classification.get('primary_language', 'unknown')}  
**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 📊 Executive Summary

### Health Score
**{health_data.get('health_score', 0)}/100**

### Key Metrics
- **Total Files:** {health_data.get('total_files', 0):,}
- **Lines of Code:** {health_data.get('total_lines', 0):,}
- **Security Issues:** {security_data.get('vulnerabilities_found', 0)}
- **Test Coverage:** {coverage_data.get('coverage_summary', 0.0):.1f}%

---

## 🏗️ Architecture

### Patterns Detected
"""
        
        # Architecture patterns
        for pattern, confidence in analysis_data.get('architecture', {}).get('patterns', {}).items():
            confidence_label = 'High' if confidence > 0.7 else 'Medium' if confidence > 0.4 else 'Low'
            md += f"- **{pattern}** (Confidence: {confidence_label})\n"
        
        md += "\n### Layers\n"
        for layer, files in analysis_data.get('architecture', {}).get('layers', {}).items():
            md += f"- **{layer.capitalize()}:** {len(files)} files\n"
        
        # Security section
        md += f"""

---

## 🔐 Security Analysis

**Total Vulnerabilities:** {security_data.get('vulnerabilities_found', 0)}

### By Severity
"""
        
        for severity, count in security_data.get('vulnerabilities_by_severity', {}).items():
            md += f"- **{severity}:** {count}\n"
        
        # Complexity section
        md += f"""

---

## 📈 Code Quality

### Complexity Metrics
- **Avg Cyclomatic Complexity:** {complexity_data.get('complexity_summary', {}).get('avg_cyclomatic', 0):.2f}
- **Avg Cognitive Complexity:** {complexity_data.get('complexity_summary', {}).get('avg_cognitive', 0):.2f}
- **Maintainability Index:** {complexity_data.get('complexity_summary', {}).get('avg_maintainability', 0):.1f}/100

### Top 5 Complexity Hotspots
"""
        
        for hotspot in complexity_data.get('hotspots', [])[:5]:
            md += f"- **{hotspot.get('name')}** ({Path(hotspot.get('file', '')).name}) - Cyclomatic: {hotspot.get('cyclomatic', 0)}, Cognitive: {hotspot.get('cognitive', 0)}\n"
        
        # Test coverage section
        md += f"""

---

## ✅ Test Coverage

**Overall Coverage:** {coverage_data.get('coverage_summary', 0.0):.1f}%  
**Total Tests:** {coverage_data.get('total_tests', 0)}

### Tests by Type
- **Unit:** {coverage_data.get('tests_by_type', {}).get('unit', 0)}
- **Integration:** {coverage_data.get('tests_by_type', {}).get('integration', 0)}
- **E2E:** {coverage_data.get('tests_by_type', {}).get('e2e', 0)}

### Coverage by Layer
"""
        
        for layer, coverage in coverage_data.get('coverage_by_layer', {}).items():
            md += f"- **{layer.capitalize()}:** {coverage:.1f}%\n"
        
        md += f"""

---

## 📦 Dependencies

**Total Dependencies:** {len(analysis_data.get('dependencies', {}).get('packages', {}))}  
**Direct:** {sum(1 for d in analysis_data.get('dependencies', {}).get('packages', {}).values() if d.get('type') == 'direct')}  
**Transitive:** {sum(1 for d in analysis_data.get('dependencies', {}).get('packages', {}).values() if d.get('type') == 'transitive')}

---

*Generated by CORTEX Lens v1.0.0*  
*© 2025 Asif Hussain. All rights reserved.*
"""
        
        return md
    
    def _export_complexity_csv(self, complexity_data: Dict[str, Any], output_path: Path):
        """Export complexity metrics to CSV."""
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Function', 'File', 'Line', 'Cyclomatic', 'Cognitive', 'Maintainability', 'Rating'])
            
            for hotspot in complexity_data.get('hotspots', []):
                writer.writerow([
                    hotspot.get('name', ''),
                    hotspot.get('file', ''),
                    hotspot.get('line', 0),
                    hotspot.get('cyclomatic', 0),
                    hotspot.get('cognitive', 0),
                    hotspot.get('maintainability', 0),
                    hotspot.get('complexity_rating', 'MEDIUM')
                ])
    
    def _export_security_csv(self, security_data: Dict[str, Any], output_path: Path):
        """Export security findings to CSV."""
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Severity', 'Type', 'File', 'Line', 'Description', 'CWE'])
            
            for finding in security_data.get('findings', []):
                writer.writerow([
                    finding.get('severity', ''),
                    finding.get('type', ''),
                    finding.get('file', ''),
                    finding.get('line', 0),
                    finding.get('description', ''),
                    finding.get('cwe', '')
                ])
    
    def _export_dependencies_csv(self, dependencies_data: Dict[str, Any], output_path: Path):
        """Export dependencies to CSV."""
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Package', 'Version', 'Type', 'Source'])
            
            for pkg_name, pkg_info in dependencies_data.get('packages', {}).items():
                writer.writerow([
                    pkg_name,
                    pkg_info.get('version', ''),
                    pkg_info.get('type', ''),
                    pkg_info.get('source', '')
                ])
