# Sub-Group 4C: Dashboard Implementation Plan

**Created:** November 6, 2025  
**Estimated Duration:** 10-12 hours  
**Status:** 📋 Ready to Begin  
**Technology Stack:** React + Vite + SQL.js + TailwindCSS

---

## 🎯 Objective

Create a modern web-based dashboard for real-time CORTEX brain visualization with:
- Live connection to SQLite databases (Tier 1, 2, 3)
- Real-time file watching for updates
- Clean, professional UI with data visualization
- Core features only (enhancements deferred to future)

---

## 📋 Task Breakdown

### Task 4C.1: Dashboard Setup (1 hour)

**Goal:** Initialize React + Vite project with required dependencies

**Actions:**
1. Create `CORTEX/dashboard/` directory
2. Initialize Vite + React + TypeScript project
3. Install dependencies:
   - `sql.js` - SQLite in browser
   - `recharts` - Data visualization
   - `tailwindcss` - Styling
   - `lucide-react` - Icons
   - `@tanstack/react-query` - Data fetching
4. Configure Vite for development
5. Set up TailwindCSS
6. Create basic layout structure

**Deliverables:**
- `CORTEX/dashboard/` - Initialized project
- `package.json` - All dependencies
- `vite.config.ts` - Vite configuration
- `tailwind.config.js` - Tailwind setup
- `src/App.tsx` - Main component skeleton

**Exit Criteria:**
- Development server runs (`npm run dev`)
- Hot reload functional
- Basic layout renders

---

### Task 4C.2: SQL.js Integration (1.5 hours)

**Goal:** Create database access layer for reading CORTEX brain SQLite files

**Actions:**
1. Create `src/lib/db/` directory
2. Implement `DatabaseLoader.ts`:
   - Load SQLite files from filesystem
   - Initialize SQL.js
   - Query helper functions
3. Implement `Tier1DB.ts`:
   - Conversations queries
   - Messages queries
   - Entity queries
4. Implement `Tier2DB.ts`:
   - Patterns queries
   - FTS5 search
   - Relationship queries
5. Implement `Tier3DB.ts`:
   - Metrics queries
   - Hotspots queries

**Deliverables:**
- `src/lib/db/DatabaseLoader.ts` - Core DB access
- `src/lib/db/Tier1DB.ts` - Tier 1 queries
- `src/lib/db/Tier2DB.ts` - Tier 2 queries
- `src/lib/db/Tier3DB.ts` - Tier 3 queries
- `src/lib/db/types.ts` - TypeScript interfaces

**Exit Criteria:**
- Can load `cortex-brain.db` successfully
- Queries return typed data
- Error handling in place

---

### Task 4C.3: Real-Time File Watching (2 hours)

**Goal:** Implement live updates when brain databases change

**Actions:**
1. Research browser FileSystem Access API limitations
2. Implement polling strategy:
   - Check file modification times every 2 seconds
   - Reload database if changed
   - Emit update events
3. Create `src/hooks/useRealtimeDB.ts`:
   - React hook for live database connection
   - Auto-reload on file changes
   - Loading/error states
4. Add visual indicators for:
   - Connected state
   - Updating state
   - Last update timestamp

**Deliverables:**
- `src/lib/watcher/FileWatcher.ts` - File watching logic
- `src/hooks/useRealtimeDB.ts` - React hook
- `src/components/ConnectionStatus.tsx` - Status indicator

**Exit Criteria:**
- Dashboard auto-updates when brain files change
- Visual feedback shows update status
- No performance degradation from polling

---

### Task 4C.4: Tier 1 Visualization (2.5 hours)

**Goal:** Display working memory (conversations, messages, entities)

**Features:**
1. **Conversations Tab:**
   - List last 20 conversations (FIFO queue)
   - Show: topic, message count, duration, outcome
   - Timeline visualization
   - Click to expand message details

2. **Recent Activity Stream:**
   - Last 50 messages across all conversations
   - Color-coded by role (user/assistant)
   - Timestamps
   - Entity highlighting

3. **Entity Tracker:**
   - List extracted entities (files, functions, etc.)
   - Show entity type and context
   - Filter by type

**Deliverables:**
- `src/pages/ConversationsPage.tsx`
- `src/components/tier1/ConversationList.tsx`
- `src/components/tier1/MessageStream.tsx`
- `src/components/tier1/EntityList.tsx`

**Exit Criteria:**
- Can view all 20 conversations
- Message stream updates in real-time
- Entity extraction displayed correctly

---

### Task 4C.5: Tier 2 Visualization (2.5 hours)

**Goal:** Display knowledge graph (patterns, relationships, workflows)

**Features:**
1. **Pattern Browser:**
   - List all patterns with confidence scores
   - Filter by category (intent, workflow, file-relationship)
   - Search patterns using FTS5
   - Show usage count and last seen

2. **Relationship Graph:**
   - Visual graph of file relationships
   - Node size = co-modification strength
   - Edge thickness = relationship confidence
   - Interactive zoom/pan

3. **Workflow Templates:**
   - List learned workflows
   - Show workflow steps
   - Display success rate
   - Copy workflow to clipboard

**Deliverables:**
- `src/pages/KnowledgePage.tsx`
- `src/components/tier2/PatternBrowser.tsx`
- `src/components/tier2/RelationshipGraph.tsx`
- `src/components/tier2/WorkflowList.tsx`

**Exit Criteria:**
- Can browse all patterns
- FTS5 search functional
- Relationship graph renders correctly

---

### Task 4C.6: Tier 3 Visualization (2 hours)

**Goal:** Display development context (metrics, hotspots, insights)

**Features:**
1. **Metrics Dashboard:**
   - Commit velocity chart (last 30 days)
   - Lines added/deleted trends
   - Test pass rate over time
   - Build success rate

2. **File Hotspots:**
   - List files by churn rate
   - Highlight unstable files (>20% churn)
   - Show co-modification patterns
   - Recommend testing strategy

3. **Insights Panel:**
   - Best work times (productivity patterns)
   - Test-first vs test-skip effectiveness
   - Velocity trends (increasing/decreasing)
   - Proactive warnings

**Deliverables:**
- `src/pages/MetricsPage.tsx`
- `src/components/tier3/MetricsCharts.tsx`
- `src/components/tier3/HotspotList.tsx`
- `src/components/tier3/InsightsPanel.tsx`

**Exit Criteria:**
- Charts render historical data
- Hotspots highlighted correctly
- Insights display actionable recommendations

---

### Task 4C.7: Performance Monitoring (1.5 hours)

**Goal:** Display system health and performance metrics

**Features:**
1. **Health Status:**
   - Tier 1 status (conversation count, capacity)
   - Tier 2 status (pattern count, FTS5 health)
   - Tier 3 status (last collection time)
   - Overall system status

2. **Query Performance:**
   - Average query times per tier
   - Slow query alerts
   - Database file sizes

3. **Resource Usage:**
   - Event backlog size
   - Memory usage (browser)
   - Auto-update frequency

**Deliverables:**
- `src/pages/HealthPage.tsx`
- `src/components/health/HealthCards.tsx`
- `src/components/health/PerformanceMetrics.tsx`

**Exit Criteria:**
- Health status accurate
- Performance metrics update in real-time
- Alerts trigger correctly

---

### Task 4C.8: Testing (1 hour)

**Goal:** Implement 5 critical E2E tests

**Tests:**
1. **Database Loading Test:**
   - Verify can load all 3 tier databases
   - Check schema validation
   - Handle missing files gracefully

2. **Conversation Display Test:**
   - Load conversations from Tier 1
   - Verify correct count (≤20)
   - Check FIFO ordering

3. **Pattern Search Test:**
   - Search patterns using FTS5
   - Verify search results
   - Check confidence sorting

4. **Real-Time Update Test:**
   - Simulate database file change
   - Verify dashboard detects update
   - Check UI refreshes

5. **Performance Test:**
   - Query all tiers
   - Verify query times <100ms
   - Check no memory leaks

**Deliverables:**
- `tests/e2e/database-loading.spec.ts`
- `tests/e2e/conversations.spec.ts`
- `tests/e2e/pattern-search.spec.ts`
- `tests/e2e/realtime-updates.spec.ts`
- `tests/e2e/performance.spec.ts`

**Exit Criteria:**
- All 5 tests passing
- Tests run in CI/CD
- No flaky tests

---

## 📦 Technology Stack

### Core Framework
- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **TypeScript** - Type safety

### Database
- **SQL.js** - SQLite in browser
- **@tanstack/react-query** - Data fetching and caching

### UI/Styling
- **TailwindCSS** - Utility-first CSS
- **Lucide React** - Icon library
- **Recharts** - Charts and graphs

### Testing
- **Vitest** - Unit tests
- **Playwright** - E2E tests

---

## 🎨 UI Design Principles

### Color Palette (CORTEX Brand)
- **Primary:** Deep Purple `#9333EA` (strategic thinking)
- **Secondary:** Electric Blue `#3B82F6` (execution)
- **Success:** Teal `#14B8A6` (completion)
- **Warning:** Yellow `#FBBF24` (alerts)
- **Danger:** Red `#EF4444` (errors)
- **Background:** Dark Gray `#1F2937`
- **Surface:** Slightly lighter `#374151`

### Layout
- **Sidebar Navigation:** Tier 1, Tier 2, Tier 3, Health
- **Main Content:** Full-width with padding
- **Cards:** Rounded corners, subtle shadows
- **Responsive:** Mobile-first design

### Typography
- **Headings:** Inter font, semi-bold
- **Body:** Inter font, regular
- **Code:** JetBrains Mono

---

## 📊 Success Criteria

### Functional Requirements
✅ Dashboard loads and displays data from all 3 tiers  
✅ Real-time updates when brain files change  
✅ Can view last 20 conversations (Tier 1)  
✅ Can search patterns using FTS5 (Tier 2)  
✅ Can view metrics and hotspots (Tier 3)  
✅ Health status displays accurately  
✅ All 5 E2E tests passing

### Performance Requirements
✅ Initial load time <2 seconds  
✅ Query response time <100ms  
✅ UI refresh on update <500ms  
✅ No memory leaks during polling  
✅ Smooth 60fps animations

### Code Quality
✅ TypeScript strict mode enabled  
✅ ESLint configured and passing  
✅ Prettier formatting  
✅ Component modularity (single responsibility)  
✅ Proper error handling

---

## 📁 File Structure

```
CORTEX/dashboard/
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
├── index.html
├── src/
│   ├── main.tsx                    # Entry point
│   ├── App.tsx                     # Root component
│   ├── lib/
│   │   ├── db/
│   │   │   ├── DatabaseLoader.ts   # Core DB access
│   │   │   ├── Tier1DB.ts         # Tier 1 queries
│   │   │   ├── Tier2DB.ts         # Tier 2 queries
│   │   │   ├── Tier3DB.ts         # Tier 3 queries
│   │   │   └── types.ts           # TypeScript types
│   │   └── watcher/
│   │       └── FileWatcher.ts     # File watching
│   ├── hooks/
│   │   └── useRealtimeDB.ts       # Real-time DB hook
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx
│   │   │   └── Header.tsx
│   │   ├── tier1/
│   │   │   ├── ConversationList.tsx
│   │   │   ├── MessageStream.tsx
│   │   │   └── EntityList.tsx
│   │   ├── tier2/
│   │   │   ├── PatternBrowser.tsx
│   │   │   ├── RelationshipGraph.tsx
│   │   │   └── WorkflowList.tsx
│   │   ├── tier3/
│   │   │   ├── MetricsCharts.tsx
│   │   │   ├── HotspotList.tsx
│   │   │   └── InsightsPanel.tsx
│   │   └── health/
│   │       ├── HealthCards.tsx
│   │       └── PerformanceMetrics.tsx
│   └── pages/
│       ├── ConversationsPage.tsx
│       ├── KnowledgePage.tsx
│       ├── MetricsPage.tsx
│       └── HealthPage.tsx
├── tests/
│   └── e2e/
│       ├── database-loading.spec.ts
│       ├── conversations.spec.ts
│       ├── pattern-search.spec.ts
│       ├── realtime-updates.spec.ts
│       └── performance.spec.ts
└── README.md
```

---

## ⏱️ Timeline Estimate

| Task | Duration | Dependencies |
|------|----------|--------------|
| 4C.1: Dashboard Setup | 1 hr | None |
| 4C.2: SQL.js Integration | 1.5 hrs | 4C.1 |
| 4C.3: Real-Time Watching | 2 hrs | 4C.2 |
| 4C.4: Tier 1 Visualization | 2.5 hrs | 4C.2, 4C.3 |
| 4C.5: Tier 2 Visualization | 2.5 hrs | 4C.2, 4C.3 |
| 4C.6: Tier 3 Visualization | 2 hrs | 4C.2, 4C.3 |
| 4C.7: Performance Monitoring | 1.5 hrs | 4C.2 |
| 4C.8: Testing | 1 hr | All above |
| **Total** | **14 hrs** | - |

**Note:** Original estimate was 10-12 hours. Padding to 14 hours for safety margin.

---

## 🚀 Next Steps

1. ✅ **Review this plan** - Ensure alignment with GROUP 4 objectives
2. ⏳ **Begin Task 4C.1** - Initialize React + Vite project
3. ⏳ **Implement Tasks 4C.2-4C.8** - Sequential implementation
4. ⏳ **Create completion report** - Document results

---

**Status:** 📋 Ready to Begin  
**Estimated Completion:** November 6-7, 2025 (14 hours)  
**Dependencies:** Sub-Groups 4A & 4B complete ✅
