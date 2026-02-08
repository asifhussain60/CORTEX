"""Phase S3: Dependencies Tab (📦) - TDD Test Suite
Tests for package management and dependency tracking
"""

import pytest
from pydantic import ValidationError
from cortex.orchestrators.onboarding.dashboard_schema_models import DependenciesTab


@pytest.fixture
def valid_dependencies():
    """Valid dependencies fixture"""
    return {
        "direct_count": 45,
        "transitive_count": 320,
        "outdated_count": 8,
        "vulnerable_count": 2,
        "packages": [],
        "dependency_graph": {},
        "licenses": []
    }


class TestDirectDependencies:
    """Test direct dependency count"""
    
    def test_zero_dependencies(self):
        """Test zero direct dependencies"""
        data = {
            "direct_count": 0,
            "transitive_count": 0,
            "outdated_count": 0,
            "vulnerable_count": 0
        }
        deps = DependenciesTab(**data)
        assert deps.direct_count == 0
    
    def test_single_dependency(self):
        """Test single direct dependency"""
        data = {
            "direct_count": 1,
            "transitive_count": 5,
            "outdated_count": 0,
            "vulnerable_count": 0
        }
        deps = DependenciesTab(**data)
        assert deps.direct_count == 1
    
    def test_many_dependencies(self):
        """Test many direct dependencies (100+)"""
        data = {
            "direct_count": 150,
            "transitive_count": 1000,
            "outdated_count": 30,
            "vulnerable_count": 5
        }
        deps = DependenciesTab(**data)
        assert deps.direct_count == 150
    
    def test_negative_dependencies(self):
        """Test negative dependency count (invalid)"""
        data = {
            "direct_count": -1,
            "transitive_count": 5,
            "outdated_count": 0,
            "vulnerable_count": 0
        }
        with pytest.raises(ValidationError):
            DependenciesTab(**data)


class TestTransitiveDependencies:
    """Test transitive dependency count"""
    
    def test_transitive_greater_than_direct(self, valid_dependencies):
        """Test transitive > direct (typical)"""
        deps = DependenciesTab(**valid_dependencies)
        # Transitive should typically be > direct
        assert deps.transitive_count >= deps.direct_count
    
    def test_transitive_zero(self):
        """Test zero transitive dependencies"""
        data = {
            "direct_count": 1,
            "transitive_count": 0,
            "outdated_count": 0,
            "vulnerable_count": 0
        }
        deps = DependenciesTab(**data)
        assert deps.transitive_count == 0
    
    def test_many_transitive(self):
        """Test high transitive count (1000+)"""
        data = {
            "direct_count": 50,
            "transitive_count": 2500,
            "outdated_count": 50,
            "vulnerable_count": 10
        }
        deps = DependenciesTab(**data)
        assert deps.transitive_count == 2500


class TestOutdatedDependencies:
    """Test outdated dependency count"""
    
    def test_zero_outdated(self):
        """Test zero outdated dependencies"""
        data = {
            "direct_count": 45,
            "transitive_count": 320,
            "outdated_count": 0,
            "vulnerable_count": 0
        }
        deps = DependenciesTab(**data)
        assert deps.outdated_count == 0
    
    def test_few_outdated(self, valid_dependencies):
        """Test few outdated dependencies"""
        deps = DependenciesTab(**valid_dependencies)
        assert deps.outdated_count == 8
    
    def test_many_outdated(self):
        """Test many outdated dependencies"""
        data = {
            "direct_count": 50,
            "transitive_count": 300,
            "outdated_count": 100,
            "vulnerable_count": 5
        }
        deps = DependenciesTab(**data)
        assert deps.outdated_count == 100
    
    def test_outdated_count(self, valid_dependencies):
        """Test outdated count validation"""
        deps = DependenciesTab(**valid_dependencies)
        # Outdated should not exceed total
        assert deps.outdated_count <= (deps.direct_count + deps.transitive_count)


class TestVulnerableDependencies:
    """Test vulnerable dependency count"""
    
    def test_zero_vulnerable(self):
        """Test zero vulnerable dependencies"""
        data = {
            "direct_count": 45,
            "transitive_count": 320,
            "outdated_count": 5,
            "vulnerable_count": 0
        }
        deps = DependenciesTab(**data)
        assert deps.vulnerable_count == 0
    
    def test_few_vulnerable(self, valid_dependencies):
        """Test few vulnerable dependencies"""
        deps = DependenciesTab(**valid_dependencies)
        assert deps.vulnerable_count == 2
    
    def test_many_vulnerable(self):
        """Test many vulnerable dependencies"""
        data = {
            "direct_count": 50,
            "transitive_count": 300,
            "outdated_count": 30,
            "vulnerable_count": 50
        }
        deps = DependenciesTab(**data)
        assert deps.vulnerable_count == 50
    
    def test_negative_vulnerable(self):
        """Test negative vulnerable count (invalid)"""
        data = {
            "direct_count": 45,
            "transitive_count": 320,
            "outdated_count": 8,
            "vulnerable_count": -1
        }
        with pytest.raises(ValidationError):
            DependenciesTab(**data)


class TestPackageList:
    """Test dependency package list"""
    
    def test_empty_packages(self, valid_dependencies):
        """Test empty package list"""
        deps = DependenciesTab(**valid_dependencies)
        assert len(deps.packages) == 0
    
    def test_dependency_graph(self, valid_dependencies):
        """Test dependency graph structure"""
        deps = DependenciesTab(**valid_dependencies)
        assert isinstance(deps.dependency_graph, dict)
    
    def test_licenses(self, valid_dependencies):
        """Test licenses tracking"""
        deps = DependenciesTab(**valid_dependencies)
        assert isinstance(deps.licenses, list)


class TestDependencyHealth:
    """Test overall dependency health assessment"""
    
    def test_healthy_dependencies(self):
        """Test healthy dependency status"""
        data = {
            "direct_count": 45,
            "transitive_count": 320,
            "outdated_count": 2,
            "vulnerable_count": 0
        }
        deps = DependenciesTab(**data)
        # Low outdated and vulnerable
        assert deps.outdated_count < 5
        assert deps.vulnerable_count == 0
    
    def test_degraded_dependencies(self):
        """Test degraded dependency status"""
        data = {
            "direct_count": 50,
            "transitive_count": 300,
            "outdated_count": 30,
            "vulnerable_count": 8
        }
        deps = DependenciesTab(**data)
        # High outdated and some vulnerable
        assert deps.outdated_count > 20
        assert deps.vulnerable_count > 0
    
    def test_critical_dependencies(self):
        """Test critical dependency status"""
        data = {
            "direct_count": 50,
            "transitive_count": 300,
            "outdated_count": 80,
            "vulnerable_count": 50
        }
        deps = DependenciesTab(**data)
        # High outdated and vulnerable
        assert deps.outdated_count > 50
        assert deps.vulnerable_count > 20


class TestDependencyEdgeCases:
    """Test dependency edge cases"""
    
    def test_minimal_dependencies(self):
        """Test minimal dependency spec"""
        data = {
            "direct_count": 0,
            "transitive_count": 0,
            "outdated_count": 0,
            "vulnerable_count": 0
        }
        deps = DependenciesTab(**data)
        assert deps.direct_count == 0
    
    def test_huge_dependency_tree(self):
        """Test huge dependency tree"""
        data = {
            "direct_count": 500,
            "transitive_count": 50000,
            "outdated_count": 1000,
            "vulnerable_count": 200
        }
        deps = DependenciesTab(**data)
        assert deps.transitive_count == 50000
