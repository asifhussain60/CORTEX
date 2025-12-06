#!/usr/bin/env python3
"""
Dashboard Data Source Registrar

Automatically updates dashboard UI with newly collected data sources.
Run after onboarding any new application.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any

class DashboardRegistrar:
    """Automatically registers new data sources in dashboard UI"""
    
    def __init__(self, cortex_root: Path = None):
        self.cortex_root = cortex_root or Path(__file__).parent
        self.dashboards_dir = self.cortex_root / "cortex-brain" / "dashboards"
        self.ui_dir = self.dashboards_dir / "ui"
        self.data_loader_js = self.ui_dir / "data-loader.js"
        self.index_html = self.ui_dir / "index.html"
    
    def discover_data_sources(self) -> List[Dict[str, str]]:
        """
        Discover all data source directories with JSON files.
        
        Returns:
            List of dicts with 'id', 'name', 'path', 'description'
        """
        sources = []
        
        if not self.dashboards_dir.exists():
            print(f"⚠️  Dashboards directory not found: {self.dashboards_dir}")
            return sources
        
        # Scan for directories with JSON data files
        for item in self.dashboards_dir.iterdir():
            if item.is_dir() and item.name not in ['ui', 'schema', '__pycache__']:
                # Check if has required JSON files
                has_metadata = (item / "metadata.json").exists()
                has_architecture = (item / "architecture.json").exists()
                
                if has_metadata or has_architecture:
                    # Try to read metadata for description
                    description = "Application"
                    if has_metadata:
                        try:
                            with open(item / "metadata.json") as f:
                                meta = json.load(f)
                                app_type = meta.get("app_type", "")
                                if app_type:
                                    description = app_type.title()
                        except:
                            pass
                    
                    # Generate display name
                    display_name = item.name.replace('-', ' ').replace('_', ' ').title()
                    
                    sources.append({
                        'id': item.name,
                        'name': display_name,
                        'path': f'/{item.name}/',
                        'description': description
                    })
        
        return sorted(sources, key=lambda x: x['name'])
    
    def update_data_loader_js(self, sources: List[Dict[str, str]]) -> bool:
        """
        Update DATA_SOURCES object in data-loader.js
        
        Args:
            sources: List of source dicts from discover_data_sources()
        
        Returns:
            True if updated, False if failed
        """
        if not self.data_loader_js.exists():
            print(f"❌ data-loader.js not found: {self.data_loader_js}")
            return False
        
        try:
            content = self.data_loader_js.read_text(encoding='utf-8')
            
            # Build new DATA_SOURCES object
            sources_lines = ["const DATA_SOURCES = {"]
            
            for source in sources:
                sources_lines.append(f"    '{source['id']}': '{source['path']}',")
            
            sources_lines.append("};")
            new_sources_block = "\n".join(sources_lines)
            
            # Replace existing DATA_SOURCES
            pattern = r'const DATA_SOURCES = \{[^}]+\};'
            updated_content = re.sub(pattern, new_sources_block, content, flags=re.DOTALL)
            
            # Increment version number
            version_pattern = r"const DATA_LOADER_VERSION = '[^']+'"
            if re.search(version_pattern, updated_content):
                # Extract current version and increment
                current_version = re.search(r"'(\d+\.\d+)\.(\d+)'", updated_content)
                if current_version:
                    major_minor = current_version.group(1)
                    patch = int(current_version.group(2)) + 1
                    new_version = f"{major_minor}.{patch}"
                    updated_content = re.sub(
                        version_pattern,
                        f"const DATA_LOADER_VERSION = '{new_version}'",
                        updated_content
                    )
            
            self.data_loader_js.write_text(updated_content, encoding='utf-8')
            print(f"✅ Updated {self.data_loader_js.name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update data-loader.js: {e}")
            return False
    
    def update_index_html(self, sources: List[Dict[str, str]]) -> bool:
        """
        Update dropdown options in index.html
        
        Args:
            sources: List of source dicts from discover_data_sources()
        
        Returns:
            True if updated, False if failed
        """
        if not self.index_html.exists():
            print(f"❌ index.html not found: {self.index_html}")
            return False
        
        try:
            content = self.index_html.read_text(encoding='utf-8')
            
            # Build new option elements
            options_lines = []
            for source in sources:
                label = f"{source['name']}"
                if source['description'] and source['description'] != source['name']:
                    label += f" ({source['description']})"
                options_lines.append(f'                    <option value="{source["id"]}">{label}</option>')
            
            new_options = "\n".join(options_lines)
            
            # Replace existing options (between <select> and </select>)
            pattern = r'(<select id="sourceSelect"[^>]*>)(.*?)(</select>)'
            
            def replace_options(match):
                return f"{match.group(1)}\n{new_options}\n                {match.group(3)}"
            
            updated_content = re.sub(pattern, replace_options, content, flags=re.DOTALL)
            
            self.index_html.write_text(updated_content, encoding='utf-8')
            print(f"✅ Updated {self.index_html.name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update index.html: {e}")
            return False
    
    def register_all_sources(self) -> bool:
        """
        Discover and register all data sources.
        
        Returns:
            True if successful, False if any step failed
        """
        print("="*70)
        print("Dashboard Data Source Registrar")
        print("="*70)
        print()
        
        # Discover sources
        print("🔍 Discovering data sources...")
        sources = self.discover_data_sources()
        
        if not sources:
            print("⚠️  No data sources found")
            return False
        
        print(f"✅ Found {len(sources)} data sources:")
        for source in sources:
            print(f"   • {source['name']} ({source['id']}) - {source['description']}")
        print()
        
        # Update files
        print("📝 Updating dashboard UI files...")
        success = True
        
        if not self.update_data_loader_js(sources):
            success = False
        
        if not self.update_index_html(sources):
            success = False
        
        print()
        if success:
            print("="*70)
            print("✅ Dashboard registration complete!")
            print("="*70)
            print()
            print("Next Steps:")
            print("   1. Refresh browser (Ctrl+F5) to clear cache")
            print("   2. Select data source from dropdown")
            print("   3. Dashboard will automatically load new data")
        else:
            print("="*70)
            print("⚠️  Registration completed with warnings")
            print("="*70)
        
        return success


def main():
    """Main entry point"""
    import sys
    
    cortex_root = Path(__file__).parent
    registrar = DashboardRegistrar(cortex_root)
    
    success = registrar.register_all_sources()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
