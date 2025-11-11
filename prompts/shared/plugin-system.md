# CORTEX Plugin System

**Plugins extend CORTEX functionality seamlessly!**

## How It Works

1. Plugins register natural language patterns during initialization
2. Router matches user intent to plugin capabilities
3. Plugin executes with full access to CORTEX brain tiers
4. Results integrate naturally into conversation

## Example Plugin

```python
class MyPlugin(BasePlugin):
    def get_natural_language_patterns(self):
        return ["analyze code quality", "review code", "check quality"]
    
    def execute(self, request, context):
        # Your plugin logic here
        return {"success": True, "data": results}
```

**For plugin developers:** See `src/plugins/base_plugin.py` for API

## Current Active Plugins

- Platform Switch (auto-detects Mac/Windows/Linux)
- System Refactor (code restructuring)
- Doc Refresh (documentation generation)
- Extension Scaffold (VS Code extension creation)
- Configuration Wizard (setup assistance)
- Code Review (quality analysis)
- Cleanup (workspace maintenance)
