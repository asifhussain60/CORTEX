# ADO Orchestrator Migration Plan
## CORTEX 3.0 → 4.0 Consolidation

**Target:** Consolidate ADO operations into unified `ADOOrchestrator` extending `PlanningOrchestrator`

**Version:** 1.0.0 | **Author:** Asif Hussain | **Date:** December 14, 2025

---

## 📋 Executive Summary

### Current State (CORTEX 3.0)
ADO operations scattered across multiple files with no unified orchestrator:

1. **ADO Utility** (`src/operations/ado.py`)
   - 449 lines of code
   - CLI for ADO work item management
   - Commands: create, load, update, summary, validate-dor, validate-dod, list
   - Direct utility functions, no orchestration

2. **ADO Agent** (`src/cortex_agents/ado_agent.py`)
   - 317 lines of code
   - Routes ADO intents to unified entry point
   - Handles: story, feature, summary, work item, code review

3. **Unified Entry Point** (`src/operations/modules/routing/unified_entry_point_utility.py`)
   - 1,301 lines (partial ADO code)
   - Functions: `execute_ado_story()`, `execute_ado_feature()`, `generate_work_summary()`
   - Scattered throughout monolithic orchestrator

4. **ADO Planning Demo** (`src/operations/modules/demo/ado_planning_demo.py`)
   - Demo/example code
   - Story/feature generation examples

**Total:** ~500 LOC of ADO-specific logic scattered across 4 files

### Target State (CORTEX 4.0)
Single unified `ADOOrchestrator` with:

- **Inherits from PlanningOrchestrator**: Reuses planning logic (complexity, phases, DoR/DoD)
- **ADO-specific formatting**: Azure DevOps markdown templates
- **Three work item types**: Story, Feature, Task (unified generation)
- **MCP integration**: All operations exposed as MCP tools
- **Event-driven**: Emits ADO-specific events
- **Completion summaries**: Auto-generate work completion summaries

**Target:** 600 LOC in `cortex_orchestrators/ado/`

---

## 🎯 Consolidation Strategy

### Architecture Changes

**Before (CORTEX 3.0):**
```
User Request "plan ado story"
    ↓
[Keyword Router]
    ↓
ADOAgent
    ↓
UnifiedEntryPointOrchestrator.execute_ado_story()
    ↓
(No orchestrator, direct utility calls)
```

**After (CORTEX 4.0):**
```
User Request "plan ado story"
    ↓
[LLM Intent Router]
    ↓
ADOOrchestrator (extends PlanningOrchestrator)
    ↓
    ├── Inherited: Complexity analysis, DoR/DoD, phase decomposition
    └── ADO-specific: Work item formatting, ADO templates, completion summaries
```

### Inheritance Strategy

ADOOrchestrator **extends** PlanningOrchestrator and adds:

1. **ADO Formatting Layer**
   - Markdown templates for Azure DevOps
   - Work item type selection (Story/Feature/Task)
   - Acceptance criteria formatting
   - ADO-specific sections (Business Value, Technical Approach)

2. **Completion Summary Generation**
   - Auto-generate summary from completed work
   - Files changed tracking
   - Test coverage metrics
   - Decision log

3. **Work Item Management**
   - Create work items via ADO REST API
   - Load existing work items
   - Update work item status
   - Link work items to code changes

### Component Mapping

| **CORTEX 3.0 Component** | **CORTEX 4.0 Location** | **Changes** |
|---------------------------|-------------------------|-------------|
| `src/operations/ado.py` (CLI) | `cortex_orchestrators/ado/cli.py` | Preserved for backward compatibility |
| `ADOAgent` | `cortex_agents/ado_agent.py` | Routes to `ADOOrchestrator` |
| `execute_ado_story()` | `ADOOrchestrator.generate_story()` | Extract from unified entry point |
| `execute_ado_feature()` | `ADOOrchestrator.generate_feature()` | Extract from unified entry point |
| `generate_work_summary()` | `ADOOrchestrator.generate_summary()` | Extract from unified entry point |
| ADO templates | `cortex_orchestrators/ado/templates/` | New template system |

---

## 🗓️ Migration Timeline

### Day 1: Foundation & Template System (8 hours)

**Goal:** Create directory structure, define ADO data models, create template system

**Tasks:**

1. **Create directory structure** (1 hour)
   ```
   cortex_orchestrators/
   └── ado/
       ├── __init__.py
       ├── orchestrator.py           # Main ADO orchestrator
       ├── cli.py                     # CLI wrapper (backward compat)
       ├── formatters.py              # ADO markdown formatters
       ├── templates/
       │   ├── __init__.py
       │   ├── story_template.py      # Story formatting
       │   ├── feature_template.py    # Feature formatting
       │   └── task_template.py       # Task formatting
       ├── models/
       │   ├── __init__.py
       │   ├── work_item.py           # WorkItem data classes
       │   └── summary.py             # Completion summary models
       └── tests/
           ├── __init__.py
           ├── test_orchestrator.py
           ├── test_formatters.py
           └── test_templates.py
   ```

2. **Define ADO data models** (2 hours)
   
   **File:** `cortex_orchestrators/ado/models/work_item.py`
   ```python
   from dataclasses import dataclass, field
   from datetime import datetime
   from typing import List, Dict, Any, Optional
   from enum import Enum
   
   class WorkItemType(Enum):
       STORY = "User Story"
       FEATURE = "Feature"
       TASK = "Task"
       BUG = "Bug"
       EPIC = "Epic"
   
   class WorkItemStatus(Enum):
       NEW = "New"
       ACTIVE = "Active"
       RESOLVED = "Resolved"
       CLOSED = "Closed"
       BLOCKED = "Blocked"
   
   @dataclass
   class WorkItem:
       """ADO work item representation."""
       work_item_id: Optional[str]
       work_item_type: WorkItemType
       title: str
       description: str
       acceptance_criteria: List[str]
       priority: int = 2  # 1=Critical, 2=High, 3=Medium, 4=Low
       status: WorkItemStatus = WorkItemStatus.NEW
       assigned_to: Optional[str] = None
       iteration: Optional[str] = None
       tags: List[str] = field(default_factory=list)
       created_date: Optional[datetime] = None
       updated_date: Optional[datetime] = None
       metadata: Dict[str, Any] = field(default_factory=dict)
   
   @dataclass
   class CompletionSummary:
       """Work completion summary for ADO."""
       work_item_id: str
       title: str
       files_created: List[str] = field(default_factory=list)
       files_modified: List[str] = field(default_factory=list)
       tests_created: List[str] = field(default_factory=list)
       test_coverage: float = 0.0
       decisions_made: List[str] = field(default_factory=list)
       acceptance_criteria_met: List[str] = field(default_factory=list)
       duration_hours: float = 0.0
       created_at: datetime = field(default_factory=datetime.now)
   ```

3. **Create ADO template system** (3 hours)
   
   **File:** `cortex_orchestrators/ado/templates/story_template.py`
   ```python
   from typing import Dict, Any
   from ..models.work_item import WorkItem, WorkItemType
   from cortex_orchestrators.planning.models.plan import FeaturePlan
   
   class StoryTemplate:
       """Azure DevOps User Story template."""
       
       @staticmethod
       def format(work_item: WorkItem, plan: FeaturePlan) -> str:
           """
           Format work item as ADO User Story markdown.
           
           Sections:
           - Title
           - Description
           - Business Value
           - Acceptance Criteria
           - Technical Approach
           - Implementation Phases
           - Definition of Ready
           - Definition of Done
           """
           
           # Header
           markdown = f"# 📋 {work_item.title}\n\n"
           markdown += f"**Type:** {work_item.work_item_type.value}  \n"
           markdown += f"**Priority:** {work_item.priority}  \n"
           markdown += f"**Complexity:** {plan.complexity.value}  \n"
           markdown += f"**Estimated:** {plan.estimated_total_days} days  \n"
           markdown += "\n---\n\n"
           
           # Description
           markdown += "## 📝 Description\n\n"
           markdown += f"{work_item.description}\n\n"
           
           # Business Value
           markdown += "## 💼 Business Value\n\n"
           business_value = work_item.metadata.get(
               "business_value",
               "Delivers requested functionality to users."
           )
           markdown += f"{business_value}\n\n"
           
           # Acceptance Criteria
           markdown += "## ✅ Acceptance Criteria\n\n"
           for idx, criterion in enumerate(work_item.acceptance_criteria, 1):
               markdown += f"{idx}. {criterion}\n"
           markdown += "\n"
           
           # Technical Approach
           markdown += "## 🔧 Technical Approach\n\n"
           for phase in plan.phases:
               markdown += f"### Phase {phase.phase_number}: {phase.name}\n\n"
               markdown += f"{phase.description}\n\n"
               markdown += "**Deliverables:**\n"
               for deliverable in phase.deliverables:
                   markdown += f"- {deliverable}\n"
               markdown += "\n"
           
           # Implementation Phases (summary)
           markdown += "## 📅 Implementation Phases\n\n"
           markdown += "| Phase | Name | Duration | Key Deliverables |\n"
           markdown += "|-------|------|----------|------------------|\n"
           for phase in plan.phases:
               deliverables_str = ", ".join(phase.deliverables[:2])
               if len(phase.deliverables) > 2:
                   deliverables_str += "..."
               markdown += f"| {phase.phase_number} | {phase.name} | "
               markdown += f"{phase.estimated_days}d | {deliverables_str} |\n"
           markdown += "\n"
           
           # Definition of Ready
           markdown += "## 🎯 Definition of Ready\n\n"
           markdown += "- [x] Requirements clear and documented\n"
           markdown += "- [x] Acceptance criteria defined\n"
           markdown += "- [x] Dependencies identified\n"
           markdown += "- [x] Technical approach approved\n"
           markdown += "- [x] Estimation complete\n\n"
           
           # Definition of Done
           markdown += "## ✅ Definition of Done\n\n"
           markdown += "- [ ] All acceptance criteria met\n"
           markdown += "- [ ] Unit tests passing (90% coverage)\n"
           markdown += "- [ ] Integration tests passing\n"
           markdown += "- [ ] Code review completed\n"
           markdown += "- [ ] Documentation updated\n"
           markdown += "- [ ] Deployed to staging\n"
           markdown += "- [ ] User acceptance testing complete\n\n"
           
           # Risks
           if plan.risks:
               markdown += "## ⚠️ Risks & Mitigation\n\n"
               markdown += "| Risk | Severity | Mitigation |\n"
               markdown += "|------|----------|------------|\n"
               for risk in plan.risks:
                   markdown += f"| {risk.description} | {risk.severity} | "
                   markdown += f"{risk.mitigation} |\n"
               markdown += "\n"
           
           # Tags
           if work_item.tags:
               markdown += f"**Tags:** {', '.join(work_item.tags)}\n\n"
           
           # Footer
           markdown += "---\n\n"
           markdown += f"*Generated by CORTEX 4.0 ADO Orchestrator*  \n"
           markdown += f"*Created: {work_item.created_date or 'N/A'}*\n"
           
           return markdown
   ```

4. **Create test scaffolding** (2 hours)
   
   **File:** `cortex_orchestrators/ado/tests/test_orchestrator.py`
   ```python
   import pytest
   from unittest.mock import Mock, AsyncMock
   from cortex_orchestrators.ado.orchestrator import ADOOrchestrator
   from cortex_orchestrators.ado.models.work_item import WorkItem, WorkItemType
   from cortex_orchestrators.planning.models.context import PlanningContext
   
   @pytest.fixture
   def mock_event_bus():
       return Mock()
   
   @pytest.fixture
   def mock_brain_engine():
       return Mock()
   
   @pytest.fixture
   def ado_orchestrator(mock_event_bus, mock_brain_engine):
       return ADOOrchestrator(
           event_bus=mock_event_bus,
           brain_engine=mock_brain_engine
       )
   
   @pytest.mark.asyncio
   async def test_generate_story(ado_orchestrator):
       """Test story generation with ADO formatting."""
       context = PlanningContext(
           feature_name="User Login",
           description="Implement OAuth 2.0 user authentication",
           acceptance_criteria=[
               "Users can log in with Google",
               "Users can log in with Microsoft",
               "Session persists for 24 hours"
           ]
       )
       
       work_item = await ado_orchestrator.generate_story(context)
       
       assert work_item.work_item_type == WorkItemType.STORY
       assert work_item.title == "User Login"
       assert len(work_item.acceptance_criteria) == 3
       assert "oauth" in work_item.description.lower()
   
   @pytest.mark.asyncio
   async def test_generate_completion_summary(ado_orchestrator):
       """Test completion summary generation."""
       work_item_id = "US-123"
       files = ["auth.py", "test_auth.py", "config.yaml"]
       
       summary = await ado_orchestrator.generate_completion_summary(
           work_item_id=work_item_id,
           files_created=files
       )
       
       assert summary.work_item_id == work_item_id
       assert len(summary.files_created) == 3
       assert "auth.py" in summary.files_created
   ```

**Deliverables (Day 1):**
- ✅ Directory structure created
- ✅ ADO data models defined (`WorkItem`, `CompletionSummary`)
- ✅ Story template implemented
- ✅ Test scaffolding ready

---

### Day 2: Core Orchestrator Implementation (8 hours)

**Goal:** Implement ADOOrchestrator extending PlanningOrchestrator

**Tasks:**

1. **Implement ADOOrchestrator** (6 hours)
   
   **File:** `cortex_orchestrators/ado/orchestrator.py`
   ```python
   from typing import Optional, Dict, Any, List
   import logging
   from pathlib import Path
   
   from cortex_core.event_bus import EventBus
   from cortex_core.brain_engine import BrainEngine
   from cortex_mcp.server import MCPServer
   
   from cortex_orchestrators.planning.orchestrator import PlanningOrchestrator
   from cortex_orchestrators.planning.models.context import PlanningContext
   from cortex_orchestrators.planning.models.plan import FeaturePlan
   
   from .models.work_item import WorkItem, WorkItemType, CompletionSummary
   from .templates.story_template import StoryTemplate
   from .templates.feature_template import FeatureTemplate
   from .templates.task_template import TaskTemplate
   
   logger = logging.getLogger(__name__)
   
   class ADOOrchestrator(PlanningOrchestrator):
       """
       ADO orchestrator extending PlanningOrchestrator.
       
       Inherits:
       - Complexity analysis
       - DoR/DoD validation
       - Phase decomposition
       - Planning strategies (Skeleton/Incremental/Full)
       
       Adds:
       - ADO-specific formatting (Story/Feature/Task templates)
       - Work item management (create, load, update)
       - Completion summary generation
       - ADO REST API integration
       """
       
       def __init__(
           self,
           event_bus: EventBus,
           brain_engine: BrainEngine,
           mcp_server: Optional[MCPServer] = None,
           ado_api_client: Optional[Any] = None
       ):
           super().__init__(event_bus, brain_engine, mcp_server)
           
           self.ado_api_client = ado_api_client
           
           # Template mapping
           self.templates = {
               WorkItemType.STORY: StoryTemplate(),
               WorkItemType.FEATURE: FeatureTemplate(),
               WorkItemType.TASK: TaskTemplate()
           }
           
           # Register ADO-specific MCP tools
           if self.mcp_server:
               self._register_ado_mcp_tools()
           
           logger.info("🎭 ADOOrchestrator initialized (extends PlanningOrchestrator)")
           logger.info("   ✅ 3 templates loaded (Story, Feature, Task)")
       
       async def generate_story(self, context: PlanningContext) -> WorkItem:
           """
           Generate ADO User Story with planning.
           
           Workflow:
           1. Generate feature plan (inherited from PlanningOrchestrator)
           2. Create WorkItem model
           3. Format as ADO Story markdown
           4. Store in brain
           5. Optionally create in ADO via API
           """
           logger.info(f"📋 Generating ADO Story: {context.feature_name}")
           
           # Emit ADO-specific event
           self.event_bus.emit("ado.story_generation_started", {
               "feature_name": context.feature_name
           })
           
           # Step 1: Generate plan (inherited)
           plan = await self.generate_plan(context)
           
           # Step 2: Create WorkItem
           work_item = WorkItem(
               work_item_id=None,  # Will be set after ADO API call
               work_item_type=WorkItemType.STORY,
               title=context.feature_name,
               description=context.description,
               acceptance_criteria=context.acceptance_criteria,
               priority=context.metadata.get("priority", 2),
               tags=self._extract_tags(context, plan)
           )
           
           # Step 3: Format as ADO markdown
           template = self.templates[WorkItemType.STORY]
           ado_markdown = template.format(work_item, plan)
           
           # Step 4: Store in brain
           work_item.metadata["plan_id"] = plan.metadata.get("plan_id")
           work_item.metadata["ado_markdown"] = ado_markdown
           await self.brain_engine.store_work_item(work_item)
           
           # Step 5: Create in ADO (optional)
           if self.ado_api_client:
               ado_response = await self.ado_api_client.create_work_item(
                   work_item_type="User Story",
                   title=work_item.title,
                   description=ado_markdown
               )
               work_item.work_item_id = ado_response.get("id")
           
           # Emit completion event
           self.event_bus.emit("ado.story_generated", {
               "work_item_id": work_item.work_item_id,
               "complexity": plan.complexity.value
           })
           
           logger.info(f"✅ ADO Story generated: {work_item.work_item_id}")
           return work_item
       
       async def generate_feature(self, context: PlanningContext) -> WorkItem:
           """
           Generate ADO Feature with planning.
           
           Similar to generate_story but uses FeatureTemplate.
           """
           logger.info(f"📋 Generating ADO Feature: {context.feature_name}")
           
           # Generate plan
           plan = await self.generate_plan(context)
           
           # Create WorkItem
           work_item = WorkItem(
               work_item_id=None,
               work_item_type=WorkItemType.FEATURE,
               title=context.feature_name,
               description=context.description,
               acceptance_criteria=context.acceptance_criteria,
               priority=context.metadata.get("priority", 2),
               tags=self._extract_tags(context, plan)
           )
           
           # Format and store
           template = self.templates[WorkItemType.FEATURE]
           ado_markdown = template.format(work_item, plan)
           work_item.metadata["ado_markdown"] = ado_markdown
           await self.brain_engine.store_work_item(work_item)
           
           logger.info(f"✅ ADO Feature generated")
           return work_item
       
       async def generate_task(self, context: PlanningContext) -> WorkItem:
           """
           Generate ADO Task with planning.
           
           Tasks typically use Skeleton strategy (LOW complexity).
           """
           logger.info(f"📋 Generating ADO Task: {context.feature_name}")
           
           # Generate plan
           plan = await self.generate_plan(context)
           
           # Create WorkItem
           work_item = WorkItem(
               work_item_id=None,
               work_item_type=WorkItemType.TASK,
               title=context.feature_name,
               description=context.description,
               acceptance_criteria=context.acceptance_criteria,
               priority=context.metadata.get("priority", 3),
               tags=self._extract_tags(context, plan)
           )
           
           # Format and store
           template = self.templates[WorkItemType.TASK]
           ado_markdown = template.format(work_item, plan)
           work_item.metadata["ado_markdown"] = ado_markdown
           await self.brain_engine.store_work_item(work_item)
           
           logger.info(f"✅ ADO Task generated")
           return work_item
       
       async def generate_completion_summary(
           self,
           work_item_id: str,
           files_created: List[str] = None,
           files_modified: List[str] = None,
           tests_created: List[str] = None,
           decisions_made: List[str] = None
       ) -> CompletionSummary:
           """
           Generate work completion summary for ADO.
           
           Auto-extracts information from:
           - Git commits (files changed)
           - Test coverage reports
           - Tier 1 conversation log (decisions made)
           """
           logger.info(f"📊 Generating completion summary: {work_item_id}")
           
           # Load work item
           work_item = await self.brain_engine.load_work_item(work_item_id)
           
           if not work_item:
               raise ValueError(f"Work item not found: {work_item_id}")
           
           # Auto-extract data if not provided
           if files_created is None:
               files_created = await self._extract_files_created(work_item_id)
           
           if tests_created is None:
               tests_created = await self._extract_tests_created(work_item_id)
           
           if decisions_made is None:
               decisions_made = await self._extract_decisions(work_item_id)
           
           # Calculate test coverage
           test_coverage = await self._calculate_coverage(work_item_id)
           
           # Create summary
           summary = CompletionSummary(
               work_item_id=work_item_id,
               title=work_item.title,
               files_created=files_created or [],
               files_modified=files_modified or [],
               tests_created=tests_created or [],
               test_coverage=test_coverage,
               decisions_made=decisions_made or [],
               acceptance_criteria_met=work_item.acceptance_criteria
           )
           
           # Store summary
           await self.brain_engine.store_completion_summary(summary)
           
           logger.info(f"✅ Completion summary generated")
           return summary
       
       def _extract_tags(self, context: PlanningContext, 
                        plan: FeaturePlan) -> List[str]:
           """Extract relevant tags for ADO work item."""
           tags = []
           
           # Complexity tag
           tags.append(f"complexity-{plan.complexity.value.lower()}")
           
           # Technology tags (from description keywords)
           tech_keywords = {
               "auth": "authentication",
               "oauth": "oauth",
               "api": "api",
               "database": "database",
               "frontend": "frontend",
               "backend": "backend"
           }
           
           desc_lower = context.description.lower()
           for keyword, tag in tech_keywords.items():
               if keyword in desc_lower:
                   tags.append(tag)
           
           return tags
       
       async def _extract_files_created(self, work_item_id: str) -> List[str]:
           """Extract files created from git commits."""
           # Query Tier 3 git metrics
           commits = await self.brain_engine.query_tier3(
               f"git_commits.work_item_id == '{work_item_id}'"
           )
           
           files = []
           for commit in commits:
               files.extend(commit.get("files_created", []))
           
           return list(set(files))  # Deduplicate
       
       async def _extract_tests_created(self, work_item_id: str) -> List[str]:
           """Extract test files from created files."""
           files = await self._extract_files_created(work_item_id)
           return [f for f in files if "test_" in f or "_test" in f]
       
       async def _extract_decisions(self, work_item_id: str) -> List[str]:
           """Extract decisions from Tier 1 conversation log."""
           conversations = await self.brain_engine.query_tier1(
               f"work_item_id == '{work_item_id}'"
           )
           
           decisions = []
           for conv in conversations:
               # Look for decision markers in conversation
               if "decided to" in conv.get("message", "").lower():
                   decisions.append(conv.get("message"))
           
           return decisions[:5]  # Top 5 decisions
       
       async def _calculate_coverage(self, work_item_id: str) -> float:
           """Calculate test coverage for work item."""
           # Query coverage reports from Tier 3
           coverage_data = await self.brain_engine.query_tier3(
               f"coverage.work_item_id == '{work_item_id}'"
           )
           
           if coverage_data:
               return coverage_data[0].get("coverage_percentage", 0.0)
           
           return 0.0
       
       def _register_ado_mcp_tools(self):
           """Register ADO-specific MCP tools."""
           
           @self.mcp_server.tool("cortex_ado_story")
           async def ado_story_tool(
               feature_name: str,
               description: str,
               acceptance_criteria: list[str],
               priority: int = 2
           ):
               """Generate ADO User Story with planning."""
               context = PlanningContext(
                   feature_name=feature_name,
                   description=description,
                   acceptance_criteria=acceptance_criteria,
                   metadata={"priority": priority}
               )
               
               work_item = await self.generate_story(context)
               
               return {
                   "work_item_id": work_item.work_item_id,
                   "title": work_item.title,
                   "complexity": work_item.metadata.get("plan", {}).get("complexity"),
                   "ado_markdown": work_item.metadata.get("ado_markdown")
               }
           
           @self.mcp_server.tool("cortex_ado_summary")
           async def ado_summary_tool(work_item_id: str):
               """Generate completion summary for ADO work item."""
               summary = await self.generate_completion_summary(work_item_id)
               
               return {
                   "work_item_id": summary.work_item_id,
                   "files_created": len(summary.files_created),
                   "test_coverage": summary.test_coverage,
                   "decisions": len(summary.decisions_made)
               }
           
           logger.info("🔧 ADO MCP tools registered: cortex_ado_story, cortex_ado_summary")
   ```

2. **Implement Feature and Task templates** (2 hours)
   
   **File:** `cortex_orchestrators/ado/templates/feature_template.py`
   ```python
   # Similar structure to StoryTemplate but with Feature-specific sections
   # - Epic linkage
   - Broader scope description
   # - Multiple story breakdown
   ```
   
   **File:** `cortex_orchestrators/ado/templates/task_template.py`
   ```python
   # Simplified template for tasks
   # - No business value section
   # - Single-phase implementation
   # - Checklist-style deliverables
   ```

**Deliverables (Day 2):**
- ✅ `ADOOrchestrator` implemented (extends `PlanningOrchestrator`)
- ✅ Story/Feature/Task generation methods
- ✅ Completion summary generation
- ✅ MCP tools registered

---

### Day 3: Integration & Testing (8 hours)

**Goal:** CLI wrapper, API integration, comprehensive testing

**Tasks:**

1. **Create CLI wrapper** (2 hours)
   
   **File:** `cortex_orchestrators/ado/cli.py`
   ```python
   """
   ADO CLI - Backward compatibility wrapper.
   
   Wraps ADOOrchestrator in CLI interface matching 3.0 behavior.
   """
   import argparse
   import asyncio
   from pathlib import Path
   
   from cortex_core.event_bus import EventBus
   from cortex_core.brain_engine import BrainEngine
   from .orchestrator import ADOOrchestrator
   from cortex_orchestrators.planning.models.context import PlanningContext
   
   async def cmd_create_story(args):
       """Create ADO story (async wrapper)."""
       event_bus = EventBus()
       brain_engine = BrainEngine(Path("cortex-brain"))
       ado = ADOOrchestrator(event_bus, brain_engine)
       
       context = PlanningContext(
           feature_name=args.title,
           description=args.description,
           acceptance_criteria=args.acceptance_criteria or []
       )
       
       work_item = await ado.generate_story(context)
       
       print(f"✅ Story created: {work_item.title}")
       print(f"Complexity: {work_item.metadata.get('complexity')}")
       print(f"\nADO Markdown saved to: {work_item.metadata.get('file_path')}")
   
   def main():
       parser = argparse.ArgumentParser(description="ADO CLI")
       subparsers = parser.add_subparsers(dest="command")
       
       # Create story command
       story_parser = subparsers.add_parser("story", help="Create user story")
       story_parser.add_argument("title", help="Story title")
       story_parser.add_argument("description", help="Story description")
       story_parser.add_argument("--ac", dest="acceptance_criteria", 
                                  action="append", help="Acceptance criteria")
       
       args = parser.parse_args()
       
       if args.command == "story":
           asyncio.run(cmd_create_story(args))
   
   if __name__ == "__main__":
       main()
   ```

2. **Unit tests** (3 hours)
   - Test story generation (10 tests)
   - Test feature generation (5 tests)
   - Test task generation (5 tests)
   - Test completion summary (10 tests)
   - Test template formatting (10 tests)

3. **Integration tests** (3 hours)
   - End-to-end story workflow (context → plan → work item → markdown)
   - MCP tool invocation tests
   - Event bus integration
   - Brain engine storage/retrieval

**Deliverables (Day 3):**
- ✅ CLI wrapper implemented (backward compatible)
- ✅ 40 unit tests passing
- ✅ 10 integration tests passing
- ✅ 95%+ code coverage

---

## 🧪 Testing Strategy

### Unit Tests (40 tests)

1. **Orchestrator** (15 tests)
   - Story generation with LOW/MEDIUM/HIGH complexity
   - Feature generation
   - Task generation
   - Completion summary generation
   - Tag extraction
   - File extraction from git
   - Decision extraction from conversations

2. **Templates** (15 tests)
   - Story template rendering
   - Feature template rendering
   - Task template rendering
   - Markdown structure validation
   - ADO section completeness

3. **Models** (10 tests)
   - WorkItem creation/validation
   - CompletionSummary creation
   - Enum conversions

### Integration Tests (10 tests)

1. **End-to-End** (5 tests)
   - Generate story → Store in brain → Retrieve
   - Generate feature → Format → Validate markdown
   - Generate summary → Extract data → Format

2. **MCP Tools** (3 tests)
   - `cortex_ado_story` tool invocation
   - `cortex_ado_summary` tool invocation
   - Error handling

3. **Event Bus** (2 tests)
   - Story generation events
   - Summary generation events

### E2E Tests (5 tests)

1. User: "plan ado story for user authentication" → ADO Story generated
2. User: "plan ado feature for reporting dashboard" → ADO Feature generated
3. User: "generate summary for US-123" → Completion summary created
4. CLI: `python -m cortex_orchestrators.ado.cli story "Login" "Auth"` → Story file created
5. Invalid request (missing acceptance criteria) → DoR failure

---

## 📊 Success Metrics

### Migration Completion Criteria

- ✅ ADO operations consolidated from 4 files into unified orchestrator
- ✅ Extends PlanningOrchestrator (inherits planning logic)
- ✅ 3 work item types supported (Story/Feature/Task)
- ✅ 95%+ test coverage
- ✅ MCP tools functional
- ✅ CLI backward compatible

### Performance Targets

- **Story generation**: <10 seconds
- **Feature generation**: <15 seconds
- **Task generation**: <5 seconds
- **Summary generation**: <3 seconds

### Code Quality Metrics

- **LOC reduction**: 500 scattered → 600 unified (net increase due to structure)
- **Cyclomatic complexity**: <10 per method
- **Documentation coverage**: 100%

---

## 🔄 Rollback Plan

If migration fails:

1. **Immediate rollback**: Revert to `CORTEX-3.0` branch
2. **Preserve data**: Export work items from brain
3. **Analyze failure**: Review logs, test failures
4. **Fix forward**: Address issues in 4.0
5. **Retry migration**: After validation

**Rollback triggers:**
- Test pass rate <90%
- ADO markdown formatting broken
- CLI backward compatibility broken

---

## 📝 Documentation Updates

### Files to Create

1. **User Guide**: `docs/orchestrators/ado-orchestrator.md`
   - How to use ADO MCP tools
   - Work item type selection
   - Completion summary generation

2. **Developer Guide**: `docs/dev/ado-orchestrator-dev.md`
   - Inheritance from PlanningOrchestrator
   - Template system
   - ADO REST API integration

---

## 🚀 Next Steps

After ADO Orchestrator complete:

1. **Maintenance Orchestrator** (Day 9-11): 7-phase system maintenance
2. **Sanitization Orchestrator** (Day 12-14): Code anonymization
3. **Review Orchestrator** (Day 15-17): PR review automation

---

**Approval Checklist:**

- [ ] Architecture approved (extends PlanningOrchestrator)
- [ ] Timeline realistic (3 days = 24 hours)
- [ ] Test coverage sufficient (55 tests)
- [ ] Templates cover all 3 work item types
- [ ] CLI backward compatible

**Sign-off:** _________________________________  Date: ___________
