// ✅ CORTEX Refactored — ValidationService (Frontend)
// ✅ SMELL-10 RESOLVED: Centralized validation (mirrors backend)
// ✅ SMELL-23 RESOLVED: Validation logic not in UI components

/**
 * Validation constants
 * ✅ SMELL-15 RESOLVED: No magic numbers
 */
const VALIDATION_RULES = {
    EMAIL_MIN_LENGTH: 5,
    EMAIL_MAX_LENGTH: 100,
    PASSWORD_MIN_LENGTH: 8,
    USERNAME_MIN_LENGTH: 3,
    USERNAME_MAX_LENGTH: 50,
    DESCRIPTION_MIN_LENGTH: 1,
    DESCRIPTION_MAX_LENGTH: 500,
    MAX_TRANSACTION_AMOUNT: 10_000_000,
} as const;

/**
 * Validation result
 */
export interface ValidationResult {
    isValid: boolean;
    errors: string[];
}

/**
 * Validation service — centralized validation logic
 */
export class ValidationService {
    /**
     * Validate email format
     */
    validateEmail(email: string): ValidationResult {
        const errors: string[] = [];

        if (!email || email.trim() === '') {
            errors.push('Email is required');
            return { isValid: false, errors };
        }

        if (!email.includes('@') || !email.includes('.')) {
            errors.push('Invalid email format');
        }

        if (email.length < VALIDATION_RULES.EMAIL_MIN_LENGTH) {
            errors.push(`Email must be at least ${VALIDATION_RULES.EMAIL_MIN_LENGTH} characters`);
        }

        if (email.length > VALIDATION_RULES.EMAIL_MAX_LENGTH) {
            errors.push(`Email must not exceed ${VALIDATION_RULES.EMAIL_MAX_LENGTH} characters`);
        }

        return { isValid: errors.length === 0, errors };
    }

    /**
     * Validate transaction data
     */
    validateTransaction(data: {
        description: string;
        amount: number;
        type: string;
    }): ValidationResult {
        const errors: string[] = [];

        // Description
        if (!data.description || data.description.trim() === '') {
            errors.push('Description is required');
        } else if (data.description.length < VALIDATION_RULES.DESCRIPTION_MIN_LENGTH) {
            errors.push(`Description must be at least ${VALIDATION_RULES.DESCRIPTION_MIN_LENGTH} characters`);
        } else if (data.description.length > VALIDATION_RULES.DESCRIPTION_MAX_LENGTH) {
            errors.push(`Description must not exceed ${VALIDATION_RULES.DESCRIPTION_MAX_LENGTH} characters`);
        }

        // Amount
        if (data.amount <= 0) {
            errors.push('Amount must be positive');
        }
        if (data.amount > VALIDATION_RULES.MAX_TRANSACTION_AMOUNT) {
            errors.push(`Amount must not exceed ${VALIDATION_RULES.MAX_TRANSACTION_AMOUNT.toLocaleString()}`);
        }

        // Type
        const validTypes = ['income', 'expense'];
        if (!validTypes.includes(data.type?.toLowerCase())) {
            errors.push("Type must be 'income' or 'expense'");
        }

        return { isValid: errors.length === 0, errors };
    }

    /**
     * Validate user creation data
     */
    validateUser(data: {
        userName: string;
        email: string;
        password: string;
        role?: string;
    }): ValidationResult {
        const errors: string[] = [];

        // Username
        if (!data.userName || data.userName.trim() === '') {
            errors.push('Username is required');
        } else if (data.userName.length < VALIDATION_RULES.USERNAME_MIN_LENGTH) {
            errors.push(`Username must be at least ${VALIDATION_RULES.USERNAME_MIN_LENGTH} characters`);
        } else if (data.userName.length > VALIDATION_RULES.USERNAME_MAX_LENGTH) {
            errors.push(`Username must not exceed ${VALIDATION_RULES.USERNAME_MAX_LENGTH} characters`);
        }

        // Email
        const emailResult = this.validateEmail(data.email);
        if (!emailResult.isValid) {
            errors.push(...emailResult.errors);
        }

        // Password
        if (!data.password || data.password === '') {
            errors.push('Password is required');
        } else if (data.password.length < VALIDATION_RULES.PASSWORD_MIN_LENGTH) {
            errors.push(`Password must be at least ${VALIDATION_RULES.PASSWORD_MIN_LENGTH} characters`);
        }

        // Role
        const validRoles = ['user', 'admin', 'moderator'];
        if (data.role && !validRoles.includes(data.role.toLowerCase())) {
            errors.push('Invalid role');
        }

        return { isValid: errors.length === 0, errors };
    }

    /**
     * Validate transfer operation
     */
    validateTransfer(data: {
        fromAccountId: number;
        toAccountId: number;
        amount: number;
    }): ValidationResult {
        const errors: string[] = [];

        if (!data.fromAccountId || data.fromAccountId <= 0) {
            errors.push('Source account is required');
        }

        if (!data.toAccountId || data.toAccountId <= 0) {
            errors.push('Destination account is required');
        }

        if (data.fromAccountId === data.toAccountId) {
            errors.push('Cannot transfer to the same account');
        }

        if (data.amount <= 0) {
            errors.push('Amount must be positive');
        }

        return { isValid: errors.length === 0, errors };
    }
}

// ✅ Singleton instance
export const validationService = new ValidationService();
