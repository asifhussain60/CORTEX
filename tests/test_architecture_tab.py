"""
Phase S2: Architecture Tab (🏗️) - TDD Test Suite
Tests for system design, layers, modules, and design patterns
"""

import pytest
from pydantic import ValidationError

from cortex.orchestrators.onboarding.dashboard_schema_models import (
    ArchitectureTab, Layer, Module, DesignPattern, RepositoryDashboardSchema
)


# ============================================================================
# FIXTURES - Test Data
# ============================================================================

@pytest.fixture
def valid_layer():
    """Valid architecture layer fixture"""
    return {
        "name": "Presentation",
        "description": "Web UI and REST APIs",
        "modules": ["WebUI", "API", "Controllers"],
        "technologies": ["React", "ASP.NET Core", "SignalR"]
    }


@pytest.fixture
def valid_module():
    """Valid code module fixture"""
    return {
        "lines_of_code": 5000,
        "files": 25,
        "complexity": 8.5,
        "sub_modules": ["OAuth", "JWT", "SessionManagement"],
        "dependencies": ["Cryptography", "Database", "Logging"]
    }


@pytest.fixture
def valid_design_pattern():
    """Valid design pattern fixture"""
    return {
        "name": "Repository Pattern",
        "description": "Data access abstraction layer",
        "location": "Data Access Layer",
        "usage_count": 45
    }


@pytest.fixture
def valid_architecture():
    """Valid complete architecture fixture"""
    return {
        "layers": [
            {
                "name": "Presentation",
                "description": "User interface and API",
                "modules": ["WebUI", "API"],
                "technologies": ["React", "ASP.NET Core"]
            },
            {
                "name": "Business Logic",
                "description": "Core business logic",
                "modules": ["Services", "Managers"],
                "technologies": ["C#", "Domain-Driven Design"]
            },
            {
                "name": "Data Access",
                "description": "Database and storage",
                "modules": ["Repositories", "DbContext"],
                "technologies": ["Entity Framework", "SQL Server"]
            }
        ],
        "modules": {
            "AuthService": {
                "lines_of_code": 5000,
                "files": 25,
                "complexity": 8.5,
                "sub_modules": ["OAuth", "JWT"],
                "dependencies": ["Cryptography", "Database"]
            },
            "PaymentService": {
                "lines_of_code": 3500,
                "files": 18,
                "complexity": 7.2,
                "sub_modules": ["StripeIntegration", "Validation"],
                "dependencies": ["HttpClient", "Logging"]
            }
        },
        "design_patterns": [
            {
                "name": "Repository Pattern",
                "description": "Data access abstraction",
                "location": "Data layer",
                "usage_count": 45
            },
            {
                "name": "Dependency Injection",
                "description": "IoC pattern",
                "location": "Application root",
                "usage_count": 120
            }
        ]
    }


# ============================================================================
# LAYER TESTS
# ============================================================================

class TestArchitectureLayers:
    """Test architecture layer validation"""
    
    def test_valid_layer(self, valid_layer):
        """Test creating valid layer"""
        layer = Layer(**valid_layer)
        assert layer.name == "Presentation"
        assert layer.description == "Web UI and REST APIs"
        assert len(layer.modules) == 3
        assert len(layer.technologies) == 3
    
    def test_layer_minimal(self):
        """Test minimal layer (required fields only)"""
        data = {
            "name": "Data Layer",
            "description": "Database access"
        }
        layer = Layer(**data)
        assert layer.name == "Data Layer"
        assert layer.modules == []
        assert layer.technologies == []
    
    def test_layer_single_module(self):
        """Test layer with single module"""
        data = {
            "name": "Caching",
            "description": "Cache layer",
            "modules": ["Redis"]
        }
        layer = Layer(**data)
        assert len(layer.modules) == 1
        assert "Redis" in layer.modules
    
    def test_layer_multiple_technologies(self):
        """Test layer with multiple technologies"""
        data = {
            "name": "Microservices",
            "description": "Independent services",
            "modules": ["Service1", "Service2"],
            "technologies": [
                "Kubernetes",
                "Docker",
                "RabbitMQ",
                "gRPC",
                "Consul"
            ]
        }
        layer = Layer(**data)
        assert len(layer.technologies) == 5
    
    def test_layer_with_empty_modules(self):
        """Test layer with explicitly empty modules"""
        data = {
            "name": "Monitoring",
            "description": "Observability",
            "modules": [],
            "technologies": ["Prometheus", "Grafana"]
        }
        layer = Layer(**data)
        assert len(layer.modules) == 0


# ============================================================================
# MODULE TESTS
# ============================================================================

class TestCodeModules:
    """Test code module validation"""
    
    def test_valid_module(self, valid_module):
        """Test valid code module"""
        module = Module(**valid_module)
        assert module.lines_of_code == 5000
        assert module.files == 25
        assert module.complexity == 8.5
    
    def test_module_zero_complexity(self):
        """Test module with zero complexity"""
        data = {
            "lines_of_code": 100,
            "files": 1,
            "complexity": 0.0
        }
        module = Module(**data)
        assert module.complexity == 0.0
    
    def test_module_high_complexity(self):
        """Test module with high complexity"""
        data = {
            "lines_of_code": 50000,
            "files": 150,
            "complexity": 250.5
        }
        module = Module(**data)
        assert module.complexity == 250.5
    
    def test_module_with_many_sub_modules(self):
        """Test module with many sub-modules"""
        data = {
            "lines_of_code": 10000,
            "files": 50,
            "complexity": 15.0,
            "sub_modules": [f"SubModule_{i}" for i in range(20)]
        }
        module = Module(**data)
        assert len(module.sub_modules) == 20
    
    def test_module_with_many_dependencies(self):
        """Test module with many dependencies"""
        data = {
            "lines_of_code": 8000,
            "files": 40,
            "complexity": 12.0,
            "dependencies": [f"Dependency_{i}" for i in range(15)]
        }
        module = Module(**data)
        assert len(module.dependencies) == 15
    
    def test_module_negative_complexity(self):
        """Test module with negative complexity (invalid)"""
        data = {
            "lines_of_code": 5000,
            "files": 25,
            "complexity": -5.0
        }
        with pytest.raises(ValidationError):
            Module(**data)
    
    def test_module_negative_files(self):
        """Test module with negative file count (invalid)"""
        data = {
            "lines_of_code": 5000,
            "files": -10,
            "complexity": 8.5
        }
        with pytest.raises(ValidationError):
            Module(**data)


# ============================================================================
# DESIGN PATTERN TESTS
# ============================================================================

class TestDesignPatterns:
    """Test design pattern validation"""
    
    def test_valid_design_pattern(self, valid_design_pattern):
        """Test valid design pattern"""
        pattern = DesignPattern(**valid_design_pattern)
        assert pattern.name == "Repository Pattern"
        assert pattern.usage_count == 45
    
    def test_single_usage_pattern(self):
        """Test design pattern with single usage"""
        data = {
            "name": "Singleton",
            "description": "Single instance pattern",
            "location": "Logger",
            "usage_count": 1
        }
        pattern = DesignPattern(**data)
        assert pattern.usage_count == 1
    
    def test_widespread_pattern(self):
        """Test widely used design pattern"""
        data = {
            "name": "Factory Pattern",
            "description": "Object creation",
            "location": "Service Factory",
            "usage_count": 500
        }
        pattern = DesignPattern(**data)
        assert pattern.usage_count == 500
    
    def test_pattern_zero_usage(self):
        """Test pattern with zero usage count"""
        data = {
            "name": "Unused Pattern",
            "description": "Not implemented",
            "location": "Architecture",
            "usage_count": 0
        }
        with pytest.raises(ValidationError):
            DesignPattern(**data)  # minimum is 1
    
    def test_pattern_description_length(self):
        """Test pattern with long description"""
        long_desc = "A very detailed explanation of the pattern " * 5
        data = {
            "name": "Custom Pattern",
            "description": long_desc,
            "location": "Custom Layer",
            "usage_count": 10
        }
        pattern = DesignPattern(**data)
        assert len(pattern.description) > 100


# ============================================================================
# COMPLETE ARCHITECTURE TESTS
# ============================================================================

class TestCompleteArchitecture:
    """Test complete architecture specifications"""
    
    def test_valid_complete_architecture(self, valid_architecture):
        """Test valid complete architecture"""
        arch = ArchitectureTab(**valid_architecture)
        assert len(arch.layers) == 3
        assert len(arch.modules) == 2
        assert len(arch.design_patterns) == 2
    
    def test_architecture_with_single_layer(self):
        """Test architecture with single layer"""
        data = {
            "layers": [
                {
                    "name": "Monolith",
                    "description": "Single tier application"
                }
            ]
        }
        arch = ArchitectureTab(**data)
        assert len(arch.layers) == 1
        assert arch.layers[0].name == "Monolith"
    
    def test_architecture_layered_pattern(self):
        """Test classic layered architecture"""
        data = {
            "layers": [
                {
                    "name": "Presentation",
                    "description": "UI layer",
                    "technologies": ["React", "Vue"]
                },
                {
                    "name": "Application",
                    "description": "Business logic",
                    "technologies": ["C#", "Python"]
                },
                {
                    "name": "Domain",
                    "description": "Core domain",
                    "technologies": ["DDD"]
                },
                {
                    "name": "Persistence",
                    "description": "Data access",
                    "technologies": ["Entity Framework", "PostgreSQL"]
                }
            ]
        }
        arch = ArchitectureTab(**data)
        assert len(arch.layers) == 4
    
    def test_architecture_microservices_pattern(self):
        """Test microservices architecture"""
        data = {
            "modules": {
                f"Service_{i}": {
                    "lines_of_code": 5000,
                    "files": 20,
                    "complexity": 8.0,
                    "dependencies": ["API_Gateway", "Service_Discovery"]
                }
                for i in range(1, 6)  # 5 services
            }
        }
        arch = ArchitectureTab(**data)
        assert len(arch.modules) == 5
    
    def test_architecture_with_many_patterns(self):
        """Test architecture with many design patterns"""
        data = {
            "design_patterns": [
                {
                    "name": f"Pattern_{i}",
                    "description": f"Pattern {i}",
                    "location": "Module",
                    "usage_count": (i + 1) * 10
                }
                for i in range(10)
            ]
        }
        arch = ArchitectureTab(**data)
        assert len(arch.design_patterns) == 10


# ============================================================================
# ARCHITECTURE CONSISTENCY TESTS
# ============================================================================

class TestArchitectureConsistency:
    """Test consistency between architecture components"""
    
    def test_module_in_layer_consistency(self):
        """Test modules reference consistency with layers"""
        data = {
            "layers": [
                {
                    "name": "API",
                    "description": "REST API",
                    "modules": ["Controllers", "Middleware"]
                }
            ],
            "modules": {
                "Controllers": {
                    "lines_of_code": 2000,
                    "files": 10,
                    "complexity": 5.0
                },
                "Middleware": {
                    "lines_of_code": 1000,
                    "files": 5,
                    "complexity": 3.0
                }
            }
        }
        arch = ArchitectureTab(**data)
        
        # Verify modules are referenced in layers
        layer_modules = set(arch.layers[0].modules)
        arch_modules = set(arch.modules.keys())
        assert layer_modules.issubset(arch_modules)
    
    def test_dependency_count_validation(self):
        """Test high dependency count scenarios"""
        data = {
            "modules": {
                "Hub": {
                    "lines_of_code": 10000,
                    "files": 50,
                    "complexity": 20.0,
                    "dependencies": [f"Module_{i}" for i in range(30)]
                }
            }
        }
        arch = ArchitectureTab(**data)
        hub_module = arch.modules["Hub"]
        assert len(hub_module.dependencies) == 30


# ============================================================================
# ARCHITECTURE INTEGRATION TESTS
# ============================================================================

class TestArchitectureIntegration:
    """Integration tests with complete dashboard"""
    
    def test_architecture_in_complete_dashboard(self):
        """Test architecture within complete dashboard"""
        dashboard_data = {
            "metadata": {
                "name": "KSESSIONS",
                "path": "D:\\PROJECTS\\KSESSIONS",
                "primary_language": "C#",
                "total_files": 26434,
                "total_lines": 3658465,
                "contributors": 30,
                "last_updated": "2026-02-08T15:30:00Z",
                "repo_age_days": 635
            },
            "overview": {
                "health_score": 87.5,
                "code_quality": 8.2,
                "test_coverage": 92.0,
                "maintainability_index": 85.0,
                "technical_debt_hours": 120,
                "languages": {"C#": 3658465}
            },
            "architecture": {
                "layers": [
                    {
                        "name": "Presentation",
                        "description": "Web UI",
                        "modules": ["WebUI"],
                        "technologies": ["ASP.NET Core"]
                    }
                ],
                "modules": {
                    "WebUI": {
                        "lines_of_code": 500000,
                        "files": 500,
                        "complexity": 50.0
                    }
                }
            },
            "quality": {
                "code_quality_score": 8.2,
                "maintainability_index": 85.0,
                "code_smells": 15,
                "duplication_percentage": 3.5,
                "technical_debt_hours": 120,
                "test_coverage": 92.0
            },
            "vulnerabilities": {"critical": 2, "high": 5, "medium": 12, "low": 8},
            "security": {"security_score": 8.5, "security_posture": "Strong"},
            "dependencies": {
                "direct_count": 45,
                "transitive_count": 320,
                "outdated_count": 8,
                "vulnerable_count": 2
            },
            "testing": {
                "coverage_percentage": 92.0,
                "test_counts": {
                    "total": 1250,
                    "passing": 1245,
                    "failing": 3,
                    "skipped": 2
                },
                "test_types": {
                    "unit": 950,
                    "integration": 200,
                    "e2e": 100
                }
            },
            "patterns": {},
            "use_cases": {}
        }
        
        schema = RepositoryDashboardSchema(**dashboard_data)
        assert schema.architecture.layers[0].name == "Presentation"
        assert "WebUI" in schema.architecture.modules


# ============================================================================
# EDGE CASES
# ============================================================================

class TestArchitectureEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_empty_architecture(self):
        """Test minimal empty architecture"""
        data = {}
        arch = ArchitectureTab(**data)
        assert arch.layers == []
        assert arch.modules == {}
        assert arch.design_patterns == []
    
    def test_very_large_architecture(self):
        """Test architecture with many components"""
        data = {
            "layers": [
                {
                    "name": f"Layer_{i}",
                    "description": f"Layer {i}"
                }
                for i in range(20)
            ],
            "modules": {
                f"Module_{i}": {
                    "lines_of_code": i * 1000,
                    "files": i * 10,
                    "complexity": float(i)
                }
                for i in range(1, 101)
            }
        }
        arch = ArchitectureTab(**data)
        assert len(arch.layers) == 20
        assert len(arch.modules) == 100
    
    def test_unicode_layer_names(self):
        """Test architecture with unicode layer names"""
        data = {
            "layers": [
                {
                    "name": "Apresentação",  # Portuguese
                    "description": "UI Layer"
                },
                {
                    "name": "表现层",  # Chinese
                    "description": "Presentation"
                }
            ]
        }
        arch = ArchitectureTab(**data)
        assert len(arch.layers) == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
