"""
PersonaStore - Persistent user preference management

Authority: Phase 37 S4
Handles YAML-based storage and retrieval of user persona preferences across sessions
"""

import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

from cortex.orchestrators.persona.models import PersonaId, DepthLevel


class PersonaStore:
    """Persistent storage for user persona preferences"""

    def __init__(self, storage_path: str = None):
        """
        Initialize PersonaStore with storage path.
        
        Args:
            storage_path: Path to YAML file for persona storage.
                         Defaults to cortex_brain/state/user_personas.yaml
        """
        if storage_path is None:
            storage_path = "cortex_brain/state/user_personas.yaml"
        
        self.storage_path = Path(storage_path)
        self._ensure_storage_ready()

    def _ensure_storage_ready(self) -> None:
        """Ensure storage directory and file exist"""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.storage_path.exists():
            self._write_store({})

    def _read_store(self) -> Dict[str, Any]:
        """Read personas from storage"""
        try:
            if not self.storage_path.exists():
                return {}
            
            with open(self.storage_path, "r") as f:
                data = yaml.safe_load(f)
                return data if data else {}
        except (yaml.YAMLError, IOError):
            # Corrupted file - recover with empty store
            return {}

    def _write_store(self, data: Dict[str, Any]) -> bool:
        """Write personas to storage"""
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.storage_path, "w") as f:
                yaml.dump(data, f, default_flow_style=False)
            
            return True
        except Exception:
            return False

    def create_user_persona(
        self,
        user_id: str,
        persona: PersonaId,
        depth: DepthLevel,
    ) -> bool:
        """
        Create new user persona preference.
        
        Args:
            user_id: Unique user identifier
            persona: Selected PersonaId enum value
            depth: Selected DepthLevel enum value
        
        Returns:
            True if creation successful, False otherwise
        """
        if not user_id or not user_id.strip():
            return False
        
        store = self._read_store()
        
        if user_id in store:
            return False  # User already exists
        
        now = datetime.now().isoformat()
        
        store[user_id] = {
            "persona": persona.value,
            "depth": depth.value,
            "created_at": now,
            "last_active": now,
            "overrides": [],
        }
        
        return self._write_store(store)

    def get_user_persona(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user persona preference.
        
        Args:
            user_id: User identifier
        
        Returns:
            User persona data dict or None if not found
        """
        store = self._read_store()
        
        if user_id not in store:
            return None
        
        # Update last_active
        store[user_id]["last_active"] = datetime.now().isoformat()
        self._write_store(store)
        
        return store[user_id]

    def update_user_persona(
        self,
        user_id: str,
        persona: PersonaId,
        depth: DepthLevel,
    ) -> bool:
        """
        Update user persona preference.
        
        Args:
            user_id: User identifier
            persona: New PersonaId
            depth: New DepthLevel
        
        Returns:
            True if successful, False otherwise
        """
        store = self._read_store()
        
        if user_id not in store:
            # Create if doesn't exist
            return self.create_user_persona(user_id, persona, depth)
        
        store[user_id]["persona"] = persona.value
        store[user_id]["depth"] = depth.value
        store[user_id]["last_active"] = datetime.now().isoformat()
        
        return self._write_store(store)

    def delete_user_persona(self, user_id: str) -> bool:
        """
        Delete user persona preference.
        
        Args:
            user_id: User identifier
        
        Returns:
            True if successful, False otherwise
        """
        store = self._read_store()
        
        if user_id not in store:
            return False
        
        del store[user_id]
        return self._write_store(store)

    def list_all_users(self) -> List[str]:
        """
        Get list of all stored user IDs.
        
        Returns:
            List of user IDs
        """
        store = self._read_store()
        return list(store.keys())

    def add_depth_override(
        self,
        user_id: str,
        override_level: DepthLevel,
        context: str = None,
    ) -> bool:
        """
        Add depth override for user.
        
        Args:
            user_id: User identifier
            override_level: Override depth level
            context: Optional context for override
        
        Returns:
            True if successful, False otherwise
        """
        store = self._read_store()
        
        if user_id not in store:
            return False
        
        override = {
            "level": override_level.value,
            "context": context,
            "added_at": datetime.now().isoformat(),
        }
        
        store[user_id]["overrides"].append(override)
        store[user_id]["last_active"] = datetime.now().isoformat()
        
        return self._write_store(store)

    def get_active_overrides(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get active overrides for user.
        
        Args:
            user_id: User identifier
        
        Returns:
            List of active override dicts
        """
        store = self._read_store()
        
        if user_id not in store:
            return []
        
        return store[user_id].get("overrides", [])

    def bulk_create_users(self, users_data: List[Dict[str, Any]]) -> bool:
        """
        Create multiple users efficiently.
        
        Args:
            users_data: List of dicts with user_id, persona, depth
        
        Returns:
            True if all successful, False otherwise
        """
        store = self._read_store()
        now = datetime.now().isoformat()
        
        for user_data in users_data:
            user_id = user_data.get("user_id")
            persona = user_data.get("persona")
            depth = user_data.get("depth")
            
            if not user_id or user_id in store:
                return False
            
            store[user_id] = {
                "persona": persona.value,
                "depth": depth.value,
                "created_at": now,
                "last_active": now,
                "overrides": [],
            }
        
        return self._write_store(store)

    def export_users(self, export_path: str) -> bool:
        """
        Export all users to separate file.
        
        Args:
            export_path: Path to export file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            store = self._read_store()
            
            export_file = Path(export_path)
            export_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_file, "w") as f:
                yaml.dump(store, f, default_flow_style=False)
            
            return True
        except Exception:
            return False

    def clear_all(self) -> bool:
        """
        Clear all stored personas (destructive).
        
        Returns:
            True if successful, False otherwise
        """
        return self._write_store({})

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about stored personas.
        
        Returns:
            Dict with user_count, personas_dist, etc.
        """
        store = self._read_store()
        
        persona_counts = {}
        depth_counts = {}
        
        for user_data in store.values():
            persona = user_data.get("persona")
            depth = user_data.get("depth")
            
            persona_counts[persona] = persona_counts.get(persona, 0) + 1
            depth_counts[depth] = depth_counts.get(depth, 0) + 1
        
        return {
            "user_count": len(store),
            "persona_distribution": persona_counts,
            "depth_distribution": depth_counts,
            "storage_path": str(self.storage_path),
        }
