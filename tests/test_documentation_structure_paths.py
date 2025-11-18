from pathlib import Path


def test_admin_documentation_config_exists():
    root = Path(__file__).resolve().parents[1]
    admin_config = root / "cortex-brain" / "admin" / "documentation" / "config"
    assert admin_config.exists(), "admin/documentation/config directory should exist"

    # Required config files
    required = [
        "diagram-definitions.yaml",
        "master-diagram-list.yaml",
        "page-definitions.yaml",
        "source-mapping.yaml",
        "validation-rules.yaml",
    ]
    for name in required:
        assert (admin_config / name).exists(), f"Missing config file: {name} in admin/documentation/config"


def test_legacy_config_location_cleaned_up():
    """Verify legacy documentation config folder has been removed after migration."""
    root = Path(__file__).resolve().parents[1]
    legacy = root / "cortex-brain" / "doc-generation-config"
    
    # After migration to admin/documentation/config, legacy folder should not exist
    assert not legacy.exists(), "Legacy doc-generation-config folder should be removed after migration to admin/documentation/config"


def test_legacy_documentation_files_cleaned_up():
    """Verify legacy documentation generation files have been removed."""
    root = Path(__file__).resolve().parents[1]
    
    # These files were part of the old documentation generation workflow
    legacy_files = [
        "DOCUMENTATION-GENERATION-VALIDATION.md",
        "DOCUMENTATION-GENERATION-RESPONSE-TEMPLATES-UPDATE.md",
        "DOCUMENTATION-GENERATION-SUMMARY.txt"
    ]
    
    for filename in legacy_files:
        legacy_file = root / filename
        assert not legacy_file.exists(), f"Legacy documentation file {filename} should be removed after migration to component architecture"
