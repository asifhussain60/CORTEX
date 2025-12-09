/**
 * Task Form Component
 * Create and edit tasks
 * 
 * @module presentation/components/task-form
 * @author Asif Hussain
 * @version 1.0.0
 */

import { TaskService } from '../../application/services.js';
import { TaskDto } from '../../application/dtos.js';
import { StorageService } from '../../utils/storage.js';
import { Logger } from '../../utils/logger.js';

export class TaskForm {
    constructor(onTaskCreated) {
        this.taskService = new TaskService();
        this.storageService = new StorageService();
        this.logger = new Logger('TaskForm');
        this.onTaskCreated = onTaskCreated;
        this.currentUser = this.storageService.getItem('currentUser');
    }

    /**
     * Render the task form
     * @param {HTMLElement} container - Container element
     */
    render(container) {
        container.innerHTML = `
            <div class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-6">
                <h2 class="text-xl font-bold mb-4 text-gray-800">✨ Create New Task</h2>
                <form id="task-form" class="flex gap-4">
                    <div class="flex-1">
                        <input type="text" 
                            id="task-title" 
                            placeholder="Enter task title..." 
                            required
                            maxlength="255"
                            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
                    </div>
                    <button type="submit" 
                        class="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-md font-medium transition-colors">
                        Add Task
                    </button>
                </form>
                <div id="form-error" class="hidden mt-3 bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded text-sm"></div>
            </div>
        `;

        this.attachEventListeners();
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        const form = document.getElementById('task-form');
        form.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    /**
     * Handle form submission
     * @param {Event} event - Form submit event
     */
    async handleSubmit(event) {
        event.preventDefault();
        this.hideError();

        const titleInput = document.getElementById('task-title');
        const title = titleInput.value.trim();

        if (!title) {
            this.showError('Task title is required');
            return;
        }

        try {
            const taskDto = TaskDto.create({ title });
            const newTask = await this.taskService.createTask(taskDto, this.currentUser.id);
            
            this.logger.info('Task created', newTask);
            
            // Clear form
            titleInput.value = '';
            
            // Notify parent component
            if (this.onTaskCreated) {
                this.onTaskCreated(newTask);
            }
        } catch (error) {
            this.logger.error('Failed to create task', error);
            this.showError(error.message);
        }
    }

    /**
     * Show error message
     * @param {string} message - Error message
     */
    showError(message) {
        const errorDiv = document.getElementById('form-error');
        errorDiv.textContent = message;
        errorDiv.classList.remove('hidden');
    }

    /**
     * Hide error message
     */
    hideError() {
        const errorDiv = document.getElementById('form-error');
        errorDiv.classList.add('hidden');
    }
}
