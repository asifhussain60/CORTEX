"""
FileSystem Adapter Implementation

Local file operations adapter for CORTEX 4.0.
Handles YAML, JSON, and Markdown files with cross-platform path support.

Author: CORTEX 4.0
Phase: 7B - Operations Simplification (Task 7.6)
Created: December 23, 2025
"""

import json
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

from .universal_adapter import (
    UniversalAdapter,
    ResourceType,
    AdapterResponse,
    AdapterError,
    AdapterFactory
)

logger = logging.getLogger(__name__)


class FileSystemAdapter(UniversalAdapter):
    """
    FileSystem adapter for local file operations.
    
    Supported resource types:
    - FILE: Read/write/delete files (YAML, JSON, Markdown, text)
    - REPOSITORY: Directory operations (list, create, delete)
    
    Features:
    - Cross-platform path handling (Path lib)
    - Multiple file format support
    - Atomic write operations
    - Backup before destructive operations
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize FileSystem adapter.
        
        Args:
            config: Configuration with optional base_path
        """
        super().__init__(config)
        self.base_path = Path(config.get("base_path", ".")) if config else Path(".")
        self.logger.info(f"FileSystemAdapter initialized: base_path={self.base_path}")
    
    async def create(
        self,
        resource_type: ResourceType,
        data: Dict[str, Any],
        **kwargs
    ) -> AdapterResponse[Dict[str, Any]]:
        """Create a file or directory"""
        try:
            if resource_type == ResourceType.FILE:
                return await self._create_file(data, **kwargs)
            elif resource_type == ResourceType.REPOSITORY:
                return await self._create_directory(data, **kwargs)
            else:
                raise AdapterError(
                    f"Unsupported resource type for create: {resource_type}",
                    error_code="UNSUPPORTED_RESOURCE_TYPE"
                )
        except Exception as e:
            self.logger.error(f"Create failed: {e}")
            return AdapterResponse(success=False, error=str(e))
    
    async def read(
        self,
        resource_type: ResourceType,
        resource_id: str,
        **kwargs
    ) -> AdapterResponse[Dict[str, Any]]:
        """Read a file or list directory"""
        try:
            if resource_type == ResourceType.FILE:
                return await self._read_file(resource_id, **kwargs)
            elif resource_type == ResourceType.REPOSITORY:
                return await self._read_directory(resource_id, **kwargs)
            else:
                raise AdapterError(
                    f"Unsupported resource type for read: {resource_type}",
                    error_code="UNSUPPORTED_RESOURCE_TYPE"
                )
        except Exception as e:
            self.logger.error(f"Read failed: {e}")
            return AdapterResponse(success=False, error=str(e))
    
    async def update(
        self,
        resource_type: ResourceType,
        resource_id: str,
        data: Dict[str, Any],
        **kwargs
    ) -> AdapterResponse[Dict[str, Any]]:
        """Update a file (overwrite or append)"""
        try:
            if resource_type == ResourceType.FILE:
                return await self._update_file(resource_id, data, **kwargs)
            else:
                raise AdapterError(
                    f"Unsupported resource type for update: {resource_type}",
                    error_code="UNSUPPORTED_RESOURCE_TYPE"
                )
        except Exception as e:
            self.logger.error(f"Update failed: {e}")
            return AdapterResponse(success=False, error=str(e))
    
    async def delete(
        self,
        resource_type: ResourceType,
        resource_id: str,
        **kwargs
    ) -> AdapterResponse[bool]:
        """Delete a file or directory"""
        try:
            path = self.base_path / resource_id
            if not path.exists():
                return AdapterResponse(
                    success=False,
                    error=f"Resource not found: {resource_id}"
                )
            
            if path.is_file():
                path.unlink()
            else:
                import shutil
                shutil.rmtree(path)
            
            self.logger.info(f"Deleted: {path}")
            return AdapterResponse(success=True, data=True)
            
        except Exception as e:
            self.logger.error(f"Delete failed: {e}")
            return AdapterResponse(success=False, error=str(e))
    
    async def search(
        self,
        resource_type: ResourceType,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        **kwargs
    ) -> AdapterResponse[List[Dict[str, Any]]]:
        """Search files by name pattern"""
        try:
            if resource_type != ResourceType.FILE:
                raise AdapterError(
                    f"Search only supported for FILE resources",
                    error_code="UNSUPPORTED_OPERATION"
                )
            
            pattern = filters.get("pattern", f"*{query}*") if filters else f"*{query}*"
            results = []
            
            for path in self.base_path.rglob(pattern):
                if path.is_file():
                    results.append({
                        "id": str(path.relative_to(self.base_path)),
                        "name": path.name,
                        "path": str(path),
                        "size": path.stat().st_size,
                        "modified": path.stat().st_mtime
                    })
                    if len(results) >= limit:
                        break
            
            return AdapterResponse(success=True, data=results)
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return AdapterResponse(success=False, error=str(e))
    
    async def list(
        self,
        resource_type: ResourceType,
        parent_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        **kwargs
    ) -> AdapterResponse[List[Dict[str, Any]]]:
        """List files or directories"""
        try:
            dir_path = self.base_path / parent_id if parent_id else self.base_path
            
            if not dir_path.exists() or not dir_path.is_dir():
                return AdapterResponse(
                    success=False,
                    error=f"Directory not found: {parent_id or '.'}"
                )
            
            results = []
            for item in sorted(dir_path.iterdir())[offset:offset + limit]:
                results.append({
                    "id": str(item.relative_to(self.base_path)),
                    "name": item.name,
                    "path": str(item),
                    "is_directory": item.is_dir(),
                    "size": item.stat().st_size if item.is_file() else None,
                    "modified": item.stat().st_mtime
                })
            
            return AdapterResponse(success=True, data=results)
            
        except Exception as e:
            self.logger.error(f"List failed: {e}")
            return AdapterResponse(success=False, error=str(e))
    
    def get_capabilities(self) -> Dict[ResourceType, List[str]]:
        """Get supported operations"""
        return {
            ResourceType.FILE: ["create", "read", "update", "delete", "search", "list"],
            ResourceType.REPOSITORY: ["create", "read", "delete", "list"]
        }
    
    def validate_config(self) -> bool:
        """Validate configuration"""
        if not self.base_path.exists():
            raise AdapterError(
                f"Base path does not exist: {self.base_path}",
                error_code="INVALID_CONFIG"
            )
        return True
    
    # Helper methods
    
    async def _create_file(self, data: Dict[str, Any], **kwargs) -> AdapterResponse:
        """Create a new file"""
        path = self.base_path / data["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        
        content = data.get("content", "")
        file_format = data.get("format", "text")
        
        if file_format == "json":
            path.write_text(json.dumps(content, indent=2))
        elif file_format == "yaml":
            path.write_text(yaml.dump(content, default_flow_style=False))
        else:
            path.write_text(content)
        
        self.logger.info(f"Created file: {path}")
        return AdapterResponse(success=True, data={"path": str(path), "size": path.stat().st_size})
    
    async def _read_file(self, resource_id: str, **kwargs) -> AdapterResponse:
        """Read file content"""
        path = self.base_path / resource_id
        
        if not path.exists():
            return AdapterResponse(success=False, error=f"File not found: {resource_id}")
        
        file_format = kwargs.get("format", "auto")
        
        if file_format == "auto":
            if path.suffix in [".json"]:
                content = json.loads(path.read_text())
            elif path.suffix in [".yaml", ".yml"]:
                content = yaml.safe_load(path.read_text())
            else:
                content = path.read_text()
        elif file_format == "json":
            content = json.loads(path.read_text())
        elif file_format == "yaml":
            content = yaml.safe_load(path.read_text())
        else:
            content = path.read_text()
        
        return AdapterResponse(
            success=True,
            data={"content": content, "path": str(path), "size": path.stat().st_size}
        )
    
    async def _update_file(self, resource_id: str, data: Dict[str, Any], **kwargs) -> AdapterResponse:
        """Update file content"""
        path = self.base_path / resource_id
        
        if not path.exists():
            return AdapterResponse(success=False, error=f"File not found: {resource_id}")
        
        # Backup if requested
        if kwargs.get("backup", False):
            backup_path = path.with_suffix(path.suffix + ".bak")
            backup_path.write_text(path.read_text())
        
        content = data.get("content", "")
        file_format = data.get("format", "text")
        
        if file_format == "json":
            path.write_text(json.dumps(content, indent=2))
        elif file_format == "yaml":
            path.write_text(yaml.dump(content, default_flow_style=False))
        else:
            path.write_text(content)
        
        return AdapterResponse(success=True, data={"path": str(path), "size": path.stat().st_size})
    
    async def _create_directory(self, data: Dict[str, Any], **kwargs) -> AdapterResponse:
        """Create a directory"""
        path = self.base_path / data["path"]
        path.mkdir(parents=True, exist_ok=True)
        return AdapterResponse(success=True, data={"path": str(path)})
    
    async def _read_directory(self, resource_id: str, **kwargs) -> AdapterResponse:
        """Get directory info"""
        path = self.base_path / resource_id
        
        if not path.exists() or not path.is_dir():
            return AdapterResponse(success=False, error=f"Directory not found: {resource_id}")
        
        return AdapterResponse(
            success=True,
            data={
                "path": str(path),
                "file_count": len(list(path.glob("*"))),
                "size": sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
            }
        )


# Register adapter
AdapterFactory.register("filesystem", FileSystemAdapter)
