/**
 * API Client - Utility for making API calls to backend
 * Handles fetch requests and WebSocket connections
 */

class APIClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
        this.wsUrl = `ws://localhost:8000`;
    }

    /**
     * GET request wrapper
     */
    async get(endpoint) {
        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`);
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error(`GET ${endpoint}:`, error);
            throw error;
        }
    }

    /**
     * Get brain tier status
     */
    async getBrainTiers() {
        return this.get('/api/brain/tiers');
    }

    /**
     * Get SSOT metrics
     */
    async getSSOTMetrics() {
        return this.get('/api/brain/metrics');
    }

    /**
     * Get audit entries
     */
    async getAuditEntries(limit = 50, offset = 0) {
        return this.get(`/api/audit/entries?limit=${limit}&offset=${offset}`);
    }

    /**
     * Get orchestrator status
     */
    async getOrchestrators() {
        return this.get('/api/orchestrators');
    }

    /**
     * Connect to WebSocket audit stream with retry logic
     */
    connectAuditStream(onMessage, onError = null) {
        const ws = new WebSocket(`${this.wsUrl}/ws/audit`);
        
        ws.onopen = () => {
            console.log('Γ£ô Connected to audit stream');
        };
        
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                onMessage(data);
            } catch (error) {
                console.error('Error parsing audit message:', error);
            }
        };
        
        ws.onerror = (error) => {
            console.error('Γ£ù WebSocket error:', error);
            if (onError) onError(error);
        };
        
        ws.onclose = () => {
            console.log('Disconnected from audit stream. Will retry in 5 seconds...');
            // Auto-reconnect after 5 seconds
            setTimeout(() => {
                console.log('Attempting to reconnect to audit stream...');
                this.connectAuditStream(onMessage, onError);
            }, 5000);
        };
        
        return ws;
    }
}

// Global API client instance
const api = new APIClient();
