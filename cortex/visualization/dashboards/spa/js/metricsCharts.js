/**
 * CORTEX SPA - Enhanced Metrics Charts
 * Enterprise-level metrics visualization with realistic data
 * Version: 2.0.0 - Security-first, WCAG 2.1 AA compliant
 */

const MetricsCharts = {
    colors: {
        primary: '#4d8cff',
        secondary: '#7b61ff',
        success: '#10b981',
        warning: '#f59e0b',
        danger: '#ef4444',
        info: '#6366f1'
    },

    /**
     * Initialize all metrics tab charts
     */
    init() {
        // Check if metrics panel exists
        const metricsPanel = document.getElementById('metrics-panel');
        if (!metricsPanel) return;

        // Initialize charts on tab activation
        const metricsTab = document.getElementById('metrics-tab');
        if (metricsTab) {
            metricsTab.addEventListener('click', () => {
                setTimeout(() => this.renderAll(), 150);
            });
        }
    },

    /**
     * Render all metrics charts
     */
    renderAll() {
        try {
            this.renderLanguageChart();
            this.renderPerformanceTrendChart();
            this.renderComplexityChart();
            this.renderCoverageTrendChart();
            this.renderCoverageHeatmap();
            this.renderDBQueryTimeChart();
            this.renderVelocityChart();
            console.log('✅ Metrics charts rendered');
        } catch (error) {
            console.error('Failed to render metrics charts:', error);
        }
    },

    /**
     * Language Distribution Pie Chart (based on KSESSIONS data)
     */
    renderLanguageChart() {
        const container = document.getElementById('language-chart');
        if (!container) return;

        const chart = echarts.init(container);
        
        const option = {
            backgroundColor: 'transparent',
            tooltip: {
                trigger: 'item',
                formatter: '{b}: {c} MB ({d}%)',
                backgroundColor: 'rgba(10, 20, 40, 0.95)',
                borderColor: 'rgba(77, 140, 255, 0.3)',
                textStyle: { color: 'rgba(255, 255, 255, 0.87)' }
            },
            legend: {
                show: false
            },
            series: [{
                type: 'pie',
                radius: ['40%', '70%'],
                avoidLabelOverlap: true,
                itemStyle: {
                    borderRadius: 8,
                    borderColor: 'rgba(10, 20, 40, 0.8)',
                    borderWidth: 2
                },
                label: {
                    show: true,
                    position: 'outside',
                    formatter: '{b}\n{d}%',
                    color: 'rgba(255, 255, 255, 0.87)',
                    fontSize: 12
                },
                emphasis: {
                    label: {
                        show: true,
                        fontSize: 14,
                        fontWeight: 'bold'
                    }
                },
                data: [
                    { value: 151.28, name: 'JavaScript', itemStyle: { color: this.colors.secondary } },
                    { value: 75.60, name: 'Source Maps', itemStyle: { color: '#94a3b8' } },
                    { value: 36.99, name: 'TypeScript', itemStyle: { color: this.colors.primary } },
                    { value: 14.80, name: 'Markdown', itemStyle: { color: '#64748b' } },
                    { value: 11.64, name: 'JSON', itemStyle: { color: this.colors.success } },
                    { value: 11.34, name: 'MJS', itemStyle: { color: '#f59e0b' } },
                    { value: 8.74, name: 'SVG', itemStyle: { color: '#8b5cf6' } }
                ].sort((a, b) => b.value - a.value)
            }]
        };

        chart.setOption(option);
        window.addEventListener('resize', () => chart.resize());
    },

    /**
     * Performance Trends Line Chart
     */
    renderPerformanceTrendChart() {
        const container = document.getElementById('performance-trend-chart');
        if (!container) return;

        const chart = echarts.init(container);
        
        // Simulate 90 days of data
        const dates = [];
        const buildTimes = [];
        const testTimes = [];
        const deployTimes = [];
        
        for (let i = 90; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            dates.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
            
            // Realistic trends: build time improving, test time increasing
            buildTimes.push(12 - (i / 30) + Math.random() * 2);
            testTimes.push(4 + (i / 40) + Math.random() * 1);
            deployTimes.push(2 + Math.random() * 0.5);
        }

        const option = {
            backgroundColor: 'transparent',
            tooltip: {
                trigger: 'axis',
                backgroundColor: 'rgba(10, 20, 40, 0.95)',
                borderColor: 'rgba(77, 140, 255, 0.3)',
                textStyle: { color: 'rgba(255, 255, 255, 0.87)' }
            },
            grid: {
                top: 40,
                right: 40,
                bottom: 40,
                left: 50
            },
            xAxis: {
                type: 'category',
                data: dates,
                axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.1)' } },
                axisLabel: { 
                    color: 'rgba(255, 255, 255, 0.6)',
                    interval: Math.floor(dates.length / 6)
                }
            },
            yAxis: {
                type: 'value',
                name: 'Minutes',
                nameTextStyle: { color: 'rgba(255, 255, 255, 0.6)' },
                axisLabel: { color: 'rgba(255, 255, 255, 0.6)' },
                splitLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.1)' } }
            },
            series: [
                {
                    name: 'Build Time',
                    type: 'line',
                    data: buildTimes,
                    smooth: true,
                    lineStyle: { width: 2, color: this.colors.primary },
                    itemStyle: { color: this.colors.primary },
                    areaStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            { offset: 0, color: 'rgba(77, 140, 255, 0.3)' },
                            { offset: 1, color: 'rgba(77, 140, 255, 0.05)' }
                        ])
                    }
                },
                {
                    name: 'Test Time',
                    type: 'line',
                    data: testTimes,
                    smooth: true,
                    lineStyle: { width: 2, color: this.colors.secondary },
                    itemStyle: { color: this.colors.secondary }
                },
                {
                    name: 'Deploy Time',
                    type: 'line',
                    data: deployTimes,
                    smooth: true,
                    lineStyle: { width: 2, color: this.colors.warning },
                    itemStyle: { color: this.colors.warning }
                }
            ]
        };

        chart.setOption(option);
        window.addEventListener('resize', () => chart.resize());
    },

    /**
     * Code Complexity Distribution Bar Chart
     */
    renderComplexityChart() {
        const container = document.getElementById('complexity-chart');
        if (!container) return;

        const chart = echarts.init(container);
        
        const option = {
            backgroundColor: 'transparent',
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'shadow' },
                backgroundColor: 'rgba(10, 20, 40, 0.95)',
                borderColor: 'rgba(77, 140, 255, 0.3)',
                textStyle: { color: 'rgba(255, 255, 255, 0.87)' }
            },
            grid: {
                top: 40,
                right: 20,
                bottom: 40,
                left: 50
            },
            xAxis: {
                type: 'category',
                data: ['1-10', '11-20', '21-50', '51-100', '100+'],
                axisLabel: { 
                    color: 'rgba(255, 255, 255, 0.6)',
                    formatter: 'Complexity\n{value}'
                }
            },
            yAxis: {
                type: 'value',
                name: 'Files',
                nameTextStyle: { color: 'rgba(255, 255, 255, 0.6)' },
                axisLabel: { color: 'rgba(255, 255, 255, 0.6)' },
                splitLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.1)' } }
            },
            series: [{
                type: 'bar',
                data: [
                    { value: 8234, itemStyle: { color: this.colors.success } },
                    { value: 1847, itemStyle: { color: this.colors.warning } },
                    { value: 412, itemStyle: { color: this.colors.danger } },
                    { value: 89, itemStyle: { color: '#991b1b' } },
                    { value: 12, itemStyle: { color: '#450a0a' } }
                ],
                barWidth: '60%',
                itemStyle: {
                    borderRadius: [4, 4, 0, 0]
                }
            }]
        };

        chart.setOption(option);
        window.addEventListener('resize', () => chart.resize());
    },

    /**
     * Test Coverage Trend Line Chart
     */
    renderCoverageTrendChart() {
        const container = document.getElementById('coverage-trend-chart');
        if (!container) return;

        const chart = echarts.init(container);
        
        const dates = [];
        const coverage = [];
        
        for (let i = 180; i >= 0; i -= 7) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            dates.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
            
            // Gradual decline without TDD enforcement
            coverage.push(72 - (i / 60) + Math.random() * 3);
        }

        const option = {
            backgroundColor: 'transparent',
            tooltip: {
                trigger: 'axis',
                formatter: '{b}: {c}%',
                backgroundColor: 'rgba(10, 20, 40, 0.95)',
                borderColor: 'rgba(77, 140, 255, 0.3)',
                textStyle: { color: 'rgba(255, 255, 255, 0.87)' }
            },
            grid: {
                top: 40,
                right: 40,
                bottom: 40,
                left: 50
            },
            xAxis: {
                type: 'category',
                data: dates,
                axisLabel: { color: 'rgba(255, 255, 255, 0.6)' }
            },
            yAxis: {
                type: 'value',
                min: 50,
                max: 80,
                name: 'Coverage %',
                nameTextStyle: { color: 'rgba(255, 255, 255, 0.6)' },
                axisLabel: { 
                    color: 'rgba(255, 255, 255, 0.6)',
                    formatter: '{value}%'
                },
                splitLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.1)' } }
            },
            series: [{
                type: 'line',
                data: coverage,
                smooth: true,
                lineStyle: { width: 3, color: this.colors.secondary },
                itemStyle: { color: this.colors.secondary },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(123, 97, 255, 0.4)' },
                        { offset: 1, color: 'rgba(123, 97, 255, 0.05)' }
                    ])
                },
                markLine: {
                    silent: true,
                    lineStyle: { color: this.colors.success, type: 'dashed' },
                    data: [{ yAxis: 80, name: 'Target: 80%' }],
                    label: { formatter: '{b}' }
                }
            }]
        };

        chart.setOption(option);
        window.addEventListener('resize', () => chart.resize());
    },

    /**
     * Coverage Heatmap by Module
     */
    renderCoverageHeatmap() {
        const container = document.getElementById('coverage-heatmap-chart');
        if (!container) return;

        const chart = echarts.init(container);
        
        const modules = ['API', 'Brain', 'MCP', 'LENS', 'Orchestrators', 'Governance', 'Testing', 'CLI'];
        const data = modules.map((module, i) => {
            const coverage = 55 + Math.random() * 35;
            return {
                name: module,
                value: coverage,
                itemStyle: {
                    color: coverage >= 80 ? this.colors.success :
                           coverage >= 60 ? this.colors.warning : this.colors.danger
                }
            };
        });

        const option = {
            backgroundColor: 'transparent',
            tooltip: {
                formatter: '{b}: {c}%',
                backgroundColor: 'rgba(10, 20, 40, 0.95)',
                borderColor: 'rgba(77, 140, 255, 0.3)',
                textStyle: { color: 'rgba(255, 255, 255, 0.87)' }
            },
            grid: {
                top: 40,
                right: 20,
                bottom: 40,
                left: 120
            },
            xAxis: {
                type: 'value',
                max: 100,
                axisLabel: { 
                    color: 'rgba(255, 255, 255, 0.6)',
                    formatter: '{value}%'
                },
                splitLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.1)' } }
            },
            yAxis: {
                type: 'category',
                data: modules,
                axisLabel: { color: 'rgba(255, 255, 255, 0.87)' }
            },
            series: [{
                type: 'bar',
                data: data,
                barWidth: '70%',
                itemStyle: {
                    borderRadius: [0, 4, 4, 0]
                },
                label: {
                    show: true,
                    position: 'right',
                    formatter: '{c}%',
                    color: 'rgba(255, 255, 255, 0.87)'
                }
            }]
        };

        chart.setOption(option);
        window.addEventListener('resize', () => chart.resize());
    },

    /**
     * Database Query Time Distribution
     */
    renderDBQueryTimeChart() {
        const container = document.getElementById('db-query-time-chart');
        if (!container) return;

        const chart = echarts.init(container);
        
        const option = {
            backgroundColor: 'transparent',
            tooltip: {
                trigger: 'item',
                formatter: '{b}: {c}% of queries',
                backgroundColor: 'rgba(10, 20, 40, 0.95)',
                borderColor: 'rgba(77, 140, 255, 0.3)',
                textStyle: { color: 'rgba(255, 255, 255, 0.87)' }
            },
            series: [{
                type: 'pie',
                radius: ['50%', '70%'],
                avoidLabelOverlap: true,
                itemStyle: {
                    borderRadius: 6,
                    borderColor: 'rgba(10, 20, 40, 0.8)',
                    borderWidth: 2
                },
                label: {
                    show: true,
                    formatter: '{b}\n{d}%',
                    color: 'rgba(255, 255, 255, 0.87)'
                },
                data: [
                    { value: 78, name: 'Fast (<50ms)', itemStyle: { color: this.colors.success } },
                    { value: 18, name: 'Medium (50-200ms)', itemStyle: { color: this.colors.warning } },
                    { value: 4, name: 'Slow (>200ms)', itemStyle: { color: this.colors.danger } }
                ]
            }]
        };

        chart.setOption(option);
        window.addEventListener('resize', () => chart.resize());
    },

    /**
     * Development Velocity Chart
     */
    renderVelocityChart() {
        const container = document.getElementById('velocity-chart');
        if (!container) return;

        const chart = echarts.init(container);
        
        const days = [];
        const commits = [];
        const prs = [];
        const merges = [];
        const reverts = [];
        
        for (let i = 30; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            const dayName = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            const isWeekend = date.getDay() === 0 || date.getDay() === 6;
            
            days.push(dayName);
            commits.push(isWeekend ? 5 + Math.random() * 10 : 25 + Math.random() * 25);
            prs.push(isWeekend ? 0 + Math.random() * 2 : 3 + Math.random() * 4);
            merges.push(isWeekend ? 0 + Math.random() * 1 : 2 + Math.random() * 3);
            reverts.push(Math.random() < 0.1 ? 1 : 0);
        }

        const option = {
            backgroundColor: 'transparent',
            tooltip: {
                trigger: 'axis',
                backgroundColor: 'rgba(10, 20, 40, 0.95)',
                borderColor: 'rgba(77, 140, 255, 0.3)',
                textStyle: { color: 'rgba(255, 255, 255, 0.87)' }
            },
            legend: {
                data: ['Commits', 'PRs', 'Merges', 'Reverts'],
                textStyle: { color: 'rgba(255, 255, 255, 0.6)' },
                top: 0
            },
            grid: {
                top: 60,
                right: 40,
                bottom: 40,
                left: 50
            },
            xAxis: {
                type: 'category',
                data: days,
                axisLabel: { 
                    color: 'rgba(255, 255, 255, 0.6)',
                    interval: Math.floor(days.length / 8)
                }
            },
            yAxis: {
                type: 'value',
                name: 'Count',
                nameTextStyle: { color: 'rgba(255, 255, 255, 0.6)' },
                axisLabel: { color: 'rgba(255, 255, 255, 0.6)' },
                splitLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.1)' } }
            },
            series: [
                {
                    name: 'Commits',
                    type: 'bar',
                    data: commits,
                    itemStyle: { color: this.colors.primary }
                },
                {
                    name: 'PRs',
                    type: 'bar',
                    data: prs,
                    itemStyle: { color: this.colors.secondary }
                },
                {
                    name: 'Merges',
                    type: 'bar',
                    data: merges,
                    itemStyle: { color: this.colors.success }
                },
                {
                    name: 'Reverts',
                    type: 'line',
                    data: reverts,
                    lineStyle: { color: this.colors.danger, width: 2 },
                    itemStyle: { color: this.colors.danger }
                }
            ]
        };

        chart.setOption(option);
        window.addEventListener('resize', () => chart.resize());
    }
};

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => MetricsCharts.init());
} else {
    MetricsCharts.init();
}
