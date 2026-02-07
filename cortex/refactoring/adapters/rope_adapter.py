"""
RopeAdapter - Python semantic refactoring via Rope library.

AC_START: AC-PHASE24.1.2-002
Description: Rope adapter for Python refactoring operations
Authority: Phase 24 - External Refactoring Tools Integration
Compliance: CORE-011 (type hints), CORE-012 (docstrings), CORE-027 (audit)

Rope Documentation: https://github.com/python-rope/rope
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from cortex.brain.core.result import Ok, Err
from cortex.refactoring.adapters.base import RefactoringToolAdapter
from cortex.refactoring.models import (
    RefactoringLanguage,
    RefactoringRequest,
    RefactoringResult,
)

logger = logging.getLogger(__name__)


class RopeAdapter(RefactoringToolAdapter):
    """Adapter for Python semantic refactoring using Rope library.
    
    Integrates Rope (https://github.com/python-rope/rope) to provide:
        - extract_method: Extract code block into new method
        - rename: Rename variables, functions, classes
        - inline: Inline variable or method
        - encapsulate_field: Create getter/setter for field
        - move_method: Move method to another class
        - change_signature: Modify method signature
    
    Features:
        - Lazy Rope project initialization (performance)
        - Graceful error handling
        - Detailed refactoring results
        - Project caching
    
    Example:
        >>> adapter = RopeAdapter()
        >>> request = RefactoringRequest(
        ...     operation="extract_method",
        ...     file_path=Path("app.py"),
        ...     language=RefactoringLanguage.PYTHON,
        ...     parameters={"start_offset": 100, "end_offset": 200, "new_name": "helper"}
        ... )
        >>> result = adapter.execute_refactoring(request)
        >>> if result.is_ok():
        ...     print(result.unwrap().description)
    """
    
    # Supported operations mapping
    _OPERATIONS = [
        "extract_method",
        "rename",
        "inline",
        "encapsulate_field",
        "move_method",
        "change_signature",
    ]
    
    # Required parameters for each operation
    _REQUIRED_PARAMS = {
        "extract_method": ["start_offset", "end_offset", "new_name"],
        "rename": ["offset", "new_name"],
        "inline": ["offset"],
        "encapsulate_field": ["offset"],
        "move_method": ["offset", "target_class"],
        "change_signature": ["offset", "new_parameters"],
    }
    
    def __init__(self) -> None:
        """Initialize RopeAdapter with lazy project loading."""
        self._project: Optional[Any] = None
        self._rope_available: Optional[bool] = None
        logger.debug("RopeAdapter initialized (lazy loading)")
    
    def get_supported_operations(self) -> List[str]:
        """Return list of supported refactoring operations.
        
        Returns:
            List of operation names
        """
        return self._OPERATIONS.copy()
    
    def get_language(self) -> RefactoringLanguage:
        """Return the programming language this adapter handles.
        
        Returns:
            RefactoringLanguage.PYTHON
        """
        return RefactoringLanguage.PYTHON
    
    def is_available(self) -> bool:
        """Check if Rope library is available.
        
        Returns:
            True if Rope is installed and importable
        """
        if self._rope_available is not None:
            return self._rope_available
        
        try:
            import rope  # noqa: F401
            self._rope_available = True
            logger.debug("Rope library available")
        except ImportError:
            self._rope_available = False
            logger.warning("Rope library not available - install with: pip install rope")
        
        return self._rope_available
    
    def validate_request(self, request: RefactoringRequest) -> Union[Ok[None], Err]:
        """Validate a refactoring request.
        
        Args:
            request: RefactoringRequest to validate
            
        Returns:
            Ok if valid, Err with error message if invalid
        """
        # Check language
        if request.language != RefactoringLanguage.PYTHON:
            return Err(
                f"RopeAdapter only supports Python, got {request.language.value}"
            )
        
        # Check operation supported
        if request.operation not in self._OPERATIONS:
            return Err(
                f"Operation '{request.operation}' not supported. "
                f"Supported: {', '.join(self._OPERATIONS)}"
            )
        
        # Check file exists
        if not request.file_path.exists():
            return Err(f"File not found: {request.file_path}")
        
        # Check required parameters
        if request.operation in self._REQUIRED_PARAMS:
            required = self._REQUIRED_PARAMS[request.operation]
            missing = [p for p in required if p not in request.parameters]
            
            if missing:
                return Err(
                    f"Missing required parameters for '{request.operation}': "
                    f"{', '.join(missing)}"
                )
        
        return Ok(None)
    
    def execute_refactoring(
        self, request: RefactoringRequest
    ) -> Union[Ok[RefactoringResult], Err]:
        """Execute a refactoring operation.
        
        Args:
            request: RefactoringRequest containing operation details
            
        Returns:
            Ok[RefactoringResult] if successful, Err with error message if failed
        """
        # Validate request first
        validation = self.validate_request(request)
        if validation.is_err():
            return validation  # type: ignore
        
        # Check Rope available
        if not self.is_available():
            return Err(
                "Rope library not available. Install with: pip install rope"
            )
        
        # Execute operation based on type
        try:
            if request.operation == "extract_method":
                return self._execute_extract_method(request)
            elif request.operation == "rename":
                return self._execute_rename(request)
            elif request.operation == "inline":
                return self._execute_inline(request)
            elif request.operation == "encapsulate_field":
                return self._execute_encapsulate_field(request)
            elif request.operation == "move_method":
                return self._execute_move_method(request)
            elif request.operation == "change_signature":
                return self._execute_change_signature(request)
            else:
                return Err(f"Operation '{request.operation}' not implemented")
        
        except Exception as e:
            logger.error(f"Refactoring failed: {e}", exc_info=True)
            return Err(f"Refactoring failed: {str(e)}")
    
    def _get_or_create_project(self, file_path: Path) -> Any:
        """Get or create Rope project for file.
        
        Uses lazy initialization and caching for performance.
        
        Args:
            file_path: Path to Python file
            
        Returns:
            Rope Project instance
        """
        from rope.base.project import Project
        
        # Use file's parent directory as project root
        project_root = file_path.parent.resolve()
        
        # Create new project for each file (Rope requirement)
        # Rope projects are lightweight, so this is acceptable
        project = Project(str(project_root))
        logger.debug(f"Created Rope project: {project_root}")
        
        return project
    
    def _execute_extract_method(
        self, request: RefactoringRequest
    ) -> Union[Ok[RefactoringResult], Err]:
        """Execute extract_method refactoring.
        
        Args:
            request: RefactoringRequest with start_offset, end_offset, new_name
            
        Returns:
            RefactoringResult with changes
        """
        try:
            from rope.refactor.extract import ExtractMethod
            
            project = self._get_or_create_project(request.file_path)
            
            # Get resource using relative path from project root
            file_name = request.file_path.name
            resource = project.get_file(file_name)
            
            start_offset = request.parameters["start_offset"]
            end_offset = request.parameters["end_offset"]
            new_name = request.parameters["new_name"]
            
            # Create refactoring
            extractor = ExtractMethod(project, resource, start_offset, end_offset)
            changes = extractor.get_changes(new_name)
            
            # Apply changes
            project.do(changes)
            
            logger.info(
                f"Extracted method '{new_name}' from {request.file_path.name}"
            )
            
            return Ok(
                RefactoringResult(
                    success=True,
                    modified_files=[request.file_path],
                    description=f"Extracted method '{new_name}' from lines at offset {start_offset}-{end_offset}",
                    warnings=[],
                    metadata={
                        "operation": "extract_method",
                        "new_name": new_name,
                        "start_offset": start_offset,
                        "end_offset": end_offset,
                    },
                )
            )
        
        except Exception as e:
            logger.error(f"Extract method failed: {e}")
            return Err(f"Extract method failed: {str(e)}")
    
    def _execute_rename(
        self, request: RefactoringRequest
    ) -> Union[Ok[RefactoringResult], Err]:
        """Execute rename refactoring.
        
        Args:
            request: RefactoringRequest with offset, new_name
            
        Returns:
            RefactoringResult with changes
        """
        try:
            from rope.refactor.rename import Rename
            
            project = self._get_or_create_project(request.file_path)
            
            # Get resource using relative path
            file_name = request.file_path.name
            resource = project.get_file(file_name)
            
            offset = request.parameters["offset"]
            new_name = request.parameters["new_name"]
            
            # Create refactoring
            renamer = Rename(project, resource, offset)
            changes = renamer.get_changes(new_name)
            
            # Apply changes
            project.do(changes)
            
            logger.info(f"Renamed to '{new_name}' in {request.file_path.name}")
            
            return Ok(
                RefactoringResult(
                    success=True,
                    modified_files=[request.file_path],
                    description=f"Renamed symbol to '{new_name}' at offset {offset}",
                    warnings=[],
                    metadata={
                        "operation": "rename",
                        "new_name": new_name,
                        "offset": offset,
                    },
                )
            )
        
        except Exception as e:
            logger.error(f"Rename failed: {e}")
            return Err(f"Rename failed: {str(e)}")
    
    def _execute_inline(
        self, request: RefactoringRequest
    ) -> Union[Ok[RefactoringResult], Err]:
        """Execute inline refactoring.
        
        Args:
            request: RefactoringRequest with offset
            
        Returns:
            RefactoringResult with changes
        """
        try:
            from rope.refactor.inline import create_inline
            
            project = self._get_or_create_project(request.file_path)
            file_name = request.file_path.name
            resource = project.get_file(file_name)
            
            offset = request.parameters["offset"]
            
            # Create refactoring
            inliner = create_inline(project, resource, offset)
            changes = inliner.get_changes()
            
            # Apply changes
            project.do(changes)
            
            logger.info(f"Inlined symbol at offset {offset} in {request.file_path.name}")
            
            return Ok(
                RefactoringResult(
                    success=True,
                    modified_files=[request.file_path],
                    description=f"Inlined symbol at offset {offset}",
                    warnings=[],
                    metadata={
                        "operation": "inline",
                        "offset": offset,
                    },
                )
            )
        
        except Exception as e:
            logger.error(f"Inline failed: {e}")
            return Err(f"Inline failed: {str(e)}")
    
    def _execute_encapsulate_field(
        self, request: RefactoringRequest
    ) -> Union[Ok[RefactoringResult], Err]:
        """Execute encapsulate_field refactoring.
        
        Args:
            request: RefactoringRequest with offset
            
        Returns:
            RefactoringResult with changes
        """
        try:
            from rope.refactor.encapsulate_field import EncapsulateField
            
            project = self._get_or_create_project(request.file_path)
            file_name = request.file_path.name
            resource = project.get_file(file_name)
            
            offset = request.parameters["offset"]
            
            # Create refactoring
            encapsulator = EncapsulateField(project, resource, offset)
            changes = encapsulator.get_changes()
            
            # Apply changes
            project.do(changes)
            
            logger.info(
                f"Encapsulated field at offset {offset} in {request.file_path.name}"
            )
            
            return Ok(
                RefactoringResult(
                    success=True,
                    modified_files=[request.file_path],
                    description=f"Encapsulated field at offset {offset}",
                    warnings=[],
                    metadata={
                        "operation": "encapsulate_field",
                        "offset": offset,
                    },
                )
            )
        
        except Exception as e:
            logger.error(f"Encapsulate field failed: {e}")
            return Err(f"Encapsulate field failed: {str(e)}")
    
    def _execute_move_method(
        self, request: RefactoringRequest
    ) -> Union[Ok[RefactoringResult], Err]:
        """Execute move_method refactoring.
        
        Args:
            request: RefactoringRequest with offset, target_class
            
        Returns:
            RefactoringResult with changes
        """
        try:
            from rope.refactor.move import MoveMethod
            
            project = self._get_or_create_project(request.file_path)
            file_name = request.file_path.name
            resource = project.get_file(file_name)
            
            offset = request.parameters["offset"]
            target_class = request.parameters["target_class"]
            
            # Create refactoring
            mover = MoveMethod(project, resource, offset)
            changes = mover.get_changes(target_class)
            
            # Apply changes
            project.do(changes)
            
            logger.info(
                f"Moved method to '{target_class}' in {request.file_path.name}"
            )
            
            return Ok(
                RefactoringResult(
                    success=True,
                    modified_files=[request.file_path],
                    description=f"Moved method to class '{target_class}'",
                    warnings=[],
                    metadata={
                        "operation": "move_method",
                        "offset": offset,
                        "target_class": target_class,
                    },
                )
            )
        
        except Exception as e:
            logger.error(f"Move method failed: {e}")
            return Err(f"Move method failed: {str(e)}")
    
    def _execute_change_signature(
        self, request: RefactoringRequest
    ) -> Union[Ok[RefactoringResult], Err]:
        """Execute change_signature refactoring.
        
        Args:
            request: RefactoringRequest with offset, new_parameters
            
        Returns:
            RefactoringResult with changes
        """
        try:
            from rope.refactor.change_signature import ChangeSignature
            
            project = self._get_or_create_project(request.file_path)
            file_name = request.file_path.name
            resource = project.get_file(file_name)
            
            offset = request.parameters["offset"]
            new_parameters = request.parameters["new_parameters"]
            
            # Create refactoring
            changer = ChangeSignature(project, resource, offset)
            changes = changer.get_changes(new_parameters)
            
            # Apply changes
            project.do(changes)
            
            logger.info(
                f"Changed signature at offset {offset} in {request.file_path.name}"
            )
            
            return Ok(
                RefactoringResult(
                    success=True,
                    modified_files=[request.file_path],
                    description=f"Changed method signature at offset {offset}",
                    warnings=[],
                    metadata={
                        "operation": "change_signature",
                        "offset": offset,
                        "new_parameters": new_parameters,
                    },
                )
            )
        
        except Exception as e:
            logger.error(f"Change signature failed: {e}")
            return Err(f"Change signature failed: {str(e)}")
    
    def __del__(self) -> None:
        """Cleanup Rope project on deletion."""
        if self._project is not None:
            try:
                self._project.close()
                logger.debug("Closed Rope project")
            except Exception as e:
                logger.warning(f"Error closing Rope project: {e}")


# AC_COMPLETE: AC-PHASE24.1.2-002 ✅
