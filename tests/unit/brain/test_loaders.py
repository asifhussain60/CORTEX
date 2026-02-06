"""
Unit tests for YAML loaders.

Part of ENH-048: Prompt Unbloating System - Phase 2
"""

import pytest
from pathlib import Path
from cortex.brain.core.yaml_loaders import (
    CoreRulesLoader,
    AuditChecklistLoader,
    ModesLoader,
    ResponseFormatLoader,
    get_loader,
    get_cortex_registry_path,
    load_core_rules,
    load_audit_checklist,
    load_modes,
    load_response_format,
    YAMLLoadError,
)
from cortex.brain.core.models import EnforcementLevel, Priority


@pytest.fixture
def registry_path() -> Path:
    """Get registry path fixture."""
    return get_cortex_registry_path()


class TestCoreRulesLoader:
    """Tests for CoreRulesLoader."""
    
    def test_loader_initialization(self, registry_path: Path) -> None:
        """Test loader initializes correctly."""
        loader = CoreRulesLoader(registry_path / "governance" / "core-rules.yaml")
        assert loader.file_path.exists()
        assert loader.load_time_ms is None
    
    def test_loader_with_missing_file(self) -> None:
        """Test loader raises error for missing file."""
        with pytest.raises(YAMLLoadError, match="not found"):
            CoreRulesLoader(Path("/nonexistent/file.yaml"))
    
    def test_load_core_rules(self, registry_path: Path) -> None:
        """Test loading core rules."""
        loader = CoreRulesLoader(registry_path / "governance" / "core-rules.yaml")
        data = loader.load()
        
        assert data.meta["version"] == "1.0"
        assert len(data.core_rules) >= 14
        assert loader.load_time_ms is not None
        assert loader.load_time_ms < 50  # Should load in <50ms
    
    def test_load_caches_data(self, registry_path: Path) -> None:
        """Test that second load uses cache."""
        loader = CoreRulesLoader(registry_path / "governance" / "core-rules.yaml")
        
        data1 = loader.load()
        first_time = loader.load_time_ms
        
        data2 = loader.load()
        second_time = loader.load_time_ms
        
        assert data1 is data2  # Same object
        assert first_time == second_time  # Time not updated
    
    def test_get_rule_by_id(self, registry_path: Path) -> None:
        """Test retrieving specific rule."""
        loader = CoreRulesLoader(registry_path / "governance" / "core-rules.yaml")
        
        rule = loader.get_rule_by_id("CORE-008")
        assert rule is not None
        assert rule.name == "TDD Mandatory"
        assert rule.enforcement == "PRE-EXECUTION"
    
    def test_get_rule_by_id_not_found(self, registry_path: Path) -> None:
        """Test retrieving nonexistent rule."""
        loader = CoreRulesLoader(registry_path / "governance" / "core-rules.yaml")
        
        rule = loader.get_rule_by_id("CORE-999")
        assert rule is None
    
    def test_get_rules_by_enforcement(self, registry_path: Path) -> None:
        """Test filtering rules by enforcement level."""
        loader = CoreRulesLoader(registry_path / "governance" / "core-rules.yaml")
        
        blocked_rules = loader.get_rules_by_enforcement("BLOCKED")
        assert len(blocked_rules) > 0
        assert all(r.enforcement == "BLOCKED" for r in blocked_rules)
    
    def test_convenience_function(self) -> None:
        """Test load_core_rules convenience function."""
        data = load_core_rules()
        assert data.meta["version"] == "1.0"
        assert len(data.core_rules) >= 14


class TestAuditChecklistLoader:
    """Tests for AuditChecklistLoader."""
    
    def test_load_audit_checklist(self, registry_path: Path) -> None:
        """Test loading audit checklist."""
        loader = AuditChecklistLoader(registry_path / "governance" / "audit-checklist.yaml")
        data = loader.load()
        
        assert data.meta["version"] == "1.0"
        assert "P0" in data.priority_checks
        assert len(data.priority_checks["P0"].checks) >= 1  # Access checks within PriorityCategory
        assert loader.load_time_ms is not None
        assert loader.load_time_ms < 50
    
    def test_get_checks_by_priority(self, registry_path: Path) -> None:
        """Test retrieving checks by priority."""
        loader = AuditChecklistLoader(registry_path / "governance" / "audit-checklist.yaml")
        
        p0_checks = loader.get_checks_by_priority("P0")
        assert len(p0_checks) > 0
        assert all(check.id.startswith("P0-") for check in p0_checks)
    
    def test_get_check_by_id(self, registry_path: Path) -> None:
        """Test retrieving specific check."""
        loader = AuditChecklistLoader(registry_path / "governance" / "audit-checklist.yaml")
        
        check = loader.get_check_by_id("P0-001")
        assert check is not None
        assert check.name == "Secrets Scan"
        assert check.tool == "grep_search"
    
    def test_convenience_function(self) -> None:
        """Test load_audit_checklist convenience function."""
        data = load_audit_checklist()
        assert data.meta["version"] == "1.0"
        assert "P0" in data.priority_checks


class TestModesLoader:
    """Tests for ModesLoader."""
    
    def test_load_modes(self, registry_path: Path) -> None:
        """Test loading modes."""
        loader = ModesLoader(registry_path / "meta" / "modes.yaml")
        data = loader.load()
        
        assert data.meta["version"] == "1.0"
        assert len(data.modes) == 7
        assert "PRE-FLIGHT" in data.modes
        assert loader.load_time_ms is not None
        assert loader.load_time_ms < 50
    
    def test_get_mode(self, registry_path: Path) -> None:
        """Test retrieving specific mode."""
        loader = ModesLoader(registry_path / "meta" / "modes.yaml")
        
        mode = loader.get_mode("AUDIT")
        assert mode is not None
        assert mode.agent == "cortex-auditor"
        assert mode.priority == 1
    
    def test_get_all_mode_names(self, registry_path: Path) -> None:
        """Test retrieving all mode names."""
        loader = ModesLoader(registry_path / "meta" / "modes.yaml")
        
        names = loader.get_all_mode_names()
        assert len(names) == 7
        assert "PRE-FLIGHT" in names
        assert "AUDIT" in names
    
    def test_convenience_function(self) -> None:
        """Test load_modes convenience function."""
        data = load_modes()
        assert data.meta["version"] == "1.0"
        assert len(data.modes) == 7


class TestResponseFormatLoader:
    """Tests for ResponseFormatLoader."""
    
    def test_load_response_format(self, registry_path: Path) -> None:
        """Test loading response format."""
        loader = ResponseFormatLoader(registry_path / "meta" / "response-format.yaml")
        data = loader.load()
        
        assert data.meta["version"] == "1.0"
        assert "template" in data.header
        assert "status" in data.icons
        assert loader.load_time_ms is not None
        assert loader.load_time_ms < 50
    
    def test_get_header_template(self, registry_path: Path) -> None:
        """Test retrieving header template."""
        loader = ResponseFormatLoader(registry_path / "meta" / "response-format.yaml")
        
        template = loader.get_header_template()
        assert "CORTEX" in template
        assert "{mode}" in template  # Changed from {operation}
    
    def test_get_status_icons(self, registry_path: Path) -> None:
        """Test retrieving status icons."""
        loader = ResponseFormatLoader(registry_path / "meta" / "response-format.yaml")
        
        icons = loader.get_status_icons()
        assert "completed" in icons
        assert icons["completed"] == "✅"  # Extracted from nested structure
    
    def test_convenience_function(self) -> None:
        """Test load_response_format convenience function."""
        data = load_response_format()
        assert data.meta["version"] == "1.0"
        assert "template" in data.header


class TestLoaderRegistry:
    """Tests for loader registry and caching."""
    
    def test_get_loader_core_rules(self, registry_path: Path) -> None:
        """Test getting core rules loader."""
        loader = get_loader("core_rules", registry_path)
        assert isinstance(loader, CoreRulesLoader)
    
    def test_get_loader_audit_checklist(self, registry_path: Path) -> None:
        """Test getting audit checklist loader."""
        loader = get_loader("audit_checklist", registry_path)
        assert isinstance(loader, AuditChecklistLoader)
    
    def test_get_loader_modes(self, registry_path: Path) -> None:
        """Test getting modes loader."""
        loader = get_loader("modes", registry_path)
        assert isinstance(loader, ModesLoader)
    
    def test_get_loader_response_format(self, registry_path: Path) -> None:
        """Test getting response format loader."""
        loader = get_loader("response_format", registry_path)
        assert isinstance(loader, ResponseFormatLoader)
    
    def test_get_loader_invalid_type(self, registry_path: Path) -> None:
        """Test getting loader with invalid type."""
        with pytest.raises(ValueError, match="Unknown YAML type"):
            get_loader("invalid_type", registry_path)
    
    def test_get_loader_caching(self, registry_path: Path) -> None:
        """Test that get_loader caches instances."""
        loader1 = get_loader("core_rules", registry_path)
        loader2 = get_loader("core_rules", registry_path)
        
        assert loader1 is loader2  # Same instance


class TestPerformance:
    """Performance tests for loaders."""
    
    def test_all_loaders_load_under_50ms(self, registry_path: Path) -> None:
        """Test that all loaders meet <50ms target."""
        loaders = [
            ("core_rules", CoreRulesLoader, "governance/core-rules.yaml"),
            ("audit_checklist", AuditChecklistLoader, "governance/audit-checklist.yaml"),
            ("modes", ModesLoader, "meta/modes.yaml"),
            ("response_format", ResponseFormatLoader, "meta/response-format.yaml"),
        ]
        
        for name, loader_class, path in loaders:
            loader = loader_class(registry_path / path)
            loader.load()
            assert loader.load_time_ms is not None
            assert loader.load_time_ms < 50, f"{name} took {loader.load_time_ms}ms (>50ms target)"
    
    def test_lazy_loading_benefits(self, registry_path: Path) -> None:
        """Test that lazy loading doesn't load until needed."""
        loader = CoreRulesLoader(registry_path / "governance" / "core-rules.yaml")
        
        # Before load
        assert loader.load_time_ms is None
        
        # After load
        loader.load()
        assert loader.load_time_ms is not None
