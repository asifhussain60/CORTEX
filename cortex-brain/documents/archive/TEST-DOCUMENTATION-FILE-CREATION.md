# Documentation File Creation - Test Execution Guide

**Quick Reference:** How to verify documentation generation actually creates files

---

## 🚀 Quick Test Commands

### Run All Tests
```bash
cd /Users/asifhussain/PROJECTS/CORTEX
python3 -m pytest tests/operations/test_documentation_file_creation.py -v -s
```

### Run Individual Tests

**1. Check Folders Exist**
```bash
python3 -m pytest tests/operations/test_documentation_file_creation.py::TestDocumentationFileCreation::test_folders_exist -v -s
```

**2. Check Folders Not Empty (Will FAIL - shows the bug)**
```bash
python3 -m pytest tests/operations/test_documentation_file_creation.py::TestDocumentationFileCreation::test_folders_not_empty -v -s
```

**3. Check Generated Folder (Will FAIL - critical test)**
```bash
python3 -m pytest tests/operations/test_documentation_file_creation.py::TestDocumentationFileCreation::test_generated_folder_has_content -v -s
```

**4. Check File Timestamps**
```bash
python3 -m pytest tests/operations/test_documentation_file_creation.py::TestDocumentationFileCreation::test_file_creation_timestamps -v -s
```

**5. Test Full Generation Pipeline**
```bash
python3 -m pytest tests/operations/test_documentation_file_creation.py::TestDocumentationFileCreation::test_enterprise_documentation_execution -v -s
```

**6. Test PageGenerator Directly**
```bash
python3 -m pytest tests/operations/test_documentation_file_creation.py::TestDocumentationFileCreation::test_page_generator_directly -v -s
```

---

## 📊 Expected Results (Current State)

| Test | Expected Result | Why |
|------|----------------|-----|
| test_folders_exist | ✅ PASS | Folders exist |
| test_folders_not_empty | ❌ FAIL | diagrams/ and generated/ are empty |
| test_generated_folder_has_content | ❌ FAIL | generated/ has 0 files |
| test_file_creation_timestamps | ✅ PASS | test-generated/ has files |
| test_enterprise_documentation_execution | ❌ FAIL | No files created |
| test_page_generator_directly | ⚠️ SKIP or FAIL | Templates missing |

---

## 🎯 Success Criteria (After Fix)

ALL tests should pass:
- ✅ Folders exist
- ✅ Folders have minimum files
- ✅ generated/ has ≥ 5 files
- ✅ Files recently modified
- ✅ Full generation creates files
- ✅ PageGenerator works directly

---

## 🔍 Quick Diagnosis Commands

### Check Empty Folders
```bash
# Check generated folder
ls -la docs/generated/
# Expected: Should have files after generation (currently empty)

# Check diagrams folder  
ls -la docs/diagrams/
# Expected: Should have .md files (currently only subdirectories)
```

### Check Templates Exist
```bash
ls -la cortex-brain/templates/doc-templates/
# Expected: Should have .j2 template files
```

### Check Page Definitions
```bash
cat cortex-brain/doc-generation-config/page-definitions.yaml
# Expected: Should define pages to generate
```

### Manual File Count
```bash
# Count files in each folder
for dir in docs/*/; do 
  echo "$dir: $(find "$dir" -maxdepth 1 -type f -name "*.md" | wc -l) files"
done
```

---

## 🔧 Integration with CI/CD

Add to your test pipeline:

```yaml
# .github/workflows/test-documentation.yml
name: Documentation Generation Tests

on: [push, pull_request]

jobs:
  test-doc-generation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run documentation file creation tests
        run: |
          python3 -m pytest tests/operations/test_documentation_file_creation.py -v -s
      - name: Upload test results
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: |
            docs/generated/
            docs/diagrams/
```

---

## 📋 Manual Verification Checklist

After running generation operation:

- [ ] Navigate to `docs/generated/`
- [ ] Count files: `ls -1 docs/generated/*.md | wc -l`
- [ ] Expected: ≥ 5 files
- [ ] Check file sizes: `ls -lh docs/generated/`
- [ ] Expected: Files > 0 bytes
- [ ] Check content: `head -20 docs/generated/[file].md`
- [ ] Expected: Valid markdown content

---

## 🆘 Troubleshooting

### Test Fails with "Module not found"

```bash
# Ensure you're in project root
cd /Users/asifhussain/PROJECTS/CORTEX

# Check Python path
python3 -c "import sys; print('\n'.join(sys.path))"

# Install test dependencies
pip3 install pytest pyyaml jinja2
```

### Test Passes but Folder Still Empty

This indicates the test needs updating or the generation is failing silently:
1. Run test 5 (full generation) with verbose output
2. Check logs for errors
3. Verify templates exist
4. Check page definitions are valid

### Cannot Write to docs/

Check permissions:
```bash
ls -ld docs/
# Should show write permissions (drwxr-xr-x)

# Fix if needed
chmod -R u+w docs/
```

---

## 📝 Adding New Tests

To add tests for additional folders:

```python
# In test_documentation_file_creation.py

@pytest.fixture
def expected_folders(self, docs_path):
    """Add new folder to check"""
    return {
        # ... existing folders ...
        "new-folder": docs_path / "new-folder",
    }

@pytest.fixture
def minimum_expected_files(self):
    """Set expected file count"""
    return {
        # ... existing counts ...
        "new-folder": 3,  # Expect at least 3 files
    }
```

---

## 🔗 Related Documentation

- **Bug Report:** `cortex-brain/documents/investigations/DOCUMENTATION-FILE-CREATION-BUG.md`
- **Test Source:** `tests/operations/test_documentation_file_creation.py`
- **PageGenerator:** `src/epm/modules/page_generator.py`
- **Operations Config:** `cortex-operations.yaml`

---

**Created:** November 17, 2025  
**Author:** Asif Hussain  
**Status:** Test suite ready for validation
