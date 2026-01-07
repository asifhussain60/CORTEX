/**
 * Task List Component
 * Displays tasks in responsive grid with filtering
 * 
 * @author Asif Hussain
 * @version 1.0.0
 */

import { Logger } from '../../utils/logger.js';
import { TaskService } from '../../application/services.js';
import { TaskFilterDTO } from '../../application/dtos.js';
import { Status, Priority } from '../../domain/enums.js';
import { escapeHtml } from '../../utils/html-utils.js';

export class TaskListComponent {
    constructor() {
        this.taskService = new TaskService();
        this.tasks = [];
        this.currentFilter = new TaskFilterDTO();
        Logger.debug('TaskListComponent initialized');
    }

    /**
     * Render task list
     * @param {HTMLElement} container - Container element
     * @param {string} userId - Current user ID
     */
    async render(container, userId) {
        if (!container) {
            Logger.error('TaskListComponent.render: container is null');
            return;
        }

        if (!userId) {
            Logger.error('TaskListComponent.render: userId is required');
            return;
        }

        try {
            // Load tasks for user
            this.tasks = await this.taskService.getMyTasks(userId);
            Logger.debug(`Loaded ${this.tasks.length} tasks for user ${userId}`);

            this._renderTaskGrid(container);
        } catch (error) {
            Logger.error('TaskListComponent.render error:', error);
            this._renderError(container, error.message);
        }
    }

    /**
     * Apply filter and re-render
     * @param {string} searchKeyword - Search keyword
     */
    async applyFilter(searchKeyword) {
        Logger.debug(`Applying filter: ${searchKeyword}`);
        this.currentFilter.searchKeyword = searchKeyword;
        
        // Re-render will be triggered externally
    }

    /**
     * Render task grid
     * @param {HTMLElement} container - Container element
     */
    _renderTaskGrid(container) {
        if (this.tasks.length === 0) {
            this._renderEmptyState(container);
            return;
        }

        const filteredTasks = this._filterTasks(this.tasks);

        container.innerHTML = `
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                ${filteredTasks.map(task => this._renderTaskCard(task)).join('')}
            </div>
        `;

        // Attach event handlers
        this._attachTaskHandlers(container);
    }

    /**
     * Filter tasks by search keyword
     * @param {Array} tasks - Tasks to filter
     * @returns {Array} Filtered tasks
     */
    _filterTasks(tasks) {
        if (!this.currentFilter.searchKeyword) {
            return tasks;
        }

        const keyword = this.currentFilter.searchKeyword.toLowerCase();
        return tasks.filter(task =>
            task.title.toLowerCase().includes(keyword) ||
            task.description.toLowerCase().includes(keyword) ||
            (task.tags && task.tags.some(tag => tag.toLowerCase().includes(keyword)))
        );
    }

    /**
     * Render single task card
     * @param {Object} task - Task DTO
     * @returns {string} HTML string
     */
    _renderTaskCard(task) {
        const statusColor = this._getStatusColor(task.status);
        const priorityColor = this._getPriorityColor(task.priority);
        const statusText = this._getStatusText(task.status);
        const priorityText = this._getPriorityText(task.priority);
        const isCompleted = task.status === Status.Completed;
        const isOverdue = task.isOverdue && !isCompleted;

        return `
            <div class="bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300 overflow-hidden" data-task-id="${task.id}">
                <!-- Task Header -->
                <div class="p-6">
                    <!-- Priority Badge -->
                    <div class="flex items-center justify-between mb-3">
                        <span class="px-3 py-1 ${priorityColor} text-white text-xs font-semibold rounded-full">
                            ${priorityText}
                        </span>
                        ${isOverdue ? '<span class="text-red-600 text-xs font-semibold">⚠ OVERDUE</span>' : ''}
                    </div>

                    <!-- Task Title -->
                    <h3 class="text-lg font-bold text-gray-800 mb-2 ${isCompleted ? 'line-through text-gray-500' : ''}">
                        ${this._escapeHtml(task.title)}
                    </h3>

                    <!-- Task Description -->
                    <p class="text-gray-600 text-sm mb-4 line-clamp-3">
                        ${this._escapeHtml(task.description || 'No description')}
                    </p>

                    <!-- Status Badge -->
                    <div class="flex items-center gap-2 mb-4">
                        <span class="px-3 py-1 ${statusColor} text-white text-xs font-medium rounded-full">
                            ${statusText}
                        </span>
                    </div>

                    <!-- Task Meta (Due Date, Tags) -->
                    <div class="space-y-2 mb-4">
                        ${task.dueDate ? `
                            <div class="flex items-center text-xs text-gray-500">
                                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                </svg>
                                Due: ${new Date(task.dueDate).toLocaleDateString()}
                            </div>
                        ` : ''}
                        
                        ${task.tags && task.tags.length > 0 ? `
                            <div class="flex flex-wrap gap-1">
                                ${task.tags.map(tag => `
                                    <span class="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                                        #${escapeHtml(tag)}
                                    </span>
                                `).join('')}
                            </div>
                        ` : ''}
                    </div>
                </div>

                <!-- Task Actions -->
                <div class="px-6 py-4 bg-gray-50 flex items-center justify-between border-t border-gray-200">
                    <button 
                        class="task-toggle-btn px-4 py-2 ${isCompleted ? 'bg-yellow-500 hover:bg-yellow-600' : 'bg-green-500 hover:bg-green-600'} text-white rounded-lg text-sm font-medium transition-colors duration-200"
                        data-task-id="${task.id}"
                    >
                        ${isCompleted ? 'Reopen' : 'Complete'}
                    </button>
                    
                    <div class="flex gap-2">
                        <button 
                            class="task-edit-btn p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors duration-200"
                            data-task-id="${task.id}"
                            title="Edit task"
                        >
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                            </svg>
                        </button>
                        
                        <button 
                            class="task-delete-btn p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors duration-200"
                            data-task-id="${task.id}"
                            title="Delete task"
                        >
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Render empty state
     * @param {HTMLElement} container - Container element
     */
    _renderEmptyState(container) {
        container.innerHTML = `
            <div class="text-center py-12">
                <svg class="mx-auto h-24 w-24 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                <h3 class="mt-4 text-lg font-medium text-gray-900">No tasks found</h3>
                <p class="mt-2 text-sm text-gray-500">
                    ${this.currentFilter.searchKeyword ? 'Try a different search term' : 'Get started by creating a new task'}
                </p>
            </div>
        `;
    }

    /**
     * Render error state
     * @param {HTMLElement} container - Container element
     * @param {string} message - Error message
     */
    _renderError(container, message) {
        container.innerHTML = `
            <div class="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
                <p class="text-red-700 font-medium">${escapeHtml(message)}</p>
            </div>
        `;
    }

    /**
     * Attach event handlers to task cards
     * @param {HTMLElement} container - Container element
     */
    _attachTaskHandlers(container) {
        // Toggle complete/reopen
        container.querySelectorAll('.task-toggle-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const taskId = e.target.closest('.task-toggle-btn').dataset.taskId;
                this._handleToggleTask(taskId);
            });
        });

        // Edit task
        container.querySelectorAll('.task-edit-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const taskId = e.target.closest('.task-edit-btn').dataset.taskId;
                this._handleEditTask(taskId);
            });
        });

        // Delete task
        container.querySelectorAll('.task-delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const taskId = e.target.closest('.task-delete-btn').dataset.taskId;
                this._handleDeleteTask(taskId);
            });
        });
    }

    /**
     * Handle toggle task completion
     * @param {string} taskId - Task ID
     */
    async _handleToggleTask(taskId) {
        Logger.debug(`Toggling task: ${taskId}`);
        
        try {
            const task = this.tasks.find(t => t.id === taskId);
            if (!task) return;

            const newStatus = task.status === Status.Completed ? Status.InProgress : Status.Completed;
            
            await this.taskService.updateTask(taskId, { status: newStatus }, task.createdBy);
            
            // Reload tasks
            const container = document.querySelector('[data-task-id]')?.parentElement?.parentElement;
            if (container) {
                await this.render(container, task.createdBy);
            }

            // Show toast (handled externally)
            window.dispatchEvent(new CustomEvent('showToast', {
                detail: { message: `Task ${newStatus === Status.Completed ? 'completed' : 'reopened'}`, type: 'success' }
            }));
        } catch (error) {
            Logger.error('Toggle task error:', error);
            window.dispatchEvent(new CustomEvent('showToast', {
                detail: { message: error.message, type: 'error' }
            }));
        }
    }

    /**
     * Handle edit task
     * @param {string} taskId - Task ID
     */
    _handleEditTask(taskId) {
        Logger.debug(`Editing task: ${taskId}`);
        window.dispatchEvent(new CustomEvent('editTask', { detail: { taskId } }));
    }

    /**
     * Handle delete task
     * @param {string} taskId - Task ID
     */
    async _handleDeleteTask(taskId) {
        if (!confirm('Are you sure you want to delete this task?')) {
            return;
        }

        Logger.debug(`Deleting task: ${taskId}`);
        
        try {
            const task = this.tasks.find(t => t.id === taskId);
            if (!task) return;

            await this.taskService.deleteTask(taskId, task.createdBy);
            
            // Reload tasks
            const container = document.querySelector('[data-task-id]')?.parentElement?.parentElement;
            if (container) {
                await this.render(container, task.createdBy);
            }

            // Show toast
            window.dispatchEvent(new CustomEvent('showToast', {
                detail: { message: 'Task deleted successfully', type: 'success' }
            }));
        } catch (error) {
            Logger.error('Delete task error:', error);
            window.dispatchEvent(new CustomEvent('showToast', {
                detail: { message: error.message, type: 'error' }
            }));
        }
    }

    /**
     * Get status color class
     * @param {number} status - Status enum value
     * @returns {string} Tailwind color class
     */
    _getStatusColor(status) {
        const colors = {
            [Status.NotStarted]: 'bg-gray-500',
            [Status.InProgress]: 'bg-blue-500',
            [Status.Blocked]: 'bg-red-500',
            [Status.Completed]: 'bg-green-500',
            [Status.Cancelled]: 'bg-gray-400'
        };
        return colors[status] || 'bg-gray-500';
    }

    /**
     * Get priority color class
     * @param {number} priority - Priority enum value
     * @returns {string} Tailwind color class
     */
    _getPriorityColor(priority) {
        const colors = {
            [Priority.Low]: 'bg-green-600',
            [Priority.Medium]: 'bg-yellow-600',
            [Priority.High]: 'bg-orange-600',
            [Priority.Critical]: 'bg-red-600'
        };
        return colors[priority] || 'bg-gray-600';
    }

    /**
     * Get status text
     * @param {number} status - Status enum value
     * @returns {string} Status text
     */
    _getStatusText(status) {
        const texts = {
            [Status.NotStarted]: 'Not Started',
            [Status.InProgress]: 'In Progress',
            [Status.Blocked]: 'Blocked',
            [Status.Completed]: 'Completed',
            [Status.Cancelled]: 'Cancelled'
        };
        return texts[status] || 'Unknown';
    }

    /**
     * Get priority text
     * @param {number} priority - Priority enum value
     * @returns {string} Priority text
     */
    _getPriorityText(priority) {
        const texts = {
            [Priority.Low]: 'Low',
            [Priority.Medium]: 'Medium',
            [Priority.High]: 'High',
            [Priority.Critical]: 'Critical'
        };
        return texts[priority] || 'Unknown';
    }

}
