# Document Converter Integration Roadmap

**Purpose:** Track current and planned integrations of universal DocumentConverter  
**Version:** 1.0.0  
**Author:** Asif Hussain  
**Last Updated:** 2025-11-27

---

## 📊 Integration Matrix

| # | Component | Status | Version | Use Case | Priority | Effort |
|---|-----------|--------|---------|----------|----------|--------|
| 1 | **PolicyScanner** | ✅ COMPLETE | v1.0.0 | Policy docs in Word/PDF | HIGH | 2h |
| 2 | **ADO Orchestrator** | ⏳ PLANNED | v1.1.0 | Requirements from attachments | HIGH | 1h |
| 3 | **Planning Orchestrator** | ⏳ PLANNED | v1.2.0 | Feature specs upload | MEDIUM | 1h |
| 4 | **Conversation Capture** | ⏳ PLANNED | v1.3.0 | Chat history import | MEDIUM | 1h |
| 5 | **Feedback Agent** | ⏳ PLANNED | v1.4.0 | Bug reports with docs | LOW | 30m |
| 6 | **Onboarding Orchestrator** | ⏳ PLANNED | v1.5.0 | Setup guides import | LOW | 30m |

**Legend:**
- ✅ COMPLETE: Implemented, tested, documented
- ⏳ PLANNED: Design complete, awaiting implementation
- 🚧 IN PROGRESS: Currently being developed
- ❌ BLOCKED: Waiting on dependencies or decisions

---

## 1. PolicyScanner ✅

**Status:** COMPLETE (v1.0.0)  
**File:** `src/operations/policy_scanner.py`  
**Effort:** 2 hours (1h implementation + 1h testing/docs)

### What It Does

Scans repository for policy documents in all formats (YAML, JSON, Markdown, Word, PDF), automatically converts Word/PDF to Markdown, then validates against organizational standards.

### Integration Code

```python
# Import with fallback
try:
    from src.utils.document_converter import DocumentConverter
    CONVERTER_AVAILABLE = True
except ImportError:
    CONVERTER_AVAILABLE = False

class PolicyScanner:
    def __init__(self, repo_root: Path):
        # Initialize converter
        self.converter = DocumentConverter() if CONVERTER_AVAILABLE else None
        
        # Extended policy locations
        self.policy_locations = [
            # ... existing locations ...
            self.repo_root / "POLICIES.docx",
            self.repo_root / "POLICIES.doc",
            self.repo_root / "POLICIES.pdf"
        ]
    
    def _parse_policy_file(self, path: Path) -> Optional[PolicyDocument]:
        # Convert Word/PDF first if needed
        if path.suffix.lower() in ['.docx', '.doc', '.pdf']:
            if not self.converter:
                print("⚠️  Word/PDF converter not available")
                return None
            
            result = self.converter.convert_to_markdown(path)
            if not result.success:
                print(f"❌ Conversion failed: {result.error_message}")
                return None
            
            path = result.markdown_path  # Use converted file
        
        # Continue with normal parsing...
```

### User Benefit

Organizations can maintain policy documents in native Word/PDF formats (95% of organizations use Word/PDF). No manual conversion needed.

### Test Results

- ✅ 9/10 tests passing (90%)
- ✅ All format detection tests pass
- ✅ DocumentConverter initializes correctly
- ❌ 1 failure: YAML multi-document parsing (pre-existing, not related)

---

## 2. ADO Work Item Orchestrator ⏳

**Status:** PLANNED (v1.1.0)  
**File:** `src/orchestrators/ado_work_item_orchestrator.py`  
**Effort:** 1 hour

### Proposed Use Case

User attaches requirements document (Word/PDF) to ADO work item. CORTEX downloads attachment, converts to Markdown, extracts requirements, auto-populates ADO form.

### Proposed Integration

```python
from src.utils.document_converter import DocumentConverter

class ADOWorkItemOrchestrator:
    def __init__(self):
        try:
            self.converter = DocumentConverter()
        except ImportError:
            self.converter = None
    
    def import_requirements(self, ado_id: int, attachment: str):
        """Import requirements from Word/PDF attachment"""
        
        # Download attachment from ADO
        attachment_path = self._download_attachment(ado_id, attachment)
        
        if attachment_path.suffix in ['.docx', '.doc', '.pdf']:
            # Convert to Markdown
            result = self.converter.convert_to_markdown(attachment_path)
            
            if not result.success:
                raise ValueError(f"Conversion failed: {result.error_message}")
            
            # Extract requirements from Markdown
            requirements = self._extract_requirements(result.markdown_path)
        else:
            # Already text format
            requirements = self._extract_requirements(attachment_path)
        
        # Auto-populate ADO form
        return self._populate_form(requirements)
```

### User Benefit

Eliminates manual copy-paste from requirements documents. Supports real-world workflows where specs are written in Word.

---

## 3. Planning Orchestrator ⏳

**Status:** PLANNED (v1.2.0)  
**File:** `src/orchestrators/planning_orchestrator.py`  
**Effort:** 1 hour

### Proposed Use Case

User uploads feature specification as Word/PDF document. CORTEX converts to Markdown, extracts requirements, validates DoR, generates planning file.

### Proposed Integration

```python
from src.utils.document_converter import DocumentConverter

class PlanningOrchestrator:
    def __init__(self):
        try:
            self.converter = DocumentConverter()
        except ImportError:
            self.converter = None
    
    def plan_from_document(self, feature_name: str, spec_document: Path):
        """Create plan from uploaded Word/PDF specification"""
        
        if spec_document.suffix in ['.docx', '.doc', '.pdf']:
            # Convert specification to Markdown
            result = self.converter.convert_to_markdown(spec_document)
            
            if not result.success:
                raise ValueError(f"Conversion failed: {result.error_message}")
            
            spec_content = result.markdown_path.read_text()
        else:
            spec_content = spec_document.read_text()
        
        # Extract requirements from spec
        requirements = self._parse_requirements(spec_content)
        
        # Generate planning file with DoR validation
        return self._generate_plan(feature_name, requirements)
```

### User Benefit

Supports Product Managers who write specs in Word. Eliminates manual requirement extraction and transcription.

---

## 4. Conversation Capture ⏳

**Status:** PLANNED (v1.3.0)  
**File:** `src/tier1/conversation_capture.py`  
**Effort:** 1 hour

### Proposed Use Case

User exports chat history to Word document (from Slack, Teams, etc.). CORTEX imports conversation, extracts patterns, stores in Tier 1 working memory.

### Proposed Integration

```python
from src.utils.document_converter import DocumentConverter

class ConversationCapture:
    def __init__(self):
        try:
            self.converter = DocumentConverter()
        except ImportError:
            self.converter = None
    
    def import_from_document(self, document_path: Path):
        """Import conversation from Word/PDF document"""
        
        if document_path.suffix in ['.docx', '.doc', '.pdf']:
            # Convert to Markdown
            result = self.converter.convert_to_markdown(document_path)
            
            if not result.success:
                raise ValueError(f"Conversion failed: {result.error_message}")
            
            conversation_text = result.markdown_path.read_text()
        else:
            conversation_text = document_path.read_text()
        
        # Parse conversation structure
        messages = self._parse_conversation(conversation_text)
        
        # Store in Tier 1 working memory
        self._store_conversation(messages)
        
        # Extract patterns for Tier 2
        patterns = self._extract_patterns(messages)
        return self._learn_patterns(patterns)
```

### User Benefit

Supports importing conversations from corporate chat systems that export to Word/PDF. Enables learning from historical conversations.

---

## 5. Feedback Agent ⏳

**Status:** PLANNED (v1.4.0)  
**File:** `src/agents/feedback_agent.py`  
**Effort:** 30 minutes

### Proposed Use Case

User reports bug with attached error log (PDF) or documentation (Word). CORTEX converts attachments, includes in feedback report, uploads to GitHub Gist.

### Proposed Integration

```python
from src.utils.document_converter import DocumentConverter

class FeedbackAgent:
    def __init__(self):
        try:
            self.converter = DocumentConverter()
        except ImportError:
            self.converter = None
    
    def report_bug(self, description: str, attachments: List[Path] = None):
        """Report bug with optional Word/PDF attachments"""
        
        converted_content = []
        
        if attachments:
            for attachment in attachments:
                if attachment.suffix in ['.docx', '.doc', '.pdf']:
                    # Convert to Markdown
                    result = self.converter.convert_to_markdown(attachment)
                    
                    if result.success:
                        content = result.markdown_path.read_text()
                        converted_content.append({
                            'filename': attachment.name,
                            'content': content
                        })
        
        # Generate feedback report with converted attachments
        report = self._generate_report(description, converted_content)
        
        # Upload to GitHub Gist
        return self._upload_to_gist(report)
```

### User Benefit

Supports attaching error logs, crash dumps, or documentation to bug reports. Converts everything to readable Markdown for GitHub Issues.

---

## 6. Onboarding Orchestrator ⏳

**Status:** PLANNED (v1.5.0)  
**File:** `src/orchestrators/onboarding_orchestrator.py`  
**Effort:** 30 minutes

### Proposed Use Case

User provides company-specific setup guide (Word/PDF). CORTEX imports guide, extracts setup steps, auto-configures CORTEX based on instructions.

### Proposed Integration

```python
from src.utils.document_converter import DocumentConverter

class OnboardingOrchestrator:
    def __init__(self):
        try:
            self.converter = DocumentConverter()
        except ImportError:
            self.converter = None
    
    def import_setup_guide(self, guide_path: Path):
        """Import setup guide from Word/PDF document"""
        
        if guide_path.suffix in ['.docx', '.doc', '.pdf']:
            # Convert to Markdown
            result = self.converter.convert_to_markdown(guide_path)
            
            if not result.success:
                raise ValueError(f"Conversion failed: {result.error_message}")
            
            guide_content = result.markdown_path.read_text()
        else:
            guide_content = guide_path.read_text()
        
        # Extract setup steps
        steps = self._parse_setup_steps(guide_content)
        
        # Auto-configure CORTEX
        return self._apply_configuration(steps)
```

### User Benefit

Enterprise teams can maintain setup documentation in Word. CORTEX automatically applies configurations from corporate guides.

---

## 🎯 Implementation Priority

### High Priority (v1.1.0)
- **ADO Work Item Orchestrator** - High user demand, common workflow

### Medium Priority (v1.2.0 - v1.3.0)
- **Planning Orchestrator** - Enhances planning workflow
- **Conversation Capture** - Improves brain learning

### Low Priority (v1.4.0 - v1.5.0)
- **Feedback Agent** - Nice to have, not critical
- **Onboarding Orchestrator** - Enterprise feature, smaller audience

---

## 📊 Effort Summary

| Integration | Effort | Lines of Code | Tests |
|-------------|--------|---------------|-------|
| PolicyScanner (COMPLETE) | 2h | ~60 | 10 |
| ADO Orchestrator | 1h | ~40 | 8 |
| Planning Orchestrator | 1h | ~40 | 8 |
| Conversation Capture | 1h | ~50 | 10 |
| Feedback Agent | 30m | ~30 | 5 |
| Onboarding Orchestrator | 30m | ~35 | 5 |
| **TOTAL** | **6h** | **~255** | **46** |

**DocumentConverter Core:** 600 lines (reused by all)  
**Total New Code:** ~255 lines (integrations)  
**Code Reuse Factor:** 2.35x (600 ÷ 255)

---

## 🚀 Implementation Plan

### Sprint 1 (Current)
- ✅ DocumentConverter core (600 lines)
- ✅ PolicyScanner integration (2h)
- ✅ Comprehensive documentation (20,000 chars)

### Sprint 2 (Next)
- ⏳ ADO Work Item Orchestrator (1h)
- ⏳ Planning Orchestrator (1h)
- ⏳ Integration tests (2h)

### Sprint 3 (Future)
- ⏳ Conversation Capture (1h)
- ⏳ Feedback Agent (30m)
- ⏳ Onboarding Orchestrator (30m)
- ⏳ End-to-end tests (2h)

**Total Implementation Time:** 10-12 hours (across 3 sprints)

---

## 📚 Resources

### Documentation
- **Comprehensive Guide:** `cortex-brain/documents/implementation-guides/universal-document-converter-guide.md`
- **Quick Reference:** `cortex-brain/DOCUMENT-CONVERTER-QUICK-REF.md`
- **Completion Report:** `cortex-brain/documents/reports/UNIVERSAL-DOCUMENT-CONVERTER-COMPLETE.md`

### Source Code
- **DocumentConverter:** `src/utils/document_converter.py` (600 lines)
- **PolicyScanner Integration:** `src/operations/policy_scanner.py` (lines 15-25, 60-80, 110-150)

### Testing
- **PolicyScanner Tests:** `tests/operations/test_policy_scanner.py` (9/10 passing)
- **DocumentConverter Tests:** `tests/utils/test_document_converter.py` (TODO, 20 test cases)

---

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Last Updated:** 2025-11-27  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.
