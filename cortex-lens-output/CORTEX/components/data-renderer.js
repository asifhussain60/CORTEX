/**
 * CORTEX Dashboard Data Renderer
 * Renders analysis data into the dashboard tabs
 * Version: 1.0.0
 */

function renderDashboardContent() {
    console.log('🎨 Rendering dashboard content from analysisData');
    
    if (typeof analysisData === 'undefined') {
        console.error('❌ analysisData not found');
        return;
    }
    
    // Render entry points
    renderEntryPoints();
    
    // Render code smells
    renderCodeSmells();
    
    // Render dependencies
    renderDependencies();
    
    // Render security advisories
    renderSecurityAdvisories();
    
    console.log('✅ Dashboard content rendered');
}

function renderEntryPoints() {
    const container = document.querySelector('.entry-points-list');
    if (!container) return;
    
    const entryPoints = analysisData.architecture?.entry_points || [];
    
    if (entryPoints.length === 0) {
        container.innerHTML = '<p style="color: #888;">No entry points detected</p>';
        return;
    }
    
    container.innerHTML = entryPoints.map(entry => `
        <div class="entry-point-item">
            <code>${entry.file || 'Unknown'}</code>
            <span class="entry-type">${entry.type || 'unknown'}</span>
        </div>
    `).join('');
}

function renderCodeSmells() {
    const container = document.querySelector('.code-smells-list');
    if (!container) return;
    
    const codeSmells = analysisData.quality?.code_smells || [];
    
    if (codeSmells.length === 0) {
        container.innerHTML = '<p style="color: #888;">No code smells detected</p>';
        return;
    }
    
    container.innerHTML = codeSmells.map(smell => `
        <div class="code-smell-item">
            <div class="smell-type">${smell.type || 'Unknown'}</div>
            <div class="smell-file"><code>${smell.file || 'N/A'}</code></div>
            <div class="smell-line">Line ${smell.line || '?'}</div>
            <div class="smell-message">${smell.message || 'No description'}</div>
        </div>
    `).join('');
}

function renderDependencies() {
    const container = document.querySelector('.dependency-tree-list');
    if (!container) return;
    
    const dependencies = analysisData.dependencies?.dependencies || [];
    
    if (dependencies.length === 0) {
        container.innerHTML = '<p style="color: #888;">No dependencies found</p>';
        return;
    }
    
    container.innerHTML = dependencies.map(dep => `
        <div class="dependency-item">
            <span class="dep-name">${dep.name || 'Unknown'}</span>
            <span class="dep-version">${dep.version || 'N/A'}</span>
            <span class="dep-status ${dep.status?.toLowerCase() || 'unknown'}">${dep.status || 'Unknown'}</span>
        </div>
    `).join('');
}

function renderSecurityAdvisories() {
    const container = document.querySelector('.security-advisories-list');
    if (!container) return;
    
    const advisories = analysisData.security?.security_advisories || [];
    
    if (advisories.length === 0) {
        container.innerHTML = '<p style="color: #10b981;">✅ No security advisories</p>';
        return;
    }
    
    container.innerHTML = advisories.map(advisory => `
        <div class="advisory-item">
            <div class="advisory-title">${advisory.title || 'Security Issue'}</div>
            <div class="advisory-package"><code>${advisory.package || 'Unknown'}</code></div>
            <div class="advisory-description">${advisory.description || 'No description available'}</div>
        </div>
    `).join('');
}

// Initialize rendering after DOM and data are ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(renderDashboardContent, 100); // Small delay to ensure analysisData is loaded
    });
} else {
    setTimeout(renderDashboardContent, 100);
}
