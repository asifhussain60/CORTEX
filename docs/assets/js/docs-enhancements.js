(function () {
  function findAssetPath(assetPath) {
    var candidates = [
      assetPath,
      './' + assetPath,
      '../' + assetPath,
      '../../' + assetPath,
      '../../../' + assetPath,
      '../../../../' + assetPath,
      '/assets/' + assetPath.split('/').slice(-2).join('/')
    ];

    for (var i = 0; i < candidates.length; i += 1) {
      var href = candidates[i].replace(/\/\/+/, '/');
      try {
        var url = new URL(href, window.location.href);
        if (url.pathname.indexOf('/assets/') !== -1) {
          return url.href;
        }
      } catch (error) {
      }
    }

    return assetPath;
  }

  function ensureStylesheet() {
    if (document.querySelector('link[data-cortex-enhancements="1"]')) {
      return;
    }

    var link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = findAssetPath('assets/css/docs-enhancements.css');
    link.setAttribute('data-cortex-enhancements', '1');
    document.head.appendChild(link);
  }

  function loadD3AndRun(callback) {
    if (window.d3) {
      callback();
      return;
    }
    var script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js';
    script.async = true;
    script.onload = callback;
    document.head.appendChild(script);
  }

  function summarizeContext() {
    var h1 = document.querySelector('h1');
    var text = (document.body.innerText || '').replace(/\s+/g, ' ').trim();
    var words = text ? text.split(' ').length : 0;
    var sectionCount = document.querySelectorAll('section').length;
    var linkCount = document.querySelectorAll('a[href]').length;
    return {
      title: h1 ? h1.textContent.trim() : document.title,
      words: words,
      sections: sectionCount,
      links: linkCount
    };
  }

  function injectContentPanel(metrics) {
    var anchor = document.querySelector('main') || document.body;
    if (!anchor || document.getElementById('cortex-enhance-wrap')) {
      return;
    }

    var wrap = document.createElement('section');
    wrap.id = 'cortex-enhance-wrap';
    wrap.className = 'cortex-enhance-wrap';
    wrap.setAttribute('aria-label', 'CORTEX page enhancement insights');

    wrap.innerHTML = [
      '<div class="cortex-enhance-grid">',
      '  <article class="cortex-enhance-card">',
      '    <h2 class="cortex-enhance-title">View Enhancement Summary</h2>',
      '    <p class="cortex-enhance-text">This panel adds cross-page context so each documentation view exposes a consistent quick-read and operational signal.</p>',
      '    <ul class="cortex-enhance-list">',
      '      <li><strong>Focus:</strong> ' + escapeHtml(metrics.title) + '</li>',
      '      <li><strong>Content Density:</strong> ' + metrics.words.toLocaleString() + ' words</li>',
      '      <li><strong>Structure:</strong> ' + metrics.sections + ' sections and ' + metrics.links + ' links</li>',
      '      <li><strong>Actionability:</strong> Use this view with linked role, learning, and architecture pages for end-to-end context.</li>',
      '    </ul>',
      '  </article>',
      '  <article class="cortex-enhance-card">',
      '    <h2 class="cortex-enhance-title">Page Signal Graph (D3.js)</h2>',
      '    <p class="cortex-enhance-text">A normalized bar graph compares this page\'s information signals to a baseline range across docs.</p>',
      '    <div class="cortex-enhance-chart" id="cortex-enhance-chart" role="img" aria-label="D3 chart showing normalized content metrics"></div>',
      '  </article>',
      '</div>'
    ].join('');

    anchor.appendChild(wrap);
  }

  function escapeHtml(text) {
    return String(text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/\"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function normalize(value, max) {
    if (!max) return 0;
    return Math.max(0, Math.min(1, value / max));
  }

  function renderChart(metrics) {
    var container = document.getElementById('cortex-enhance-chart');
    if (!container || !window.d3) {
      return;
    }

    var baseline = {
      words: 4000,
      sections: 18,
      links: 80
    };

    var data = [
      { label: 'Words', value: normalize(metrics.words, baseline.words), raw: metrics.words },
      { label: 'Sections', value: normalize(metrics.sections, baseline.sections), raw: metrics.sections },
      { label: 'Links', value: normalize(metrics.links, baseline.links), raw: metrics.links }
    ];

    var width = Math.max(container.clientWidth, 320);
    var height = 220;
    var margin = { top: 20, right: 20, bottom: 42, left: 38 };
    var innerWidth = width - margin.left - margin.right;
    var innerHeight = height - margin.top - margin.bottom;

    var svg = d3.select(container)
      .append('svg')
      .attr('viewBox', '0 0 ' + width + ' ' + height)
      .attr('preserveAspectRatio', 'xMidYMid meet');

    var g = svg.append('g').attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

    var x = d3.scaleBand()
      .domain(data.map(function (d) { return d.label; }))
      .range([0, innerWidth])
      .padding(0.28);

    var y = d3.scaleLinear()
      .domain([0, 1])
      .nice()
      .range([innerHeight, 0]);

    g.append('g')
      .attr('transform', 'translate(0,' + innerHeight + ')')
      .call(d3.axisBottom(x))
      .selectAll('text')
      .attr('fill', '#cbd5e1');

    g.append('g')
      .call(d3.axisLeft(y).ticks(4).tickFormat(function (d) { return Math.round(d * 100) + '%'; }))
      .selectAll('text')
      .attr('fill', '#94a3b8');

    g.selectAll('.domain, .tick line')
      .attr('stroke', 'rgba(148,163,184,0.28)');

    g.selectAll('rect.metric-bar')
      .data(data)
      .enter()
      .append('rect')
      .attr('class', 'metric-bar')
      .attr('x', function (d) { return x(d.label); })
      .attr('y', function (d) { return y(d.value); })
      .attr('width', x.bandwidth())
      .attr('height', function (d) { return innerHeight - y(d.value); })
      .attr('rx', 8)
      .attr('fill', 'rgba(34, 211, 238, 0.75)');

    g.selectAll('text.metric-value')
      .data(data)
      .enter()
      .append('text')
      .attr('class', 'metric-value')
      .attr('x', function (d) { return x(d.label) + x.bandwidth() / 2; })
      .attr('y', function (d) { return y(d.value) - 8; })
      .attr('text-anchor', 'middle')
      .attr('fill', '#e2e8f0')
      .attr('font-size', '12px')
      .text(function (d) { return d.raw; });
  }

  function run() {
    ensureStylesheet();
    var metrics = summarizeContext();
    injectContentPanel(metrics);
    loadD3AndRun(function () {
      renderChart(metrics);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }
})();
