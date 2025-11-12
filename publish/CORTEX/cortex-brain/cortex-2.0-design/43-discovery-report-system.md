# Design Document: Discovery Report System

**Document ID:** 43  
**Feature:** Post-Setup Discovery Report  
**Status:** 🎯 PLANNED  
**Priority:** HIGH  
**Target:** CORTEX 2.1  
**Created:** 2025-11-10  
**Author:** Asif Hussain

---

## 📋 Executive Summary

The **Discovery Report System** generates a comprehensive markdown report after setup/demo that showcases CORTEX's deep understanding of the user's project. Instead of showing what CORTEX *can* do theoretically, it demonstrates what CORTEX *has already learned* about the specific project in real-time.

**Key Innovation:** Transforms demo from generic capability showcase into personalized project intelligence report.

---

## 🎯 Problem Statement

### Current State
- Demo shows generic examples ("add a button")
- User must imagine how CORTEX applies to their project
- Intelligence capabilities not immediately visible
- Setup runs but doesn't show what it discovered

### Desired State
- Demo generates personalized report for user's actual project
- Immediate proof of CORTEX intelligence
- Actionable insights and recommendations
- Visual demonstration of memory, learning, and context awareness

---

## 🏗️ Architecture Overview

### Component Structure

```
src/operations/
├── demo_discovery.py          # Main orchestrator
└── crawlers/
    ├── __init__.py
    ├── base_crawler.py        # Abstract base class
    ├── file_scanner.py        # File structure analysis
    ├── git_analyzer.py        # Git history & metrics
    ├── test_parser.py         # Test coverage analysis
    ├── doc_mapper.py          # Documentation discovery
    ├── brain_inspector.py     # Tier 1/2/3 analysis
    ├── plugin_registry.py     # Plugin ecosystem scan
    └── health_assessor.py     # Project health scoring
```

### Data Flow

```
User runs "demo" or "setup"
    ↓
Discovery Orchestrator starts
    ↓
Parallel Crawler Execution:
    ├── File Scanner    → Project structure
    ├── Git Analyzer    → Development history
    ├── Test Parser     → Quality metrics
    ├── Doc Mapper      → Documentation map
    ├── Brain Inspector → Memory/learning state
    ├── Plugin Registry → Capability inventory
    └── Health Assessor → Risk/opportunity analysis
    ↓
Data Aggregation & Scoring
    ↓
Markdown Report Generation
    ↓
Save to: cortex-brain/discovery-reports/YYYY-MM-DD-HHmmss.md
    ↓
Display summary + file path to user
```

---

## 🔍 Crawler Specifications

### 1. File Scanner Crawler

**Purpose:** Analyze project file structure and technology stack

**Discovers:**
- Total files, directories, lines of code
- Programming languages detected (extensions)
- Framework indicators (package.json, requirements.txt, etc.)
- Configuration files (pytest.ini, mkdocs.yml, etc.)
- Project size metrics

**Output Format:**
```python
{
    "total_files": 847,
    "total_directories": 92,
    "total_lines": 45230,
    "languages": {
        "python": {"files": 234, "lines": 38420},
        "markdown": {"files": 87, "lines": 5210},
        "yaml": {"files": 23, "lines": 1600}
    },
    "frameworks": ["Flask", "pytest", "MkDocs"],
    "architecture_pattern": "plugin-based"
}
```

**Implementation:** Uses `pathlib` and file pattern matching

---

### 2. Git Analyzer Crawler

**Purpose:** Extract development history and activity patterns

**Discovers:**
- Total commits, branches, contributors
- Recent activity (last 7/30/90 days)
- Commit frequency patterns
- Active development areas (most changed files)
- Branch health (merged vs stale)

**Output Format:**
```python
{
    "total_commits": 1247,
    "branches": {"total": 8, "active": 3, "stale": 2},
    "contributors": 2,
    "recent_activity": {
        "last_7_days": 47,
        "last_30_days": 183
    },
    "hot_files": [
        {"path": "src/operations/demo.py", "commits": 23},
        {"path": "prompts/user/cortex.md", "commits": 19}
    ]
}
```

**Implementation:** Uses `subprocess` to call `git` commands

---

### 3. Test Parser Crawler

**Purpose:** Analyze test coverage and quality metrics

**Discovers:**
- Total tests (unit, integration, e2e)
- Test pass/fail rates
- Coverage percentage (if pytest-cov available)
- Test file locations
- Untested modules

**Output Format:**
```python
{
    "total_tests": 82,
    "passing": 82,
    "failing": 0,
    "coverage": 85.2,
    "test_files": 24,
    "untested_modules": ["src/operations/cleanup.py"],
    "test_types": {
        "unit": 67,
        "integration": 12,
        "e2e": 3
    }
}
```

**Implementation:** Parses pytest output and `pytest --co` (collect-only)

---

### 4. Documentation Mapper Crawler

**Purpose:** Map documentation structure and completeness

**Discovers:**
- Total documentation files
- Documentation types (user guides, API docs, design docs)
- Documentation coverage (documented vs undocumented modules)
- README quality score
- Help system availability

**Output Format:**
```python
{
    "total_docs": 87,
    "user_guides": 6,
    "api_docs": 12,
    "design_docs": 142,
    "readme_quality": 9.2,
    "documented_modules": 34,
    "undocumented_modules": 8,
    "help_system": "response-templates (43 patterns)"
}
```

**Implementation:** File scanning + content analysis

---

### 5. Brain Inspector Crawler

**Purpose:** Analyze CORTEX brain state and learning

**Discovers:**
- Tier 1: Conversation count, memory retention
- Tier 2: Knowledge patterns, learned behaviors
- Tier 3: Development context metrics
- Brain health score
- Protection rules active

**Output Format:**
```python
{
    "tier1": {
        "conversations": 20,
        "oldest": "2025-10-15",
        "newest": "2025-11-10",
        "retention_rate": 100
    },
    "tier2": {
        "knowledge_patterns": 47,
        "capabilities": 34,
        "architectural_patterns": 12,
        "lessons_learned": 28
    },
    "tier3": {
        "git_commits_tracked": 1247,
        "test_coverage": 85.2,
        "file_relationships": 123
    },
    "protection_rules": 4,
    "brain_health": 9.1
}
```

**Implementation:** Direct database/YAML queries

---

### 6. Plugin Registry Crawler

**Purpose:** Inventory CORTEX plugin ecosystem

**Discovers:**
- Registered plugins (active, inactive)
- Natural language patterns registered
- Command registry entries
- Plugin health (initialization success)
- Extensibility points

**Output Format:**
```python
{
    "total_plugins": 8,
    "active_plugins": 8,
    "inactive_plugins": 0,
    "natural_language_patterns": 47,
    "commands_registered": 12,
    "initialization_success_rate": 100,
    "plugin_list": [
        {"name": "Platform Switch", "status": "active", "commands": 1},
        {"name": "Doc Refresh", "status": "active", "commands": 1}
    ]
}
```

**Implementation:** Queries plugin registry + command registry

---

### 7. Health Assessor Crawler

**Purpose:** Evaluate project health and provide recommendations

**Discovers:**
- Overall health score (0-10)
- Risk factors (low test coverage, stale branches, etc.)
- Opportunities (areas for improvement)
- Strengths (what's working well)
- Actionable recommendations

**Output Format:**
```python
{
    "health_score": 8.7,
    "grade": "A-",
    "risks": [
        {"type": "untested_module", "severity": "medium", "item": "cleanup.py"}
    ],
    "opportunities": [
        {"type": "documentation", "impact": "low", "suggestion": "Add API docs for Tier 3"}
    ],
    "strengths": [
        "97% token optimization achieved",
        "100% plugin initialization success",
        "Strong test coverage (85%)"
    ],
    "recommendations": [
        "Add tests for cleanup operation",
        "Consider branch cleanup (2 stale branches)"
    ]
}
```

**Implementation:** Heuristic scoring based on crawler data

---

## 📊 Report Format Specification

### Markdown Template Structure

```markdown
# CORTEX Discovery Report

**Generated:** {timestamp}  
**Project:** {project_name}  
**Platform:** {platform} ({os_version})  
**Health Score:** {health_score}/10 ({grade})

---

## 🎯 Intelligence Summary

{high_level_overview_with_visual_bars}

---

## 📁 Project Structure

**Technology Stack:**
- {language_1}: {file_count} files, {line_count} lines
- {language_2}: {file_count} files, {line_count} lines

**Frameworks Detected:**
- {framework_1}
- {framework_2}

**Architecture Pattern:** {pattern}

**Project Size:** {size_category} ({total_files} files, {total_lines} lines)

---

## 🧠 CORTEX Brain Analysis

### Tier 1: Working Memory
- **Conversations Stored:** {count} (last 20 sessions)
- **Memory Retention:** {retention_rate}%
- **Date Range:** {oldest} to {newest}

### Tier 2: Knowledge Graph
- **Patterns Learned:** {pattern_count}
- **Capabilities Documented:** {capability_count}
- **Lessons Accumulated:** {lesson_count}

### Tier 3: Development Context
- **Git Commits Tracked:** {commit_count}
- **Test Coverage:** {coverage}%
- **File Relationships:** {relationship_count}

**Brain Health:** {brain_health}/10 ✅

---

## 🔍 Deep Scan Results

### Git Activity
- **Total Commits:** {commit_count}
- **Active Branches:** {active_branches}
- **Recent Activity:** {last_7_days} commits (7 days), {last_30_days} commits (30 days)
- **Hot Files:** {top_5_most_changed}

### Test Coverage
- **Total Tests:** {test_count} ({passing} passing, {failing} failing)
- **Coverage:** {coverage_percent}%
- **Test Types:** {unit} unit, {integration} integration, {e2e} E2E
- **Untested Modules:** {untested_list}

### Documentation
- **Total Docs:** {doc_count}
- **Documentation Coverage:** {doc_coverage}%
- **Help System:** {help_system_type}
- **README Quality:** {readme_score}/10

---

## 🔌 Plugin Ecosystem

**Registered Plugins:** {plugin_count}
- {plugin_1_name} ({status})
- {plugin_2_name} ({status})
- ...

**Natural Language Patterns:** {pattern_count}
**Command Registry:** {command_count} commands available
**Initialization Success:** {init_success_rate}%

---

## 💡 Capabilities Discovered

CORTEX can help you with:

1. **{capability_1}** - {description}
2. **{capability_2}** - {description}
3. **{capability_3}** - {description}
...

---

## 🚀 Quick Start Commands

Based on your project, try these:

```
{suggested_command_1}
```
{explanation}

```
{suggested_command_2}
```
{explanation}

---

## 📈 Health Assessment

**Overall Score:** {health_score}/10 ({grade})

### ✅ Strengths
- {strength_1}
- {strength_2}
- {strength_3}

### ⚠️ Risks
- {risk_1} ({severity})
- {risk_2} ({severity})

### 💡 Opportunities
- {opportunity_1}
- {opportunity_2}

### 🎯 Recommendations
1. {recommendation_1}
2. {recommendation_2}
3. {recommendation_3}

---

## 📊 Token Optimization

**Before Modularization:** {old_tokens} tokens
**After Modularization:** {new_tokens} tokens
**Reduction:** {reduction_percent}%
**Annual Cost Savings:** ${cost_savings}

---

## 🎓 Next Steps

1. **Try a command:** Start with `{suggested_first_command}`
2. **Enable tracking:** See [Tracking Guide](#) for conversation memory
3. **Explore capabilities:** Ask "what can you help me with?"
4. **Review recommendations:** Address {high_priority_count} high-priority items

---

*Report saved to: `{report_path}`*
*Want a fresh scan? Just say "refresh discovery report"*
```

---

## 🎨 Visual Elements

### Progress Bars (Text-Based)

```
Test Coverage:  ████████████████░░░░  85%
Documentation:  ██████████████████░░  90%
Git Activity:   ███████████████████░  95%
Brain Health:   ████████████████████ 100%
```

### Health Score Badge

```
┌─────────────────┐
│  HEALTH SCORE   │
│    8.7 / 10     │
│      A−         │
└─────────────────┘
```

### Technology Stack Icon List

```
🐍 Python 3.11
🌶️ Flask 2.3
🧪 pytest 7.4
📚 MkDocs 1.5
```

---

## ⚙️ Implementation Plan

### Phase 1: Core Infrastructure (Day 1)

**Tasks:**
1. Create base crawler class (`src/operations/crawlers/base_crawler.py`)
2. Implement orchestrator (`src/operations/demo_discovery.py`)
3. Set up report template engine
4. Create discovery reports directory

**Deliverables:**
- Basic framework for adding crawlers
- Report generation pipeline
- Test harness for crawlers

---

### Phase 2: Essential Crawlers (Day 1-2)

**Priority Order:**
1. File Scanner (easiest, high value)
2. Brain Inspector (CORTEX-specific intelligence)
3. Plugin Registry (showcases extensibility)
4. Health Assessor (provides recommendations)

**Why this order:** Shows immediate value with minimal dependencies

---

### Phase 3: Advanced Crawlers (Day 2)

**Tasks:**
1. Git Analyzer (requires subprocess handling)
2. Test Parser (requires pytest integration)
3. Doc Mapper (requires content analysis)

**Challenges:**
- Git may not be available (handle gracefully)
- Test coverage requires pytest-cov
- Documentation quality scoring heuristics

---

### Phase 4: Integration (Day 2-3)

**Tasks:**
1. Integrate with demo operation
2. Add to setup workflow (optional flag)
3. Create refresh mechanism
4. Add caching for performance

**Integration Points:**
```python
# In src/operations/demo.py
from src.operations.demo_discovery import generate_discovery_report

def execute_demo(request: str, context: dict) -> dict:
    # ... existing demo logic ...
    
    # Generate discovery report
    report_path = generate_discovery_report()
    
    return {
        "success": True,
        "report_path": report_path,
        "summary": "Discovery complete!"
    }
```

---

### Phase 5: Testing & Polish (Day 3)

**Tasks:**
1. Unit tests for each crawler
2. Integration tests for orchestrator
3. Performance optimization (parallel execution)
4. Error handling for missing data
5. User documentation

**Test Coverage Target:** 80%+

---

## 🔧 Technical Specifications

### Base Crawler Interface

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseCrawler(ABC):
    """Abstract base class for all discovery crawlers"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
    
    @abstractmethod
    def crawl(self) -> Dict[str, Any]:
        """Execute crawler and return discovery data"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Return crawler name for logging"""
        pass
    
    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """Standard error handling"""
        return {
            "error": str(error),
            "crawler": self.get_name(),
            "status": "failed"
        }
```

---

### Orchestrator Interface

```python
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor

class DiscoveryOrchestrator:
    """Coordinates all crawlers and generates report"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.crawlers = self._initialize_crawlers()
    
    def _initialize_crawlers(self) -> List[BaseCrawler]:
        """Load all crawler instances"""
        return [
            FileScanner(self.project_root),
            BrainInspector(self.project_root),
            PluginRegistry(self.project_root),
            HealthAssessor(self.project_root),
            GitAnalyzer(self.project_root),
            TestParser(self.project_root),
            DocMapper(self.project_root),
        ]
    
    def execute(self) -> Dict[str, Any]:
        """Run all crawlers in parallel"""
        results = {}
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(crawler.crawl): crawler.get_name()
                for crawler in self.crawlers
            }
            
            for future in futures:
                name = futures[future]
                try:
                    results[name] = future.result(timeout=30)
                except Exception as e:
                    results[name] = {"error": str(e)}
        
        return results
    
    def generate_report(self, data: Dict[str, Any]) -> str:
        """Generate markdown report from crawler data"""
        # Template rendering logic
        pass
```

---

### Report Generation

```python
from jinja2 import Template
from datetime import datetime

class ReportGenerator:
    """Generates markdown reports from crawler data"""
    
    def __init__(self, template_path: str):
        with open(template_path) as f:
            self.template = Template(f.read())
    
    def generate(self, data: Dict[str, Any]) -> str:
        """Render report from data"""
        context = {
            "timestamp": datetime.now().isoformat(),
            "project_name": data.get("project_name", "Unknown"),
            **data
        }
        
        return self.template.render(context)
    
    def save(self, content: str, output_path: str) -> str:
        """Save report to file"""
        with open(output_path, 'w') as f:
            f.write(content)
        return output_path
```

---

## 📁 File Organization

```
src/operations/
├── demo_discovery.py                 # Main entry point
├── crawlers/
│   ├── __init__.py
│   ├── base_crawler.py              # Abstract base class
│   ├── file_scanner.py              # 150 lines
│   ├── git_analyzer.py              # 200 lines
│   ├── test_parser.py               # 180 lines
│   ├── doc_mapper.py                # 160 lines
│   ├── brain_inspector.py           # 220 lines
│   ├── plugin_registry.py           # 140 lines
│   └── health_assessor.py           # 190 lines
└── templates/
    └── discovery_report.md.j2        # Jinja2 template

tests/operations/
├── test_demo_discovery.py
└── crawlers/
    ├── test_file_scanner.py
    ├── test_git_analyzer.py
    ├── test_test_parser.py
    ├── test_doc_mapper.py
    ├── test_brain_inspector.py
    ├── test_plugin_registry.py
    └── test_health_assessor.py

cortex-brain/
└── discovery-reports/                # Generated reports
    ├── 2025-11-10-143215.md
    ├── 2025-11-09-092347.md
    └── latest.md                     # Symlink to most recent
```

---

## 🎯 Success Metrics

### Quantitative
- **Report Generation Time:** < 5 seconds
- **Crawler Success Rate:** > 95%
- **Report Accuracy:** > 90% (verified against manual inspection)
- **Test Coverage:** > 80%

### Qualitative
- **User Reaction:** "Wow, it already knows my project!"
- **Actionable Insights:** Users act on 3+ recommendations
- **Demo Impact:** Increased perceived value of CORTEX
- **Adoption:** 70%+ of users run discovery after setup

---

## 🚨 Risk Mitigation

### Risk 1: Missing Dependencies
**Scenario:** Git not installed, pytest not available
**Mitigation:** Graceful degradation - skip crawler, note in report

### Risk 2: Large Projects
**Scenario:** 10,000+ files causes slow scan
**Mitigation:** Sampling strategy, configurable depth limits

### Risk 3: Incorrect Analysis
**Scenario:** False positives in technology detection
**Mitigation:** Conservative heuristics, manual override option

### Risk 4: Sensitive Data
**Scenario:** Report includes private information
**Mitigation:** Data sanitization, local-only storage, no cloud upload

---

## 🔄 Future Enhancements (CORTEX 2.2+)

### Phase 2 Features
1. **Interactive Report:** Click recommendations to execute fixes
2. **Trend Analysis:** Compare reports over time
3. **Team Dashboards:** Aggregate data across team members
4. **CI/CD Integration:** Auto-generate on merge to main
5. **Custom Crawlers:** Plugin API for user-defined crawlers

### Phase 3 Features
6. **AI Insights:** Use LLM to analyze patterns and suggest improvements
7. **Benchmark Comparisons:** Compare against industry standards
8. **Visual Graphs:** Generate charts for metrics over time
9. **Export Formats:** JSON, HTML, PDF options
10. **Scheduled Scans:** Daily/weekly automated reports

---

## 📚 Documentation Requirements

### User Documentation
- **Quick Start Guide:** How to generate first discovery report
- **Interpretation Guide:** Understanding report sections
- **Action Guide:** How to act on recommendations
- **Troubleshooting:** Common issues and solutions

### Developer Documentation
- **Crawler Development Guide:** How to add new crawlers
- **API Reference:** BaseCrawler interface documentation
- **Testing Guide:** How to test crawlers
- **Template Customization:** How to modify report format

---

## ✅ Acceptance Criteria

### Must Have (MVP)
- [ ] Generate basic discovery report with 4+ crawlers
- [ ] Report includes: file structure, brain state, plugins, health score
- [ ] Report saves to `cortex-brain/discovery-reports/`
- [ ] Integration with demo operation
- [ ] Error handling for missing data
- [ ] Basic test coverage (60%+)

### Should Have (v1.1)
- [ ] All 7 crawlers implemented
- [ ] Parallel execution for performance
- [ ] Visual progress bars in report
- [ ] Actionable recommendations section
- [ ] Test coverage 80%+
- [ ] User documentation complete

### Nice to Have (v1.2)
- [ ] Interactive report links
- [ ] Trend analysis (compare reports)
- [ ] Custom crawler plugin API
- [ ] Export to JSON/HTML
- [ ] Scheduled auto-reports

---

## 🎓 Learning Objectives

This feature demonstrates:
1. **System-wide context awareness:** CORTEX understands entire project
2. **Multi-source data integration:** Combines git, tests, docs, brain
3. **Intelligent analysis:** Not just data collection, but insight generation
4. **Personalization:** Report is specific to user's project
5. **Actionable intelligence:** Provides next steps, not just information

---

## 📅 Timeline Summary

**Total Effort:** 2-3 days (16-24 hours)

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Phase 1: Infrastructure | 4 hours | Base crawler, orchestrator, template |
| Phase 2: Essential Crawlers | 6 hours | File, brain, plugin, health |
| Phase 3: Advanced Crawlers | 6 hours | Git, test, doc |
| Phase 4: Integration | 4 hours | Demo/setup integration, caching |
| Phase 5: Testing & Polish | 4 hours | Tests, docs, error handling |

**Target Completion:** End of Week 1, CORTEX 2.1

---

## 🔗 Related Documents

- `#file:cortex-brain/cortex-2.0-design/42-interactive-demo-system.md` - Demo operation architecture
- `#file:cortex-brain/cortex-2.0-design/02-plugin-system.md` - Plugin registry architecture
- `#file:cortex-brain/cortex-2.0-design/06-documentation-system.md` - Documentation structure
- `#file:cortex-brain/cortex-2.0-design/13-testing-strategy.md` - Testing approach

---

## 💭 Open Questions

1. **Should discovery report be generated automatically on first setup?**
   - Pro: Immediate value demonstration
   - Con: Adds setup time

2. **How often should reports be refreshed?**
   - Options: Manual, daily, weekly, on-demand
   - Recommendation: Manual + "refresh discovery" command

3. **Should we cache crawler results?**
   - Pro: Faster subsequent reports
   - Con: Staleness risk
   - Recommendation: Cache with 1-hour TTL

4. **Privacy considerations for sharing reports?**
   - Recommendation: Add "--sanitize" flag to remove sensitive data

---

## 🎉 Expected Impact

### For Users
- **Immediate Proof:** CORTEX intelligence is visible within seconds
- **Actionable Insights:** Clear next steps to improve project
- **Confidence:** Trust that CORTEX understands their codebase
- **Engagement:** Higher likelihood of continued use

### For CORTEX Project
- **Differentiation:** No other AI assistant does this
- **Adoption:** Stronger first impression drives retention
- **Feedback Loop:** Reports reveal areas for CORTEX improvement
- **Showcase:** Perfect demo for stakeholders/investors

---

**Status:** Ready for implementation  
**Next Step:** Begin Phase 1 (infrastructure setup)  
**Estimated Completion:** 2025-11-13 (3 days from now)

---

*This design document will be updated as implementation progresses.*
