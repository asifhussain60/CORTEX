# Brain Crawler Agent

**Version:** 1.1 (YAML-based configuration)  
**Status:** 🕷️ ACTIVE  
**Config:** `#file:cortex-brain/agents/crawler-config.yaml`

---

## 🎯 Purpose

Comprehensive codebase analysis agent that **crawls the entire application** and feeds BRAIN with essential information, similar to how Google's crawler indexes websites.

**Think of it as:**
- 🕷️ Google Bot for your codebase
- 📊 Census of your application
- 🧠 BRAIN's initial education system
- 🗺️ Map of your application's architecture

---

## 🚀 Quick Start

### Invoke Full Crawl
```bash
# Load crawler config
#file:cortex-brain/agents/crawler-config.yaml

# Execute full crawl
python src/operations/brain_crawler.py --mode=full
```

### Incremental Update (Fast)
```bash
# Crawl only changed files since last run
python src/operations/brain_crawler.py --mode=incremental
```

---

## 🏗️ What Gets Crawled

Load complete crawl targets from: `#file:cortex-brain/agents/crawler-config.yaml`

**Three Discovery Phases:**

1. **Phase 1: Structure** (Fast - ~30 seconds)
   - File/directory tree
   - Component hierarchy
   - Service layer patterns
   - API structure
   - Test organization

2. **Phase 2: Relationships** (Medium - ~2 minutes)
   - File dependencies (imports/using)
   - Git co-modification patterns
   - Component composition
   - Service injection patterns
   - API-to-UI mappings

3. **Phase 3: Deep Analysis** (Slow - ~5 minutes)
   - Code parsing and AST analysis
   - Test framework detection
   - Coverage mapping
   - Visual regression tool discovery

---

## 📊 BRAIN Feeding Strategy

```yaml
Tier 1 (Working Memory):
  - Real-time file activity
  - Recent modification patterns
  
Tier 2 (Knowledge Graph):
  - file_relationships.yaml (after each crawl)
  - Component hierarchy
  - Dependency graphs
  
Tier 3 (Context Intelligence):
  - validation_insights.yaml (after full crawl)
  - Architectural patterns
  - Test strategy insights
```

---

## 🔄 Update Modes

### Incremental (Default)
- **Trigger:** File modification detected
- **Scope:** Modified file + dependencies
- **Speed:** Fast (~10 seconds)
- **Use:** Continuous development

### Full Recrawl
- **Trigger:** Manual request or 7 days elapsed
- **Scope:** Entire codebase
- **Speed:** Slow (~5 minutes)
- **Use:** Major refactors, weekly maintenance

---

## 🎯 Output Files

All crawler results stored in CORTEX brain:

```yaml
file_relationships.yaml:
  - Architectural patterns
  - Component relationships
  - Dependency graphs

tier3/validation-insights.yaml:
  - Test patterns
  - Framework detection
  - Selector conventions

knowledge-graph.yaml:
  - Code-to-docs relationships
  - API mappings
  - Cross-cutting concerns

tier3/crawler-metrics.json:
  - Crawl performance
  - Coverage statistics
  - Discovery trends
```

---

## 📋 Crawl Targets

See `crawler-config.yaml` for complete target definitions:

- **File Structure:** Components, services, controllers, tests, config, assets
- **Code Relationships:** Dependencies, co-modification, composition
- **Test Patterns:** Frameworks, test data, selectors, visual regression tools

---

## 🚫 Exclusions

Automatically skips (see `crawler-config.yaml`):
- Dependencies: `node_modules`, `bin`, `obj`, `.venv`
- Generated: `dist`, `build`, minified files
- Version control: `.git`, lock files

---

## 🔧 Advanced Usage

### Custom Crawl Targets
```bash
# Crawl specific directory
python src/operations/brain_crawler.py --target="src/components"

# Crawl with pattern filter
python src/operations/brain_crawler.py --pattern="**/*.razor"
```

### Force Recrawl
```bash
# Ignore cache, start fresh
python src/operations/brain_crawler.py --force --mode=full
```

### Dry Run
```bash
# Preview what would be crawled (no BRAIN updates)
python src/operations/brain_crawler.py --dry-run
```

---

## 📈 Example Output

```yaml
# file-relationships.yaml (excerpt)
HostControlPanel.razor:
  imports:
    - Services/ShareButtonInjectionService.cs
    - wwwroot/css/noor-canvas.css
  co_modified_with:
    - path: wwwroot/css/noor-canvas.css
      frequency: 0.75
  child_components:
    - Components/Canvas/TranscriptCanvas.razor
  apis_called:
    - POST /api/sessions/save
    - GET /api/users/current
```

---

## 🎓 Integration with CORTEX

**When Crawler Runs:**
1. Discovers codebase structure
2. Analyzes relationships
3. Feeds BRAIN tiers (1→2→3)
4. Updates knowledge graph
5. Returns metrics

**CORTEX Then Uses:**
- File suggestions ("You modified X, might need to update Y")
- Test recommendations ("This component needs Playwright test")
- Architectural insights ("Services follow DI pattern")
- Context-aware planning ("Similar pattern in AuthService")

---

**Version:** 1.1 - YAML-based config, 75% token reduction  
**Configuration:** See `cortex-brain/agents/crawler-config.yaml` for full details  
**Last Updated:** 2025-11-16
