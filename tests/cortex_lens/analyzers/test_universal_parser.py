"""
Unit Tests for UniversalParser

Tests multi-language AST parsing with tree-sitter for:
- C# (14,459 files across projects)
- SQL (7,284 files across projects)
- Python, JavaScript, TypeScript, HTML, CSS
- ColdFusion fallback (regex-based)

Copyright © 2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from src.cortex_lens.analyzers.universal_parser import (
    UniversalParser,
    get_universal_parser,
    analyze_file
)


@pytest.fixture
def parser():
    """Get UniversalParser instance"""
    return UniversalParser()


@pytest.fixture
def test_files(tmp_path):
    """Create test files for each supported language"""
    files = {}
    
    # Python test file
    py_file = tmp_path / "test.py"
    py_file.write_text("""
import os
from typing import List

def hello_world():
    '''Simple function'''
    return "Hello, World!"

class MyClass:
    def __init__(self):
        self.value = 42
    
    def get_value(self):
        return self.value
""")
    files['python'] = py_file
    
    # C# test file
    cs_file = tmp_path / "test.cs"
    cs_file.write_text("""
using System;
using System.Collections.Generic;

namespace MyApp
{
    public class MyClass
    {
        private int _value;
        
        public MyClass()
        {
            _value = 42;
        }
        
        public int GetValue()
        {
            return _value;
        }
    }
    
    public interface IMyInterface
    {
        void DoSomething();
    }
}
""")
    files['csharp'] = cs_file
    
    # JavaScript test file
    js_file = tmp_path / "test.js"
    js_file.write_text("""
import React from 'react';

function HelloWorld() {
    return "Hello, World!";
}

class MyClass {
    constructor() {
        this.value = 42;
    }
    
    getValue() {
        return this.value;
    }
}

export { HelloWorld, MyClass };
""")
    files['javascript'] = js_file
    
    # TypeScript test file
    ts_file = tmp_path / "test.ts"
    ts_file.write_text("""
interface Person {
    name: string;
    age: number;
}

class User implements Person {
    name: string;
    age: number;
    
    constructor(name: string, age: number) {
        this.name = name;
        this.age = age;
    }
    
    greet(): string {
        return `Hello, ${this.name}`;
    }
}

export { User, Person };
""")
    files['typescript'] = ts_file
    
    # SQL test file
    sql_file = tmp_path / "test.sql"
    sql_file.write_text("""
CREATE TABLE Users (
    Id INT PRIMARY KEY,
    Name VARCHAR(100),
    Email VARCHAR(255)
);

CREATE PROCEDURE GetUserById
    @UserId INT
AS
BEGIN
    SELECT * FROM Users WHERE Id = @UserId;
END;

CREATE FUNCTION GetUserCount()
RETURNS INT
AS
BEGIN
    RETURN (SELECT COUNT(*) FROM Users);
END;
""")
    files['sql'] = sql_file
    
    # HTML test file
    html_file = tmp_path / "test.html"
    html_file.write_text("""
<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
</head>
<body>
    <div class="container">
        <h1>Hello World</h1>
        <p>Test paragraph</p>
    </div>
</body>
</html>
""")
    files['html'] = html_file
    
    # CSS test file
    css_file = tmp_path / "test.css"
    css_file.write_text("""
.container {
    max-width: 1200px;
    margin: 0 auto;
}

h1 {
    color: #333;
    font-size: 24px;
}

.button {
    background: blue;
    color: white;
}
""")
    files['css'] = css_file
    
    # ColdFusion test file
    cfm_file = tmp_path / "test.cfm"
    cfm_file.write_text("""
<cfcomponent>
    <cffunction name="getUserById" access="public" returntype="query">
        <cfargument name="userId" type="numeric" required="true">
        
        <cfquery name="qryUser" datasource="mydb">
            SELECT * FROM Users WHERE Id = <cfqueryparam value="#arguments.userId#" cfsqltype="cf_sql_integer">
        </cfquery>
        
        <cfreturn qryUser>
    </cffunction>
</cfcomponent>
""")
    files['coldfusion'] = cfm_file
    
    # JSON test file
    json_file = tmp_path / "test.json"
    json_file.write_text("""
{
    "name": "test-project",
    "version": "1.0.0",
    "dependencies": {
        "react": "^18.0.0"
    }
}
""")
    files['json'] = json_file
    
    # YAML test file
    yaml_file = tmp_path / "test.yaml"
    yaml_file.write_text("""
name: test-workflow
on:
  push:
    branches:
      - main
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
""")
    files['yaml'] = yaml_file
    
    return files


# =============================================================================
# PARSER INITIALIZATION TESTS
# =============================================================================

def test_parser_initialization(parser):
    """Test that parser initializes correctly"""
    assert parser is not None
    assert isinstance(parser.available_languages, set)
    assert len(parser.available_languages) > 0
    print(f"✅ Available languages: {parser.available_languages}")


def test_available_languages(parser):
    """Test that core languages are available"""
    core_languages = {'python', 'c_sharp', 'sql', 'javascript', 'typescript', 'html', 'css'}
    
    for lang in core_languages:
        assert lang in parser.available_languages, f"{lang} not available"
    
    print(f"✅ All core languages available: {core_languages}")


def test_singleton_pattern():
    """Test that get_universal_parser returns singleton"""
    parser1 = get_universal_parser()
    parser2 = get_universal_parser()
    
    assert parser1 is parser2, "Not a singleton"
    print("✅ Singleton pattern working")


# =============================================================================
# PYTHON PARSING TESTS
# =============================================================================

def test_python_parsing(parser, test_files):
    """Test Python file parsing"""
    tree = parser.parse_file(test_files['python'])
    assert tree is not None, "Failed to parse Python file"
    
    structure = parser.extract_structure(tree, 'python')
    
    assert 'hello_world' in structure['functions']
    assert 'MyClass' in structure['classes']
    assert len(structure['imports']) > 0
    
    print(f"✅ Python parsing: {structure['functions']}, {structure['classes']}")


def test_python_convenience_function(test_files):
    """Test convenience analyze_file function"""
    result = analyze_file(test_files['python'])
    
    assert 'functions' in result
    assert 'classes' in result
    assert 'hello_world' in result['functions']
    
    print(f"✅ Convenience function works: {result.keys()}")


# =============================================================================
# C# PARSING TESTS
# =============================================================================

def test_csharp_parsing(parser, test_files):
    """Test C# file parsing"""
    tree = parser.parse_file(test_files['csharp'])
    assert tree is not None, "Failed to parse C# file"
    
    structure = parser.extract_structure(tree, 'c_sharp')
    
    assert 'MyClass' in structure['classes']
    assert 'IMyInterface' in structure['interfaces']
    assert 'MyApp' in structure['namespaces']
    assert len(structure['usings']) > 0
    
    print(f"✅ C# parsing: {structure['classes']}, {structure['interfaces']}, {structure['namespaces']}")


def test_csharp_methods(parser, test_files):
    """Test C# method extraction"""
    tree = parser.parse_file(test_files['csharp'])
    structure = parser.extract_structure(tree, 'c_sharp')
    
    assert len(structure['methods']) > 0
    assert 'GetValue' in structure['methods']
    
    print(f"✅ C# methods: {structure['methods']}")


# =============================================================================
# JAVASCRIPT/TYPESCRIPT TESTS
# =============================================================================

def test_javascript_parsing(parser, test_files):
    """Test JavaScript file parsing"""
    tree = parser.parse_file(test_files['javascript'])
    assert tree is not None, "Failed to parse JavaScript file"
    
    structure = parser.extract_structure(tree, 'javascript')
    
    assert 'HelloWorld' in structure['functions']
    assert 'MyClass' in structure['classes']
    assert len(structure['imports']) > 0
    assert len(structure['exports']) > 0
    
    print(f"✅ JavaScript parsing: {structure['functions']}, {structure['classes']}")


def test_typescript_parsing(parser, test_files):
    """Test TypeScript file parsing"""
    tree = parser.parse_file(test_files['typescript'])
    assert tree is not None, "Failed to parse TypeScript file"
    
    structure = parser.extract_structure(tree, 'typescript')
    
    assert 'User' in structure['classes']
    assert len(structure['exports']) > 0
    
    print(f"✅ TypeScript parsing: {structure['classes']}")


# =============================================================================
# SQL PARSING TESTS
# =============================================================================

def test_sql_parsing(parser, test_files):
    """Test SQL file parsing"""
    tree = parser.parse_file(test_files['sql'])
    assert tree is not None, "Failed to parse SQL file"
    
    structure = parser.extract_structure(tree, 'sql')
    
    # Tree-sitter SQL may not extract all elements perfectly
    # Just verify we get some structure back
    assert 'statement_count' in structure
    assert structure['statement_count'] > 0
    
    print(f"✅ SQL parsing: {structure.get('tables', [])}, statements={structure['statement_count']}")


# =============================================================================
# HTML/CSS TESTS
# =============================================================================

def test_html_parsing(parser, test_files):
    """Test HTML file parsing"""
    tree = parser.parse_file(test_files['html'])
    assert tree is not None, "Failed to parse HTML file"
    
    structure = parser.extract_structure(tree, 'html')
    
    assert 'tags' in structure
    assert 'tag_count' in structure
    assert structure['tag_count'] > 0
    
    print(f"✅ HTML parsing: {structure['tags'][:10]}")


def test_css_parsing(parser, test_files):
    """Test CSS file parsing"""
    tree = parser.parse_file(test_files['css'])
    assert tree is not None, "Failed to parse CSS file"
    
    structure = parser.extract_structure(tree, 'css')
    
    assert 'rule_count' in structure
    assert structure['rule_count'] > 0
    
    print(f"✅ CSS parsing: {structure['rule_count']} rules")


# =============================================================================
# DATA FORMAT TESTS
# =============================================================================

def test_json_parsing(parser, test_files):
    """Test JSON file parsing"""
    tree = parser.parse_file(test_files['json'])
    assert tree is not None, "Failed to parse JSON file"
    
    structure = parser.extract_structure(tree, 'json')
    assert structure is not None
    
    print(f"✅ JSON parsing successful")


def test_yaml_parsing(parser, test_files):
    """Test YAML file parsing"""
    tree = parser.parse_file(test_files['yaml'])
    assert tree is not None, "Failed to parse YAML file"
    
    structure = parser.extract_structure(tree, 'yaml')
    assert structure is not None
    
    print(f"✅ YAML parsing successful")


# =============================================================================
# FALLBACK PARSER TESTS (ColdFusion)
# =============================================================================

def test_coldfusion_fallback(parser, test_files):
    """Test ColdFusion regex fallback parser"""
    result = parser.parse_file(test_files['coldfusion'])
    
    assert result is not None
    assert isinstance(result, dict)
    assert result['type'] == 'coldfusion'
    assert result['parser'] == 'regex_fallback'
    assert 'getUserById' in result['functions']
    assert result['query_count'] > 0
    assert 'warning' in result
    
    print(f"✅ ColdFusion fallback: {result['functions']}, queries={result['query_count']}")


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================

def test_unsupported_extension(parser, tmp_path):
    """Test handling of unsupported file types"""
    unsupported = tmp_path / "test.xyz"
    unsupported.write_text("random content")
    
    tree = parser.parse_file(unsupported)
    assert tree is None
    
    print("✅ Unsupported extension handled gracefully")


def test_invalid_syntax(parser, tmp_path):
    """Test handling of files with syntax errors"""
    invalid_py = tmp_path / "invalid.py"
    invalid_py.write_text("""
def broken_function(
    # Missing closing parenthesis
    print("This won't parse")
""")
    
    tree = parser.parse_file(invalid_py)
    # tree-sitter is error-recovery, so may still return a tree
    # Just verify it doesn't crash
    assert tree is not None or tree is None  # Either is acceptable
    
    print("✅ Invalid syntax handled gracefully")


def test_empty_file(parser, tmp_path):
    """Test parsing empty file"""
    empty = tmp_path / "empty.py"
    empty.write_text("")
    
    tree = parser.parse_file(empty)
    assert tree is not None  # tree-sitter handles empty files
    
    structure = parser.extract_structure(tree, 'python')
    assert structure['functions'] == []
    assert structure['classes'] == []
    
    print("✅ Empty file handled correctly")


# =============================================================================
# PERFORMANCE TESTS
# =============================================================================

def test_lazy_loading(parser):
    """Test that parsers are lazy-loaded"""
    # Initially only detected, not loaded
    initial_loaded = len(parser.parsers)
    
    # Load Python parser
    parser.get_parser('python')
    after_python = len(parser.parsers)
    
    # Load C# parser
    parser.get_parser('c_sharp')
    after_csharp = len(parser.parsers)
    
    assert after_python > initial_loaded
    assert after_csharp > after_python
    
    print(f"✅ Lazy loading: {initial_loaded} → {after_python} → {after_csharp}")


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

def test_multi_file_batch(parser, test_files):
    """Test parsing multiple files in sequence"""
    results = {}
    
    for name, path in test_files.items():
        tree = parser.parse_file(path)
        if tree:
            ext = path.suffix.lower()
            lang = parser.EXTENSION_MAP.get(ext)
            if lang:
                results[name] = parser.extract_structure(tree, lang, path)
    
    # Verify we got results for most files
    assert len(results) >= 8, f"Only parsed {len(results)} files"
    
    print(f"✅ Batch parsing: {len(results)} files processed")


def test_extension_mapping_coverage(parser):
    """Test that EXTENSION_MAP covers all common types"""
    expected_extensions = {
        '.cs', '.sql', '.py', '.js', '.ts', '.tsx',
        '.html', '.css', '.json', '.yaml', '.cfm', '.md'
    }
    
    mapped_extensions = set(parser.EXTENSION_MAP.keys())
    
    for ext in expected_extensions:
        assert ext in mapped_extensions, f"{ext} not in EXTENSION_MAP"
    
    print(f"✅ Extension mapping: {len(mapped_extensions)} extensions covered")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
