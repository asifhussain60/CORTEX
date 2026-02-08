bootstrap.js:13 [Bootstrap] Starting CORTEX Dashboard...
bootstrap.js:37 [Bootstrap] Services created ✓
bootstrap.js:50 [Bootstrap] Embedded data registered: ksessions
DashboardController.js:48 [Controller] Initializing dashboard...
DashboardController.js:51 [Controller] → Injecting dependencies...
DashboardController.js:56 [Controller] ✓ Dependencies injected
DashboardController.js:59 [Controller] → Initializing DOM references...
DashboardController.js:557 [Controller] _initTabs: Initializing tab navigation...
DashboardController.js:558 [Controller] _initTabs: tabNav element: ✓ Found
DashboardController.js:565 [Controller] _initTabs: Creating 6 tab buttons
DashboardController.js:567 [Controller] _initTabs:   1. Overview (overview)
DashboardController.js:567 [Controller] _initTabs:   2. Architecture (architecture)
DashboardController.js:567 [Controller] _initTabs:   3. Quality (quality)
DashboardController.js:567 [Controller] _initTabs:   4. Security (security)
DashboardController.js:567 [Controller] _initTabs:   5. Dependencies (dependencies)
DashboardController.js:567 [Controller] _initTabs:   6. Use Cases (usecases)
DashboardController.js:579 [Controller] _initTabs: ✓ Tab HTML generated
DashboardController.js:580 [Controller] _initTabs: ✓ Tab navigation initialized
DashboardController.js:61 [Controller] ✓ DOM references initialized
DashboardController.js:64 [Controller] → Subscribing to state changes...
DashboardController.js:66 [Controller] ✓ State subscription active
DashboardController.js:69 [Controller] → Setting up event listeners...
DashboardController.js:71 [Controller] ✓ Event listeners attached
DashboardController.js:76 [Controller] → Loading initial repository: ksessions
DashboardController.js:77 [Controller]   URL params: {repo: 'ksessions'}
DashboardController.js:78 [Controller]   Default repo: ksessions
DashboardController.js:89 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DashboardController.js:90 [Controller] loadRepository: Starting load for "ksessions"
DashboardController.js:91 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DashboardController.js:93 [Controller] loadRepository: Generation BEFORE state update: 0
DashboardController.js:96 [Controller] loadRepository: → Updating state (loading started)...
StateManager.js:60 [StateManager] setState called by: at DashboardController.loadRepository (file:///D:/PROJECTS/CORTEX/company/dashboards/spa/js/controllers/DashboardController.js:97:27)
StateManager.js:61 [StateManager] Current generation: 0 → 1
StateManager.js:87 [StateManager] Notifying 1 subscribers...
DashboardController.js:771 [Controller] _onStateChange: State change detected
DashboardController.js:772 [Controller] _onStateChange: Old generation: 0
DashboardController.js:773 [Controller] _onStateChange: New generation: 1
DashboardController.js:774 [Controller] _onStateChange: Generation delta: 1
DashboardController.js:778 [Controller] _onStateChange: Repo changed: null → ksessions
DashboardController.js:787 [Controller] _onStateChange: Handler complete (no state mutations)
StateManager.js:89 [StateManager] setState complete. New generation: 1
DashboardController.js:102 [Controller] loadRepository: ✓ State updated
DashboardController.js:106 [Controller] loadRepository: Generation AFTER state update (CAPTURED): 1
DashboardController.js:109 [Controller] loadRepository: → Showing loading overlay...
DashboardController.js:111 [Controller] loadRepository: ✓ Loading overlay visible
DashboardController.js:115 [Controller] loadRepository: → Checking cache...
DashboardController.js:129 [Controller] loadRepository: ✗ Cache MISS
DashboardController.js:133 [Controller] loadRepository: → Loading from RepositoryService...
DashboardController.js:135 [Controller] loadRepository: ✓ Data loaded from service
DashboardController.js:138 [Controller] loadRepository: → Data structure:
DashboardController.js:139 [Controller] loadRepository:   Keys: (5) ['repo', 'overview', 'metrics', 'security', 'dependencies']
DashboardController.js:140 [Controller] loadRepository:   Repo: KSESSIONS
DashboardController.js:141 [Controller] loadRepository:   Overview: ✓
DashboardController.js:142 [Controller] loadRepository:   Metrics: ✓
DashboardController.js:143 [Controller] loadRepository:   Metadata: ✗
DashboardController.js:148 [Controller] loadRepository: → Validating data integrity...
DashboardController.js:155 [Controller] loadRepository: ✓ Validation PASSED
DashboardController.js:159 [Controller] loadRepository: ⚠ Validation warnings: [{…}]
loadRepository @ DashboardController.js:159
await in loadRepository
initialize @ DashboardController.js:80
bootstrapDashboard @ bootstrap.js:60
(anonymous) @ bootstrap.js:170
DashboardController.js:166 [Controller] loadRepository: → Caching data...
StateManager.js:159 [StateManager] setCacheEntry: Caching ksessions (internal cache, no state mutation)
StateManager.js:174 [StateManager] setCacheEntry: Cache size: 1 / 10
DashboardController.js:168 [Controller] loadRepository: ✓ Data cached
DashboardController.js:173 [Controller] loadRepository: → Proceeding to render (generation tracking handled by _renderCurrentTab)
DashboardController.js:176 [Controller] loadRepository: → Updating state (loading complete)...
StateManager.js:60 [StateManager] setState called by: at DashboardController.loadRepository (file:///D:/PROJECTS/CORTEX/company/dashboards/spa/js/controllers/DashboardController.js:177:31)
StateManager.js:61 [StateManager] Current generation: 1 → 2
StateManager.js:87 [StateManager] Notifying 1 subscribers...
DashboardController.js:771 [Controller] _onStateChange: State change detected
DashboardController.js:772 [Controller] _onStateChange: Old generation: 1
DashboardController.js:773 [Controller] _onStateChange: New generation: 2
DashboardController.js:774 [Controller] _onStateChange: Generation delta: 1
DashboardController.js:787 [Controller] _onStateChange: Handler complete (no state mutations)
StateManager.js:89 [StateManager] setState complete. New generation: 2
DashboardController.js:182 [Controller] loadRepository: ✓ State updated with data
DashboardController.js:183 [Controller] loadRepository:   New generation: 2
DashboardController.js:186 [Controller] loadRepository: → Updating URL...
DashboardController.js:188 [Controller] loadRepository: ✓ URL updated
DashboardController.js:191 [Controller] loadRepository: → Rendering current tab...
StateManager.js:60 [StateManager] setState called by: at DashboardController._renderCurrentTab (file:///D:/PROJECTS/CORTEX/company/dashboards/spa/js/controllers/DashboardController.js:247:27)
StateManager.js:61 [StateManager] Current generation: 2 → 3
StateManager.js:87 [StateManager] Notifying 1 subscribers...
DashboardController.js:771 [Controller] _onStateChange: State change detected
DashboardController.js:772 [Controller] _onStateChange: Old generation: 2
DashboardController.js:773 [Controller] _onStateChange: New generation: 3
DashboardController.js:774 [Controller] _onStateChange: Generation delta: 1
DashboardController.js:787 [Controller] _onStateChange: Handler complete (no state mutations)
StateManager.js:89 [StateManager] setState complete. New generation: 3
DashboardController.js:254 [Controller] _renderCurrentTab: Generation captured for staleness check: 3
DashboardController.js:263 [Controller] _renderCurrentTab: Pre-render generation check: 3 vs 3
DashboardController.js:270 [Controller] _renderCurrentTab: Generation valid - proceeding with render
StateManager.js:60 [StateManager] setState called by: at DashboardController._renderCurrentTab (file:///D:/PROJECTS/CORTEX/company/dashboards/spa/js/controllers/DashboardController.js:298:31)
StateManager.js:61 [StateManager] Current generation: 3 → 4
StateManager.js:87 [StateManager] Notifying 1 subscribers...
DashboardController.js:771 [Controller] _onStateChange: State change detected
DashboardController.js:772 [Controller] _onStateChange: Old generation: 3
DashboardController.js:773 [Controller] _onStateChange: New generation: 4
DashboardController.js:774 [Controller] _onStateChange: Generation delta: 1
DashboardController.js:787 [Controller] _onStateChange: Handler complete (no state mutations)
StateManager.js:89 [StateManager] setState complete. New generation: 4
DashboardController.js:193 [Controller] loadRepository: ✓ Tab rendered
DashboardController.js:195 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DashboardController.js:196 [Controller] loadRepository: ✅ SUCCESS - "ksessions" loaded
DashboardController.js:197 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DashboardController.js:82 [Controller] ✅ Initialization complete
bootstrap.js:67 [Bootstrap] Controller initialized ✓
bootstrap.js:77 [Bootstrap] Dashboard ready ✓
bootstrap.js:115 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
bootstrap.js:116 🚀 CORTEX Dashboard Development Mode
bootstrap.js:117 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
bootstrap.js:118 
bootstrap.js:119 Available Commands:
bootstrap.js:120   window.dashboardDiagnostics()  - Export diagnostics
bootstrap.js:121   window.dashboardState          - Access state manager
bootstrap.js:122   window.dashboardController     - Access controller
bootstrap.js:123 
bootstrap.js:124 State Management:
bootstrap.js:125   - Immutable state with versioning ✓
bootstrap.js:126   - Race condition prevention ✓
bootstrap.js:127   - Stale render rejection ✓
bootstrap.js:128 
bootstrap.js:129 Error Handling:
bootstrap.js:130   - Component error boundaries ✓
bootstrap.js:131   - Retry logic (3x exponential backoff) ✓
bootstrap.js:132   - Timeout protection (5s) ✓
bootstrap.js:133 
bootstrap.js:134 Security:
bootstrap.js:135   - XSS protection (HTML sanitization) ✓
bootstrap.js:136   - Data validation before render ✓
bootstrap.js:137   - Trust boundary enforcement ✓
bootstrap.js:138 
bootstrap.js:139 Performance:
bootstrap.js:140   - Lazy tab loading ✓
bootstrap.js:141   - Request deduplication ✓
bootstrap.js:142   - LRU cache (10 items, 5min TTL) ✓
bootstrap.js:143 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
StateManager.js:60 [StateManager] setState called by: at DashboardController.switchTab (file:///D:/PROJECTS/CORTEX/company/dashboards/spa/js/controllers/DashboardController.js:224:27)
StateManager.js:61 [StateManager] Current generation: 4 → 5
StateManager.js:87 [StateManager] Notifying 1 subscribers...
DashboardController.js:771 [Controller] _onStateChange: State change detected
DashboardController.js:772 [Controller] _onStateChange: Old generation: 4
DashboardController.js:773 [Controller] _onStateChange: New generation: 5
DashboardController.js:774 [Controller] _onStateChange: Generation delta: 1
DashboardController.js:782 [Controller] _onStateChange: Tab changed: overview → architecture
DashboardController.js:787 [Controller] _onStateChange: Handler complete (no state mutations)
StateManager.js:89 [StateManager] setState complete. New generation: 5
StateManager.js:60 [StateManager] setState called by: at DashboardController._renderCurrentTab (file:///D:/PROJECTS/CORTEX/company/dashboards/spa/js/controllers/DashboardController.js:247:27)
StateManager.js:61 [StateManager] Current generation: 5 → 6
StateManager.js:87 [StateManager] Notifying 1 subscribers...
DashboardController.js:771 [Controller] _onStateChange: State change detected
DashboardController.js:772 [Controller] _onStateChange: Old generation: 5
DashboardController.js:773 [Controller] _onStateChange: New generation: 6
DashboardController.js:774 [Controller] _onStateChange: Generation delta: 1
DashboardController.js:787 [Controller] _onStateChange: Handler complete (no state mutations)
StateManager.js:89 [StateManager] setState complete. New generation: 6
DashboardController.js:254 [Controller] _renderCurrentTab: Generation captured for staleness check: 6
DashboardController.js:263 [Controller] _renderCurrentTab: Pre-render generation check: 6 vs 6
DashboardController.js:270 [Controller] _renderCurrentTab: Generation valid - proceeding with render
StateManager.js:60 [StateManager] setState called by: at DashboardController._renderCurrentTab (file:///D:/PROJECTS/CORTEX/company/dashboards/spa/js/controllers/DashboardController.js:298:31)
StateManager.js:61 [StateManager] Current generation: 6 → 7
StateManager.js:87 [StateManager] Notifying 1 subscribers...
DashboardController.js:771 [Controller] _onStateChange: State change detected
DashboardController.js:772 [Controller] _onStateChange: Old generation: 6
DashboardController.js:773 [Controller] _onStateChange: New generation: 7
DashboardController.js:774 [Controller] _onStateChange: Generation delta: 1
DashboardController.js:787 [Controller] _onStateChange: Handler complete (no state mutations)
StateManager.js:89 [StateManager] setState complete. New generation: 7
StateManager.js:60 [StateManager] setState called by: at DashboardController.switchTab (file:///D:/PROJECTS/CORTEX/company/dashboards/spa/js/controllers/DashboardController.js:224:27)
StateManager.js:61 [StateManager] Current generation: 7 → 8
StateManager.js:87 [StateManager] Notifying 1 subscribers...
DashboardController.js:771 [Controller] _onStateChange: State change detected
DashboardController.js:772 [Controller] _onStateChange: Old generation: 7
DashboardController.js:773 [Controller] _onStateChange: New generation: 8
DashboardController.js:774 [Controller] _onStateChange: Generation delta: 1
DashboardController.js:782 [Controller] _onStateChange: Tab changed: architecture → quality
DashboardController.js:787 [Controller] _onStateChange: Handler complete (no state mutations)
StateManager.js:89 [StateManager] setState complete. New generation: 8
StateManager.js:60 [StateManager] setState called by: at DashboardController._renderCurrentTab (file:///D:/PROJECTS/CORTEX/company/dashboards/spa/js/controllers/DashboardController.js:247:27)
StateManager.js:61 [StateManager] Current generation: 8 → 9
StateManager.js:87 [StateManager] Notifying 1 subscribers...
DashboardController.js:771 [Controller] _onStateChange: State change detected
DashboardController.js:772 [Controller] _onStateChange: Old generation: 8
DashboardController.js:773 [Controller] _onStateChange: New generation: 9
DashboardController.js:774 [Controller] _onStateChange: Generation delta: 1
DashboardController.js:787 [Controller] _onStateChange: Handler complete (no state mutations)
StateManager.js:89 [StateManager] setState complete. New generation: 9
DashboardController.js:254 [Controller] _renderCurrentTab: Generation captured for staleness check: 9
DashboardController.js:263 [Controller] _renderCurrentTab: Pre-render generation check: 9 vs 9
DashboardController.js:270 [Controller] _renderCurrentTab: Generation valid - proceeding with render
StateManager.js:60 [StateManager] setState called by: at DashboardController._renderCurrentTab (file:///D:/PROJECTS/CORTEX/company/dashboards/spa/js/controllers/DashboardController.js:298:31)
StateManager.js:61 [StateManager] Current generation: 9 → 10
StateManager.js:87 [StateManager] Notifying 1 subscribers...
DashboardController.js:771 [Controller] _onStateChange: State change detected
DashboardController.js:772 [Controller] _onStateChange: Old generation: 9
DashboardController.js:773 [Controller] _onStateChange: New generation: 10
DashboardController.js:774 [Controller] _onStateChange: Generation delta: 1
DashboardController.js:787 [Controller] _onStateChange: Handler complete (no state mutations)
StateManager.js:89 [StateManager] setState complete. New generation: 10
StateManager.js:60 [StateManager] setState called by: at DashboardController.switchTab (file:///D:/PROJECTS/CORTEX/company/dashboards/spa/js/controllers/DashboardController.js:224:27)
StateManager.js:61 [StateManager] Current generation: 10 → 11
StateManager.js:87 [StateManager] Notifying 1 subscribers...
DashboardController.js:771 [Controller] _onStateChange: State change detected
DashboardController.js:772 [Controller] _onStateChange: Old generation: 10
DashboardController.js:773 [Controller] _onStateChange: New generation: 11
DashboardController.js:774 [Controller] _onStateChange: Generation delta: 1
DashboardController.js:782 [Controller] _onStateChange: Tab changed: quality → security
DashboardController.js:787 [Controller] _onStateChange: Handler complete (no state mutations)
StateManager.js:89 [StateManager] setState complete. New generation: 11
StateManager.js:60 [StateManager] setState called by: at DashboardController._renderCurrentTab (file:///D:/PROJECTS/CORTEX/company/dashboards/spa/js/controllers/DashboardController.js:247:27)
StateManager.js:61 [StateManager] Current generation: 11 → 12
StateManager.js:87 [StateManager] Notifying 1 subscribers...
DashboardController.js:771 [Controller] _onStateChange: State change detected
DashboardController.js:772 [Controller] _onStateChange: Old generation: 11
DashboardController.js:773 [Controller] _onStateChange: New generation: 12
DashboardController.js:774 [Controller] _onStateChange: Generation delta: 1
DashboardController.js:787 [Controller] _onStateChange: Handler complete (no state mutations)
StateManager.js:89 [StateManager] setState complete. New generation: 12
DashboardController.js:254 [Controller] _renderCurrentTab: Generation captured for staleness check: 12
DashboardController.js:263 [Controller] _renderCurrentTab: Pre-render generation check: 12 vs 12
DashboardController.js:270 [Controller] _renderCurrentTab: Generation valid - proceeding with render
StateManager.js:60 [StateManager] setState called by: at DashboardController._renderCurrentTab (file:///D:/PROJECTS/CORTEX/company/dashboards/spa/js/controllers/DashboardController.js:298:31)
StateManager.js:61 [StateManager] Current generation: 12 → 13
StateManager.js:87 [StateManager] Notifying 1 subscribers...
DashboardController.js:771 [Controller] _onStateChange: State change detected
DashboardController.js:772 [Controller] _onStateChange: Old generation: 12
DashboardController.js:773 [Controller] _onStateChange: New generation: 13
DashboardController.js:774 [Controller] _onStateChange: Generation delta: 1
DashboardController.js:787 [Controller] _onStateChange: Handler complete (no state mutations)
StateManager.js:89 [StateManager] setState complete. New generation: 13
StateManager.js:60 [StateManager] setState called by: at DashboardController.switchTab (file:///D:/PROJECTS/CORTEX/company/dashboards/spa/js/controllers/DashboardController.js:224:27)
StateManager.js:61 [StateManager] Current generation: 13 → 14
StateManager.js:87 [StateManager] Notifying 1 subscribers...
DashboardController.js:771 [Controller] _onStateChange: State change detected
DashboardController.js:772 [Controller] _onStateChange: Old generation: 13
DashboardController.js:773 [Controller] _onStateChange: New generation: 14
DashboardController.js:774 [Controller] _onStateChange: Generation delta: 1
DashboardController.js:782 [Controller] _onStateChange: Tab changed: security → dependencies
DashboardController.js:787 [Controller] _onStateChange: Handler complete (no state mutations)
StateManager.js:89 [StateManager] setState complete. New generation: 14
StateManager.js:60 [StateManager] setState called by: at DashboardController._renderCurrentTab (file:///D:/PROJECTS/CORTEX/company/dashboards/spa/js/controllers/DashboardController.js:247:27)
StateManager.js:61 [StateManager] Current generation: 14 → 15
StateManager.js:87 [StateManager] Notifying 1 subscribers...
DashboardController.js:771 [Controller] _onStateChange: State change detected
DashboardController.js:772 [Controller] _onStateChange: Old generation: 14
DashboardController.js:773 [Controller] _onStateChange: New generation: 15
DashboardController.js:774 [Controller] _onStateChange: Generation delta: 1
DashboardController.js:787 [Controller] _onStateChange: Handler complete (no state mutations)
StateManager.js:89 [StateManager] setState complete. New generation: 15
DashboardController.js:254 [Controller] _renderCurrentTab: Generation captured for staleness check: 15
DashboardController.js:263 [Controller] _renderCurrentTab: Pre-render generation check: 15 vs 15
DashboardController.js:270 [Controller] _renderCurrentTab: Generation valid - proceeding with render
visualizations.js:1237 [Viz] renderDependencyGraph error: TypeError: packages.slice is not a function
    at createDependencyGraph (visualizations.js:195:34)
    at Object.renderDependencyGraph (visualizations.js:1234:13)
    at DashboardController._renderDependencies (DashboardController.js:499:36)
    at errorBoundary.wrap.tabId (DashboardController.js:286:40)
    at ErrorBoundary.wrap (ErrorBoundary.js:41:17)
    at DashboardController._renderCurrentTab (DashboardController.js:258:38)
    at DashboardController.switchTab (DashboardController.js:229:20)
    at HTMLElement.<anonymous> (DashboardController.js:592:26)
renderDependencyGraph @ visualizations.js:1237
_renderDependencies @ DashboardController.js:499
errorBoundary.wrap.tabId @ DashboardController.js:286
wrap @ ErrorBoundary.js:41
_renderCurrentTab @ DashboardController.js:258
switchTab @ DashboardController.js:229
(anonymous) @ DashboardController.js:592
DashboardController.js:263 [Controller] _renderCurrentTab: Pre-render generation check: 15 vs 15
DashboardController.js:270 [Controller] _renderCurrentTab: Generation valid - proceeding with render
visualizations.js:1237 [Viz] renderDependencyGraph error: TypeError: packages.slice is not a function
    at createDependencyGraph (visualizations.js:195:34)
    at Object.renderDependencyGraph (visualizations.js:1234:13)
    at DashboardController._renderDependencies (DashboardController.js:499:36)
    at errorBoundary.wrap.tabId (DashboardController.js:286:40)
    at ErrorBoundary.wrap (ErrorBoundary.js:41:17)
    at ErrorBoundary._handleError (ErrorBoundary.js:96:31)
    at async ErrorBoundary.wrap (ErrorBoundary.js:54:20)
    at async DashboardController._renderCurrentTab (DashboardController.js:258:13)
    at async DashboardController.switchTab (DashboardController.js:229:9)
renderDependencyGraph @ visualizations.js:1237
_renderDependencies @ DashboardController.js:499
errorBoundary.wrap.tabId @ DashboardController.js:286
wrap @ ErrorBoundary.js:41
_handleError @ ErrorBoundary.js:96
await in _handleError
wrap @ ErrorBoundary.js:54
await in wrap
_renderCurrentTab @ DashboardController.js:258
switchTab @ DashboardController.js:229
(anonymous) @ DashboardController.js:592
StateManager.js:60 [StateManager] setState called by: at DashboardController.switchTab (file:///D:/PROJECTS/CORTEX/company/dashboards/spa/js/controllers/DashboardController.js:224:27)
StateManager.js:61 [StateManager] Current generation: 15 → 16
StateManager.js:87 [StateManager] Notifying 1 subscribers...
DashboardController.js:771 [Controller] _onStateChange: State change detected
DashboardController.js:772 [Controller] _onStateChange: Old generation: 15
DashboardController.js:773 [Controller] _onStateChange: New generation: 16
DashboardController.js:774 [Controller] _onStateChange: Generation delta: 1
DashboardController.js:782 [Controller] _onStateChange: Tab changed: dependencies → quality
DashboardController.js:787 [Controller] _onStateChange: Handler complete (no state mutations)
StateManager.js:89 [StateManager] setState complete. New generation: 16
StateManager.js:60 [StateManager] setState called by: at DashboardController._renderCurrentTab (file:///D:/PROJECTS/CORTEX/company/dashboards/spa/js/controllers/DashboardController.js:247:27)
StateManager.js:61 [StateManager] Current generation: 16 → 17
StateManager.js:87 [StateManager] Notifying 1 subscribers...
DashboardController.js:771 [Controller] _onStateChange: State change detected
DashboardController.js:772 [Controller] _onStateChange: Old generation: 16
DashboardController.js:773 [Controller] _onStateChange: New generation: 17
DashboardController.js:774 [Controller] _onStateChange: Generation delta: 1
DashboardController.js:787 [Controller] _onStateChange: Handler complete (no state mutations)
StateManager.js:89 [StateManager] setState complete. New generation: 17
DashboardController.js:254 [Controller] _renderCurrentTab: Generation captured for staleness check: 17
DashboardController.js:263 [Controller] _renderCurrentTab: Pre-render generation check: 17 vs 17
DashboardController.js:270 [Controller] _renderCurrentTab: Generation valid - proceeding with render
StateManager.js:60 [StateManager] setState called by: at DashboardController._renderCurrentTab (file:///D:/PROJECTS/CORTEX/company/dashboards/spa/js/controllers/DashboardController.js:298:31)
StateManager.js:61 [StateManager] Current generation: 17 → 18
StateManager.js:87 [StateManager] Notifying 1 subscribers...
DashboardController.js:771 [Controller] _onStateChange: State change detected
DashboardController.js:772 [Controller] _onStateChange: Old generation: 17
DashboardController.js:773 [Controller] _onStateChange: New generation: 18
DashboardController.js:774 [Controller] _onStateChange: Generation delta: 1
DashboardController.js:787 [Controller] _onStateChange: Handler complete (no state mutations)
StateManager.js:89 [StateManager] setState complete. New generation: 18
StateManager.js:60 [StateManager] setState called by: at DashboardController.switchTab (file:///D:/PROJECTS/CORTEX/company/dashboards/spa/js/controllers/DashboardController.js:224:27)
StateManager.js:61 [StateManager] Current generation: 18 → 19
StateManager.js:87 [StateManager] Notifying 1 subscribers...
DashboardController.js:771 [Controller] _onStateChange: State change detected
DashboardController.js:772 [Controller] _onStateChange: Old generation: 18
DashboardController.js:773 [Controller] _onStateChange: New generation: 19
DashboardController.js:774 [Controller] _onStateChange: Generation delta: 1
DashboardController.js:782 [Controller] _onStateChange: Tab changed: quality → architecture
DashboardController.js:787 [Controller] _onStateChange: Handler complete (no state mutations)
StateManager.js:89 [StateManager] setState complete. New generation: 19
StateManager.js:60 [StateManager] setState called by: at DashboardController._renderCurrentTab (file:///D:/PROJECTS/CORTEX/company/dashboards/spa/js/controllers/DashboardController.js:247:27)
StateManager.js:61 [StateManager] Current generation: 19 → 20
StateManager.js:87 [StateManager] Notifying 1 subscribers...
DashboardController.js:771 [Controller] _onStateChange: State change detected
DashboardController.js:772 [Controller] _onStateChange: Old generation: 19
DashboardController.js:773 [Controller] _onStateChange: New generation: 20
DashboardController.js:774 [Controller] _onStateChange: Generation delta: 1
DashboardController.js:787 [Controller] _onStateChange: Handler complete (no state mutations)
StateManager.js:89 [StateManager] setState complete. New generation: 20
DashboardController.js:254 [Controller] _renderCurrentTab: Generation captured for staleness check: 20
DashboardController.js:263 [Controller] _renderCurrentTab: Pre-render generation check: 20 vs 20
DashboardController.js:270 [Controller] _renderCurrentTab: Generation valid - proceeding with render
StateManager.js:60 [StateManager] setState called by: at DashboardController._renderCurrentTab (file:///D:/PROJECTS/CORTEX/company/dashboards/spa/js/controllers/DashboardController.js:298:31)
StateManager.js:61 [StateManager] Current generation: 20 → 21
StateManager.js:87 [StateManager] Notifying 1 subscribers...
DashboardController.js:771 [Controller] _onStateChange: State change detected
DashboardController.js:772 [Controller] _onStateChange: Old generation: 20
DashboardController.js:773 [Controller] _onStateChange: New generation: 21
DashboardController.js:774 [Controller] _onStateChange: Generation delta: 1
DashboardController.js:787 [Controller] _onStateChange: Handler complete (no state mutations)
StateManager.js:89 [StateManager] setState complete. New generation: 21
DashboardController.js:263 [Controller] _renderCurrentTab: Pre-render generation check: 15 vs 21
DashboardController.js:266 [Controller] _renderCurrentTab: Stale render detected - aborting
errorBoundary.wrap.tabId @ DashboardController.js:266
wrap @ ErrorBoundary.js:41
_handleError @ ErrorBoundary.js:96
await in _handleError
wrap @ ErrorBoundary.js:54
await in wrap
_handleError @ ErrorBoundary.js:96
await in _handleError
wrap @ ErrorBoundary.js:54
await in wrap
_renderCurrentTab @ DashboardController.js:258
switchTab @ DashboardController.js:229
(anonymous) @ DashboardController.js:592
bootstrap.js:25 [ErrorBoundary] tab_dependencies: Error: Stale render cancelled
    at errorBoundary.wrap.tabId (DashboardController.js:267:31)
    at ErrorBoundary.wrap (ErrorBoundary.js:41:17)
    at ErrorBoundary._handleError (ErrorBoundary.js:96:31)
    at async ErrorBoundary.wrap (ErrorBoundary.js:54:20)
    at async ErrorBoundary._handleError (ErrorBoundary.js:96:20)
    at async ErrorBoundary.wrap (ErrorBoundary.js:54:20)
    at async DashboardController._renderCurrentTab (DashboardController.js:258:13)
    at async DashboardController.switchTab (DashboardController.js:229:9)
onError @ bootstrap.js:25
_handleError @ ErrorBoundary.js:101
wrap @ ErrorBoundary.js:54
await in wrap
_handleError @ ErrorBoundary.js:96
await in _handleError
wrap @ ErrorBoundary.js:54
await in wrap
_handleError @ ErrorBoundary.js:96
await in _handleError
wrap @ ErrorBoundary.js:54
await in wrap
_renderCurrentTab @ DashboardController.js:258
switchTab @ DashboardController.js:229
(anonymous) @ DashboardController.js:592
StateManager.js:60 [StateManager] setState called by: at DashboardController._renderCurrentTab (file:///D:/PROJECTS/CORTEX/company/dashboards/spa/js/controllers/DashboardController.js:298:31)
StateManager.js:61 [StateManager] Current generation: 21 → 22
StateManager.js:87 [StateManager] Notifying 1 subscribers...
DashboardController.js:771 [Controller] _onStateChange: State change detected
DashboardController.js:772 [Controller] _onStateChange: Old generation: 21
DashboardController.js:773 [Controller] _onStateChange: New generation: 22
DashboardController.js:774 [Controller] _onStateChange: Generation delta: 1
DashboardController.js:787 [Controller] _onStateChange: Handler complete (no state mutations)
StateManager.js:89 [StateManager] setState complete. New generation: 22
