/**
 * Navigation Bar Component
 * Top navigation with user info and logout
 * 
 * @module presentation/components/navbar
 * @author Asif Hussain
 * @version 1.0.0
 */

import { StorageService } from '../../utils/storage.js';
import { Logger } from '../../utils/logger.js';

export class Navbar {
    constructor() {
        this.storageService = new StorageService();
        this.logger = new Logger('Navbar');
        this.currentUser = this.storageService.getItem('currentUser');
    }

    /**
     * Render the navbar
     * @param {HTMLElement} container - Container element
     */
    render(container) {
        if (!this.currentUser) {
            // Redirect to login if not authenticated
            window.location.href = 'login.html';
            return;
        }

        container.innerHTML = `
            <nav class="bg-indigo-600 shadow-lg">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div class="flex justify-between h-16">
                        <div class="flex items-center">
                            <h1 class="text-white text-2xl font-bold">📋 Cortex-SDD</h1>
                        </div>
                        <div class="flex items-center space-x-4">
                            <span class="text-white text-sm">
                                👤 ${this.currentUser.username} 
                                <span class="text-indigo-200">(${this.currentUser.roleName})</span>
                            </span>
                            <button id="logout-btn" 
                                class="bg-indigo-700 hover:bg-indigo-800 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors">
                                Logout
                            </button>
                        </div>
                    </div>
                </div>
            </nav>
        `;

        this.attachEventListeners();
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.handleLogout());
        }
    }

    /**
     * Handle logout
     */
    handleLogout() {
        this.logger.info('User logging out', this.currentUser);
        this.storageService.removeItem('authToken');
        this.storageService.removeItem('currentUser');
        window.location.href = 'login.html';
    }
}
