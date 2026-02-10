"""
Tests for TypeSymbolResolver

AC_START: AC-PHASE67-S1-TYPE-RESOLVER-TEST-001
"""

import pytest
from pathlib import Path
from cortex_lens.dotnet.type_symbol_resolver import TypeSymbolResolver


@pytest.fixture
def sample_semantic_model():
    """Create sample semantic model with type relationships."""
    return [
        {
            "Name": "Core",
            "Types": [
                {
                    "Name": "IEntity",
                    "FullName": "Core.Entities.IEntity",
                    "Namespace": "Core.Entities",
                    "Kind": "Interface",
                    "BaseType": None,
                    "Interfaces": [],
                    "Methods": [],
                    "Properties": [
                        {"Name": "Id", "Type": "int", "IsPublic": True, "HasGetter": True, "HasSetter": True}
                    ]
                },
                {
                    "Name": "EntityBase",
                    "FullName": "Core.Entities.EntityBase",
                    "Namespace": "Core.Entities",
                    "Kind": "Class",
                    "IsAbstract": True,
                    "BaseType": "object",
                    "Interfaces": ["Core.Entities.IEntity"],
                    "Methods": [],
                    "Properties": [
                        {"Name": "Id", "Type": "int", "IsPublic": True, "HasGetter": True, "HasSetter": True}
                    ]
                },
                {
                    "Name": "User",
                    "FullName": "Core.Entities.User",
                    "Namespace": "Core.Entities",
                    "Kind": "Class",
                    "BaseType": "Core.Entities.EntityBase",
                    "Interfaces": [],  # Inherits IEntity from EntityBase
                    "Methods": [
                        {"Name": "GetDisplayName", "ReturnType": "string", "Parameters": [], "IsPublic": True}
                    ],
                    "Properties": [
                        {"Name": "Name", "Type": "string", "IsPublic": True, "HasGetter": True, "HasSetter": True}
                    ]
                },
                {
                    "Name": "Product",
                    "FullName": "Core.Entities.Product",
                    "Namespace": "Core.Entities",
                    "Kind": "Class",
                    "BaseType": "object",
                    "Interfaces": ["Core.Entities.IEntity"],
                    "Methods": [],
                    "Properties": [
                        {"Name": "Id", "Type": "int", "IsPublic": True, "HasGetter": True, "HasSetter": True},
                        {"Name": "Title", "Type": "string", "IsPublic": True, "HasGetter": True, "HasSetter": True}
                    ]
                }
            ]
        }
    ]


class TestTypeSymbolResolver:
    """Test suite for TypeSymbolResolver."""
    
    def test_init(self, sample_semantic_model):
        """Test resolver initialization."""
        resolver = TypeSymbolResolver(sample_semantic_model)
        
        assert resolver is not None
        assert hasattr(resolver, 'resolve_interface_implementations')
        assert len(resolver._type_index) > 0
    
    def test_resolve_interface_implementations(self, sample_semantic_model):
        """
        Test finding types implementing an interface.
        
        AC: Resolve IEntity → [EntityBase, Product]
        """
        resolver = TypeSymbolResolver(sample_semantic_model)
        
        implementations = resolver.resolve_interface_implementations("IEntity")
        
        assert len(implementations) == 2
        impl_names = [t["Name"] for t in implementations]
        assert "EntityBase" in impl_names
        assert "Product" in impl_names
    
    def test_resolve_base_classes(self, sample_semantic_model):
        """
        Test resolving base class hierarchy.
        
        AC: User → [EntityBase, object]
        """
        resolver = TypeSymbolResolver(sample_semantic_model)
        
        bases = resolver.resolve_base_classes("User")
        
        assert len(bases) >= 1
        assert "EntityBase" in bases[0]
        assert "object" in bases
    
    def test_resolve_derived_types(self, sample_semantic_model):
        """
        Test finding types deriving from base class.
        
        AC: EntityBase → [User]
        """
        resolver = TypeSymbolResolver(sample_semantic_model)
        
        derived = resolver.resolve_derived_types("EntityBase")
        
        assert len(derived) == 1
        assert derived[0]["Name"] == "User"
    
    def test_get_type_info(self, sample_semantic_model):
        """Test retrieving type information by name."""
        resolver = TypeSymbolResolver(sample_semantic_model)
        
        user_info = resolver.get_type_info("User")
        
        assert user_info is not None
        assert user_info["Name"] == "User"
        assert user_info["FullName"] == "Core.Entities.User"
        assert len(user_info["Methods"]) >= 1
    
    def test_get_all_types(self, sample_semantic_model):
        """Test retrieving all types."""
        resolver = TypeSymbolResolver(sample_semantic_model)
        
        all_types = resolver.get_all_types()
        
        assert len(all_types) == 4  # IEntity, EntityBase, User, Product
        type_names = [t["Name"] for t in all_types]
        assert "IEntity" in type_names
        assert "User" in type_names


# AC_COMPLETE: AC-PHASE67-S1-TYPE-RESOLVER-TEST-001 ✅ 6 tests defined
