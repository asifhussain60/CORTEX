/**
 * Code Organization Tab Component
 * 
 * Renders code organization view with D3.js treemap heatmap and hotspots table.
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Source-Available (Use Allowed, No Contributions)
 */

import { showPanelSpinner } from '../shared-utils.js';

/**
 * Render code organization tab
 * @param {Object} data - Dashboard data containing code organization information
 */
export function renderCodeOrganization(data) {
    const container = document.getElementById('code-org-container');
    if (!container) {
        console.error('Code organization container not found');
        return;
    }
    
    // Show loading spinner
    showPanelSpinner(container, 'Analyzing code organization...');
    
    // Render after brief delay to show spinner
    setTimeout(() => {
        const codeOrg = data.codeOrganization || {};
        const summary = codeOrg.summary || {};
        const hotspots = codeOrg.hotspots || [];
        const fileComplexity = codeOrg.file_complexity || [];
        
        // Build HTML
        container.innerHTML = `
        <div class="view-header">
            <h2>📊 Code Organization & Hotspots</h2>
            <div class="header-actions">
                <button class="btn-secondary" onclick="exportHotspots()">Export Hotspots</button>
            </div>
        </div>

        <!-- Summary Cards -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
            <div class="glass-card" style="display: flex; align-items: center; gap: 1rem; padding: 1.5rem;">
                <div style="font-size: 2.5rem;">📁</div>
                <div>
                    <h3 style="font-size: 2rem; margin: 0; color: var(--accent-primary);">
                        ${summary.total_files || 0}
                    </h3>
                    <p style="margin: 0.25rem 0 0 0; color: var(--text-secondary);">Total Files</p>
                </div>
            </div>
            
            <div class="glass-card" style="display: flex; align-items: center; gap: 1rem; padding: 1.5rem;">
                <div style="font-size: 2.5rem;">⚠️</div>
                <div>
                    <h3 style="font-size: 2rem; margin: 0; color: var(--warning);">
                        ${summary.high_complexity_files || 0}
                    </h3>
                    <p style="margin: 0.25rem 0 0 0; color: var(--text-secondary);">High Complexity</p>
                </div>
            </div>
            
            <div class="glass-card" style="display: flex; align-items: center; gap: 1rem; padding: 1.5rem;">
                <div style="font-size: 2.5rem;">🔥</div>
                <div>
                    <h3 style="font-size: 2rem; margin: 0; color: var(--danger);">
                        ${summary.hotspot_count || 0}
                    </h3>
                    <p style="margin: 0.25rem 0 0 0; color: var(--text-secondary);">Hotspots</p>
                </div>
            </div>
            
            <div class="glass-card" style="display: flex; align-items: center; gap: 1rem; padding: 1.5rem;">
                <div style="font-size: 2.5rem;">📈</div>
                <div>
                    <h3 style="font-size: 2rem; margin: 0; color: var(--accent-primary);">
                        ${(summary.avg_complexity || 0).toFixed(1)}
                    </h3>
                    <p style="margin: 0.25rem 0 0 0; color: var(--text-secondary);">Avg Complexity</p>
                </div>
            </div>
        </div>

        <!-- Complexity Heatmap -->
        <div class="glass-card" style="margin-bottom: 2rem;">
            <h3 style="margin-bottom: 0.5rem;">🗺️ Complexity Heatmap</h3>
            <p style="color: var(--text-secondary); font-size: 0.875rem; margin-bottom: 1.5rem;">
                Files are sized by LOC and colored by complexity. Larger, redder files need attention.
            </p>
            <div id="complexity-heatmap" style="width: 100%; height: 600px;"></div>
            <div style="display: flex; align-items: center; justify-content: center; gap: 1rem; margin-top: 1.5rem;">
                <span style="color: var(--text-secondary); font-size: 0.875rem;">Low Complexity</span>
                <div style="
                    width: 200px;
                    height: 20px;
                    background: linear-gradient(90deg, #10b981, #f59e0b, #ef4444);
                    border-radius: 4px;
                "></div>
                <span style="color: var(--text-secondary); font-size: 0.875rem;">High Complexity</span>
            </div>
        </div>

        <!-- Hotspots Table -->
        <div class="glass-card">
            <h3 style="margin-bottom: 0.5rem;">🔥 Critical Hotspots</h3>
            <p style="color: var(--text-secondary); font-size: 0.875rem; margin-bottom: 1.5rem;">
                Files with high complexity and frequent changes - highest refactoring priority.
            </p>
            <div style="overflow-x: auto;">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="border-bottom: 1px solid var(--glass-border);">
                            <th style="padding: 1rem; text-align: left; color: var(--text-secondary); font-weight: 600;">File</th>
                            <th style="padding: 1rem; text-align: left; color: var(--text-secondary); font-weight: 600;">Risk Score</th>
                            <th style="padding: 1rem; text-align: left; color: var(--text-secondary); font-weight: 600;">Complexity</th>
                            <th style="padding: 1rem; text-align: left; color: var(--text-secondary); font-weight: 600;">Changes</th>
                            <th style="padding: 1rem; text-align: left; color: var(--text-secondary); font-weight: 600;">Recommendation</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${hotspots.map(hotspot => renderHotspotRow(hotspot)).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;
        
        // Initialize visualizations after DOM is updated
        setTimeout(() => {
            initComplexityHeatmap(fileComplexity);
        }, 100);
    }, 250);
}

/**
 * Render hotspot row
 * @param {Object} hotspot - Hotspot object
 * @returns {string} HTML string
 */
function renderHotspotRow(hotspot) {
    const riskScore = hotspot.risk_score || 0;
    let riskColor = 'var(--success)';
    let riskLabel = 'Medium';
    
    if (riskScore >= 80) {
        riskColor = 'var(--danger)';
        riskLabel = 'Critical';
    } else if (riskScore >= 60) {
        riskColor = 'var(--warning)';
        riskLabel = 'High';
    }
    
    return `
        <tr style="border-bottom: 1px solid var(--glass-border);">
            <td style="padding: 1rem; font-family: monospace; font-size: 0.875rem;">
                ${hotspot.file || 'Unknown'}
            </td>
            <td style="padding: 1rem;">
                <div style="
                    display: inline-block;
                    padding: 0.25rem 0.75rem;
                    border-radius: 12px;
                    font-size: 0.875rem;
                    font-weight: 600;
                    background: ${riskColor}22;
                    color: ${riskColor};
                ">
                    ${riskScore} - ${riskLabel}
                </div>
            </td>
            <td style="padding: 1rem; color: var(--text-secondary);">
                ${hotspot.complexity || 'N/A'}
            </td>
            <td style="padding: 1rem; color: var(--text-secondary);">
                ${hotspot.change_frequency || 0} commits
            </td>
            <td style="padding: 1rem; color: var(--text-secondary); font-size: 0.875rem;">
                ${hotspot.recommendation || 'Review recommended'}
            </td>
        </tr>
    `;
}

/**
 * Initialize complexity heatmap with D3.js treemap
 * @param {Array} fileComplexity - File complexity data
 */
function initComplexityHeatmap(fileComplexity) {
    // Check if D3 is available
    if (typeof d3 === 'undefined') {
        console.warn('D3.js not loaded, skipping heatmap visualization');
        return;
    }
    
    const container = document.getElementById('complexity-heatmap');
    if (!container) return;
    
    // Clear any existing content
    d3.select('#complexity-heatmap').selectAll('*').remove();
    
    if (!fileComplexity || fileComplexity.length === 0) {
        d3.select('#complexity-heatmap')
            .append('div')
            .style('text-align', 'center')
            .style('padding', '2rem')
            .style('color', 'var(--text-secondary)')
            .text('No complexity data available');
        return;
    }
    
    const width = container.clientWidth;
    const height = 600;
    
    // Prepare data for treemap
    const hierarchyData = {
        name: 'root',
        children: fileComplexity.slice(0, 50).map(file => ({
            name: file.file || 'Unknown',
            value: file.loc || 100,
            complexity: file.complexity || 0
        }))
    };
    
    const root = d3.hierarchy(hierarchyData)
        .sum(d => d.value)
        .sort((a, b) => b.value - a.value);
    
    const treemap = d3.treemap()
        .size([width, height])
        .padding(2);
    
    treemap(root);
    
    const svg = d3.select('#complexity-heatmap')
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    const colorScale = d3.scaleLinear()
        .domain([0, 50, 100])
        .range(['#10b981', '#f59e0b', '#ef4444']);
    
    const cell = svg.selectAll('g')
        .data(root.leaves())
        .enter()
        .append('g')
        .attr('transform', d => `translate(${d.x0},${d.y0})`);
    
    cell.append('rect')
        .attr('width', d => d.x1 - d.x0)
        .attr('height', d => d.y1 - d.y0)
        .attr('fill', d => colorScale(d.data.complexity))
        .attr('stroke', '#1a1f3a')
        .attr('stroke-width', 2)
        .style('opacity', 0.8)
        .on('mouseover', function(event, d) {
            d3.select(this).style('opacity', 1);
        })
        .on('mouseout', function(event, d) {
            d3.select(this).style('opacity', 0.8);
        });
    
    cell.append('text')
        .attr('x', 5)
        .attr('y', 20)
        .text(d => {
            const width = d.x1 - d.x0;
            const name = d.data.name.split('/').pop();
            return width > 80 ? name : '';
        })
        .attr('font-size', '12px')
        .attr('fill', '#ffffff')
        .style('pointer-events', 'none');
    
    cell.append('text')
        .attr('x', 5)
        .attr('y', 40)
        .text(d => {
            const width = d.x1 - d.x0;
            return width > 80 ? `Complexity: ${d.data.complexity}` : '';
        })
        .attr('font-size', '10px')
        .attr('fill', '#ffffff')
        .style('opacity', 0.8)
        .style('pointer-events', 'none');
}

/**
 * Export hotspots (placeholder)
 */
window.exportHotspots = function() {
    console.log('Export hotspots');
    alert('Hotspots export functionality coming soon!');
};
