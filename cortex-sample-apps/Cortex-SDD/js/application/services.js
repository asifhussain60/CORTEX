/**
 * Application Services
 * Business logic and use case orchestration
 * 
 * @author Asif Hussain
 * @version 1.0.0
 */

import { Logger } from '../utils/logger.js';
import { TaskRepository, UserRepository } from '../infrastructure/repositories.js';
import { PasswordHasher, JWTManager, AuthManager, AuthorizationHelper } from '../infrastructure/security.js';
import { TaskValidator, UserValidator } from './validators.js';
import { TaskDTO, UserDTO, AuthResponseDTO, TaskFilterDTO } from './dtos.js';
import { Status, Role } from '../domain/enums.js';
import { Comment } from '../domain/entities.js';

/**
 * Task Service
 * Manages task-related business logic
 */
export class TaskService {
    constructor() {
        this.taskRepo = new TaskRepository();
        this.userRepo = new UserRepository();
        Logger.info('TaskService initialized');
    }

    /**
     * Get all tasks
     * @returns {Promise<TaskDTO[]>} Array of task DTOs
     */
    async getAllTasks() {
        Logger.debug('TaskService.getAllTasks called');
        const tasks = await this.taskRepo.getAll();
        return tasks.map(t => TaskDTO.fromEntity(t));
    }

    /**
     * Get task by ID
     * @param {string} id - Task ID
     * @returns {Promise<TaskDTO|null>} Task DTO or null
     */
    async getTaskById(id) {
        Logger.debug(`TaskService.getTaskById called: ${id}`);
        
        if (!id) {
            throw new Error('Task ID is required');
        }

        const task = await this.taskRepo.getById(id);
        return task ? TaskDTO.fromEntity(task) : null;
    }

    /**
     * Get tasks with filters
     * @param {TaskFilterDTO} filterDto - Filter criteria
     * @returns {Promise<TaskDTO[]>} Filtered tasks
     */
    async getTasks(filterDto) {
        Logger.debug('TaskService.getTasks called', filterDto);

        // Validate filters
        const validation = TaskValidator.validateFilter(filterDto.toRepositoryFilter());
        if (!validation.isValid) {
            throw new Error(`Invalid filters: ${validation.errors.join(', ')}`);
        }

        // Get filtered tasks
        let tasks = await this.taskRepo.getFiltered(filterDto.toRepositoryFilter());

        // Apply search if provided
        if (filterDto.searchKeyword) {
            tasks = tasks.filter(t => 
                t.title.toLowerCase().includes(filterDto.searchKeyword.toLowerCase()) ||
                t.description.toLowerCase().includes(filterDto.searchKeyword.toLowerCase()) ||
                t.tags.some(tag => tag.toLowerCase().includes(filterDto.searchKeyword.toLowerCase()))
            );
        }

        return tasks.map(t => TaskDTO.fromEntity(t));
    }

    /**
     * Get tasks assigned to user
     * @param {string} userId - User ID
     * @returns {Promise<TaskDTO[]>} User's tasks
     */
    async getMyTasks(userId) {
        Logger.debug(`TaskService.getMyTasks called: ${userId}`);
        
        if (!userId) {
            throw new Error('User ID is required');
        }

        const tasks = await this.taskRepo.getByAssignee(userId);
        return tasks.map(t => TaskDTO.fromEntity(t));
    }

    /**
     * Create new task
     * @param {TaskDTO} taskDto - Task data
     * @param {string} currentUserId - Current user ID
     * @returns {Promise<TaskDTO>} Created task
     */
    async createTask(taskDto, currentUserId) {
        Logger.debug('TaskService.createTask called');

        // Validate input
        const validation = TaskValidator.validateCreate(taskDto.toObject());
        if (!validation.isValid) {
            const errorMsg = `Validation failed: ${validation.errors.join(', ')}`;
            Logger.warn(errorMsg);
            throw new Error(errorMsg);
        }

        // Check if assignee exists (if provided)
        if (taskDto.assignedTo) {
            const assignee = await this.userRepo.getById(taskDto.assignedTo);
            if (!assignee) {
                throw new Error('Assigned user does not exist');
            }
            if (!assignee.isActive) {
                throw new Error('Cannot assign task to inactive user');
            }
        }

        // Set creator
        taskDto.createdBy = currentUserId;

        // Create task
        const task = await this.taskRepo.create(taskDto.toObject());
        Logger.info(`Task created: ${task.id}`);

        return TaskDTO.fromEntity(task);
    }

    /**
     * Update existing task
     * @param {string} id - Task ID
     * @param {Object} updates - Fields to update
     * @param {string} currentUserId - Current user ID
     * @returns {Promise<TaskDTO|null>} Updated task
     */
    async updateTask(id, updates, currentUserId) {
        Logger.debug(`TaskService.updateTask called: ${id}`);

        // Validate ID
        if (!id) {
            throw new Error('Task ID is required');
        }

        // Validate updates
        const validation = TaskValidator.validateUpdate(updates);
        if (!validation.isValid) {
            const errorMsg = `Validation failed: ${validation.errors.join(', ')}`;
            Logger.warn(errorMsg);
            throw new Error(errorMsg);
        }

        // Check task exists
        const existingTask = await this.taskRepo.getById(id);
        if (!existingTask) {
            throw new Error('Task not found');
        }

        // Check authorization
        const currentUser = await this.userRepo.getById(currentUserId);
        if (!AuthorizationHelper.canEditTask(currentUser, existingTask)) {
            throw new Error('Not authorized to edit this task');
        }

        // Check assignee exists (if changing)
        if (updates.assignedTo) {
            const assignee = await this.userRepo.getById(updates.assignedTo);
            if (!assignee) {
                throw new Error('Assigned user does not exist');
            }
            if (!assignee.isActive) {
                throw new Error('Cannot assign task to inactive user');
            }
        }

        // Update task
        const updated = await this.taskRepo.update(id, updates);
        Logger.info(`Task updated: ${id}`);

        return updated ? TaskDTO.fromEntity(updated) : null;
    }

    /**
     * Delete task
     * @param {string} id - Task ID
     * @param {string} currentUserId - Current user ID
     * @returns {Promise<boolean>} True if deleted
     */
    async deleteTask(id, currentUserId) {
        Logger.debug(`TaskService.deleteTask called: ${id}`);

        // Validate ID
        if (!id) {
            throw new Error('Task ID is required');
        }

        // Check task exists
        const existingTask = await this.taskRepo.getById(id);
        if (!existingTask) {
            throw new Error('Task not found');
        }

        // Check authorization
        const currentUser = await this.userRepo.getById(currentUserId);
        if (!AuthorizationHelper.canDeleteTask(currentUser, existingTask)) {
            throw new Error('Not authorized to delete this task');
        }

        // Delete task
        const result = await this.taskRepo.delete(id);
        Logger.info(`Task deleted: ${id}`);

        return result;
    }

    /**
     * Add comment to task
     * @param {string} taskId - Task ID
     * @param {string} commentText - Comment text
     * @param {string} userId - User ID
     * @returns {Promise<TaskDTO>} Updated task
     */
    async addComment(taskId, commentText, userId) {
        Logger.debug(`TaskService.addComment called: ${taskId}`);

        // Validate inputs
        if (!taskId) throw new Error('Task ID is required');
        if (!commentText || commentText.trim() === '') throw new Error('Comment text is required');
        if (!userId) throw new Error('User ID is required');

        // Get task
        const task = await this.taskRepo.getById(taskId);
        if (!task) throw new Error('Task not found');

        // Create comment
        const comment = new Comment(commentText, userId);
        task.addComment(comment);

        // Save
        await this.taskRepo.update(taskId, { comments: task.comments });
        Logger.info(`Comment added to task: ${taskId}`);

        return TaskDTO.fromEntity(task);
    }

    /**
     * Get task statistics
     * @returns {Promise<Object>} Statistics
     */
    async getStatistics() {
        Logger.debug('TaskService.getStatistics called');

        const allTasks = await this.taskRepo.getAll();

        const stats = {
            total: allTasks.length,
            byStatus: {},
            byPriority: {},
            overdue: allTasks.filter(t => t.isOverdue()).length,
            completed: allTasks.filter(t => t.isCompleted()).length,
            completionRate: 0
        };

        // Count by status
        allTasks.forEach(task => {
            stats.byStatus[task.status] = (stats.byStatus[task.status] || 0) + 1;
            stats.byPriority[task.priority] = (stats.byPriority[task.priority] || 0) + 1;
        });

        // Calculate completion rate
        if (stats.total > 0) {
            stats.completionRate = Math.round((stats.completed / stats.total) * 100);
        }

        return stats;
    }
}

/**
 * Authentication Service
 * Manages authentication and user registration
 */
export class AuthService {
    constructor() {
        this.userRepo = new UserRepository();
        Logger.info('AuthService initialized');
    }

    /**
     * Authenticate user
     * @param {string} username - Username
     * @param {string} password - Password
     * @returns {Promise<AuthResponseDTO>} Authentication result
     */
    async login(username, password) {
        Logger.debug(`AuthService.login called: ${username}`);

        // Validate input
        const validation = UserValidator.validateLogin(username, password);
        if (!validation.isValid) {
            const errorMsg = `Validation failed: ${validation.errors.join(', ')}`;
            Logger.warn(errorMsg);
            throw new Error(errorMsg);
        }

        // Find user
        const user = await this.userRepo.getByUsername(username);
        if (!user) {
            Logger.warn(`Login failed: User not found - ${username}`);
            throw new Error('Invalid username or password');
        }

        // Check if user is active
        if (!user.isActive) {
            Logger.warn(`Login failed: User inactive - ${username}`);
            throw new Error('User account is inactive');
        }

        // Verify password
        const passwordValid = PasswordHasher.verify(password, user.passwordHash);
        if (!passwordValid) {
            Logger.warn(`Login failed: Invalid password - ${username}`);
            throw new Error('Invalid username or password');
        }

        // Generate token
        const token = JWTManager.generate({
            userId: user.id,
            username: user.username,
            role: user.role
        });

        // Save authentication state
        AuthManager.saveAuth(token, user);

        Logger.info(`User logged in: ${username}`);
        return new AuthResponseDTO(token, user);
    }

    /**
     * Register new user
     * @param {RegisterDTO} registerDto - Registration data
     * @returns {Promise<AuthResponseDTO>} Registration result
     */
    async register(registerDto) {
        Logger.debug('AuthService.register called', { username: registerDto.username });

        // Validate input
        const validation = UserValidator.validateRegister(registerDto);
        if (!validation.isValid) {
            const errorMsg = `Validation failed: ${validation.errors.join(', ')}`;
            Logger.warn(errorMsg);
            throw new Error(errorMsg);
        }

        // Check if username exists
        const existingUsername = await this.userRepo.getByUsername(registerDto.username);
        if (existingUsername) {
            throw new Error('Username already exists');
        }

        // Check if email exists
        const existingEmail = await this.userRepo.getByEmail(registerDto.email);
        if (existingEmail) {
            throw new Error('Email already exists');
        }

        // Hash password
        const passwordHash = PasswordHasher.hash(registerDto.password);

        // Create user
        const userData = {
            username: registerDto.username,
            email: registerDto.email,
            passwordHash: passwordHash,
            role: registerDto.role || Role.User,
            fullName: registerDto.fullName
        };

        const user = await this.userRepo.create(userData);

        // Generate token
        const token = JWTManager.generate({
            userId: user.id,
            username: user.username,
            role: user.role
        });

        // Save authentication state
        AuthManager.saveAuth(token, user);

        Logger.info(`User registered: ${user.username}`);
        return new AuthResponseDTO(token, user);
    }

    /**
     * Logout current user
     */
    logout() {
        Logger.debug('AuthService.logout called');
        AuthManager.clearAuth();
        Logger.info('User logged out');
    }

    /**
     * Get current authenticated user
     * @returns {UserDTO|null} Current user or null
     */
    getCurrentUser() {
        Logger.debug('AuthService.getCurrentUser called');
        const user = AuthManager.getCurrentUser();
        return user ? new UserDTO(user) : null;
    }

    /**
     * Check if user is authenticated
     * @returns {boolean} True if authenticated
     */
    isAuthenticated() {
        return AuthManager.isAuthenticated();
    }

    /**
     * Refresh authentication token
     * @returns {boolean} True if refreshed
     */
    refreshToken() {
        return AuthManager.refreshTokenIfNeeded();
    }

    /**
     * Change user password
     * @param {string} userId - User ID
     * @param {string} currentPassword - Current password
     * @param {string} newPassword - New password
     * @returns {Promise<boolean>} True if changed
     */
    async changePassword(userId, currentPassword, newPassword) {
        Logger.debug(`AuthService.changePassword called: ${userId}`);

        // Get user
        const user = await this.userRepo.getById(userId);
        if (!user) {
            throw new Error('User not found');
        }

        // Verify current password
        const passwordValid = PasswordHasher.verify(currentPassword, user.passwordHash);
        if (!passwordValid) {
            throw new Error('Current password is incorrect');
        }

        // Validate new password
        const validation = PasswordHasher.validateStrength(newPassword);
        if (!validation.isValid) {
            throw new Error(`Password validation failed: ${validation.errors.join(', ')}`);
        }

        // Hash new password
        const newPasswordHash = PasswordHasher.hash(newPassword);

        // Update user
        await this.userRepo.update(userId, { passwordHash: newPasswordHash });

        Logger.info(`Password changed for user: ${userId}`);
        return true;
    }
}

/**
 * User Service
 * Manages user-related operations
 */
export class UserService {
    constructor() {
        this.userRepo = new UserRepository();
        Logger.info('UserService initialized');
    }

    /**
     * Get all users
     * @returns {Promise<UserDTO[]>} Array of users
     */
    async getAllUsers() {
        Logger.debug('UserService.getAllUsers called');
        const users = await this.userRepo.getAll();
        return users.map(u => UserDTO.fromEntity(u));
    }

    /**
     * Get user by ID
     * @param {string} id - User ID
     * @returns {Promise<UserDTO|null>} User DTO or null
     */
    async getUserById(id) {
        Logger.debug(`UserService.getUserById called: ${id}`);
        const user = await this.userRepo.getById(id);
        return user ? UserDTO.fromEntity(user) : null;
    }

    /**
     * Get active users
     * @returns {Promise<UserDTO[]>} Active users
     */
    async getActiveUsers() {
        Logger.debug('UserService.getActiveUsers called');
        const users = await this.userRepo.getActive();
        return users.map(u => UserDTO.fromEntity(u));
    }

    /**
     * Update user profile
     * @param {string} id - User ID
     * @param {Object} updates - Updates
     * @param {string} currentUserId - Current user ID
     * @returns {Promise<UserDTO|null>} Updated user
     */
    async updateUser(id, updates, currentUserId) {
        Logger.debug(`UserService.updateUser called: ${id}`);

        // Validate updates
        const validation = UserValidator.validateUpdate(updates);
        if (!validation.isValid) {
            throw new Error(`Validation failed: ${validation.errors.join(', ')}`);
        }

        // Check authorization (users can only update themselves unless admin)
        const currentUser = await this.userRepo.getById(currentUserId);
        if (id !== currentUserId && !AuthorizationHelper.canManageUsers(currentUser)) {
            throw new Error('Not authorized to update this user');
        }

        // Update user
        const updated = await this.userRepo.update(id, updates);
        Logger.info(`User updated: ${id}`);

        return updated ? UserDTO.fromEntity(updated) : null;
    }

    /**
     * Deactivate user
     * @param {string} id - User ID
     * @param {string} currentUserId - Current user ID
     * @returns {Promise<boolean>} True if deactivated
     */
    async deactivateUser(id, currentUserId) {
        Logger.debug(`UserService.deactivateUser called: ${id}`);

        // Check authorization
        const currentUser = await this.userRepo.getById(currentUserId);
        if (!AuthorizationHelper.canManageUsers(currentUser)) {
            throw new Error('Not authorized to deactivate users');
        }

        // Cannot deactivate self
        if (id === currentUserId) {
            throw new Error('Cannot deactivate your own account');
        }

        // Deactivate
        const updated = await this.userRepo.update(id, { isActive: false });
        Logger.info(`User deactivated: ${id}`);

        return updated !== null;
    }
}

export default {
    TaskService,
    AuthService,
    UserService
};
