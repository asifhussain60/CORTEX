---
title: CORTEX Documentation
slug: /
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<div className="heroBanner">
  <div className="container">
    <div className="cortexKicker">CORTEX 6.0 • Governance‑Driven Orchestration</div>
    <h1 className="cortexHeadline">
      The <span className="cortexGlow">brain</span> for GitHub Copilot
    </h1>
    <p style={{maxWidth: 860, fontSize: '1.05rem', opacity: 0.92}}>
      CORTEX is a governance‑first orchestration framework that turns ambiguous developer requests into
      deterministic, test‑driven, auditable work — across one repo or many.
    </p>

    <div className="cortexCardGrid">
      <div className="cortexCard">
        <div className="cortexKicker">Governance</div>
        <strong>4‑Category rule merging</strong>
        <p>Core rules + business compliance + company standards + learned patterns → one unified instruction set.</p>
      </div>
      <div className="cortexCard">
        <div className="cortexKicker">Orchestration</div>
        <strong>DAG‑based TODO execution</strong>
        <p>Work is represented as a Directed Acyclic Graph for ordering, parallelism, checkpoints, and rollback.</p>
      </div>
      <div className="cortexCard">
        <div className="cortexKicker">Multi‑Repo</div>
        <strong>MCP / JSON‑RPC automation</strong>
        <p>Standardized API for cross‑repo workflows with strict company isolation and domain plugins.</p>
      </div>
    </div>
  </div>
</div>

## What you’ll find here

<Tabs>
  <TabItem value="start" label="Start here" default>
    - **Getting Started**: what CORTEX is and how it fits in your workflow  
    - **Architecture**: the 6‑layer system model and component interactions  
    - **Governance**: rule tiers, merge algorithm, and unified instruction set  
  </TabItem>
  <TabItem value="build" label="Build & extend">
    - **Orchestrators**: master routing, TODO DAGs, workflow orchestrators  
    - **Multi‑Repo & MCP**: topology, registry, cross‑repo calls  
    - **Implementation**: roadmap, testing strategy, success criteria  
  </TabItem>
</Tabs>

## Design principles (high level)

- **Planning isolation**: planning produces structure, not code.
- **TDD enforcement**: tests fail before implementation begins.
- **Auditability**: every operation is logged.
- **Company isolation**: business knowledge doesn’t contaminate global core rules.
- **Incremental execution**: small steps to prevent context overflow and enable checkpoints.
