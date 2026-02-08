/**
 * Vulnerabilities Tab Component (⚠️)
 * Displays security vulnerabilities, CVE tracking, and severity distribution
 * 
 * Features:
 * - Severity breakdown (critical, high, medium, low)
 * - CVE tracking and OWASP findings
 * - Severity distribution chart
 * - Risk heat map
 * - Secrets scanning status
 */

class VulnerabilitiesTab {
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
    const total = this.getTotalVulnerabilities();
    const riskLevel = this.getRiskLevel(total);

    this.container.innerHTML = `
      <div class="vulnerabilities-tab">
        <div class="vulnerabilities-header">
          <h2>⚠️ Vulnerability Report</h2>
          <div class="risk-indicator ${riskLevel.class}">
            <div class="risk-badge">${riskLevel.label}</div>
            <div class="total-vulns">Total: ${total}</div>
          </div>
        </div>

        <div class="vulnerabilities-content">
          ${this.renderSeverityBreakdown()}
          ${this.renderDistributionChart()}
          ${this.renderOWASPFindings()}
          ${this.renderSecretsScanning()}
        </div>
      </div>

      <style>
        .vulnerabilities-tab {
          padding: 20px;
          background: #f5f5f5;
        }

        .vulnerabilities-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 30px;
          border-bottom: 2px solid #ddd;
          padding-bottom: 15px;
        }

        .vulnerabilities-header h2 {
          margin: 0;
          font-size: 28px;
        }

        .risk-indicator {
          display: flex;
          align-items: center;
          gap: 15px;
          padding: 15px 20px;
          border-radius: 8px;
          background: white;
        }

        .risk-badge {
          padding: 8px 16px;
          border-radius: 4px;
          font-weight: 600;
          font-size: 14px;
          text-transform: uppercase;
        }

        .risk-indicator.critical .risk-badge {
          background: #f44336;
          color: white;
        }

        .risk-indicator.high .risk-badge {
          background: #ff9800;
          color: white;
        }

        .risk-indicator.medium .risk-badge {
          background: #ffc107;
          color: #333;
        }

        .risk-indicator.low .risk-badge {
          background: #4caf50;
          color: white;
        }

        .total-vulns {
          font-size: 18px;
          font-weight: 600;
          color: #333;
        }

        .vulnerabilities-content {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 20px;
        }

        .severity-card {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .severity-section {
          margin-bottom: 20px;
        }

        .severity-item {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 12px;
          margin-bottom: 10px;
          border-radius: 4px;
          background: #f9f9f9;
          border-left: 4px solid;
        }

        .severity-item.critical {
          border-left-color: #f44336;
          background: #ffebee;
        }

        .severity-item.high {
          border-left-color: #ff9800;
          background: #fff3e0;
        }

        .severity-item.medium {
          border-left-color: #ffc107;
          background: #fffde7;
        }

        .severity-item.low {
          border-left-color: #4caf50;
          background: #e8f5e9;
        }

        .severity-label {
          display: flex;
          align-items: center;
          gap: 8px;
          font-weight: 500;
        }

        .severity-count {
          font-size: 20px;
          font-weight: 700;
          margin: 0 15px;
        }

        .severity-bar {
          flex: 1;
          height: 8px;
          background: #e0e0e0;
          border-radius: 4px;
          overflow: hidden;
          margin: 0 10px;
        }

        .severity-fill {
          height: 100%;
          transition: width 0.3s ease;
        }

        .severity-fill.critical {
          background: #f44336;
        }

        .severity-fill.high {
          background: #ff9800;
        }

        .severity-fill.medium {
          background: #ffc107;
        }

        .severity-fill.low {
          background: #4caf50;
        }

        .distribution-chart {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          grid-column: 1 / -1;
        }

        .chart-container {
          position: relative;
          width: 100%;
          height: 300px;
          margin-top: 20px;
        }

        .pie-chart {
          display: flex;
          justify-content: center;
          align-items: center;
          width: 100%;
          height: 100%;
        }

        .owasp-findings {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .owasp-findings h4 {
          margin: 0 0 15px 0;
          font-size: 16px;
          border-bottom: 2px solid #e0e0e0;
          padding-bottom: 10px;
        }

        .owasp-item {
          padding: 10px 0;
          border-bottom: 1px solid #f0f0f0;
        }

        .owasp-item:last-child {
          border-bottom: none;
        }

        .secrets-scan {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .secrets-scan h4 {
          margin: 0 0 15px 0;
          font-size: 16px;
          border-bottom: 2px solid #e0e0e0;
          padding-bottom: 10px;
        }

        .scan-status {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 10px;
          border-radius: 4px;
          background: #f0f0f0;
        }

        .scan-status.active {
          background: #e8f5e9;
        }

        .status-dot {
          width: 12px;
          height: 12px;
          border-radius: 50%;
          background: #999;
        }

        .status-dot.active {
          background: #4caf50;
          animation: pulse 2s infinite;
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      </style>
    `;
  }

  renderSeverityBreakdown() {
    const { critical, high, medium, low } = this.data;
    const total = this.getTotalVulnerabilities();
    const max = Math.max(critical, high, medium, low, 1);

    return `
      <div class="severity-card">
        <h3>Severity Breakdown</h3>
        <div class="severity-section">
          <div class="severity-item critical">
            <span class="severity-label">🔴 Critical</span>
            <span class="severity-count">${critical || 0}</span>
            <div class="severity-bar">
              <div class="severity-fill critical" style="width: ${((critical || 0) / max * 100)}%"></div>
            </div>
            <span style="font-size: 12px; color: #666;">${total > 0 ? ((critical || 0) / total * 100).toFixed(0) : 0}%</span>
          </div>

          <div class="severity-item high">
            <span class="severity-label">🟠 High</span>
            <span class="severity-count">${high || 0}</span>
            <div class="severity-bar">
              <div class="severity-fill high" style="width: ${((high || 0) / max * 100)}%"></div>
            </div>
            <span style="font-size: 12px; color: #666;">${total > 0 ? ((high || 0) / total * 100).toFixed(0) : 0}%</span>
          </div>

          <div class="severity-item medium">
            <span class="severity-label">🟡 Medium</span>
            <span class="severity-count">${medium || 0}</span>
            <div class="severity-bar">
              <div class="severity-fill medium" style="width: ${((medium || 0) / max * 100)}%"></div>
            </div>
            <span style="font-size: 12px; color: #666;">${total > 0 ? ((medium || 0) / total * 100).toFixed(0) : 0}%</span>
          </div>

          <div class="severity-item low">
            <span class="severity-label">🟢 Low</span>
            <span class="severity-count">${low || 0}</span>
            <div class="severity-bar">
              <div class="severity-fill low" style="width: ${((low || 0) / max * 100)}%"></div>
            </div>
            <span style="font-size: 12px; color: #666;">${total > 0 ? ((low || 0) / total * 100).toFixed(0) : 0}%</span>
          </div>
        </div>
      </div>
    `;
  }

  renderDistributionChart() {
    const { critical, high, medium, low } = this.data;
    const total = this.getTotalVulnerabilities();

    return `
      <div class="distribution-chart">
        <h3>Distribution Overview</h3>
        <div class="chart-container">
          <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; width: 100%; height: 100%;">
            <div style="text-align: center; display: flex; flex-direction: column; justify-content: center;">
              <div style="font-size: 32px; font-weight: bold; color: #f44336;">${critical || 0}</div>
              <div style="font-size: 12px; color: #999; margin-top: 5px;">Critical</div>
              <div style="font-size: 11px; color: #bbb;">${total > 0 ? ((critical || 0) / total * 100).toFixed(1) : 0}%</div>
            </div>
            <div style="text-align: center; display: flex; flex-direction: column; justify-content: center;">
              <div style="font-size: 32px; font-weight: bold; color: #ff9800;">${high || 0}</div>
              <div style="font-size: 12px; color: #999; margin-top: 5px;">High</div>
              <div style="font-size: 11px; color: #bbb;">${total > 0 ? ((high || 0) / total * 100).toFixed(1) : 0}%</div>
            </div>
            <div style="text-align: center; display: flex; flex-direction: column; justify-content: center;">
              <div style="font-size: 32px; font-weight: bold; color: #ffc107;">${medium || 0}</div>
              <div style="font-size: 12px; color: #999; margin-top: 5px;">Medium</div>
              <div style="font-size: 11px; color: #bbb;">${total > 0 ? ((medium || 0) / total * 100).toFixed(1) : 0}%</div>
            </div>
            <div style="text-align: center; display: flex; flex-direction: column; justify-content: center;">
              <div style="font-size: 32px; font-weight: bold; color: #4caf50;">${low || 0}</div>
              <div style="font-size: 12px; color: #999; margin-top: 5px;">Low</div>
              <div style="font-size: 11px; color: #bbb;">${total > 0 ? ((low || 0) / total * 100).toFixed(1) : 0}%</div>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  renderOWASPFindings() {
    const findings = this.data.owasp_findings || [];
    
    if (findings.length === 0) {
      return `
        <div class="owasp-findings">
          <h4>🔐 OWASP Findings</h4>
          <p style="color: #999; font-size: 14px;">No OWASP findings detected</p>
        </div>
      `;
    }

    return `
      <div class="owasp-findings">
        <h4>🔐 OWASP Findings (${findings.length})</h4>
        ${findings.map(f => `
          <div class="owasp-item">
            <div style="font-weight: 500;">${f.category || "Unknown"}</div>
            <div style="font-size: 12px; color: #666;">${f.description || ""}</div>
          </div>
        `).join("")}
      </div>
    `;
  }

  renderSecretsScanning() {
    const secrets = this.data.secrets_scan;
    const isActive = secrets != null;

    return `
      <div class="secrets-scan">
        <h4>🔑 Secrets Scanning</h4>
        <div class="scan-status ${isActive ? "active" : ""}">
          <span class="status-dot ${isActive ? "active" : ""}"></span>
          <span>${isActive ? "Active" : "Inactive"}</span>
        </div>
        ${isActive ? `
          <div style="margin-top: 10px; font-size: 12px; color: #666;">
            <div>Secrets Found: ${secrets.secrets_found || 0}</div>
            <div>Last Scan: ${secrets.last_scan_date || "N/A"}</div>
          </div>
        ` : ""}
      </div>
    `;
  }

  getTotalVulnerabilities() {
    return (this.data.critical || 0) + (this.data.high || 0) + 
           (this.data.medium || 0) + (this.data.low || 0);
  }

  getRiskLevel(total) {
    const critical = this.data.critical || 0;
    const high = this.data.high || 0;

    if (critical > 0) {
      return { label: "CRITICAL", class: "critical" };
    } else if (high > 5) {
      return { label: "HIGH", class: "high" };
    } else if (high > 0 || total > 20) {
      return { label: "MEDIUM", class: "medium" };
    }
    return { label: "LOW", class: "low" };
  }

  update(newData) {
    this.data = { ...this.data, ...newData };
    this.render();
  }
}

// Export for module usage
if (typeof module !== "undefined" && module.exports) {
  module.exports = VulnerabilitiesTab;
}
