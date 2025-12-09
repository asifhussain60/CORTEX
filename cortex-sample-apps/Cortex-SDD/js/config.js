/**
 * Cortex-SDD Configuration
 * Central configuration for the application
 * 
 * @author Asif Hussain
 * @version 1.0.0
 */

export const AppConfig = {
    // Application Info
    name: 'Cortex-SDD',
    version: '1.0.0',
    environment: 'development',
    
    // Storage Keys
    storageKeys: {
        currentUser: 'cortex_current_user',
        authToken: 'cortex_auth_token',
        tasks: 'cortex_tasks',
        users: 'cortex_users',
        roles: 'cortex_roles',
        dbSeeded: 'cortex_db_seeded'
    },
    
    // JWT Simulation Settings
    jwt: {
        expirationMinutes: 60, // 1 hour
        issuer: 'Cortex-SDD',
        audience: 'Cortex-SDD-Users'
    },
    
    // Security Settings
    security: {
        minPasswordLength: 8,
        requireUppercase: true,
        requireNumber: true,
        requireSpecialChar: false,
        saltRounds: 10 // For BCrypt simulation
    },
    
    // UI Settings
    ui: {
        toastDuration: 3000, // milliseconds
        debounceDelay: 300, // milliseconds for filter input
        animationDuration: 200 // milliseconds
    },
    
    // API Simulation Settings
    api: {
        simulatedDelay: 300, // milliseconds (simulate network latency)
        baseUrl: '/api/v1'
    },
    
    // Logging Settings
    logging: {
        enabled: true,
        level: 'info', // 'debug', 'info', 'warn', 'error'
        includeTimestamp: true,
        includeStackTrace: false
    }
};

// Freeze configuration to prevent modifications
Object.freeze(AppConfig);

export default AppConfig;
