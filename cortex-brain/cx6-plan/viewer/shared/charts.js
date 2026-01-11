/**
 * CORTEX 6.0 HTML Views - Chart.js Configurations
 * ============================================================================
 * Shared Chart.js templates and utility functions
 */

// Load Chart.js library
async function ensureChartJS() {
  if (typeof Chart !== 'undefined') {
    return;
  }
  
  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js';
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('Failed to load Chart.js'));
    document.head.appendChild(script);
  });
}

/**
 * Create a bar chart with CORTEX styling
 */
async function createChartBar(canvasId, labels, datasets, options = {}) {
  await ensureChartJS();
  
  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;

  const defaultColors = ['#00d4ff', '#7b2cbf', '#ff006e', '#06ffa5', '#ffbe0b'];

  const defaultDatasets = datasets.map((dataset, index) => ({
    label: dataset.label,
    data: dataset.data,
    backgroundColor: dataset.backgroundColor || defaultColors[index % defaultColors.length],
    borderColor: dataset.borderColor || defaultColors[index % defaultColors.length],
    borderRadius: 8,
    borderWidth: 0,
    ...dataset
  }));

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#e0e0e0',
          font: { size: 12, family: "'Segoe UI', sans-serif" },
          padding: 15
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        borderColor: '#00d4ff',
        borderWidth: 1,
        titleColor: '#00d4ff',
        bodyColor: '#e0e0e0',
        padding: 12,
        cornerRadius: 8
      }
    },
    scales: {
      x: {
        ticks: { color: '#a0a0a0', font: { size: 11 } },
        grid: { color: 'rgba(26, 31, 58, 0.5)' }
      },
      y: {
        ticks: { color: '#a0a0a0', font: { size: 11 } },
        grid: { color: 'rgba(26, 31, 58, 0.5)' },
        beginAtZero: true
      }
    },
    ...options
  };

  return new Chart(canvas, {
    type: 'bar',
    data: { labels, datasets: defaultDatasets },
    options: chartOptions
  });
}

/**
 * Create a line chart with CORTEX styling
 */
async function createChartLine(canvasId, labels, datasets, options = {}) {
  await ensureChartJS();
  
  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;

  const defaultColors = ['#00d4ff', '#7b2cbf', '#ff006e', '#06ffa5', '#ffbe0b'];

  const defaultDatasets = datasets.map((dataset, index) => ({
    label: dataset.label,
    data: dataset.data,
    borderColor: dataset.borderColor || defaultColors[index % defaultColors.length],
    backgroundColor: `${dataset.borderColor || defaultColors[index % defaultColors.length]}22`,
    borderWidth: 2,
    pointRadius: 4,
    pointBackgroundColor: dataset.borderColor || defaultColors[index % defaultColors.length],
    pointBorderColor: '#fff',
    pointBorderWidth: 2,
    tension: 0.4,
    fill: true,
    ...dataset
  }));

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#e0e0e0',
          font: { size: 12, family: "'Segoe UI', sans-serif" },
          padding: 15
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        borderColor: '#00d4ff',
        borderWidth: 1,
        titleColor: '#00d4ff',
        bodyColor: '#e0e0e0',
        padding: 12,
        cornerRadius: 8
      }
    },
    scales: {
      x: {
        ticks: { color: '#a0a0a0', font: { size: 11 } },
        grid: { color: 'rgba(26, 31, 58, 0.5)' }
      },
      y: {
        ticks: { color: '#a0a0a0', font: { size: 11 } },
        grid: { color: 'rgba(26, 31, 58, 0.5)' },
        beginAtZero: true
      }
    },
    ...options
  };

  return new Chart(canvas, {
    type: 'line',
    data: { labels, datasets: defaultDatasets },
    options: chartOptions
  });
}

/**
 * Create a pie/donut chart with CORTEX styling
 */
async function createChartPie(canvasId, labels, data, options = {}) {
  await ensureChartJS();
  
  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;

  const colors = ['#00d4ff', '#7b2cbf', '#ff006e', '#06ffa5', '#ffbe0b', '#ff9a00', '#40e0d0'];

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#e0e0e0',
          font: { size: 12, family: "'Segoe UI', sans-serif" },
          padding: 15
        },
        position: 'right'
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        borderColor: '#00d4ff',
        borderWidth: 1,
        titleColor: '#00d4ff',
        bodyColor: '#e0e0e0',
        padding: 12,
        cornerRadius: 8,
        callbacks: {
          label: function(context) {
            const total = context.dataset.data.reduce((a, b) => a + b, 0);
            const percentage = ((context.parsed / total) * 100).toFixed(1);
            return `${context.label}: ${context.parsed} (${percentage}%)`;
          }
        }
      }
    },
    ...options
  };

  const chartType = options.donut ? 'doughnut' : 'pie';

  return new Chart(canvas, {
    type: chartType,
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: colors.slice(0, labels.length),
        borderColor: 'rgba(10, 14, 39, 0.8)',
        borderWidth: 2
      }]
    },
    options: chartOptions
  });
}

/**
 * Create a radar chart with CORTEX styling
 */
async function createChartRadar(canvasId, labels, datasets, options = {}) {
  await ensureChartJS();
  
  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;

  const defaultColors = ['#00d4ff', '#7b2cbf', '#ff006e', '#06ffa5'];

  const defaultDatasets = datasets.map((dataset, index) => ({
    label: dataset.label,
    data: dataset.data,
    borderColor: dataset.borderColor || defaultColors[index % defaultColors.length],
    backgroundColor: `${dataset.borderColor || defaultColors[index % defaultColors.length]}22`,
    borderWidth: 2,
    pointRadius: 4,
    pointBackgroundColor: dataset.borderColor || defaultColors[index % defaultColors.length],
    pointBorderColor: '#fff',
    pointBorderWidth: 2,
    ...dataset
  }));

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#e0e0e0',
          font: { size: 12, family: "'Segoe UI', sans-serif" },
          padding: 15
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        borderColor: '#00d4ff',
        borderWidth: 1,
        titleColor: '#00d4ff',
        bodyColor: '#e0e0e0',
        padding: 12,
        cornerRadius: 8
      }
    },
    scales: {
      r: {
        ticks: { color: '#a0a0a0', font: { size: 11 } },
        grid: { color: 'rgba(26, 31, 58, 0.5)' },
        beginAtZero: true
      }
    },
    ...options
  };

  return new Chart(canvas, {
    type: 'radar',
    data: { labels, datasets: defaultDatasets },
    options: chartOptions
  });
}

/**
 * Create a horizontal bar chart
 */
async function createChartHorizontalBar(canvasId, labels, datasets, options = {}) {
  await ensureChartJS();
  
  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;

  const defaultColors = ['#00d4ff', '#7b2cbf', '#ff006e', '#06ffa5', '#ffbe0b'];

  const defaultDatasets = datasets.map((dataset, index) => ({
    label: dataset.label,
    data: dataset.data,
    backgroundColor: dataset.backgroundColor || defaultColors[index % defaultColors.length],
    borderColor: dataset.borderColor || defaultColors[index % defaultColors.length],
    borderRadius: 8,
    borderWidth: 0,
    ...dataset
  }));

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: 'y',
    plugins: {
      legend: {
        labels: {
          color: '#e0e0e0',
          font: { size: 12, family: "'Segoe UI', sans-serif" },
          padding: 15
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        borderColor: '#00d4ff',
        borderWidth: 1,
        titleColor: '#00d4ff',
        bodyColor: '#e0e0e0',
        padding: 12,
        cornerRadius: 8
      }
    },
    scales: {
      x: {
        ticks: { color: '#a0a0a0', font: { size: 11 } },
        grid: { color: 'rgba(26, 31, 58, 0.5)' },
        beginAtZero: true
      },
      y: {
        ticks: { color: '#a0a0a0', font: { size: 11 } },
        grid: { color: 'rgba(26, 31, 58, 0.5)' }
      }
    },
    ...options
  };

  return new Chart(canvas, {
    type: 'bar',
    data: { labels, datasets: defaultDatasets },
    options: chartOptions
  });
}

/**
 * Create a scatter chart
 */
async function createChartScatter(canvasId, datasets, options = {}) {
  await ensureChartJS();
  
  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;

  const defaultColors = ['#00d4ff', '#7b2cbf', '#ff006e', '#06ffa5', '#ffbe0b'];

  const defaultDatasets = datasets.map((dataset, index) => ({
    label: dataset.label,
    data: dataset.data,
    backgroundColor: dataset.backgroundColor || defaultColors[index % defaultColors.length],
    borderColor: dataset.borderColor || defaultColors[index % defaultColors.length],
    borderWidth: 1,
    pointRadius: 6,
    ...dataset
  }));

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#e0e0e0',
          font: { size: 12, family: "'Segoe UI', sans-serif" },
          padding: 15
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        borderColor: '#00d4ff',
        borderWidth: 1,
        titleColor: '#00d4ff',
        bodyColor: '#e0e0e0',
        padding: 12,
        cornerRadius: 8,
        callbacks: {
          label: function(context) {
            return `(${context.parsed.x}, ${context.parsed.y})`;
          }
        }
      }
    },
    scales: {
      x: {
        ticks: { color: '#a0a0a0', font: { size: 11 } },
        grid: { color: 'rgba(26, 31, 58, 0.5)' },
        title: { display: true, text: options.xAxisLabel || 'X Axis', color: '#e0e0e0' }
      },
      y: {
        ticks: { color: '#a0a0a0', font: { size: 11 } },
        grid: { color: 'rgba(26, 31, 58, 0.5)' },
        title: { display: true, text: options.yAxisLabel || 'Y Axis', color: '#e0e0e0' }
      }
    },
    ...options
  };

  return new Chart(canvas, {
    type: 'scatter',
    data: { datasets: defaultDatasets },
    options: chartOptions
  });
}

/**
 * Create a doughnut chart with percentages
 */
async function createChartDoughnut(canvasId, labels, data, options = {}) {
  return createChartPie(canvasId, labels, data, { ...options, donut: true });
}

/**
 * Create a stacked bar chart
 */
async function createChartStackedBar(canvasId, labels, datasets, options = {}) {
  await ensureChartJS();
  
  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;

  const defaultColors = ['#00d4ff', '#7b2cbf', '#ff006e', '#06ffa5', '#ffbe0b'];

  const defaultDatasets = datasets.map((dataset, index) => ({
    label: dataset.label,
    data: dataset.data,
    backgroundColor: dataset.backgroundColor || defaultColors[index % defaultColors.length],
    borderColor: dataset.borderColor || defaultColors[index % defaultColors.length],
    borderRadius: 8,
    borderWidth: 0,
    ...dataset
  }));

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#e0e0e0',
          font: { size: 12, family: "'Segoe UI', sans-serif" },
          padding: 15
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        borderColor: '#00d4ff',
        borderWidth: 1,
        titleColor: '#00d4ff',
        bodyColor: '#e0e0e0',
        padding: 12,
        cornerRadius: 8
      }
    },
    scales: {
      x: {
        stacked: true,
        ticks: { color: '#a0a0a0', font: { size: 11 } },
        grid: { color: 'rgba(26, 31, 58, 0.5)' }
      },
      y: {
        stacked: true,
        ticks: { color: '#a0a0a0', font: { size: 11 } },
        grid: { color: 'rgba(26, 31, 58, 0.5)' },
        beginAtZero: true
      }
    },
    ...options
  };

  return new Chart(canvas, {
    type: 'bar',
    data: { labels, datasets: defaultDatasets },
    options: chartOptions
  });
}

/**
 * Destroy chart instance
 */
function destroyChart(chartInstance) {
  if (chartInstance) {
    chartInstance.destroy();
  }
}

/**
 * Update chart data
 */
function updateChartData(chartInstance, newData, newLabels = null) {
  if (!chartInstance) return;
  
  if (newLabels) {
    chartInstance.data.labels = newLabels;
  }
  
  chartInstance.data.datasets.forEach((dataset, index) => {
    if (newData[index]) {
      dataset.data = newData[index];
    }
  });
  
  chartInstance.update();
}
