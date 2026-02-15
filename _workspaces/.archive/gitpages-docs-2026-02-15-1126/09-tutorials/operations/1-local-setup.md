# Tutorial: Local Setup

**Time:** 15 minutes | **Level:** Beginner  
**Goal:** Set up CORTEX for local development

## Overview

Getting CORTEX running locally for development and testing is the first step. This tutorial covers the complete setup process.

## Prerequisites

- Python 3.8+
- Git installed
- 2GB free disk space
- Basic terminal knowledge

## Step 1: Clone and Install

```bash
# Clone repository
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Step 2: Configuration

Create `.env` file:

```env
CORTEX_ENV=development
CORTEX_DEBUG=true
CORTEX_LOG_LEVEL=DEBUG
CORTEX_DATABASE_URL=sqlite:///cortex.db
CORTEX_API_HOST=127.0.0.1
CORTEX_API_PORT=8000
```

## Step 3: Initialize Database

```bash
cortex db init
cortex db migrate
```

## Step 4: Start Services

```bash
# Terminal 1: Start API server
cortex api start

# Terminal 2: Start orchestrator service
cortex orchestrator service start

# Terminal 3: Start monitoring
cortex monitor start
```

## Step 5: Verify Installation

```bash
# Check API is running
curl http://localhost:8000/health

# List orchestrators
cortex orchestrator list

# Execute a test orchestrator
cortex orchestrator execute --orchestrator hello_world --user alice
```

## Troubleshooting

### Python Not Found
```bash
# Ensure Python 3.8+ is installed
python --version

# Use python3 if python isn't available
python3 --version
```

### Module Import Errors
```bash
# Reinstall with development dependencies
pip install -e ".[dev]"

# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
```

### Port Already in Use
```bash
# Change port in .env
CORTEX_API_PORT=8001

# Or find process using port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows
```

## Development Commands

```bash
# Run tests
pytest tests/

# Run tests with coverage
pytest --cov=cortex tests/

# Lint code
flake8 cortex/

# Format code
black cortex/

# Type checking
mypy cortex/
```

## Next Steps

- [Monitoring Dashboard](2-monitoring-dashboard.md) - Monitor your setup
- [Installation](../../01-getting-started/0-installation.md) - Full installation guide
