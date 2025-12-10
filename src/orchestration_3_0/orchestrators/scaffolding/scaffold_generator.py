"""
Scaffold Generator Component
Auto-generates modern folder structure and boilerplate code.

Features:
- Clean Architecture folder structure generation
- Boilerplate code templates (entities, repositories, use cases, controllers)
- Configuration file generation (pyproject.toml, pytest.ini, Dockerfile)
- Documentation templates (README, API docs, architecture diagrams)
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ScaffoldGenerator:
    """
    Generates modern project scaffolding from architecture assessment.
    
    Creates:
    - Folder structure (domain/, application/, infrastructure/, presentation/)
    - Boilerplate code (base classes, interfaces)
    - Configuration files (pyproject.toml, pytest.ini, .env.example, Dockerfile)
    - Documentation (README.md, API docs, architecture diagrams)
    
    Example:
        generator = ScaffoldGenerator(output_path=Path("./my_new_project"))
        generator.generate(architecture_assessment)
    """
    
    def __init__(self, output_path: Path):
        """
        Initialize scaffold generator.
        
        Args:
            output_path: Root path for generated scaffold
        """
        self.output_path = output_path
        self.language = None
        self.framework = None
    
    def generate(self, architecture_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate complete scaffold.
        
        Args:
            architecture_assessment: Architecture assessment from ArchitectureIntelligence
        
        Returns:
            Dictionary with generation results
        """
        # Extract assessment details
        recommended_pattern = architecture_assessment.get('recommended_pattern', 'clean_architecture')
        tech_stack = architecture_assessment.get('tech_stack', {})
        service_candidates = architecture_assessment.get('service_candidates', [])
        
        self.framework = tech_stack.get('framework', 'FastAPI')
        self.language = self._detect_language(tech_stack)
        
        logger.info(f"Generating {recommended_pattern} scaffold at {self.output_path}")
        
        # Create folder structure
        self._create_folder_structure(recommended_pattern)
        
        # Generate boilerplate code
        files_created = []
        files_created.extend(self._generate_domain_layer(service_candidates))
        files_created.extend(self._generate_application_layer(service_candidates))
        files_created.extend(self._generate_infrastructure_layer(tech_stack))
        files_created.extend(self._generate_presentation_layer(service_candidates, tech_stack))
        files_created.extend(self._generate_tests_structure())
        
        # Generate configuration files
        files_created.extend(self._generate_config_files(tech_stack))
        
        # Generate documentation
        files_created.extend(self._generate_documentation(architecture_assessment))
        
        result = {
            'scaffold_path': str(self.output_path),
            'files_created': len(files_created),
            'files': files_created,
            'language': self.language,
            'framework': self.framework,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Scaffold generation complete: {len(files_created)} files created")
        return result
    
    def _detect_language(self, tech_stack: Dict[str, str]) -> str:
        """Detect target language from tech stack."""
        framework = tech_stack.get('framework', '').lower()
        
        if 'fastapi' in framework or 'flask' in framework or 'django' in framework:
            return 'python'
        elif 'nestjs' in framework or 'express' in framework:
            return 'typescript'
        elif '.net' in framework:
            return 'csharp'
        
        return 'python'  # Default
    
    def _create_folder_structure(self, pattern: str):
        """Create Clean Architecture folder structure."""
        folders = [
            'domain/entities',
            'domain/repositories',
            'domain/value_objects',
            'application/use_cases',
            'application/dtos',
            'infrastructure/persistence',
            'infrastructure/config',
            'presentation/api',
            'presentation/schemas',
            'tests/unit',
            'tests/integration',
            'tests/e2e',
        ]
        
        for folder in folders:
            folder_path = self.output_path / folder
            folder_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Created {len(folders)} directories")
    
    def _generate_domain_layer(self, service_candidates: List[Dict[str, Any]]) -> List[str]:
        """Generate domain layer files (entities, repositories)."""
        files = []
        
        # Base entity
        entity_template = self._get_base_entity_template()
        entity_file = self.output_path / 'domain' / 'entities' / f'base_entity.{self._file_extension()}'
        entity_file.write_text(entity_template)
        files.append(str(entity_file))
        
        # Repository interface
        repo_template = self._get_base_repository_template()
        repo_file = self.output_path / 'domain' / 'repositories' / f'base_repository.{self._file_extension()}'
        repo_file.write_text(repo_template)
        files.append(str(repo_file))
        
        # Generate entity per service candidate
        for service in service_candidates[:3]:  # Top 3 services
            service_name = service.get('name', 'Service').replace('Service', '')
            
            entity_template = self._get_entity_template(service_name)
            entity_file = self.output_path / 'domain' / 'entities' / f'{service_name.lower()}.{self._file_extension()}'
            entity_file.write_text(entity_template)
            files.append(str(entity_file))
            
            repo_interface = self._get_repository_interface_template(service_name)
            repo_file = self.output_path / 'domain' / 'repositories' / f'{service_name.lower()}_repository.{self._file_extension()}'
            repo_file.write_text(repo_interface)
            files.append(str(repo_file))
        
        return files
    
    def _generate_application_layer(self, service_candidates: List[Dict[str, Any]]) -> List[str]:
        """Generate application layer files (use cases, DTOs)."""
        files = []
        
        # Base use case
        usecase_template = self._get_base_usecase_template()
        usecase_file = self.output_path / 'application' / 'use_cases' / f'base_use_case.{self._file_extension()}'
        usecase_file.write_text(usecase_template)
        files.append(str(usecase_file))
        
        # Generate use case per service candidate
        for service in service_candidates[:3]:
            service_name = service.get('name', 'Service').replace('Service', '')
            
            usecase_template = self._get_usecase_template(service_name)
            usecase_file = self.output_path / 'application' / 'use_cases' / f'process_{service_name.lower()}.{self._file_extension()}'
            usecase_file.write_text(usecase_template)
            files.append(str(usecase_file))
        
        return files
    
    def _generate_infrastructure_layer(self, tech_stack: Dict[str, str]) -> List[str]:
        """Generate infrastructure layer files (persistence, config)."""
        files = []
        
        # Config/settings file
        config_template = self._get_config_template(tech_stack)
        config_file = self.output_path / 'infrastructure' / 'config' / f'settings.{self._file_extension()}'
        config_file.write_text(config_template)
        files.append(str(config_file))
        
        # Database connection (if ORM specified)
        if tech_stack.get('orm'):
            db_template = self._get_database_template(tech_stack)
            db_file = self.output_path / 'infrastructure' / 'persistence' / f'database.{self._file_extension()}'
            db_file.write_text(db_template)
            files.append(str(db_file))
        
        return files
    
    def _generate_presentation_layer(self, service_candidates: List[Dict[str, Any]], tech_stack: Dict[str, str]) -> List[str]:
        """Generate presentation layer files (API controllers, schemas)."""
        files = []
        
        # Main app entry point
        app_template = self._get_app_template(tech_stack)
        app_file = self.output_path / 'presentation' / f'main.{self._file_extension()}'
        app_file.write_text(app_template)
        files.append(str(app_file))
        
        # API controller per service candidate
        for service in service_candidates[:3]:
            service_name = service.get('name', 'Service').replace('Service', '')
            
            controller_template = self._get_controller_template(service_name, tech_stack)
            controller_file = self.output_path / 'presentation' / 'api' / f'{service_name.lower()}_controller.{self._file_extension()}'
            controller_file.write_text(controller_template)
            files.append(str(controller_file))
        
        return files
    
    def _generate_tests_structure(self) -> List[str]:
        """Generate test structure with sample tests."""
        files = []
        
        # Conftest (pytest) or test setup
        if self.language == 'python':
            conftest = self.output_path / 'tests' / 'conftest.py'
            conftest.write_text("# Pytest configuration and fixtures\nimport pytest\n")
            files.append(str(conftest))
        
        return files
    
    def _generate_config_files(self, tech_stack: Dict[str, str]) -> List[str]:
        """Generate configuration files (pyproject.toml, pytest.ini, Dockerfile)."""
        files = []
        
        if self.language == 'python':
            # pyproject.toml
            pyproject = self.output_path / 'pyproject.toml'
            pyproject.write_text(self._get_pyproject_template(tech_stack))
            files.append(str(pyproject))
            
            # pytest.ini
            pytest_ini = self.output_path / 'pytest.ini'
            pytest_ini.write_text("[pytest]\ntestpaths = tests\npython_files = test_*.py\n")
            files.append(str(pytest_ini))
            
            # .env.example
            env_example = self.output_path / '.env.example'
            env_example.write_text("DATABASE_URL=postgresql://user:pass@localhost/db\nAPI_KEY=your_api_key_here\n")
            files.append(str(env_example))
            
            # Dockerfile
            dockerfile = self.output_path / 'Dockerfile'
            dockerfile.write_text(self._get_dockerfile_template())
            files.append(str(dockerfile))
        
        return files
    
    def _generate_documentation(self, architecture_assessment: Dict[str, Any]) -> List[str]:
        """Generate documentation files."""
        files = []
        
        # README.md
        readme = self.output_path / 'README.md'
        readme.write_text(self._get_readme_template(architecture_assessment))
        files.append(str(readme))
        
        return files
    
    # Template methods (simplified - in production, use Jinja2 or similar)
    
    def _file_extension(self) -> str:
        """Get file extension for target language."""
        return {'python': 'py', 'typescript': 'ts', 'csharp': 'cs'}.get(self.language, 'py')
    
    def _get_base_entity_template(self) -> str:
        if self.language == 'python':
            return '''"""Base entity for domain layer."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class BaseEntity:
    """Base class for all domain entities."""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
'''
        return "// Base entity template"
    
    def _get_base_repository_template(self) -> str:
        if self.language == 'python':
            return '''"""Base repository interface."""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """Base repository interface for data access."""
    
    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[T]:
        """Retrieve entity by ID."""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[T]:
        """Retrieve all entities."""
        pass
    
    @abstractmethod
    async def save(self, entity: T) -> T:
        """Save entity."""
        pass
    
    @abstractmethod
    async def delete(self, id: int) -> bool:
        """Delete entity by ID."""
        pass
'''
        return "// Base repository template"
    
    def _get_entity_template(self, service_name: str) -> str:
        if self.language == 'python':
            return f'''"""{ service_name} entity."""
from dataclasses import dataclass
from .base_entity import BaseEntity

@dataclass
class {service_name}(BaseEntity):
    """{ service_name} domain entity."""
    # TODO: Add entity properties
    name: str = ""
'''
        return f"// {service_name} entity template"
    
    def _get_repository_interface_template(self, service_name: str) -> str:
        if self.language == 'python':
            return f'''"""{ service_name} repository interface."""
from abc import ABC
from .base_repository import BaseRepository
from domain.entities.{service_name.lower()} import {service_name}

class {service_name}Repository(BaseRepository[{service_name}], ABC):
    """{ service_name} repository interface."""
    # TODO: Add custom repository methods
    pass
'''
        return f"// {service_name} repository template"
    
    def _get_base_usecase_template(self) -> str:
        if self.language == 'python':
            return '''"""Base use case for application layer."""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

TRequest = TypeVar('TRequest')
TResponse = TypeVar('TResponse')

class BaseUseCase(ABC, Generic[TRequest, TResponse]):
    """Base use case interface."""
    
    @abstractmethod
    async def execute(self, request: TRequest) -> TResponse:
        """Execute use case."""
        pass
'''
        return "// Base use case template"
    
    def _get_usecase_template(self, service_name: str) -> str:
        if self.language == 'python':
            return f'''"""Process { service_name} use case."""
from dataclasses import dataclass
from application.use_cases.base_use_case import BaseUseCase

@dataclass
class Process{service_name}Request:
    """Request DTO for process {service_name} use case."""
    # TODO: Add request properties
    pass

@dataclass
class Process{service_name}Response:
    """Response DTO for process {service_name} use case."""
    # TODO: Add response properties
    success: bool = False

class Process{service_name}(BaseUseCase[Process{service_name}Request, Process{service_name}Response]):
    """Process { service_name} use case."""
    
    async def execute(self, request: Process{service_name}Request) -> Process{service_name}Response:
        # TODO: Implement business logic
        return Process{service_name}Response(success=True)
'''
        return f"// {service_name} use case template"
    
    def _get_config_template(self, tech_stack: Dict[str, str]) -> str:
        if self.language == 'python':
            return '''"""Application settings."""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application configuration."""
    database_url: str = "postgresql://user:pass@localhost/db"
    api_key: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
'''
        return "// Config template"
    
    def _get_database_template(self, tech_stack: Dict[str, str]) -> str:
        if self.language == 'python' and tech_stack.get('orm') == 'SQLAlchemy':
            return '''"""Database connection."""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from infrastructure.config.settings import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
'''
        return "// Database template"
    
    def _get_app_template(self, tech_stack: Dict[str, str]) -> str:
        if self.language == 'python' and 'fastapi' in tech_stack.get('framework', '').lower():
            return '''"""FastAPI application entry point."""
from fastapi import FastAPI

app = FastAPI(title="Modern Application", version="1.0.0")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        return "// App template"
    
    def _get_controller_template(self, service_name: str, tech_stack: Dict[str, str]) -> str:
        if self.language == 'python' and 'fastapi' in tech_stack.get('framework', '').lower():
            return f'''"""{ service_name} API controller."""
from fastapi import APIRouter, HTTPException
from application.use_cases.process_{service_name.lower()} import Process{service_name}, Process{service_name}Request

router = APIRouter(prefix="/{service_name.lower()}", tags=["{service_name}"])

@router.post("/")
async def process_{service_name.lower()}(request: Process{service_name}Request):
    """Process { service_name} endpoint."""
    use_case = Process{service_name}()
    response = await use_case.execute(request)
    return response
'''
        return f"// {service_name} controller template"
    
    def _get_pyproject_template(self, tech_stack: Dict[str, str]) -> str:
        framework = tech_stack.get('framework', 'FastAPI')
        return f'''[tool.poetry]
name = "modern-application"
version = "1.0.0"
description = "Modernized application using {framework}"
authors = ["Your Name <you@example.com>"]

[tool.poetry.dependencies]
python = "^3.10"
{framework.lower()} = "^0.100.0"
sqlalchemy = "^2.0.0"
pytest = "^7.0.0"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
'''
    
    def _get_dockerfile_template(self) -> str:
        return '''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "presentation.main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
    
    def _get_readme_template(self, architecture_assessment: Dict[str, Any]) -> str:
        pattern = architecture_assessment.get('recommended_pattern', 'Clean Architecture')
        tech_stack = architecture_assessment.get('tech_stack', {})
        
        return f'''# Modern Application

## Architecture: {pattern}

## Tech Stack
{chr(10).join(f"- **{k.capitalize()}:** {v}" for k, v in tech_stack.items())}

## Getting Started

### Installation
```bash
pip install -r requirements.txt
```

### Running
```bash
python presentation/main.py
```

### Testing
```bash
pytest
```

## Project Structure
```
domain/         - Domain entities and repository interfaces
application/    - Use cases and business logic
infrastructure/ - External dependencies (database, config)
presentation/   - API controllers and schemas
tests/          - Unit, integration, and e2e tests
```

## Generated by CORTEX Scaffolding Orchestrator
'''
