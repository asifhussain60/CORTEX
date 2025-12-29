"""
Plan Manifest Tracker - Active Plans Registry
=============================================

Manages active-plans-manifest.yaml for tracking all active plans.

Purpose:
- Register approved plans in manifest
- Track plan metadata (status, dates, complexity)
- Enable plan discovery and monitoring
- Support cleanup operations

Author: Asif Hussain
Date: December 17, 2025
Version: 1.0.0
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from src.operations.modules.orchestration.audit_logger import get_audit_logger

logger = logging.getLogger(__name__)
audit_logger = get_audit_logger()


class PlanManifestTracker:
    """
    Tracks active plans in manifest file.
    
    Manifest Location:
    cortex-brain/documents/planning/active-plans-manifest.yaml
    
    Manifest Structure:
    ```yaml
    version: "1.0"
    last_updated: "2025-12-17T10:30:00"
    plans:
      - plan_id: "user-auth-v1"
        title: "User Authentication System"
        status: "active"
        complexity_tier: 3
        created_date: "2025-12-15"
        approved_date: "2025-12-15"
        folder: "active/user-auth-v1"
        phases: 4
        estimated_days: 7
    ```
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize manifest tracker.
        
        Args:
            project_root: Root directory of CORTEX project
        """
        self.project_root = Path(project_root)
        self.manifest_file = (
            self.project_root / "cortex-brain" / "documents" / "planning" / "active-plans-manifest.yaml"
        )
        
        # Ensure parent directory exists
        self.manifest_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load or create manifest
        self.manifest = self._load_manifest()
        
        logger.info("✅ PlanManifestTracker initialized")
    
    def register_plan(
        self,
        plan_id: str,
        title: str,
        status: str,
        complexity_tier: int,
        created_date: str,
        approved_date: str,
        folder: str,
        phases: int,
        estimated_days: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Register plan in manifest.
        
        Args:
            plan_id: Plan identifier
            title: Plan title
            status: Plan status (active, in_progress, etc.)
            complexity_tier: Complexity tier (1-4)
            created_date: Creation date (ISO format)
            approved_date: Approval date (ISO format)
            folder: Folder path relative to planning/
            phases: Number of phases
            estimated_days: Estimated duration in days
            metadata: Additional metadata (optional)
        """
        logger.info(f"📋 Registering plan in manifest: {plan_id}")
        
        # Create plan entry
        plan_entry = {
            "plan_id": plan_id,
            "title": title,
            "status": status,
            "complexity_tier": complexity_tier,
            "created_date": created_date,
            "approved_date": approved_date,
            "folder": folder,
            "phases": phases,
            "estimated_days": estimated_days
        }
        
        # Add optional metadata
        if metadata:
            plan_entry.update(metadata)
        
        # Add or update in manifest
        existing_plans = self.manifest.get("plans", [])
        
        # Remove existing entry if present
        existing_plans = [p for p in existing_plans if p.get("plan_id") != plan_id]
        
        # Add new entry
        existing_plans.append(plan_entry)
        
        # Update manifest
        self.manifest["plans"] = existing_plans
        self.manifest["last_updated"] = datetime.now().isoformat()
        
        # Persist
        self._save_manifest()
        
        logger.info(f"✅ Plan registered: {plan_id}")
        
        # Audit: Manifest updated (plan registered)
        audit_logger.log_event(
            event_type="manifest_updated",
            session_id="manifest-ops",
            plan_id=plan_id,
            orchestrator="PlanManifestTracker",
            phase="registration",
            metadata={
                "operation": "register_plan",
                "status": status,
                "complexity_tier": complexity_tier,
                "phases": phases,
                "estimated_days": estimated_days
            }
        )
    
    def update_plan_status(self, plan_id: str, status: str):
        """
        Update plan status in manifest.
        
        Args:
            plan_id: Plan identifier
            status: New status
        """
        plans = self.manifest.get("plans", [])
        
        old_status = None
        for plan in plans:
            if plan.get("plan_id") == plan_id:
                old_status = plan.get("status")
                plan["status"] = status
                plan["last_updated"] = datetime.now().isoformat()
                break
        
        self.manifest["last_updated"] = datetime.now().isoformat()
        self._save_manifest()
        
        logger.info(f"✅ Updated plan status: {plan_id} → {status}")
        
        # Audit: Manifest updated (status change)
        if old_status is not None:
            audit_logger.log_event(
                event_type="manifest_updated",
                session_id="manifest-ops",
                plan_id=plan_id,
                orchestrator="PlanManifestTracker",
                phase="status_update",
                metadata={
                    "operation": "update_plan_status",
                    "old_status": old_status,
                    "new_status": status
                }
            )
    
    def get_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """
        Get plan metadata from manifest.
        
        Args:
            plan_id: Plan identifier
            
        Returns:
            Plan metadata dict, or None if not found
        """
        plans = self.manifest.get("plans", [])
        
        for plan in plans:
            if plan.get("plan_id") == plan_id:
                return plan
        
        return None
    
    def get_all_plans(self) -> List[Dict[str, Any]]:
        """Get all plans from manifest."""
        return self.manifest.get("plans", [])
    
    def get_plans_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Get plans by status.
        
        Args:
            status: Status filter (active, in_progress, etc.)
            
        Returns:
            List of matching plans
        """
        plans = self.manifest.get("plans", [])
        return [p for p in plans if p.get("status") == status]
    
    def remove_plan(self, plan_id: str):
        """
        Remove plan from manifest.
        
        Args:
            plan_id: Plan identifier
        """
        plans = self.manifest.get("plans", [])
        plans = [p for p in plans if p.get("plan_id") != plan_id]
        
        self.manifest["plans"] = plans
        self.manifest["last_updated"] = datetime.now().isoformat()
        
        self._save_manifest()
        
        logger.info(f"✅ Removed plan from manifest: {plan_id}")
    
    def _load_manifest(self) -> Dict[str, Any]:
        """Load manifest from file."""
        if not self.manifest_file.exists():
            return self._create_default_manifest()
        
        try:
            with open(self.manifest_file, 'r', encoding='utf-8') as f:
                manifest = yaml.safe_load(f)
            
            if manifest is None:
                return self._create_default_manifest()
            
            logger.info(f"✅ Loaded manifest with {len(manifest.get('plans', []))} plans")
            return manifest
        except Exception as e:
            logger.error(f"Failed to load manifest: {e}")
            return self._create_default_manifest()
    
    def _save_manifest(self):
        """Save manifest to file."""
        try:
            with open(self.manifest_file, 'w', encoding='utf-8') as f:
                yaml.dump(
                    self.manifest,
                    f,
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True
                )
        except Exception as e:
            logger.error(f"Failed to save manifest: {e}")
    
    def _create_default_manifest(self) -> Dict[str, Any]:
        """Create default manifest structure."""
        return {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "plans": []
        }
