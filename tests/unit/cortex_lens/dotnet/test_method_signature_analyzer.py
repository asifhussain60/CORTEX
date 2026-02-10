"""
Tests for MethodSignatureAnalyzer

AC_START: AC-PHASE67-S1-METHOD-ANALYZER-TEST-001
"""

import pytest
from cortex_lens.dotnet.method_signature_analyzer import MethodSignatureAnalyzer


@pytest.fixture
def sample_type_info():
    """Create sample type with multiple methods."""
    return {
        "Name": "UserService",
        "FullName": "Core.Services.UserService",
        "Methods": [
            {
                "Name": "GetById",
                "ReturnType": "Core.Entities.User",
                "Parameters": [
                    {"Name": "id", "Type": "int"}
                ],
                "IsPublic": True,
                "IsStatic": False,
                "IsAbstract": False,
                "IsVirtual": False
            },
            {
                "Name": "GetById",
                "ReturnType": "Core.Entities.User?",
                "Parameters": [
                    {"Name": "id", "Type": "string"}
                ],
                "IsPublic": True,
                "IsStatic": False,
                "IsAbstract": False,
                "IsVirtual": False
            },
            {
                "Name": "Create",
                "ReturnType": "void",
                "Parameters": [
                    {"Name": "name", "Type": "string"},
                    {"Name": "email", "Type": "string"}
                ],
                "IsPublic": True,
                "IsStatic": False,
                "IsAbstract": False,
                "IsVirtual": True
            },
            {
                "Name": "GetDefault",
                "ReturnType": "Core.Entities.User",
                "Parameters": [],
                "IsPublic": True,
                "IsStatic": True,
                "IsAbstract": False,
                "IsVirtual": False
            }
        ]
    }


class TestMethodSignatureAnalyzer:
    """Test suite for MethodSignatureAnalyzer."""
    
    def test_extract_signature(self, sample_type_info):
        """Test extracting method signature."""
        analyzer = MethodSignatureAnalyzer()
        method = sample_type_info["Methods"][0]
        
        sig = analyzer.extract_signature(method)
        
        assert sig["name"] == "GetById"
        assert sig["return_type"] == "Core.Entities.User"
        assert len(sig["parameters"]) == 1
        assert sig["parameters"][0]["name"] == "id"
        assert sig["parameters"][0]["type"] == "int"
        assert sig["is_public"] is True
        assert sig["is_static"] is False
    
    def test_resolve_parameter_types(self):
        """Test resolving parameter types."""
        analyzer = MethodSignatureAnalyzer()
        params = [
            {"Name": "id", "Type": "int"},
            {"Name": "name", "Type": "string?"}
        ]
        
        resolved = analyzer.resolve_parameter_types(params)
        
        assert len(resolved) == 2
        assert resolved[0]["name"] == "id"
        assert resolved[0]["type"] == "int"
        assert resolved[0]["is_nullable"] is False
        assert resolved[1]["is_nullable"] is True
    
    def test_extract_return_type(self, sample_type_info):
        """Test extracting return type."""
        analyzer = MethodSignatureAnalyzer()
        method = sample_type_info["Methods"][0]
        
        return_type = analyzer.extract_return_type(method)
        
        assert return_type == "Core.Entities.User"
    
    def test_find_methods_by_name(self, sample_type_info):
        """Test finding methods by name (includes overloads)."""
        analyzer = MethodSignatureAnalyzer()
        
        methods = analyzer.find_methods_by_name(sample_type_info, "GetById")
        
        assert len(methods) == 2  # 2 overloads
        assert all(m["Name"] == "GetById" for m in methods)
    
    def test_find_methods_by_signature(self, sample_type_info):
        """Test finding method by exact signature."""
        analyzer = MethodSignatureAnalyzer()
        
        method = analyzer.find_methods_by_signature(
            sample_type_info, 
            "GetById", 
            ["int"]
        )
        
        assert method is not None
        assert method["Name"] == "GetById"
        assert len(method["Parameters"]) == 1
        assert method["Parameters"][0]["Type"] == "int"
    
    def test_get_all_public_methods(self, sample_type_info):
        """Test retrieving all public methods."""
        analyzer = MethodSignatureAnalyzer()
        
        public_methods = analyzer.get_all_public_methods(sample_type_info)
        
        assert len(public_methods) == 4
        assert all(m["IsPublic"] for m in public_methods)
    
    def test_get_static_methods(self, sample_type_info):
        """Test retrieving static methods."""
        analyzer = MethodSignatureAnalyzer()
        
        static_methods = analyzer.get_static_methods(sample_type_info)
        
        assert len(static_methods) == 1
        assert static_methods[0]["Name"] == "GetDefault"


# AC_COMPLETE: AC-PHASE67-S1-METHOD-ANALYZER-TEST-001 ✅ 7 tests defined
