# Installation

Set up CORTEX in your project in under 10 minutes.

## Prerequisites

- **GitHub Copilot** (subscription required)
- **VS Code** with GitHub Copilot extension
- **Git** (for version control)
- **Python 3.8+** (for CORTEX brain system)

## Step 1: Clone CORTEX

```bash
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX
```

## Step 2: Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r CORTEX/requirements.txt
```

## Step 3: Initialize the Brain

```bash
# Run setup script
python setup_cortex.py

# This creates:
# - cortex-brain/ directory structure
# - Tier 0-5 storage files
# - Initial configuration
```

You should see:

```
✅ CORTEX Brain initialized
   📁 cortex-brain/ created
   📚 Tier 0: Governance rules loaded
   🧠 Tier 1: Conversation memory ready
   🧩 Tier 2: Knowledge graph created
   📊 Tier 3: Development context initialized
   🎬 Tier 4: Event stream ready
   🏥 Tier 5: Protection system active

✨ CORTEX is ready!
```

## Step 4: Configure (Optional)

Edit `cortex.config.json` to customize:

```json
{
  "brain": {
    "conversation_limit": 20,
    "auto_update_threshold": 50,
    "tier3_refresh_interval": 3600
  },
  "agents": {
    "enable_brain_protector": true,
    "enforce_tdd": true
  },
  "project": {
    "name": "MyProject",
    "type": "web-application"
  }
}
```

See [Configuration Guide](configuration.md) for all options.

## Step 5: Test Your Setup

```bash
# Quick test
python test_cortex.py

# Expected output:
# ✅ Brain structure exists
# ✅ Tier 0 rules loaded (23 rules)
# ✅ Conversation manager operational
# ✅ Knowledge graph ready
# ✅ Event logger functional
# ✅ Protection system active
#
# 🎉 All systems operational!
```

## Step 6: First Interaction

Open GitHub Copilot Chat and try:

```markdown
#file:prompts/user/cortex.md

Test CORTEX setup
```

CORTEX should respond with:

```
✅ CORTEX Brain Operational

Status: All systems green
- Tier 0: 23 governance rules active
- Tier 1: 0/20 conversations (empty, ready)
- Tier 2: Initial patterns loaded
- Tier 3: Collecting baseline metrics
- Tier 4: Event stream active
- Tier 5: Protection enabled

Ready to start learning from your project! 🧠
```

## Troubleshooting

### "Python not found"

Install Python 3.8+ from [python.org](https://python.org)

### "Module not found: yaml"

```bash
pip install pyyaml
```

### "Brain directory not created"

Check permissions:
```bash
# Windows
icacls cortex-brain /grant Everyone:F

# macOS/Linux
chmod -R 755 cortex-brain
```

### "Copilot doesn't recognize cortex.md"

Ensure the file path is correct:
```
prompts/user/cortex.md (relative to project root)
```

## Project Structure

After installation:

```
your-project/
├── cortex-brain/           # Brain storage
│   ├── conversation-history.jsonl
│   ├── conversation-context.jsonl
│   ├── knowledge-graph.yaml
│   ├── development-context.yaml
│   └── events.jsonl
├── prompts/
│   └── user/
│       └── cortex.md       # Universal entry point
├── governance/
│   └── rules.md            # Tier 0 instincts
├── cortex.config.json      # Configuration
└── setup_cortex.py         # Setup script
```

## Verification Checklist

- ✅ Python environment active
- ✅ Dependencies installed
- ✅ Brain directory created
- ✅ Tier 0 rules loaded
- ✅ Test script passes
- ✅ Copilot recognizes cortex.md
- ✅ First interaction successful

## Next Steps

- **[Your First Task](first-task.md)** - Complete a full workflow
- **[Configuration](configuration.md)** - Customize for your project
- **[Understanding the Brain](../guides/brain-system.md)** - Learn how memory works

## Integration with Existing Projects

CORTEX can be added to existing projects:

1. Copy `prompts/` and `cortex-brain/` to your project
2. Run `setup_cortex.py` in your project directory
3. CORTEX will start learning from your existing codebase

No changes to your existing code required!

## Uninstallation

To remove CORTEX:

```bash
# Remove brain directory
rm -rf cortex-brain/

# Remove prompts
rm -rf prompts/

# Remove config
rm cortex.config.json

# Deactivate environment
deactivate
```

Your code remains untouched—CORTEX only adds intelligence, doesn't modify your project structure.
