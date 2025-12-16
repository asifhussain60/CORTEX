# CORTEX Toolkit - Analytics

Analysis, profiling, metrics, and visualization tools.

## Profiling Tools

### profile (`cortex-profile`)

**Purpose:** Performance profiling and analysis.

**File:** `profiling/profile_performance.py`

**Usage:**
```bash
python cortex-toolkit/analytics/profiling/profile_performance.py --module brain
```

**Features:**
- Module-level profiling
- Function execution timing
- Memory usage analysis
- Performance bottleneck detection

---

### startup-profile

**Purpose:** Startup time analysis.

**File:** `profiling/profile_startup.py`

**Usage:**
```bash
python cortex-toolkit/analytics/profiling/profile_startup.py
```

---

## Metrics Tools

### metrics (`cortex-metrics`)

**Purpose:** Collect and display system metrics.

**File:** `metrics/collect_dashboard_data.py`

**Usage:**
```bash
python cortex-toolkit/analytics/metrics/collect_dashboard_data.py
```

**Features:**
- Dashboard data collection
- Progress tracking
- Metric aggregation

---

### brain-health-monitor

**Purpose:** Monitor brain tier health.

**File:** `metrics/monitor_brain_health.py`

**Usage:**
```bash
python cortex-toolkit/analytics/metrics/monitor_brain_health.py
```

---

## Visualization Tools

### visualize (`cortex-visualize`)

**Purpose:** Visualize brain health and metrics.

**File:** `visualization/visualize_brain_health.py`

**Usage:**
```bash
python cortex-toolkit/analytics/visualization/visualize_brain_health.py
```

---

### uml (`cortex-uml`)

**Purpose:** Generate UML diagrams.

**File:** `visualization/generate_uml_standalone.py`

**Usage:**
```bash
python cortex-toolkit/analytics/visualization/generate_uml_standalone.py
```

---

### dependency-graph

**Purpose:** Generate dependency graphs.

**File:** `visualization/dependency_graph_generator.py`

**Usage:**
```bash
python cortex-toolkit/analytics/visualization/dependency_graph_generator.py
```

---

## Output

Analytics tools generate outputs in:
- `logs/toolkit/` - Log files
- `metrics/` - Metric data
- `cortex-lens-output/` - Visualizations
