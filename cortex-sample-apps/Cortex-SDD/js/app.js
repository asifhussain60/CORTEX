/**
 * Application Bootstrap
 * Main entry point for index.html
 * 
 * @module app
 * @author Asif Hussain
 * @version 1.0.0
 */

import { NavbarComponent } from './presentation/components/navbar.js';
import { TaskFormComponent } from './presentation/components/task-form.js';
import { TaskListComponent } from './presentation/components/task-list.js';
import { initializeDatabase } from './infrastructure/mock-db.js';
import { StorageService } from './utils/storage.js';
import { Logger } from './utils/logger.js';

class App {
    constructor() {
        this.storageService = new StorageService();
        this.navbar = null;
        this.taskForm = null;
        this.taskList = null;
        this.currentUser = null;
    }

    /**
     * Initialize the application
     */
    async init() {
        try {
            Logger.info('Initializing Cortex-SDD Application');

            // Check authentication
            const userJson = this.storageService.get('currentUser');
            if (!userJson) {
                Logger.warn('No auth token found, redirecting to login');
                window.location.href = 'login.html';
                return;
            }

            this.currentUser = JSON.parse(userJson);

            // Initialize database (seed if needed)
            await this._initializeDatabase();

            // Render components
            await this._renderComponents();

            // Setup global event listeners
            this._setupEventListeners();

            Logger.info('Application initialized successfully');
        } catch (error) {
            Logger.error('Failed to initialize application', error);
            this._showToast('Failed to initialize application: ' + error.message, 'error');
        }
    }

    /**
     * Initialize mock database
     */
    async _initializeDatabase() {
        const dbSeeded = this.storageService.get('dbSeeded');
        if (!dbSeeded) {
            Logger.info('Database not seeded, seeding now');
            await initializeDatabase();
            this.storageService.set('dbSeeded', 'true');
        }
    }

    /**
     * Render all components
     */
    async _renderComponents() {
        // Render navbar
        const navbarContainer = document.getElementById('navbar');
        if (navbarContainer) {
            this.navbar = new NavbarComponent();
            this.navbar.render(navbarContainer, this.currentUser);
        }

        // Initialize task form (modal-based, not rendered yet)
        this.taskForm = new TaskFormComponent();

        // Render task list
        const taskListContainer = document.getElementById('task-list-container');
        if (taskListContainer) {
            this.taskList = new TaskListComponent();
            await this.taskList.render(taskListContainer, this.currentUser.id);
        }
    }

    /**
     * Setup global event listeners
     */
    _setupEventListeners() {
        // Create task button
        const createBtn = document.getElementById('create-task-btn');
        if (createBtn) {
            createBtn.addEventListener('click', () => {
                this.taskForm.showCreate(this.currentUser.id);
            });
        }

        // Filter input with debounce
        const filterInput = document.getElementById('task-filter');
        if (filterInput) {
            let debounceTimer;
            filterInput.addEventListener('input', (e) => {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(async () => {
                    await this.taskList.applyFilter(e.target.value);
                    const taskListContainer = document.getElementById('task-list-container');
                    if (taskListContainer) {
                        await this.taskList.render(taskListContainer, this.currentUser.id);
                    }
                }, 300);
            });
        }

        // Task changed event (from form)
        window.addEventListener('taskChanged', async () => {
            const taskListContainer = document.getElementById('task-list-container');
            if (taskListContainer && this.taskList) {
                await this.taskList.render(taskListContainer, this.currentUser.id);
            }
        });

        // Edit task event (from task list)
        window.addEventListener('editTask', (e) => {
            if (e.detail && e.detail.taskId) {
                this.taskForm.showEdit(e.detail.taskId, this.currentUser.id);
            }
        });

        // Show toast event
        window.addEventListener('showToast', (e) => {
            if (e.detail) {
                this._showToast(e.detail.message, e.detail.type || 'info');
            }
        });
    }

    /**
     * Show toast notification
     * @param {string} message - Message to display
     * @param {string} type - Toast type (success, error, info)
     */
    _showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) return;

        const colors = {
            success: 'bg-green-500',
            error: 'bg-red-500',
            info: 'bg-blue-500'
        };

        const toast = document.createElement('div');
        toast.className = `${colors[type] || colors.info} text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-3 slide-in-right`;
        toast.innerHTML = `
            <span>${escapeHtml(message)}</span>
            <button class="ml-2 text-white hover:text-gray-200">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
            </button>
        `;

        toastContainer.appendChild(toast);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            toast.classList.add('fade-out');
            setTimeout(() => toast.remove(), 300);
        }, 5000);

        // Manual close
        toast.querySelector('button').addEventListener('click', () => {
            toast.classList.add('fade-out');
            setTimeout(() => toast.remove(), 300);
        });
    }

}

// Initialize app when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', async () => {
        const app = new App();
        await app.init();
    });
} else {
    const app = new App();
    await app.init();
}
