// CORTEX Dashboard - Frontend Logic v1.0.0
// Phase 2: Frontend SPA Development - Vanilla JavaScript

// ============================================================================
// Configuration
// ============================================================================
const CONFIG = {
    API_BASE: 'http://localhost:8000',
    WS_URL: 'ws://localhost:8000/ws',
    REFRESH_INTERVAL: 5000, // 5 seconds
    HEARTBEAT_INTERVAL: 30000, // 30 seconds
};

// ============================================================================
// State Management
// ============================================================================
const state = {
    ws: null,
    wsConnected: false,
    progressData: null,
    planData: null,
    autoRefresh: true,
    refreshTimer: null,
};

// ============================================================================
// API Client
// ============================================================================
const api = {
    async fetch(endpoint) {
        try {
            const response = await fetch(`${CONFIG.API_BASE}${endpoint}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    },

    getPlan: () => api.fetch('/api/plan'),
    getProgress: () => api.fetch('/api/progress'),
    getAuditLogs: () => api.fetch('/api/audit-logs'),
    getTests: () => api.fetch('/api/tests'),
    getSummary: () => api.fetch('/api/summary'),
};

// ============================================================================
// WebSocket Management
// ============================================================================
function connectWebSocket() {
    if (state.wsConnected) {
        console.log('WebSocket already connected');
        updateWSStatus('✅ Connected', 'success');
        return;
    }

    try {
        state.ws = new WebSocket(CONFIG.WS_URL);

        state.ws.onopen = () => {
            console.log('WebSocket connected');
            state.wsConnected = true;
            updateWSStatus('✅ Connected', 'success');
        };

        state.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log('WebSocket message:', data);
                
                if (data.type === 'progress_update') {
                    handleProgressUpdate(data.payload);
                } else if (data.type === 'heartbeat') {
                    console.log('Heartbeat received');
                }
            } catch (error) {
                console.error('WebSocket message parse error:', error);
            }
        };

        state.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            updateWSStatus('❌ Error', 'error');
        };

        state.ws.onclose = () => {
            console.log('WebSocket disconnected');
            state.wsConnected = false;
            updateWSStatus('⚠️ Disconnected', 'warning');
            
            // Attempt reconnect after 5 seconds
            setTimeout(() => {
                if (!state.wsConnected) {
                    console.log('Attempting WebSocket reconnection...');
                    connectWebSocket();
                }
            }, 5000);
        };
    } catch (error) {
        console.error('WebSocket connection failed:', error);
        updateWSStatus('❌ Failed', 'error');
    }
}

function updateWSStatus(text, type) {
    const statusEl = document.getElementById('ws-status');
    if (statusEl) {
        statusEl.textContent = text;
        statusEl.className = `mt-2 text-xs status-${type}`;
    }
}

function handleProgressUpdate(payload) {
    console.log('Progress update received:', payload);
    state.progressData = payload;
    updateProgressDisplay();
}

// ============================================================================
// UI Updates
// ============================================================================
function updateProgressDisplay() {
    const data = state.progressData;
    if (!data) return;

    // Update progress bar
    const progressFill = document.getElementById('progress-fill');
    const progressPercentage = document.getElementById('progress-percentage');
    if (progressFill && progressPercentage) {
        const percentage = Math.round(data.overall_progress * 100);
        progressFill.style.width = `${percentage}%`;
        progressPercentage.textContent = `${percentage}%`;
    }

    // Update metrics
    const currentPhase = document.getElementById('current-phase');
    if (currentPhase) {
        currentPhase.textContent = data.current_phase || '-';
    }

    const completedTasks = document.getElementById('completed-tasks');
    if (completedTasks) {
        completedTasks.textContent = `${data.completed_tasks || 0}/${data.total_tasks || 0}`;
    }

    const planStatus = document.getElementById('plan-status');
    if (planStatus) {
        planStatus.textContent = data.plan_status || '-';
    }
}

async function loadProgressData() {
    try {
        const data = await api.getSummary();
        state.progressData = data;
        updateProgressDisplay();
    } catch (error) {
        console.error('Failed to load progress data:', error);
    }
}

// ============================================================================
// Endpoint Interaction
// ============================================================================
async function fetchEndpoint(endpoint) {
    const responseViewer = document.getElementById('response-viewer');
    const responseContent = document.getElementById('response-content');

    if (!responseViewer || !responseContent) return;

    try {
        // Show loading state
        responseViewer.classList.remove('hidden');
        responseContent.textContent = 'Loading...';

        // Fetch data
        const data = await api.fetch(endpoint);

        // Display formatted JSON
        responseContent.textContent = JSON.stringify(data, null, 2);
    } catch (error) {
        responseContent.textContent = `Error: ${error.message}`;
    }
}

function closeResponseViewer() {
    const responseViewer = document.getElementById('response-viewer');
    if (responseViewer) {
        responseViewer.classList.add('hidden');
    }
}

// ============================================================================
// Auto-Refresh
// ============================================================================
function startAutoRefresh() {
    if (state.refreshTimer) {
        clearInterval(state.refreshTimer);
    }

    state.refreshTimer = setInterval(() => {
        if (state.autoRefresh) {
            loadProgressData();
        }
    }, CONFIG.REFRESH_INTERVAL);
}

function stopAutoRefresh() {
    if (state.refreshTimer) {
        clearInterval(state.refreshTimer);
        state.refreshTimer = null;
    }
}

// ============================================================================
// Initialization
// ============================================================================
async function init() {
    console.log('CORTEX Dashboard initializing...');

    // Load initial data
    await loadProgressData();

    // Connect WebSocket
    connectWebSocket();

    // Start auto-refresh
    startAutoRefresh();

    console.log('CORTEX Dashboard ready');
}

// ============================================================================
// Event Listeners
// ============================================================================
document.addEventListener('DOMContentLoaded', init);

window.addEventListener('beforeunload', () => {
    stopAutoRefresh();
    if (state.ws && state.wsConnected) {
        state.ws.close();
    }
});

// ============================================================================
// Global Functions (called from HTML)
// ============================================================================
window.fetchEndpoint = fetchEndpoint;
window.closeResponseViewer = closeResponseViewer;
window.connectWebSocket = connectWebSocket;
