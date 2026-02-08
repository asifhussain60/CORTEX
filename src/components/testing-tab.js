/**
 * Testing Tab Component (🧪)
 * Displays test coverage, test counts, failing tests, and code quality metrics
 * 
 * Features:
 * - Test coverage tracking and trending
 * - Test count breakdown (passing, failing, skipped)
 * - Test type classification (unit, integration, e2e)
 * - Failing test tracking and prioritization
 * - Module-level coverage analysis
 */

class TestingTab {
  constructor(containerSelector, data) {
    this.container = document.querySelector(containerSelector);
    this.data = data;
    this.init();
  }

  init() {
    if (!this.container) {
      console.error("Container not found");
      return;
    }
    this.render();
  }

  render() {
    const coverage = this.data.coverage_percentage || 0;
    const health = this.getTestHealth();

    this.container.innerHTML = `
      <div class="testing-tab">
        <div class="testing-header">
          <h2>🧪 Testing & Quality</h2>
          <div class="coverage-indicator ${health.class}">
            <div class="coverage-circle">
              <svg width="120" height="120" viewBox="0 0 120 120">
                <circle cx="60" cy="60" r="50" fill="none" stroke="#e0e0e0" stroke-width="8"/>
                <circle cx="60" cy="60" r="50" fill="none" stroke="${health.color}" stroke-width="8"
                        stroke-dasharray="${coverage * 3.14}" stroke-dashoffset="0"
                        transform="rotate(-90 60 60)" style="transition: stroke-dasharray 0.3s ease;"/>
                <text x="60" y="70" text-anchor="middle" font-size="32" font-weight="bold" fill="${health.color}">
                  ${coverage.toFixed(0)}%
                </text>
              </svg>
            </div>
            <div class="health-label">${health.label}</div>
          </div>
        </div>

        <div class="testing-content">
          ${this.renderCoverageOverview()}
          ${this.renderTestCounts()}
          ${this.renderTestTypes()}
          ${this.renderCoverageByModule()}
          ${this.renderFailingTests()}
        </div>
      </div>

      <style>
        .testing-tab {
          padding: 20px;
          background: #f5f5f5;
        }

        .testing-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 30px;
          border-bottom: 2px solid #ddd;
          padding-bottom: 15px;
        }

        .testing-header h2 {
          margin: 0;
          font-size: 28px;
        }

        .coverage-indicator {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 10px;
          padding: 15px;
          background: white;
          border-radius: 8px;
        }

        .coverage-circle {
          width: 120px;
          height: 120px;
        }

        .health-label {
          font-size: 14px;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 1px;
        }

        .testing-content {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 20px;
        }

        .testing-card {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .testing-card h3 {
          margin: 0 0 15px 0;
          font-size: 16px;
          border-bottom: 2px solid #e0e0e0;
          padding-bottom: 10px;
        }

        .coverage-trend-chart {
          height: 150px;
          position: relative;
          margin-bottom: 10px;
        }

        .trend-line {
          position: absolute;
          bottom: 0;
          left: 0;
          right: 0;
          height: 100px;
          border-left: 1px solid #e0e0e0;
          border-bottom: 1px solid #e0e0e0;
        }

        .trend-point {
          position: absolute;
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: #667eea;
          transform: translate(-3px, 3px);
          bottom: 0;
        }

        .test-count-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 10px;
          margin-bottom: 8px;
          background: #f9f9f9;
          border-radius: 4px;
          border-left: 3px solid;
        }

        .test-count-item.passing {
          border-left-color: #4caf50;
        }

        .test-count-item.failing {
          border-left-color: #f44336;
        }

        .test-count-item.skipped {
          border-left-color: #ffc107;
        }

        .test-count-label {
          font-weight: 500;
          flex: 1;
        }

        .test-count-value {
          font-size: 18px;
          font-weight: 700;
          margin-left: 10px;
        }

        .test-count-percentage {
          font-size: 12px;
          color: #999;
          margin-left: 10px;
          min-width: 50px;
          text-align: right;
        }

        .test-types-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 10px;
        }

        .test-type-box {
          padding: 15px;
          background: #f0f0f0;
          border-radius: 4px;
          text-align: center;
        }

        .test-type-count {
          font-size: 24px;
          font-weight: 700;
          line-height: 1;
          margin-bottom: 5px;
        }

        .test-type-label {
          font-size: 12px;
          font-weight: 500;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          color: #666;
        }

        .module-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 10px;
          margin-bottom: 8px;
          background: #f9f9f9;
          border-radius: 4px;
        }

        .module-name {
          font-weight: 500;
          flex: 1;
        }

        .module-bar {
          flex: 1;
          height: 6px;
          background: #e0e0e0;
          border-radius: 3px;
          margin: 0 10px;
          overflow: hidden;
        }

        .module-fill {
          height: 100%;
          background: linear-gradient(90deg, #4caf50, #45a049);
        }

        .module-coverage {
          min-width: 50px;
          text-align: right;
          font-weight: 600;
          font-size: 12px;
        }

        .failing-tests-section {
          grid-column: 1 / -1;
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .failing-tests-section h3 {
          margin: 0 0 15px 0;
          font-size: 16px;
          border-bottom: 2px solid #e0e0e0;
          padding-bottom: 10px;
        }

        .failing-test-item {
          padding: 12px;
          margin-bottom: 10px;
          border-radius: 4px;
          background: #ffebee;
          border-left: 3px solid #f44336;
        }

        .failing-test-name {
          font-weight: 600;
          margin-bottom: 3px;
        }

        .failing-test-file {
          font-size: 12px;
          color: #666;
          font-family: monospace;
          margin-bottom: 5px;
        }

        .failing-test-error {
          font-size: 12px;
          color: #666;
          margin-bottom: 5px;
        }

        .failing-test-priority {
          display: inline-block;
          padding: 2px 6px;
          border-radius: 3px;
          font-size: 11px;
          font-weight: 600;
          text-transform: uppercase;
        }

        .failing-test-priority.high {
          background: #ffc107;
          color: #333;
        }

        .failing-test-priority.medium {
          background: #ff9800;
          color: white;
        }

        .empty-state {
          padding: 20px;
          text-align: center;
          color: #999;
        }
      </style>
    `;
  }

  renderCoverageOverview() {
    const trend = this.data.coverage_trend || [];

    return `
      <div class="testing-card">
        <h3>📊 Coverage Trend</h3>
        <div class="coverage-trend-chart">
          <div class="trend-line"></div>
          ${trend.slice(-10).map((p, i, arr) => {
            const pct = (i / Math.max(arr.length - 1, 1)) * 100;
            const height = (p.value / 100) * 100;
            return `<div class="trend-point" style="left: ${pct}%; bottom: ${height}%;"></div>`;
          }).join("")}
        </div>
        <div style="font-size: 12px; color: #666;">
          Current: <strong>${this.data.coverage_percentage.toFixed(1)}%</strong>
          ${trend.length > 1 ? `| Change: <strong>${(this.data.coverage_percentage - trend[0].value).toFixed(1)}%</strong>` : ""}
        </div>
      </div>
    `;
  }

  renderTestCounts() {
    const counts = this.data.test_counts;
    const total = counts.total || 1;

    return `
      <div class="testing-card">
        <h3>🎯 Test Counts</h3>
        
        <div class="test-count-item passing">
          <span class="test-count-label">✓ Passing</span>
          <span class="test-count-percentage">${((counts.passing / total) * 100).toFixed(0)}%</span>
          <span class="test-count-value">${counts.passing}</span>
        </div>

        <div class="test-count-item failing">
          <span class="test-count-label">✗ Failing</span>
          <span class="test-count-percentage">${((counts.failing / total) * 100).toFixed(0)}%</span>
          <span class="test-count-value">${counts.failing}</span>
        </div>

        <div class="test-count-item skipped">
          <span class="test-count-label">⊘ Skipped</span>
          <span class="test-count-percentage">${((counts.skipped / total) * 100).toFixed(0)}%</span>
          <span class="test-count-value">${counts.skipped}</span>
        </div>

        <div style="margin-top: 10px; padding: 10px; background: #e3f2fd; border-radius: 4px; font-size: 12px;">
          Total: <strong>${counts.total}</strong> tests
        </div>
      </div>
    `;
  }

  renderTestTypes() {
    const types = this.data.test_types;
    const total = (types.unit || 0) + (types.integration || 0) + (types.e2e || 0) || 1;

    return `
      <div class="testing-card">
        <h3>🔬 Test Types</h3>
        <div class="test-types-grid">
          <div class="test-type-box">
            <div class="test-type-count">${types.unit || 0}</div>
            <div class="test-type-label">Unit</div>
            <div style="font-size: 11px; color: #999;">
              ${((types.unit || 0) / total * 100).toFixed(0)}%
            </div>
          </div>
          <div class="test-type-box">
            <div class="test-type-count">${types.integration || 0}</div>
            <div class="test-type-label">Integration</div>
            <div style="font-size: 11px; color: #999;">
              ${((types.integration || 0) / total * 100).toFixed(0)}%
            </div>
          </div>
          <div class="test-type-box">
            <div class="test-type-count">${types.e2e || 0}</div>
            <div class="test-type-label">E2E</div>
            <div style="font-size: 11px; color: #999;">
              ${((types.e2e || 0) / total * 100).toFixed(0)}%
            </div>
          </div>
        </div>
      </div>
    `;
  }

  renderCoverageByModule() {
    const modules = this.data.coverage_by_module || {};
    const moduleList = Object.entries(modules);

    if (moduleList.length === 0) {
      return `
        <div class="testing-card">
          <h3>📦 Module Coverage</h3>
          <div class="empty-state">No module data</div>
        </div>
      `;
    }

    return `
      <div class="testing-card">
        <h3>📦 Module Coverage</h3>
        ${moduleList.slice(0, 5).map(([name, coverage]) => `
          <div class="module-item">
            <span class="module-name">${name}</span>
            <div class="module-bar">
              <div class="module-fill" style="width: ${coverage}%"></div>
            </div>
            <span class="module-coverage">${coverage.toFixed(0)}%</span>
          </div>
        `).join("")}
        ${moduleList.length > 5 ? `
          <div style="padding: 10px; font-size: 12px; color: #999;">
            ... and ${moduleList.length - 5} more modules
          </div>
        ` : ""}
      </div>
    `;
  }

  renderFailingTests() {
    const failing = this.data.failing_tests || [];

    if (failing.length === 0) {
      return `
        <div class="failing-tests-section">
          <h3>✓ Failing Tests</h3>
          <div class="empty-state">All tests passing! 🎉</div>
        </div>
      `;
    }

    return `
      <div class="failing-tests-section">
        <h3>⚠️ Failing Tests (${failing.length})</h3>
        ${failing.slice(0, 10).map(test => `
          <div class="failing-test-item">
            <div class="failing-test-name">${test.name}</div>
            <div class="failing-test-file">${test.file}</div>
            <div class="failing-test-error">${test.error}</div>
            <span class="failing-test-priority ${test.priority}">
              ${test.priority} priority
            </span>
          </div>
        `).join("")}
        ${failing.length > 10 ? `
          <div style="padding: 10px; font-size: 12px; color: #999;">
            ... and ${failing.length - 10} more failing tests
          </div>
        ` : ""}
      </div>
    `;
  }

  getTestHealth() {
    const coverage = this.data.coverage_percentage || 0;
    const failing = (this.data.test_counts?.failing) || 0;

    if (failing > 0) {
      return {
        label: "FAILING",
        class: "critical",
        color: "#f44336"
      };
    } else if (coverage >= 90) {
      return {
        label: "EXCELLENT",
        class: "excellent",
        color: "#4caf50"
      };
    } else if (coverage >= 75) {
      return {
        label: "GOOD",
        class: "good",
        color: "#8bc34a"
      };
    } else if (coverage >= 50) {
      return {
        label: "FAIR",
        class: "fair",
        color: "#ffc107"
      };
    }

    return {
      label: "POOR",
      class: "poor",
      color: "#f44336"
    };
  }

  update(newData) {
    this.data = { ...this.data, ...newData };
    this.render();
  }
}

// Export for module usage
if (typeof module !== "undefined" && module.exports) {
  module.exports = TestingTab;
}
