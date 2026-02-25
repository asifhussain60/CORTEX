# Logo Dimension Tests

Automated testing suite for CORTEX logo assets and dimensions.

## Overview

These tests ensure that the CORTEX logo (`cortex-logo-200.png`) is:
- ✅ Present in the documentation assets
- ✅ A valid PNG image
- ✅ Exactly 128x128 pixels (working version per git commit 12aba98b9)
- ✅ Properly optimized (<100KB file size)
- ✅ Integrated with mkdocs configuration
- ✅ Properly styled in CSS (100x100px display via glassmorphism.css)

## Test Suite Structure

### `test_logo_dimensions.py`

Core test suite with two main classes:

#### TestLogoDimensions
- `test_cortex_logo_200_exists()` - Verifies file exists
- `test_cortex_logo_200_is_valid_image()` - Validates PNG format
- `test_cortex_logo_200_dimensions_128x128()` - Checks exact dimensions
- `test_cortex_logo_200_file_size_reasonable()` - Validates file size
- `test_logo_variants_dimensions()` - Tests 64x64, 128x128, 512x512 variants
- `test_cortex_logo_svg_exists()` - Validates light mode SVG
- `test_cortex_logo_white_svg_exists()` - Validates dark mode SVG
- `test_cortex_logo_svg_is_valid_xml()` - Validates SVG format
- `test_cortex_logo_white_svg_is_valid_xml()` - Validates dark SVG format
- `test_svg_logos_file_size_optimized()` - Checks SVG optimization

#### TestLogoIntegration
- `test_logo_used_in_mkdocs_config()` - Verifies mkdocs.yml references
- `test_logo_css_styling_configured()` - Checks CSS configuration

#### TestLogoAccessibility
- `test_primary_logo_has_alt_text_references()` - Documents alt text requirements
- `test_logo_is_not_sole_navigation_indicator()` - WCAG 2.1 AA compliance

### `conftest.py`

Pytest configuration and fixtures:
- Session-scoped fixtures for docs/project roots
- Auto-logging of all logo tests
- Pre-test logo asset validation

### `pytest.ini`

Pytest configuration:
- Test discovery patterns
- Custom markers (logo, assets, integration, mkdocs)
- Output formatting
- Timeout settings (30s default)

### `mkdocs_build_hook.py`

Build integration script:
- Runs logo tests as part of mkdocs build
- Provides colored output with status indicators
- Returns appropriate exit codes for CI/CD

## Quick Start

### Run All Logo Tests

```bash
cd docs/_tests
pytest test_logo_dimensions.py -v
```

### Run Specific Test Class

```bash
pytest test_logo_dimensions.py::TestLogoDimensions -v
pytest test_logo_dimensions.py::TestLogoIntegration -v
```

### Run Only Logo Marker Tests

```bash
pytest -m logo -v
```

### Run with mkdocs Integration Flag

```bash
pytest --mkdocs-build -v
```

### Run as Part of mkdocs Build

```bash
python mkdocs_build_hook.py
```

## Integration with mkdocs Build

### Option 1: Pre-build Hook (Recommended)

Add to `mkdocs.yml`:

```yaml
plugins:
  - search
  
# Run logo tests before build
hooks:
  - !include_relative _tests/mkdocs_build_hook.py
```

### Option 2: Manual Pre-build

```bash
# Test logos first
python docs/_tests/mkdocs_build_hook.py

# Then build
mkdocs build
```

### Option 3: CI/CD Integration

In your CI/CD pipeline (GitHub Actions, etc.):

```yaml
- name: Validate Logo Assets
  run: |
    cd docs/_tests
    pytest test_logo_dimensions.py::TestLogoDimensions -m logo --mkdocs-build
```

## Test Markers

Mark and filter tests using pytest markers:

```bash
# Run only logo tests
pytest -m logo

# Run only asset tests
pytest -m assets

# Run only integration tests
pytest -m integration

# Run only mkdocs-related tests
pytest -m mkdocs

# Exclude slow tests
pytest -m "not slow"
```

## Requirements

### Python Packages

```bash
pip install pytest pillow
```

### File Structure

```
docs/
├── _tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── pytest.ini
│   ├── test_logo_dimensions.py
│   ├── mkdocs_build_hook.py
│   └── README.md (this file)
├── assets/
│   └── images/
│       ├── cortex-logo-200.png (128x128 - PRIMARY)
│       ├── cortex-logo-64.png
│       ├── cortex-logo-128.png
│       ├── cortex-logo-512.png
│       ├── cortex-logo.svg (light)
│       └── cortex-logo-white.svg (dark)
├── stylesheets/
│   └── cortex-glassmorphism.css (contains .md-logo styling)
└── mkdocs.yml (references cortex-logo)
```

## Logo Specifications

### Primary Asset: cortex-logo-200.png
- **Dimensions**: 128×128 pixels
- **Format**: PNG (lossless)
- **File Size**: ~22KB
- **Usage**: Main documentation logo, headers
- **CSS Display Size**: 100×100px (via cortex-glassmorphism.css)
- **DPI Consideration**: 128px image at 100px display = 2x DPI for crisp rendering

### SVG Variants
- **cortex-logo.svg**: Light mode (2.5KB)
- **cortex-logo-white.svg**: Dark mode (2.6KB)
- **Format**: SVG (scalable vector)
- **Features**: Dark mode auto-detection, hover effects

### Additional PNG Variants
- **cortex-logo-64.png**: 64×64 - Favicons, thumbnails
- **cortex-logo-128.png**: 128×128 - Standard display
- **cortex-logo-512.png**: 512×512 - High-resolution, print

## Git History References

### Working Version
- **Commit**: `12aba98b9`
- **Message**: "Increase logo size to 100x100px"
- **Content**: CSS styling changes (32px → 100px)
- **Note**: Actual image is 128px, CSS display is 100px for 2x DPI

### Logo Integration
- **Commit**: `30254ac07`
- **Message**: "DO-001-01: Logo Integration in Header - Complete"
- **Features**: SVG variants, dark mode support, accessibility

## Test Execution Reports

Tests generate logs in `pytest-docs.log`:

```
=== test session starts ===
docs/_tests/test_logo_dimensions.py::TestLogoDimensions::test_cortex_logo_200_exists PASSED
docs/_tests/test_logo_dimensions.py::TestLogoDimensions::test_cortex_logo_200_dimensions_128x128 PASSED
...
=== 15 passed in 0.42s ===
```

## Troubleshooting

### Test Fails: "cortex-logo-200.png not found"

**Issue**: Logo file doesn't exist at expected path

**Solution**:
```bash
ls -la docs/assets/images/cortex-logo-200.png
# Should exist: docs/assets/images/cortex-logo-200.png
```

### Test Fails: "Image dimensions are 128x64, expected 128x128"

**Issue**: Logo was overwritten with wrong version

**Solution**:
```bash
# Restore from git
git checkout HEAD -- docs/assets/images/cortex-logo-200.png

# Or verify commit 12aba98b9 had correct version
git show 12aba98b9:docs/assets/images/cortex-logo-200.png > \
  docs/assets/images/cortex-logo-200.png
```

### Test Fails: "PIL not installed"

**Issue**: Pillow library not available

**Solution**:
```bash
pip install pillow
```

### mkdocs_build_hook.py: "pytest not found"

**Issue**: pytest not installed or not in PATH

**Solution**:
```bash
pip install pytest
```

## CI/CD Integration Examples

### GitHub Actions

```yaml
name: Validate Documentation

on: [push, pull_request]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      
      - name: Install Dependencies
        run: pip install pytest pillow mkdocs mkdocs-material
      
      - name: Validate Logo Assets
        run: python docs/_tests/mkdocs_build_hook.py
      
      - name: Run All Documentation Tests
        run: pytest docs/_tests -v
      
      - name: Build Documentation
        run: mkdocs build
```

### GitLab CI

```yaml
test_logo_assets:
  image: python:3.10
  script:
    - pip install pytest pillow mkdocs mkdocs-material
    - python docs/_tests/mkdocs_build_hook.py
    - pytest docs/_tests -v
  artifacts:
    paths:
      - docs/_tests/pytest-docs.log
    reports:
      junit: docs/_tests/pytest-docs.log
```

## Maintenance

### Adding New Tests

1. Add test method to appropriate TestClass in `test_logo_dimensions.py`
2. Use descriptive names: `test_<asset>_<validation>()`
3. Include docstrings explaining what's tested and why
4. Mark with appropriate pytest markers

### Updating Logo

When logo changes:

1. Update image file(s) in `docs/assets/images/`
2. Verify dimensions match test expectations
3. Run logo tests: `pytest -m logo -v`
4. Commit with message: "docs: update cortex-logo-*.png to <dimensions>x<dimensions>px"

### Debugging Tests

Enable debug logging:

```bash
pytest -v --log-cli-level=DEBUG test_logo_dimensions.py
```

## License

Tests are part of the CORTEX documentation system.
See docs/LICENSE.md for licensing information.

---

**Last Updated**: January 22, 2026  
**Test Coverage**: 15 assertions across logo assets, dimensions, formats, and integration  
**Required Packages**: pytest, pillow
