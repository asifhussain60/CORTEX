# Plugin System Details Narrative

## For Leadership

The Plugin System enables extensibility without bloating CORTEX core, allowing custom functionality while maintaining architectural integrity.

**Zero-Footprint Philosophy** - Plugins use existing CORTEX brain tiers (no external APIs, no additional tools, no network dependencies). Like adding furniture to a room without expanding the foundation.

**Natural Language Discovery** - Plugins register trigger phrases: "recommend improvements" → Recommendation Plugin, "analyze code quality" → Code Review Plugin. Users don't memorize plugin names; they just ask naturally.

**Seamless Integration** - Plugins access full CORTEX intelligence (Tier 2 patterns, Tier 3 metrics) and return results in standard format. To users, plugins feel like native CORTEX features.

**Flagship Example** - Recommendation API Plugin: analyzes code using learned patterns (Tier 2) and file stability (Tier 3), suggests refactoring priorities. No external tools required; pure CORTEX intelligence.

**Business Impact:** Customize CORTEX for your domain (healthcare, finance, e-commerce) without forking codebase. Add company-specific workflows while maintaining upgrade path.

## For Developers

**Plugin Architecture:**

```
User Request ("recommend improvements")
        ↓
Intent Router (detects plugin trigger)
        ↓
Plugin Manager (loads Recommendation Plugin)
        ↓
Plugin Execution:
  - Access Tier 2 (learned patterns)
  - Access Tier 3 (file stability, git metrics)
  - Generate recommendations
        ↓
Return to user (standard format)
```

**Base Plugin Class:**

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BasePlugin(ABC):
    """Base class for all CORTEX plugins"""
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.version = "1.0.0"
        self.enabled = True
    
    @abstractmethod
    def get_natural_language_patterns(self) -> List[str]:
        """Return trigger phrases for natural language detection"""
        pass
    
    @abstractmethod
    def execute(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Main execution logic"""
        pass
    
    def validate(self, context: Dict[str, Any]) -> bool:
        """Validate inputs before execution"""
        return True
    
    def on_before_execute(self, context: Dict[str, Any]):
        """Hook called before main execution"""
        pass
    
    def on_after_execute(self, result: Dict[str, Any]):
        """Hook called after execution"""
        pass
    
    def on_error(self, error: Exception):
        """Hook called if execution fails"""
        pass
```

**Recommendation Plugin (Flagship Example):**

```python
class RecommendationAPIPlugin(BasePlugin):
    """Intelligent code recommendations using CORTEX brain"""
    
    def __init__(self):
        super().__init__()
        self.knowledge_graph = KnowledgeGraph()  # Tier 2
        self.context_intelligence = ContextIntelligence()  # Tier 3
    
    def get_natural_language_patterns(self) -> List[str]:
        return [
            "recommend improvements",
            "suggest optimizations",
            "analyze code quality",
            "what should I refactor?",
            "code review recommendations"
        ]
    
    def execute(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        file_path = context.get("file_path")
        
        # Use Tier 3 for file stability
        stability = self.context_intelligence.get_file_stability(file_path)
        metrics = self.context_intelligence.get_file_metrics(file_path)
        
        # Use Tier 2 for learned patterns
        similar_files = self.knowledge_graph.find_similar_files(file_path)
        successful_patterns = self.knowledge_graph.get_successful_refactorings()
        
        # Generate recommendations
        recommendations = []
        
        # Stability-based recommendations
        if stability == "volatile":
            recommendations.append({
                "priority": "high",
                "type": "stability",
                "title": "Reduce File Churn",
                "description": f"File has {metrics.churn_rate:.0%} churn rate (volatile)",
                "suggestion": "Consider breaking into smaller, focused modules",
                "effort": "medium",
                "impact": "high"
            })
        
        # Complexity-based recommendations
        if metrics.total_lines > 400:
            recommendations.append({
                "priority": "medium",
                "type": "complexity",
                "title": "Reduce File Size",
                "description": f"File has {metrics.total_lines} lines (large)",
                "suggestion": "Apply Single Responsibility Principle",
                "effort": "high",
                "impact": "medium"
            })
        
        # Pattern-based recommendations
        for pattern in successful_patterns:
            if pattern.applicable_to(file_path):
                recommendations.append({
                    "priority": "low",
                    "type": "pattern",
                    "title": f"Apply {pattern.title}",
                    "description": f"Similar files improved by {pattern.improvement:.0%}",
                    "suggestion": pattern.steps,
                    "effort": "low",
                    "impact": "medium"
                })
        
        return {
            "success": True,
            "file": file_path,
            "stability": stability,
            "recommendations": sorted(recommendations, key=lambda r: r["priority"])
        }
```

**Plugin Registration:**

```python
class PluginManager:
    def __init__(self):
        self.plugins = {}
        self.trigger_map = {}
    
    def register_plugin(self, plugin: BasePlugin):
        # Store plugin
        self.plugins[plugin.name] = plugin
        
        # Register natural language triggers
        for trigger in plugin.get_natural_language_patterns():
            self.trigger_map[trigger.lower()] = plugin
    
    def find_plugin(self, user_request: str) -> Optional[BasePlugin]:
        # Check for direct trigger match
        request_lower = user_request.lower()
        for trigger, plugin in self.trigger_map.items():
            if trigger in request_lower:
                return plugin
        return None
    
    def execute_plugin(self, plugin_name: str, request: str, context: Dict[str, Any]):
        plugin = self.plugins.get(plugin_name)
        if not plugin or not plugin.enabled:
            raise ValueError(f"Plugin {plugin_name} not found or disabled")
        
        # Validate inputs
        if not plugin.validate(context):
            raise ValueError("Plugin validation failed")
        
        # Execute with lifecycle hooks
        try:
            plugin.on_before_execute(context)
            result = plugin.execute(request, context)
            plugin.on_after_execute(result)
            return result
        except Exception as e:
            plugin.on_error(e)
            raise
```

**Plugin Discovery:**

```python
def discover_plugins(plugin_directory: str) -> List[BasePlugin]:
    """Auto-discover plugins from directory"""
    plugins = []
    
    for file in os.listdir(plugin_directory):
        if file.endswith("_plugin.py"):
            module_name = file[:-3]
            module = importlib.import_module(f"plugins.{module_name}")
            
            # Find plugin classes
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BasePlugin) and 
                    obj != BasePlugin):
                    plugin = obj()
                    plugins.append(plugin)
    
    return plugins
```

**Plugin Testing:**

```python
class TestRecommendationPlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = RecommendationAPIPlugin()
    
    def test_natural_language_patterns(self):
        patterns = self.plugin.get_natural_language_patterns()
        self.assertIn("recommend improvements", patterns)
        self.assertIn("suggest optimizations", patterns)
    
    def test_volatile_file_recommendation(self):
        context = {
            "file_path": "HostControlPanel.razor",
            "churn_rate": 0.32,  # volatile
            "total_lines": 450
        }
        
        result = self.plugin.execute("recommend improvements", context)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["stability"], "volatile")
        
        # Should recommend reducing churn
        high_priority = [r for r in result["recommendations"] if r["priority"] == "high"]
        self.assertTrue(any("churn" in r["title"].lower() for r in high_priority))
```

## Key Takeaways

1. **Zero-footprint** - No external dependencies, pure CORTEX intelligence
2. **Natural language** - Users trigger plugins with plain English
3. **Brain-powered** - Full access to Tier 2 patterns and Tier 3 metrics
4. **Lifecycle hooks** - Before/after execute, error handling
5. **Auto-discovery** - Drop plugin file in directory, auto-registered

## Usage Scenarios

**Scenario 1: Code Quality Recommendations**
```
User: "recommend improvements for AuthService.cs"

Plugin Execution:
  1. Recommendation Plugin activated (trigger match)
  2. Access Tier 3: File stability = "volatile" (32% churn)
  3. Access Tier 2: Find similar successful refactorings
  4. Generate recommendations:
     - HIGH: Reduce file churn (break into modules)
     - MEDIUM: Reduce complexity (520 lines → 300 lines)
     - LOW: Apply authentication_refactor pattern (88% success rate)

Result: Prioritized list of actionable recommendations with effort/impact
```

**Scenario 2: Custom Domain Plugin**
```
Plugin: HealthcareCompliancePlugin

Natural Language Triggers:
  - "check HIPAA compliance"
  - "validate PHI handling"
  - "audit patient data access"

Execution:
  1. User: "check HIPAA compliance"
  2. Plugin analyzes code using Tier 2 patterns
  3. Checks against healthcare_compliance.yaml rules
  4. Flags PHI data handling issues
  5. Returns compliance report with violations and fixes
```

**Scenario 3: Plugin Chaining**
```
User: "analyze code quality and generate docs"

CORTEX executes:
  1. CodeQualityPlugin (recommendations)
  2. Passes results to DocumentationPlugin
  3. Generates docs with quality insights embedded
  4. Returns comprehensive report

Plugins chain via context passing
```

*Version: 1.0*  
*Last Updated: November 17, 2025*
