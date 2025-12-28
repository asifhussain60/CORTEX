/**
 * CORTEX Interactive Roadmap Visualization
 * D3.js-based timeline showing milestones, features, and projections
 */

class RoadmapVisualization {
    constructor() {
        this.data = null;
        this.svg = null;
        this.zoom = 1;
        this.currentView = 'timeline';
        this.margin = { top: 60, right: 60, bottom: 100, left: 100 };
        this.tooltip = document.getElementById('timeline-tooltip');
        
        this.init();
    }
    
    async init() {
        await this.loadData();
        this.setupControls();
        this.renderMetrics();
        this.renderTimeline();
    }
    
    async loadData() {
        try {
            const response = await fetch('../assets/data/roadmap-data.json');
            this.data = await response.json();
            console.log('Roadmap data loaded:', this.data);
        } catch (error) {
            console.error('Error loading roadmap data:', error);
            this.data = this.getMockData();
        }
    }
    
    getMockData() {
        // Fallback mock data if JSON fails to load
        return {
            velocity: {
                features_per_month: 15.5,
                commits_per_week: 42.3,
                avg_features_per_sprint: 7.75,
                analysis_period_days: 90
            },
            timeline: [
                {
                    milestone: 'CORTEX 3.1',
                    target_quarter: 'Q1 2026',
                    projected_date: '2026-03-01',
                    confidence_range: { early: '2026-02-01', late: '2026-04-01' },
                    key_features: ['Natural Language Evolution', 'Enhanced Context Awareness']
                },
                {
                    milestone: 'CORTEX 3.2',
                    target_quarter: 'Q2 2026',
                    projected_date: '2026-06-01',
                    confidence_range: { early: '2026-05-01', late: '2026-07-01' },
                    key_features: ['Self-Optimizing Operations', 'Performance Analytics']
                },
                {
                    milestone: 'CORTEX 4.0',
                    target_quarter: 'Q4 2026',
                    projected_date: '2026-12-01',
                    confidence_range: { early: '2026-11-01', late: '2027-01-01' },
                    key_features: ['Multi-Model Support', 'Cloud-Native Deployment', 'Enterprise Security']
                }
            ],
            priorities: [
                { goal: 'Natural Language Evolution', priority: 'HIGH', category: 'AI-first' },
                { goal: 'Self-Optimizing Operations', priority: 'HIGH', category: 'AI-first' },
                { goal: 'Multi-Model Support', priority: 'MEDIUM', category: 'Cloud-native' },
                { goal: 'Cloud Deployment', priority: 'MEDIUM', category: 'Collaboration' },
                { goal: 'Enterprise Security', priority: 'LOW', category: 'Security' },
                { goal: 'Plugin Marketplace', priority: 'LOW', category: 'Community' }
            ]
        };
    }
    
    setupControls() {
        // View controls
        document.querySelectorAll('.control-btn[data-view]').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.control-btn[data-view]').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.currentView = btn.dataset.view;
                this.renderTimeline();
            });
        });
        
        // Zoom controls
        document.querySelectorAll('.control-btn[data-zoom]').forEach(btn => {
            btn.addEventListener('click', () => {
                if (btn.dataset.zoom === 'in') {
                    this.zoom = Math.min(this.zoom * 1.2, 3);
                } else {
                    this.zoom = Math.max(this.zoom / 1.2, 0.5);
                }
                this.renderTimeline();
            });
        });
        
        // Reset control
        document.querySelector('.control-btn[data-action="reset"]').addEventListener('click', () => {
            this.zoom = 1;
            this.renderTimeline();
        });
    }
    
    renderMetrics() {
        const velocity = this.data.velocity;
        
        document.getElementById('features-per-month').textContent = velocity.features_per_month.toFixed(1);
        document.getElementById('commits-per-week').textContent = velocity.commits_per_week.toFixed(1);
        document.getElementById('features-per-sprint').textContent = velocity.avg_features_per_sprint.toFixed(1);
        document.getElementById('analysis-days').textContent = velocity.analysis_period_days;
    }
    
    renderTimeline() {
        // Clear existing SVG
        d3.select('#timeline-svg').selectAll('*').remove();
        
        const container = document.getElementById('timeline-svg');
        const width = container.clientWidth;
        const height = container.clientHeight;
        
        this.svg = d3.select('#timeline-svg')
            .attr('viewBox', `0 0 ${width} ${height}`)
            .attr('preserveAspectRatio', 'xMidYMid meet');
        
        // Create main group with zoom
        const g = this.svg.append('g')
            .attr('transform', `translate(${this.margin.left}, ${this.margin.top}) scale(${this.zoom})`);
        
        const innerWidth = width - this.margin.left - this.margin.right;
        const innerHeight = height - this.margin.top - this.margin.bottom;
        
        // Parse dates
        const timeline = this.data.timeline.map(m => ({
            ...m,
            projectedDate: new Date(m.projected_date),
            earlyDate: new Date(m.confidence_range.early),
            lateDate: new Date(m.confidence_range.late)
        }));
        
        // Time scale
        const xScale = d3.scaleTime()
            .domain([
                d3.min(timeline, d => d.earlyDate),
                d3.max(timeline, d => d.lateDate)
            ])
            .range([0, innerWidth]);
        
        // Draw time axis
        const xAxis = d3.axisBottom(xScale)
            .ticks(6)
            .tickFormat(d3.timeFormat('%b %Y'));
        
        g.append('g')
            .attr('class', 'timeline-axis')
            .attr('transform', `translate(0, ${innerHeight - 50})`)
            .call(xAxis);
        
        // Draw milestones
        const milestoneY = innerHeight - 100;
        
        timeline.forEach((milestone, i) => {
            const x = xScale(milestone.projectedDate);
            
            // Confidence range
            if (this.currentView === 'timeline' || this.currentView === 'milestones') {
                g.append('rect')
                    .attr('class', 'confidence-range')
                    .attr('x', xScale(milestone.earlyDate))
                    .attr('y', milestoneY - 15)
                    .attr('width', xScale(milestone.lateDate) - xScale(milestone.earlyDate))
                    .attr('height', 30);
            }
            
            // Milestone marker
            const milestoneGroup = g.append('g')
                .attr('class', 'milestone-marker')
                .attr('transform', `translate(${x}, ${milestoneY})`)
                .on('mouseover', (event) => this.showTooltip(event, milestone))
                .on('mouseout', () => this.hideTooltip())
                .on('click', () => this.handleMilestoneClick(milestone));
            
            milestoneGroup.append('circle')
                .attr('class', 'milestone-circle')
                .attr('r', 12);
            
            milestoneGroup.append('text')
                .attr('class', 'milestone-label')
                .attr('y', -25)
                .text(milestone.milestone);
            
            milestoneGroup.append('text')
                .attr('class', 'milestone-date')
                .attr('y', -10)
                .text(milestone.target_quarter);
            
            // Draw features if in features view
            if (this.currentView === 'features' || this.currentView === 'timeline') {
                this.drawFeatures(g, milestone, x, milestoneY - 100, i);
            }
        });
        
        // Draw connecting line
        if (this.currentView === 'timeline' || this.currentView === 'milestones') {
            const line = d3.line()
                .x(d => xScale(d.projectedDate))
                .y(() => milestoneY);
            
            g.append('path')
                .datum(timeline)
                .attr('d', line)
                .attr('stroke', 'rgba(102, 126, 234, 0.3)')
                .attr('stroke-width', 2)
                .attr('fill', 'none');
        }
    }
    
    drawFeatures(g, milestone, x, baseY, milestoneIndex) {
        const priorities = this.data.priorities;
        const relevantPriorities = priorities.slice(milestoneIndex * 2, (milestoneIndex * 2) + 2);
        
        relevantPriorities.forEach((priority, i) => {
            const y = baseY - (i * 35);
            const barWidth = 80;
            const barHeight = 25;
            
            const featureGroup = g.append('g')
                .attr('class', `feature-bar ${priority.priority.toLowerCase()}-priority`)
                .attr('transform', `translate(${x - barWidth / 2}, ${y})`)
                .on('mouseover', (event) => this.showFeatureTooltip(event, priority))
                .on('mouseout', () => this.hideTooltip());
            
            featureGroup.append('rect')
                .attr('width', barWidth)
                .attr('height', barHeight)
                .attr('rx', 5)
                .attr('stroke-width', 2);
            
            featureGroup.append('text')
                .attr('x', barWidth / 2)
                .attr('y', barHeight / 2 + 5)
                .attr('text-anchor', 'middle')
                .attr('fill', 'white')
                .attr('font-size', '11px')
                .attr('font-weight', '600')
                .text(priority.priority);
        });
    }
    
    showTooltip(event, milestone) {
        const tooltipContent = `
            <div class="tooltip-title">${milestone.milestone}</div>
            <div class="tooltip-content">
                <div class="tooltip-metric">
                    <span class="tooltip-metric-label">Target:</span>
                    <span class="tooltip-metric-value">${milestone.target_quarter}</span>
                </div>
                <div class="tooltip-metric">
                    <span class="tooltip-metric-label">Projected:</span>
                    <span class="tooltip-metric-value">${new Date(milestone.projected_date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}</span>
                </div>
                <div class="tooltip-metric">
                    <span class="tooltip-metric-label">Confidence:</span>
                    <span class="tooltip-metric-value">±1 month</span>
                </div>
                ${milestone.key_features.length > 0 ? `
                    <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.1);">
                        <strong>Key Features:</strong><br>
                        ${milestone.key_features.slice(0, 3).map(f => `• ${f}`).join('<br>')}
                    </div>
                ` : ''}
            </div>
        `;
        
        this.tooltip.innerHTML = tooltipContent;
        this.tooltip.classList.add('visible');
        this.tooltip.style.left = (event.pageX + 15) + 'px';
        this.tooltip.style.top = (event.pageY - 15) + 'px';
    }
    
    showFeatureTooltip(event, priority) {
        const tooltipContent = `
            <div class="tooltip-title">${priority.goal}</div>
            <div class="tooltip-content">
                <div class="tooltip-metric">
                    <span class="tooltip-metric-label">Priority:</span>
                    <span class="tooltip-metric-value">${priority.priority}</span>
                </div>
                <div class="tooltip-metric">
                    <span class="tooltip-metric-label">Category:</span>
                    <span class="tooltip-metric-value">${priority.category}</span>
                </div>
                ${priority.dependencies && priority.dependencies.length > 0 ? `
                    <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.1);">
                        <strong>Dependencies:</strong><br>
                        ${priority.dependencies.slice(0, 2).map(d => `• ${d}`).join('<br>')}
                    </div>
                ` : ''}
            </div>
        `;
        
        this.tooltip.innerHTML = tooltipContent;
        this.tooltip.classList.add('visible');
        this.tooltip.style.left = (event.pageX + 15) + 'px';
        this.tooltip.style.top = (event.pageY - 15) + 'px';
    }
    
    hideTooltip() {
        this.tooltip.classList.remove('visible');
    }
    
    handleMilestoneClick(milestone) {
        console.log('Milestone clicked:', milestone);
        // Future: Navigate to milestone detail page
        // window.location.href = `milestone-${milestone.milestone.toLowerCase().replace(' ', '-')}.html`;
    }
}

// Initialize visualization when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new RoadmapVisualization();
});

// Handle window resize
let resizeTimeout;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        if (window.roadmapViz) {
            window.roadmapViz.renderTimeline();
        }
    }, 250);
});
