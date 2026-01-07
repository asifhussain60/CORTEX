/**
 * Security Module
 * Handles authentication, authorization, and cryptography
 * 
 * @author Asif Hussain
 * @version 1.0.0
 */

import { AppConfig } from '../config.js';
import { Logger } from '../utils/logger.js';
import { StorageManager } from '../utils/storage.js';

/**
 * Simple password hashing (demo purposes only)
 * NOTE: In production, use bcrypt or similar
 */
export class PasswordHasher {
    /**
     * Hash password (Base64 encoding for demo)
     * @param {string} password - Plain text password
     * @returns {string} Hashed password
     */
    static hash(password) {
        // Simple Base64 encoding for demo (NOT secure for production!)
        const salt = 'cortex-sdd-salt-2025';
        const combined = salt + password + salt;
        return btoa(combined);
    }

    /**
     * Verify password against hash
     * @param {string} password - Plain text password
     * @param {string} hash - Password hash
     * @returns {boolean} True if match
     */
    static verify(password, hash) {
        const computed = this.hash(password);
        return computed === hash;
    }

    /**
     * Validate password strength
     * @param {string} password - Password to validate
     * @returns {Object} Validation result
     */
    static validateStrength(password) {
        const result = {
            isValid: true,
            errors: [],
            strength: 'weak'
        };

        if (password.length < AppConfig.security.minPasswordLength) {
            result.isValid = false;
            result.errors.push(`Password must be at least ${AppConfig.security.minPasswordLength} characters`);
        }

        if (AppConfig.security.requireUppercase && !/[A-Z]/.test(password)) {
            result.isValid = false;
            result.errors.push('Password must contain at least one uppercase letter');
        }

        if (AppConfig.security.requireLowercase && !/[a-z]/.test(password)) {
            result.isValid = false;
            result.errors.push('Password must contain at least one lowercase letter');
        }

        if (AppConfig.security.requireNumber && !/[0-9]/.test(password)) {
            result.isValid = false;
            result.errors.push('Password must contain at least one number');
        }

        if (AppConfig.security.requireSpecialChar && !/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
            result.isValid = false;
            result.errors.push('Password must contain at least one special character');
        }

        // Calculate strength
        if (result.isValid) {
            let score = 0;
            if (password.length >= 12) score++;
            if (/[A-Z]/.test(password)) score++;
            if (/[a-z]/.test(password)) score++;
            if (/[0-9]/.test(password)) score++;
            if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) score++;

            if (score >= 4) result.strength = 'strong';
            else if (score >= 3) result.strength = 'medium';
        }

        return result;
    }
}

/**
 * JWT Token Manager (simulated)
 * NOTE: This is a simplified demo version
 */
export class JWTManager {
    /**
     * Generate JWT token (Base64 encoded JSON for demo)
     * @param {Object} payload - Token payload
     * @returns {string} JWT token
     */
    static generate(payload) {
        const header = {
            alg: 'HS256',
            typ: 'JWT'
        };

        const tokenPayload = {
            ...payload,
            iss: AppConfig.jwt.issuer,
            aud: AppConfig.jwt.audience,
            iat: Math.floor(Date.now() / 1000),
            exp: Math.floor(Date.now() / 1000) + (AppConfig.jwt.expirationMinutes * 60)
        };

        // Simple Base64 encoding (NOT secure for production!)
        const headerEncoded = btoa(JSON.stringify(header));
        const payloadEncoded = btoa(JSON.stringify(tokenPayload));
        const signature = btoa(`${headerEncoded}.${payloadEncoded}.secret`);

        const token = `${headerEncoded}.${payloadEncoded}.${signature}`;
        Logger.debug('JWT token generated', { userId: payload.userId });
        return token;
    }

    /**
     * Decode JWT token
     * @param {string} token - JWT token
     * @returns {Object|null} Decoded payload or null if invalid
     */
    static decode(token) {
        try {
            const parts = token.split('.');
            if (parts.length !== 3) {
                Logger.warn('Invalid JWT format');
                return null;
            }

            const payloadJson = atob(parts[1]);
            const payload = JSON.parse(payloadJson);

            // Check expiration
            const now = Math.floor(Date.now() / 1000);
            if (payload.exp && payload.exp < now) {
                Logger.warn('JWT token expired');
                return null;
            }

            return payload;
        } catch (error) {
            Logger.error('Failed to decode JWT', error);
            return null;
        }
    }

    /**
     * Verify JWT token
     * @param {string} token - JWT token
     * @returns {boolean} True if valid
     */
    static verify(token) {
        const payload = this.decode(token);
        return payload !== null;
    }

    /**
     * Get user ID from token
     * @param {string} token - JWT token
     * @returns {string|null} User ID or null
     */
    static getUserId(token) {
        const payload = this.decode(token);
        return payload ? payload.userId : null;
    }

    /**
     * Check if token is expired
     * @param {string} token - JWT token
     * @returns {boolean} True if expired
     */
    static isExpired(token) {
        const payload = this.decode(token);
        if (!payload || !payload.exp) return true;

        const now = Math.floor(Date.now() / 1000);
        return payload.exp < now;
    }
}

/**
 * Authentication Manager
 * Handles user authentication state
 */
export class AuthManager {
    /**
     * Save authentication state
     * @param {string} token - JWT token
     * @param {Object} user - User object
     */
    static saveAuth(token, user) {
        StorageManager.set(AppConfig.storage.authTokenKey, token);
        StorageManager.set(AppConfig.storage.currentUserKey, {
            id: user.id,
            username: user.username,
            email: user.email,
            role: user.role,
            fullName: user.fullName
        });
        Logger.info('Authentication saved', { userId: user.id });
    }

    /**
     * Get current authentication token
     * @returns {string|null} Token or null
     */
    static getToken() {
        return StorageManager.get(AppConfig.storage.authTokenKey, null);
    }

    /**
     * Get current user
     * @returns {Object|null} User object or null
     */
    static getCurrentUser() {
        return StorageManager.get(AppConfig.storage.currentUserKey, null);
    }

    /**
     * Check if user is authenticated
     * @returns {boolean} True if authenticated
     */
    static isAuthenticated() {
        const token = this.getToken();
        if (!token) return false;

        return JWTManager.verify(token);
    }

    /**
     * Clear authentication state
     */
    static clearAuth() {
        StorageManager.remove(AppConfig.storage.authTokenKey);
        StorageManager.remove(AppConfig.storage.currentUserKey);
        Logger.info('Authentication cleared');
    }

    /**
     * Check if current user has role
     * @param {number} requiredRole - Required role value
     * @returns {boolean} True if user has role
     */
    static hasRole(requiredRole) {
        const user = this.getCurrentUser();
        if (!user) return false;

        return user.role >= requiredRole;
    }

    /**
     * Refresh token if needed
     * @returns {boolean} True if token refreshed
     */
    static refreshTokenIfNeeded() {
        const token = this.getToken();
        if (!token) return false;

        const payload = JWTManager.decode(token);
        if (!payload) return false;

        // Refresh if less than 5 minutes remaining
        const now = Math.floor(Date.now() / 1000);
        const timeRemaining = payload.exp - now;

        if (timeRemaining < 300) { // 5 minutes
            const newToken = JWTManager.generate({
                userId: payload.userId,
                role: payload.role
            });
            StorageManager.set(AppConfig.storage.authTokenKey, newToken);
            Logger.info('Token refreshed', { userId: payload.userId });
            return true;
        }

        return false;
    }
}

/**
 * Authorization Helper
 * Provides authorization checks
 */
export class AuthorizationHelper {
    /**
     * Check if user can edit task
     * @param {Object} user - User object
     * @param {Object} task - Task object
     * @returns {boolean} True if authorized
     */
    static canEditTask(user, task) {
        if (!user || !task) return false;

        // Admin can edit all
        if (user.role === 3) return true; // Role.Admin

        // Team lead can edit all
        if (user.role === 2) return true; // Role.TeamLead

        // User can edit own tasks or assigned tasks
        return task.createdBy === user.id || task.assignedTo === user.id;
    }

    /**
     * Check if user can delete task
     * @param {Object} user - User object
     * @param {Object} task - Task object
     * @returns {boolean} True if authorized
     */
    static canDeleteTask(user, task) {
        if (!user || !task) return false;

        // Admin can delete all
        if (user.role === 3) return true;

        // Team lead can delete all
        if (user.role === 2) return true;

        // User can only delete own created tasks
        return task.createdBy === user.id;
    }

    /**
     * Check if user can assign tasks
     * @param {Object} user - User object
     * @returns {boolean} True if authorized
     */
    static canAssignTasks(user) {
        if (!user) return false;
        // Team lead and admin can assign
        return user.role >= 2;
    }

    /**
     * Check if user can manage users
     * @param {Object} user - User object
     * @returns {boolean} True if authorized
     */
    static canManageUsers(user) {
        if (!user) return false;
        // Only admin can manage users
        return user.role === 3;
    }
}

export default {
    PasswordHasher,
    JWTManager,
    AuthManager,
    AuthorizationHelper
};
