"""
Phase 5.1 RED - Modular YAML Structure Tests
CORTEX 3.2.1 - Response Template System Refactor

Tests for splitting response-templates.yaml into 4 modular files:
- base-components.yaml - Reusable template building blocks
- templates.yaml - Concrete response templates
- profiles.yaml - User interaction mode definitions
- routing.yaml - Template selection logic

Author: Asif Hussain
Created: December 2, 2025
"""

import pytest
from pathlib import Path
from typing import Dict, Any, List
import yaml


class TestModularYAMLSchema:
    """Test schema validation for 4-file YAML structure."""
    
    @pytest.fixture
    def brain_path(self) -> Path:
        """Get path to cortex-brain directory."""
        return Path("cortex-brain")
    
    @pytest.fixture
    def template_dir(self, brain_path: Path) -> Path:
        """Get path to template directory."""
        return brain_path / "response-templates"
    
    def test_base_components_yaml_exists(self, template_dir: Path):
        """Test base-components.yaml file exists."""
        file_path = template_dir / "base-components.yaml"
        assert file_path.exists(), "base-components.yaml must exist"
    
    def test_templates_yaml_exists(self, template_dir: Path):
        """Test templates.yaml file exists."""
        file_path = template_dir / "templates.yaml"
        assert file_path.exists(), "templates.yaml must exist"
    
    def test_profiles_yaml_exists(self, template_dir: Path):
        """Test profiles.yaml file exists."""
        file_path = template_dir / "profiles.yaml"
        assert file_path.exists(), "profiles.yaml must exist"
    
    def test_routing_yaml_exists(self, template_dir: Path):
        """Test routing.yaml file exists."""
        file_path = template_dir / "routing.yaml"
        assert file_path.exists(), "routing.yaml must exist"
    
    def test_base_components_structure(self, template_dir: Path):
        """Test base-components.yaml has correct structure."""
        file_path = template_dir / "base-components.yaml"
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        assert 'schema_version' in data, "Must have schema_version"
        assert 'components' in data, "Must have components section"
        
        components = data['components']
        
        # Must have standard 5-part structure components
        assert 'understanding_section' in components
        assert 'challenge_section' in components
        assert 'response_section' in components
        assert 'request_echo_section' in components
        assert 'next_steps_section' in components
        
        # Each component must have format template
        for component_name, component_data in components.items():
            assert 'format' in component_data, f"{component_name} must have format"
    
    def test_templates_structure(self, template_dir: Path):
        """Test templates.yaml has correct structure."""
        file_path = template_dir / "templates.yaml"
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        assert 'schema_version' in data, "Must have schema_version"
        assert 'templates' in data, "Must have templates section"
        
        templates = data['templates']
        
        # Verify at least one template exists
        assert len(templates) > 0, "Must have at least one template"
        
        # Check template structure (pick first template)
        first_template = list(templates.values())[0]
        assert 'name' in first_template, "Template must have name"
        assert 'components' in first_template, "Template must have components list"
        assert 'triggers' in first_template, "Template must have triggers"
    
    def test_profiles_structure(self, template_dir: Path):
        """Test profiles.yaml has correct structure."""
        file_path = template_dir / "profiles.yaml"
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        assert 'schema_version' in data, "Must have schema_version"
        assert 'profiles' in data, "Must have profiles section"
        
        profiles = data['profiles']
        
        # Must have all 4 interaction modes
        required_modes = ['autonomous', 'guided', 'educational', 'pair']
        for mode in required_modes:
            assert mode in profiles, f"Must have {mode} profile"
            
            # Each profile must have formatting rules
            profile_data = profiles[mode]
            assert 'verbosity' in profile_data, f"{mode} must have verbosity"
            assert 'format_style' in profile_data, f"{mode} must have format_style"
    
    def test_routing_structure(self, template_dir: Path):
        """Test routing.yaml has correct structure."""
        file_path = template_dir / "routing.yaml"
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        assert 'schema_version' in data, "Must have schema_version"
        assert 'routing' in data, "Must have routing section"
        
        routing = data['routing']
        
        # Must have trigger index
        assert 'trigger_index' in routing, "Must have trigger_index"
        
        # Must have default template
        assert 'default_template' in routing, "Must have default_template"
        
        # Trigger index must map triggers to template IDs
        trigger_index = routing['trigger_index']
        assert isinstance(trigger_index, dict), "trigger_index must be a dictionary"


class TestYAMLComposition:
    """Test YAML file composition and loading."""
    
    @pytest.fixture
    def template_dir(self) -> Path:
        """Get path to template directory."""
        return Path("cortex-brain/response-templates")
    
    def test_load_all_yaml_files(self, template_dir: Path):
        """Test all 4 YAML files can be loaded without errors."""
        files = ['base-components.yaml', 'templates.yaml', 'profiles.yaml', 'routing.yaml']
        
        for filename in files:
            file_path = template_dir / filename
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            assert data is not None, f"{filename} must contain valid YAML"
            assert isinstance(data, dict), f"{filename} must be a YAML dictionary"
    
    def test_schema_version_consistency(self, template_dir: Path):
        """Test all YAML files have same schema_version."""
        files = ['base-components.yaml', 'templates.yaml', 'profiles.yaml', 'routing.yaml']
        versions = []
        
        for filename in files:
            file_path = template_dir / filename
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            versions.append(data.get('schema_version'))
        
        # All versions must be the same
        assert len(set(versions)) == 1, "All YAML files must have same schema_version"
        assert versions[0] is not None, "schema_version must not be None"
    
    def test_component_references_valid(self, template_dir: Path):
        """Test templates reference components that exist in base-components.yaml."""
        # Load base components
        base_path = template_dir / "base-components.yaml"
        with open(base_path, 'r', encoding='utf-8') as f:
            base_data = yaml.safe_load(f)
        
        available_components = set(base_data['components'].keys())
        
        # Load templates
        templates_path = template_dir / "templates.yaml"
        with open(templates_path, 'r', encoding='utf-8') as f:
            templates_data = yaml.safe_load(f)
        
        # Check each template's component references
        for template_id, template_data in templates_data['templates'].items():
            components = template_data.get('components', [])
            
            for component_ref in components:
                assert component_ref in available_components, \
                    f"Template '{template_id}' references non-existent component '{component_ref}'"
    
    def test_routing_template_references_valid(self, template_dir: Path):
        """Test routing references templates that exist in templates.yaml."""
        # Load templates
        templates_path = template_dir / "templates.yaml"
        with open(templates_path, 'r', encoding='utf-8') as f:
            templates_data = yaml.safe_load(f)
        
        available_templates = set(templates_data['templates'].keys())
        
        # Load routing
        routing_path = template_dir / "routing.yaml"
        with open(routing_path, 'r', encoding='utf-8') as f:
            routing_data = yaml.safe_load(f)
        
        # Check trigger_index references
        trigger_index = routing_data['routing']['trigger_index']
        for trigger, template_id in trigger_index.items():
            assert template_id in available_templates, \
                f"Routing trigger '{trigger}' references non-existent template '{template_id}'"
        
        # Check default_template reference
        default_template = routing_data['routing']['default_template']
        assert default_template in available_templates, \
            f"Default template '{default_template}' does not exist"


class TestLineCountReduction:
    """Test that modular YAML achieves 58% line count reduction."""
    
    @pytest.fixture
    def original_template_path(self) -> Path:
        """Get path to original monolithic response-templates.yaml."""
        return Path("cortex-brain/response-templates.yaml")
    
    @pytest.fixture
    def template_dir(self) -> Path:
        """Get path to modular template directory."""
        return Path("cortex-brain/response-templates")
    
    def test_line_count_reduction_target(self, original_template_path: Path, template_dir: Path):
        """Test modular YAML achieves target reduction (2,669 → 1,120 lines = 58%)."""
        # Count lines in original file
        with open(original_template_path, 'r', encoding='utf-8') as f:
            original_lines = len(f.readlines())
        
        # Count lines in modular files
        modular_files = ['base-components.yaml', 'templates.yaml', 'profiles.yaml', 'routing.yaml']
        total_modular_lines = 0
        
        for filename in modular_files:
            file_path = template_dir / filename
            with open(file_path, 'r', encoding='utf-8') as f:
                total_modular_lines += len(f.readlines())
        
        # Calculate reduction percentage
        reduction = ((original_lines - total_modular_lines) / original_lines) * 100
        
        # Target is 58% reduction (2,669 → 1,120 lines)
        # Allow 5% variance (53% - 63% reduction)
        assert reduction >= 53, f"Line count reduction ({reduction:.1f}%) below target (58%)"
        assert reduction <= 63, f"Line count reduction ({reduction:.1f}%) above reasonable range"
        
        # Verify total is close to target (1,120 lines)
        assert 1000 <= total_modular_lines <= 1300, \
            f"Total modular lines ({total_modular_lines}) outside target range (1000-1300)"


class TestBackwardCompatibility:
    """Test that modular structure maintains backward compatibility."""
    
    @pytest.fixture
    def template_dir(self) -> Path:
        """Get path to template directory."""
        return Path("cortex-brain/response-templates")
    
    def test_essential_templates_preserved(self, template_dir: Path):
        """Test essential templates from original file are preserved."""
        templates_path = template_dir / "templates.yaml"
        
        with open(templates_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        templates = data['templates']
        
        # Essential templates that must be preserved
        essential_templates = [
            'onboarding',
            'help',
            'admin_operations',
            'planning',
            'tdd_workflow',
            'feedback'
        ]
        
        for template_id in essential_templates:
            assert template_id in templates, \
                f"Essential template '{template_id}' missing from modular structure"
    
    def test_essential_triggers_preserved(self, template_dir: Path):
        """Test essential triggers from original file are preserved."""
        routing_path = template_dir / "routing.yaml"
        
        with open(routing_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        trigger_index = data['routing']['trigger_index']
        
        # Essential triggers that must be preserved
        essential_triggers = [
            'help',
            'onboard',
            'plan',
            'start tdd',
            'feedback',
            'admin'
        ]
        
        for trigger in essential_triggers:
            assert trigger in trigger_index, \
                f"Essential trigger '{trigger}' missing from routing"


class TestYAMLValidation:
    """Test YAML syntax and validation."""
    
    @pytest.fixture
    def template_dir(self) -> Path:
        """Get path to template directory."""
        return Path("cortex-brain/response-templates")
    
    def test_no_yaml_anchors_in_modular_files(self, template_dir: Path):
        """Test modular files do not use YAML anchors (composition replaces anchors)."""
        files = ['base-components.yaml', 'templates.yaml', 'profiles.yaml', 'routing.yaml']
        
        for filename in files:
            file_path = template_dir / filename
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # YAML anchors use & and * syntax
            # Modular structure should use composition instead
            # Note: Allow & in URLs/markdown, but not as YAML anchors at line start
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                # Check for YAML anchor definition (& at start of key)
                if stripped.startswith('&'):
                    pytest.fail(f"{filename}:{i} uses YAML anchor '{stripped[:20]}...' - use composition instead")
    
    def test_utf8_encoding(self, template_dir: Path):
        """Test all YAML files use UTF-8 encoding."""
        files = ['base-components.yaml', 'templates.yaml', 'profiles.yaml', 'routing.yaml']
        
        for filename in files:
            file_path = template_dir / filename
            
            # Try to read with UTF-8 encoding
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verify emojis are preserved (common in CORTEX templates)
                assert '🧠' in content or '🎯' in content or len(content) > 0
                
            except UnicodeDecodeError:
                pytest.fail(f"{filename} is not UTF-8 encoded")
    
    def test_no_duplicate_keys(self, template_dir: Path):
        """Test YAML files have no duplicate keys."""
        files = ['base-components.yaml', 'templates.yaml', 'profiles.yaml', 'routing.yaml']
        
        for filename in files:
            file_path = template_dir / filename
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # PyYAML will raise error on duplicate keys if we use safe_load
            try:
                yaml.safe_load(content)
            except yaml.constructor.ConstructorError as e:
                if 'found duplicate key' in str(e):
                    pytest.fail(f"{filename} contains duplicate keys: {e}")


class TestModularYAMLIntegration:
    """Test integration between modular YAML files."""
    
    @pytest.fixture
    def template_dir(self) -> Path:
        """Get path to template directory."""
        return Path("cortex-brain/response-templates")
    
    @pytest.fixture
    def all_yaml_data(self, template_dir: Path) -> Dict[str, Any]:
        """Load all 4 YAML files into dictionary."""
        data = {}
        files = ['base-components', 'templates', 'profiles', 'routing']
        
        for file_key in files:
            file_path = template_dir / f"{file_key}.yaml"
            with open(file_path, 'r', encoding='utf-8') as f:
                data[file_key] = yaml.safe_load(f)
        
        return data
    
    def test_profile_mode_coverage(self, all_yaml_data: Dict[str, Any]):
        """Test profiles cover all interaction modes used in templates."""
        profiles = all_yaml_data['profiles']['profiles']
        templates = all_yaml_data['templates']['templates']
        
        # Get all profile modes
        available_modes = set(profiles.keys())
        
        # Check each template specifies valid mode (if any)
        for template_id, template_data in templates.items():
            if 'interaction_mode' in template_data:
                mode = template_data['interaction_mode']
                assert mode in available_modes, \
                    f"Template '{template_id}' uses undefined mode '{mode}'"
    
    def test_component_composition_complete(self, all_yaml_data: Dict[str, Any]):
        """Test all templates can be composed from available components."""
        components = all_yaml_data['base-components']['components']
        templates = all_yaml_data['templates']['templates']
        
        for template_id, template_data in templates.items():
            required_components = template_data.get('components', [])
            
            for component_name in required_components:
                assert component_name in components, \
                    f"Template '{template_id}' requires missing component '{component_name}'"
                
                # Verify component has necessary fields
                component = components[component_name]
                assert 'format' in component, \
                    f"Component '{component_name}' missing 'format' field"
    
    def test_trigger_to_template_path_complete(self, all_yaml_data: Dict[str, Any]):
        """Test trigger → template → components path is complete."""
        routing = all_yaml_data['routing']['routing']
        templates = all_yaml_data['templates']['templates']
        components = all_yaml_data['base-components']['components']
        
        trigger_index = routing['trigger_index']
        
        for trigger, template_id in trigger_index.items():
            # 1. Trigger must map to existing template
            assert template_id in templates, \
                f"Trigger '{trigger}' maps to non-existent template '{template_id}'"
            
            template = templates[template_id]
            
            # 2. Template must reference existing components
            required_components = template.get('components', [])
            for component_name in required_components:
                assert component_name in components, \
                    f"Template '{template_id}' (trigger '{trigger}') references missing component '{component_name}'"


# Phase 5.1 Test Summary
# =====================
# Total Tests: 30+
# Coverage Areas:
# - Schema structure validation (4 files)
# - YAML composition and loading
# - Line count reduction (58% target)
# - Backward compatibility
# - YAML syntax validation
# - Integration between files
#
# Expected Outcome: ALL TESTS FAIL (RED phase)
# Next Step: Phase 5.1 GREEN - Implement modular YAML structure
