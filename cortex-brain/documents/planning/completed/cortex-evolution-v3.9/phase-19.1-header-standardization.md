# Phase 19.1: CORTEX Header Standardization

**🔗 Breadcrumb:** [← Back to Master Plan](cortex-3.9-master.md)

**Status:** ⏳ Pending  
**Phase ID:** 19.1  
**Estimated Time:** 1 hour (60 minutes)  
**Actual Start:** -  
**Actual End:** -  
**Actual Work Time:** -  
**Dependencies:** Phase 03 (Planning Orchestrator 3.0) ✅  
**Blocks:** None (Enhancement phase)

---

## 🎯 Phase Objective

Implement standardized CORTEX branding header across all planning documents, reports, and generated markdown files. Replace individual author attribution with unified CORTEX identity while maintaining copyright transparency.

**Success Criteria:**
- ✅ Standardized header template created
- ✅ Planning Orchestrator 3.0 auto-injects header
- ✅ ADO Orchestrator 3.0 auto-injects header
- ✅ All cortex-3.9 documents updated
- ✅ Header configuration in cortex.config.json

---

## 🎨 Standardized Header Design

### Template Structure

```markdown
<!--
████████████████████████████████████████████████████████████████████████████████
█                                                                              █
█   ██████╗ ██████╗ ██████╗ ████████╗███████╗██╗  ██╗                        █
█  ██╔════╝██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝╚██╗██╔╝                        █
█  ██║     ██║   ██║██████╔╝   ██║   █████╗   ╚███╔╝                         █
█  ██║     ██║   ██║██╔══██╗   ██║   ██╔══╝   ██╔██╗                         █
█  ╚██████╗╚██████╔╝██║  ██║   ██║   ███████╗██╔╝ ██╗                        █
█   ╚═════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝                        █
█                                                                              █
█  AI-Powered Development Intelligence System                                 █
█  Author: Asif Hussain | GitHub: github.com/asifhussain60/CORTEX            █
█  Copyright © 2025 Asif Hussain. All rights reserved.                       █
█                                                                              █
████████████████████████████████████████████████████████████████████████████████
-->

# {Document Title}

**Type:** {Document Type}  
**Status:** {Status}  
**Created:** {Date}  
**Version:** {Version}
```

### Usage Examples

**Master Plan:**
```markdown
<!--
████████████████████████████████████████████████████████████████████████████████
█                                                                              █
█   ██████╗ ██████╗ ██████╗ ████████╗███████╗██╗  ██╗                        █
█  ██╔════╝██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝╚██╗██╔╝                        █
█  ██║     ██║   ██║██████╔╝   ██║   █████╗   ╚███╔╝                         █
█  ██║     ██║   ██║██╔══██╗   ██║   ██╔══╝   ██╔██╗                         █
█  ╚██████╗╚██████╔╝██║  ██║   ██║   ███████╗██╔╝ ██╗                        █
█   ╚═════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝                        █
█                                                                              █
█  AI-Powered Development Intelligence System                                 █
█  Author: Asif Hussain | GitHub: github.com/asifhussain60/CORTEX            █
█  Copyright © 2025 Asif Hussain. All rights reserved.                       █
█                                                                              █
████████████████████████████████████████████████████████████████████████████████
-->

# CORTEX Evolution v3.9 - Unified Orchestration & AST Enhancement

**Plan Name:** CORTEX Evolution v3.9 - Orchestration Intelligence & AST Integration  
**Type:** Tier 4 Complex Plan  
**Status:** 🟡 In Progress  
**Created:** 2024-12-14 05:30 AM  
**Version:** 3.9.0
```

**Sub-Plan:**
```markdown
<!--
████████████████████████████████████████████████████████████████████████████████
█                                                                              █
█   ██████╗ ██████╗ ██████╗ ████████╗███████╗██╗  ██╗                        █
█  ██╔════╝██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝╚██╗██╔╝                        █
█  ██║     ██║   ██║██████╔╝   ██║   █████╗   ╚███╔╝                         █
█  ██║     ██║   ██║██╔══██╗   ██║   ██╔══╝   ██╔██╗                         █
█  ╚██████╗╚██████╔╝██║  ██║   ██║   ███████╗██╔╝ ██╗                        █
█   ╚═════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝                        █
█                                                                              █
█  AI-Powered Development Intelligence System                                 █
█  Author: Asif Hussain | GitHub: github.com/asifhussain60/CORTEX            █
█  Copyright © 2025 Asif Hussain. All rights reserved.                       █
█                                                                              █
████████████████████████████████████████████████████████████████████████████████
-->

# Phase 04: ADO Orchestrator 3.0

**🔗 Breadcrumb:** [← Back to Master Plan](cortex-3.9-master.md)

**Status:** ✅ Complete  
**Phase ID:** 04  
**Created:** 2024-12-14 08:45 AM  
**Version:** 3.0.0
```

---

## 🏗️ Implementation Plan

### Task 1: Create Header Template Module (20 min) ✅ COMPLETE

**File:** `src/operations/modules/templates/cortex_header.py`

**Status:** ✅ Implemented with H2 congratulations section after copyright

```python
CORTEX_ASCII_LOGO = """<!--
████████████████████████████████████████████████████████████████████████████████
█                                                                              █
█   ██████╗ ██████╗ ██████╗ ████████╗███████╗██╗  ██╗                        █
█  ██╔════╝██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝╚██╗██╔╝                        █
█  ██║     ██║   ██║██████╔╝   ██║   █████╗   ╚███╔╝                         █
█  ██║     ██║   ██║██╔══██╗   ██║   ██╔══╝   ██╔██╗                         █
█  ╚██████╗╚██████╔╝██║  ██║   ██║   ███████╗██╔╝ ██╗                        █
█   ╚═════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝                        █
█                                                                              █
█  AI-Powered Development Intelligence System                                 █
█  Author: Asif Hussain | GitHub: github.com/asifhussain60/CORTEX            █
█  Copyright © 2025 Asif Hussain. All rights reserved.                       █
█                                                                              █
████████████████████████████████████████████████████████████████████████████████
-->

## 🎉 CONGRATULATIONS"""


def generate_cortex_header(
    document_title: str,
    document_type: str,
    status: str = "🟡 In Progress",
    version: Optional[str] = None,
    additional_metadata: Optional[dict] = None
) -> str:
    """
    Generate standardized CORTEX header for markdown documents.
    
    Args:
        document_title: Title of the document (H1 level)
        document_type: Type classification (Master Plan, Sub-Plan, Report, etc.)
        status: Document status with emoji
        version: Version number (optional)
        additional_metadata: Extra metadata fields (optional)
    
    Returns:
        Formatted markdown header with CORTEX branding
    
    Example:
        >>> header = generate_cortex_header(
        ...     document_title="CORTEX Evolution v3.9",
        ...     document_type="Tier 4 Complex Plan",
        ...     status="🟡 In Progress",
        ...     version="3.9.0"
        ... )
    """
    created_date = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    
    # Build metadata section
    metadata = [
        f"**Type:** {document_type}",
        f"**Status:** {status}",
        f"**Created:** {created_date}"
    ]
    
    if version:
        metadata.append(f"**Version:** {version}")
    
    if additional_metadata:
        for key, value in additional_metadata.items():
            metadata.append(f"**{key}:** {value}")
    
    # Assemble header
    header_parts = [
        CORTEX_ASCII_LOGO,
        "",
        f"# {document_title}",
        "",
        "\n".join(metadata),
        "",
        "---",
        ""
    ]
    
    return "\n".join(header_parts)


def generate_sub_plan_header(
    phase_id: str,
    phase_name: str,
    master_plan_path: str,
    status: str = "⏳ Pending",
    version: Optional[str] = None
) -> str:
    """
    Generate header specifically for sub-plan documents.
    
    Args:
        phase_id: Phase identifier (e.g., "04")
        phase_name: Human-readable phase name
        master_plan_path: Relative path to master plan
        status: Phase status
        version: Version number (optional)
    
    Returns:
        Formatted sub-plan header with breadcrumb navigation
    """
    created_date = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    
    # Build metadata
    metadata = [
        f"**🔗 Breadcrumb:** [← Back to Master Plan]({master_plan_path})",
        "",
        f"**Status:** {status}",
        f"**Phase ID:** {phase_id}",
        f"**Created:** {created_date}"
    ]
    
    if version:
        metadata.append(f"**Version:** {version}")
    
    # Assemble header
    header_parts = [
        CORTEX_ASCII_LOGO,
        "",
        f"# Phase {phase_id}: {phase_name}",
        "",
        "\n".join(metadata),
        "",
        "---",
        ""
    ]
    
    return "\n".join(header_parts)


# Quick access functions
def master_plan_header(title: str, plan_type: str, version: str) -> str:
    """Generate header for master planning documents."""
    return generate_cortex_header(
        document_title=title,
        document_type=plan_type,
        status="🟡 In Progress",
        version=version
    )


def report_header(title: str, report_type: str) -> str:
    """Generate header for reports and analysis documents."""
    return generate_cortex_header(
        document_title=title,
        document_type=report_type,
        status="✅ Complete"
    )
```

### Task 2: Update Planning Orchestrator 3.0 (20 min)

**Modification:** `src/operations/modules/orchestration/planning_orchestrator.py`

Add import:
```python
from src.operations.modules.templates.cortex_header import (
    generate_cortex_header, generate_sub_plan_header
)
```

Modify `_create_planning_document()` method to inject header:
```python
def _create_planning_document(self, context: PlanningContext) -> Path:
    """Create planning document with CORTEX header."""
    
    # Generate header
    header = generate_cortex_header(
        document_title=context.title,
        document_type=f"Tier {context.tier} Plan",
        status="🟡 In Progress",
        version=self.version
    )
    
    # Assemble content
    content = f"{header}\n\n{context.body_content}"
    
    # Write file
    doc_path.write_text(content, encoding='utf-8')
    return doc_path
```

### Task 3: Update ADO Orchestrator 3.0 (10 min)

**Modification:** `src/operations/modules/orchestration/ado_planning_orchestrator.py`

Same pattern as Planning Orchestrator - inject header in document creation methods.

### Task 4: Update Existing cortex-3.9 Documents (10 min)

**Files to Update:**
- `cortex-3.9-master.md`
- All phase sub-plans (phase-00-govern.md through phase-18-autodocs.md)

**Script:** Create migration script for bulk update

---

## 📋 Expected Deliverables

### Code Files
- ✅ `src/operations/modules/templates/cortex_header.py` (new module - H2 congratulations after copyright)
- ✅ `src/operations/modules/templates/__init__.py` (package init)
- ⏳ `src/operations/modules/orchestration/planning_orchestrator.py` (updated)
- ⏳ `src/operations/modules/orchestration/ado_planning_orchestrator.py` (updated)
- ⏳ `scripts/migrate_cortex_headers.py` (migration script)

### Documentation
- ⏳ `cortex-3.9-master.md` (updated with new header)
- ⏳ All phase sub-plans updated with standardized headers
- ⏳ `cortex.config.json` (header configuration section)

### Test Coverage
- ✅ `tests/test_cortex_header.py` (22 tests - 100% passing)
- **Target:** ✅ Achieved 100% coverage for header generation

---

## 🔄 Task 5: Congratulations Section Placement (NEW) ✅ COMPLETE

**Objective:** Clarify that congratulations header appears AFTER the ASCII logo, not within it

**Implementation:**
```python
CORTEX_ASCII_LOGO = """<!--
████████████████████████████████████████████████████████████████████████████████
█                                                                              █
█   ██████╗ ██████╗ ██████╗ ████████╗███████╗██╗  ██╗                        █
█  ██╔════╝██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝╚██╗██╔╝                        █
█  ██║     ██║   ██║██████╔╝   ██║   █████╗   ╚███╔╝                         █
█  ██║     ██║   ██║██╔══██╗   ██║   ██╔══╝   ██╔██╗                         █
█  ╚██████╗╚██████╔╝██║  ██║   ██║   ███████╗██╔╝ ██╗                        █
█   ╚═════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝                        █
█                                                                              █
█  AI-Powered Development Intelligence System                                 █
█  Author: Asif Hussain | GitHub: github.com/asifhussain60/CORTEX            █
█  Copyright © 2025 Asif Hussain. All rights reserved.                       █
█                                                                              █
████████████████████████████████████████████████████████████████████████████████
-->"""

# Congratulations appears AFTER logo in completion documents:
# 
# {CORTEX_ASCII_LOGO}
# 
## 🎉 CONGRATULATIONS
#
# ## 🧠 CORTEX {Operation Name}
```

**Usage Clarification:**
1. **Standard Documents:** ASCII logo only (box art with copyright)
2. **Completion Documents:** ASCII logo + "🎉 CONGRATULATIONS" as H2 + document content
3. **Introduction Response:** Separate blocky "CORTEX" ASCII art (second screenshot)

**Changes:**
- ASCII logo remains clean with just the box art and copyright
- Congratulations section added separately in completion response templates
- Blocky ASCII art reserved for introduction/branding responses only

**Status:** ✅ Complete - ASCII logo restored to original format

---

## 🔄 Next Steps

**Upon Completion:**
1. All future planning documents automatically include CORTEX header
2. Existing documents maintain consistency with brand identity
3. Professional appearance for external sharing

**Integration Points:**
- Planning Orchestrator 3.0
- ADO Planning Orchestrator 3.0
- Future document generation systems

---

## 🎯 Benefits

1. **Brand Consistency:** Unified identity across all CORTEX outputs
2. **Professional Appearance:** Polished documents for stakeholder sharing
3. **Copyright Clarity:** Clear attribution while maintaining authorship
4. **Automation:** One-time setup, automatic for all future work
5. **Maintainability:** Single source of truth for header format

---

**Phase Owner:** Asif Hussain  
**Phase Status:** ⏳ Ready to Implement  
**Priority:** MEDIUM (Enhancement, not blocking)
