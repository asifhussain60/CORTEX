# Document Converter Quick Reference

**Universal Word/PDF → Markdown Converter for ALL CORTEX Components**

---

## ⚡ Quick Start

```python
from src.utils.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert_to_markdown(Path("document.docx"))

if result.success:
    print(f"✅ {result.markdown_path}")
else:
    print(f"❌ {result.error_message}")
```

---

## 📦 Installation

```bash
# Python dependencies (required)
pip install python-docx PyPDF2

# External tools (optional, better quality)
# pandoc: https://pandoc.org/installing.html
# pdftotext (poppler): brew install poppler (Mac)
```

---

## 🎯 Current Integrations

| Component | Status | Use Case |
|-----------|--------|----------|
| **PolicyScanner** | ✅ COMPLETE | Policy documents in Word/PDF |
| **ADO Orchestrator** | ⏳ PLANNED | Requirements from attachments |
| **Planning Orchestrator** | ⏳ PLANNED | Feature specs upload |
| **Conversation Capture** | ⏳ PLANNED | Chat history import |
| **Feedback Agent** | ⏳ PLANNED | Bug reports with docs |
| **Onboarding** | ⏳ PLANNED | Setup guides import |

---

## 🔧 Integration Pattern

```python
# 1. Import with fallback
try:
    from src.utils.document_converter import DocumentConverter
    CONVERTER_AVAILABLE = True
except ImportError:
    CONVERTER_AVAILABLE = False

# 2. Initialize once
converter = DocumentConverter() if CONVERTER_AVAILABLE else None

# 3. Check file type
needs_convert = file.suffix in ['.docx', '.doc', '.pdf']

# 4. Convert if needed
if needs_convert and converter:
    result = converter.convert_to_markdown(file)
    if result.success:
        content = result.markdown_path.read_text()
```

---

## 🏗️ Converter Priority

1. **pandoc** (best quality, external)
2. **pdftotext + python-docx** (good quality, mixed)
3. **PyPDF2** (basic quality, Python-only)

---

## 📊 Performance

| Scenario | Time | Cached |
|----------|------|--------|
| Small Word (5 pages) | 150-500ms | 3ms |
| Large Word (50 pages) | 800ms-1.5s | 3ms |
| Small PDF (5 pages) | 100-800ms | 3ms |
| Large PDF (50 pages) | 600ms-5s | 3ms |

**Cache:** MD5(filepath + mtime), auto-invalidates on file change

---

## ⚠️ Error Handling

```python
result = converter.convert_to_markdown(file)

if not result.success:
    if "not available" in result.error_message:
        # Show installation guide
        print(converter.get_installation_guide())
    elif "timeout" in result.error_message:
        # Handle 60s timeout
        print("Document too large or corrupted")
    else:
        # Generic error
        print(f"Conversion failed: {result.error_message}")
```

---

## 🎓 Best Practices

✅ **DO:**
- Import with try/except fallback
- Reuse converter instance (caching)
- Check CONVERTER_AVAILABLE before using
- Provide installation guidance on errors

❌ **DON'T:**
- Hard require converter (breaks without dependencies)
- Create new instance per conversion (loses cache)
- Assume all converters installed
- Silent failure on conversion errors

---

## 🐛 Common Issues

**"Converter not available"**
→ `pip install python-docx PyPDF2`

**Poor quality conversion**
→ Install pandoc (external tool)

**Conversion timeout (60s)**
→ Split large documents or use faster converter

**Cached version outdated**
→ Cache auto-invalidates on mtime change

---

## 📚 Full Guide

**Complete Documentation:** `cortex-brain/documents/implementation-guides/universal-document-converter-guide.md`

**Source Code:** `src/utils/document_converter.py` (600 lines)

**Integration Example:** `src/operations/policy_scanner.py`

---

**Author:** Asif Hussain | **Version:** 1.0.0 | **Updated:** 2025-11-27
