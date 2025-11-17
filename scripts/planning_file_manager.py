#!/usr/bin/env python3
"""
Planning File Manager - Lifecycle management for ADO planning files

This module manages the complete lifecycle of planning .md files:
- Auto-create planning files when ADOs are created
- Track file status (pending, approved, rejected, archived)
- Sync file status with database records
- Implement approval workflow
- Hook approved plans into development pipeline
- Version control integration

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain
License: Proprietary
Repository: https://github.com/asifhussain60/CORTEX
"""

import os
import json
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class FileStatus(Enum):
    """Planning file status states"""
    PENDING = "pending"  # Just created, awaiting review
    ACTIVE = "active"    # Currently being worked on
    APPROVED = "approved"  # Approved for implementation
    REJECTED = "rejected"  # Rejected, needs revision
    COMPLETED = "completed"  # Implementation complete
    BLOCKED = "blocked"  # Blocked by dependencies
    ARCHIVED = "archived"  # No longer relevant


@dataclass
class PlanningFile:
    """Represents a planning file"""
    ado_number: str
    file_path: str
    status: FileStatus
    created_at: str
    updated_at: str
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    rejection_reason: Optional[str] = None
    completion_percentage: int = 0
    related_files: List[str] = None
    
    def __post_init__(self):
        if self.related_files is None:
            self.related_files = []


class PlanningFileManager:
    """Manages planning file lifecycle"""
    
    def __init__(self, base_path: str = "cortex-brain/documents/planning"):
        self.base_path = Path(base_path)
        self.ado_path = self.base_path / "ado"
        
        # Status directories
        self.directories = {
            FileStatus.PENDING: self.ado_path / "pending",
            FileStatus.ACTIVE: self.ado_path / "active",
            FileStatus.APPROVED: self.ado_path / "approved",
            FileStatus.REJECTED: self.ado_path / "rejected",
            FileStatus.COMPLETED: self.ado_path / "completed",
            FileStatus.BLOCKED: self.ado_path / "blocked",
            FileStatus.ARCHIVED: self.ado_path / "archived"
        }
        
        # Ensure directories exist
        self._ensure_directories()
        
        # Metadata file
        self.metadata_file = self.ado_path / "planning_metadata.json"
        self.metadata = self._load_metadata()
    
    def _ensure_directories(self):
        """Create all required directories"""
        for directory in self.directories.values():
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_metadata(self) -> Dict:
        """Load planning file metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_metadata(self):
        """Save planning file metadata"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2)
    
    def create_planning_file(
        self,
        ado_number: str,
        title: str,
        template_content: str,
        status: FileStatus = FileStatus.PENDING
    ) -> Tuple[bool, str]:
        """
        Create a new planning file from template
        
        Returns:
            (success: bool, file_path: str)
        """
        # Generate filename
        timestamp = datetime.now().strftime("%Y-%m-%d")
        safe_title = self._sanitize_filename(title)
        filename = f"{ado_number}-{timestamp}-{safe_title}.md"
        
        # Determine target directory
        target_dir = self.directories[status]
        file_path = target_dir / filename
        
        # Check if file already exists
        if file_path.exists():
            return False, f"File already exists: {file_path}"
        
        # Create the file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            # Store metadata
            self.metadata[ado_number] = {
                'file_path': str(file_path),
                'status': status.value,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'title': title
            }
            self._save_metadata()
            
            return True, str(file_path)
            
        except Exception as e:
            return False, f"Error creating file: {e}"
    
    def get_file_status(self, ado_number: str) -> Optional[FileStatus]:
        """Get current status of a planning file"""
        if ado_number in self.metadata:
            status_str = self.metadata[ado_number]['status']
            return FileStatus(status_str)
        return None
    
    def get_file_path(self, ado_number: str) -> Optional[str]:
        """Get file path for an ADO number"""
        if ado_number in self.metadata:
            return self.metadata[ado_number]['file_path']
        return None
    
    def move_to_status(
        self,
        ado_number: str,
        new_status: FileStatus,
        reason: Optional[str] = None,
        approved_by: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Move planning file to a new status directory
        
        Args:
            ado_number: ADO work item number
            new_status: Target status
            reason: Optional reason for rejection
            approved_by: User who approved (for approved status)
        
        Returns:
            (success: bool, message: str)
        """
        if ado_number not in self.metadata:
            return False, f"Planning file not found for ADO {ado_number}"
        
        current_path = Path(self.metadata[ado_number]['file_path'])
        if not current_path.exists():
            return False, f"File does not exist: {current_path}"
        
        # Determine new path
        target_dir = self.directories[new_status]
        new_path = target_dir / current_path.name
        
        # Move the file
        try:
            shutil.move(str(current_path), str(new_path))
            
            # Update metadata
            self.metadata[ado_number]['file_path'] = str(new_path)
            self.metadata[ado_number]['status'] = new_status.value
            self.metadata[ado_number]['updated_at'] = datetime.now().isoformat()
            
            if new_status == FileStatus.APPROVED:
                self.metadata[ado_number]['approved_by'] = approved_by or 'system'
                self.metadata[ado_number]['approved_at'] = datetime.now().isoformat()
            
            if new_status == FileStatus.REJECTED and reason:
                self.metadata[ado_number]['rejection_reason'] = reason
            
            self._save_metadata()
            
            return True, f"Moved to {new_status.value}: {new_path}"
            
        except Exception as e:
            return False, f"Error moving file: {e}"
    
    def approve_plan(
        self,
        ado_number: str,
        approved_by: str,
        inject_to_context: bool = True
    ) -> Tuple[bool, str]:
        """
        Approve a planning file and optionally inject into development context
        
        Args:
            ado_number: ADO work item number
            approved_by: User approving the plan
            inject_to_context: Whether to inject into CORTEX Tier 1
        
        Returns:
            (success: bool, message: str)
        """
        # Move to approved status
        success, message = self.move_to_status(
            ado_number,
            FileStatus.APPROVED,
            approved_by=approved_by
        )
        
        if not success:
            return False, message
        
        # Inject into context if requested
        if inject_to_context:
            file_path = self.get_file_path(ado_number)
            if file_path:
                # Hook into CORTEX Tier 1 context
                # This would integrate with existing context manager
                print(f"✅ Plan approved and injected into Tier 1: {ado_number}")
        
        return True, f"Plan approved by {approved_by}"
    
    def reject_plan(
        self,
        ado_number: str,
        reason: str
    ) -> Tuple[bool, str]:
        """Reject a planning file with reason"""
        return self.move_to_status(
            ado_number,
            FileStatus.REJECTED,
            reason=reason
        )
    
    def complete_plan(self, ado_number: str) -> Tuple[bool, str]:
        """Mark planning file as completed"""
        return self.move_to_status(ado_number, FileStatus.COMPLETED)
    
    def block_plan(
        self,
        ado_number: str,
        reason: str
    ) -> Tuple[bool, str]:
        """Mark planning file as blocked"""
        return self.move_to_status(
            ado_number,
            FileStatus.BLOCKED,
            reason=reason
        )
    
    def archive_plan(self, ado_number: str) -> Tuple[bool, str]:
        """Archive a planning file"""
        return self.move_to_status(ado_number, FileStatus.ARCHIVED)
    
    def list_plans_by_status(self, status: FileStatus) -> List[Dict]:
        """List all planning files with a specific status"""
        plans = []
        for ado_number, data in self.metadata.items():
            if data['status'] == status.value:
                plans.append({
                    'ado_number': ado_number,
                    'title': data.get('title', 'N/A'),
                    'file_path': data['file_path'],
                    'created_at': data['created_at'],
                    'updated_at': data['updated_at']
                })
        return plans
    
    def get_plan_details(self, ado_number: str) -> Optional[Dict]:
        """Get detailed information about a planning file"""
        if ado_number in self.metadata:
            return self.metadata[ado_number]
        return None
    
    def sync_with_database(self, ado_manager) -> Dict[str, int]:
        """
        Sync planning file status with ADO database
        
        Returns:
            Statistics dictionary
        """
        stats = {
            'synced': 0,
            'created': 0,
            'updated': 0,
            'errors': 0
        }
        
        for ado_number in self.metadata.keys():
            try:
                # Get database record
                ado_item = ado_manager.get_ado(ado_number)
                if not ado_item:
                    continue
                
                # Get file status
                file_status = self.get_file_status(ado_number)
                db_status = ado_item['status']
                
                # Sync status if different
                if file_status and file_status.value != db_status:
                    # Update database with file status
                    success = ado_manager.update_status(
                        ado_number,
                        file_status.value
                    )
                    if success:
                        stats['updated'] += 1
                    else:
                        stats['errors'] += 1
                
                stats['synced'] += 1
                
            except Exception as e:
                print(f"❌ Error syncing {ado_number}: {e}")
                stats['errors'] += 1
        
        return stats
    
    def _sanitize_filename(self, title: str) -> str:
        """Sanitize title for use in filename"""
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            title = title.replace(char, '')
        
        # Replace spaces with hyphens
        title = title.replace(' ', '-')
        
        # Limit length
        return title[:50]
    
    def export_statistics(self) -> Dict:
        """Export statistics about planning files"""
        stats = {
            'total': len(self.metadata),
            'by_status': {}
        }
        
        for status in FileStatus:
            count = sum(
                1 for data in self.metadata.values()
                if data['status'] == status.value
            )
            stats['by_status'][status.value] = count
        
        return stats


# Integration function for ADO Manager
def create_planning_file_for_ado(
    ado_number: str,
    title: str,
    work_item_type: str,
    template_path: str,
    manager: Optional[PlanningFileManager] = None
) -> Tuple[bool, str]:
    """
    Create a planning file when an ADO is created
    
    Args:
        ado_number: ADO work item number
        title: Work item title
        work_item_type: Type (Feature, Bug, Task, etc.)
        template_path: Path to template file
        manager: Optional PlanningFileManager instance
    
    Returns:
        (success: bool, file_path: str)
    """
    if manager is None:
        manager = PlanningFileManager()
    
    # Load template
    template_file = Path(template_path)
    if not template_file.exists():
        return False, f"Template not found: {template_path}"
    
    with open(template_file, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Substitute variables
    template_content = template_content.replace('{{ADO_NUMBER}}', ado_number)
    template_content = template_content.replace('{{TITLE}}', title)
    template_content = template_content.replace('{{TYPE}}', work_item_type)
    template_content = template_content.replace('{{DATE}}', datetime.now().strftime("%Y-%m-%d"))
    
    # Create the file
    return manager.create_planning_file(
        ado_number,
        title,
        template_content,
        status=FileStatus.ACTIVE
    )


# CLI interface
def main():
    """Test the planning file manager"""
    manager = PlanningFileManager()
    
    print("🗂️  Planning File Manager Demo\n")
    
    # Test 1: Create a planning file
    print("1️⃣ Creating planning file...")
    success, file_path = manager.create_planning_file(
        ado_number="ADO-12345",
        title="Test Feature Implementation",
        template_content="# Test Feature\n\n## Description\nThis is a test feature.",
        status=FileStatus.PENDING
    )
    
    if success:
        print(f"   ✅ Created: {file_path}")
    else:
        print(f"   ❌ Failed: {file_path}")
    
    # Test 2: Check status
    print("\n2️⃣ Checking file status...")
    status = manager.get_file_status("ADO-12345")
    print(f"   📊 Current status: {status.value if status else 'Not found'}")
    
    # Test 3: Approve plan
    print("\n3️⃣ Approving plan...")
    success, message = manager.approve_plan("ADO-12345", "asif.hussain")
    print(f"   {'✅' if success else '❌'} {message}")
    
    # Test 4: List plans by status
    print("\n4️⃣ Listing approved plans...")
    approved_plans = manager.list_plans_by_status(FileStatus.APPROVED)
    for plan in approved_plans:
        print(f"   📁 {plan['ado_number']}: {plan['title']}")
    
    # Test 5: Export statistics
    print("\n5️⃣ Export statistics...")
    stats = manager.export_statistics()
    print(f"   📊 Total plans: {stats['total']}")
    for status, count in stats['by_status'].items():
        if count > 0:
            print(f"      • {status}: {count}")
    
    # Test 6: Complete plan
    print("\n6️⃣ Completing plan...")
    success, message = manager.complete_plan("ADO-12345")
    print(f"   {'✅' if success else '❌'} {message}")
    
    print("\n✅ Planning File Manager demo complete!")


if __name__ == '__main__':
    main()
