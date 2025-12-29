/**
 * Repository Layer
 * Data access layer using Repository pattern
 * 
 * @author Asif Hussain
 * @version 1.0.0
 */

import { Logger } from '../utils/logger.js';
import { getDatabase } from './mock-db.js';
import { Task, User } from '../domain/entities.js';
import { Status, Priority } from '../domain/enums.js';

/**
 * Base Repository
 * Provides common CRUD operations
 */
class BaseRepository {
    constructor(collectionName) {
        this.collectionName = collectionName;
        this.db = getDatabase();
        Logger.debug(`${this.constructor.name} initialized`);
    }

    /**
     * Get collection from database
     * @returns {Array} Collection array
     */
    getCollection() {
        return this.db[this.collectionName];
    }

    /**
     * Save changes to storage
     */
    save() {
        this.db.saveToStorage();
    }
}

/**
 * Task Repository
 * Manages task data access
 */
export class TaskRepository extends BaseRepository {
    constructor() {
        super('tasks');
    }

    /**
     * Get all tasks
     * @returns {Promise<Task[]>} Array of tasks
     */
    async getAll() {
        Logger.debug('TaskRepository.getAll called');
        return [...this.getCollection()];
    }

    /**
     * Get task by ID
     * @param {string} id - Task ID
     * @returns {Promise<Task|null>} Task or null if not found
     */
    async getById(id) {
        Logger.debug(`TaskRepository.getById called: ${id}`);
        const task = this.getCollection().find(t => t.id === id);
        return task || null;
    }

    /**
     * Get tasks with filters
     * @param {Object} filters - Filter criteria
     * @param {number} [filters.status] - Filter by status
     * @param {number} [filters.priority] - Filter by priority
     * @param {string} [filters.assignedTo] - Filter by assigned user
     * @param {string} [filters.createdBy] - Filter by creator
     * @param {string} [filters.tag] - Filter by tag
     * @param {boolean} [filters.overdue] - Filter overdue tasks
     * @returns {Promise<Task[]>} Filtered tasks
     */
    async getFiltered(filters = {}) {
        Logger.debug('TaskRepository.getFiltered called', filters);
        
        let results = [...this.getCollection()];

        if (filters.status !== undefined) {
            results = results.filter(t => t.status === filters.status);
        }

        if (filters.priority !== undefined) {
            results = results.filter(t => t.priority === filters.priority);
        }

        if (filters.assignedTo) {
            results = results.filter(t => t.assignedTo === filters.assignedTo);
        }

        if (filters.createdBy) {
            results = results.filter(t => t.createdBy === filters.createdBy);
        }

        if (filters.tag) {
            results = results.filter(t => t.tags.includes(filters.tag));
        }

        if (filters.overdue === true) {
            results = results.filter(t => t.isOverdue());
        }

        return results;
    }

    /**
     * Create new task
     * @param {Object} taskData - Task data
     * @returns {Promise<Task>} Created task
     */
    async create(taskData) {
        Logger.debug('TaskRepository.create called', taskData);

        const task = new Task(
            taskData.title,
            taskData.description,
            taskData.priority,
            taskData.status,
            null, // ID will be generated
            taskData.assignedTo,
            taskData.createdBy,
            null, // createdDate will be set to now
            taskData.dueDate ? new Date(taskData.dueDate) : null,
            taskData.tags
        );

        this.getCollection().push(task);
        this.save();

        Logger.info(`Task created: ${task.id}`);
        return task;
    }

    /**
     * Update existing task
     * @param {string} id - Task ID
     * @param {Object} updates - Fields to update
     * @returns {Promise<Task|null>} Updated task or null if not found
     */
    async update(id, updates) {
        Logger.debug(`TaskRepository.update called: ${id}`, updates);

        const collection = this.getCollection();
        const index = collection.findIndex(t => t.id === id);

        if (index === -1) {
            Logger.warn(`Task not found: ${id}`);
            return null;
        }

        const task = collection[index];

        // Update allowed fields
        if (updates.title !== undefined) task.title = updates.title;
        if (updates.description !== undefined) task.description = updates.description;
        if (updates.priority !== undefined) task.priority = updates.priority;
        if (updates.status !== undefined) task.status = updates.status;
        if (updates.assignedTo !== undefined) task.assignedTo = updates.assignedTo;
        if (updates.dueDate !== undefined) task.dueDate = updates.dueDate ? new Date(updates.dueDate) : null;
        if (updates.tags !== undefined) task.tags = updates.tags;

        this.save();

        Logger.info(`Task updated: ${id}`);
        return task;
    }

    /**
     * Delete task
     * @param {string} id - Task ID
     * @returns {Promise<boolean>} True if deleted
     */
    async delete(id) {
        Logger.debug(`TaskRepository.delete called: ${id}`);

        const collection = this.getCollection();
        const index = collection.findIndex(t => t.id === id);

        if (index === -1) {
            Logger.warn(`Task not found: ${id}`);
            return false;
        }

        collection.splice(index, 1);
        this.save();

        Logger.info(`Task deleted: ${id}`);
        return true;
    }

    /**
     * Get tasks assigned to user
     * @param {string} userId - User ID
     * @returns {Promise<Task[]>} User's tasks
     */
    async getByAssignee(userId) {
        return this.getFiltered({ assignedTo: userId });
    }

    /**
     * Get tasks created by user
     * @param {string} userId - User ID
     * @returns {Promise<Task[]>} Tasks created by user
     */
    async getByCreator(userId) {
        return this.getFiltered({ createdBy: userId });
    }

    /**
     * Search tasks by keyword
     * @param {string} keyword - Search keyword
     * @returns {Promise<Task[]>} Matching tasks
     */
    async search(keyword) {
        Logger.debug(`TaskRepository.search called: ${keyword}`);

        const lowerKeyword = keyword.toLowerCase();
        return this.getCollection().filter(t =>
            t.title.toLowerCase().includes(lowerKeyword) ||
            t.description.toLowerCase().includes(lowerKeyword) ||
            t.tags.some(tag => tag.toLowerCase().includes(lowerKeyword))
        );
    }
}

/**
 * User Repository
 * Manages user data access
 */
export class UserRepository extends BaseRepository {
    constructor() {
        super('users');
    }

    /**
     * Get all users
     * @returns {Promise<User[]>} Array of users
     */
    async getAll() {
        Logger.debug('UserRepository.getAll called');
        return [...this.getCollection()];
    }

    /**
     * Get user by ID
     * @param {string} id - User ID
     * @returns {Promise<User|null>} User or null if not found
     */
    async getById(id) {
        Logger.debug(`UserRepository.getById called: ${id}`);
        const user = this.getCollection().find(u => u.id === id);
        return user || null;
    }

    /**
     * Get user by username
     * @param {string} username - Username
     * @returns {Promise<User|null>} User or null if not found
     */
    async getByUsername(username) {
        Logger.debug(`UserRepository.getByUsername called: ${username}`);
        const user = this.getCollection().find(u => u.username === username);
        return user || null;
    }

    /**
     * Get user by email
     * @param {string} email - Email address
     * @returns {Promise<User|null>} User or null if not found
     */
    async getByEmail(email) {
        Logger.debug(`UserRepository.getByEmail called: ${email}`);
        const normalizedEmail = email.toLowerCase();
        const user = this.getCollection().find(u => u.email === normalizedEmail);
        return user || null;
    }

    /**
     * Create new user
     * @param {Object} userData - User data
     * @returns {Promise<User>} Created user
     */
    async create(userData) {
        Logger.debug('UserRepository.create called', { username: userData.username });

        // Check for duplicates
        const existingUsername = await this.getByUsername(userData.username);
        if (existingUsername) {
            throw new Error('Username already exists');
        }

        const existingEmail = await this.getByEmail(userData.email);
        if (existingEmail) {
            throw new Error('Email already exists');
        }

        const user = new User(
            userData.username,
            userData.email,
            userData.passwordHash,
            userData.role,
            null, // ID will be generated
            userData.fullName
        );

        this.getCollection().push(user);
        this.save();

        Logger.info(`User created: ${user.id} (${user.username})`);
        return user;
    }

    /**
     * Update existing user
     * @param {string} id - User ID
     * @param {Object} updates - Fields to update
     * @returns {Promise<User|null>} Updated user or null if not found
     */
    async update(id, updates) {
        Logger.debug(`UserRepository.update called: ${id}`, updates);

        const collection = this.getCollection();
        const index = collection.findIndex(u => u.id === id);

        if (index === -1) {
            Logger.warn(`User not found: ${id}`);
            return null;
        }

        const user = collection[index];

        // Update allowed fields
        if (updates.email !== undefined) user.email = updates.email.toLowerCase();
        if (updates.fullName !== undefined) user.fullName = updates.fullName;
        if (updates.role !== undefined) user.role = updates.role;
        if (updates.isActive !== undefined) user.isActive = updates.isActive;
        if (updates.passwordHash !== undefined) user.passwordHash = updates.passwordHash;

        this.save();

        Logger.info(`User updated: ${id}`);
        return user;
    }

    /**
     * Delete user
     * @param {string} id - User ID
     * @returns {Promise<boolean>} True if deleted
     */
    async delete(id) {
        Logger.debug(`UserRepository.delete called: ${id}`);

        const collection = this.getCollection();
        const index = collection.findIndex(u => u.id === id);

        if (index === -1) {
            Logger.warn(`User not found: ${id}`);
            return false;
        }

        collection.splice(index, 1);
        this.save();

        Logger.info(`User deleted: ${id}`);
        return true;
    }

    /**
     * Get users by role
     * @param {number} role - Role value
     * @returns {Promise<User[]>} Users with specified role
     */
    async getByRole(role) {
        Logger.debug(`UserRepository.getByRole called: ${role}`);
        return this.getCollection().filter(u => u.role === role);
    }

    /**
     * Get active users
     * @returns {Promise<User[]>} Active users
     */
    async getActive() {
        Logger.debug('UserRepository.getActive called');
        return this.getCollection().filter(u => u.isActive);
    }
}

export default { TaskRepository, UserRepository };
