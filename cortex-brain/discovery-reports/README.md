# Discovery Reports Directory

This directory contains CORTEX Discovery Reports - comprehensive intelligence reports showcasing what CORTEX has learned about your project.

## What Are Discovery Reports?

Discovery Reports are automatically generated markdown documents that demonstrate CORTEX's deep understanding of your project by analyzing:

- **File Structure** - Languages, frameworks, architecture patterns
- **Git History** - Commits, branches, development activity
- **Test Coverage** - Test count, coverage percentage, quality metrics
- **Documentation** - Docs, README quality, help systems
- **CORTEX Brain** - Tier 1/2/3 state, memory, knowledge
- **Plugin Ecosystem** - Active plugins, capabilities
- **Health Assessment** - Overall score, risks, recommendations

## When Are They Generated?

Reports are generated:
- After running `demo` operation
- After running `setup` operation (optional)
- On-demand via `discovery report` command
- Automatically in background (future feature)

## Report Naming

Reports are saved with timestamp filenames:
```
discovery-2025-11-10-143523.md
discovery-2025-11-10-091234.md
```

The `latest.md` file always points to the most recent report.

## Usage

View the latest report:
```bash
cat cortex-brain/discovery-reports/latest.md
```

Or open in your editor/browser for best formatting.

## Report Refresh

Discovery reports can be refreshed anytime:
```
discovery report
refresh discovery
```

This will re-scan your project and generate a new report with updated information.

---

*Generated reports are stored locally and never uploaded to any external service.*
