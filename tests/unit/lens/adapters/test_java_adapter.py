"""
Unit tests for JavaAdapter (Phase 3).

Tests Java AST parsing using tree-sitter.
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from cortex.lens.adapters.java_adapter import JavaAdapter
from cortex.lens.models.polyglot_ast_result import PolyglotASTResult


@pytest.fixture
def temp_java_file():
    """Create temporary Java file for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def simple_java_class(temp_java_file):
    """Fixture for simple Java class."""
    java_file = temp_java_file / "User.java"
    java_file.write_text("""package com.example.model;

import java.util.List;
import java.util.ArrayList;

public class User {
    private String name;
    private int age;
    
    public User(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public void printInfo() {
        System.out.println(name + " is " + age + " years old");
    }
}
""")
    return java_file


@pytest.fixture
def java_interface(temp_java_file):
    """Fixture for Java interface."""
    java_file = temp_java_file / "UserService.java"
    java_file.write_text("""package com.example.service;

import com.example.model.User;
import java.util.List;

public interface UserService {
    User findById(long id);
    List<User> findAll();
    void save(User user);
    void delete(long id);
}
""")
    return java_file


@pytest.fixture
def java_annotation_class(temp_java_file):
    """Fixture for Java class with annotations."""
    java_file = temp_java_file / "UserController.java"
    java_file.write_text("""package com.example.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
@RequestMapping("/users")
public class UserController {
    
    @GetMapping("/list")
    public String listUsers() {
        return "users";
    }
}
""")
    return java_file


class TestJavaAdapter:
    """Test JavaAdapter parsing capabilities."""
    
    def test_adapter_creation(self):
        """Test that JavaAdapter can be instantiated."""
        adapter = JavaAdapter()
        assert adapter is not None
        assert adapter.get_supported_extensions() == [".java"]
        assert adapter.get_language_name() == "java"
    
    def test_parse_simple_class(self, simple_java_class):
        """Test parsing a simple Java class."""
        adapter = JavaAdapter()
        result = adapter.parse_file(simple_java_class)
        
        assert isinstance(result, PolyglotASTResult)
        assert result.language.value == "java"
        assert len(result.classes) == 1
        
        user_class = result.classes[0]
        assert user_class.name == "User"
        assert user_class.base_classes == []
    
    def test_parse_methods(self, simple_java_class):
        """Test method extraction from Java class."""
        adapter = JavaAdapter()
        result = adapter.parse_file(simple_java_class)
        
        user_class = result.classes[0]
        assert len(user_class.methods) >= 4  # Constructor + getter + setter + printInfo
        
        method_names = [m.name for m in user_class.methods]
        assert "getName" in method_names
        assert "setName" in method_names
        assert "printInfo" in method_names
    
    def test_parse_fields(self, simple_java_class):
        """Test field extraction from Java class."""
        adapter = JavaAdapter()
        result = adapter.parse_file(simple_java_class)
        
        user_class = result.classes[0]
        assert len(user_class.properties) == 2
        
        field_names = [p["name"] for p in user_class.properties]
        assert "name" in field_names
        assert "age" in field_names
    
    def test_parse_imports(self, simple_java_class):
        """Test import statement extraction."""
        adapter = JavaAdapter()
        result = adapter.parse_file(simple_java_class)
        
        assert len(result.imports) >= 2
        import_modules = [imp.module for imp in result.imports]
        assert "java.util.List" in import_modules
        assert "java.util.ArrayList" in import_modules
    
    def test_parse_interface(self, java_interface):
        """Test Java interface parsing."""
        adapter = JavaAdapter()
        result = adapter.parse_file(java_interface)
        
        assert len(result.classes) == 1
        interface = result.classes[0]
        assert interface.name == "UserService"
        assert len(interface.methods) == 4
        
        method_names = [m.name for m in interface.methods]
        assert "findById" in method_names
        assert "findAll" in method_names
        assert "save" in method_names
        assert "delete" in method_names
    
    def test_parse_annotations(self, java_annotation_class):
        """Test annotation extraction from Java class."""
        adapter = JavaAdapter()
        result = adapter.parse_file(java_annotation_class)
        
        assert len(result.classes) == 1
        controller_class = result.classes[0]
        assert controller_class.name == "UserController"
        
        # Verify methods with annotations are extracted
        method_names = [m.name for m in controller_class.methods]
        assert "listUsers" in method_names
    
    def test_error_handling_invalid_file(self, temp_java_file):
        """Test error handling for non-existent file."""
        adapter = JavaAdapter()
        non_existent = temp_java_file / "DoesNotExist.java"
        
        result = adapter.parse_file(non_existent)
        assert result.language.value == "java"
        assert len(result.classes) == 0
        assert len(result.parse_errors) > 0
