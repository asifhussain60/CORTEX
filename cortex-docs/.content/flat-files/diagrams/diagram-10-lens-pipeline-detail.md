# LENS Analysis Pipeline — Detailed Analyzer Flow
# 10-analyzer parallel execution with synthesis and caching

```
                            ┌──────────────────────┐
                            │  SOURCE CODE INPUT   │
                            │  (file, directory,   │
                            │   or repository)     │
                            └──────────┬───────────┘
                                       │
                                       ▼
                            ┌──────────────────────┐
                            │   LENS CONTROLLER    │
                            │   cortex/lens/       │
                            │                      │
                            │   • Route to cache?  │
                            │   • TTL check        │
                            │   • Hash fingerprint │
                            └──────────┬───────────┘
                                       │
                              CACHE HIT? ──→ YES ──→ Return cached result
                                       │
                                       │ NO
                                       ▼
              ┌────────────────────────────────────────────────┐
              │          PARALLEL DISPATCH (all 10)            │
              │          concurrent execution                  │
              └──┬──────┬──────┬──────┬──────┬──────┬────┬────┘
                 │      │      │      │      │      │    │
   ┌─────────┐  │  ┌───┴──┐  ┌┴─────┐ ┌┴────┐ ┌───┴┐  ┌┴────┐
   │   AST   │  │  │ Git  │  │Commt │ │Impt │ │Sec │  │Patn │
   │Analyzer │  │  │Hist. │  │Anlyz │ │Anlyz│ │Anlz│  │Anlyz│
   │         │  │  │      │  │      │ │     │ │    │  │     │
   │Classes  │  │  │Freq  │  │Docs  │ │Deps │ │CVE │  │Arch │
   │Funcs    │  │  │Churn │  │TODO  │ │Circ │ │Sec │  │Anti │
   │Inherit  │  │  │Authrs│  │Ratio │ │Graph│ │Pats│  │Pats │
   │Complex  │  │  │Blame │  │Cover │ │     │ │    │  │     │
   └────┬────┘  │  └──┬───┘  └──┬───┘ └──┬──┘ └─┬──┘  └──┬──┘
        │       │     │         │        │      │        │
        │  ┌────┴──┐ ┌┴──────┐ ┌┴──────┐│      │        │
        │  │Metric │ │Domain │ │ Tech  ││      │        │
        │  │Anlyz  │ │Anlyz  │ │ Stack ││      │        │
        │  │       │ │       │ │Anlyz  ││      │        │
        │  │Lines  │ │Biz    │ │       ││      │        │
        │  │Dup    │ │Knwldg │ │Frame  ││      │        │
        │  │Ratio  │ │Align  │ │Lang   ││      │        │
        │  └──┬────┘ └──┬────┘ └──┬────┘│      │        │
        │     │         │        │      │      │        │
        └─────┴─────────┴────────┴──────┴──────┴────────┘
                                 │
                                 ▼
              ┌──────────────────────────────────────────┐
              │           SYNTHESIS ENGINE               │
              │                                          │
              │  Input: 10 AnalyzerResult objects         │
              │                                          │
              │  Operations:                             │
              │  ├── Merge findings across analyzers     │
              │  ├── Detect cross-analyzer correlations  │
              │  ├── Compute composite confidence (0–1)  │
              │  ├── Generate risk assessment            │
              │  ├── Build actionable recommendations    │
              │  └── Create cross-reference index        │
              │                                          │
              │  Output: UnifiedLENSResult               │
              │  ├── confidence_score: float             │
              │  ├── risk_level: LOW | MEDIUM | HIGH     │
              │  ├── findings: List[Finding]             │
              │  ├── recommendations: List[Action]       │
              │  └── cross_refs: Dict[analyzer, refs]    │
              └──────────────────┬───────────────────────┘
                                 │
                                 ▼
              ┌──────────────────────────────────────────┐
              │           CACHE STORE                    │
              │                                          │
              │  Key: hash(file_path + content_hash)     │
              │  Value: UnifiedLENSResult                │
              │  TTL: configurable (default 5 min)       │
              │  Eviction: LRU when capacity exceeded    │
              └──────────────────┬───────────────────────┘
                                 │
                                 ▼
                        LENS ANALYSIS RESULT
                        (300–800ms total)
```

# LENS Acronym Expanded

```
    L ── Language     ──→  AST parsing, syntax tree construction, language detection
    │
    E ── Examination  ──→  Deep inspection: metrics, patterns, security, complexity
    │
    N ── Navigation   ──→  Dependency graphs, import chains, call hierarchies
    │
    S ── Synthesis    ──→  Merge all findings into one unified intelligence report
```
