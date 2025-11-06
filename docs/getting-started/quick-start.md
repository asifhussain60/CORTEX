# Quick Start Guide

Get up and running with CORTEX in under 5 minutes.

## Prerequisites

- Python 3.9 or higher
- Git
- VS Code with GitHub Copilot

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate it (macOS/Linux)
source .venv/bin/activate

# Activate it (Windows)
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure CORTEX

```bash
# Copy the example config
cp cortex.config.example.json cortex.config.json

# Edit with your paths
# Update "brain_path" to your cortex-brain directory
```

## First Use

### 1. Open the Universal Entry Point

In VS Code, open:
```
prompts/user/cortex.md
```

### 2. Make Your First Request

At the bottom of `cortex.md`, add:

```markdown
#file:/Users/asifhussain/PROJECTS/CORTEX/prompts/user/cortex.md

Tell me about my recent work
```

### 3. Let CORTEX Handle It

GitHub Copilot will:
1. Route your request to the right agent
2. Query the brain for relevant context
3. Provide an intelligent response
4. Learn from the interaction

## What Just Happened?

CORTEX:
- ✅ Analyzed your intent
- ✅ Checked conversation history (Tier 1)
- ✅ Referenced the knowledge graph (Tier 2)
- ✅ Pulled development metrics (Tier 3)
- ✅ Routed to the appropriate agent
- ✅ Recorded the interaction

## Next Steps

- [Configure CORTEX](configuration.md) for your environment
- [Read the Architecture Guide](../architecture/overview.md)
- [Explore the Agent System](../agents/overview.md)

## Troubleshooting

### "Module not found" errors

Make sure your virtual environment is activated:
```bash
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
```

### Configuration issues

Verify your `cortex.config.json` paths match your system:
```json
{
  "brain_path": "/absolute/path/to/cortex-brain",
  "project_root": "/absolute/path/to/CORTEX"
}
```

### Need Help?

Check the [full documentation](../index.md) or open an issue on GitHub.

---

**Ready to dive deeper?** Continue to [Installation Details](installation.md)
