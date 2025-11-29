"""
Tests for SKULL-006: Privacy Protection

Ensures publish script NEVER includes files with:
- Machine-specific paths (C:\\, D:\\, /home/, AHHOME)
- Coverage reports with machine names
- Log files with absolute paths
- Health reports with diagnostic data
- Development artifacts

Author: CORTEX SKULL Protection Layer
Created: 2025-11-12
"""

import pytest
import re
from pathlib import Path
from typing import List, Tuple, Set


class TestPublishPrivacy:
    """SKULL-006: Privacy Protection Tests"""
    
    @pytest.fixture
    def publish_cortex_path(self) -> Path:
        """Get path to publish/CORTEX folder"""
        repo_root = Path(__file__).parent.parent.parent
        return repo_root / 'publish' / 'CORTEX'
    
    @pytest.fixture
    def privacy_patterns(self) -> List[re.Pattern]:
        """Patterns that indicate privacy leaks.
        
        Note: Generic replacement paths like '/Users/username' or '/home/user' 
        are acceptable - these are our sanitized values.
        """
        return [
            re.compile(r'AHHOME'),
            re.compile(r'C:\\\\'),
            re.compile(r'D:\\\\'),
            re.compile(r'/home/asif'),  # Only specific username
            re.compile(r'/Users/asifhussain'),  # Only specific username
            re.compile(r'\\\\\\?\\\\C:'),  # Windows long path format
        ]
    
    @pytest.fixture
    def excluded_file_patterns(self) -> Set[str]:
        """File patterns that should NEVER be published"""
        return {
            '.coverage.*',
            '*.log',
            'health-report-*.json',
        }
    
    def test_no_coverage_files_published(self, publish_cortex_path: Path):
        """
        SKULL-006: Verify no .coverage.* files in publish package
        
        Coverage files contain machine names like .coverage.AHHOME.12345
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        coverage_files = list(publish_cortex_path.rglob('.coverage.*'))
        
        assert len(coverage_files) == 0, (
            f"SKULL-006 VIOLATION: Found {len(coverage_files)} coverage files in publish:\n" +
            "\n".join(f"  - {f.relative_to(publish_cortex_path)}" for f in coverage_files[:10])
        )
    
    def test_no_log_files_published(self, publish_cortex_path: Path):
        """
        SKULL-006: Verify no .log files in publish package
        
        Log files contain absolute paths and machine-specific data
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        log_files = list(publish_cortex_path.rglob('*.log'))
        
        assert len(log_files) == 0, (
            f"SKULL-006 VIOLATION: Found {len(log_files)} log files in publish:\n" +
            "\n".join(f"  - {f.relative_to(publish_cortex_path)}" for f in log_files[:10])
        )
    
    def test_no_health_reports_published(self, publish_cortex_path: Path):
        """
        SKULL-006: Verify no health-reports/ folder in publish package
        
        Health reports contain diagnostic data for development only
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        health_reports_dir = publish_cortex_path / 'cortex-brain' / 'health-reports'
        
        assert not health_reports_dir.exists(), (
            f"SKULL-006 VIOLATION: health-reports/ directory found in publish package"
        )
    
    def test_no_logs_folder_published(self, publish_cortex_path: Path):
        """
        SKULL-006: Verify no logs/ folder in publish package
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        logs_dir = publish_cortex_path / 'logs'
        
        assert not logs_dir.exists(), (
            f"SKULL-006 VIOLATION: logs/ directory found in publish package"
        )
    
    def test_no_pycache_published(self, publish_cortex_path: Path):
        """
        SKULL-006: Verify no __pycache__ folders in publish package
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        pycache_dirs = list(publish_cortex_path.rglob('__pycache__'))
        
        assert len(pycache_dirs) == 0, (
            f"SKULL-006 VIOLATION: Found {len(pycache_dirs)} __pycache__ directories:\n" +
            "\n".join(f"  - {d.relative_to(publish_cortex_path)}" for d in pycache_dirs[:10])
        )
    
    def test_config_uses_template_not_real_paths(self, publish_cortex_path: Path):
        """
        SKULL-006: Verify cortex.config.template.json is used (not cortex.config.json)
        
        The publish package should use the template file with placeholders,
        not the developer's actual config with machine names.
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        # cortex.config.json should NOT be in publish (contains AHHOME)
        config_file = publish_cortex_path / 'cortex.config.json'
        assert not config_file.exists(), (
            "SKULL-006 VIOLATION: cortex.config.json (with machine paths) found in publish. "
            "Should use cortex.config.template.json instead."
        )
        
        # cortex.config.template.json SHOULD be present
        template_file = publish_cortex_path / 'cortex.config.template.json'
        assert template_file.exists(), (
            "SKULL-006 VIOLATION: cortex.config.template.json not found in publish package"
        )
    
    def scan_file_for_privacy_leaks(
        self,
        file_path: Path,
        privacy_patterns: List[re.Pattern]
    ) -> List[Tuple[str, str]]:
        """
        Scan a file for privacy-leaking patterns
        
        Returns:
            List of (pattern_name, matched_text) tuples
        """
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Skip files that are clearly documentation/examples (not actual leaks)
            if any(indicator in content.lower() for indicator in [
                'example:',
                'for example',
                '# examples',
                'sample configuration',
                'placeholder'
            ]):
                # More lenient checking for documentation
                # Only flag if we see ACTUAL machine-specific names, not generic patterns
                if 'AHHOME' in content or '/Users/asifhussain' in content:
                    for pattern in privacy_patterns:
                        if pattern.pattern in ['AHHOME', r'/Users/asifhussain']:
                            matches = pattern.findall(content)
                            if matches:
                                violations.append((pattern.pattern, ', '.join(set(matches[:3]))))
                return violations
            
            # Strict checking for non-documentation files
            for pattern in privacy_patterns:
                matches = pattern.findall(content)
                if matches:
                    # Filter out false positives
                    real_matches = []
                    for match in matches:
                        # Skip generic Windows drive letters in code (e.g., "for drive in ['C:\\', 'D:\\']")
                        if match in ['C:\\\\', 'D:\\\\'] and ("for drive in" in content or "'C:\\\\'," in content):
                            continue
                        # Skip example paths like /home/user
                        if match == '/home/user':
                            continue
                        real_matches.append(match)
                    
                    if real_matches:
                        violations.append((pattern.pattern, ', '.join(set(real_matches[:3]))))
        
        except Exception:
            pass  # Skip files that can't be read
        
        return violations
    
    def test_no_absolute_paths_in_text_files(
        self,
        publish_cortex_path: Path,
        privacy_patterns: List[re.Pattern]
    ):
        """
        SKULL-006: Scan all text files for machine-specific absolute paths
        
        Checks .py, .md, .json, .yaml files for privacy leaks
        
        Excludes documentation files that legitimately contain examples:
        - brain-protection-rules.yaml (contains SKULL-006 example)
        - setup-guide.md (contains example paths)
        - Governance/rule files that document violations
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        text_extensions = {'.py', '.md', '.json', '.yaml', '.yml', '.txt'}
        violations_found = []
        
        # Files that legitimately contain example paths (documentation/governance)
        allowed_example_files = {
            'brain-protection-rules.yaml',  # Contains SKULL-006 example with AHHOME
            'publish-config.yaml',  # Contains forbidden pattern examples (documentation)
            'self-review-checklist.yaml',   # Contains verification examples
            'setup-guide.md',  # Installation guide with example paths like /Users/you and D:\\
            'technical-reference.md',  # May contain example configurations
            'configuration-reference.md',  # May contain example configs
            'tracking-guide.md',  # May contain example tracking paths
        }
        
        for file_path in publish_cortex_path.rglob('*'):
            if not file_path.is_file():
                continue
            
            if file_path.suffix not in text_extensions:
                continue
            
            # Skip allowed documentation/governance files
            if file_path.name in allowed_example_files:
                continue
            
            # Skip large files (>1MB)
            if file_path.stat().st_size > 1_000_000:
                continue
            
            violations = self.scan_file_for_privacy_leaks(file_path, privacy_patterns)
            
            if violations:
                rel_path = file_path.relative_to(publish_cortex_path)
                violations_found.append((rel_path, violations))
        
        if violations_found:
            error_msg = "SKULL-006 VIOLATION: Privacy leaks detected in published files:\n\n"
            
            for file_path, violations in violations_found[:10]:  # Show first 10
                error_msg += f"📁 {file_path}\n"
                for pattern, matches in violations:
                    error_msg += f"   🔍 Pattern '{pattern}': {matches}\n"
                error_msg += "\n"
            
            if len(violations_found) > 10:
                error_msg += f"... and {len(violations_found) - 10} more files\n"
            
            pytest.fail(error_msg)
    
    def test_exclude_patterns_comprehensive(self):
        """
        SKULL-006: Verify publish script has comprehensive exclusion patterns
        """
        from scripts.publish_cortex import EXCLUDE_PATTERNS
        
        required_exclusions = {
            '**/.coverage.*',
            '**/logs/**',
            '**/*.log',
            '**/health-reports/**',
            '**/__pycache__/**',
        }
        
        missing = required_exclusions - EXCLUDE_PATTERNS
        
        assert len(missing) == 0, (
            f"SKULL-006 VIOLATION: publish script missing exclusion patterns:\n" +
            "\n".join(f"  - {pattern}" for pattern in missing)
        )
    
    def test_publish_script_imports_correctly(self):
        """Verify publish script can be imported for testing"""
        try:
            from scripts import publish_cortex
            assert hasattr(publish_cortex, 'EXCLUDE_PATTERNS')
        except ImportError as e:
            pytest.fail(f"Cannot import publish script: {e}")
    
    def test_no_admin_documentation_published(self, publish_cortex_path: Path):
        """
        SKULL-006 (CORTEX 3.0): Verify no admin documentation in publish package
        
        Admin content that should be excluded:
        - docs/images/system-design-prompts/ → Image generation prompts
        - docs/images/system-design-prompts/narrative/ → PR narratives
        - docs/architecture/ → Architecture diagrams
        - docs/development/ → Development guides
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        # Check for entire docs/ folder (should not exist)
        docs_dir = publish_cortex_path / 'docs'
        
        assert not docs_dir.exists(), (
            "SKULL-006 VIOLATION: docs/ directory found in publish package. "
            "This contains admin-only content (image prompts, narratives, architecture docs)."
        )
    
    def test_no_image_prompt_narratives_published(self, publish_cortex_path: Path):
        """
        SKULL-006 (CORTEX 3.0): Verify no image prompt narratives in publish
        
        Specifically checks for:
        - docs/images/system-design-prompts/narrative/*.md
        - Any files matching *-narrative.md pattern
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        # Search for narrative files
        narrative_files = list(publish_cortex_path.rglob('*-narrative.md'))
        
        assert len(narrative_files) == 0, (
            f"SKULL-006 VIOLATION: Found {len(narrative_files)} narrative files in publish:\n" +
            "\n".join(f"  - {f.relative_to(publish_cortex_path)}" for f in narrative_files)
        )
    
    def test_no_design_documents_published(self, publish_cortex_path: Path):
        """
        SKULL-006 (CORTEX 3.0): Verify no design documents in publish
        
        Checks for:
        - cortex-brain/cortex-2.0-design/
        - cortex-brain/cortex-3.0-design/
        - Any PHASE-*.md, SESSION-*.md files
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        # Check for design directories
        design_dirs = [
            publish_cortex_path / 'cortex-brain' / 'cortex-2.0-design',
            publish_cortex_path / 'cortex-brain' / 'cortex-3.0-design',
        ]
        
        found_dirs = [d for d in design_dirs if d.exists()]
        
        assert len(found_dirs) == 0, (
            f"SKULL-006 VIOLATION: Found {len(found_dirs)} design directories in publish:\n" +
            "\n".join(f"  - {d.relative_to(publish_cortex_path)}" for d in found_dirs)
        )
        
        # Check for development documentation patterns
        # Note: session-loader.md is a legitimate user doc (not a dev session log)
        dev_doc_patterns = ['PHASE-*.md', 'SESSION-[0-9]*.md', 'COVERAGE-*.md', 'CLEANUP-*.md']
        found_dev_docs = []
        
        for pattern in dev_doc_patterns:
            matches = list(publish_cortex_path.rglob(pattern))
            found_dev_docs.extend(matches)
        
        assert len(found_dev_docs) == 0, (
            f"SKULL-006 VIOLATION: Found {len(found_dev_docs)} development docs in publish:\n" +
            "\n".join(f"  - {f.relative_to(publish_cortex_path)}" for f in found_dev_docs[:10])
        )
    
    def test_publish_config_yaml_exists(self, publish_cortex_path: Path):
        """
        SKULL-006 (CORTEX 3.0): Verify publish-config.yaml exists and is valid
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        config_file = publish_cortex_path / 'cortex-brain' / 'publish-config.yaml'
        
        assert config_file.exists(), (
            "SKULL-006 VIOLATION: publish-config.yaml not found in publish package. "
            "This file defines admin/user tier separation."
        )
        
        # Verify it's valid YAML
        import yaml
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            # Check for required keys
            required_keys = ['version', 'deployment_tiers', 'admin_content_patterns', 'user_content_patterns']
            missing_keys = [key for key in required_keys if key not in config_data]
            
            assert len(missing_keys) == 0, (
                f"SKULL-006 VIOLATION: publish-config.yaml missing required keys: {missing_keys}"
            )
        
        except yaml.YAMLError as e:
            pytest.fail(f"SKULL-006 VIOLATION: publish-config.yaml is invalid YAML: {e}")
    
    def test_no_admin_operations_published(self, publish_cortex_path: Path):
        """
        SKULL-006 (CORTEX 3.0): Verify no admin operation modules in publish
        
        Admin operations that should be excluded:
        - design_sync
        - interactive_planning (if implemented)
        - system_refactor
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        admin_operation_files = [
            'design_sync.py',
            'design_sync_orchestrator.py',
            'system_refactor_plugin.py',
            'interactive_planning.py',
        ]
        
        found_admin_ops = []
        for admin_file in admin_operation_files:
            matches = list(publish_cortex_path.rglob(admin_file))
            found_admin_ops.extend(matches)
        
        assert len(found_admin_ops) == 0, (
            f"SKULL-006 VIOLATION: Found {len(found_admin_ops)} admin operation files in publish:\n" +
            "\n".join(f"  - {f.relative_to(publish_cortex_path)}" for f in found_admin_ops)
        )
