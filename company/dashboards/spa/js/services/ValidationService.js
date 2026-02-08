/**
 * ValidationService - Data Integrity and Security Validation
 * 
 * Addresses Critical Issues:
 * - No data validation before rendering
 * - XSS vulnerabilities (unsanitized HTML)
 * - Trust boundary violations
 * 
 * Authority: violations.md § Data Integrity Theater & Security
 * Audit: AC_START: AC-SPA-001-04
 */

class ValidationService {
    constructor() {
        this.issues = [];
    }
    
    /**
     * Validate repository data integrity
     * @param {Object} data - Repository data
     * @returns {Object} { valid, issues, warnings }
     */
    validateDataIntegrity(data) {
        this.issues = [];
        
        // Check description vs business summary contradiction
        this._checkDescriptionContradiction(data);
        
        // Check LOC=0 with language counts
        this._checkLOCInconsistency(data);
        
        // Check files=0 with languages
        this._checkFilesInconsistency(data);
        
        // Check dependency inconsistencies
        this._checkDependencyInconsistency(data);
        
        // Check health score consistency
        this._checkHealthScoreConsistency(data);
        
        return {
            valid: this.issues.filter(i => i.severity === 'error').length === 0,
            issues: this.issues.filter(i => i.severity === 'error'),
            warnings: this.issues.filter(i => i.severity === 'warning')
        };
    }
    
    /**
     * Sanitize HTML to prevent XSS
     * @param {String} html - Raw HTML
     * @returns {String} Sanitized HTML
     */
    sanitizeHTML(html) {
        if (!html) return '';
        
        // Create temporary element
        const temp = document.createElement('div');
        temp.textContent = html;
        
        return temp.innerHTML;
    }
    
    /**
     * Sanitize for attribute values
     */
    sanitizeAttribute(value) {
        if (!value) return '';
        return String(value)
            .replace(/[<>"'&]/g, char => {
                const entities = {
                    '<': '&lt;',
                    '>': '&gt;',
                    '"': '&quot;',
                    "'": '&#39;',
                    '&': '&amp;'
                };
                return entities[char];
            });
    }
    
    /**
     * Check description contradiction
     */
    _checkDescriptionContradiction(data) {
        const desc = (data.metadata?.description || '').toLowerCase();
        const summary = (data.overview?.business_summary || '').toLowerCase();
        
        if (!desc || !summary) return;
        
        // Extract tech keywords
        const descTech = this._extractTechKeywords(desc);
        const summaryTech = this._extractTechKeywords(summary);
        
        // Check for contradictions
        const contradictions = [];
        for (const tech of descTech) {
            if (summaryTech.length > 0 && !summaryTech.includes(tech)) {
                contradictions.push(tech);
            }
        }
        
        if (contradictions.length > 0 && summaryTech.length > 0) {
            this.issues.push({
                type: 'contradiction',
                severity: 'warning',
                message: `Description mentions ${contradictions.join(', ')} but business summary describes different technology`,
                confidence: 0.85
            });
        }
    }
    
    /**
     * Check LOC inconsistency
     */
    _checkLOCInconsistency(data) {
        const loc = data.overview?.lines_of_code || 0;
        const languages = data.architecture?.languages || {};
        const totalLanguageLOC = Object.values(languages).reduce((sum, val) => sum + val, 0);
        
        if (loc === 0 && totalLanguageLOC > 0) {
            this.issues.push({
                type: 'extraction_incomplete',
                severity: 'error',
                message: `LOC reported as 0, but language counts show ${totalLanguageLOC} lines`,
                confidence: 1.0
            });
        }
    }
    
    /**
     * Check files inconsistency
     */
    _checkFilesInconsistency(data) {
        const files = data.overview?.total_files || 0;
        const languages = data.architecture?.languages || {};
        
        if (files === 0 && Object.keys(languages).length > 0) {
            this.issues.push({
                type: 'extraction_incomplete',
                severity: 'error',
                message: `Files reported as 0, but ${Object.keys(languages).length} languages detected`,
                confidence: 1.0
            });
        }
    }
    
    /**
     * Check dependency inconsistency
     */
    _checkDependencyInconsistency(data) {
        const direct = data.dependencies?.direct_count || 0;
        const transitive = data.dependencies?.transitive_count || 0;
        
        if (direct === 0 && transitive > 0) {
            this.issues.push({
                type: 'data_inconsistency',
                severity: 'warning',
                message: `No direct dependencies but ${transitive} transitive dependencies`,
                confidence: 0.9
            });
        }
    }
    
    /**
     * Check health score consistency
     */
    _checkHealthScoreConsistency(data) {
        const healthScore = data.metadata?.health_score || 0;
        const riskScore = data.metadata?.risk_score || 0;
        
        // Health and risk should be inversely related
        if (healthScore > 80 && riskScore > 80) {
            this.issues.push({
                type: 'score_inconsistency',
                severity: 'warning',
                message: `High health score (${healthScore}) but also high risk score (${riskScore})`,
                confidence: 0.75
            });
        }
    }
    
    /**
     * Extract tech keywords
     */
    _extractTechKeywords(text) {
        const keywords = [
            'python', 'javascript', 'typescript', 'java', 'csharp', 'c#',
            '.net', 'dotnet', 'react', 'vue', 'angular', 'django', 'flask',
            'spring', 'express', 'fastapi'
        ];
        
        return keywords.filter(keyword => text.includes(keyword));
    }
    
    /**
     * Validate schema structure
     */
    validateSchema(data) {
        const errors = [];
        
        // Check required fields
        const requiredFields = {
            'metadata': ['name', 'description', 'health_score'],
            'overview': ['business_summary', 'lines_of_code'],
            'architecture': ['languages', 'structure'],
            'quality': ['metrics'],
            'security': ['vulnerabilities'],
            'dependencies': ['packages']
        };
        
        for (const [section, fields] of Object.entries(requiredFields)) {
            if (!data[section]) {
                errors.push(`Missing section: ${section}`);
                continue;
            }
            
            for (const field of fields) {
                if (data[section][field] === undefined) {
                    errors.push(`Missing field: ${section}.${field}`);
                }
            }
        }
        
        return {
            valid: errors.length === 0,
            errors
        };
    }
    
    /**
     * Get integrity report
     */
    getIntegrityReport() {
        return {
            totalIssues: this.issues.length,
            errors: this.issues.filter(i => i.severity === 'error').length,
            warnings: this.issues.filter(i => i.severity === 'warning').length,
            issues: this.issues
        };
    }
}

// AC_COMPLETE: AC-SPA-001-04 ✅ ValidationService with XSS protection
