/**
 * Application Bootstrap
 * Main entry point for index.html
 * 
 * @module app
 * @author Asif Hussain
 * @version 1.0.0
 */

import { Navbar } from './presentation/components/navbar.js';
import { TaskForm } from './presentation/components/task-form.js';
import { TaskList } from './presentation/components/task-list.js';
import { MockDatabase } from './infrastructure/mock-db.js';
import { StorageService } from './utils/storage.js';
import { Logger } from './utils/logger.js';

class App {
    constructor() {
        this.logger = new Logger('App');
        this.storageService = new StorageService();
        this.navbar = null;
        this.taskForm = null;
        this.taskList = null;
    }

    /**
     * Initialize the application
     */
    async init() {
        try {
            this.logger.info('Initializing Cortex-SDD Application');

            // Check authentication
            const authToken = this.storageService.getItem('authToken');
            if (!authToken) {
                this.logger.warn('No auth token found, redirecting to login');
                window.location.href = 'login.html';
                return;
            }

            // Initialize database (seed if needed)
            await this.initializeDatabase();

            // Render components
            this.renderComponents();

            this.logger.info('Application initialized successfully');
        } catch (error) {
            this.logger.error('Failed to initialize application', error);
            alert('Failed to initialize application: ' + error.message);
        }
    }

    /**
     * Initialize mock database
     */
    async initializeDatabase() {
        const isSeeded = this.storageService.getItem('dbSeeded');
        if (!isSeeded) {
            this.logger.info('Database not seeded, seeding now');
            await MockDatabase.seed();
            this.storageService.setItem('dbSeeded', true);
        }
    }

    /**
     * Render all components
     */
    renderComponents() {
        // Render navbar
        const navbarContainer = document.getElementById('navbar');
        if (navbarContainer) {
            this.navbar = new Navbar();
            this.navbar.render(navbarContainer);
        }

        // Render task form
        const formContainer = document.getElementById('task-form-container');
        if (formContainer) {
            this.taskForm = new TaskForm((newTask) => this.onTaskCreated(newTask));
            this.taskForm.render(formContainer);
        }

        // Render task list
        const listContainer = document.getElementById('task-list-container');
        if (listContainer) {
            this.taskList = new TaskList();
            this.taskList.render(listContainer);
        }
    }

    /**
     * Handle task created event
     * @param {Object} newTask - Newly created task
     */
    onTaskCreated(newTask) {
        this.logger.info('New task created, refreshing list', newTask);
        if (this.taskList) {
            this.taskList.refresh();
        }
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
