/**
 * Patterns Tab Component (🎨)
 * Displays design patterns, anti-patterns, SOLID principles, and refactoring opportunities
 * 
 * Features:
 * - Design pattern detection and usage tracking
 * - Anti-pattern and code smell detection
 * - SOLID principles compliance scores
 * - Refactoring opportunity prioritization
 */

class PatternsTab {
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
    const solidScore = this.getAverageSOLIDScore();

    this.container.innerHTML = `
      <div class="patterns-tab">
        <div class="patterns-header">
          <h2>🎨 Code Patterns & Quality</h2>
          <div class="solid-score-badge">
            <div class="score-value">${solidScore.toFixed(1)}</div>
            <div class="score-label">SOLID Score</div>
          </div>
        </div>

        <div class="patterns-grid">
          ${this.renderDesignPatterns()}
          ${this.renderSOLIDPrinciples()}
          ${this.renderAntiPatterns()}
          ${this.renderRefactoringOpportunities()}
        </div>
      </div>

      <style>
        .patterns-tab {
          padding: 20px;
          background: #f5f5f5;
        }

        .patterns-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 30px;
          border-bottom: 2px solid #ddd;
          padding-bottom: 15px;
        }

        .patterns-header h2 {
          margin: 0;
          font-size: 28px;
        }

        .solid-score-badge {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          width: 100px;
          height: 100px;
          border-radius: 50%;
          background: linear-gradient(135deg, #667eea, #764ba2);
          color: white;
          box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }

        .score-value {
          font-size: 36px;
          font-weight: 700;
          line-height: 1;
        }

        .score-label {
          font-size: 11px;
          margin-top: 5px;
          text-transform: uppercase;
          letter-spacing: 1px;
          font-weight: 600;
        }

        .patterns-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 20px;
        }

        .pattern-card {
          background: white;
          padding: 20px;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .pattern-card h3 {
          margin: 0 0 15px 0;
          font-size: 16px;
          border-bottom: 2px solid #e0e0e0;
          padding-bottom: 10px;
        }

        .design-pattern-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 10px;
          margin-bottom: 8px;
          border-radius: 4px;
          background: #f9f9f9;
          border-left: 3px solid #667eea;
        }

        .pattern-name {
          font-weight: 500;
          flex: 1;
        }

        .pattern-count {
          background: #667eea;
          color: white;
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 600;
          margin-left: 10px;
        }

        .solid-principles-grid {
          display: grid;
          gap: 10px;
        }

        .solid-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 10px;
          background: #f9f9f9;
          border-radius: 4px;
        }

        .solid-label {
          font-size: 13px;
          font-weight: 500;
          flex: 1;
          margin-right: 10px;
        }

        .solid-bar {
          flex: 1;
          height: 8px;
          background: #e0e0e0;
          border-radius: 4px;
          overflow: hidden;
          margin-right: 10px;
        }

        .solid-fill {
          height: 100%;
          background: linear-gradient(90deg, #667eea, #764ba2);
          transition: width 0.3s ease;
        }

        .solid-score {
          min-width: 40px;
          text-align: right;
          font-weight: 600;
          font-size: 12px;
        }

        .anti-pattern-item {
          padding: 12px;
          margin-bottom: 10px;
          border-radius: 4px;
          background: #fff3e0;
          border-left: 3px solid #ff9800;
        }

        .anti-pattern-item.critical {
          background: #ffebee;
          border-left-color: #f44336;
        }

        .anti-pattern-name {
          font-weight: 600;
          margin-bottom: 3px;
        }

        .anti-pattern-severity {
          font-size: 12px;
          color: #666;
          margin-bottom: 5px;
        }

        .anti-pattern-remediation {
          font-size: 12px;
          color: #666;
          font-style: italic;
        }

        .refactoring-item {
          padding: 12px;
          margin-bottom: 10px;
          border-radius: 4px;
          background: #e3f2fd;
          border-left: 3px solid #1976d2;
        }

        .refactoring-item.high-priority {
          background: #fff3e0;
          border-left-color: #ff9800;
        }

        .refactoring-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 5px;
        }

        .refactoring-title {
          font-weight: 600;
        }

        .refactoring-effort {
          font-size: 12px;
          background: rgba(0,0,0,0.1);
          padding: 2px 6px;
          border-radius: 3px;
        }

        .refactoring-file {
          font-size: 12px;
          color: #666;
          margin-bottom: 5px;
          font-family: monospace;
        }

        .refactoring-description {
          font-size: 12px;
          color: #666;
        }

        .empty-state {
          padding: 20px;
          text-align: center;
          color: #999;
        }
      </style>
    `;
  }

  renderDesignPatterns() {
    const patterns = this.data.design_patterns || [];

    if (patterns.length === 0) {
      return `
        <div class="pattern-card">
          <h3>📋 Design Patterns</h3>
          <div class="empty-state">No patterns detected</div>
        </div>
      `;
    }

    return `
      <div class="pattern-card">
        <h3>📋 Design Patterns (${patterns.length})</h3>
        ${patterns.slice(0, 5).map(p => `
          <div class="design-pattern-item">
            <div class="pattern-name">${p.name}</div>
            <div class="pattern-count">${p.usage_count}</div>
          </div>
        `).join("")}
        ${patterns.length > 5 ? `
          <div style="padding: 10px; font-size: 12px; color: #999;">
            ... and ${patterns.length - 5} more
          </div>
        ` : ""}
      </div>
    `;
  }

  renderSOLIDPrinciples() {
    const solid = this.data.solid_principles;

    if (!solid) {
      return `
        <div class="pattern-card">
          <h3>⭐ SOLID Principles</h3>
          <div class="empty-state">No data available</div>
        </div>
      `;
    }

    const principles = [
      { label: "Single Responsibility", value: solid.single_responsibility },
      { label: "Open/Closed", value: solid.open_closed },
      { label: "Liskov Substitution", value: solid.liskov_substitution },
      { label: "Interface Segregation", value: solid.interface_segregation },
      { label: "Dependency Inversion", value: solid.dependency_inversion }
    ];

    return `
      <div class="pattern-card">
        <h3>⭐ SOLID Principles</h3>
        <div class="solid-principles-grid">
          ${principles.map(p => `
            <div class="solid-item">
              <span class="solid-label">${p.label}</span>
              <div class="solid-bar">
                <div class="solid-fill" style="width: ${p.value}%"></div>
              </div>
              <span class="solid-score">${p.value.toFixed(0)}%</span>
            </div>
          `).join("")}
        </div>
      </div>
    `;
  }

  renderAntiPatterns() {
    const antiPatterns = this.data.anti_patterns || [];

    if (antiPatterns.length === 0) {
      return `
        <div class="pattern-card">
          <h3>⚠️ Anti-Patterns</h3>
          <div class="empty-state">✓ No code smells detected</div>
        </div>
      `;
    }

    return `
      <div class="pattern-card">
        <h3>⚠️ Anti-Patterns (${antiPatterns.length})</h3>
        ${antiPatterns.slice(0, 3).map(ap => `
          <div class="anti-pattern-item ${ap.severity === "critical" ? "critical" : ""}">
            <div class="anti-pattern-name">${ap.name}</div>
            <div class="anti-pattern-severity">
              Severity: <strong>${ap.severity}</strong> | Count: <strong>${ap.count}</strong>
            </div>
            <div class="anti-pattern-remediation">💡 ${ap.remediation}</div>
          </div>
        `).join("")}
        ${antiPatterns.length > 3 ? `
          <div style="padding: 10px; font-size: 12px; color: #999;">
            ... and ${antiPatterns.length - 3} more
          </div>
        ` : ""}
      </div>
    `;
  }

  renderRefactoringOpportunities() {
    const opportunities = this.data.refactoring_opportunities || [];

    if (opportunities.length === 0) {
      return `
        <div class="pattern-card">
          <h3>🔧 Refactoring Opportunities</h3>
          <div class="empty-state">✓ Code looks good!</div>
        </div>
      `;
    }

    const total_hours = opportunities.reduce((sum, o) => sum + o.effort_hours, 0);

    return `
      <div class="pattern-card">
        <h3>🔧 Refactoring (${opportunities.length} items, ${total_hours.toFixed(1)}h)</h3>
        ${opportunities.slice(0, 3).map(opp => `
          <div class="refactoring-item ${opp.priority === "high" ? "high-priority" : ""}">
            <div class="refactoring-header">
              <span class="refactoring-title">${opp.type}</span>
              <span class="refactoring-effort">${opp.effort_hours}h</span>
            </div>
            <div class="refactoring-file">${opp.file}</div>
            <div class="refactoring-description">${opp.description}</div>
          </div>
        `).join("")}
        ${opportunities.length > 3 ? `
          <div style="padding: 10px; font-size: 12px; color: #999;">
            ... and ${opportunities.length - 3} more
          </div>
        ` : ""}
      </div>
    `;
  }

  getAverageSOLIDScore() {
    const solid = this.data.solid_principles;
    if (!solid) return 0;

    const scores = [
      solid.single_responsibility,
      solid.open_closed,
      solid.liskov_substitution,
      solid.interface_segregation,
      solid.dependency_inversion
    ];

    return scores.reduce((a, b) => a + b, 0) / scores.length;
  }

  update(newData) {
    this.data = { ...this.data, ...newData };
    this.render();
  }
}

// Export for module usage
if (typeof module !== "undefined" && module.exports) {
  module.exports = PatternsTab;
}
