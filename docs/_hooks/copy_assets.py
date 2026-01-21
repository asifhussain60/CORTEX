"""
MkDocs Post-Build Hook: Copy Assets to Site
Auto-copies assets/ folder to _build/site/assets/ after build completes
Merges with existing Material theme assets (does not overwrite)
"""

import shutil
import os
from pathlib import Path


def on_post_build(config):
    """
    Copy assets folder to site output after MkDocs build completes.
    Merges with existing assets (preserves Material theme CSS/JS).
    
    Args:
        config: MkDocs config object
    """
    project_root = Path(config['docs_dir']).parent
    assets_src = project_root / 'assets'
    assets_dest = Path(config['site_dir']) / 'assets'
    
    if assets_src.exists():
        # Merge assets - copy each item without deleting existing
        for item in assets_src.iterdir():
            dest_item = assets_dest / item.name
            if item.is_dir():
                if dest_item.exists():
                    shutil.rmtree(dest_item)
                shutil.copytree(item, dest_item)
            else:
                shutil.copy2(item, dest_item)
        print(f"✅ Assets merged: {assets_src} → {assets_dest}")
    else:
        print(f"⚠️  Assets folder not found: {assets_src}")
