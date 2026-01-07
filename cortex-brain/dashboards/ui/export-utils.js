/**
 * Export Utilities Module
 * 
 * Provides export functionality for dashboard data in multiple formats:
 * - JSON download
 * - CSV generation
 * - PDF report export
 * - PNG chart export
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 * License: Source-Available (Use Allowed, No Contributions)
 */

import { showSuccessToast, showErrorToast, showLoading, hideLoading } from './shared-utils.js';

/**
 * Export data as JSON file
 * @param {Object} data - Data to export
 * @param {string} filename - Output filename (without extension)
 */
export function exportToJson(data, filename = 'dashboard-data') {
    try {
        const jsonString = JSON.stringify(data, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json' });
        downloadFile(blob, `${filename}.json`);
        showSuccessToast('JSON exported successfully');
    } catch (error) {
        console.error('JSON export failed:', error);
        showErrorToast('Failed to export JSON');
    }
}

/**
 * Export data as CSV file
 * @param {Array} data - Array of objects to export
 * @param {string} filename - Output filename (without extension)
 * @param {Array} columns - Column names to include (optional)
 */
export function exportToCsv(data, filename = 'dashboard-data', columns = null) {
    try {
        if (!Array.isArray(data) || data.length === 0) {
            throw new Error('Data must be a non-empty array');
        }
        
        // Get columns from first object if not specified
        const headers = columns || Object.keys(data[0]);
        
        // Build CSV string
        let csv = headers.join(',') + '\n';
        
        data.forEach(row => {
            const values = headers.map(header => {
                let value = row[header] !== undefined ? row[header] : '';
                // Escape quotes and wrap in quotes if contains comma
                value = String(value).replace(/"/g, '""');
                if (value.includes(',') || value.includes('\n') || value.includes('"')) {
                    value = `"${value}"`;
                }
                return value;
            });
            csv += values.join(',') + '\n';
        });
        
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        downloadFile(blob, `${filename}.csv`);
        showSuccessToast('CSV exported successfully');
    } catch (error) {
        console.error('CSV export failed:', error);
        showErrorToast('Failed to export CSV');
    }
}

/**
 * Export current view as PDF using print stylesheet
 * @param {string} title - Document title
 */
export function exportToPdf(title = 'Dashboard Report') {
    try {
        showLoading('Preparing PDF export...');
        
        // Set document title
        const originalTitle = document.title;
        document.title = title;
        
        // Add print-specific styles
        const printStyle = document.createElement('style');
        printStyle.id = 'print-styles';
        printStyle.textContent = `
            @media print {
                @page {
                    size: A4;
                    margin: 1cm;
                }
                
                body {
                    background: white !important;
                    color: black !important;
                }
                
                .sidebar,
                .header-actions,
                button,
                .loading-overlay,
                .toast {
                    display: none !important;
                }
                
                .content-area {
                    margin-left: 0 !important;
                    width: 100% !important;
                }
                
                .glass-card {
                    background: white !important;
                    border: 1px solid #ddd !important;
                    box-shadow: none !important;
                    page-break-inside: avoid;
                    margin-bottom: 1rem;
                }
                
                h1, h2, h3 {
                    page-break-after: avoid;
                }
                
                svg {
                    max-width: 100%;
                    height: auto;
                }
            }
        `;
        document.head.appendChild(printStyle);
        
        // Wait for styles to apply
        setTimeout(() => {
            hideLoading();
            window.print();
            
            // Cleanup
            document.title = originalTitle;
            printStyle.remove();
            
            showSuccessToast('PDF export initiated - use your browser\'s print dialog');
        }, 500);
        
    } catch (error) {
        console.error('PDF export failed:', error);
        hideLoading();
        showErrorToast('Failed to export PDF');
    }
}

/**
 * Export a specific element as PNG image
 * @param {string} elementId - ID of element to export
 * @param {string} filename - Output filename (without extension)
 */
export async function exportToPng(elementId, filename = 'chart') {
    try {
        const element = document.getElementById(elementId);
        if (!element) {
            throw new Error(`Element ${elementId} not found`);
        }
        
        showLoading('Generating PNG...');
        
        // Check if html2canvas is available
        if (typeof html2canvas === 'undefined') {
            throw new Error('html2canvas library not loaded');
        }
        
        const canvas = await html2canvas(element, {
            backgroundColor: '#0a0e27',
            scale: 2, // Higher resolution
            logging: false
        });
        
        canvas.toBlob(blob => {
            downloadFile(blob, `${filename}.png`);
            hideLoading();
            showSuccessToast('PNG exported successfully');
        });
        
    } catch (error) {
        console.error('PNG export failed:', error);
        hideLoading();
        showErrorToast('Failed to export PNG - html2canvas library may not be loaded');
    }
}

/**
 * Export SVG element as PNG
 * @param {string} svgId - ID of SVG element
 * @param {string} filename - Output filename (without extension)
 */
export function exportSvgToPng(svgId, filename = 'chart') {
    try {
        const svg = document.getElementById(svgId);
        if (!svg) {
            throw new Error(`SVG element ${svgId} not found`);
        }
        
        showLoading('Generating PNG from SVG...');
        
        // Get SVG dimensions
        const bbox = svg.getBBox();
        const width = bbox.width;
        const height = bbox.height;
        
        // Create canvas
        const canvas = document.createElement('canvas');
        canvas.width = width * 2; // Higher resolution
        canvas.height = height * 2;
        const ctx = canvas.getContext('2d');
        
        // Scale for high DPI
        ctx.scale(2, 2);
        
        // Create image from SVG
        const svgString = new XMLSerializer().serializeToString(svg);
        const blob = new Blob([svgString], { type: 'image/svg+xml;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        
        const img = new Image();
        img.onload = () => {
            ctx.drawImage(img, 0, 0);
            canvas.toBlob(blob => {
                downloadFile(blob, `${filename}.png`);
                URL.revokeObjectURL(url);
                hideLoading();
                showSuccessToast('PNG exported successfully');
            });
        };
        
        img.onerror = () => {
            hideLoading();
            showErrorToast('Failed to export SVG as PNG');
        };
        
        img.src = url;
        
    } catch (error) {
        console.error('SVG to PNG export failed:', error);
        hideLoading();
        showErrorToast('Failed to export SVG');
    }
}

/**
 * Generate complete dashboard report with all data
 * @param {Object} dashboardData - Complete dashboard data
 * @param {string} source - Data source name
 */
export function generateFullReport(dashboardData, source = 'mock') {
    try {
        showLoading('Generating full report...');
        
        const report = {
            generated_at: new Date().toISOString(),
            source: source,
            report_type: 'full_dashboard_export',
            data: {
                health: dashboardData.healthData,
                tech_stack: dashboardData.techStack,
                security: dashboardData.security,
                architecture: dashboardData.architecture,
                code_organization: dashboardData.codeOrganization,
                team_metrics: dashboardData.teamMetrics,
                vendors: dashboardData.vendors
            },
            metadata: {
                export_version: '1.0.0',
                dashboard_version: '3.0.0',
                user_agent: navigator.userAgent,
                screen_resolution: `${window.screen.width}x${window.screen.height}`
            }
        };
        
        hideLoading();
        exportToJson(report, `dashboard-full-report-${source}-${Date.now()}`);
        
    } catch (error) {
        console.error('Full report generation failed:', error);
        hideLoading();
        showErrorToast('Failed to generate full report');
    }
}

/**
 * Export tech stack data as CSV
 * @param {Object} techStack - Tech stack data
 */
export function exportTechStackCsv(techStack) {
    try {
        const allTechnologies = [
            ...techStack.frontend.map(t => ({ ...t, category: 'Frontend' })),
            ...techStack.backend.map(t => ({ ...t, category: 'Backend' })),
            ...techStack.database.map(t => ({ ...t, category: 'Database' })),
            ...techStack.devops.map(t => ({ ...t, category: 'DevOps' }))
        ];
        
        exportToCsv(
            allTechnologies,
            `tech-stack-${Date.now()}`,
            ['name', 'category', 'version', 'latest', 'status', 'cve_count']
        );
    } catch (error) {
        console.error('Tech stack CSV export failed:', error);
        showErrorToast('Failed to export tech stack');
    }
}

/**
 * Export security vulnerabilities as CSV
 * @param {Object} security - Security data
 */
export function exportSecurityCsv(security) {
    try {
        const owaspData = security.owasp_top_10.map(item => ({
            risk_id: item.risk,
            name: item.name,
            score: item.score,
            status: item.status
        }));
        
        exportToCsv(
            owaspData,
            `security-owasp-${Date.now()}`,
            ['risk_id', 'name', 'score', 'status']
        );
    } catch (error) {
        console.error('Security CSV export failed:', error);
        showErrorToast('Failed to export security data');
    }
}

/**
 * Export code hotspots as CSV
 * @param {Array} hotspots - Hotspots array
 */
export function exportHotspotsCsv(hotspots) {
    try {
        exportToCsv(
            hotspots,
            `code-hotspots-${Date.now()}`,
            ['file', 'risk_score', 'complexity', 'change_frequency', 'recommendation']
        );
    } catch (error) {
        console.error('Hotspots CSV export failed:', error);
        showErrorToast('Failed to export hotspots');
    }
}

/**
 * Export team contributors as CSV
 * @param {Array} contributors - Contributors array
 */
export function exportTeamCsv(contributors) {
    try {
        exportToCsv(
            contributors,
            `team-contributors-${Date.now()}`,
            ['name', 'commits', 'lines_added', 'lines_removed', 'files_changed']
        );
    } catch (error) {
        console.error('Team CSV export failed:', error);
        showErrorToast('Failed to export team data');
    }
}

/**
 * Export vendors as CSV
 * @param {Array} vendors - Vendors array
 */
export function exportVendorsCsv(vendors) {
    try {
        const vendorData = vendors.map(v => ({
            name: v.name,
            category: v.category,
            status: v.status,
            confidence: v.detection_confidence,
            integration_points: v.integration_points,
            last_used: v.last_used
        }));
        
        exportToCsv(
            vendorData,
            `vendors-${Date.now()}`,
            ['name', 'category', 'status', 'confidence', 'integration_points', 'last_used']
        );
    } catch (error) {
        console.error('Vendors CSV export failed:', error);
        showErrorToast('Failed to export vendors');
    }
}

/**
 * Download file helper
 * @param {Blob} blob - File blob
 * @param {string} filename - Filename with extension
 */
function downloadFile(blob, filename) {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

/**
 * Copy data to clipboard as JSON
 * @param {Object} data - Data to copy
 */
export async function copyToClipboard(data) {
    try {
        const jsonString = JSON.stringify(data, null, 2);
        await navigator.clipboard.writeText(jsonString);
        showSuccessToast('Copied to clipboard');
    } catch (error) {
        console.error('Copy to clipboard failed:', error);
        showErrorToast('Failed to copy to clipboard');
    }
}

/**
 * Share data via Web Share API (if available)
 * @param {Object} data - Data to share
 * @param {string} title - Share title
 */
export async function shareData(data, title = 'Dashboard Data') {
    try {
        if (!navigator.share) {
            throw new Error('Web Share API not supported');
        }
        
        const jsonString = JSON.stringify(data, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json' });
        const file = new File([blob], 'dashboard-data.json', { type: 'application/json' });
        
        await navigator.share({
            title: title,
            text: 'Dashboard data export',
            files: [file]
        });
        
        showSuccessToast('Shared successfully');
    } catch (error) {
        console.error('Share failed:', error);
        showErrorToast('Sharing not supported or cancelled');
    }
}
