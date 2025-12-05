/**
 * Vendors Tab Component
 * 
 * Renders external vendor dependencies and integration status.
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Source-Available (Use Allowed, No Contributions)
 */

import { showPanelSpinner } from '../shared-utils.js';

/**
 * Render vendors tab
 * @param {Object} data - Dashboard data containing vendors information
 */
export function renderVendors(data) {
    const container = document.getElementById('vendors-container');
    if (!container) {
        console.error('Vendors container not found');
        return;
    }
    
    showPanelSpinner(container, 'Loading vendor data...');
    
    setTimeout(() => {
        const vendors = data.vendors || {};
        const summary = vendors.summary || {};
        const vendorList = vendors.vendors || [];
        
        // Build HTML
        container.innerHTML = `
        <div class="view-header">
            <h2>🔗 Dependencies & Vendors</h2>
            <div class="header-actions">
                <button class="btn-secondary" onclick="exportVendors()">Export Report</button>
            </div>
        </div>

        <!-- Summary Cards -->
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-bottom: 2rem;">
            <div class="glass-card" style="display: flex; align-items: center; gap: 1rem; padding: 1.5rem;">
                <div style="font-size: 2.5rem;">📦</div>
                <div>
                    <h3 style="font-size: 2rem; margin: 0; color: var(--accent-primary);">
                        ${summary.total_vendors || 0}
                    </h3>
                    <p style="margin: 0.25rem 0 0 0; color: var(--text-secondary);">External Vendors</p>
                </div>
            </div>
            
            <div class="glass-card" style="display: flex; align-items: center; gap: 1rem; padding: 1.5rem;">
                <div style="font-size: 2.5rem;">✅</div>
                <div>
                    <h3 style="font-size: 2rem; margin: 0; color: var(--success);">
                        ${summary.active_vendors || 0}
                    </h3>
                    <p style="margin: 0.25rem 0 0 0; color: var(--text-secondary);">Active Integrations</p>
                </div>
            </div>
            
            <div class="glass-card" style="display: flex; align-items: center; gap: 1rem; padding: 1.5rem;">
                <div style="font-size: 2.5rem;">⚠️</div>
                <div>
                    <h3 style="font-size: 2rem; margin: 0; color: var(--warning);">
                        ${summary.inactive_vendors || 0}
                    </h3>
                    <p style="margin: 0.25rem 0 0 0; color: var(--text-secondary);">Unused Credentials</p>
                </div>
            </div>
            
            <div class="glass-card" style="display: flex; align-items: center; gap: 1rem; padding: 1.5rem;">
                <div style="font-size: 2.5rem;">🔒</div>
                <div>
                    <h3 style="font-size: 2rem; margin: 0; color: var(--danger);">
                        ${summary.credentials_needing_refresh || 0}
                    </h3>
                    <p style="margin: 0.25rem 0 0 0; color: var(--text-secondary);">Expired Credentials</p>
                </div>
            </div>
        </div>

        <!-- How to Read Description -->
        <div class="glass-card" style="margin-bottom: 2rem; background: linear-gradient(135deg, var(--glass-light) 0%, var(--background-secondary) 100%);">
            <h3 style="margin-bottom: 1rem;">🔗 Dependencies & Integration Status</h3>
            <p style="color: var(--text-secondary); line-height: 1.6; margin-bottom: 1rem;">
                This view shows external service integrations and vendor dependencies detected in your project. 
                <strong style="color: var(--success);">✅ Active</strong> integrations are in use, 
                <strong style="color: var(--warning);">⚠️ Unused</strong> credentials should be removed, and 
                <strong style="color: var(--danger);">❌ Not Configured</strong> services require setup.
                <strong>Hover over each vendor card</strong> to see detailed integration information, security recommendations, and credential status.
            </p>
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
                        External vendor integrations are detected through environment variables and code analysis.
                        <span style="color: var(--success); font-weight: 600;">✅ Active</span> vendors have recent usage evidence.
                        <span style="color: var(--warning); font-weight: 600;">⚠️ Unused</span> integrations have credentials but no recent activity (consider removing).
                        <span style="color: var(--danger); font-weight: 600;">❌ Not Configured</span> means vendor code found without credentials.
                        <strong>Detection confidence</strong> indicates reliability of automated detection. 
                        <strong>Hover over vendor cards</strong> for security recommendations and integration details.
                    </div>
                </div>
            </div>
        </div>

        <!-- Vendor Cards by Category -->
        ${renderVendorsByCategory(vendorList)}
    `;
    }, 250);
}

/**
 * Render vendors grouped by category
 * @param {Array} vendorList - Array of vendor objects
 * @returns {string} HTML string
 */
function renderVendorsByCategory(vendorList) {
    // Group vendors by category
    const categories = {
        'payment': { title: '💳 Payment Services', vendors: [] },
        'authentication': { title: '🔐 Authentication', vendors: [] },
        'storage': { title: '☁️ Storage & CDN', vendors: [] },
        'communication': { title: '📧 Communication', vendors: [] },
        'monitoring': { title: '📊 Monitoring & Analytics', vendors: [] },
        'other': { title: '🔧 Other Services', vendors: [] }
    };
    
    // Group vendors
    vendorList.forEach(vendor => {
        const category = vendor.category || 'other';
        if (categories[category]) {
            categories[category].vendors.push(vendor);
        } else {
            categories.other.vendors.push(vendor);
        }
    });
    
    // Render each category
    return Object.entries(categories)
        .filter(([_, cat]) => cat.vendors.length > 0)
        .map(([key, cat]) => `
            <div style="margin-bottom: 2rem;">
                <h3 style="margin-bottom: 1rem;">${cat.title}</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1.5rem;">
                    ${cat.vendors.map(vendor => renderVendorCard(vendor)).join('')}
                </div>
            </div>
        `).join('');
}

/**
 * Render vendor card
 * @param {Object} vendor - Vendor object
 * @returns {string} HTML string
 */
function renderVendorCard(vendor) {
    const statusConfig = {
        'configured_active': {
            icon: '✅',
            label: 'Active',
            color: 'var(--success)',
            borderColor: 'var(--success)'
        },
        'configured_unused': {
            icon: '⚠️',
            label: 'Unused',
            color: 'var(--warning)',
            borderColor: 'var(--warning)'
        },
        'not_configured': {
            icon: '❌',
            label: 'Not Configured',
            color: 'var(--danger)',
            borderColor: 'var(--danger)'
        }
    };
    
    const status = statusConfig[vendor.status] || statusConfig.not_configured;
    const confidence = vendor.detection_confidence || 0;
    
    // Build tooltip explanation
    const explanation = buildVendorTooltipExplanation(vendor);
    
    return `
        <div 
            class="vendor-card-hoverable glass-card" 
            style="
                border-left: 4px solid ${status.borderColor};
                cursor: pointer;
                transition: all 0.3s ease;
            " 
            onmouseover="showVendorTooltip(event, ${JSON.stringify(vendor).replace(/"/g, '&quot;')}, this); this.style.transform='translateY(-4px)'; this.style.boxShadow='0 8px 24px rgba(0,0,0,0.3)'"
            onmouseout="hideVendorTooltip(this); this.style.transform='translateY(0)'; this.style.boxShadow=''"
        >
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                <div>
                    <h4 style="margin: 0 0 0.5rem 0; color: var(--text-primary);">
                        ${vendor.name || 'Unknown Vendor'}
                    </h4>
                    <span style="
                        font-size: 0.75rem;
                        padding: 0.25rem 0.5rem;
                        border-radius: 8px;
                        background: var(--glass-bg);
                        color: var(--text-secondary);
                    ">
                        ${(vendor.category || 'other').replace('_', ' ').toUpperCase()}
                    </span>
                </div>
                <div style="
                    padding: 0.25rem 0.75rem;
                    border-radius: 12px;
                    font-size: 0.875rem;
                    font-weight: 600;
                    background: ${status.color}22;
                    color: ${status.color};
                ">
                    ${status.icon} ${status.label}
                </div>
            </div>
            
            ${vendor.description ? `
                <p style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 1rem;">
                    ${vendor.description}
                </p>
            ` : ''}
            
            <div style="display: grid; gap: 0.5rem; font-size: 0.875rem;">
                ${vendor.integration_points ? `
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-secondary);">Integration Points:</span>
                        <span style="font-weight: 600;">${vendor.integration_points}</span>
                    </div>
                ` : ''}
                
                ${vendor.last_used ? `
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-secondary);">Last Used:</span>
                        <span style="font-weight: 600;">${vendor.last_used}</span>
                    </div>
                ` : ''}
                
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: var(--text-secondary);">Detection Confidence:</span>
                    <span style="font-weight: 600; color: ${getConfidenceColor(confidence)};">
                        ${confidence}%
                    </span>
                </div>
            </div>
            
            ${vendor.env_vars && vendor.env_vars.length > 0 ? `
                <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--glass-border);">
                    <div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                        Environment Variables:
                    </div>
                    <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                        ${vendor.env_vars.slice(0, 3).map(envVar => `
                            <code style="
                                font-size: 0.7rem;
                                padding: 0.25rem 0.5rem;
                                border-radius: 4px;
                                background: rgba(0, 0, 0, 0.3);
                                color: var(--accent-primary);
                            ">${envVar}</code>
                        `).join('')}
                        ${vendor.env_vars.length > 3 ? `
                            <span style="font-size: 0.7rem; color: var(--text-secondary);">
                                +${vendor.env_vars.length - 3} more
                            </span>
                        ` : ''}
                    </div>
                </div>
            ` : ''}
            
            ${vendor.files && vendor.files.length > 0 ? `
                <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--glass-border);">
                    <div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                        Referenced in:
                    </div>
                    <div style="font-size: 0.7rem; font-family: monospace; color: var(--text-secondary);">
                        ${vendor.files.slice(0, 2).map(file => `<div>${file}</div>`).join('')}
                        ${vendor.files.length > 2 ? `<div style="color: var(--accent-primary);">+${vendor.files.length - 2} more files</div>` : ''}
                    </div>
                </div>
            ` : ''}
        </div>
    `;
}

/**
 * Get confidence color based on percentage
 * @param {number} confidence - Confidence percentage (0-100)
 * @returns {string} Color value
 */
function getConfidenceColor(confidence) {
    if (confidence >= 80) return 'var(--success)';
    if (confidence >= 50) return 'var(--warning)';
    return 'var(--danger)';
}

/**
 * Build tooltip explanation for a vendor
 * @param {Object} vendor - Vendor object
 * @returns {string} Explanation text
 */
function buildVendorTooltipExplanation(vendor) {
    const status = vendor.status || 'not_configured';
    const confidence = vendor.detection_confidence || 0;
    const integrationPoints = vendor.integration_points || 0;
    
    let explanation = '';
    
    if (status === 'configured_active') {
        explanation = `This vendor integration is <strong>actively used</strong> with ${integrationPoints} integration point${integrationPoints !== 1 ? 's' : ''}. `;
        explanation += `Detection confidence is ${confidence}%, indicating reliable usage patterns. `;
        if (vendor.last_used) {
            explanation += `Last activity: ${vendor.last_used}. `;
        }
        explanation += 'Ensure credentials are rotated regularly per security policy.';
    } else if (status === 'configured_unused') {
        explanation = `Credentials are <strong>configured but not actively used</strong>. `;
        explanation += `This represents a security risk - unused credentials should be removed to minimize attack surface. `;
        if (vendor.last_used) {
            explanation += `Last used: ${vendor.last_used}. `;
        }
        explanation += 'Consider removing credentials if integration is no longer needed.';
    } else {
        explanation = `This vendor was <strong>detected but not configured</strong>. `;
        explanation += `Integration may be incomplete or credentials may be missing. `;
        if (integrationPoints > 0) {
            explanation += `${integrationPoints} integration point${integrationPoints !== 1 ? 's' : ''} detected in code. `;
        }
        explanation += 'Review integration requirements and configure credentials if needed.';
    }
    
    return explanation;
}

/**
 * Show vendor tooltip on hover
 * @param {Event} event - Mouse event
 * @param {Object} vendor - Vendor data
 * @param {HTMLElement} element - Hovered element
 */
window.showVendorTooltip = function(event, vendor, element) {
    // Parse vendor if it's a string (from JSON.stringify)
    if (typeof vendor === 'string') {
        try {
            vendor = JSON.parse(vendor);
        } catch (e) {
            console.error('Failed to parse vendor data:', e);
            return;
        }
    }
    
    // Remove existing tooltip
    const existing = document.getElementById('vendor-tooltip');
    if (existing) {
        existing.remove();
    }
    
    const status = vendor.status || 'not_configured';
    let statusIcon = '✅';
    let statusLabel = 'Active';
    let statusColor = 'var(--success)';
    
    if (status === 'configured_unused') {
        statusIcon = '⚠️';
        statusLabel = 'Unused';
        statusColor = 'var(--warning)';
    } else if (status === 'not_configured') {
        statusIcon = '❌';
        statusLabel = 'Not Configured';
        statusColor = 'var(--danger)';
    }
    
    const confidence = vendor.detection_confidence || 0;
    const confidenceColor = getConfidenceColor(confidence);
    const explanation = buildVendorTooltipExplanation(vendor);
    
    // Create tooltip
    const tooltip = document.createElement('div');
    tooltip.id = 'vendor-tooltip';
    tooltip.style.cssText = `
        position: fixed;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.98) 0%, rgba(30, 41, 59, 0.98) 100%);
        border: 1px solid ${statusColor};
        border-radius: 12px;
        padding: 1.25rem;
        max-width: 450px;
        z-index: 10000;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        pointer-events: none;
        animation: tooltipFadeIn 0.2s ease-out;
        backdrop-filter: blur(10px);
    `;
    
    tooltip.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid var(--glass-border);">
            <div style="font-size: 2rem;">${statusIcon}</div>
            <div style="flex: 1;">
                <div style="font-weight: 700; font-size: 1.1rem; color: var(--text-primary); margin-bottom: 0.25rem;">
                    ${vendor.name || 'Unknown Vendor'}
                </div>
                <div style="font-size: 0.875rem; color: var(--text-secondary);">
                    ${(vendor.category || 'other').replace('_', ' ')}
                </div>
            </div>
        </div>
        
        <div style="display: flex; gap: 0.75rem; flex-wrap: wrap; margin-bottom: 1rem;">
            <div style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; background: ${statusColor}22; border-radius: 8px;">
                <span style="font-size: 1.25rem;">${statusIcon}</span>
                <span style="color: ${statusColor}; font-weight: 600; font-size: 0.875rem;">
                    ${statusLabel}
                </span>
            </div>
            <div style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; background: var(--glass-border); border-radius: 8px;">
                <span style="font-size: 1.25rem;">🎯</span>
                <span style="color: ${confidenceColor}; font-weight: 600; font-size: 0.875rem;">
                    ${confidence}% confidence
                </span>
            </div>
            ${vendor.integration_points ? `
                <div style="display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; background: var(--glass-border); border-radius: 8px;">
                    <span style="font-size: 1.25rem;">🔌</span>
                    <span style="color: var(--text-primary); font-weight: 600; font-size: 0.875rem;">
                        ${vendor.integration_points} integration${vendor.integration_points !== 1 ? 's' : ''}
                    </span>
                </div>
            ` : ''}
        </div>
        
        <div style="color: var(--text-secondary); line-height: 1.6; font-size: 0.875rem; margin-bottom: 1rem;">
            ${explanation}
        </div>
        
        ${vendor.env_vars && vendor.env_vars.length > 0 ? `
            <div style="margin-bottom: 1rem; padding: 1rem; background: rgba(0,0,0,0.2); border-radius: 8px;">
                <div style="color: var(--accent-primary); font-size: 0.875rem; font-weight: 600; margin-bottom: 0.5rem;">
                    🔑 Environment Variables (${vendor.env_vars.length})
                </div>
                <div style="font-family: monospace; font-size: 0.75rem; color: var(--text-secondary);">
                    ${vendor.env_vars.slice(0, 3).join(', ')}
                    ${vendor.env_vars.length > 3 ? ` <span style="color: var(--accent-primary);">+${vendor.env_vars.length - 3} more</span>` : ''}
                </div>
            </div>
        ` : ''}
        
        ${vendor.files && vendor.files.length > 0 ? `
            <div style="margin-bottom: 1rem; padding: 1rem; background: rgba(0,0,0,0.2); border-radius: 8px;">
                <div style="color: var(--accent-primary); font-size: 0.875rem; font-weight: 600; margin-bottom: 0.5rem;">
                    📁 Referenced Files (${vendor.files.length})
                </div>
                <div style="font-family: monospace; font-size: 0.75rem; color: var(--text-secondary);">
                    ${vendor.files.slice(0, 2).map(f => `<div style="margin-bottom: 0.25rem;">${f}</div>`).join('')}
                    ${vendor.files.length > 2 ? `<div style="color: var(--accent-primary);">+${vendor.files.length - 2} more files</div>` : ''}
                </div>
            </div>
        ` : ''}
        
        <div style="padding-top: 1rem; border-top: 1px solid var(--glass-border);">
            <div style="color: var(--accent-primary); font-size: 0.875rem; font-weight: 600; margin-bottom: 0.5rem;">
                ${status === 'configured_unused' ? '🔒 Security Recommendation' : '💡 Best Practice'}
            </div>
            <div style="color: var(--text-secondary); font-size: 0.875rem; line-height: 1.6;">
                ${status === 'configured_unused' 
                    ? 'Remove unused credentials to reduce attack surface. Audit and clean up environment variables regularly.'
                    : status === 'not_configured'
                    ? 'If this integration is required, configure credentials in environment variables or secure key vault.'
                    : 'Rotate credentials every 90 days. Monitor integration health and API rate limits.'}
            </div>
        </div>
    `;
    
    document.body.appendChild(tooltip);
    
    // Position tooltip
    const rect = element.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();
    
    let left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
    let top = rect.top - tooltipRect.height - 12;
    
    // Keep tooltip on screen
    if (left < 10) left = 10;
    if (left + tooltipRect.width > window.innerWidth - 10) {
        left = window.innerWidth - tooltipRect.width - 10;
    }
    
    if (top < 10) {
        top = rect.bottom + 12;
    }
    
    tooltip.style.left = left + 'px';
    tooltip.style.top = top + 'px';
};

/**
 * Hide vendor tooltip
 * @param {HTMLElement} element - Hovered element
 */
window.hideVendorTooltip = function(element) {
    // Remove tooltip
    const tooltip = document.getElementById('vendor-tooltip');
    if (tooltip) {
        tooltip.remove();
    }
};

/**
 * Export vendors (placeholder)
 */
window.exportVendors = function() {
    console.log('Export vendors');
    alert('Vendors export functionality coming soon!');
};
