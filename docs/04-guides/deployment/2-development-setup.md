# Development Setup

**Status:** Production Ready | **Last Updated:** 2026-01-21

Local development environment setup for CORTEX development.

## Prerequisites

- Python 3.8+
- Git
- Virtual environment tool
- Code editor (VS Code recommended)

## Step 1: Clone Repository

```bash
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX
```

## Step 2: Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e ".[dev]"
```

## Step 4: Configure IDE

### VS Code

1. Install Python extension
2. Select interpreter: `venv/bin/python`
3. Install Pylance for language support
4. Create `.vscode/settings.json`:

```json
{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "[python]": {
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "ms-python.python"
    }
}
```

## Step 5: Run Tests

```bash
pytest tests/
pytest --cov=cortex tests/
```

## Step 6: Start Development Server

```bash
cortex api start --debug
```

## Development Commands

| Command | Purpose |
|---------|---------|
| `pytest` | Run tests |
| `black .` | Format code |
| `flake8 cortex/` | Lint code |
| `mypy cortex/` | Type checking |
| `cortex db init` | Initialize database |

## Related Resources

- [Local Setup Tutorial](../../06-tutorials/operations/1-local-setup.md)
- [Contributing Guidelines](../../07-contributing/1-contributing-guidelines.md)
