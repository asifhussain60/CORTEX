/**
 * DataIntegrityValidator - Data Contradiction Detection
 * 
 * Fixes GPR-003: Data Contradictions Make Dashboard Look Broken
 * - Detects internal contradictions in dataset
 * - Calculates data quality score
 * - Marks sections as Degraded when confidence is low
 * - Provides transparency about data issues
 * 
 * Authority: gpr-recommendation.txt § Root Cause #3
 */

class DataIntegrityValidator {
    constructor() {
        this.contradictions = [];
        this.missingFields = [];
        this.confidenceScore = 1.0;
        this.coveragePct = 100;
    }

    /**
     * Validate entire repository data structure
     * @param {Object} data - Repository data
     * @returns {Object} Validation result with status and issues
     */
    validate(data) {
        this.contradictions = [];
        this.missingFields = [];

        // Check each section for contradictions
        this._validateOverview(data.overview);
        this._validateMetrics(data.metrics);
        this._validateSecurity(data.security);
        this._validateDependencies(data.dependencies);
        this._validateLanguages(data.overview?.languages, data.metrics);

        // Calculate quality metrics
        this._calculateQualityMetrics();

        return {
            isHealthy: this.contradictions.length === 0,
            confidenceScore: this.confidenceScore,
            coveragePct: this.coveragePct,
            contradictions: this.contradictions,
            missingFields: this.missingFields,
            status: this._getStatus()
        };
    }

    /**
     * Validate overview section
     */
    _validateOverview(overview) {
        if (!overview) {
            this.contradictions.push({
                severity: 'critical',
                field: 'overview',
                issue: 'Overview section missing entirely'
            });
            return;
        }

        // Check description consistency
        if (overview.description && overview.business_summary) {
            const descLen = overview.description.length;
            const summaryLen = overview.business_summary.length;
            
            // If descriptions are vastly different in length, might indicate data issue
            if (descLen < 20 && summaryLen > 200) {
                this.contradictions.push({
                    severity: 'warning',
                    field: 'overview.description',
                    issue: 'Description is much shorter than business summary - possible data extraction issue',
                    actual: { description: descLen, summary: summaryLen }
                });
            }
        }

        if (!overview.description) {
            this.missingFields.push('overview.description');
        }
    }

    /**
     * Validate metrics section
     */
    _validateMetrics(metrics) {
        if (!metrics) {
            this.missingFields.push('metrics');
            return;
        }

        // Check files count vs language counts
        if (metrics.files === 0 && metrics.loc > 0) {
            this.contradictions.push({
                severity: 'error',
                field: 'metrics.files',
                issue: 'Files count is 0 but LOC count is non-zero - data extraction incomplete',
                actual: { files: metrics.files, loc: metrics.loc }
            });
        }

        // Check LOC consistency with languages
        if (metrics.loc > 0 && (!metrics.languages || Object.keys(metrics.languages).length === 0)) {
            this.contradictions.push({
                severity: 'warning',
                field: 'metrics.languages',
                issue: 'LOC count is high but no language breakdown provided',
                actual: { loc: metrics.loc, languagesCount: 0 }
            });
        }

        if (!metrics.files) this.missingFields.push('metrics.files');
        if (!metrics.loc) this.missingFields.push('metrics.loc');
    }

    /**
     * Validate security section
     */
    _validateSecurity(security) {
        if (!security) {
            this.missingFields.push('security');
            return;
        }

        // Check vulnerability contradictions
        if (security.total_vulnerabilities === 0 && security.summary && 
            security.summary.includes('vulnerabilities')) {
            this.contradictions.push({
                severity: 'error',
                field: 'security.total_vulnerabilities',
                issue: 'Total vulnerabilities is 0 but summary mentions vulnerabilities',
                actual: security.summary
            });
        }

        if (!security.total_vulnerabilities) this.missingFields.push('security.total_vulnerabilities');
    }

    /**
     * Validate dependencies section
     */
    _validateDependencies(dependencies) {
        if (!dependencies) {
            this.missingFields.push('dependencies');
            return;
        }

        // Check direct_count vs packages
        if (dependencies.direct_count === 0 && dependencies.packages && 
            Object.keys(dependencies.packages).length > 0) {
            this.contradictions.push({
                severity: 'error',
                field: 'dependencies.direct_count',
                issue: 'Direct count is 0 but packages list is non-empty',
                actual: { 
                    directCount: dependencies.direct_count, 
                    packagesCount: Object.keys(dependencies.packages).length 
                }
            });
        }

        if (!dependencies.direct_count) this.missingFields.push('dependencies.direct_count');
    }

    /**
     * Validate language data consistency
     */
    _validateLanguages(languages, metrics) {
        if (!languages) {
            this.missingFields.push('overview.languages');
            return;
        }

        // Check language count consistency
        const languageTotal = Object.values(languages).reduce((a, b) => a + b, 0);
        
        if (metrics && metrics.loc > 0 && languageTotal === 0) {
            this.contradictions.push({
                severity: 'error',
                field: 'overview.languages',
                issue: 'LOC metric is high but all language values are zero',
                actual: { metricsLOC: metrics.loc, languageTotal: languageTotal }
            });
        }
    }

    /**
     * Calculate overall quality metrics
     */
    _calculateQualityMetrics() {
        // Calculate confidence score (0-1.0)
        let score = 1.0;

        // Deduct for each issue
        score -= this.contradictions.filter(c => c.severity === 'critical').length * 0.3;
        score -= this.contradictions.filter(c => c.severity === 'error').length * 0.15;
        score -= this.contradictions.filter(c => c.severity === 'warning').length * 0.05;
        score -= this.missingFields.length * 0.02;

        this.confidenceScore = Math.max(0, Math.min(1.0, score));

        // Coverage percentage (100% - missing/20 fields expected)
        const expectedFields = 20;
        this.coveragePct = Math.max(0, 100 - (this.missingFields.length / expectedFields) * 100);
    }

    /**
     * Get human-readable status
     */
    _getStatus() {
        if (this.confidenceScore >= 0.9) {
            return { level: '✅ Healthy', color: '#10b981' };
        } else if (this.confidenceScore >= 0.7) {
            return { level: '⚠️ Degraded', color: '#f59e0b' };
        } else if (this.confidenceScore >= 0.5) {
            return { level: '❌ Poor', color: '#ef4444' };
        } else {
            return { level: '❌ Critical', color: '#b91c1c' };
        }
    }

    /**
     * Generate data quality report HTML
     */
    generateReport() {
        const report = document.createElement('div');
        report.className = 'data-integrity-report';
        report.innerHTML = `
            <div class="report-header">
                <h3>📊 Data Integrity Report</h3>
                <div class="report-status" style="color: ${this.confidenceScore >= 0.9 ? '#10b981' : '#f59e0b'}">
                    Confidence: ${(this.confidenceScore * 100).toFixed(0)}%
                </div>
            </div>

            ${this.contradictions.length > 0 ? `
                <div class="report-section">
                    <h4>⚠️ Detected Contradictions (${this.contradictions.length})</h4>
                    <ul class="contradiction-list">
                        ${this.contradictions.map(c => `
                            <li class="contradiction-${c.severity}">
                                <strong>${c.field}</strong>: ${c.issue}
                                ${c.actual ? `<br><small>Actual: ${JSON.stringify(c.actual)}</small>` : ''}
                            </li>
                        `).join('')}
                    </ul>
                </div>
            ` : ''}

            ${this.missingFields.length > 0 ? `
                <div class="report-section">
                    <h4>📭 Missing Fields (${this.missingFields.length})</h4>
                    <ul class="missing-list">
                        ${this.missingFields.map(f => `<li>${f}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}

            ${this.contradictions.length === 0 && this.missingFields.length === 0 ? `
                <div class="report-section">
                    <p style="color: #10b981; font-weight: 500;">✅ All data integrity checks passed</p>
                </div>
            ` : ''}

            <div class="report-footer">
                <small>Data Quality: ${this.coveragePct.toFixed(0)}% coverage | Confidence: ${(this.confidenceScore * 100).toFixed(0)}%</small>
            </div>
        `;

        return report;
    }

    /**
     * Generate degradation banner if needed
     */
    generateDegradationBanner() {
        if (this.confidenceScore >= 0.9) return null;

        const banner = document.createElement('div');
        banner.className = 'data-degradation-banner';
        banner.innerHTML = `
            <div class="banner-content">
                <span class="banner-icon">⚠️</span>
                <span class="banner-text">
                    Data Quality: ${(this.confidenceScore * 100).toFixed(0)}% 
                    ${this.contradictions.length} contradictions detected
                </span>
                <button class="banner-detail-btn">View Details</button>
            </div>
        `;

        banner.querySelector('.banner-detail-btn')?.addEventListener('click', () => {
            alert(this._formatDetailsForAlert());
        });

        return banner;
    }

    /**
     * Format details for alert/modal
     */
    _formatDetailsForAlert() {
        let text = 'Data Integrity Issues:\n\n';

        if (this.contradictions.length > 0) {
            text += 'CONTRADICTIONS:\n';
            this.contradictions.forEach(c => {
                text += `- [${c.severity}] ${c.field}: ${c.issue}\n`;
            });
            text += '\n';
        }

        if (this.missingFields.length > 0) {
            text += 'MISSING FIELDS:\n';
            this.missingFields.forEach(f => {
                text += `- ${f}\n`;
            });
        }

        text += `\nConfidence Score: ${(this.confidenceScore * 100).toFixed(0)}%`;
        text += `\nData Coverage: ${this.coveragePct.toFixed(0)}%`;

        return text;
    }

    /**
     * Static method for direct validation
     */
    static validate(data) {
        const validator = new DataIntegrityValidator();
        return validator.validate(data);
    }

    /**
     * Static method for report generation
     */
    static generateReport(data) {
        const validator = new DataIntegrityValidator();
        validator.validate(data);
        return validator.generateReport();
    }

    /**
     * Static method for banner generation
     */
    static generateBanner(data) {
        const validator = new DataIntegrityValidator();
        validator.validate(data);
        return validator.generateDegradationBanner();
    }
}

// Auto-initialize singleton
window.DataIntegrityValidator = DataIntegrityValidator;
