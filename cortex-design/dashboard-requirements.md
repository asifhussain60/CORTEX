# CORTEX Dashboard - Requirements & Design Specification

**Version:** 1.0  
**Date:** 2025-11-05  
**Status:** 📋 REQUIREMENTS DEFINED  
**Purpose:** Define CORTEX-native dashboard approach (eliminates dual WPF+HTML dashboards)

---

## 🎯 Executive Summary

**Decision**: Build a **client-side React dashboard** with beautiful modern UI that reads SQLite directly via sql.js. **Zero server dependencies**, **live data**, and **10x simpler** than KDS v8's dual dashboard approach.

**Key Benefits:**
- ✅ **Beautiful & Modern**: Tailwind CSS + Shadcn/ui components
- ✅ **Live Data**: Real-time file watching (always current)
- ✅ **Zero Servers**: Client-side only (no API, no dependencies)
- ✅ **Fast**: sql.js queries <50ms (runs in browser)
- ✅ **Simple**: ~500 LOC vs 5,000+ (WPF)
- ✅ **Cross-platform**: Works anywhere (browser-based)

---

## 📊 Problem Statement

### KDS v8 Dashboard Issues

**Dual dashboards with redundant features:**

1. **WPF Dashboard** (dashboard-wpf/)
   - 5,000+ lines of C# code
   - Windows-only (.NET 8 required)
   - Built for 6-tier architecture
   - FileSystemWatcher + YAML/JSONL parsing
   - Material Design (looks good)
   - Real-time updates (works)
   - **Problem**: Not portable, tied to KDS v8

2. **HTML Dashboard** (kds-dashboard.html)
   - 2,769 lines (inline CSS/JS)
   - Cross-platform (browser-based)
   - No real-time (manual refresh only)
   - Chart.js visualization
   - **Problem**: No live data, unmaintainable

**Result**: Maintenance burden, feature fragmentation, user confusion

---

## ✅ CORTEX Solution

### Architecture: Client-Side Dashboard (Zero Server)

```
CORTEX/
├── cortex-brain.db                    # SQLite database (live data)
│
├── cortex-dashboard/                  # Static React app
│   ├── index.html                     # Entry point
│   ├── package.json                   # Dependencies (React, sql.js, Tailwind)
│   ├── tailwind.config.js             # Tailwind + Shadcn/ui config
│   │
│   ├── src/
│   │   ├── App.tsx                    # Main app component
│   │   ├── lib/
│   │   │   ├── sqlite.ts              # sql.js wrapper
│   │   │   └── file-watcher.ts        # File System Access API
│   │   │
│   │   ├── components/                # Shadcn/ui components
│   │   │   ├── ui/                    # Base components (button, card, etc.)
│   │   │   ├── GovernancePanel.tsx    # Tier 0: Rule viewer
│   │   │   ├── ConversationList.tsx   # Tier 1: Recent conversations
│   │   │   ├── KnowledgeGraph.tsx     # Tier 2: Pattern visualization
│   │   │   ├── MetricCharts.tsx       # Tier 3: Dev metrics
│   │   │   └── HealthStatus.tsx       # Overall brain health
│   │   │
│   │   └── hooks/
│   │       ├── useSqlite.ts           # React hook for DB queries
│   │       ├── useFileWatcher.ts      # React hook for live updates
│   │       └── useTheme.ts            # Dark/light theme switching
│   │
│   └── public/
│       └── cortex-brain.db            # Symlink to actual DB (read-only)
```

---

## 🛠️ Technology Stack

### 1. Frontend Framework: **React 18+**

**Why React (not Next.js/Svelte)?**
- ✅ **Mature ecosystem**: Vast component library support
- ✅ **Shadcn/ui compatibility**: Best React integration
- ✅ **Client-side rendering**: No server needed (static build)
- ✅ **Hooks**: Clean state management for live data
- ✅ **Developer familiarity**: Most widely known framework

**Deployment**: Static build (`npm run build` → pure HTML/CSS/JS)

---

### 2. UI Framework: **Tailwind CSS + Shadcn/ui**

**Why Shadcn/ui?**
- ✅ **Beautiful out-of-box**: Pre-designed, modern components
- ✅ **Accessible**: WCAG 2.1 AA compliance built-in
- ✅ **Customizable**: Copy components to project (not package)
- ✅ **Tailwind-based**: Utility-first CSS (fast development)
- ✅ **Dark/light themes**: Built-in theme system
- ✅ **Professional look**: Matches modern design standards

**Component Library Examples:**
- Cards (for metric panels)
- Tables (for conversation lists)
- Charts (via Recharts integration)
- Modals (for detailed views)
- Tabs (for tier navigation)
- Badges (for status indicators)

---

### 3. SQLite Access: **sql.js (WebAssembly)**

**How it works:**
```typescript
// Load sql.js once
import initSqlJs from 'sql.js';
const SQL = await initSqlJs({
  locateFile: file => `/sql-wasm.wasm`
});

// Open cortex-brain.db (read-only)
const dbFile = await fetch('/cortex-brain.db').then(r => r.arrayBuffer());
const db = new SQL.Database(new Uint8Array(dbFile));

// Query directly (no server needed!)
const conversations = db.exec(`
  SELECT conversation_id, title, created_at, message_count
  FROM conversations
  ORDER BY created_at DESC
  LIMIT 20
`);

// Result: Array of conversation objects
console.log(conversations[0].values); // [[id, title, timestamp, count], ...]
```

**Why sql.js (not better-sqlite3/API)?**
- ✅ **Browser-native**: Runs in WebAssembly (no Node.js)
- ✅ **Zero server**: No API layer needed
- ✅ **Fast**: <50ms queries (local, no network)
- ✅ **Official**: Maintained by SQLite team
- ✅ **Small**: ~500KB (acceptable for dashboard)

**Dependency**: `sql.js` only (1 package)

---

### 4. Real-Time Updates: **File System Access API**

**How it works:**
```typescript
// Request directory access (once, on dashboard load)
const dirHandle = await window.showDirectoryPicker();

// Watch for file changes
async function watchDatabase() {
  for await (const change of dirHandle.watch()) {
    if (change.path === 'cortex-brain.db') {
      console.log('Database updated!');
      reloadDashboard(); // Re-query SQLite
    }
  }
}

// React hook wrapper
function useFileWatcher(filePath: string, onChanged: () => void) {
  useEffect(() => {
    const watcher = new FileSystemWatcher(filePath);
    watcher.onChange(onChanged);
    return () => watcher.stop();
  }, [filePath]);
}
```

**Why File System Access API (not WebSocket)?**
- ✅ **Browser-native**: No server needed
- ✅ **Real-time**: Detects file changes instantly (<100ms)
- ✅ **Simple**: No WebSocket server to manage
- ✅ **Secure**: User grants permission once

**Fallback**: Polling (if File System API unavailable) - check file timestamp every 1 second

---

### 5. Charts: **Recharts** (TBD)

**Why Recharts (not Chart.js)?**
- ✅ **React-native**: Built for React (declarative)
- ✅ **Composable**: Chart components like React components
- ✅ **Responsive**: Auto-adjusts to container size
- ✅ **Accessible**: Better keyboard navigation
- ✅ **Modern**: Hooks-based API

**Alternative**: Chart.js (if Recharts too complex)

**Chart Types Needed:**
- Line charts (conversation timeline)
- Bar charts (event type distribution)
- Area charts (metric trends)
- Pie charts (pattern categories)

---

## 🎨 Design Requirements

### Visual Design Principles

1. **Professional Appearance**
   - Clean, minimal interface
   - Consistent spacing and typography
   - Professional color palette
   - High contrast for readability

2. **Modern Aesthetics**
   - Smooth animations (200-300ms transitions)
   - Subtle shadows and depth
   - Rounded corners (border-radius: 0.5rem)
   - Gradient accents (optional)

3. **Accessibility**
   - WCAG 2.1 AA compliance
   - Keyboard navigation
   - Screen reader support
   - High contrast mode

4. **Responsiveness**
   - Desktop-first (primary use case)
   - Tablet-friendly (optional)
   - Mobile-viewable (nice-to-have)

---

### Theme System

**Dark Theme (Default):**
- Background: `#0a0a0a` (near-black)
- Surface: `#1a1a1a` (dark gray)
- Primary: `#3b82f6` (blue)
- Success: `#10b981` (green)
- Warning: `#f59e0b` (amber)
- Critical: `#ef4444` (red)
- Text primary: `#f5f5f5` (off-white)
- Text secondary: `#a3a3a3` (gray)

**Light Theme:**
- Background: `#ffffff` (white)
- Surface: `#f5f5f5` (light gray)
- Primary: `#2563eb` (darker blue)
- (Same accent colors as dark)
- Text primary: `#0a0a0a` (near-black)
- Text secondary: `#737373` (dark gray)

**Theme Switching:**
- Toggle button in header
- Persists in localStorage
- System preference detection (prefers-color-scheme)

---

### Layout Structure

```
┌─────────────────────────────────────────────────────────────┐
│ Header: [🧠 CORTEX Dashboard] [Theme Toggle] [Refresh]     │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────┬─────────────┬─────────────┬─────────────┐ │
│ │ Tier 0      │ Tier 1      │ Tier 2      │ Tier 3      │ │ (Tabs)
│ └─────────────┴─────────────┴─────────────┴─────────────┘ │
│                                                             │
│ ┌───────────────────────────────────────────────────────┐ │
│ │ Brain Health Status (Overall)                         │ │
│ │ [Excellent] Events: 20 | Patterns: 1,234 | Conv: 18  │ │
│ └───────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────┐ ┌─────────────────────────────┐  │
│ │ Recent Activity     │ │ Key Metrics                 │  │
│ │ • conversation_rec  │ │ [Chart: Event Distribution] │  │
│ │ • pattern_learned   │ │                             │  │
│ │ • context_updated   │ │                             │  │
│ └─────────────────────┘ └─────────────────────────────┘  │
│                                                             │
│ ┌───────────────────────────────────────────────────────┐ │
│ │ Detailed View (depends on active tab)                 │ │
│ │ - Tier 0: Rule list with status                       │ │
│ │ - Tier 1: Conversation timeline                       │ │
│ │ - Tier 2: Knowledge graph visualization              │ │
│ │ - Tier 3: Development metrics charts                 │ │
│ └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Feature Requirements

### Priority 0 (Must-Have for v1.0)

**1. Brain Health Dashboard**
- Overall health status (Excellent/Good/Fair/Needs Attention)
- Key metrics: Event count, pattern count, conversation count
- Health calculation logic (same as KDS V8)
- Real-time updates (file watching)

**2. Tier 0: Governance Panel**
- List all 22 governance rules
- Status: Active/Protected/Violated
- Rule details: Description, category, severity
- Violation history (if any)

**3. Tier 1: Conversation Viewer**
- Last 20 conversations (FIFO)
- Display: Title, timestamp, message count, entities
- Click to expand: Show conversation details
- Real-time updates when new conversations added

**4. Tier 2: Pattern List (Simple)**
- List patterns by type (feature/command/workflow)
- Display: Name, confidence, last accessed
- Filter by type
- Search by keyword

**5. Tier 3: Metrics Summary**
- Git activity: Recent commits, lines added
- Test results: Pass rate, test count
- Build status: Success/failure
- Development velocity trends

**6. Theme System**
- Dark/light theme toggle
- Persists preference
- Smooth transitions

---

### Priority 1 (High Priority, Post-v1.0)

**7. Knowledge Graph Visualization**
- Interactive node graph (patterns + relationships)
- D3.js or Cytoscape.js
- Click node → show related patterns
- Filter by confidence threshold

**8. Advanced Charts**
- Conversation timeline (line chart)
- Event type distribution (pie chart)
- Metric trends over time (area chart)
- Interactive tooltips

**9. Search & Filter**
- Global search across all tiers
- Filter conversations by entity/file
- Filter patterns by confidence/type
- Date range filtering

**10. Export Features**
- Export conversations to JSON/CSV
- Export patterns to JSON
- Export metrics to CSV
- Copy to clipboard

---

### Priority 2 (Nice-to-Have)

**11. Alert System**
- Notification when health degrades
- Alert when rule violated
- Warning when conversation limit near (18/20)
- Browser notifications (opt-in)

**12. Pattern Analytics**
- Pattern confidence decay visualization
- Most frequently accessed patterns
- Pattern relationship strength
- Unused pattern detection

**13. Developer Insights**
- Productivity heatmap (by hour/day)
- File churn analysis
- Test coverage trends
- Velocity predictions

**14. Customization**
- Rearrange dashboard panels (drag-drop)
- Hide/show panels
- Customize theme colors
- Save custom views

---

## 🔄 Real-Time Data Flow

### How Live Data Works

```
1. CORTEX writes to cortex-brain.db
   ↓
2. SQLite transaction commits
   ↓
3. File modification timestamp updates
   ↓
4. File System Access API detects change (<100ms)
   ↓
5. Dashboard re-queries database (via sql.js)
   ↓
6. React state updates
   ↓
7. UI re-renders with new data
```

**Total Latency**: <200ms (file watch + query + render)

---

### SQL Queries (Examples)

**Tier 0: Get All Rules**
```sql
SELECT rule_id, name, severity, status, violation_count
FROM governance_rules
ORDER BY severity DESC, rule_id ASC;
```

**Tier 1: Get Recent Conversations**
```sql
SELECT conversation_id, title, created_at, message_count, is_active
FROM conversations
ORDER BY created_at DESC
LIMIT 20;
```

**Tier 2: Search Patterns**
```sql
SELECT pattern_id, name, pattern_type, confidence, last_accessed
FROM patterns
WHERE patterns MATCH 'export button' -- FTS5 search
ORDER BY rank
LIMIT 10;
```

**Tier 3: Get Metrics Summary**
```sql
SELECT metric_name, metric_value, timestamp
FROM context_metrics
WHERE metric_name IN ('commits_today', 'test_pass_rate', 'build_status')
ORDER BY timestamp DESC;
```

---

## 📦 Dependencies

### Production Dependencies
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "sql.js": "^1.8.0",
    "recharts": "^2.10.0",
    "lucide-react": "^0.263.1",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^5.0.0",
    "vite": "^5.0.0",
    "tailwindcss": "^3.3.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0"
  }
}
```

**Total Size**: ~2.5 MB (uncompressed), ~800 KB (gzipped)

**Note**: Shadcn/ui components are **copied into project** (not a package dependency)

---

## 🚀 Implementation Strategy

### Phase 0: Requirements & Mockups (2-3 hours) ← CURRENT

- ✅ Define technology stack (this document)
- ✅ Design requirements and layout
- 📋 Create wireframes/mockups (optional)
- 📋 Validate approach with user

### Phase 1: Tier 1 Complete → Conversation Viewer (3-4 hours)

**When**: After Tier 1 STM implementation complete

**Tasks**:
1. Set up React + Vite project
2. Install Tailwind + Shadcn/ui
3. Integrate sql.js
4. Build ConversationList component
5. Test with real cortex-brain.db

**Deliverable**: Functional conversation viewer with live data

---

### Phase 2: Tier 2 Complete → Pattern List (2-3 hours)

**When**: After Tier 2 LTM implementation complete

**Tasks**:
1. Add KnowledgeGraph component (simple list view)
2. Implement FTS5 search
3. Add pattern filtering
4. Test pattern queries

**Deliverable**: Pattern browser with search

---

### Phase 3: Tier 3 Complete → Metrics Dashboard (2-3 hours)

**When**: After Tier 3 Context implementation complete

**Tasks**:
1. Add MetricCharts component
2. Integrate Recharts
3. Build metric queries
4. Add trend visualization

**Deliverable**: Complete metrics dashboard

---

### Phase 4: Polish & Enhancement (3-4 hours)

**When**: All tiers complete

**Tasks**:
1. Add Tier 0 governance panel
2. Implement theme switching
3. Add health status summary
4. Performance optimization
5. Accessibility audit
6. Browser compatibility testing

**Deliverable**: Production-ready dashboard (v1.0)

---

## 📊 Success Metrics

**Dashboard is successful when:**

### Performance
- ✅ Initial load: <2 seconds
- ✅ Query latency: <50ms per query
- ✅ UI render: <100ms (60fps)
- ✅ File watch response: <200ms total

### Usability
- ✅ Users prefer it over KDS v8 dashboards
- ✅ Zero learning curve (intuitive)
- ✅ Provides actionable insights
- ✅ "Looks professional and modern"

### Technical
- ✅ Zero server dependencies
- ✅ Cross-browser compatibility (Chrome, Firefox, Safari, Edge)
- ✅ Accessibility score: 90+ (Lighthouse)
- ✅ Code size: <500 LOC (excluding Shadcn components)

---

## 🎯 Benefits Summary

### vs WPF Dashboard

| Aspect | WPF | CORTEX Dashboard |
|--------|-----|------------------|
| **Lines of Code** | 5,000+ | ~500 |
| **Platform** | Windows-only | Cross-platform |
| **Dependencies** | .NET 8 runtime | Browser only |
| **Real-time** | FileSystemWatcher | File System API |
| **Design** | Material Design | Tailwind + Shadcn/ui |
| **Maintenance** | High (2 codebases) | Low (1 codebase) |

### vs HTML Dashboard

| Aspect | HTML | CORTEX Dashboard |
|--------|------|------------------|
| **Real-time** | Manual refresh | Live (file watching) |
| **Code Quality** | Inline CSS/JS | Modular components |
| **Charts** | Static Chart.js | Interactive Recharts |
| **Maintainability** | Low (monolith) | High (components) |
| **Design** | Basic | Modern (Shadcn/ui) |

---

## ✅ Decision Summary

**Technology Stack:**
- ✅ React 18+ (frontend framework)
- ✅ Tailwind CSS + Shadcn/ui (modern, beautiful UI)
- ✅ sql.js (client-side SQLite)
- ✅ File System Access API (real-time watching)
- ✅ Recharts (data visualization)

**Architecture:**
- ✅ Client-side only (zero server dependencies)
- ✅ Direct SQLite access (no API layer)
- ✅ Static build (deploy anywhere)
- ✅ Incremental implementation (grows with tiers)

**Design:**
- ✅ Professional dark/light themes
- ✅ Accessible (WCAG 2.1 AA)
- ✅ Responsive (desktop-first)
- ✅ Modern aesthetics

**Benefits:**
- ✅ Saves 6-9 hours (no WPF/HTML maintenance, no API server)
- ✅ 10x simpler (~500 LOC vs 5,000+)
- ✅ Beautiful & modern UI
- ✅ Live data (real-time updates)
- ✅ Cross-platform (works anywhere)

---

**Status**: ✅ REQUIREMENTS COMPLETE  
**Next**: Create architecture specifications (7 docs)  
**Timeline**: Dashboard implementation during Phase 1-4 (incremental)
