/**
 * CORTEX UX Enhancement Dashboard - D3 Utilities
 * Reusable helper functions for D3.js visualizations
 */

const D3Utils = {
    /**
     * Create a color scale based on score value
     * @param {number} score - Score value (0-100)
     * @returns {string} - Color hex code
     */
    getScoreColor(score) {
        if (score >= 80) return '#10b981'; // Green
        if (score >= 60) return '#f59e0b'; // Yellow
        return '#ef4444'; // Red
    },

    /**
     * Format large numbers with K/M suffixes
     * @param {number} num - Number to format
     * @returns {string} - Formatted number
     */
    formatNumber(num) {
        if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
        if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
        return num.toString();
    },

    /**
     * Create tooltip element
     * @returns {d3.Selection} - Tooltip selection
     */
    createTooltip() {
        return d3.select('body')
            .append('div')
            .attr('class', 'tooltip')
            .style('position', 'absolute')
            .style('padding', '8px 12px')
            .style('background', 'rgba(0, 0, 0, 0.9)')
            .style('color', 'white')
            .style('border-radius', '4px')
            .style('font-size', '12px')
            .style('pointer-events', 'none')
            .style('z-index', '1000')
            .style('opacity', 0);
    },

    /**
     * Show tooltip at mouse position
     * @param {d3.Selection} tooltip - Tooltip selection
     * @param {string} content - HTML content for tooltip
     * @param {Event} event - Mouse event
     */
    showTooltip(tooltip, content, event) {
        tooltip
            .html(content)
            .style('opacity', 1)
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 28) + 'px');
    },

    /**
     * Hide tooltip
     * @param {d3.Selection} tooltip - Tooltip selection
     */
    hideTooltip(tooltip) {
        tooltip.style('opacity', 0);
    },

    /**
     * Create responsive SVG with proper margins
     * @param {string} containerId - ID of container element
     * @param {Object} dimensions - Width, height, margins
     * @returns {Object} - SVG selection and dimensions
     */
    createSVG(containerId, dimensions = {}) {
        const container = d3.select(`#${containerId}`);
        const containerWidth = container.node().getBoundingClientRect().width;
        
        const margin = dimensions.margin || { top: 20, right: 20, bottom: 40, left: 60 };
        const width = (dimensions.width || containerWidth) - margin.left - margin.right;
        const height = (dimensions.height || 400) - margin.top - margin.bottom;

        // Remove existing SVG if any
        container.selectAll('svg').remove();

        const svg = container
            .append('svg')
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom)
            .append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        return { svg, width, height, margin };
    },

    /**
     * Create legend for visualization
     * @param {d3.Selection} svg - SVG selection
     * @param {Array} items - Legend items [{label, color}]
     * @param {Object} position - {x, y} coordinates
     */
    createLegend(svg, items, position = { x: 0, y: 0 }) {
        const legend = svg.append('g')
            .attr('class', 'legend')
            .attr('transform', `translate(${position.x},${position.y})`);

        const legendItems = legend.selectAll('.legend-item')
            .data(items)
            .enter()
            .append('g')
            .attr('class', 'legend-item')
            .attr('transform', (d, i) => `translate(0,${i * 20})`);

        legendItems.append('rect')
            .attr('width', 15)
            .attr('height', 15)
            .attr('fill', d => d.color);

        legendItems.append('text')
            .attr('x', 20)
            .attr('y', 12)
            .style('font-size', '12px')
            .style('fill', 'var(--text-primary)')
            .text(d => d.label);
    },

    /**
     * Animate progress bar
     * @param {string} elementId - ID of progress bar element
     * @param {number} targetValue - Target percentage (0-100)
     * @param {number} duration - Animation duration in ms
     */
    animateProgressBar(elementId, targetValue, duration = 1000) {
        const element = document.getElementById(elementId);
        if (!element) return;

        let start = null;
        const startValue = 0;

        function animate(timestamp) {
            if (!start) start = timestamp;
            const progress = Math.min((timestamp - start) / duration, 1);
            const currentValue = startValue + (targetValue - startValue) * progress;
            
            element.style.width = currentValue + '%';
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        }

        requestAnimationFrame(animate);
    },

    /**
     * Update score display with color coding
     * @param {string} elementId - ID of score element
     * @param {number} score - Score value (0-100)
     * @param {string} suffix - Suffix to append (e.g., '%', '/100')
     */
    updateScore(elementId, score, suffix = '%') {
        const element = document.getElementById(elementId);
        if (!element) return;

        const color = this.getScoreColor(score);
        element.textContent = score + suffix;
        element.style.color = color;
    },

    /**
     * Create force-directed graph
     * @param {string} containerId - ID of container element
     * @param {Object} data - Graph data {nodes, links}
     * @param {Object} options - Configuration options
     */
    createForceGraph(containerId, data, options = {}) {
        const { svg, width, height } = this.createSVG(containerId, options.dimensions);
        const tooltip = this.createTooltip();

        const simulation = d3.forceSimulation(data.nodes)
            .force('link', d3.forceLink(data.links).id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2));

        const link = svg.append('g')
            .selectAll('line')
            .data(data.links)
            .enter()
            .append('line')
            .style('stroke', '#999')
            .style('stroke-width', 2);

        const node = svg.append('g')
            .selectAll('circle')
            .data(data.nodes)
            .enter()
            .append('circle')
            .attr('r', d => d.size || 10)
            .style('fill', d => d.color || '#3b82f6')
            .call(d3.drag()
                .on('start', dragstarted)
                .on('drag', dragged)
                .on('end', dragended))
            .on('mouseover', (event, d) => {
                this.showTooltip(tooltip, `<strong>${d.name}</strong><br>${d.description || ''}`, event);
            })
            .on('mouseout', () => this.hideTooltip(tooltip));

        const label = svg.append('g')
            .selectAll('text')
            .data(data.nodes)
            .enter()
            .append('text')
            .text(d => d.name)
            .style('font-size', '12px')
            .style('fill', 'var(--text-primary)')
            .attr('text-anchor', 'middle');

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
                .attr('y', d => d.y + 25);
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
    },

    /**
     * Create heatmap visualization
     * @param {string} containerId - ID of container element
     * @param {Array} data - Heatmap data [{x, y, value}]
     * @param {Object} options - Configuration options
     */
    createHeatmap(containerId, data, options = {}) {
        const { svg, width, height } = this.createSVG(containerId, options.dimensions);
        const tooltip = this.createTooltip();

        const xValues = [...new Set(data.map(d => d.x))];
        const yValues = [...new Set(data.map(d => d.y))];

        const xScale = d3.scaleBand()
            .domain(xValues)
            .range([0, width])
            .padding(0.05);

        const yScale = d3.scaleBand()
            .domain(yValues)
            .range([0, height])
            .padding(0.05);

        const colorScale = d3.scaleSequential()
            .domain([0, d3.max(data, d => d.value)])
            .interpolator(d3.interpolateRdYlGn);

        svg.selectAll('rect')
            .data(data)
            .enter()
            .append('rect')
            .attr('x', d => xScale(d.x))
            .attr('y', d => yScale(d.y))
            .attr('width', xScale.bandwidth())
            .attr('height', yScale.bandwidth())
            .style('fill', d => colorScale(d.value))
            .on('mouseover', (event, d) => {
                this.showTooltip(tooltip, `<strong>${d.x} - ${d.y}</strong><br>Value: ${d.value}`, event);
            })
            .on('mouseout', () => this.hideTooltip(tooltip));

        // Add axes
        svg.append('g')
            .attr('transform', `translate(0,${height})`)
            .call(d3.axisBottom(xScale));

        svg.append('g')
            .call(d3.axisLeft(yScale));
    },

    /**
     * Truncate text to fit width
     * @param {string} text - Text to truncate
     * @param {number} maxWidth - Maximum width in pixels
     * @returns {string} - Truncated text
     */
    truncateText(text, maxWidth) {
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        context.font = '12px sans-serif';
        
        if (context.measureText(text).width <= maxWidth) {
            return text;
        }
        
        let truncated = text;
        while (context.measureText(truncated + '...').width > maxWidth && truncated.length > 0) {
            truncated = truncated.slice(0, -1);
        }
        
        return truncated + '...';
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = D3Utils;
}
