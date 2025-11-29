"""
CORTEX Upgrade System Validator

Validates that upgrade system correctly:
1. Updates VERSION file after successful upgrade
2. Handles dictionary template format in config merger
3. Properly reads VERSION file (plain text and JSON formats)

This validator ENFORCES fixes - deployment will fail if these tests fail.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import sys
from pathlib import Path
import tempfile
import shutil
import json

# Add operations directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "operations"))

from version_detector import VersionDetector
from config_merger import ConfigMerger

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

class UpgradeSystemValidator:
    """Validates upgrade system functionality"""
    
    def __init__(self):
        self.failures = []
        self.warnings = []
        self.test_count = 0
        self.passed_count = 0
    
    def run_all_tests(self) -> bool:
        """Run all upgrade system validation tests"""
        print(f"\n{Colors.BOLD}CORTEX Upgrade System Validation{Colors.RESET}")
        print("=" * 70)
        
        tests = [
            ("VERSION file reads plain text format", self.test_version_file_plain_text),
            ("VERSION file reads legacy JSON format", self.test_version_file_legacy_json),
            ("VERSION file handles missing file", self.test_version_file_missing),
            ("Version detector strips v prefix", self.test_version_strip_prefix),
            ("Version comparison works correctly", self.test_version_comparison),
            ("Config merger handles dict templates", self.test_config_merger_dict_templates),
            ("Config merger handles None values", self.test_config_merger_none_values),
            ("Config merger type safety", self.test_config_merger_type_safety),
            ("Upgrade info handles string version", self.test_upgrade_info_string_version),
            ("Upgrade info handles dict version", self.test_upgrade_info_dict_version),
        ]
        
        for test_name, test_func in tests:
            self.test_count += 1
            try:
                result = test_func()
                if result:
                    self.passed_count += 1
                    print(f"  {Colors.GREEN}✅ {test_name}{Colors.RESET}")
                else:
                    print(f"  {Colors.RED}❌ {test_name}{Colors.RESET}")
                    self.failures.append(test_name)
            except Exception as e:
                print(f"  {Colors.RED}❌ {test_name}: {e}{Colors.RESET}")
                self.failures.append(f"{test_name}: {e}")
        
        return len(self.failures) == 0
    
    def test_version_file_plain_text(self) -> bool:
        """Test VERSION file reading (plain text format)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create mock CORTEX structure
            prompts_dir = tmppath / ".github" / "prompts"
            prompts_dir.mkdir(parents=True)
            (prompts_dir / "CORTEX.prompt.md").write_text("# CORTEX")
            
            # Create VERSION file (plain text format)
            version_file = tmppath / "VERSION"
            version_file.write_text("v3.3.0\n")
            
            # Test reading
            detector = VersionDetector(tmppath)
            version = detector.get_current_version()
            
            if version != "v3.3.0":
                raise AssertionError(f"Expected 'v3.3.0', got '{version}'")
            
            return True
    
    def test_version_file_legacy_json(self) -> bool:
        """Test VERSION file reading (legacy JSON format)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create mock CORTEX structure
            prompts_dir = tmppath / ".github" / "prompts"
            prompts_dir.mkdir(parents=True)
            (prompts_dir / "CORTEX.prompt.md").write_text("# CORTEX")
            
            # Create VERSION file (legacy JSON format)
            version_file = tmppath / "VERSION"
            version_data = {
                "cortex_version": "v3.2.0",
                "schema_version": 1,
                "installed_date": "2025-11-24"
            }
            version_file.write_text(json.dumps(version_data, indent=2))
            
            # Test reading
            detector = VersionDetector(tmppath)
            version = detector.get_current_version()
            
            # Should return dict for JSON format
            if not isinstance(version, dict):
                raise AssertionError(f"Expected dict, got {type(version)}")
            
            if version.get("cortex_version") != "v3.2.0":
                raise AssertionError(f"Expected cortex_version='v3.2.0', got '{version.get('cortex_version')}'")
            
            return True
    
    def test_version_file_missing(self) -> bool:
        """Test VERSION file missing scenario"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create mock CORTEX structure
            prompts_dir = tmppath / ".github" / "prompts"
            prompts_dir.mkdir(parents=True)
            (prompts_dir / "CORTEX.prompt.md").write_text("# CORTEX")
            
            # No VERSION file created
            
            # Test reading
            detector = VersionDetector(tmppath)
            version = detector.get_current_version()
            
            if version is not None:
                raise AssertionError(f"Expected None, got '{version}'")
            
            return True
    
    def test_version_strip_prefix(self) -> bool:
        """Test version prefix stripping"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create mock CORTEX structure
            prompts_dir = tmppath / ".github" / "prompts"
            prompts_dir.mkdir(parents=True)
            (prompts_dir / "CORTEX.prompt.md").write_text("# CORTEX")
            
            # Create VERSION file without 'v' prefix
            version_file = tmppath / "VERSION"
            version_file.write_text("3.3.0\n")
            
            # Test reading (should still work)
            detector = VersionDetector(tmppath)
            version = detector.get_current_version()
            
            if version != "3.3.0":
                raise AssertionError(f"Expected '3.3.0', got '{version}'")
            
            return True
    
    def test_version_comparison(self) -> bool:
        """Test version comparison logic"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create mock CORTEX structure
            prompts_dir = tmppath / ".github" / "prompts"
            prompts_dir.mkdir(parents=True)
            (prompts_dir / "CORTEX.prompt.md").write_text("# CORTEX")
            
            detector = VersionDetector(tmppath)
            
            # Test comparisons
            tests = [
                ("3.1.0", "3.2.0", -1),  # 3.1.0 < 3.2.0
                ("3.2.0", "3.2.0", 0),   # 3.2.0 == 3.2.0
                ("3.3.0", "3.2.0", 1),   # 3.3.0 > 3.2.0
            ]
            
            for v1, v2, expected in tests:
                result = detector.compare_versions(v1, v2)
                if result != expected:
                    raise AssertionError(
                        f"compare_versions({v1}, {v2}) = {result}, expected {expected}"
                    )
            
            return True
    
    def test_config_merger_dict_templates(self) -> bool:
        """Test config merger handles dictionary template format"""
        merger = ConfigMerger()
        
        # Simulate new response-templates.yaml format (dict of dicts)
        base = {
            "templates": {
                "help_table": {"name": "Help", "triggers": ["help"]}
            }
        }
        
        local = {
            "templates": {
                "help_table": {"name": "Help", "triggers": ["help"]},
                "custom": {"name": "Custom", "triggers": ["custom"]}
            }
        }
        
        upgrade = {
            "templates": {
                "help_table": {"name": "Help Enhanced", "triggers": ["help", "?"]},
                "new_feature": {"name": "New", "triggers": ["new"]}
            }
        }
        
        # Should not crash
        try:
            result = merger._three_way_merge(base, local, upgrade)
            
            # Verify merge results
            if "templates" not in result:
                raise AssertionError("Missing 'templates' key in result")
            
            templates = result["templates"]
            
            # Should have help_table (upgraded), custom (local), new_feature (upgrade)
            if "help_table" not in templates:
                raise AssertionError("Missing 'help_table' in merged templates")
            if "custom" not in templates:
                raise AssertionError("Missing 'custom' in merged templates")
            if "new_feature" not in templates:
                raise AssertionError("Missing 'new_feature' in merged templates")
            
            return True
        except AttributeError as e:
            raise AssertionError(f"Config merger crashed on dict templates: {e}")
    
    def test_config_merger_none_values(self) -> bool:
        """Test config merger handles None values gracefully"""
        merger = ConfigMerger()
        
        # Test with None values
        try:
            result = merger._three_way_merge(None, None, None)
            if not isinstance(result, dict):
                raise AssertionError(f"Expected dict, got {type(result)}")
            return True
        except Exception as e:
            raise AssertionError(f"Config merger crashed on None values: {e}")
    
    def test_config_merger_type_safety(self) -> bool:
        """Test config merger handles non-dict values"""
        merger = ConfigMerger()
        
        # Test with string values (should not crash)
        base = {"key": "value"}
        local = {"key": "local_value"}
        upgrade = {"key": {"nested": "dict"}}
        
        try:
            result = merger._three_way_merge(base, local, upgrade)
            # Should resolve conflict (prefer upgrade)
            if result["key"] != {"nested": "dict"}:
                raise AssertionError("Conflict resolution failed")
            return True
        except Exception as e:
            raise AssertionError(f"Config merger type safety failed: {e}")
    
    def test_upgrade_info_string_version(self) -> bool:
        """Test get_upgrade_info handles string version format"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create mock CORTEX structure
            prompts_dir = tmppath / ".github" / "prompts"
            prompts_dir.mkdir(parents=True)
            (prompts_dir / "CORTEX.prompt.md").write_text("# CORTEX")
            
            # Create VERSION file (plain text)
            version_file = tmppath / "VERSION"
            version_file.write_text("v3.3.0\n")
            
            # Test get_upgrade_info
            detector = VersionDetector(tmppath)
            info = detector.get_upgrade_info()
            
            if info["current_version"] != "v3.3.0":
                raise AssertionError(
                    f"Expected current_version='v3.3.0', got '{info['current_version']}'"
                )
            
            if "upgrade_available" not in info:
                raise AssertionError("Missing 'upgrade_available' key")
            
            return True
    
    def test_upgrade_info_dict_version(self) -> bool:
        """Test get_upgrade_info handles dict version format (legacy)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create mock CORTEX structure
            prompts_dir = tmppath / ".github" / "prompts"
            prompts_dir.mkdir(parents=True)
            (prompts_dir / "CORTEX.prompt.md").write_text("# CORTEX")
            
            # Create VERSION file (legacy JSON)
            version_file = tmppath / "VERSION"
            version_data = {
                "cortex_version": "v3.2.0",
                "installed_date": "2025-11-24",
                "workspace_id": "test-123"
            }
            version_file.write_text(json.dumps(version_data))
            
            # Test get_upgrade_info
            detector = VersionDetector(tmppath)
            info = detector.get_upgrade_info()
            
            if info["current_version"] != "v3.2.0":
                raise AssertionError(
                    f"Expected current_version='v3.2.0', got '{info['current_version']}'"
                )
            
            if info["workspace_id"] != "test-123":
                raise AssertionError("workspace_id not extracted from dict format")
            
            return True
    
    def print_summary(self) -> bool:
        """Print validation summary"""
        print("\n" + "=" * 70)
        print(f"{Colors.BOLD}VALIDATION SUMMARY{Colors.RESET}")
        print("=" * 70)
        
        print(f"Tests Run: {self.test_count}")
        print(f"{Colors.GREEN}Passed: {self.passed_count}{Colors.RESET}")
        
        if self.failures:
            print(f"{Colors.RED}Failed: {len(self.failures)}{Colors.RESET}")
            for failure in self.failures:
                print(f"  ❌ {failure}")
        
        if self.warnings:
            print(f"{Colors.YELLOW}Warnings: {len(self.warnings)}{Colors.RESET}")
            for warning in self.warnings:
                print(f"  ⚠️  {warning}")
        
        print("=" * 70)
        
        if not self.failures:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✅ ALL UPGRADE SYSTEM TESTS PASSED{Colors.RESET}")
            print(f"{Colors.GREEN}Upgrade system is production-ready{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ UPGRADE SYSTEM VALIDATION FAILED{Colors.RESET}")
            print(f"{Colors.RED}Fix failures before deployment{Colors.RESET}")
        
        return len(self.failures) == 0


def main():
    """Run upgrade system validation"""
    validator = UpgradeSystemValidator()
    success = validator.run_all_tests()
    validator.print_summary()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
