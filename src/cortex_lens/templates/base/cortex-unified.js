/**
 * CORTEX Unified JavaScript Framework
 * 
 * Features:
 * - Tab navigation
 * - Theme switching (dark/light)
 * - Chart.js integration
 * - Data injection from JSON
 * - Responsive interactions
 * 
 * Author: Asif Hussain
 * Version: 1.0.0
 * Date: December 2025
 */

// ========== Global State ==========
let analysisData = {};
let charts = {};

// ========== Initialization ==========
document.addEventListener('DOMContentLoaded', () => {
    initializeData();
    initializeTabs();
    initializeTheme();
    initializeCharts();
    console.log('🧠 CORTEX Dashboard initialized');
});

// ========== Data Loading ==========
function initializeData() {
    const dataScript = document.getElementById('analysisData');
    if (dataScript) {
        try {
            analysisData = JSON.parse(dataScript.textContent);
            console.log('📊 Analysis data loaded:', Object.keys(analysisData));
        } catch (error) {
            console.error('Failed to load analysis data:', error);
        }
    }
}

// ========== Tab Navigation ==========
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.dataset.tab;
            
            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked button and target content
            button.classList.add('active');
            const targetContent = document.getElementById(targetTab);
            if (targetContent) {
                targetContent.classList.add('active');
            }
            
            // Update URL hash
            window.location.hash = targetTab;
        });
    });
    
    // Handle initial hash or default to overview
    const initialTab = window.location.hash.slice(1) || 'overview';
    const initialButton = document.querySelector(`[data-tab="${initialTab}"]`);
    if (initialButton) {
        initialButton.click();
    }
}

// ========== Theme Management ==========
function initializeTheme() {
    // Check for saved theme or default to dark
    const savedTheme = localStorage.getItem('cortex-theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('cortex-theme', newTheme);
    updateThemeIcon(newTheme);
    
    // Update charts with new theme colors
    updateChartColors();
}

function updateThemeIcon(theme) {
    const themeIcon = document.querySelector('.theme-icon');
    if (themeIcon) {
        themeIcon.textContent = theme === 'dark' ? '🌙' : '☀️';
    }
}

// ========== Chart Management ==========
function initializeCharts() {
    // Language Distribution Chart
    const languageCanvas = document.getElementById('languageChart');
    if (languageCanvas && analysisData.languages) {
        charts.language = createLanguageChart(languageCanvas);
    }
    
    // Security Issues Chart
    const securityCanvas = document.getElementById('securityChart');
    if (securityCanvas && analysisData.security) {
        charts.security = createSecurityChart(securityCanvas);
    }
    
    // Coverage by Layer Chart
    const coverageCanvas = document.getElementById('coverageChart');
    if (coverageCanvas && analysisData.coverage) {
        charts.coverage = createCoverageChart(coverageCanvas);
    }
}

function createLanguageChart(canvas) {
    const ctx = canvas.getContext('2d');
    const colors = getChartColors();
    
    const data = {
        labels: analysisData.languages?.map(l => l.name) || [],
        datasets: [{
            data: analysisData.languages?.map(l => l.percentage) || [],
            backgroundColor: colors,
            borderColor: 'rgba(255, 255, 255, 0.1)',
            borderWidth: 2
        }]
    };
    
    return new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: getTextColor(),
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: ${context.parsed}%`;
                        }
                    }
                }
            }
        }
    });
}

function createSecurityChart(canvas) {
    const ctx = canvas.getContext('2d');
    
    const severityData = analysisData.security?.by_severity || {};
    
    const data = {
        labels: ['Critical', 'High', 'Medium', 'Low'],
        datasets: [{
            label: 'Vulnerabilities',
            data: [
                severityData.CRITICAL || 0,
                severityData.HIGH || 0,
                severityData.MEDIUM || 0,
                severityData.LOW || 0
            ],
            backgroundColor: [
                'rgba(255, 107, 157, 0.6)',
                'rgba(255, 182, 39, 0.6)',
                'rgba(0, 212, 255, 0.6)',
                'rgba(107, 122, 144, 0.6)'
            ],
            borderColor: [
                'rgba(255, 107, 157, 1)',
                'rgba(255, 182, 39, 1)',
                'rgba(0, 212, 255, 1)',
                'rgba(107, 122, 144, 1)'
            ],
            borderWidth: 2
        }]
    };
    
    return new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: getTextColor(),
                        precision: 0
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: getTextColor()
                    },
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

function createCoverageChart(canvas) {
    const ctx = canvas.getContext('2d');
    
    const coverageData = analysisData.coverage?.by_layer || {};
    
    const data = {
        labels: ['Presentation', 'Business', 'Data Access'],
        datasets: [{
            label: 'Coverage %',
            data: [
                coverageData.presentation || 0,
                coverageData.business || 0,
                coverageData.data || 0
            ],
            backgroundColor: 'rgba(0, 212, 255, 0.2)',
            borderColor: 'rgba(0, 212, 255, 1)',
            borderWidth: 2,
            fill: true
        }]
    };
    
    return new Chart(ctx, {
        type: 'radar',
        data: data,
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        color: getTextColor(),
                        stepSize: 20
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    pointLabels: {
                        color: getTextColor(),
                        font: {
                            size: 12
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// ========== Utility Functions ==========
function getChartColors() {
    return [
        'rgba(0, 212, 255, 0.8)',
        'rgba(123, 44, 191, 0.8)',
        'rgba(6, 255, 165, 0.8)',
        'rgba(255, 182, 39, 0.8)',
        'rgba(255, 107, 157, 0.8)'
    ];
}

function getTextColor() {
    const theme = document.documentElement.getAttribute('data-theme');
    return theme === 'dark' ? '#b8c5d6' : '#495057';
}

function updateChartColors() {
    // Update all chart text colors when theme changes
    Object.values(charts).forEach(chart => {
        if (chart.options.plugins?.legend?.labels) {
            chart.options.plugins.legend.labels.color = getTextColor();
        }
        if (chart.options.scales?.y?.ticks) {
            chart.options.scales.y.ticks.color = getTextColor();
        }
        if (chart.options.scales?.x?.ticks) {
            chart.options.scales.x.ticks.color = getTextColor();
        }
        if (chart.options.scales?.r?.ticks) {
            chart.options.scales.r.ticks.color = getTextColor();
        }
        if (chart.options.scales?.r?.pointLabels) {
            chart.options.scales.r.pointLabels.color = getTextColor();
        }
        chart.update();
    });
}

// ========== Number Formatting ==========
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

// ========== Export Functions ==========
function exportToPDF() {
    console.log('📄 Exporting to PDF...');
    window.print();
}

function exportToJSON() {
    console.log('💾 Exporting to JSON...');
    const dataStr = JSON.stringify(analysisData, null, 2);
    downloadFile(dataStr, 'cortex-lens-analysis.json', 'application/json');
}

function downloadFile(content, filename, contentType) {
    const blob = new Blob([content], { type: contentType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// ========== Print Styles ==========
window.addEventListener('beforeprint', () => {
    // Show all tabs for printing
    document.querySelectorAll('.tab-content').forEach(content => {
        content.style.display = 'block';
    });
});

window.addEventListener('afterprint', () => {
    // Restore tab visibility
    document.querySelectorAll('.tab-content').forEach(content => {
        if (!content.classList.contains('active')) {
            content.style.display = 'none';
        }
    });
});

// ========== Global Exports ==========
window.toggleTheme = toggleTheme;
window.exportToPDF = exportToPDF;
window.exportToJSON = exportToJSON;
