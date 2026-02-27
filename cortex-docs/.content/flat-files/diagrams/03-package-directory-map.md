# Package & Directory Map
# The canonical cortex/ package and its 20 top-level directories

```
cortex/                                    ← Single canonical Python package (all imports: cortex.*)
│
├── __init__.py                            ← Package root
├── bootstrap.py                           ← Application bootstrapping
├── health_check_service.py                ← Health check entry point
│
├── core/                                  ← Core abstractions
│   ├── orchestrator_protocol_mixin.py     ← Primary base (51 orchestrators)
│   ├── orchestrator_base.py               ← Legacy base (2 orchestrators)
│   ├── file_factory.py                    ← File operations
│   └── workflow_engine.py                 ← FSM workflow execution
│
├── orchestrators/                         ← 51 wired orchestrators
│   ├── core/           17 orchestrators   ← MasterOrch, IntentRouter, TDD, Enforcement…
│   ├── domain/          7 orchestrators   ← Refactoring, Planning, Dashboard…
│   ├── support/        23 orchestrators   ← Health, Vacuum, Upgrade, Sweep…
│   └── git/             4 orchestrators   ← Git, GitPublish, PreCommit, Sanitization
│
├── mcp/                                   ← Model Context Protocol gateway
│   ├── __main__.py                        ← Entry: python3 -m cortex.mcp
│   ├── server.py                          ← stdio JSON-RPC 2.0 server
│   └── tools/          39 tool modules    ← One file per tool
│
├── intelligence/                          ← Cognitive intelligence system
│   ├── perception/                        ← Tier 1: Pattern recognition
│   ├── reasoning/                         ← Tier 2: Strategy selection
│   ├── action/                            ← Tier 3: Execution planning
│   ├── domain_brain/                      ← Domain-specific knowledge
│   ├── learning/                          ← URS feedback loop
│   ├── knowledge/                         ← Knowledge synthesis
│   ├── cross_cutting/                     ← Intelligence Matrix
│   └── wiring/                            ← Cross-tier integration
│
├── lens/                                  ← LENS analysis engine
│   ├── analyzers/      10 analyzers       ← AST, Git, Comment, Import, Security…
│   ├── synthesis/                         ← Multi-analyzer result merge
│   └── cache/                             ← TTL-based result caching
│
├── governance/                            ← Rule enforcement
│   ├── rules/                             ← Rule implementations
│   └── enforcement/                       ← EnforcementOrchestrator agents
│
├── infrastructure/     50+ modules        ← Cross-cutting concerns
│   ├── tracing/                           ← OpenTelemetry
│   ├── metrics/                           ← Prometheus
│   ├── resilience/                        ← Circuit breaker, retry, bulkhead
│   ├── cache/                             ← Cache management
│   └── security/                          ← Secret redaction, PII removal
│
├── testing/                               ← Test framework
│   ├── quality_gate.py                    ← TestQualityGate scoring
│   ├── parallel_runner.py                 ← pytest-xdist integration
│   └── golden/                            ← Golden test utilities
│
├── config/                                ← Configuration management
├── models/                                ← Data models and schemas
├── knowledge/                             ← Knowledge base access
├── templates/                             ← Template management
├── toolkit/                               ← Scanning, batch, adapters
├── tools/                                 ← CLI tools
├── cli/                                   ← CLI interface
├── dashboards/                            ← Dashboard generation
├── enforcement/                           ← Enforcement utilities
├── observability/                         ← Observability hooks
├── repositories/                          ← Repository access layer
└── secrets/                               ← Secret management

cortex-registry/                           ← Git-backed configuration
├── core/tier0-skull/   skull-rules.yaml   ← 38 CORE governance rules
├── patterns/           9 patterns         ← Enterprise architecture patterns
├── workflows/templates/                   ← Audit, TDD, production templates
├── planning/                              ← Master plan index + phase files
├── knowledge-base/                        ← Domain knowledge
└── config/                                ← System configuration

tests/                                     ← Mirrors cortex/ structure
├── golden/             486 tests          ← Regression-proof truth tests
├── orchestrators/                         ← Per-orchestrator tests
├── mcp/                                   ← MCP tool tests
├── lens/                                  ← LENS analyzer tests
├── governance/                            ← Governance rule tests
├── integration/                           ← Cross-component tests
├── infrastructure/                        ← Infrastructure tests
├── intelligence/                          ← Intelligence layer tests
└── fixtures/                              ← Shared test fixtures

.cortex-runtime/                           ← Runtime data (gitignored)
├── traces/             orchestrator-traces.db  ← SQLite WAL audit log
├── logs/                                  ← Execution logs
└── cache/                                 ← Runtime cache
```
