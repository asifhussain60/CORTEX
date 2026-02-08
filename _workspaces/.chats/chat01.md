bootstrap.js:18 [Bootstrap] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
bootstrap.js:19 [Bootstrap] Starting CORTEX Dashboard...
bootstrap.js:20 [Bootstrap] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
bootstrap.js:21 [Bootstrap] URL: http://localhost:8000/company/dashboards/spa/index.html?repo=ksessions#overview
bootstrap.js:22 [Bootstrap] Protocol: http:
bootstrap.js:28 [Bootstrap] ━━ PHASE 0: Deployment Mode Setup ━━
bootstrap.js:30 [Bootstrap] Checking DeploymentMode availability...
bootstrap.js:34 [Bootstrap] DeploymentMode found: function
bootstrap.js:36 [Bootstrap] Calling DeploymentMode.getConfig()...
bootstrap.js:38 [Bootstrap] ✓ Config retrieved successfully
bootstrap.js:39 [Bootstrap] Deployment Mode: undefined
bootstrap.js:40 [Bootstrap] Full config: {
  "allowFetch": true,
  "requireEmbeddedData": false,
  "description": "HTTP Server",
  "icon": "🌐",
  "fallbackStrategy": "fetch_with_fallback",
  "warning": null
}
bootstrap.js:59 [Bootstrap] ━━ PHASE 1: Service Creation ━━
bootstrap.js:61 [Bootstrap] Creating ErrorBoundary...
bootstrap.js:70 [Bootstrap] ✓ ErrorBoundary created
bootstrap.js:72 [Bootstrap] Creating StateManager...
bootstrap.js:74 [Bootstrap] ✓ StateManager created
bootstrap.js:76 [Bootstrap] Creating ValidationService...
bootstrap.js:78 [Bootstrap] ✓ ValidationService created
bootstrap.js:80 [Bootstrap] Creating RepositoryService...
bootstrap.js:82 [Bootstrap] ✓ RepositoryService created
bootstrap.js:84 [Bootstrap] Creating DashboardController...
bootstrap.js:86 [Bootstrap] ✓ DashboardController created
bootstrap.js:88 [Bootstrap] ✅ All services created successfully
bootstrap.js:101 [Bootstrap] Embedded data registered: ksessions
DashboardController.js:48 [Controller] Initializing dashboard...
DashboardController.js:51 [Controller] → Injecting dependencies...
DashboardController.js:56 [Controller] ✓ Dependencies injected
DashboardController.js:59 [Controller] → Initializing DOM references...
DashboardController.js:667 [Controller] _initTabs: Initializing tab navigation...
DashboardController.js:668 [Controller] _initTabs: tabNav element: ✓ Found
DashboardController.js:675 [Controller] _initTabs: Creating 6 tab buttons
DashboardController.js:677 [Controller] _initTabs:   1. Overview (overview)
DashboardController.js:677 [Controller] _initTabs:   2. Architecture (architecture)
DashboardController.js:677 [Controller] _initTabs:   3. Quality (quality)
DashboardController.js:677 [Controller] _initTabs:   4. Security (security)
DashboardController.js:677 [Controller] _initTabs:   5. Dependencies (dependencies)
DashboardController.js:677 [Controller] _initTabs:   6. Use Cases (usecases)
DashboardController.js:689 [Controller] _initTabs: ✓ Tab HTML generated
DashboardController.js:690 [Controller] _initTabs: ✓ Tab navigation initialized
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
StateManager.js:60 [StateManager] setState called by: at DashboardController.loadRepository (http://localhost:8000/company/dashboards/spa/js/controllers/DashboardController.js:97:27)
StateManager.js:61 [StateManager] Current generation: 0 → 1
StateManager.js:87 [StateManager] Notifying 1 subscribers...
DashboardController.js:881 [Controller] _onStateChange: State change detected
DashboardController.js:882 [Controller] _onStateChange: Old generation: 0
DashboardController.js:883 [Controller] _onStateChange: New generation: 1
DashboardController.js:884 [Controller] _onStateChange: Generation delta: 1
DashboardController.js:888 [Controller] _onStateChange: Repo changed: null → ksessions
DashboardController.js:897 [Controller] _onStateChange: Handler complete (no state mutations)
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
bootstrapDashboard @ bootstrap.js:111
(anonymous) @ bootstrap.js:275
DashboardController.js:166 [Controller] loadRepository: → Caching data...
StateManager.js:159 [StateManager] setCacheEntry: Caching ksessions (internal cache, no state mutation)
StateManager.js:174 [StateManager] setCacheEntry: Cache size: 1 / 10
DashboardController.js:168 [Controller] loadRepository: ✓ Data cached
DashboardController.js:173 [Controller] loadRepository: → Proceeding to render (generation tracking handled by _renderCurrentTab)
DashboardController.js:176 [Controller] loadRepository: → Updating state (loading complete)...
StateManager.js:60 [StateManager] setState called by: at DashboardController.loadRepository (http://localhost:8000/company/dashboards/spa/js/controllers/DashboardController.js:177:31)
StateManager.js:61 [StateManager] Current generation: 1 → 2
StateManager.js:87 [StateManager] Notifying 1 subscribers...
DashboardController.js:881 [Controller] _onStateChange: State change detected
DashboardController.js:882 [Controller] _onStateChange: Old generation: 1
DashboardController.js:883 [Controller] _onStateChange: New generation: 2
DashboardController.js:884 [Controller] _onStateChange: Generation delta: 1
DashboardController.js:897 [Controller] _onStateChange: Handler complete (no state mutations)
StateManager.js:89 [StateManager] setState complete. New generation: 2
DashboardController.js:182 [Controller] loadRepository: ✓ State updated with data
DashboardController.js:183 [Controller] loadRepository:   New generation: 2
DashboardController.js:186 [Controller] loadRepository: → Updating URL...
DashboardController.js:188 [Controller] loadRepository: ✓ URL updated
DashboardController.js:191 [Controller] loadRepository: → Rendering current tab...
StateManager.js:60 [StateManager] setState called by: at DashboardController._renderCurrentTab (http://localhost:8000/company/dashboards/spa/js/controllers/DashboardController.js:247:27)
StateManager.js:61 [StateManager] Current generation: 2 → 3
StateManager.js:87 [StateManager] Notifying 1 subscribers...
DashboardController.js:881 [Controller] _onStateChange: State change detected
DashboardController.js:882 [Controller] _onStateChange: Old generation: 2
DashboardController.js:883 [Controller] _onStateChange: New generation: 3
DashboardController.js:884 [Controller] _onStateChange: Generation delta: 1
DashboardController.js:897 [Controller] _onStateChange: Handler complete (no state mutations)
StateManager.js:89 [StateManager] setState complete. New generation: 3
DashboardController.js:254 [Controller] _renderCurrentTab: Generation captured for staleness check: 3
DashboardController.js:263 [Controller] _renderCurrentTab: Pre-render generation check: 3 vs 3
DashboardController.js:270 [Controller] _renderCurrentTab: Generation valid - proceeding with render
StateManager.js:60 [StateManager] setState called by: at DashboardController._renderCurrentTab (http://localhost:8000/company/dashboards/spa/js/controllers/DashboardController.js:298:31)
StateManager.js:61 [StateManager] Current generation: 3 → 4
StateManager.js:87 [StateManager] Notifying 1 subscribers...
DashboardController.js:881 [Controller] _onStateChange: State change detected
DashboardController.js:882 [Controller] _onStateChange: Old generation: 3
DashboardController.js:883 [Controller] _onStateChange: New generation: 4
DashboardController.js:884 [Controller] _onStateChange: Generation delta: 1
DashboardController.js:897 [Controller] _onStateChange: Handler complete (no state mutations)
StateManager.js:89 [StateManager] setState complete. New generation: 4
DashboardController.js:193 [Controller] loadRepository: ✓ Tab rendered
DashboardController.js:195 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DashboardController.js:196 [Controller] loadRepository: ✅ SUCCESS - "ksessions" loaded
DashboardController.js:197 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DashboardController.js:82 [Controller] ✅ Initialization complete
bootstrap.js:118 [Bootstrap] Controller initialized ✓
bootstrap.js:150 [Bootstrap] Data Integrity Validator wired ✓
bootstrap.js:160 [Bootstrap] Dashboard ready ✓
bootstrap.js:198 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
bootstrap.js:199 🚀 CORTEX Dashboard Development Mode
bootstrap.js:200 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
bootstrap.js:201 
bootstrap.js:202 Deployment:
bootstrap.js:246 [Bootstrap] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
bootstrapDashboard @ bootstrap.js:246
await in bootstrapDashboard
(anonymous) @ bootstrap.js:275
bootstrap.js:247 [Bootstrap] ❌ FATAL ERROR
bootstrapDashboard @ bootstrap.js:247
await in bootstrapDashboard
(anonymous) @ bootstrap.js:275
bootstrap.js:248 [Bootstrap] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
bootstrapDashboard @ bootstrap.js:248
await in bootstrapDashboard
(anonymous) @ bootstrap.js:275
bootstrap.js:249 [Bootstrap] Error type: TypeError
bootstrapDashboard @ bootstrap.js:249
await in bootstrapDashboard
(anonymous) @ bootstrap.js:275
bootstrap.js:250 [Bootstrap] Error message: Cannot read properties of undefined (reading 'toUpperCase')
bootstrapDashboard @ bootstrap.js:250
await in bootstrapDashboard
(anonymous) @ bootstrap.js:275
bootstrap.js:251 [Bootstrap] Error stack: TypeError: Cannot read properties of undefined (reading 'toUpperCase')
    at bootstrapDashboard (http://localhost:8000/company/dashboards/spa/js/bootstrap.js:203:58)
bootstrapDashboard @ bootstrap.js:251
await in bootstrapDashboard
(anonymous) @ bootstrap.js:275
bootstrap.js:252 [Bootstrap] ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
bootstrapDashboard @ bootstrap.js:252
await in bootstrapDashboard
(anonymous) @ bootstrap.js:275
ContentIsolatedWorld.js:2 Initializing CS WAX...
ContentIsolatedWorld.js:2 WAX CS initialized
9830.vendors.chunk.js:2 [DEFAULT]: WARN : Using DEFAULT root logger
printToConsole @ 9830.vendors.chunk.js:2
(anonymous) @ 9830.vendors.chunk.js:2
logImpl @ 9830.vendors.chunk.js:2
log @ 9830.vendors.chunk.js:2
warn @ 9830.vendors.chunk.js:2
getRootLogger @ 9830.vendors.chunk.js:2
get root @ 9830.vendors.chunk.js:2
getLogger @ 9830.vendors.chunk.js:2
create @ 9830.vendors.chunk.js:2
C.checkingServiceProvider @ AAA-initAssistant.common.chunk.js:1
kt @ AAA-initAssistant.common.chunk.js:1
(anonymous) @ Grammarly-check.js:1
Promise.then
_load @ Grammarly-check.js:1
update @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
Promise.then
(anonymous) @ Grammarly-check.js:1
e.next @ Grammarly-check.js:1
t._next @ Grammarly-check.js:1
t.next @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
a._next @ Grammarly-check.js:1
t.next @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
a._next @ Grammarly-check.js:1
t.next @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
e._trySubscribe @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
o @ Grammarly-check.js:1
e.subscribe @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
a._next @ Grammarly-check.js:1
t.next @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
a._next @ Grammarly-check.js:1
t.next @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
a._next @ Grammarly-check.js:1
t.next @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
Promise.then
(anonymous) @ Grammarly-check.js:1
e._trySubscribe @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
o @ Grammarly-check.js:1
e.subscribe @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
a._next @ Grammarly-check.js:1
t.next @ Grammarly-check.js:1
c @ Grammarly-check.js:1
u @ Grammarly-check.js:1
t._execute @ Grammarly-check.js:1
t.execute @ Grammarly-check.js:1
t.flush @ Grammarly-check.js:1
setInterval
setInterval @ Grammarly-check.js:1
t.requestAsyncId @ Grammarly-check.js:1
t.schedule @ Grammarly-check.js:1
e.schedule @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
a._next @ Grammarly-check.js:1
t.next @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
a._next @ Grammarly-check.js:1
t.next @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
e._trySubscribe @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
o @ Grammarly-check.js:1
e.subscribe @ Grammarly-check.js:1
_ @ Grammarly-check.js:1
m @ Grammarly-check.js:1
a._next @ Grammarly-check.js:1
t.next @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
e._trySubscribe @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
o @ Grammarly-check.js:1
e.subscribe @ Grammarly-check.js:1
s @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
o @ Grammarly-check.js:1
e.subscribe @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
o @ Grammarly-check.js:1
e.subscribe @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
o @ Grammarly-check.js:1
e.subscribe @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
o @ Grammarly-check.js:1
e.subscribe @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
p @ Grammarly-check.js:1
u @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
p @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
e._trySubscribe @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
o @ Grammarly-check.js:1
e.subscribe @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
o @ Grammarly-check.js:1
e.subscribe @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
p @ Grammarly-check.js:1
u @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
p @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
e._trySubscribe @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
o @ Grammarly-check.js:1
e.subscribe @ Grammarly-check.js:1
browser @ Grammarly-check.js:1
await in browser
(anonymous) @ Grammarly-check.js:1
(anonymous) @ Grammarly-check.js:1
