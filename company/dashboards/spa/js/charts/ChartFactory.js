/**
 * CORTEX SPA - Chart Factory
 * Creates ECharts instances with consistent theming
 * Version: 1.0.0
 */

const ChartFactory = {
    // CORTEX theme colors
    colors: {
        primary: '#4d8cff',
        secondary: '#7fb3ff',
        tertiary: '#a3c9ff',
        success: '#22c55e',
        warning: '#f59e0b',
        danger: '#ef4444',
        info: '#6366f1',
        text: 'rgba(255, 255, 255, 0.87)',
        textSecondary: 'rgba(255, 255, 255, 0.6)',
        border: 'rgba(255, 255, 255, 0.1)',
        background: 'rgba(10, 20, 40, 0.5)'
    },
    
    // Base chart options
    baseOptions: {
        backgroundColor: 'transparent',
        textStyle: {
            fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
            color: 'rgba(255, 255, 255, 0.87)'
        },
        grid: {
            top: 60,
            right: 20,
            bottom: 40,
            left: 60,
            containLabel: true
        },
        tooltip: {
            trigger: 'axis',
            backgroundColor: 'rgba(10, 20, 40, 0.95)',
            borderColor: 'rgba(77, 140, 255, 0.3)',
            textStyle: { color: 'rgba(255, 255, 255, 0.87)' }
        }
    },
    
    /**
     * Create a pie/donut chart
     */
    createPieChart(container, data, options = {}) {
        const chart = echarts.init(container);
        
        const chartOptions = {
            ...this.baseOptions,
            tooltip: {
                trigger: 'item',
                backgroundColor: 'rgba(10, 20, 40, 0.95)',
                borderColor: 'rgba(77, 140, 255, 0.3)',
                textStyle: { color: 'rgba(255, 255, 255, 0.87)' }
            },
            legend: {
                orient: 'vertical',
                right: 10,
                top: 'center',
                textStyle: { color: this.colors.textSecondary }
            },
            series: [{
                type: 'pie',
                radius: options.donut ? ['50%', '70%'] : '70%',
                center: ['40%', '50%'],
                avoidLabelOverlap: true,
                itemStyle: {
                    borderRadius: 4,
                    borderColor: 'rgba(10, 20, 40, 0.8)',
                    borderWidth: 2
                },
                label: {
                    show: false
                },
                emphasis: {
                    label: {
                        show: true,
                        fontSize: 14,
                        fontWeight: 'bold'
                    },
                    itemStyle: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                },
                data: data.map((item, i) => ({
                    ...item,
                    itemStyle: { color: this.getColor(i) }
                }))
            }]
        };
        
        chart.setOption(chartOptions);
        return chart;
    },
    
    /**
     * Create a bar chart
     */
    createBarChart(container, categories, series, options = {}) {
        const chart = echarts.init(container);
        
        const chartOptions = {
            ...this.baseOptions,
            xAxis: {
                type: 'category',
                data: categories,
                axisLine: { lineStyle: { color: this.colors.border } },
                axisLabel: { color: this.colors.textSecondary },
                axisTick: { show: false }
            },
            yAxis: {
                type: 'value',
                axisLine: { show: false },
                axisLabel: { color: this.colors.textSecondary },
                splitLine: { lineStyle: { color: this.colors.border } }
            },
            series: series.map((s, i) => ({
                ...s,
                type: 'bar',
                itemStyle: {
                    color: this.getGradient(i),
                    borderRadius: [4, 4, 0, 0]
                },
                emphasis: {
                    itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.3)' }
                }
            }))
        };
        
        chart.setOption(chartOptions);
        return chart;
    },
    
    /**
     * Create a line chart
     */
    createLineChart(container, categories, series, options = {}) {
        const chart = echarts.init(container);
        
        const chartOptions = {
            ...this.baseOptions,
            xAxis: {
                type: 'category',
                data: categories,
                boundaryGap: false,
                axisLine: { lineStyle: { color: this.colors.border } },
                axisLabel: { color: this.colors.textSecondary },
                axisTick: { show: false }
            },
            yAxis: {
                type: 'value',
                axisLine: { show: false },
                axisLabel: { color: this.colors.textSecondary },
                splitLine: { lineStyle: { color: this.colors.border } }
            },
            series: series.map((s, i) => ({
                ...s,
                type: 'line',
                smooth: true,
                symbol: 'circle',
                symbolSize: 6,
                lineStyle: { width: 2, color: this.getColor(i) },
                itemStyle: { color: this.getColor(i) },
                areaStyle: options.area ? {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: this.getColor(i, 0.4) },
                        { offset: 1, color: this.getColor(i, 0.05) }
                    ])
                } : undefined
            }))
        };
        
        chart.setOption(chartOptions);
        return chart;
    },
    
    /**
     * Create a gauge chart
     */
    createGaugeChart(container, value, options = {}) {
        const chart = echarts.init(container);
        
        const color = value >= 80 ? this.colors.success : 
                      value >= 60 ? this.colors.warning : this.colors.danger;
        
        const chartOptions = {
            ...this.baseOptions,
            series: [{
                type: 'gauge',
                startAngle: 200,
                endAngle: -20,
                min: 0,
                max: 100,
                splitNumber: 10,
                radius: '90%',
                center: ['50%', '60%'],
                axisLine: {
                    lineStyle: {
                        width: 12,
                        color: [
                            [0.3, this.colors.danger],
                            [0.6, this.colors.warning],
                            [1, this.colors.success]
                        ]
                    }
                },
                pointer: {
                    itemStyle: { color: color },
                    width: 4
                },
                axisTick: { show: false },
                splitLine: { show: false },
                axisLabel: { show: false },
                detail: {
                    valueAnimation: true,
                    formatter: '{value}%',
                    color: this.colors.text,
                    fontSize: 24,
                    fontWeight: 'bold',
                    offsetCenter: [0, '30%']
                },
                title: {
                    show: !!options.title,
                    offsetCenter: [0, '60%'],
                    color: this.colors.textSecondary,
                    fontSize: 12
                },
                data: [{ value, name: options.title || '' }]
            }]
        };
        
        chart.setOption(chartOptions);
        return chart;
    },
    
    /**
     * Create a treemap chart
     */
    createTreemapChart(container, data, options = {}) {
        const chart = echarts.init(container);
        
        const chartOptions = {
            ...this.baseOptions,
            tooltip: {
                trigger: 'item',
                backgroundColor: 'rgba(10, 20, 40, 0.95)',
                borderColor: 'rgba(77, 140, 255, 0.3)',
                textStyle: { color: 'rgba(255, 255, 255, 0.87)' }
            },
            series: [{
                type: 'treemap',
                roam: false,
                nodeClick: false,
                breadcrumb: { show: false },
                label: {
                    show: true,
                    formatter: '{b}',
                    color: this.colors.text,
                    fontSize: 11
                },
                itemStyle: {
                    borderColor: 'rgba(10, 20, 40, 0.8)',
                    borderWidth: 2,
                    gapWidth: 2
                },
                levels: [
                    {
                        itemStyle: {
                            borderWidth: 0,
                            gapWidth: 4
                        }
                    },
                    {
                        colorSaturation: [0.35, 0.5],
                        itemStyle: {
                            borderColorSaturation: 0.6,
                            gapWidth: 2
                        }
                    }
                ],
                data: data
            }]
        };
        
        chart.setOption(chartOptions);
        return chart;
    },
    
    /**
     * Create a radar chart
     */
    createRadarChart(container, indicators, data, options = {}) {
        const chart = echarts.init(container);
        
        const chartOptions = {
            ...this.baseOptions,
            radar: {
                indicator: indicators,
                axisName: { color: this.colors.textSecondary },
                splitArea: { areaStyle: { color: ['rgba(77, 140, 255, 0.05)', 'transparent'] } },
                splitLine: { lineStyle: { color: this.colors.border } },
                axisLine: { lineStyle: { color: this.colors.border } }
            },
            series: [{
                type: 'radar',
                data: data.map((d, i) => ({
                    ...d,
                    lineStyle: { color: this.getColor(i), width: 2 },
                    areaStyle: { color: this.getColor(i, 0.2) },
                    itemStyle: { color: this.getColor(i) }
                }))
            }]
        };
        
        chart.setOption(chartOptions);
        return chart;
    },
    
    // Helper methods
    getColor(index, alpha = 1) {
        const palette = [
            this.colors.primary,
            this.colors.success,
            this.colors.warning,
            this.colors.danger,
            this.colors.info,
            this.colors.secondary,
            this.colors.tertiary
        ];
        const color = palette[index % palette.length];
        
        if (alpha < 1) {
            // Convert hex to rgba
            const r = parseInt(color.slice(1, 3), 16);
            const g = parseInt(color.slice(3, 5), 16);
            const b = parseInt(color.slice(5, 7), 16);
            return `rgba(${r}, ${g}, ${b}, ${alpha})`;
        }
        return color;
    },
    
    getGradient(index) {
        const color = this.getColor(index);
        return new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: color },
            { offset: 1, color: this.getColor(index, 0.6) }
        ]);
    },
    
    getSeverityColor(severity) {
        const map = {
            critical: this.colors.danger,
            high: '#ef4444',
            medium: this.colors.warning,
            low: this.colors.success,
            info: this.colors.info
        };
        return map[severity?.toLowerCase()] || this.colors.primary;
    }
};

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChartFactory;
}
