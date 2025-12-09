/**
 * Data Transfer Objects (DTOs)
 * Define data structures for transferring data between layers
 * 
 * @author Asif Hussain
 * @version 1.0.0
 */

/**
 * Task Data Transfer Object
 */
export class TaskDTO {
    constructor(data = {}) {
        this.id = data.id || null;
        this.title = data.title || '';
        this.description = data.description || '';
        this.priority = data.priority || 2; // Default to Medium
        this.status = data.status || 1; // Default to Open
        this.assignedTo = data.assignedTo || null;
        this.createdBy = data.createdBy || null;
        this.createdDate = data.createdDate || null;
        this.dueDate = data.dueDate || null;
        this.tags = data.tags || [];
        this.comments = data.comments || [];
    }

    /**
     * Create DTO from domain entity
     * @param {Task} task - Task entity
     * @returns {TaskDTO} Task DTO
     */
    static fromEntity(task) {
        return new TaskDTO({
            id: task.id,
            title: task.title,
            description: task.description,
            priority: task.priority,
            status: task.status,
            assignedTo: task.assignedTo,
            createdBy: task.createdBy,
            createdDate: task.createdDate,
            dueDate: task.dueDate,
            tags: task.tags,
            comments: task.comments
        });
    }

    /**
     * Convert to plain object
     * @returns {Object} Plain object
     */
    toObject() {
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
}

/**
 * User Data Transfer Object
 */
export class UserDTO {
    constructor(data = {}) {
        this.id = data.id || null;
        this.username = data.username || '';
        this.email = data.email || '';
        this.role = data.role || 1; // Default to User
        this.fullName = data.fullName || '';
        this.createdDate = data.createdDate || null;
        this.isActive = data.isActive !== undefined ? data.isActive : true;
    }

    /**
     * Create DTO from domain entity
     * @param {User} user - User entity
     * @returns {UserDTO} User DTO
     */
    static fromEntity(user) {
        return new UserDTO({
            id: user.id,
            username: user.username,
            email: user.email,
            role: user.role,
            fullName: user.fullName,
            createdDate: user.createdDate,
            isActive: user.isActive
        });
    }

    /**
     * Convert to plain object
     * @returns {Object} Plain object
     */
    toObject() {
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
}

/**
 * Login Request DTO
 */
export class LoginDTO {
    constructor(username, password) {
        this.username = username || '';
        this.password = password || '';
    }

    /**
     * Validate login data
     * @returns {Object} Validation result
     */
    validate() {
        const errors = [];

        if (!this.username || this.username.trim() === '') {
            errors.push('Username is required');
        }

        if (!this.password || this.password.trim() === '') {
            errors.push('Password is required');
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }
}

/**
 * Register Request DTO
 */
export class RegisterDTO {
    constructor(data = {}) {
        this.username = data.username || '';
        this.email = data.email || '';
        this.password = data.password || '';
        this.confirmPassword = data.confirmPassword || '';
        this.fullName = data.fullName || '';
        this.role = data.role || 1; // Default to User
    }

    /**
     * Validate registration data
     * @returns {Object} Validation result
     */
    validate() {
        const errors = [];

        if (!this.username || this.username.trim() === '') {
            errors.push('Username is required');
        } else if (this.username.length < 3) {
            errors.push('Username must be at least 3 characters');
        } else if (this.username.length > 50) {
            errors.push('Username must be 50 characters or less');
        }

        if (!this.email || this.email.trim() === '') {
            errors.push('Email is required');
        } else {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(this.email)) {
                errors.push('Invalid email format');
            }
        }

        if (!this.password || this.password.trim() === '') {
            errors.push('Password is required');
        }

        if (this.password !== this.confirmPassword) {
            errors.push('Passwords do not match');
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }
}

/**
 * Authentication Response DTO
 */
export class AuthResponseDTO {
    constructor(token, user) {
        this.token = token;
        this.user = UserDTO.fromEntity(user);
        this.timestamp = new Date();
    }

    /**
     * Convert to plain object
     * @returns {Object} Plain object
     */
    toObject() {
        return {
            token: this.token,
            user: this.user.toObject(),
            timestamp: this.timestamp
        };
    }
}

/**
 * Task Filter DTO
 */
export class TaskFilterDTO {
    constructor(data = {}) {
        this.status = data.status || null;
        this.priority = data.priority || null;
        this.assignedTo = data.assignedTo || null;
        this.createdBy = data.createdBy || null;
        this.tag = data.tag || null;
        this.overdue = data.overdue || false;
        this.searchKeyword = data.searchKeyword || null;
    }

    /**
     * Check if any filters are active
     * @returns {boolean} True if filters active
     */
    hasFilters() {
        return this.status !== null ||
               this.priority !== null ||
               this.assignedTo !== null ||
               this.createdBy !== null ||
               this.tag !== null ||
               this.overdue ||
               this.searchKeyword !== null;
    }

    /**
     * Convert to repository filter object
     * @returns {Object} Filter object
     */
    toRepositoryFilter() {
        const filter = {};
        
        if (this.status !== null) filter.status = this.status;
        if (this.priority !== null) filter.priority = this.priority;
        if (this.assignedTo) filter.assignedTo = this.assignedTo;
        if (this.createdBy) filter.createdBy = this.createdBy;
        if (this.tag) filter.tag = this.tag;
        if (this.overdue) filter.overdue = true;

        return filter;
    }
}

/**
 * Password Change DTO
 */
export class PasswordChangeDTO {
    constructor(currentPassword, newPassword, confirmPassword) {
        this.currentPassword = currentPassword || '';
        this.newPassword = newPassword || '';
        this.confirmPassword = confirmPassword || '';
    }

    /**
     * Validate password change data
     * @returns {Object} Validation result
     */
    validate() {
        const errors = [];

        if (!this.currentPassword) {
            errors.push('Current password is required');
        }

        if (!this.newPassword) {
            errors.push('New password is required');
        }

        if (this.newPassword !== this.confirmPassword) {
            errors.push('New passwords do not match');
        }

        if (this.currentPassword === this.newPassword) {
            errors.push('New password must be different from current password');
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }
}

export default {
    TaskDTO,
    UserDTO,
    LoginDTO,
    RegisterDTO,
    AuthResponseDTO,
    TaskFilterDTO,
    PasswordChangeDTO
};
