# LENS Company Domain Integration
# How LENS adapts analysis to company-specific contexts

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMPANY CONFIGURATION                        │
│                                                                 │
│  cortex-registry/company/                                       │
│  ├── domains.yaml          ← Business domain definitions        │
│  ├── standards.yaml        ← Company-specific coding standards  │
│  ├── patterns.yaml         ← Custom architecture patterns       │
│  └── work-items.yaml       ← Ticketing system configuration     │
│                                                                 │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               │ loaded at startup
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                    LENS ANALYSIS                                 │
│                                                                  │
│  Standard Analyzers (10)     Company Overlay                     │
│  ┌──────────────────┐       ┌──────────────────┐                 │
│  │ AST              │       │ Domain Analyzer  │                 │
│  │ Git History      │       │                  │                 │
│  │ Comment          │       │ Maps code to     │                 │
│  │ Import           │◄─────►│ business domains │                 │
│  │ Security         │       │ using company    │                 │
│  │ Pattern          │       │ domain defs      │                 │
│  │ Metrics          │       │                  │                 │
│  │ Domain           │       │ Custom rules     │                 │
│  │ Tech Stack       │       │ override generic │                 │
│  │ Extended         │       │                  │                 │
│  └──────────────────┘       └──────────────────┘                 │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │                SYNTHESIS                                  │    │
│  │                                                          │    │
│  │  Generic findings + Company-specific findings merged     │    │
│  │  Company rules WIN on conflict with generic rules        │    │
│  │                                                          │    │
│  │  Output includes:                                        │    │
│  │  • Standard LENS scores                                  │    │
│  │  • Business domain classification                        │    │
│  │  • Company-standard compliance                           │    │
│  │  • Custom pattern match scores                           │    │
│  └──────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘

                        ┌─────────────────┐
                        │ ADO INTEGRATION │
                        └────────┬────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│ WorkItemProvider │   │ Sprint Context  │   │ Priority Data   │
│                  │   │                 │   │                 │
│ 3 methods:       │   │ LENS uses work  │   │ Risk scores     │
│ • list_items     │   │ item context to │   │ weighted by     │
│ • get_item       │   │ enrich analysis │   │ business        │
│ • create_item    │   │ with priority   │   │ priority from   │
│                  │   │ and assignment  │   │ ticketing data  │
└─────────────────┘   └─────────────────┘   └─────────────────┘
```
