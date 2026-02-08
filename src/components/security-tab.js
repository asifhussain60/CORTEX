/**
 * Security Tab Component (🔒)
 * Displays security assessments, compliance, and encryption status
 * 
 * Features:
 * - Security score visualization (0-10 gauge)
 * - Security posture display
 * - Compliance framework tracking
 * - Authentication & encryption status
 * - Data protection measures
 */

class SecurityTab {
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
    this.container.innerHTML = `
      <div class="security-tab">
        <div class="security-header">
          <h2>🔒 Security Assessment</h2>
          <div class="security-score-container">
            ${this.renderSecurityScore()}
          </div>
        </div>

        <div class="security-content">
          <div class="security-grid">
            ${this.renderPosture()}
            ${this.renderAuthentication()}
            ${this.renderEncryption()}
            ${this.renderDataProtection()}
          </div>

          <div class="frameworks-section">
            <h3>Compliance Frameworks</h3>
            ${this.renderFrameworks()}
          </div>
        </div>
      </div>

      <style>
        .security-tab {
          padding: 20px;
          background: #f5f5f5;
        }

        .security-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 30px;
          border-bottom: 2px solid #ddd;
          padding-bottom: 15px;
        }

        .security-header h2 {
          margin: 0;
          font-size: 28px;
        }

        .security-score-container {
          display: flex;
          align-items: center;
          gap: 20px;
        }

        .score-gauge {
          width: 120px;
          height: 120px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 36px;
          font-weight: bold;
          color: white;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .score-gauge.excellent {
          background: linear-gradient(135deg, #4caf50, #45a049);
        }

        .score-gauge.good {
          background: linear-gradient(135deg, #8bc34a, #7cb342);
        }

        .score-gauge.moderate {
          background: linear-gradient(135deg, #ff9800, #f57c00);
        }

        .score-gauge.poor {
          background: linear-gradient(135deg, #f44336, #d32f2f);
        }

        .score-info h3 {
          margin: 0 0 5px 0;
          font-size: 18px;
        }

        .score-info p {
          margin: 0;
          font-size: 14px;
          color: #666;
        }

        .security-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 20px;
          margin-bottom: 30px;
        }

        .security-card {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .security-card h4 {
          margin: 0 0 15px 0;
          font-size: 16px;
          border-bottom: 2px solid #e0e0e0;
          padding-bottom: 10px;
        }

        .status-item {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 10px;
          padding: 8px 0;
        }

        .status-label {
          font-weight: 500;
          font-size: 14px;
        }

        .status-value {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 14px;
        }

        .status-badge {
          display: inline-block;
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 600;
        }

        .status-badge.enabled {
          background: #c8e6c9;
          color: #2e7d32;
        }

        .status-badge.disabled {
          background: #ffcdd2;
          color: #c62828;
        }

        .status-badge.partial {
          background: #ffe0b2;
          color: #e65100;
        }

        .frameworks-section {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .frameworks-section h3 {
          margin: 0 0 15px 0;
          font-size: 18px;
          border-bottom: 2px solid #e0e0e0;
          padding-bottom: 10px;
        }

        .framework-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px;
          border-bottom: 1px solid #f0f0f0;
        }

        .framework-item:last-child {
          border-bottom: none;
        }

        .framework-name {
          font-weight: 500;
          flex: 1;
        }

        .framework-score {
          font-size: 14px;
          margin: 0 15px;
          color: #666;
        }

        .framework-issues {
          background: #fff3e0;
          color: #e65100;
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 600;
        }

        .framework-status {
          margin-left: 15px;
        }
      </style>
    `;
  }

  renderSecurityScore() {
    const score = this.data.security_score || 0;
    let scoreClass = "poor";
    let scoreStatus = "Critical";

    if (score >= 8) {
      scoreClass = "excellent";
      scoreStatus = "Excellent";
    } else if (score >= 6) {
      scoreClass = "good";
      scoreStatus = "Good";
    } else if (score >= 4) {
      scoreClass = "moderate";
      scoreStatus = "Moderate";
    }

    return `
      <div class="score-gauge ${scoreClass}">${score.toFixed(1)}</div>
      <div class="score-info">
        <h3>Security Score</h3>
        <p>Status: <strong>${scoreStatus}</strong></p>
        <p>Posture: <strong>${this.data.security_posture || "Unknown"}</strong></p>
      </div>
    `;
  }

  renderPosture() {
    return `
      <div class="security-card">
        <h4>Security Posture</h4>
        <div class="status-item">
          <span class="status-label">Current State</span>
          <span class="status-value">${this.data.security_posture || "N/A"}</span>
        </div>
      </div>
    `;
  }

  renderAuthentication() {
    const auth = this.data.authentication;
    if (!auth) {
      return `
        <div class="security-card">
          <h4>Authentication</h4>
          <p>Not configured</p>
        </div>
      `;
    }

    return `
      <div class="security-card">
        <h4>🔐 Authentication</h4>
        <div class="status-item">
          <span class="status-label">Type</span>
          <span class="status-value">${auth.implemented || "N/A"}</span>
        </div>
        <div class="status-item">
          <span class="status-label">Multi-Factor</span>
          <span class="status-badge ${auth.multi_factor ? "enabled" : "disabled"}">
            ${auth.multi_factor ? "Enabled" : "Disabled"}
          </span>
        </div>
        <div class="status-item">
          <span class="status-label">Standards</span>
          <span class="status-value">${(auth.standards || []).join(", ") || "None"}</span>
        </div>
      </div>
    `;
  }

  renderEncryption() {
    const encryption = this.data.encryption;
    if (!encryption) {
      return `
        <div class="security-card">
          <h4>Encryption</h4>
          <p>Not configured</p>
        </div>
      `;
    }

    return `
      <div class="security-card">
        <h4>🔑 Encryption</h4>
        <div class="status-item">
          <span class="status-label">At Rest</span>
          <span class="status-badge ${encryption.at_rest ? "enabled" : "disabled"}">
            ${encryption.at_rest ? "✓ Yes" : "✗ No"}
          </span>
        </div>
        <div class="status-item">
          <span class="status-label">In Transit</span>
          <span class="status-badge ${encryption.in_transit ? "enabled" : "disabled"}">
            ${encryption.in_transit ? "✓ Yes" : "✗ No"}
          </span>
        </div>
        <div class="status-item">
          <span class="status-label">Key Mgmt</span>
          <span class="status-value">${encryption.key_management || "N/A"}</span>
        </div>
      </div>
    `;
  }

  renderDataProtection() {
    const dp = this.data.data_protection;
    if (!dp) {
      return `
        <div class="security-card">
          <h4>Data Protection</h4>
          <p>Not configured</p>
        </div>
      `;
    }

    return `
      <div class="security-card">
        <h4>🛡️ Data Protection</h4>
        <div class="status-item">
          <span class="status-label">PII Detection</span>
          <span class="status-value">${dp.pii_detection || 0} items</span>
        </div>
        <div class="status-item">
          <span class="status-label">Masking</span>
          <span class="status-badge ${dp.masking ? "enabled" : "disabled"}">
            ${dp.masking ? "✓ Enabled" : "✗ Disabled"}
          </span>
        </div>
        <div class="status-item">
          <span class="status-label">Retention</span>
          <span class="status-value">${dp.retention_policy || "N/A"}</span>
        </div>
      </div>
    `;
  }

  renderFrameworks() {
    const frameworks = this.data.frameworks || [];
    
    if (frameworks.length === 0) {
      return "<p>No frameworks configured</p>";
    }

    return frameworks.map(fw => `
      <div class="framework-item">
        <div class="framework-name">${fw.name}</div>
        <div class="framework-score">${fw.score || 0}%</div>
        <div class="framework-issues">
          ${fw.issues || 0} issues
        </div>
        <div class="framework-status">
          <span class="status-badge ${fw.status === "compliant" ? "enabled" : (fw.status === "partial" ? "partial" : "disabled")}">
            ${fw.status === "compliant" ? "✓ Compliant" : (fw.status === "partial" ? "~ Partial" : "✗ Non-Compliant")}
          </span>
        </div>
      </div>
    `).join("");
  }

  update(newData) {
    this.data = { ...this.data, ...newData };
    this.render();
  }
}

// Export for module usage
if (typeof module !== "undefined" && module.exports) {
  module.exports = SecurityTab;
}
