window.CORTEX_DOC = {
  "version": "1.0.0",
  "lastUpdated": "2026-02-10",
  "roles": [
    {"id":"business","name":"Business Leader","icon":"👔","tagline":"Understand capability, risk, and outcomes. Skip the code; keep the truth.","path":["overview","capabilities","risk","ops","next"]},
    {"id":"po","name":"Product Owner","icon":"📋","tagline":"Turn ideas into ready-to-build work with Definition-of-Ready discipline.","path":["overview","capabilities","journeys","intelligence","next"]},
    {"id":"manager","name":"Dev Manager","icon":"🧭","tagline":"Predictable delivery: drift prevention, quality gates, test posture, and ops readiness.","path":["overview","architecture","quality","risk","ops","next"]},
    {"id":"engineer","name":"Software Engineer","icon":"💻","tagline":"How the wiring, orchestrators, and LENS intelligence actually operate.","path":["overview","architecture","intelligence","wiring","quality","next"]},
    {"id":"quality","name":"Quality / SET","icon":"🧪","tagline":"TDD-first behavior, regression matrices, and brittleness-proof release confidence.","path":["overview","quality","wiring","risk","ops","next"]}
  ],
  "tabs": [
    {"id":"overview","title":"Overview"},
    {"id":"capabilities","title":"Capabilities"},
    {"id":"journeys","title":"Role Journeys"},
    {"id":"architecture","title":"Architecture"},
    {"id":"intelligence","title":"Intelligence (LENS)"},
    {"id":"wiring","title":"Wiring & Registry"},
    {"id":"quality","title":"Quality & Testing"},
    {"id":"risk","title":"Security & Risk"},
    {"id":"ops","title":"Ops & Deployment"},
    {"id":"next","title":"Next Steps"}
  ],
  "executive": {
    "headline": "CORTEX is a governed AI development system: it routes intent, builds evidence-backed context, blocks unsafe work early, and orchestrates delivery with quality gates.",
    "truth": "Architecture is strong. Brittleness concentrates in wiring completeness, enforcement consistency, and deployment assumptions—fixable hardening tasks.",
    "whatYouGet": [
      "Decision-grade visibility (what exists, what’s wired, what’s risky)",
      "Guided workflows (DoR → plan → implement → validate)",
      "A platform for team collaboration (shared standards, templates, guardrails)",
      "A foundation for LENS dashboards that convert repos into visual documentation"
    ]
  },
  "capabilities": [
    {"id":"gov","name":"Governance & CORE Rules","icon":"🛡️","maturity":"implemented","business":"Prevents costly rework by blocking ambiguous or unsafe requests before execution.","engineering":"Enforces DoR, structured Q&A, acceptance criteria, and evidence trails."},
    {"id":"lens","name":"CORTEX LENS Intelligence","icon":"🧠","maturity":"partial","business":"Turns codebases into understandable capability maps and architecture stories.","engineering":"Uses analyzers and synthesis to provide context to orchestrators; value increases as wiring becomes universal."},
    {"id":"registry","name":"Registry + Wiring as Source of Truth","icon":"🧬","maturity":"implemented","business":"Makes CORTEX repeatable and auditable across teams and time.","engineering":"wiring.yaml defines what exists and how flows connect."},
    {"id":"tdd","name":"TDD-first Delivery Orchestration","icon":"🧪","maturity":"partial","business":"Reduces regressions and improves confidence per release.","engineering":"Promotes red→green→refactor and regression-matrix thinking."},
    {"id":"review","name":"Holistic Review & Drift Prevention","icon":"🔍","maturity":"partial","business":"Catches late surprises earlier, reducing schedule risk.","engineering":"Architecture checks + enforcement orchestrators reduce scope creep."},
    {"id":"lensdash","name":"LENS Dashboard (9–10 tab model)","icon":"🗺️","maturity":"planned","business":"Stakeholders explore architecture, risks, and capabilities visually.","engineering":"Standardized JSON artifacts power a UI without fragile manual docs."}
  ],
  "journeys": [
    {"id":"j_biz","role":"business","title":"Leadership Tour: From value to risk to readiness","steps":[{"name":"Capability map","desc":"See what CORTEX enables (governance, LENS context, orchestration)."},{"name":"Risk constellation","desc":"Identify brittleness, security exposure, and adoption risks."},{"name":"Deployment readiness","desc":"Understand what it takes to make CORTEX permanent and reliable."}]},
    {"id":"j_po","role":"po","title":"Product Tour: Make work “ready” and measurable","steps":[{"name":"Definition of Ready","desc":"Convert ideas into scoped, testable outcomes before coding."},{"name":"Use-case sequences","desc":"See how intent becomes executable steps across orchestrators."},{"name":"Acceptance & auditability","desc":"Ensure outputs are reviewable and traceable."}]},
    {"id":"j_eng","role":"engineer","title":"Engineer Tour: Wiring truth, intelligence flow, test posture","steps":[{"name":"Architecture graph","desc":"Navigate orchestrators and their responsibilities."},{"name":"LENS pipeline","desc":"Understand analyzers → synthesis → gating → execution."},{"name":"Wiring integrity","desc":"Find gaps: orphans, missing validators, drift risks."}]},
    {"id":"j_qual","role":"quality","title":"Quality Tour: From TDD to regression confidence","steps":[{"name":"Test pyramid","desc":"Make unit/integration/E2E balance explicit."},{"name":"Regression matrix","desc":"Map capabilities → tests; expose untested critical paths."},{"name":"Break-the-wiring tests","desc":"Prove safe failure and deployment resilience."}]}
  ],
  "architectureGraph": {
    "nodes": [
      {"id":"User","group":"external"},
      {"id":"MCP Gateway","group":"core"},
      {"id":"IntentRouter","group":"core"},
      {"id":"LENS Analyzers","group":"intelligence"},
      {"id":"LENSSynthesis","group":"intelligence"},
      {"id":"EnforcementOrchestrator","group":"core"},
      {"id":"MasterOrchestrator","group":"core"},
      {"id":"PlanningOrchestrator","group":"domain"},
      {"id":"TDDOrchestrator","group":"domain"},
      {"id":"RefactorOrchestrator","group":"domain"},
      {"id":"ReviewOrchestrator","group":"support"},
      {"id":"Brain Tiers (0–3)","group":"brain"},
      {"id":"Registry + wiring.yaml","group":"registry"},
      {"id":"Knowledge Repository","group":"brain"}
    ],
    "links": [
      {"source":"User","target":"MCP Gateway","label":"request"},
      {"source":"MCP Gateway","target":"IntentRouter","label":"route"},
      {"source":"IntentRouter","target":"LENSSynthesis","label":"context"},
      {"source":"LENS Analyzers","target":"LENSSynthesis","label":"evidence"},
      {"source":"LENSSynthesis","target":"EnforcementOrchestrator","label":"DoR / gates"},
      {"source":"EnforcementOrchestrator","target":"MasterOrchestrator","label":"permit"},
      {"source":"MasterOrchestrator","target":"PlanningOrchestrator","label":"PLAN"},
      {"source":"MasterOrchestrator","target":"TDDOrchestrator","label":"IMPLEMENT/FIX"},
      {"source":"MasterOrchestrator","target":"RefactorOrchestrator","label":"REFACTOR"},
      {"source":"MasterOrchestrator","target":"ReviewOrchestrator","label":"validate"},
      {"source":"Brain Tiers (0–3)","target":"LENSSynthesis","label":"rules/templates"},
      {"source":"Registry + wiring.yaml","target":"MasterOrchestrator","label":"declares"},
      {"source":"Knowledge Repository","target":"LENSSynthesis","label":"best practices"}
    ]
  },
  "wiringMatrix": {
    "columns": ["Declared in wiring","Importable","Used by flow","Has validator","Has tests"],
    "rows": [
      {"name":"MasterOrchestrator","vals":[1,1,1,1,1],"badge":"implemented"},
      {"name":"IntentRouter","vals":[1,1,1,1,1],"badge":"implemented"},
      {"name":"LENSSynthesis","vals":[1,1,1,0,0],"badge":"partial"},
      {"name":"EnforcementOrchestrator","vals":[1,1,1,0,0],"badge":"partial"},
      {"name":"TDDOrchestrator","vals":[1,1,1,0,0],"badge":"partial"},
      {"name":"RefactorOrchestrator","vals":[1,1,1,0,0],"badge":"partial"}
    ],
    "note": "Illustrative until generated directly from wiring.yaml inventory."
  },
  "risks": [
    {"id":"r_wiring","category":"Wiring","severity":4,"likelihood":3,"title":"Uneven wiring completeness","desc":"Intelligence modules exist but are not consistently wired, creating drift and inconsistent behavior."},
    {"id":"r_dor","category":"Governance","severity":4,"likelihood":3,"title":"DoR not universally enforced","desc":"DoR described as universal; it must be hard-blocked in all flows to prevent bypass."},
    {"id":"r_assumptions","category":"Deployment","severity":4,"likelihood":4,"title":"Environment assumptions","desc":"Filepaths, working directory, and tool availability can break in CI/container/enterprise restrictions."},
    {"id":"r_injection","category":"Security","severity":3,"likelihood":2,"title":"Prompt/data injection surface","desc":"Repo content can contain adversarial instructions; LENS must sanitize and enforce policies."},
    {"id":"r_observability","category":"Ops","severity":3,"likelihood":3,"title":"Limited diagnosability","desc":"Without structured logs and correlation IDs, debugging wiring failures becomes slow and trust erodes."}
  ],
  "testing": {
    "pyramid": [{"name":"Unit","value":55},{"name":"Integration","value":30},{"name":"E2E","value":15}],
    "highValue": [
      "Wiring integrity tests: every orchestrator declared is importable and reachable; no orphans.",
      "Golden-path regression tests for PLAN / IMPLEMENT / ANALYZE with deterministic outputs.",
      "Break-the-wiring tests: rename/remove a wired component; fail fast with diagnostics.",
      "Schema validation tests for all JSON artifacts (versioned).",
      "Injection resilience tests: adversarial repo content cannot override CORE rules."
    ]
  },
  "ops": {
    "assumptions": [
      "Working directory and relative paths are stable (or resolved explicitly).",
      "Read-only vs write boundaries are explicit (safe by default).",
      "Tooling availability is validated (MCP server, analyzers, file access)."
    ],
    "observability": [
      "Decision log: why routing chose a path.",
      "Evidence log: which files/symbols informed an output.",
      "Correlation IDs to trace a request across orchestrators."
    ]
  },
  "next": [
    {"title":"Finish wiring completion (highest leverage)","items":["Wire intended intelligence engines into the analyzer pipeline consistently.","Add startup validator comparing code orchestrators vs wiring.yaml; fail on drift."]},
    {"title":"Harden governance invariants","items":["Make DoR a hard block for all IMPLEMENT/FIX flows.","Machine-validate AC markers (or scope them explicitly)."]},
    {"title":"Make deployment boring","items":["Add CI/container smoke profile and environment assumptions checklist.","Add observability hooks and a debug playbook surfaced via LENS."]}
  ]
};
