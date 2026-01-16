/**
 * Domain Entities
 * Core business entities for task management
 * 
 * @author Asif Hussain
 * @version 1.0.0
 */

import { Priority, Status, Role } from './enums.js';

/**
 * Generate unique ID
 * @returns {string} Unique identifier
 */
function generateId() {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Validate email format
 * @param {string} email - Email address
 * @returns {boolean} True if valid
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Task Entity
 * Represents a work item in the system
 */
export class Task {
    /**
     * Create a new task
     * @param {string} title - Task title
     * @param {string} description - Task description
     * @param {number} priority - Priority level (from Priority enum)
     * @param {number} status - Task status (from Status enum)
     * @param {string} [id] - Optional task ID (generated if not provided)
     * @param {string} [assignedTo] - User ID assigned to task
     * @param {string} [createdBy] - User ID who created task
     * @param {Date} [createdDate] - Creation timestamp
     * @param {Date} [dueDate] - Due date
     * @param {string[]} [tags] - Task tags
     */
    constructor(title, description, priority, status, id = null, assignedTo = null, createdBy = null, createdDate = null, dueDate = null, tags = []) {
        // Validation
        if (!title || title.trim() === '') {
            throw new Error('Task title is required');
        }
        if (title.length > 200) {
            throw new Error('Task title must be 200 characters or less');
        }
        if (!Object.values(Priority).includes(priority)) {
            throw new Error('Invalid priority value');
        }
        if (!Object.values(Status).includes(status)) {
            throw new Error('Invalid status value');
        }

        this.id = id || generateId();
        this.title = title.trim();
        this.description = description ? description.trim() : '';
        this.priority = priority;
        this.status = status;
        this.assignedTo = assignedTo;
        this.createdBy = createdBy;
        this.createdDate = createdDate || new Date();
        this.dueDate = dueDate;
        this.tags = tags || [];
        this.comments = [];
    }

    /**
     * Check if task is overdue
     * @returns {boolean} True if overdue
     */
    isOverdue() {
        if (!this.dueDate || this.status === Status.Completed || this.status === Status.Cancelled) {
            return false;
        }
        return new Date() > new Date(this.dueDate);
    }

    /**
     * Check if task is completed
     * @returns {boolean} True if completed
     */
    isCompleted() {
        return this.status === Status.Completed;
    }

    /**
     * Add comment to task
     * @param {Comment} comment - Comment to add
     */
    addComment(comment) {
        this.comments.push(comment);
    }

    /**
     * Convert to plain object for serialization
     * @returns {Object} Plain object
     */
    toJSON() {
        return {
            id: this.id,
            title: this.title,
            description: this.description,
            priority: this.priority,
            status: this.status,
            assignedTo: this.assignedTo,
            createdBy: this.createdBy,
            createdDate: this.createdDate,
            dueDate: this.dueDate,
            tags: this.tags,
            comments: this.comments
        };
    }

    /**
     * Create Task from plain object
     * @param {Object} obj - Plain object
     * @returns {Task} Task instance
     */
    static fromJSON(obj) {
        const task = new Task(
            obj.title,
            obj.description,
            obj.priority,
            obj.status,
            obj.id,
            obj.assignedTo,
            obj.createdBy,
            obj.createdDate ? new Date(obj.createdDate) : null,
            obj.dueDate ? new Date(obj.dueDate) : null,
            obj.tags
        );
        if (obj.comments) {
            task.comments = obj.comments.map(c => Comment.fromJSON(c));
        }
        return task;
    }
}

/**
 * User Entity
 * Represents a system user
 */
export class User {
    /**
     * Create a new user
     * @param {string} username - Username
     * @param {string} email - Email address
     * @param {string} passwordHash - Hashed password
     * @param {number} role - User role (from Role enum)
     * @param {string} [id] - Optional user ID
     * @param {string} [fullName] - Full name
     * @param {Date} [createdDate] - Creation timestamp
     */
    constructor(username, email, passwordHash, role, id = null, fullName = '', createdDate = null) {
        // Validation
        if (!username || username.trim() === '') {
            throw new Error('Username is required');
        }
        if (username.length < 3 || username.length > 50) {
            throw new Error('Username must be between 3 and 50 characters');
        }
        if (!email || !isValidEmail(email)) {
            throw new Error('Valid email address is required');
        }
        if (!passwordHash || passwordHash.trim() === '') {
            throw new Error('Password hash is required');
        }
        if (!Object.values(Role).includes(role)) {
            throw new Error('Invalid role value');
        }

        this.id = id || generateId();
        this.username = username.trim();
        this.email = email.trim().toLowerCase();
        this.passwordHash = passwordHash;
        this.role = role;
        this.fullName = fullName ? fullName.trim() : '';
        this.createdDate = createdDate || new Date();
        this.isActive = true;
    }

    /**
     * Check if user has admin privileges
     * @returns {boolean} True if admin
     */
    isAdmin() {
        return this.role === Role.Admin;
    }

    /**
     * Check if user has team lead privileges
     * @returns {boolean} True if team lead or admin
     */
    isTeamLead() {
        return this.role === Role.TeamLead || this.role === Role.Admin;
    }

    /**
     * Convert to plain object (without password hash)
     * @returns {Object} Plain object
     */
    toJSON() {
        return {
            id: this.id,
            username: this.username,
            email: this.email,
            role: this.role,
            fullName: this.fullName,
            createdDate: this.createdDate,
            isActive: this.isActive
        };
    }

    /**
     * Convert to plain object with password hash (for storage)
     * @returns {Object} Plain object with password
     */
    toStorageJSON() {
        return {
            ...this.toJSON(),
            passwordHash: this.passwordHash
        };
    }

    /**
     * Create User from plain object
     * @param {Object} obj - Plain object
     * @returns {User} User instance
     */
    static fromJSON(obj) {
        const user = new User(
            obj.username,
            obj.email,
            obj.passwordHash || '',
            obj.role,
            obj.id,
            obj.fullName,
            obj.createdDate ? new Date(obj.createdDate) : null
        );
        user.isActive = obj.isActive !== undefined ? obj.isActive : true;
        return user;
    }
}

/**
 * Comment Entity
 * Represents a comment on a task
 */
export class Comment {
    /**
     * Create a new comment
     * @param {string} text - Comment text
     * @param {string} userId - User ID who created comment
     * @param {string} [id] - Optional comment ID
     * @param {Date} [createdDate] - Creation timestamp
     */
    constructor(text, userId, id = null, createdDate = null) {
        // Validation
        if (!text || text.trim() === '') {
            throw new Error('Comment text is required');
        }
        if (!userId || userId.trim() === '') {
            throw new Error('User ID is required');
        }

        this.id = id || generateId();
        this.text = text.trim();
        this.userId = userId;
        this.createdDate = createdDate || new Date();
    }

    /**
     * Convert to plain object
     * @returns {Object} Plain object
     */
    toJSON() {
        return {
            id: this.id,
            text: this.text,
            userId: this.userId,
            createdDate: this.createdDate
        };
    }

    /**
     * Create Comment from plain object
     * @param {Object} obj - Plain object
     * @returns {Comment} Comment instance
     */
    static fromJSON(obj) {
        return new Comment(
            obj.text,
            obj.userId,
            obj.id,
            obj.createdDate ? new Date(obj.createdDate) : null
        );
    }
}

export default { Task, User, Comment };
