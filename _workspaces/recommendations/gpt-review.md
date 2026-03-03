Please act as an Expert UI/UX Engineer and Data Visualization Architect. I need you to completely redesign and elevate three distinct HTML views for my platform, CORTEX (business-leader.html, product-owner.html, and software-engineer.html). These pages will be hosted on GitHub Pages, so they must rely entirely on static front-end technologies: HTML5, CSS3, vanilla JavaScript, D3.js (v7), and Mermaid.js.
The overarching design system must be a premium, modern "Dark Blue Glassmorphism" theme. Use deep navy backgrounds (#0a0e27), vibrant cyan/neon blue and emerald green accents, semi-transparent frosted glass cards (backdrop-filter: blur(12px)), subtle glowing borders, and clean typography (Inter and Space Grotesk). Integrate intelligent, subtle CSS animations like smooth fade-ins on scroll (using Intersection Observer), gentle hover elevations, and pulse effects for critical metrics.
CRITICAL RULE: Do not repeat content, diagrams, or chart styles across the three views. Previously, the views felt like carbon copies with just the text swapped out. Each view must feature entirely bespoke visualizations tailored to the specific psychological and professional goals of the target persona.
1. Business Leader View (Target: CTOs, VP of Engineering, Executives)
This view must lead with BLUF (Bottom Line Up Front) and focus on capital efficiency, risk mitigation, and compounding ROI. Do not show low-level pipeline details here.
* Visualizations to Build:
    *     * D3.js Area Chart (The Compounding Cost of Tech Debt): Create a visually striking, dual-series area chart comparing the exponential cost curve of unmanaged AI technical debt versus the flattened, predictable OPEX curve governed by CORTEX over a 12-month projection. Use glowing gradients for the fill areas.
    *     * D3.js Interactive Bubble Chart (Risk vs. Capability Matrix): Plot "Delivery Velocity" on the X-axis and "Compliance Risk" on the Y-axis. Show how legacy and ungoverned AI sit in high-risk/low-velocity quadrants, while CORTEX forces teams into the high-velocity/zero-risk quadrant.
    *     * Mermaid.js Diagram (Executive Value Stream): Design a high-level, boardroom-ready flowchart showing Capital Input → Autonomous Governance (Zero-Trust Gate) → Secured IP/Asset Generation.
* * UI Elements: Include premium "Metric Ticker" cards at the top displaying hard numbers: OPEX savings, 0% escaped CVEs, and 4x Time-to-Market acceleration.
2. Product Owner View (Target: Agile Leaders, Scrum Masters, Product Managers)
This view must focus strictly on predictability, backlog throughput, scope control, and Definition of Ready (DoR) / Definition of Done (DoD) enforcement.
* Visualizations to Build:
    *     * D3.js Sprint Burnup Chart with Scope Creep: Create a chart showing a standard sprint burnup. Crucially, add a "Scope" line that remains perfectly flat to visually prove that CORTEX's DoR enforcement eliminates mid-sprint scope creep.
    *     * D3.js Dual-Axis Bar/Line Chart (Throughput vs. Escaped Defects): Use bars to show Story Points delivered increasing sprint-over-sprint, overlaid with a line chart showing escaped defects dropping to absolute zero.
    *     * Mermaid.js State Diagram (Intent Routing & Traceability): Show how a User Story maps to Acceptance Criteria, which routes through the Workflow Composer, automatically generates TDD tests, and outputs a cryptographic SQLite audit hash.
* * UI Elements: Build interactive, horizontal comparative cards showing the "Traditional User Story Lifecycle" (fraught with rework and QA ping-pong) versus the "CORTEX Governed Lifecycle" (linear, automated, verified).
3. Software Engineer View (Target: Developers, Architects)
This page is currently just a stub and needs the most work. It must take the user on a multi-level "Deep Dive Journey" from high-level architecture down to intricate execution, proving CORTEX's technical superiority.
* Level 1: The Macro Architecture (High-Level)
    *     * Mermaid.js C4-Style Diagram: Create a complex system architecture map showcasing the 9 domains, the MCP Gateway, and the Enforcement Orchestrator.
* Level 2: The Orchestrator Ecosystem (Intricate Design)
    *     * D3.js Force-Directed Network Graph: Build a highly impressive, interactive network graph representing the 258 orchestrator files and 30 MCP tools. Nodes should be grouped by domain with connecting links showing data flow. Allow users to hover over nodes to see tooltips of their functions.
* Level 3: The Micro-Execution (Code/Execution Level)
    *     * D3.js Sunburst or Flame Graph: Visualize the 300-800ms "LENS Analysis" phase, breaking down how the AST structure, Security, and Dependency scans run in parallel fractions of a second.
    *     * Mermaid.js Sequence Diagram: Map out the exact step-by-step technical execution of the CORE-068 Convergence Loop (TDD RED → GREEN → REFACTOR).
* * UI Elements: Include mock IDE terminal windows with syntax-highlighted code snippets showing the YAML governance rules and SQLite WAL audit logs. Use sticky scroll-spy navigation so the user can easily traverse this deep technical journey.
Please rewrite the HTML, CSS, and JS for these three files ensuring they are distinct, fully responsive, visually breathtaking, and perfectly aligned with the dark glassmorphism aesthetic. Output the complete, single-file code for each view.