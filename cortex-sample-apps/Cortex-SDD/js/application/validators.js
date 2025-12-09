/**
 * Validators
 * Input validation for application layer
 * 
 * @author Asif Hussain
 * @version 1.0.0
 */

import { AppConfig } from '../config.js';
import { Priority, Status, Role } from '../domain/enums.js';
import { PasswordHasher } from '../infrastructure/security.js';

/**
 * Base Validator
 * Provides common validation methods
 */
class BaseValidator {
    /**
     * Check if value is empty
     * @param {*} value - Value to check
     * @returns {boolean} True if empty
     */
    static isEmpty(value) {
        return value === null || value === undefined || 
               (typeof value === 'string' && value.trim() === '');
    }

    /**
     * Check if string length is within range
     * @param {string} value - String to check
     * @param {number} min - Minimum length
     * @param {number} max - Maximum length
     * @returns {boolean} True if valid
     */
    static isLengthValid(value, min, max) {
        if (this.isEmpty(value)) return false;
        const length = value.trim().length;
        return length >= min && length <= max;
    }

    /**
     * Check if email format is valid
     * @param {string} email - Email to validate
     * @returns {boolean} True if valid
     */
    static isEmailValid(email) {
        if (this.isEmpty(email)) return false;
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    /**
     * Check if value is in enum
     * @param {*} value - Value to check
     * @param {Object} enumObj - Enum object
     * @returns {boolean} True if valid
     */
    static isEnumValid(value, enumObj) {
        return Object.values(enumObj).includes(value);
    }
}

/**
 * Task Validator
 * Validates task-related data
 */
export class TaskValidator extends BaseValidator {
    /**
     * Validate task creation data
     * @param {Object} data - Task data
     * @returns {Object} Validation result
     */
    static validateCreate(data) {
        const errors = [];

        // Title validation
        if (this.isEmpty(data.title)) {
            errors.push('Task title is required');
        } else if (!this.isLengthValid(data.title, 1, 200)) {
            errors.push('Task title must be between 1 and 200 characters');
        }

        // Description validation (optional but has max length)
        if (data.description && data.description.length > 2000) {
            errors.push('Task description must be 2000 characters or less');
        }

        // Priority validation
        if (data.priority === undefined || data.priority === null) {
            errors.push('Task priority is required');
        } else if (!this.isEnumValid(data.priority, Priority)) {
            errors.push('Invalid priority value');
        }

        // Status validation
        if (data.status === undefined || data.status === null) {
            errors.push('Task status is required');
        } else if (!this.isEnumValid(data.status, Status)) {
            errors.push('Invalid status value');
        }

        // Due date validation (must be in future if provided)
        if (data.dueDate) {
            const dueDate = new Date(data.dueDate);
            if (isNaN(dueDate.getTime())) {
                errors.push('Invalid due date format');
            }
        }

        // Tags validation
        if (data.tags && !Array.isArray(data.tags)) {
            errors.push('Tags must be an array');
        } else if (data.tags && data.tags.length > 10) {
            errors.push('Maximum 10 tags allowed');
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }

    /**
     * Validate task update data
     * @param {Object} data - Update data
     * @returns {Object} Validation result
     */
    static validateUpdate(data) {
        const errors = [];

        // Title validation (if provided)
        if (data.title !== undefined) {
            if (this.isEmpty(data.title)) {
                errors.push('Task title cannot be empty');
            } else if (!this.isLengthValid(data.title, 1, 200)) {
                errors.push('Task title must be between 1 and 200 characters');
            }
        }

        // Description validation (if provided)
        if (data.description !== undefined && data.description && data.description.length > 2000) {
            errors.push('Task description must be 2000 characters or less');
        }

        // Priority validation (if provided)
        if (data.priority !== undefined && !this.isEnumValid(data.priority, Priority)) {
            errors.push('Invalid priority value');
        }

        // Status validation (if provided)
        if (data.status !== undefined && !this.isEnumValid(data.status, Status)) {
            errors.push('Invalid status value');
        }

        // Due date validation (if provided)
        if (data.dueDate !== undefined && data.dueDate) {
            const dueDate = new Date(data.dueDate);
            if (isNaN(dueDate.getTime())) {
                errors.push('Invalid due date format');
            }
        }

        // Tags validation (if provided)
        if (data.tags !== undefined) {
            if (!Array.isArray(data.tags)) {
                errors.push('Tags must be an array');
            } else if (data.tags.length > 10) {
                errors.push('Maximum 10 tags allowed');
            }
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }

    /**
     * Validate task filter data
     * @param {Object} filters - Filter data
     * @returns {Object} Validation result
     */
    static validateFilter(filters) {
        const errors = [];

        if (filters.status !== undefined && filters.status !== null && 
            !this.isEnumValid(filters.status, Status)) {
            errors.push('Invalid status filter value');
        }

        if (filters.priority !== undefined && filters.priority !== null && 
            !this.isEnumValid(filters.priority, Priority)) {
            errors.push('Invalid priority filter value');
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }
}

/**
 * User Validator
 * Validates user-related data
 */
export class UserValidator extends BaseValidator {
    /**
     * Validate user creation data
     * @param {Object} data - User data
     * @returns {Object} Validation result
     */
    static validateCreate(data) {
        const errors = [];

        // Username validation
        if (this.isEmpty(data.username)) {
            errors.push('Username is required');
        } else if (!this.isLengthValid(data.username, 3, 50)) {
            errors.push('Username must be between 3 and 50 characters');
        } else if (!/^[a-zA-Z0-9_-]+$/.test(data.username)) {
            errors.push('Username can only contain letters, numbers, hyphens, and underscores');
        }

        // Email validation
        if (this.isEmpty(data.email)) {
            errors.push('Email is required');
        } else if (!this.isEmailValid(data.email)) {
            errors.push('Invalid email format');
        }

        // Password validation (if provided - for registration)
        if (data.password !== undefined) {
            const passwordValidation = PasswordHasher.validateStrength(data.password);
            if (!passwordValidation.isValid) {
                errors.push(...passwordValidation.errors);
            }
        }

        // Role validation
        if (data.role !== undefined && data.role !== null && 
            !this.isEnumValid(data.role, Role)) {
            errors.push('Invalid role value');
        }

        // Full name validation (optional)
        if (data.fullName && data.fullName.length > 100) {
            errors.push('Full name must be 100 characters or less');
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }

    /**
     * Validate user update data
     * @param {Object} data - Update data
     * @returns {Object} Validation result
     */
    static validateUpdate(data) {
        const errors = [];

        // Email validation (if provided)
        if (data.email !== undefined) {
            if (this.isEmpty(data.email)) {
                errors.push('Email cannot be empty');
            } else if (!this.isEmailValid(data.email)) {
                errors.push('Invalid email format');
            }
        }

        // Role validation (if provided)
        if (data.role !== undefined && !this.isEnumValid(data.role, Role)) {
            errors.push('Invalid role value');
        }

        // Full name validation (if provided)
        if (data.fullName !== undefined && data.fullName && data.fullName.length > 100) {
            errors.push('Full name must be 100 characters or less');
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }

    /**
     * Validate login credentials
     * @param {string} username - Username
     * @param {string} password - Password
     * @returns {Object} Validation result
     */
    static validateLogin(username, password) {
        const errors = [];

        if (this.isEmpty(username)) {
            errors.push('Username is required');
        }

        if (this.isEmpty(password)) {
            errors.push('Password is required');
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }

    /**
     * Validate registration data
     * @param {Object} data - Registration data
     * @returns {Object} Validation result
     */
    static validateRegister(data) {
        const errors = [];

        // Use create validation
        const createValidation = this.validateCreate(data);
        errors.push(...createValidation.errors);

        // Password confirmation
        if (data.password && data.confirmPassword && data.password !== data.confirmPassword) {
            errors.push('Passwords do not match');
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }

    /**
     * Validate password change
     * @param {string} currentPassword - Current password
     * @param {string} newPassword - New password
     * @param {string} confirmPassword - Confirm new password
     * @returns {Object} Validation result
     */
    static validatePasswordChange(currentPassword, newPassword, confirmPassword) {
        const errors = [];

        if (this.isEmpty(currentPassword)) {
            errors.push('Current password is required');
        }

        if (this.isEmpty(newPassword)) {
            errors.push('New password is required');
        } else {
            const passwordValidation = PasswordHasher.validateStrength(newPassword);
            if (!passwordValidation.isValid) {
                errors.push(...passwordValidation.errors);
            }
        }

        if (newPassword !== confirmPassword) {
            errors.push('New passwords do not match');
        }

        if (currentPassword === newPassword) {
            errors.push('New password must be different from current password');
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }
}

/**
 * Comment Validator
 * Validates comment-related data
 */
export class CommentValidator extends BaseValidator {
    /**
     * Validate comment data
     * @param {Object} data - Comment data
     * @returns {Object} Validation result
     */
    static validate(data) {
        const errors = [];

        if (this.isEmpty(data.text)) {
            errors.push('Comment text is required');
        } else if (!this.isLengthValid(data.text, 1, 1000)) {
            errors.push('Comment must be between 1 and 1000 characters');
        }

        if (this.isEmpty(data.userId)) {
            errors.push('User ID is required');
        }

        return {
            isValid: errors.length === 0,
            errors
        };
    }
}

export default {
    TaskValidator,
    UserValidator,
    CommentValidator
};
