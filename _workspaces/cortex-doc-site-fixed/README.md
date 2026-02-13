# CORTEX Documentation Site (Offline)

This directory contains an offline HTML5 application that presents a high‑level overview of the CORTEX architecture, including its governance tiers, orchestrators, wiring health, quality strategy and risk areas. The site is designed to run locally without any external network requests, making it suitable for file‑protocol loading (e.g. opening with `file://` in your browser).

## Usage

1. Unzip the `cortex-doc-site` directory and open the `index.html` file in a modern desktop browser (Chrome, Edge, Firefox).
2. When the page loads, select your role (Business Leader, Product Owner, Dev Manager, Software Engineer or Quality). This customises the suggested navigation path through the tabs.
3. Use the tabs at the top to navigate through different sections:
   - **Overview:** Introduction to CORTEX and a radial diagram of its four governance tiers.
   - **Capabilities:** Cards describing major functional areas such as governance, planning, intelligence and execution.
   - **Architecture:** A network diagram depicting orchestrators and their dependencies.
   - **Intelligence:** Highlights CORTEX LENS and shows a coverage bar chart for tiers.
   - **Wiring & Registry:** Table summarising orchestrator wiring health.
   - **Quality & Testing:** Test pyramid bar chart.
   - **Security & Risk:** Risk matrix table.
   - **Ops & Deployment:** Operational checklist for running CORTEX in CI or container environments.
   - **Next Steps:** Suggested actions tailored to the selected role.

## Customisation

The data driving the visualisations is defined in `assets/js/data.js`. You can extend or modify the arrays to reflect new orchestrators, tiers, capabilities, tests and risks.

Visualisations are implemented with plain SVG in `assets/js/visualizations.js`. Feel free to adjust colours, sizes or add new diagrams.

## Limitations

This offline documentation is a simplified representation intended for demonstration purposes. It does not reflect every orchestrator or phase in the real CORTEX system and makes assumptions about wiring statuses and counts.