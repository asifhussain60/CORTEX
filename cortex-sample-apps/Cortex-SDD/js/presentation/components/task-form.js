/**
 * Task Form Component
 * Modal form for creating and editing tasks
 * 
 * @author Asif Hussain
 * @version 1.0.0
 */

import { Logger } from '../../utils/logger.js';
import { TaskService } from '../../application/services.js';
import { Priority, Status } from '../../domain/enums.js';

export class TaskFormComponent {
    constructor() {
        this.taskService = new TaskService();
        this.currentTaskId = null;
        this.mode = 'create'; // 'create' or 'edit'
        Logger.debug('TaskFormComponent initialized');
    }

    /**
     * Show create task modal
     * @param {string} userId - Current user ID
     */
    showCreate(userId) {
        this.mode = 'create';
        this.currentTaskId = null;
        this._renderModal(userId, null);
    }

    /**
     * Show edit task modal
     * @param {string} taskId - Task ID to edit
     * @param {string} userId - Current user ID
     */
    async showEdit(taskId, userId) {
        this.mode = 'edit';
        this.currentTaskId = taskId;

        try {
            const task = await this.taskService.getTaskById(taskId);
            if (task) {
                this._renderModal(userId, task);
            } else {
                Logger.error('Task not found:', taskId);
            }
        } catch (error) {
            Logger.error('Error loading task for edit:', error);
        }
    }

    /**
     * Hide modal
     */
    hide() {
        const modal = document.querySelector('#task-form-modal');
        if (modal) {
            modal.remove();
        }
    }

    /**
     * Render modal
     * @param {string} userId - Current user ID
     * @param {Object|null} task - Task data for edit mode
     */
    _renderModal(userId, task) {
        // Remove existing modal
        this.hide();

        const isEdit = this.mode === 'edit';
        const title = isEdit ? 'Edit Task' : 'Create New Task';
        const submitText = isEdit ? 'Update Task' : 'Create Task';

        const modalHtml = `
            <div id="task-form-modal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 fade-in">
                <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto slide-in-up">
                    <!-- Modal Header -->
                    <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between rounded-t-2xl">
                        <h2 class="text-2xl font-bold text-gray-800">${title}</h2>
                        <button id="close-modal-btn" class="text-gray-400 hover:text-gray-600 transition-colors">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>

                    <!-- Modal Body -->
                    <form id="task-form" class="p-6 space-y-6">
                        <!-- Title Field -->
                        <div>
                            <label for="task-title" class="block text-sm font-medium text-gray-700 mb-2">
                                Task Title <span class="text-red-500">*</span>
                            </label>
                            <input 
                                type="text" 
                                id="task-title" 
                                name="title"
                                required
                                maxlength="200"
                                value="${task ? this._escapeAttr(task.title) : ''}"
                                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                                placeholder="Enter task title"
                            />
                            <span class="text-red-500 text-sm hidden" id="title-error"></span>
                        </div>

                        <!-- Description Field -->
                        <div>
                            <label for="task-description" class="block text-sm font-medium text-gray-700 mb-2">
                                Description
                            </label>
                            <textarea 
                                id="task-description" 
                                name="description"
                                rows="4"
                                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all resize-none"
                                placeholder="Enter task description"
                            >${task ? this._escapeHtml(task.description || '') : ''}</textarea>
                        </div>

                        <!-- Priority & Status Row -->
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <!-- Priority Field -->
                            <div>
                                <label for="task-priority" class="block text-sm font-medium text-gray-700 mb-2">
                                    Priority <span class="text-red-500">*</span>
                                </label>
                                <select 
                                    id="task-priority" 
                                    name="priority"
                                    required
                                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                                >
                                    <option value="${Priority.Low}" ${task?.priority === Priority.Low ? 'selected' : ''}>Low</option>
                                    <option value="${Priority.Medium}" ${task?.priority === Priority.Medium || !task ? 'selected' : ''}>Medium</option>
                                    <option value="${Priority.High}" ${task?.priority === Priority.High ? 'selected' : ''}>High</option>
                                    <option value="${Priority.Critical}" ${task?.priority === Priority.Critical ? 'selected' : ''}>Critical</option>
                                </select>
                            </div>

                            <!-- Status Field (Edit mode only) -->
                            ${isEdit ? `
                                <div>
                                    <label for="task-status" class="block text-sm font-medium text-gray-700 mb-2">
                                        Status <span class="text-red-500">*</span>
                                    </label>
                                    <select 
                                        id="task-status" 
                                        name="status"
                                        required
                                        class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                                    >
                                        <option value="${Status.NotStarted}" ${task?.status === Status.NotStarted ? 'selected' : ''}>Not Started</option>
                                        <option value="${Status.InProgress}" ${task?.status === Status.InProgress ? 'selected' : ''}>In Progress</option>
                                        <option value="${Status.Blocked}" ${task?.status === Status.Blocked ? 'selected' : ''}>Blocked</option>
                                        <option value="${Status.Completed}" ${task?.status === Status.Completed ? 'selected' : ''}>Completed</option>
                                        <option value="${Status.Cancelled}" ${task?.status === Status.Cancelled ? 'selected' : ''}>Cancelled</option>
                                    </select>
                                </div>
                            ` : `
                                <input type="hidden" name="status" value="${Status.NotStarted}" />
                            `}
                        </div>

                        <!-- Due Date Field -->
                        <div>
                            <label for="task-due-date" class="block text-sm font-medium text-gray-700 mb-2">
                                Due Date
                            </label>
                            <input 
                                type="date" 
                                id="task-due-date" 
                                name="dueDate"
                                value="${task && task.dueDate ? new Date(task.dueDate).toISOString().split('T')[0] : ''}"
                                min="${new Date().toISOString().split('T')[0]}"
                                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                            />
                        </div>

                        <!-- Tags Field -->
                        <div>
                            <label for="task-tags" class="block text-sm font-medium text-gray-700 mb-2">
                                Tags <span class="text-gray-500 text-xs">(comma-separated)</span>
                            </label>
                            <input 
                                type="text" 
                                id="task-tags" 
                                name="tags"
                                value="${task && task.tags ? task.tags.join(', ') : ''}"
                                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                                placeholder="bug, feature, urgent"
                            />
                        </div>

                        <!-- Error Message -->
                        <div id="form-error" class="hidden bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
                        </div>

                        <!-- Hidden User ID -->
                        <input type="hidden" name="userId" value="${userId}" />
                    </form>

                    <!-- Modal Footer -->
                    <div class="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-6 py-4 flex items-center justify-end gap-3 rounded-b-2xl">
                        <button 
                            id="cancel-btn"
                            type="button"
                            class="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors duration-200 font-medium"
                        >
                            Cancel
                        </button>
                        <button 
                            id="submit-btn"
                            type="submit"
                            form="task-form"
                            class="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors duration-200 font-medium flex items-center"
                        >
                            <span id="submit-text">${submitText}</span>
                            <span id="submit-spinner" class="hidden ml-2">
                                <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                            </span>
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);
        this._attachHandlers(userId);
    }

    /**
     * Attach event handlers
     * @param {string} userId - Current user ID
     */
    _attachHandlers(userId) {
        const form = document.querySelector('#task-form');
        const closeBtn = document.querySelector('#close-modal-btn');
        const cancelBtn = document.querySelector('#cancel-btn');
        const modal = document.querySelector('#task-form-modal');

        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this._handleSubmit(e.target, userId);
            });
        }

        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.hide());
        }

        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.hide());
        }

        // Close on backdrop click
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hide();
                }
            });
        }

        // Close on Escape key
        document.addEventListener('keydown', this._escapeHandler = (e) => {
            if (e.key === 'Escape') {
                this.hide();
            }
        });
    }

    /**
     * Handle form submission
     * @param {HTMLFormElement} form - Form element
     * @param {string} userId - Current user ID
     */
    async _handleSubmit(form, userId) {
        const formData = new FormData(form);
        
        const taskData = {
            title: formData.get('title')?.trim(),
            description: formData.get('description')?.trim() || '',
            priority: parseInt(formData.get('priority')),
            status: parseInt(formData.get('status') || Status.NotStarted),
            dueDate: formData.get('dueDate') || null,
            tags: formData.get('tags')
                ?.split(',')
                .map(t => t.trim())
                .filter(t => t.length > 0) || []
        };

        // Clear previous errors
        this._clearErrors();

        // Validate
        if (!taskData.title) {
            this._showError('Task title is required');
            return;
        }

        if (taskData.title.length > 200) {
            this._showError('Task title must be 200 characters or less');
            return;
        }

        // Show loading
        this._setLoading(true);

        try {
            if (this.mode === 'create') {
                await this.taskService.createTask(userId, taskData);
                Logger.info('Task created successfully');
            } else {
                await this.taskService.updateTask(this.currentTaskId, taskData, userId);
                Logger.info('Task updated successfully');
            }

            // Close modal
            this.hide();

            // Trigger task list refresh
            window.dispatchEvent(new CustomEvent('taskChanged'));

            // Show success toast
            window.dispatchEvent(new CustomEvent('showToast', {
                detail: { 
                    message: `Task ${this.mode === 'create' ? 'created' : 'updated'} successfully`,
                    type: 'success' 
                }
            }));
        } catch (error) {
            Logger.error(`${this.mode === 'create' ? 'Create' : 'Update'} task error:`, error);
            this._showError(error.message || 'Failed to save task');
        } finally {
            this._setLoading(false);
        }
    }

    /**
     * Show error message
     * @param {string} message - Error message
     */
    _showError(message) {
        const errorDiv = document.querySelector('#form-error');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.classList.remove('hidden');
        }
    }

    /**
     * Clear errors
     */
    _clearErrors() {
        const errorDiv = document.querySelector('#form-error');
        if (errorDiv) {
            errorDiv.classList.add('hidden');
        }
    }

    /**
     * Set loading state
     * @param {boolean} isLoading - Loading state
     */
    _setLoading(isLoading) {
        const submitBtn = document.querySelector('#submit-btn');
        const submitText = document.querySelector('#submit-text');
        const submitSpinner = document.querySelector('#submit-spinner');

        if (submitBtn) {
            submitBtn.disabled = isLoading;
        }

        if (submitText) {
            submitText.classList.toggle('hidden', isLoading);
        }

        if (submitSpinner) {
            submitSpinner.classList.toggle('hidden', !isLoading);
        }
    }

    /**
     * Escape HTML attribute
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    _escapeAttr(text) {
        return text.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }

    /**
     * Escape HTML content
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
