"""
MkDocs Post-Build Hook: Copy Assets to Site
Auto-copies assets/ folder to _build/site/assets/ after build completes
Ensures assets are accessible from built site without duplication
"""

import shutil
import os
from pathlib import Path


def on_post_build(config):
    """
    Copy assets folder to site output after MkDocs build completes
    
    Args:
        config: MkDocs config object
    """
    project_root = Path(config['docs_dir']).parent
    assets_src = project_root / 'assets'
    assets_dest = Path(config['site_dir']) / 'assets'
    
    if assets_src.exists():
        # Remove existing assets in site (if any)
        if assets_dest.exists():
            shutil.rmtree(assets_dest)
        
        # Copy assets to site
        shutil.copytree(assets_src, assets_dest)
        print(f"✅ Assets copied: {assets_src} → {assets_dest}")
    else:
        print(f"⚠️  Assets folder not found: {assets_src}")
