# 🔧 Onboarding Dashboard - Deployment Guide

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Last Updated:** November 30, 2025

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Deployment Methods](#deployment-methods)
5. [Production Checklist](#production-checklist)
6. [Monitoring](#monitoring)
7. [Maintenance](#maintenance)

---

## ✅ Prerequisites

### System Requirements

**Minimum:**
- Python 3.8+
- 2GB RAM
- 500MB disk space

**Recommended:**
- Python 3.10+
- 4GB RAM
- 2GB disk space (for caching and exports)

### Required Software

```bash
# Python (3.8+)
python --version

# Graphviz (for UML diagrams)
dot -V

# pip (latest)
pip --version
```

### Installing Graphviz

**macOS:**
```bash
brew install graphviz
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install graphviz libgraphviz-dev
```

**Windows:**
1. Download from https://graphviz.org/download/
2. Add to PATH: `C:\Program Files\Graphviz\bin`
3. Verify: `dot -V`

---

## 📦 Installation

### 1. Clone Repository

```bash
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX
```

### 2. Create Virtual Environment

```bash
# Create venv
python -m venv .venv

# Activate
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### 3. Install Dependencies

```bash
# Core dependencies
pip install -r requirements.txt

# Optional: PPTX export
pip install python-pptx

# Optional: PDF export
pip install weasyprint
```

### 4. Verify Installation

```bash
# Run tests
pytest tests/

# Generate sample dashboard
python examples/generate_sample_dashboard.py
```

---

## ⚙️ Configuration

### Dashboard Configuration

Create `config/dashboard.yaml`:

```yaml
dashboard:
  # Performance
  cache:
    enabled: true
    ttl_hours: 24
    max_size_mb: 100
  
  # Features
  features:
    uml_diagrams: true
    pptx_export: true
    accessibility: true
    responsive: true
  
  # Limits
  limits:
    max_table_rows: 100
    max_uml_classes: 500
    max_chart_points: 1000
  
  # Styling
  theme:
    primary_color: "#0066cc"
    success_color: "#28a745"
    warning_color: "#ffc107"
    danger_color: "#dc3545"
```

### Environment Variables

Create `.env` file:

```bash
# CORTEX Configuration
CORTEX_ENV=production
CORTEX_LOG_LEVEL=INFO

# Dashboard Settings
DASHBOARD_CACHE_DIR=.cache/dashboard
DASHBOARD_OUTPUT_DIR=output/dashboards
DASHBOARD_MAX_AGE_HOURS=24

# Optional: External Services
GRAPHVIZ_PATH=/usr/local/bin/dot
```

---

## 🚀 Deployment Methods

### Method 1: Static Site Generation (Recommended)

**Best for:** Documentation sites, CI/CD pipelines, GitHub Pages

```bash
# Generate dashboard HTML
python -m src.dashboard.cli generate \
  --project-path /path/to/project \
  --output-path ./public/dashboard.html \
  --static

# Deploy to static host
cp ./public/dashboard.html /var/www/html/
```

**Advantages:**
- ✅ No server required
- ✅ Fast loading (pre-generated)
- ✅ Easy to cache (CDN-friendly)
- ✅ Secure (no dynamic execution)

**Deployment Targets:**
- GitHub Pages
- Netlify
- Vercel
- AWS S3 + CloudFront
- Any static file server

### Method 2: Flask Web Application

**Best for:** Dynamic dashboards, real-time updates, authenticated access

```python
# app.py
from flask import Flask, render_template
from src.dashboard.use_cases.generate_dashboard import generate_dashboard_data

app = Flask(__name__)

@app.route('/dashboard/<project_id>')
def show_dashboard(project_id):
    dashboard_data = generate_dashboard_data(project_id)
    return render_template('dashboard.html', **dashboard_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

**Run Server:**
```bash
# Development
flask run --host=0.0.0.0 --port=8000

# Production (with gunicorn)
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Method 3: CI/CD Integration

**GitHub Actions Example:**

```yaml
# .github/workflows/dashboard.yml
name: Generate Dashboard

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 0 * * *'  # Daily

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          sudo apt-get install graphviz
      
      - name: Generate dashboard
        run: |
          python -m src.dashboard.cli generate \
            --project-path . \
            --output-path ./docs/dashboard.html
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
```

---

## ✅ Production Checklist

### Pre-Deployment

- [ ] All tests passing (`pytest tests/`)
- [ ] Dependencies installed and locked (`pip freeze > requirements.txt`)
- [ ] Configuration files reviewed (no sensitive data)
- [ ] Environment variables set
- [ ] Graphviz installed and accessible
- [ ] Cache directory created with write permissions
- [ ] Output directory created with write permissions
- [ ] SSL/TLS certificates configured (if web server)
- [ ] Firewall rules configured
- [ ] Backup strategy in place

### Security

- [ ] Input validation enabled
- [ ] Output encoding enabled
- [ ] XSS protection enabled
- [ ] CSRF protection enabled (if dynamic)
- [ ] HTTPS enforced
- [ ] Authentication implemented (if required)
- [ ] Rate limiting configured
- [ ] Logging enabled
- [ ] Error messages sanitized (no stack traces in production)

### Performance

- [ ] Caching enabled
- [ ] Cache TTL configured
- [ ] Lazy loading enabled
- [ ] Browser caching headers set
- [ ] CDN configured (if static)
- [ ] Database indices created (if dynamic)
- [ ] Connection pooling enabled (if database)
- [ ] Compression enabled (gzip/brotli)

### Monitoring

- [ ] Health check endpoint created
- [ ] Logging configured
- [ ] Error tracking enabled (e.g., Sentry)
- [ ] Performance monitoring enabled
- [ ] Uptime monitoring configured
- [ ] Alert thresholds set

---

## 📊 Monitoring

### Health Check Endpoint

```python
@app.route('/health')
def health_check():
    checks = {
        'cache': check_cache_health(),
        'database': check_database_health(),
        'graphviz': check_graphviz_available(),
        'disk_space': check_disk_space()
    }
    
    healthy = all(checks.values())
    status_code = 200 if healthy else 503
    
    return jsonify({
        'status': 'healthy' if healthy else 'unhealthy',
        'checks': checks,
        'timestamp': datetime.now().isoformat()
    }), status_code
```

### Logging Configuration

```python
# logging_config.yaml
version: 1
formatters:
  standard:
    format: '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
handlers:
  file:
    class: logging.handlers.RotatingFileHandler
    filename: logs/dashboard.log
    maxBytes: 10485760  # 10MB
    backupCount: 5
    formatter: standard
  console:
    class: logging.StreamHandler
    formatter: standard
root:
  level: INFO
  handlers: [file, console]
```

### Metrics to Track

1. **Dashboard Generation Time**
   - Target: <2s (cached), <10s (uncached)
   - Alert: >30s

2. **Cache Hit Rate**
   - Target: >80%
   - Alert: <50%

3. **Error Rate**
   - Target: <1%
   - Alert: >5%

4. **Disk Usage**
   - Target: <1GB cache size
   - Alert: >2GB

---

## 🔄 Maintenance

### Daily Tasks

```bash
# Check health
curl http://localhost:8000/health

# Review logs
tail -f logs/dashboard.log

# Check disk usage
du -sh .cache/dashboard/
```

### Weekly Tasks

```bash
# Update dependencies
pip list --outdated
pip install -U <package>

# Clean old cache
find .cache/dashboard -mtime +7 -delete

# Backup configuration
cp config/dashboard.yaml backups/dashboard-$(date +%Y%m%d).yaml
```

### Monthly Tasks

```bash
# Review performance metrics
python -m src.dashboard.cli stats

# Test restore from backup
cp backups/latest.yaml config/dashboard.yaml

# Update documentation
# Review and update deployment guide
```

### Emergency Procedures

**Dashboard Not Loading:**
```bash
# 1. Check service status
systemctl status dashboard  # systemd
pm2 status dashboard       # PM2

# 2. Check logs
tail -100 logs/dashboard.log

# 3. Restart service
systemctl restart dashboard
pm2 restart dashboard

# 4. Clear cache if needed
rm -rf .cache/dashboard/*
```

**High Memory Usage:**
```bash
# 1. Check cache size
du -sh .cache/dashboard/

# 2. Clear old cache
find .cache/dashboard -mtime +1 -delete

# 3. Reduce cache TTL
# Edit config/dashboard.yaml: cache.ttl_hours = 6

# 4. Restart service
```

---

## 🔗 Additional Resources

- **User Guide:** `onboarding-dashboard-user-guide.md`
- **API Reference:** `api-reference.md`
- **Troubleshooting:** `troubleshooting-guide.md`
- **GitHub Issues:** https://github.com/asifhussain60/CORTEX/issues

---

**Deployment Support:**

For deployment assistance, create an issue on GitHub with:
- Operating system and version
- Python version
- Deployment method
- Error messages and logs
- Steps to reproduce
