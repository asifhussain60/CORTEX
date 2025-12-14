/**
 * CORTEX Real-Time Dashboard WebSocket Client
 * 
 * Features:
 * - Auto-reconnect with exponential backoff (1s, 2s, 4s, 8s max)
 * - Heartbeat/ping-pong mechanism (30s interval)
 * - Message handlers for different channels
 * - Client-side rate limiting
 * - Connection status monitoring
 * - Event-driven architecture
 * 
 * Usage:
 *   const client = new CortexWebSocketClient('ws://localhost:8765', 'your-token');
 *   
 *   client.on('metrics_update', (data) => {
 *     console.log('Metrics:', data);
 *   });
 *   
 *   client.on('operation_progress', (data) => {
 *     updateProgressBar(data.operation, data.progress);
 *   });
 *   
 *   client.connect();
 * 
 * Author: Asif Hussain
 * Copyright: © 2024-2025 Asif Hussain. All rights reserved.
 */

class CortexWebSocketClient {
    constructor(url, authToken, options = {}) {
        this.url = url;
        this.authToken = authToken;
        
        // Configuration
        this.options = {
            heartbeatInterval: options.heartbeatInterval || 30000, // 30 seconds
            maxReconnectDelay: options.maxReconnectDelay || 8000,  // 8 seconds
            initialReconnectDelay: options.initialReconnectDelay || 1000, // 1 second
            reconnectBackoffFactor: options.reconnectBackoffFactor || 2,
            maxMessageRate: options.maxMessageRate || 100, // messages per second
            enableLogging: options.enableLogging !== false
        };
        
        // State
        this.ws = null;
        this.reconnectDelay = this.options.initialReconnectDelay;
        this.reconnectAttempts = 0;
        this.isConnected = false;
        this.messageHandlers = {};
        this.heartbeatTimer = null;
        this.reconnectTimer = null;
        
        // Rate limiting
        this.messageCount = 0;
        this.rateLimitWindow = Date.now();
        
        // Metrics
        this.metrics = {
            messagesReceived: 0,
            messagesSent: 0,
            reconnects: 0,
            errors: 0,
            lastMessageTime: null
        };
    }
    
    /**
     * Register message handler for specific type
     * @param {string} type - Message type (metrics_update, operation_progress, etc.)
     * @param {function} handler - Handler function
     */
    on(type, handler) {
        if (!this.messageHandlers[type]) {
            this.messageHandlers[type] = [];
        }
        this.messageHandlers[type].push(handler);
        this.log(`Registered handler for: ${type}`);
    }
    
    /**
     * Connect to WebSocket server
     */
    connect() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.log('Already connected');
            return;
        }
        
        this.log(`Connecting to ${this.url}...`);
        
        try {
            this.ws = new WebSocket(this.url);
            
            this.ws.onopen = () => this.handleOpen();
            this.ws.onmessage = (event) => this.handleMessage(event);
            this.ws.onerror = (error) => this.handleError(error);
            this.ws.onclose = (event) => this.handleClose(event);
        } catch (error) {
            this.log(`Connection error: ${error.message}`, 'error');
            this.scheduleReconnect();
        }
    }
    
    /**
     * Disconnect from WebSocket server
     */
    disconnect() {
        this.log('Disconnecting...');
        
        // Clear timers
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }
        
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
        
        // Close WebSocket
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        
        this.isConnected = false;
    }
    
    /**
     * Handle WebSocket connection open
     */
    handleOpen() {
        this.log('Connection opened');
        this.isConnected = true;
        this.reconnectDelay = this.options.initialReconnectDelay;
        this.reconnectAttempts = 0;
        
        // Send authentication
        this.authenticate();
        
        // Start heartbeat
        this.startHeartbeat();
        
        // Notify connection listeners
        this.dispatchEvent('connected', { timestamp: new Date().toISOString() });
    }
    
    /**
     * Authenticate with server
     */
    authenticate() {
        const authMessage = {
            type: 'auth',
            token: this.authToken
        };
        
        this.send(authMessage);
        this.log('Authentication sent');
    }
    
    /**
     * Handle incoming WebSocket message
     * @param {MessageEvent} event - WebSocket message event
     */
    handleMessage(event) {
        this.metrics.messagesReceived++;
        this.metrics.lastMessageTime = new Date();
        
        try {
            const message = JSON.parse(event.data);
            this.log(`Received: ${message.type}`, 'debug');
            
            // Handle special message types
            switch (message.type) {
                case 'connected':
                    this.log('Authentication successful');
                    this.dispatchEvent('authenticated', message);
                    break;
                    
                case 'error':
                    this.log(`Server error: ${message.message}`, 'error');
                    this.dispatchEvent('error', message);
                    break;
                    
                case 'pong':
                    this.log('Heartbeat acknowledged', 'debug');
                    break;
                    
                default:
                    // Dispatch to registered handlers
                    this.dispatchEvent(message.type, message.data || message);
            }
        } catch (error) {
            this.log(`Message parse error: ${error.message}`, 'error');
            this.metrics.errors++;
        }
    }
    
    /**
     * Handle WebSocket error
     * @param {Event} error - Error event
     */
    handleError(error) {
        this.log(`WebSocket error: ${error.message || 'Unknown error'}`, 'error');
        this.metrics.errors++;
        this.dispatchEvent('error', { error: error.message });
    }
    
    /**
     * Handle WebSocket connection close
     * @param {CloseEvent} event - Close event
     */
    handleClose(event) {
        this.log(`Connection closed (code: ${event.code}, reason: ${event.reason})`);
        this.isConnected = false;
        
        // Stop heartbeat
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }
        
        // Notify disconnection listeners
        this.dispatchEvent('disconnected', {
            code: event.code,
            reason: event.reason,
            timestamp: new Date().toISOString()
        });
        
        // Auto-reconnect if not intentional close
        if (event.code !== 1000) { // 1000 = normal closure
            this.scheduleReconnect();
        }
    }
    
    /**
     * Schedule reconnection with exponential backoff
     */
    scheduleReconnect() {
        if (this.reconnectTimer) {
            return; // Already scheduled
        }
        
        this.reconnectAttempts++;
        this.metrics.reconnects++;
        
        this.log(`Reconnecting in ${this.reconnectDelay}ms (attempt ${this.reconnectAttempts})...`);
        
        this.reconnectTimer = setTimeout(() => {
            this.reconnectTimer = null;
            this.connect();
        }, this.reconnectDelay);
        
        // Exponential backoff
        this.reconnectDelay = Math.min(
            this.reconnectDelay * this.options.reconnectBackoffFactor,
            this.options.maxReconnectDelay
        );
    }
    
    /**
     * Start heartbeat mechanism
     */
    startHeartbeat() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
        }
        
        this.heartbeatTimer = setInterval(() => {
            if (this.isConnected) {
                this.send({ type: 'ping' });
                this.log('Heartbeat sent', 'debug');
            }
        }, this.options.heartbeatInterval);
    }
    
    /**
     * Send message to server with rate limiting
     * @param {object} message - Message object
     * @returns {boolean} - True if sent, false if rate limited
     */
    send(message) {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            this.log('Cannot send: Not connected', 'warn');
            return false;
        }
        
        // Rate limiting check
        if (this.isRateLimited()) {
            this.log('Rate limit exceeded', 'warn');
            return false;
        }
        
        try {
            this.ws.send(JSON.stringify(message));
            this.metrics.messagesSent++;
            this.messageCount++;
            return true;
        } catch (error) {
            this.log(`Send error: ${error.message}`, 'error');
            this.metrics.errors++;
            return false;
        }
    }
    
    /**
     * Check if rate limited
     * @returns {boolean} - True if rate limited
     */
    isRateLimited() {
        const now = Date.now();
        const windowElapsed = now - this.rateLimitWindow;
        
        // Reset window every second
        if (windowElapsed >= 1000) {
            this.messageCount = 0;
            this.rateLimitWindow = now;
            return false;
        }
        
        // Check limit
        return this.messageCount >= this.options.maxMessageRate;
    }
    
    /**
     * Dispatch event to registered handlers
     * @param {string} type - Event type
     * @param {any} data - Event data
     */
    dispatchEvent(type, data) {
        const handlers = this.messageHandlers[type] || [];
        
        handlers.forEach(handler => {
            try {
                handler(data);
            } catch (error) {
                this.log(`Handler error for ${type}: ${error.message}`, 'error');
            }
        });
        
        // Also dispatch to wildcard handlers
        const wildcardHandlers = this.messageHandlers['*'] || [];
        wildcardHandlers.forEach(handler => {
            try {
                handler({ type, data });
            } catch (error) {
                this.log(`Wildcard handler error: ${error.message}`, 'error');
            }
        });
    }
    
    /**
     * Subscribe to specific channels
     * @param {string[]} channels - Array of channel names
     */
    subscribe(channels) {
        this.send({
            type: 'subscribe',
            channels: channels
        });
        
        this.log(`Subscribed to channels: ${channels.join(', ')}`);
    }
    
    /**
     * Unsubscribe from channels
     * @param {string[]} channels - Array of channel names
     */
    unsubscribe(channels) {
        this.send({
            type: 'unsubscribe',
            channels: channels
        });
        
        this.log(`Unsubscribed from channels: ${channels.join(', ')}`);
    }
    
    /**
     * Get connection status
     * @returns {object} - Connection status
     */
    getStatus() {
        return {
            connected: this.isConnected,
            readyState: this.ws ? this.ws.readyState : WebSocket.CLOSED,
            reconnectAttempts: this.reconnectAttempts,
            metrics: { ...this.metrics }
        };
    }
    
    /**
     * Log message
     * @param {string} message - Log message
     * @param {string} level - Log level (log, debug, warn, error)
     */
    log(message, level = 'log') {
        if (!this.options.enableLogging) {
            return;
        }
        
        const timestamp = new Date().toISOString();
        const logMessage = `[CortexWS ${timestamp}] ${message}`;
        
        switch (level) {
            case 'debug':
                console.debug(logMessage);
                break;
            case 'warn':
                console.warn(logMessage);
                break;
            case 'error':
                console.error(logMessage);
                break;
            default:
                console.log(logMessage);
        }
    }
}

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CortexWebSocketClient;
}
