# CORTEX Plugin System

**Plugins extend CORTEX functionality seamlessly with zero-footprint architecture!**

## Zero-Footprint Philosophy

CORTEX plugins **do not increase tool dependency footprint** - they use only existing CORTEX brain tiers for intelligence:
- **Tier 2 (Knowledge Graph):** Learned patterns from past implementations
- **Tier 3 (Context Intelligence):** Git analysis, file stability, code health
- **Plugin System:** Natural language routing and command registration

**No external APIs, additional tools, or network dependencies required.**

## Flagship Example: Recommendation API Plugin

**Purpose:** Intelligent code recommendations using only CORTEX brain intelligence  
**Dependencies:** Zero external dependencies  
**Architecture:** Pure CORTEX implementation  

```python
class RecommendationAPIPlugin(BasePlugin):
    def get_natural_language_patterns(self):
        return [
            "recommend improvements", "suggest optimizations", 
            "analyze code quality", "what should I refactor?"
        ]
    
    def execute(self, request, context):
        # Use Tier 2 for learned patterns
        patterns = self.knowledge_graph.search_patterns(query=request)
        
        # Use Tier 3 for file stability analysis  
        stability = self.context_intelligence.get_file_stability(file_path)
        
        # Generate intelligent recommendations
        return self._analyze_and_recommend(patterns, stability)
```

**See full implementation:** `docs/plugins/recommendation-api-plugin.md`

## How It Works

1. Plugins register natural language patterns during initialization
2. Router matches user intent to plugin capabilities
3. Plugin executes with full access to CORTEX brain tiers
4. Results integrate naturally into conversation
5. **Zero external tools or APIs needed**

## Plugin Template

```python
class MyPlugin(BasePlugin):
    def get_natural_language_patterns(self):
        return ["analyze code quality", "review code", "check quality"]
    
    def execute(self, request, context):
        # Access CORTEX brain tiers (no external dependencies)
        tier2_data = self.knowledge_graph.search_patterns(request)
        tier3_data = self.context_intelligence.analyze_files(context)
        
        # Your plugin logic here
        return {"success": True, "data": results}
```

**For plugin developers:** See `src/plugins/base_plugin.py` for API

## Current Active Plugins

- **Recommendation API** (flagship zero-footprint example)
- Platform Switch (auto-detects Mac/Windows/Linux)
- System Refactor (code restructuring)
- Doc Refresh (documentation generation)
- Extension Scaffold (VS Code extension creation)
- Configuration Wizard (setup assistance)
- Code Review (quality analysis)
- Cleanup (workspace maintenance)

All plugins follow the **zero-footprint principle** - no additional tool dependencies required.
