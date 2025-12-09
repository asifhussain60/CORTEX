/**
 * Validation Layer
 * Input validation for DTOs and business rules
 * 
 * @module application/validators
 * @author Asif Hussain
 * @version 1.0.0
 */

/**
 * Validation result class
 */
export class ValidationResult {
    constructor() {
        this.isValid = true;
        this.errors = [];
    }

    /**
     * Add validation error
     * @param {string} field - Field name
     * @param {string} message - Error message
     */
    addError(field, message) {
        this.isValid = false;
        this.errors.push({ field, message });
    }

    /**
     * Check if field has errors
     * @param {string} field - Field name
     * @returns {boolean}
     */
    hasError(field) {
        return this.errors.some(e => e.field === field);
    }

    /**
     * Get all errors for a field
     * @param {string} field - Field name
     * @returns {Array<string>}
     */
    getErrors(field) {
        return this.errors
            .filter(e => e.field === field)
            .map(e => e.message);
    }
}

/**
 * Task Validator
 */
export class TaskValidator {
    /**
     * Validate task creation/update
     * @param {Object} taskDto - Task DTO
     * @returns {ValidationResult}
     */
    static validate(taskDto) {
        const result = new ValidationResult();

        // Title validation
        if (!taskDto.title || taskDto.title.trim() === '') {
            result.addError('title', 'Title is required');
        } else if (taskDto.title.length > 255) {
            result.addError('title', 'Title cannot exceed 255 characters');
        }

        // UserId validation (for creation)
        if (taskDto.userId !== undefined && taskDto.userId === null) {
            result.addError('userId', 'User ID is required');
        }

        return result;
    }
}

/**
 * User Validator
 */
export class UserValidator {
    /**
     * Validate user data
     * @param {Object} userDto - User DTO
     * @returns {ValidationResult}
     */
    static validate(userDto) {
        const result = new ValidationResult();

        // Username validation
        if (!userDto.username || userDto.username.trim() === '') {
            result.addError('username', 'Username is required');
        } else if (userDto.username.length < 3) {
            result.addError('username', 'Username must be at least 3 characters');
        } else if (userDto.username.length > 50) {
            result.addError('username', 'Username cannot exceed 50 characters');
        }

        // Email validation
        if (!userDto.email || userDto.email.trim() === '') {
            result.addError('email', 'Email is required');
        } else if (!this.isValidEmail(userDto.email)) {
            result.addError('email', 'Invalid email format');
        }

        return result;
    }

    /**
     * Check if email format is valid
     * @param {string} email - Email address
     * @returns {boolean}
     */
    static isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
}

/**
 * Login DTO Validator
 */
export class LoginValidator {
    /**
     * Validate login credentials
     * @param {Object} loginDto - Login DTO
     * @returns {ValidationResult}
     */
    static validate(loginDto) {
        const result = new ValidationResult();

        // Username or email validation
        if (!loginDto.usernameOrEmail || loginDto.usernameOrEmail.trim() === '') {
            result.addError('usernameOrEmail', 'Username or email is required');
        }

        // Password validation
        if (!loginDto.password || loginDto.password.trim() === '') {
            result.addError('password', 'Password is required');
        }

        return result;
    }
}

/**
 * Register DTO Validator
 */
export class RegisterValidator {
    /**
     * Validate registration data
     * @param {Object} registerDto - Register DTO
     * @returns {ValidationResult}
     */
    static validate(registerDto) {
        const result = new ValidationResult();

        // Username validation
        if (!registerDto.username || registerDto.username.trim() === '') {
            result.addError('username', 'Username is required');
        } else if (registerDto.username.length < 3) {
            result.addError('username', 'Username must be at least 3 characters');
        } else if (registerDto.username.length > 50) {
            result.addError('username', 'Username cannot exceed 50 characters');
        }

        // Email validation
        if (!registerDto.email || registerDto.email.trim() === '') {
            result.addError('email', 'Email is required');
        } else if (!UserValidator.isValidEmail(registerDto.email)) {
            result.addError('email', 'Invalid email format');
        }

        // Password validation
        if (!registerDto.password || registerDto.password.trim() === '') {
            result.addError('password', 'Password is required');
        } else if (registerDto.password.length < 6) {
            result.addError('password', 'Password must be at least 6 characters');
        } else if (!this.isStrongPassword(registerDto.password)) {
            result.addError('password', 'Password must contain at least one uppercase letter, one lowercase letter, and one number');
        }

        // Confirm password validation
        if (!registerDto.confirmPassword || registerDto.confirmPassword.trim() === '') {
            result.addError('confirmPassword', 'Confirm password is required');
        } else if (registerDto.password !== registerDto.confirmPassword) {
            result.addError('confirmPassword', 'Passwords do not match');
        }

        return result;
    }

    /**
     * Check if password meets strength requirements
     * @param {string} password - Password to validate
     * @returns {boolean}
     */
    static isStrongPassword(password) {
        const hasUppercase = /[A-Z]/.test(password);
        const hasLowercase = /[a-z]/.test(password);
        const hasNumber = /[0-9]/.test(password);
        return hasUppercase && hasLowercase && hasNumber;
    }
}
