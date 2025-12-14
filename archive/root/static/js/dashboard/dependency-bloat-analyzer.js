/**
 * Dependency Bloat Analyzer - Frontend Visualization
 * 
 * Displays histogram and box plot of package count distribution
 * with bloat scoring and outlier detection.
 * 
 * Author: Asif Hussain
 * Date: December 6, 2025
 */

class DependencyBloatAnalyzer {
    constructor(containerId, techStackData) {
        this.container = d3.select(`#${containerId}`);
        this.techStackData = techStackData;
        this.analysis = null;
        
        // Dimensions
        this.margin = { top: 40, right: 40, bottom: 80, left: 80 };
        this.histogramHeight = 400;
        this.boxPlotHeight = 300;
        this.width = 1000;
        
        // Bloat score thresholds
        this.BLOAT_CRITICAL = 2.0;
        this.BLOAT_WARNING = 1.0;
        
        this.init();
    }
    
    init() {
        // Create container structure
        this.container.html('');
        
        // Header
        const header = this.container.append('div')
            .attr('class', 'bloat-header');
        
        header.append('h2')
            .text('Dependency Bloat Analysis');
        
        // Statistics summary
        this.statsContainer = this.container.append('div')
            .attr('class', 'bloat-stats-summary');
        
        // Histogram section
        const histogramSection = this.container.append('div')
            .attr('class', 'bloat-histogram-section');
        
        histogramSection.append('h3')
            .text('Package Count Distribution');
        
        this.histogramSvg = histogramSection.append('svg')
            .attr('class', 'bloat-histogram')
            .attr('width', this.width)
            .attr('height', this.histogramHeight);
        
        // Box plot section
        const boxPlotSection = this.container.append('div')
            .attr('class', 'bloat-boxplot-section');
        
        boxPlotSection.append('h3')
            .text('Statistical Distribution');
        
        this.boxPlotSvg = boxPlotSection.append('svg')
            .attr('class', 'bloat-boxplot')
            .attr('width', this.width)
            .attr('height', this.boxPlotHeight);
        
        // Solutions table
        this.solutionsContainer = this.container.append('div')
            .attr('class', 'bloat-solutions-table');
        
        // Recommendations
        this.recommendationsContainer = this.container.append('div')
            .attr('class', 'bloat-recommendations');
        
        // Analyze data
        this.analyzeData();
        
        // Render visualizations
        this.renderStatsSummary();
        this.renderHistogram();
        this.renderBoxPlot();
        this.renderSolutionsTable();
        this.renderRecommendations();
    }
    
    analyzeData() {
        // Extract package counts
        const solutions = this.techStackData.solutions || [];
        const countsWithNames = solutions.map(s => ({
            name: s.name,
            count: (s.packages || []).length
        }));
        
        const counts = countsWithNames.map(c => c.count);
        
        if (counts.length === 0) {
            this.analysis = {
                solutions: [],
                stats: { mean: 0, median: 0, q1: 0, q3: 0, iqr: 0, outlierThreshold: 0 },
                histogramBins: [],
                boxPlotData: {},
                recommendations: ['No data available for analysis.']
            };
            return;
        }
        
        // Calculate statistics
        const stats = this.calculateStatistics(counts);
        
        // Calculate standard deviation
        const stdDev = counts.length > 1 ? this.standardDeviation(counts, stats.mean) : 0;
        
        // Detect outliers
        const outlierFlags = counts.map(c => c > stats.outlierThreshold);
        
        // Create solution stats
        const solutionStats = countsWithNames.map((item, idx) => {
            const bloatScore = this.calculateBloatScore(item.count, stats.mean, stdDev);
            const category = this.categorizeBloat(bloatScore);
            
            return {
                name: item.name,
                packageCount: item.count,
                bloatScore: bloatScore,
                isOutlier: outlierFlags[idx],
                category: category
            };
        });
        
        // Sort by bloat score (highest first)
        solutionStats.sort((a, b) => b.bloatScore - a.bloatScore);
        
        // Create histogram bins
        const histogramBins = this.createHistogramBins(countsWithNames);
        
        // Create box plot data
        const outlierSolutions = solutionStats.filter(s => s.isOutlier).map(s => s.name);
        const boxPlotData = {
            median: stats.median,
            q1: stats.q1,
            q3: stats.q3,
            whiskerLow: Math.max(0, stats.q1 - (1.5 * stats.iqr)),
            whiskerHigh: stats.outlierThreshold,
            outliers: outlierSolutions,
            outlierValues: solutionStats.filter(s => s.isOutlier).map(s => s.packageCount)
        };
        
        // Generate recommendations
        const recommendations = this.generateRecommendations(solutionStats, stats);
        
        this.analysis = {
            solutions: solutionStats,
            stats: stats,
            histogramBins: histogramBins,
            boxPlotData: boxPlotData,
            recommendations: recommendations
        };
    }
    
    calculateStatistics(counts) {
        const sorted = [...counts].sort((a, b) => a - b);
        const n = sorted.length;
        
        const mean = sorted.reduce((sum, val) => sum + val, 0) / n;
        const median = n % 2 === 0 
            ? (sorted[n/2 - 1] + sorted[n/2]) / 2 
            : sorted[Math.floor(n/2)];
        
        const q1 = this.percentile(sorted, 25);
        const q3 = this.percentile(sorted, 75);
        const iqr = q3 - q1;
        const outlierThreshold = q3 + (1.5 * iqr);
        
        return { mean, median, q1, q3, iqr, outlierThreshold };
    }
    
    percentile(sorted, p) {
        const index = (p / 100) * (sorted.length - 1);
        const lower = Math.floor(index);
        const upper = Math.ceil(index);
        const weight = index - lower;
        
        if (lower === upper) {
            return sorted[lower];
        }
        
        return sorted[lower] * (1 - weight) + sorted[upper] * weight;
    }
    
    standardDeviation(values, mean) {
        const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length;
        return Math.sqrt(variance);
    }
    
    calculateBloatScore(packageCount, mean, stdDev) {
        if (stdDev === 0) return 0;
        return (packageCount - mean) / stdDev;
    }
    
    categorizeBloat(bloatScore) {
        if (bloatScore >= this.BLOAT_CRITICAL) return 'critical';
        if (bloatScore >= this.BLOAT_WARNING) return 'warning';
        return 'normal';
    }
    
    createHistogramBins(countsWithNames) {
        const bins = [
            { range: [0, 50], label: '0-50', solutions: [] },
            { range: [51, 100], label: '51-100', solutions: [] },
            { range: [101, 150], label: '101-150', solutions: [] },
            { range: [151, 200], label: '151-200', solutions: [] },
            { range: [201, 1000], label: '200+', solutions: [] }
        ];
        
        countsWithNames.forEach(item => {
            for (const bin of bins) {
                if (item.count >= bin.range[0] && item.count <= bin.range[1]) {
                    bin.solutions.push(item.name);
                    break;
                }
            }
        });
        
        return bins.map(bin => ({
            ...bin,
            count: bin.solutions.length
        }));
    }
    
    generateRecommendations(solutions, stats) {
        const recommendations = [];
        
        const criticalCount = solutions.filter(s => s.category === 'critical').length;
        const warningCount = solutions.filter(s => s.category === 'warning').length;
        const outlierCount = solutions.filter(s => s.isOutlier).length;
        
        if (criticalCount > 0) {
            recommendations.push(
                `⚠️ ${criticalCount} solution(s) have critical dependency bloat (>2σ above mean). Immediate review recommended.`
            );
        }
        
        if (warningCount > 0) {
            recommendations.push(
                `📊 ${warningCount} solution(s) have elevated package counts (1-2σ above mean). Consider consolidation opportunities.`
            );
        }
        
        if (outlierCount > 0) {
            recommendations.push(
                `🔍 ${outlierCount} outlier(s) detected using IQR method. These solutions may benefit from dependency audits.`
            );
        }
        
        if (stats.mean > 100) {
            recommendations.push(
                '💡 High overall package usage detected (mean >100). Consider establishing package governance policies.'
            );
        }
        
        if (stats.iqr > 50) {
            recommendations.push(
                '📈 Wide variation in package usage (IQR >50). Standardize dependency management across solutions.'
            );
        }
        
        if (criticalCount > 0 || outlierCount > 0) {
            recommendations.push(
                '⏱️ High package counts impact build times and maintenance. Review for unused dependencies and consolidation opportunities.'
            );
        }
        
        if (recommendations.length === 0) {
            recommendations.push(
                '✅ Dependency usage is well-distributed. No significant bloat detected.'
            );
        }
        
        return recommendations;
    }
    
    renderStatsSummary() {
        const stats = this.analysis.stats;
        
        const cards = [
            { label: 'Mean', value: stats.mean.toFixed(1), unit: 'packages' },
            { label: 'Median', value: stats.median.toFixed(1), unit: 'packages' },
            { label: 'IQR', value: stats.iqr.toFixed(1), unit: 'range' },
            { label: 'Outlier Threshold', value: stats.outlierThreshold.toFixed(1), unit: 'packages' }
        ];
        
        const cardsContainer = this.statsContainer.selectAll('.stat-card')
            .data(cards)
            .enter()
            .append('div')
            .attr('class', 'stat-card');
        
        cardsContainer.append('div')
            .attr('class', 'stat-label')
            .text(d => d.label);
        
        cardsContainer.append('div')
            .attr('class', 'stat-value')
            .text(d => d.value);
        
        cardsContainer.append('div')
            .attr('class', 'stat-unit')
            .text(d => d.unit);
    }
    
    renderHistogram() {
        const data = this.analysis.histogramBins;
        const innerWidth = this.width - this.margin.left - this.margin.right;
        const innerHeight = this.histogramHeight - this.margin.top - this.margin.bottom;
        
        const g = this.histogramSvg.append('g')
            .attr('transform', `translate(${this.margin.left},${this.margin.top})`);
        
        // Scales
        const xScale = d3.scaleBand()
            .domain(data.map(d => d.label))
            .range([0, innerWidth])
            .padding(0.2);
        
        const yScale = d3.scaleLinear()
            .domain([0, d3.max(data, d => d.count) || 1])
            .range([innerHeight, 0])
            .nice();
        
        // Axes
        g.append('g')
            .attr('class', 'x-axis')
            .attr('transform', `translate(0,${innerHeight})`)
            .call(d3.axisBottom(xScale))
            .append('text')
            .attr('x', innerWidth / 2)
            .attr('y', 40)
            .attr('fill', 'currentColor')
            .attr('text-anchor', 'middle')
            .text('Package Count Range');
        
        g.append('g')
            .attr('class', 'y-axis')
            .call(d3.axisLeft(yScale).ticks(5))
            .append('text')
            .attr('transform', 'rotate(-90)')
            .attr('x', -innerHeight / 2)
            .attr('y', -50)
            .attr('fill', 'currentColor')
            .attr('text-anchor', 'middle')
            .text('Number of Solutions');
        
        // Bars
        const bars = g.selectAll('.bar')
            .data(data)
            .enter()
            .append('rect')
            .attr('class', 'bar')
            .attr('x', d => xScale(d.label))
            .attr('y', d => yScale(d.count))
            .attr('width', xScale.bandwidth())
            .attr('height', d => innerHeight - yScale(d.count))
            .attr('fill', '#4A90E2')
            .attr('opacity', 0.8);
        
        // Tooltips
        bars.on('mouseover', (event, d) => {
            const tooltip = d3.select('body').append('div')
                .attr('class', 'bloat-tooltip')
                .style('position', 'absolute')
                .style('left', `${event.pageX + 10}px`)
                .style('top', `${event.pageY - 10}px`);
            
            tooltip.append('div')
                .attr('class', 'tooltip-header')
                .text(`${d.label} packages`);
            
            tooltip.append('div')
                .text(`Solutions: ${d.count}`);
            
            if (d.solutions.length > 0) {
                tooltip.append('div')
                    .attr('class', 'tooltip-solutions')
                    .text(d.solutions.slice(0, 5).join(', ') + 
                          (d.solutions.length > 5 ? '...' : ''));
            }
        })
        .on('mouseout', () => {
            d3.selectAll('.bloat-tooltip').remove();
        });
        
        // Bar labels
        g.selectAll('.bar-label')
            .data(data)
            .enter()
            .append('text')
            .attr('class', 'bar-label')
            .attr('x', d => xScale(d.label) + xScale.bandwidth() / 2)
            .attr('y', d => yScale(d.count) - 5)
            .attr('text-anchor', 'middle')
            .attr('font-size', '12px')
            .text(d => d.count);
    }
    
    renderBoxPlot() {
        const data = this.analysis.boxPlotData;
        const innerWidth = this.width - this.margin.left - this.margin.right;
        const innerHeight = this.boxPlotHeight - this.margin.top - this.margin.bottom;
        
        const g = this.boxPlotSvg.append('g')
            .attr('transform', `translate(${this.margin.left},${this.margin.top})`);
        
        // Scale
        const maxVal = Math.max(
            data.whiskerHigh,
            ...(data.outlierValues || [])
        );
        
        const yScale = d3.scaleLinear()
            .domain([0, maxVal * 1.1])
            .range([innerHeight, 0])
            .nice();
        
        const boxWidth = 80;
        const centerX = innerWidth / 2;
        
        // Axis
        g.append('g')
            .attr('class', 'y-axis')
            .call(d3.axisLeft(yScale).ticks(10))
            .append('text')
            .attr('transform', 'rotate(-90)')
            .attr('x', -innerHeight / 2)
            .attr('y', -50)
            .attr('fill', 'currentColor')
            .attr('text-anchor', 'middle')
            .text('Package Count');
        
        // Whiskers
        g.append('line')
            .attr('x1', centerX)
            .attr('x2', centerX)
            .attr('y1', yScale(data.whiskerLow))
            .attr('y2', yScale(data.q1))
            .attr('stroke', '#333')
            .attr('stroke-width', 1.5);
        
        g.append('line')
            .attr('x1', centerX)
            .attr('x2', centerX)
            .attr('y1', yScale(data.q3))
            .attr('y2', yScale(data.whiskerHigh))
            .attr('stroke', '#333')
            .attr('stroke-width', 1.5);
        
        // Whisker caps
        [data.whiskerLow, data.whiskerHigh].forEach(val => {
            g.append('line')
                .attr('x1', centerX - 20)
                .attr('x2', centerX + 20)
                .attr('y1', yScale(val))
                .attr('y2', yScale(val))
                .attr('stroke', '#333')
                .attr('stroke-width', 1.5);
        });
        
        // Box (Q1 to Q3)
        g.append('rect')
            .attr('x', centerX - boxWidth / 2)
            .attr('y', yScale(data.q3))
            .attr('width', boxWidth)
            .attr('height', yScale(data.q1) - yScale(data.q3))
            .attr('fill', '#4A90E2')
            .attr('opacity', 0.6)
            .attr('stroke', '#333')
            .attr('stroke-width', 2);
        
        // Median line
        g.append('line')
            .attr('x1', centerX - boxWidth / 2)
            .attr('x2', centerX + boxWidth / 2)
            .attr('y1', yScale(data.median))
            .attr('y2', yScale(data.median))
            .attr('stroke', '#E74C3C')
            .attr('stroke-width', 3);
        
        // Outliers
        if (data.outlierValues && data.outlierValues.length > 0) {
            g.selectAll('.outlier')
                .data(data.outlierValues)
                .enter()
                .append('circle')
                .attr('class', 'outlier')
                .attr('cx', centerX)
                .attr('cy', d => yScale(d))
                .attr('r', 5)
                .attr('fill', '#E74C3C')
                .attr('stroke', '#C0392B')
                .attr('stroke-width', 2);
        }
        
        // Labels
        const labels = [
            { text: `Q3: ${data.q3.toFixed(1)}`, y: data.q3 },
            { text: `Median: ${data.median.toFixed(1)}`, y: data.median },
            { text: `Q1: ${data.q1.toFixed(1)}`, y: data.q1 }
        ];
        
        labels.forEach(label => {
            g.append('text')
                .attr('x', centerX + boxWidth / 2 + 10)
                .attr('y', yScale(label.y) + 5)
                .attr('font-size', '12px')
                .text(label.text);
        });
    }
    
    renderSolutionsTable() {
        this.solutionsContainer.append('h3')
            .text('Solutions by Bloat Score');
        
        const table = this.solutionsContainer.append('table')
            .attr('class', 'bloat-table');
        
        // Header
        const thead = table.append('thead');
        thead.append('tr')
            .selectAll('th')
            .data(['Solution', 'Packages', 'Bloat Score', 'Category', 'Outlier'])
            .enter()
            .append('th')
            .text(d => d);
        
        // Body (top 10 solutions)
        const tbody = table.append('tbody');
        const rows = tbody.selectAll('tr')
            .data(this.analysis.solutions.slice(0, 10))
            .enter()
            .append('tr')
            .attr('class', d => `category-${d.category}`);
        
        rows.append('td').text(d => d.name);
        rows.append('td').text(d => d.packageCount);
        rows.append('td').text(d => d.bloatScore.toFixed(2));
        rows.append('td')
            .append('span')
            .attr('class', d => `badge badge-${d.category}`)
            .text(d => d.category.toUpperCase());
        rows.append('td').text(d => d.isOutlier ? '🔴' : '—');
    }
    
    renderRecommendations() {
        this.recommendationsContainer.append('h3')
            .text('Recommendations');
        
        const list = this.recommendationsContainer.append('ul')
            .attr('class', 'recommendations-list');
        
        list.selectAll('li')
            .data(this.analysis.recommendations)
            .enter()
            .append('li')
            .html(d => d);
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DependencyBloatAnalyzer;
}
