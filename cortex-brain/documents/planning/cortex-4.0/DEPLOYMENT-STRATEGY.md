# 🚀 CORTEX 4.0 - Deployment & Distribution Strategy

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Status:** 📋 Planning

---

## 🎯 Deployment Goals

**Vision:** Make CORTEX 4.0 as easy to install as any Python package

**Targets:**
1. **PyPI** - `pip install cortex-ai` (primary)
2. **Docker** - `docker run cortex-ai:4.0` (containerized)
3. **VS Code** - One-click extension install (integrated)
4. **GitHub Action** - Workflow automation (CI/CD)

**Key Requirements:**
- Installation time < 2 minutes
- Zero manual configuration (sensible defaults)
- Cross-platform (Windows, macOS, Linux)
- Offline capable (local LLM optional)

---

## 📦 1. PyPI Package Distribution

### Package Structure

```
cortex-ai/
├── setup.py                     # setuptools configuration
├── pyproject.toml               # Modern Python packaging
├── MANIFEST.in                  # Include non-Python files
├── README.md                    # PyPI description
├── LICENSE                      # MIT License
├── requirements.txt             # Core dependencies
├── requirements-dev.txt         # Development dependencies
├── requirements-llm.txt         # Optional LLM dependencies
├── cortex_core/                 # Core package
├── cortex_orchestrators/        # Orchestrators package
├── cortex_tools/                # Tools package
├── cortex_brain/                # Brain templates (read-only)
└── tests/                       # Test suite (not packaged)
```

### setup.py Configuration

```python
# setup.py
from setuptools import setup, find_packages
from pathlib import Path

# Read long description from README
long_description = (Path(__file__).parent / "README.md").read_text()

# Read requirements
requirements = (Path(__file__).parent / "requirements.txt").read_text().splitlines()
requirements_dev = (Path(__file__).parent / "requirements-dev.txt").read_text().splitlines()
requirements_llm = (Path(__file__).parent / "requirements-llm.txt").read_text().splitlines()

setup(
    name="cortex-ai",
    version="4.0.0",
    author="Asif Hussain",
    author_email="asifhussain60@users.noreply.github.com",
    description="GitHub Copilot memory & planning system with MCP integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/asifhussain60/CORTEX",
    project_urls={
        "Bug Tracker": "https://github.com/asifhussain60/CORTEX/issues",
        "Documentation": "https://cortex-ai.readthedocs.io",
        "Source Code": "https://github.com/asifhussain60/CORTEX",
    },
    packages=find_packages(exclude=["tests*", "docs*", "archive*"]),
    include_package_data=True,  # Include files from MANIFEST.in
    install_requires=requirements,
    extras_require={
        "dev": requirements_dev,
        "llm": requirements_llm,
        "all": requirements_dev + requirements_llm,
    },
    entry_points={
        "console_scripts": [
            "cortex=cortex_core.cli:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="copilot ai planning tdd memory mcp github development",
)
```

### pyproject.toml (Modern Packaging)

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "cortex-ai"
version = "4.0.0"
description = "GitHub Copilot memory & planning system"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
authors = [
    {name = "Asif Hussain", email = "asifhussain60@users.noreply.github.com"}
]
maintainers = [
    {name = "Asif Hussain", email = "asifhussain60@users.noreply.github.com"}
]
keywords = ["copilot", "ai", "planning", "tdd", "mcp"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
]

dependencies = [
    "mcp>=1.0.0",
    "pyyaml>=6.0",
    "click>=8.0",
    "rich>=13.0",
    "pydantic>=2.0",
    "httpx>=0.25.0",
    "aiofiles>=23.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "pytest-asyncio>=0.21",
    "ruff>=0.1.0",
    "mypy>=1.7",
    "black>=23.0",
]
llm = [
    "llama-cpp-python>=0.2.0",
    "transformers>=4.35.0",
]

[project.scripts]
cortex = "cortex_core.cli:main"

[project.urls]
Homepage = "https://github.com/asifhussain60/CORTEX"
Documentation = "https://cortex-ai.readthedocs.io"
Repository = "https://github.com/asifhussain60/CORTEX"
Issues = "https://github.com/asifhussain60/CORTEX/issues"

[tool.setuptools.packages.find]
exclude = ["tests*", "docs*", "archive*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "--cov --cov-report=term-missing --cov-report=html"

[tool.coverage.run]
source = ["cortex_core", "cortex_orchestrators", "cortex_tools"]
omit = ["*/tests/*", "*/test_*.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]

[tool.ruff]
line-length = 100
target-version = "py38"

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### MANIFEST.in

```
# MANIFEST.in - Include non-Python files in package

include README.md
include LICENSE
include requirements.txt
include requirements-dev.txt
include requirements-llm.txt

# Include brain templates
recursive-include cortex_brain/templates *.md *.yaml

# Include MCP schemas
recursive-include cortex_core/mcp/schemas *.json

# Exclude test files
recursive-exclude tests *
recursive-exclude * __pycache__
recursive-exclude * *.py[co]
```

### CLI Entry Point

```python
# cortex_core/cli.py

import click
from pathlib import Path
from rich.console import Console

console = Console()

@click.group()
@click.version_option(version="4.0.0")
def main():
    """CORTEX - GitHub Copilot memory & planning system"""
    pass

@main.command()
@click.option("--path", default=".", help="Project path")
def init(path):
    """Initialize CORTEX brain"""
    console.print("[bold green]Initializing CORTEX brain...[/bold green]")
    
    brain_path = Path(path) / "cortex-brain"
    brain_path.mkdir(exist_ok=True)
    
    # Copy templates from package
    from cortex_brain import copy_templates
    copy_templates(brain_path)
    
    console.print("[bold green]✓ Brain initialized![/bold green]")
    console.print(f"Location: {brain_path}")

@main.command()
def healthcheck():
    """Run system health check"""
    console.print("[bold blue]Running health check...[/bold blue]")
    
    from cortex_orchestrators.maintenance import MaintenanceOrchestrator
    # ... health check logic
    
    console.print("[bold green]✓ System healthy[/bold green]")

@main.command()
@click.option("--port", default=5000, help="Server port")
def serve(port):
    """Start MCP server"""
    console.print(f"[bold blue]Starting MCP server on port {port}...[/bold blue]")
    
    from cortex_core.mcp import CortexMCPServer
    import asyncio
    
    server = CortexMCPServer()
    asyncio.run(server.start(port=port))

if __name__ == "__main__":
    main()
```

### Publishing Workflow

**1. Build Package:**

```bash
# Clean previous builds
rm -rf build dist *.egg-info

# Build source and wheel distributions
python -m build

# Verify package contents
tar -tzf dist/cortex-ai-4.0.0.tar.gz
unzip -l dist/cortex_ai-4.0.0-py3-none-any.whl
```

**2. Test Package Locally:**

```bash
# Install in editable mode
pip install -e .

# Test CLI
cortex --version
cortex init
cortex healthcheck

# Uninstall
pip uninstall cortex-ai
```

**3. Upload to TestPyPI:**

```bash
# Install twine
pip install twine

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ cortex-ai
```

**4. Upload to PyPI:**

```bash
# Upload to production PyPI
twine upload dist/*

# Verify on PyPI
open https://pypi.org/project/cortex-ai/
```

**5. GitHub Release:**

```bash
# Tag release
git tag -a v4.0.0 -m "CORTEX 4.0.0 - Clean Architecture Release"
git push origin v4.0.0

# GitHub Action will automatically publish to PyPI
```

### Automated Publishing

**File:** `.github/workflows/publish.yml`

```yaml
name: Publish to PyPI

on:
  push:
    tags:
      - 'v4.*'

jobs:
  build-and-publish:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install build dependencies
        run: |
          pip install build twine
      
      - name: Build package
        run: python -m build
      
      - name: Check package
        run: twine check dist/*
      
      - name: Publish to TestPyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.TEST_PYPI_API_TOKEN }}
        run: |
          twine upload --repository testpypi dist/*
      
      - name: Test installation from TestPyPI
        run: |
          pip install --index-url https://test.pypi.org/simple/ cortex-ai
          cortex --version
      
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: |
          twine upload dist/*
      
      - name: Create GitHub Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: CORTEX ${{ github.ref }}
          body: |
            CORTEX 4.0.0 - Clean Architecture Release
            
            ## Installation
            ```bash
            pip install cortex-ai
            ```
            
            ## What's New
            - MCP server integration
            - LLM-powered intent routing
            - Team brain features
            - 12 orchestrators migrated
            - 100% test coverage
          draft: false
          prerelease: false
```

---

## 🐳 2. Docker Distribution

### Dockerfile

```dockerfile
# cortex_deployment/docker/Dockerfile

FROM python:3.11-slim as builder

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /build

# Copy requirements
COPY requirements.txt requirements-llm.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt
RUN pip install --no-cache-dir --user -r requirements-llm.txt

# Final stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Set PATH
ENV PATH=/root/.local/bin:$PATH

# Set working directory
WORKDIR /app

# Copy source code
COPY cortex_core/ ./cortex_core/
COPY cortex_orchestrators/ ./cortex_orchestrators/
COPY cortex_tools/ ./cortex_tools/
COPY cortex_brain/ ./cortex_brain/

# Create brain directory
RUN mkdir -p /workspace/cortex-brain

# Expose MCP server port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "from cortex_core.mcp import healthcheck; healthcheck()"

# Entry point
ENTRYPOINT ["python", "-m", "cortex_core.mcp.server"]
CMD ["--host", "0.0.0.0", "--port", "5000"]
```

### docker-compose.yml

```yaml
# cortex_deployment/docker/docker-compose.yml

version: '3.8'

services:
  cortex:
    image: cortex-ai:4.0
    container_name: cortex-mcp-server
    build:
      context: ../..
      dockerfile: cortex_deployment/docker/Dockerfile
    ports:
      - "5000:5000"
    volumes:
      # Mount brain data (persistent)
      - cortex-brain:/workspace/cortex-brain
      # Mount workspace (user code)
      - ${WORKSPACE_PATH:-./workspace}:/workspace
    environment:
      - CORTEX_CONFIG=/app/cortex.config.json
      - CORTEX_LOG_LEVEL=${LOG_LEVEL:-INFO}
      - CORTEX_TEAM_ID=${TEAM_ID:-}
    restart: unless-stopped
    networks:
      - cortex-network

volumes:
  cortex-brain:
    driver: local

networks:
  cortex-network:
    driver: bridge
```

### Usage

```bash
# Build image
docker build -t cortex-ai:4.0 -f cortex_deployment/docker/Dockerfile .

# Run standalone
docker run -d \
  --name cortex \
  -p 5000:5000 \
  -v $(pwd)/cortex-brain:/workspace/cortex-brain \
  -v $(pwd):/workspace \
  cortex-ai:4.0

# Run with docker-compose
export WORKSPACE_PATH=/path/to/workspace
export TEAM_ID=my-team
docker-compose -f cortex_deployment/docker/docker-compose.yml up -d

# View logs
docker logs -f cortex

# Execute commands
docker exec cortex cortex healthcheck

# Stop
docker-compose down
```

### Docker Hub Publishing

```bash
# Login to Docker Hub
docker login

# Tag image
docker tag cortex-ai:4.0 asifhussain60/cortex-ai:4.0
docker tag cortex-ai:4.0 asifhussain60/cortex-ai:latest

# Push to Docker Hub
docker push asifhussain60/cortex-ai:4.0
docker push asifhussain60/cortex-ai:latest

# Users can pull
docker pull asifhussain60/cortex-ai:4.0
```

---

## 🔌 3. VS Code Extension

### package.json

```json
{
  "name": "cortex-copilot-brain",
  "displayName": "CORTEX - Copilot Brain",
  "description": "Memory & planning for GitHub Copilot with MCP integration",
  "version": "4.0.0",
  "publisher": "asifhussain60",
  "icon": "images/icon.png",
  "engines": {
    "vscode": "^1.85.0"
  },
  "categories": ["AI", "Programming Languages", "Other"],
  "keywords": ["copilot", "ai", "planning", "tdd", "memory", "mcp"],
  "repository": {
    "type": "git",
    "url": "https://github.com/asifhussain60/CORTEX"
  },
  "bugs": {
    "url": "https://github.com/asifhussain60/CORTEX/issues"
  },
  "homepage": "https://github.com/asifhussain60/CORTEX#readme",
  "activationEvents": ["onStartupFinished"],
  "main": "./out/extension.js",
  "contributes": {
    "commands": [
      {
        "command": "cortex.init",
        "title": "CORTEX: Initialize Brain"
      },
      {
        "command": "cortex.healthcheck",
        "title": "CORTEX: Health Check"
      },
      {
        "command": "cortex.plan",
        "title": "CORTEX: Plan Feature"
      },
      {
        "command": "cortex.tddStart",
        "title": "CORTEX: Start TDD"
      },
      {
        "command": "cortex.maintenance",
        "title": "CORTEX: System Maintenance"
      }
    ],
    "configuration": {
      "title": "CORTEX",
      "properties": {
        "cortex.mcpServer.enabled": {
          "type": "boolean",
          "default": true,
          "description": "Enable CORTEX MCP server"
        },
        "cortex.mcpServer.port": {
          "type": "number",
          "default": 5000,
          "description": "MCP server port"
        },
        "cortex.mcpServer.autoStart": {
          "type": "boolean",
          "default": true,
          "description": "Auto-start MCP server on VS Code launch"
        },
        "cortex.llmIntent.enabled": {
          "type": "boolean",
          "default": true,
          "description": "Enable LLM-powered intent routing"
        },
        "cortex.team.enabled": {
          "type": "boolean",
          "default": false,
          "description": "Enable team brain features"
        },
        "cortex.team.teamId": {
          "type": "string",
          "default": "",
          "description": "Team ID for shared brain"
        }
      }
    }
  },
  "scripts": {
    "vscode:prepublish": "npm run compile",
    "compile": "tsc -p ./",
    "watch": "tsc -watch -p ./",
    "lint": "eslint src --ext ts",
    "test": "node ./out/test/runTest.js",
    "package": "vsce package",
    "publish": "vsce publish"
  },
  "devDependencies": {
    "@types/vscode": "^1.85.0",
    "@types/node": "^20.0.0",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "eslint": "^8.50.0",
    "typescript": "^5.3.0",
    "@vscode/test-electron": "^2.3.0",
    "vsce": "^2.15.0"
  },
  "dependencies": {
    "mcp": "^1.0.0"
  }
}
```

### Publishing to VS Code Marketplace

```bash
# Install vsce (Visual Studio Code Extension Manager)
npm install -g @vscode/vsce

# Login to publisher account
vsce login asifhussain60

# Package extension
vsce package

# Publish to marketplace
vsce publish

# Users can install
code --install-extension asifhussain60.cortex-copilot-brain
```

---

## 🔄 4. GitHub Action

### action.yml

```yaml
# cortex_deployment/github_action/action.yml

name: 'CORTEX Planning'
description: 'AI-powered feature planning and TDD workflow'
author: 'Asif Hussain'
branding:
  icon: 'cpu'
  color: 'blue'

inputs:
  command:
    description: 'CORTEX command (plan, tdd, sanitize, etc.)'
    required: true
  feature:
    description: 'Feature description (for plan command)'
    required: false
  module:
    description: 'Module name (for tdd command)'
    required: false
  directory:
    description: 'Target directory (for sanitize command)'
    required: false

outputs:
  result:
    description: 'Command execution result'
    value: ${{ steps.cortex.outputs.result }}

runs:
  using: 'composite'
  steps:
    - name: Install CORTEX
      shell: bash
      run: |
        pip install cortex-ai
    
    - name: Initialize Brain
      shell: bash
      run: |
        cortex init
    
    - name: Execute Command
      id: cortex
      shell: bash
      run: |
        cortex ${{ inputs.command }} \
          --feature "${{ inputs.feature }}" \
          --module "${{ inputs.module }}" \
          --directory "${{ inputs.directory }}"
```

### Usage Example

```yaml
# .github/workflows/cortex-planning.yml

name: CORTEX Feature Planning

on:
  issues:
    types: [labeled]

jobs:
  plan-feature:
    if: contains(github.event.issue.labels.*.name, 'needs-plan')
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Plan feature
        id: plan
        uses: asifhussain60/cortex-action@v4
        with:
          command: plan
          feature: ${{ github.event.issue.body }}
      
      - name: Comment plan
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## 🎯 Feature Plan\n\n${{ steps.plan.outputs.result }}`
            })
```

---

## 📊 Deployment Checklist

### Pre-Release
- [ ] All tests passing (100% coverage)
- [ ] Documentation complete
- [ ] CHANGELOG updated
- [ ] Version bumped (4.0.0)
- [ ] License verified (MIT)

### PyPI
- [ ] setup.py configured
- [ ] pyproject.toml configured
- [ ] MANIFEST.in created
- [ ] Package built (`python -m build`)
- [ ] Tested on TestPyPI
- [ ] Published to PyPI
- [ ] Installation verified

### Docker
- [ ] Dockerfile created
- [ ] docker-compose.yml created
- [ ] Image built and tested
- [ ] Published to Docker Hub
- [ ] Pull and run verified

### VS Code Extension
- [ ] package.json configured
- [ ] Extension packaged (`.vsix`)
- [ ] Tested in VS Code
- [ ] Published to marketplace
- [ ] Installation verified

### GitHub Action
- [ ] action.yml created
- [ ] Action tested in workflow
- [ ] Published to marketplace
- [ ] Usage documented

---

## 🎉 Success Metrics

**Installation:**
- [ ] PyPI: `pip install cortex-ai` works
- [ ] Docker: `docker run cortex-ai:4.0` works
- [ ] VS Code: Extension install works
- [ ] GitHub Action: Workflow runs successfully

**Performance:**
- [ ] Installation time < 2 minutes
- [ ] First run setup < 5 minutes
- [ ] MCP server starts < 10 seconds

**User Experience:**
- [ ] Zero manual configuration required
- [ ] Works offline (with keyword fallback)
- [ ] Clear error messages
- [ ] Good documentation

