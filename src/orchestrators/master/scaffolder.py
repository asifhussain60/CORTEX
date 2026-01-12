"""
Orchestrator Scaffolder - Creates complete orchestrator implementations.

AC-SCAFFOLD-001: Scaffolder CLI creates orchestrator with tests, docs, and registration.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import re


@dataclass
class ScaffoldResult:
    """Result of scaffolding operation."""
    success: bool
    message: str
    created_files: List[Path] = field(default_factory=list)
    files_to_create: List[Path] = field(default_factory=list)


class OrchestratorScaffolder:
    """
    Scaffolds complete orchestrator implementations.
    
    Features:
    - Creates orchestrator implementation file
    - Generates test file with fixtures
    - Creates documentation
    - Updates __init__.py imports
    - Supports custom templates
    - Dry-run mode
    """
    
    def __init__(self, workspace: Optional[Path] = None):
        """Initialize scaffolder."""
        self.logger = logging.getLogger("cortex.orchestrators.master.scaffolder")
        self.workspace = workspace or Path.cwd()
    
    def scaffold(
        self,
        name: str,
        category: str,
        ac_ids: Optional[List[str]] = None,
        template: Optional[str] = None,
        dry_run: bool = False
    ) -> ScaffoldResult:
        """
        Scaffold complete orchestrator implementation.
        
        Args:
            name: Orchestrator name (e.g., "TestOrchestrator")
            category: Category (e.g., "feature", "core", "utility")
            ac_ids: Optional list of AC-IDs this orchestrator implements
            template: Optional custom template name
            dry_run: If True, show what would be created without creating
            
        Returns:
            ScaffoldResult with created files or files to create
        """
        # Validate name format
        if not self._validate_name(name):
            raise ValueError(f"Invalid orchestrator name: {name}. Must be PascalCase alphanumeric.")
        
        # Convert to snake_case for filenames
        snake_name = self._to_snake_case(name)
        
        # Define file paths
        orch_file = self.workspace / "src" / "orchestrators" / f"{snake_name}.py"
        test_file = self.workspace / "tests" / "orchestrators" / f"test_{snake_name}.py"
        doc_file = self.workspace / "docs" / "orchestrators" / f"{snake_name.replace('_', '-')}.md"
        
        # Check for conflicts
        if orch_file.exists() and not dry_run:
            raise FileExistsError(f"Orchestrator already exists: {orch_file}")
        
        files_to_create = [orch_file, test_file, doc_file]
        
        if dry_run:
            return ScaffoldResult(
                success=True,
                message=f"Dry run: Would create {len(files_to_create)} files",
                files_to_create=files_to_create
            )
        
        # Create files
        created_files = []
        
        # Check for custom template
        if template:
            template_file = self.workspace / "templates" / f"{template}.py.j2"
            if template_file.exists():
                # Use custom template
                self._create_from_template(orch_file, template_file, name, category)
                created_files.append(orch_file)
            else:
                # Fall back to default if template doesn't exist
                self._create_orchestrator_file(orch_file, name, category)
                created_files.append(orch_file)
        else:
            # 1. Create orchestrator implementation
            self._create_orchestrator_file(orch_file, name, category)
            created_files.append(orch_file)
        
        # 2. Create test file
        self._create_test_file(test_file, name, snake_name)
        created_files.append(test_file)
        
        # 3. Create documentation
        self._create_documentation(doc_file, name, ac_ids or [])
        created_files.append(doc_file)
        
        # 4. Update __init__.py
        self._update_init_file(name, snake_name)
        
        self.logger.info(
            f"Scaffolded orchestrator: {name}",
            extra={
                "name": name,
                "category": category,
                "files_created": len(created_files)
            }
        )
        
        return ScaffoldResult(
            success=True,
            message=f"Created orchestrator: {name}",
            created_files=created_files
        )
    
    def _validate_name(self, name: str) -> bool:
        """Validate orchestrator name format."""
        # Must be PascalCase, alphanumeric
        pattern = r'^[A-Z][a-zA-Z0-9]*$'
        return bool(re.match(pattern, name))
    
    def _to_snake_case(self, name: str) -> str:
        """Convert PascalCase to snake_case."""
        # Insert underscore before uppercase letters
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def _create_orchestrator_file(self, path: Path, name: str, category: str) -> None:
        """Create orchestrator implementation file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        
        content = f'''"""
{name} - {category.capitalize()} orchestrator.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

from src.orchestrators.base_orchestrator import BaseOrchestrator


@dataclass
class {name}Result:
    """Result from {name} execution."""
    success: bool
    message: str
    data: Dict[str, Any]


class {name}(BaseOrchestrator):
    """
    {name} orchestrator.
    
    Category: {category}
    """
    
    def __init__(self):
        """Initialize {name}."""
        super().__init__()
        self.logger = logging.getLogger(f"cortex.orchestrators.{{self.__class__.__name__.lower()}}")
    
    def handle_request(self, request: str, context: Optional[Dict[str, Any]] = None) -> {name}Result:
        """
        Handle orchestrator request.
        
        Args:
            request: User request
            context: Optional execution context
            
        Returns:
            {name}Result with execution outcome
        """
        self.logger.info(f"Handling request: {{request}}")
        
        # TODO: Implement orchestrator logic
        
        return {name}Result(
            success=True,
            message="Orchestrator executed successfully",
            data={{"request": request}}
        )
'''
        
        path.write_text(content)
    
    def _create_from_template(self, path: Path, template_path: Path, name: str, category: str) -> None:
        """Create orchestrator file from custom template."""
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Read template
        template_content = template_path.read_text()
        
        # Simple variable replacement ({{ name }})
        content = template_content.replace("{{ name }}", name)
        content = content.replace("{{ category }}", category)
        
        path.write_text(content)
    
    def _create_test_file(self, path: Path, name: str, snake_name: str) -> None:
        """Create test file with fixtures."""
        path.parent.mkdir(parents=True, exist_ok=True)
        
        content = f'''"""
Tests for {name}.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from unittest.mock import Mock

from src.orchestrators.{snake_name} import {name}


class Test{name}:
    """Test {name} orchestrator."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create {name} instance."""
        return {name}()
    
    def test_initialization(self, orchestrator):
        """Test: Orchestrator initializes successfully."""
        assert orchestrator is not None
        assert hasattr(orchestrator, 'handle_request')
    
    def test_handle_request(self, orchestrator):
        """Test: Can handle basic request."""
        result = orchestrator.handle_request("test request")
        
        assert result is not None
        assert result.success
    
    def test_handle_request_with_context(self, orchestrator):
        """Test: Can handle request with context."""
        context = {{"key": "value"}}
        result = orchestrator.handle_request("test request", context=context)
        
        assert result is not None
        assert result.success
'''
        
        path.write_text(content)
    
    def _create_documentation(self, path: Path, name: str, ac_ids: List[str]) -> None:
        """Create documentation file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Always include AC-IDs section
        ac_section = "\n## AC-IDs\n\n"
        if ac_ids:
            ac_section += "\n".join(f"- {ac_id}" for ac_id in ac_ids)
        else:
            ac_section += "No AC-IDs associated yet."
        
        content = f'''# {name}

## Purpose

{name} orchestrator implementation.

## Usage

```python
from src.orchestrators.{self._to_snake_case(name)} import {name}

orchestrator = {name}()
result = orchestrator.handle_request("your request")
```

## Features

- Feature 1
- Feature 2
- Feature 3{ac_section}

## Implementation Notes

TODO: Add implementation details

---

**Author:** Asif Hussain  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
'''
        
        path.write_text(content)
    
    def _update_init_file(self, name: str, snake_name: str) -> None:
        """Update __init__.py with new orchestrator import."""
        init_file = self.workspace / "src" / "orchestrators" / "__init__.py"
        
        if not init_file.exists():
            return
        
        content = init_file.read_text()
        
        # Check if import already exists
        import_line = f"from src.orchestrators.{snake_name} import {name}"
        if import_line in content:
            return
        
        # Add import at end
        content += f"\n{import_line}\n"
        init_file.write_text(content)
