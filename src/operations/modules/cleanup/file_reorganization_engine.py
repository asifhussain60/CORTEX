"""
CORTEX Cleanup: File Reorganization Engine

Reorganizes files into proper structure and automatically updates all references.
Tracks moves and updates imports, paths, and links across the codebase.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Set, Optional, Tuple
from dataclasses import dataclass, field
import logging
import shutil
import re

from .file_scanner import FileMetadata, FileCategory, FilePurpose
from .reference_tracker import ReferenceTracker, FileReference

logger = logging.getLogger(__name__)


@dataclass
class ReorganizationRule:
    """Rule for reorganizing files"""
    name: str
    description: str
    source_pattern: str  # Regex pattern for source files
    destination_template: str  # Template for destination path
    category_filter: Optional[FileCategory] = None
    purpose_filter: Optional[FilePurpose] = None
    priority: int = 50  # Higher priority rules execute first


@dataclass
class FileMove:
    """Record of a file move operation"""
    old_path: str
    new_path: str
    reason: str
    timestamp: datetime
    references_updated: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'old_path': self.old_path,
            'new_path': self.new_path,
            'reason': self.reason,
            'timestamp': self.timestamp.isoformat(),
            'references_updated': self.references_updated
        }


class FileReorganizationEngine:
    """
    File reorganization engine with automatic reference updating.
    
    Capabilities:
    - Rule-based file reorganization
    - Automatic Python import updates
    - File path reference updates
    - Markdown link updates
    - Config file reference updates
    - Move tracking and rollback capability
    """
    
    # Default reorganization rules
    DEFAULT_RULES = [
        ReorganizationRule(
            name="scripts_to_category",
            description="Organize scripts into categories",
            source_pattern=r"^scripts/.*\.(py|sh)$",
            destination_template="scripts/{category}/{filename}",
            priority=80
        ),
        ReorganizationRule(
            name="tests_to_hierarchy",
            description="Organize tests into proper hierarchy",
            source_pattern=r"^tests/test_.*\.py$",
            destination_template="tests/{component}/{filename}",
            category_filter=FileCategory.TEST,
            priority=75
        ),
        ReorganizationRule(
            name="docs_to_category",
            description="Organize docs by category",
            source_pattern=r"^docs/.*\.md$",
            destination_template="docs/{doc_category}/{filename}",
            category_filter=FileCategory.DOCUMENTATION,
            priority=70
        ),
        ReorganizationRule(
            name="deployment_files_to_reports",
            description="Move deployment logs and validation files to cortex-brain/documents/reports",
            source_pattern=r"^(deploy-log|deploy-output|deployment-validation|ado-validation|alignment_result)\.(txt|json)$",
            destination_template="cortex-brain/documents/reports/{filename}",
            priority=95
        ),
        ReorganizationRule(
            name="patches_to_artifacts",
            description="Move patch files to cortex-brain/artifacts",
            source_pattern=r"^.*\.patch$",
            destination_template="cortex-brain/artifacts/{filename}",
            priority=92
        ),
        ReorganizationRule(
            name="diagrams_to_docs",
            description="Move diagram files to docs/diagrams",
            source_pattern=r"^.*\.(svg|png|jpg|jpeg|drawio)$",
            destination_template="docs/diagrams/{filename}",
            priority=91
        ),
        ReorganizationRule(
            name="root_cleanup",
            description="Move misplaced files from root to scripts/misc",
            source_pattern=r"^[^/]+\.(py|sh|md|txt|json|yaml|yml|ini|backup|bak|old)$",
            destination_template="scripts/misc/{filename}",
            priority=90
        )
    ]
    
    def __init__(self, project_root: Path, reference_tracker: ReferenceTracker):
        """
        Initialize reorganization engine.
        
        Args:
            project_root: Root directory of project
            reference_tracker: Reference tracker instance
        """
        self.project_root = project_root
        self.reference_tracker = reference_tracker
        
        # Reorganization rules
        self.rules: List[ReorganizationRule] = self.DEFAULT_RULES.copy()
        
        # Move tracking
        self.moves: List[FileMove] = []
        self.move_map: Dict[str, str] = {}  # old_path -> new_path
        
        # Statistics
        self.total_moved = 0
        self.total_references_updated = 0
        self.failed_moves = 0
    
    def add_rule(self, rule: ReorganizationRule) -> None:
        """Add custom reorganization rule"""
        self.rules.append(rule)
        # Sort by priority (higher first)
        self.rules.sort(key=lambda r: r.priority, reverse=True)
    
    def analyze_reorganization(self, files: Dict[str, FileMetadata]) -> Dict[str, str]:
        """
        Analyze files and determine reorganization plan.
        
        Args:
            files: Dictionary of relative_path -> FileMetadata
            
        Returns:
            Dictionary of old_path -> new_path for all moves
        """
        logger.info(f"Analyzing {len(files)} files for reorganization...")
        
        reorganization_plan = {}
        
        for relative_path, metadata in files.items():
            # Skip protected files
            if metadata.is_protected:
                continue
            
            # Apply rules to find destination
            new_path = self._apply_rules(metadata)
            
            if new_path and new_path != relative_path:
                reorganization_plan[relative_path] = new_path
        
        logger.info(f"Reorganization plan: {len(reorganization_plan)} files to move")
        
        return reorganization_plan
    
    def _apply_rules(self, metadata: FileMetadata) -> Optional[str]:
        """Apply reorganization rules to file"""
        for rule in self.rules:
            # Check category filter
            if rule.category_filter and metadata.category != rule.category_filter:
                continue
            
            # Check purpose filter
            if rule.purpose_filter and metadata.purpose != rule.purpose_filter:
                continue
            
            # Check pattern match
            if re.match(rule.source_pattern, metadata.relative_path):
                # Generate destination path
                destination = self._generate_destination(metadata, rule)
                
                if destination:
                    return destination
        
        return None
    
    def _generate_destination(self, metadata: FileMetadata, rule: ReorganizationRule) -> Optional[str]:
        """Generate destination path from template"""
        try:
            # Prepare template variables
            variables = {
                'filename': Path(metadata.relative_path).name,
                'category': self._infer_script_category(metadata),
                'component': self._infer_test_component(metadata),
                'doc_category': self._infer_doc_category(metadata),
                'extension': metadata.extension
            }
            
            # Apply template
            destination = rule.destination_template.format(**variables)
            
            return destination
            
        except Exception as e:
            logger.error(f"Error generating destination for {metadata.relative_path}: {e}")
            return None
    
    def _infer_script_category(self, metadata: FileMetadata) -> str:
        """Infer script category from filename and content"""
        name = Path(metadata.relative_path).name.lower()
        
        if any(word in name for word in ['test', 'validate', 'verify']):
            return 'testing'
        elif any(word in name for word in ['deploy', 'build', 'release']):
            return 'deployment'
        elif any(word in name for word in ['cleanup', 'maintain', 'optimize']):
            return 'maintenance'
        elif any(word in name for word in ['migrate', 'convert', 'transform']):
            return 'migration'
        elif any(word in name for word in ['fix', 'patch']):
            return 'fixes'
        else:
            return 'utilities'
    
    def _infer_test_component(self, metadata: FileMetadata) -> str:
        """Infer test component from filename"""
        name = Path(metadata.relative_path).name.lower()
        
        # Extract component from test_<component>_*.py
        match = re.match(r'test_(\w+?)(?:_|\.)', name)
        if match:
            component = match.group(1)
            
            # Map to logical components
            if component in ['tier0', 'tier1', 'tier2', 'tier3']:
                return f"brain/{component}"
            elif component in ['agent', 'agents']:
                return 'agents'
            elif component in ['orchestrator', 'orchestrators']:
                return 'orchestrators'
            elif component in ['operation', 'operations']:
                return 'operations'
            else:
                return component
        
        return 'misc'
    
    def _infer_doc_category(self, metadata: FileMetadata) -> str:
        """Infer documentation category"""
        name = Path(metadata.relative_path).name.lower()
        path = metadata.relative_path.lower()
        
        if 'api' in name or 'reference' in name:
            return 'api'
        elif 'guide' in name or 'tutorial' in name or 'howto' in name:
            return 'guides'
        elif 'design' in name or 'architecture' in name:
            return 'architecture'
        elif 'plan' in name or 'roadmap' in name:
            return 'planning'
        elif 'report' in name or 'status' in name or 'summary' in name:
            return 'reports'
        elif 'implementation' in name or 'impl' in name:
            return 'implementation'
        else:
            return 'general'
    
    def execute_reorganization(
        self,
        reorganization_plan: Dict[str, str],
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Execute file reorganization with reference updates.
        
        Args:
            reorganization_plan: Dictionary of old_path -> new_path
            dry_run: If True, only simulate moves
            
        Returns:
            Dictionary with reorganization results
        """
        logger.info(f"Executing reorganization: {len(reorganization_plan)} files")
        
        moved_files = []
        failed_moves = []
        total_references_updated = 0
        
        for old_path, new_path in reorganization_plan.items():
            try:
                # Get reference update instructions
                update_instructions = self.reference_tracker.get_update_instructions(old_path, new_path)
                
                if dry_run:
                    logger.info(f"[DRY RUN] Would move: {old_path} → {new_path}")
                    logger.info(f"[DRY RUN] Would update {len(update_instructions)} references")
                    moved_files.append(old_path)
                    total_references_updated += len(update_instructions)
                else:
                    # Execute move
                    success = self._move_file(old_path, new_path)
                    
                    if success:
                        # Update references
                        updated_count = self._update_references(update_instructions)
                        
                        # Record move
                        move = FileMove(
                            old_path=old_path,
                            new_path=new_path,
                            reason="Reorganization rule applied",
                            timestamp=datetime.now(),
                            references_updated=[inst['file'] for inst in update_instructions]
                        )
                        self.moves.append(move)
                        self.move_map[old_path] = new_path
                        
                        moved_files.append(old_path)
                        total_references_updated += updated_count
                        self.total_moved += 1
                        self.total_references_updated += updated_count
                        
                        logger.info(f"Moved: {old_path} → {new_path} (updated {updated_count} references)")
                    else:
                        failed_moves.append({
                            'old_path': old_path,
                            'new_path': new_path,
                            'error': "Move failed"
                        })
                        self.failed_moves += 1
            
            except Exception as e:
                logger.error(f"Error moving {old_path}: {e}")
                failed_moves.append({
                    'old_path': old_path,
                    'new_path': new_path,
                    'error': str(e)
                })
                self.failed_moves += 1
        
        results = {
            'dry_run': dry_run,
            'moved_count': len(moved_files),
            'failed_count': len(failed_moves),
            'references_updated': total_references_updated,
            'moved_files': moved_files,
            'failed_moves': failed_moves
        }
        
        logger.info(f"Reorganization complete: {len(moved_files)} files moved, {total_references_updated} references updated")
        
        return results
    
    def _move_file(self, old_path: str, new_path: str) -> bool:
        """Move file to new location"""
        try:
            source = self.project_root / old_path
            destination = self.project_root / new_path
            
            # Validate source exists
            if not source.exists():
                logger.error(f"Source file does not exist: {old_path}")
                return False
            
            # Create destination directory
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if destination already exists
            if destination.exists():
                logger.warning(f"Destination already exists: {new_path}")
                # Generate unique name
                counter = 1
                while destination.exists():
                    stem = destination.stem
                    suffix = destination.suffix
                    destination = destination.parent / f"{stem}_{counter}{suffix}"
                    counter += 1
                
                logger.info(f"Using alternative destination: {destination.relative_to(self.project_root)}")
            
            # Move file
            shutil.move(str(source), str(destination))
            
            return True
            
        except Exception as e:
            logger.error(f"Error moving file {old_path}: {e}")
            return False
    
    def _update_references(self, update_instructions: List[Dict[str, Any]]) -> int:
        """Update all references for a moved file"""
        updated_count = 0
        
        # Group by file for efficient updating
        updates_by_file: Dict[str, List[Dict[str, Any]]] = {}
        for instruction in update_instructions:
            file_path = instruction['file']
            if file_path not in updates_by_file:
                updates_by_file[file_path] = []
            updates_by_file[file_path].append(instruction)
        
        # Update each file
        for file_path, instructions in updates_by_file.items():
            try:
                if self._update_file_references(file_path, instructions):
                    updated_count += len(instructions)
            except Exception as e:
                logger.error(f"Error updating references in {file_path}: {e}")
        
        return updated_count
    
    def _update_file_references(self, file_path: str, instructions: List[Dict[str, Any]]) -> bool:
        """Update references in a single file"""
        try:
            full_path = self.project_root / file_path
            
            if not full_path.exists():
                logger.warning(f"File not found for reference update: {file_path}")
                return False
            
            # Read file content
            content = full_path.read_text(encoding='utf-8')
            
            # Apply updates (in reverse line order to preserve line numbers)
            instructions_sorted = sorted(instructions, key=lambda x: x['line'], reverse=True)
            
            lines = content.split('\n')
            
            for instruction in instructions_sorted:
                line_num = instruction['line'] - 1  # Convert to 0-indexed
                
                if 0 <= line_num < len(lines):
                    old_ref = instruction['old_reference']
                    new_ref = instruction['new_reference']
                    
                    # Replace reference in line
                    lines[line_num] = lines[line_num].replace(old_ref, new_ref)
            
            # Write updated content
            updated_content = '\n'.join(lines)
            full_path.write_text(updated_content, encoding='utf-8')
            
            logger.debug(f"Updated {len(instructions)} references in {file_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating file {file_path}: {e}")
            return False
    
    def generate_move_manifest(self, output_path: Optional[Path] = None) -> Path:
        """Generate manifest of all file moves"""
        if output_path is None:
            output_path = self.project_root / 'cortex-brain' / 'cleanup-reports' / f'reorganization-manifest-{datetime.now().strftime("%Y%m%d-%H%M%S")}.json'
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        import json
        manifest = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_moved': self.total_moved,
                'total_references_updated': self.total_references_updated,
                'failed_moves': self.failed_moves
            },
            'moves': [move.to_dict() for move in self.moves]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"Reorganization manifest saved: {output_path}")
        
        return output_path
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get reorganization statistics"""
        return {
            'total_moved': self.total_moved,
            'total_references_updated': self.total_references_updated,
            'failed_moves': self.failed_moves,
            'total_rules': len(self.rules)
        }
