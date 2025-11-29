"""Tests for Namespace value object"""
import pytest
from src.domain.value_objects import Namespace


class TestNamespaceCreation:
    """Test Namespace creation and validation"""
    
    def test_create_valid_namespace(self):
        """Should create namespace with valid format"""
        ns = Namespace(value="cortex.brain.tier1")
        assert ns.value == "cortex.brain.tier1"
    
    def test_create_root_namespace(self):
        """Should create root-level namespace"""
        ns = Namespace(value="cortex")
        assert ns.value == "cortex"
    
    def test_reject_empty_namespace(self):
        """Should reject empty namespace"""
        with pytest.raises(ValueError, match="Namespace.value cannot be empty"):
            Namespace(value="")
    
    def test_reject_whitespace_namespace(self):
        """Should reject whitespace-only namespace"""
        with pytest.raises(ValueError, match="Namespace.value cannot be empty"):
            Namespace(value="   ")
    
    def test_reject_invalid_characters(self):
        """Should reject invalid characters"""
        with pytest.raises(ValueError, match="Invalid namespace format"):
            Namespace(value="cortex.brain@tier1")
    
    def test_reject_leading_dot(self):
        """Should reject leading dot"""
        with pytest.raises(ValueError, match="Invalid namespace format"):
            Namespace(value=".cortex.brain")
    
    def test_reject_trailing_dot(self):
        """Should reject trailing dot"""
        with pytest.raises(ValueError, match="Invalid namespace format"):
            Namespace(value="cortex.brain.")
    
    def test_reject_consecutive_dots(self):
        """Should reject consecutive dots"""
        with pytest.raises(ValueError, match="Invalid namespace format"):
            Namespace(value="cortex..brain")


class TestNamespaceStructure:
    """Test namespace structure properties"""
    
    def test_root_property(self):
        """Should extract root namespace"""
        ns = Namespace(value="cortex.brain.tier1")
        assert ns.root == "cortex"
    
    def test_root_property_single_level(self):
        """Should return self for single-level namespace"""
        ns = Namespace(value="cortex")
        assert ns.root == "cortex"
    
    def test_is_workspace_cortex(self):
        """Should identify cortex workspace"""
        ns = Namespace(value="cortex.brain.tier1")
        assert ns.is_workspace
    
    def test_is_workspace_user_workspace(self):
        """Should identify user workspace"""
        ns = Namespace(value="workspace.myproject.backend")
        assert ns.is_workspace
    
    def test_is_not_workspace(self):
        """Should not identify external namespace as workspace"""
        ns = Namespace(value="external.library.utils")
        assert not ns.is_workspace


class TestNamespacePriority:
    """Test priority multiplier logic"""
    
    def test_workspace_priority(self):
        """Should give 2.0x priority to workspace namespace"""
        ns = Namespace(value="workspace.myproject.backend")
        assert ns.priority_multiplier == 2.0
    
    def test_cortex_priority(self):
        """Should give 1.5x priority to cortex namespace"""
        ns = Namespace(value="cortex.brain.tier1")
        assert ns.priority_multiplier == 1.5
    
    def test_external_priority(self):
        """Should give 0.5x priority to external namespace"""
        ns = Namespace(value="external.library.utils")
        assert ns.priority_multiplier == 0.5
    
    def test_other_priority(self):
        """Should give 1.0x priority to other namespaces"""
        ns = Namespace(value="custom.module.helper")
        assert ns.priority_multiplier == 1.0


class TestNamespaceHierarchy:
    """Test namespace hierarchy methods"""
    
    def test_is_parent_of_direct_child(self):
        """Should identify direct child"""
        parent = Namespace(value="cortex")
        child = Namespace(value="cortex.brain")
        assert parent.is_parent_of(child)
    
    def test_is_parent_of_nested_child(self):
        """Should identify nested child"""
        parent = Namespace(value="cortex")
        child = Namespace(value="cortex.brain.tier1")
        assert parent.is_parent_of(child)
    
    def test_is_not_parent_of_different_root(self):
        """Should not identify different root as child"""
        parent = Namespace(value="cortex")
        other = Namespace(value="workspace.project")
        assert not parent.is_parent_of(other)
    
    def test_is_not_parent_of_self(self):
        """Should not be parent of itself"""
        ns = Namespace(value="cortex.brain")
        assert not ns.is_parent_of(ns)
    
    def test_is_not_parent_of_sibling(self):
        """Should not identify sibling as child"""
        ns1 = Namespace(value="cortex.brain")
        ns2 = Namespace(value="cortex.memory")
        assert not ns1.is_parent_of(ns2)


class TestNamespacePatternMatching:
    """Test pattern matching functionality"""
    
    def test_matches_exact_pattern(self):
        """Should match exact namespace"""
        ns = Namespace(value="cortex.brain.tier1")
        assert ns.matches_pattern("cortex.brain.tier1")
    
    def test_matches_wildcard_pattern(self):
        """Should match wildcard pattern"""
        ns = Namespace(value="cortex.brain.tier1")
        assert ns.matches_pattern("cortex.brain.*")
    
    def test_matches_root_wildcard(self):
        """Should match root-level wildcard"""
        ns = Namespace(value="cortex.brain.tier1")
        assert ns.matches_pattern("cortex.*")
    
    def test_matches_all_wildcard(self):
        """Should match universal wildcard"""
        ns = Namespace(value="cortex.brain.tier1")
        assert ns.matches_pattern("*")
    
    def test_does_not_match_different_pattern(self):
        """Should not match different pattern"""
        ns = Namespace(value="cortex.brain.tier1")
        assert not ns.matches_pattern("workspace.*")
    
    def test_does_not_match_partial_pattern(self):
        """Should not match partial pattern"""
        ns = Namespace(value="cortex.brain.tier1")
        assert not ns.matches_pattern("cortex.brain.tier2")


class TestNamespaceValueObjectBehavior:
    """Test value object behavior"""
    
    def test_equality_same_value(self):
        """Should be equal with same value"""
        ns1 = Namespace(value="cortex.brain.tier1")
        ns2 = Namespace(value="cortex.brain.tier1")
        assert ns1 == ns2
    
    def test_inequality_different_values(self):
        """Should not be equal with different values"""
        ns1 = Namespace(value="cortex.brain.tier1")
        ns2 = Namespace(value="cortex.brain.tier2")
        assert ns1 != ns2
    
    def test_hashable(self):
        """Should be hashable"""
        ns1 = Namespace(value="cortex.brain.tier1")
        ns2 = Namespace(value="cortex.brain.tier1")
        ns3 = Namespace(value="cortex.brain.tier2")
        
        ns_set = {ns1, ns2, ns3}
        assert len(ns_set) == 2
    
    def test_immutable(self):
        """Should be immutable"""
        ns = Namespace(value="cortex.brain.tier1")
        with pytest.raises(Exception):
            ns.value = "cortex.brain.tier2"
