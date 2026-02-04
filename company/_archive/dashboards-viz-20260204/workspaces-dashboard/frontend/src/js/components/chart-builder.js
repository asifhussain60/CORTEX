/**
 * Chart Builder Component
 * 
 * Wrapper for Chart.js with common configurations and utilities
 */

class ChartBuilder {
    constructor() {
        this.charts = new Map();
        this.defaultOptions = {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    labels: {
                        color: '#e5e7eb'
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#9ca3af'
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#9ca3af'
                    }
                }
            }
        };
    }

    createChart(canvasId, type, data, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) {
            console.warn(`Canvas element '${canvasId}' not found`);
            return null;
        }

        // Merge options with defaults
        const mergedOptions = this.mergeOptions(this.defaultOptions, options);

        // Create chart
        const chart = new Chart(ctx, {
            type: type,
            data: data,
            options: mergedOptions
        });

        // Store reference
        this.charts.set(canvasId, chart);

        return chart;
    }

    updateChart(canvasId, newData) {
        const chart = this.charts.get(canvasId);
        if (!chart) {
            console.warn(`Chart '${canvasId}' not found`);
            return;
        }

        chart.data = newData;
        chart.update();
    }

    destroyChart(canvasId) {
        const chart = this.charts.get(canvasId);
        if (chart) {
            chart.destroy();
            this.charts.delete(canvasId);
        }
    }

    destroyAll() {
        this.charts.forEach(chart => chart.destroy());
        this.charts.clear();
    }

    mergeOptions(defaults, custom) {
        return {
            ...defaults,
            ...custom,
            plugins: {
                ...defaults.plugins,
                ...(custom.plugins || {})
            },
            scales: {
                ...defaults.scales,
                ...(custom.scales || {})
            }
        };
    }

    // Preset configurations
    createRadarChart(canvasId, labels, datasets, options = {}) {
        return this.createChart(canvasId, 'radar', {
            labels: labels,
            datasets: datasets.map(ds => ({
                ...ds,
                borderColor: ds.borderColor || 'rgba(99, 102, 241, 1)',
                backgroundColor: ds.backgroundColor || 'rgba(99, 102, 241, 0.2)'
            }))
        }, {
            ...options,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        color: '#9ca3af'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        });
    }

    createDoughnutChart(canvasId, labels, data, options = {}) {
        return this.createChart(canvasId, 'doughnut', {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    'rgba(99, 102, 241, 0.8)',
                    'rgba(139, 92, 246, 0.8)',
                    'rgba(168, 85, 247, 0.8)',
                    'rgba(192, 132, 252, 0.8)'
                ]
            }]
        }, options);
    }

    createBarChart(canvasId, labels, datasets, options = {}) {
        return this.createChart(canvasId, 'bar', {
            labels: labels,
            datasets: datasets.map(ds => ({
                ...ds,
                backgroundColor: ds.backgroundColor || 'rgba(99, 102, 241, 0.8)'
            }))
        }, options);
    }

    createLineChart(canvasId, labels, datasets, options = {}) {
        return this.createChart(canvasId, 'line', {
            labels: labels,
            datasets: datasets.map(ds => ({
                ...ds,
                borderColor: ds.borderColor || 'rgba(99, 102, 241, 1)',
                backgroundColor: ds.backgroundColor || 'rgba(99, 102, 241, 0.1)',
                fill: ds.fill !== undefined ? ds.fill : true
            }))
        }, options);
    }
}

// Create global instance
window.chartBuilder = new ChartBuilder();

// Export
window.ChartBuilder = ChartBuilder;
