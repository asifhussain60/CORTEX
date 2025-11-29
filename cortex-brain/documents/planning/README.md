# Planning Category

**Purpose:** Feature plans, ADO work items, roadmaps, strategies, and project planning documentation.

**Auto-Detection Patterns:**
- `PLAN-*.md` - Feature plans
- `ADO-*.md` - Azure DevOps work items
- `*-planning.md` - Planning documents
- `*roadmap*.md` - Roadmaps
- `*strategy*.md` - Strategy documents
- `feature-plan-*.md` - Feature plans
- `*sprint*plan*.md` - Sprint planning
- `*milestone*.md` - Milestone planning
- `*backlog*.md` - Backlog items

**Common Document Types:**
- Feature plans with DoR/DoD
- ADO work item tracking
- Sprint planning documents
- Roadmaps and strategies
- Milestone planning
- Backlog management
- Release planning

**Content Detection:**
Documents containing "Definition of Ready", "Definition of Done", "DoR", "DoD", or "acceptance criteria" are automatically categorized as planning documents.

**Subdirectories:**
- `features/` - Feature-specific plans
- `ado/` - Azure DevOps work items
- `active/` - Active planning documents
- `completed/` - Completed plans (archive)

**Index:** See [INDEX.md](./INDEX.md) for complete listing with date grouping.

**Organization:** Documents are automatically organized by date and status, with special handling for ADO work items and feature plans.
