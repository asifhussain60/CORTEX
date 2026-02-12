// Global data definitions for the CORTEX documentation site.
// This object provides structured information used by the
// visualisation functions and tab rendering. All data is static
// and embedded so that the site works offline via file://.

window.CORTEX_DATA = {
    roles: {
        leader: {
            name: 'Business Leader',
            description: 'High-level overview of why CORTEX matters, ROI, and strategic benefits.'
        },
        po: {
            name: 'Product Owner',
            description: 'Focus on backlog health, definition of ready, and governance enforcement.'
        },
        manager: {
            name: 'Dev Manager',
            description: 'Emphasis on team orchestration, code quality, and delivery efficiency.'
        },
        engineer: {
            name: 'Software Engineer',
            description: 'Detailed view of architecture, wiring, and day‑to‑day integration.'
        },
        quality: {
            name: 'Quality / SET',
            description: 'Testing strategy, risk analysis, and continuous quality enforcement.'
        }
    },
    tiers: [
        { id: 'T0', name: 'Tier 0: Immutable Core Rules', count: 29, description: 'Enforces unchangeable governance rules such as incremental execution and naming conventions.' },
        { id: 'T1', name: 'Tier 1: Acceptance Criteria & Tracking', count: 15, description: 'Tracks AC IDs, state transitions, evidence and gates.' },
        { id: 'T2', name: 'Tier 2: Response Templates', count: 10, description: 'Maintains reusable response templates and optimises token usage.' },
        { id: 'T3', name: 'Tier 3: Knowledge Library', count: 8, description: 'Stores domain patterns, best practices and caching strategies.' }
    ],
    orchestrators: [
        { id: 'MO', name: 'MasterOrchestrator', category: 'Core', status: 'wired' },
        { id: 'IO', name: 'InteractionOrchestrator', category: 'Core', status: 'wired' },
        { id: 'IR', name: 'IntentRouter', category: 'Core', status: 'wired' },
        { id: 'TI', name: 'TechIntelligenceOrchestrator', category: 'Core', status: 'partial' },
        { id: 'PO', name: 'PlanningOrchestrator', category: 'Core', status: 'partial' },
        { id: 'TDD', name: 'TDDOrchestrator', category: 'Core', status: 'wired' },
        { id: 'AEE', name: 'AutonomousExecutionEngine', category: 'Core', status: 'aspirational' },
        { id: 'Rec', name: 'RecommendationEngine', category: 'Domain', status: 'partial' },
        { id: 'Sec', name: 'SecurityOrchestrator', category: 'Support', status: 'wired' },
        { id: 'Observ', name: 'ObservabilityOrchestrator', category: 'Support', status: 'wired' },
        { id: 'LENS', name: 'LENSContextProvider', category: 'Support', status: 'partial' }
    ],
    capabilities: [
        { id: 'gov', name: 'Governance & DoR', description: 'Ensures definition of ready, acceptance criteria, and gating are enforced via templates and states.' },
        { id: 'plan', name: 'Planning & Intent', description: 'Routes intents, synthesises plans and ensures alignment with acceptance criteria.' },
        { id: 'intel', name: 'Intelligence & LENS', description: 'Provides context‑aware knowledge via LENS, analyzers, and unified intelligence provider.' },
        { id: 'exec', name: 'Execution & TDD', description: 'Runs incremental code generation, TDD loops, and monitors continuous delivery.' },
        { id: 'know', name: 'Knowledge & Registry', description: 'Serves knowledge patterns, wiring specs, and phase registry through Git backed registry.' },
        { id: 'obs', name: 'Observability & Security', description: 'Captures metrics, traces, audits and ensures secure operations.' }
    ],
    wiringMatrix: [
        // Each entry describes an orchestrator and its dependencies/health for wiring.
        { name: 'MasterOrchestrator', dependencies: ['InteractionOrchestrator','IntentRouter','PlanningOrchestrator'], status: 'wired' },
        { name: 'TechIntelligenceOrchestrator', dependencies: ['LENSContextProvider'], status: 'partial' },
        { name: 'AutonomousExecutionEngine', dependencies: ['PlanningOrchestrator','TDDOrchestrator'], status: 'aspirational' },
        { name: 'RecommendationEngine', dependencies: ['TechIntelligenceOrchestrator'], status: 'partial' },
        { name: 'SecurityOrchestrator', dependencies: [], status: 'wired' }
    ],
    tests: [
        { layer: 'Unit', percent: 60 },
        { layer: 'Integration', percent: 25 },
        { layer: 'System', percent: 10 },
        { layer: 'End-to-End', percent: 5 }
    ],
    risks: [
        { area: 'Wiring', severity: 3, likelihood: 2, description: 'Partial wiring may cause orchestrators to be unreachable.' },
        { area: 'Intelligence', severity: 2, likelihood: 3, description: 'Incomplete LENS integration limits knowledge context.' },
        { area: 'Security', severity: 4, likelihood: 2, description: 'Secrets exposure and prompt injection surfaces.' },
        { area: 'Deployment', severity: 3, likelihood: 3, description: 'Assumptions on environment can break in CI or containers.' }
    ]
};