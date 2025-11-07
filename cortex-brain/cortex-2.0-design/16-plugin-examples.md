# CORTEX 2.0 Plugin Examples

**Document:** 16-plugin-examples.md  
**Version:** 2.0.0-alpha  
**Date:** 2025-11-07

---

## 🎯 Purpose
Provide concrete plugin examples that demonstrate best practices for:
- Hook usage and return payloads
- Safety and boundary guard integration
- Observability (telemetry, logs)
- Config-driven behavior and lightweight dependencies

---

## 🧱 Conventions
- Each plugin exports `Plugin(BasePlugin)` class
- Metadata includes `plugin_id`, `category`, `priority`, `hooks`
- `execute(context)` inspects `context.get("hook")` if needed
- Safe file writes always go through Boundary Guard

---

## 🧹 Example 1: Temp Cleanup Plugin

Goal: Remove temp files older than N days from `tempRoot`.

```python
# src/plugins/temp_cleanup_plugin.py
from plugins.base_plugin import BasePlugin, PluginMetadata, PluginCategory, PluginPriority
from plugins.hooks import HookPoint
from datetime import datetime, timedelta
from pathlib import Path

class Plugin(BasePlugin):
    def _get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="temp_cleanup_plugin",
            name="Temp Cleanup",
            version="1.0.0",
            category=PluginCategory.UTILITY,
            priority=PluginPriority.MEDIUM,
            description="Removes temp files older than N days",
            dependencies=[],
            hooks=[HookPoint.ON_STARTUP.value, HookPoint.ON_DB_MAINTENANCE.value]
        )

    def execute(self, context):
        cfg = self.config.get("plugins", {}).get("config", {}).get("temp_cleanup_plugin", {})
        days = int(cfg.get("maxAgeDays", 7))
        temp_root = self.config["path_resolver"].resolve(self.config["paths"]["tempRoot"])  # pseudo

        cutoff = datetime.now() - timedelta(days=days)
        removed = 0

        for p in Path(temp_root).glob("**/*"):
            if p.is_file() and datetime.fromtimestamp(p.stat().st_mtime) < cutoff:
                # Boundary guard log only (delete is safe within temp root)
                p.unlink(missing_ok=True)
                removed += 1

        return {"success": True, "removed": removed}
```

---

## 🧭 Example 2: Documentation Lint Plugin

Goal: Lint markdown files and report issues in self-review.

```python
# src/plugins/doc_lint_plugin.py
from plugins.base_plugin import BasePlugin, PluginMetadata, PluginCategory, PluginPriority
from plugins.hooks import HookPoint
from pathlib import Path

class Plugin(BasePlugin):
    def _get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="doc_lint_plugin",
            name="Documentation Lint",
            version="1.0.0",
            category=PluginCategory.VALIDATION,
            priority=PluginPriority.LOW,
            description="Lints markdown docs for structure and code fences",
            dependencies=[],
            hooks=[HookPoint.ON_SELF_REVIEW.value]
        )

    def execute(self, context):
        docs_root = self.config["path_resolver"].resolve(self.config["paths"]["docsRoot"])  # pseudo
        issues = []
        for md in Path(docs_root).glob("**/*.md"):
            text = md.read_text(encoding="utf-8", errors="ignore")
            if text.count("```") % 2 != 0:
                issues.append({"file": str(md), "issue": "Unbalanced code fences"})
            if not text.strip().startswith("# "):
                issues.append({"file": str(md), "issue": "Missing top-level header"})
        return {"success": True, "issues": issues}
```

---

## 🗂️ Example 3: Knowledge Organizer Plugin

Goal: Classify and move incoming artifacts to the correct project folder.

```python
# src/plugins/knowledge_organizer_plugin.py
from plugins.base_plugin import BasePlugin, PluginMetadata, PluginCategory, PluginPriority
from plugins.hooks import HookPoint
from pathlib import Path
import shutil

class Plugin(BasePlugin):
    def _get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="knowledge_organizer_plugin",
            name="Knowledge Organizer",
            version="1.0.0",
            category=PluginCategory.ORGANIZATION,
            priority=PluginPriority.MEDIUM,
            description="Classifies and organizes artifacts into project folders",
            dependencies=[],
            hooks=[HookPoint.ON_AFTER_WRITE.value]
        )

    def execute(self, context):
        path = Path(context["path"])  # recently written artifact
        # Simple rule: move screenshots to docs/images
        if path.suffix.lower() in {".png", ".jpg"}:
            images = Path(self.config["path_resolver"].resolve("docs/images/"))
            images.mkdir(parents=True, exist_ok=True)
            target = images / path.name
            shutil.move(str(path), str(target))
            return {"success": True, "moved_to": str(target)}
        return {"success": True}
```

Safety note: in production, ensure Boundary Guard permits the target path and record provenance.

---

## 🔍 Example 4: Rule Compliance Reporter

Goal: Aggregate rule compliance stats for dashboards.

```python
# src/plugins/rule_compliance_reporter.py
from plugins.base_plugin import BasePlugin, PluginMetadata, PluginCategory, PluginPriority
from plugins.hooks import HookPoint

class Plugin(BasePlugin):
    def _get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="rule_compliance_reporter",
            name="Rule Compliance Reporter",
            version="1.0.0",
            category=PluginCategory.REPORTING,
            priority=PluginPriority.LOW,
            description="Summarizes rule compliance for dashboards",
            dependencies=[],
            hooks=[HookPoint.ON_SELF_REVIEW.value]
        )

    def execute(self, context):
        # Imagine these are loaded from tier0 rules runtime
        rules = [
            {"number": 22, "title": "Brain Protector", "compliant": True},
            {"number": 4, "title": "Paths relative", "compliant": True}
        ]
        noncompliant = [r for r in rules if not r["compliant"]]
        return {"success": True, "noncompliant": len(noncompliant)}
```

---

## 🧰 Example 5: Simple Health Monitor

Goal: Record a heartbeat row to confirm scheduler working.

```python
# src/plugins/heartbeat_plugin.py
from plugins.base_plugin import BasePlugin, PluginMetadata, PluginCategory, PluginPriority
from plugins.hooks import HookPoint
from datetime import datetime

class Plugin(BasePlugin):
    def _get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="heartbeat_plugin",
            name="Heartbeat",
            version="1.0.0",
            category=PluginCategory.MONITORING,
            priority=PluginPriority.LOW,
            description="Writes a heartbeat timestamp",
            dependencies=[],
            hooks=[HookPoint.ON_STARTUP.value]
        )

    def execute(self, context):
        return {"success": True, "timestamp": datetime.now().isoformat()}
```

---

## ✅ Best Practices Checklist

- Use PathResolver for all file paths
- Validate writes with Boundary Guard
- Keep plugin state minimal; prefer DB tables for durable data
- Return structured payloads; always include `success`
- Log durations and errors via standard telemetry surfaces
- Add tests per plugin (unit + minimal component level)

---

## 🧪 Testing Plugins

- Unit test `execute` for expected contexts
- Component test hooks integration via a small registry + router stub
- Verify telemetry rows inserted on failure (if you write to DB)

---

**Next:** 17-monitoring-dashboard.md (Real-time health monitoring)
