# 🎨 D3.js Visualization Templates

**Purpose:** Reusable D3.js templates with glassmorphism styling

---

## Template 1: Force-Directed Graph (Knowledge Graph)

```javascript
// Force-directed graph with glass nodes
function createKnowledgeGraph(container, data) {
    const width = 800;
    const height = 600;
    
    const svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .attr('class', 'glass-optimized');
    
    // Glass filter definition
    const defs = svg.append('defs');
    const filter = defs.append('filter')
        .attr('id', 'glass-blur')
        .attr('x', '-50%')
        .attr('y', '-50%')
        .attr('width', '200%')
        .attr('height', '200%');
    
    filter.append('feGaussianBlur')
        .attr('in', 'SourceGraphic')
        .attr('stdDeviation', '2');
    
    // Simulation
    const simulation = d3.forceSimulation(data.nodes)
        .force('link', d3.forceLink(data.links).id(d => d.id))
        .force('charge', d3.forceManyBody().strength(-100))
        .force('center', d3.forceCenter(width / 2, height / 2));
    
    // Links with gradient
    const link = svg.append('g')
        .selectAll('line')
        .data(data.links)
        .join('line')
        .attr('stroke', 'rgba(0, 212, 255, 0.3)')
        .attr('stroke-width', d => Math.sqrt(d.weight) * 2);
    
    // Nodes with liquid blob effect
    const node = svg.append('g')
        .selectAll('circle')
        .data(data.nodes)
        .join('circle')
        .attr('r', d => d.size || 8)
        .attr('class', 'magnetic-glass')
        .style('fill', 'var(--glass-bg)')
        .style('stroke', 'var(--accent-primary)')
        .style('stroke-width', '2')
        .style('filter', 'url(#glass-blur)')
        .call(drag(simulation));
    
    // Hebbian learning animation
    node.on('mouseover', function(event, d) {
        d3.select(this)
            .transition()
            .duration(200)
            .attr('r', d.size * 1.5)
            .style('box-shadow', '0 0 20px var(--accent-primary)');
    });
    
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        node
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
    });
    
    function drag(simulation) {
        return d3.drag()
            .on('start', (event, d) => {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            })
            .on('drag', (event, d) => {
                d.fx = event.x;
                d.fy = event.y;
            })
            .on('end', (event, d) => {
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            });
    }
}
```

---

## Template 2: Concentric Rings (SKULL Protection)

```javascript
// 8-layer concentric shield visualization
function createConcentricShield(container, layers) {
    const width = 600;
    const height = 600;
    const centerX = width / 2;
    const centerY = height / 2;
    
    const svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .attr('class', 'glass-optimized');
    
    const layerColors = [
        '#ffd700', // Layer 1: Gold (Document Org)
        '#00d4ff', // Layer 2: Cyan
        '#7b61ff', // Layer 3: Purple
        '#00ff88', // Layer 4: Green
        '#ff6b6b', // Layer 5: Red
        '#ffa500', // Layer 6: Orange
        '#00d4ff', // Layer 7: Cyan
        '#7b61ff'  // Layer 8: Purple
    ];
    
    const maxRadius = Math.min(width, height) / 2 - 20;
    const radiusStep = maxRadius / layers.length;
    
    // Draw layers from outside to inside
    layers.reverse().forEach((layer, i) => {
        const radius = maxRadius - (i * radiusStep);
        
        // Ring
        svg.append('circle')
            .attr('cx', centerX)
            .attr('cy', centerY)
            .attr('r', radius)
            .attr('fill', 'none')
            .attr('stroke', layerColors[i])
            .attr('stroke-width', radiusStep - 5)
            .attr('stroke-opacity', 0.3)
            .attr('class', 'pulse-glow-glass')
            .style('filter', 'blur(2px)');
        
        // Layer label
        svg.append('text')
            .attr('x', centerX)
            .attr('y', centerY - radius + radiusStep / 2)
            .attr('text-anchor', 'middle')
            .attr('fill', layerColors[i])
            .attr('font-size', '12px')
            .text(layer.name);
    });
    
    // Animated threat pulse
    function pulseLayer(layerIndex) {
        svg.selectAll('circle')
            .filter((d, i) => i === layerIndex)
            .transition()
            .duration(500)
            .attr('stroke-opacity', 1)
            .transition()
            .duration(500)
            .attr('stroke-opacity', 0.3);
    }
    
    return { pulseLayer };
}
```

---

## Template 3: Thermal Heatmap Treemap

```javascript
// Code thermal zones visualization
function createThermalHeatmap(container, data) {
    const width = 800;
    const height = 500;
    
    const svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .attr('class', 'glass-optimized');
    
    // Temperature color scale
    const colorScale = d3.scaleLinear()
        .domain([0, 50, 80, 100])
        .range(['#00ff88', '#ffd700', '#ff6b6b', '#ff0000']);
    
    const treemap = d3.treemap()
        .size([width, height])
        .padding(2);
    
    const root = d3.hierarchy(data)
        .sum(d => d.commits)
        .sort((a, b) => b.value - a.value);
    
    treemap(root);
    
    // Cells with glass effect
    const cell = svg.selectAll('g')
        .data(root.leaves())
        .join('g')
        .attr('transform', d => `translate(${d.x0},${d.y0})`);
    
    cell.append('rect')
        .attr('width', d => d.x1 - d.x0)
        .attr('height', d => d.y1 - d.y0)
        .attr('fill', d => colorScale(d.data.temperature))
        .attr('fill-opacity', 0.7)
        .attr('stroke', 'rgba(255, 255, 255, 0.2)')
        .attr('rx', 4)
        .attr('class', 'morph-card')
        .on('mouseover', function() {
            d3.select(this)
                .transition()
                .duration(200)
                .attr('fill-opacity', 1);
        })
        .on('mouseout', function() {
            d3.select(this)
                .transition()
                .duration(200)
                .attr('fill-opacity', 0.7);
        });
    
    // Labels
    cell.append('text')
        .attr('x', 5)
        .attr('y', 15)
        .attr('fill', 'white')
        .attr('font-size', '10px')
        .text(d => d.data.name)
        .attr('clip-path', d => `inset(0 ${d.x1 - d.x0 - 10}px 0 0)`);
}
```

---

## Template 4: TDD Cycle Animated Ring

```javascript
// RED-GREEN-REFACTOR cycle visualization
function createTDDCycleRing(container) {
    const width = 400;
    const height = 400;
    const radius = 150;
    
    const svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .attr('class', 'glass-optimized');
    
    const g = svg.append('g')
        .attr('transform', `translate(${width/2},${height/2})`);
    
    const phases = [
        { name: 'RED', color: '#ff6b6b', angle: 0 },
        { name: 'GREEN', color: '#00ff88', angle: 120 },
        { name: 'REFACTOR', color: '#00d4ff', angle: 240 }
    ];
    
    const arc = d3.arc()
        .innerRadius(radius - 40)
        .outerRadius(radius)
        .startAngle(d => d.angle * Math.PI / 180)
        .endAngle(d => (d.angle + 110) * Math.PI / 180);
    
    // Phase arcs
    g.selectAll('path')
        .data(phases)
        .join('path')
        .attr('d', arc)
        .attr('fill', d => d.color)
        .attr('fill-opacity', 0.6)
        .attr('class', 'pulse-glow-glass')
        .style('filter', 'blur(1px)');
    
    // Phase labels
    phases.forEach(phase => {
        const angle = (phase.angle + 55) * Math.PI / 180;
        const x = Math.sin(angle) * (radius - 20);
        const y = -Math.cos(angle) * (radius - 20);
        
        g.append('text')
            .attr('x', x)
            .attr('y', y)
            .attr('text-anchor', 'middle')
            .attr('fill', phase.color)
            .attr('font-weight', 'bold')
            .text(phase.name);
    });
    
    // Animated progress indicator
    const progressArc = d3.arc()
        .innerRadius(radius - 50)
        .outerRadius(radius - 45)
        .startAngle(0);
    
    const progress = g.append('path')
        .datum({ endAngle: 0 })
        .attr('d', progressArc)
        .attr('fill', 'white');
    
    function animateToPhase(phaseIndex) {
        const targetAngle = phases[phaseIndex].angle * Math.PI / 180;
        progress.transition()
            .duration(1000)
            .attrTween('d', () => {
                const interpolate = d3.interpolate(progress.datum().endAngle, targetAngle);
                return t => {
                    progress.datum().endAngle = interpolate(t);
                    return progressArc(progress.datum());
                };
            });
    }
    
    return { animateToPhase };
}
```

---

## Usage Notes

1. Include D3.js v7: `<script src="https://d3js.org/d3.v7.min.js"></script>`
2. Apply `.glass-optimized` class for GPU acceleration
3. Use CSS variables from glassmorphism standard
4. Add reduced-motion support for animations
