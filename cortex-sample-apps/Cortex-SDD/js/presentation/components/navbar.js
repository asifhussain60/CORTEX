/**
 * Navigation Bar Component
 * Renders navigation with user info and logout
 * 
 * @author Asif Hussain
 * @version 1.0.0
 */

import { Logger } from '../../utils/logger.js';
import { StorageService } from '../../utils/storage.js';

export class NavbarComponent {
    constructor() {
        this.storageService = new StorageService();
        Logger.debug('NavbarComponent initialized');
    }

    /**
     * Render navbar
     * @param {HTMLElement} container - Container element
     * @param {Object} currentUser - Current user object
     */
    render(container, currentUser) {
        if (!container) {
            Logger.error('NavbarComponent.render: container is null');
            return;
        }

        if (!currentUser) {
            Logger.warn('NavbarComponent.render: no current user');
            this._renderGuestNav(container);
            return;
        }

        this._renderAuthenticatedNav(container, currentUser);
    }

    /**
     * Render guest navigation (login link)
     * @param {HTMLElement} container - Container element
     */
    _renderGuestNav(container) {
        container.innerHTML = `
            <div class="container mx-auto px-4">
                <div class="flex items-center justify-between h-16">
                    <div class="flex items-center">
                        <span class="text-2xl font-bold text-blue-600">Cortex-SDD</span>
                        <span class="ml-3 text-sm text-gray-500">Task Management</span>
                    </div>
                    <div>
                        <a href="login.html" class="text-blue-600 hover:text-blue-800 font-medium">
                            Login
                        </a>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Render authenticated navigation
     * @param {HTMLElement} container - Container element
     * @param {Object} currentUser - Current user object
     */
    _renderAuthenticatedNav(container, currentUser) {
        const roleDisplay = this._getRoleDisplay(currentUser.role);
        const roleColor = this._getRoleColor(currentUser.role);

        container.innerHTML = `
            <div class="container mx-auto px-4">
                <div class="flex items-center justify-between h-16">
                    <!-- Logo and Brand -->
                    <div class="flex items-center">
                        <span class="text-2xl font-bold text-blue-600">Cortex-SDD</span>
                        <span class="ml-3 text-sm text-gray-500 hidden md:inline">Task Management</span>
                    </div>

                    <!-- User Menu -->
                    <div class="flex items-center gap-4">
                        <!-- User Info -->
                        <div class="hidden md:flex items-center gap-3">
                            <div class="text-right">
                                <div class="text-sm font-medium text-gray-700">
                                    ${this._escapeHtml(currentUser.username)}
                                </div>
                                <div class="text-xs ${roleColor}">
                                    ${roleDisplay}
                                </div>
                            </div>
                            <div class="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold">
                                ${this._getInitials(currentUser.username)}
                            </div>
                        </div>

                        <!-- Mobile User Initial -->
                        <div class="md:hidden w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold">
                            ${this._getInitials(currentUser.username)}
                        </div>

                        <!-- Logout Button -->
                        <button 
                            id="logout-btn"
                            class="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors duration-200 text-sm font-medium"
                        >
                            Logout
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Attach logout event
        const logoutBtn = container.querySelector('#logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this._handleLogout());
        }
    }

    /**
     * Handle logout action
     */
    _handleLogout() {
        Logger.info('User logging out');
        
        // Clear storage
        this.storageService.remove('currentUser');
        this.storageService.remove('authToken');
        
        // Redirect to login
        window.location.href = 'login.html';
    }

    /**
     * Get user initials
     * @param {string} username - Username
     * @returns {string} Initials (2 chars max)
     */
    _getInitials(username) {
        if (!username) return '?';
        const parts = username.split(' ');
        if (parts.length >= 2) {
            return (parts[0][0] + parts[1][0]).toUpperCase();
        }
        return username.substring(0, 2).toUpperCase();
    }

    /**
     * Get role display name
     * @param {number} role - Role enum value
     * @returns {string} Role display name
     */
    _getRoleDisplay(role) {
        const roles = {
            1: 'Administrator',
            2: 'Team Lead',
            3: 'User'
        };
        return roles[role] || 'Unknown';
    }

    /**
     * Get role color class
     * @param {number} role - Role enum value
     * @returns {string} Tailwind color class
     */
    _getRoleColor(role) {
        const colors = {
            1: 'text-purple-600',  // Admin
            2: 'text-blue-600',    // Team Lead
            3: 'text-gray-600'     // User
        };
        return colors[role] || 'text-gray-600';
    }

    /**
     * Escape HTML to prevent XSS
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
