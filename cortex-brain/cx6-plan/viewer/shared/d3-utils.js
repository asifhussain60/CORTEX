/**
 * CORTEX 6.0 HTML Views - D3.js Utilities
 * ============================================================================
 * Shared D3.js helper functions and chart templates
 */

// Ensure D3 is loaded
async function ensureD3() {
  if (typeof d3 !== 'undefined') {
    return;
  }
  
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = 'https://d3js.org/d3.v7.min.js';
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('Failed to load D3.js'));
    document.head.appendChild(script);
  });
}

/**
 * Create a simple bar chart using D3
 */
async function createBarChart(containerId, data, options = {}) {
  await ensureD3();
  
  const {
    xKey = 'label',
    yKey = 'value',
    color = '#00d4ff',
    height = 400,
    margin = { top: 20, right: 30, bottom: 30, left: 60 }
  } = options;

  const container = document.getElementById(containerId);
  if (!container) return;

  const width = container.offsetWidth - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  // Clear previous content
  d3.select(`#${containerId}`).selectAll('*').remove();

  const svg = d3.select(`#${containerId}`)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`);

  const x = d3.scaleBand()
    .domain(data.map(d => d[xKey]))
    .range([0, width])
    .padding(0.1);

  const y = d3.scaleLinear()
    .domain([0, d3.max(data, d => d[yKey])])
    .range([innerHeight, 0]);

  // Draw bars
  svg.selectAll('.bar')
    .data(data)
    .enter()
    .append('rect')
    .attr('class', 'bar')
    .attr('x', d => x(d[xKey]))
    .attr('y', d => y(d[yKey]))
    .attr('width', x.bandwidth())
    .attr('height', d => innerHeight - y(d[yKey]))
    .style('fill', color)
    .style('opacity', 0.8)
    .on('mouseover', function() {
      d3.select(this).style('opacity', 1);
    })
    .on('mouseout', function() {
      d3.select(this).style('opacity', 0.8);
    });

  // X axis
  svg.append('g')
    .attr('transform', `translate(0,${innerHeight})`)
    .call(d3.axisBottom(x))
    .style('color', '#a0a0a0');

  // Y axis
  svg.append('g')
    .call(d3.axisLeft(y))
    .style('color', '#a0a0a0');
}

/**
 * Create a line chart using D3
 */
async function createLineChart(containerId, data, options = {}) {
  await ensureD3();
  
  const {
    xKey = 'date',
    yKey = 'value',
    color = '#00d4ff',
    height = 400,
    margin = { top: 20, right: 30, bottom: 30, left: 60 }
  } = options;

  const container = document.getElementById(containerId);
  if (!container) return;

  const width = container.offsetWidth - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  d3.select(`#${containerId}`).selectAll('*').remove();

  const svg = d3.select(`#${containerId}`)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`);

  const x = d3.scaleLinear()
    .domain(d3.extent(data, (d, i) => i))
    .range([0, width]);

  const y = d3.scaleLinear()
    .domain([0, d3.max(data, d => d[yKey])])
    .range([innerHeight, 0]);

  const line = d3.line()
    .x((d, i) => x(i))
    .y(d => y(d[yKey]));

  // Draw line
  svg.append('path')
    .datum(data)
    .attr('fill', 'none')
    .attr('stroke', color)
    .attr('stroke-width', 2)
    .attr('d', line);

  // X axis
  svg.append('g')
    .attr('transform', `translate(0,${innerHeight})`)
    .call(d3.axisBottom(x.domain([0, data.length - 1])))
    .style('color', '#a0a0a0');

  // Y axis
  svg.append('g')
    .call(d3.axisLeft(y))
    .style('color', '#a0a0a0');
}

/**
 * Create a force-directed graph
 */
async function createForceGraph(containerId, { nodes, links }, options = {}) {
  await ensureD3();
  
  const {
    height = 600,
    nodeColor = '#00d4ff',
    linkColor = '#1a1f3a',
    onNodeClick = null
  } = options;

  const container = document.getElementById(containerId);
  if (!container) return;

  const width = container.offsetWidth;

  d3.select(`#${containerId}`).selectAll('*').remove();

  const svg = d3.select(`#${containerId}`)
    .append('svg')
    .attr('width', width)
    .attr('height', height);

  const simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d => d.id).distance(80))
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(width / 2, height / 2));

  const link = svg.selectAll('line')
    .data(links)
    .enter()
    .append('line')
    .style('stroke', linkColor)
    .style('stroke-width', 2);

  const node = svg.selectAll('circle')
    .data(nodes)
    .enter()
    .append('circle')
    .attr('r', d => d.size || 5)
    .style('fill', d => d.color || nodeColor)
    .style('cursor', 'pointer')
    .call(d3.drag()
      .on('start', dragstarted)
      .on('drag', dragged)
      .on('end', dragended))
    .on('click', (event, d) => {
      if (onNodeClick) onNodeClick(d);
    });

  const label = svg.selectAll('text')
    .data(nodes)
    .enter()
    .append('text')
    .text(d => d.label || d.id)
    .style('font-size', '12px')
    .style('fill', '#e0e0e0')
    .style('pointer-events', 'none')
    .style('text-anchor', 'middle');

  simulation.on('tick', () => {
    link
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y);

    node
      .attr('cx', d => d.x)
      .attr('cy', d => d.y);

    label
      .attr('x', d => d.x)
      .attr('y', d => d.y - (d.size || 5) - 5);
  });

  function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  }

  function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
  }

  function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }
}

/**
 * Create a sunburst chart
 */
async function createSunburst(containerId, data, options = {}) {
  await ensureD3();
  
  const {
    height = 600,
    radius = 200
  } = options;

  const container = document.getElementById(containerId);
  if (!container) return;

  const width = container.offsetWidth;

  d3.select(`#${containerId}`).selectAll('*').remove();

  const svg = d3.select(`#${containerId}`)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${width / 2},${height / 2})`);

  const partition = d3.partition()
    .size([2 * Math.PI, radius]);

  const root = d3.hierarchy(data)
    .sum(d => d.value)
    .sort((a, b) => b.value - a.value);

  const arcs = partition(root);

  const arc = d3.arc()
    .startAngle(d => d.x0)
    .endAngle(d => d.x1)
    .innerRadius(d => d.y0)
    .outerRadius(d => d.y1);

  const color = d3.scaleOrdinal()
    .domain(['depth0', 'depth1', 'depth2'])
    .range(['#00d4ff', '#7b2cbf', '#ff006e']);

  svg.selectAll('path')
    .data(arcs.descendants().filter(d => d.depth > 0))
    .enter()
    .append('path')
    .attr('d', arc)
    .style('fill', (d, i) => {
      const colors = ['#00d4ff', '#7b2cbf', '#ff006e', '#06ffa5', '#ffbe0b'];
      return colors[i % colors.length];
    })
    .style('opacity', 0.8)
    .on('mouseover', function() {
      d3.select(this).style('opacity', 1);
    })
    .on('mouseout', function() {
      d3.select(this).style('opacity', 0.8);
    });

  svg.selectAll('text')
    .data(arcs.descendants().filter(d => d.depth > 0))
    .enter()
    .append('text')
    .attr('transform', d => `rotate(${(d.x0 + d.x1) / 2 * 180 / Math.PI - 90}) translate(${(d.y0 + d.y1) / 2})`)
    .attr('dy', '0.35em')
    .style('font-size', '11px')
    .style('fill', '#fff')
    .style('text-anchor', 'middle')
    .text(d => d.data.name);
}

/**
 * Create a heatmap using D3
 */
async function createHeatmap(containerId, data, options = {}) {
  await ensureD3();
  
  const {
    rows = [],
    columns = [],
    height = 400,
    margin = { top: 30, right: 30, bottom: 30, left: 100 }
  } = options;

  const container = document.getElementById(containerId);
  if (!container) return;

  const width = container.offsetWidth - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  d3.select(`#${containerId}`).selectAll('*').remove();

  const svg = d3.select(`#${containerId}`)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`);

  const cellSize = Math.min(
    width / columns.length,
    innerHeight / rows.length
  );

  const colorScale = d3.scaleLinear()
    .domain([0, 50, 100])
    .range(['#ff006e', '#ffbe0b', '#06ffa5']);

  // Create cells
  data.forEach((row, i) => {
    row.forEach((value, j) => {
      svg.append('rect')
        .attr('x', j * cellSize)
        .attr('y', i * cellSize)
        .attr('width', cellSize)
        .attr('height', cellSize)
        .style('fill', colorScale(value))
        .style('stroke', '#1a1f3a')
        .style('stroke-width', 1);

      svg.append('text')
        .attr('x', j * cellSize + cellSize / 2)
        .attr('y', i * cellSize + cellSize / 2)
        .attr('dy', '0.35em')
        .style('text-anchor', 'middle')
        .style('fill', '#fff')
        .style('font-size', '12px')
        .style('font-weight', '700')
        .text(`${Math.round(value)}%`);
    });
  });

  // Add row labels
  svg.selectAll('.row-label')
    .data(rows)
    .enter()
    .append('text')
    .attr('class', 'row-label')
    .attr('x', -10)
    .attr('y', (d, i) => i * cellSize + cellSize / 2)
    .attr('dy', '0.35em')
    .style('text-anchor', 'end')
    .style('fill', '#a0a0a0')
    .style('font-size', '12px')
    .text(d => d);

  // Add column labels
  svg.selectAll('.col-label')
    .data(columns)
    .enter()
    .append('text')
    .attr('class', 'col-label')
    .attr('x', (d, i) => i * cellSize + cellSize / 2)
    .attr('y', -10)
    .attr('dy', '0.35em')
    .style('text-anchor', 'middle')
    .style('fill', '#a0a0a0')
    .style('font-size', '12px')
    .text(d => d);
}

/**
 * Create a simple tree layout
 */
async function createTree(containerId, data, options = {}) {
  await ensureD3();
  
  const {
    height = 600,
    onNodeClick = null
  } = options;

  const container = document.getElementById(containerId);
  if (!container) return;

  const width = container.offsetWidth;
  const margin = { top: 20, right: 120, bottom: 20, left: 120 };
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  d3.select(`#${containerId}`).selectAll('*').remove();

  const svg = d3.select(`#${containerId}`)
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`);

  const tree = d3.tree().size([innerHeight, innerWidth]);
  const hierarchy = d3.hierarchy(data);
  const root = tree(hierarchy);

  // Links
  svg.selectAll('path.link')
    .data(root.links())
    .enter()
    .append('path')
    .attr('class', 'link')
    .attr('d', d3.linkHorizontal()
      .x(d => d.y)
      .y(d => d.x))
    .style('fill', 'none')
    .style('stroke', '#1a1f3a')
    .style('stroke-width', 2);

  // Nodes
  const nodeGroup = svg.selectAll('g.node')
    .data(root.descendants())
    .enter()
    .append('g')
    .attr('class', 'node')
    .attr('transform', d => `translate(${d.y},${d.x})`)
    .style('cursor', 'pointer')
    .on('click', (event, d) => {
      if (onNodeClick) onNodeClick(d);
    });

  nodeGroup.append('circle')
    .attr('r', 5)
    .style('fill', '#00d4ff')
    .style('stroke', '#fff')
    .style('stroke-width', 2);

  nodeGroup.append('text')
    .attr('dy', '0.35em')
    .attr('x', d => d.children ? -10 : 10)
    .style('text-anchor', d => d.children ? 'end' : 'start')
    .style('fill', '#e0e0e0')
    .style('font-size', '12px')
    .text(d => d.data.name);
}

/**
 * Create gauge/speedometer chart
 */
async function createGauge(containerId, value, max = 100, options = {}) {
  const {
    size = 200,
    color = '#00d4ff'
  } = options;

  const container = document.getElementById(containerId);
  if (!container) return;

  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', `0 0 ${size} ${size}`);
  svg.setAttribute('width', size);
  svg.setAttribute('height', size);

  const radius = size / 2 - 20;
  const angle = (value / max) * 180;

  // Background arc
  const bgPath = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
  bgPath.setAttribute('cx', size / 2);
  bgPath.setAttribute('cy', size / 2);
  bgPath.setAttribute('r', radius);
  bgPath.setAttribute('fill', 'none');
  bgPath.setAttribute('stroke', '#1a1f3a');
  bgPath.setAttribute('stroke-width', '10');
  svg.appendChild(bgPath);

  // Value arc
  const valuePath = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
  valuePath.setAttribute('cx', size / 2);
  valuePath.setAttribute('cy', size / 2);
  valuePath.setAttribute('r', radius);
  valuePath.setAttribute('fill', 'none');
  valuePath.setAttribute('stroke', color);
  valuePath.setAttribute('stroke-width', '10');
  valuePath.setAttribute('stroke-dasharray', `${(angle / 180) * Math.PI * radius * 2} ${Math.PI * radius * 2}`);
  valuePath.setAttribute('stroke-dashoffset', `${(Math.PI * radius)}`);
  svg.appendChild(valuePath);

  // Text
  const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
  text.setAttribute('x', size / 2);
  text.setAttribute('y', size / 2);
  text.setAttribute('text-anchor', 'middle');
  text.setAttribute('dy', '0.35em');
  text.setAttribute('fill', '#e0e0e0');
  text.setAttribute('font-size', '48');
  text.setAttribute('font-weight', '700');
  text.textContent = `${Math.round(value)}`;
  svg.appendChild(text);

  container.innerHTML = '';
  container.appendChild(svg);
}
