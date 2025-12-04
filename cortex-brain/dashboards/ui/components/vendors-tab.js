/**
 * Vendors Tab Component
 * 
 * Renders external vendor dependencies and integration status.
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Source-Available (Use Allowed, No Contributions)
 */

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

        <!-- Vendor Cards by Category -->
        ${renderVendorsByCategory(vendorList)}
    `;
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
    
    return `
        <div class="glass-card" style="
            border-left: 4px solid ${status.borderColor};
            cursor: pointer;
            transition: transform 0.2s ease;
        " onmouseover="this.style.transform='translateY(-4px)'" onmouseout="this.style.transform='translateY(0)'">
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
 * Export vendors (placeholder)
 */
window.exportVendors = function() {
    console.log('Export vendors');
    alert('Vendors export functionality coming soon!');
};
