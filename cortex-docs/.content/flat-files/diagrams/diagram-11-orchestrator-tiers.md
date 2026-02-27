# Orchestrator Tier Architecture
# 51 wired orchestrators across 4 tiers with communication patterns

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              CORE TIER (17 orchestrators)                            │
│                                                                                     │
│  ┌──────────────────┐                                                               │
│  │ MasterOrchestrator│─────────────────────────────────────────────────┐             │
│  │ (central entry)   │                                                 │             │
│  └────────┬─────────┘                                                 │             │
│           │                                                           │             │
│  ┌────────┴─────────┐   ┌────────────────┐   ┌────────────────────┐   │             │
│  │  IntentRouter    │   │ TDDOrchestrator│   │ EnforcementOrch.  │   │             │
│  │  12+ intents     │   │ RED→GRN→REFAC  │   │ 10 agents         │   │             │
│  │  20–40ms         │   │ CORE-008       │   │ 38 rules          │   │             │
│  └──────────────────┘   └────────────────┘   └────────────────────┘   │             │
│                                                                       │             │
│  ┌────────────────┐ ┌─────────────────┐ ┌──────────────────────┐      │             │
│  │ WorkflowOrch.  │ │ ConversationO.  │ │ InteractionOrch.     │      │             │
│  │ FSM engine     │ │ multi-turn      │ │ DoR / user flows     │      │             │
│  └────────────────┘ └─────────────────┘ └──────────────────────┘      │             │
│                                                                       │             │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐             │             │
│  │ AuditOrch.     │ │ ResponseOrch.  │ │ MetaAuditOrch. │             │             │
│  │ 19-point scan  │ │ formatting     │ │ 23 checks      │             │             │
│  └────────────────┘ └────────────────┘ └────────────────┘             │             │
│                                                                       │             │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐             │             │
│  │ HolisticValid. │ │ ChallengeOrch. │ │ SOLIDOrch.     │             │             │
│  │ CORE-048 gate  │ │ alternatives   │ │ design check   │             │             │
│  └────────────────┘ └────────────────┘ └────────────────┘             │             │
│                                                                       │             │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐             │             │
│  │ SecurityOrch.  │ │ Stage1Orch.    │ │ Stage3/4Orch.  │             │             │
│  │ vuln scanning  │ │ pipeline stg 1 │ │ pipeline stg 3-4│            │             │
│  └────────────────┘ └────────────────┘ └────────────────┘             │             │
│                                                                       │             │
│  All core orchestrators route through MasterOrchestrator ◄────────────┘             │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                     │
                    OrchestratorEventBus (decoupled messaging)
                                     │
┌─────────────────────────────────────┴────────────────────────────────────────────────┐
│                              DOMAIN TIER (7 orchestrators)                           │
│                                                                                      │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ ┌────────────────┐   │
│  │ RefactoringOrch. │ │ PlanningOrch.    │ │ DomainOrch.      │ │ DashboardOrch. │   │
│  │ Python/TS/C#     │ │ gap catalogues   │ │ business logic   │ │ static gen     │   │
│  └──────────────────┘ └──────────────────┘ └──────────────────┘ └────────────────┘   │
│                                                                                      │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐                      │
│  │ SDLCWorkflowO.   │ │ EnhancedPlanO.   │ │ ServiceDecompO.  │                      │
│  │ lifecycle templ.  │ │ ROI scoring      │ │ decomposition    │                      │
│  └──────────────────┘ └──────────────────┘ └──────────────────┘                      │
└──────────────────────────────────────────────────────────────────────────────────────┘
                                     │
┌─────────────────────────────────────┴────────────────────────────────────────────────┐
│                              SUPPORT TIER (23 orchestrators)                         │
│                                                                                      │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐  │
│  │ HealthOrch.  │ │ VacuumOrch.  │ │ UpgradeOrch. │ │ SweepCatO.   │ │ SetupOrch. │  │
│  │ monitoring   │ │ cleanup      │ │ lifecycle    │ │ CORE-064     │ │ env setup  │  │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘  │
│                                                                                      │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐  │
│  │ OnboardOrch. │ │ BulkDigest   │ │ DigestSessO. │ │ DebuggerO.   │ │ RollbackO. │  │
│  │ LENS onboard │ │ bulk ingest  │ │ session mgmt │ │ debug coord  │ │ recovery   │  │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘  │
│                                                                                      │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                 │
│  │ UnifDiscovO. │ │ UnifQualO.   │ │ AutoHealMCP  │ │ CortexDocsO. │                │
│  │ discovery    │ │ quality gate │ │ self-heal    │ │ doc gen      │                 │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘                 │
│  + additional support orchestrators                                                  │
└──────────────────────────────────────────────────────────────────────────────────────┘
                                     │
┌─────────────────────────────────────┴────────────────────────────────────────────────┐
│                              GIT TIER (4 orchestrators)                              │
│                                                                                      │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ ┌────────────────┐   │
│  │ GitOrchestrator  │ │ GitPublishOrch.  │ │ PreCommitEnfO.   │ │ SanitizeOrch.  │   │
│  │ commit/branch/   │ │ structured       │ │ CORE rules at    │ │ secret scan    │   │
│  │ merge/diff       │ │ commit + push    │ │ commit time      │ │ PII removal    │   │
│  └──────────────────┘ └──────────────────┘ └──────────────────┘ └────────────────┘   │
└──────────────────────────────────────────────────────────────────────────────────────┘
```
