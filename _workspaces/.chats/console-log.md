bootstrap.js:13 [Bootstrap] Starting CORTEX Dashboard...
bootstrap.js:37 [Bootstrap] Services created ✓
DashboardController.js:640 [Controller] Repo changed: null → ksessions
index.html?repo=ksessions:1 Access to fetch at 'file:///D:/PROJECTS/CORTEX/company/dashboards/spa/data/ksessions.json' from origin 'null' has been blocked by CORS policy: Cross origin requests are only supported for protocol schemes: chrome, chrome-extension, chrome-untrusted, data, http, https, isolated-app.
/D:/PROJECTS/CORTEX/company/dashboards/spa/data/ksessions.json:1  Failed to load resource: net::ERR_FAILED
index.html?repo=ksessions:1 Access to fetch at 'file:///D:/PROJECTS/CORTEX/company/dashboards/spa/data/ksessions.json' from origin 'null' has been blocked by CORS policy: Cross origin requests are only supported for protocol schemes: chrome, chrome-extension, chrome-untrusted, data, http, https, isolated-app.
/D:/PROJECTS/CORTEX/company/dashboards/spa/data/ksessions.json:1  Failed to load resource: net::ERR_FAILED
index.html?repo=ksessions:1 Access to fetch at 'file:///D:/PROJECTS/CORTEX/company/dashboards/spa/data/ksessions.json' from origin 'null' has been blocked by CORS policy: Cross origin requests are only supported for protocol schemes: chrome, chrome-extension, chrome-untrusted, data, http, https, isolated-app.
/D:/PROJECTS/CORTEX/company/dashboards/spa/data/ksessions.json:1  Failed to load resource: net::ERR_FAILED
index.html?repo=ksessions:1 Access to fetch at 'file:///D:/PROJECTS/CORTEX/company/dashboards/spa/data/ksessions.json' from origin 'null' has been blocked by CORS policy: Cross origin requests are only supported for protocol schemes: chrome, chrome-extension, chrome-untrusted, data, http, https, isolated-app.
/D:/PROJECTS/CORTEX/company/dashboards/spa/data/ksessions.json:1  Failed to load resource: net::ERR_FAILED
bootstrap.js:25 [ErrorBoundary] repository_ksessions: TypeError: Failed to fetch
    at errorBoundary.wrap.repoName.repoName (RepositoryService.js:71:40)
    at ErrorBoundary.wrap (ErrorBoundary.js:41:17)
    at ErrorBoundary._handleError (ErrorBoundary.js:96:31)
    at async ErrorBoundary.wrap (ErrorBoundary.js:54:20)
    at async ErrorBoundary._handleError (ErrorBoundary.js:96:20)
    at async ErrorBoundary.wrap (ErrorBoundary.js:54:20)
    at async ErrorBoundary._handleError (ErrorBoundary.js:96:20)
    at async ErrorBoundary.wrap (ErrorBoundary.js:54:20)
    at async RepositoryService._loadRepositoryInternal (RepositoryService.js:60:16)
    at async RepositoryService.loadRepository (RepositoryService.js:47:28)
onError @ bootstrap.js:25
DashboardController.js:129 [Controller] Load failed: TypeError: Cannot read properties of null (reading 'metadata')
    at ValidationService._checkDescriptionContradiction (ValidationService.js:85:28)
    at ValidationService.validateDataIntegrity (ValidationService.js:27:14)
    at DashboardController.loadRepository (DashboardController.js:99:59)
    at async DashboardController.initialize (DashboardController.js:67:9)
    at async bootstrapDashboard (bootstrap.js:59:9)
loadRepository @ DashboardController.js:129
bootstrap.js:66 [Bootstrap] Controller initialized ✓
bootstrap.js:76 [Bootstrap] Dashboard ready ✓
bootstrap.js:114 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
bootstrap.js:115 🚀 CORTEX Dashboard Development Mode
bootstrap.js:116 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
bootstrap.js:117 
bootstrap.js:118 Available Commands:
bootstrap.js:119   window.dashboardDiagnostics()  - Export diagnostics
bootstrap.js:120   window.dashboardState          - Access state manager
bootstrap.js:121   window.dashboardController     - Access controller
bootstrap.js:122 
bootstrap.js:123 State Management:
bootstrap.js:124   - Immutable state with versioning ✓
bootstrap.js:125   - Race condition prevention ✓
bootstrap.js:126   - Stale render rejection ✓
bootstrap.js:127 
bootstrap.js:128 Error Handling:
bootstrap.js:129   - Component error boundaries ✓
bootstrap.js:130   - Retry logic (3x exponential backoff) ✓
bootstrap.js:131   - Timeout protection (5s) ✓
bootstrap.js:132 
bootstrap.js:133 Security:
bootstrap.js:134   - XSS protection (HTML sanitization) ✓
bootstrap.js:135   - Data validation before render ✓
bootstrap.js:136   - Trust boundary enforcement ✓
bootstrap.js:137 
bootstrap.js:138 Performance:
bootstrap.js:139   - Lazy tab loading ✓
bootstrap.js:140   - Request deduplication ✓
bootstrap.js:141   - LRU cache (10 items, 5min TTL) ✓
bootstrap.js:142 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
