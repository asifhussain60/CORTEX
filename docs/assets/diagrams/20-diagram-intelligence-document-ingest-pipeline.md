---
id: intelligence-document-ingest-pipeline
title: Document Ingest Pipeline — 5-Component Knowledge Extraction
purpose: Show how CORTEX ingests external documents (Word, Excel, PowerPoint, PDF) and converts them into structured knowledge in cortex-registry/.
audience:
  - Business Leaders
  - Product Owners
  - Software Developers
source_of_truth:
  - cortex/orchestrators/support/ingest/file_classifier.py
  - cortex/orchestrators/support/ingest/document_reader.py
  - cortex/orchestrators/support/ingest/knowledge_extractor.py
  - cortex/orchestrators/support/ingest/content_router.py
  - cortex/orchestrators/support/ingest/document_ingest_orchestrator.py
last_verified: 2026-03-09
phase_status: "Phase 144 COMPLETE"
diagram_type: Intelligence
render: ascii
render_html: true
d3_method: "d3.sankey() — document flow through 5-component pipeline"
---

# Document Ingest Pipeline — 5-Component Knowledge Extraction

```
 ═══════════════════════════════════════════════════════════════════════════════
  DOCUMENT INGEST PIPELINE
  "Convert external documents into structured, governed knowledge"
 ═══════════════════════════════════════════════════════════════════════════════

  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  INPUT: External Documents                                                  │
  │                                                                             │
  │  📄 Word (.docx)  📊 Excel (.xlsx)  📽️ PowerPoint (.pptx)  📕 PDF (.pdf)   │
  │  📝 YAML (.yaml)  📑 Markdown (.md)                                         │
  │                                                                             │
  └──────────────────────────────┬──────────────────────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  COMPONENT 1: FileClassifier                                                │
  │                                                                             │
  │  • 9 file categories (POLICY, PROCESS, TECHNICAL, ADR, RUNBOOK, etc.)       │
  │  • Binary extension blocklist (reject .exe, .dll, .bin)                     │
  │  • PII detection gate (names, emails, credentials → REJECT)                 │
  │  • Output: ClassifiedFile dataclass with category + metadata                │
  │                                                                             │
  │  ❌ REJECTED FILES: binary, PII-containing, unknown format                  │
  └──────────────────────────────┬──────────────────────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  COMPONENT 2: DocumentReader                                                │
  │                                                                             │
  │  • python-docx → Word text extraction (paragraphs, tables, headers)         │
  │  • openpyxl → Excel cell extraction (sheets, ranges, formulas)              │
  │  • python-pptx → PowerPoint slide extraction (text boxes, notes)            │
  │  • pypdf → PDF text extraction (pages, metadata)                            │
  │  • Native → YAML parsing, Markdown structure extraction                     │
  │                                                                             │
  │  ⚙️ GRACEFUL DEGRADATION: Missing libraries → skip format, log warning     │
  │  Output: DocumentContent dataclass with raw text + structure                │
  └──────────────────────────────┬──────────────────────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  COMPONENT 3: KnowledgeExtractor                                            │
  │                                                                             │
  │  • YAML normalization (consistent key ordering, schema validation)          │
  │  • Text → knowledge conversion (headings, lists, code blocks)               │
  │  • Metadata extraction (author, date, version, domain signals)              │
  │  • Confidence scoring based on structure clarity                            │
  │                                                                             │
  │  Output: ExtractedKnowledge dataclass with normalized content               │
  └──────────────────────────────┬──────────────────────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  COMPONENT 4: ContentRouter                                                 │
  │                                                                             │
  │  14-Domain Routing Table:                                                   │
  │  ┌─────────────┬────────────────────────────────────────────────────────┐  │
  │  │ Domain      │ Target Path                                            │  │
  │  ├─────────────┼────────────────────────────────────────────────────────┤  │
  │  │ security    │ cortex-registry/knowledge/best-practices/security/     │  │
  │  │ architecture│ cortex-registry/knowledge/sdlc/                        │  │
  │  │ testing     │ cortex-registry/knowledge/best-practices/testing/      │  │
  │  │ governance  │ cortex-registry/governance/                            │  │
  │  │ runbook     │ cortex-registry/playbooks/                             │  │
  │  │ adr         │ cortex-registry/decisions/                             │  │
  │  │ company     │ cortex-registry/company/                               │  │
  │  │ ...         │ (14 domains total)                                     │  │
  │  └─────────────┴────────────────────────────────────────────────────────┘  │
  │                                                                             │
  │  🔒 COMPANY SEGREGATION: Company-specific content → cortex-registry/company/│
  │  Output: RoutingDecision with target path + domain classification          │
  └──────────────────────────────┬──────────────────────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  COMPONENT 5: DocumentIngestOrchestrator                                    │
  │                                                                             │
  │  Pipeline Coordination:                                                     │
  │  1. classify_directory() → scan source folder                               │
  │  2. read_documents() → extract content from each file                       │
  │  3. extract_knowledge() → normalize and structure                           │
  │  4. route_content() → determine destination                                 │
  │  5. persist_knowledge() → write to cortex-registry/ via FileFactory         │
  │  6. register_in_index() → add to Knowledge INDEX.yaml                       │
  │                                                                             │
  │  🔄 OPJ INTEGRATION: Success recorded to Operational Pattern Journal        │
  │  ↩️ TEARDOWN SUPPORT: Every ingested artifact can be cleanly reversed       │
  │                                                                             │
  │  Output: IngestResult with artifact manifest + rollback instructions        │
  └──────────────────────────────┬──────────────────────────────────────────────┘
                                 │
                                 ▼
  ┌─────────────────────────────────────────────────────────────────────────────┐
  │  OUTPUT: Structured Knowledge in cortex-registry/                           │
  │                                                                             │
  │  📚 knowledge/best-practices/   — Domain-specific guidance YAMLs            │
  │  📜 playbooks/                   — Operational runbooks                     │
  │  🏢 company/                     — Organisation-specific knowledge          │
  │  📋 INDEX.yaml                   — Updated registry with new entries        │
  │                                                                             │
  │  ✅ KNOWLEDGE READY: Available to KnowledgeGuidanceEngine + LENS analysis   │
  └─────────────────────────────────────────────────────────────────────────────┘
```

## Supported File Formats

| Format | Library | Extraction Capability |
|---|---|---|
| **Word (.docx)** | python-docx | Paragraphs, tables, headers, footers, styles |
| **Excel (.xlsx)** | openpyxl | Cell values, formulas, sheet names, ranges |
| **PowerPoint (.pptx)** | python-pptx | Slide text, speaker notes, layouts |
| **PDF (.pdf)** | pypdf | Page text, metadata, table of contents |
| **YAML (.yaml)** | PyYAML (built-in) | Full structure preservation |
| **Markdown (.md)** | Native | Headings, lists, code blocks, links |

## Graceful Degradation

All Office/PDF libraries are **lazy-loaded** with graceful degradation. If a library is unavailable:
- The specific format is skipped (not the entire pipeline)
- A warning is logged identifying the missing capability
- Other formats continue to process normally

This ensures the Document Ingest Pipeline works in minimal environments without requiring all dependencies to be installed.

## Business Impact

**For Business Leaders:** Convert existing documentation libraries (policies, procedures, compliance guides) into actionable knowledge that CORTEX references during every code review and implementation.

**For Product Owners:** Ensure that product requirements documented in Word or PDF format are automatically surfaced when engineers implement related features.

**For Engineers:** Access institutional knowledge from runbooks, ADRs, and technical guides without leaving the IDE — CORTEX retrieves relevant content automatically based on the code context.

---

*Document Ingest Pipeline verified against live implementation · Phase 144 COMPLETE*
