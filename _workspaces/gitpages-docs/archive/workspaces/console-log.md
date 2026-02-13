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
DashboardController.js:782 [Controller] _onStateChange: Tab changed: architecture → security
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
DashboardController.js:782 [Controller] _onStateChange: Tab changed: security → dependencies
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
visualizations.js:1249 [Viz] renderDependencyGraph error: TypeError: packages.slice is not a function
    at createDependencyGraph (visualizations.js:197:34)
    at Object.renderDependencyGraph (visualizations.js:1246:13)
    at DashboardController._renderDependencies (DashboardController.js:499:36)
    at errorBoundary.wrap.tabId (DashboardController.js:286:40)
    at ErrorBoundary.wrap (ErrorBoundary.js:41:17)
    at DashboardController._renderCurrentTab (DashboardController.js:258:38)
    at DashboardController.switchTab (DashboardController.js:229:20)
    at HTMLElement.<anonymous> (DashboardController.js:592:26)
renderDependencyGraph @ visualizations.js:1249
_renderDependencies @ DashboardController.js:499
errorBoundary.wrap.tabId @ DashboardController.js:286
wrap @ ErrorBoundary.js:41
_renderCurrentTab @ DashboardController.js:258
switchTab @ DashboardController.js:229
(anonymous) @ DashboardController.js:592
DashboardController.js:263 [Controller] _renderCurrentTab: Pre-render generation check: 12 vs 12
DashboardController.js:270 [Controller] _renderCurrentTab: Generation valid - proceeding with render
visualizations.js:1249 [Viz] renderDependencyGraph error: TypeError: packages.slice is not a function
    at createDependencyGraph (visualizations.js:197:34)
    at Object.renderDependencyGraph (visualizations.js:1246:13)
    at DashboardController._renderDependencies (DashboardController.js:499:36)
    at errorBoundary.wrap.tabId (DashboardController.js:286:40)
    at ErrorBoundary.wrap (ErrorBoundary.js:41:17)
    at ErrorBoundary._handleError (ErrorBoundary.js:96:31)
    at async ErrorBoundary.wrap (ErrorBoundary.js:54:20)
    at async DashboardController._renderCurrentTab (DashboardController.js:258:13)
    at async DashboardController.switchTab (DashboardController.js:229:9)
renderDependencyGraph @ visualizations.js:1249
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
DashboardController.js:263 [Controller] _renderCurrentTab: Pre-render generation check: 12 vs 12
DashboardController.js:270 [Controller] _renderCurrentTab: Generation valid - proceeding with render
visualizations.js:1249 [Viz] renderDependencyGraph error: TypeError: packages.slice is not a function
    at createDependencyGraph (visualizations.js:197:34)
    at Object.renderDependencyGraph (visualizations.js:1246:13)
    at DashboardController._renderDependencies (DashboardController.js:499:36)
    at errorBoundary.wrap.tabId (DashboardController.js:286:40)
    at ErrorBoundary.wrap (ErrorBoundary.js:41:17)
    at ErrorBoundary._handleError (ErrorBoundary.js:96:31)
    at async ErrorBoundary.wrap (ErrorBoundary.js:54:20)
    at async ErrorBoundary._handleError (ErrorBoundary.js:96:20)
    at async ErrorBoundary.wrap (ErrorBoundary.js:54:20)
    at async DashboardController._renderCurrentTab (DashboardController.js:258:13)
renderDependencyGraph @ visualizations.js:1249
_renderDependencies @ DashboardController.js:499
errorBoundary.wrap.tabId @ DashboardController.js:286
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
DashboardController.js:263 [Controller] _renderCurrentTab: Pre-render generation check: 12 vs 12
DashboardController.js:270 [Controller] _renderCurrentTab: Generation valid - proceeding with render
visualizations.js:1249 [Viz] renderDependencyGraph error: TypeError: packages.slice is not a function
    at createDependencyGraph (visualizations.js:197:34)
    at Object.renderDependencyGraph (visualizations.js:1246:13)
    at DashboardController._renderDependencies (DashboardController.js:499:36)
    at errorBoundary.wrap.tabId (DashboardController.js:286:40)
    at ErrorBoundary.wrap (ErrorBoundary.js:41:17)
    at ErrorBoundary._handleError (ErrorBoundary.js:96:31)
    at async ErrorBoundary.wrap (ErrorBoundary.js:54:20)
    at async ErrorBoundary._handleError (ErrorBoundary.js:96:20)
    at async ErrorBoundary.wrap (ErrorBoundary.js:54:20)
    at async ErrorBoundary._handleError (ErrorBoundary.js:96:20)
renderDependencyGraph @ visualizations.js:1249
_renderDependencies @ DashboardController.js:499
errorBoundary.wrap.tabId @ DashboardController.js:286
wrap @ ErrorBoundary.js:41
_handleError @ ErrorBoundary.js:96
await in _handleError
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
bootstrap.js:25 [ErrorBoundary] tab_dependencies: TypeError: packages.slice is not a function
    at createDependencyGraph (visualizations.js:197:34)
    at Object.renderDependencyGraph (visualizations.js:1246:13)
    at DashboardController._renderDependencies (DashboardController.js:499:36)
    at errorBoundary.wrap.tabId (DashboardController.js:286:40)
    at ErrorBoundary.wrap (ErrorBoundary.js:41:17)
    at ErrorBoundary._handleError (ErrorBoundary.js:96:31)
    at async ErrorBoundary.wrap (ErrorBoundary.js:54:20)
    at async ErrorBoundary._handleError (ErrorBoundary.js:96:20)
    at async ErrorBoundary.wrap (ErrorBoundary.js:54:20)
    at async ErrorBoundary._handleError (ErrorBoundary.js:96:20)
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
_handleError @ ErrorBoundary.js:96
await in _handleError
wrap @ ErrorBoundary.js:54
await in wrap
_renderCurrentTab @ DashboardController.js:258
switchTab @ DashboardController.js:229
(anonymous) @ DashboardController.js:592
StateManager.js:60 [StateManager] setState called by: at DashboardController._renderCurrentTab (file:///D:/PROJECTS/CORTEX/company/dashboards/spa/js/controllers/DashboardController.js:298:31)
StateManager.js:61 [StateManager] Current generation: 12 → 13
StateManager.js:87 [StateManager] Notifying 1 subscribers...
DashboardController.js:771 [Controller] _onStateChange: State change detected
DashboardController.js:772 [Controller] _onStateChange: Old generation: 12
DashboardController.js:773 [Controller] _onStateChange: New generation: 13
DashboardController.js:774 [Controller] _onStateChange: Generation delta: 1
DashboardController.js:787 [Controller] _onStateChange: Handler complete (no state mutations)
StateManager.js:89 [StateManager] setState complete. New generation: 13



<html lang="en"><head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="CORTEX Repository Dashboard - Interactive Code Visualization with D3.js">
    <meta name="author" content="Asif Hussain">
    <title>Repository Dashboard | CORTEX</title>
    
    <!-- Favicon -->
    <link rel="icon" type="image/png" href="assets/images/cortex-logo-200.png">
    
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&amp;display=swap" rel="stylesheet">
    
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" rel="stylesheet" crossorigin="anonymous">
    
    <!-- D3.js -->
    <script src="https://d3js.org/d3.v7.min.js"></script>
    
    <!-- Custom Styles -->
    <link rel="stylesheet" href="css/styles.css">
</head>
<body>
    <!-- Animated Background -->
    <div class="bg-gradients"></div>
    
    <!-- Loading Overlay -->
    <div id="loading-overlay" class="loading-overlay hidden">
        <div class="loading-spinner">
            <div class="spinner-ring"></div>
            <div class="spinner-ring"></div>
        </div>
        <div class="loading-text">Loading Dashboard...</div>
    </div>
    
    <!-- Navigation -->
    <nav class="main-nav">
        <div class="nav-content">
            <a href="index.html" class="nav-brand">
                <img src="assets/images/cortex-logo-200.png" alt="CORTEX Logo" class="nav-logo">
                <div>
                    <div class="nav-title" id="repo-title">KSESSIONS</div>
                    <div class="nav-subtitle" id="repo-subtitle">User Authentication platform built with Python</div>
                </div>
            </a>
            
            <div class="status-badges">
                <span id="status-tdd" class="status-badge success">
                    <i class="fas fa-vial"></i> TDD Pass
                </span>
                <span id="status-git" class="status-badge success">
                    <i class="fab fa-git-alt"></i> Git Clean
                </span>
                <span id="status-errors" class="status-badge success"><i class="fas fa-check-circle"></i> 0 Errors</span>
                <button id="repo-selector-btn" class="btn" style="margin-left: 1rem;">
                    <i class="fas fa-th-large"></i> Change Repository
                </button>
            </div>
        </div>
    </nav>
    
    <!-- Repository Selector Modal -->
    <div id="modal-overlay" class="modal-overlay">
        <div class="modal-content">
            <div class="modal-header">
                <h2 class="modal-title">Select Repository</h2>
                <button id="modal-close" class="modal-close">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div id="repo-grid" class="repo-grid">
                <!-- Populated by app.js -->
            </div>
        </div>
    </div>
    
    <!-- Main Container -->
    <div class="container">
        <main class="main-content">
            
            <!-- Hero Metrics Section -->
            <section class="glass-card panel-cyan mb-lg">
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-icon"><i class="fas fa-heartbeat"></i></div>
                        <div class="metric-value" id="health-score">35</div>
                        <div class="metric-label">Health Score</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon"><i class="fas fa-code"></i></div>
                        <div class="metric-value" id="primary-lang">JavaScript</div>
                        <div class="metric-label">Primary Language</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon"><i class="fas fa-file-code"></i></div>
                        <div class="metric-value" id="total-files">150</div>
                        <div class="metric-label">Total Files</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-icon"><i class="fas fa-calendar"></i></div>
                        <div class="metric-value" id="last-updated">2026-02-08</div>
                        <div class="metric-label">Last Updated</div>
                    </div>
                </div>
            </section>
            
<!-- Data Integrity Banner (DIGEST ENH-D01, ENH-D08) -->
    <div id="integrity-banner" class="glass-card mb-lg" style="display: none; border-left: 4px solid var(--status-warning); background: rgba(245, 158, 11, 0.05);">
        <div class="section-header">
            <div class="section-icon" style="background: rgba(245, 158, 11, 0.2);"><i class="fas fa-exclamation-triangle" style="color: var(--status-warning);"></i></div>
            <div>
                <h2 class="section-title" style="color: var(--status-warning);">Data Integrity Warnings</h2>
                <p class="section-subtitle">Detected contradictions require attention</p>
            </div>
        </div>
        <div id="integrity-issues" style="margin-top: 1rem;">
            <!-- Populated by app.js -->
        </div>
    </div>
    
    <!-- Tab Navigation -->
            <nav id="tab-nav" class="tab-nav">
            <button class="tab-btn" data-tab="overview">
                <i class="fas fa-chart-line"></i>
                Overview
            </button>
        
            <button class="tab-btn" data-tab="architecture">
                <i class="fas fa-sitemap"></i>
                Architecture
            <div id="arch-diagram" style="margin-bottom: 20px;"><svg width="800" height="400" viewBox="0 0 800 400" preserveAspectRatio="xMidYMid meet"><g><line stroke="rgba(123, 97, 255, 0.3)" stroke-width="1.650166976069412" x1="427.21254119422343" y1="194.6913122517525" x2="487.537496664253" y2="142.1645042191423"></line><line stroke="rgba(123, 97, 255, 0.3)" stroke-width="1.8291049931490266" x1="427.21254119422343" y1="194.6913122517525" x2="382.1702631833159" y2="325.71569637957697"></line><line stroke="rgba(123, 97, 255, 0.3)" stroke-width="1.5570854652666053" x1="427.21254119422343" y1="194.6913122517525" x2="336.2091532581794" y2="90.20328189574236"></line><line stroke="rgba(123, 97, 255, 0.3)" stroke-width="1.0200158016576597" x1="427.21254119422343" y1="194.6913122517525" x2="502.8597521688206" y2="220.6834731766816"></line><line stroke="rgba(123, 97, 255, 0.3)" stroke-width="1.651220299325362" x1="427.21254119422343" y1="194.6913122517525" x2="291.20102599880676" y2="221.22997911475994"></line><line stroke="rgba(123, 97, 255, 0.3)" stroke-width="1.8239678858540056" x1="366.8654763606454" y1="247.20990192606143" x2="487.537496664253" y2="142.1645042191423"></line><line stroke="rgba(123, 97, 255, 0.3)" stroke-width="1.4858836008160563" x1="366.8654763606454" y1="247.20990192606143" x2="382.1702631833159" y2="325.71569637957697"></line><line stroke="rgba(123, 97, 255, 0.3)" stroke-width="1.1878448101404422" x1="366.8654763606454" y1="247.20990192606143" x2="336.2091532581794" y2="90.20328189574236"></line><line stroke="rgba(123, 97, 255, 0.3)" stroke-width="1.8009381770800188" x1="366.8654763606454" y1="247.20990192606143" x2="502.8597521688206" y2="220.6834731766816"></line><line stroke="rgba(123, 97, 255, 0.3)" stroke-width="1.3232354289713069" x1="366.8654763606454" y1="247.20990192606143" x2="291.20102599880676" y2="221.22997911475994"></line><line stroke="rgba(123, 97, 255, 0.3)" stroke-width="1.6846056789850405" x1="411.8817640559522" y1="116.18244012345438" x2="487.537496664253" y2="142.1645042191423"></line><line stroke="rgba(123, 97, 255, 0.3)" stroke-width="1.5973064009622204" x1="411.8817640559522" y1="116.18244012345438" x2="382.1702631833159" y2="325.71569637957697"></line><line stroke="rgba(123, 97, 255, 0.3)" stroke-width="1.7962834992283105" x1="411.8817640559522" y1="116.18244012345438" x2="336.2091532581794" y2="90.20328189574236"></line><line stroke="rgba(123, 97, 255, 0.3)" stroke-width="1.0013801690845177" x1="411.8817640559522" y1="116.18244012345438" x2="502.8597521688206" y2="220.6834731766816"></line><line stroke="rgba(123, 97, 255, 0.3)" stroke-width="1.6594287801694214" x1="411.8817640559522" y1="116.18244012345438" x2="291.20102599880676" y2="221.22997911475994"></line><line stroke="rgba(123, 97, 255, 0.3)" stroke-width="1.7197974397877336" x1="442.51799162064515" y1="273.2014067804628" x2="487.537496664253" y2="142.1645042191423"></line><line stroke="rgba(123, 97, 255, 0.3)" stroke-width="1.8955920514104847" x1="442.51799162064515" y1="273.2014067804628" x2="382.1702631833159" y2="325.71569637957697"></line><line stroke="rgba(123, 97, 255, 0.3)" stroke-width="1.7965630744988221" x1="442.51799162064515" y1="273.2014067804628" x2="336.2091532581794" y2="90.20328189574236"></line><line stroke="rgba(123, 97, 255, 0.3)" stroke-width="1.5776884197060972" x1="442.51799162064515" y1="273.2014067804628" x2="502.8597521688206" y2="220.6834731766816"></line><line stroke="rgba(123, 97, 255, 0.3)" stroke-width="1.0946185364172794" x1="442.51799162064515" y1="273.2014067804628" x2="291.20102599880676" y2="221.22997911475994"></line><line stroke="rgba(123, 97, 255, 0.3)" stroke-width="1.1898403336745824" x1="351.54402700303365" y1="168.71727422583618" x2="487.537496664253" y2="142.1645042191423"></line><line stroke="rgba(123, 97, 255, 0.3)" stroke-width="1.85403820837745" x1="351.54402700303365" y1="168.71727422583618" x2="382.1702631833159" y2="325.71569637957697"></line><line stroke="rgba(123, 97, 255, 0.3)" stroke-width="1.2767526641562008" x1="351.54402700303365" y1="168.71727422583618" x2="336.2091532581794" y2="90.20328189574236"></line><line stroke="rgba(123, 97, 255, 0.3)" stroke-width="1.7226864718631736" x1="351.54402700303365" y1="168.71727422583618" x2="502.8597521688206" y2="220.6834731766816"></line><line stroke="rgba(123, 97, 255, 0.3)" stroke-width="1.9665153523653613" x1="351.54402700303365" y1="168.71727422583618" x2="291.20102599880676" y2="221.22997911475994"></line></g><g><g transform="translate(427.21254119422343, 194.6913122517525)"><circle r="25" fill="#00d4ff" opacity="0.8" style="cursor: pointer;"></circle><text dy="4" text-anchor="middle" style="fill: rgb(255, 255, 255); font-size: 11px; font-weight: 600; pointer-events: none;">Sessions</text></g><g transform="translate(366.8654763606454, 247.20990192606143)"><circle r="25" fill="#00d4ff" opacity="0.8" style="cursor: pointer;"></circle><text dy="4" text-anchor="middle" style="fill: rgb(255, 255, 255); font-size: 11px; font-weight: 600; pointer-events: none;">Audio</text></g><g transform="translate(411.8817640559522, 116.18244012345438)"><circle r="25" fill="#00d4ff" opacity="0.8" style="cursor: pointer;" stroke="none" stroke-width="2"></circle><text dy="4" text-anchor="middle" style="fill: rgb(255, 255, 255); font-size: 11px; font-weight: 600; pointer-events: none;">Transcripts</text></g><g transform="translate(442.51799162064515, 273.2014067804628)"><circle r="25" fill="#00d4ff" opacity="0.8" style="cursor: pointer;"></circle><text dy="4" text-anchor="middle" style="fill: rgb(255, 255, 255); font-size: 11px; font-weight: 600; pointer-events: none;">Authentica...</text></g><g transform="translate(351.54402700303365, 168.71727422583618)"><circle r="25" fill="#00d4ff" opacity="0.8" style="cursor: pointer;"></circle><text dy="4" text-anchor="middle" style="fill: rgb(255, 255, 255); font-size: 11px; font-weight: 600; pointer-events: none;">Users</text></g><g transform="translate(487.537496664253, 142.1645042191423)"><circle r="18" fill="#7b61ff" opacity="0.8" style="cursor: pointer;" stroke="none" stroke-width="2"></circle><text dy="4" text-anchor="middle" style="fill: rgb(255, 255, 255); font-size: 11px; font-weight: 600; pointer-events: none;">Etymology</text></g><g transform="translate(382.1702631833159, 325.71569637957697)"><circle r="18" fill="#7b61ff" opacity="0.8" style="cursor: pointer;"></circle><text dy="4" text-anchor="middle" style="fill: rgb(255, 255, 255); font-size: 11px; font-weight: 600; pointer-events: none;">Arabic</text></g><g transform="translate(336.2091532581794, 90.20328189574236)"><circle r="18" fill="#7b61ff" opacity="0.8" style="cursor: pointer;" stroke="none" stroke-width="2"></circle><text dy="4" text-anchor="middle" style="fill: rgb(255, 255, 255); font-size: 11px; font-weight: 600; pointer-events: none;">Search</text></g><g transform="translate(502.8597521688206, 220.6834731766816)"><circle r="18" fill="#7b61ff" opacity="0.8" style="cursor: pointer;"></circle><text dy="4" text-anchor="middle" style="fill: rgb(255, 255, 255); font-size: 11px; font-weight: 600; pointer-events: none;">Data Manag...</text></g><g transform="translate(291.20102599880676, 221.22997911475994)"><circle r="18" fill="#7b61ff" opacity="0.8" style="cursor: pointer;"></circle><text dy="4" text-anchor="middle" style="fill: rgb(255, 255, 255); font-size: 11px; font-weight: 600; pointer-events: none;">Tools</text></g></g></svg></div><div id="arch-components" style="margin-bottom: 20px;"><svg width="600" height="400" viewBox="0 0 600 400" preserveAspectRatio="xMidYMid meet"><g transform="translate(0, 40)"><rect width="136" height="77" fill="#f7df1e" opacity="0.7" rx="4" style="cursor: pointer; transition: 0.2s;" stroke="none" stroke-width="2"></rect><text x="6" y="16" style="fill: rgb(255, 255, 255); font-size: 11px; font-weight: 500; pointer-events: none;">javascript...</text></g><g transform="translate(0, 119)"><rect width="136" height="74" fill="#f7df1e" opacity="0.7" rx="4" style="cursor: pointer; transition: 0.2s;" stroke="none" stroke-width="2"></rect><text x="6" y="16" style="fill: rgb(255, 255, 255); font-size: 11px; font-weight: 500; pointer-events: none;">javascript...</text></g><g transform="translate(0, 195)"><rect width="136" height="74" fill="#f7df1e" opacity="0.7" rx="4" style="cursor: pointer; transition: 0.2s;" stroke="none" stroke-width="2"></rect><text x="6" y="16" style="fill: rgb(255, 255, 255); font-size: 11px; font-weight: 500; pointer-events: none;">javascript...</text></g><g transform="translate(0, 271)"><rect width="136" height="66" fill="#f7df1e" opacity="0.7" rx="4" style="cursor: pointer; transition: 0.2s;" stroke="none" stroke-width="2"></rect><text x="6" y="16" style="fill: rgb(255, 255, 255); font-size: 11px; font-weight: 500; pointer-events: none;">javascript...</text></g><g transform="translate(0, 339)"><rect width="136" height="61" fill="#f7df1e" opacity="0.7" rx="4" style="cursor: pointer; transition: 0.2s;"></rect><text x="6" y="16" style="fill: rgb(255, 255, 255); font-size: 11px; font-weight: 500; pointer-events: none;">javascript...</text></g><g transform="translate(138, 40)"><rect width="94" height="69" fill="#f7df1e" opacity="0.7" rx="4" style="cursor: pointer; transition: 0.2s;"></rect><text x="6" y="16" style="fill: rgb(255, 255, 255); font-size: 11px; font-weight: 500; pointer-events: none;">javascript...</text></g><g transform="translate(234, 40)"><rect width="74" height="69" fill="#f7df1e" opacity="0.7" rx="4" style="cursor: pointer; transition: 0.2s;"></rect><text x="6" y="16" style="fill: rgb(255, 255, 255); font-size: 11px; font-weight: 500; pointer-events: none;">javascript...</text></g><g transform="translate(310, 40)"><rect width="54" height="69" fill="#f7df1e" opacity="0.7" rx="4" style="cursor: pointer; transition: 0.2s;"></rect><text x="6" y="16" style="fill: rgb(255, 255, 255); font-size: 11px; font-weight: 500; pointer-events: none;">javascript...</text></g><g transform="translate(370, 40)"><rect width="47" height="62" fill="#6b7280" opacity="0.7" rx="4" style="cursor: pointer; transition: 0.2s;"></rect></g><g transform="translate(419, 40)"><rect width="44" height="62" fill="#6b7280" opacity="0.7" rx="4" style="cursor: pointer; transition: 0.2s;"></rect></g><g transform="translate(465, 40)"><rect width="30" height="62" fill="#6b7280" opacity="0.7" rx="4" style="cursor: pointer; transition: 0.2s;"></rect></g><g transform="translate(370, 104)"><rect width="24" height="38" fill="#6b7280" opacity="0.7" rx="4" style="cursor: pointer; transition: 0.2s;"></rect></g><g transform="translate(370, 144)"><rect width="24" height="35" fill="#6b7280" opacity="0.7" rx="4" style="cursor: pointer; transition: 0.2s;"></rect></g><g transform="translate(370, 181)"><rect width="24" height="29" fill="#6b7280" opacity="0.7" rx="4" style="cursor: pointer; transition: 0.2s;"></rect></g><g transform="translate(501, 40)"><rect width="74" height="67" fill="#e34c26" opacity="0.7" rx="4" style="cursor: pointer; transition: 0.2s;"></rect><text x="6" y="16" style="fill: rgb(255, 255, 255); font-size: 11px; font-weight: 500; pointer-events: none;">html-5.html</text></g><g transform="translate(577, 40)"><rect width="15" height="67" fill="#e34c26" opacity="0.7" rx="4" style="cursor: pointer; transition: 0.2s;"></rect></g><g transform="translate(501, 109)"><rect width="38" height="15" fill="#e34c26" opacity="0.7" rx="4" style="cursor: pointer; transition: 0.2s;"></rect></g><g transform="translate(541, 109)"><rect width="29" height="15" fill="#e34c26" opacity="0.7" rx="4" style="cursor: pointer; transition: 0.2s;"></rect></g><g transform="translate(572, 109)"><rect width="20" height="15" fill="#e34c26" opacity="0.7" rx="4" style="cursor: pointer; transition: 0.2s;"></rect></g><g transform="translate(370, 232)"><rect width="53" height="47" fill="#3572A5" opacity="0.7" rx="4" style="cursor: pointer; transition: 0.2s;"></rect><text x="6" y="16" style="fill: rgb(255, 255, 255); font-size: 11px; font-weight: 500; pointer-events: none;">python-4.py</text></g><g transform="translate(370, 281)"><rect width="53" height="31" fill="#3572A5" opacity="0.7" rx="4" style="cursor: pointer; transition: 0.2s;"></rect><text x="6" y="16" style="fill: rgb(255, 255, 255); font-size: 11px; font-weight: 500; pointer-events: none;">python-1.py</text></g><g transform="translate(425, 232)"><rect width="13" height="68" fill="#3572A5" opacity="0.7" rx="4" style="cursor: pointer; transition: 0.2s;"></rect></g><g transform="translate(425, 302)"><rect width="13" height="10" fill="#3572A5" opacity="0.7" rx="4" style="cursor: pointer; transition: 0.2s;"></rect></g><g transform="translate(370, 334)"><rect width="55" height="36" fill="#563d7c" opacity="0.7" rx="4" style="cursor: pointer; transition: 0.2s;" stroke="none" stroke-width="2"></rect><text x="6" y="16" style="fill: rgb(255, 255, 255); font-size: 11px; font-weight: 500; pointer-events: none;">css-1.css</text></g><g transform="translate(370, 372)"><rect width="55" height="28" fill="#563d7c" opacity="0.7" rx="4" style="cursor: pointer; transition: 0.2s;"></rect><text x="6" y="16" style="fill: rgb(255, 255, 255); font-size: 11px; font-weight: 500; pointer-events: none;">css-2.css</text></g><g transform="translate(427, 334)"><rect width="11" height="66" fill="#563d7c" opacity="0.7" rx="4" style="cursor: pointer; transition: 0.2s;" stroke="none" stroke-width="2"></rect></g><g transform="translate(514, 232)"><rect width="55" height="47" fill="#178600" opacity="0.7" rx="4" style="cursor: pointer; transition: 0.2s;"></rect><text x="6" y="16" style="fill: rgb(255, 255, 255); font-size: 11px; font-weight: 500; pointer-events: none;">c#-3.cs</text></g><g transform="translate(571, 232)"><rect width="21" height="47" fill="#178600" opacity="0.7" rx="4" style="cursor: pointer; transition: 0.2s;"></rect></g><g transform="translate(514, 281)"><rect width="6" height="62" fill="#178600" opacity="0.7" rx="4" style="cursor: pointer; transition: 0.2s;"></rect></g><g transform="translate(514, 365)"><rect width="19" height="35" fill="#e38c00" opacity="0.7" rx="4" style="cursor: pointer; transition: 0.2s;"></rect></g><g transform="translate(561, 365)"><rect width="15" height="28" fill="#3178c6" opacity="0.7" rx="4" style="cursor: pointer; transition: 0.2s;"></rect></g><g transform="translate(561, 407)"><rect width="26" height="0" fill="#777BB4" opacity="0.7" rx="4" style="cursor: pointer; transition: 0.2s;"></rect></g><text class="category-label" x="6" y="34" style="fill: rgb(255, 255, 255); font-size: 12px; font-weight: 700; pointer-events: none;">JavaScript</text><text class="category-label" x="376" y="34" style="fill: rgb(255, 255, 255); font-size: 12px; font-weight: 700; pointer-events: none;">Config</text><text class="category-label" x="507" y="34" style="fill: rgb(255, 255, 255); font-size: 12px; font-weight: 700; pointer-events: none;">HTML</text><text class="category-label" x="376" y="226" style="fill: rgb(255, 255, 255); font-size: 12px; font-weight: 700; pointer-events: none;">Python</text><text class="category-label" x="376" y="328" style="fill: rgb(255, 255, 255); font-size: 12px; font-weight: 700; pointer-events: none;">CSS</text><text class="category-label" x="520" y="226" style="fill: rgb(255, 255, 255); font-size: 12px; font-weight: 700; pointer-events: none;">C#</text><text class="category-label" x="520" y="359" style="fill: rgb(255, 255, 255); font-size: 12px; font-weight: 700; pointer-events: none;">SQL</text><text class="category-label" x="567" y="359" style="fill: rgb(255, 255, 255); font-size: 12px; font-weight: 700; pointer-events: none;">TypeScript</text><text class="category-label" x="567" y="409" style="fill: rgb(255, 255, 255); font-size: 12px; font-weight: 700; pointer-events: none;">PHP</text></svg></div><div id="arch-dependencies" style="margin-bottom: 20px;"></div></button>
        
            <button class="tab-btn " data-tab="quality">
                <i class="fas fa-medal"></i>
                Quality
            </button>
        
            <button class="tab-btn" data-tab="security">
                <i class="fas fa-shield-alt"></i>
                Security
            <div id="security-donut-chart" style="margin-bottom: 20px;"><svg width="300" height="300" viewBox="0 0 300 300" preserveAspectRatio="xMidYMid meet"><g transform="translate(150, 150)"><circle r="130" fill="rgba(16, 185, 129, 0.1)" stroke="#10b981" stroke-width="3"></circle><text text-anchor="middle" dy="-10px" style="fill: rgb(16, 185, 129); font-size: 48px;">✓</text><text text-anchor="middle" dy="30px" style="fill: rgb(160, 166, 192); font-size: 14px;">No Vulnerabilities</text></g></svg></div><div id="security-overview" style="margin-bottom: 20px;"></div></button>
        
            <button class="tab-btn active" data-tab="dependencies">
                <i class="fas fa-cubes"></i>
                Dependencies
            <div id="dependency-visualization" style="margin-bottom: 20px;"></div></button>
        
            <button class="tab-btn " data-tab="usecases">
                <i class="fas fa-lightbulb"></i>
                Use Cases
            </button>
        </nav>
            
            <!-- Tab Content: Overview -->
            <div id="tab-overview" class="tab-content">
                <div class="glass-card panel-purple mb-lg">
                    <div class="section-header">
                        <div class="section-icon"><i class="fas fa-info-circle"></i></div>
                        <div>
                            <h2 class="section-title">Repository Overview</h2>
                            <p class="section-subtitle">Business context and key findings</p>
                        </div>
                    </div>
                    <div id="overview-summary" style="line-height: 1.8; margin-bottom: 1.5rem;">&lt;strong&gt;KSESSIONS&lt;/strong&gt; is a comprehensive .NET Framework 4.8 application for managing educational Islamic sessions, featuring audio recordings with transcripts, etymology analysis, and Arabic linguistic tools. The application provides user authentication, data management, search &amp; discovery capabilities.</div>
                    <h3 style="font-size: 1.1rem; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                        <i class="fas fa-lightbulb" style="color: var(--accent-primary);"></i>
                        Key Findings
                    </h3>
                    <ul id="key-findings" style="list-style: none; padding: 0;">
                        <!-- Populated by app.js -->
                    </ul>
                </div>
                
<!-- Health Gauge Visualization with Explainability (DIGEST ENH-D02) -->
        <div class="viz-container">
            <div class="viz-header">
                <h3 class="viz-title"><i class="fas fa-tachometer-alt"></i> Health Score Gauge</h3>
                <button class="btn" onclick="toggleExplainability('health-explainer')" style="font-size: 0.85rem; padding: 0.4rem 0.8rem;">
                    <i class="fas fa-question-circle"></i> How is this computed?
                </button>
            </div>
            <div id="health-explainer" class="explainability-panel" style="display: none; background: rgba(123, 97, 255, 0.05); border-left: 3px solid var(--accent-primary); padding: 1rem; margin-bottom: 1rem; border-radius: 8px;">
                <h4 style="font-size: 0.95rem; margin-bottom: 0.5rem;"><i class="fas fa-calculator"></i> Formula</h4>
                <code style="display: block; background: rgba(0, 0, 0, 0.2); padding: 0.5rem; border-radius: 4px; font-size: 0.85rem;">
                    health_score = (quality * 0.4) + (security * 0.3) + (coverage * 0.2) + (docs * 0.1)
                </code>
                <p style="margin-top: 0.5rem; font-size: 0.85rem; line-height: 1.5;">
                    <strong>Sources:</strong> Quality metrics, security scan, test coverage, documentation completeness.
                    <br><strong>Confidence:</strong> <span id="health-confidence">85%</span> (varies based on data completeness)
                </p>
                    </div>
                    <div id="viz-health" class="viz-canvas" style="min-height: 220px;"></div>
                </div>
            </div>
            
            <!-- Tab Content: Architecture -->
            <div id="tab-architecture" class="tab-content">
                <div class="glass-card panel-emerald mb-lg">
                    <div class="section-header">
                        <div class="section-icon"><i class="fas fa-sitemap"></i></div>
                        <div>
                            <h2 class="section-title">Code Architecture</h2>
                            <p class="section-subtitle">Language distribution, file structure, and domain concepts</p>
                        </div>
                    </div>
                </div>
                
                <!-- Domain Concept Map (DIGEST ENH-D05) -->
                <div class="viz-container mb-lg">
                    <div class="viz-header">
                        <h3 class="viz-title"><i class="fas fa-project-diagram"></i> Domain Concept Map</h3>
                        <button class="btn" onclick="toggleExplainability('domain-explainer')" style="font-size: 0.85rem; padding: 0.4rem 0.8rem;">
                            <i class="fas fa-question-circle"></i> How is this generated?
                        </button>
                    </div>
                    <div id="domain-explainer" class="explainability-panel" style="display: none; background: rgba(16, 185, 129, 0.05); border-left: 3px solid var(--status-success); padding: 1rem; margin-bottom: 1rem; border-radius: 8px;">
                        <h4 style="font-size: 0.95rem; margin-bottom: 0.5rem;"><i class="fas fa-brain"></i> Inference Method</h4>
                        <p style="font-size: 0.85rem; line-height: 1.5;">
                            Domain concepts extracted from: <strong>business summary NLP</strong>, code identifiers, documentation, and naming patterns.
                            <br><strong>Confidence:</strong> <span id="domain-confidence">72%</span> (based on signal strength)
                        </p>
                    </div>
                    <div id="viz-domain" class="viz-canvas" style="min-height: 400px;"></div>
                    <div class="viz-legend">
                        <div class="legend-item">
                            <span class="legend-dot" style="background: #00d4ff;"></span>
                            <span>Core Domain</span>
                        </div>
                        <div class="legend-item">
                            <span class="legend-dot" style="background: #7b61ff;"></span>
                            <span>Supporting</span>
                        </div>
                        <div class="legend-item">
                            <span class="legend-dot" style="background: #10b981;"></span>
                            <span>Integration Point</span>
                        </div>
                    </div>
                </div>
                
                <!-- Language Sunburst -->
                <div class="viz-container">
                    <div class="viz-header">
                        <h3 class="viz-title"><i class="fas fa-chart-pie"></i> Language Distribution</h3>
                    </div>
                    <div id="viz-languages" class="viz-canvas" style="min-height: 400px;"><svg width="400" height="400" viewBox="0 0 400 400" preserveAspectRatio="xMidYMid meet"><g transform="translate(200, 200)"><path fill="#f7df1e" d="M1,-197.997A198,198,0,1,1,-134.053,145.718L-40.107,44.626A60,60,0,1,0,1,-59.992Z" style="cursor: pointer; transition: 0.3s; filter: brightness(1); transform: scale(1);"></path><path fill="#6b7280" d="M-135.518,144.356A198,198,0,0,1,-196.262,26.175L-59.377,8.622A60,60,0,0,0,-41.572,43.264Z" style="cursor: pointer; transition: 0.3s;"></path><path fill="#e34c26" d="M-196.517,24.191A198,198,0,0,1,-184.055,-72.991L-56.027,-21.469A60,60,0,0,0,-59.632,6.638Z" style="cursor: pointer; transition: 0.3s;"></path><path fill="#3572A5" d="M-183.309,-74.846A198,198,0,0,1,-140.888,-139.12L-43.18,-41.659A60,60,0,0,0,-55.281,-23.324Z" style="cursor: pointer; transition: 0.3s;"></path><path fill="#563d7c" d="M-139.476,-140.536A198,198,0,0,1,-84.684,-178.977L-26.29,-53.934A60,60,0,0,0,-41.768,-43.075Z" style="cursor: pointer; transition: 0.3s;"></path><path fill="#178600" d="M-82.872,-179.823A198,198,0,0,1,-26.175,-196.262L-8.622,-59.377A60,60,0,0,0,-24.478,-54.78Z" style="cursor: pointer; transition: 0.3s;"></path><path fill="#e38c00" d="M-24.191,-196.517A198,198,0,0,1,-11.494,-197.666L-4.179,-59.854A60,60,0,0,0,-6.638,-59.632Z" style="cursor: pointer; transition: 0.3s; filter: brightness(1); transform: scale(1);"></path><path fill="#3178c6" d="M-9.497,-197.772A198,198,0,0,1,-1.5,-197.994L-1.151,-59.989A60,60,0,0,0,-2.181,-59.96Z" style="cursor: pointer; transition: 0.3s;"></path><path fill="#777BB4" d="M-0.25,-198L-0.076,-60Z" style="cursor: pointer; transition: 0.3s;"></path><text text-anchor="middle" dy="-0.5em" style="fill: rgb(255, 255, 255); font-size: 24px; font-weight: 700;">4,976</text><text text-anchor="middle" dy="1.2em" style="fill: rgb(160, 166, 192); font-size: 12px; text-transform: uppercase; letter-spacing: 0.1em;">Total Lines</text></g></svg></div>
                    <div class="viz-legend">
                        <div class="legend-item">
                            <span class="legend-dot" style="background: #f7df1e;"></span>
                            <span>JavaScript</span>
                        </div>
                        <div class="legend-item">
                            <span class="legend-dot" style="background: #3178c6;"></span>
                            <span>TypeScript</span>
                        </div>
                        <div class="legend-item">
                            <span class="legend-dot" style="background: #3572A5;"></span>
                            <span>Python</span>
                        </div>
                        <div class="legend-item">
                            <span class="legend-dot" style="background: #178600;"></span>
                            <span>C#</span>
                        </div>
                        <div class="legend-item">
                            <span class="legend-dot" style="background: #e34c26;"></span>
                            <span>HTML</span>
                        </div>
                        <div class="legend-item">
                            <span class="legend-dot" style="background: #563d7c;"></span>
                            <span>CSS</span>
                        </div>
                    </div>
                </div>
                
                <!-- File Treemap -->
                <div class="viz-container">
                    <div class="viz-header">
                        <h3 class="viz-title"><i class="fas fa-folder-tree"></i> File Structure Treemap</h3>
                    </div>
                    <div id="viz-files" class="viz-canvas" style="min-height: 400px;"></div>
                </div>
            </div>
            
            <!-- Tab Content: Quality -->
            <div id="tab-quality" class="tab-content">
                <div class="glass-card panel-purple mb-lg">
                    <div class="section-header">
                        <div class="section-icon"><i class="fas fa-medal"></i></div>
                        <div>
                            <h2 class="section-title">Code Quality</h2>
                            <p class="section-subtitle">Quality metrics and analysis</p>
                        </div>
                    </div>
                    
                    <div class="metrics-grid" style="margin-top: 1.5rem;">
                        <div class="metric-card">
                            <div class="metric-icon" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.1));"><i class="fas fa-vial" style="color: var(--status-success);"></i></div>
                            <div class="metric-value" style="color: var(--status-success);">0%</div>
                            <div class="metric-label">Test Coverage</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-icon" style="background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(123, 97, 255, 0.2));"><i class="fas fa-clone"></i></div>
                            <div class="metric-value">0</div>
                            <div class="metric-label">Code Duplications</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-icon" style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(245, 158, 11, 0.1));"><i class="fas fa-code-branch" style="color: var(--status-warning);"></i></div>
                            <div class="metric-value">N/A</div>
                            <div class="metric-label">Complexity</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-icon" style="background: linear-gradient(135deg, rgba(123, 97, 255, 0.2), rgba(0, 212, 255, 0.2));"><i class="fas fa-file-alt"></i></div>
                            <div class="metric-value">N/A</div>
                            <div class="metric-label">Documentation</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Tab Content: Security -->
            <div id="tab-security" class="tab-content">
                <div class="glass-card panel-cyan mb-lg">
                    <div class="section-header">
                        <div class="section-icon"><i class="fas fa-shield-alt"></i></div>
                        <div>
                            <h2 class="section-title">Security Analysis</h2>
                            <p class="section-subtitle">Vulnerability scanning and compliance</p>
                        </div>
                    </div>
                    
                    <!-- Security Stats Grid -->
                    <div class="security-grid" style="margin-top: 1.5rem;">
                        <div class="security-stat critical">
                            <div class="security-count">0</div>
                            <div class="metric-label">Critical</div>
                        </div>
                        <div class="security-stat high">
                            <div class="security-count">0</div>
                            <div class="metric-label">High</div>
                        </div>
                        <div class="security-stat medium">
                            <div class="security-count">0</div>
                            <div class="metric-label">Medium</div>
                        </div>
                        <div class="security-stat low">
                            <div class="security-count">0</div>
                            <div class="metric-label">Low</div>
                        </div>
                    </div>
                </div>
                
                <!-- Security Donut -->
                <div class="viz-container">
                    <div class="viz-header">
                        <h3 class="viz-title"><i class="fas fa-chart-pie"></i> Vulnerability Distribution</h3>
                    </div>
                    <div id="viz-security" class="viz-canvas" style="min-height: 300px;"></div>
                </div>
                
                <!-- Vulnerability List -->
                <div class="glass-card panel-purple">
                    <h3 style="margin-bottom: 1rem;">
                        <i class="fas fa-list" style="color: var(--accent-primary); margin-right: 0.5rem;"></i>
                        Vulnerability Details
                    </h3>
                    <div id="sec-vuln-list">
                    <div class="empty-state">
                        <i class="fas fa-shield-alt"></i>
                        <h3 style="color: var(--status-success);">All Clear!</h3>
                        <p>No security vulnerabilities detected.</p>
                    </div>
                </div>
                </div>
            </div>
            
            <!-- Tab Content: Dependencies -->
            <div id="tab-dependencies" class="tab-content active">
                <div class="glass-card panel-emerald mb-lg">
                    <div class="section-header">
                        <div class="section-icon"><i class="fas fa-cubes"></i></div>
                        <div>
                            <h2 class="section-title">Dependency Analysis</h2>
                            <p class="section-subtitle">Package dependencies and relationships</p>
                        </div>
                    </div>
                </div>
                
                <!-- Dependency Graph -->
                <div class="viz-container">
                    <div class="viz-header">
                        <h3 class="viz-title"><i class="fas fa-project-diagram"></i> Dependency Network</h3>
                    </div>
                    <div id="viz-deps" class="viz-canvas" style="min-height: 500px;"></div>
                    <div class="viz-legend">
                        <div class="legend-item">
                            <span class="legend-dot" style="background: #00d4ff;"></span>
                            <span>Direct Dependencies</span>
                        </div>
                        <div class="legend-item">
                            <span class="legend-dot" style="background: #7b61ff;"></span>
                            <span>Transitive Dependencies</span>
                        </div>
                    </div>
                </div>
                
                <!-- Dependency Table -->
                <div class="glass-card panel-purple">
                    <h3 style="margin-bottom: 1rem;">
                        <i class="fas fa-table" style="color: var(--accent-primary); margin-right: 0.5rem;"></i>
                        Package List
                    </h3>
                    <div id="dep-table" style="overflow-x: auto;">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Package</th>
                            <th>Version</th>
                            <th>Type</th>
                            <th>License</th>
                        </tr>
                    </thead>
                    <tbody>
                    <tr>
                        <td style="font-family: var(--font-mono);">eslint</td>
                        <td style="font-family: var(--font-mono);">8.56.0</td>
                        <td>
                            <span class="badge badge-info">
                                Direct
                            </span>
                        </td>
                        <td>MIT</td>
                    </tr>
                
                    <tr>
                        <td style="font-family: var(--font-mono);">prettier</td>
                        <td style="font-family: var(--font-mono);">3.1.1</td>
                        <td>
                            <span class="badge badge-info">
                                Direct
                            </span>
                        </td>
                        <td>MIT</td>
                    </tr>
                
                    <tr>
                        <td style="font-family: var(--font-mono);">mocha</td>
                        <td style="font-family: var(--font-mono);">10.2.0</td>
                        <td>
                            <span class="badge badge-info">
                                Direct
                            </span>
                        </td>
                        <td>MIT</td>
                    </tr>
                
                    <tr>
                        <td style="font-family: var(--font-mono);">chai</td>
                        <td style="font-family: var(--font-mono);">4.3.10</td>
                        <td>
                            <span class="badge badge-info">
                                Direct
                            </span>
                        </td>
                        <td>MIT</td>
                    </tr>
                
                    <tr>
                        <td style="font-family: var(--font-mono);">typescript</td>
                        <td style="font-family: var(--font-mono);">4.7.4</td>
                        <td>
                            <span class="badge badge-info">
                                Direct
                            </span>
                        </td>
                        <td>Apache-2.0</td>
                    </tr>
                
                    <tr>
                        <td style="font-family: var(--font-mono);">rimraf</td>
                        <td style="font-family: var(--font-mono);">5.0.5</td>
                        <td>
                            <span class="badge badge-success">
                                Transitive
                            </span>
                        </td>
                        <td>ISC</td>
                    </tr>
                
                    <tr>
                        <td style="font-family: var(--font-mono);">axios</td>
                        <td style="font-family: var(--font-mono);">0.21.1</td>
                        <td>
                            <span class="badge badge-success">
                                Transitive
                            </span>
                        </td>
                        <td>MIT</td>
                    </tr>
                
                    <tr>
                        <td style="font-family: var(--font-mono);">lodash</td>
                        <td style="font-family: var(--font-mono);">4.17.15</td>
                        <td>
                            <span class="badge badge-success">
                                Transitive
                            </span>
                        </td>
                        <td>MIT</td>
                    </tr>
                
                    <tr>
                        <td style="font-family: var(--font-mono);">react</td>
                        <td style="font-family: var(--font-mono);">16.14.0</td>
                        <td>
                            <span class="badge badge-success">
                                Transitive
                            </span>
                        </td>
                        <td>MIT</td>
                    </tr>
                
                    <tr>
                        <td style="font-family: var(--font-mono);">semver</td>
                        <td style="font-family: var(--font-mono);">7.1.3</td>
                        <td>
                            <span class="badge badge-success">
                                Transitive
                            </span>
                        </td>
                        <td>ISC</td>
                    </tr>
                
                    <tr>
                        <td style="font-family: var(--font-mono);">@babel/core</td>
                        <td style="font-family: var(--font-mono);">7.10.3</td>
                        <td>
                            <span class="badge badge-success">
                                Transitive
                            </span>
                        </td>
                        <td>MIT</td>
                    </tr>
                
                    <tr>
                        <td style="font-family: var(--font-mono);">@babel/preset-env</td>
                        <td style="font-family: var(--font-mono);">7.10.3</td>
                        <td>
                            <span class="badge badge-success">
                                Transitive
                            </span>
                        </td>
                        <td>MIT</td>
                    </tr>
                
                    <tr>
                        <td style="font-family: var(--font-mono);">nyc</td>
                        <td style="font-family: var(--font-mono);">17.1.0</td>
                        <td>
                            <span class="badge badge-success">
                                Transitive
                            </span>
                        </td>
                        <td>ISC</td>
                    </tr>
                
                    <tr>
                        <td style="font-family: var(--font-mono);">winston</td>
                        <td style="font-family: var(--font-mono);">3.11.0</td>
                        <td>
                            <span class="badge badge-success">
                                Transitive
                            </span>
                        </td>
                        <td>MIT</td>
                    </tr>
                
                    <tr>
                        <td style="font-family: var(--font-mono);">express</td>
                        <td style="font-family: var(--font-mono);">4.18.2</td>
                        <td>
                            <span class="badge badge-success">
                                Transitive
                            </span>
                        </td>
                        <td>MIT</td>
                    </tr>
                
                    <tr>
                        <td style="font-family: var(--font-mono);">acorn</td>
                        <td style="font-family: var(--font-mono);">8.4.1</td>
                        <td>
                            <span class="badge badge-success">
                                Transitive
                            </span>
                        </td>
                        <td>MIT</td>
                    </tr>
                
                    <tr>
                        <td style="font-family: var(--font-mono);">uuid</td>
                        <td style="font-family: var(--font-mono);">9.0.0</td>
                        <td>
                            <span class="badge badge-success">
                                Transitive
                            </span>
                        </td>
                        <td>MIT</td>
                    </tr>
                
                    <tr>
                        <td style="font-family: var(--font-mono);">dotenv</td>
                        <td style="font-family: var(--font-mono);">16.0.3</td>
                        <td>
                            <span class="badge badge-success">
                                Transitive
                            </span>
                        </td>
                        <td>BSD-2-Clause</td>
                    </tr>
                
                    <tr>
                        <td style="font-family: var(--font-mono);">commander</td>
                        <td style="font-family: var(--font-mono);">11.0.0</td>
                        <td>
                            <span class="badge badge-success">
                                Transitive
                            </span>
                        </td>
                        <td>MIT</td>
                    </tr>
                
                    <tr>
                        <td style="font-family: var(--font-mono);">chalk</td>
                        <td style="font-family: var(--font-mono);">5.3.0</td>
                        <td>
                            <span class="badge badge-success">
                                Transitive
                            </span>
                        </td>
                        <td>MIT</td>
                    </tr>
                </tbody>
                </table>
                <p class="text-muted mt-md">
                    Showing 20 of 20 packages
                    
                </p>
            </div>
                </div>
            </div>
            
            <!-- Tab Content: Use Cases (DIGEST ENH-D03) -->
            <div id="tab-usecases" class="tab-content">
                <div class="glass-card panel-purple mb-lg">
                    <div class="section-header">
                        <div class="section-icon"><i class="fas fa-lightbulb"></i></div>
                        <div>
                            <h2 class="section-title">Use Case Library</h2>
                            <p class="section-subtitle">Persona-based insights and actionable recommendations</p>
                        </div>
                    </div>
                    
                    <!-- Persona Filters -->
                    <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 1rem;">
                        <button class="btn btn-filter active" data-persona="all" onclick="filterUseCases('all')">
                            <i class="fas fa-users"></i> All
                        </button>
                        <button class="btn btn-filter" data-persona="po" onclick="filterUseCases('po')">
                            <i class="fas fa-user-tie"></i> Product Owner
                        </button>
                        <button class="btn btn-filter" data-persona="eng" onclick="filterUseCases('eng')">
                            <i class="fas fa-code"></i> Engineering Manager
                        </button>
                        <button class="btn btn-filter" data-persona="tech" onclick="filterUseCases('tech')">
                            <i class="fas fa-project-diagram"></i> Tech Lead
                        </button>
                        <button class="btn btn-filter" data-persona="security" onclick="filterUseCases('security')">
                            <i class="fas fa-shield-alt"></i> Security Lead
                        </button>
                        <button class="btn btn-filter" data-persona="qa" onclick="filterUseCases('qa')">
                            <i class="fas fa-vial"></i> QA Lead
                        </button>
                    </div>
                </div>
                
                <!-- Use Case Treemap (DIGEST requirement) -->
                <div class="viz-container mb-lg">
                    <div class="viz-header">
                        <h3 class="viz-title"><i class="fas fa-th"></i> Use Case Treemap by Persona &amp; Category</h3>
                    </div>
                    <div id="viz-usecases" class="viz-canvas" style="min-height: 400px;"></div>
                </div>
                
                <!-- Use Case Cards Grid -->
                <div id="usecase-grid" class="glass-card panel-emerald">
                    <!-- Populated by app.js -->
                </div>
            </div>
            
        </main>
        
        <!-- Footer -->
        <footer class="footer">
            <p>© 2026 CORTEX. Repository Dashboard powered by D3.js &amp; Glassmorphism Design.</p>
        </footer>
    </div>
    
    <!-- Embedded Data (file:// protocol support) -->
    <script id="data-ksessions" type="application/json">
    {
      "repo": {
        "slug": "ksessions",
        "display_name": "KSESSIONS",
        "description": "User Authentication platform built with Python",
        "owner": "Unknown",
        "primary_language": "JavaScript",
        "version": "1.0",
        "last_analyzed_at": "2026-02-08T12:38:25.534690"
      },
      "overview": {
        "summary": "Repository analysis",
        "business_summary": "<strong>KSESSIONS</strong> is a comprehensive .NET Framework 4.8 application for managing educational Islamic sessions, featuring audio recordings with transcripts, etymology analysis, and Arabic linguistic tools. The application provides user authentication, data management, search & discovery capabilities.",
        "key_findings": [
          "No critical security issues detected",
          "Multi-language codebase with JavaScript as primary",
          "8,351 total dependencies across the project",
          "Educational platform with rich linguistic features"
        ]
      },
      "metrics": {
        "health_score": 35,
        "risk_score": 0,
        "loc": 4976,
        "files": 150,
        "coverage_pct": 0.0,
        "languages": {
          "JavaScript": 3081,
          "Config": 550,
          "HTML": 404,
          "Python": 318,
          "CSS": 277,
          "C#": 245,
          "SQL": 59,
          "TypeScript": 40,
          "PHP": 2
        }
      },
      "security": {
        "total_count": 0,
        "critical_count": 0,
        "high_count": 0,
        "medium_count": 0,
        "low_count": 0,
        "vulnerabilities": []
      },
      "dependencies": {
        "total_count": 8351,
        "direct_count": 0,
        "transitive_count": 8351,
        "packages": [
          {"name": "eslint", "version": "8.56.0", "license": "MIT", "is_direct": true},
          {"name": "prettier", "version": "3.1.1", "license": "MIT", "is_direct": true},
          {"name": "mocha", "version": "10.2.0", "license": "MIT", "is_direct": true},
          {"name": "chai", "version": "4.3.10", "license": "MIT", "is_direct": true},
          {"name": "typescript", "version": "4.7.4", "license": "Apache-2.0", "is_direct": true},
          {"name": "rimraf", "version": "5.0.5", "license": "ISC", "is_direct": false},
          {"name": "axios", "version": "0.21.1", "license": "MIT", "is_direct": false},
          {"name": "lodash", "version": "4.17.15", "license": "MIT", "is_direct": false},
          {"name": "react", "version": "16.14.0", "license": "MIT", "is_direct": false},
          {"name": "semver", "version": "7.1.3", "license": "ISC", "is_direct": false},
          {"name": "@babel/core", "version": "7.10.3", "license": "MIT", "is_direct": false},
          {"name": "@babel/preset-env", "version": "7.10.3", "license": "MIT", "is_direct": false},
          {"name": "nyc", "version": "17.1.0", "license": "ISC", "is_direct": false},
          {"name": "winston", "version": "3.11.0", "license": "MIT", "is_direct": false},
          {"name": "express", "version": "4.18.2", "license": "MIT", "is_direct": false},
          {"name": "acorn", "version": "8.4.1", "license": "MIT", "is_direct": false},
          {"name": "uuid", "version": "9.0.0", "license": "MIT", "is_direct": false},
          {"name": "dotenv", "version": "16.0.3", "license": "BSD-2-Clause", "is_direct": false},
          {"name": "commander", "version": "11.0.0", "license": "MIT", "is_direct": false},
          {"name": "chalk", "version": "5.3.0", "license": "MIT", "is_direct": false}
        ]
      }
    }
    </script>
    
    <!-- Scripts: Multi-Layer Architecture (AC-SPA-001) -->
    
    <!-- Core Services -->
    <script src="js/core/StateManager.js"></script>
    <script src="js/core/ErrorBoundary.js"></script>
    
    <!-- Services -->
    <script src="js/services/ValidationService.js"></script>
    <script src="js/services/RepositoryService.js"></script>
    
    <!-- Controllers -->
    <script src="js/controllers/DashboardController.js"></script>
    
    <!-- Visualizations -->
    <script src="js/visualizations.js"></script>
    
    <!-- Bootstrap (Entry Point) -->
    <script src="js/bootstrap.js"></script><div class="viz-tooltip" style="position: absolute; visibility: hidden; background: rgba(26, 31, 58, 0.95); border: 1px solid rgba(0, 212, 255, 0.3); border-radius: 8px; padding: 12px 16px; color: rgb(255, 255, 255); font-size: 14px; z-index: 10000; pointer-events: none; backdrop-filter: blur(10px);">
                    <div style="font-weight: 600; color: #f7df1e; margin-bottom: 4px;">
                        JavaScript
                    </div>
                    <div style="color: #a0a6c0;">
                        3,081 lines (61.9%)
                    </div>
                </div>
    
    <!-- Legacy App (Deprecated - will be removed) -->
    <!-- <script src="js/app.js"></script> -->


<div class="viz-tooltip-domain" style="position: absolute; visibility: hidden; background: rgba(26, 31, 58, 0.95); border: 1px solid rgba(0, 212, 255, 0.3); border-radius: 8px; padding: 12px 16px; color: rgb(255, 255, 255); font-size: 13px; z-index: 10000; backdrop-filter: blur(10px); top: 771px; left: 1102px;">
                    <div style="font-weight: 600; color: #00d4ff;">
                        Transcripts
                    </div>
                    <div style="color: #a0a6c0; margin-top: 4px; text-transform: uppercase; font-size: 11px;">
                        core domain
                    </div>
                    <div style="color: #6b7280; font-size: 11px; margin-top: 4px;">
                        Confidence: 93%
                    </div>
                </div><div class="viz-tooltip-tree" style="position: absolute; visibility: hidden; background: rgba(26, 31, 58, 0.95); border: 1px solid rgba(0, 212, 255, 0.3); border-radius: 8px; padding: 12px 16px; color: rgb(255, 255, 255); font-size: 13px; z-index: 10000; backdrop-filter: blur(10px); top: 773px; left: 1506px;">
                    <div style="font-weight: 600; color: #f7df1e;">
                        javascript-1.js
                    </div>
                    <div style="color: #a0a6c0; margin-top: 4px;">
                        504 lines
                    </div>
                    <div style="color: #6b7280; font-size: 11px; margin-top: 2px;">
                        JavaScript
                    </div>
                </div></body></html>