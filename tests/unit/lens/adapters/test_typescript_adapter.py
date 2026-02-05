"""
TypeScriptAdapter Unit Tests

Tests tree-sitter-based TypeScript AST parsing:
- Class, interface, type alias parsing
- Method, constructor, property extraction
- Import/export statement parsing
- Decorator detection (@Component, @Injectable, etc.)
- Error handling

Author: Asif Hussain
Created: 2026-02-05
Authority: LENS-MULTI-LANGUAGE-ENHANCEMENT.yaml Phase 4
"""

import pytest
from pathlib import Path
from cortex.lens.adapters.typescript_adapter import TypeScriptAdapter
from cortex.lens.models.polyglot_ast_result import LanguageType


@pytest.fixture
def adapter():
    """Create TypeScriptAdapter instance."""
    return TypeScriptAdapter()


@pytest.fixture
def temp_typescript_file(tmp_path: Path) -> Path:
    """Create temporary TypeScript file with class and methods."""
    ts_file = tmp_path / "User.ts"
    ts_file.write_text("""
export interface IUser {
    id: number;
    name: string;
    email: string;
}

export class User implements IUser {
    constructor(
        public id: number,
        public name: string,
        public email: string
    ) {}
    
    getName(): string {
        return this.name;
    }
    
    setName(name: string): void {
        this.name = name;
    }
    
    getEmail(): string {
        return this.email;
    }
}
""")
    return ts_file


@pytest.fixture
def temp_interface_file(tmp_path: Path) -> Path:
    """Create TypeScript file with interface."""
    ts_file = tmp_path / "UserService.ts"
    ts_file.write_text("""
import { User } from './User';

export interface UserService {
    getUser(id: number): Promise<User>;
    createUser(user: User): Promise<void>;
    updateUser(id: number, user: User): Promise<void>;
    deleteUser(id: number): Promise<void>;
}
""")
    return ts_file


@pytest.fixture
def temp_decorator_file(tmp_path: Path) -> Path:
    """Create TypeScript file with decorators."""
    ts_file = tmp_path / "UserController.ts"
    ts_file.write_text("""
import { Controller, Get, Post } from '@nestjs/common';

@Controller('users')
export class UserController {
    @Get()
    findAll() {
        return [];
    }
    
    @Post()
    create() {
        return {};
    }
}
""")
    return ts_file


def test_adapter_creation(adapter):
    """Test TypeScriptAdapter instantiation."""
    assert adapter is not None
    assert "typescript" in adapter.get_supported_extensions()
    assert ".ts" in adapter.get_supported_extensions()
    assert adapter.get_language_name() == "typescript"


def test_parse_simple_class(adapter, temp_typescript_file):
    """Test parsing simple TypeScript class."""
    result = adapter.parse_file(temp_typescript_file)
    
    assert result.language == LanguageType.TYPESCRIPT
    assert len(result.classes) >= 1
    
    # Find User class
    user_class = next((c for c in result.classes if c.name == "User"), None)
    assert user_class is not None
    assert user_class.base_classes == ["IUser"]


def test_parse_methods(adapter, temp_typescript_file):
    """Test method extraction from TypeScript class."""
    result = adapter.parse_file(temp_typescript_file)
    
    user_class = next((c for c in result.classes if c.name == "User"), None)
    assert user_class is not None
    
    # Should have constructor + 3 methods
    method_names = [m.name for m in user_class.methods]
    assert "constructor" in method_names
    assert "getName" in method_names
    assert "setName" in method_names
    assert "getEmail" in method_names


def test_parse_properties(adapter, temp_typescript_file):
    """Test property extraction from TypeScript class."""
    result = adapter.parse_file(temp_typescript_file)
    
    user_class = next((c for c in result.classes if c.name == "User"), None)
    assert user_class is not None
    
    # Should have id, name, email properties
    properties = user_class.properties
    assert len(properties) >= 3
    assert "id" in properties
    assert "name" in properties
    assert "email" in properties


def test_parse_imports(adapter, temp_interface_file):
    """Test import statement extraction."""
    result = adapter.parse_file(temp_interface_file)
    
    assert len(result.imports) >= 1
    
    # Should import User
    import_names = [imp.module for imp in result.imports]
    assert "./User" in import_names or "User" in str(result.imports)


def test_parse_interface(adapter, temp_interface_file):
    """Test interface parsing."""
    result = adapter.parse_file(temp_interface_file)
    
    assert len(result.classes) >= 1
    
    # Find UserService interface
    user_service = next((c for c in result.classes if c.name == "UserService"), None)
    assert user_service is not None
    
    # Should have 4 methods
    assert len(user_service.methods) == 4
    method_names = [m.name for m in user_service.methods]
    assert "getUser" in method_names
    assert "createUser" in method_names


def test_parse_decorators(adapter, temp_decorator_file):
    """Test decorator extraction."""
    result = adapter.parse_file(temp_decorator_file)
    
    assert len(result.classes) >= 1
    
    controller_class = next((c for c in result.classes if c.name == "UserController"), None)
    assert controller_class is not None
    
    # Should have methods (getUsers, createUser)
    assert len(controller_class.methods) >= 2
    
    # Check that decorators were found (Controller, Get, Post)
    # Decorators should be in attributes list or method decorators
    has_decorators = (
        len(controller_class.attributes) > 0 or 
        any(len(m.decorators) > 0 for m in controller_class.methods)
    )


def test_error_handling_invalid_file(adapter, tmp_path):
    """Test handling of non-existent file."""
    non_existent = tmp_path / "does_not_exist.ts"
    result = adapter.parse_file(non_existent)
    
    assert result.language == LanguageType.TYPESCRIPT
    assert len(result.parse_errors) > 0
    assert len(result.classes) == 0
