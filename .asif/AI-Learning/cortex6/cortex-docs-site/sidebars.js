/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
module.exports = {
  docs: [
    'index',
    {
      type: 'category',
      label: 'Getting Started',
      items: [
        'getting-started/what-is-cortex',
        'getting-started/quickstart',
        'getting-started/repo-structure',
      ],
    },
    {
      type: 'category',
      label: 'Architecture',
      items: [
        'architecture/layers',
        'architecture/components',
        'architecture/data-model',
        'architecture/state-resilience',
        'architecture/security-performance',
      ],
    },
    {
      type: 'category',
      label: 'Governance',
      items: [
        'governance/overview',
        'governance/categories',
        'governance/merge-algorithm',
        'governance/unified-instruction-set',
      ],
    },
    {
      type: 'category',
      label: 'Orchestrators',
      items: [
        'orchestrators/master',
        'orchestrators/todo',
        'orchestrators/pattern-router',
        'orchestrators/workflows',
        'orchestrators/audit-resource-limits',
      ],
    },
    {
      type: 'category',
      label: 'Multi‑Repo & MCP',
      items: [
        'multi-repo/overview',
        'multi-repo/topology',
        'multi-repo/workflows',
      ],
    },
    {
      type: 'category',
      label: 'Implementation',
      items: [
        'implementation/roadmap',
        'implementation/testing-strategy',
        'implementation/success-criteria',
      ],
    },
    {
      type: 'category',
      label: 'Diagrams',
      items: [
        'diagrams/governance-merge-flow',
        'diagrams/system-architecture',
        'diagrams/multi-repo-topology',
        'diagrams/todo-dag-example',
      ],
    },
    'glossary',
  ],
};
