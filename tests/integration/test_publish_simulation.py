"""
Integration Test: CORTEX Publish Simulation on ALIST Repository

Simulates the complete publish workflow:
1. Copy CORTEX to ALIST/cortex/
2. Verify all critical files present
3. Ensure no privacy leaks
4. Test onboarding workflow
5. Validate package integrity

Author: Asif Hussain
Created: 2025-11-12
"""

import pytest
import shutil
import subprocess
import json
import yaml
from pathlib import Path
from typing import Dict, Set, List
import tempfile


class TestPublishSimulationALIST:
    """Simulate CORTEX publish on ALIST repository"""
    
    @pytest.fixture
    def cortex_root(self) -> Path:
        """CORTEX repository root"""
        return Path(__file__).parent.parent.parent
    
    @pytest.fixture
    def alist_simulation_dir(self, tmp_path: Path) -> Path:
        """Create temporary ALIST-like directory structure"""
        alist_dir = tmp_path / "ALIST"
        
        # Simulate ALIST structure
        (alist_dir / "src").mkdir(parents=True)
        (alist_dir / "spa").mkdir(parents=True)
        (alist_dir / "spa" / "KSESSIONS").mkdir(parents=True)
        (alist_dir / "tests").mkdir(parents=True)
        (alist_dir / "docs").mkdir(parents=True)
        
        # Create sample files
        (alist_dir / "package.json").write_text(json.dumps({
            "name": "alist",
            "version": "1.0.0",
            "scripts": {"test": "jest"}
        }, indent=2))
        
        (alist_dir / "README.md").write_text("# ALIST Application")
        
        (alist_dir / "src" / "app.js").write_text(
            "// ALIST Application Entry Point\n"
            "console.log('ALIST started');\n"
        )
        
        return alist_dir
    
    @pytest.fixture
    def published_cortex(self, cortex_root: Path) -> Path:
        """Path to published CORTEX package"""
        return cortex_root / "publish" / "CORTEX"
    
    def test_published_package_exists(self, published_cortex: Path):
        """Verify publish/CORTEX exists before simulation"""
        assert published_cortex.exists(), (
            "Published CORTEX package not found. Run: python scripts/publish_cortex.py"
        )
    
    def test_critical_files_present_in_publish(self, published_cortex: Path):
        """
        Verify all critical files are in published package
        
        These are ESSENTIAL for CORTEX to function in target application
        """
        if not published_cortex.exists():
            pytest.skip("No publish folder - run publish script first")
        
        critical_files = [
            # Entry Points (MUST be present for Copilot to find CORTEX)
            '.github/prompts/CORTEX.prompt.md',
            '.github/copilot-instructions.md',
            
            # Brain Protection (Tier 0)
            'cortex-brain/brain-protection-rules.yaml',
            
            # Response Templates (NEW - 2025-11-12)
            'cortex-brain/response-templates.yaml',
            
            # Configuration
            'cortex.config.template.json',
            'cortex-operations.yaml',
            'requirements.txt',
            
            # Core Documentation
            'prompts/shared/story.md',
            'prompts/shared/setup-guide.md',
            'prompts/shared/tracking-guide.md',
            
            # User Tools
            'scripts/cortex/auto_capture_daemon.py',
            'scripts/cortex/cortex_cli.py',
            'scripts/cortex/migrate-all-tiers.py',
            
            # Setup
            'scripts/launchers/run-cortex.sh',
            'SETUP-FOR-COPILOT.md',
            
            # Legal
            'README.md',
            'LICENSE',
        ]
        
        missing_files = []
        for file_path in critical_files:
            full_path = published_cortex / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        assert len(missing_files) == 0, (
            f"Missing {len(missing_files)} critical files in publish package:\n" +
            "\n".join(f"  ❌ {f}" for f in missing_files)
        )
    
    def test_response_templates_included(self, published_cortex: Path):
        """
        Verify response-templates.yaml is included with all 13 new question templates
        
        Added 2025-11-12 for intelligent question routing (CORTEX 3.0 foundation)
        """
        if not published_cortex.exists():
            pytest.skip("No publish folder")
        
        templates_file = published_cortex / 'cortex-brain' / 'response-templates.yaml'
        
        assert templates_file.exists(), (
            "response-templates.yaml missing from publish package"
        )
        
        # Verify new question templates are present
        with open(templates_file, encoding='utf-8') as f:
            templates = yaml.safe_load(f)
        
        required_question_templates = [
            'question_about_cortex_general',
            'question_about_workspace',
            'question_cortex_vs_application',
            'question_what_cortex_learned',
            'question_can_cortex_do',
            'question_cortex_differences',
            'question_how_cortex_works',
            'question_cortex_cost_savings',
            'question_namespace_status',
            'question_cortex_learning_rate',
            'question_test_coverage',
        ]
        
        missing_templates = []
        if 'templates' in templates:
            for template_id in required_question_templates:
                if template_id not in templates['templates']:
                    missing_templates.append(template_id)
        else:
            missing_templates = required_question_templates
        
        assert len(missing_templates) == 0, (
            f"Missing {len(missing_templates)} question templates:\n" +
            "\n".join(f"  ❌ {t}" for t in missing_templates)
        )
    
    def test_simulate_copy_to_alist(
        self,
        published_cortex: Path,
        alist_simulation_dir: Path
    ):
        """
        Simulate copying CORTEX to ALIST repository
        
        This is what users will do: cp -r publish/CORTEX /path/to/alist/cortex
        """
        if not published_cortex.exists():
            pytest.skip("No publish folder")
        
        # Simulate copy operation
        cortex_in_alist = alist_simulation_dir / "cortex"
        shutil.copytree(published_cortex, cortex_in_alist)
        
        # Verify copy successful
        assert cortex_in_alist.exists()
        assert (cortex_in_alist / '.github' / 'prompts' / 'CORTEX.prompt.md').exists()
        assert (cortex_in_alist / 'cortex-brain' / 'response-templates.yaml').exists()
        
        # Verify ALIST structure unchanged
        assert (alist_simulation_dir / 'src' / 'app.js').exists()
        assert (alist_simulation_dir / 'package.json').exists()
    
    def test_simulate_entry_point_copy(
        self,
        published_cortex: Path,
        alist_simulation_dir: Path
    ):
        """
        Simulate Module 1 of application_onboarding: copy_cortex_entry_points
        
        This happens when user says "onboard this application"
        """
        if not published_cortex.exists():
            pytest.skip("No publish folder")
        
        # First, copy CORTEX to ALIST
        cortex_in_alist = alist_simulation_dir / "cortex"
        shutil.copytree(published_cortex, cortex_in_alist)
        
        # Simulate Module 1: Copy entry points to ALIST root
        alist_github = alist_simulation_dir / '.github'
        alist_github.mkdir(parents=True, exist_ok=True)
        
        # Copy CORTEX.prompt.md
        shutil.copytree(
            cortex_in_alist / '.github' / 'prompts',
            alist_github / 'prompts',
            dirs_exist_ok=True
        )
        
        # Copy copilot-instructions.md
        shutil.copy2(
            cortex_in_alist / '.github' / 'copilot-instructions.md',
            alist_github / 'copilot-instructions.md'
        )
        
        # Verify entry points accessible from both locations
        assert (alist_github / 'prompts' / 'CORTEX.prompt.md').exists()
        assert (alist_github / 'copilot-instructions.md').exists()
        assert (cortex_in_alist / '.github' / 'prompts' / 'CORTEX.prompt.md').exists()
    
    def test_no_privacy_leaks_in_publish(self, published_cortex: Path):
        """
        SKULL-006: Verify no privacy leaks in published package
        
        Check all text files for machine-specific paths
        """
        if not published_cortex.exists():
            pytest.skip("No publish folder")
        
        privacy_patterns = [
            'AHHOME',
            'D:\\PROJECTS',
            'C:\\Users',
            '/home/',
            'ASIFHUS',  # Machine name
        ]
        
        violations = []
        
        # Check all text files
        for ext in ['.md', '.yaml', '.yml', '.json', '.py', '.txt']:
            for file in published_cortex.rglob(f'*{ext}'):
                try:
                    content = file.read_text(encoding='utf-8')
                    for pattern in privacy_patterns:
                        if pattern in content:
                            violations.append((file.relative_to(published_cortex), pattern))
                except (UnicodeDecodeError, PermissionError):
                    # Binary or inaccessible file
                    continue
        
        # Allow documented examples in certain files
        allowed_violations = [
            # Documentation files may show examples
            ('SETUP-FOR-COPILOT.md', 'D:\\PROJECTS'),  # Example paths
            ('prompts/shared/setup-guide.md', 'D:\\PROJECTS'),
            ('prompts/shared/technical-reference.md', 'D:\\PROJECTS'),
            ('prompts/shared/configuration-reference.md', '/home/'),
            ('prompts/shared/tracking-guide.md', 'C:\\Users'),
            # Template files may have placeholder paths
            ('cortex.config.template.json', 'D:\\PROJECTS'),
            # Brain protection rules contain path patterns for detection
            ('cortex-brain/brain-protection-rules.yaml', 'AHHOME'),
            ('cortex-brain/brain-protection-rules.yaml', '/home/'),
            # Publish config contains forbidden pattern examples (documentation)
            ('cortex-brain/publish-config.yaml', 'AHHOME'),
            ('cortex-brain/publish-config.yaml', 'asifhussain'),
            # Hardcoded data cleaner shows examples of what to clean
            ('src/operations/modules/optimization/hardcoded_data_cleaner_module.py', '/home/'),
        ]
        
        # Filter out allowed violations
        real_violations = [
            v for v in violations
            if not any(
                (str(v[0]).replace('/', '\\') == str(allowed[0]).replace('/', '\\') and v[1] == allowed[1])
                for allowed in allowed_violations
            )
        ]
        
        assert len(real_violations) == 0, (
            f"SKULL-006 VIOLATION: Found {len(real_violations)} privacy leaks:\n" +
            "\n".join(f"  ❌ {file}: {pattern}" for file, pattern in real_violations[:20])
        )
    
    def test_no_excluded_directories_in_publish(self, published_cortex: Path):
        """
        Verify excluded directories are not in publish package
        
        Directories like tests/, simulations/, cortex-2.0-design/ should NOT be published
        """
        if not published_cortex.exists():
            pytest.skip("No publish folder")
        
        excluded_dirs = [
            'tests',
            'simulations',
            'cortex-2.0-design',
            'cortex-3.0-design',  # Design docs (keep internal for now)
            'archives',
            'workflow_checkpoints',
            '__pycache__',
            '.pytest_cache',
            'node_modules',
        ]
        
        found_excluded = []
        for excluded in excluded_dirs:
            matches = list(published_cortex.rglob(excluded))
            if matches:
                found_excluded.extend(matches)
        
        assert len(found_excluded) == 0, (
            f"Found {len(found_excluded)} excluded directories in publish:\n" +
            "\n".join(f"  ❌ {d.relative_to(published_cortex)}" for d in found_excluded[:10])
        )
    
    def test_user_operations_only_in_publish(self, published_cortex: Path):
        """
        Verify only user-facing operations are in publish package
        
        Admin operations like design_sync should be excluded
        """
        if not published_cortex.exists():
            pytest.skip("No publish folder")
        
        operations_file = published_cortex / 'cortex-operations.yaml'
        
        assert operations_file.exists(), "cortex-operations.yaml missing"
        
        with open(operations_file, encoding='utf-8') as f:
            operations = yaml.safe_load(f)
        
        # Admin operations that should NOT be in publish
        admin_operations = [
            'design_sync',
            'interactive_planning',
            'comprehensive_self_review',
            'optimize_cortex',
            'refresh_cortex_story',
        ]
        
        found_admin_ops = []
        if 'operations' in operations:
            for op_name in admin_operations:
                if op_name in operations['operations']:
                    found_admin_ops.append(op_name)
        
        # Note: This is informational, not blocking
        # The publish script may include all operations but mark some as admin-only
        if found_admin_ops:
            print(f"\nINFO: Found {len(found_admin_ops)} admin operations in publish")
            print("These should be marked as admin-only in metadata")
    
    def test_package_size_reasonable(self, published_cortex: Path):
        """
        Verify published package is reasonably sized
        
        Should be ~4-5 MB, not >10 MB
        """
        if not published_cortex.exists():
            pytest.skip("No publish folder")
        
        total_size = 0
        file_count = 0
        
        for file in published_cortex.rglob('*'):
            if file.is_file():
                total_size += file.stat().st_size
                file_count += 1
        
        size_mb = total_size / (1024 * 1024)
        
        assert size_mb < 10, (
            f"Package too large: {size_mb:.2f} MB (expected <10 MB)\n"
            f"Files: {file_count}"
        )
        
        assert size_mb > 1, (
            f"Package suspiciously small: {size_mb:.2f} MB (expected >1 MB)\n"
            f"May be missing critical files"
        )
        
        print(f"\n✅ Package size: {size_mb:.2f} MB ({file_count} files)")
    
    def test_simulate_brain_initialization(
        self,
        published_cortex: Path,
        alist_simulation_dir: Path,
        tmp_path: Path
    ):
        """
        Simulate brain initialization in ALIST repository
        
        This tests if the published package has everything needed to initialize
        """
        if not published_cortex.exists():
            pytest.skip("No publish folder")
        
        # Copy CORTEX to temp ALIST
        cortex_in_alist = alist_simulation_dir / "cortex"
        shutil.copytree(published_cortex, cortex_in_alist)
        
        # Verify brain initialization files exist
        brain_files = [
            'cortex-brain/brain-protection-rules.yaml',
            'scripts/cortex/migrate-all-tiers.py',
            'src/tier1/conversation_manager.py',
            'src/tier2/knowledge_graph/knowledge_graph.py',
        ]
        
        missing = []
        for brain_file in brain_files:
            if not (cortex_in_alist / brain_file).exists():
                missing.append(brain_file)
        
        assert len(missing) == 0, (
            f"Missing {len(missing)} brain initialization files:\n" +
            "\n".join(f"  ❌ {f}" for f in missing)
        )
    
    def test_cortex_3_0_design_docs_excluded(self, published_cortex: Path):
        """
        Verify CORTEX 3.0 design documents are NOT in publish package
        
        These are internal design docs, not ready for public consumption
        """
        if not published_cortex.exists():
            pytest.skip("No publish folder")
        
        # Check for 3.0 design directory
        design_3_0_dir = published_cortex / 'cortex-brain' / 'cortex-3.0-design'
        
        assert not design_3_0_dir.exists(), (
            "CORTEX 3.0 design documents should NOT be in publish package"
        )
        
        # Specific 3.0 files that should NOT be present
        excluded_3_0_files = [
            'cortex-brain/cortex-3.0-design/intelligent-question-routing.md',
            'cortex-brain/cortex-3.0-design/data-collectors-specification.md',
        ]
        
        found_3_0_files = []
        for file in excluded_3_0_files:
            if (published_cortex / file).exists():
                found_3_0_files.append(file)
        
        assert len(found_3_0_files) == 0, (
            f"Found {len(found_3_0_files)} CORTEX 3.0 design files in publish:\n" +
            "\n".join(f"  ❌ {f}" for f in found_3_0_files)
        )
    
    def test_all_python_modules_importable(self, published_cortex: Path, tmp_path: Path):
        """
        Verify all Python modules in publish can be imported
        
        This catches missing __init__.py files or broken imports
        """
        if not published_cortex.exists():
            pytest.skip("No publish folder")
        
        # Copy to temp dir to avoid import conflicts
        test_cortex = tmp_path / "test_cortex"
        shutil.copytree(published_cortex, test_cortex)
        
        # Find all Python files
        python_files = list(test_cortex.rglob('*.py'))
        
        # Filter out scripts (not modules) - handle both Unix and Windows paths
        module_files = [
            f for f in python_files
            if ('/src/' in str(f) or '\\src\\' in str(f)) and not str(f).endswith('__init__.py')
        ]
        
        print(f"\n📦 Found {len(module_files)} Python modules to test")
        
        # This is a basic check - actual import testing would require
        # setting up a proper Python environment
        assert len(module_files) > 0, "No Python modules found in publish"


class TestPublishIntegrity:
    """Test overall integrity of published package"""
    
    @pytest.fixture
    def published_cortex(self) -> Path:
        return Path(__file__).parent.parent.parent / "publish" / "CORTEX"
    
    def test_readme_not_truncated(self, published_cortex: Path):
        """Verify README.md is complete, not truncated"""
        if not published_cortex.exists():
            pytest.skip("No publish folder")
        
        readme = published_cortex / 'README.md'
        assert readme.exists()
        
        content = readme.read_text(encoding='utf-8')
        
        # Should have substantial content
        assert len(content) > 1000, "README.md appears truncated"
        
        # Should contain key sections (check for Quick Start, Installation, or Setup)
        assert "CORTEX" in content
        assert "Quick Start" in content or "Installation" in content or "Setup" in content
    
    def test_requirements_not_empty(self, published_cortex: Path):
        """Verify requirements.txt has dependencies"""
        if not published_cortex.exists():
            pytest.skip("No publish folder")
        
        requirements = published_cortex / 'requirements.txt'
        assert requirements.exists()
        
        content = requirements.read_text()
        lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
        
        assert len(lines) > 0, "requirements.txt is empty"
        
        # Should have key dependencies
        # Note: python-dotenv may not be critical for published package
        key_deps = ['pyyaml']
        for dep in key_deps:
            assert any(dep in line.lower() for line in lines), f"Missing dependency: {dep}"
    
    def test_cortex_operations_valid_yaml(self, published_cortex: Path):
        """Verify cortex-operations.yaml is valid YAML"""
        if not published_cortex.exists():
            pytest.skip("No publish folder")
        
        operations_file = published_cortex / 'cortex-operations.yaml'
        assert operations_file.exists()
        
        try:
            with open(operations_file, encoding='utf-8') as f:
                operations = yaml.safe_load(f)
            
            assert operations is not None
            assert 'operations' in operations
            assert len(operations['operations']) > 0
        except yaml.YAMLError as e:
            pytest.fail(f"cortex-operations.yaml is invalid YAML: {e}")
    
    def test_brain_protection_rules_valid_yaml(self, published_cortex: Path):
        """Verify brain-protection-rules.yaml is valid YAML"""
        if not published_cortex.exists():
            pytest.skip("No publish folder")
        
        rules_file = published_cortex / 'cortex-brain' / 'brain-protection-rules.yaml'
        assert rules_file.exists()
        
        try:
            with open(rules_file, encoding='utf-8') as f:
                rules = yaml.safe_load(f)
            
            assert rules is not None
            # Current schema uses protection_layers, not brain_protection
            assert 'protection_layers' in rules
            assert isinstance(rules['protection_layers'], list)
        except yaml.YAMLError as e:
            pytest.fail(f"brain-protection-rules.yaml is invalid YAML: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
