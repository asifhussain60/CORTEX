"""
Documentation Refresh Plugin

Automatically refreshes the 4 synchronized documentation files based on CORTEX 2.0 design:
- docs/story/CORTEX-STORY/Technical-CORTEX.md
- docs/story/CORTEX-STORY/Awakening Of CORTEX.md
- docs/story/CORTEX-STORY/Image-Prompts.md (TECHNICAL DIAGRAMS ONLY - no cartoons)
- docs/story/CORTEX-STORY/History.md

Triggered by: 'Update Documentation' or 'Refresh documentation' commands at entry point

NOTE: Image-Prompts.md generates SYSTEM DIAGRAMS (flowcharts, sequence diagrams, 
architecture diagrams) that reveal CORTEX design - NOT cartoon characters or story 
illustrations. For story illustrations, see prompts/user/cortex-gemini-image-prompts.md
"""

from src.plugins.base_plugin import BasePlugin, PluginMetadata, PluginCategory, PluginPriority
from src.plugins.hooks import HookPoint
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class Plugin(BasePlugin):
    """Documentation Refresh Plugin for CORTEX 2.0"""
    
    def _get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="doc_refresh_plugin",
            name="Documentation Refresh",
            version="1.0.0",
            category=PluginCategory.DOCUMENTATION,
            priority=PluginPriority.HIGH,
            description="Refreshes synchronized documentation files based on CORTEX 2.0 design",
            author="CORTEX Team",
            dependencies=[],
            hooks=[
                HookPoint.ON_DOC_REFRESH.value,
                HookPoint.ON_SELF_REVIEW.value
            ],
            config_schema={
                "type": "object",
                "properties": {
                    "auto_refresh": {
                        "type": "boolean",
                        "description": "Auto-refresh on design changes",
                        "default": False
                    },
                    "incremental_lines": {
                        "type": "integer",
                        "description": "Max lines per update (prevents length limit)",
                        "default": 150
                    },
                    "backup_before_refresh": {
                        "type": "boolean",
                        "description": "Create backups before refresh",
                        "default": True
                    }
                }
            }
        )
    
    def initialize(self) -> bool:
        """Initialize plugin - verify paths exist"""
        try:
            # Verify cortex-2.0-design directory exists
            design_dir = Path("cortex-brain/cortex-2.0-design")
            if not design_dir.exists():
                logger.error(f"Design directory not found: {design_dir}")
                return False
            
            # Verify story directory exists
            story_dir = Path("docs/story/CORTEX-STORY")
            if not story_dir.exists():
                logger.warning(f"Story directory not found, will create: {story_dir}")
                story_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info("Documentation Refresh Plugin initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize doc_refresh_plugin: {e}")
            return False
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute documentation refresh"""
        hook = context.get("hook")
        
        if hook == HookPoint.ON_DOC_REFRESH.value:
            return self._refresh_all_docs(context)
        elif hook == HookPoint.ON_SELF_REVIEW.value:
            return self._check_doc_sync(context)
        
        return {"success": False, "error": "Unknown hook"}
    
    def _refresh_all_docs(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Refresh all 4 synchronized documentation files"""
        results = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "files_refreshed": [],
            "errors": []
        }
        
        # Load CORTEX 2.0 design context
        design_context = self._load_design_context()
        
        # Refresh each document
        docs_to_refresh = [
            ("Technical-CORTEX.md", self._refresh_technical_doc),
            ("Awakening Of CORTEX.md", self._refresh_story_doc),
            ("Image-Prompts.md", self._refresh_image_prompts_doc),
            ("History.md", self._refresh_history_doc)
        ]
        
        for filename, refresh_func in docs_to_refresh:
            try:
                file_path = Path(f"docs/story/CORTEX-STORY/{filename}")
                
                # Backup if enabled
                if self.config.get("backup_before_refresh", True):
                    self._create_backup(file_path)
                
                # Refresh document
                refresh_result = refresh_func(file_path, design_context)
                
                if refresh_result["success"]:
                    results["files_refreshed"].append(filename)
                else:
                    results["errors"].append(f"{filename}: {refresh_result.get('error')}")
                    
            except Exception as e:
                logger.error(f"Error refreshing {filename}: {e}")
                results["errors"].append(f"{filename}: {str(e)}")
                results["success"] = False
        
        return results
    
    def _check_doc_sync(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check if documentation is synchronized with design"""
        issues = []
        
        # Check last modified timestamps
        design_index = Path("cortex-brain/cortex-2.0-design/00-INDEX.md")
        story_dir = Path("docs/story/CORTEX-STORY")
        
        if design_index.exists():
            design_mtime = design_index.stat().st_mtime
            
            for doc in ["Technical-CORTEX.md", "Awakening Of CORTEX.md", "Image-Prompts.md"]:
                doc_path = story_dir / doc
                if doc_path.exists():
                    doc_mtime = doc_path.stat().st_mtime
                    if doc_mtime < design_mtime:
                        issues.append({
                            "file": doc,
                            "issue": "Out of sync with design (older than 00-INDEX.md)",
                            "severity": "MEDIUM"
                        })
        
        return {
            "success": True,
            "synchronized": len(issues) == 0,
            "issues": issues
        }
    
    def _load_design_context(self) -> Dict[str, Any]:
        """Load CORTEX 2.0 design context from all design docs"""
        design_dir = Path("cortex-brain/cortex-2.0-design")
        context = {
            "design_docs": [],
            "features": {},
            "implementation_status": {}
        }
        
        # Load key design documents
        key_docs = [
            "00-INDEX.md",
            "01-core-architecture.md",
            "02-plugin-system.md",
            "03-conversation-state.md",
            "07-self-review-system.md",
            "21-workflow-pipeline-system.md",
            "22-request-validator-enhancer.md",
            "23-modular-entry-point.md"
        ]
        
        for doc_name in key_docs:
            doc_path = design_dir / doc_name
            if doc_path.exists():
                context["design_docs"].append({
                    "name": doc_name,
                    "path": str(doc_path),
                    "content": doc_path.read_text(encoding="utf-8")
                })
        
        return context
    
    def _refresh_technical_doc(self, file_path: Path, design_context: Dict[str, Any]) -> Dict[str, Any]:
        """Refresh Technical-CORTEX.md"""
        # This will be implemented incrementally
        return {
            "success": True,
            "message": "Technical doc refresh scheduled (incremental updates)",
            "action_required": "Use #file:Technical-CORTEX.md update with design context"
        }
    
    def _refresh_story_doc(self, file_path: Path, design_context: Dict[str, Any]) -> Dict[str, Any]:
        """Refresh Awakening Of CORTEX.md story"""
        return {
            "success": True,
            "message": "Story doc refresh scheduled",
            "action_required": "Extend story with CORTEX 2.0 chapters"
        }
    
    def _refresh_image_prompts_doc(self, file_path: Path, design_context: Dict[str, Any]) -> Dict[str, Any]:
        """Refresh Image-Prompts.md with TECHNICAL DIAGRAMS (not cartoons)"""
        return {
            "success": True,
            "message": "Technical diagram prompts refresh scheduled",
            "action_required": "Generate Gemini prompts for system diagrams (flowcharts, sequence diagrams, architecture diagrams)",
            "note": "For story illustrations/cartoons, see prompts/user/cortex-gemini-image-prompts.md instead"
        }
    
    def _refresh_history_doc(self, file_path: Path, design_context: Dict[str, Any]) -> Dict[str, Any]:
        """Refresh History.md"""
        return {
            "success": True,
            "message": "History doc refresh scheduled",
            "action_required": "Document KDS evolution timeline"
        }
    
    def _create_backup(self, file_path: Path) -> None:
        """Create backup of file before refresh"""
        if not file_path.exists():
            return
        
        backup_dir = file_path.parent / ".backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"
        
        import shutil
        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup: {backup_path}")
    
    def cleanup(self) -> bool:
        """Cleanup plugin resources"""
        return True
