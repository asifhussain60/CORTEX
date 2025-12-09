/**
 * Task List Component
 * Display and manage tasks
 * 
 * @module presentation/components/task-list
 * @author Asif Hussain
 * @version 1.0.0
 */

import { TaskService } from '../../application/services.js';
import { StorageService } from '../../utils/storage.js';
import { Logger } from '../../utils/logger.js';

export class TaskList {
    constructor() {
        this.taskService = new TaskService();
        this.storageService = new StorageService();
        this.logger = new Logger('TaskList');
        this.currentUser = this.storageService.getItem('currentUser');
        this.tasks = [];
        this.filter = { isCompleted: null, searchTerm: '' };
    }

    /**
     * Render the task list
     * @param {HTMLElement} container - Container element
     */
    async render(container) {
        container.innerHTML = `
            <div class="bg-white shadow-md rounded px-8 pt-6 pb-8">
                <div class="flex justify-between items-center mb-6">
                    <h2 class="text-xl font-bold text-gray-800">📝 My Tasks</h2>
                    <div class="flex gap-2">
                        <button id="filter-all" class="px-4 py-2 rounded-md text-sm font-medium transition-colors bg-indigo-600 text-white">
                            All
                        </button>
                        <button id="filter-active" class="px-4 py-2 rounded-md text-sm font-medium transition-colors bg-gray-200 text-gray-700 hover:bg-gray-300">
                            Active
                        </button>
                        <button id="filter-completed" class="px-4 py-2 rounded-md text-sm font-medium transition-colors bg-gray-200 text-gray-700 hover:bg-gray-300">
                            Completed
                        </button>
                    </div>
                </div>
                
                <div class="mb-4">
                    <input type="text" 
                        id="search-tasks" 
                        placeholder="Search tasks..." 
                        class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500">
                </div>

                <div id="tasks-container">
                    <div class="text-center py-8">
                        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                        <p class="mt-2 text-gray-600">Loading tasks...</p>
                    </div>
                </div>
            </div>
        `;

        this.attachEventListeners();
        await this.loadTasks();
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        document.getElementById('filter-all').addEventListener('click', () => this.setFilter(null));
        document.getElementById('filter-active').addEventListener('click', () => this.setFilter(false));
        document.getElementById('filter-completed').addEventListener('click', () => this.setFilter(true));
        
        const searchInput = document.getElementById('search-tasks');
        searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));
    }

    /**
     * Set completion filter
     * @param {boolean|null} isCompleted - Filter value
     */
    async setFilter(isCompleted) {
        this.filter.isCompleted = isCompleted;
        
        // Update button styles
        document.getElementById('filter-all').className = isCompleted === null 
            ? 'px-4 py-2 rounded-md text-sm font-medium transition-colors bg-indigo-600 text-white'
            : 'px-4 py-2 rounded-md text-sm font-medium transition-colors bg-gray-200 text-gray-700 hover:bg-gray-300';
        
        document.getElementById('filter-active').className = isCompleted === false
            ? 'px-4 py-2 rounded-md text-sm font-medium transition-colors bg-indigo-600 text-white'
            : 'px-4 py-2 rounded-md text-sm font-medium transition-colors bg-gray-200 text-gray-700 hover:bg-gray-300';
        
        document.getElementById('filter-completed').className = isCompleted === true
            ? 'px-4 py-2 rounded-md text-sm font-medium transition-colors bg-indigo-600 text-white'
            : 'px-4 py-2 rounded-md text-sm font-medium transition-colors bg-gray-200 text-gray-700 hover:bg-gray-300';

        await this.loadTasks();
    }

    /**
     * Handle search input
     * @param {string} searchTerm - Search term
     */
    async handleSearch(searchTerm) {
        this.filter.searchTerm = searchTerm;
        await this.loadTasks();
    }

    /**
     * Load tasks from service
     */
    async loadTasks() {
        try {
            this.tasks = await this.taskService.getAllTasks(this.currentUser.id, this.filter);
            this.renderTasks();
        } catch (error) {
            this.logger.error('Failed to load tasks', error);
            this.renderError(error.message);
        }
    }

    /**
     * Render tasks in the container
     */
    renderTasks() {
        const container = document.getElementById('tasks-container');

        if (this.tasks.length === 0) {
            container.innerHTML = `
                <div class="text-center py-8 text-gray-500">
                    <p class="text-lg">No tasks found</p>
                    <p class="text-sm">Create your first task above!</p>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <div class="space-y-3">
                ${this.tasks.map(task => this.renderTaskItem(task)).join('')}
            </div>
        `;

        // Attach task-specific event listeners
        this.tasks.forEach(task => {
            document.getElementById(`toggle-${task.id}`).addEventListener('click', () => this.toggleTask(task.id));
            document.getElementById(`delete-${task.id}`).addEventListener('click', () => this.deleteTask(task.id));
        });
    }

    /**
     * Render a single task item
     * @param {Object} task - Task DTO
     * @returns {string} HTML string
     */
    renderTaskItem(task) {
        const completedClass = task.isCompleted 
            ? 'bg-green-50 border-green-200' 
            : 'bg-white border-gray-200';
        const textClass = task.isCompleted 
            ? 'line-through text-gray-500' 
            : 'text-gray-800';
        const checkboxClass = task.isCompleted 
            ? 'text-green-600' 
            : 'text-gray-400';

        return `
            <div class="flex items-center justify-between p-4 border-2 ${completedClass} rounded-md hover:shadow-md transition-shadow">
                <div class="flex items-center gap-3 flex-1">
                    <button id="toggle-${task.id}" class="focus:outline-none">
                        <svg class="w-6 h-6 ${checkboxClass}" fill="currentColor" viewBox="0 0 20 20">
                            ${task.isCompleted 
                                ? '<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>'
                                : '<path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm0-2a6 6 0 100-12 6 6 0 000 12z" clip-rule="evenodd"/>'}
                        </svg>
                    </button>
                    <span class="${textClass} flex-1">${this.escapeHtml(task.title)}</span>
                </div>
                <button id="delete-${task.id}" 
                    class="ml-4 text-red-600 hover:text-red-800 focus:outline-none">
                    <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd"/>
                    </svg>
                </button>
            </div>
        `;
    }

    /**
     * Toggle task completion status
     * @param {number} taskId - Task ID
     */
    async toggleTask(taskId) {
        try {
            await this.taskService.toggleTaskCompletion(taskId, this.currentUser.id);
            await this.loadTasks();
        } catch (error) {
            this.logger.error('Failed to toggle task', error);
            alert(`Error: ${error.message}`);
        }
    }

    /**
     * Delete a task
     * @param {number} taskId - Task ID
     */
    async deleteTask(taskId) {
        if (!confirm('Are you sure you want to delete this task?')) {
            return;
        }

        try {
            await this.taskService.deleteTask(taskId, this.currentUser.id);
            await this.loadTasks();
        } catch (error) {
            this.logger.error('Failed to delete task', error);
            alert(`Error: ${error.message}`);
        }
    }

    /**
     * Render error message
     * @param {string} message - Error message
     */
    renderError(message) {
        const container = document.getElementById('tasks-container');
        container.innerHTML = `
            <div class="text-center py-8">
                <p class="text-red-600 font-medium">Error loading tasks</p>
                <p class="text-gray-600 text-sm">${this.escapeHtml(message)}</p>
            </div>
        `;
    }

    /**
     * Escape HTML to prevent XSS
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Refresh task list (called from parent)
     */
    async refresh() {
        await this.loadTasks();
    }
}
