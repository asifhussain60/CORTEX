"""
Refresh design documentation module.

Part of the Documentation Update operation - updates design documentation files.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationPhase,
    OperationStatus
)


class RefreshDesignDocsModule(BaseOperationModule):
    """
    Refresh design documentation.
    
    Scans design documentation directory for outdated files,
    updates indexes, and ensures documentation structure is current.
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Get module metadata."""
        return OperationModuleMetadata(
            module_id="refresh_design_docs",
            name="Refresh Design Documentation",
            description="Update design documentation",
            phase=OperationPhase.PROCESSING,
            priority=15
        )
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute design documentation refresh.
        
        Args:
            context: Operation context
            
        Returns:
            OperationResult with refresh status
        """
        try:
            project_root = Path(context.get("project_root", os.getcwd()))
            design_dir = project_root / "docs" / "architecture"
            
            if not design_dir.exists():
                self.log_info(f"Design docs directory does not exist: {design_dir}")
                return OperationResult(
                    success=True,
                    status=OperationStatus.SKIPPED,
                    message="Design docs directory not found, skipping",
                    data={"skipped": True}
                )
            
            self.log_info(f"Refreshing design documentation in {design_dir}")
            
            # Find all design docs
            design_files = list(design_dir.rglob("*.md"))
            self.log_info(f"Found {len(design_files)} design documentation files")
            
            # Analyze documentation
            analysis = self._analyze_design_docs(design_files)
            
            # Update index if needed
            index_updated = self._update_design_index(design_dir, design_files)
            
            # Add update timestamps
            updated_count = self._add_update_timestamps(design_files)
            
            self.log_success(
                f"Refreshed {len(design_files)} design docs, "
                f"updated {updated_count} timestamps"
            )
            
            return OperationResult(
                success=True,
                status=OperationStatus.SUCCESS,
                message=f"Refreshed {len(design_files)} design documentation files",
                data={
                    "files_processed": len(design_files),
                    "timestamps_updated": updated_count,
                    "index_updated": index_updated,
                    "analysis": analysis
                }
            )
            
        except Exception as e:
            self.log_error(f"Failed to refresh design docs: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message="Design documentation refresh failed",
                error=str(e)
            )
    
    def _analyze_design_docs(self, design_files: List[Path]) -> Dict[str, Any]:
        """
        Analyze design documentation for completeness.
        
        Args:
            design_files: List of design doc files
            
        Returns:
            Analysis results
        """
        analysis = {
            "total_files": len(design_files),
            "by_category": {},
            "outdated_files": [],
            "missing_metadata": []
        }
        
        for doc_file in design_files:
            try:
                content = doc_file.read_text(encoding="utf-8")
                
                # Categorize by directory
                category = doc_file.parent.name
                if category not in analysis["by_category"]:
                    analysis["by_category"][category] = 0
                analysis["by_category"][category] += 1
                
                # Check for metadata
                if "**Date:**" not in content and "Last Updated:" not in content:
                    analysis["missing_metadata"].append(str(doc_file.name))
                
                # Check if outdated (more than 30 days without update)
                # This would need file modification time or content parsing
                
            except Exception as e:
                self.log_warning(f"Failed to analyze {doc_file}: {e}")
        
        return analysis
    
    def _update_design_index(self, design_dir: Path, design_files: List[Path]) -> bool:
        """
        Update or create design documentation index.
        
        Args:
            design_dir: Design docs directory
            design_files: List of design doc files
            
        Returns:
            True if index was updated
        """
        try:
            index_file = design_dir / "index.md"
            
            content = [
                "# Design Documentation Index",
                "",
                f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}",
                "",
                "## Overview",
                "",
                "This directory contains CORTEX design and architecture documentation.",
                "",
                "## Documents",
                ""
            ]
            
            # Group by subdirectory
            docs_by_dir = {}
            for doc_file in sorted(design_files):
                if doc_file.name == "index.md":
                    continue
                
                rel_dir = doc_file.relative_to(design_dir).parent
                if str(rel_dir) not in docs_by_dir:
                    docs_by_dir[str(rel_dir)] = []
                
                docs_by_dir[str(rel_dir)].append(doc_file)
            
            # Generate index entries
            for dir_name, docs in sorted(docs_by_dir.items()):
                if dir_name != ".":
                    content.append(f"### {dir_name}")
                    content.append("")
                
                for doc in sorted(docs):
                    rel_path = doc.relative_to(design_dir)
                    doc_name = doc.stem.replace('-', ' ').replace('_', ' ').title()
                    content.append(f"- [{doc_name}]({rel_path})")
                
                content.append("")
            
            index_file.write_text("\n".join(content), encoding="utf-8")
            return True
            
        except Exception as e:
            self.log_warning(f"Failed to update design index: {e}")
            return False
    
    def _add_update_timestamps(self, design_files: List[Path]) -> int:
        """
        Add or update timestamps in design documentation files.
        
        Args:
            design_files: List of design doc files
            
        Returns:
            Number of files updated
        """
        updated_count = 0
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        for doc_file in design_files:
            if doc_file.name == "index.md":
                continue
            
            try:
                content = doc_file.read_text(encoding="utf-8")
                lines = content.split('\n')
                
                # Check if timestamp exists
                has_timestamp = any("**Date:**" in line or "Last Updated:" in line for line in lines[:10])
                
                if not has_timestamp:
                    # Add timestamp after title
                    for i, line in enumerate(lines):
                        if line.startswith('#'):
                            # Insert timestamp after title
                            lines.insert(i + 1, "")
                            lines.insert(i + 2, f"**Last Updated:** {current_date}")
                            break
                    
                    # Write updated content
                    doc_file.write_text('\n'.join(lines), encoding="utf-8")
                    updated_count += 1
                
            except Exception as e:
                self.log_warning(f"Failed to update timestamp in {doc_file}: {e}")
        
        return updated_count


def register() -> BaseOperationModule:
    """Register module for discovery."""
    return RefreshDesignDocsModule()
