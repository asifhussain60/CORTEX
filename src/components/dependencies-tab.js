/**
 * Dependencies Tab Component (📦)
 * Displays package management and dependency tracking
 * 
 * Features:
 * - Direct vs transitive dependency counts
 * - Outdated and vulnerable dependency tracking
 * - Dependency health assessment
 * - Package list with versions
 * - License tracking
 */

class DependenciesTab {
  constructor(containerSelector, data) {
    this.container = document.querySelector(containerSelector);
    this.data = data;
    this.init();
  }

  init() {
    if (!this.container) {
      console.error("Container not found:", this.container);
      return;
    }
    this.render();
  }

  render() {
    const health = this.getDependencyHealth();

    this.container.innerHTML = `
      <div class="dependencies-tab">
        <div class="dependencies-header">
          <h2>📦 Dependencies Report</h2>
          <div class="health-indicator ${health.class}">
            <div class="health-badge">${health.label}</div>
            <div class="health-details">${health.details}</div>
          </div>
        </div>

        <div class="dependencies-content">
          ${this.renderDependencyMetrics()}
          ${this.renderPackageStatus()}
          ${this.renderLicenses()}
        </div>
      </div>

      <style>
        .dependencies-tab {
          padding: 20px;
          background: #f5f5f5;
        }

        .dependencies-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 30px;
          border-bottom: 2px solid #ddd;
          padding-bottom: 15px;
        }

        .dependencies-header h2 {
          margin: 0;
          font-size: 28px;
        }

        .health-indicator {
          display: flex;
          align-items: center;
          gap: 15px;
          padding: 15px 20px;
          border-radius: 8px;
          background: white;
        }

        .health-badge {
          padding: 8px 16px;
          border-radius: 4px;
          font-weight: 600;
          font-size: 14px;
          text-transform: uppercase;
        }

        .health-indicator.healthy .health-badge {
          background: #4caf50;
          color: white;
        }

        .health-indicator.warning .health-badge {
          background: #ffc107;
          color: #333;
        }

        .health-indicator.critical .health-badge {
          background: #f44336;
          color: white;
        }

        .health-details {
          font-size: 12px;
          color: #666;
          line-height: 1.4;
        }

        .dependencies-content {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
        }

        @media (max-width: 1024px) {
          .dependencies-content {
            grid-template-columns: 1fr;
          }
        }

        .metrics-card {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .metrics-card h3 {
          margin: 0 0 20px 0;
          font-size: 18px;
          border-bottom: 2px solid #e0e0e0;
          padding-bottom: 10px;
        }

        .metric-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px;
          margin-bottom: 8px;
          border-radius: 4px;
          background: #f9f9f9;
        }

        .metric-label {
          display: flex;
          align-items: center;
          gap: 8px;
          font-weight: 500;
          flex: 1;
        }

        .metric-value {
          font-size: 18px;
          font-weight: 700;
          color: #333;
          min-width: 60px;
          text-align: right;
        }

        .metric-bar {
          flex: 1;
          height: 6px;
          background: #e0e0e0;
          border-radius: 3px;
          margin: 0 10px;
          overflow: hidden;
        }

        .metric-fill {
          height: 100%;
          transition: width 0.3s ease;
        }

        .metric-fill.good {
          background: #4caf50;
        }

        .metric-fill.warning {
          background: #ffc107;
        }

        .metric-fill.danger {
          background: #f44336;
        }

        .ratio-display {
          font-size: 12px;
          color: #999;
          min-width: 60px;
          text-align: right;
        }

        .package-status {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          grid-column: 1 / -1;
        }

        .package-status h3 {
          margin: 0 0 15px 0;
          font-size: 18px;
          border-bottom: 2px solid #e0e0e0;
          padding-bottom: 10px;
        }

        .status-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          gap: 15px;
        }

        .status-box {
          padding: 15px;
          border-radius: 8px;
          text-align: center;
          background: #f0f0f0;
        }

        .status-box.healthy {
          background: #e8f5e9;
          border: 1px solid #4caf50;
        }

        .status-box.warning {
          background: #fff3e0;
          border: 1px solid #ffc107;
        }

        .status-box.critical {
          background: #ffebee;
          border: 1px solid #f44336;
        }

        .status-number {
          font-size: 28px;
          font-weight: 700;
          line-height: 1;
          margin-bottom: 5px;
        }

        .status-label {
          font-size: 12px;
          font-weight: 500;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          color: #666;
        }

        .licenses-section {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .licenses-section h3 {
          margin: 0 0 15px 0;
          font-size: 18px;
          border-bottom: 2px solid #e0e0e0;
          padding-bottom: 10px;
        }

        .license-item {
          display: flex;
          justify-content: space-between;
          padding: 10px;
          border-bottom: 1px solid #f0f0f0;
        }

        .license-item:last-child {
          border-bottom: none;
        }

        .license-name {
          font-weight: 500;
          flex: 1;
        }

        .license-count {
          background: #f0f0f0;
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 600;
          margin-left: 10px;
        }

        .graph-visualization {
          margin-top: 10px;
          padding: 15px;
          background: #f9f9f9;
          border-radius: 4px;
          font-size: 12px;
          color: #666;
          white-space: pre-wrap;
          font-family: monospace;
        }
      </style>
    `;
  }

  renderDependencyMetrics() {
    const total = (this.data.direct_count || 0) + (this.data.transitive_count || 0);
    const outdatedRatio = total > 0 ? ((this.data.outdated_count || 0) / total * 100) : 0;
    const vulnerableRatio = total > 0 ? ((this.data.vulnerable_count || 0) / total * 100) : 0;

    return `
      <div class="metrics-card">
        <h3>📊 Dependency Metrics</h3>

        <div class="metric-item">
          <span class="metric-label">📌 Direct</span>
          <div class="metric-bar">
            <div class="metric-fill good" style="width: ${Math.min((this.data.direct_count || 0) / 100 * 100, 100)}%"></div>
          </div>
          <span class="metric-value">${this.data.direct_count || 0}</span>
        </div>

        <div class="metric-item">
          <span class="metric-label">🔗 Transitive</span>
          <div class="metric-bar">
            <div class="metric-fill good" style="width: ${Math.min((this.data.transitive_count || 0) / 500 * 100, 100)}%"></div>
          </div>
          <span class="metric-value">${this.data.transitive_count || 0}</span>
        </div>

        <div class="metric-item">
          <span class="metric-label">⏰ Outdated</span>
          <div class="metric-bar">
            <div class="metric-fill ${outdatedRatio > 20 ? "danger" : (outdatedRatio > 10 ? "warning" : "good")}" 
                 style="width: ${outdatedRatio}%"></div>
          </div>
          <span class="metric-value">${this.data.outdated_count || 0}</span>
          <span class="ratio-display">${outdatedRatio.toFixed(1)}%</span>
        </div>

        <div class="metric-item">
          <span class="metric-label">⚠️ Vulnerable</span>
          <div class="metric-bar">
            <div class="metric-fill ${vulnerableRatio > 5 ? "danger" : (vulnerableRatio > 2 ? "warning" : "good")}" 
                 style="width: ${vulnerableRatio * 5}%"></div>
          </div>
          <span class="metric-value">${this.data.vulnerable_count || 0}</span>
          <span class="ratio-display">${vulnerableRatio.toFixed(1)}%</span>
        </div>

        <div class="metric-item" style="margin-top: 15px; background: #e3f2fd; border-radius: 4px;">
          <span class="metric-label">Total</span>
          <span class="metric-value" style="color: #1976d2;">${total}</span>
        </div>
      </div>
    `;
  }

  renderPackageStatus() {
    const total = (this.data.direct_count || 0) + (this.data.transitive_count || 0);
    const outdated = this.data.outdated_count || 0;
    const vulnerable = this.data.vulnerable_count || 0;
    const healthy = total - outdated - vulnerable;

    return `
      <div class="package-status">
        <h3>📦 Package Status</h3>
        <div class="status-grid">
          <div class="status-box healthy">
            <div class="status-number">${healthy}</div>
            <div class="status-label">Up-to-Date</div>
          </div>
          <div class="status-box ${outdated > 0 ? "warning" : ""}">
            <div class="status-number">${outdated}</div>
            <div class="status-label">Outdated</div>
          </div>
          <div class="status-box ${vulnerable > 0 ? "critical" : ""}">
            <div class="status-number">${vulnerable}</div>
            <div class="status-label">Vulnerable</div>
          </div>
        </div>

        ${this.renderDependencyGraph()}
      </div>
    `;
  }

  renderDependencyGraph() {
    const graph = this.data.dependency_graph || {};
    if (Object.keys(graph).length === 0) {
      return "";
    }

    let graphText = "Dependency Graph:\n";
    for (const [pkg, deps] of Object.entries(graph).slice(0, 10)) {
      graphText += `├─ ${pkg}\n`;
      if (Array.isArray(deps)) {
        deps.slice(0, 3).forEach((dep, i) => {
          const isLast = i === deps.length - 1;
          graphText += `│  ${isLast ? "└─" : "├─"} ${dep}\n`;
        });
        if (deps.length > 3) {
          graphText += `│  └─ ... +${deps.length - 3} more\n`;
        }
      }
    }

    return `<div class="graph-visualization">${graphText}</div>`;
  }

  renderLicenses() {
    const licenses = this.data.licenses || [];
    
    if (licenses.length === 0) {
      return `
        <div class="licenses-section">
          <h3>📄 Licenses</h3>
          <p style="color: #999; font-size: 14px;">No license information available</p>
        </div>
      `;
    }

    return `
      <div class="licenses-section">
        <h3>📄 Licenses (${licenses.length} types)</h3>
        ${licenses.slice(0, 10).map(lic => `
          <div class="license-item">
            <div class="license-name">${lic.name || "Unknown"}</div>
            <div class="license-count">${lic.count || 0} packages</div>
          </div>
        `).join("")}
        ${licenses.length > 10 ? `
          <div style="padding: 10px; font-size: 12px; color: #999;">
            ... and ${licenses.length - 10} more license types
          </div>
        ` : ""}
      </div>
    `;
  }

  getDependencyHealth() {
    const total = (this.data.direct_count || 0) + (this.data.transitive_count || 0);
    if (total === 0) {
      return { label: "No Dependencies", class: "healthy", details: "No packages configured" };
    }

    const outdated = this.data.outdated_count || 0;
    const vulnerable = this.data.vulnerable_count || 0;
    const outdatedPct = total > 0 ? (outdated / total * 100) : 0;
    const vulnerablePct = total > 0 ? (vulnerable / total * 100) : 0;

    if (vulnerable > 0) {
      return {
        label: "CRITICAL",
        class: "critical",
        details: `${vulnerable} vulnerable packages detected`
      };
    } else if (outdatedPct > 25) {
      return {
        label: "WARNING",
        class: "warning",
        details: `${outdatedPct.toFixed(0)}% dependencies outdated`
      };
    } else if (outdatedPct > 10) {
      return {
        label: "FAIR",
        class: "warning",
        details: `${outdatedPct.toFixed(0)}% dependencies outdated`
      };
    }

    return {
      label: "HEALTHY",
      class: "healthy",
      details: `All ${total} packages up-to-date`
    };
  }

  update(newData) {
    this.data = { ...this.data, ...newData };
    this.render();
  }
}

// Export for module usage
if (typeof module !== "undefined" && module.exports) {
  module.exports = DependenciesTab;
}
