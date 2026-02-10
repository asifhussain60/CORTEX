/*
 * Visualization helper functions for the CORTEX documentation site.
 * These functions use plain SVG and HTML to draw charts without external
 * dependencies. They are intentionally simple to ensure compatibility
 * with the file:// protocol and to avoid any network fetches.
 */

// Utility to clear a container and return a fresh element
function clearContainer(container) {
    while (container.firstChild) {
        container.removeChild(container.firstChild);
    }
}

// Draw a radial (pie) diagram for brain tiers
function drawRadialDiagram(container, tiers) {
    const width = 400;
    const height = 400;
    const cx = width / 2;
    const cy = height / 2;
    const radius = 150;
    const total = tiers.reduce((sum, t) => sum + t.count, 0);
    // Create SVG element
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', width);
    svg.setAttribute('height', height);
    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
    let startAngle = -Math.PI / 2;
    tiers.forEach((tier, index) => {
        const sliceAngle = (tier.count / total) * 2 * Math.PI;
        const endAngle = startAngle + sliceAngle;
        // Compute arc path
        const x1 = cx + radius * Math.cos(startAngle);
        const y1 = cy + radius * Math.sin(startAngle);
        const x2 = cx + radius * Math.cos(endAngle);
        const y2 = cy + radius * Math.sin(endAngle);
        const largeArcFlag = sliceAngle > Math.PI ? 1 : 0;
        const d = `M ${cx},${cy} L ${x1},${y1} A ${radius},${radius} 0 ${largeArcFlag} 1 ${x2},${y2} Z`;
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', d);
        // Color palette: vary hue
        const hue = (index * 80) % 360;
        path.setAttribute('fill', `hsl(${hue}, 60%, 50%)`);
        path.setAttribute('stroke', '#0a152b');
        path.setAttribute('stroke-width', '1');
        svg.appendChild(path);
        // Label
        const midAngle = startAngle + sliceAngle / 2;
        const lx = cx + (radius + 20) * Math.cos(midAngle);
        const ly = cy + (radius + 20) * Math.sin(midAngle);
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', lx);
        text.setAttribute('y', ly);
        text.setAttribute('fill', '#e2e8f0');
        text.setAttribute('font-size', '12');
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('dominant-baseline', 'middle');
        text.textContent = tier.id;
        svg.appendChild(text);
        startAngle = endAngle;
    });
    container.appendChild(svg);
}

// Draw a simple horizontal bar chart
function drawBarChart(container, data, opts = {}) {
    const width = opts.width || 500;
    const height = opts.height || 250;
    const barHeight = (height - 40) / data.length;
    const maxVal = Math.max(...data.map(d => d.percent || d.value));
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', width);
    svg.setAttribute('height', height);
    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
    // Draw bars
    data.forEach((item, i) => {
        const val = item.percent || item.value;
        const barWidth = (val / maxVal) * (width - 150);
        // Bar background
        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('x', 120);
        rect.setAttribute('y', 20 + i * barHeight);
        rect.setAttribute('width', barWidth);
        rect.setAttribute('height', barHeight - 8);
        rect.setAttribute('fill', 'rgba(66, 153, 225, 0.6)');
        svg.appendChild(rect);
        // Label
        const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        label.setAttribute('x', 10);
        label.setAttribute('y', 20 + i * barHeight + (barHeight - 8) / 2);
        label.setAttribute('fill', '#e2e8f0');
        label.setAttribute('font-size', '12');
        label.setAttribute('dominant-baseline', 'middle');
        label.textContent = item.layer || item.name;
        svg.appendChild(label);
        // Value
        const valueText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        valueText.setAttribute('x', 120 + barWidth + 5);
        valueText.setAttribute('y', 20 + i * barHeight + (barHeight - 8) / 2);
        valueText.setAttribute('fill', '#a0aec0');
        valueText.setAttribute('font-size', '12');
        valueText.setAttribute('dominant-baseline', 'middle');
        valueText.textContent = val + '%';
        svg.appendChild(valueText);
    });
    container.appendChild(svg);
}

// Draw a simple network diagram for orchestrators
function drawNetworkGraph(container, nodes) {
    const width = 500;
    const height = 500;
    const cx = width / 2;
    const cy = height / 2;
    const radius = 180;
    // Precompute positions evenly spaced on circle
    const angleStep = (2 * Math.PI) / nodes.length;
    nodes.forEach((node, i) => {
        node._x = cx + radius * Math.cos(i * angleStep - Math.PI / 2);
        node._y = cy + radius * Math.sin(i * angleStep - Math.PI / 2);
    });
    // Create SVG
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', width);
    svg.setAttribute('height', height);
    svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
    // Draw edges (dependencies)
    nodes.forEach(node => {
        (node.dependencies || []).forEach(depName => {
            const target = nodes.find(n => n.name === depName);
            if (!target) return;
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', node._x);
            line.setAttribute('y1', node._y);
            line.setAttribute('x2', target._x);
            line.setAttribute('y2', target._y);
            line.setAttribute('stroke', 'rgba(125, 146, 192, 0.6)');
            line.setAttribute('stroke-width', '1');
            svg.appendChild(line);
        });
    });
    // Draw nodes
    nodes.forEach(node => {
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', node._x);
        circle.setAttribute('cy', node._y);
        circle.setAttribute('r', 18);
        // colour by status
        let fill;
        switch (node.status) {
            case 'wired': fill = 'rgba(56, 161, 105, 0.8)'; break;
            case 'partial': fill = 'rgba(236, 201, 75, 0.8)'; break;
            case 'aspirational': fill = 'rgba(229, 62, 62, 0.8)'; break;
            default: fill = 'rgba(96, 125, 139, 0.8)';
        }
        circle.setAttribute('fill', fill);
        circle.setAttribute('stroke', '#0a152b');
        circle.setAttribute('stroke-width', '1');
        svg.appendChild(circle);
        // Label text
        const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        label.setAttribute('x', node._x);
        label.setAttribute('y', node._y + 30);
        label.setAttribute('fill', '#e2e8f0');
        label.setAttribute('font-size', '10');
        label.setAttribute('text-anchor', 'middle');
        label.textContent = node.id;
        svg.appendChild(label);
    });
    container.appendChild(svg);
}

// Render functions for each tab
function renderOverviewTab(container) {
    clearContainer(container);
    const card = document.createElement('div');
    card.className = 'card';
    const h = document.createElement('h2');
    h.textContent = 'What is CORTEX?';
    const p = document.createElement('p');
    p.textContent = 'CORTEX is an MCP-first development intelligence system with 24 orchestrators, 4 tiers of governance, and a Git-backed registry. It enforces definition of ready, automates planning, integrates context-aware intelligence, and manages execution through TDD loops.';
    card.appendChild(h);
    card.appendChild(p);
    container.appendChild(card);
    // Radial diagram for tiers
    const chartDiv = document.createElement('div');
    chartDiv.className = 'chart';
    container.appendChild(chartDiv);
    drawRadialDiagram(chartDiv, window.CORTEX_DATA.tiers);
    // Explanation list
    const list = document.createElement('ul');
    window.CORTEX_DATA.tiers.forEach(tier => {
        const li = document.createElement('li');
        li.innerHTML = `<strong>${tier.name}</strong>: ${tier.description}`;
        list.appendChild(li);
    });
    container.appendChild(list);
}

function renderCapabilitiesTab(container) {
    clearContainer(container);
    const heading = document.createElement('h2');
    heading.textContent = 'Capabilities';
    container.appendChild(heading);
    window.CORTEX_DATA.capabilities.forEach(cap => {
        const card = document.createElement('div');
        card.className = 'card';
        const h3 = document.createElement('h3');
        h3.textContent = cap.name;
        const p = document.createElement('p');
        p.textContent = cap.description;
        card.appendChild(h3);
        card.appendChild(p);
        container.appendChild(card);
    });
}

function renderArchitectureTab(container) {
    clearContainer(container);
    const heading = document.createElement('h2');
    heading.textContent = 'High-Level Architecture';
    container.appendChild(heading);
    const description = document.createElement('p');
    description.textContent = 'This diagram shows the core orchestrators and how they depend on one another.';
    container.appendChild(description);
    const chartDiv = document.createElement('div');
    chartDiv.className = 'chart';
    container.appendChild(chartDiv);
    drawNetworkGraph(chartDiv, window.CORTEX_DATA.wiringMatrix.map(entry => {
        return {
            id: entry.name.split(/(?=[A-Z])/).map(w => w[0]).join(''),
            name: entry.name,
            dependencies: entry.dependencies,
            status: entry.status
        };
    }));
}

function renderIntelligenceTab(container) {
    clearContainer(container);
    const heading = document.createElement('h2');
    heading.textContent = 'Intelligence & LENS';
    container.appendChild(heading);
    const p = document.createElement('p');
    p.textContent = 'CORTEX LENS aggregates context from your repositories, knowledge libraries and analyzers. It synthesises intelligence across turns, enabling the system to generate coherent, context‑aware responses. The unified intelligence provider accumulates signals across orchestrators.';
    container.appendChild(p);
    const sub = document.createElement('h3');
    sub.textContent = 'Intelligence Coverage Across Tiers';
    container.appendChild(sub);
    // Use bar chart to visualise intelligence coverage per tier (dummy values)
    const chartDiv = document.createElement('div');
    chartDiv.className = 'chart';
    container.appendChild(chartDiv);
    const coverage = window.CORTEX_DATA.tiers.map(tier => {
        // assume coverage increases with tier index
        return { name: tier.id, value: (tier.count % 10 + 1) * 5 };
    });
    drawBarChart(chartDiv, coverage, { width: 400, height: 200 });
    const note = document.createElement('p');
    note.textContent = 'Higher tiers provide richer domain knowledge and patterns.';
    container.appendChild(note);
}

function renderWiringTab(container) {
    clearContainer(container);
    const heading = document.createElement('h2');
    heading.textContent = 'Wiring & Registry';
    container.appendChild(heading);
    const description = document.createElement('p');
    description.textContent = 'This table summarises the wiring health of orchestrators and their dependencies.';
    container.appendChild(description);
    const table = document.createElement('table');
    table.style.width = '100%';
    table.style.borderCollapse = 'collapse';
    // header
    const thead = document.createElement('thead');
    const headRow = document.createElement('tr');
    ['Orchestrator','Dependencies','Status'].forEach(text => {
        const th = document.createElement('th');
        th.textContent = text;
        th.style.textAlign = 'left';
        th.style.padding = '0.5rem';
        th.style.borderBottom = '1px solid rgba(255,255,255,0.1)';
        headRow.appendChild(th);
    });
    thead.appendChild(headRow);
    table.appendChild(thead);
    // body
    const tbody = document.createElement('tbody');
    window.CORTEX_DATA.wiringMatrix.forEach(entry => {
        const tr = document.createElement('tr');
        const tdName = document.createElement('td');
        tdName.textContent = entry.name;
        tdName.style.padding = '0.5rem';
        const tdDep = document.createElement('td');
        tdDep.textContent = entry.dependencies.length > 0 ? entry.dependencies.join(', ') : 'None';
        tdDep.style.padding = '0.5rem';
        const tdStatus = document.createElement('td');
        tdStatus.textContent = entry.status;
        tdStatus.style.padding = '0.5rem';
        // colour-coded status
        if (entry.status === 'wired') tdStatus.style.color = '#38a169';
        if (entry.status === 'partial') tdStatus.style.color = '#ecc94b';
        if (entry.status === 'aspirational') tdStatus.style.color = '#e53e3e';
        tr.appendChild(tdName);
        tr.appendChild(tdDep);
        tr.appendChild(tdStatus);
        tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    container.appendChild(table);
}

function renderQualityTab(container) {
    clearContainer(container);
    const heading = document.createElement('h2');
    heading.textContent = 'Quality & Testing';
    container.appendChild(heading);
    const description = document.createElement('p');
    description.textContent = 'CORTEX emphasises test‑driven development (TDD) and continuous quality. The pyramid below illustrates the distribution of test types recommended.';
    container.appendChild(description);
    const chartDiv = document.createElement('div');
    chartDiv.className = 'chart';
    container.appendChild(chartDiv);
    drawBarChart(chartDiv, window.CORTEX_DATA.tests, { width: 400, height: 200 });
    const note = document.createElement('p');
    note.textContent = 'Unit tests form the base, complemented by integration and higher level tests.';
    container.appendChild(note);
}

function renderSecurityTab(container) {
    clearContainer(container);
    const heading = document.createElement('h2');
    heading.textContent = 'Security & Risk';
    container.appendChild(heading);
    const description = document.createElement('p');
    description.textContent = 'Security is baked into CORTEX from the ground up. The risk matrix below highlights key risk areas.';
    container.appendChild(description);
    // Table representing risks with severity and likelihood
    const table = document.createElement('table');
    table.style.width = '100%';
    table.style.borderCollapse = 'collapse';
    const head = document.createElement('thead');
    const hr = document.createElement('tr');
    ['Area','Severity','Likelihood','Description'].forEach(txt => {
        const th = document.createElement('th');
        th.textContent = txt;
        th.style.padding = '0.5rem';
        th.style.borderBottom = '1px solid rgba(255,255,255,0.1)';
        hr.appendChild(th);
    });
    head.appendChild(hr);
    table.appendChild(head);
    const body = document.createElement('tbody');
    window.CORTEX_DATA.risks.forEach(item => {
        const tr = document.createElement('tr');
        const tdArea = document.createElement('td'); tdArea.textContent = item.area; tdArea.style.padding = '0.5rem';
        const tdSev = document.createElement('td'); tdSev.textContent = item.severity; tdSev.style.padding = '0.5rem';
        const tdLik = document.createElement('td'); tdLik.textContent = item.likelihood; tdLik.style.padding = '0.5rem';
        const tdDesc = document.createElement('td'); tdDesc.textContent = item.description; tdDesc.style.padding = '0.5rem';
        tr.appendChild(tdArea);
        tr.appendChild(tdSev);
        tr.appendChild(tdLik);
        tr.appendChild(tdDesc);
        body.appendChild(tr);
    });
    table.appendChild(body);
    container.appendChild(table);
}

function renderOpsTab(container) {
    clearContainer(container);
    const heading = document.createElement('h2');
    heading.textContent = 'Ops & Deployment';
    container.appendChild(heading);
    const p = document.createElement('p');
    p.textContent = 'CORTEX assumes a Git-backed workspace with appropriate permissions and environment variables. Deployment requires verifying wiring, loading registry YAML, and ensuring all orchestrators are reachable in the container or CI environment. Observability is provided via logs and metrics.';
    container.appendChild(p);
    const checklist = document.createElement('ul');
    ['Use consistent file structure and environment variables.','Validate wiring YAML before runtime.','Ensure CI runners mount the repository correctly.','Collect metrics and logs for observability.','Pin template and schema versions to prevent drift.'].forEach(item => {
        const li = document.createElement('li'); li.textContent = item; checklist.appendChild(li);
    });
    container.appendChild(checklist);
}

function renderNextTab(container) {
    clearContainer(container);
    const heading = document.createElement('h2');
    heading.textContent = 'Next Steps';
    container.appendChild(heading);
    const p = document.createElement('p');
    p.textContent = 'Depending on your role, here are suggested next actions to continue your CORTEX journey.';
    container.appendChild(p);
    const lists = {
        leader: [
            'Review ROI and success stories.',
            'Allocate budget for phase completion and wiring enforcement.',
            'Align teams on governance and quality practices.'
        ],
        po: [
            'Define acceptance criteria for your backlog.',
            'Ensure each story meets definition of ready before planning.',
            'Collaborate with engineers to integrate LENS context.'
        ],
        manager: [
            'Audit wiring and registry health.',
            'Prioritise technical debt such as partial orchestrators.',
            'Set up continuous testing and observability.'
        ],
        engineer: [
            'Explore orchestrator code and templates.',
            'Write wiring and schema validation tests.',
            'Contribute to LENS analyzers and knowledge library.'
        ],
        quality: [
            'Design high‑value regression tests.',
            'Measure coverage across orchestrators.',
            'Automate TDD enforcement through pipelines.'
        ]
    };
    // Determine role from nav label (set by app.js)
    const roleKey = window.CORTEX_APP && window.CORTEX_APP.currentRole || 'leader';
    const ul = document.createElement('ul');
    lists[roleKey].forEach(item => {
        const li = document.createElement('li'); li.textContent = item; ul.appendChild(li);
    });
    container.appendChild(ul);
}

// Export renderers via global object for app.js to call
window.CORTEX_VIZ = {
    overview: renderOverviewTab,
    capabilities: renderCapabilitiesTab,
    architecture: renderArchitectureTab,
    intelligence: renderIntelligenceTab,
    wiring: renderWiringTab,
    quality: renderQualityTab,
    security: renderSecurityTab,
    ops: renderOpsTab,
    next: renderNextTab
};