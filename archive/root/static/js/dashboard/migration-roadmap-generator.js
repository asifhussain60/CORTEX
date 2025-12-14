/**
 * Migration Roadmap Generator Frontend
 * 
 * Purpose: Interactive D3.js timeline visualization of migration roadmap with:
 * - Timeline view showing phases and tasks
 * - Phase cards with effort estimates and task lists
 * - Markdown export functionality
 * - Priority-based color coding
 * 
 * Author: CORTEX Dashboard System
 * Version: 1.0.0
 * Created: December 6, 2025
 */

class MigrationRoadmapGenerator {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.roadmapData = null;
        this.selectedPhase = null;
        
        this.init();
    }
    
    init() {
        this.createLayout();
        this.loadRoadmap();
    }
    
    createLayout() {
        this.container.innerHTML = `
            <div class="roadmap-header">
                <h2>Migration Roadmap Generator</h2>
                <div class="roadmap-controls">
                    <button id="refreshRoadmap" class="btn-primary">Refresh Roadmap</button>
                    <button id="exportMarkdown" class="btn-secondary">Export to Markdown</button>
                </div>
            </div>
            
            <div class="roadmap-summary" id="roadmapSummary">
                <!-- Summary populated by renderSummary() -->
            </div>
            
            <div class="roadmap-timeline" id="roadmapTimeline">
                <!-- Timeline populated by renderTimeline() -->
            </div>
            
            <div class="roadmap-phases" id="roadmapPhases">
                <!-- Phase cards populated by renderPhases() -->
            </div>
        `;
        
        // Attach event listeners
        document.getElementById('refreshRoadmap').addEventListener('click', () => this.loadRoadmap());
        document.getElementById('exportMarkdown').addEventListener('click', () => this.exportToMarkdown());
    }
    
    async loadRoadmap() {
        try {
            const response = await fetch('/api/migration-roadmap');
            this.roadmapData = await response.json();
            
            this.renderSummary();
            this.renderTimeline();
            this.renderPhases();
        } catch (error) {
            console.error('Error loading roadmap:', error);
            this.showError('Failed to load migration roadmap');
        }
    }
    
    renderSummary() {
        if (!this.roadmapData || !this.roadmapData.summary) {
            return;
        }
        
        const summary = this.roadmapData.summary;
        const container = document.getElementById('roadmapSummary');
        
        container.innerHTML = `
            <div class="summary-grid">
                <div class="summary-card">
                    <div class="summary-value">${summary.total_migrations}</div>
                    <div class="summary-label">Total Migrations</div>
                </div>
                <div class="summary-card">
                    <div class="summary-value">${summary.total_effort_hours}h</div>
                    <div class="summary-label">${summary.estimated_duration_weeks} weeks</div>
                </div>
                <div class="summary-card">
                    <div class="summary-value">${summary.technologies_impacted}</div>
                    <div class="summary-label">Technologies</div>
                </div>
                <div class="summary-card">
                    <div class="summary-value">${summary.total_projects}</div>
                    <div class="summary-label">Projects Impacted</div>
                </div>
            </div>
            
            <div class="complexity-breakdown">
                <h3>Complexity Breakdown</h3>
                <div class="complexity-bars">
                    <div class="complexity-bar">
                        <div class="complexity-label">HIGH</div>
                        <div class="complexity-bar-fill high" style="width: ${this.calculatePercentage(summary.complexity_breakdown.HIGH, summary.total_migrations)}%"></div>
                        <div class="complexity-count">${summary.complexity_breakdown.HIGH}</div>
                    </div>
                    <div class="complexity-bar">
                        <div class="complexity-label">MEDIUM</div>
                        <div class="complexity-bar-fill medium" style="width: ${this.calculatePercentage(summary.complexity_breakdown.MEDIUM, summary.total_migrations)}%"></div>
                        <div class="complexity-count">${summary.complexity_breakdown.MEDIUM}</div>
                    </div>
                    <div class="complexity-bar">
                        <div class="complexity-label">LOW</div>
                        <div class="complexity-bar-fill low" style="width: ${this.calculatePercentage(summary.complexity_breakdown.LOW, summary.total_migrations)}%"></div>
                        <div class="complexity-count">${summary.complexity_breakdown.LOW}</div>
                    </div>
                </div>
            </div>
            
            <div class="highest-priority">
                <strong>Highest Priority:</strong> ${summary.highest_priority}
            </div>
        `;
    }
    
    renderTimeline() {
        if (!this.roadmapData || !this.roadmapData.phases) {
            return;
        }
        
        const container = document.getElementById('roadmapTimeline');
        const width = container.clientWidth - 40;
        const height = 200;
        const margin = { top: 20, right: 20, bottom: 30, left: 50 };
        
        // Clear existing content
        container.innerHTML = '';
        
        // Create SVG
        const svg = d3.select(container)
            .append('svg')
            .attr('width', width)
            .attr('height', height);
        
        const g = svg.append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);
        
        const chartWidth = width - margin.left - margin.right;
        const chartHeight = height - margin.top - margin.bottom;
        
        // Calculate cumulative weeks for x-axis
        const phases = this.roadmapData.phases.map((phase, idx) => {
            const startWeek = idx === 0 ? 0 : this.roadmapData.phases.slice(0, idx).reduce((sum, p) => sum + p.estimated_weeks, 0);
            return {
                ...phase,
                startWeek,
                endWeek: startWeek + phase.estimated_weeks
            };
        });
        
        const totalWeeks = phases[phases.length - 1].endWeek;
        
        // Scales
        const xScale = d3.scaleLinear()
            .domain([0, totalWeeks])
            .range([0, chartWidth]);
        
        const yScale = d3.scaleBand()
            .domain(phases.map(p => `Phase ${p.phase}`))
            .range([0, chartHeight])
            .padding(0.2);
        
        // X-axis
        g.append('g')
            .attr('transform', `translate(0,${chartHeight})`)
            .call(d3.axisBottom(xScale).ticks(10))
            .append('text')
            .attr('x', chartWidth / 2)
            .attr('y', 25)
            .attr('fill', '#000')
            .attr('text-anchor', 'middle')
            .text('Weeks');
        
        // Y-axis
        g.append('g')
            .call(d3.axisLeft(yScale));
        
        // Timeline bars
        const bars = g.selectAll('.timeline-bar')
            .data(phases)
            .enter()
            .append('g')
            .attr('class', 'timeline-bar-group')
            .style('cursor', 'pointer')
            .on('click', (event, d) => this.selectPhase(d.phase));
        
        bars.append('rect')
            .attr('class', 'timeline-bar')
            .attr('x', d => xScale(d.startWeek))
            .attr('y', d => yScale(`Phase ${d.phase}`))
            .attr('width', d => xScale(d.endWeek) - xScale(d.startWeek))
            .attr('height', yScale.bandwidth())
            .attr('fill', d => this.getComplexityColor(d))
            .attr('stroke', '#333')
            .attr('stroke-width', 1);
        
        // Bar labels (effort hours)
        bars.append('text')
            .attr('x', d => xScale(d.startWeek) + (xScale(d.endWeek) - xScale(d.startWeek)) / 2)
            .attr('y', d => yScale(`Phase ${d.phase}`) + yScale.bandwidth() / 2)
            .attr('text-anchor', 'middle')
            .attr('dominant-baseline', 'middle')
            .attr('fill', '#fff')
            .attr('font-size', '12px')
            .text(d => `${d.total_effort_hours}h`);
        
        // Tooltips
        bars.append('title')
            .text(d => `Phase ${d.phase}\n${d.total_effort_hours} hours (${d.estimated_weeks} weeks)\n${d.tasks.length} tasks`);
    }
    
    renderPhases() {
        if (!this.roadmapData || !this.roadmapData.phases) {
            return;
        }
        
        const container = document.getElementById('roadmapPhases');
        container.innerHTML = '';
        
        this.roadmapData.phases.forEach(phase => {
            const phaseCard = this.createPhaseCard(phase);
            container.appendChild(phaseCard);
        });
    }
    
    createPhaseCard(phase) {
        const card = document.createElement('div');
        card.className = `phase-card ${this.selectedPhase === phase.phase ? 'selected' : ''}`;
        card.onclick = () => this.selectPhase(phase.phase);
        
        // Phase header
        const header = document.createElement('div');
        header.className = 'phase-header';
        header.innerHTML = `
            <h3>Phase ${phase.phase}</h3>
            <div class="phase-effort">${phase.total_effort_hours}h (${phase.estimated_weeks} weeks)</div>
        `;
        card.appendChild(header);
        
        // Tasks table
        const tasksTable = document.createElement('div');
        tasksTable.className = 'phase-tasks';
        
        let tableHTML = `
            <table>
                <thead>
                    <tr>
                        <th>Technology</th>
                        <th>Migration</th>
                        <th>Projects</th>
                        <th>Effort</th>
                        <th>Complexity</th>
                        <th>Priority</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        phase.tasks.forEach(task => {
            const complexityClass = task.complexity.toLowerCase();
            const priorityClass = this.getPriorityClass(task.priority_score);
            
            tableHTML += `
                <tr>
                    <td>${task.technology} ${task.version}</td>
                    <td>${task.migration}</td>
                    <td>${task.project_count}</td>
                    <td>${task.effort_hours}h</td>
                    <td><span class="complexity-badge ${complexityClass}">${task.complexity}</span></td>
                    <td><span class="priority-badge ${priorityClass}">${task.priority_score}</span></td>
                </tr>
            `;
        });
        
        tableHTML += `
                </tbody>
            </table>
        `;
        
        tasksTable.innerHTML = tableHTML;
        card.appendChild(tasksTable);
        
        // Benefits section
        const benefitsSection = document.createElement('div');
        benefitsSection.className = 'phase-benefits';
        benefitsSection.innerHTML = '<h4>Key Benefits</h4>';
        
        phase.tasks.forEach(task => {
            const benefitsList = document.createElement('div');
            benefitsList.className = 'task-benefits';
            benefitsList.innerHTML = `<strong>${task.migration}:</strong>`;
            
            const ul = document.createElement('ul');
            task.benefits.forEach(benefit => {
                const li = document.createElement('li');
                li.textContent = benefit;
                ul.appendChild(li);
            });
            
            benefitsList.appendChild(ul);
            benefitsSection.appendChild(benefitsList);
        });
        
        card.appendChild(benefitsSection);
        
        return card;
    }
    
    selectPhase(phaseNum) {
        this.selectedPhase = this.selectedPhase === phaseNum ? null : phaseNum;
        this.renderPhases();
        
        // Scroll to phase card
        if (this.selectedPhase !== null) {
            const card = document.querySelector(`.phase-card.selected`);
            if (card) {
                card.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }
    }
    
    exportToMarkdown() {
        if (!this.roadmapData) {
            return;
        }
        
        let markdown = '# Migration Roadmap\n\n';
        markdown += `**Generated:** ${this.roadmapData.generated_date}\n\n`;
        
        // Summary
        const summary = this.roadmapData.summary;
        markdown += '## Summary\n\n';
        markdown += `- **Total Migrations:** ${summary.total_migrations}\n`;
        markdown += `- **Total Effort:** ${summary.total_effort_hours} hours (${summary.estimated_duration_weeks} weeks)\n`;
        markdown += `- **Technologies Impacted:** ${summary.technologies_impacted}\n`;
        markdown += `- **Total Projects:** ${summary.total_projects}\n`;
        markdown += `- **Highest Priority:** ${summary.highest_priority}\n\n`;
        
        // Complexity breakdown
        markdown += '**Complexity Breakdown:**\n\n';
        markdown += `- HIGH: ${summary.complexity_breakdown.HIGH} migrations\n`;
        markdown += `- MEDIUM: ${summary.complexity_breakdown.MEDIUM} migrations\n`;
        markdown += `- LOW: ${summary.complexity_breakdown.LOW} migrations\n\n`;
        
        // Phases
        this.roadmapData.phases.forEach(phase => {
            markdown += `## Phase ${phase.phase}\n\n`;
            markdown += `**Effort:** ${phase.total_effort_hours} hours (${phase.estimated_weeks} weeks)\n\n`;
            
            // Tasks table
            markdown += '| Technology | Migration | Projects | Effort | Complexity | Priority |\n';
            markdown += '|------------|-----------|----------|--------|------------|----------|\n';
            
            phase.tasks.forEach(task => {
                markdown += `| ${task.technology} ${task.version} | `;
                markdown += `${task.migration} | `;
                markdown += `${task.project_count} | `;
                markdown += `${task.effort_hours}h | `;
                markdown += `${task.complexity} | `;
                markdown += `${task.priority_score} |\n`;
            });
            
            markdown += '\n';
            
            // Benefits
            phase.tasks.forEach(task => {
                markdown += `### ${task.migration}\n\n`;
                markdown += '**Key Benefits:**\n\n';
                task.benefits.forEach(benefit => {
                    markdown += `- ${benefit}\n`;
                });
                markdown += '\n';
            });
        });
        
        // Download
        this.downloadMarkdown(markdown, 'migration_roadmap.md');
    }
    
    downloadMarkdown(content, filename) {
        const blob = new Blob([content], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
    
    // Helper methods
    
    calculatePercentage(value, total) {
        return total > 0 ? (value / total * 100).toFixed(1) : 0;
    }
    
    getComplexityColor(phase) {
        // Color based on dominant complexity in phase
        const high = phase.tasks.filter(t => t.complexity === 'HIGH').length;
        const medium = phase.tasks.filter(t => t.complexity === 'MEDIUM').length;
        const low = phase.tasks.filter(t => t.complexity === 'LOW').length;
        
        if (high > medium && high > low) {
            return '#dc3545'; // Red
        } else if (medium > low) {
            return '#ffc107'; // Yellow
        } else {
            return '#28a745'; // Green
        }
    }
    
    getPriorityClass(priority) {
        if (priority >= 70) return 'critical';
        if (priority >= 50) return 'high';
        if (priority >= 30) return 'medium';
        return 'low';
    }
    
    showError(message) {
        this.container.innerHTML = `
            <div class="error-message">
                <h3>Error</h3>
                <p>${message}</p>
            </div>
        `;
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    new MigrationRoadmapGenerator('migrationRoadmapContainer');
});
