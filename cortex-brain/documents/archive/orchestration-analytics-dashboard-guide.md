# Orchestration Analytics Dashboard - User Guide

**Feature:** Orchestrator Enhancement Plan v2.0 - Feature 15  
**Version:** 3.8.1  
**Author:** Asif Hussain

---

## Overview

The Orchestration Analytics Dashboard provides real-time and historical visualization of orchestrator engagement patterns. It aggregates metrics from `OrchestrationMetricsCollector` logs and generates interactive dashboards and static HTML reports.

---

## Features

### 1. Metrics Aggregation
- **7-day window:** Recent activity trends
- **30-day window:** Monthly performance overview
- **Per-orchestrator stats:** Engagement count, average duration, success rate, error count
- **Daily breakdown:** Activity per day

### 2. Visualizations
- **Performance Trends:** Line charts showing duration over time
- **Success Rate:** Pie charts for success/failure/skip distribution
- **Orchestrator Comparison:** Side-by-side statistics table
- **Multi-orchestrator Trends:** Overlay multiple orchestrators on same chart

### 3. HTML Reports
- **Static reports:** Generated in `cortex-brain/documents/reports/`
- **Embedded charts:** PNG images included in HTML
- **Metadata:** Generation timestamp, data range, aggregate stats
- **Responsive design:** Clean, professional layout

### 4. Live Dashboard
- **Flask server:** Runs on port 5000 (configurable)
- **Endpoints:**
  - `http://localhost:5000/dashboard` - Full HTML dashboard
  - `http://localhost:5000/metrics/7days` - 7-day JSON data
  - `http://localhost:5000/metrics/30days` - 30-day JSON data
  - `http://localhost:5000/health` - Server health check

---

## Usage

### Python API

```python
from src.operations.utilities.orchestration_analytics_dashboard import OrchestrationAnalyticsDashboard

# Initialize dashboard
dashboard = OrchestrationAnalyticsDashboard()

# Generate 7-day aggregated metrics
metrics = dashboard.aggregate_metrics(days=7)
print(f"Total engagements: {metrics['total_engagements']}")
print(f"Success rate: {metrics['success_rate']:.1f}%")

# Compare orchestrators
comparison = dashboard.compare_orchestrators(days=7, sort_by="engagement_count")
for orch in comparison:
    print(f"{orch['orchestrator_name']}: {orch['total_engagements']} engagements")

# Generate performance trends
trend_data = dashboard.generate_performance_trend(days=7)
chart_path = dashboard.generate_duration_chart(trend_data)

# Calculate success metrics
success_metrics = dashboard.calculate_success_metrics(days=7)
pie_chart_path = dashboard.generate_success_pie_chart(success_metrics)

# Generate HTML report
report_path = dashboard.generate_html_report(days=7)
print(f"Report saved: {report_path}")

# Start live dashboard server
dashboard.start_server(host="127.0.0.1", port=5000)
```

### CLI Command (Coming Soon)

```bash
# Launch live dashboard
cortex dashboard launch

# Generate static report
cortex dashboard report --days 7

# Generate 30-day report
cortex dashboard report --days 30 --output custom_report.html
```

---

## Data Source

The dashboard reads metrics from:
```
logs/orchestration-metrics/
├── 2025-12-08/
│   ├── planningorchestrator-abc12345-start.json
│   ├── planningorchestrator-abc12345-complete.json
│   └── ...
├── 2025-12-09/
│   └── ...
└── ...
```

Each event file contains:
- `event_type`: "start" or "complete"
- `event_id`: UUID for matching start/complete
- `orchestrator_name`: Name of orchestrator
- `timestamp`: ISO 8601 timestamp
- `status`: "success", "error", or "skip" (complete events only)
- `duration_ms`: Execution duration (complete events only)

---

## Configuration

### Custom Paths

```python
from pathlib import Path

dashboard = OrchestrationAnalyticsDashboard(
    metrics_base_path=Path("/custom/metrics/path"),
    report_output_path=Path("/custom/reports/path"),
    port=8080  # Custom Flask port
)
```

### Default Paths
- **Metrics:** `CORTEX/logs/orchestration-metrics/`
- **Reports:** `CORTEX/cortex-brain/documents/reports/`
- **Port:** 5000

---

## Output Examples

### Aggregated Metrics (JSON)

```json
{
  "total_engagements": 42,
  "by_orchestrator": {
    "PlanningOrchestrator": {
      "count": 15,
      "avg_duration_ms": 2340.5,
      "success_rate": 93.3,
      "error_count": 1
    },
    "TDDOrchestrator": {
      "count": 27,
      "avg_duration_ms": 1856.2,
      "success_rate": 100.0,
      "error_count": 0
    }
  },
  "by_day": {
    "2025-12-08": 12,
    "2025-12-09": 18,
    "2025-12-10": 12
  },
  "avg_duration_ms": 2034.7,
  "success_rate": 97.6
}
```

### HTML Report Structure

```html
<!DOCTYPE html>
<html>
<head>
    <title>Orchestration Analytics Dashboard</title>
    <!-- Embedded CSS -->
</head>
<body>
    <!-- Header with timestamp and data range -->
    <!-- Stat cards: Total, Avg Duration, Success Rate, Active Orchestrators -->
    <!-- Comparison table with all orchestrators -->
    <!-- Performance trend line chart (PNG) -->
    <!-- Success rate pie chart (PNG) -->
    <!-- Footer with attribution -->
</body>
</html>
```

---

## Performance

- **Metrics loading:** ~10ms per daily folder (7 days = ~70ms)
- **Chart generation:** ~200-500ms per chart (matplotlib)
- **HTML report:** ~1-2 seconds total (including charts)
- **Flask response time:** <100ms for JSON endpoints, <2s for dashboard

---

## Dependencies

```bash
pip install matplotlib>=3.5.0 flask>=2.3.0
```

Already included in `requirements.txt` for CORTEX 3.8.1+.

---

## Integration with Other Features

### OrchestrationMetricsCollector
Dashboard reads metrics collected by `OrchestrationMetricsCollector` (Feature 10):

```python
from src.operations.utilities.orchestration_metrics_collector import with_orchestration_metrics

@with_orchestration_metrics
async def my_orchestrator(request):
    # Your orchestrator logic
    return response
```

### Scheduled Reports (Coming Soon)
Weekly automated reports sent to `cortex-brain/documents/reports/weekly/`:

```yaml
# cortex-brain/config/analytics-config.yaml
scheduled_reports:
  enabled: true
  frequency: weekly  # or daily, monthly
  days: 7
  output_path: cortex-brain/documents/reports/weekly/
```

---

## Troubleshooting

### Issue: No data in dashboard
**Solution:** Ensure orchestrators are using `@with_orchestration_metrics` decorator and metrics are being written to `logs/orchestration-metrics/`.

### Issue: Charts not rendering
**Solution:** Verify matplotlib is installed: `pip install matplotlib>=3.5.0`

### Issue: Flask server won't start
**Solution:** Check if port 5000 is in use: `lsof -i :5000`. Use custom port: `dashboard.start_server(port=8080)`

### Issue: Reports missing data
**Solution:** Check date range - metrics older than 30 days are archived. Verify daily folders exist in `logs/orchestration-metrics/`.

---

## Future Enhancements

- [ ] Real-time WebSocket updates for live dashboard
- [ ] Exportable CSV/JSON data dumps
- [ ] Alerting for anomalous patterns (sudden duration spikes, success rate drops)
- [ ] Integration with CI/CD for automated reporting
- [ ] Historical trend analysis (compare current vs. previous week)

---

## Copyright

© 2024-2025 Asif Hussain. All rights reserved.

**License:** Proprietary - CORTEX Enhancement Plan v2.0
