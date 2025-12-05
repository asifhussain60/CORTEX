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

        <!-- Description Panel -->
        <div style="
            background: var(--glass-light);
            border: 1px solid var(--glass-border);
            border-left: 4px solid var(--accent-primary);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        ">
            <div style="display: flex; align-items: start; gap: 1rem;">
                <div style="font-size: 2rem; line-height: 1; opacity: 0.8;">💡</div>
                <div style="flex: 1;">
                    <div style="font-size: 0.95rem; color: var(--text-secondary); line-height: 1.6;">
                        Code organization metrics identify maintenance priorities.
                        <span style="color: var(--success); font-weight: 600;">✅ Low Complexity</span> files (&lt;20) are easy to maintain.
                        <span style="color: var(--warning); font-weight: 600;">⚠️ Medium Complexity</span> files (20-50) need monitoring.
                        <span style="color: var(--danger); font-weight: 600;">🔥 High Complexity</span> files (&gt;50) require urgent refactoring.
                        <strong>Hotspots</strong> combine high complexity with frequent changes, indicating technical debt accumulation.
                        <strong>Hover over heatmap cells and table rows</strong> for detailed analysis and recommendations.
                    </div>
                </div>
            </div>
        </div>

        <!-- How to Read Description -->
        <div class="glass-card" style="margin-bottom: 2rem; background: linear-gradient(135deg, var(--glass-light) 0%, var(--background-secondary) 100%);">
            <h3 style="margin-bottom: 1rem;">📊 Code Organization Insights</h3>
            <p style="color: var(--text-secondary); line-height: 1.6; margin-bottom: 1rem;">
                This analysis identifies code quality hotspots based on complexity and change frequency. 
                <strong style="color: var(--success);">🟢 Green areas</strong> are maintainable, 
                <strong style="color: var(--warning);">🟡 Yellow areas</strong> need monitoring, and 
                <strong style="color: var(--danger);">🔴 Red areas</strong> require immediate refactoring.
                <strong>Hover over heatmap cells or table rows</strong> to see detailed complexity metrics, LOC, change history, and specific refactoring recommendations.
            </p>
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
        <tr 
            style="
                border-bottom: 1px solid var(--glass-border);
                transition: all 0.2s;
                cursor: pointer;
            "
            onmouseover="showHotspotTooltip(event, ${JSON.stringify(hotspot).replace(/"/g, '&quot;')}, this); this.style.background='var(--glass-light)'"
            onmouseout="hideHotspotTooltip(this); this.style.background='transparent'"
        >
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
        .style('cursor', 'pointer')
        .on('mouseover', function(event, d) {
            d3.select(this).style('opacity', 1).attr('stroke-width', 3);
            showHeatmapTooltip(event, d.data);
        })
        .on('mouseout', function(event, d) {
            d3.select(this).style('opacity', 0.8).attr('stroke-width', 2);
            hideHeatmapTooltip();
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

/**
 * Show hotspot tooltip with detailed analysis
 * @param {Event} event - Mouse event
 * @param {Object} hotspot - Hotspot data
 * @param {HTMLElement} row - Table row element
 */
window.showHotspotTooltip = function(event, hotspot, row) {
    hideHotspotTooltip();
    
    const riskScore = hotspot.risk_score || 0;
    let riskColor = 'var(--success)';
    let riskLabel = 'Medium Risk';
    let riskIcon = '🟡';
    let actionPriority = 'Monitor';
    
    if (riskScore >= 80) {
        riskColor = 'var(--danger)';
        riskLabel = 'Critical Risk';
        riskIcon = '🔴';
        actionPriority = 'Immediate Refactoring Required';
    } else if (riskScore >= 60) {
        riskColor = 'var(--warning)';
        riskLabel = 'High Risk';
        riskIcon = '🟠';
        actionPriority = 'Schedule Refactoring Soon';
    } else {
        actionPriority = 'Monitor and Review Periodically';
    }
    
    const complexity = hotspot.complexity || 0;
    let complexityLevel = 'Low';
    if (complexity > 50) complexityLevel = 'Very High';
    else if (complexity > 30) complexityLevel = 'High';
    else if (complexity > 20) complexityLevel = 'Medium';
    
    const changeFreq = hotspot.change_frequency || 0;
    const fileName = hotspot.file ? hotspot.file.split('/').pop() : 'Unknown';
    
    const tooltip = document.createElement('div');
    tooltip.id = 'hotspot-tooltip';
    tooltip.innerHTML = `
        <div style="
            position: fixed;
            background: linear-gradient(135deg, var(--glass-dark) 0%, var(--background-primary) 100%);
            border: 2px solid ${riskColor};
            border-radius: 12px;
            padding: 1.25rem;
            max-width: 450px;
            box-shadow: 0 12px 40px rgba(0,0,0,0.4);
            z-index: 10000;
            animation: tooltipFadeIn 0.2s ease-out;
        ">
            <!-- Header -->
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem; padding-bottom: 0.75rem; border-bottom: 1px solid var(--glass-border);">
                <div style="font-size: 1.5rem;">${riskIcon}</div>
                <div style="flex: 1;">
                    <div style="font-weight: 600; font-size: 1.125rem; margin-bottom: 0.25rem;">${fileName}</div>
                    <div style="font-size: 0.75rem; color: var(--text-secondary); font-family: monospace; overflow: hidden; text-overflow: ellipsis;">${hotspot.file || 'Unknown path'}</div>
                </div>
                <div style="
                    padding: 0.375rem 0.75rem;
                    border-radius: 8px;
                    background: ${riskColor}22;
                    color: ${riskColor};
                    font-size: 0.75rem;
                    font-weight: 600;
                    white-space: nowrap;
                ">
                    ${riskLabel}
                </div>
            </div>
            
            <!-- Metrics Grid -->
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem; margin-bottom: 1rem;">
                <div style="background: var(--glass-light); border-radius: 8px; padding: 0.75rem; text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: 600; color: var(--accent-primary);">${riskScore}</div>
                    <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.25rem;">Risk Score</div>
                </div>
                <div style="background: var(--glass-light); border-radius: 8px; padding: 0.75rem; text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: 600; color: var(--warning);">${complexity}</div>
                    <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.25rem;">${complexityLevel}</div>
                </div>
                <div style="background: var(--glass-light); border-radius: 8px; padding: 0.75rem; text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: 600; color: var(--info);">${changeFreq}</div>
                    <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.25rem;">Commits</div>
                </div>
            </div>
            
            <!-- Analysis -->
            <div style="background: var(--glass-light); border-radius: 8px; padding: 0.75rem; margin-bottom: 0.75rem;">
                <div style="font-weight: 600; font-size: 0.875rem; margin-bottom: 0.5rem; color: var(--text-primary);">
                    📊 Analysis
                </div>
                <div style="font-size: 0.875rem; color: var(--text-secondary); line-height: 1.5;">
                    This file is a hotspot due to ${complexityLevel.toLowerCase()} complexity (${complexity}) 
                    combined with ${changeFreq} recent changes. Files that change frequently and have high 
                    complexity accumulate technical debt rapidly and are prone to bugs.
                </div>
            </div>
            
            <!-- Recommendation -->
            <div style="
                background: ${riskScore >= 80 ? 'var(--danger)22' : riskScore >= 60 ? 'var(--warning)22' : 'var(--info)22'};
                border: 1px solid ${riskColor};
                border-radius: 8px;
                padding: 0.75rem;
            ">
                <div style="font-weight: 600; font-size: 0.875rem; margin-bottom: 0.5rem; color: ${riskColor};">
                    💡 ${actionPriority}
                </div>
                <div style="font-size: 0.875rem; color: var(--text-secondary); line-height: 1.5;">
                    ${hotspot.recommendation || 'Break down this file into smaller, focused modules. Extract reusable logic into separate functions. Add comprehensive unit tests before refactoring.'}
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(tooltip);
    
    // Position tooltip
    const tooltipRect = tooltip.firstElementChild.getBoundingClientRect();
    const rowRect = row.getBoundingClientRect();
    
    let left = rowRect.right + 10;
    let top = rowRect.top;
    
    if (left + tooltipRect.width > window.innerWidth) {
        left = rowRect.left - tooltipRect.width - 10;
    }
    
    if (top + tooltipRect.height > window.innerHeight) {
        top = window.innerHeight - tooltipRect.height - 10;
    }
    
    if (top < 10) top = 10;
    
    tooltip.firstElementChild.style.left = `${left}px`;
    tooltip.firstElementChild.style.top = `${top}px`;
};

/**
 * Hide hotspot tooltip
 * @param {HTMLElement} row - Table row element
 */
window.hideHotspotTooltip = function(row) {
    const tooltip = document.getElementById('hotspot-tooltip');
    if (tooltip) tooltip.remove();
};

/**
 * Show heatmap cell tooltip
 * @param {Event} event - Mouse event
 * @param {Object} data - Cell data
 */
window.showHeatmapTooltip = function(event, data) {
    hideHeatmapTooltip();
    
    const complexity = data.complexity || 0;
    let complexityColor = 'var(--success)';
    let complexityLabel = 'Low Complexity';
    let complexityIcon = '✅';
    
    if (complexity > 50) {
        complexityColor = 'var(--danger)';
        complexityLabel = 'Very High Complexity';
        complexityIcon = '🔥';
    } else if (complexity > 30) {
        complexityColor = 'var(--warning)';
        complexityLabel = 'High Complexity';
        complexityIcon = '⚠️';
    } else if (complexity > 20) {
        complexityColor = 'var(--info)';
        complexityLabel = 'Medium Complexity';
        complexityIcon = 'ℹ️';
    }
    
    const fileName = data.name.split('/').pop();
    const loc = data.value || 0;
    
    const tooltip = document.createElement('div');
    tooltip.id = 'heatmap-tooltip';
    tooltip.innerHTML = `
        <div style="
            position: fixed;
            background: linear-gradient(135deg, var(--glass-dark) 0%, var(--background-primary) 100%);
            border: 2px solid ${complexityColor};
            border-radius: 12px;
            padding: 1rem;
            max-width: 350px;
            box-shadow: 0 12px 40px rgba(0,0,0,0.4);
            z-index: 10000;
            animation: tooltipFadeIn 0.2s ease-out;
        ">
            <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
                <div style="font-size: 1.5rem;">${complexityIcon}</div>
                <div style="flex: 1;">
                    <div style="font-weight: 600; font-size: 1rem;">${fileName}</div>
                    <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.25rem;">${complexityLabel}</div>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
                <div style="background: var(--glass-light); border-radius: 8px; padding: 0.75rem; text-align: center;">
                    <div style="font-size: 1.25rem; font-weight: 600; color: var(--accent-primary);">${loc.toLocaleString()}</div>
                    <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.25rem;">Lines of Code</div>
                </div>
                <div style="background: var(--glass-light); border-radius: 8px; padding: 0.75rem; text-align: center;">
                    <div style="font-size: 1.25rem; font-weight: 600; color: ${complexityColor};">${complexity}</div>
                    <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.25rem;">Complexity</div>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(tooltip);
    
    const tooltipRect = tooltip.firstElementChild.getBoundingClientRect();
    let left = event.pageX + 15;
    let top = event.pageY - tooltipRect.height / 2;
    
    if (left + tooltipRect.width > window.innerWidth) {
        left = event.pageX - tooltipRect.width - 15;
    }
    
    if (top + tooltipRect.height > window.innerHeight) {
        top = window.innerHeight - tooltipRect.height - 10;
    }
    
    if (top < 10) top = 10;
    
    tooltip.firstElementChild.style.left = `${left}px`;
    tooltip.firstElementChild.style.top = `${top}px`;
};

/**
 * Hide heatmap tooltip
 */
window.hideHeatmapTooltip = function() {
    const tooltip = document.getElementById('heatmap-tooltip');
    if (tooltip) tooltip.remove();
};
